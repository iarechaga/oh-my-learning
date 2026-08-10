---
id: multiprocessor-programming/06
subject: multiprocessor-programming
title: Concurrent linked lists and skip lists
slug: concurrent-lists-skip-lists
status: drafted
mastery:
seniority: senior
source: The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 9 and Chapter 14
prerequisites: [multiprocessor-programming/04, multiprocessor-programming/05]
created: 2026-08-10
updated: 2026-08-10
---

# Concurrent linked lists and skip lists

## TL;DR
A concurrent linked-list set can be built with progressively less locking — coarse-
grained (one lock for the whole list), fine-grained (hand-over-hand per-node locking),
optimistic (traverse without locks, lock and re-validate before committing), and lazy
(mark-then-delete, letting reads run fully lock-free) — each trading implementation
complexity for reduced contention. Concurrent skip lists extend the same lazy/optimistic
techniques to a structure with O(log n) search, giving a scalable ordered set.

## The idea
A **set** implemented as a sorted linked list supports `add`, `remove`, `contains`, each
needing to traverse the list to find the right position. In a sequential world this is
trivial. Concurrently, multiple threads traversing, inserting, and removing nodes at the
same time can corrupt the list's pointer structure (a classic bug: thread A is about to
link a new node after node X, but thread B concurrently removes X, and A's link now
points into a detached, garbage node) or produce non-linearizable results
(`multiprocessor-programming/05`) even without literal corruption. This lesson walks
through a spectrum of designs, from the simplest-but-worst-performing (one big lock) to
increasingly clever techniques that let more operations proceed truly in parallel, each
addressing the previous design's specific contention or complexity problem.

## How it works

### Coarse-grained locking: one lock for the whole list
The simplest correct approach: a single lock guards the entire list; every `add`,
`remove`, `contains` acquires it for their whole duration. This is trivially linearizable
(it's just sequential execution, serialized by the lock) and trivially correct. Its
problem is equally obvious: **zero parallelism** — even two `contains()` calls that don't
touch the same part of the list, or would not conflict at all, are serialized behind the
single lock. Under any real contention, this doesn't scale at all; it's the baseline
every finer-grained scheme improves upon.

### Fine-grained locking: hand-over-hand traversal
Instead of one lock, give **each node its own lock**. A thread traversing the list
acquires the next node's lock *before* releasing the current node's lock ("hand-over-
hand" or "lock coupling") — this ensures no other thread can splice in or remove a node
out from under the traversal at the exact point the thread is examining.

**Worked example.** To find the insertion point for value 7 in list `[3, 5, 9]`: lock
node(head), lock node(3), unlock node(head); lock node(5), unlock node(3); lock node(9),
unlock node(5) — now holding node(5) and node(9)'s locks (the predecessor/successor pair
that 7 belongs between), insert the new node(7), then release both.

This allows far more parallelism than coarse-grained (two threads operating on disjoint
parts of the list don't block each other) but pays a real cost: acquiring and releasing a
lock *per node visited* during every traversal is expensive, and correctness requires
careful discipline (always acquire the next lock before releasing the current one, or a
concurrent modification could slip through the gap).

### Optimistic locking: traverse free, validate before commit
Fine-grained locking pays the lock-acquisition cost even for `contains()` calls that
never modify anything. **Optimistic locking** flips the strategy: traverse the entire
list *without* acquiring any locks at all, find the predecessor/successor pair you need,
*then* lock just those two nodes, and **validate** — re-check that the predecessor still
points to the successor and neither has been logically removed — before committing the
operation. If validation fails (something changed during the lock-free traversal), abort
and retry the whole traversal.

This removes the per-node locking cost from the traversal phase entirely, paying locking
cost only at the very end, for exactly the two nodes actually being modified. The risk:
under high contention, many attempts may fail validation and need to retry, and a naive
implementation might not distinguish "list changed somewhere irrelevant" from "list
changed at exactly my insertion point" — both trigger a full retry unless the validation
logic is precise about only what actually matters (the linkage between the specific
predecessor and successor nodes).

### Lazy synchronization: separate logical and physical removal
Optimistic locking still requires validating on *every* operation, including `contains()`
— read-heavy workloads still pay retry costs. **Lazy synchronization** improves on this by
adding a `marked` boolean field to each node, splitting removal into two steps:
1. **Logical removal**: under the two relevant nodes' locks, set the target node's
   `marked` flag to true. This alone makes the node "invisible" to any correct
   implementation of `contains()`.
2. **Physical removal**: unlink the marked node from the list (can happen immediately
   after marking, while still holding the locks, or be deferred).

The payoff: **`contains()` needs no locks and no validation at all** — it simply
traverses the list (following `next` pointers, which are never observed in an
inconsistent state because physical unlinking only happens under lock) and checks each
node's key and `marked` flag directly. Since reads dominate most real workloads, this is
often the biggest practical win in the whole progression: reads become essentially free
of synchronization overhead, while writes (`add`/`remove`) still use the same lock-then-
validate discipline as optimistic locking, now simplified because validation only needs
to check that neither the predecessor nor the node about to be examined is marked.

### Lock-free lists (a step further)
Going one step further than lazy synchronization (which still locks for writes), a fully
**lock-free** list uses atomic compare-and-swap (`multiprocessor-programming/10`) to
perform both the logical mark and the physical unlink without ever taking a lock, at the
cost of a subtler implementation (typically packing the "marked" bit into the low bit of
the `next` pointer itself, so marking and checking can both be done with a single atomic
CAS on the pointer word — a widely used trick). This connects directly to
`multiprocessor-programming/07`'s progress guarantees: coarse/fine-grained/optimistic/
lazy designs are all still blocking (locks), while a fully lock-free list guarantees
system-wide progress even if a thread is preempted mid-operation.

### Skip lists: adding express lanes
A sorted linked list's `contains`/`add`/`remove` are all O(n) — no way to skip ahead. A
**skip list** fixes this the same way an express subway line supplements a local one:
each node is probabilistically assigned a "height" (via coin flips — height h with
probability roughly `2^-h`), and a node of height h participates in h stacked linked
lists, from the bottom (level 0, containing every element, i.e. the full sorted list) up
to progressively sparser higher levels. Searching starts at the top (sparsest) level,
moves right as far as possible without overshooting the target, then drops down a level
and repeats — skipping over large swaths of the bottom-level list in the same way an
express train skips local stops. Expected search cost is O(log n) because each level's
expected node count roughly halves.

**Concurrent skip lists** apply the exact same techniques as the linked-list progression
above (lazy synchronization is the most common real-world choice) to each level: `marked`
flags for logical removal, lock-then-validate for `add`/`remove` on each affected level's
predecessor/successor pair, and lock-free traversal for `contains`. The key extra
subtlety versus a plain list: a node's insertion/removal must be consistently reflected
across *all* its levels (a node of height 3 exists in 3 separate linked lists
simultaneously) — implementations typically insert bottom-up and remove top-down to keep
partial states safely interpretable by concurrent readers at every point in the process.

## Pros
- The coarse-to-lazy progression is a genuinely reusable design pattern beyond lists: the
  same idea (separate "is this logically gone" from "is this physically unlinked," make
  reads lock-free) applies to many concurrent structures.
- Lazy synchronization gives essentially lock-free reads with only moderate implementation
  complexity — an excellent fit for read-heavy workloads, which most real systems are.
- Skip lists give expected O(log n) operations with a much simpler concurrent
  implementation than a concurrently-balanced tree would require (no rebalancing
  rotations to synchronize).

## Cons
- Fine-grained and optimistic locking both add real implementation complexity and subtle
  correctness pitfalls (forgetting to hold the right lock during validation, or validating
  the wrong condition) compared to coarse-grained locking's simplicity.
- Lazy synchronization's deferred physical removal means marked-but-not-yet-unlinked
  nodes linger in the list, adding minor traversal overhead and requiring a memory
  reclamation strategy (`multiprocessor-programming/12`) to reclaim them safely once no
  thread can still be examining them.
- Skip lists have probabilistic, not worst-case, height/performance guarantees — a run of
  bad luck in the coin flips can (rarely) produce a poorly balanced structure, though this
  is exponentially unlikely at scale.

## Alternatives
- **Concurrent hash tables** — O(1) expected operations instead of a list/skip-list's
  O(n)/O(log n), but don't support ordered traversal (range queries, "next key after X")
  the way a sorted list or skip list does.
- **Concurrently-balanced trees (e.g. concurrent AVL or red-black trees)** — also give
  O(log n) with worst-case (not just probabilistic) height bounds, but synchronizing tree
  rotations correctly under concurrency is substantially harder than skip lists' simpler
  level-based structure, which is exactly why skip lists are often preferred in
  concurrent settings despite red-black trees being more common sequentially.

## When to use it
Use coarse-grained locking as your starting point for correctness and only move to fine-
grained/optimistic/lazy once profiling shows the coarse lock is actually a bottleneck —
premature fine-grained locking adds real complexity for no benefit if contention is low.
Reach for lazy-synchronized lists or skip lists specifically when you need an ordered set
with concurrent, read-heavy access patterns (e.g. a concurrent priority structure, an
in-memory index needing range queries).

## When NOT to use it
Don't reach for fine-grained or lock-free list variants when the list is short-lived,
rarely contended, or accessed by very few threads — coarse-grained locking's simplicity
wins there, and the added complexity of the finer-grained schemes buys nothing. Don't use
a plain (non-skip) sorted linked list at all when O(n) search is a real bottleneck and
ordered traversal is needed — a concurrent skip list or balanced tree is the right
structure instead. Finally, avoid hand-rolling lazy synchronization or lock-free variants
without also having a memory reclamation plan (`multiprocessor-programming/12`) —
physically unlinking a node while another thread might still be dereferencing it is a
use-after-free bug waiting to happen; this is one of the most common real-world mistakes
in concurrent list implementations.

## Key takeaways / mental model
The progression coarse -> fine-grained -> optimistic -> lazy is a single narrative: push
synchronization cost off the common case (usually reads) and onto the rare case (writes),
each step removing unnecessary locking from the previous step's remaining bottleneck.
Lazy synchronization's key trick — separate *logical* removal (a `marked` flag, checked
by lock-free reads) from *physical* removal (actual unlinking, done under lock) — is the
single most reusable idea in this lesson. Skip lists apply the same techniques across
multiple stacked levels to get O(log n) search while staying simpler to synchronize than
a balanced tree.

## Self-check questions
1. Walk through why coarse-grained locking is trivially linearizable but fine-grained
   hand-over-hand locking requires more careful reasoning to prove linearizable.
2. Explain the two-phase (logical then physical) removal in lazy synchronization, and why
   it lets `contains()` run without acquiring any locks at all.
3. Why does a concurrent skip list typically insert a multi-level node bottom-up and
   remove it top-down? What could go wrong with a concurrent reader if the order were
   reversed?
4. A read-heavy workload with rare writes needs an ordered concurrent set. Argue for
   lazy-synchronized skip lists over both coarse-grained locking and a concurrent hash
   table, addressing what each alternative gets wrong for this workload.

## References
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 9: "Linked Lists: The
  Role of Locking."
- The Art of Multiprocessor Programming (Herlihy & Shavit), Chapter 14: "Skiplists and
  Balanced Search."
