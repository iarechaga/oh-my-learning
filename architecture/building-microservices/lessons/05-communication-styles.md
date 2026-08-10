---
id: building-microservices/05
subject: building-microservices
title: "Inter-Service Communication Styles"
slug: communication-styles
status: drafted
mastery: 
seniority: mid
source: "Building Microservices, 2nd ed. (Sam Newman), Chapter 5"
prerequisites: [building-microservices/01, building-microservices/03]
created: 2026-08-10
updated: 2026-08-10
---

# Inter-Service Communication Styles

## TL;DR
Services can talk to each other in two fundamentally different styles: **request-response** (synchronous, the caller waits for an answer) and **event-based** (asynchronous, the sender fires a message and moves on). Within event-based communication, the coordination logic for a multi-step business process can live in one place (**orchestration**) or be distributed across the services reacting to events (**choreography**). Each choice trades off coupling, complexity of reasoning, and failure behavior differently — there is no universally correct style, only the right style for a given interaction.

## The idea
Once you have service boundaries (Lessons 02-03), those services need to collaborate to get real work done — a checkout needs Cart, Order, Payment, and Inventory to cooperate. How they talk to each other is one of the highest-leverage decisions in a microservice system, because it directly determines how tightly coupled the services end up being in practice (temporal coupling, from Lesson 03) and how failures propagate.

At the highest level, there are two styles:

- **Request-response**: Service A sends a request to Service B and waits for B's response before proceeding. This is the natural, familiar mental model — it mirrors a function call. B might be called synchronously (A blocks until B replies) or the call might be made asynchronously in the sense of "non-blocking I/O," but conceptually A still needs B's answer to continue its own logic.
- **Event-based**: Service A publishes a fact that something happened (`OrderPlaced`) without addressing it to anyone in particular, and without waiting for anyone to act on it. Zero, one, or many other services may be listening and react independently, on their own schedule. A doesn't know or care who's listening, and doesn't block waiting for a reaction.

These aren't mutually exclusive within one system — most real microservice architectures use both, choosing per-interaction based on the nature of that specific collaboration. This lesson introduces the concept-level trade-offs; Lesson 06 goes deep on the mechanics and failure behavior of synchronous vs. asynchronous communication, and Lesson 08 covers how event-based communication underpins sagas for distributed transactions.

## How it works

### Request-response, conceptually

A calls B and needs an answer to proceed: "is this item in stock?" "what is this customer's shipping address?" This is the natural fit when A's own logic genuinely cannot continue without B's answer — it's a *query* or a *command that needs a synchronous result* (e.g., "reserve this item," which must succeed or fail before checkout can proceed). Request-response is easy to reason about locally: read the code, see the call, see what happens with the result, roughly like reading a single-threaded function.

The cost: A is now coupled *in time* to B being available and reasonably fast (temporal coupling, Lesson 03) — this is developed fully in Lesson 06.

### Event-based, conceptually

A does something significant (places an order) and announces it as a fact: `OrderPlaced { orderId, customerId, items, total }`. A does not know or care whether Inventory, Shipping-notifications, Analytics, or Fraud-detection are listening; it just publishes the fact and moves on. Any number of other services can subscribe and react — reserve stock, send a confirmation email, update a dashboard, run a fraud check — entirely independently, on their own timeline, without A waiting for any of them or even being aware they exist.

This inverts the coupling relationship: A is not coupled to *who* reacts to the event or *how many* services react — new subscribers can be added later with zero change to A. The trade-off is that A no longer has a synchronous answer — if Inventory's stock-reservation reaction fails, A finds out later (if at all directly), not in the same call. Reasoning about "what happens after `OrderPlaced`" now requires understanding a distributed, asynchronous flow rather than reading one call stack — this is the core cost, expanded in Lesson 06 and Lesson 13 (tracing this kind of flow is exactly what correlation IDs are for).

### Orchestration vs. choreography: who coordinates a multi-step process?

When a business process spans several services and steps — place order, reserve inventory, charge payment, ship — someone or something needs to know the sequence and handle what happens when a step fails. There are two structural answers, both usable with event-based communication:

**Orchestration**: a central coordinator (an orchestrator service, or explicit workflow logic within one service) explicitly calls each participant in sequence, tracks the state of the whole process, and decides what to do on failure (e.g., trigger compensating actions). It's directive: "Order Orchestrator, do step 1, then step 2, then step 3."

```
        +-------------------+
        | Order Orchestrator|
        +-------------------+
         |       |       |
         v       v       v
     Payment  Inventory Shipping
```

**Choreography**: there is no central coordinator. Each service reacts to events from other services and emits its own events in turn, and the overall process emerges from these local reactions chaining together, like dancers each following their own steps in response to the music and each other, without a choreographer directing them from the front.

```
Order --(OrderPlaced)--> Payment --(PaymentAuthorized)--> Inventory --(InventoryReserved)--> Shipping
```

Both are legitimate and both are used in the sagas that answer distributed transactions (Lesson 08 covers this trade-off with a full worked example including compensating actions; the deep, exhaustive pattern catalog for saga coordination lives in `hard-parts/14`, "Transactional Sagas" — this lesson and Lesson 08 introduce the concept at the level Newman presents it in the book, which is more about *when to reach for which style* than an exhaustive pattern taxonomy).

The trade-off, at a glance:

| | Orchestration | Choreography |
|---|---|---|
| Where is the process logic? | Centralized, explicit, in one place | Distributed across every participating service |
| Easy to see the whole flow? | Yes — read the orchestrator | No — must trace events across services |
| Coupling | Orchestrator is coupled to every participant it calls | Each service only knows the events it listens to/emits, not the whole flow |
| Adding a new step/participant | Change the orchestrator | Add a new listener; no change to existing services (often) |
| Risk | Orchestrator becomes a de facto "god service" that knows too much | Process logic becomes invisible/implicit, hard to debug ("where did this order actually go?") |

Newman's practical steer: orchestration tends to be easier to understand and debug for a small number of tightly sequenced steps, especially where failure handling needs central, explicit compensating logic. Choreography tends to fit better when the set of interested parties is open-ended and growing (many independent consumers reacting to the same fact, like `OrderPlaced` triggering email, analytics, fraud-check, and loyalty-points services that don't need to know about each other) — forcing that through a central orchestrator would make the orchestrator a bottleneck that has to be touched every time a new, unrelated consumer is added.

### Worked example: the trade-off in one flow

Consider "customer places an order" implemented two ways.

**Request-response chain**: `order-service` calls `payment-service` synchronously to authorize payment, waits, then calls `inventory-service` synchronously to reserve stock, waits, then returns success to the customer. Easy to follow, and the customer gets an immediate, definitive yes/no. But `order-service` is now temporally coupled to both `payment-service` and `inventory-service` being up and fast (Lesson 03, Lesson 06); if `inventory-service` is slow, the customer's checkout hangs.

**Event-based / choreographed**: `order-service` publishes `OrderPlaced` and immediately tells the customer "order received, confirming shortly." `payment-service` listens, authorizes, and publishes `PaymentAuthorized` (or `PaymentFailed`). `inventory-service` listens for `PaymentAuthorized` and reserves stock, publishing `InventoryReserved` or `InventoryUnavailable`. A notification service listens for the final state and emails the customer. No service blocks on another; `order-service`'s own request completes fast. But the customer no longer gets an instant definitive answer — the system is eventually consistent, and building a good customer experience around "we'll let you know" (rather than an immediate yes/no) is itself a design problem, not a purely technical one.

Neither is "correct" in general — the right choice depends on whether the interaction genuinely needs an immediate answer (favor request-response) or can tolerate eventual resolution in exchange for looser coupling (favor event-based), and Lesson 06 gives the deeper mechanical reasoning for making that call.

## Pros
- **Request-response**: simple to reason about, gives an immediate answer, familiar programming model.
- **Event-based**: loose coupling (publishers don't know or care about subscribers), natural fit for one-to-many reactions, subscribers can be added without touching the publisher.
- **Orchestration**: process logic is centralized and explicit — easy to see the whole flow and to implement centralized failure/compensation handling.
- **Choreography**: no single service needs to know the whole process; adding new reactions to an existing event requires no change to the publisher.

## Cons
- **Request-response**: creates temporal coupling — caller's availability and latency become bound to callee's (Lesson 06, Lesson 14).
- **Event-based**: harder to reason about the end-to-end flow, no immediate answer, requires infrastructure (a broker/event stream) and its own operational concerns (Lesson 06).
- **Orchestration**: the orchestrator can become a bottleneck and a "god service" that accumulates too much knowledge of every participant.
- **Choreography**: the overall business process becomes implicit — nobody can read one place to understand "what happens when an order is placed," which makes debugging and onboarding harder without good tracing (Lesson 13).

## Alternatives
- **Hybrid approaches** — most real systems mix styles: synchronous request-response for reads/queries that need an immediate answer, events for state-change notifications and cross-service side effects, and orchestration for the small number of complex, must-be-reliable workflows (e.g., payment/refund flows) while using choreography for open-ended fan-out reactions (e.g., analytics, notifications).
- **API composition / backend-for-frontend** — for read-heavy aggregation across services, sometimes neither pure request-response chains nor events are the right tool; an aggregating layer queries several services and composes the result (touched on in Lesson 07 as an answer to cross-service queries).

## When to use it
- **Request-response** when the caller genuinely cannot proceed without the answer, or the interaction is a simple query with a clear, immediate right answer.
- **Event-based** when other services need to react to a fact but the publisher doesn't need (or want) to know who they are, or when decoupling availability from downstream consumers matters more than instant consistency.
- **Orchestration** for a small number of tightly-sequenced, must-be-correct steps with centralized failure handling (e.g., an order-fulfillment saga).
- **Choreography** for an open-ended, growing set of independent reactions to the same event.

## When NOT to use it
- Don't default to synchronous chains for everything just because it's the familiar model — long synchronous chains across many services are one of the most common causes of cascading failure in production microservice systems (Lesson 06, Lesson 14).
- Don't default to choreography for a small, tightly-coupled, must-be-reliable process where explicit centralized control over failure/compensation is actually what you need — the implicit, distributed logic of choreography can make such a process much harder to operate correctly.

## Key takeaways / mental model
Two axes, two decisions. Axis one: does this specific interaction need an immediate answer (request-response) or can it tolerate "I'll react when I get to it" (event-based)? Axis two, only for multi-step processes: does the flow need a single place that knows and controls the whole sequence (orchestration), or can it emerge from independent local reactions (choreography)? Make the choice per-interaction, not once for the whole system — most real systems use all four combinations somewhere.

## Self-check questions
1. Why does event-based communication reduce coupling between the publisher and its consumers compared to a synchronous call, even though "someone" still has to process the event eventually?
2. Give one scenario where orchestration is clearly the better fit, and one where choreography is clearly the better fit. What made the difference?
3. In the choreographed order-placement example, what happens to the customer's experience compared to the request-response version, and what non-technical design problem does that create?
4. A team implements a five-step business process purely via choreography and later struggles to answer "why did this specific order get stuck?" What trade-off from this lesson explains that difficulty, and what would help (hint: see Lesson 13)?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 5: "Microservice Communication Styles"
- Related: `hard-parts/13` (Distributed Workflows: Orchestration and Choreography) for a deeper, pattern-catalog-level treatment of coordination styles; `building-microservices/08` for the saga pattern built on top of these communication styles.
