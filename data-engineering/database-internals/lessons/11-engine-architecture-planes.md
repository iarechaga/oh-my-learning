---
id: database-internals/11
subject: database-internals
title: "Engine Architecture: Separating Storage, Execution, and Control Planes"
slug: engine-architecture-planes
status: drafted
mastery:
seniority: staff
source: Database Internals (Alex Petrov), Part II, Chapter 9 (Introduction to Distributed Systems, architectural framing)
prerequisites: [database-internals/05, database-internals/10]
created: 2026-08-10
updated: 2026-08-10
---

# Engine Architecture: Separating Storage, Execution, and Control Planes

## TL;DR
A mature database engine is not one monolithic blob but a small number of loosely-coupled planes with distinct responsibilities and evolution rates: the **storage plane** (durable data and indexes, everything covered in Part I of this subject), the **execution plane** (query parsing, planning, and execution against the storage plane), and the **control plane** (cluster membership, configuration, schema/DDL, placement decisions, and coordination with consensus/replication machinery). Recognizing this separation — and its increasing physical decoupling in modern cloud-native databases (storage-compute separation) — is what lets a staff engineer reason about scaling, failure isolation, and evolution of a database architecture as a system, not just as a single component's internals.

## The idea
Everything in Part I of this subject (pages, B-Trees, LSM-Trees, buffer pools, WAL) lives inside what this lesson calls the storage plane — the layer responsible for durably persisting and indexing bytes. But a real database also has to parse SQL, choose a query plan, execute that plan against the storage layer, manage schema changes, coordinate cluster membership and failover, and enforce access control — none of which is "storage" in the sense of the earlier lessons. Historically these all lived in one process, tightly coupled (a classic monolithic RDBMS). The staff-level insight this lesson develops: these responsibilities have genuinely different failure modes, scaling characteristics, and rates of change, and increasingly, modern systems architect around that difference explicitly — separating storage from compute, and both from cluster-control/coordination — rather than accepting the monolith's coupling as inevitable.

## How it works

### The three planes, defined
- **Storage plane**: durable persistence and indexing — pages, B-Trees/LSM-Trees, buffer management, WAL (`database-internals/01`-`database-internals/10`). Its job: given a key or range, durably store and retrieve bytes correctly and efficiently. It doesn't know or care what a SQL query is.
- **Execution plane**: query parsing, planning/optimization, and execution — turning a declarative query into a sequence of storage-plane operations (index scans, joins, aggregations), and often holding transient, per-query state (intermediate result buffers, sort/hash structures) that's separate from the storage plane's durable data.
- **Control plane**: cluster membership, leader election, schema/DDL propagation, partition placement and rebalancing decisions (`database-internals/14`), and consensus coordination (`database-internals/15`) — the "who is responsible for what, and how do we agree on it" layer, operating at a much lower frequency and different consistency model than the hot read/write path.

### Why the separation matters: different scaling and failure characteristics
Each plane wants to scale differently under load, and conflating them forces awkward compromises:
- Storage needs to scale with **data volume** — more disk, more nodes holding more partitions.
- Execution needs to scale with **query complexity and concurrency** — more CPU/RAM for query processing, potentially independent of how much data exists.
- Control needs to scale with **cluster size and churn rate** — how often nodes join/leave/fail, how often schema changes — and it needs strong consistency (it's making decisions everyone must agree on) even though it handles far lower request volume than the hot data path.

**Worked example — why coupling storage and execution hurts.** In a traditional monolithic RDBMS running on a single machine, a burst of complex analytical queries (execution-plane-heavy: lots of CPU for joins/sorts) competes directly for the same CPU and memory resources as the storage plane's buffer pool and background flush/compaction threads (`database-internals/05`, `database-internals/07`) — an analytical query surge can starve the buffer pool of CPU time needed for its own housekeeping, degrading unrelated OLTP write latency on the same machine, even though the two workloads have nothing to do with each other logically. Separating execution onto independently-scalable compute nodes (as in modern cloud data warehouses) lets you scale query compute up during an analytical burst without touching the storage tier at all, eliminating this cross-workload interference.

### Storage-compute separation: the modern cloud-native pattern
A significant architectural trend (Amazon Aurora, Snowflake, more recently many "cloud-native" OLTP systems) takes the storage/execution split from a *logical* separation within one process to a *physical* separation across the network: the execution plane runs on stateless (or nearly stateless) compute nodes that can be added/removed/scaled independently of the storage plane, which runs on a separate, durable, often replicated storage tier (frequently built on distributed log/replication primitives from `database-internals/12` and `database-internals/13`).

**Worked example — Aurora-style log-as-storage.** Aurora's storage plane persists only the write-ahead log stream (`database-internals/04`) — not full data pages — replicating that log across multiple storage nodes/availability zones; individual storage nodes independently and lazily materialize data pages from the log as needed to serve reads, and the compute (execution) plane holds a buffer-pool cache but can be scaled, restarted, or failed over largely independent of the storage tier's own health, because the durable source of truth (the log) lives entirely in the storage plane. Compare this to a traditional single-node engine where compute and storage are the same process — losing that process means losing (temporarily) both query execution *and* direct access to the buffer pool's cached state simultaneously, with no independent scaling lever for either.

### Control plane: why it needs a different consistency model than the hot path
The control plane makes decisions like "which node currently owns partition 7" or "what is the current schema version" — decisions that every other node needs to agree on, but that change relatively rarely compared to the volume of reads/writes flowing through the storage and execution planes. This is exactly the profile that favors a consensus protocol (`database-internals/15`) over the storage plane's own (potentially weaker, higher-throughput-oriented) consistency model: the control plane can afford consensus's latency cost (a control decision might take tens of milliseconds to commit) because it's not on the hot per-query path, while the storage/execution planes need much higher throughput and often accept weaker consistency guarantees (e.g. eventual consistency for replicated reads, `database-internals/13`) in exchange for that throughput.

**Worked example — a schema change propagating through the control plane.** An `ALTER TABLE` DDL statement is, structurally, a control-plane operation: it must be agreed upon and consistently visible to every node before any node starts interpreting rows under the new schema (a race here — some nodes serving the old schema, some the new — causes real correctness bugs). A well-architected system routes this through the same consensus mechanism used for cluster membership decisions (`database-internals/15`), accepting the latency cost of consensus for this rare, safety-critical operation, while the hot read/write path (storage and execution planes) never pays that consensus latency per-query — it only needs to observe "the current agreed schema version" cheaply, refreshed periodically or on a cache-invalidation signal from the control plane.

### The staff-level judgment call: when is separation worth the complexity?
Separating planes adds real operational complexity: more independently-deployed services, network calls where there used to be in-process function calls, and new failure modes (the execution plane being up while the storage plane is degraded, or vice versa — a partial-failure mode that doesn't exist in a monolith). This is a genuine cross-system, cross-team trade-off, not a free architectural win: a small-scale system with predictable, co-located load may get real simplicity benefits from *not* separating these planes, while a system operating at genuinely independent scaling needs for storage vs. compute (the Aurora/Snowflake profile — huge data volume, bursty and variable query compute demand) gets a real, load-bearing benefit from separation that's worth its added operational surface.

## Pros
- Each plane can scale, fail, and evolve independently, matching infrastructure investment to the actual bottleneck (data volume vs. query compute vs. coordination overhead) rather than over- or under-provisioning a monolith uniformly.
- Physical storage-compute separation (cloud-native pattern) enables genuinely elastic compute scaling and often much faster failover (a stateless compute node can be replaced quickly; the durable state lives safely in the storage plane).
- Isolates failure/interference between workload types (e.g. analytical query bursts no longer directly starve OLTP storage housekeeping).

## Cons
- Introduces network calls and partial-failure modes between planes that don't exist in a monolithic design — genuinely harder to reason about and debug.
- Physical separation (not just logical) adds real latency for operations that need tight coordination between planes (e.g. a compute node's buffer pool cache miss now potentially means a network round-trip to a separate storage tier rather than a local disk read).
- Requires the control plane's consensus-based decisions to be correctly and promptly propagated/cached by the other planes — a stale or lagging control-plane view (e.g. serving queries against an outdated partition-ownership map) is a real class of production bug in these architectures.

## Alternatives
- **Monolithic engine (all planes co-located in one process)** — the traditional RDBMS architecture; simpler to reason about and operate at moderate scale, at the cost of coupled scaling and failure characteristics across planes; still the right choice for the large majority of systems that don't have Aurora/Snowflake-scale independent scaling pressures.
- **Shared-nothing architecture without an explicit control plane** (each node independently makes local decisions, reconciled via gossip/anti-entropy rather than consensus) — trades the control plane's strong consistency for higher availability and simpler operation, appropriate when the coordinated decisions (like partition ownership) can tolerate eventual, rather than immediate, agreement — see `database-internals/13`.

## When to use it
Explicitly separate storage, execution, and control planes when you observe genuinely independent scaling pressures across them (e.g. highly variable analytical query load against a large, steady-growth dataset) or when you need independent failure isolation between workload types serving different SLAs from the same underlying data.

## When NOT to use it
Don't introduce this separation preemptively for a system without evidence of these independent scaling pressures — for the majority of OLTP systems at moderate scale, a well-tuned monolithic engine (or a simple primary/replica setup) is simpler to operate and reason about, and the added network hops and partial-failure surface of a separated architecture are a real cost without a corresponding benefit at that scale.

## Key takeaways / mental model
Think of a restaurant: the pantry/walk-in fridge (storage plane) holds ingredients durably and needs to scale with how much food you stock; the kitchen line (execution plane) needs to scale with how many complex orders are being cooked simultaneously, which can spike independently of pantry size on a big event night; and the manager's office (control plane) makes rare, high-stakes decisions everyone must agree on (menu changes, which station handles what) that don't need to happen fast, but must happen correctly and be seen consistently by every cook. A tiny diner can run all three out of one small room (a monolith); a large restaurant chain benefits from centralizing the pantry (shared storage), scaling kitchen staff per location independently, and having the manager's decisions apply consistently across every location — but that separation only pays off once you're actually running at that scale.

## Self-check questions
1. Explain, using a concrete scenario, why an analytical query surge in a monolithic (non-separated) engine can degrade unrelated OLTP write latency, and how storage-compute separation specifically prevents that interference.
2. Why does the control plane typically use a stronger consistency model (consensus, `database-internals/15`) than the storage/execution hot path, given that the control plane handles far less request volume?
3. Describe a specific new failure mode introduced by physically separating compute and storage (e.g. Aurora-style) that simply doesn't exist in a monolithic single-process engine — what would "storage plane healthy, compute plane degraded" actually look like operationally?
4. A startup is building an MVP OLTP application with predictable, moderate load. Using this lesson's "when NOT to use it" guidance, argue why they should default to a monolithic engine rather than prematurely architecting storage-compute separation.

## References
- Database Internals (Alex Petrov), Part II, Chapter 9 (architectural framing preceding the distributed-systems chapters).
- See also: `database-internals/12`, `database-internals/13`, `database-internals/15` for the replication and consensus mechanisms the control plane and separated storage tiers depend on.
