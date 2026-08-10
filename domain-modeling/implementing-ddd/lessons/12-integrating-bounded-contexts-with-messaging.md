---
id: implementing-ddd/12
subject: implementing-ddd
title: Integrating bounded contexts with messaging
slug: integrating-bounded-contexts-with-messaging
status: drafted
mastery:
seniority: senior
source: Implementing Domain-Driven Design (Vaughn Vernon), Chapter 13: Integrating Bounded Contexts
prerequisites: [implementing-ddd/07, implementing-ddd/10, implementing-ddd/06]
created: 2026-08-10
updated: 2026-08-10
---

# Integrating bounded contexts with messaging

## TL;DR
Messaging (durable queues/topics carrying published domain events) is Vernon's preferred mechanism for integrating bounded contexts, because it preserves each context's autonomy (`implementing-ddd/03`) and matches the eventual-consistency reality of cross-context processes (`implementing-ddd/06`) — but it requires deliberate engineering for delivery guarantees, ordering, and idempotency that a synchronous REST call doesn't force you to think about upfront (and therefore tends to hide until production).

## The idea
Two bounded contexts can integrate synchronously (context A calls context B's API directly and waits for a response) or asynchronously (context A publishes a fact, context B consumes it whenever it's ready). Vernon's default recommendation, consistent with everything already established about bounded-context autonomy and eventual consistency, is asynchronous messaging built on domain events (`implementing-ddd/07`) wherever the relationship allows it. The reasoning: a synchronous call couples the *availability* of the two contexts together (if context B is down, context A's operation now fails too, even though A's own aggregate update might have nothing structurally wrong with it) and couples them temporally (A has to wait for B, adding latency to A's own use case for a side effect A doesn't actually need an answer to before it can consider its own work done). Messaging decouples both: context A publishes `OrderPlaced` and moves on; context B consumes it whenever it's ready, and if B is down for an hour, the message waits in the queue rather than failing A's request.

## How it works

### Choosing sync vs. async for a given integration
Not every integration should be asynchronous — Vernon is pragmatic here. Use synchronous calls (REST, gRPC) when the caller genuinely needs an immediate answer to proceed (e.g. checking a payment authorization before completing checkout — the customer is waiting, and there's no sensible way to "eventually" tell them their card was declined). Use asynchronous messaging when the receiving context's reaction doesn't block the sender's own use case from being considered complete (e.g. sending a confirmation email after an order is placed — the order is fully placed whether or not the email has gone out yet).

### The publish side: events as the Published Language
The events published across a bounded-context boundary should be treated as the context's Published Language (`implementing-ddd/10`) — a deliberately designed, versioned, documented contract, not an accidental byproduct of internal implementation details leaking out. This often means the event published externally is a translated, more stable version of an internal domain event, not the literal internal event class serialized as-is (the internal event can change freely as the model evolves; the published contract changes only deliberately, with versioning).

**Worked example — e-commerce.** Internally, the *Order Management* context's `Order` aggregate raises a rich `OrderPlaced` domain event with internal implementation details (line-item discount calculation intermediate values, internal workflow state). What gets published externally, on a topic other contexts subscribe to, is a deliberately smaller, stable `OrderPlacedIntegrationEvent` containing only what other contexts genuinely need (order ID, customer ID, line items, total) — insulating subscribers from internal refactors of *Order Management*'s own model.

### The consume side: idempotency and at-least-once delivery
Most durable messaging systems (Kafka, RabbitMQ, SQS) guarantee at-least-once delivery, not exactly-once — a consumer must be prepared to receive and process the same message more than once (network retries, consumer crash-and-redeliver scenarios) without corrupting state. Handlers must be idempotent: applying `OrderPlaced` twice to the *Inventory* context's reservation logic must not reserve stock twice.

```
class InventoryReservationHandler {
    void on(OrderPlacedIntegrationEvent event) {
        if (processedEvents.contains(event.eventId())) return;  // idempotency guard
        for (var item : event.lineItems()) {
            inventoryRepository.findBySku(item.sku()).reserve(item.quantity());
        }
        processedEvents.record(event.eventId());
    }
}
```

### The transactional outbox pattern
A subtle but critical failure mode: if an aggregate's state change is committed to the database, and *then* the corresponding event is published to the message broker as a separate step, a crash between those two steps loses the event forever — the database says the order was placed, but no one downstream ever finds out. The transactional outbox pattern fixes this: write the event to an "outbox" table in the *same database transaction* as the aggregate's state change, and have a separate, reliable process (a polling publisher or change-data-capture tailer) read from the outbox and publish to the message broker, retrying until it succeeds. This guarantees the event is never lost relative to the state change that caused it, at the cost of extra infrastructure (the outbox table and its publisher).

### Ordering guarantees — and when they matter
Some cross-context flows depend on events arriving in order (`OrderPlaced` must be processed before `OrderCancelled` for the same order); most brokers only guarantee ordering within a single partition/queue, keyed appropriately (e.g. partitioning by `orderId` so all events for one order land in the same ordered partition). Designs that don't need cross-event ordering (each event is independently meaningful) avoid this complexity entirely — worth checking explicitly rather than assuming ordering is guaranteed by default.

**Worked example — banking, cross-context notification.** The *Fraud Detection* context subscribes to `FundsWithdrawnIntegrationEvent` published by the *Accounts* context. Fraud Detection doesn't block a withdrawal from succeeding (that would make Accounts' availability depend on Fraud Detection's uptime, exactly the coupling messaging avoids) — it consumes the event asynchronously and, if a pattern looks suspicious, raises its own event (`SuspiciousActivityDetected`) that a different downstream consumer (customer notification, account freeze workflow) reacts to in turn.

## Pros
- Decouples bounded contexts' availability and deployment schedules from each other — a downstream context being down, slow, or mid-deployment doesn't block the upstream context's own use cases from completing.
- Naturally matches the eventual-consistency model already required by small aggregate design (`implementing-ddd/04`, `implementing-ddd/06`), rather than fighting it with synchronous coupling.
- Scales well to many consumers of the same event (an Open Host Service topic, `implementing-ddd/10`) without the publisher needing to know who's listening or how many subscribers exist.

## Cons
- Requires real infrastructure investment (a message broker, an outbox mechanism, dead-letter handling, monitoring for stuck/unprocessed messages) that a direct synchronous call doesn't need — this is a genuine operational cost, not just a design preference.
- Debugging cross-context flows is harder: a bug might manifest only as "context B never saw the event," requiring distributed tracing, correlation IDs, and message-broker introspection to diagnose, versus a synchronous call's straightforward stack trace.
- Ordering, deduplication, and idempotency are easy to get subtly wrong, and the failure modes (duplicate processing, out-of-order application) are often silent until a specific timing coincidence triggers them in production.

## Alternatives
- **Synchronous REST/RPC integration** — simpler mental model, immediate feedback, easier to trace and debug; appropriate when the caller genuinely needs an immediate answer, but couples availability and adds latency, and is a poor fit for the "fire and let downstream catch up eventually" shape most cross-context domain-event flows actually have.
- **Shared database / direct table access** — the fastest to implement (no messaging infrastructure at all) but violates the bounded-context autonomy this entire subject builds toward (`implementing-ddd/03`) and reintroduces tight coupling at the schema level.
- **API composition / backend-for-frontend aggregation** — for read-only cross-context needs (assembling a view from multiple contexts), skip messaging entirely and have a gateway layer call each context's read API and stitch results together per-request, avoiding the need for either synchronous coupling between the contexts themselves or asynchronous event-driven state duplication.

## When to use it
For any cross-bounded-context interaction where the publishing context's own use case doesn't need to wait for the downstream reaction — which, per the reasoning in `implementing-ddd/06`, is the majority of genuine cross-context integrations in a system with well-drawn boundaries.

## When NOT to use it
When the caller genuinely cannot proceed without an immediate answer from the other context (real-time authorization checks, synchronous validation the user is waiting on), reach for a synchronous call instead — forcing an inherently synchronous need into an asynchronous shape (e.g. polling for a response) usually adds complexity without a corresponding benefit.

## Key takeaways / mental model
Before choosing sync or async for a cross-context integration, ask: "does the publishing context's own use case need this reaction to happen before it can be considered done?" If no, messaging is the default — it preserves autonomy and matches the eventual-consistency reality already baked into the aggregate design. If yes, that's a genuine synchronous dependency, and the context map (`implementing-ddd/10`) should reflect that coupling honestly rather than hiding it behind an artificial async wrapper.

## Self-check questions
1. Take a cross-context interaction from a system you know. Is it currently synchronous or asynchronous, and does that match the "does the caller need to wait?" test from this lesson? If not, what's the risk of the mismatch?
2. Explain the transactional outbox pattern in your own words: what specific failure does it prevent, and what would go wrong without it?
3. Why must event consumers be idempotent under at-least-once delivery, and what's a concrete idempotency mechanism you could implement for a handler that reserves inventory?
4. Give an example of a cross-context flow where event ordering genuinely matters, and one where it doesn't. What design choice reflects that difference?

## References
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 13: "Integrating Bounded Contexts".
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 4: "Architecture" (messaging and REST integration styles).
