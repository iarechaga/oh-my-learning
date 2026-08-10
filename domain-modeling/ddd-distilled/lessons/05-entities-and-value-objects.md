---
id: ddd-distilled/05
subject: ddd-distilled
title: Entities and value objects
slug: entities-and-value-objects
status: drafted
mastery:
seniority: mid
source: Domain-Driven Design Distilled (Vaughn Vernon), Chapter 5 "Tactical Design with Aggregates" (entities/value objects as building blocks)
prerequisites: [ddd-distilled/01, ddd-distilled/02]
created: 2026-08-10
updated: 2026-08-10
---

# Entities and value objects

## TL;DR
An **entity** is a domain object defined by a persistent identity that continues to
matter across changes to its attributes over time (a specific `Order`, a specific
`Customer`). A **value object** is defined entirely by its attributes, has no identity of
its own, and is treated as interchangeable and immutable (two `Money` objects both
representing "$10 USD" are simply equal, not "the same instance that happens to have the
same value"). Choosing correctly between the two, for every concept in your model, is the
single most consequential tactical modeling decision in DDD — it determines how equality,
mutability, and lifecycle work for that concept throughout the codebase.

## The idea
Most modeling mistakes at the tactical level come from treating everything as an entity
by default — giving every class an ID field and mutable setters, "just in case" — because
that's what ORM tooling and database-table thinking nudge you toward. But most domain
concepts are *not* individually trackable things with a lifecycle; they're descriptive
attributes, measurements, or compound values, and modeling them as entities adds
unnecessary identity-tracking machinery and, worse, unnecessary mutability where
immutability would have prevented bugs.

The entity/value-object distinction answers one question for every concept in your
model: **does this thing's individual identity matter, independent of its current
attribute values, or is it fully described by its attributes?**
- If a `Customer` changes their email address, it's still the *same* customer — identity
  persists across attribute change. Entity.
- If an `Address` changes from "123 Main St" to "456 Oak Ave," that's not the "same
  address with a new value" — it's simply a different address. There's no meaningful
  sense in which the old address "became" the new one. Value object.

This distinction ripples into equality semantics (entities compare by identity/ID; value
objects compare by structural equality of all their attributes), mutability (entities
change over time in place; value objects are typically immutable — "changing" one means
replacing it with a new instance), and lifecycle tracking (entities need to be
individually persisted, looked up by ID, and audited across changes; value objects are
just data carried along inside entities or aggregates, with no independent existence
worth tracking).

## How it works

### Deciding entity vs. value object — the identity test
For each domain concept, ask: **if two instances have identical attributes right now, are
they still meaningfully different things?** If yes (two different `Order`s could
coincidentally have the exact same items, same total, same date — they're still two
different orders because they represent two different real-world purchase events),
identity matters — entity. If no (two `$10 USD` amounts, two `(40.7128, -74.0060)`
coordinates — nothing distinguishes them beyond their attribute values), it's a value
object.

A second, related test: **does it make sense to ask "has this specific one changed over
time?"** You can meaningfully ask "has this Order's status changed since yesterday" —
entity. It doesn't make sense to ask "has this $10 changed since yesterday" — a
`Money` value either represents $10 or it doesn't; if the amount needs to be different,
you construct a new `Money` instance, you don't mutate the old one in place.

### Worked example — a ride-hailing domain
- **`Trip`** — has an identity that persists across its whole lifecycle: requested,
  driver assigned, in progress, completed. Two trips with identical pickup/dropoff and
  fare are still different trips (different riders, different points in time). **Entity.**
  Its identity (`tripId`) is what you use to look it up, update its status, and audit its
  history.
- **`GeoCoordinate` (lat/lng pair)** — two coordinates with the same lat/lng values are
  simply the same location; there's no meaningful sense of "this coordinate instance" as
  opposed to another with identical values. **Value object**, immutable, compared by
  value.
- **`FareBreakdown` (base fare + surge multiplier + tolls + tip)** — fully described by
  its component amounts; recomputing a fare produces a *new* `FareBreakdown`, it doesn't
  mutate the old one (which matters for auditability — you want to know what the fare
  breakdown *was* at trip-completion time, immutably, not have it silently changed
  later). **Value object.**
- **`Driver`** — persists identity across trips, rating changes, vehicle changes over
  years of driving for the platform. **Entity.**
- **`VehicleDescription` (make, model, year, color)** — if two drivers happen to drive
  identical vehicles (same make/model/year/color), the descriptions are simply equal;
  there's no "this vehicle description instance" identity distinct from its values.
  **Value object** — though note the *actual physical vehicle*, if the domain needed to
  track individual vehicles (e.g., for a fleet-management context with maintenance
  history per physical car), would itself be an entity with its own identity (VIN). The
  same real-world "thing" can be modeled as a value object in one bounded context and an
  entity in another, depending on what that context actually needs to track — this is a
  direct consequence of bounded contexts having independent models (`ddd-distilled/03`).

### Worked example — a subtle case: is `EmailAddress` an entity or a value object?
A common point of confusion: `EmailAddress` looks like it "identifies" a person, so
learners sometimes reach for entity. But test it against the two questions above: does a
specific `EmailAddress` instance have a lifecycle independent of its string value? No —
"alice@example.com" is just that string; if Alice changes her email, the old
`EmailAddress` doesn't "become" the new one, it's replaced. Two `EmailAddress` value
objects holding the same string are simply equal. `EmailAddress` is a **value object**
— what actually has identity here is the `Customer` (or `Account`) entity that *holds* an
`EmailAddress` as one of its attributes, and can have that attribute value replaced over
time while the customer's own identity persists.

### Encapsulating validation and behavior in value objects
A well-modeled value object isn't just a data bag — it enforces its own invariants at
construction (an `EmailAddress` value object can validate the format in its constructor
so that an invalid email can never exist as a value in the system) and can carry
behavior relevant to itself (a `Money` value object can expose `add()`, `multiply()`,
with currency-mismatch checks built in, rather than scattering that arithmetic logic
across every place `Money` is used). This is what distinguishes a rich value object from
a plain struct/DTO — see `software-engineering/clean-code` (`clean-code/06`) on the
general objects-vs-data-structures distinction, which this specializes for the domain
layer.

### Entities and identity stability
An entity's identity must be stable and unambiguous for its entire lifecycle — usually a
generated ID (UUID, sequence) rather than a "natural" identifier that might itself change
(don't use email address as a `Customer`'s identity if customers are allowed to change
their email — that would make the identity mutable, defeating the point). Entities
compare by identity, not by attributes: two `Customer` objects with the same identity are
"the same customer" even if one is a stale in-memory copy with outdated attribute values
— this matters directly for aggregate design in `ddd-distilled/06`.

## Pros
- Immutable value objects eliminate an entire class of bugs caused by unexpected shared
  mutable state (two parts of the code holding the same `Money` reference, one mutating
  it, the other silently seeing a changed value it didn't expect).
- Value objects with self-validating constructors make invalid states unrepresentable —
  once you have an `EmailAddress` instance, you know it's valid, everywhere, without
  re-validating.
- Getting the entity/value-object split right dramatically simplifies equality logic,
  persistence mapping, and reasoning about "what changed" during debugging.
- Value objects are naturally easy to test (pure, deterministic, no hidden identity or
  mutable state) and easy to reuse across entities.

## Cons
- Overusing entities (giving everything an ID and mutable setters) is the default failure
  mode most ORMs and database-first thinking nudge you toward, and it's easy to fall into
  without deliberate attention.
- Modeling something as a value object when the domain actually needs to track its
  individual lifecycle (the vehicle-fleet counter-example above) loses real information
  and forces awkward workarounds later.
- Immutability requires "replace, don't mutate" discipline throughout the codebase,
  which can feel unfamiliar or verbose to developers used to setter-heavy objects,
  especially in languages without strong value-type/record support.
- Persistence frameworks (traditional ORMs) sometimes model everything as identity-bearing
  rows by default, requiring extra configuration (embedded/composite value types) to
  correctly persist value objects without accidentally giving them their own identity
  column.

## Alternatives
- **Anemic data objects / DTOs for everything** — simpler initially (no need to reason
  about identity vs. value at all) but pushes all validation and behavior out into
  service classes, producing the "objects vs. data structures" hybrid antipattern
  described in `software-engineering/clean-code` (`clean-code/06`) — worst of both
  worlds if done by accident rather than deliberately.
- **Primitive obsession** (using raw strings/numbers instead of value objects — `string`
  for email, `decimal` for money) — the default in many codebases; loses
  self-validation and type safety, and makes it easy to accidentally pass a `customerId`
  where an `orderId` was expected since both are "just strings."
  Value objects are the direct fix for primitive obsession in domain code.
- **Records / structs in languages with first-class support** (Java records, Kotlin data
  classes, C# records, Python dataclasses with `frozen=True`) — a good language-level
  starting point for value objects, though the domain still needs deliberate validation
  logic added on top of the language feature's free equality/immutability.

## When to use it
Apply the entity/value-object distinction to every domain concept inside a bounded
context you're modeling deliberately (i.e., inside your core or carefully-modeled
supporting subdomains, per `ddd-distilled/04`) — this is foundational tactical modeling
work that everything else (aggregates in `ddd-distilled/06`, repositories in
`ddd-distilled/07`, domain events in `ddd-distilled/08`) builds on.

## When NOT to use it
For generic/throwaway subdomains or simple CRUD screens with no real domain rules, this
level of rigor is usually unnecessary ceremony — plain data classes are fine. Also don't
force a value object's immutability onto a concept the domain genuinely needs to track
individually over time (don't make `Order` a value object just because it "feels
data-like" — it has a real lifecycle and identity that matters).

## Key takeaways / mental model
For every domain concept, ask: "if I have two instances with identical current
attributes, are they still meaningfully two different things?" Yes -> entity, model
identity, allow controlled mutation over time, compare by ID. No -> value object, make it
immutable, compare by value, let "changing" it mean constructing a new instance. Get this
right first — it's the foundation every other tactical pattern in this subject builds on.

## Self-check questions
1. For a `SubscriptionPlan` in a SaaS billing system (name, price, billing interval),
   would you model it as an entity or a value object? What would make you reconsider?
2. Explain why `EmailAddress` is normally a value object even though it "looks like" an
   identifier. What entity actually needs identity in that scenario?
3. Give an example (from the lesson or your own experience) of the same real-world
   concept being correctly modeled as an entity in one bounded context and a value object
   in another. Why isn't that a contradiction?
4. What concrete bug can arise from treating a value object as mutable and sharing a
   reference to it across two entities? Walk through a specific scenario.
5. Why does an entity need a stable, non-changing identity field, and what goes wrong if
   you pick a "natural" identifier that the entity can later change (e.g., email as ID)?

## References
- Domain-Driven Design Distilled (Vaughn Vernon), Chapter 5: "Tactical Design with
  Aggregates" (entities and value objects as the foundational building blocks discussed
  before aggregate composition).
- For the objects-vs-data-structures distinction this specializes, see
  `software-engineering/clean-code` (`clean-code/06`).
- For deeper tactical-pattern treatment and more worked examples, see
  `domain-modeling/ddd-evans` and `domain-modeling/implementing-ddd`.
