---
id: distributed-systems/01
subject: distributed-systems
title: "What a Distributed System Is: Goals and Pitfalls"
slug: goals-and-pitfalls
status: drafted
mastery: 
seniority: mid
source: "Distributed Systems, 3rd ed. (van Steen & Tanenbaum), Chapter 1"
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# What a Distributed System Is: Goals and Pitfalls

## TL;DR
A distributed system is a collection of independent computers that presents itself to users as a single coherent system, but where each machine has its own memory, its own clock, and can fail without the others knowing. That last fact - partial, independent failure - is the whole ballgame: almost every hard problem in distributed systems (from clocks to consensus to consistency) is a direct consequence of not sharing memory, not sharing a clock, and not being able to tell the difference between "slow" and "dead."

## The idea
A single computer is easy to reason about. It has one memory space, one clock, and when it crashes, everything stops at once - there is no partial failure, no partial state. A distributed system breaks all three of those comforts on purpose, usually in exchange for scale, geographic reach, or fault tolerance that a single machine cannot offer.

Van Steen and Tanenbaum define a distributed system as: a collection of autonomous computing elements that appears to its users as a single coherent system. Two things matter in that definition:

1. **Autonomous computing elements.** Each node runs its own operating system, has its own local memory, and makes its own local decisions. There is no shared RAM and no shared clock across nodes - a node can only learn about another node's state by sending it a message and waiting (possibly forever) for a reply.
2. **Appears as a single coherent system.** The whole point of distributing something is that users and programmers should not need to *care* that it is distributed. A distributed file system should look like a local disk; a distributed database should look like one database. Achieving that illusion despite point (1) is the discipline this entire subject is about.

Why distribute anything at all, given how much harder it makes reasoning about correctness? Three recurring motivations:
- **Scale** - one machine cannot hold all the data or serve all the requests; you need many machines cooperating.
- **Fault tolerance / availability** - a single machine is a single point of failure; replicating work and data across machines lets the system survive individual failures.
- **Geography** - users are spread around the planet, and the speed of light means a single data center can never be "close" to everyone.

None of these benefits are free. Distribution is a trade-off, not a default: it buys you scale and resilience at the cost of consistency headaches, operational complexity, and a class of failure (partial failure) that simply does not exist on a single machine. A senior engineer's job is knowing when that trade is worth making - Lesson 08 (consistency and replication) and Lesson 09 (fault tolerance) go deep on the mechanics; this lesson is about recognizing the shape of the problem before you reach for any particular mechanism.

## How it works

### 1. The defining property: no shared memory, no shared clock
Every hard problem in this subject traces back to two missing pieces that a single-machine program takes for granted:

- **No shared memory.** On one machine, thread A can write a variable and thread B can read it a nanosecond later with a guarantee (modulo memory-model subtleties) that B sees A's write. Across machines, the only way for B to learn what A did is a message over a network that can delay, reorder, duplicate, or drop that message. There is no instantaneous "peek" at another node's state.
- **No shared clock.** Each machine has its own physical clock, and those clocks drift relative to one another (crystal oscillators are not perfectly synchronized). You cannot reliably ask "did event X on node 1 happen before event Y on node 2?" using wall-clock timestamps alone - Lesson 06 devotes an entire lesson to the clock and ordering problem this creates.

Everything else in the subject - naming, communication, coordination, consistency, consensus - is essentially: *given that we cannot share memory or a clock, how do we still build something that behaves coherently?*

### 2. Partial failure: the central pitfall
On a single machine, if the machine crashes, the whole program stops - there is no in-between state to reason about from the outside. In a distributed system, individual nodes can fail while others keep running. Worse, from the perspective of a healthy node, there is **no way to distinguish a crashed node from a node that is merely slow or a network link that is merely congested**. All three look identical: no response arrives within the time you were willing to wait.

This is not a minor inconvenience - it is the reason distributed systems need timeouts, retries, heartbeats, and failure detectors instead of simple if/else crash checks, and it is the reason consensus (Lesson 10) is provably impossible to solve with a guaranteed bound on time in a fully asynchronous network. A system that has not confronted partial failure explicitly (in its retry logic, its idempotency story, its timeout budgets) will exhibit failure modes that only show up under real network conditions, not in a local dev environment where "the network" is loopback and never actually degrades.

### 3. The eight fallacies of distributed computing
In the 1990s, engineers at Sun Microsystems (L. Peter Deutsch and others) catalogued the false assumptions that programmers new to distributed systems tend to make - now known as the "Fallacies of Distributed Computing." They remain the sharpest gut-check for whether a design has actually reckoned with distribution:

1. **The network is reliable.** It isn't - packets are dropped, links fail, switches misbehave.
2. **Latency is zero.** A round trip across a data center is not free; a round trip across continents can be 100-300ms, and that is before any processing.
3. **Bandwidth is infinite.** Large payloads, chatty protocols, and N+1 request patterns all hit real bandwidth ceilings.
4. **The network is secure.** Every hop is a potential eavesdropping or tampering point unless you explicitly secure it (Lesson 12).
5. **Topology doesn't change.** Nodes join, leave, get rescheduled by an orchestrator, or move between racks/regions - hard-coded assumptions about "which machine is where" break.
6. **There is one administrator.** Large systems cross team, organizational, and even company boundaries; you cannot assume a single entity controls every node.
7. **Transport cost is zero.** Serialization, connection setup (e.g., TLS handshakes), and message framing all cost CPU and time, not just bandwidth.
8. **The network is homogeneous.** Different links have wildly different latency/bandwidth/reliability characteristics (a same-rack call is not the same as a cross-region call over the public internet).

**Worked example.** Imagine a junior engineer builds a "distributed" recommendation service by having the web server synchronously call five separate microservices per request (user profile, inventory, pricing, personalization, and ads), each over HTTP, and assumes each call takes "about 5ms because that's what it took on localhost." In production, cross-AZ calls average 2ms but P99 spikes to 80ms during network congestion (fallacy 2), one of the five services occasionally times out entirely when its host is rescheduled (fallacy 1 and 5), and the aggregate payload from all five responses is larger than expected once real user data is used, pushing bandwidth usage far past what was profiled locally (fallacy 3). The fix is not "make the network faster" - it's redesigning around the fallacies: parallel calls with bounded timeouts, fallbacks for non-critical services (Lesson 09's fault-tolerance patterns), and treating "no response" as a first-class outcome rather than an edge case.

### 4. Transparency: the illusion you are trying to build
"Appears as a single coherent system" is operationalized through several kinds of **transparency** - hiding a specific distribution-related fact from the user or programmer:

| Transparency type | What it hides | Example |
| --- | --- | --- |
| **Access** | Differences in how data is represented / how it's accessed (local vs. remote) | Calling a remote method looks like calling a local one (RPC, Lesson 04) |
| **Location** | Where a resource physically resides | A URL doesn't reveal which data center serves it |
| **Migration** | That a resource may move between locations | A VM live-migrates between hosts; clients don't notice |
| **Relocation** | That a resource may move while in use | A mobile client keeps its session as it roams between cell towers |
| **Replication** | That multiple copies of a resource exist | Reading from a replicated database looks like reading from one database |
| **Concurrency** | That a resource is shared among multiple concurrent users | Two users editing "the same" document don't see internal locking machinery |
| **Failure** | Faults and recovery | A retried request that succeeded on the second replica looks like it just worked |
| **Persistence** | Whether a resource is in memory or on disk | An ORM's object graph looks the same whether cached or freshly loaded from disk |

No real system achieves *full* transparency, and van Steen and Tanenbaum are explicit that **full transparency is not even always desirable**. If failure transparency is total, a client cannot distinguish "slow but eventually consistent" from "instant and strongly consistent," which can silently violate the guarantees an application actually needs. A well-designed API deliberately leaks *some* distribution facts - e.g., exposing that a write is "eventually visible" rather than pretending it's instantaneous - so callers can make correct decisions. Deciding which transparency to preserve and which to intentionally expose is itself a design decision, not a default to maximize.

### 5. Scalability pitfalls
Scalability is usually discussed along three axes:
- **Size scalability** - adding more users/resources without a proportional loss of performance (e.g., can you go from 1,000 to 1,000,000 users?).
- **Geographical scalability** - users and resources spread across distance without unacceptable latency.
- **Administrative scalability** - the system can span multiple independent administrative domains without collapsing under coordination overhead.

The classic scaling pitfall is **hidden centralization**. A system that looks decentralized on paper (many nodes doing work in parallel) often has a single component that every request must pass through - a central lock manager, a single metadata service, a single load balancer with no failover. That component's capacity becomes the system's true ceiling, no matter how many worker nodes you add. This is why techniques like consistent hashing (`system-design/04`) and partitioning (`ddia/10`) exist: they let you scale out the *data* and the *coordination*, not just the compute.

**Worked example.** A team builds a chat application where every message write goes through a single Postgres instance acting as the source of truth, fronted by ten stateless API servers. Adding more API servers linearly increases request-handling capacity - but write throughput plateaus at whatever the single Postgres instance can sustain, because every API server ultimately serializes through it. The system "scaled" its stateless tier but not its stateful bottleneck. Recognizing this requires asking, for every component: *if load grows 100x, does this specific piece grow with it, or does everything eventually funnel through it?*

## Pros
- Enables scale (data volume, request volume) that no single machine can provide.
- Enables fault tolerance: no single machine's failure need be catastrophic if work and data are replicated.
- Enables geographic proximity to users, cutting latency for a global user base.
- Enables administrative independence: different organizations or teams can own different parts of the system.

## Cons
- Introduces partial failure - a fundamentally new failure mode absent on a single machine.
- Removes shared memory and a shared clock, making ordering and consistency non-trivial (Lessons 06 and 08).
- Adds real operational and cognitive complexity: retries, idempotency, timeouts, monitoring across many independent processes.
- Makes correctness harder to test - failures that only manifest under real network conditions rarely show up in local development.

## Alternatives
- **A single, vertically-scaled machine** - simpler to reason about (no partial failure, shared memory and clock), but bounded by the largest machine you can buy and represents a single point of failure. Preferable when your scale and availability needs genuinely fit on one box - "you are not Google" applies more often than engineers like to admit.
- **A single machine with local replication/backup (not truly distributed)** - e.g., synchronous disk mirroring or a hot standby that is not concurrently serving traffic. Gets you some fault tolerance without the concurrency and consistency problems of a live multi-node system, at the cost of not scaling read/write throughput.
- **A distributed system with strong centralization accepted deliberately** - e.g., a single leader handling all writes with distributed followers only for reads (common in practice, see Lesson 08). This is a *conscious* trade of write scalability for simplicity, distinct from the "hidden centralization" pitfall above where the bottleneck was accidental.

## When to use it
- Data or request volume genuinely exceeds what a well-specified single machine can handle.
- Users are geographically distributed and latency to a single location is unacceptable.
- The availability requirement exceeds what a single machine (even with local redundancy) can offer.
- Different parts of the system are legitimately owned by different teams or organizations that need independent deployment and failure domains.

## When NOT to use it
- Your actual scale fits comfortably on a single well-resourced machine (or a simple primary/standby pair) - the complexity of a truly distributed architecture is not "free insurance," it's ongoing cost (operational burden, harder debugging, consistency bugs).
- You're distributing because it's fashionable or resume-driven, not because a measured bottleneck demands it. Start by asking "what specifically fails to scale on one machine?" before decomposing anything.
- The team lacks the operational maturity to run and debug a distributed system (monitoring, tracing, chaos testing) - a distributed system without that maturity tends to be *less* reliable than a well-run single machine, not more.

## Key takeaways / mental model
Think of a distributed system as a group of people who can only communicate by sending letters that might get lost, delayed, or arrive out of order, and any one of whom might silently stop responding forever with no way for the others to tell if they're dead or just busy. Every technique in this subject - naming, clocks, consensus, replication, commit protocols - is a strategy for that group to still act coherently despite those constraints. Before reaching for any specific technique, ask: which of the eight fallacies is this design implicitly assuming away, and which kind of transparency am I actually trying to provide (and which am I dangerously trying to fake)?

## Self-check questions
1. Why is "distinguishing a crashed node from a slow node" fundamentally impossible in an asynchronous network, and what design techniques (previewed here, detailed later) exist to cope with that impossibility rather than solve it?
2. Pick three of the eight fallacies of distributed computing and describe a concrete bug you'd expect from a team that implicitly assumed each one was false.
3. Explain the difference between failure transparency and exposing failure to the caller. Give an example where hiding failure completely would be actively harmful to correctness.
4. A colleague proposes "distributing" a service that currently handles 200 requests/second comfortably on one modest server, citing "future scale." What questions would you ask before agreeing this is the right call?
5. Describe a system with "hidden centralization" - components that look decentralized but funnel through one bottleneck - and how you'd detect it before it becomes a production incident.

## References
- *Distributed Systems*, 3rd ed. (van Steen & Tanenbaum), Chapter 1: Introduction
- Peter Deutsch et al., "The Eight Fallacies of Distributed Computing" (Sun Microsystems)
- distributed-systems.net (free companion site for the source book)
