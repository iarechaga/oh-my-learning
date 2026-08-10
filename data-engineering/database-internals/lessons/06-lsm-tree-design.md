---
id: database-internals/06
subject: database-internals
title: "LSM-Tree Design and the Read-Write Amplification Trade-off"
slug: lsm-tree-design
status: drafted
mastery:
seniority: senior
source: Database Internals (Alex Petrov), Part I, Chapter 7 (Log-Structured Storage)
prerequisites: [database-internals/01, database-internals/04]
created: 2026-08-10
updated: 2026-08-10
---

# LSM-Tree Design and the Read-Write Amplification Trade-off

## TL;DR
A Log-Structured Merge-Tree (LSM-Tree) turns all writes into sequential, append-only operations by buffering them in an in-memory sorted structure (the memtable) backed by a write-ahead log, periodically flushing that memtable to an immutable sorted file on disk (an SSTable, `database-internals/07`), and later merging those files together in the background (compaction) to bound how many files a read must check. The central trade-off, formalized as the **RUM conjecture** (Read, Update, Memory), is that optimizing write throughput this way necessarily costs you something in read cost (checking multiple files) or space (temporarily duplicated data) — you cannot minimize all three simultaneously.

## The idea
`database-internals/03` showed that B-Trees minimize read cost by keeping every key in exactly one place, at the cost of in-place random writes. The LSM-Tree inverts that priority: minimize write cost by never updating in place at all — always append — accepting that a read might now need to check several places before it can be sure it has the latest (or only) version of a key. This is a direct, deliberate trade against the disk/SSD economics from `database-internals/01`: sequential appends are cheap, so push as much work as possible into "append now, reconcile later" and do the reconciliation (compaction) as a background process that can be scheduled, throttled, and amortized, rather than paid synchronously on every write.

## How it works

### The write path: memtable + WAL
Every write (`set(key, value)` or a delete, represented as a **tombstone** — see `database-internals/07`) follows two steps, both cheap:
1. Append the write to an on-disk **write-ahead log** (`database-internals/04`) — pure sequential I/O, purely for crash recovery of the memtable's contents.
2. Insert the write into an in-memory **memtable** — a sorted structure (commonly a skip list or a balanced tree, see `database-internals/09`) that keeps keys in order so it can later be flushed to disk already sorted, with no separate sort pass needed.

The write is considered durable and complete once both steps finish — no disk read, no random disk write, nothing waiting on a data-page location. This is why LSM-Trees achieve dramatically higher write throughput than B-Trees for the same hardware: every single write is O(log n) in-memory work plus one sequential log append, full stop.

### Flushing: memtable to SSTable
Memtables are capped in size (a common default is 32-64 MB, tunable). Once a memtable hits its size limit:
1. It's marked immutable/frozen and a new, empty memtable takes over incoming writes.
2. A background thread writes the frozen memtable's sorted contents to disk as a new **SSTable** (Sorted String Table, `database-internals/07`) — since the memtable is already sorted, this write is a single efficient sequential pass, no in-memory sort needed at flush time.
3. Once the SSTable is durably on disk, the WAL segment associated with that flushed memtable can be deleted (it's no longer needed for crash recovery — the data now lives durably in the SSTable itself).

**Worked example — sizing and flush frequency.** A write-heavy service ingests 10 MB/s sustained. With a 50 MB memtable size, a flush happens roughly every 5 seconds (`50MB / 10MB/s`), producing a new SSTable file on disk every 5 seconds. Over an hour, that's ~720 SSTable files accumulating if nothing merges them — which is exactly the problem compaction exists to solve (see below): without merging, a read might eventually have to check hundreds or thousands of files to find a single key.

### The read path: check memtable, then SSTables newest-first
A read for key `K` must, in principle, check: the active memtable first (most recent data), then any recently-flushed-but-not-yet-compacted memtables, then every SSTable on disk, from newest to oldest, until it finds `K` (returning the first — i.e. most recent — match) or exhausts all files (meaning the key doesn't exist, or was deleted via a tombstone). This is **read amplification**: one logical read can require touching many physical files, each potentially a separate disk I/O. Two mechanisms keep this tractable:
- **Bloom filters** (`database-internals/07`) — a compact in-memory probabilistic structure per SSTable that can definitively say "key K is NOT in this file" (with no false negatives, some false positives), letting reads skip the vast majority of files that don't contain the key, without touching disk at all for those skips.
- **Compaction** (below) — reduces the *number* of SSTables that can possibly contain a given key, bounding read amplification even without Bloom filters.

**Worked example — a read with 5 SSTables.** A read for key `"user:4271"` checks the memtable (miss), then SSTable_5 (newest, Bloom filter says maybe-present, disk check: miss), then SSTable_4 (Bloom filter says definitely-absent, skip — no disk I/O), then SSTable_3 (Bloom filter says maybe-present, disk check: hit, value found). The read stops here — it never needs to check SSTable_2 or SSTable_1, because SSTable_3's match is guaranteed to be the most recent version (files are checked newest-first) among the remaining set. Total disk I/O: 2 checks, out of 5 files, thanks to Bloom-filter skipping and newest-first short-circuiting.

### Compaction: merging SSTables to bound read amplification
Because flushing constantly produces new SSTables, a background **compaction** process periodically merges multiple SSTables into fewer, larger ones, using a mergesort-style algorithm (since each input SSTable is already internally sorted) that also discards superseded (older) versions of any key that appears in more than one input file, and drops keys whose most recent record is a tombstone once that tombstone is provably safe to remove (see `database-internals/07`).

**Worked example — compaction reducing file count.** Ten 50 MB SSTables (500 MB total, with significant key overlap from repeated updates to the same hot keys) are merged by compaction into two 200 MB SSTables (400 MB total — smaller, because superseded versions and safely-collapsed tombstones were dropped). A subsequent read now needs to check at most 2 files instead of 10 in the worst case — cutting worst-case read amplification by 5x, at the cost of the I/O the compaction pass itself consumed (reading 500 MB and writing 400 MB, i.e. ~900 MB of disk bandwidth spent as background work, not counted against foreground read/write latency directly, but consuming shared disk bandwidth while it runs).

### The RUM conjecture: you can't minimize Read, Update, and Memory (space) simultaneously
The RUM conjecture, a useful mental shorthand introduced in Petrov's book: any storage engine design that optimizes strongly for one of {Read amplification, Update/write amplification, Memory/space amplification} necessarily gives something up in at least one of the other two. LSM-Trees are a specific, deliberate point in this space:
- **Write amplification**: low at the *point of write* (just a sequential append), but compaction reintroduces write amplification later — rewriting the same logical data multiple times as it moves through compaction rounds. A key written once might be physically rewritten by compaction 3-5+ times over its lifetime in a leveled scheme (`database-internals/07`), so total lifetime write amplification is not actually zero — it's deferred and batched, not eliminated.
- **Read amplification**: higher than a B-Tree's "exactly one place," bounded by Bloom filters and compaction, but never fully eliminated — a read in the worst case (e.g. right after a burst of flushes, before compaction catches up) can still touch several files.
- **Space amplification**: temporarily higher than the logical data size, because old versions of updated/deleted keys linger until compaction reclaims them — a workload with heavy overwrite churn can have significantly more bytes on disk than live, distinct keys, until compaction runs.

B-Trees sit at a different point in the same trade space: minimal read amplification (one place per key) and minimal space amplification (in-place updates, no lingering old versions), at the cost of higher write amplification per write (whole-page rewrites, per `database-internals/03`). Neither design is objectively better — they're different, principled answers to the same three-way trade-off, and `database-internals/08` covers how to choose between them for a given workload.

## Pros
- Converts essentially all writes into sequential I/O, achieving very high write throughput, especially valuable on media where random writes are expensive (spinning disks) or amplify further (SSDs, per `database-internals/01`).
- Compaction is a background, schedulable, throttleable process — write latency for the foreground path doesn't depend on it directly, unlike a B-Tree's synchronous page-split cost.
- Naturally suits append-heavy, write-dominated workloads (logging, time-series, event ingestion) extremely well.

## Cons
- Read amplification: a point lookup may need to check multiple files, mitigated but not eliminated by Bloom filters and compaction.
- Compaction itself consumes significant background disk I/O and CPU, competing with foreground traffic, and can cause latency spikes ("compaction stalls") if it falls behind incoming write volume.
- Space amplification from lingering old versions and tombstones until compaction catches up — under sustained heavy overwrite/delete churn, disk usage can be a large multiple of the logical live dataset size.

## Alternatives
- **B-Trees** (`database-internals/03`) — the direct alternative, minimizing read/space amplification at the cost of write amplification; see `database-internals/08` for the full comparison and decision framework.
- **Fractal Trees / Bε-trees** — buffer writes inside internal tree nodes rather than in a separate memtable+SSTable hierarchy, aiming for a middle ground between B-Tree read performance and LSM-Tree write performance.
- **Log-structured file systems** — apply the same append-then-compact principle at the filesystem layer rather than the database layer; conceptually related but a different problem scope.

## When to use it
Choose an LSM-Tree-based engine (RocksDB, Cassandra, HBase, LevelDB) for write-heavy or append-dominated workloads — logging, telemetry/time-series ingestion, event sourcing — especially where write throughput and the ability to sustain high ingest rates matter more than guaranteeing the lowest possible single-key read latency.

## When NOT to use it
Avoid LSM-Trees when workloads need highly predictable, low read tail latency with minimal jitter (compaction stalls are a real operational risk), or when the workload is read-dominated with relatively few writes, where a B-Tree's single-location read guarantee is simply the better fit with none of LSM's read-amplification or compaction-overhead costs.

## Key takeaways / mental model
Picture a busy inbox (memtable) you keep sorted as things arrive, which you periodically empty into a labeled, sealed box (an SSTable) once it's full — fast, because you're never rearranging old boxes to add something new. Finding an old letter later means checking the inbox first, then the most recent sealed box, then the next, and so on, until you find it — slower than a single filing cabinet with one slot per letter (a B-Tree), but you occasionally consolidate old boxes together (compaction) to keep the number of boxes you'd ever have to check manageable. You've traded "instant, single-location filing" for "instant, no-rearranging inbox," and you pay for that trade later, in background box-consolidation labor and slightly slower searches.

## Self-check questions
1. Explain why flushing a memtable to an SSTable doesn't require an in-memory sort pass at flush time — what property of the memtable makes this true, and what data structure choices for the memtable (see `database-internals/09`) make maintaining that property cheap on every write?
2. Walk through the RUM conjecture's three-way trade-off and place both LSM-Trees and B-Trees on it: which corner does each favor, and which does each sacrifice?
3. A service does heavy overwrite churn on a small set of hot keys (the same 1,000 keys updated thousands of times per second) in an LSM-Tree engine. Explain why disk space usage might balloon well beyond the logical size of those 1,000 keys' current values, and what mechanism eventually reclaims that space.
4. Why can a read short-circuit after finding a key in a newer SSTable without needing to check any older SSTables, and why is "newest-first" order specifically load-bearing for that short-circuit to be correct?

## References
- Database Internals (Alex Petrov), Part I, Chapter 7: "Log-Structured Storage."
- See also: `database-internals/01` for the I/O economics motivating this design, `database-internals/04` for the WAL mechanics behind memtable durability, and `ddia/04` for the DDIA-level LSM-Tree framing.
