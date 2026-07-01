---
id: ddia/07
subject: ddia
title: "Replication: Single-Leader"
slug: replication-single-leader
status: drafted
mastery:
seniority: mid
source: "Designing Data-Intensive Applications (Martin Kleppmann), Chapter 5"
prerequisites: [ddia/01]
created: 2026-06-30
updated: 2026-06-30
---

# Replication: Single-Leader

## TL;DR
Replication copies the same data to multiple machines so the system stays up even if some hardware fails. In a single-leader system, all writes go to one main node, which broadcasts updates to other nodes. These backup nodes can handle read queries, helping the system scale its read volume.

## The idea
Why do we copy data across multiple physical servers? If you keep everything on a single disk, any hardware failure can take your entire service offline. Spreading copies of your datasets across different machines improves availability, reduces network latency by placing data closer to users, and scales read capacity. Before studying these mechanics, it is useful to review the core tenets of reliability, scalability, and maintainability in [01-reliability-scalability-maintainability.md](01-reliability-scalability-maintainability.md).

Single-leader replication, sometimes called master-slave or active-passive, offers a structured path to achieve these goals. It solves the coordination problem by appointing one node as the leader. Instead of letting any node accept changes, which would lead to immediate conflicts, we route all data modifications through this single source of truth. The other nodes simply follow along, applying the changes to their own local state. This design ensures that all replicas eventually look the same, while providing a clear and simple mechanism for handling writes.

In high-throughput systems, scaling reads by simply adding more followers is incredibly popular. However, this pattern introduces lag: since updates travel from the leader to followers over networks, different replicas might show slightly different states of the database at the same time. If a user writes to the leader and then reads from a lagged follower, they might see their own update disappear. This forces us to think carefully about replication lag and consistency guarantees. We want to balance performance with durability and consistency. If we optimize purely for write speeds, we end up with asynchronous replication and lag-related anomalies. If we optimize for perfect consistency, we run synchronous replication and suffer massive latency penalties. Single-leader replication acts as the classic architectural sandbox where these trade-offs are negotiated.

## How it works
The process of single-leader replication involves a steady flow of updates from the leader to the followers. Every write request from a client goes to the leader. After updating its local database, the leader writes the change to its replication log. The followers read this log and apply the updates in the exact order they were processed by the leader.

### Core Replication Mechanics
In a single-leader database, we distinguish between two types of nodes:
- **Leader**: The leader, also known as the master or primary node, is the only node that can accept write requests from clients. Whenever a client wants to write data, the request must go to the leader. The leader writes the new data to its local storage.
- **Followers**: The followers, also known as replicas, slaves, secondaries, or hot standbys, are read-only nodes. They do not accept direct write requests. Instead, they consume the leader's stream of changes, applying them in the exact order the leader applied them.

Clients can read from either the leader or any follower. Writes, however, must always go to the leader.

### Synchronous vs Asynchronous Replication
Deciding when a write is complete involves a major trade-off.

In synchronous replication, the leader waits for the followers to confirm they wrote the data before telling the client the write succeeded.
- **Synchronous advantage**: Followers are guaranteed to have up-to-date copies of the data. If the leader fails, we can trust the replica has not lost any updates.
- **Potential problem**: Writes stall if even one follower crashes or the network blocks.

In asynchronous replication, the leader writes to its own disk and immediately reports success to the client. It does not wait for a response from the followers.
- **Asynchronous advantage**: The leader can keep processing writes even if all followers are offline.
- **Potential problem**: Writes are permanently lost if the leader dies before those updates reach the followers.

Many systems use a semi-synchronous compromise. One follower replicates synchronously, while the others replicate asynchronously. If the synchronous follower becomes slow or disconnected, the leader can temporarily promote another asynchronous follower to be synchronous, keeping the write path open. This setup ensures at least one follower is always up-to-date without blocking writes if multiple backup nodes fail.

Here is an ASCII timing diagram showing the difference:

```
[Synchronous Replication]
Client             Leader          Follower (Sync)
  |                  |                   |
  |-- 1. Write ----->|                   |
  |                  |-- 2. Log update ->|
  |                  |                   | [Process update]
  |                  |<- 3. Ack ---------|
  |<- 4. Success ----|                   |
  |                  |                   |

[Asynchronous Replication]
Client             Leader          Follower (Async)
  |                  |                   |
  |-- 1. Write ----->|                   |
  |                  | [Log locally]     |
  |<- 2. Success ----|                   |
  |                  |-- 3. Log update ->|
  |                  |                   | [Process update]
  |                  |<- 4. Ack ---------|
```

### The Durability-vs-Latency Trade-off
Choosing between synchronous and asynchronous replication is a fundamental choice. If you choose synchronous, you guarantee that if the leader crashes, the data is safe on at least one follower. However, your write latency now includes the network round-trip time to the follower and the time it takes for that follower to write the data to disk.

If you choose asynchronous, your write latency remains very low because the leader responds immediately. However, if the leader experiences a catastrophic hardware failure before the log entries are transmitted, those writes are lost forever.

### Setting Up New Followers
We often need to add new replicas to scale reads or replace failed nodes. The process must happen without pausing writes:

1. **Consistent Snapshot**: Take a consistent snapshot of the leader's database without locking the entire system. Modern databases accomplish this by exploiting Multi-Version Concurrency Control (MVCC) or taking a physical copy of the data files combined with a point-in-time replication log position.
2. **Copy Snapshot**: Copy this snapshot to the new follower node.
3. **Log Synchronization**: The follower connects to the leader and requests all data changes since the snapshot. A specific log position, like a Log Sequence Number (LSN) in PostgreSQL or binlog coordinates in MySQL, identifies this exact moment.
4. **Catch-up**: Once the follower applies these backlog changes, it is caught up. It can now process regular updates as they arrive.

### Handling Node Outages
Nodes can crash or lose power at any time.

- **Follower crash**: Each follower records its progress in a local transaction log. When it recovers, it knows exactly which transaction was the last one applied before the crash. It then requests any newer transactions from the leader.
- **Leader crash (Failover)**: This is much more complex. One of the followers must be promoted to the new leader. Clients need to reconfigure their writes to target this new node, and the remaining followers must start consuming updates from it.

### Failover Steps in Detail
An automatic failover process typically involves three phases:
1. **Detection**: The remaining nodes monitor each other via periodic heartbeats. If the leader fails to respond for a designated timeout (e.g., 30 seconds), it is declared dead.
2. **Election**: A new leader is chosen. This is done through a consensus algorithm among the remaining nodes, or a separate controller node appoints the follower with the most up-to-date replication log.
3. **Reconfiguration**: The system is updated so that clients send writes to the new leader. Followers are instructed to pull their replication log streams from the new leader. If the old leader comes back online, it must recognize the new leader and demote itself to a follower.

### Failover Dangers
Automatic failover is fraught with peril:
- **Lost writes**: If we use asynchronous replication, the new leader might not have received all writes from the old leader before the crash. If the old leader comes back online and rejoins, what happens to those writes? Typically, they are discarded, which can break client expectations. This can be devastating if other parts of your infrastructure (like an external cache) depend on those writes having occurred.
- **Split brain**: This occurs when two nodes both believe they are the active leader. Both accept writes, causing data to diverge rapidly. The system must shut down one of the nodes to prevent data corruption. To solve this, some clusters employ fencing mechanisms. An extreme form of fencing is STONITH, which stands for "Shoot The Other Node In The Head." This involves using a power management switch to physically power down or reboot the old leader node, ensuring it can no longer accept writes.
- **Timeout configuration**: Deciding when a leader is actually dead is difficult. If the timeout is too short, temporary network glitches or CPU spikes will trigger unnecessary failovers, degrading performance and causing unnecessary elections. If the timeout is too long, the system remains unavailable for writes during a real crash, increasing the recovery time objective.
- **Cascading failures**: When a leader dies, the remaining nodes must elect a new leader and handle the replication traffic. If the database was already running near maximum capacity, the extra overhead of failover, re-routing traffic, and catching up replicas can overwhelm the newly promoted leader. This can cause the new leader to crash as well, triggering another failover, and eventually bringing down the entire cluster.

### Client Routing and Discovery
When a failover occurs, clients must discover the new leader. There are several ways to solve this routing problem:
- **DNS updates**: The system updates a DNS record to point to the new leader's IP address. However, DNS caching and replication delays across the internet can cause clients to send writes to the old leader for minutes. Clients and routers often ignore DNS TTLs (Time to Live), keeping the stale IP cached in memory.
- **Virtual IP routing**: The cluster uses a shared virtual IP address (VIP) that is dynamically assigned to the active leader's network card. If the leader fails, a tool like Keepalived or Heartbeat moves the IP to the new leader using ARP spoofing. This is extremely fast but is limited to a single local area network (LAN) segment, meaning it cannot span across geographically distant datacenters.
- **Routing tiers**: Clients connect to a proxy layer (like ProxySQL or HAProxy) that queries a consensus coordinator (like ZooKeeper, Consul, or etcd) to discover the active leader and route writes accordingly. This is the most resilient approach because the routing tier receives instantaneous configuration updates. However, it adds network hops, increases latency, and requires managing a complex consensus cluster.

### Replication Log Implementations
Leaders use different methods to represent the stream of changes:

1. **Statement-based replication**: The leader logs every write request statement, like SQL queries, and sends them to followers.
   - *Limitation*: Any non-deterministic function like `NOW()` or `RAND()` will produce different data on followers. For example, `INSERT INTO events (id, created_at) VALUES (UUID(), NOW())` will generate a different primary key and timestamp on every replica. Autoincrementing columns or triggers can also execute out of order. This can cause the databases on different replicas to diverge silently.
2. **Write-Ahead Log (WAL) shipping**: The database logs low-level disk modifications. For example, PostgreSQL and Oracle ship raw WAL files containing exact byte offsets on disk pages. For LSM-trees, this is the commit log. For B-trees, this is the redo log.
   - *Format issues*: This log is tightly coupled to the storage engine. Upgrading the database version on followers becomes extremely difficult if the log format changes, forcing teams to perform a full system shutdown to upgrade the database. If you try to run different versions on leader and followers, replication will likely break due to raw byte mismatch.
3. **Logical (row-based) log replication**: The log contains a sequence of record-level writes. For an insert, it contains the new column values. For a delete, it contains the unique identifier.
   - *System decoupled*: This decouples the replication log from the internal storage engine, allowing different database versions to replicate easily. It is also excellent for Change Data Capture (CDC) systems that stream changes from a transactional database into an external search index like Elasticsearch or a cache like Redis. It allows us to perform zero-downtime rolling upgrades because we can run a newer database version on a follower while the leader runs an older version.
4. **Trigger-based replication**: Custom application code registers triggers that log changes to a separate table.
   - *Custom logic*: This approach is highly flexible, letting you filter data or replicate only a subset of tables. For example, systems like Bucardo for PostgreSQL or GoldenGate for Oracle write updates to shadow tables, which are read by external coordinator processes.
   - *Performance cost*: It carries a much higher performance overhead than native replication, as every insert, update, or delete triggers additional SQL operations and disk writes. However, it remains the ultimate fallback when you must replicate data across completely different database vendors.

### Replication Lag and Consistency Anomalies
When reading from followers to scale read-heavy workloads, we must deal with replication lag. This lag can cause various anomalies that affect the user experience:
- **Read-Your-Own-Writes Consistency**: If a user submits a write to the leader and then immediately views their profile, the query might hit a lagged follower. To the user, it looks like their update was lost. To prevent this, the database or application can route queries for a user's own data to the leader, while routing other users' data to followers.
- **Monotonic Reads**: If a user refreshes a page multiple times, their queries might hit different followers. If follower A is up to date but follower B is lagging, the user will see a newer state on their first load and an older state on their second load, making it seem like time has run backward. We can guarantee monotonic reads by ensuring that a given user always reads from the same replica (e.g., by hashing their user ID to a specific replica).
- **Consistent Prefix Reads**: This anomaly occurs when writes are ordered causally but replicated out of order due to network paths. For instance, if a question is asked and then answered, a reader might see the answer before the question. To prevent this, causally related writes must always be written to the same database partition, which preserves their global ordering.

---

### Worked Examples

#### Worked Example 1: Latency and Replication Lag
Suppose an e-commerce platform has one leader node in North America and two follower nodes in Europe. Let's trace how a product price update flows through the system and how it affects customers due to replication lag.

```
Time (ms)  Event Description
-----------------------------------------------------------------------------------
T=0        Merchant sends a write request to change the price of "Database Guide"
           from 40 USD to 45 USD. The request lands on the Leader.
T=5        The Leader writes the change to its local storage and updates its WAL.
T=10       The Leader returns a success response to the merchant.
T=11       The Leader sends a replication log packet to Follower 1 (Europe) over
           the WAN.
T=125      Customer A, located in London, sends a read query to Follower 1.
           At this millisecond, the replication packet has not arrived. Customer A
           sees the old price of 40 USD.
T=150      The replication packet finally arrives at Follower 1. The follower
           applies the update to its database.
T=155      Customer B, also in London, queries Follower 1 and sees the updated
           price of 45 USD.
```

In this scenario, Customer A experienced a stale read due to a 150ms replication lag over the WAN. If the user interface allows a user to update their own profile, a 150ms lag will cause immediate confusion if they refresh and see old data. This demonstrates why we need read-your-own-writes consistency.

#### Worked Example 2: Semi-Synchronous Replication Latency and Failure
Let's analyze the mathematical impact on latency and reliability in a semi-synchronous cluster.
Suppose we have a leader node and two followers (Follower A and Follower B). Follower A is synchronous, while Follower B is asynchronous.

We define:
- $L_{local}$: The time the leader takes to write a transaction to its local disk = 2ms.
- $RTT_A$: Network round-trip time between leader and Follower A = 10ms.
- $RTT_B$: Network round-trip time between leader and Follower B = 80ms.
- $Disk_A$: Follower A's disk write latency = 3ms.

If a client sends a write request:
1. The leader writes locally ($L_{local} = 2$ms).
2. The leader sends the replication packet to Follower A and Follower B in parallel.
3. The leader blocks, waiting only for Follower A because it is synchronous.
4. Follower A receives the packet, writes to disk ($Disk_A = 3$ms), and sends an ACK.
5. The total time before the leader can respond to the client is:
   $$\text{Write Latency} = L_{local} + RTT_A + Disk_A = 2 + 10 + 3 = 15\text{ms}$$
6. Even though Follower B takes much longer due to $RTT_B = 80$ms, the client does not wait for it.

What happens if Follower A crashes?
The leader will wait for Follower A's ACK. If no ACK arrives within a configured timeout (e.g., 500ms), the leader marks Follower A as inactive. The system then demotes Follower A to asynchronous and promotes Follower B to synchronous.
During that 500ms timeout period, all client writes are blocked, showing how synchronous replication prioritizes consistency over availability. Once Follower B is promoted, subsequent write latency increases to:
$$\text{Write Latency} = L_{local} + RTT_B + Disk_B = 2 + 80 + 3 = 85\text{ms}$$
This showcases the trade-off of routing traffic across slower paths to maintain durability.

#### Worked Example 3: Automatic Failover and the GitHub Autoincrement Incident
Let's examine how automatic failover can go wrong when an out-of-date replica is promoted. This is modeled after a real-world incident at GitHub where MySQL and Redis went out of sync.

Imagine a system where MySQL uses single-leader replication. An external cache, Redis, is used to generate unique primary keys using an incrementing counter.

```
MySQL Leader (Node 1)    MySQL Follower (Node 2)      Redis Counter
[Max ID = 5000]          [Max ID = 4998 (Lagged)]     [Counter = 5000]
```

1. The network splits. MySQL Node 1 is cut off from Node 2 and from the automatic failover controller.
2. The controller notices Node 1 is unreachable. It declares Node 1 dead and promotes Node 2 to be the new leader.
3. Meanwhile, a client wants to insert a new row. It requests a new ID from Redis. Redis returns 5001.
4. The client sends an insert to the new MySQL leader (Node 2) with ID 5001. Node 2 accepts it because its local maximum ID was only 4998.
5. The network partition heals. The old leader (Node 1) rejoins the cluster. It has a write with ID 4999 and ID 5000 that never reached Node 2.
6. When Node 1 attempts to reconcile its log with the new leader (Node 2), a primary key conflict occurs because both nodes have divergent logs for those high ID values.
7. To resolve the conflict, Node 1's un-replicated writes (IDs 4999 and 5000) are discarded.
8. Because those records were discarded, client requests that expected to find data for IDs 4999 and 5000 now see different, unrelated rows inserted by clients on Node 2. This can result in users seeing private data belonging to other accounts.

---

## Pros
- **High availability**: The system can survive node crashes. If the leader fails, a follower can be promoted to keep writes functioning.
- **Reduced read latency**: Keeping copies of data geographically closer to users accelerates query times.
- **Scalable read capacity**: Multiple followers can serve read-only requests, offloading pressure from the leader.
- **Simple write model**: Routing all updates through a single leader eliminates write conflicts, making coordination straightforward.

## Cons
- **Single point of failure for writes**: If the leader is down and failover is not set up, writes are entirely blocked.
- **Complex failover mechanics**: Detecting dead leaders, preventing split brain, and handling discarded writes are notoriously difficult to implement correctly.
- **Inconsistent reads**: Followers lag behind the leader, meaning users can read stale data or see conflicting states.
- **Network overhead**: Continually streaming logs consumes significant bandwidth, which can limit throughput.

## Alternatives
- **Multi-leader replication**: Multiple nodes can accept writes, replicating changes to each other. This model is preferable for multi-datacenter setups or offline-first clients where a single leader would become a severe write bottleneck.
- **Leaderless replication**: Every replica can accept writes and reads. Clients send updates directly to multiple nodes in parallel. This approach is preferable when you need high write tolerance and are willing to handle conflict resolution on the read path.

## When to use it
Single-leader replication is ideal for applications where reads far outnumber writes, and where a clean, conflict-free writing model is crucial. It is the default choice for standard relational databases like PostgreSQL or MySQL when they need to scale read volume or increase read resilience.

## When NOT to use it
Avoid single-leader replication if your write volume is too high for a single machine to handle, or if your system needs to accept writes even during network partitions. In those situations, reach for leaderless databases or multi-leader setups instead. You should also avoid it if you require absolute, real-time read consistency across all nodes without tolerating any lag.

## Key takeaways / mental model
Think of single-leader replication like a newsroom with one editor and several printing presses. All fresh articles must be approved and logged by the editor before they are printed. The printing presses can distribute copies of the newspaper to millions of readers simultaneously, but they cannot write new articles on their own. If the editor falls ill, the team must elect a new editor from the printing press operators to keep the paper running.

## Self-check questions
1. How does a semi-synchronous replication setup balance write latency with data durability?
2. What is a split-brain scenario in a single-leader system, and why is it dangerous?
3. Why does write-ahead log shipping make database upgrades on followers more difficult than logical row-based logging?
4. What steps must a system take to bring a new follower online without interrupting active write operations?
5. In Worked Example 2, if the leader fails before Follower B acknowledges the lagged write, how does that affect durability in an asynchronous replication model?
6. What is the fundamental cause of the data-exposure risk during the MySQL and Redis autoincrement failover incident described in Worked Example 3?
7. How does a routing proxy tier combined with a configuration service like Consul solve the client discovery problem during database failover?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 5
