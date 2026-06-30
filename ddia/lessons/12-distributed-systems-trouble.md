---
id: ddia/12
subject: ddia
title: The Trouble with Distributed Systems
slug: distributed-systems-trouble
status: drafted
mastery:
source: Designing Data-Intensive Applications (Martin Kleppmann), Chapter 8
prerequisites: [ddia/07]
created: 2026-06-30
updated: 2026-06-30
---

# The Trouble with Distributed Systems

## TL;DR
Distributed systems are characterized by partial failure, where some components break while others continue running. This unpredictability arises because of unreliable networks, unstable clocks, and arbitrary process pauses. Engineering around these faults requires defining explicit system models and relying on quorum-based consensus with fencing tokens.

## The idea
Writing software for a single computer is relatively straightforward because the hardware either works or crashes completely. Distributed systems do not have this luxury, as they suffer from partial failures. In a partial-failure scenario, some parts of the system break while other parts remain operational in ways you cannot easily predict. This makes distributed systems uniquely hard to build, because a node cannot know for sure what is happening on another machine. You must design software with the assumption that things will go wrong, and you have to use peer consensus to determine the state of the world.

Before studying consistency and consensus, it is highly recommended to review single-leader replication in [07-replication-single-leader.md](07-replication-single-leader.md) to understand how data is distributed and synchronized.

## How it works
To understand how distributed systems behave, we must examine the specific physical limitations of our hardware and infrastructure. These limitations manifest in three primary areas: the network, the system clocks, and the processes themselves.

### 1. Unreliable Networks
IP networks are asynchronous, meaning they make no guarantees about when a packet will arrive or if it will arrive at all. When you send a message over the network, it can be lost, delayed, duplicated, or reordered. If you do not receive a response from a remote node, you cannot determine if the request was lost, the remote node crashed, or the response was lost on its way back. Slow nodes look identical to dead nodes.

Timeouts are the only tool we have to detect failures. Choosing a timeout value involves a difficult trade-off. A short timeout detects dead nodes quickly, but risks falsely declaring a slow node as dead. Long timeouts prevent false positives but force the system to wait a long time before recovering. Synchronous networks, like the telephone system, reserve bandwidth to guarantee latency, but packet-switched networks multiplex traffic and cannot offer such guarantees without extreme inefficiency.

### 2. Unreliable Clocks
Computers have two different types of clocks. Time-of-day clocks, synchronized via Network Time Protocol (NTP), return the current wall-clock time. These clocks are prone to sudden jumps backward or forward when NTP adjusts them, and they suffer from clock skew across different machines. Monotonic clocks are designed for measuring elapsed time, as they only move forward.

Relying on time-of-day clocks to order writes across different nodes is dangerous. For instance, in a last-write-wins (LWW) conflict resolution scheme, clock skew can cause a newer write to be silently discarded because its timestamp is lower than a stale write from a node with a fast clock. Logical clocks, which use sequence numbers instead of physical time, provide a reliable way to order events.

### 3. Process Pauses
Node execution is not continuous. A node might pause at any time due to stop-the-world garbage collection, virtual machine suspension, or thread scheduling. These pauses can last for seconds or even minutes.

Suppose a node obtains a lease to be the leader for ten seconds. If it experiences a nine-second garbage collection pause, it might think it still holds the lease when it resumes, even though the lease has expired. It will then proceed to perform unsafe writes, corrupting the database.

### 4. Knowledge, Truth, and Lies
Distributed systems cannot rely on a single node to determine what is true. Truth is defined by a majority or quorum of nodes. A single node must accept that its own perspective might be outdated or incorrect.

To prevent a paused leader from performing unsafe writes, we use fencing tokens. Every time a lease is granted, a lock server issues a fencing token, which is an increasing number. The storage engine validates this token on every write and rejects requests with a token lower than the last processed one. Finally, we usually assume nodes are honest but faulty. Byzantine faults, where nodes actively lie or send malicious messages, require much more complex protocols to solve, and we usually assume they do not occur in private datacenters.

## Pros
- Partial tolerance: The system can keep running even if some nodes crash.
- Scalability: You can distribute the workload across multiple physical machines.
- Geographic locality: Running nodes closer to users reduces latency.

## Cons
- Extreme complexity: Debugging and reasoning about partial failures is incredibly difficult.
- Latency overhead: Communicating over the network adds significant latency compared to memory access.
- Consistency issues: Replicating data across nodes introduces race conditions and synchronization challenges.

## Alternatives
- **Single-machine database**: Run everything on a single, powerful machine with replication only for backup. This avoids all network and clock issues but limits your scalability.
- **Synchronous cluster**: Use a tightly coupled network with hardware-guaranteed latencies. It eliminates the unpredictability of asynchronous networks but is incredibly expensive and lacks flexibility.

## When to use it
You should design your application for a distributed environment when your data size or transaction volume exceeds the capacity of a single machine. It is also necessary when you need high availability across different geographical regions to survive total datacenter outages. This approach is standard for large-scale web applications.

## When NOT to use it
Do not build a distributed system if your entire dataset fits comfortably on a single server and your uptime requirements can be met with simple active-passive cold standbys. The complexity is rarely worth the overhead for small-scale applications. In those cases, reach for a single, high-performance database instance instead.

## Key takeaways / mental model
In a distributed system, a single node is a fundamentally unreliable narrator. It cannot trust its own clock, its execution speed, or its connection to the rest of the cluster. Truth must be established through a quorum of nodes, and any action taken by a leader must be validated using fencing tokens to prevent paused nodes from corrupting the system.

## Self-check questions
1. Why is a network timeout the only reliable way to detect if a remote node has failed?
2. What is the difference between a time-of-day clock and a monotonic clock, and why should you never use the former to order writes?
3. How can a garbage collection pause cause a node to falsely believe it is still the leader of a cluster?
4. What role do fencing tokens play in preventing a paused node from executing outdated or corrupting writes?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 8
- Prerequisites and baseline replication concepts are in [07-replication-single-leader.md](07-replication-single-leader.md).
