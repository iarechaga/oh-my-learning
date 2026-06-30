---
id: hard-parts/11
subject: hard-parts
title: Distributed Transactions and Eventual Consistency
slug: distributed-transactions-eventual-consistency
status: drafted
mastery:
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 9
prerequisites: [hard-parts/10, ddia/11, ddia/09]
created: 2026-06-30
updated: 2026-06-30
---

# Distributed Transactions and Eventual Consistency
## TL;DR
Once data is owned by multiple services, one business request can no longer rely on one local ACID transaction. You can force global atomicity with distributed transactions, but most teams avoid that because it hurts throughput, availability, and autonomy. The practical default is eventual consistency with explicit failure handling, retries, and compensating actions.

## The idea
Lesson 10 introduced service-level data ownership. That design is good architecture, but it changes transaction math.

Inside one service and one database, ACID gives strong guarantees with a clear commit point. Across services, each service commits locally and independently. A single business command now becomes a sequence of local commits separated by network calls.

That sequence creates a hard reality:

1. Step A can commit.
2. Step B can fail.
3. Other systems may already observe A.
4. There is no magic global rollback.

So the architectural problem is not "how do we keep pretending this is one DB transaction?" It is "how do we design convergence and recovery when local commits happen at different times?"

## How it works
The model has three layers: local guarantees (ACID), distributed trade-offs (BASE), and sync patterns to converge state.

### ACID and BASE from first principles
ACID describes guarantees of a transaction, usually within one service boundary.

- Atomicity: all operations in the transaction commit, or none do.
- Consistency: constraints/invariants remain valid before and after commit.
- Isolation: concurrent transactions do not leak partial intermediate state.
- Durability: committed data survives crashes.

BASE describes behavior you accept across distributed boundaries.

- Basically Available: prioritize staying up and answering requests.
- Soft state: replicas/projections may temporarily differ and continue changing.
- Eventual consistency: if updates stop and delivery continues, states converge.

ACID and BASE are not enemies; they apply at different scopes:

1. Use ACID to protect local invariants in each service.
2. Use BASE-style convergence for cross-service workflows.

### Why 2PC/XA is usually avoided between services
Two-phase commit can provide distributed commit semantics, but most modern service architectures avoid it as the default.

Main reasons:

1. Blocking coordination
   - Participants wait on prepare/commit phases.
   - Slow participants slow everyone.

2. Coordinator dependency
   - A coordinator controls progress.
   - If it is unavailable at the wrong time, transactions can stall.

3. Long lock/hold times
   - Cross-network coordination keeps resources reserved longer.
   - Throughput drops under contention.

4. Availability trade-off
   - During partitions/failures, strict global commit often chooses safety over liveness.
   - User-facing systems usually need graceful degradation instead.

5. Poor scalability
   - More participants means more latency and more failure combinations.

6. Tight coupling
   - Shared transaction managers and compatible stacks are required.
   - Polyglot services and diverse datastores become painful.

This lesson follows the Hard Parts Chapter 9 stance: avoid distributed transactions across services and design for eventual consistency. For deeper protocol and consistency theory, revisit [11-transactions.md](../../ddia/lessons/11-transactions.md) and [09-replication-lag-and-consistency.md](../../ddia/lessons/09-replication-lag-and-consistency.md).

### Pattern 1: Background Synchronization
This pattern uses a periodic reconciler to sync state between stores.

How it works:

1. Source services update their own stores normally.
2. A scheduled job scans source records.
3. It computes differences and writes missing/updated data to target stores.
4. Divergence exists until the next successful run.

Timeline (generic):

```
10:00 Source update committed
10:00-10:04 Target copies stale
10:05 Reconciler runs
10:06 Copies aligned
```

Pros:

- Request path stays fast and simple.
- Services stay decoupled during user traffic.
- Works for bulk repair and backfill.

Cons:

- Longest inconsistency window.
- Poor fit for near-real-time reactions.
- Reconciler must understand many schemas, weakening bounded contexts.

Failure shape:

1. If a target system is down, that slice remains stale.
2. Retry happens next run (or on batch retry strategy).
3. Drift can accumulate and then spike during catch-up.

### Pattern 2: Orchestrated Request-Based
This pattern performs all service updates during one synchronous request via a mediator/orchestrator.

How it works:

1. Client sends one command to orchestrator.
2. Orchestrator calls Service A, then B, then C (or another defined sequence).
3. If all calls succeed, response returns success and data is aligned by response time.
4. If a later call fails, orchestrator triggers compensating updates for already committed steps.

Timeline (generic):

```
t0 Client -> Orchestrator
t1 Orchestrator -> A success
t2 Orchestrator -> B success
t3 Orchestrator -> C success
t4 200 OK
```

Pros:

- Strongest end-of-request consistency of the three patterns.
- One explicit control point for policy and ordering.

Cons:

- Slowest response path.
- Complex branching for timeout/retry/compensate paths.
- Orchestrator can become coupling hub and bottleneck.

Failure shape:

1. A late failure can require compensating prior committed work.
2. Compensation can fail independently.
3. Client may receive failure while some steps already committed.

### Pattern 3: Event-Based
This pattern publishes domain events and lets subscribers update asynchronously through a durable broker.

How it works:

1. Producer service commits local transaction.
2. Producer emits event (for example `TicketCompleted`).
3. Subscriber services consume event and update local models.
4. Retries, dead-letter queues, and replay handle failures.

Timeline (generic):

```
t0 Producer local commit
t0+ Event persisted to broker
t1 Subscriber X updates local store
t2 Subscriber Y updates local store
t3 Converged view
```

Pros:

- High decoupling and scalability.
- Fast producer response.
- Natural fit for adding more downstream consumers.

Cons:

- Temporary inconsistency window is expected.
- Requires durable messaging discipline.
- Consumers must be idempotent and observable.

Failure shape:

1. Down subscriber lags; broker retains messages.
2. Other subscribers can still progress.
3. Recovery replays pending events.

### Compensating transaction
A compensating transaction is an action that semantically undoes a previously committed local step.

Example:

1. Service A charges a card.
2. Service B fails permanently.
3. Compensation submits a refund.

Pitfalls:

1. Compensation itself can fail.
2. Some effects are not truly reversible (emails, external shipments).
3. No distributed isolation means others may observe intermediate states.
4. "Undo" is often business-equivalent, not exact physical rollback.

This is the conceptual setup for sagas in [14-transactional-sagas.md](14-transactional-sagas.md).

### Comparison table
| Pattern | Consistency timeliness | Responsiveness | Coupling | Complexity | Failure handling |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Background synchronization | Slowest, bounded by schedule | Fast request path | Low runtime coupling, high reconciler knowledge coupling | Medium batch logic, high mapping burden | Next-run retries, long stale windows |
| Orchestrated request-based | By end of request if success | Slowest request latency | High orchestrator-to-service coupling | High branching and compensation logic | Immediate failure paths plus compensation |
| Event-based | Near real-time to delayed by lag | Fast producer path | Low service coupling via contracts | Medium/high async ops and idempotency work | Durable retries, replay, DLQ, eventual convergence |

### Worked example: Sysops Squad
Rule: when a ticket is marked COMPLETE, Survey and Billing must learn it.

#### Sysops Squad with Background Synchronization
Normal path:

1. Ticket service marks `T-900` COMPLETE at 14:00.
2. Survey and Billing still show old status until batch.
3. Reconciler runs at 14:05 and reads changed tickets.
4. Reconciler writes updates to Survey and Billing projections.
5. At 14:06 all three views agree.

Failure path (Survey down at 14:05):

1. Billing projection updates successfully.
2. Survey write fails and is queued for next run.
3. System remains partially inconsistent.
4. Next successful run updates Survey and convergence is restored.

#### Sysops Squad with Orchestrated Request-Based
Normal path:

1. UI sends `CompleteTicket(T-900)` to orchestrator.
2. Orchestrator calls Ticket service and commit succeeds.
3. Orchestrator calls Survey service and succeeds.
4. Orchestrator calls Billing service and succeeds.
5. Orchestrator returns success; state is aligned at response time.

Failure path (Survey unavailable after Ticket commit):

1. Ticket commit already happened.
2. Survey call times out.
3. Orchestrator executes policy:
   - compensate Ticket back to previous status, or
   - keep COMPLETE and mark pending recovery workflow.
4. If compensation fails, manual or automated remediation is required.

#### Sysops Squad with Event-Based
Normal path:

1. Ticket service commits COMPLETE locally.
2. Ticket service publishes `TicketCompleted(T-900)` to durable broker.
3. Survey consumer handles event and updates its store.
4. Billing consumer handles event and updates its store.
5. Short lag exists, then convergence.

Failure path (Survey consumer down):

1. Broker retains event durably.
2. Billing still updates successfully.
3. Survey consumer recovers and reprocesses backlog.
4. Idempotency key prevents duplicate side effects on redelivery.

#### Guidance from the example
For Sysops Squad, event-based is usually the best default because it keeps ticket completion responsive and decoupled while still converging reliably.

Use orchestrated request-based only when the business requirement is explicit end-of-request consistency, such as "do not return success unless Survey and Billing are done now."

Use background synchronization mainly for non-urgent reconciliation, bulk correction, and migration cleanup.

## Pros
- Aligns with bounded contexts and service ownership.
- Better availability and throughput than global locking approaches in most architectures.
- Supports independent scaling and evolution of services.
- Makes failure handling explicit and testable.
- Works well with modern event and workflow platforms.

## Cons
- Accepts temporary inconsistency, which needs business agreement.
- Requires strong operational tooling (monitoring, retries, replay, DLQ handling).
- Increases design effort around idempotency, ordering, and duplicate handling.
- Cross-service debugging is harder than local transaction debugging.
- Compensation logic may be incomplete for irreversible side effects.

## Alternatives
- **Single-service redesign**: move workflow into one bounded context and use local ACID if ownership boundaries were split too aggressively.
- **Distributed XA/2PC**: choose stronger global atomicity when constraints justify latency/coupling cost and platform supports it.
- **Manual reconciliation**: for low-value workflows, accept drift and fix with reports/operations playbooks.

## When to use it
Use eventual consistency when business workflows span multiple data owners and short-lived divergence is acceptable.
Good fit signals:

1. Independent service deployment and storage are intentional.
2. Domain tolerates brief inconsistency windows.
3. Availability and responsiveness are high priorities.
4. Team can operate async messaging and recovery pipelines safely.

## When NOT to use it
Avoid this approach when immediate global correctness is mandatory and temporary divergence is unacceptable.
Bad fit signals:

1. Legal/safety/regulatory rules require synchronous all-or-nothing outcome.
2. Any interim visible state creates critical harm.
3. Platform lacks durable messaging and observability maturity.
4. Boundaries are artificial and could be simplified into one owner.

## Key takeaways / mental model
Use this mental model:
1. Protect local invariants with ACID at each service boundary.
2. Connect boundaries with explicit convergence mechanisms.
3. Treat failure, retry, and compensation as primary design concerns.

In short: local commit, global converge. You trade global immediate certainty for scalability, availability, and autonomy, then repay that debt with robust async design and operations.

## Self-check questions
1. Why does service-level data ownership remove the assumption of one global ACID transaction?
2. Define each letter in ACID and BASE, and explain where each model applies.
3. Why do many teams avoid XA/2PC in microservice architectures even though it can enforce distributed atomicity?
4. In Sysops Squad, what happens when Survey is down under each of the three patterns?
5. What makes compensating transactions fundamentally different from true rollback?
6. What technical controls must exist before event-based consistency is production-safe?

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 9
- [10-data-ownership.md](10-data-ownership.md)
- [14-transactional-sagas.md](14-transactional-sagas.md)
- [13-distributed-workflows-orchestration-choreography.md](13-distributed-workflows-orchestration-choreography.md)
- [11-transactions.md](../../ddia/lessons/11-transactions.md)
- [09-replication-lag-and-consistency.md](../../ddia/lessons/09-replication-lag-and-consistency.md)
