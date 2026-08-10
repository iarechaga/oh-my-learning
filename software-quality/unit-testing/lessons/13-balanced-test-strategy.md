---
id: unit-testing/13
subject: unit-testing
title: Building a Balanced Test Strategy for a Codebase
slug: balanced-test-strategy
status: drafted
mastery:
seniority: staff
source: Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 11
prerequisites: [unit-testing/03, unit-testing/08, unit-testing/09, unit-testing/10]
created: 2026-08-10
updated: 2026-08-10
---

# Building a Balanced Test Strategy for a Codebase

## TL;DR
A healthy test suite is not one style applied uniformly — it's a deliberately shaped mix (many fast, behavior-focused unit tests; a smaller layer of integration tests at real boundaries; a very small number of end-to-end tests) chosen per code region based on that region's complexity and domain significance, with common anti-patterns (testing private methods, leaking implementation details, over-mocking, one-assertion dogma taken too far) actively guarded against as the suite grows and the team scales.

## The idea
Every lesson so far in this subject has been about the quality of an *individual* test. This closing lesson is about the shape of the *whole suite* — a question that only becomes visible at scale, and that individually-good tests don't automatically answer. A codebase can be full of well-written, behavior-focused, deterministic unit tests (per `unit-testing/01`-`unit-testing/06`) and still have a badly shaped suite overall: too much coverage on trivial code, too little on complex business rules, no integration coverage at the real boundaries, or a slow-growing infestation of anti-patterns that individually look reasonable but compound into a suite nobody trusts or wants to maintain.

Khorikov's framing for the shape question is a variant of the well-known "test pyramid": most tests should be fast unit tests, a smaller number should be integration tests at genuine system boundaries (`unit-testing/10`), and end-to-end tests should be rare, reserved for the highest-value user journeys. But the *interesting* part — and the part that requires real judgment, not a formula — is deciding, region by region within a codebase, how much test investment a given piece of code deserves at all.

## How it works

### The complexity/domain-significance matrix
Not all code is equally worth testing exhaustively. Khorikov proposes thinking about code along two axes: **complexity** (how many branches, edge cases, and non-obvious logic does it have?) and **domain significance** (how much does getting it wrong actually cost the business?).

```
                    LOW complexity          HIGH complexity
HIGH domain          Trivial but            <- Prime target:
significance         important (light         exhaustive unit
                      testing, careful         tests, most of
                      review)                  your test budget
LOW domain           Not worth much          Complicated but
significance         testing at all           low-stakes (light
                      (e.g. simple CRUD        testing, maybe
                      getters/setters)          skip if truly low-
                                                 stakes utility code)
```

- **High complexity + high domain significance** (e.g., the `OrderCalculator` discount logic used throughout this subject, tax computation, pricing rules): this is where you invest the most — exhaustive unit tests covering every branch and edge case, because both the likelihood of a bug (complexity) and the cost of one (domain significance) are high.
- **Low complexity + high domain significance** (e.g., a simple but critical configuration flag that toggles a payment feature on/off): light testing is enough because there's little logic to get wrong, but don't skip it entirely — a trivial-looking flag can still gate something expensive to get wrong.
- **High complexity + low domain significance** (e.g., an elaborate but purely cosmetic UI layout algorithm): often the least intuitive quadrant — teams frequently over-invest here because "it's complicated, so it must need lots of tests," when the actual cost of a bug is low. Light coverage, or accept some risk, is often the right call.
- **Low complexity + low domain significance** (e.g., a one-line getter, trivial glue code): usually not worth a dedicated test at all — this echoes `unit-testing/01`'s point that coverage for its own sake is not the goal.

### Worked example: allocating a testing budget across a real feature
A "checkout" feature has: (1) a discount/tax calculation engine (complex, high-stakes), (2) a `CheckoutController` orchestrating calculation, persistence, and payment (thin, per `unit-testing/11`), (3) a `PaymentGateway` integration (external boundary, per `unit-testing/10`), and (4) a `formatReceiptHtml()` utility that just interpolates values into an HTML template (simple, cosmetic).

A balanced allocation:
- **Discount/tax engine**: dozens of unit tests, one per rule and edge case (boundary discount thresholds, multiple simultaneous discounts, zero/negative-price edge cases) — this is quadrant 1, the prime target.
- **`CheckoutController`**: two or three orchestration tests per `unit-testing/11` — happy path, primary error path, one order-of-operations edge case. Not exhaustive, because the real logic lives one layer down.
- **`PaymentGateway` integration**: one or two integration tests against a sandbox (`unit-testing/10`), covering successful charge and declined-card handling — few in number, but irreplaceable, because nothing else verifies the real contract.
- **`formatReceiptHtml()`**: maybe one smoke test, or none — quadrant 4, low complexity and low domain significance (a cosmetic bug here is annoying, not costly).

A team that instead spreads its testing effort evenly across all four (say, ten tests each) has under-invested in the discount engine (where bugs are expensive and numerous edge cases exist) and over-invested in the HTML formatter (where the ceiling on both bug likelihood and bug cost is low) — the same total test count, badly allocated.

### Anti-patterns to actively guard against as the suite grows
1. **Testing private methods directly.** A private method is, by definition, an implementation detail (`unit-testing/04`) — if it's complex enough to seem to need its own tests, that's usually a sign it should be extracted into its own class with a public API, tested directly and honestly, rather than reached into via reflection tricks.
2. **Leaking domain knowledge into tests.** A test that re-implements the production discount formula inline to compute its own "expected" value (`expected = subtotal * (1 - (0.1 if type == "CORPORATE" else 0))`) isn't really testing anything — it's asserting the code agrees with a copy of itself. Prefer hardcoded expected values derived by hand from the requirement, not recomputed by mirroring the algorithm.
3. **One-assertion-per-test taken too literally.** `unit-testing/02`'s AAA discipline calls for one *behavior* per test, not literally one `assert` statement — a test checking three facets of one outcome (`order.total`, `order.status`, `order.discountApplied`, all describing the result of one `place()` call) is fine as one test; artificially splitting it into three tests each re-doing the same Arrange/Act just to have "one assertion" adds maintenance cost without adding clarity.
4. **Mystery guests** — a test that depends on data set up somewhere far away (a shared fixture file, a database seeded by a separate script) instead of visibly, locally, in its own Arrange section. Even if technically deterministic, this makes a test unreadable in isolation — you can't tell what it needs without hunting down the hidden setup.
5. **Over-mocking creeping back in under time pressure** (`unit-testing/04`, `unit-testing/08`) — the single most common way a previously well-shaped suite degrades: as deadlines tighten, developers reach for "just mock it" to get a test passing quickly, reintroducing implementation coupling one test at a time until the suite is broadly brittle again. Guarding against this is a matter of ongoing code review discipline, not a one-time fix.

### Retrofitting a strategy onto an existing, poorly tested codebase
Applying this lesson to a brand-new codebase is straightforward; applying it to an existing codebase with weak or absent tests is the more common real-world problem. The practical approach: don't try to test everything retroactively at once. Prioritize using the same complexity/domain-significance matrix — start with high-complexity, high-domain-significance code that currently has the least coverage (often exactly the riskiest code to touch without tests), applying Humble Object (`unit-testing/05`) to extract testable logic from tangled legacy code as you go, one change at a time, rather than as a separate big-bang testing initiative.

## Pros
- Concentrates limited testing effort where it actually reduces risk, instead of spreading it evenly (which under-protects the code that matters most and over-protects the code that doesn't).
- Naming specific anti-patterns gives reviewers concrete, actionable things to flag, rather than vague "this test doesn't feel right" pushback.
- Scales: the matrix and pyramid shape give new team members a shared, teachable framework for testing decisions, rather than relying on tribal knowledge or one senior engineer's intuition.

## Cons
- Requires ongoing judgment calls (what counts as "high domain significance"?) that can be genuinely contested and may shift as the business changes.
- A codebase with an already-degraded suite (widespread over-mocking, mystery guests) requires sustained, deliberate remediation effort — there's no shortcut, and it competes with feature work for time.
- The complexity/domain-significance matrix is a heuristic, not a formula; misjudging a quadrant (treating something as low-stakes when it's actually high-stakes) silently reintroduces risk.

## Alternatives
- **Uniform coverage targets** (e.g., "80% coverage everywhere") — much simpler to state and measure automatically, but per `unit-testing/01` and the worked example above, blind to where the real risk and value actually are.
- **Risk-based testing frameworks from broader QA practice** — more formal, often used in regulated industries, explicitly scoring components by failure probability and failure impact; a more rigorous cousin of this lesson's complexity/domain-significance matrix, worth adopting wholesale in high-compliance contexts.
- **Test-nothing-until-it-breaks (reactive testing)** — write a regression test only after a bug is found in a given area; cheap upfront but systematically under-invests in prevention, catching each bug only after it's already shipped once.

## When to use it
Apply this lesson whenever you're deciding, at a team or codebase level, where to invest testing effort — new feature planning, a legacy-code remediation effort, or a periodic suite health review. Use the complexity/domain-significance matrix explicitly rather than defaulting to "test everything the same amount."

## When NOT to use it
Don't use "it's low domain significance" as an excuse to skip testing code you're not actually confident is low-stakes — misjudging the matrix is a real risk, and the honest, careful version of this framework requires being skeptical of your own convenient conclusions, especially under deadline pressure.

## Key takeaways / mental model
Shape your test suite like a portfolio, not a blanket: put the most fast, exhaustive unit-test coverage where complexity and business stakes are both high; keep integration tests few and aimed precisely at real system boundaries; keep end-to-end tests rarest of all. Watch continuously for the suite's quality eroding through specific, nameable anti-patterns (private-method testing, mirrored-logic assertions, mystery guests, creeping over-mocking) rather than assuming a good suite, once built, stays good on its own.

## Self-check questions
1. Using the complexity/domain-significance matrix, classify a rate-limiting utility that's algorithmically intricate (sliding window, token bucket) but only protects an internal admin tool nobody outside the company uses. How much testing investment does this lesson suggest, and why might that feel counterintuitive?
2. A test computes its expected value with `expected = price * (1 - discountRate)`, mirroring the production formula exactly, and asserts `actual == expected`. Explain specifically what bug class this test would fail to catch, and rewrite it to avoid the "leaking domain knowledge" anti-pattern.
3. You've inherited a legacy codebase with almost no tests and a release next month. Using this lesson's retrofitting guidance, describe your first two moves — what would you prioritize testing first, and what tool from earlier in this subject would you reach for to make untestable legacy code testable?

## References
- Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 11: "Unit Testing Anti-patterns."
- See also: `refactoring/12` in the sibling `software-engineering/refactoring` subject, on incremental, evidence-driven investment versus upfront guessing — the same underlying discipline applied to test strategy here.
