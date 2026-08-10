---
id: distributed-systems/07
subject: distributed-systems
title: "Coordination: Election, Gossip, Distributed Events"
slug: coordination
status: drafted
mastery: 
seniority: senior
source: "Distributed Systems, 3rd ed. (van Steen & Tanenbaum), Chapter 6"
prerequisites: [distributed-systems/06]
created: 2026-08-10
updated: 2026-08-10
---

# Coordination: Election, Gossip, Distributed Events

## TL;DR
Coordination protocols let a group of independent nodes agree on things without shared memory: election algorithms (bully, ring) pick a single coordinator when the current one is suspected dead; gossip protocols disseminate information across a large, churning population by having nodes randomly exchange state with a few peers at a time, achieving eventual, probabilistic convergence without any central broadcaster; and distributed event ordering/detection builds on the logical-clock machinery from Lesson 06 to answer questions like "has this computation terminated?" or "in what order did these events really happen?" across the whole system.

## The idea
Lesson 06 gave us tools to *order* events and detect concurrency. This lesson uses those tools (and some new ones) to solve three concrete coordination problems that come up constantly in real systems:

1. **Who is in charge right now?** When a coordinator (Lesson 06's centralized mutual exclusion, Lesson 08's leader-based replication, Lesson 11's transaction coordinator) fails, someone new must take over - **election algorithms** decide who.
2. **How does information spread reliably across a large, dynamic set of nodes without a central broadcaster?** - **gossip (epidemic) protocols** answer this with randomized, peer-to-peer dissemination.
3. **How do you reason about global properties of a running distributed computation** - e.g., has it terminated, or what is a consistent snapshot of its state - when no single node can see the whole system at once? - **distributed event detection** techniques answer this.

All three are direct, practical answers to the same root problem from Lesson 01: no shared memory, no shared clock, and no way to instantaneously know another node's state.

## How it works

### 1. Election algorithms: picking a coordinator
Many algorithms in this subject (centralized mutual exclusion, leader-based replication, two-phase commit) assume a single coordinator exists. Election algorithms answer: **when the current coordinator is suspected to have failed, how does the group agree on a new one, using only messages, with no shared state?**

**The Bully algorithm.** Every process has a unique, comparable ID (e.g., a process number), and the convention is "the process with the highest ID becomes coordinator." When a process P notices the coordinator is unresponsive (via timeout - the same crash/slow ambiguity from Lesson 01 applies here too), it starts an election:
1. P sends an `ELECTION` message to every process with a *higher* ID than itself.
2. If no one responds within a timeout, P declares itself the winner and broadcasts `COORDINATOR` to everyone.
3. If a higher-ID process responds with `OK`, P drops out and waits to hear who the new coordinator is; the responding higher-ID process takes over running the election itself (sending its own `ELECTION` messages further up).
4. This recurses until the single highest-ID *live* process wins and broadcasts `COORDINATOR` to all.

The name "Bully" comes from the fact that a higher-ID process always bullies its way into overriding a lower-ID process's election attempt. It's simple and always converges to the highest-ID surviving process, but it is message-heavy in the worst case (O(N^2) messages if many processes detect failure and start elections simultaneously) and biased: the "biggest" process always wins, even if it's a poor choice for other reasons (e.g., it's on an overloaded or network-disadvantaged machine).

**Worked example.** Five processes, P1 through P5 (P5 currently the coordinator), and P5 crashes. P2 notices first (its periodic health-check to P5 times out) and starts an election: it sends `ELECTION` to P3, P4, P5. P5 is dead (no reply). P3 and P4 both reply `OK` and each starts their own election in turn. P3 sends `ELECTION` to P4 and P5; P4 replies `OK`, P5 is dead. P3 drops out, waiting. P4 sends `ELECTION` to P5 (the only higher ID); no reply. P4, hearing nothing from anyone higher, declares itself coordinator and broadcasts `COORDINATOR` to P1, P2, P3, P5. P1, P2, P3 update their records: P4 is now coordinator. Notice the redundant work - P2's original election indirectly triggered P3's and P4's separate election attempts, which is exactly the source of the algorithm's worst-case O(N^2) message cost when detection isn't perfectly staggered.

**The Ring algorithm.** Processes are logically arranged in a ring (each knows its successor). A process noticing the coordinator is down builds an `ELECTION` message containing its own ID and forwards it to its successor. Each process receiving the message compares the ID inside against its own: if its own ID is larger, it replaces the ID in the message before forwarding; if smaller, it forwards unchanged; either way, it forwards the message onward around the ring. Once the message travels all the way around and returns to the process that started it, that process finds its own ID still in the message only if it turned out to be the largest at some previous forwarding decision - more precisely, the process recognizes the message has completed a full circle (e.g., by including the original initiator's ID separately) and then broadcasts a second `COORDINATOR` message around the ring announcing the winner (the largest ID seen).

Ring election is more predictable in message cost (roughly `2N` messages for a full circle plus the announcement pass, regardless of how many processes detect failure simultaneously) than the Bully algorithm's worst case, but it depends on the ring topology staying correctly maintained (every process must correctly know its successor, including adapting when a process is found to be dead partway around the ring - which requires the ring-repair logic to skip over it).

| Algorithm | Message complexity (typical) | Assumes | Weakness |
| --- | --- | --- | --- |
| Bully | O(N^2) worst case, O(N) best case | Every process can message every other directly | High-ID process always wins even if a poor choice; redundant concurrent elections |
| Ring | ~2N (roughly linear) | A maintained logical ring topology | Depends on ring integrity; slower to converge if the ring is large |

### 2. Gossip (epidemic) protocols: dissemination without a broadcaster
Election algorithms assume the group is small enough and stable enough that direct messaging (to every peer, or around a maintained ring) is feasible. At much larger scale, with high churn (nodes joining and leaving constantly) and no reliable membership list, **gossip protocols** take a completely different approach, modeled explicitly on how epidemics spread through a population.

**The core mechanism.** Each node periodically picks a small, random subset of peers (often just one or a handful) and exchanges state with them - "here's what I know, what do you know?" Information that is genuinely new to a node gets absorbed and, on the node's next gossip round, propagated further to its own randomly chosen peers. There is no central coordinator deciding who talks to whom; the randomness is exactly what makes the protocol scale and tolerate churn - no single node's failure can prevent information from spreading, because it wasn't relying on any single path.

Three common gossip patterns:
- **Push gossip** - a node with new information actively pushes it to random peers.
- **Pull gossip** - a node periodically asks a random peer "what's new?" and pulls updates.
- **Push-pull gossip** - nodes exchange in both directions during each contact, which converges fastest (this is what most production systems, e.g., Cassandra's gossip-based membership protocol, actually use).

**Convergence is probabilistic, not guaranteed by a deadline** - but it converges *fast*, in expectation, because of the same mathematics that makes epidemics spread exponentially: after round `k`, roughly `2^k` nodes know a given piece of information (each "infected" node infects a new random peer each round), so full convergence across N nodes takes on the order of `log(N)` rounds in expectation. This is dramatically more scalable than any scheme requiring a central broadcaster to individually reach every node.

**Worked example.** A cluster of 1,000 nodes uses gossip to disseminate cluster-membership changes (a new node joining). At round 0, only the new node and the single "seed" node it contacted know about the join - 2 nodes informed. At round 1, each of those 2 nodes gossips to 1 random peer each, so up to 4 nodes are now informed (assuming no repeat contacts). At round 2, up to 8; round 3, up to 16... following `2^k`. After about 10 rounds, `2^10 = 1024`, comfortably covering all 1,000 nodes (accounting for some redundant/repeated contacts slowing this slightly in practice, real convergence is typically closer to `O(log N)` rounds with a modest constant factor, e.g. a few dozen rounds for thousands of nodes, still vastly better than direct broadcast to every node from one source). If gossip runs every second, the entire 1,000-node cluster learns about the new member within roughly 10-30 seconds - no central component had to individually notify 1,000 nodes, and the protocol keeps working even if a large fraction of nodes are unreachable at any given moment, since information simply routes around them via other random contacts.

**Anti-entropy vs. rumor-mongering.** Gossip protocols come in two flavors with different trade-offs: **anti-entropy** gossip periodically compares and reconciles *entire* state between two nodes (guarantees eventual full consistency, but is expensive per exchange if state is large), while **rumor-mongering** gossip only propagates specific recent updates ("rumors") and stops actively spreading a rumor once it seems to have saturated the network (cheap per exchange, but a small chance some node never receives a given update and needs anti-entropy as a periodic backstop). Production systems (e.g., Cassandra, Amazon's Dynamo-inspired systems) typically run rumor-mongering for fast day-to-day propagation and periodic anti-entropy as a correctness safety net.

### 3. Distributed event ordering and detection
Beyond ordering individual events (Lesson 06), coordination sometimes needs to answer global questions about a *whole distributed computation* - questions no single node can answer just by looking at its own state.

**Distributed termination detection.** In a computation spread across many nodes passing messages to each other, how does *any* node know the entire computation has finished, when a node only ever sees its own local state (idle or busy) and cannot directly see whether messages are still in flight elsewhere? A classic solution (the Dijkstra-Scholten / "token" style algorithms) has an idle node pass a marker token around a ring; if the token makes a full circuit and every node reports having been idle the whole time *and* no messages were sent that could still be in flight, termination is confirmed. The subtlety is exactly the "in-flight message" problem: a node can look idle locally while a message it sent earlier is still traveling toward another node that will wake up and become busy again - naive local-idle checks alone are not sufficient.

**Consistent global snapshots (the Chandy-Lamport algorithm).** Sometimes you need a consistent picture of the *entire* distributed system's state at "roughly the same moment" - e.g., for checkpointing or debugging - even though there is no shared clock to define "the same moment" precisely. The Chandy-Lamport snapshot algorithm has an initiating process record its own local state and send a special `MARKER` message on all its outgoing channels; any process receiving a `MARKER` for the first time immediately records its own local state, then forwards `MARKER`s on all of its own outgoing channels, and also starts recording any messages that arrive on other channels *before* their corresponding marker arrives (these are the messages "in flight" during the snapshot, and are recorded as part of the channel's state). The result is a **consistent cut** - a global snapshot that, while not corresponding to any single physical instant, is causally consistent (it could have actually occurred, respecting happens-before) and therefore useful for correct checkpointing or debugging.

**Worked example.** Two processes, P1 and P2, connected by channels in both directions, are running a computation where P1 periodically sends P2 tokens representing work items. P1 initiates a snapshot: it records its own state (say, "5 tokens sent so far") and sends a MARKER on the P1->P2 channel. Suppose, just before the MARKER, P1 had also sent a regular message ("token #6") that is still in flight when P2 receives the MARKER. P2, upon receiving the MARKER, records its own local state and then continues receiving messages on the P1->P2 channel until it explicitly recognizes "token #6" arriving *before* the logical marker point in causal terms is already accounted for - the algorithm records "token #6" as part of the *channel state* (a message in transit at snapshot time), not as part of either process's local state. This is exactly why naive snapshotting (just asking every node "what's your state right now?" without accounting for messages en route) produces an inconsistent picture: P1's snapshot might not show token #6 as sent, while P2's naive snapshot (taken slightly later) might already show it received - double-counting or losing it depending on timing. The marker protocol closes that gap by making channel state explicit.

## Pros
- **Election algorithms**: give a deterministic, well-understood way to restore a single coordinator after failure, which many other protocols in this subject depend on.
- **Gossip protocols**: scale to very large, highly dynamic (churning) populations with no central bottleneck and strong resilience - no single node's failure meaningfully slows dissemination.
- **Distributed snapshot/termination algorithms**: let you answer genuinely global questions (has this finished? what is a consistent global state?) without requiring a shared clock or a single omniscient observer.

## Cons
- **Election algorithms**: message cost can spike under concurrent failure detection (Bully's O(N^2) worst case); depend on accurate-enough failure detection, which (per Lesson 01) can never be perfect in an asynchronous network - a merely-slow coordinator can trigger a spurious, disruptive election.
- **Gossip protocols**: convergence is probabilistic, not deterministic - there is no hard deadline by which every node is guaranteed informed, which is unacceptable for correctness-critical information (though fine for approximate/eventually-consistent needs); anti-entropy's full-state comparison can be expensive at scale.
- **Distributed snapshot/termination algorithms**: add real protocol overhead (marker messages, channel-state bookkeeping) and complexity; snapshots are causally consistent but not "as of a real instant," which can be a subtle source of confusion when interpreting results.

## Alternatives
- **Consensus-backed leader election (Lesson 10)** - rather than a bespoke Bully/Ring election, use a consensus protocol (Raft's built-in leader election, or a lock acquired via etcd/ZooKeeper) which provides stronger guarantees (a single leader per term, safe against split-brain) at the cost of requiring a quorum of nodes to be reachable.
- **Centralized membership/broadcast service** - instead of gossip, use a central pub/sub system (Lesson 04's MOM) to broadcast membership changes. Simpler to reason about and faster in the common case, but reintroduces a central bottleneck and single point of failure that gossip was specifically designed to avoid.
- **Vector-clock-based causal snapshots** - an alternative to the Chandy-Lamport marker protocol for capturing consistent global state, using vector clocks (Lesson 06) to identify a causally consistent cut after the fact rather than coordinating markers during execution; trades real-time coordination overhead for post-hoc analysis complexity.

## When to use it
- Use **election algorithms** (or, more often in practice, a consensus protocol's built-in election) whenever a system design requires exactly one active coordinator/leader and must recover automatically from that coordinator's failure.
- Use **gossip protocols** for membership dissemination, failure detection, and state propagation in large, dynamic clusters where eventual, probabilistic consistency is acceptable and central broadcast doesn't scale (Cassandra, Consul, and many service meshes use gossip for exactly this).
- Use **distributed snapshot algorithms** when you need a provably consistent global checkpoint of a running distributed computation for debugging, recovery, or auditing.

## When NOT to use it
- Don't hand-roll a Bully or Ring election for a production system when a mature consensus library already provides safer leader election with quorum-based split-brain protection - reserve hand-rolled election for learning purposes or genuinely constrained environments where a consensus library isn't available.
- Don't use gossip for information where a hard, bounded propagation deadline matters (e.g., "every node must know about this within 100ms or the system is unsafe") - gossip's convergence is probabilistic and unbounded in the worst case; use a more deterministic broadcast or consensus mechanism instead.
- Don't run a full Chandy-Lamport-style snapshot for lightweight monitoring purposes where an approximate, eventually-consistent view (e.g., via metrics aggregation) is good enough - the protocol overhead is justified only when a genuinely consistent global cut is required.

## Key takeaways / mental model
Election answers "who's in charge, deterministically, right now" and pays for that certainty with message overhead and sensitivity to false failure suspicion. Gossip answers "how does information reach everyone eventually" and pays for its massive scalability and resilience with a lack of hard deadlines. Distributed snapshot/termination detection answers global questions about a running system with no shared clock, by explicitly capturing what's "in flight" between processes rather than assuming a naive simultaneous poll would be accurate. All three are variations on the same theme from Lesson 01: no node can see the whole system at once, so coordination must be built out of message exchange, not shared state.

## Self-check questions
1. Walk through a Bully-algorithm election among 6 processes where the two lowest-ID processes detect the coordinator's failure simultaneously. How many redundant election attempts occur, and why does the algorithm still converge correctly?
2. Explain why gossip protocol convergence time scales roughly with `log(N)` rather than `N`. What real-world property of epidemics does this mirror, and why does that make gossip attractive for very large, churning clusters?
3. What is the difference between anti-entropy and rumor-mongering gossip? Why might a production system run both simultaneously?
4. Why can't a distributed system determine "has this computation terminated?" by simply asking every node "are you idle right now?" What specific failure mode does that naive approach miss, and how does token-passing termination detection address it?
5. In the Chandy-Lamport snapshot algorithm, why must in-flight messages be recorded as part of the *channel's* state rather than either endpoint's process state? What would go wrong if they weren't recorded at all?

## References
- *Distributed Systems*, 3rd ed. (van Steen & Tanenbaum), Chapter 6: Coordination
- K.M. Chandy and L. Lamport, "Distributed Snapshots: Determining Global States of Distributed Systems" (1985)
- distributed-systems.net (free companion site for the source book)
