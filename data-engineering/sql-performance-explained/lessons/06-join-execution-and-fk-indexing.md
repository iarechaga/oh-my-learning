---
id: sql-performance-explained/06
subject: sql-performance-explained
title: Join Execution and Indexing Foreign-Key Relationships
slug: join-execution-and-fk-indexing
status: drafted
mastery:
seniority: mid
source: SQL Performance Explained (Markus Winand), Chapter 4 - The Join Operation
prerequisites: [sql-performance-explained/02, sql-performance-explained/05]
created: 2026-08-10
updated: 2026-08-10
---

# Join Execution and Indexing Foreign-Key Relationships

## TL;DR
A join is just repeated lookups between two row sets, and the optimizer picks among three physical join algorithms (nested loop, hash, sort-merge) based on the same cost reasoning as `sql-performance-explained/01`, applied twice. Foreign-key columns are not automatically indexed by most databases, and an unindexed FK is one of the most common, easy-to-fix causes of a slow join.

## The idea
Conceptually, `SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id` says "for every order, find its matching customer." Physically, the database has to pick *how* to perform that matching at scale - reading every combination is quadratic and unworkable for large tables, so real databases use one of a small set of join algorithms, each with a different cost shape depending on table sizes, available indexes, and whether the result needs to be sorted. Understanding these algorithms turns "why is this join slow" from a mystery into a checklist.

## How it works

### Nested loop join
For each row in the "outer" (driving) table, search the "inner" table for matches - literally a loop within a loop.
```sql
SELECT o.id, c.name FROM orders o JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'pending';
```
If `orders.status = 'pending'` is selective (say, 50 rows) and there's an index on `customers.id` (the primary key, always indexed), the plan looks like:
```
1. Use idx on orders.status to find ~50 pending orders.        (index seek, ~50 rows)
2. For EACH of those 50 orders, seek customers by id (indexed  (50 index seeks,
   PK lookup) to find the matching customer.                    each O(log n))
```
Cost: roughly `driving_rows x cost_of_one_inner_lookup`. This is excellent when the outer/driving side is small and the inner side has a usable index - exactly the shape `sql-performance-explained/01`'s "index wins when selective" reasoning predicts, applied per-row across the join. It degrades badly when the driving side is large or the inner side has no usable index, because each of many outer rows now triggers an expensive inner scan.

### Hash join
Build an in-memory hash table from one side (usually the smaller), then scan the other side once, probing the hash table for matches.
```sql
SELECT o.id, c.name FROM orders o JOIN customers c ON o.customer_id = c.id;
-- (no selective filter - most/all of both tables participate)
```
```
1. Build a hash table from customers, keyed by id.        (one full scan of
                                                             customers, O(n))
2. Scan orders once; for each row, probe the hash table    (one full scan of
   for a matching customer_id.                              orders, O(m))
```
Cost: roughly `O(n + m)` - no index required on the join key at all, because the hash table itself *is* the lookup structure, built fresh in memory for this query. Hash join is typically the optimizer's choice for large, unfiltered (or weakly filtered) joins where nested loop's per-row lookup cost would multiply out to something far worse. Its downside: it needs enough memory to hold the hash table, and it produces results in no particular order (no sort order to reuse for a later `ORDER BY`).

### Sort-merge join
Sort both sides by the join key, then walk them together like merging two sorted lists.
```sql
SELECT o.id, c.name FROM orders o JOIN customers c ON o.customer_id = c.id
ORDER BY o.customer_id;
```
```
1. Sort (or use an already-sorted index on) orders by customer_id.
2. Sort (or use an already-sorted index on) customers by id.
3. Walk both sorted streams together, advancing whichever side is "behind,"
   emitting matches as the keys align.
```
Cost: roughly the cost of sorting both sides (or free, if both are already delivered pre-sorted by matching indexes - see `sql-performance-explained/07`) plus a single linear merge pass, `O(n log n + m log m)` in the worst case, `O(n + m)` if both sides are already sorted. Sort-merge shines specifically when both sides are already sorted (or nearly so) on the join key - e.g. both have a B-tree index on it - because then the "sort" step is essentially free and the result also comes out pre-sorted, which can feed a later `ORDER BY` or `GROUP BY` for free too.

### Why foreign keys need their own index
A `FOREIGN KEY` constraint guarantees referential integrity; it does **not**, in most databases, automatically create an index on the referencing column. The referenced column (usually a primary key on the "one" side) is indexed automatically, but the FK column on the "many" side is not.
```sql
CREATE TABLE customers (id INT PRIMARY KEY, name TEXT);   -- id is indexed (PK)
CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_id INT REFERENCES customers(id),                -- NOT indexed by default
  total NUMERIC
);
```
This asymmetry causes two distinct real-world problems:
1. **Slow joins in the "wrong" direction.** `SELECT * FROM orders WHERE customer_id = 101` (or a join driven from the `customers` side, nested-loop-probing into `orders` per customer) has no index to seek with on `orders.customer_id`, forcing a full scan of `orders` per lookup.
2. **Slow, unnecessary locking/scanning on parent-row deletes.** Deleting a row from `customers` requires checking whether any `orders` rows reference it (to enforce or cascade the constraint); without an index on `orders.customer_id`, that check is a full scan of `orders` for every single delete.

```sql
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```
This single, easy-to-forget index is one of the highest-value, lowest-effort fixes in relational schema design - and its absence is a very common real-world cause of "this join used to be fine and now it's slow as the table grew," because a full scan degrades linearly while an indexed nested loop barely degrades at all (`sql-performance-explained/01`, `sql-performance-explained/02`).

## Pros
- Three distinct join algorithms, each with a clear cost shape, means "why is this join slow" nearly always maps to "which algorithm ran, and did it match the data shape" - a diagnosable question, not a mystery.
- Indexing FK columns is cheap, low-risk, and frequently the single highest-leverage index you can add to an OLTP schema.
- Understanding join algorithms lets you predict how a query will scale *before* running it against production-sized data.

## Cons
- The optimizer's choice among the three algorithms depends on the same cardinality estimates covered in `sql-performance-explained/03`, so it inherits all the same estimate-can-be-wrong risks.
- Hash join's memory requirement means a join that works fine at moderate scale can suddenly spill to disk (much slower) as data grows past available memory, without an intuitive external symptom.
- Indexing every FK column adds write-side cost across the board (`sql-performance-explained/02`'s general index trade-off), so a "always index every FK" policy, while a reasonable default, isn't free.

## Alternatives
- **Denormalize the joined data** - store a copy of frequently-joined columns directly on the row (e.g. `orders.customer_name`) to avoid the join altogether for hot read paths, at the cost of update anomalies and duplicated data - a broader, more invasive alternative than indexing.
- **Materialized join view** - precompute and store the joined result, refreshed periodically, when the join is expensive, run often, and can tolerate some staleness.
- **Force a specific join algorithm via hints** - a last-resort override, analogous to forcing an access path (`sql-performance-explained/01`), for when the optimizer's estimate-driven choice is provably and persistently wrong for a specific query.

## When to use it
Always index foreign-key columns on tables where you'll query, join, delete-cascade, or update-cascade through that relationship in either direction - which, in practice, is nearly every FK in an OLTP schema. Reason about which join algorithm you'd expect for a query before treating slowness as unexplainable.

## When NOT to use it
Don't index an FK column that's genuinely never queried, joined-from, or targeted by cascading deletes/updates on a very write-heavy table where every additional index has measurable cost - a rare case, but worth confirming with actual query patterns rather than assuming. Don't force a join algorithm via hints as a first response; confirm via the execution plan (`sql-performance-explained/10`) that the optimizer's natural choice is actually wrong before overriding it.

## Key takeaways / mental model
A join is "for each row on one side, find matches on the other side" - nested loop does this literally with per-row index seeks; hash join swaps per-row seeks for one shared in-memory lookup structure; sort-merge exploits (or creates) sorted order on both sides to merge in one pass. Foreign keys are indexed on the referenced ("one") side automatically but never on the referencing ("many") side automatically - that gap is yours to close.

## Self-check questions
1. A join between a 100-row filtered `orders` set and a 5-million-row `customers` table, with an index on `customers.id`, is fast. The same query pattern but joining two full, unfiltered multi-million-row tables is slow with the same join algorithm. Which algorithm would you expect the optimizer to switch to for the second case, and why?
2. Explain why a hash join doesn't require an index on the join column, while a nested loop join effectively does (for the inner side) to be efficient.
3. A `customers` row delete is mysteriously slow and appears to lock the `orders` table. What is the most likely missing piece of schema, and why does it cause this specific symptom?
4. Under what condition does a sort-merge join's "sort" step cost effectively nothing, and how does that connect to `sql-performance-explained/07`'s treatment of `ORDER BY`?

## References
- SQL Performance Explained (Markus Winand), Chapter 4: "The Join Operation."
- See also: `sql-performance-explained/01` (access-path cost reasoning), `sql-performance-explained/02` (index lookup mechanics), `sql-performance-explained/07` (sort order reuse), `ddia/04` (storage engine internals underlying these algorithms).
