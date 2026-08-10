---
id: unit-testing/11
subject: unit-testing
title: Testing Controllers and Application Services
slug: testing-controllers-services
status: drafted
mastery:
seniority: mid
source: Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 7
prerequisites: [unit-testing/05, unit-testing/10]
created: 2026-08-10
updated: 2026-08-10
---

# Testing Controllers and Application Services

## TL;DR
Controllers and application services (the "humble" orchestration layer from `unit-testing/05`) coordinate domain logic and infrastructure but should contain little decision-making of their own; test them with a small number of focused tests that verify orchestration is wired correctly, and let the rich unit tests on the pure domain logic underneath do the heavy lifting — don't try to exhaustively re-test business rules at this layer.

## The idea
Once business logic has been pulled out into a pure, thoroughly-unit-tested domain layer (per `unit-testing/05`'s Humble Object pattern), what's left — the controller or application service that receives a request, calls the domain logic, and talks to infrastructure (database, external APIs) — is deliberately thin. But "thin" doesn't mean "untested." This layer is where wiring bugs live: calling the wrong domain method, passing arguments in the wrong order, forgetting to persist the result, swallowing an exception incorrectly, returning the wrong HTTP status. These bugs are real and common, and they're specifically located in the layer that pure domain unit tests, by construction, never touch.

The right test strategy for this layer is narrower and shallower than for the domain layer: verify that orchestration happens correctly (the right domain method gets called, its result gets persisted, the right response gets returned) without re-deriving every business-rule edge case that the domain layer's own tests already own exhaustively.

## How it works

### The layered picture
```
Controller/Application Service (thin, orchestration)
        |
        v
Domain logic (pure, rich, exhaustively unit-tested — unit-testing/01-09)
        |
        v
Infrastructure (repository, gateway — covered by integration tests, unit-testing/10)
```
Each layer gets a different *kind* and *amount* of test coverage matched to what it actually does. Concretely:

```
class PlaceOrderController:
    def __init__(self, calculator, repository, emailGateway):
        self._calculator = calculator
        self._repository = repository
        self._email = emailGateway

    def handle(self, request):
        try:
            total = self._calculator.calculate(request.subtotal, request.customerType)
        except InvalidSubtotalError:
            return HttpResponse(400, "Invalid subtotal")

        order = Order(customerId: request.customerId, total: total, status: "PLACED")
        self._repository.save(order)
        self._email.sendConfirmation(request.customerEmail, order)
        return HttpResponse(200, {"orderId": order.id, "total": total})
```

The domain logic (`OrderCalculator.calculate`) already has exhaustive unit tests from `unit-testing/05` covering every discount rule and edge case. What's left to verify here is orchestration:

```
test "a valid order request returns 200 with the calculated total":
    calculator = new OrderCalculator()          # real — fast, deterministic
    repo = new InMemoryOrderRepository()         # fake
    emailMock = mock(EmailGateway)               # true external dependency, per unit-testing/08
    controller = new PlaceOrderController(calculator, repo, emailMock)

    response = controller.handle(OrderRequest(subtotal: 200, customerType: "CORPORATE", customerEmail: "a@b.com"))

    assert response.status == 200
    assert response.body.total == 180
    assert repo.findLast().total == 180          # verifies persistence actually happened
    verify(emailMock.sendConfirmation("a@b.com", anyOrder())).wasCalledOnce()

test "an invalid subtotal returns 400 and does not persist or email anything":
    calculator = new OrderCalculator()
    repo = new InMemoryOrderRepository()
    emailMock = mock(EmailGateway)
    controller = new PlaceOrderController(calculator, repo, emailMock)

    response = controller.handle(OrderRequest(subtotal: -10, customerType: "RETAIL", customerEmail: "a@b.com"))

    assert response.status == 400
    assert repo.findLast() == null
    verify(emailMock.sendConfirmation(any(), any())).wasNeverCalled()
```
Notice what these two tests do and don't do: they verify the *happy path wires correctly* (calculation feeds into persistence and email, with the right response) and the *error path short-circuits correctly* (no persistence, no email on invalid input) — but they don't re-test every discount tier or every validation rule; `OrderCalculator`'s own tests already own that exhaustively. Two or three tests here (happy path, one representative error path, maybe one edge case specific to orchestration like "email failure shouldn't prevent the order response") is usually enough — not dozens.

### The specific bug classes this layer's tests should target
- **Wrong arguments passed to the domain layer** — e.g., accidentally passing `request.customerType` where `request.subtotal` was expected; a domain-layer test can't catch this because it only tests the domain function directly with correct arguments.
- **Result not persisted, or persisted incorrectly** — the calculation is right, but the controller forgets to call `save()`, or saves the pre-discount total instead of the post-discount one.
- **Wrong status code or response shape** — the domain logic correctly rejects invalid input, but the controller maps that rejection to a 500 instead of a 400.
- **Side effects happening in the wrong order or under the wrong condition** — e.g., the email gets sent even when persistence fails, or vice versa (as tested in the second example above).

### Worked example: a bug this layer's tests catch (that domain tests can't)
Suppose a developer refactors the controller and accidentally swaps two arguments:
```
order = Order(customerId: request.customerId, total: request.subtotal, status: "PLACED")  # bug: forgot to use `total`!
```
`OrderCalculator`'s own tests still pass — the calculation itself is untouched and still correct in isolation. But the orchestration test `assert repo.findLast().total == 180` now fails, because the controller is persisting the raw subtotal (200) instead of the calculated total (180). This is exactly the class of bug this layer's tests exist to catch, and exactly the class of bug that only testing the domain layer in isolation would miss entirely.

## Pros
- Targets a real, distinct class of bugs (wiring/orchestration mistakes) that neither pure domain unit tests nor infrastructure integration tests are positioned to catch.
- Stays cheap: a handful of tests per controller/service, not an exhaustive re-derivation of business rules, because the heavy lifting is already done by the domain layer's tests.
- Reinforces the Humble Object boundary (`unit-testing/05`) by making it obvious, through the test list itself, when a controller has accumulated too much real logic (if you find yourself wanting many edge-case tests here, logic has probably leaked out of the domain layer).

## Cons
- Requires the Humble Object split to already be in place — applying this lesson's thin-testing approach to a controller that still has tangled business logic in it leaves that logic under-tested.
- The judgment call ("is this orchestration or is this actually a business rule that leaked into the controller?") isn't always obvious, especially as a codebase evolves and small conditionals creep into controllers over time.
- Using a mix of fakes and mocks at this layer (as in the worked example) requires the reader to already understand the taxonomy from `unit-testing/07`/`unit-testing/08` to interpret the test correctly.

## Alternatives
- **Test the controller purely through end-to-end/integration tests (real HTTP, real DB)** — more realistic, but far slower, and doesn't isolate orchestration bugs from domain-logic bugs or infrastructure bugs when a test fails, making diagnosis slower.
- **Skip controller-level tests entirely, relying only on domain unit tests plus manual QA** — cheaper upfront, but leaves the exact bug class described above (wiring mistakes) uncaught until a human notices in production or QA.
- **Snapshot-test the full HTTP response** — captures the entire response shape at once and diffs against a saved snapshot; convenient for catching accidental response-shape changes, but less precise about *why* a change happened than the explicit assertions shown here.

## When to use it
Write a small, focused set of orchestration tests (happy path, primary error path, any order-of-operations edge cases specific to this layer) for every controller or application service, once its business logic has been extracted per `unit-testing/05`.

## When NOT to use it
Don't try to exhaustively cover every business-rule edge case at the controller level — that coverage belongs to, and is cheaper at, the domain layer. If you find yourself wanting many edge-case tests at the controller level to feel confident, that's usually a sign logic hasn't actually been extracted yet, and the fix is to revisit the Humble Object split, not to add more controller tests.

## Key takeaways / mental model
A controller's tests should answer "did I wire the pieces together correctly?" — not "is the business logic correct?" (that's the domain layer's job) and not "does the real database actually work?" (that's the integration layer's job, `unit-testing/10`). A short, focused test list at this layer is a feature, not a gap — it's a sign the Humble Object split is doing its job.

## Self-check questions
1. A controller test suite has grown to 25 tests covering many discount-percentage edge cases. What does this lesson suggest is likely wrong, and what would you check first?
2. In the worked "wrong argument" bug example, explain precisely why `OrderCalculator`'s own unit tests kept passing even though the system was broken. What layer's test caught it, and why was that layer positioned to catch it when the domain layer's tests weren't?
3. Design (in words) the minimal set of orchestration tests you'd write for a `CancelOrderController` that (a) looks up an order, (b) rejects cancellation if the order has already shipped, (c) otherwise marks it cancelled and refunds the payment via an external gateway. Which collaborators would be fakes vs. mocks, per `unit-testing/07`/`unit-testing/08`?

## References
- Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 7: "Refactoring Toward Valuable Unit Tests" (Humble Object applied to controllers/application services).
