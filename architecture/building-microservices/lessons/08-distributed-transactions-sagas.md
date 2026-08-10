---
id: building-microservices/08
subject: building-microservices
title: "Distributed Transactions and Sagas"
slug: distributed-transactions-sagas
status: drafted
mastery: 
seniority: senior
source: "Building Microservices, 2nd ed. (Sam Newman), Chapter 6"
prerequisites: [building-microservices/05, building-microservices/07, hard-parts/14]
created: 2026-08-10
updated: 2026-08-10
---

# Distributed Transactions and Sagas

## TL;DR
Once each service owns its own database (Lesson 07), you can no longer wrap a multi-service business operation in a single ACID transaction. A **saga** is the practical answer: a sequence of local transactions, one per service, where failures are handled by explicitly running **compensating actions** to semantically undo the steps that already committed. Sagas can be **orchestrated** (a central coordinator drives the sequence and failure handling) or **choreographed** (each service reacts to the previous step's event and emits its own) — this lesson covers sagas at the practitioner level Newman presents them; the exhaustive eight-pattern catalog for saga coordination lives in `hard-parts/14`.

## The idea
Lesson 07 established that database-per-service means giving up cross-service joins and, more painfully, cross-service ACID transactions. This lesson is about that second loss specifically: how do you get a "place order → reserve inventory → charge payment → arrange shipping" business operation to behave *consistently* — either the whole thing succeeds, or it's cleanly and visibly undone — when each step commits to a different service's separate database, and there is no single database transaction manager spanning all of them?

In a monolith, this was one transaction: `BEGIN; <all four steps>; COMMIT;` — if payment fails, the whole thing rolls back atomically, and nothing else in the system ever observed the partial state. A **distributed transaction** in the classical sense (two-phase commit, XA transactions) tries to replicate this across services by having a coordinator ask every participant to "prepare" to commit, then tell them all to actually commit only if everyone agreed — but this requires every participant to hold locks while waiting for the coordinator's decision, which couples every participant's availability to the coordinator's and to every other participant's (exactly the temporal coupling Lesson 03 and Lesson 06 warn against), and doesn't play well with heterogeneous datastores or long-running business processes. Newman, along with most of the industry, treats two-phase commit as a poor fit for microservices in practice.

The **saga pattern** (originally from a 1987 database paper by Garcia-Molina and Salengut, adapted to microservices) gives up global atomicity and replaces it with something weaker but achievable: a sequence of independent local transactions, each of which commits (or aborts) entirely within one service, with explicit **compensating transactions** defined for each step to undo its effects if a later step in the sequence fails. The business operation as a whole is not atomic in the ACID sense — for a window of time, the system can be in a partially-completed state that's visible to other parts of the system — but it is guaranteed to eventually reach either "fully completed" or "fully compensated back to a consistent state," never stuck half-done forever.

## How it works

### The core mechanism: local transactions + compensating actions

A saga is: `T1, T2, T3, ..., Tn`, a sequence of local transactions, each in one service. If `Tk` fails, the saga runs compensating transactions `Ck-1, Ck-2, ..., C1` in reverse order for every step that already committed, semantically undoing them. Note "semantically undoing," not "rolling back a database transaction" — a compensating action is business logic, not a database rollback. If `PaymentAuthorized` already happened and a later step fails, you don't "un-happen" the authorization at the database level; you issue a `RefundPayment` compensating action, which is itself a new, forward-moving business operation that reverses the effect.

### Worked example: order placement saga with compensations

Steps: `ReserveInventory` (inventory-service) → `AuthorizePayment` (payment-service) → `ConfirmOrder` (order-service) → `ScheduleShipment` (shipping-service).

Each step has a defined compensating action:

| Step | Forward action | Compensating action |
|---|---|---|
| 1 | `ReserveInventory` | `ReleaseInventory` |
| 2 | `AuthorizePayment` | `RefundPayment` (or `VoidAuthorization` if not yet captured) |
| 3 | `ConfirmOrder` | `CancelOrder` |
| 4 | `ScheduleShipment` | `CancelShipment` |

Happy path: all four steps succeed in order; the saga completes with a confirmed, paid, shipped order.

Failure path: suppose steps 1 and 2 succeed (inventory reserved, payment authorized), but step 3 (`ConfirmOrder`) fails — say, a business rule rejects the order because the shipping address is in a restricted region, discovered only at this step. The saga now runs compensations in reverse for the steps that already committed: `RefundPayment` (undo step 2), then `ReleaseInventory` (undo step 1). Step 4 never ran, so it needs no compensation. The end state: no order confirmed, payment refunded, inventory released — a consistent, fully-compensated outcome, even though it took several separate local transactions and a temporary in-between state to get there.

### Orchestrated sagas

A central **saga orchestrator** (an explicit piece of coordination logic, often modeled as its own service or a workflow engine) drives the sequence directly: it calls `ReserveInventory`, waits for success, calls `AuthorizePayment`, waits for success, and so on, tracking the saga's state explicitly (e.g., in its own persistence: "this saga is at step 2, steps 1-2 completed"). On a failure at any step, the orchestrator is the one that knows which compensations to run and in what order, and it runs them.

```
                +----------------------+
                |   Order Orchestrator |
                |  (tracks saga state) |
                +----------------------+
                 |   |    |    |
        step1    v   v    v    v   step4
   +--------+ +-------+ +-----+ +--------+
   |Inventory| |Payment| |Order| |Shipping|
   +--------+ +-------+ +-----+ +--------+
```

This mirrors the orchestration style from Lesson 05: the orchestrator explicitly knows and controls the whole flow, including failure handling. This makes the process easy to see and reason about in one place (you can read the orchestrator's code and know exactly what the saga does, in what order, and how it compensates), and centralizes the compensating-action bookkeeping. The cost: the orchestrator is coupled to every participant it calls, and becomes an important, must-be-reliable piece of infrastructure in its own right — if the orchestrator itself is down or loses its saga state, the in-flight saga can get stuck.

### Choreographed sagas

No central coordinator. Each service reacts to the previous step's event and, on success, emits its own event that the next service listens for; on failure, it emits a failure event, and every service that already committed a step listens for that failure (or a downstream compensation-triggering event) and runs its own compensating action independently.

```
Order --(OrderPlaced)--> Inventory --(InventoryReserved)--> Payment --(PaymentAuthorized)--> Order(confirm) --> Shipping
                              |                                    |
                       (if fails: InventoryUnavailable)     (if fails: PaymentFailed)
                                                                    |
                                                    Inventory listens for PaymentFailed
                                                    and runs ReleaseInventory itself
```

Concretely, in the same failure scenario as above (step 3, `ConfirmOrder`, fails business validation): `order-service` publishes `OrderConfirmationFailed`. `payment-service`, which is listening for exactly this event (because it knows its own step might need to be undone if a later step fails), reacts by running `RefundPayment` itself and publishing `PaymentRefunded`. `inventory-service`, listening for `PaymentRefunded` (or directly for `OrderConfirmationFailed`, depending on how the choreography is wired), reacts by running `ReleaseInventory` itself.

The advantage: no single orchestrator to build, deploy, and keep reliable; each service only needs to know the events relevant to its own step, mirroring the loose coupling of choreography from Lesson 05. The cost, and it's a real one at saga scale: the overall compensation logic is now scattered across every participating service, each independently knowing which events trigger its own compensating action — there is no single place to read "what does this saga do end to end," which makes reasoning about correctness and debugging a stuck or partially-compensated saga significantly harder as the number of steps grows. This is the same orchestration-vs-choreography trade-off from Lesson 05, now applied specifically to the failure-handling logic of a multi-step transaction, where the stakes of "hard to trace" are higher because money and state consistency are directly on the line.

### The catch: compensating actions aren't always clean, and isolation is weaker

Two important caveats Newman is careful to flag:

1. **Not every action is cleanly compensable.** `RefundPayment` is easy to define. `SendConfirmationEmail` is much harder — you can't "un-send" an email; the best you can typically do is send a follow-up ("disregard the previous email, your order was cancelled"). Some saga steps are better placed *last* in the sequence, specifically because they're hard or impossible to compensate (irreversible steps generally belong as late in the saga as possible, after all the easily-reversible steps that could still fail).
2. **Sagas give up isolation, not just atomicity.** Between steps 2 and 3 in the worked example, the system is in a state where payment is authorized but the order isn't yet confirmed — and other parts of the system (a customer checking order status, an analytics dashboard) can observe this intermediate, not-yet-final state. In a single ACID transaction, nobody outside the transaction ever sees a partial state (that's what isolation guarantees); a saga has no equivalent guarantee. Designing for this — showing a customer a "processing" status rather than a premature "confirmed," for instance — is real, necessary product/UX work, not an edge case to ignore.

## Pros
- **Makes multi-service business transactions possible at all**, without the availability and locking cost of two-phase commit.
- **Failures are handled explicitly and observably**, via defined compensating actions, rather than being an undefined or manually-fixed state.
- **Fits naturally with the event-based communication style** already needed for loose coupling between services (Lesson 05, Lesson 06).

## Cons
- **Gives up isolation** — intermediate, partially-completed states are observable by the rest of the system, and product/UX must account for this.
- **Compensating actions must be designed explicitly for every step**, and not every action is cleanly reversible (e.g., sending an email, calling an external non-refundable service).
- **Choreographed sagas scatter compensation logic across every participant**, making it hard to see or verify the whole flow's correctness in one place as the saga grows.
- **Orchestrated sagas introduce a critical piece of coordination infrastructure** that must itself be reliable and must persist saga state durably, or in-flight sagas can get stuck.

## Alternatives
- **Two-phase commit / distributed (XA) transactions** — gives true atomicity and isolation across services, but at the cost of blocking locks held across the network while every participant waits on the coordinator's decision; poor fit for microservices' availability goals, largely rejected in practice for this reason.
- **Avoid the need for a distributed transaction entirely** — sometimes the real fix is a boundary redesign (Lesson 02, Lesson 03): if two operations always need to be atomic together, that's often a signal they shouldn't have been split into two separate services' data ownership in the first place.
- **Best-effort eventual consistency without formal sagas** — for genuinely low-stakes side effects (e.g., updating a "recently viewed" cache), sometimes explicit saga/compensation machinery is overkill and "eventually correct, and it's fine if it's occasionally slightly off" is an acceptable, much simpler answer.

## When to use it
- Any business operation that must update state consistently across two or more services that each own their own data, where the operation can fail partway through and needs a well-defined, observable way to unwind.
- Orchestration when the process is complex, the stakes are high (money, compliance), and centralized visibility into the whole flow's state and failure handling is valuable.
- Choreography when the set of reacting participants is naturally open-ended and loosely coupled, and the process itself is relatively simple.

## When NOT to use it
- Don't reach for a saga (or any cross-service transaction machinery) when a boundary redesign would eliminate the need — if two pieces of data are always written together and never independently, that's a cohesion signal (Lesson 03) they may belong in the same service.
- Don't use sagas for operations where losing isolation is unacceptable and correctness genuinely requires strict atomicity across the data involved — that's a sign the operation's data shouldn't be split across service boundaries in the first place, rather than a case for forcing a saga to paper over it.

## Key takeaways / mental model
A saga trades atomicity and isolation for availability and service autonomy: instead of one all-or-nothing transaction, it's a sequence of local transactions with explicit, business-defined "undo" logic (compensating actions) for the case where a later step fails. Orchestration centralizes that sequencing and failure logic in one place, easy to read but coupled to every participant; choreography distributes it as independent reactions to events, loosely coupled but hard to see as a whole. Order steps so the hardest-to-compensate actions happen last, and design the product experience around the fact that intermediate states are now visible to the rest of the system. For the full eight-pattern catalog of saga coordination and compensation techniques, see `hard-parts/14`.

## Self-check questions
1. Why does Newman (and the industry generally) avoid two-phase commit for microservices, even though it offers true cross-service atomicity?
2. Walk through the order-placement saga worked example: if `ScheduleShipment` (step 4) fails after all prior steps succeeded, what compensating actions run, and in what order?
3. Give an example of a saga step that is very hard to cleanly compensate, and explain how ordering the saga's steps can reduce the impact of that difficulty.
4. What does it mean that "sagas give up isolation," and what concrete product/UX consequence does that have for a customer-facing order flow?
5. When would you choose an orchestrated saga over a choreographed one for the same business process? What's the deciding factor?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 6: "Workflow"
- Hector Garcia-Molina and Kenneth Salem, "Sagas" (ACM SIGMOD, 1987) — the original saga pattern for long-lived transactions.
- `hard-parts/14` (Transactional Sagas) — the exhaustive catalog of saga coordination and compensation patterns, for depth beyond the practitioner-level treatment here.
