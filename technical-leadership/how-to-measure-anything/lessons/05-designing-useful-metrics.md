---
id: how-to-measure-anything/05
subject: how-to-measure-anything
title: Designing useful metrics tied to concrete decisions
slug: designing-useful-metrics
status: drafted
mastery:
seniority: staff
source: How to Measure Anything (Douglas W. Hubbard), Chapter 4, Chapter 7
prerequisites: [how-to-measure-anything/01, how-to-measure-anything/04]
created: 2026-08-10
updated: 2026-08-10
---

# Designing useful metrics tied to concrete decisions

## TL;DR
A metric only earns its keep if it can change what someone does — if you can't name the decision it feeds and describe how a different measured value would change that decision, don't build it. Most dashboards fail this test and exist as decoration, not decision support.

## The idea
Organizations reflexively build dashboards and metrics because "we should be data-driven," without first asking what decision the data is meant to inform. Hubbard's framing, formalized here as **Applied Information Economics**, insists on working backwards from the decision: identify the decision, identify what information would change it, then and only then design the measurement. This inverts the common practice of measuring everything that's cheap or available (vanity metrics: lines of code, commit counts, story points closed) and hoping insight emerges. A metric with no attached decision is trivia — interesting, maybe, but not worth the engineering and maintenance cost of collecting, storing, and displaying it. The test Hubbard proposes is blunt: for any proposed metric, ask "if this number came in at value A versus value B, would anyone do anything differently?" If the answer is no for any plausible value the metric could take, the metric isn't decision-relevant and shouldn't be built, no matter how "insightful" it sounds in a planning meeting.

## How it works

### The decision-first design procedure
1. **Name the decision.** Not "understand developer productivity" (not a decision) but "decide whether to fund a second platform team next quarter" (a decision, with a real cost and a real alternative).
2. **Name the decision-maker and the threshold.** Who decides, and what would make them choose one option over another? ("The VP will fund the team if toil is costing more than ~15 engineer-hours/week across the org; below that, the cost doesn't clear the bar against other roadmap items.")
3. **Work out what variable(s) actually drive that threshold**, using decomposition (`how-to-measure-anything/04`) if the driving variable is itself fuzzy.
4. **Design the metric to estimate exactly that variable** — no more, no less. Resist the urge to also track five adjacent "nice to know" numbers once you're building the pipeline anyway; each one has an ongoing cost (see Cons).
5. **Set the reporting cadence to the decision's cadence**, not to an arbitrary "let's check daily" default. A quarterly funding decision does not need a real-time dashboard; a production incident-response decision does.

### Worked example: designing an "engineering velocity" metric properly
A common, badly-designed request: "give leadership a velocity dashboard so we can track team performance." Applying decision-first design:
- **What decision is this actually for?** Pressed further, the request turns out to be about two different decisions bundled together: (a) whether a specific team is understaffed relative to its roadmap commitments, and (b) whether to intervene when a team seems to be "slow." These are different decisions needing different metrics — bundling them into one "velocity" number is the first mistake.
- **Decision (a): staffing.** The threshold that matters is whether committed roadmap work is slipping due to capacity vs. due to scope creep vs. due to external blockers. The right metric isn't story points/sprint (notoriously gameable and not comparable across teams) but **committed-vs-delivered scope per quarter, tagged by slip reason** (capacity, scope change, external blocker) — a metric that directly maps to the staffing decision because it separates the causes leadership can and can't act on.
- **Decision (b): intervention.** The threshold that matters is outlier detection — is this team's cycle time meaningfully worse than its own historical baseline or than comparable teams, in a way that suggests a fixable systemic issue (e.g., review bottlenecks, flaky CI, unclear requirements)? The right metric is **cycle time broken down by stage (coding, review, QA, deploy) compared against the team's own trailing 6-month baseline** — not a cross-team leaderboard, which invites gaming and morale damage without informing any real decision (comparing unlike teams doing unlike work rarely identifies an actionable intervention).
- **Result:** two narrow, decision-tied metrics replace one vague "velocity dashboard," each with a clear owner, a clear threshold, and a clear "so what happens if this number changes."

### The "would anyone act differently" filter, applied
Before building any metric, explicitly write down: "If this metric reads [low value], we would do X. If it reads [high value], we would do Y." If X and Y are the same action, or if nobody can articulate X and Y at all, the metric fails the filter. Example failure: a team proposes tracking "number of Slack messages in the eng channel" as an "engagement" metric. Pressed on the filter: "if it's high, we'd... feel good about engagement? If it's low, we'd... worry?" No concrete action attaches to either value — this metric fails and should not be built.

### Leading vs. lagging, and the cost of a metric over its lifetime
A well-designed metric also considers *when* the decision needs the information. A lagging metric (e.g., quarterly churn rate) confirms a decision was right or wrong after the fact — useful for calibrating future decisions but too late to change the current one. A leading metric (e.g., weekly trial-to-paid conversion trend) can inform a decision while there's still time to act. Part of decision-first design is asking whether the decision window requires a leading indicator, and if the cheap/obvious metric available is actually lagging and therefore useless for the decision at hand, no matter how easy it would be to collect.

## Pros
- Prevents the common failure mode of dashboard sprawl — dozens of metrics nobody consults, each still costing engineering time to maintain and each still capable of being misread and acted on wrongly.
- Forces stakeholders to be explicit about decision thresholds up front, which frequently surfaces disagreement about what actually matters before any data collection effort is wasted.
- Produces metrics that are inherently more resistant to gaming, because they're narrowly tied to a real decision rather than a broad, ambiguous proxy for "goodness" that people learn to optimize superficially (Goodhart's Law).

## Cons
- Requires genuine access to and negotiation with the actual decision-maker, which is organizationally harder than just building "the dashboard everyone asks for."
- Decision-first metrics can feel narrow or unsatisfying to stakeholders who wanted a broad, exploratory "let's see what the data shows" dashboard — this approach deliberately trades exploratory breadth for decision relevance.
- If the decision itself changes (reorg, new strategy), a tightly-scoped metric may need to be redesigned, whereas a broad, generic dashboard degrades more gracefully (though less usefully) across such changes.

## Alternatives
- **Exploratory / broad-spectrum dashboards** — collect a wide range of plausibly-useful metrics without a specific decision in mind, hoping patterns emerge; appropriate in genuinely early, undirected research contexts, but expensive to maintain and prone to spurious pattern-finding at scale.
- **OKRs / KPI frameworks** — top-down metric-setting tied to strategic goals rather than individual decisions; complementary to this lesson's approach (OKRs can supply the "decision" — did we hit the goal, do we change strategy) but still needs decision-first design applied to each individual KPI to avoid vanity metrics creeping in.
- **North Star Metric (product analytics)** — a single metric chosen to proxy overall product health; useful for org-wide alignment but risks becoming exactly the kind of "no specific decision attached, no clear action at any value" metric this lesson warns against unless it's explicitly tied to concrete strategic decisions.

## When to use it
Whenever someone proposes building a new metric, dashboard, or report — especially before committing engineering time to instrument, pipeline, and visualize it. Also apply retroactively to existing dashboards during a cleanup: run the "would anyone act differently" filter on every existing widget and retire the ones that fail.

## When NOT to use it
Skip the full decision-first ritual for cheap, ephemeral, one-off investigative queries (e.g., "let me quickly check how many users hit this error last week" to debug an incident) — that's investigation, not metric design, and doesn't need a standing decision framework. Also, don't force decision-first rigor onto genuinely exploratory research spikes where the goal is legitimately "see what's there" before any decision exists to attach to.

## When a metric predates its decision
Sometimes a metric already exists (e.g., a legacy dashboard) and the task is to evaluate whether to keep it. Apply the same filter retroactively rather than assuming past investment justifies continued cost — sunk cost in building a dashboard is not a reason to keep paying its maintenance cost if it fails the "would anyone act differently" test today.

## Key takeaways / mental model
Before building any metric, write one sentence: "This tells [decision-maker] whether to [action A] or [action B]." If you can't finish that sentence honestly, you don't need the metric yet — go find the decision first, then design backwards from it.

## Self-check questions
1. Pick an existing dashboard or metric at your workplace. Apply the "would anyone act differently" filter: at what value would someone change what they do, and what would they do differently?
2. Explain why "engineering velocity" as a single cross-team number is usually a poorly-designed metric, using the decomposition into two decisions from the worked example.
3. A stakeholder asks for "a metric on code quality" with no further detail. What two or three questions would you ask before building anything?
4. Describe a metric you've seen that was gamed (people optimized the number without improving the underlying thing it was meant to represent). How would decision-first design have made it more gaming-resistant?

## References
- How to Measure Anything: Finding the Value of Intangibles in Business (Douglas W. Hubbard), Chapter 4: "Clarifying the Measurement Problem," and Chapter 7: "The AIE (Applied Information Economics) Approach."
