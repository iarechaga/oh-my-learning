---
id: unit-testing/03
subject: unit-testing
title: The Four Pillars of Good Tests
slug: four-pillars
status: drafted
mastery:
seniority: senior
source: Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 4
prerequisites: [unit-testing/02]
created: 2026-08-10
updated: 2026-08-10
---

# The Four Pillars of Good Tests

## TL;DR
Every test can be scored against four properties — protection against regressions, resistance to refactoring, fast feedback, and maintainability — and no test scores perfectly on all four simultaneously; good test design is a deliberate trade-off among them, not a checklist to maximize blindly.

## The idea
"Is this a good test?" is usually answered with vague proxies: does it pass, does it raise coverage, does it look like the other tests in the file. Khorikov's central contribution is replacing "good" with four concrete, individually assessable properties, so you can point at a specific test and say precisely *why* it's weak (e.g., "it has high protection but terrible maintainability") instead of a vague unease. This framework is the evaluative backbone for the rest of the subject — `unit-testing/04` through `unit-testing/09` are all, in one way or another, techniques for improving one of these four pillars without wrecking another.

## How it works

### The four pillars, defined
1. **Protection against regressions** — how likely is this test to catch a real bug if one is introduced? Depends on the amount of code executed, the complexity of that code, and the domain significance of what's being checked. A test that exercises one trivial getter protects against almost nothing; a test that exercises a pricing engine with several branches protects against a lot.
2. **Resistance to refactoring** — how likely is this test to stay *green* through a refactor that changes the code's structure but not its observable behavior? A test that only checks observable outcomes (inputs → outputs) is resistant; a test that asserts on internal method calls or private state breaks the moment the internals change, even when nothing is actually wrong.
3. **Fast feedback** — how quickly does the test run, and how quickly does it tell you something is wrong? A test hitting a real network call might take 2 seconds; a thousand of those make the suite too slow to run on every save, which erodes the habit of running tests at all.
4. **Maintainability** — how easy is the test to understand and to keep working as the codebase legitimately evolves? Driven by test size/readability and by how many (and how complex) the collaborators it needs to set up are — a test needing an elaborate mock graph just to exercise one method is expensive to maintain even if it never fails spuriously.

### The key insight: you cannot maximize all four at once
Khorikov's illustrative claim, developed through the book: protection against regressions and resistance to refactoring together are in *tension* with fast feedback and, in a specific way, with each other's implementation strategy. Concretely:

- Maximizing **protection** pushes you toward exercising more real code and fewer test doubles — which tends to slow tests down (less **fast feedback**) and pull in more real collaborators (worse **maintainability**, since more setup is needed).
- Maximizing **resistance to refactoring** pushes you toward asserting only on observable outcomes, never on implementation details — this is nearly free to do well (see `unit-testing/04`), so it's usually not the pillar in real tension, but *violating* it (over-mocking to hit interactions) trades this pillar away in exchange for faster, more isolated tests.
- Maximizing **fast feedback** pushes you toward heavy isolation (test doubles for every collaborator) — which *reduces protection*, because a test double is by construction a stand-in that can't catch real bugs in the thing it replaces.

In practice, resistance to refactoring is treated as close to non-negotiable (a test that breaks on every harmless refactor is actively harmful — see `unit-testing/04`), which leaves the real, everyday trade-off as **protection vs. speed**, tuned per layer of the system (this is exactly what `unit-testing/13`'s test-strategy pyramid is optimizing).

### Worked example: scoring four tests for the same behavior
Behavior under test: "an `Order` with a corporate customer and a $200 subtotal has a $180 total after discount."

**Test 1 — trivial/no-op:**
```
test "discount applies":
    order = new Order(CORPORATE, 200)
    order.applyDiscount()
    assert order != null
```
Protection: near zero (asserts almost nothing). Resistance: high (nothing to break). Speed: instant. Maintainability: trivial. **Verdict: worthless** — passes forever, protects nothing.

**Test 2 — over-mocked, interaction-based:**
```
test "discount applies":
    customerMock = mock(Customer, type: CORPORATE)
    pricingServiceMock = mock(PricingService)
    order = new Order(customerMock, 200, pricingServiceMock)
    order.applyDiscount()
    verify(pricingServiceMock.getRateFor(customerMock)).wasCalledOnce()
```
Protection: moderate (does exercise something) but brittle. Resistance: **low** — any refactor of *how* the rate is fetched breaks this test even if the discount is still correctly 10%. Speed: fast. Maintainability: worse (mock setup, verify syntax). **Verdict: actively harmful** — it will produce false failures during safe refactors, training developers to distrust or ignore red tests.

**Test 3 — output-based, real objects, no doubles:**
```
test "a corporate customer with a $200 order receives a 10 percent discount":
    order = new Order(customer: Customer(CORPORATE), subtotal: 200)
    order.applyDiscount()
    assert order.total == 180
```
Protection: high (exercises the real discount calculation). Resistance: high (only checks the outcome). Speed: fast (no real I/O involved here — `Order` and `Customer` are plain in-memory objects). Maintainability: high (short, self-contained). **Verdict: this is what a good unit test looks like** — it scores well on all four because the collaborators here are simple in-memory value objects, not slow external systems.

**Test 4 — same assertion, but against a real database-backed pricing service:**
```
test "a corporate customer with a $200 order receives a 10 percent discount":
    db = realTestDatabase()
    pricingService = new PricingService(db)
    order = new Order(customer: Customer(CORPORATE), subtotal: 200, pricing: pricingService)
    order.applyDiscount()
    assert order.total == 180
```
Protection: highest (exercises real persistence logic too). Resistance: high. Speed: **much slower** (real DB connection, migrations, cleanup). Maintainability: lower (DB fixture setup/teardown). **Verdict: a legitimate integration test** (`unit-testing/10`) — more protective, but the fast-feedback and maintainability cost means you want very few of these compared to Test 3's shape.

This progression is the whole chapter in miniature: Test 1 is worthless, Test 2 is worse than worthless (false confidence plus false failures), Test 3 is the unit-test sweet spot, and Test 4 is a deliberate, expensive trade for extra protection — valuable in small numbers, ruinous if it's the norm.

## Pros
- Gives a precise vocabulary for critiquing a test ("this fails resistance to refactoring") instead of vague dissatisfaction.
- Makes trade-offs explicit and intentional rather than accidental — you can decide "this layer needs more protection, I'll accept slower tests" deliberately.
- Directly explains *why* certain popular practices (heavy mocking, testing private methods) produce brittle suites, rather than just asserting "don't do that."

## Cons
- Four independent axes make trade-off decisions genuinely harder than a single "good/bad" heuristic — there's no formula, only judgment calibrated by experience.
- Protection and speed are in real tension, and teams under deadline pressure often default to over-mocking to get speed, quietly eroding resistance to refactoring without noticing until refactors start "randomly" breaking tests.
- The framework doesn't by itself tell you *where* in a codebase to spend the protection budget — that requires domain judgment (see `unit-testing/13`).

## Alternatives
- **Code coverage as the primary metric** — cheaper to measure automatically, but (per `unit-testing/01`) doesn't distinguish Test 1 (worthless) from Test 3 (excellent) above — both hit 100% of the relevant lines.
- **Mutation testing** — automatically introduces small bugs ("mutants") into the code and checks whether tests catch them; a more rigorous, tool-driven proxy for the protection-against-regressions pillar specifically, but says nothing about resistance to refactoring or maintainability.
- **"Test everything" maximalism** — write exhaustive tests for every code path regardless of value; tends to maximize protection at severe cost to maintainability and speed, producing large slow suites that people stop running.

## When to use it
Use the four pillars as a review lens any time you're writing a new test or evaluating an existing one — especially when a test suite feels expensive to maintain or untrustworthy (frequently red for no real reason, or never catches real bugs). Ask, explicitly: which of the four does this test sacrifice, and is that trade-off the right one for this piece of code?

## When NOT to use it
Don't apply the full four-pillar analysis ceremonially to every trivial test (a one-line getter test) — the framework is most useful for judgment calls on non-trivial or contested tests, not as bureaucratic overhead on obviously-fine ones.

## Key takeaways / mental model
Score a test on four axes — protection, resistance to refactoring, speed, maintainability — and remember that resistance to refactoring is close to a hard requirement (a test that lies to you during safe refactors is worse than no test), while protection vs. speed is the real dial you tune, layer by layer, across the system.

## Self-check questions
1. A teammate proposes replacing Test 3 in the worked example (real in-memory objects) with Test 2's shape (mocked `PricingService`, verifying the call) to make the test "more isolated." Using the four pillars, argue for or against this change.
2. Why is resistance to refactoring treated as closer to non-negotiable than the protection-vs-speed trade-off? What goes wrong in a team's day-to-day workflow when a suite scores low on this pillar?
3. Think of a real test you've written or seen recently. Score it informally on all four pillars. Which pillar is weakest, and what would you change to improve it — and what would that change cost on another pillar?

## References
- Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 4: "The Four Pillars of a Good Unit Test."
