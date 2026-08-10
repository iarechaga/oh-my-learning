---
id: learning-ddd/08
subject: learning-ddd
title: Aggregates and invariants in tactical design
slug: aggregates-and-invariants-in-tactical-design
status: drafted
mastery:
seniority: senior
source: Learning Domain-Driven Design (Vlad Khononov), Part II, Chapter 6 (continued) - "Aggregates"
prerequisites: [learning-ddd/07]
created: 2026-08-10
updated: 2026-08-10
---

# Aggregates and invariants in tactical design

## TL;DR
An aggregate is a cluster of domain objects treated as a single consistency unit: it has one designated **root** entity through which all external access happens, and every business rule (invariant) that must hold *at all times* is enforced inside the aggregate's boundary, in a single transaction. Aggregate boundaries should be drawn as small as possible while still containing everything a true invariant needs - not around "everything related," which is the single most common tactical-design mistake in DDD.

## The idea
`learning-ddd/07` established that a Domain Model enforces invariants by making illegal states unrepresentable through an object's own API. Aggregates answer the next question: *which objects, exactly, need to be modified together, atomically, to keep an invariant true?* An invariant is a rule that must never be violated, even momentarily - "an order's total must equal the sum of its line items," "a subscription cannot have two overlapping billing periods," "a bank account's balance must never go negative." If enforcing a rule requires reading and possibly changing more than one object in the same transaction, those objects belong in the same aggregate. If two objects merely *reference* each other but no invariant requires them to change together atomically, they belong in **separate** aggregates, connected only by identifier reference (not object reference).

The aggregate's **root** is the single entity that all outside code interacts with; every other object inside the boundary is only reachable through the root, and the root is responsible for enforcing every invariant on any change. This is what makes "illegal states unrepresentable" actually true in practice: there is no back door that lets external code mutate an internal object directly and bypass the root's checks.

## How it works

### The core question: what must be transactionally consistent, right now?
For every candidate rule, ask: "if this rule were violated for even a moment, would that cause real business harm, or could the system self-correct shortly after via a separate process?" Rules in the first category are true invariants and define aggregate boundaries. Rules in the second category can be enforced **eventually** (across aggregates, often via domain events - `learning-ddd/09`), not within one transaction.

### Worked example - e-commerce: Order and OrderLineItems as one aggregate
An Order's total must always equal the sum of its line items' (price * quantity), and an order must always have at least one line item once placed. These are true, must-hold-instantly invariants: if a bug ever let the stored total drift from the sum of line items, that's a direct financial-correctness bug. So `Order` is the aggregate root, and `OrderLineItem` objects live inside its boundary, only reachable and mutable through methods on `Order` (`order.addLineItem(...)`, `order.removeLineItem(...)`), each of which recalculates and re-validates the total before returning. No code anywhere is allowed to reach into an `OrderLineItem` and change its quantity directly without going through `Order`.

### Worked example - e-commerce: Order and Customer are separate aggregates
It might seem natural to nest `Customer` inside `Order` (an order "belongs to" a customer), but there is no invariant requiring an order and its customer's other data (address book, loyalty tier, order history) to be transactionally consistent with each other *at the instant either changes*. A customer updating their shipping address does not need to happen in the same transaction as placing an order. So `Order` references `Customer` only by `customerId` (an identifier), not by holding a live `Customer` object inside its boundary - keeping the `Order` aggregate small, and letting `Customer` be modified independently without any risk of lock contention or unrelated invariant checks blocking either operation.

### Worked example - SaaS billing: why "the whole Subscription plus every past Invoice" is the wrong aggregate boundary
A tempting first design nests every historical `Invoice` inside the `Subscription` aggregate, reasoning "invoices belong to a subscription." But no invariant requires a subscription and its entire invoice history to be loaded and locked together for every operation - upgrading a plan doesn't need to touch past invoices at all, and generating a new invoice doesn't need to re-validate every prior one. Bundling them creates a needlessly large aggregate: every write to the subscription now contends for a lock that also blocks reads of invoice history, and loading the aggregate for a simple plan-name change pulls in years of invoice records. The corrected design: `Subscription` is its own small aggregate (current plan, status, current billing period - the things that genuinely have instant, must-hold invariants together), and each `Invoice` is its **own** aggregate, referencing `subscriptionId` by identifier. The rule "an invoice's line items must sum to its total" is a true invariant *within* the Invoice aggregate; the relationship between a subscription and its invoices does not need transactional consistency, only eventual consistency (`learning-ddd/10`), typically established by a domain event ("Billing Period Ended") that triggers invoice generation as a separate transaction.

### Worked example - logistics: Shipment aggregate boundary around capacity
A `Vehicle`'s cargo capacity must never be exceeded by the sum of `Shipment`s assigned to it at any given moment - a true, instant invariant (a truck literally cannot carry more than its physical capacity). So capacity-checking logic lives inside a `VehicleLoad` aggregate (root: the vehicle's current load manifest) that owns the invariant "sum of assigned shipment weights <= vehicle capacity," and every shipment-assignment operation goes through this aggregate's root, which re-checks the invariant before committing. Route-optimization details (traffic, ETA calculation) do *not* need to be inside this same transactional boundary - they can be recalculated separately, asynchronously, without threatening the one true invariant (capacity) that must never be violated even momentarily.

### Sizing the boundary: the "small aggregates" heuristic
Khononov (echoing Vernon's "effective aggregate design" guidance) recommends aggregates be as small as possible: prefer referencing other aggregates by ID over nesting them, prefer eventual consistency (via domain events, `learning-ddd/09`) between aggregates over trying to cram everything that's merely *related* into one transactional boundary. Large aggregates cause real, measurable problems: more lock contention (two unrelated operations on "the same" giant aggregate block each other), larger objects to load into memory for even trivial operations, and - most insidiously - a false sense that everything inside the boundary is somehow "safer" together, when in fact most of what's been bundled in didn't need to be.

## Pros
- Gives a concrete, testable definition of a transactional/consistency boundary, replacing vague intuitions like "these classes are related" with the precise question "does an invariant require these to change together, atomically?"
- Prevents the two most common tactical-design failures at once: invariant violations from boundaries drawn too small (a rule spans two separate aggregates and is enforced inconsistently or not at all), and performance/contention problems from boundaries drawn too large.
- Makes concurrency reasoning tractable: a repository (`learning-ddd/08`'s Domain Model partner) loads and saves one aggregate per transaction, so "can two operations conflict" reduces to "do they touch the same aggregate instance."
- Sets up `learning-ddd/09` and `learning-ddd/10` cleanly: cross-aggregate coordination becomes an explicit, deliberate domain-event-driven or eventually-consistent design decision, not an accident of a too-large boundary.

## Cons
- Genuinely hard to get right on a first pass - teams new to DDD very commonly draw aggregates too large ("everything related to an Order") out of a reasonable-seeming but mistaken instinct that relatedness implies transactional necessity.
- Small aggregates push more coordination logic into cross-aggregate, eventually-consistent territory, which requires understanding domain events (`learning-ddd/09`) and accepting that some rules are enforced slightly after the fact rather than instantly - a genuine mental-model shift for teams used to relational-database-style immediate consistency everywhere.
- Redrawing an aggregate boundary after a system has grown around the wrong one is expensive - it usually means a real data-migration and API-contract change, not just a refactor.
- Requires a fairly precise understanding of the actual business invariants, which in turn depends on the ubiquitous-language and event-storming work (`learning-ddd/05`, `learning-ddd/06`) having already surfaced them accurately.

## Alternatives
- **No explicit aggregate boundaries, ad hoc transaction scripts that touch whatever data they need** - simpler for genuinely simple subdomains (pairs with Transaction Script or Active Record from `learning-ddd/07`), but reintroduces scattered, inconsistent invariant enforcement for anything with real cross-object rules.
- **Database-enforced constraints (foreign keys, check constraints, triggers) as the primary invariant mechanism** - can enforce some invariants (uniqueness, referential integrity) without any aggregate design at all, but cannot express most non-trivial business rules (proration math, capacity limits computed across several fields) and pushes business logic into the database layer, away from the ubiquitous-language-driven domain model.
- **Sagas / process managers** for invariants that genuinely span multiple aggregates and must eventually be reconciled - not an alternative to aggregate design so much as the complementary mechanism for the cross-aggregate coordination that small, well-drawn aggregates deliberately push outside any single transaction; connects to `learning-ddd/09` and `learning-ddd/11`.
- **`ddd-evans`'s original Aggregate pattern** - Evans introduced the term and the root/boundary concept; Khononov's treatment leans more heavily on the "prefer small aggregates, reference by ID" guidance popularized by Vernon's "Effective Aggregate Design" work, reflected also in `domain-modeling/implementing-ddd`.

## When to use it
Design explicit aggregates for any Domain Model (`learning-ddd/07`) in a core or complexity-justified supporting subdomain where real invariants exist that must hold atomically across more than one object. This is tactical design work that follows naturally once event storming (`learning-ddd/06`) has surfaced the process and its rules.

## When NOT to use it
Don't introduce formal aggregate boundaries for logic already correctly handled by Transaction Script or simple Active Record (`learning-ddd/07`) - if there's no true cross-object invariant, there's no aggregate design decision to make. Also resist the urge to model every "this belongs to that" relationship as an aggregate-nesting decision; most such relationships are just references, not transactional-consistency requirements.

## Key takeaways / mental model
For every pair of objects you're tempted to put in the same aggregate, ask: "if these two changed in separate transactions, milliseconds apart, could the system ever be observed in a state that violates a real business rule?" If yes, they must be in the same aggregate. If no - if the worst case is a brief, tolerable staleness - they belong in separate aggregates, connected by ID reference and reconciled eventually, typically via a domain event (`learning-ddd/09`).

## Self-check questions
1. Take an aggregate (or "big related object cluster") from a system you've built. Identify one true invariant it protects, and one piece of data inside it that doesn't actually need to be there because no invariant requires it.
2. Explain, using the Order/Customer example, why referencing by ID rather than nesting is the right call even though "an order belongs to a customer" sounds like a strong relationship.
3. Why does Khononov (and Vernon before him) recommend aggregates be as small as possible, given that small aggregates push more work into eventual consistency?
4. Describe a scenario where drawing an aggregate boundary too large caused a real operational problem (lock contention, unnecessary loading, or similar) - even if hypothetical, reason through the mechanism.

## References
- Learning Domain-Driven Design (Vlad Khononov), Part II, Chapter 6: "Aggregates".
- Domain-Driven Design (Eric Evans, 2003), Chapter 6, "The Life Cycle of a Domain Object" - original Aggregate pattern, see `domain-modeling/ddd-evans`.
- Implementing Domain-Driven Design (Vaughn Vernon), "Effective Aggregate Design" - see `domain-modeling/implementing-ddd`.
