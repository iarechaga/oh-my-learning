---
id: ddia/01
subject: ddia
title: Reliability, Scalability, and Maintainability
slug: reliability-scalability-maintainability
status: drafted
mastery:
source: Designing Data-Intensive Applications (Martin Kleppmann), Chapter 1
prerequisites: []
created: 2026-06-30
updated: 2026-06-30
---

# Reliability, Scalability, and Maintainability

## TL;DR
A good data-intensive system is judged on three non-functional concerns: reliability (it keeps working correctly when things go wrong), scalability (it copes as load grows), and maintainability (people can keep working on it over time). These three lenses give you a shared vocabulary for reasoning about and comparing designs.

## The idea
Functional requirements describe *what* an application does (store a tweet, return a timeline). The three concerns in this lesson describe *how well* it must do that under stress and over years of change. Without shared definitions, "we need it to be fast and robust" is just hand-waving: you cannot measure it, compare two designs, or tell when you are done. Reliability, scalability, and maintainability turn vague wishes into things you can argue about with evidence.

## How it works

### Reliability: tolerate faults
Reliability means continuing to work correctly even when faults occur. A key distinction: a **fault** is one component deviating from its spec (a disk dies, a function throws); a **failure** is the system as a whole stopping its service to users. The goal of a reliable system is to stop faults from cascading into failures, that is, to be **fault-tolerant**.

Three families of faults:
- **Hardware faults** (disk crashes, RAM errors, power loss). Mitigated with redundancy: RAID, dual power supplies, replicas. Mostly independent and random.
- **Software errors** (a systematic bug triggered by a specific input, a runaway process, cascading failures). Harder than hardware faults because they are correlated: the same bug hits every node at once.
- **Human errors** (misconfiguration is a leading cause of outages). Mitigated by good abstractions and APIs, sandboxes/staging, easy and fast rollback, and thorough monitoring (telemetry).

A useful practice is deliberately injecting faults to check tolerance (for example, Netflix's Chaos Monkey killing random production nodes).

### Scalability: cope with growing load
Scalability is the ability to cope with increased load. It is not a yes/no label ("X is scalable"); it is a question: "if load grows in *this* way, what are our options?"

First, **describe the load** with load parameters chosen for your system: requests per second, read/write ratio, cache hit rate, fan-out. Kleppmann's Twitter example makes this concrete. Posting a tweet is cheap, but building each user's home timeline is the expensive part:
- *Fan-out on read*: store tweets in one place; when a user loads their timeline, query all the people they follow and merge. Cheap writes, expensive reads.
- *Fan-out on write*: maintain a precomputed timeline cache per user; when someone tweets, insert it into every follower's cache. Expensive writes, cheap reads.
The right choice depends on the load parameter (here, the distribution of followers); the real Twitter uses a hybrid, with fan-out on write for most users and fan-out on read for celebrities with millions of followers.

Then, **describe performance**. For batch systems you care about **throughput** (records processed per second); for online systems you care about **response time**. Crucially, report response time as **percentiles, not the mean**: p50 (median) is the typical experience, while p95, p99, and p999 are the **tail latencies**. Tails matter because the slowest requests often belong to your most valuable users (more data, more activity), and in systems that fan out to many backends, the overall request is as slow as its slowest dependency (tail latency amplification).

### Maintainability: keep it workable
Most of a system's cost is in ongoing maintenance, not initial build. Three design principles:
- **Operability**: make life easy for operations through good monitoring, automation, and predictable behavior.
- **Simplicity**: manage complexity with good abstractions; fight *accidental* complexity (the "big ball of mud") that is not inherent to the problem.
- **Evolvability** (extensibility): make it easy to change the system as requirements shift.

## Pros
- Gives a common, measurable vocabulary (load parameters, percentiles) instead of vague adjectives.
- Forces non-functional requirements to be explicit at design and review time.
- Targets the dimensions that actually cause real-world pain: outages (reliability), growth crises (scalability), and rewrites (maintainability).

## Cons
- These are qualities, not a recipe; they tell you *what* to care about, not *how* to achieve it.
- The three trade off against each other and against cost (redundancy buys reliability with money; caching buys read latency with write complexity).
- "Consistency" in the database sense is not part of this framework; it is covered later under transactions and consensus.

## Alternatives
- **ISO/IEC 25010 software quality model** - a broader, formal taxonomy of quality attributes (also security, portability, compatibility, and more). It is exhaustive and general, whereas Kleppmann's three are a focused subset tuned for data systems.
- **The architecture "-ilities"** (as catalogued in *Fundamentals of Software Architecture*) - a longer menu of characteristics to pick from per project; the DDIA three are the small core that nearly every data system must reason about.

## When to use it
Use these lenses whenever you design or review a data-intensive service, plan capacity, or set service-level objectives (SLOs). Percentile targets (for example, "p99 < 200 ms") come directly from the scalability lens; redundancy decisions come from the reliability lens.

## When NOT to use it
This framework is not a substitute for domain and functional requirements; it does not tell you what the product should do. For a throwaway prototype or a tiny internal tool with a handful of users, heavy scalability analysis is premature optimization. Favor simplicity first and add load analysis only once real load (or a credible forecast of it) exists.

## Key takeaways / mental model
Three lenses to stress-test any design. Reliability: tolerate faults so a fault never becomes a failure. Scalability: there is no magic "scalable" property; describe the load, then measure performance with percentiles. Maintainability: operability plus simplicity plus evolvability. If you can answer "what faults do we tolerate, how does cost grow with load, and how painful is the next change?", you have used all three.

## Self-check questions
1. What is the difference between a fault and a failure, and why does fault-tolerance target the link between them?
2. Why are response-time percentiles (p95, p99) more honest than the mean, and what are tail latencies?
3. Explain the two Twitter home-timeline approaches and the trade-off between them. Which load parameter decides the winner?
4. Name the three principles of maintainability and give one concrete practice for each.

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 1.
