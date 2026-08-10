---
id: unit-testing/10
subject: unit-testing
title: Integration Testing Around External Systems
slug: integration-testing-boundaries
status: drafted
mastery:
seniority: senior
source: Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 10
prerequisites: [unit-testing/03, unit-testing/06]
created: 2026-08-10
updated: 2026-08-10
---

# Integration Testing Around External Systems

## TL;DR
Integration tests verify that your code correctly collaborates with real out-of-process dependencies (a real database, a real message queue) and are indispensable at the boundary where unit tests, by design, use doubles instead — but because they're slow and less isolated, you write far fewer of them, aimed specifically at the seams and failure modes that unit tests structurally cannot cover.

## The idea
Unit tests, per `unit-testing/06` and `unit-testing/09`, keep collaborators real only when they're fast and deterministic, and replace true external dependencies (a real database, a real payment gateway) with doubles. That's the right trade-off for the bulk of a suite — but it leaves a real gap: nothing has actually verified that your SQL query returns the row you expect from *your actual schema*, or that your code handles the *real* error format your payment gateway returns on a declined card. A test suite entirely made of unit tests with everything external stubbed can be 100% green while the system is fundamentally broken against the real world, because every stub encodes an *assumption* about how the real dependency behaves, and that assumption is never itself checked.

Integration tests close this gap by running against the real (or a realistic, close-to-real) version of the dependency. They trade speed and isolation for a kind of confidence unit tests cannot provide: confidence that the seams actually fit.

## How it works

### What counts as the boundary, and why it's the right place to concentrate integration tests
The "boundary" of your system is any point where your code hands off to something out-of-process: a database, a filesystem, a network call to another service, the system clock/OS (partially — `unit-testing/12` covers this specifically), a message queue. Business logic sitting entirely on your side of that boundary is already well-covered by fast unit tests (`unit-testing/01`–`unit-testing/09`); what's specifically under-tested without integration tests is the handoff itself — the exact query, the exact serialization format, the exact way errors surface.

Applying the Humble Object split from `unit-testing/05` sharpens this further: once business logic is pulled into a pure, thoroughly unit-tested layer, what's *left* at the boundary (the "humble" persistence/IO layer) is exactly what integration tests should target — not because it's more important, but because it's the only layer left that unit tests structurally cannot reach.

### Worked example: a repository, tested at two different layers
```
class OrderRepository:
    def __init__(self, db):
        self._db = db
    def save(self, order):
        self._db.execute(
            "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)",
            order.customerId, order.total, order.status
        )
    def findById(self, orderId):
        row = self._db.queryOne("SELECT * FROM orders WHERE id = ?", orderId)
        return Order.fromRow(row) if row else None
```
A unit test with a fake (`InMemoryOrderRepository`, per `unit-testing/07`) verifies that *code calling the repository* behaves correctly given a save/find contract — fast, and appropriate for the bulk of the suite. But it cannot catch a typo in the real SQL (`orders` misspelled as `order`), a column type mismatch, or a broken `Order.fromRow` mapping against the actual schema. Only a test against a real database can:
```
test "saving and then finding an order round-trips correctly":
    db = testDatabase()                      # real DB, dedicated to tests
    repo = new OrderRepository(db)
    order = new Order(customerId: 7, total: 180, status: "PLACED")

    repo.save(order)
    found = repo.findById(order.id)

    assert found.customerId == 7
    assert found.total == 180
    assert found.status == "PLACED"
```
This test is slower (a real connection, a real query round-trip) and needs infrastructure the unit tests don't (a running test database), but it verifies something the fake fundamentally cannot: that the real SQL and real schema actually agree with what the rest of the code assumes.

### Keeping integration tests fast and isolated enough to trust
The determinism principles from `unit-testing/06` still apply at the integration layer, just achieved differently:
- **Isolate each test's data.** Wrap each test in a transaction that's rolled back at the end (so no test's writes leak into the next), or generate unique keys/IDs per test run instead of hardcoding them.
- **Use a dedicated test database/schema**, never a shared development or production database — a test that could accidentally corrupt real data is not a test you can run freely or trust.
- **Reset to a known state before each test**, rather than assuming a particular starting state left over from a previous run.
- **Prefer a local, disposable instance** (e.g., a containerized database spun up for the test run) over a shared remote environment, so tests don't compete with other developers' runs or depend on network reliability.

### Deciding what NOT to cover with an integration test
Because integration tests are expensive (in run time and in infrastructure), they should be aimed narrowly at what unit tests can't verify — the actual query/schema/serialization correctness — not re-derive business-rule coverage that unit tests already own. A common mistake is writing an integration test that re-checks the discount-calculation logic from `unit-testing/03`'s worked example against a real database, duplicating unit-test coverage while paying integration-test costs for no extra confidence. The discount math doesn't change based on whether the database is real; only the persistence handoff does.

**Worked contrast:**
- Redundant integration test (re-verifies logic already covered by a fast unit test): "an order with a corporate customer, saved and reloaded from the real DB, has a $180 total." (Assuming the discount calculation itself is untouched by persistence, this doesn't need a real DB to catch a bug in the discount math — a unit test already owns that.)
- Well-aimed integration test (verifies exactly the persistence seam): "saving and reloading an order via the real repository preserves every field correctly, including the `status` enum's exact on-disk representation."

### Testing third-party APIs specifically
When the external dependency is a third-party API (a payment gateway, an email provider) rather than your own database, running the real integration test against the live third-party service on every CI run is often impractical (rate limits, cost, non-determinism, requiring live credentials). Common, more practical patterns: a small number of integration tests against a sandbox/test environment the provider offers (most payment gateways provide one specifically for this), combined with contract tests or recorded-response replay (mentioned in `unit-testing/07`) for the bulk of day-to-day runs, reserving the real sandbox calls for a slower, less frequent verification pass (e.g., nightly rather than on every commit).

## Pros
- Catches an entire class of real bugs (schema mismatches, serialization errors, real error-format handling) that unit tests, using doubles by design, structurally cannot catch.
- Gives genuine confidence that the seams between your code and the outside world actually work, not just that your code's assumptions about them are internally consistent.
- Forces explicit, deliberate handling of infrastructure setup/teardown, which often surfaces environment or configuration issues before they hit production.

## Cons
- Much slower than unit tests (network/disk I/O, connection setup) — a suite dominated by integration tests becomes too slow to run on every save, eroding fast feedback (`unit-testing/03`).
- Requires real infrastructure (a running database, network access to a sandbox), which adds setup complexity and potential flakiness sources (`unit-testing/06`) that pure unit tests don't have.
- Easy to over-invest in, duplicating business-logic coverage that a fast unit test already owns, without adding proportional confidence.

## Alternatives
- **Contract tests** — verify that a fake/stub's assumed behavior matches the real dependency's actual contract, run separately (and less often) from the main suite; narrower and often faster than full integration tests while still catching drift between assumption and reality.
- **End-to-end tests** — go a layer further than integration tests, exercising the whole system (UI through to database) as a real user would; even slower and more brittle, reserved for a small number of critical user journeys rather than a substitute for either unit or integration tests.
- **Staging/production smoke tests** — a handful of lightweight checks run against a real deployed environment after release, catching deployment/configuration issues that no pre-deploy test (unit or integration) can see, at the cost of only running post-deploy.

## When to use it
Write an integration test specifically for the handoff points identified via the Humble Object split (`unit-testing/05`): real database queries, real API calls, real message serialization. Aim for enough of these to cover every distinct seam at least once, not to re-verify business logic already covered elsewhere.

## When NOT to use it
Don't use an integration test to verify business logic that has no real dependency on the actual external system's behavior — a fast unit test with a fake already covers that more cheaply (`unit-testing/07`). Don't let integration tests become the primary safety net for a codebase; per `unit-testing/13`, they should be a comparatively small layer on top of a much larger base of fast unit tests.

## Key takeaways / mental model
Unit tests answer "does my logic do the right thing, assuming my dependencies behave as I assume?" Integration tests answer the question unit tests can't: "do my dependencies actually behave the way I assumed?" Aim integration tests precisely at that gap — the seams — and keep them few, isolated, and deliberately not duplicating unit-level coverage.

## Self-check questions
1. A team's integration test suite re-tests every business rule (discounts, validation, pricing tiers) against a real database, and takes 40 minutes to run. Using this lesson's framing, what's misallocated here, and how would you restructure the coverage?
2. Explain why a fake repository (`unit-testing/07`) passing all its unit tests does not guarantee that the real repository's SQL is correct. What specific kind of bug would only an integration test catch?
3. You're integrating with a third-party payment gateway that has strict API rate limits and no reliable sandbox environment. Propose a testing strategy that still gives you confidence about the integration without hammering the real API on every commit.

## References
- Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 10: "Testing the Database."
