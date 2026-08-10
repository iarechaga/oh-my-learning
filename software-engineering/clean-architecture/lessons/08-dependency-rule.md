---
id: clean-architecture/08
subject: clean-architecture
title: The Dependency Rule and Clean-Architecture Layers
slug: dependency-rule
status: drafted
mastery:
seniority: senior
source: Clean Architecture (Robert C. Martin), Chapter 22
prerequisites: [clean-architecture/07, clean-architecture/06]
created: 2026-08-10
updated: 2026-08-10
---

# The Dependency Rule and Clean-Architecture Layers

## TL;DR
Source-code dependencies must point only inward, toward higher-level policy — never outward, toward lower-level, more volatile detail. This single rule, applied consistently across Martin's four concentric rings (Entities, Use Cases, Interface Adapters, Frameworks & Drivers), is the entire mechanism that keeps business logic independent of databases, UI frameworks, and external services — everything else in this subject builds toward, or follows from, this one rule.

## The idea
This lesson is the synthesis point of the whole subject: `clean-architecture/03`-`04`'s SOLID principles (especially DIP) and `clean-architecture/05`-`06`'s component principles (especially SDP's "depend toward stability") converge here into one overarching architectural rule, applied at the scale of an entire system's layers. **The Dependency Rule**: source code dependencies can only point inward. Nothing in an inner circle can know anything at all about anything in an outer circle — not the name of a class, not the name of a function, not even that a specific outer-circle concept exists.

## How it works

### The four concentric circles
Martin's specific layering (the number and exact naming can vary by presentation, but the ordering and direction are fixed):
1. **Entities** (innermost) — the general business rules, per `clean-architecture/07`. Depends on nothing else in the system.
2. **Use Cases** — application-specific business rules, per `clean-architecture/07`. Depends only on Entities.
3. **Interface Adapters** — converts data between the format Use Cases/Entities need and the format external agents (a web framework, a database, a UI) need — controllers, presenters, gateways. Depends on Use Cases and Entities.
4. **Frameworks & Drivers** (outermost) — the actual database, the actual web framework, the actual UI toolkit, the actual external services. Depends on Interface Adapters.

The Dependency Rule says: **an arrow of source-code dependency may only point from an outer circle to an inner circle, never the reverse.** Nothing in Entities or Use Cases may `import` or reference anything defined in Interface Adapters or Frameworks & Drivers.

### Crossing the boundary — the mechanism, precisely
The obvious problem this rule creates: at *runtime*, control absolutely must flow outward too — a Use Case needs to save data to a real database, which lives in the outermost circle. How can control flow outward while source-code dependencies point only inward? The answer is exactly `clean-architecture/04`'s DIP mechanism, applied at this larger scale: **define the interface the Use Case needs (e.g., `OrderRepository`) inside the Use Case's own circle, and have the outer-circle's concrete implementation (`PostgresOrderRepository`) implement that inner-circle-owned interface.**

**Worked example, laid out across the circles.**
```
# --- Use Cases circle ---
class OrderRepository:                      # interface, OWNED by this inner circle
    def save(self, order): raise NotImplementedError

class PlaceOrderUseCase:
    def __init__(self, repository: OrderRepository):   # depends only on the interface
        self.repository = repository
    def execute(self, order_data):
        order = Order(order_data)            # Order is an Entity — one circle further in
        self.repository.save(order)          # control flows outward via the interface

# --- Frameworks & Drivers circle ---
class PostgresOrderRepository(OrderRepository):   # implements the inner circle's interface
    def save(self, order):
        db.execute("INSERT INTO orders ...", order.to_row())
```
The *source-code* dependency (`PostgresOrderRepository` imports and implements `OrderRepository`) points inward, exactly satisfying the Dependency Rule. The *runtime control flow* (`PlaceOrderUseCase.execute()` eventually causing a real database `INSERT`) flows outward, exactly as it must. This is the precise resolution to the apparent contradiction — dependency direction and control-flow direction are allowed to differ, and the whole architecture is built specifically to exploit that difference.

### Crossing the boundary with data — plain, simple structures, not domain objects leaking outward
When data needs to cross a circle boundary (a Use Case's result needs to reach a web controller in the Interface Adapters circle, to eventually be serialized into an HTTP response), the data should cross as a **simple data structure** (a plain DTO, per `clean-code/06`'s data-structure style) — never as an Entity or a database-specific object. Passing a full `Order` Entity outward to a web controller would let the controller (an outer-circle concept) start depending on the Entity's internal structure, and worse, risks the Entity accidentally acquiring dependencies on outer-circle concerns (a serialization annotation, an ORM decorator) to make that crossing convenient — precisely the kind of boundary violation this whole rule exists to prevent.

### Why this rule is worth its structural cost
Directly connecting back to `clean-architecture/01`'s framing of architecture's purpose: this rule is what makes a database swap, a UI framework migration, or a new delivery mechanism (adding a CLI alongside an existing web app) a change confined entirely to the outer circles — the Entities and Use Cases, where the actual, valuable business logic lives, never need to change or even be recompiled/redeployed for any of those technical changes. This is architecture's core value proposition (minimizing effort to build and maintain, per `clean-architecture/01`) made concrete and mechanical, rather than aspirational.

## Pros
- Makes business logic (Entities, Use Cases) genuinely testable without any database, network connection, or UI framework running — dramatically faster and more reliable tests (`clean-code/09`'s F.I.R.S.T. properties).
- Confines the cost of swapping a technical detail (database, framework, external service) to the outer circles, leaving the valuable business logic entirely untouched.
- Gives a single, consistent, checkable rule ("does this inner-circle file import anything from an outer circle?") that unifies and operationalizes everything else in this subject.

## Cons
- Consistently applying the rule requires real, ongoing discipline — a "quick," rule-violating shortcut (a Use Case directly importing an ORM model "just this once") is often the path of least resistance under deadline pressure, and each violation quietly erodes the architecture's actual guarantees.
- The interface-crossing mechanism (defining an interface in the inner circle, implemented outward) adds genuine structural overhead — more files, more indirection — that's disproportionate for genuinely small applications with little enduring business logic to protect.
- Passing only plain data structures across boundaries sometimes requires extra mapping/translation code (converting between an Entity and a DTO) that can feel like needless duplication for simple cases, even though it's precisely what prevents the boundary violation this rule exists to guard against.

## Alternatives
- **A simpler layered architecture without strict inward-only enforcement** (see `architecture/fundamentals`) — a lighter-weight, less strictly-enforced version of the same layering idea, appropriate when the full rigor of Clean Architecture's boundary-crossing mechanism isn't justified by the system's actual complexity or expected lifespan.
- **Hexagonal Architecture / Ports and Adapters** — a closely related, largely equivalent architectural style (often considered essentially the same underlying idea presented differently), using "ports" (interfaces) and "adapters" (implementations) terminology instead of concentric circles.
- **A framework-coupled "quick and dirty" architecture** — accepting business logic tightly coupled to a specific framework/database for a genuinely small, short-lived, or throwaway application (`pragmatic-programmer/06`) where the Dependency Rule's long-term payoff would never materialize.

## When to use it
Apply the Dependency Rule rigorously for any system expected to have a real lifespan, meaningful business logic complexity, or a credible chance of needing to swap a technical detail (database, framework, delivery mechanism) over its life.

## When NOT to use it
Don't impose the full four-circle structure and strict boundary-crossing discipline on a genuinely small, short-lived application with thin business logic and no credible need to ever swap its technical details — the structural cost isn't justified there, echoing `clean-architecture/01`'s own "architecture is a trade-off, not something to maximize unconditionally" caution.

## Key takeaways / mental model
For any file, ask: "does this import or reference anything from a circle further out than itself?" If yes, and the file is meant to live in an inner circle, that's a Dependency Rule violation — fix it by introducing an inner-circle-owned interface the outer-circle code implements, exactly as `clean-architecture/04`'s DIP prescribes, now applied at the whole-system scale.

## Self-check questions
1. Using the `PlaceOrderUseCase`/`PostgresOrderRepository` example, explain precisely how the source-code dependency and the runtime control flow point in opposite directions, and why that's not a contradiction.
2. Why should data crossing a circle boundary be a plain data structure rather than a full Entity object? What specific risk does passing an Entity outward create?
3. Describe a rule-violating shortcut you've seen (or could imagine) — a Use Case or Entity directly depending on an outer-circle concept "just this once." What was, or would be, the eventual cost?
4. For a genuinely small application, explain why imposing the full four-circle structure might be a poor trade-off, using `clean-architecture/01`'s "architecture is a trade-off" framing.

## References
- Clean Architecture: A Craftsman's Guide to Software Structure and Design (Robert C. Martin), Chapter 22: "The Clean Architecture".
