---
id: sql-performance-explained/03
subject: sql-performance-explained
title: Selectivity, Cardinality Estimates, and Predicate Shape
slug: selectivity-cardinality-and-predicates
status: drafted
mastery:
seniority: mid
source: SQL Performance Explained (Markus Winand), Chapter 2 - The Where Clause
prerequisites: [sql-performance-explained/02]
created: 2026-08-10
updated: 2026-08-10
---

# Selectivity, Cardinality Estimates, and Predicate Shape

## TL;DR
An index only helps if the optimizer both *estimates* it will be selective enough to be worth using and can actually *apply* the index's sort order to your predicate as written. Selectivity is a number (fraction of rows a condition matches); "sargability" (whether a predicate can search the index at all) is a shape property of the `WHERE` clause - a query can fail on either axis independently, and most "the index isn't being used" bugs trace back to one of them.

## The idea
`sql-performance-explained/01` introduced the idea that the optimizer picks access paths based on estimated row counts, and `sql-performance-explained/02` showed how a B-tree index physically supports fast lookups on its sorted column. This lesson fills the gap between them: how does the optimizer *get* those row-count estimates, and what makes a predicate usable by an index's sort order in the first place? Two independent failure modes live here: bad *cardinality estimates* (the optimizer guesses wrong about how many rows match) and non-*sargable* predicates (the predicate's shape hides the column from the index entirely, regardless of how good the estimate would otherwise be).

## How it works

### Selectivity and cardinality, defined
**Cardinality** of a column is the number of distinct values it holds (e.g. a `status` column with 5 possible values has cardinality 5). **Selectivity** of a specific predicate is the fraction of rows it's expected to match - a `status = 'refunded'` predicate on a column where refunds are 0.5% of rows has selectivity 0.005 (highly selective, good for indexing); `status = 'completed'` at 85% has poor selectivity (a full scan likely wins). High cardinality columns *tend* toward good selectivity for equality predicates, but this isn't automatic - a high-cardinality column can still have a skewed distribution where one value dominates.

The database keeps statistics (row counts, distinct-value counts, sometimes histograms of value frequency) and uses them at plan-compile time to estimate selectivity *before running the query*. This estimate, not the true selectivity, drives the access-path decision from `sql-performance-explained/01`.

### When cardinality estimates go wrong
- **Stale statistics** - if 100,000 new `'refunded'` rows were inserted since statistics were last collected, the optimizer may still think `status = 'refunded'` is rare and choose an index lookup that's now actually worse than a scan. Regularly refreshing statistics (`ANALYZE` / equivalent) is a first-line fix.
- **Data skew a single histogram can't capture** - even fresh statistics summarize a distribution; if `customer_id = 42` (a huge enterprise account with 200,000 orders) is wildly different from `customer_id = 9001` (a small account with 3 orders), a coarse statistic can misestimate either one.
- **Bind-variable / parameter blindness** - a query compiled once with a placeholder (`WHERE customer_id = ?`) and reused for many different actual values can get "stuck" with a plan optimized for the first value it saw, which may be a poor fit for later, differently-selective calls. This is a real, common production surprise: the same query text, same table, same index - different actual parameter, and the cached plan is now wrong.

### Sargability: predicate shape matters as much as selectivity
"Sargable" (Search ARGument ABLE) means the predicate can be evaluated directly against the index's stored, sorted values - i.e., the index can be searched, not just scanned in full. A predicate can be perfectly selective and still be non-sargable if its *shape* hides the column from the index:

```sql
CREATE INDEX idx_employees_last_name ON employees(last_name);

-- Sargable: index can search directly on the stored values
SELECT * FROM employees WHERE last_name = 'Winand';
SELECT * FROM employees WHERE last_name LIKE 'W%';       -- prefix wildcard: sargable
SELECT * FROM employees WHERE last_name BETWEEN 'A' AND 'M';

-- NOT sargable: the column is wrapped, so the index's stored (unwrapped)
-- values no longer match what's being compared
SELECT * FROM employees WHERE UPPER(last_name) = 'WINAND';
SELECT * FROM employees WHERE last_name || '' = 'Winand';
SELECT * FROM employees WHERE SUBSTR(last_name, 1, 1) = 'W';

-- NOT sargable: a leading wildcard defeats the sorted-prefix structure -
-- there is no fixed starting point to jump to
SELECT * FROM employees WHERE last_name LIKE '%nand';
```

The reason `UPPER(last_name) = 'WINAND'` can't use the plain index: the index stores `last_name` values as-is (`'Winand'`, `'winand'`, `'WINAND'` would each sort to a different leaf position), but the query is comparing the *transformed* value. The B-tree's sort order (from `sql-performance-explained/02`) was built on the raw column, not on `UPPER(last_name)`, so there is no way to binary-search the tree for the transformed condition - the database must read every row, apply `UPPER()`, and check. The fix is a **function-based (expression) index**:

```sql
CREATE INDEX idx_employees_last_name_upper ON employees(UPPER(last_name));

SELECT * FROM employees WHERE UPPER(last_name) = 'WINAND';  -- now sargable
```
Now the index physically stores the *uppercased* values in sorted order, matching exactly what the predicate compares against.

The leading-wildcard case (`LIKE '%nand'`) has no equivalent fix with a plain B-tree - there is no "starting letter" to seek to, since the match could begin anywhere in the string. This is one of the reasons full-text search indexes exist as a separate mechanism outside this subject's scope.

### Obfuscated conditions that look sargable but aren't
Predicate shape traps are often subtle:
```sql
-- Looks like a plain equality on order_date, but implicitly wraps it
WHERE YEAR(order_date) = 2026                 -- NOT sargable (function on column)
-- Rewrite as a sargable range instead:
WHERE order_date >= '2026-01-01' AND order_date < '2027-01-01'   -- sargable
```
```sql
-- Type mismatch forces an implicit cast on the indexed column
WHERE numeric_id_column = '123'    -- if numeric_id_column is INTEGER and '123' is
                                    -- a string literal, some databases must convert
                                    -- the *column*, not the literal, defeating the index
```
The general pattern: **anything that transforms the indexed column itself** (a function call, an implicit type cast, string concatenation) breaks sargability, while transforming the *literal* side of the comparison is always safe, because the index is never touched by that transformation.

## Pros
- Once you can name "is this predicate sargable?" and "how selective is it?" as two separate questions, most "why isn't my index used" mysteries resolve quickly.
- Rewriting a non-sargable predicate (moving the transform to the literal side, or adding a function-based index) is usually a small, low-risk change with a large payoff.
- This reasoning transfers across databases - sargability is a relational-algebra property of the predicate, not a vendor-specific quirk.

## Cons
- Function-based indexes add write-time cost like any index, and only help the exact expression they're built on - `UPPER(last_name)` doesn't help `LOWER(last_name)`.
- Fixing sargability sometimes requires touching application query-building code (ORMs in particular love to wrap columns in functions or implicit casts without the developer noticing).
- Cardinality-estimate problems (stale stats, skew, parameter sensitivity) are harder to fix than sargability - they require operational discipline (statistics maintenance) rather than a one-time query rewrite.

## Alternatives
- **Case-insensitive collation at the column/database level** - instead of a function-based index for `UPPER()` comparisons, some databases let you declare a case-insensitive collation on the column itself, making plain equality sargable without any query rewrite - a cleaner fix when case-insensitivity is a permanent requirement, not a one-off query need.
- **Generated/computed columns** - materialize the transformed value as a real (indexed) column maintained by the database, functionally similar to a function-based index but sometimes more portable or easier to reason about.
- **Full-text search indexes** - the right tool when the real need is substring/leading-wildcard/fuzzy text search, which no B-tree rewrite can serve well.

## When to use it
Apply this checklist whenever a query with an apparently-relevant index runs slower than expected: first ask "is the predicate sargable as written?" (check for functions/casts on the indexed column), then ask "is the estimate plausible?" (check statistics freshness and whether the value is unusually skewed).

## When NOT to use it
Don't reach for a function-based index as a first response to every slow query - if the real issue is a stale statistics estimate or a genuinely non-selective predicate (`sql-performance-explained/01`), no amount of predicate rewriting fixes it, because the index was never the bottleneck.

## Key takeaways / mental model
Two separate questions, two separate diagnoses: "How many rows does this match?" (selectivity/cardinality, an estimation problem) and "Can the index's sort order even be searched for this predicate as written?" (sargability, a shape problem). A predicate must pass both checks before an index lookup can help - failing either one alone is enough to force a full scan.

## Self-check questions
1. `WHERE TRIM(email) = 'a@b.com'` against a plain index on `email` fails to use the index. Explain why, and give two different fixes.
2. A query filtering `WHERE order_date = '2026-08-10'` against a well-maintained index is slow only in August, when this particular date has 50x the normal order volume due to a sale. What's the most likely cause, and is it a sargability problem or a cardinality-estimate problem?
3. Rewrite `WHERE amount * 1.1 > 100` so that the `amount` column (indexed) is no longer wrapped in an expression, while keeping the same logical condition.
4. Why can't a function-based index on `UPPER(last_name)` help a query that filters `WHERE LOWER(last_name) = 'winand'`?

## References
- SQL Performance Explained (Markus Winand), Chapter 2: "The Where Clause."
- See also: `sql-performance-explained/01` (access-path choice), `sql-performance-explained/02` (B-tree structure), `sql-performance-explained/10` (reading execution plans to confirm sargability in practice).
