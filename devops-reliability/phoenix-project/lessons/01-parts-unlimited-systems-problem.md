---
id: phoenix-project/01
subject: phoenix-project
title: The Parts Unlimited Crisis as a Systems Problem
slug: parts-unlimited-systems-problem
status: drafted
mastery:
seniority: senior
source: The Phoenix Project (Kim, Behr, Spafford), Part 1
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# The Parts Unlimited Crisis as a Systems Problem

## TL;DR
When an IT organization is drowning in outages, missed deadlines, and firefighting, the instinctive response is to blame individuals ("this engineer made a mistake," "that manager didn't plan well enough"). The durable lesson from Parts Unlimited's near-collapse is that chronic, repeating IT crises are almost always a **systems problem**: a small number of structural conditions (no visibility into total work, no shared prioritization, unmanaged dependencies, unlimited unplanned work) reliably produce the same failures regardless of who staffs the roles. Fix the system, not the people, or you will keep replacing "the person who caused the outage" and get the same outage next quarter.

## The idea
In the novel, Bill Palmer is abruptly promoted to VP of IT Operations at Parts Unlimited, a company whose IT department is in a state of near-permanent emergency: the Phoenix Project (a critical, over-budget, repeatedly-delayed initiative) is about to have a botched rollout, payroll processing is at risk of failing, and every week brings a new fire that consumes the best engineers' entire attention. The company's instinct — expressed by executives and by Bill's own initial reflexes — is to look for someone to blame or fire: the engineer who pushed the bad change, the manager who "let" the deadline slip, the vendor who delivered late.

The book's founding insight, which everything else in the subject builds on, is that this framing is a category error. A crisis that recurs across different projects, different teams, and different individual engineers is not a personnel problem; it is evidence of a **system that reliably produces failure**, the way a factory with a broken machine on the line will produce the same defect no matter which operator staffs that station. W. Edwards Deming's management theory (which heavily influenced the book, particularly through the character Erik) makes this explicit: the vast majority of quality and performance problems in an organization come from the system — its structure, incentives, and processes — not from the competence or diligence of the people working inside it. Firing or shaming individuals inside a broken system doesn't fix the system; it just changes who burns out next.

This matters for engineers and engineering leaders because it changes where you look for a fix. If you treat a bad deploy as "an individual made a mistake," your remedy is discipline, blame, or replacing the person. If you treat it as "the system allowed an under-tested, poorly-reviewed, high-risk change to reach production during a period of unmanaged, unprioritized parallel work," your remedy is structural: change what work is allowed to happen, how it flows, and what safety nets exist. Only the second framing produces a fix that survives personnel turnover.

## How it works

### Recognizing the pattern: symptoms vs. root cause
Parts Unlimited exhibits a cluster of symptoms that, individually, each looks like a local, explainable failure: a database change that takes down authentication (attributed to "a junior DBA's mistake"), the Phoenix Project rollout collapsing under load ("the vendor's SAN wasn't sized correctly"), payroll at risk ("HR didn't communicate the deadline"). Each explanation is locally true and globally useless — it identifies *a* proximate cause without asking why the system made that cause both likely and catastrophic.

The systems-thinking move is to ask, for each incident: *would a different, equally competent person in this same role, under these same structural conditions, have been likely to produce a similar outcome?* If the answer is yes, the fix belongs at the system level (the volume of concurrent unprioritized work, the absence of a change-review gate, the lack of a staging environment that mirrors production) rather than at the individual level. Bill's arc across the book is precisely this: he starts by hunting for who to blame per incident, and only gains traction once he starts asking what conditions in the plant (his own literal manufacturing-plant background gives him this vocabulary) make failure the expected outcome rather than the exception.

**Worked example.** Imagine a 40-engineer product organization where, over one quarter, three unrelated production incidents each get attributed to "the engineer who wrote the bad code": a config change that leaked credentials, a migration that locked a table for 20 minutes during peak traffic, and a feature flag that shipped to 100% of users instead of 1%. Investigated individually, each has a distinct "root cause" and a different guilty party — three different remedial actions (retrain engineer A, add a checklist item for engineer B, add a confirmation dialog for engineer C). Investigated as a system, a single pattern emerges: none of the three changes went through a peer review or staged rollout process, because the team's review process is informally skipped whenever a delivery deadline is tight — and deadlines have been tight for the last two quarters because of chronic overcommitment. The system-level fix (a required, non-skippable review-and-staged-rollout gate, and a serious look at why the team is chronically overcommitted) prevents the *next* incident, whoever causes it; the three individual fixes do not.

### The trap of "IT is a black box" thinking to the business
A second structural condition the book surfaces: business leadership at Parts Unlimited treats IT as an opaque cost center that should simply execute requests, without visibility into IT's actual capacity or the dependencies between projects. Steve Masters (the CEO) and other executives keep adding urgent initiatives — the Phoenix Project, a new compliance requirement (SOX-404 audit findings), routine "keep the lights on" work — without any shared view of how much total capacity IT has, so every new ask is treated as if it were free. This is a systems problem at the organizational level: IT's work is invisible to the people making commitments on IT's behalf, so the business systematically over-promises and IT systematically fails to deliver, and each side blames the other's competence rather than the shared lack of a visibility mechanism. This directly motivates `phoenix-project/02` (treating work as flow you can see and measure) — you cannot fix what you cannot see, and Parts Unlimited's crisis is, underneath the specific outages, a visibility failure.

### Why "get better people" doesn't fix a systems problem
A natural objection: doesn't more competence help? It does, but only up to the ceiling the system imposes. A brilliant engineer dropped into a system with no WIP limits (`phoenix-project/04`), no change gate, and constant context-switching will still produce worse outcomes than a merely competent engineer working inside a well-designed system — because the system, not raw skill, determines how much of that skill actually reaches the work. Parts Unlimited's most technically gifted engineer, Brent, is simultaneously the company's biggest single point of failure precisely *because* the system routes every hard problem to him with no queue, no documentation, and no cross-training — a systems failure that swallows his individual excellence and converts it into organizational fragility (this becomes central to `phoenix-project/03` and `phoenix-project/04`).

## Pros
- Produces fixes that survive personnel turnover, because they target the structural conditions that produce failure rather than the specific person present when it last happened.
- Reduces the blame-and-fear culture that suppresses the honest reporting needed to actually find root causes (a precondition for `phoenix-project/06`'s feedback loops).
- Redirects scarce leadership attention toward the handful of structural levers (visibility, prioritization, WIP, review gates) that improve outcomes across every future incident, not just the last one.

## Cons
- Systems thinking can become an excuse to avoid ever holding anyone accountable for genuine negligence or repeated individual failure — the discipline requires distinguishing systemic causes from real individual performance issues, not eliminating individual accountability entirely.
- It is slower and less politically satisfying than finding a scapegoat: executives and stakeholders often want a fast, visible response to an incident, and "we're going to restructure how work is prioritized" doesn't provide the same immediate reassurance as "we fired the person responsible."
- Diagnosing the actual systemic cause takes real investigative discipline (the kind of root-cause analysis in `phoenix-project/06`); done poorly, "it's a systems problem" becomes a vague, unfalsifiable excuse rather than a specific, actionable diagnosis.

## Alternatives
- **Individual accountability model** — treat each incident as caused by an identifiable individual's action and respond with retraining, discipline, or replacement; appropriate only when an incident truly is an isolated case of negligence or misconduct rather than part of a recurring pattern, and dangerous when applied to systemic failures because it never touches the actual cause.
- **Pure process/compliance overlay** — add more approval gates, checklists, and sign-offs without changing the underlying flow or prioritization system; treats the symptom (risky changes reaching production) without treating the cause (unmanaged, unprioritized, excessive concurrent work), often just slowing everything down without reducing incident rates.
- **Vendor/tooling replacement** — assume better tools (a new monitoring stack, a new deployment platform) will resolve the crisis; useful as a complement but insufficient alone, since Parts Unlimited's core problem is how work is chosen and sequenced, not what tools execute it.

## When to use it
Reach for systems-level diagnosis whenever failures are *recurring* across different people, teams, or projects, or whenever the "root cause" explanations for a string of incidents all sound plausible individually but never seem to reduce the incident rate. It is the right lens for any leader inheriting a chronically firefighting organization, and the necessary first step before any of this subject's later concepts (constraints, flow, WIP limits) can be applied meaningfully — you cannot manage a system's flow until you've stopped treating its failures as isolated personnel events.

## When NOT to use it
Do not use systems-level framing to excuse a genuinely isolated case of negligence, dishonesty, or a one-off individual performance failure unconnected to any structural pattern — collapsing every incident into "the system's fault" removes legitimate accountability and can itself become a way to avoid difficult but necessary personnel conversations. It's also the wrong lens for a single, non-recurring incident with a clear, unusual proximate cause (e.g., a genuine one-time hardware failure) where there is no broader pattern to diagnose.

## Key takeaways / mental model
Before asking "who caused this," ask "would this have happened to almost anyone in this role, given how work reaches them and how much of it there is?" If yes, the fix lives in the system (visibility, prioritization, WIP, review gates), not in the person. A crisis that keeps recurring with different people attached to it is always telling you where the system, not the staff, needs to change.

## Self-check questions
1. A team has had three "bad deploy" incidents in a quarter, each blamed on a different engineer's mistake. What single question would you ask to test whether this is a systems problem rather than three unrelated individual failures?
2. Explain why Brent, the most technically skilled engineer at Parts Unlimited, is simultaneously an asset and the company's biggest systemic risk. What structural condition (not skill level) creates this?
3. Give an example, from your own experience or a plausible one, of an incident where the individual-accountability response would be the *correct* one rather than a systems-thinking response — what makes it different from a recurring pattern?
4. Why does "IT is a black box to the business" count as a systems problem rather than a business-leadership competence problem? What structural fix (rather than a competence fix) would address it?

## References
- The Phoenix Project: A Novel about IT, DevOps, and Helping Your Business Win (Kim, Behr, Spafford), Part 1.
- See also `phoenix-project/02` (making work visible as flow) and `phoenix-project/03` (Theory of Constraints), which build directly on this systems framing.
