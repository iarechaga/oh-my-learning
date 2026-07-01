---
id: microservices-patterns/04
subject: microservices-patterns
title: "Managing Transactions with Sagas"
slug: sagas
status: drafted
mastery:
seniority: senior
source: "Microservices Patterns (Chris Richardson), Chapter 4"
prerequisites: [microservices-patterns/03]
created: 2026-07-01
updated: 2026-07-01
---

# Managing Transactions with Sagas

## TL;DR
Once each service owns its own database, a business operation that spans several services can no longer use a single ACID transaction - there is no shared database to commit across. A **saga** replaces the one big transaction with a sequence of *local* transactions, one per service, coordinated by asynchronous messages; if a step fails, the saga runs **compensating transactions** to semantically undo the steps that already committed. The price you pay is giving up atomicity and isolation: a saga is eventually consistent and its intermediate states are visible, so you must design explicitly for partial failure and for anomalies that a database would have hidden.

## The idea
In a monolith, "place an order" might, in one ACID transaction, create the order, reserve credit on the customer's account, and create a kitchen ticket - all committed together or all rolled back. ACID guarantees this is atomic (all-or-nothing), consistent, isolated (concurrent transactions don't interfere), and durable.

Microservices break this. With **database-per-service**, the order lives in `Order Service`'s database, credit in `Accounting Service`'s, and the ticket in `Kitchen Service`'s. There is no transaction manager spanning three separate databases (and distributed two-phase commit, 2PC, is generally rejected in microservices: it hurts availability - a blocked coordinator stalls everyone - and many modern datastores and message brokers don't support it). So the classic question is: **how do you keep data consistent across services without a distributed transaction?**

The answer is the **saga**: model the operation as a sequence of local transactions `T1, T2, ..., Tn`, each in one service, each committing to *that service's* database and then triggering the next step via a message or event. Because there is no global rollback, a saga handles failure differently: if step `Ti` fails, the saga executes **compensating transactions** `Ci-1, ..., C1` that semantically undo the effects of the steps that already committed. "Semantically undo" is key - you cannot un-commit a committed transaction, so you issue a *new* transaction that reverses its business effect (refund the charge, cancel the ticket).

This trade is the heart of the lesson: you regain the ability to operate across services, but you **lose atomicity and isolation**. A saga is not a transaction; it is a state machine that must cope with the messy reality that some steps have committed while others have not.

## How it works

### Local transactions chained by messages
A saga is `T1 -> T2 -> ... -> Tn`, where each `Ti` is an ordinary ACID transaction *within one service*, and the completion of `Ti` reliably triggers `Ti+1`. "Reliably triggers" matters: the message that starts the next step must be sent atomically with the local transaction (otherwise you commit the DB change but lose the message, or send the message but the DB change rolls back). That atomic "commit-and-publish" is the **transactional outbox** pattern - write the outgoing message into an `outbox` table in the *same* local transaction, then a relay reads the outbox and publishes it. (This connects to reliable messaging in lesson 03.)

```text
Order Service        Accounting Service      Kitchen Service
  T1: create order      T2: authorize card      T3: create ticket
  (PENDING) --msg-->     (reserve $) --msg-->     (ticket)
  local ACID            local ACID               local ACID
  + outbox publish      + outbox publish         + outbox publish
```

### Compensating transactions: undoing what cannot be rolled back
If a later step fails, the saga rewinds by running compensations in reverse for every step that already committed:

- `T1 create order` is compensated by `C1 reject/cancel order`.
- `T2 authorize card` is compensated by `C2 reverse authorization / refund`.
- `T3 create ticket` is compensated by `C3 cancel ticket`.

Compensations are themselves local transactions and must be **idempotent** and **guaranteed to eventually succeed** (a compensation that can fail leaves the system inconsistent, so it must be retried until it does). Not every step needs a compensation: steps are classified as **compensatable** (can be undone: create order), **pivot** (the point of no return - once it commits, the saga will run forward to completion; e.g. capturing payment), and **retriable** (steps after the pivot that only go forward and must eventually succeed, so they are retried, never compensated). Ordering the saga so that risky/failable checks happen *before* the pivot, and only guaranteed-to-succeed steps happen after, is a core design skill.

```text
  compensatable steps   |  PIVOT   |   retriable steps
  T1 --- T2 --- T3       |  T4      |   T5 --- T6
  (can be compensated)   | (commit  |   (only retried forward,
   if a later step fails |  point of|    never undone)
                          no return)
```

### Two coordination styles: choreography vs orchestration
A saga needs coordination logic - "when step N finishes, do step N+1; on failure, compensate." There are two ways to place it, and choosing is a real architectural decision (see [hard-parts/13 - orchestration vs choreography](../../hard-parts/lessons/13-distributed-workflows-orchestration-choreography.md)).

- **Choreography (event-driven, decentralized):** there is no central coordinator. Each service publishes **domain events** when its local transaction commits, and other services **subscribe** and react. `Order Service` publishes `OrderCreated`; `Accounting` hears it, authorizes the card, and publishes `CardAuthorized`; `Kitchen` hears *that* and creates a ticket. The saga logic is distributed across the participants' event handlers.
  - Good for: simple sagas, few participants, loose coupling.
  - Bad for: complex flows - the logic is smeared across many services, cyclic event dependencies appear, and no single place describes "what the saga does," making it hard to understand and to know if it completed.

- **Orchestration (centralized):** a dedicated **saga orchestrator** (often an object with an explicit state machine) tells each participant what to do via **command messages** and receives replies. The orchestrator holds the whole flow: send `AuthorizeCard` to Accounting; on `CardAuthorized`, send `CreateTicket` to Kitchen; on any failure, send the compensations.
  - Good for: complex sagas - the logic lives in one place, dependencies are simpler (star, not web), and the orchestrator explicitly tracks saga state and completion.
  - Bad for: risk of a "smart orchestrator, dumb services" god component if you push business logic that belongs in services into the orchestrator.

The book's guidance: use **choreography for simple sagas**, **orchestration for complex ones** - and orchestration is the more common production choice as flows grow.

### The hard part: no isolation, and the countermeasures
A database gives **isolation** - concurrent transactions appear to run one at a time, so you never see another transaction's half-done state. Sagas have **no isolation**: because each step commits independently, the partial results of an in-flight saga are *visible* to other transactions, which can cause anomalies:

- **Lost updates:** one saga overwrites changes another saga made without reading them.
- **Dirty reads:** a saga reads data that another saga wrote but will later compensate (undo).
- **Fuzzy/non-repeatable reads:** a saga reads the same data twice and gets different values because another saga wrote between the reads.

Concrete example: saga A creates an order (`PENDING`) and, before it authorizes the card, saga B (or a user) reads that order and acts on it - but then A's card authorization fails and A compensates by canceling the order. B acted on data that was rolled back - a dirty read the database would have prevented.

Richardson prescribes **countermeasures** to manage the lack of isolation (you don't get isolation back, you *manage* its absence):

1. **Semantic lock:** mark records with an in-progress state (an `*_PENDING` status, like `Order = APPROVAL_PENDING`) so other transactions know the data is not final and can wait, fail, or handle it explicitly. This is an application-level lock.
2. **Commutative updates:** design updates so order doesn't matter (e.g. debit/credit that commute), so interleaving is safe.
3. **Pessimistic view:** reorder the saga's steps to minimize the business risk of dirty reads (do the step that, if seen partially, does least harm).
4. **Reread value:** before updating, re-read and verify the record hasn't changed (optimistic-offline-lock style) to catch lost updates.
5. **Version file / by-value:** record operations to detect and reorder out-of-order messages, or route by risk value.

These are not free - they add complexity to the business logic - which is exactly why sagas are a senior-level topic.

### Worked example 1: the FTGO Create Order saga, happy path
`createOrder` spans Order, Consumer, Accounting (Kitchen omitted for brevity), orchestrated.

1. `T1` Order Service: create `Order` in state `APPROVAL_PENDING` (semantic lock). Orchestrator starts.
2. Orchestrator sends `VerifyConsumer` command to Consumer Service. `T2`: Consumer verifies the consumer can place orders; replies OK.
3. Orchestrator sends `AuthorizeCard` to Accounting. `T4` (pivot): Accounting authorizes/charges the card; replies OK. This is the point of no return.
4. Orchestrator sends `ApproveOrder` to Order Service. `T5` (retriable): Order transitions `APPROVAL_PENDING -> APPROVED`.
5. Saga complete. The order is consistent across services - achieved without any distributed transaction, using one local transaction per service linked by commands/replies.

Note the semantic lock (`APPROVAL_PENDING`) covering the window between steps: any other transaction seeing the order knows it is not final.

### Worked example 2: a failure triggers compensation
Same saga, but the card authorization fails (insufficient funds).

1. `T1` create order `APPROVAL_PENDING`; `T2` verify consumer OK.
2. Orchestrator sends `AuthorizeCard`; Accounting replies **FAILED** (declined). This is *before* the pivot commits, so the saga must roll back the compensatable steps.
3. Orchestrator runs compensations in reverse for what committed:
   - `C2` (if the consumer step had side effects, undo them - here often a no-op).
   - `C1` Order Service: transition the order `APPROVAL_PENDING -> REJECTED` (the compensation for "create order"). We cannot delete the committed order row, so we issue a new transaction that sets it to a terminal rejected state.
4. The system is consistent again: no charge (authorization never succeeded), order marked `REJECTED`. The compensation `C1` must be idempotent - if the orchestrator retries it after a crash, setting `REJECTED` twice is harmless.

The example shows the defining behavior: **failure after partial commit is handled by forward-executed compensations, not by rollback.**

### Worked example 3: a dirty-read anomaly and the semantic-lock fix
Show the isolation gap concretely.

1. Saga A: create order `O-1` (`APPROVAL_PENDING`), then attempt card auth.
2. Meanwhile, a "current orders" report (transaction B) queries orders and *includes* `O-1` as an active order, emailing the restaurant "new order incoming."
3. Saga A's card auth fails; A compensates, setting `O-1 = REJECTED`.
4. Anomaly: the restaurant was told about an order that never really happened - transaction B performed a **dirty read** of A's uncommitted-in-spirit state.
5. Fix with a **semantic lock**: because `O-1` was in `APPROVAL_PENDING`, transaction B's query is written to *exclude* (or clearly flag) orders not yet `APPROVED`. B only acts on orders past the pivot. The `*_PENDING` status is the application-level lock that lets other transactions avoid acting on not-yet-final data - reclaiming, by convention, the safety a database's isolation would have given automatically.

## Pros
- **Enables cross-service business operations without distributed transactions** - maintains data consistency across a database-per-service architecture, which 2PC cannot do well.
- **Preserves service autonomy and availability** - each step is a local transaction; no blocking global coordinator, so one slow service doesn't lock the others (unlike 2PC).
- **Works with heterogeneous stores and brokers** - relies only on local transactions plus messaging, not on distributed-transaction support in every datastore.
- **Explicit failure handling** - compensations and the pivot/retriable classification make partial-failure recovery a first-class, designed part of the flow.

## Cons
- **No atomicity or isolation** - intermediate states are visible; you must add countermeasures (semantic locks, etc.) to prevent anomalies a database would have hidden.
- **Only eventual consistency** - there is a window where the system is partially updated; operations and clients must tolerate it.
- **Significant design complexity** - compensating transactions, idempotency, the pivot ordering, and isolation countermeasures are hard to get right and to test.
- **Harder to reason about and debug** - especially with choreography, where the flow is spread across services and "did it complete?" is non-obvious.

## Alternatives
- **Two-phase commit (2PC / XA distributed transactions):** true atomicity across resources, but rejected in most microservice designs - it blocks on the coordinator (hurting availability) and isn't supported by many NoSQL stores and brokers.
- **Keep the data in one service (avoid the distributed transaction):** if a set of data truly needs single-transaction consistency, that can be a signal the service boundary is wrong - merging it into one service replaces the saga with a local ACID transaction (relates to decomposition, lesson 02).
- **Choreography vs orchestration:** the two saga *coordination* styles - event-driven/decentralized vs command-driven/centralized - chosen by saga complexity.
- **Eventual consistency via plain domain events (no compensations):** for flows where steps only ever succeed-forward and never need undo, a pure event-driven propagation without saga rollback machinery can suffice.

## When to use it
- A business operation must update data owned by multiple services and you need those updates to be consistent, but a single ACID transaction is impossible (database-per-service).
- You can accept eventual consistency and design for visible intermediate states with countermeasures.
- The operation's steps can be given sensible compensations, and you can identify a pivot separating failable steps from guaranteed-forward ones.
- 2PC is unavailable or unacceptable (availability-critical system, heterogeneous stores).

## When NOT to use it
- The data can (and arguably should) live in a single service, so a local ACID transaction suffices - do that instead of a saga.
- The operation genuinely requires strong isolation/atomicity that you cannot safely emulate with countermeasures (e.g. certain financial invariants) - rethink the boundary or the requirement.
- A step has no meaningful compensation (its effect is irreversible and cannot be semantically undone) placed *before* the pivot - reorder so it is the pivot or later, or the saga cannot roll back correctly.
- The team cannot bear the added complexity and the flow is simple enough to keep in one service.

## Key takeaways / mental model
Think of a saga as a multi-leg trip booked separately (flight, hotel, car) with no single "cancel everything" button. You book each leg one at a time; if the car rental falls through after you've paid for the flight and hotel, you can't un-pay - you file *cancellations/refunds* (compensations) for the legs you already booked. And because each booking is confirmed independently, someone glancing at your itinerary mid-booking might see a half-planned trip (no isolation). Two rules of thumb:

1. **A saga trades ACID's atomicity and isolation for the ability to span services.** It is a sequence of local transactions linked by messages, with compensations replacing rollback and a pivot dividing "can still undo" from "must go forward." Design the ordering so failable steps come before the pivot.
2. **You don't get isolation back - you manage its absence.** Intermediate states are visible, so use semantic locks (`*_PENDING` statuses) and the other countermeasures to prevent dirty reads and lost updates; make every step and compensation idempotent; and choose choreography for simple sagas, orchestration for complex ones.

## Self-check questions
1. Why can't a business operation spanning three services use a single ACID transaction, and why does the book reject 2PC as the fix? What does a saga use instead?
2. What is a compensating transaction, why is it a *new* transaction rather than a rollback, and what two properties must every compensation have?
3. Explain the classification of saga steps into compensatable, pivot, and retriable. Why does ordering the saga around the pivot matter, and where should failable steps go?
4. Contrast choreography and orchestration for saga coordination. Give one saga where each is the better choice and say why.
5. Sagas lack isolation. Describe a concrete dirty-read anomaly in the Create Order saga and show how a semantic lock prevents it. Name two other countermeasures.
6. You must design a "transfer funds between two accounts in different services" saga. Identify the local transactions, the compensations, the pivot, and the isolation countermeasure you would apply, and explain what anomaly you are guarding against.

## References
- Microservices Patterns (Chris Richardson), Chapter 4: "Managing transactions with sagas"
- [hard-parts/14 - Transactional sagas](../../hard-parts/lessons/14-transactional-sagas.md)
- [ddia/11 - Transactions (ACID, isolation, serializability)](../../ddia/lessons/11-transactions.md)
