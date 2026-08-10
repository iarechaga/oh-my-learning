---
id: refactoring/06
subject: refactoring
title: Moving Features Between Objects
slug: moving-features
status: drafted
mastery:
seniority: mid
source: Refactoring, 2nd ed. (Martin Fowler), Chapter 8
prerequisites: [refactoring/05, clean-code/10]
created: 2026-08-10
updated: 2026-08-10
---

# Moving Features Between Objects

## TL;DR
Move Function and Move Field relocate behavior or data to the class that actually owns the underlying responsibility — the direct, mechanical fix for Feature Envy and Shotgun Surgery (`refactoring/04`). Extract Class and Inline Class adjust the *granularity* of classes themselves, splitting an overloaded one apart or merging two that no longer earn separate existence.

## The idea
`clean-code/10` and `refactoring/04` both establish *why* misplaced responsibility is a problem (low cohesion, scattered changes); this lesson gives the concrete, mechanical *how* for fixing it once identified. Moving a method or field to a different class is conceptually simple but has real mechanical care points — updating every caller, handling any remaining dependencies on the original location — that make it worth treating as its own disciplined procedure rather than an ad hoc cut-and-paste.

## How it works

### Move Function — relocate behavior to where its data lives
When a method uses another class's data more than its own (Feature Envy, per `clean-code/12`/`refactoring/04`), Move Function relocates it to that other class, updating the original class to either delegate to the new location or remove the method entirely if callers can be updated to call the new location directly.

**Worked example.**
```
# Before — CustomerAccount computes something that's really about Customer's data
class CustomerAccount:
    def __init__(self, customer): self.customer = customer
    def overdue_days(self):
        return (today() - self.customer.last_payment_date).days

# After — moved to Customer, which actually owns last_payment_date
class Customer:
    def overdue_days(self):
        return (today() - self.last_payment_date).days

class CustomerAccount:
    def __init__(self, customer): self.customer = customer
    def overdue_days(self):
        return self.customer.overdue_days()   # delegates, or callers updated to call Customer directly
```
The logic now lives where its data lives — `Customer` no longer needs `CustomerAccount` to exist at all to compute this, and if `Customer`'s date-tracking representation ever changes, only `Customer` needs updating, not `CustomerAccount` as well (directly resolving the change-amplification/leakage concern from `philosophy-of-software-design/01` and `/04`).

### Move Field — the data-side counterpart
The same logic applied to fields rather than methods: if a field on class A is used mostly by methods on class B (or logically belongs to a concept B represents), move the field to B, updating A to reference it via B rather than storing it directly. This often precedes or accompanies Move Function, since a method's Feature Envy frequently correlates with the *data* it envies also being in the wrong place.

### Extract Class — split an overloaded class into two
When a class has accumulated more than one genuine responsibility (echoing `clean-code/10`'s cohesion diagnosis and the "class name needs 'and'" test), Extract Class splits it: create a new class for the responsibility being separated out, move the relevant fields and methods to it (using Move Field/Move Function as the underlying mechanics), and link the original class to the new one (typically by holding a reference to an instance of it).

**Worked example.**
```
# Before — Person handles both personal info and phone-number formatting/validation
class Person:
    def __init__(self, name, office_area_code, office_number):
        self.name = name
        self.office_area_code = office_area_code
        self.office_number = office_number
    def telephone_number(self):
        return f"({self.office_area_code}) {self.office_number}"

# After — phone-number responsibility extracted into its own class
class TelephoneNumber:
    def __init__(self, area_code, number):
        self.area_code, self.number = area_code, number
    def formatted(self):
        return f"({self.area_code}) {self.number}"

class Person:
    def __init__(self, name, office_phone: TelephoneNumber):
        self.name = name
        self.office_phone = office_phone
    def telephone_number(self):
        return self.office_phone.formatted()
```
`TelephoneNumber` can now be reused anywhere a phone number is needed (a customer's phone, a vendor's phone), independent of `Person` — directly recovering `philosophy-of-software-design/05`'s general-purpose-module benefit as a side effect of fixing the original cohesion problem.

### Inline Class — the precise inverse
When a class no longer justifies its separate existence — its responsibilities have shrunk (perhaps through other refactorings) to the point where it's not doing enough to earn its own interface (echoing `philosophy-of-software-design/03`'s depth criterion) — Inline Class merges it back into the class that uses it, removing an unnecessary layer of indirection.

## Pros
- Move Function/Field directly fix Feature Envy and Shotgun Surgery by relocating responsibility to where it structurally belongs, reducing future change amplification.
- Extract Class recovers reusability and cohesion simultaneously, often producing a genuinely useful new abstraction as a side effect of fixing an existing problem.
- All four techniques are incremental and individually verifiable against tests, fitting the small-steps safety discipline from `refactoring/01` and `refactoring/03`.

## Cons
- Moving a widely-called method or field requires updating every caller, which can be a substantial mechanical effort in a large codebase even though each individual update is simple — IDE tooling helps significantly here.
- Extract Class, done prematurely or based on a single occurrence rather than genuine repeated evidence, risks the same premature-abstraction trap `pragmatic-programmer/05`'s Rule-of-Three caution warns against.
- Repeatedly moving features back and forth between two classes (rather than settling on a stable boundary) can indicate the underlying responsibility split itself hasn't been correctly identified yet — a sign to step back and reconsider the domain model, not just keep mechanically moving code.

## Alternatives
- **Leaving Feature Envy in place if it's genuinely minor and isolated** — moving code has a real cost (updating callers, re-testing) that isn't always worth paying for a very small, one-off instance of envy that doesn't yet indicate a broader pattern.
- **Extract Interface instead of Extract Class** — when the goal is decoupling callers from a concrete class's implementation (echoing `design-patterns/01`) rather than splitting genuinely separate responsibilities, extracting an interface addresses a different (though related) need than extracting a whole new class.
- **Domain-driven modeling from the start** (see `domain-modeling/ddd-evans`) — a more upfront, deliberate approach to arriving at correct class boundaries, reducing how often Move Function/Extract Class are needed as corrective, after-the-fact fixes.

## When to use it
Apply Move Function/Field whenever Feature Envy is identified and confirmed genuine (not just superficial). Apply Extract Class when a class's responsibilities have genuinely diverged into two or more separable concerns, ideally once you have concrete evidence (a second real use case, per the Rule of Three) that the split is worth making.

## When NOT to use it
Don't move a method or field for a single, minor, isolated instance of apparent envy that doesn't reflect a genuine, recurring pattern — the update cost may exceed the benefit. Don't extract a class speculatively, before a genuine second responsibility or reuse need has actually appeared, echoing `pragmatic-programmer/05`'s caution against premature abstraction.

## Key takeaways / mental model
When you spot Feature Envy, ask "which class actually owns the data this method needs?" and move the method there. When a class's name needs "and" to describe it (`clean-code/10`), split it with Extract Class — and if two classes end up bouncing features back and forth repeatedly, that's a sign to reconsider the underlying model, not just keep moving code mechanically.

## Self-check questions
1. Using the `overdue_days` example, explain exactly what problem Move Function solved, and connect it to the change-amplification concept from `philosophy-of-software-design/01`.
2. Walk through Extract Class on a class from your own code that has more than one genuine responsibility, and identify what the new class's interface should look like.
3. Why might Inline Class be the right move for a class that Extract Class created a while ago? What would have to be true about how that class's responsibilities evolved?
4. Describe a situation where moving a feature between two classes repeatedly (back and forth) would be a signal to step back and reconsider the domain model, rather than to keep refactoring mechanically.

## References
- Refactoring: Improving the Design of Existing Code, 2nd ed. (Martin Fowler), Chapter 8: "Moving Features".
