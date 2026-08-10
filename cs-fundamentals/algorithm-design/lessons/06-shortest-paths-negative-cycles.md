---
id: algorithm-design/06
subject: algorithm-design
title: Shortest paths and negative cycles
slug: shortest-paths-negative-cycles
status: drafted
mastery:
seniority: mid
source: Algorithm Design (Kleinberg & Tardos), Chapter 6
prerequisites: [algorithm-design/04, algorithm-design/05, clrs/14]
created: 2026-08-10
updated: 2026-08-10
---

# Shortest paths and negative cycles

## TL;DR
Dijkstra's algorithm (greedy, `algorithm-design/04`) finds shortest paths efficiently but
only when all edge weights are non-negative; the Bellman-Ford algorithm (dynamic
programming, `algorithm-design/05`) handles negative edge weights and detects negative
cycles, at higher cost. This lesson pairs the two as a single design decision point —
*which algorithm does your graph's edge weights force you into* — and treats Bellman-Ford
as the book's flagship example of DP over a graph, distinct from CLRS's more
mechanics-focused treatment (`clrs/14`).

## The idea
Shortest-path problems look uniform ("find the cheapest path from s to every other
vertex") but the *right algorithm* depends entirely on whether negative edge weights are
possible. This isn't a minor implementation detail: Dijkstra's algorithm is provably
*incorrect* in the presence of negative edges (not just slower — wrong), because its
correctness proof depends on a "greedy stays ahead" argument (`algorithm-design/04`) that
assumes distances only increase as you extend a path, an assumption negative edges break
outright. Recognizing this dependency — and recognizing when a shortest-path problem might
even be *ill-defined* (a negative cycle makes "shortest path" meaningless, since you can
loop the cycle indefinitely to decrease cost without bound) — is the core transferable
skill this lesson covers.

## How it works

### Dijkstra's algorithm (non-negative weights only)
Maintain a set S of vertices whose shortest distance from s is already finalized. Repeat:
pick the vertex v not in S with the smallest tentative distance d(v), add it to S, then
**relax** every edge out of v (if d(v) + weight(v,u) < d(u), update d(u)). This is a greedy
algorithm: each vertex, once added to S, is never revisited — this book's "greedy stays
ahead" proof technique (`algorithm-design/04`) shows that when the vertex with the
smallest tentative distance is finalized, that tentative distance is already its *true*
shortest distance, provided every edge weight is non-negative.

**Why the proof breaks with negative edges.** The proof relies on: any path to a
not-yet-finalized vertex must pass through the "frontier" (vertices not yet in S), and
since all subsequent edge weights are non-negative, extending a path can only add
non-negative cost — so the frontier vertex with smallest tentative distance can't possibly
be beaten later by a longer path. A negative edge breaks exactly this: a longer path
(more edges) can have *smaller* total weight than a shorter one already finalized,
meaning a vertex declared "done" by Dijkstra can later turn out to have had a cheaper path
all along, through an edge Dijkstra already stopped considering.

**Worked counterexample.** Vertices s, a, b. Edges: s->a (weight 1), s->b (weight 4), a->b
(weight -3). Dijkstra: finalizes s (d=0), then picks the smallest tentative distance among
{a: 1, b: 4} — picks a (d=1), finalized. Relax a's edges: d(b) = min(4, 1 + (-3)) = -2.
Then finalizes b at d=-2. In this small case Dijkstra happens to still get the right
answer because a was processed before b — but reorder so b is processed before a is
discovered to have a cheaper route through it, and the algorithm finalizes a wrong,
too-large distance for a vertex before ever seeing the negative edge that would have
lowered it. The general failure mode: once Dijkstra finalizes a vertex, it never revisits
it, but with negative edges, a later relaxation could still improve a "finalized"
distance — the algorithm has no mechanism to catch this.

### Bellman-Ford algorithm (handles negative weights, detects negative cycles)
A DP formulation (`algorithm-design/05`): let OPT(i, v) = the shortest path from s to v
using **at most i edges**. Recurrence:

    OPT(i, v) = min( OPT(i-1, v),                                   # don't use the i-th edge
                      min over edges (u,v) of ( OPT(i-1, u) + weight(u,v) ) )  # use edge (u,v) last

Base case: OPT(0, s) = 0, OPT(0, v) = infinity for v != s. Run for i = 1 to n-1 (n =
number of vertices) — any *simple* shortest path (no repeated vertices) uses at most n-1
edges, so if no negative cycle exists, OPT(n-1, v) is the true shortest distance for every
v. Each round relaxes every edge once; n-1 rounds over m edges gives O(n*m) total, strictly
worse than Dijkstra's O((n+m) log n) with a binary heap, but correct even with negative
edges.

**Worked example.** Same graph as above (s->a: 1, s->b: 4, a->b: -3). Round 1 (at most 1
edge): d(a) = 1, d(b) = min(4, from s directly) = 4. Round 2 (at most 2 edges): d(a)
unchanged (no 2-edge path improves it), d(b) = min(4, d(a) + (-3)) = min(4, 1-3) =
min(4,-2) = -2. Round 3: no further improvement (n=3 vertices, so n-1=2 rounds suffice) —
final distances: d(a)=1, d(b)=-2, matching the true shortest paths, unlike a naive
Dijkstra run that processes b before discovering a's improving edge.

### Detecting negative cycles
If a negative cycle is reachable from s, "shortest path" is undefined — you can traverse
the cycle repeatedly to make the path arbitrarily cheap. Bellman-Ford detects this
directly: run one *extra* round (round n, beyond the n-1 needed for simple paths); if any
distance still improves in this extra round, a negative cycle reachable from s exists (a
genuine shortest simple path never needs more than n-1 edges, so any improvement on round
n proves some path is being extended around a cycle for further gain, which is only
possible if that cycle has negative total weight). This detection is itself a valuable,
distinct use case: verifying a graph of currency exchange rates, dependency constraints,
or a difference-constraint system has no negative cycle is often the actual goal, not just
a side effect of computing distances.

### Practical implication: choosing between them
- All edge weights guaranteed non-negative (e.g. physical distances, non-negative costs)
  -> Dijkstra, for its better O((n+m) log n) running time.
- Any edge weight might be negative (e.g. modeling gains/refunds as negative cost, or
  detecting arbitrage in currency exchange graphs) -> Bellman-Ford is required for
  correctness, accepting its higher O(n*m) cost.
- Need to *detect* whether a negative cycle exists at all, independent of computing actual
  distances -> Bellman-Ford's extra round is the standard tool.

### Relation to the general shortest-path landscape
`clrs/14` covers the same two algorithms plus Floyd-Warshall (all-pairs); this lesson's
distinct focus is the *design decision* — recognizing which algorithm your problem's edge
weights force you into, and specifically the negative-cycle detection use case, which
Kleinberg & Tardos frame as a DP state-design exercise (`algorithm-design/05`: OPT(i,v)
parameterized by edge count) rather than as a graph-algorithm-first presentation.

## Pros
- Dijkstra: near-linear performance (O((n+m) log n)) for the common non-negative-weight
  case, the default choice whenever applicable.
- Bellman-Ford: strictly more general (handles negative weights) and doubles as a
  negative-cycle detector, a genuinely useful separate capability.
- Both reuse general design techniques already covered in this subject — greedy
  ("greedy stays ahead," `algorithm-design/04`) and DP (state design,
  `algorithm-design/05`) respectively — reinforcing that shortest paths is an application
  of those paradigms, not a separate topic.

## Cons
- Dijkstra silently produces wrong answers on negative-weight graphs rather than failing
  loudly — a dangerous failure mode if edge weights aren't guaranteed non-negative by
  construction.
- Bellman-Ford's O(n*m) cost is significantly worse than Dijkstra's on large graphs,
  making it a poor default even when weights happen to be non-negative.
- Neither algorithm defines a meaningful answer when a negative cycle is reachable from
  the source — "shortest path" is fundamentally undefined there, and callers must check
  for this explicitly (Bellman-Ford's extra round) rather than trusting a numeric output.

## Alternatives
- **Floyd-Warshall** (`clrs/14`) — all-pairs shortest paths via DP over "intermediate
  vertex allowed," O(n^3); preferable when you need distances between *every* pair, not
  just from a single source, even though it also handles negative weights (still requires
  no negative cycles).
- **A\* search** — when a good admissible heuristic exists (e.g. Euclidean distance for
  geographic shortest paths), often much faster than plain Dijkstra in practice for
  single-target queries, at the cost of needing a problem-specific heuristic.
- **Johnson's algorithm** — reweights a graph with Bellman-Ford once to eliminate negative
  edges, then runs Dijkstra from every vertex; combines Bellman-Ford's generality with
  Dijkstra's speed for the all-pairs case, more efficient than repeated Bellman-Ford runs.

## When to use it
Use Dijkstra whenever edge weights are guaranteed non-negative by the problem's semantics.
Use Bellman-Ford whenever negative weights are possible, or when you specifically need to
detect whether a negative cycle exists (currency arbitrage detection, consistency checking
of difference constraints).

## When NOT to use it
Don't use Dijkstra on a graph where negative edges are even a remote possibility without
first proving they can't occur — the failure mode is silent wrong answers, not a crash.
Don't use Bellman-Ford by default "to be safe" on large graphs where non-negative weights
are actually guaranteed — its O(n*m) cost is a real, avoidable performance tax versus
Dijkstra's near-linear alternative.

## Key takeaways / mental model
Shortest-path algorithm choice is entirely gated by one question: can edge weights be
negative? If no, Dijkstra (greedy, fast, provably correct via "greedy stays ahead" —
`algorithm-design/04`). If yes, Bellman-Ford (DP over edge count, slower, still correct,
and doubles as a negative-cycle detector via one extra relaxation round —
`algorithm-design/05`). A negative cycle reachable from the source makes "shortest path"
undefined, not just harder to compute.

## Self-check questions
1. Walk through the counterexample graph (s->a:1, s->b:4, a->b:-3) and explain precisely
   where Dijkstra's "greedy stays ahead" assumption breaks down.
2. Explain the Bellman-Ford recurrence OPT(i,v) in your own words — what does the "i"
   parameter represent, and why does n-1 rounds suffice for any negative-cycle-free graph?
3. How does Bellman-Ford detect a negative cycle using just one extra round of relaxation,
   and why does an improvement in that extra round prove a negative cycle exists?
4. You're building a shortest-path feature for a road-network navigation app (all edge
   weights are non-negative travel times). A colleague suggests using Bellman-Ford "to be
   safe." How would you respond?

## References
- Algorithm Design (Jon Kleinberg, Eva Tardos), Chapter 4 (Dijkstra's algorithm) and
  Chapter 6 (Bellman-Ford as a dynamic programming application).
