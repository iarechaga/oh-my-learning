---
id: accelerate/05
subject: accelerate
title: Continuous delivery foundations and small-batch flow
slug: continuous-delivery-foundations
status: drafted
mastery:
seniority: senior
source: Accelerate (Forsgren, Humble, Kim), Chapter 4 "Technical Practices"
prerequisites: [accelerate/02, accelerate/03, accelerate/04]
created: 2026-08-10
updated: 2026-08-10
---

# Continuous delivery foundations and small-batch flow

## TL;DR
Continuous delivery (CD) is the technical practice cluster the research found to be the single strongest predictor of the four key metrics: it means keeping the codebase always in a releasable state, through comprehensive automated testing, trunk-based development, and deployment automation — so releasing is a routine, low-risk, on-demand decision, not a risky event.

## The idea
The book asks: what specific, adoptable practices actually cause the improvements in deployment frequency, lead time, change failure rate, and MTTR (`accelerate/03`, `accelerate/04`)? Continuous delivery is the answer the data points to most strongly. Continuous delivery, as defined here (following Humble and Farley's earlier book *Continuous Delivery*), is not "we have a CI server" or "we deploy often" — it's a *capability*: the codebase is kept in a state where it *could* be deployed to production at any time, because every change that merges passes through a fully automated build-and-test pipeline that gives fast, reliable feedback on whether it's safe to release.

This reframes releasing from "an event we prepare for" to "a decision we can make at any moment because the system is always ready." That shift is what makes small-batch flow (`accelerate/03`) practically achievable — you cannot deploy many times a day if getting to a releasable state requires a multi-day manual stabilization effort each time.

## How it works

### The core practices that constitute continuous delivery
The book's statistical model identifies several practices that, together, predict CD capability and, through it, the four key metrics:

1. **Comprehensive automated testing** (detailed further in `accelerate/07`) — a suite the team trusts enough to make a ship/no-ship decision from, without manual regression testing as a gate.
2. **Trunk-based development with short-lived branches** — developers integrate to a shared mainline frequently (at least daily), rather than working in long-lived feature branches that diverge for weeks and merge in one large, risky integration. This is one of the more counter-intuitive findings for teams used to GitFlow-style long-lived branches: the data shows shorter branch lifetimes and fewer active branches correlate with higher delivery performance.
3. **Deployment automation** — the process of getting a build into production is a scripted, repeatable, push-button (or fully automatic) pipeline, not a runbook of manual steps a human executes under pressure.
4. **Continuous integration** — every merge triggers an automated build and test run against the full codebase, so integration problems surface within minutes, not weeks later during a "merge day."
5. **Trunk stays releasable** — the team treats a broken build on trunk as a stop-the-line event to fix immediately, rather than something that can linger while other work continues on top of it.

### Worked example — the cost of a broken continuous delivery discipline
Consider a team with a CI server that runs tests on every commit, but where a red (failing) build is common and tolerated — "oh, that test is flaky, ignore it" is a routine comment in code review. Over time, the team accumulates a set of known-flaky or known-broken tests that everyone has learned to ignore. The build is "passing" in name but has stopped functioning as a genuine gate. When a real regression lands, it's buried among the noise of expected failures and ships to production anyway. This team has CI *infrastructure* but not CD *capability* — the distinction the book insists on. Fixing it requires treating every red build as a stop-the-line signal (a lean manufacturing practice discussed further in `accelerate/09`), which is an organizational discipline change, not a tooling change.

### Worked example — trunk-based development vs. long-lived branches
Team X uses long-lived feature branches: each feature branch lives for 3-4 weeks before merging to main. By the time of the merge, main has drifted significantly, producing large, painful merge conflicts and a burst of integration bugs that require days of stabilization — exactly the large-batch dynamic from `accelerate/03` and `accelerate/04`, except the "batch" here is a branch's divergence rather than a release. Team Y practices trunk-based development: every developer merges to main at least once a day, behind feature flags if the feature isn't ready for users yet. Integration problems are caught within hours, in small increments, while the context is still fresh in the author's mind. Team Y's change failure rate and lead time both benefit from the same batch-size mechanism explored in earlier lessons, just applied to the unit of "code integration" rather than "deployment."

### The distinction: continuous delivery vs. continuous deployment
The book is careful to separate these: **continuous delivery** means every change is automatically verified as production-ready and *could* be deployed on demand — a human (or business decision) still chooses when to actually release it. **Continuous deployment** goes one step further: every change that passes the pipeline is deployed automatically, with no manual gate at all. Continuous deployment is not required to get the delivery performance benefits the research measures — many elite performers practice continuous delivery with a manual "go" decision (e.g., for business/compliance reasons) while still deploying many times a day, because the manual decision itself is fast and cheap, not a multi-day stabilization process.

## Pros
- Strongest single predictor in the research of the four key metrics — the highest-leverage investment for an organization trying to move from Low/Medium to High/Elite performance.
- Converts releasing from a high-stakes, anxiety-inducing event into a routine, boring, frequent action — which itself reduces the fear-driven behaviors (over-cautious change review, infrequent releases) that create large batches in the first place.
- Trunk-based development, once adopted, tends to simplify a team's entire branching and merge strategy, reducing process overhead beyond just the release pipeline.

## Cons
- Requires substantial up-front investment in test automation (`accelerate/07`) and deployment automation before it pays off — teams sometimes underestimate this cost and half-adopt CD, getting the risk of frequent releases without the safety net.
- Trunk-based development requires discipline (feature flags for incomplete work, small commits, fast CI feedback) that's a real behavior change for teams used to long-lived branches, and often meets resistance framed as "trunk-based development is unsafe."
- Legacy systems with tightly coupled architecture (see `accelerate/06`) can make true CD very difficult to achieve without first addressing the architecture — CD can't be bolted onto a system that structurally requires coordinated, big-bang releases across many components.

## Alternatives
- **GitFlow / long-lived feature branches** — the traditional alternative; provides isolation for in-progress work at the cost of larger, riskier integration events; the book's data argues against it as a default for teams optimizing for delivery performance.
- **Scheduled release trains (e.g., train leaves every two weeks regardless of readiness)** — a middle ground that gives more predictability than ad hoc releases without requiring full CD maturity, but doesn't get you to elite-tier lead time or deployment frequency.
- **Manual QA-gated releases** — relies on a dedicated QA phase/team rather than automated tests as the release gate; historically common, but the research associates heavy reliance on manual regression testing with worse, not better, delivery performance, because it caps how small and frequent batches can practically be.

## When to use it
Continuous delivery is the right target for essentially any team whose delivery performance needs to improve — it's the practice cluster with the strongest predictive weight in the research, so when in doubt about where to invest first, invest here (alongside the architectural prerequisites in `accelerate/06`).

## When NOT to use it
Don't attempt to adopt trunk-based development and high deploy frequency before the test automation (`accelerate/07`) that makes trunk-based development safe is in place — that ordering produces the fear of the "broken build is normal" failure mode from the worked example above, not the benefits. In genuinely high-stakes, tightly regulated release contexts (e.g., firmware for medical devices with mandatory external certification per release), full continuous deployment may not be achievable, but continuous *delivery* — always being release-ready, even if the actual release cadence is constrained externally — usually still is, and still pays off in reduced risk per release.

## Key takeaways / mental model
Continuous delivery is a *capability* — "we could release right now, safely" — not a specific tool or a deploy-frequency number. The practices that build this capability (automated testing, trunk-based development, deployment automation) all attack the same target: keep the gap between "code written" and "code verified as production-ready" as close to zero as possible, at all times, so releasing stops being a special event.

## Self-check questions
1. Explain the difference between "we have a CI server" and "we practice continuous delivery," using the flaky-test worked example. What organizational discipline, not tooling, does the difference come down to?
2. Why does the research associate long-lived feature branches with worse delivery performance, even though branches are meant to isolate risk? What's the trade-off trunk-based development makes instead?
3. Distinguish continuous delivery from continuous deployment. Can an elite performer (per the DORA clusters) practice continuous delivery without continuous deployment? Explain how.
4. A team with a tightly coupled, legacy monolith wants to adopt trunk-based development and CD next quarter. What would you tell them to check first, and why (hint: connect to `accelerate/06`)?

## References
- Accelerate: The Science of Lean Software and DevOps (Forsgren, Humble, Kim), Chapter 4: "Technical Practices".
- Continuous Delivery (Jez Humble, David Farley) — the foundational text this chapter builds on.
