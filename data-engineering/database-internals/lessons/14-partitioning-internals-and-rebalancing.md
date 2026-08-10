---
id: database-internals/14
subject: database-internals
title: "Partitioning Internals and Rebalancing Algorithms"
slug: partitioning-internals-and-rebalancing
status: drafted
mastery:
seniority: staff
source: Database Internals (Alex Petrov), Part II, Chapter 13 (Cluster Management and Partitioning)
prerequisites: [database-internals/11, database-internals/13]
created: 2026-08-10
updated: 2026-08-10
---

# Partitioning Internals and Rebalancing Algorithms

## TL;DR
Partitioning splits a dataset across many nodes so no single node needs to hold (or serve) all of it, but the specific algorithm chosen to map keys to partitions — range partitioning, hash partitioning, or consistent hashing — determines how much data has to move (and how disruptively) whenever nodes are added or removed. Consistent hashing exists specifically to solve the rebalancing problem that plain modulo-based hash partitioning gets catastrophically wrong.

## The idea
Once a dataset is too large or too hot for one node (`database-internals/11`'s storage-plane scaling concern), it must be partitioned (sharded) across many nodes. The core design question isn't just "how do I decide which node owns key K" (any deterministic function works for that) — it's "when the cluster's node count changes (scaling up, scaling down, or recovering from a failure), how much data has to physically move to new owners, and can that movement happen incrementally without a full, disruptive reshuffle?" Getting the partitioning scheme wrong here doesn't show up until your cluster changes size for the first time — at which point a naive scheme can mean moving nearly all your data at once, an operational disaster at scale.

## How it works

### Range partitioning
Keys are divided into contiguous ranges (e.g. `A-F` on node 1, `G-M` on node 2, `N-S` on node 3, `T-Z` on node 4), and each node owns one or more ranges. This preserves key ordering across nodes, making range scans (find all keys between X and Y) efficient — often serviceable by a small number of nodes rather than scattering across the whole cluster.

**Worked example — range partitioning and hot spots.** A time-series database partitions by timestamp range, one range per day. This works well for historical range-scan queries (fetch all of last Tuesday's data touches exactly one partition) but creates a severe write hot spot: at any given moment, *all* current writes land on whichever single partition owns "today," while every other partition sits idle for writes — a direct consequence of choosing a monotonically-increasing key as the partitioning key. Mitigation typically means salting the key (prefixing with a partition-spreading value) or choosing a different partitioning key for the write path than for the query path.

### Hash partitioning (naive modulo)
Keys are hashed, and the hash is mapped to a node via `hash(key) mod N` (N = number of nodes). This spreads keys evenly (assuming a good hash function) and avoids range partitioning's hot-spot risk for uniformly-distributed keys, but has a severe problem when N changes.

**Worked example — why modulo-based hashing breaks on rebalance.** With N=4 nodes, key `K` with `hash(K)=17` maps to node `17 mod 4 = 1`. If a 5th node is added (N=5), the same key now maps to `17 mod 5 = 2` — a *different* node. This isn't an isolated case: adding or removing even one node changes the modulo result for the vast majority of keys across the entire keyspace (roughly `(N-1)/N` of all keys change owner when going from N to N+1 nodes, e.g. adding a 5th node to 4 causes about 80% of *all* keys to need to move, not just a proportional share). This makes modulo-based hash partitioning nearly useless for any system that needs to scale its node count without a massive, disruptive full-dataset reshuffle.

### Consistent hashing: bounding the data movement
**Consistent hashing** solves the rebalancing problem directly: both keys and nodes are hashed onto the same circular hash space (a "ring," typically 0 to 2^32-1 or similar). A key belongs to the first node encountered walking clockwise around the ring from the key's hash position. Adding or removing a node only affects the contiguous arc of the ring immediately adjacent to that node — every other node's ownership is completely undisturbed.

**Worked example — consistent hashing's bounded movement.** A ring has 4 nodes (A, B, C, D) placed at hash positions 0, 25, 50, 75 (out of 100 for simplicity). Node A owns keys hashing into `(75, 100]` and `[0, 25)` combined... more precisely, each node owns the arc from the *previous* node's position (exclusive) to its own position (inclusive) walking clockwise — so B owns `(0, 25]`, C owns `(25, 50]`, D owns `(50, 75]`, A owns `(75, 100]`. Adding a new node E at position 60 only affects the arc `(50, 60]`, which previously belonged to D — those keys move from D to E, and every other node (A, B, C) is completely unaffected. Compare this to modulo hashing's ~80% reshuffle for the same node-count change: consistent hashing bounds movement to roughly `1/N` of the total keyspace for a single node addition/removal, a dramatically smaller and more predictable disruption.

### Virtual nodes: fixing consistent hashing's load-balance weakness
Plain consistent hashing with one ring-position per physical node has a real weakness: with few nodes, the arcs can be very unevenly sized purely by the luck of where each node's hash lands, causing some nodes to own far more of the keyspace (and thus far more load) than others. **Virtual nodes (vnodes)** fix this: each physical node is assigned many positions on the ring (e.g. 256 virtual positions per physical node) rather than just one, so each physical node's total owned keyspace is the sum of many small, independently-randomly-placed arcs — which, by the law of large numbers, evens out much more predictably than one single arc per node ever could.

**Worked example — vnodes smoothing load distribution.** With 4 physical nodes and 1 ring-position each, random placement might give node A 40% of the keyspace and node D only 10% — a 4x load imbalance purely from unlucky hash placement. With 256 vnodes per physical node (1024 total ring positions), each physical node's *share* of the ring is the sum of ~256 small, independently-scattered arcs, and the law of large numbers pulls each physical node's actual total share close to the ideal 25% — observed imbalances typically shrink to single-digit percentage deviations rather than multiples. Vnodes also make rebalancing more granular: adding a new physical node with its own 256 vnode positions pulls a small, evenly-distributed slice from *many* existing nodes simultaneously, rather than concentrating the entire new node's initial data transfer on just one neighbor.

### Rebalancing operations: what actually happens when the cluster changes
When a node is added: the system identifies which key ranges (or vnode arcs) now belong to the new node, and streams that data from the node(s) that previously owned it — during this transfer, the system must decide whether to serve reads/writes from the old owner, the new owner, or both, consistently, without losing writes that happen mid-transfer (often handled via the same hinted-handoff/quorum machinery from `database-internals/13`, treating the transfer period as a temporary, tracked divergence rather than an instantaneous cutover). When a node is removed (planned decommission or unplanned failure): its owned ranges must be redistributed among the remaining nodes, following the same consistent-hashing/vnode logic in reverse, and — for planned removals — this is ideally done proactively (stream data off before taking the node down) rather than reactively (only after failure, relying on existing replication factor to have already covered the loss).

**Worked example — planned node decommission with replication factor.** A cluster running replication factor 3 (each key stored on 3 nodes, per `database-internals/13`'s quorum framing) decommissions node D. Because D's data already exists on 2 other replicas (say B and C, per the replication scheme), there's no data-loss risk purely from D leaving — but the cluster's ring/vnode ownership must still be updated so that *future* writes for D's former key ranges go to a new appropriate replica (say, a newly-added node E, or redistributing among B, C, and a fourth existing node), restoring the full replication factor of 3 for those keys rather than silently operating at a degraded factor of 2 indefinitely.

## Pros
- Consistent hashing with virtual nodes bounds rebalancing disruption to a small, predictable fraction of the keyspace, making elastic scaling operationally tractable at large cluster sizes.
- Range partitioning preserves ordering, enabling efficient range scans that hash-based schemes can't offer without scattering the scan across many nodes.
- Vnodes additionally improve load-balance quality and let rebalancing spread load across many existing nodes rather than concentrating it on one neighbor.

## Cons
- Naive modulo-based hash partitioning is a well-known trap: it distributes load evenly at a fixed cluster size but is essentially unusable for a cluster that needs to grow or shrink without massive reshuffling.
- Range partitioning is vulnerable to hot spots whenever the partitioning key correlates with access recency or popularity (e.g. monotonic timestamps, viral content keys).
- Vnodes add real operational complexity (more metadata to track, more moving pieces during rebalancing) in exchange for the load-balance and rebalancing-granularity improvements.

## Alternatives
- **Static/manual sharding** — partition assignment decided and fixed by an operator rather than computed algorithmically; simpler to reason about at small scale but doesn't automatically rebalance and requires manual intervention for every scaling event.
- **Directory-based partitioning** (an explicit lookup table mapping key ranges/hashes to nodes, maintained by the control plane from `database-internals/11`) — more flexible than pure consistent hashing (can encode arbitrary, operator-driven placement decisions, e.g. for compliance/locality reasons) at the cost of needing to consult (and keep consistent) an extra indirection layer on every request, rather than computing ownership purely algorithmically.

## When to use it
Use consistent hashing with virtual nodes as the default partitioning scheme for any system expected to scale its node count over its lifetime (nearly all distributed databases) — it's the mechanism that makes "add a node to handle more load" an operationally boring, bounded-impact event rather than a major incident. Use range partitioning specifically when range-scan query patterns dominate and you can actively manage (or accept) the hot-spot risk on the partitioning key.

## When NOT to use it
Avoid plain modulo-based hash partitioning for anything expected to change size — reserve it, if at all, for genuinely fixed-size deployments where the node count is truly static for the system's entire lifetime, which is rare in practice. Avoid naive range partitioning on monotonically-increasing keys (raw timestamps, auto-increment IDs) without an explicit mitigation for the resulting write hot spot.

## Key takeaways / mental model
Think of consistent hashing as seating people (keys) around a circular table with reserved sections (nodes) marked at various points around the circle; each person sits at the first reserved-section marker they reach going clockwise. Adding a new reserved section only pulls people from the one section immediately counter-clockwise of it — everyone else stays exactly where they were. Compare this to modulo hashing, which is like re-numbering every seat in the room from scratch every time you add a table — nearly everyone has to get up and move, even though only the number of tables changed, not the fundamental question of who should sit where relative to their neighbors.

## Self-check questions
1. Walk through, with actual numbers, why adding a 5th node to a 4-node cluster under naive `hash(key) mod N` partitioning moves roughly 80% of keys, and explain precisely why consistent hashing bounds that same operation to roughly 1/N of the keyspace instead.
2. Explain why a single ring-position per physical node in consistent hashing can produce uneven load distribution, and how virtual nodes fix this using the law of large numbers intuition.
3. A time-series system partitions by day-range and observes that write throughput is bottlenecked on a single node (today's partition) while yesterday's and older partitions' nodes sit nearly idle. Diagnose the root cause and propose a fix that preserves efficient range-scan queries for historical data.
4. During a planned node decommission in a replication-factor-3 cluster, why is there no immediate data-loss risk from removing the node, but why does the cluster still need to actively rebalance rather than just letting replication factor silently drop to 2 for the affected keys?

## References
- Database Internals (Alex Petrov), Part II, Chapter 13: "Cluster Management" (partitioning, consistent hashing, rebalancing).
- See also: `database-internals/11` for the control-plane responsibilities partition placement belongs to, `database-internals/13` for the quorum/replication machinery rebalancing interacts with, and `ddia/10` for the DDIA-level partitioning framing.
