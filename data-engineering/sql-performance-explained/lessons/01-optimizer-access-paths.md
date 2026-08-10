---
id: sql-performance-explained/01
subject: sql-performance-explained
title: How the Optimizer Chooses Access Paths
slug: optimizer-access-paths
status: drafted
mastery:
seniority: junior
source: SQL Performance Explained (Markus Winand), Chapter 1 - Anatomy of an Index
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# How the Optimizer Chooses Access Paths

## TL;DR
Every SQL statement can be answered in more than one physical way: scan the whole table, or use an index to jump straight to the matching rows. The query optimizer picks between these **access paths** using row-count estimates, not by reading your SQL literally - understanding that choice is the foundation for every other performance concept in this subject.

## The idea
SQL is declarative: you say *what* rows you want, not *how* to fetch them. Underneath every query, the database has to translate your `WHERE` clause into a physical retrieval plan. There are, broadly, two families of plan for finding rows that match a condition:

1. **Full table scan** - read every row in the table (or every page of it), check each one against the condition, keep the matches. Simple, and its cost is proportional to the table's total size, not the size of the result.
2. **Index access** - use an auxiliary structure (an index) that is sorted on the columns you filtered on, so the database can jump directly to the matching rows without touching the rest of the table. Its cost is roughly proportional to the *result size*, not the table size.

The optimizer's job is to pick whichever path is actually cheaper for a *given* query and a *given* amount of data - and "cheaper" is genuinely data-dependent, not a fixed rule. This lesson is about the intuition and math behind that choice; `sql-performance-explained/02` covers exactly how the index structure itself makes fast lookups possible, and `sql-performance-explained/03` covers how the optimizer estimates the row counts that drive this decision.

## How it works

### Why scanning isn't always bad
Consider `SELECT * FROM employees WHERE department = 'Engineering'`. If 80% of the 10,000 rows in `employees` are in Engineering, a full table scan reads roughly 10,000 rows to return roughly 8,000 of them - hardly wasted effort. An index lookup here would still need to fetch those ~8,000 matching rows from the table itself (unless the index is "covering" - see `sql-performance-explained/05`), plus pay the overhead of walking the index structure first. For a *non-selective* condition (one that matches a large fraction of the table), a full scan can genuinely be the faster plan.

Now consider `SELECT * FROM employees WHERE employee_id = 4821` on the same 10,000-row table. Exactly one row matches. A full scan reads (on average) 5,000 rows before finding it; an index on `employee_id` finds it in a handful of steps (see `sql-performance-explained/02` for why it's a handful, not a full read). Here the index wins by orders of magnitude.

The dividing line between these two cases is **selectivity** - what fraction of the table a condition matches - covered in depth in `sql-performance-explained/03`. The core intuition to take from this lesson: index access pays a small, roughly constant "lookup tax" to *locate* the starting point, then pays per-row cost to *fetch* matches; full scan pays no lookup tax but pays per-row cost for the *entire table* regardless of how selective the condition is. Index access wins when the per-row savings (skipping the rows you don't need) outweighs the lookup tax; full scan wins when there's barely anything to skip.

### The optimizer decides per query, using estimates
Crucially, this is not a static, table-wide decision - it's re-evaluated for every query, because different queries against the same table can have wildly different selectivity. `WHERE department = 'Engineering'` (matches 80%) and `WHERE department = 'Facilities'` (matches 0.1%) against the *same* `department` column can legitimately get *different* access paths: a scan for the first, an index lookup for the second. The optimizer makes this call using statistics it keeps about the table - approximate row counts, distinct-value counts, sometimes histograms of value frequency - to *estimate* how many rows a condition will match before actually running the query. Those estimates are necessarily approximate, and when they're wrong (stale statistics, unusual data skew, or a parameter value the optimizer never saw at plan-compile time) the optimizer can pick the wrong access path - which is exactly why performance problems often trace back not to "the index is missing" but to "the index exists but the optimizer didn't choose it," a scenario covered further in `sql-performance-explained/10`.

### A worked comparison
Take a `orders` table with 1,000,000 rows and an index on `status`.

```sql
-- Selective: status = 'refunded' matches ~500 rows (0.05%)
SELECT * FROM orders WHERE status = 'refunded';
-- Optimizer picks: INDEX RANGE SCAN on idx_orders_status, then table lookups
--   cost ~= log(1,000,000) [tree traversal] + 500 [leaf entries] + 500 [table fetches]

-- Non-selective: status = 'completed' matches ~850,000 rows (85%)
SELECT * FROM orders WHERE status = 'completed';
-- Optimizer picks: FULL TABLE SCAN
--   cost ~= 1,000,000 [read every row once, sequentially]
--   (an index path here would cost ~log(1,000,000) + 850,000 + 850,000 -
--    strictly worse, because random-access table fetches are pricier than
--    the scan's sequential reads)
```

Same table, same index available, two different plans - driven entirely by how many rows each condition matches.

### It isn't only about `WHERE`
Access-path choice also interacts with `ORDER BY`, `JOIN`, and `GROUP BY` - an index can sometimes be chosen not because it filters efficiently but because it already delivers rows in the order a later clause needs (avoiding a separate sort, see `sql-performance-explained/07`), or because it's the cheap side of a join (`sql-performance-explained/06`). Access-path reasoning is the lens every later lesson in this subject reuses.

## Pros
- Understanding this decision explains *why* an index that exists is sometimes ignored - it's not a bug, it's the optimizer doing its job on a non-selective query.
- Gives you a mental cost model (lookup tax + per-row cost vs. flat per-row cost) you can apply to almost any query without needing to memorize database-specific optimizer internals.
- Directly explains slow-query symptoms: "the index is right there, why isn't it used?" is answerable once you can estimate selectivity yourself.

## Cons
- The optimizer's choice depends on statistics that can be stale or wrong, so real behavior sometimes diverges from this idealized model - you still need to check the actual execution plan (`sql-performance-explained/10`) rather than reasoning in the abstract.
- Selectivity is a property of the *query's actual parameter value*, not just the column - the same query with a different literal can get a different plan, which surprises people used to thinking "this query uses an index" as a fixed fact.
- The simple two-path model (scan vs. single index) understates real optimizers, which also consider bitmap index combinations, multiple candidate indexes, and join-order interactions - useful as a first mental model, not the whole picture.

## Alternatives
- **Force a specific access path with a hint** - some databases let you override the optimizer (e.g. `FORCE INDEX`, optimizer hints). This trades the optimizer's adaptability for a guarantee, and is a last resort when you're certain the optimizer's estimate is wrong and can't be fixed by refreshing statistics.
- **Materialized/precomputed results** - instead of relying on the optimizer to make an expensive query cheap, precompute and store the answer (a materialized view or a summary table), sidestepping the access-path decision for that query entirely.
- **Denormalization or caching at the application layer** - moves the "how do I avoid scanning" problem outside the database altogether; a different trade-off covered outside this subject's scope.

## When to use it
Use this reasoning whenever a query is slower than expected: ask "roughly what fraction of the table does this condition match?" before assuming an index is missing or broken. It's also the right lens when deciding *whether an index is worth creating at all* - an index on a low-selectivity column may never get used.

## When NOT to use it
Don't over-trust this model for compound conditions, joins, or aggregates without also reading the actual execution plan - selectivity estimation gets much harder once multiple predicates or tables interact, and only the optimizer's real cost estimates (visible via `EXPLAIN`) tell you what will actually happen.

## Key takeaways / mental model
Two access paths, two cost shapes: index access costs "a bit to find the start, then one step per matching row"; full scan costs "one step per row in the whole table, no matter what." The optimizer estimates which is cheaper *per query*, using how many rows the condition is expected to match. When the estimate is right, the plan is right; when it's wrong, that's your bug.

## Self-check questions
1. A table has 2 million rows. A `WHERE` condition is expected to match 900,000 of them. Would you expect the optimizer to choose an index or a full scan, and why?
2. Two queries run against the same `orders` table and the same `status` column, one filtering `status = 'cancelled'` (rare) and one filtering `status = 'completed'` (common). Explain why they can legitimately get two different execution plans even though nothing about the table or index changed.
3. A developer says "I added an index but the query is still slow, so the index must be broken." Give two other explanations that don't involve the index being broken.
4. Why might the "lookup tax" of index access make it worse than a full scan even for a moderately selective condition, if the matching rows are scattered randomly across the table rather than clustered together? (You'll cover the resolution to this in `sql-performance-explained/09`.)

## References
- SQL Performance Explained (Markus Winand), Chapter 1: "Anatomy of an Index."
- See also: `sql-performance-explained/02` (index structure), `sql-performance-explained/03` (selectivity and cardinality), `sql-performance-explained/10` (reading execution plans).
