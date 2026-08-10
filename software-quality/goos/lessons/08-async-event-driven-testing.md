---
id: goos/08
subject: goos
title: Testing Asynchronous and Event-Driven Behavior
slug: async-event-driven-testing
status: drafted
mastery:
seniority: senior
source: Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part II/Chapter 9
prerequisites: [goos/06]
created: 2026-08-10
updated: 2026-08-10
---

# Testing Asynchronous and Event-Driven Behavior

## TL;DR
Asynchronous systems break the simple "call a method, assert on the immediate result" testing model, because the effect a test cares about happens on a different thread, in a different process, or after an unpredictable delay. Freeman & Pryce's approach is to make the asynchrony explicit at the test boundary — using a small, well-understood polling or event-waiting utility to observe eventual outcomes reliably — rather than either ignoring timing (producing flaky tests) or testing only the synchronous internals and skipping the real asynchronous seam entirely.

## The idea
The auction sniper is inherently asynchronous: it receives price and close events over a network connection at unpredictable times, updates its own state, sends bid requests asynchronously, and updates a UI — none of which happens as a single synchronous call-and-return the way the pure domain logic tests in `goos/05` and `goos/07` do. A naive acceptance test written as if this were synchronous ("send an event, immediately assert the UI shows the new state") will be **flaky**: it might pass most of the time and fail intermittently, because the UI update genuinely hasn't happened yet at the moment the assertion runs — not because the code is wrong, but because the test made a false assumption about timing.

Freeman & Pryce's answer is neither to accept flaky tests as an inevitable cost of testing async systems, nor to avoid testing the async boundary altogether and only test the synchronous domain logic underneath it (which would leave the actual integration — the part most likely to have real bugs — untested). Instead, they build a small, deliberate **polling/waiting utility** into the test infrastructure itself: a helper that repeatedly checks for an expected outcome (e.g., "the UI now shows SniperState.WINNING for this item") within a bounded timeout, succeeding as soon as the condition becomes true and failing only if it never becomes true within a generous, explicit time budget.

## How it works

### Why "just add a sleep" is the wrong fix
A common first instinct when a test fails intermittently due to timing is to add `Thread.sleep(500)` before the assertion. This "fixes" the immediate flakiness but at real cost: it makes every test run slower by a fixed amount regardless of how fast the system actually responds (violating `goos/01`'s fast-feedback principle), and it's still not actually reliable — under load, or on a slower CI machine, 500ms might not be enough, and the test becomes flaky again. Freeman & Pryce reject fixed sleeps as a testing strategy for exactly these reasons.

### The polling approach: wait for the condition, not for a fixed duration
Instead, the book's testing infrastructure (embodied in a small `AuctionSniperDriver`/`ApplicationRunner`-style test helper) polls for the expected outcome at short intervals (e.g., every 100ms) up to a generous overall timeout (e.g., 5 seconds), returning as soon as the condition is observed true. This means the test runs as fast as the system actually is in the common case (often much less than 100ms if the system is healthy) while still tolerating genuine, occasional slowness without becoming flaky — the test only fails if the condition truly never becomes true within a timeout generous enough to rule out "it just hadn't happened yet."

**Worked example.** An acceptance test for "the sniper shows WINNING after it places a bid and no one outbids it":

```
auctionSniperDriver.startBiddingFor("item-54321");
auctionDriver.hasReceivedBid();          // drives the fake auction to accept the bid
auctionSniperDriver.showsSniperStatus("item-54321", "Winning");
```

`showsSniperStatus(...)` here is not a single assertion — it's a helper that polls the UI's actual displayed state, repeatedly, until it matches `"Winning"` or a timeout elapses. If the UI update genuinely takes 30ms because a network round-trip and an event dispatch have to complete first, the test passes in about 30ms. If something is actually broken and the UI never shows "Winning," the test fails after the full timeout, with a clear message about what was expected versus what was last observed — not a mysterious, unrepeatable one-off failure.

### Isolating the asynchronous seam so most tests don't need to deal with it
This connects directly to `goos/06`'s ports-and-adapters lesson: because the messy, genuinely asynchronous, real-network behavior is isolated inside adapter classes (the real `XMPPAuction`, the real UI event dispatch), the *domain* unit tests from `goos/05` and `goos/07` can stay entirely synchronous — `AuctionSniper.currentPrice(...)` is a plain, synchronous method call in its own tests, with no polling needed, because the domain object itself has no asynchrony; it's just called asynchronously by adapters in the real system. Polling-based waiting is needed only at the *acceptance*-test level (`goos/04`), where the test genuinely has to cross a real asynchronous boundary end-to-end — which is exactly where you'd want that cost concentrated, since acceptance tests are already fewer and slower than the bulk of the fast unit-test suite.

### Handling "nothing happens" — testing for the absence of an event
A subtler async testing problem: how do you test that something correctly does *not* happen (e.g., "the sniper does not bid again after it has already won")? You can't poll for an absence the same way you poll for a presence — waiting the full timeout every time to confirm nothing happened would make that one test as slow as the timeout itself, and worse, a genuine but late bid would only be caught if it happened to land within that window. Freeman & Pryce's practical answer: rely primarily on synchronous domain-level tests (`goos/05`, `goos/07`) to establish "no bid call happens in this state," where a mock's absence-of-a-call assertion is precise and immediate, and reserve the slower end-to-end async tests for confirming the presence of expected behavior, not the absence of unexpected behavior — pushing negative assertions down to the layer where they can be checked synchronously and cheaply.

## Pros
- Produces async and acceptance tests that are as fast as the system actually is in the common case, without the fixed cost or unreliability of arbitrary sleeps.
- Tests genuinely exercise the real asynchronous seam (the thing most likely to actually break), rather than being scoped away entirely to synchronous domain logic.
- Failure messages from a timeout-based wait are diagnostic ("expected WINNING, last observed BIDDING after 5s") rather than the opaque, hard-to-reproduce failures typical of sleep-based flaky tests.

## Cons
- Polling utilities add real test infrastructure complexity that a purely synchronous test suite doesn't need — building and maintaining a reliable wait-for-condition helper is itself nontrivial work.
- Even well-built polling tests are slower than pure unit tests (bounded by real event-dispatch latency, not just CPU time), so they must be used sparingly, at genuine async boundaries, not throughout the suite.
- Testing for the *absence* of an async event remains genuinely hard and typically has to be pushed down to a synchronous layer (per the worked point above) rather than solved directly at the async boundary — an important limitation to design around rather than around which you can spuriously wait-and-hope.

## Alternatives
- **Fixed sleeps before assertions** — simplest to write, but slow (always waits the full fixed time) and still not fully reliable, the exact failure mode this lesson argues against.
- **Synchronous test doubles that fake away the asynchrony entirely** — replace the real async adapter with a synchronous fake for testing, avoiding timing issues altogether. Useful for domain-level tests (and consistent with `goos/06`'s port isolation), but doesn't validate that the real asynchronous integration actually works — some tests still need to cross the real boundary.
- **Explicit callback/future-based synchronization in tests** — instead of polling, have the test register a callback or await a future that the production code explicitly completes when the awaited event occurs. Can be more precise and faster than polling when the production code already exposes such a hook, but requires the production code to expose test-observable completion signals it might not otherwise need.

## When to use it
Use polling-based waiting at any acceptance or integration test that genuinely crosses a real asynchronous boundary — network calls, message queues, UI event dispatch, background threads. This is inherent to testing systems like the sniper that are asynchronous by nature, not a niche technique.

## When NOT to use it
Don't reach for polling/waiting utilities in domain-level unit tests where the object under test is itself synchronous (per `goos/06`'s isolation) — that's a sign the test is accidentally exercising a real async boundary it should be isolated from via a port/adapter or a synchronous fake. Also avoid using async waiting to test the absence of an event; use a synchronous mock-based test instead, per the worked point above.

## Key takeaways / mental model
Never assert immediately on something that happens asynchronously — wait for the condition to become true, bounded by a generous timeout, and fail with a clear "expected X, last saw Y" message if it never does. Keep as much of your test suite synchronous as possible by isolating real asynchrony behind ports and adapters (`goos/06`); reserve polling-based waiting for the few tests that genuinely need to observe a real asynchronous boundary.

## Self-check questions
1. Explain concretely why `Thread.sleep(500)` before an assertion is worse than a poll-with-timeout helper, even though both "solve" an immediate flaky-test symptom.
2. Why is testing for the *absence* of an asynchronous event structurally harder than testing for its presence, and what does this lesson recommend doing instead?
3. A teammate wants to add polling-based waiting to a domain-level unit test for `AuctionSniper.currentPrice(...)`, because "it might be called from a different thread in production." What would you check first, and what's the likely actual fix?

## References
- Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part II, Chapter 9 (testing across the messaging/UI boundary) and the `AuctionSniperDriver`/Swing UI testing material.
