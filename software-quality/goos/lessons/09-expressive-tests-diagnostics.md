---
id: goos/09
subject: goos
title: Keeping Tests Expressive and Diagnosing Failures
slug: expressive-tests-diagnostics
status: drafted
mastery:
seniority: senior
source: Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part III/Chapter 11
prerequisites: [goos/05]
created: 2026-08-10
updated: 2026-08-10
---

# Keeping Tests Expressive and Diagnosing Failures

## TL;DR
A test suite's long-term value depends less on how many tests exist than on how quickly a failing test tells you *what* is wrong — treat test readability and diagnostic quality as first-class design goals, not afterthoughts, using techniques like custom matchers, builder-style test data construction, and intention-revealing names to keep tests reading as a clear specification of behavior rather than a wall of low-level setup and assertion noise.

## The idea
`goos/01` sells TDD on the promise of fast feedback, but that promise quietly assumes something else: that when a test fails, you can tell *why* quickly. A test suite that runs fast but produces cryptic, low-level failure messages ("expected `<AuctionSniper@4a3f2e>` but was `<AuctionSniper@1b9c30>`") doesn't actually deliver fast feedback — it delivers a fast "something's wrong" signal followed by a slow manual investigation, which is a big part of the loop `goos/01` set out to eliminate. Freeman & Pryce treat **listening to your tests** as an ongoing discipline: when a test is hard to write, hard to read, or produces an unhelpful failure message, that's diagnostic information about the *production code's* design, not just an annoyance to work around in the test.

Two separate but related concerns fall out of this: (1) tests should read clearly, as a specification a new team member could understand without archaeology, and (2) when a test fails, its output should point directly at the specific, meaningful difference between expected and actual behavior — not force the reader to reconstruct that difference by hand.

## How it works

### Test readability: tests as executable specification
A test's job is not only to catch regressions but to document, in a form that stays true because it's checked by the computer, what the system is actually supposed to do. Freeman & Pryce advocate structuring tests so that a reader can understand *the scenario being tested* at a glance, before getting into implementation-level details. Concretely, this often means:

- **Given/When/Then-shaped structure** (even without a BDD framework): clearly separate "set up the starting state," "perform the action," and "check the outcome" — visually or via comments/blank lines — rather than interleaving them.
- **Test data builders** for constructing realistic-but-simplified objects, so a test doesn't drown in boilerplate setup unrelated to what it's actually checking. Instead of manually constructing a fully-populated `Auction` object with a dozen irrelevant fields for a test that cares about exactly one, a builder (`anAuction().withCurrentPrice(122).build()`) lets the test state only what matters, defaulting everything else sensibly.
- **Intention-revealing test names** — `bidsHigherWhenNewPriceArrivesAndOutbid()` communicates the scenario directly; `test3()` or `testBid()` doesn't. A good test name should let someone reading a failure report understand roughly what broke without opening the test body at all.

**Worked example — before and after.** A poorly-structured test:
```
@Test
public void test1() {
    Auction a = new Auction("item1", 100, 10, "server", "user", "pass", true, false, null);
    AuctionSniper s = new AuctionSniper(a);
    s.currentPrice(100, 10);
    assertTrue(s.getState() == 2);
}
```
This buries the scenario (an outbid sniper should respond by bidding) under irrelevant construction noise (most of those `Auction` constructor arguments are unrelated to this test) and an opaque assertion (`state == 2` requires knowing what state `2` means). Restructured using a builder and an intention-revealing comparison:
```
@Test
public void bidsHigherWhenOutbidBelowStopPrice() {
    Auction auction = anAuction().withCurrentPrice(100).withIncrement(10).build();
    AuctionSniper sniper = new AuctionSniper(auction);

    sniper.currentPrice(100, 10);

    assertThat(sniper.getState(), is(SniperState.BIDDING));
}
```
The second version reads almost like a sentence describing the behavior, and a failure message ("expected BIDDING but was LOSING") is immediately meaningful without needing to decode a magic number.

### Diagnostics: a failing test should point at the actual difference
Beyond readability at write-time, Freeman & Pryce emphasize what happens the moment a test fails. A generic `assertTrue(condition)` failure tells you only that *some* condition was false — it doesn't say what was expected or what was actually observed, forcing whoever's debugging to add print statements or step through a debugger just to see what the real values were. Freeman & Pryce (and the broader xUnit tradition, see `xunit-test-patterns` if authored) advocate using assertion styles and **custom matchers** that report the specific expected-vs-actual difference automatically: `assertThat(sniper.getState(), is(SniperState.WINNING))` fails with `"Expected: WINNING, got: LOSING"` — the diagnosis is right there in the failure output, with zero additional investigation needed.

For complex domain objects, this often means writing a small custom matcher (e.g., a Hamcrest matcher for comparing `Auction` snapshots) that reports precisely which field differed, rather than relying on a generic `equals()`-based comparison that just says "not equal" without saying *how*. The investment in writing that matcher once pays off every time a related test fails afterward.

### Listening to a test that's hard to write
The subtler, more important half of this lesson: when a test is awkward to write — requiring elaborate setup, multiple unrelated collaborators mocked just to reach the one behavior you actually want to check, or an assertion that has to dig through several layers of an object graph — treat that difficulty as a signal about the *production* design, not a testing inconvenience to push through with more test helper code. A class that's hard to test in isolation is very often a class with too many responsibilities or too many entangled collaborators (a design smell independent of testing, but one testing surfaces early and concretely). Freeman & Pryce's guidance: when a test resists being written cleanly, stop and ask whether the object under test needs to be split or its dependencies reduced, rather than reaching immediately for a more powerful mocking framework to force the ugly test through.

**Worked example.** Suppose testing `AuctionSniper.currentPrice(...)` requires setting up a mock UI, a mock auction connection, a mock persistence layer, and a mock logger, even though the test only cares about the sniper's bidding decision. That excess of required setup is a strong signal `AuctionSniper` has taken on responsibilities (UI updates, persistence, logging) that belong in separate, more narrowly-focused collaborators — splitting them out (each with its own narrow, easily-mocked role per `goos/05`) both simplifies the test and improves the design independently.

## Pros
- A failing test that clearly states what was expected vs. observed collapses the "found a bug" to "understood the bug" gap from minutes to seconds, directly serving `goos/01`'s fast-feedback goal.
- Readable tests double as living documentation of intended behavior, valuable to new team members long after the original author has moved on.
- Treating awkward-to-write tests as design feedback catches responsibility-overload and poor decomposition early, often before it becomes expensive to fix.

## Cons
- Investing in test readability infrastructure (builders, custom matchers) is real upfront work that doesn't pay off on a single test — it pays off across many tests over time, which can be a hard sell under short-term delivery pressure.
- Over-engineering test helpers (an overly clever builder DSL, matchers for things that will only ever be asserted once) can itself become a maintenance burden — apply this investment where it will actually be reused.
- "Listening to a hard-to-write test" requires judgment; sometimes a test is genuinely just testing a legitimately complex scenario, not signaling a design flaw, and over-applying this heuristic can lead to over-splitting classes that didn't need it.

## Alternatives
- **Minimal, low-level tests with default assertion messages** — fastest to write in the moment, but pushes diagnostic cost onto every future failure, repeatedly, rather than paying it once at write-time — usually a false economy over a codebase's life.
- **Behavior-Driven Development (BDD) frameworks** (Cucumber, SpecFlow, etc.) — push test readability further by expressing scenarios in structured natural language, readable by non-programmers. More ceremony and indirection than GOOS's plain-code approach, worthwhile mainly when non-technical stakeholders genuinely need to read the specifications directly.
- **Snapshot/golden-file testing** — compare a large actual output against a stored expected output wholesale. Fast to set up for complex outputs, but tends to produce exactly the vague, hard-to-diagnose failures this lesson warns against ("output differs") unless paired with good diffing tools.

## When to use it
Invest in expressive tests and diagnostic assertions in any codebase intended to live and be maintained by more than one person over more than a few weeks — which is most real software. The payoff compounds: the same investment (a builder, a matcher) benefits every test that reuses it, for the life of the codebase.

## When NOT to use it
For genuinely disposable, short-lived scripts or one-off spikes (per `goos/01`'s "don't force TDD onto throwaway code"), investing in test readability infrastructure is wasted effort — there's no long "life of the codebase" over which the investment pays back.

## Key takeaways / mental model
Ask two questions of every test: "if this fails at 2am, will the failure message alone tell the on-call engineer what's wrong?" and "if this test is painful to write, what is that pain telling me about the code I'm testing?" The first question drives investment in matchers and clear assertions; the second turns testing friction into a design tool rather than a nuisance.

## Self-check questions
1. Rewrite (in words, not code) why `assertTrue(sniper.getState() == 2)` is worse than `assertThat(sniper.getState(), is(SniperState.WINNING))`, focused specifically on what happens when the test fails, not when it passes.
2. A test for `OrderProcessor` requires mocking six different collaborators to test one pricing rule. Using this lesson's framing, what should you investigate before writing a seventh helper to make the mocking easier?
3. Describe a genuine, appropriate use of a custom matcher in a codebase you're familiar with (or invent a plausible one), and explain what it would report on failure that a generic equality check would not.

## References
- Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part III, Chapter 11: "Test Readability" and Chapter 12: "Test Diagnostics."
