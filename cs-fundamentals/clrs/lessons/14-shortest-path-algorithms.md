---
id: clrs/14
subject: clrs
title: Shortest-path algorithms
slug: shortest-path-algorithms
status: drafted
mastery:
seniority: mid
source: Introduction to Algorithms (CLRS), Chapters 24-24.3
prerequisites: [clrs/07, clrs/13]
created: 2026-08-10
updated: 2026-08-10
---

# Shortest-path algorithms

## TL;DR
Dijkstra's algorithm finds shortest paths from a single source in graphs with
non-negative edge weights, in O((V+E) log V) using a min-priority queue, via a greedy
"always finalize the closest unfinalized vertex" strategy. Bellman-Ford handles graphs
with negative edge weights (and detects negative-weight cycles, where "shortest path" is
undefined) in O(VE), using repeated relaxation instead of a greedy priority order.

## The idea
BFS (`clrs/13`) finds shortest paths by edge *count* in an unweighted graph, but real
graphs often have weighted edges (distances, costs, latencies), and the shortest path by
total weight can be very different from the shortest path by edge count. Both algorithms
here rely on the same core operation, **relaxation**: given an edge (u,v) with weight w,
if the best known distance to u plus w is less than the best known distance to v, update
v's distance (and predecessor) to that improved value. The algorithms differ entirely in
*which order* they apply relaxation, and that ordering choice is exactly what determines
whether negative weights can be tolerated.

## How it works

### Relaxation, precisely
Maintain `dist[v]` (best known distance from source to v, initialized to infinity except
`dist[source] = 0`) and `pred[v]` (predecessor on that best-known path). RELAX(u, v, w):
if `dist[u] + w < dist[v]`, set `dist[v] = dist[u] + w` and `pred[v] = u`. This single
operation, applied enough times in the right order, is the entire mechanism both
algorithms use — they differ only in scheduling.

### Dijkstra's algorithm
Maintain a min-priority queue (`clrs/07`) of not-yet-finalized vertices, keyed by current
`dist`. Repeatedly extract the minimum (the closest not-yet-finalized vertex), mark it
finalized, and relax all its outgoing edges. Repeat until the queue is empty.

**Why this greedy order is correct (the key insight, and why negative weights break it).**
When a vertex u is extracted as the current minimum, the claim is that `dist[u]` is
already its true shortest distance and will never improve. Why? Any other path to u must
pass through some not-yet-finalized vertex first (since all finalized vertices' shortest
paths are already correctly settled by induction), and every not-yet-finalized vertex
currently has `dist >= dist[u]` (that's exactly why u was the minimum) — and since **all
edge weights are non-negative**, continuing along any path through a not-yet-finalized
vertex can only add non-negative weight, never *decrease* the total below what it already
is. So no alternate path through an unfinalized vertex could possibly beat `dist[u]`.
**This argument requires non-negative weights**: if a later edge could have negative
weight, a longer-looking path through an unfinalized vertex could still end up cheaper
overall, and the greedy "finalize the current minimum" choice could be wrong — which is
exactly why Dijkstra's algorithm gives incorrect results on graphs with negative edges,
not just slower ones.

**Complexity.** With a binary heap, each of the V extract-min operations is O(log V), and
each of the E relaxations potentially triggers a DECREASE-KEY, also O(log V) — total
O((V+E) log V). (A Fibonacci heap, mentioned but not required in CLRS's core treatment,
improves this to O(E + V log V) by making decrease-key O(1) amortized, mattering mainly
for very dense graphs.)

### Bellman-Ford algorithm
Relax **every edge in the graph, V-1 times** (in any fixed order, repeated as a whole
pass V-1 times). No priority queue, no greedy ordering — just brute-force repetition.

**Why V-1 passes suffice.** Any shortest path in a graph with V vertices has at most V-1
edges (a simple path visits each vertex at most once). After the k-th full pass over all
edges, every shortest path using at most k edges has been correctly relaxed into `dist`
(a straightforward induction: a shortest path with k edges is a shortest path with k-1
edges to its second-to-last vertex, plus one more edge — which, by the inductive
hypothesis, was already correct after pass k-1, so pass k correctly extends it). After
V-1 passes, every shortest path (having at most V-1 edges) is correctly computed,
**regardless of the sign of the edge weights** — the algorithm never needs to assume
non-negativity, because it isn't making any greedy commitment about which vertex is
"done" early; it just brute-force-propagates every possible relaxation enough times.

**Negative-cycle detection.** After V-1 passes, run one more full pass over all edges: if
*any* edge can still be relaxed (still improves some `dist[v]`), the graph contains a
negative-weight cycle reachable from the source — "shortest path" is genuinely undefined
in that case (you could loop the negative cycle indefinitely, decreasing the path weight
without bound), and Bellman-Ford's extra pass is precisely how you detect and report this
rather than silently returning a wrong answer.

**Complexity.** V-1 passes, each examining all E edges: O(VE) — substantially worse than
Dijkstra's O((V+E) log V) for graphs where E is not close to V^2, which is the trade-off
you accept in exchange for correctness under negative weights.

### Worked comparison
Consider a graph with an edge of weight -5. Dijkstra's algorithm, upon finalizing some
vertex u early (because its currently-known distance looked smallest), might never
revisit u even if a path through a later-discovered, negative-weight edge would have
given u a smaller true distance — producing a silently wrong answer, not a crash or
error. Bellman-Ford, having no notion of "finalized," keeps relaxing every edge every
pass and will correctly propagate that improvement by the time it's due, as long as no
negative cycle exists to begin with.

### Why not always just use Bellman-Ford to be safe?
Because O(VE) is a real, often large cost difference from O((V+E) log V) at scale —
for a graph with V=100,000 and E=1,000,000 (a fairly typical sparse large graph),
Dijkstra's roughly (V+E)log(V) ≈ 1.1M * 17 ≈ 18.7M operations vastly outperforms
Bellman-Ford's V*E = 100,000,000,000 operations. The choice between them is a genuine
engineering trade-off: use Dijkstra whenever you can *guarantee* non-negative weights
(true for the overwhelming majority of real-world shortest-path use cases — physical
distances, non-refundable costs, latencies — none of which are ever negative), and
reserve Bellman-Ford specifically for the cases that actually need to model negative
weights (e.g. arbitrage detection in currency-exchange graphs, where a negative cycle
literally represents a risk-free profit opportunity).

## Pros
- Dijkstra: near-linear time (O((V+E) log V)) for the extremely common non-negative-
  weight case, using a well-understood, simple-to-implement priority-queue mechanism.
- Bellman-Ford: strictly more general (handles negative weights) and doubles as a
  negative-cycle *detector*, a genuinely useful capability (arbitrage detection,
  constraint-system feasibility checking) beyond plain shortest-path computation.
- Both build on the same simple relaxation primitive, making their correctness proofs and
  implementations conceptually connected rather than unrelated algorithms to memorize
  separately.

## Cons
- Dijkstra silently produces a *wrong* answer (not an error) on graphs with negative
  edges — a dangerous failure mode if you're not certain your graph's weights are all
  non-negative.
- Bellman-Ford's O(VE) is substantially slower than Dijkstra's O((V+E) log V) on large
  sparse graphs — using it "just to be safe" everywhere has a real performance cost.
- Neither algorithm, as presented, computes all-pairs shortest paths efficiently for
  large graphs — that requires either running one of these V times (V*(V+E)log V) or a
  dedicated all-pairs algorithm (Floyd-Warshall, O(V^3), or Johnson's algorithm combining
  Bellman-Ford and Dijkstra, both mentioned in CLRS beyond this lesson's scope).

## Alternatives
- **BFS** (`clrs/13`) — for unweighted graphs (or graphs where all edges have equal
  weight), BFS is simpler and faster (Theta(V+E), no priority queue needed at all) than
  either Dijkstra or Bellman-Ford.
- **A\* search** — for shortest-path queries between one specific source and one specific
  target (not all destinations), A* extends Dijkstra with a heuristic estimate of
  remaining distance, often exploring far fewer vertices in practice — standard in
  routing and pathfinding applications.
- **Floyd-Warshall / Johnson's algorithm** — for all-pairs shortest paths (every vertex to
  every other vertex) rather than single-source, dedicated algorithms avoid the
  redundancy of naively rerunning a single-source algorithm V times.

## When to use it
Use Dijkstra whenever edge weights are guaranteed non-negative (the common case for
physical distances, costs, and latencies) and you need single-source shortest paths. Use
Bellman-Ford when negative edge weights are possible, or when you specifically need to
detect a negative-weight cycle.

## When NOT to use it
Don't use Dijkstra on a graph where negative weights are even possible, without first
verifying they can't occur — a silent wrong answer is worse than a slower but correct
one. Don't use Bellman-Ford's O(VE) by default on large sparse graphs where non-negative
weights are guaranteed — the performance cost compared to Dijkstra is real and often
substantial at scale.

## Key takeaways / mental model
Both algorithms repeatedly apply the same relaxation operation; they differ only in
scheduling. Dijkstra's greedy "always finalize the current closest vertex" order is fast
but assumes non-negative weights make that greedy commitment safe. Bellman-Ford's
brute-force "relax everything, V-1 times" makes no such assumption, tolerates negative
weights, and can detect negative cycles as a byproduct — at a real asymptotic cost.

## Self-check questions
1. Explain precisely why Dijkstra's proof of correctness (finalizing the current minimum
   is always safe) breaks down the moment a negative-weight edge is introduced.
2. Why does Bellman-Ford need exactly V-1 passes (not more, not fewer) to guarantee
   correctness on a graph without negative cycles, and what does the extra V-th pass
   detect?
3. Construct a small graph (3-4 vertices, one negative edge, no negative cycle) where
   Dijkstra's algorithm produces a wrong `dist` value, and trace through why.
4. Given a graph guaranteed to have only non-negative weights and V=1,000,000,
   E=5,000,000, estimate why Dijkstra's O((V+E)log V) would be strongly preferred over
   Bellman-Ford's O(VE) in practice.

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 24:
  "Single-Source Shortest Paths," sections 24.1-24.3.
