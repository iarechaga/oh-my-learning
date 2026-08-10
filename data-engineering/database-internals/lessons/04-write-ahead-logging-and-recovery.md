---
id: database-internals/04
subject: database-internals
title: "Write-Ahead Logging and Crash Recovery Basics"
slug: write-ahead-logging-and-recovery
status: drafted
mastery:
seniority: senior
source: Database Internals (Alex Petrov), Part I, Chapter 7 (Log-Structured Storage) and Part II, Chapter 10 (Replication and Consistency, WAL foundations)
prerequisites: [database-internals/02, database-internals/03]
created: 2026-08-10
updated: 2026-08-10
---

# Write-Ahead Logging and Crash Recovery Basics

## TL;DR
A write-ahead log (WAL) is an append-only, sequential record of every change before it is applied to the actual data pages, so that if the process crashes mid-write, the engine can replay the log on restart to reconstruct exactly the state it was in — no more, no less. WAL turns "was this change durable?" into a question answered by one sequential log file, rather than by trusting the consistency of scattered, randomly-updated data pages.

## The idea
Recall from `database-internals/02` and `database-internals/03` that updating a B-Tree page in place risks a torn write (a crash mid-write leaves the page in a state that's neither fully old nor fully new). If a database simply wrote directly to data pages and crashed mid-write, recovery would be nearly impossible: you can't tell what the intended change was from a half-written page. The write-ahead logging principle solves this by decoupling *durability* from *applying the change to its final location*: first durably record "here is the change I intend to make" in a simple, append-only log; only then apply that change to the actual (harder-to-recover) data pages. On crash, replay whatever log entries exist to bring data pages back to a consistent state, because the log itself — being append-only — is far less prone to the corruption a random in-place write is exposed to.

## How it works

### The WAL rule: log before data
The core invariant, sometimes called the **WAL rule** or **ARIES rule** (from the classic ARIES recovery algorithm): a change to a data page must not be flushed to disk before the corresponding log record describing that change has been flushed to disk. This ordering guarantee is what makes recovery possible — if a crash happens, you're guaranteed that any change visible in a data page on disk was *also* logged, so the log is always a superset (or equal) description of what actually happened to the data, never a subset.

**Worked example — why the ordering matters.** Suppose the ordering were reversed: a data page update is flushed to disk *before* its log record. A crash occurs in that gap. On restart, the data page reflects the change, but the log doesn't mention it — recovery has no way to know this change happened, and worse, no way to *undo* it if it turns out the transaction that made the change was never committed (was rolled back or never finished). With the correct WAL-before-data ordering, the reverse failure mode is instead: the log describes a change that never made it to the data page. That's the *safe* failure mode, because replaying the log on restart re-applies exactly that missing change — recovery can always move forward from "log says X, data hasn't caught up" but can never safely reconstruct from "data says X, log doesn't know."

### Anatomy of a log record
Each log entry typically contains: a monotonically increasing **log sequence number (LSN)**, the transaction ID that made the change, the page ID affected, enough information to redo the change (and often enough to undo it), and a checksum. Log records are appended sequentially to the log file/segment — pure sequential I/O, the cheapest kind (`database-internals/01`) — and each data page, once modified, stores the LSN of the log record that most recently changed it, directly in the page header. That per-page LSN is the key that later lets recovery figure out precisely which log records still need to be replayed against which pages.

### The three-pass recovery algorithm: analysis, redo, undo
Classic WAL-based recovery (as formalized in ARIES) runs in three passes over the log after a crash:

1. **Analysis pass** — scan the log forward from the last checkpoint (see below) to determine which transactions were in-flight (neither committed nor rolled back) at the time of the crash, and which data pages were "dirty" (modified but not yet flushed) at that time.
2. **Redo pass** — replay the log forward, re-applying every logged change whose LSN is greater than the page's stored LSN (meaning the change hadn't made it to disk before the crash) — this brings the database back to *exactly* the state it was in at the moment of the crash, including changes from transactions that hadn't committed yet.
3. **Undo pass** — walk backward through the log and undo the changes made by any transaction that was still in-flight (uncommitted) at crash time, restoring atomicity — a transaction is all-or-nothing, so partial, uncommitted work must be rolled back even though it was redone in step 2.

**Worked example — redo then undo.** Transaction T1 updates row A (committed) and transaction T2 updates row B then crashes before committing. On restart: analysis finds T2 was in-flight. Redo replays *both* T1's and T2's changes from the log (bringing pages back to their exact pre-crash state, uncommitted work included — this is intentional, it's simpler to redo everything and then selectively undo than to try to redo only "the right" subset). Undo then walks the log backward and reverses T2's change to row B specifically (using undo information in T2's log records), while leaving T1's committed change to row A intact. The net effect matches exactly what should have happened: T1's committed work survives, T2's uncommitted work vanishes.

### Checkpoints: bounding how much log must be replayed
Without checkpoints, recovery would have to scan the *entire* log from the beginning of time, which becomes impractically slow as a database runs for months or years. A **checkpoint** periodically records a snapshot of "which transactions are currently active" and "which dirty pages exist and their oldest unflushed LSN," and recovery only needs to start its analysis pass from the most recent checkpoint, not from the start of the log.

**Worked example — checkpoint interval trade-off.** A database checkpoints every 5 minutes. If it crashes 4 minutes after the last checkpoint, recovery only needs to replay ~4 minutes of log — fast. If checkpoints were taken every hour instead, a crash near the end of that hour means replaying up to an hour's worth of log — much slower recovery, but with less overhead spent taking checkpoints during normal operation (a checkpoint itself has a cost: it typically forces some dirty pages to flush). This is a direct availability/overhead trade-off: frequent checkpoints shrink recovery time (better availability after a crash) at the cost of more background I/O during normal operation.

### Group commit: batching fsyncs for throughput
As established in `database-internals/01`, calling `fsync` on every single transaction commit is prohibitively slow (each fsync costs roughly a disk-seek's worth of latency). **Group commit** batches multiple transactions' log records into a single fsync: the engine buffers log records from several concurrently-committing transactions for a short window (often just a few milliseconds, or until a buffer fills), then issues one fsync covering all of them, and only then acknowledges all those transactions as committed together.

**Worked example — throughput math.** Suppose a single fsync costs 5 ms. Without group commit, committing transactions one at a time caps throughput at `1000ms / 5ms = 200` transactions/second, no matter how fast the CPU is. With group commit batching 50 transactions per fsync (achievable if transactions arrive faster than the fsync latency, which is common under concurrent load), the same single 5 ms fsync now covers 50 commits, raising effective throughput to `50 * 200 = 10,000` transactions/second — a 50x improvement, at the cost of each individual transaction's commit latency growing slightly (it must wait for the batch window to close, e.g. up to a few ms, rather than being acknowledged the instant its own fsync returns).

### WAL vs. the data files: two different durability tiers
It's worth being explicit that the WAL and the actual data pages are durabilized on different schedules: the WAL is fsynced frequently (on every commit or commit-batch, since that's the durability contract), while dirty data pages are flushed to disk lazily, on the buffer pool's own schedule (`database-internals/05`) — often minutes later, or only when evicted or checkpointed. This is safe *only* because of the WAL-before-data ordering rule: as long as the log record for a change reached disk before the corresponding data page write is even attempted, it's fine for the data page itself to lag far behind, because the log can always reconstruct it.

## Pros
- Converts recovery from "figure out what state scattered pages are in" into "replay one sequential file" — dramatically simpler and more robust than trying to make in-place page writes themselves atomic.
- Sequential log writes are cheap (`database-internals/01`), decoupling commit latency from the cost of the (potentially random) data-page writes it describes.
- Group commit lets a WAL-based engine achieve very high commit throughput despite fsync's inherent latency cost.

## Cons
- Every write pays a "write twice" tax: once to the log, once (eventually) to the data page — pure overhead in total I/O volume compared to a hypothetical crash-proof in-place write.
- Recovery time is proportional to log volume since the last checkpoint; a database that crashes right before a scheduled checkpoint, or that has checkpointing disabled/misconfigured, can have surprisingly long recovery/downtime.
- WAL correctness depends on strict ordering guarantees from the underlying storage (the log record really must hit stable storage before the data page write) — misconfigured storage (e.g. a disk cache that lies about fsync completion) silently breaks the entire recovery guarantee.

## Alternatives
- **Shadow paging / copy-on-write** (touched on in `database-internals/02`) — instead of logging changes and replaying them, never overwrite a page in place at all; atomicity comes from atomically swapping a root pointer to a new page tree, avoiding the need for redo/undo logging entirely, at the cost of extra write amplification up the tree on every change.
- **Log-structured storage with no separate data files** (LSM-Trees, `database-internals/06`) — the "log" and the durable data store become closer to the same thing; the memtable is recovered by replaying its own WAL, but the SSTables it flushes to are themselves immutable, sidestepping in-place page recovery concerns entirely.

## When to use it
Any engine that mutates data in place (B-Trees and similar page-oriented structures, `database-internals/03`) needs WAL-style logging to make crash recovery tractable — it's essentially mandatory infrastructure for that family of storage engine, not an optional add-on.

## When NOT to use it
Purely in-memory, non-durable caches (where losing all data on crash/restart is an accepted trade-off) don't need WAL machinery at all. Similarly, engines built entirely on copy-on-write/immutable-file principles need a different (simpler, in some ways) recovery story than classic ARIES-style redo/undo, since they never have a "torn in-place write" to recover from in the first place.

## Key takeaways / mental model
Think of the WAL as a ship's logbook kept in permanent ink, versus the cargo hold (data pages) that gets rearranged by hand and can be knocked over in a storm. You never trust the cargo hold's current arrangement after a storm — you trust the logbook, and you re-do every entry in it to rebuild the cargo hold's correct arrangement, then undo any entry for a delivery that was never actually finalized. The logbook is written in order, one line at a time, cheaply; the cargo hold is expensive and slow to rearrange, so you do that lazily and recover it from the logbook whenever needed.

## Self-check questions
1. Explain why the WAL-before-data ordering rule (not just "having a WAL" in general) is the specific property that makes crash recovery correct — what could go wrong if an engine had a WAL but didn't enforce that ordering?
2. Walk through why recovery needs both a redo pass and an undo pass rather than just one or the other — what would go wrong with redo-only recovery for an uncommitted transaction?
3. A team wants to reduce commit latency for a high-throughput OLTP workload with many small, concurrent transactions. Explain how group commit helps, and what specific trade-off (in terms of individual transaction latency) it introduces.
4. Why does a longer interval between checkpoints reduce steady-state overhead but increase the risk/impact of a bad crash? Given a database that needs to guarantee under-10-second recovery time after a crash, what checkpoint-interval decision does that imply?

## References
- Database Internals (Alex Petrov), Part I, Chapter 7: "Log-Structured Storage," and recovery algorithm background (ARIES).
- See also: `database-internals/01` for the sequential-vs-random I/O reasoning behind logging, and `database-internals/03` for the B-Tree page updates this recovery mechanism protects.
