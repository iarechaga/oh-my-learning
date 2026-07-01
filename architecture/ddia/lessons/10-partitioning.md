---
id: ddia/10
subject: ddia
title: Partitioning (Sharding)
slug: partitioning
status: drafted
mastery:
seniority: senior
source: Designing Data-Intensive Applications (Martin Kleppmann), Chapter 6
prerequisites: [ddia/07]
created: 2026-06-30
updated: 2026-06-30
---

# Partitioning (Sharding)

## TL;DR
Partitioning splits a large dataset into smaller, independent subsets called partitions, distributing them across multiple database nodes to allow horizontal scalability. To prevent data loss and ensure high availability, partitioning is combined with replication, meaning every partition is copied across several nodes. This lesson covers key-value partitioning strategies, secondary indexes, rebalancing mechanisms, and request routing architectures.

## The idea
When a dataset grows too large or receives more write traffic than a single database server can handle, we must distribute the workload. While replication duplicates the same data across multiple machines for fault tolerance, partitioning breaks the data apart into smaller, manageable chunks called partitions (or shards). 

```
+-------------------------------------------------------------------+
|                           Total Dataset                           |
|  [Record 1]  [Record 2]  [Record 3]  [Record 4]  [Record 5] ...   |
+------------------------------------+------------------------------+
                                     |
           +-------------------------+-------------------------+
           |                                                   |
           v                                                   v
+---------------------+                             +---------------------+
|     Partition 1     |                             |     Partition 2     |
| [Record 1] [Record 3]                             | [Record 2] [Record 4]
+---------------------+                             +---------------------+
```

Each record belongs to exactly one partition. The primary goal of partitioning is scalability, allowing the system to scale its storage capacity, read throughput, and write throughput by adding more machines. 

When we partition a database, each node only handles a fraction of the total dataset. This means we can store far more data than would fit on any single hard drive, and we can process far more concurrent queries than a single CPU or memory controller could ever support. 

### Combining Partitioning and Replication
Partitioning is almost always combined with replication. Each partition has its own leader and follower replicas, distributed across the cluster. A single database node can act as the leader for some partitions and a follower for others, maximizing resource usage.

```
Node 1                       Node 2                       Node 3
+------------------------+   +------------------------+   +------------------------+
| Partition 1 (Leader)   |   | Partition 1 (Follower) |   | Partition 1 (Follower) |
| Partition 2 (Follower) |   | Partition 2 (Leader)   |   | Partition 2 (Follower) |
| Partition 3 (Follower) |   | Partition 3 (Follower) |   | Partition 3 (Leader)   |
+------------------------+   +------------------------+   +------------------------+
```

In this layout, if Node 1 fails, Partition 1's replica on Node 2 or Node 3 can be promoted to leader, while Node 2 continues serving writes for Partition 2. This hybrid architecture ensures that the system scales horizontally without sacrificing reliability.

---

## How it works

To make partitioning work efficiently, we must choose how to slice the data, search it using secondary indexes, rebalance partitions, and route requests to the correct nodes.

### Partitioning Key-Value Data

The first challenge is deciding how to distribute records across partitions. If our distribution is uneven, some partitions will store more data or handle more traffic, leading to skew. A partition with disproportionately high load is called a hot spot. We use two main partitioning strategies to avoid this:

#### 1. Key Range Partitioning
This strategy assigns a continuous range of keys to each partition, similar to an alphabetical encyclopedia. For example, Partition 1 holds keys from A to C, and Partition 2 holds keys from D to F.

```
       [Key Range Partitioning]
       A - C   ===>   Partition 1 (Node A)
       D - F   ===>   Partition 2 (Node B)
       G - Z   ===>   Partition 3 (Node C)
```

##### Worked Example 1 (Range Scan with Prepended Prefixes)
- A system stores sensor data where the keys are timestamps, such as `2026-06-30T12:00:00`.
- We assign keys from `2026-06-30T00:00:00` to `2026-06-30T08:00:00` to Partition 1. Keys from `2026-06-30T08:00:01` to `2026-06-30T16:00:00` go to Partition 2, and so on.
- When an application queries sensor readings between `12:00:00` and `13:00:00`, it performs a single range scan on Partition 2. This is extremely fast because data is kept in sorted order within the partition.
- A critical bottleneck arises, however, because all writes for the current hour target the exact same partition (Partition 2). This crushes the node hosting Partition 2 while other nodes remain idle.
- To mitigate this timestamp hot-spot, we prepend the sensor ID to the key, changing it to `sensor42_2026-06-30T12:00:00`.
- Writes for different sensors now land on different partitions based on alphabetical sorting. The trade-off is that scanning a range of times across all sensors now requires querying multiple partitions and merging the results.

#### 2. Hash Partitioning
To prevent skew and hot spots, many databases use a hash function to assign keys to partitions. This function takes an arbitrary key and produces a uniformly distributed number.

```
       [Hash Partitioning]
       "user_948"  ===> Hash: 48102 ===> Partition 1
       "user_949"  ===> Hash: 12903 ===> Partition 3
       "user_950"  ===> Hash: 89321 ===> Partition 2
```

##### Worked Example 2 (Compound Keys in Cassandra)
- We have five partitions, and we use a hash function like MurmurHash3 to map a key to a partition ID.
- Sequential keys like `user_94812` and `user_94813` hash to entirely different values, ensuring they land on separate partitions. This even distribution eliminates hot spots.
- The cost is that we completely lose the ability to perform efficient range scans. Adjacent keys are scattered randomly across different partitions, forcing the database to execute a slow scatter-gather query.
- To bridge this gap, databases like Cassandra use a compound primary key. The first column of the key is hashed to determine the partition, while the remaining columns act as a clustering key to keep data sorted within that partition.
- For example, with a compound primary key of `(user_id, timestamp)`, the database hashes `user_id` to select the partition, but stores all records for that user sorted by `timestamp` on that single partition. This allows fast range scans over a time window for a single user, while maintaining an even partition balance across the cluster.

##### Kleppmann's Caveat on Consistent Hashing
In academic papers, "consistent hashing" is often described as the standard way to partition databases. Martin Kleppmann notes that in practice, consistent hashing (which uses a ring of nodes where keys are assigned to the next closest node on the ring) is rarely used in real-world databases. Instead, systems prefer simpler approaches like fixed numbers of partitions or dynamic partition splitting, which are easier to manage, reason about, and balance. 

Consistent hashing is highly effective for transient caches like memcached where nodes join and leave constantly and minor data loss during transitions is acceptable. For databases with durable, transaction-isolated workloads, the complexity of managing a dynamic hash ring is rarely worth the marginal flexibility.

---

### Skew and Hot Spots (The Celebrity Problem)

Even with hash partitioning, extreme application workloads can still cause skew. If a popular celebrity with millions of followers posts an update, millions of users will read and write comments to that single celebrity's ID.

##### Worked Example 3 (Random-Prefix Mitigation)
- A social media post ID `post_777` hashes to Partition 4.
- During a viral event, 50,000 writes per second hit `post_777`. This overloads the node hosting Partition 4.
- To prevent this, the application appends a random two-digit suffix to the key, turning it into a range of sub-keys from `post_777_0` to `post_777_99`.
- This splits the writes for this single hot key across 100 different logical keys, distributing the load over multiple partitions and nodes.
- The trade-off is that reading the post's comments now requires reading all 100 logical keys and merging them on the client-side. This adds significant read latency, so the application should only apply this prefixing technique to a small subset of highly active keys.

---

### Partitioning and Secondary Indexes

The complexity of partitioning increases when we need to query data by fields other than the primary key. Secondary indexes can be structured in two ways:

| Index Type | Write Cost | Read Cost | Scalability | Key Characteristic |
| :--- | :--- | :--- | :--- | :--- |
| **Local (Document-Partitioned)** | Low (write to one partition) | High (scatter-gather) | Highly scalable for writes | Each partition indexes only its own documents. |
| **Global (Term-Partitioned)** | High (touches many partitions) | Low (reads one partition) | Better for read-heavy workloads | The index itself is partitioned across nodes. |

#### 1. Document-Partitioned (Local) Indexes
In this approach, each partition maintains its own local secondary index. When a user writes a record, the database only needs to update the index of the partition that holds that specific record.

##### The Local Index Write
If we write a record `{car_id: 1245, make: "Tesla", color: "red"}` to Partition 1, the node hosting Partition 1 writes the document and appends `1245` to its local index under the term `color:red`. No other node in the cluster is contacted. This keeps writes extremely fast and scalable.

##### The Local Index Read Challenge
If a user searches for all cars with `color:red`, the database does not know which partitions hold those cars. It must send the search query to every single partition in the cluster (e.g., all 16 partitions). Each partition searches its local index and returns its matching list of car IDs. The database coordinator then merges these lists before returning them to the user. This is called a scatter-gather query. It is highly vulnerable to tail-latency amplification: if one partition is slow due to heavy background traffic, the entire search query waits, degrading overall search performance.

#### 2. Term-Partitioned (Global) Indexes
Instead of storing local indexes, we can build a global index that covers the entire dataset. To prevent this global index from becoming a bottleneck on a single node, we partition the index itself by the index term.

##### The Global Index Read
If we search for all cars with `color:red`, we determine which partition holds the "color" index terms. For example, index terms starting with letters `a` to `m` are stored on Partition 3, and `n` to `z` on Partition 4. We can send a single read request directly to Partition 4 (which holds `red`) and get the complete list of matching car IDs immediately. This makes reads highly efficient and avoids scatter-gather overhead.

##### The Global Index Write Challenge
Writing is much slower and more complex. When we insert `{car_id: 1245, make: "Tesla", color: "red"}` into Partition 1, we must update the primary document on Partition 1. We must also contact Partition 4 to append `1245` to the global index entry for `color:red`. Since this write touches multiple partition nodes, it requires a distributed transaction or asynchronous coordination. This adds substantial overhead and can degrade write throughput.

---

### Rebalancing Strategies

As data grows, cluster traffic increases, or nodes join and leave, we must move partitions between machines to maintain balance. This process is called rebalancing.

#### Why "Hash Mod N" is Bad
A naive approach to partitioning is to assign a key to a node using `hash(key) % N`, where N is the number of nodes. 

If the number of nodes N changes from 10 to 11 because we added a machine, almost every key's modulo result changes. This forces nearly the entire database to move across the network, creating massive disk and network overhead. Databases avoid this by using three main rebalancing strategies:

#### 1. Fixed Number of Partitions
We create many more partitions than there are nodes (for example, 256 partitions for 10 nodes). Each node is assigned a subset of these partitions.

When a new node joins the cluster, it takes ownership of a few entire partitions from existing nodes. The boundaries of the partitions themselves never change, and the keys inside them do not move. Only the assignment of partitions to nodes changes, keeping network movement to a minimum.

#### 2. Dynamic Partitioning
Mainly used in range-partitioned databases, this strategy automatically splits a partition into two equal halves when it grows beyond a configured size (such as 10 GB). If a large volume of data is deleted and a partition shrinks, it can merge with an adjacent partition.

This is highly adaptive. A small database starts with a single partition. As data grows, partitions split and are distributed across new nodes, naturally scaling with the workload.

#### 3. Partitioning Proportional to Nodes
Under this strategy, the number of partitions is a fixed multiple of the number of nodes. When a new node joins, it randomly selects a fixed number of existing partitions to split, taking ownership of half of the data from each of those partitions. This keeps individual partition sizes stable as the cluster grows.

#### Automatic vs. Manual Rebalancing
While automatic rebalancing is convenient, it can be dangerous. Rebalancing is a resource-intensive process that requires copying large amounts of data over the network, which can saturate network links and degrade client query performance.

If a node experiences a temporary slowdown or brief network partition, other nodes might assume it failed and trigger automatic rebalancing to evacuate its data. This process adds massive network load, which can slow down other nodes and trigger a cascade of failures across the rest of the cluster. For this reason, most production databases require a human operator to approve or initiate the rebalancing process.

#### Operational Cost and Throttling
To keep rebalancing from killing production performance, databases use throttling mechanisms:
- **Rate-limiting partition migrations**: We limit the bandwidth used for transferring partition data (e.g., capping migration transfers at 50 MB/s).
- **Staging transfers during off-peak hours**: Operators schedule partition migrations during periods of low client activity to minimize user impact.
- **Background priority queues**: Data replication for rebalancing runs on a low-priority thread, ensuring that client read and write requests are always processed first.

---

### Request Routing and Service Discovery

Once the database is partitioned, the client must find which node holds the correct partition for a given key. This is handled in three ways:

1. **Any-Node Routing**: The client connects to any node in the cluster. If that node holds the partition, it processes the request. If not, it forwards the request to the correct node, waits for the response, and returns it to the client.
2. **Routing Tier**: The client sends all requests to a dedicated routing tier or load balancer. The routing tier acts as a partition-aware proxy, directing each request to the appropriate database node.
3. **Partition-Aware Clients**: The client itself maintains a map of partition-to-node assignments and connects directly to the correct node, avoiding extra network hops.

#### Coordination Services and Consensus
To prevent routing tables from getting out of sync, systems need a reliable way to publish updates. Coordination services like Apache ZooKeeper are commonly used as the single source of truth for partition-to-node mappings:
- **ZooKeeper Node Registry**: Each database node registers itself and its assigned partitions in ZooKeeper.
- **Active Watchers**: The routing tier and clients register watchers with ZooKeeper. Whenever a partition is rebalanced and assigned to a new node, ZooKeeper triggers a watch event to push the updated routing table to all active components.
- **Consensus Guarantee**: ZooKeeper uses a consensus protocol to ensure that the routing table remains highly consistent and atomic, preventing split-brain routing tables.

#### Gossip Protocols (Decentralized Routing)
Alternatively, databases like Cassandra use a gossip protocol among the nodes to share routing information directly, avoiding any external coordination service:
- **Peer-to-Peer Gossiping**: Nodes periodically exchange routing state updates with a few random peers. These updates slowly diffuse across the entire cluster.
- **No Single Point of Failure**: This peer-to-peer approach removes ZooKeeper as a single point of failure or scalability bottleneck.
- **Eventual Routing Consistency**: The trade-off is that routing updates are eventually consistent. A client might briefly send a request to the wrong node because its routing map is stale. The recipient node then redirects the request, which adds a minor network overhead during active rebalancing events.

#### Parallel Query Execution (MPP)
For complex analytical queries, simple routing is not enough. Massively Parallel Processing (MPP) database engines break down a complex SQL query into multiple sub-queries. These sub-queries are executed in parallel on the individual partitions holding the data, and the intermediate results are shuffled and merged across nodes to produce the final answer. This parallel execution is critical for fast analytics on large-scale datasets.

## Pros
- **Horizontal scalability**: Spreading data and query workloads across an arbitrary number of cheap commodity servers bypasses the physical hardware limits of a single machine.
- **Increased throughput**: Read and write operations can execute in parallel across different partitions, multiplying the total capacity of the database.
- **Improved fault isolation**: A hardware failure on a single node only takes down the specific partitions stored on that node, leaving the rest of the cluster's partitions fully operational.
- **Geographic distribution**: Data can be partitioned so that records are stored physically closer to the users who access them, reducing overall network latency.

## Cons
- **High operational complexity**: Managing partition maps, cluster coordination, and service discovery adds significant engineering and operational overhead.
- **Expensive secondary indexes**: Searching by fields other than the primary key requires slow scatter-gather queries or complex, distributed index updates.
- **Limited cross-partition queries**: Joining tables or running transaction updates across multiple partitions is extremely slow, difficult to implement, or completely unsupported.
- **Risk of data skew and hot spots**: Choosing an ineffective partition key can lead to unbalanced loads, which slows down the entire database to the speed of its single overloaded node.

## Alternatives
- **Vertical Scaling (Scaling Up)**: Upgrading the hardware of a single machine by adding more RAM, faster CPUs, or larger NVMe SSDs. This keeps the architecture simple and avoids network latency, but it has hard physical limits and becomes exponentially expensive at scale.
- **Replication-Only Cluster**: Running a cluster where every node contains a complete copy of the entire dataset, as described in [07-replication-single-leader.md](../lessons/07-replication-single-leader.md). This is ideal when the total data volume is small but read traffic is extremely high, avoiding the complexity of sharding.
- **Distributed SQL (NewSQL)**: Reaching for modern distributed databases like CockroachDB, Google Spanner, or TiDB. These systems handle automatic partitioning, secondary index sync, and rebalancing under the hood while maintaining standard SQL capabilities and ACID transactions. This is preferable if your team wants horizontal scaling but cannot tolerate the limited query semantics of NoSQL sharding.
- **Federated Databases**: Splitting data across entirely independent databases at the application level. This is simpler to implement than clustering, but it forces application developers to manually handle routing, joins, and data consistency.

## When to use it
You should use partitioning when your dataset size, write volume, or read traffic exceeds the hardware limits of a single database server. It is highly suited for large-scale key-value workloads, time-series data, log analytics, and multi-tenant applications where data can be naturally grouped by a partition key with little to no need for cross-partition queries or transactions.

## When NOT to use it
Do not use partitioning if your entire dataset and workload easily fit on a single, reasonably sized server. You should also avoid it if your application relies heavily on complex SQL joins, multi-record transactions across different entities, or frequent queries on multiple secondary indexes. For these use cases, a single-node relational database or a replication-only architecture is far easier to develop, maintain, and tune.

## Key takeaways / mental model

Think of partitioning like organizing a massive warehouse of documents. 

- **Key range partitioning** is like filing papers alphabetically by client name. It is easy to find all clients named "Smith", but if a single letter has millions of clients, that shelf overflows. 
- **Hash partitioning** is like assigning papers to boxes using a random mathematical formula based on the client's ID. It keeps all boxes perfectly balanced, but if you want to find all clients in a specific postal code, you must open and search every single box in the warehouse.

## Self-check questions
1. Why is using `hash(key) % N` as a partitioning strategy highly problematic during cluster rebalancing, and how do fixed partitions solve this?
2. Explain the fundamental trade-off between local (document-partitioned) and global (term-partitioned) secondary indexes in terms of read and write performance.
3. How does dynamic partitioning work, and which partitioning strategy does it typically pair with?
4. What is a "scatter-gather" query, and why does it represent a major performance bottleneck in partitioned databases?
5. Imagine a social media system where comments are partitioned by a hash of the Post ID. A post by a celebrity goes viral, receiving millions of comments. How does this partition layout fail, and what mitigation technique can you apply?
6. Why can automatic, unsupervised rebalancing under heavy database load trigger a cascade of failures across a cluster, and how do database operators mitigate this risk?
7. Explain how a compound primary key (such as Cassandra's partition key and clustering key) combines the benefits of hash partitioning and key range scans. What are the main limits of this design?
8. What is Massively Parallel Processing (MPP) in the context of analytical query execution, and how does it coordinate work across multiple partitioned nodes?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 6
- [07-replication-single-leader.md](../lessons/07-replication-single-leader.md)
