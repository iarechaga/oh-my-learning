---
id: evolutionary-architectures/04
subject: evolutionary-architectures
title: "Incremental Change (Deployment Pipelines)"
slug: incremental-change
status: drafted
mastery: 
seniority: senior
source: "Building Evolutionary Architectures, 2nd ed. (Ford, Parsons, Kua, Sadalage), Chapter 4"
prerequisites: [evolutionary-architectures/01, evolutionary-architectures/02]
created: 2026-08-10
updated: 2026-08-10
---

# Incremental Change (Deployment Pipelines)

## TL;DR
Deployment pipelines are the delivery mechanism that makes incremental change real: a
staged, automated sequence (build -> test -> fitness functions -> deploy) that every
change flows through before reaching production. Fast, reliable pipelines aren't a
productivity nicety — they're the *precondition* for evolutionary architecture, because
without them, "incremental" change is either too slow to be incremental in practice, or
too risky to be trusted without an expensive manual gauntlet.

## The idea

### Incremental development vs. incremental deployment
`evolutionary-architectures/01` introduced this split; it matters enough to build out
fully here:

- **Incremental development** — writing software in small, reviewable, mergeable
  increments (a PR that changes one thing, not a thousand-file branch that diverges for
  three months).
- **Incremental deployment** — actually getting each of those increments into
  production, independently, without waiting to batch them into a big release.

Teams routinely do the first without the second: developers write small PRs, merge them
into a `main` branch — and then the *release* is still a quarterly, hand-orchestrated
event where months of merged-but-undeployed changes go out together. That's not
incremental deployment, no matter how small the individual commits were. The
architectural benefit of small changes (easy to review, easy to reason about, easy to
roll back) evaporates the moment fifty of them get bundled into one release, because now
if something breaks, you're debugging an interaction between fifty changes, not one.

### Why fitness functions need a pipeline to mean anything
A fitness function is only as useful as how often it runs and how quickly a failure gets
back to the person who caused it. A fitness function that runs once a quarter, right
before a big release, still catches the problem — but at that point, the offending
change might be three months old, its author has moved to different work, and
untangling *which* of the quarter's hundred changes caused the regression is its own
investigation. A fitness function wired into a fast, frequent pipeline catches the same
problem within minutes of the change that caused it, while the context is still fresh
and the diff is small enough to make the fix obvious.

This is why `evolutionary-architectures/01` treats incremental change and fitness
functions as inseparable pillars: fitness functions are the *governor*, but the pipeline
is the *engine* that makes the governor's feedback fast enough to be useful. Slow the
engine down and the governor becomes decorative.

## How it works

### Anatomy of a deployment pipeline
A typical pipeline is a sequence of stages, each a gate the change must pass:

```
commit -> build -> unit tests -> atomic fitness functions -> package/artifact
       -> deploy to staging -> holistic/integration fitness functions
       -> (manual approval, if needed) -> deploy to production
       -> continual fitness functions (monitoring, alerting)
```

Key properties that make this a *deployment pipeline* rather than just "a CI script":
- **Stages are ordered by cost and feedback speed.** Cheap, fast checks (compile, unit
  tests, atomic static-analysis fitness functions) run first and fail fast, so a
  developer gets feedback in seconds/minutes, not after a slow end-to-end suite has
  ground through 40 minutes of setup. Expensive checks (holistic integration tests,
  performance/load tests) run later, only once the cheap gates have already passed —
  no point running a 30-minute load test against code that doesn't even compile.
- **Every stage is a fitness function or contains one.** Unit tests are functional
  fitness functions; the atomic-check stage runs architectural fitness functions
  (`evolutionary-architectures/02`, `/03`); the staging deploy plus integration tests
  can host holistic fitness functions; production monitoring is where continual fitness
  functions live.
- **A failure at any stage stops the pipeline** — the change does not reach the next
  stage, let alone production, until it's fixed. This is what makes "guided" real: the
  gate has teeth.

### Worked example: what changes when a pipeline goes from slow/manual to fast/automated
Team A ships a payments feature with a manual QA pass and a quarterly release train.
Team B ships the same kind of feature with a pipeline that runs unit tests, an atomic
dependency-direction fitness function, and a staging smoke test automatically on every
merge, deploying to production within the hour if everything passes.

| | Team A (manual, quarterly) | Team B (automated, hourly) |
|---|---|---|
| Time from bug introduced to caught | up to 3 months | minutes to hours |
| Batch size when something breaks | ~quarter's worth of changes | 1 change |
| Cost to diagnose a regression | high — many candidate causes | low — one obvious diff |
| Cost of a single bad release | very high (whole quarter blocked/rolled back) | low (one small change reverted) |
| Team's appetite for architectural refactoring | low (any change is scary — blast radius unknown) | higher (blast radius is one small, verified change) |

The last row is the crux of why this lesson belongs in an evolutionary-architecture
subject at all: Team A's engineers rationally become *risk-averse* about architectural
change, because the cost of getting something wrong is enormous and the feedback loop is
too slow to catch it early. That risk-aversion is exactly what prevents the incremental,
guided change that evolutionary architecture depends on. Team B's fast, reliable
pipeline is what makes "let's try this architectural improvement in small steps and
verify each one" a viable, low-stress way of working instead of a leap of faith.

### Worked example: wiring a specific fitness function into a specific stage
Take the performance-budget fitness function from `evolutionary-architectures/02`
("checkout API must respond in under 300ms at p95 under 500 req/s"). Placing it in the
pipeline:

- **Not at the unit-test stage** — it needs a running, deployed instance to load-test
  against; a unit test can't measure real network/DB latency.
- **At the staging-deploy stage**, after the build and unit tests pass (no point running
  an expensive load test against code that's already broken at the unit level) — the
  pipeline deploys the candidate build to a staging environment sized similarly to
  production, then runs the load-test fitness function against it.
- **Gate**: if p95 exceeds 300ms, the pipeline halts before promoting to production; the
  developer sees the failure attached to their specific change within the same CI run
  that built it.
- **Complementary continual check**: even after this gate passes, a production APM alert
  (a continual fitness function, per `evolutionary-architectures/03`) keeps watching
  live p95 latency, because staging load characteristics never perfectly match
  production (different data volume, different traffic mix, cache warmth, etc.) — the
  pipeline gate reduces risk, it doesn't eliminate the need for production observability.

### Why "fast" is a precondition, not an optimization
It's tempting to treat pipeline speed as a developer-experience nicety ("nice to have
CI run in 5 minutes instead of 45"). In the evolutionary-architecture framing, speed is
structural:
- A slow pipeline means fewer deploys per day, which means larger batches per deploy,
  which reintroduces exactly the large-blast-radius risk that incremental deployment is
  supposed to eliminate.
- A slow pipeline means fitness-function feedback arrives late, when the context is
  stale and the fix is expensive — undermining the entire "guided" half of the
  definition, per the earlier discussion.
- Slow, unreliable (flaky) pipelines train developers to distrust and route around
  gates ("just rerun it, it's probably flaky") — which quietly disables the fitness
  functions riding on top of them, even though the pipeline nominally still exists.

## Pros
- Turns fitness functions from a theoretical gate into an actually-enforced one, running
  frequently enough to catch drift while it's cheap to fix.
- Shrinks blast radius per change, which lowers the perceived and actual risk of making
  architectural improvements — a virtuous cycle that encourages more incremental
  evolution rather than deferred, risky big-bang rewrites.
- Produces a fast, tight feedback loop that keeps context fresh for the person who
  introduced a regression.
- Forces explicit ordering of checks by cost, which naturally optimizes developer wait
  time without sacrificing thoroughness.

## Cons
- Building and maintaining a fast, reliable pipeline is significant, ongoing engineering
  investment — infrastructure, test-suite health, environment parity between
  staging/production.
- Flaky pipelines are worse than no pipeline in one specific way: they train engineers to
  distrust and bypass gates, silently disabling the fitness functions riding on them.
- Some fitness functions (large load tests, security audits) are inherently slow or
  costly and resist being squeezed into a fast per-commit loop — needs careful staging
  (see the "triggered" discussion in `evolutionary-architectures/03`).
- Pipeline infrastructure itself becomes a critical piece of architecture that needs its
  own maintenance and ownership, which is easy to under-resource.

## Alternatives
- **Manual QA gate with a release train** — a human test pass before a scheduled release.
  Differs by trading speed and frequency for (arguably) deeper human judgment on complex
  scenarios; can still coexist with an automated pipeline as one additional gate for
  high-risk changes, but shouldn't be the *only* gate if incremental evolution is a goal.
- **Feature flags with continuous deployment and no formal "pipeline" stages** — ship
  everything to production behind flags, verify with real traffic. Differs by moving
  more verification into production itself; works well combined with a pipeline (flags
  reduce the blast radius of a bad merge further) but isn't a substitute for pre-
  production automated checks like fitness functions and unit tests.
- **Canary/progressive delivery** — deploy to a small percentage of production traffic
  first, expand gradually based on live metrics. Differs by treating "deploy" itself as
  incremental, not just "the change that gets deployed"; a natural complement to a fast
  pipeline, not a replacement for one — you still want fitness functions to catch
  problems *before* even a canary sees them.

## When to use it
- Any system pursuing evolutionary architecture at all — per `evolutionary-
  architectures/01`, incremental deployment is one of the three non-negotiable pillars,
  not an optional enhancement.
- Especially valuable where the cost of a slow feedback loop is visibly compounding
  (long-lived branches, painful merges, "big scary release" culture).

## When NOT to use it
- A genuinely short-lived, low-risk, single-developer prototype may not justify the
  investment in pipeline infrastructure — the payoff period is longer than the
  project's lifespan.
- Regulatory contexts that mandate a slow, audited manual release process for specific
  artifact classes (e.g., certain medical-device firmware) may not be able to fully
  automate deployment — but even there, automating the *fitness-function checks*
  upstream of the mandated manual gate still shrinks blast radius and should not be
  skipped just because the final release step is manual.

## Key takeaways / mental model
Think of the deployment pipeline as the nervous system connecting a change to its
consequences: the faster and more reliable that connection, the sooner a developer feels
the "fitness function said no" signal and the cheaper it is to respond. A fitness
function without a fast pipeline is like a smoke detector with a dead battery — it
exists, but it isn't actually protecting anything in practice. Incremental deployment
isn't about moving fast for its own sake; it's about keeping the feedback loop short
enough that "guided, incremental change" is something the team can actually sustain,
rather than an aspiration undone by a quarterly release train.

## Self-check questions
1. Explain the difference between incremental development and incremental deployment,
   and why having only the first doesn't give you evolutionary architecture.
2. Why does pipeline *speed* matter architecturally, not just as a developer-experience
   concern?
3. Walk through where you'd place a load-test fitness function in a pipeline, and
   justify the ordering relative to unit tests and static-analysis checks.
4. What's the risk of a flaky pipeline beyond "developers get annoyed"? How does it
   specifically undermine fitness functions?
5. Give an example of a fitness function that's hard to fit into a fast per-commit loop,
   and describe how you'd stage it instead.

## References
- *Building Evolutionary Architectures*, 2nd ed. (Ford, Parsons, Kua, Sadalage,
  O'Reilly 2022), Chapter 4: Engineering Incremental Change
- `evolutionary-architectures/02` (fitness functions) and `/03` (fitness function
  categories) — the pipeline is where triggered fitness functions actually execute.
