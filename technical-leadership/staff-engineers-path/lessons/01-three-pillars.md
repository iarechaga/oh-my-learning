---
id: staff-engineers-path/01
subject: staff-engineers-path
title: The three pillars of staff engineering
slug: three-pillars
status: drafted
mastery:
seniority: staff
source: The Staff Engineer's Path (Tanya Reilly), Chapter 1 - "What would you say you do here?"
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# The three pillars of staff engineering

## TL;DR
Staff-plus engineering is not "senior engineer with a bigger title" — it is a distinct job built on three pillars: **big-picture thinking** (seeing beyond your own team's scope), **execution** (getting big, ambiguous things done, mostly through other people), and **leveling up others** (making the engineers and systems around you better even when you're not in the room). Every staff-level behavior in this subject is an instance of one (or more) of these three.

## The idea
Individual-contributor career ladders usually describe growth as "do more of what a senior engineer does, but better and on harder problems." That model breaks down at staff level, because the actual job changes shape. A senior engineer's success is measured mostly by what they personally build. A staff engineer's success is measured by outcomes that are bigger than what one person can build — which means the job has to include thinking about scope beyond your own code, and getting work done through other people's hands, not just your own.

Tanya Reilly's framing solves the "what am I even supposed to be doing?" confusion that hits many new staff engineers: the job is genuinely different, not just "more," and it decomposes cleanly into three areas that don't require you to become a manager to practice.

1. **Big-picture thinking** — operating with an organization-wide (or company-wide) view of the technical landscape: knowing what other teams are building, where the org is headed, which problems are actually worth solving, and how a local decision plays out three systems away.
2. **Execution** — turning big, vague, cross-team problems into real, shipped outcomes. This is the pillar most people already associate with "senior engineer," but at staff scope it requires driving work you cannot do alone: writing the plan, building consensus, unblocking other people, and staying accountable for an outcome you don't fully control.
3. **Leveling up other engineers and the organization** — mentoring, sponsoring, setting technical standards, and building systems/processes/docs that make *other people* more effective, so your impact persists and compounds even in rooms you're not in.

## How it works

### Why "just write more code" stops scaling
A senior engineer who writes 2x as much code as a mid-level engineer produces roughly 2x the impact. A staff engineer who tried to scale the same way — writing code alone, faster — would hit a hard ceiling: one person's output, however excellent, cannot move a 200-person organization's technical trajectory. The three pillars exist because staff impact has to route *through* other people and *through* the org's shared context, not just through your own keyboard.

**Worked example.** Imagine a company where the checkout service and the inventory service are both creaking under load, owned by two different teams who don't talk to each other much. A strong senior engineer on the checkout team might rewrite checkout's hot path and ship a 40% latency win — real, valuable, scoped to their team.

A staff engineer looking at the same situation applies all three pillars:
- **Big picture**: notices that both teams are independently building near-identical caching layers, and that the *actual* bottleneck is a shared database's connection pool, not either service's code.
- **Execution**: writes a short technical direction doc proposing a shared caching layer, gets both team leads to agree on an owner and a rough timeline, and personally builds the riskiest piece (the failover logic) to unblock both teams.
- **Leveling up others**: documents the caching pattern as a reusable library with a design-review checklist, so the next three teams that hit this problem don't need a staff engineer to reinvent the fix.

The senior engineer's fix is faster to deliver and locally correct. The staff engineer's fix costs more calendar time up front but changes the trajectory of the *organization*, not just one service — that's the qualitative difference the three pillars are pointing at.

### How the pillars interact
The pillars are not three independent checkboxes; each one enables the others.
- Big-picture thinking tells you *which* problems are worth executing on (pillar 2) — without it, you might expertly execute the wrong project.
- Execution proves your judgment is trustworthy, which is what earns you the standing to set direction and mentor credibly (pillar 3).
- Leveling up others multiplies your own execution capacity — a well-mentored team, a good onboarding doc, or a shared quality bar means fewer things need your direct hands-on involvement, freeing you to spend big-picture time on the next problem.

### A rough self-diagnostic
Reilly suggests staff engineers periodically ask which pillar they've been neglecting. A common failure pattern: an engineer promoted to staff for strong execution keeps doing *only* execution — heads-down building — because it's the most comfortable, familiar mode, and quietly lets big-picture awareness and mentoring atrophy. Six months later they're technically excellent but organizationally invisible, and their manager can't articulate their impact beyond "ships good code," which is a senior-level story, not a staff-level one.

## Pros
- Gives a concrete, three-part vocabulary for a notoriously fuzzy job title, useful for self-assessment, promotion cases, and explaining your own role to skeptical stakeholders.
- Each pillar is independently practicable without formal authority — you don't need to be a manager to do big-picture thinking, drive execution, or mentor.
- The framework naturally explains *why* staff engineers spend less time coding as scope grows: it's not "staff engineers stop being technical," it's that the job's other two pillars compete for the same hours.

## Cons
- The three pillars are descriptive, not prescriptive — they don't tell you *how much* of each to do, which varies enormously by company, team maturity, and individual strength (a "big-picture-heavy" staff engineer and an "execution-heavy" staff engineer can both be doing the job well).
- Easy to over-apply as a checklist ("did I hit all three this quarter?") rather than as a lens for judgment; the framework works best as a diagnostic question, not a scorecard.
- Some orgs' staff-plus expectations genuinely lean on only one or two pillars (e.g., a "technical fellow" track may be almost entirely big-picture + a little execution, with mentoring optional) — the three-pillar split is a generalization, not a universal formula.

## Alternatives
- **The staff engineer archetypes (Tech Lead, Architect, Solver, Right Hand)** — a complementary framework, also from Reilly's book, describing common *shapes* a staff role takes; the three pillars describe *what* the job is made of, the archetypes describe *how* a given role combines them.
- **Career ladder rubrics (e.g., "scope of impact: team -> org -> company")** — many companies express staff-plus levels purely in terms of blast radius, without naming the three pillars explicitly; useful for calibration but doesn't explain *how* to achieve that scope.
- **"10x engineer" narratives** — a competing, code-output-centric framing that treats staff-level impact as scaled-up individual output; the three-pillar model is explicitly a rebuttal to this, arguing that leverage through others is what actually scales past a certain point.

## When to use it
Use the three pillars as a lens whenever you're deciding what to work on next as a senior-plus engineer, when writing a promotion narrative, when a new staff engineer is unsure what the job even is, or when diagnosing why a technically strong engineer isn't landing as "staff-level" in calibration.

## When NOT to use it
Don't force all three pillars into every single project — a two-week execution-heavy sprint doesn't need a mentoring component bolted on artificially. And don't use the framework to justify avoiding hands-on technical work entirely; losing technical credibility (see `staff-engineers-path/04`) undermines all three pillars, since big-picture judgment and trustworthy execution both depend on staying technically sharp.

## Key takeaways / mental model
Staff engineering = big-picture thinking x execution x leveling up others. It's a multiplication, not a sum: being excellent at execution while ignoring the other two still caps your impact at "very good senior engineer." When your impact feels capped, ask which pillar you've been neglecting.

## Self-check questions
1. Pick a project you've worked on recently. Which of the three pillars did it exercise? Which pillar was completely absent, and would the project's impact have been bigger if it had been present?
2. Explain why "just write more/better code faster" stops being a viable staff-level growth strategy past a certain scope, using your own words rather than the lesson's checkout/inventory example.
3. Describe a scenario where an engineer is technically excellent at execution but would still be assessed as "not yet staff" in a calibration meeting. What's missing?
4. How do the three pillars reinforce each other? Give an example of big-picture thinking making execution better, and execution making mentoring more credible.

## References
- The Staff Engineer's Path (Tanya Reilly), Chapter 1: "What would you say you do here?"
