---
id: sql-performance-explained/07
subject: sql-performance-explained
title: ORDER BY, GROUP BY, and Avoiding Expensive Sorts
slug: order-by-group-by-and-sorts
status: drafted
mastery:
seniority: mid
source: SQL Performance Explained (Markus Winand), Chapter 6 - Sorting and Grouping
prerequisites: [sql-performance-explained/04]
created: 2026-08-10
updated: 2026-08-10
---

# ORDER BY, GROUP BY, and Avoiding Expensive Sorts

## TL;DR
`ORDER BY`, `GROUP BY`, and `DISTINCT` all fundamentally need rows in sorted (or grouped) order - and the database can either get that order "for free" from a B-tree index's inherent sort order, or pay for it explicitly with a sort operation (often called a "filesort" when it spills to disk). Whether you get the free path depends on precise alignment between the index's column order and the query's clauses.

## The idea
`sql-performance-explained/02` established that a B-tree's leaf level is stored in sorted order and linked sequentially. That sortedness is useful for more than filtering - if a query needs its output in a particular order (`ORDER BY`), or needs to group identical values together (`GROUP BY`, `DISTINCT`), and an index already delivers rows in exactly that order, the database can walk the index and emit rows directly, with **no separate sort step**. When no index provides the needed order, the database must materialize all the candidate rows and sort them explicitly - an operation whose cost grows faster than linear (`O(n log n)`) and, for large row sets that don't fit in memory, spills to temporary disk space, becoming dramatically slower.

## How it works

### Getting `ORDER BY` for free
```sql
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

SELECT * FROM orders WHERE customer_id = 101 ORDER BY order_date;
```
Because the index is sorted by `(customer_id, order_date)`, all rows with `customer_id = 101` already appear in `order_date` order within that group - the leaf-chain walk from `sql-performance-explained/02`'s range-lookup example returns them pre-sorted. No sort operation is needed; the database just streams the leaf entries in the order they're already stored.

```sql
-- Same index, but ordering by a column NOT covered by the index's sort
-- order after the equality prefix - the free ordering is lost
SELECT * FROM orders WHERE customer_id = 101 ORDER BY total;
```
Here `total` isn't part of the index at all, so after finding the matching rows, the database must sort them explicitly by `total` - an explicit sort step, even though the same query with `ORDER BY order_date` would have been free.

### `DESC` and mixed sort directions
Most B-trees can be walked in either direction (forward or backward) at essentially the same cost, so:
```sql
SELECT * FROM orders WHERE customer_id = 101 ORDER BY order_date DESC;
```
is still free - just walk the leaf chain backward instead of forward. Mixed directions across columns are trickier:
```sql
-- Index sorted (customer_id ASC, order_date ASC) cannot natively deliver
-- this order without an explicit sort, because within each customer_id
-- ASC group you'd need order_date DESC - the opposite of storage order
SELECT * FROM orders ORDER BY customer_id ASC, order_date DESC;
```
Some databases support explicitly mixed-direction indexes (`CREATE INDEX ... (customer_id ASC, order_date DESC)`) precisely to make this specific ordering free; without one, this query pays for an explicit sort.

### `GROUP BY` and index order
`GROUP BY` needs identical values brought together, which a sorted index also provides directly - grouping is essentially "walk the sorted stream, and start a new group whenever the value changes," no separate materialize-and-sort step required:
```sql
CREATE INDEX idx_orders_status ON orders(status);

SELECT status, COUNT(*) FROM orders GROUP BY status;
```
Because `idx_orders_status` already delivers rows sorted by `status`, the database can stream through the index leaves, counting within each contiguous run of identical `status` values, and emit a group as soon as the value changes - no hash table, no separate sort. (An optimizer may instead choose a *hash*-based grouping strategy, analogous to hash join in `sql-performance-explained/06`, which doesn't need sorted input at all - a different, also-valid way to avoid an explicit sort, at the cost of memory for the hash table.)

### `DISTINCT` is grouping in disguise
```sql
SELECT DISTINCT status FROM orders;
```
is logically equivalent to `GROUP BY status` with no aggregate - it benefits from the exact same sorted-index reasoning, or the same hash-based alternative.

### What a "filesort" actually costs
When no index supplies the needed order, the database:
1. Collects all rows matching the `WHERE` clause (via whatever access path `sql-performance-explained/01` chose) into a working set.
2. Sorts that entire working set by the `ORDER BY`/`GROUP BY` columns - an `O(n log n)` operation on `n` matching rows.
3. If the working set is larger than the memory budgeted for sorting, the database spills intermediate sorted runs to temporary disk storage and merges them - dramatically slower than an in-memory sort, and the specific reason a query that's fast on a small dataset can become disproportionately slow as the table (or the matched row count) grows.

This is often called a "filesort" (the term originates from MySQL's `EXPLAIN` output but the underlying cost applies universally): it's not necessarily literally writing to a file, but it names the class of problem - an explicit, potentially disk-spilling sort that a well-chosen index could have avoided.

### A worked before/after
```sql
-- Before: no useful index; the database must fetch all "shipped" orders and
-- sort them by order_date explicitly (an explicit sort/filesort step)
SELECT * FROM orders WHERE status = 'shipped' ORDER BY order_date;

-- After: one concatenated index removes the sort entirely
CREATE INDEX idx_orders_status_date ON orders(status, order_date);
SELECT * FROM orders WHERE status = 'shipped' ORDER BY order_date;
-- Rows come back pre-sorted by order_date within status = 'shipped',
-- streamed directly off the index leaves.
```
This is the same left-prefix reasoning from `sql-performance-explained/04` (equality column(s) first, then the sort column) applied specifically to eliminate a sort rather than to speed up filtering - often the *dominant* reason a query is slow, especially for `LIMIT`-based pagination, covered next in `sql-performance-explained/08`.

## Pros
- Eliminating an explicit sort is frequently a bigger performance win than the filtering itself, especially for queries returning many rows.
- The same index-column-order reasoning from `sql-performance-explained/04` applies directly here, so there's nothing new to learn structurally - just one more clause to align the index against.
- Avoiding disk-spilling sorts removes one of the most severe, non-linear slowdown cliffs in query performance.

## Cons
- An index designed to avoid a sort for one query's `ORDER BY` may conflict with a different query's needs (e.g. mixed `ASC`/`DESC` requirements across different call sites), sometimes forcing a choice between multiple specialized indexes.
- Sort-avoiding index design tightens the coupling between index definition and exact query shape - a seemingly harmless change to a query's `ORDER BY` clause can silently reintroduce an expensive sort.
- Not every sort can be avoided by indexing - aggregate functions with complex expressions, or ordering by a computed/non-indexed expression, often have no sort-free path at all.

## Alternatives
- **Accept the sort, but bound its cost** - for queries with a `LIMIT`, some optimizers can use a partial/top-N sort that avoids materializing the entire result, which is cheaper than a full sort even without an index (though still not as cheap as reading pre-sorted index order).
- **Hash-based grouping instead of sort-based grouping** - for `GROUP BY`/`DISTINCT` specifically, a hash table avoids the need for sorted input entirely, trading sort cost for memory cost - the optimizer often picks between these automatically based on estimated group count.
- **Materialized, pre-sorted summary table** - for a `GROUP BY` aggregate queried very frequently, precomputing and storing the grouped result avoids paying grouping cost on every query.

## When to use it
Design (or extend) a concatenated index specifically to match a hot query's equality-filter-then-sort-column shape whenever that query runs frequently or returns a large row count - the sort-avoidance payoff scales with both frequency and result size.

## When NOT to use it
Don't add sort-specific indexes for rarely-run queries or ones that already return very few rows (where even an explicit sort is trivially cheap) - the added write-side index cost isn't justified. Don't assume an index removes a sort without checking the plan (`sql-performance-explained/10`); subtle mismatches (wrong direction, an extra unindexed grouping column) silently defeat it.

## Key takeaways / mental model
Sorting is either "free" (reuse an index's existing sorted order) or "explicit and potentially expensive" (materialize and sort the working set, risking a disk spill). The dividing line is precise alignment: does an available index's column order, direction, and prefix match the query's `ORDER BY`/`GROUP BY` exactly, after accounting for the equality-filter columns already consumed? If yes, free; if no, pay for a filesort.

## Self-check questions
1. Given `CREATE INDEX idx ON events(tenant_id, created_at)`, explain whether `SELECT * FROM events WHERE tenant_id = 5 ORDER BY created_at` needs an explicit sort, and whether `SELECT * FROM events ORDER BY created_at` (no `WHERE`) does too.
2. Why can a B-tree index serve `ORDER BY col DESC` just as cheaply as `ORDER BY col ASC`, but not necessarily `ORDER BY col1 ASC, col2 DESC` from a single ascending-only index?
3. A `GROUP BY` query suddenly becomes much slower after the underlying table grows past a certain size, well beyond what row-count growth alone would explain. What's the likely mechanism, and what term does this lesson use for it?
4. Explain why `SELECT DISTINCT status FROM orders` and `SELECT status, COUNT(*) FROM orders GROUP BY status` can use the exact same index in the exact same way.

## References
- SQL Performance Explained (Markus Winand), Chapter 6: "Sorting and Grouping."
- See also: `sql-performance-explained/02` (index sort order), `sql-performance-explained/04` (left-prefix and column order), `sql-performance-explained/08` (pagination, where sort avoidance matters most), `sql-performance-explained/10` (confirming sort avoidance in an execution plan).
