---
id: design-patterns/11
subject: design-patterns
title: "Behavioral: Iterator, Mediator, Visitor, and the Rest"
slug: iterator-mediator-visitor
status: drafted
mastery:
seniority: senior
source: Design Patterns (Gamma, Helm, Johnson, Vlissides), Chapter 5
prerequisites: [design-patterns/10]
created: 2026-08-10
updated: 2026-08-10
---

# Behavioral: Iterator, Mediator, Visitor, and the Rest

## TL;DR
Iterator provides a uniform way to traverse a collection without exposing its internal structure — now largely built into modern languages, but worth understanding as the reason `for` loops over arbitrary collections work at all. Mediator centralizes complex many-to-many communication between objects into one coordinator, so objects don't need direct references to each other. Visitor lets you add new operations to a stable object structure without modifying the structure's classes — directly resolving the "hard to add operations" downside of the object style from `clean-code/06`.

## The idea
This closing lesson gathers the remaining, still-broadly-useful behavioral patterns from the catalog, several of which have become so foundational that they're now built directly into mainstream language features rather than something you'd typically hand-implement — worth recognizing by name even when you're really just using the language's native support for the same underlying idea.

## How it works

### Iterator — traverse without exposing internal structure
Iterator provides a standard interface (`has_next()`/`next()`, or a language's native iteration protocol) for stepping through a collection's elements one at a time, without the calling code needing to know whether the collection is backed by an array, a linked list, a tree, or something else — directly the Law of Demeter's "ask, don't reach through" principle (`pragmatic-programmer/10`), applied specifically to traversal.

**Worked example (the pattern, underneath what a language's `for` loop already gives you for free):**
```
class TreeIterator:
    def __init__(self, root):
        self._stack = [root] if root else []
    def has_next(self): return len(self._stack) > 0
    def next(self):
        node = self._stack.pop()
        self._stack.extend(reversed(node.children))
        return node.value

it = TreeIterator(tree_root)
while it.has_next():
    print(it.next())     # caller never touches the tree's internal structure directly
```
Most modern languages provide this exact capability natively (Python's `for x in collection`, Java's `Iterable`, C#'s `IEnumerable`) — the pattern's continuing relevance is less "you'll hand-write this" and more "understanding *why* uniform iteration over heterogeneous internal structures is valuable in the first place," which matters whenever you're designing a *new*, custom traversable structure and deciding what iteration interface to expose for it.

### Mediator — centralize complex many-to-many communication
When many objects need to communicate with each other, direct object-to-object references produce a combinatorial tangle (each object holding references to many others, and any change to one object's interface potentially rippling to every other object that talks to it directly). Mediator introduces one central object that all the participants talk to instead of talking to each other directly, converting many-to-many coupling into many-to-one.

**Worked example.** A UI form where a checkbox, a text field, and a submit button all need to react to each other's state (checking the box enables the text field; the text field being non-empty enables the submit button):
```
class FormMediator:
    def __init__(self, checkbox, text_field, submit_button):
        self.checkbox, self.text_field, self.submit_button = checkbox, text_field, submit_button
    def on_checkbox_changed(self):
        self.text_field.set_enabled(self.checkbox.is_checked)
    def on_text_changed(self):
        self.submit_button.set_enabled(bool(self.text_field.value) and self.checkbox.is_checked)
```
Without a Mediator, `checkbox`, `text_field`, and `submit_button` would each need direct references to each other, and any new widget added to this interaction (say, a validation warning label) would require touching every existing widget's code to add the new cross-reference. With Mediator, only the `FormMediator` needs to change — the widgets themselves stay unaware of each other entirely, each only reporting its own state changes to the mediator.

### Visitor — add new operations to a stable structure without modifying its classes
Directly resolving `clean-code/06`'s named trade-off: object-oriented style makes adding new *types* easy but adding new *operations* hard (every class needs the new method). Visitor is a specific, structured workaround: define a separate `Visitor` interface with one `visit_X` method per existing type, and have each element in the structure accept a visitor and call back the appropriate `visit_X` method on it (`accept(visitor)` calls `visitor.visit_circle(self)`, etc.) — new operations are then added as entirely new Visitor implementations, touching none of the existing element classes.

**Worked example.**
```
class ShapeVisitor:
    def visit_circle(self, circle): raise NotImplementedError
    def visit_square(self, square): raise NotImplementedError

class Circle:
    def __init__(self, radius): self.radius = radius
    def accept(self, visitor: ShapeVisitor): visitor.visit_circle(self)

class Square:
    def __init__(self, side): self.side = side
    def accept(self, visitor: ShapeVisitor): visitor.visit_square(self)

class AreaVisitor(ShapeVisitor):                         # a NEW operation, no existing class touched
    def visit_circle(self, circle): return math.pi * circle.radius ** 2
    def visit_square(self, square): return square.side ** 2

class PerimeterVisitor(ShapeVisitor):                     # ANOTHER new operation, still zero changes elsewhere
    def visit_circle(self, circle): return 2 * math.pi * circle.radius
    def visit_square(self, square): return 4 * square.side
```
Adding `PerimeterVisitor` required writing one new class and touching nothing in `Circle` or `Square` — directly recovering, via this pattern, the "easy to add operations" property that `clean-code/06` identified as the data-structure style's advantage and the object style's specific weakness, while still keeping the encapsulation benefits of the object style for everything else.

### The trade-off Visitor makes explicit
Visitor is only worth its ceremony (a whole parallel `Visitor` interface, an `accept` method on every element class) when the *element structure itself* is genuinely stable (rarely gaining new shape types) but *operations on it* are genuinely expected to grow (new calculations, new exporters, new validators) — precisely the mirror-image condition to when plain object-style polymorphism (one method per operation on each class) is the better fit, per `clean-code/06`'s original framing. Adding a new element type (`Triangle`) under Visitor requires updating the `ShapeVisitor` interface *and* every existing Visitor implementation — exactly as costly as adding a new type under the plain data-structure style, so Visitor doesn't escape the fundamental trade-off, it just relocates which axis (types vs. operations) is cheap and which is expensive, deliberately, to match the actual expected direction of change.

## Pros
- Iterator provides uniform traversal regardless of internal structure, and understanding it clarifies why to design custom collection types with a clean, standard iteration interface.
- Mediator converts an unmanageable many-to-many web of direct references into a single, centrally-understandable coordination point.
- Visitor recovers "easy to add operations" for an object-style structure without abandoning encapsulation, specifically when that trade-off direction genuinely matches expected future change.

## Cons
- Mediator can itself become an overloaded, low-cohesion "god object" (echoing `clean-code/10`) if it accumulates too much unrelated coordination logic over time.
- Visitor's ceremony (a full parallel interface, an `accept` method on every element) is substantial, and it locks in the assumption that element types are stable — if that assumption later proves wrong and new types start appearing frequently, Visitor becomes actively more painful than plain polymorphism would have been.
- All three patterns add real structural indirection that's disproportionate for small, simple, unlikely-to-grow structures.

## Alternatives
- **Native language iteration protocols**, instead of hand-rolled Iterator — the practical default in virtually all modern code; understanding the pattern mainly informs *designing* new iterable types well, not reimplementing existing iteration mechanisms.
- **Direct object references / event buses**, instead of Mediator — direct references are fine for a small, genuinely simple set of interacting objects; an event bus (`design-patterns/09`'s Observer, generalized) is a more distributed-friendly alternative for larger or looser coordination needs.
- **Pattern matching / double dispatch in languages with strong native support** — some languages offer built-in mechanisms (sum types with exhaustive pattern matching) that achieve Visitor's "add operations easily, compiler-checked exhaustiveness" benefit with substantially less boilerplate than the classic OO Visitor structure.

## When to use it
Use Iterator's underlying idea whenever designing a new custom collection/structure — expose a standard iteration interface rather than internal structure. Use Mediator when object-to-object coupling in a many-to-many interaction has become genuinely unmanageable. Use Visitor specifically when an element structure is stable but operations on it are expected to keep growing.

## When NOT to use it
Don't hand-implement Iterator when your language's native iteration protocol already covers the need. Don't reach for Mediator for a small, simple set of interactions that direct references already handle clearly. Don't use Visitor if you expect the element structure itself (not just the operations) to keep growing — that's exactly the case where Visitor's cost outweighs its benefit.

## Key takeaways / mental model
For Iterator: use your language's native support, but design new structures to expose the same kind of clean, structure-hiding traversal. For Mediator: when you notice a tangled many-to-many web of direct references, centralize it. For Visitor: ask "is my structure stable but my operations growing, or the reverse?" — the answer tells you whether Visitor helps or hurts.

## Self-check questions
1. Explain why a modern language's built-in `for` loop is, underneath, an application of the Iterator pattern, even though you never write an explicit `Iterator` class for it.
2. Using the form-widget example, describe what would go wrong (in terms of coupling) if Mediator were removed and every widget held direct references to every other widget instead.
3. Using the shapes example, explain exactly what has to change if a new `Triangle` type is added under the Visitor design, and why that's just as costly as it would be under the plain data-structure style from `clean-code/06`.
4. Describe a domain where you'd expect operations to grow faster than types (favoring Visitor) versus one where you'd expect the opposite (favoring plain polymorphism).

## References
- Design Patterns: Elements of Reusable Object-Oriented Software (Gamma, Helm, Johnson, Vlissides), Chapter 5: "Behavioral Patterns" (Iterator, Mediator, Visitor sections, and the remaining catalog entries: Interpreter, Memento).
- See also: `clean-code/06` (Objects and Data Structures) for the types-vs-operations trade-off Visitor directly addresses.
