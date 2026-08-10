---
id: goos/05
subject: goos
title: Mock Objects and Role-Based Design
slug: mock-objects-role-design
status: drafted
mastery:
seniority: senior
source: Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part II/Chapter 6
prerequisites: [goos/01, goos/04]
created: 2026-08-10
updated: 2026-08-10
---

# Mock Objects and Role-Based Design

## TL;DR
Mock objects, in Freeman & Pryce's usage, are primarily a *design discovery tool*, not just a stand-in for slow or unavailable dependencies: writing a unit test with a mock forces you to decide, right now, what role a collaborator plays and exactly what messages an object needs to send it — discovering the object's protocol through the pressure of writing a test for it, rather than designing it in the abstract beforehand. "Tell, don't ask" and interface-per-role design fall directly out of this practice.

## The idea
Mock objects originated as a way to test a unit in isolation from slow or awkward dependencies (databases, networks, other classes not yet built). That utility is real, but Freeman & Pryce's central claim is different and more radical: the *act of writing a mock-based test* is itself a design technique. When you're building `AuctionSniper` and it needs to tell an auction "please place this bid," you don't yet need a real `Auction` implementation — you need to decide, right now, in the test, exactly what method that call is, what parameters it takes, and what `AuctionSniper` expects back. Writing that expectation on a mock *is* designing the `Auction` interface, driven entirely by what the calling code actually needs, not by what feels "complete" from the callee's perspective.

This connects to two related ideas that Freeman & Pryce treat as inseparable from mocking done well:

- **Tell, don't ask**: objects should be told what to do (`auction.bid(amount)`) rather than interrogated for data that the caller then acts on (`auction.getCurrentPrice()` followed by the caller deciding and then calling something else). Mock-object tests naturally push toward "tell" because a mock is easiest to specify in terms of *what messages it receives*, not what data it hands back for the caller to process.
- **Role-based interfaces**: an object doesn't have one monolithic interface — it plays different *roles* to different collaborators, and each role should be its own small, focused interface. `Auction` might implement one narrow interface (`AuctionEventListener`) for receiving price-change notifications and a separate one (`Bidder`) for accepting bid requests — discovered because two different tests, from two different callers' perspectives, needed two different, unrelated sets of messages.

## How it works

### The distinction: mocks discover behavior, stubs supply state
A precise vocabulary matters here (Freeman & Pryce are careful about it, echoing Meszaros's *xUnit Test Patterns*, which this repo's `xunit-test-patterns` subject covers in depth). A **stub** is a test double that returns canned data when queried — it exists to feed the object under test with state it needs (`stub Auction returns currentPrice() = 122`). A **mock** is a test double that the test sets *expectations* on, then verifies afterward that specific calls actually happened, in the way the object under test was supposed to make them (`mock Auction expects bid(135) to be called exactly once`). Stubs support the "ask" side of an interaction (getting data); mocks verify the "tell" side (an action was actually requested). Conflating the two — asserting on a stub's return value, or using a mock just to avoid a slow dependency without caring about the interaction itself — loses the design-discovery benefit this lesson is about.

**Worked example.** Testing that `AuctionSniper` bids when outbid:

```
@Test
public void bidsHigherWhenNewPriceArrivesAndOutbid() {
    Auction auction = mock(Auction.class);
    AuctionSniper sniper = new AuctionSniper(auction);

    sniper.currentPrice(1000, 1200);  // price is now 1000, increment 200, so next bid is 1200
    // sniper is not the last bidder, so it should respond

    verify(auction).bid(1200);
}
```

Writing this test *before* `Auction.bid(int amount)` exists is what invents that method's exact signature — not a design meeting, not a UML diagram, but the immediate, concrete pressure of "what does `AuctionSniper` need to say to its auction collaborator to accomplish this behavior?" The mock forces the answer to be specific and minimal: not `Auction.submitBidRequest(BidRequest request, BidCallback callback)` (over-engineered, guessing at future flexibility) but exactly `bid(int amount)` — the one message this test's scenario actually needs.

### Discovering roles: one object, several small interfaces
As more tests get written against `AuctionSniper` from different angles, distinct roles emerge. One test needs `AuctionSniper` to *receive* price-change notifications — this discovers an `AuctionEventListener` role/interface with a method like `currentPrice(price, increment)` and `auctionClosed()`. A separate test needs `AuctionSniper` to *send* bid requests — this discovers a `Bidder`-facing need on `Auction`, distinct from the listener role. Freeman & Pryce's insight is that these two roles don't need to live on the same interface just because one class (`Auction`) happens to implement both in the real system — keeping them as separate, narrow interfaces, each shaped by the tests that needed them, keeps every consumer coupled only to the small slice of behavior it actually uses (an application of the Interface Segregation Principle, discovered bottom-up rather than applied top-down from a principle).

### Mock-driven design vs. designing the interface first, then testing it
Contrast this with a common alternative sequence: design `Auction`'s full interface upfront (perhaps because "an auction obviously needs to support bidding, price queries, closing, and history"), then write mocks that conform to that pre-decided interface. This inverts the discovery process — instead of the test's actual need shaping a minimal interface, a guessed-at, "complete-feeling" interface gets imposed on the test, typically producing a fatter interface than any single caller needs, with methods that exist because they seemed plausible rather than because any test demanded them. Freeman & Pryce's mock-first approach is deliberately narrower and more disciplined: no method exists on a collaborator's interface unless some test, driven by real calling code, needed it.

### A worked contrast: "ask" vs. "tell" for the same scenario
Suppose `AuctionSniper` needs to decide whether to bid. An "ask" style: `if (auction.getCurrentPrice() < myStopPrice) { auction.submitBid(auction.getCurrentPrice() + auction.getIncrement()); }` — this pulls state out of `Auction`, computes with it, then pushes a decision back in, coupling `AuctionSniper` to `Auction`'s internal notion of price and increment as separate queryable values. A "tell" style: `Auction` pushes a `currentPrice(price, increment)` event to any listener, and `AuctionSniper` (which already knows its own stop price) decides internally and calls `auction.bid(amount)` only when it decides to. The tell style keeps the decision logic and the state that feeds it together in one place, and it's the style a mock-based test for `AuctionSniper` naturally leads you toward, because specifying "when told X, sniper should call Y" is exactly what a mock's expectation captures.

## Pros
- Turns interface design into an evidence-driven, incremental discovery process instead of an upfront guessing exercise, producing minimal, role-shaped interfaces.
- Naturally pushes toward "tell, don't ask" and better encapsulation, because mocks are easiest to specify in terms of messages sent, not data queried.
- Makes an object's actual dependencies and responsibilities explicit and visible in its tests — the mocked collaborators in a test are a direct readout of what that object needs from the world.

## Cons
- Overusing mocks — especially mocking concrete classes you don't own, or mocking every collaborator including simple data objects — produces brittle tests tightly coupled to implementation details rather than behavior (this failure mode is the focus of `goos/10`).
- Teams new to the technique often write mocks that assert on incidental calls rather than the behavior that actually matters, producing tests that break on harmless refactorings.
- Requires collaborators to be genuinely substitutable (usually via an interface), which pushes toward more interfaces and more indirection than a codebase not using this technique would have — a cost that only pays off if the resulting design is actually used well.

## Alternatives
- **State-based testing with real collaborators** — construct real objects and assert on the resulting state after an operation, rather than mocking interactions. Simpler and often more robust to refactoring for objects whose collaborators are cheap and side-effect-free, but doesn't provide the same interface-discovery pressure.
- **Stub-only testing** — use stubs to supply necessary data without setting behavioral expectations, verifying only the object under test's return value or resulting state. Avoids mock brittleness but also loses the "tell" discipline mocks encourage.
- **Fakes** — lightweight, working (if simplified) implementations of a dependency (e.g., an in-memory auction server) used across many tests. Better than mocks for exercising realistic multi-step interactions, at the cost of being more work to build and maintain than a one-off mock expectation.

## When to use it
Use mock-driven tests specifically when designing the interaction between an object you're actively building and a collaborator whose interface isn't fixed yet — this is where the discovery benefit is real. It's especially valuable at architectural seams (per `goos/06`) where getting the interface's shape right matters most.

## When NOT to use it
Don't mock simple, stateless value objects (a `Money` or `Price` type) — there's no meaningful interaction to discover; state-based assertions are simpler and just as safe. Don't mock a collaborator whose interface is already fixed and well-understood (a stable library type) purely out of habit — save mocking for genuine design discovery or genuine isolation from slow/external dependencies.

## Key takeaways / mental model
A mock expectation is a sentence: "when X happens, this object should tell that collaborator Y." Writing that sentence, before the collaborator's real implementation exists, is how the collaborator's interface gets designed — minimally, from actual need, one role at a time — rather than guessed at wholesale. If you can't write that sentence naturally, that's a signal the design isn't clear yet, not a reason to force the mock.

## Self-check questions
1. Explain, using the `AuctionSniper`/`Auction` example, how the exact signature of `Auction.bid(int amount)` gets "discovered" rather than designed in a separate step.
2. Why does Freeman & Pryce's approach favor several small, role-based interfaces on `Auction` (a listener role, a bidder role) over one larger `Auction` interface with all its methods together?
3. A teammate mocks `getCurrentPrice()` on `Auction` and asserts the mock was called, in a test for logic that only uses the returned price to compute a bid. Explain why this is closer to stub usage than genuine mock-driven interaction testing, and what's lost by treating it as a mock.
4. Give an example of a collaborator you would deliberately choose NOT to mock, and explain what alternative (state-based test, fake, or real object) you'd use instead and why.

## References
- Growing Object-Oriented Software, Guided by Tests (Freeman & Pryce), Part II, Chapter 6: "Object-Oriented Style" and Chapter 8: "Building on Third-Party Infrastructure."
- See also: `xunit-test-patterns` (if authored) for the precise stub/mock/fake/spy vocabulary this lesson relies on.
