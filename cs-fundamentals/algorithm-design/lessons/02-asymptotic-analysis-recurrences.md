---
id: algorithm-design/02
subject: algorithm-design
title: Asymptotic analysis and recurrence solving
slug: asymptotic-analysis-recurrences
status: drafted
mastery:
seniority: mid
source: Algorithm Design (Kleinberg & Tardos), Chapter 2
prerequisites: [algorithm-design/01, clrs/01, clrs/02]
created: 2026-08-10
updated: 2026-08-10
---

# Asymptotic analysis and recurrence solving

## TL;DR
Asymptotic analysis abstracts away machine-specific constants to classify how an
algorithm's running time scales with input size; recurrences describe the running time of
divide-and-conquer algorithms in terms of themselves on smaller inputs, and solving them
(via the recursion tree method or the Master theorem) turns a recursive definition into a
closed-form bound. This lesson pairs with `algorithm-design/03`: the recurrence is how you
*compute* the running time of any divide-and-conquer algorithm you design there.

## The idea
Two different machines, compilers, or implementations of the same algorithm will have
different constant-factor running times, but their *growth rate* as input size n grows is
an implementation-independent property of the algorithm itself. Asymptotic notation
(O, Omega, Theta) captures exactly that growth rate, discarding constants and lower-order
terms so that algorithms can be compared meaningfully across hardware and implementation
details. This book leans on the same notation as CLRS (`clrs/01`) but treats it more as a
working tool inside proofs of running time than as an object of study in itself — you will
use it constantly in later chapters without re-deriving it each time.

Recurrences exist because a divide-and-conquer algorithm's cost is naturally
self-referential: solving a size-n problem costs "some work to split/combine" plus the
cost of solving smaller subproblems, and that smaller-subproblem cost is again the same
function applied to a smaller input. A recurrence *is* the running time; solving it is
the only way to get a usable bound like O(n log n) out of a recursive definition.

## How it works

### Notation recap (see clrs/01 for full depth)
- **O(g(n))**: an asymptotic *upper* bound — the algorithm runs no slower than g(n), up to
  constants, for large n.
- **Omega(g(n))**: an asymptotic *lower* bound.
- **Theta(g(n))**: both — a tight bound.
This book's chapter 2 uses these mainly to state and compare running times of algorithms
built in later chapters (e.g. "this greedy runs in O(n log n)"), and to give a working
definition without the full CLRS formalism — treat `clrs/01` as the rigorous reference if
the limit-based definitions are unfamiliar.

### Where recurrences come from
A divide-and-conquer algorithm that splits a size-n input into `a` subproblems of size
`n/b` each, doing `f(n)` work to split and recombine, has running time:

    T(n) = a*T(n/b) + f(n),   T(1) = O(1)  (base case)

Different (a, b, f(n)) combinations describe different algorithms: mergesort is
a=2, b=2, f(n)=Theta(n) (linear merge step); binary search is a=1, b=2, f(n)=O(1).

### Method 1: the recursion tree
Draw the recursion as a tree: the root does f(n) work and has `a` children, each doing
f(n/b) work, each of *those* has `a` children doing f(n/b^2) work, and so on until the
base case. Sum the work **per level**, then sum across all levels (there are log_b(n)
levels, since the input shrinks by a factor of b each level until it reaches 1).

**Worked example: mergesort.** T(n) = 2T(n/2) + Theta(n).
- Level 0 (root): 1 node, work = c*n.
- Level 1: 2 nodes, each size n/2, work = 2 * c*(n/2) = c*n.
- Level 2: 4 nodes, each size n/4, work = 4 * c*(n/4) = c*n.
- ... every level does exactly c*n total work.
- Number of levels: log2(n) (halving n until it reaches 1).
- Total: c*n * log2(n) = Theta(n log n).

**Worked example: a degenerate split.** T(n) = T(n-1) + O(1) (each call only shrinks the
problem by 1, like naive unmemoized recursion or a poorly balanced split). The recursion
tree is a single chain of n nodes, each doing O(1) work: total Theta(n) calls stacked to
depth n — this is what happens when "divide" doesn't actually shrink geometrically, a
degenerate case worth recognizing as a design smell in your own divide-and-conquer
algorithms (see `algorithm-design/03`).

### Method 2: the Master theorem
For T(n) = a*T(n/b) + f(n) with a >= 1, b > 1, compare f(n) against n^(log_b(a)):

1. If f(n) = O(n^(log_b(a) - eps)) for some eps > 0 (f grows *slower*), then
   T(n) = Theta(n^(log_b(a))) — the leaves dominate.
2. If f(n) = Theta(n^(log_b(a))) (f grows at the *same* rate), then
   T(n) = Theta(n^(log_b(a)) * log n) — every level contributes equally (mergesort's case).
3. If f(n) = Omega(n^(log_b(a) + eps)) for some eps > 0 (f grows *faster*), **and** the
   regularity condition a*f(n/b) <= c*f(n) holds for some c < 1 and large n, then
   T(n) = Theta(f(n)) — the root dominates.

**Worked example: binary search.** T(n) = T(n/2) + O(1). a=1, b=2, log_b(a) = log2(1) = 0,
so n^(log_b(a)) = n^0 = 1. f(n) = O(1) = Theta(n^0) -> case 2 applies:
T(n) = Theta(1 * log n) = Theta(log n).

**Worked example: a Strassen-style recurrence.** T(n) = 7T(n/2) + Theta(n^2) (matrix
multiplication via Strassen's algorithm). log_b(a) = log2(7) ~ 2.807. f(n) = n^2 grows
*slower* than n^2.807 -> case 1: T(n) = Theta(n^log2(7)) ~ Theta(n^2.807) — strictly better
than the naive Theta(n^3) matrix multiplication, and this is exactly why the Master
theorem matters practically: it lets you *compare* two divide-and-conquer strategies for
the same problem by comparing their recurrences directly, without redoing a full recursion
tree each time.

### When the Master theorem doesn't apply
The Master theorem only covers recurrences of the exact form a*T(n/b) + f(n) with
polynomial-ish f(n) satisfying the regularity condition; it does not directly handle
T(n) = 2T(n/2) + n/log(n) (case 3's polynomial-growth requirement fails even though f
grows faster than n^1 in a loose sense) or unequal-size splits like
T(n) = T(n/3) + T(2n/3) + O(n). These need the recursion tree method directly (unequal
splits still have bounded depth O(log n) and bounded per-level work, so the same
level-summing technique works, just with asymmetric branching) or more advanced techniques
(the Akra-Bazzi method) beyond this lesson's scope.

## Pros
- Gives a mechanical, checkable procedure (Master theorem) for the overwhelming majority
  of divide-and-conquer recurrences encountered in practice.
- The recursion tree method always works (even when the Master theorem's preconditions
  fail) and builds the intuition for *why* a given closed form is correct, not just a
  formula to memorize.
- Comparing recurrences directly (n^2 vs n^2.807 vs n^3) lets you evaluate algorithm
  design choices analytically before ever implementing or benchmarking them.

## Cons
- The Master theorem's preconditions (polynomial f(n), regularity condition, equal-size
  subproblems) are easy to misapply if not checked carefully — plugging into the wrong
  case silently gives a wrong bound.
- Asymptotic bounds hide constants; an algorithm with a better asymptotic bound can still
  lose to a worse-bound algorithm on realistic input sizes if its constant factor is much
  larger (Strassen's algorithm is a real example: rarely used in practice below very large
  matrix sizes because of a larger constant and worse numerical stability).
- Recurrences model *comparison/arithmetic-operation* counts cleanly but can obscure
  real-world costs like cache behavior, memory allocation, or I/O that don't fit neatly
  into the recurrence's cost model.

## Alternatives
- **Direct recursion-tree summation without the Master theorem** — always applicable,
  slower to execute by hand, necessary when the Master theorem's form doesn't match.
- **Substitution method (guess and verify by induction)** — guess a closed form, then
  prove it by strong induction; more work per recurrence but handles cases (like unusual
  boundary conditions) the other two methods handle awkwardly.
- **Amortized analysis** (see `clrs/17`) — for algorithms whose *sequence* of operations
  matters more than any single call's recursive structure (e.g. dynamic array growth),
  recurrences aren't the right tool at all.

## When to use it
Use recurrence solving every time you design or evaluate a divide-and-conquer algorithm
(`algorithm-design/03`) and need its running time — this is the mechanical last step after
identifying the split factor, subproblem count, and combine cost.

## When NOT to use it
Don't force a recurrence-based analysis onto algorithms that aren't naturally recursive
(most greedy or straight-line iterative algorithms are more directly analyzed by counting
loop iterations). Don't trust a Master theorem application without checking the
regularity condition in case 3 — the polynomial-growth gap between f(n) and n^(log_b(a))
must be a genuine polynomial factor (n^eps), not just "eventually bigger."

## Key takeaways / mental model
A recurrence is the running time of a recursive algorithm, expressed as a function of
itself on smaller inputs; solving it converts that self-referential definition into a
usable closed form. The recursion tree method always works: sum the work per level, sum
across log_b(n) levels. The Master theorem is a shortcut for the common a*T(n/b)+f(n) form,
determined entirely by comparing f(n) to n^(log_b(a)) — whichever grows faster
(leaf-heavy, balanced, or root-heavy) dominates the total.

## Self-check questions
1. Derive, using the recursion tree method (not the Master theorem), the closed form for
   T(n) = 4T(n/2) + Theta(n). Which term dominates: the root's work or the leaves' total
   work?
2. A divide-and-conquer algorithm splits into 3 subproblems of size n/2 each, doing O(n)
   work to combine. Which Master theorem case applies, and what is T(n)?
3. Why does T(n) = T(n-1) + O(1) produce Theta(n) rather than something logarithmic —
   what's structurally different about this recurrence compared to T(n) = T(n/2) + O(1)?
4. Strassen's algorithm has a better asymptotic bound than naive matrix multiplication but
   is rarely the default choice in practice. What does this tell you about the limits of
   asymptotic analysis as a sole basis for algorithm selection?

## References
- Algorithm Design (Jon Kleinberg, Eva Tardos), Chapter 2: "Basics of Algorithm Analysis."
