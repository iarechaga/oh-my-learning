---
id: ddd-distilled/08
subject: ddd-distilled
title: Domain events and eventual consistency
slug: domain-events-and-eventual-consistency
status: drafted
mastery:
seniority: senior
source: Domain-Driven Design Distilled (Vaughn Vernon), Chapter 6 "Tactical Design with Domain Events"
prerequisites: [ddd-distilled/06]
created: 2026-08-10
updated: 2026-08-10
---

# Domain events and eventual consistency

## TL;DR
A domain event is an immutable record of something meaningful that already happened in
the domain, named in the past tense and expressed in ubiquitous language (`OrderPlaced`,
`PaymentCaptured`, `TripCompleted`). Domain events are the primary mechanism for
coordinating change *across* aggregate boundaries (`ddd-distilled/06`) — instead of one
big transaction spanning multiple aggregates, aggregate A completes its own atomic
change, publishes an event describing what happened, and aggregate B (or a separate
bounded context, per `ddd-distilled/03`) reacts to that event on its own schedule,
becoming consistent with A a moment later — eventual consistency.

## The idea
Small, well-drawn aggregates (`ddd-distilled/06`) solve the contention and coupling
problems of one giant transactional unit, but they create a new question: how does the
rest of the system learn that something happened, and react, without collapsing back
into one big cross-aggregate transaction? Domain events answer this. When `Order.place()`
succeeds, the `Order` aggregate doesn't reach out and directly call methods on `Inventory`
or `Payment` — that would recreate tight coupling and shared-transaction contention. It
instead publishes an `OrderPlaced` event, a plain, immutable fact about what just
happened, and lets interested aggregates or bounded contexts subscribe and react
independently, each within their own transactional boundary, at their own pace.

This is also a strategic-design tool, not just a tactical one: domain events are commonly
the integration mechanism between bounded contexts (`ddd-distilled/03`) — a `Checkout`
context publishes `OrderPlaced`, and `Fulfillment`, `Analytics`, and `Notifications`
contexts each subscribe independently, with no direct coupling between them and no need
for `Checkout` to know who's listening.

The trade-off this pattern makes explicit and deliberate is **consistency now vs.
consistency soon**: within one aggregate, invariants hold instantly, always
(`ddd-distilled/06`). Across aggregates and across bounded contexts, consistency is
eventual — there is a real, sometimes-observable window where the rest of the system
hasn't caught up yet with what the source aggregate already knows. DDD's tactical design
teaches you to draw that line deliberately, rather than accidentally.

## How it works

### Anatomy of a domain event
A domain event is:
- **Named in the past tense**, describing a fact, not a command (`OrderPlaced`, not
  `PlaceOrder`) — by the time anyone sees the event, the thing already happened and
  cannot be "rejected," only reacted to.
- **Immutable** — a value object (`ddd-distilled/05`) representing a snapshot of relevant
  data at the moment it occurred, typically including enough information for subscribers
  to act without needing to immediately query back to the source aggregate (though they
  may still need to for full detail).
- **Published by the aggregate root** whose state change the event describes, usually
  right after (or as part of) the same operation that changed the aggregate's own state,
  as a record of what the aggregate did.

**Worked example — an order placement flow.**
```
OrderPlaced {
  orderId: OrderId
  customerId: CustomerId
  lineItems: [LineItemSnapshot]
  totalAmount: Money
  placedAt: Timestamp
}
```
`Order.place()` validates its own invariants (line items present, total correctly
computed — `ddd-distilled/06`), transitions its own status to `Placed`, and returns (or
internally records) an `OrderPlaced` event. An application service (`ddd-distilled/07`)
persists the `Order` aggregate and then publishes the event to whatever messaging
mechanism the system uses (an in-process event bus, a message queue, a transactional
outbox). `Inventory` subscribes and reacts by reserving stock for each line item — a
change to the `Inventory` aggregate(s), in their own transaction, moments after the order
was placed. `Notifications` subscribes and sends a confirmation email. Neither of these
subscribers blocks order placement, and `Order` never needed to know either of them
exists.

### Worked example — eventual consistency's observable window
In the flow above, there's a real window — milliseconds to seconds, depending on the
messaging infrastructure — during which the order exists as `Placed` but inventory has
not yet been reserved. If a second order is placed for the last unit of the same item
during that window, the system needs an explicit answer for what happens (a compensating
event like `InventoryReservationFailed`, triggering an `OrderCancelled` or
`OrderRequiresAttention` event back on the order side). This is the real cost of
eventual consistency made concrete: it's not just an implementation detail, it's a
business scenario the team must design for explicitly, usually by asking domain experts
"what should happen if X and Y happen close together" — precisely the kind of question
collaborative modeling (`ddd-distilled/02`) is meant to surface.

### Worked example — domain events as bounded-context integration
Recall the healthcare scheduling example from `ddd-distilled/03`: `Scheduling` and
`Billing` are separate bounded contexts specifically because "Appointment" meant
different things to each. The clean integration is a domain event: `Scheduling`
publishes `AppointmentCompleted` (with the minimal data Billing actually needs — patient
ID, provider ID, procedure codes, completion timestamp) once an appointment's clinical
visit is marked done. `Billing` subscribes, and constructs its own `BillableEncounter`
entity from the event — using its own vocabulary and its own model, decoupled entirely
from Scheduling's internal representation. This is the Open Host Service /
event-driven-integration pattern from `ddd-distilled/03` in concrete form.

### Domain events vs. integration events
A useful distinction: a **domain event** published and consumed *within* one bounded
context (coordinating aggregates inside the same context) can carry rich, internal
vocabulary and can change shape more freely as the model evolves. An **integration
event**, published *across* a bounded-context boundary to other contexts, functions as a
public contract — other teams depend on its shape, so it needs the same discipline as
any public API (versioning, backward compatibility, deliberate design) and typically
carries only the minimal data downstream consumers actually need, not an internal dump of
the source aggregate's full state.

### Reliable publication — the outbox pattern (brief)
A subtle but important implementation concern: an aggregate's state change and its
corresponding event publication need to be reliably linked — if the `Order` save
succeeds but the event publish silently fails (or vice versa), the system drifts into
permanent inconsistency, not just a temporary eventual-consistency window. The common
solution is a **transactional outbox**: write the event to an outbox table in the same
database transaction as the aggregate's state change, then have a separate, reliable
process publish outbox entries to the messaging system asynchronously. This is
implementation detail beyond what the primer covers in depth, but worth knowing exists —
`domain-modeling/implementing-ddd` covers it further.

## Pros
- Decouples aggregates and bounded contexts from each other — a publisher never needs to
  know who's subscribed, which lets new consumers be added without touching the source.
- Keeps each aggregate's own transaction small (per `ddd-distilled/06`'s sizing guidance)
  by moving cross-aggregate coordination out of the transaction and into asynchronous
  reaction.
- Produces a natural audit trail / history of what happened in the domain, which is
  often independently valuable (event sourcing, discussed below, takes this further; even
  without full event sourcing, a log of domain events is a useful record for debugging
  and analytics).
- Domain events, being named in ubiquitous language, double as living documentation of
  "what significant things can happen in this domain" — often clarifying for domain
  experts reviewing the model.

## Cons
- Eventual consistency is a real business behavior change, not just a technical detail —
  it must be explicitly designed for (the "what if two things race" scenario above), and
  stakeholders unfamiliar with the trade-off can be surprised or uncomfortable with it.
- Debugging across an asynchronous, event-driven flow is harder than following a single
  synchronous call stack — tracing "why didn't inventory get reserved" now involves
  checking whether the event was published, delivered, and processed correctly.
- Reliable event publication (avoiding the "state changed but event lost" failure mode)
  requires real infrastructure investment (outbox pattern, message broker guarantees) —
  not just "call an event bus and hope."
- Integration events, once other teams depend on them, become a compatibility contract
  that constrains future changes — the same versioning discipline any public API needs.

## Alternatives
- **Direct synchronous calls between aggregates/services** — simpler to trace and reason
  about for low-complexity coordination, but reintroduces tight coupling and
  cross-aggregate transactional contention; reasonable for genuinely simple, low-volume
  coordination where eventual consistency's complexity isn't worth it.
- **Event sourcing** — a more aggressive relative of this pattern where an aggregate's
  *entire* state is derived by replaying its full history of domain events, rather than
  storing current state directly. A legitimate, more advanced technique for aggregates
  where a full audit history is itself a core requirement (e.g., financial ledgers), but
  a substantially bigger commitment than "publish events for cross-aggregate
  coordination," and out of scope for this primer — see `domain-modeling/implementing-ddd`
  for it.
- **Change-data-capture (CDC) from the database** — publishing events derived from
  database row changes rather than from explicit domain-model method calls; technically
  simpler to bolt onto an existing system, but the resulting events describe *data*
  changes, not *domain* facts, and typically lack the ubiquitous-language clarity a
  hand-modeled domain event has.

## When to use it
Use domain events whenever a use case's effects legitimately need to reach beyond a
single aggregate (`ddd-distilled/06`) or beyond a single bounded context
(`ddd-distilled/03`), and the business can tolerate a short delay before the rest of the
system catches up. This is the default coordination mechanism once you've committed to
small, well-bounded aggregates — the two patterns are designed to work together.

## When NOT to use it
Don't reach for domain events for coordination that genuinely must be instantly
consistent (in which case it likely belongs inside one aggregate's boundary instead —
revisit `ddd-distilled/06`'s invariant test), and don't add event-driven machinery to a
generic/simple subdomain where a direct call is clearer and the eventual-consistency
trade-off buys nothing.

## Key takeaways / mental model
Small aggregates make consistency instant *inside* their boundary and eventual *across*
boundaries — domain events are the mechanism that carries "what just happened" across
that gap, in ubiquitous language, without coupling the publisher to its subscribers.
Whenever you introduce a domain event for cross-aggregate coordination, explicitly design
for the window where the two sides are temporarily out of sync — that window is a real
business scenario, not an implementation footnote.

## Self-check questions
1. Why is a domain event named in the past tense, and why does that matter for how
   subscribers are allowed to react to it (can a subscriber "reject" an `OrderPlaced`
   event)?
2. Walk through the "last unit of inventory, two simultaneous orders" scenario. What
   domain event(s) would you introduce to handle it, and what should happen on the order
   side?
3. What's the difference between a domain event used purely inside one bounded context
   and an integration event published across bounded contexts? Why does that difference
   affect how carefully you design the event's shape?
4. Explain, in your own words, why publishing an event and saving the aggregate's state
   need to be reliably linked, and what can go wrong if they aren't (tie this to the
   transactional outbox idea).
5. Give an example of a coordination need where a direct synchronous call would actually
   be preferable to a domain event, and explain why.

## References
- Domain-Driven Design Distilled (Vaughn Vernon), Chapter 6: "Tactical Design with
  Domain Events".
- For event sourcing, the transactional outbox pattern, and deeper event-driven
  integration case studies, see `domain-modeling/implementing-ddd`.
