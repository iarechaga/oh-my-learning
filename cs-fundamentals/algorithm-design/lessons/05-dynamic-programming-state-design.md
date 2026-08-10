---
id: algorithm-design/05
subject: algorithm-design
title: "Dynamic programming: optimal substructure and state design"
slug: dynamic-programming-state-design
status: drafted
mastery:
seniority: mid
source: Algorithm Design (Kleinberg & Tardos), Chapter 6
prerequisites: [algorithm-design/03, algorithm-design/04, clrs/11]
created: 2026-08-10
updated: 2026-08-10
---

# Dynamic programming: optimal substructure and state design

## TL;DR
Dynamic programming solves problems with overlapping subproblems and optimal
substructure by memoizing subproblem solutions instead of recomputing them; this book's
distinct emphasis, beyond CLRS's mechanics-first treatment (`clrs/11`), is a repeatable
**design procedure for choosing the state** — the hardest and most creative part of DP,
where most real design difficulty lives, more than the recurrence or table-filling once
the state is right.

## The idea
`clrs/11` teaches the DP mechanics well: optimal substructure, overlapping subproblems,
top-down memoization vs. bottom-up tabulation. What it under-emphasizes, and what this
book foregrounds, is that **the hard, creative step in DP is deciding what a "state"
even is** — before you can write a recurrence, you have to choose a parameterization of
subproblems that (a) is small enough to enumerate efficiently and (b) captures exactly
enough information that a subproblem's optimal solution can be computed from smaller
subproblems' optimal solutions alone, with nothing extra needed. Get the state wrong (too
little information) and the recurrence simply isn't correct — no amount of clever
tabulation fixes a wrong state. Get it right but too large, and the algorithm becomes
impractically slow. This book teaches state design as a first-class skill via a
progression of examples, each adding one dimension of difficulty to the state.

## How it works

### The state-design procedure this book teaches
1. **Start from the naive recursive formulation** — a direct, possibly exponential,
   recursion that's obviously correct (even if slow) by construction, usually by
   considering "make one decision, recurse on the rest."
2. **Identify what varies across recursive calls** — this is the candidate state; the
   parameters that fully determine which subproblem you're in.
3. **Check for overlap**: do multiple root-to-call paths reach the *same* (state) values?
   If not, this is plain divide and conquer (`algorithm-design/03`), not DP — memoization
   wouldn't help because nothing repeats.
4. **Check the state actually captures enough information** for the recurrence to be
   correct — the recurring failure mode: a state that's too small to distinguish
   subproblems whose optimal *continuations* differ, silently producing a wrong answer
   that still looks plausible.
5. **Bound the total number of distinct states** — this determines the algorithm's space
   and (combined with per-state work) time complexity; if the state space is
   exponentially large, DP as formulated doesn't help and a different or reduced state is
   needed.

### Worked example 1: weighted interval scheduling (1D state, warm-up)
n jobs with start, finish, and weight (value); select a maximum-weight subset of
non-overlapping jobs (unlike plain interval scheduling in `clrs/12`, greedy fails here —
counterexample: two low-weight non-overlapping jobs can beat one high-weight job that
overlaps both, so no simple "pick by X" greedy rule works; correctness would require an
exchange argument that provably doesn't exist for arbitrary weights). Sort jobs by finish
time; let p(j) = the largest index i < j such that job i doesn't overlap job j. State:
OPT(j) = best value using only jobs 1..j. Recurrence:

    OPT(j) = max( OPT(j-1),                      # exclude job j
                  w_j + OPT(p(j)) )               # include job j

Base case OPT(0) = 0. This is a 1D state (single integer j) with O(n) states, each O(1)
work given p(j) precomputed (O(n log n) to compute all p(j) via sorting + binary search) —
O(n log n) total.

### Worked example 2: segmented least squares (state requires a *choice*, not just a
prefix)
Given n points, partition them into contiguous segments and fit a line to each segment,
minimizing (sum of squared error across segments) + (a fixed penalty per segment, to
discourage overfitting with too many tiny segments). Naive recursion over "which points
belong to the last segment" alone isn't enough — you need to know the *error contribution*
of every possible candidate last segment, not just "how many points." State: OPT(j) = best
total cost considering only the first j points. Recurrence:

    OPT(j) = min over i < j of ( e(i+1, j) + C + OPT(i) )

where e(i+1, j) is the precomputed least-squares error of fitting points i+1..j as one
segment, and C is the fixed per-segment penalty. This example is chosen specifically to
show a state that still looks 1D (just j) but whose recurrence requires an *inner*
minimization over all possible previous segment boundaries i — a step easy to get wrong by
under-designing the state (e.g. forgetting to precompute e(i,j) for all pairs, or
conflating "the state" with "the transition," which are different design decisions).

### Worked example 3: knapsack, where the state must include a resource dimension
0/1 knapsack (`clrs/11` covers this too): items with weights and values, capacity W,
choose a subset maximizing value without exceeding W. Naive attempt at a 1D state
OPT(i) = "best value using items 1..i" is **provably insufficient** — it can't express
"how much capacity is left," and different subsets of items 1..i that achieve the same
value can leave very different remaining capacity, which matters for what can still be
added. The correct state must add a second dimension: OPT(i, w) = best value using items
1..i with capacity exactly w available. Recurrence:

    OPT(i, w) = max( OPT(i-1, w),                       # exclude item i
                      v_i + OPT(i-1, w - w_i) )          # include item i, if w_i <= w

This is a 2D state (i, w), with O(n*W) total states — deliberately chosen by the book to
illustrate that the state dimensionality must match the problem's actual dependencies; the
"first attempt" 1D state is a canonical illustration of *why* the recognize-insufficient-
state step in the procedure above matters, and why "pseudo-polynomial" (dependent on W,
the numeric value of capacity, not just n, the count of items) is the honest complexity
here — knapsack remains NP-hard in the strong sense (`algorithm-design/09`) despite this
polynomial-*looking* DP, precisely because W can be exponential in the input's bit length.

### Top-down memoization vs. bottom-up tabulation
Both compute the same values; top-down (recursive with a memo table) only computes states
actually reachable from the initial call, useful when many states in the full grid are
never needed, while bottom-up (iterative, filling the table in dependency order) avoids
recursion overhead and is usually preferred once the dependency order between states is
clear (as in all three examples above: process states in increasing j or increasing i).
See `clrs/11` for the full mechanics of both; this book treats the choice as secondary to
getting the state right in the first place.

## Pros
- A systematic state-design procedure (rather than pattern-matching to memorized problem
  types) transfers to genuinely novel problems, not just recognizable variants of
  textbook DP problems.
- Once the state is correctly identified, the recurrence and complexity analysis usually
  follow mechanically — most of the intellectual difficulty front-loads into state design.
- DP guarantees a correct (if not always fast) solution whenever true optimal
  substructure and overlapping subproblems exist, unlike greedy which needs a proof that
  might not exist (`algorithm-design/04`).

## Cons
- A wrong or under-dimensioned state produces a *silently* wrong algorithm (segmented
  least squares' or knapsack's naive first attempts look plausible and can even pass
  casual testing on inputs where the missing dimension doesn't happen to matter).
- State space size directly drives complexity; a poorly designed but "technically
  correct" state (too many dimensions, or dimensions with too large a range) can make DP
  impractically slow or memory-hungry even when a smaller correct state exists.
- Pseudo-polynomial running times (like knapsack's O(nW)) can be deceptively "polynomial
  looking" while still being exponential in the actual input size (bit length of W) —
  easy to misjudge as tractable without checking this distinction.

## Alternatives
- **Greedy algorithms** (`algorithm-design/04`) — when a provably correct greedy rule
  exists, strictly cheaper than DP; always check before reaching for DP, since many
  problems that look like they need DP actually admit a greedy solution.
- **Divide and conquer** (`algorithm-design/03`) — appropriate when subproblems don't
  overlap; using DP-style memoization on non-overlapping subproblems wastes memory for no
  benefit.
- **ILP/LP relaxations or approximation algorithms** (`algorithm-design/10`) — when the
  correct DP state space is exponential in the input's natural parameters (common for
  NP-hard problems, `algorithm-design/09`), exact DP isn't tractable and an approximate or
  relaxed formulation may be the practical alternative.

## When to use it
Use DP once you've identified genuine overlapping subproblems and optimal substructure,
and have gone through the state-design procedure to confirm your candidate state actually
carries enough information for the recurrence to be correct — not just "this problem feels
like it needs DP."

## When NOT to use it
Don't reach for DP as a default whenever a problem "seems complicated" — first check for a
provably correct greedy rule (cheaper) or non-overlapping divide and conquer (simpler).
Don't accept a state design without explicitly checking it captures enough information;
"it compiles and runs" is not evidence the recurrence is correct if the state is
underspecified (the naive knapsack 1D-state attempt is the canonical trap).

## Key takeaways / mental model
The hard part of DP is choosing the state, not filling the table. Work through it as a
procedure: start from a correct naive recursion, identify what varies (candidate state),
confirm subproblems actually overlap, and — critically — confirm the candidate state
carries *enough* information for the recurrence to be provably correct, not just enough to
compile. Dimensionality of the state (1D prefix, 2D prefix+resource, etc.) should be driven
by what the recurrence genuinely needs to distinguish, illustrated by the progression from
weighted interval scheduling (1D) to knapsack (2D, resource-constrained).

## Self-check questions
1. Explain why OPT(i) = "best value using items 1..i" is an insufficient state for 0/1
   knapsack — construct a small example where two different subsets of the same items
   achieve the same value but should lead to different future decisions.
2. Walk through the state-design procedure (naive recursion -> candidate state -> overlap
   check -> sufficiency check -> state space bound) for weighted interval scheduling.
3. Why is knapsack's O(nW) running time called "pseudo-polynomial," and why does this
   matter for whether the problem is "really" tractable?
4. In segmented least squares, why does the recurrence need an inner minimization over all
   valid previous segment boundaries, rather than referencing a single fixed p(j) the way
   weighted interval scheduling does?

## References
- Algorithm Design (Jon Kleinberg, Eva Tardos), Chapter 6: "Dynamic Programming."
