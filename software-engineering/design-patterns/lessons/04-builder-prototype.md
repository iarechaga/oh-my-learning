---
id: design-patterns/04
subject: design-patterns
title: "Creational: Builder and Prototype"
slug: builder-prototype
status: drafted
mastery:
seniority: mid
source: Design Patterns (Gamma, Helm, Johnson, Vlissides), Chapter 3
prerequisites: [design-patterns/03]
created: 2026-08-10
updated: 2026-08-10
---

# Creational: Builder and Prototype

## TL;DR
Builder separates the *steps* of constructing a complex object from its final *representation*, letting the same construction process produce different results and avoiding constructors with a dozen optional parameters. Prototype creates new objects by cloning an existing, fully-configured instance rather than constructing from scratch, useful when construction is expensive or when the exact class to instantiate isn't known until runtime.

## The idea
Both patterns address problems with plain constructors once object creation gets sufficiently complex or expensive. **Builder** solves the "too many constructor parameters, many of them optional, some combinations invalid" problem by turning construction into a sequence of clear, named steps instead of one overloaded call. **Prototype** solves a different problem: sometimes the cheapest and most flexible way to get a "new" object is to copy an existing one you already have configured correctly, rather than re-running an expensive or complex construction process from zero.

## How it works

### Builder — step-by-step construction, decoupled from the final representation
The classic motivating problem: a class with many optional configuration parameters produces either an unwieldy constructor (`Pizza(size, crust, cheese, pepperoni, mushrooms, olives, extra_sauce, gluten_free, ...)`, most of which are optional and easy to pass in the wrong order) or a proliferation of overloaded constructors for every meaningful combination.

**Worked example — before (telescoping constructor problem):**
```
pizza = Pizza(12, "thin", True, False, True, False, False, False)
# what does the 5th positional argument even mean, without checking the signature?
```
**After (Builder):**
```
class PizzaBuilder:
    def __init__(self): self._pizza = Pizza()
    def size(self, s): self._pizza.size = s; return self
    def crust(self, c): self._pizza.crust = c; return self
    def add_topping(self, t): self._pizza.toppings.append(t); return self
    def build(self): return self._pizza

pizza = (PizzaBuilder()
         .size(12)
         .crust("thin")
         .add_topping("mushrooms")
         .build())
```
Every step is named, self-documenting, and optional steps can simply be omitted rather than requiring a placeholder value in a fixed positional order. The "decoupled from representation" half of Builder's intent goes further still: the *same* sequence of builder calls (or a shared, parameterized construction *process*) can, with a different concrete builder implementation, produce a different final representation entirely — e.g., a `PizzaOrderSummaryBuilder` that takes the same size/crust/topping steps but produces a text receipt instead of a `Pizza` object, reusing the same step-sequencing logic for a genuinely different output.

### Prototype — clone an existing, configured instance
Instead of constructing a new object from scratch (which might be expensive — a database lookup, a network call, complex initialization logic) or requiring the calling code to know the exact concrete class to instantiate, Prototype creates new objects by asking an existing "prototype" instance to `clone()` itself.

**Worked example.** A graphics editor needs to create many similar shapes with slightly varied properties, where each shape type's construction is nontrivial (loading a texture, computing derived geometry):
```
class Shape:
    def clone(self) -> "Shape": raise NotImplementedError

class Circle(Shape):
    def __init__(self, radius, texture):
        self.radius = radius
        self.texture = load_texture(texture)   # expensive to redo from scratch
    def clone(self):
        new_circle = copy.copy(self)            # reuses the already-loaded texture
        return new_circle

template_circle = Circle(radius=10, texture="red_gradient.png")   # expensive, done once
for _ in range(100):
    shape = template_circle.clone()               # cheap, no texture reload
    shape.radius = random.randint(5, 20)
```
Cloning avoids re-running the expensive `load_texture` step 100 times — each clone reuses the already-loaded texture reference, only varying the cheap-to-set properties per instance. Prototype is also useful when the calling code genuinely doesn't know which concrete `Shape` subclass to instantiate (it could be any registered shape type) but *does* have access to an already-instantiated example of the right kind — cloning sidesteps needing to name the concrete class at all, complementary to (and sometimes combined with) Factory Method (`design-patterns/03`) for exactly this "don't know the concrete type" situation.

### Shallow vs. deep cloning — a real, common Prototype pitfall
Cloning is not automatically safe: a naive shallow copy duplicates an object's own fields but leaves any *referenced* mutable objects shared between the original and the clone — mutating a shared referenced list through the clone would silently also affect the "original" prototype. Correct Prototype implementations must deliberately decide, field by field, whether a deep copy is needed for any mutable, reference-type field the clone shouldn't share with its source.

## Pros
- Builder eliminates telescoping-constructor ambiguity and lets construction happen in clear, named, optional steps rather than one overloaded call.
- Builder's separation of construction process from final representation allows genuinely reusing the same step sequence to produce different outputs.
- Prototype avoids re-running expensive construction logic and can create new instances without the calling code needing to know the concrete class.

## Cons
- Builder adds a whole extra class (and often a fluent-interface pattern) for problems that a simple set of well-named optional/keyword arguments (in languages that support them cleanly) might solve with far less ceremony.
- Prototype's shallow-vs-deep-copy pitfall is a genuine, easy-to-get-wrong correctness trap — a naive `clone()` can silently introduce shared-mutable-state bugs (echoing `pragmatic-programmer/11`'s concurrency-adjacent shared-state concerns, here in a single-threaded cloning context).
- Both patterns add indirection that's disproportionate for objects with few, simple, always-required construction parameters.

## Alternatives
- **Named/keyword arguments with sensible defaults** (in languages with strong support for them) — often solves the telescoping-constructor problem Builder addresses with far less structural overhead, when the language makes optional named parameters ergonomic.
- **Data classes / value objects with a validating constructor** — for objects whose "construction" is really just "assemble and validate a fixed set of fields," a well-designed constructor or factory function is simpler than a full Builder.
- **Object pools** — a different technique for the "construction is expensive" problem Prototype partially addresses, reusing existing instances from a pool rather than cloning a template, appropriate when instances are interchangeable and reset-able rather than needing per-instance variation.

## When to use it
Use Builder when a class has many optional parameters, invalid combinations to guard against, or a construction process worth reusing across different output representations. Use Prototype when construction is measurably expensive to repeat, or when the exact concrete class to instantiate isn't known but a suitable existing instance is available to copy.

## When NOT to use it
Don't reach for Builder for objects with few, simple, always-required fields — a plain constructor or a lightweight factory function is clearer. Don't reach for Prototype if construction is cheap and the concrete class is always known — cloning adds shallow/deep-copy correctness risk with no corresponding benefit in that case.

## Key takeaways / mental model
For Builder, ask: "does this object have enough optional, order-independent configuration that a single constructor call would be ambiguous or error-prone?" For Prototype, ask: "is constructing a fresh instance from scratch expensive, or do I not actually know the concrete class but have a working example of the right kind on hand?"

## Self-check questions
1. Rewrite a constructor from your own code that takes several optional parameters using the Builder pattern, and explain what ambiguity the rewrite removes.
2. Explain the shallow-vs-deep-copy pitfall in Prototype using a concrete example of a bug it could cause.
3. Describe a situation where Prototype and Factory Method could be combined, and explain what problem that combination solves that neither pattern alone would.
4. When would introducing a Builder be clearly disproportionate to the problem? Give an example.

## References
- Design Patterns: Elements of Reusable Object-Oriented Software (Gamma, Helm, Johnson, Vlissides), Chapter 3: "Creational Patterns" (Builder and Prototype sections).
