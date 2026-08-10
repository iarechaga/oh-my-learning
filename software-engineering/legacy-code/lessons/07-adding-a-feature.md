---
id: legacy-code/07
subject: legacy-code
title: Adding a Feature to Untested Code
slug: adding-a-feature
status: drafted
mastery:
seniority: senior
source: Working Effectively with Legacy Code (Michael C. Feathers), Chapter 8
prerequisites: [legacy-code/03, refactoring/02]
created: 2026-08-10
updated: 2026-08-10
---

# Adding a Feature to Untested Code

## TL;DR
The disciplined sequence for adding a feature to legacy code: identify the specific point of change, get that specific area under characterization tests (`legacy-code/03`), write a failing test for the new feature (test-first, like ordinary TDD), make it pass with the smallest reasonable change, and only then consider refactoring the surrounding structure — never mix "add the feature" and "clean up the surrounding mess" into one unverifiable step.

## The idea
This lesson pulls together several of the subject's earlier techniques (seams, characterization tests, the two-hats discipline from `refactoring/01`) into the specific, recurring, practical workflow this whole book exists to support: you have a real feature to add, the code you need to touch has no tests, and you need a disciplined path from "untested and risky" to "feature added, verified, and no worse off structurally than before." Feathers' sequence resists two common, tempting shortcuts: adding the feature directly into the messy existing structure (fast, but compounds the mess — echoing `pragmatic-programmer/02`'s broken-windows concern) and refactoring the whole area extensively *before* adding the feature, without a safety net justifying that confidence (risky, per `legacy-code/01`'s change dilemma).

## How it works

### Step 1: identify the specific point of change
Before touching anything, pinpoint exactly where the new feature's logic needs to live or be triggered from — informed by `legacy-code/06`'s comprehension-building sketch technique if the area isn't already well understood. This is deliberately narrow: you're not trying to understand the whole module, just enough to know precisely where the change belongs.

### Step 2: find or create a test point (seam), and characterize existing behavior around it
Using `legacy-code/02`'s seam-finding and `legacy-code/05`'s dependency-breaking techniques as needed, get the specific area you're about to touch into a state where you *can* write tests against it — then write characterization tests (`legacy-code/03`) covering its current behavior, specifically the behavior your new feature must not accidentally break.

### Step 3: write a test for the new feature, and watch it fail
Exactly like ordinary test-driven development: write a test expressing the new feature's desired behavior *before* implementing it, confirm it fails (since the feature doesn't exist yet), which both verifies the test is actually exercising the right code path and gives you a clear, concrete target to implement toward.

### Step 4: make the new test pass with the smallest reasonable change
Implement the feature with the minimum change needed to make the new test pass, without yet worrying about whether the surrounding code's structure is ideal — this keeps the "adding function" hat on (per `refactoring/01`) and defers structural concerns to a separate, later step.

**Worked example — the full sequence, concretely.** Adding a "loyalty points" calculation to an existing, untested `calculate_total(order)` function:
1. **Identify the point of change**: the new points calculation should hook in right after the total is computed, inside `calculate_total`.
2. **Seam and characterize**: `calculate_total` currently has no dependencies needing breaking (it's a pure function of `order`), so no seam work is needed here — go straight to characterization: write tests locking in `calculate_total`'s current output for a representative sample of orders (a normal order, an order with a discount, an empty order), so you have a trustworthy safety net for the *existing* behavior before touching anything.
3. **Test-first for the new feature**: write `test_calculate_total_also_awards_loyalty_points()`, asserting the new, not-yet-existing behavior; confirm it fails.
4. **Implement minimally**: add the loyalty-points calculation, make the new test pass, and re-run the characterization tests from step 2 to confirm the *existing* total-calculation behavior is genuinely unchanged.

### Step 5 (optional, separate step): refactor now that a safety net exists
Only once the feature is added and verified working, *and* you now have both the original characterization tests and the new feature test in place as a safety net, consider whether the surrounding code's structure would benefit from refactoring (per `refactoring/02`'s "make the change easy" framing, now applied retroactively, or simply as ordinary opportunistic cleanup). This step is explicitly optional and separate — the feature is already safely delivered before this point, so there's no pressure to combine cleanup with the feature work in the same risky step.

### Why this sequence resists both tempting shortcuts
- **Against "just add it to the mess"**: doing so without characterization tests first means you have no way to verify the existing behavior wasn't accidentally disturbed by your change — you're relying on hope, exactly `legacy-code/01`'s change dilemma.
- **Against "refactor first, extensively, then add the feature"**: doing so *before* you have tests in place means the refactoring itself is unverified and risky — you'd be trying to improve structure you don't yet have a safety net for, which is precisely the scenario `refactoring/03` warns against.

## Pros
- The sequence provides a concrete, repeatable, low-risk path for the single most common real-world legacy-code task: adding a feature to code nobody has verified the behavior of.
- Test-first feature development, even retrofitted onto legacy code via this sequence, produces the same clarity-of-target benefit ordinary TDD provides.
- Deferring refactoring to an explicit, optional, later step (once a safety net exists) avoids the risk of an unverified structural change compounding with an unverified feature change.

## Cons
- The full sequence takes real, sometimes substantial time for a feature that might otherwise feel like it "should" be a five-minute change — a real cost that can be hard to justify to stakeholders unfamiliar with why the extra steps matter.
- Characterizing "enough" of the existing behavior (step 2) to be a genuinely trustworthy safety net requires judgment — too little coverage leaves real gaps; attempting exhaustive coverage can itself become disproportionate.
- If the specific point of change (step 1) is misidentified due to poor initial comprehension, the whole subsequent sequence is built on a wrong foundation, and may need to be restarted once the mistake is discovered.

## Alternatives
- **Feature flags / branch by abstraction at a larger scale** (`refactoring/11`) — for larger, riskier features than a single function's worth of change, wrapping the new feature behind a flag while it's incrementally built and verified, rather than this lesson's finer-grained, single-change-point sequence.
- **A "spike" implementation first** (`pragmatic-programmer/06`), thrown away, purely to understand the feature's real shape and interactions, before applying this lesson's disciplined sequence for the "real" implementation — useful when the feature's requirements or interactions with the legacy code are still unclear.
- **Skipping characterization tests for very low-risk, well-understood, rarely-touched code** — a pragmatic simplification of this sequence when the actual risk of the specific change is genuinely low, though this requires honest judgment, not just impatience, to apply safely.

## When to use it
Use this full sequence whenever you need to add a real feature to code with no existing tests and non-trivial risk if something breaks — which, per `legacy-code/01`'s definition, describes a large fraction of real-world legacy-code work.

## When NOT to use it
Don't apply the full, careful sequence to a trivial, extremely low-risk change where the cost of characterization testing and careful sequencing clearly exceeds the actual risk being managed — proportionality (echoing `code-complete/01`'s doghouse-vs-skyscraper framing) still matters even within this subject's own careful discipline.

## Key takeaways / mental model
When adding a feature to untested code, resist both the urge to just add it to the mess and the urge to refactor everything first — sequence it: understand the specific point of change, characterize existing behavior there, write a failing test for the new feature, implement minimally, and only then, with a safety net now in place, consider refactoring.

## Self-check questions
1. Walk through this lesson's five-step sequence using a real or hypothetical feature you'd need to add to untested code, being specific about what each step would involve.
2. Explain why adding a feature directly into unrefactored, uncharacterized legacy code is risky, using `legacy-code/01`'s change-dilemma framing.
3. Why does the book recommend deferring refactoring to an explicit, separate, later step rather than doing it alongside the feature addition?
4. Describe a case where skipping characterization tests for a "trivial" change turned out to be the wrong call, or where it was genuinely the right call. What made the difference?

## References
- Working Effectively with Legacy Code (Michael C. Feathers), Chapter 8: "How Do I Add a Feature?".
