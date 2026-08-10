---
id: goos/10
subject: goos
title: Managing Coupling and Avoiding Brittle Interaction Tests
slug: managing-test-coupling
status: drafted
mastery:
seniority: senior
source: Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part III/Chapter 20
prerequisites: [goos/05, goos/07]
created: 2026-08-10
updated: 2026-08-10
---

# Managing Coupling and Avoiding Brittle Interaction Tests

## TL;DR
Mock-based interaction tests (`goos/05`, `goos/07`) are powerful precisely because they couple a test to how an object talks to its collaborators — but that same coupling, applied carelessly, produces brittle tests that break on harmless refactorings, mock every collaborator instead of the ones that matter, and become more expensive to maintain than the bugs they catch. This lesson is the discipline that keeps the earlier lessons' techniques honest: mock only roles that genuinely matter to the behavior under test, and only assert on the parts of an interaction that are actually meaningful.

## The idea
`goos/05` shows mocking as a design-discovery tool; `goos/07` shows collaboration tests capturing meaningful sequences. Both techniques share a structural risk: a test that asserts on an interaction is, by construction, coupled to *how* an object accomplishes something, not just *what* it accomplishes. State-based tests ("after calling X, the object's state is Y") are naturally more resilient to internal refactoring, because they don't care how Y was reached. Interaction-based tests ("calling X causes collaborator C to receive message M") are more fragile by nature, because any legitimate internal refactoring that changes *how* X is accomplished — even while preserving its externally observable effect — can break the test, even though nothing is actually wrong.

Freeman & Pryce are explicit that this isn't a reason to avoid mock-based testing (which they clearly advocate throughout the book) — it's a reason to apply it with real discipline. Overmocking — treating every collaborator, including simple, stateless, or purely-internal helper objects, as something to mock and assert against — multiplies this fragility across the whole test suite, producing the well-known complaint that "our tests break every time we refactor, even when we didn't change behavior." That complaint is usually a sign of overmocking, not a reason to abandon interaction testing altogether.

## How it works

### Only mock roles the object genuinely depends on for its own decisions
Not every object a class touches needs to be mocked. A useful filter: mock a collaborator when the object under test needs to make a decision based on how that collaborator responds, or when the interaction with that collaborator *is* the behavior being tested (per `goos/05`'s design-discovery framing). Don't mock simple value objects, immutable data holders, or utility functions with no meaningful behavior of their own — construct and use real instances of those, the same way you'd use a real integer or string. Mocking a `Money` value object to assert its `getAmount()` was called is not testing anything useful; using a real `Money` and asserting on the resulting value is both simpler and more robust to refactoring.

**Worked example — overmocked vs. appropriately mocked.** Testing `AuctionSniper`'s response to being outbid, an overmocked version might mock the auction connection, the bid amount calculator, the UI, and a logger, asserting specific calls on all four — meaning any refactoring that changes, say, how the bid amount is computed internally (even while producing the same final bid) breaks the calculator mock's expectations, even though the sniper's actual externally-visible behavior (placing bid X) hasn't changed. An appropriately-scoped version mocks only the `Auction` collaborator (whose `bid()` call *is* the behavior under test) and uses a real, simple bid-amount calculation inline or via a real, cheap collaborator whose correctness is separately covered by its own unit tests — the sniper's test now only breaks if the actual bidding decision changes, which is exactly what should make it fail.

### Assert on what matters, not on everything that happened
Even for a collaborator that genuinely deserves to be mocked, over-specifying the assertion is its own brittleness risk. Asserting the *exact* number of times a logging call happened, or asserting on incidental parameter values that aren't actually meaningful to the behavior (e.g., a timestamp parameter whose exact value isn't being tested), ties the test to implementation detail that could reasonably change without the behavior being wrong. Freeman & Pryce's guidance: assert only on the calls and parameters that are actually part of the contract being verified, using flexible matchers (`any()`, `anyOf(...)`) for parts of an interaction that genuinely don't matter to this particular test, rather than pinning down every detail just because the mocking framework makes it easy to do so.

### Distinguish "the interaction is the behavior" from "the interaction is incidental plumbing"
A useful diagnostic question for any mock expectation: is this call *the point* of the test, or is it just something that happens to occur along the way? For `AuctionSniper` responding to being outbid, `auction.bid(1200)` is the point — that call is the entire externally meaningful behavior being verified. A call to an internal logging or metrics collaborator that happens incidentally during the same code path is plumbing — testing that it happened (and with exactly what parameters) usually adds fragility without adding meaningful protection against real bugs; if logging behavior itself matters enough to test, it deserves its own, separately scoped test, not a bolt-on assertion inside an unrelated behavioral test.

### The maintenance-cost tell: high test-to-refactor breakage ratio
A concrete, retrospective signal that a suite has drifted into overmocking: track how often tests break during refactorings that were deliberately meant to preserve behavior. If test failures during a "pure refactor, no behavior change" pass are common and have to be individually inspected and fixed just to get back to green, that's strong evidence the suite is coupled to implementation details rather than behavior — the fix is usually to go back through the suite's mocks and tighten scope to only the collaborators and calls that are genuinely part of the tested behavior's contract, per the filters above.

## Pros
- Disciplined, appropriately-scoped mocking keeps interaction tests resilient to internal refactoring while still catching genuine behavioral regressions at collaboration boundaries.
- Reduces the ongoing maintenance tax of a test suite — fewer tests break for reasons unrelated to actual bugs, which keeps trust in red failures high (a failing test is more likely to mean something real).
- Forces continual reflection on what a collaborator relationship is actually *for*, which tends to also improve production design (fewer accidental, unnecessary dependencies).

## Cons
- The judgment calls involved (which collaborators to mock, which parameters matter) require real experience and are easy to get wrong in either direction — undermocking (missing real behavioral coverage) or overmocking (fragility) are both live risks.
- Retrofitting discipline onto an already-overmocked suite is significant, unglamorous work with no new features to show for it, which can be hard to prioritize.
- Loosening assertions (using flexible matchers for "don't-care" parameters) can, if applied carelessly, accidentally hide a real bug that a stricter assertion would have caught — the loosening itself needs judgment, not blanket application.

## Alternatives
- **State-based testing wherever possible** — prefer asserting on an object's resulting state over its interactions, reserving interaction testing specifically for cases where the interaction itself is the observable behavior (no meaningful state to assert on, e.g., "did we notify the payment gateway"). Reduces brittleness risk structurally by using interaction tests only where they're genuinely the right tool.
- **Classical/detroit-school TDD** — an alternative TDD tradition (contrasted with the "London school" mocking-heavy style GOOS represents) that favors real collaborators over mocks wherever feasible, accepting somewhat slower or more complex test setup in exchange for tests inherently less coupled to implementation. A legitimate different balance point on the same trade-off this lesson discusses.
- **Contract/consumer-driven contract tests** — for cross-service boundaries specifically, formal contract tests (rather than ad hoc mocks) can pin down exactly the agreed interaction shape between two services, reducing the risk of a mock silently drifting out of sync with the real collaborator's actual behavior.

## When to use it
Apply this discipline continuously, as a habit, any time you're using mock-based interaction tests — which, given `goos/05` and `goos/07`, is throughout a GOOS-style codebase. It's especially important to revisit after a period of rapid feature growth, when test suites tend to accumulate incidental overmocking fastest.

## When NOT to use it
This isn't a technique to selectively apply or skip — it's the ongoing discipline that keeps `goos/05`'s and `goos/07`'s techniques healthy. The only real "opt-out" is choosing state-based testing over interaction testing in the first place, for collaborators where that's a better fit (see Alternatives above).

## Key takeaways / mental model
Before adding a mock expectation, ask: "is this call the actual point of the test, or incidental plumbing?" Mock and assert precisely on the former; use real objects or loose matchers for the latter. If a supposedly pure refactor keeps breaking tests, that's not the refactor's fault — go find and loosen the over-specified interaction assertions responsible.

## Self-check questions
1. Explain, using the bid-amount-calculator example, why mocking an internal calculation collaborator (rather than letting the test use a real one) makes the sniper's test more fragile without making it more correct.
2. A refactor that only renames a private method and reorders two independent internal calls breaks four tests. What does this suggest about those tests, and what specifically would you look for when fixing them?
3. Give an example of a collaborator interaction where asserting the exact call *is* the correct, intended behavior being tested (not overmocking) — and contrast it with a superficially similar case where asserting on it would be overmocking.

## References
- Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part III, Chapter 20 (or the book's mock-object discipline chapters more broadly — "the London school" of TDD and its trade-offs).
