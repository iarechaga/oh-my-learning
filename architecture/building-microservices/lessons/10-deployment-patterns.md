---
id: building-microservices/10
subject: building-microservices
title: "Deployment: Containers, Orchestration, and Patterns"
slug: deployment-patterns
status: drafted
mastery: 
seniority: senior
source: "Building Microservices, 2nd ed. (Sam Newman), Chapter 9"
prerequisites: [building-microservices/09]
created: 2026-08-10
updated: 2026-08-10
---

# Deployment: Containers, Orchestration, and Patterns

## TL;DR
Containers are the standard unit of deployment for microservices — a lightweight, immutable, self-contained package of a service and its dependencies. An orchestration platform (in the shape of Kubernetes) handles scheduling containers onto machines, service discovery, and self-healing at scale. On top of that infrastructure, deployment *patterns* — blue-green, canary, rolling — control how a new version actually gets rolled out to traffic, trading off release speed against blast-radius control.

## The idea
Lesson 09 got a service to a versioned, immutable artifact. This lesson is about what happens next: getting that artifact running, reliably, at whatever scale is needed, and rolling out new versions without taking the service down or exposing every user to a bad release at once.

Before containers, deploying a service commonly meant provisioning a whole virtual machine (or worse, a physical machine) per service instance — slow to provision, heavyweight, and prone to "works on my machine" drift between environments because the VM's OS, libraries, and config could differ subtly from what was tested. **Containers** solve this by packaging a service together with everything it needs to run (its runtime, libraries, and configuration) into a single lightweight, immutable image that runs identically wherever a container runtime is available — a developer's laptop, a CI runner, or a production cluster. This directly supports the immutable-artifact discipline from Lesson 09: the exact container image validated in CI is the exact image that runs in production.

Once you have many services, each potentially running many container instances for scale and redundancy, someone or something needs to decide which physical machines run which containers, restart containers that crash, route traffic to healthy instances, and scale instance counts up or down with load. That's the job of an **orchestration platform** — Kubernetes is the dominant one in practice, and its core concepts are worth understanding even in the abstract, because most orchestration platforms converge on similar ideas.

## How it works

### Containers: the deployment unit

A container image bundles: the service's compiled/packaged code, its runtime (e.g., a JVM, a Node.js runtime, a Python interpreter), its library dependencies, and configuration defaults — built once (Lesson 09) as an immutable, versioned artifact (e.g., `payment-service:2.4.0`). A container is a running instance of that image: an isolated process (using OS-level isolation — namespaces and cgroups on Linux) with its own filesystem view, network interface, and resource limits, but sharing the host machine's kernel (unlike a full virtual machine, which virtualizes hardware and runs its own kernel). This makes containers dramatically lighter-weight to start (seconds, not minutes) and denser to pack onto a machine (many containers per host vs. one OS per VM) than VMs, while still giving each service strong isolation from its neighbors' dependencies and file systems.

### Orchestration: scheduling, service discovery, self-healing

At the scale of dozens or hundreds of services, each with multiple instances for redundancy and load, manually deciding "which machine runs which container" and "what happens when a container crashes" doesn't scale. An orchestration platform automates this. The core concepts (using Kubernetes-shaped vocabulary, since it's the dominant real-world implementation, but the concepts generalize):

- **Scheduling** — you declare *what* you want running (e.g., "run 4 instances of `payment-service:2.4.0`, each needing 512MB memory and 0.5 CPU") and the orchestrator decides *where* — which physical/virtual machines in the cluster have the capacity — and places the containers there, without a human manually picking machines.
- **Service discovery** — as containers are scheduled, rescheduled (e.g., after a crash), or scaled up/down, their network locations (IP addresses) change constantly. Service discovery gives every service a stable name (e.g., `payment-service`) that resolves to whichever healthy instances currently exist, so calling services never need to track individual container IPs directly — they call the stable name, and the orchestrator's internal load balancing/DNS routes the request to a live instance.
- **Self-healing** — the orchestrator continuously compares the *desired state* you declared ("4 healthy instances of `payment-service`") against the *actual state* it observes (via health checks). If a container crashes, becomes unresponsive, or its host machine dies, the orchestrator automatically schedules a replacement elsewhere to restore the desired count, without a human paging in to do it manually. This is a meaningful operational shift: engineers declare intent, and the platform continuously works to maintain it, rather than engineers imperatively reacting to every failure.

### Deployment patterns: how a new version reaches traffic

Getting a new container image built and schedulable is only half the problem — you also need a strategy for how traffic transitions from the old version to the new one. Three common patterns, each trading off release speed, resource cost, and blast-radius control differently:

**Rolling deployment.** Replace old instances with new ones incrementally, a few at a time, while the service keeps serving traffic throughout. E.g., with 10 instances of `payment-service` v2.3 running, the orchestrator brings up 2 instances of v2.4, waits for them to pass health checks, then terminates 2 instances of v2.3, and repeats until all 10 are v2.4. At every point during the rollout, *both* versions are simultaneously serving live traffic to different requests. This is resource-efficient (never need double the total capacity) and is the default strategy most orchestrators use out of the box, but it means a bug in the new version is immediately exposed to some fraction of real users as soon as the rollout starts, and a mid-rollout mix of two versions serving traffic simultaneously must be something your API/data contracts can tolerate (see Lesson 12 on why backward compatibility matters here).

**Blue-green deployment.** Run two complete, identically-sized environments — "blue" (the current live version) and "green" (the new version) — side by side, with green receiving no live traffic initially. Once green is deployed and verified (smoke tests, health checks), traffic is switched from blue to green all at once, typically at a router or load-balancer level. If something's wrong, you switch back to blue instantly, since it's still fully running and untouched. The cost: you need double the infrastructure capacity during the transition (both blue and green fully provisioned at once), and the cutover — while instant to revert — still exposes 100% of traffic to the new version the moment you flip, with no gradual exposure ramp.

**Canary deployment.** Deploy the new version to a small subset of infrastructure and route only a small percentage of real traffic to it (e.g., 5%), while the vast majority continues to hit the old version. Monitor the canary's error rates, latency, and business metrics closely; if it looks healthy, gradually increase the percentage of traffic routed to it (5% → 25% → 100%) over time; if it looks unhealthy, route traffic away from it immediately and investigate, having limited the blast radius to a small slice of real users throughout. Canary gives the most gradual, most tightly-controlled exposure of the three, at the cost of the most operational complexity — you need traffic-splitting infrastructure and enough monitoring signal to make a confident "promote or roll back" decision at each step, and a canary rollout takes longer end-to-end than a rolling or blue-green deploy.

### Worked example: comparing the three for a risky release

`payment-service` is shipping a change to its retry logic for a downstream card-processor call — a genuinely risky change, since a bug could mean double-charging customers or silently failing authorizations.

- **Rolling:** as instances update, some fraction of *all* payment traffic hits the new logic immediately, with no way to control which customers see it first or limit exposure below "roughly the fraction of instances updated so far." If the bug is bad, real customers are affected before a human necessarily notices.
- **Blue-green:** the team fully validates green in a pre-production-like state, then flips 100% of traffic in one action. If the bug slips through validation and only shows up under real production load, 100% of live payment traffic is instantly exposed the moment green goes live — the instant rollback capability is valuable, but doesn't prevent the initial full-traffic exposure.
- **Canary:** the team routes 2% of real payment traffic to the new version, watches authorization success rate and refund/dispute signals closely for an hour, and only ramps to 10%, then 50%, then 100% as confidence builds at each step. If the retry bug causes a measurable dip in authorization success at 2%, it's caught while affecting a small, bounded slice of transactions, and traffic is routed back to the old version immediately.

For a change this risky, canary is the strongest fit precisely because it bounds the blast radius during the riskiest, least-proven window of the rollout — for a low-risk change (a copy tweak in a non-critical service), the operational overhead of canary may not be worth it, and rolling deployment is perfectly adequate.

## Pros
- **Containers**: consistent, immutable, portable deployment unit; fast startup; efficient density versus VMs; strong per-service isolation.
- **Orchestration**: automates scheduling, service discovery, and failure recovery at scale, freeing engineers from manual machine-by-machine operations.
- **Rolling**: resource-efficient, works out of the box on most platforms, no downtime.
- **Blue-green**: instant, reliable rollback (the old environment is untouched and ready).
- **Canary**: tightest blast-radius control, real production signal before full exposure.

## Cons
- **Containers/orchestration**: real operational learning curve and infrastructure to run and maintain (the orchestrator itself is a critical, complex piece of infrastructure).
- **Rolling**: exposes some live traffic to the new version immediately with no control over how much or which users, and requires the API/data layer to tolerate two versions running simultaneously.
- **Blue-green**: doubles infrastructure cost during the transition window; the cutover itself is still all-or-nothing exposure.
- **Canary**: the most operationally complex of the three (needs traffic splitting and strong monitoring signal); slowest to reach full rollout.

## Alternatives
- **Feature flags as a complement, not a replacement** — deploying new code is a separate concern from exposing new *behavior*; a feature flag lets you deploy a new version fully (via any of the three patterns) while keeping the new behavior dark, then turn it on gradually or instantly independent of the deployment mechanism. Often combined with canary or rolling deployments for even finer-grained control.
- **Serverless/function-as-a-service platforms** — for some workloads, skip container orchestration entirely and let a managed platform (e.g., AWS Lambda-style) handle scaling and scheduling transparently; trades operational control and some latency/cold-start characteristics for significantly less infrastructure to own, appropriate for certain service shapes (event-driven, spiky, stateless) more than others.

## When to use it
- Containers and orchestration: the default for any microservices system of meaningful scale — dozens of services, many instances each, needing consistent packaging and automated scheduling/recovery.
- Rolling deployment: the default for most routine, low-to-medium risk releases.
- Blue-green: when instant, guaranteed rollback matters more than infrastructure cost, and the change is well-validated pre-release.
- Canary: for high-risk changes (payment logic, core business rules, anything with real customer/financial impact) where bounding blast radius during rollout is worth the operational complexity.

## When NOT to use it
- Don't reach for full container orchestration for a tiny system (one or two services, low scale) — the operational overhead of running and learning an orchestrator can exceed the entire rest of the system's complexity; a simpler deployment approach (even a couple of VMs with a basic deploy script) may be entirely adequate until scale demands otherwise.
- Don't use blue-green for changes with any risk of incompatible data/schema side effects between old and new versions — since both environments may briefly need to handle in-flight requests or shared state during cutover, a schema change that isn't backward-compatible can break the rollback path itself.
- Don't skip canary for genuinely high-stakes changes just because rolling deployment is the default and "usually fine" — the cost of a canary process is much smaller than the cost of a bad release fully exposed to all traffic.

## Key takeaways / mental model
Containers give you a consistent, immutable unit to deploy; orchestration automates getting that unit running, discoverable, and self-healing at scale, so engineers declare desired state rather than manually managing machines. On top of that foundation, the deployment *pattern* you choose (rolling, blue-green, canary) is really a decision about how much you trust the release and how tightly you want to bound the blast radius while that trust is still being earned — rolling for routine changes, blue-green when instant full rollback matters most, canary when you need to prove a risky change is safe on a small slice of real traffic before it reaches everyone.

## Self-check questions
1. What specific problem does an orchestration platform's "self-healing" behavior solve, and how does it differ from an engineer manually restarting a crashed process?
2. Why does a rolling deployment require your API/data contracts to tolerate two versions of a service running simultaneously, and what could go wrong if they can't (hint: connect this to Lesson 12)?
3. For a high-stakes payment-logic change, walk through why canary deployment bounds risk more effectively than blue-green, even though blue-green offers instant rollback.
4. What's the relationship between a feature flag and a deployment pattern like canary — why are they complementary rather than substitutes for each other?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 9: "Deployment"
