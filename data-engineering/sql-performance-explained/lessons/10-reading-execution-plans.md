---
id: sql-performance-explained/10
subject: sql-performance-explained
title: Reading Execution Plans and Validating Performance Hypotheses
slug: reading-execution-plans
status: drafted
mastery:
seniority: mid
source: SQL Performance Explained (Markus Winand), Appendix - Execution Plans
prerequisites: [sql-performance-explained/01, sql-performance-explained/03, sql-performance-explained/06, sql-performance-explained/07]
created: 2026-08-10
updated: 2026-08-10
---

# Reading Execution Plans and Validating Performance Hypotheses

## TL;DR
Every idea in this subject - access paths, index structure, sargability, join algorithms, sort avoidance, clustering - is a *prediction* about what the database will do. An execution plan (`EXPLAIN`, or its "actually ran" variant `EXPLAIN ANALYZE`) is how you check the prediction against reality, instead of guessing. Reading plans well means knowing which few numbers and operator names actually matter, and treating estimated vs. actual row counts as the single most diagnostic signal available.

## The idea
Every prior lesson in this subject built a mental cost model: index vs. scan (`sql-performance-explained/01`), tree traversal cost (`sql-performance-explained/02`), sargability (`sql-performance-explained/03`), left-prefix usability (`sql-performance-explained/04`), covering (`sql-performance-explained/05`), join algorithm choice (`sql-performance-explained/06`), sort avoidance (`sql-performance-explained/07`), pagination cost shape (`sql-performance-explained/08`), and clustering (`sql-performance-explained/09`). All of that reasoning produces *hypotheses*: "I expect this query to use an index range scan and avoid a sort." An execution plan is the database's own report of what it actually decided (and, with `ANALYZE`, what actually happened when it ran) - the tool that turns every hypothesis in this subject into a checkable fact.

## How it works

### `EXPLAIN` vs. `EXPLAIN ANALYZE`
- **`EXPLAIN`** (plan-only) shows what the optimizer *intends* to do and its *estimated* costs/row counts, without running the query. Fast, safe to run on anything, but only as accurate as the optimizer's estimates (`sql-performance-explained/03`).
- **`EXPLAIN ANALYZE`** (or equivalent) actually *executes* the query and reports *actual* row counts and timing alongside the estimates. This is the single most valuable diagnostic step in this whole subject, because comparing estimated vs. actual row counts tells you directly whether the optimizer's statistics-driven guess (`sql-performance-explained/03`) was right or wrong - and a large mismatch is the most reliable signal that a plan is wrong for a reason worth investigating, rather than a shrug-worthy inefficiency.

```
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 101 AND status = 'completed'
ORDER BY order_date;

-> Index Scan using idx_orders_customer_status_date on orders
     (cost=0.42..8.61 rows=12 width=64)
     (actual time=0.03..0.09 rows=11 loops=1)
   Index Cond: (customer_id = 101 AND status = 'completed')
```
Reading this: `rows=12` (estimated) vs. `actual ... rows=11` - close enough to trust the rest of the plan's shape. `Index Scan` on the expected index confirms the access path from `sql-performance-explained/01`, and the absence of a separate `Sort` node confirms `sql-performance-explained/07`'s sort-avoidance prediction actually held.

### The operator names map directly to earlier lessons
Reading a plan is largely pattern-matching operator names to the concepts already covered:

| Plan operator (typical names) | Maps to |
| --- | --- |
| `Seq Scan` / `Table Scan` / `Full Scan` | Full table scan, `sql-performance-explained/01` |
| `Index Scan` / `Index Range Scan` | Index access path, `sql-performance-explained/01`, `sql-performance-explained/02` |
| `Index Only Scan` / `Covering Index Scan` | Covering index, no table fetch, `sql-performance-explained/05` |
| `Nested Loop` | Nested loop join, `sql-performance-explained/06` |
| `Hash Join` / `Hash Match` | Hash join, `sql-performance-explained/06` |
| `Merge Join` / `Sort-Merge Join` | Sort-merge join, `sql-performance-explained/06` |
| `Sort` / `Filesort` | Explicit sort not avoided, `sql-performance-explained/07` |
| `HashAggregate` | Hash-based grouping, `sql-performance-explained/07` |

Once you can name what you *expect* to see (from the reasoning in earlier lessons) you're reading the plan to confirm or refute a specific hypothesis, not parsing it cold.

### Diagnosing a mismatch: estimate vs. actual
```
-> Seq Scan on orders (cost=0.00..24531.00 rows=5 width=64)
     (actual time=145.02..145.02 rows=850000 loops=1)
   Filter: (status = 'refunded')
```
Estimated `rows=5`, actual `rows=850000` - a five-order-of-magnitude miss. This single line explains a slow query far better than staring at total timing: the optimizer thought `status = 'refunded'` was highly selective (chose... actually here it *still* chose a scan, but imagine the mirror case where it estimated low and chose an index that then had to fetch 850,000 rows one-by-one - the classic bad-estimate-driven-bad-plan scenario from `sql-performance-explained/03`). The fix, per `sql-performance-explained/03`, is almost always to refresh statistics first, then re-examine; only reach for a hint or forced plan if the estimate remains wrong after that.

### Confirming sargability broke an index
```
-> Seq Scan on employees (cost=0.00..1834.00 rows=1 width=40)
   Filter: (upper((last_name)::text) = 'WINAND'::text)
```
A `Seq Scan` with a `Filter` condition wrapping the column in a function, on a table where an index on `last_name` exists, is the plan-level confirmation of the exact non-sargable-predicate problem from `sql-performance-explained/03` - the giveaway is that the index doesn't even appear in the plan at all, because the optimizer never considered it usable for this predicate shape.

### Confirming a join algorithm and its inputs
```
-> Hash Join (cost=... rows=48000)
   Hash Cond: (o.customer_id = c.id)
   -> Seq Scan on orders o (rows=1000000)
   -> Hash
        -> Seq Scan on customers c (rows=50000)
```
This confirms `sql-performance-explained/06`'s hash-join reasoning directly: both sides are large and unfiltered, so the optimizer built a hash table from the smaller side (`customers`) and streamed the larger side (`orders`) through it - exactly the shape predicted for large, weakly-filtered joins.

### What actually matters when reading a plan
For a working diagnostic habit, in priority order:
1. **Estimated vs. actual row counts at each node** - the biggest single signal of a wrong plan, because it's an estimate problem (`sql-performance-explained/03`), not a structural one.
2. **Which access path/join/sort operator was chosen**, compared against what your mental model (from earlier lessons) predicted.
3. **Where the *time* actually went** (with `ANALYZE`) - the node with the largest actual time/row count is where to focus, not necessarily the top of the plan.
4. **Total cost numbers alone**, without the above three - the least useful signal in isolation; costs are internal, unitless numbers useful for *comparing plans*, not for judging absolute performance.

## Pros
- Turns every earlier lesson's reasoning from a plausible story into a checkable fact, closing the loop between "I think this should be fast" and "I confirmed it is."
- Estimated-vs-actual row count comparison is a fast, reliable, close-to-universal diagnostic that generalizes across databases and query shapes.
- Learning to read plans is a compounding skill: once the vocabulary (scan types, join types, sort/aggregate operators) is familiar, it transfers directly to every future query, in every database that exposes a plan.

## Cons
- Plan output format, operator names, and available detail differ meaningfully across database engines - the *concepts* transfer, the exact syntax and node names don't.
- `EXPLAIN ANALYZE` actually executes the query, which is unsafe to run carelessly against production for expensive or write-modifying statements without care (read-only `SELECT`s are generally safe; be more careful with anything that has side effects).
- Plans describe *what the optimizer decided*, not *why* in full detail - understanding *why* still requires the reasoning from earlier lessons (selectivity, sargability, structure); the plan is the checkpoint, not the explanation on its own.

## Alternatives
- **Database-specific visual plan tools** (e.g. graphical `EXPLAIN` viewers in various database GUIs) - present the same information as text-based `EXPLAIN` output, often easier to scan for complex, deeply nested plans, but not fundamentally different information.
- **Query-level timing/logging** (slow query logs, APM tracing) - useful for finding *which* queries are slow in aggregate across a production system, complementary to (not a replacement for) `EXPLAIN` for understanding *why* a specific query is slow.
- **Synthetic benchmarking against representative data volumes** - since estimates and plans can differ meaningfully between a small dev database and a large production one, testing against production-scale (or realistically-scaled) data is often necessary to catch plan differences that only show up at scale.

## When to use it
Read the execution plan (with `ANALYZE` where safe) any time a query's performance is surprising, before or after applying any fix suggested by earlier lessons in this subject - both to diagnose the actual cause and to confirm a fix actually changed the plan the way you expected.

## When NOT to use it
Don't run `EXPLAIN ANALYZE` (which executes the query) against expensive or side-effecting statements in production without appropriate caution (transactions you can roll back, read replicas, or off-peak timing); use plan-only `EXPLAIN` when you only need the intended plan, not confirmed actual behavior.

## Key takeaways / mental model
Every performance idea in this subject is a hypothesis about what the database will do; an execution plan is how you test it. Read the operator names first (do they match what you predicted?), then compare estimated vs. actual row counts (is the optimizer's model of the data right?) - that combination diagnoses the overwhelming majority of real slow queries.

## Self-check questions
1. A plan shows `Seq Scan` with `Filter: (upper(last_name) = 'WINAND')` even though an index on `last_name` exists. Which earlier lesson's concept does this confirm, and what's the standard fix?
2. Explain why a large mismatch between estimated and actual row counts at a plan node is a more useful diagnostic signal than the node's raw cost number.
3. A plan shows a `Nested Loop` join between two large, unfiltered tables, and the query is slow. Based on `sql-performance-explained/06`'s reasoning, what would you expect a healthier plan to show instead, and why might the optimizer have picked nested loop anyway?
4. Why is `EXPLAIN` (without `ANALYZE`) sometimes insufficient to diagnose a slow query, even though it's safer to run?

## References
- SQL Performance Explained (Markus Winand), Appendix: "Execution Plans" (and plan-reading guidance woven throughout the book's chapters).
- See also: every prior lesson in this subject (`sql-performance-explained/01` through `sql-performance-explained/09`) - this lesson is the validation step for all of them.
