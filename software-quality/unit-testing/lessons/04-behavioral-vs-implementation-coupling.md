---
id: unit-testing/04
subject: unit-testing
title: Behavioral vs. Implementation Coupling
slug: behavioral-vs-implementation-coupling
status: drafted
mastery:
seniority: senior
source: Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 5
prerequisites: [unit-testing/03]
created: 2026-08-10
updated: 2026-08-10
---

# Behavioral vs. Implementation Coupling

## TL;DR
A test should couple itself to the *observable behavior* of the code (its public contract: given these inputs, produce these outputs/effects) and never to *how* that behavior is achieved internally. Tests coupled to implementation details break every time you refactor, even when nothing is actually broken — this single failure mode is the most common reason teams grow to distrust and ignore their test suites.

## The idea
Refactoring, by definition, changes a system's internal structure while preserving its observable behavior. A test suite's entire value proposition rests on being able to tell those two things apart: a test should turn red when behavior actually changes, and stay green when only internals change. A test coupled to implementation details cannot make that distinction — it turns red on both, producing "false failures" that have nothing to do with real bugs. Over time, false failures teach developers a corrosive habit: see a red test, assume it's noise, and either delete it or update it to match the new implementation without checking that the behavior is still correct — at which point the test has stopped protecting anything.

This is the pillar Khorikov calls **resistance to refactoring** (`unit-testing/03`), examined here in depth because it's the pillar most commonly and unknowingly sacrificed, usually via overuse of mocks that verify *interactions* rather than *outcomes*.

## How it works

### Public API vs. implementation detail
Every piece of code has an **observable behavior** (what a caller outside the class can see: return values, thrown exceptions, state changes visible through public members, calls made to *external, out-of-process* systems) and **implementation details** (private helper methods, the specific algorithm chosen, which internal collaborator gets called and in what order, private fields). A well-designed test interacts with code only through the first category.

Concretely: if a method is `private`, a test should never call it directly (most languages prevent this anyway, but the discipline matters even where reflection tricks make it technically possible). If a class delegates to an internal collaborator purely as an implementation choice (e.g., it could just as easily inline the logic), a test should not assert that the collaborator was called — it should assert on the resulting output.

### Worked example: the classic over-mocking failure
A `Order.place()` method needs to notify the customer. Implementation:
```
class Order:
    def place(self, notifier):
        self.status = PLACED
        notifier.sendConfirmation(self.customerEmail)
```
Interaction-based test (implementation-coupled):
```
test "placing an order sends a confirmation":
    notifierMock = mock(Notifier)
    order = new Order(customerEmail: "a@b.com")
    order.place(notifierMock)
    verify(notifierMock.sendConfirmation("a@b.com")).wasCalledOnce()
```
This test passes today. Now a developer refactors: instead of calling the notifier synchronously inside `place()`, they switch to raising a domain event (`OrderPlaced`) that a separate event handler picks up and turns into a notification — a cleaner design, and the *customer still gets the exact same email*. The refactor changes nothing a user of the system can observe. But the test above breaks immediately, because `sendConfirmation` is never called directly from `place()` anymore. The test has just lied: it reported a regression where there was none.

An output/state-based test avoids this:
```
test "placing an order marks it as placed":
    order = new Order(customerEmail: "a@b.com")
    order.place()
    assert order.status == PLACED
```
plus, separately, a test at the boundary that confirms notifications actually go out (see `unit-testing/10` for how to test that boundary without re-coupling to internals). Neither of these breaks when the internal delivery mechanism changes, because neither one cares *how* the confirmation happens — only that placing the order leaves it `PLACED`, and (verified elsewhere, at the seam where it actually matters) that a confirmation is eventually sent.

### The exception: mocking a true external dependency is still behavior
This isn't "never verify a call" — it's "never verify a call to something that's purely an internal implementation choice." If `Notifier` wraps a real external system (an email provider), and the *actual requirement* is "the system must call the email provider," then asserting that call happened is verifying real observable behavior — from the outside world's perspective, "did an email get sent" is exactly the behavior in question. The distinguishing question, developed further in `unit-testing/08`, is: **is this collaborator a true external dependency (I/O, another service, uncontrolled volatility) or an internal implementation detail I chose to factor out?** Mock the former when appropriate; never assert interactions with the latter.

### Worked example: two refactors, one good test
Take the $200 corporate-discount test from `unit-testing/03`:
```
test "a corporate customer with a $200 order receives a 10 percent discount":
    order = new Order(customer: Customer(CORPORATE), subtotal: 200)
    order.applyDiscount()
    assert order.total == 180
```
Now apply two different refactors to the discount logic:

1. **Refactor A** — extract the rate lookup into a private helper `_rateFor(customerType)` inside `Order`. The test still passes untouched, because it never referenced `_rateFor`.
2. **Refactor B** — replace the `if/else` discount logic with a lookup table (`DISCOUNT_RATES = {CORPORATE: 0.1, RETAIL: 0.0}`). The test still passes untouched, because it never asserted *how* the rate was determined, only the resulting total.

Both refactors are safe, verified-safe changes precisely because the test only touches the public contract (construct an `Order`, call `applyDiscount()`, read `total`).

### A litmus test you can apply to any assertion
Ask: "if I changed *only* the internal implementation, keeping the input/output contract identical, would this assertion still hold?" If the answer is "no, because I'm checking a private method got called, a specific internal object was constructed, or a particular algorithm ran" — that assertion is implementation-coupled and should be removed or rewritten against the observable outcome instead.

## Pros
- Tests survive legitimate refactors, which is the entire point of having them alongside a refactoring practice (see `refactoring/01` in the sibling refactoring subject for the code-quality side of this same coin).
- Reduces false failures, which preserves developer trust in "red means something is actually broken."
- Tests end up documenting *what* the system promises, which is more durable and more useful to a reader than documenting *how* it currently happens to be implemented.

## Cons
- Requires real discipline to identify what's "observable" vs. "internal," especially in codebases with fuzzy boundaries or classes that expose too much internal state through public getters (which then makes almost everything look "observable").
- Sometimes there genuinely is no way to observe an outcome except by checking that a call happened (e.g., a fire-and-forget side effect with no return value and no state change) — this is a real, if narrower, use case for interaction testing, covered precisely in `unit-testing/08`.
- Retrofitting this discipline onto an existing, heavily mock-based suite is expensive — it often means rewriting large numbers of tests, not just tweaking them.

## Alternatives
- **Interaction/mock-based testing as the default style** — the "London school" approach (`unit-testing/09`) leans on this more heavily by design and has its own coherent rationale (verifying an object correctly orchestrates its collaborators); it's not "wrong," but it requires much stricter discipline about which interactions are worth verifying to avoid the brittleness shown above.
- **Snapshot/golden-master testing** — captures the entire output of a function and diffs future runs against a saved snapshot; behaviorally-coupled almost by construction (it only cares about output), but can be too coarse-grained to give a precise failure message.
- **Property-based testing** — asserts general properties across many generated inputs ("total is always non-negative") instead of one hand-picked example; inherently behavior-focused, and a strong complement to example-based tests for catching edge cases a human wouldn't think to write by hand.

## When to use it
Apply this discipline to every unit test you write: assert on return values, thrown exceptions, and state changes visible through the public API. Treat any assertion on a private member or an internal-only collaborator call as a smell to be justified or removed.

## When NOT to use it
The one carve-out is verifying calls to genuine external dependencies where the call *is* the requirement (e.g., "an order confirmation email must be sent") — see `unit-testing/08` for exactly how to do that without sliding back into over-mocking every collaborator.

## Key takeaways / mental model
Ask "would this assertion survive a refactor that keeps behavior identical but changes internals?" before writing it. If not, you're testing implementation, not behavior — and the test will eventually cry wolf.

## Self-check questions
1. Take the `Order.place()` interaction-based test in this lesson and explain, step by step, why it breaks under the event-based refactor even though no bug was introduced. What specific assertion is the culprit?
2. Give an example (different from the ones in this lesson) of a collaborator call that IS legitimate to verify via a mock, and explain what makes it different from an internal implementation detail.
3. A test asserts `order._internalDiscountCache.size == 1` after calling a public method. Classify this assertion and predict what will happen to this test the next time someone removes the caching optimization without changing observable behavior.

## References
- Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 5: "Mocks and Test Fragility."
- See also: `refactoring/01` (What refactoring preserves) in the sibling `software-engineering/refactoring` subject.
