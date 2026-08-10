---
id: pragmatic-programmer/13
subject: pragmatic-programmer
title: Pragmatic Testing and Property-Based Testing
slug: pragmatic-testing
status: drafted
mastery:
seniority: mid
source: The Pragmatic Programmer (20th Anniversary ed., Hunt & Thomas), Chapter 7
prerequisites: [pragmatic-programmer/09]
created: 2026-08-10
updated: 2026-08-10
---

# Pragmatic Testing and Property-Based Testing

## TL;DR
Test to break your own code before someone else does, treat every bug found as a signal to add a test that would have caught it, and test at multiple granularities (unit, integration, resource, performance) because each level catches a different class of bug. Property-based testing generates many varied inputs to check general *properties* that must always hold, catching edge cases a human wouldn't think to write by hand.

## The idea
The book frames testing as an adversarial mindset applied to your own work: "test ruthlessly," specifically meaning try to find the input, sequence, or condition that breaks your code, rather than writing the minimum tests needed to demonstrate the happy path works. This is psychologically harder than it sounds — you just spent effort building something to work, and now you're asked to actively hunt for ways it doesn't. The payoff is that finding it yourself, before shipping, is dramatically cheaper than a user or an incident finding it for you.

Property-based testing extends this adversarial instinct with a tool: instead of you hand-picking a handful of example inputs (which reflects your own blind spots — you tend to pick examples that confirm what you already believe works), a property-based testing framework generates hundreds or thousands of varied, often weird inputs and checks that a *general property* holds for all of them, actively searching for the counterexample you didn't think of.

## How it works

### Test at the right granularity — each level catches different bugs
- **Unit tests** — a single function/class in isolation, with dependencies mocked/stubbed. Catches logic errors in that unit but nothing about how units interact.
- **Integration tests** — multiple real components wired together (e.g., a real database, not a mock). Catches contract mismatches between components that each pass their own unit tests but disagree about the shape of data they exchange.
- **Resource tests** — verifying behavior under resource constraints: what happens when the disk is full, the network is down, memory is scarce, a dependency is unreachable. Catches the class of bug that only appears when the environment misbehaves, not the code's own logic.
- **Performance / load tests** — verifying the system holds up under realistic (or worse-than-realistic) volume, not just correctness under a single request. Catches bugs that are only bugs *at scale* (an O(n²) algorithm that's invisible at n=10 and catastrophic at n=10,000).

The book's point isn't "run all of these on every change" — it's that skipping a whole category (e.g., only ever unit testing, never integration testing) leaves an entire, predictable class of bugs systematically undetected until production.

### "If it's not tested, it's broken" as an operating assumption
A deliberately blunt heuristic: treat *untested* code as *broken* code by default, not as "probably fine." This reframes the burden of proof — you don't get to assume code works because it compiles or because it looks obviously correct; you have to demonstrate it with a test, because "looks obviously correct" is exactly the confidence level at which the most embarrassing bugs slip through.

### Every bug is a missing test
When a bug is found — by QA, by a user, by an incident — the pragmatic response isn't just "fix the bug," it's "write the test that would have caught this, *then* fix the code, watch the test go from red to green." This has two payoffs: it proves the fix actually addresses the reported symptom (the test literally reproduces it), and it means that specific class of regression can never silently reappear later, because it's now permanently guarded.

**Worked example.** A bug report: "exporting a report with exactly 0 rows crashes with a division-by-zero." 
- Bad response: patch the crash (`if rows: avg = total/len(rows) else: avg = 0`), ship it, close the ticket.
- Pragmatic response: first write `test_export_with_zero_rows_does_not_crash_and_returns_zero_average()`, confirm it fails (reproducing the bug on demand), then apply the fix, confirm the test now passes, and keep the test in the suite permanently — so a future refactor that reintroduces the same edge case is caught automatically rather than shipped again.

### Property-based testing — testing what must always be true, not one example at a time
Traditional example-based tests assert specific input/output pairs: "`sort([3,1,2])` should equal `[1,2,3]`." Property-based testing instead asserts a *general property* that should hold for *any* valid input, and lets a framework (e.g., Hypothesis in Python, QuickCheck in Haskell, fast-check in JS) generate large numbers of varied inputs — including deliberately weird edge cases like empty lists, huge lists, negative numbers, duplicate values, or unicode strings — to try to violate the property.

**Worked example.** For a `sort` function, instead of (or in addition to) example-based tests, assert properties that must hold for *every* possible input:
```
property: sorted_output has the same length as input           # no elements lost or added
property: sorted_output is a permutation of input                # same multiset of elements
property: for every i, sorted_output[i] <= sorted_output[i+1]    # actually ordered
```
The framework then generates hundreds of random lists — including `[]`, `[5]`, `[3,3,3]`, lists with negative numbers, lists of 10,000 elements — and checks all three properties against each. If it finds a failing case (say, a list containing `NaN`, which breaks naive comparison-based sorts in some languages), it reports the smallest input that still fails ("shrinking"), which is often far more revealing than any example a human would have thought to hand-write, because humans systematically under-sample edge cases relative to what an automated generator finds.

## Pros
- Testing across multiple granularities catches distinct bug classes that no single level can catch alone.
- "Every bug becomes a test" converts each production incident into a permanent, compounding improvement to the test suite's coverage.
- Property-based testing finds edge cases humans reliably miss, because it doesn't share human cognitive biases about which inputs are "worth" testing.

## Cons
- Genuinely ruthless, multi-granularity testing takes real time and discipline, and is one of the first things cut under deadline pressure.
- Property-based tests require actually being able to state a *general property* — some behaviors (a specific UI layout, a specific business rule with no clean invariant) don't reduce to a checkable property easily.
- Resource and performance testing require infrastructure (staging environments, load generators) that's a real investment to build and maintain, not just "write more test functions."

## Alternatives
- **Mutation testing** — a complementary technique that deliberately introduces small bugs ("mutants") into your code and checks whether your existing test suite catches them, measuring test *quality* rather than just test *coverage* (a suite can have 100% line coverage and still catch zero mutants if assertions are weak).
- **Manual/exploratory QA testing** — a human deliberately trying to break the system through the UI/API without a scripted test plan, complementary to automated testing because humans notice usability and "this feels wrong" issues automated assertions don't check for.
- **Formal verification** — mathematically proving a program meets its specification, used in very high-assurance domains (aerospace, security-critical crypto) where the cost of a property-based test's probabilistic confidence isn't sufficient.

## When to use it
Apply ruthless testing and the "every bug is a missing test" discipline to any code with real consequences if wrong. Reach for property-based testing specifically for logic with clean, statable invariants — serialization/deserialization round-trips, sorting/searching, parsers, mathematical functions — where "for all valid inputs, X holds" is a natural, checkable statement.

## When NOT to use it
Don't force property-based testing onto code whose correctness genuinely depends on specific, hand-picked business scenarios rather than general mathematical properties (e.g., "this specific tax bracket calculation for this specific jurisdiction") — example-based tests communicate intent better there. Don't run full performance/load test suites on every trivial change if the change has no plausible performance impact — reserve that granularity for changes that could plausibly affect it.

## Key takeaways / mental model
Assume your code is broken until a test proves otherwise, at more than one granularity. And whenever you find a bug, ask "what property or example, if it had been tested, would have caught this?" — then add it, permanently, before you consider the bug actually fixed.

## Self-check questions
1. Describe a bug you've seen that a unit test wouldn't catch but an integration test would, and explain why the boundary matters.
2. Write (in prose) three general properties you'd check with property-based testing for a function that parses a date string into a `Date` object.
3. Why does "the test suite has 100% code coverage" not guarantee the tests are actually good, and what technique addresses that gap?
4. Walk through the "every bug is a missing test" loop for a real bug you've fixed, including what the test looked like before and after.

## References
- The Pragmatic Programmer, 20th Anniversary Edition (David Thomas & Andrew Hunt), Chapter 7: "While You Are Coding" (Pragmatic Testing section, with a note on Property-Based Testing).
- See also: `software-quality/unit-testing` and `software-quality/goos` for deeper treatment of test design and strategy.
