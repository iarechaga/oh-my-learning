---
id: sql-performance-explained/02
subject: sql-performance-explained
title: B-Tree Index Structure and Lookup Mechanics
slug: b-tree-index-structure
status: drafted
mastery:
seniority: junior
source: SQL Performance Explained (Markus Winand), Chapter 1 - Anatomy of an Index
prerequisites: [sql-performance-explained/01]
created: 2026-08-10
updated: 2026-08-10
---

# B-Tree Index Structure and Lookup Mechanics

## TL;DR
A database index is (almost always) a **B-tree**: a shallow, sorted, self-balancing tree of fixed-size pages that lets the database find any indexed value in a handful of page reads, regardless of table size - and then walk sideways along the sorted leaf level to collect a range of matches cheaply. Understanding this structure is what lets you predict *why* an index helps (or doesn't) rather than treating it as a black box.

## The idea
`sql-performance-explained/01` established that index access wins when it can jump straight to matching rows instead of reading the whole table. This lesson explains the actual data structure that makes that jump possible: the B-tree (specifically, most production databases use a B+tree variant, though "B-tree" is the near-universal casual name). The core promise of a B-tree is **logarithmic-time lookup with sorted-order traversal**: it takes only a few page reads to find any value even in a billion-row table, and once you've found one value, the next one in sorted order is right next to it - no re-searching required. That second property is what makes range conditions (`BETWEEN`, `>`, `LIKE 'prefix%'`) and `ORDER BY` cheap, not just exact-match lookups.

## How it works

### The shape of the tree
A B-tree index has three conceptual layers:

```
                [ Root page ]
               /      |      \
       [Branch]   [Branch]   [Branch]
        /  \        /  \        /  \
   [Leaf][Leaf] [Leaf][Leaf] [Leaf][Leaf]  <- sorted, linked left-to-right
```

- **Root page** - one page, the entry point, holding pointers to a handful of branch pages and the key ranges each covers.
- **Branch pages** - intermediate pages, each holding pointers to the next level down, again keyed by ranges. There may be several branch levels for a very large index, but rarely more than 3-4 even for huge tables, because each page holds hundreds of pointers (fan-out).
- **Leaf pages** - the bottom level, holding the actual indexed values in sorted order, each paired with a **rowid** (a physical or logical pointer to the actual table row). Leaf pages are linked to their neighbors, left and right, forming a sorted doubly-linked list.

Because each page can hold hundreds of entries (a branch page storing pointers is small per entry), the tree stays shallow even as the table grows enormously - a table of 10 million rows might need a tree only 3-4 levels deep. This is why index lookup cost is described as **O(log n)**: each level of the tree eliminates most of the remaining rows, so the number of levels (and thus page reads) grows very slowly as the table grows.

### An exact-match lookup, step by step
```sql
CREATE INDEX idx_employees_last_name ON employees(last_name);

SELECT * FROM employees WHERE last_name = 'Winand';
```
1. Start at the root page. It says (roughly) "values starting with A-M are in branch 1; N-Z are in branch 2." `'Winand'` falls in branch 2 - follow that pointer. (1 page read)
2. Branch 2 narrows further: "T-V in leaf-group X; W-Z in leaf-group Y." Follow the pointer for `'W...'`. (1 page read)
3. Land on the leaf page containing `'Winand'`, alongside its rowid. (1 page read)
4. Use the rowid to fetch the actual row from the table (1 more read, unless the index is covering - see `sql-performance-explained/05`).

Four page reads total, regardless of whether the table has 10,000 rows or 10,000,000 - that's the logarithmic-cost promise in action. Compare this to `sql-performance-explained/01`'s full-scan alternative, which would need to read every page of the table.

### A range lookup, step by step
```sql
SELECT * FROM employees WHERE last_name BETWEEN 'Smith' AND 'Turner';
```
1. Traverse the tree exactly as above to find the *first* matching leaf entry (`'Smith'` or the first value after it). This is the same handful of page reads as an exact match.
2. From that leaf entry, walk **sideways** along the linked leaf pages, in sorted order, collecting every entry up to `'Turner'`. No re-traversal of the tree is needed - the leaf level is already sorted and linked, so this is a simple sequential scan of just the leaf pages in range.
3. For each matching leaf entry, fetch the corresponding table row via its rowid (unless covering).

This is exactly why B-trees are so well suited to range conditions and sorted output: the expensive part (tree traversal) happens once, and everything after that is cheap sequential movement through already-sorted data. This same leaf-order property is what lets an index satisfy an `ORDER BY` without a separate sort step - covered in `sql-performance-explained/07`.

### Why "slow indexes despite indexing" happens
An index being present doesn't guarantee it's cheap to use for a *particular* query. Two common traps:
- **Low selectivity** (from `sql-performance-explained/01`): finding the leaf entries is cheap, but if there are 500,000 of them, fetching 500,000 individual table rows via their rowids can be slower than a full scan - the tree traversal was never the bottleneck; the row-fetch fan-out was.
- **Non-sargable predicates**: wrapping the indexed column in a function or applying it inconsistently (e.g. `WHERE UPPER(last_name) = 'WINAND'` against a plain index on `last_name`) prevents the optimizer from using the tree's sort order at all, forcing a full scan. This is the focus of `sql-performance-explained/03`.

## Pros
- Logarithmic lookup cost means index performance degrades extremely gracefully as tables grow - a well-indexed query on a 100-row table and a 100-million-row table can cost roughly the same number of page reads.
- The sorted, linked leaf level makes range scans, `ORDER BY`, and `MIN`/`MAX` queries on the indexed column cheap, not just exact matches.
- The structure is self-balancing - inserts and deletes keep the tree shallow automatically, without manual maintenance in normal operation.

## Cons
- Every index is a second copy of (part of) the data that must be kept in sync on every insert, update, or delete - a cost covered in depth when you look at write-heavy workloads (outside this lesson's scope, but worth remembering: indexes are not free).
- Index lookups fetch matching rows from the table via essentially random-access pointers (rowids), which can be slow on spinning disks or when matches are scattered - see `sql-performance-explained/09` for how physical row clustering affects this.
- A B-tree only helps if the query's predicate can be expressed as a search on the indexed column's sorted values *as stored* - functions, type mismatches, or leading wildcards can defeat it (`sql-performance-explained/03`).

## Alternatives
- **Hash index** - O(1) average lookup for exact-match equality only; no ordering, so it cannot serve range conditions or `ORDER BY`. Useful in databases that support it when you truly only need `=` lookups and want to avoid tree-traversal overhead.
- **Bitmap index** - stores a bit-vector per distinct value rather than a sorted tree; excellent for low-cardinality columns (e.g. a `status` flag) in read-heavy analytical workloads, but expensive to update, making it a poor fit for OLTP write-heavy tables.
- **No index (full scan)** - genuinely preferable for low-selectivity predicates or very small tables, per `sql-performance-explained/01`.

## When to use it
Reach for a standard B-tree index whenever a column is used in equality or range predicates, `ORDER BY`, or joins, and the values you filter on are reasonably selective. It's the correct default index type in essentially every mainstream relational database.

## When NOT to use it
Don't expect a B-tree index to help a low-selectivity predicate (`sql-performance-explained/01`), a predicate hidden inside a function without a matching function-based index (`sql-performance-explained/03`), or a column that's rarely filtered/sorted on at all - every unused index is pure write-amplification cost with no read-side benefit.

## Key takeaways / mental model
Picture the B-tree as a shallow signpost tree sitting on top of a sorted, linked chain of leaf pages. Exact-match lookup: follow signposts down (a few page reads), land on the leaf. Range lookup: follow signposts down once, then walk sideways along the chain. The number of signpost levels barely grows even as the table grows enormously - that's the whole performance story.

## Self-check questions
1. Why does a B-tree lookup cost stay roughly constant (a handful of page reads) even as a table grows from 10,000 to 10,000,000 rows?
2. Explain, in terms of tree traversal vs. leaf-chain walking, why `WHERE last_name BETWEEN 'Smith' AND 'Turner'` is cheap for a B-tree index but a query needing values from many scattered, non-adjacent ranges would not get the same benefit.
3. A colleague adds an index on a column and is confused that a query filtering on it is still slow. List two structural reasons (beyond "the index doesn't exist") that a B-tree index lookup can still be expensive.
4. Why is a hash index unable to serve an `ORDER BY <indexed column>` query efficiently, while a B-tree index can?

## References
- SQL Performance Explained (Markus Winand), Chapter 1: "Anatomy of an Index."
- See also: `sql-performance-explained/01` (access-path choice), `sql-performance-explained/03` (selectivity and predicate shape), `database-internals/03` and `database-internals/06` (deeper index-structure internals).
