---
id: fundamentals/20
subject: fundamentals
title: Architecture Decisions and ADRs
slug: architecture-decisions-and-adrs
status: drafted
mastery:
seniority: senior
source: Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 20
prerequisites: [hard-parts/01]
created: 2026-06-30
updated: 2026-06-30
---

# Architecture Decisions and ADRs

## TL;DR
Architecture decisions are the technical commitments that shape a system's structure. Documenting these choices using Architecture Decision Records (ADRs) ensures that teams retain the underlying trade-offs, context, and consequences of a decision instead of relying on fragile tribal memory or ad-hoc practices.

## The idea
Design decisions are cheap to change. If you choose the wrong variable name or loop structure, you can fix it in five minutes. Architecture decisions are expensive and difficult to reverse. They dictate how services communicate, where data lives, and how teams cooperate.

When teams fail to document these decisions, they fall into trap patterns. New developers arrive and don't understand why the system was built a certain way. They assume the original team was incompetent and attempt to rewrite it, reproducing the exact bugs the original architecture solved. This loss of context causes teams to cycle through the same arguments repeatedly.

An Architecture Decision Record (ADRs) is a simple, lightweight markdown document stored directly in the source control repository beside the code. It captures a point-in-time choice, the context that prompted it, the alternatives considered, and the concrete positive and negative consequences. By using ADRs, you treat architecture choices as version-controlled code artifacts.

## How it works

To make effective architecture decisions and capture them reliably, you must understand decision anti-patterns and follow a structured ADR format.

### The Four Crucial Decision Anti-Patterns

```
1. Ad-Hoc Architecture   -> Decisions made on gut feel with zero documentation.
2. Email/Wiki Graves     -> Decisions hidden in old threads or stale wiki spaces.
3. Groundhog Day         -> Teams re-arguing the same decision every three months.
4. Shrinking Architecture -> Design choices slowly erode the core architecture.
```

1. **Ad-Hoc Architecture**:
   Decisions are made in chat channels or hallway conversations. There is no central log. Engineering teams end up with a collection of random choices that contradict each other. This creates a fragmented system that is difficult to maintain.

2. **Email/Wiki Graves**:
   Decisions are documented, but they are buried in old email threads, chat logs, or abandoned corporate wiki pages. Because these locations are disconnected from the codebase, they quickly drift out of date and developers can't find them when they need them.

3. **Groundhog Day**:
   The team repeatedly debates the same technical choice because the original rationale was never written down. Every time a new engineer joins or a minor issue occurs, the debate starts again. This wastes massive amounts of development time.

4. **Shrinking Architecture**:
   As features are rushed out, developers bypass architectural boundaries. They might write direct queries to another service's database or introduce circular dependencies. Without active decision-making, the architecture slowly erodes until the system becomes a tightly coupled monolith.

### The Standard ADR Structure
A high-signal ADR must include five core sections:
1. **Title**: A clear name containing the decision number and the core topic.
2. **Status**: The current lifecycle stage of the decision (Proposed, Accepted, Superseded, Rejected).
3. **Context**: The forces and business constraints that led to this decision.
4. **Decision**: The chosen technical action. Use active voice and clear statements.
5. **Consequences**: The trade-offs. You must include both the positive gains and the negative costs. If an ADR lists only positives, the trade-off analysis is incomplete.

### Realistic Worked Example: ADR-024 for "FastShop"
FastShop needs to decide how to handle transactional messaging between Checkout and Fulfillment.

```markdown
# ADR-024: Use Transactional Outbox Pattern for Checkout Events

## Status
Accepted (2026-06-30)

## Context
- The Checkout service publishes a TicketAssigned event when a checkout completes.
- The Fulfillment service consumes this event to prepare orders.
- Currently, Checkout writes to its local database and immediately publishes to the message broker in a single API request thread.
- During network hiccups, the broker can fail to acknowledge the message. If we roll back the database transaction, the customer is charged but the order is lost. If we commit the database write before publishing, the database write can succeed but the event is never published, leaving fulfillment stalled.
- We need dual-write consistency: Checkout writes and event publishes must both succeed or both fail.
- Distributed transactions (two-phase commit) are not supported by our message broker and introduce unacceptable latency.

## Decision
- We will implement the Transactional Outbox Pattern.
- The Checkout service will write Checkout records and CheckoutOutbox event payloads to the same relational database in a single database transaction.
- A background Outbox Publisher process will poll the Outbox table every 500 milliseconds, publish pending events to the message broker, and mark them as published upon successful broker acknowledgement.
- We will enforce at-least-once delivery semantics.

## Consequences

### Positive
- High Availability: Checkout transactions can complete even if the message broker is temporarily down.
- Data Consistency: We guarantee that every completed checkout eventually produces a published event.
- Performance: We eliminate the network call to the broker from the synchronous user request path, dropping checkout latency.

### Negative
- Operational Complexity: We must maintain, scale, and monitor a background polling process.
- Outbox Table Bloq: The Outbox table will grow rapidly. We need an automated partition-purging job to delete records older than 14 days.
- Message Duplication: Under network partitions, the publisher might publish an event twice. The Fulfillment service must implement idempotent event processing.

### Follow-up Actions
- Checkout team must set up database indexes on the status and created_at columns of the Outbox table.
- Fulfillment team must configure an idempotency check using the checkout_id as the unique deduplication key.
- Setup an alert for any outbox record that remains in a pending state for more than 5 minutes.
```

## Pros
- Stops the Groundhog Day effect by preserving the point-in-time rationale.
- Democratizes architecture by keeping records in git where developers can review them via pull requests.
- Forces teams to acknowledge the negative consequences of their choices before writing code.
- Speeds up onboarding by giving new developers a chronological log of how the system evolved.

## Cons
- Requires continuous team discipline. If ADRs are not updated when decisions change, the log becomes confusing.
- Writing good ADRs takes time and can feel like unnecessary paperwork to developers who prefer to just build features.
- Can lead to over-documentation of minor design details that should be decided inline.

## Alternatives
- **RFC (Request for Comments) Documents**: Collaborative design papers written before a decision is made. They are great for gathering feedback but are often too long and don't track the final, long-term state of a decision.
- **Wiki-Based Architecture Registers**: Documenting decisions in tools like Confluence or Notion. This makes them accessible to non-technical stakeholders, but they easily drift from the code and lack git history.
- **Inline Code Comments**: Documenting decisions directly in the code. This places context close to the implementation, but it's impossible to search across multiple repositories and lacks a unified timeline.

## When to use it
Use ADRs for any decision that has a high cost of change, a broad blast radius, or affects key architectural characteristics. This includes choosing frameworks, introducing new integration patterns, partitioning databases, or setting security protocols.

## When NOT to use it
Don't write ADRs for low-impact design decisions. Choosing a library for date formatting, naming a local utility class, or selecting a validation library should be decided by team consensus or coding guidelines, not formal ADRs.

## Key takeaways / mental model
Every architecture decision is a trade-off. An undocumented decision is a ticking time bomb.

1. Capture context and consequences, not just the technical choice.
2. If there are no negative consequences, you don't understand the trade-off.
3. Keep ADRs close to the code: store them in markdown inside the source repository.
4. Use ADR pull requests to encourage team review and share architectural knowledge.

## Self-check questions
1. How does the Groundhog Day anti-pattern impact a development team's velocity and morale?
2. What is the fundamental difference between the context section and the decision section of an ADR?
3. Why must every valid ADR include negative consequences?
4. How do you prevent your ADR directory from becoming an unmaintained wiki grave?

## References
- Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 20
- [01-tradeoffs-no-best-practices.md](../../hard-parts/lessons/01-tradeoffs-no-best-practices.md)
