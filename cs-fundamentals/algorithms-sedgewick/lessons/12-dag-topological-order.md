---
id: algorithms-sedgewick/12
subject: algorithms-sedgewick
title: Directed acyclic graphs and topological order
slug: dag-topological-order
status: drafted
mastery:
seniority: mid
source: Algorithms (Sedgewick, Wayne), Section 4.2
prerequisites: [algorithms-sedgewick/10]
created: 2026-08-10
updated: 2026-08-10
---

# Directed acyclic graphs and topological order

## TL;DR
A **topological order** of a directed acyclic graph (DAG) — an ordering of vertices such
that every edge points from earlier to later — exists if and only if the graph has no
directed cycle, and is computed by a single DFS pass: the reverse postorder of the DFS
*is* a valid topological order, with no extra bookkeeping needed beyond what DFS already
tracks.

## The idea
Many real problems are "do X before Y" constraint graphs: course prerequisites, build
dependencies, spreadsheet cell recalculation, task scheduling. Model each constraint as a
directed edge (X must come before Y becomes edge X->Y), and the question "is there a
valid order satisfying every constraint?" becomes "does this directed graph have a
topological order?" The elegant result this lesson covers is that DFS — the same
traversal used for basic reachability in `algorithms-sedgewick/10` — answers this
question and produces the order itself, with almost no additional work.

## How it works

### Detecting a directed cycle first
A topological order cannot exist if the graph has a directed cycle (a cycle among X, Y,
Z would demand X before Y before Z before X — an unsatisfiable constraint loop). Before
computing an order, `DirectedCycle` runs a DFS tracking which vertices are currently
**on the recursion stack** (an `onStack[]` boolean array, separate from the usual
`marked[]` array). A **back edge** — an edge from the current vertex to some vertex still
on the recursion stack — means a cycle exists: the path from that ancestor down to the
current vertex, plus this edge back up, forms the cycle. This is a stricter check than
"already visited": in a DAG, DFS routinely re-encounters already-visited vertices via a
different path (that's fine, not a cycle) but never re-encounters a vertex still
*currently on the stack* (that would be a cycle).

Worked example: DAG-attempt with edges A->B, B->C, C->A. DFS from A: visit A (push onto
recursion stack), visit B (push), visit C (push), C's only edge goes to A — A is still
`onStack[A] = true` — back edge detected, cycle A->B->C->A confirmed. Contrast: edges
A->B, A->C, B->C (no cycle). DFS from A: visit A, visit B, visit C, pop C, back at B, no
more edges, pop B, back at A, visit C again via A->C — but C is already `marked[]` (not
`onStack[]`, since B's subtree already fully returned) — not a back edge, just a
legitimate second path to an already-explored vertex. No cycle.

### Computing topological order via reverse DFS postorder
Once the graph is confirmed acyclic, `DepthFirstOrder` runs DFS and records each
vertex's **postorder** — the order in which vertices are *finished* (all their
descendants fully explored), not the order they're first visited (preorder). The claim,
proved by induction on recursion depth, is: **reverse postorder is a valid topological
order.** Intuitively, a vertex finishes (gets added to postorder) only after everything
reachable from it has already finished — so in the *forward* postorder, a vertex's
dependents (things it points to) come before it; reversing that list puts dependencies
before dependents, exactly the topological property.

Worked example: DAG with edges A->B, A->C, B->D, C->D. DFS from A: visit A, visit B,
visit D (no outgoing edges, finishes first: postorder = [D]), back at B, finishes
(postorder = [D, B]), back at A, visit C, C's only edge goes to D (already marked, skip),
C finishes (postorder = [D, B, C]), A finishes (postorder = [D, B, C, A]). Reverse:
[A, C, B, D]. Check against the edges: A->B (A before B, OK), A->C (A before C, OK),
B->D (B before D, OK), C->D (C before D, OK). Valid topological order — and notably
different from a plain BFS/DFS visit order, which would *not* generally satisfy this
property.

### Why this only works on DAGs
The reverse-postorder construction implicitly assumes no vertex depends on a descendant
of itself, which is exactly the acyclic property. Running it on a cyclic graph produces
an ordering that violates at least one edge's constraint (some edge will point from
later to earlier in the "topological" order) — which is why `DirectedCycle` must run
first (or the two checks combined) whenever the input isn't already guaranteed acyclic.

### Topological sort in scheduling and build systems
This exact algorithm underlies real build systems and package managers: a `Makefile`'s
target dependencies, or a package manager's install-order constraints, form a DAG, and
topological sort produces a valid build/install order. When a build system reports a
"circular dependency" error, it has run exactly the `DirectedCycle` check above and found
a back edge.

## Pros
- Reuses the same DFS traversal already built for reachability (`algorithms-sedgewick/10`)
  — no new traversal algorithm, just different bookkeeping (postorder recording,
  `onStack[]` tracking).
- Both cycle detection and topological order computation run in O(V + E), a single
  linear pass over the graph.
- The reverse-postorder characterization is simple enough to implement correctly from
  memory, unlike some alternative topological-sort formulations (e.g. repeatedly removing
  zero-in-degree vertices, which needs an explicit queue and degree-counting structure).

## Cons
- A topological order is generally **not unique** — a DAG with independent (unconnected)
  subchains admits multiple valid orderings, and DFS-based topological sort picks one
  arbitrarily based on traversal order, which can surprise callers expecting a specific
  "canonical" order.
- The postorder-based construction is a proof-then-use result — the *why* (induction on
  recursion depth) is less immediately intuitive than the mechanical "keep removing
  zero-in-degree vertices" alternative, even though both are O(V+E).
- Requires a full DFS pass (and cycle check) even if only a partial order or a single
  pairwise "does X come before Y" query is needed.

## Alternatives
- **Kahn's algorithm (in-degree removal)** — repeatedly select and remove a vertex with
  in-degree zero, decrementing its neighbors' in-degrees; more intuitive for some
  learners and naturally reports "no valid order" if the queue empties before all
  vertices are removed (equivalent to cycle detection), at the cost of needing an
  explicit in-degree array and queue.
- **Strongly connected components first** (`algorithm-design/07`) — if the graph might
  have cycles but you still want a meaningful order, condense each SCC into a single
  node first (producing a genuine DAG), topologically sort that, then order vertices
  within each SCC by whatever secondary criterion applies.

## When to use it
Use DFS-based topological sort whenever you have a dependency DAG (build systems, task
scheduling, course prerequisites, spreadsheet recalculation order) and need any valid
order satisfying all "before" constraints, with the fewest new concepts beyond DFS
itself.

## When NOT to use it
Don't apply topological sort to a graph that might contain cycles without checking
first (or combining the check) — running it blindly on a cyclic graph silently produces
an order that violates some edge's constraint rather than failing loudly. Don't use it
when a unique canonical order matters (e.g. reproducible build output) without also
imposing a deterministic tie-breaking rule, since plain DFS order depends on adjacency
list iteration order.

## Key takeaways / mental model
A topological order exists exactly when a directed graph has no cycle, checkable via DFS
tracking which vertices are currently on the recursion stack (a back edge to an
`onStack` vertex means a cycle). Given an acyclic graph, the **reverse of DFS postorder**
is a valid topological order — a vertex finishes only after everything it points to has
already finished, so reversing that finish order puts dependencies before dependents.
Both computations reuse a single O(V+E) DFS pass with different bookkeeping, not a new
traversal algorithm.

## Self-check questions
1. Explain, using the A->B, B->C, C->A example, exactly why `onStack[]` is needed and
   why checking only `marked[]` would fail to detect this cycle correctly.
2. Walk through why reverse postorder (not forward postorder, and not preorder) is the
   one that produces a valid topological order.
3. Give a concrete real-world DAG (other than build systems) where topological sort
   directly answers a practical scheduling question.
4. Why is a DAG's topological order generally not unique, and what would you need to add
   to the algorithm to make the output deterministic and reproducible across runs?

## References
- Algorithms, 4th Edition (Robert Sedgewick, Kevin Wayne), Section 4.2 ("Directed
  Graphs").
