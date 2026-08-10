---
id: seven-databases/07
subject: seven-databases
title: "DynamoDB: Partition-Key Design, Throughput Units, and Access Constraints"
slug: dynamodb-partition-key-design
status: drafted
mastery:
seniority: senior
source: Seven Databases in Seven Weeks (Perkins, Redmond, Wilson), Chapter 7
prerequisites: [seven-databases/01, seven-databases/03]
created: 2026-08-10
updated: 2026-08-10
---

# DynamoDB: Partition-Key Design, Throughput Units, and Access Constraints

## TL;DR
DynamoDB is a fully-managed, key-value/wide-column hybrid database that scales horizontally by hashing a chosen partition key across many physical partitions, deliberately trading query flexibility for predictable, near-infinite scale and operational simplicity — but only if you design your access patterns and partition key correctly *before* writing any data, because unlike PostgreSQL, restructuring access patterns after the fact is expensive and sometimes requires a full data migration.

## The idea
HBase (`seven-databases/03`) gives you horizontal scale via row-key design, but you operate the cluster yourself. DynamoDB takes the same core idea — partition the keyspace, scale by adding partitions — and removes the operational burden entirely: no cluster to patch, no compaction to tune, no ZooKeeper to babysit. AWS manages the partitioning, replication, and failover; you manage the schema design and pay per throughput consumed (or per request, in on-demand mode).

The trade-off for that operational simplicity is a much stricter modeling discipline than PostgreSQL or even HBase. DynamoDB actively discourages "model the data, then figure out queries later" — its own documentation and this book both push you toward **access-pattern-first design**: enumerate every query your application will ever run against a table *before* choosing your keys, because DynamoDB's query engine can efficiently do almost nothing except "look up by exact partition key" and "range-scan a sort key within one partition." Anything else (arbitrary filters, joins, ad hoc aggregation) is either a full table scan (slow, expensive, and actively discouraged) or requires a secondary index designed in advance.

## How it works

### Partition key and sort key, concretely
A DynamoDB table for an order-tracking system might use:

```
Table: Orders
Partition key: customerId   (e.g., "cust_042")
Sort key:      orderId#timestamp   (e.g., "ord_991#20260810T1530")
```

Every item's partition key is hashed by DynamoDB to determine which physical partition stores it; items sharing a partition key are stored together, sorted by the sort key. This gives you two efficient operations: fetch one item by exact `(partition key, sort key)`, or fetch a range of items sharing one partition key, sorted by sort key — e.g., "all of customer 042's orders, most recent first." This is structurally the same idea as HBase's sorted-row-key design (`seven-databases/03`), with the partition key playing the role of "the part of the row key that determines physical placement" and the sort key playing the role of "the part that determines order within that placement."

### The hot-partition problem, and why it's unforgiving
**Worked example.** A naive design uses `orderStatus` ("pending," "shipped," "delivered") as the partition key, reasoning "we often query by status." Because there are only three possible values, every item lands on one of three partitions — no matter how many partitions DynamoDB is technically capable of creating, all traffic concentrates on three, and DynamoDB throttles requests once a partition's throughput capacity is exceeded, regardless of the table's overall provisioned capacity. This is the same hot-partition failure mode as HBase's naive timestamp-only row key (`seven-databases/03`), but DynamoDB's fully-managed nature makes the fix less visible until you actually hit throttling in production — there's no cluster dashboard showing you one RegionServer maxed out; you just see `ProvisionedThroughputExceededException` errors. The fix is the same principle as HBase's: choose a partition key with high cardinality that spreads write and read load evenly (`customerId` above works because there are many customers, each with a bounded number of orders).

### Access-pattern-first design — the discipline in practice
**Worked example.** Suppose the application needs three query patterns: (1) a customer's orders, most recent first; (2) all orders for a given product, to compute sales stats; (3) an order by its own ID directly (e.g., from an email link). A single table with `customerId` as partition key satisfies (1) and (3) if you also store `orderId` as an attribute you can look up via a secondary index, but it does *not* satisfy (2) — there's no efficient way to ask "all orders containing product X" from a table partitioned by customer. DynamoDB's answer is a **Global Secondary Index (GSI)**: a second, differently-partitioned copy of (a projection of) the same data, maintained automatically, with `productId` as its partition key. Each query pattern that doesn't fit the base table's key structure typically needs its own GSI, decided *at design time* — adding one after the fact is possible but requires a backfill and, in the interim, extra engineering to keep old code working.

### Throughput and cost model
DynamoDB (in provisioned mode) charges per Read/Write Capacity Unit: roughly, one Write Capacity Unit covers one write of up to 1KB per second, one (strongly consistent) Read Capacity Unit covers one read of up to 4KB per second. On-demand mode charges per actual request instead, trading predictable cost for no capacity planning. The practical consequence: a poorly-designed access pattern that causes scans instead of targeted lookups doesn't just run slowly — it directly and often dramatically increases your AWS bill, because a scan consumes capacity proportional to every item examined, not just every item returned. This turns a modeling mistake into a highly visible operational cost problem quickly, more so than the "just add an index" fix that would resolve a slow PostgreSQL query.

### Consistency model
DynamoDB defaults to eventually consistent reads (cheaper, per the throughput model above) but offers strongly consistent reads on request (at double the read capacity cost) — a directly tunable version of the CAP trade-off from `seven-databases/01`. Under normal operation (no partition), both options return current data; the distinction matters specifically during replica lag or partition events, where an eventually consistent read might return a slightly stale value. This tunability is DynamoDB's version of CouchDB's explicit AP posture (`seven-databases/05`) — DynamoDB defaults to AP-leaning behavior but lets you pay for CP-like guarantees on a per-query basis, rather than fixing the whole system's posture at the architecture level.

## Pros
- Fully managed: no cluster operations, patching, or compaction tuning, unlike HBase (`seven-databases/03`) — a major reduction in operational burden for teams without dedicated database infrastructure expertise.
- Near-infinite horizontal scale with predictable, tunable performance once the partition key is well-chosen, and per-request pricing that scales down to near-zero for low-traffic tables.
- Tunable consistency (eventual vs. strong per read) gives fine-grained control over the classic CAP trade-off without operating a separate consistency-tuning mechanism yourself.

## Cons
- Access patterns must be known and designed for upfront; a genuinely new query pattern discovered after launch often means adding a GSI (with backfill cost) or, in the worst case, restructuring the table — much less forgiving than adding an index to an existing PostgreSQL table.
- A poorly-chosen partition key causes silent throttling under load that may not surface until a real traffic spike, and the fix (redesigning the key, migrating data) is expensive after the fact.
- No joins, very limited ad hoc querying (scans are possible but explicitly discouraged and costly) — reporting and analytics workloads typically need to export to a separate analytical store rather than querying DynamoDB directly.

## Alternatives
- **HBase** (`seven-databases/03`) — the same partition/row-key design discipline, but self-managed; appropriate when you need that control (or must avoid vendor lock-in) and have the operational capacity to run the cluster.
- **PostgreSQL with sharding extensions** (`seven-databases/02`) — appropriate if you need DynamoDB-like scale but also genuinely need joins and flexible ad hoc queries, at the cost of more manual sharding engineering.
- **MongoDB with sharding** (`seven-databases/04`) — a middle ground offering more query flexibility than DynamoDB with a broadly similar sharding-by-key model, at the cost of self-managing the cluster (or paying for a managed MongoDB service).

## When to use it
Reach for DynamoDB when your access patterns are well-understood and stable, your team wants zero database operations overhead, and your scale needs (or growth trajectory) genuinely justify a partition-key-driven design — high-throughput, key-lookup-dominated workloads like session stores, shopping carts, IoT event ingestion, and gaming leaderboards are classic fits.

## When NOT to use it
Avoid it when query patterns are still evolving or genuinely ad hoc (a data-exploration or reporting-heavy workload), when you need joins or multi-row transactions across arbitrary entities as a first-class feature, or when your scale doesn't actually require it — the design discipline DynamoDB demands is a real cost that only pays off once you're at a scale (or have an access-pattern rigor) that needs it. See `seven-databases/09` for the full comparison.

## Key takeaways / mental model
DynamoDB asks you to pay its design cost upfront (enumerate every access pattern, choose a high-cardinality partition key, provision a GSI per pattern that doesn't fit the base table) in exchange for near-zero operational cost and near-infinite scale later — the opposite trade from PostgreSQL, which asks little upfront and lets you add indexes and adapt queries later, at the cost of a scaling ceiling. Treat "what are all my access patterns?" as a hard prerequisite question, not an afterthought, whenever DynamoDB is on the table.

## Self-check questions
1. A team picks `country` as a DynamoDB partition key for a global user table, reasoning "it's a natural grouping." What will go wrong at scale, and why is this the same underlying failure as a bad HBase row key?
2. Six months after launch, a new requirement appears: "show all orders placed in the last hour, across all customers." The existing table is partitioned by `customerId`. What are your options, and what does each cost?
3. Explain why a full table scan in DynamoDB is not just slow but also expensive in a way that a full table scan in PostgreSQL, while also slow, typically isn't as directly costly per-query.
4. Given a workload needing (a) strict access-pattern discipline is acceptable, (b) zero desire to operate infrastructure, and (c) massive, spiky scale — would you choose DynamoDB or HBase? Now change only (b) to "the team has strong ops capacity and wants full control" — does your answer change, and why?

## References
- Seven Databases in Seven Weeks (Perkins, Redmond, Wilson), Chapter 7: "DynamoDB."
- See also: `seven-databases/01` (CAP framing), `seven-databases/03` (HBase's related partition-key discipline), `ddia/10` (partitioning) and `database-internals/08` (engine trade-offs) for deeper background.
