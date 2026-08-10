# SQL Performance Explained

A compact recap of *SQL Performance Explained* by Markus Winand, concept by
concept. This subject builds one continuous mental model - the optimizer's
access-path decision - and then applies it, layer by layer, to indexing,
predicates, joins, sorting, pagination, physical row layout, and finally to
reading execution plans to check every prediction against reality.

Progress note: all 10 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded yet. This
page will gain depth (especially on the concepts the learner finds hard) as
discussions happen - the last section below will fill in from discussion
records.

See the progress table in [README.md](README.md). Reading order is top to
bottom: access-path fundamentals first, then index design (structure,
predicates, column order, covering), then joins/sorting/pagination that build
on that foundation, then clustering as a deeper structural wrinkle, and
finally execution plans as the validation tool for everything before it.

## Access-path fundamentals

- **[sql-performance-explained/01] How the optimizer chooses access paths** -
  every query can be answered by a full table scan (cost proportional to
  table size) or an index lookup (cost proportional to result size plus a
  small lookup tax); the optimizer picks per query, per parameter value,
  based on row-count estimates - not by reading the SQL literally.
  ([lesson](lessons/01-optimizer-access-paths.md))
- **[sql-performance-explained/02] B-Tree index structure and lookup
  mechanics** - an index is a shallow, sorted, self-balancing tree of pages;
  exact-match lookup traverses root -> branch -> leaf in a handful of reads
  regardless of table size, and range lookups walk the sorted, linked leaf
  chain sideways from there - the structural reason logarithmic-cost lookup
  and cheap range scans are possible at all.
  ([lesson](lessons/02-b-tree-index-structure.md))

## Index design

- **[sql-performance-explained/03] Selectivity, cardinality estimates, and
  predicate shape** - two independent failure modes explain most "why isn't
  my index used" bugs: bad cardinality estimates (stale stats, skew,
  parameter sensitivity) and non-sargable predicates (wrapping the indexed
  column in a function or cast defeats the index's sort order, even when
  selectivity is fine).
  ([lesson](lessons/03-selectivity-cardinality-and-predicates.md))
- **[sql-performance-explained/04] Multi-column indexes and left-prefix
  behavior** - a concatenated index sorts lexicographically by its column
  list, so it's only searchable starting from its leftmost column(s); a range
  condition stops the usable prefix, which is why "equality columns first,
  one range column last" is the standard design rule.
  ([lesson](lessons/04-multi-column-indexes-and-left-prefix.md))
- **[sql-performance-explained/05] Covering indexes and index-only
  retrieval** - a normal index lookup pays a second trip to the table per
  matching row; a covering index stores every column a query needs directly
  in its leaves, letting the database skip the table entirely (an
  "index-only scan") - often the single biggest win available for
  high-frequency, fixed-shape queries.
  ([lesson](lessons/05-covering-indexes-and-index-only-retrieval.md))

## Joins, sorting, and pagination

- **[sql-performance-explained/06] Join execution and indexing foreign-key
  relationships** - joins run as one of three algorithms (nested loop, hash,
  sort-merge), each with a cost shape matching the access-path reasoning from
  concept 01 applied per row or per side; foreign-key columns are *not*
  auto-indexed on the referencing side, and that gap is one of the highest-
  leverage, easiest-to-miss schema fixes.
  ([lesson](lessons/06-join-execution-and-fk-indexing.md))
- **[sql-performance-explained/07] ORDER BY, GROUP BY, and avoiding
  expensive sorts** - a sorted index can deliver `ORDER BY`/`GROUP BY`/
  `DISTINCT` output for free by reusing its stored order; when no index
  matches, the database pays for an explicit sort that can spill to disk
  ("filesort") as data grows - frequently a bigger cost than the filtering
  itself.
  ([lesson](lessons/07-order-by-group-by-and-sorts.md))
- **[sql-performance-explained/08] Pagination patterns: OFFSET pitfalls and
  keyset pagination** - `OFFSET` pagination forces the database to walk and
  discard every row before the requested page, an `O(offset)` cost per page
  that degrades linearly with depth; keyset ("seek") pagination reframes
  paging as a sargable range condition on a uniquely-ordered cursor, giving
  constant-cost pages at any depth and immunity to concurrent-insert
  skew. ([lesson](lessons/08-pagination-offset-vs-keyset.md))

## Physical layout and validation

- **[sql-performance-explained/09] Clustering effects and physical row
  ordering trade-offs** - an index says *which* rows match; whether those
  rows sit near each other physically (clustered/index-organized) or
  scattered across a heap determines how expensive fetching them actually
  is. A table can only be clustered by one key, so choosing it is a genuine
  trade-off between the access pattern that gets cheap sequential range
  scans and every other pattern, which does not.
  ([lesson](lessons/09-clustering-and-row-ordering-trade-offs.md))
- **[sql-performance-explained/10] Reading execution plans and validating
  performance hypotheses** - every idea in this subject is a testable
  prediction about what the database will do; `EXPLAIN`/`EXPLAIN ANALYZE`
  is how you check it, and comparing estimated vs. actual row counts at each
  plan node is the single most diagnostic signal for a wrong plan.
  ([lesson](lessons/10-reading-execution-plans.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
