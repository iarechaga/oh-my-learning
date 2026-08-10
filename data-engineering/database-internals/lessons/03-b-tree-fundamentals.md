---
id: database-internals/03
subject: database-internals
title: "B-Tree Fundamentals and Page-Oriented Indexing"
slug: b-tree-fundamentals
status: drafted
mastery:
seniority: senior
source: Database Internals (Alex Petrov), Part I, Chapter 4 (B-Tree Basics) and Chapter 5 (B-Tree Implementation)
prerequisites: [database-internals/02]
created: 2026-08-10
updated: 2026-08-10
---

# B-Tree Fundamentals and Page-Oriented Indexing

## TL;DR
A B-Tree is a balanced, disk-page-oriented search tree with high fan-out (dozens to hundreds of children per node), designed so that finding any record requires touching only a handful of pages even across millions of rows — typically 3-4 levels deep. Its shape (wide and shallow, not tall and narrow like a binary tree) is a direct consequence of the page/disk-seek economics from `database-internals/01`: minimizing the *number* of page reads matters far more than minimizing comparisons within a page.

## The idea
A binary search tree over a million keys is about 20 levels deep (log2(1,000,000) ≈ 20). If each level lived on a separate disk page, a single lookup would cost 20 random disk seeks — at ~5-10 ms each on a spinning disk, that's 100-200 ms for one lookup, unusable for an interactive database. The insight behind the B-Tree: disk I/O cost is dominated by the *number of pages touched*, not by in-memory comparisons within a page, so trade "few comparisons per level, many levels" for "many comparisons per level (fine, RAM is fast), few levels." Make each node as wide as a disk page can hold (high fan-out) and the tree gets dramatically shallower for the same number of keys, at the cost of doing a bit more in-memory work searching within each wide node — a trade that's overwhelmingly favorable given the size of the RAM/disk latency gap.

## How it works

### Fan-out math: why B-Trees stay shallow
Fan-out is the number of children a single node can point to. It's determined by how many `(key, child-pointer)` pairs fit in one page. Suppose:
- Page size: 8 KB (8192 bytes).
- Each key: ~16 bytes (e.g. a UUID or two 8-byte integers).
- Each child pointer: ~8 bytes (a page ID).

Each `(key, pointer)` pair costs ~24 bytes, so a page holds roughly `8192 / 24 ≈ 340` pairs — call it a fan-out of 300 after accounting for header/slot overhead. With a fan-out of 300:
- 1 level (root only): up to 300 keys.
- 2 levels: up to 300 x 300 = 90,000 keys.
- 3 levels: up to 300^3 = 27,000,000 keys.
- 4 levels: up to 300^4 = 8.1 billion keys.

**This is the headline number to internalize: a B-Tree over even billions of rows is typically only 3-4 levels deep**, meaning a point lookup costs only 3-4 page reads — and in practice fewer, because the top 1-2 levels (a few hundred KB to a few MB) are almost always cache-resident in the buffer pool (`database-internals/05`), so a real lookup often costs 1-2 *actual* disk I/Os, not 3-4.

### Anatomy of a B-Tree: internal nodes vs. leaf nodes
A B-Tree has two node types:
- **Internal (index) nodes**: contain only keys and child pointers, used purely for navigation — no actual row data.
- **Leaf nodes**: contain the actual data (or, in a non-clustered index, pointers to where the data lives in a heap file, per `database-internals/02`), plus a pointer to the *next* leaf node, forming a linked list across all leaves. This leaf-level linked list is what makes range scans fast: once you've navigated down to the starting leaf, you can walk sideways leaf-to-leaf without going back up through the tree.

**Worked example — a lookup.** Tree: root has keys `[100, 500]` pointing to three children. Looking up key `320`:
1. Load root page (likely cached). `100 <= 320 < 500`, follow the middle pointer.
2. Load the internal node at that pointer — say it has keys `[200, 350, 420]` pointing to four children. `200 <= 320 < 350`, follow the second pointer.
3. Load the leaf page. Binary-search within it (an in-memory operation over a few hundred keys, effectively free compared to a disk read) to find key `320` and read its value.
Total: 3 page reads (or fewer with buffer-pool caching), regardless of whether the tree holds a thousand rows or a billion.

### Node splits: how a B-Tree grows on insert
When a leaf node is full and a new key must be inserted, the node **splits**:
1. The leaf's current keys plus the new key are conceptually sorted.
2. The node is divided into two half-full nodes at the median key.
3. The median key is **copied up** (for leaf splits — the median stays in both the new leaf and becomes a separator in the parent) or **pushed up** (for internal-node splits, where the median moves up and does not remain in either child) into the parent as a new separator key with a pointer to the new right-hand node.
4. If the parent is now full too, the split **cascades upward**, potentially all the way to the root — a root split is the only way a B-Tree grows a new level, and it's rare precisely because fan-out is so high.

**Worked example — cascading split.** A leaf holding `[30, 32, 35, 40]` (at its 4-key capacity) receives an insert of `31`. Sorted: `[30, 31, 32, 35, 40]`. Split at the median (`32`): left leaf becomes `[30, 31]`, right leaf becomes `[32, 35, 40]`, and `32` is copied up into the parent as a new separator pointing to the right leaf. If the parent, say `[20, 50]`, now must accept `32` and was already full at 2 keys with a 2-key max, the parent itself splits the same way, pushing its own median up — and so on until either a non-full ancestor is found or the root splits (creating a brand-new root one level higher, the only operation that increases tree depth).

Because each split roughly halves a full node, nodes after a split are only ~50% full — this partial fill factor is normal and is why real-world B-Trees typically run at 60-70% average page utilization rather than 100%, a deliberate trade-off that leaves room for future inserts without immediately re-splitting.

### Deletes and rebalancing (merges and redistribution)
Deletes are the mirror problem: removing a key can leave a node under a minimum occupancy threshold (commonly half-full). When that happens, the engine either:
- **Redistributes**: borrows a key from an adjacent sibling that has room to spare (rotating one key through the parent separator), avoiding a merge.
- **Merges**: if no sibling has spare keys, combines the underfull node with a sibling into one node, removing a separator key from the parent — which can itself cascade upward the same way splits do.

Many production B-Tree implementations (including most relational databases) actually skip *eager* rebalancing-on-delete as an optimization, tolerating underfull nodes and reclaiming space later via a periodic maintenance pass (e.g. `VACUUM`/index rebuild), because eager rebalancing adds write amplification to every delete for a benefit (perfectly packed pages) that's rarely worth it in practice.

### Concurrency: latches and the challenge of concurrent splits
Because multiple threads/transactions read and write a B-Tree concurrently, pages need protection independent of the transaction-level locking covered in `database-internals/10`. B-Trees use lightweight, short-held **latches** (distinct from transactional locks: latches protect physical page structure for microseconds during a single operation, while transaction locks protect logical data for the duration of a transaction). A naive approach — latch the entire root-to-leaf path before starting, in case a split cascades all the way up — serializes almost all writers on the root and destroys concurrency. Real engines use techniques like **latch crabbing** (hold a parent latch only until you've confirmed the child you're descending into is *not* about to split/merge, then release the parent latch before descending further) to keep the "worst case, cascading split" path safe while keeping the common case (no split needed) highly concurrent.

### Why fan-out, not perfect balance, is the real lever
It's tempting to think "balanced" (as in AVL or red-black trees) is the star property of a B-Tree. It isn't, for this use case — balance alone doesn't help if the tree is still 20 levels deep. The star property is **fan-out**: turning "many levels of cheap comparisons" (fine for RAM-resident binary trees) into "few levels of many comparisons" (necessary when each level costs a disk read). A B-Tree is balanced *as a side effect* of always splitting at the median and always growing upward from a root split — but the *reason* it's fast is fan-out, not balance per se.

## Pros
- Logarithmic-depth lookups with a very small constant (3-4 levels for billions of rows) thanks to high fan-out tuned to page size.
- Leaf-level linked list makes ordered range scans fast and sequential.
- Mature, well-understood concurrency and recovery techniques (latch crabbing, WAL-based redo/undo) after decades of production use.

## Cons
- In-place updates mean random disk writes for out-of-order inserts, incurring the write amplification and seek costs described in `database-internals/01`.
- Splits/merges add complexity and occasional latency spikes, especially under high write concurrency (latch contention on hot pages, e.g. always inserting at the tail).
- Page fill factor after splits (~50-70%) wastes some disk space compared to a fully packed structure.

## Alternatives
- **LSM-Trees** (`database-internals/06`) — replace in-place page updates with append-only writes and background compaction, trading read amplification (checking multiple files) for far better write throughput; see `database-internals/08` for the head-to-head comparison.
- **Hash indexes** — O(1) average point lookups but no support for range scans (no ordering), useful only when the workload is purely point-lookup.
- **Skip lists / in-memory balanced trees** — appropriate for in-memory-only structures (e.g. a memtable, `database-internals/09`) where disk-seek economics don't apply and per-level cost really is comparison-only.

## When to use it
B-Trees are the right default for read-heavy or mixed workloads that need fast point lookups *and* fast ordered range scans, especially where update patterns are relatively random (not append-mostly) and strict read latency predictability matters (see `database-internals/08` for the fuller decision framework).

## When NOT to use it
Avoid a plain B-Tree for extremely write-heavy, append-dominated workloads (e.g. time-series ingestion, event logging) where the random-write cost of in-place page updates and split-driven write amplification becomes the bottleneck — an LSM-Tree (`database-internals/06`) is usually the better fit there.

## Key takeaways / mental model
A B-Tree is a phone book split across a small number of very wide, thick sections rather than a huge number of single-entry pages: you narrow down which thick section to grab (a page read) only 3-4 times, then flip through a few hundred entries on that one page in your hand almost for free, because that flipping happens in RAM, not on disk. The entire design exists to minimize "trips to grab a new page," because that trip — not the flipping — is where all the time goes.

## Self-check questions
1. Why does increasing the page size (say, from 8 KB to 16 KB) usually increase fan-out and reduce tree depth, and why doesn't a database just make pages arbitrarily large to get a 1-level tree?
2. Walk through what happens, step by step, when an insert causes a leaf split whose median key push-up also overflows the parent. At what point (if any) does the tree's depth actually increase?
3. Why do latches (page-structure protection) need to be a separate mechanism from the transactional locks covered in `database-internals/10`, rather than reusing the same lock manager?
4. A workload does mostly sequential-key inserts (e.g. an auto-incrementing ID or timestamp as the primary key). Explain why this specific pattern causes B-Tree splits to concentrate on the rightmost leaf, and what practical problem that creates (hint: think about concurrency/latch contention from `database-internals/01`'s I/O framing).

## References
- Database Internals (Alex Petrov), Part I, Chapter 4: "B-Tree Basics" and Chapter 5: "B-Tree Implementation."
- See also: `ddia/04` for the DDIA-level B-Tree vs. LSM-Tree framing, and `database-internals/02` for the page/slot layout this lesson builds on.
