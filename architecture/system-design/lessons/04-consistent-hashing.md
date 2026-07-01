---
id: system-design/04
subject: system-design
title: "Consistent Hashing"
slug: consistent-hashing
status: drafted
mastery: 
seniority: mid
source: "System Design Guide for Software Professionals (Sinha & Chopra), Chapters 3 and 5"
prerequisites: [ddia/10]
created: 2026-06-30
updated: 2026-06-30
---

# Consistent Hashing

## TL;DR
Consistent hashing is a partitioning strategy that maps both servers and data keys to a shared circular space called a hash ring. When a server is added or removed, only a small fraction of keys must be relocated, avoiding the massive reshuffling caused by naive hash-modulo methods. It scales distributed systems horizontally by decoupling partition mapping from the absolute server count.

## The idea
In large scale distributed systems, data must be partitioned across multiple servers to handle load and storage limits. The simplest way to distribute keys across N servers is to compute `hash(key) % N`. This works well when the cluster size is static.

If you add a new server or a server fails, the value of N changes. Suddenly, almost every key hashes to a different node. This triggers a massive, system wide data transfer as keys move to their new locations, which can overwhelm databases, clear caches, and cause severe performance degradation.

Consistent hashing solves this problem. It maps both keys and servers to a circular coordinate space. By decoupling server assignment from the exact count of active servers, adding or removing a node only impacts a local subset of keys. It ensures that only a fraction of keys, roughly equal to the total keys divided by the number of servers, are relocated when the cluster topology changes.

## How it works

### Naive Hash Modulo N and its Fatal Flaw
In a standard hashing scheme, we assign keys to N nodes using:
`node_index = hash(key) % N`

If we have 4 nodes (0, 1, 2, 3) and N changes to 5 because we scaled up, the denominator changes. For example, a key hashing to 12 goes to node 0 under mod 4, but goes to node 2 under mod 5. A key hashing to 34 goes to node 2 under mod 4, but goes to node 4 under mod 5. On average, N / (N + 1) of the existing keys must be moved to different nodes when scaling from N to N + 1 nodes. If N is large, this is nearly 100% of your data.

### The Hash Ring Concept
Consistent hashing maps both servers and keys to a continuous circular range. This range is usually represented as a circle, or a hash ring. Let's assume we use a standard 32 bit hash function like MD5 or SHA-1, which produces outputs from 0 to 2^32 - 1. We treat the largest hash value as wrapping around to 0, forming a closed loop.

```
          0 / 2^32
         /        \
    3*2^30        2^30
       |            |
    2*2^30        2*2^31
         \        /
           2^31
```

### Key and Node Mapping
To place a server on the ring, we hash its unique identifier, such as its IP address or hostname:
`server_position = hash(server_ip)`

To place a data key on the ring, we hash the key itself:
`key_position = hash(key)`

To find which server should store a key, we locate the key's position on the ring, then travel clockwise until we encounter the first server. That server becomes the coordinator or owner of the key.

### Virtual Nodes: Balancing and Heterogeneous Capacity
Using basic consistent hashing can lead to uneven distribution. If servers are hashed to random positions, they might cluster together, leaving huge gaps on the ring. The server following a large gap will receive a disproportionate share of the keys, creating a hot spot.

To fix this, we use virtual nodes, or vnodes. Instead of mapping a physical machine to a single point, we map it to multiple virtual points on the ring.
`vnode_position = hash(server_ip + "-vnode-" + index)`

If a server has 100 vnodes, it has 100 different positions spread across the ring. This averages out the gaps, leading to a much more balanced distribution of keys. Additionally, vnodes allow us to handle servers with different hardware capacities. A server with twice the RAM or CPU of another can be assigned twice as many vnodes, allowing it to take on twice the data load.

### Replication on the Hash Ring
In distributed databases, high availability requires replication. Consistent Hashing supports this naturally. To replicate a key with a replication factor of R, we first find the primary coordinator node by walking clockwise from the key's position. We then continue walking clockwise along the ring to select the next R - 1 distinct physical servers.

We must skip virtual nodes belonging to physical servers we have already selected for this key. This ensures replicas reside on different physical hardware, protecting against single points of failure.

---

### Worked Example 1: Resizing a Cluster (Hash Mod N vs. Consistent Hashing)
Let's analyze what happens when we grow a cluster from 4 nodes to 5 nodes. We have 10 keys with specific hash values: 12, 23, 34, 45, 56, 67, 78, 89, 90, 101.

#### Part A: Naive Hash Modulo N
With N = 4, keys map as follows:
- Key 12: 12 % 4 = Node 0
- Key 23: 23 % 4 = Node 3
- Key 34: 34 % 4 = Node 2
- Key 45: 45 % 4 = Node 1
- Key 56: 56 % 4 = Node 0
- Key 67: 67 % 4 = Node 3
- Key 78: 78 % 4 = Node 2
- Key 89: 89 % 4 = Node 1
- Key 90: 90 % 4 = Node 2
- Key 101: 101 % 4 = Node 1

Now we add a fifth node, N = 5:
- Key 12: 12 % 5 = Node 2 (Moved from 0)
- Key 23: 23 % 5 = Node 3 (No change)
- Key 34: 34 % 5 = Node 4 (Moved from 2)
- Key 45: 45 % 5 = Node 0 (Moved from 1)
- Key 56: 56 % 5 = Node 1 (Moved from 0)
- Key 67: 67 % 5 = Node 2 (Moved from 3)
- Key 78: 78 % 5 = Node 3 (Moved from 2)
- Key 89: 89 % 5 = Node 4 (Moved from 1)
- Key 90: 90 % 5 = Node 0 (Moved from 2)
- Key 101: 101 % 5 = Node 1 (No change)

Out of 10 keys, 8 had to move to new nodes. That is an 80% data movement rate.

#### Part B: Consistent Hashing
Let's use a simplified ring space of [0, 1000).
We place 4 physical nodes on the ring:
- Node A: hash value 100
- Node B: hash value 350
- Node C: hash value 600
- Node D: hash value 850

```
               [0 / 1000]
             /            \
     Node A [100]        Node D [850]
           |                |
     Node B [350]        Node C [600]
             \            /
                [500]
```

We place 7 keys on the ring:
- K1 (hash 50): mapped to Node A (first node clockwise)
- K2 (hash 150): mapped to Node B (first node clockwise)
- K3 (hash 300): mapped to Node B (first node clockwise)
- K4 (hash 400): mapped to Node C (first node clockwise)
- K5 (hash 550): mapped to Node C (first node clockwise)
- K6 (hash 700): mapped to Node D (first node clockwise)
- K7 (hash 900): mapped to Node A (first node clockwise, wraps around)

Now we add Node E with a hash of 500:
- Node E is positioned between Node B (350) and Node C (600).
- The only keys affected are those with hashes between 350 and 500.
- Let's re-evaluate each key:
  - K1 (50): Node A (No change)
  - K2 (150): Node B (No change)
  - K3 (300): Node B (No change)
  - K4 (400): Node E (Moved from Node C)
  - K5 (550): Node C (No change)
  - K6 (700): Node D (No change)
  - K7 (900): Node A (No change)

Only K4 moved. The other 6 keys remained on their assigned nodes. Data movement was limited to 1 out of 7 keys, roughly 14%.

---

### Worked Example 2: Virtual Nodes and Load Balance
Let's see how virtual nodes prevent load imbalance.
Suppose we have two physical servers, Node X and Node Y.
If Node X hashes to 100 and Node Y hashes to 900, the ring is split unevenly:
- Node X is responsible for range (900, 100], which is 20% of the ring.
- Node Y is responsible for range (100, 900], which is 80% of the ring.
Node Y will handle 4 times as much traffic as Node X, leading to overload.

To balance the system, we assign 3 virtual nodes to each server:
- Node X: X1 at 150, X2 at 450, X3 at 750
- Node Y: Y1 at 300, Y2 at 600, Y3 at 900

This interleaves the servers on the ring:
```
               [0 / 1000]
             /            \
        Y3 [900]         X1 [150]
          \               /
      X3 [750]          Y1 [300]
          \               /
        Y2 [600]         X2 [450]
             \            /
                [500]
```

Let's calculate the ranges:
- Range (900, 150] -> Maps to X1 (Server X). Size: 250.
- Range (150, 300] -> Maps to Y1 (Server Y). Size: 150.
- Range (300, 450] -> Maps to X2 (Server X). Size: 150.
- Range (450, 600] -> Maps to Y2 (Server Y). Size: 150.
- Range (600, 750] -> Maps to X3 (Server X). Size: 150.
- Range (750, 900] -> Maps to Y3 (Server Y). Size: 150.

Total space for Server X: 250 + 150 + 150 = 550 (55% of the ring).
Total space for Server Y: 150 + 150 + 150 = 450 (45% of the ring).

By adding just 3 vnodes per server, we reduced the capacity imbalance from an 80/20 split to a 55/45 split. In a production system with 100 to 200 vnodes per server, the distribution becomes extremely close to 50/50.

---

### Worked Example 3: Replication Factor 3 Placement
Let's track how data is replicated with a replication factor of 3 (RF = 3).
Our physical servers are A, B, C, and D.
Each server has 2 virtual nodes on our 1000 point ring:
- Physical A: A1 at 100, A2 at 500
- Physical B: B1 at 200, B2 at 600
- Physical C: C1 at 300, C2 at 700
- Physical D: D1 at 400, D2 at 800

The ring layout is:
`A1 (100) -> B1 (200) -> C1 (300) -> D1 (400) -> A2 (500) -> B2 (600) -> C2 (700) -> D2 (800)`

Assume we want to store a key with a hash value of 150.
We place the key on the ring and walk clockwise:
1. The first node we encounter is B1 (at 200).
   - This virtual node belongs to physical Server B.
   - Server B is the primary coordinator. Replica 1 is stored on Server B.
2. We continue walking clockwise to find the next physical server:
   - Next is C1 (at 300). This belongs to physical Server C.
   - Server C has not been used yet. Replica 2 is stored on Server C.
3. We continue walking clockwise:
   - Next is D1 (at 400). This belongs to physical Server D.
   - Server D has not been used yet. Replica 3 is stored on Server D.

Now let's store a key with a hash value of 350.
1. Walk clockwise to find the coordinator:
   - First node is D1 (at 400). Physical Server D gets Replica 1.
2. Continue walking clockwise:
   - Next is A2 (at 500). Physical Server A gets Replica 2.
3. Continue walking clockwise:
   - Next is B2 (at 600). Physical Server B gets Replica 3.

If we had encountered a vnode belonging to a physical server that was already selected, we would skip it and move to the next. For example, if we had a vnode A3 at 550, we would skip it when placing replicas because Server A was already chosen at 500.

## Pros
- **Minimal Data Movement on Resizing**: Adding or removing a node only requires moving a fraction of the total keys, preventing network storms and massive cache evictions.
- **Improved Load Balancing**: Virtual nodes distribute keys evenly across the available physical space, preventing individual servers from becoming hot spots.
- **Heterogeneous Capacity Support**: Nodes with superior hardware configurations can be allocated a larger number of virtual nodes, allowing them to handle a higher percentage of the overall traffic.
- **Easy Partitioning and Replication integration**: The circular structure simplifies replication workflows. You can easily find replica nodes by walking clockwise from the primary coordinator node.

## Cons
- **Increased Metadata Complexity**: Clients or routers must maintain a detailed map of all virtual node locations on the ring. This map must be kept in sync as servers join or leave.
- **Non-Uniform Distribution with Few Vnodes**: If the number of virtual nodes per physical server is too low, the keys will not be distributed evenly, leading to hot spots.
- **Cascading Rebalancing Load**: When a server fails, its keys are redistributed to its clockwise neighbors. If those neighbors are already running near capacity, this sudden influx of keys can cause them to fail as well, triggering a chain reaction across the cluster.
- **Split Brain Sensitivity**: If network partitions divide the cluster, different parts of the network might develop differing views of the ring topology, leading to conflicting key writes and read inconsistencies.

## Alternatives
- **Fixed Partitioning (Pre-sharding / Fixed Partitions)**: The hash space is divided into a fixed, large number of logical partitions, such as 1024 or 4096, which remains constant. Physical servers are assigned a subset of these partitions. When a server is added, entire partitions are moved from existing servers to the new server. This is the primary method used by systems like Redis Cluster and Elasticsearch.
- **Range-Based Partitioning**: Keys are ordered sequentially, and each server is assigned a continuous range of keys (e.g., A-E on Server 1, F-J on Server 2). This supports efficient range queries, but requires a dynamic coordination service to split and merge ranges as data grows, and can create massive write bottlenecks if keys are written sequentially (such as timestamped logs).
- **Directory-Based Partitioning / Lookup Service**: A centralized lookup service or database stores the exact mapping of every key or partition to its physical node. This allows for absolute flexibility in moving data, but introduces a single point of failure or a significant network hop bottleneck for every read and write operation.

## When to use it
- **Distributed Caching Clients**: When designing clients for distributed caches like Memcached or Redis, consistent hashing ensures that server restarts or resizing events do not invalidate the entire cache, keeping hit rates high.
- **Dynamo-style Distributed Databases**: For databases like Apache Cassandra or Amazon DynamoDB that require peer to peer, decentralized architectures with no single point of failure, consistent hashing provides a reliable way to distribute and replicate data across a highly dynamic set of nodes.
- **Load Balancers and API Gateways**: When routing requests to stateful backend servers or sticky sessions, consistent hashing maps user sessions to servers while minimizing disruption when backend servers scale up or down.

## When NOT to use it
- **Small, Static Clusters**: If your database cluster is small, rarely changes size, and scaling operations are scheduled and handled manually, the complexity of consistent hashing is unnecessary. Simple modulo hashing or manual sharding is much easier to implement and debug.
- **Strict Transactional and Range Query Workloads**: If your application relies on multi-key transactions or fast range scans across contiguous keys, consistent hashing is a poor fit. Hashing scatters sequential keys across random nodes on the ring, making range queries incredibly slow as they must fan out to every server in the cluster. Range based partitioning is much better suited for these use cases.

## Key takeaways / mental model
Think of consistent hashing as a circular racetrack where both servers and keys are runners. Keys always run clockwise to find the nearest server station. If a server station is removed, the keys that were headed there simply run a bit further clockwise to the next station. No other runner on the track is disrupted.

---

### Designing Data-Intensive Applications: The Partitioning Connection
Consistent hashing is a core pattern within the broader topic of database partitioning, which is covered in detail in `ddia/10 (partitioning)`. In Designing Data-Intensive Applications, Martin Kleppmann provides an important caveat regarding consistent hashing. He points out that the academic definition of consistent hashing, which involves randomly mapping keys and nodes to a ring to balance load, is rarely used in database systems. 

Instead, modern databases usually opt for a hybrid approach: they use a large, fixed number of partitions per node (often called token ranges or virtual nodes), and then explicitly move these pre-defined partitions when nodes join or leave. Pure consistent hashing is more commonly found in load balancers and caching client libraries rather than primary databases, which require stricter guarantees around transactional boundaries and metadata consistency.

## Self-check questions
1. Why does naive modulo N hashing cause almost all keys to move when N changes, and what is the exact proportion of keys that move?
2. How do virtual nodes solve both the problem of uneven key distribution and the issue of heterogeneous hardware capacity?
3. If a physical node fails in a consistent hashing cluster without virtual nodes, which node receives the failed node's entire write load, and why can this be dangerous?
4. In a replication factor of 3 system using consistent hashing with virtual nodes, what rules must be followed when choosing the second and third replica nodes to ensure fault tolerance?
5. Why are range queries extremely inefficient in a system that uses consistent hashing to partition its data?
6. What is Martin Kleppmann's caveat regarding consistent hashing, and how do systems like Cassandra adapt the academic model to handle actual database sharding?

## References
- *System Design Guide for Software Professionals* (Sinha & Chopra, Packt 2024), Chapters 3 and 5
- *Designing Data-Intensive Applications* (Martin Kleppmann, O'Reilly 2017), Chapter 6: Partitioning (referred to in this curriculum as `ddia/10`)
