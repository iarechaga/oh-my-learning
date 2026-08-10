---
id: algorithm-design/11
subject: algorithm-design
title: "Coping with NP-hardness: local search and heuristic design"
slug: local-search-heuristics
status: drafted
mastery:
seniority: senior
source: Algorithm Design (Kleinberg & Tardos), Chapter 12
prerequisites: [algorithm-design/09, algorithm-design/10]
created: 2026-08-10
updated: 2026-08-10
---

# Coping with NP-hardness: local search and heuristic design

## TL;DR
Local search starts from some feasible solution and repeatedly moves to a better
"neighboring" solution (defined by a chosen move set) until no neighbor improves, at which
point it has reached a **local optimum** — which may or may not be the true global optimum,
and generally comes with no provable quality guarantee at all, unlike approximation
algorithms (`algorithm-design/10`). This lesson covers how to design a neighborhood
structure, why local search gets stuck, and the standard techniques (random restarts,
simulated annealing) for escaping poor local optima in practice.

## The idea
Approximation algorithms (`algorithm-design/10`) give a provable worst-case bound but
require finding a problem-specific structural or LP-based argument, which sometimes
doesn't exist (general TSP has no bounded approximation at all). Local search takes the
opposite trade: give up the provable guarantee entirely, in exchange for an approach that
applies to almost *any* optimization problem, however unstructured, and that in practice
often finds very good (if not certified-optimal or certified-near-optimal) solutions
quickly. The central design decision — and the one that determines whether local search
works well or poorly on a given problem — is the choice of **neighborhood structure**: what
counts as a small, cheap-to-generate-and-evaluate modification of the current solution.

## How it works

### The generic local search template
```
start with any feasible solution S
while some neighbor S' of S has better objective value than S:
    S = S'   (move to the improving neighbor; often the best one, or the first found)
return S
```
The **neighborhood** N(S) — the set of solutions reachable from S by one "move" — is
entirely problem-specific and is the single biggest design lever: too small a
neighborhood (few, weak moves) gets stuck in poor local optima quickly; too large a
neighborhood (elaborate moves) makes each iteration expensive to evaluate, trading
iteration count for iteration cost.

### Worked example: local search for maximum cut
Given a graph, partition vertices into two sets A and B maximizing the number of edges
crossing between them (an NP-hard problem). **Neighborhood**: moving a single vertex from
its current side to the other side (a "flip" move; |V| possible neighbors from any
solution). **Local search**: repeatedly flip whichever vertex's move most increases the
cut size, until no flip improves it. **A provable quality fact even without a full
approximation proof**: at a local optimum under this neighborhood, every vertex has at
least as many crossing edges as non-crossing edges (else flipping it would improve the
cut) — summing this fact over all vertices shows the local optimum's cut size is always at
least half of all edges, which happens to also be a valid 2-approximation, illustrating
that local search *can* sometimes be shown to coincide with a bounded approximation
ratio, but this requires a separate proof specific to the neighborhood structure — it's
not automatic just because local search is being used.

### Why local search gets stuck: the local-optimum trap
A **local optimum** is a solution with no improving neighbor under the chosen
neighborhood — it says nothing about being globally optimal, only that no *single small
move* improves it. **Worked illustration**: in max-cut with single-vertex-flip
neighborhoods, a solution can be locally optimal (no single flip helps) while a
*two-vertex swap* would improve it substantially — the neighborhood structure itself
determines which local optima exist, and a richer neighborhood (allowing pairs of flips)
generally has fewer, better local optima, at the cost of a neighborhood of size O(V^2)
instead of O(V) to search each iteration.

### The neighborhood-design trade-off, explicit
- **Small neighborhood** (e.g. single-element changes): cheap per-iteration cost, fast to
  search, but more and typically worse local optima to potentially get stuck in.
- **Large neighborhood** (e.g. multi-element changes, or entire sub-structure
  reconstructions): fewer, typically better local optima, but expensive per-iteration
  search cost, sometimes expensive enough that even one iteration is impractical.
There is no universal right answer — designing a good local search algorithm for a new
problem means explicitly reasoning about this trade-off for the specific problem's
structure, an engineering judgment call this book treats as a first-class design skill on
par with choosing a greedy rule (`algorithm-design/04`) or a DP state
(`algorithm-design/05`).

### Escaping poor local optima: random restarts
Run local search multiple times from different random starting solutions, keep the best
result found across all runs. Simple, easy to parallelize (each restart is independent),
but provides no guarantee of eventually finding the global optimum, and its practical
effectiveness depends heavily on how "rugged" the objective landscape is (many
similarly-poor local optima vs. a few dominant good ones).

### Escaping poor local optima: simulated annealing
Instead of only ever moving to improving neighbors, simulated annealing sometimes accepts
a *worse* neighbor, with probability decreasing over time (governed by a "temperature"
parameter that starts high and gradually cools). Early on (high temperature), the
algorithm explores broadly, tolerating many worsening moves, escaping shallow local optima;
late (low temperature), it behaves increasingly like plain greedy local search, settling
into a hopefully-better basin found during the exploratory phase. The acceptance
probability for a worsening move of size delta is typically exp(-delta / temperature) — a
larger worsening or lower temperature makes acceptance less likely. Tuning the cooling
schedule (how fast temperature decreases) is itself a hyperparameter problem with no
universal answer, and a poorly chosen schedule can perform worse than plain local search
with random restarts.

### Why no quality guarantee, in general
Unlike approximation algorithms (`algorithm-design/10`), a generic local search algorithm
comes with **no proof** that its output is within any bounded factor of the true optimum —
the max-cut example above is a *special case* where such a proof happens to exist for that
specific neighborhood; for most problems and neighborhoods, no such proof is available, and
none should be assumed. This is the fundamental trade this lesson is about: broader
applicability and often strong empirical performance, in exchange for giving up the formal
guarantee that is approximation algorithms' entire selling point.

## Pros
- Applies to essentially any optimization problem with a well-defined objective and
  feasible-solution space, including problems where no known approximation algorithm
  exists at all (general TSP being the sharpest example, per `algorithm-design/10`).
- Often fast and simple to implement relative to constructing a problem-specific
  approximation proof (no need to find an LP relaxation or structural lower bound).
- In practice, frequently produces solutions close to optimal on realistic instance
  distributions, even without any formal guarantee — the empirical performance gap between
  "provably alpha-approximate" and "good local search result" is often smaller in practice
  than the lack of a proof would suggest.

## Cons
- No provable worst-case quality guarantee in general — a poorly designed neighborhood or
  an unlucky problem instance can produce arbitrarily bad local optima with no warning.
- Neighborhood design is itself a non-trivial, problem-specific skill with real
  trade-offs (search cost vs. local optimum quality) and no universal recipe.
- Techniques for escaping local optima (random restarts, simulated annealing) add
  hyperparameters (number of restarts, cooling schedule) that themselves need tuning, and
  poor tuning can perform worse than no escape mechanism at all.

## Alternatives
- **Approximation algorithms** (`algorithm-design/10`) — when a provable worst-case bound
  is required or highly valuable, and the problem admits one; strictly preferable to local
  search on that dimension when both are available.
- **Exact algorithms for small/structured instances** — when instance size or structure
  makes exact solving feasible despite general NP-hardness, exact beats any heuristic on
  quality.
- **Genetic algorithms / other metaheuristics** — maintain a *population* of candidate
  solutions and combine them (crossover) in addition to local perturbation (mutation); a
  different exploration strategy than single-solution local search, sometimes better at
  escaping local optima at the cost of more complexity and tuning surface.

## When to use it
Use local search when a problem is NP-hard (or otherwise lacks an efficient exact
algorithm) and either no good approximation algorithm is known, or empirical
near-optimality matters more than a formal worst-case guarantee — this covers a large
fraction of real-world combinatorial optimization (routing, scheduling, layout,
clustering) where problem-specific approximation results may not exist or may be too weak
to be practically useful.

## When NOT to use it
Don't use unadorned local search (no restarts, no annealing) on a problem landscape known
or suspected to have many poor local optima — plain greedy local search will very likely
get stuck early and never explore further. Don't substitute local search for an
approximation algorithm when a provable guarantee is actually required (e.g. contractual
service-level guarantees, safety-critical resource allocation) — local search's lack of a
formal bound makes it unsuitable there regardless of good empirical performance.

## Key takeaways / mental model
Local search trades approximation algorithms' provable guarantee for broad applicability
and often-strong empirical performance: start from a feasible solution, repeatedly move to
a better neighbor under a chosen neighborhood structure, stop at a local optimum. The
neighborhood structure is the central design lever (small = cheap but easily stuck; large
= better optima but expensive per iteration), and techniques like random restarts and
simulated annealing exist specifically to escape poor local optima, at the cost of added
tuning surface, still with no general quality guarantee.

## Self-check questions
1. Explain why a solution being a "local optimum" under one neighborhood structure doesn't
   imply it's a local optimum (or anywhere near the global optimum) under a different,
   richer neighborhood structure — use the max-cut single-flip vs. two-vertex-swap example.
2. Walk through why the max-cut local search result under single-vertex-flip neighborhoods
   is provably at least half of all edges — what property does every vertex satisfy at a
   local optimum, and why does that property force this bound?
3. Describe how simulated annealing's temperature parameter changes the algorithm's
   behavior over time, and why a poorly chosen cooling schedule could make it perform
   worse than plain local search with random restarts.
4. A colleague is choosing between an approximation algorithm with a known 2x guarantee
   and a local search heuristic with no guarantee but empirically better average-case
   performance on their specific data. Under what circumstances would you recommend each?

## References
- Algorithm Design (Jon Kleinberg, Eva Tardos), Chapter 12: "Local Search."
