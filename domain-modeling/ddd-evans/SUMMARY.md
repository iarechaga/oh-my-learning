# Domain-Driven Design (Evans) - Subject Summary

A comprehensive recap of *Domain-Driven Design: Tackling Complexity in the Heart of
Software* by Eric Evans, concept by concept.

**Progress note:** all 16 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
shared language and model intent first, tactical building blocks next, then strategic
boundaries and system-wide evolution.

## Language and model intent

- **[ddd-evans/01] Knowledge crunching and ubiquitous language** - the model comes from
  collaborative, iterative digestion of messy domain knowledge with domain experts; the
  resulting vocabulary must appear identically in conversation, code, tests, and
  diagrams, with no private translation layer.
  ([lesson](lessons/01-knowledge-crunching-and-ubiquitous-language.md))
- **[ddd-evans/02] Model-driven design and the domain layer** - the model isn't
  documentation about the code, it's the code; business rules live in an isolated
  domain layer, not scattered across controllers and SQL.
  ([lesson](lessons/02-model-driven-design-and-domain-layer.md))
- **[ddd-evans/03] Layered architecture for model integrity** - UI, application,
  domain, and infrastructure layers, with dependencies pointing inward toward the
  domain, so the domain layer never depends on delivery mechanisms or persistence
  technology. ([lesson](lessons/03-layered-architecture-for-model-integrity.md))

## Tactical building blocks

- **[ddd-evans/04] Entities and continuity of identity** - defined by a thread of
  identity, not attribute values; two entities with identical attributes are still
  different things. ([lesson](lessons/04-entities-and-continuity-of-identity.md))
- **[ddd-evans/05] Value objects and side-effect-free modeling** - defined entirely by
  attributes, immutable, equal by value; validation baked into the constructor makes
  invalid values unrepresentable.
  ([lesson](lessons/05-value-objects-and-side-effect-free-modeling.md))
- **[ddd-evans/06] Services when behavior does not fit an object** - cross-object
  domain processes get an explicit, stateless, named home instead of being forced
  awkwardly onto one participant; domain services only, not application or
  infrastructure services in disguise.
  ([lesson](lessons/06-services-when-behavior-does-not-fit-an-object.md))
- **[ddd-evans/07] Modules as conceptual boundaries** - organize code by domain concept
  (high cohesion, low coupling), not by technical role; module names are part of the
  ubiquitous language too. ([lesson](lessons/07-modules-as-conceptual-boundaries.md))
- **[ddd-evans/08] Aggregates and transactional consistency boundaries** - one entity
  as aggregate root guards every cross-object invariant inside the cluster; one
  transaction touches at most one aggregate; reference other aggregates by ID.
  ([lesson](lessons/08-aggregates-and-transactional-consistency-boundaries.md))
- **[ddd-evans/09] Factories for complex creation and invariant safety** - centralize
  multi-step assembly so an aggregate can never exist in a partially-valid state;
  plain validating constructors are enough for simple objects.
  ([lesson](lessons/09-factories-for-complex-creation-and-invariant-safety.md))
- **[ddd-evans/10] Repositories for persistence ignorance** - a collection-like
  interface, defined in the domain layer and implemented in infrastructure, for
  loading and saving whole aggregates by identity.
  ([lesson](lessons/10-repositories-for-persistence-ignorance.md))
- **[ddd-evans/11] Associations and model navigation trade-offs** - every stored,
  navigable reference is a coupling cost; prefer unidirectional, qualified
  associations, and promote a relationship to its own entity when it starts carrying
  its own data.
  ([lesson](lessons/11-associations-and-model-navigation-trade-offs.md))

## Supple design and distillation

- **[ddd-evans/12] Supple design for expressive and malleable models** - a cluster of
  mutually reinforcing techniques (intention-revealing interfaces, side-effect-free
  functions, explicit assertions, conceptual contours, standalone classes, closure of
  operations) that make a correct model also easy to understand and safe to change.
  ([lesson](lessons/12-supple-design-for-expressive-and-malleable-models.md))
- **[ddd-evans/13] Distillation: core domain and generic subdomains** - not every part
  of the system deserves equal investment; identify the small core domain that
  actually differentiates the business and protect it, buy or minimally build the
  generic rest.
  ([lesson](lessons/13-distillation-core-domain-and-generic-subdomains.md))

## Strategic design across contexts

- **[ddd-evans/14] Bounded contexts and explicit model boundaries** - one model and
  one language hold consistently only within an explicit boundary; the same word can
  and should mean different things in different contexts, with deliberate translation
  at the seams. ([lesson](lessons/14-bounded-contexts-and-explicit-model-boundaries.md))
- **[ddd-evans/15] Context mapping and anti-corruption boundaries** - document how
  bounded contexts actually relate (partnership, conformist, customer/supplier, open
  host service, ...); build an anti-corruption layer to protect a downstream model
  from an upstream model you don't control.
  ([lesson](lessons/15-context-mapping-and-anti-corruption-boundaries.md))
- **[ddd-evans/16] Large-scale structure and continuous model refactoring** - a
  lightweight, shared vocabulary for orienting across many bounded contexts, discovered
  from well-understood contexts rather than imposed upfront; models at every scale are
  hypotheses, continuously revised as domain insight deepens.
  ([lesson](lessons/16-large-scale-structure-and-continuous-model-refactoring.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
