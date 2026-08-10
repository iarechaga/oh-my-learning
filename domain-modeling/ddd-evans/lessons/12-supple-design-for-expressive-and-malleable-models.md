---
id: ddd-evans/12
subject: ddd-evans
title: Supple design for expressive and malleable models
slug: supple-design-for-expressive-and-malleable-models
status: drafted
mastery:
seniority: senior
source: Domain-Driven Design (Eric Evans), Part III, Chapters 9-10
prerequisites: [ddd-evans/02, ddd-evans/04, ddd-evans/05, ddd-evans/06]
created: 2026-08-10
updated: 2026-08-10
---

# Supple design for expressive and malleable models

## TL;DR
Supple design is the pursuit of a model whose code is both easy to understand deeply and easy to change safely — achieved through a cluster of mutually reinforcing techniques: intention-revealing interfaces, side-effect-free functions, assertions that surface invariants, conceptual contours that match the domain's real joints, standalone classes, and closure of operations.

## The idea
A model can be *technically correct* — every rule enforced, every test passing — while still being brittle and opaque: hard to extend without breaking something, hard to understand without reading every line of implementation, hard to safely refactor because nobody can tell which changes are safe. Evans calls the opposite quality "supple design": a model that invites change rather than resisting it, because its structure closely mirrors the domain's actual conceptual joints, and its interfaces tell you honestly what they do without forcing you to read the implementation to find out.

This is where the building-block patterns from earlier lessons stop being independent techniques and start reinforcing each other into a coherent design philosophy: value objects (`ddd-evans/05`) and side-effect-free functions make behavior safe to compose and reason about; well-named methods and classes (following `ddd-evans/01`'s ubiquitous language) make intent legible without implementation-reading; and a handful of specific techniques — described below — push a model from merely "correct" to genuinely supple.

## How it works

### Intention-revealing interfaces
A method's name and signature should tell the caller everything they need to use it correctly, without reading its body.

**Before:**
```
def process(order, flag):
    ...
```
What does `process` do? What does `flag` control? A caller has to read the implementation (or, worse, guess) to use this safely.

**After:**
```
def apply_discount_if_eligible(order: Order, discount_code: DiscountCode) -> Order:
    ...
```
The name states the operation and its condition; the parameter type states exactly what's needed; the return type states what comes back. This directly extends `ddd-evans/01`'s naming discipline into method signatures specifically — a signature is a contract, and a supple one is a contract you can trust without inspecting its implementation.

### Side-effect-free functions, isolated from commands
Building on `ddd-evans/05`: aggressively separate operations that compute and return a result (functions) from operations that change state (commands). A function like `order.total()` should be perfectly safe to call any number of times, from anywhere, without consequence — which means it can be freely used in logging, in other calculations, in tests, without ever worrying about triggering an unwanted side effect. Push as much domain logic as possible into this side-effect-free category; reserve commands for the smallest possible surface of actual state-changing operations, and make those commands simple and few in number, so the "dangerous" part of the API is small and easy to audit.

### Assertions that state invariants explicitly
Rather than leaving an invariant implicit (hoping every caller happens to respect it), state it as an explicit, checked assertion at the boundary where it must hold:
```
class BankAccount:
    def withdraw(self, amount: Money) -> None:
        assert amount.is_positive(), "withdrawal amount must be positive"
        if amount > self._balance:
            raise InsufficientFundsError()
        self._balance = self._balance.subtract(amount)
        assert not self._balance.is_negative(), "balance invariant violated"
```
The book's point isn't just "add asserts for safety" — it's that assertions *document* the invariant in a form that's checked, not just described in a comment that can silently drift out of sync (echoing `clean-code`-style reasoning about comments rotting while code doesn't). A reader scanning `withdraw()` learns the account's core invariant (balance never negative) directly from the code, with no separate documentation to go stale.

### Conceptual contours: let the model's own natural joints drive class boundaries
Some ways of splitting a model into classes feel arbitrary — technically valid, but not aligned with where the domain actually "wants" to be divided. "Conceptual contours" means finding the divisions the domain itself suggests. A shipping domain might be tempted to bundle "package dimensions" and "package handling instructions" into one `PackageDetails` value object because they're both "about the package" — but if handling instructions change independently and far more often than dimensions, and different parts of the system need one without the other, the domain is signaling a natural seam between them that the current design is ignoring. Splitting along that seam (`PackageDimensions` and `HandlingInstructions` as separate value objects) produces a model that's easier to extend because each piece changes for its own reason — directly echoing the high-cohesion principle from `ddd-evans/07`, applied at the class level instead of the module level.

### Standalone classes
Minimize a class's dependencies on other classes wherever the domain allows it — a class that can be understood, tested, and modified without pulling in a dozen other classes' definitions is far cheaper to work with than one entangled in a dense dependency web. This doesn't mean avoiding all dependencies (that's impossible and undesirable), but actively noticing and reducing *unnecessary* ones, the same discipline `ddd-evans/11` applies specifically to associations, generalized to dependencies of any kind (including on services, other value objects, or shared state).

### Closure of operations
Where the domain allows it, design an operation so its return type matches its argument types — closed under the operation, the way addition on integers returns an integer. `Money.add(Money) -> Money` is closed; you can chain `.add().add().multiply()` freely, compose operations fluently, and never leave the type. This is a small but powerful suppleness technique: it makes a whole class of operations trivially composable without any special-casing, exactly because the type never "escapes" into something incompatible with the next operation in a chain.

### Worked example: a supple discount-calculation redesign
An early, un-supple design had `Order.applyDiscount(code: str, percentOff: float, flag: bool)` — an intention-obscuring signature (what's `flag` for? what if `percentOff` is wrong for this discount type?), doing both validation and mutation together, with no reusable, side-effect-free way to preview a discount before committing to it. A supple redesign separates concerns along the lines above:
```
class Discount:                                   # value object, closed operations
    def apply_to(self, amount: Money) -> Money: ...

class DiscountCatalog:
    def eligible_discount_for(self, order: Order, customer: Customer) -> Optional[Discount]: ...  # side-effect-free function

class Order:
    def preview_total_with_discount(self, discount: Discount) -> Money: ...   # side-effect-free
    def apply_discount(self, discount: Discount) -> None: ...                 # the one actual command
```
Now a caller can *preview* a discount's effect with zero risk (pure function), the eligibility logic is isolated and independently testable, and the one genuinely state-changing operation (`apply_discount`) is small, clearly named, and easy to audit — this is what "supple" concretely buys you: safety to explore, compose, and extend the model without fear.

## Pros
- Makes a model genuinely safer to extend and refactor over a long project lifetime, not just correct at a single point in time.
- Reduces the "must read the implementation to trust this" tax across the whole codebase, compounding the benefits of good naming (`ddd-evans/01`) into method and class design broadly.
- Side-effect-free functions and closed operations make ad hoc composition and exploratory use (during debugging, in tests, in new features) safe by construction.

## Cons
- These techniques take real design skill and iteration to apply well — supple design is rarely achieved on a first attempt, and the book is explicit that it's discovered through refactoring toward deeper insight (`ddd-evans/13`), not designed upfront in full.
- Aggressively minimizing side effects and dependencies can, if taken too literally, produce excessive indirection or an unnatural proliferation of tiny pure-function wrapper classes.
- Conceptual contours require genuine domain insight to find — without deep enough knowledge crunching (`ddd-evans/01`), a team may misidentify which seams are "natural" and split along the wrong lines.

## Alternatives
- **"Good enough," correctness-only design** — ship code that passes tests and satisfies current requirements without investing in these suppleness techniques; faster in the short term, but accumulates exactly the resistance-to-change costs this lesson is meant to avoid, especially as the codebase and team grow.
- **Heavy upfront architecture / big design up front** — try to anticipate future flexibility needs and design elaborate extension points in advance; the book is skeptical of this too, preferring suppleness discovered iteratively through real refactoring pressure over speculative generality designed before it's needed.

## When to use it
Invest in supple design deliberately for the parts of the model that are central to the business and expected to change often over the system's life — see `ddd-evans/13` for how to identify which parts of the model deserve this level of investment versus which don't.

## When NOT to use it
Don't over-invest suppleness effort in peripheral, rarely-touched, or generic parts of the system — the cost/benefit only pays off where the model actually experiences ongoing change pressure; applying it uniformly everywhere is itself a form of speculative generality the book would caution against.

## Key takeaways / mental model
Supple design asks of every interface: "if I only ever read this signature and never its body, would I use it correctly?" and of every class: "does this boundary match where the domain itself naturally splits, or is it an arbitrary technical convenience?" Both questions, asked repeatedly and honestly, are what turn a merely-correct model into one that's actually pleasant and safe to keep changing.

## Self-check questions
1. Rewrite a method signature from your own code that currently requires reading the implementation to use safely, applying the intention-revealing-interface technique. What changed?
2. Why does "closure of operations" (`Money.add(Money) -> Money`) make chaining and composition safer than an operation that returns a different, incompatible type?
3. In the discount-redesign example, what specific new capability (safety, testability) did splitting `applyDiscount` into `preview_total_with_discount` and `apply_discount` unlock that the single-method version didn't have?
4. Explain, in your own words, what a "conceptual contour" is, and give an example (real or hypothetical) of a class that's currently split along the *wrong* seam.

## References
- Domain-Driven Design: Tackling Complexity in the Heart of Software (Eric Evans), Chapter 9: "Making Implicit Concepts Explicit" and Chapter 10: "Supple Design".
