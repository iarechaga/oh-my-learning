---
id: clrs/19
subject: clrs
title: NP-completeness and polynomial-time reductions
slug: np-completeness-reductions
status: drafted
mastery:
seniority: senior
source: Introduction to Algorithms (CLRS), Chapter 34
prerequisites: [clrs/01, clrs/11, clrs/12]
created: 2026-08-10
updated: 2026-08-10
---

# NP-completeness and polynomial-time reductions

## TL;DR
P is the class of problems solvable in polynomial time; NP is the class of problems whose
*proposed solutions* can be *verified* in polynomial time (whether or not they can be
*found* efficiently). A problem is NP-complete if it's in NP and every other NP problem
can be polynomial-time-reduced to it — meaning an efficient algorithm for any one
NP-complete problem would give an efficient algorithm for *all* of them. Proving a
problem NP-complete is a rigorous, practically load-bearing way to justify giving up on
finding an efficient exact algorithm for it.

## The idea
Some problems (sorting, shortest paths, MST) have known polynomial-time algorithms. Many
other important problems (the traveling salesman problem, boolean satisfiability, graph
coloring) have resisted every attempt at an efficient algorithm for decades, despite
massive effort by the entire field. NP-completeness theory doesn't (yet) prove these
problems are truly intractable — that's the famous open P vs. NP question — but it does
prove something almost as useful: these problems are all *equally hard*, in the precise
sense that a polynomial-time algorithm for any single one of them would immediately yield
one for all of them (and, in fact, for every problem in NP). Given that thousands of
brilliant researchers have failed to find such an algorithm for any of them over
decades, this equivalence is treated, in practice, as very strong evidence that no
efficient algorithm exists for any of them — which is precisely why proving a new
problem NP-complete is treated as a legitimate, rigorous reason to stop searching for an
exact polynomial-time algorithm and pivot to approximation (`clrs/20`) or heuristics
instead.

## How it works

### The complexity classes P, NP, and NP-complete
- **P** — problems solvable by a deterministic algorithm in polynomial time (in the size
  of the input). Sorting (Theta(n log n)), shortest paths (`clrs/14`), MST (`clrs/15`) are
  all in P.
- **NP** ("nondeterministic polynomial time") — problems for which a proposed *solution*
  (a "certificate") can be **verified** correct in polynomial time, regardless of how
  hard it might be to *find* that solution in the first place. Every problem in P is
  trivially also in NP (if you can solve it in polynomial time, you can certainly verify
  a solution in polynomial time — just solve it yourself and compare). The open question
  "P = NP?" asks whether the reverse also holds: can every efficiently *verifiable*
  problem also be efficiently *solved*? Nobody knows.
- **NP-hard** — a problem to which every problem in NP can be polynomial-time-reduced,
  regardless of whether the problem itself is in NP (it might be even harder, or not even
  a yes/no decision problem at all).
- **NP-complete** — a problem that is both in NP *and* NP-hard: the hardest problems
  *within* NP, in the precise sense that a polynomial-time algorithm for any single
  NP-complete problem would prove P = NP.

### Polynomial-time reductions: the mechanism that ties these problems together
A polynomial-time reduction from problem A to problem B is a polynomial-time-computable
transformation of any instance of A into an instance of B, such that the transformed
instance is a "yes" instance of B if and only if the original was a "yes" instance of A.
**If such a reduction exists, and B is solvable in polynomial time, then A is too**
(transform A's instance to B, solve B, translate the answer back — all in polynomial
time). This is the entire logical engine behind the theory: reductions let you transfer
both *hardness* (if A is known NP-hard and reduces to B, B is also NP-hard) and
*hypothetical tractability* (if B turns out to have an efficient algorithm, so does A)
across problems.

### The bootstrapping problem, and Cook-Levin
To call *anything* NP-complete, you need at least one problem already proven NP-complete
to reduce *from* — but the very first one can't be established that way (there's nothing
earlier to reduce from). The **Cook-Levin theorem** breaks this circularity by directly
proving **Boolean satisfiability (SAT)** — given a boolean formula, does some assignment
of true/false to its variables make it evaluate to true? — is NP-complete, by a direct
construction showing any NP problem's polynomial-time verification process can itself be
encoded as a SAT instance. Once SAT is established as the first NP-complete problem,
every subsequent NP-completeness proof works by reducing a *known* NP-complete problem
to the *new* problem being classified (showing the new problem is at least as hard),
combined with showing the new problem is itself in NP (a certificate exists and is
polynomial-time verifiable) — together proving the new problem is also NP-complete.

### Worked example: reducing from a known NP-complete problem
To prove a new problem X is NP-complete: (1) show X is in NP (exhibit a certificate
format and a polynomial-time verifier). (2) Pick a *known* NP-complete problem Y (e.g.
SAT, or 3-SAT, or the clique problem, or vertex cover — all previously established via
their own chains of reductions back to SAT), and construct a polynomial-time reduction
*from* Y *to* X — i.e. show how to transform any Y-instance into an X-instance that has
the same yes/no answer. This proves X is at least as hard as Y (NP-hard), and combined
with step 1 (X is in NP), X is NP-complete. **Classic example: vertex cover reduces from
independent set.** A graph has an independent set of size k if and only if it has a
vertex cover of size (V - k) — the complement of any independent set is exactly a vertex
cover, and vice versa. This is a trivially polynomial-time (in fact O(1) beyond copying
the graph) transformation, immediately transferring independent set's known
NP-completeness to vertex cover.

### Why this matters practically, not just theoretically
Once a problem is proven NP-complete, spending more effort hunting for an exact,
polynomial-time algorithm is (barring an eventual proof that P=NP, considered very
unlikely by most researchers) provably as hard as solving the single biggest open
problem in computer science — a strong, legitimate signal to redirect engineering effort
toward approximation algorithms (`clrs/20`), heuristics, exploiting special structure in
your specific instances (e.g. small input sizes, or graphs with bounded treewidth), or
accepting exponential-time exact solutions for genuinely small inputs.

## Pros
- Gives a rigorous, well-established way to *justify* abandoning the search for an exact
  efficient algorithm — a scientifically grounded reason, not just "we tried and gave
  up," backed by the fact that success would resolve P vs. NP.
- The web of reductions across hundreds of known NP-complete problems means recognizing a
  new problem's resemblance to a known one (e.g. "this looks like vertex cover") often
  quickly reveals both its hardness and clues about how to approach it (approximation
  techniques often transfer along the same reduction relationships).
- Establishes a genuine equivalence class ("these problems are all exactly as hard as
  each other"), a deep and surprising structural fact about computation, not just an
  informal folklore claim about "hard problems."

## Cons
- NP-completeness is not a proof of intractability — it's a proof of *relative*
  hardness contingent on the open P vs. NP question; in the (widely considered unlikely)
  event P=NP is eventually proven, every NP-complete problem would suddenly have an
  efficient algorithm.
- Doesn't help at all with the *specific* instances you actually need to solve — some
  NP-complete problems have large classes of practically-easy special cases (small
  inputs, particular graph structures) that are perfectly tractable despite the
  problem's general-case hardness.
- Constructing a correct reduction proof requires real care and rigor — a subtly wrong
  reduction (one that doesn't correctly preserve yes/no answers in both directions) is a
  common error, especially for learners new to the technique.

## Alternatives
- **Approximation algorithms** (`clrs/20`) — for NP-hard optimization problems, accept a
  provably-bounded-distance-from-optimal answer in polynomial time instead of an exact
  answer.
- **Exponential/exact algorithms for small or structured instances** — many NP-complete
  problems have efficient exact algorithms when restricted to bounded input size, bounded
  treewidth, planar graphs, or other special structure — worth checking before assuming
  the general-case hardness applies to your specific instances.
- **Heuristics and local search** (`algorithm-design/11`) — no worst-case guarantee at
  all, but often good in practice for the specific instance distributions encountered in
  a real application.

## When to use it
Reach for NP-completeness theory (recognizing a reduction from a known NP-complete
problem) whenever you're stuck failing to find an efficient algorithm for a new
combinatorial problem — proving it NP-complete redirects effort productively toward
approximation or heuristics instead of continuing to search for an exact polynomial-time
solution that almost certainly doesn't exist.

## When NOT to use it
Don't invoke "it's NP-complete, so we give up" without checking whether your actual
instances have exploitable special structure (small size, bounded treewidth, restricted
input class) that makes the general-case hardness irrelevant to your specific use case.
Don't confuse "NP-complete" with "impossible" — it's a statement about *worst-case,
general-instance* hardness, not a blanket statement that no useful algorithm exists for
any instance you'll ever encounter.

## Key takeaways / mental model
NP-completeness is a web of polynomial-time reductions, all ultimately anchored to SAT
via the Cook-Levin theorem, proving a large class of important problems are all exactly
as hard as each other and as hard as any problem in NP. Proving a new problem NP-complete
is done by finding a reduction *from* an already-known NP-complete problem *to* it — a
constructive proof technique, not just an informal classification.

## Self-check questions
1. Explain the difference between "solvable in polynomial time" (P) and "verifiable in
   polynomial time" (NP), and why every problem in P is automatically also in NP.
2. Walk through the independent-set-to-vertex-cover reduction: why does a graph having an
   independent set of size k directly imply it has a vertex cover of size V-k?
3. Why couldn't the very first NP-complete problem (SAT) be proven NP-complete by
   reducing from another already-known NP-complete problem, and how does the Cook-Levin
   theorem solve this bootstrapping problem?
4. A colleague says "this problem is NP-complete, so there's no point trying to solve it
   efficiently for our use case." Under what circumstances might that conclusion be wrong
   for a specific practical instance?

## References
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein), Chapter 34:
  "NP-Completeness."
