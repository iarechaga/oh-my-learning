# Microservices Patterns

The pattern-catalog layer for microservices: a structured set of named patterns for
decomposition, inter-service communication, distributed data consistency, querying
across services, testing, deployment, and observability. Where *Building Microservices*
covers the practice broadly, this subject drills into the reusable patterns (with the
saga and CQRS material front and center). Cross-links to DDIA and The Hard Parts.

**Source book:** *Microservices Patterns* - Chris Richardson (Manning, 2018).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`microservices-patterns/<NN>`* (e.g. *"discuss `microservices-patterns/05`"*). Ordered
by dependency: motivation and decomposition first, then the data-consistency patterns
(sagas, event sourcing, CQRS), then external API, testing, and production concerns.

**Seniority baseline:** senior (lessons range mid->staff).

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | The monolithic hell and the microservice architecture | mid | drafted | — | — | [lesson](lessons/01-monolithic-hell.md) | — |
| 02  | Decomposition strategies (by capability and subdomain) | senior | drafted | — | — | [lesson](lessons/02-decomposition-strategies.md) | — |
| 03  | Inter-process communication patterns | senior | drafted | — | — | [lesson](lessons/03-ipc-patterns.md) | — |
| 04  | Managing transactions with sagas | senior | drafted | — | — | [lesson](lessons/04-sagas.md) | — |
| 05  | Designing the business logic (aggregates and domain events) | senior | drafted | — | — | [lesson](lessons/05-business-logic-aggregates.md) | — |
| 06  | Event sourcing | senior | drafted | — | — | [lesson](lessons/06-event-sourcing.md) | — |
| 07  | Querying with CQRS | senior | drafted | — | — | [lesson](lessons/07-cqrs.md) | — |
| 08  | External API patterns and the API gateway | senior | drafted | — | — | [lesson](lessons/08-external-api-gateway.md) | — |
| 09  | Testing strategies for microservices | senior | drafted | — | — | [lesson](lessons/09-testing-strategies.md) | — |
| 10  | Production-ready services (observability, security, config) | senior | drafted | — | — | [lesson](lessons/10-production-ready-services.md) | — |
| 11  | Deployment patterns | mid | drafted | — | — | [lesson](lessons/11-deployment-patterns.md) | — |
| 12  | Refactoring a monolith to microservices | staff | drafted | — | — | [lesson](lessons/12-refactoring-to-microservices.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites** (e.g. `ddia/11`, `hard-parts/12`) are listed per lesson
in its front matter and named in prose.
