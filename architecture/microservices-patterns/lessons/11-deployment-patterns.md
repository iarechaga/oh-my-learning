---
id: microservices-patterns/11
subject: microservices-patterns
title: "Deployment Patterns"
slug: deployment-patterns
status: drafted
mastery:
seniority: mid
source: "Microservices Patterns (Chris Richardson), Chapter 12"
prerequisites: [microservices-patterns/03]
created: 2026-07-01
updated: 2026-07-01
---

# Deployment Patterns

## TL;DR
Microservices only pay off when deployment is fast, reliable, and routine.
You need a repeatable way to package and run many service instances without dependency
conflicts, slow recovery, or risky releases.

There is a deployment ladder: language package on host -> VM -> container ->
orchestration -> serverless. Each step changes isolation, startup speed, cost, and
operational control. For many teams, service-per-container plus orchestration is the
best balance, with rolling, blue-green, and canary as release tools.

## The idea
In a monolith, deployment is one unit. In microservices, deployment is a fleet problem.
Every service needs packaging, runtime setup, health checks, scaling, and rollback.

That means deployment is an architecture concern, not only an ops concern. If the
deployment model is fragile, teams ship less often, incidents last longer, and service
independence becomes theory instead of reality.

The goal is to run each instance in a unit that is:

- isolated enough to avoid runtime conflicts,
- lightweight enough to run many instances,
- fast enough to replace during failures and releases,
- consistent enough that dev/stage/prod behave similarly.

The deployment mechanism is a spectrum with real trade-offs, not a single best answer.

## How it works

### 1) Language-specific packages on hosts
You build an artifact in the language ecosystem and install it on a machine:

- Java: JAR/WAR plus JVM.
- Node.js: app package plus node runtime.
- Python: wheel/source plus virtualenv.

This is the shortest path to production for a small system.

Strengths:

- simple workflow,
- low platform overhead,
- familiar debugging model.

Weaknesses at microservice scale:

- host drift (different machines, different behavior),
- dependency conflicts between services,
- weak isolation and noisy neighbors,
- slow, error-prone rollback when hosts are mutated over time.

This model is operationally cheap early and expensive later.

### 2) Service-as-a-VM
Each service instance runs in a dedicated VM image.

Benefits:

- strong isolation,
- clear security boundary,
- fewer runtime conflicts across services.

Trade-offs:

- heavier images,
- slower boot and replacement,
- lower density per host,
- more cost for many small services.

VM-per-service can be valid for strict compliance or legacy infra standards, but often
slows frequent releases and fast scaling.

### 3) Service-as-a-container (service-per-container)
This is where most microservice platforms land.

A container image packages app + runtime dependencies in an immutable artifact. The
runtime starts containers quickly on shared hosts with process-level isolation.

Typical flow:

1. Build image `ftgo-order-service:2.1.0`.
2. Push to image registry.
3. Platform starts containers from that image.
4. Upgrades happen by replacing containers with new image tags.

Why this is a sweet spot:

- better isolation than host packages,
- much lighter and faster than VM-per-service,
- consistent runtime from CI to production,
- clear deployment unit for automation.

### Worked example 1 - service-per-container pod with sidecar
FTGO deploys Order Service in Kubernetes as one app container plus one sidecar.

```text
Node
+----------------------------------------------------------------+
| Pod: order-service-7d4f8                                       |
|                                                                |
|  +--------------------------+   localhost   +----------------+ |
|  | app container            | <-----------> | sidecar proxy  | |
|  | image: ftgo/order:2.1.0  |               | image: envoy   | |
|  | port: 8080               |               | port: 15001    | |
|  | role: business logic     |               | role: mTLS,    | |
|  |                          |               | retries, traces| |
|  +--------------------------+               +----------------+ |
+----------------------------------------------------------------+

Ingress -> Service -> Pod -> sidecar policy -> app
Egress  -> app -> sidecar policy -> network
```

Result: app code stays focused on business behavior; transport/security policy is handled
by deployment-time components.

### 4) Orchestration (Kubernetes)
Containers package software. Orchestration runs fleets.

Kubernetes introduces a desired-state control loop that automates core operations:

1. Scheduling - place pods onto nodes from declared constraints.
2. Restart/self-healing - replace failed containers automatically.
3. Scaling - change replica counts manually or via autoscaling.
4. Service discovery - stable DNS/service abstraction over ephemeral pods.
5. Rollouts/rollback - controlled replacement and revision history.

This is the difference between "we can run containers" and "we can run microservices at
scale without manual heroics".

### Sidecar and service mesh as deployment-time cross-cutting control
The sidecar pattern (see `designing-distributed-systems/01`) deploys helper containers
next to app containers in the same pod-level unit.

Good sidecar use cases:

- mTLS and cert rotation,
- retries/timeouts/circuit rules,
- telemetry export,
- policy enforcement.

A service mesh generalizes this fleet-wide with a control plane and many sidecar proxies.

Why teams adopt mesh:

- consistent network policy across services,
- less duplicated resilience/security code,
- language-agnostic cross-cutting behavior.

Why teams delay mesh:

- extra moving parts,
- extra latency/resource overhead,
- harder troubleshooting.

### 5) Serverless deployment (FaaS)
In FaaS, you deploy functions, not long-lived service processes. The provider manages
servers and scales execution up/down automatically, often down to zero idle instances.

Benefits:

- minimal server management,
- strong fit for bursty event-driven tasks,
- pay mostly for invocation/runtime.

Constraints:

- cold starts,
- execution/runtime limits,
- less low-level control,
- possible provider lock-in.

A practical rule: if the workload is event-based, spiky, and stateless, FaaS is a good
candidate. If it is latency-sensitive and long-lived API traffic, containers are usually
a better fit.

### Release strategies: rolling, blue-green, canary
Once deployment units are defined, release strategy controls risk.

#### Rolling update
Gradually replace old pods with new pods while keeping service available.

- Efficient on resources.
- Default in Kubernetes deployments.
- Requires compatibility because versions coexist during rollout.

### Worked example 2 - readiness-gated rolling update with 6 replicas
FTGO Order Service runs 6 replicas. Config: `maxUnavailable=1`, `maxSurge=1`.

```text
Start:
  v1 ready=6, v2 ready=0

Cycle:
  1) create one v2 pod (surge)
  2) wait until readiness probe passes
  3) terminate one v1 pod (respect maxUnavailable=1)
  4) repeat

Progress snapshots:
  after first replacement: v1=5, v2=1, ready total=6
  midpoint:                v1=3, v2=3, ready total>=5
  end:                     v1=0, v2=6, ready total=6
```

Key point: readiness gates traffic. A new pod does not receive live requests until it is
proven healthy.

#### Blue-green deployment
Run two environments: Blue (current) and Green (new). Switch traffic in one cutover.

- Fast rollback by switching back.
- Cleaner pre-cutover validation.
- Higher temporary infrastructure cost.

#### Canary deployment
Route a small percentage to the new version first, then increase progressively.

- Limits blast radius.
- Uses real production behavior as proof.
- Needs strong metrics/alerting discipline.

### Worked example 3 - one release, blue-green vs canary
Release target: FTGO Order Service v2.1.0.

```text
Blue-Green path:
  Step 1: Blue(v2.0.4)=100%, Green(v2.1.0)=0%
  Step 2: Deploy and validate Green
  Step 3: Cut over to Green=100%
  Step 4: If errors spike, switch back to Blue immediately

Canary path:
  Step 1: stable 95%, canary 5%
  Step 2: hold and evaluate p95 latency, 5xx, conversion
  Step 3: increase to 25% if healthy
  Step 4: hold and evaluate again
  Step 5: promote to 100% or roll back to 0%
```

How to choose:

- choose blue-green when immediate fallback is critical and extra capacity is acceptable,
- choose canary when you want gradual confidence and measured blast radius.

## Pros
- Reproducible runtime via immutable images.
- Better isolation than package-on-host with lower weight than VM-per-service.
- Fast start and replacement, improving recovery and rollout speed.
- Declarative orchestration for scheduling, healing, and scaling.
- Well-understood release patterns for controlled change in production.
- Good team boundary: app teams ship features, platform teams operate runtime policies.

## Cons
- Platform complexity is real: networking, security, storage, and cluster operations.
- Teams must learn orchestration concepts and failure modes.
- Sidecar/mesh layers can increase latency and troubleshooting complexity.
- CI/CD and config discipline become mandatory, not optional.
- Costs rise if environments are overprovisioned or always-on.

## Alternatives
- **VM-per-service** - strongest isolation and familiar ops in some enterprises, but
  heavier startup, lower density, and slower rollout cadence.
- **Language-package-on-host** - simplest to start (JAR/WAR/npm/virtualenv on a host),
  but weakest isolation and most prone to host drift and dependency conflicts.
- **Serverless/FaaS** - excellent for bursty event-driven workloads with scale-to-zero,
  but constrained runtime model and less control for long-lived low-latency services.
- **PaaS** - managed deployment experience with lower operational burden, but potentially
  less control/flexibility than running your own orchestrated container platform.

## When to use it
Use container + orchestration as your default when you run multiple independently
deployable services, release frequently, and need predictable scaling/recovery behavior.

It is especially strong for long-lived API services with strict uptime goals and teams
that want explicit rollout control (readiness gates, progressive rollout, rollback).

## When NOT to use it
Do not default to a full orchestrated platform for very small systems with low release
frequency. The operational overhead can exceed the benefit.

Also avoid forcing containers when the workload is pure bursty event handling (FaaS may
be better), or when strict isolation rules require VM boundaries.

## Key takeaways / mental model
Keep this model in your head:

1. Deployment is a trade-off ladder, not a binary choice.
2. Isolation and control increase as you move up, but so does platform complexity.
3. Containers + orchestration are the common middle ground for long-lived microservices.
4. Release strategy is part of architecture: rolling for efficiency, blue-green for fast
   fallback, canary for controlled exposure.
5. Sidecars/mesh are tools for cross-cutting concerns, not mandatory from day one.

## Self-check questions
1. Your services run as language packages on shared hosts and often fail after runtime
   upgrades. Which ladder step would you choose next, and what failure class does it fix?
2. In a rolling update of 6 replicas with `maxUnavailable=1`, what availability behavior
   do you expect, and why are readiness probes non-negotiable?
3. You must release a risky pricing change for FTGO. Would you pick blue-green or canary
   first, and what metrics would decide promotion or rollback?
4. Your team wants service mesh for mTLS and retries. What scale/pain signals justify
   mesh adoption, and what debugging complexity should you expect afterward?
5. A workload is idle most of the day, then spikes 30x for 10 minutes. Compare
   containerized service and FaaS on cost, latency behavior, and operational control.
6. A team says, "We containerized everything, so deployment is solved." What orchestrator
   and release responsibilities are still missing from that statement?

## References
- Microservices Patterns (Chris Richardson), Chapter 12: "Deploying microservices"
- [designing-distributed-systems/01 - Why Distributed Patterns](../../designing-distributed-systems/lessons/01-why-distributed-patterns.md)
- [system-design/07 - API gateways and reverse proxies](../../system-design/lessons/07-api-gateways-proxies.md)
