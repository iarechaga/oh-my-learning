# Database Internals

A concept-by-concept recap of *Database Internals: A Deep Dive into How Distributed
Data Systems Work* by Alex Petrov. This subject moves from physical storage-engine
mechanics (Part I) into distributed replication, partitioning, and consensus
(Part II), so you can reason about why a data system behaves the way it does under
load and failure - not just recite component names.

Progress note: all 16 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded yet. This page
will gain per-concept detail (especially on concepts the learner finds hard) as
discussions happen - the seniority spans mid (foundational hardware/IO framing) up
through senior (most of Part I and early Part II) to staff (engine architecture,
partitioning, consensus, and production evolution).

See the progress table in [README.md](README.md). Reading order is top to bottom:
storage foundations first, then transactional/engine architecture, then distributed
replication and consensus, ending with the operational synthesis lesson.

## Storage foundations

- **[database-internals/01] Hardware and IO foundations for storage engines** - the
  storage hierarchy's latency cliffs (RAM vs. SSD vs. HDD), why random I/O is
  catastrophically more expensive than sequential I/O, and why this single fact
  shapes every mechanism later in the subject (WAL, LSM-Trees, buffer pools).
  ([lesson](lessons/01-hardware-and-io-foundations.md))
- **[database-internals/02] Data layout and file organization on disk** - the page
  as the atomic unit of I/O, slotted pages for variable-length records, heap vs.
  clustered file organization, and checksums for detecting torn writes.
  ([lesson](lessons/02-data-layout-and-file-organization.md))
- **[database-internals/03] B-Tree fundamentals and page-oriented indexing** - why
  high fan-out (not balance per se) is what keeps a B-Tree shallow (3-4 levels for
  billions of rows), how splits and merges work, and latch crabbing for concurrency.
  ([lesson](lessons/03-b-tree-fundamentals.md))
- **[database-internals/04] Write-ahead logging and crash recovery basics** - the
  WAL-before-data ordering rule, the three-pass (analysis/redo/undo) recovery
  algorithm, checkpoints, and group commit for batching fsyncs.
  ([lesson](lessons/04-write-ahead-logging-and-recovery.md))
- **[database-internals/05] Buffer management, caching, and compaction pressure** -
  the buffer pool's hit/miss economics, eviction policies (LRU, CLOCK, 2Q) and why
  plain LRU fails under sequential flooding, dirty-page flush, and how LSM
  compaction competes with foreground cache effectiveness.
  ([lesson](lessons/05-buffer-management-and-caching.md))

## The LSM-Tree family and engine selection

- **[database-internals/06] LSM-Tree design and the read-write amplification
  trade-off** - the memtable+WAL write path, flush-to-SSTable, the RUM conjecture
  (Read, Update, Memory amplification can't all be minimized at once), and how this
  contrasts with a B-Tree's trade-off point.
  ([lesson](lessons/06-lsm-tree-design.md))
- **[database-internals/07] SSTables, compaction strategies, and tombstones** -
  sparse indexes and Bloom filters inside an SSTable, how deletes work via
  tombstones in an append-only structure, and size-tiered vs. leveled compaction's
  differing amplification trade-offs.
  ([lesson](lessons/07-sstables-compaction-and-tombstones.md))
- **[database-internals/08] B-Tree vs LSM-Tree: workload-driven engine selection** -
  a four-axis decision framework (read:write ratio, write pattern, latency
  variance tolerance, space/wear efficiency) plus worked examples covering
  read-heavy OLTP, write-heavy ingestion, and genuinely bimodal workloads that
  warrant segmenting storage by entity type.
  ([lesson](lessons/08-b-tree-vs-lsm-selection.md))
- **[database-internals/09] In-memory structures and lock-free indexing patterns** -
  why skip lists (not balanced trees) back the memtable, how their local,
  rotation-free splicing enables CAS-based lock-free concurrent inserts, and why
  readers never need to coordinate with writers.
  ([lesson](lessons/09-in-memory-structures-and-lock-free-indexing.md))

## Transactions and engine architecture

- **[database-internals/10] Transaction internals: MVCC, snapshots, and isolation
  mechanics** - version tagging and snapshot visibility rules, write-write conflict
  detection (first-committer-wins), why long-running transactions block garbage
  collection table-wide, and how named isolation levels map to snapshot-timing
  rules.
  ([lesson](lessons/10-transaction-internals-mvcc-and-isolation.md))
- **[database-internals/11] Engine architecture: separating storage, execution, and
  control planes** - why storage, execution, and control have genuinely different
  scaling/failure characteristics, the modern storage-compute separation pattern
  (Aurora-style), and the staff-level judgment call of when separation is worth its
  added operational surface.
  ([lesson](lessons/11-engine-architecture-planes.md))

## Distributed replication and consensus

- **[database-internals/12] Replication logs, shipping models, and durability
  semantics** - statement/physical/logical replication trade-offs, the
  synchronous-vs-asynchronous durability/availability spectrum, and the concrete
  failure sequence under which async replication silently loses an acknowledged
  write.
  ([lesson](lessons/12-replication-logs-and-durability.md))
- **[database-internals/13] Quorums, anti-entropy, and conflict resolution in
  replicated stores** - the W+R>N quorum-overlap guarantee, sloppy quorums and
  hinted handoff, vector clocks vs. last-write-wins for genuine write-write
  conflicts, and Merkle-tree anti-entropy for catching divergence in cold data.
  ([lesson](lessons/13-quorums-anti-entropy-and-conflict-resolution.md))
- **[database-internals/14] Partitioning internals and rebalancing algorithms** -
  why naive modulo hash partitioning collapses under rebalancing (~80% of keys move
  when going from 4 to 5 nodes), how consistent hashing bounds movement to ~1/N,
  and how virtual nodes fix consistent hashing's load-imbalance weakness.
  ([lesson](lessons/14-partitioning-internals-and-rebalancing.md))
- **[database-internals/15] Consensus internals with Raft and log agreement
  mechanics** - terms as a logical clock that forces stale leaders to step down,
  randomized election timeouts preventing split votes, majority-based log
  commitment, and why a minority partition can structurally never make progress.
  ([lesson](lessons/15-consensus-internals-with-raft.md))

## Operating a distributed storage engine

- **[database-internals/16] Building and evolving a distributed storage engine in
  production** - synthesizes the whole subject into operational judgment: revisiting
  engine choice as workload drifts, staged (zero-downtime) rebalancing, tunable
  per-operation consistency, and safe phased rollouts of breaking format/protocol
  changes across a live, heterogeneous-version cluster.
  ([lesson](lessons/16-evolving-a-distributed-storage-engine.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
