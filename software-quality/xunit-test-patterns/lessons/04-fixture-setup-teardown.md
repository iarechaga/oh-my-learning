---
id: xunit-test-patterns/04
subject: xunit-test-patterns
title: Fixture Setup and Teardown Patterns
slug: fixture-setup-teardown
status: drafted
mastery:
seniority: mid
source: xUnit Test Patterns: Refactoring Test Code (Gerard Meszaros), Chapters 5-6
prerequisites: [xunit-test-patterns/02]
created: 2026-08-10
updated: 2026-08-10
---

# Fixture Setup and Teardown Patterns

## TL;DR
There are two fundamentally different strategies for getting a test's fixture into place — **Fresh Fixture** (build it from scratch, per test) and **Shared Fixture** (reuse one fixture across many tests) — and each has a matching teardown discipline. Meszaros's strong default recommendation is Fresh Fixture: it costs more setup time per test but buys independence between tests, which is usually the better trade because Shared Fixture is the single biggest source of Erratic Tests in real suites.

## The idea
Building a fixture (the known world a test needs, per `xunit-test-patterns/01`) costs something — time to write, time to run, sometimes real infrastructure (a database, a file system). The natural instinct, especially under time or performance pressure, is to build the fixture once and reuse it across many tests: create one user account, run every "user" test against it. This is **Shared Fixture**, and it seems efficient, but it introduces a hazard that dominates its savings: tests that share mutable state can affect each other's outcomes depending on execution order, which is one of the most common root causes of an **Erratic Test** (a test that sometimes passes, sometimes fails, with no code change — see `xunit-test-patterns/07`).

**Fresh Fixture** is the alternative: every test builds its own private fixture from nothing, uses it, and (if needed) tears it down, so no test can ever be affected by what another test did. The lesson is fundamentally about this trade-off — setup cost and speed versus independence and reliability — and when each side of the trade-off should win.

## How it works

### Fresh Fixture: build it, use it, discard it
```
test "withdraw fails when balance is insufficient":
    account = new Account(balance=50)      # fresh, private fixture

    result = account.withdraw(100)

    assert result.success == false
    assert account.balance == 50
```

Every test constructs its own `Account`. No test can leak state into another, because nothing is shared. This is the safe default and should be your starting point for essentially all unit-level tests, especially in-memory ones where construction is cheap.

### Shared Fixture: the tempting shortcut and its trap
```
# fixture built ONCE for the whole test class/suite
beforeAll:
    sharedAccount = new Account(balance=50)

test "withdraw fails when balance is insufficient":
    result = sharedAccount.withdraw(100)
    assert result.success == false

test "deposit increases balance":
    sharedAccount.deposit(20)
    assert sharedAccount.balance == 70   # WRONG if the first test already mutated balance,
                                          # or if test execution order changes
```

If these two tests run in the order shown, and the first test's `withdraw(100)` was rejected (balance unchanged at 50), the second test's assertion of `70` accidentally passes. But if a *third* test is added later that successfully withdraws money from `sharedAccount`, or if the test runner parallelizes or reorders tests, the second test's assumption "balance starts at 50" silently breaks — and the failure has nothing to do with a real bug in `deposit`. This is the archetypal Erratic Test caused by shared, mutable fixture state, and it's exactly the trap Meszaros warns against.

### When Shared Fixture is worth the risk: Prebuilt Fixture for expensive setup
Sometimes fixture construction is genuinely expensive — spinning up a real database schema, loading a large reference dataset, starting an external process. Rebuilding it fresh for every single test can make a suite too slow to run often (see `xunit-test-patterns/08`). Meszaros's compromise pattern here is **Prebuilt Fixture**: build the expensive, *read-only* part of the fixture once (e.g., a database schema with reference/lookup tables that no test mutates), and combine it with a Fresh Fixture for anything the test actually exercises or mutates.

```
beforeAll:
    testDb = provisionSchemaWithReferenceData()   # expensive, but read-only — shared safely

test "order total includes the correct tax rate for CA":
    order = new Order(state="CA", subtotal=100)   # fresh, per-test, mutable fixture
    result = taxCalculator.calculate(order, testDb.taxRatesTable)

    assert result.total == 107.25
```

The key discriminator: it's safe to share a fixture across tests **only if no test mutates it**. The moment any test writes to shared state, Prebuilt Fixture degrades back into unsafe Shared Fixture.

### Teardown strategies matched to each approach
- **Fresh Fixture** usually needs little explicit teardown for in-memory objects (garbage collected automatically), but *does* need explicit teardown for external resources acquired during setup — an open file, a database transaction, a temp directory — using an **Automated Teardown** pattern (framework-level `afterEach`/`finally` hooks) so cleanup can't be forgotten even if the test fails partway through.
- **Shared Fixture / Prebuilt Fixture** needs teardown scoped to the *whole suite*, not each test (`afterAll`), and — critically — needs a guarantee that individual tests cannot mutate it, often enforced by using immutable data, defensive copies, or running mutating operations inside a transaction that's rolled back after each test (**Table Truncation Teardown** or the transaction-rollback variant is a common concrete technique for database fixtures).

### Worked example: the transaction-rollback compromise
A common way to get Fresh-Fixture-like independence with Shared-Fixture-like speed for database-backed tests:

```
beforeEach:
    transaction = testDb.beginTransaction()

test "..." :
    # fixture setup, exercise, and verify all happen inside the open transaction

afterEach:
    transaction.rollback()   # discards ALL writes, however many tests wrote
```

Each test *appears* to get a Fresh Fixture (a clean database state) without paying the full cost of re-provisioning the schema from scratch — the expensive schema/reference-data setup is Prebuilt Fixture (shared, read-only, done once), and the per-test mutations are wrapped in a transaction that's always rolled back. This is one of the most common real-world compromises between the two strategies.

## Pros
- Fresh Fixture: complete test independence, tests can run in any order or in parallel, failures are always attributable to the SUT rather than fixture leakage.
- Shared/Prebuilt Fixture: substantial speed savings when fixture construction is genuinely expensive, and reference/lookup data is often naturally read-only, making the sharing safe.

## Cons
- Fresh Fixture: setup cost is paid on every single test; for expensive fixtures (real databases, external services) this can make the suite slow enough that people stop running it locally.
- Shared Fixture: order-dependence and cross-test interference are subtle to spot, especially as a suite grows and more tests touch the same shared object over time — the bug often appears months after the fixture was introduced, far from its cause.

## Alternatives
- **In-memory Fake DOCs instead of real infrastructure** (see `xunit-test-patterns/05`) — sidesteps the whole Fresh-vs-Shared trade-off for many tests by replacing the expensive real dependency (a database, an external API) with a fast, fresh, in-memory Fake Object, so Fresh Fixture stays cheap even when the "real" DOC would have been expensive.
- **Test containers / ephemeral environments** — spin up a real, isolated instance of a dependency (a containerized database) per test run or per test class; a middle ground that keeps realism higher than a Fake while still avoiding cross-test-suite sharing.
- **Object Mother / Test Data Builder** (see `xunit-test-patterns/09`) — addresses a related but distinct problem: making fixture *construction code* itself readable and reusable, independent of whether the fixture is fresh or shared.

## When to use it
Default to Fresh Fixture for essentially all unit-level tests — the independence is worth the setup cost, and modern in-memory construction is usually fast enough that the cost is negligible. Reach for Prebuilt Fixture only for genuinely expensive, read-only setup (schema, reference data), and pair it with a mechanism (transactions, defensive copies) that guarantees no test can mutate the shared part.

## When NOT to use it
Never use Shared Fixture for anything a test mutates unless you have an explicit, verified reset mechanism between tests (transaction rollback, full re-seed) — "we're careful not to mutate it" is not a mechanism, it's a hope, and it erodes the first time a new team member doesn't know the rule.

## Key takeaways / mental model
Ask of every fixture: "can any test mutate this?" If yes, it must be Fresh (or reset deterministically between tests). If genuinely no (pure reference data), it's safe to share and prebuild for speed. Erratic Tests are the tell-tale symptom of getting this classification wrong.

## Self-check questions
1. You inherit a test suite where tests pass individually but fail when run as a full suite, in a way that changes depending on run order. Using this lesson's vocabulary, what's your first hypothesis and how would you confirm it?
2. Describe a fixture in a codebase you know that is genuinely safe to share across tests, and explain specifically why no test mutates it.
3. Design a teardown strategy for a test suite that needs realistic relational data but must run in under 5 seconds for 200 tests. What would you share, what would you keep fresh, and how would you reset between tests?
4. Why does Meszaros treat "prebuilt but read-only" as a distinct, safer category from ordinary Shared Fixture, rather than just a variant of the same risky pattern?

## References
- xUnit Test Patterns: Refactoring Test Code (Gerard Meszaros), Chapter 5: "Test Fixture, Prebuilt Fixture, Fresh Fixture" and Chapter 6 (Result Verification / Teardown strategies).
- See also: `xunit-test-patterns/07` for how a poorly chosen fixture strategy manifests as Fragile/Erratic Tests, and `xunit-test-patterns/09` for fixture *data* management patterns.
