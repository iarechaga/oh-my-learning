---
id: implementing-ddd/06
subject: implementing-ddd
title: Eventual consistency around aggregate boundaries
slug: eventual-consistency-around-aggregate-boundaries
status: drafted
mastery:
seniority: senior
source: Implementing Domain-Driven Design (Vaughn Vernon), Chapter 4 (Architecture) and Chapter 10 (Aggregates) — eventual consistency
prerequisites: [implementing-ddd/04, implementing-ddd/05]
created: 2026-08-10
updated: 2026-08-10
---

# Eventual consistency around aggregate boundaries

## TL;DR
Once aggregate boundaries are drawn small and correctly (`implementing-ddd/04`), everything outside a single aggregate's boundary is, by construction, eventually consistent rather than transactionally consistent — accepting and designing for that lag (rather than fighting it with distributed transactions) is what makes small-aggregate design actually work in production.

## The idea
Small aggregate design has a direct, unavoidable consequence: if only one aggregate can be modified per transaction, then any business process that touches more than one aggregate necessarily involves a window of time during which the system is in a state the business considers "not yet caught up" but not wrong — the first aggregate has changed, the second hasn't yet. Vernon's treatment of eventual consistency is about naming this honestly and designing for it, rather than reaching for the two most common escape hatches: distributed transactions (two-phase commit across aggregates, which reintroduces the scalability and locking costs small aggregates were meant to avoid) or quietly widening the aggregate boundary back out until everything needed fits in one transaction (which reintroduces the large-aggregate concurrency problems from `implementing-ddd/04`). Eventual consistency is the deliberate third option: accept that some things will be briefly stale, make that staleness bounded and observable, and use domain events (`implementing-ddd/07`) as the mechanism that closes the gap.

## How it works

### Step 1 — Identify the consistency window explicitly
For any process spanning two aggregates, name the window: how long can aggregate B remain unaware of aggregate A's change before it's a business problem? This isn't a vague "eventually" — Vernon pushes teams to get a concrete answer from domain experts (milliseconds, seconds, minutes, hours) because that number drives real engineering decisions (message queue choice, retry policy, whether a synchronous fallback is needed).

**Worked example — order fulfillment.** When an `Order` aggregate transitions to `Placed`, the `Inventory` aggregate for each line item needs to reserve stock. These are separate aggregates (small-aggregate design, `implementing-ddd/04`) — the consistency window here is "how long can inventory remain unaware an order was placed before it's a problem?" For most retail systems, the honest answer is seconds, not milliseconds — a slight delay in stock reservation is tolerable, whereas a two-phase-commit lock held across order placement and inventory reservation would create a scalability bottleneck at checkout for no real business benefit.

### Step 2 — Use domain events to drive the catch-up
The aggregate that changed first raises a domain event (`implementing-ddd/07`) describing what happened (`OrderPlaced`, carrying the order ID and line items). A subscriber — inside the same bounded context or across a context boundary via messaging (`implementing-ddd/12`) — reacts to the event and updates the second aggregate in its own, separate transaction. This is the mechanism, not a side detail: eventual consistency without a reliable event-delivery mechanism just becomes silent, unbounded staleness with no catch-up guarantee at all.

```
// Aggregate 1's transaction
order.place();  // raises OrderPlaced(orderId, lineItems)

// Separate transaction, driven by the event, possibly on a different service
class InventoryReservationHandler {
    void on(OrderPlaced event) {
        for (LineItem item : event.lineItems()) {
            inventoryRepository.findBySku(item.sku()).reserve(item.quantity());
        }
    }
}
```

### Step 3 — Design the UI and API to be honest about the lag
Eventual consistency has to be visible where it matters. If a customer places an order and immediately checks "my orders," the order should already show as placed (that's within the aggregate that changed first). But if the same customer immediately checks stock availability for the same item elsewhere in the catalog, that number might not have decremented yet — an honest UI either tolerates this (most e-commerce systems do, and customers generally don't notice a few seconds of lag) or explicitly signals "processing" for the affected window rather than presenting stale data as if it were current truth.

### Step 4 — Handle failure and idempotency in the catch-up step
Because the second aggregate's update happens in a separate transaction, it can fail independently of the first — the message might be delivered twice (at-least-once delivery is the norm for reliable messaging, see `implementing-ddd/12`), or the handler might crash mid-update. Event handlers that mutate a second aggregate must be idempotent — applying the same `OrderPlaced` event twice must not reserve inventory twice. A common technique: track processed event IDs on the receiving aggregate or in a dedup table, and skip events already applied.

**Worked example — banking (funds transfer).** Withdrawing from `Account A` and depositing to `Account B` (from `implementing-ddd/04`'s example) is eventually consistent by necessity. If the deposit step fails after the withdrawal succeeded, the system is now in an inconsistent state that eventual consistency alone doesn't resolve — this is exactly the scenario a saga or process manager (`implementing-ddd/15`) exists to handle: detecting the failed step and either retrying or issuing a compensating action (crediting the funds back to Account A).

## Pros
- Lets aggregate boundaries stay small (preserving the concurrency and scalability benefits from `implementing-ddd/04`) without resorting to distributed transactions, which don't scale well and reintroduce cross-aggregate locking.
- Matches how most real businesses actually operate — few real-world processes are instantaneously, globally consistent (a warehouse doesn't know about a sale the microsecond it happens either), so eventual consistency is often a more honest model of the domain than forced synchronous consistency.
- Domain events as the consistency mechanism double as an audit trail and an integration point (`implementing-ddd/07`, `implementing-ddd/12`) — the same events that resolve the consistency window are useful for entirely separate purposes (analytics, notifications) essentially for free.

## Cons
- Genuinely harder to reason about than a single ACID transaction — developers have to explicitly think through "what does the system look like during the consistency window," and bugs in that category (users seeing stale or apparently-contradictory data) are notoriously hard to reproduce because they depend on timing.
- Requires reliable, idempotent event handling infrastructure (retries, dead-letter queues, deduplication) that a purely transactional design doesn't need — this is real additional engineering investment, not a free simplification.
- Failure handling across the consistency window (what happens if the second step never completes) requires explicit compensating logic — sagas (`implementing-ddd/15`) — that has no equivalent in a single-transaction design, where the database's own rollback handles failure for free.

## Alternatives
- **Distributed transactions (two-phase commit)** — keep strict, immediate consistency across aggregates using a transaction coordinator; avoids the reasoning complexity of eventual consistency, but at a severe scalability and availability cost (locks held across network calls, coordinator as a single point of failure) that makes it a poor fit for most systems beyond a small scale.
- **Widen the aggregate boundary** — fold the two aggregates back into one so a single transaction suffices; sometimes the right call if a careful re-examination (per `implementing-ddd/04`'s "true invariant" test) reveals the two really do share a true invariant, but wrong if done merely to dodge the discomfort of eventual consistency.
- **Synchronous cross-context calls with compensating rollback** — call the second service synchronously (e.g. an HTTP call to reserve inventory as part of placing an order) and manually roll back the first step if it fails; simpler to trace than an async event flow, but couples the two systems' availability together (if inventory is down, order placement fails too) in a way pure eventual consistency avoids.

## When to use it
Whenever a business process legitimately spans more than one aggregate (which, under Rule 4 from `implementing-ddd/04`, is most cross-aggregate processes) — accept and design explicitly for the consistency window rather than trying to eliminate it.

## When NOT to use it
When the business genuinely requires zero-lag, all-or-nothing consistency across what would otherwise be two aggregates (rare, but real — e.g. certain regulated financial postings), that's often actually a signal the two "aggregates" share a true invariant and should be one aggregate (`implementing-ddd/04`), rather than a case for distributed transactions.

## Key takeaways / mental model
Eventual consistency isn't a bug you tolerate — it's the direct, necessary consequence of small aggregate boundaries, and the question to ask for every cross-aggregate process isn't "how do we avoid this lag" but "how long can this lag safely be, and what closes the gap reliably." Domain events are the answer to the second question.

## Self-check questions
1. Pick a cross-aggregate process you've encountered (in any system). What is the actual acceptable consistency window for it, in concrete time units, and who would you ask to find out?
2. Why does eventual consistency require idempotent event handlers specifically, rather than just "handlers that work correctly"?
3. A stakeholder insists a cross-aggregate update must be instantly consistent "because the business requires it." What two follow-up questions would help you determine whether that's a true invariant (implying the aggregates should be merged) or a preference that eventual consistency could actually satisfy?
4. Describe a UI/UX pattern that honestly communicates an eventual-consistency lag to a user, versus one that dishonestly hides it by presenting stale data as current.

## References
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 4: "Architecture" (consistency and scalability trade-offs).
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 10: "Aggregates" (eventual consistency across aggregate boundaries).
