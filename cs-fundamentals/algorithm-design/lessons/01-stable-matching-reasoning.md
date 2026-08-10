---
id: algorithm-design/01
subject: algorithm-design
title: Stable matching and algorithmic reasoning
slug: stable-matching-reasoning
status: drafted
mastery:
seniority: mid
source: Algorithm Design (Kleinberg & Tardos), Chapter 1
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# Stable matching and algorithmic reasoning

## TL;DR
The stable matching problem — pairing up two equal-size groups with individual
preference rankings so that no pair would rather be matched to each other than to their
assigned partners — is the book's opening case study in a discipline this subject
teaches throughout: state a precise problem definition, propose an algorithm, then
*prove* it terminates, is correct, and runs efficiently, rather than trusting intuition.
The Gale-Shapley algorithm solves it in O(n^2) and its proof introduces the invariant-based
reasoning style used for every later paradigm in this book.

## The idea
Before you can design an algorithm you have to know exactly what problem you are
solving — a surprisingly large fraction of algorithmic failures trace back to a fuzzy or
wrong problem statement, not a bad algorithm. Stable matching is chosen as the opening
example precisely because it forces this discipline: the informal goal ("pair everyone up
well") is ambiguous until you define what "well" means, and the definition that turns out
to be right (no pair prefers each other over their assigned partners) is not the first one
most people guess.

The historical motivation was matching medical school graduates to residency programs.
Both sides rank the other side by preference. A naive "maximize total happiness" matching
can be *unstable*: two people who are not matched to each other might both prefer each
other over who they got, and would defect together given the chance — exactly what
happened in real residency matching before a stable algorithm was adopted, causing
en-masse informal renegotiation outside the official system. A **stable** matching
eliminates every such incentive to defect.

## How it works

### Formal setup
n men and n women (Kleinberg & Tardos's original framing; the algorithm generalizes to
any two-sided market — companies and applicants, buyers and sellers). Each person ranks
everyone on the other side in a strict total order of preference. A **perfect matching**
pairs every person with exactly one person on the other side. A matching is **unstable**
if there exist a man m and a woman w, not matched to each other, such that m prefers w to
his assigned partner *and* w prefers m to her assigned partner — such a pair is called an
**instability** (or "rogue couple"). A matching is **stable** if it contains no
instability.

### The Gale-Shapley algorithm
```
initialize all m in M and w in W to free
while some man m is free and has not proposed to every woman:
    w = m's highest-ranked woman he has not yet proposed to
    if w is free:
        engage (m, w)
    else if w prefers m to her current partner m':
        free m'; engage (m, w)
    else:
        w rejects m (m remains free)
return the set of engaged pairs
```
Men propose in decreasing order of their own preference; women only ever trade *up* — a
woman who is engaged only breaks the engagement for someone she prefers more, never
someone she prefers less. This asymmetry (proposers get worse off over time, receivers
get better off over time) is the structural fact the entire correctness proof leans on.

### Worked example
3 men (X, Y, Z), 3 women (A, B, C). Preferences:
- X: A > B > C. Y: B > A > C. Z: A > B > C.
- A: Y > X > Z. B: X > Y > Z. C: X > Y > Z.

Trace: X proposes to A (free) -> engaged (X,A). Y proposes to B (free) -> engaged (Y,B).
Z proposes to A (engaged to X); A prefers Y > X > Z, so A still prefers her current
partner over Z... wait, A's current partner is X, and A ranks Y > X > Z, so A prefers X
to Z -> Z rejected. Z proposes to B (engaged to Y); B ranks X > Y > Z, prefers current
partner Y to Z -> Z rejected. Z proposes to C (free) -> engaged (Z,C). All men matched:
{(X,A), (Y,B), (Z,C)}. Check stability: does any pair prefer each other over their match?
Y prefers B to A (already matched to B, fine). Z prefers A to C but A prefers X to Z — no
defection. This matching is stable.

### Why the algorithm terminates
Each iteration removes one (man, woman) pair from the pool of "not yet proposed to" pairs
permanently — a man never proposes to the same woman twice. There are at most n^2 such
pairs, so the loop runs at most n^2 times before every man is either matched or has
exhausted his list. This gives the O(n^2) running time directly from the termination
argument, not a separate analysis.

### Why the result is a perfect matching
Proof by contradiction: suppose some man m ends up unmatched. Since the algorithm only
stops when no man is free, m must have proposed to and been rejected by every woman. But a
woman, once engaged, never becomes free again (she only trades up to a *better* partner,
never drops to no partner) — so every woman is engaged by the end. n women all engaged to
n-1 other men is impossible by counting, so this cannot happen: every woman ends up
engaged, hence every man does too. This "no one can end up unmatched" argument is a
template that recurs across this book: prove a required invariant, then derive existence
from a counting contradiction.

### Why the result is stable
Proof by contradiction again: suppose (m, w) is an instability under the algorithm's
output — m prefers w to his match w', and w prefers m to her match m'. Since m prefers w
to w', and men propose in decreasing preference order, m must have proposed to w *before*
w'. w either rejected m then (meaning she already had a partner she preferred over m at
that time — and since women only trade up afterward, she prefers her final partner m' to
m even more, contradicting the assumption that w prefers m to m') or she accepted m and
later traded up to someone she prefers over m, which must eventually be m' — again meaning
w prefers m' to m, the same contradiction. Either branch contradicts the assumed
instability, so no instability can exist in the output.

### Whose preferences the algorithm favors
A subtler, non-obvious result: Gale-Shapley (proposer-optimal) always produces the
matching that is simultaneously *best* for every proposer (each man gets the best partner
he could possibly get in *any* stable matching) and *worst* for every receiver (each woman
gets the worst partner she could possibly get in any stable matching). Swapping who
proposes flips this asymmetry. This matters practically — in real matching markets
(residency matching, school choice), *who proposes* is a policy decision with real
distributional consequences, not just an implementation detail.

## Pros
- Guarantees existence of a stable matching for any preference profile, constructively
  (the algorithm itself is the existence proof — no separate non-constructive argument
  needed).
- Runs in O(n^2), efficient enough for real markets with thousands of participants
  (residency matching, school choice systems both use variants of this algorithm today).
- The proposer-optimal/receiver-pessimal asymmetry is itself a useful, teachable fact for
  designing fair two-sided markets.

## Cons
- Requires strict, complete preference lists on both sides; ties or partial preferences
  need extensions of the basic algorithm and can break some of the clean guarantees.
- Multiple stable matchings can exist for the same preference profile, and which one you
  get is entirely determined by who proposes — not a neutral design choice.
- Does not account for capacity beyond 1:1 pairing (real markets like hospital-resident
  matching need many-to-one variants, which require additional care).

## Alternatives
- **Random/arbitrary perfect matching** — trivially satisfies "everyone matched" but gives
  no stability guarantee; real deployments (pre-1950s medical residency matching) suffered
  exactly this failure mode.
- **Maximum-weight bipartite matching** (Hungarian algorithm) — optimizes a global sum of
  utilities instead of the pairwise no-defection property; useful when a cardinal utility
  function exists and stability isn't the actual requirement.
- **Many-to-one and many-to-many stable matching (hospital/residents problem)** — a direct
  generalization used in real deployments, preserving the same proposal-based mechanism
  with capacities.

## When to use it
Use stable matching whenever you're designing a two-sided market where participants rank
each other and you need a matching immune to informal side-deals/defections — residency
matching, school assignment, and any centralized market design problem with ordinal
(ranking-based, not cardinal-utility) preferences on both sides.

## When NOT to use it
Don't reach for stable matching if the actual goal is maximizing a global objective (total
utility, total value) rather than eliminating individual incentives to defect — that's a
different, generally incompatible objective (the stable matching that is optimal for
proposers is not generally the one maximizing total utility). Don't use the basic 1:1
algorithm untouched when capacities exceed one per side; use the appropriate many-to-one
extension instead.

## Key takeaways / mental model
Stable matching is the book's demonstration that (1) precisely defining the problem is
itself hard and consequential, and (2) proving an algorithm correct means proving specific
invariants (here: women only trade up; men propose in decreasing preference order) that,
combined with a counting or contradiction argument, establish termination, feasibility,
and the target property (stability) — a proof template reused for every later paradigm in
this subject (greedy in `algorithm-design/04`, divide and conquer in `algorithm-design/03`).

## Self-check questions
1. Explain, in your own words, why "women only ever trade up" is the key invariant that
   makes the stability proof work — what would break if a woman could accept a
   worse-ranked man to replace her current partner?
2. Walk through why the algorithm cannot terminate with an unmatched man, using the
   counting argument (women engaged vs. men matched).
3. Why does Gale-Shapley favor proposers over receivers — give an intuitive reason tied
   to who takes the "risk" of rejection during the algorithm.
4. Suppose preferences include ties (a person is indifferent between two options on the
   other side). What breaks in the correctness proof, and roughly what would you need to
   change to handle ties?

## References
- Algorithm Design (Jon Kleinberg, Eva Tardos), Chapter 1: "Introduction: Some
  Representative Problems."
