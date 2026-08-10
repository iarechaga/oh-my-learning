---
id: clrs/03
subject: clrs
title: Divide and conquer as a design paradigm
slug: divide-and-conquer
status: drafted
mastery:
seniority: mid
source: Introduction to Algorithms (CLRS), Chapter 4
prerequisites: [clrs/02]
created: 2026-08-10
updated: 2026-08-10
---

# Divide and conquer as a design paradigm

## TL;DR
Divide and conquer solves a problem by splitting it into smaller subproblems of the same
kind, solving each recursively, then combining the subsolutions into a solution for the
original problem. It is a general design strategy, not a single algorithm, and its
efficiency is entirely determined by the recurrence it induces (`clrs/02`) — specifically
by the balance between how much the problem shrinks and how expensive the combine step
is.

## The idea
Many problems have a self-similar structure: a solution to the whole can be assembled
from solutions to smaller pieces of the same problem. If you can (a) split the problem
into smaller instances cheaply, (b) solve each piece independently (often recursively,
using the exact same algorithm), and (c) merge the pieces' answers into a final answer,
you have a divide-and-conquer algorithm. The technique matters because it turns what
might look like an unavoidably brute-force problem into something whose cost is governed
by a recurrence — and recurrences of the standard shape are frequently far faster than
brute force (Theta(n log n) instead of Theta(n^2), for example).

## How it works

### The three steps, explicitly
- **Divide** the problem into a number of smaller subproblems of the same kind (usually
  by splitting the input, e.g. an array in half).
- **Conquer** the subproblems by solving them recursively; if a subproblem is small
  enough, solve it directly (the base case).
- **Combine** the subproblem solutions into a solution for the original problem.

The "combine" step's cost, f(n), together with the number of subproblems (a) and their
relative size (n/b), together determine the recurrence T(n) = a*T(n/b) + f(n) that
`clrs/02` teaches you to solve.

### Worked example 1: mergesort (already introduced in clrs/02)
Divide: split the array into two halves (Theta(1) — just compute the midpoint index; no
copying needed if done by index range). Conquer: recursively sort each half. Combine:
merge the two sorted halves into one sorted array (Theta(n), since it visits every
element exactly once). Recurrence: T(n) = 2T(n/2) + Theta(n) = Theta(n log n) by the
Master method.

### Worked example 2: binary search
Divide: compare the target to the middle element (Theta(1)). Conquer: recurse into
*only one* of the two halves (not both — this is the key difference from mergesort:
the branching factor a=1, not 2). Combine: trivial, Theta(1) (the answer from the single
recursive call *is* the answer). Recurrence: T(n) = T(n/2) + Theta(1) = Theta(log n).

Comparing these two examples side by side shows exactly how the recurrence's parameters
(a = number of subproblems recursed into, b = shrink factor, f(n) = combine cost)
translate design choices into asymptotic outcomes: doubling the branching factor from 1
to 2 (searching both halves instead of one) while keeping everything else the same is
exactly the difference between Theta(log n) and Theta(n) — a large practical difference
that traces directly to one design decision.

### Worked example 3: the maximum-subarray problem
Given an array of numbers (possibly negative), find the contiguous subarray with the
largest sum. Divide: split the array at the midpoint into a left half and a right half.
Conquer: the best subarray lies entirely in the left half, entirely in the right half, or
crosses the midpoint — recursively solve the first two cases. Combine: for the
"crossing" case, scan outward from the midpoint in both directions to find the best
left-extension and best right-extension (Theta(n) work, since this scan touches every
element once), then take the max of all three cases. Recurrence:
T(n) = 2T(n/2) + Theta(n) = Theta(n log n) by the Master method — structurally identical
to mergesort's recurrence, even though the problem is completely different. This
illustrates a broader point: **once you've expressed a problem's structure as a
divide-and-conquer recurrence, the Master method (or recursion tree) gives you the
answer regardless of the problem's domain.**

### Worked example 4: Strassen's algorithm for matrix multiplication
The naive algorithm for multiplying two n x n matrices does 8 recursive multiplications
of (n/2) x (n/2) submatrices plus Theta(n^2) combine work: T(n) = 8T(n/2) + Theta(n^2),
which solves (Master Case 1) to Theta(n^3) — no better than the straightforward triple-
loop algorithm. Strassen's insight was a clever algebraic trick that computes the same
result using only **7** recursive multiplications instead of 8 (at the cost of more
addition/subtraction work, still Theta(n^2)): T(n) = 7T(n/2) + Theta(n^2). Because
log2(7) ≈ 2.807 < 3, this solves (Master Case 1 again) to Theta(n^2.807) — asymptotically
faster than the naive Theta(n^3), purely by reducing the branching factor a from 8 to 7.
This is the clearest possible illustration of *why* the recurrence's parameters matter:
one fewer recursive call, chosen cleverly, changes the exponent itself.

## Pros
- Frequently turns a naive Theta(n^2) (or worse) problem into Theta(n log n) or better,
  by trading brute-force enumeration for recursive structure.
- Subproblems are independent, which makes divide-and-conquer algorithms naturally
  parallelizable (the two recursive calls in mergesort can run concurrently).
- The recurrence framework (`clrs/02`) gives a mechanical way to evaluate a candidate
  design's asymptotic cost before fully implementing it — you can compare design options
  by their induced recurrences alone.

## Cons
- The combine step's cost is the whole game — a divide-and-conquer approach with an
  expensive combine step (e.g. Theta(n^2) combine work) can be no better, or even worse,
  than a simpler direct algorithm.
- Recursive overhead (function call stack, repeated small-array handling) has real
  constant-factor cost; many production sort implementations switch to insertion sort
  below a small size threshold specifically to avoid this overhead — divide-and-conquer
  is a strategy for the asymptotic regime, not automatically for every n.
- Not every problem decomposes cleanly into independent subproblems of the same kind —
  problems with heavy interdependency between subproblems (many dynamic-programming
  problems, `clrs/11`) need a fundamentally different technique (overlapping subproblems
  handled via memoization/tabulation, not independent recursive solves).

## Alternatives
- **Dynamic programming** (`clrs/11`) — for problems whose subproblems *overlap* (the
  same subproblem is needed by multiple parents), solving each subproblem independently
  via divide-and-conquer redoes the same work exponentially many times; DP instead solves
  each distinct subproblem once and reuses the result.
- **Greedy algorithms** (`clrs/12`) — for problems where a sequence of locally optimal
  choices, each made once and never revisited, provably reaches a globally optimal
  answer, avoiding the need to explore multiple subproblem branches at all.
- **Brute force / direct iteration** — for small inputs or provably non-decomposable
  problems, the simplicity and low constant factor of a direct algorithm can beat a
  divide-and-conquer approach's overhead.

## When to use it
Reach for divide and conquer when a problem naturally splits into independent
subproblems of the same kind with a combine step that's cheaper than solving the whole
problem directly (typically linear or near-linear combine cost relative to the
subproblem's shrinking size).

## When NOT to use it
Don't reach for divide and conquer when subproblems overlap significantly (redoing the
same subproblem's work repeatedly wastes exponential time — that's the signal to switch
to dynamic programming instead), or when the combine step would be as expensive as
solving the problem directly (in which case the recursive structure buys nothing).

## Key takeaways / mental model
Divide and conquer is: split into independent same-kind subproblems, solve each
recursively, combine. Its cost is entirely captured by the recurrence it induces
(a subproblems of size n/b, plus f(n) combine cost) — evaluate a design by writing down
that recurrence and solving it (`clrs/02`) before committing to an implementation.

## Self-check questions
1. Write the recurrence for the maximum-subarray algorithm above and solve it via the
   Master method. Why does the "crossing" combine step need to be Theta(n), not more?
2. Explain, using Strassen's algorithm, exactly how reducing the branching factor from 8
   to 7 changes the final asymptotic complexity, and why this wouldn't have worked if the
   combine (addition) step had also grown to Theta(n^3).
3. Give an example of a problem where divide and conquer's "combine" step would end up
   costing as much as solving the whole problem directly — what does that tell you about
   whether divide and conquer is the right paradigm there?
4. Why are divide-and-conquer algorithms naturally easier to parallelize than dynamic-
   programming algorithms with heavily overlapping subproblems?

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 4:
  "Divide-and-Conquer," including 4.1 (maximum subarray) and 4.2 (Strassen's algorithm).
