---
id: clrs/16
subject: clrs
title: Maximum flow and the max-flow min-cut theorem
slug: maximum-flow-min-cut
status: drafted
mastery:
seniority: senior
source: Introduction to Algorithms (CLRS), Chapter 26
prerequisites: [clrs/13]
created: 2026-08-10
updated: 2026-08-10
---

# Maximum flow and the max-flow min-cut theorem

## TL;DR
Given a directed graph with edge capacities, a source, and a sink, the maximum-flow
problem asks for the greatest total flow that can be pushed from source to sink without
exceeding any edge's capacity. The Ford-Fulkerson method finds it by repeatedly pushing
flow along any path with spare capacity in a **residual graph** (which also lets flow be
"undone" via reverse edges) until no such path remains — and the max-flow min-cut theorem
proves that the resulting flow is provably maximum, exactly equal to the capacity of the
graph's smallest "bottleneck" cut.

## The idea
Picture a network of pipes (edges) with capacities, water entering at a source and
draining at a sink — how much water can flow through per unit time, given every pipe's
capacity limit? This is a genuinely different kind of problem from shortest paths or
MSTs: it's not about finding one good path, but about combining flow across *multiple*
paths simultaneously while respecting a global constraint (each edge's total flow can't
exceed its capacity), and — non-obviously — sometimes you must be able to partially
*undo* an earlier flow decision to reach the true optimum, which is exactly what the
residual graph's reverse edges are for.

## How it works

### Flow networks, precisely
A flow network is a directed graph where every edge (u,v) has a capacity c(u,v) >= 0, a
designated source s (no incoming edges needed, conceptually flow originates here) and
sink t (flow's destination). A **flow** f assigns each edge a value 0 <= f(u,v) <=
c(u,v), subject to **flow conservation**: for every vertex except s and t, total flow in
equals total flow out (flow doesn't appear or vanish at intermediate vertices). The
**value** of a flow is the net flow out of s (equivalently, into t). Maximum flow: find
the flow of greatest value satisfying these constraints.

### The residual graph: the key mechanism
Given a current flow f, the **residual graph** G_f has, for every original edge (u,v)
with capacity c(u,v) and current flow f(u,v): a forward residual edge (u,v) with residual
capacity c(u,v) - f(u,v) (how much *more* flow could still be pushed along this edge),
and a **backward residual edge** (v,u) with residual capacity f(u,v) (representing the
ability to *cancel* up to the current amount of flow already pushed along (u,v)).

**Why the backward edge is essential, not optional.** Without it, Ford-Fulkerson could
get stuck at a suboptimal flow: having greedily pushed flow along a path that seemed
good, a better overall solution might require partially routing some of that flow
differently — the backward edge is exactly the mechanism that lets a later augmenting
path "undo" part of an earlier, locally-reasonable-looking choice. This is what makes
Ford-Fulkerson correct despite being a greedy-looking, path-at-a-time algorithm: the
residual graph's structure guarantees that if any additional flow is still possible, some
augmenting path (possibly using backward edges) in the residual graph will find it.

### The Ford-Fulkerson method
While there exists a path from s to t in the residual graph G_f (an **augmenting path**),
find one (via BFS or DFS, `clrs/13`), compute its **bottleneck** (the minimum residual
capacity among all edges on that path — you can't push more flow through the path than
its tightest link allows), and increase flow along every forward edge on the path by that
bottleneck amount (decreasing it along any backward edges used, which correctly models
"cancelling" some previously-committed flow). Repeat until no augmenting path remains —
at that point, no more flow can possibly be pushed, and (proven below) the current flow
is provably maximum.

**Edmonds-Karp refinement.** Ford-Fulkerson as stated doesn't specify *which* augmenting
path to use, and a poor choice (e.g. always picking the path with smallest bottleneck)
can require an enormous, even irrational-input-dependent, number of iterations in the
worst case. **Edmonds-Karp** specifies using **BFS** to always find a shortest (fewest-
edges) augmenting path, which provably bounds the algorithm to O(VE) iterations, each
costing O(E) to find via BFS — total O(VE^2). This is the practical, guaranteed-
polynomial version of the method that's actually used.

### The max-flow min-cut theorem
A **cut** here (s-t cut) partitions vertices into a set S containing s and a set T
containing t; its **capacity** is the sum of capacities of edges going from S to T (edges
from T to S don't count). The theorem states: **the maximum flow value equals the minimum
capacity over all possible s-t cuts.** Intuitively, any flow from s to t must cross every
possible cut, so no flow can ever exceed the tightest (minimum-capacity) cut — that's the
easy direction (weak duality). The theorem's non-obvious content is the *equality*:
Ford-Fulkerson's termination condition (no augmenting path left in the residual graph)
exactly identifies a cut whose capacity equals the current flow value — take S as every
vertex still reachable from s in the final residual graph, T as everything else; every
edge from S to T must be at full capacity (else it would still be a usable forward
residual edge, contradicting "no path exists"), and every edge from T to S must carry
zero flow (else its backward residual edge would offer a usable path) — so the cut's
capacity exactly equals the flow's value, proving both that the flow is maximum and
exhibiting the matching minimum cut simultaneously.

### Worked example, sketched
A network: s -> a (capacity 10), s -> b (capacity 5), a -> t (capacity 5), a -> b
(capacity 15), b -> t (capacity 10). First augmenting path s-a-t, bottleneck
min(10,5)=5: push 5, flow value = 5. Residual graph now has a backward edge a->s
(capacity 5) and a's forward edge to t exhausted (residual 0). Second augmenting path
s-b-t, bottleneck min(5,10)=5: push 5, flow value = 10. Third augmenting path s-a-b-t
(now that a->b, capacity 15, is unused): bottleneck min(residual s-a = 5, a-b = 15,
residual b-t = 5) = 5: push 5, flow value = 15. No further augmenting path exists (s's
outgoing edges are now both at full capacity — s-a used 10/10, s-b used 10/... wait, s-b
capacity was only 5, already used fully in step 2) — final max flow = 15, matching the
min cut {s,a,b} vs {t} with capacity c(a,t) + c(b,t) = 5 + 10 = 15.

## Pros
- Solves a genuinely general problem (network flow with capacity constraints) that models
  an enormous range of applications far beyond literal pipe networks: bipartite matching,
  project selection, image segmentation, airline scheduling, and sports-elimination
  problems can all be reduced to max-flow.
- The max-flow min-cut theorem gives a constructive, verifiable certificate of optimality
  — once you find a flow with no augmenting path left, you automatically also have a
  matching min cut proving no better flow exists, which is a strong and useful guarantee.
- Edmonds-Karp's BFS-based augmenting path choice gives a clean, guaranteed-polynomial
  runtime bound (O(VE^2)) without needing more advanced techniques.

## Cons
- Ford-Fulkerson's runtime, without the Edmonds-Karp refinement, depends on the
  *magnitude* of capacities (each augmentation can increase flow by as little as 1 unit
  if capacities are chosen adversarially and paths are chosen poorly) — a real
  pseudo-polynomial trap that catches naive implementations.
- O(VE^2) (Edmonds-Karp) or even the faster known algorithms (not covered here) can still
  be too slow for very large graphs compared to, say, Dijkstra's near-linear shortest-
  path performance — max flow is a genuinely harder problem class.
- Reducing a real-world problem to max-flow (e.g. recognizing that bipartite matching is a
  flow problem) is a modeling skill that isn't always obvious and takes practice to
  recognize.

## Alternatives
- **Push-relabel algorithms** (mentioned in CLRS beyond this lesson's core scope) — a
  different algorithmic family for max flow, often faster in practice than
  augmenting-path methods for large or dense graphs, at the cost of more implementation
  complexity.
- **Linear programming** — max flow can be formulated and solved as an LP; useful when a
  generic LP solver is already available or when the problem has additional linear
  constraints beyond simple capacities.
- **Bipartite matching via Hopcroft-Karp** — for the specific special case of maximum
  bipartite matching (which reduces to max flow but has additional exploitable structure),
  a dedicated algorithm can outperform generic max-flow methods.

## When to use it
Use max-flow/min-cut whenever a problem can be modeled as pushing a limited resource
through a capacity-constrained network — literal network capacity planning, bipartite
matching, project selection with dependencies, image segmentation, and any "how much can
get from A to B given these bottlenecks" question.

## When NOT to use it
Don't reach for full max-flow machinery when a simpler algorithm suffices for your
specific structure (e.g. plain BFS/DFS connectivity when capacities aren't actually a
constraint, or a dedicated bipartite-matching algorithm when your problem is exactly
that special case). Don't use plain Ford-Fulkerson with arbitrary path selection when
capacities can be large — use Edmonds-Karp's BFS-based selection (or a better-known
algorithm) to guarantee polynomial time regardless of capacity magnitudes.

## Key takeaways / mental model
Max flow is found by repeatedly pushing flow along augmenting paths in a residual graph
that includes "undo" (backward) edges — this is what lets the algorithm reach the true
optimum despite making path-at-a-time greedy-looking choices. The max-flow min-cut
theorem's equality is both a stopping condition (no augmenting path left) and a
certificate of optimality (that same residual-graph structure exhibits a matching minimum
cut).

## Self-check questions
1. Explain why the backward (reverse) residual edges are necessary for Ford-Fulkerson's
   correctness — construct a small example where omitting them would cause the algorithm
   to get stuck at a suboptimal flow.
2. Why does using BFS specifically (Edmonds-Karp), rather than arbitrary path selection,
   guarantee a polynomial number of augmentations, while arbitrary selection can require
   far more (even capacity-magnitude-dependent) iterations?
3. Walk through why the max-flow min-cut theorem's "no augmenting path left" termination
   condition directly identifies a cut whose capacity exactly matches the final flow's
   value.
4. Describe how bipartite matching can be reduced to a max-flow problem (source connected
   to all left-side vertices, sink connected to all right-side vertices, capacity 1
   everywhere) and why the resulting max flow's value equals the maximum matching size.

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 26: "Maximum
  Flow."
