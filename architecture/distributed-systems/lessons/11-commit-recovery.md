---
id: distributed-systems/11
subject: distributed-systems
title: "Distributed Commit and Recovery"
slug: commit-recovery
status: drafted
mastery: 
seniority: senior
source: "Distributed Systems, 3rd ed. (van Steen & Tanenbaum), Chapter 8"
prerequisites: [distributed-systems/09, distributed-systems/10]
created: 2026-08-10
updated: 2026-08-10
---

# Distributed Commit and Recovery

## TL;DR
Two-phase commit (2PC) lets multiple independent resource managers agree to atomically commit or abort a distributed transaction, but it has a fundamental weakness: if the coordinator crashes at the wrong moment, participants that voted "yes" are stuck blocked, unable to safely commit or abort on their own, until the coordinator recovers. Three-phase commit (3PC) adds an extra phase specifically to eliminate that blocking window under crash failures (though not under network partitions), at the cost of an extra round trip on every transaction. Understanding exactly *why* 2PC blocks - and exactly what 3PC does and doesn't fix - is the core of this lesson.

## The idea
Lesson 08 covered how to keep *replicated copies* of the same data consistent. This lesson covers a related but distinct problem: how do you make a single logical transaction that spans *multiple independent resource managers* (e.g., a transaction touching a payments database and a separate inventory database, or a transaction whose writes must land atomically on several partition shards) either commit **everywhere** or abort **everywhere** - never partially commit on some participants and abort on others, which would leave the system in a state no single-machine transaction could ever produce?

This is the **atomic commitment problem**, and it's a close cousin of consensus (Lesson 10): instead of agreeing on an arbitrary value, the participants must agree specifically on "commit" or "abort," and every participant's individual constraint (can it actually commit? did its local work succeed?) must be respected - a participant that can't commit must be able to force the outcome to "abort" for everyone, which is a stronger requirement than general consensus (where any proposed value is acceptable, not just what individual participants can "agree to").

## How it works

### 1. Two-Phase Commit (2PC): the mechanics
2PC involves one **coordinator** (often the process that initiated the transaction) and multiple **participants** (each resource manager involved, e.g., each database shard touched by the transaction). It proceeds in two phases:

**Phase 1: Voting (prepare) phase.**
1. The coordinator sends `PREPARE` to every participant.
2. Each participant does whatever local work is needed to be *certain* it can commit if asked (e.g., acquiring locks, writing its intended changes to a durable local log) - but does **not** actually commit yet.
3. Each participant replies `VOTE-COMMIT` (if it's ready and able to commit) or `VOTE-ABORT` (if it cannot, for any reason - a constraint violation, a local failure, insufficient resources).

**Phase 2: Commit/abort (decision) phase.**
4. The coordinator collects all votes. If **every** participant voted `VOTE-COMMIT`, the coordinator decides `GLOBAL-COMMIT` and sends `COMMIT` to everyone. If **any** participant voted `VOTE-ABORT` (or failed to respond within a timeout), the coordinator decides `GLOBAL-ABORT` and sends `ABORT` to everyone.
5. Each participant, upon receiving the coordinator's decision, actually commits or aborts its local work accordingly, and acknowledges.

```
Coordinator          Participant A       Participant B
     |-- PREPARE ------->|                    |
     |-- PREPARE --------------------------->  |
     |<- VOTE-COMMIT -----|                    |
     |<- VOTE-COMMIT ------------------------  |
     |  (all voted commit -> decide GLOBAL-COMMIT)
     |-- COMMIT -------->|                    |
     |-- COMMIT --------------------------->  |
     |<- ACK -------------|                    |
     |<- ACK ---------------------------------  |
```

**The crucial detail: once a participant votes `VOTE-COMMIT`, it has surrendered its unilateral right to abort.** It must be *durably prepared* to commit (all necessary local work done and logged) before voting yes, precisely because the coordinator might decide `GLOBAL-COMMIT` based on that vote, and the participant must honor that decision even if it crashes and restarts in the meantime (recovering from its durable log to the "prepared" state and waiting for the coordinator's decision). This is the mechanism that makes atomicity possible - but it's also exactly where the protocol's weakness comes from.

### 2. The blocking problem: what happens when the coordinator crashes
Consider a participant that has voted `VOTE-COMMIT` (Phase 1 complete) and is now waiting for the coordinator's Phase 2 decision - call this the **prepared/uncertain state**. If the coordinator crashes at exactly this moment, before sending the decision to any participant, that participant is stuck: it cannot unilaterally commit (the coordinator might have decided `GLOBAL-ABORT` based on some other participant's vote it hasn't heard about) and it cannot unilaterally abort (the coordinator might have decided `GLOBAL-COMMIT`, and if this participant then aborted while others committed, the transaction would be inconsistent across participants - exactly the atomicity violation the protocol exists to prevent). **The participant must wait until the coordinator recovers** (or until it can somehow learn the decision from another source), holding whatever locks it acquired during Phase 1 the entire time - and per Lesson 01's central pitfall, the participant cannot even distinguish "coordinator is slow" from "coordinator is permanently dead," so it has no principled way to decide how long to wait before giving up (and giving up is unsafe anyway, per the reasoning above).

**Worked example.** A distributed transaction touches Participant A (an inventory shard) and Participant B (a payments shard), coordinated by process C. Both A and B receive `PREPARE`, do their local prepare work (A reserves the inventory item and logs "prepared," B reserves the payment authorization and logs "prepared"), and both reply `VOTE-COMMIT`. At this exact moment - after receiving both votes but before sending out the decision - coordinator C crashes (its host loses power). A and B are now both sitting in the prepared state, each holding locks on their respective data (A's inventory row is locked, unavailable for other transactions; B's payment authorization is held). Neither A nor B can safely proceed: if A independently decided to commit and B independently decided to abort (or vice versa), the transaction would end up partially applied - inventory reserved but payment never captured, or payment captured but inventory never actually reserved - a serious correctness bug. Both A and B are **blocked**, holding their locks (and therefore blocking any other transaction that needs those same locked resources), until C restarts, consults its own durable log to recall what decision it had reached (or, if it crashed *before* deciding, it must re-poll A and B for their votes and only then decide), and finally communicates the decision. If C's disk is also lost, or C never restarts, A and B may be blocked indefinitely, requiring manual operator intervention (a "heuristic decision," in transaction-processing terminology - manually forcing a commit or abort based on human judgment, at the very real risk of that judgment being wrong).

This blocking scenario is 2PC's single most consequential weakness: **it is not fault-tolerant during exactly the window that matters most** - after votes are cast but before the decision is disseminated - and the cost of that window failing is locks held indefinitely across multiple systems, degrading availability far beyond just the failed transaction itself.

### 3. Three-Phase Commit (3PC): closing the blocking window
3PC addresses 2PC's blocking problem specifically for **crash failures** (not network partitions - see the limitation below) by splitting the decision phase into two steps, ensuring that by the time any participant might need to make a unilateral decision, there's enough information distributed among the surviving participants to do so safely without risking disagreement.

**Phase 1: Voting** - identical to 2PC's Phase 1 (`PREPARE` -> `VOTE-COMMIT`/`VOTE-ABORT`).

**Phase 2: Pre-commit.** If all participants voted commit, the coordinator sends `PRE-COMMIT` (rather than jumping straight to the final `COMMIT` as in 2PC) and waits for participants to acknowledge. This step's purpose is subtle but crucial: receiving a `PRE-COMMIT` tells a participant that **every participant has voted commit** - meaning it is now safe for any participant that later loses contact with the coordinator to conclude, with certainty, that the eventual decision will be commit (since a `GLOBAL-ABORT` could never happen once all votes were unanimous "commit" and everyone has been told so via pre-commit).

**Phase 3: Commit.** Once the coordinator has collected pre-commit acknowledgments from everyone, it sends the final `COMMIT`.

**Why this eliminates blocking under crash failures.** If the coordinator crashes *after* some participant received `PRE-COMMIT` but before the final `COMMIT`, the surviving participants can safely proceed themselves: since at least one of them received `PRE-COMMIT`, they know (by the meaning of that message) that all participants voted commit, so they can collectively decide to commit without waiting for the crashed coordinator - a new coordinator (elected via Lesson 07's election algorithms) can query the surviving participants' states and safely conclude `COMMIT` if *any* surviving participant reports having received `PRE-COMMIT` (or already committed), or safely conclude `ABORT` if none did (meaning the failure happened before unanimity was even established, so aborting cannot contradict any already-made commit decision). Contrast this with 2PC, where a participant merely knowing "I voted commit" tells it nothing about what *other* participants voted - it genuinely cannot know if abort is still possible, which is precisely what forces the blocking wait.

**Worked example.** Using the same A/B/C scenario as before, but now with 3PC: A and B vote commit (Phase 1). C sends `PRE-COMMIT` to both; suppose only A receives and acknowledges it before C crashes (B never receives `PRE-COMMIT` due to a coincidental network delay, and C crashes before retrying). The surviving participants, A and B, now coordinate among themselves (via a recovery protocol - typically electing a temporary coordinator among themselves): A reports "I received PRE-COMMIT," which is enough information for the group to safely conclude the transaction must commit (since PRE-COMMIT could only have been sent after unanimous commit votes) - B is told to commit as well, even though B itself never received the message directly from the now-crashed C. No indefinite blocking occurred; the surviving participants had enough distributed information to reach a safe, unblocked decision on their own.

### 4. 3PC's own cost and its remaining limitation
3PC is not a free upgrade over 2PC - it pays for eliminating the blocking window with a real, permanent cost on every single transaction: **an extra round trip** (the additional Pre-commit phase), meaning higher latency for every transaction, all the time, in exchange for better behavior during the relatively rare event of a coordinator crash. This is a classic distributed-systems trade-off: pay a small, constant cost always, to avoid a large, rare cost sometimes.

**The remaining limitation: 3PC assumes no network partitions**, only clean crash failures with eventual recovery. If a network partition splits the participants into two groups that can't communicate with each other (but each group can still communicate internally and might each believe it can proceed independently), 3PC's blocking-avoidance guarantee breaks down: it's possible for each side of the partition to reach a *different* decision (one side concluding commit based on partial pre-commit information, the other side concluding abort), which would violate atomicity - exactly the kind of split-brain scenario that a genuine consensus protocol (Lesson 10) is needed to prevent rigorously. This is why 3PC, despite solving the specific blocking problem it targets, never achieved the widespread production adoption that plain 2PC (accepted with its blocking risk, mitigated operationally) or consensus-based alternatives did - it solves a real problem but not the *general* problem, while adding permanent latency cost, a trade-off many production systems judged not worth it.

### 5. Recovery after failure: what a restarting participant/coordinator must do
Both protocols require participants and coordinators to maintain a **durable log** of protocol state (votes cast, decisions received) specifically so that a crashed process, upon restart, can determine where it left off rather than guessing:
- A **participant** that restarts and finds itself logged as "prepared" (voted commit, awaiting decision) must contact the coordinator (or, in 3PC, other participants) to learn the actual outcome - it cannot decide on its own, for exactly the reasons explored above.
- A **participant** that restarts and finds no log entry for a given transaction (it crashed before even receiving `PREPARE`, or the transaction is unknown to it) can safely conclude the transaction never involved it in a state requiring recovery.
- A **coordinator** that restarts must consult its own log: if it had already recorded a `GLOBAL-COMMIT` or `GLOBAL-ABORT` decision before crashing, it simply re-sends that decision to any participants that haven't acknowledged it yet (participants must tolerate receiving the same decision multiple times - idempotency, echoing Lesson 04's discussion of delivery semantics). If it crashed *before* reaching a decision (still mid-Phase-1), it must re-poll participants for their votes and proceed from there.

**Worked example: why the durable log order matters.** A participant, in order to be safe, must write "prepared, voted commit" to durable storage **before** sending its `VOTE-COMMIT` reply, not after. If it sent the vote first and crashed before persisting the log entry, it would restart with no memory of having voted commit - and might, incorrectly, feel free to unilaterally decide something (or simply not know it owes the coordinator continued availability to receive a decision), while the coordinator (having received and acted on the vote) might have already told other participants to commit. The ordering discipline - durably log the intended state transition *before* communicating it - is a general pattern that recurs throughout distributed commit and recovery protocols, and getting the order backwards is a classic, subtle source of real production data-corruption bugs.

## Pros
- **2PC**: guarantees atomicity (all-or-nothing) across independently-owned resource managers, which is essential whenever a logical transaction genuinely spans multiple independent systems; relatively simple to reason about in the failure-free case.
- **3PC**: eliminates the indefinite-blocking window under crash failures, meaning locks aren't held indefinitely across a coordinator outage - a meaningful availability improvement over 2PC for that specific failure scenario.

## Cons
- **2PC**: the blocking problem is severe in practice - a coordinator crash at the wrong moment holds locks across every participant indefinitely, degrading availability far beyond the single failed transaction, and requires either coordinator recovery or risky manual intervention.
- **3PC**: adds a permanent extra round trip to every transaction (real latency cost, always paid); does not solve the general problem under network partitions (only under clean crash-and-eventual-recovery failures), which limits how much protection it actually buys in real, partition-prone networks.
- **Both**: require careful, correctly-ordered durable logging by every participant and the coordinator - getting the log-before-reply ordering wrong reintroduces exactly the corruption risk the protocol exists to prevent.

## Alternatives
- **Consensus-based atomic commit** - rather than a dedicated 2PC/3PC coordinator, use a full consensus protocol (Lesson 10) to agree on the commit/abort decision, gaining the stronger safety guarantees consensus provides (correct even under network partitions, not just crashes) at the cost of running a heavier-weight protocol for what might otherwise be a simpler transaction.
- **Sagas (compensating transactions)** - rather than atomic all-or-nothing commitment across services, break a distributed transaction into a sequence of local transactions, each with a corresponding compensating action to "undo" it if a later step fails; avoids 2PC/3PC's locking and blocking issues entirely, at the cost of giving up atomicity in the strict sense (the system passes through genuinely intermediate, partially-applied states that other transactions might observe) - `hard-parts/11`'s treatment of the eight saga patterns covers this alternative in depth.
- **Avoiding distributed transactions altogether** - the most common real-world "solution": design service boundaries and data ownership so that most operations only need a single local transaction (within one database/service), reserving true multi-participant atomic commitment for the rare cases that genuinely require it.

## When to use it
- Use **2PC** when a transaction genuinely must span multiple independent resource managers atomically, failures are relatively rare, and the operational team can tolerate (and has a plan for) occasional blocking incidents requiring coordinator recovery or manual intervention - common inside a single, well-controlled infrastructure (e.g., a database's internal distributed-transaction coordinator across its own shards).
- Use **3PC** (or note it's rarely deployed in practice) when the extra latency cost is acceptable and the failure model genuinely is "crash and eventual recovery" without significant network-partition risk - a narrower set of circumstances than 2PC's use case, which is part of why 3PC saw limited real-world adoption.

## When NOT to use it
- Don't use 2PC or 3PC across service boundaries owned by different teams or organizations where you can't guarantee every participant's availability and correct recovery behavior - the blocking risk (2PC) or partition-safety gap (3PC) becomes a genuine cross-team operational hazard; prefer sagas or redesigning boundaries to avoid the need for distributed atomic commitment.
- Don't reach for distributed atomic commit at all when the actual requirement can be satisfied by a single local transaction through better service/data-ownership boundaries - this is almost always the better fix, and is exactly what `hard-parts`'s treatment of data ownership and service granularity is about.
- Don't assume 3PC "solves" the coordinator-crash problem in a network with realistic partition risk - it only solves the narrower crash-only case; for genuine partition tolerance, use a real consensus protocol instead.

## Key takeaways / mental model
Two-phase commit buys atomicity across independent participants by having each one durably commit to "I can and will do this if told to" before the coordinator decides - but that commitment is exactly what creates the blocking window: once prepared, a participant cannot safely decide on its own, and a coordinator crash at that moment strands every participant holding locks indefinitely. Three-phase commit closes that window by making the "everyone voted yes" fact itself durable and disseminated (via pre-commit) before the final decision, so surviving participants can safely conclude the outcome without the coordinator - but it pays for that with a permanent extra round trip and still doesn't protect against network partitions, only crashes. The deepest lesson underneath both protocols: distributed atomic commitment is expensive precisely because it requires every participant to give up its own autonomy at exactly the point where the coordinator becomes a single point of failure - which is why, in practice, teams work hard to avoid needing distributed transactions at all, reaching for sagas or better service boundaries instead.

## Self-check questions
1. Walk through exactly why a participant that has voted `VOTE-COMMIT` in 2PC cannot safely decide to abort on its own if it stops hearing from the coordinator, even after waiting a long time.
2. Explain precisely what information the Pre-commit phase in 3PC gives surviving participants that 2PC's Phase 1 does not, and why that information is what allows them to avoid blocking after a coordinator crash.
3. Why does 3PC still fail to guarantee atomicity under a network partition, even though it solves the blocking problem under crash failures? What would actually be needed to handle partitions safely?
4. A participant's implementation writes its `VOTE-COMMIT` reply to the network *before* durably logging that it voted commit. Describe a crash scenario where this ordering bug causes a real correctness problem.
5. A team is designing a checkout flow that touches an inventory service and a payments service, owned by different teams. Would you recommend 2PC, 3PC, or a saga-based approach, and why?

## References
- *Distributed Systems*, 3rd ed. (van Steen & Tanenbaum), Chapter 8: Fault Tolerance (distributed commit sections)
- `hard-parts/11` (The Eight Saga Patterns) - the compensating-transaction alternative to atomic distributed commit
- distributed-systems.net (free companion site for the source book)
