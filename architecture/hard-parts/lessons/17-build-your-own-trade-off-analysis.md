---
id: hard-parts/17
subject: hard-parts
title: Build Your Own Trade-Off Analysis
slug: build-your-own-trade-off-analysis
status: drafted
mastery:
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 15
prerequisites: [hard-parts/01]
created: 2026-06-30
updated: 2026-06-30
---

# Build Your Own Trade-Off Analysis

## TL;DR
This lesson is the capstone method for the whole book.
You can apply one repeatable process to any architecture decision: identify entangled forces, separate what is independent, evaluate each dimension, and then recombine into a context-aware judgment.
There are no universal best practices, only better and worse fits for a specific system at a specific moment.

## The idea
Lesson 01 opened with a hard truth: architecture has no best practices, only trade-offs.
This final lesson closes that loop with a practical method you can run repeatedly.

The method matters because most architecture mistakes are not technical ignorance.
They come from mixing concerns, skipping context, or pretending one force is all that matters.
Teams say things like "Kafka is scalable" or "REST is simpler" without stating the domain case, the constraints, and the competing quality attributes.

A useful trade-off analysis does three things.
First, it names the forces that are coupled inside one decision.
Second, it separates what can be reasoned about independently from what is truly entangled.
Third, it turns that reasoning into an explicit choice, with conditions that would change the choice later.

This lesson synthesizes the patterns and cautions from lessons 02 through 16.
Those lessons gave you many specific trade-offs.
This one gives you the reusable engine that produces those analyses on demand.

## How it works
Treat this as a lightweight, repeatable architecture workflow.
You can run it in a design session, an ADR review, or a migration planning meeting.

### 1) Find what parts are ENTANGLED
Start with one concrete decision statement, not a vague technology debate.

Bad framing:
"Should we use events?"

Good framing:
"Between ticket completion and survey creation in Sysops Squad, should we call the survey service synchronously via REST, or publish an event that the survey service consumes?"

Now list the dimensions touched by this single decision.
Typical dimensions include performance, scalability, fault tolerance, consistency, coupling, operational complexity, observability, cost, and team cognitive load.

The key is to detect coupling.
If changing one option shifts several dimensions at once, those dimensions are entangled in this decision.
For example, choosing asynchronous messaging often changes fault tolerance, consistency timing, and operational complexity together.

### 2) Analyze HOW they are coupled
Once dimensions are listed, map influence.
Ask: "If this force changes, which other forces move with it?"

You are trying to split the problem into:
1. Genuinely independent dimensions.
2. Entangled dimensions that must be judged together.

Example mapping for REST vs events:
1. Performance and consistency are partly independent when traffic is low.
2. Scalability and fault tolerance become more entangled as throughput and failure frequency rise.
3. Complexity and coupling are entangled because introducing a broker lowers runtime coupling but raises platform and operational complexity.

This mapping step prevents false certainty.
Without it, teams accidentally compare one dimension in depth and hand-wave the rest.

### 3) Assess the TRADE-OFFS, then recombine
Now evaluate each dimension explicitly.
Use relative judgments like better, worse, or similar, with short rationale.
If you have measurements, include them.
If not, stay qualitative but explicit.

Then recombine.
A final decision is not "Option A wins 4 out of 6 rows."
A final decision is "Given our current constraints and priorities, the dimensions we care most about dominate, so we pick X, and we will revisit if Y changes."

This recombination step is where architecture judgment lives.
It converts analysis into accountable decision-making.

### Practice: model domain cases, not generic cases
Do not evaluate options against abstract benchmark stories.
Build representative examples from your own system.

A representative examples exercise can be small and fast.
Pick 3 to 5 scenarios that reflect real load, failure, and business expectations.

Example set for Sysops Squad survey triggering:
1. Normal weekday load: 400 ticket completions per minute, survey expected within 5 seconds.
2. Peak incident window: 10x spike for 20 minutes.
3. Partial outage: survey service unavailable for 8 minutes.
4. Compliance check: no customer should receive duplicate survey links.

Generic benchmark claims like "broker X can do 1 million messages per second" are not useless, but they are not enough.
Your trade-off is about your latency target, your failure mode, your staffing, and your error tolerance.

### Practice: use qualitative first, quantitative where possible
You do not need perfect numbers to make a solid decision.
Start with qualitative relative analysis when data is missing.
Then add quantitative checks where measurement is feasible.

Qualitative examples:
1. Event-based messaging is better for producer resilience during consumer downtime.
2. Synchronous REST is better for immediate response semantics.

Quantitative examples:
1. End-to-end p95 latency budget: ticket completion API must stay under 300 ms.
2. Availability target: survey trigger path must meet 99.95 percent monthly success.
3. Fitness function: fewer than 0.1 percent duplicate surveys in production.
4. Throughput benchmark: sustain 5,000 completions per minute for 30 minutes without backlog overflow.

Use both modes.
Qualitative gives speed and coverage.
Quantitative gives precision and safety where risk is highest.

### Practice: avoid common decision traps
Three traps repeatedly break architecture decisions.

Trap 1: out-of-context trade-offs.
A choice that worked elsewhere is copied without importing its conditions.
Example: "Company Z used event streaming for everything, so we should too," while ignoring that Company Z had a dedicated platform team and different consistency needs.

Trap 2: evangelism or resume-driven development.
A technology is championed regardless of fit.
The debate becomes identity-driven instead of context-driven.

Trap 3: analysis paralysis.
The team keeps analyzing because certainty is impossible.
Instead of waiting for perfect confidence, prefer reversible decisions and add fitness functions to detect drift.

### Practice: make decisions reversible, record, and guard
If a decision is hard to reverse, raise the evidence bar.
If it is easy to reverse, decide earlier and learn faster.

Record decisions in ADRs.
This ties directly back to lesson 01: architecture is about explicit trade-offs, not hidden defaults.
An ADR should include context, options considered, selected option, and "what would change this decision."

Then guard the decision with fitness functions.
A fitness function is an executable or measurable check that enforces architectural intent.

Examples for this topic:
1. Automated check that survey duplicate rate stays below threshold.
2. Alert if survey trigger lag exceeds 60 seconds for more than 5 minutes.
3. Contract tests for event schema compatibility.
4. SLO dashboard gate in release review.

This is how you prevent architectural drift from silently undoing your reasoning.

### Reusable trade-off table template
Use this simple ASCII table in design docs or ADRs.

```
+----------------------+---------------------+---------------------+
| Dimension            | Option A            | Option B            |
+----------------------+---------------------+---------------------+
| Performance          | better/worse/similar| better/worse/similar|
| Scalability          | better/worse/similar| better/worse/similar|
| Fault tolerance      | better/worse/similar| better/worse/similar|
| Consistency          | better/worse/similar| better/worse/similar|
| Complexity           | better/worse/similar| better/worse/similar|
| Coupling             | better/worse/similar| better/worse/similar|
+----------------------+---------------------+---------------------+
| Notes / rationale    | why this rating?    | why this rating?    |
+----------------------+---------------------+---------------------+
```

You can add rows like cost, operability, observability, or team maturity.
Keep the table short enough to force clarity.

### Worked example: Sysops Squad REST vs event-based messaging
Decision statement:
Between ticket completion and survey creation, should Sysops Squad use synchronous REST or event-based messaging?

Step 1: define candidate options.
1. Option A: ticket service makes direct REST call to survey service during completion flow.
2. Option B: ticket service publishes TicketCompleted event; survey service consumes asynchronously.

Step 2: list dimensions for this decision.
1. Performance
2. Scalability
3. Fault tolerance
4. Consistency
5. Complexity
6. Coupling

Step 3: rate each dimension qualitatively in context.

Assumptions for this run:
1. Current load is moderate but spikes during incidents.
2. Survey can tolerate short delay after ticket completion.
3. Team has basic broker experience but no full-time messaging platform team.

```
+----------------------+------------------------------+------------------------------+
| Dimension            | Sync REST                    | Event-based messaging        |
+----------------------+------------------------------+------------------------------+
| Performance          | better for immediate request | similar to slightly worse    |
|                      | path latency at low load     | for instant response, but    |
|                      |                              | acceptable for async flow    |
| Scalability          | worse under burst fan-out    | better decoupled buffering   |
|                      | because caller waits         | and consumer scaling         |
| Fault tolerance      | worse if survey service down | better via durable queue and |
|                      | completion path degrades     | retry without blocking user  |
| Consistency          | better for immediate         | worse for immediate read,    |
|                      | confirmation semantics       | but acceptable eventual sync |
| Complexity           | better initially, fewer      | worse initially, adds broker,|
|                      | moving parts                 | retries, schema governance   |
| Coupling             | worse temporal coupling      | better runtime decoupling    |
|                      | and tighter dependency       | between producer/consumer    |
+----------------------+------------------------------+------------------------------+
| Notes / rationale    | simple to ship now, but      | resilient under outages and  |
|                      | fragile during outages and   | peaks; operational maturity  |
|                      | peaks                        | required                     |
+----------------------+------------------------------+------------------------------+
```

Step 4: recombine into a decision.
Given Sysops Squad priorities, the decisive dimensions are fault tolerance and scalability during incident spikes.
Survey creation is not on the critical path for ticket completion correctness.
A short delay is acceptable.

So the context-justified decision is Option B, event-based messaging.
The team accepts added complexity in exchange for resilience and decoupling.

Step 5: make it reversible and guarded.
1. Record ADR with why eventing was chosen now.
2. Add fitness functions for trigger lag, duplicate survey rate, and delivery success.
3. Keep a fallback path design for temporary synchronous call if broker is unavailable at launch.

Step 6: state what would change this decision.
Switch toward synchronous REST if these conditions become true:
1. Product requirement changes to strict immediate consistency for survey creation confirmation in same response.
2. Operational cost of broker management exceeds team capacity and outage profile is low.
3. Throughput remains low and stable for long period, making simpler coupling acceptable.

This "what changes the decision" section is essential.
It turns architecture from static dogma into adaptive governance.

### Mini example 2: database per service vs shared database
You can reuse the same method quickly.

1. Entangled dimensions: autonomy, consistency, reporting complexity, operational cost.
2. Coupling analysis: autonomy and deployment speed are tightly coupled; reporting and cross-domain joins are tightly coupled.
3. Assessment: per-service DB improves autonomy but increases cross-service reporting complexity.
4. Recombine: if independent deployability is strategic and reporting can be solved with read models, choose per-service DB.

No universal answer.
Only context-weighted trade-offs.

### Mini example 3: choreography vs orchestration in sagas
1. Entangled dimensions: visibility, coupling, local autonomy, debugging effort.
2. Coupling analysis: orchestration improves visibility but centralizes control.
3. Assessment: choreography lowers central dependency but can increase emergent behavior complexity.
4. Recombine: choose based on failure handling clarity and team ability to observe distributed flow.

Again, same engine, different decision.

## Pros
- Provides a repeatable method that works across technology domains.
- Forces explicit context, reducing cargo-cult architecture choices.
- Supports both fast qualitative decisions and rigorous quantitative validation.
- Encourages reversible decisions and continuous governance via fitness functions.
- Produces artifacts such as ADRs and trade-off tables that improve team alignment.

## Cons
- Takes discipline and time compared to instinct-driven decisions.
- Can feel heavy if applied with too many dimensions at once.
- Qualitative ratings can become subjective without clear rationale.
- Requires organizational honesty to avoid politics and evangelism bias.
- Reversibility is not always possible for deeply structural decisions.

## Alternatives
- **Single-axis optimization** - Optimize one metric only, such as latency or cost. Faster to execute, but risky because hidden costs in other dimensions emerge later.
- **Copy a reference architecture** - Reuse a known pattern from another company or team. Useful as input, but dangerous if context differences are ignored.
- **Delay decision until full data exists** - Reduces uncertainty, but can create analysis paralysis and delivery delay when reversible action was possible earlier.
- **Expert intuition only** - Senior experience can be valuable, but without explicit trade-off reasoning it is hard to audit, teach, or revisit.

## When to use it
Use this method for any non-trivial architecture decision that affects multiple quality attributes.
Typical triggers include communication style choices, data ownership boundaries, consistency models, scaling strategies, resilience patterns, and migration paths.

It is especially useful when teams disagree strongly.
The framework converts opinion battles into structured, evidence-aware comparison.

Use it early in design and again at major context changes.
A decision that was correct six months ago may be wrong after growth, regulation changes, or team structure shifts.

## When NOT to use it
Do not run full trade-off workshops for tiny, low-impact decisions.
If reversal is cheap and risk is minimal, choose quickly and move on.

Do not pretend this method gives mathematical certainty.
It gives transparent reasoning under uncertainty.
If stakeholders demand certainty that does not exist, the answer is better risk framing, not infinite analysis.

Do not use generic template outputs without domain scenarios.
A table with no context is architecture theater.

## Key takeaways / mental model
Think of architecture decisions as knots of forces, not isolated checkboxes.
Your job is to untangle the knot enough to reason clearly, then tie a deliberate knot that matches your current context.

The meta-point of the entire book is fluency in this practice.
You are not memorizing best practices.
You are building the habit of context-first trade-off analysis.

Use this compact mental loop:
1. Name the decision in one sentence.
2. Find entangled dimensions.
3. Separate independent from coupled forces.
4. Evaluate each dimension with explicit rationale.
5. Recombine according to current priorities.
6. Record in ADR.
7. Guard with fitness functions.
8. Revisit when context shifts.

If you do this consistently, architecture becomes explainable, evolvable, and teachable.

## Self-check questions
1. Why is "best practice" language dangerous in architecture decisions?
2. In your own words, what is the difference between finding entanglement and assessing trade-offs?
3. Give one example of two dimensions that are independent and two that are entangled in a decision you recently made.
4. How would you design three representative domain cases for a decision in your current system?
5. When should you stay qualitative, and when must you add quantitative checks?
6. What are the signs of out-of-context copying, evangelism, and analysis paralysis in a team discussion?
7. For the Sysops Squad survey-trigger decision, what assumptions made eventing preferable, and what assumptions could reverse that outcome?
8. Which fitness functions would you add to guard your latest architecture decision from drift?

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 15
- This lesson synthesizes lessons 02 through 16 and closes the loop from lesson 01.
- [01-tradeoffs-no-best-practices.md](01-tradeoffs-no-best-practices.md)
