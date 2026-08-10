---
id: seeking-sre/11
subject: seeking-sre
title: Measuring SRE Program Impact and Organizational Health
slug: sre-program-impact
status: drafted
mastery:
seniority: principal
source: Seeking SRE (David Blank-Edelman, ed.), essay on proving SRE investment is working beyond raw uptime numbers
prerequisites: [seeking-sre/06, sre/04]
created: 2026-08-10
updated: 2026-08-10
---

# Measuring SRE Program Impact and Organizational Health

## TL;DR
Raw uptime percentage is a weak, often misleading measure of whether an SRE program is working — it can improve while the organization quietly burns out its engineers, and it can look flat while the program is preventing worse outcomes that never happened; a credible measurement approach combines outcome metrics (SLO attainment trend), process-health metrics (postmortem completion rate, pager load), and leading indicators (near-miss reporting rate) into a single narrative that survives scrutiny from skeptical leadership.

## The idea
An SRE program's sponsor (an engineering VP, a founder) will eventually be asked to justify its cost — headcount, tooling spend, roadmap capacity reserved (`seeking-sre/09`) — and "uptime went from 99.5% to 99.8%" sounds like a defensible answer but is a genuinely weak one on its own, for a specific reason: it's a lagging, noisy, and gameable single number. A team can hit a great uptime number by getting lucky (no major dependency outage that quarter), by narrowing what counts as "down" in a way that quietly excludes real user pain, or by burning out on-call engineers into unsustainable pager loads that will produce worse outcomes next year. None of that shows up in the headline uptime number, which is exactly why the book argues a credible SRE program needs a broader measurement portfolio, not a single metric, and needs to actively guard against optimizing the metric instead of the underlying goal (Goodhart's law, applied to reliability programs specifically).

The strategic-level question this lesson is really about: how would you, as a principal engineer or engineering leader, actually *know* whether the SRE program is a good investment — not just whether uptime moved, but whether it's producing durable, healthy reliability outcomes and organizational capability.

## How it works

### Three categories of metric, and why you need all three
**1. Outcome metrics** — the closest thing to "did reliability actually improve": SLO attainment rate across services (not raw uptime, but percentage of time SLOs were actually met, which accounts for services having different appropriate targets), trended over multiple quarters rather than a single snapshot, and customer-facing incident count/severity trended over time. These answer "is the user experiencing fewer/smaller reliability problems."

**2. Process-health metrics** — these catch the "looks good but is unsustainable" failure mode outcome metrics miss: postmortem action-item completion rate (from `seeking-sre/09`'s reserved-capacity mechanism — if this is falling, reliability work is being deprioritized even if uptime hasn't dropped yet), pager-load trend per person (`seeking-sre/04` — rising pager load with flat uptime is a warning sign of unsustainable effort propping up the number), and time-to-detect/acknowledge/resolve trends (are incidents being caught and handled faster, independent of whether they happen at all).

**3. Leading indicators** — signals that predict future reliability before it shows up in outcomes: near-miss/close-call reporting rate (a *rising* near-miss report rate, counterintuitively, is often a good sign — it means psychological safety, `seeking-sre/05`, is high enough that people report problems before they become incidents, not that things are getting worse), and toil-hours trend (`seeking-sre/08` — is toil actually shrinking as a share of capacity, or growing invisibly).

### Worked example: the metric that looked great and wasn't
A company reports uptime improving from 99.6% to 99.9% over a year and presents this as clear proof the SRE program is working. A closer look at the other two metric categories tells a different story: postmortem action-item completion rate has fallen from 70% to 35% over the same period (reliability fixes are being deferred, not fewer problems are occurring), and pager-load per on-call engineer has risen 40% (the improved uptime is being propped up by increasingly unsustainable manual vigilance, not by durable systemic fixes). The honest read: this program is trading future reliability and engineer retention for a good-looking current-quarter number — exactly the failure mode a single-metric report would have hidden, and exactly the pattern that predicts a reversal (a burnout-driven departure, then a reliability regression) within the next year or two if untouched.

### Worked example: the metric that looked flat and was actually working
A different team's uptime number is essentially flat quarter over quarter (99.85% to 99.87%, not a meaningful change) and a skeptical stakeholder asks whether the reliability investment is paying off at all. The fuller picture: near-miss reports have tripled over the same period (people are catching and reporting problems before they become incidents, a leading indicator of a healthier system, not a worse one), toil-hours have dropped 25% as a share of team capacity (freeing that capacity for more of exactly this kind of proactive work), and the one severe incident that did occur was resolved in 40 minutes versus the roughly 3 hours a similar-severity incident took the prior year (a large improvement in response effectiveness invisible in the uptime number, which only counts total downtime, not response quality). The honest read here is the opposite: the program is working, and the flat uptime number is actually consistent with a system getting healthier, not evidence against it — the report needs to explain *why* flat uptime is good news in this specific case, or a skeptical stakeholder will draw the wrong conclusion from the headline number alone.

### Avoiding Goodhart's-law gaming
Any of these metrics, once it becomes the thing a team is evaluated on, creates pressure to game it rather than improve the underlying reality — narrowing SLO scope to make attainment look better, closing postmortem action items superficially to hit a completion-rate target, or discouraging near-miss reporting because a rising number looks bad to someone reading only the headline. The book's concrete defense: rotate which metric gets the most scrutiny each review cycle rather than fixating on one, and periodically have someone outside the team (a different SRE lead, an external auditor for regulated contexts per `seeking-sre/10`) spot-check a sample of the underlying data (did this postmortem action item actually get done, or just get marked done) rather than trusting the aggregate number at face value.

### Communicating a multi-metric story to leadership
This connects directly to `seeking-sre/06`'s translation problem: a three-category metrics dashboard is more credible but also more complex than a single uptime number, so the report to leadership needs a short, honest narrative wrapped around the numbers — "uptime is flat, and here's specifically why that's good news this quarter" — rather than assuming the raw numbers speak for themselves to a non-technical audience.

## Pros
- Catches failure modes (unsustainable effort propping up a good-looking number, deferred fixes accumulating invisibly) that a single uptime metric hides entirely.
- Gives principal-level leaders a genuine basis for judging whether an SRE program is a good investment, not just a plausible-sounding one.
- The leading-indicator category (near-miss reporting, toil trend) provides earlier warning of problems than outcome metrics alone, which only show up after the fact.

## Cons
- A multi-metric portfolio is genuinely harder to build, maintain, and explain than a single number, and requires real measurement discipline (consistent postmortem tracking, honest toil logging) to stay trustworthy.
- Any individual metric in the portfolio remains gameable under pressure; the multi-metric approach reduces but doesn't eliminate Goodhart's-law risk.
- Communicating a nuanced, multi-metric story to a skeptical or time-pressed stakeholder is harder than a single reassuring number, and requires the communication skill from `seeking-sre/06` to land well.

## Alternatives
- **Single headline uptime/SLA number as the primary success metric** — simpler to report and widely understood by non-technical stakeholders, but exactly the approach this lesson argues is insufficient on its own due to gameability and blindness to unsustainable effort.
- **Purely qualitative program review (leadership interviews, engineer sentiment surveys) instead of metrics** — captures nuance a dashboard misses (genuine burnout signals, morale) but lacks the objective, trended evidence needed to defend program investment against a skeptical stakeholder asking for numbers.
- **External benchmarking against industry reliability standards** — comparing your metrics against industry peers or standards bodies; useful context, especially in regulated industries (`seeking-sre/10`), but doesn't replace internal trend tracking since peer benchmarks rarely account for your specific system's risk profile.

## When to use it
Build a multi-category metrics portfolio as soon as an SRE program is being asked to justify its investment, or roughly annually as a discipline regardless of whether anyone's asking — waiting until a skeptical stakeholder demands proof is a worse position to build the story from than having it ready.

## When NOT to use it
Don't build an elaborate three-category dashboard for a very early-stage program (Stage 1-2 per `seeking-sre/03`) that doesn't yet have enough incident and postmortem history to produce meaningful trends — a handful of data points trended over a few months is noise, not signal, and premature dashboards can mislead as easily as a single bad metric.

## Key takeaways / mental model
Never trust a single reliability number, especially uptime, on its own. Triangulate across outcome (did users experience fewer/smaller problems), process health (is the org sustaining this without burning people out or deferring fixes), and leading indicators (are people catching problems early, is toil shrinking) — and be ready to explain, in plain language, why a flat or even worsening headline number might actually represent a healthier program, or why an improving one might not.

## Self-check questions
1. A company's uptime improved significantly this year, but postmortem completion rate fell and pager load rose. What's the honest read on this program, and what would you tell a skeptical CFO who only sees the uptime number?
2. Why does the lesson argue that a *rising* near-miss reporting rate is often a good sign rather than a bad one? What would make you suspicious that a rising near-miss rate is actually bad news instead?
3. Describe a concrete way a team could game the "postmortem action-item completion rate" metric without actually improving reliability, and propose a countermeasure.
4. A team's uptime is flat quarter over quarter. Walk through the other metrics you'd check before concluding whether the program is working, and explain what pattern in those metrics would change your conclusion in each direction.

## References
- Seeking SRE (David Blank-Edelman, ed.), essay on proving SRE investment is working beyond raw uptime numbers.
- See also `sre/04` (error budgets, the mechanism outcome metrics like SLO attainment build on) and `seeking-sre/06` (stakeholder communication, needed to land a nuanced multi-metric story with leadership).
