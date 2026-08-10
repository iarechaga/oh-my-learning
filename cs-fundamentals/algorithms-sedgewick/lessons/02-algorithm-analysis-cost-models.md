---
id: algorithms-sedgewick/02
subject: algorithms-sedgewick
title: Algorithm analysis and cost models
slug: algorithm-analysis-cost-models
status: drafted
mastery:
seniority: junior
source: Algorithms (Sedgewick, Wayne), Section 1.4
prerequisites: [algorithms-sedgewick/01]
created: 2026-08-10
updated: 2026-08-10
---

# Algorithm analysis and cost models

## TL;DR
Sedgewick and Wayne frame algorithm analysis around a concrete **cost model** — naming
the specific basic operation you're counting (array accesses, comparisons, character
compares) — and pairing mathematical (tilde/Big-O) analysis with actual empirical
measurement of running programs, rather than treating asymptotic notation as a purely
abstract exercise divorced from real code.

## The idea
CLRS's asymptotic notation (`clrs/01`) is mathematically precise but implementation-
agnostic — it doesn't tell you *which* operation to count in a specific piece of code.
Sedgewick's approach is more concretely tied to actual programs: pick a **cost model**
(the operation that dominates a given algorithm's running time — array accesses for
array-based algorithms, character comparisons for string algorithms, key comparisons for
sorting), count how many times that operation executes as a function of input size, and
validate the resulting formula empirically by actually running the program and measuring
wall-clock time on inputs of different sizes. This closes the loop between "the math says
this should scale like n log n" and "does my actual implementation really behave that
way," which matters because implementation details (memory allocation patterns, cache
behavior, JIT warmup) can cause real code to deviate from the idealized cost-model
prediction.

## How it works

### Choosing a cost model
For a given algorithm, identify the single operation whose count best predicts total
running time — usually the operation inside the innermost loop that's `Theta`-dominant.
For array-based algorithms, this is typically **array accesses**; for comparison-based
sorts, **key comparisons** (and sometimes, separately, **array accesses/swaps**, tracked
as two related but distinct cost models for the same algorithm, since a sort's
comparisons and its data movement don't always scale identically — e.g. insertion sort's
comparisons and swaps happen to scale the same way, but selection sort's comparisons are
always Theta(n^2) while its swaps are only Theta(n)).

### Tilde notation: a companion to Big-O for more precise comparison
Sedgewick introduces **tilde notation** (~f(n)) alongside Big-O: f(n) ~ g(n) means
f(n)/g(n) -> 1 as n -> infinity — a *more precise* claim than Theta, because it pins down
the leading constant, not just the growth family. For example, "~n^2/2 compares" for
insertion sort's worst case is a tilde-notation statement more informative than
"Theta(n^2)" alone — it tells you the actual leading coefficient, useful when comparing
two algorithms in the *same* asymptotic class (e.g. comparing insertion sort's ~n^2/2
against selection sort's ~n^2/2 compares, which turn out to have the *same* leading term
despite different actual runtime behavior, since their swap counts differ dramatically:
insertion sort does ~n^2/4 swaps on random input while selection sort does only ~n
swaps).

### Doubling ratio experiments: validating a cost model empirically
Sedgewick's signature empirical technique: run the actual program on inputs of size n,
2n, 4n, 8n, ..., and observe the ratio of consecutive running times. **If the algorithm
is Theta(n^b), the ratio of running times as n doubles should converge to 2^b** — e.g. a
Theta(n^2) algorithm's running time should roughly quadruple (2^2 = 4) each time input
size doubles; a Theta(n log n) algorithm's ratio approaches 2 but very slowly (since
log(2n)/log(n) approaches 1, the ratio 2*log(2n)/log(n) approaches 2 as n grows, but only
approximately at any finite, reachable n) — a useful empirical fingerprint for
distinguishing linearithmic from purely linear growth in practice, and for catching bugs
where an implementation's actual asymptotic behavior doesn't match its intended design
(e.g. an accidentally quadratic implementation of what was meant to be a linearithmic
algorithm, a real and common class of performance bug).

### Worked example: doubling ratios distinguishing growth classes
Suppose measured running times are: n=1000 -> 0.1s, n=2000 -> 0.4s, n=4000 -> 1.6s,
n=8000 -> 6.4s. Each doubling of n quadruples the time (ratio = 4 = 2^2 consistently) —
strong empirical evidence the algorithm is Theta(n^2), confirmed independently of (and as
a cross-check on) a mathematical derivation of its cost model.

### Best, worst, and average case, and why all three matter
Sedgewick emphasizes reporting **all three** cases where they differ meaningfully (not
just the worst case, as CLRS's default framing might suggest emphasizing) — because for
several important algorithms (insertion sort on nearly-sorted input; quicksort on random
input, `clrs/08`), the *typical* real-world case is far better than the worst case, and
knowing this distinction changes which algorithm you'd actually deploy for a given known
input characteristic (e.g. preferring insertion sort specifically for nearly-sorted
data, where its best-case behavior is Theta(n), dramatically better than its Theta(n^2)
worst case).

## Pros
- Tying analysis to a concrete cost model (a specific counted operation) makes asymptotic
  claims directly checkable against real code, rather than staying purely abstract.
- Doubling ratio experiments give a fast, practical sanity check on whether an
  implementation's actual behavior matches its intended theoretical complexity — useful
  for catching implementation bugs that silently change asymptotic behavior.
- Tilde notation's extra precision (pinning the leading constant, not just the growth
  family) helps distinguish between algorithms in the same Big-O class that nonetheless
  perform meaningfully differently in practice.

## Cons
- A cost model chosen for one algorithm (e.g. comparisons for a sort) may not capture
  everything that affects real running time (cache misses, memory allocation, constant-
  factor differences in the "cheap" operations you didn't count) — empirical measurement
  is a necessary complement, not something the cost model alone guarantees.
- Doubling ratio experiments require an actual runnable implementation and real
  measurement infrastructure — they don't substitute for a mathematical derivation when
  you need a guarantee that holds for all input sizes, not just the ones you happened to
  test.
- Tilde notation's extra precision is only meaningful when comparing algorithms already
  known to be in the same Big-O class — it says nothing new when comparing algorithms of
  genuinely different growth rates, where Big-O/Theta already settles the comparison.

## Alternatives
- **Pure Big-O/Theta/Omega analysis** (`clrs/01`) — sufficient and standard when you only
  need to compare algorithms across different growth-rate families, without needing the
  extra leading-constant precision tilde notation provides.
- **Profiling tools** — for diagnosing where real running time actually goes in a
  specific implementation (as opposed to a hand-chosen cost model), a profiler gives
  ground truth that can reveal cost-model assumptions were wrong (e.g. memory allocation,
  not comparisons, turned out to dominate).

## When to use it
Use a concrete cost model plus doubling-ratio empirical validation whenever you're
implementing (not just theoretically analyzing) an algorithm and want confidence that
your actual code's performance matches its intended design — especially useful for
catching accidental complexity regressions during development.

## When NOT to use it
Don't rely solely on doubling-ratio experiments as a substitute for a real complexity
proof when you need a guarantee for input sizes far beyond what you can practically
test, or for adversarial/worst-case inputs your test data doesn't include. Don't bother
with tilde notation's extra precision when comparing algorithms of clearly different
Big-O classes — it adds no useful information there.

## Key takeaways / mental model
Pick a concrete operation to count (the cost model), derive its growth rate
mathematically, then validate empirically via doubling-ratio experiments (time should
scale as 2^b when input doubles, for a Theta(n^b) algorithm). This closes the loop
between abstract asymptotic analysis and the actual behavior of running code.

## Self-check questions
1. For an algorithm you suspect is Theta(n log n), what doubling ratio would you expect
   to observe empirically as input size doubles repeatedly, and why does it only
   approach, rather than exactly equal, that value at any finite input size?
2. Explain why insertion sort and selection sort can share the same ~n^2/2 comparison
   count (tilde notation) while having very different swap counts, and why that
   difference matters practically.
3. Describe a scenario where a cost model based purely on counting comparisons would fail
   to predict real-world running time, and what empirical step would reveal the
   discrepancy.
4. Why might reporting best-case, not just worst-case, complexity change which sorting
   algorithm you'd choose for a specific known input distribution (e.g. nearly-sorted
   data)?

## References
- Algorithms, 4th Edition (Robert Sedgewick, Kevin Wayne), Section 1.4: "Analysis of
  Algorithms."
