---
id: ddia/08
subject: ddia
title: "Replication: Multi-Leader and Leaderless"
slug: replication-multi-leader-leaderless
status: drafted
mastery:
source: "Designing Data-Intensive Applications (Martin Kleppmann), Chapter 5"
prerequisites: [ddia/07]
created: 2026-06-30
updated: 2026-06-30
---

# Replication: Multi-Leader and Leaderless

## TL;DR
Multi-leader and leaderless replication models allow multiple database nodes to accept write requests directly. This design removes the single leader bottleneck but introduces complex synchronization challenges. It requires advanced conflict resolution strategies to ensure data consistency across replicas.

## The idea
What happens when a single database leader cannot keep up with write requests, or if a network cut blocks access to the only leader node? In [07-replication-single-leader.md](07-replication-single-leader.md), we saw how routing all writes through a single leader simplifies consistency. However, that leader becomes a single point of failure and a severe bottleneck for writes. 

To overcome these limits, we can use replication systems where multiple nodes accept write requests. Multi-leader systems assign a leader in each datacenter, while leaderless systems let any replica accept writes from clients. These approaches eliminate the single write bottleneck, but they force us to abandon the simple, conflict-free world of single-leader systems. They are built for extreme write scalability, high fault tolerance, and offline operations.

## How it works
This lesson covers two distinct architectures that allow multiple nodes to accept writes: multi-leader and leaderless replication.

### Part 1: Multi-Leader Replication
In a multi-leader configuration, you have more than one leader node, typically distributed across different geographical regions.

#### Key Use Cases
1. **Multi-datacenter deployment**: Each datacenter has its own leader. Local writes are fast because clients talk to the leader in their closest datacenter, and the leaders replicate changes to each other in the background.
2. **Clients with offline operation**: Applications like mobile calendars must accept writes even without an internet connection. Every device acts as a local leader that queues writes locally and syncs with other leaders once it reconnects.
3. **Real-time collaborative editing**: Tools like Google Docs let several users edit a document simultaneously. Every user edit is applied immediately to a local replica and streamed asynchronously to other users.

#### The Problem of Write Conflicts
Because writes happen concurrently on different leaders, conflicts are inevitable.

Imagine two users update the same inventory item at the same time:
1. User A changes the item name to "Blue Hat" on Leader 1.
2. User B changes the item name to "Red Hat" on Leader 2.
3. Leader 1 replicates the update to Leader 2.
4. Leader 2 replicates the update to Leader 1.
5. Without conflict resolution, Leader 1 would keep "Blue Hat" while Leader 2 would keep "Red Hat", causing permanent data divergence.

#### Conflict Resolution Strategies
Systems use several strategies to resolve these clashes:
- **Last-Write-Wins (LWW)**: Each write gets a timestamp, and the latest write wins. Although simple, this strategy carries a high risk of data loss due to clock skew, as even slightly inaccurate clocks can cause newer updates to be discarded in favor of older ones.
- **Application-defined resolution**: The database detects the conflict and lets custom code resolve it. This code can run during the write path to merge data automatically, or during the read path by prompting the user to choose.
- **Conflict-Free Replicated Data Types (CRDTs)**: Special data structures, like sets or registers, merge concurrent writes mathematically without needing a central coordinator. They guarantee all replicas arrive at the same state once they receive all updates.

---

### Part 2: Leaderless Replication (Dynamo-Style)
In leaderless systems, popularized by Amazon's Dynamo paper, the database has no leader. Clients write directly to several replicas in parallel, or send them to a coordinator node that handles this write fan-out.

#### Quorums and the Condition w + r > n
Consistency in leaderless systems depends on quorums.

If we have $n$ replicas, we can configure our writes to require confirmation from $w$ replicas, and our reads to query at least $r$ replicas.
As long as we satisfy the condition:
$$w + r > n$$
we are guaranteed that the set of replicas we read from will overlap with the set of replicas we wrote to by at least one node. This overlapping node ensures we read the most up-to-date value.

#### Example of a Quorum Setup
Consider a cluster with $n = 3$ replicas:
1. We configure a write quorum of $w = 2$.
2. A client writes a new value `v2` to the database. Replicas 1 and 2 accept the write, but Replica 3 is offline and misses it.
3. Later, the client wants to read the data. We configure a read quorum of $r = 2$.
4. The client queries Replica 2 and Replica 3.
5. Replica 2 returns the new value `v2`, while Replica 3 returns the stale value `v1`.
6. Comparing the timestamps, the client identifies `v2` as the latest write and returns it to the user.

#### Repairing Stale Replicas
When nodes miss writes, they must eventually catch up. Leaderless systems use two main processes to sync stale nodes:
- **Read repair**: When a client performs a read quorum and notices that one replica returned a stale value, it writes the newer value back to that replica. This updates the stale node on demand.
- **Anti-entropy process**: A background job constantly compares datasets between replicas to find missing data. It uses compact Merkle trees to compare data chunks efficiently without sending the entire database over the network.

#### Sloppy Quorums and Hinted Handoff
In a large cluster, a network partition might isolate a client from its designated $n$ replicas, preventing it from reaching $w$ nodes.

Instead of rejecting writes, the system can accept them on temporary nodes outside the primary $n$ replicas. This setup is a sloppy quorum.
Once the network partition heals, the temporary nodes deliver these writes to the primary replicas. This delivery process is called hinted handoff.

#### Limits of Quorums and Eventual Consistency
Even when we maintain $w + r > n$, eventual consistency remains the norm. Real-world edge cases can still return stale data:
- **Concurrent writes**: Clashes can occur when two updates happen at the exact same time, and LWW might discard one based on imprecise clocks.
- **Failed writes**: Replicas that accepted a write do not roll back their changes if the write fails to hit $w$ nodes, leaving partial state on some replicas.
- **Sloppy quorums**: Network partitions can delay hinted handoffs or lose data if the handoff node fails before transferring its updates, violating quorum guarantees.

## Pros
- **High write throughput**: Spreading write operations across multiple nodes avoids the bottlenecks of a single leader.
- **Geographic latency reduction**: Placing leaders or replicas closer to users speeds up local writes and reads.
- **Fault tolerance during network cuts**: Systems continue accepting writes even if datacenters or nodes are partitioned from each other.
- **Offline support**: Clients can modify their local databases offline and sync changes smoothly when they reconnect.

## Cons
- **Complex conflict resolution**: Merging concurrent writes requires delicate strategies like LWW, custom application logic, or CRDTs.
- **Clock skew vulnerability**: Strategies like LWW depend on synchronized clocks, which can lose data if clocks drift.
- **Stale reads**: Quorum configurations can still return old values due to replication lag or overlapping limitations.
- **Network bandwidth**: Background anti-entropy processes and write fan-outs consume significant network resources.

## Alternatives
- **Single-leader replication**: A single node handles all writes, eliminating conflict resolution entirely. This approach is preferable if your write volume can fit on one machine and write availability during a network cut is not critical.
- **Partitioning (Sharding)**: You split the dataset into smaller subsets and assign a leader to each subset. This pattern is preferable when you want single-leader simplicity but need to scale writes beyond a single machine's capacity.

## When to use it
Reach for multi-leader or leaderless replication when your application has extreme write volume, requires multi-datacenter low-latency writes, or must operate offline. It is ideal for collaborative tools, distributed key-value stores, and global telemetry platforms.

## When NOT to use it
Avoid these models if your application requires immediate, strict consistency or transactions across multiple rows. If write conflicts are unacceptable and you cannot tolerate stale reads, stick to single-leader systems or highly coordinated SQL databases instead.

## Key takeaways / mental model
Think of multi-leader replication like a multinational company with regional offices. Each office has its own manager who can approve local sales. Aligning the offices requires managers to constantly email each other to reconcile transactions, occasionally dealing with overlapping deals. Leaderless replication is like a decentralized task board where team members pick up tasks and report progress. To verify if a task is actually finished, you must ask a majority of the team to see if they agree on the status.

## Self-check questions
1. Why does Last-Write-Wins (LWW) conflict resolution carry a high risk of data loss?
2. If a database cluster has $n = 5$ replicas, what write quorum $w$ and read quorum $r$ are needed to guarantee we read the latest write?
3. What is the difference between read repair and the background anti-entropy process?
4. How does a sloppy quorum differ from a strict quorum, and when is it safe to use?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 5
