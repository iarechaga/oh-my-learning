---
id: unit-testing/01
subject: unit-testing
title: What a Unit Test Is and Why It Matters
slug: what-a-unit-test-is
status: drafted
mastery:
seniority: junior
source: Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 1
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# What a Unit Test Is and Why It Matters

## TL;DR
A unit test verifies a small piece of behavior, runs fast, and runs in isolation from other tests; its real purpose is not "coverage" but *protecting the codebase against regressions while keeping change cheap*. Tests are code too — they must be evaluated for their return on investment, not written to hit a percentage.

## The idea
Every non-trivial codebase changes constantly: features get added, bugs get fixed, code gets restructured. Every change risks breaking something that used to work. Manual re-verification ("click through the app and check nothing broke") does not scale — it is slow, easy to skip under deadline pressure, and does not cover the parts of the system nobody remembers to click. A unit test is an automated, repeatable check that a specific piece of behavior still works, written once and re-run for free on every future change.

The word "unit" historically meant "a single class" or "a single method," tested completely on its own with every collaborator replaced by a test double. Khorikov's book pushes back on that definition (this is explored fully in `unit-testing/09`, London vs. classical schools). For now, the working definition that matters is functional, not structural:

A unit test is a piece of code that:
1. Verifies a small piece of the system's **behavior** (not necessarily a single class or method),
2. Does so **quickly** (milliseconds, not seconds — thousands of these should run in seconds),
3. Runs **in isolation** from other tests — no shared mutable state, no dependency on execution order, and (in the classical view) no dependency on out-of-process collaborators like a real database or network call.

If any of these three properties is missing, what you have is still a valuable test — but it isn't a *unit* test. A test that hits a real database is an **integration test** (covered in `unit-testing/10`). A test that drives a browser end-to-end is an **end-to-end test**. All of these have a place; the point of naming them precisely is that they have different speed, isolation, and reliability trade-offs, and a healthy test suite needs the right *mix*, not maximum coverage from one type.

## How it works

### The core motivation: change is the thing being protected
Imagine a `ShoppingCart` class that computes a total price, applying a 10% discount once the cart exceeds $100. Without tests, every time someone touches the discount logic (say, changing the threshold to $150, or adding a second discount tier), the only way to know if the existing behavior still holds is to trace through the code by hand or manually exercise the app. A unit test that says "a $120 cart gets a 10% discount" runs automatically after every change and immediately tells you if that behavior broke — in milliseconds, without a human in the loop.

This is why Khorikov frames unit testing as risk management for the *codebase's ability to evolve*, not as a checkbox. A codebase with a strong test suite can be refactored aggressively and features can be added quickly, because regressions are caught immediately. A codebase with no tests (or with a suite nobody trusts) makes every change scary, because nobody knows what might break.

### Worked example: same behavior, two very different "tests"
Suppose the requirement is: "an order with a corporate customer gets a 10% discount." Two ways to test this:

**Test A (verifies the actual behavior):**
```
test "corporate customer receives a 10 percent discount":
    order = new Order(customer: CORPORATE, subtotal: 200)
    order.applyDiscount()
    assert order.total == 180
```

**Test B (verifies an implementation detail):**
```
test "applyDiscount calls getDiscountRate on the customer":
    customerMock = mock(Customer)
    order = new Order(customer: customerMock, subtotal: 200)
    order.applyDiscount()
    verify(customerMock.getDiscountRate()).wasCalledOnce()
```

Both tests pass today. But Test B is coupled to *how* the discount is computed, not *what* the discount is. If a developer refactors `applyDiscount` tomorrow to compute the rate differently (say, by looking up a `DiscountPolicy` table instead of calling `getDiscountRate()` directly) — a refactor that changes nothing about observable behavior — Test B breaks even though nothing is actually wrong. Test A keeps passing, because it only cares about the observable outcome (`total == 180`). This distinction — testing *what* vs. testing *how* — is the seed of `unit-testing/04` (behavioral vs. implementation coupling) and the single most important idea in the whole book. It is introduced here because it is the difference between a test that earns its keep and one that becomes a maintenance tax.

### The three properties, applied to a concrete test
Take this test for a `PasswordValidator`:
```
test "password shorter than 8 characters is rejected":
    validator = new PasswordValidator()
    result = validator.validate("abc123")
    assert result.isValid == false
    assert result.error == "TOO_SHORT"
```
- **Small piece of behavior**: it checks exactly one rule (minimum length), not the whole validator.
- **Fast**: no I/O, no sleeping, no network — this runs in microseconds.
- **Isolated**: no shared state with other tests; running it alone or in a suite of 10,000 tests in any order gives the same result.

Compare that to a test that spins up a real web server, submits a signup form through HTTP, and checks the database row afterward. That test might be *valuable*, but it's not a unit test — it's slow (seconds, not milliseconds) and it depends on external infrastructure being up. Neither test is "better" in the abstract; they answer different questions at different costs. A healthy suite has many of the first kind and comparatively few of the second (this ratio is the subject of `unit-testing/13`).

### Why "coverage" is a bad primary goal
A tempting but misleading proxy metric is code coverage: "80% of lines are exercised by tests." Coverage measures whether a line *executed* during a test run, not whether the test would *catch a bug* in that line. A test that calls a method and asserts nothing (or asserts something trivially true) inflates coverage while providing zero protection. Khorikov's framing, developed fully in `unit-testing/03`, is that a test's value is measured by how well it protects against regressions and how cheap it is to maintain — coverage is, at best, a weak proxy for the first of those and says nothing about the second.

## Pros
- Automated regression protection: bugs reintroduced by later changes are caught in seconds, not discovered in production.
- Fast feedback loop enables confident, frequent refactoring and rapid iteration.
- Executable documentation: a well-named test describing "corporate customer receives a 10 percent discount" tells a reader what the system does without reading the implementation.

## Cons
- Tests are code: they must be written, read, and maintained, and a badly designed test suite becomes a drag on velocity rather than an aid to it.
- Poorly written tests (testing implementation details, over-mocking) can actively resist refactoring, punishing exactly the kind of change they should be enabling.
- Writing tests takes real upfront time that is easy to skip under deadline pressure, even though the cost is usually repaid many times over.

## Alternatives
- **Manual QA / exploratory testing** — a human clicks through the app; catches things automated tests miss (visual glitches, "does this feel right") but does not scale, is not repeatable, and is far slower per check.
- **Integration and end-to-end tests as the primary safety net** — trades unit tests' speed and isolation for closer-to-production realism; valuable at system boundaries (`unit-testing/10`) but too slow and brittle to be the *bulk* of a suite.
- **Static typing / type checkers** — catches a real but narrow class of bugs (wrong types) at compile time for free, but says nothing about business-rule correctness (a well-typed function can still compute the wrong discount).

## When to use it
Reach for a unit test whenever you are encoding a piece of business logic, a calculation, a validation rule, or a decision — anything where "what should this produce given this input" has a clear, checkable answer. This is the default, cheapest form of automated regression protection and should be the bulk of any test suite.

## When NOT to use it
Don't use a unit test (in isolation) to verify behavior that only makes sense in combination with a real collaborator — e.g., "does this SQL query actually retrieve the right row from a real database schema." That question needs an integration test (`unit-testing/10`). Also don't write a unit test purely to move a coverage number; a test with no meaningful assertion, or one that only re-states the implementation, adds maintenance cost without adding protection.

## Key takeaways / mental model
A unit test is not defined by "tests one class" — it's defined by three properties: small behavior, fast, isolated. Its purpose is protecting the codebase against regressions cheaply, so treat every test as an investment: ask "does this test protect me from a real bug, and is it cheap to keep?" before asking "does this raise coverage?"

## Self-check questions
1. A colleague writes a test that mocks every collaborator of the class under test and asserts that each mock method was called with the right arguments, but never asserts on any return value or observable output. Using this lesson's framing, what is missing from that test, and what could go wrong later because of it?
2. Your team currently has 95% code coverage but ships regressions every other release. Given this lesson, what question would you ask about the *existing* tests before writing more?
3. Give an example of a test that is fast and isolated but is NOT testing a "unit" in the classical sense described here — what would make it fail one of the three properties?

## References
- Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 1: "The Goal of Unit Testing."
