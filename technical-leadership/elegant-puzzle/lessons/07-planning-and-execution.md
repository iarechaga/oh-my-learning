---
id: elegant-puzzle/07
subject: elegant-puzzle
title: Planning and execution in medium and large organizations
slug: planning-and-execution
status: drafted
mastery:
seniority: senior
source: An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Planning" and "Managing Technical Quality"
prerequisites: [elegant-puzzle/01, elegant-puzzle/06]
created: 2026-08-10
updated: 2026-08-10
---

# Planning and execution in medium and large organizations

## TL;DR
Planning at scale is a forecasting-under-uncertainty problem, not a scheduling problem: the goal of a planning process isn't to predict the future correctly, it's to surface conflicts and dependencies early enough to resolve them cheaply, and to create a shared, revisable commitment that execution can be measured against.

## The idea
At small scale, planning is informal: a handful of engineers talk in a room and agree on what to build next. That doesn't survive growth, because the number of dependencies between teams grows faster than headcount -- every additional team is a potential blocker or blocked-by relationship for every other team. Formal planning processes (quarterly planning, roadmap reviews, dependency mapping) exist to surface those cross-team conflicts while they're still cheap to resolve (in a planning meeting) rather than expensive (discovered mid-quarter when Team A is blocked on Team B, who didn't know Team A needed them). The plan produced is never going to be exactly right -- Larson is explicit that plans are wrong the moment they're written, because the future is uncertain -- but the *process* of planning, done well, is valuable regardless of how accurate the resulting document turns out to be.

## How it works

### Plans are forecasts, not commitments carved in stone
Treat a quarterly plan the way a weather forecast is treated: useful for decision-making, expected to be revised as new information arrives, and a failure mode if anyone treats the original forecast as something reality is now obligated to match. A team that hits 70% of a well-calibrated plan while adapting sensibly to what they learned mid-quarter has executed well; a team that hits 100% of a plan by refusing to incorporate anything learned along the way has often executed badly, at the cost of ignoring real information.

### Surfacing dependencies early is the main point
The most valuable output of a cross-team planning process is not the roadmap itself, it's the dependency graph it forces into the open: "Team A's Q2 project needs an API from Team B, who hadn't planned to build it until Q3." Found during planning, this is a scheduling conversation. Found in week 6 of the quarter, it's a crisis that stalls Team A for weeks. Formal planning rituals (a dependency-review meeting, a shared planning doc reviewed across teams before commitment) exist specifically to catch this class of problem while it's still cheap.

**Worked example.** A company runs quarterly planning where each team submits its top 3 priorities and any cross-team asks two weeks before the quarter starts. During review, it surfaces that four different teams all expect the Platform team to ship a new deployment tool this quarter, but Platform only planned for one such project. Because this surfaced during planning, leadership can explicitly prioritize which team's need is most urgent, tell the other three to plan around the current tooling for one more quarter, and avoid all four teams independently discovering the conflict mid-quarter and improvising incompatible workarounds.

### Buffer, don't pad
A common instinct under planning pressure is to pad every estimate ("say it'll take 3 weeks instead of 2, just in case"), but padding hides real risk and information rather than managing it -- nobody can distinguish a genuinely padded estimate from an accurate one, so padding degrades the whole plan's reliability at once. The better mechanism is an explicit, visible buffer at the portfolio level (e.g., "we're only committing to 80% of estimated capacity this quarter, leaving 20% for the inevitable unplanned work"), which preserves the honesty of individual estimates while still accounting for uncertainty.

### Managing technical quality inside the plan
Planning that only tracks feature work reliably starves tech-debt and quality work, because tech debt has no natural advocate in a planning process built around feature deadlines -- it competes against work with a visible deadline and a visible stakeholder, and it usually loses. Larson's guidance: make quality and debt-reduction work visible and budgeted for explicitly in the plan (a fixed percentage of capacity, or a named set of debt-reduction projects with the same planning status as feature work), rather than hoping it happens in the gaps, because gaps under deadline pressure are exactly where it gets cut first.

### Execution: track leading indicators, not just the deadline
Waiting until the deadline to find out whether a project is on track means finding out too late to react. Track leading indicators throughout the quarter -- is scope creeping, are the riskiest technical unknowns being resolved early or being deferred to the end, is the team blocked on something -- so a project heading for trouble is visible in week 4, not week 11 of a 12-week quarter.

## Pros
- Surfacing dependencies during planning avoids the much higher cost of discovering them mid-execution.
- Treating plans as forecasts rather than commitments reduces the incentive to hide risk through padding or to make bad calls just to "hit the number."
- Explicit budgeting for tech-debt work protects it from being silently squeezed out by feature deadlines every single quarter.

## Cons
- Formal planning processes have real overhead (meetings, documents, review cycles) that can feel like pure bureaucracy, especially to teams whose work has few cross-team dependencies.
- "Plans are forecasts, not commitments" can be misused as an excuse for chronic under-delivery if there's no accountability mechanism attached to it.
- Explicit capacity buffers and debt-work allocations are easy for leadership to quietly erode under pressure ("just this once, let's commit to 100%"), and once eroded, they're hard to restore.

## Alternatives
- **No formal cross-team planning (fully autonomous team roadmaps)** -- each team plans independently; minimal overhead, but reliably fails once teams have real dependencies on each other, producing the mid-quarter-discovery problem described above.
- **Heavyweight, long-horizon annual planning** -- plan a full year in detail up front; gives a longer view for large capital-intensive bets, but the forecast accuracy degrades sharply past a quarter or two, so detailed annual plans are often stale well before the year is out.
- **Kanban / continuous flow with no fixed planning cadence** -- prioritize continuously rather than in quarterly batches; well suited to teams with few cross-team dependencies and highly variable, hard-to-forecast work, but loses the dependency-surfacing benefit that a shared planning cadence provides across teams.

## When to use it
Use structured, cross-team planning once you have real dependencies between teams -- once a delay on one team can silently stall another. It's essential for medium-to-large orgs (multiple teams, shared platforms) and especially valuable before quarters with major cross-team initiatives.

## When NOT to use it
Don't impose heavyweight quarterly planning on a small, low-dependency team where informal coordination is sufficient -- the ritual's overhead only pays for itself once the dependency-surfacing benefit is worth more than the meeting time it costs.

## Key takeaways / mental model
The plan is disposable; the planning process's job is to surface conflicts and dependencies while they're still cheap to fix. Judge a quarter's execution by whether the team adapted well to what they learned, not by whether they matched the original document exactly -- and protect tech-debt work with an explicit budget, because it has no natural deadline to defend it.

## Self-check questions
1. A team hits 100% of their quarterly plan by refusing to adjust when they discovered a better approach mid-quarter. Is that good execution? Why or why not?
2. Describe a cross-team dependency conflict that would be cheap to resolve if found during planning but expensive if found in week 8 of a 12-week quarter. What planning mechanism would have surfaced it early?
3. Why does padding individual estimates degrade a plan's overall reliability, and what's the alternative that preserves both honesty and a safety margin?
4. Your org's planning process has no explicit allocation for tech-debt work. Predict what happens to that work over several quarters, and explain the mechanism, not just the outcome.

## References
- An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Planning" and "Managing Technical Quality", Part III.
