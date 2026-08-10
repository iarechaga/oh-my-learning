---
id: seven-databases/03
subject: seven-databases
title: "HBase: Wide-Column Modeling and Access-Pattern-First Design"
slug: hbase-wide-column-modeling
status: drafted
mastery:
seniority: mid
source: Seven Databases in Seven Weeks (Perkins, Redmond, Wilson), Chapter 3
prerequisites: [seven-databases/01, seven-databases/02]
created: 2026-08-10
updated: 2026-08-10
---

# HBase: Wide-Column Modeling and Access-Pattern-First Design

## TL;DR
HBase is a distributed, sorted, wide-column store built on Hadoop's HDFS, modeled after Google's Bigtable: data is organized by a single sorted row key into column families, and it scales to enormous volumes by splitting the key space across many servers (regions). Its defining discipline is that you design the row key and table layout around your *query patterns first*, before worrying about normalization — the opposite order from PostgreSQL's approach in `seven-databases/02`.

## The idea
PostgreSQL's relational model (`seven-databases/02`) assumes a single coordinating node can enforce cross-table correctness and answer arbitrary ad hoc joins. HBase abandons both assumptions to serve a different problem: petabyte-scale, high-write-throughput data (sensor logs, web crawl data, time-series metrics) that needs to be *written* fast, *scanned* in sorted order, and *scaled* by adding commodity machines rather than buying a bigger single machine.

To do this, HBase gives up joins, gives up a query planner, and gives up flexible ad hoc queries entirely. What you get in exchange: near-linear horizontal scalability, and extremely fast reads/writes when your access pattern matches the row-key design — because HBase is fundamentally a giant, distributed, sorted map from row key to column data, not a general-purpose query engine.

## How it works

### The data model: a sparse, sorted, multi-dimensional map
An HBase table is best understood as a map keyed by `(row key, column family:column qualifier, timestamp) -> value`. Rows are stored in sorted order by row key across the cluster, which is the single most important fact about HBase — it explains almost everything else about how you design a schema for it.

**Worked example.** A time-series table storing sensor readings might look like:

```
Row key: sensor042#20260810153000   (sensor ID + reverse-sortable timestamp)
Column family "reading":
  reading:temp     -> 21.4
  reading:humidity -> 55
Column family "meta":
  meta:battery -> 87
```

Each row can have a different set of columns within a column family — there's no fixed schema declaring "every row has exactly these five columns," unlike a PostgreSQL table. Column families, however, *are* declared upfront (they map to physical storage files), so you typically have few, stable column families (e.g., `reading`, `meta`) each holding many dynamically-named columns.

### Row key design is the whole game
Because HBase only really offers two access patterns efficiently — get a row by exact key, or scan a contiguous range of sorted keys — the row key must be designed so that the queries you actually need map onto "exact key" or "range scan."

**Worked example — good vs. bad row key.** Suppose you need "all readings for sensor042 in the last hour." A row key of `sensor042#20260810153000` (sensor ID first, timestamp second) makes this a contiguous range scan: all of sensor042's readings sort together, and within that, by time. A row key of `20260810153000#sensor042` (timestamp first) would scatter one sensor's readings across the entire keyspace, interleaved with every other sensor's readings at that moment — turning "all readings for sensor042" into a full table scan instead of a cheap range scan. This single design choice is the difference between a query that takes milliseconds and one that takes minutes at scale.

**Worked example — the hot-region problem.** A naive row key of `20260810153000` (timestamp only, ascending) causes every new write to land on whichever region currently holds the newest timestamps — one server absorbs 100% of write traffic while the rest of the cluster idles, defeating the purpose of horizontal scaling. The standard fix is to *salt* the key (prefix with a hash or a reversed/bucketed value) so writes spread across regions, at the cost of making "give me the most recent N readings across all sensors" a scatter-gather query instead of a simple scan.

### Column families and physical storage
Each column family is stored in its own set of files (HFiles) on HDFS, sorted by row key within the family. This means: read patterns that only need one column family (e.g., `reading` but not `meta`) can skip reading the other family's files entirely — a strong argument for grouping columns by *access pattern together*, not by logical relatedness. If `meta:battery` is rarely read alongside `reading:temp`, splitting them into separate families (as shown above) avoids paying an I/O cost for data you don't need.

### Scaling model: regions and RegionServers
A table's sorted row-key range is split into contiguous chunks called **regions**, each served by one RegionServer. As a region grows past a size threshold, HBase splits it automatically into two, and the cluster's master rebalances regions across servers. This is how HBase scales writes horizontally: add more RegionServers, and (assuming your row key spreads write load evenly, per the salting discussion above) throughput scales roughly linearly. This is architecturally the same idea as DynamoDB's partition-key sharding (`seven-databases/07`), though the operational model (self-managed cluster on HDFS vs. fully-managed service) differs sharply.

### Consistency model
HBase is strongly consistent per row: a read after a write to the same row always sees that write (there's a single RegionServer authoritative for any given row key at a time). This is a deliberate CP choice per the CAP framing in `seven-databases/01` — if a RegionServer is unreachable, the rows in its regions become temporarily unavailable rather than served with possibly-stale data from elsewhere, unlike DynamoDB's or CouchDB's AP-leaning designs. This makes HBase attractive whenever "read your own write, always, everywhere" actually matters (e.g., deduplication counters), and less attractive when you need every read to succeed even during a partial outage.

## Pros
- Near-linear horizontal write scalability by adding RegionServers, with automatic region splitting as data grows — designed from the ground up for volumes that would require heavy manual sharding in PostgreSQL.
- Strong per-row consistency (unlike many AP-leaning NoSQL stores), which simplifies reasoning about individual row updates even at massive scale.
- Efficient sorted range scans make it a strong fit for time-series and log-style data where "give me everything between key A and key B" is the dominant query.

## Cons
- No joins, no secondary indexes by default, no ad hoc query language — every query pattern must be designed into the row key and column family layout upfront; a new access pattern you didn't anticipate often means redesigning the schema or maintaining a denormalized second table.
- Operationally heavy: HBase depends on HDFS and ZooKeeper, and running a healthy cluster (compaction tuning, region balancing, garbage collection tuning on the JVM) is a genuine specialty, unlike a managed or lightly-operated PostgreSQL instance.
- Poor fit for small datasets or low-traffic applications — the operational overhead and design rigidity aren't worth paying unless you actually have the scale problem HBase is built to solve.

## Alternatives
- **Apache Cassandra** — a similar wide-column model with a more explicitly AP-leaning, masterless architecture (tunable consistency instead of HBase's strong per-row consistency); a common alternative when availability during partitions matters more than always-strong per-row reads.
- **DynamoDB** (`seven-databases/07`) — a managed, key-value-first alternative with similar partition-key design discipline but a simpler data model (no column families) and no operational cluster to run.
- **PostgreSQL with partitioning/sharding** (`seven-databases/02`) — viable if the scale need is more moderate and the relational conveniences (joins, ad hoc queries) are worth the extra engineering to shard manually.

## When to use it
Reach for HBase when you have genuinely large-volume, high-write data with well-understood, stable access patterns dominated by key lookups and sorted range scans (time-series, event logs, sensor data), you need strong per-row consistency, and you have (or are willing to build) the operational capacity to run a Hadoop-ecosystem cluster.

## When NOT to use it
Avoid it when your queries are ad hoc or evolving, when the dataset is small enough that the operational overhead isn't justified, or when you need joins and multi-row transactional guarantees across different keys — reach for PostgreSQL (`seven-databases/02`) instead, or a managed alternative like DynamoDB (`seven-databases/07`) if you want the scaling story without operating the cluster yourself. See `seven-databases/09` for the full decision framework.

## Key takeaways / mental model
HBase is a giant, distributed, sorted map — design the row key around the one or two access patterns you actually need (exact key, or range scan on a prefix), because that's the only thing HBase can do efficiently, and that constraint is the entire trade you're making for its horizontal write scale.

## Self-check questions
1. You're designing a table for "all orders placed by a given customer, most recent first." Propose a row key design and explain why it does or doesn't cause a hot-region problem.
2. Why does grouping columns into column families by *access pattern* rather than by *logical relatedness* matter for HBase's performance? Give a concrete example.
3. A team wants to add a new query — "all sensor readings above a temperature threshold, across all sensors" — to a table keyed by `sensorID#timestamp`. Why is this hard in HBase, and what are your options?
4. Contrast HBase's CAP posture with CouchDB's (`seven-databases/05`). Given a fraud-detection system where a stale read could mean approving a transaction that should have been blocked, which posture would you want, and why?

## References
- Seven Databases in Seven Weeks (Perkins, Redmond, Wilson), Chapter 3: "HBase."
- See also: `seven-databases/01` (CAP framing), `seven-databases/07` (DynamoDB's related partition-key discipline), `ddia/10` (partitioning) and `database-internals/08` (engine trade-offs) for deeper background.
