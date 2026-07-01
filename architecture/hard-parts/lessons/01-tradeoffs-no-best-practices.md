---
id: hard-parts/01
subject: hard-parts
title: Trade-offs and "No Best Practices"
slug: tradeoffs-no-best-practices
status: drafted
mastery:
seniority: senior
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 1
prerequisites: []
created: 2026-06-30
updated: 2026-06-30
---

# Trade-offs and "No Best Practices"

## TL;DR
In distributed architecture, there are no universal best practices.
Every decision improves one force and worsens another.
The architect's work is to expose local trade-offs, choose with explicit rationale, and enforce decisions with architecture fitness functions.

## The idea
Teams like reusable formulas: pattern X plus checklist Y equals success.
That worked better in centralized systems with fewer interacting variables.

Distributed systems changed the game.
A service boundary adds network variance, partial failure, independent deployments, and data ownership splits.
The same pattern can succeed in one environment and fail in another.

Chapter 1 puts it plainly:

- Everything in software architecture is a trade-off.
- Why is more important than how.

If you copy only how, you copy mechanics and miss assumptions.
If you understand why, you can adapt when constraints change.

## How it works
Use this loop whenever decisions are expensive to reverse:

1. Find what is entangled.
2. Analyze how it is coupled and which forces interact.
3. Assess trade-offs per dimension, then recombine.

Running example: Sysops Squad, a ticket and customer-support platform being modernized into distributed services.

### Why distributed systems broke copy-paste advice
In a monolith, assumptions are often stable:

- local calls are fast,
- one data store simplifies consistency,
- failure boundaries are easier to reason about.

In distributed systems, boundary effects dominate:

```
Boundary -> latency variance -> retries/timeouts -> coupling shifts
```

Worked example 1: copied advice fails in Sysops Squad

Imported advice: "Always use asynchronous messaging between services."

1. Assumption: eventual consistency is acceptable for all ticket actions.
2. Local reality: premium support promises immediate assignment confirmation.
3. Assumption: team can handle broker lag/replay safely.
4. Local reality: broker operations maturity is low.
5. Outcome: blind adoption increases incident risk.

The pattern is not universally wrong.
The context mismatch is wrong.

### The architect's core loop in action
Loop sketch:

```
[Find entanglement] -> [Analyze coupling + forces] -> [Assess dimensions]
         ^                                                   |
         +---------------------------------------------------+
```

Worked example 2: Ticketing assignment and Notification

Current flow: Ticketing assigns a ticket, then synchronously calls Notification.

Step 1, find entanglement:

- Assignment completion depends on Notification responsiveness.
- Business concern A (assignment) is runtime-coupled to concern B (notification).

Step 2, analyze coupling:

- Dynamic coupling: synchronous request chain.
- Operational coupling: Notification incidents degrade Ticketing SLO.
- Organizational coupling: Ticketing release risk now includes Notification behavior.

Step 3, assess dimensions:

1. Availability: async isolates failures better.
2. Latency semantics: sync gives immediate end-to-end acknowledgment.
3. Complexity: async adds idempotency, replay, and broker operations.
4. Auditability: async logs can improve tracing.

Recombine:
if assignment must survive downstream outages and notification may lag up to 120 seconds, async is often better.
if each assignment must be immediately confirmed for legal reasons, sync can be mandatory.

No universal winner exists.
Only a context-weighted winner exists.

### Architecture vs design: practical boundary
The boundary is fuzzy, so use cost of change and blast radius.

Treat as architecture when most are true:

1. Expensive to reverse after release.
2. Crosses team or service boundaries.
3. Materially affects quality attributes.
4. Requires migration or compatibility commitments.
5. Changes runbooks, alerts, or incident response.

Treat as design when local, cheap, and quickly reversible.

Worked example 3: classify two Sysops Squad decisions

Decision A: rename an internal Ticketing method.
- low reversal cost, local blast radius, design.

Decision B: Reporting can no longer query Ticketing tables directly and must consume events.
- high reversal cost, broad blast radius, architecture.

### Qualitative and quantitative reasoning together
Good trade-off analysis uses narrative plus numbers.

Qualitative prompts:

- Which team needs autonomy?
- Which failure damages trust most?
- Which complexity is most error-prone during incidents?

Quantitative prompts:

- What p99 latency budget must hold?
- What delivery success threshold is required?
- What peak load must be sustained?

Worked example 4: integration-style decision

Qualitative forces:

1. Premium users expect immediate confirmation.
2. Support operations need assignment continuity during outages.
3. Broker operations maturity is limited today.

Quantitative constraints:

1. Assignment API p99 <= 300 ms.
2. Notification success >= 99.9% within 120 seconds.
3. Platform handles 3x burst traffic.

If narrative priorities and numeric budgets conflict, revisit one of them.

### Decision traps to avoid
#### Trap 1: Out-of-context decisions
"It worked there" is not enough.

Countermeasures:

1. Write local context first.
2. List imported assumptions.
3. Validate assumptions against current reality.

#### Trap 2: Resume-driven or evangelism choices
Technology selected for prestige, ideology, or trend alignment.

Countermeasures:

1. Compare alternatives with one rubric.
2. Require explicit consequences.
3. Rank by business outcomes, not novelty.

#### Trap 3: Analysis paralysis
The team keeps analyzing and never commits.

Countermeasures:

1. Timebox analysis.
2. Prefer reversible choices under uncertainty.
3. Use fitness functions to manage post-decision risk.

### Supporting tool #1: Architecture Decision Records (ADRs)
ADRs preserve trade-off reasoning in a durable format.

Core structure:

1. Title
2. Status
3. Context
4. Decision
5. Consequences

Optional sections:

- Compliance/Governance
- Notes

Full worked ADR example:

```
ADR-014: Use asynchronous messaging between ticket assignment and customer notification

Status
Accepted (2026-06-30)

Context
- Sysops Squad is modernizing into distributed services.
- Ticketing currently calls Notification synchronously.
- Incident reviews showed timeout cascades during Notification latency spikes.
- Requirement: assignment must succeed during partial downstream outage.
- Allowance: non-critical notifications may lag up to 120 seconds.

Decision
- Ticketing publishes TicketAssigned events to a durable broker.
- Notification consumes events asynchronously.
- Ticketing returns success after event persistence.
- Priority-1 tickets keep an exception path for immediate confirmation.

Consequences
Positive
- Assignment availability decouples from Notification uptime.
- Burst traffic is buffered.
- Services scale independently.

Negative
- Eventual consistency: customer notification may lag.
- Added operations overhead: broker health, lag monitoring, dead-letter handling.
- New failure mode: publish succeeds while consumer pipeline is misconfigured.

Neutral/Follow-up
- Add idempotency keys for Notification consumers.
- Define replay runbook ownership.
- Re-evaluate after 90 days of production metrics.

Compliance/Governance
- Retain event audit trail for 90 days.
- Enforce PII masking in payloads.

Notes
- Supersedes temporary manual retry runbook from INC-2217.
- Related fitness functions: FF-07 and FF-11.
```

### Supporting tool #2: Architecture fitness functions
A fitness function is an objective, automatable test guarding an architecture characteristic.
ADRs define intent; fitness functions enforce intent continuously.

Example A: dependency governance

```text
FF-07 dependency-governance
Rule: src/ticketing/** cannot depend on src/reporting/**
Execution: every CI pull request build
Failure action: fail build and print dependency chain
```

Failure sample:

```text
Forbidden dependency detected
src/ticketing/assignment/AssignmentService.ts
  -> src/reporting/query/ReportView.ts
Violation: ADR-009 data ownership boundary
```

Example B: performance budget

```text
FF-11 assignment-latency-budget
Rule: /api/tickets/{id}/assign p99 <= 300 ms under reference load
Execution: nightly perf run + release gate
Failure action: block release and open regression issue
```

Sample output:

```
+----------------------+--------+--------+---------+
| Metric               | Budget | Actual | Verdict |
+----------------------+--------+--------+---------+
| p50 latency (ms)     | <=120  | 94     | PASS    |
| p95 latency (ms)     | <=220  | 208    | PASS    |
| p99 latency (ms)     | <=300  | 341    | FAIL    |
+----------------------+--------+--------+---------+
```

### Worked mini-example: sync REST vs async messaging
Decision question:
how should Ticketing trigger Notification in Sysops Squad?

Options:

1. synchronous REST,
2. asynchronous messaging.

Competing forces:

1. Immediate customer feedback.
2. Resilience during Notification outages.
3. Operational complexity and skill.
4. Debuggability and traceability.

Step-by-step comparison:

1. Mandatory immediate confirmation favors sync.
2. Outage isolation favors async.
3. Low broker maturity can favor sync short-term.
4. Burst-induced timeout cascades favor async buffering.

Illustrative scorecard:

```
+------------------------------+-----------+-----------+
| Force                        | Sync REST | Async Msg |
+------------------------------+-----------+-----------+
| Immediate confirmation       | High      | Medium    |
| Outage isolation             | Low       | High      |
| Simplicity right now         | High      | Medium    |
| Burst absorption             | Medium    | High      |
+------------------------------+-----------+-----------+
```

No row is always correct.
Weights come from business context.

## Pros
- Prevents cargo-cult architecture through explicit context checks.
- Surfaces costs before they become incidents.
- Improves cross-team alignment with written rationale.
- Encourages reversible progress under uncertainty.
- Preserves decision memory via ADRs.
- Reduces drift with automatable fitness checks.

## Cons
- Requires upfront analysis effort.
- Needs discipline to maintain ADRs and tests.
- Can feel slower than copying defaults.
- Depends on measurement capability for quantitative checks.
- Can still become over-analysis without timeboxing.

## Alternatives
- **Best-practice playbooks** - fast startup, fragile under context mismatch.
- **Pure expert intuition** - quick, but weak auditability and transferability.
- **Framework defaults** - lower cognitive load, constrained trade-off space.
- **Ad hoc trial-and-error** - flexible early, weak institutional learning.

## When to use it
Use this method when decisions are expensive to reverse, cross team boundaries, or significantly affect reliability, scalability, security, operability, or delivery speed.
It is especially useful during monolith decomposition, service-boundary work, and data ownership redesign.

## When NOT to use it
Do not run heavyweight trade-off analysis for tiny local changes that are cheap to reverse.
For low-blast-radius details, lightweight design judgment is enough.
Also avoid fake precision: when data is missing, state uncertainty and choose reversible options protected by fitness functions.

## Key takeaways / mental model
Architecture is not pattern memorization.
It is explicit decision-making under competing forces.

Mental model:

1. No universal best practices in distributed systems.
2. Every gain has a cost.
3. Explain why before how.
4. Find entanglement, analyze coupling, assess dimensions, recombine.
5. Record intent in ADRs.
6. Enforce intent with fitness functions.
7. Re-evaluate with production evidence.

## Self-check questions
1. Why can a technically sound pattern still fail when copied into a different distributed context?
2. Apply find-analyze-assess to Sysops Squad's assignment-notification flow when notification may lag 120 seconds.
3. How do reversibility and blast radius separate architecture decisions from design decisions?
4. What ADR sections are mandatory, and how do they reduce out-of-context and resume-driven choices?
5. How do dependency and latency fitness functions make architecture intent enforceable?
6. For Ticketing -> Notification, when does sync REST win, and when does async messaging win?

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 1
- [01-reliability-scalability-maintainability.md](../../ddia/lessons/01-reliability-scalability-maintainability.md)
