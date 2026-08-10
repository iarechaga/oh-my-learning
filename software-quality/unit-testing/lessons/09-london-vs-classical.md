---
id: unit-testing/09
subject: unit-testing
title: London vs. Classical Schools in Practice
slug: london-vs-classical
status: drafted
mastery:
seniority: senior
source: Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 2
prerequisites: [unit-testing/07, unit-testing/08]
created: 2026-08-10
updated: 2026-08-10
---

# London vs. Classical Schools in Practice

## TL;DR
The London (mockist) school isolates the class under test by mocking every one of its collaborators, defining a "unit" as one class; the classical (Detroit/Chicago) school isolates test *cases* from each other but freely uses real collaborators within a single test, defining a "unit" as a unit of behavior that may span several classes, and mocks only true external dependencies. Khorikov advocates the classical school because, per `unit-testing/04` and `unit-testing/08`, it produces tests with much better resistance to refactoring — but understanding both schools, and where each genuinely fits, is necessary to make that case rather than just assert it.

## The idea
"Should I mock this collaborator?" is a question every test author faces constantly, and two coherent, historically distinct schools of thought answer it differently — not out of carelessness, but from different starting definitions of what a "unit" is and what "isolation" means.

- **London school** (also called "mockist," associated with Steve Freeman and Nat Pryce's *Growing Object-Oriented Software, Guided by Tests*): a unit is a single class. Isolating a unit means replacing *every* dependency of that class — internal or external — with a test double, so the class is tested completely alone. Tests verify how the class *interacts* with its collaborators, because with everything mocked, interaction is often the only thing left to check.
- **Classical school** (also called "Detroit" or "Chicago," the original style from the early xUnit/JUnit tradition, e.g. Kent Beck): a unit is a unit of *behavior*, which may legitimately span multiple classes working together. Isolating a unit means isolating *test cases from each other* (per `unit-testing/06` — no shared state between tests), not isolating a class from its real collaborators. Only genuinely shared, out-of-process, or slow/non-deterministic dependencies get replaced with doubles.

Both schools use the word "isolation" — they just isolate different things (a class from its collaborators, vs. a test case from other test cases). That terminology collision is the single biggest source of confusion when people argue about mocking without naming which school they mean.

## How it works

### The same feature, tested both ways
Feature: `OrderService.placeOrder()` validates the order, calculates the total via `PricingCalculator`, and persists it via `OrderRepository` (an in-memory-backed repository in this example, not a live database — a genuinely internal collaborator either way).

**London-school version — every collaborator mocked:**
```
test "placeOrder calculates total and saves the order":
    pricingMock = mock(PricingCalculator)
    when(pricingMock.calculate(200, "CORPORATE")).thenReturn(180)
    repoMock = mock(OrderRepository)

    service = new OrderService(pricingMock, repoMock)
    service.placeOrder(customerType: "CORPORATE", subtotal: 200)

    verify(pricingMock.calculate(200, "CORPORATE")).wasCalledOnce()
    verify(repoMock.save(argThat(order => order.total == 180))).wasCalledOnce()
```
This isolates `OrderService` completely: neither `PricingCalculator` nor `OrderRepository` runs for real. The test verifies *that OrderService correctly orchestrates its collaborators* — a legitimate thing to want to know, especially for a class whose entire job is coordination.

**Classical-school version — real collaborators, doubles only at the true system boundary:**
```
test "placing a corporate order with a $200 subtotal results in a $180 total being saved":
    repo = new InMemoryOrderRepository()          # fake, not mock — see unit-testing/07
    service = new OrderService(new PricingCalculator(), repo)   # real pricing calculator
    service.placeOrder(customerType: "CORPORATE", subtotal: 200)
    saved = repo.findLast()
    assert saved.total == 180
```
This test uses the *real* `PricingCalculator` (a fast, deterministic, in-memory collaborator — nothing to gain by mocking it) and a fake in-memory repository (standing in only because a real database would be slow/external, per `unit-testing/07`). It asserts on the actual outcome, not on how the pieces talked to each other.

### Why the classical test wins on resistance to refactoring
Suppose `PricingCalculator`'s internal algorithm changes (say, it's rewritten to use a lookup table instead of an if/else chain), or `OrderService` is refactored to call `PricingCalculator` twice for logging purposes before finalizing the total. Neither change affects the final `total` value.

- The **classical test** doesn't care — it only reads `saved.total`, so it stays green through both refactors, exactly matching `unit-testing/04`'s discipline.
- The **London test** breaks on the second refactor immediately: `verify(pricingMock.calculate(...)).wasCalledOnce()` fails because the call now happens twice. Nothing is actually wrong with the code — the assertion is coupled to an implementation detail (how many times, and how, `OrderService` happens to call its collaborator).

This is the concrete mechanism behind Khorikov's preference: London-school tests, by mocking every collaborator including purely internal ones, systematically produce exactly the implementation-coupled assertions that `unit-testing/04` and `unit-testing/08` warn against, unless the practitioner is extremely disciplined about which interactions to verify.

### Where the London school genuinely earns its keep
The London school isn't simply "wrong" — it has a real, coherent motivation that classical testing doesn't fully address: when a class's entire responsibility *is* orchestration (deciding which collaborators to call, in what order, with what arguments — with little other logic of its own), verifying those interactions IS verifying the class's actual behavior, not an incidental implementation detail. It also offers a practical benefit for top-down, outside-in TDD (as in Freeman & Pryce's GOOS): you can write a test for a not-yet-built class by mocking its collaborators before those collaborators exist at all, letting the mocks specify the collaborators' contracts before you implement them.

The classical rebuttal, and Khorikov's practical guidance: even for an orchestration-heavy class, most of that "orchestration" typically resolves down to a smaller number of *true external-dependency* calls (matching `unit-testing/08`'s boundary test) — mock only those, and let the purely internal coordination be exercised (and implicitly verified) through real objects and an output assertion, as in the classical example above.

### A litmus test to classify your own instinct
When you catch yourself reaching for a mock, ask: "if I ran this class's real collaborator instead of a double, would the test still be fast and deterministic?" If yes (a plain in-memory value object, a pure calculation), the classical answer is: just use the real thing. If no (real network I/O, real disk access, genuine non-determinism), a double is warranted — and per `unit-testing/08`, whether it should be a *mock specifically* (interaction verified) or a stub/fake (data-only) depends on whether the interaction itself crosses your system's boundary.

## Pros
- **London school**: naturally supports outside-in TDD where collaborators don't exist yet; makes a class's coordination responsibilities explicit and directly testable; can pinpoint failures to a very specific interaction.
- **Classical school**: produces tests that survive refactors (`unit-testing/04`), tests closer to real end-to-end behavior with fewer doubles to maintain, and a smaller, simpler mental model (mock only true external dependencies).

## Cons
- **London school**: prone to brittleness when applied indiscriminately to every collaborator (per `unit-testing/04`/`unit-testing/08`); large mock setups reduce maintainability (per `unit-testing/03`); can produce tests that pass while the *integrated* system is actually broken (each piece individually does what its mock-verified contract says, but the pieces don't actually fit together — a gap covered by integration testing, `unit-testing/10`).
- **Classical school**: needs the boundary judgment call from `unit-testing/08` (what counts as "true external") to avoid accidentally pulling in slow dependencies; a class whose job really is pure orchestration can end up under-tested if the discipline to test orchestration correctness is dropped rather than adapted.

## Alternatives
This lesson *is* the comparison of the two dominant alternatives to each other; there isn't a meaningful third school with comparable adoption, though teams commonly blend them pragmatically — classical by default, London-style interaction tests reserved narrowly for genuinely orchestration-only classes, which is close to Khorikov's actual recommendation once the two schools' terminology is untangled.

## When to use it
Default to the classical school for the bulk of a test suite — real collaborators wherever they're fast and deterministic, test doubles reserved for true external dependencies (`unit-testing/08`). Reach for a London-style, fully-mocked test specifically when a class's entire responsibility is coordinating calls to collaborators with little independent logic of its own, or when doing genuinely outside-in TDD against not-yet-built collaborators.

## When NOT to use it
Don't adopt London-school mocking as a blanket default under the belief that "more isolation is always better" — per `unit-testing/03` and `unit-testing/04`, that trade-off actively sacrifices resistance to refactoring for a form of isolation (isolating a class from its real collaborators) that the classical school gets for free within a single test case without needing doubles at all.

## Key takeaways / mental model
Both schools want tests that are isolated and trustworthy — they disagree about *what* needs isolating: a class from its collaborators (London) or a test case from other test cases (classical). Default classical; use targeted, boundary-respecting mocks (`unit-testing/08`) rather than blanket London-style mocking, and reserve full interaction-based testing for classes whose entire job is orchestration.

## Self-check questions
1. In the worked `OrderService` example, explain precisely why the London-school test breaks when `OrderService` is refactored to call `PricingCalculator` twice, while the classical-school test doesn't. What does this reveal about what each test is actually coupled to?
2. Describe a real class from a codebase you know where the London-school argument (its whole job is orchestration) genuinely applies. What would you verify, and would that verification survive a refactor that changed the order of two independent calls?
3. A teammate says "classical school just means don't use mocks." Correct this misunderstanding using this lesson's definitions — what does classical actually isolate, and where does it still use test doubles?

## References
- Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 2: "What Is a Unit Test?"
- Growing Object-Oriented Software, Guided by Tests (Steve Freeman, Nat Pryce) — the canonical London-school reference.
