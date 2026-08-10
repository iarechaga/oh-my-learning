---
id: clrs/11
subject: clrs
title: Dynamic programming fundamentals
slug: dynamic-programming-fundamentals
status: drafted
mastery:
seniority: mid
source: Introduction to Algorithms (CLRS), Chapter 15
prerequisites: [clrs/03]
created: 2026-08-10
updated: 2026-08-10
---

# Dynamic programming fundamentals

## TL;DR
Dynamic programming (DP) solves problems with **overlapping subproblems** and **optimal
substructure** by solving each distinct subproblem exactly once and reusing the result,
instead of recomputing it every time it's needed (which is what naive recursive
divide-and-conquer would do, often blowing up to exponential time). The two mechanisms
for reuse are **memoization** (top-down recursion with a cache) and **tabulation**
(bottom-up iteration filling a table), and they compute the same answer via the same
subproblem structure.

## The idea
`clrs/03` covers divide and conquer for problems whose subproblems are *independent* — no
subproblem is ever needed by more than one parent, so solving each recursively, once,
is fine. Many important problems don't have that property: the same subproblem is needed
by many different parent calls. A naive recursive solution re-solves that shared
subproblem from scratch every single time it's requested, and if the recursion tree
branches enough, the *same* subproblem can be recomputed exponentially many times — the
canonical example is naive recursive Fibonacci, which recomputes fib(n-2) twice, fib(n-3)
three times, and so on, giving Theta(phi^n) exponential time for a problem with only n
distinct subproblems. Dynamic programming's entire contribution is: **notice that there
are only a polynomial number of distinct subproblems, solve each exactly once, and look
up the answer instead of recomputing it** whenever it's needed again.

## How it works

### The two required properties
1. **Optimal substructure** — an optimal solution to the problem can be constructed from
   optimal solutions to its subproblems. (This property is also needed for greedy
   algorithms and divide-and-conquer, `clrs/12`, `clrs/03` — it's necessary but not
   sufficient for DP specifically.)
2. **Overlapping subproblems** — the recursive solution revisits the *same* subproblems
   repeatedly, rather than always generating fresh ones (this is the property that
   distinguishes DP from plain divide-and-conquer, and is what makes caching worthwhile).

If a problem has optimal substructure but *not* overlapping subproblems (like mergesort),
plain divide-and-conquer is already efficient and DP's caching buys nothing. If it has
overlapping subproblems but *not* optimal substructure, DP doesn't apply at all — no
amount of caching fixes a problem where the greedy/local optimum doesn't combine into a
global optimum.

### Worked example 1: Fibonacci, minimal but maximally clear
Naive recursion: `fib(n) = fib(n-1) + fib(n-2)`. This has overlapping subproblems
(fib(n-2) is computed once as part of fib(n-1)'s call and again directly) and trivial
optimal substructure. Naive recursive time: Theta(phi^n) (exponential — the recursion
tree has exponentially many nodes, most of them recomputing values already computed
elsewhere in the tree).

**Memoized version (top-down):** same recursive structure, but before computing fib(n),
check a cache; if present, return the cached value; otherwise compute and store it. Since
there are only n+1 distinct subproblems (fib(0) through fib(n)), and each is computed
exactly once (Theta(1) work per subproblem beyond the two lookups), total time is
Theta(n) — from exponential to linear, purely by eliminating redundant recomputation.

**Tabulated version (bottom-up):** build an array `table[0..n]`, fill `table[0]=0,
table[1]=1`, then iterate i from 2 to n setting `table[i] = table[i-1] + table[i-2]`.
Same Theta(n) time, no recursion at all, and — for this specific problem — can even be
reduced to O(1) extra space by only keeping the last two values, since nothing older is
ever needed again.

### Worked example 2: the rod-cutting problem
Given a rod of length n and a price table `price[1..n]` (the price you can sell a piece
of each length for), find the maximum revenue obtainable by cutting the rod into pieces
and selling them. **Optimal substructure:** an optimal cutting of a rod of length n
either sells it whole (revenue price[n]) or cuts off a first piece of length i (for some
1 <= i < n) and optimally cuts the remaining n-i, so
`revenue(n) = max over i of (price[i] + revenue(n-i))`. **Overlapping subproblems:**
`revenue(n-i)` for various splits at various levels of recursion computes the same
smaller-length subproblems repeatedly (e.g. revenue(2) is needed by revenue(5)'s
i=3 split, revenue(4)'s i=2 split, revenue(6)'s i=4 split, and more) — naive recursion
here is Theta(2^n). Tabulating bottom-up (compute revenue(0), then revenue(1) using
revenue(0), then revenue(2) using revenue(0) and revenue(1), and so on up to revenue(n))
gives Theta(n^2) — each of the n subproblems takes O(n) work to consider all its splits.

### Worked example 3: matrix-chain multiplication
Given a chain of matrices to multiply, the total scalar-multiplication cost depends
heavily on the parenthesization (multiplication is associative but the intermediate
matrix sizes produced by different groupings differ enormously). Let `m[i][j]` be the
minimum cost to multiply matrices i through j. **Optimal substructure:**
`m[i][j] = min over k (i <= k < j) of m[i][k] + m[k+1][j] + cost of multiplying the two
resulting matrices`. **Overlapping subproblems:** `m[i][k]` for a given (i,k) pair is
needed by every j > k that considers splitting at that k — a genuinely two-dimensional
overlap pattern. Tabulating by increasing chain length (fill in `m[i][j]` for all
length-1 chains, then length-2, then length-3, ...) gives Theta(n^3) — a case where the
subproblem space itself is two-dimensional (indexed by the pair i,j, giving Theta(n^2)
distinct subproblems), each taking O(n) work to consider all split points k.

### Memoization vs. tabulation: when each is preferable
**Memoization (top-down)** only computes the subproblems actually needed for the
specific input — valuable when the full subproblem space is large but a particular input
only touches a sparse subset of it. It carries recursion overhead (function call stack)
and requires a hashable/indexable key scheme for the cache. **Tabulation (bottom-up)**
computes every subproblem in a fixed dependency order (smallest first), avoiding
recursion overhead entirely and often enabling space optimization (as in the Fibonacci
example, keeping only the last few rows/values when older ones are provably never needed
again) — but it requires the full subproblem space up to the input size to actually be
filled, even if some of it goes unused for a particular input.

### Reconstructing the actual solution, not just its value
The DP table gives the *optimal value* (e.g. the maximum revenue, the minimum cost), but
often you also need the *actual solution* (which cuts, which parenthesization). This
requires tracking, alongside each table entry, which choice achieved that optimal value
(e.g. a parallel `choice[i][j]` table storing which split point k was optimal), then
walking back through those choices after the table is filled — a step that's easy to
forget when first learning DP, since the recurrence alone only computes values.

## Pros
- Converts exponential-time naive recursive solutions into polynomial time by eliminating
  redundant recomputation — often the difference between "intractable" and "fast" for the
  exact same recursive structure.
- The recurrence relation (once correctly identified) mechanically determines both the
  subproblem space size and the per-subproblem work, giving a clean and predictable way
  to derive the algorithm's total complexity.
- Generalizes across an enormous range of problems (sequence alignment, scheduling,
  resource allocation, string problems) once you can spot the optimal-substructure
  recurrence — a genuinely reusable design skill.

## Cons
- Identifying the correct subproblem definition and recurrence is often the hardest part
  and doesn't have a fully mechanical process — this is a skill built through practice on
  many problems, not a checklist.
- Space cost can be significant (a two-dimensional table for matrix-chain multiplication
  is Theta(n^2) space) unless a space-optimization pass (like Fibonacci's O(1) reduction)
  is applied, which isn't always possible depending on the dependency structure.
- Easy to correctly compute the optimal *value* while forgetting to also track the
  choices needed to reconstruct the actual optimal *solution*.

## Alternatives
- **Plain divide and conquer** (`clrs/03`) — the right choice when subproblems don't
  actually overlap; adding memoization to a divide-and-conquer algorithm whose
  subproblems are already disjoint adds overhead for no benefit.
- **Greedy algorithms** (`clrs/12`) — for problems where optimal substructure holds
  *and* a provably-correct local, never-revisited choice at each step reaches the global
  optimum, greedy is simpler and often faster (no need to consider all subproblem
  choices), but requires proving the greedy-choice property holds, which not all
  DP-solvable problems satisfy.
- **Branch and bound / exhaustive search with pruning** — for problems lacking optimal
  substructure entirely (so DP doesn't apply), where an exact answer is still required.

## When to use it
Use dynamic programming when a problem has optimal substructure (the whole is built from
optimal solutions to parts) and overlapping subproblems (the same subproblem recurs
across different branches of the natural recursive solution) — verify both properties
explicitly before committing to a DP formulation.

## When NOT to use it
Don't reach for DP when subproblems don't actually overlap (plain divide and conquer is
simpler and equally efficient) or when a provably-correct greedy strategy exists (greedy
is simpler and often faster). Don't apply DP mechanically without first confirming
optimal substructure actually holds — some problems that look DP-shaped (e.g. certain
scheduling variants) don't actually decompose this way, and a DP formulation over them
would silently produce a wrong answer.

## Key takeaways / mental model
DP is "smart recursion that remembers": identify the recurrence (optimal substructure),
confirm subproblems overlap (otherwise plain recursion is already fine), then either
cache top-down (memoization) or fill bottom-up (tabulation) so each distinct subproblem
is solved exactly once. The complexity is (number of distinct subproblems) x (work per
subproblem) — both terms come directly from the recurrence you wrote down.

## Self-check questions
1. For naive recursive Fibonacci, sketch the recursion tree for fib(5) and count how
   many times fib(2) is computed. Explain how memoization eliminates this redundancy.
2. For the rod-cutting problem, explain why the naive recursive solution is Theta(2^n)
   but the tabulated solution is Theta(n^2) — where exactly does the exponential blowup
   come from in the naive version?
3. Give an example of a problem with optimal substructure but *without* overlapping
   subproblems, and explain why applying DP's memoization to it would add unnecessary
   overhead rather than provide a benefit.
4. Why does the matrix-chain multiplication DP need a two-dimensional table (indexed by
   pairs i,j) rather than a one-dimensional one, and how does that affect the total
   number of distinct subproblems?

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 15: "Dynamic
  Programming."
