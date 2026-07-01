---
id: hard-parts/13
subject: hard-parts
title: "Distributed Workflows: Orchestration vs Choreography"
slug: distributed-workflows-orchestration-choreography
status: drafted
mastery:
seniority: senior
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 11
prerequisites: [hard-parts/03]
created: 2026-06-30
updated: 2026-06-30
---

# Distributed Workflows: Orchestration vs Choreography

## TL;DR
Distributed workflows coordinate multiple services to finish one business outcome.
You can coordinate with orchestration (one conductor service controls steps) or choreography (services react to events without a conductor).
Orchestration is easier to reason about when workflows are complex or failure-prone, while choreography shines for simple high-throughput flows.

## The idea
In lesson 03, dynamic coupling introduced the coordination dimension: when one business action spans many services, those services must agree on order, progress, and failure handling.
That agreement creates coupling even if each service has its own database and deploys independently.

The core question is not whether coupling exists.
The core question is where you place it.

In distributed workflows, semantic coupling and implementation coupling are different:

1. Semantic coupling is unavoidable business coupling.
   A ticket cannot be completed before it exists.
   A refund cannot be notified before it is approved.
2. Implementation coupling is optional technical coupling.
   You decide whether one service enforces sequence centrally, or many services infer sequence from events.

Orchestration and choreography are two ways to implement the same semantic requirement.
Both can be correct, and both can fail badly when used in the wrong context.

Think of this as an architecture trade-off:

- Orchestration pays with central control and possible bottlenecks to gain clarity and recoverability.
- Choreography pays with distributed logic and harder failure management to gain autonomy and scale.

## How it works
At a high level, every distributed workflow must answer five questions:

1. Who decides the next step?
2. Who stores workflow state?
3. Who detects failure?
4. Who decides compensation or retry?
5. Who can explain where a workflow currently is?

The two styles answer these questions differently.

### Orchestration
In orchestration, a dedicated orchestrator service owns the workflow definition and progression.
Participants do one local task and return success or failure.
The orchestrator keeps state and issues the next command.

Typical flow pattern:

1. Client starts workflow by calling Orchestrator.
2. Orchestrator creates workflow instance and state record.
3. Orchestrator calls Service A.
4. On success, orchestrator updates state and calls Service B.
5. On failure, orchestrator runs retry, fallback, or compensation logic.
6. Orchestrator marks workflow completed or failed.

#### Sysops Squad sequence sketch (orchestration)
Ticket lifecycle: create -> assign -> route -> notify -> complete -> survey.

```
Client -> Workflow Orchestrator: start(ticket)
Workflow Orchestrator -> Ticket Service: create
Ticket Service -> Workflow Orchestrator: created(ticketId)
Workflow Orchestrator -> Assignment Service: assign(ticketId)
Assignment Service -> Workflow Orchestrator: assigned(agentId)
Workflow Orchestrator -> Routing Service: route(ticketId, agentId)
Routing Service -> Workflow Orchestrator: routed(queue)
Workflow Orchestrator -> Notification Service: notify(ticketId)
Notification Service -> Workflow Orchestrator: FAILED(timeout)
Workflow Orchestrator -> Routing Service: compensate(unroute ticketId)
Routing Service -> Workflow Orchestrator: unrouted
Workflow Orchestrator -> Assignment Service: compensate(unassign ticketId)
Assignment Service -> Workflow Orchestrator: unassigned
Workflow Orchestrator -> Ticket Service: compensate(mark_pending_notification)
Ticket Service -> Workflow Orchestrator: updated
Workflow Orchestrator -> Client: workflow_failed(notification_step)
```

In this failure, one place knows the truth: the orchestrator.
It knows step boundaries, what succeeded, what failed, and what compensation has run.

#### Pros of orchestration
- Single explicit location for workflow logic and branching.
- State ownership is clear and queryable.
- Error handling and compensation are easier to make deterministic.
- Recoverability is stronger because restart logic has one checkpoint model.
- Observability is straightforward: one timeline per workflow instance.
- Complex workflows with many branches are manageable.

#### Cons of orchestration
- The orchestrator is a coupling point between many services.
- High traffic often passes through it, which can limit throughput.
- Latency may increase due to command-response hops.
- If the orchestrator grows without boundaries, it becomes a god service.
- Team autonomy can degrade if every workflow change centralizes in one codebase.

### Choreography
In choreography, there is no central coordinator.
Each service listens to events and decides whether to perform its local action.
State is emergent across services and messages.

Typical flow pattern:

1. Service A emits event E1 after local commit.
2. Service B listens to E1, does work, emits E2.
3. Service C listens to E2, does work, emits E3.
4. Any service can emit failure events.
5. Other services decide retries or compensations based on subscribed events.

#### Sysops Squad sequence sketch (choreography)
Same lifecycle: create -> assign -> route -> notify -> complete -> survey.

```
Client -> Ticket Service: create ticket
Ticket Service -> Event Bus: TicketCreated(ticketId)
Assignment Service -> Event Bus: AgentAssigned(ticketId, agentId)
Routing Service -> Event Bus: TicketRouted(ticketId, queue)
Notification Service -> Event Bus: NotificationFailed(ticketId, reason=timeout)
Assignment Service -> Event Bus: TicketUnassigned(ticketId)
Routing Service -> Event Bus: TicketUnrouted(ticketId)
Ticket Service -> Event Bus: TicketStatusChanged(ticketId, pending_notification)
Front Controller -> Client: workflow_failed(notification_step)
```

Notice what changed:

1. No single service owns the complete progression graph.
2. Failure knowledge is fragmented unless you add a consolidating mechanism.
3. Compensation requires explicit subscriptions and rules across participants.

The sketch includes a Front Controller to collect workflow outcome.
Without it, client visibility is often poor.

#### Pros of choreography
- Services are loosely coupled at the implementation level.
- No central bottleneck service for all decisions.
- Can scale with high event throughput and parallel consumers.
- Natural fit for simple, mostly linear workflows.
- Teams can evolve participants independently when contracts are stable.

#### Cons of choreography
- End-to-end workflow logic is scattered and hard to understand.
- Debugging and observability become cross-service reconstruction tasks.
- Failure detection is hard: who decides workflow is truly failed?
- Compensation can become inconsistent if participants interpret events differently.
- State tracking often requires extra patterns to avoid blind spots.

### Managing workflow state
State ownership is the key differentiator.

In orchestration, state is explicit and centralized:

- Workflow ID, current step, prior successful steps.
- Retry counters, timeout markers, compensation progress.
- Final outcome and audit timeline.

In choreography, state is distributed unless you add supporting patterns.
Two common options are used.

Option 1: Carry a workflow-state object in messages.

1. TicketCreated includes a state envelope.
2. Each service appends fields and republishes.
3. Downstream services read one payload to infer current stage.

This improves traceability but introduces stamp coupling.
Many consumers become coupled to a broad message shape they do not fully need.
That links directly to contracts and stamp-coupling concerns from lesson 15.

Option 2: Use separate state lookup service.

1. Events carry minimal identifiers.
2. Services query workflow-state store when needed.
3. A dedicated component aggregates progress.

This reduces payload bloat but adds runtime dependency and lookup latency.

### Error handling comparison
Error handling is where the styles diverge most in operational difficulty.

#### Mid-workflow failure in orchestration (notify step fails)

1. Orchestrator sends notify command.
2. Notification service returns timeout/failure.
3. Orchestrator marks step failed and applies retry policy.
4. If retries exhausted, orchestrator executes ordered compensation.
5. Orchestrator records terminal state and emits final outcome.

Who knows it failed?
The orchestrator knows first and can prove exact failure state.

Who triggers compensation?
The orchestrator triggers compensation explicitly, in controlled order.

#### Mid-workflow failure in choreography (notify step fails)

1. Notification service emits NotificationFailed event.
2. One or more services decide whether to compensate prior work.
3. Another component decides whether to retry notify.
4. A separate observer or front controller decides terminal workflow status.

Who knows it failed?
Potentially several services partially know; no single source by default.

Who triggers compensation?
Distributed listeners trigger compensation if subscribed and correctly coded.

This is why choreography often needs extra conventions:

- Dedicated failure-topic taxonomy.
- Correlation IDs on every event.
- Timeout monitors.
- A front controller or state tracker for outcome visibility.

### Trade-off table
The table below compares coordination styles on practical dimensions.

| Dimension | Orchestration | Choreography |
| :--- | :--- | :--- |
| Workflow-state owner | Central orchestrator | Distributed or external state helper |
| Error-handling difficulty | Lower (centralized policy) | Higher (distributed policy) |
| Recoverability | Strong checkpoints, easier replay | Harder replay, fragmented context |
| Responsiveness | Often slower per step due to central mediation | Often faster reactive event flow |
| Scalability | Limited by orchestrator design/capacity | High with partitioned event consumers |
| Coupling profile | Structural coupling to orchestrator | Semantic coupling spread across events |
| Tolerable workflow complexity | High (branches, long-running, retries) | Best for simple mostly-linear flows |

### Rule of thumb
Use the chapter's practical heuristic:

- Complex, branching, error-prone workflows usually favor orchestration.
- Simple, high-throughput workflows usually favor choreography.

This is not dogma.
It is a cost model: choose the style that makes failures easier to survive in your context.

## Pros
Coordinating distributed workflows, regardless of style, brings systemic benefits compared with ad-hoc service-to-service behavior.

- Makes multi-service business processes explicit rather than accidental.
- Creates repeatable execution semantics for ordering, retries, and timeouts.
- Enables end-to-end observability with correlation IDs and workflow instances.
- Reduces hidden race conditions caused by unmanaged cross-service dependencies.
- Provides a framework for compensation and eventual consistency strategies.

## Cons
Distributed workflow coordination has unavoidable costs regardless of whether you orchestrate or choreograph.

- Adds architectural and operational complexity compared with single-service flows.
- Requires disciplined contract management across service boundaries.
- Introduces additional latency from cross-network coordination.
- Demands stronger observability, tracing, and failure-injection practices.
- Increases cognitive load for teams that must reason about partial failure.

## Alternatives
The practical alternative is often a hybrid rather than a pure style.
1. Hybrid orchestration-choreography.
   Use orchestration for high-risk segments (payments, compliance, irreversible actions), and choreography for low-risk fan-out notifications.
2. Domain-sliced orchestrators.
   Instead of one global conductor, create smaller orchestrators per bounded context to avoid a god orchestrator.
3. Choreography with outcome controller.
   Keep event-driven autonomy, but add a thin front controller that tracks workflow outcome for clients.
4. Choreography with explicit state carrier.
   Pass a workflow-state envelope when traceability is critical, while controlling stamp coupling through strict versioned contracts.

These alternatives are often transitional paths, not permanent compromises.
Many systems start choreography-first for speed, then introduce orchestration where failure and compliance pressure rises.

## When to use it
Use distributed workflow coordination when one business outcome requires multiple services and local transactions are insufficient.
Choose orchestration when:
1. Workflow steps branch heavily or include long-running waits.
2. Failure recovery and compensation must be deterministic and auditable.
3. Operators need one place to inspect, replay, or resume workflows.
4. The cost of incorrect ordering is high.

Choose choreography when:
1. The flow is short, linear, and semantically simple.
2. Throughput and responsiveness are more important than centralized control.
3. Teams can maintain strong event contracts and tracing discipline.
4. You can tolerate extra investment in distributed failure visibility.

## When NOT to use it
Do not introduce distributed workflow coordination if the business process can stay inside one service boundary.
Avoid orchestration when:
1. The workflow is trivial and central control adds needless latency.
2. One orchestrator would become a clear throughput bottleneck.
3. Team structure cannot support centralized workflow ownership.

Avoid choreography when:
1. The workflow has many branches, compensations, and strict audit requirements.
2. The organization lacks mature observability and event-governance practices.
3. Failure outcomes must be decided by one authoritative policy engine.

If you cannot answer "who knows the workflow failed" with confidence, your current design is unsafe.

## Key takeaways / mental model
A distributed workflow is a shared story across services.
The architecture decision is where the narrator lives.

1. Orchestration: one narrator tells every chapter in order and keeps the official timeline.
2. Choreography: each participant tells its own chapter after hearing prior chapters.

Neither removes semantic coupling.
They only distribute implementation responsibility differently.

Use this quick memory rule:

- If correctness under failure is your hardest problem, bias toward orchestration.
- If throughput and autonomy for simple flows are your hardest problems, bias toward choreography.

This lesson sets up transactional sagas in lesson 14, where coordination style interacts directly with consistency and compensation design.

## Self-check questions
1. What is the difference between semantic coupling and implementation coupling in distributed workflows?
2. In orchestration, who owns workflow state and compensation ordering, and why does that matter operationally?
3. In choreography, who decides that a workflow has terminally failed, and what extra pattern is commonly added to make that explicit?
4. For the Sysops Squad flow, describe exactly how a notify-step failure is detected and recovered in both styles.
5. Why can carrying workflow-state objects in events improve traceability but increase stamp coupling risk?
6. Given a high-throughput linear workflow with low branch complexity, which style is usually preferred and why?
7. Given a long-running workflow with many branches and strict audit requirements, which style is usually preferred and why?

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 11
- [03-dynamic-coupling.md](03-dynamic-coupling.md)
- [14-transactional-sagas.md](14-transactional-sagas.md)
- [15-contracts.md](15-contracts.md)
