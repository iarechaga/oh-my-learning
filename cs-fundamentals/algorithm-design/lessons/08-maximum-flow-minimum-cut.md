---
id: algorithm-design/08
subject: algorithm-design
title: Maximum flow and minimum cut
slug: maximum-flow-minimum-cut
status: drafted
mastery:
seniority: senior
source: Algorithm Design (Kleinberg & Tardos), Chapter 7
prerequisites: [algorithm-design/07, clrs/16]
created: 2026-08-10
updated: 2026-08-10
---

# Maximum flow and minimum cut

## TL;DR
The Ford-Fulkerson method computes maximum flow in a network by repeatedly finding
augmenting paths in a residual graph until none remain; the max-flow min-cut theorem
proves the resulting flow value exactly equals the capacity of the network's bottleneck
(minimum) cut. This book's distinctive emphasis, beyond CLRS's algorithmic treatment
(`clrs/16`), is max flow as a **modeling primitive**: recognizing that a wide range of
seemingly unrelated problems (bipartite matching, image segmentation, project selection,
scheduling with resource constraints) are secretly instances of max flow once you find the
right reduction.

## The idea
`clrs/16` covers the Ford-Fulkerson method, residual graphs, and the max-flow min-cut
theorem's proof in depth. What this book adds, and what this lesson foregrounds, is
*flow network modeling as a design skill*: max flow's real power in practice is less about
implementing the algorithm (usually a library call) and more about recognizing that a
problem you're facing — which may not look like a graph problem at all — can be encoded as
a flow network, at which point a well-understood polynomial algorithm solves it. This
"reduce to a known solvable problem" move is itself a general design technique, distinct
from (and often paired with) the reduction technique used to prove *hardness*
(`algorithm-design/09`).

## How it works

### Flow network basics (brief recap; see clrs/16 for full mechanics)
A flow network is a directed graph with a source s, a sink t, and a capacity c(u,v) >= 0
on each edge. A **flow** f assigns a value to each edge respecting capacity (0 <= f(u,v)
<= c(u,v)) and conservation (flow into a vertex equals flow out, for every vertex except s
and t). The **value** of a flow is the net flow out of s. Maximum flow: the largest
achievable value.

### The max-flow min-cut theorem
An **s-t cut** partitions vertices into two sets S (containing s) and T (containing t);
its capacity is the sum of capacities of edges crossing from S to T. The theorem states:
**the maximum flow value equals the minimum cut capacity, over all possible s-t cuts.**
Intuitively, no flow can exceed any cut's capacity (every unit of flow from s to t must
cross every s-t cut at some point), so max flow <= min cut always; the theorem's real
content is that this bound is always *achievable* — there's no gap.

### Ford-Fulkerson: augmenting paths and residual graphs
Start with zero flow. Repeat: build the **residual graph** (for each edge (u,v) with
capacity c and current flow f, add a forward residual edge with capacity c-f if f<c, and a
backward residual edge with capacity f if f>0 — the backward edge represents the ability
to "undo" flow already sent). Find any path from s to t in the residual graph (an
**augmenting path**); push flow along it equal to the minimum residual capacity on the
path (the **bottleneck**). Repeat until no augmenting path exists.

**Why backward edges matter — worked example.** Vertices s, a, b, t. Edges: s->a (cap 10),
a->b (cap 1), s->b (cap 10), b->t (cap 10), a->t (cap... suppose only s->a, a->b, b->t,
s->b, b->t exist as described). A naive algorithm that greedily saturates s->a->b->t first
(pushing 1 unit, limited by a->b's capacity) without a way to "undo" a poor early choice
could get stuck suboptimally. The residual graph's backward edges are exactly the
mechanism that lets a later augmenting path effectively cancel and reroute an earlier
choice — this is why Ford-Fulkerson with residual graphs (not just naively removing
saturated edges) is necessary for correctness, not just an implementation nicety.

### Termination and the correctness argument
When no augmenting path exists in the residual graph, let S = the set of vertices reachable
from s in the residual graph, T = everything else (t is guaranteed in T, since no s-t path
remains). Every edge crossing from S to T in the *original* graph must be fully saturated
(f = c) — otherwise a residual forward edge would exist, making the far endpoint reachable,
contradicting T's definition. Every edge from T to S in the original graph must carry zero
flow — otherwise a residual backward edge would exist, same contradiction. This means the
current flow's value exactly equals this cut's capacity, and since flow value <= every
cut's capacity always, this flow is simultaneously proven maximum *and* this cut is proven
minimum — the termination condition directly constructs the max-flow min-cut theorem's
proof, rather than needing a separate argument.

### Reduction 1: bipartite matching as max flow
Given a bipartite graph (left set L, right set R, edges only between L and R), find a
maximum matching (maximum set of edges with no shared endpoints). **Reduction**: create a
source s connected to every L vertex (capacity 1 each), every original edge L->R gets
capacity 1, every R vertex connects to a sink t (capacity 1 each). Max flow in this network
exactly equals the maximum matching size — integer-valued max flow (guaranteed when all
capacities are integers, by the augmenting-path construction always pushing integer
amounts) directly corresponds to a valid matching, since capacity-1 edges out of each L
vertex and into each R vertex enforce "used at most once." This reduction is why stable
matching's cousin problems (`algorithm-design/01`) and general bipartite matching are
often solved via off-the-shelf max-flow solvers rather than bespoke matching algorithms.

### Reduction 2: project selection / maximum weight closure
Given projects with profits (possibly negative) and prerequisite dependencies (project A
requires project B also be selected), choose a subset maximizing total profit while
respecting all prerequisites. **Reduction**: build a graph with s connected to every
positive-profit project (capacity = profit), every negative-profit project connected to t
(capacity = |profit|), and infinite-capacity edges encoding prerequisite constraints
(A requires B -> edge A->B with capacity infinity, forcing any min-cut to include B on the
source side whenever A is). The **minimum cut** in this network directly identifies the
optimal project selection — total positive profit minus the min cut value gives the
maximum achievable profit. This reduction is a good illustration of using the *min-cut*
side of the theorem as the actual object of interest, not just flow value.

### Recognizing a max-flow-shaped problem
A recurring skill: a problem is a candidate for max-flow reduction when it involves
selecting/routing/matching subject to capacity or mutual-exclusion constraints between two
"sides" or through a network of resource limits — bipartite matching, image segmentation
(foreground/background as a min-cut), scheduling with resource limits, and project
selection with prerequisites are the canonical examples this book uses to build the
pattern-recognition skill.

## Pros
- Polynomial-time algorithms exist for max flow (Ford-Fulkerson runs in O(E * maxflow) in
  the worst case with arbitrary augmenting path choice; smarter path selection like
  Edmonds-Karp gives O(VE^2), and more advanced algorithms do better still) — a genuinely
  efficient, well-understood tool once a problem is reduced to it.
- The max-flow min-cut theorem gives two views of the same answer (flow value and cut
  capacity), and many practical problems are more naturally phrased in terms of one or the
  other — having both available is a real modeling advantage.
- The reduction technique (encode your problem as a flow network) reuses a single
  well-optimized solver across a huge range of superficially unrelated problems, avoiding
  the need to design and prove correct a bespoke algorithm each time.

## Cons
- Recognizing that a problem reduces to max flow is a non-obvious modeling skill — an
  unrecognized max-flow-shaped problem might get solved with a much more expensive
  bespoke algorithm, or incorrectly assumed to need exponential search.
- Naive Ford-Fulkerson with arbitrary augmenting-path selection can be slow (or even fail
  to terminate) on graphs with irrational capacities; using a specific path-selection rule
  (like Edmonds-Karp's shortest-augmenting-path, or scaling algorithms) is needed for
  guaranteed polynomial performance.
- Flow-network models capture capacity and routing constraints well but don't directly
  express every kind of combinatorial constraint (e.g. general graph coloring doesn't
  reduce naturally to max flow) — over-applying the "maybe this is max flow" instinct
  wastes modeling effort on problems it doesn't fit.

## Alternatives
- **Direct combinatorial algorithms for special cases** — e.g. the Hopcroft-Karp algorithm
  for bipartite matching specifically, which can outperform a generic max-flow solver by
  exploiting the problem's specific structure.
- **Linear programming** — max flow is itself a special case of LP; for problems close to
  but not exactly matching the max-flow model (e.g. with additional side constraints), a
  general LP formulation may be the more flexible, if computationally heavier, alternative.
- **Greedy or DP approaches** (`algorithm-design/04`, `algorithm-design/05`) — for
  problems that don't genuinely have flow-network structure, forcing a max-flow reduction
  is unnecessary complexity compared to a direct greedy or DP solution.

## When to use it
Reach for a max-flow reduction whenever a problem involves matching, routing, or selection
under capacity/mutual-exclusion/prerequisite constraints between two sides or across a
resource-limited network — bipartite matching, project selection with dependencies, and
network capacity/routing problems are the direct fits.

## When NOT to use it
Don't force a max-flow model onto a problem whose constraints aren't genuinely
capacity/routing-shaped — general constraint satisfaction or scheduling problems with
richer constraint types (e.g. general graph coloring, `algorithm-design/09`'s NP-complete
territory) usually don't reduce cleanly and forcing the attempt wastes effort better spent
recognizing the problem is NP-hard and reaching for approximation instead
(`algorithm-design/10`).

## Key takeaways / mental model
Max flow is both an efficient algorithm (Ford-Fulkerson via augmenting paths in a residual
graph) and a modeling primitive: the max-flow min-cut theorem's "no gap between flow and
cut" result is what makes many problems solvable simply by finding the right reduction to
a flow network (bipartite matching via unit-capacity edges, project selection via
positive/negative profit edges and infinite-capacity prerequisite edges). The reduction —
not the algorithm — is usually the hard, creative part in practice.

## Self-check questions
1. Explain why backward (residual) edges are necessary for Ford-Fulkerson's correctness —
   construct a small example where an algorithm without backward edges gets stuck at a
   suboptimal flow.
2. Walk through the termination argument: why does the reachable set S (from s in the
   residual graph) at termination define a cut whose capacity exactly equals the current
   flow's value?
3. Explain the bipartite matching reduction: why does giving every s->L and R->t edge
   capacity exactly 1 correctly enforce "each vertex used at most once" in the resulting
   matching?
4. A colleague has a scheduling problem with resource capacity constraints and asks
   whether it might be a max-flow problem in disguise. What features of the problem would
   you look for to decide?

## References
- Algorithm Design (Jon Kleinberg, Eva Tardos), Chapter 7: "Network Flow."
