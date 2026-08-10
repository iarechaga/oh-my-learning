---
id: ddd-evans/05
subject: ddd-evans
title: Value objects and side-effect-free modeling
slug: value-objects-and-side-effect-free-modeling
status: drafted
mastery:
seniority: mid
source: Domain-Driven Design (Eric Evans), Part II, Chapters 5-6
prerequisites: [ddd-evans/02, ddd-evans/04]
created: 2026-08-10
updated: 2026-08-10
---

# Value objects and side-effect-free modeling

## TL;DR
A value object is a domain object defined entirely by its attributes, with no conceptual identity — two value objects with the same attributes are interchangeable and equal. Making them immutable and giving them side-effect-free behavior eliminates whole categories of bugs that entities (`ddd-evans/04`) are structurally prone to.

## The idea
Not everything in a domain needs to be tracked as a specific, continuous thing. A `Money` amount of $50, an `Address`, a `DateRange`, a `Color` — nobody in the business cares "which specific $50 is this," only "is it $50." These are values: interchangeable, defined completely by what they hold, with no lifecycle or history of their own.

Treating something as a value object rather than an entity is a deliberate simplification with real payoff: values can be immutable (once created, never changed — any "modification" produces a new value instead), which means they can be freely shared, copied, cached, and passed around without fear that some other part of the system will mutate them out from under you. This is where "side-effect-free modeling" comes in: methods on a value object should be pure functions that return a new value rather than mutating `self`, which makes the object trivially safe to reason about and share, in sharp contrast to the careful, defensive handling entities require because of their mutable, identity-bearing state.

## How it works

### Defining equality by attributes, not identity
```
class Money:
    def __init__(self, amount: Decimal, currency: str):
        self._amount = amount
        self._currency = currency

    def __eq__(self, other):
        return (isinstance(other, Money)
                and self._amount == other._amount
                and self._currency == other._currency)

    def __hash__(self):
        return hash((self._amount, self._currency))
```
Two `Money(50, "USD")` instances, constructed separately, are equal — there's no `id` field to distinguish them, because the business genuinely doesn't distinguish them. This is the mirror image of `ddd-evans/04`'s entity equality, and the two should never be implemented the same way for the same class.

### Immutability and side-effect-free operations
```
class Money:
    ...
    def add(self, other: "Money") -> "Money":
        if self._currency != other._currency:
            raise CurrencyMismatchError()
        return Money(self._amount + other._amount, self._currency)

    def multiply(self, factor: Decimal) -> "Money":
        return Money(self._amount * factor, self._currency)
```
`add` and `multiply` never touch `self` — they return brand-new `Money` instances. This means a `Money` value handed to unrelated code (a logging function, a different module, a background job) can never be silently altered by that code, because there's no mutation method to call in the first place. Contrast this with a mutable `set_amount()` method: any code holding a reference to the same object could change it underneath every other holder of that reference, a classic source of "why did this total suddenly change" bugs that are painful to trace in a large system.

### Worked example: an `Address` value object with validation baked in
```
class Address:
    def __init__(self, street: str, city: str, postal_code: str, country: str):
        if not postal_code_matches_country(postal_code, country):
            raise InvalidAddressError(f"{postal_code} is not valid for {country}")
        self.street = street
        self.city = city
        self.postal_code = postal_code
        self.country = country

    def with_street(self, new_street: str) -> "Address":
        return Address(new_street, self.city, self.postal_code, self.country)
```
Validation happens once, in the constructor — it's structurally impossible to have an `Address` instance that violates the postal-code-matches-country rule, because there's no way to construct one that skips validation and no setter that could later put it into an invalid state. `with_street` follows the same side-effect-free pattern as `Money.add`: it returns a new, validated `Address` rather than mutating the existing one. This is a much stronger guarantee than validating in a separate "is this address valid" function called at various points — that pattern relies on every caller remembering to validate, whereas baking validation into the constructor makes invalid instances simply unrepresentable.

### Value objects can be composite and can contain behavior, not just data
A `DateRange` value object isn't just a start and end date — it can carry genuine domain behavior:
```
class DateRange:
    def __init__(self, start: date, end: date):
        if start > end:
            raise InvalidDateRangeError()
        self.start = start
        self.end = end

    def overlaps(self, other: "DateRange") -> bool:
        return self.start <= other.end and other.start <= self.end

    def duration_days(self) -> int:
        return (self.end - self.start).days
```
`overlaps` is a pure query with no side effects — this is exactly the "side-effect-free function" style the book advocates for any operation that doesn't need to change state: prefer a `Function` (returns a result, no side effect) over a `Command` (changes state) wherever the domain allows it, because functions are trivially composable and testable, and their results can be cached or reused freely since calling them twice can never produce a different outcome from any hidden state change. This same principle scales up into `ddd-evans/12` (supple design), where minimizing side effects across the whole model — not just within value objects — is treated as a first-class design goal.

### Value objects as attributes of entities
An entity like `Order` (`ddd-evans/04`) typically *contains* several value objects: a `ShippingAddress`, a `Total` (a `Money`), a `Discount`. The entity has identity and a lifecycle; its value-object attributes don't — replacing `order.shippingAddress` with a new `Address` value entirely is normal and doesn't threaten the order's own identity, because the address was never the thing being tracked. This composition — entities as the identity-bearing skeleton, value objects as the rich, safe-to-share flesh — is the default DDD building-block pattern and shows up constantly inside aggregates (`ddd-evans/08`).

## Pros
- Immutability eliminates an entire category of aliasing bugs — no code can mutate a value object shared elsewhere without your knowledge.
- Equality by value makes value objects trivially safe to use as dictionary keys, cache keys, and in sets — behavior identical every time for the "same" logical value.
- Baking validation into the constructor makes invalid states genuinely unrepresentable, rather than merely "checked at some point."
- Side-effect-free operations are easy to test (pure functions, no setup/teardown of state) and easy to reason about in concurrent code, since there's no shared mutable state to guard.

## Cons
- Every "modification" allocates a new object, which can matter for performance in extremely hot paths (though this is rarely the actual bottleneck in a typical line-of-business system, and premature optimization here usually isn't worth the modeling cost).
- Developers coming from a mutable-object-by-default mindset (especially in languages/frameworks where ORMs assume mutable entities everywhere) have to unlearn the instinct to add a setter to everything.
- Deciding the right granularity for a value object (should `street`, `city`, `postal_code` be one `Address` value or three loose fields on `Order`?) takes judgment, and getting it too fine-grained adds ceremony without payoff.

## Alternatives
- **Entities** (`ddd-evans/04`) — the correct choice when the business genuinely needs to distinguish two instances with identical current attributes.
- **Mutable data classes / plain structs** — simpler to write, common default in many codebases, but reintroduces aliasing risk and scattered validation; acceptable for short-lived, purely internal data that never crosses a boundary where sharing/aliasing could matter.
- **Primitive obsession** (an anti-pattern, not a real alternative) — using raw strings, decimals, and tuples instead of a `Money` or `Address` value object; faster to write initially but loses the validation-at-construction guarantee and scatters formatting/comparison/arithmetic logic across the codebase instead of centralizing it in one type.

## When to use it
Use a value object for anything defined completely by its attributes with no need to track a specific instance over time: money, addresses, date ranges, measurements, names (in many domains), coordinates, colors, identifiers themselves (an `OrderId` wrapping a raw UUID is itself usually a value object).

## When NOT to use it
Don't reach for a value object when the domain genuinely needs to track one specific instance through a changing history — that's what entities (`ddd-evans/04`) are for. Also avoid over-modeling: wrapping every single primitive in a bespoke value type in a domain with no real validation or behavior to attach adds ceremony without benefit; apply judgment about where the domain actually has rules worth protecting.

## Key takeaways / mental model
If replacing an instance entirely with another instance that has the same attribute values would be completely unnoticed and inconsequential to the business, it's a value object — make it immutable, define equality by attributes, and push validation into the constructor so invalid values can't exist.

## Self-check questions
1. Why does `Money.add` return a new `Money` instead of mutating `self`? What bug does that prevent that a mutating version wouldn't?
2. Explain why baking validation into an `Address` constructor is a stronger guarantee than a separate `validate_address()` function called by convention at various points.
3. Give an example of primitive obsession from a codebase you've seen (a raw string or number standing in for a concept with real rules), and describe what value object would fix it.
4. An entity often *contains* value objects as attributes. Walk through what changes about `Order`'s identity, if anything, when you replace its `shippingAddress` attribute with a new `Address` value.

## References
- Domain-Driven Design: Tackling Complexity in the Heart of Software (Eric Evans), Chapter 5: "A Model Expressed in Software" (Value Objects section) and Chapter 6: "The Life Cycle of a Domain Object" (Side-Effect-Free Functions).
