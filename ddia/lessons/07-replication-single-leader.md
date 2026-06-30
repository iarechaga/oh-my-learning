---
id: ddia/07
subject: ddia
title: "Replication: Single-Leader"
slug: replication-single-leader
status: drafted
mastery:
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

## How it works
The process of single-leader replication involves a steady flow of updates from the leader to the followers. Every write request from a client goes to the leader. After updating its local database, the leader writes the change to its replication log. The followers read this log and apply the updates in the exact order they were processed by the leader.

### Example: E-Commerce Catalog Update
Imagine an e-commerce platform with one leader node and two follower nodes, all storing a product inventory database.

1. A merchant updates a product price. They change the price of "Database Design Guide" from 40 USD to 45 USD.
2. This write request hits the leader. The leader updates its disk and writes a log entry: `UPDATE products SET price = 45 WHERE id = 101`.
3. Followers fetch the new log entry.
4. Follower 1 applies the update immediately.
5. Network latency delays Follower 2's update by two seconds.
6. Customer A queries Follower 1. They see the new price of 45 USD.
7. Customer B queries Follower 2 during the latency period. They still see the old price of 40 USD until the update finishes.

### Synchronous vs Asynchronous Replication
Deciding when a write is complete involves a major trade-off.

In synchronous replication, the leader waits for the followers to confirm they wrote the data before telling the client the write succeeded.
- **Synchronous advantage**: Followers are guaranteed to have up-to-date copies of the data. If the leader fails, we can trust the replica has not lost any updates.
- **Potential problem**: Writes stall if even one follower crashes or the network blocks.

In asynchronous replication, the leader writes to its own disk and immediately reports success to the client. It does not wait for a response from the followers.
- **Asynchronous advantage**: The leader can keep processing writes even if all followers are offline.
- **Potential problem**: Writes are permanently lost if the leader dies before those updates reach the followers.

Many systems use a semi-synchronous compromise. One follower replicates synchronously, while the others replicate asynchronously. This setup ensures at least one follower is always up-to-date without blocking writes if multiple backup nodes fail.

### Setting Up New Followers
We often need to add new replicas to scale reads or replace failed nodes. The process must happen without pausing writes:

1. Take a consistent snapshot of the leader's database without locking the entire system.
2. Copy this snapshot to the new follower node.
3. The follower connects to the leader and requests all data changes since the snapshot. A specific log position, like a Log Sequence Number, identifies this exact moment.
4. Once the follower applies these backlog changes, it is caught up. It can now process regular updates as they arrive.

### Handling Node Outages
Nodes can crash or lose power at any time.

- **Follower crash**: Each follower records its progress in a local transaction log. When it recovers, it knows exactly which transaction was the last one applied before the crash. It then requests any newer transactions from the leader.
- **Leader crash (Failover)**: This is much more complex. One of the followers must be promoted to the new leader. Clients need to reconfigure their writes to target this new node, and the remaining followers must start consuming updates from it.

### Failover Dangers
Automatic failover is fraught with peril:
- **Lost writes**: If we use asynchronous replication, the new leader might not have received all writes from the old leader before the crash. If the old leader comes back online and rejoins, what happens to those writes? Typically, they are discarded, which can break client expectations.
- **Split brain**: This occurs when two nodes both believe they are the active leader. Both accept writes, causing data to diverge rapidly. The system must shut down one of the nodes to prevent data corruption.
- **Timeout configuration**: Deciding when a leader is actually dead is difficult. If the timeout is too short, temporary network glitches will trigger unnecessary failovers, degrading performance. If the timeout is too long, the system remains unavailable for writes during a real crash.

### Replication Log Implementations
Leaders use different methods to represent the stream of changes:

1. **Statement-based replication**: The leader logs every write request statement, like SQL queries, and sends them to followers.
   - *Limitation*: Any non-deterministic function like `NOW()` or `RAND()` will produce different data on followers.
2. **Write-Ahead Log (WAL) shipping**: The database logs low-level disk modifications.
   - *Format issues*: This log is tightly coupled to the storage engine. Upgrading the database version on followers becomes extremely difficult if the log format changes.
3. **Logical (row-based) log replication**: The log contains a sequence of record-level writes. For an insert, it contains the new column values. For a delete, it contains the unique identifier.
   - *System decoupled*: This decouples the replication log from the internal storage engine, allowing different database versions to replicate easily.
4. **Trigger-based replication**: Custom application code registers triggers that log changes to a separate table.
   - *Custom logic*: This approach is highly flexible, letting you filter data or replicate only a subset of tables.
   - *Performance cost*: It carries a much higher performance overhead than native replication.

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

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 5
