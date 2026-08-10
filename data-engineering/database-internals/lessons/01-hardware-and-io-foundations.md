---
id: database-internals/01
subject: database-internals
title: "Hardware and IO Foundations for Storage Engines"
slug: hardware-and-io-foundations
status: drafted
mastery:
seniority: mid
source: Database Internals (Alex Petrov), Part I, Chapter 1 (Introduction and Overview)
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# Hardware and IO Foundations for Storage Engines

## TL;DR
Every storage engine design decision is a response to one physical fact: random access to persistent storage is orders of magnitude slower than sequential access, and RAM is orders of magnitude faster (and more expensive, and volatile) than either. Understanding disk seeks, SSD page/block mechanics, and the RAM-vs-disk latency gap explains *why* B-Trees, LSM-Trees, write-ahead logs, and buffer pools are shaped the way they are, before you ever look at their code.

## The idea
Database textbooks often present B-Trees and LSM-Trees as if they were chosen for elegance. They weren't. They are engineering responses to the cost model of physical storage media. If you don't know that cost model, every subsequent design in this subject looks arbitrary; once you know it, almost every design looks inevitable.

The core problem: a database must persist data (survive power loss, process crashes) while also serving reads and writes fast enough to be useful. Persistence historically meant "on a spinning disk," which is catastrophically slow for random access compared to sequential access. Modern flash (SSD) storage changes the *mechanism* of that slowness but not the *shape* of the problem: random writes are still costly, just for a different physical reason. This lesson builds the mental model of the storage hierarchy that every later lesson in this subject leans on.

## How it works

### The storage hierarchy and its latency cliffs
Roughly, from fastest/smallest/most expensive to slowest/largest/cheapest:

| Medium | Typical latency | Typical order-of-magnitude vs RAM |
| --- | --- | --- |
| CPU register / L1 cache | ~1 ns | baseline |
| RAM | ~100 ns | ~100x slower than L1 |
| SSD (NVMe) random read | ~10-100 microseconds | ~1,000x slower than RAM |
| HDD random seek | ~5-10 milliseconds | ~100,000x slower than RAM |
| HDD sequential read/write | throughput close to SSD | but only if access is sequential |

The number worth memorizing: a single random seek on a spinning disk (moving the read/write head to a new track, waiting for the platter to rotate into position) costs about **5-10 milliseconds**. In that time you could have done roughly a **million** RAM accesses. This is why "minimize random disk I/O" is close to a first commandment of storage engine design — it dominates every other cost by several orders of magnitude.

### Why sequential access is cheap and random access is expensive (HDD)
A hard disk drive is a physical, mechanical device: a spinning platter and a moving arm with a read/write head. Two costs dominate any I/O operation:
- **Seek time** — moving the arm to the correct track (a few milliseconds).
- **Rotational latency** — waiting for the platter to spin the target sector under the head (up to ~4 ms for a 7200 RPM disk, since one full rotation takes ~8.3 ms and you wait on average half a rotation).

If you read data sequentially (consecutive bytes on the same track, or adjacent tracks), you pay this seek+rotation cost *once*, then stream data at the disk's raw throughput — often 100-200 MB/s. If you read data randomly (a different, unrelated location for every access), you pay the ~5-10 ms cost *per access*. Concretely: reading 1000 scattered 4KB blocks randomly could take 1000 x 7ms = 7 seconds. Reading the same 4MB sequentially takes a fraction of a second. That's a >100x difference for the exact same amount of data, purely because of access pattern.

This single fact explains: why append-only write-ahead logs exist (`database-internals/04`), why LSM-Trees defer random writes into batched sequential flushes (`database-internals/06`), and why B-Trees try to keep related data physically close together (`database-internals/02`).

### SSDs change the mechanism, not the lesson
Solid-state drives have no moving parts — reads and writes are electrical operations on flash cells, and random reads on SSD are fast (tens of microseconds), nowhere near as punishing as HDD random seeks. But SSDs have their own asymmetry that reintroduces the "sequential is better" lesson from a different angle:

- Flash memory is organized into **pages** (typically 4-16 KB, the unit of read/write) grouped into **blocks** (typically 128-256 pages, i.e. 512 KB-4 MB, the unit of *erase*).
- You can write to an empty page directly, but you **cannot overwrite a page in place** — to change data, the SSD's firmware must write the new version to a *different*, already-erased page, and mark the old page as stale. This is called **write amplification**: one logical write can trigger reading/rewriting many physical pages during garbage collection.
- Periodically, a background process (garbage collection) must find blocks with mostly stale pages, copy the still-valid pages elsewhere, and erase the whole block so it can be reused. Erasing is done at the block granularity, and each cell can only tolerate a limited number of erase cycles (wear leveling) before it degrades.

**Worked example — write amplification on SSD.** Suppose an application does small, scattered 4KB random writes across a drive that is 80% full. Every new write likely lands in a fresh page, but reclaiming space requires garbage collection to move live pages out of a stale-heavy block before erasing it. If a 256-page block has 200 stale pages and 56 still-valid pages, garbage collection must first copy those 56 pages elsewhere (56 extra writes) before the block can be erased and reused. The *application* only asked for 1 write; the *device* performed dozens. This is the SSD-flavored version of the same lesson HDDs teach: workloads that produce large, sequential, append-style writes cause far less amplification than workloads that scatter small random writes, because sequential writes fill blocks cleanly and age out together, leaving fewer partially-stale blocks behind.

This is precisely why LSM-Trees (`database-internals/06`), which turn random writes into sequential, append-only I/O plus batched background compaction, are so well matched to SSDs and cloud block storage, even though the *original* HDD-seek argument for them technically doesn't apply anymore — the write-amplification argument replaces it with the same practical conclusion.

### The RAM/disk gap and why buffering matters
Even ignoring random-vs-sequential, RAM is roughly 100-1000x faster than SSD and 10,000-100,000x faster than HDD for a single access, and it's byte-addressable (no page/block granularity constraint the way flash has). This gap is why every serious storage engine keeps a large in-memory cache of hot pages (a **buffer pool**, see `database-internals/05`), why write-ahead logs are appended to an in-memory buffer before an fsync forces them to disk, and why in-memory data structures like memtables (`database-internals/06`) exist as a staging area before data is durably flushed.

**Worked example — the durability tension.** A database must acknowledge a write only after it is *durable* (survives a crash), which technically means the data reached persistent storage — not just RAM, and often not even the OS page cache, since that too is lost on power failure, only an explicit `fsync`/`fdatasync` (or equivalent) that flushes to the physical medium's non-volatile storage counts. But calling fsync on every single write is disastrous for throughput: each fsync may cost roughly as much as a disk seek (milliseconds), so a naive "fsync per write" database caps out at a few hundred to a few thousand writes per second, however fast its CPU is. This is why databases batch: they append many logical writes into one write-ahead log buffer and fsync once per batch (or once per fixed time interval, trading a small durability window for large throughput gains) — turning N potential fsyncs into 1.

### Putting the pieces together: a mental checklist
When you meet a new storage-engine mechanism in this subject, ask:
1. Does it turn random I/O into sequential I/O? (If yes, it's paying the HDD-seek tax and the SSD-write-amplification tax down, at the cost of some later reorganization work — usually called compaction or vacuum.)
2. Does it batch fsyncs? (If yes, it's trading a small durability/latency window for throughput.)
3. Does it keep hot data in RAM? (If yes, it's exploiting the RAM/disk latency gap, at the cost of needing an eviction policy and a recovery path for what wasn't yet durable.)
Almost every mechanism in Part I of this subject is a specific answer to one or more of these three questions.

## Pros
- This is a mental model, not a mechanism — but understanding it lets you *predict* a new storage engine's trade-offs from its I/O pattern alone, without reading its source code.
- Explains why "premature micro-optimization" advice doesn't apply the same way to storage engines: the gap between sequential and random I/O is so large that access-pattern decisions dominate almost everything else.

## Cons
- The exact numbers (seek time, page size, RAM latency) drift with hardware generations — treat the figures here as orders of magnitude to reason with, not specs to cite verbatim for a specific device.
- Cloud "disks" (e.g. network-attached block storage) add another latency layer on top of the underlying physical medium, so real production latencies can be higher and noisier than raw hardware numbers suggest — the sequential-vs-random lesson still holds, but absolute numbers need re-measuring per environment.

## Alternatives
- **Treating storage as a black box and only measuring empirically (benchmarking-first)** — valid for tuning a specific deployment, but without this mental model you can't reason about *why* a benchmark result looks the way it does, or predict behavior for a workload you haven't yet tested.
- **Relying purely on vendor-documented "IOPS" numbers** — useful for capacity planning, but IOPS figures usually hide the random-vs-sequential distinction (a vendor's headline IOPS number is almost always the best case, sequential, large-block number) and can mislead if taken as representative of your actual access pattern.

## When to use it
Reach for this mental model whenever you're choosing between storage engines or diagnosing a performance problem: "is this workload dominated by random or sequential I/O, and is the pain point disk-bound, fsync-bound, or memory-bound?" It's the first diagnostic question for almost any database performance issue.

## When NOT to use it
Don't over-apply raw hardware latency numbers to fully-managed cloud databases or serverless offerings where the underlying storage medium and its access pattern are abstracted away and outside your control — there the relevant unit of reasoning is often the vendor's documented performance model (e.g. provisioned IOPS, burst credits) rather than raw disk physics.

## Key takeaways / mental model
Picture a librarian (RAM) at a desk who can hand you a book in a second, versus walking to a warehouse across town (disk) that takes several minutes per trip. If you need ten unrelated books, you don't want the librarian making ten warehouse trips (random I/O) — you want one trip that picks up ten books stored on the same shelf (sequential I/O), or better yet, books the librarian already keeps at the desk (cached in RAM). Every storage engine mechanism in this subject is some version of "how do we arrange the warehouse and the desk so that trips are batched, sequential, and rare."

## Self-check questions
1. A workload does 10,000 random 4KB writes per second to a spinning disk. Without doing exact math, explain in your own words why this workload is almost certainly disk-bound, and what change to the write pattern (not the hardware) would most improve it.
2. Why does an SSD's inability to overwrite a page in place produce a "write amplification" problem, and how does that end up favoring the same append-then-compact design pattern that HDD seek costs favored, for a different underlying reason?
3. A team proposes calling `fsync` after every single row insert "to be safe." What throughput problem will this likely cause, and what's the standard mitigation databases use, and what durability trade-off does that mitigation introduce?
4. Given the storage hierarchy, explain why a buffer pool (`database-internals/05`) is a load-bearing component of nearly every disk-based database, rather than a nice-to-have optimization.

## References
- Database Internals (Alex Petrov), Part I, Chapter 1: "Introduction and Overview."
- See also: `ddia/04` for the storage-engine framing this subject builds on in more depth.
