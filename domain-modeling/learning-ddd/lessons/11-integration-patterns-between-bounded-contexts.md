---
id: learning-ddd/11
subject: learning-ddd
title: Integration patterns between bounded contexts
slug: integration-patterns-between-bounded-contexts
status: drafted
mastery:
seniority: senior
source: Learning Domain-Driven Design (Vlad Khononov), Part III, Chapter 9 - "Communication Patterns"
prerequisites: [learning-ddd/04, learning-ddd/09, learning-ddd/10]
created: 2026-08-10
updated: 2026-08-10
---

# Integration patterns between bounded contexts

## TL;DR
Once a context map (`learning-ddd/04`) has decided the *social* relationship between two bounded contexts, and data ownership (`learning-ddd/10`) has decided the *consistency* model, integration patterns decide the concrete *technical* mechanism: synchronous request-response (REST/RPC), asynchronous messaging (queues/pub-sub), or event streaming - each with different failure modes, coupling characteristics, and operational demands.

## The idea
It's tempting to treat "how do two services talk to each other" as a purely technical decision, made once, applied everywhere (e.g., "we're a REST shop" or "we're an event-driven shop"). Khononov argues this is backwards: the technical mechanism should be *derived* from the relationship pattern (`learning-ddd/04`) and consistency requirement (`learning-ddd/10`) already established for that specific pair of contexts, not chosen uniformly in advance. A Conformist relationship with a strong-consistency need points toward synchronous request-response; an Open Host Service relationship feeding many loosely-coupled downstream consumers with an eventual-consistency tolerance points toward asynchronous events. Picking the mechanism first and retrofitting the relationship to fit it produces integrations that fight their own requirements - synchronous calls forced onto a genuinely tolerant-of-lag relationship (creating unnecessary availability coupling), or asynchronous messaging forced onto a genuinely strong-consistency need (creating race conditions the team then has to paper over).

## How it works

### Synchronous request-response (REST, RPC, GraphQL)
The calling context blocks and waits for the response. Simplest mental model (looks like a normal function call), but couples the caller's availability and latency directly to the callee's: if the callee is down or slow, the caller is too, unless deliberately isolated (timeouts, circuit breakers, fallbacks).

**Worked example - SaaS billing (from `learning-ddd/10`).** Billing calls Subscription Management's API synchronously to fetch the exact plan price at invoice-generation time - infrequent, consistency-sensitive, and Billing is willing to accept a direct availability dependency on Subscription Management for this specific, low-volume call. This matches a Customer-Supplier relationship (`learning-ddd/04`) with negotiated API stability, and a strong-consistency need (`learning-ddd/10`).

### Asynchronous messaging (point-to-point queues)
The sender publishes a message to a queue and moves on; a single consumer processes it, typically at its own pace, with retry and dead-letter handling for failures. Decouples availability (the sender doesn't need the consumer to be up at the exact moment of sending) but not necessarily timing precision for the *sender's* own workflow if it needs to know the outcome.

**Worked example - logistics.** Route Planning places a "Recalculate Route" message on a queue whenever a new shipment is added to an existing route; a Route-Optimization worker consumes messages from the queue at its own pace, potentially batching several route changes together for efficiency. Route Planning doesn't block on the recalculation completing - it continues accepting new shipment assignments regardless of whether the optimizer is caught up.

### Event streaming / publish-subscribe
The publishing context announces domain events (`learning-ddd/09`) to a stream or topic, with zero knowledge of who (if anyone) is subscribed, and multiple independent consumers can each process the same event stream for entirely different purposes. This is the mechanism that most naturally implements an Open Host Service relationship (`learning-ddd/04`) and the data-replication-via-events pattern (`learning-ddd/10`).

**Worked example - e-commerce.** Order-Management publishes `OrderPlaced`, `OrderCancelled`, and `OrderShipped` events to a stream. Independently, and without Order-Management knowing any of them exist: Analytics consumes the stream to update dashboards; Fraud-Detection consumes it to score new orders; Recommendations consumes it to update a customer's purchase-history-based model; Customer-Notifications consumes it to send status emails. Adding a fifth consumer next quarter requires zero changes to Order-Management - this is the payoff of designing the event as a genuine, stable Published Language (`learning-ddd/04`) rather than a bespoke per-consumer contract.

### The outbox pattern - making "publish an event" reliable
A common, subtle bug: an aggregate saves its state change in one transaction, then tries to publish the corresponding domain event in a separate step - if the process crashes between the two, the state change is saved but the event is silently lost, and every downstream consumer's copy of the data (`learning-ddd/10`) permanently drifts out of sync with no way to detect it. The **outbox pattern** fixes this: the event is written to an "outbox" table in the *same* local database transaction as the state change itself (so both succeed or both fail together, atomically), and a separate, independent process reads the outbox and reliably publishes each event to the message broker, retrying until it succeeds and marking events as sent only after confirmed delivery.

**Worked example - SaaS billing.** When `Subscription.cancel()` runs, both the updated subscription row and a new `SubscriptionCancelled` outbox row are written in one local database transaction. A separate relay process polls the outbox table and publishes each unpublished row to the event stream, marking it sent only after the broker confirms receipt. If the relay process crashes mid-publish, it simply resumes from the last unsent row on restart - no event is ever silently lost, because the event's existence was never dependent on a second, separate operation succeeding.

### Idempotent consumers - handling at-least-once delivery
Most reliable messaging systems guarantee **at-least-once** delivery (a message might be delivered more than once, especially after a consumer crash-and-retry), never exactly-once. Consumers must therefore be written so that processing the same event twice produces the same result as processing it once - e.g., checking "have I already applied this event's ID?" before acting, or using an operation that is naturally idempotent (setting a status to a specific value, rather than incrementing a counter).

**Worked example - healthcare.** Patient-Communications, consuming `AppointmentConfirmed` events to send SMS reminders, records each processed event's unique ID in a small local table before sending; if the same event is redelivered (a genuinely common occurrence after any consumer restart or network hiccup), the duplicate is detected and the SMS is not sent twice - a real user-facing bug (patients getting three copies of the same reminder) that idempotent handling prevents cheaply.

## Pros
- Deriving the mechanism from the already-decided relationship and consistency needs (rather than picking one style company-wide) means each integration's technical shape actually matches its real requirements.
- Asynchronous and event-streaming approaches deliver strong decoupling: the publishing context's uptime, deploy schedule, and internal changes don't directly threaten unrelated consumers.
- The outbox pattern and idempotent-consumer discipline, once established as team habits, make "reliable eventing" a solved, repeatable problem rather than something re-litigated (and re-broken) per integration.
- Synchronous calls, used where genuinely appropriate, remain the simplest mechanism to reason about, test, and debug - not every integration needs messaging infrastructure.

## Cons
- Running multiple integration mechanisms side by side (some synchronous, some queued, some streamed) is operationally more complex than a single company-wide standard, and requires engineers to understand which mechanism is in play for any given dependency.
- Asynchronous and streaming approaches introduce eventual consistency and at-least-once delivery semantics that are a genuine source of subtle bugs if the team hasn't internalized idempotency and staleness-tolerance discipline.
- The outbox pattern requires real infrastructure (a relay process, monitoring for a growing unpublished-outbox backlog) that's easy to under-invest in until a lost-event incident forces the issue.
- Synchronous request-response, if applied to a relationship that should have been eventually consistent, creates unnecessary availability coupling - a slow or down callee now directly degrades the caller, when a queued or event-driven approach would have isolated the failure.

## Alternatives
- **Shared database access** - the anti-pattern flagged in `learning-ddd/10`; sometimes mistaken for an "integration pattern" because it requires no messaging infrastructure at all, but it destroys the autonomy bounded contexts (`learning-ddd/03`) exist to provide.
- **API Gateway / Backend-for-Frontend aggregation** - a client-facing concern (aggregating multiple contexts' data for a single UI screen) rather than a context-to-context integration pattern; often built *using* the synchronous or event-driven mechanisms above, not a substitute for choosing among them.
- **GraphQL federation** - a specific synchronous-integration technology that can implement an Open Host Service relationship with a unified query surface across multiple contexts; a technology choice within the "synchronous request-response" category above, not a fundamentally different pattern.

## When to use it
Choose the integration mechanism per relationship, after (not before) the context map (`learning-ddd/04`) and data-ownership/consistency decisions (`learning-ddd/10`) are made for that specific pair of contexts. Use the outbox pattern and idempotent consumers as a default discipline for any asynchronous or event-driven integration in a system where losing or double-processing an event would cause real business harm.

## When NOT to use it
Don't introduce event-streaming infrastructure for a low-volume, strongly-consistent, simple relationship between two contexts owned by the same small team - a direct synchronous call is simpler to build, test, and debug, and the decoupling benefits of streaming aren't worth the operational cost there. Similarly, don't force a synchronous call onto a relationship that's genuinely tolerant of staleness just because it feels simpler upfront - the resulting availability coupling will surface as an incident eventually.

## Key takeaways / mental model
Integration mechanism is a consequence, not a starting point: first decide the relationship (`learning-ddd/04`) and the consistency need (`learning-ddd/10`) for a specific pair of contexts, then pick synchronous, queued, or streamed accordingly - and whenever the mechanism is asynchronous, treat "reliable publish" (outbox) and "safe re-processing" (idempotency) as non-negotiable, not optional hardening.

## Self-check questions
1. Take an integration between two services you know. Was the mechanism (sync/async/streamed) chosen deliberately based on the relationship and consistency need, or was it just "how we always do it"? Would a different mechanism fit better?
2. Explain the specific failure the outbox pattern prevents, and why writing the event to a message broker directly after (rather than atomically with) the state-change transaction is unsafe.
3. Why must consumers of an event stream be idempotent, given that most messaging systems only guarantee at-least-once delivery? Give a concrete example of a non-idempotent handler and the bug it would cause under redelivery.
4. Give an example of a relationship where synchronous request-response is the right choice despite the general preference for decoupled, asynchronous integration - and justify why.

## References
- Learning Domain-Driven Design (Vlad Khononov), Part III, Chapter 9: "Communication Patterns".
- Enterprise Integration Patterns (Gregor Hohpe, Bobby Woolf) - outbox, idempotent receiver, and messaging pattern foundations.
