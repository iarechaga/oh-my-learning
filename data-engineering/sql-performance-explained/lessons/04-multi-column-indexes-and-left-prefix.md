---
id: sql-performance-explained/04
subject: sql-performance-explained
title: Multi-Column Indexes and Left-Prefix Behavior
slug: multi-column-indexes-and-left-prefix
status: drafted
mastery:
seniority: mid
source: SQL Performance Explained (Markus Winand), Chapter 3 - Performance and Scalability
prerequisites: [sql-performance-explained/02, sql-performance-explained/03]
created: 2026-08-10
updated: 2026-08-10
---

# Multi-Column Indexes and Left-Prefix Behavior

## TL;DR
A concatenated (multi-column) index is one B-tree sorted first by its first column, then by its second column within each value of the first, and so on - which means it can only be searched efficiently starting from its **leftmost** column(s). Column order in a multi-column index is a design decision with real consequences, not an arbitrary listing.

## The idea
`sql-performance-explained/02` showed that a B-tree index is a single sorted structure. A multi-column (concatenated) index extends that idea: instead of sorting by one column, it sorts by a *tuple* of columns, lexicographically - exactly like a phone book sorted by (last name, first name): all the "Smith"s are grouped together, and within "Smith" they're further sorted by first name. You can efficiently find "all Smiths" or "the Smith named John," but you cannot efficiently find "everyone named John" without scanning the whole book, because first names are only sorted *within* each last name, not globally. This single analogy explains almost everything about how multi-column indexes behave.

## How it works

### The structure
```sql
CREATE INDEX idx_orders_customer_status ON orders(customer_id, status);
```
This index is one B-tree whose leaf entries are sorted by `customer_id` first, and *within* each `customer_id`, by `status`:
```
customer_id | status     ->  sorted leaf order
------------+-----------
   101      | cancelled
   101      | completed
   101      | pending
   102      | cancelled
   102      | completed
   103      | completed
   103      | pending
   ...
```
Notice: `status` values are sorted, but only locally, within each `customer_id` group. Globally, `status = 'cancelled'` values are scattered throughout the index (once per customer), not grouped together.

### The left-prefix rule
A concatenated index on `(a, b, c)` can be used efficiently for predicates on:
- `a` alone
- `a` and `b` together
- `a`, `b`, and `c` together

...but **not** efficiently for predicates on `b` alone, `c` alone, or `b` and `c` without `a` - because without fixing `a` first, there's no single contiguous range of the tree to jump to; matching values are scattered across every `a` group.

```sql
CREATE INDEX idx_orders_customer_status_date ON orders(customer_id, status, order_date);

-- Efficient: uses the full index (customer_id, then status within it)
SELECT * FROM orders WHERE customer_id = 101 AND status = 'completed';

-- Efficient: uses only the customer_id prefix (status/order_date unused for
-- seeking, but rows already grouped by customer_id are fetched from there)
SELECT * FROM orders WHERE customer_id = 101;

-- Efficient: uses the full three-column prefix, and order_date's local sort
-- can also serve an ORDER BY within the equality-filtered group (see below)
SELECT * FROM orders WHERE customer_id = 101 AND status = 'completed'
ORDER BY order_date;

-- NOT efficient: status alone skips customer_id, the leading column - the
-- index cannot be searched, only scanned in full (if used at all)
SELECT * FROM orders WHERE status = 'completed';

-- NOT efficient: order_date alone skips both customer_id and status
SELECT * FROM orders WHERE order_date > '2026-01-01';
```

The rule generalizes: a range or inequality condition on one of the columns "stops" the usable prefix at that point, because after a range condition, the *next* column's ordering is no longer globally meaningful within that range.

```sql
-- customer_id is equality (fine), status is a range (fine, uses prefix so
-- far), but order_date's sort order can no longer be trusted for seeking,
-- because within a *range* of statuses, order_date isn't contiguously sorted
SELECT * FROM orders WHERE customer_id = 101 AND status > 'cancelled'
AND order_date > '2026-01-01';
-- Index is used for (customer_id = 101 AND status > 'cancelled'); the
-- order_date condition is then checked row-by-row on the resulting rows,
-- not searched via the index's sort order.
```
This is why the common design guidance is **equality columns first, then at most one range column last** in a concatenated index: every equality column preserves the prefix; the first range column consumes the remaining usable sort order.

### Choosing column order deliberately
Given the same two columns, different orders serve different queries:

```sql
CREATE INDEX idx_a ON orders(customer_id, status);   -- good for customer_id-first queries
CREATE INDEX idx_b ON orders(status, customer_id);   -- good for status-first queries
```
`idx_a` serves `WHERE customer_id = 101` and `WHERE customer_id = 101 AND status = 'completed'` well, but is useless (as a search structure) for `WHERE status = 'completed'` alone. `idx_b` is the mirror image. Deciding which order to build depends entirely on your actual query patterns - a common heuristic is: put the column used in the most queries, or the more selective column when both appear together (`sql-performance-explained/03`), first. When *both* access patterns are common and important, you may genuinely need two indexes, accepting the extra write cost.

### Interaction with `ORDER BY`
A multi-column index's sort order can satisfy an `ORDER BY` without a separate sort step, but only for columns that come *after* the equality-filtered prefix, in the same order they appear in the index (see `sql-performance-explained/07` for the general rule). In the example above, `ORDER BY order_date` after `customer_id = 101 AND status = 'completed'` is free precisely because both filter columns were equality conditions, leaving `order_date`'s local sort order intact and usable.

## Pros
- One well-designed concatenated index can serve several related query shapes (the column itself, the column plus one more, etc.) without needing a separate index per query.
- Can eliminate a separate sort step for `ORDER BY` when column order lines up correctly, which is often a bigger win than the filtering itself (`sql-performance-explained/07`).
- Scales the "index vs. full scan" reasoning from `sql-performance-explained/01` to compound conditions, which is how most real-world `WHERE` clauses actually look.

## Cons
- Column order is a one-way design commitment per index - reordering means dropping and recreating it (or adding a second index), and getting it wrong silently produces a "the index exists but doesn't help this query" situation.
- Wider indexes (more columns) cost more to store and more to maintain on every write, compounding the general index write-cost trade-off.
- The left-prefix rule is easy to state but easy to violate unintentionally - reordering `WHERE` clauses in the query text has *no* effect (the optimizer reorders predicates freely), but reordering the index's *definition* has everything to do with it, which surprises people who assume the two are symmetric.

## Alternatives
- **Multiple single-column indexes, combined via index intersection/bitmap operations** - some optimizers can combine two separate single-column indexes on the fly, but this is usually less efficient than one well-ordered concatenated index and isn't reliably chosen for every query shape.
- **Covering index (extends this idea further)** - append additional columns purely to avoid a table lookup rather than to filter or sort; the left-prefix rule still governs the filtering/sorting columns, but trailing columns can be "along for the ride." See `sql-performance-explained/05`.
- **Partial index** - filter to a subset of rows (e.g. `WHERE status != 'archived'`) rather than adding more columns, when the real problem is a small, frequently-queried slice of a large table.

## When to use it
Build a concatenated index when queries consistently filter on the same combination of columns together, ordering them equality-columns-first (most selective or most common first among ties), with at most one trailing range/sort column.

## When NOT to use it
Don't build a wide concatenated index speculatively "in case it helps" - unused prefixes of an index provide no benefit while still costing write overhead, and a column buried after an unrelated equality filter it's never actually paired with in real queries is dead weight. Also avoid concatenated indexes when the component queries genuinely need to search by each column independently and equally often - two focused single-column indexes may serve that better than one compromise index.

## Key takeaways / mental model
Think phone book sorted by (last name, first name): great for "all Smiths" and "John Smith," useless as a search structure for "all Johns." A concatenated index's usable prefix runs left to right, through equality columns, and stops at the first range condition - design the column order around your actual queries, not alphabetically or by convenience.

## Self-check questions
1. Given `CREATE INDEX idx ON events(tenant_id, event_type, created_at)`, which of these queries can use the index efficiently for filtering: (a) `WHERE tenant_id = 5`, (b) `WHERE event_type = 'click'`, (c) `WHERE tenant_id = 5 AND created_at > '2026-01-01'`, (d) `WHERE tenant_id = 5 AND event_type = 'click' AND created_at > '2026-01-01'`? Explain each.
2. Why does a range condition on a middle column of a concatenated index prevent the index from being used to search a later column, even though an equality condition on that same middle column would not?
3. You have two equally common query shapes: `WHERE customer_id = ?` alone, and `WHERE status = ? AND customer_id = ?` together. Would one concatenated index on `(customer_id, status)` serve both well? Justify your answer using the left-prefix rule.
4. A teammate reorders the columns in a `WHERE` clause, hoping it will let a `(b, a)` index be used for a query filtering on `a` alone. Explain why this has no effect, and what would actually be needed instead.

## References
- SQL Performance Explained (Markus Winand), Chapter 3: "Performance and Scalability" (concatenated indexes and column order).
- See also: `sql-performance-explained/02` (B-tree structure), `sql-performance-explained/03` (selectivity), `sql-performance-explained/05` (covering indexes), `sql-performance-explained/07` (ORDER BY and index sort order).
