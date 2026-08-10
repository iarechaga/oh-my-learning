---
id: seeking-sre/08
subject: seeking-sre
title: Managing Toil at Organizational Scale
slug: org-scale-toil-management
status: drafted
mastery:
seniority: staff
source: Seeking SRE (David Blank-Edelman, ed.), essay on applying toil-reduction principles with a 5-person team instead of Google's automation budget
prerequisites: [seeking-sre/04]
created: 2026-08-10
updated: 2026-08-10
---

# Managing Toil at Organizational Scale

## TL;DR
Google's toil-reduction playbook assumes you can dedicate real engineering time (sometimes whole teams) to building automation that eliminates categories of manual work; a 5-person team doesn't have that luxury, so the adapted version of toil management is about ruthless prioritization of the highest-value 20% of toil, cheap "good enough" fixes over comprehensive automation, and treating toil visibility itself (making it countable and trended) as the first and cheapest intervention.

## The idea
Google's SRE book (see `sre/05`'s toil-elimination framing, referenced here at a higher organizational level) treats toil — repetitive, manual, automatable operational work with no enduring value — as something to be measured and driven toward zero via dedicated automation investment, often justified because at Google's scale, eliminating an hour of recurring toil per week can be worth an engineer's full-time salary once multiplied across enough services and enough years. That math doesn't work the same way for a 5-person team: building a robust automation system to eliminate 2 hours a week of toil might cost 3 weeks of one engineer's time that the team genuinely cannot spare, making the "proper" fix net-negative in the near term even though it's clearly correct in principle.

The book's adaptation: toil management at small scale is less about comprehensive automation and more about **triage under real capacity constraints** — deciding, honestly, which toil is worth fixing now, which is worth a cheap partial fix, and which is worth just tolerating for now, with visibility as the mechanism that makes those trade-offs deliberate instead of accidental.

## How it works

### Toil visibility as the first, cheapest intervention
Before any automation investment, the single highest-leverage move for a small team is simply **tracking toil time explicitly** — even a rough weekly tally ("roughly how many hours this week went to repetitive manual work: deploys, log-digging for known issues, manual scaling, access requests") logged in a shared doc or a lightweight time-category tag on tickets. This alone often surfaces surprises: a team might discover that one specific recurring task (manually rotating a credential every two weeks, taking 45 minutes each time but requiring careful, error-prone steps) accounts for a disproportionate share of toil, becoming an obvious, cheap automation target — obvious only once measured, easy to miss when it's spread thin across many people's memory.

### Prioritizing under real capacity constraints
With a rough toil inventory in hand, a 5-person team should triage using two axes: **frequency/total time cost** and **fix cost**. This produces four honest categories:
- **High cost, cheap fix** — automate immediately; this is where nearly all of a small team's toil-reduction budget should go (the credential-rotation example above: 45 minutes every 2 weeks, but a fix might be a half-day script).
- **High cost, expensive fix** — the hardest category; often the temptation is to ignore it because the fix is too big, but this is exactly where a *partial*, "good enough" fix (see below) earns its keep.
- **Low cost, cheap fix** — worth doing opportunistically (in slack time, or bundled into other work) but never worth interrupting planned work for.
- **Low cost, expensive fix** — explicitly deprioritize and say so out loud; this is the category most small teams waste effort on by fixing "because it's annoying," not because it's high-leverage.

### The "good enough" partial fix, as a first-class strategy
Where Google's scale often justifies building a fully general, robust automation system, a 5-person team should actively prefer a narrower, uglier fix that eliminates 80% of a toil category's cost for 20% of the effort. Worked example: a team manually re-provisions a test environment every time a QA engineer needs a fresh one, taking about 90 minutes and requiring a specific senior engineer who "just knows the steps." A fully general self-service provisioning platform might take 4-6 weeks to build properly. A team of 5 doesn't have 4-6 weeks to spare on this. The "good enough" version: turn the senior engineer's manual steps into a single shell script checked into the repo, runnable by anyone, taking 2 days to build — it doesn't have a nice UI, doesn't self-heal, and someone still has to run it manually, but it eliminates the "only one person knows how" bottleneck and cuts the time from 90 minutes to 10, for a fraction of the effort of the general solution.

### Making the "we're tolerating this" decision explicit and revisited
For the low-value/expensive-fix and even some high-value/expensive-fix toil that a small team genuinely can't afford to fix right now, the discipline this lesson emphasizes is naming the deferral out loud and revisiting it on a schedule (e.g., quarterly) rather than letting it become invisible, permanent background load. A shared "toil we're knowingly tolerating" list, reviewed each quarter alongside the pager-load trend from `seeking-sre/04`, keeps these decisions from silently calcifying into "this is just how it is here" — and gives the team a concrete trigger to revisit once headcount grows or priorities shift.

### Worked example: a 5-person platform team's toil quarter
The team logs roughly 35 hours of collective toil in a representative week: 12 hours on manual deploys requiring a human to babysit each step, 8 hours on access-request approvals, 6 hours on the credential rotation mentioned above, and 9 hours scattered across smaller one-off tasks. Given roughly 200 person-hours of total capacity that week, this is a meaningful chunk (~17%) but not catastrophic. Triage: the 12-hour deploy toil is high-cost but the fix is genuinely expensive (a proper CI/CD pipeline rebuild) — the team commits one engineer to a scoped-down, 2-week "good enough" version (automate the 3 riskiest manual steps, leave the rest manual) rather than the full rebuild. The 6-hour credential rotation gets a 2-day script fix immediately. The 8-hour access-request toil is deprioritized explicitly and added to the tolerated-toil list, to be revisited once the deploy automation frees up capacity next quarter.

## Pros
- Makes toil-reduction tractable for teams that genuinely cannot afford Google-scale automation investment, by focusing effort where it pays back fastest.
- Prevents both extremes: ignoring toil entirely (letting it silently consume growing chunks of capacity) and over-investing in perfect automation the team can't afford.
- The explicit "tolerating this" list keeps deferred toil visible and revisited instead of quietly becoming permanent, invisible overhead.

## Cons
- "Good enough" partial fixes accumulate technical debt of their own (the ugly shell script nobody documents well) that needs eventual cleanup once the team can afford it.
- Requires real discipline to keep toil tracking going — it's easy for a busy team to let the weekly tally lapse, at which point the visibility benefit disappears.
- Triage decisions under real time pressure can be swayed by whoever's most annoyed that week rather than the actual data, undermining the honesty this approach depends on.

## Alternatives
- **Full Google-style dedicated automation investment** — appropriate once team size and toil volume genuinely justify it (typically once toil-hours saved would clearly outweigh a dedicated engineer's fully-loaded cost); premature at 5-person scale but the natural next step as the team grows.
- **Ignore toil tracking and rely on informal complaint volume ("whoever's most annoyed brings it up")** — lower overhead than formal tracking, but systematically under-weights toil that's spread thin across many people (no one person is annoyed enough to escalate) even when its total cost is high.
- **Outsource the toil-generating task entirely (a vendor or managed service replacing the manual process)** — sometimes cheaper than any in-house fix, especially for generic operational tasks (secrets management, access provisioning) where mature SaaS tooling already exists; worth checking before building anything in-house.

## When to use it
Apply this triage framework as soon as a small team has any recurring manual operational work and limited capacity to fix it comprehensively — which describes nearly every team under ~10 engineers. Start with visibility (a simple weekly tally) before any fix, since it's the cheapest step and it directs the rest of the effort.

## When NOT to use it
Don't apply "good enough" partial fixes to toil with real safety or compliance stakes (see `seeking-sre/10`) where a shortcut fix risks a serious incident or regulatory violation — those deserve the more rigorous treatment even at small-team cost. And don't let the tolerated-toil list become a permanent parking lot that's never actually revisited; if it's not reviewed on a real cadence, it isn't serving its purpose.

## Key takeaways / mental model
Toil management at small scale is triage, not elimination. Measure first (a rough weekly tally is enough to start), sort into frequency-times-fix-cost quadrants, prefer 80%-effective cheap fixes over comprehensive automation you can't afford, and keep a visible, revisited list of what you're knowingly tolerating so deferral stays a deliberate choice instead of an invisible drift.

## Self-check questions
1. A 5-person team discovers 35 hours of weekly toil spread across several tasks. Walk through how you'd triage it using the frequency/fix-cost framework, and justify which task gets fixed first.
2. Why does the lesson recommend a narrow, "good enough" partial fix over a fully general automation system for a small team, even when the general system is clearly the better long-term solution?
3. What's the risk of never revisiting a team's "toil we're knowingly tolerating" list, and what mechanism does this lesson suggest to prevent that?
4. Give an example of toil where a "good enough" 80%-effort fix would be the wrong call, and explain why it needs the more rigorous, comprehensive treatment instead.

## References
- Seeking SRE (David Blank-Edelman, ed.), essay on applying toil-reduction principles with a 5-person team instead of Google's automation budget.
- See also `sre/05` (toil identification and quantification mechanics) and `seeking-sre/04` (on-call sustainability, since reduced toil is one of the levers for sustainable pager load).
