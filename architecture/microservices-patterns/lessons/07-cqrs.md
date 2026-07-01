---
id: microservices-patterns/07
subject: microservices-patterns
title: "Implementing Queries with CQRS"
slug: cqrs
status: drafted
mastery:
seniority: senior
source: "Microservices Patterns (Chris Richardson), Chapter 7"
prerequisites: [microservices-patterns/05, microservices-patterns/06]
created: 2026-07-01
updated: 2026-07-01
---

# Implementing Queries with CQRS

## TL;DR
In a database-per-service architecture, queries that need data from several services (or that don't fit the write model's shape - like event sourcing's event streams) are painful: you can't just `JOIN` across service databases. **CQRS (Command Query Responsibility Segregation)** splits the model in two: a **command side** that owns writes and enforces invariants (aggregates, possibly event-sourced), and one or more **query-side read models** - separate, denormalized datastores shaped exactly for specific queries, kept up to date by subscribing to the command side's domain events. You gain query independence, the freedom to use the right storage per query (SQL, Elasticsearch, a graph DB), and better read scaling - at the cost of more moving parts and the **eventual consistency** (replication lag) between writing and the read model reflecting it.

## The idea
Non-CQRS thinking uses one model for both reads and writes: the same tables you update are the ones you query. That's fine in a monolith. In microservices it breaks for two recurring reasons.

First, **cross-service queries**. "Show the order history for this consumer, including restaurant name and delivery status" needs data from Order, Restaurant, and Delivery services - three databases you cannot `JOIN`. Second, **the write model is a bad query model**. Event sourcing (lesson 06) stores event streams, which cannot answer "all shipped orders" with a query at all; even with state storage, a normalized write schema optimized for consistency is often wrong for a specific read pattern (e.g. full-text search, or a heavily denormalized dashboard).

CQRS resolves this by **segregating responsibility**: commands (writes) and queries (reads) use *different* models, often *different* databases. The command side handles create/update/delete, enforces invariants through aggregates, and - critically - **publishes domain events** whenever data changes (exactly the events from lesson 05, or the event stream from lesson 06). The query side maintains **read models** (also called views or projections): purpose-built, denormalized datastores that **subscribe to those events** and update themselves, so they are always shaped for the queries they serve. A query hits a read model directly; it never touches the command side or joins across services.

The deep point: CQRS lets each side be optimized for its job. Writes optimize for consistency and correct invariants; reads optimize for query shape, speed, and the right storage technology. The unavoidable tax is that the read model lags the write by however long event propagation takes - the system is **eventually consistent** (ddia/09).

## How it works

### Two sides, connected by events
```text
  COMMAND SIDE (writes)                 QUERY SIDE (reads)
  +----------------------+   events     +------------------------+
  | Aggregates           |  --------->  | Read model / view      |
  | enforce invariants   | (domain      | denormalized, shaped   |
  | own the write DB     |  events on   | for a specific query   |
  | publish domain events|  a broker)   | own the read DB        |
  +----------------------+              +------------------------+
        ^                                        ^
        | commands (create/update)               | queries (fast, no joins)
        | from clients                           | from clients
```

- **Command side:** create/update aggregates, enforce invariants, publish `OrderCreated`, `OrderShipped`, `RestaurantMenuUpdated`, etc.
- **Query side:** one or more read models. Each subscribes to the relevant events and keeps a denormalized datastore current.
- **Clients** send commands to one side and queries to the other; the two are decoupled and can scale and be stored independently.

### Read models are disposable projections you can rebuild
A read model is **derived data** - it holds no source-of-truth state; it's a projection of events. That has powerful consequences:

- You can **add a new read model at any time** by replaying past events to populate it - no change to the command side. Need a new query? Build a new view.
- You can **rebuild a corrupted or reshaped read model** from scratch by re-consuming events. The read store is throwaway; the command side (or event store) is the truth.
- You can **choose the ideal storage per view**: SQL for relational queries, Elasticsearch for full-text/geospatial search, Redis for hot key-value lookups, a graph DB for relationship queries. Each read model picks what fits.

### Building the query side: idempotent, ordered event handling
The query side is a set of event handlers that translate domain events into datastore updates (insert/update/delete a denormalized record). Getting this right requires care that mirrors lesson 03/05:

- **Idempotency:** events may be delivered more than once (at-least-once). Handlers must detect duplicates (e.g. track the max processed event id per aggregate) so replays don't double-apply.
- **Ordering:** applying `OrderShipped` before `OrderCreated` corrupts the view. Handlers must handle out-of-order delivery (per-aggregate sequence numbers, or a store that orders by key).
- **Concurrency:** parallel handlers updating the same record need optimistic locking to avoid lost updates.

These are the price of maintaining a derived store from an event stream, and they're why CQRS is a senior topic rather than a free lunch.

### The central trade-off: eventual consistency (replication lag)
Because the read model updates *after* the command commits and its event propagates, there is a lag: a client can write, then immediately query and **not see its own change yet**. This is the same replication-lag / read-your-writes problem from ddia/09, now by design. You must handle it deliberately:

- Have the UI show the value it just submitted optimistically, rather than re-reading.
- Return the new aggregate version from the command and have the query wait until the read model has caught up to that version ("read-your-writes" via version tokens).
- Accept the lag where the domain tolerates it (most dashboards, search, history do).

Ignoring this leads to confusing "I saved it but it's not there" bugs - the most common CQRS pitfall.

### When CQRS is essentially forced
CQRS is optional for simple services but effectively **mandatory** in two cases: (1) with **event sourcing** (lesson 06), because event streams can't serve queries at all; and (2) for **cross-service query APIs** (e.g. an API Gateway needing a composite view, lesson 08), where an API-composition approach would require too many calls or too much in-memory joining, so a dedicated read model that pre-joins the data is far better.

### Worked example 1: a cross-service view (the FTGO order history)
Requirement: "order history for a consumer" showing order status (Order Service), restaurant name (Restaurant Service), and courier location (Delivery Service).

1. Without CQRS you'd call three services per order and stitch results in memory (API composition) - N calls, fragile, slow for a list.
2. With CQRS, build an `OrderHistory` read model. It subscribes to events from all three services: `OrderCreated/OrderStateChanged`, `RestaurantCreated/RestaurantUpdated` (for the name), `DeliveryStatusChanged`.
3. On each event, it upserts a **denormalized** `order_history` record already containing the order status, restaurant name, and delivery status together.
4. The query is now a single fast lookup against the read model - no cross-service joins at request time. The read model pre-joined the data offline, driven by events.

This is the canonical reason CQRS exists in microservices: it turns an expensive runtime cross-service join into a cheap local read.

### Worked example 2: right storage for the query (text search)
Requirement: full-text search over restaurant menus ("find vegan burrito near me").

1. The command side stores restaurants/menus in a relational DB optimized for updates and invariants - terrible at fuzzy text and geo search.
2. Build a **read model in Elasticsearch**. It subscribes to `RestaurantCreated`, `MenuItemAdded`, `MenuItemUpdated`, indexing menu text and location.
3. Search queries hit Elasticsearch; writes still go to the relational command side.
4. CQRS let each side use the *right* technology: relational for correct writes, a search engine for search - impossible with a single shared model.

### Worked example 3: adding a new query later, and read-your-writes lag
Requirement (new, months in): a "restaurant revenue dashboard," plus a UX bug report that "a just-placed order doesn't appear immediately."

1. **Add a view with zero command-side change:** create a `RestaurantRevenue` read model and **replay** historical order/payment events to populate it, then keep it live. New query capability, no write-side impact - because read models are rebuildable projections.
2. **The lag bug:** a consumer places an order (command commits) and the order-history read model hasn't consumed `OrderCreated` yet, so their history looks empty for a second - a **read-your-writes** violation from eventual consistency.
3. **Fix:** the command returns the new order's version; the UI either shows the just-created order optimistically, or the history query passes that version and waits until the read model has caught up. Choosing where to absorb the lag is a required CQRS design decision.

## Pros
- **Serves queries the write model can't** - cross-service views and event-sourced data become efficient single-store reads via denormalized read models.
- **Right storage per query** - each read model uses the ideal technology (SQL, Elasticsearch, Redis, graph), independently of the write store.
- **Independent read scaling and isolation** - reads scale separately from writes and don't compete with them; heavy queries don't threaten write consistency.
- **Flexible, rebuildable views** - new read models can be added anytime by replaying events, and corrupted/reshaped views can be rebuilt from the source of truth.

## Cons
- **More complexity and moving parts** - two models, event handlers, and extra datastores to build, deploy, and operate versus a single shared model.
- **Eventual consistency (replication lag)** - the read side trails the write side, causing read-your-writes anomalies you must design around.
- **Idempotent, ordered event handling is non-trivial** - duplicate and out-of-order events and concurrent updates must all be handled to keep views correct.
- **Data duplication** - the same data is stored in the write model and every read model, increasing storage and requiring the propagation pipeline to stay healthy.

## Alternatives
- **API composition (lesson 08):** answer cross-service queries at request time by calling each service and joining in memory. Simpler and immediately consistent, but poor for large result sets, many services, or complex joins - and it couples the caller to every service's availability.
- **Single shared read/write model:** one model for both - simplest, strongly consistent, fine for simple services and same-service queries; fails for cross-service or event-sourced queries.
- **Materialized views inside one database:** in a monolith or single DB, a materialized view gives denormalized reads without full CQRS - not available across separate service databases.
- **Reporting/analytics via a data lake or warehouse (CDC/ETL):** for heavy analytics, stream changes into a warehouse rather than building operational read models - complementary to CQRS for OLAP-style needs.

## When to use it
- A query needs data owned by multiple services and API composition would be too slow, chatty, or fragile.
- You are using event sourcing (lesson 06) and therefore need queryable read models.
- Different queries need different storage technologies (relational writes, full-text/geo search, key-value hot reads).
- Read and write workloads have very different scaling or performance profiles and benefit from independent optimization.

## When NOT to use it
- The service is simple, its queries fit its write model, and all needed data is local - a single model is simpler and strongly consistent.
- The domain cannot tolerate the read-your-writes lag for the query in question and you can't reasonably design around it.
- The team can't yet build reliable, idempotent, ordered event handling and operate the extra datastores - the complexity will cause more bugs than it solves.
- API composition already answers the cross-service query acceptably (small result sets, few services) - prefer the simpler option.

## Key takeaways / mental model
Think of CQRS as **a newsroom vs. its published newspapers**. The newsroom (command side) is where facts are established and verified - the source of truth. From those facts, the paper prints different editions tailored to different readers: a sports section, a finance section, a search index (query-side read models). Each edition is a *projection* of the same facts, shaped for its audience, and can be reprinted from the archives at any time. But a reader always sees yesterday's paper, not the newsroom's live desk - there's a publishing delay (eventual consistency). Two rules of thumb:

1. **Separate the write model from the read models, and connect them with events.** Commands enforce invariants and publish domain events; read models subscribe and maintain denormalized, purpose-built, rebuildable projections - so each side uses the right shape and storage for its job. This is what makes cross-service and event-sourced queries efficient.
2. **The tax is eventual consistency, paid on the read side.** The read model lags the write, so design explicitly for read-your-writes (optimistic UI or version-token waits) and make event handlers idempotent and order-tolerant. Reach for CQRS when queries outgrow a single model or event sourcing forces it - not by default.

## Self-check questions
1. What two recurring problems in a microservice architecture does CQRS solve, and how does segregating commands from queries address each?
2. Describe the roles of the command side and the query side and exactly what flows between them. Why can a query-side read model use a completely different database technology than the write side?
3. Why are read models described as "disposable projections," and what two capabilities does that property give you (think: new queries, and corruption)?
4. What is the central trade-off of CQRS, and describe a concrete read-your-writes anomaly plus two ways to design around it.
5. When is CQRS effectively mandatory rather than optional? Explain the event-sourcing case and the cross-service-query case.
6. Contrast CQRS with API composition for answering "order history across three services." For which situations does each win, and what specifically makes CQRS better for a large, frequently viewed list?

## References
- Microservices Patterns (Chris Richardson), Chapter 7: "Implementing queries in a microservice architecture"
- [ddia/09 - Replication lag and consistency (read-your-writes, eventual consistency)](../../ddia/lessons/09-replication-lag-and-consistency.md)
- [ddia/15 - Stream processing (maintaining derived views from event streams)](../../ddia/lessons/15-stream-processing.md)
- [microservices-patterns/08 - External API patterns and the API Gateway](08-external-api-gateway.md)
