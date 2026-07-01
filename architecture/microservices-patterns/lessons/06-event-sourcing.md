---
id: microservices-patterns/06
subject: microservices-patterns
title: "Event Sourcing"
slug: event-sourcing
status: drafted
mastery:
seniority: senior
source: "Microservices Patterns (Chris Richardson), Chapter 6"
prerequisites: [microservices-patterns/05]
created: 2026-07-01
updated: 2026-07-01
---

# Event Sourcing

## TL;DR
Traditional persistence stores an aggregate as its **current state** - one row you overwrite on every change - which loses history and makes reliable event publishing awkward. **Event sourcing** flips this: it persists an aggregate as the **full, ordered sequence of domain events** that happened to it, and rebuilds current state by replaying those events. This makes event publishing intrinsic (the events *are* the source of truth, so nothing can diverge), gives a perfect audit log and time-travel, and pairs naturally with sagas. The costs are real: a different, event-centric persistence model; queries become hard (you can't `SELECT` on state), forcing CQRS (lesson 07); and evolving event schemas over years is a genuine challenge.

## The idea
Recall from lesson 05 that aggregates emit domain events and that publishing those events reliably requires extra machinery (the transactional outbox), because the event publish is separate from the state save and the two can diverge. Event sourcing removes that gap by making a radical choice about *how the aggregate is stored*.

Instead of storing an `Order` as a row - `{id, state: SHIPPED, total: 42.00}` - and `UPDATE`-ing that row on every change, event sourcing stores the **sequence of events** that produced it: `OrderCreated`, `OrderApproved`, `OrderShipped`, .... These events are appended to an **event store**, never updated or deleted. To get the current state of the aggregate, you **load its events and replay them** through the aggregate, applying each one to fold up the current state.

The consequences ripple outward. Because the events are now the *system of record* (not a derived side effect), publishing them is no longer a separate risky step - persisting the aggregate **is** recording the events, so "state changed" and "event happened" are the same act; divergence is impossible by construction. You also get, for free, a complete history (audit, debugging, analytics, "what did this order look like last Tuesday?"). But you also lose the ability to query current state with a normal database query - which is why event sourcing almost always comes with **CQRS** (lesson 07) to build queryable read models from the event stream.

## How it works

### The event store: an append-only log of events per aggregate
The **event store** is a hybrid of a database and a message broker. As a database, it stores events; as a broker, it lets services subscribe to them. Events are organized by aggregate: each aggregate instance has an ordered stream of events keyed by its id and an event sequence number/version.

- **Append, never mutate.** Business operations *append* new events; they never update or delete past events. The log is immutable.
- **Optimistic concurrency via version.** To prevent lost updates when two commands hit the same aggregate concurrently, appends carry the expected version; if the stored version has moved, the append is rejected and the command retried (optimistic locking on the event stream).

```text
  Event store, stream for Order O-1:
  seq  event            payload
  1    OrderCreated     {consumerId, lineItems, total}
  2    OrderApproved    {}
  3    OrderShipped     {shippedAt}
  (append-only; current state = fold over [1,2,3])
```

### Reconstructing state by replaying events
An event-sourced aggregate is written as: a method that **handles a command** by validating it against current state and *producing* new events (it does not mutate state directly), plus a method that **applies an event** to update in-memory state. Loading works by replaying:

1. Read all events for the aggregate id from the store, in order.
2. Create an empty aggregate, then `apply()` each event in sequence to fold up the current state.
3. Now the aggregate is "loaded" and can handle the next command.

Handling a command then means: `process(command) -> returns new events`; the framework `apply()`s them to update state and **appends** them to the store. This split - commands produce events, events mutate state - is the core discipline.

### Snapshots: so replay doesn't get slow
Replaying thousands of events on every load is expensive. The standard optimization is a **snapshot**: periodically store the aggregate's serialized current state at version N. To load, start from the latest snapshot and replay only the events *after* N. Long-lived aggregates (an account open for years) rely on snapshots to keep load time bounded.

```text
  snapshot @ seq 100  --then replay-->  events 101..105
  (load = deserialize snapshot + apply 5 events, not 105)
```

### Event sourcing makes sagas and event publishing natural
Because the event store is also a broker, subscribers receive events as they're appended - so publishing domain events to other services (for choreographed sagas, CQRS views, notifications) is built in, with none of the outbox plumbing lesson 05 needed. Event-sourcing frameworks (the book uses Eventuate as the reference) often also provide **saga orchestration** on top, since the event store already reliably records and delivers events. So event sourcing and sagas fit together: the same reliable-event mechanism drives both.

### The costs: querying, evolution, and deletion
Event sourcing is powerful but shifts real difficulty elsewhere:

- **You cannot query current state directly.** There is no `orders` table to `SELECT * WHERE state='SHIPPED'`. Finding all shipped orders by replaying every aggregate is infeasible. The answer is **CQRS** (lesson 07): subscribe to the event stream and project it into a separate, queryable read-model database.
- **Evolving event schemas is hard.** Events are stored *forever*, so a v1 `OrderCreated` from three years ago must still be replayable by today's code. You must handle multiple event versions, typically with **upcasting** (transforming old event versions to new on read). Schema evolution (ddia/06) becomes a long-horizon commitment.
- **Deleting data is awkward.** An immutable, append-only log conflicts with "delete this user's data" (e.g. GDPR). Techniques like encryption-with-key-deletion (crypto-shredding) are needed, adding complexity.
- **Conceptual shift + framework dependence.** Thinking in "commands produce events, replay yields state" is a real learning curve, and teams usually adopt a framework/event store rather than build one.

### Worked example 1: the Order aggregate as an event-sourced aggregate
Contrast with lesson 05's state-stored `Order`.

1. `create(details)` command: the aggregate validates the request and, instead of setting fields, **returns** an `OrderCreated` event carrying the details.
2. The framework `apply(OrderCreated)`s it - *that* is where `state = APPROVAL_PENDING`, line items, and total get set in memory - and **appends** the event to the store at seq 1.
3. Later, `approve()` command: validates the order is in `APPROVAL_PENDING`, returns `OrderApproved`; `apply` sets `state = APPROVED`; appended at seq 2.
4. To load `O-1` next time, the service replays `[OrderCreated, OrderApproved]` to reconstruct `state = APPROVED`.

The defining difference from lesson 05: the aggregate never overwrites a state row; its history *is* the storage, and current state is a fold over that history.

### Worked example 2: audit and time-travel for free
FTGO support needs to answer "why is this order in a weird state, and who changed it when?"

1. With state storage, the `orders` row shows only the *current* state - the path that led there is gone unless you built a separate audit table by hand.
2. With event sourcing, the order's event stream **is** the audit log: `OrderCreated -> OrderApproved -> OrderRevised(added item) -> OrderCancelled(reason=...)`, each with a timestamp and actor.
3. Support can reconstruct the order's state at *any* past point by replaying events up to that time ("what did it look like before the revision?").
4. This capability is inherent, not bolted on - a direct benefit of storing changes instead of overwriting state. It's a common reason regulated/financial domains adopt event sourcing.

### Worked example 3: why a simple query forces CQRS
Product wants a screen: "all APPROVAL_PENDING orders for restaurant R, newest first."

1. In an event-sourced store there is no queryable `orders` table - only per-aggregate event streams. You cannot efficiently answer this by replaying every order aggregate.
2. So you introduce a **CQRS read model** (lesson 07): a subscriber consumes the order event stream and maintains a denormalized `orders_by_restaurant` table (or Elasticsearch index) shaped exactly for this query, updating it on each `OrderCreated` / `OrderApproved` / etc.
3. The query hits that read model, not the event store.
4. Lesson: **event sourcing on the write side makes CQRS on the read side almost mandatory** - the two patterns are usually adopted together, which is why lesson 07 follows directly.

## Pros
- **Reliable event publishing by construction** - events are the source of truth, so "state changed" and "event emitted" are the same act; no outbox needed and no divergence possible.
- **Complete audit log and time-travel** - the full history is retained, enabling audit, debugging, temporal queries, and analytics that state storage discards.
- **Natural fit with sagas and eventual consistency** - the event store doubles as a broker, so choreography, CQRS views, and orchestration frameworks build cleanly on top.
- **Preserves business intent** - events capture *what happened and why* (e.g. `OrderCancelled(reason)`), richer than a mutated state field.

## Cons
- **Queries are hard** - you can't query current state directly, which forces adopting CQRS to build queryable read models (added architecture and eventual-consistency lag).
- **Event schema evolution over years** - immutable events stored forever must remain replayable, requiring versioning/upcasting discipline.
- **Deleting data is awkward** - append-only logs conflict with erasure requirements (GDPR), needing techniques like crypto-shredding.
- **Steep learning curve and framework dependence** - the command/event/replay model is unfamiliar, and teams typically depend on an event store / framework.

## Alternatives
- **State-based persistence + transactional outbox (lesson 05):** store current state and reliably publish events via an outbox table + relay. Far more familiar and directly queryable; you give up the free audit log and must maintain the outbox.
- **State-based persistence + change data capture (CDC):** tail the database transaction log to emit events from ordinary state changes - reliable events without rewriting the persistence model, but no full domain-event history or replay.
- **Audit logging as a separate concern:** if you only need history, add explicit audit tables/logging rather than adopting full event sourcing.
- **Event sourcing without CQRS (rare):** feasible only if you never need rich queries over current state - usually impractical, hence the CQRS pairing.

## When to use it
- Reliable event publishing and strong integration via events are central, and you want to eliminate the outbox/divergence problem structurally.
- The domain genuinely benefits from a complete, immutable history: audit, compliance, financial/ledger systems, debugging complex state, temporal analytics.
- You are already committing to sagas and event-driven collaboration and want a persistence model that reinforces them.
- The team can adopt CQRS for the read side and take on schema-evolution discipline.

## When NOT to use it
- The service is simple CRUD with straightforward queries and no strong audit/history need - state persistence plus (if required) an outbox is far cheaper.
- The team lacks capacity for the conceptual shift, a suitable event store/framework, and long-term event-versioning discipline.
- Hard data-deletion/erasure requirements dominate and crypto-shredding-style complexity isn't justified.
- You need rich ad-hoc querying but cannot take on CQRS - event sourcing alone will not serve those queries.

## Key takeaways / mental model
Think of event sourcing as keeping a **bank ledger instead of just a balance**. A normal system stores your balance and overwrites it on each transaction - fast to read, but the story of how you got there is gone. A ledger records every deposit and withdrawal, append-only, forever; your balance is *derived* by summing the ledger (and you keep periodic statements - snapshots - so you don't re-add from the beginning every time). The ledger is the truth; the balance is a projection. Two rules of thumb:

1. **Store the changes, derive the state.** Persist an aggregate as its append-only sequence of domain events and reconstruct current state by replaying them (with snapshots to bound load time). This makes events the source of truth, so publishing them is intrinsic and gives a perfect audit log - at the price of a persistence model that can't answer state queries directly.
2. **Event sourcing pulls CQRS in with it.** Because you can't `SELECT` on state, you project the event stream into separate read models (lesson 07) for queries, and you commit to versioning events for as long as you keep them. Adopt it when reliable events, audit/history, and event-driven collaboration are worth that cost - not for simple CRUD.

## Self-check questions
1. How does event sourcing persist an aggregate differently from traditional state storage, and how is the aggregate's current state obtained?
2. Why does event sourcing make reliable event publishing "intrinsic," and how does that eliminate the transactional-outbox problem from lesson 05?
3. What is a snapshot and what problem does it solve? Describe how loading an aggregate works when a snapshot exists.
4. In an event-sourced aggregate, what is the division of responsibility between "handling a command" and "applying an event"? Why must a command produce events rather than mutate state directly?
5. Explain why event sourcing typically forces the adoption of CQRS. Use the "all APPROVAL_PENDING orders for a restaurant" query to illustrate.
6. Name three genuine costs of event sourcing (beyond querying) and, for a financial ledger microservice, argue whether event sourcing is the right choice and why.

## References
- Microservices Patterns (Chris Richardson), Chapter 6: "Developing business logic with event sourcing"
- [ddia/15 - Stream processing (event logs, change data capture)](../../ddia/lessons/15-stream-processing.md)
- [ddia/04 - Storage engines (append-only logs, LSM-trees)](../../ddia/lessons/04-storage-engines.md)
- [microservices-patterns/07 - CQRS](07-cqrs.md)
