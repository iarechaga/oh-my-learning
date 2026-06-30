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
Consistency guarantees in distributed systems restrict the state transitions we can observe across nodes. Linearizability provides a strong recency guarantee by making a multi-node system behave like a single atomic copy of data. Causality represents a weaker but performant alternative, whereas consensus algorithms provide the ultimate coordinating block for achieving fault-tolerant agreement.

## The idea
Building dependable applications requires strong guarantees about how data changes are seen by clients. Without consistency guarantees, concurrent reads and writes can lead to bizarre anomalies that confuse users and corrupt business state. This lesson explores the spectrum of consistency models, from the ultra-strict linearizability to the weaker causal consistency. It also examines how systems reach consensus to coordinate decisions across a cluster.

Understanding these concepts builds directly upon transactions, as discussed in [11-transactions.md](11-transactions.md), and physical node limitations covered in [12-distributed-systems-trouble.md](12-distributed-systems-trouble.md).

## How it works
To understand how consistency works, we must study the guarantees provided by different models and how systems coordinate state transitions.

### 1. Linearizability (Strong Consistency)
Linearizability, which is also known as strong consistency, is a recency guarantee. It ensures that the system behaves as if there is only a single copy of the data, and every operation is atomic. Once a read returns a new value, all subsequent reads by any client must return that value or an even newer one.

It is critical not to confuse linearizability with serializability. Serializability is an isolation property of transactions, ensuring that executing concurrent transactions has the same effect as running them in some serial order. Linearizability is a recency guarantee on read and write operations of a single object. You can combine both to get strict serializability.

Achieving linearizability has severe costs. In terms of performance, network round trips are required on reads to ensure no other node has accepted a newer write. Under the CAP theorem, if a network partition occurs, a linearizable system must reject write or read requests to prevent returning stale data. The system sacrifices availability to preserve its strong consistency guarantees.

### 2. Ordering and Causality
Causality is a weaker guarantee than linearizability, but it is often sufficient and much cheaper. A causally consistent system preserves the order of cause and effect. If question A is answered by post B, then post B must always be displayed after question A across all nodes.

To implement causal ordering without the performance penalty of linearizability, systems use logical timestamps. Lamport timestamps are a classic example. Every node maintains a counter, and it increments this counter on every event. The node attaches its counter to every message. When another node receives a message with a higher timestamp, it updates its own counter to match the received timestamp plus one. This mechanism defines a total order of events, but it does not allow a node to know immediately if a request is valid without communicating with other nodes.

Total order broadcast is an ordering protocol where all nodes receive the same messages in the exact same order. This protocol is mathematically equivalent to consensus. If you can solve total order broadcast, you can solve consensus, and vice versa.

### 3. Distributed Transactions and Consensus
Distributed transactions ensure that an operation either commits on all participating nodes or aborts on all of them. The standard protocol for this is two-phase commit (2PC). In 2PC, a coordinator node asks all participants to prepare to commit. Supposing every participant votes 'yes', the coordinator sends a commit message in the second phase. Otherwise, if any participant votes 'no' or times out, the coordinator sends an abort message.

The main weakness of 2PC is that it is a blocking protocol. If the coordinator crashes after participants have voted 'yes' but before sending the commit decision, the participants are left in limbo. They cannot safely abort or commit, and they must hold onto locks until the coordinator recovers.

Consensus algorithms, such as Paxos, Raft, or Zab, solve this blocking problem. These protocols are non-blocking because they only require a majority of nodes to be functional. They elect a leader to propose sequence numbers and use quorums to agree on state transitions.

The FLP impossibility result states that no consensus protocol can guarantee agreement in a purely asynchronous system model if even a single node is allowed to crash. Real systems sidestep this theoretical limitation by using timeouts. They assume a partially synchronous network model where messages are eventually delivered within a reasonable delay.

### 4. Coordination Services
Services like ZooKeeper and etcd use consensus under the hood to provide high-level coordination features. They act as small, highly available databases that offer lock lease management, leader election, and group membership tracking. Other larger systems build on top of these coordination services to manage their own distributed state.

## Pros
- Strongest predictability: Linearizability makes reasoning about concurrent state changes straightforward.
- Causal correctness: Preserving causal ordering prevents user confusion in collaborative applications.
- Automatic coordination: Consensus algorithms allow systems to automatically elect new leaders and recover from node failures.

## Cons
- Performance degradation: Linearizable systems suffer from significant latency overhead.
- Partition intolerance: Enforcing linearizability requires sacrificing availability when nodes cannot communicate.
- Deadlock risks: Two-phase commit can block forever if the coordinator crashes during the critical phase.

## Alternatives
- **Eventual consistency**: Allow nodes to diverge temporarily and resolve conflicts later. This is highly available and fast, but clients can read stale or inconsistent data.
- **Causal consistency**: Enforce ordering based on cause and effect instead of a global wall clock. It provides a good balance of speed and consistency for collaborative tools.

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

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 9
- For foundation concepts on transactions, see [11-transactions.md](11-transactions.md).
- To review the physical limitations and troubles of distributed networks, see [12-distributed-systems-trouble.md](12-distributed-systems-trouble.md).
