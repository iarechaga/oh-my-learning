---
id: hard-parts/07
subject: hard-parts
title: Service Granularity
slug: service-granularity
status: drafted
mastery:
seniority: senior
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 7
prerequisites: [hard-parts/05]
created: 2026-06-30
updated: 2026-06-30
---

# Service Granularity

## TL;DR
Service granularity answers one of the most practical architecture questions: how small should a service be? "Micro" is not the goal. The goal is to choose a boundary that balances forces pushing a service apart (disintegrators) against forces pulling it together (integrators), then revisit that choice as the system evolves.

## The idea
When teams first adopt microservices, they often ask for a hard rule like "one service per business capability" or "never more than X classes per service." Chapter 7 argues that this is the wrong framing. There is no universal size target because service boundaries are not static geometry; they are trade-offs under changing constraints.

The real question is not "How small can we make this?" It is "What boundary gives us the best operational and change profile right now?" A boundary that is excellent for independent scaling may be terrible for transactions. A boundary that is excellent for security isolation may increase workflow chatter and failure modes.

Think of service size as force balancing:

1. Disintegrators push you to split a service into smaller pieces.
2. Integrators push you to keep pieces together or merge them.
3. Architects evaluate both force sets for a candidate boundary.
4. The chosen boundary is a decision snapshot, not permanent truth.

This perspective avoids two common mistakes:

- Mistake A: service atomization, where teams split too aggressively and create an expensive distributed system they cannot operate.
- Mistake B: fear-based consolidation, where teams keep everything together and lose independent deployability, fault isolation, and scale flexibility.

Service granularity is therefore a balancing discipline, not a naming convention.

## How it works
A practical way to choose granularity is to score a proposed boundary against explicit forces. Do not debate from vibes. Write down why components should split and why they should stay together.

### The two force sets
Use this side-by-side checklist during design reviews.

| GRANULARITY DISINTEGRATORS (push to split) | GRANULARITY INTEGRATORS (push to keep/merge) |
| --- | --- |
| 1) Service scope and function | 1) Database transactions |
| 2) Code volatility | 2) Workflow and choreography |
| 3) Scalability and throughput | 3) Shared code |
| 4) Fault tolerance | 4) Data relationships |
| 5) Security |  |
| 6) Extensibility |  |

### Granularity disintegrators
These forces increase the value of splitting a service.

### 1) Service scope and function
If a service is doing several unrelated jobs, it is usually too broad. The single responsibility signal at service level is similar to class-level cohesion: when one unit has multiple reasons to change, split pressure increases.

Example signal: one service owns user profile reads, report generation, and outbound SMS delivery. Those functions have different actors, different runtime behavior, and different failure characteristics.

### 2) Code volatility
If two parts of a service change at very different rates, independent deployability becomes valuable. Stable code should not need retesting and redeployment every time volatile code changes.

Example signal: template rendering logic changes monthly, while postal rate integration changes weekly due to vendor policy updates.

### 3) Scalability and throughput
Different load profiles are a strong split signal. If one function is called 1000x more than another, scaling the whole service wastes resources or creates performance coupling.

Example signal: email and SMS requests spike during marketing campaigns, while postal mail volume remains steady and low.

### 4) Fault tolerance
If one function is crash-prone, timeout-prone, or dependent on unstable providers, isolating it reduces blast radius. A failure in one service should not take unrelated capabilities down.

Example signal: a flaky third-party carrier API intermittently hangs request threads.

### 5) Security
Sensitive data handling is a classic reason to isolate components. If one slice of behavior touches PCI or other regulated data, isolating that slice can reduce compliance scope and simplify controls.

Example signal: card tokenization requires stricter audit and network restrictions than generic customer notifications.

### 6) Extensibility
If a capability is expected to continuously gain new features, plugins, or channels, it may deserve an independent lifecycle. Growth pressure can otherwise destabilize unrelated areas.

Example signal: notification channels are expected to expand to push, chat apps, and in-app inbox while core account APIs stay stable.

### Granularity integrators
These forces increase the value of keeping components together.

### 1) Database transactions
If two operations must share a single ACID transaction, separation can force distributed transactions, sagas, or compensations. Those can be valid, but they raise complexity and failure handling burden.

Integrator strength is high when correctness depends on atomicity across both operations.

### 2) Workflow and choreography
If two candidate services would constantly call each other in tight request chains, the network overhead and dynamic coupling can dominate. Chatty workflows increase latency, availability sensitivity, and operational fragility.

This is closely related to dynamic coupling from lesson 03: more runtime hops means more potential points of failure and coordination cost.

### 3) Shared code
If splitting forces a heavily changing shared library, teams can accidentally create change coupling through that library. Frequent shared-library updates can recreate monolithic release pain in distributed form.

The issue is not shared code itself; the issue is volatile shared code with broad consumers.

### 4) Data relationships
When data is tightly related and commonly queried or updated together, splitting can scatter the data model and introduce expensive joins across services (or denormalized duplication with consistency burden).

Strong relationship density is an integrator because locality often improves correctness and simplicity.

### Step-by-step balancing technique
Use this method for each proposed boundary.

1. Define the candidate split in one sentence.
   - Example: "Split Notification into Email, SMS, and Postal services."
2. List disintegrators that apply, with concrete evidence.
   - Use observed change rates, throughput data, incident history, security requirements.
3. List integrators that apply, with concrete evidence.
   - Use transaction rules, workflow call graphs, data access patterns.
4. Assign rough force strength (low/medium/high).
   - Keep it simple. Precision is less important than explicit reasoning.
5. Identify dominant risks on each side.
   - Split risk: chatter, eventual consistency pain, overhead.
   - Merge risk: poor scaling, larger blast radius, slower deploy cadence.
6. Choose the boundary and define re-evaluation triggers.
   - Example trigger: "If postal throughput doubles for 3 consecutive months, revisit split."

### Worked example 1: Sysops Squad notification capability
Context: Sysops Squad owns customer notifications for account events. The capability currently handles SMS, email, and postal mail in one service.

Candidate boundary:

1. Split into three services: Notification-SMS, Notification-Email, Notification-Postal.

Disintegrator analysis:

1. Scope and function: medium split pressure.
   - All are notifications, but transport mechanics are different.
2. Code volatility: high split pressure.
   - SMS provider APIs change frequently.
   - Postal integration changes with batch-file formats and vendor SLAs.
   - Email rendering changes with marketing needs.
3. Scalability and throughput: high split pressure.
   - SMS and email can spike hard.
   - Postal remains lower, often batch-oriented.
4. Fault tolerance: medium split pressure.
   - A postal vendor outage should not block SMS password reset flow.
5. Security: low to medium split pressure.
   - Similar PII class across channels, no extreme divergence.
6. Extensibility: medium split pressure.
   - New channels are expected later.

Integrator analysis:

1. Database transactions: low integrator pressure.
   - Channels do not require one shared ACID write path.
2. Workflow/choreography: high integrator pressure.
   - Message composition, preference checks, and suppression rules are shared in the runtime path.
3. Shared code: high integrator pressure.
   - Templating, personalization, and audience resolution change frequently.
4. Data relationships: medium integrator pressure.
   - Shared recipient profile and preference state are tightly connected.

Decision reasoning:

1. A full split into three independent services would maximize scaling freedom.
2. But today, strong integrators around workflow chatter and volatile shared logic would create high operational and change coupling.
3. The team chooses to keep one Notification service boundary for now, with internal channel modules and separate worker pools per channel.
4. This captures some scaling and fault isolation benefits without immediate cross-service choreography cost.
5. Revisit trigger is explicit: if channel logic divergence continues and shared pipeline coupling drops, extract channels incrementally.

Why this is a good lesson: disintegrators did not "lose." They informed internal design and future extraction criteria. Integrators simply dominate at this moment.

### Worked example 2: payment plus ledger pair
Context: an order flow performs payment authorization/capture and ledger posting.

Candidate boundary:

1. Split into Payment service and Ledger service.

Disintegrator analysis:

1. Scope and function: medium split pressure.
   - Different domain language exists.
2. Code volatility: low split pressure.
   - Both change together during policy updates.
3. Scalability and throughput: low split pressure.
   - Similar transaction volumes.
4. Fault tolerance: medium split pressure.
   - Isolation could reduce blast radius.
5. Security: low split pressure.
   - Both already operate under strict controls.
6. Extensibility: low to medium split pressure.

Integrator analysis:

1. Database transactions: very high integrator pressure.
   - Business invariant requires atomic payment state and ledger entry.
   - Partial success is unacceptable.
2. Workflow/choreography: high integrator pressure.
   - Every payment operation immediately depends on ledger mutation.
3. Shared code: medium integrator pressure.
   - Validation and accounting rules evolve together.
4. Data relationships: high integrator pressure.
   - Reconciliation queries rely on tightly linked records.

Decision reasoning:

1. Integrators are dominant, especially ACID atomicity.
2. Splitting now would push the core invariant into distributed transaction patterns.
3. Team keeps payment and ledger together in one service boundary.
4. If future constraints demand split, they will first redesign invariants for eventual consistency and compensations.

This example shows a classic case where "micro" would be architecture theater. The correct granularity is larger.

### The core trade-off in one place
Smaller services can improve independent deployment, scaling precision, and fault isolation. They also introduce costs:

1. More network calls across boundaries.
2. More dynamic coupling and runtime coordination risk (see lesson 03).
3. Higher chance of distributed transaction complexity.
4. More observability, CI/CD, and operational overhead.

Larger services reduce cross-service coordination and transaction pain, but can reduce team autonomy and make scaling less targeted. Granularity work is the art of choosing which pain you prefer for a given context.

## Pros
- Encourages explicit architectural reasoning instead of cargo-cult microservice sizing rules.
- Produces boundaries aligned with real forces like volatility, throughput, and transaction requirements.
- Improves communication between architects, developers, and operations teams through a shared decision framework.
- Supports evolutionary design because decisions include reevaluation triggers.
- Reduces costly rework by exposing distributed-system costs before splitting.

## Cons
- Requires disciplined evidence gathering; weak data leads to weak boundary decisions.
- Can feel slower than "just split it" when teams are under delivery pressure.
- Force weighting includes judgment calls, so teams may disagree on relative strength.
- Decisions can become stale if reevaluation triggers are not monitored.
- Overusing the framework on trivial boundaries can add unnecessary process overhead.

## Alternatives
- **Rule-based sizing** - Use fixed heuristics such as "one service per bounded context" or "one service per team." Faster initially, but can ignore runtime and transaction realities.
- **Premature decomposition** - Split aggressively, then merge later. This can surface boundaries early, but usually incurs high dynamic coupling and operational cost.
- **Modular monolith first** - Keep one deployable unit with strict internal module boundaries, then extract services only when disintegrators clearly dominate.
- **Event-first decomposition** - Start from domain events and asynchronous flows, using eventual consistency by design. Useful in high-scale domains but still must respect transaction-critical integrators.

## When to use it
Use force-based granularity analysis when:

1. You are introducing or refactoring microservices and need defensible boundaries.
2. A service is showing stress signals such as scaling mismatch, frequent incidents, or release bottlenecks.
3. Teams debate whether to split or merge and need a common decision language.
4. You must explain architecture decisions to stakeholders beyond engineering.
5. You are planning platform investments and need to forecast operational overhead of additional services.

This approach is especially valuable in growing systems where yesterday's correct boundary can become today's bottleneck.

## When NOT to use it
Do not run a heavyweight granularity exercise when:

1. The codebase is tiny and a simple modular monolith is clearly sufficient.
2. You lack basic operational telemetry and cannot yet evaluate throughput, failures, or change rate.
3. The decision is temporary and low impact, such as a short-lived internal tool.
4. Organizational constraints dominate architecture (for example, one team owns everything and deployment is trivial).

In these cases, keep design simple, document assumptions, and postpone service decomposition until real pressure appears.

## Key takeaways / mental model
Treat service granularity like adjusting zoom on a map, not like achieving a purity score.

1. "Micro" is not success. Fitness to forces is success.
2. Disintegrators push boundaries apart; integrators pull boundaries together.
3. Write both force lists for every serious split or merge decision.
4. Prefer explicit trade-offs over ideology.
5. Revisit boundaries when data changes.

Compact mental model:

- If you split too early, you buy distributed-system complexity before you need it.
- If you merge too long, you buy coupling and scaling pain that slows evolution.
- Good architecture picks the cheaper pain for current constraints, then adapts.

## Self-check questions
1. Why is "how small can we make services" the wrong primary question for granularity?
2. Name the six disintegrators and give one real signal for each.
3. Name the four integrators and explain why database transactions are often dominant.
4. In the Sysops Squad example, why can "keep together for now" still be a sound decision even with strong split pressure?
5. How does dynamic coupling increase as services become smaller and more chatty?
6. You have two components that must update in one atomic step and also have very different throughput. How would you reason about that conflict?
7. What reevaluation triggers would you define after choosing to keep a boundary together?

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 7
- [05-architectural-decomposition.md](05-architectural-decomposition.md)
- [03-dynamic-coupling.md](03-dynamic-coupling.md)
- [11-distributed-transactions-eventual-consistency.md](11-distributed-transactions-eventual-consistency.md)
