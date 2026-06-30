---
id: ddia/13
subject: ddia
title: Consistency and Consensus
slug: consistency-and-consensus
status: drafted
mastery:
source: Designing Data-Intensive Applications (Martin Kleppmann), Chapter 9
prerequisites: [ddia/11, ddia/12]
created: 2026-06-30
updated: 2026-06-30
---

# Consistency and Consensus

## TL;DR
Consistency guarantees restrict the state transitions we can observe across nodes in a distributed system. Linearizability behaves like a single atomic copy of data with a strict recency guarantee, while causal consistency preserves ordering based on cause and effect. Enforcing these strong guarantees requires consensus, which is equivalent to total order broadcast and solves the atomic commit problem.

## The idea
In a distributed system, a client reading from different replicas might see old data on one node and new data on another. This inconsistency leads to subtle, hard to debug errors that frustrate users and corrupt database state. Consistency models exist to provide predictable rules for how operations on different nodes appear to be ordered. They allow application developers to treat a complex cluster of machines as a unified system, hiding the underlying network failures and replication delays.

Understanding these concepts builds directly upon transactions, as discussed in [11-transactions.md](11-transactions.md), and physical node limitations covered in [12-distributed-systems-trouble.md](12-distributed-systems-trouble.md).

## How it works
To understand how consistency works, we must study the guarantees provided by different models and how systems coordinate state transitions.

### 1. What is Linearizability?
Linearizability, which is also known as strong consistency, is a recency guarantee. It ensures that the system behaves as if there's only a single copy of the data, and every operation is atomic. Once a read returns a new value, all subsequent reads by any client must return that value or an even newer one.

The basic model is a register, which is a single variable that clients can read or write. Linearizability imposes a real-time constraint: if operation B starts after operation A completes in real time, then B must see the state of the world as it is after A, or even newer.

It's critical not to confuse linearizability with serializability. Serializability is an isolation property of transactions, ensuring that executing concurrent transactions has the same effect as running them in some serial order. Linearizability is a recency guarantee on read and write operations of a single object. You can combine both to get strict serializability.

Here's a comparison table summarizing the core differences:

| Property | Linearizability | Serializability |
| --- | --- | --- |
| **Type of Guarantee** | Recency / Real-time order of single operations | Isolation of multi-operation transactions |
| **Multi-object?** | No (guarantees a single object/register) | Yes (guarantees across multiple objects/rows) |
| **Real-time constraint?** | Yes (subsequent read must see completed write) | No (allows arbitrary serialisable executions) |
| **Performance Cost** | High (latency round trips on every read/write) | High (lock contention, aborts, or coordination) |

Let's look at a read and write timeline to understand this distinction. Here's an execution showing concurrent operations.

```
Client A: |---- write(x, 1) ----|
Client B:       |-- read(x) -> 1 --|
Client C:             |---- write(x, 2) ----|
Client D:                   |-- read(x) -> 1 --|  <-- Linearizability Violation!
Client E:                         |-- read(x) -> 2 --|
```

In this timeline:
- Client A writes 1 to register x.
- Client B reads x and gets 1. This is valid because the write was concurrent.
- Client C writes 2 to register x.
- Client D reads x and gets 1. This is a violation of linearizability. Since Client B already read the value 1 and Client C completed the write of 2 (or we observed its effect), reading an older value like 1 after a newer value has been read violates the recency guarantee.
- Client E reads x and gets 2, which is correct.

Once a read returns a new value, the system must freeze that state for all future reads. Here's a valid linearizable read/write timeline:

```
Client A: |---- write(x, 1) ----|
Client B:       |-- read(x) -> 1 --|
Client C:             |---- write(x, 2) ----|
Client D:                   |-- read(x) -> 2 --|  <-- Valid! Returns newest value
Client E:                         |-- read(x) -> 2 --|
```

### 2. Why and When We Need Linearizability
We need linearizability in several critical application scenarios where weaker consistency models would lead to race conditions or incorrect behavior:

- **Locks and leader election**: In systems like ZooKeeper or etcd, we must ensure that only a single node is the leader at any given time. If two nodes concurrently try to acquire a lock to become the leader, only one must succeed. This lock has to be linearizable. If it's not, we might end up with split-brain, where two nodes believe they are both the active leader, leading to concurrent writes and data corruption.
- **Uniqueness constraints**: When a user registers a username or email address, two concurrent sign-ups for the same name can't both succeed. We need a linearizable register to check and set the value. Under eventual consistency, both registrations might succeed on different replicas and only conflict later during asynchronous replication, which is too late to prevent the duplicate account.
- **Cross-channel race conditions**: If a user uploads an image, the web server stores it in an object store (like S3), and then puts a message on a message queue for the image resizer. If the resizer reads the queue, pulls the message, and tries to read the image from the replica before it has finished replicating, the image will be missing. This race condition occurs because S3 doesn't offer linearizable guarantees across these communication channels.

### 3. Implementing Linearizable Systems
Can we build a linearizable system using common replication methods? Let's analyze the possibilities:

- **Single-leader replication**: This can be linearizable if we route all reads and writes to the leader. However, we must ensure that the leader is still the true leader (split-brain problem). If there's a network partition, the old leader might think it's still the leader but a new leader was elected. To avoid this, we can implement:
  - **Read-index path**: The leader queries a majority of replicas during the read to verify it's still the leader and find the latest committed index.
  - **Lease-read path**: The leader uses a physical clock lease during which it can serve reads locally without querying other nodes. This method relies on synchronized physical clocks.
- **Consensus algorithms**: Yes, protocols like Raft or Paxos can implement linearizable reads and writes because they naturally use quorums and leader leases to avoid split-brain scenarios.
- **Multi-leader replication**: No, because they allow concurrent writes on different nodes, which are merged asynchronously, violating the single-register illusion. For instance, if Client A writes x=2 at Leader 1, and Client B writes x=3 at Leader 2, concurrent reads on both leaders will return different values, breaking linearizability.
- **Leaderless replication**: Even with quorums (W + R > N), leaderless replication is not linearizable. Let's look at how this fails.

#### Worked Example 1: Non-Linearizability in Leaderless Quorums
Suppose we have a 3-replica cluster (Node 1, Node 2, Node 3) with W=2, R=2, N=3. The initial value of register x is 1.

```
Node 1: [ x=1 ] -> [ x=2 ]
Node 2: [ x=1 ] ---------> [ x=2 ] (delayed write)
Node 3: [ x=1 ] 
```

1. Client A performs a write `write(x, 2)` with quorum W=2.
2. The write succeeds on Node 1, but the write to Node 2 is delayed due to network lag. The client gets confirmation because Node 1 and Node 2 eventually accept it, but at the exact moment of overlap, let's see what happens.
3. Client B performs a read with quorum R=2, reading from Node 1 and Node 3. It gets values `[2, 1]` and picks 2 as the newest value.
4. Client C performs a read with quorum R=2, reading from Node 2 and Node 3. Since Node 2 has not received the write yet, Client C gets values `[1, 1]` and picks 1.
5. Even though Client C's read started after Client B's read completed and returned 2, Client C reads the stale value 1. This violates linearizability.

#### The Read Repair Timing Anomaly
You might think that read repair can restore linearizability in leaderless systems. However, it can't, because of timing anomalies during concurrent reads and writes.

Suppose we write a new value x=2 with W=2. The write succeeds on Node 1 but is delayed on Node 2. Now Client B reads with R=2 from Node 1 and Node 3. Client B sees x=2 from Node 1 and x=1 from Node 3. It selects x=2 and initiates an asynchronous read repair to update Node 3.

Before the read repair completes on Node 3, Client C reads with R=2 from Node 2 and Node 3. Node 2 has not received the write yet, and Node 3's repair is still in progress. Client C reads x=1 from Node 2 and x=1 from Node 3, and returns x=1. Client C has read a stale value *after* Client B read the newer value. This violates linearizability. To prevent this, read repairs must be synchronous and block the returning of Client B's read until Node 3 is fully updated, which drastically hurts performance.

Furthermore, **Last-Write-Wins (LWW)** is inherently non-linearizable. This is because physical clocks can't be synchronized perfectly across machines. A clock can drift backwards or forwards, meaning a node might assign a timestamp to a write that is in the future compared to another node's clock. This clock skew causes writes to be dropped or overwritten in ways that violate the real-time order, breaking the recency guarantee of linearizability.

### 4. The Cost of Linearizability (CAP and Performance)
The CAP theorem states that if there's a network partition (P), a distributed system must choose between Consistency (C, which means linearizability) or Availability (A, which means returning a response even if it's stale).

```
          +-----------------------------------------+
          |            Network Partition            |
          +-----------------------------------------+
                     /                           \
                    /                             \
   Choose Consistency (C)                       Choose Availability (A)
   - Rejects stale reads/writes                 - Allows local reads/writes
   - Ensures linearizability                    - Violates linearizability
   - Sacrifices availability                    - Stale data is returned
```

But even when there's no partition, linearizability carries a massive performance penalty. Because every read requires either talking to a quorum of nodes or checking with the leader to ensure it's still the leader, we add network round trips and latency. High performance and linearizability are fundamentally at odds.

### 5. Ordering, Causality, and Timestamps
Causality is a weaker guarantee than linearizability, but it's often sufficient and much cheaper. It preserves the order of cause and effect. It's the strongest consistency model that doesn't require a global clock or consensus, meaning it can remain fully available even during a network partition.

- **Causal order is a partial order**: Not all events are comparable. If event A caused event B, they are ordered. If they are independent, they are concurrent, meaning we can't say which happened first.
- **Linearizable order is a total order**: Every event is ordered in real time.

#### Worked Example 2: Lamport Timestamps versus Version Vectors
To track causality, systems use logical timestamps. Let's compare Lamport timestamps and version vectors:

```
Lamport Timestamp: (counter, nodeId) -> Total Order
Version Vector:    [NodeA: cA, NodeB: cB] -> Partial Order (Causality Tracking)
```

**Lamport Timestamp Algorithm**:
1. Each node maintains a local counter, initialized to 0.
2. Before executing an event (like a write), the node increments its counter: `counter = counter + 1`.
3. When sending a message, the node attaches its counter and its unique node ID: `(counter, nodeId)`.
4. On receiving a message with timestamp `(msg_counter, msg_nodeId)`, the node updates its local counter: `counter = max(counter, msg_counter) + 1`.
5. We compare two timestamps `(c1, n1)` and `(c2, n2)`: event 1 is less than event 2 if `c1 < c2`, or if `c1 == c2` and `n1 < n2`.

**Version Vector Algorithm**:
1. Each node maintains a vector of counters representing the writes it has seen from each node: `[NodeA: cA, NodeB: cB, ...]`.
2. When a node performs a write, it increments its own counter in its local vector.
3. It attaches its local vector to every message sent.
4. When receiving a message, a node updates its vector by taking the element-wise maximum of its local vector and the received vector.
5. If vector V1 is element-wise greater than or equal to V2, and has at least one strictly greater element, then V1 causally succeeds V2. Otherwise, if neither is greater, the events are concurrent.

Suppose we have two nodes, A and B. They execute concurrent events:
- Event 1 on Node A: local counter increments to 1. Lamport timestamp: `(1, A)`. Version vector: `[A: 1, B: 0]`.
- Event 2 on Node B: local counter increments to 1. Lamport timestamp: `(1, B)`. Version vector: `[A: 0, B: 1]`.

If we compare Lamport timestamps:
- `(1, A)` is less than `(1, B)` because we break ties using the node ID. This gives us a total order, but it doesn't tell us if the events were concurrent.
- If we look at version vectors `[A: 1, B: 0]` and `[A: 0, B: 1]`, neither is greater than the other. This tells us the events are concurrent, which Lamport timestamps can't do.

Why timestamp ordering alone is insufficient: suppose we want to enforce a username uniqueness constraint on the fly. If two users try to claim "bob" concurrently, and we get timestamps `(1, A)` and `(1, B)`. Node B can't decide immediately whether to accept the request. It has to wait and see if any other node has generated a request with a lower timestamp. This requires communicating with every other node, which is equivalent to total order broadcast.

**Total order broadcast** is an ordering protocol where:
1. All messages are delivered to all nodes in the exact same order.
2. No messages are lost.

This protocol is mathematically equivalent to consensus. If you can solve total order broadcast, you can solve consensus, and vice versa. It's the basis of **State-Machine Replication (SMR)**, where nodes process the same sequence of logs in the same order, maintaining identical state.

### 6. Distributed Transactions and Consensus
Distributed transactions ensure that an operation either commits on all participating nodes or aborts on all of them. The standard protocol for this is two-phase commit (2PC).

It is crucial to distinguish 2PC from consensus protocols like Raft. 2PC is for atomic commit across different shards, where *every* participant must agree to commit. If even one participant votes no or crashes, the transaction must abort. Raft, on the other hand, is for replicating a log within a single shard, where only a *majority* of replicas must agree, allowing the system to make progress even if some replicas fail.

#### Worked Example 3: Two-Phase Commit Execution and Failure
Let's look at the sequence of messages in a 2PC transaction:

```
Coordinator                  Participant 1                Participant 2
    |                              |                            |
    |---- 1. Prepare ------------->|                            |
    |---- 1. Prepare ------------------------------------------>|
    |                              |                            |
    |--------- (Participants check constraints/locks) ----------|
    |                              |                            |
    |<--- 2. Vote Yes -------------|                            |
    |<--- 2. Vote Yes ------------------------------------------|
    |                              |                            |
    |-- [CRASHES HERE]             |                            |
    X                              |                            |
                             (In Doubt!)                  (In Doubt!)
```

Let's break down the execution steps:
1. **Prepare Phase**: The coordinator assigns a unique transaction ID and sends a `prepare` message to all participants.
2. **Voting**: Each participant checks if it can commit (e.g. locks are acquired, constraints are met). They write a prepared record to their log and vote `yes` or `no`.
3. **Commit Phase**: If everyone votes `yes`, the coordinator writes a `commit` decision to its transaction log on disk and sends a `commit` message to all participants. If any participant votes `no` or times out, the coordinator writes `abort` to its log and sends an `abort` message.

**The Blocking Problem**: If the coordinator crashes after participants have voted `yes` but before sending the commit or abort decision, the participants are in doubt. They can't decide on their own because they don't know if another participant received a commit. They must block and hold onto their locks indefinitely until the coordinator recovers.

**XA Transactions**: XA is an open standard for distributed transactions across heterogeneous systems (e.g. a database and a message queue). It relies on 2PC, which means it suffers from the same blocking problem and carries heavy performance costs.

XA consists of two main components:
- **Transaction Manager**: The coordinator that manages the lifecycle of the transaction and makes the commit or abort decisions.
- **Resource Managers**: The databases or message queues participating in the transaction, which implement the XA API to interact with the transaction manager.

The XA API allows resource managers to tell the transaction manager whether they have successfully prepared. However, XA is a blocking protocol. If the transaction manager crashes, resource managers must keep locks on all modified data until the manager restarts and decides. This lock-holding can bring a high-throughput system to a complete standstill.

#### 6.1 Three-Phase Commit (3PC) in Detail
Three-Phase Commit (3PC) was proposed to solve the blocking problem of 2PC. It splits the commit phase into two stages, leading to three phases:
1. **CanCommit Phase**: Similar to the prepare phase, the coordinator asks if participants can commit.
2. **PreCommit Phase**: If all vote yes, the coordinator sends a `PreCommit` message. Participants write to their logs and acknowledge. If the coordinator crashes now, participants can safely time out and abort, or coordinate amongst themselves because they know everyone has at least voted yes.
3. **DoCommit Phase**: The coordinator sends a `DoCommit` message to finalise the transaction.

While 3PC is theoretically non-blocking, it relies on a perfect failure detector with bounded delays. Because real networks have unbounded delays, a slow participant can easily be misidentified as dead, leading to a split state where some nodes commit and others abort under partitions. Thus, 3PC is rarely used in practice.

#### Formal Properties of Consensus
A consensus algorithm must satisfy four formal properties to be correct:
1. **Uniform Agreement**: No two nodes decide differently.
2. **Integrity**: No node decides twice.
3. **Validity**: If a node decides value V, then V must have been proposed by some node.
4. **Termination**: Every node that does not crash eventually decides some value.

Algorithms like Raft, Paxos, Multi-Paxos, and Zab solve this by using:
- **Epoch / Ballot / Term numbers**: To track leadership generations and ensure only one leader is active per term.
- **Quorums**: To ensure that a leader must consult a majority of nodes to elect itself or commit proposals. This guarantees that at least one node in the new leader's quorum has the latest committed state.

**The FLP Impossibility Result**:
Fischer, Lynch, and Paterson (1985) proved that in a purely asynchronous system model (where clocks don't exist, messages can be delayed indefinitely, and nodes can fail by crashing), no deterministic consensus protocol can guarantee agreement if even a single node can fail. Real systems handle this limitation by moving to a partially synchronous model, using timeouts to detect and suspect crashed nodes, and electing new leaders.

### 6.2 Comparing Consensus Algorithms
Let's look at how the main consensus algorithms compare in their primary goals and replication models:

| Algorithm | Primary Model | Leader Model | Key Failure Recovery Mechanism |
|---|---|---|---|
| **Paxos** | Consensus on a single value (Basic) or sequence of values (Multi-Paxos) | Symmetric (any node can propose), but Multi-Paxos uses distinguished proposer | Two-phase ballot round-trips to override older leaders |
| **Raft** | Replicated log | Strong leader (only logs can flow from leader to followers) | Term-based leader election with strict log-matching safety property |
| **Zab** | ZooKeeper Atomic Broadcast | Active primary leader for all state updates | Phase recovery using epoch numbers and transactional log synchronisation |
| **VSR** | Viewstamp Replication | Primary-backup with view changes | View-change protocol where a new primary reconstructs state from replicas |

**Limitations of Consensus**:
- They require a majority of nodes to make progress. If more than half the nodes fail, the system blocks.
- They have high network overhead due to constant heartbeat messages and voting round trips.
- They are sensitive to slow or unstable nodes, which can drag down the performance of the entire cluster.

### 7. Coordination Services
Services like ZooKeeper and etcd use consensus under the hood to provide high-level coordination features. They act as small, highly available databases that offer:
- **Lease management**: To automatically release locks if a client crashes or becomes partitioned.
- **Leader election**: To select a single master node for a larger application.
- **Group membership**: To track which nodes are currently alive in a cluster.
- **Watch notifications**: To allow clients to subscribe to changes in the database state without polling.

While ZooKeeper uses the Zab protocol and etcd uses Raft, they both provide a similar hierarchical key-value model. ZooKeeper represents data as nodes in a tree (similar to a filesystem), whereas etcd presents a flat key-value namespace with prefix queries. Both services are designed for small metadata volumes, not for storing bulk application data. Reading and writing to them is slow compared to standard relational databases, but they provide the ultimate source of truth for clustering configurations.

Other larger systems build on top of these coordination services to manage their own distributed state.

## Pros
- **Strongest predictability**: Linearizability makes reasoning about concurrent state changes straightforward because the system behaves like a single copy of data.
- **Causal correctness**: Preserving causal ordering prevents user confusion in collaborative applications like chat apps or discussion forums.
- **Automatic coordination**: Consensus algorithms allow systems to automatically elect new leaders and recover from node failures without human intervention.
- **Preventing split-brain**: Strong consensus guarantees that only one node can act as the leader, preventing data corruption from dual leaders.

## Cons
- **Performance degradation**: Linearizable systems suffer from significant latency overhead due to network round trips on every read and write.
- **Partition intolerance**: Enforcing linearizability requires sacrificing availability when nodes cannot communicate, as dictated by the CAP theorem.
- **Deadlock and blocking**: Two-phase commit can block forever if the coordinator crashes during the critical phase, holding locks on all participants.
- **Majority requirement**: Consensus algorithms require a strict majority of healthy nodes to make progress, making them vulnerable to larger outages.

## Alternatives
- **Eventual consistency**: Allow nodes to diverge temporarily and resolve conflicts later. This is highly available and fast, but clients can read stale or inconsistent data.
- **Causal consistency**: Enforce ordering based on cause and effect instead of a global clock. It provides a good balance of speed and consistency for collaborative tools.
- **Saga pattern**: Break a distributed transaction into a series of local transactions. Each local transaction updates the database and triggers the next step. If a step fails, compensation transactions are executed to undo the changes. Under a Saga, we do not lock resource managers. Instead, each local transaction commits and we use compensation transactions to rollback if subsequent steps fail.

## When to use it
Reach for linearizability when you are implementing financial ledgers, asset tracking, or username registries where race conditions can lead to immediate duplicate accounts or lost funds. Choose consensus algorithms when building primary-replica database orchestrators that require automated, split-brain-free leader election. These tools are indispensable for highly coordinated state machines.

## When NOT to use it
Avoid linearizable systems if your application requires high availability across unstable networks, such as mobile clients or multi-region deployments. In these scenarios, use eventual or causal consistency instead. You should also avoid two-phase commit for high-throughput transactional systems due to its high blocking latency. Reach for saga patterns or local partition-based transactions for better scalability.

## Key takeaways / mental model
Linearizability and serializability are orthogonal concepts. The former guarantees read recency on a single object, while the latter guarantees transaction isolation on multiple objects. When you need guaranteed agreement across nodes, use consensus protocols which rely on quorums and leaders, while sidestepping theoretical asynchronous limits through timeouts.

## Self-check questions
1. How does linearizability differ from serializability in terms of what they guarantee?
2. What is the blocking problem in two-phase commit, and how do consensus algorithms solve it?
3. Under what network condition does the FLP impossibility result apply, and how do practical systems handle it?
4. How can we use Lamport timestamps to establish a total order of events, and what is their main limitation?
5. Why are quorum read and write operations (W + R > N) in a leaderless system insufficient to guarantee linearizability?
6. What is the difference between a total order (like linearizability) and a partial order (like causal consistency)?
7. How does a two-phase commit (2PC) protocol differ from a consensus protocol like Raft or Paxos?
8. Why are etcd and ZooKeeper designed only for small volumes of metadata, and what would happen if you tried to store gigabytes of bulk application data in them?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 9
- For foundation concepts on transactions, see [11-transactions.md](11-transactions.md).
- To review the physical limitations and troubles of distributed networks, see [12-distributed-systems-trouble.md](12-distributed-systems-trouble.md).
