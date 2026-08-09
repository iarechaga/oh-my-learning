---
id: system-design-interview/06
subject: system-design-interview
title: "Design a Key-Value Store"
slug: key-value-store
status: drafted
mastery: 
seniority: senior
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 6"
prerequisites: [system-design-interview/01, system-design-interview/02, system-design-interview/03, system-design-interview/05, ddia/05, ddia/09]
created: 2026-08-10
updated: 2026-08-10
---

# Design a Key-Value Store

## TL;DR
A distributed key-value store (the Dynamo-style design behind Cassandra, Riak, and
DynamoDB) supports simple `get(key)`/`put(key, value)` operations at massive scale by
combining consistent hashing for partitioning, quorum reads/writes for tunable
consistency, vector clocks or last-write-wins for conflict resolution, and
gossip/anti-entropy for failure detection and repair. The entire design is a case study
in trading strong consistency for availability and partition tolerance (CAP) at scale.

## The idea
A relational database gives you rich queries, joins, and transactions but is hard to
scale horizontally without sacrificing a lot. A distributed key-value store gives up
most of that richness — no joins, no complex queries, no cross-key transactions — in
exchange for near-linear horizontal scalability, high availability, and low, predictable
latency for simple get/put operations. This is the right trade for workloads like
session storage, shopping carts, user preferences, or as the storage layer under a
higher-level system (e.g., a news feed's per-user timeline cache).

The design challenge is entirely about what happens when the network misbehaves:
nodes fail, partitions occur, and messages get delayed or lost, yet the system must
keep accepting reads and writes.

## How it works

### Step 1: Clarify requirements
- **Data size and access pattern.** Small values (a KB or less), accessed by exact key
  only — no range queries, no joins. (Assume: session data and user profile blobs, a
  few KB each.)
- **Availability vs. consistency.** Per CAP, under a network partition, do we favor
  availability (AP — always accept reads/writes, resolve conflicts later) or
  consistency (CP — reject requests rather than risk stale data)? (Assume: AP — this is
  the canonical Dynamo-style choice and what makes the deep dive interesting.)
- **Scale.** Assume 10 TB of data, replicated 3x for durability, spread across
  commodity servers.

### Step 2: Back-of-the-envelope
10 TB of data at replication factor 3 = 30 TB of total storage needed. If each server
node has 4 TB of usable disk, that's `30 TB / 4 TB ≈ 8` nodes minimum for storage alone,
though you'd provision more for headroom and to keep per-node load reasonable. If peak
read+write QPS is 200,000 and each node can handle roughly 10,000-20,000 ops/sec, you
need on the order of 10-20 nodes for throughput — storage and throughput needs roughly
agree here, so a cluster in the low tens of nodes is a reasonable starting point.

### Step 3: High-level design
```
[Client] --> [Coordinator node (any node can serve this role)]
                    |
        (consistent hashing determines the N nodes
         responsible for this key)
                    |
      +-------------+-------------+
      v             v             v
  [Node A]      [Node B]      [Node C]   (replicas for this key)
```

Any node can act as the **coordinator** for a given request — it's the node the client
happens to contact, and it's responsible for forwarding the request to the replica
nodes and assembling the response. Data placement uses consistent hashing with virtual
nodes (see `system-design-interview/05`), so the coordinator can compute which physical
nodes own a key without a central lookup service.

### Step 4: Deep dive — quorum consistency (tuning CAP per operation)
Define `N` = number of replicas per key, `W` = number of nodes that must acknowledge a
write before it's considered successful, `R` = number of nodes that must respond to a
read before it's returned to the client.

**The core rule:** if `W + R > N`, reads and writes overlap on at least one node,
guaranteeing the read sees the most recent write (strong-ish consistency). If
`W + R <= N`, reads might miss the latest write (better latency/availability, weaker
consistency).

*Worked example, N=3:*
- `W=3, R=1`: every write must reach all 3 replicas (slow, low availability — a single
  down node blocks writes), but any single read is guaranteed fresh.
- `W=1, R=1`: fastest possible, most available (only one node needs to be up for either
  operation) — but a read can easily return stale data if it hits a replica that missed
  the latest write.
- `W=2, R=2` (the book's common default): `W+R=4 > N=3`, so every read overlaps with
  every write on at least one node — a good balance of latency, availability, and
  consistency. Either write or read can tolerate one node being down and still succeed.

This quorum mechanism is the direct, concrete answer to "how do you make this AP system
still usably consistent" — it doesn't require unanimous agreement, but it mathematically
guarantees overlap.

### Step 5: Deep dive — handling conflicting writes
Because writes can succeed with less than all N replicas acknowledging (e.g., W=2 of
N=3), and because network partitions can let two coordinators both accept a write for
the same key, replicas can end up with conflicting versions of the same key. Two
strategies:

**Last-write-wins (LWW).** Attach a timestamp to every write; on conflict, keep the one
with the later timestamp. Simple, but requires synchronized clocks (clock skew across
servers can silently drop a legitimately later write if that server's clock lags) and
can lose data (the "losing" write's information is gone, not merged).

**Vector clocks.** Each value carries a vector of `(node_id, version_counter)` pairs
tracking its causal history. Comparing two vector clocks tells you if one is a strict
ancestor of the other (safe to discard the ancestor) or if they're **concurrent**
(genuinely conflicting, requiring resolution).

*Worked example:*
- Client writes key `K` via coordinator node A: value `v1`, vector clock `[A:1]`.
- Client reads `v1` (clock `[A:1]`), then writes an update `v2` also via node A: clock
  becomes `[A:2]` (a clean, causal update — `[A:2]` supersedes `[A:1]`).
- Now suppose a network partition happens. A different client, unaware of `v2`, reads
  the old `v1` (clock `[A:1]`) from a replica that hasn't yet seen `v2`, and writes an
  update `v3` via coordinator node B: clock becomes `[A:1, B:1]`.
- After the partition heals, the system holds two versions: `v2` with clock `[A:2]` and
  `v3` with clock `[A:1, B:1]`. Neither vector clock is an ancestor of the other (A:2
  is higher for A, but B:1 doesn't appear in v2's clock at all) — these are **concurrent
  conflicting writes**. The system cannot pick a winner automatically; it returns both
  versions to the next client that reads `K`, and the *application* resolves the
  conflict (e.g., merging a shopping cart's contents from both versions).

This is the crux of the AP trade-off: the system stays available through the partition
by accepting both writes, but pushes conflict resolution up to the client/application,
which must be designed to handle it (this is exactly what Amazon's original Dynamo
paper describes for shopping carts — merge instead of picking one).

### Step 6: Deep dive — failure detection and recovery
- **Gossip protocol.** Nodes periodically exchange membership/heartbeat state with a
  few random peers; failure/join information propagates across the cluster without a
  central coordinator, avoiding a single point of failure for membership itself.
- **Sloppy quorum and hinted handoff.** If a node that should hold a replica is
  temporarily down, the coordinator writes to the next healthy node on the ring instead
  and attaches a "hint" that the write really belongs to the down node. When the down
  node recovers, the hint is replayed to it. This keeps writes succeeding (favoring
  availability) even when the "correct" quorum can't be reached.
- **Merkle trees for anti-entropy.** To detect and repair divergence between replicas
  without comparing every key, each replica maintains a Merkle tree (a hash tree) over
  its key range: leaf nodes hash individual key ranges, and each parent hashes its
  children. Two replicas compare their tree roots; if they match, the ranges are
  identical. If not, recurse down only the mismatched branches. This lets two replicas
  find their differences in `O(log n)` comparisons instead of comparing every key.

### Step 7: Wrap-up — CAP in this design
Summarize explicitly: this design chooses **AP** — under a partition, every reachable
node keeps accepting reads and writes (sloppy quorum ensures this), at the cost of
temporary inconsistency resolved via vector clocks and anti-entropy after the partition
heals. Contrast this with a CP design (e.g., a system backed by Raft/Paxos consensus,
see `system-design/03`), which would instead reject writes it can't get proper quorum
for, favoring correctness over availability.

## Pros
- Near-linear horizontal scalability via consistent hashing.
- High availability, even during network partitions or node failures (sloppy quorum,
  hinted handoff).
- Tunable consistency per operation via N/W/R, letting different use cases trade off
  latency vs. freshness without redesigning the system.

## Cons
- No joins, no complex queries, no multi-key transactions — a real functional
  limitation compared to a relational database.
- Conflict resolution (vector clocks) pushes real complexity onto the application layer.
- Operationally more complex than a single relational database: gossip, hinted handoff,
  Merkle-tree anti-entropy, and quorum tuning all need monitoring and understanding.

## Alternatives
- **A CP key-value store (e.g., etcd, ZooKeeper, or Cassandra configured with strong
  consistency levels)** — favors consistency over availability during a partition;
  right choice when correctness (e.g., leader election, configuration) matters more
  than uptime.
- **A single-node or leader-follower relational database** — simpler operationally,
  supports rich queries/transactions, but doesn't scale writes horizontally and has a
  harder failover story.
- **A managed service (DynamoDB, Cosmos DB)** — gets the same Dynamo-style design
  without operating the cluster yourself, at the cost of vendor lock-in and less
  control over tuning.

## When to use it
High-scale, simple-access-pattern workloads where availability matters more than
perfect consistency: session stores, shopping carts, user preference/profile stores,
caching layers, and as a building block under higher-level systems (e.g., storing
per-user feed state).

## When NOT to use it
Workloads needing multi-key transactions, complex queries/joins, or strict consistency
(e.g., a financial ledger, inventory counts that must never oversell) are a poor fit —
reach for a CP system or a relational database with proper transaction isolation
instead. Also avoid it when the team can't operationally support the complexity
(gossip, quorum tuning, conflict resolution) for a workload that a simple single-node
database would have handled fine.

## Key takeaways / mental model
Think of N/W/R as a dial, not a fixed setting: it lets you choose, per operation type,
how much you want the "everyone must agree" guarantee versus "one node is enough,
resolve conflicts later." Vector clocks aren't there to prevent conflicts — nothing
can, once you've chosen availability over strict ordering — they exist to let the
system *detect* which conflicts are real (concurrent, unordered) versus fake (one write
causally followed the other), so only the real ones need to bubble up to the
application.

## Self-check questions
1. With N=3, W=2, R=2, why does every read overlap with every write on at least one
   replica, and why doesn't that guarantee the same thing as strong consistency across
   the whole system?
2. Two vector clocks are `[A:2, B:1]` and `[A:2, B:2]`. Which one is a strict ancestor
   of the other, and which write should be discarded?
3. Two vector clocks are `[A:2]` and `[B:1]`. Are these concurrent or causally ordered?
   What must the system do with both values?
4. What specific problem does hinted handoff solve, and what does it trade away
   (relative to a strict quorum) to solve it?
5. Why would you reject this entire design for a workload that needs multi-key
   transactions, and what would you propose instead?

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 6
- Amazon's Dynamo paper (2007) — the original design this chapter is based on.
- `ddia/05` (Replication) and `ddia/09` (Consistency and Consensus) for the underlying
  theory.
- `system-design-interview/05` (Consistent Hashing) for the partitioning mechanism.
