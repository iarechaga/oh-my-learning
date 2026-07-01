# Implementing Domain-Driven Design

This subject is the practical DDD execution layer - the red-book guidance for building
real systems around aggregates, bounded contexts, and asynchronous collaboration. It
focuses on implementation details that keep the model honest under concurrency,
integration pressure, and changing business workflows.

**Source book:** *Implementing Domain-Driven Design* - Vaughn Vernon (Addison-Wesley, 2013).

**Seniority baseline:** senior (lessons range mid->staff).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`implementing-ddd/<NN>`* (e.g. *"discuss `implementing-ddd/03`"*). Ordered by dependency: implementation foundations first, then aggregate and context mechanics, then integration and long-running process coordination.

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Distilling strategic design into implementation decisions | senior | drafted | — | — | [lesson](lessons/01-distilling-strategic-design-into-implementation-decisions.md) | — |
| 02  | Domain model building blocks in code | mid | drafted | — | — | [lesson](lessons/02-domain-model-building-blocks-in-code.md) | — |
| 03  | Bounded contexts as autonomous service boundaries | senior | drafted | — | — | [lesson](lessons/03-bounded-contexts-as-autonomous-service-boundaries.md) | — |
| 04  | Effective aggregate design and true invariants | senior | drafted | — | — | [lesson](lessons/04-effective-aggregate-design-and-true-invariants.md) | — |
| 05  | Aggregate references by identity | senior | drafted | — | — | [lesson](lessons/05-aggregate-references-by-identity.md) | — |
| 06  | Eventual consistency around aggregate boundaries | senior | drafted | — | — | [lesson](lessons/06-eventual-consistency-around-aggregate-boundaries.md) | — |
| 07  | Domain events and immutable business facts | senior | drafted | — | — | [lesson](lessons/07-domain-events-and-immutable-business-facts.md) | — |
| 08  | Repositories and persistence-mapping strategies | senior | drafted | — | — | [lesson](lessons/08-repositories-and-persistence-mapping-strategies.md) | — |
| 09  | Application services and command orchestration | mid | drafted | — | — | [lesson](lessons/09-application-services-and-command-orchestration.md) | — |
| 10  | Published language and context-map contracts | staff | drafted | — | — | [lesson](lessons/10-published-language-and-context-map-contracts.md) | — |
| 11  | Anti-corruption layers and translation boundaries | staff | drafted | — | — | [lesson](lessons/11-anti-corruption-layers-and-translation-boundaries.md) | — |
| 12  | Integrating bounded contexts with messaging | senior | drafted | — | — | [lesson](lessons/12-integrating-bounded-contexts-with-messaging.md) | — |
| 13  | Event sourcing and stream-based aggregates | staff | drafted | — | — | [lesson](lessons/13-event-sourcing-and-stream-based-aggregates.md) | — |
| 14  | CQRS and read-model segregation | senior | drafted | — | — | [lesson](lessons/14-cqrs-and-read-model-segregation.md) | — |
| 15  | Sagas and process managers for long-running consistency | staff | drafted | — | — | [lesson](lessons/15-sagas-and-process-managers-for-long-running-consistency.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Seniority:** `junior` · `mid` · `senior` · `staff` · `principal` - the band whose job the concept anchors.
