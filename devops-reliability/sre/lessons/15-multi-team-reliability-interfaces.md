---
id: sre/15
subject: sre
title: Multi-Team Reliability Interfaces and Support Boundaries
slug: multi-team-reliability-interfaces
status: drafted
mastery:
seniority: staff
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 18
prerequisites: [sre/01, sre/04, sre/09]
created: 2026-08-10
updated: 2026-08-10
---

# Multi-Team Reliability Interfaces and Support Boundaries

## TL;DR
As an organization grows past a handful of services, reliability stops being a single team's internal practice and becomes a cross-team interface problem: which team is on the hook when a shared dependency breaks, how does an SRE team decide which services it takes on (and which it doesn't), and how do error budgets and postmortem culture stay meaningful when an incident's root cause and its user impact sit in different teams entirely. This lesson is about designing those interfaces deliberately, because an undesigned one defaults to whichever team is loudest or most available during an incident — not whichever team actually owns the fix.

## The idea
Every lesson so far in this subject (SLOs, error budgets, on-call, incident command, postmortems) was framed mostly within a single team or service's boundary. That framing breaks down at scale: a real production incident routinely spans a dependency chain of five or ten services owned by different teams, each with its own SLO, its own on-call rotation, and its own error budget — and the incident's *symptom* (a user-facing failure) and its *root cause* (a bug or capacity issue three hops upstream) are frequently owned by entirely different teams.

This creates genuinely staff-level problems that don't have clean, mechanical answers the way a single-service SLO calculation does: Whose error budget gets charged when service A's outage is actually caused by service B's bug? Should there be a dedicated SRE team for every service, or should a smaller central SRE org selectively take on only the highest-leverage services — and by what criteria? When two teams' reliability priorities conflict (team A wants to freeze releases to protect its budget; team B, whose feature depends on team A's service, has a launch deadline), who adjudicates? These are org-design and negotiation problems, not calculations.

## How it works

### The SRE engagement model: not every service gets dedicated SRE
Google's SRE org doesn't take on every internal service — the book describes an explicit **launch and production readiness review (a variant: PRR)** gate: a service requesting dedicated SRE support must meet a bar (demonstrated reliability practices already in place, sufficient scale/criticality to justify the investment, a workable on-call/monitoring baseline already built by the product team) before an SRE team takes it on. This is deliberate scarcity: SRE headcount doesn't scale linearly with the number of services in the company, so it must be allocated to the highest-leverage places, and the PRR process makes that allocation decision explicit and criteria-based rather than political.

**Worked example.** A product team building a new internal analytics dashboard requests dedicated SRE support. The PRR process asks: does this service have real business-criticality (is downtime costly)? Does the team already have basic monitoring, an on-call rotation, and a defined SLO, even a rough one? Is the architecture reviewed for obvious scaling or single-point-of-failure risk? If the answers are mostly "not yet," SRE's response isn't automatically "no" — it's typically a set of concrete readiness requirements the team must meet first (build basic monitoring, define an SLO, demonstrate a functioning on-call rotation for some period) before SRE resourcing is committed. This protects SRE capacity from being spread too thin across services not yet mature enough to benefit from it, and gives the requesting team a clear, actionable bar rather than an opaque rejection.

### Consulting vs. embedded SRE engagement
Not every service that meets the bar gets a permanently embedded SRE team. The book describes a spectrum: a **consulting engagement** (SRE advises on architecture and practices for a bounded period, then hands full ownership back to the product team) versus a **fully embedded** model (SRE holds the pager and owns production operations of the service long-term). **Worked example.** A team launching a new but lower-risk internal service might get a 6-week consulting engagement — SRE helps them design SLOs, set up golden-signal monitoring, and establish an on-call rotation — after which the product team runs it themselves. A company-critical, extremely high-traffic service (like the checkout API used throughout this subject) is more likely to warrant a fully embedded SRE team indefinitely, given the scale of impact if it fails.

### Charging error budget across a dependency chain
When an incident's symptom and root cause span two teams, the book's guidance is to attribute the SLO/error-budget impact to the team whose service the *user actually experienced the failure through* (the symptom owner), while the postmortem's action items get assigned to whichever team owns the actual root cause — these are not the same team, and conflating them creates perverse incentives. **Worked example.** Service A (checkout) depends on Service B (a shared authentication service). Service B has a bug causing 8 minutes of failed auth checks, which manifests to users as checkout failures. Checkout's (Service A's) SLO absorbs the budget hit, because that's what users actually experienced — but the postmortem's root-cause action items are owned by the authentication team (Service B), because that's where the actual fix belongs. If instead Service B's budget were charged (since it was the "cause"), Service A's team would have no visibility into or stake in fixing a problem that keeps happening to *their* users — the attribution rule keeps the incentive aligned with who the user actually experiences the failure through, while the fix ownership stays aligned with who can actually fix it.

### Support boundaries and escalation contracts between teams
A dependency relationship needs an explicit interface contract, not an implicit assumption: what SLO does the upstream team commit to for the downstream team's use case, what's the escalation path when the upstream service is suspected as an incident's root cause, and who has authority to page the upstream team directly during an active incident versus needing to go through a slower support-ticket channel. **Worked example.** The checkout team and the authentication team formalize: authentication commits to a 99.95% SLO specifically for checkout's traffic pattern (not just its aggregate SLO across all consumers, which might mask checkout-specific degradation); checkout's on-call has a direct paging path to authentication's on-call during a declared incident (bypassing the normal ticket queue); and authentication commits to being included as a stakeholder in any postmortem where their service is identified as a contributing cause. Without this kind of explicit contract, the default behavior during a real incident is often confusion about who to even contact, adding minutes or hours to resolution exactly when `sre/09`'s incident-command structure is trying to move fast.

### When priorities conflict across teams
A recurring staff-level problem: team A's error budget is exhausted and its policy says freeze releases, but team B's roadmap depends on a change to team A's service for an already-announced launch. The book doesn't offer a mechanical formula here — it frames this explicitly as a negotiation that needs an escalation path to a shared manager or leadership when the two teams can't resolve it directly, precisely because a purely bottom-up, team-by-team error-budget policy has no built-in way to arbitrate genuine cross-team conflicts of priority. The important discipline is that this escalation happens *openly*, with the error-budget data as shared evidence both sides look at, rather than either team unilaterally overriding the other's stated policy.

## Pros
- Explicit PRR-style engagement criteria protect scarce SRE capacity from being spread indiscriminately across every service, directing it to where it has the most leverage.
- Clear error-budget attribution rules (charge the symptom owner, assign fixes to the root-cause owner) keep incentives aligned across team boundaries instead of creating finger-pointing or misdirected accountability.
- Explicit interface contracts between dependent teams (SLO commitments, escalation paths) remove ambiguity during exactly the highest-pressure moments (an active incident spanning teams).

## Cons
- PRR-style gating adds real process overhead and can feel like an obstacle to teams whose service genuinely needs help but doesn't yet meet the readiness bar — striking the right bar (not too strict, not too lax) is itself a hard, ongoing judgment call.
- Cross-team error-budget attribution requires trust and shared tooling (both teams need to see the same incident data) that many organizations, especially ones without a mature SRE culture yet, don't have in place.
- Escalating genuine cross-team priority conflicts to leadership doesn't scale well if it happens often — it's meant to be a rare release valve, not a routine decision-making channel, and an organization that needs it constantly likely has a deeper structural misalignment.

## Alternatives
- **Every team fully self-sufficient, no dedicated or consulting SRE at all** — avoids the engagement-model overhead entirely, but leaves each team to reinvent SLO, monitoring, and incident-command practices independently, with uneven quality and no cross-team consistency in how dependencies are handled.
- **A single centralized ops team responsible for all services uniformly** — simpler org chart, avoids the "who gets SRE" allocation question, but doesn't scale expertise or context the way a selective, criteria-based engagement model does, and tends to become a bottleneck as the number of services grows.
- **No formal cross-team SLO/escalation contracts, handled ad hoc per incident** — lower upfront coordination cost, but reliably produces confusion and delay during real incidents about who to contact and who owns the fix, exactly when speed matters most.

## When to use it
Design explicit multi-team reliability interfaces once an organization has enough services and enough real cross-team dependencies that incidents routinely span team boundaries — typically well past the single-team-per-service scale this subject's earlier lessons assume. Use PRR-style criteria to allocate scarce dedicated SRE capacity, and formalize SLO/escalation contracts for any dependency relationship significant enough that its failure would materially affect the downstream team's own SLO.

## When NOT to use it
Don't build formal PRR gates, cross-team SLO contracts, or complex budget-attribution rules for a small organization where every team can reasonably coordinate informally and incidents rarely span more than one or two teams — the coordination overhead isn't justified yet. Revisit as the dependency graph and team count grow.

## Key takeaways / mental model
Past a certain scale, reliability is an interface problem between teams, not just a practice within one. Allocate scarce SRE capacity deliberately (PRR-style criteria), charge error-budget impact to whoever the user experienced the failure through while assigning fixes to whoever owns the actual cause, and make dependency contracts (SLOs, escalation paths) explicit before an incident forces the question under pressure.

## Self-check questions
1. Service X's outage is caused by a bug in Service Y, three hops upstream, that Service X depends on indirectly. Explain which team's error budget should be charged and which team should own the postmortem's action items, and why those are not necessarily the same team.
2. A team requests dedicated embedded SRE support for a new service with 200 daily users and no defined SLO yet. Using the PRR framework from this lesson, what would you tell them, and what concrete steps would you ask them to take first?
3. Team A's error budget is exhausted and their policy freezes releases, but Team B has an externally announced launch depending on a Team A API change. Describe how this lesson says the conflict should be resolved, and why a purely bottom-up, single-team error-budget policy doesn't have a built-in answer to this.
4. Why does the book distinguish a "consulting" SRE engagement from a "fully embedded" one, and what factors would push a service toward one model over the other?

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 18 ("Software Engineering in SRE") and the Part IV management chapters on SRE team engagement models.
- See also: `sre/04` (error budgets, whose cross-team attribution this lesson extends), `sre/09` (incident command, which this lesson's escalation contracts feed into during multi-team incidents), and `devops-reliability/seeking-sre` (forthcoming) for how these organizational interfaces evolve as SRE practice matures further.
