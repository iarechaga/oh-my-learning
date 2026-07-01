---
id: microservices-patterns/05
subject: microservices-patterns
title: "Designing Business Logic: Aggregates and Domain Events"
slug: business-logic-aggregates
status: drafted
mastery:
seniority: senior
source: "Microservices Patterns (Chris Richardson), Chapter 5"
prerequisites: [microservices-patterns/02, microservices-patterns/04]
created: 2026-07-01
updated: 2026-07-01
---

# Designing Business Logic: Aggregates and Domain Events

## TL;DR
Once a service owns its data, the shape of its business logic decides whether that data stays consistent and whether the service can play its part in sagas. Domain-Driven Design's **aggregate** - a cluster of domain objects (entities and value objects) treated as one consistency boundary with a single **root** as the only entry point - is the organizing pattern. Aggregates give you a rule of thumb for transaction scope (one aggregate = one local transaction), they keep invariants enforceable, and their boundaries tend to align with service boundaries. Paired with **domain events** - records that "something important happened" - aggregates become the natural trigger for the messaging and sagas that keep *other* services consistent.

## The idea
A service's business logic can be organized two ways. The **transaction script** style puts procedural logic in service methods that operate on dumb data objects (getters/setters only); it works for simple logic but degenerates into tangled, duplicated code as complexity grows ("anemic domain model"). The **domain model** style (object-oriented) puts behavior *with* the data in rich objects. For non-trivial microservices, the domain model style wins - but a plain object graph raises hard questions: which objects load and save together? What is the boundary of a single transaction? Where do you enforce invariants that span several objects?

Domain-Driven Design answers with the **aggregate**: a graph of objects that forms a *consistency boundary*. One object is the **aggregate root**; external code may only hold references to and invoke methods on the root, never reach inside to child objects directly. The aggregate is loaded, saved, and made consistent as a unit. In FTGO, an `Order` aggregate contains the `Order` root plus `OrderLineItem` value objects and perhaps `DeliveryInfo`; a `Consumer` is a different aggregate.

Two properties make aggregates the right microservices tool. First, **an aggregate is the unit of consistency**: DDD's rule is that a single transaction may create or update **exactly one aggregate**, because within an aggregate you can enforce invariants but *across* aggregates you cannot (they may be in different services). Second, aggregates naturally decompose the domain into chunks that map onto services (this echoes the decomposition work in lesson 02). And because you can only change one aggregate per transaction, any operation that must touch several aggregates is precisely the operation that needs a **saga** (lesson 04) - so aggregate design and saga design are two sides of one coin.

## How it works

### Aggregates: root, boundary, and the reference-by-identity rule
An aggregate has three structural rules:

1. **Single root, single entry point.** The root is an entity with a global identity; the outside world references and calls only the root. Child objects (like line items) are reachable only *through* the root, so the root can enforce every invariant on the way in.
2. **Reference other aggregates by identity, not by object reference.** An `Order` does not hold a `Consumer` object; it holds a `consumerId`. This keeps aggregate boundaries crisp, prevents accidental cross-aggregate object graphs, and - crucially in microservices - lets the two aggregates live in **different services and different databases**.
3. **One aggregate per transaction.** A transaction creates or updates one aggregate instance. Multi-aggregate changes are done with sagas / eventual consistency, not one big transaction.

```text
  Order AGGREGATE (consistency boundary)
  +--------------------------------------+
  |  Order (ROOT)  <-- only entry point  |
  |    - id                              |
  |    - state                           |
  |    - consumerId  --------------------|--> (identity ref only)
  |    - OrderLineItem[]  (children)     |      to Consumer aggregate
  |    - total()  invariant enforced here|      in another service
  +--------------------------------------+
```

### Choosing aggregate granularity: a real design trade-off
How big should an aggregate be? This is a genuine architectural decision, not a formality.

- **Large aggregates** (e.g. make `Consumer` contain all their `Order`s) enlarge the consistency boundary, so you can enforce more invariants in one transaction - but they hurt scalability and concurrency: the whole aggregate is the unit of locking, so two users updating two different orders of the same consumer would contend on the same aggregate. Large aggregates also cannot be split across services.
- **Small aggregates** (make `Order` its own aggregate, referencing `consumerId`) maximize concurrency and let aggregates be distributed across services - at the cost that any invariant spanning them now needs a saga and becomes eventually consistent.

The guidance: **prefer small aggregates**, and accept that cross-aggregate consistency becomes a saga. This directly enables the database-per-service and decomposition patterns.

### Designing the domain logic inside the aggregate
Within the boundary, use a rich **domain model**: the root exposes intention-revealing methods (`order.cancel()`, `order.revise(newLineItems)`) that enforce invariants and manage state transitions, rather than exposing setters. Many aggregates are effectively **state machines** - an `Order` moves `APPROVAL_PENDING -> APPROVED -> ... -> CANCELLED`, and each method checks the current state is legal for that command (you can't ship a cancelled order). Modeling the aggregate as an explicit state machine also makes it a good saga participant, because sagas drive exactly these state transitions and need "pending" states as semantic locks (lesson 04).

### Domain events: publishing that something happened
A **domain event** is an object recording that something significant happened to an aggregate - `OrderCreated`, `OrderCancelled`, `OrderApproved`. Events are named in the past tense and carry the aggregate id plus the data consumers need. They matter because:

- **They trigger cross-service consistency.** Other services subscribe to a service's domain events to keep their own data or process consistent - this is the mechanism behind choreographed sagas and eventual consistency (lesson 04) and behind CQRS read models (lesson 07).
- **They decouple.** The publisher doesn't know who consumes; new consumers can be added without changing the aggregate.
- **They enable notifications, analytics, and audit.**

An aggregate *generates* events as part of executing a command; the service then *publishes* them.

### Reliably publishing events: generate, then publish atomically
The dangerous gap: the aggregate's state change is committed to the database, but the event publish is a separate action. If the process crashes between them, you either lose the event (DB updated, event never sent) or emit a phantom (event sent, DB rolled back). The fix is the **transactional outbox** (from lesson 03): in the *same* local transaction that saves the aggregate, insert the domain event into an `OUTBOX` table; a separate **message relay** (via polling or transaction-log tailing / CDC) reads the outbox and publishes to the broker, then marks it sent. This gives at-least-once publishing tied to the aggregate's transaction - so "aggregate changed" and "event published" cannot diverge. (Consumers must therefore be idempotent - lesson 03.)

```text
  ONE local transaction:
    UPDATE order SET state='CANCELLED' WHERE id=...
    INSERT INTO outbox (event='OrderCancelled', payload=...)
  COMMIT
        |
        v
   Message Relay (polling / CDC) --> Broker --> subscribers
```

### Worked example 1: the Order aggregate enforces an invariant
FTGO rule: an order's line items must total at least the restaurant's minimum, and you can only revise an order before it ships.

1. Client calls `orderService.reviseOrder(orderId, revisedLineItems)`.
2. Service loads the **whole `Order` aggregate** (root + line items) in one read.
3. It calls `order.revise(revisedLineItems)` on the **root** - not on the line items directly. The root checks (a) the order is in a revisable state (`APPROVED`, not `SHIPPED`), and (b) the new total still meets the minimum. Because all line items live inside the aggregate, the root can enforce this invariant with certainty - nothing outside could have changed a line item behind its back.
4. If valid, the aggregate updates its line items and total and returns a `OrderRevised` domain event.
5. The service saves the aggregate and inserts `OrderRevised` into the outbox in **one transaction** (one aggregate, one transaction).

The single-entry-point rule is what makes the invariant enforceable: had callers mutated `OrderLineItem`s directly, no one could guarantee the total invariant.

### Worked example 2: an operation across two aggregates needs a saga
FTGO: placing an order must check the `Consumer` (are they allowed to order?) and create the `Order`. These are two aggregates, likely in two services.

1. You **cannot** update `Consumer` and create `Order` in one transaction (one-aggregate-per-transaction, and they may be in different databases).
2. So the operation becomes a **saga** (lesson 04): create `Order` in `APPROVAL_PENDING` (`T1`, one aggregate), then a step verifies the `Consumer` aggregate in its own service (`T2`), then approve the order (`T3`).
3. Aggregate design *forced* the saga: the moment an operation spans aggregates, cross-aggregate consistency is eventual and coordinated by messages, not by a shared transaction.

This is the key connection: **aggregate boundaries decide where sagas appear.**

### Worked example 3: a domain event drives another service (choreography)
FTGO: when an order is cancelled, the kitchen must cancel its ticket.

1. `order.cancel()` runs on the `Order` root, transitions state to `CANCELLED`, and produces an `OrderCancelled` domain event.
2. The service saves the aggregate + writes `OrderCancelled` to the outbox in one transaction; the relay publishes it.
3. `Kitchen Service` subscribes to `OrderCancelled`, and in its own local transaction cancels the corresponding `Ticket` aggregate.
4. Result: two services stay consistent with no distributed transaction - the domain event emitted by one aggregate triggered a state change in another. The consumer is idempotent, so a redelivered `OrderCancelled` is harmless.

This is exactly the machinery that powers choreographed sagas and, later, CQRS view updates (lesson 07).

## Pros
- **Clear consistency boundary** - "one aggregate per transaction" gives an unambiguous rule for transaction scope and keeps invariants enforceable at the root.
- **Aligns with microservice boundaries** - reference-by-identity lets aggregates live in separate services/databases, directly supporting database-per-service and decomposition.
- **Rich, maintainable business logic** - the domain-model style keeps behavior with data and avoids the tangled/anemic transaction-script sprawl as complexity grows.
- **Natural integration point** - domain events emitted by aggregates are the trigger for sagas, eventual consistency, CQRS read models, auditing, and notifications.

## Cons
- **Getting boundaries right is hard** - too-large aggregates kill concurrency and can't be split; too-small ones push more logic into sagas and eventual consistency.
- **More moving parts for cross-aggregate operations** - any multi-aggregate change becomes a saga with compensations and visible intermediate state (all of lesson 04's costs).
- **Reliable event publishing needs infrastructure** - the outbox + relay (polling or CDC) must be built and operated, and consumers must be idempotent.
- **Learning curve** - DDD concepts (aggregates, roots, value objects, bounded contexts) and the discipline of the reference-by-identity rule take time for a team to absorb.

## Alternatives
- **Transaction script pattern:** procedural logic over dumb data objects - simpler for genuinely simple services, but degrades into duplicated, hard-to-maintain code (the anemic domain model) as logic grows.
- **One big aggregate / larger consistency boundary:** enforce more invariants in a single transaction at the cost of concurrency and the ability to split across services.
- **Event sourcing (lesson 06):** persist the aggregate as its sequence of domain events rather than as current state - makes event publishing intrinsic and gives a perfect audit log, at the cost of a different persistence and query model.
- **Shared mutable data across services (anti-pattern):** skip aggregates/identity references and let services touch each other's tables - reintroduces the coupling that microservices exist to remove; avoid.

## When to use it
- The service has non-trivial business logic and invariants that must be enforced reliably.
- You are applying database-per-service and need a principled way to scope transactions and decide what changes together.
- Operations frequently need to keep *other* services consistent - domain events give you the hook.
- You want service boundaries and consistency boundaries to reinforce each other.

## When NOT to use it
- The service is a thin CRUD wrapper with essentially no invariants - full DDD aggregates may be overkill; a transaction script can be fine.
- You are tempted to make one giant aggregate to force strong consistency across what are really separate concepts - that's a signal to rethink boundaries, not to enlarge the aggregate.
- The team has no capacity to build reliable event publishing (outbox/relay) or to make consumers idempotent, and the domain doesn't actually need cross-service events yet.
- You'd add DDD ceremony without the complexity that justifies it (premature sophistication).

## Key takeaways / mental model
Picture an aggregate as a **sealed package with one authorized signer**. Everything inside (line items, delivery info) can only be handled by the signer at the door (the root), so the signer can guarantee the package's internal rules always hold. Packages refer to each other only by tracking number (identity), never by reaching inside another package - so packages can sit in different warehouses (services). You can only reseal one package per transaction; coordinating several packages is a logistics workflow (a saga). And whenever a package changes, it drops a slip in the outbox ("OrderCancelled") that other warehouses subscribe to. Two rules of thumb:

1. **One aggregate = one consistency boundary = one transaction.** Design small aggregates that reference others by identity; the moment an operation spans aggregates, it becomes a saga with eventual consistency (lesson 04). Enforce invariants only at the root.
2. **Aggregates emit domain events, and events are the nervous system of the architecture.** Publish them reliably with the transactional outbox so "state changed" and "event sent" never diverge; those events drive sagas, keep other services consistent, and feed read models and audit logs.

## Self-check questions
1. What is an aggregate, what are its three structural rules (root/entry point, reference-by-identity, one-per-transaction), and why does each rule matter specifically in a microservices setting?
2. Why does DDD say a single transaction should create or update exactly one aggregate, and how does that rule connect aggregate design to sagas?
3. Compare large vs small aggregates. What does each choice buy and cost in terms of concurrency, invariants, and the ability to split across services - and which does the book prefer?
4. What is a domain event, and give three distinct things domain events enable in a microservice architecture.
5. Describe the reliability gap between committing an aggregate's state change and publishing its event, and explain precisely how the transactional outbox closes it. Why must consumers be idempotent?
6. In FTGO, "cancel an order and refund the customer" touches the `Order` aggregate (Order Service) and the customer's balance (Accounting Service). Walk through how aggregate rules force this into a saga, which domain event(s) you'd emit, and how the two services end up consistent.

## References
- Microservices Patterns (Chris Richardson), Chapter 5: "Designing business logic in a microservice architecture"
- [hard-parts/10 - Data ownership and distributed data](../../hard-parts/lessons/10-data-ownership.md)
- [microservices-patterns/06 - Event sourcing](06-event-sourcing.md)
