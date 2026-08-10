---
id: implementing-ddd/15
subject: implementing-ddd
title: Sagas and process managers for long-running consistency
slug: sagas-and-process-managers-for-long-running-consistency
status: drafted
mastery:
seniority: staff
source: Implementing Domain-Driven Design (Vaughn Vernon), Chapter 4 (Architecture) and Chapter 8 (Domain Events) — long-running processes
prerequisites: [implementing-ddd/06, implementing-ddd/12, implementing-ddd/14]
created: 2026-08-10
updated: 2026-08-10
---

# Sagas and process managers for long-running consistency

## TL;DR
A saga (or process manager) is a stateful coordinator that drives a multi-step business process spanning several aggregates or bounded contexts to completion, reacting to each step's outcome and issuing compensating actions when a step fails — it's the pattern that makes eventual consistency (`implementing-ddd/06`) *safe* for processes that must reach a definite, correct final outcome rather than being left indefinitely half-done.

## The idea
Eventual consistency (`implementing-ddd/06`) tells you that cross-aggregate processes happen in separate transactions with a tolerable lag between them — but it doesn't, by itself, answer "what happens if step two fails after step one already succeeded?" A domain event handler that reacts to `OrderPlaced` by reserving inventory is fine as long as the reservation succeeds; if it fails (out of stock, a downstream service is down), something has to notice the process is now stuck in an inconsistent state (an order marked placed with no inventory reserved) and either retry, escalate, or unwind the first step (cancel the order, notify the customer). A saga is that "something": explicit, durable, coordinating logic that tracks a multi-step process's state, knows what step comes next given what's happened so far, and knows how to compensate (undo, in business terms — not a database rollback) if a step can't complete.

## How it works

### Choreography vs. orchestration
There are two structurally different ways to implement a saga:
- **Choreography** — no central coordinator; each participating aggregate/context reacts to events from the others and raises its own events in turn, and the "process" emerges from the chain of reactions. Simpler to start (no new component), but the overall process logic is implicit, scattered across every participant's event handlers — understanding "what happens when an order is placed, end to end" requires reading code in several different places.
- **Orchestration (process manager)** — a dedicated, explicit component owns the process state and actively directs each step (send this command, wait for that event, then send the next command), rather than each participant reacting independently. Vernon generally favors orchestration for processes of real complexity, because the process logic is centralized, testable as a unit, and visible in one place — at the cost of introducing a new stateful component that itself needs to be built, deployed, and made reliable.

### Worked example — order fulfillment saga (orchestration style)
An order-placement-to-fulfillment process spans `Order`, `Inventory`, and `Payment` — three separate aggregates, possibly three separate bounded contexts. A `OrderFulfillmentSaga` process manager tracks state explicitly:
```
class OrderFulfillmentSaga {
    enum State { STARTED, INVENTORY_RESERVED, PAYMENT_CHARGED, COMPLETED, COMPENSATING, FAILED }
    private State state = State.STARTED;
    private OrderId orderId;

    void on(OrderPlaced event) {
        this.orderId = event.orderId();
        commandBus.send(new ReserveInventory(event.orderId(), event.lineItems()));
    }

    void on(InventoryReserved event) {
        state = State.INVENTORY_RESERVED;
        commandBus.send(new ChargePayment(orderId, event.totalAmount()));
    }

    void on(InventoryReservationFailed event) {
        state = State.FAILED;
        commandBus.send(new CancelOrder(orderId, "inventory unavailable"));
    }

    void on(PaymentCharged event) {
        state = State.COMPLETED;
        commandBus.send(new ConfirmOrder(orderId));
    }

    void on(PaymentFailed event) {
        state = State.COMPENSATING;
        commandBus.send(new ReleaseInventoryReservation(orderId));  // compensating action
        commandBus.send(new CancelOrder(orderId, "payment failed"));
    }
}
```
The saga's state must itself be persisted durably (typically in its own small aggregate-like store) so that if the process crashes mid-flight, it can be reloaded and resume exactly where it left off — a saga that only lives in memory would lose track of in-flight processes on any restart, silently abandoning them.

### Compensating actions, not rollback
The key conceptual shift from a single-transaction rollback: once `InventoryReserved` has actually happened (committed, visible to other parts of the system), you cannot simply "undo" it the way a database transaction rolls back uncommitted changes — you have to issue an explicit, meaningful compensating business action (`ReleaseInventoryReservation`) that itself is a real operation with its own consequences, possibly its own further failure modes, and its own domain event. Compensating actions are business logic, not infrastructure — deciding what "undo" means for a given step is itself a domain design decision (e.g. does releasing a reservation restock immediately, or after a grace period in case the failure was transient?).

### Timeouts and stuck processes
A saga waiting for a step's response also needs to handle "the response never came" — a timeout that triggers either a retry or a move to a compensating/failed state, rather than waiting indefinitely. This is a genuinely distinct failure mode from an explicit failure event and needs its own explicit handling in the process manager's design.

**Worked example — banking (funds transfer saga, revisiting `implementing-ddd/04`'s and `implementing-ddd/06`'s example).** The `FundsTransferSaga` tracks a transfer between two `Account` aggregates: it issues `WithdrawFunds` to the source account, and on `FundsWithdrawn`, issues `DepositFunds` to the destination account. If the deposit step fails (destination account closed, for instance), the saga issues a compensating `DepositFunds` back into the *source* account (crediting the withdrawn amount back) rather than leaving the money in limbo — the compensating action here is itself a real, auditable financial transaction, not a silent rollback.

## Pros
- Makes multi-step, cross-aggregate/cross-context business processes explicit and centrally reasoned-about (in the orchestration style), rather than leaving "what happens end to end when an order is placed" implicit and scattered across independent event handlers.
- Provides a principled way to handle partial failure in an eventually-consistent system — without a saga, a failed second step in a multi-aggregate process has no defined recovery path and silently leaves the system inconsistent.
- Compensating actions, expressed in business terms, keep failure-handling logic in the domain model's vocabulary rather than degrading into ad hoc technical error handling.

## Cons
- A saga/process manager is itself a new, stateful component that needs its own durable persistence, needs to be resumable after a crash, and needs its own monitoring (is any saga stuck? how many are in a `COMPENSATING` state right now?) — real, ongoing operational overhead beyond the business logic itself.
- Designing correct compensating actions is genuinely hard domain design work, not a mechanical inversion of the forward action — "undo a payment" is a business decision (refund? partial refund? store credit?) that requires real domain expertise to get right, not just a technical rollback.
- Choreography-style sagas, while requiring no new component, become very difficult to understand and debug as the number of participating steps grows — there's a real trade-off between the simplicity of adding no new infrastructure and the clarity of centralizing process logic.

## Alternatives
- **Choreography (event chains with no central coordinator)** — simpler for short processes (two or three steps) where each participant reacting to the previous step's event is easy to follow; degrades in clarity as the process grows longer or needs richer failure handling, since there's no single place that shows the whole process.
- **Distributed transactions (two-phase commit)** — avoid the need for compensating actions entirely by keeping the whole multi-step process in one atomic transaction; as discussed in `implementing-ddd/06`, this reintroduces severe scalability and availability costs and is rarely appropriate across aggregate or service boundaries.
- **Manual/human-in-the-loop reconciliation** — for genuinely rare failure cases, skip automated compensation and instead surface a stuck process to a human operator (a support queue, an ops dashboard) to resolve manually; appropriate when the failure is rare enough, and the compensating logic complex enough, that automating it isn't worth the engineering investment relative to occasional manual handling.

## When to use it
For any business process that spans more than two steps across separate aggregates or bounded contexts, especially where failure at any step needs a defined, business-meaningful recovery path — order fulfillment, financial transfers, multi-party workflows, provisioning processes with several external dependencies.

## When NOT to use it
For a simple two-aggregate eventually-consistent update where failure is rare and easily handled by a straightforward retry or manual intervention, a full saga/process-manager component is likely overkill — plain event-driven eventual consistency (`implementing-ddd/06`, `implementing-ddd/12`) without a dedicated coordinator is often sufficient, reserving saga complexity for processes that genuinely need multi-step tracking and compensation.

## Key takeaways / mental model
A saga exists to answer one question a plain domain-event handler can't: "if this multi-step process gets partway done and then a step fails, what happens next, and who's responsible for making sure the system doesn't get stuck in that half-done state forever?" If a process has more than a couple of steps or a real need for compensation logic, that responsibility needs an explicit, durable owner — the saga.

## Self-check questions
1. Take a multi-step process from a system you know (e.g. checkout, user onboarding, provisioning). List its steps and, for each, what a sensible compensating action would look like if that step's predecessor already succeeded but this step fails.
2. Explain the difference between choreography and orchestration sagas, and give a concrete signal that would tell you a choreography-style implementation has grown complex enough to warrant switching to orchestration.
3. Why must a saga's state be persisted durably rather than kept only in memory? What specifically goes wrong if it isn't?
4. Why is "compensating action" a more accurate term than "rollback" for what a saga does when a later step fails? Use the funds-transfer example to justify your answer.

## References
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 4: "Architecture" (long-running processes, sagas).
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 8: "Domain Events" (process managers reacting to events).
