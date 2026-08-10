---
id: xunit-test-patterns/05
subject: xunit-test-patterns
title: Test Doubles in xUnit Patterns Language
slug: test-doubles-pattern-language
status: drafted
mastery:
seniority: mid
source: xUnit Test Patterns: Refactoring Test Code (Gerard Meszaros), Chapters 11-13
prerequisites: [xunit-test-patterns/01, xunit-test-patterns/04]
created: 2026-08-10
updated: 2026-08-10
---

# Test Doubles in xUnit Patterns Language

## TL;DR
"Test double" is Meszaros's umbrella term (borrowed from "stunt double") for any object that stands in for a real DOC (Depended-On Component) during a test. The four core kinds — **Dummy**, **Stub**, **Mock**, and **Fake Object** — differ in exactly one dimension each: what they do when called and what, if anything, the test checks about how they were called. Picking the wrong kind for a given test is a common source of both Obscure Tests and Fragile Tests (see `xunit-test-patterns/07`).

## The idea
A SUT often depends on things that are slow, non-deterministic, expensive, or hard to control in a test: a real database, a payment gateway, the system clock, a third-party API. Test doubles let you replace those DOCs with something fast, deterministic, and fully under the test's control — without changing the SUT's code, as long as the SUT depends on an interface/abstraction rather than a concrete implementation.

The reason Meszaros gives four *distinct* names instead of one generic "mock" (the term many developers use loosely for all of them) is that each kind answers a genuinely different question, and conflating them leads to tests that check the wrong thing — usually by accidentally asserting on implementation details (*how* the SUT called its collaborator) when the test only cared about an outcome (*what* the SUT produced).

## How it works

### Dummy — a placeholder that's never actually used
A Dummy is passed in only because the API requires *something* in that parameter slot; the test never expects it to be called or inspected.

```
test "invoice number generator ignores the logger argument":
    dummyLogger = new DummyLogger()   # required by the constructor, never invoked in this path
    generator = new InvoiceNumberGenerator(dummyLogger)

    number = generator.next()

    assert number == "INV-0001"
```

If `DummyLogger`'s methods were ever called, that would usually indicate the test wired something up wrong — a Dummy's whole point is that it's inert.

### Stub — feeds the SUT canned answers
A Stub is used when the SUT *calls* the DOC and needs a return value to proceed — the test controls what that value is, to drive the SUT down a specific path.

```
test "shipping calculator applies free shipping above the threshold":
    stubPricing = new StubPricingService(returns=110.00)   # canned answer
    calculator = new ShippingCalculator(stubPricing)

    fee = calculator.feeFor(order)

    assert fee == 0.00   # free shipping, because stubbed subtotal exceeds threshold
```

The test cares about the SUT's *output* given a controlled input from the DOC — not about whether or how many times `StubPricingService` was called. Asserting call counts on a Stub is a category error that Meszaros calls out directly: it conflates Stub with Mock.

### Mock — verifies the SUT's outgoing interactions (Behavior Verification)
A Mock is used specifically when the *interaction itself* — that a call happened, with what arguments, how many times — is the behavior under test, typically because the DOC has no observable return value the test could otherwise check (a "tell, don't ask" style dependency like a notifier or a logger of record).

```
test "order placement notifies the customer exactly once":
    mockNotifier = new MockEmailNotifier()
    service = new OrderService(mockNotifier)

    service.placeOrder(order)

    mockNotifier.verifyCalledOnceWith(order.customerEmail, "order confirmed")
```

Here there's no meaningful return value to check — the test's actual point is "did the SUT correctly tell the notifier to send this." This is **Behavior Verification** (see `xunit-test-patterns/10`), and Mock is the tool for it.

### Fake Object — a working, lightweight implementation
A Fake Object isn't canned or inert — it's a real, working (but simplified) implementation of the DOC's contract, usually in-memory.

```
class InMemoryOrderRepository implements OrderRepository:
    storage = {}
    function save(order):
        storage[order.id] = order
    function findById(id):
        return storage.get(id)
```

```
test "order service persists a placed order and can retrieve it":
    fakeRepo = new InMemoryOrderRepository()
    service = new OrderService(fakeRepo)

    service.placeOrder(order)

    assert fakeRepo.findById(order.id) == order
```

A Fake genuinely implements the behavior (state really is stored and retrievable) rather than returning a pre-scripted answer, which makes it well suited for **State Verification** — checking the resulting state through the DOC's own real interface, rather than through raw assertions on internal fields (see `xunit-test-patterns/10`).

### Choosing the right double: a decision guide
| Question | Answer -> double |
| --- | --- |
| Does the test even care what this dependency does? | No -> **Dummy** |
| Does the SUT need a return value from it to proceed down the path under test? | Yes, and the value is what matters -> **Stub** |
| Is the fact that the SUT called it (with what args, how many times) itself the behavior under test? | Yes -> **Mock** |
| Would a lightweight, real, working implementation be cheap and let you verify through state instead? | Yes -> **Fake Object** |

### A common misuse worth naming: over-mocking
A frequent real-world mistake is reaching for a Mock everywhere, including places where a Stub or Fake would do, because mocking frameworks make it syntactically easy. The cost: Mock-heavy tests couple tightly to the SUT's exact sequence of calls, so a harmless internal refactor (e.g., caching a value instead of calling the DOC twice) breaks tests that never should have cared about *how* the SUT reached its answer. This is Interface Sensitivity, one of the four causes of Fragile Test covered in `xunit-test-patterns/07` — and it's the single most common way test-double choice creates fragility.

## Pros
- Makes SUTs testable in isolation from slow, non-deterministic, or dangerous real dependencies (databases, payment gateways, clocks).
- Naming the four kinds precisely prevents accidentally asserting on the wrong thing (call sequence vs. outcome).
- Fake Objects in particular let you keep State Verification (often more robust to refactoring) even when the real DOC would be too slow or unsafe to use directly.

## Cons
- Overuse of Mocks in particular creates Fragile Tests that break on harmless internal refactors, because they encode *how* the SUT works, not just *what* it produces.
- Maintaining Fake Objects that genuinely mirror the real DOC's contract is itself an investment; a Fake that drifts out of sync with the real implementation gives false confidence.
- Deep test-double chains (doubles that themselves depend on doubles) can become as hard to read as the obscure tests they were meant to prevent.

## Alternatives
- **Using the real DOC** — preferable whenever it's fast, deterministic, and safe (e.g., a pure in-memory value object never needs a double at all); reserve doubles for genuinely problematic dependencies.
- **Contract tests against the real DOC, doubles for everything else** — run a small separate test suite that verifies your Fake/Stub actually matches the real DOC's contract, mitigating the "Fake drifts out of sync" risk while keeping most tests fast.
- **Sociable unit tests** (deliberately allowing a SUT to collaborate with real, fast, in-process collaborators rather than doubling every one) — a stylistic alternative common in the London/Chicago testing-school debate; trades some isolation for more realistic coverage of collaboration bugs.

## When to use it
Use a test double whenever a real DOC would make the test slow, non-deterministic, expensive, or unsafe to run repeatedly (external services, real time, real payment processing). Choose the specific kind (Dummy/Stub/Mock/Fake) by asking what the test actually needs to verify, not by defaulting to whatever your mocking framework makes easiest to type.

## When NOT to use it
Don't double a dependency that's already fast, deterministic, and safe — a plain value object or a simple, pure in-memory collaborator usually needs no double at all, and adding one just adds indirection. Don't reach for a Mock (behavior verification) when a Stub or Fake (state verification) would answer the same question more robustly to refactoring.

## Key takeaways / mental model
Four doubles, four different jobs: Dummy = never used, Stub = feeds an answer, Mock = verifies an interaction happened, Fake = a real lightweight implementation. Pick by asking "what does this test actually need to know?" — an outcome (favor Stub/Fake, State Verification) or an interaction (Mock, Behavior Verification). Over-reaching for Mock is the most common real-world misuse and a direct cause of Fragile Tests.

## Self-check questions
1. You're testing a `ReportGenerator` that calls `EmailSender.send()` with no return value your test cares about, purely to notify someone the report is ready. Which double would you choose, and why would a Stub be the wrong choice here?
2. A teammate mocks a `Clock` DOC and asserts it was called exactly twice. What's a likely problem with this test, and what would you use instead?
3. Explain, in your own words, why Meszaros considers "Mock" and "Stub" different patterns rather than two names for the same thing.
4. Design a Fake Object for a `FeatureFlagService` DOC. What would make it a genuine Fake rather than a Stub in disguise?

## References
- xUnit Test Patterns: Refactoring Test Code (Gerard Meszaros), Chapter 11: "Using Test Doubles," Chapter 12 (Configurable/Behavior-driven doubles), Chapter 13 (Fake examples).
- See also: `xunit-test-patterns/10` for the State vs. Behavior Verification distinction this lesson leans on, and `xunit-test-patterns/07` for how double misuse causes Fragile Tests.
