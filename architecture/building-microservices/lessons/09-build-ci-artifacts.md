---
id: building-microservices/09
subject: building-microservices
title: "Build, CI, and Artifact Management"
slug: build-ci-artifacts
status: drafted
mastery: 
seniority: mid
source: "Building Microservices, 2nd ed. (Sam Newman), Chapter 8"
prerequisites: [building-microservices/01]
created: 2026-08-10
updated: 2026-08-10
---

# Build, CI, and Artifact Management

## TL;DR
Each microservice needs its own independent build pipeline producing its own independently versioned, immutable artifact — never a single monolithic build that compiles, tests, and packages every service together. A shared build defeats the entire point of independent deployability: if changing one service still requires rebuilding and re-validating every other service before anything can ship, you haven't actually decoupled their releases.

## The idea
Lesson 01 defined independent deployability as the core property of a microservice. This lesson is about the concrete build/CI mechanics that either deliver on that promise or quietly undermine it. It's easy to draw clean service boundaries (Lessons 02-03) and still end up with a system that can't actually deploy services independently, because the *build* process ties them together — a single repository with a single build script that compiles, tests, and packages all services as one unit whenever anything changes.

**The one-giant-build anti-pattern.** Imagine ten services live in one repository with one CI pipeline: any commit triggers a build that compiles all ten, runs the full test suite for all ten, and produces ten new artifact versions together, tagged with the same build number. Even though the ten services are logically separate deployables, in practice you cannot ship a fix to Service 3 without waiting on the build (and any flaky test) for Services 1, 2, and 4-10 too. The team has recreated the monolith's release-train problem inside a "microservices" repo — this is deployment coupling (Lesson 03) introduced at the build layer rather than the runtime layer.

The fix Newman recommends: **one pipeline per service**, triggered only by changes to that service, producing one independently versioned artifact for that service, and nothing else. A change to `payment-service` should never trigger a rebuild, retest, or new artifact version for `inventory-service`.

## How it works

### Per-service pipelines

Each service gets its own CI pipeline (regardless of whether services live in separate repositories or a single "monorepo" with per-directory pipeline triggers — the repository layout is a separate decision from the pipeline independence this lesson is about). The pipeline for `payment-service`:
1. Triggers only on changes within `payment-service`'s own code path.
2. Runs `payment-service`'s own unit and integration tests (Lesson 11) — not any other service's tests.
3. Builds `payment-service`'s own artifact (a container image, typically) and pushes it to an artifact repository with its own version number.
4. Optionally triggers `payment-service`'s own deployment pipeline (Lesson 10) — again, independent of any other service's deploy.

If `inventory-service`'s code changes, only `inventory-service`'s pipeline runs — `payment-service`'s pipeline is untouched, and no new `payment-service` artifact is produced. This is what makes "release `payment-service` today, leave `inventory-service` at its current version" a normal, cheap, everyday operation rather than something requiring careful coordination.

### Artifact versioning and immutability

Every build produces one **immutable artifact** — typically a container image tagged with a unique version (a semantic version, a git SHA, or a monotonically increasing build number) — that, once built, is never mutated. The same artifact that passed CI and was validated in a staging environment is the *exact same bytes* deployed to production, never rebuilt or "touched up" along the way.

Why this matters concretely: if you rebuild an artifact between staging validation and production deployment (even from the "same" source code, using a build step that isn't perfectly reproducible — differing dependency resolution, base image drift, non-pinned versions), you can no longer be certain the thing you tested is the thing you're running. Immutability closes this gap: build once, tag it, promote that exact artifact through every environment (staging → production), never rebuild mid-pipeline.

Versioning discipline also matters for dependency management between services and for rollback: if `order-service` calls `payment-service` v2.3.1 and a deploy of `payment-service` v2.4.0 introduces a regression, being able to identify precisely which immutable artifact was running before, and redeploy exactly that artifact, is what makes rollback fast and safe (versus trying to rebuild "the old version" from source and hoping it comes out identical).

### Worked example: the release-train problem, before and after

**Before (monolithic build):** A 12-service system shares one repository and one Jenkins pipeline. A developer fixes a one-line bug in `notification-service`. To ship it, the full pipeline runs: compiling all 12 services (8 minutes), running the combined test suite for all 12 (35 minutes, and one flaky integration test in `reporting-service` fails intermittently, requiring a re-run), then building and versioning all 12 artifacts together under one release number. The one-line fix takes the better part of an hour to ship, and its release is at the mercy of every other service's test suite that day — a completely unrelated flaky test in `reporting-service` blocks `notification-service`'s fix from shipping.

**After (per-service pipelines):** `notification-service` has its own pipeline. The same one-line fix triggers only `notification-service`'s build: compile (30 seconds), run `notification-service`'s own test suite (90 seconds), build and push a new immutable artifact tagged `notification-service:1.14.2`. Total time: under three minutes, entirely unaffected by anything happening in `reporting-service` or any of the other ten services. This is independent deployability actually realized at the build layer, not just claimed at the architecture-diagram layer.

### Repository layout is a separate question from pipeline independence

A common point of confusion: "monorepo vs. many repos" is not the same decision as "one build vs. many builds." You can have all services in a single monorepo *and* still have fully independent per-service pipelines, as long as the CI system is configured to trigger builds based on which paths within the repo changed (most modern CI systems — GitHub Actions, GitLab CI, Bazel-based build systems — support this directly). Conversely, you can have services split across many separate repositories and still accidentally couple their builds (e.g., a shared build script invoked identically by every repo's pipeline that happens to also rebuild a shared library every time, or a shared CI "release day" process that batches releases together). The property that actually matters is **pipeline independence** — whether a change to Service A can be built, tested, versioned, and released without touching Service B's pipeline — not which repository layout you chose.

## Pros
- **Preserves real independent deployability at the build layer**, not just the architecture-diagram layer — this is the whole point of Lesson 01's promise.
- **Fast, focused feedback** — a developer working on one service gets a CI result scoped to their own change in minutes, not tied to the health of every other service's test suite.
- **Clear, traceable versioning** — each service's history of exactly what was deployed when is independently trackable, and rollback means redeploying a known-good immutable artifact, not rebuilding from source and hoping.

## Cons
- **More pipelines to build, configure, and maintain** — N services means N pipeline configurations (though this is usually mitigated with shared pipeline templates/tooling, as long as the templates don't reintroduce coupling by batching builds together).
- **Cross-service changes (e.g., an API contract change touching both a provider and its consumer) require coordinating two independent pipelines/releases**, which needs deliberate practice (e.g., consumer-driven contracts, Lesson 12, and backward-compatible rollout ordering) rather than relying on a shared build to catch the mismatch for you.
- **Shared libraries need their own careful versioning discipline** — a shared internal library used by several services' builds can quietly reintroduce coupling if all consumers are forced to upgrade in lockstep; keep such libraries small, stable, and independently versioned (semantic versioning with real backward-compatibility discipline).

## Alternatives
- **Monolithic/shared build for a genuinely small number of tightly-coupled services** — occasionally acceptable early in a system's life when there are only two or three services that in practice always change together, but should be treated as a stepping stone with an explicit plan to split, not a permanent choice, since it silently reintroduces deployment coupling (Lesson 03) as the system grows.
- **Trunk-based development with feature flags across services** — doesn't replace per-service pipelines, but is a common complementary practice: keep every service's `main` branch always releasable, and use feature flags to control the visibility of in-progress cross-service features, rather than long-lived feature branches that need coordinated merges.

## When to use it
- Always, as the default for any system with more than a couple of independently-owned services — per-service pipelines and independently versioned, immutable artifacts are foundational, not optional, infrastructure for a microservices architecture.

## When NOT to use it
- A very small number of services (two or three) that are, in practice, always changed and released together by the same team, where the overhead of fully separate pipelines doesn't yet pay for itself — but treat this as temporary, and revisit it as soon as the services' release cadences start to diverge or a second team gets involved (Lesson 17).

## Key takeaways / mental model
Independent deployability is not just an architecture property — it has to be built into the pipeline, or it doesn't actually exist. One service, one pipeline, one independently versioned and immutable artifact, triggered only by changes to that service. Ask, for any proposed build setup: "can I ship a one-line fix to Service X today without touching or waiting on any other service's build?" If the answer is no, the build — not the architecture — is where the coupling lives.

## Self-check questions
1. A team has ten services in ten separate git repositories, but a single shared CI script rebuilds and re-versions all ten together on every merge. Have they achieved independent deployability? Why or why not?
2. Why does artifact immutability (never rebuilding between staging and production) matter for confidence in what's actually running in production?
3. Explain why "monorepo vs. many repos" and "one pipeline vs. many pipelines" are separate decisions, and give an example of a monorepo setup that still achieves fully independent per-service pipelines.
4. A shared internal library is used by six of your twelve services' builds, and a change to it requires all six to bump their dependency and redeploy together. What coupling problem does this recreate, and what's the standard mitigation?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 8: "Deployment" (build and CI/CD pipeline discussion)
