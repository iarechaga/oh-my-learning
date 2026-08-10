---
id: clrs/01
subject: clrs
title: Asymptotic growth and Big-O/Theta/Omega
slug: asymptotic-growth
status: drafted
mastery:
seniority: junior
source: Introduction to Algorithms (CLRS), Chapter 3
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# Asymptotic growth and Big-O/Theta/Omega

## TL;DR
Asymptotic notation (O, Omega, Theta) describes how an algorithm's running time or space
grows as input size grows without bound, ignoring constant factors and low-order terms.
It lets you compare algorithms by their fundamental scaling behavior rather than by
machine-specific timing, which is the only comparison that survives moving to different
hardware, languages, or input sizes.

## The idea
Two algorithms solving the same problem can be compared by literally timing them, but
that comparison is fragile: it depends on the machine, the compiler, the specific input,
and the constant-factor overhead of the implementation. What you usually want to know is
a structural question: *as the input gets larger and larger, how does the cost grow?*
Does doubling the input double the work, quadruple it, or barely change it? Asymptotic
notation answers exactly this question by classifying functions into growth-rate
families and discarding the details that don't matter at scale — constant multipliers
and anything that becomes insignificant compared to the dominant term as n approaches
infinity.

This is why "the algorithm is O(n log n)" is a portable, hardware-independent claim,
while "the algorithm took 4.2 seconds on my laptop for n=10000" is not.

## How it works

### The three notations, precisely
Let f(n) and g(n) be functions from natural numbers to non-negative reals (a running-time
function and a reference function, respectively).

**Big-O (upper bound, "grows no faster than"):** f(n) = O(g(n)) means there exist
positive constants c and n0 such that 0 <= f(n) <= c*g(n) for all n >= n0. Read this as
"f is asymptotically bounded above by g, up to a constant factor, eventually." O(g(n)) is
a *set* of functions — technically you should write f(n) ∈ O(g(n)), though "f(n) = O(g(n))"
is the conventional abuse of notation used throughout CLRS and this lesson.

**Big-Omega (lower bound, "grows at least as fast as"):** f(n) = Omega(g(n)) means there
exist positive constants c and n0 such that 0 <= c*g(n) <= f(n) for all n >= n0. This is
the mirror image of O: a guarantee that f doesn't grow *slower* than g, eventually.

**Big-Theta (tight bound, "grows exactly as fast as"):** f(n) = Theta(g(n)) means there
exist positive constants c1, c2, and n0 such that 0 <= c1*g(n) <= f(n) <= c2*g(n) for all
n >= n0. Theta is O and Omega simultaneously — f is sandwiched between two constant
multiples of g for all sufficiently large n. **Theta is the strongest and most
informative of the three**, because it pins down the exact growth family, not just one
side of it.

### The "eventually" and "up to constants" clauses, worked through
Take f(n) = 3n^2 + 5n + 2. Claim: f(n) = Theta(n^2).

To prove the upper half (O(n^2)): for n >= 1, 3n^2 + 5n + 2 <= 3n^2 + 5n^2 + 2n^2 = 10n^2,
so c2 = 10, n0 = 1 works — f(n) <= 10*n^2 for all n >= 1.

To prove the lower half (Omega(n^2)): for n >= 1, 3n^2 + 5n + 2 >= 3n^2, so c1 = 3, n0 = 1
works — f(n) >= 3*n^2 for all n >= 1.

Both halves hold with the same n0 = 1, so f(n) = Theta(n^2) with c1 = 3, c2 = 10, n0 = 1.
Notice the constants (3, 10) and the low-order terms (5n, 2) all vanished from the final
classification — that is exactly the point. An algorithm that takes 3n^2 + 5n + 2
microseconds and one that takes 1000n^2 microseconds are both "Theta(n^2)" — the
notation deliberately discards the difference between a well-tuned and a poorly-tuned
constant factor, because that difference doesn't change how the algorithm scales.

### A common mistake: O as if it means Theta
In casual conversation, people say "this algorithm is O(n^2)" to mean "this algorithm's
running time is a quadratic function," but strictly, O(n^2) only claims an *upper* bound
— an algorithm that always finishes in O(1) time is *also*, technically, O(n^2), because
constant time is certainly bounded above by a quadratic function. When you want to say
"this is quadratic, no better and no worse," Theta(n^2) is the notation that actually
says that. CLRS is careful about this distinction; in interviews and casual engineering
conversation it's frequently blurred, so it's worth knowing the shortcut you're taking
when you do it.

### Rules of thumb for deriving asymptotic bounds
1. **Drop lower-order terms.** n^2 + n = Theta(n^2); the n term is asymptotically
   irrelevant once n^2 dominates.
2. **Drop constant multiplicative factors.** 5n = Theta(n); 500n = Theta(n) too.
3. **Nested loops multiply their bounds if independent**; a loop of n iterations
   containing a loop of m iterations is Theta(n*m).
4. **Sequential blocks of code add, and addition simplifies to the max** — code block A
   taking Theta(n) followed by code block B taking Theta(n^2) is Theta(n) + Theta(n^2) =
   Theta(n^2), since the larger term dominates the sum for large n.
5. **Common growth families, from slowest to fastest growing:** Theta(1) < Theta(log n)
   < Theta(n) < Theta(n log n) < Theta(n^2) < Theta(n^3) < Theta(2^n) < Theta(n!).
   Knowing this ladder lets you sanity-check a derived bound against intuition.

### Worked example: binary search
Binary search on a sorted array of n elements halves the search space each iteration.
After k halvings, the space has size n / 2^k; the search ends when this reaches 1, i.e.
k = log2(n). So the number of iterations is Theta(log n) — and since each iteration does
O(1) work (one comparison), the total running time is Theta(log n). Compare this to
linear search, which is Theta(n) in the worst case: for n = 1,000,000, binary search does
about 20 comparisons; linear search can do up to 1,000,000. This gap is exactly what
asymptotic notation is built to make visible and comparable.

## Pros
- Machine- and implementation-independent: a Theta(n log n) claim is true on any
  hardware, in any language, forever (modulo genuinely different computational models).
- Composable: the "drop lower terms, take the max of sequential blocks, multiply nested
  loops" rules let you derive a bound for a large program by combining bounds for its
  parts.
- Separates the concerns of *algorithm design* (asymptotic behavior) from *engineering
  tuning* (constant-factor optimization) — both matter, but they're different jobs with
  different tools.

## Cons
- Hides constant factors that can dominate in practice for realistic input sizes — an
  algorithm that is Theta(n) with a huge constant can lose to a Theta(n log n) algorithm
  with a tiny constant for every n you'll ever actually run.
- Says nothing about best-case or average-case behavior unless you explicitly qualify
  which case you're bounding (worst-case O(n^2) for quicksort vs. expected-case
  Theta(n log n) are both true and both important).
- Encourages premature "big-O golf" — chasing a better asymptotic bound for code that
  never runs on inputs large enough for the difference to matter.

## Alternatives
- **Direct empirical benchmarking** — measure real running time on real inputs on the
  target hardware; complements asymptotic analysis rather than replacing it, especially
  for choosing between algorithms with the same asymptotic class but different constants.
- **Amortized analysis** (`clrs/17`) — a different lens for algorithms whose per-operation
  cost varies but whose cost *averaged over a sequence* of operations is what matters
  (e.g. a growable array's occasional resize).
- **Probabilistic/expected-case analysis** (`clrs/04`) — asymptotic notation applied to
  the *expected* running time over random inputs or random choices, rather than the
  worst case.

## When to use it
Use asymptotic notation whenever comparing algorithms' fundamental scalability, choosing
a data structure or algorithm for a problem where input size will grow, or reasoning
about whether a solution will still work at 10x or 100x the current data volume.

## When NOT to use it
Don't rely on asymptotic notation alone to pick between two algorithms whose bounds are
close (e.g. Theta(n log n) vs. Theta(n log log n)) for small, bounded, known input sizes
— at that scale, constant factors and cache behavior often matter more, and empirical
benchmarking on realistic data is the better tool.

## Key takeaways / mental model
O is "at most," Omega is "at least," Theta is "exactly, up to constants." When someone
says "this is O(n^2)" colloquially, they usually mean Theta(n^2); know the difference
when precision matters. Asymptotic analysis answers "how does this scale," not "how fast
is this right now" — both questions are legitimate, but they need different tools.

## Self-check questions
1. Prove that f(n) = 7n^3 + 2n^2 + 100 is Theta(n^3) by exhibiting constants c1, c2, n0.
2. Why is it technically correct, if unhelpful, to say that an O(1) algorithm is also
   O(n^100)? What notation would you use instead to make a precise, informative claim?
3. Two algorithms are both Theta(n log n). Under what practical circumstances might one
   still be meaningfully faster than the other, and what analysis would you reach for to
   tell them apart?
4. Explain, using the "sequential blocks add and simplify to the max" rule, why an
   algorithm that does a Theta(n) preprocessing pass followed by a Theta(n^2) main pass is
   overall Theta(n^2), not Theta(n) + Theta(n^2) as two separate terms.

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 3: "Growth of
  Functions."
