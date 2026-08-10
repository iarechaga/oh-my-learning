# Design Patterns - Subject Summary

A comprehensive recap of *Design Patterns: Elements of Reusable Object-Oriented
Software* (the "Gang of Four"), concept by concept.

**Progress note:** all 11 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
foundational principles first, then creational, structural, and behavioral patterns.

## Foundational principles

- **[design-patterns/01] What patterns are; program to an interface** - a pattern is a
  named problem/solution shape, not code to copy; "program to an interface, not an
  implementation" underlies nearly the whole catalog.
  ([lesson](lessons/01-what-patterns-are.md))
- **[design-patterns/02] Composition over inheritance** - inheritance couples a
  subclass to its parent's implementation (the fragile base class problem); composition
  achieves reuse through a stable interface and supports runtime flexibility.
  ([lesson](lessons/02-composition-over-inheritance.md))

## Creational patterns

- **[design-patterns/03] Factory Method and Abstract Factory** - defer which concrete
  class to instantiate to a subclass (Factory Method) or guarantee a consistent family
  of related objects (Abstract Factory). ([lesson](lessons/03-factory-patterns.md))
- **[design-patterns/04] Builder and Prototype** - Builder replaces telescoping
  constructors with named steps; Prototype creates new objects by cloning a configured
  instance instead of constructing from scratch. ([lesson](lessons/04-builder-prototype.md))
- **[design-patterns/05] Singleton (and its problems)** - guarantees exactly one
  instance, but its usual global-access mechanism reintroduces hidden coupling and
  breaks testability; prefer dependency-injecting a single constructed instance.
  ([lesson](lessons/05-singleton.md))

## Structural patterns

- **[design-patterns/06] Adapter, Bridge, Composite** - Adapter translates an
  incompatible interface; Bridge splits two independent dimensions of variation to
  avoid a subclass explosion; Composite lets clients treat one object and a tree of
  objects uniformly. ([lesson](lessons/06-adapter-bridge-composite.md))
- **[design-patterns/07] Decorator, Facade, Proxy** - Decorator adds behavior at
  runtime without subclassing; Facade simplifies a complex subsystem; Proxy controls
  access to an object transparently (lazy loading, permissions, remote calls, caching).
  ([lesson](lessons/07-decorator-facade-proxy.md))
- **[design-patterns/08] Flyweight** - shares immutable, common ("intrinsic") state
  across many objects to cut memory use when object count is a measured bottleneck.
  ([lesson](lessons/08-flyweight.md))

## Behavioral patterns

- **[design-patterns/09] Strategy, Template Method, Observer** - Strategy swaps a whole
  algorithm via composition; Template Method fixes a process's skeleton via
  inheritance; Observer notifies decoupled, unknown-in-advance listeners of state
  changes. ([lesson](lessons/09-strategy-template-observer.md))
- **[design-patterns/10] Command, State, Chain of Responsibility** - Command reifies an
  action as an object (enabling undo/queuing/logging); State replaces mode-checking
  conditionals with polymorphism; Chain of Responsibility passes a request along
  handlers until one processes it. ([lesson](lessons/10-command-state-chain.md))
- **[design-patterns/11] Iterator, Mediator, Visitor, and the rest** - Iterator hides
  traversal internals (now mostly built into languages); Mediator centralizes
  many-to-many coordination; Visitor adds new operations to a stable structure without
  modifying it. ([lesson](lessons/11-iterator-mediator-visitor.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
