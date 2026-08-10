---
id: unit-testing/07
subject: unit-testing
title: Types of Test Doubles and Trade-offs
slug: test-doubles-trade-offs
status: drafted
mastery:
seniority: mid
source: Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 5
prerequisites: [unit-testing/06]
created: 2026-08-10
updated: 2026-08-10
---

# Types of Test Doubles and Trade-offs

## TL;DR
"Mock" is used loosely to mean any test double, but there are five distinct kinds — dummy, stub, spy, mock, and fake — each with a different purpose and a different effect on test fragility. Knowing which one you actually need (and reaching for the least powerful one that does the job) is what separates a resilient test suite from a brittle, over-mocked one.

## The idea
A **test double** is any object substituted for a real collaborator during a test — the umbrella term (borrowed from "stunt double") that Khorikov, following Gerard Meszaros's *xUnit Test Patterns*, breaks into five precise categories. The word "mock" gets used colloquially for all of them ("I'll just mock that out"), which hides an important distinction: some doubles only exist to satisfy a constructor signature and are never inspected (dummy), some feed canned data into the system under test (stub), and some exist specifically so the test can verify a call happened (mock, spy). Conflating these leads directly to the over-mocking failure mode from `unit-testing/04` — using a mock (which asserts on interactions, coupling the test to implementation) in a place where a stub (which just supplies data, coupling the test only to the resulting behavior) would have done the job with far less fragility.

## How it works

### The five kinds, defined with the same example
Take a `ReportGenerator` that depends on a `CustomerRepository` to look up customer data and an `EmailService` to send the finished report.

**1. Dummy** — passed in only because the API requires *something*, never actually used by the code path under test.
```
test "report title includes the report name":
    dummyEmailService = new NullEmailService()   # never called in this test
    generator = new ReportGenerator(repo: realRepo, emailService: dummyEmailService)
    report = generator.buildTitle("Q3 Sales")
    assert report == "Q3 Sales Report"
```
The `dummyEmailService` exists purely to satisfy the constructor; this test doesn't exercise anything about email.

**2. Stub** — provides canned answers to calls made during the test; the test never asserts anything about the stub itself, only about the resulting output.
```
test "report includes all active customers":
    stubRepo = new StubCustomerRepository(returns: [Customer("Ana", active: true), Customer("Bo", active: false)])
    generator = new ReportGenerator(repo: stubRepo, emailService: dummyEmailService)
    report = generator.build()
    assert report.customerNames == ["Ana"]
```
The stub's job is purely to feed a known, controlled input into the system under test — the assertion checks `report`, never the stub.

**3. Spy** — a stub that *additionally* records how it was used, so the test can inspect that record afterward (without necessarily failing the test via a strict `verify()` — that's the mock's job, see below).
```
test "building a report records that the repository was queried once":
    spyRepo = new SpyCustomerRepository(returns: [])
    generator = new ReportGenerator(repo: spyRepo, emailService: dummyEmailService)
    generator.build()
    assert spyRepo.callCount == 1          # inspected manually, after the fact
```
A spy is a passive recorder; the test decides what (if anything) to check about the recording, and can mix that with other, output-based assertions.

**4. Mock** — like a spy, but with built-in expectation-setting and automatic verification; you declare up front "this call must happen with these arguments," and the mock framework fails the test itself if it doesn't.
```
test "building a report sends an email notification":
    mockEmailService = mock(EmailService)
    generator = new ReportGenerator(repo: stubRepo, emailService: mockEmailService)
    generator.build()
    verify(mockEmailService.send(anyReport())).wasCalledOnce()   # framework asserts this
```
This is the double most directly implicated in `unit-testing/04`'s brittleness warning: because it fails the test automatically on any interaction mismatch, careless use of mocks against internal collaborators (rather than true external dependencies) is what produces refactor-breaking tests.

**5. Fake** — a working, simplified implementation of the real dependency, usually swapping a slow/external backend for a fast in-memory one, but preserving real behavior.
```
class InMemoryCustomerRepository:
    def __init__(self):
        self._customers = {}
    def save(self, customer):
        self._customers[customer.id] = customer
    def findActive(self):
        return [c for c in self._customers.values() if c.active]

test "report includes customers saved as active":
    fakeRepo = new InMemoryCustomerRepository()
    fakeRepo.save(Customer("Ana", active: true))
    generator = new ReportGenerator(repo: fakeRepo, emailService: dummyEmailService)
    report = generator.build()
    assert report.customerNames == ["Ana"]
```
Unlike a stub (which returns a fixed, hardcoded answer regardless of what's "saved"), a fake actually implements the save/query contract, just against memory instead of a real database — this makes it reusable across many tests and closer to real behavior, at the cost of being more work to build and maintain correctly.

### Why the taxonomy matters: matching the double to the job
The practical rule that falls out of this taxonomy: **use the least powerful double that lets the test express what it actually needs to check.**
- Need to satisfy a constructor and nothing else? **Dummy.**
- Need to feed the system under test some data so you can assert on the *output*? **Stub.**
- Need to confirm a call happened, but the assertion is secondary to output checks? **Spy** (assert manually, mix with output assertions).
- Need a call to a *true external dependency* to be the primary thing under test (e.g., "an email must be sent")? **Mock** — but reserve this for genuine external-effect verification, per `unit-testing/04` and `unit-testing/08`.
- Need realistic, stateful behavior from a slow/external dependency, reused across many tests? **Fake.**

Reaching for a mock by default (the most common mistake) tends to over-verify interactions with things that are really internal implementation details, producing exactly the refactor-breaking brittleness from `unit-testing/04`. Reaching for a stub or fake instead, wherever the test's real concern is "what does the system produce," keeps the test coupled to behavior, not mechanism.

## Pros
- Precise vocabulary lets a team discuss test design ("this should be a stub, not a mock") instead of arguing past each other with "mock" meaning five different things.
- Choosing the least powerful double by default naturally steers toward behavior-focused, refactor-resistant tests.
- Fakes, once built, are reusable investments that make many future tests both fast and realistic.

## Cons
- Five categories is more conceptual overhead than "just mock everything," and takes deliberate practice to apply consistently.
- Building a good fake (one that faithfully mirrors real behavior, including edge cases and error conditions) is nontrivial work and can itself have bugs that mask real ones.
- Some mocking frameworks blur these categories by default (e.g., a "mock" object that can also stub return values), which can obscure which role a given double is actually playing in a specific test.

## Alternatives
- **Real objects everywhere, no doubles** — the classical/Detroit-school default (`unit-testing/09`) wherever the real collaborator is fast and deterministic (plain in-memory value objects); avoids the whole taxonomy question by not needing doubles at all.
- **Contract tests against the real external system** — instead of doubling an external dependency, run a smaller number of tests against the real thing (or a realistic sandbox) to make sure the fake/stub's assumed behavior still matches reality; a complement to fakes, not a replacement, addressing the risk that a fake silently drifts from the real implementation.
- **Record/replay testing (VCR-style)** — records real interactions with an external system once, then replays the recorded responses as a stub in future runs; a middle ground between a hand-written stub and a full integration test.

## When to use it
Use this taxonomy any time you're about to reach for "a mock" — pause and ask which of the five you actually need based on what the test is trying to verify (output vs. an interaction with a true external effect). Quick decision guide: only need the test to compile/construct -> dummy; need controlled input data -> stub; need to double-check a call happened, secondary to output -> spy; verifying a call to a true external effect is the point of the test -> mock; need realistic, reusable, stateful behavior for a slow dependency -> fake.

## When NOT to use it
Don't invest in building a fake for a dependency used in only one or two tests — a simple stub is cheaper and the reuse benefit of a fake won't materialize. Don't use a mock/spy to verify calls to collaborators that are purely internal implementation choices (see `unit-testing/04`) regardless of which double "feels" convenient in your framework.

## Key takeaways / mental model
Five words, five distinct jobs: dummy (placeholder), stub (feeds data), spy (records, checked manually), mock (asserts automatically), fake (working lightweight implementation). Default to the least powerful one that lets the test check what actually matters — behavior and output, not internal wiring.

## Self-check questions
1. You need to test that `ReportGenerator.build()` returns the right customer names given a repository that has two active and one inactive customer. Which test double is the right fit, and why would using a mock instead be a worse choice here?
2. Explain the difference between a spy and a mock in terms of *when* the test fails on a mismatched call, and why that difference matters for readability and debugging.
3. Your team has a fake `InMemoryPaymentGateway` used across 40 tests. The real `PaymentGateway` recently added a new required field to its response. What risk does this scenario illustrate about fakes, and how would you mitigate it?

## References
- Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 5: "Mocks and Test Fragility."
- xUnit Test Patterns (Gerard Meszaros) — origin of the dummy/stub/spy/mock/fake taxonomy.
