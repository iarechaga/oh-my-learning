---
id: unit-testing/02
subject: unit-testing
title: AAA Structure and Test Naming
slug: aaa-and-naming
status: drafted
mastery:
seniority: junior
source: Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 3
prerequisites: [unit-testing/01]
created: 2026-08-10
updated: 2026-08-10
---

# AAA Structure and Test Naming

## TL;DR
Structure every test as Arrange-Act-Assert (set up the world, perform the one action under test, check the outcome), and name it after the *behavior* being verified in plain language, not after the method being called. Both practices exist for the same reason: a test's job is to communicate intent to a human reader as much as to a test runner.

## The idea
A test is read far more often than it is written — by the original author debugging a failure months later, by a teammate trying to understand what a class does, by whoever is diagnosing why a refactor broke something. If a test's structure and name don't communicate what is being tested and why, all that reading time is wasted re-deriving intent from raw code. AAA (Arrange-Act-Assert, sometimes called Given-When-Then) and disciplined naming are the two cheapest, highest-leverage habits for making tests self-explanatory — they cost nothing extra to apply and pay back every time someone reads the test later.

## How it works

### The three sections
Every well-formed unit test has (at most) three parts, ideally visually separated by blank lines or comments:

```
test "adding an item increases the cart total by its price":
    # Arrange — build the world the test needs
    cart = new ShoppingCart()
    item = new Item(name: "Book", price: 15.00)

    # Act — the single action under test
    cart.add(item)

    # Assert — check the observable outcome
    assert cart.total == 15.00
```

- **Arrange** builds every precondition the test needs: constructing the object under test, its collaborators, and any input data.
- **Act** performs exactly *one* action — usually one method call — on the object under test. If Act needs more than one line, that's often a sign the API under test is awkward (see the "more than one Act line" pitfall below).
- **Assert** verifies the resulting state or outcome. A test can have multiple assertions, but they should all be checking facets of the *same* outcome, not unrelated behaviors bolted together.

### Why exactly one Act line matters
Consider a test that both adds an item to a cart and applies a discount, then asserts on the final total:
```
test "cart total is correct":
    cart = new ShoppingCart()
    cart.add(new Item(price: 100))
    cart.applyDiscount(0.1)          # second action!
    assert cart.total == 90
```
This mixes two behaviors — "adding updates the total" and "discounting reduces the total" — into one test. If it fails, you don't immediately know which behavior broke without stepping through it. Split it into two tests, each with one Act line:
```
test "adding an item sets the total to its price":
    cart = new ShoppingCart()
    cart.add(new Item(price: 100))
    assert cart.total == 100

test "applying a 10 percent discount reduces the total by 10 percent":
    cart = new ShoppingCart()
    cart.add(new Item(price: 100))          # arrange, not act — sets up precondition
    cart.applyDiscount(0.1)                 # the one action under test
    assert cart.total == 90
```
Notice the second test still calls `add` — that's fine, because relative to *this* test's purpose, `add` is part of Arrange (building the precondition "a cart with $100 in it"), and `applyDiscount` is the one Act being verified. The rule isn't "call exactly one method" — it's "verify exactly one behavior."

### Naming: describe the behavior, not the method
A common but weak convention names tests after the method under test plus the scenario, e.g. `applyDiscount_Test1`, `test_add_item`. These names say *what code runs* but not *what should happen* — a reader has to open the test body to learn anything. Khorikov recommends plain-language names describing the scenario and the expected outcome, written as if explaining the behavior to a non-programmer:

Weak: `testApplyDiscount()`
Better: `applying_discount_reduces_total_by_percentage()`
Best (readable as a sentence, framework-permitting): `"a corporate customer with a $200 order receives a 10 percent discount"`

A useful template: **"[unit of behavior] does [expected result] when [scenario]"** — e.g., "the cart total reflects a 10 percent discount when the customer is corporate." This format is deliberately implementation-agnostic: it says nothing about *which method* computes the discount, so the test name — and the test itself, if written to match — survives a refactor that changes the implementation without changing the behavior. This is the naming-level expression of the behavioral-coupling idea developed fully in `unit-testing/04`.

### Worked example: a bad test rewritten
Bad version:
```
test "test1":
    v = new PasswordValidator()
    r1 = v.validate("ab")
    assertFalse(r1.isValid)
    r2 = v.validate("abcdefgh")
    assertTrue(r2.isValid)
    v2 = new PasswordValidator(minLength: 4)
    r3 = v2.validate("abc")
    assertFalse(r3.isValid)
```
This packs three unrelated scenarios (short password rejected, valid password accepted, custom minimum length) into one unnamed test with no Arrange/Act/Assert separation. A failure gives you a line number and nothing else. Rewritten:
```
test "a password shorter than the minimum length is rejected":
    validator = new PasswordValidator(minLength: 8)
    result = validator.validate("abc")
    assert result.isValid == false

test "a password meeting the minimum length is accepted":
    validator = new PasswordValidator(minLength: 8)
    result = validator.validate("abcdefgh")
    assert result.isValid == true

test "a custom minimum length is enforced":
    validator = new PasswordValidator(minLength: 4)
    result = validator.validate("abc")
    assert result.isValid == false
```
Each test now fails independently with a name that tells you exactly which behavior broke, without opening the file.

## Pros
- A failing test's name alone often tells you what broke, before you read any code — faster debugging.
- AAA's visual separation makes it immediately clear what's setup vs. what's actually being verified, reducing the chance of accidentally testing the wrong thing.
- Behavior-based names decouple the test from the implementation, so tests survive refactors that don't change behavior (feeds into `unit-testing/04`).

## Cons
- Disciplined naming and structure take a little more thought upfront than dashing off `test1`, `test2`.
- Overly long behavior-description names can become unwieldy in frameworks that require them as valid identifiers (mitigated by frameworks supporting string-based test names).
- AAA can feel like overkill for trivial one-line tests, though the discipline still pays off as soon as tests grow past the trivial case.

## Alternatives
- **Given-When-Then (BDD style)** — semantically identical to AAA (Given = Arrange, When = Act, Then = Assert), typically used with frameworks like Cucumber/SpecFlow that support natural-language scenario files; prefer it when tests need to be readable by non-developers (e.g. product owners).
- **Four-phase test (adds explicit Teardown)** — AAA plus a fourth explicit cleanup phase; relevant mainly for tests with real external resources (files, database connections) that must be released deterministically, which most unit tests, by definition, don't have.
- **Method-name-based naming** (`testApplyDiscount1`) — faster to write, but sacrifices the self-documenting property; acceptable only for extremely simple, obvious tests where the loss of clarity is negligible.

## When to use it
Use AAA and behavior-based naming for every test, by default — the cost is negligible and the benefit compounds every time someone (including future you) reads a failing test.

## When NOT to use it
There's rarely a reason to skip AAA structure. The one legitimate flexibility is naming format: if your team or framework has a strong existing convention (e.g., a BDD tool expecting Given/When/Then blocks), follow that convention rather than forcing prose-sentence method names — the underlying principle (describe behavior, separate phases) matters more than the exact syntax.

## Key takeaways / mental model
Every test tells a three-beat story: here's the world (Arrange), here's what happens (Act — one thing), here's what should be true afterward (Assert). Its name should let a teammate understand that story without reading the body. If you can't summarize a test in one behavior-focused sentence, it's probably testing more than one thing and should be split.

## Self-check questions
1. Rewrite this test name to follow the behavior-based convention: `test_getTotal_2()`. You don't know the test body — what information would you need to name it well, and why does that matter?
2. A test has two Act-phase calls that both mutate the object under test before a single assert. What's the risk of leaving it that way, and how would you fix it?
3. Why does a behavior-based test name ("applying a discount reduces the total") tend to survive refactors better than a method-based name ("testApplyDiscount")? Connect this to what you'd expect to happen if the discount calculation moved to a different method.

## References
- Unit Testing: Principles, Practices, and Patterns (Vladimir Khorikov), Chapter 3: "The Anatomy of a Unit Test."
