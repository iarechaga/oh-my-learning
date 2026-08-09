---
id: system-design-interview/05
subject: system-design-interview
title: "Design Consistent Hashing"
slug: consistent-hashing
status: drafted
mastery: 
seniority: mid
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 5"
prerequisites: [system-design-interview/01, system-design-interview/02, system-design/04, ddia/10]
created: 2026-08-10
updated: 2026-08-10
---

# Design Consistent Hashing

## TL;DR
When you shard data or cache entries across N servers using `hash(key) % N`, adding or
removing a single server reshuffles almost all keys. Consistent hashing fixes this by
mapping both servers and keys onto a shared ring, so a server joining or leaving only
displaces the keys immediately adjacent to it — roughly `1/N` of the total, not nearly
all of it. This lesson walks it as an interview problem end-to-end; the mechanism
itself parallels `system-design/04`, but is retold here fully self-contained with the
interview framing (why it comes up, how to introduce it, what to draw).

## The idea
Distributed caches and sharded databases need a rule for "which server owns this key."
The naive rule, `server = hash(key) % N`, is trivial to implement and perfectly
balanced — as long as N never changes. The moment a server is added or removed, N
changes, and because the modulo operation depends on the *exact* value of N, the
mapping for nearly every key shifts to a different server. For a distributed cache,
this means a near-total cache wipe at the exact moment you're scaling (usually because
of a traffic spike) — the worst possible time for every request to become a cache miss
and hammer the database.

Consistent hashing decouples "which server" from "the exact count of servers" by giving
both servers and keys a position on a shared, fixed coordinate space (a ring), so that
adding or removing one server only affects the small neighborhood of the ring around
it.

## How it works

### Step 1: Clarify requirements (as you would in the interview)
- **What are we hashing?** Cache keys across cache nodes (the most common interview
  framing) — but the same mechanism applies to sharding a database or routing requests
  to backend servers.
- **How many nodes, and how dynamic is the cluster?** Assume a cache cluster that
  starts at 4 nodes and needs to scale up/down periodically without mass cache
  invalidation.
- **Do nodes have equal capacity?** Assume no — some nodes have more RAM than others,
  and the design should let them take a proportionally larger share.

### Step 2: Why the naive approach fails (the setup for the "aha")
With N=4 nodes, `hash(key) % 4` distributes keys evenly. Suppose we scale to N=5. A key
that hashed to 12 now maps to `12 % 4 = 0` under the old scheme but `12 % 5 = 2` under
the new one — a different node. This isn't an edge case; on average, `N/(N+1)` of all
existing keys move to a different node when scaling from N to N+1. Going from 4 to 5
nodes moves `4/5 = 80%` of keys. At Twitter-scale numbers (recall the 90 GB of "hot"
cached data from `system-design-interview/02`), an 80% cache invalidation event means
80% of that traffic now falls through to the database simultaneously — precisely the
failure mode a cache exists to prevent.

### Step 3: The hash ring
Map the output space of a hash function (e.g., SHA-1, producing values 0 to 2^32-1)
onto a circle, where the maximum value wraps back around to 0:

```
              0 / 2^32
            /          \
      Node D            Node A
         |                |
      Node C            Node B
            \          /
               2^31
```

Both servers and keys are hashed into this same space:
- `server_position = hash(server_id)` (e.g., hash of the IP address or hostname)
- `key_position = hash(key)`

To find the owner of a key, start at its position and walk clockwise around the ring
until you hit the first server. That server owns the key.

**Worked example.** Ring space simplified to [0, 1000) for readability. Four nodes:
A=100, B=350, C=600, D=850. Keys: K1=50, K2=200, K3=500, K4=780.
- K1 (50) walks clockwise to A (100).
- K2 (200) walks clockwise to B (350).
- K3 (500) walks clockwise to C (600).
- K4 (780) walks clockwise to D (850).

Now add Node E at position 500 (between B and C):
- K1, K2, K4 are unaffected — their nearest clockwise node hasn't changed.
- K3 (500) now lands exactly at E, so it's the first node clockwise from its own
  position and moves from C to E.

Only 1 of 4 keys moved. In general, adding a node only affects the keys in the arc
between the new node and its counter-clockwise neighbor — roughly `1/N` of the ring on
average, not 80%.

### Step 4: Deep dive — the two problems basic consistent hashing has, and virtual nodes
State this in the interview as: "the ring by itself has two problems — I'll fix both
with virtual nodes." This shows you know the naive version isn't production-ready on
its own, which is exactly the kind of self-critique interviewers look for.

**Problem 1 — uneven load.** If 4 servers hash to essentially random ring positions,
they might cluster together, leaving one huge gap. Whichever server follows that gap
owns a disproportionate share of the keyspace.

*Worked example:* Node X at 100, Node Y at 900 (only two nodes, extreme case for
clarity). X owns the arc (900, 100] = 200 units (20% of the ring). Y owns (100, 900] =
800 units (80% of the ring) — a 4x imbalance despite having "equal" nodes.

**Problem 2 — can't weight by capacity.** A basic ring gives each physical server
exactly one position, so a server with 2x the RAM of another cannot be given 2x the
keyspace.

**The fix: virtual nodes.** Instead of one ring position per physical server, give each
server many positions ("virtual nodes" or vnodes), e.g., `hash(server_id + "-" + i)`
for `i` in `0..k`. With enough vnodes spread across the ring, the gaps average out.

*Continuing the worked example:* give X and Y 3 vnodes each instead of 1:
- X: X1=150, X2=450, X3=750
- Y: Y1=300, Y2=600, Y3=900

Ranges: (900,150]→X1=250, (150,300]→Y1=150, (300,450]→X2=150, (450,600]→Y2=150,
(600,750]→X3=150, (750,900]→Y3=150. Total for X: 250+150+150=550 (55%). Total for Y:
150+150+150=450 (45%). Three vnodes each took an 80/20 imbalance down to 55/45; real
systems use 100-200 vnodes per physical server, converging close to a perfectly even
split. Vnodes also solve Problem 2 directly: give the higher-capacity server twice as
many vnodes, and it will own roughly twice the keyspace.

### Step 5: Deep dive — replication on the ring
For fault tolerance, most systems using consistent hashing also replicate each key to
`R` distinct physical servers. From the key's position, walk clockwise and collect
the first `R` *distinct physical servers* encountered (skipping additional vnodes that
belong to a physical server already chosen, so replicas land on different hardware).

*Worked example, R=3, four physical servers A-D, two vnodes each:*
Ring order: A1(100) → B1(200) → C1(300) → D1(400) → A2(500) → B2(600) → C2(700) →
D2(800). A key hashing to 150 walks clockwise: first hits B1 (200) → replica 1 on B;
continues to C1 (300) → replica 2 on C; continues to D1 (400) → replica 3 on D. Three
distinct physical servers, as required.

### Step 6: Wrap-up — what this buys you and what it costs
Summarize for the interviewer: minimal data movement on resize (the headline benefit),
better load balance via vnodes, and natural support for replication by walking the ring
further. The cost is metadata — every client or router needs an up-to-date map of ring
positions to physical servers, which must be kept consistent as the cluster changes
(often via a coordination service like ZooKeeper/etcd, or a gossip protocol as in
Cassandra/DynamoDB).

## Pros
- Adding/removing a node moves roughly `1/N` of keys instead of nearly all of them.
- Virtual nodes give near-even load distribution and support heterogeneous server
  capacity.
- Replication integrates naturally: replicas are just "the next R distinct servers
  walking clockwise."

## Cons
- Every client/router needs a synchronized view of ring membership; a stale view
  causes some requests to be misrouted.
- Too few virtual nodes still leaves meaningful imbalance.
- A node failure dumps its keys onto its clockwise neighbor(s); if the cluster is
  already near capacity, this can cascade.
- Range queries are effectively impossible — hashing scatters sequential keys randomly
  around the ring.

## Alternatives
- **Fixed/pre-sharded partitioning** — divide the keyspace into a large fixed number of
  partitions (e.g., 4096) up front and move whole partitions between nodes as they
  join/leave, rather than computing positions dynamically. Used by Redis Cluster and
  Elasticsearch; simpler to reason about operationally.
- **Range partitioning** — assign each server a contiguous key range; supports
  efficient range scans, but needs a coordination service to split/merge ranges and can
  create write hotspots for sequential keys (e.g., timestamps).
- **Directory-based lookup** — a central service maps every key (or partition) to its
  server explicitly. Maximally flexible but adds a lookup hop and a potential single
  point of failure/bottleneck.

## When to use it
Distributed caches (Memcached/Redis client-side sharding), peer-to-peer/Dynamo-style
databases (Cassandra, DynamoDB) that need decentralized, dynamic partitioning, and
load balancers routing sticky sessions to backend servers that scale up/down.

## When NOT to use it
Small, rarely-resized clusters where the operational simplicity of naive modulo hashing
or manual sharding outweighs the resize-cost problem. Also avoid it for workloads that
depend on range queries or multi-key transactions across contiguous keys — hashing
destroys the locality those need; prefer range partitioning there instead.

## Key takeaways / mental model
A ring where both servers and keys are runners; keys always run clockwise to the
nearest server. Removing a server only disturbs the runners between it and the next
server counter-clockwise — nobody else's route changes. Virtual nodes exist purely to
prevent any one server's "aha, no one's ahead of me for a long stretch" gap advantage.
In the interview, always present the naive `hash % N` failure first — it's what makes
the ring's benefit legible — then the ring, then virtual nodes as the fix for the
ring's own imbalance problem, then replication as a natural extension of "keep walking
clockwise."

## Self-check questions
1. Walk through why scaling from 4 to 5 nodes under `hash(key) % N` moves ~80% of keys,
   using the general formula `N/(N+1)`.
2. In the worked example, adding Node E at position 500 only moved K3. Explain in your
   own words why K1, K2, and K4 were unaffected.
3. Why do virtual nodes fix both the uneven-load problem and the
   heterogeneous-capacity problem with a single mechanism?
4. When placing replica 2 and replica 3 for a key with replication factor 3, why must
   you skip a vnode belonging to a physical server you've already selected?
5. A candidate proposes consistent hashing for a system that needs frequent
   multi-key range scans (e.g., "give me all events between timestamp T1 and T2").
   What should you push back on, and what would you propose instead?

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 5
- `system-design/04` (Consistent Hashing) — the same mechanism from the system-design
  angle, with additional worked examples.
- `ddia/10` (Partitioning) — Kleppmann's caveat that most production systems use a
  fixed-partition hybrid rather than pure academic consistent hashing.
