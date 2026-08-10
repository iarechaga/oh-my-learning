---
id: distributed-systems/09
subject: distributed-systems
title: "Fault Tolerance and Reliable Group Communication"
slug: fault-tolerance
status: drafted
mastery: 
seniority: senior
source: "Distributed Systems, 3rd ed. (van Steen & Tanenbaum), Chapter 8"
prerequisites: [distributed-systems/04, distributed-systems/07]
created: 2026-08-10
updated: 2026-08-10
---

# Fault Tolerance and Reliable Group Communication

## TL;DR
Fault tolerance starts with naming the failure model precisely - crash, omission, timing, or the worst case, Byzantine (arbitrary/malicious) failures - because the techniques that tolerate one model can be completely inadequate for another. Reliable multicast and virtual synchrony extend Lesson 04's group-communication guarantees specifically to survive failures mid-broadcast, ensuring replicas stay consistent even when the sender or some recipients crash partway through. Recovery strategies (checkpointing, logging, replay) determine how a failed process rejoins the system with correct state rather than silently corrupting it.

## The idea
Lesson 01 established that partial failure - not crashing all at once, the way a single machine does - is the defining hardship of distributed systems. This lesson turns that observation into engineering practice: to tolerate faults, you first have to be precise about *what kind* of fault you're defending against, because "handles failures" is meaningless without specifying which failures. A system that gracefully handles a node crashing (going silent and never coming back) may be completely undefended against a node that sends *corrupted* messages while still appearing alive - a much harder problem requiring fundamentally different techniques.

Once the failure model is pinned down, this lesson covers two more layers: **reliable group communication** (extending Lesson 04's multicast guarantees so that replicas stay consistent even when failures happen mid-broadcast, not just in the failure-free case), and **recovery** (how a process that failed and restarts gets back to a correct state instead of silently rejoining with stale or corrupted data).

## How it works

### 1. Failure models: naming what can go wrong
Distributed-systems theory organizes failures into a hierarchy of severity, each strictly more permissive (harder to defend against) than the last:

- **Crash failure.** A process simply stops executing and never resumes - no more messages sent, no corrupted state left behind, just silence. This is the easiest model to tolerate and the one most techniques in this subject (leader election in Lesson 07, most consensus discussion in Lesson 10) assume by default unless stated otherwise.
- **Omission failure.** A process fails to send or receive some messages it should have (e.g., a message is dropped due to a buffer overflow or a transient network issue) but otherwise continues functioning correctly. Splits into **send-omission** (fails to send) and **receive-omission** (fails to receive) failures.
- **Timing failure.** A process's response falls outside a specified time bound - either too slow (most common and most relevant to the partial-failure ambiguity from Lesson 01: "is it dead or just late?") or, in principle, too fast for a protocol expecting a minimum delay.
- **Response failure.** A process responds, but the response is *wrong* - either the value is incorrect (**value failure**) or the process deviates from the expected control flow / protocol steps (**state-transition failure**) - critically, the process is still "trying" to follow the protocol, it's just buggy, as opposed to acting maliciously.
- **Arbitrary (Byzantine) failure.** The worst case: a process can do *anything* - send contradictory messages to different peers, claim to have received messages it never sent, actively collude with other faulty processes, or behave in a coordinated malicious way. Named after the "Byzantine Generals Problem," this model makes no assumption at all about what a faulty process will do, including assuming it might be actively adversarial.

| Failure model | What can happen | Relative difficulty to tolerate |
| --- | --- | --- |
| Crash | Process stops, stays silent forever | Easiest |
| Omission | Some messages sent/received are dropped | Moderate |
| Timing | Response arrives too late (or too early) | Moderate (compounds with crash ambiguity) |
| Response (value/state) | Process responds, but incorrectly | Hard |
| Byzantine (arbitrary) | Anything, including malicious/coordinated behavior | Hardest |

**Why the distinction matters in practice.** A protocol designed only to tolerate crash failures (e.g., simple leader-based replication that assumes a follower is either up-to-date or silently dead) can be completely broken by a Byzantine node that actively lies about its state - it might claim to have acknowledged a write it never received, corrupting the replication guarantee in a way the crash-only design never anticipated. Conversely, protocols that tolerate Byzantine failures (Lesson 10 touches on Byzantine fault-tolerant consensus, e.g., in blockchain contexts) are dramatically more expensive - typically requiring `3f+1` nodes to tolerate `f` Byzantine failures (versus `2f+1` for crash failures under many consensus protocols), because you need enough honest votes to outvote any possible coalition of liars. **Most enterprise distributed systems (internal microservices, most databases) explicitly assume crash failures only** - it is a deliberate, usually reasonable simplifying assumption because all nodes are owned and operated by one trusted organization; Byzantine tolerance is reserved for adversarial settings like public blockchains or multi-party systems with no shared trust anchor (foreshadowing Lesson 12's threat model, where "the network is untrusted" gets taken fully seriously).

**Worked example.** A 5-node internal replicated log service assumes crash failures only and uses a simple majority-quorum protocol (3 of 5 nodes must acknowledge a write). This works correctly as long as every node either behaves correctly or goes silent. Now suppose one node has a memory-corruption bug that causes it to occasionally acknowledge writes it never actually persisted (a response/value failure, not quite Byzantine but already outside the crash-only model). The quorum protocol, having assumed crash-only failures, has no mechanism to detect this lying acknowledgment - it simply counts the node's "yes" and proceeds, potentially declaring a write durable when it isn't on that node. This is exactly why the failure model must be chosen deliberately and explicitly, not assumed by default: the protocol's safety guarantee is only as strong as its stated failure-model assumption, and violating that assumption (even accidentally, via a bug rather than malice) breaks the guarantee.

### 2. Reliable multicast under failure
Lesson 04 introduced reliable and (totally) ordered multicast as guarantees for group communication in the failure-free case. This lesson extends that: what happens when the *sender itself* crashes partway through disseminating a message to a group?

**The problem.** A sender begins multicasting message M to a group of 5 replicas, successfully delivering it to replicas 1, 2, and 3, then crashes before reaching replicas 4 and 5. Without a specific protocol addressing this, the group ends up in a genuinely inconsistent state: replicas 1-3 have applied M, replicas 4-5 have not, and there is no natural mechanism for 4 and 5 to ever learn about M (the sender that would have told them is dead).

**Reliable multicast's guarantee, precisely stated:** if *any* correct (non-faulty) process delivers M, then *every* correct process eventually delivers M too - covering exactly the failure-during-broadcast scenario above. A common way to implement this is for each recipient, upon receiving M for the first time, to *itself* relay M to every other member of the group (not just the original sender relaying it) - so even if the original sender dies mid-broadcast, any recipient that did get the message becomes a secondary source for the rest of the group. This trades extra message overhead (each message now potentially gets relayed by every recipient, not just sent once by the origin) for the strong reliability guarantee.

**Virtual synchrony.** A more complete model (developed for systems like Isis and its successors) that combines reliable, ordered multicast with **group membership management**: it guarantees that all members of a group see the same sequence of both messages *and* membership changes (a node joining or leaving/crashing) in the same order, relative to each other - so a message is always delivered "within" a consistent view of who was in the group at the time, and everyone agrees on when that view changed. This matters because a message multicast "to the group" is ambiguous if different members disagree about who's currently in the group (does a message sent just before node 4 crashed count as delivered "to node 4" or not?) - virtual synchrony resolves that ambiguity by making membership-change events themselves part of the totally ordered stream every member observes identically.

**Worked example.** A distributed cache with virtual synchrony has replicas {A, B, C, D, E}. Replica D is about to crash. Virtual synchrony guarantees that every surviving replica (A, B, C, E) agrees on the exact same "view" transition - specifically, they all agree on which multicast messages were delivered *before* D's departure was recognized as part of the {A,B,C,D,E} view, versus which were delivered *after* the new {A,B,C,E} view was established. Without this guarantee, replica A might believe a particular update was delivered to D (and thus expect D, upon recovery, to already have it) while replica B believes the same update was sent *after* D had already left the group (and thus D should not be expected to have it) - a disagreement that would make recovery (the next topic) unreliable, since the recovering D wouldn't know which updates it's missing versus which it was never supposed to receive.

### 3. Recovery: getting a failed process back to a correct state
When a crashed process restarts (or a new process replaces it), it must reach a state consistent with the rest of the system - not stale, not corrupted, not silently missing updates it should have. Three complementary techniques:

- **Checkpointing.** A process periodically saves its full state to stable storage (disk, or a durable external store). On restart, it loads the most recent checkpoint rather than starting from scratch - dramatically reducing recovery time versus replaying the entire history, at the cost of the periodic overhead of taking checkpoints and the storage needed to hold them.
- **Message logging.** In addition to (or instead of) checkpointing state directly, a process logs the messages it has sent and/or received. Combined with a checkpoint, replaying the logged messages since that checkpoint deterministically reconstructs the exact state the process had right before it crashed - useful because logging messages is often cheaper (smaller, append-only writes) than checkpointing full state on every change.
- **Coordinated vs. independent checkpointing.** If every process in a group checkpoints independently, on its own schedule, a naive recovery risks the same inconsistency problem the Chandy-Lamport snapshot algorithm (Lesson 07) was built to solve: process A's checkpoint might reflect having sent a message that process B's checkpoint doesn't reflect having received (or the reverse - an "orphan message" problem where B's checkpoint shows a message received that A's checkpoint shows never sent, an even worse inconsistency). **Coordinated checkpointing** uses a protocol like Chandy-Lamport to ensure the whole group's checkpoints together form a consistent global snapshot, so recovering from them - even recovering *multiple* crashed processes at once - doesn't require expensive cross-checking against every other process's log to untangle causality.

**Worked example.** A stream-processing job with 3 worker nodes uses independent (uncoordinated) checkpointing, each worker saving its own state every 60 seconds on its own clock. Worker 2 crashes and restarts from its checkpoint taken 40 seconds ago. But worker 1's checkpoint (taken on its own independent schedule, 10 seconds before worker 2's) reflects having sent worker 2 a message that worker 2's checkpoint shows as *not yet received* - so on replay, is that message "in flight" and should be resent, or was it actually processed by worker 2 after its checkpoint but the effect wasn't captured? Independent checkpointing alone can't answer this without extra bookkeeping (e.g., logging in-flight messages separately). Switching to coordinated checkpointing (using markers, exactly as in Chandy-Lamport) ensures that when worker 2 recovers, the *entire group's* most recent coordinated checkpoint set is mutually consistent - any message "in flight" at checkpoint time is explicitly recorded as part of the channel state (as in Lesson 07's snapshot algorithm) rather than left ambiguous, so recovery is deterministic and doesn't require the recovering node to reconcile against every other node's independent history.

## Pros
- **Precise failure models**: force explicit reasoning about what a protocol actually defends against, preventing the false confidence of "we're fault tolerant" without specifying against what.
- **Reliable multicast / virtual synchrony**: give strong, well-defined consistency guarantees for group communication even when senders or recipients crash mid-operation, which is essential for correctly replicated systems.
- **Checkpointing and logging**: dramatically reduce recovery time and complexity compared to full replay-from-scratch or (worse) undefined/inconsistent recovery behavior.
- **Coordinated checkpointing**: eliminates the ambiguity of independent, uncoordinated checkpoints, making multi-node recovery deterministic and correct.

## Cons
- **Handling stronger failure models (response/Byzantine)** costs significantly more in nodes, messages, and complexity than crash-only tolerance - and it's easy to accidentally build a crash-only protocol while believing it handles more.
- **Reliable multicast / virtual synchrony**: relay-based reliability and group-view tracking add real message and coordination overhead versus best-effort multicast.
- **Checkpointing**: periodic overhead (pausing or slowing the process to save state) and storage cost; too-infrequent checkpoints mean long recovery/replay times, too-frequent ones hurt steady-state performance.
- **Coordinated checkpointing**: requires a synchronization protocol across the whole group, which itself has cost and complexity (and can be disrupted by the very failures it's trying to help recover from, if not designed carefully).

## Alternatives
- **Stateless recovery (replace, don't restore)** - rather than recovering a crashed process's exact prior state, treat it as disposable: kill it, spin up a fresh replacement with no state, and let it rebuild state from an external source of truth (e.g., re-fetch from a database, rejoin as an empty replica and let normal replication catch it up). Simpler than checkpoint/log recovery when state can be cheaply reconstructed, but not viable when the process *is* the durable source of truth for some data.
- **Byzantine fault-tolerant (BFT) consensus protocols** - rather than accepting crash-only assumptions, use protocols like PBFT (Practical Byzantine Fault Tolerance) or blockchain-style consensus designed from the ground up to tolerate arbitrary/malicious behavior, at the cost of requiring `3f+1` nodes and significantly more message rounds per operation than crash-tolerant equivalents.
- **External orchestration-based recovery** - rather than each process implementing its own checkpoint/recovery logic, delegate to an orchestrator (e.g., Kubernetes) that detects failed instances (via health checks) and restarts/reschedules them, with the application relying on external durable storage (a database, a distributed log) rather than in-process state at all - shifts the recovery problem from "reconstruct this process's exact state" to "make this process stateless and let the state live elsewhere."

## When to use it
- Explicitly choose and document **crash-failure tolerance** as the default assumption for internal systems within a single trusted administrative domain - it's the right cost/benefit trade-off for the overwhelming majority of enterprise distributed systems.
- Use **reliable multicast / virtual synchrony** whenever multiple replicas must apply the same sequence of state-changing operations and must stay consistent even if the operation's originator or some recipients fail mid-broadcast.
- Use **checkpointing plus logging** for any long-running stateful process where full replay-from-the-beginning on every restart would be unacceptably slow.
- Use **coordinated checkpointing** specifically when multiple cooperating processes' states are causally entangled (they exchange messages that affect each other's state) and independent, uncoordinated checkpoints would leave recovery ambiguous.

## When NOT to use it
- Don't over-invest in Byzantine fault tolerance for a system where every node is owned and operated by one trusted organization - the `3f+1` node cost and protocol complexity buy protection against a threat (malicious/compromised internal nodes) that is usually far less likely than the crash and network failures the system already needs to handle, and BFT is not a substitute for proper access control and operational security.
- Don't build independent, uncoordinated checkpointing for tightly-coupled cooperating processes that exchange a lot of messages affecting each other's state - the recovery ambiguity this creates (as in the worked example) tends to cause subtle, hard-to-debug data-loss or duplication bugs; coordinate the checkpoints instead.
- Don't reach for stateful recovery (checkpoint/log/replay) machinery for a process whose state can be trivially and cheaply reconstructed from an external source of truth - stateless replace-on-failure is simpler and has fewer moving parts.

## Key takeaways / mental model
"Fault tolerant" is meaningless without naming the failure model - crash, omission, timing, response, or Byzantine - because each is a strictly harder problem than the last, and a protocol built for one offers no guarantee against the next. Reliable multicast and virtual synchrony extend group-communication guarantees specifically into the failure case, ensuring replicas that received a message stay consistent with replicas that didn't yet, even if the sender dies mid-broadcast, by making group-membership changes themselves part of the ordered, agreed-upon stream. Recovery (checkpointing, logging, and - when processes are causally entangled - coordinating those checkpoints) is how a system gets a failed component back to a *correct*, not just *any*, state. The recurring discipline across all of it: state your assumptions about failure precisely, because the gap between "what we assumed" and "what actually happened" is where the worst production incidents live.

## Self-check questions
1. Explain why a protocol designed to tolerate only crash failures can be broken by a node exhibiting a response (value) failure, using a concrete scenario (not necessarily the one in this lesson).
2. Why does reliable multicast typically require recipients to relay the message to each other, rather than relying solely on the original sender? What specific failure scenario does this defend against?
3. What extra guarantee does virtual synchrony provide beyond plain reliable, ordered multicast, and why does that extra guarantee matter for recovery after a group-membership change?
4. Compare checkpointing and message logging as recovery techniques. Why might a system use both together rather than just one?
5. A team runs uncoordinated, independent checkpointing across three tightly-coupled worker processes that pass messages to each other constantly. Describe a concrete inconsistency their recovery process could hit, and explain how coordinated checkpointing (Chandy-Lamport-style) would prevent it.

## References
- *Distributed Systems*, 3rd ed. (van Steen & Tanenbaum), Chapter 8: Fault Tolerance
- L. Lamport, R. Shostak, M. Pease, "The Byzantine Generals Problem" (1982)
- distributed-systems.net (free companion site for the source book)
