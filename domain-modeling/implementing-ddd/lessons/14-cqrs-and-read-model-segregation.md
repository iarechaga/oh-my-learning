---
id: implementing-ddd/14
subject: implementing-ddd
title: CQRS and read-model segregation
slug: cqrs-and-read-model-segregation
status: drafted
mastery:
seniority: senior
source: Implementing Domain-Driven Design (Vaughn Vernon), Chapter 4 (Architecture) — CQRS
prerequisites: [implementing-ddd/08, implementing-ddd/12]
created: 2026-08-10
updated: 2026-08-10
---

# CQRS and read-model segregation

## TL;DR
Command Query Responsibility Segregation splits the write model (aggregates, enforcing invariants, handling commands) from the read model (denormalized, query-optimized projections, often rebuilt from domain events) — freeing reads from ever having to be shaped by the write model's aggregate boundaries, at the cost of reads becoming eventually consistent with writes.

## The idea
A repository-backed aggregate (`implementing-ddd/08`) is designed around write-side concerns: enforcing invariants, keeping consistency boundaries small (`implementing-ddd/04`), referencing other aggregates by identity only (`implementing-ddd/05`). Those same design choices make aggregates *bad* at serving read/query needs: a dashboard wanting "top 10 customers by order volume this month, with customer name and total" would require joining across many `Order` aggregates and a separate `Customer` aggregate, none of which the write model is designed to make efficient (per `implementing-ddd/05`, aggregates can't even navigate to each other directly). CQRS's insight is that the read side doesn't need to go through the aggregate/repository machinery at all — it can be served by an entirely separate, denormalized model built and optimized purely for the queries actual users and screens need, kept up to date asynchronously from the same domain events (`implementing-ddd/07`) the write side already raises.

## How it works

### The split: commands go through aggregates, queries go through read models
Commands (`implementing-ddd/09`) — "place this order," "close this discussion" — go through the familiar fetch-aggregate, invoke-behavior, persist, publish-events flow. Queries — "show me this customer's order history," "list all discussions I'm subscribed to" — bypass the aggregate/repository layer entirely and read directly from a purpose-built read model, typically a denormalized table, document, or search index shaped exactly like the screen or API response that needs it.

**Worked example — e-commerce order history page.** The write side has `Order` aggregates, each independently loadable by `OrderId`, referencing `CustomerId` only (per `implementing-ddd/05`). The order-history page needs, per row: order ID, placed date, item count, total, and the customer's display name — spanning two aggregates and reshaping the data entirely. Rather than the page's backend fetching each `Order` via `OrderRepository` and then a separate `Customer` fetch per row (an N+1 pattern), a dedicated `OrderHistoryReadModel` table is maintained:
```sql
CREATE TABLE order_history_view (
    order_id UUID PRIMARY KEY,
    customer_id UUID,
    customer_display_name TEXT,
    placed_at TIMESTAMP,
    item_count INT,
    total_amount DECIMAL
);
```
populated and kept current by a projector subscribing to `OrderPlaced`, `OrderCancelled`, and `CustomerRenamed` events:
```
class OrderHistoryProjector {
    void on(OrderPlaced event) {
        orderHistoryView.insert(event.orderId(), event.customerId(),
            customerNameCache.get(event.customerId()), event.placedAt(),
            event.lineItems().size(), event.total());
    }
    void on(CustomerRenamed event) {
        orderHistoryView.updateCustomerName(event.customerId(), event.newName());
    }
}
```
The order-history page now issues one simple, fast, indexed query against `order_history_view` — no aggregate loading, no cross-aggregate fetches, no N+1 problem.

### Choosing a storage technology per read model, independent of the write side
Because read models are just projections, nothing requires them to live in the same database or even the same storage technology as the write model — a read model optimized for full-text search can live in Elasticsearch, one optimized for graph traversal in a graph database, one optimized for simple lookups in a Redis cache, all fed by the same underlying domain events, each chosen purely for what best serves its specific query shape.

### Accepting eventual consistency on the read side
Since read models are updated asynchronously from events (`implementing-ddd/06`, `implementing-ddd/07`), there's a window after a command completes during which the read model hasn't caught up yet — a customer who just placed an order might refresh the order-history page and briefly not see it. This has to be a deliberate, communicated trade-off (often mitigated in the UI by optimistically showing the just-completed action immediately, or by routing the immediate post-command confirmation screen through the write-side aggregate directly rather than the read model, while subsequent visits use the read model).

### Rebuilding read models from scratch
Because read models are pure projections derived from events, they're disposable and rebuildable — if a projector has a bug, or a new read model is needed for a feature that didn't exist when the system was designed, it can be built by replaying the full history of relevant events from the beginning (this is far more natural when paired with event sourcing, `implementing-ddd/13`, where the full event history is already the durable system of record; without event sourcing, this requires the message broker to retain history long enough, or an event archive).

**Worked example — a forum/collaboration tool.** A `DiscussionSearchIndex` read model (Elasticsearch-backed) is added months after launch to support full-text search across discussions and comments — a query shape the original `Discussion`/`Comment` aggregates were never designed to serve efficiently. It's built by replaying `DiscussionCreated`, `CommentPosted`, and `DiscussionClosed` events from the event log, with zero changes required to the write-side aggregates themselves.

## Pros
- Frees query performance and shape entirely from write-side aggregate-boundary constraints — a read model can denormalize across as many aggregates as a screen needs, something the write model deliberately refuses to do (`implementing-ddd/05`).
- Lets each read model use the storage technology best suited to its specific query pattern, rather than forcing every query through the write model's relational (or whatever) schema.
- New read models can be added later, non-disruptively, by writing a new projector against existing events — no changes to the write-side aggregates or commands required.

## Cons
- Read models are eventually consistent with the write side, introducing a genuine (if often small) lag that has to be designed for explicitly in the UI/UX, not silently ignored.
- Real added infrastructure and operational complexity: more moving parts (projectors, potentially multiple storage technologies), more things that can fall behind or fail silently, and monitoring needs (is this projector caught up? did it error and stop?) that a simple relational query wouldn't require.
- Maintaining projector logic in parallel with write-side aggregate logic is additional code to keep correct and in sync conceptually, even though it's structurally decoupled — a change to an event's schema (`implementing-ddd/07`) can require updating every projector that consumes it.

## Alternatives
- **Single model for both reads and writes (repository-driven queries)** — serve all queries through the aggregate repository (`implementing-ddd/08`), possibly with some ad hoc query methods; simpler, strongly consistent by default, and entirely adequate for systems without demanding cross-aggregate or denormalized query needs — most CRUD-shaped and many supporting-subdomain systems never need full CQRS.
- **Database views / materialized views** — achieve some of CQRS's denormalization benefit using the database's own view or materialized-view features rather than a separately maintained, event-driven projection; simpler to set up (no separate projector infrastructure) but ties the "read model" to the same database and schema as the write side, and materialized views typically refresh on a schedule or trigger rather than reacting to domain events in real time.
- **GraphQL/BFF aggregation at query time** — instead of pre-computing a denormalized read model, aggregate data from multiple sources at request time in an API gateway layer; avoids the staleness/eventual-consistency trade-off (data is always fresh) at the cost of request-time latency and complexity, a reasonable choice for lower-traffic queries where pre-computation isn't worth the projector infrastructure.

## When to use it
When query needs genuinely diverge from what the write-side aggregate structure can serve efficiently — cross-aggregate denormalized views, full-text search, reporting/analytics, or any screen whose natural shape doesn't map to "load one aggregate by ID." Especially valuable in a core domain (`implementing-ddd/01`) with meaningfully different read and write access patterns.

## When NOT to use it
For simple systems where queries map naturally onto loading a single aggregate by ID (or a small, well-indexed set of repository query methods), full CQRS read-model infrastructure is unnecessary complexity — the repository pattern (`implementing-ddd/08`) alone is sufficient, and introducing a whole separate read-model/projector architecture would be solving a scaling or denormalization problem the system doesn't actually have.

## Key takeaways / mental model
Ask, for any query that's awkward or slow against the aggregate/repository model: "is this query shape fundamentally different from what a single aggregate is designed to serve?" If yes, that's the signal for a dedicated, event-driven read model — not a signal to compromise the write model's aggregate boundaries (per `implementing-ddd/04`) to make the query easier.

## Self-check questions
1. Take a query from a system you know that currently requires joining or fetching across multiple aggregates/tables awkwardly. Sketch what a dedicated read model for that query would look like, and what events would keep it updated.
2. Explain the eventual-consistency trade-off CQRS introduces on the read side, and describe a concrete UX technique for mitigating user-visible staleness right after a command completes.
3. Why can a read model safely use a completely different storage technology than the write model, and what specific query need would justify that choice (e.g. full-text search, graph traversal)?
4. A team wants to add CQRS read models to a small internal CRUD tool with no demanding query patterns. What would you push back on, and why?

## References
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 4: "Architecture" (CQRS).
