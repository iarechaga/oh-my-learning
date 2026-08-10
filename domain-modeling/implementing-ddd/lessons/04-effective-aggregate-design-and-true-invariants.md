---
id: implementing-ddd/04
subject: implementing-ddd
title: Effective aggregate design and true invariants
slug: effective-aggregate-design-and-true-invariants
status: drafted
mastery:
seniority: senior
source: Implementing Domain-Driven Design (Vaughn Vernon), Chapter 10: Aggregates
prerequisites: [implementing-ddd/02]
created: 2026-08-10
updated: 2026-08-10
---

# Effective aggregate design and true invariants

## TL;DR
An aggregate is a consistency boundary, not a convenience grouping — Vernon distills aggregate design to four rules: model true invariants inside boundaries, design small aggregates, reference other aggregates by identity only, and update one aggregate per transaction; violating any of these produces either data corruption under concurrency or performance/scalability problems that only surface under real load.

## The idea
Evans introduces the aggregate as a cluster of entities and value objects treated as a single unit for data changes, with one member designated the aggregate root that's the only object outside code is allowed to hold a reference to (see `ddd-evans`). What Evans doesn't spell out in operational detail is *how big an aggregate should be* — and this is the single most common tactical DDD mistake in practice: teams build large, deeply nested aggregates (an `Order` aggregate that contains every `LineItem`, every `Shipment`, every `Payment`, all loaded and locked together) because it feels natural to group "everything related to an order" into one object graph. Vernon's chapter exists specifically to correct this instinct, arguing from first principles that aggregate boundaries should be as small as possible — ideally a single entity — and that "related" is not the same as "must be transactionally consistent together."

The core distinction the chapter turns on is **true invariants vs. eventual consistency**. A true invariant is a business rule that must never be violated, even for an instant, within a single transaction (e.g. "an order's total must equal the sum of its line items at every point in time within one transaction"). Anything that can tolerate being briefly out of sync — updated a moment later, in a separate transaction — is not a true invariant and does not need to live inside the same aggregate boundary.

## How it works

### Rule 1 — Model true invariants, and only true invariants, inside the boundary
Ask, for every piece of data you're tempted to include in an aggregate: "if this were updated a second later, in a separate transaction, would the business consider that an error?" If yes, it's a true invariant and belongs inside the boundary. If the honest answer is "that would be fine, we'd just want it to happen soon," it doesn't need transactional consistency with the rest — it can be eventually consistent (`implementing-ddd/06`).

**Worked example — order fulfillment.** A tempting design: one `Order` aggregate containing the full list of `LineItem`s and the running `total`. The true invariant here is real: the `total` must always equal the sum of the current line items' amounts — you cannot allow a reader to observe a partially-updated total. So `LineItem`s and `total` stay inside the `Order` aggregate boundary together. But now consider adding `Shipment` tracking to the same aggregate — is "the order's shipment status is instantly consistent with the order's line items" a true invariant? Almost never: a warehouse system updating shipment status operates on its own timeline, and the business tolerates a shipment status lagging by seconds without considering it an error. `Shipment` belongs in its own aggregate, referenced from `Order` by identity only (Rule 3), kept in sync via domain events (`implementing-ddd/07`) and eventual consistency.

### Rule 2 — Design small aggregates
Smaller aggregates mean: less data loaded per transaction, shorter-held locks, fewer concurrent-modification conflicts (two users editing different parts of what used to be one giant aggregate no longer collide), and better horizontal scalability, since each aggregate instance is a smaller, more independently-shardable unit of consistency. Vernon's guidance is aggressive: default to a single entity as the aggregate root with no child entities at all, and only add complexity (a child entity, a value-object collection) when a true invariant genuinely demands it.

**Worked example — a forum/collaboration tool.** A `Discussion` aggregate that includes every `Comment` as a child entity inside its boundary means loading the entire comment history to post a single new discussion-level edit, and means two users commenting simultaneously on the same discussion collide on the same aggregate lock even though their comments don't actually conflict with each other. The fix: make `Comment` its own aggregate root, referencing its parent `Discussion` by `DiscussionId` only. The true invariant "a comment must belong to an existing, non-deleted discussion" is enforced at comment-creation time (checking the discussion exists) rather than by nesting comments physically inside the discussion's consistency boundary.

### Rule 3 — Reference other aggregates by identity, not by object reference
An aggregate should hold only the identity (e.g. `CustomerId`, not a `Customer` object reference) of any other aggregate it relates to. This is covered in depth in `implementing-ddd/05` — the short version here is that holding an object reference tempts you to navigate across the reference and modify the other aggregate within the same transaction, silently widening your consistency boundary back to the large-aggregate problem Rule 2 exists to avoid.

### Rule 4 — Use eventual consistency outside the boundary, one aggregate per transaction
A single application service operation (`implementing-ddd/09`) should modify exactly one aggregate instance per transaction. If a use case seems to require modifying two aggregates atomically, that's a signal either that the aggregate boundary is drawn wrong (the two "aggregates" actually share a true invariant and should be one aggregate), or that the second update should happen asynchronously via a domain event, tolerating brief inconsistency (`implementing-ddd/06`, `implementing-ddd/07`).

**Worked example — banking.** Transferring funds between two `Account` aggregates looks like it needs one atomic transaction touching both. Applying Rule 4: the transfer happens as two separate transactions — withdraw from the source account (raising a `FundsWithdrawn` domain event), then, driven by that event, deposit into the destination account in a second transaction. Between the two transactions there is a real (very brief) window where money has left one account and not yet arrived in the other — the design has to accept that window and build compensating logic (a saga, `implementing-ddd/15`) for the case where the second step fails.

## Pros
- Small, correctly-bounded aggregates dramatically reduce concurrent-modification conflicts (optimistic concurrency failures) because unrelated changes no longer compete for the same lock or version number.
- Loading and persisting less data per transaction improves latency and reduces the blast radius of any single operation, which matters directly for scalability under load.
- Forces an explicit, examined answer to "what must actually be atomic here?" — a question many designs never ask, defaulting instead to "everything that seems related should be one transaction," which is usually wrong.

## Cons
- Small aggregates push more logic out to eventual consistency and domain events, which is a genuine increase in design and operational complexity (message delivery guarantees, ordering, idempotency — see `implementing-ddd/06`, `implementing-ddd/12`) compared to a single ACID transaction.
- Determining what is and isn't a "true" invariant requires real domain conversation and judgment; getting it wrong in the direction of too-small aggregates means a genuine business rule can be silently violated (a race condition slips through a boundary that should have enforced it atomically).
- Existing systems built around large, ORM-convenient aggregates (with cascading loads and saves across an entire object graph) require significant, risky refactoring to adopt this discipline — it's much cheaper to get right from the start than to retrofit.

## Alternatives
- **Large, richly-nested aggregates ("aggregate as object graph")** — group everything intuitively "related" into one root; simpler to reason about for small systems with low concurrency, but the approach this lesson explicitly argues against for anything with real concurrent load or complex object graphs.
- **No aggregates, table-per-entity CRUD** — skip the consistency-boundary concept entirely and let each entity persist and update independently, relying on database-level foreign key constraints for referential integrity; adequate for a generic/supporting subdomain (per `implementing-ddd/01`) with minimal true invariants, but insufficient wherever cross-entity business rules must hold atomically.
- **Event-sourced aggregates** — instead of persisting current state, persist the aggregate as a stream of events and derive current state by replay; complementary to (not a replacement for) small aggregate boundaries — see `implementing-ddd/13` — but adds its own significant complexity, chosen for audit/replay needs rather than as a default.

## When to use it
For every aggregate in a core domain (per `implementing-ddd/01`'s distillation): explicitly enumerate true invariants before drawing the boundary, default to single-entity aggregates, and push everything else out to eventual consistency via domain events.

## When NOT to use it
Skip the rigor for a generic/supporting subdomain with no meaningful invariants to protect — a simple CRUD entity with database-level constraints is sufficient there, and applying full aggregate design discipline would be over-engineering for no corresponding benefit.

## Key takeaways / mental model
Before including anything inside an aggregate boundary, ask: "if this were updated a moment later, in a separate transaction, would the business actually call that a bug?" If the honest answer is no, it doesn't belong inside — model it as a separate aggregate, connected by identity reference and domain events, and let eventual consistency do the work.

## Self-check questions
1. Take an aggregate you've designed or seen (in any codebase) that contains more than one entity type. For each contained entity, ask the "updated a moment later, in a separate transaction — would that be a bug?" question. Does the current boundary still hold up?
2. Explain, in concrete terms, why a large aggregate causes more concurrent-modification conflicts than several small ones covering the same data, even if the total amount of data mutated per unit time is the same.
3. A team insists two aggregates must be updated atomically in one transaction because "the business requires it." How would you probe whether that's a true invariant or a convenience assumption?
4. Why does referencing other aggregates by identity (Rule 3) matter specifically for enforcing Rule 4 (one aggregate per transaction)? What would go wrong if aggregates held direct object references to each other instead?

## References
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 10: "Aggregates".
- Domain-Driven Design (Eric Evans) — the original Aggregate pattern definition; see `ddd-evans`.
