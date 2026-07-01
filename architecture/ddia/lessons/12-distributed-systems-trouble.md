---
id: ddia/12
subject: ddia
title: The Trouble with Distributed Systems
slug: distributed-systems-trouble
status: drafted
mastery:
seniority: senior
source: Designing Data-Intensive Applications (Martin Kleppmann), Chapter 8
prerequisites: [ddia/07]
created: 2026-06-30
updated: 2026-06-30
---

# The Trouble with Distributed Systems

## TL;DR
Distributed systems operate under the constant threat of partial failure, where some components break while others continue running unpredictably. This environment suffers from asynchronous network delays, unstable physical clocks, and unexpected process pauses like garbage collection. To build reliable systems on top of these shaky foundations, we must define strict system models and establish truth through node quorums with fencing tokens.

## The idea
Writing software for a single computer is straightforward because the hardware is deterministic: it either works or fails completely. Distributed systems do not have this luxury, as they suffer from partial failures. In a partial-failure scenario, some parts of the system break while other parts remain operational in ways that are highly unpredictable.

This makes distributed systems uniquely hard to build, because a node cannot know for sure what is happening on another machine. You must design software with the assumption that everything will eventually fail, using peer consensus to determine the state of the world.

This represents a major philosophical divide in computing. The supercomputer philosophy treats a cluster of machines as a single large computer, halting the entire system if any component fails. This is typical of high-performance computing (HPC) workloads. The cloud computing philosophy assumes that commodity hardware is cheap and untrusted, meaning that partial failures are expected, and the software must tolerate individual node deaths without interrupting the user.

Before studying consistency and consensus, it is highly recommended to review single-leader replication in [07-replication-single-leader.md](07-replication-single-leader.md) to understand how data is distributed and synchronized.

## How it works
To understand how distributed systems behave, we must examine the physical limitations of our hardware, networks, and clocks.

### Unreliable Networks
IP networks are asynchronous, meaning they make no guarantees about when a packet will arrive or if it will arrive at all. When you send a message over the network, it can be lost, delayed, duplicated, or reordered. If you do not receive a response from a remote node, you cannot determine if the request was lost, the remote node crashed, or the response was lost on its way back. Slow nodes look identical to dead nodes.

Timeouts are the only tool we have to detect failures. Choosing a timeout value involves a difficult trade-off. A short timeout detects dead nodes quickly, but risks falsely declaring a slow node as dead. Long timeouts prevent false positives but force the system to wait a long time before recovering.

Queueing is the main driver of network latency fluctuations. If multiple nodes try to send packets to the same destination simultaneously, the network switch must buffer them, creating a queue. If the buffer fills up, packets are silently dropped. Similar queueing delays happen in the operating system's network stack, hypervisors, and virtual machines.

Additionally, TCP head-of-line blocking can delay application-level delivery of packets even if they physically arrive on time. You cannot simply make the network reliable because packet-switched networks multiplex traffic dynamically, prioritizing utilization over latency guarantees. This contrasts with synchronous circuit-switched networks used in telephone lines, which reserve dedicated bandwidth but are highly inefficient for bursty computer data.

### Unreliable Clocks
Clocks are a fundamental source of truth for software, yet they are shockingly unreliable in distributed systems. Every node has its own local quartz crystal oscillator, which drifts over time due to temperature variations, age, and vibration.

To keep these clocks aligned, we rely on the Network Time Protocol (NTP), which queries a set of time servers. NTP sync comes with massive limitations, as it can be blocked by network congestion or firewalls. NTP servers are organized into strata, representing their distance from a high-precision reference clock like an atomic clock or GPS receiver.

If a node's clock is adjusted backward by NTP, time-of-day clocks will experience sudden jumps, making them dangerous for measuring elapsed time. To avoid these jumps, NTP can gradually slow down or speed up the clock rate, a process called slewing, but this still has limits.

In contrast, monotonic clocks only move forward, making them perfect for measuring duration on a single machine. They are usually backed by CPU tick counters like the Time Stamp Counter (TSC) on x86 processors. However, monotonic clocks cannot be compared across different servers because their absolute values are meaningless outside the local machine.

Relying on physical timestamps to order events across multiple servers is an invitation to data loss. This is especially true in last-write-wins conflict resolution, where clock skew can cause a newer write to be discarded.

Google Spanner tackles this by using TrueTime, an API that returns a confidence interval representing the earliest and latest possible time `[earliest, latest]`. If the confidence intervals of two events do not overlap, we can safely determine their order. To guarantee transactions are ordered correctly, Spanner actually waits out the uncertainty interval before committing a write, ensuring that no subsequent transaction can obtain a lower timestamp.

### Process Pauses
Node execution is not continuous. A node might pause at any time due to stop-the-world garbage collection, virtual machine suspension, or thread scheduling. These pauses can last for seconds or even minutes.

During a virtual machine migration, the hypervisor pauses the VM, copies its memory to another physical host, and resumes it. This pause is transparent to the guest OS but can cause massive real-world pauses. Similarly, a page fault in the operating system can cause a thread to block on disk I/O, pausing execution.

Suppose a node obtains a lease to be the leader for ten seconds. If it experiences a nine-second garbage collection pause, it might think it still holds the lease when it resumes, even though the lease has expired. It will then proceed to perform unsafe writes, corrupting the database.

To mitigate this, applications can use garbage collection pauses detection, or run on languages without automatic memory management. However, these steps only reduce the frequency of pauses; they cannot eliminate them.

### Fencing Tokens
To prevent a paused leader from performing unsafe writes, we use fencing tokens. Every time a lease is granted, a lock server issues an increasing number as a fencing token. The storage engine validates this token on every write and rejects requests with a token lower than the last processed one.

```
 +---------------+                   +---------------+
 | Old Leader    |                   | Lock Service  |
 | (Node A)      |                   | (ZooKeeper)   |
 +-------+-------+                   +-------+-------+
         |                                   |
         |  1. Request Lease                 |
         |==================================>|
         |  2. Grant Lease (Token: 34)       |
         |<----------------------------------|
         |                                   |
         |  [ GC Pause Starts ]              |
         |  [ Lease Expires ]                |
         |                                   |
         |                                   |  3. Grant Lease to Node B (Token: 35)
         |                                   |----------------------------------+
         |                                   |                                  |
         |                                   |<---------------------------------+
         |                                   |
         |  [ GC Pause Ends ]                |
         |  (Node A unaware of expiry)       |
         |                                   |
         |  4. Write with Token 34           |
         |-----------------------------------+==================================+
         |                                   |                                  |
         |                                   |                                  v
         |                                   |                        +------------------+
         |                                   |                        | Shared Storage   |
         |                                   |                        | (Active Token:35)|
         |                                   |                        +--------+---------+
         |                                   |                                 |
         |                                   |  5. REJECTED: Token 34 < 35     |
         |<==================================+<--------------------------------+
```

### Knowledge, Truth, and Lies
Distributed systems cannot rely on a single node to determine what is true. Truth is defined by a majority or quorum of nodes. A single node must accept that its own perspective might be outdated or incorrect.

We usually assume nodes are honest but faulty. Byzantine faults, where nodes actively lie, forge packets, or send malicious messages, require much more complex protocols to solve, and we usually assume they do not occur in private datacenters.

System models help us prove properties of our algorithms. We classify networks into:
- **Synchronous**: Delays have a known upper bound. This is unrealistic in real-world IP networks but useful for theoretical analysis.
- **Partially Synchronous**: The network behaves synchronously most of the time, but occasionally experiences unbounded delays. This is the most practical model for real-world engineering.
- **Asynchronous**: Delays have no upper bound. It is impossible to solve consensus in this model if even a single node can crash.

We also classify node failures into:
- **Crash-stop**: Nodes fail by halting permanently.
- **Crash-recovery**: Nodes can crash, but can recover and resume execution after some time, recovering their persistent disk state.
- **Byzantine**: Nodes can fail in arbitrary ways, including active deception and malicious behavior.

System models help us prove properties of our algorithms. We typically classify these properties into safety and liveness.

A safety property guarantees that nothing bad happens, meaning that once the rule is broken, the violation cannot be undone. For example, ensuring that a database never elects two leaders simultaneously is a safety property.

Conversely, a liveness property asserts that something good eventually happens, meaning it can be temporarily violated but must be satisfied in the future. An example of this is guaranteeing that every sent message is eventually delivered. Distinguishing between these two categories is critical for distributed algorithms. Engineers often design algorithms to preserve safety under all conditions, even when the network is fully asynchronous.

---

### Concrete Worked Examples

#### Example 1: Calculating the Perfect Timeout under Unbounded Network Delay
Let us trace why selecting a static "safe" failure detection timeout is impossible in an asynchronous network.

```
System Assumptions:
- Normal one-way network transit latency: 10ms
- Receiver application processing time: 5ms
- Base round-trip time (RTT): 10ms + 5ms + 10ms = 25ms
- Selected Timeout: 35ms (allowing for 10ms of minor jitter)
```

1. **Sender initiates heartbeat**: The sender sends a heartbeat ping to the receiver.
2. **Congestion hits network switch**: A concurrent batch write in the datacenter saturates the network switch.
   - The heartbeat packet is placed in a switch queue.
   - It waits 50ms in the queue before being forwarded.
3. **Receiver processes heartbeat**: The packet arrives at the receiver after 60ms. The receiver processes it in 5ms and sends an acknowledgment.
4. **Sender triggers timeout**: At 35ms, the sender's clock reaches the timeout limit.
   - The sender has not received the acknowledgment yet.
   - It assumes the receiver is dead.
   - The sender promotes a standby node to become the new leader.
5. **Receiver acknowledgment arrives**: The acknowledgment arrives at the sender at 85ms.
6. **Split-brain corruption occurs**: There are now two active leaders running in the system. Both accept concurrent writes on the same dataset, causing silent data corruption when their writes conflict.
   - Increasing the timeout to 100ms reduces false positives but forces the system to wait 100ms before recovering from a real crash, degrading system availability.

#### Example 2: Last-Write-Wins Clock Skew Disaster
Let us trace how clock skew leads to silent data loss under Last-Write-Wins (LWW) replication across two nodes.

```
Initial Database State:
- Key "status" = "draft"
- Node A Clock: 100ms slow (thinks physical time 1000ms is 900ms)
- Node B Clock: Perfectly synchronized (thinks physical time 1000ms is 1000ms)
```

1. **Write 1 (User 1)**: User 1 writes `status = "sent"` to Node A at physical time T = 1000ms.
   - Node A reads its slow clock: `900ms`.
   - Node A writes: `status = "sent" (Timestamp: 900ms)`.
2. **Write 2 (User 2)**: User 2 writes `status = "archived"` to Node B at physical time T = 1010ms.
   - Node B reads its synchronized clock: `1010ms`.
   - Node B writes: `status = "archived" (Timestamp: 1010ms)`.
3. **Write 3 (User 1)**: User 1 updates `status = "delivered"` to Node A at physical time T = 1020ms.
   - Node A reads its slow clock: `920ms`.
   - Node A writes: `status = "delivered" (Timestamp: 920ms)`.
4. **Database Reconciliation (LWW)**: The nodes synchronize their replicas.
   - The database merges the writes by keeping the value with the highest timestamp.
   - Versions available:
     - `status = "sent" (Timestamp: 900ms)`
     - `status = "delivered" (Timestamp: 920ms)`
     - `status = "archived" (Timestamp: 1010ms)`
   - Result: The database keeps `status = "archived" (Timestamp: 1010ms)` because `1010ms > 920ms`.
   - Outcome: User 1's update to `"delivered"` (the newest physical write at 1020ms) is permanently overwritten by User 2's older physical write (at 1010ms). The update was lost.

#### Example 3: Leader Lease Expiry and the Fencing Token Solution
Let us trace a lease expiry scenario with and without fencing tokens.

```
System State:
- Storage Node holds key "config" = "v1"
- Storage Node tracking: Last_Processed_Token = 33
- Lock Service (ZooKeeper) tracking: Active_Token = 33
```

**Scenario A: Without Fencing Tokens**
1. Node A (Leader) requests a lease from ZooKeeper. ZooKeeper grants Node A a 10-second lease.
2. Node A starts a transaction to update "config" to "v2".
3. **GC Pause hits Node A**: A major garbage collection pause halts all threads on Node A for 12 seconds.
4. **Lease expires**: At 10 seconds, ZooKeeper detects Node A's lease has expired.
   - ZooKeeper grants the leader lease to Node B.
5. **Node B updates config**: Node B writes `config = "v3"` to the Storage Node. The Storage Node updates the key to `"v3"`.
6. **Node A resumes**: The GC pause on Node A ends.
   - Unaware that time has passed, Node A sends its write: `config = "v2"` to the Storage Node.
   - The Storage Node accepts the write.
   - Result: `"v3"` is overwritten by the stale `"v2"`. Node B's valid update is lost.

**Scenario B: With Fencing Tokens**
1. Node A requests a lease from ZooKeeper. ZooKeeper grants the lease and issues **Fencing Token 34**.
2. Node A starts its write transaction, attaching Fencing Token 34.
3. **GC Pause hits Node A**: Node A pauses for 12 seconds.
4. **Lease expires**: ZooKeeper expires Node A's lease.
   - ZooKeeper grants the lease to Node B, issuing **Fencing Token 35**.
5. **Node B updates config**: Node B writes `config = "v3"` with **Token 35** to the Storage Node.
   - The Storage Node checks: `35 > 33` (Last_Processed_Token).
   - The write is accepted. The Storage Node updates `Last_Processed_Token = 35`.
6. **Node A resumes**: Node A sends its write `config = "v2"` with **Token 34** to the Storage Node.
   - The Storage Node checks: `34 < 35` (Last_Processed_Token).
   - The Storage Node rejects the write, returning an error to Node A.
   - Result: The database is protected from stale writes.

## Pros
- Enables horizontal scaling: Splitting workloads across nodes allows systems to handle traffic that would overwhelm a single large server.
- Supports high availability: Creating redundant copies of data across different machines ensures that the system keeps running when some nodes crash.
- Decreases user latency: Deploying servers in multiple geographic regions brings data physically closer to users, speeding up access times.
- Survives localized disasters: Running replica nodes in different power grids or geological zones protects against total datacenter outages.

## Cons
- Introduces partial failure: Having some components fail while others run creates highly complex and unpredictable edge cases.
- Exposes clock synchronization bugs: Unreliable physical clocks make it difficult to determine the exact order of events across servers.
- Suffers from network partitions: Asynchronous networks can drop or delay packets, forcing nodes to make decisions with incomplete information.
- Demands complex testing: Verifying distributed state requires simulating network drops, VM pauses, and split-brain scenarios, which is extremely difficult.

## Alternatives
- **Vertical Scaling (Scale-Up)**: Rather than dealing with multiple servers, you buy a single, larger machine with more CPUs and RAM, which completely eliminates network and clock synchronization issues.
- **Active-Passive Cold Standby**: You run your application on a single primary node and replicate data asynchronously to a backup server that remains offline until a complete manual failover is triggered.
- **Tightly Coupled Supercomputing**: This approach runs workloads on a highly specialized network with hardware-level timing guarantees, which avoids the packet queueing and unbounded delays of commodity ethernet.

## When to use it
Use a distributed architecture when your application demands scalability or fault tolerance that a single physical machine cannot provide. This is necessary for global retail sites, banking networks, global communication platforms, and real-time streaming services.

## When NOT to use it
Avoid distributed systems if your entire dataset fits easily on a single standard database instance and your team cannot afford the complex engineering overhead. For simple web applications, local business tools, and small-scale databases, use a single well-provisioned relational database server instead.

## Key takeaways / mental model
Think of a distributed system as a team of detectives trying to solve a case without a central office. They can only communicate via letters that might get lost, delayed, or delivered in the wrong order. Since they have no master clock, they cannot easily tell who found a clue first. To agree on the truth, they must rely on a majority vote, and any detective who loses contact must be stripped of their authority to prevent conflicting reports.

## Self-check questions
1. Why is a network timeout the only definitive way to detect a remote node failure in an asynchronous network?
2. What are the core differences between a time-of-day clock and a monotonic clock?
3. How does clock skew across different nodes lead to silent data loss in Last-Write-Wins (LWW) replication?
4. Explain the mechanics of a garbage collection pause and how it can cause a node to violate its leader lease.
5. Draw and explain how fencing tokens prevent a paused leader from executing stale writes to shared storage.
6. What is the difference between safety and liveness properties, and why is safety prioritized in database algorithms?
7. When is a synchronous network model appropriate, and why do modern datacenters use asynchronous packet networks instead?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 8
- Prerequisites and baseline replication concepts are in [07-replication-single-leader.md](07-replication-single-leader.md).
