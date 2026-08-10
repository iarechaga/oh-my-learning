---
id: unit-testing/06
subject: unit-testing
title: Shared State, Isolation, and Deterministic Tests
slug: isolation-and-determinism
status: drafted
mastery:
seniority: mid
source: Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 6
prerequisites: [unit-testing/01]
created: 2026-08-10
updated: 2026-08-10
---

# Shared State, Isolation, and Deterministic Tests

## TL;DR
A test must produce the same result regardless of which other tests ran before it, in what order, or in parallel — this requires eliminating shared mutable state between tests (in-process statics/singletons, and out-of-process shared fixtures like a shared database row) and eliminating hidden non-determinism (system clock, randomness, unordered collections used where order matters). A test suite that only passes "most of the time" or "in the right order" is not a safety net — it's a source of noise.

## The idea
The entire value of automated tests rests on a test's result meaning something: red means a real problem, green means real confidence. If a test's outcome depends on incidental factors — which tests ran before it, what order the suite executes in, what the wall-clock time happens to be, what a random number generator produced — its result stops being trustworthy. A "flaky" test (one that sometimes passes, sometimes fails, with no code change in between) is worse than no test at all, because it trains the team to re-run failures without investigating them, which lets *real* regressions hide behind "oh, that test is just flaky."

Isolation here operates at two levels: isolation between tests (no test should be able to affect another) and isolation from non-determinism (no test should depend on unpredictable inputs it doesn't explicitly control).

## How it works

### Shared state between tests, in-process
The most common source of test interdependence is a shared mutable object that outlives a single test — typically a static/global variable, a singleton, or a shared fixture object reused (not recreated) across tests.

```
class OrderIdGenerator:
    _counter = 0                      # class-level, shared across all instances
    @staticmethod
    def next():
        OrderIdGenerator._counter += 1
        return OrderIdGenerator._counter

test "first order gets id 1":
    assert OrderIdGenerator.next() == 1     # passes if run FIRST, fails otherwise

test "second call increments":
    OrderIdGenerator.next()
    assert OrderIdGenerator.next() == 3     # depends on exactly how many calls happened before
```
Run these two tests in isolation, each passes. Run them together, or in a different order, or introduce a third test that also calls `next()`, and the assertions start failing unpredictably — not because of a bug, but because `_counter` is shared, mutable state that leaks across test boundaries. The fix is to make the counter's lifetime match the test's lifetime: reset it in a setup hook before every test, or (better) avoid the static entirely and inject a fresh generator instance per test:
```
test "first call to a fresh generator returns 1":
    generator = new OrderIdGenerator()      # new instance, not shared
    assert generator.next() == 1
```
Now each test owns its own generator; order and count of other tests become irrelevant.

### Shared state between tests, out-of-process
The same problem shows up, often worse, with external resources like a shared test database. If two tests both insert a row with the same hardcoded primary key, or both assume the `orders` table starts empty, running them in the same suite run (or in parallel) produces order-dependent or intermittent failures — a unique-constraint violation in one run, a stale row breaking an assertion in the next. This is a central concern of integration testing (`unit-testing/10`), which covers concrete techniques (per-test transactions rolled back at the end, unique generated IDs, dedicated test schemas) — but the underlying principle is the same one from this lesson: every test must start from a known, isolated state, and must not leave state behind for the next test to trip over.

### Non-determinism: the system clock
```
class Coupon:
    def isExpired(self):
        return DateTime.now() > self.expiryDate

test "a coupon expiring tomorrow is not expired":
    coupon = new Coupon(expiryDate: DateTime.now() + days(1))
    assert coupon.isExpired() == false
```
This test happens to pass today, but it's fragile in a subtler way: it's asserting something true *relative to whenever the test happens to run*, which makes the test's actual guarantee fuzzy, and it becomes outright broken if `expiryDate` is ever a fixed calendar date instead of relative to "now" (a classic bug: a test using `DateTime.now() + days(1)` passes every day until, say, a leap-year edge case or timezone boundary breaks it once a year). The fix, per `unit-testing/12` (which covers this fully), is to inject the "current time" as an explicit, controlled input rather than letting the code reach out to the real clock:
```
test "a coupon is not expired the day before its expiry date":
    coupon = new Coupon(expiryDate: fixedDate("2026-08-15"))
    assert coupon.isExpired(currentTime: fixedDate("2026-08-14")) == false
```
Now the test's outcome is fully determined by its inputs, forever, regardless of when it's actually executed.

### Non-determinism: randomness
Code using `Random()` directly inside logic under test has the same problem — a test asserting on a randomly generated value either has to accept a wide, weak assertion ("the value is between 0 and 100") or becomes literally impossible to write precisely. The fix, again, is dependency injection: pass a seeded (or fixed, or fake) random source into the code so the test controls exactly what "random" produces during that run — this is developed alongside the time-control techniques in `unit-testing/12`.

### Non-determinism: unordered collections
A subtler source: iterating over a hash-based collection (a set, or a dictionary in languages without insertion-order guarantees) and asserting on the resulting order. If the underlying implementation doesn't guarantee order, a test asserting `result == [1, 2, 3]` might pass on one platform/runtime version and fail on another, or even vary run to run. The fix is either to assert on an order-independent property (`assert set(result) == {1, 2, 3}`) or to use an explicitly ordered structure when order genuinely matters to the behavior being tested.

## Pros
- Deterministic, isolated tests can run in any order, in parallel, and give the same answer every time — a prerequisite for fast, trustworthy CI.
- Eliminates an entire class of maddening, hard-to-reproduce bugs in the test suite itself ("it fails on CI but not locally," "it fails only on Tuesdays").
- Makes root-causing a real failure much faster, because you can rule out "maybe it's just flaky" and trust that red means red.

## Cons
- Requires discipline to avoid convenient shortcuts (a shared test database fixture, a cached singleton) that are genuinely faster to set up initially.
- Retrofitting isolation onto an existing suite with entangled shared state can be a significant undertaking.
- Some non-determinism (true concurrency bugs, per `unit-testing/12`) can't be fully eliminated from a test, only made rare enough to manage deliberately, which requires a different, explicit strategy.

## Alternatives
- **Tolerate flakiness and retry failed tests automatically** — a common but risky band-aid; hides real intermittent bugs behind automatic retries and erodes the "red means broken" signal this lesson is protecting.
- **Force serial, fixed-order test execution** — sidesteps ordering issues by never running tests in a different order or in parallel, but sacrifices speed (no parallelism) and doesn't fix the underlying shared-state problem, which can still bite in production-like concurrent scenarios.
- **Full environment reset per test (fresh container/process)** — the most bulletproof isolation, commonly used for integration tests (`unit-testing/10`), but far too slow to apply to every unit test.

## When to use it
Design every unit test, from the start, to construct its own fresh state and control every non-deterministic input explicitly (time, randomness). Treat any static/global/singleton touched by code under test as a red flag requiring either a reset-per-test hook or, preferably, replacement with per-test dependency injection.

## When NOT to use it
There's no real "opt out" of determinism for unit tests — a unit test that isn't deterministic has, by this subject's definition (`unit-testing/01`), stopped being a reliable unit test. The one place where full isolation is relaxed by necessity is at integration boundaries (`unit-testing/10`), where techniques like transactional rollback replace full determinism with "isolated enough, deliberately."

## Key takeaways / mental model
Ask of every test: "if I ran this alone, in a random order with 500 other tests, or in parallel, would I get the same result?" If the honest answer involves "usually" or "as long as X ran first," that test has a hidden dependency — find it and eliminate it before it costs someone a debugging afternoon.

## Self-check questions
1. A test suite passes reliably when run test-by-test but fails intermittently when run in parallel. What are the first two things you'd look for, based on this lesson?
2. Rewrite this test to remove its hidden non-determinism: `test "shuffled deck has 52 cards": deck = new Deck(); deck.shuffle(); assert deck.cards[0] != deck.cards[1]`. What's actually wrong with the assertion, independent of the shuffle itself?
3. Why is a flaky test arguably worse than having no test for that behavior at all? Connect your answer to what happens to a team's trust in "red" over time.

## References
- Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 6: "Styles of Unit Testing" (isolation discussion) and Chapter 3 (shared test fixtures).
