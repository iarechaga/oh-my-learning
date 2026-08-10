---
id: clrs/18
subject: clrs
title: Disjoint sets and union-find analysis
slug: disjoint-sets-union-find
status: drafted
mastery:
seniority: mid
source: Introduction to Algorithms (CLRS), Chapter 19
prerequisites: [clrs/17]
created: 2026-08-10
updated: 2026-08-10
---

# Disjoint sets and union-find analysis

## TL;DR
A disjoint-set (union-find) structure maintains a collection of non-overlapping sets,
supporting FIND (which set does x belong to?) and UNION (merge two sets) — with two
independent optimizations, **union by rank** and **path compression**, the amortized
cost per operation becomes essentially O(1) (more precisely, O(inverse-Ackermann(n)), a
function that grows so slowly it's smaller than 5 for any n you could ever represent).

## The idea
Many algorithms (Kruskal's MST, `clrs/15`; certain connectivity and clustering problems)
need to repeatedly ask "are these two elements in the same group?" and "merge these two
groups into one," without needing anything else about the groups (no ordering, no
searching within a group). A naive implementation — e.g. representing each set as a
linked list and merging by concatenation — makes UNION cheap but FIND expensive (O(n)
per lookup if elements don't track their set directly), or the reverse. The union-find
structure with its two classic optimizations achieves near-constant-time performance for
*both* operations simultaneously, which is what makes it the standard tool whenever a
graph or clustering algorithm needs fast, repeated connectivity queries.

## How it works

### The forest-of-trees representation
Each set is represented as a tree (not a balanced search tree — just a plain parent
pointer per node), where the tree's root is that set's designated representative. FIND(x)
walks up parent pointers from x to the root, returning the root as the set's identity.
UNION(x, y) finds each one's root and makes one root point to the other, merging the two
trees into one.

**Naive version's problem.** Without any care about *which* root gets attached to which,
repeated UNIONs can build a very unbalanced tree (e.g. a long chain), making FIND cost
O(n) in the worst case — no better than a plain linked list.

### Optimization 1: union by rank
Track each tree's **rank** (an upper bound on its height, not necessarily its exact
height once path compression is also in play). On UNION, attach the root of the
smaller-rank tree under the root of the larger-rank tree (breaking ties arbitrarily, and
incrementing the surviving root's rank only when the two ranks were equal). This
guarantees a tree of n nodes has height O(log n) — the same style of argument as a
balanced binary structure: attaching a smaller tree under a larger one can at most add 1
to the resulting tree's height, and this can only happen when the two trees were the
same size, bounding how many times height can increase across any sequence of unions.

### Optimization 2: path compression
On every FIND(x), after walking up to the root, make **every node visited along the
way** point directly to the root (not just to its immediate former parent). This doesn't
change the current FIND's asymptotic cost (still proportional to the path length just
walked), but it flattens the tree for **every future** FIND on any of those nodes,
making them O(1) from then on. This is a beautiful example of amortized analysis
(`clrs/17`) in action: individual FIND calls occasionally do real work restructuring the
tree, but that work pays off across all subsequent calls.

### Combined complexity: the inverse Ackermann function
Using **both** optimizations together (not just one alone — each helps, but together
they compound), CLRS proves a sequence of m union/find operations on n elements takes
O(m * alpha(n)) total time, where alpha(n) is the **inverse Ackermann function** — a
function that grows so unbelievably slowly that alpha(n) < 5 for any n you could ever
possibly construct in the physical universe (the Ackermann function itself grows so
explosively fast that its inverse is, for all practical purposes, a constant). This is
one of the most striking results in algorithm analysis: a data structure with a
theoretically non-constant but for-every-practical-purpose-constant per-operation cost.

**Why both optimizations matter together, not just one.** Union by rank alone bounds
height to O(log n) without path compression, giving O(log n) per operation — already
good, but path compression on top of that is what drives the bound down to the
near-constant inverse-Ackermann rate, because path compression's flattening effect
compounds across the whole sequence of operations in a way that interacts specifically
well with the rank-bounded tree shapes union by rank produces.

### Worked example: Kruskal's algorithm revisited
Recall from `clrs/15`: Kruskal's algorithm processes edges in sorted order, and for each
edge (u,v), needs to check "are u and v already connected?" (FIND(u) == FIND(v)?) and,
if not, connect them (UNION(u,v)). Across all E edges, this is E FIND calls plus up to
V-1 UNION calls — with union by rank and path compression, this totals
O(E * alpha(V)) ≈ O(E) for any practical V, which is exactly why Kruskal's overall
complexity is dominated by the initial edge sort (O(E log E)), not by the union-find
bookkeeping at all.

## Pros
- Near-constant amortized time per operation (O(alpha(n)), practically O(1)) for both
  FIND and UNION simultaneously — a rare case where two operations that trade off against
  each other in naive designs are *both* made fast together.
- Extremely simple to implement (an array of parent pointers plus an array of ranks) —
  a handful of lines of code deliver this near-optimal performance.
- Directly enables efficient algorithms elsewhere (Kruskal's MST, `clrs/15`; dynamic
  connectivity queries; certain image-processing and clustering algorithms) that would
  otherwise need a full graph traversal per connectivity check.

## Cons
- Supports only FIND and UNION — no way to *split* a set back apart once merged, and no
  way to enumerate a set's members efficiently (only to test membership/identity via
  FIND) — a genuinely narrow, special-purpose interface.
- The inverse-Ackermann bound, while for-all-practical-purposes constant, is still not
  literally O(1) — a purist worst-case-obsessed context might care about this
  distinction, though it essentially never matters in practice.
- The tree structure carries no information about the elements within a set beyond
  connectivity — if you need, say, the sum or max of a set's elements maintained
  incrementally, that requires augmenting the structure yourself.

## Alternatives
- **Graph traversal (BFS/DFS) per query** (`clrs/13`) — answers the same "are u and v
  connected?" question but at O(V+E) per query, versus union-find's amortized O(alpha(n))
  — union-find wins decisively whenever many connectivity queries are needed over a graph
  that's being incrementally built (edges only added, never removed).
- **Dynamic connectivity structures** (beyond CLRS's scope) — for graphs where edges are
  both added *and* removed over time, plain union-find doesn't support deletion
  efficiently; specialized dynamic-connectivity data structures exist for that harder
  problem.

## When to use it
Use union-find whenever you need repeated "are these connected?" and "merge these"
queries on a graph or partition that only grows (edges/merges only added, never removed)
— Kruskal's MST algorithm, dynamic connectivity checks, and many clustering and
image-segmentation algorithms.

## When NOT to use it
Don't use plain union-find when you need to *undo* a union (split a set back apart) or
when edges/connections can be removed over time — it has no efficient support for either;
a different, more complex dynamic-connectivity structure is needed for that case. Don't
reach for it when you need more than pure connectivity information about each set (e.g.
sorted iteration within a set) without augmenting it — a different structure, or a union-
find with extra per-set metadata tracked alongside, would be needed.

## Key takeaways / mental model
Union-find represents sets as parent-pointer trees; union by rank keeps trees shallow
(O(log n) height) by always attaching the smaller tree under the larger; path compression
flattens trees on every FIND, paying off for all future queries on those nodes. Together,
they give amortized near-O(1) performance — one of algorithm analysis's most striking
results, because the "small" residual cost (inverse Ackermann) is smaller than any number
you could concretely name.

## Self-check questions
1. Explain why union by rank alone (without path compression) already guarantees
   O(log n) height, and what specifically path compression adds on top of that.
2. Walk through what happens to the tree structure during and after a FIND call with
   path compression on a chain of 5 nodes — how does this change the cost of a second
   FIND on the same nodes?
3. Why is union-find the right structure for Kruskal's algorithm's cycle-detection check,
   rather than, say, running BFS/DFS after every candidate edge to check connectivity?
4. Why can't plain union-find efficiently support "undo the last union" or "remove an
   edge," and what would you need to add or change to support that?

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 19: "Data
  Structures for Disjoint Sets."
