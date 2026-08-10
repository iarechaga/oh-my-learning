---
id: sql-performance-explained/05
subject: sql-performance-explained
title: Covering Indexes and Index-Only Retrieval
slug: covering-indexes-and-index-only-retrieval
status: drafted
mastery:
seniority: mid
source: SQL Performance Explained (Markus Winand), Chapter 1 - Anatomy of an Index
prerequisites: [sql-performance-explained/04]
created: 2026-08-10
updated: 2026-08-10
---

# Covering Indexes and Index-Only Retrieval

## TL;DR
A normal index lookup finds matching leaf entries, then does a second trip to the table to fetch the actual row data - that second trip is often the *most expensive* part. A **covering index** includes every column a query needs directly in the index itself, letting the database answer the query from the index alone, skipping the table entirely.

## The idea
`sql-performance-explained/02` walked through index lookup as a two-step process: traverse the tree to find matching leaf entries, then use each entry's rowid to fetch the full row from the table. That second step is a separate, often random-access, page read per matching row - and if there are many matches, this "table lookup fan-out" can dominate the query's total cost, sometimes to the point where the index barely helps at all (this is one of the "slow indexes despite indexing" scenarios flagged in `sql-performance-explained/02`). A covering index eliminates that second step by storing every column the query needs - both the filter/sort columns and the columns being selected - directly in the index's leaf entries, so the database never has to touch the table.

## How it works

### The two-step cost, made visible
```sql
CREATE INDEX idx_orders_customer ON orders(customer_id);

SELECT order_id, total FROM orders WHERE customer_id = 101;
```
For each of, say, 40 orders belonging to customer 101:
1. Tree traversal finds the leaf range for `customer_id = 101` (a few page reads, shared across all 40 matches).
2. For **each** of the 40 matching leaf entries, follow its rowid to the table and read `order_id` and `total` from the actual row (up to 40 separate page reads, since the matching rows aren't guaranteed to sit on the same table page - see `sql-performance-explained/09` for when they might).

Total: a handful of index reads plus up to 40 table reads. The table reads dominate.

### Making it covering
```sql
CREATE INDEX idx_orders_customer_covering ON orders(customer_id, order_id, total);

SELECT order_id, total FROM orders WHERE customer_id = 101;
```
Now `order_id` and `total` are stored directly in the index's leaf entries, alongside `customer_id`. The database:
1. Traverses the tree to find the leaf range for `customer_id = 101` (same as before).
2. Reads `order_id` and `total` **directly from the leaf entries it already found** - no rowid follow-up, no table access at all.

This is called an **index-only scan** (or "covered query"). The 40 table reads are gone entirely; only the index pages (typically far fewer, and often already cached, since indexes are usually smaller than the table) are touched.

### `INCLUDE`/non-key columns
Several databases let you add trailing columns to an index that are stored for covering purposes only, without affecting the index's sort order or being usable for seeking - keeping the "searchable" prefix meaning from `sql-performance-explained/04` clean while still gaining covering benefits:
```sql
-- Conceptually equivalent to appending order_id, total after customer_id,
-- but explicitly marked as "included, not indexed for search"
CREATE INDEX idx_orders_customer_covering
  ON orders(customer_id) INCLUDE (order_id, total);
```
The distinction matters for the left-prefix rule (`sql-performance-explained/04`): `INCLUDE`d columns can never be used to seek or filter, only to avoid a table lookup once the seek is already done via the true key columns.

### It only covers what it stores
```sql
-- NOT covered: shipping_address isn't in the index, forcing a table lookup
-- for every matching row, defeating the whole point
SELECT order_id, total, shipping_address FROM orders WHERE customer_id = 101;
```
A covering index only helps for the *exact* set of columns it stores (and any it's sorted by). Add `SELECT *` or any column not included in the index, and the database falls back to table lookups for that column - so covering indexes are inherently tied to specific, known query shapes, not general-purpose.

### Covering combined with left-prefix
Covering composes naturally with everything from `sql-performance-explained/04`:
```sql
CREATE INDEX idx_orders_covering
  ON orders(customer_id, status, order_date) INCLUDE (total);

SELECT order_date, total FROM orders
WHERE customer_id = 101 AND status = 'completed'
ORDER BY order_date;
```
Here the index (a) seeks on the equality prefix `customer_id, status`, (b) supplies `order_date`'s sort order for the `ORDER BY` "for free" (`sql-performance-explained/07`), and (c) covers `total` via the included column - three separate performance wins from one index.

## Pros
- Removes the table-lookup fan-out entirely for matching queries, which is frequently the single biggest cost component of an otherwise-indexed query.
- Compounds with other index benefits (left-prefix filtering, `ORDER BY` satisfaction) rather than replacing them.
- Especially valuable for "hot path" queries that run extremely frequently (e.g. an API endpoint hit thousands of times per second), where even a small per-query saving multiplies into a large aggregate saving.

## Cons
- Widens the index, increasing storage and write-maintenance cost on every insert/update/delete that touches any covered column - you're now duplicating more data per row.
- Tightly coupled to a specific query's `SELECT` list - adding one more selected column, or a different query against the same filter, can silently fall back to table lookups without any error, just quietly worse performance.
- Easy to over-apply: covering every hot query with its own wide index can balloon total index count and write overhead across a busy table.

## Alternatives
- **Accept the table lookup** - for queries that run rarely or return few rows, the extra table reads are negligible; covering is an optimization for *frequent, high-fan-out* queries specifically, not a default.
- **Clustered/index-organized table** (`sql-performance-explained/09`) - instead of covering one specific query, physically order the whole table by its primary key so that *any* lookup by that key is cheap and localized - a broader, structural alternative rather than a per-query index trick.
- **Materialized view / summary table** - precompute and store exactly the columns a reporting query needs, sidestepping the covering-index question by making the "index" the entire storage of that shape.

## When to use it
Reach for a covering index on queries that run very frequently, filter/sort on a stable, well-known set of columns, and select a small, stable set of columns - the classic case is a hot lookup endpoint (`get orders for customer X`) with a fixed, known projection.

## When NOT to use it
Don't cover ad-hoc or `SELECT *`-style queries, or queries whose selected columns change often - the index will silently stop covering and you gain only extra write cost for no benefit. Also avoid covering very wide rows (many included columns) on tables with heavy write traffic, where the added index-maintenance cost can outweigh the read-side savings.

## Key takeaways / mental model
Every index lookup is potentially "seek, then fetch." A covering index removes the "then fetch" by storing the answer directly at the seek destination. It is a query-shape-specific optimization: ask "does this index contain literally everything this query selects, filters, and sorts by?" - if yes, the table is never touched.

## Self-check questions
1. Explain, in terms of page reads, why fetching 40 matching rows via table lookups can be more expensive than the tree traversal that found them in the first place.
2. A covering index serves `SELECT order_id, total FROM orders WHERE customer_id = ?` perfectly. A teammate later changes the query to `SELECT order_id, total, notes FROM orders WHERE customer_id = ?`. What happens to the query's performance, and why does the database not raise an error?
3. Why do `INCLUDE`d (non-key) columns not affect the left-prefix seeking behavior of an index, while key columns do?
4. Give a concrete scenario where adding a covering index would be the wrong call despite genuinely speeding up one query.

## References
- SQL Performance Explained (Markus Winand), Chapter 1: "Anatomy of an Index" (index-only scans / covering indexes).
- See also: `sql-performance-explained/02` (two-step lookup mechanics), `sql-performance-explained/04` (left-prefix and column order), `sql-performance-explained/09` (clustering as a structural alternative).
