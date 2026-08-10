# Learning Domain-Driven Design - Subject Summary

A comprehensive recap of *Learning Domain-Driven Design* (Vlad Khononov), concept by
concept.

**Progress note:** all 14 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
strategic framing and problem-space analysis first, then collaborative discovery, then
tactical modeling, then architecture, integration, and evolution.

## Strategic design: where to invest

- **[learning-ddd/01] Why domain complexity drives design choices** - design investment
  should track business complexity and differentiation, not technology habit; the
  founding claim the whole subject builds on. ([lesson](lessons/01-why-domain-complexity-drives-design-choices.md))
- **[learning-ddd/02] Subdomains: core, supporting, and generic** - classify every part
  of the business as core (competitive advantage), supporting (necessary but not
  differentiating), or generic (buy, don't build); revisit as strategy shifts.
  ([lesson](lessons/02-subdomains-core-supporting-and-generic.md))
- **[learning-ddd/03] Bounded contexts and autonomy boundaries** - draw explicit
  linguistic/organizational boundaries so the same word can safely mean different
  things in different parts of the system; the solution-space answer to subdomains.
  ([lesson](lessons/03-bounded-contexts-and-autonomy-boundaries.md))
- **[learning-ddd/04] Context maps and relationship patterns** - name the power dynamic
  between bounded contexts (Partnership, Customer-Supplier, Conformist, Anticorruption
  Layer, Open Host Service, Separate Ways) instead of leaving it implicit.
  ([lesson](lessons/04-context-maps-and-relationship-patterns.md))

## Collaborative discovery

- **[learning-ddd/05] Ubiquitous language in collaborative discovery** - use domain
  experts' exact vocabulary in code, with zero silent translation, inside each bounded
  context. ([lesson](lessons/05-ubiquitous-language-in-collaborative-discovery.md))
- **[learning-ddd/06] Event storming to discover process and hotspots** - a
  collaborative workshop technique (orange events, blue commands, purple policies, red
  hotspots) that surfaces real process, vocabulary, and disagreements far faster than
  interviews or written specs. ([lesson](lessons/06-event-storming-to-discover-process-and-hotspots.md))

## Tactical design

- **[learning-ddd/07] Business logic patterns: transaction script, active record,
  domain model** - match implementation pattern to subdomain complexity: simple/generic
  logic gets Transaction Script or Active Record; genuinely complex core logic earns a
  rich Domain Model. ([lesson](lessons/07-business-logic-patterns-transaction-script-active-record-domain-model.md))
- **[learning-ddd/08] Aggregates and invariants in tactical design** - draw the
  transactional-consistency boundary as small as possible, around only what a true
  invariant requires to change atomically together. ([lesson](lessons/08-aggregates-and-invariants-in-tactical-design.md))
- **[learning-ddd/09] Domain events and temporal modeling** - aggregates communicate
  across boundaries via past-tense domain events; taken further, events themselves can
  become the system of record (event sourcing) for genuine audit/history needs.
  ([lesson](lessons/09-domain-events-and-temporal-modeling.md))

## Cross-context data and integration

- **[learning-ddd/10] Data ownership and consistency boundaries** - exactly one context
  owns any given fact; every other context holds a deliberately-chosen, explicit
  eventually-consistent copy or queries the owner directly, never shared-database
  access. ([lesson](lessons/10-data-ownership-and-consistency-boundaries.md))
- **[learning-ddd/11] Integration patterns between bounded contexts** - the technical
  mechanism (sync request-response, async messaging, event streaming) follows from the
  relationship and consistency decisions already made; outbox pattern and idempotent
  consumers make async integration reliable. ([lesson](lessons/11-integration-patterns-between-bounded-contexts.md))

## Architecture and evolution

- **[learning-ddd/12] Domain model to service architecture alignment** - Layered
  Architecture, Ports & Adapters, and CQRS are chosen per bounded context based on its
  business-logic pattern and read/write divergence, not applied uniformly.
  ([lesson](lessons/12-domain-model-to-service-architecture-alignment.md))
- **[learning-ddd/13] Evolutionary design and refactoring of contexts** - every
  boundary and classification is a hypothesis; start coarse, split or merge on real
  evidence, and use the Strangler Fig pattern for safe structural migration.
  ([lesson](lessons/13-evolutionary-design-and-refactoring-of-contexts.md))
- **[learning-ddd/14] Socio-technical alignment and team topologies for DDD** -
  Conway's Law means bounded-context boundaries and team boundaries should be designed
  together (Stream-Aligned, Platform, Enabling, Complicated-Subsystem teams), closing
  the loop from strategic design back to organizational design.
  ([lesson](lessons/14-socio-technical-alignment-and-team-topologies-for-ddd.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
