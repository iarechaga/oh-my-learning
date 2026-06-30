---
id: hard-parts/12
subject: hard-parts
title: Distributed Data Access
slug: distributed-data-access
status: drafted
mastery:
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 10
prerequisites: [hard-parts/10, system-design/10]
created: 2026-06-30
updated: 2026-06-30
---

# Distributed Data Access

## TL;DR
In a distributed architecture, a service often needs to read data owned by another service.
If it reaches directly into the other service's database, you silently re-create tight coupling and collapse service boundaries into a larger quantum.
Distributed data access patterns give you explicit trade-offs for how to get non-owned data without pretending those trade-offs do not exist.

## The idea
Microservices encourage data ownership: each service owns its schema, storage, and change lifecycle.
That boundary is not paperwork.
It is the technical line that allows teams to evolve independently.

Then reality arrives.
One service needs data from another domain to answer a user request.
For example, a ticketing service needs customer name and shipping address to display and route support tickets.
The customer service owns that data.

The tempting shortcut is direct database access.
Ticketing reads the customer table from the customer database.
The query works.
Latency is low.
Engineers feel clever for ten minutes.

But this shortcut breaks service ownership.
Now the ticketing service depends on customer schema details, indexes, naming, and migration timing.
A column rename in customer can break ticketing at runtime.
You no longer have two independent services.
You have one larger, accidentally shared deployment unit.
This is exactly the kind of recoupling that turns architecture quanta back into monolith-shaped coupling.

So the core problem is this:
How does a service read data it does not own while preserving the most important properties of distributed design?

There is no universal winner.
You choose among four patterns based on freshness needs, latency budget, data volume, change frequency, failure tolerance, and team coupling appetite.

## How it works
All four patterns answer one question:
Where does the consumer get the data at read time?

The options range from "always ask the owner now" to "keep a local copy" to "share storage on purpose."
Each option moves complexity to a different layer: runtime calls, replication pipelines, cache management, or shared schema governance.

### 1) Inter-Service Communication
The consumer calls the owning service synchronously whenever it needs the data.
The owner remains the only source of truth, and no copy is persisted by the consumer.

How it works:
1. Ticketing receives `GET /tickets/{id}`.
2. Ticketing loads ticket details from its own store.
3. Ticketing sees `customerId=123` and calls Customer API.
4. Customer service reads its own database and returns current customer profile.
5. Ticketing merges local ticket data plus remote customer data into one response.

What this optimizes:
- Freshness is strong because each read comes from the owner.
- Data duplication is zero.
- Ownership clarity remains high.

Failure and scale shape:
- Request latency includes network hop plus remote query latency.
- If customer service is down or slow, ticketing is now down or slow for that endpoint.
- High ticketing traffic can overload customer service even if customer traffic is otherwise stable.
- Chatty patterns create the N+1 trap (many remote calls per page or workflow).

Numbered worked example:
1. A support UI shows 50 tickets.
2. Ticketing fetches 50 ticket rows locally in 15 ms.
3. For each row, ticketing calls customer service for name and address.
4. Even at 20 ms average per call, total time can explode or require fan-out concurrency.
5. Under load, customer API starts queuing and p99 latency spikes for both domains.

Pros:
- Simplest conceptual model.
- Always freshest owner-approved value.
- No storage duplication in consumer.

Cons:
- Runtime and availability coupling.
- Higher latency per read path.
- Scalability coupling across domains.
- High risk of chatty N+1 traffic.

### 2) Column Schema Replication
The owner replicates selected columns into the consumer's database.
The consumer reads local replicated fields as if they were part of its own query model.

How it works:
1. Customer service defines an outbound contract, for example `{customerId, fullName, address}`.
2. On customer updates, owner emits change events or pushes replication updates.
3. Ticketing stores those fields in a local table keyed by `customerId`.
4. Ticketing joins tickets with local replicated customer projection.
5. Reads stay local; synchronization happens asynchronously.

What this optimizes:
- Fast local reads.
- No per-request runtime call to customer service.
- Better availability isolation for read paths.

Failure and scale shape:
- Copies can lag behind source of truth.
- You need replication logic, retries, ordering, and reconciliation.
- Team confusion can appear if people treat replicated columns as owned by ticketing.
- Schema contract changes need migration choreography across publisher and consumer.

Numbered worked example:
1. Customer renames from "Ana Li" to "Ana L. Rivera".
2. Customer service commits change at 10:02:00.
3. Replication event is delayed by queue congestion.
4. Ticketing UI still shows old name for 40 seconds.
5. At 10:02:40, replication catches up and UI reflects new value.

Pros:
- Low-latency local reads.
- No read-time dependency on owner uptime.
- Scales consumer reads independently.

Cons:
- Data duplication and drift windows.
- Extra replication infrastructure complexity.
- Potential ownership ambiguity.
- Event ordering and replay edge cases.

### 3) Replicated Caching
The consumer keeps an in-memory distributed or replicated cache of non-owned data.
Service instances read from memory and synchronize cache updates via replication or invalidation.

How it works:
1. Ticketing boots and warms a cache for customer reference data.
2. Cache entries replicate across ticketing instances.
3. Ticketing reads `customerId -> name/address` from local memory.
4. Updates arrive from owner events or periodic refresh.
5. On miss or stale detection, fallback policy fetches owner and refreshes cache.

What this optimizes:
- Very low latency due to in-memory reads.
- No per-request owner call for cache hits.
- Partial resilience if owner is temporarily unavailable.

Failure and scale shape:
- Cache coherence and invalidation are hard.
- Memory is finite; this works best for small datasets.
- Startup can depend on cache warmup quality.
- Staleness windows still exist.

This pattern is especially good for relatively static reference data, such as region codes, support tier labels, tax rates, or customer display names that rarely change.
It connects directly to distributed caching design concerns discussed in system design lesson 10.

Numbered worked example:
1. Ticketing stores 200,000 active customer display profiles in a replicated cache.
2. Median cache read is sub-millisecond.
3. Customer service goes down for 5 minutes.
4. Ticketing continues serving last known name/address for existing cache entries.
5. New unseen customer IDs fail open or degrade based on configured fallback policy.

Pros:
- Fastest read path for hot reference data.
- Reduced runtime coupling on cache hits.
- Can continue serving during short owner outages.

Cons:
- Memory cost and capacity limits.
- Sync, invalidation, and consistency complexity.
- Warmup and cold-start sensitivity.
- Not ideal for large, high-churn datasets.

### 4) Data Domain
Both services read shared data directly from a shared data domain by design.
You explicitly give up strict single-service ownership for that dataset.

How it works:
1. Team defines a shared customer data domain accessible by ticketing and customer services.
2. Ownership shifts from single service to shared governance.
3. Both services query the shared domain directly.
4. Joins and local query composition become straightforward again.
5. Schema changes require cross-team coordination and compatibility discipline.

What this optimizes:
- No duplication pipeline.
- No runtime network hop to owner API for every read.
- Direct relational access can simplify query-heavy use cases.

Failure and scale shape:
- Coupling returns through shared schema.
- Independent deployability drops when one schema serves many services.
- Any incompatible schema change can break multiple services at once.
- You intentionally widen an architecture quantum around shared data.

Numbered worked example:
1. Customer table adds mandatory field `address_format_version`.
2. Customer service migrates quickly.
3. Ticketing query does not handle new NOT NULL requirement in write path.
4. Ticketing deployment fails until both teams align migration plan.
5. Release lead time increases because schema governance now spans teams.

Pros:
- No duplicate copy to maintain.
- No per-read remote call.
- Complex joins are possible again.

Cons:
- Shared coupling and governance overhead.
- Weaker independent deployability.
- Higher risk of broad breakage from schema change.
- Boundary blur against service autonomy goals.

### Decision matrix
Use the matrix as a first-pass filter, then confirm with workload measurements.

```
+---------------------------+----------------------------+--------------------------+----------------------------+-------------------------------+-----------------------------------------+
| Pattern                   | Performance / latency      | Availability coupling    | Data consistency           | Scalability                   | Data volume / change frequency fit      |
+---------------------------+----------------------------+--------------------------+----------------------------+-------------------------------+-----------------------------------------+
| Inter-service comms       | Medium to low (remote hop) | High at runtime          | Strong freshness           | Coupled to owner capacity     | Handles large and volatile data best    |
| Column schema replication | High (local DB read)       | Low at runtime           | Eventual (replication lag) | Independent read scaling      | Good for medium to large data, moderate |
| Replicated caching        | Very high (in-memory read) | Low on cache hit paths   | Eventual / bounded stale   | Great for hot-read workloads  | Best for small, relatively static data  |
| Data domain               | High (direct shared read)  | Medium (shared platform) | Strong if same store read  | Shared scaling characteristics| Can handle large data, but shared churn |
+---------------------------+----------------------------+--------------------------+----------------------------+-------------------------------+-----------------------------------------+
```

### Sysops Squad worked example
Context:
Sysops Squad runs a ticketing platform.
The ticketing service owns ticket lifecycle and SLA state.
The customer service owns legal customer profile data.
Ticket screens need customer name and address for routing and contact.

Scenario A: data is small and rarely changes.
Assumptions:
1. Active customer records used by ticketing are around 80,000.
2. Name/address changes are less than 0.5 percent per day.
3. Support dashboard must load under 200 ms p95.
4. Temporary stale values under 2 minutes are acceptable.

Reasoning:
1. Inter-service calls add avoidable latency and create dependency for every ticket read.
2. Column replication works, but persistent copy plus sync machinery may be heavier than needed.
3. Replicated caching gives sub-millisecond local lookups for the hot path.
4. Given low churn and small footprint, cache staleness risk is manageable.
5. Decision: replicated caching is the most balanced choice.

Scenario B: data is large and volatile.
Assumptions:
1. Customer dataset relevant to ticketing is 40 million records.
2. Address and profile updates are frequent from many channels.
3. Compliance requires near-current address on each ticket action.
4. Memory footprint for full cache is not practical.

Reasoning:
1. Replicated caching no longer fits due to size and high churn.
2. If strict freshness dominates, inter-service communication is safest and simplest semantically.
3. If ticketing read throughput is very high and slight lag is acceptable, column replication can offload read traffic from customer service.
4. Data domain is possible but should be treated as deliberate shared coupling, not a convenience shortcut.
5. Decision: prefer inter-service communication for strict freshness; consider column replication for throughput-sensitive read models with acceptable lag.

Short selection heuristic:
1. Need latest value on every request and can tolerate runtime coupling? Use inter-service communication.
2. Need fast local reads at scale with acceptable lag? Use column schema replication.
3. Need ultra-fast reads for small, mostly static reference data? Use replicated caching.
4. Need relational sharing and accept reduced independence? Use a data domain intentionally.

## Pros
- Makes trade-offs explicit instead of hidden inside forbidden direct database access.
- Preserves architectural intent by choosing a known pattern for cross-boundary reads.
- Allows teams to optimize for their real constraint: freshness, latency, resilience, or autonomy.
- Creates a shared vocabulary for discussing coupling and data movement in design reviews.

## Cons
- Every option introduces non-trivial cost somewhere: runtime dependency, replication machinery, cache complexity, or shared governance.
- Teams can misapply patterns without clear staleness and failure budgets.
- Operational burden increases when data synchronization is asynchronous or multi-hop.
- Poorly documented ownership boundaries can still lead to accidental recoupling.

## Alternatives
- **Direct database access across services** - Fast to implement but usually the wrong architectural move because it re-couples teams and schemas into one larger quantum.
- **API composition layer (BFF or gateway aggregation)** - Centralizes read orchestration for clients, but the underlying data access trade-offs still exist and must be handled explicitly.
- **CQRS read model projection** - Builds dedicated read views from events; this is often a structured form of replication and can be a good fit for complex query patterns.
- **Data mesh productized datasets** - Useful at larger organizational scale where domains publish governed data products; still requires clear contracts and lifecycle ownership.

## When to use it
Use distributed data access patterns whenever one service needs another service's data and direct database reads would violate service boundaries.
This is common in microservices handling rich user views, back-office workflows, orchestration, fraud checks, and cross-domain reporting.

Pick a pattern based on concrete constraints:
1. Freshness requirement (seconds, minutes, or eventual).
2. Latency budget for user-facing requests.
3. Read/write volume and growth expectations.
4. Failure mode tolerance when owner is unavailable.
5. Organizational readiness for shared governance.

## When NOT to use it
Do not apply these patterns if your system is actually one tightly cohesive domain that should remain a single service or modular monolith.
Forcing distribution where autonomy does not exist creates needless complexity.

Also avoid over-engineered replication or caching for low-traffic internal tools where a direct synchronous call is entirely adequate.
Choose the smallest pattern that satisfies real non-functional requirements.

Finally, do not choose a data domain accidentally.
If you share storage, do it intentionally with explicit governance, compatibility rules, and cross-team ownership agreements.

## Key takeaways / mental model
Think in terms of coupling placement, not "best pattern".

If you pull data at request time, you pay in runtime coupling.
If you copy data ahead of time, you pay in consistency and synchronization complexity.
If you share the same data domain, you pay in organizational coupling and reduced independence.

A practical mental checklist:
1. What is the maximum staleness the business can accept?
2. What happens when the owner is down right now?
3. How large and how volatile is the required dataset?
4. Which coupling cost is least harmful in this context?

Architectural maturity is not avoiding trade-offs.
It is choosing the trade-off you can operate safely.

## Self-check questions
1. Why is direct database access from one service into another service's schema considered recoupling, even if it seems faster?
2. In what situations is inter-service communication the most honest choice despite higher latency?
3. What failure modes must you design for when using column schema replication?
4. Why is replicated caching especially suitable for small, relatively static reference data, and risky for high-churn large datasets?
5. How does a data domain improve query convenience while reducing deploy independence?
6. Given a requirement of p95 under 150 ms and stale tolerance of up to 60 seconds, which pattern would you evaluate first and why?
7. In the Sysops Squad example, why might the recommended pattern change as data volume and change frequency grow?

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 10
- [10-data-ownership.md](10-data-ownership.md)
- [03-dynamic-coupling.md](03-dynamic-coupling.md)
- [10-distributed-caching.md](../../system-design/lessons/10-distributed-caching.md)
