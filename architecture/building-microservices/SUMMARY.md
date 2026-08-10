# Building Microservices - Subject Summary

A concept-by-concept recap of the building-microservices subject: how to split a
system into independently deployable services and keep them shippable - boundaries,
communication, data, delivery, testing, operations, and the organizational side of
running many services.

**Source book:** *Building Microservices* (2nd edition) - Sam Newman (O'Reilly, 2021).

**Progress note:** all 17 lessons are `drafted`; none discussed yet, so mastery is
pending and no weak spots are recorded. See the table in [README.md](README.md).
Reading order is top to bottom (dependency-ordered): definitions and modelling first,
then communication and data, then delivery, operations, and scaling the organization.

## Foundations: what and where to split

- **[01] What microservices are (and are not)** - defined by independent
  deployability, not size; a service is modeled around a business domain and owns its
  own data. Microservices are a deliberate trade-off (real operational complexity for
  independent deployability and scaling) - only worth taking on when you actually need
  it. ([lesson](lessons/01-what-microservices-are.md))
- **[02] Modelling services around business domains** - use DDD-style bounded
  contexts, found via event storming and watching for words ("Customer") that mean
  different things to different parts of the business, to find natural service seams.
  Includes a worked decomposition of an e-commerce order flow into
  catalog/cart/order/payment/inventory/shipping services.
  ([lesson](lessons/02-modelling-services.md))
- **[03] Defining service boundaries and coupling/cohesion** - high cohesion, low
  coupling as the north star. Three coupling types to actively avoid: implementation
  coupling (shared database), temporal coupling (synchronous chains), deployment
  coupling (must-release-together). Information hiding is the main tool for keeping
  coupling low. ([lesson](lessons/03-service-boundaries-coupling.md))
- **[04] Splitting the monolith (migration patterns)** - never a big-bang rewrite;
  extract incrementally via the strangler fig pattern (intercept and redirect traffic),
  branch by abstraction (an in-code seam for internal replacements), and parallel run
  (verify the new path before trusting it). Extract the least-coupled pieces first, not
  the tangled core. ([lesson](lessons/04-splitting-the-monolith.md))

## Communication and data

- **[05] Inter-service communication styles** - request-response (needs an immediate
  answer) vs. event-based (fire and let subscribers react independently); orchestration
  (centralized process control) vs. choreography (distributed, event-driven reactions)
  for multi-step processes. ([lesson](lessons/05-communication-styles.md))
- **[06] Synchronous vs asynchronous and event-driven** - the mechanics: synchronous
  chains compound latency (additive) and multiply unavailability (`p^N`); a slow
  downstream service can cascade upward and exhaust caller resources. Async/event-driven
  (brokers, event streams) decouples callers in time at the cost of eventual
  consistency. Worked latency/availability math included.
  ([lesson](lessons/06-sync-async-event-driven.md))
- **[07] Managing data: per-service databases** - the shared-database anti-pattern
  recreates monolithic coupling; database-per-service is the fix. Losing free joins and
  ACID transactions is answered with API composition, CQRS-lite (service-owned read
  models built from events), and dedicated data pipelines for analytics.
  ([lesson](lessons/07-per-service-data.md))
- **[08] Distributed transactions and sagas** - sagas replace cross-service ACID with a
  sequence of local transactions plus explicit compensating actions; orchestrated vs.
  choreographed sagas, with a full worked example of a four-step order saga and its
  compensations. Practitioner-level treatment; the exhaustive pattern catalog is in
  `hard-parts/14`. ([lesson](lessons/08-distributed-transactions-sagas.md))

## Delivery and quality

- **[09] Build, CI, and artifact management** - one pipeline per service, triggered
  only by that service's own changes, producing one independently versioned, immutable
  artifact. A shared monolithic build recreates the release-train problem microservices
  are meant to escape. ([lesson](lessons/09-build-ci-artifacts.md))
- **[10] Deployment: containers, orchestration, and patterns** - containers as the
  standard deployment unit; orchestration (Kubernetes-shaped: scheduling, service
  discovery, self-healing) at scale. Rolling, blue-green, and canary deployment patterns
  compared on release speed vs. blast-radius control, with a worked risky-payment-change
  example. ([lesson](lessons/10-deployment-patterns.md))
- **[11] Testing microservices (unit to contract to E2E)** - the testing pyramid
  adapted to microservices, with contract tests as the essential new middle layer; E2E
  tests get exponentially more expensive/flaky as service count grows, so keep that
  layer small; testing in production (canary, feature flags) as a necessary complement,
  never a substitute. ([lesson](lessons/11-testing-microservices.md))
- **[12] Consumer-driven contracts** - the consumer defines exactly what it needs from
  a provider's API; the provider's own pipeline verifies every consumer's contract
  against its real implementation on every change, catching breaking changes in CI
  without a full E2E suite. Includes a worked example of a field rename caught before
  release. ([lesson](lessons/12-consumer-driven-contracts.md))

## Operations at scale

- **[13] Observability: logs, metrics, tracing, correlation IDs** - a single user
  request can span many services, so a correlation ID generated at entry and propagated
  on every call is what lets you reconstruct the full story. The three pillars (logs,
  metrics, traces) plus centralized log aggregation and distributed tracing move from
  nice-to-have to necessity. ([lesson](lessons/13-observability.md))
- **[14] Resilience: timeouts, retries, bulkheads, circuit breakers** - the toolkit for
  containing the cascading-failure risk from Lesson 06: timeouts bound waiting, retries
  need backoff and jitter to avoid retry storms, circuit breakers (closed/open/half-open)
  stop calling a persistently failing dependency, bulkheads isolate resource pools so
  one dependency's trouble can't starve calls to another.
  ([lesson](lessons/14-resilience.md))
- **[15] Scaling microservices** - the AKF scale cube: duplicate (X-axis, stateless
  only), decompose by function (Y-axis, what microservices give you for free), partition
  data (Z-axis, sharding). The critical distinction is stateless (scales by simple
  duplication) vs. stateful (needs partitioning/replication with a real consistency
  model). ([lesson](lessons/15-scaling.md))
- **[16] Security in a microservice system** - more services means more internal
  network calls means more attack surface; defense in depth applies authentication and
  authorization at every hop, not just the perimeter. mTLS and service identity answer
  "who is calling," centralized secrets management keeps credentials safe and rotatable,
  and zero-trust replaces the dangerous "trusted internal network" assumption.
  ([lesson](lessons/16-security.md))

## The organizational layer

- **[17] Conway's law and team organization** - a system's architecture mirrors the
  communication structure of the organization that built it; you cannot sustain a
  loosely-coupled architecture on top of a tightly-coupled team structure. The inverse
  Conway maneuver restructures teams first, around the target architecture, so
  organizational friction reinforces the intended boundaries. Stream-aligned teams
  (Team Topologies) with genuine end-to-end ownership, supported by platform and
  enabling teams, is the practical pattern. Highest-band lesson in the subject (staff) -
  covers org-shaped technical decisions and their second-order, cross-team effects.
  ([lesson](lessons/17-conways-law-teams.md))

## Cross-subject connections

- `ddia/10` (Partitioning) and `system-design/04` (Consistent Hashing) underpin Lesson
  15's Z-axis sharding.
- `hard-parts/14` (Transactional Sagas) is the deep, exhaustive pattern catalog behind
  Lesson 08's practitioner-level saga treatment; `hard-parts/13` (Distributed Workflows)
  does the same for Lesson 05's orchestration-vs-choreography introduction.
- `system-design/13`, `/14`, and `/15` (Security, Rate Limiting and Resilience,
  Observability) cover the same operational toolkits (Lessons 16, 14, 13) at the
  system-design level, with a broader, less microservices-specific lens.
