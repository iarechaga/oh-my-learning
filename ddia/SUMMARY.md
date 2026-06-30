# DDIA - Subject Summary

A comprehensive recap of *Designing Data-Intensive Applications*, concept by concept.

**Progress note:** all 16 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom
(dependency-ordered).

## Part I - Foundations of Data Systems

- **[ddia/01] Reliability, scalability, maintainability** - the three non-functional
  lenses for any data system. Reliability = tolerating hardware, software, and human
  faults so a *fault* never becomes a *failure*. Scalability = describing load with
  load parameters and measuring performance with percentiles (p95/p99 tail latencies),
  never the mean. Maintainability = operability + simplicity + evolvability.
  ([lesson](lessons/01-reliability-scalability-maintainability.md))
- **[ddia/02] Data models** - relational (joins, strong at many-to-many), document
  (locality, natural one-to-many trees, schema-on-read), and graph (relationships as
  first-class, traversal-heavy). Match the model to the relationship shape.
  ([lesson](lessons/02-data-models.md))
- **[ddia/03] Query languages** - declarative (SQL) states *what* and lets the engine
  optimize and parallelize; imperative states *how* and freezes one strategy.
  MapReduce is the middle ground. ([lesson](lessons/03-query-languages.md))
- **[ddia/04] Storage engines** - two families: LSM-trees (append-only, SSTables,
  compaction, Bloom filters, write-optimized) vs B-trees (in-place updates, WAL,
  read-optimized). The trade-off is write amplification vs read/write throughput.
  ([lesson](lessons/04-storage-engines.md))
- **[ddia/05] OLTP vs OLAP** - transaction processing (row-oriented, small point
  access) vs analytics (large scans and aggregations). Data warehousing, star schemas,
  and column-oriented storage with compression speed analytic queries.
  ([lesson](lessons/05-oltp-olap-column-storage.md))
- **[ddia/06] Encoding and schema evolution** - binary schema formats (Thrift,
  Protocol Buffers, Avro) vs textual (JSON/XML). Backward and forward compatibility;
  Avro's reader/writer schemas; dataflow through databases, services, and message
  brokers. ([lesson](lessons/06-encoding-and-schema-evolution.md))

## Part II - Distributed Data

- **[ddia/07] Replication: single-leader** - one leader accepts writes, followers
  replicate from its log; synchronous vs asynchronous (durability vs latency); the
  dangers of failover (lost writes, split brain).
  ([lesson](lessons/07-replication-single-leader.md))
- **[ddia/08] Replication: multi-leader and leaderless** - multi-leader for
  multi-datacenter, offline, and collaborative editing, with write-conflict
  resolution; leaderless (Dynamo-style) with quorums (w + r > n), read repair,
  anti-entropy, and sloppy quorums.
  ([lesson](lessons/08-replication-multi-leader-leaderless.md))
- **[ddia/09] Replication lag and consistency** - asynchronous lag produces eventual
  consistency and visible anomalies; the guarantees that fix them are read-your-writes,
  monotonic reads, and consistent prefix reads.
  ([lesson](lessons/09-replication-lag-and-consistency.md))
- **[ddia/10] Partitioning (sharding)** - split data by key range (range scans, but
  hot spots) or by hash of key (even spread, no range queries); local vs global
  secondary indexes; rebalancing strategies; request routing.
  ([lesson](lessons/10-partitioning.md))
- **[ddia/11] Transactions** - ACID precisely (atomicity = abortability, consistency =
  application invariant, isolation, durability); the anomalies (dirty reads/writes,
  read skew, lost updates, write skew, phantoms); weak isolation (read committed,
  snapshot isolation via MVCC); and serializability (serial execution, 2PL, SSI).
  ([lesson](lessons/11-transactions.md))
- **[ddia/12] The trouble with distributed systems** - partial failure is the core
  difficulty. Unreliable networks (you cannot distinguish a slow node from a dead one;
  timeouts are the only tool), unreliable clocks (skew; never order by wall-clock
  time), and process pauses; truth is defined by majority, with fencing tokens to
  contain a paused leader. ([lesson](lessons/12-distributed-systems-trouble.md))
- **[ddia/13] Consistency and consensus** - linearizability (a recency guarantee, the
  single-copy illusion, with a CAP availability cost) vs the cheaper causal
  consistency; total order broadcast is equivalent to consensus; two-phase commit
  (blocking) vs consensus algorithms (Raft/Paxos/Zab); the FLP result; coordination
  via ZooKeeper/etcd. Note: linearizability is *not* serializability.
  ([lesson](lessons/13-consistency-and-consensus.md))

## Part III - Derived Data

- **[ddia/14] Batch processing** - bounded input, no time pressure. The Unix
  philosophy of composable tools; MapReduce (map, shuffle, reduce on a distributed
  filesystem); reduce-side vs map-side joins; immutable, idempotent, re-runnable
  outputs; dataflow engines (Spark, Flink) that improve on MapReduce.
  ([lesson](lessons/14-batch-processing.md))
- **[ddia/15] Stream processing** - unbounded, never-ending events. Traditional
  message brokers (AMQP/JMS) vs log-based brokers (Kafka, with replayable offsets);
  change data capture and event sourcing; stream joins; event time vs processing time;
  windowing and late events; exactly-once via idempotence.
  ([lesson](lessons/15-stream-processing.md))
- **[ddia/16] The future of data systems** - the synthesis chapter. Data integration
  by combining specialized tools with a log/stream backbone that keeps derived views
  (indexes, caches, warehouses) in sync; "unbundling the database"; the lambda
  architecture; designing for end-to-end correctness.
  ([lesson](lessons/16-future-of-data-systems.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on the concepts
rated `shaky` or `not-yet`.
