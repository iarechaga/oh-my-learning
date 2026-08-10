---
id: ddd-evans/07
subject: ddd-evans
title: Modules as conceptual boundaries
slug: modules-as-conceptual-boundaries
status: drafted
mastery:
seniority: mid
source: Domain-Driven Design (Eric Evans), Part II, Chapter 5
prerequisites: [ddd-evans/02]
created: 2026-08-10
updated: 2026-08-10
---

# Modules as conceptual boundaries

## TL;DR
Modules (packages, namespaces) are not just a mechanism for avoiding naming collisions or organizing files by technical type — they should express real conceptual divisions in the domain model itself, chosen for low coupling between modules and high cohesion within them, and named with the same ubiquitous language (`ddd-evans/01`) as everything else.

## The idea
It's tempting to organize code by technical role — a `controllers` folder, a `models` folder, a `services` folder — because that's what most framework tutorials teach by default. Evans argues this is close to the worst possible organizing principle for a nontrivial domain, because it groups things that change for entirely unrelated reasons (every controller together, regardless of what business area it serves) and scatters things that belong together (the `Order` model, `OrderService`, and `OrderController` end up in three different, distant folders instead of being visibly related).

The alternative: organize modules around domain concepts, the same way you'd organize a conversation with a domain expert into topics. A `shipping` module, a `billing` module, a `catalog` module — each one is a cohesive slice of the domain, and the module boundary itself becomes a meaningful piece of the model, not just a filesystem convenience. Splitting or merging modules is itself a modeling decision, revisited as understanding of the domain deepens, exactly like renaming a class or introducing a new concept from the ubiquitous language.

## How it works

### Organize by domain concept, not technical layer
**Before — technical/layer-based organization:**
```
/controllers
    OrderController.py
    ShipmentController.py
    InvoiceController.py
/services
    OrderService.py
    ShipmentService.py
    InvoiceService.py
/models
    Order.py
    Shipment.py
    Invoice.py
```
To understand everything about how shipping works, a developer has to open three unrelated top-level folders and hunt through each for the shipping-related file. The folder structure tells you nothing about the domain — it only tells you about implementation mechanics (which the layered architecture from `ddd-evans/03` already governs at a finer grain within each module anyway).

**After — domain-concept-based organization:**
```
/ordering
    Order.py
    OrderController.py
    OrderApplicationService.py
/shipping
    Shipment.py
    ShipmentController.py
    ShippingService.py
/billing
    Invoice.py
    InvoiceController.py
    BillingService.py
```
Now the module boundary *is* domain information: everything related to shipping lives together, and a developer working on a shipping feature has one place to look. The layered structure (`ddd-evans/03`) still applies — there can be sub-namespaces or naming conventions distinguishing domain code from application code within `shipping` — but the top-level organizing principle is the domain, not the technical role.

### Low coupling, high cohesion — chosen deliberately, not accidentally
Two rules govern good module boundaries:
- **High cohesion within a module**: the classes inside `shipping` should have a strong conceptual and functional relationship — if you can't explain why two classes are in the same module beyond "they seemed related," that's a signal the module's concept is too vague.
- **Low coupling between modules**: `shipping` should depend on `ordering` only through a narrow, deliberate interface (perhaps just needing to know an `OrderId` and a `ShippingAddress`), not by reaching deep into `ordering`'s internals. A module with many bidirectional dependencies on many other modules has, in effect, no real boundary at all — everything is secretly one big tangled module wearing separate folder names.

### Worked example: a module boundary that reveals a missing concept
A team had a single `orders` module that had grown to include everything about order creation, payment processing, and fulfillment tracking. As it grew, changes to payment logic kept requiring changes to fulfillment code and vice versa, and nobody could explain *why* those two things were coupled — they just always happened to change together because they lived in the same sprawling module. Splitting `orders` into `ordering`, `payments`, and `fulfillment` — driven by asking "what would a domain expert call each of these responsibilities?" — didn't just reorganize files; it forced the team to define an explicit, narrow interface between the new modules (an `OrderId` and a small set of domain events like `PaymentCaptured`), which in turn surfaced that "payment" and "fulfillment" genuinely operate on different timelines and should never have been tightly coupled in the first place. This is knowledge crunching (`ddd-evans/01`) happening through refactoring, not just through conversation — restructuring modules is itself a way of testing and sharpening the model.

### Module names are part of the ubiquitous language
Just as class and method names must match the domain vocabulary, module names should too. A module called `misc` or `common` or `utils` is a confession that no real domain concept was identified — it's a place things get dumped because nobody took the time to name what they actually are. Over time these grow unboundedly and become high-coupling hotspots because everything ends up depending on the miscellaneous grab-bag.

## Pros
- Module structure becomes a map of the domain itself, readable by both developers and (at a coarse level) domain experts, rather than an arbitrary technical artifact.
- High cohesion / low coupling boundaries make it dramatically easier to reason about the blast radius of a change — "if I change something in `shipping`, what else might break?" has a much smaller, more honest answer.
- Provides a natural seam for splitting a monolith into services later (each well-bounded module is a strong candidate for extraction) without a from-scratch redesign.

## Cons
- Getting module boundaries right requires real domain understanding upfront (or willingness to refactor boundaries repeatedly as understanding deepens) — a premature, wrong boundary can be as costly to live with as no boundary at all.
- Teams used to technical-layer organization (very common, especially with framework-generated scaffolding) face real friction and tooling mismatch adopting domain-based modules.
- Overly fine-grained modules (one module per tiny concept) can create excessive ceremony and cross-module wiring for genuinely small domains.

## Alternatives
- **Technical-layer organization** (`controllers`/`services`/`models`) — simpler to set up, matches most framework defaults and tutorials, but scatters related domain logic and provides no real coupling/cohesion discipline, as this lesson describes.
- **Feature-folder / vertical-slice architecture** — a modern relative of this same idea, common in web frameworks, organizing by user-facing feature rather than strictly by domain concept; often very similar in practice, sometimes finer-grained.
- **Bounded contexts as physical service boundaries** (`ddd-evans/14`) — the strategic-design escalation of this same idea: once a module boundary also implies a distinct ubiquitous language and team ownership, it may deserve to become a separate deployable service, not just a code module within one codebase.

## When to use it
Apply domain-concept-based module boundaries in any codebase big enough that "where do I find the code for X" is a real, recurring question — which is most systems past a small prototype.

## When NOT to use it
For a genuinely small codebase (a handful of files, one clear domain concern), imposing multiple domain modules is premature structure with no payoff; a flat organization is fine until the code actually grows enough to need boundaries.

## Key takeaways / mental model
A good module answers "what business concept lives here?" in one phrase a domain expert would recognize; a bad module answers "what kind of file is this?" Choose boundaries the same way you choose vocabulary — by asking what the domain actually distinguishes, not by copying a framework's default folder names.

## Self-check questions
1. Take a codebase you know and identify one module boundary organized by technical layer rather than domain concept. What would a domain-concept reorganization look like?
2. In the orders-splitting example, what specific symptom (repeated unrelated changes happening together) signaled that the module boundary was wrong?
3. Why is a module named `utils` or `common` treated as a warning sign rather than a neutral, harmless convenience?
4. Explain the relationship between a module (this lesson) and a bounded context (`ddd-evans/14`). When does a module boundary deserve to become a bounded-context boundary?

## References
- Domain-Driven Design: Tackling Complexity in the Heart of Software (Eric Evans), Chapter 5: "A Model Expressed in Software" (Modules section).
