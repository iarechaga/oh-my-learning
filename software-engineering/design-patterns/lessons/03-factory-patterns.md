---
id: design-patterns/03
subject: design-patterns
title: "Creational: Factory Method and Abstract Factory"
slug: factory-patterns
status: drafted
mastery:
seniority: mid
source: Design Patterns (Gamma, Helm, Johnson, Vlissides), Chapter 3
prerequisites: [design-patterns/01, clean-code/11]
created: 2026-08-10
updated: 2026-08-10
---

# Creational: Factory Method and Abstract Factory

## TL;DR
Factory Method lets a subclass decide which concrete class to instantiate, without the base class needing to name it; Abstract Factory groups several related Factory Methods behind one interface so a caller can create a whole *family* of consistent, related objects without knowing their concrete types. Both push the "which concrete class" decision to a boundary, exactly as `clean-code/11` recommends.

## The idea
`clean-code/11` established that construction (deciding which concrete class to instantiate) and use (calling methods on that object) are different concerns that should be kept apart. The two Factory patterns are named, specific shapes for doing that decoupling in two common recurring situations: **Factory Method** handles "I need to create one thing, but which specific kind depends on context I don't want to hardcode here"; **Abstract Factory** handles "I need to create several *related* things that must be consistent with each other (all from the same 'family'), without the calling code knowing which family it's using."

## How it works

### Factory Method — defer instantiation to a subclass
Instead of a class directly instantiating a concrete type it needs, it calls an overridable "factory method" whose job is exactly that one decision — and a subclass overrides that method to supply a different concrete type, without changing anything else about the base class's logic.

**Worked example.** A `ReportGenerator` base class needs to create an `Exporter` but shouldn't hardcode which kind:
```
class ReportGenerator:
    def create_exporter(self) -> Exporter:      # the factory method
        raise NotImplementedError
    def generate(self, report):
        exporter = self.create_exporter()        # use, not construction
        exporter.export(report)

class PdfReportGenerator(ReportGenerator):
    def create_exporter(self) -> Exporter:
        return PdfExporter()

class CsvReportGenerator(ReportGenerator):
    def create_exporter(self) -> Exporter:
        return CsvExporter()
```
`generate()` never knows or cares whether it's dealing with a PDF or CSV exporter — the decision is isolated entirely to `create_exporter()`, overridden per subclass. Adding a new export format means adding a new subclass, touching nothing in `generate()` — directly the "easy to add new types" trade-off from `clean-code/06`'s object-style discussion.

### Abstract Factory — create a consistent family of related objects
When several related objects must be created *together*, consistently — using the wrong combination would be a bug — Abstract Factory groups their creation behind one interface with one method per product in the family, so a caller gets a matched, internally-consistent set without knowing which concrete family it's actually using.

**Worked example.** A UI toolkit that must render consistently either as "Light theme" or "Dark theme" widgets — mixing a light-theme button with a dark-theme checkbox would look broken:
```
class WidgetFactory:
    def create_button(self) -> Button: raise NotImplementedError
    def create_checkbox(self) -> Checkbox: raise NotImplementedError

class LightThemeFactory(WidgetFactory):
    def create_button(self): return LightButton()
    def create_checkbox(self): return LightCheckbox()

class DarkThemeFactory(WidgetFactory):
    def create_button(self): return DarkButton()
    def create_checkbox(self): return DarkCheckbox()

def render_form(factory: WidgetFactory):
    button = factory.create_button()
    checkbox = factory.create_checkbox()
    # guaranteed to be from the SAME theme — factory enforces the consistency
```
`render_form` receives one factory and gets a guaranteed-matching button and checkbox — the caller cannot accidentally mix a light button with a dark checkbox, because whichever concrete factory is passed in produces only its own family's consistent set. Compare with the alternative of passing theme as a loose parameter to each widget's constructor separately: nothing would prevent an inconsistent combination there, whereas Abstract Factory makes the consistency structurally guaranteed.

### The relationship between the two
Abstract Factory is often *implemented using* several Factory Methods internally (each `create_X` method in the abstract factory is itself a Factory Method) — they're not competing alternatives so much as one pattern (Abstract Factory) frequently built by composing several instances of the other (Factory Method) to solve the larger "consistent family" problem, on top of the smaller "one polymorphic creation decision" problem.

## Pros
- Both patterns isolate "which concrete class" decisions from the code that uses the result, directly supporting `clean-code/11`'s testability and flexibility goals.
- Abstract Factory structurally guarantees consistency across a family of related objects, preventing an entire class of "mismatched combination" bugs by construction.
- Adding a new product variant (a new export format, a new UI theme) requires adding a new factory/subclass, not modifying existing client code — the Open/Closed Principle in action (see `software-engineering/clean-architecture`).

## Cons
- Both patterns add real structural indirection (extra classes and interfaces) that's disproportionate for a simple, single, rarely-varying construction decision — a plain constructor call is often genuinely sufficient.
- Abstract Factory specifically requires anticipating and defining the full family of related products upfront; adding a genuinely new *kind* of product to an existing family (not just a new variant of existing products) requires changing the abstract factory interface itself, touching every concrete factory.
- Deep factory hierarchies (factories that create factories) can become their own source of the "how do I trace what actually gets constructed" confusion this whole family of patterns is meant to prevent, if overused.

## Alternatives
- **A simple parameterized function/dictionary-based factory** — `create_exporter(format: str) -> Exporter` using a dictionary or `if`/`elif` dispatch — often sufficient when the decision doesn't need to vary per-subclass or maintain family consistency, avoiding the class-hierarchy overhead of formal Factory Method.
- **Dependency injection frameworks** (see `clean-code/11`) — for larger systems, a DI container's configuration can play a similar role to a factory, deciding which concrete implementation to wire in, often with less hand-written boilerplate than an explicit Factory Method hierarchy.
- **Builder pattern** (`design-patterns/04`) — addresses a related but distinct problem (constructing one complex object step by step) rather than choosing among several interchangeable concrete types.

## When to use it
Use Factory Method when a class needs to create an object but the exact concrete type should be decided by a subclass or a configuration point, especially when you expect new types to be added over time. Use Abstract Factory specifically when several related objects must be created together and their consistency as a *family* is a genuine correctness requirement, not just a convenience.

## When NOT to use it
Don't reach for either pattern when there's only ever one concrete type in practice, with no genuine expectation of variation — a plain constructor call is clearer and has zero indirection cost. Don't use Abstract Factory if the "family" framing is artificial — if the related objects don't actually need to vary together consistently, a set of independent Factory Methods (or even plain constructors) is simpler.

## Key takeaways / mental model
Ask: "am I choosing one concrete type (Factory Method), or a whole matched set of several related concrete types that must stay consistent with each other (Abstract Factory)?" Either way, the goal is the same as `clean-code/11`'s: isolate the decision from the code that uses the result.

## Self-check questions
1. Using the report-exporter example, explain what changes (and where) when a new export format is added, under the Factory Method design versus a hardcoded `if format == "pdf"` approach.
2. Why does Abstract Factory prevent a "mismatched combination" bug that a set of independent constructors/factories wouldn't prevent?
3. Give an example from your own domain where a family of related objects genuinely needs to stay consistent (a theme, a region-specific rule set, a database-vendor-specific set of drivers).
4. Describe a situation where using Factory Method or Abstract Factory would be over-engineering relative to a simpler alternative.

## References
- Design Patterns: Elements of Reusable Object-Oriented Software (Gamma, Helm, Johnson, Vlissides), Chapter 3: "Creational Patterns" (Abstract Factory and Factory Method sections).
