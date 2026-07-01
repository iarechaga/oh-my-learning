# SQL Performance Explained

This subject is a practical guide to why SQL queries are fast or slow.
It starts from index structure and access paths, then moves through joins,
ordering, grouping, and pagination patterns that appear in real applications.
You will focus on choosing query and index shapes that match workload reality.

**Source book:** *SQL Performance Explained* - Markus Winand (Markus Winand, 2012).

**Seniority baseline:** mid (lessons range junior->senior).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`sql-performance-explained/<NN>`* (e.g. *"discuss `sql-performance-explained/03`"*). Ordered by dependency: access-path basics first, then index design, then joins/sorting/pagination, and finally execution-plan reasoning.

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | How the optimizer chooses access paths | junior | drafted | — | — | [lesson](lessons/01-optimizer-access-paths.md) | — |
| 02  | B-Tree index structure and lookup mechanics | junior | drafted | — | — | [lesson](lessons/02-b-tree-index-structure.md) | — |
| 03  | Selectivity, cardinality estimates, and predicate shape | mid | drafted | — | — | [lesson](lessons/03-selectivity-cardinality-and-predicates.md) | — |
| 04  | Multi-column indexes and left-prefix behavior | mid | drafted | — | — | [lesson](lessons/04-multi-column-indexes-and-left-prefix.md) | — |
| 05  | Covering indexes and index-only retrieval | mid | drafted | — | — | [lesson](lessons/05-covering-indexes-and-index-only-retrieval.md) | — |
| 06  | Join execution and indexing foreign-key relationships | mid | drafted | — | — | [lesson](lessons/06-join-execution-and-fk-indexing.md) | — |
| 07  | ORDER BY, GROUP BY, and avoiding expensive sorts | mid | drafted | — | — | [lesson](lessons/07-order-by-group-by-and-sorts.md) | — |
| 08  | Pagination patterns: OFFSET pitfalls and keyset pagination | mid | drafted | — | — | [lesson](lessons/08-pagination-offset-vs-keyset.md) | — |
| 09  | Clustering effects and physical row ordering trade-offs | senior | drafted | — | — | [lesson](lessons/09-clustering-and-row-ordering-trade-offs.md) | — |
| 10  | Reading execution plans and validating performance hypotheses | mid | drafted | — | — | [lesson](lessons/10-reading-execution-plans.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Seniority:** `junior` · `mid` · `senior` · `staff` · `principal` - the band whose job the concept anchors.

**Cross-subject prerequisites:** pairs well with `ddia/04` (storage engines), `ddia/05` (OLTP vs OLAP), and `database-internals/03` plus `database-internals/06` for index-structure intuition.
