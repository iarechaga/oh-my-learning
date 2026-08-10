---
id: clrs/02
subject: clrs
title: Recurrences and the Master method
slug: recurrences-master-method
status: drafted
mastery:
seniority: mid
source: Introduction to Algorithms (CLRS), Chapter 4
prerequisites: [clrs/01]
created: 2026-08-10
updated: 2026-08-10
---

# Recurrences and the Master method

## TL;DR
A recursive algorithm's running time is naturally expressed as a recurrence — a function
defined in terms of itself on smaller inputs. Solving that recurrence (finding a closed-form
asymptotic bound) tells you the algorithm's true complexity. The Master method is a
plug-in formula that solves the specific, extremely common recurrence shape
T(n) = a*T(n/b) + f(n) by comparing how fast the recursive work grows against the
non-recursive ("combine") work at each level.

## The idea
`clrs/01` gave you the vocabulary (O, Omega, Theta) to describe growth, but for
recursive algorithms you first need to *derive* the growth rate before you can classify
it, and recursive algorithms don't hand you a closed-form running time directly — they
hand you an equation like T(n) = 2*T(n/2) + n (mergesort's recurrence: two subproblems of
half the size, plus linear work to merge). Solving means turning that self-referential
equation into a plain function of n, like Theta(n log n), that you can actually reason
about and compare to other algorithms.

## How it works

### Where a recurrence comes from
Take mergesort: to sort n elements, split into two halves (Theta(1) work), recursively
sort each half (2 subproblems of size n/2), then merge the two sorted halves (Theta(n)
work, since merging requires touching every element once). This directly translates to:
T(n) = 2*T(n/2) + Theta(n), with a base case T(1) = Theta(1). This equation *is* the
algorithm's cost model — solving it is the remaining step.

### Three ways to solve a recurrence
1. **The recursion tree method** — draw the recursion as a tree, sum the work done at
   each level, then sum across all levels. Intuitive and works for almost anything, but
   requires care to get right (this lesson works one fully).
2. **The substitution method** — guess the closed form, then prove it correct by
   induction (substituting the guess into the recurrence and checking it holds). Powerful
   for irregular recurrences the Master method can't handle, but requires a good initial
   guess.
3. **The Master method** — a direct formula for recurrences of the exact shape
   T(n) = a*T(n/b) + f(n), where a >= 1 and b > 1 are constants and f(n) is
   asymptotically positive. Fast when it applies, but it only applies to this one shape.

### Recursion tree, worked in full: T(n) = 2T(n/2) + n
- **Level 0:** 1 problem of size n, doing n units of non-recursive work. Total: n.
- **Level 1:** 2 problems of size n/2, each doing n/2 units of work. Total: 2*(n/2) = n.
- **Level 2:** 4 problems of size n/4, each doing n/4 units of work. Total: 4*(n/4) = n.
- **Level i:** 2^i problems of size n/2^i, each doing n/2^i units of work. Total: n.

Every level contributes exactly n units of work — the "problem gets smaller" and "problem
count grows" effects exactly cancel. The tree has depth log2(n) (since the subproblem size
shrinks from n to 1 by repeated halving), so total work = n (per level) * log2(n) (number
of levels) = Theta(n log n). This is exactly mergesort's known complexity, derived from
first principles rather than memorized.

### The Master method, stated
For T(n) = a*T(n/b) + f(n), compare f(n) against n^(log_b(a)) — this quantity,
n^(log_b(a)), is the cost of the leaves if the recursive work dominated evenly at every
level (it's often called the "watershed function").

- **Case 1 — recursive work dominates:** if f(n) = O(n^(log_b(a) - eps)) for some
  constant eps > 0 (f grows polynomially slower), then T(n) = Theta(n^(log_b(a))).
- **Case 2 — balanced:** if f(n) = Theta(n^(log_b(a)) * log^k(n)) for some k >= 0
  (commonly just k=0, i.e. f(n) = Theta(n^(log_b(a)))), then
  T(n) = Theta(n^(log_b(a)) * log^(k+1)(n)).
- **Case 3 — combine work dominates:** if f(n) = Omega(n^(log_b(a) + eps)) for some
  constant eps > 0 (f grows polynomially faster), *and* the regularity condition
  a*f(n/b) <= c*f(n) holds for some c < 1 and large n, then T(n) = Theta(f(n)).

Intuition: the recursion tree has work concentrated either at the leaves (case 1, many
small subproblems dominate), spread evenly across all log(n) levels (case 2, mergesort's
situation), or concentrated at the root (case 3, the combine step itself dominates).

### Worked examples applying the Master method
1. **Mergesort:** T(n) = 2T(n/2) + n. Here a=2, b=2, so n^(log_b(a)) = n^(log2(2)) = n^1
   = n. Compare f(n) = n against n^1 = n: they match exactly (k=0), so **Case 2** applies:
   T(n) = Theta(n^1 * log^1(n)) = Theta(n log n).
2. **Binary search:** T(n) = T(n/2) + Theta(1). Here a=1, b=2, so n^(log_b(a)) =
   n^(log2(1)) = n^0 = 1. Compare f(n) = Theta(1) against n^0 = 1: they match (k=0), so
   **Case 2** applies: T(n) = Theta(1 * log^1(n)) = Theta(log n) — matching the informal
   derivation in `clrs/01`.
3. **A hypothetical T(n) = T(n/2) + n^2:** a=1, b=2, n^(log_b(a)) = n^0 = 1. f(n) = n^2
   grows polynomially faster than n^0 (eps=2 works), and the regularity condition holds
   (a*f(n/b) = 1*(n/2)^2 = n^2/4 <= c*n^2 for c=1/2 < 1), so **Case 3** applies:
   T(n) = Theta(n^2) — the single combine step dominates, and the recursion barely
   matters.
4. **A hypothetical T(n) = 4T(n/2) + n:** a=4, b=2, n^(log_b(a)) = n^(log2(4)) = n^2.
   f(n) = n grows polynomially slower than n^2 (eps=1 works), so **Case 1** applies:
   T(n) = Theta(n^2) — the sheer number of leaf subproblems (4 branching factor against
   only 2x size reduction) dominates.

### When the Master method doesn't apply
The Master method requires the exact shape a*T(n/b) + f(n) with constant a, b. It cannot
solve, for example, T(n) = 2T(n/2) + n/log(n) (the gap between cases isn't polynomial,
just logarithmic — none of the three cases' polynomial-gap conditions hold) or
T(n) = T(n-1) + n (subtractive, not divisional recurrence — quicksort's worst case has
this shape). For these, fall back to the recursion tree or substitution method, or (for
the n/log(n) case) the more general Akra-Bazzi method, which CLRS mentions but doesn't
develop in full.

## Pros
- The Master method turns a class of recurrence-solving problems into a lookup-and-plug
  exercise, fast once you recognize the shape.
- The recursion tree method builds genuine intuition for *why* an algorithm has the
  complexity it does, which transfers to recurrences the Master method can't handle.
- Both connect directly to algorithm design decisions: the branching factor (a), the
  subproblem shrink factor (b), and the per-level combine cost (f(n)) are all things a
  designer chooses, and this framework tells you exactly how each choice affects the
  final complexity.

## Cons
- The Master method's three cases have a real gap between them (polynomially smaller,
  polynomially larger, or exactly matching) — recurrences with only a logarithmic gap
  fall through and need other tools.
- Easy to misapply by fudging which case "roughly" fits without checking the precise
  polynomial-gap or regularity conditions, leading to a wrong bound.
- Doesn't handle recurrences with non-constant a or b, or subtractive recurrences (where
  the subproblem is n-c rather than n/b).

## Alternatives
- **Substitution method (guess-and-prove-by-induction)** — more general, handles
  irregular recurrences, but requires already having a good guess for the answer.
- **Akra-Bazzi method** — a strict generalization of the Master method that handles
  unequal subproblem sizes and a wider range of f(n); more powerful but more mechanically
  involved, and not developed in CLRS itself.
- **Direct recursion-tree summation** — always applicable in principle, but requires
  carefully summing a series (sometimes a geometric series, sometimes not) rather than a
  formula lookup.

## When to use it
Reach for the Master method first whenever a divide-and-conquer recurrence has the form
a*T(n/b) + f(n) with constant a and b — this covers most textbook divide-and-conquer
algorithms (mergesort, many matrix and tree algorithms, Strassen's algorithm). Use the
recursion tree when you want to build or check intuition, or when the recurrence doesn't
fit the Master method's shape.

## When NOT to use it
Don't force the Master method onto a subtractive recurrence like T(n) = T(n-1) + n (this
is Theta(n^2) by direct summation, not solvable by the Master method) or onto a
recurrence with a logarithmic — not polynomial — gap between f(n) and n^(log_b(a)); use
substitution or Akra-Bazzi instead.

## Key takeaways / mental model
A recurrence's complexity depends on a three-way tug-of-war: work concentrated at the
leaves (Case 1: many small subproblems win), work spread evenly across levels (Case 2:
mergesort's situation, add a log factor), or work concentrated at the root (Case 3: the
combine step wins, recursion barely matters). Identify which one wins by comparing f(n)
to n^(log_b(a)).

## Self-check questions
1. Derive, using a recursion tree, the complexity of T(n) = 3T(n/2) + n. Then verify your
   answer using the Master method.
2. For T(n) = T(n/3) + T(2n/3) + n (not a Master-method shape because the two subproblems
   are different sizes), sketch why the recursion tree is *not* perfectly balanced, and
   why the answer is still Theta(n log n) (the shallowest and deepest root-to-leaf paths
   both have length Theta(log n)).
3. Why does binary search's recurrence T(n) = T(n/2) + Theta(1) fall into Master method
   Case 2 rather than Case 1 or 3? What would have to change about the algorithm for it to
   fall into Case 1 instead?
4. Explain in your own words why T(n) = 2T(n/2) + n/log(n) cannot be solved by the Master
   method, even though it looks almost identical to mergesort's recurrence.

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 4: "Divide-and-
  Conquer," especially 4.3-4.6 (substitution, recursion-tree, and Master methods).
