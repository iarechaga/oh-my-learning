---
id: sql-performance-explained/08
subject: sql-performance-explained
title: "Pagination Patterns: OFFSET Pitfalls and Keyset Pagination"
slug: pagination-offset-vs-keyset
status: drafted
mastery:
seniority: mid
source: SQL Performance Explained (Markus Winand), Chapter 7 - Partial Results
prerequisites: [sql-performance-explained/07]
created: 2026-08-10
updated: 2026-08-10
---

# Pagination Patterns: OFFSET Pitfalls and Keyset Pagination

## TL;DR
`OFFSET`-based pagination ("page 500") forces the database to generate and discard every row before the offset, on every single page request - a cost that grows linearly with how deep into the results you page, no matter how good your indexes are. **Keyset pagination** ("give me rows after the last one I saw") turns the same access pattern into a cheap, constant-cost index seek, by reusing exactly the sorted-order reasoning from `sql-performance-explained/07`.

## The idea
"Show me page 500 of the results, 20 rows per page" sounds like it should be trivial - you already have an index that avoids sorting (`sql-performance-explained/07`), so why would deep pages be slow? The answer is that `LIMIT`/`OFFSET` is a description of a *position in the result stream*, and the only way most databases know how to reach position 10,000 in a sorted stream is to walk through positions 1 through 9,999 first and throw them away. The index makes producing the *sorted order* cheap; it does nothing to make *skipping ahead* cheap. Keyset pagination solves this by changing the question from "skip N rows" (a position) to "give me rows greater than this specific value" (a search condition) - which an index can answer directly, at any depth, for the same cost as page 1.

## How it works

### OFFSET pagination and why it degrades
```sql
CREATE INDEX idx_orders_date ON orders(order_date);

-- Page 1
SELECT * FROM orders ORDER BY order_date LIMIT 20 OFFSET 0;
-- Page 500
SELECT * FROM orders ORDER BY order_date LIMIT 20 OFFSET 9980;
```
Both queries can use the index to avoid an explicit sort (`sql-performance-explained/07`) - the index already delivers rows in `order_date` order, so the database walks the leaf chain from the beginning. But `OFFSET 9980` means: walk past the first 9,980 leaf entries (and, if the query selects columns not covered by the index, fetch and discard 9,980 table rows too - see `sql-performance-explained/05`), *then* start returning rows. The database has no way to "jump to position 9,980" in a B-tree - position isn't something the tree indexes; only *value* is. So the cost of fetching page 500 is proportional to 9,980 + 20, not to 20. As users page deeper, each page gets linearly more expensive - `O(offset)` per page, `O(n^2)` in total cost to page through the entire result set page by page. This is the single most common cause of "pagination that was fine in testing but crawls in production once the table has real data."

### Keyset (seek) pagination
Instead of asking for a position, ask for "the next values after the last one you saw":
```sql
-- Page 1 (no prior cursor)
SELECT * FROM orders ORDER BY order_date LIMIT 20;
-- (remember the order_date of the LAST row returned, e.g. '2026-03-04')

-- "Page 2" — really: the next 20 rows after that value
SELECT * FROM orders
WHERE order_date > '2026-03-04'
ORDER BY order_date
LIMIT 20;
```
Now the `WHERE order_date > '2026-03-04'` is a normal, sargable range predicate (`sql-performance-explained/03`) against the index - the database seeks directly to that value in the tree (a handful of page reads, exactly like the range-lookup mechanics from `sql-performance-explained/02`) and walks forward 20 entries. This costs the same whether it's "page 2" or "page 5,000" - **O(log n)** to seek, plus a constant 20 rows to walk, regardless of depth. This is why it's also called "seek" pagination: every page is a fresh seek, never a walk-and-discard.

### Handling ties with a unique tiebreaker
`order_date` alone might not be unique - if two orders share the exact same `order_date`, `WHERE order_date > '2026-03-04'` could skip or duplicate rows across pages. The fix is to always paginate on a unique (or uniquely-combined) key:
```sql
CREATE INDEX idx_orders_date_id ON orders(order_date, id);

SELECT * FROM orders
WHERE (order_date, id) > ('2026-03-04', 8172)
ORDER BY order_date, id
LIMIT 20;
```
The tuple comparison `(order_date, id) > (?, ?)` expands to "either `order_date` is later, or it's exactly equal and `id` is greater" - a compound seek condition matched exactly by the compound index's sort order, per the left-prefix reasoning in `sql-performance-explained/04`. This guarantees a stable, gap-free, duplicate-free page sequence even when `order_date` has ties.

### What keyset pagination gives up
The trade-off is real, not free:
- **No arbitrary jump to "page 500."** Keyset pagination only supports "next N after this cursor" (and, with more care, "previous N before this cursor"). You cannot cheaply compute "jump straight to page 500" without still walking there - keyset removes the *per-page-turn* cost, not the cost of arbitrary random access.
- **The cursor must be a value from the sorted column(s), not a page number.** This usually means changing the API/UI contract from `?page=500` to `?after=2026-03-04T00:00:00Z,8172` - a real integration change, not just a query rewrite.
- **Total counts ("Showing 1-20 of 45,231") still require a separate count query** (or an approximation), since keyset pagination itself doesn't compute the total.

### A quick comparative table
```
                     OFFSET pagination        Keyset pagination
Cost of page 1        O(1)                     O(log n)  (seek)
Cost of page 5,000     O(offset)  (slow)         O(log n)  (same as page 1)
Jump to arbitrary page  Yes (but slow deep in)    No (sequential only)
Stable under concurrent inserts?  No - rows can shift between pages  Yes - cursor position is a value, immune to insertions elsewhere
```
That last row is an under-appreciated bonus: because `OFFSET` is a *position*, a row inserted earlier in the sort order while a user is paging shifts every subsequent row's position by one, causing rows to be skipped or duplicated across page loads. A keyset cursor is a *value*, immune to this - "after `order_date = '2026-03-04', id = 8172`" means the same thing regardless of what else was inserted elsewhere.

## Pros
- Constant-cost pages regardless of depth - removes one of the most common "works in dev, dies in production at scale" performance cliffs.
- Naturally stable under concurrent writes, avoiding the skipped/duplicated-row bugs that `OFFSET` pagination is prone to under real traffic.
- Composes directly with everything already covered: it's just a sargable range predicate (`sql-performance-explained/03`) against an index that also satisfies the `ORDER BY` (`sql-performance-explained/07`).

## Cons
- No cheap arbitrary "jump to page N" - only forward/backward sequential navigation from a known cursor, which doesn't fit every UI (page-number pickers, "jump to last page").
- Requires the client to carry and pass back a cursor (the last-seen sort-key values) instead of a simple page number, which is an API design change, not just a backend optimization.
- Needs a genuinely unique ordering (tiebreaker column) to be correct, which is easy to overlook and produces subtle, hard-to-notice bugs (duplicate or skipped rows on ties) if missed.

## Alternatives
- **OFFSET pagination with a capped max depth** - keep `OFFSET` for its simplicity and UI flexibility, but refuse (or discourage) very deep pages, accepting the limitation rather than the complexity of keyset - a pragmatic compromise for admin UIs with low real paging depth.
- **Approximate/cached total counts** - decouple "how many total results" from the paging mechanism itself (e.g. a periodically refreshed count), since keyset pagination doesn't naturally provide it and an exact `COUNT(*)` on every page load is its own cost.
- **Cursor-based pagination libraries/frameworks** - many web frameworks and APIs (e.g. GraphQL's Relay-style cursors) implement keyset pagination under a standard interface, so you often don't need to hand-roll the cursor encoding yourself.

## When to use it
Use keyset pagination for any feed, list, or API endpoint that can be paged deeply, is accessed frequently, or needs to stay correct under concurrent inserts - infinite scroll, API pagination, activity feeds, and any endpoint where "page 500" is a realistic user or client behavior.

## When NOT to use it
Keep simple `OFFSET` pagination for small, bounded result sets (a settings list with 40 rows total) or admin UIs where users genuinely need to jump to an arbitrary page number and paging depth is inherently shallow - the added API complexity of keyset isn't worth it there.

## Key takeaways / mental model
`OFFSET` asks "skip this many rows" - a position the database can only reach by walking through and discarding everything before it. Keyset pagination asks "give me rows after this value" - a search the index answers directly, at any depth, for the same cost. Prefer designing pagination as a seek (a `WHERE` condition on a sorted, indexed, uniquely-ordered key) rather than a skip whenever depth or scale is a realistic concern.

## Self-check questions
1. A dashboard's "page 1" loads instantly but "page 200" takes several seconds, even though both use `LIMIT 20` against the same indexed, sorted column. Explain the mechanism causing this, in terms of what the database actually has to do for each request.
2. Why does keyset pagination require the ordering to be genuinely unique (e.g. via a tiebreaker column), while `OFFSET` pagination does not have this requirement (even though it has other correctness problems)?
3. A user reports that while scrolling an infinite-scroll feed implemented with `OFFSET`, they occasionally see the same item twice or seem to skip an item. Explain why this happens and how switching to keyset pagination would fix it.
4. Give one concrete UI requirement that keyset pagination genuinely cannot support well, and explain why.

## References
- SQL Performance Explained (Markus Winand), Chapter 7: "Partial Results."
- See also: `sql-performance-explained/03` (sargable range predicates), `sql-performance-explained/04` (compound key ordering for tiebreakers), `sql-performance-explained/07` (getting sort order for free from an index).
