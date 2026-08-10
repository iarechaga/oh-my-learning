---
id: design-patterns/01
subject: design-patterns
title: What Patterns Are; Program to an Interface
slug: what-patterns-are
status: drafted
mastery:
seniority: mid
source: Design Patterns (Gamma, Helm, Johnson, Vlissides), Chapter 1
prerequisites: [clean-code/06]
created: 2026-08-10
updated: 2026-08-10
---

# What Patterns Are; Program to an Interface

## TL;DR
A design pattern is a named, proven solution to a recurring design problem in a specific context — not a piece of code you copy, but a *shape* you adapt. The single principle underlying nearly all 23 patterns is "program to an interface, not an implementation": depend on what an object *can do*, not on its concrete type, so implementations can vary and be swapped without touching the code that uses them.

## The idea
Before this catalog existed, experienced designers were independently arriving at the same handful of good solutions to the same handful of recurring problems, over and over, without a shared vocabulary to name them — meaning every team had to rediscover (or fail to discover) these solutions from scratch, and had no quick way to communicate "use the thing where you swap the algorithm at runtime" except by describing the whole mechanism from first principles each time. The Gang of Four's core contribution was cataloging and *naming* 23 of these recurring solutions, each tied to a specific problem context and a specific set of trade-offs — turning tacit expert knowledge into an explicit, teachable, and — crucially — nameable vocabulary.

A pattern is not the code itself. The book is explicit: a pattern is a *description* of a problem and a solution shape, applicable across many different concrete implementations. Two Strategy-pattern implementations in two different codebases can look completely different in their actual code, while both being unmistakably "the Strategy pattern" because they share the same underlying structural idea (an interchangeable algorithm, selected at runtime, behind a common interface).

## How it works

### Every pattern description follows the same structure
The book documents each pattern using a consistent template, useful to internalize because it's the right *set of questions* to ask about any design decision, pattern or not:
- **Intent** — what problem does this solve, in one or two sentences?
- **Motivation** — a concrete scenario illustrating the problem and why a naive approach falls short.
- **Applicability** — when should you actually reach for this pattern (and, implicitly, when should you not)?
- **Structure** — the class/object relationships, typically shown as a diagram.
- **Consequences** — the trade-offs: what you gain, and what you give up.

Internalizing this template matters more than memorizing any specific pattern's diagram, because it's the discipline this whole subject teaches: for any design choice, ask what problem it solves, when it applies, what it costs.

### "Program to an interface, not an implementation" — the load-bearing principle
Nearly every pattern in the catalog is, at its core, one particular application of this single idea: code that depends on an abstract interface (what an object can *do*) rather than a concrete class (what an object concretely *is*) can have its concrete implementation swapped, extended, or varied without the depending code changing at all. This directly generalizes `clean-code/11`'s dependency-injection discussion and `code-complete/03`'s "identify what varies and encapsulate it" heuristic — patterns are, in large part, a catalog of *specific, well-proven shapes* for doing exactly that in different recurring situations.

**Worked example — the principle in its simplest form:**
```
# Programming to an implementation (rigid)
class OrderProcessor:
    def __init__(self):
        self.notifier = EmailNotifier()   # concrete type baked in
    def complete(self, order):
        self.notifier.send(order.customer, "Order complete")

# Programming to an interface (flexible)
class Notifier:
    def send(self, recipient, message): raise NotImplementedError

class OrderProcessor:
    def __init__(self, notifier: Notifier):   # depends on the interface
        self.notifier = notifier
    def complete(self, order):
        self.notifier.send(order.customer, "Order complete")
```
Nothing here is yet a "named pattern" — it's the raw principle. Nearly every pattern discussed later in this subject (Strategy, Observer, Factory Method, Decorator) is a specific, named refinement of this exact same underlying move, applied to a specific recurring shape of problem (swapping an algorithm, reacting to state changes, deferring which concrete class to instantiate, adding behavior without subclassing).

### Patterns are a shared vocabulary, not a mandate to use them
A common misapplication of this subject: treating "use design patterns" as a goal in itself, forcing a named pattern's structure onto a problem that doesn't actually need that specific flexibility — producing more classes and indirection than the problem warrants (echoing `clean-code/12`'s speculative-generality smell). The book's own framing resists this: patterns exist to be *reached for* when their specific applicability conditions genuinely hold, and to give teams a fast, shared way to communicate a design choice ("this is a Strategy") once it's made — not to be applied reflexively as a badge of sophistication.

### Class-based vs. object-based patterns, and static vs. dynamic structure
The book distinguishes patterns that rely primarily on class *inheritance* (relationships fixed at compile time) from those that rely primarily on object *composition* (relationships that can be reconfigured at runtime) — a distinction that foreshadows `design-patterns/02`'s "composition over inheritance" lesson directly. Many of the catalog's most broadly useful patterns (Strategy, Decorator, Observer) lean on composition specifically because it offers more runtime flexibility than a fixed inheritance hierarchy can.

## Pros
- A shared, named vocabulary dramatically speeds up design communication among engineers who know the catalog — "make this a Strategy" replaces paragraphs of explanation.
- "Program to an interface" as a foundational discipline pays off broadly, independent of whether any specific named pattern is ever explicitly invoked.
- Learning the consistent pattern-description template (intent, applicability, consequences) builds a transferable habit for evaluating *any* design decision, not just the 23 cataloged ones.

## Cons
- Treating pattern *usage* as inherently virtuous, independent of whether the applicability conditions actually hold, produces over-engineered code with unnecessary indirection (the "pattern for pattern's sake" failure mode).
- The vocabulary itself has a real learning-curve cost — a team where only some members know the catalog can talk past each other ("what's a Visitor?") until the vocabulary is genuinely shared.
- Many patterns were cataloged against 1990s-era object-oriented language constraints; some (Iterator, and parts of Singleton and Command) are now partially or fully built into modern languages/standard libraries, making a hand-rolled implementation of the "raw" pattern sometimes redundant.

## Alternatives
- **Ad hoc, un-named design solutions** — arriving at a good design without reference to the catalog; works fine, but loses the fast-communication benefit of a name once the same shape recurs across a team or industry.
- **Functional programming idioms as an alternative vocabulary** — many OO patterns (Strategy, Command, Visitor) have close functional-programming analogues (higher-order functions, first-class functions passed as arguments) that achieve the same flexibility with less structural ceremony in languages that support them well.
- **Architectural-level patterns** (see `architecture/fundamentals`, `software-engineering/enterprise-patterns`) — a different, coarser-grained catalog of named, recurring solutions operating at the system/module level rather than this subject's class/object level.

## When to use it
Reach for "program to an interface" as a default discipline for any dependency you expect might need to vary or be tested independently (echoing `clean-code/11`). Use the specific named patterns from later lessons when their stated applicability conditions genuinely match your problem — not merely because the pattern is well-known or impressive-sounding.

## When NOT to use it
Don't introduce an interface/abstraction for a dependency that will never plausibly vary and costs nothing to depend on concretely — that's ceremony without payoff (echoing `pragmatic-programmer/10`'s configuration-decoupling caution, applied here to interfaces specifically). Don't force a named pattern's specific structure onto a problem just because a name exists for something superficially similar.

## Key takeaways / mental model
Before applying any pattern, ask the book's own five questions about it: what problem does it solve, is my situation actually that problem, what's the structure, and — most importantly — what do I gain and what do I give up by using it here? If you can't answer "what do I give up," you haven't actually evaluated the pattern, you've just recognized its name.

## Self-check questions
1. Explain, in your own words, why "program to an interface, not an implementation" is described as the principle underlying most of the catalog rather than being a pattern itself.
2. Give an example from your own code of "programming to an implementation" that could be refactored to program to an interface instead, and explain what flexibility that would unlock.
3. Describe a situation where applying a named design pattern would be over-engineering. What would a simpler, un-patterned solution look like instead?
4. Why does the book insist a pattern is not the code itself, but a description of a problem/solution shape? What follows from that distinction in practice?

## References
- Design Patterns: Elements of Reusable Object-Oriented Software (Gamma, Helm, Johnson, Vlissides), Chapter 1: "Introduction".
