---
id: sre/16
subject: sre
title: Evolving SRE Practices with Service Maturity
slug: sre-practice-maturity
status: drafted
mastery:
seniority: staff
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 1-2 and synthesis across Parts I-IV
prerequisites: [sre/04, sre/05, sre/15]
created: 2026-08-10
updated: 2026-08-10
---

# Evolving SRE Practices with Service Maturity

## TL;DR
The right amount of SRE practice — how tight the SLO, how automated the release pipeline, how large the on-call rotation, whether dedicated SRE exists at all — is not a fixed target; it's a function of a service's current scale, criticality, and organizational maturity, and it should change deliberately as those change. Applying full Google-scale SRE machinery to a young, low-traffic service is as much a maturity mismatch as running a fast-growing, business-critical service with no SLOs and an informal on-call rotation.

## The idea
Every lesson in this subject so far describes a practice as though its "right" configuration were fixed: an SLO of 99.9%, a 6-8 person on-call rotation, a 50% toil cap, dedicated SRE engagement. In reality, these are not universal constants — they're calibrated answers for a service at a particular point in its lifecycle, and the book is explicit (particularly in its opening framing and its closing synthesis) that SRE practice itself has to evolve as a service and the organization around it evolve. A team that locks in Year-1 practices forever either over-invests early (formal SLOs and dedicated on-call for a service with 50 users) or under-invests later (still running informal, ad hoc ops for a service that's grown into company-critical infrastructure).

This is a genuinely staff/principal-level judgment call because it requires reading signals across the whole organization — not just one service's metrics — and making a call about *when* to invest in the next level of practice, which is inherently ambiguous and has real cost either way (premature investment wastes engineering effort; late investment risks a painful, reactive scramble during an incident that reveals the gap).

## How it works

### A rough maturity progression
Synthesizing this subject's earlier lessons into stages (not a rigid model, but a useful lens):

**Stage 1 — Informal.** A new service, small user base, single team. Monitoring exists but is ad hoc (dashboards, no formal SLO). On-call, if it exists at all, is informal ("ping me if it's down"). No dedicated SRE engagement; the product team runs everything. Toil is real but small in absolute terms, so it's tolerated rather than tracked.

**Stage 2 — Foundational practices.** The service has real users and real cost-of-downtime. The team defines its first SLIs and SLOs (`sre/02`, `sre/03`), even if rough, and starts an error budget (`sre/04`) as a genuine, if lightweight, release-governance signal. A real on-call rotation forms (`sre/08`), even if smaller than the 6-8 person ideal. Toil is tracked informally, even if not yet capped at 50%.

**Stage 3 — Engineered reliability.** The service is business-critical or high-scale. Full golden-signal monitoring and multi-window burn-rate alerting (`sre/07`) replace ad hoc dashboards. Progressive delivery and hermetic builds (`sre/12`) replace all-at-once deploys. The on-call rotation meets sustainable-size guidelines, formal incident command activates for real incidents (`sre/09`), and postmortems are a standing, enforced practice (`sre/10`). The team may request dedicated or consulting SRE engagement via a PRR-style process (`sre/15`).

**Stage 4 — Cross-org reliability infrastructure.** The service is one of many the organization depends on; reliability practices themselves become standardized platform capabilities (shared SLO tooling, shared incident-command training, shared postmortem review across teams) rather than something each team builds independently, and multi-team interface contracts (`sre/15`) are formalized because the dependency graph is now too complex for informal coordination.

**Worked example — a service moving from Stage 1 to Stage 2.** An internal reporting tool built by a 3-person team starts as Stage 1: no SLO, informal support. After six months, a major department starts depending on it daily for planning decisions, and an unnoticed multi-hour outage causes a missed budget deadline. This is the signal to move to Stage 2: the team defines a first SLI ("percentage of report-generation requests completing successfully within 2 minutes"), sets an initial SLO (deliberately looser than what Stage 3 might eventually demand — say 99% rather than 99.9%, since the team doesn't yet have the tooling or headcount to sustain a tighter target), and starts a lightweight on-call rotation among the 3 team members, even though that's below the 6-8 person ideal from `sre/08` — an explicit, temporary trade-off made with the intention of growing the rotation as the team grows, not a permanent state.

### Signals that indicate a stage transition is due
The book doesn't give a mechanical formula, but several recurring signals from earlier lessons compound into a judgment call:
- **Toil measurement (`sre/05`) creeping upward** without a corresponding increase in headroom — a sign informal practices are starting to buckle under growth.
- **Repeated postmortem findings (`sre/10`) pointing at the same structural gap** (e.g., "we still don't have a real SLO to alert against") — a sign the org keeps hitting the ceiling of its current practice stage.
- **On-call load (`sre/08`) exceeding sustainable bounds** for the current, smaller rotation — a direct signal the team has outgrown its informal support model.
- **Business dependency growing faster than reliability investment** — e.g., the reporting-tool example above, where downstream criticality outpaced the operational maturity supporting it.

### The cost of moving too early vs. too late
**Worked example — moving too early.** A brand-new, low-traffic internal prototype adopts full Stage 3 practices from day one: multi-window burn-rate alerting, a formal 8-person on-call rotation, hermetic build infrastructure. The prototype's usage pattern is still changing weekly as the team learns what the product should even be — the SLO is stale within a month, the elaborate alerting fires on noise from constant architecture churn, and the 8-person rotation is mostly unnecessary given how rarely anything breaks (and how low the cost is when it does). The engineering investment in Stage 3 tooling would have been better spent iterating on the product itself.

**Worked example — moving too late.** A service that's quietly become company-critical (say, an internal auth service now used by 40 downstream teams) is still run as Stage 1: no formal SLO, no dedicated on-call, informal single-team support. A cascading failure (`sre/14`) triggered by one of those 40 dependents overwhelms the service, and the resulting outage is severe and slow to diagnose specifically because there's no golden-signal monitoring, no incident-command structure, and no existing SLO to even measure the damage against. The postmortem's core finding isn't really about the specific bug — it's "we should have moved this service to Stage 3 reliability practices a year ago, when it first became widely depended-upon," a maturity-mismatch finding that's much more expensive to discover reactively, during an incident, than proactively.

### Right-sizing, not maximizing, at every stage
A subtle but important point: moving to a later stage doesn't mean adopting every practice at its most rigorous setting immediately. A Stage 2 service might have a real SLO but a deliberately loose one (99% rather than 99.9%) because the cost of a tighter target (per `sre/03`'s cost/benefit reasoning) isn't yet justified by the service's current criticality — tightening the SLO itself is a later, separate maturity step, not bundled automatically with "now we have an SLO at all."

## Pros
- Prevents both failure modes symmetrically: wasted engineering investment on premature rigor, and painful reactive scrambles from under-investment in a service that's outgrown its practices.
- Gives teams and leadership a shared vocabulary (stages, transition signals) for a conversation ("are we still Stage 1 practices on a Stage 3 service?") that would otherwise be vague and easy to defer indefinitely.
- Connects every earlier lesson in this subject into one coherent, evolving system rather than a checklist to apply uniformly and permanently to every service.

## Cons
- The stage boundaries are inherently fuzzy judgment calls, not measurable thresholds — reasonable people can disagree about whether a service has crossed into needing the next stage's investment.
- Recognizing the need for a stage transition requires someone with visibility across the whole organization (not just one service's metrics), which is exactly the kind of cross-cutting responsibility that's easy for no one to clearly own.
- Moving too late is often invisible until an incident reveals it (as in the worked example above), meaning the strongest evidence for the need to invest often only arrives *after* the cost of not investing has already been paid.

## Alternatives
- **One-size-fits-all reliability policy applied uniformly to every service regardless of maturity** — simpler to communicate and govern, but as this lesson argues, produces predictable waste (over-investment in young services) and predictable risk (under-investment in services that have quietly become critical) at both ends of the spectrum.
- **Fully reactive, incident-driven maturity investment (only upgrade practices after a bad outage forces the question)** — avoids any speculative investment, but guarantees the organization learns about maturity gaps in the most expensive possible way, during a real incident, rather than proactively.
- **A rigid, calendar-based maturity schedule (e.g., "every service formalizes SLOs at month 6")** — more predictable than ad hoc judgment, but ignores that services grow in criticality at very different rates; a fixed schedule will still both over- and under-invest for services that don't match the assumed growth curve.

## When to use it
Periodically (e.g., during the quarterly SLO and capacity reviews mentioned in `sre/03` and `sre/11`) ask explicitly whether a service's current reliability practices still match its actual current criticality and scale — not just whether the practices are being executed well. Treat recurring toil growth, repeated postmortem findings pointing at the same structural gap, and growing downstream dependency as concrete signals worth escalating, rather than accepting them as background noise.

## When NOT to use it
Don't force every service toward Stage 3/4 practices as a default aspiration — most services should stay at a lighter stage indefinitely, and that's the correct, efficient outcome, not a shortcoming to be corrected. Avoid using "maturity" as a vague, unfalsifiable justification for either under-investing ("we're not mature enough yet" as a permanent excuse) or over-investing ("we should always aim for the most mature practices") — ground the decision in the concrete signals (toil trend, postmortem patterns, dependency growth) this lesson describes.

## Key takeaways / mental model
Reliability practice should track a service's actual current criticality and scale, not a fixed ideal or the practices it happened to start with. Watch for concrete signals — rising toil, repeated postmortem findings, outgrown on-call load, growing downstream dependency — that a service has quietly outgrown its current stage, and treat both premature over-investment and reactive under-investment as real, symmetric costs to avoid.

## Self-check questions
1. A 3-person team's internal tool starts getting used by a major department for daily decisions. Using the stage-transition signals from this lesson, what specific evidence would tell you it's time to move from Stage 1 to Stage 2, and what would you deliberately *not* adopt yet (i.e., stay at a lighter setting) even after making that move?
2. Explain, using the "moving too early" worked example, why applying Stage 3 practices (multi-window burn-rate alerting, hermetic builds, an 8-person on-call rotation) to a rapidly-iterating prototype is a net loss even though each individual practice is well-designed in isolation.
3. Why is "moving too late" often invisible until an incident reveals it? What would you build into an organization's regular review process (referencing `sre/03`'s or `sre/11`'s review cadences) to catch it proactively instead?
4. A service has a real SLO but leadership has never let the error budget actually freeze a release, even when exhausted. Using this lesson's framing, is this service's SLO/error-budget practice actually at Stage 2 maturity, or does it just look like it is? Justify your answer by referencing `sre/04`.

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 1 ("Introduction"), Chapter 2 ("The Production Environment at Google"), and synthesis across Parts I-IV.
- See also: `sre/04` (error budgets), `sre/05` (toil), and `sre/15` (multi-team interfaces) — this lesson's maturity stages are the throughline connecting every earlier lesson in the subject; `devops-reliability/seeking-sre` (forthcoming) picks up directly where this lesson leaves off, extending SRE practice evolution into organizational culture and strategy.
