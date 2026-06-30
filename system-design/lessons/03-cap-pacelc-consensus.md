---
id: system-design/03
subject: system-design
title: "CAP, PACELC, and Consensus in Practice"
slug: cap-pacelc-consensus
status: drafted
mastery:
source: "System Design Guide for Software Professionals (Sinha & Chopra), Chapter 3"
prerequisites: [ddia/09, ddia/13]
created: 2026-06-30
updated: 2026-06-30
---

# CAP, PACELC, and Consensus in Practice

## TL;DR
Distributed databases must handle network splits by prioritizing either absolute data consistency or overall system availability. The PACELC theorem expands this framework by addressing the trade-off between read/write latency and data consistency during normal, partition-free operations. Practical systems manage these trade-offs using consensus engines like Raft or Paxos to safely coordinate leaders, quorums, and configuration changes.

## The idea
When we build distributed systems, we spread data and processing across multiple physical machines. This distribution allows us to handle massive traffic and survive hardware failures, but it introduces a major challenge: physical machines must communicate over a network. Networks are unreliable, meaning they occasionally drop packets, experience severe congestion, or split entirely. We cannot have a database that is perfectly consistent, always available, and lightning fast under all conditions.

When a network partition occurs, some nodes cannot talk to others. We must decide whether to stop serving requests to keep data identical, or keep serving requests and let nodes diverge. During normal times, we still face a trade-off. We must choose whether to wait for data to replicate to all nodes to ensure consistency, or respond immediately to the client to minimize latency. Consensus protocols provide the actual algorithmic machinery to safely enforce these choices.

## How it works
To understand these trade-offs, we must analyze the theoretical frameworks and the practical tools that implement them. This section breaks down the CAP theorem, the PACELC theorem, and consensus mechanisms.

### The CAP Theorem
The CAP theorem, formulated by Eric Brewer, describes distributed systems under network partitions. It states that a distributed data store can simultaneously provide at most two of the following three guarantees:

1. **Consistency (C):** Every read receives the most recent write or an error. This is equivalent to linearizability, where the system behaves as if there is only a single copy of the data.
2. **Availability (A):** Every non-failing node returns a non-error response to every request, without a guarantee that it contains the most recent write. This means the system cannot return an error or time out if the node is running.
3. **Partition Tolerance (P):** The system continues to operate despite an arbitrary number of dropped or delayed messages by the network.

Since physical networks cannot guarantee perfect delivery, we must assume partitions will happen. Therefore, partition tolerance is non-negotiable. The actual choice is between Consistency and Availability during a partition:

```
               +-----------------------------------+
               |         Network Partition         |
               +-----------------------------------+
                                 |
                +----------------+----------------+
                |                                 |
         [ CP System ]                     [ AP System ]
      Prefer Consistency               Prefer Availability
  - Refuse reads/writes on         - Accept reads/writes on
    isolated nodes to avoid          any node, leading to
    stale or divergent data.         divergent data.
  - ZooKeeper, HBase.              - Cassandra, DynamoDB.
```

- **CP Systems:** If a partition occurs, the system shuts down or blocks requests on partitioned nodes to prevent stale reads or conflicting writes. HBase and ZooKeeper choose this path.
- **AP Systems:** The system keeps accepting writes and serving reads on any reachable node. Nodes on different sides of the partition will diverge, and clients may read stale data. Cassandra and Dynamo choose this path.

#### The CAP Formal Proof Intuition
Let us walk through the simple, mathematical proof intuition formulated by Seth Gilbert and Nancy Lynch. Imagine a cluster of two nodes, Node 1 and Node 2, that hold a single variable `v` whose initial value is 0.

```
       [ Client A ]                     [ Client B ]
            |                                |
       Write v = 1                        Read v
            v                                v
        [ Node 1 ]      X (Partition)    [ Node 2 ]
```

Suppose a network partition occurs, completely separating Node 1 and Node 2. A client connects to Node 1 and writes `v = 1`. If Node 1 accepts the write, it becomes available for writes. However, Node 1 cannot propagate this write to Node 2 due to the partition.

Subsequently, a different client connects to Node 2 and requests the value of `v`. To remain consistent (linearizable), Node 2 must return the value 1. Since it cannot communicate with Node 1 to learn about the write, its only choices are to return the stale value 0 (violating consistency) or refuse to respond with a valid value by returning an error or timing out (violating availability). Thus, no system can achieve both guarantees in the presence of a network partition.

### The PACELC Theorem
The CAP theorem only covers system behavior when a partition actually occurs. Daniel Abadi formulated the PACELC theorem to describe the trade-offs during normal operation. It reads:

**If there is a Partition (P), how does the system choose between Availability (A) and Consistency (C)? Else (E), how does the system choose between Latency (L) and Consistency (C)?**

This creates four distinct system classifications:

- **PC/EC (e.g., HBase, ZooKeeper):** During a partition, they choose Consistency. In normal operation, they choose Consistency, preferring to wait for replication to complete even if it increases read/write latency.
- **PC/EL (e.g., MongoDB by default):** During a partition, they choose Consistency. In normal operation, they prioritize low Latency, allowing reads from local secondaries which might contain stale data.
- **PA/EL (e.g., Cassandra, DynamoDB):** During a partition, they remain Available. In normal operation, they prioritize low Latency by replicating asynchronously. This introduces replication lag, which is discussed as a core trade-off in ddia/09 (replication lag and consistency).
- **PA/EC:** During a partition, they remain Available. In normal operation, they choose Consistency, forcing synchronous replication. This classification is rare because a system willing to sacrifice availability during partitions usually does not mind sacrificing latency during normal times.

#### The Latency/Consistency Trade-off under Normal Conditions
Under normal, partition-free operations, databases must replicate writes to other nodes. This replication can be either synchronous or asynchronous.

```
  Client             Primary Node             Replica Node
    |                      |                       |
    |--- Write Request --->|                       |
    |                      |--- Replicate Write -->|
    |                      |<-- Acknowledge Write -|
    |<-- Success (200) ----|                       | (Synchronous - EC)
    v                      v                       v
```

```
  Client             Primary Node             Replica Node
    |                      |                       |
    |--- Write Request --->|                       |
    |<-- Success (200) ----|                       | (Asynchronous - EL)
    |                      |--- Replicate Write -->|
    |                      |<-- Acknowledge Write -|
    v                      v                       v
```

If we choose Consistency (EC), we must write synchronously. The primary node waits for a majority of replicas to write the data and acknowledge it before returning success to the client. This guarantees that any subsequent read will find the updated value, but it adds the network round-trip time between nodes to our write latency.

If we choose Latency (EL), we write asynchronously. The primary node returns success to the client immediately after writing to its local disk. It replicates the write to other nodes in the background. While this makes writes extremely fast, it introduces replication lag. During this lag window, if a read request hits a replica node before the background replication finishes, the client receives stale data.

### Consensus and Leader Election in Practice
To enforce consistency, distributed databases must agree on a single sequence of inputs and state changes. This is the consensus problem, which is analyzed in ddia/13 (consistency and consensus). It is practically implemented using consensus algorithms like Raft and Paxos.

These protocols use the concept of State Machine Replication. Every node runs an identical state machine and executes the same log of commands in the same order. To achieve this, nodes elect a single leader. The leader receives client writes, appends them to its log, and replicates them to other nodes (followers).

A key mechanism in consensus is the **Quorum**. To commit a write or elect a leader, a node must gather votes from a majority of the cluster. For a cluster of size `N`, a quorum requires at least `ceil((N + 1) / 2)` nodes. If a cluster has 5 nodes, any quorum requires at least 3 nodes. This ensures that even if the network partitions, at most one partition can contain a majority, preventing split-brain scenarios where two nodes believe they are both the active leader.

```
       [Follower] <--- log replicate --- [ Leader ] ---> log replicate ---> [Follower]
           |                                 |                                 |
     Executes log                      Manages log                       Executes log
```

#### Raft Consensus Algorithm Mechanics
The Raft protocol simplifies consensus by dividing it into clear, independent sub-problems. It organizes time into consecutive Term numbers, which act as logical clocks.

A Raft node exists in one of three states: Follower, Candidate, or Leader. Under normal operations, there is exactly one leader, and all other nodes are followers. Followers are passive: they issue no requests on their own but respond to incoming messages.

```
     [ Follower ] --(timeout, starts election)--> [ Candidate ]
          ^                                            |
          |--(discovers leader or higher term)---------|
          |                                            |
          |                                     (gets majority votes)
          |                                            v
          |<---------(steps down)----------------- [ Leader ]
```

When followers stop receiving heartbeats from the leader within a randomized election timeout (typically between 150ms and 300ms), they assume the leader has failed. The follower then transitions to the Candidate state, increments its term number, votes for itself, and sends RequestVote messages to all other nodes. If the candidate receives votes from a majority of nodes in the cluster, it becomes the new leader. Randomized timeouts prevent split-vote scenarios where multiple followers try to elect themselves simultaneously.

Once elected, the leader manages log replication. It receives client write commands, appends them to its local log, and broadcasts them via AppendEntries messages. After a majority of followers acknowledge writing the entry to their logs, the leader commits the write, applies it to its local state machine, and returns success to the client.

#### Cluster Membership and Configuration Changes
Consensus groups are not static. Servers fail permanently and require replacement, or we must scale out the cluster by adding new nodes. Changing cluster membership safely is difficult because we cannot transition all nodes from the old configuration to the new configuration at the exact same instant.

During the transition, the cluster can split into two overlapping majorities, leading to a split-brain condition where two independent leaders are elected. To prevent this, Raft uses a two-phase joint consensus approach. The leader replicates a special configuration entry that requires majorities from both the old and new configurations before committing the transition, ensuring the cluster never splits.

#### Coordination Services
Instead of implementing Raft or Paxos inside every application, developers use coordination services like ZooKeeper or etcd. These services use consensus internally to provide highly reliable, strongly consistent operations. Applications use them for:

- **Leader Election:** Active servers try to create a lock or node. The coordinator guarantees only one server succeeds.
- **Leases and Heartbeats:** The leader must periodically renew a lease. If the leader fails to heartbeat, the coordinator expires the lease and triggers a new election.
- **Ephemeral Nodes:** ZooKeeper allows nodes to exist only as long as the client session is active. If the client dies, the ephemeral node disappears, alerting other nodes via a watch mechanism.

---

### Worked Examples

#### Example 1: Classifying Real-World Systems on CAP and PACELC
Let's analyze how HBase, Cassandra, and MongoDB fit these frameworks based on their internal write paths.

| System | CAP Classification | PACELC Classification | Core Mechanism |
| :--- | :--- | :--- | :--- |
| **HBase** | CP | PC/EC | Writes go to a single RegionServer. If it fails, the region is offline until recovered, ensuring strong consistency at the expense of write latency and temporary availability. |
| **Cassandra** | AP | PA/EL | Tunable consistency allows writes to return after hitting a single replica (write quorum = 1). Hinted handoffs and read repair handle divergence later, prioritizing latency and availability. |
| **MongoDB** | CP | PC/EC (Default) | Uses a single primary for all writes. If a partition isolates the primary, it steps down. You can alter this to PC/EL by allowing reads from secondaries. |

In HBase, data is divided into regions served by a single RegionServer. Because every read and write for a key must go through this single active RegionServer, HBase achieves strong consistency (EC) during normal operations. When a RegionServer fails or gets partitioned, those regions become completely unavailable until the master detects the failure and reassigns them (PC).

Cassandra is designed for maximum availability and low latency. Writes can be accepted by any replica, and the system coordinates replication in the background. If you read with a consistency level of ONE, Cassandra returns data from the nearest replica immediately, prioritizing low latency (EL) and high availability (PA).

MongoDB uses a single-leader replica set architecture. The primary node processes all writes by default, ensuring consistency (EC). During a partition, if the primary cannot reach a majority of the replica set, it steps down to a secondary role, and the system temporarily rejects writes (PC) until the remaining nodes elect a new primary.

#### Example 2: Leader Election via ZooKeeper Ephemeral Nodes
Imagine three worker nodes (Node A, Node B, and Node C) attempting to coordinate an active/passive cluster where only one node can process jobs. They use ZooKeeper to elect a leader.

```
           +---------------------------+
           |     ZooKeeper Cluster     |
           +---------------------------+
             /           |           \
     Creates           Creates        Creates
  /election/n_1     /election/n_2   /election/n_3
     (Leader)          (Watch)        (Watch)
       /                 |               \
   [Node A]          [Node B]          [Node C]
```

1. **Initialization:** All nodes connect to ZooKeeper and create ephemeral sequential nodes under `/election/n_`.
   - Node A creates `/election/n_1`
   - Node B creates `/election/n_2`
   - Node C creates `/election/n_3`
2. **Election Rule:** The node with the lowest sequence number is the leader. Node A detects that `/election/n_1` is the lowest, so it assumes the leader role.
3. **Setting Watches:** Follower nodes must watch for failures. Rather than watching all nodes, each node watches the next-lowest sequence number to prevent a thundering herd problem:
   - Node B watches `/election/n_1`
   - Node C watches `/election/n_2`
4. **Failure Detection:** Node A crashes, and its TCP connection to ZooKeeper terminates. ZooKeeper detects the session loss after the session timeout (e.g., 5 seconds) and deletes `/election/n_1`.
5. **Watch Trigger:** The deletion of `/election/n_1` triggers the watch on Node B. Node B queries `/election` and sees its node `/election/n_2` is now the lowest. Node B immediately takes over as the leader.

#### Example 3: Client Observations During a Network Partition
Let's trace what a client observes when interacting with a 5-node cluster (Nodes 1, 2, 3, 4, 5) that gets partitioned into Partition Major (Nodes 1, 2, 3) and Partition Minor (Nodes 4, 5).

```
   [Partition Major: Nodes 1, 2, 3]        ||      [Partition Minor: Nodes 4, 5]
   - Can form a majority (3/5)             ||      - Cannot form a majority (2/5)
   - Client writes are accepted here       ||      - Client writes fail or block here
```

**Scenario A: Under a CP System (e.g., etcd)**
- **Client 1 connects to Node 1 (Major side) and writes `val = 10`:** Node 1 contacts Node 2 and Node 3. It receives votes from a quorum of 3 nodes, commits the write, and returns success to Client 1.
- **Client 2 connects to Node 5 (Minor side) and tries to write `val = 20`:** Node 5 tries to contact other nodes. It can only reach Node 4, failing to form a quorum of 3. Node 5 rejects the write, returning an error or timing out.
- **Client 3 connects to Node 5 and tries to read `val`:** If etcd is configured for linearizable reads, Node 5 must contact a quorum before responding. Since it cannot, the read is rejected, ensuring the client never reads stale data.

**Scenario B: Under an AP System (e.g., Cassandra with Write=1, Read=1)**
- **Client 1 connects to Node 1 and writes `val = 10`:** Node 1 writes to its local storage, propagates it asynchronously to Node 2 and Node 3, and returns success.
- **Client 2 connects to Node 5 and writes `val = 20`:** Node 5 writes to its local storage, cannot reach Nodes 1, 2, or 3, but returns success to Client 2 anyway. It stores a "hint" to replicate to the other nodes once the partition heals.
- **Client 3 connects to Node 4 and reads `val`:** Node 4 returns its local value of `val`, which is old or potentially empty, because it cannot communicate with the major side. The system is available, but clients see diverging realities.

## Pros
- **CP Systems** ensure absolute data correctness across all nodes in the cluster. Clients never make business decisions based on stale or conflicting information, which is critical for banking and financial ledgers.
- **AP Systems** maximize system uptime by serving client requests even when major fiber cables are severed. This keeps essential operations like user checkouts and social interactions online during infrastructure failures.
- **Latency-optimized designs (EL)** provide fast user interactions. By avoiding synchronous round-trips across WAN networks during peace-time, applications achieve single-digit millisecond response times.
- **Consensus engines (Raft, Paxos)** automate cluster failover. They eliminate human operator intervention from leader election, allowing clusters to self-heal and recover in seconds.
- **Quorums** guarantee that system updates are durable once committed. Even if multiple nodes crash immediately after a write succeeds, the remaining majority ensures the data is preserved.

## Cons
- **CP Systems** generate high write failure rates and timeouts during minor network disruptions. If a partition isolates a client from the quorum, the client is completely blocked from updating state.
- **AP Systems** push the complexity of conflict resolution to the application layer. Developers must write complex merging logic, such as Last-Write-Wins or Conflict-Free Replicated Data Types (CRDTs), which are prone to bugs.
- **Latency-optimized systems** expose applications to read-your-own-writes anomalies. A client might update their profile, refresh the page immediately, and see their old profile because the read went to a lagging replica.
- **Consensus protocols** degrade in performance as the cluster size grows. Every write requires network round-trips to a majority of nodes, meaning larger clusters increase write latency.
- **Coordination services** introduce a single point of failure if they are misconfigured. If the ZooKeeper cluster itself loses quorum, the entire application dependency chain can lock up.

## Alternatives
- **Gossip Protocols:** Systems like Consul use gossip protocols (SWIM) to share cluster membership and health state. Gossip does not provide strong consensus but scales to thousands of nodes with minimal overhead, making it ideal for service discovery.
- **Single-Leader with Manual Failover:** Databases can use traditional master-slave replication without a consensus engine. If the master dies, replication stops or reads continue from slaves, and an operator must manually promote a new master. This avoids consensus latency but risks long downtime.
- **Multi-Master Replication:** In this model, multiple nodes can accept writes independently and sync later. It avoids a single consensus leader bottleneck, but requires conflict resolution strategies since concurrent, conflicting writes are guaranteed to happen.

## When to use it
- Use a **CP system with a consensus engine** when managing critical system state, such as service registration, cluster configuration, database schemas, or financial balances where correctness is non-negotiable.
- Use an **AP system with a latency-optimized setup** for high-volume telemetry, clickstream tracking, chat applications, or shopping carts where dropping a write or showing slightly stale data is preferable to blocking the user.
- Reach for **ZooKeeper or etcd** when you need to build distributed locks, leader election, or service discovery, rather than trying to write your own Raft or Paxos implementation.

## When NOT to use it
- Do not use a **CP consensus-backed database** for high-throughput, low-latency document or object storage. The network round-trips required for majority quorums will choke your write throughput.
- Do not use an **AP system** if your business logic cannot tolerate temporary inconsistency or if concurrent writes to the same record cannot be easily merged.
- Avoid using **ZooKeeper or etcd** to store large application payloads or files. These engines keep their entire state machine in memory to remain fast, so storing large assets will quickly exhaust node RAM and degrade consensus performance.

## Key takeaways / mental model
Think of a distributed system as a team of coworkers. If the phone lines go down (a network partition), they cannot talk. Two options present themselves. You can tell them to stop taking orders so they do not make conflicting sales (Consistency / CP), or you can tell them to keep taking orders and accept that they will have to resolve duplicate bookings tomorrow (Availability / AP). During normal days when the phones work, you must still decide whether to make a customer wait on hold while you double-check a sale with your colleague (Latency-Consistency trade-off / PACELC). Consensus protocols are the strict rulebooks that coworkers use to safely elect a team lead and agree on transactions.

To internalize this model, remember that consensus is not a single event. It is a continuous loop of heartbeat checks, quorum verification, and state transitions. Coordination services like ZooKeeper do not run your application logic. Instead, they act as the infallible referee, ensuring that even under severe network stress, only a single source of truth exists.

## Self-check questions
1. Why does the CAP theorem define consistency as linearizability, and how does this differ from the consistency (C) in ACID database transactions?
2. If a cluster of 7 nodes suffers a partition that isolates 3 nodes on one side and 4 nodes on the other, can a CP system using Raft continue to accept writes on both sides? Explain why or why not.
3. In the PACELC framework, why is it rare to see a database classified as PA/EC, and what would such a database prioritize during a partition versus normal times?
4. How does ZooKeeper use ephemeral nodes and watches to detect a leader failure and notify followers without requiring constant polling?
5. A client updates their username from "UserA" to "UserB" on a PA/EL database. Under what conditions will a subsequent read by the same client still return "UserA", and how does this relate to ddia/09?
6. When building a distributed locking mechanism, why must the lock lease have a timeout, and what happens if a node GC pause exceeds that timeout?
7. How does a database using Paxos or Raft handle network partitions differently from a traditional database using active-passive replication with automated failover via a witness node?

## References
- *System Design Guide for Software Professionals* (Sinha & Chopra, 2024), Chapter 3: "Distributed Systems Guarantees and Consensus"
- *Designing Data-Intensive Applications* (Martin Kleppmann), Chapter 9: "Consistency and Consensus"
- *Designing Data-Intensive Applications* (Martin Kleppmann), Chapter 5: "Replication"
