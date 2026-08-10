---
id: seven-databases/02
subject: seven-databases
title: "PostgreSQL: Relational Modeling, Constraints, and Transactional Strength"
slug: postgresql-relational-modeling
status: drafted
mastery:
seniority: junior
source: Seven Databases in Seven Weeks (Perkins, Redmond, Wilson), Chapter 2
prerequisites: [seven-databases/01]
created: 2026-08-10
updated: 2026-08-10
---

# PostgreSQL: Relational Modeling, Constraints, and Transactional Strength

## TL;DR
PostgreSQL is a fully-featured relational database whose core value is letting the database itself enforce data correctness — via typed columns, foreign keys, unique/check constraints, and ACID transactions — rather than trusting application code to do it everywhere it touches the data. It is the CP-leaning, schema-rigid anchor point of this subject's tour: strong on correctness and rich querying, weaker on effortless horizontal scale.

## The idea
Every one of the other six databases in this subject exists because, for some workload, the relational model's rigidity or single-node-centric scaling was too costly. To judge those trade-offs fairly, you need a solid, concrete picture of what you're trading away — this lesson is that picture.

The relational model's core idea, going back to Codd's 1970 paper, is deceptively simple: represent all data as **relations** (tables), each row a fact about one entity, related to other facts via shared key values rather than by physical nesting or pointers. The database, not the application, is responsible for guaranteeing that those facts stay internally consistent — a `line_items` row can't reference an `order_id` that doesn't exist; two rows can't claim the same `email` if it's declared unique; a `quantity` column can't hold a negative number if a check constraint forbids it. PostgreSQL implements this model plus extensions (JSON columns, arrays, full-text search, extensibility via extensions like PostGIS) that keep it competitive even against document and search-oriented stores for many workloads.

## How it works

### The relational model, concretely
Consider a small e-commerce schema:

```
customers(id PK, name, email UNIQUE)
orders(id PK, customer_id FK -> customers.id, created_at, status)
line_items(id PK, order_id FK -> orders.id, product_id FK -> products.id, quantity CHECK (quantity > 0), unit_price)
products(id PK, name, sku UNIQUE)
```

Each table holds one kind of fact. An order doesn't embed its line items or its customer's details — it references them by ID (a **foreign key**). This is **normalization**: each fact is stored exactly once, so updating a customer's email touches one row, not every order that customer ever placed. The cost of normalization is that reading a full order (customer name, line items, product names) requires a **join** — a query-time operation that stitches rows from multiple tables back together based on matching key values:

```sql
SELECT o.id, c.name, p.name, li.quantity, li.unit_price
FROM orders o
JOIN customers c ON c.id = o.customer_id
JOIN line_items li ON li.order_id = o.id
JOIN products p ON p.id = li.product_id
WHERE o.id = 42;
```

This single query, backed by indexes on the foreign key columns, replaces what would otherwise be several round trips or manual application-side stitching — the relational engine's query planner decides the most efficient join order and index usage for you.

### Constraints: correctness enforced by the database, not the application
The schema above encodes business rules directly: `quantity > 0` (a check constraint) makes a negative quantity structurally impossible, not just "usually prevented by the checkout form." `email UNIQUE` makes duplicate accounts structurally impossible. `customer_id FK -> customers.id` makes an orphaned order (referencing a deleted customer) structurally impossible, unless you explicitly choose a cascade behavior (`ON DELETE CASCADE`, `ON DELETE RESTRICT`, `ON DELETE SET NULL`).

This matters because application code has many entry points — a web API, a batch job, an admin script, a data migration — and every one of them is a place a bug could insert bad data if the *only* thing enforcing correctness is application logic. Constraints move that enforcement to one place that every entry point must pass through.

### ACID transactions, concretely
Suppose an order cancellation needs to: mark the order `cancelled`, restore the inventory count for each line item's product, and issue a refund record — three separate writes across two tables. Wrapped in a transaction:

```sql
BEGIN;
UPDATE orders SET status = 'cancelled' WHERE id = 42;
UPDATE products SET stock = stock + 3 WHERE id = 101;
INSERT INTO refunds (order_id, amount) VALUES (42, 59.97);
COMMIT;
```

If the process crashes after the second `UPDATE` but before `COMMIT`, PostgreSQL guarantees none of the three writes take effect (**Atomicity**) — a concurrent reader never sees the order half-cancelled with stock already restored but no refund recorded. If two customers' cancellations race for the same product's stock row, PostgreSQL's row-level locking and configurable **Isolation** levels (default `READ COMMITTED`, with `REPEATABLE READ` and `SERIALIZABLE` available) prevent one transaction from clobbering the other's update invisibly.

### Indexing and query performance
A table scan (checking every row) is fine for a thousand rows and disastrous for a hundred million. An index (typically a B-tree) on `orders.customer_id` lets PostgreSQL jump directly to the relevant rows instead of scanning the table — the same structural idea that underlies HBase's row-key ordering (`seven-databases/03`) and MongoDB's document indexes (`seven-databases/04`), just implemented differently per engine. `EXPLAIN ANALYZE` shows the actual query plan PostgreSQL chose, which is the primary tool for diagnosing a slow query — a skill that transfers to every other database in this subject in some form.

### Where PostgreSQL scales, and where it strains
Vertical scaling (a bigger machine: more CPU, RAM, faster disks) and read replicas (async or sync copies serving read traffic) take PostgreSQL a long way — many production systems never outgrow a well-tuned single-primary-plus-replicas setup. Where it strains: write throughput is bounded by one primary node's capacity (you can't add more primaries to absorb more writes without sharding, which PostgreSQL doesn't do natively — extensions like Citus add it, at real operational cost); and cross-shard joins/transactions, if you do shard manually, lose the clean guarantees this lesson just described. This is exactly the ceiling that HBase (`seven-databases/03`) and DynamoDB (`seven-databases/07`) are built to blow past, at the cost of the relational conveniences shown above.

## Pros
- Constraints and transactions push correctness enforcement into the database itself, closing an entire class of bugs that "remember to check in application code" can't reliably close.
- A mature, expressive query language (SQL) plus a cost-based query planner means complex, ad hoc questions ("top 10 customers by refund rate last quarter") are answerable without writing custom aggregation code.
- Decades of tooling, extensions (JSONB for semi-structured data, PostGIS for geospatial, full-text search), and operational maturity make it a safe, well-understood default for a huge range of workloads.

## Cons
- Horizontal write scaling is not native — sharding requires extensions or significant manual engineering, unlike systems designed for it from the ground up (HBase, DynamoDB).
- A rigid schema means every row must conform, which is friction when your data's shape genuinely varies row to row (though JSONB columns mitigate this partially).
- Joins across very large tables at high concurrency can become a real performance and locking concern; the discipline that keeps this manageable (indexing, query review, connection pooling) is itself an ongoing operational cost.

## Alternatives
- **MySQL/MariaDB** — a similar relational feature set with different internals and historical trade-offs (e.g., storage engine choice); broadly interchangeable with PostgreSQL for many workloads, chosen more by ecosystem/team familiarity than technical necessity in most cases.
- **NewSQL (CockroachDB, Spanner)** — keeps relational semantics and strong consistency while adding native horizontal scaling via distributed consensus, at the cost of more operational complexity and, for some designs, higher write latency.
- **A NoSQL family from this subject** — appropriate when the actual bottleneck is write-scale beyond what a well-sharded PostgreSQL can reasonably handle, or when the data's natural shape (graph, wide-column, document) fights the relational model hard enough that the constraint/join benefits stop paying for themselves; see `seven-databases/09` for the concrete decision framework.

## When to use it
Default to PostgreSQL whenever the data has real relational structure (entities that reference each other, invariants that span multiple tables) and the write volume doesn't exceed what vertical scaling plus read replicas can handle — which is the large majority of business applications, especially anything involving money, inventory, or other data where a wrong or missing constraint is a real incident, not a cosmetic bug.

## When NOT to use it
Avoid it (or supplement it) when write throughput genuinely exceeds single-primary capacity even after tuning, when the data's natural shape is a deep graph of relationships best walked by traversal rather than joins (`seven-databases/06`), or when schema variability is central to the domain rather than an edge case (`seven-databases/04`). Don't reach for a NoSQL system just because "SQL feels old" — that's not a technical reason; see `seven-databases/09`.

## Key takeaways / mental model
PostgreSQL's whole value proposition is: put correctness enforcement in the database (constraints, transactions), and get expressive, ad hoc querying (SQL, joins) in return — at the cost of a rigid schema and a scaling ceiling that's real but often further away than people assume. Every other database in this subject can be understood as "PostgreSQL, but we deliberately gave up X (rigid schema / single-node transactions / join-time correctness) to get Y (schema flexibility / horizontal scale / graph traversal / raw speed)."

## Self-check questions
1. A junior engineer proposes removing a foreign-key constraint "because it's slowing down our bulk import." What would you want to know before agreeing, and what risk does removing it introduce?
2. Walk through what happens, step by step, if the process crashes mid-transaction in the order-cancellation example above. What does a concurrent reader see before and after the crash?
3. Given a workload with heavy write volume that's outgrowing a single PostgreSQL primary, but where the data is still genuinely relational (needs joins and multi-row transactions), what are your realistic options, and what does each cost you?
4. Why does a table full of check constraints and foreign keys represent a *design decision*, not just defensive boilerplate? What would you lose by dropping all constraints and relying only on application-level validation?

## References
- Seven Databases in Seven Weeks (Perkins, Redmond, Wilson), Chapter 2: "PostgreSQL."
- See also: `seven-databases/01` for the CAP/schema framing this lesson is measured against; `ddia/02` (data models) for a deeper treatment of relational vs. other models.
