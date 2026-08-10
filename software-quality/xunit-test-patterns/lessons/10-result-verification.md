---
id: xunit-test-patterns/10
subject: xunit-test-patterns
title: Result Verification and Behavior vs State Checks
slug: result-verification
status: drafted
mastery:
seniority: mid
source: xUnit Test Patterns: Refactoring Test Code (Gerard Meszaros), Chapter 9
prerequisites: [xunit-test-patterns/03, xunit-test-patterns/05]
created: 2026-08-10
updated: 2026-08-10
---

# Result Verification and Behavior vs State Checks

## TL;DR
There are two fundamentally different ways to verify a test passed: **State Verification** checks the resulting state of the SUT (or a DOC) after the exercise phase; **Behavior Verification** checks that specific interactions (calls, with what arguments) happened during the exercise phase. Meszaros's guidance: prefer State Verification wherever a meaningful outcome exists to check, and reserve Behavior Verification for the cases where the interaction genuinely *is* the point — because Behavior Verification is the more fragile of the two (see Interface/Behavior Sensitivity in `xunit-test-patterns/07`).

## The idea
Every test eventually has to answer "did the exercise phase produce the right result?" — but "right result" can mean two different things. Sometimes it means "the world ended up in the right state" (an order's status is now `SHIPPED`, an account's balance decreased by the right amount). Sometimes there's no meaningful resulting *state* to check at all — the SUT's whole job was to *tell* something else to do something (send an email, publish an event, write a log line) — and the only way to verify that happened is to check that the call was made.

This distinction connects directly to the test-double choice in `xunit-test-patterns/05`: State Verification pairs naturally with Stubs and Fake Objects (you ask the Fake for its resulting state); Behavior Verification pairs naturally with Mocks (you ask the Mock whether it was called correctly). Picking the wrong verification style for a given scenario is a common, avoidable source of Fragile Tests.

## How it works

### State Verification: checking the aftermath
```
test "withdraw reduces the account balance":
    account = anAccount().withBalance(500).build()

    account.withdraw(200)

    assert account.balance == 300   # checking resulting STATE
```
The test doesn't care *how* `withdraw` internally computed the new balance — maybe it does `balance -= amount`, maybe it delegates to a `LedgerEntry` object, maybe it recalculates from a list of transactions. Any internal implementation that produces the correct resulting state passes this test, which is exactly the point: State Verification is naturally robust to internal refactoring (low Interface/Behavior Sensitivity, per `xunit-test-patterns/07`), because it only checks the externally observable outcome.

### Behavior Verification: checking the interaction itself
```
test "placeOrder notifies the customer":
    mockNotifier = new MockEmailNotifier()
    service = new OrderService(mockNotifier)

    service.placeOrder(order)

    mockNotifier.verifyCalledOnceWith(order.customerEmail, "order confirmed")   # checking an INTERACTION
```
Here there's no `order.wasCustomerNotified()` state to check — notification is an outward call with no return value the test can inspect afterward. Behavior Verification is the *only* way to test this particular responsibility, which is exactly when it's the right tool: the interaction genuinely is the observable behavior under test, not an implementation detail.

### The decision point, worked through a shared example
Consider `OrderService.placeOrder()`, which (a) computes and stores the order total, and (b) calls a `PaymentGateway.charge()`.

For (a), State Verification is natural and more robust:
```
test "placeOrder computes the correct total":
    service = new OrderService(stubGateway, fakeRepo)
    order = anOrder().withItems([item1, item2]).build()

    service.placeOrder(order)

    saved = fakeRepo.findById(order.id)
    assert saved.total == 145.00   # state, via a Fake's real (if in-memory) storage
```

For (b), there's genuinely no resulting state to check that would tell you charging happened correctly — the payment gateway's real state lives outside the process. Behavior Verification is the right (often only) tool:
```
test "placeOrder charges the customer the order total":
    mockGateway = new MockPaymentGateway()
    service = new OrderService(mockGateway, fakeRepo)

    service.placeOrder(order)

    mockGateway.verifyCalledOnceWith("charge", order.total)   # only meaningful part of the call
```
Note the assertion checks only the meaningful argument (`order.total`), not the full call signature or call count beyond "once" — this is the Behavior-Sensitivity mitigation from `xunit-test-patterns/07` applied directly: assert the minimum necessary to express the test's actual intent.

### A common mistake: reaching for Behavior Verification out of habit
```
# unnecessarily fragile: verifying an internal call instead of checking the outcome
test "withdraw reduces the account balance":
    mockLedger = new MockLedger()
    account = new Account(mockLedger)

    account.withdraw(200)

    mockLedger.verifyCalledOnceWith("recordDebit", 200)   # implementation detail, not the actual point
```
This test now breaks if `Account.withdraw` is refactored to compute the balance differently (batch the debit, cache it, whatever) — even though the resulting balance is still correct. The State Verification version earlier in this lesson checks exactly the thing the test's name promises ("reduces the balance") without caring how. This is Interface Sensitivity (`xunit-test-patterns/07`) introduced by choosing the wrong verification style for a scenario that had a perfectly good state to check.

### When State Verification isn't available even though it seems like it should be
Sometimes a DOC is real infrastructure (a real message queue, a real external API) with observable state that's slow or awkward to query in a test. In that case, a Fake Object (see `xunit-test-patterns/05`) that exposes queryable in-memory state is often the better fix — converting an otherwise Behavior-Verification-only scenario back into a fast, robust State Verification one, rather than reaching for a Mock purely because querying the real DOC's state is inconvenient.

## Pros
- State Verification is naturally robust to internal implementation changes, reducing Interface and Behavior Sensitivity (`xunit-test-patterns/07`).
- Behavior Verification is the only option for genuinely "tell, don't ask" interactions with no observable resulting state (notifications, published events, log entries of record).
- Explicitly choosing between the two, rather than defaulting to whichever the mocking framework makes easiest, produces tests that fail for the right reasons.

## Cons
- State Verification requires the SUT (or its DOCs) to actually expose observable state — sometimes that means adding a getter or query method purely for testability, which is a real (if often small) production-code cost.
- Behavior Verification, even when narrowly scoped to meaningful arguments, still couples the test to *some* aspect of how the SUT is implemented — it can never be as refactor-proof as pure State Verification.

## Alternatives
- **Hybrid verification** — using a Fake Object with queryable state specifically to convert what would otherwise require Behavior Verification into State Verification (see the message-queue example above); often the best available compromise.
- **Event-sourcing-style verification** — for systems built around published domain events, verifying "the correct event was published, with the correct payload" is itself a form of State Verification if events are captured into an inspectable log, rather than Behavior Verification against a Mock.

## When to use it
Default to State Verification whenever the SUT or a DOC has a meaningful, queryable resulting state after the exercise phase. Reach for Behavior Verification specifically when the responsibility under test is an outward call with no other observable trace — and even then, assert only the meaningful part of that call.

## When NOT to use it
Don't reach for Behavior Verification just because a mocking framework makes it the path of least resistance — check first whether a Fake Object could expose state instead, giving you a more refactor-robust test for the same behavior.

## Key takeaways / mental model
Ask "after this runs, is there a meaningful resulting state I can check, or is the whole point that a specific call happened?" State exists -> State Verification, using Stubs/Fakes. No state, only an outward call -> Behavior Verification, using a Mock, scoped to only the meaningful arguments.

## Self-check questions
1. Rewrite the "withdraw reduces balance via mockLedger" example from this lesson into a State Verification test, and explain concretely why it's more robust to refactoring.
2. Give an example (different from the ones in this lesson) of a responsibility that structurally has no observable state to check, making Behavior Verification the only real option.
3. A Mock-based test verifies a call was made "exactly once, with these exact five arguments, in this exact order." Using this lesson and `xunit-test-patterns/07`, what would you narrow the assertion to, and why?
4. Describe a scenario where converting a Mock-based Behavior Verification test into a Fake-based State Verification test would require a production-code change. Is that change worth making?

## References
- xUnit Test Patterns: Refactoring Test Code (Gerard Meszaros), Chapter 9: "Result Verification" (State Verification and Behavior Verification).
- See also: `xunit-test-patterns/05` for the test-double choices this pattern pairs with, and `xunit-test-patterns/07` for the Fragile Test consequences of choosing the wrong verification style.
