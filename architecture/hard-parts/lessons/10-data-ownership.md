---
id: hard-parts/10
subject: hard-parts
title: Data Ownership
slug: data-ownership
status: drafted
mastery:
seniority: senior
source: Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 9
prerequisites: [hard-parts/08]
created: 2026-06-30
updated: 2026-06-30
---

# Data Ownership

## TL;DR
After decomposing operational data, the critical next question is ownership: who is allowed to write each table? The governing rule is simple and strict: the service that writes a table owns it. Single ownership is the target state, while joint and common ownership require explicit resolution patterns and usually increase coupling and consistency complexity.

## The idea
Lesson 08 decomposed operational data so we can stop treating one large shared schema as inevitable. But decomposition by itself does not solve coordination pain. Teams still get stuck if two or more services can write the same table.

Data ownership turns this into a clear decision model.

1. Every table needs one ownership answer.
2. Ownership is determined by write authority, not read frequency.
3. Reads by other services are valid, but handled through distributed data access patterns (lesson 12), not by granting write rights.

This matters because writes are where semantic authority lives. The writer decides validation rules, state transitions, and invariants. If multiple services write the same table without a deliberate strategy, you get hidden coupling, lockstep releases, and fragile distributed transactions.

A practical mental shift helps: table ownership is an architectural boundary, not just a database privilege setting. The boundary decides who can evolve data semantics independently.

## How it works
Start from the write paths, not from ER diagrams.

1. List each operational table.
2. For each table, enumerate all services that can execute INSERT, UPDATE, or DELETE.
3. Classify ownership into one of three scenarios.
4. Resolve joint or common ownership explicitly.
5. Document read access separately from write ownership.

If you skip this process, architecture drifts into accidental shared ownership.

### Single Ownership
Single ownership means exactly one service writes a table. That service owns the table.

This is the clean, desired case because semantic authority is local. One team controls schema evolution, validation, state transitions, and write-side performance concerns.

ASCII picture:

```
+-------------------+            writes            +----------------+
| TicketService     | ---------------------------> | ticket table   |
+-------------------+                              +----------------+

+-------------------+            reads             +----------------+
| RoutingService    | ---------------------------> | ticket table   |
+-------------------+      (via access pattern)    +----------------+
```

Key points:

1. Ownership is about writes, not reads.
2. Other services can still read, but should do it through approved distributed-data-access patterns (lesson 12).
3. Schema changes can be planned by one owner team and published through contract evolution.

Worked example 1:

1. CatalogService writes `product_catalog`.
2. SearchService and RecommendationService need product reads.
3. CatalogService remains owner because only it writes.
4. Search and Recommendation build read models via replication/event streams rather than direct write access.

Result: clean ownership, reduced coupling, predictable evolution.

### Joint Ownership
Joint ownership means multiple services write the same table. Example: Catalog service and Inventory service both writing `products`.

This is the hard case because semantic authority is now split. Any schema or invariant change may require coordination across services and teams.

ASCII picture:

```
+-------------------+    writes    +----------------+
| CatalogService    | -----------> | products table |
+-------------------+              +----------------+
                                   ^
                                   |
+-------------------+    writes    |
| InventoryService  | -------------+
+-------------------+
```

When this appears, use one of four resolution techniques.

#### 1) Table Split
Split the shared table so each service owns its own rows or columns.

How:

1. Identify fields that belong to each domain.
2. Create separate tables with separate write ownership.
3. Reconcile and compose views using data-sync patterns.

Example:

- `product_catalog` owned by CatalogService for name, description, category.
- `product_inventory` owned by InventoryService for stock level, warehouse state.

Trade-offs:

- Pros: restores single ownership, improves independent deployability.
- Cons: requires synchronization and join logic in read paths; eventual consistency concerns move to integration.

#### 2) Data Domain
Place the shared table in a shared data domain that both services co-own.

How:

1. Define a shared ownership boundary with explicit governance.
2. Accept coordinated change and release planning.
3. Treat the co-owned data as one architecture quantum (lesson 02).

Trade-offs:

- Pros: can be practical when data is genuinely inseparable.
- Cons: gives up some independent deployability, increases static coupling, and often creates multi-team coordination overhead.

#### 3) Delegation
Assign single write ownership to one service. Other service sends write requests to the owner.

How:

1. Choose one service as write authority.
2. Non-owner uses API or message command to request changes.
3. Owner validates and persists updates.

Trade-offs:

- Pros: restores single ownership without immediate schema split.
- Cons: adds dynamic coupling between caller and owner, including latency and availability dependencies in synchronous calls.

#### 4) Service Consolidation
Merge both services into one service when separation is artificial.

How:

1. Confirm both services constantly co-change.
2. Merge into one boundary with one owned schema.
3. Re-evaluate granularity using lesson 07 guidance.

Trade-offs:

- Pros: removes cross-service write conflicts and accidental distribution.
- Cons: larger service boundary, possible team ownership changes, reduced independent scaling options.

Worked example 2 (joint ownership resolution):

1. Two services write `products`.
2. Team first tries governance-only co-ownership.
3. Release friction rises because every schema change needs both teams.
4. Team applies Table Split into `product_catalog` and `product_inventory`.
5. Read model composes both for UI.

Result: write ownership becomes explicit and deployability improves.

### Common Ownership
Common ownership means nearly all services write one table, such as global audit/log or shared reference data.

ASCII picture:

```
+-------------------+  msg  \
| AssignmentService | -----> \
+-------------------+         \
                             +-------------------+   writes   +------------------+
+-------------------+  msg   / | AuditLogService | ---------> | audit_log table  |
| RoutingService    | -----> /  +-------------------+          +------------------+
+-------------------+       /
                           /
+-------------------+  msg /
| CompletionService | ----/
+-------------------+
```

Resolution pattern:

1. Create a dedicated owning service for that table.
2. All other services send events or commands to this owner.
3. Owner performs all writes.

Why asynchronous messaging fits:

1. Audit and log writes are high fan-in and high volume.
2. Async decouples producer latency from centralized write throughput.
3. Message brokers provide buffering during spikes and partial outages.
4. At-least-once delivery can be handled with idempotent write keys.

Worked example 3:

1. Ten services currently write `audit_log` directly.
2. Introduce AuditLogService as sole writer.
3. Producers publish `ActionOccurred` events.
4. AuditLogService consumes, enriches, deduplicates, writes.
5. Producers no longer share a writable table.

Result: ownership is single again, and producer services avoid database coupling.

### Ownership and distributed transactions (lesson 11)
Ownership decisions and transaction strategy are tightly linked.

1. Single ownership reduces cross-service write coordination and keeps many invariants local.
2. Joint ownership often creates workflows where multiple services must update related state.
3. Common ownership introduces shared write dependencies that can force asynchronous coordination.

In practice, joint and common ownership cases frequently push systems toward sagas and eventual consistency, because strict cross-service atomicity is expensive and brittle. This is why ownership cleanup is not cosmetic; it directly lowers distributed transaction complexity.

## Pros
- Makes write authority explicit and reduces semantic ambiguity.
- Improves independent deployability when single ownership is enforced.
- Clarifies accountability for schema evolution and invariant enforcement.
- Reduces accidental distributed transactions caused by shared writes.
- Helps teams reason separately about write ownership and read access patterns.

## Cons
- Migrating from existing shared schemas can be costly.
- Table splits and delegation introduce integration and synchronization work.
- Dedicated owner services can become hotspots if poorly designed.
- Temporary dual models during migration add operational complexity.
- Some domains are genuinely shared and require conscious coordination trade-offs.

## Alternatives
- **Keep shared writes with governance only** - fastest short-term path, but usually accumulates coupling and release friction.
- **Database-level ownership rules only** - permissions help enforcement, but without service-boundary redesign they do not solve semantic coupling.
- **Event sourcing for all state** - can centralize write semantics differently, but still requires clear command ownership and does not remove boundary decisions.
- **Monolithic consolidation** - valid when service separation has little value and shared writes are constant.

## When to use it
Use this ownership model immediately after decomposing operational data (lesson 08) and before scaling service interactions. It is especially useful when teams report lockstep releases, unclear responsibility for data bugs, or frequent conflicts around schema changes. It is also a prerequisite for making distributed-data-access decisions cleanly in lesson 12.

## When NOT to use it
Do not force complex ownership redistribution for a tiny single-team system where one bounded deployment is already intentional and stable. Also avoid over-optimizing ownership when the real issue is wrong service granularity; in that case, consolidation (lesson 07) may be the simpler fix.

## Key takeaways / mental model
Think of each table as having exactly one steering wheel for writes.

1. If one service writes it, ownership is clear.
2. If more than one service writes it, you are paying coordination tax.
3. Your first move is to restore single ownership whenever possible.
4. If joint ownership appears, prefer Table Split or Delegation before introducing a shared data domain, unless the data is truly inseparable.
5. Common ownership should be converted into dedicated ownership with message-driven writes.

Short decision guide:

1. Prefer single ownership by default.
2. If joint ownership exists, first evaluate Table Split.
3. If split is not practical yet, use Delegation to establish one write authority.
4. Use shared data domain only when the data is truly shared and co-change is unavoidable.
5. If friction remains high, reconsider service granularity and consolidate.

### Sysops Squad worked example: `ticket` table conflict
Situation:

1. AssignmentService writes assignee fields in `ticket`.
2. RoutingService writes route and priority fields in `ticket`.
3. CompletionService writes closure state and resolution fields in `ticket`.

This is textbook joint ownership: three services writing one table.

Option A: Delegation

1. Choose TicketService as sole owner of `ticket`.
2. Assignment, Routing, Completion send commands to TicketService.
3. TicketService performs validation and writes all updates.

Effects:

- Fast to implement relative to schema surgery.
- Introduces dynamic coupling to TicketService.
- Sync command calls may increase latency and expose availability dependency.
- Async commands reduce latency coupling but require eventual consistency handling.

Option B: Table Split

1. Split into `ticket_assignment`, `ticket_routing`, `ticket_completion` owned separately.
2. Each service writes only its own table.
3. Build a composed read model for unified ticket views.

Effects:

- Strong ownership clarity and lower write-side coupling.
- Higher short-term migration and read-model composition effort.
- Consistency between sub-tables becomes an integration concern.

Which would I pick here and why?

I would pick Table Split for Sysops Squad if ticket lifecycle data naturally separates into distinct subdomains that evolve independently, because it gives durable ownership boundaries and avoids creating a central write bottleneck. If delivery pressure is high and split cannot be done safely yet, I would use Delegation as an intermediate step, then plan a staged split.

This recommendation follows the guide above: prefer single ownership; if joint ownership appears, prefer Table Split or Delegation over a shared data domain unless data is truly shared.

## Self-check questions
1. Why is write authority, not read frequency, the decisive rule for table ownership?
2. In single ownership, how should other services read data without taking write rights?
3. A `products` table is written by Catalog and Inventory services. Explain why this is joint ownership and compare Table Split vs Delegation.
4. When is a shared data domain a valid choice, and what does it imply for architecture quantum boundaries?
5. Why does common ownership often fit an async message-to-owner pattern better than direct shared writes?
6. How do joint or common ownership patterns increase pressure toward sagas and eventual consistency?
7. In the Sysops Squad ticket case, what migration path would you choose first if the team is under severe deadline pressure, and why?

## References
- Software Architecture: The Hard Parts (Ford, Richards, Sadalage, Dehghani), Chapter 9
- [08-decomposing-operational-data.md](08-decomposing-operational-data.md)
- [11-distributed-transactions-eventual-consistency.md](11-distributed-transactions-eventual-consistency.md)
- [12-distributed-data-access.md](12-distributed-data-access.md)
- [07-service-granularity.md](07-service-granularity.md)
