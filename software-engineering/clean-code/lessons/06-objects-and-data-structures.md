---
id: clean-code/06
subject: clean-code
title: Objects and Data Structures
slug: objects-and-data-structures
status: drafted
mastery:
seniority: mid
source: Clean Code (Robert C. Martin), Chapter 6
prerequisites: [clean-code/03]
created: 2026-08-10
updated: 2026-08-10
---

# Objects and Data Structures

## TL;DR
Objects hide their data behind behavior (you ask them to do something; you don't reach in and grab their fields); data structures expose their data with no meaningful behavior (you reach in and operate on the fields yourself). These are deliberately opposite designs, and mixing them — a "hybrid" with both exposed fields and meaningful methods — gives you the worst of both: fragile to change in either direction.

## The idea
The chapter draws a sharp, deliberate line between two ways of organizing data and behavior, and argues that good design commits clearly to one or the other for a given class, rather than blending them.

**Objects** hide their internal representation and expose behavior: you call `shape.area()` and the shape decides how to compute that, based on its own internal, hidden representation — you never need to know whether it's a circle, square, or triangle internally. Adding a new *kind* of shape means adding a new class that implements the same interface; existing calling code is untouched.

**Data structures** (in this book's specific sense) expose their data and have little or no meaningful behavior — a plain struct/record with public fields, or getters/setters that are just field access in disguise. External code that operates on the data structure decides what to do with the fields itself (a separate function computes area based on the exposed shape type and dimensions). Adding a new *operation* on the data means adding a new function; existing data-structure definitions are untouched.

**The core insight — these are mirror images, on purpose:** objects make adding new *types* easy (implement the interface) but adding new *operations* hard (every implementing class needs the new method); data structures make adding new *operations* easy (write a new function) but adding new *types* hard (every existing operation-function needs a new case for the new type). This is sometimes called the "Vishnu/expression problem" duality — you can optimize for one axis of extensibility or the other, but a design mixing both loosely doesn't get the benefit of either.

## How it works

### Worked example: procedural (data-structure) style
```
class Square:
    def __init__(self, side): self.side = side

class Circle:
    def __init__(self, radius): self.radius = radius

def area(shape):
    if isinstance(shape, Square):
        return shape.side ** 2
    elif isinstance(shape, Circle):
        return math.pi * shape.radius ** 2
```
Adding a new operation (`perimeter(shape)`) is trivial — write one new function, touch nothing else. Adding a new shape (`Triangle`) requires finding and modifying *every* existing operation function (`area`, and now `perimeter`, and any future one) to add a new `elif` branch — the change is scattered across every operation, in proportion to how many operations already exist.

### Worked example: object-oriented style
```
class Shape:
    def area(self): raise NotImplementedError

class Square(Shape):
    def __init__(self, side): self.side = side
    def area(self): return self.side ** 2

class Circle(Shape):
    def __init__(self, radius): self.radius = radius
    def area(self): return math.pi * self.radius ** 2
```
Adding a new shape (`Triangle`) is trivial — one new class implementing `area()`, touching nothing existing. Adding a new operation (`perimeter()`) requires touching *every* existing shape class to add the new method — the change is scattered across every type, in proportion to how many types already exist.

### The Law of Demeter connects directly here
`pragmatic-programmer/10` established "ask, don't reach through" as a coupling discipline; this chapter gives it its precise object-vs-data-structure grounding: the Law of Demeter is a rule specifically for **objects** (ask an object a question, don't chain through its internals) and doesn't apply the same way to genuine data structures, whose entire purpose is to expose their fields for external code to operate on directly. Confusing the two — applying object-style encapsulation discipline to something that's really just a data-transfer struct, or applying data-structure-style field access to something meant to be an encapsulated object — is a design-clarity failure, not a minor style nit.

### The hybrid trap
A "hybrid" class exposes fields/getters-setters *and* has meaningful behavior methods that depend on those exposed internals. This is, the book argues, worse than committing to either pure style: adding a new type still requires touching every operation that switches on type (data-structure downside), *and* adding a new operation still requires touching every type's implementation if behavior is spread across classes (object downside) — plus, because internals are exposed, external code can bypass the object's own behavior methods and manipulate state directly, breaking whatever invariants the behavior methods were trying to maintain.

### DTOs and Active Record: legitimate, narrow uses of the data-structure style
Not every class should be a "real" encapsulated object. **Data Transfer Objects (DTOs)** — plain structures moving data between layers/processes/serialization boundaries (see `software-engineering/enterprise-patterns`) — are appropriately data-structure-style: their entire job is to expose fields for (de)serialization, and adding encapsulation there would add friction with no benefit. **Active Record** objects (see `software-engineering/enterprise-patterns`) are a deliberate, bounded hybrid — they carry both data access and minimal persistence behavior — accepted specifically because their scope is narrow and well-understood (mapping one row to one object), not because hybrids are generally fine.

## Pros
- Choosing deliberately between object and data-structure style makes a class's extensibility trade-off explicit and intentional rather than accidental.
- Object style, applied where new *types* are the expected axis of change, isolates that change cleanly (open/closed principle, foreshadowing `software-engineering/clean-architecture`'s OCP).
- Data-structure style, applied where new *operations* are the expected axis of change, keeps operations simple, inspectable, and free of forced ceremony.

## Cons
- Committing to pure object style when new operations turn out to be the actual frequent change (not new types) forces touching every class repeatedly — the wrong axis was optimized for.
- Committing to pure data-structure style when new types turn out to be the actual frequent change forces touching every operation function repeatedly — same problem, opposite direction.
- Correctly predicting which axis (new types vs. new operations) will change more often requires real domain judgment, and getting it wrong has a real refactoring cost later.

## Alternatives
- **Visitor pattern** (see `software-engineering/design-patterns`) — a structured way to add new operations to an existing object hierarchy without modifying each class, partially mitigating the object style's "adding operations is hard" weakness at the cost of real complexity.
- **Pattern matching / sum types (in languages that support them, e.g., Rust, Scala, Kotlin)** — give some of data-structure style's "easy new operations" benefit with compiler-enforced exhaustiveness checking, catching the "forgot to handle a new type in this operation" failure mode statically instead of at runtime.
- **Functional core, imperative shell** — a broader architectural alternative where data flows as plain, transparent data structures through pure transformation functions (echoing `pragmatic-programmer/12`), reserving encapsulated objects for the imperative boundary layers (I/O, side effects).

## When to use it
Choose object style when you expect the *set of types/variants* to grow or vary (plugins, strategies, polymorphic behavior) and the operations on them are relatively stable. Choose data-structure style when you expect the *set of operations* to grow and the types themselves are relatively stable and simple (DTOs, value objects, data crossing a serialization boundary).

## When NOT to use it
Don't build a hybrid by reflexively adding both public getters/setters and behavior methods to every class "just in case" — pick a lane deliberately, per class, based on which axis (types or operations) is actually expected to change for that specific concept.

## Key takeaways / mental model
Ask, for any class: "am I more likely to add new *kinds* of this, or new *things this can do*?" New kinds expected -> object style (encapsulate behavior, one class per kind). New operations expected -> data-structure style (expose data, one function per operation). Never both by accident.

## Self-check questions
1. Using the shape example, explain concretely what changes (and where) when you add a new shape under each style, and when you add a new operation under each style.
2. Why does the Law of Demeter (`pragmatic-programmer/10`) apply cleanly to objects but not meaningfully to data structures?
3. Give an example of a "hybrid" class from real code you've seen, and explain which of the two downsides (touching every operation, or bypassing behavior via exposed fields) it actually suffered from.
4. Why are DTOs and Active Record objects treated as legitimate exceptions rather than violations of this lesson's principle?

## References
- Clean Code: A Handbook of Agile Software Craftsmanship (Robert C. Martin), Chapter 6: "Objects and Data Structures".
