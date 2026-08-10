---
id: seeking-sre/03
subject: seeking-sre
title: Evolving Incident Response Maturity Over Time
slug: incident-response-maturity
status: drafted
mastery:
seniority: senior
source: Seeking SRE (David Blank-Edelman, ed.), essay on scaling incident response from founder-led firefighting to structured process
prerequisites: [seeking-sre/01, sre/08]
created: 2026-08-10
updated: 2026-08-10
---

# Evolving Incident Response Maturity Over Time

## TL;DR
Incident response maturity is a staged progression — informal/founder-led, then ad hoc on-call, then structured rotations with runbooks, then measured and continuously improving — and the mistake most growing companies make is either staying in an earlier stage too long (burning out the few people who "just know how to fix it") or importing a later stage's heavyweight process before the org has the incident volume or headcount to sustain it.

## The idea
Every company starts incident response the same way: a handful of people (often literally the founders) get paged, know the whole system, and fix things themselves. This works fine at low incident volume and small system surface area. It fails predictably as the company grows, because the number of things that can break grows faster than the number of people who understand all of them — the founders become a single point of failure, get paged at 3am indefinitely, and either burn out or leave, taking undocumented tribal knowledge with them.

The book frames incident response maturity as a **staged capability**, not a switch you flip. Each stage solves the previous stage's failure mode but introduces a new cost (mostly process overhead), so the right stage is the one that matches your current incident volume and team size — not the most sophisticated one you've read about.

## How it works

### The four stages
**Stage 1 - founder/hero-led.** Whoever built the system fixes it, whenever it breaks, informally. No rotation, no runbooks — the fix lives in one person's head.
- *Works when*: under ~5 engineers, low incident frequency (a handful of pages a month), system small enough for one or two people to hold a full mental model.
- *Breaking point*: incident frequency or system complexity outpaces what 1-2 people can absorb; the hero starts missing pages, and there's no one else who can respond.

**Stage 2 - ad hoc on-call.** A rotation exists ("whoever's on-call this week"), but there are no runbooks, no defined severity levels, and response quality varies enormously by who's on call — a page that a senior engineer resolves in 10 minutes takes a newer engineer two hours because nothing is written down.
- *Works when*: 5-20 engineers, growing incident volume, but the team hasn't yet accumulated enough repeat-incident patterns to justify runbooks for everything.
- *Breaking point*: new hires dread being on-call because they have no reference material; time-to-resolution has high variance; institutional knowledge still concentrated in the same 2-3 people who happen to remember every past incident.

**Stage 3 - structured rotation with runbooks and severity levels.** A formal rotation (with defined schedule, escalation policy, and secondary on-call), a growing library of runbooks for known failure modes, and a shared severity taxonomy (P1/P2/P3) that determines response urgency and who gets paged.
- *Works when*: 20-100+ engineers, incident volume high enough that patterns repeat and runbooks pay for themselves, enough headcount to sustain a real rotation without any one person carrying too much pager load (see `seeking-sre/04` on sustainable on-call).
- *Breaking point*: runbooks go stale as the system changes, severity definitions get gamed (everything becomes "P1" to get attention) without governance, and postmortems (`sre/10`) either don't happen or don't produce real follow-through.

**Stage 4 - measured, continuously improving response.** Incident response itself is instrumented: mean time to detect/acknowledge/resolve tracked over time, postmortem action items tracked to completion, and the response process is periodically reviewed and revised based on that data, not just intuition.
- *Works when*: mature engineering orgs with dedicated reliability investment (often where a platform/central SRE function exists, per `seeking-sre/01`) and where the cost of further incident-response improvement is justified by genuine business risk (regulated industry, high-revenue-per-minute-of-downtime).
- *Breaking point*: over-investment here before Stage 3 is solid is wasted effort — dashboards measuring a process that isn't yet consistent (no reliable runbooks, ad hoc severity) produce noisy, misleading metrics.

### Worked example: a 15-person company stuck at Stage 1
A 15-engineer SaaS company still runs Stage 1: the two co-founders get paged for everything because "they know the system best," averaging 8 pages a week between them, most resolved from memory with no notes left behind. A new hire who could plausibly take some pager load instead spends every incident watching a founder fix it live over screen share, learning nothing transferable. The fix isn't jumping to Stage 3's full rotation-and-runbook machinery overnight (the team is too small to sustain a formal rotation with adequate coverage) — it's a deliberate Stage 2 move: add 2-3 more engineers to a lightweight rotation, and require that the *next* five incidents each produce a short "what happened, what we did" note, seeding the runbook library that Stage 3 will eventually need. Jumping straight to a heavyweight PagerDuty-plus-severity-taxonomy setup for a 15-person team without that groundwork usually just adds process overhead without actually distributing the tribal knowledge.

### Worked example: over-engineering at Stage 4 too early
A 40-engineer company, inspired by a conference talk about Google's incident response metrics, builds an elaborate MTTA/MTTR dashboard with SLA targets by severity before it has consistent severity definitions or a runbook library. The dashboard shows "MTTR is 4 hours" as a single aggregate number that's meaningless because it blends a P1 database outage with a P3 UI glitch that sat unactioned over a long weekend. The lesson: Stage 4 tooling amplifies whatever process exists underneath it — garbage in, garbage out. The fix is finishing Stage 3 (a real, governed severity taxonomy and runbook coverage for the top 10 recurring incident types) before the metrics layer can say anything useful.

### Diagnosing your current stage
A quick self-assessment: if incident response quality depends heavily on *who* is on-call, you're at Stage 1 or 2. If quality is consistent across responders but you're not tracking response-process metrics over time, you're at Stage 3. If you're already tracking metrics but they aren't driving actual process changes, you have Stage 4 tooling without Stage 4 practice — worth fixing before adding more instrumentation.

## Pros
- Gives growing companies a concrete, staged roadmap instead of either staying stuck in hero-mode too long or cargo-culting a mature org's tooling prematurely.
- Names the specific failure mode of each stage, making it easier to recognize "we've outgrown this" versus "we're not ready for the next stage yet."
- Ties maturity progression to headcount and incident volume rather than treating it as a fixed timeline, which keeps the advice honest across very different company trajectories.

## Cons
- Stages are a simplification — real orgs often have Stage 3 maturity for one critical service and Stage 1 maturity for a newer one, and the model doesn't fully capture that unevenness.
- Progressing a stage too early wastes engineering effort building process the org isn't ready to sustain (runbooks no one maintains, severity taxonomies no one respects).
- Requires someone with the authority and time to actually drive the transition (write the first runbooks, define severities) — without a sponsor, orgs tend to drift rather than deliberately progress.

## Alternatives
- **Buy a mature incident-management platform and impose its default process wholesale** — can accelerate reaching Stage 3's structure but doesn't substitute for the org actually having repeat-incident patterns and headcount to sustain the process; tooling alone doesn't create maturity.
- **Outsource incident response for after-hours coverage (a managed NOC)** — addresses the Stage 1 "founders get paged forever" pain directly without progressing internal maturity at all; useful as a stopgap but doesn't build the internal tribal-knowledge transfer this lesson is about.
- **Chaos engineering / game days to accelerate learning** — instead of waiting for real incidents to build runbook content, deliberately manufacture practice incidents; effective at speeding Stage 2->3 transition but requires some Stage 2 discipline (a rotation, willingness to write things down) to already exist.

## When to use it
Use this staged model whenever you're assessing "is our incident response good enough," onboarding a new reliability lead, or deciding what to invest in next. Name your current stage explicitly and pick the smallest next step (not the most sophisticated end-state) that addresses your specific failure mode.

## When NOT to use it
Don't use stage-jumping as a status symbol — building Stage 4 dashboards to look mature in front of investors or leadership, without Stage 3's underlying discipline, produces misleading data and wasted effort. Don't force a tiny, low-incident-volume team into full rotation-and-runbook machinery it doesn't yet need; lightweight founder-led response is a legitimate, appropriate stage for genuinely small, low-risk systems.

## Key takeaways / mental model
Ask two questions to place yourself on the ladder: does response quality depend on who's on-call (stuck at Stage 1/2), and are you tracking response metrics that actually change your process (Stage 4) versus not tracking at all (Stage 3 or below)? Move one stage at a time, and build the underlying discipline (rotation, runbooks, severity governance) before adding the metrics layer on top of it.

## Self-check questions
1. A 10-person startup's two most senior engineers are each averaging 3 pages a night. Which stage are they stuck in, and what's the smallest concrete next step — not the most sophisticated one — you'd recommend?
2. Explain why building an MTTR dashboard before a company has a governed severity taxonomy tends to produce misleading rather than useful data.
3. A mid-size company has excellent runbooks and a stable rotation for its core payments service, but a newer analytics service still runs on founder-led firefighting. Is this a contradiction of the staged model, or does it fit? Explain.
4. What's the difference between "Stage 4 tooling" and "Stage 4 practice," and why does the lesson argue tooling without practice is worse than no tooling at all?

## References
- Seeking SRE (David Blank-Edelman, ed.), essay on scaling incident response from founder-led firefighting to structured process.
- See also `sre/08` (on-call engineering mechanics) and `sre/10` (postmortems) for the Stage 3/4 machinery this lesson references, and `seeking-sre/04` for the human-sustainability side of the rotation described in Stage 3.
