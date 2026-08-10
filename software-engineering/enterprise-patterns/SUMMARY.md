# Patterns of Enterprise Application Architecture - Subject Summary

A comprehensive recap of *Patterns of Enterprise Application Architecture* (Martin
Fowler), concept by concept.

**Progress note:** all 14 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
layering and domain-logic patterns first, then data-source and O/R mapping patterns,
then web presentation, concurrency, and distribution.

## Layering and domain logic

- **[enterprise-patterns/01] Layering and the enterprise application** - Presentation,
  Domain, Data Source as the foundational three-layer split; the older, looser ancestor
  of `clean-architecture/08`'s dependency rule. ([lesson](lessons/01-layering.md))
- **[enterprise-patterns/02] Domain logic: Transaction Script vs Domain Model** -
  one procedure per transaction (simple, duplicates) vs. a network of objects with
  data and behavior (powerful, costs mapping complexity).
  ([lesson](lessons/02-domain-logic-patterns.md))
- **[enterprise-patterns/03] Table Module and Service Layer** - Table Module organizes
  logic around a whole table; Service Layer gives Presentation clients one clean,
  coarse-grained, use-case-shaped API regardless of what's underneath.
  ([lesson](lessons/03-table-module-service-layer.md))

## Data source and object-relational mapping

- **[enterprise-patterns/04] Data source: Row Data Gateway and Table Data Gateway** -
  business-logic-free wrappers around SQL, matched to Domain Model (per-row) or
  Table Module/Transaction Script (per-table). ([lesson](lessons/04-data-source-gateways.md))
- **[enterprise-patterns/05] Active Record** - merges business logic and persistence
  into one class per table; the pragmatic default behind most productive ORMs, until
  logic complexity strains the merge. ([lesson](lessons/05-active-record.md))
- **[enterprise-patterns/06] Data Mapper** - fully separates persistence-ignorant
  domain objects from a dedicated translation layer; the fuller realization of
  `clean-architecture/11`'s "database is a detail." ([lesson](lessons/06-data-mapper.md))
- **[enterprise-patterns/07] Unit of Work** - tracks new/dirty/removed objects across a
  business transaction and commits them together, atomically; what an ORM's
  session/context object actually is. ([lesson](lessons/07-unit-of-work.md))
- **[enterprise-patterns/08] Identity Map and Lazy Load** - one object per row per
  transaction (preventing silent lost updates); defer loading relationships until
  accessed (watch for the N+1 query trap). ([lesson](lessons/08-identity-map-lazy-load.md))
- **[enterprise-patterns/09] Object-relational structural mapping (inheritance)** -
  Single Table, Class Table, and Concrete Table Inheritance trade off storage waste,
  join cost, and schema-change coordination differently.
  ([lesson](lessons/09-or-structural-mapping.md))
- **[enterprise-patterns/10] Object-relational metadata mapping** - declarative
  field-to-column metadata plus one generic mapping engine, replacing hand-written
  Mappers; what ORM annotations/config actually do.
  ([lesson](lessons/10-or-metadata-mapping.md))

## Presentation, concurrency, and distribution

- **[enterprise-patterns/11] Web presentation (MVC, Page/Front Controller)** - Model/
  View/Controller separation; Front Controller centralizes cross-cutting concerns that
  Page Controller would otherwise duplicate. ([lesson](lessons/11-web-presentation.md))
- **[enterprise-patterns/12] Concurrency: optimistic vs pessimistic locking** -
  detect a lost-update conflict at save time via a version check (Optimistic) vs.
  prevent it by locking at edit-start (Pessimistic) - a question of actual contention
  rate. ([lesson](lessons/12-concurrency-locking.md))
- **[enterprise-patterns/13] Session state patterns** - Client, Server, and Database
  session state trade off server memory pressure, horizontal scalability, and
  restart-resilience differently. ([lesson](lessons/13-session-state.md))
- **[enterprise-patterns/14] Distribution and the Remote Facade / DTO** - fine-grained
  objects are catastrophic across a network boundary; coarse-grained Remote Facades
  plus plain DTOs minimize round trips. ([lesson](lessons/14-distribution-remote-facade-dto.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
