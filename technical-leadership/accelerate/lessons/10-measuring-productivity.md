---
id: accelerate/10
subject: accelerate
title: Measuring productivity without vanity metrics
slug: measuring-productivity
status: drafted
mastery:
seniority: senior
source: Accelerate (Forsgren, Humble, Kim), Chapter 3 "Measuring and Changing Culture" (developer productivity section) and Chapter 8 "Making Work Sustainable"
prerequisites: [accelerate/02, accelerate/03, accelerate/04]
created: 2026-08-10
updated: 2026-08-10
---

# Measuring productivity without vanity metrics

## TL;DR
Common individual and team productivity metrics — lines of code, commit count, hours worked, story points, utilization — either don't measure what leaders think they measure, or actively incentivize behavior that hurts delivery performance. The book argues for measuring productivity at the outcome level (the four key metrics, `accelerate/03`/`accelerate/04`) rather than at the activity level, and for treating burnout and deployment pain as leading indicators worth tracking directly.

## The idea
Measuring "productivity" is genuinely hard, and the temptation is to measure whatever is easiest to count — lines of code written, commits made, hours logged, tickets closed, story points burned. These are **vanity metrics**: numbers that are easy to produce, look like they mean something, but don't reliably track the thing you actually care about (value delivered, system health, team sustainability), and worse, they're all *gameable* in ways that actively work against real productivity once people learn a metric is being watched.

The book's alternative is to measure productivity at the level of *outcomes* the four key metrics already capture — throughput and stability of value delivered to production — rather than at the level of individual *activity*. It goes further, though: productivity in a sustainable sense also depends on the human side of the system, so the book treats burnout and self-reported deployment pain as legitimate, measurable leading indicators of whether current productivity is sustainable or borrowed against the future.

## How it works

### Why common activity metrics fail
- **Lines of code (LOC)**: rewards verbosity, penalizes the (often more valuable) work of deleting or simplifying code. A senior engineer who deletes 500 lines of dead code and replaces a complex module with a 50-line one has, by this metric, done "negative work," even though that's frequently the highest-value change possible.
- **Commit count**: trivially gameable by splitting one logical change into many small commits, or inflated by noisy auto-generated commits (formatting, dependency bumps) that carry no real content.
- **Hours worked / utilization**: measures presence, not output, and actively conflicts with sustainable pace — a team logging more hours may be compensating for a broken process (see the deployment pain discussion below) rather than being more productive; treating hours as a target also directly predicts and produces burnout.
- **Story points / velocity**: an *estimation* tool, useful for a single team's own sprint planning, that becomes meaningless (and gameable via point inflation) the moment it's used to compare across teams or as an external productivity target — Goodhart's Law in action, where a measure that becomes a target stops being a good measure.

**Worked example — the LOC/velocity trap:** A manager, under pressure to show "productivity" improving, starts reporting team velocity (story points per sprint) up the chain. Within two sprints, the team's velocity number climbs 30% with no corresponding increase in actual delivered value — because the team, consciously or not, has started estimating tickets more generously (the same work now gets more points) in response to the metric being watched. The manager now has a number trending the "right" direction that is disconnected from reality, and worse, has lost the tool's original internal planning usefulness because the team's point scale has drifted.

### What to measure instead: outcomes, not activity
The book directs measurement toward the four key metrics (`accelerate/03`, `accelerate/04`) precisely because they're scoped to *value reaching production*, not to internal activity — you cannot inflate deployment frequency by writing more code that never ships, and you cannot hide a high change failure rate behind a high commit count. These metrics are also comparable across teams without needing to normalize for codebase size, language verbosity, or team seniority mix, unlike LOC or story points.

### Deployment pain as a leading indicator
The book introduces a specific, simple, and effective instrument: directly asking engineers to rate how painful deployments are, on a simple scale, and tracking that over time. This single self-reported question turns out to be a strong signal — high deployment pain correlates with the very organizational dysfunctions (large batches, manual gates, fear-driven caution) this whole subject has been describing, and it surfaces the problem *before* it fully shows up in the lagging outcome metrics. It's cheap to collect, hard to game (unlike a productivity number tied to compensation), and directly actionable — a team reporting high deployment pain has told you exactly where to invest next.

### Burnout as a productivity metric, not just a wellness metric
The book's data links technical and process capabilities (deployment automation, loosely coupled architecture, generative culture) not just to delivery performance but *negatively* to burnout — teams with better capabilities report significantly lower burnout, and burnout in turn predicts worse organizational outcomes over time (attrition, mistakes, disengagement). This reframes burnout from a purely HR/wellness concern into a productivity-relevant leading indicator: an organization "getting productivity" out of a team via unsustainable hours or constant firefighting is borrowing against future output, not generating it, and the book's framing treats measuring and addressing burnout as part of the same productivity-measurement discipline as the four key metrics, not a separate program.

**Worked example — hidden cost of "high productivity":** A team hits an aggressive quarterly deadline by working nights and weekends for six weeks, and leadership praises the "productivity." Two months later, two senior engineers on that team resign, citing burnout, and the team spends the next quarter re-hiring and re-onboarding, plus fixing a cluster of bugs traced back to rushed decisions made during the crunch. The quarter that "looked" most productive by a naive activity measure produced a net productivity *loss* over the two-quarter window once attrition and defect remediation are counted — exactly the kind of cost the book argues activity-based productivity measurement systematically hides.

## Pros
- Outcome-based metrics (the four key DORA metrics) are far harder to game than activity metrics and stay meaningful when compared across teams.
- Tracking deployment pain and burnout surfaces systemic problems as leading indicators, before they fully materialize as degraded lagging metrics (change failure rate, attrition).
- Shifts leadership conversations away from "who is working the most hours" toward "what is blocking the system from delivering value faster and more safely," which is both more accurate and less likely to damage morale.

## Cons
- Outcome metrics are team/system-level by design, which means they deliberately can't be used to rank or compare individual engineers — a real limitation for organizations whose performance-review processes expect individual productivity numbers.
- Self-reported measures (deployment pain, burnout surveys) require psychological safety (a generative culture, `accelerate/09`) to get honest answers — in a low-trust environment, people will under-report pain and burnout precisely when leadership most needs to know about it.
- Moving an organization off familiar activity metrics (velocity, utilization) that are deeply embedded in existing planning and reporting processes is a real change-management effort, not a metrics swap you can do unilaterally on one team.

## Alternatives
- **Individual output metrics (commits, LOC, tickets closed)** — the status quo this lesson argues against; easy to compute per-person, which is exactly why they're popular for individual performance management, despite being gameable and often anti-correlated with real value once watched.
- **Story points / velocity (used correctly, within a single team, for planning only)** — not wrong per se, just scoped wrong when used as a cross-team or external productivity metric; still legitimate as an internal estimation tool for the team that owns the scale.
- **SPACE framework (Forsgren et al., a later, complementary framework)** — a broader multi-dimensional productivity model (Satisfaction, Performance, Activity, Communication, Efficiency) developed partly by the same lead author after *Accelerate*, explicitly designed to avoid single-metric reductionism; worth knowing as the natural "next step" framework beyond this chapter's model.

## When to use it
Use the four key metrics plus deployment pain and burnout tracking as your organization's productivity dashboard whenever leadership asks "how productive is engineering," and push back specifically when asked to produce individual-level activity numbers (LOC, commit count) as a stand-in for productivity.

## When NOT to use it
Don't use deployment pain or burnout survey data punitively (e.g., to identify and pressure the "low productivity" team) — the moment self-reported data is used against the people reporting it, the data stops being honest, destroying the instrument's value; this connects directly to the generative-culture requirement in `accelerate/09`. Also, outcome metrics at the team/system level genuinely aren't designed to isolate individual contribution — don't force them into that role; individual performance evaluation needs a different (and inherently more qualitative) approach.

## Key takeaways / mental model
Ask of any productivity metric: "can someone make this number go up without actually delivering more value, just by changing their behavior in response to being watched?" If yes, it's a vanity metric. Outcome metrics scoped to value-reaching-production (the four key metrics) resist this failure mode much better than activity metrics — and sustainable productivity requires watching the human cost (deployment pain, burnout) as a leading indicator, not treating it as separate from the "real" productivity conversation.

## Self-check questions
1. Take a productivity metric your organization currently tracks (or one you've encountered) and apply the "can this be gamed without delivering more value" test from the key takeaways. What would gaming it look like in practice?
2. Explain why story points are a legitimate tool for a single team's internal planning but a poor metric for comparing productivity across teams. What specifically breaks when you widen the scope?
3. Walk through the six-week-crunch worked example and identify where a purely activity-based productivity measurement would have shown "success" while an outcome-and-burnout-based measurement would have flagged risk earlier.
4. Why does the book treat deployment pain as a useful metric despite being self-reported and subjective, rather than dismissing it as "just a feeling"? What property makes self-reported data trustworthy or untrustworthy here (connect to `accelerate/09`)?

## References
- Accelerate: The Science of Lean Software and DevOps (Forsgren, Humble, Kim), Chapter 3 (developer productivity section), Chapter 8: "Making Work Sustainable".
- Forsgren et al., "The SPACE of Developer Productivity" (ACM Queue, 2021) — a complementary, later framework worth knowing as a next step.
