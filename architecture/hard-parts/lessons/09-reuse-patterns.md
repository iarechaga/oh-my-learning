---
id: hard-parts/09
subject: hard-parts
title: Reuse Patterns
slug: reuse-patterns
status: drafted
mastery:
seniority: mid
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 8
prerequisites: [hard-parts/02, hard-parts/07]
created: 2026-06-30
updated: 2026-06-30
---

# Reuse Patterns

## TL;DR
Reuse in distributed systems is a coupling choice.
You can copy code, ship a shared library, call a shared service, or standardize operational behavior through sidecars and a service mesh.
The right option depends on change frequency, consistency needs, and acceptable failure blast radius.

## The idea
Many services need similar functionality: authentication checks, log formatting, shared domain calculations, and request metadata handling.
In a monolith, shared code is usually straightforward.
In microservices, reuse can accidentally re-couple independent services.

So the design question is not "should we reuse?"
It is "what kind of dependency are we creating by reusing this?"

The key trade-off:

1. Too little reuse -> duplication, drift, repeated bugs.
2. Too much reuse in the wrong form -> synchronized change and distributed-monolith behavior.

A useful mental test is:
if this shared logic changes tomorrow, who must react, and when?

## How it works
The four patterns differ by binding time and coupling style:

- Code replication: no shared dependency after copy.
- Shared library: compile-time or build-time binding.
- Shared service: runtime network binding.
- Sidecar plus mesh: operational runtime binding for cross-cutting concerns.

### 1) Code Replication
Copy common code into each service repository.
No package.
No shared runtime.
Each team owns its local copy.

Worked example:

1. Sysops Squad runs Inventory, Billing, and Incidents services.
2. Each copies a tiny `sanitizeHeaderValue()` helper.
3. A bug appears in edge-case input handling.
4. Inventory patches immediately.
5. Billing patches next sprint.
6. Incidents patches later after a support ticket.
7. Temporary behavior drift appears.

Pros for code replication:

- Zero coupling between services from reused code.
- No dependency graph management.
- No runtime latency overhead.
- Maximum team autonomy.

Cons for code replication:

- Every fix must be repeated manually.
- Drift and inconsistency are common.
- Security fixes can lag across services.
- Hard to prove uniform behavior.

When to use:

- Very small helper code.
- Very stable and rarely changing logic.
- Low risk if services diverge briefly.

When to avoid:

- Security-sensitive or policy-heavy logic.
- Frequently changing shared behavior.
- Strict consistency requirements.

### 2) Shared Library
Package common code as a versioned binary dependency (JAR, NuGet, wheel, etc.).
Consumers compile against a selected version.
This is static coupling.

Worked example:

1. Sysops Squad creates `sysops-auth-lib` for token validation and claim parsing.
2. Inventory upgrades to v2.2 quickly.
3. Billing remains on v2.1 due to transitive dependency conflicts.
4. During upgrade lag, auth behavior differs slightly.

Pros for shared library:

- Fast runtime (local call, no network hop).
- Compile-time checks catch many integration mistakes.
- Versioning enables staged rollout.
- Good fit for moderate, controlled change rates.

Cons for shared library:

- Consumers must rebuild and redeploy to adopt changes.
- Versioning and compatibility strategy become critical.
- Dependency hell can slow delivery.
- Breaking changes can affect many consumers.

Granularity trade-off:

1. More granular libraries improve change isolation.
2. But more libraries increase dependency complexity.
3. One large library simplifies dependency list.
4. But one large library increases blast radius.

When to use:

- Shared logic changes at moderate pace.
- Teams can manage version governance.
- Compile-time safety matters.

When to avoid:

- Rules must update everywhere immediately.
- Dependency management is already a bottleneck.

### 3) Shared Service
Extract shared functionality into a standalone service called over the network.
This is dynamic coupling at runtime.

Worked example:

1. Sysops Squad builds `auth-policy-service`.
2. Inventory, Billing, and Incidents request auth decisions at runtime.
3. Compliance rule changes Monday morning.
4. Auth team deploys one update.
5. All consumers enforce new policy immediately.
6. Tuesday latency spikes in auth service.
7. Callers suffer retries, timeouts, and possible outage propagation.

Pros for shared service:

- Deploy once, propagate instantly.
- Language-agnostic integration.
- Single authoritative implementation.
- Best fit for frequently changing shared logic.

Cons for shared service:

- Adds network latency.
- Introduces runtime dependency and potential single point of failure.
- No compile-time contract guarantee for consumers.
- Provider scalability issues can affect many services.

When to use:

- Shared logic changes frequently.
- Immediate consistency is required.
- You can operate timeouts, retries, circuit breakers, autoscaling, and SLOs.

When to avoid:

- Very tight latency budgets.
- Weak platform reliability maturity.

### 4) Sidecar and Service Mesh
This pattern targets operational concerns, not domain coupling.

Sidecar: companion process next to each service instance.
Service mesh: networked plane of sidecars plus control policy.

Typical mesh concerns:

- mTLS
- tracing propagation
- telemetry export
- retries/timeouts
- circuit breaking and traffic controls

Worked example:

1. Sysops Squad keeps auth domain logic in library or shared service.
2. They move mTLS and tracing to sidecars.
3. Retry and timeout defaults are mesh policy.
4. All services inherit consistent operational behavior.
5. Domain code stays focused on business decisions.

Pros for sidecar and service mesh:

- Consistent operational behavior across services.
- Central governance for observability and security.
- Less duplicated operational plumbing in app code.
- Avoids domain-level recoupling.

Cons for sidecar and service mesh:

- Significant infrastructure complexity.
- Misconfiguration can create broad incidents.
- Requires strong platform ownership.
- Debugging spans app and mesh layers.

When to use:

- Many services need uniform operational controls.
- A platform team can operate and govern mesh lifecycle.

When to avoid:

- Small systems where overhead exceeds benefit.
- Teams without mature operations discipline.

### ASCII comparison table

+----------------------+-----------------------------+---------------------------------------------+---------------------------------------------+---------------------------------------------+---------------------------------------------+-------------------------------+
| Pattern              | Binding time                | Coupling type                               | Change propagation                          | Performance                                 | Failure blast radius                         | Best-fit change rate          |
+----------------------+-----------------------------+---------------------------------------------+---------------------------------------------+---------------------------------------------+---------------------------------------------+-------------------------------+
| Code replication     | none after copy             | no inter-service dependency                 | manual patch per service                    | local call, fastest                          | local, per service copy                      | very low and stable           |
| Shared library       | compile-time / build-time   | static binary dependency                    | per-consumer upgrade and redeploy           | local call, fast                             | medium, depends on version adoption          | moderate and controlled       |
| Shared service       | runtime                     | dynamic runtime dependency                  | immediate after provider deploy             | network hop and serialization overhead       | high, provider issues affect all callers     | high and fast-changing        |
| Sidecar + mesh       | operational runtime         | operational coupling (not domain coupling)  | policy rollout via control plane/sidecars   | data-plane overhead, tunable                 | platform-wide if mesh policy/control fails   | frequent operational changes  |
+----------------------+-----------------------------+---------------------------------------------+---------------------------------------------+---------------------------------------------+---------------------------------------------+-------------------------------+

### Worked decision: Sysops Squad authentication
Sysops Squad needs shared authentication across Inventory, Billing, and Incidents.
Decision rule:

1. If auth rules change quarterly, pick shared library.
2. If auth rules change weekly and must take effect immediately, pick shared service.
3. In both cases, keep mTLS, tracing, retries, and circuit breaking in sidecars/mesh.

Branch A (shared library):

1. Publish `sysops-auth-lib` v3.0.
2. Upgrade services during normal release trains.
3. Keep runtime path fast and local.

Branch B (shared service):

1. Run central `auth-policy-service`.
2. Deploy policy once for instant global effect.
3. Enforce strict timeout/fallback behavior at callers.

This separation keeps domain reuse and operational reuse from being mixed.

## Pros
- Reduces duplicated engineering work for recurring capabilities.
- Improves consistency for policy, compliance, and user-visible behavior.
- Makes coupling decisions explicit and governable.
- Helps teams focus on domain differentiation instead of rebuilding utilities.
- Enables architecture-level optimization (autonomy vs consistency vs speed) when chosen deliberately.

## Cons
- Can reintroduce coupling if chosen mechanically.
- Requires ownership, governance, and rollout coordination.
- Central reuse points can become runtime or delivery bottlenecks.
- Wrong pattern can increase blast radius and incident impact.
- Migrating off a poor early choice can be expensive.

## Alternatives
The primary alternative is intentional duplication: do not reuse yet.

Use that choice when all are true:

1. Shared logic is tiny.
2. Change rate is low.
3. Inconsistency risk is acceptable.
4. Service boundaries are still evolving.

Re-evaluate periodically.
When change frequency or consistency pressure rises, move to shared library or shared service.

## When to use it
Use reuse patterns when unmanaged duplication causes drift, defects, or repeated delivery effort across services.

Selector:

1. Tiny stable helper -> code replication.
2. Moderate-change shared logic -> shared library.
3. Fast-changing shared logic needing instant rollout -> shared service.
4. Cross-cutting operational consistency -> sidecar and mesh.

Add fitness functions so reuse remains enforceable.
Examples:

- all services call shared auth with timeout and circuit breaker
- approved auth library major version adopted within defined window

## When NOT to use it
Do not force reuse by default.
If boundaries are unclear or platform operations are weak, reuse can increase risk.

Common anti-fits:

1. Shared service for slow-changing logic.
2. Shared library when dependency graph is already unstable.
3. Mesh adoption without platform readiness.
4. Code replication for logic that must remain globally consistent.

Also avoid category errors:
operational concerns belong in platform mechanisms,
not in duplicated domain code.

## Key takeaways / mental model
Reuse patterns are change channels.

1. Replication channel: no shared dependency, manual propagation.
2. Library channel: static coupling, versioned propagation.
3. Service channel: dynamic coupling, immediate propagation.
4. Mesh channel: operational coupling, policy propagation.

Match channel to change rate and failure tolerance.
If change must be immediate, accept runtime dependency.
If autonomy matters most, accept controlled duplication.
If concern is operational, keep it out of domain code and put it in sidecars/mesh.

Remember this sentence:
reuse is beneficial only when the coupling it introduces is the coupling you actually want.

## Self-check questions
1. Why can a shared library improve runtime speed yet still increase architectural coupling?
2. When is code replication an intentional design choice rather than an anti-pattern?
3. Why does shared service improve change propagation but increase runtime risk?
4. In Sysops Squad, what evidence would make you choose shared service over shared library for auth?
5. Which concerns belong in sidecar/mesh and should not be implemented as domain-code reuse?
6. How does library granularity affect change isolation versus dependency complexity?
7. If policy mismatch appears across services for two weeks, which reuse pattern is most likely in play, and why?

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 8
- [02-architecture-quantum-static-coupling.md](02-architecture-quantum-static-coupling.md)
- [03-dynamic-coupling.md](03-dynamic-coupling.md)
- [07-api-gateways-proxies.md](../../system-design/lessons/07-api-gateways-proxies.md)
