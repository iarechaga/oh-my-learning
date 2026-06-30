---
id: hard-parts/04
subject: hard-parts
title: Architectural Modularity
slug: architectural-modularity
status: drafted
mastery:
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 3
prerequisites: [hard-parts/01]
created: 2026-06-30
updated: 2026-06-30
---

# Architectural Modularity

## TL;DR
Architectural modularity explains when a monolith should be split, not how.
You only pay distribution cost when specific drivers justify it:
maintainability, testability, deployability, scalability, elasticity,
and availability. These are drivers, not guarantees.

## The idea
The core question is simple: why break a monolith apart at all?
A monolith can be a very good default because local calls are fast,
consistency is easier, debugging is simpler, and operations are cheaper.
If a team splits too early, they import complexity before they earn value.

Architectural modularity gives a decision framework.
Distribution is not a badge of maturity.
It is an economic trade.

This lesson is about justification, not mechanics.
You are deciding whether decomposition is worth it,
and if yes, which part deserves that cost.

## How it works
Think in two moves:
1. Identify which modularity drivers are actually painful in your current system.
2. Translate those pains into measurable outcomes and guardrails.

If no strong drivers exist, keep the monolith.
If only one narrow area is constrained, distribute only that area.
If many drivers align and data supports them, deeper decomposition can make sense.

### Step 1: Start from the baseline truth
A monolith has genuine structural advantages:
- In-process calls instead of network hops.
- Fewer moving parts to deploy and monitor.
- Easier transactional consistency.
- Lower platform and team overhead.

So the burden of proof is on decomposition.
Do not ask "Why monolith?"
Ask "Which driver is strong enough that we should pay for distribution?"

### Step 2: Evaluate the modularity drivers
Each driver answers a different pain.
Each driver also carries a catch.

### Maintainability
What it buys:
- Smaller deployable units localize change.
- Fewer cross-cutting edits across unrelated features.
- Clearer ownership boundaries between teams.

What the catch is:
- Boundary mistakes create cross-service coordination work.
- Shared domain concepts can drift if governance is weak.
- You can replace one big tangle with many small tangles.

A practical signal:
If one change request regularly touches many unrelated modules,
and release reviews are mostly "did we break something else?",
maintainability pressure is real.

### Testability
What it buys:
- Smaller scope means faster unit tests.
- Local behavior becomes easier to isolate and reason about.
- Teams can run focused test suites more often.

What the catch is:
- Integration and end-to-end testing get harder, not easier.
- Contract drift and environment setup become recurring risks.
- Failure modes move from "wrong method call" to "timeout/retry/order".

This is a real trade-off: local test speed often improves,
while system test complexity increases.

### Deployability
What it buys:
- Independent deployment lowers release ceremony.
- Smaller blast radius per release lowers risk.
- Higher release frequency becomes realistic.

What the catch is:
- Version compatibility between services must be managed.
- Rolling upgrades and rollback strategies become mandatory.
- Release coordination still exists when flows span services.

A practical signal:
If teams delay minor changes because a full-system release is expensive,
deployability is likely a valid driver.

### Scalability and elasticity
These are related but different.

Scalability means capacity can grow with added resources,
usually with near-linear gains in the target slice.

Elasticity means the system can react rapidly to spikes,
scaling up and down without long manual cycles.

What they buy:
- You scale only the hot path services.
- You avoid paying to overprovision cold paths.
- You can absorb sudden demand peaks with less disruption.

What the catch is:
- Autoscaling feedback loops can be unstable.
- Hot partitions, queue contention, and throttling become design concerns.
- Observability must be strong enough to detect saturation early.

Why monoliths struggle here:
In a monolith, to scale one expensive function,
you usually replicate the entire codebase and runtime.
You scale everything to scale anything.

### Availability and fault tolerance
What it buys:
- A fault in one module does not have to crash the whole system.
- Degraded operation becomes possible in unaffected capabilities.
- Recovery scope narrows to impacted services.

What the catch is:
- This gain depends on dynamic coupling, not only static boundaries.
- If every request is synchronous and blocking across services,
one dependency outage can still cascade widely.
- Circuit breakers, timeouts, fallbacks, and queue decoupling
are often required to realize the benefit.

If runtime coupling remains tight, modularity on paper
will not produce fault isolation in production.

### Driver matrix: gains versus new costs
Use this table as a quick architecture decision aid.

| Driver | What improves | Cost introduced by distribution |
| --- | --- | --- |
| Maintainability | Smaller change surface, clearer ownership, less cross-cutting edits | Boundary governance, duplicate concepts, cross-service coordination |
| Testability | Faster and more focused unit tests | Harder integration/E2E tests, contract test burden, environment orchestration |
| Deployability | Independent releases, lower per-release risk, faster cadence | Versioning discipline, rollout/rollback complexity, release dependency mapping |
| Scalability | Scale only hot components instead of full system | Capacity modeling per service, hotspot management, more tuning knobs |
| Elasticity | Rapid scale up/down for bursty demand | Autoscaling control complexity, noisy neighbor effects, telemetry dependency |
| Availability/fault tolerance | Better fault isolation and graceful degradation | Network failures, fallback logic, resilience engineering overhead |

### Step 3: Drivers are not guarantees
Distribution introduces hard problems that monoliths hide:
- Network failure and latency variance are now normal, not exceptional.
- Eventual consistency appears when synchronous consistency is too expensive.
- Operational overhead rises: service discovery, observability, CI/CD pipelines,
  on-call complexity, and incident coordination.
- Distributed transactions are difficult; many workflows need compensations.

So you do not "get" modularity benefits for free.
You earn them by engineering for them.

### Step 4: Build the business case, not just the architecture case
A solid modularity proposal converts drivers into measurable targets.

Good target style:
- "Deploy lead time from commit to production drops from 10 days to 2 days."
- "Storm-period assignment throughput increases from 200/min to 8,000/min."
- "P95 assignment latency during burst stays below 800 ms."
- "Ticketing remains partially available even if assignment is degraded."

Then guard those targets with fitness functions:
executable checks that enforce architecture characteristics over time.

Examples of fitness functions for this lesson:
1. Throughput fitness function: fail CI if assignment load test cannot sustain
   the agreed transactions per second at target latency.
2. Deployability fitness function: fail release quality gate if one change
   requires synchronized deployment of too many unrelated services.
3. Availability fitness function: fail resilience tests if assignment outage
   causes ticket creation endpoint failure beyond agreed threshold.

Without measurable outcomes plus fitness functions,
"let us move to services" is a preference, not a case.

### Worked example 1: Sysops Squad justifies selective decomposition
Context:
Sysops Squad runs incident ticketing for operations teams.
Most traffic is steady, but severe weather events create storm spikes.
The ticket-assignment engine becomes the hot path under stress.

Current state in monolith:
1. Normal load: 400 assignment requests/min.
2. Storm spike: up to 20,000 assignment requests/min for 30-60 minutes.
3. Assignment logic consumes most CPU during spikes.
4. Full monolith deploy takes 45 minutes with high coordination cost.
5. Release cadence is every 2 weeks because deploys feel risky.

Observed pain mapped to drivers:
1. Scalability: only assignment path saturates, not whole app.
2. Elasticity: spike arrives faster than manual scaling response.
3. Deployability: small assignment fixes wait for full monolith release windows.

Decision:
Extract only assignment-related services,
keep most capabilities in the monolith for now.

Quantified reasoning:
1. Assume only about 5 percent of code/runtime is on the assignment hot path.
2. Storm requires roughly 50x more capacity for that hot path.
3. Monolith approach means replicating 100 percent of runtime 50x
   to satisfy one 5 percent bottleneck.
4. Selective distribution scales the 5 percent slice to 50x,
   while the remaining 95 percent stays near baseline.
5. Even with platform overhead, this is dramatically cheaper in compute,
   and operationally safer for release frequency.

Outcome goals for the business case:
1. Assignment service can autoscale from 4 to 200 instances in under 5 minutes.
2. Assignment release frequency increases from biweekly to daily.
3. Storm-period ticket ingestion remains available even if assignment is degraded,
   with queued retries and bounded backlog.

Key lesson from Sysops Squad:
Decompose the constrained slice, not the entire system.
Architecture is a scalpel, not a chainsaw.

### Worked example 2: Counter-example where monolith is the right choice
Context:
An internal admin tool supports HR data cleanup.
It has 15 daily users, low request volume,
and only 1-2 small changes per quarter.

Current state:
1. Single deployment takes 8 minutes.
2. End-to-end test suite is stable and quick.
3. No observed CPU or memory saturation.
4. No uptime SLO beyond office hours.

Driver check:
1. Maintainability pressure is low.
2. Testability pressure is low.
3. Deployability pressure is low.
4. Scalability/elasticity pressure is absent.
5. Availability pressure is modest and already met.

Decision:
Stay monolithic.

Why:
If drivers are absent, distributing adds cost without value:
- More deployment artifacts.
- More monitoring and on-call noise.
- More integration complexity.
- More opportunities for network-induced failures.

This is cost-aware engineering.

### A practical decision checklist
Before decomposing, answer these in writing:
1. Which two drivers are strongest, based on production evidence?
2. What measurable outcomes will improve, by how much, and by when?
3. What new distributed-system costs will appear,
   and how will we absorb them operationally?
4. Which fitness functions will fail fast when the architecture drifts?
5. Why is selective decomposition better than full decomposition right now?

If these cannot be answered concretely,
you likely need more evidence before splitting the monolith.

## Pros
- Forces architecture decisions to be evidence-driven rather than trend-driven.
- Prevents premature decomposition by requiring explicit modularity drivers.
- Encourages selective extraction so teams only pay distribution costs where needed.
- Improves communication with business stakeholders through measurable goals.
- Connects architectural intent to enforceable fitness functions over time.

## Cons
- Requires disciplined measurement that some teams do not yet have.
- Can be misused as a checklist theater if metrics are vague.
- Still depends on boundary quality; good drivers do not fix poor design.
- Adds analysis overhead before teams can act.
- May under-account for organizational factors if treated as purely technical.

## Alternatives
- **Keep and tune the monolith** - Improve profiling, caching, query plans,
  and release automation without service extraction.
  Prefer this when pain is localized but solvable in-process.
- **Modular monolith** - Strengthen internal module boundaries first,
  while keeping one deployable unit.
  Prefer this when maintainability pressure is real but distribution pressure is weak.
- **Event-driven decomposition for one workflow** - Extract only one critical,
  burst-prone workflow behind asynchronous messaging.
  Prefer this when elasticity and fault isolation matter for a narrow path.

## When to use it
Use architectural modularity analysis when monolith pain is visible
and teams are proposing distribution as a remedy.
It is most useful when one part of the system has very different
scaling, release, or resilience needs than the rest.

## When NOT to use it
Do not use this approach as a pretext to force microservices everywhere.
If your system is low change, low traffic, and operationally stable,
the driver model will correctly point to staying monolithic.

Also avoid decomposition when your team cannot yet support
distributed operations (observability, incident response,
release automation, and ownership boundaries).

## Key takeaways / mental model
Treat architectural modularity as an investment memo.
A monolith is the baseline: simple, coherent, efficient.
Carve out distributed units only when a capability
needs different economics.

Drivers are the reasons to invest.
Fitness functions are the governance that keeps the investment honest.
If you cannot state both clearly, do not decompose yet.

## Self-check questions
1. Why is "we want microservices" an incomplete argument without modularity drivers?
2. How does testability improve locally while becoming harder at integration scope?
3. Explain the difference between scalability and elasticity using one concrete scenario.
4. In what way can synchronous runtime coupling cancel out availability gains from decomposition?
5. For Sysops Squad, why is extracting only assignment services economically better than scaling the whole monolith?
6. What measurable goals and fitness functions would you define before approving a decomposition proposal?

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 3
- [01-tradeoffs-no-best-practices.md](01-tradeoffs-no-best-practices.md)
- [01-reliability-scalability-maintainability.md](../../ddia/lessons/01-reliability-scalability-maintainability.md)
- [02-distributed-system-attributes.md](../../system-design/lessons/02-distributed-system-attributes.md)
