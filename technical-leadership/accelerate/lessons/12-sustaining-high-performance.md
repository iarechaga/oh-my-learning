---
id: accelerate/12
subject: accelerate
title: Sustaining high performance and preventing local optimization
slug: sustaining-high-performance
status: drafted
mastery:
seniority: staff
source: Accelerate (Forsgren, Humble, Kim), Chapter 8 "Making Work Sustainable" and Chapter 10 "Conclusion"
prerequisites: [accelerate/09, accelerate/10, accelerate/11]
created: 2026-08-10
updated: 2026-08-10
---

# Sustaining high performance and preventing local optimization

## TL;DR
Reaching elite delivery performance is a temporary state unless the organization actively guards against two forces that erode it over time: burnout from treating high performance as a sprint rather than a sustainable pace, and local optimization, where individual teams or functions improve their own metrics in ways that harm the system as a whole. Sustaining performance requires system-level thinking and continuous reinvestment, not a one-time transformation program (`accelerate/11`) followed by coasting.

## The idea
It's tempting to treat reaching "elite performer" status on the four key metrics (`accelerate/03`, `accelerate/04`) as a finish line — a state achieved once, then maintained by default. The book's longitudinal data (tracking organizations across multiple years, not just a single snapshot) argues against this: performance regresses without continued investment, for two specific, well-evidenced reasons.

First, **unsustainable pace**: an organization can hit strong short-term delivery numbers by running the team hot — long hours, constant context-switching, deferred technical debt — but this borrows against future capacity. Burnout (discussed as a productivity signal in `accelerate/10`) degrades judgment, increases mistakes (raising change failure rate), and drives attrition, which itself degrades delivery performance as institutional knowledge walks out the door and replacements ramp up.

Second, **local optimization**: any sufficiently large organization has multiple teams, each of which can improve *its own* local metrics in ways that don't improve — and sometimes actively harm — the system as a whole. A platform team that reduces its own on-call load by making its API harder to misuse but much harder to integrate with pushes cost onto every consuming team; a security team that reduces its own audit findings by adding a slow, heavyweight review gate improves its local metric while degrading the org-wide lead time this whole subject is built around. Sustaining high *organizational* performance requires actively watching for and correcting this, because no single team's local metrics will reveal it — it only shows up at the system level.

## How it works

### Sustainable pace as an engineering input, not just a wellness policy
The book frames sustainable pace (a concept with roots in Agile/XP practice) as directly load-bearing for the four key metrics, not a separate HR concern layered on top. Chapter 8's data connects burnout to weaker technical and cultural capabilities (deployment pain, low WIP-limit discipline, pathological/bureaucratic rather than generative culture, `accelerate/09`) and to worse delivery outcomes over time — the causal arrows run in both directions: bad capabilities cause burnout, and burnout further degrades the judgment and attention that good delivery practice requires (careful code review, thoughtful incident response, disciplined testing), creating a reinforcing spiral if unaddressed.

**Worked example — the reinforcing spiral:** A team, understaffed relative to its workload, starts skipping code review depth to keep up ("just approve it, we're behind"). Change failure rate creeps up. Handling the resulting incidents consumes even more of the team's time, leaving even less time for the careful work (tests, review, refactoring) that would have prevented the incidents. Morale drops, two engineers leave, remaining engineers absorb more load, the spiral tightens. What looked initially like a scheduling/staffing problem has become a full capability erosion, visible in the four key metrics trending the wrong direction — and it started from a seemingly small, locally reasonable decision ("skip review depth just this sprint") made under unsustainable pace.

### Local optimization: the classic systems-thinking failure mode
Drawing on systems thinking and Lean's whole-value-stream view (echoing `accelerate/09`'s Lean management practices), the book warns that optimizing any single stage of the delivery pipeline in isolation can worsen the end-to-end flow, even while that stage's own metrics improve. This is the same insight behind Goldratt's Theory of Constraints: a system's throughput is governed by its bottleneck, and improving a non-bottleneck stage doesn't help the whole system — but the book adds a sharper version: improving a non-bottleneck stage *at the expense of* the bottleneck or of a downstream team actively makes the whole system worse, not just neutral.

**Worked example — local optimization in practice:** A QA team, measured on "defects escaped to production per QA review," responds by making its review process more thorough and slower — its own metric improves. But this review is a gate every team's release must pass through, so end-to-end lead time (`accelerate/03`) across the whole organization gets worse, and because releases now batch up waiting for the slower QA gate, change failure rate (`accelerate/04`) can get worse too, via the same batch-size mechanism this subject keeps returning to. The QA team's dashboard looks like a success story; the organization's DORA metrics tell the opposite story. Fixing this requires measuring and rewarding the *system*-level outcome (end-to-end lead time, org-wide change failure rate), not each team's local proxy metric, echoing the productivity-measurement caution from `accelerate/10`.

### What sustaining performance concretely requires
1. **Keep measuring the four key metrics on an ongoing basis**, not just during a transformation push — treat them as a permanent operating dashboard, not a project-completion report.
2. **Watch for local-optimization signals**: a team whose own metrics improve while an adjacent team's pain (deployment pain, `accelerate/10`) increases is a red flag worth investigating, even if no single metric alone shows a problem.
3. **Treat sustainable pace as a leading indicator to protect**, not a slack variable to sacrifice under deadline pressure — the short-term gain from crunch is reliably smaller than the medium-term cost the book's data associates with the resulting burnout and attrition.
4. **Revisit the capability model (`accelerate/11`) continuously**: today's bottleneck, once resolved, is replaced by a new one; sustaining performance means the diagnose-invest-remeasure loop never actually stops, even after reaching elite status.

## Pros
- Prevents the common failure mode of treating a successful transformation (`accelerate/11`) as a completed project, setting the correct expectation that this is ongoing operating discipline, not a one-time initiative.
- Makes burnout and local optimization *visible and namable* problems with specific diagnostic patterns, rather than vague, hard-to-address organizational drift.
- Reframes cross-team conflicts (e.g., "QA is too slow" vs. "developers ship too many bugs") around a shared, system-level metric instead of an unproductive blame exchange between teams each optimizing their own local number.

## Cons
- Detecting local optimization requires system-level (cross-team) visibility that many organizations' reporting structures don't naturally provide — it takes deliberate effort to build the dashboards and forums where this becomes visible.
- Protecting sustainable pace under real business pressure (a genuine market deadline, a competitive threat) requires leadership discipline to resist short-term crunch even when the short-term case for it looks compelling in the moment — the cost of unsustainable pace is real but delayed, which makes it easy to discount.
- No formulaic answer for *how much* investment is enough to sustain performance indefinitely — unlike a one-time capability gap, this is an ongoing resource allocation question that competes with every other business priority, indefinitely.

## Alternatives
- **Theory of Constraints (Goldratt)** — the original systems-thinking framework this lesson's local-optimization argument draws from; more general-purpose (applicable to any production system, not just software), useful as deeper background on why optimizing a non-bottleneck doesn't help and can actively hurt.
- **Team Topologies (Skelton & Pais)** — a complementary, more recent framework specifically addressing how to structure teams and their interaction modes to avoid exactly this kind of cross-team local optimization and cognitive-load overload; a natural next read after this subject.
- **Periodic "reset" transformation pushes (repeat `accelerate/11` every few years)** — an alternative operating model where organizations accept performance will erode and periodically re-invest in a fresh push rather than sustaining continuously; the book's data favors continuous investment over this cycle, since the erosion-and-recovery pattern costs more in the aggregate (lost capability, burnout, attrition) than steady maintenance.

## When to use it
Apply this lesson's diagnostic lens (sustainable pace + local-optimization check) once an organization has made real capability gains (`accelerate/05` through `accelerate/11`) and needs to protect them — specifically, revisit it whenever a team's local metrics improve without a corresponding system-level improvement, or whenever leadership considers trading sustainable pace for a short-term deadline.

## When NOT to use it
Don't use "protect sustainable pace" as a blanket objection to every deadline or urgent push — genuinely time-boxed, occasional pushes for a real, well-communicated reason, followed by real recovery time, are different from chronic unsustainable pace; the book's concern is the *chronic* pattern and its long-run cost, not the existence of any short-term urgency ever. Similarly, don't chase every local-optimization instance to zero — some amount of local metric ownership is still useful for team-level accountability; the goal is catching cases where local optimization measurably harms the system, not eliminating local metrics altogether.

## Key takeaways / mental model
High performance is a dynamic equilibrium that requires continuous energy to maintain, not a state you arrive at and keep by default — like physical fitness, not like a certification. Two specific forces erode it if unwatched: burnout (spending down the team's sustainable capacity for a short-term metric win) and local optimization (a team improving its own numbers while degrading the system's). Sustaining performance means keeping the diagnose-invest-remeasure loop from `accelerate/11` running indefinitely, and always evaluating any local metric improvement against its system-level effect.

## Self-check questions
1. Walk through the reinforcing-spiral worked example and identify the point where a system-level metric (one of the four key metrics) would have flagged the problem before it became severe. What made it invisible to the team in the moment?
2. Explain the QA-team local-optimization worked example in your own words, and propose a different metric the QA team could be measured on that would better align its incentives with the system-level lead time goal.
3. A leadership team says "we hit elite performer status last year, we're done." Using this lesson's argument, explain what specifically is wrong with that statement and what evidence you'd look for to check whether performance is actually eroding.
4. Distinguish a legitimate occasional deadline push from the chronic unsustainable-pace pattern this lesson warns about. What two or three concrete signals would tell you which one you're looking at?

## References
- Accelerate: The Science of Lean Software and DevOps (Forsgren, Humble, Kim), Chapter 8: "Making Work Sustainable", Chapter 10: "Conclusion".
- Eliyahu M. Goldratt, The Goal — the origin of the Theory of Constraints referenced in the local-optimization discussion.
