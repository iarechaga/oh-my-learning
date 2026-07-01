# Database Internals: A Deep Dive into How Distributed Data Systems Work

This subject explains how data systems behave beneath APIs and query languages.
You will move from storage-engine mechanics into distributed operation, learning
which trade-offs are fundamental and which are implementation choices. The goal
is to reason about behavior under load and failure, not just memorize components.

**Source book:** *Database Internals: A Deep Dive into How Distributed Data Systems Work* - Alex Petrov (O'Reilly, 2019).

**Seniority baseline:** senior (lessons range mid->staff).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`database-internals/<NN>`* (e.g. *"discuss `database-internals/03`"*). Ordered by dependency: physical storage and indexing first, then transactional and engine architecture, then distributed replication and consensus.

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Hardware and IO foundations for storage engines | mid | drafted | — | — | [lesson](lessons/01-hardware-and-io-foundations.md) | — |
| 02  | Data layout and file organization on disk | senior | drafted | — | — | [lesson](lessons/02-data-layout-and-file-organization.md) | — |
| 03  | B-Tree fundamentals and page-oriented indexing | senior | drafted | — | — | [lesson](lessons/03-b-tree-fundamentals.md) | — |
| 04  | Write-ahead logging and crash recovery basics | senior | drafted | — | — | [lesson](lessons/04-write-ahead-logging-and-recovery.md) | — |
| 05  | Buffer management, caching, and compaction pressure | senior | drafted | — | — | [lesson](lessons/05-buffer-management-and-caching.md) | — |
| 06  | LSM-tree design and the read-write amplification trade-off | senior | drafted | — | — | [lesson](lessons/06-lsm-tree-design.md) | — |
| 07  | SSTables, compaction strategies, and tombstones | senior | drafted | — | — | [lesson](lessons/07-sstables-compaction-and-tombstones.md) | — |
| 08  | B-Tree vs LSM-tree: workload-driven engine selection | senior | drafted | — | — | [lesson](lessons/08-b-tree-vs-lsm-selection.md) | — |
| 09  | In-memory structures and lock-free indexing patterns | senior | drafted | — | — | [lesson](lessons/09-in-memory-structures-and-lock-free-indexing.md) | — |
| 10  | Transaction internals: MVCC, snapshots, and isolation mechanics | senior | drafted | — | — | [lesson](lessons/10-transaction-internals-mvcc-and-isolation.md) | — |
| 11  | Engine architecture: separating storage, execution, and control planes | staff | drafted | — | — | [lesson](lessons/11-engine-architecture-planes.md) | — |
| 12  | Replication logs, shipping models, and durability semantics | senior | drafted | — | — | [lesson](lessons/12-replication-logs-and-durability.md) | — |
| 13  | Quorums, anti-entropy, and conflict resolution in replicated stores | staff | drafted | — | — | [lesson](lessons/13-quorums-anti-entropy-and-conflict-resolution.md) | — |
| 14  | Partitioning internals and rebalancing algorithms | staff | drafted | — | — | [lesson](lessons/14-partitioning-internals-and-rebalancing.md) | — |
| 15  | Consensus internals with Raft and log agreement mechanics | staff | drafted | — | — | [lesson](lessons/15-consensus-internals-with-raft.md) | — |
| 16  | Building and evolving a distributed storage engine in production | staff | drafted | — | — | [lesson](lessons/16-evolving-a-distributed-storage-engine.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Seniority:** `junior` · `mid` · `senior` · `staff` · `principal` - the band whose job the concept anchors.

**Cross-subject prerequisites:** helpful background from `ddia/04` (storage engines), `ddia/07` (replication), `ddia/10` (partitioning), and `ddia/13` (consensus and coordination).
