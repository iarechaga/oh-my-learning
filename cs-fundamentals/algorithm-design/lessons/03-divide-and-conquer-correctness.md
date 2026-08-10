---
id: algorithm-design/03
subject: algorithm-design
title: Divide and conquer with proof of correctness
slug: divide-and-conquer-correctness
status: drafted
mastery:
seniority: mid
source: Algorithm Design (Kleinberg & Tardos), Chapter 5
prerequisites: [algorithm-design/02, clrs/03]
created: 2026-08-10
updated: 2026-08-10
---

# Divide and conquer with proof of correctness

## TL;DR
Divide and conquer solves a problem by splitting it into smaller independent
subproblems of the *same* problem, solving each recursively, and combining the results;
correctness is proved by strong induction on the input size, and running time is derived
from the resulting recurrence (`algorithm-design/02`). This lesson emphasizes the proof
obligation CLRS's `clrs/03` treats more lightly: every divide-and-conquer algorithm needs
an explicit inductive correctness argument, not just a plausible-sounding recursive
sketch.

## The idea
Many problems have a recursive structure: the answer for a large instance can be
assembled from answers to smaller instances of the *identical* problem. When this
structure exists and subproblems don't overlap (contrast with dynamic programming,
`algorithm-design/05`, where subproblems *do* overlap and get memoized), divide and
conquer is often the simplest correct and efficient design. But "split, recurse, combine"
is a *template*, not a guarantee — a wrong combine step or a wrong base case silently
produces an incorrect algorithm that nonetheless "looks recursive" and might even work on
your first few test cases. The discipline this book insists on is proving correctness by
strong induction: assume the recursive calls on strictly smaller inputs are correct
(the induction hypothesis), then prove the combine step correctly produces the answer for
the full input from those (assumed-correct) smaller answers.

## How it works

### The three steps and the matching proof structure
1. **Divide**: split the input into smaller subproblems of the same kind.
2. **Conquer**: solve each subproblem recursively (base case handles the smallest
   instances directly).
3. **Combine**: merge the subproblem solutions into a solution for the original input.

The correctness proof mirrors this exactly, by **strong induction on input size n**:
- **Base case**: verify the algorithm is correct on the smallest input(s) directly (often
  trivial, e.g. n=0 or n=1).
- **Inductive step**: assume the algorithm is correct on every input strictly smaller than
  n (the induction hypothesis — this is why it's *strong* induction, not simple induction
  on n-1 alone: divide and conquer often splits into pieces of varying smaller sizes, not
  just "one smaller"). Prove that, given correct answers to the subproblems (guaranteed by
  the hypothesis), the combine step produces a correct answer for size n.

### Worked example 1: closest pair of points
Given n points in the plane, find the two closest together. Brute force is O(n^2) (check
every pair). Divide and conquer:
1. **Divide**: sort points by x-coordinate; split into left half L and right half R by a
   vertical line.
2. **Conquer**: recursively find the closest pair in L (distance d_L) and in R (distance
   d_R). Let d = min(d_L, d_R).
3. **Combine**: the true closest pair might straddle the dividing line — one point in L,
   one in R, closer together than d. Check only points within distance d of the dividing
   line (a "strip"). The key geometric fact making this efficient: within that strip, for
   any point, at most a constant number of other strip points can be within distance d of
   it (a packing argument — points closer than d to each other can't be densely packed in
   a strip of width 2d without violating d being the current best). So sorting the strip
   by y-coordinate and checking each point against a small constant number of neighbors
   suffices, giving O(n log n) for the strip step (dominated by the sort) rather than
   O(n^2).

**Correctness by induction**: base case (n <= 3) checked directly by brute force. Inductive
step: assume recursive calls on L and R (each strictly smaller than n) correctly return
d_L and d_R. The combine step's correctness rests on the packing argument above: it's
proven that *no* cross-boundary pair closer than min(d_L, d_R) can be missed by only
checking the strip — this is the non-trivial part of the proof, not the recursion itself.
Overall T(n) = 2T(n/2) + O(n log n) naively (from re-sorting the strip each time), which a
smarter implementation reduces to O(n) combine work by carrying a pre-sorted-by-y list
through the recursion, giving T(n) = 2T(n/2) + O(n) = O(n log n) by the Master theorem
(`algorithm-design/02`).

### Worked example 2: counting inversions
Given a sequence, count the number of pairs (i, j) with i < j but a[i] > a[j] (a measure
of "how far from sorted" the sequence is — used to measure similarity between rankings).
Naive: O(n^2), check every pair. Divide and conquer piggybacks on mergesort: split in
half, recursively count inversions within each half, then count "cross" inversions (left
element after a right element in sorted order) during the merge step itself — every time
the merge step takes an element from the right half before exhausting the left half, that
element is smaller than *all remaining* left-half elements, contributing exactly
(remaining left-half count) cross inversions in O(1) extra work per merge step. Total:
T(n) = 2T(n/2) + O(n) (linear merge, same as mergesort) = O(n log n), versus O(n^2) naive
— a direct illustration that recognizing an existing efficient algorithm's structure
(mergesort) inside a *different* problem (counting inversions) is itself a design skill
this book is teaching.

### Base case pitfalls
A subtle, common bug source: base cases that are correct but *too large or too small*.
Too small (e.g. always recursing down to n=1 individually) can make the combine step do
needless extra work compared to switching to brute force earlier (this is also a real
practical optimization — many production sort/search implementations switch to insertion
sort below a small threshold, as noted in `algorithms-sedgewick/05`). Too large or
malformed base cases (e.g. assuming n is always even when splitting, then mishandling an
odd n) are a correctness bug, not just a performance one — always verify the divide step
handles n=1, n=2, and odd/even n explicitly.

### Why "it looks recursive" is not a proof
A tempting but invalid shortcut is to write a divide-and-conquer-shaped algorithm, test it
on a few small inputs, and declare it correct because "the recursion obviously works."
This fails to catch bugs where the *combine* step is subtly wrong for some input shapes
but happens to be right on your test cases (the closest-pair strip argument above is
exactly the kind of non-obvious combine-step correctness fact a few test cases would never
surface). The strong-induction proof is what actually certifies correctness for *all* n,
not just the tested ones — treat "prove the combine step correct assuming the recursive
calls are correct" as a mandatory step, not an optional formality.

## Pros
- Naturally yields efficient algorithms (often O(n log n)) for problems where brute force
  is quadratic or worse, by exploiting a splitting structure.
- The induction-based proof template is reusable and mechanical once internalized: base
  case, inductive hypothesis, prove the combine step — the same shape every time.
- Subproblems are independent (unlike DP), so divide-and-conquer algorithms parallelize
  naturally — each recursive call can run concurrently.

## Cons
- Only applies when the problem actually decomposes into independent, same-shaped
  subproblems — forcing a divide-and-conquer shape onto a problem without that structure
  produces either an incorrect algorithm or one with no efficiency benefit.
- The combine step is often the hard, non-obvious part (the closest-pair strip argument),
  and a wrong combine step is a silent correctness bug, not a crash — testing alone rarely
  catches it.
- Recursive call overhead (stack frames, function call cost) can make divide and conquer
  slower than a well-tuned iterative algorithm in practice for small n, even with a better
  asymptotic bound.

## Alternatives
- **Dynamic programming** (`algorithm-design/05`) — for problems whose recursive
  subproblems *overlap* (the same subproblem recurs many times); memoizing to avoid
  redundant recomputation is the DP alternative to pure divide and conquer's assumption of
  independent subproblems.
- **Greedy algorithms** (`algorithm-design/04`) — when a single locally-optimal choice,
  proven correct via an exchange argument, avoids recursion into subproblems altogether;
  simpler and faster when applicable, but a strictly narrower set of problems.
- **Brute force** — always correct, often the right choice for small n or as the base
  case cutoff, or when the divide-and-conquer combine step turns out to be as expensive as
  brute force itself (offering no real benefit).

## When to use it
Use divide and conquer when a problem splits into same-shaped, independent subproblems
whose combine cost is cheap relative to brute force's total cost — sorting, closest pair,
counting inversions, and (as covered in `clrs/03`) fast multiplication algorithms are the
classic cases.

## When NOT to use it
Don't use it when subproblems overlap significantly (recomputing the same subproblem many
times) — that's dynamic programming's territory (`algorithm-design/05`) and pure divide
and conquer without memoization would be exponentially wasteful (the naive recursive
Fibonacci is the textbook cautionary example). Don't skip the inductive correctness proof
just because the recursive structure "looks obviously right" — the combine step is where
real bugs hide.

## Key takeaways / mental model
Divide and conquer is "split into same-shaped independent subproblems, recurse, combine" —
and every instance of it owes you a strong-induction proof: base case correct, and (assume
recursive calls on strictly smaller inputs are correct) prove the combine step is correct.
Running time comes from solving the resulting recurrence (`algorithm-design/02`). The hard
part is almost always the combine step's correctness, not the recursive skeleton.

## Self-check questions
1. In the closest-pair algorithm, why isn't it enough to just take the minimum of d_L and
   d_R — what specific case does the "strip" combine step catch that the two recursive
   calls alone would miss?
2. Write out, in your own words, the base case and inductive step of a strong-induction
   correctness proof for the counting-inversions algorithm.
3. Give an example of a problem where a divide-and-conquer-shaped recursion would be
   *inefficient* because the subproblems overlap, and explain what technique fixes that.
4. Why is "I tested it on 5 inputs and it worked" not equivalent to a correctness proof
   for a divide-and-conquer algorithm — what kind of bug would testing on small inputs
   likely miss?

## References
- Algorithm Design (Jon Kleinberg, Eva Tardos), Chapter 5: "Divide and Conquer."
