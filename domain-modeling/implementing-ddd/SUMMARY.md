# Implementing Domain-Driven Design - Subject Summary

A comprehensive recap of *Implementing Domain-Driven Design* by Vaughn Vernon, concept
by concept - the practical execution layer for building real systems around
aggregates, bounded contexts, and asynchronous collaboration.

**Progress note:** all 15 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
strategic foundations, then domain-model building blocks and aggregate mechanics, then
persistence and orchestration, then cross-context integration, then advanced
architecture for consistency at scale.

## Strategic foundations

- **[implementing-ddd/01] Distilling strategic design into implementation decisions** -
  classify subdomains as core, supporting, or generic before writing code; tactical
  investment (rich aggregates, events, event sourcing) should track that classification,
  not be applied uniformly everywhere.
  ([lesson](lessons/01-distilling-strategic-design-into-implementation-decisions.md))
- **[implementing-ddd/03] Bounded contexts as autonomous service boundaries** - a
  linguistic/model boundary only holds if it's also a team, deployment, and schema
  boundary; Conway's Law applied deliberately.
  ([lesson](lessons/03-bounded-contexts-as-autonomous-service-boundaries.md))

## Domain model building blocks and aggregate mechanics

- **[implementing-ddd/02] Domain model building blocks in code** - entities (identity,
  mutable, lifecycle), value objects (immutable, structural equality), domain services
  (logic spanning entities), and concept-first modules.
  ([lesson](lessons/02-domain-model-building-blocks-in-code.md))
- **[implementing-ddd/04] Effective aggregate design and true invariants** - model only
  true invariants inside a boundary, design small aggregates, reference other aggregates
  by identity, one aggregate per transaction.
  ([lesson](lessons/04-effective-aggregate-design-and-true-invariants.md))
- **[implementing-ddd/05] Aggregate references by identity** - never hold a live object
  reference to another aggregate; identity-only references are what makes small
  aggregate boundaries structurally real, not just aspirational.
  ([lesson](lessons/05-aggregate-references-by-identity.md))
- **[implementing-ddd/06] Eventual consistency around aggregate boundaries** - the
  necessary consequence of small aggregates: name the consistency window explicitly and
  close it with domain events instead of distributed transactions.
  ([lesson](lessons/06-eventual-consistency-around-aggregate-boundaries.md))
- **[implementing-ddd/07] Domain events and immutable business facts** - past-tense,
  self-sufficient records of what happened, raised by the aggregate that owns the fact;
  the mechanism behind eventual consistency and integration alike.
  ([lesson](lessons/07-domain-events-and-immutable-business-facts.md))

## Persistence and orchestration

- **[implementing-ddd/08] Repositories and persistence-mapping strategies** - give the
  domain model an in-memory-collection illusion over whole aggregates only; interface in
  the domain layer, implementation in infrastructure.
  ([lesson](lessons/08-repositories-and-persistence-mapping-strategies.md))
- **[implementing-ddd/09] Application services and command orchestration** - one method
  per use case, fetch-invoke-persist-publish, zero business logic in the service itself.
  ([lesson](lessons/09-application-services-and-command-orchestration.md))

## Cross-context integration

- **[implementing-ddd/10] Published language and context-map contracts** - name the
  integration relationship (Partnership, Customer/Supplier, Conformist, ACL, Open Host
  Service/Published Language, Shared Kernel, Separate Ways) explicitly for every pair of
  related contexts.
  ([lesson](lessons/10-published-language-and-context-map-contracts.md))
- **[implementing-ddd/11] Anti-corruption layers and translation boundaries** - a
  Facade/Adapter/Translator boundary that keeps an upstream system's model and quirks
  from leaking into your own.
  ([lesson](lessons/11-anti-corruption-layers-and-translation-boundaries.md))
- **[implementing-ddd/12] Integrating bounded contexts with messaging** - durable,
  idempotent, event-driven integration as the default; transactional outbox to avoid
  losing events; sync calls reserved for genuine immediate-answer needs.
  ([lesson](lessons/12-integrating-bounded-contexts-with-messaging.md))

## Advanced architecture for consistency at scale

- **[implementing-ddd/13] Event sourcing and stream-based aggregates** - persist the
  event stream as the system of record, derive current state by replay; powerful for
  audit/temporal needs, heavyweight otherwise.
  ([lesson](lessons/13-event-sourcing-and-stream-based-aggregates.md))
- **[implementing-ddd/14] CQRS and read-model segregation** - split queries onto
  denormalized, event-driven read models freed from write-side aggregate boundaries.
  ([lesson](lessons/14-cqrs-and-read-model-segregation.md))
- **[implementing-ddd/15] Sagas and process managers for long-running consistency** -
  stateful, durable coordination of multi-step cross-aggregate processes, with explicit
  compensating actions when a step fails.
  ([lesson](lessons/15-sagas-and-process-managers-for-long-running-consistency.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
