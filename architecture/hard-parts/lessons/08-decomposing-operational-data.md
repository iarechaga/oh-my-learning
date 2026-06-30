---
id: hard-parts/08
subject: hard-parts
title: Decomposing Operational Data
slug: decomposing-operational-data
status: drafted
mastery:
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 6
prerequisites: [hard-parts/04, ddia/10]
created: 2026-06-30
updated: 2026-06-30
---

# Decomposing Operational Data

## TL;DR
Breaking apart a codebase is often easier than breaking apart its database. Operational data is the live OLTP data that runs the business, and decomposing it is required if teams want true service independence. The move is incremental: identify data domains, isolate ownership, and split connections and infrastructure in reversible steps while the system stays online.

## The idea
Most teams discover this the hard way: they split a monolith into services but keep one shared database. At first this feels practical. Then hidden coupling appears: one schema creates team coordination tax, one connection pool becomes a bottleneck, and one outage takes down everything.

This lesson is about decomposing operational data, not analytical data. Operational data is the OLTP side of the world: create ticket, assign engineer, submit survey, close incident, charge card, update inventory. It is highly concurrent, transactional, and latency-sensitive because it powers day-to-day business workflows.
Analytical data has different goals and constraints, and this course covers it later in lesson 16. Here, we focus on how to split the operational database safely.
The central concept is a data domain.
A data domain is a bounded set of tables that are owned, changed, and deployed together. Think of it as a data bounded context. If two tables almost always evolve together and serve one capability, they probably belong to the same domain.
The hard part is trade-offs. There are forces that push data apart and forces that pull it together. Good architecture is knowing which force dominates for a given part of the system.

## How it works
Start from first principles: data decomposition is a balancing act between disintegrators and integrators.

### Disintegrators: forces that push data apart

1. Change control

A shared schema creates a shared-schema bottleneck. Team A cannot safely add, rename, or repurpose columns without checking whether Team B, C, or D depend on them.

Example:
1. Ticketing team splits `ticket.priority` into `impact` and `urgency`.
2. Reporting job owned by another team still reads `priority`.
3. Mobile API expects old shape and fails.
4. Everyone coordinates a release train.

This is exactly what services were supposed to avoid. Independent deployability at code level fails if data changes still require global coordination.

2. Connection management

A shared DB often fails from connection pressure before CPU or storage limits.

Simple numbers:
1. You run 30 services.
2. Each service has 4 instances.
3. Each instance keeps 10 DB connections.
4. Total demand is 30 x 4 x 10 = 1200 connections.
5. Database max connections is 200.
6. Result: timeout storms, retry amplification, and cascading failures.
Even if your numbers differ, the scaling shape is the problem. As services multiply, every team competes for one global connection budget.

3. Scalability

Different workloads scale differently. Survey submissions may spike during post-incident follow-ups, while ticket comments stay flat. With one shared store, you scale everything together, even when only one domain is hot.

Independent stores let each domain scale by its own bottleneck:
- CPU-heavy query domain gets read replicas or better indexes.
- write-heavy event domain gets partitioning/sharding.
- low-traffic reference domain stays small and cheap.

4. Fault tolerance

One shared operational DB is a single point of failure for all services. If it is unavailable, every service that depends on it becomes unavailable, even if their business functions are unrelated.

With domain-separated stores, failure blast radius shrinks:
1. Survey DB outage blocks survey workflows.
2. Ticketing DB remains healthy.
3. Incident assignment can continue.
4. Business degrades partially instead of fully.

5. Architectural quantum

An architectural quantum is the smallest independently deployable and evolvable unit of architecture. If two services share operational tables directly, they are not truly independent. They form one larger quantum.

In practice, shared data collapses service boundaries:
1. Service A deploy needs schema prep used by Service B.
2. Service B rollback reverts schema assumptions used by Service A.
3. Both teams now coordinate release windows.
You may have microservices in diagrams, but you still have macro-coupling in production. Independent deployability requires independent data ownership.

6. Database type optimization

Not all data shapes fit one database equally well. Polyglot persistence means choosing per domain, not per organization.

Examples:
- Ticket lifecycle with strict constraints may fit relational.
- Session cache or rate-limits may fit key-value.
- Survey responses with variable question sets may fit document.
- Relationship-heavy dependency mapping may fit graph.
A shared single engine forces compromise everywhere.

### Integrators: forces that push data together

1. Data relationships
Relational models offer foreign keys, joins, and referential integrity checks inside one engine. Splitting tables across domains removes cheap in-database joins and moves consistency concerns into application logic.
If data has dense and frequently queried relationships, splitting too early can increase complexity sharply.

2. Database transactions
A single ACID transaction across related tables is easy in one database. After splitting stores, that same workflow becomes a distributed coordination problem, often handled with sagas and compensations.
If your core workflow depends on strict multi-table atomicity, decomposition must be designed very carefully.

### Monolithic vs distributed data trade-off

Monolithic data gives strong local consistency and simple joins, but weak team autonomy and broad failure blast radius.

Distributed data gives team autonomy, fault isolation, and per-domain scaling, but adds complexity around consistency, cross-domain queries, and operations. There is no free lunch: you choose where complexity lives.

### The five-step decomposition process
The safest approach is incremental and reversible. Each step can be rolled back without stopping the business.

### Step 1: Analyze the database and create data domains
Map business capabilities to table clusters.

What to do:
1. Inventory tables, views, procedures, and high-traffic queries.
2. Group tables by business capability and ownership.
3. Document update frequency and coupling patterns.
4. Name candidate data domains.
Sysops Squad example:
- Candidate domain A: ticketing (`tickets`, `ticket_comments`, `ticket_assignments`, `ticket_status_history`).
- Candidate domain B: survey (`surveys`, `survey_questions`, `survey_responses`).

Reversible move: this step is analysis only. No runtime risk.

### Step 2: Assign tables to data domains
Choose a primary owner for each table and remove ambiguous ownership.

What to do:
1. Assign every table to exactly one domain owner.
2. Mark cross-domain references explicitly.
3. Define allowed integration contracts.
4. Decide temporary bridge strategy for legacy SQL.
Sysops Squad example:
1. `tickets` family assigned to Ticketing domain.
2. `surveys` family assigned to Survey domain.
3. Legacy report that joins both becomes a tracked migration item.

Reversible move: ownership map can be revised without downtime.

### Step 3: Separate database connections per data domain
Keep one physical DB for now, but force code-level isolation.

What to do:
1. Give each domain its own credentials and connection pool.
2. Restrict services so they can only access their domain schema.
3. Block direct table access outside domain boundaries.
4. Route cross-domain needs through service APIs, not SQL joins.

This is a crucial inflection point. You still have one server, but boundaries are now real in code and permissions.

Sysops Squad breakage made explicit:

Before:
```sql
SELECT t.id, t.status, s.score
FROM tickets t
JOIN survey_responses s ON s.ticket_id = t.id
WHERE t.opened_at >= CURRENT_DATE - INTERVAL '7 days';
```

After step 3, Ticketing service can no longer join Survey tables directly. The same business question becomes a cross-service interaction:
1. Ticketing service queries recent tickets.
2. For each ticket (or batched ids), it calls Survey service for satisfaction scores.
3. It composes the response in application code.
This introduces network and consistency concerns, covered later in communication and distributed transaction lessons.

Reversible move: if needed, permissions can be relaxed temporarily while fixing migration issues.

### Step 4: Move schemas to separate database servers
Now split logically isolated schemas onto separate servers, still possibly in same environment class.

What to do:
1. Provision target server per domain.
2. Replicate and migrate schema/data.
3. Switch connection strings with feature flags.
4. Monitor latency, errors, and reconciliation checks.

Sysops Squad example:
1. Survey schema moves to `survey-db`.
2. Ticketing remains on `ops-db` initially.
3. Survey service flips connection first.
4. Ticketing integration remains API-based, so no SQL rewrite needed at cutover.

Reversible move: rollback by switching connection string back.

### Step 5: Switch to independent physical database servers
Complete the move to fully independent physical deployments, lifecycle, and scaling policies.

What to do:
1. Ensure each domain has independent backup/restore.
2. Tune engine and hardware per workload.
3. Set distinct SLOs and incident runbooks.
4. Remove old shared infrastructure paths.

At this step, decomposition is no longer cosmetic. Teams can evolve schemas, tune performance, and absorb failures independently.

Reversible move: harder than earlier steps, but still manageable with tested restore and failback procedures.

### Choosing database types per data domain
Once domains are isolated, pick stores by access pattern, not by fashion.

Use these questions:
1. Is consistency strict and relational integrity central?
2. Is access mostly key lookups at very high throughput?
3. Is the shape nested and variable over time?
4. Are queries graph traversal heavy?
5. Is distributed SQL with strong consistency required?

Short mapping table:

| Data shape and access pattern | Suitable database type |
| --- | --- |
| Strong relational constraints, joins, ACID OLTP | Relational |
| Simple key lookup, caching, counters, sessions | Key-value |
| Nested JSON, evolving schema, aggregate reads | Document |
| Huge write volume, sparse wide rows, time buckets | Column-family |
| Multi-hop relationships and path queries | Graph |
| Distributed SQL with strong consistency requirements | NewSQL |
| Managed autoscaling with tight cloud integration | Cloud-native databases |

Tie this to prior concepts:
- Data model fit from [02-data-models.md](../../ddia/lessons/02-data-models.md).
- Partitioning and load distribution from [10-partitioning.md](../../ddia/lessons/10-partitioning.md).

### Worked example: Sysops Squad end-to-end without downtime
Scenario: Sysops Squad has one operational PostgreSQL database with ticketing and survey tables, and they want independent deployment and scaling.

Initial pain:
1. Survey team needs weekly schema changes.
2. Ticketing team needs high write throughput during incidents.
3. Both teams compete for one connection pool.

Execution:

1. Step 1 analysis
   - They discover two natural domains: Ticketing and Survey.
   - They map cross-domain query hotspots.

2. Step 2 ownership
   - Each table gets a single owner.
   - They flag one report that joins `tickets` and `survey_responses`.

3. Step 3 connection separation
   - New DB users restrict each service to its schema.
   - The old join breaks by design.
   - They replace it with Ticketing -> Survey service call composition.

4. Step 4 server separation
   - Survey domain migrates first.
   - Read consistency checks compare old and new paths.
   - Feature flag enables immediate rollback.

5. Step 5 independent physical operations
   - Ticketing later moves to optimized server class.
   - Backup windows and scaling policies diverge.
   - Survey outage no longer blocks ticket creation.

Outcome: no full-system downtime, independent schema deployments, reduced blast radius, and explicit cross-domain integration contracts.

## Pros
- Independent schema evolution per team, reducing release coordination.
- Better connection isolation and lower contention risk.
- Independent scalability by workload and domain bottleneck.
- Smaller failure blast radius and improved resilience.
- Enables polyglot persistence where it actually provides value.
- Aligns data ownership with service ownership and architectural quanta.

## Cons
- Cross-domain joins disappear and must be replaced by APIs or projections.
- Referential integrity across domains becomes an application concern.
- Some single-DB ACID workflows become saga-style distributed workflows.
- Operational overhead increases: more backups, monitoring, runbooks.
- Debugging business flows requires tracing across services and stores.
- Migration requires discipline to avoid half-split states.

## Alternatives
- Keep a modular monolith with one database and strict internal boundaries when team count is small and release cadence is moderate.
- Use logical separation only (schemas, users, permissions) on one physical server if operational maturity is low.
- Build read models/materialized views for cross-domain reporting instead of preserving shared operational joins.
- Delay full decomposition and first fix schema governance, query ownership, and connection policy if pain is mostly process, not architecture.

## When to use it
Use operational data decomposition when your biggest pains are coordination bottlenecks, connection contention, uneven scaling needs, or full-system fragility from a single shared data tier.

It is especially appropriate when:
1. Teams own distinct business capabilities.
2. Domains change at different rates.
3. Outage isolation has high business value.
4. You can invest in explicit service contracts for cross-domain interactions.

## When NOT to use it
Do not split operational data just because microservices are popular. Keep data together when most value comes from dense joins and strict multi-table transactions.

Avoid decomposition when:
1. Team topology is still highly centralized.
2. Cross-domain boundaries are unclear or unstable.
3. Operational maturity is too low for multi-store ownership.
4. Current bottlenecks are in code or process, not in shared data coupling.

In those cases, improve modularity and ownership first, then decompose later.

## Key takeaways / mental model
Use a push-pull mental model.

Disintegrators push data apart: autonomy, scaling, resilience, fit-for-purpose storage.
Integrators pull data together: joins, referential integrity, single-transaction simplicity.

Your job is not to pick a universal winner. Your job is to set domain boundaries where autonomy gains exceed distributed-data costs.

Remember the sequence:
1. Define data domains.
2. Enforce ownership in code and permissions.
3. Split infrastructure gradually.

If you skip stepwise migration and jump straight to physical split, risk rises. If you never split despite clear disintegrator pressure, hidden coupling remains and service independence is lost.

## Self-check questions
1. What is operational data, and why is this lesson focused on it rather than analytical data?
2. Why does a shared operational schema create a change-control bottleneck across teams?
3. In the 30 services x 10 connections example, what system behavior should you expect when max DB connections is 200?
4. Explain how a shared database can collapse multiple services into one architectural quantum.
5. What do you lose immediately when you split data domains that previously relied on joins and foreign keys?
6. Why can a workflow that was one ACID transaction become a saga after decomposition?
7. Describe each of the five decomposition steps and why each one is incremental and reversible.
8. In the Sysops Squad example, what specifically broke when ticketing and survey access were isolated, and how was it replaced?
9. How does polyglot persistence relate to access patterns rather than organizational preference?
10. What signals tell you to postpone decomposition even if it sounds architecturally clean?

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 6
- [10-partitioning.md](../../ddia/lessons/10-partitioning.md)
- [02-data-models.md](../../ddia/lessons/02-data-models.md)
- [08-choosing-databases-storage.md](../../system-design/lessons/08-choosing-databases-storage.md)
