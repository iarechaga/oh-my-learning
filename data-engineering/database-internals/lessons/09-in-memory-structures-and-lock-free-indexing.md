---
id: database-internals/09
subject: database-internals
title: "In-Memory Structures and Lock-Free Indexing Patterns"
slug: in-memory-structures-and-lock-free-indexing
status: drafted
mastery:
seniority: senior
source: Database Internals (Alex Petrov), Part I, Chapter 4 (skip lists appendix) and Chapter 6 (concurrent in-memory structures)
prerequisites: [database-internals/06]
created: 2026-08-10
updated: 2026-08-10
---

# In-Memory Structures and Lock-Free Indexing Patterns

## TL;DR
The memtable at the heart of every LSM-Tree (`database-internals/06`) needs a sorted, concurrently-mutable in-memory structure, and the industry's default answer is a **skip list**, not a balanced binary tree — because skip lists support simple, efficient lock-free (or nearly lock-free) concurrent inserts, while balanced trees like AVL/red-black trees require structural rebalancing that's brutally hard to make correct under concurrent, low-latency access.

## The idea
Once you understand why the memtable needs to be sorted (`database-internals/06`: sorted data flushes to an SSTable with no extra sort pass), the next question is: sorted with *what* data structure? A relational database's textbook answer for an in-memory sorted structure is often "balanced binary search tree." But production LSM-Tree engines almost universally use skip lists instead. This lesson explains why, and more broadly builds the mental model for how in-memory concurrent data structures differ from their disk-oriented cousins covered earlier in this subject — no disk seeks to worry about, but real concurrency correctness problems that don't exist in a single-threaded structure.

## How it works

### Why not a balanced tree for the memtable?
A memtable is written to by many concurrent client threads (or, in a single-writer engine, at minimum needs to support concurrent *reads* while a write is in progress) and read by both client reads and the background flush thread. Balanced trees (AVL, red-black) maintain their balance invariant through **rotations** — structural changes that touch multiple nodes and pointers atomically from a correctness standpoint. Making rotations safe under concurrent access typically requires locking a non-trivial subtree during the rotation, which either serializes concurrent writers around hot regions of the tree or requires very sophisticated (and bug-prone) fine-grained locking or lock-free rebalancing schemes that are hard to get right and rarely worth the complexity for this specific use case.

### Skip lists: probabilistic balance without rotations
A **skip list** is a layered linked list: the bottom layer contains every element in sorted order (a plain sorted linked list); each layer above contains a randomly-chosen subset of the elements below it (typically each element independently has, say, a 50% or 25% chance of being "promoted" to the next layer up), forming express lanes that let a search skip over many elements at once.

```
Level 3:  H -------------------------> N -------------------> T
Level 2:  H ---------> K -------------> N ---------> R ------> T
Level 1:  H -> J -> K -> L -> M -> N -> O -> P -> R -> S -> T
```

**Worked example — a skip list search.** Searching for key `P` starting at the top level (Level 3): compare `H` and `N` — `P > N`, but there's no further node at Level 3, so drop down to Level 2 at `N`. Compare `N` and `R` — `P < R`, so move down to Level 1 at `N`. Walk forward: `N -> O -> P`, found. Total comparisons: roughly proportional to the number of layers (`O(log n)` expected, matching a balanced tree's depth), achieved purely by *skipping* forward through express lanes rather than by any tree-rotation-maintained invariant.

**Why this avoids the concurrency problem.** Inserting a new node into a skip list means: pick a random height for the new node (e.g. via repeated coin flips — each "heads" promotes it one more level, capped at some max), then splice it into each layer it belongs to, from the bottom up. Critically, this splicing is purely *local* — it only touches the new node and its immediate predecessor/successor pointers at each layer, never requiring a cascading rebalance of unrelated parts of the structure the way a tree rotation can. This locality is exactly what makes skip lists amenable to lock-free implementations using atomic compare-and-swap (CAS) operations on individual pointers, rather than needing to lock a whole subtree.

### Lock-free insertion sketch
A simplified lock-free skip-list insert (the real algorithms, e.g. from Java's `ConcurrentSkipListMap`, have more nuance around marking nodes for deletion and retry loops, but the core idea holds):
1. Find the predecessor node at each level the new node will occupy (a normal, wait-free search).
2. At the bottom level, atomically CAS the predecessor's `next` pointer to point to the new node (with the new node's `next` already set to the old successor) — if the CAS fails (another thread modified that pointer concurrently), retry the search-and-CAS from that point.
3. Repeat the CAS-and-retry-on-failure pattern for each higher level the new node occupies, working upward.

Because each CAS only touches one pointer, and a failed CAS just means "retry locally, someone else made progress" (not "the whole structure is now inconsistent"), multiple threads can insert into different parts of the skip list fully concurrently with no locks at all, and even concurrent inserts to *nearby* keys typically only contend briefly on a shared predecessor pointer, not on the whole structure.

**Worked example — concurrent inserts, no contention.** Two threads simultaneously insert `"key_500"` and `"key_9000"` into a skip list with a million existing entries. Because these keys land in entirely different regions of the sorted structure, their CAS operations touch entirely different predecessor/successor pointers — both inserts succeed on their first CAS attempt with zero retries, fully concurrently, with no shared lock ever taken. Compare this to a naive single-lock-protected balanced tree, where both inserts would have to fully serialize regardless of how far apart the keys are.

### Read consistency without locks: why memtable reads don't need to block
A crucial property that makes lock-free memtables practical: reads (lookups, range scans for flush) don't need to coordinate with concurrent writers at all in the common design, because a skip list's nodes, once linked into the structure, are never mutated in place — an insert only ever adds a new node via pointer splicing, never edits an existing node's key/value. A reader that's mid-traversal when a concurrent insert happens will either see the new node (if it hasn't passed that point yet) or not (if it already passed) — both outcomes are valid linearizable results (the insert either "happened before" or "happened after" the read, from the read's perspective), so no read-side locking or retry is needed. This mirrors the copy-on-write philosophy from `database-internals/02`, applied at the level of individual pointers rather than whole pages.

### Beyond skip lists: other in-memory concurrent structures in database engines
- **Lock-free hash tables** — used where ordering doesn't matter (e.g. a buffer pool's page table, `database-internals/05`, mapping page IDs to frame locations) — typically implemented via open addressing with CAS-based slot claiming, or via sharded/striped locking when full lock-freedom isn't worth the complexity.
- **Copy-on-write B-Trees held entirely in memory** — some engines use an immutable, versioned in-memory tree (each update produces a new root pointing to mostly-shared subtrees, only the path to the change is new) to give concurrent readers a stable, consistent snapshot without any locking — conceptually the in-memory cousin of the on-disk copy-on-write B-Trees mentioned in `database-internals/02`.
- **MVCC-versioned in-memory structures** — layering multiple versions of a value in the same structure (see `database-internals/10`) so readers at different snapshot timestamps can proceed without blocking writers, and vice versa.

## Pros
- Skip lists achieve balanced-tree-equivalent expected `O(log n)` search/insert/delete performance with dramatically simpler, more concurrency-friendly implementation (no rotations).
- Lock-free (CAS-based) implementations allow high write concurrency with minimal contention, especially for keys spread across the key space — a strong fit for the memtable's high-throughput write path.
- Read operations proceed without any locking or coordination with writers, thanks to append-only (never-mutate-in-place) node linking.

## Cons
- Skip lists have probabilistic (not worst-case guaranteed) balance — an unlucky sequence of random coin flips can, in principle, produce a poorly-balanced structure, though this is exceedingly rare in practice with a reasonable promotion probability and is not something engines typically guard against explicitly.
- Skip lists use somewhat more memory per element than a plain balanced tree (extra forward pointers per promoted level), though this is usually a minor overhead relative to the value data itself.
- Lock-free algorithms are notoriously hard to get exactly right (subtle ABA problems, memory reclamation hazards under concurrent deletes) — most teams use a well-tested library implementation (e.g. Java's `ConcurrentSkipListMap`, or a vetted C++ equivalent) rather than writing their own.

## Alternatives
- **Balanced binary trees with fine-grained or optimistic locking** — viable but significantly more complex to implement correctly under high concurrency; used in some engines but less common than skip lists specifically for this use case.
- **Sharded/partitioned memtables** — instead of one shared concurrent structure, partition the key space (or hash space) across N independent memtables, each with simpler (even single-threaded) internal locking, trading some cross-shard coordination complexity (e.g. flush must coordinate across shards) for much simpler per-shard concurrency.

## When to use it
Reach for a skip list (or a well-tested concurrent-skip-list library) whenever you need a sorted, concurrently-mutable in-memory structure under moderate-to-high write concurrency — the memtable use case is the canonical example, but the pattern generalizes to any in-memory sorted index that needs to support concurrent inserts without heavy locking.

## When NOT to use it
Don't reach for a custom lock-free skip-list implementation for a low-concurrency or single-threaded use case — the complexity isn't justified when a plain sorted structure (or even a simple mutex-protected balanced tree) would perform identically for that access pattern with far less implementation risk.

## Key takeaways / mental model
A skip list is an express-train system laid over a plain sorted linked list: most stops (nodes) are only reachable via the local line (bottom level), but some are also reachable via express lines (higher levels) that skip over many local stops at once, and which express lines a stop belongs to is decided by a coin flip when it's built. Because adding a new stop only ever touches its immediate neighbors on each line it joins — never requiring the express lines themselves to be redrawn — many workers can add new stops to different parts of the system fully in parallel, which is precisely the property a memtable under concurrent write load needs.

## Self-check questions
1. Explain, structurally, why a balanced binary tree's rotation-based rebalancing is fundamentally harder to make lock-free than a skip list's insertion — what property does a rotation require that a skip-list splice doesn't?
2. Walk through why a reader traversing a skip list doesn't need to coordinate with a concurrent writer, linking this back to the "never mutate a node in place" property — what specific mutation, if it were allowed, would break this guarantee?
3. Why is a skip list's `O(log n)` performance described as "expected" rather than "guaranteed," and why is this a perfectly acceptable trade-off for a memtable despite that theoretical weakness?
4. A team is building a low-write-concurrency embedded database (single writer thread, occasional readers) and is debating a lock-free skip-list memtable vs. a simple mutex-protected balanced tree. Which would you recommend, and why does the "when NOT to use it" guidance apply here?

## References
- Database Internals (Alex Petrov), Part I, Chapter 4 (skip list appendix) and Chapter 6 (concurrent structure discussion).
- See also: `database-internals/06` for the memtable's role in the LSM-Tree write path, and `database-internals/02` for the copy-on-write philosophy this lesson's lock-free reads echo at the pointer level.
