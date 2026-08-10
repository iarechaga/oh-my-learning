---
id: building-microservices/07
subject: building-microservices
title: "Managing Data: Per-Service Databases"
slug: per-service-data
status: drafted
mastery: 
seniority: senior
source: "Building Microservices, 2nd ed. (Sam Newman), Chapter 7"
prerequisites: [building-microservices/03, building-microservices/06]
created: 2026-08-10
updated: 2026-08-10
---

# Managing Data: Per-Service Databases

## TL;DR
Each microservice must own its data exclusively — no other service reads or writes its database directly. This is what makes independent deployability real rather than nominal, but it removes cross-service joins and multi-table ACID transactions as tools, forcing you to solve cross-service queries and reporting with new techniques: API composition, CQRS-lite (service-owned read models built from events), and dedicated data pipelines for analytics.

## The idea
Lesson 03 named "implementation coupling via shared database" as one of the three coupling types to actively avoid, and Lesson 01 named data ownership as one of the three defining properties of a microservice. This lesson makes the mechanics and consequences of that rule concrete — because giving it up is, in practice, one of the hardest parts of adopting microservices, precisely because relational databases make joins and transactions so easy *within* one schema, and those tools simply don't work across service boundaries anymore.

**The shared-database anti-pattern.** Picture a "microservices" system where `order-service`, `inventory-service`, and `shipping-service` are three separate deployables, but all three read and write tables in the same Postgres database — `orders`, `inventory`, `shipments`, maybe even with foreign keys between tables owned by different services. This is not meaningfully microservices, whatever the deployment tooling says: any schema change to a shared table is a de facto joint release across every service that touches it (implementation coupling, Lesson 03), and one service's implementation detail (e.g., a specific column's meaning, or the order in which rows get written) can silently become another service's unstated dependency. It recreates the exact coordination bottleneck microservices exist to escape — and the coupling is invisible in the deployment pipeline, so it's often discovered only when a release unexpectedly breaks something in a completely different team's service.

**Database-per-service** is the fix: each service has its own database (or its own dedicated schema/namespace, with hard access controls preventing any other service from connecting to it directly), and it's the *only* thing allowed to touch that data. Every other service accesses that data only via the owning service's published interface — its API or its published events.

## How it works

### The rule and how it's enforced

Concretely: `order-service` owns an `orders` database. No other service is granted database credentials to it, no other service's deployment configuration references its connection string, and ideally the network layer itself prevents other services from reaching it (e.g., firewall rules, or the database simply not being on a network segment reachable by other services). If `inventory-service` needs to know something about an order, it asks `order-service` — through an API call or by consuming an event `order-service` publishes — never by querying the `orders` table.

This isn't just a policy — Newman is clear that this needs to be an *enforced* boundary, not just a convention teams are trusted to follow, because a "just this once, temporarily" cross-service query is exactly how implementation coupling creeps back in (Lesson 03's caution about coupling requiring ongoing discipline applies directly here).

### The problem this creates: no more free joins, no more free ACID

Inside one database, "show me all orders for customers in California with more than 3 items, joined with their current shipment status" is one SQL query with a join. Once `orders` and `shipments` live in separate databases owned by separate services, that join is no longer possible at the database level — there's no shared connection, and even if there were, that would violate the data-ownership rule you just established.

Similarly, "place an order and reserve inventory in one atomic transaction" used to be a single database transaction (`BEGIN; INSERT INTO orders...; UPDATE inventory SET stock = stock - 1...; COMMIT;`), giving you atomicity for free. Once `orders` and `inventory` are owned by separate services with separate databases, there is no shared transaction manager that can atomically commit or roll back writes across both — you've lost cross-service ACID transactions entirely. (This specific problem — and its answer, sagas — is the whole subject of Lesson 08.)

This lesson focuses on the *query* side of the problem: how do you answer questions that used to be a join, and how do you build cross-service reports, once direct database access is off the table?

### Answer 1: API composition

The simplest fix: have a caller (a client, a backend-for-frontend, or a dedicated aggregating service) make multiple API calls to the owning services and combine the results in application code instead of in a database join.

**Worked example.** "Show a customer their order history with current shipment status for each order." An aggregating layer:
1. Calls `order-service.getOrders(customerId)` → gets a list of orders.
2. For each order, calls `shipping-service.getShipmentStatus(orderId)` → gets current status.
3. Combines the two into one response for the UI.

This works well for a small number of calls with modest data volumes. It gets expensive and slow as the number of "joined" services or the row count grows (N+1 call patterns, e.g., one shipment-status call per order, are a real performance trap — batch endpoints, like `shipping-service.getShipmentStatuses(orderIds)`, are the usual mitigation). It also pushes filtering/sorting logic that a database would normally do efficiently (e.g., "orders with more than 3 items") into application code operating on data pulled over the network, which doesn't scale well to large datasets.

### Answer 2: CQRS-lite — service-owned read models

**Command Query Responsibility Segregation (CQRS)**, applied lightly at the microservices level (not the full event-sourced version, which is a heavier architectural commitment): a service builds and owns its *own* local, denormalized read model of data it needs from other services, kept up to date by consuming events those services publish, rather than querying them live on every read.

**Worked example.** `shipping-service` frequently needs to know order details (items, customer address) to plan shipments, but doesn't want to call `order-service` synchronously on every operation (temporal coupling, Lesson 03/06). Instead, `shipping-service` subscribes to `OrderPlaced` and `OrderUpdated` events published by `order-service`, and maintains its own local, read-optimized copy of the order data it actually needs (`shipping-service`'s own `order_summary` table, in its own schema, containing only the fields shipping cares about). When it needs to plan a shipment, it reads from its own local copy — fast, no network call, no coupling to `order-service`'s availability.

The cost: `shipping-service`'s local copy is only as fresh as its event consumption lag — it's eventually consistent with `order-service`'s source of truth, not instantaneously consistent. For most read use cases (planning, displaying, reporting) this lag (typically milliseconds to a few seconds) is entirely acceptable; for cases needing the absolute latest state (e.g., "is this specific order still cancellable right now?") a direct synchronous call to the owning service may still be the right tool.

### Answer 3: dedicated data pipelines for analytics and reporting

Cross-service, company-wide reporting ("total revenue by region by product category, joined with fulfillment SLA compliance, across all of last quarter") is a fundamentally different problem from a single feature's read model — it needs to correlate data from many services, over long time windows, for ad hoc analytical queries that don't map cleanly to any one service's API.

The standard answer: each service publishes its relevant data (via events, or via periodic batch export) into a **dedicated analytical data store** — a data warehouse or data lake — via an ETL/ELT pipeline, decoupled entirely from the services' operational databases. Analysts and reporting tools query the warehouse, never the live operational databases of individual services. This keeps analytical query load (often large, slow, ad hoc scans) from ever competing with or endangering a service's operational (transactional, latency-sensitive) database, and gives analysts one place to correlate data across every service without needing direct access to each one's internals.

This connects to the OLTP/OLAP distinction covered in `ddia/05` — each service's own database is an OLTP store optimized for its operational workload; the warehouse is a separate OLAP store optimized for exactly this kind of cross-cutting analytical query, fed by a pipeline rather than queried live.

## Pros
- **Preserves real independent deployability** — a service's schema is truly private, so it can be changed, migrated, or even replaced (switching from Postgres to DynamoDB, say) without coordinating with any other team.
- **Enforces information hiding at the data layer** (Lesson 03) — consumers depend only on a stable published contract, never on internal schema details.
- **Enables per-service technology choice** — each service can pick the datastore best suited to its access patterns (a graph database for a recommendation service, a document store for a catalog service, a relational database for an accounting service).

## Cons
- **Loses free cross-service joins and ACID transactions** — real, recurring extra design work is now required for every cross-service query and every multi-service write that used to be trivial inside one database.
- **Data duplication becomes normal** (e.g., `shipping-service`'s local copy of order data) — more storage, and a real eventual-consistency lag to reason about and communicate to users where it matters.
- **New infrastructure and complexity**: event consumers, read-model builders, ETL pipelines, and the operational burden of keeping all of it healthy and monitored.

## Alternatives
- **Shared database** — the anti-pattern this lesson argues against; sometimes chosen deliberately as a *temporary* stepping stone during a strangler-fig migration (Lesson 04) where two services genuinely need to share data for a bounded period, but should be treated as technical debt with an explicit removal plan, not a permanent architecture.
- **Full event sourcing** — a heavier commitment than CQRS-lite, where a service's true source of truth *is* its event log (not a conventional current-state table), and all read models (including its own) are projections built by replaying that log. Powerful for audit trails and temporal queries, but adds real complexity; Newman treats it as a specialized tool, not a default.

## When to use it
- Always, as the default rule for any two services that need each other's data — database-per-service is the baseline microservices data architecture.
- API composition for simple, low-volume, ad hoc cross-service reads (especially UI aggregation).
- CQRS-lite read models for frequent, latency-sensitive cross-service reads where eventual consistency (seconds of lag) is acceptable.
- Dedicated data pipelines/warehouse for cross-cutting analytical and reporting needs.

## When NOT to use it
- Don't reach for full event sourcing just to solve a simple cross-service query problem — it's a much bigger architectural commitment than the problem usually requires; try API composition or CQRS-lite first.
- Don't build a CQRS-lite read model for data that's rarely needed or where the owning service's API is fast enough — the added infrastructure (event consumers, a synced local copy) isn't free, and a direct API call may be simpler and perfectly adequate.
- Don't let "we need this join for a report" justify direct cross-service database access, even "just for reporting" — that's exactly the case dedicated data pipelines exist to solve without compromising the ownership boundary.

## Key takeaways / mental model
"Your database, your business" — a service's data is as private as its internal code, accessible to others only through its published API or events, never directly. Losing free joins and free multi-table transactions is the real, unavoidable cost of that privacy; API composition, CQRS-lite read models, and dedicated analytical pipelines are the three standard tools for paying that cost deliberately and well, chosen based on query frequency, latency needs, and scope (single feature vs. company-wide reporting).

## Self-check questions
1. Why is a system where three "independently deployed" services all read and write the same shared database not meaningfully microservices, even though each has its own deployment pipeline?
2. When would you reach for API composition versus a CQRS-lite local read model to answer a cross-service query? What's the deciding factor?
3. `shipping-service` maintains a local copy of order data built from `OrderPlaced` events. A customer cancels an order and immediately checks whether it's still shippable — what could go wrong with reading from `shipping-service`'s local copy in that moment, and how would you address it?
4. Why does company-wide analytical reporting need its own dedicated data pipeline/warehouse rather than just querying each service's operational database directly, even with permission?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 7: "Workflow" and Chapter 6 database-per-service discussion (Newman's 2nd edition restructures data-management content across the "Workflow" and integration chapters)
- Related: `building-microservices/08` (Distributed Transactions and Sagas) for the write-side counterpart to this lesson's read-side focus; `ddia/10` (Partitioning) and `ddia/05` (OLTP/OLAP) for the underlying data-systems theory.
