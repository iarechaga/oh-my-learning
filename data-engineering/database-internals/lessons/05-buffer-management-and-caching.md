---
id: database-internals/05
subject: database-internals
title: "Buffer Management, Caching, and Compaction Pressure"
slug: buffer-management-and-caching
status: drafted
mastery:
seniority: senior
source: Database Internals (Alex Petrov), Part I, Chapter 6 (Files and Buffer Management)
prerequisites: [database-internals/01, database-internals/03]
created: 2026-08-10
updated: 2026-08-10
---

# Buffer Management, Caching, and Compaction Pressure

## TL;DR
A buffer pool (buffer manager) is an in-memory cache of disk pages, sitting between the storage engine's logic and the filesystem, that decides which pages stay hot in RAM and which get evicted under memory pressure — and it must do this while also tracking which pages are "dirty" (modified but not yet flushed) so it never evicts unflushed data without first durably persisting it. Choosing the eviction policy well is the difference between a database that serves most reads from RAM and one that thrashes against disk on every query.

## The idea
`database-internals/01` established that RAM is orders of magnitude faster than disk, and `database-internals/03` showed that a B-Tree's top levels are small enough to fit comfortably in RAM. The buffer pool is the component that actually exploits this: rather than every page read/write going straight to disk, the storage engine reads/writes through an in-memory cache of fixed-size page frames. The central design problem is that RAM is finite and much smaller than the on-disk dataset, so the buffer pool must constantly decide which pages earn a spot in the limited cache and which get evicted — and it must never lose a write in the process.

## How it works

### The buffer pool's basic contract
The buffer pool exposes something like `pin(page_id) -> page in RAM` and `unpin(page_id)` to the rest of the engine. When a page is requested: if it's already cached (a **cache hit**), return it immediately from RAM — no disk I/O. If not (a **cache miss**), find a free frame (or evict something to make one), read the page from disk into that frame, and return it. Every page frame carries metadata: a **dirty bit** (has this page been modified since it was read from disk?), a **pin count** (is anything currently using this page — pinned pages must never be evicted), and whatever bookkeeping the eviction policy needs (e.g. last-access time, reference bits).

**Worked example — a hit and a miss.** A buffer pool holds 10,000 8 KB page frames (80 MB total). A query needs page 42, which is already cached (index lookup into the buffer pool's page table finds it) — the engine returns it in microseconds, no disk I/O. The next query needs page 9001, not cached. The buffer pool must evict some other unpinned page to free a frame, issue a disk read for page 9001 (costing the disk-latency numbers from `database-internals/01`), populate the frame, and return it. The entire performance character of the database, for read-heavy workloads, comes down to how often this second path (a miss) happens versus the first (a hit) — the **buffer pool hit ratio**.

### Eviction policies: LRU, CLOCK, and why naive LRU isn't enough
The simplest eviction policy is **Least Recently Used (LRU)**: evict whichever cached page hasn't been accessed in the longest time, on the theory that recently-used pages are likely to be used again soon (temporal locality). Pure LRU has a well-known failure mode: a large sequential scan (e.g. a full-table scan or a big range query) touches a huge number of pages exactly once, each of which — under pure LRU — gets promoted to "most recently used" and evicts genuinely hot pages that were being reused by other concurrent queries, even though the scanned pages themselves will likely never be touched again. This is called **sequential flooding** and can wreck cache effectiveness for the rest of the workload for as long as the scan runs.

Real engines mitigate this with variations:
- **CLOCK (a cheap LRU approximation)**: each frame has a reference bit set on access; eviction sweeps frames in a circular order, clearing reference bits and skipping pages that were recently referenced, evicting the first one found with a clear bit. Cheaper than maintaining an exact LRU list (no need to move list nodes on every access), at the cost of being an approximation.
- **LRU-K / 2Q / segmented LRU**: track recency of the *last K* accesses (not just the last one), or maintain separate "probationary" and "protected" segments, so a page must be accessed more than once before earning long-term cache residency — directly defeating the sequential-flooding problem, since a one-off scan's pages never earn promotion to the protected segment.

**Worked example — sequential flooding and its fix.** A buffer pool with plain LRU and 1,000 frames is serving a mix of point lookups against a hot 500-page working set (currently ~90% cache hit ratio) when a batch job kicks off a full-table scan touching 50,000 distinct pages once each. Under pure LRU, this scan evicts the entire hot 500-page working set within the first ~1,000 pages of the scan, and the point-lookup workload's hit ratio collapses toward 0% for the scan's duration. Under a segmented policy (e.g. 2Q), the scanned pages enter only a small probationary segment and are evicted among themselves without displacing the "protected" segment holding the genuinely hot 500 pages — the point-lookup workload's hit ratio stays largely intact even while the scan runs.

### Dirty pages: the eviction/durability interaction
A page can't simply be evicted the instant it's chosen — if it's **dirty** (modified since last read from disk), evicting it without first writing it back would silently lose that change (or, if WAL discipline from `database-internals/04` is followed correctly, would just mean the change needs to be re-derived from the log on next read, which is wasteful but not unsafe, *provided* the WAL-before-data ordering rule was respected). The standard approach: on eviction of a dirty page, first **flush** it to disk (write it back), and only then reuse its frame. This is why database write throughput is often gated less by "can we log the change" (cheap, sequential, per `database-internals/04`) and more by "can we flush dirty pages back fast enough to keep freeing frames for new reads" — under heavy write load with a small buffer pool, the engine can spend more time flushing dirty victims than serving new requests.

**Background flushing (write-back) as a mitigation.** Rather than only flushing a dirty page at the moment it's chosen for eviction (synchronous, blocking whoever needed that frame), most engines run a background thread that proactively flushes dirty pages during idle I/O capacity, keeping the fraction of dirty pages in the pool below some target threshold (e.g. never more than 20-30% dirty) so that eviction rarely has to block on a synchronous flush.

### Buffer pool sizing and the "working set" concept
A database's **working set** is the subset of pages actively touched by ongoing queries in a given time window. If the buffer pool is at least as large as the working set, the hit ratio approaches 100% and the database behaves as if it were an in-memory database for practical purposes. If the buffer pool is smaller than the working set, the engine constantly evicts pages it will need again shortly, and performance degrades sharply — often non-linearly, since a buffer pool at 90% of working-set size can still perform far worse than one at 100%, because the "missing" 10% might be pages accessed by nearly every query.

**Worked example — sizing decision.** A database's actively-queried data is 40 GB, and available RAM for the buffer pool is 32 GB (80% of the working set). In practice this frequently produces a hit ratio in the 60-80% range rather than a proportional 80%, because eviction pressure doesn't evenly spread across all 40 GB — some subset of pages (indexes on frequently-filtered columns, hot partitions) get evicted and re-fetched repeatedly, disproportionately hurting exactly the queries that rely on them. This nonlinearity is why "just under-provision memory a little" is a much worse bet than it sounds, and why capacity planning for a database usually targets buffer-pool size comfortably above the known working set, not just barely above it.

### Compaction pressure: where LSM-Trees interact with buffer management
In LSM-Tree engines (`database-internals/06`, `database-internals/07`), buffer/cache management has an extra dimension: background compaction reads and rewrites large volumes of SSTable data, competing for both disk I/O bandwidth and buffer-pool cache space with foreground query traffic. A compaction pass reading old SSTables to merge them pollutes the cache with pages that (similar to sequential flooding above) are unlikely to be re-read soon, unless the engine explicitly bypasses the cache for compaction I/O (many engines do exactly this — using direct, uncached I/O for compaction reads/writes specifically to avoid evicting the foreground working set). This compaction-vs-cache tension is a recurring operational pain point: aggressive compaction improves read amplification (fewer SSTables to check) but can transiently hurt cache effectiveness and disk bandwidth availability for foreground traffic while it runs.

## Pros
- Buffer pooling turns a disk-bound workload into a largely RAM-bound one whenever the working set fits in the pool, delivering the RAM/disk latency-gap benefit from `database-internals/01` transparently to the rest of the engine.
- Smarter eviction policies (CLOCK, 2Q, LRU-K) directly defend against pathological access patterns (large scans) that would otherwise destroy cache effectiveness for concurrent workloads.
- Background/asynchronous flushing decouples eviction latency from synchronous disk-write latency in the common case.

## Cons
- Every eviction policy is a heuristic guess at future access patterns; no policy is optimal for every workload, and the "wrong" policy for a given workload's access pattern (e.g. plain LRU under heavy scans) can be catastrophic.
- Dirty-page flushing creates a background I/O workload that competes with foreground query I/O, and under sustained heavy writes can become the actual throughput bottleneck rather than logging.
- Buffer pool effectiveness degrades non-linearly once the working set exceeds available memory — a "slightly too small" buffer pool can perform dramatically worse than a "just barely large enough" one, making capacity planning error-prone.

## Alternatives
- **OS page cache reliance (no dedicated buffer pool)** — some engines (historically, e.g. many LSM-Tree implementations reading SSTable files) lean on the operating system's own file-system page cache instead of managing their own buffer pool, trading control (no engine-specific eviction policy) for simplicity, at the risk of double-buffering (data cached both by the OS and, if the engine also has its own cache, redundantly by the engine).
- **Direct I/O with fully custom cache management** — engines that bypass the OS page cache entirely (O_DIRECT) implement their own buffer pool with full control over eviction and prefetching, at the cost of more implementation complexity but avoiding double-buffering and giving the engine precise control matched to its own access patterns.

## When to use it
Any disk-based storage engine benefits from an explicit, workload-aware buffer management strategy — it's essentially always present in production database engines, though the sophistication of the eviction policy (plain LRU vs. segmented/scan-resistant policies) should scale with how mixed the workload is (point lookups plus occasional big scans, vs. a uniform access pattern).

## When NOT to use it
If the entire dataset comfortably fits in RAM and the engine is explicitly designed as an in-memory database (with disk used only for durability logging/snapshots, not as the primary storage tier), a full disk-page eviction policy is unnecessary complexity — the interesting problems shift to log/snapshot durability rather than cache eviction.

## Key takeaways / mental model
Think of the buffer pool as a small, fast desk (RAM) next to a huge, slow warehouse (disk): you keep the books (pages) you're actively using on the desk, and when the desk is full and you need a new book, you have to put one away first — ideally not one you'll need again in the next five minutes. Plain LRU is "put away whatever I touched longest ago," which fails badly if you just did a one-time inventory sweep of the entire warehouse (a full scan) — you'd end up clearing your whole desk of genuinely useful books to make room for books you'll never open again. Smarter policies protect books that have proven themselves useful more than once from being displaced by one-off sweeps.

## Self-check questions
1. Explain sequential flooding in your own words: why does a large scan under plain LRU disproportionately damage a concurrent point-lookup workload's cache hit ratio, and how does a segmented/2Q-style policy specifically defend against it?
2. Why must a dirty page be flushed to disk before (or as part of) its eviction, and what would go wrong if an engine allowed evicting a dirty page without ever flushing it (assume no WAL exists to reconstruct it)?
3. A database's working set is 50 GB and its buffer pool is 45 GB (90%). Explain why observed cache hit ratio in production is likely to be noticeably worse than a naive "90% of pages fit, so ~90% hit ratio" estimate would suggest.
4. In an LSM-Tree engine (`database-internals/06`), why might background compaction reads deliberately bypass the buffer pool's cache rather than populating it like a normal foreground read would?

## References
- Database Internals (Alex Petrov), Part I, Chapter 6: "Files and Buffer Management."
- See also: `database-internals/01` for the RAM/disk latency gap this component exploits, and `database-internals/03` for the B-Tree page-access patterns the buffer pool serves.
