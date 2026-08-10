---
id: database-internals/12
subject: database-internals
title: "Replication Logs, Shipping Models, and Durability Semantics"
slug: replication-logs-and-durability
status: drafted
mastery:
seniority: senior
source: Database Internals (Alex Petrov), Part II, Chapter 10 (Replication and Consistency)
prerequisites: [database-internals/04, database-internals/11]
created: 2026-08-10
updated: 2026-08-10
---

# Replication Logs, Shipping Models, and Durability Semantics

## TL;DR
Replication takes the write-ahead log mechanism from `database-internals/04` — already the source of truth for recovering a single node — and ships it to other nodes, so that a replica can reconstruct the same state by replaying the same sequence of changes. The precise choice of *what* gets shipped (statements, the WAL itself, or logical row-level changes) and *when* the leader waits for replica acknowledgment (synchronous vs. asynchronous) together determine the system's durability, consistency, and availability trade-offs under node failure.

## The idea
A single node's WAL (`database-internals/04`) already solves "how do I recover my own state after a crash" by replaying a sequential log of changes. Replication asks a related but distinct question: "how do I keep a *second* node's state consistent with the first, in real time, so that if the first node dies entirely, the second can take over?" The elegant reuse at the heart of this lesson: the same log that gives single-node crash recovery its correctness (redo/undo, `database-internals/04`) is also, almost for free, exactly the artifact you need to ship to a replica — a replica that faithfully replays the leader's log ends up in the same state the leader was in, without needing a fundamentally different mechanism.

## How it works

### What gets shipped: statement-based, WAL-based (physical), and logical/row-based
- **Statement-based replication**: ship the original SQL statements (e.g. `UPDATE accounts SET balance = balance - 50 WHERE id = 7`) and re-execute them on the replica. Compact, but fragile — any non-deterministic statement (using `NOW()`, `RAND()`, auto-increment values assigned differently) can produce divergent results on leader vs. replica if not handled carefully.
- **WAL-based (physical) replication**: ship the raw write-ahead log records themselves (`database-internals/04`) — literally "page X, offset Y, change these bytes." Extremely faithful (the replica ends up byte-for-byte identical, since it's replaying the exact same low-level operations), but tightly coupled to the storage engine's internal format — a replica typically must run the exact same storage engine version, since the WAL format is an internal implementation detail, not a portable interface.
- **Logical (row-based) replication**: ship a higher-level description of the change (e.g. "row with primary key 7 in table accounts changed column balance from 500 to 450"), decoupled from physical storage layout. More portable (can replicate across different storage engine versions, or even into a different system entirely, like a data warehouse or a search index) at the cost of being derived/reconstructed from the physical WAL rather than being the WAL itself, adding a translation step.

**Worked example — why WAL-based replication is fragile across versions.** A leader running storage engine version 12 ships physical WAL records that reference an internal page-layout format specific to version 12 (`database-internals/02`). If the replica is running version 13, which changed its internal page/slot layout, applying version-12 WAL records to a version-13 page structure is either meaningless or actively corrupting — this is exactly why physical/WAL-based replication typically requires leader and replicas to run identical (or very tightly version-matched) storage engine builds, unlike logical replication, which can tolerate more version skew since it operates at the "what changed logically" level rather than "what bytes changed physically."

### Synchronous vs. asynchronous replication: the durability/availability trade-off
Once the leader has generated a log record for a write, when does it acknowledge the write as "committed" to the client?
- **Asynchronous replication**: the leader acknowledges the write as soon as it's durable *locally* (its own WAL fsync completes, `database-internals/04`), without waiting for any replica to receive or apply it. Fastest write latency, but if the leader crashes before a replica catches up, that committed-and-acknowledged write can be lost entirely when a replica is promoted to leader — the classic **replication lag** durability gap.
- **Synchronous replication**: the leader waits for at least one replica to acknowledge receiving (and often durably persisting) the log record before acknowledging the write to the client. No data loss if the leader crashes immediately after (the synchronous replica has it too), but write latency now includes a network round-trip to the replica, and — critically — if that replica becomes unreachable, the leader either blocks writes entirely (strict durability, but the system becomes unavailable for writes) or must fail over to asynchronous mode temporarily (a documented, deliberate durability/availability trade decision, not a silent one).
- **Semi-synchronous replication**: a middle ground — the leader waits for acknowledgment from at least one of several replicas (not all), balancing durability improvement against not being fully blocked by any single replica's unavailability.

**Worked example — the durability gap under asynchronous replication.** A leader acknowledges write W to the client the instant its local WAL fsync completes, then immediately begins asynchronously shipping W's log record to its replica — but before that shipment completes (say, a 5 ms network delay), the leader's host crashes. The replica never received W's log record. If the replica is now promoted to be the new leader (a common failover response), W is permanently lost, despite having been acknowledged as "committed" to the original client. This exact scenario is why financial and other durability-critical systems typically require at least synchronous (or semi-synchronous) replication for the specific class of writes where losing an acknowledged transaction is unacceptable, accepting the added write latency as the cost of that guarantee.

### Log shipping cadence: continuous streaming vs. batch shipping
- **Continuous/streaming replication**: the leader ships log records to replicas as they're generated, in near real-time — minimizes replication lag, the standard approach in most modern systems (PostgreSQL streaming replication, MySQL binlog streaming).
- **Batch/periodic log shipping**: the leader ships accumulated log segments at intervals (e.g. every few minutes, or when a WAL segment file fills) — simpler, lower network overhead, but introduces larger, bounded replication lag by design, more common in older or simpler replication setups, or for shipping to a geographically distant, non-latency-critical standby.

**Worked example — measuring replication lag's real-world impact.** A replica configured for continuous streaming typically lags the leader by milliseconds to low seconds under normal load (network RTT plus apply time). If that same system used 5-minute batch log shipping instead, a client reading from the replica immediately after a write to the leader could see data up to 5 minutes stale — this concretely illustrates why the choice of shipping cadence directly determines how "read-your-writes"-capable a read-replica architecture can be (see `ddia/09` for the DDIA-level treatment of replication lag and the specific consistency anomalies — stale reads, monotonic-read violations — it produces).

### Failover and the log's role in re-establishing consistency
When a replica is promoted to leader after the original leader fails, the new leader must ensure its own log is at least as far along as anything any client might have seen acknowledged. If replication was asynchronous and the old leader had unshipped log entries at the moment of failure, those entries are gone — but more subtly, if the old leader recovers and rejoins the cluster later, it may have log entries that were never shipped and that conflict with what the new leader has since done (a **split-brain**-adjacent divergence). Correct failover protocols require the recovering old leader to discard (or reconcile) any of its own unshipped, now-superseded log entries before rejoining as a replica — treating the new leader's log as authoritative going forward. This exact reconciliation problem is a major reason quorum-based and consensus-based replication schemes (`database-internals/13`, `database-internals/15`) exist: they make it structurally impossible for two nodes to simultaneously believe they're both the authoritative leader with diverging logs, rather than relying on operational discipline to catch and fix divergence after the fact.

## Pros
- Reusing the WAL as the replication artifact means correctness-critical logic (ordering, durability semantics) doesn't need to be reinvented separately for replication versus single-node recovery.
- The sync/async/semi-sync spectrum gives operators an explicit, tunable lever matching durability guarantees to actual business requirements per write (or per system).
- Logical replication's storage-engine independence enables powerful use cases beyond simple failover — feeding search indexes, data warehouses, or cross-version migrations from the same replication stream.

## Cons
- Physical/WAL-based replication's tight coupling to storage engine internals limits flexibility (same-version requirement) even though it's the most efficient and faithful option.
- Synchronous replication's latency and availability cost is real and must be explicitly budgeted for — it's not a free durability upgrade.
- Asynchronous replication's silent, unbounded-in-the-worst-case durability gap is an easy trap for teams who assume "replicated" implies "no data loss risk" without understanding the acknowledgment timing.

## Alternatives
- **Multi-leader or leaderless replication** (covered from a conflict-resolution angle in `database-internals/13`) — accepts writes at multiple nodes simultaneously rather than funneling all writes through one leader's log, trading this lesson's single-log-ordering simplicity for higher write availability at the cost of needing explicit conflict resolution.
- **Consensus-based replicated logs** (`database-internals/15`) — instead of a single leader unilaterally deciding the log order and shipping it, use a consensus protocol (Raft) so that a log entry is only considered committed once a quorum of nodes has durably accepted it — closing the asynchronous-replication durability gap structurally, at the cost of requiring a live quorum to make any progress at all.

## When to use it
Use asynchronous replication for read-scaling replicas and disaster-recovery standbys where a small, bounded durability/staleness window is acceptable in exchange for lower write latency. Use synchronous or semi-synchronous replication (or move to consensus-based replication, `database-internals/15`) for any write path where losing an acknowledged transaction is unacceptable (financial transactions, inventory commits with real-world consequences).

## When NOT to use it
Don't rely on asynchronous replication alone as your durability story for critical writes — "we have a replica" is not the same guarantee as "we cannot lose an acknowledged write," and conflating the two is a common, expensive production mistake. Don't default to full synchronous replication for high-throughput, latency-sensitive workloads where the write-latency cost of waiting on every replica isn't justified by the actual durability requirements of that data.

## Key takeaways / mental model
Replication is dictation: the leader reads its log aloud (ships WAL/logical records), and the replica writes down exactly what it hears, in order, to end up with the same document. Asynchronous replication is dictation over a delayed phone line — you keep talking without confirming the listener heard the last sentence, so if you're cut off, the listener's copy might be missing your most recent words even though you already told your boss "it's written down." Synchronous replication is dictation where you pause after every sentence until the listener confirms they wrote it down before you continue — safer, but you talk slower.

## Self-check questions
1. Explain concretely why WAL-based (physical) replication typically requires leader and replica to run matching storage engine versions, while logical replication tolerates version skew — tie this back to `database-internals/02`'s page format discussion.
2. Walk through the exact failure sequence under which asynchronous replication loses an acknowledged write, and identify the precise point at which switching to synchronous replication would have prevented that loss.
3. A system uses semi-synchronous replication (wait for 1 of 3 replicas). Explain why this is a meaningful durability improvement over pure asynchronous replication, but still doesn't provide the same guarantee as waiting for all replicas or a majority quorum (`database-internals/13`).
4. Describe the split-brain-adjacent divergence risk when a failed leader recovers and rejoins after a new leader was promoted, and explain in one sentence why consensus-based replication (`database-internals/15`) structurally prevents this rather than just operationally discouraging it.

## References
- Database Internals (Alex Petrov), Part II, Chapter 10: "Replication and Consistency."
- See also: `database-internals/04` for the WAL mechanics this lesson's replication log builds on, and `ddia/07`/`ddia/09` for the DDIA-level replication and replication-lag framing.
