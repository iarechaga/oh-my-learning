---
id: accelerate/04
subject: accelerate
title: Change failure rate and time to restore service
slug: change-failure-and-restore-time
status: drafted
mastery:
seniority: senior
source: Accelerate (Forsgren, Humble, Kim), Chapter 2 "Measuring Performance"
prerequisites: [accelerate/01, accelerate/02, accelerate/03]
created: 2026-08-10
updated: 2026-08-10
---

# Change failure rate and time to restore service

## TL;DR
Change failure rate (what percentage of production changes cause a failure requiring remediation) and time to restore service (how long it takes to recover when a failure happens) are the two stability metrics in the DORA model. Paired with deployment frequency and lead time (`accelerate/03`), they complete the four-metric model, proving that elite performers achieve both high throughput *and* high stability — refuting the idea that speed must be traded off against safety.

## The idea
Throughput metrics alone are dangerous: an organization could deploy constantly and have every third deployment break production, and deployment frequency alone would still look great. DORA's model closes that loophole with two stability metrics that measure the cost of failure, not just how fast you move.

- **Change failure rate**: of all changes deployed to production, what percentage result in degraded service (an outage, a rollback, a hotfix) requiring remediation?
- **Time to restore service (MTTR — mean time to restore/recover)**: when a production failure happens, how long does it take to restore service?

These two, together with deployment frequency and lead time, give a complete picture: you cannot look good on the model by sacrificing stability for speed, or vice versa, because both dimensions are measured. The book's single most important empirical finding rides on this pairing: elite performers are *not* trading stability for speed — they score well on all four metrics simultaneously, deploying far more often than low performers while also failing less often and recovering faster when they do fail.

## How it works

### Defining change failure rate precisely
Change failure rate is scoped to changes that reach production and require some form of remediation — a rollback, a hotfix, a patch — as opposed to, say, a bug found and fixed before release (that's a normal part of development, not a "change failure" in this metric's sense). It's expressed as a percentage: failed changes / total changes deployed.

| Performance level | Change failure rate |
| --- | --- |
| Elite | 0-15% |
| High | 16-30% |
| Medium (and Low, similar range in various report years) | 16-30%+ |

(Exact cluster boundaries have shifted slightly across report years as the sample grew, but the qualitative finding is stable: elite performers have a meaningfully *lower* change failure rate than low performers, not a higher one, despite deploying far more often.)

**Worked example:** Team A deploys once a quarter, and 1 in 10 of those deployments (10%) requires an emergency rollback. Team B deploys 50 times a week, and 1 in 20 (5%) of those requires a rollback. Team B's change failure rate is *lower* despite deploying roughly 650x more often per quarter — because each of Team B's deployments is small enough to test thoroughly, to reason about in review, and to catch problems in before they compound. This is the small-batch mechanism from `accelerate/03` showing up again: smaller batches are individually less likely to fail, not just individually cheaper to fix.

### Defining time to restore service precisely
MTTR measures the clock from "service is degraded" to "service is restored" — not to root-cause-fully-understood, not to "post-mortem written," just to restored. This scoping matters because it isolates the operational capability (detection, diagnosis, rollback/fix mechanisms) from the separate (also valuable, but different) practice of blameless post-incident learning.

| Performance level | Time to restore service |
| --- | --- |
| Elite | Less than one hour |
| High | Less than one day |
| Medium | Less than one day |
| Low | Between one week and one month |

**Worked example — why small batches shorten MTTR:** A production incident occurs after a deployment. If that deployment contained one change, the on-call engineer has one suspect: revert it, service restored in minutes. If that deployment bundled 200 changes (a large, infrequent release), the on-call engineer must bisect through 200 candidate changes under pressure, likely paging multiple teams whose code was in the batch, dramatically extending time to restore. The same batch-size mechanism that drives deployment frequency and lead time (`accelerate/03`) also drives MTTR: small batches make diagnosis nearly trivial (small diff, recent change, fresh in the author's memory) while large batches make diagnosis a forensic investigation.

### The headline finding: speed and stability move together
Putting all four metrics side by side is the chapter's central payoff. Across the research years, the data consistently showed elite performers *simultaneously* leading on deployment frequency, lead time, change failure rate, and time to restore — not leading on two while lagging on the other two. This directly falsifies the "speed vs. stability trade-off" intuition from `accelerate/01`: the mechanism (small batches, strong technical practices, fast feedback) that improves throughput is the *same* mechanism that improves stability, so an organization that genuinely invests in the underlying capabilities gets both, and an organization that tries to buy stability by slowing down (bigger batches, more approval gates) actually gets worse at both.

## Pros
- Closes the loophole in throughput-only measurement — a team can no longer look good by deploying fast and breaking things often.
- MTTR in particular focuses attention on detection and recovery capability (observability, rollback mechanisms, feature flags) rather than only on defect *prevention*, which is a distinct and equally important operational muscle.
- Both metrics are derivable from incident/deployment records without requiring subjective self-assessment, keeping them relatively hard to game.

## Cons
- "What counts as a failure requiring remediation" needs a clear, consistently-applied definition or the metric becomes inconsistent across teams (a rollback clearly counts; a minor cosmetic bug fixed in the next normal release is more ambiguous) — teams must agree on the boundary up front.
- MTTR can be gamed by defining "restored" loosely (e.g., declaring service restored once a workaround is applied, even if the underlying cause resurfaces later) — the metric needs a consistent, honest definition of "restored" to stay meaningful.
- Neither metric alone tells you *why* failures happen or recovery is slow — they're diagnostic signals that require deeper investigation (architecture, `accelerate/06`; test automation, `accelerate/07`) to act on.

## Alternatives
- **SLA/SLO error budgets** — a related but distinct framework (popularized separately by Google SRE) that tracks acceptable unreliability over a time window; complements change failure rate and MTTR by giving a business-facing reliability target, but doesn't attribute failure specifically to *changes* the way change failure rate does.
- **Defect escape rate (QA-era metric)** — counts bugs that escape pre-production testing into production; overlaps conceptually with change failure rate but is typically scoped to functional defects found by QA, not to operational failures (outages, rollbacks) more broadly.
- **Post-incident review count/severity trends** — tracks incidents qualitatively over time; valuable for organizational learning but not a normalized rate like change failure rate, so it's harder to compare across teams of different deployment volumes.

## When to use it
Pair change failure rate and MTTR with deployment frequency and lead time (`accelerate/03`) any time you report or reason about delivery performance — never report throughput metrics without their stability counterparts, and vice versa. Use MTTR trends specifically to evaluate investments in observability, alerting, and rollback tooling.

## When NOT to use it
Don't use change failure rate to punish individuals or teams in a blame-oriented way (that undermines the generative culture `accelerate/09` describes, which is itself a predictor of the very outcomes these metrics measure) — use it as a system-level signal to invest in technical practices, not as a scorecard for performance reviews. Don't rely on MTTR alone when the real problem is *detection* time (how long until you even know something's wrong) — if failures go unnoticed for hours before the MTTR clock even starts, you have a monitoring gap the metric won't surface by itself.

## Key takeaways / mental model
Stability metrics exist to prevent throughput metrics from being gamed, and the pairing reveals the book's central insight: small batches (the mechanism behind deployment frequency and lead time) are *also* the mechanism behind low change failure rate and fast MTTR. There is no dial to trade off — investing in the capabilities that produce small, safe batches moves all four metrics in the same direction at once.

## Self-check questions
1. Explain why an organization that deploys once a quarter would plausibly have a *higher* change failure rate than one that deploys 50 times a week, using the batch-size mechanism from `accelerate/03`.
2. Your team's MTTR looks excellent on paper, but customers keep reporting that "the site was slow for hours" before any alert fired. What gap does this reveal, and which metric (or missing metric) would surface it?
3. A manager proposes using change failure rate in individual performance reviews to identify "which engineers cause the most outages." Explain, using this lesson's framing, why that is likely to backfire.
4. Give a concrete example of how "time to restore" could be gamed by a loose definition of "restored," and propose a tighter definition that would close that loophole.

## References
- Accelerate: The Science of Lean Software and DevOps (Forsgren, Humble, Kim), Chapter 2: "Measuring Performance".
