---
id: ddia/09
subject: ddia
title: "Replication Lag and Consistency Guarantees"
slug: replication-lag-and-consistency
status: drafted
mastery:
source: "Designing Data-Intensive Applications (Martin Kleppmann), Chapter 5"
prerequisites: [ddia/07]
created: 2026-06-30
updated: 2026-06-30
---

# Replication Lag and Consistency Guarantees

## TL;DR
Asynchronous replication allows systems to remain highly available but introduces replication lag, causing temporary inconsistency across nodes. This lesson explains three critical consistency guarantees: read-your-writes consistency, monotonic reads, and consistent prefix reads. These guarantees protect users from experiencing confusing anomalies while the system converges toward eventual consistency.

## The idea
Why does eventual consistency feel so frustrating for users? In [07-replication-single-leader.md](07-replication-single-leader.md), we explored how asynchronous replication allows leaders to answer writes immediately while updating followers in the background. While this is great for performance, the delay between a write hitting the leader and appearing on a follower is called replication lag. 

If a user writes data and immediately reads from a lagging follower, they will see stale data, making it look like their write was lost. This divergence can trigger baffling user experiences. To prevent this confusion, we must implement hybrid consistency guarantees. These guarantees are weaker than strict, immediate consensus, but they ensure a coherent user experience despite underlying replication delays.

## How it works
Eventual consistency means that if no new writes occur, all replicas will eventually sync up and become identical. However, when replication lag is high, three classic anomalies emerge. We can prevent each anomaly by implementing a specific consistency guarantee.

---

### 1. Read-Your-Writes Consistency (Read-After-Write)
This guarantee ensures that if a user updates some data, they will always see their own update when they reload the page. It makes no promises about what other users see.

#### The Anomaly
Imagine a user updates their profile picture on a social media site.
1. A user uploads a new profile picture, sending it to the leader.
2. Success is reported to the user immediately.
3. They refresh their profile page immediately.
4. Their read request is routed to a lagging follower replica.
5. Because the replica lacks the new picture, the old profile picture is returned.
6. Confused by this stale view, the user uploads the picture again.

#### The Fix
We can enforce read-your-writes consistency with several techniques:
- **Leader routing for owned data**: Always read things that the user might have modified from the leader. For example, a user's own profile page is read from the leader, while other users' profiles are read from followers.
- **Time-based routing**: Track the timestamp of the user's last write. For a set duration after a write, route all reads from that user to the leader, or block reads on followers until they have caught up to that timestamp.

---

### 2. Monotonic Reads
This guarantee ensures that once a user has seen a certain piece of data, they will not see older versions of that same data on subsequent queries. It prevents time from appearing to run backwards.

#### The Anomaly
Imagine a customer is checking the status of a package delivery.
1. The package status is updated to "Delivered" on the leader.
2. Replica 1 receives the update, and the user queries it to see "Delivered".
3. They refresh the page a moment later.
4. Their second query is routed to Replica 2, which is lagging behind.
5. Seeing "In Transit" on this node makes the user think their package was undelivered.

#### The Fix
To achieve monotonic reads, we must ensure that a user always queries the same replica for their reads.
- **Replica pinning**: Route a user's requests to the same database node using a hash of their user ID rather than choosing nodes randomly. If that replica fails, route the user to a new replica.

---

### 3. Consistent Prefix Reads
This guarantee ensures that if a sequence of writes happens in a specific causal order, anyone reading those writes will see them appear in that exact same order.

#### The Anomaly
This anomaly typically occurs in partitioned databases. Imagine a conversation between two friends:
- Alice: "Are you free for lunch tomorrow?"
- Bob: "Yes, I am!"

If the conversation is replicated asynchronously across partitions, a third observer might see the messages out of order:
1. Alice's message is routed to Partition 1.
2. Bob's reply is routed to Partition 2.
3. Lagging replication allows Bob's reply to reach a follower before Alice's question does.
4. The observer reads from this follower, seeing Bob say "Yes, I am!" first.

#### The Fix
We must preserve causal relationships across partitions:
- **Causal tracking**: Keep track of causal dependencies between writes, ensuring that dependent writes are not displayed before their prerequisites.
- **Single partition routing**: Keep causally related data in the same database partition, which forces the single-leader partition order to maintain the causal sequence.

---

### Relation to Stronger Consistency
These three guarantees are weaker than the strict consistency models covered in later chapters. They do not provide real-time, global coordination across all users. Instead, they are smart compromises designed to run on top of asynchronous systems, offering a good user experience without sacrificing write availability. We will explore stronger guarantees in future lessons on consistency and consensus.

## Pros
- **Improved user experience**: Providing these guarantees prevents users from seeing confusing data regressions or out-of-order histories.
- **High read availability**: We can continue serving reads from any replica without sacrificing write performance.
- **Simpler application logic**: Offloading consistency guarantees to database-level routing prevents developers from writing complex client-side retry rules.
- **Low latency**: We avoid the massive network overhead of global, strong synchronization on every read.

## Cons
- **Increased routing complexity**: Systems must track user IDs, types of content, or causal metadata to route requests to the correct replica.
- **Inefficient load balancing**: Pinning a user to a specific replica can cause uneven load across nodes, reducing the benefit of read scaling.
- **Partial synchronization lag**: Replicas must carry extra causal tracking records, which increases overall network payload size.
- **Weaker than strong consistency**: These guarantees do not prevent concurrent write conflicts from other users, only anomalies for a single user.

## Alternatives
- **Strong consistency (Linearizability)**: The database guarantees that all reads see the absolute latest write globally, as if there was only one copy of the data. This model is preferable for financial transactions but requires slow, expensive coordinator steps.
- **Synchronous replication**: You enforce that all followers must accept a write before replying to a client. This approach is preferable if your node count is low and you cannot tolerate any replication lag whatsoever.

## When to use it
These consistency guarantees are perfect for social media feeds, profile pages, and messaging applications where low-latency reads are vital and users expect logical order but do not need immediate global synchronization.

## When NOT to use it
Avoid relying on these weak guarantees if you are building bank ledger systems, inventory stock counters, or ticket booking systems where two users cannot concurrently claim the same asset. For those systems, reach for strict serializable transactions or strong consensus models instead.

## Key takeaways / mental model
Think of eventual consistency like a group of friends sharing gossip. Alice tells Bob a secret, who then tells Charlie, meaning it takes time for the news to spread. Querying Dave too early will result in him knowing nothing. Read-your-writes is like keeping a diary of what you said so you never contradict yourself. Monotonic reads is like only talking to friends who are at least as caught up on the gossip as the last person you spoke to. Consistent prefix reads ensures you never hear the punchline of a joke before the setup.

## Self-check questions
1. How does pinning a user to a specific replica help achieve monotonic reads, and what happens if that replica fails?
2. What is the difference between read-your-writes consistency and linearizability?
3. Why do consistent prefix read anomalies occur in partitioned databases but rarely in single-partition, single-leader systems?
4. How can a system implement read-after-write consistency using logical timestamp metadata?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 5
