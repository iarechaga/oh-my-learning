---
id: database-internals/07
subject: database-internals
title: "SSTables, Compaction Strategies, and Tombstones"
slug: sstables-compaction-and-tombstones
status: drafted
mastery:
seniority: senior
source: Database Internals (Alex Petrov), Part I, Chapter 7 (Log-Structured Storage, SSTable internals) and Chapter 4 appendix on compaction strategies
prerequisites: [database-internals/06]
created: 2026-08-10
updated: 2026-08-10
---

# SSTables, Compaction Strategies, and Tombstones

## TL;DR
An SSTable (Sorted String Table) is an immutable, on-disk file of key-value pairs sorted by key, paired with a sparse index and a Bloom filter for fast lookups; compaction is the background process that merges SSTables to control how many files a read must check (read amplification) and to reclaim space from overwritten or deleted (tombstoned) data. The choice between **size-tiered** and **leveled** compaction strategies is one of the most consequential operational decisions in running an LSM-Tree engine, trading write amplification against read amplification and space amplification in different proportions.

## The idea
`database-internals/06` established that LSM-Trees flush memtables into SSTables and periodically merge them via compaction. This lesson goes one level deeper into the SSTable's own internal structure (how it supports fast lookups despite being a flat sorted file) and into the mechanics and strategy choices of compaction itself — because "just merge sorted files" hides a genuinely important design space: *when* and *how* to merge determines the engine's read/write/space trade-off in practice, not just in theory.

## How it works

### Inside an SSTable: data blocks, sparse index, and Bloom filter
An SSTable file is not just a flat sorted list of key-value pairs — that would force a linear scan (or at best a disk-seeking binary search across the whole file) for every lookup. Instead, a typical SSTable has three logical parts:
1. **Data blocks** — the sorted key-value pairs themselves, grouped into blocks (e.g. 4-64 KB each), often compressed, since sequential similar data compresses well.
2. **A sparse index** — an in-memory (or memory-mapped) index recording only the *first* key of every data block, not every key. Because the file is sorted, knowing "block N starts at key X" is enough to binary-search the sparse index for the right block, then scan just that one block to find the exact key.
3. **A Bloom filter** — a compact probabilistic bitset that can say "this key is definitely not in this file" with zero false negatives (and a small, tunable false-positive rate), letting a read skip a file's disk I/O entirely without needing the sparse index or a data-block read at all.

**Worked example — Bloom filter mechanics.** A Bloom filter is a bit array of size `m` with `k` hash functions. To insert key `K`, compute `k` hash values of `K`, and set those `k` bit positions to 1. To query "is `K` present?", compute the same `k` hash positions and check if all of them are set to 1 — if even one is 0, `K` is *definitely not* in the set (no false negatives, because inserting would have set that bit). If all `k` are 1, `K` is *probably* present (could be a false positive, where those bits happened to be set by other keys' hashes colliding). A common tuning: 10 bits per key and 7 hash functions yields roughly a 1% false-positive rate — meaning a read for a genuinely absent key wastes disk I/O checking that specific SSTable only about 1% of the time, versus 100% of the time with no Bloom filter at all.

**Worked example — sparse index lookup.** An SSTable has 1 million sorted key-value pairs organized into 4 KB data blocks holding ~200 pairs each, giving ~5,000 blocks. The sparse index (one entry per block: first-key -> block-offset) has only 5,000 entries — small enough to comfortably keep entirely in RAM even for a very large SSTable. To find key `"user:88214"`: binary-search the 5,000-entry sparse index (a handful of comparisons, effectively free) to find which block it would fall in, then read that one 4 KB block from disk and scan its ~200 entries linearly (or binary-search within it) to find the exact key. Total disk I/O: one 4 KB block read, regardless of whether the SSTable holds a thousand or a billion keys — the sparse index absorbs the "which block" question entirely in RAM.

### Tombstones: how deletes work in an append-only structure
Since SSTables are immutable and never updated in place, a delete cannot simply "remove" a key from an existing file. Instead, a delete writes a special marker record called a **tombstone** — logically "key K is deleted as of this point in time" — through the exact same write path as a normal write (memtable, then eventually flushed to an SSTable). A read that encounters a tombstone for key `K` (checking newest-to-oldest, per `database-internals/06`) knows `K` is deleted and must not fall through to check older SSTables for a stale, pre-delete value.

**Worked example — a tombstone's lifecycle.** `delete("session:abc")` writes a tombstone into the current memtable, which later flushes into SSTable_7. A subsequent read for `"session:abc"` checks SSTable_7 (newest first), finds the tombstone, and correctly reports "not found" — even though an older SSTable_3 still physically contains the original value, that value is now shadowed. The tombstone itself is only truly safe to *discard* (during compaction) once every older SSTable that could possibly contain a shadowed version of that key has also been compacted away or merged past — discarding a tombstone too early, before all shadowed data is gone, would resurrect deleted data on the next read. This is why LSM-Tree engines (famously, Cassandra) warn operators about tombstone accumulation: if compaction is disabled, delayed, or misconfigured, tombstones (and the stale data they're meant to shadow) can accumulate indefinitely, wasting space and, in pathological cases (e.g. a read scanning past thousands of tombstones to find a live value), hurting read latency directly.

### Size-tiered compaction
**Size-tiered compaction** groups SSTables of similar size into "tiers"; when enough same-tier SSTables accumulate (a common trigger: 4 files of similar size), they're merged into one larger SSTable, which then becomes a candidate for the next tier up once enough files of *that* new size accumulate.

**Worked example — size-tiered progression.** Flushes produce four 50 MB SSTables. Compaction merges them into one 200 MB SSTable. Meanwhile, four more 50 MB SSTables accumulate from ongoing flushes and get merged into a second 200 MB SSTable. Once four 200 MB SSTables exist, they merge into one 800 MB SSTable, and so on — an exponentially growing tier structure. Characteristics: write amplification is relatively low (each byte is rewritten roughly `log(total_size / initial_size)` times across all tiers, and no strict per-level bound forces early re-merging), but read amplification and space amplification can be worse — a read may need to check one SSTable per tier (several files), and because tiers can hold overlapping key ranges, a lot of duplicate/superseded data can coexist until a big merge finally happens, temporarily inflating space usage (in the worst case, up to ~2x the live data size right before/during a large tier merge).

### Leveled compaction
**Leveled compaction** (used by RocksDB and Cassandra's LCS option) organizes SSTables into numbered levels (L0, L1, L2, ...), where each level has a fixed maximum total size (often growing ~10x per level), and — critically — within any level L1 or higher, SSTables are kept **non-overlapping** in key range (only L0, fed directly by memtable flushes, is allowed overlapping ranges among its own files).

**Worked example — leveled compaction mechanics.** L0 has a cap of, say, 4 files (memtable flushes land here directly, and L0 files *can* overlap in key range with each other). Once L0 exceeds its file-count threshold, a compaction picks L0 files plus any overlapping L1 files, merges them, and writes the result into L1 as new, non-overlapping SSTables. Because L1 (and every level above it) enforces non-overlapping key ranges, a read for key `K` needs to check *at most one* SSTable per level (find the one file in each level whose key range could contain `K`, via the sparse index approach) — this is the leveled scheme's core read-amplification win: read cost is bounded by the *number of levels* (typically 5-7 for very large datasets), not by the total number of SSTable files, which could be in the thousands.

**The trade-off, concretely.** Leveled compaction achieves much better read amplification (checking ~1 file per level vs. potentially several per tier) and much better space amplification (non-overlapping levels mean far less duplicate/superseded data lingers, typically bounding space overhead to roughly 10-20% above the live dataset size rather than size-tiered's occasional ~2x spikes) — but at the cost of significantly higher write amplification, because a single key can be rewritten once per level as it's repeatedly promoted from L0 through L1, L2, etc. during its lifetime; it's common for leveled compaction to have a write amplification factor of 10-30x (each logical byte physically rewritten that many times over its lifetime), versus size-tiered's typically lower (but less predictable) write amplification.

### Choosing a compaction strategy: the practical decision
- **Size-tiered** favors write-heavy workloads that can tolerate higher read/space amplification — good for append-mostly, rarely-read-back data (e.g. write-heavy logging where reads are rare and mostly recent).
- **Leveled** favors read-heavy or mixed workloads, or workloads sensitive to space usage (e.g. SSD-backed deployments where disk space is a real cost constraint), at the cost of more background compaction I/O (higher write amplification) competing for disk bandwidth.

Some engines (RocksDB) also offer hybrid strategies (e.g. "leveled with size-tiered L0") specifically to blend these trade-offs.

## Pros
- SSTables' sparse index + Bloom filter combination gives near-O(1) practical lookup cost per file despite the file being a flat sorted structure, with minimal RAM overhead relative to the data size.
- Tombstones let deletes flow through the same simple append-only write path as any other write, with no special in-place removal machinery needed.
- Compaction strategy choice (size-tiered vs. leveled) gives operators a real, tunable lever to match the read/write/space trade-off to their actual workload, rather than a one-size-fits-all default.

## Cons
- Tombstone accumulation under disabled/delayed/misconfigured compaction is a well-known operational failure mode that degrades both space usage and read latency, and can even resurrect deleted data if handled incorrectly (e.g. tombstones expiring/being garbage-collected before all shadowed data has actually been compacted away).
- Leveled compaction's high write amplification (10-30x) means significant background disk I/O and, on SSDs, real wear/endurance cost, competing directly with foreground traffic.
- Size-tiered compaction's occasional large-tier merges can cause pronounced, hard-to-predict I/O and space spikes, complicating capacity planning.

## Alternatives
- **No compaction / manual compaction only** — some use cases (write-once, rarely-updated datasets) can run with minimal or infrequent compaction, accepting a static, larger set of SSTables since there's little superseded data to reclaim.
- **Time-windowed compaction** (a size-tiered variant used for time-series data) — groups SSTables by time window rather than pure size, exploiting the fact that time-series data is rarely updated outside its own time window and can be dropped wholesale once the window expires (e.g. via TTL), without needing to merge across windows at all.

## When to use it
Use leveled compaction when read latency and space efficiency matter more than write throughput headroom (e.g. a user-facing read/write mixed workload). Use size-tiered (or time-windowed) compaction when write throughput dominates and reads are rare, recent-biased, or tolerant of somewhat higher latency (e.g. high-volume event ingestion with infrequent ad hoc querying).

## When NOT to use it
Don't run size-tiered compaction for a workload with heavy point-lookup read traffic against old data spread across many tiers — the read amplification will be painful. Don't run leveled compaction for an extremely write-heavy, latency-insensitive-on-reads workload where you can't afford the 10-30x write amplification's disk bandwidth and SSD wear cost.

## Key takeaways / mental model
An SSTable is a sealed, sorted book with a table of contents (sparse index) and a "definitely not in this book" quick-check (Bloom filter) on the cover, so you rarely have to open a book (disk I/O) you don't need. A tombstone is a "this entry was removed" sticky note filed in the same book, keeping deletes as simple as writes. Compaction is periodically re-shelving and merging books: size-tiered merges same-size books together lazily whenever enough pile up (cheap re-shelving, but you might have several books to check per topic); leveled compaction insists each shelf only ever has one book per topic (fast to find anything, at most one book per shelf), which means constantly moving books between shelves as new ones arrive (expensive re-shelving labor).

## Self-check questions
1. Explain why a Bloom filter's "definitely not present" answer can be trusted with zero false negatives, while its "probably present" answer cannot be trusted without a real disk check — walk through the hash-bit mechanics that make this asymmetry true.
2. Why must a tombstone survive in the LSM-Tree until every SSTable holding an older, shadowed version of that key has been compacted away — what specific bug would occur if a tombstone were discarded too early?
3. Contrast size-tiered and leveled compaction on all three RUM-conjecture axes (read, write/update, space/memory amplification, from `database-internals/06`) — which does each strategy sacrifice most, and why does that make leveled compaction the better default for a read-heavy user-facing service?
4. A time-series ingestion system writes constantly, rarely updates old data, and mostly queries recent data. Explain why time-windowed compaction is a better fit than generic leveled compaction for this specific access pattern.

## References
- Database Internals (Alex Petrov), Part I, Chapter 7: "Log-Structured Storage" (SSTable format, compaction strategies, Bloom filters, tombstones).
- See also: `database-internals/06` for the LSM-Tree write/read path this lesson's SSTable and compaction mechanics support.
