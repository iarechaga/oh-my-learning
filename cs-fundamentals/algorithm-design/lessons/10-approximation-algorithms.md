---
id: algorithm-design/10
subject: algorithm-design
title: "Coping with NP-hardness: approximation algorithms"
slug: approximation-algorithms
status: drafted
mastery:
seniority: senior
source: Algorithm Design (Kleinberg & Tardos), Chapter 11
prerequisites: [algorithm-design/09, clrs/20]
created: 2026-08-10
updated: 2026-08-10
---

# Coping with NP-hardness: approximation algorithms

## TL;DR
An **alpha-approximation algorithm** runs in polynomial time and is guaranteed to
produce a solution within a provable factor alpha of optimal, for *every* input, even
though the optimal value itself is never computed (or even known). This lesson's distinct
emphasis over CLRS's example-driven treatment (`clrs/20`) is the **design and proof
technique**: bound the optimal solution's value indirectly (via a relaxation, a
structural lower/upper bound, or an LP relaxation) since the true optimum is NP-hard to
compute directly, then compare your algorithm's output to that bound instead.

## The idea
Once a problem is proven NP-complete (`algorithm-design/09`), exact polynomial-time
solutions are (almost certainly) unavailable, but giving up on any guarantee at all — pure
heuristics with no provable bound — is often unsatisfying for high-stakes applications.
Approximation algorithms occupy the middle ground: sacrifice exactness for a *provable*
worst-case bound. The central technical challenge that gives this area its character:
since you cannot compute OPT (the true optimal value) efficiently, every approximation
proof has to bound your algorithm's output against some *other*, efficiently-computable
quantity that is itself provably no better than OPT (a lower bound, for minimization
problems, or an upper bound, for maximization problems) — the proof's creativity lives
almost entirely in finding that comparison point.

## How it works

### The core proof pattern
For a minimization problem, an alpha-approximation algorithm produces a solution SOL with
SOL <= alpha * OPT for every instance, alpha >= 1. Since OPT is unknown, the standard proof
technique is:
1. Find some efficiently-computable quantity LB (lower bound) with **LB <= OPT** provably,
   for every instance (this is the hard, creative step).
2. Prove **SOL <= alpha * LB** directly by analyzing the algorithm (this is usually more
   mechanical, an algorithm-specific argument).
3. Chain: SOL <= alpha * LB <= alpha * OPT — done, without ever computing OPT.
(For maximization problems, the pattern mirrors this with an upper bound UB >= OPT and
SOL >= (1/alpha) * UB.)

### Worked example 1: vertex cover, a 2-approximation via structural bound
Given a graph, find a minimum vertex cover (a set of vertices touching every edge).
**Algorithm**: repeatedly pick any uncovered edge (u,v), add *both* u and v to the cover,
remove all edges now covered, repeat until no edges remain. **Proof**: let M be the set of
edges picked this way — no two edges in M share an endpoint (each pick removes both
endpoints' edges from consideration), so M is a **matching**. Any vertex cover must include
at least one endpoint of every edge in M (since M's edges are disjoint, no single vertex
can cover two of them) — so **OPT >= |M|** (this is the lower bound, LB = |M|, a
structural fact about matchings vs. covers). The algorithm's output has size exactly 2|M|
(two vertices added per matching edge). So SOL = 2|M| = 2*LB <= 2*OPT — a clean
2-approximation, and notably the *lower bound* (matching size) is the creative insight,
not the simple algorithm itself.

### Worked example 2: set cover, a greedy ln(n)-approximation via LP relaxation-style
reasoning
Given a universe of n elements and a collection of subsets, each with a cost, choose a
minimum-cost sub-collection whose union covers all n elements. **Algorithm**: repeatedly
choose the subset covering the most *currently uncovered* elements per unit cost
(greedy by cost-effectiveness), until everything is covered. **Proof sketch**: charge each
element, when it gets covered, a cost equal to (chosen subset's cost) / (number of
newly-covered elements at that step). It's shown that the total charged cost equals the
algorithm's total cost exactly (by construction), and each element's charge is bounded by
OPT/(remaining uncovered elements at that point) — summing a harmonic-series-like bound
across all n elements gives total cost <= H(n) * OPT, where H(n) = 1 + 1/2 + 1/3 + ... +
1/n ~ ln(n). This is a fundamentally different (and, notably, provably *tight* — no better
constant-factor approximation exists for set cover unless P=NP) bound than vertex cover's
clean factor-2, illustrating that different problems admit very different *quality* of
achievable approximation guarantee, not just different algorithms.

### Worked example 3: LP relaxation as the source of the lower bound
For many problems (including vertex cover, via an alternate proof), formulate the exact
problem as an **integer linear program** (ILP): variables constrained to {0,1}, an
objective to minimize/maximize, and constraints encoding the problem (e.g., for vertex
cover: for each edge (u,v), x_u + x_v >= 1, minimize sum of x_v). Solving the ILP exactly
is itself NP-hard (integer constraints are what make it hard) — but **relaxing** the {0,1}
constraint to the continuous interval [0,1] gives a **linear program (LP)**, solvable in
polynomial time. Since the LP's feasible region is a superset of the ILP's (every valid
0/1 solution is also a valid fractional solution), the **LP's optimal value is always at
least as good as the ILP's optimal value** — giving exactly the lower/upper bound needed
for an approximation proof, without any problem-specific structural argument like
matchings. **Rounding** the LP's fractional solution back to integers (e.g., "round x_v to
1 if x_v >= 0.5" for vertex cover) while bounding how much the rounding can hurt the
objective is the standard technique that converts an LP-relaxation bound into an actual
approximation algorithm — vertex cover's rounding scheme also achieves the same factor-2
bound as the matching-based proof above, illustrating that the same approximation ratio
can sometimes be reached via genuinely different proof techniques.

### Comparing approximation ratios: not all NP-hard problems are equally approximable
- Vertex cover: constant factor 2, achievable by a simple algorithm.
- Set cover: ln(n) factor, and this is *provably the best possible* (unless P=NP) — no
  constant-factor approximation exists.
- The general Traveling Salesman Problem (no triangle inequality assumed): **no
  polynomial-time approximation with any bounded factor exists** (unless P=NP) — if it
  did, it would let you solve Hamiltonian Cycle exactly (a reduction argument in the style
  of `algorithm-design/09`, applied here to rule out approximability rather than to prove
  hardness).
- Metric TSP (triangle inequality holds, a realistic assumption for e.g. geographic
  distances): a 2-approximation exists via minimum spanning tree doubling, and a
  1.5-approximation via the more involved Christofides algorithm.
This spread is itself an important lesson: "NP-hard" alone doesn't tell you what quality
of approximation to expect — that requires a separate, problem-specific investigation
(sometimes a positive result, sometimes a proof that no good approximation exists at all).

## Pros
- Provides a *provable* worst-case guarantee, unlike pure heuristics (`algorithm-design/11`)
  which offer no formal bound at all — valuable when correctness-adjacent guarantees
  matter (e.g. resource allocation with contractual SLAs).
- The LP-relaxation technique is broadly reusable across many different NP-hard
  optimization problems, not just vertex cover — a genuinely general-purpose tool for
  constructing both the bound and, via rounding, the algorithm itself.
- Approximation ratios let you *compare* the intrinsic difficulty of different NP-hard
  problems (constant-factor vs. logarithmic vs. inapproximable), a finer-grained picture
  than "both are NP-hard."

## Cons
- Finding the right lower/upper bound (matching argument, LP relaxation, or another
  structural fact) is itself a creative, problem-specific task with no fully mechanical
  procedure — unlike, say, applying the Master theorem (`algorithm-design/02`).
- A provably good worst-case ratio says nothing about *typical-case* performance — an
  algorithm with a weak worst-case bound (or even no bound) can still perform excellently
  on real-world instance distributions, so the approximation ratio alone shouldn't be the
  only selection criterion.
- Some NP-hard problems provably admit no bounded-factor approximation at all (general
  TSP) — approximation algorithms are not a universal fallback for every NP-hard problem.

## Alternatives
- **Local search / heuristics** (`algorithm-design/11`) — no provable worst-case bound but
  often excellent typical-case performance, and applicable even to problems (like general
  TSP) where no bounded approximation exists at all.
- **Exact exponential-time algorithms** — for genuinely small instances, or where the
  problem structure permits fixed-parameter tractable algorithms, exact solutions may be
  feasible despite NP-hardness in general.
- **Restricting to a tractable special case** (`algorithm-design/12`) — sometimes the real
  instances you face have exploitable structure (e.g. metric TSP's triangle inequality)
  making an entirely different, better-approximable problem the actual one you need to
  solve.

## When to use it
Reach for an approximation algorithm once a problem is confirmed NP-hard
(`algorithm-design/09`) and a provable worst-case quality guarantee is valuable (contractual
guarantees, safety-critical resource allocation, or simply wanting a principled fallback
rather than an unverified heuristic) — check the literature for the problem's known
approximability class first, since results vary enormously (constant factor, logarithmic,
or provably inapproximable).

## When NOT to use it
Don't assume every NP-hard problem has a good (or any) polynomial-time approximation —
verify the specific problem's approximability results before investing effort (general TSP
is a stark counterexample). Don't rely solely on worst-case approximation ratio when
typical-case performance on your actual instance distribution is what matters and a
well-tuned heuristic (`algorithm-design/11`) would serve just as well with less
implementation complexity.

## Key takeaways / mental model
Approximation algorithms trade exactness for a provable worst-case bound, and every proof
follows the same shape: find an efficiently-computable bound (structural, like a matching,
or via LP relaxation) that's provably no better than the true optimum, then show your
algorithm's output is within a factor alpha of that bound. Different NP-hard problems have
wildly different achievable approximation quality (constant factor, logarithmic, or
provably none at all) — this is itself problem-specific information you have to look up or
derive, not something "NP-hard" alone tells you.

## Self-check questions
1. Walk through the vertex cover 2-approximation proof: why does the size of a matching
   provide a valid lower bound on the true minimum vertex cover size?
2. Explain, at a high level, why relaxing an integer linear program's {0,1} constraints to
   [0,1] always gives a bound at least as good as the true integer optimum.
3. Why does set cover's ln(n) approximation ratio not contradict vertex cover's constant
   factor-2 ratio — what does this difference tell you about the intrinsic structure of
   the two problems?
4. A colleague says "TSP is NP-hard, so we should just use the same 2-approximation
   technique as vertex cover." What's wrong with this reasoning, and what additional
   assumption (triangle inequality) would make an approximation guarantee possible for
   TSP specifically?

## References
- Algorithm Design (Jon Kleinberg, Eva Tardos), Chapter 11: "Approximation Algorithms."
