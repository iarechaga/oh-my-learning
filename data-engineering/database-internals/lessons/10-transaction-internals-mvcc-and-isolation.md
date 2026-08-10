---
id: database-internals/10
subject: database-internals
title: "Transaction Internals: MVCC, Snapshots, and Isolation Mechanics"
slug: transaction-internals-mvcc-and-isolation
status: drafted
mastery:
seniority: senior
source: Database Internals (Alex Petrov), Part II, Chapter 8 (Transaction Processing and Recovery)
prerequisites: [database-internals/04, database-internals/03]
created: 2026-08-10
updated: 2026-08-10
---

# Transaction Internals: MVCC, Snapshots, and Isolation Mechanics

## TL;DR
Multi-Version Concurrency Control (MVCC) implements transaction isolation by keeping multiple versions of each row (tagged with the transaction/timestamp that created them) rather than locking rows for reads, letting readers see a consistent snapshot of the database as of some point in time without blocking concurrent writers, and vice versa. Understanding MVCC at the mechanism level — how versions are tagged, when old versions are garbage-collected, and exactly what a "snapshot" means internally — is what turns isolation-level names (read committed, repeatable read, snapshot isolation) from vocabulary into something you can reason about under a specific failure scenario.

## The idea
Classic lock-based concurrency control (two-phase locking) makes readers and writers block each other: a reader takes a shared lock, a writer needs an exclusive lock, and they contend directly. This is correct but throughput-limiting — in a read-heavy system, readers constantly queue behind writers and vice versa. MVCC's insight: instead of readers and writers fighting over *one* copy of a row, keep *multiple* versions of the row around, each tagged with when it was created (and, for old versions, when it was superseded). A reader doesn't need to lock anything — it just picks the version of each row that was current as of its own snapshot start time, and reads that version, even if a writer is concurrently creating a newer version. Readers never block writers, and writers never block readers; only writer-writer conflicts need locking (or an equivalent conflict-detection mechanism).

## How it works

### Version tagging: how MVCC identifies "which version is this?"
Every row version is tagged with metadata identifying its validity window — commonly a `(created_by_txn, created_at_ts)` and, once superseded, a `(deleted_by_txn, deleted_at_ts)`. A transaction reading under snapshot isolation is itself assigned a **snapshot timestamp** (or an equivalent, like a list of transaction IDs considered "in progress" at its start) when it begins, and for any row it reads, it picks the version whose validity window contains that snapshot timestamp — i.e. the version that was "current" at the moment the transaction's snapshot was taken, ignoring any versions created by transactions that started later or that are still in-flight.

**Worked example — a snapshot read during a concurrent write.** Row `X` currently has version V1 (`created_by: T1, ts=100`), i.e., X was last written by transaction T1 which committed at logical time 100. Transaction T5 begins at logical time 150, taking a snapshot as of ts=150. Concurrently, transaction T7 (which started at ts=140 and is still running) updates row X, creating V2 (`created_by: T7`, not yet committed). T5's read of X must pick V1, not V2 — even though V2 physically exists in the table by the time T5 reads — because V2 was created by a transaction (T7) that hadn't committed as of T5's snapshot time, and MVCC visibility rules exclude uncommitted (and not-yet-started-at-snapshot-time) versions. If T7 later commits at ts=160, that still doesn't matter to T5, which took its snapshot at ts=150 — T5 continues to see V1 for the entire duration of its transaction, which is precisely what gives snapshot isolation its "consistent, unchanging view" guarantee.

### Write-write conflicts: where locking (or its equivalent) still applies
MVCC eliminates reader-writer blocking, but two transactions trying to *write* the same row concurrently still need a conflict-resolution mechanism, because you can't have two uncommitted versions of the same row simultaneously without a defined winner. Two common approaches:
- **First-committer-wins (optimistic)**: both transactions proceed and create their own tentative version; whichever commits first succeeds, and the second transaction, upon attempting to commit, detects that the row it based its write on has since been modified by another committed transaction and is forced to abort (and typically retry).
- **First-updater-wins (a form of pessimistic locking layered on top of MVCC)**: the first transaction to attempt the write acquires a row-level write lock immediately; a second concurrent writer blocks until the first commits or aborts, then proceeds (or, in stricter modes, aborts directly if the conflict would violate the isolation level).

**Worked example — first-committer-wins conflict.** Transactions T1 and T2 both start with snapshot ts=100, both read row `Y` (current value: balance=500), and both attempt to update it (T1: balance=500-50=450; T2: balance=500-30=470) based on the value they read. T1 commits first, creating V2 of row Y with balance=450. When T2 attempts to commit, the engine detects that row Y has been modified by a transaction (T1) that committed after T2's snapshot was taken — this is a write-write conflict. Under first-committer-wins, T2's commit is rejected; T2 must abort and retry (re-reading the now-current balance=450 and recomputing its update against that). Without this check, T2 would silently overwrite T1's committed change, losing T1's update entirely (the classic **lost update** anomaly).

### Garbage collection of old versions
Old row versions aren't kept forever — once no active (or future) transaction's snapshot could possibly need to see a given old version (i.e., every transaction that started before that version was superseded has since completed), it becomes eligible for cleanup. Different engines implement this differently:
- **PostgreSQL's `VACUUM`**: a background process that scans tables for dead (superseded, no-longer-visible-to-anyone) row versions and reclaims their space, since PostgreSQL stores old and new versions in the same heap file (this is *why* PostgreSQL needs regular vacuuming — without it, table bloat from accumulated dead versions degrades performance and can eventually exhaust transaction ID space).
- **LSM-Tree-backed MVCC stores**: old versions age out naturally via the same compaction process covered in `database-internals/07`, since each version is effectively just another timestamped write, and compaction can drop versions no longer visible to any live snapshot the same way it drops tombstoned/superseded keys.

**Worked example — a long-running transaction blocking garbage collection.** A long-running analytical query starts a transaction with snapshot ts=1000 and takes 20 minutes to complete, during which thousands of other transactions commit updates to rows the analytical query never even touches. Because MVCC garbage collection must preserve every version that could still be visible to *any* active transaction's snapshot, and the analytical transaction's snapshot is pinned at ts=1000, the garbage collector cannot reclaim *any* version created after ts=1000 for *any* row, table-wide, until that long-running transaction finishes — not just rows the query reads. This is the well-known "long-running transaction bloats the database" operational problem, and it's a direct, mechanistic consequence of how MVCC visibility and garbage collection interact, not an implementation bug.

### Isolation levels as different visibility rules over the same MVCC machinery
The named SQL isolation levels are, under MVCC, really just different rules for *when* a transaction's snapshot timestamp is taken and re-taken:
- **Read committed**: the transaction takes a *fresh* snapshot for every individual statement (not once for the whole transaction) — so two SELECTs in the same transaction can see different committed data if another transaction committed in between.
- **Repeatable read / snapshot isolation**: the transaction takes one snapshot at the start and uses it for every statement in that transaction — guaranteeing every read within the transaction sees a single, consistent point-in-time view, but still permitting write skew anomalies in the absence of full serializability (a scenario where two transactions independently read overlapping data, each makes a decision valid against what they read, but the combination of both committed decisions violates an invariant neither transaction's individual read/write set would have caught).
- **Serializable**: typically layered on top of snapshot isolation via additional conflict detection (serializable snapshot isolation, SSI) that tracks read-write dependencies between concurrent transactions and aborts one if their combined effect couldn't have arisen from *some* serial (one-at-a-time) execution order.

## Pros
- Readers never block writers and writers never block readers, which is a major throughput win over pure two-phase locking for read-heavy workloads.
- Snapshot isolation gives a genuinely simple mental model ("as if I have a private, unchanging copy of the database from the moment I started") that's easy to reason about for most application code.
- MVCC's versioning naturally supports time-travel/point-in-time query features as a side benefit in some engines.

## Cons
- Old-version accumulation requires active garbage collection (vacuum/compaction), and long-running transactions can block that cleanup, causing table bloat and, in pathological cases, severe performance degradation.
- Snapshot isolation alone does not prevent write skew — genuine serializability requires additional machinery (SSI or locking) with its own cost (aborts under contention).
- Write-write conflict handling (first-committer-wins) means application code must be prepared to handle and retry aborted transactions, adding complexity compared to a lock-based model where a writer simply waits rather than being rejected after doing work.

## Alternatives
- **Two-phase locking (2PL)** — the classic alternative, where readers and writers directly block each other via shared/exclusive locks; simpler to reason about for write conflicts (blocking, not aborting) but sacrifices the read/write non-blocking property MVCC provides.
- **Optimistic concurrency control (OCC) without full MVCC versioning** — validates at commit time using read/write sets rather than keeping full historical versions, similar in spirit to first-committer-wins but without necessarily retaining old versions for long-running readers.

## When to use it
MVCC is the right default for read-heavy or mixed OLTP workloads where minimizing reader-writer contention matters — which is why it's the default (or the only) concurrency model in PostgreSQL, MySQL/InnoDB, Oracle, and most modern relational and many NoSQL engines.

## When NOT to use it
Be cautious relying on plain snapshot isolation (without SSI or explicit locking) for logic sensitive to write-skew anomalies — e.g. enforcing an invariant across two rows read independently by concurrent transactions (like ensuring the sum of two account balances never goes negative) needs either serializable isolation or explicit application-level locking, not snapshot isolation alone.

## Key takeaways / mental model
Picture MVCC as a library where every book has a full edit history bound into it: when you check it out (start a transaction), you're handed the edition that was current the moment you walked in, and no one can change the pages in *your* copy even if the library keeps publishing new editions while you're reading — but if you try to submit your own edit and someone already published a newer edition since you checked your copy out, your edit is rejected and you must start over from the latest edition. The library periodically pulps old editions (garbage collection) — but only once it's sure no one still checked out with that edition is still reading.

## Self-check questions
1. Walk through why a transaction under snapshot isolation continues to see the same row version throughout its lifetime even as other transactions commit changes to that row in the meantime — what specific rule makes this true?
2. Explain the lost-update anomaly that first-committer-wins conflict detection prevents, and describe a concrete scenario (different from the balance example above) where skipping this check would silently corrupt data.
3. A production PostgreSQL database is suffering severe table bloat despite `VACUUM` running on schedule. A common root cause is a long-running, idle-in-transaction connection. Explain, mechanistically, why that specific situation blocks vacuuming table-wide rather than just for the rows that connection touched.
4. Describe a concrete write-skew scenario (two concurrent transactions, each individually valid under snapshot isolation, whose combination violates a business invariant) and explain what additional mechanism (beyond plain snapshot isolation) would be needed to prevent it.

## References
- Database Internals (Alex Petrov), Part II, Chapter 8: "Transaction Processing and Recovery."
- See also: `database-internals/04` for the WAL/recovery machinery transactions rely on, and `ddia/11`-equivalent isolation-level framing in the DDIA subject for a complementary treatment.
