# Microservices Patterns - Subject Summary

A comprehensive recap of *Microservices Patterns* (Chris Richardson), concept by concept.

**Progress note:** all 12 lessons are `drafted`; none have been discussed yet, so mastery
is pending across the board and no weak spots are recorded. This summary will gain depth
(especially on the concepts you find hard) as discussions happen - the "Focus areas"
section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom
(dependency-ordered): motivation and decomposition first, then the data-consistency
patterns (sagas, event sourcing, CQRS), then external API, testing, and production
concerns. **Seniority baseline:** senior (lessons range mid->staff). The running example
throughout is FTGO (Food to Go), a food-delivery application.

## Motivation and decomposition

- **[microservices-patterns/01] The monolithic hell and the microservice architecture**
  (mid) - why a successful monolith eventually slows to a crawl (slow builds, coupled
  deploys, scaling-as-a-unit, tech lock-in) and how a microservice architecture -
  services organized around business capabilities, each independently deployable with its
  own database - relieves that pain at the cost of new distributed-systems complexity.
  ([lesson](lessons/01-monolithic-hell.md))
- **[microservices-patterns/02] Decomposition strategies** (senior) - how to actually
  find service boundaries: decompose by **business capability** and by **subdomain**
  (DDD), keep services loosely coupled and cohesive, and respect the database-per-service
  rule. Introduces the obstacles (god classes, cross-service data) that later patterns
  solve. ([lesson](lessons/02-decomposition-strategies.md))

## Inter-process communication

- **[microservices-patterns/03] Inter-process communication patterns** (senior) - the
  communication layer: synchronous (REST/gRPC) vs asynchronous messaging; the problem of
  partial failure and why it pushes you toward async; reliable messaging with the
  **transactional outbox** and message relay; and the need for **idempotent** consumers.
  Foundation for sagas, events, and CQRS. ([lesson](lessons/03-ipc-patterns.md))

## Data-consistency patterns (the core of the book)

- **[microservices-patterns/04] Managing transactions with sagas** (senior) - the
  centerpiece. With database-per-service you cannot use one ACID transaction across
  services, and 2PC is rejected. A **saga** is a sequence of local transactions linked by
  messages, with **compensating transactions** replacing rollback and a **pivot** dividing
  compensatable from retriable steps. Covers **choreography vs orchestration** and the
  hard part - no isolation - with countermeasures (semantic locks, etc.).
  ([lesson](lessons/04-sagas.md))
- **[microservices-patterns/05] Designing business logic: aggregates and domain events**
  (senior) - organizing a service's logic with the DDD **aggregate** (a consistency
  boundary with a single root; one aggregate per transaction; reference other aggregates
  by identity). Aggregate boundaries decide where sagas appear. **Domain events** emitted
  by aggregates (published reliably via the outbox) are the nervous system driving sagas,
  CQRS, and audit. ([lesson](lessons/05-business-logic-aggregates.md))
- **[microservices-patterns/06] Event sourcing** (senior) - persist an aggregate as its
  append-only sequence of domain events and rebuild state by replaying them (with
  **snapshots** to bound load time). Makes event publishing intrinsic (events are the
  source of truth) and gives a perfect audit log, at the cost of a different persistence
  model, hard event-schema evolution, and forcing CQRS for queries.
  ([lesson](lessons/06-event-sourcing.md))
- **[microservices-patterns/07] Querying with CQRS** (senior) - when queries span services
  or the write model can't serve them (e.g. event streams), split into a **command side**
  (writes, invariants, publishes events) and **query-side read models** (denormalized,
  purpose-built, rebuildable projections kept current by subscribing to events). The tax
  is eventual consistency (read-your-writes lag) paid on the read side.
  ([lesson](lessons/07-cqrs.md))

## External API

- **[microservices-patterns/08] External API patterns and the API gateway** (senior) - how
  outside clients reach the services. The **API Gateway** is a single entry point that
  routes, composes (API composition), and offloads cross-cutting concerns; the
  **Backends-for-Frontends (BFF)** variant gives each client type its own gateway.
  Contrast with direct client-to-service access. ([lesson](lessons/08-external-api-gateway.md))

## Testing and production concerns

- **[microservices-patterns/09] Testing strategies for microservices** (senior) - testing
  independently deployable services without slow, brittle end-to-end suites. The **test
  pyramid** applied to services, and **consumer-driven contract tests** (Pact-style) that
  verify inter-service compatibility cheaply, plus component and integration testing.
  ([lesson](lessons/09-testing-strategies.md))
- **[microservices-patterns/10] Production-ready services** (senior) - making a service
  fit for production: the **observability** patterns (health-check API, log aggregation,
  distributed tracing, application metrics, exception tracking) and the **security**,
  configuration (externalized config), and reliability concerns that operating many
  services demands. ([lesson](lessons/10-production-ready-services.md))
- **[microservices-patterns/11] Deployment patterns** (mid) - the spectrum of how services
  run: language-specific packages, virtual machines, containers, and **serverless**, plus
  the **service mesh** and sidecar. The trade-offs in isolation, resource use, and
  operational overhead. Cross-links to the sidecar pattern in Designing Distributed
  Systems. ([lesson](lessons/11-deployment-patterns.md))

## Migration

- **[microservices-patterns/12] Refactoring a monolith to microservices** (staff) - the
  real-world job: migrate incrementally with the **Strangler Fig** strategy (never a
  big-bang rewrite). Stop digging (build new features as services), split frontend from
  backend, and extract capabilities one at a time by value/risk; keep data consistent
  across the seam with anti-corruption layers, events, and sagas; and change the
  organization, not just the code. ([lesson](lessons/12-refactoring-to-microservices.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak spots
and misconceptions will be aggregated here, with extra detail on the concepts rated
`shaky` or `not-yet`. (Likely candidates for depth once discussed: sagas and the isolation
countermeasures (04), and the event-sourcing/CQRS pairing (06-07), which carry the most
subtlety.)
