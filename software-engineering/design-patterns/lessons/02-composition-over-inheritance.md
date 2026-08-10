---
id: design-patterns/02
subject: design-patterns
title: Composition Over Inheritance
slug: composition-over-inheritance
status: drafted
mastery:
seniority: mid
source: Design Patterns (Gamma, Helm, Johnson, Vlissides), Chapter 1
prerequisites: [design-patterns/01]
created: 2026-08-10
updated: 2026-08-10
---

# Composition Over Inheritance

## TL;DR
Inheritance fixes a relationship at compile time and exposes a subclass to its parent's implementation details (breaking encapsulation); composition builds behavior by holding references to other objects and delegating to them, which can be reconfigured at runtime and doesn't require exposing internals. Prefer composition by default; reach for inheritance specifically when you need to reuse an *interface*, not to reuse *implementation*.

## The idea
Inheritance looks, at first glance, like the natural tool for reuse — "this new class is basically like that one, plus a bit more" — but the book's second foundational principle (after `design-patterns/01`'s "program to an interface") is a specific, hard-won caution against reaching for it too readily: inheritance creates one of the tightest possible couplings between two classes, because a subclass's correctness can depend on its parent's *implementation*, not just its documented interface — and that implementation is free to change in ways the subclass author never anticipated, silently breaking the subclass.

**Composition** — where a class holds a reference to another object and delegates work to it, rather than inheriting from it — achieves similar reuse of *behavior* without this coupling: the composed object is used strictly through its public interface (echoing `design-patterns/01`), and, critically, which concrete object is composed can be decided and changed at runtime, not frozen at compile time the way a class hierarchy is.

## How it works

### The fragile base class problem
When class `B` inherits from class `A`, `B`'s behavior isn't just "whatever `A`'s interface promises" — it's "whatever `A`'s *actual current implementation* happens to do," including incidental details `A`'s author never intended to promise as a stable contract. If `A`'s author later changes an internal implementation detail (even one that doesn't violate `A`'s own documented interface), `B` can silently break — a failure mode named the **fragile base class problem**.

**Worked example.** A `Stack` class implemented by inheriting from a general-purpose `List`, reusing `List`'s `add`/`remove` methods internally to implement `push`/`pop`:
```
class Stack(List):
    def push(self, item): self.add(item)
    def pop(self): return self.remove(len(self) - 1)
```
This looks like reasonable reuse — until `List`'s author, for an unrelated reason, overrides `add()` internally to also call a new `validate()` hook, and `validate()` happens to reject items above a certain size for `List`'s own use cases. `Stack.push()` now silently inherits that unrelated validation restriction, breaking `Stack`'s own contract (a stack should accept anything) — not because `Stack`'s code changed at all, but because it depended on `List`'s *implementation details*, not just its documented interface, and those details shifted underneath it.

### Composition avoids the fragile base class problem by construction
Rebuilding the same `Stack` via composition:
```
class Stack:
    def __init__(self):
        self._items = []          # a composed List, used only via its public interface
    def push(self, item): self._items.append(item)
    def pop(self): return self._items.pop()
```
Here, `Stack` uses `_items` (a `list`) strictly through its stable, documented public interface (`append`, `pop`) and has no dependency on `list`'s internal implementation. If `list`'s internal implementation changes in a future language version (while its documented interface stays the same, as it should), `Stack` is completely unaffected — the coupling is only to the interface, exactly as `design-patterns/01` recommends.

### White-box reuse (inheritance) vs. black-box reuse (composition)
The book's own terms for this distinction: inheritance is "white-box" reuse — the subclass can see, and can become entangled with, the parent's internals, since subclasses typically have access to protected members and inherited implementation. Composition is "black-box" reuse — the composed object's internals are never visible or reachable at all; only its public interface is used. Black-box reuse trades away certain conveniences (you can't override a small piece of the composed object's internal logic the way a subclass could override one method) in exchange for a much stronger, more reliable decoupling.

### When inheritance genuinely is the right tool
The book doesn't argue inheritance is never appropriate — it argues for reaching for it specifically to reuse an **interface** (a true is-a relationship, where every operation the base class promises genuinely makes sense for the subclass, and the subclass is usable anywhere the base class is expected — the Liskov Substitution Principle, developed fully in `software-engineering/clean-architecture`) rather than purely to reuse *implementation* convenience. A `Circle` and `Square` both genuinely being a `Shape`, each implementing `area()` according to the same interface contract, is a legitimate is-a relationship; a `Stack` inheriting from `List` purely to borrow `add`/`remove` methods, with no genuine is-a relationship (a stack isn't really "a kind of" general list — it has a deliberately narrower, different contract), is reuse-by-implementation-convenience dressed up as inheritance, and is exactly the pattern this lesson argues against.

### Composition enables runtime flexibility inheritance structurally cannot
Because a composed object is just a field holding a reference, it can be swapped at runtime (directly enabling patterns like Strategy, `design-patterns/09`) — `stack.set_storage(new_backing_store)` is a normal method call. An inheritance relationship, by contrast, is fixed at compile/class-definition time — you cannot change which class a given object inherits from while the program is running. Any design that anticipates needing to vary behavior dynamically (per `code-complete/03`'s "identify what varies" heuristic) is, by construction, better served by composition than inheritance.

## Pros
- Composition avoids the fragile base class problem entirely, since it only depends on a stable public interface, never on implementation internals.
- Composed behavior can be swapped at runtime, enabling flexibility (Strategy-like designs) that a fixed inheritance hierarchy cannot provide.
- Composition tends to produce flatter, easier-to-reason-about object graphs than deep inheritance hierarchies, which can become hard to trace once several levels deep.

## Cons
- Composition requires writing more explicit delegation code (forwarding calls to the composed object) than inheritance's "free" method reuse, which can feel like more boilerplate for genuinely simple cases.
- A true is-a relationship where every base-class operation genuinely applies is sometimes most naturally and simply expressed via inheritance, and forcing composition onto it can be more awkward than the straightforward inheritance alternative.
- Deep composition chains (an object composed of an object composed of another object) can themselves become hard to trace, trading one kind of complexity (fragile inheritance) for another (delegation sprawl) if not kept in check.

## Alternatives
- **Mixins / traits** (in languages that support them) — a middle ground offering some of inheritance's implementation-reuse convenience with somewhat more modularity than a single deep hierarchy, though still subject to a milder version of the fragile-base-class risk if a mixin's internals are relied upon.
- **Interface-only inheritance (implementing multiple interfaces, no shared implementation)** — reuse the interface benefit of inheritance (`design-patterns/01`'s "program to an interface") with zero of the implementation-coupling risk, at the cost of needing every implementing class to provide its own full implementation.
- **Pure functional composition (function composition instead of object composition)** — in functional-leaning codebases, achieve similar flexibility by composing small functions rather than objects, sidestepping the inheritance-vs-composition question for OO classes entirely.

## When to use it
Default to composition whenever you're reusing another class's *behavior* for convenience, especially when you anticipate needing to swap or configure that behavior later. Reach for inheritance specifically when there's a genuine is-a relationship where the subclass is a true substitutable specialization of the base class's documented interface (Liskov Substitution).

## When NOT to use it
Don't default to composition so rigidly that you force awkward delegation boilerplate onto a genuinely simple, stable is-a relationship where inheritance is the clearer, more natural fit. Don't use inheritance purely to avoid writing a few lines of delegation code when the relationship isn't genuinely is-a — that's exactly the fragile-base-class trap.

## Key takeaways / mental model
Before inheriting from a class, ask: "is every one of the base class's operations genuinely something my subclass should support, such that any code expecting the base class would work correctly if I substituted my subclass instead?" If the honest answer is no — if you're really just trying to reuse a couple of convenient methods — use composition instead.

## Self-check questions
1. Using the `Stack`-inherits-from-`List` example, explain concretely how a change to `List`'s internals (not its interface) could break `Stack`, and why composition avoids that failure mode.
2. What's the difference between "white-box" and "black-box" reuse, and which does inheritance represent?
3. Give an example of a genuine is-a relationship from your own code where inheritance is the right tool, and justify it using the Liskov Substitution idea.
4. Why does composition, but not inheritance, naturally support swapping behavior at runtime?

## References
- Design Patterns: Elements of Reusable Object-Oriented Software (Gamma, Helm, Johnson, Vlissides), Chapter 1: "Introduction" (Inheritance versus Composition section).
