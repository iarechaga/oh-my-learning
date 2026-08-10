---
id: unit-testing/12
subject: unit-testing
title: Handling Time, Randomness, and Concurrency in Tests
slug: time-randomness-concurrency
status: drafted
mastery:
seniority: senior
source: Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 6
prerequisites: [unit-testing/06]
created: 2026-08-10
updated: 2026-08-10
---

# Handling Time, Randomness, and Concurrency in Tests

## TL;DR
Anything a test can't fully control — the system clock, a random number generator, thread scheduling — must be pulled out from behind an implicit call and turned into an explicit, injectable input, so the test can pin it to a known value and get a deterministic result. Concurrency is the hardest of the three because the bug you actually care about (a race condition) is often precisely the thing that's hardest to reproduce deterministically in a test.

## The idea
`unit-testing/06` established the general principle: a unit test must be deterministic, and any hidden non-deterministic input threatens that. This lesson works through the three most common sources of hidden non-determinism in real code — time, randomness, and concurrency — because each requires a specific, slightly different technique to tame, and because getting this wrong is one of the most common reasons teams give up on testing certain classes of logic altogether ("you can't really test that, it's time-dependent" or "that's a threading thing, it's untestable").

## How it works

### Time: inject it, don't reach for it
Code that calls `DateTime.now()`, `System.currentTimeMillis()`, or equivalent, directly inside business logic makes that logic's output depend on *when the test happens to run* — which is either subtly wrong (the test's real guarantee is fuzzier than it looks) or outright flaky (a test computing a relative date near a boundary, like midnight or month-end, can fail only on certain days).

**Before (hidden dependency on the clock):**
```
class Subscription:
    def isActive(self):
        return DateTime.now() < self.expiresAt
```
**After (time becomes an explicit parameter):**
```
class Subscription:
    def isActive(self, currentTime):
        return currentTime < self.expiresAt
```
```
test "a subscription expiring tomorrow is active today":
    sub = new Subscription(expiresAt: fixedDate("2026-08-11"))
    assert sub.isActive(currentTime: fixedDate("2026-08-10")) == true

test "a subscription that expired yesterday is not active":
    sub = new Subscription(expiresAt: fixedDate("2026-08-09"))
    assert sub.isActive(currentTime: fixedDate("2026-08-10")) == false
```
Both tests now express exact, permanent guarantees, independent of when they're actually executed — a much stronger and clearer contract than "probably works, assuming you run it before the subscription actually expires."

**A common variant: an injectable clock object**, useful when passing a raw timestamp through many layers is awkward:
```
class Clock:
    def now(self): return DateTime.now()          # real implementation

class FixedClock:
    def __init__(self, fixed): self._fixed = fixed
    def now(self): return self._fixed              # test double

class Subscription:
    def __init__(self, clock):
        self._clock = clock
    def isActive(self):
        return self._clock.now() < self.expiresAt
```
This is the same idea as `unit-testing/05`'s Humble Object split applied specifically to time: the "real" clock becomes a thin, untested (or barely tested) implementation detail at the edge of the system, and every test injects a `FixedClock` instead, restoring full determinism.

### Randomness: seed it or inject it
The same pattern applies to anything using a random number generator directly:
```
class DiscountCodeGenerator:
    def generate(self):
        return "".join(random.choice(ALPHABET) for _ in range(8))
```
A test can only make weak assertions against this ("the result is 8 characters long, drawn from the alphabet") — it can never assert the *exact* value, because the value is different every run. Two fixes, appropriate in different situations:
1. **Inject a seeded random source** so the test controls exactly what "random" produces:
```
test "code generation with a fixed seed produces a specific code":
    generator = new DiscountCodeGenerator(random: SeededRandom(seed: 42))
    assert generator.generate() == "QX7B2LMK"   # deterministic given the seed
```
2. **Test the properties, not the exact value**, when the exact value genuinely doesn't matter to the requirement:
```
test "generated code is 8 characters from the allowed alphabet":
    generator = new DiscountCodeGenerator(random: SystemRandom())
    code = generator.generate()
    assert len(code) == 8
    assert all(c in ALPHABET for c in code)
```
Both are legitimate; the choice depends on whether the requirement cares about the exact output (rare) or just its properties (common). What's not legitimate is leaving `random.choice` called directly inside untestable logic with no way to control it at all.

### Concurrency: the hardest of the three
Time and randomness share a common fix (inject the non-deterministic source, pin it in the test). Concurrency doesn't have an equivalently clean fix, because the bug that actually matters — a race condition, where the outcome depends on the precise, unpredictable interleaving of two threads — is *defined* by non-determinism that's difficult to both control and to eliminate without also eliminating the concurrency itself.

**The core problem, illustrated:**
```
class Counter:
    def __init__(self):
        self._value = 0
    def increment(self):
        current = self._value      # read
        self._value = current + 1  # write — not atomic with the read!
```
Two threads calling `increment()` concurrently can interleave between the read and the write, losing an increment. A single-threaded unit test calling `increment()` twice in sequence will never observe this bug — it's structurally invisible to a test that doesn't actually introduce concurrent execution.

**Strategies, each with real limits:**
- **Test the synchronization logic directly and deterministically**, where possible, by structuring the code so the critical section is small and its correctness can be reasoned about (and tested) without needing an actual race — e.g., testing that a lock is acquired before a shared resource is touched, using the interaction-testing techniques from `unit-testing/07`/`unit-testing/08` narrowly for this purpose (this is one of the rarer cases where verifying an internal interaction is defensible, because "was the lock held during this operation" often *is* the behavior in question for concurrency-safety code).
- **Stress tests**: spin up many threads hammering the same shared object and check invariants hold afterward (e.g., a counter incremented 10,000 times by 10 threads equals exactly 10,000). This can catch real races, but a passing run is never proof of absence — it only lowers the probability a race went undetected; a failing run is a strong (though not perfectly reproducible) signal.
- **Design away the concurrency where possible**: prefer immutable data structures and message-passing/actor-style designs over shared mutable state — per this lesson's own logic, the *cheapest* way to make concurrent code testable is often to restructure it so there's less genuinely concurrent mutable state to test in the first place, echoing the general principle (seen throughout this subject) that testability problems are often, at root, design problems.
- **Accept a layer of integration/soak testing** (running the real system under realistic concurrent load for an extended period, per `unit-testing/10`'s boundary-testing spirit extended to a different kind of "environment") as a necessary complement to unit-level tests for genuinely concurrency-heavy components — unit tests alone are not expected to fully close this gap.

## Pros
- Injecting time and randomness makes previously "untestable" or flaky logic fully deterministic and precisely specifiable, at very low implementation cost.
- Makes the *contract* of time/randomness-dependent code explicit in its signature (`isActive(currentTime)` vs. `isActive()`), which is also better API design independent of testing.
- Naming concurrency's specific difficulty precisely (non-determinism is the bug, not just an obstacle to testing it) prevents teams from either ignoring concurrency risk or wasting effort chasing a "fully deterministic concurrency test" that may not be achievable.

## Cons
- Injecting a clock or random source touches every call site along the way, which can mean nontrivial refactoring in an existing codebase not designed with this in mind.
- Stress tests for concurrency are inherently probabilistic — a green stress-test run is evidence, not proof, and a team can develop false confidence from a suite that "usually" catches races.
- Some concurrency bugs only manifest under real production load patterns or specific hardware/scheduler behavior that no practical test environment reproduces reliably.

## Alternatives
- **Property-based/fuzz testing with controlled randomness** — generates many random inputs but through a seeded, reproducible generator, combining broad coverage with the ability to replay a failing case exactly; a strong complement to hand-picked example tests for both the randomness and (to a lesser extent) time-boundary cases in this lesson.
- **Formal/model checking tools for concurrency** (e.g., TLA+) — proves properties about concurrent algorithms mathematically rather than testing them empirically; far more rigorous for genuinely tricky concurrent algorithms, at the cost of a much steeper learning curve and not integrating into a typical unit-test suite.
- **Static analysis / linters for concurrency hazards** — catches some classes of races (unsynchronized shared mutable field access) at compile/lint time, before any test even runs; a useful complement, not a replacement, for runtime testing.

## When to use it
Inject time and randomness as explicit parameters or via a swappable clock/random object in any code whose logic depends on "now" or on a random draw — treat a direct call to `DateTime.now()` or `random.*` inside business logic as a code smell to fix, per the same instinct as `unit-testing/05`'s Humble Object pattern. For concurrency, invest in stress tests and design-level simplification (less shared mutable state) specifically for components where races are a real risk, and don't expect unit tests alone to fully cover that risk.

## When NOT to use it
Don't over-engineer clock/random injection for code where the actual, real-world timestamp or randomness genuinely doesn't affect correctness in any way that's worth testing (e.g., a log timestamp used purely for human debugging, not for any decision logic) — the value of injection comes from making a *decision* deterministic and testable, not from a blanket rule against ever calling `DateTime.now()` anywhere in the codebase.

## Key takeaways / mental model
If a test's outcome could plausibly differ depending on *when* or *how randomly* it happened to run, that's a sign a non-deterministic input is hiding inside the code instead of being passed in explicitly — pull it out, inject it, and pin it in the test. For concurrency, accept that unit tests alone cannot fully prove absence of races; combine deterministic tests of synchronization logic, probabilistic stress tests, and design choices that minimize shared mutable state in the first place.

## Self-check questions
1. A test asserts `assert coupon.expiresIn30Days() == expectedDate` where `expiresIn30Days()` internally calls `DateTime.now()`. Identify exactly what's wrong with this test's design and rewrite it to be fully deterministic.
2. Why can a race condition in a `Counter.increment()` method be completely invisible to a single-threaded unit test that calls `increment()` twice in a row? What kind of test would actually have a chance of catching it, and why is even that test not proof the bug doesn't exist?
3. A teammate argues "we should never call `DateTime.now()` anywhere in the codebase, full stop." Using this lesson's guidance, when would that rule be overkill, and when is the underlying instinct correct?

## References
- Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 6: "Styles of Unit Testing" (non-deterministic dependencies).
