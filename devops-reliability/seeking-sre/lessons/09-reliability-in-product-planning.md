---
id: seeking-sre/09
subject: seeking-sre
title: Embedding Reliability in Product Planning and Prioritization
slug: reliability-in-product-planning
status: drafted
mastery:
seniority: staff
source: Seeking SRE (David Blank-Edelman, ed.), essay on getting reliability work onto the roadmap instead of treated as overhead
prerequisites: [seeking-sre/02, seeking-sre/06]
created: 2026-08-10
updated: 2026-08-10
---

# Embedding Reliability in Product Planning and Prioritization

## TL;DR
Reliability work loses every unstructured competition against visible feature work for roadmap space, because features have an obvious champion (product) and a legible payoff (new revenue, a demo-able launch) while reliability's payoff is an absence (incidents that didn't happen) — so reliability has to be embedded into the planning process itself, as a structural line item with its own advocate and its own budget, rather than left to compete feature-by-feature.

## The idea
A recurring failure pattern: a company builds real SRE practice (SLOs, error budgets, on-call, postmortems — this subject's earlier lessons) but still finds that reliability improvements identified in postmortems never actually get scheduled, because every planning cycle, a reliability fix competes one-on-one against a feature with a named revenue number and an executive sponsor, and loses. The reliability fix is real, and everyone agrees it's important in the postmortem meeting — but "important" without a designated claim on roadmap capacity quietly becomes "someday," and someday incidents recur.

The book's framing: this isn't a prioritization failure by any individual product manager acting in bad faith — it's a structural mismatch. Feature work and reliability work are evaluated with different, incompatible logics (one is a bet on future upside with a visible advocate, the other is risk reduction with a diffuse, easy-to-defer cost), and structural fixes (reserved capacity, joint OKRs, error-budget-linked roadmap rules) are what actually change the outcome, not appeals to "we should care about reliability."

## How it works

### Reserved capacity, stated as a policy not a request
The single most direct fix: a standing rule that a fixed percentage of every team's roadmap capacity (commonly 15-25%, and this should be tuned to the service's actual risk profile, not copied blindly) is reserved for reliability and technical-health work, decided by the team itself rather than re-litigated feature-by-feature every planning cycle. The critical detail that makes this work versus becoming another line item that gets silently raided under pressure: the reservation needs an owner with the authority to say no to a feature push that would violate it — usually an engineering lead, explicitly empowered by whoever the product organization ultimately answers to, so "no, that violates our reliability reservation" isn't a junior engineer's unilateral, overridable opinion.

### Linking error-budget state directly to roadmap rules
`sre/04` and `seeking-sre/06` establish error budgets as both a technical governance mechanism and a stakeholder-communication tool. This lesson closes the loop into planning: an explicit rule that when a service's error budget is exhausted, a defined portion of the *next* planning cycle's capacity for that team is automatically allocated to reliability work addressing the causes, without requiring a fresh prioritization argument each time. This converts a postmortem action item from "a suggestion competing against features" into "an already-scheduled consequence of the budget being spent" — removing the recurring, exhausting need to re-win the same argument every cycle.

### Worked example: the postmortem action item graveyard
A company's postmortems consistently identify good, specific action items (add a circuit breaker here, fix a known race condition there), but a review after a year shows only 30% were ever completed — most sit in the backlog indefinitely, re-surfacing each time a related incident recurs, met with "yeah, we know, it's on the list." The fix implemented: every postmortem action item gets an explicit due date and owner *at postmortem time*, and it's added not to a generic backlog but to a dedicated "reliability capacity" board that draws from the reserved-capacity policy above — so it has a real claim on a real sprint, not a hope. Six months later, completion rate is tracked and reported in the recurring stakeholder review (`seeking-sre/06`) as one of the concrete metrics of whether the SRE program is working (`seeking-sre/11`).

### Joint OKRs as an alternative or complement to reserved capacity
Instead of (or alongside) a fixed percentage reservation, some teams frame reliability as a shared objective between product and platform/reliability functions: a joint OKR like "maintain 99.9% availability on checkout while shipping the Q3 roadmap" makes reliability an explicit, shared success criterion for the *same* team that owns the features, rather than a separate competing initiative. This works especially well in the embedded ownership model (`seeking-sre/02`) where the product team already owns its own reliability — it reframes reliability not as "work stolen from features" but as "a condition the feature work has to satisfy," which changes the psychology of the trade-off entirely.

### Making the trade-off visible at planning time, not just execution time
Even with reserved capacity, planning conversations benefit from a lightweight but explicit risk-tagging step: when a new feature is being scoped, ask "does this materially change our traffic pattern, failure surface, or data model in a way that affects our current reliability posture?" and if yes, require a brief reliability review (drawing on the ownership-contract thinking from `seeking-sre/02`) *before* the feature is scheduled, not after it ships and causes an incident. This is cheap (a checklist question, a short review) compared to the cost of discovering the same risk via an outage.

## Pros
- Converts reliability from a recurring, exhausting argument into a structural default, dramatically improving the odds that identified fixes actually get done.
- Reduces the "postmortem action item graveyard" pattern where known risks are documented repeatedly but never actually addressed.
- Aligns incentives by making reliability a shared success condition (joint OKRs) rather than a competing initiative that pits product against reliability.

## Cons
- Reserved capacity is genuinely unpopular during periods of real competitive or revenue pressure, and it will be tested — someone with authority has to actually hold the line, which takes organizational courage.
- A percentage-based reservation is a blunt instrument; it can over-allocate to genuinely low-risk services and under-allocate to genuinely high-risk ones if applied uniformly rather than tuned per service.
- Joint OKRs can be gamed by setting an easy reliability target that doesn't reflect real risk, undermining the mechanism's intent while still checking the box.

## Alternatives
- **Case-by-case prioritization with strong reliability advocacy (no structural reservation)** — relies entirely on a skilled advocate (per `seeking-sre/06`) winning the argument every cycle; lower structural overhead but reverts to the postmortem-graveyard failure mode the moment that advocate is unavailable or overruled once.
- **A fully separate reliability team with its own independent roadmap and budget** — sidesteps the competition for shared roadmap capacity entirely by giving reliability work its own lane (ties to the centralized/platform model in `seeking-sre/01`); effective at removing the competition but risks the reliability work being disconnected from product teams' actual priorities.
- **Executive mandate with no structural mechanism ("reliability matters, make it happen")** — the weakest alternative; without reserved capacity or linked rules, a mandate alone tends to produce the same graveyard pattern under the next deadline crunch, because good intentions don't survive contact with a real prioritization trade-off.

## When to use it
Introduce reserved capacity or joint OKRs as soon as you observe the postmortem-graveyard pattern (known action items repeatedly not completed) or as soon as error budgets exist as a real governance mechanism (`sre/04`) that needs a way to actually influence the next planning cycle, not just the current release decision.

## When NOT to use it
Don't impose a uniform reserved-capacity percentage across services with very different risk profiles without tuning it — a low-risk internal tool doesn't need the same 20% reservation as a revenue-critical, customer-facing service, and treating them the same wastes capacity on one and under-protects the other. Don't rely on joint OKRs alone in a culture where OKR targets are routinely set conservatively to guarantee they're hit — that incentive undermines genuine reliability investment.

## Key takeaways / mental model
Reliability loses feature-by-feature prioritization fights by structural design, not bad faith — features have visible advocates and legible upside, reliability has an invisible, diffuse payoff (incidents that didn't happen). Fix the structure, not the argument: reserve real roadmap capacity with an empowered owner, link error-budget exhaustion directly to scheduled follow-up work, and consider joint OKRs to reframe reliability as a shared success condition rather than a competing initiative.

## Self-check questions
1. A company's postmortems consistently identify good action items, but only 30% are ever completed a year later. Diagnose the structural cause this lesson identifies, and propose the specific mechanism that would fix it.
2. Why does the lesson argue that reserved capacity needs an "owner with the authority to say no," and what happens to the policy without one?
3. Compare reserved-capacity percentages and joint OKRs as mechanisms for embedding reliability into planning. When would you prefer one over the other?
4. How could a joint OKR ("maintain 99.9% availability while shipping the roadmap") be gamed, and what would you check for to make sure it's a genuine commitment rather than a box-checking exercise?

## References
- Seeking SRE (David Blank-Edelman, ed.), essay on getting reliability work onto the roadmap instead of treated as overhead.
- See also `seeking-sre/02` (ownership boundaries, since embedded ownership shapes how joint OKRs work) and `seeking-sre/06` (stakeholder communication, the advocacy skill this lesson's structural fixes are meant to reduce reliance on).
