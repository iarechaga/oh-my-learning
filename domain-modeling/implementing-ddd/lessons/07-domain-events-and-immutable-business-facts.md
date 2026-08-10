---
id: implementing-ddd/07
subject: implementing-ddd
title: Domain events and immutable business facts
slug: domain-events-and-immutable-business-facts
status: drafted
mastery:
seniority: senior
source: Implementing Domain-Driven Design (Vaughn Vernon), Chapter 8: Domain Events
prerequisites: [implementing-ddd/02, implementing-ddd/04]
created: 2026-08-10
updated: 2026-08-10
---

# Domain events and immutable business facts

## TL;DR
A domain event is an immutable record of something significant that already happened in the domain, named in the past tense in the ubiquitous language; it's the mechanism that closes eventual-consistency gaps (`implementing-ddd/06`), decouples aggregates and bounded contexts, and — done well — becomes a durable, meaningful audit trail rather than an implementation afterthought bolted onto a CRUD system.

## The idea
Most systems, even ones without any DDD influence, have *some* notion of "things that happened" — audit logs, activity feeds, webhook notifications. What distinguishes a domain event in Vernon's treatment is that it's a first-class part of the domain model itself, not an infrastructure concern layered on top after the fact. A domain event is named the way a domain expert would describe what happened — `OrderPlaced`, `FundsWithdrawn`, `DiscussionClosed` — never a generic `EntityChanged` or `OrderUpdated` that forces a subscriber to inspect a diff to figure out what actually occurred. Events are raised by aggregates as a direct consequence of a state-changing operation, are immutable once created (a fact about the past cannot be edited — you can only record a subsequent fact that supersedes it), and carry exactly the data a subscriber needs to react, without requiring the subscriber to reach back into the aggregate that raised the event to get more context. This last property is what makes domain events the connective tissue for eventual consistency (`implementing-ddd/06`) and cross-context integration (`implementing-ddd/12`) — a subscriber that's fully informed by the event payload alone can react without a synchronous callback to the source.

## How it works

### Step 1 — Name events as past-tense business facts, not technical mutations
`OrderPlaced`, not `OrderStatusChanged`. `FundsWithdrawn`, not `AccountUpdated`. `DiscussionClosed`, not `DiscussionFieldModified`. The naming discipline matters because a generic name forces every subscriber to inspect the event's contents (or worse, re-query the aggregate) to determine what actually happened, defeating the purpose of the event as a self-describing fact.

### Step 2 — Raise the event from inside the aggregate that owns the fact
The aggregate itself is responsible for creating its own events, as a direct side effect of the operation that caused them — not the application service (`implementing-ddd/09`), which should only be responsible for collecting and dispatching events the aggregate already raised, not deciding what happened.

**Worked example — order fulfillment.**
```
class Order {
    private final List<DomainEvent> events = new ArrayList<>();

    void place() {
        if (this.status != OrderStatus.DRAFT) throw new IllegalStateException(...);
        this.status = OrderStatus.PLACED;
        this.events.add(new OrderPlaced(this.id, this.customerId, this.lineItems, Instant.now()));
    }

    List<DomainEvent> pullEvents() {
        List<DomainEvent> pulled = List.copyOf(events);
        events.clear();
        return pulled;
    }
}
```
The application service, after calling `order.place()` and persisting the aggregate, pulls the recorded events and publishes them — the *aggregate* decided what fact occurred; the application service is only responsible for making sure the fact gets delivered.

### Step 3 — Make the event payload self-sufficient
`OrderPlaced` should carry the customer ID, the line items, and the placed timestamp — everything a reasonable subscriber (an inventory reservation handler, a notification service, an analytics pipeline) would need, without forcing every subscriber to make a follow-up call back to the `Order` aggregate to get details. This is what allows the event to cross a bounded-context boundary safely (`implementing-ddd/12`) — a subscriber in a different context, possibly a different service entirely, cannot casually call back into the `Order` aggregate's internal API, so the event has to be complete.

**Worked example — banking.** `FundsWithdrawn` carries the account ID, the amount, the resulting balance, and a transaction reference — not just "something changed on account X." A fraud-detection subscriber reacting to withdrawal patterns needs the amount and timing directly from the event; requiring it to query the account for every event it processes would create a synchronous coupling eventual consistency exists to avoid.

### Step 4 — Version events deliberately as the model evolves
Once an event schema is published (especially across a bounded-context boundary, `implementing-ddd/10`), it becomes a contract that other teams' code depends on. Adding a new field is usually safe if new fields are optional/additive; removing or renaming a field is a breaking change and needs an explicit versioning strategy (`OrderPlacedV2`, or a schema registry with compatibility rules) rather than silently changing the shape of an event subscribers already depend on.

### Step 5 — Persist events when they need to be replayed, audited, or drive event sourcing
Not every domain event needs durable storage — some are purely used for immediate in-process notification. But when an event stream needs to support replay (rebuilding a read model, `implementing-ddd/14`), audit requirements (a regulated financial system needing a complete history of what happened, not just current state), or event-sourced aggregates (`implementing-ddd/13`), events are appended to a durable event store or log (e.g. Kafka, an event-sourcing-specific store) rather than only published transiently.

## Pros
- Decouples the aggregate/context that caused a fact from every downstream consumer of that fact — new subscribers can be added later without modifying the aggregate that raises the event, which is a major win for extensibility (a new "send a Slack notification on order placement" feature needs zero changes to the `Order` aggregate).
- Provides a natural, meaningful audit trail almost for free, since the events *are* a chronological record of what happened in business terms, not a generic technical change log that requires interpretation after the fact.
- Is the concrete mechanism that makes eventual consistency (`implementing-ddd/06`) and cross-bounded-context integration (`implementing-ddd/12`) actually work, rather than remaining abstract design principles with no implementation path.

## Cons
- Adds real infrastructure requirements once events cross process boundaries — reliable delivery, at-least-once semantics with idempotent handling, ordering guarantees where they matter — that a simple synchronous method call doesn't need.
- Debugging a system driven substantially by asynchronous domain events is harder than tracing a single synchronous call stack — a bug might only manifest as "handler X never processed event Y," requiring distributed tracing or correlation IDs to diagnose.
- Overusing events for things that are really just internal implementation details (raising an event for every trivial field mutation) creates noise, performance overhead, and a proliferation of handlers that's harder to reason about than the plain method calls it replaced — reserve events for genuinely significant business facts.

## Alternatives
- **Direct synchronous method calls between aggregates/services** — simpler to trace (a normal call stack), immediately consistent; the natural default for interactions within a single aggregate's boundary, but inappropriate across aggregate or bounded-context boundaries per `implementing-ddd/04`'s and `implementing-ddd/06`'s reasoning.
- **Generic "entity changed" notifications with a diff** — technically similar to a domain event but names nothing in business terms, forcing subscribers to reconstruct meaning from a diff; simpler to implement generically (one notification type for all entities) but loses the self-describing, ubiquitous-language benefit that's the whole point of a domain event.
- **Change Data Capture (CDC) off the database** — derive "events" by tailing the database transaction log rather than having the domain model explicitly raise them; avoids requiring application code to remember to raise events, but produces technical row-change facts rather than business-meaningful facts, and can leak persistence-schema details across the same boundary domain events are meant to protect.

## When to use it
Whenever a state change is significant enough that some other part of the system (a different aggregate, a different bounded context, an external system) needs to react to it — especially at every point where eventual consistency (`implementing-ddd/06`) is in play.

## When NOT to use it
Skip domain events for state changes with no interested subscriber, no cross-boundary consequence, and no audit value — raising an event for every trivial internal mutation adds ceremony and noise without a corresponding benefit; a plain method call inside the aggregate's own boundary is simpler and correct there.

## Key takeaways / mental model
A domain event answers one question precisely: "what fact, described the way a domain expert would describe it, just became true?" If you can't name the event in clean past tense using vocabulary a domain expert would recognize, either the event doesn't deserve to exist yet, or the underlying operation itself isn't well understood.

## Self-check questions
1. Take a state-changing operation from a system you know (e.g. "update order status to shipped") and rename it as a proper past-tense domain event. What data does a reasonable subscriber need in the payload to act without calling back to the source?
2. Why should the aggregate itself raise its own events rather than the application service deciding what event to publish after calling the aggregate's method?
3. Describe a realistic breaking change to an event's schema (once it's published across a bounded context boundary) and how you'd version it without breaking existing subscribers.
4. Give an example of a state change that does NOT deserve a domain event, and explain what signal told you that.

## References
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 8: "Domain Events".
