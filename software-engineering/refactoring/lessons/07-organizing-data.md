---
id: refactoring/07
subject: refactoring
title: Organizing Data
slug: organizing-data
status: drafted
mastery:
seniority: mid
source: Refactoring, 2nd ed. (Martin Fowler), Chapter 9
prerequisites: [refactoring/06, code-complete/07]
created: 2026-08-10
updated: 2026-08-10
---

# Organizing Data

## TL;DR
Encapsulate Variable protects a piece of data behind accessor methods so its representation can change later without touching every caller. Replace Primitive with Object gives a bare, constraint-free value (a string, a number) its own type that can enforce domain rules and carry its own behavior. Change Value to Reference (and its inverse) decides whether two representations of "the same conceptual thing" should actually share identity or remain independent copies.

## The idea
Data organization refactorings target a different axis of design quality than the function/class refactorings in `refactoring/05`-`06`: rather than "where does this behavior/data belong," these techniques ask "does this data's *current representation* correctly capture the constraints and identity relationships the domain actually has?" A bare `str` or `float` used where a richer, constrained representation belongs is a common, quiet source of bugs and duplicated validation logic (echoing `code-complete/07`'s "most restrictive representation" guidance and `refactoring/04`'s Primitive Obsession smell) that these refactorings directly address.

## How it works

### Encapsulate Variable — protect access before changing representation
Before changing how a piece of data is represented or computed, first ensure all access to it goes through a method rather than direct field access — this creates a stable seam that insulates callers from whatever representation change comes next (directly echoing `clean-code/06`'s object-vs-data-structure encapsulation argument, applied here as a *preparatory* step for further refactoring).

**Worked example.**
```
# Before — direct field access, no seam for a future representation change
order.discount_pct = 0.1
apply = order.discount_pct * order.total

# After — encapsulated; callers use methods, not a raw field
order.set_discount(0.1)
apply = order.discount_amount()   # internal representation (percent vs. fixed amount) can now change freely
```
Once encapsulated, `Order` is free to change how it internally stores or computes a discount (percentage vs. a fixed monetary amount, or a more sophisticated discount-rule object per Replace Primitive with Object below) without any caller needing to change at all — the encapsulation step is what makes the *next* refactoring safe and localized.

### Replace Primitive with Object — give bare values domain-aware behavior
A bare primitive (a `str` for a phone number, a `float` for money) carries no domain constraints or behavior of its own — validation, formatting, and any domain-specific operations end up either duplicated at every use site or simply never enforced consistently. Replacing it with a small, dedicated value type centralizes both the constraint and any related behavior in exactly one place.

**Worked example.**
```
# Before — a bare float, no enforcement, formatting duplicated everywhere it's displayed
price = 19.999999999   # a float rounding artifact nobody catches until display time

# After — a Money type owns precision, currency, and formatting
class Money:
    def __init__(self, cents: int, currency: str):
        self.cents, self.currency = cents, currency
    def formatted(self):
        return f"{self.cents / 100:.2f} {self.currency}"
    def __add__(self, other):
        assert self.currency == other.currency
        return Money(self.cents + other.cents, self.currency)

price = Money(1999, "USD")   # no floating-point rounding artifacts; currency mismatches caught by __add__
```
This is directly `code-complete/07`'s "most restrictive representation" principle and `pragmatic-programmer/09`'s Design-by-Contract spirit, expressed as a specific, named, mechanical refactoring: the bare `float`'s complete absence of domain constraints (no currency, no fixed precision, silent floating-point drift) is replaced by a type that makes an entire class of bugs (currency mismatches, precision drift) structurally impossible rather than merely "hopefully checked" at every use site.

### Change Value to Reference, and its inverse — deciding on shared identity
Two objects representing "the same conceptual thing" (two `Order` objects both referring to "Customer #42") can either each hold their own independent *copy* of that customer's data (value semantics — if one order's view of the customer's address is updated, the other doesn't automatically see the change) or both hold a *reference* to one shared `Customer` object (reference semantics — an update through either order is immediately visible to both, since there's genuinely only one `Customer #42` in memory).

**Worked example of the problem this decides.** If customer address changes are supposed to apply consistently everywhere that customer is referenced (a single source of truth, echoing `pragmatic-programmer/03`'s DRY), value semantics (independent copies) silently produces inconsistent, stale data across different orders' views of the same customer — a bug that's easy to introduce accidentally if the data started as a simple copied value and the "these should always be the same object" requirement wasn't deliberately enforced. Change Value to Reference fixes this by ensuring all orders referencing "Customer #42" hold a reference to the exact same, single `Customer` instance (often via a registry or repository ensuring exactly one instance per ID), so an update anywhere is visible everywhere.

The **inverse** (Change Reference to Value) is appropriate when independent copies are actually what's wanted — e.g., a `Money` amount frozen at the time of an order shouldn't retroactively change if some "current price" reference object it was created from later changes; freezing it as an independent value, not a live reference, is the correct choice there specifically because independence, not shared mutability, is the actual domain requirement.

### The underlying design question these three techniques all serve
Each of these refactorings is really answering one of two questions about a piece of data: "should access to this be protected behind a seam, so its representation can evolve?" (Encapsulate Variable) and "does two things sharing a conceptual identity mean they should share literal object identity (reference) or just have equal, independent values (value)?" (Change Value/Reference to the other) — plus a third, related question, "does this specific value carry enough domain meaning and constraint that it deserves its own type?" (Replace Primitive with Object).

## Pros
- Encapsulate Variable creates a stable, low-risk seam that makes subsequent, more substantial representation changes safe and localized.
- Replace Primitive with Object centralizes domain constraints and behavior that would otherwise be duplicated or inconsistently enforced across every use site.
- Correctly choosing value versus reference semantics prevents an entire class of stale-data or unintended-shared-mutation bugs, depending on which direction the mistake was made in.

## Cons
- Wrapping every primitive in its own dedicated type adds real definitional overhead, disproportionate for values with no genuine domain constraints or behavior beyond their raw representation.
- Reference semantics introduces shared-mutable-state risk (echoing `pragmatic-programmer/11`) if not paired with careful thinking about concurrent access or unexpected side effects propagating further than intended.
- Getting value-versus-reference semantics wrong in either direction can be a subtle, hard-to-diagnose bug class, and correcting it later (via Change Value to Reference or its inverse) is a real, sometimes substantial refactoring effort once code has been written assuming the wrong semantics.

## Alternatives
- **Sticking with primitives and validating at every boundary** (echoing `code-complete/06`'s defensive-programming discussion) — a legitimate lighter-weight alternative when a value genuinely doesn't recur often enough to justify a dedicated type (echoing the Rule of Three).
- **Immutable value objects universally, avoiding reference semantics wherever possible** — a stronger, more opinionated stance (common in functional-programming-influenced codebases) that sidesteps the value-vs-reference decision by defaulting to immutable values everywhere, accepting the cost of explicit propagation when a genuine update needs to reach multiple holders.
- **A shared cache/repository ensuring single-instance-per-ID semantics** — the common mechanism underlying Change Value to Reference in practice, worth recognizing as infrastructure you may already have (e.g., an ORM's identity map) rather than something to hand-build from scratch every time.

## When to use it
Use Encapsulate Variable before any planned change to a variable's representation, as a low-risk first step. Use Replace Primitive with Object once a bare value's domain constraints or duplicated validation logic become a recurring, evidenced problem (Rule of Three). Choose reference semantics when updates to a shared concept must be visible everywhere it's referenced; choose value semantics when independent copies genuinely reflect the domain's actual requirement.

## When NOT to use it
Don't wrap every primitive in a dedicated type reflexively — reserve it for values with genuine domain constraints, recurring validation, or behavior worth centralizing. Don't introduce reference semantics for data that's genuinely meant to be an independent, frozen snapshot (like a historical price) — that's exactly the case Change Reference to Value protects.

## Key takeaways / mental model
For any piece of data, ask three questions: "is access to this protected behind a seam yet?", "does this bare value actually carry domain meaning or constraints that deserve their own type?", and "if I have two things referring to 'the same' conceptual entity, should an update to one be visible through the other, or should they be independent?" Each question points to one of this lesson's three techniques.

## Self-check questions
1. Walk through Encapsulate Variable on a directly-accessed field from your own code, and explain what future refactoring it would enable safely.
2. Using the `Money` example, explain what bug classes Replace Primitive with Object eliminates structurally, rather than merely making less likely.
3. Describe a real or hypothetical bug caused by the wrong choice between value and reference semantics, and identify which of the two techniques would fix it.
4. Why is Replace Primitive with Object subject to the same Rule-of-Three caution as other generalizing refactorings? Give an example of applying it prematurely.

## References
- Refactoring: Improving the Design of Existing Code, 2nd ed. (Martin Fowler), Chapter 9: "Organizing Data".
