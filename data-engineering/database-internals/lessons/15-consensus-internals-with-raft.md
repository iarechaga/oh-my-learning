---
id: database-internals/15
subject: database-internals
title: "Consensus Internals with Raft and Log Agreement Mechanics"
slug: consensus-internals-with-raft
status: drafted
mastery:
seniority: staff
source: Database Internals (Alex Petrov), Part II, Chapter 14 (Consistency and Consensus)
prerequisites: [database-internals/12, database-internals/13]
created: 2026-08-10
updated: 2026-08-10
---

# Consensus Internals with Raft and Log Agreement Mechanics

## TL;DR
Raft is a consensus protocol that lets a cluster of nodes agree on a single, ordered, replicated log despite node crashes and network partitions, using a leader-election mechanism (terms and randomized timeouts) plus a log-replication rule requiring a majority quorum to commit any entry. Understanding Raft's actual mechanics — not just "it achieves consensus" — is what lets you reason about split-brain prevention, why a minority partition can't make progress, and what really happens during a leader failover.

## The idea
`database-internals/12` and `database-internals/13` covered replication schemes (leader-based log shipping, leaderless quorums) that either require operational care to avoid split-brain (two nodes both believing they're leader) or accept eventual consistency with explicit conflict resolution. Consensus protocols like Raft close this gap structurally: they guarantee that at any given time, the cluster can have **at most one** node that's genuinely authorized to act as leader (enforced by the protocol itself, not by external coordination discipline), and that a log entry is only ever considered committed once a **majority** of nodes have durably stored it — making split-brain and lost-committed-writes provably impossible as long as a majority of nodes remain reachable.

## How it works

### Terms: a logical clock for detecting stale leaders
Raft divides time into **terms**, each identified by a monotonically increasing integer. At most one leader can be elected per term (an election either succeeds with exactly one leader, or fails and a new term begins with a new election attempt). Every message in Raft carries the sender's current term number, and any node that sees a message with a higher term than its own immediately updates its own term and steps down from any leadership role it held — this is the core mechanism that prevents an old, isolated leader from continuing to act authoritatively after a new leader has been elected in a higher term.

**Worked example — a stale leader stepping down.** Leader L1 is elected in term 5. A network partition isolates L1 from the majority of the cluster. The majority, no longer hearing L1's heartbeats, times out and elects a new leader L2 in term 6. When the partition heals and L1 rejoins, it receives a message (or a heartbeat/request) carrying term 6 — higher than its own term 5 — and Raft's rule forces L1 to immediately recognize it's stale, step down from believing it's leader, and update its term to 6. This is what prevents split-brain: L1 cannot simply keep acting as leader after being isolated, because the term number is a built-in, unforgeable signal of "a more recent leadership decision has been made," and every node is required to defer to the higher term.

### Leader election: randomized timeouts prevent split votes
Every follower node runs an **election timeout** (randomized, e.g. 150-300ms, deliberately randomized so nodes don't all time out simultaneously) — if a follower doesn't hear from a leader within that window, it assumes the leader is dead, increments its term, votes for itself, and requests votes from every other node. A node grants its vote to at most one candidate per term (first-come, first-served within that term), and a candidate becomes leader once it receives votes from a **majority** of the cluster.

**Worked example — why randomized timeouts matter.** If every node used the exact same fixed timeout, a leader failure could cause every follower to time out and start an election at nearly the same instant, splitting the vote across multiple simultaneous candidates (each getting some votes, none reaching a majority) — forcing a retry, which without randomization could split again, repeatedly. With randomized timeouts, one follower almost always times out meaningfully earlier than the others, requests votes before anyone else starts a competing election, and typically wins a clean majority before a second candidate even times out — making split votes rare in practice despite being possible in principle (Raft handles the rare split-vote case by simply retrying with a fresh random timeout and a new term).

### Log replication: how an entry becomes committed
Once elected, a leader accepts client writes as new log entries, appended locally first, then sent to every follower via `AppendEntries` RPCs. A log entry is considered **committed** only once it has been replicated to (durably stored by) a **majority** of nodes, including the leader itself. Only after an entry is committed does the leader apply it to its own state machine and respond to the client — and only then does the leader inform followers (via subsequent `AppendEntries` calls' commit-index field) that they may also apply it.

**Worked example — committing an entry with a 5-node cluster.** Leader L (part of a 5-node cluster) receives a client write, appends it to its own log at index 42, and sends `AppendEntries` to all 4 followers. Followers F1 and F2 durably persist and acknowledge it quickly; F3 acknowledges a moment later; F4 is slow/unreachable and hasn't responded yet. Once L has confirmation from itself plus F1, F2, and F3 (4 out of 5, a majority — though technically just 3 acks plus the leader's own copy, i.e. 3 non-leader acks needed for a majority of 5 total counting the leader, so L + 2 followers = 3, already a majority), the entry at index 42 is committed, regardless of F4's status. L can now apply it and acknowledge the client. F4, once it reconnects, will eventually receive and apply index 42 too, but its slowness never blocked commitment — this is precisely why Raft only needs a **majority**, not all nodes, to make progress: it tolerates a minority of nodes being slow or down without stalling.

### Why a minority partition cannot make progress
If a network partition splits a 5-node cluster into a group of 2 and a group of 3, only the group of 3 (a majority) can elect a leader and commit new entries — any node in the group of 2 that tries to become leader can never gather a majority of votes (it can get at most 2, needing 3), so it remains a candidate indefinitely (retrying elections that keep failing) without ever becoming an authoritative leader. This is the structural mechanism, not an operational convention, that prevents split-brain: it's mathematically impossible for two disjoint groups to *both* contain a majority of the same fixed cluster size, so at most one side of any partition can ever elect a leader and make progress — the other side is correctly, safely unavailable until the partition heals.

**Worked example — the minority side's experience.** In the 5-node cluster split into {A, B} and {C, D, E}, suppose C is elected leader within the majority group and continues committing new entries normally. Meanwhile, A and B (the minority) cannot elect a leader (neither can get 3 votes from only 2 possible voters) and cannot commit any writes a client might send them — they correctly report themselves as unavailable for writes (some implementations still serve stale reads from a minority node if the application explicitly accepts that risk, but that's a deliberate consistency trade-off layered on top, not Raft's default safe behavior). This is availability sacrificed deliberately in exchange for consistency (per the CAP-theorem framing covered at the DDIA level in `ddia/12`) — Raft chooses correctness over availability during a partition, by design.

### Log matching and catching up a lagging follower
Raft guarantees a **log matching property**: if two logs contain an entry with the same index and term, every entry before that point is identical in both logs — this lets a leader efficiently determine exactly where a follower's log diverges (if at all) using a simple backward-search-then-forward-fill protocol during `AppendEntries`, and safely overwrite any conflicting (uncommitted, necessarily stale) entries in the follower's log with the leader's authoritative version, bringing the follower fully in sync.

## Pros
- Provides a genuinely strong consistency guarantee (linearizable replicated log) with a structural, mathematically-provable prevention of split-brain, not merely an operational best-practice.
- Well-understood, widely implemented (etcd, Consul, CockroachDB, many others), and considerably easier to reason about and implement correctly than its predecessor Paxos, thanks to Raft's explicit design goal of understandability.
- Tolerates up to a minority of nodes being slow, crashed, or partitioned away without stalling progress, as long as a majority remains reachable.

## Cons
- Every committed write requires a round trip to a majority of nodes before acknowledgment — meaningfully higher write latency than asynchronous or even quorum-based leaderless replication (`database-internals/12`, `database-internals/13`), especially across geographically distant nodes.
- Availability is deliberately sacrificed during a network partition for the minority side — a system needing to stay writable even when it can't reach a majority (accepting eventual reconciliation instead) needs a different model entirely (leaderless with conflict resolution, `database-internals/13`).
- Adding or removing cluster members (reconfiguration) is a genuinely subtle operation in Raft, requiring careful protocol extensions (joint consensus or single-server changes) to avoid a window where two disjoint majorities could theoretically both believe they're authoritative.

## Alternatives
- **Paxos** — the original, more general consensus protocol Raft was explicitly designed to be a more understandable alternative to; equivalent in the guarantees it can provide, but notoriously harder to implement correctly due to its more abstract formulation.
- **Leaderless quorum replication** (`database-internals/13`) — sacrifices Raft's strong linearizable consistency for higher write availability during partitions, appropriate when eventual consistency with explicit conflict resolution is an acceptable trade.
- **Primary-backup replication without consensus** (`database-internals/12`) — simpler and lower-latency than Raft for the common case, but relies on external failover coordination (or accepts a real split-brain risk) rather than Raft's structural guarantee.

## When to use it
Use Raft (or an equivalent consensus protocol) specifically for the control-plane decisions described in `database-internals/11` — cluster membership, leader election for partitions, configuration/schema agreement — and for any data path that genuinely requires linearizable, single-ordered-log consistency (e.g. a distributed lock service, a metadata store multiple systems depend on for correctness).

## When NOT to use it
Don't use Raft (or full consensus) for the high-throughput hot data path of a system where quorum-based or asynchronous replication's weaker guarantees are an acceptable trade for lower latency and higher availability — paying consensus's majority-round-trip latency cost on every single write, for data that doesn't need linearizability, is a common and avoidable performance mistake.

## Key takeaways / mental model
Think of Raft as a strict town-hall voting process: every decision (log entry) needs a show of hands from more than half the town before it's official, and every meeting has a numbered session (term) so that if someone shows up late claiming to still be running last session's meeting, everyone knows to ignore them in favor of whoever's running the current numbered session. If the town splits into two groups that can't talk to each other, only the group with more than half the townspeople can hold a valid vote — the smaller group, however confident, simply cannot pass anything official until they reconnect, by the plain arithmetic of what "majority" means.

## Self-check questions
1. Walk through exactly why an isolated former leader (like L1 in the worked example) cannot cause split-brain when the partition heals, tying your answer specifically to the term mechanism rather than just saying "Raft prevents it."
2. In a 7-node Raft cluster, what is the minimum number of nodes that must be reachable and agreeing for the cluster to elect a leader and commit new entries? What happens to write availability if exactly that many minus one are reachable?
3. Explain why randomized (rather than fixed) election timeouts meaningfully reduce the likelihood of repeated split votes, even though split votes remain possible in principle.
4. A team wants sub-millisecond write latency for a globally-distributed application and is considering Raft across regions. Using this lesson's cons and "when NOT to use it" guidance, explain why this is likely a poor fit, and what alternative (from `database-internals/12` or `database-internals/13`) might serve the latency goal better, with what consistency trade-off.

## References
- Database Internals (Alex Petrov), Part II, Chapter 14: "Consistency and Consensus."
- See also: `database-internals/12` and `database-internals/13` for the replication models Raft's stronger guarantees are contrasted against, and `ddia/13` for the DDIA-level consensus and coordination framing.
