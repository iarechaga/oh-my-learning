---
id: legacy-code/03
subject: legacy-code
title: Characterization Tests
slug: characterization-tests
status: drafted
mastery:
seniority: mid
source: Working Effectively with Legacy Code (Michael C. Feathers), Chapter 13
prerequisites: [legacy-code/02, refactoring/03]
created: 2026-08-10
updated: 2026-08-10
---

# Characterization Tests

## TL;DR
A characterization test doesn't assert what the code *should* do — it asserts what the code *actually, currently* does, discovered by running it and observing the real output, then locking that observed behavior in as the test's expected value. This is the specific technique for building a genuine safety net (per `refactoring/03`) around legacy code whose true behavior isn't fully known or trusted, without the risk of encoding your possibly-wrong assumptions instead.

## The idea
`refactoring/03` established that refactoring needs a safety net of tests verifying behavior is preserved — but for legacy code specifically, there's a subtler trap: if you write tests based on what you *believe* the code should do (reading the code, forming a mental model, then writing assertions matching that model), any place where your belief is wrong — a subtle bug nobody noticed, an edge case handled in a surprising way, a quirky behavior other code has come to silently depend on — produces a test that's *wrong in the same direction as your misunderstanding*, giving you false confidence exactly where you need real confidence most.

A **characterization test** sidesteps this trap entirely by construction: rather than deciding what the output *should* be and then checking it, you run the actual code with a specific input, observe whatever it *actually* outputs (bugs and quirks included), and write the assertion to match that observed output exactly. The test then "characterizes" — precisely describes — the code's current, real behavior, whatever that behavior happens to be, without requiring you to correctly understand or judge that behavior first.

## How it works

### The mechanical procedure
1. Pick a specific input (or set of inputs) for the piece of code you need to change.
2. Write a test that calls the code with that input, but instead of writing an assertion for what you *think* the result should be, write a placeholder that will obviously fail (e.g., `assert result == "PLACEHOLDER — REPLACE ME"`, or simply omit the assertion and print the result).
3. Run the test and observe the actual output.
4. Replace the placeholder with an assertion matching that actual, observed output.
5. Run the test again — it should now pass, because it's asserting exactly what the code already, actually does.
6. Repeat for other inputs, especially ones covering different code paths (informed by `code-complete/11`'s cyclomatic-complexity-based coverage thinking) and known or suspected edge cases.

**Worked example.**
```
# Step 2 — deliberately wrong placeholder, to force yourself to look at the real output
def test_calculate_discount_for_bulk_order():
    result = calculate_discount(quantity=150, unit_price=10)
    assert result == "PLACEHOLDER"   # will fail — that's the point, forces us to look

# Step 3 — run it, observe the actual failure message: "AssertionError: 135.0 != PLACEHOLDER"
# discovering the function returns 135.0 for this input — maybe surprising, maybe not,
# but now it's KNOWN rather than assumed.

# Step 4 — replace with the real, observed value
def test_calculate_discount_for_bulk_order():
    result = calculate_discount(quantity=150, unit_price=10)
    assert result == 135.0   # characterizes what the code ACTUALLY does today
```
If `135.0` seems surprising (perhaps you expected a 15% discount on a $1500 order to be $225 off, giving $1275, not $1365) — that surprise is valuable information, not a problem to silently "fix" mid-test-writing. It might reveal a genuine, pre-existing bug, or it might reveal a business rule you didn't previously understand (maybe the discount only applies above 200 units, and 150 gets a smaller, different rate). Either way, the characterization test's job right now is only to *lock in* the current behavior — the separate question of whether that behavior is *correct* is handled afterward, deliberately, with the "adding function" hat on (per `refactoring/01`'s two-hats distinction), not conflated with the safety-net-building step.

### Characterization tests deliberately capture bugs too — and that's the point, for now
A common, understandable objection: "should I really write a test asserting a buggy behavior is correct?" Yes, temporarily, and deliberately — the characterization test's job at this stage is purely to detect *any change* to current behavior, bug included, so that your upcoming refactoring or feature addition doesn't accidentally alter something you didn't intend to touch. Once the safety net is in place, fixing a discovered bug is a separate, deliberate activity: update the characterization test's expected value to the *correct* behavior, confirm it now fails against the current (buggy) code, then fix the code so the test passes — exactly the "write the test that would have caught this, watch it go red then green" discipline from `pragmatic-programmer/13`, now applied specifically in the legacy-code context where the bug was discovered via characterization rather than via a reported incident.

### Choosing which inputs to characterize
Since you can't feasibly characterize every possible input for anything but the simplest functions, prioritize: inputs exercising each distinct code path (informed by `code-complete/11`'s complexity metric — a cyclomatic complexity of 5 suggests at least 5 meaningfully different inputs worth characterizing), boundary values (`code-complete/13`'s boundary-testing checklist — min, max, zero, empty), and specifically the inputs relevant to the change you're actually about to make (since the goal right now is a targeted safety net for *this* change, not exhaustive documentation of the entire function's behavior for its own sake).

## Pros
- Characterization tests capture the code's *actual* behavior faithfully, without requiring you to first correctly understand or judge whether that behavior is right — sidestepping the "my test encodes my own misunderstanding" trap.
- The placeholder-then-observe procedure is mechanical and repeatable, making it approachable even for code you don't yet deeply understand.
- Provides a genuine, trustworthy safety net for legacy code specifically, resolving `legacy-code/01`'s change dilemma in a way that assumption-based test-writing cannot.

## Cons
- Characterization tests, by design, lock in bugs alongside correct behavior — if you (or a later reader) forget that a specific assertion characterizes a known bug rather than intended behavior, it can be mistaken for a real spec and inadvertently preserved longer than necessary.
- Choosing which inputs to characterize still requires judgment — a characterization suite covering only the easy, obvious inputs provides a false sense of complete safety while leaving real gaps.
- The technique requires the code to actually be *runnable* to observe its output in the first place — for code with hard dependencies (a database, a network call) that can't yet be exercised in a test environment, you may first need seam-finding and dependency-breaking (`legacy-code/02`, `legacy-code/05`) before you can even begin characterizing behavior.

## Alternatives
- **Assumption-based (specification) tests written from your understanding of intended behavior** — the standard, non-legacy-specific approach; appropriate once you're confident your understanding of intended behavior is actually correct, but risky as the *first* line of defense for genuinely unfamiliar or complex legacy code, per this lesson's central argument.
- **Golden-master / snapshot testing** — a related, often complementary technique: capture a large output (a whole rendered page, a whole API response) as a "golden" reference snapshot, and flag any future difference for review — a coarser-grained cousin of characterization testing, useful when individual, precise assertions are impractical for very complex outputs.
- **Property-based testing** (`pragmatic-programmer/13`) — asserts *general properties* rather than specific observed values, a different (not necessarily superior) approach that requires you to already know what properties genuinely must hold, which brings back some of the "requires correct understanding" risk this lesson's technique specifically avoids.

## When to use it
Use characterization tests as the default first step for building a safety net around any legacy code whose actual, current behavior isn't already fully known, trusted, and well-specified — especially before any refactoring (`refactoring/01`) or feature addition (`legacy-code/07`) that touches it.

## When NOT to use it
Don't use characterization tests as a substitute for eventually writing genuine specification tests once behavior is well-understood and confirmed correct — characterization is a bootstrapping technique for unfamiliar, untested code, not a permanent testing philosophy for code whose correct behavior you already know with confidence. Don't skip investigating a surprising characterized value — a surprise is exactly the signal worth pausing on, even if you defer fixing it to a separate step.

## Key takeaways / mental model
When you don't yet know (or trust) what a piece of legacy code actually does, don't guess and assert your guess — run it, observe what it actually does, and lock that in as your starting safety net. Investigate anything surprising you find along the way, but treat fixing it as a deliberate, separate step from building the safety net itself.

## Self-check questions
1. Walk through the placeholder-then-observe procedure on a real or hypothetical function, explaining why starting with a deliberately wrong assertion is useful rather than just guessing the right one directly.
2. Why is it acceptable, even correct, for a characterization test to assert a value that reflects a known bug? What happens to that test once the bug is later fixed?
3. Using `code-complete/11`'s cyclomatic complexity, explain how you'd decide how many and which inputs to characterize for a moderately complex function.
4. Describe a case where you couldn't write a characterization test yet because the code wasn't runnable in a test environment. What would need to happen first?

## References
- Working Effectively with Legacy Code (Michael C. Feathers), Chapter 13: "I Need to Make a Change, But I Don't Know What Tests to Write" (Characterization Tests).
- See also: `refactoring/03` (Tests as the Safety Net) for the general safety-net requirement this technique specifically satisfies for legacy code.
