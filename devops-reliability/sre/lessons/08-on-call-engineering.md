---
id: sre/08
subject: sre
title: "On-Call Engineering: Rotations, Load, and Sustainability"
slug: on-call-engineering
status: drafted
mastery:
seniority: senior
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 11
prerequisites: [sre/07]
created: 2026-08-10
updated: 2026-08-10
---

# On-Call Engineering: Rotations, Load, and Sustainability

## TL;DR
On-call is a designed system with explicit limits, not just "whoever's turn it is answers the phone." The book sets concrete bounds — enough engineers per rotation to keep any individual's on-call load sustainable, and caps on both the volume of incidents per shift and the fraction of time spent actively handling them — because an overloaded, under-staffed on-call rotation degrades both incident response quality and engineer retention.

## The idea
On-call exists because someone has to be reachable when an alert (`sre/07`) fires outside business hours. The naive approach — a rotating pager with no limits on team size, shift length, or incident volume — tends to fail in one of two ways: either too few people share the burden (each person is on-call too often, leading to burnout and eventually attrition), or the volume of pages per shift is too high for any one person to handle carefully (leading to rushed, low-quality incident response, or pages being silenced/ignored out of self-preservation).

The book's framing is that on-call load is a resource to be engineered and budgeted, just like toil (`sre/05`) or error budget (`sre/04`) — with explicit numeric guidelines, not vibes, because "how much on-call is too much" is exactly the kind of question that degrades slowly and invisibly until someone burns out or quits.

## How it works

### Sizing the rotation
The book's rule of thumb: a healthy on-call rotation needs a minimum of **6-8 engineers** (across sites/time zones ideally, so any individual isn't disproportionately hit by their region's business hours) to keep the frequency of any one person's on-call shifts sustainable. Fewer than that, and each person is on-call too often relative to their non-on-call working life.

**Worked example.** A team of 4 engineers running a weekly on-call rotation means each person is on-call one week in four — 25% of all weeks, indefinitely. Compare to a team of 8: each person is on-call one week in eight (12.5%), with 7 weeks between rotations to recover, do focused engineering work, and not have on-call anxiety hanging over normal working weeks. The difference isn't just comfort — infrequent on-call means each shift starts from a well-rested, non-burned-out baseline, which directly affects incident-response quality (`sre/09`).

### Bounding shift load: the two caps
Within a shift, the book recommends bounding both:
- **Number of incidents per shift** — a guideline of roughly **no more than ~2 significant events per 12-hour on-call shift** on average; more than that consistently signals either the alerting is too noisy (`sre/07`) or the underlying system has real reliability problems needing engineering investment, not just more on-call capacity.
- **Time spent actively engaged, not just reachable** — a target that active incident-handling time stays under roughly **25-30% of the shift**; being on-call is supposed to mean "reachable while doing something else" most of the time, not "consumed by firefighting."

**Worked example.** An on-call engineer logs 5 pages over a 12-hour shift, each requiring 40 minutes of focused response: 5 x 40 = 200 minutes of active engagement out of 720 minutes on shift ≈ 28% — right at the edge of sustainable, and 5 pages is well above the ~2-per-shift guideline. This is a quantifiable signal (much like toil measurement, `sre/05`) that the underlying system needs reliability work, or the alert set needs tuning for precision, before the next rotation — not just "the on-call person should try to keep up."

### Compensating for on-call burden
The book notes Google explicitly compensates on-call time (extra pay or equivalent time off), separate from base salary, precisely because being interruptible outside working hours is a real cost to the person even on a quiet shift — treating it as free is a hidden subsidy the engineer pays for out of their personal life. This also creates a useful economic signal: if on-call compensation costs are rising because shift frequency or load is increasing, that cost is visible in a budget line, which helps make the case for headcount or reliability investment in the same way the error budget makes reliability trade-offs visible to product stakeholders.

### Escalation paths and the secondary on-call
A single point of failure in the rotation (one primary on-call, no backup) means a missed page (phone died, no signal, asleep through the alert) has no fallback. The book's standard structure: a **primary** on-call who gets paged first, with an **escalation policy** that pages a **secondary** on-call (or the primary's manager, or a broader team alias) if the primary doesn't acknowledge within a defined window (e.g., 5-10 minutes). **Worked example.** A primary on-call doesn't acknowledge a page within 8 minutes (phone on silent); the paging system automatically escalates to the secondary, who acknowledges within 2 minutes and begins response — total delay from alert to human response: 10 minutes instead of an unbounded wait. The escalation window is itself a tuned parameter: too short, and the secondary gets paged unnecessarily whenever the primary is just slightly slow to check their phone; too long, and real incidents sit unattended for longer than the SLO's error budget can tolerate (tie this window to the fast-burn alert's urgency from `sre/07`).

### Handoffs and shift transitions
A clean handoff between outgoing and incoming on-call — a short written or verbal summary of ongoing issues, recent changes, anything to watch — prevents context loss at exactly the moment it's most costly (the start of a new shift, when the incoming engineer has the least situational awareness). **Worked example.** An outgoing on-call flags: "we deployed a config change to the caching layer at 4pm that hasn't fully rolled out yet; if you see elevated cache-miss rate in the next few hours, check the rollout status before escalating as a new incident." Without this handoff, the incoming engineer might spend 30+ minutes re-diagnosing a known, already-understood condition from scratch.

## Pros
- Explicit numeric guidelines (rotation size, incidents/shift, active-engagement fraction) turn "is our on-call sustainable?" into a measurable, trackable question instead of a vague morale issue that surfaces only after someone quits.
- Compensating on-call burden explicitly makes its real cost visible to the organization, supporting the case for headcount or reliability investment when load grows.
- A defined escalation path bounds the worst-case response delay when a primary on-call is unreachable, rather than leaving it open-ended.

## Cons
- The 6-8 person minimum rotation size is a real staffing cost many teams, especially smaller ones or early-stage products, can't afford — smaller teams must either accept less sustainable rotations or find another way to share the load (e.g., across a broader org).
- Enforcing shift-load caps (~2 incidents/shift, ~25-30% active time) requires the alerting discipline from `sre/07` already being in place; a team with noisy alerts will blow past these caps regardless of rotation size.
- On-call compensation adds real budget cost, which can create organizational friction if not planned for, especially as team size or shift frequency changes.

## Alternatives
- **"Whoever's available" informal on-call, no fixed rotation** — lower overhead to set up, but load distribution is unpredictable and tends to concentrate on whoever is most responsive or most senior, leading to uneven burnout risk.
- **Follow-the-sun on-call across time zones** — instead of a single person covering off-hours, route pages to whichever region is currently in business hours; avoids night-time pages entirely, but requires a genuinely distributed team across compatible time zones and careful handoff discipline between regions.
- **Fully centralized NOC (network operations center) triage** — a dedicated 24/7 team handles first response and escalates to engineering only when needed; reduces load on individual engineers' personal time, at the cost of a slower, less-informed first response compared to the engineer who built the system being paged directly.

## When to use it
Apply explicit rotation-size, shift-load, and escalation-path design to any team with production on-call responsibility, and treat exceeding the shift-load guidelines as a trigger for reliability investment or alert tuning (`sre/07`), not just something the current on-call person has to push through.

## When NOT to use it
Don't force a rigid 6-8 person, heavily formalized on-call structure onto a very small team or an early-stage service where the operational load is genuinely low and infrequent — the overhead of building compensation policy, escalation tooling, and formal rotations can exceed the benefit until the service and team are large enough to need it. A lighter, informal arrangement (with an honest eye on whether it's actually sustainable) is a reasonable precursor.

## Key takeaways / mental model
On-call load is a budget, like toil or error budget: size the rotation so no individual carries too much of it, cap the volume and active-engagement time per shift, and treat exceeding those caps as a signal to fix the system (better alerts, more reliability engineering) rather than a signal to ask people to endure more. A clean escalation path and handoff are the safety net for the inevitable case where a shift doesn't go as planned.

## Self-check questions
1. A 5-person team runs a weekly on-call rotation. Using this lesson's guidelines, identify the specific sustainability problem and propose two different structural fixes (not "just tough it out").
2. An on-call engineer logs 6 significant pages in one 12-hour shift, each taking about 25 minutes to resolve. Compute the active-engagement percentage and explain what this data should trigger, referencing `sre/07`.
3. Why does the book recommend a secondary on-call and an automatic escalation window, rather than relying on the primary always being reachable? What would you set the escalation window to, and what tradeoff does that window length represent?
4. Explain why Google explicitly compensates on-call time separately from base salary, and how this connects to the same "make the hidden cost visible" logic behind the error budget (`sre/04`).

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 11 ("Being On-Call").
- See also: `sre/07` (alerting design, which determines shift load) and `sre/09` (incident command, for what happens once a page is acknowledged).
