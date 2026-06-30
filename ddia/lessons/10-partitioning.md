---
id: ddia/10
subject: ddia
title: Partitioning (Sharding)
slug: partitioning
status: drafted
mastery:
source: Designing Data-Intensive Applications (Martin Kleppmann), Chapter 6
prerequisites: [ddia/07]
created: 2026-06-30
updated: 2026-06-30
---

# Partitioning (Sharding)

## TL;DR
Partitioning splits a large dataset into smaller, independent subsets called partitions, distributing them across multiple database nodes to allow horizontal scalability. Each partition functions as a small database of its own, meaning the database can handle much higher query and write throughput than any single machine. By distributing the data and query load evenly across a cluster, partitioning prevents individual nodes from becoming bottlenecks.

## The idea
When a dataset grows beyond the storage capacity or processing power of a single server, we must distribute the data across multiple machines. While replication, which we discussed in [07-replication-single-leader.md](07-replication-single-leader.md), copies the exact same data to multiple nodes to ensure fault tolerance, partitioning breaks the data apart so that different nodes hold different subsets.
Every record, whether it is a row in a SQL table or a document in a NoSQL database, belongs to exactly one partition. The primary motivation for partitioning is scalability. If a database is partitioned evenly across ten nodes, each node only needs to handle one tenth of the total read and write requests, theoretically increasing system throughput tenfold.
However, partitioning is rarely perfect. If some partitions receive far more data or read/write traffic than others, we have skew. A partition with a disproportionately high workload is called a hot spot. In a highly skewed database, the entire system can slow down to the speed of the single hot spot node, defeating the purpose of sharding. Therefore, the core challenge of partitioning is to choose a partition key and strategy that distributes data and queries as evenly as possible.

## How it works
To understand how partitioning works in practice, let us look at the strategies for dividing key-value data, managing secondary indexes, rebalancing data, and routing client requests.

### Partitioning Key-Value Data
The simplest way to partition key-value data is to decide which partition holds a record based on its key. There are two primary strategies:

#### 1. Key Range Partitioning
We assign a continuous range of keys to each partition, similar to how an encyclopedia divides words alphabetically across volumes. For example, Partition 1 holds keys from A to C, Partition 2 holds keys from D to F, and so on.
Within each partition, we can keep the keys in sorted order. This makes range scans incredibly efficient. If we want to retrieve all sensor measurements for a specific day, a single range query can fetch all matching records from one partition in a single sequential disk scan.
The major drawback of key range partitioning is the high risk of hot spots. If our keys are timestamps, then all writes for a given day will target the exact same partition. The node hosting that partition will be crushed by write traffic, while all other nodes sit idle.
To mitigate this, applications can prepend a prefix to the key. For example, if we prepend the sensor ID to the timestamp, writes for different sensors are distributed across different partitions. However, this comes at a cost, as range queries across all sensors now require separate requests to multiple partitions.

#### 2. Hash Partitioning
To avoid skew and hot spots, many distributed databases use a hash function to determine the partition for a given key. A cryptographic or non-cryptographic hash function (like MurmurHash3) takes an input key and produces a uniform distribution of output values.
If we have five partitions, we can hash the key and map the hash value to a partition. For instance, the key "user_94812" hashes to a value that falls into the range assigned to Partition 3, while "user_94813" hashes to a value for Partition 1. Even if user IDs are sequential, their hashes are distributed randomly, ensuring an even distribution of data.
While hash partitioning is excellent at preventing hot spots, it destroys efficient range queries. Keys that were once adjacent are now scattered randomly across different partitions. To perform a range query, the database must send the request to every single partition, which is highly inefficient.
To get the best of both worlds, some databases like Cassandra use a compound primary key. The first column of the key is hashed to determine the partition, while the remaining columns are used as a clustering key to keep data sorted within that partition. This allows efficient range scans, but only within a single partition.

#### Mitigating Hot Spots on Hash Keys
Even with hash partitioning, extreme hot spots can still occur. If a celebrity on a social network with millions of followers receives a flurry of comments, all writes for that celebrity's ID will hash to the same partition, overloading that node.
To mitigate this, the application must detect highly active keys and append a random two-digit number to the end of the key. This splits the writes for that single hot key across 100 different sub-keys, distributing them to multiple partitions. The downside is that reads for that celebrity's data must now read from all 100 sub-keys and merge the results.

### Partitioning and Secondary Indexes
Partitioning gets significantly more complex when we introduce secondary indexes, which are essential for searching records by fields other than the primary key. There are two main approaches:

#### 1. Document-Partitioned (Local) Indexes
In a document-partitioned database, each partition maintains its own local secondary index. When you insert a record, the database writes it to the appropriate partition and indexes it locally.
This approach makes writes very fast, since the write only needs to update the local index on that single partition. However, reads become extremely expensive. If you search for cars with the color "blue", the database has no idea which partitions hold those cars. It must send the query to every single partition, wait for all of them to search their local indexes, and then merge the results. This is called a scatter-gather query, and it is highly susceptible to tail-latency amplification.

#### 2. Term-Partitioned (Global) Indexes
Instead of keeping a separate index on each partition, we can build a global index that covers all partitions. To prevent this global index from becoming a bottleneck on a single node, we partition the index itself.
For example, index terms starting with letters A to M might be stored on Partition 1, and N to Z on Partition 2. When you query cars with the color "blue", the database lookups the term "blue" in the global index, which points directly to the exact partitions holding those records.
This makes reads highly efficient because they only target the partition holding that specific index term. However, writes are slower and more complex. A single write to a partition might require updating global index entries stored on multiple other partitions, requiring expensive distributed transactions or asynchronous background updates.

### Rebalancing Strategies
As data grows, read traffic increases, or nodes fail, we must move data and partitions from one node to another. This process is called rebalancing. A good rebalancing strategy must move data as quickly and safely as possible while minimizing disk and network overhead.

#### Why "Hash Mod N" is Bad
A simple partitioning strategy is to assign a key to a node using `hash(key) % N`, where N is the number of nodes. While this is easy to implement, it is a disaster for rebalancing. If N changes from 10 to 11 because we added a node, almost every key's mod value changes. This forces nearly the entire database to move across the network, causing a massive, unnecessary performance hit.

#### 1. Fixed Number of Partitions
To avoid the mod N problem, we can create many more partitions than there are nodes (e.g., 256 partitions for 10 nodes). Each node is assigned a subset of these partitions.
When a new node joins the cluster, it takes a few partitions from existing nodes until the cluster is balanced again. The boundaries of the partitions themselves never change, and the keys within those partitions do not move to different partitions. Only the assignment of entire partitions to nodes changes. This greatly reduces the volume of data that needs to move across the network.

#### 2. Dynamic Partitioning
Relational databases that use key range partitioning often use dynamic partitioning. When a partition grows larger than a configured limit (such as 10 GB), it automatically splits into two equal partitions, each taking half of the data. Conversely, if a large volume of data is deleted and a partition shrinks, it can merge with an adjacent partition.
This is highly adaptive. A small database starts with a single partition on a single node. As the database grows, partitions split and are distributed across new nodes, ensuring the workload scales naturally with data volume.

#### 3. Partitioning Proportional to Nodes
Under this strategy, the number of partitions is a fixed multiple of the number of nodes. When a new node joins the cluster, it randomly chooses a fixed number of existing partitions to split, taking ownership of half of the data from each of those partitions. This keeps the size of each partition relatively stable as the cluster grows.

### Request Routing and Service Discovery
When a client wants to read or write a key, it must find the node holding the correct partition. This is a classic service discovery challenge. Databases generally employ one of three routing patterns:
1. **Any-Node Routing**: The client sends the request to any node in the cluster. If that node holds the partition, it processes the request. If not, it forwards the request to the correct node, waits for the response, and returns it to the client.
2. **Routing Tier**: The client sends all requests to a dedicated routing tier or load balancer. The routing tier acts as a partition-aware proxy, directing each request to the appropriate node.
3. **Partition-Aware Clients**: The client itself maintains a map of which partitions are on which nodes and connects directly to the correct node, eliminating any intermediate network hops.

To prevent routing tables from getting out of sync, many systems use an external coordination service like Apache ZooKeeper. ZooKeeper acts as the single source of truth for partition-to-node mapping. When a partition moves during rebalancing, ZooKeeper notifies the routing tier or clients, allowing them to update their local routing tables instantly.

## Pros
- Enables horizontal scalability by spreading data and query workloads across an arbitrary number of cheap commodity servers.
- Increases overall read and write throughput, as different nodes can process independent queries and writes in parallel.
- Improves fault tolerance and availability, as the failure of a single node only affects the specific partitions stored on that node rather than the entire dataset.

## Cons
- Increases system complexity significantly, as the application or database engine must handle request routing, partition maps, and cluster coordination.
- Makes secondary indexes highly expensive or complex, requiring either slow scatter-gather queries or slow global index updates.
- Severely limits cross-partition operations, making joins and multi-record transactions extremely slow, difficult to implement, or completely unsupported.

## Alternatives
- **Vertical Scaling (Scaling Up)**: Upgrading the hardware of a single machine by adding more RAM, faster CPUs, or larger NVMe SSDs. This differs from partitioning because it keeps the architecture simple and avoids network overhead, but it has hard physical limits and becomes exponentially expensive.
- **Replication-Only Cluster**: Running a cluster where every node contains a complete copy of the entire dataset, as described in [07-replication-single-leader.md](07-replication-single-leader.md). This differs because the dataset is not split, meaning every node must have enough storage for the whole dataset. This is preferable when the total data volume is small but read traffic is extremely high.

## When to use it
You should use partitioning when your dataset size, write volume, or read traffic exceeds the hardware limits of a single database server. It is highly suited for large-scale key-value workloads, time-series data, log analytics, and multi-tenant applications where data can be naturally grouped by a partition key with little to no need for cross-partition queries or transactions.

## When NOT to use it
Do not use partitioning if your entire dataset and workload easily fit on a single, reasonably sized server. You should also avoid it if your application relies heavily on complex SQL joins, multi-record transactions across different entities, or frequent queries on multiple secondary indexes. For these use cases, a single-node relational database or a replication-only architecture is far easier to develop, maintain, and tune.

## Key takeaways / mental model
Think of partitioning like organizing a massive warehouse of documents. Key range partitioning is like filing papers alphabetically by client name. It is easy to find all clients named "Smith", but if a single letter has millions of clients, that shelf overflows. Hash partitioning is like assigning papers to boxes using a random mathematical formula based on the client's ID. It keeps all boxes perfectly balanced, but if you want to find all clients in a specific postal code, you must open and search every single box in the warehouse.

## Self-check questions
1. Why is using `hash(key) % N` as a partitioning strategy highly problematic during cluster rebalancing, and how do fixed partitions solve this?
2. Explain the fundamental trade-off between local (document-partitioned) and global (term-partitioned) secondary indexes in terms of read and write performance.
3. How does dynamic partitioning work, and which partitioning strategy does it typically pair with?
4. What is a "scatter-gather" query, and why does it represent a major performance bottleneck in partitioned databases?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 6
- [07-replication-single-leader.md](07-replication-single-leader.md)
