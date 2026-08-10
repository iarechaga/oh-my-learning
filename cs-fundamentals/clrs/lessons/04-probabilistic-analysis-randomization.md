---
id: clrs/04
subject: clrs
title: Probabilistic analysis and randomized algorithms
slug: probabilistic-analysis-randomization
status: drafted
mastery:
seniority: senior
source: Introduction to Algorithms (CLRS), Chapter 5
prerequisites: [clrs/01]
created: 2026-08-10
updated: 2026-08-10
---

# Probabilistic analysis and randomized algorithms

## TL;DR
Probabilistic analysis computes an algorithm's *expected* running time by assuming a
distribution over inputs (often "all permutations equally likely"). Randomized
algorithms instead make random choices *during execution*, so the algorithm itself
introduces randomness rather than assuming it about the input — this guarantees good
expected performance regardless of what the input actually is, which is the stronger and
more useful guarantee in practice.

## The idea
Worst-case analysis (`clrs/01`) answers "what's the most this algorithm could ever cost?"
— a vital and honest question, but sometimes pessimistic: an algorithm might have a bad
worst case that occurs only for a vanishingly rare or adversarially-constructed input,
while performing excellently on every input you'll realistically see. Probabilistic
analysis asks a different, complementary question: "if inputs are drawn from some
distribution, what's the *average* cost?" But that requires knowing (or assuming) the
input distribution, which is often unrealistic — you rarely control what data your users
actually feed the algorithm, and "average case over all permutations" is meaningless if
your real inputs are anything but uniformly random.

Randomization sidesteps this: instead of assuming randomness about the *input*, the
*algorithm* injects its own randomness (e.g. shuffling the input first, or picking a
random pivot). The running time becomes a random variable whose distribution the
algorithm controls, completely independent of what the actual input looks like — a
malicious or adversarial input-provider cannot force a bad case, because they don't
control the algorithm's coin flips.

## How it works

### Probabilistic analysis: the hiring problem
CLRS's running example: you interview n candidates in a fixed order, hiring a new
assistant (at a switching cost) every time you meet someone better than your current
best. In the worst case (candidates arrive in increasing order of quality), you hire all
n candidates — expensive. But *if* you assume the candidates arrive in a uniformly random
order, the *expected* number of hires is only H(n) = 1 + 1/2 + 1/3 + ... + 1/n ≈ ln(n) —
logarithmic, not linear. This is derived using **indicator random variables**: define
X_i = 1 if candidate i is hired, 0 otherwise. Candidate i is hired exactly when they are
the best of the first i candidates, which (by symmetry, under a random ordering) happens
with probability exactly 1/i. By linearity of expectation, E[total hires] =
sum(E[X_i]) = sum(1/i) for i=1 to n = H(n) ≈ ln(n).

**Linearity of expectation is the key tool here**: E[X_1 + X_2 + ... + X_n] = E[X_1] +
E[X_2] + ... + E[X_n], *even when the X_i are not independent* — this is what makes the
technique so broadly usable, since real algorithms' events are often correlated in
complicated ways that would make a direct joint-probability calculation intractable.

### The catch: this result requires assuming random input order
The ln(n) result assumes candidates arrive in random order. If your actual hiring
process interviews candidates in, say, alphabetical order of last name, this analysis
says nothing useful — the input isn't random, so the "expected number of hires" isn't
meaningful for your actual process.

### Randomized algorithms: making the algorithm supply the randomness
The fix: don't assume the input is random — make it random. **Randomize in advance**:
permute the candidate list uniformly at random *before* the interview process starts.
Now the ln(n) expected-hires bound holds *for any* input list, because the randomness
comes from the algorithm's own shuffle step, not from an assumption about how the input
arrived.

### Worked example: randomized quicksort
Quicksort's worst case (Theta(n^2)) occurs specifically when the pivot chosen is always
the smallest or largest remaining element — e.g. always picking the first element as
pivot on an already-sorted array. **Randomized quicksort** picks the pivot uniformly at
random from the current subarray on every partition step. This doesn't change the
worst-case complexity (an adversary who somehow knew every random choice in advance could
still force Theta(n^2)), but it makes that worst case require the random choices
themselves to be adversarial, which — if the random number generator is truly random and
unknown to any adversary supplying the input — has vanishing probability. The **expected**
running time of randomized quicksort is Theta(n log n) for *any* input, including
already-sorted or adversarially chosen ones, because the pivot choices, not the input,
determine the good or bad partitioning.

This is the crucial distinction to internalize: **deterministic quicksort's Theta(n log n)
is an average over *inputs*** (true for "most" permutations, false for sorted or
reverse-sorted ones) **while randomized quicksort's Theta(n log n) is an average over the
algorithm's *own coin flips*, true for every single input.** The second guarantee is
strictly more useful, because you don't get to choose your users' data, but you do
control your own random number generator.

### Two flavors of randomized algorithm
- **Las Vegas algorithms** — always produce a correct answer; only the running time is
  random (randomized quicksort is Las Vegas: the sort is always correct, but how long it
  takes to finish varies).
- **Monte Carlo algorithms** — run in a fixed (often deterministic) time bound but have a
  small, controllable probability of producing an incorrect answer (e.g. randomized
  primality testing, which errs on the side of caution and can be made arbitrarily
  reliable by repeating the test).

## Pros
- Randomized algorithms defend against adversarial or unluckily-structured inputs without
  needing to know or assume anything about the actual input distribution.
- Indicator random variables plus linearity of expectation let you compute expected costs
  even when the underlying events are complex and dependent, sidestepping a full joint-
  distribution analysis.
- Often the simplest known algorithm for a problem is a randomized one (randomized
  quicksort is simpler to reason about than deterministic worst-case-optimal partitioning
  schemes like median-of-medians).

## Cons
- A worst case still technically exists for Las Vegas algorithms (randomized quicksort
  can still take Theta(n^2) time on an extraordinarily unlucky sequence of random
  choices) — randomization changes the *probability* of the bad case, not its existence.
- Requires a genuine, unpredictable source of randomness; a poor or predictable random
  number generator can reintroduce exactly the adversarial vulnerability randomization
  was meant to remove.
- Monte Carlo algorithms trade a probability of outright incorrectness for speed —
  inappropriate wherever a wrong answer is unacceptable regardless of probability.
- Non-reproducibility: a randomized algorithm's running time (and, for Monte Carlo, its
  answer) varies run to run, which complicates debugging and testing unless the random
  seed is fixed and logged.

## Alternatives
- **Deterministic worst-case-optimal algorithms** — e.g. the median-of-medians selection
  algorithm (`clrs/10`) guarantees Theta(n) worst-case time with no randomness at all, at
  the cost of a larger constant factor and more complex implementation than its randomized
  counterpart.
- **Amortized analysis** (`clrs/17`) — a different technique for bounding cost *over a
  sequence of operations* on a single, possibly adversarial input, rather than bounding
  expected cost over random choices or random inputs.
- **Worst-case analysis alone** (`clrs/01`) — appropriate when you need a hard guarantee
  regardless of probability, e.g. in real-time or safety-critical systems where "usually
  fast" isn't an acceptable guarantee.

## When to use it
Use randomized algorithms when you need good expected performance regardless of input
(especially when inputs might be adversarial, sorted, or otherwise structured in a way
that defeats a deterministic algorithm's assumptions), and when occasional variance in
running time (Las Vegas) or a small controllable error probability (Monte Carlo) is
acceptable.

## When NOT to use it
Don't use randomized algorithms where a hard worst-case time bound is required (real-time
systems, safety-critical code) — use a deterministic worst-case-optimal algorithm
instead. Don't use Monte Carlo algorithms where any probability of an incorrect answer,
however small, is unacceptable.

## Key takeaways / mental model
Probabilistic analysis assumes randomness about the input; randomized algorithms supply
their own randomness and thereby get a guarantee that holds for *every* input. Indicator
random variables plus linearity of expectation is the workhorse technique for computing
expected costs of complex, dependent events. Randomization changes an adversary's job
from "craft a bad input" to "predict a random number generator" — a much harder job.

## Self-check questions
1. In the hiring problem, why does the expected number of hires (~ln n) require an
   assumption about input order, while randomized quicksort's expected Theta(n log n)
   does not?
2. Explain why linearity of expectation applies to the indicator variables in the hiring
   problem even though the events "candidate i is hired" are not independent of each
   other.
3. Randomized quicksort can still take Theta(n^2) time. In what sense, precisely, is it
   still an improvement over deterministic quicksort with a fixed pivot rule?
4. Give a real scenario where a Monte Carlo algorithm's small error probability would be
   unacceptable, and one where it would be a perfectly reasonable trade-off for speed.

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 5: "Probabilistic
  Analysis and Randomized Algorithms."
