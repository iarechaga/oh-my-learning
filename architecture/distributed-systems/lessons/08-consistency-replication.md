---
id: distributed-systems/08
subject: distributed-systems
title: "Consistency and Replication Models"
slug: consistency-replication
status: drafted
mastery: 
seniority: senior
source: "Distributed Systems, 3rd ed. (van Steen & Tanenbaum), Chapter 7"
prerequisites: [distributed-systems/06, distributed-systems/07, ddia/13]
created: 2026-08-10
updated: 2026-08-10
---

# Consistency and Replication Models

## TL;DR
Replication (keeping multiple copies of data across nodes) buys availability and performance, but forces a choice about what guarantees those copies must uphold relative to each other. Data-centric consistency models (strict, sequential, causal, eventual) specify how the *system as a whole* behaves regardless of who's asking; client-centric models (monotonic reads/writes, read-your-writes, writes-follow-reads) specify what guarantees an *individual client's own session* gets, which is often a cheaper and more practically useful promise than a system-wide guarantee. This lesson is the formal-theory counterpart to `ddia/13`'s treatment of the same territory; where that lesson builds up from linearizability toward consensus, this one organizes the full spectrum of models van Steen and Tanenbaum define and pairs each with the replication mechanism that realizes it.

## The idea
Replicating data across nodes (Lesson 01's core motivation: fault tolerance and performance) immediately raises a question no single-copy system has to answer: **when a client reads, which copy's value should it see, and how "fresh" must that value be relative to the most recent write, anywhere in the system?** Answer that question strictly ("always the absolute latest write, everywhere, instantly") and you've bought yourself a very strong guarantee that is expensive to implement (every read may need to coordinate with every write) and hostile to availability under a network partition (Lesson 09). Answer it loosely ("whatever a replica happens to have, we'll converge eventually") and you've bought cheap, highly available reads at the cost of clients sometimes seeing stale or contradictory data.

Consistency models exist to name specific points on this spectrum precisely, so that application developers and system designers can reason about exactly what guarantee they're getting (and paying for) rather than an vague, unstated assumption. This lesson organizes the spectrum in two families - **data-centric** (properties of the system, independent of any one client) and **client-centric** (properties of what one client's session observes) - and connects each to concrete replication strategies.

## How it works

### 1. Why replicate at all: the trade-off this lesson formalizes
Replication serves two purposes: **availability/fault tolerance** (if one replica dies, others still serve) and **performance** (spread read load across replicas; place replicas near users to cut latency). Both benefits scale with how loosely you're willing to keep replicas synchronized - the tighter the consistency guarantee, the more coordination replicas need on every write (and often every read too), which directly taxes both latency and availability. This is the same trade-off CAP/PACELC formalize (`system-design/03`); this lesson goes one level more precise, giving named models rather than just "consistent" vs. "available."

### 2. Data-centric consistency models
These models describe what *any* client, at any time, is guaranteed to observe about the system's global history of operations - a property of the system, not of a particular client's session.

**Strict consistency.** The strongest, purest theoretical model: any read returns the result of the most recent write, where "most recent" is defined by absolute, real, global time. This requires all processes to share an instantaneous, perfectly synchronized clock - which Lesson 06 already established is impossible. Strict consistency is a theoretical ceiling, not an implementable target; it exists mainly as the baseline every weaker model is defined relative to.

**Sequential consistency.** Weaker than strict, but still very strong and useful: the result of any execution is the same as if all operations from all processes were executed in *some* sequential order, and each process's own operations appear in that order in the sequence they were issued by that process (program order is preserved per-process, but there's no requirement that this sequential order match real/wall-clock time across processes). This is exactly what you'd get if every operation, from every client, funneled through a single serializing point.

**Worked example: sequential consistency.** Two processes, P1 and P2, both write to and read from a shared replicated variable `x` (initially 0).

```
P1:  write(x, 1)  ------------------  read(x)
P2:            write(x, 2)  ------------------  read(x)
```

Under sequential consistency, *any* global ordering of these four operations is acceptable, as long as each process's own two operations stay in the order it issued them (P1's write(x,1) must precede P1's read in the agreed sequence; P2's write(x,2) must precede P2's read). So a valid sequential-consistency execution could be: `write(x,1) [P1], write(x,2) [P2], read(x)->2 [P1], read(x)->2 [P2]` - both reads see 2, which is fine even though, in real wall-clock time, P1's read might have physically happened before P2's write completed; sequential consistency doesn't care about real time, only that *some* consistent global order exists in which program order per-process is respected. What sequential consistency forbids is P1 reading 2 and P2 later reading 1 with no consistent single ordering that explains both (that would imply two different, contradictory total orders).

**Causal consistency.** Weaker still, and directly built on Lesson 06's happens-before relation: writes that are *causally related* (one happened-before the other, e.g., because of message passing between the writers) must be seen by everyone in that same causal order; writes with *no* causal relationship (concurrent writes, per Lesson 06's vector-clock definition) may be seen in different orders by different processes. This is exactly the guarantee vector clocks (Lesson 06) are built to support.

**Worked example: causal consistency.** A social-media-style system: user A posts "Going on vacation!" (write W1). User B, having seen W1, replies "Have fun!" (write W2 - causally dependent on W1, since B's reply only makes sense after reading A's post). A third user, C, must never see W2 (the reply) without also seeing W1 (the original post) first - that would be causally nonsensical ("Have fun!" replying to nothing visible). But a completely unrelated post from user D, made around the same time with no causal link to W1 or W2, may legitimately appear before or after W1/W2 for different viewers - causal consistency makes no promise about ordering unrelated writes, only about preserving cause-and-effect chains.

**Eventual consistency.** The weakest commonly-used model: if no new writes occur, all replicas will *eventually* converge to the same value - but with no bound on how long "eventually" takes, and no guarantee about what any single read sees in the meantime (it might see any previously-written value, in any order, from any replica). This is the model behind Dynamo-style systems and DNS's caching-and-TTL behavior (Lesson 05): cheap, highly available, but requires the application to tolerate (or explicitly resolve, as with vector clocks) temporarily divergent views.

| Model | Global real-time order required? | Per-process order preserved? | Causally-related writes ordered consistently? | Convergence guaranteed? |
| --- | --- | --- | --- | --- |
| Strict | Yes (theoretical only) | Yes | Yes | N/A (always instantly consistent) |
| Sequential | No | Yes | Yes (implied) | Yes, immediately (single agreed order) |
| Causal | No | Yes | Yes | Eventually, respecting causal order |
| Eventual | No | Not guaranteed | Not guaranteed | Eventually, with no ordering promise otherwise |

### 3. Client-centric consistency models
Data-centric models describe what *the system* guarantees to any observer. Client-centric models instead describe what a *single client's own session* is guaranteed to see, which is often exactly what an application actually needs - and much cheaper to provide than a strong system-wide guarantee, because it only requires tracking one client's own history, not coordinating across every client.

- **Monotonic reads** - if a client has read a value at some point, any subsequent read by that same client will never return an *older* value than what it already saw. (Without this: a user refreshes their inbox and briefly sees an email disappear that they'd already read moments ago, because the second read hit a replica that hadn't caught up yet.)
- **Monotonic writes** - a client's writes are applied in the order that client issued them, everywhere. (Without this: a user updates their profile picture twice in quick succession, and due to replication races, the *older* picture ends up as the final stored value.)
- **Read-your-writes** - a client that just wrote a value will always see that write (or a newer one) in its own subsequent reads - never an older value than what it itself just wrote. (Without this: a user posts a comment, refreshes the page, and doesn't see their own comment because the read hit a replica the write hadn't reached yet - a famously jarring bug in early web applications built on eventually consistent stores.)
- **Writes-follow-reads** - if a client has read a value, any subsequent write by that client is guaranteed to be ordered after (build upon) whatever it read, everywhere. (Without this: a user reads a forum post, replies to it, and somewhere in the system the reply could end up visible *before* the original post it's replying to, because the write wasn't causally anchored to the read that motivated it - a specific case of the causal-consistency worked example above, but scoped to guaranteeing it for one client's own read-then-write sequence.)

**Worked example: read-your-writes in practice.** A user on an eventually consistent, multi-region social platform updates their bio, and the write lands on the region-local replica (say, US-East). The user immediately reloads their profile page, and the request happens to route to a different region's replica (EU-West) that hasn't yet received the update via inter-region replication (which might take a few hundred milliseconds to a few seconds). Without a read-your-writes guarantee, the user sees their *old* bio and reasonably assumes the save failed - a real, common UX bug in globally distributed systems. Fixing this doesn't require full strong consistency system-wide (expensive); it requires a much narrower guarantee: route this specific client's reads to a replica known to have absorbed this specific client's writes (e.g., by "sticky" session routing to the write's region for some window of time, or by having the client track and present a version/timestamp its next read must be at least as new as). This is exactly why client-centric models are so practically valuable - they solve the user-visible bug cheaply, without paying for a system-wide strong-consistency guarantee that the application never actually needed.

### 4. Replication strategies that implement these models
Consistency models are promises; replication strategies are the mechanisms that keep (or don't keep) those promises.

- **Primary-backup (single-leader) replication.** All writes go to one designated primary, which then propagates them to backup replicas. If replication to backups is *synchronous* (the primary waits for backups to acknowledge before confirming the write to the client), you get strong consistency (reads from any acknowledged-caught-up replica are safe) at the cost of write latency and availability (a slow/unreachable backup blocks writes). If replication is *asynchronous* (the primary confirms immediately, backups catch up afterward), writes are fast, but reads from a lagging backup can return stale data - you've dropped to something closer to eventual consistency for backup reads, even though the primary itself is always strictly up to date.
- **Multi-primary (multi-leader) replication.** Multiple nodes can each accept writes independently, then propagate them to each other. This improves write availability and can reduce latency (write to your nearest primary), but concurrent writes to different primaries for the same data item can conflict - exactly the scenario vector clocks (Lesson 06) are designed to detect, requiring an explicit conflict-resolution policy (last-writer-wins, application-level merge, or surfacing the conflict to the user).
- **Leaderless (quorum-based) replication.** No node is designated primary; any replica can accept a write, and reads/writes use quorums (a write is considered successful once W replicas acknowledge it; a read consults R replicas and returns the most recent value among them) - classically Dynamo-style systems. Choosing `W + R > N` (where N is the total replica count) guarantees every read quorum overlaps with every write quorum by at least one replica, which is what gives you a *read-your-writes*-style guarantee even without a single primary - though true strong consistency still requires careful conflict handling on genuinely concurrent writes.

**Worked example: quorum tuning.** A system with N=5 replicas per key can tune W and R to trade consistency strength against latency/availability. Setting W=3, R=3 (`W+R=6 > N=5`) guarantees read/write quorum overlap - any read is guaranteed to see the latest acknowledged write, at the cost of needing 3 of 5 replicas to respond for both reads and writes, hurting availability if 3 replicas aren't reachable. Setting W=1, R=1 maximizes availability and minimizes latency (only one replica needs to respond either way) but gives no overlap guarantee at all - a read can easily miss the most recent write, landing you close to eventual consistency. This single tunable dial - which most Dynamo-derived systems expose directly - is a very concrete, practical embodiment of the abstract consistency-vs-availability trade-off this whole lesson is about.

## Pros
- **Strong models (strict/sequential)**: simplest for application developers to reason about - "just works" the way a single-copy system would, no surprising stale reads.
- **Causal consistency**: preserves the intuitive cause-and-effect ordering users expect (replies after posts, acknowledgments after requests) while still allowing far more concurrency/availability than sequential consistency.
- **Eventual consistency**: maximizes availability and minimizes latency - reads and writes can be served by whatever replica is closest/healthiest, with no cross-replica coordination required on the hot path.
- **Client-centric models**: solve the specific, common UX problems (stale own-writes, regressing reads) cheaply, without paying for full system-wide strong consistency.

## Cons
- **Strong models (strict/sequential)**: expensive to implement (coordination on every operation) and directly hostile to availability under network partitions (Lesson 09) - strict consistency isn't even implementable in practice.
- **Causal consistency**: still requires tracking causal metadata (vector clocks or similar) across the system, adding real bookkeeping overhead relative to plain eventual consistency.
- **Eventual consistency**: applications must explicitly tolerate (or resolve) temporarily divergent, out-of-order, or conflicting views - pushing real complexity onto application code (or requiring conflict-resolution logic) that a stronger model would have hidden.
- **Client-centric models**: only guarantee something to the client whose own session is being tracked - they say nothing about what two *different* clients might simultaneously observe, so they don't substitute for a data-centric guarantee when cross-client consistency actually matters.

## Alternatives
- **CRDTs (Conflict-free Replicated Data Types)** - data structures specifically designed so that concurrent, conflicting updates always merge deterministically without coordination or explicit conflict resolution (e.g., a grow-only counter, an OR-set). A more specialized alternative to general-purpose eventual consistency plus ad hoc conflict resolution, at the cost of only working for specific data-structure shapes.
- **Linearizability via consensus (Lesson 10)** - rather than choosing a weaker consistency model to avoid coordination cost, some systems pay the coordination cost directly by routing every operation through a consensus protocol (e.g., Raft-backed systems), getting the strongest practical guarantee (linearizability, close to sequential consistency plus real-time ordering) at the throughput/latency cost of consensus on every write.
- **Session-scoped consistency via explicit versioning** - instead of relying on infrastructure-level guarantees (sticky routing, client-centric models baked into the replication layer), applications can carry an explicit version/timestamp token with each request and require reads to be "at least as new as" that token - a portable, storage-agnostic way to implement read-your-writes-style guarantees at the application layer.

## When to use it
- Use **strong (sequential-level) consistency** for data where stale or out-of-order reads cause real, hard-to-recover harm - financial ledgers, inventory counts that must never oversell, coordination/lock state.
- Use **causal consistency** for interactive, social, or collaborative applications where preserving cause-and-effect (replies after posts, edits after prior edits) matters to users, but full global ordering of unrelated events doesn't.
- Use **eventual consistency** for data where availability and low latency matter more than immediate freshness, and either conflicts are rare/mergeable or the application can tolerate brief staleness - caches, presence/status indicators, non-critical counters, product catalogs.
- Use **client-centric guarantees (read-your-writes, monotonic reads)** as a targeted, cheap fix whenever the specific user-visible symptom is "I don't see my own change" or "things seem to go backward for me" - almost always cheaper than reaching for full system-wide strong consistency.

## When NOT to use it
- Don't default to strong/sequential consistency for data that doesn't need it - you'll pay real latency and availability costs (and, under partition, may have to sacrifice availability entirely per CAP) for a guarantee your application never actually required.
- Don't rely on eventual consistency for data where even brief inconsistency causes real damage (double-spending a balance, overselling the last unit of inventory) - the "eventually" in eventual consistency provides no protection during the window before convergence.
- Don't assume client-centric guarantees (read-your-writes) solve cross-client consistency problems - they only protect the guarantee-holding client's own view; two different users can still observe the system in different, unreconciled states.

## Key takeaways / mental model
Consistency models are promises about *what an observer is guaranteed to see*, and every promise costs something in coordination, latency, or availability - there is no free strongest option. Data-centric models (strict > sequential > causal > eventual, in decreasing strength and decreasing cost) describe system-wide guarantees; client-centric models (read-your-writes, monotonic reads/writes, writes-follow-reads) describe cheaper, narrower guarantees scoped to one client's own session, and often solve the actual user-visible bug more directly than a system-wide guarantee would. Replication strategy (primary-backup, multi-primary, leaderless/quorum) is the mechanism; the consistency model is the promise that mechanism is configured to keep. Always ask, for any given piece of data: what's the cheapest model that still prevents real harm if violated?

## Self-check questions
1. Explain the difference between sequential consistency and causal consistency using a concrete example where sequential consistency would forbid an ordering that causal consistency would permit.
2. Why is strict consistency a theoretical ceiling rather than an implementable target? Connect your answer back to Lesson 06's discussion of physical clock synchronization.
3. A user updates their profile picture, refreshes the page, and briefly still sees the old picture before it "catches up." Which client-centric consistency guarantee is missing, and how would you fix it without moving the whole system to strong consistency?
4. In a Dynamo-style quorum system with N=5 replicas, explain why setting W=2, R=2 fails to guarantee read-after-write consistency, while W=3, R=3 succeeds. What's the general rule?
5. Compare primary-backup, multi-primary, and leaderless replication along the axis of "what happens to writes when the primary/a node is unreachable." Which consistency models does each naturally support well, and which does each struggle with?

## References
- *Distributed Systems*, 3rd ed. (van Steen & Tanenbaum), Chapter 7: Consistency and Replication
- `ddia/13` (Consistency and Consensus) - practical treatment of linearizability, causal consistency, and consensus
- `system-design/03` (CAP, PACELC, and Consensus in Practice) - the availability/consistency trade-off applied to system design
- distributed-systems.net (free companion site for the source book)
