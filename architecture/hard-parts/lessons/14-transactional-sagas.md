---
id: hard-parts/14
subject: hard-parts
title: Transactional Sagas
slug: transactional-sagas
status: drafted
mastery:
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 12
prerequisites: [hard-parts/11, hard-parts/13, ddia/13]
created: 2026-06-30
updated: 2026-06-30
---

# Transactional Sagas

## TL;DR
A saga is a sequence of local ACID transactions across multiple services that together implement one business action.
Because there is no global ACID transaction across services, failures are handled with compensating transactions.
The hard part is not only "undo" logic, but also coordination style, consistency tradeoffs, and state tracking.

## The idea
In a monolith with one relational database, a transaction can usually commit or rollback atomically.
In distributed systems, that guarantee is expensive and often unrealistic.
Each microservice owns its data, often in separate databases, and cannot safely share one global lock manager.

Sagas are the practical compromise.
You break one big business workflow into smaller local transactions.
Each step commits in its own service.
If a later step fails, previously committed steps are semantically undone using compensation.
Definition to memorize:
1. A saga is an ordered sequence of local ACID transactions.
2. Each local transaction updates one service boundary.
3. There is no single global ACID transaction over the full sequence.
4. Failures are handled through compensating transactions.
This connects directly to earlier lessons:
- Lesson 11 (distributed transactions and eventual consistency): compensation is the way you recover when global rollback is unavailable.
- Lesson 13 (distributed workflows): orchestration and choreography are two coordination styles for running saga steps.

Think of a saga as "transactional behavior at business level" instead of strict database-level atomicity.
You preserve business intent, not perfect temporal isolation.

## How it works
At runtime, a saga usually behaves like a state machine.
It starts in an initial state, executes steps, records progress, and reaches either a success terminal state or a compensated terminal state.

### Core mechanics

1. Start the saga with a unique saga ID.
2. Execute local transaction T1 in service A.
3. If T1 succeeds, persist state and move to T2.
4. Continue until all steps succeed, then mark saga completed.
5. If step Tk fails, execute compensations Ck-1 ... C1 in reverse semantic order.
6. Mark the saga as failed-compensated (or failed-partial if compensation also fails).

### Why compensation is semantic, not physical rollback
Compensation is not a database rollback.
Rollback reverts uncommitted changes inside one transaction scope.
Compensation creates new committed events that attempt to neutralize prior business effects.

Example: "reserve seat" can be compensated by "release seat".
But "email sent" cannot be unsent.
At best, you send a follow-up correction.

### The eight saga patterns (book taxonomy)
Chapter 12 classifies sagas by three dynamic-coupling dimensions from lesson 03:
- Communication: synchronous or asynchronous
- Consistency: atomic or eventual
- Coordination: orchestrated or choreographed
2 x 2 x 2 = 8 patterns.

```
+----------------------+---------------+-------------+---------------+-------------------+-------------+----------------------+
| Name                 | Communication | Consistency | Coordination  | Coupling level    | Scalability | Complexity           |
+----------------------+---------------+-------------+---------------+-------------------+-------------+----------------------+
| Epic Saga            | Synchronous   | Atomic      | Orchestrated  | Very high         | Low         | High                 |
| Phone Tag Saga       | Synchronous   | Atomic      | Choreographed | Very high         | Low-Medium  | Very high            |
| Fairy Tale Saga      | Synchronous   | Eventual    | Orchestrated  | Medium-High       | Medium      | Medium               |
| Time Travel Saga     | Synchronous   | Eventual    | Choreographed | Medium            | Medium      | High                 |
| Fantasy Fiction Saga | Asynchronous  | Atomic      | Orchestrated  | High              | Medium      | Very high            |
| Horror Story Saga    | Asynchronous  | Atomic      | Choreographed | High              | Medium      | Extreme              |
| Parallel Saga        | Asynchronous  | Eventual    | Orchestrated  | Medium            | High        | Medium-High          |
| Anthology Saga       | Asynchronous  | Eventual    | Choreographed | Low               | Very high   | High (ops/observ.)   |
+----------------------+---------------+-------------+---------------+-------------------+-------------+----------------------+
```

1) Epic Saga - Synchronous, Atomic, Orchestrated.
Classic transactional feel.
A central orchestrator issues synchronous commands and expects all-or-nothing behavior.
High control, low elasticity, high runtime coupling.

2) Phone Tag Saga - Synchronous, Atomic, Choreographed.
Services call each other directly while still aiming for atomic outcome.
No central controller, but tight call chains and failure propagation make error handling messy.

3) Fairy Tale Saga - Synchronous, Eventual, Orchestrated.
Central coordinator with synchronous calls, but eventual consistency semantics.
Popular because control is clear and compensation is manageable.

4) Time Travel Saga - Synchronous, Eventual, Choreographed.
Direct synchronous collaboration with eventual consistency.
Less central bottleneck than orchestration, but service-to-service coupling can grow quickly.

5) Fantasy Fiction Saga - Asynchronous, Atomic, Orchestrated.
Tries to combine async decoupling with atomic guarantees under a coordinator.
Possible in narrow domains, but expensive and operationally brittle.

6) Horror Story Saga - Asynchronous, Atomic, Choreographed.
Worst combination in practice.
Without central coordination, enforcing atomic semantics over async messaging becomes a failure labyrinth.

7) Parallel Saga - Asynchronous, Eventual, Orchestrated.
Coordinator emits async commands and tracks replies/events.
Strong scalability with explicit control and observable state transitions.

8) Anthology Saga - Asynchronous, Eventual, Choreographed.
Fully event-driven saga families.
Maximum decoupling and scale, but harder observability, debugging, and global reasoning.

### Why atomic plus asynchronous is so hard
Atomic means one shared commit decision.
Asynchronous means delayed, independent, and retriable delivery.
Combining them forces you to solve all of this simultaneously:
1. Message arrival order is not guaranteed.
2. Duplicate delivery must be tolerated.
3. Partial visibility appears while waiting for late participants.
4. Timeouts are ambiguous (slow or failed?).
5. Atomic commit intent conflicts with autonomous retries.

This is why most teams prefer eventual-consistency sagas (Fairy Tale, Parallel, Anthology).

### Compensating transactions in depth
Compensation needs first-class design, not afterthought code.
Key pitfalls:
1. Compensation can fail.
   - If "refund payment" fails after "cancel order", your saga enters a dangerous partial state.
   - You need retries, dead-letter handling, and manual recovery playbooks.

2. Some side effects are irreversible.
   - Sent email, pushed webhook, SMS, external shipment trigger.
   - You compensate with corrective actions, not true undo.

3. Compensation order matters.
   - Usually reverse order of successful forward steps.
   - But business semantics may require custom ordering.

4. No isolation.
   - Other workflows may observe intermediate states between step commits and later compensation.
   - This is the "no isolation" reality compared with database serializability.

5. Idempotency is mandatory.
   - Both forward and compensating handlers must be safe to retry.
   - Use saga IDs, dedup keys, and idempotency tables.

### State management and saga logs
Without state tracking, you cannot reason about failures.
Typical saga state fields:
- saga_id
- current_state
- started_at / updated_at
- completed_steps
- pending_compensations
- last_error
- retry_count per step

Orchestrated and choreographed tracking differ:
1. Orchestrated:
   - A central orchestrator owns the saga state machine.
   - Easier to query: one place to inspect progress.
   - Single logical control point, but can become a bottleneck.

2. Choreographed:
   - State is distributed across emitted events and local service stores.
   - Better decoupling and resilience.
   - Harder debugging, tracing, and compliance audit.

A practical pattern in choreography is to add a dedicated "saga observer" projection.
It does not control the saga, but reconstructs state from event streams for observability.

### Worked example A: Sysops Squad as Epic Saga (sync/atomic/orchestrated)
Business goal: open incident ticket, assign engineer, reserve on-call slot, post war-room notice, send customer survey/notification.
Assume the final survey/notification call fails after prior commits.
Happy path flow:

```
Client -> SagaOrchestrator -> TicketService: createTicket()
Client -> SagaOrchestrator -> AssignmentService: assignEngineer()
Client -> SagaOrchestrator -> OnCallService: reserveSlot()
Client -> SagaOrchestrator -> CommsService: postWarRoomNotice()
Client -> SagaOrchestrator -> SurveyService: sendSurvey()
Client <- SagaOrchestrator: SUCCESS
```
Numbered happy path:
1. Orchestrator creates saga S-9001, state=STARTED.
2. TicketService commits ticket T-443.
3. AssignmentService commits assignee E-17.
4. OnCallService commits reservation R-88.
5. CommsService commits war-room notice N-73.
6. SurveyService sends survey successfully.
7. Saga marked COMPLETED.
Failure and compensation flow (survey fails):

```
TicketService      : createTicket()            [committed]
AssignmentService  : assignEngineer()          [committed]
OnCallService      : reserveSlot()             [committed]
CommsService       : postWarRoomNotice()       [committed]
SurveyService      : sendSurvey()              [FAILED]

Compensate in semantic reverse order:
CommsService       : retractNotice(N-73)
OnCallService      : releaseSlot(R-88)
AssignmentService  : unassignEngineer(E-17)
TicketService      : closeTicketAsAborted(T-443)
```
Numbered failure path:
1. Steps 1-5 succeed and are logged.
2. Step 6 times out; orchestrator marks step FAILED.
3. Orchestrator starts compensation state.
4. Retract notice (if already visible to humans, add correction message).
5. Release on-call slot.
6. Unassign engineer.
7. Close ticket with reason SAGA_COMPENSATED.
8. Saga state becomes FAILED_COMPENSATED.

Observation:
This tries to resemble ACID-style user expectation, but still lacks strict isolation.
Other services may briefly see T-443 before compensation completes.
That links back to DDIA transaction guarantees in lesson 11 and consistency limits in lesson 13.

### Worked example B: Sysops Squad as Anthology Saga (async/eventual/choreographed)
Now model the same process using domain events.
Happy path event flow:

```
TicketCreated -> EngineerAssigned -> OnCallReserved -> WarRoomNoticePosted -> SurveySent
```
Participants subscribe and emit the next event.
No central orchestrator issues direct commands.
Numbered happy path:
1. TicketService commits T-443 and emits TicketCreated.
2. AssignmentService handles TicketCreated, commits E-17 assignment, emits EngineerAssigned.
3. OnCallService handles EngineerAssigned, commits R-88 reservation, emits OnCallReserved.
4. CommsService handles OnCallReserved, commits N-73, emits WarRoomNoticePosted.
5. SurveyService handles WarRoomNoticePosted, sends survey, emits SurveySent.
6. Reporting projection marks business workflow complete.

Failure path (SurveyService fails after prior commits):
```
... -> WarRoomNoticePosted -> SurveySendFailed
                           -> CompensationRequested
                           -> NoticeRetractionRequested
                           -> OnCallReleaseRequested
                           -> EngineerUnassignRequested
                           -> TicketAbortRequested
```
Numbered compensation path:
1. SurveyService cannot send and emits SurveySendFailed with saga_id.
2. Compensation policy component emits CompensationRequested.
3. CommsService handles NoticeRetractionRequested, emits NoticeRetracted.
4. OnCallService handles OnCallReleaseRequested, emits OnCallReleased.
5. AssignmentService handles EngineerUnassignRequested, emits EngineerUnassigned.
6. TicketService handles TicketAbortRequested, emits TicketAborted.
7. Observer projection marks saga FAILED_COMPENSATED.

Important nuance:
In choreography, compensation trigger logic can be centralized in policy events or distributed across participants.
Both work, but distributed triggers can create hidden coupling if event contracts are unclear.

## Pros
- Enables multi-service business transactions without requiring distributed 2PC across all databases.
- Matches microservice ownership boundaries: each service keeps local ACID guarantees.
- Provides explicit failure strategy through compensating transactions.
- Scales better than global locking when using eventual-consistency variants.
- Supports incremental modernization from monolith workflows to distributed domains.

## Cons
- No true isolation: intermediate states can leak to other readers and workflows.
- Compensation logic is complex and domain-specific, not generic rollback.
- Observability is harder, especially in choreographed async variants.
- Irreversible side effects require business correction patterns, not technical undo.
- Operational burden rises: retries, idempotency keys, dead-letter queues, and runbooks become mandatory.

## Alternatives
- **Two-Phase Commit (2PC/XA)** - stronger atomic semantics across resources, but high latency, coordinator fragility, and weak fit for autonomous microservices.
- **Try-Confirm/Cancel (TCC)** - explicit reserve-confirm-cancel protocol for each participant; can be cleaner than ad-hoc compensation, but requires strict contract design in every service.
- **Single service boundary for critical invariants** - collapse tightly coupled writes into one service/database transaction when the domain allows it.
- **Event sourcing with process managers** - represent business transitions as immutable events and use process managers for long-running coordination.

## When to use it
Use transactional sagas when one business action spans multiple services and databases, and you cannot or should not enforce a global ACID transaction.
Choose by default among eventual-consistency options:
1. Fairy Tale Saga when you want central control and synchronous call simplicity.
2. Parallel Saga when you want central control plus async scale.
3. Anthology Saga when you prioritize decoupling and very high throughput.
Good signals:
- You can define clear compensating actions per step.
- Temporary inconsistency is acceptable within bounded time.
- Teams can implement idempotent handlers and operational tracing.

## When NOT to use it
Do not use sagas when the domain requires strict serializable isolation at all times.
Classic examples include certain financial ledger postings, where intermediate visibility is unacceptable.

Avoid atomic plus asynchronous combinations (Fantasy Fiction, Horror Story) unless you have exceptional platform maturity.
They are difficult because they combine async uncertainty with atomic expectations.

Also avoid sagas when compensation is impossible or legally invalid.
If actions cannot be meaningfully undone, redesign boundaries or use a different consistency strategy.

## Key takeaways / mental model
Think of a saga as a coordinated story with checkpoints, not a single magic transaction.
Mental model:
1. Local transactions are chapters.
2. Saga state is the table of contents.
3. Compensation is an epilogue that repairs narrative intent when a chapter fails.
4. Orchestration gives one narrator; choreography gives many narrators.
5. Eventual consistency variants are usually the practical default in distributed systems.

If you remember one line, keep this:
Sagas trade global ACID guarantees for controlled, observable business recovery over time.

## Self-check questions
1. What is the difference between database rollback and compensating transaction in a saga?
2. Why does the lack of isolation in sagas create risks that do not appear in serializable database transactions?
3. In the eight-pattern table, why are Fantasy Fiction and Horror Story considered high-risk choices?
4. Compare Sysops Squad as Epic Saga versus Anthology Saga: what changes in coordination, failure handling, and observability?
5. If compensation for one step fails, what concrete operational mechanisms should exist before you call the design production-ready?
6. When would you intentionally choose orchestration over choreography even if it increases central coupling?

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 12
- [11-distributed-transactions-eventual-consistency.md](11-distributed-transactions-eventual-consistency.md)
- [13-distributed-workflows-orchestration-choreography.md](13-distributed-workflows-orchestration-choreography.md)
- [11-transactions.md](../../ddia/lessons/11-transactions.md)
- [13-consistency-and-consensus.md](../../ddia/lessons/13-consistency-and-consensus.md)
