---
id: accelerate/03
subject: accelerate
title: Deployment frequency and lead time for changes
slug: deployment-frequency-and-lead-time
status: drafted
mastery:
seniority: senior
source: Accelerate (Forsgren, Humble, Kim), Chapter 2 "Measuring Performance"
prerequisites: [accelerate/01, accelerate/02]
created: 2026-08-10
updated: 2026-08-10
---

# Deployment frequency and lead time for changes

## TL;DR
Deployment frequency (how often you ship to production) and lead time for changes (how long from code committed to code running in production) are the two throughput metrics in the DORA model. They measure batch size indirectly — high frequency and short lead time both mean small batches — and small batches are the mechanism that makes software delivery simultaneously faster and safer.

## The idea
Throughput in software delivery is easy to measure badly. "Lines of code shipped," "story points completed," and "number of features released" all sound like throughput but are gameable, don't reflect actual value delivered to users, and don't connect to risk. DORA's research settled on two metrics instead, both defined from the perspective of when value actually reaches the customer, not when work was reported "done" internally:

- **Deployment frequency**: how often does the organization successfully release to production (or to end users, for non-server software)?
- **Lead time for changes**: how long does it take to go from code committed to that code successfully running in production?

Both metrics share a hidden variable they're really measuring: **batch size**. If you deploy once a quarter, each deployment necessarily bundles a quarter's worth of changes — a large batch. If you deploy multiple times a day, each deployment is a handful of changes — a small batch. Lead time tells the same story from a different angle: a long lead time means change sits in a queue (code review, staging, manual QA, change advisory board) accumulating with other changes before release, which is another way of describing large batches. Small batches are the throughline: they reduce the amount of untested, unreleased work in flight, they make each individual deployment lower-risk (less to go wrong, easier to isolate what did), and they shorten the feedback loop from "we wrote this code" to "we know if it works in production."

## How it works

### Defining deployment frequency precisely
Deployment frequency is not "how often we cut a release branch" or "how often we run a build" — it's how often a deployment actually reaches production and is exposed to real usage (accounting for techniques like feature flags and canary releases, where code can be deployed without being fully "released" to all users — DORA counts the deployment event, not necessarily 100% user exposure). The DORA performance clusters bucket organizations roughly as:

| Performance level | Deployment frequency |
| --- | --- |
| Elite | Multiple deploys per day (on-demand) |
| High | Between once per day and once per week |
| Medium | Between once per week and once per month |
| Low | Between once per month and once every six months |

**Worked example:** A payments team deploys to production 40 times a day via an automated pipeline, each deploy carrying one or two merged pull requests. A separate reporting team, working on a legacy monolith, deploys once every six weeks via a manual release process with a change advisory board. Even if both teams write comparable-quality code, the payments team's batch size (1-2 changes/deploy) versus the reporting team's (potentially hundreds of changes bundled into a six-week release) means the payments team can isolate and roll back a bad change trivially, while the reporting team, if something breaks, must diagnose across a much larger diff.

### Defining lead time for changes precisely
Lead time here is scoped specifically to **the engineering lead time**: from code commit to code running in production — not the broader "idea to production" lead time that includes product discovery, design, and prioritization (that broader cycle time is a related but distinct concept, more connected to product management practice than to the technical/process capability this metric targets). This scoping matters: it isolates the part of the pipeline that engineering practices (CI/CD, code review process, test automation, release process) directly control, rather than conflating it with upstream product decisions engineering doesn't own.

| Performance level | Lead time for changes |
| --- | --- |
| Elite | Less than one hour |
| High | Between one day and one week |
| Medium | Between one week and one month |
| Low | Between one month and six months |

**Worked example — decomposing a slow lead time:** A team measures their lead time at three weeks and wants to know why. They break the pipeline into stages: code review (2 days average, often waiting for a specific senior reviewer), CI test suite (45 minutes), staging deployment and manual QA sign-off (5 business days, because QA is a separate team with its own queue), and a weekly change advisory board that must approve before production deploy (up to 6 days wait depending on where in the week the change lands). The largest single contributor is the human-queue-based review gates (QA queue, CAB), not the automated pipeline. This is a common finding in the book: lead time bottlenecks are usually process and organizational (queues, handoffs, approval gates), not the raw speed of the build/test tooling itself.

### Why these two metrics move together
Deployment frequency and lead time are not independent — they are two views of the same underlying batch-size variable, and the research treats them as correlated aspects of throughput. An organization that shortens lead time (removes queues, automates gates) will almost mechanically increase deployment frequency, because it becomes cheap and fast to get any given change to production, removing the incentive to batch changes up to amortize a costly release process.

## Pros
- Both metrics are measurable objectively from deployment logs and version control, resisting the gaming that afflicts metrics like "story points" or "features shipped."
- They correlate directly with batch size, which is the actual causal lever for reducing risk — so improving these metrics genuinely reduces risk, it isn't just a vanity number going up.
- They're comparable across teams and organizations without needing to normalize for team size or codebase complexity, since they're about cadence and time, not volume.

## Cons
- Easy to game locally without real improvement — e.g., splitting one meaningful change into many trivial deploys to inflate deployment frequency without actually shortening the underlying lead time for the change that matters.
- Deployment frequency alone says nothing about whether those deployments are stable — see `accelerate/04` for the paired stability metrics needed to prevent this metric from being optimized in isolation.
- Lead time as scoped (commit to production) can create a blind spot: a team can look great on this metric while the *broader* idea-to-production cycle (including product discovery and design queues) remains slow, misleading stakeholders about overall speed to value.

## Alternatives
- **Cycle time (ticket-to-done)** — measures work-in-progress-to-completion in a project management sense; useful for team-level flow but doesn't capture "actually running in production," so it can look good while deployment is still gated behind a slow release process.
- **Velocity (story points per sprint)** — an estimation-based throughput proxy long used in Scrum contexts; notoriously ungameable-resistant is the wrong word — it's *easily* gamed (points inflate over time) and doesn't correlate with the batch-size mechanism this lesson describes.
- **Feature/release-count metrics** — count "things shipped" rather than cadence; conflates value delivered with delivery cadence and is easy to game by bundling or splitting arbitrarily.

## When to use it
Use deployment frequency and lead time as your primary throughput dashboard when you want an objective, hard-to-game view of your delivery pipeline's actual cadence, and specifically when diagnosing where batch size is too large (a proxy for undiagnosed risk and slow feedback).

## When NOT to use it
Don't report deployment frequency or lead time in isolation to leadership as "we're doing great" without also reporting the paired stability metrics (`accelerate/04`) — a team could be shipping fast and constantly breaking production, and these two metrics alone won't reveal that. Also don't use lead time (commit-to-production) as a stand-in for the broader product cycle time (idea-to-production) when the audience actually cares about the latter — be explicit about the scope.

## Key takeaways / mental model
Deployment frequency and lead time are both proxies for one thing: batch size. Ask "how much unreleased work is currently sitting in the pipeline?" — the smaller that number, the higher your deployment frequency and the shorter your lead time will mechanically be, and the lower your risk per deployment. Improving these two metrics is really about shrinking batch size, not about working faster in a raw sense.

## Self-check questions
1. A team wants to improve their deployment frequency number without doing the harder work of shrinking batch size. Describe a way they could game the metric, and explain what would still be true about their actual risk profile.
2. Decompose an imaginary lead time of two weeks into pipeline stages the way the worked example does. Which stages are automatable, and which are organizational/queue-based? Why does that distinction matter for what to fix first?
3. Why does the book scope "lead time for changes" specifically to commit-to-production, rather than idea-to-production? What's the risk of conflating the two when talking to a non-engineering stakeholder?
4. Explain the causal link between deployment frequency, lead time, and batch size in your own words, without using the word "throughput."

## References
- Accelerate: The Science of Lean Software and DevOps (Forsgren, Humble, Kim), Chapter 2: "Measuring Performance".
