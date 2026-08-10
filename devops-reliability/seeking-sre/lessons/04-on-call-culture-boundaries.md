---
id: seeking-sre/04
subject: seeking-sre
title: Building Sustainable On-Call Culture and Boundaries
slug: on-call-culture-boundaries
status: drafted
mastery:
seniority: senior
source: Seeking SRE (David Blank-Edelman, ed.), essay on preventing on-call burnout in teams without Google-scale headcount
prerequisites: [seeking-sre/03, sre/08]
created: 2026-08-10
updated: 2026-08-10
---

# Building Sustainable On-Call Culture and Boundaries

## TL;DR
Sustainable on-call is a function of pager load per person, not just "having a rotation" — a rotation of 4 people getting paged 20 times a week is worse than a rotation of 8 people getting paged 5 times a week, and small teams without Google's headcount need explicit, deliberate boundaries (load caps, compensation, escalation rules, opt-out paths) to keep on-call from quietly becoming a retention risk.

## The idea
`seeking-sre/03` describes the *structural* progression of incident response (from hero-led to rotation to measured process). This lesson zooms into the human dimension of Stage 3-and-beyond: once you have a rotation, is it actually sustainable for the people in it? Google's SRE book (`sre/08`) prescribes concrete pager-load targets (no more than roughly 2 events per on-call shift, enough headcount that no one is on-call more than ~25% of their time) built on the assumption that you can hire enough SREs to hit those numbers. Most companies applying SRE ideas don't have that luxury — a 6-person platform team supporting a 24/7 service can't easily hit "on-call no more than 1 week in 6" without either hiring more people (often not immediately possible) or actively reducing pager load through other means.

The book's contribution is naming on-call sustainability as something that has to be engineered deliberately at small scale, not something that falls out naturally once you "have SRE." Left unmanaged, on-call becomes an invisible tax that disproportionately drives out your most reliability-conscious engineers, because they're the ones most likely to actually notice and be worn down by an unsustainable rotation.

## How it works

### The pager-load math at small scale
Take a 6-person team running a weekly primary/secondary rotation. If the service pages 15 times a week (a genuinely modest number for a growing product), the primary on-call absorbs roughly 15 interruptions across a single week once every 6 weeks — a heavy week, but survivable if it's rare. The real risk is when growth outpaces headcount: the same team six months later, still 6 people, now supporting 3x the traffic and 35 pages a week. Nothing about the rotation *structure* changed, but the lived experience did — and if leadership is only tracking "do we have a rotation," this degradation is invisible until someone quits.

Two levers, usable independently of hiring, that this lesson highlights:
- **Reduce pages, not just tolerate them** — every recurring page is a toil-reduction candidate (see `seeking-sre/08`); a team that halves its noisy/low-value pages through better alerting (`sre/07`-style signal quality) effectively doubles its sustainable headcount without hiring anyone.
- **Widen the rotation deliberately, even with reluctant participants** — a 6-person team where only 3 people are "trusted" to be on-call (the rest too junior, or never onboarded) is really a 3-person rotation wearing a 6-person label; investing in onboarding and shadowing shifts to genuinely widen the pool is often higher-leverage than hiring.

### Concrete boundaries worth writing down
- **A hard load cap with an explicit escalation plan** when it's breached — e.g., "if primary on-call is paged more than 6 times in one shift, escalate to secondary and the shift is logged as an incident against the alerting system itself, not just the underlying service."
- **Compensation or time-off-in-lieu for on-call**, even informally at a small company — treating on-call as free, unrecognized labor is one of the fastest routes to resentment; a fixed on-call stipend or a guaranteed comp-day after a heavy week signals the company treats the burden as real.
- **A no-blame opt-out path for genuine life circumstances** (new parent, health issue) without the person having to justify it repeatedly, and a plan for how the rotation absorbs that gap.
- **A hard rule against "the expert always gets pulled in"** — if Slack culture means the on-call engineer pages the one person who "actually knows this service" every time, that person is functionally always on-call regardless of the rotation schedule; the fix is deliberate documentation and shadowing (linking back to `seeking-sre/03`'s runbook-building) so expertise isn't a single point of failure.

### Worked example: catching silent degradation
A team's weekly retro starts including one number: pages-per-shift, trended over the last 8 weeks. When it creeps from an average of 4 to 11 over two months (because a new feature launched without adequate load testing), the team has an early, objective signal to act on — either fast-follow work to fix the noisy alerts, or an explicit conversation with leadership about needing another rotation member — well before anyone burns out silently. Without this trend line, the same degradation is usually only "discovered" when someone resigns and cites on-call exhaustion in their exit interview.

### When headcount genuinely can't grow
Not every team can hire its way to Google's target ratios. In that case, the honest move — one this lesson explicitly endorses — is to **narrow the on-call scope** rather than pretend the current headcount can sustainably cover it: reduce which severities page a human at all (auto-remediate or defer non-urgent classes), reduce the hours covered (business-hours-only paging for genuinely non-critical services, with an honest SLO reflecting that), or reduce the service surface any one person is on-call for (split a monolithic rotation into narrower, better-understood slices). Pretending a 4-person rotation can safely cover a 24/7, revenue-critical, unbounded-scope on-call is a choice that trades a visible near-term staffing gap for an invisible long-term attrition problem.

## Pros
- Makes on-call sustainability measurable (pages per shift, trended) rather than a vague cultural vibe, catching degradation early.
- Offers concrete levers (toil reduction, rotation widening, scope narrowing) that don't require headcount growth, which matters for teams that can't simply hire their way out.
- Frames on-call boundaries as a retention issue, giving leadership a business reason (attrition cost) to invest, not just an engineering-comfort argument.

## Cons
- Narrowing on-call scope or auto-remediating pages has real risk if done carelessly — it can hide genuine problems rather than reduce noise, if the underlying alert was actually meaningful.
- Compensation and load-cap policies cost real money and process overhead that small, cash-constrained companies may resist funding.
- Trend-line monitoring of pager load only works if pages are being logged consistently and honestly; teams under pressure to "look fine" can under-report.

## Alternatives
- **Follow-the-sun coverage across time zones** — eliminates night-shift pager load entirely by handing off to a team in a different time zone; effective but only available to companies with genuinely distributed engineering presence, which most small/mid companies lack.
- **Fully automated remediation for the noisiest page classes** — removes humans from the loop for well-understood failure modes (auto-restart, auto-scale) instead of managing human tolerance for those pages; a strong complement to this lesson's boundaries but requires upfront engineering investment to build safely.
- **Managed/outsourced after-hours on-call** — shifts the load-bearing question outside the team entirely; addresses burnout directly but at the cost of losing in-house context during incidents, and requires very good runbooks (`seeking-sre/03`) to work at all.

## When to use it
Set explicit on-call boundaries (load caps, compensation, opt-out paths, trended pager-load metrics) as soon as a rotation exists at all — don't wait for a resignation to reveal it was unsustainable. Revisit the boundaries whenever traffic or service count grows materially.

## When NOT to use it
Don't over-formalize on-call policy for a genuinely tiny, low-page-volume service where a single informal "whoever's around" arrangement is truly low-burden; heavy process here is its own kind of toil. And don't use "we can't afford more headcount" as a reason to skip narrowing scope — an honest, narrower on-call commitment beats an unsustainable, unbounded one every time.

## Key takeaways / mental model
Track pages-per-shift like you'd track any other health metric, not just "is there a rotation." When headcount can't grow to meet Google's target ratios, don't silently absorb the gap — deliberately reduce pages (toil work), widen the rotation (invest in onboarding), or narrow the scope (fewer things page, or page fewer hours) so the commitment you're making matches what the team can actually sustain.

## Self-check questions
1. A 6-person rotation's pages-per-shift has crept from 4 to 11 over two months. Name two levers this lesson offers that don't require hiring, and explain which you'd try first and why.
2. Why does the lesson argue that "the expert always gets pulled in" effectively defeats a rotation, even if the official schedule looks healthy?
3. A leadership team says "we can't afford to hire another SRE right now, so just keep the current rotation as-is." What's the honest alternative this lesson recommends instead of silently absorbing the gap?
4. Give an example of when narrowing on-call scope (fewer things paging) would be the wrong move because it risks hiding a genuine problem rather than reducing noise.

## References
- Seeking SRE (David Blank-Edelman, ed.), essay on preventing on-call burnout in teams without Google-scale headcount.
- See also `sre/08` (on-call engineering mechanics and target ratios) and `seeking-sre/08` (org-scale toil management) for the pager-reduction lever discussed above.
