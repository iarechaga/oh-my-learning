---
id: database-internals/13
subject: database-internals
title: "Quorums, Anti-Entropy, and Conflict Resolution in Replicated Stores"
slug: quorums-anti-entropy-and-conflict-resolution
status: drafted
mastery:
seniority: staff
source: Database Internals (Alex Petrov), Part II, Chapter 11 (Leaderless Replication) and Chapter 12 (Anti-Entropy and Dissemination)
prerequisites: [database-internals/12]
created: 2026-08-10
updated: 2026-08-10
---

# Quorums, Anti-Entropy, and Conflict Resolution in Replicated Stores

## TL;DR
Leaderless (Dynamo-style) replicated stores accept writes at any of N replicas rather than funneling everything through a single leader, and use quorum math (requiring W replicas to acknowledge a write and R replicas to agree on a read, with W+R>N) to guarantee reads see the latest write despite no single node holding authoritative state — but this creates genuine conflicts (concurrent writes to different replicas) that must be resolved via mechanisms like vector clocks, last-write-wins, or CRDTs, and any replicas that missed a write must be brought back in sync via anti-entropy processes (read repair, hinted handoff, Merkle-tree comparison).

## The idea
`database-internals/12` covered leader-based replication: one node is authoritative, and its log is the source of truth others copy. That model gives simple, total ordering for writes but has an availability cost: if the leader is unreachable, writes can't proceed (or require a failover, which takes time and coordination). Leaderless replication takes the opposite bet: let *any* replica accept a write, prioritizing availability even during partial network failures, and use mathematical guarantees (quorums) plus reconciliation machinery (anti-entropy) to keep the system's data eventually consistent and reads reliably fresh enough — without ever requiring a single node to be "the" leader.

## How it works

### Quorum math: W + R > N
In a system with N replicas per piece of data, define **W** (write quorum: how many replicas must acknowledge a write before it's considered successful) and **R** (read quorum: how many replicas a read must query and reconcile among). The core guarantee: if **W + R > N**, then any read quorum and any write quorum are guaranteed to overlap in at least one replica — meaning any read is guaranteed to include at least one replica that has the most recent successfully-acknowledged write, so the read can always find (and, via version comparison, identify) the latest value.

**Worked example — quorum overlap guarantee.** N=5, W=3, R=3. W+R=6 > N=5, so the guarantee holds. A write succeeds after 3 of the 5 replicas acknowledge it (say replicas 1, 2, 3). A subsequent read queries any 3 replicas — by the pigeonhole principle, since the write touched 3 out of 5 and the read touches 3 out of 5, and 3+3=6 > 5, at least one replica must be in both sets (e.g. if the read happens to query replicas 3, 4, 5, replica 3 is shared with the write's set). That shared replica has the latest write, so the read is guaranteed to see it (once the read compares versions across the replicas it queried and picks the latest). If instead W=2 and R=2 (W+R=4, not > N=5), there's no such overlap guarantee — a read could query two replicas that both missed the write entirely, silently returning stale data with no way to detect it.

**Worked example — tuning W and R for different goals.** N=3 always. Setting W=1, R=3 makes writes fast (only 1 replica needs to ack) but reads slow/expensive (must query all 3, though this does still satisfy W+R=4>3=N, so correctness holds) — appropriate for a write-heavy, read-light workload. Setting W=3, R=1 makes reads fast (query just 1 replica, since every write already reached all 3) but writes slow and less available (a write fails if even 1 of 3 replicas is unreachable) — appropriate for a read-heavy workload that can tolerate stricter write requirements. A common balanced choice: N=3, W=2, R=2 (W+R=4>3) — both operations only need a majority, and the system tolerates one replica being down for either reads or writes.

### Sloppy quorums and hinted handoff
Strict quorums (always using the same N designated replicas) can become unavailable if enough of those specific nodes are down, even if other healthy nodes exist elsewhere in the cluster. **Sloppy quorums** relax this: if some of a key's designated replicas are unreachable, the write is temporarily accepted by other, non-designated nodes instead, to preserve write availability — with a **hint** stored alongside the write recording "this really belongs to node X, please forward it once X is reachable again."

**Worked example — hinted handoff in action.** Key `K`'s designated replicas are nodes A, B, C, but node C is temporarily down (network partition or crash). A write to `K` needs W=2 acknowledgments; nodes A and B accept normally, but to maintain the full replication factor, node D (not normally responsible for K) accepts a "hinted" copy of the write, tagged "this belongs to C." Once C comes back online, D detects (via periodic hint-checking) that C is reachable again and forwards the hinted write to C, then discards its own hinted copy. This preserves both write availability (the write succeeded despite C being down) and eventual full replication (C eventually gets its copy) — at the cost of a temporary window where C's designated replica set doesn't actually include an up-to-date copy on C itself.

### Conflict resolution: when concurrent writes genuinely disagree
Because any replica can accept writes independently, two clients can concurrently write different values to the same key on different replicas with neither write aware of the other — a genuine conflict, not just staleness. Resolution strategies:
- **Last-write-wins (LWW)**: attach a timestamp to each write; on conflict, the write with the later timestamp wins, and the other is silently discarded. Simple, but requires trusting clock synchronization across nodes (clock skew can cause a genuinely later write to lose to an earlier one with a skewed-forward clock) and always discards one write's data outright, which is unacceptable for some use cases (e.g. silently dropping one of two concurrent shopping-cart additions).
- **Vector clocks**: each replica tracks a per-replica counter for each key, forming a vector like `[A:2, B:1]` that records "this version reflects 2 writes seen by A's causal history and 1 by B's." Comparing two versions' vector clocks can determine if one **causally precedes** the other (safe to discard the older one) or if they're **concurrent** (neither precedes the other — a genuine, irreconcilable-by-timestamp conflict that must be surfaced to the application, or merged).
- **CRDTs (Conflict-free Replicated Data Types)**: data structures specifically designed so that concurrent updates can always be merged deterministically and losslessly (e.g. a grow-only set just unions; a counter that separately tracks increments and decrements per replica and sums them) — avoiding the need to ever pick a "winner" by construction, at the cost of being limited to specific data-structure shapes that support this merge property.

**Worked example — vector clocks detecting a genuine conflict.** A shopping cart starts at version `[A:1]` (created via replica A). Client 1 reads this version and adds an item via replica A, producing `[A:2]`. Concurrently (without having seen A's update), client 2 reads the *original* `[A:1]` version via replica B and adds a different item, producing `[A:1, B:1]`. When these two versions are compared: `[A:2]` has seen everything `[A:1]` had plus one more A-write, and `[A:1,B:1]` has seen the same base plus one more B-write — neither vector dominates the other (A:2 has more A-writes than A:1,B:1's A:1, but A:1,B:1 has a B-write that A:2 has none of) — so the system correctly identifies this as a **concurrent, irreconcilable conflict**, not a simple staleness case, and must either present both versions to the application to merge (the original Dynamo's approach) or apply an application-specific merge function (e.g. union both items into the cart, which is the actually-correct business resolution for a shopping cart, and precisely the kind of merge a CRDT could automate).

### Anti-entropy: read repair and Merkle-tree synchronization
Beyond hinted handoff, leaderless systems need ongoing background mechanisms to catch and fix divergence between replicas that quorum reads/writes alone don't guarantee to fully resolve:
- **Read repair**: when a read queries multiple replicas and detects that some returned stale versions, it opportunistically writes the latest version back to the stale replicas as a side effect of serving the read — piggybacking repair on normal read traffic, but only reaching data that's actually being read (cold, rarely-read data can stay stale indefinitely without other mechanisms).
- **Merkle-tree anti-entropy**: replicas periodically compare a hash tree (Merkle tree) summarizing their entire dataset — comparing just the root hash first (cheap), and only descending into subtrees where hashes differ, to efficiently identify exactly which keys have diverged between two large replicas without transferring or comparing every key individually. This is the mechanism that catches and repairs divergence even for cold data that read repair never touches.

**Worked example — Merkle tree efficiency.** Two replicas each hold 10 million keys. A naive full comparison would require exchanging and comparing 10 million key-value hashes. With a Merkle tree (say, a binary tree of hashes over key ranges, depth ~24 for 10 million leaves), the replicas first compare only their root hashes — if equal, they're fully in sync, done in one comparison. If different, they compare the next level down (2 hashes each), recursing only into the subtrees whose hashes differ — in a typical case where only a small fraction of keys have actually diverged (say, 100 out of 10 million due to a brief partition), this converges to identifying exactly those 100 divergent keys after a logarithmic number of comparison rounds, transferring only a tiny fraction of the data a naive full comparison would have required.

## Pros
- Leaderless replication with quorums provides strong availability — writes and reads can succeed even when some replicas (up to N-W or N-R respectively) are unreachable, with no single point of failure like a leader.
- Quorum math (W+R>N) gives a precise, tunable guarantee for read-your-latest-write consistency without requiring full consensus overhead on every operation.
- Anti-entropy mechanisms (read repair, Merkle trees, hinted handoff) provide layered, complementary paths to eventual consistency, each catching cases the others miss.

## Cons
- Genuine write-write conflicts are a real, unavoidable consequence of accepting writes at multiple independent replicas — the system must have a real conflict-resolution story (LWW, vector clocks, CRDTs, or application-level merge), and getting this wrong (e.g. naive LWW under clock skew) causes silent data loss.
- Quorum guarantees (W+R>N) provide consistency for individual key reads but do not provide the stronger guarantees (like linearizability or serializable multi-key transactions) that leader-based or consensus-based systems can offer.
- Operational complexity: hinted handoff, read repair, and Merkle-tree anti-entropy are all separate subsystems that must be correctly implemented, monitored, and tuned — more moving parts than a single-leader replicated log.

## Alternatives
- **Leader-based replication** (`database-internals/12`) — simpler consistency reasoning (a single ordered log) at the cost of the leader being a single point of unavailability during failover.
- **Consensus-based replication** (`database-internals/15`) — provides stronger consistency guarantees (linearizable, single agreed-upon log) than quorum-based leaderless replication, at the cost of requiring an actual majority quorum to make *any* progress (no sloppy-quorum fallback), trading availability under partition for stronger consistency.

## When to use it
Choose leaderless, quorum-based replication (Dynamo-style: Cassandra, Riak, DynamoDB) when write availability during partial failures and network partitions is the priority, and the application either can tolerate eventual consistency with an explicit conflict-resolution story, or operates on data shapes (counters, sets) that map well to CRDTs.

## When NOT to use it
Avoid leaderless quorum-based systems for workloads that need strong, immediately-consistent multi-key transactions or a strict, single global ordering of operations (e.g. a ledger that must never show two conflicting "final" balances) — those needs are better served by leader-based or consensus-based systems (`database-internals/12`, `database-internals/15`), where conflicts are prevented structurally rather than resolved after the fact.

## Key takeaways / mental model
Picture N librarians who each independently accept returned books (writes) without checking with each other in real time. A reader (read quorum) checks with enough librarians (R of them) that, combined with how many librarians took part in shelving the latest edition (W of them), at least one of the librarians you asked is guaranteed to have that latest edition — simple arithmetic (W+R>N) guarantees the overlap. But if two patrons return conflicting edits to the same book to two different librarians at the same moment, neither librarian knows about the other's edit — someone has to notice this later (vector clocks catching the concurrent conflict) and either pick one, merge them, or ask a person to decide. Periodically, librarians compare inventory summaries (Merkle trees) to catch and fix any books that fell out of sync unnoticed.

## Self-check questions
1. Given N=7, would W=3, R=3 satisfy the quorum overlap guarantee? Compute W+R and explain, using the pigeonhole argument, whether a read is guaranteed to see the latest acknowledged write.
2. Explain why last-write-wins conflict resolution can silently lose data even when both writes were logically important (e.g. two different items added to a cart), and describe how vector clocks detect this case as "concurrent" rather than resolving it silently.
3. Walk through why hinted handoff preserves write availability during a temporary node outage, and explain the window of risk it introduces (what happens if the node holding the hint fails permanently before forwarding it)?
4. A cold dataset (rarely read) has quietly diverged between two replicas due to a network blip that resolved before anyone noticed. Explain why read repair alone would not catch this divergence, and what mechanism would.

## References
- Database Internals (Alex Petrov), Part II, Chapter 11: "Leaderless Replication" and Chapter 12: "Anti-Entropy and Dissemination."
- See also: `database-internals/12` for the leader-based alternative this lesson contrasts with, and `ddia/08` for the DDIA-level leaderless replication and Dynamo-style framing.
