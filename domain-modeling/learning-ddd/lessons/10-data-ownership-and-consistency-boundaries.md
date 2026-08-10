---
id: learning-ddd/10
subject: learning-ddd
title: Data ownership and consistency boundaries
slug: data-ownership-and-consistency-boundaries
status: drafted
mastery:
seniority: senior
source: Learning Domain-Driven Design (Vlad Khononov), Part II, Chapter 6 (continued) and Part III, Chapter 10 - "Data Ownership Patterns"
prerequisites: [learning-ddd/08, learning-ddd/03]
created: 2026-08-10
updated: 2026-08-10
---

# Data ownership and consistency boundaries

## TL;DR
Every piece of data should have exactly one bounded context that **owns** it - the only place allowed to change it directly - and every other context that needs that data holds a deliberately-chosen, explicitly out-of-date **copy**, kept fresh through one of a small set of well-understood data-ownership patterns, rather than reaching directly into another context's database. Consistency (whether two pieces of data must always agree instantly, or can briefly diverge) is a design decision made per relationship, not an accident of how the database happens to be structured.

## The idea
`learning-ddd/08` established that a single aggregate is the transactional-consistency boundary within a bounded context. This lesson extends that question across bounded-context boundaries (`learning-ddd/03`): when a Pricing context needs to know a product's current inventory level to decide whether to show a "low stock" surge price, does it need that number to be perfectly, instantly accurate, or is "accurate as of a few seconds ago" good enough? The honest answer, for the overwhelming majority of cross-context data needs, is the latter - and pretending otherwise (e.g., having Pricing query Inventory's live database directly, in the request path, "just to be safe") creates a tight coupling that defeats the entire purpose of drawing the bounded-context boundary in the first place: Inventory can no longer change its schema or scale independently without breaking Pricing.

Khononov frames the resulting design choice as: pick, deliberately, per cross-context data dependency, whether it needs to be **strongly consistent** (instantly, always agreeing - genuinely rare and expensive across a network boundary) or **eventually consistent** (allowed to lag briefly, reconciled via the mechanisms below) - and then choose an explicit ownership pattern to implement that choice, rather than letting direct database access or ad hoc synchronous calls make the decision by default.

## How it works

### Single ownership, many consumers
Exactly one bounded context is the **system of record** for any given piece of data - the only place with write access. Every other context that needs it gets a read-only, intentionally-lagging copy. This single rule prevents the classic distributed-systems failure mode of two services both being able to write "the truth" about the same fact and silently disagreeing.

### Pattern: Data replication via domain events
The owning context publishes domain events (`learning-ddd/09`) whenever the owned data changes; consuming contexts subscribe and maintain their own local, denormalized copy shaped exactly for their own needs.

**Worked example - e-commerce.** Inventory owns stock-level data. When stock changes, Inventory publishes a `StockLevelChanged` event. Pricing subscribes and maintains its own tiny local cache (`productId -> approximateStockLevel`) used only to decide whether to apply surge pricing - it does not need Inventory's full warehouse-location, reorder-threshold, or supplier data, so its local copy is deliberately narrower than Inventory's own model, shaped for Pricing's specific need. If Inventory's event delivery lags by a few seconds during a traffic spike, Pricing's surge-pricing decision is very slightly stale - an entirely acceptable trade-off, since "stock level for pricing purposes" was never a strong-consistency requirement in the first place (compare this to a genuine strong-consistency need, like "don't sell more units than physically exist," which belongs *inside* Inventory's own aggregate boundary per `learning-ddd/08`, not delegated to a lagging copy elsewhere).

### Pattern: Request-response synchronous query, with the owning context always as the source of truth
Instead of replicating data, a consuming context calls the owning context's API directly, in real time, whenever it needs the current value, and never persists its own copy. Appropriate when the need is infrequent, staleness truly cannot be tolerated even briefly, or maintaining a replicated copy isn't worth the engineering cost for how rarely the data is needed.

**Worked example - SaaS billing.** When generating an invoice, Billing calls Subscription Management's API synchronously to fetch the exact plan and price in effect *at that instant*, rather than maintaining its own replicated copy of every subscription's plan history - invoice generation is infrequent enough (once per billing period per customer) and consistency-sensitive enough (a stale plan price on an invoice is a real billing error) that a direct, synchronous call, accepting the coupling and availability dependency it creates, is the right trade-off here. This is `learning-ddd/04`'s Customer-Supplier or Open Host Service relationship playing out at the data layer.

### Pattern: Saga / process manager for coordinated writes across owners
When a single business process needs to update data owned by multiple different contexts, and those updates must all happen or none should (or partial completion needs explicit compensating action), a saga coordinates the sequence of local transactions, each owned by its respective context, with compensating actions if a later step fails.

**Worked example - logistics.** "Cancel Shipment" needs to: release reserved vehicle capacity (owned by Fleet/Route Planning), refund the customer (owned by Billing), and notify the customer (owned by Notifications). No single context owns all three pieces of data, and there is no single database transaction that could span all three services anyway. A saga issues each step as its own local transaction against its owning context, and if, say, the refund step fails, a compensating action (re-reserve the capacity, since the cancellation is now only partially complete) runs rather than leaving the system in a silently inconsistent state.

### Anti-pattern: shared database access across bounded contexts
The most common violation of this lesson's core rule: two contexts reading (or worse, writing) the same underlying database tables directly, bypassing the owning context's API and domain model entirely. This silently recreates the "one shared model" problem `learning-ddd/03` exists to solve - any schema change the owning context wants to make now risks breaking a consumer that was never a declared dependency, because the dependency lives in an undocumented shared table rather than an explicit contract.

## Pros
- Makes staleness (or its absence) an explicit, reviewable design decision instead of an accidental property of whatever database structure happened to exist.
- Preserves bounded-context autonomy (`learning-ddd/03`) in practice, not just on paper - an owning context can genuinely change its internal schema without a cross-team migration project, as long as its published event/API contract stays stable.
- Lets each consuming context shape its local copy of foreign data exactly to its own needs (Pricing's tiny stock-level cache versus Inventory's full warehouse model), rather than everyone being forced to work with one generic shared representation.
- Sagas give a principled way to handle multi-context business processes without pretending a distributed transaction is possible or desirable.

## Cons
- Eventual consistency is a genuine cognitive shift for teams used to relational-database strong consistency everywhere - engineers must reason about "what could a user see during the lag window" for every replicated read, which is easy to get wrong on a first pass.
- Replicated copies mean the same fact exists in multiple places; without careful event-delivery guarantees (`learning-ddd/11`'s outbox pattern and idempotent consumers) copies can drift permanently out of sync rather than just briefly lag.
- Sagas add real implementation complexity (compensating actions, partial-failure handling, often a dedicated orchestration mechanism) compared to a single ACID transaction - justified only when data ownership genuinely spans contexts.
- Deciding which relationships need strong versus eventual consistency requires real domain judgment; getting it wrong in the "should have been strong" direction produces subtle correctness bugs that only show up under specific timing/load conditions, which are notoriously hard to reproduce and debug.

## Alternatives
- **A single shared database for the whole system, with all services reading/writing directly** - eliminates the ownership question entirely by making everything trivially "strongly consistent," but is exactly the anti-pattern this lesson warns against: it destroys context autonomy and reintroduces cross-team coupling at the schema level.
- **Distributed transactions (two-phase commit) across services** - theoretically preserves strong consistency across context boundaries, but is operationally fragile, poorly supported by most modern infrastructure, and blocks/locks across services in a way that undermines the availability and autonomy benefits bounded contexts were meant to provide; sagas are almost always the better-fitting alternative in practice.
- **CQRS's read-model replication** (`learning-ddd/12`) - a specific, common application of the "data replication via domain events" pattern above, focused on building purpose-shaped read models; complementary to, not distinct from, this lesson's data-ownership thinking.

## When to use it
Apply explicit data-ownership design at every bounded-context boundary (`learning-ddd/03`, `learning-ddd/04`) where one context needs data that another owns - which is nearly every non-trivial multi-context system. Decide strong-versus-eventual consistency deliberately, per relationship, based on the real cost of staleness for that specific use case.

## When NOT to use it
Within a single bounded context, this lesson does not apply directly - internal data ownership there is handled by aggregate boundaries (`learning-ddd/08`) and normal transactional consistency, not by the cross-context replication patterns above. Also don't reach for a saga for a process that's actually contained within one context's aggregate - that's over-engineering a problem `learning-ddd/08`'s aggregate design already solves more simply.

## Key takeaways / mental model
For every piece of data a context needs but doesn't own, ask: "if this were five seconds stale, would that cause real business harm?" If no (the overwhelming majority of cases), replicate it via domain events and accept the lag. If yes, call the owner synchronously and accept the availability coupling. Never let a context write data it doesn't own, and never let two contexts silently disagree about who owns a given fact.

## Self-check questions
1. Pick a piece of data that flows between two parts of a system you know. Which context owns it? Is the current mechanism for the other side to access it explicit (an API or event) or implicit (shared database access)?
2. Explain why "Pricing needs Inventory's stock level" is usually an eventual-consistency relationship, while "Billing needs the exact plan price for an invoice" is more often a strong-consistency one. What's the distinguishing factor?
3. Why can't a single ACID database transaction solve the "Cancel Shipment" saga example across Fleet, Billing, and Notifications? What would a naive attempt to force it look like, and why would it fail in practice?
4. What early warning signs would tell you two bounded contexts are sharing a database table directly rather than respecting ownership boundaries?

## References
- Learning Domain-Driven Design (Vlad Khononov), Part III, Chapter 10: "Data Ownership Patterns".
- Domain-Driven Design (Eric Evans, 2003) - see `domain-modeling/ddd-evans` for the underlying bounded-context autonomy rationale.
