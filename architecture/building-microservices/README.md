# Building Microservices

The service-decomposition layer of the architecture track: how to split a system into
independently deployable services and keep them shippable - service boundaries,
inter-service communication, per-service data, deployment and delivery, testing,
observability, resilience, and the organizational side of running many services.
Cross-links to DDIA (data and consistency) and The Hard Parts (granularity and sagas).

**Source book:** *Building Microservices* (2nd edition) - Sam Newman (O'Reilly, 2021).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`building-microservices/<NN>`* (e.g. *"discuss `building-microservices/03`"*). Ordered
by dependency: definitions and modelling first, then communication and data, then
delivery, operations, and scaling the organization.

**Seniority baseline:** senior (lessons range mid->staff).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | What microservices are (and are not) | mid | drafted | — | — | [lesson](lessons/01-what-microservices-are.md) | — |
| 02  | Modelling services around business domains | senior | drafted | — | — | [lesson](lessons/02-modelling-services.md) | — |
| 03  | Defining service boundaries and coupling/cohesion | senior | drafted | — | — | [lesson](lessons/03-service-boundaries-coupling.md) | — |
| 04  | Splitting the monolith (migration patterns) | senior | drafted | — | — | [lesson](lessons/04-splitting-the-monolith.md) | — |
| 05  | Inter-service communication styles | mid | drafted | — | — | [lesson](lessons/05-communication-styles.md) | — |
| 06  | Synchronous vs asynchronous and event-driven | senior | drafted | — | — | [lesson](lessons/06-sync-async-event-driven.md) | — |
| 07  | Managing data: per-service databases | senior | drafted | — | — | [lesson](lessons/07-per-service-data.md) | — |
| 08  | Distributed transactions and sagas | senior | drafted | — | — | [lesson](lessons/08-distributed-transactions-sagas.md) | — |
| 09  | Build, CI, and artifact management | mid | drafted | — | — | [lesson](lessons/09-build-ci-artifacts.md) | — |
| 10  | Deployment: containers, orchestration, and patterns | senior | drafted | — | — | [lesson](lessons/10-deployment-patterns.md) | — |
| 11  | Testing microservices (unit to contract to E2E) | mid | drafted | — | — | [lesson](lessons/11-testing-microservices.md) | — |
| 12  | Consumer-driven contracts | senior | drafted | — | — | [lesson](lessons/12-consumer-driven-contracts.md) | — |
| 13  | Observability: logs, metrics, tracing, correlation IDs | mid | drafted | — | — | [lesson](lessons/13-observability.md) | — |
| 14  | Resilience: timeouts, retries, bulkheads, circuit breakers | senior | drafted | — | — | [lesson](lessons/14-resilience.md) | — |
| 15  | Scaling microservices | senior | drafted | — | — | [lesson](lessons/15-scaling.md) | — |
| 16  | Security in a microservice system | senior | drafted | — | — | [lesson](lessons/16-security.md) | — |
| 17  | Conway's law and team organization | staff | drafted | — | — | [lesson](lessons/17-conways-law-teams.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites** (e.g. `ddia/11`, `hard-parts/11`) are listed per lesson
in its front matter and named in prose.
