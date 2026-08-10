---
id: unit-testing/05
subject: unit-testing
title: Humble Object and Separating Pure Logic
slug: humble-object
status: drafted
mastery:
seniority: mid
source: Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 7
prerequisites: [unit-testing/04]
created: 2026-08-10
updated: 2026-08-10
---

# Humble Object and Separating Pure Logic

## TL;DR
When code is hard to unit test because it's tangled together with an untestable dependency (UI, database, network, filesystem), split it into two pieces: a "humble" thin wrapper that does nothing but talk to the untestable thing, and a rich piece of pure logic that contains all the actual decisions and is trivially testable in isolation. You then test the logic thoroughly with fast unit tests and leave the humble wrapper mostly untested (or covered by a thin integration/smoke test), because it has nothing worth testing on its own.

## The idea
Some dependencies are fundamentally hard to unit test: a UI framework, a real database connection, the system clock, a third-party HTTP API. Code that mixes business decisions with direct use of these dependencies inherits their untestability — you can't test "does this validation logic work" without also standing up a UI or a database, because they're welded together in the same function.

The **Humble Object pattern** (a term Khorikov borrows from Gerard Meszaros's xUnit Test Patterns) solves this by refusing to accept that coupling as necessary. It extracts all the *decision-making* logic into a separate, pure, dependency-free piece of code, leaving behind a deliberately "humble" (i.e., too simple to need much testing) piece that does nothing but pass data to and from the untestable dependency. The humble piece has so little logic in it — often just one or two lines of pass-through — that testing it thoroughly stops being valuable; the interesting logic, now isolated, becomes trivial to test exhaustively.

## How it works

### The general shape of the split
Before:
```
class OrderController:
    def submit(self, request):
        # parses HTTP request, validates business rules, talks to DB, all mixed together
        if request.subtotal < 0:
            return HttpResponse(400, "Invalid subtotal")
        discount = 0.1 if request.customerType == "CORPORATE" else 0.0
        total = request.subtotal * (1 - discount)
        db.execute("INSERT INTO orders (...) VALUES (...)", total)
        return HttpResponse(200, {"total": total})
```
To unit test the discount calculation here, you'd need a real (or heavily mocked) HTTP request object and a real (or mocked) database — none of which have anything to do with the actual thing worth testing: "corporate customers get a 10% discount."

After applying Humble Object:
```
# Pure logic — trivially testable, no dependencies
class OrderCalculator:
    def calculate(self, subtotal, customerType):
        if subtotal < 0:
            raise InvalidSubtotalError()
        discount = 0.1 if customerType == "CORPORATE" else 0.0
        return subtotal * (1 - discount)

# Humble wrapper — thin, does almost nothing itself
class OrderController:
    def submit(self, request):
        try:
            total = OrderCalculator().calculate(request.subtotal, request.customerType)
        except InvalidSubtotalError:
            return HttpResponse(400, "Invalid subtotal")
        db.execute("INSERT INTO orders (...) VALUES (...)", total)
        return HttpResponse(200, {"total": total})
```
Now `OrderCalculator.calculate` is pure: no HTTP, no database, just inputs and outputs. It can be unit tested exhaustively:
```
test "corporate customer receives a 10 percent discount":
    calculator = new OrderCalculator()
    assert calculator.calculate(subtotal: 200, customerType: "CORPORATE") == 180

test "negative subtotal raises an error":
    calculator = new OrderCalculator()
    assertRaises(InvalidSubtotalError):
        calculator.calculate(subtotal: -10, customerType: "RETAIL")
```
`OrderController` is now "humble" — it just wires the calculator to HTTP and the database. There's very little logic left to get wrong, so it doesn't need (and often can't cheaply get) the same exhaustive unit-test treatment; a small number of integration or smoke tests covering the wiring is enough (see `unit-testing/10` and `unit-testing/11` for how to test this remaining layer appropriately).

### Why this is different from "just extract a method"
It's tempting to see this as generic "extract a function" refactoring, but the Humble Object framing adds a specific *intent*: the split boundary is drawn exactly at the line between untestable infrastructure and testable logic, and the goal is explicitly to make one side rich-and-tested and the other side thin-and-mostly-untested. A refactor that extracts a method but leaves business rules split across both pieces doesn't achieve this — you'd still need the untestable dependency to test some of the rules. The test of a good split: can you write a unit test for every business rule using *only* the extracted piece, with zero doubles for infrastructure? If yes, the split succeeded.

### Worked example: testing time-dependent logic
A method that grants a "new customer" discount within 30 days of signup:
```
class DiscountEngine:
    def isEligibleForNewCustomerDiscount(self, customer):
        return (DateTime.now() - customer.signupDate).days <= 30
```
`DateTime.now()` is effectively an untestable dependency (it changes every time you run the test — see `unit-testing/12` for controlling time directly). Applying Humble Object here means separating "what is now" from "given now and a signup date, is this customer eligible":
```
class DiscountEngine:
    def isEligibleForNewCustomerDiscount(self, customer, currentTime):
        return (currentTime - customer.signupDate).days <= 30
```
Now the logic is pure and trivially testable with fixed timestamps:
```
test "customer signed up 10 days ago is eligible":
    engine = new DiscountEngine()
    assert engine.isEligibleForNewCustomerDiscount(
        customer: Customer(signupDate: "2026-08-01"),
        currentTime: "2026-08-11"
    ) == true
```
The humble part — actually calling `DateTime.now()` and passing it in — moves to a thin caller at the application's edge, which is where it belongs and where it's cheap to leave untested (there's almost nothing left in it to get wrong).

## Pros
- Makes previously "untestable" logic (entangled with UI, DB, or the clock) fully unit-testable with zero test doubles for infrastructure.
- Concentrates all business-rule bugs in the one place that's exhaustively tested, and concentrates plumbing bugs in a thin layer that's easy to review by inspection.
- Improves design as a side effect: the split usually produces a cleaner separation of concerns even independent of testing.

## Cons
- Requires an upfront refactor of existing tangled code, which takes real effort and can be risky to do without tests already in place (a chicken-and-egg problem — see `unit-testing/13` for a strategy on legacy code).
- Adds an extra layer/class, which is a small but real increase in structural complexity for very simple features.
- The humble layer, while "not worth exhaustive unit testing," still needs *some* verification (integration or smoke tests) — skipping that entirely leaves a real gap.

## Alternatives
- **Mocking the untestable dependency directly** — instead of extracting pure logic, wrap the DB/UI/clock behind an interface and mock it in the test; works, but per `unit-testing/07`/`unit-testing/08`, over-mocking infrastructure this way often produces brittle, low-value tests compared to a clean logic/plumbing split.
- **In-memory fakes for infrastructure** (e.g., an in-memory database) — lets you keep the tangled structure but swap the real dependency for a fast fake; useful when the coupling to infrastructure can't be cleanly separated from the logic (see `unit-testing/07`'s fakes discussion).
- **Leave it untested and rely on integration/E2E tests** — sometimes pragmatic for genuinely trivial glue code, but doesn't scale once real decision logic accumulates inside the "humble" layer by accident.

## When to use it
Apply Humble Object whenever business logic is currently entangled with a hard-to-test dependency (UI event handlers, controllers, ORM-bound models, code calling `DateTime.now()` or `Random()` directly). It's especially valuable when the logic is complex enough (many branches, edge cases) that you want exhaustive example coverage.

## When NOT to use it
Don't apply it to genuinely trivial glue code with no real decisions in it — splitting a two-line pass-through into two even-thinner pieces adds structure without adding testability. Also don't use it as an excuse to leave the humble layer completely unverified forever; it still needs some form of coverage appropriate to its role (see `unit-testing/10`, `unit-testing/11`).

## Key takeaways / mental model
When logic is stuck to something untestable, don't try to test the glue — cut it apart. Push every decision into a pure, dependency-free piece you can test exhaustively; leave behind a thin, boring wrapper with so little logic that it barely needs tests of its own.

## Self-check questions
1. Take a method you've written recently that mixes a database call with a business rule. Sketch how you'd split it using Humble Object — what goes in the pure piece, what stays in the humble wrapper?
2. Why does testing `DiscountEngine.isEligibleForNewCustomerDiscount(customer, currentTime)` (with `currentTime` passed in) avoid the untestability problem that `DiscountEngine.isEligibleForNewCustomerDiscount(customer)` (calling `DateTime.now()` internally) has? What specifically changed about the function's nature?
3. A reviewer objects: "this refactor just adds an extra class for no reason." Using this lesson's litmus test ("can every business rule be unit tested using only the extracted piece, with zero infrastructure doubles?"), how would you defend the split — or concede the point if the logic really is trivial?

## References
- Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 7: "Refactoring Toward Valuable Unit Tests."
