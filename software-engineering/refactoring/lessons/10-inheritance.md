---
id: refactoring/10
subject: refactoring
title: Dealing with Inheritance
slug: inheritance
status: drafted
mastery:
seniority: mid
source: Refactoring, 2nd ed. (Martin Fowler), Chapter 12
prerequisites: [refactoring/06, design-patterns/02]
created: 2026-08-10
updated: 2026-08-10
---

# Dealing with Inheritance

## TL;DR
Pull Up Method/Field moves duplicated logic or data from sibling subclasses up to their shared superclass; Push Down Method/Field does the reverse, moving something from a superclass to only the specific subclasses that actually need it. Replace Superclass with Delegate (or vice versa) corrects an inheritance relationship that was never a genuine is-a relationship in the first place — the concrete migration path away from `design-patterns/02`'s fragile-base-class problem, once it's already been built.

## The idea
Inheritance hierarchies, once built, tend to accumulate a specific, recognizable set of problems as requirements evolve: duplicated logic across sibling subclasses that should have been shared, a superclass method that only some subclasses actually need, or — most fundamentally — an inheritance relationship that was a reasonable-seeming shortcut at the time but never actually represented a genuine is-a relationship (`design-patterns/02`'s Liskov Substitution concern). This lesson's techniques are the concrete, mechanical, safe ways to fix each of these once identified, rather than a one-time rewrite of the whole hierarchy.

## How it works

### Pull Up Method / Pull Up Field — eliminate sibling duplication
When two or more subclasses of the same superclass have near-identical methods or fields (Duplicated Code, `refactoring/04`, specifically arising across a hierarchy rather than within one class), move the shared logic/data up to the superclass, where every subclass inherits it once instead of each maintaining its own copy.

**Worked example.**
```
# Before — near-identical logic duplicated across siblings
class Engineer(Employee):
    def annual_cost(self): return self.salary * 12 + self.bonus

class Manager(Employee):
    def annual_cost(self): return self.salary * 12 + self.bonus   # identical logic, duplicated

# After — pulled up to the shared superclass
class Employee:
    def annual_cost(self): return self.salary * 12 + self.bonus

class Engineer(Employee): pass
class Manager(Employee): pass
```
A future change to how annual cost is computed now happens once, in `Employee`, rather than requiring an update to every sibling subclass independently — directly resolving the change-amplification risk (`philosophy-of-software-design/01`) that duplicated sibling logic creates.

### Push Down Method / Push Down Field — the precise inverse
When a superclass method or field is actually only relevant to *some* of its subclasses (not all), keeping it on the superclass forces every subclass to inherit something it doesn't need or, worse, that doesn't correctly apply to it — a Liskov Substitution violation waiting to surface. Push Down moves it to specifically the subclasses that genuinely need it, removing it from the superclass and from the subclasses that don't.

**Worked example.** If only `SalariedEmployee` (not `HourlyEmployee`, another sibling) genuinely has a `bonus` concept, keeping `bonus` on the shared `Employee` superclass means `HourlyEmployee` inherits a field that means nothing for it (perhaps defaulting to zero, silently, forever) — pushing `bonus` down to `SalariedEmployee` specifically removes that meaningless inherited baggage from `HourlyEmployee`, making the hierarchy accurately reflect which behavior/data actually belongs to which concrete type.

### Replace Superclass with Delegate — fix a relationship that was never really is-a
Sometimes a class inherits from another purely to reuse some of its methods conveniently (echoing `design-patterns/02`'s "white-box reuse" caution directly) — without every one of the superclass's operations genuinely making sense for the subclass. This shows up as `design-patterns/02`'s fragile base class problem in a mature codebase, and the fix is exactly what that lesson recommends in the abstract, now given as a concrete, step-by-step migration: replace the inheritance relationship with composition, having the class hold a reference to (delegate to) an instance of the former "superclass" instead of inheriting from it directly.

**Worked example — revisiting `design-patterns/02`'s own `Stack`-inherits-from-`List` case, as a refactoring rather than a from-scratch design choice:**
```
# Before — inheritance, exposing all of List's operations (including ones Stack shouldn't have)
class Stack(List):
    def push(self, item): self.append(item)
    def pop(self): return self.pop_at(len(self) - 1)

# After — composition via delegation, only push/pop are exposed
class Stack:
    def __init__(self): self._items = []
    def push(self, item): self._items.append(item)
    def pop(self): return self._items.pop()
```
This migration, done incrementally (verify each delegated method against tests before removing the corresponding inherited one, per `refactoring/01`'s small-steps discipline), removes `Stack`'s exposure to every one of `List`'s other operations (insertion at arbitrary positions, slicing) that never should have been part of a stack's contract in the first place — fixing, after the fact, exactly the design mistake `design-patterns/02` warns against making up front.

### Replace Delegate with Superclass — the (rarer) inverse
Occasionally the opposite correction is warranted: a class was built using composition/delegation to another, but it turns out every one of the delegate's operations genuinely does apply, and the relationship really is a clean is-a — in which case converting to inheritance can simplify the code by removing repetitive delegation boilerplate. This is explicitly the less common direction, since — per `design-patterns/02` — composition is the *safer default*; this inverse is only warranted once a genuine, thoroughly-checked is-a relationship is confirmed.

## Pros
- Pull Up Method/Field directly eliminates cross-sibling duplication, reducing change amplification for logic that's genuinely shared.
- Push Down keeps a hierarchy's structure honest about which behavior/data actually belongs to which concrete subclasses, preventing silent Liskov violations.
- Replace Superclass with Delegate provides a safe, incremental migration path away from an inheritance relationship that's already causing fragile-base-class problems, rather than requiring a risky big-bang rewrite.

## Cons
- Pull Up Method assumes the duplicated logic really is identical (or should be) across all siblings — pulling up logic that's only coincidentally similar today, but conceptually independent, risks creating an artificial, brittle shared dependency.
- Push Down, applied repeatedly as a hierarchy evolves, can leave a superclass increasingly thin and possibly not worth keeping at all — occasionally a sign the hierarchy itself should be reconsidered rather than incrementally trimmed.
- Replace Superclass with Delegate is a genuinely more involved migration than the other techniques in this lesson (updating every place the old inherited interface was relied upon, including any place that used the subclass polymorphically as an instance of the superclass), and needs the full safety-net discipline from `refactoring/03`.

## Alternatives
- **Extract Superclass**, the inverse-direction sibling-consolidation technique — when two previously-unrelated classes turn out to share enough behavior to warrant a *new* common superclass, rather than pulling shared logic into an already-existing one.
- **Composition from the start** (`design-patterns/02`) — avoids ever needing Replace Superclass with Delegate by simply not building the fragile inheritance relationship in the first place; this lesson's technique is specifically the remedial fix once that mistake already exists in a live codebase.
- **Mixins/traits** (in supporting languages) — a middle-ground alternative to full Pull Up/Push Down cycles, sharing implementation across a hierarchy without necessarily committing to a single, rigid superclass structure.

## When to use it
Use Pull Up when you spot genuine, meaningful duplication across sibling subclasses. Use Push Down when a superclass member doesn't actually apply to all its subclasses. Use Replace Superclass with Delegate once an existing inheritance relationship is confirmed to violate Liskov Substitution or is causing fragile-base-class problems in practice.

## When NOT to use it
Don't Pull Up logic that's only coincidentally similar, not conceptually shared — that risks creating an artificial coupling between siblings that should stay independent. Don't undertake a full Replace Superclass with Delegate migration for a hierarchy that's causing no actual problems, purely on the principle that composition is generally preferred — the migration has a real cost that should be justified by a genuine, observed issue.

## Key takeaways / mental model
When you see the same logic in sibling subclasses, ask "is this genuinely the same concept, or coincidentally similar?" before pulling it up. When a superclass member doesn't fit all its subclasses, push it down to where it actually belongs. And when an inheritance relationship is causing real fragile-base-class pain, migrate it to composition incrementally, verifying each step, rather than declaring the whole hierarchy broken and starting over.

## Self-check questions
1. Using the `Employee` example, explain what change-amplification risk Pull Up Method eliminates, and how you'd verify the duplicated logic is genuinely the same concept before pulling it up.
2. Describe a superclass member from a hierarchy you've seen that didn't actually apply to all subclasses, and explain how Push Down would fix it.
3. Walk through migrating the `Stack`/`List` example from inheritance to delegation, step by step, verifying behavior at each stage.
4. Under what specific circumstance would Replace Delegate with Superclass (the rarer inverse) actually be the right call?

## References
- Refactoring: Improving the Design of Existing Code, 2nd ed. (Martin Fowler), Chapter 12: "Dealing with Inheritance".
- See also: `design-patterns/02` (Composition Over Inheritance) for the design-time version of the problem this lesson fixes after the fact.
