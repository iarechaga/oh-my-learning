---
id: enterprise-patterns/03
subject: enterprise-patterns
title: Table Module and Service Layer
slug: table-module-service-layer
status: drafted
mastery:
seniority: senior
source: Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 9
prerequisites: [enterprise-patterns/02]
created: 2026-08-10
updated: 2026-08-10
---

# Table Module and Service Layer

## TL;DR
Table Module organizes domain logic around a database *table*, with one class handling all rows of that table at once — a middle ground between Transaction Script and Domain Model, well-suited to tools (like many reporting/data-binding frameworks) that naturally think in terms of whole tables/result sets rather than individual objects. Service Layer sits in front of whichever domain-logic pattern you chose (Transaction Script, Domain Model, or Table Module), defining the application's actual operations as a clean, coarse-grained API for Presentation-layer clients to call.

## The idea
`enterprise-patterns/02` presented Transaction Script and Domain Model as the two primary poles; this lesson covers two more specific, narrower patterns that address particular situations those two poles don't handle ideally: Table Module for when your data-access technology and domain shape are already fundamentally table-oriented, and Service Layer for defining a clean boundary regardless of which underlying domain-logic pattern you're using.

## How it works

### Table Module — one class per table, not per row
Unlike Domain Model (where you'd typically have one `Customer` *instance* per customer row), Table Module has a single `CustomerTableModule` *class* whose methods operate on a whole result set (potentially many rows) at once, typically accepting and returning a table-like data structure (a `DataTable`, a result set, a DataFrame-like structure) rather than individual domain objects.

**Worked example.**
```
class CustomerTableModule:
    def __init__(self, dataset):        # dataset holds ALL customer rows currently loaded
        self.dataset = dataset
    def discount_rate_for(self, customer_id):
        row = self.dataset.find_row("customers", id=customer_id)
        return 0.1 if row["is_vip"] else 0
    def apply_discounts(self):           # operates across MANY rows at once
        for row in self.dataset.rows("customers"):
            row["discounted_total"] = row["total"] * (1 - self.discount_rate_for(row["id"]))
```
This pattern fits especially well when the underlying data-access technology (many reporting tools, some older .NET/ADO-style data-binding frameworks, or a system heavily oriented around returning and manipulating whole SQL result sets) already hands you a table-shaped structure — Table Module lets business logic sit right alongside that structure without needing to first convert it into a full network of individual domain objects (Domain Model) or scatter logic across many independent transaction procedures (Transaction Script).

**The trade-off versus Domain Model.** Table Module doesn't capture rich relationships between individual records as naturally as Domain Model's object network does (there's no natural `customer.orders` navigable reference — you'd query the orders table again) — it's a genuine middle ground, offering some of Domain Model's logic-centralization benefit (discount logic lives in one place, `CustomerTableModule`, not scattered across transactions) without Domain Model's full object-relational mapping complexity, because it deliberately doesn't try to build a rich, individually-instantiated object graph at all.

### Service Layer — a clean, coarse-grained boundary in front of the domain
Regardless of which domain-logic pattern is used underneath, Fowler recommends defining a **Service Layer**: a set of coarse-grained, use-case-shaped operations that Presentation-layer clients call, hiding the domain's internal structure (whether that's Transaction Script procedures, a Domain Model's fine-grained object interactions, or Table Module's table operations) behind a stable, purpose-built API — directly echoing `clean-architecture/07`'s Use Cases, and a direct historical ancestor of that concept, from an earlier book.

**Worked example.**
```
class OrderService:                              # Service Layer — coarse-grained, use-case-shaped
    def __init__(self, order_repository, customer_repository):
        self.order_repository = order_repository
        self.customer_repository = customer_repository
    def place_order(self, customer_id, items):    # ONE coarse-grained call for the whole use case
        customer = self.customer_repository.find(customer_id)
        order = Order(customer, items)              # underneath, could be Domain Model, Table Module, etc.
        order.place()
        self.order_repository.save(order)
        return order.final_total()
```
A web controller (or a mobile app's API client, or a batch job) calls `OrderService.place_order()` once, with simple, serializable arguments, and gets back a simple result — it never needs to know whether the actual business logic underneath is implemented via rich Domain Model objects, Table Module operations, or Transaction Script procedures. This is especially valuable when the Presentation layer might be **remote** (a separate process, a separate machine) from the domain logic — Service Layer's coarse-grained methods minimize the number of round trips needed, directly connecting to `enterprise-patterns/14`'s later treatment of distribution and the Remote Facade pattern.

### Why Service Layer matters even when everything runs in one process
Even without remote calls, Service Layer provides real value: it gives Presentation-layer code one clean, stable, well-tested entry point per use case, rather than requiring Presentation code to orchestrate several fine-grained domain-object interactions itself (which would couple Presentation code to the domain's internal structure, echoing `clean-architecture/09`'s general boundary-drawing logic). It's also the natural place to put cross-cutting technical concerns for a given use case — starting a database transaction, checking authorization, logging — without scattering that concern across every fine-grained domain call, or leaking it into Presentation code.

## Pros
- Table Module fits naturally with table/result-set-oriented data-access technology, avoiding unnecessary conversion into a full object graph when that graph's relational benefits aren't actually needed.
- Service Layer gives Presentation-layer clients one clean, coarse-grained, well-tested entry point per use case, regardless of the domain-logic pattern used underneath.
- Service Layer minimizes round trips for remote clients and provides a natural home for cross-cutting, per-use-case technical concerns (transactions, authorization, logging).

## Cons
- Table Module's lack of a rich, per-record object graph means relationship-heavy business logic (traversing many linked records with complex interactions) is often more awkward to express than in a true Domain Model.
- Service Layer, if its methods become too fine-grained (essentially mirroring domain objects' individual methods one-to-one) or too coarse-grained (one giant "do everything" method per use case), loses much of its value — getting the granularity right takes real design judgment.
- Adding a Service Layer to a genuinely simple application, with few real use cases and no remote clients, can be unnecessary structural overhead relative to calling the domain layer's Transaction Script procedures directly.

## Alternatives
- **Domain Model with no Table Module** — the more common, richer choice for a domain complex enough to benefit from individual object relationships, at the cost of Table Module's simpler fit with table-oriented data tooling.
- **Direct Presentation-to-domain calls, no Service Layer** — a leaner alternative for genuinely small applications with a single, local Presentation layer and no remote clients, where Service Layer's coarse-grained boundary adds little value beyond what direct calls already provide.
- **Use Cases as a more formalized descendant** (`clean-architecture/07`) — a later, more rigorously specified evolution of essentially the same Service Layer idea, with a more explicit and stricter dependency-direction discipline.

## When to use it
Use Table Module when your data-access technology is fundamentally table/result-set-oriented and the domain doesn't need Domain Model's rich, per-record relationship navigation. Use Service Layer whenever a Presentation layer (especially a remote one, or one you expect to have multiple clients) needs a clean, stable, use-case-shaped API in front of the domain logic.

## When NOT to use it
Don't use Table Module for a domain whose business logic is genuinely relationship-heavy and would benefit substantially from Domain Model's individually-instantiated, richly-linked objects. Don't add a Service Layer to a genuinely small, single-client, local-only application where it would just be an extra layer of indirection with no real coarse-graining or cross-cutting-concern benefit.

## Key takeaways / mental model
Choose Table Module specifically when your data naturally arrives and is manipulated as whole tables/result sets, not individual records. Add a Service Layer whenever Presentation-layer clients would otherwise need to orchestrate multiple fine-grained domain interactions themselves — give them one clean, use-case-shaped call instead.

## Self-check questions
1. Using the `CustomerTableModule` example, explain what kind of business logic Table Module handles naturally, and what kind it would struggle with compared to a true Domain Model.
2. Using the `OrderService.place_order` example, explain what Presentation-layer code would have had to do instead if no Service Layer existed, and why that's worse.
3. Why does Service Layer's coarse-grained method design matter especially for remote clients? Connect this to round-trip cost.
4. Describe a genuinely simple application where adding a Service Layer would be unnecessary overhead, and explain what calling the domain layer directly would look like instead.

## References
- Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 9: "Domain Logic Patterns" (Table Module section) and Chapter 4: "Web Presentation" (Service Layer section, cross-referenced).
