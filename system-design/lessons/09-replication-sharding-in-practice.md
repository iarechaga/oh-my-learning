---
id: system-design/09
subject: system-design
title: Replication and Sharding in Practice
slug: replication-sharding-in-practice
status: drafted
mastery:
source: System Design Guide for Software Professionals (Sinha & Chopra), Chapter 5
prerequisites: [ddia/07, ddia/08, ddia/10]
created: 2026-06-30
updated: 2026-06-30
---

# Replication and Sharding in Practice

## TL;DR
Designing a production-grade data tier requires combining replication to ensure high availability with sharding to scale write throughput and storage capacity. By aligning single-leader, multi-leader, or leaderless architectures with partition-key strategies, systems can store petabytes of data while keeping latency low. However, this combination introduces trade-offs like replication lag, resharding storms, and strict quorum conditions.

## The idea
Single database instances eventually hit physical ceilings in CPU, memory, storage, and network throughput. While vertical scaling buys time, large-scale systems must distribute data across multiple physical machines. 

Historically, companies scaled relational systems by purchasing larger mainframes. However, this approach is extremely expensive and eventually hits hard physical limits of hardware manufacturing. Horizontal scaling on commodity hardware has become the industry standard.

This distribution is achieved using two core axes:

1. Replication copies the exact same data to multiple nodes. This mechanism improves read throughput, tolerates node crashes, and keeps data geographically close to users.

2. Sharding, also known as partitioning, divides a large dataset into smaller, independent subsets. Each shard is assigned to a specific node, which splits the write workload across the cluster.

High-throughput systems must use both techniques simultaneously. A cluster is typically divided into shards, and each shard is replicated across a small group of nodes. This setup avoids single points of failure while scaling horizontal capacity.

## How it works

### Scaling Reads with Replication Topologies
Replication requires keeping data copies synchronized across nodes. The way writes are routed determines the topology of the system:

* **Single-Leader Replication (DDIA Concept 07)**: All writes go to a designated leader node. The leader writes to its local storage and sends a stream of data changes to followers. Followers apply these changes and serve read-only queries. 

  This pattern is great for read-heavy workloads but creates a write bottleneck at the leader. If the leader crashes, the system must trigger a failover process. This involves selecting a new leader, which can lead to split-brain scenarios where two nodes believe they are both the active leader.

* **Multi-Leader Replication (DDIA Concept 08)**: Multiple nodes act as leaders, each accepting writes and forwarding them to other leaders. This approach suits multi-datacenter setups but introduces complex write-conflict resolution challenges, such as resolving concurrent edits on the same record. Conflict resolution often requires last-write-wins (LWW) rules or conflict-free replicated data types (CRDTs).
  
  LWW relies on timestamps, which are prone to clock drift across servers. To achieve better guarantees, systems use physical clocks synchronized via NTP or expensive GPS-based atomic clocks. Alternatively, they use logical clocks like vector clocks to track causal history.
  
  CRDTs resolve conflicts deterministically. State-based CRDTs merge complete replica states, while operation-based CRDTs propagate mutation operations across nodes, ensuring all replicas eventually converge to the same state.

* **Leaderless Replication**: Clients write to multiple nodes directly. The system relies on quorums and background processes like read repair and active anti-entropy to resolve version mismatches without any single node acting as an orchestrator. This pattern is pioneered by Dynamo-style databases to provide extreme write availability.

```
[Replication Topologies Comparison]

+---------------+---------------+---------------+---------------------+---------------------+
| Topology      | Write Latency | Read Latency  | Conflict Resolution | Failover Complexity |
+---------------+---------------+---------------+---------------------+---------------------+
| Single-Leader | Low (1 node)  | Low (replicas)| None (sequential)   | High (re-election)  |
+---------------+---------------+---------------+---------------------+---------------------+
| Multi-Leader  | Low (local)   | Low (local)   | High (CRDTs/LWW)    | Low (multi-active)  |
+---------------+---------------+---------------+---------------------+---------------------+
| Leaderless    | Medium (W quorum) High (R quorum) Medium (Read Repair) | None (no leader)    |
+---------------+---------------+---------------+---------------------+---------------------+
```

When scaling reads via follower replicas, replication lag is inevitable. This lag is not a static constant; it fluctuates dynamically based on network congestion, disk write throughput on followers, and replication thread bottlenecks. In production systems, engineering teams monitor replication lag closely by injecting heartbeat timestamps on the leader and measuring how long they take to appear on followers. When lag spikes past a safety threshold, the routing tier can temporarily stop directing read queries to the lagging node.

If a client writes to the leader and immediately reads from a lagging follower, they may observe stale data. This anomaly requires carefully designed consistency guarantees:

* **Read-After-Write Consistency**: Users must always see their own updates. Systems achieve this by routing reads for a user's own profile to the leader, while routing other reads to followers.

* **Monotonic Reads**: A user won't see data slip backward in time. This is achieved by hashing the user ID to a specific replica, ensuring all their reads go to the same node instead of bouncing across different servers with varied lags.

* **Consistent Prefix Reads**: Reads must show causal sequences in order. This guarantee is critical in partitioned databases where different shards might replicate at different speeds, which could cause a reply to appear before the question that prompted it.

### Sharding Strategies and Partitioning (DDIA Concept 10)
Sharding divides data to prevent hot spots. The three main strategies for assigning records to shards are:

* **Range-Based Sharding**: Keys are kept sorted, and shards own contiguous ranges. This makes range queries highly efficient, but it easily creates write hot spots if keys are sequential (like auto-incrementing IDs or timestamps) because all new writes hit the same end shard.

* **Hash-Based Sharding**: A hash function maps keys uniformly across a numeric range. This distributes writes evenly but destroys key ordering, making range queries require parallel scans across all shards.

* **Directory-Based Sharding**: A lookup service or routing tier maps keys to shard IDs. This provides massive flexibility for manual data placement but introduces a centralized lookup bottleneck and a single point of failure.

```
[Sharding Strategies Trade-offs]

+-----------------+---------------------------+---------------------------+------------------+
| Strategy        | Best For                  | Hot Spot Risk             | Range Queries    |
+-----------------+---------------------------+---------------------------+------------------+
| Range-Based     | Ordered sequences         | High (on sequential keys) | Extremely Fast   |
+-----------------+---------------------------+---------------------------+------------------+
| Hash-Based      | Uniform write distribution| Very Low                  | Very Slow (scan) |
+-----------------+---------------------------+---------------------------+------------------+
| Directory-Based | Dynamic key placement     | Low (managed by directory)| Slow (lookup)    |
+-----------------+---------------------------+---------------------------+------------------+
```

### DynamoDB-Style Architecture
DynamoDB and Cassandra combine leaderless replication with hash-based partitioning:

* **Consistent Hashing**: Hash values are mapped onto a logical ring. Each node is assigned a token on the ring and owns the range between its token and its predecessor's token.

* **Virtual Nodes (Vnodes)**: Physical machines are assigned multiple logical tokens on the ring. This balances data distribution when nodes have varied capacities and simplifies rebalancing because adding a physical node means redistributing smaller virtual nodes.

* **Quorum ($W + R > N$)**: For $N$ replicas of a partition, a write is successful if acknowledged by $W$ nodes, and a read is successful if it queries $R$ nodes. If $W + R > N$, the read quorum and write quorum must overlap by at least one node, ensuring the client reads the latest version.

* **Sloppy Quorums and Hinted Handoff**: If some nodes are unreachable, writes can be accepted by temporary nodes outside the home replica set. When the original node recovers, the temporary node delivers the writes back to it.

* **Active Anti-Entropy**: In the background, replica nodes use Merkle trees to compare their stored data ranges. This allows them to identify and copy missing or outdated keys without transferring the entire database contents over the network.

* **Global Tables**: Active-active replication across geographic regions. This setup relies on conflict-free replicated data types or last-write-wins rules to resolve write collisions when data is updated concurrently in different regions.

### Wide-Column Region Splits
Databases like HBase and Bigtable use range partitioning. Data is ordered lexicographically. When a partition (region) exceeds a size limit (such as 10 GB), the storage engine automatically splits it into two new regions. A master node coordinates the split and updates the routing metadata, allowing the system to scale storage dynamically while maintaining key sorted order.

During a region split, the system creates tiny reference files pointing to the parent region's files. This design ensures that the split completes in milliseconds. Later, background major compactions rewrite the physical data into separate files on disk, cleaning up the parent references.

Conversely, if regions shrink significantly due to heavy deletes, the master node can coordinate region merges. Merging empty or near-empty regions prevents the cluster from wasting resources on managing thousands of tiny, underutilized partitions.

### Combining Replication with Sharding
To achieve both high availability and scale, a database partition is not just a single node; it is a replication group. In this design, the database is divided into multiple shards, and each shard is replicated across $N$ nodes. 

A single physical machine might act as the leader for Shard 1, a follower for Shard 2, and a follower for Shard 3. This interleaving maximizes hardware utilization and ensures that even if several nodes fail, every partition remains readable and writeable.

```
       [Combining Replication with Sharding Cluster View]
       
  +------------------+  +------------------+  +------------------+
  |      Node A      |  |      Node B      |  |      Node C      |
  |                  |  |                  |  |                  |
  | Shard 1 (Leader) |  | Shard 1 (Follow) |  | Shard 1 (Follow) |
  | Shard 2 (Follow) |  | Shard 2 (Leader) |  | Shard 2 (Follow) |
  | Shard 3 (Follow) |  | Shard 3 (Follow) |  | Shard 3 (Leader) |
  +------------------+  +------------------+  +------------------+
```

---

### Worked Example 1: Hash Sharding a 1-Billion-Row Users Table
We need to partition a users table containing 1,000,000,000 rows. The key is `user_id` (UUIDv4). Each row is roughly 500 bytes, totaling 500 GB of data. We want to distribute this across an initial cluster of 4 physical nodes using consistent hashing with 256 virtual nodes.

```
Step 1: Compute Hash Range
The hash function produces a 32-bit integer: 0 to 4,294,967,295.

Step 2: Assign Vnodes
Each physical node gets 64 vnodes.
Node 1 gets vnodes: {v0, v4, v8, ...}
Node 2 gets vnodes: {v1, v5, v9, ...}
Node 3 gets vnodes: {v2, v6, v10, ...}
Node 4 gets vnodes: {v3, v7, v11, ...}

Step 3: Map a User ID
User UUID: f47ac10b-58cc-4372-a567-0e02b2c3d479
Hash(UUID) = 1,073,741,824 (exactly 25% of the ring).
This hash maps to vnode 64, which is assigned to Node 1.

Step 4: Scale Capacity
We add Node 5 to the cluster.
Node 5 needs 51 vnodes. It takes these vnodes from existing nodes:
- Node 1 surrenders 13 vnodes to Node 5
- Node 2 surrenders 13 vnodes to Node 5
- Node 3 surrenders 13 vnodes to Node 5
- Node 4 surrenders 12 vnodes to Node 5

Only the data associated with those specific reassigned vnodes must migrate over the network.
The other 80% of the data remains completely untouched on its original physical nodes.
This prevents a complete re-sharding storm where all data moves to new locations.
```

---

### Worked Example 2: Follower Lag and Read Consistency Trade-Off
A social network uses single-leader replication to scale reads for user posts. The leader handles all post creations. Three followers handle timeline reads.

```
Time 100ms: User A creates a post. 
            The write is saved to Leader.
Time 101ms: Leader responds "Success" to User A.
Time 102ms: User A refreshes their page.
            The load balancer routes the read to Follower 3.
            Follower 3 is currently lagging behind Leader by 150ms.
Time 103ms: Follower 3 responds "No posts found".
            User A sees their post disappear. This breaks read-after-write consistency.

[The Solution: Routing Tier Policy]
If a user reads their own feed:
Route read to Leader.

If a user reads another user's feed:
Route read to Follower.

Track the user's latest update timestamp.
If the update happened less than 5 seconds ago, force the read to go to Leader.
This guarantees they see their own updates while offloading 95% of reads to followers.
```

---

### Worked Example 3: Configuring a Leaderless Quorum
We configure a cluster with $N = 3$ replicas to store session data. We want to analyze what happens during concurrent operations and node failures under different quorum values.

```
Scenario A: $W = 2, R = 2$ ($W + R > N$)
1. Client writes key "sess_1" with value "v2", version 2.
2. The write succeeds on Node A and Node B. Node C fails or is slow.
3. Since $W=2$, the write returns success to the client.
4. Client reads key "sess_1" from Node B and Node C.
5. Node B returns "v2" (version 2). Node C returns "v1" (version 1).
6. The client compares versions, returns "v2" to the user, and initiates a background read repair on Node C.
7. This configuration guarantees strong consistency because Node B is present in both the write set {A, B} and the read set {B, C}.

Scenario B: $W = 1, R = 2$ ($W + R \le N$)
1. Client writes "sess_2" with value "v3", version 3.
2. Write succeeds on Node A ($W=1$). Node B and Node C do not receive it yet.
3. Client immediately reads "sess_2" from Node B and Node C.
4. Both return "v2" (version 2).
5. The client receives stale data. Strong consistency is lost because the write set {A} and the read set {B, C} do not overlap.
```

## Pros
* **Horizontal scalability**: Sharding allows scaling writes and storage capacity linearly by adding cheap commodity servers instead of expensive hardware upgrades.
* **High fault tolerance**: Replication ensures the system remains operational and durable even if several physical nodes crash.
* **Low read latency**: Read replicas can be distributed globally, placing data physically closer to users and reducing network transit times.
* **Load distribution**: Splitting writes through sharding and reads through replicas prevents any single database node from becoming a hot spot.
* **Seamless rolling maintenance**: Upgrades, backups, and maintenance can be performed on replicas one by one without system downtime.
* **Geographical proximity**: Placing replicas in different regions keeps data close to international user bases, minimizing global latency.

## Cons
* **Operational complexity**: Monitoring, managing, and rebalancing a sharded cluster requires sophisticated automation and tooling.
* **Stale reads**: Relying on asynchronous replicas means application developers must design around temporary consistency anomalies and write complex handling code.
* **No multi-shard transactions**: Atomic transactions spanning multiple shards are extremely expensive, slow, and often completely unsupported.
* **Resharding storms**: Changing sharding keys or rebalancing partition ranges moves gigabytes of data across the network, degrading live application performance.
* **Split-brain risks**: In single-leader setups, network partitions can cause multiple nodes to claim leadership, leading to data corruption if writes are accepted.
* **Cross-datacenter bandwidth costs**: Replicating data across regions constantly consumes network bandwidth, resulting in high cloud hosting fees.

## Alternatives
* **Vertical scaling**: Upgrading to a larger database instance with more CPU, RAM, and disk IOPS. This avoids architectural complexity but has hard physical ceilings.
* **Distributed SQL databases**: Databases like CockroachDB or Google Spanner manage sharding and replication transparently. This keeps standard SQL features intact but adds query latency.
* **NoSQL Document Stores**: Systems like MongoDB that handle sharding natively. This works well for unstructured data but sacrifices relational constraints.
* **Read-only relational replicas**: Keeping a single relational database for writes and using replication only to scale reads. This keeps the database simple but does not scale write throughput.

## When to use it
* **Write throughput bottleneck**: Choose this when a single database leader is saturated with write operations and queueing delays are spiking.
* **Dataset exceeds single-node storage**: Use sharding when your total volume of data exceeds the maximum disk capacity of a single high-end cloud instance.
* **Global audience**: Use multi-region replication to deliver single-digit millisecond read latencies to users distributed across different continents.
* **High-availability requirements**: Use this when your business cannot tolerate any database downtime, as replication groups allow seamless failovers.
* **Geographical compliance**: Use sharding combined with country-specific replica sets to keep sensitive user data within legal boundaries.

## When NOT to use it
* **Complex relational queries**: Avoid this when your application relies heavily on SQL joins across multiple tables. These joins require slow cross-network coordination once sharded.
* **Small datasets**: Don't use sharding if your entire dataset fits comfortably in the memory of a standard virtual machine. The engineering overhead outweighs any minor scaling benefit.
* **Low write volume**: If writes are sparse, stick to simple single-leader replication with read replicas. Do not add the partitioning complexity of sharding.
* **Strict ACID transaction requirements**: If your business logic requires transactions that span many different types of entities, sharding will make maintaining atomicity extremely slow and complex.
* **Monolithic team structures**: Avoid this if your engineering team is small and lacks dedicated platform or DevOps engineers to manage the complex cluster operations.

## Key takeaways / mental model
Think of sharding as cutting a massive book into individual chapters and giving each chapter to a different person (sharding). Think of replication as making photocopies of each chapter so multiple people can read them at the same time (replication). To scale, you must do both. Each chapter is stored by a small team of people. If one person falls asleep, their teammates have the copy. If a team gets overwhelmed, you split their chapter in half and hand the new pieces to a fresh team.

## Self-check questions
1. Why does a quorum of $W=2, R=2$ with $N=3$ guarantee that a reader will see the most recent write, and what happens if one node goes offline?
2. How does consistent hashing minimize data movement during cluster expansion compared to a simple modulo-based sharding scheme (`hash(key) % node_count`)?
3. A system requires strict read-after-write consistency for a user's own profile updates but wants to scale reads using followers. What routing policy solves this?
4. What is the fundamental difference in how write conflicts are handled in single-leader replication versus multi-leader replication?
5. Under what conditions will an HBase region split occur, and how does the master node coordinate this split without taking the database offline?
6. Imagine a user table sharded by `country_id`. Why is this a dangerous choice for a global application, and what key would you choose instead to avoid hot spots?
7. In leaderless replication, how do background read repairs differ from active anti-entropy using Merkle trees?
8. What is split-brain in a single-leader cluster, and how do consensus-based voting systems prevent two nodes from accepting writes concurrently?

## References
- System Design Guide for Software Professionals (Sinha & Chopra), Chapter 5
- Designing Data-Intensive Applications (Kleppmann), Chapter 5 (Replication) and Chapter 6 (Partitioning)
