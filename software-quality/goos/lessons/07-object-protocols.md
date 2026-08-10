---
id: goos/07
subject: goos
title: Designing Object Protocols Through Collaboration Tests
slug: object-protocols
status: drafted
mastery:
seniority: senior
source: Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part II/Chapter 7
prerequisites: [goos/05]
created: 2026-08-10
updated: 2026-08-10
---

# Designing Object Protocols Through Collaboration Tests

## TL;DR
An object's "protocol" is the ordered, meaningful sequence of messages it exchanges with its collaborators over time — not just any single method's signature, but the conversation as a whole. Freeman & Pryce show that this protocol is best discovered by writing collaboration tests that walk through realistic multi-step scenarios, letting the sequence and shape of calls emerge from actual behavior rather than being specified as a static interface upfront.

## The idea
`goos/05` covers how a single mock expectation discovers one method's signature. This lesson goes one level further: real objects rarely exchange just one message and stop — they hold a *conversation* over time, and the order, repetition, and conditions of that conversation matter as much as any individual method. Two collaborators can have technically compatible interfaces (the right method names and types) and still be badly designed together if the *protocol* — the expected sequence and rhythm of calls — is awkward, surprising, or requires the caller to remember state the callee should be managing itself.

Freeman & Pryce call this "designing the conversation between objects." For the auction sniper, `AuctionSniper` doesn't just receive one price update — it receives a whole stream of them over the life of an auction (price changes, being outbid, eventually closing), and its behavior needs to make sense across that entire sequence, not just for one isolated event. Collaboration tests that walk through a realistic multi-event scenario are what surface whether the protocol between `AuctionSniper` and its collaborators (the auction connection, the UI) actually holds together — a single-call mock test can miss protocol problems that only show up across a sequence.

## How it works

### A protocol is a sequence, not a signature
Consider `AuctionSniper` and the UI it reports its status to. A naive, signature-only view might say: "the UI needs a `showStatus(state)` method." But the actual protocol has more shape than that single method suggests: status updates arrive in a specific meaningful order (an auction can go from "joining" to "bidding" to "winning" or "losing," but never, say, from "lost" back to "bidding") and the UI needs to reflect exactly one auction's current state at a time, correctly, even as many updates arrive rapidly. A collaboration test that only checks a single `showStatus()` call in isolation won't catch a bug where the second and third updates overwrite each other incorrectly, or where the UI briefly shows a stale state during a fast sequence of events — bugs that only exist *in the sequence*, not in any single call.

**Worked example — a sequence-level collaboration test.** Instead of testing one event:

```
@Test
public void reportsLostIfAuctionClosesWhenBidding() {
    sniper.currentPrice(123, 45);      // step 1: price update, sniper bids
    sniper.auctionClosed();            // step 2: auction ends while sniper was bidding

    assertEquals(SniperState.LOST, sniper.getState());
}
```

This single test already checks a two-step sequence, and it's revealing: it forces `AuctionSniper` to track *which state it was in* (bidding, not winning) when the auction closed, in order to correctly report LOST rather than WON. A design that only handles isolated events in isolation — with no memory of what happened just before — would fail this test, exposing that state-across-time, not just per-event handling, is a real part of the object's required behavior.

### Discovering the protocol iteratively, scenario by scenario
Freeman & Pryce build up `AuctionSniper`'s full protocol through a series of such scenario tests, each covering one meaningful path through the object's lifecycle: joining and immediately losing; bidding and winning; bidding, being outbid, re-bidding, and eventually winning; bidding and losing because the stop price was reached. Each new scenario either confirms the existing protocol handles it correctly or exposes a gap — a state transition nobody had thought about, an event ordering that breaks an assumption baked into an earlier test. This is design work happening through tests, not despite them: the full state machine implicit in "how an auction sniper behaves over the life of one auction" emerges from enumerating and testing realistic sequences, rather than being drawn as a state diagram upfront and then implemented to match.

### Protocols constrain how a mock should be used
This lesson also refines `goos/05`'s guidance: when a mock stands in for a collaborator across a multi-step scenario, its expectations should reflect the *sequence* that matters, not just that certain calls happened at some point. Some testing frameworks let you assert calls happened "in order" specifically for this reason. Asserting only "bid() was called with 1200 at some point during this test" is weaker than asserting "the sniper called bid(1200) only after receiving the outbid notification, and did not call it before" — the ordered assertion is what actually verifies the protocol, not just the presence of an isolated call.

### A protocol mismatch is a design smell, not just a bug
When two objects' protocols don't cleanly fit — one side needs to call a sequence of three methods in a fragile, specific order that the other side doesn't enforce or document, or a caller has to poll a collaborator's state repeatedly to know when it's safe to call the next method — that's a signal the interface, not just the implementation, needs rethinking. Freeman & Pryce treat this as exactly the kind of thing collaboration tests are for catching early: if writing a realistic multi-step test for two collaborating objects feels awkward, contorted, or requires excessive setup to get into the right state, that awkwardness is telling you something true about the design, not just about the test.

## Pros
- Surfaces protocol-level design problems (bad state handling, fragile call ordering, missing lifecycle events) that single-call, signature-only tests miss entirely.
- Produces objects whose collaborators can rely on a well-understood, tested sequence of interactions, reducing the chance of subtle "worked in isolation, broke in combination" bugs.
- Makes design awkwardness visible early: a test that's painful to write because the protocol is clumsy is direct, actionable feedback during development rather than a problem discovered after the fact.

## Cons
- Collaboration tests covering realistic multi-step scenarios are more complex to write and read than single-call unit tests, and can become brittle if they over-specify incidental ordering that doesn't actually matter (a concern this subject returns to in `goos/10`).
- Requires more upfront thought about what the *meaningful* scenarios are (which sequences matter, which don't) — done poorly, you either miss important sequences or waste effort testing irrelevant ones.
- Protocol discovery through tests works best incrementally; retrofitting proper sequence-aware collaboration tests onto an already-built, protocol-naive design is much harder than designing them together from the start.

## Alternatives
- **Formal state machine design upfront** — model the object's full lifecycle (states and transitions) as a diagram or specification before writing any code or tests, then implement and test against that fixed design. More rigorous for genuinely complex protocols (e.g., safety-critical systems) but loses the emergent-discovery benefit and can still miss scenarios nobody thought to model.
- **Single-call unit tests only, no sequence testing** — test each method's behavior in isolation, trusting that correct individual behaviors compose correctly. Simpler tests, but exactly the gap this lesson identifies: correct-in-isolation methods can still combine into an incorrect protocol.
- **Contract tests / Design by Contract** — specify pre/post-conditions and invariants formally for each method, checked at runtime or via static tooling. Complementary rather than opposed to collaboration testing — contracts constrain individual calls, collaboration tests constrain sequences of them.

## When to use it
Use scenario-level collaboration tests whenever an object's correct behavior genuinely depends on history — what happened before this call — which is most objects with any real lifecycle (state machines, session-like objects, anything reacting to a stream of events over time, like the sniper).

## When NOT to use it
Skip sequence-level collaboration tests for genuinely stateless objects where each call's outcome depends only on its own inputs, not on anything that happened before — a pure function or a stateless calculator gains nothing from scenario testing that single-call unit tests don't already provide.

## Key takeaways / mental model
Ask of any collaborating pair of objects: "if I only test one call at a time, what could still go wrong across a realistic sequence of calls?" If the honest answer is "something," write the multi-step scenario test that would catch it — and if that test is painful to write, treat the pain as a design signal about the protocol itself, not just an annoyance to push through.

## Self-check questions
1. Explain why the two-step test (`currentPrice` then `auctionClosed`) catches a class of bug that two separate, single-event tests would miss.
2. Describe a protocol mismatch you'd expect to find awkward to test between two collaborating objects, and explain what that awkwardness would be telling you about the design.
3. A collaboration test asserts that three specific mock calls happened "in this exact order," but on reflection, two of those three calls could happen in either order without affecting correctness. What's the risk of leaving that over-specified ordering assertion in place, and how does it relate to `goos/10`'s concerns?

## References
- Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part II, Chapter 7: "Achieving Object-Oriented Design."
