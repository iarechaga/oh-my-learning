---
id: pragmatic-programmer/04
subject: pragmatic-programmer
title: Orthogonality and Decoupling
slug: orthogonality
status: drafted
mastery:
seniority: mid
source: The Pragmatic Programmer (20th Anniversary ed., Hunt & Thomas), Chapter 2
prerequisites: [pragmatic-programmer/03]
created: 2026-08-10
updated: 2026-08-10
---

# Orthogonality and Decoupling

## TL;DR
Two components are orthogonal if a change to one has no effect on the other. Designing for orthogonality — independent, self-contained modules with no hidden dependencies — makes systems easier to change, test, and reason about, because the blast radius of any single change stays small and predictable.

## The idea
The term comes from geometry: two axes are orthogonal when they're at right angles, meaning movement along one produces zero movement along the other. The book borrows this as a design goal: **can you change component A without needing to think about, or accidentally breaking, component B?**

Non-orthogonal (tangled) systems have a specific, painful symptom: small changes have unpredictable, far-reaching effects. You fix a display bug in the UI and the database layer starts throwing errors. You change a logging format and authentication breaks. This isn't a coincidence or bad luck — it's the direct, measurable cost of components that secretly depend on each other's internals rather than communicating through narrow, well-defined interfaces.

## How it works

### The car analogy
The book's illustrative example: a car's radio and steering are orthogonal — turning the wheel doesn't change the station, and changing the station doesn't affect steering. Now imagine a poorly engineered car where turning the steering wheel *also* slightly changes the radio volume because the wires happen to run near each other and interfere. That's a non-orthogonal design: an accidental coupling between systems that have no business affecting each other.

### Where hidden coupling comes from in software
1. **Shared mutable state** — two modules both read and write the same global variable or shared object; changing how one module uses that state can silently break the other's assumptions.
2. **Leaky abstractions** — a module exposes its internal representation instead of a stable interface, so callers start depending on implementation details that were never meant to be a contract.
3. **Implicit ordering dependencies** — module B only works correctly if module A ran first and left something in a particular state, with no explicit enforcement of that order.
4. **Duplicated knowledge** (see Lesson 03) — when the same fact lives in two places, changing one without the other is a coupling failure even though there's no direct code reference between them.

### Worked example: detecting non-orthogonality with a simple test
The book proposes a practical test: **when you're about to make a change, ask how many modules will be affected.** If the answer is consistently "just this one," the design is orthogonal. If small changes routinely ripple across the codebase, that's a measurable orthogonality problem, not bad luck.

Concretely: a team estimates a "change the currency displayed on invoices from USD to a configurable currency" ticket. If the estimate comes back as "update the invoice template" (1 file), the display layer is well-decoupled from formatting rules. If the estimate comes back as "update the invoice template, the PDF export, the email template, the analytics dashboard, and the tax calculator because they all independently hardcode `$`," that's four hidden couplings to the same underlying fact (currency symbol), discovered only because a change forced them into the light.

### Design techniques that produce orthogonality
- **Encapsulation / narrow interfaces**: expose only what's needed; hide internal representation so callers can't accidentally couple to it.
- **Dependency injection over hardcoded references**: a module that receives its collaborators as parameters (rather than reaching out and constructing/locating them itself) can be swapped or tested independently.
- **Avoid global state**: prefer passing explicit state through function calls/constructors over shared mutable globals that create invisible cross-module wiring.
- **Single responsibility per module**: a module that does one thing has, by construction, fewer reasons to change and fewer things other modules could accidentally depend on.

### The testing payoff
Orthogonal modules are independently testable: you can unit-test module A with mocked collaborators, because A's contract with the rest of the world is explicit and narrow. A tangled module resists unit testing — you end up needing most of the system running just to exercise one function, because that function secretly depends on global state, ambient configuration, or side effects from other modules.

## Pros
- Localizes the blast radius of changes, making estimates more reliable and bugs easier to isolate.
- Enables independent testing, development, and even independent team ownership of different modules.
- Makes the system easier to reason about: you can understand module A in isolation without loading the whole system into your head.

## Cons
- Achieving true orthogonality has real design cost — narrow interfaces and dependency injection take more upfront thought than reaching for a shared global.
- Over-applying orthogonality (forcing independence between things that are genuinely, deeply related) can produce excessive indirection and boilerplate for no real benefit.
- Some domains have genuine cross-cutting concerns (logging, auth, transactions) that resist clean orthogonal decomposition and require deliberate patterns (middleware, aspects) rather than a simple "just decouple it" fix.

## Alternatives
- **Tight coupling by design (monolithic modules)** — acceptable and sometimes faster for small, short-lived systems where the coordination cost of formal boundaries outweighs the flexibility benefit.
- **Layered architecture** — a coarser-grained way to bound coupling (each layer depends only on the layer below), trading some of orthogonality's independence for a simpler, well-understood structure.
- **Microservices** — push orthogonality to the extreme by giving each concern its own deployable, independently-scalable process; solves coupling at the cost of operational complexity (see the `architecture` domain's Hard Parts and Building Microservices subjects).

## When to use it
Apply orthogonality thinking whenever you're deciding how two pieces of functionality should communicate — prefer explicit, narrow interfaces over shared state or implicit ordering. It's especially valuable in code you expect to change frequently or that multiple people/teams will touch.

## When NOT to use it
Don't invest heavily in decoupling code that is genuinely one cohesive concept just to satisfy an abstract "everything should be orthogonal" rule — some things really do belong together, and artificially separating them (e.g., splitting a tiny, stable value object into three "orthogonal" pieces) adds indirection without reducing real coupling.

## Key takeaways / mental model
Before changing something, ask: "if I change this, what else, if anything, breaks or needs to change?" A short, predictable answer means good orthogonality. A long, surprising answer is a design smell worth fixing — usually by finding and naming the hidden shared knowledge or state causing it.

## Self-check questions
1. Using the car-radio analogy, describe a real coupling bug you've seen where changing one thing unexpectedly affected something "unrelated."
2. What's the concrete difference between shared mutable state and duplicated knowledge as sources of non-orthogonality?
3. Why does orthogonality make unit testing easier, specifically?
4. Give an example of over-applying orthogonality — decoupling two things that should have stayed together — and explain the cost that decision introduced.

## References
- The Pragmatic Programmer, 20th Anniversary Edition (David Thomas & Andrew Hunt), Chapter 2: "A Pragmatic Approach" (Orthogonality section).
