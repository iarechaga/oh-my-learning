---
id: devops-handbook/16
subject: devops-handbook
title: "Measuring Outcomes: Delivery Performance and Reliability Metrics"
slug: delivery-reliability-metrics
status: drafted
mastery:
seniority: staff
source: The DevOps Handbook (Kim, Humble, Debois, Willis), Part V
prerequisites: [devops-handbook/06, devops-handbook/11, devops-handbook/13]
created: 2026-08-10
updated: 2026-08-10
---

# Measuring Outcomes: Delivery Performance and Reliability Metrics

## TL;DR
Four measures — deployment frequency, lead time for changes, mean time to restore (MTTR), and change failure rate — capture the whole system's actual performance across both speed and stability, and were later validated by the DORA (DevOps Research and Assessment) research program as reliably distinguishing high-performing organizations from low-performing ones; critically, elite performers score well on *all four together*, disproving the assumption that speed and stability trade off against each other.

## The idea
Every earlier lesson in this subject describes a practice (small batches, CI, telemetry, blameless postmortems, self-service governance). This lesson asks the meta-question: how do you know, in aggregate, whether any of it is actually working? Without a small set of trusted outcome metrics, organizations tend to fall back on either vanity metrics (lines of code, number of story points, number of meetings held) that don't correlate with actual delivery performance, or on pure anecdote ("it feels like we're shipping faster"). The Handbook's contribution — later empirically validated at large scale by the DORA research program across thousands of organizations — is that four specific metrics, two on speed and two on stability, together capture the health of the whole delivery system, and that the historically assumed trade-off between "fast" and "safe" is actually false: the data shows the best-performing organizations excel at both simultaneously, because the *same* practices (small batches, automation, fast feedback) that increase speed also increase stability.

## How it works

### The four metrics, precisely defined
- **Deployment frequency** — how often code deploys to production. Elite performers deploy on-demand, multiple times per day; low performers deploy between once a month and once every six months.
- **Lead time for changes** — the time from a code commit to that code running successfully in production (distinct from, but closely related to, the value-stream lead time in `devops-handbook/02`, which can also include the time from idea to commit). Elite performers: under one hour. Low performers: one to six months.
- **Mean time to restore (MTTR)** — the time from a production incident being detected to service being restored. Elite performers: under one hour. Low performers: one week to one month.
- **Change failure rate** — the percentage of deployments to production that result in degraded service requiring remediation (a rollback, a hotfix, an incident). Elite performers: 0-15%. Low performers: 46-60%.

### Why these four, together, disprove the speed/stability trade-off
The historically assumed intuition is that moving faster (higher deployment frequency, shorter lead time) necessarily means more risk (higher change failure rate, longer MTTR when things do break) — "move fast and break things" as an accepted cost. The DORA research's most important empirical finding directly contradicts this: elite performers score well on *all four* metrics simultaneously, not two-out-of-four. The mechanism explaining why isn't mysterious once you connect it to earlier lessons in this subject — small batches (`devops-handbook/03`) mean each individual deploy carries less risk and is easier to diagnose if it does fail; strong CI/CD (`devops-handbook/05`, `devops-handbook/06`) catches problems before they reach production; good telemetry and alerting (`devops-handbook/10`, `devops-handbook/11`) shrink MTTR by surfacing problems fast; and fast, direct incident feedback (`devops-handbook/12`) combined with blameless learning (`devops-handbook/13`) means each failure that does happen makes the next one less likely. Speed and stability aren't competing goals fought over with the same finite resource — they're both downstream effects of the same underlying practices.

**Worked example — reading a team's four-metric profile diagnostically.** A team reports: deployment frequency = weekly, lead time = 3 days, MTTR = 6 hours, change failure rate = 8%. Their low change failure rate and reasonably fast MTTR suggest their testing and incident-response practices (`devops-handbook/05`, `devops-handbook/11`) are working reasonably well — but their weekly deployment frequency and 3-day lead time suggest a batching or pipeline-automation problem (worth investigating with a value stream map, `devops-handbook/02`) rather than a quality problem. The diagnosis points investment toward `devops-handbook/06` (deployment pipeline automation) and `devops-handbook/07` (trunk-based development to reduce batch size), not toward more testing — because testing quality isn't where this particular team's actual constraint lives.

### The trap of optimizing metrics in isolation, disconnected from practice
A team under pressure to "improve deployment frequency" can trivially game the number — deploying trivial no-op changes frequently while the actual meaningful lead time for real features stays unchanged — without any real underlying improvement. The Handbook's caution, consistent with `devops-handbook/13`'s treatment of blameless postmortems, is that these four metrics are diagnostic instruments pointing at where to invest in real practices, not targets to be hit directly through metric-gaming; an organization that improves its four-metric scorecard through genuine adoption of small batches, CI/CD, telemetry, and blameless learning gets the real underlying benefit, while one that games the numbers directly gets a better-looking dashboard and no actual improvement in outcomes.

### Connecting delivery metrics to reliability metrics: where SRE picks up
This subject's four metrics focus on the delivery pipeline itself (how fast and how safely can we ship changes). `sre/*`'s treatment of SLIs and SLOs (`sre/02`, `sre/03`) and error budgets (`sre/04`) approaches a closely related but distinct question: given the deployment pipeline you have, how do you set and enforce reliability targets for the *running service* itself, and use error-budget consumption as an explicit, quantified release-governance signal? The two frameworks compose naturally: a healthy four-metric delivery profile is what makes it *safe* to deploy frequently against an error budget, and an error budget provides the release-governance mechanism (`devops-handbook/15`'s self-service standard-change logic can incorporate error-budget status directly) that decides when deployment frequency should throttle back in favor of stability work.

### Using the metrics to prioritize this subject's practices, in reverse
A useful way to close out this subject: given a team's actual four-metric profile, you can work backward to prioritize which specific practice from earlier lessons to invest in next — high change failure rate points to `devops-handbook/05`/`08` (testing, security gates); slow MTTR points to `devops-handbook/10`/`11`/`12` (telemetry, alerting, feedback routing); slow lead time or low deployment frequency points to `devops-handbook/03`/`06`/`07` (batch size, pipeline automation, trunk-based development); and recurring similar incidents point to `devops-handbook/13`/`14` (postmortem discipline and organizational propagation not actually happening).

## Pros
- Captures both speed and stability together, empirically disproving the assumption that they trade off, which reframes "fast vs. safe" debates with actual data rather than intuition.
- Gives a compact, standardized scorecard that's comparable across teams and over time, useful for diagnosing where to invest next rather than relying on anecdote.
- Connects cleanly back to nearly every earlier practice in this subject, functioning as an outcome-level check on whether those practices are actually working.

## Cons
- Easy to game superficially (trivial frequent deploys, narrowly-defined "success" for change failure rate) if treated as a target rather than a diagnostic signal — Goodhart's Law applies directly.
- The specific numeric benchmarks (elite/high/medium/low performer bands) are drawn from broad industry survey data and don't automatically transfer to every context (a safety-critical embedded system has a different acceptable change failure rate than a low-stakes internal tool).
- Measuring these four metrics accurately requires the underlying telemetry and deployment-pipeline infrastructure (`devops-handbook/06`, `devops-handbook/10`) already be in place — a team without that infrastructure can't measure its own baseline reliably, which is itself a diagnostic signal worth acting on.

## Alternatives
- **SLO/error-budget-based reliability measurement** (`sre/03`, `sre/04`) — focuses on the running service's user-facing reliability rather than the pipeline's delivery performance; complementary rather than competing, answering a different but related question.
- **Velocity/story-point tracking** — a common alternative "how fast are we going" metric from Agile practice; measures planning-and-estimation throughput rather than actual delivery-to-production performance, and is well-known to be gameable and not comparable across teams with different estimation habits.
- **Business-outcome metrics (revenue, customer satisfaction, NPS)** — measure the ultimate goal delivery performance is meant to serve, but are further removed from engineering practice and slower-moving, making them poor short-feedback-loop signals for whether a specific technical practice is working.

## When to use it
Track all four metrics together, as a standing scorecard, once your pipeline and telemetry infrastructure can measure them accurately — use the profile to diagnose which of this subject's earlier practices most needs investment next, rather than chasing any single metric in isolation.

## When NOT to use it
Don't set these metrics as isolated targets divorced from the underlying practices that actually move them — a mandate to "increase deployment frequency" without corresponding investment in small batches, CI/CD, and telemetry just produces metric gaming or genuine harm (deploying more without the safety practices to back it up increases change failure rate and MTTR, which the other three metrics will then reveal). Don't compare raw numbers across fundamentally different contexts (a safety-critical system vs. an internal tool) without accounting for genuinely different acceptable risk profiles.

## Key takeaways / mental model
Read the four metrics as a diagnostic profile, not a single score: two speed numbers (deployment frequency, lead time) and two stability numbers (MTTR, change failure rate), and an elite profile requires all four to be strong together — a profile strong on speed but weak on stability, or vice versa, points precisely at which practices from this subject still need investment.

## Self-check questions
1. Using the worked example team's profile (weekly deploys, 3-day lead time, 6-hour MTTR, 8% change failure rate), explain why the diagnosis points toward pipeline automation and batch size rather than testing quality — what in the numbers rules out a testing-quality problem?
2. Why does the DORA research's finding that elite performers score well on all four metrics simultaneously matter more than any single metric's absolute value?
3. A team's deployment frequency has doubled after being told to "ship more often," but change failure rate has also tripled. What likely went wrong, using this lesson's reasoning about metrics as diagnostics vs. targets?
4. How do this subject's delivery metrics relate to, but differ from, `sre/03`'s and `sre/04`'s SLO and error-budget framing? Could a team have a strong four-metric delivery profile and still have a reliability problem an SLO would catch?

## References
- The DevOps Handbook (Kim, Humble, Debois, Willis), Part V: "The Third Way: Technical Practices of Continual Learning," and the DORA (DevOps Research and Assessment) *Accelerate* research program, which independently validated these four metrics at scale.
- See also: `devops-handbook/02` (value stream mapping, a complementary diagnostic), `sre/03` and `sre/04` (SLOs and error budgets, the closely related reliability-measurement framework).
