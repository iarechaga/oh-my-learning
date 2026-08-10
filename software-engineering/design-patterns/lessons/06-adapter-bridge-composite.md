---
id: design-patterns/06
subject: design-patterns
title: "Structural: Adapter, Bridge, Composite"
slug: adapter-bridge-composite
status: drafted
mastery:
seniority: mid
source: Design Patterns (Gamma, Helm, Johnson, Vlissides), Chapter 4
prerequisites: [design-patterns/02]
created: 2026-08-10
updated: 2026-08-10
---

# Structural: Adapter, Bridge, Composite

## TL;DR
Adapter converts one interface into another your code already expects, so incompatible components can work together — the formal name for `clean-code/08`'s boundary-wrapping technique. Bridge separates an abstraction from its implementation so both can vary and evolve independently, avoiding a combinatorial explosion of subclasses. Composite lets clients treat a single object and a whole tree of objects uniformly, through one shared interface.

## The idea
All three patterns in this lesson are about *structuring relationships between objects* so that a system is more flexible to extend or integrate than a naive, direct-coupling approach would allow — but each solves a distinctly different structural problem, and mixing them up in conversation ("shouldn't we use an Adapter here?" when Bridge is what's actually needed) is a common source of confused design discussions.

## How it works

### Adapter — make an incompatible interface fit
When you have an existing class with a useful implementation, but its interface doesn't match what your calling code expects (commonly: a third-party library, or legacy code you can't modify), Adapter wraps it in a new class that implements the interface your code wants, translating calls to the wrapped object's actual interface underneath.

**Worked example.** Your code expects a `PaymentProcessor` interface with a `charge(amount)` method, but a newly-adopted vendor SDK exposes `submitTransaction(cents, currency_code)`:
```
class PaymentProcessor:
    def charge(self, amount: float): raise NotImplementedError

class VendorSdkAdapter(PaymentProcessor):
    def __init__(self, vendor_client):
        self.vendor_client = vendor_client
    def charge(self, amount: float):
        cents = int(amount * 100)
        self.vendor_client.submitTransaction(cents, "USD")
```
This is exactly `clean-code/08`'s boundary-wrapping technique, now given its formal pattern name — the rest of your codebase depends only on `PaymentProcessor`, never on the vendor SDK's specific, differently-shaped interface.

### Bridge — decouple an abstraction from its implementation so both vary independently
Bridge addresses a specific, easy-to-miss trap: when a class hierarchy has *two* independent dimensions of variation (say, "what kind of shape" and "how it's rendered"), naive inheritance produces a combinatorial explosion — a subclass for every *combination* (`VectorCircle`, `RasterCircle`, `VectorSquare`, `RasterSquare`, ...). Bridge splits the two dimensions into two separate, independently-extensible hierarchies connected by composition (an abstraction *holds a reference to* an implementation, rather than inheriting a fixed combination of both).

**Worked example.**
```
class Renderer:                          # the "implementation" hierarchy
    def render_circle(self, radius): raise NotImplementedError

class VectorRenderer(Renderer):
    def render_circle(self, radius): ...  # draw as vector paths

class RasterRenderer(Renderer):
    def render_circle(self, radius): ...  # draw as pixels

class Shape:                              # the "abstraction" hierarchy
    def __init__(self, renderer: Renderer):
        self.renderer = renderer          # the "bridge" — composition, not inheritance

class Circle(Shape):
    def __init__(self, renderer, radius):
        super().__init__(renderer)
        self.radius = radius
    def draw(self):
        self.renderer.render_circle(self.radius)
```
Adding a new shape (`Square`) requires one new class, reused with *any* existing renderer. Adding a new renderer (`SvgRenderer`) requires one new class, usable with *any* existing shape. Neither addition requires touching or multiplying the other hierarchy — precisely avoiding the N×M subclass explosion a single, combined inheritance hierarchy would force.

### Composite — treat one object and a tree of objects uniformly
When a domain naturally forms a part-whole tree (a filesystem of files and folders, a UI of widgets and containers of widgets, an organization chart), Composite defines one shared interface for both individual ("leaf") objects and groupings ("composite") of them, so client code can operate on either without needing to know or check which one it has.

**Worked example.**
```
class FileSystemNode:
    def get_size(self) -> int: raise NotImplementedError

class File(FileSystemNode):               # leaf
    def __init__(self, size): self.size = size
    def get_size(self): return self.size

class Folder(FileSystemNode):             # composite
    def __init__(self): self.children = []
    def add(self, node: FileSystemNode): self.children.append(node)
    def get_size(self):
        return sum(child.get_size() for child in self.children)   # recurses transparently

root = Folder()
root.add(File(100))
sub = Folder()
sub.add(File(50))
root.add(sub)
root.get_size()  # 150 — works identically whether summing files or nested folders
```
Calling code never needs an `if isinstance(node, Folder)` check anywhere — `get_size()` is called uniformly, and the recursion through nested composites happens transparently through the shared interface, directly avoiding the repeated-type-checking smell `clean-code/12` warns about.

## Pros
- Adapter lets you integrate incompatible third-party or legacy code without modifying it, isolating translation logic to one clearly-scoped class.
- Bridge avoids combinatorial subclass explosions when two independent dimensions of variation exist, letting each evolve without affecting the other.
- Composite lets client code treat individual objects and entire subtrees uniformly, eliminating type-checking branches for "is this one item or a group" throughout the codebase.

## Cons
- Adapter adds an extra layer that, for a very simple, one-off interface mismatch, might be more overhead than a direct, ad hoc translation at the single call site that needs it.
- Bridge is only worth its structural cost when there genuinely are two independent dimensions of variation; forcing it onto a hierarchy with only one real dimension adds unnecessary indirection.
- Composite's uniform-interface elegance can strain when leaf and composite nodes genuinely need meaningfully different operations (e.g., "add a child" makes no sense on a `File`) — often handled by throwing/no-op-ing on leaves, which is a minor interface-purity compromise.

## Alternatives
- **Direct, ad hoc translation code at the point of use, without a formal Adapter class** — reasonable for a genuinely single-use, unlikely-to-repeat interface mismatch.
- **Strategy pattern** (`design-patterns/09`) instead of Bridge — when only one dimension actually varies (not two independent ones), Strategy is the simpler, more directly applicable pattern.
- **Flat lists with explicit type tags and manual recursion**, instead of Composite — sometimes simpler for shallow, rarely-nested structures where the uniform-interface elegance of Composite isn't worth its structural setup.

## When to use it
Use Adapter whenever integrating a component whose interface doesn't match what your code expects, especially third-party or legacy code you shouldn't modify directly. Use Bridge when you find yourself facing (or anticipating) a two-dimensional combinatorial subclass explosion. Use Composite whenever your domain naturally forms a part-whole tree and client code would otherwise need repeated type-checks to handle individual items versus groups.

## When NOT to use it
Don't wrap a trivial, unlikely-to-repeat interface mismatch in a formal Adapter class if an inline translation at the one call site is clearly simpler. Don't apply Bridge to a hierarchy with only one real axis of variation — that's solved more simply by ordinary inheritance or Strategy. Don't force Composite onto a structure that isn't genuinely a recursive part-whole tree.

## Key takeaways / mental model
Adapter: "I have the right behavior, wrong shape — translate the shape." Bridge: "I have two independent things that vary — split them so neither multiplies the other." Composite: "I have a tree of parts and wholes — give them one shared interface so client code stops asking 'which kind is this?'"

## Self-check questions
1. Using the payment example, explain what would go wrong if you skipped the Adapter and called the vendor SDK's methods directly throughout your codebase.
2. Why does a single, combined inheritance hierarchy for "shape type x rendering method" become unmanageable as both dimensions grow, and how does Bridge fix that specifically?
3. Give an example of a part-whole tree from your own domain that could benefit from Composite, and describe what type-checking code it would eliminate.
4. Describe a case where introducing Bridge would be premature, given only one axis of variation currently exists.

## References
- Design Patterns: Elements of Reusable Object-Oriented Software (Gamma, Helm, Johnson, Vlissides), Chapter 4: "Structural Patterns" (Adapter, Bridge, Composite sections).
- See also: `clean-code/08` (Boundaries and Third-Party Code) for the boundary-wrapping motivation behind Adapter.
