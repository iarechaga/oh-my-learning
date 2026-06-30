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

#### Conflict Avoidance
The simplest way to handle conflicts is to avoid them entirely. If the application can guarantee that all writes for a particular user are always routed to the same datacenter, conflicts cannot occur between different datacenters. From the user's perspective, the system behaves like a single-leader database.
For example, a user in Europe has their account assigned to a Parisian datacenter. All of their profile updates go to the Paris leader. If they travel to Asia, their traffic might still be routed back to Paris over the WAN, or the system might have to handle a transition of their home datacenter, which can lead to concurrency issues.

#### Converging to a Consistent State
If conflicts cannot be avoided, the system must resolve them. All replicas must eventually converge to the exact same value. Database systems use several approaches:
- **Last-Write-Wins (LWW)**: Each write is stamped with a physical clock timestamp. The write with the highest timestamp is kept, and the others are discarded. While simple, LWW is prone to losing data because physical clocks drift and network delays can cause an earlier write to be stamped with a higher time.
- **Higher-ID-Wins**: Each replica or transaction is assigned a unique ID. The update with the highest ID is chosen as the winner. Like LWW, this is a destructive resolution strategy because it throws away updates.
- **Merge Values**: The database concatenates or merges the conflicting values. For example, if one leader changed an address and another changed a phone number, the merged record contains both updates.
- **Record and Resolve**: The database preserves all conflicting versions (called siblings) and reports them to the application layer. The application can then resolve the conflict later, perhaps by asking the user to choose.

#### Automatic Conflict Resolution
To avoid human intervention and the data loss of LWW, modern databases use mathematical structures designed to resolve conflicts automatically:
- **Conflict-Free Replicated Data Types (CRDTs)**: These are special data structures (like registers, counters, or sets) that can be updated concurrently without coordination. They guarantee that if different nodes receive the same set of updates in any order, they will compute the exact same final state.
- **Mergeable Persistent Data Structures**: Similar to Git repositories, these track history as a directed acyclic graph (DAG) of revisions. They merge branches using clear, structural rules.
- **Operational Transformation (OT)**: This is the algorithm behind collaborative applications like Google Docs. When two users make concurrent edits to a document, the system transforms the coordinates of the edits so that the final text is identical on all screens.

#### Multi-Leader Topologies
Leaders must communicate writes to one another. The path that replication logs take defines the topology:
- **Circular Topology**: Each leader receives writes from one neighbor and forwards them to another, forming a ring. A major drawback is that if a single leader node fails, it breaks the replication chain for the rest of the circle.
- **Star Topology**: One central coordinator node receives writes from all leaders and broadcasts them to everyone else. Like the circular model, it has a single point of failure (the hub).
- **All-to-All Topology**: Every leader sends its writes directly to every other leader. This is the most resilient topology because it has no single bottleneck, but it is vulnerable to causality pitfalls.

```
[Circular Topology]      [Star Topology]        [All-to-All Topology]
   L1 ---> L2                L1     L2               L1 <---> L2
   ^        |                  \   /                 ^  \   / ^
   |        v                   v v                  |   \ /  |
   L4 <--- L3                    C                   |    X   |
                                / \                  v   / \  v
                             L3     L4               L4 <---> L3
```

#### Causality Pitfalls and Version Vectors
In an all-to-all topology, network speeds vary. A replication message from Leader A might arrive at Leader B before a prior message from Leader C, even if Leader C's write happened first. This out-of-order delivery violates causality.
To track the causal history of writes across multiple leaders, databases use version vectors. A version vector is a list of counter values, with one counter per replica (e.g., `[LeaderA: 3, LeaderB: 1]`). By comparing these vectors, the database can determine if one write happened before another, or if they occurred concurrently.

---

### Part 2: Leaderless Replication (Dynamo-Style)
Leaderless systems, inspired by Amazon's Dynamo architecture, abandon the concept of a master node entirely. Any replica can accept writes and reads directly from the client.

#### Amazon Dynamo Lineage
Systems like Apache Cassandra, Riak, and Voldemort belong to this lineage. They are optimized for high write availability. They accept writes even during severe network partitions, resolving inconsistencies during the read path or in the background.

#### Quorums and the Condition w + r > n
Consistency in leaderless systems is maintained using quorums.
Suppose we have a cluster of $n$ total replicas.
- $w$ is the write quorum: the number of replicas that must confirm a write before it is considered successful.
- $r$ is the read quorum: the number of replicas we must query when reading data.

As long as we configure these values such that:
$$w + r > n$$
the set of nodes we write to and the set of nodes we read from must overlap by at least one node. This overlapping node contains the most recent value, allowing the client to detect stale data.

Usually, $n$ is configured as an odd number (like 3 or 5), and we set:
$$w = r = \frac{n + 1}{2}$$
For example, in a 5-node cluster, we set $w = 3$ and $r = 3$. Because $3 + 3 = 6 > 5$, we are guaranteed to read from at least one node that received the latest write.

```
                  Replica 1 (Stale)
                /
               /  Replica 2 (Latest) <--- Overlap node (contained in both sets!)
Client <----> *
               \  Replica 3 (Latest)
                \
                  Replica 4 (Stale)
```

#### Detecting Concurrent Writes
In a leaderless system, clients can send writes to different replicas in parallel. To prevent data corruption, replicas must detect when writes occur concurrently:
- **Version Numbers**: Each replica tracks a version number for every key. When a client writes, it includes the version number it is replacing.
- **Version Vectors**: Since there is no single leader to assign sequential numbers, the database uses version vectors across replicas to identify concurrent operations.
- **Siblings**: If two writes are concurrent, the replicas preserve both values as siblings. When a client reads from the database, it receives both siblings and must merge them or let the application select the correct one.

#### Limits of Quorums
Even if $w + r > n$, there are edge cases where a client might read stale data:
- **Sloppy Quorums**: If a network partition occurs and the client cannot reach the primary $n$ replicas, the database might accept writes on temporary "hand-off" nodes outside the primary set. Until these writes are copied back, a read quorum of primary nodes will return stale data.
- **Failed Writes**: If a write succeeds on some replicas but fails to reach the quorum $w$, the database does not roll back those successful writes. A subsequent read might return the partially written value, even though the write was reported as a failure to the client.
- **Clock Drift**: If LWW is used, physical clock drift can cause newer writes to be discarded or older writes to overwrite newer ones.
- **Concurrent Reads and Writes**: If a write is in progress on some replicas while a read is happening on others, it is undefined whether the read will return the old or new value.

#### Repairing Stale Replicas
When nodes go offline and miss writes, they must catch up once they recover. Leaderless databases use two recovery mechanisms:
- **Read Repair**: When a client performs a read quorum and notices that one replica returned an outdated value, the client writes the newer value back to that replica.
- **Anti-Entropy Process**: A background process constantly compares data between replicas. It uses compact Merkle trees to find differences quickly without transmitting the entire dataset over the network.

#### Sloppy Quorums and Hinted Handoff
In a strict quorum, if the client cannot reach $w$ of the designated $n$ replicas, the write fails.
In a sloppy quorum, the database accepts writes on any reachable nodes, even if they are not part of the primary $n$ replicas. These temporary nodes store the write locally with a "hint" in the header indicating where the data belongs. Once the network partition heals, the temporary nodes deliver these writes to the primary replicas. This process is called hinted handoff.

Sloppy quorums increase write availability, but they do not guarantee strict consistency until the hinted handoff completes.

---

### Worked Examples

#### Worked Example 1: Multi-Leader Conflict Avoidance and Resolution
Let's consider a user, Alice, who updates her profile. The database has two leaders: Leader A in New York and Leader B in Frankfurt.

**Scenario A: Conflict Avoidance**
Alice is located in Munich. Her requests are routed to Leader B in Frankfurt.
1. Alice updates her phone number to `+49 123456`. This write is saved on Leader B.
2. The change is replicated to Leader A in the background. No conflict occurs because Alice is the only one modifying her profile, and all her writes go to Leader B.

**Scenario B: Conflict Occurrence and Resolution**
Alice logs into two devices. Her mobile phone connects to Frankfurt (Leader B) over mobile data, while her laptop routes to New York (Leader A) due to a corporate VPN.

At the exact same second:
- **Device 1 (Laptop -> Leader A)**: Alice changes her status to "Working".
- **Device 2 (Phone -> Leader B)**: Alice changes her status to "On Vacation".

```
Leader A (New York)              Leader B (Frankfurt)
------------------------------------------------------
Receives status = "Working"      Receives status = "On Vacation"
Assigns Vector: [A:1, B:0]       Assigns Vector: [A:0, B:1]
```

How does the system resolve this conflict?
1. **Using Last-Write-Wins (LWW)**:
   Suppose Leader A's clock is 50ms behind Leader B's clock due to clock drift.
   - Write A gets timestamp `12:00:00.050`.
   - Write B gets timestamp `12:00:00.100`.
   Even if Write A actually happened slightly later in real physical time, Leader B's write is kept because its timestamp is higher. Alice's status becomes "On Vacation". The update "Working" is silently discarded.
2. **Using Record and Resolve (Siblings)**:
   The database detects that the version vectors `[A:1, B:0]` and `[A:0, B:1]` are concurrent because neither dominates the other.
   Replicas keep both values: `{"Working", "On Vacation"}`.
   When Alice's app reads her profile, it receives both values. The application's UI displays: *"You have concurrent updates from two devices. Please choose which status is correct."*

#### Worked Example 2: Leaderless Quorum Calculations and Limitations
Let's configure a leaderless cluster with $n = 5$ replicas: Node 1, Node 2, Node 3, Node 4, and Node 5.
We choose a write quorum of $w = 3$ and a read quorum of $r = 3$.

**Scenario A: Normal Quorum Operation**
1. A client writes a key `user_99` with value `{"role": "admin"}`.
2. The write request is sent to all 5 nodes.
3. Node 1, Node 2, and Node 3 write the value successfully and return ACKs. Node 4 and Node 5 are slow due to network congestion and do not respond in time.
4. Since $w = 3$ nodes acknowledged the write, the client receives a success response.
5. Later, another client wants to read `user_99`. It queries Node 3, Node 4, and Node 5.
6. The nodes return:
   - Node 3: `{"role": "admin"}`, Version 1
   - Node 4: `{"role": "user"}`, Version 0 (stale)
   - Node 5: `{"role": "user"}`, Version 0 (stale)
7. The client compares the versions, identifies Node 3's value as the latest, and returns `{"role": "admin"}` to the application.
8. The client performs a **Read Repair**: it writes `{"role": "admin"}` with Version 1 to Node 4 and Node 5 so they catch up.

**Scenario B: Quorum Limitation (Failed Write)**
1. A client attempts to update `user_99` to `{"role": "guest"}` (Version 2).
2. The write goes to all nodes. Node 1 and Node 2 accept it.
3. The remaining three nodes (Node 3, Node 4, Node 5) suffer a network disruption and reject the write.
4. The database reports a write failure to the client because only 2 nodes accepted the write, which is less than $w = 3$.
5. However, Node 1 and Node 2 **do not roll back** their changes.
6. A subsequent client reads from Node 1, Node 2, and Node 3.
7. Node 1 and Node 2 return the "failed" Version 2 value, while Node 3 returns Version 1.
8. The client sees Version 2 as the latest and returns it to the user.
This illustrates a major limitation: even though a write failed, its partial updates remain visible, violating transactional isolation guarantees.

#### Worked Example 3: Version Vectors and Concurrent Writes
Let's trace three replicas: Node A, Node B, and Node C. We want to see how version vectors track concurrent writes and resolve them.
Initially, the key `cart` has an empty value on all nodes, with version vector `[A:0, B:0, C:0]`.

```
Time  Client Action     Target Node   Resulting State & Version Vector
-----------------------------------------------------------------------------------------
T=1   Client 1 adds     Node A        Node A saves cart=["milk"], vector=[A:1, B:0, C:0]
      "milk"
T=2   Client 2 reads    Node A        Client 2 receives ["milk"], vector=[A:1, B:0, C:0]
      from Node A
T=3   Client 2 adds     Node B        Node B receives write with vector [A:1, B:0, C:0].
      "eggs"                          Node B sees that this write succeeds Client 1's
                                      write. Node B saves cart=["milk", "eggs"]
                                      with vector [A:1, B:1, C:0].
T=4   Client 3 (unaware Node C        Client 3 writes cart=["bread"] with vector
      of T=1 or T=3)                  [A:0, B:0, C:0] because it read the empty state.
      adds "bread"                    Node C saves cart=["bread"] with vector
                                      [A:0, B:0, C:1].
```

At $T=5$, a client performs a read quorum ($r = 3$) querying Node A, Node B, and Node C.
The client receives:
- From Node A: `["milk"]` with vector `[A:1, B:0, C:0]` (This is obsolete, because Node B's vector `[A:1, B:1, C:0]` dominates it).
- From Node B: `["milk", "eggs"]` with vector `[A:1, B:1, C:0]`.
- From Node C: `["bread"]` with vector `[A:0, B:0, C:1]`.

The client compares the vectors of Node B and Node C:
- Node B's vector `[A:1, B:1, C:0]` does not dominate Node C's vector `[A:0, B:0, C:1]` because Node B has higher counters for A and B, but Node C has a higher counter for C.
- Therefore, these writes are concurrent.
- The client returns both values as siblings: `["milk", "eggs"]` and `["bread"]`.
- The application merges the siblings by taking the union of the two shopping carts: `["milk", "eggs", "bread"]`. It then writes this merged value back to the database with a version vector of `[A:1, B:1, C:1]`. This updates all replicas and resolves the conflict.

---

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
5. Explain how a version vector is used to determine whether two writes are concurrent or if one causally succeeded the other.
6. In Worked Example 2, why does a failed write still leave partial updates visible on some replicas, and how does this affect transaction isolation?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 5
