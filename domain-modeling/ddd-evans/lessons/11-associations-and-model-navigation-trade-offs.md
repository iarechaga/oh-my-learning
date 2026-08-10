---
id: ddd-evans/11
subject: ddd-evans
title: Associations and model navigation trade-offs
slug: associations-and-model-navigation-trade-offs
status: drafted
mastery:
seniority: senior
source: Domain-Driven Design (Eric Evans), Part II, Chapter 5
prerequisites: [ddd-evans/04, ddd-evans/05, ddd-evans/08]
created: 2026-08-10
updated: 2026-08-10
---

# Associations and model navigation trade-offs

## TL;DR
Every association between domain objects — one references another, one navigates to another — is a design decision with real cost, not a free byproduct of "these two things are related in real life"; the book pushes toward constraining associations to a single direction and a qualified, bounded scope wherever the domain allows it, rather than defaulting to bidirectional, unconstrained references.

## The idea
Real-world domains are richly interconnected — a `Customer` has `Orders`, each `Order` references a `Customer`, a `Product` appears in many `Orders`, a `Warehouse` stores many `Products` which are also sold by multiple `Suppliers`. Modeling software after this naively, by giving every object a direct reference to every other object it's "related to" in conversation, produces a tangled graph where every object transitively knows about nearly every other object in the system. That tangle makes the system nearly impossible to reason about locally: understanding `Order` requires understanding `Customer`, which requires understanding `PaymentMethod`, which requires understanding `Bank`, and so on outward, with no natural stopping point.

Evans's guidance: before adding a navigable reference from A to B, ask whether the domain genuinely requires traversing from A to B, or whether the relationship is only ever queried starting from B toward A (or not navigated directly at all, only looked up via a repository). Prefer unidirectional associations. Prefer qualifying a reference to narrow it (instead of "a `Customer` has all their `Orders`," narrow it to "a `Customer`, given a date range, has these `Orders`," often meaning the relationship isn't a stored reference at all but a repository query). And, per `ddd-evans/08`, prefer referencing other aggregates by identity rather than holding a live object reference at all.

## How it works

### Bidirectional references — the default trap
```
class Customer:
    def __init__(self):
        self.orders: list["Order"] = []     # Customer -> Order

class Order:
    def __init__(self, customer: Customer):
        self.customer = customer            # Order -> Customer
        customer.orders.append(self)        # keeping both sides in sync
```
This looks natural — "of course a customer has orders and an order has a customer" — but it has real costs: both objects must be kept in sync on every change (forget one side of the update, and the graph is inconsistent), both objects now depend on each other's full class definition (complicating modular boundaries, `ddd-evans/07`), and it's not clear which object is responsible for enforcing invariants that involve both (does `Customer` or `Order` own the rule "a customer can have at most 3 pending orders"?).

### Constraining to one direction
Ask: does the domain actually need to navigate from `Customer` to all its `Order`s directly through object references, or is that only ever a query ("show me this customer's orders"), which a repository can answer without a stored bidirectional link at all?
```
class Order:
    def __init__(self, order_id: OrderId, customer_id: CustomerId):
        self.id = order_id
        self.customer_id = customer_id   # Order -> Customer, by ID only (ddd-evans/08)

# "Customer's orders" becomes a repository query, not a stored reference:
orders = order_repository.find_by_customer(customer_id)
```
`Customer` no longer needs to know about `Order` at all — the association is one-directional (`Order` knows its `customer_id`), and the "reverse" navigation is answered by asking the `OrderRepository`, not by traversing an in-memory object graph. This is a direct application of `ddd-evans/08`'s aggregate-reference-by-ID guidance, generalized: the same reasoning that says aggregates shouldn't hold direct references to other aggregates applies more broadly to any association where bidirectionality isn't earning its cost.

### Qualifying an association to narrow its scope
Sometimes an association is genuinely needed in a direction, but modeling it as "all of them" is both semantically wrong and operationally expensive. A `Warehouse` doesn't need "all `Product`s ever stocked, unbounded" — it usually needs "current stock levels for products currently in this warehouse," which is a qualified, filtered relationship, not an unbounded collection reference:
```
class Warehouse:
    def stock_level(self, product_id: ProductId) -> int:
        return self._stock_repository.level_at(self.id, product_id)
```
Rather than `Warehouse.products: list[Product]` (an unbounded, ever-growing in-memory collection that would need to be loaded in full for any operation), the association is qualified down to "give me the level for *this* product," answered on demand. This keeps `Warehouse` lightweight and avoids ever loading a potentially enormous collection just to answer a narrow question.

### Worked example: a many-to-many association that hides a missing concept
A course-enrollment system modeled `Student.courses: list[Course]` and `Course.students: list[Student]` as a plain bidirectional many-to-many. It worked until the business needed to track *when* a student enrolled and their *grade* in the course — information that doesn't belong to either `Student` or `Course` alone, but to the *relationship* between them. This is a recurring pattern: an association that starts as a simple reference often turns out, once knowledge crunching (`ddd-evans/01`) digs deeper, to be hiding its own first-class concept — here, an `Enrollment` entity (with its own identity, `enrolledDate`, and `grade`) replacing the raw many-to-many link entirely. The lesson generalizes: when an association feels like it wants extra data attached to the *link itself*, that's usually a sign the association should become an object, not stay a raw reference.

### Traversal direction and aggregate boundaries interact
Because aggregates (`ddd-evans/08`) already constrain what's directly reachable, association design mostly matters *within* an aggregate (should `Order` navigate down to `OrderLine`, obviously yes, that's the root's own internals) and *across* aggregate boundaries (should `Order` hold a live reference to `Customer`, per the above, generally no — reference by ID and query when needed). Getting this right means association design and aggregate design are really the same design conversation, not two separate ones.

## Pros
- Unidirectional, qualified associations dramatically reduce the "everything touches everything" coupling that makes large object graphs hard to reason about or test in isolation.
- Removing unnecessary bidirectional sync logic eliminates a class of consistency bugs (forgetting to update both sides of a relationship).
- Forces genuinely valuable modeling discoveries, like promoting an association to its own entity (`Enrollment`) when it turns out to carry meaningful data of its own.

## Cons
- Constraining navigation sometimes means a query that used to be "just walk the object graph" now requires an explicit repository call, which can feel like a step backward in convenience for genuinely simple, always-needed lookups.
- Requires upfront judgment about which direction the domain actually needs, which isn't always obvious early and may need revisiting as usage patterns become clear.
- Overcorrecting into avoiding *all* direct references, even within a clearly single aggregate, adds needless indirection where a plain internal reference (like `Order` to its own `OrderLine`s) is completely appropriate.

## Alternatives
- **Bidirectional references everywhere** — simplest mental model at small scale ("just link everything that's related"), but doesn't scale past a small object graph, as shown above; usually the unexamined default rather than a deliberate choice.
- **Graph databases / native graph traversal** — for domains that are genuinely, primarily about rich, multi-directional traversal (social networks, recommendation engines), embracing a graph-native storage and query model may be more honest than fighting the domain's natural shape with DDD's traversal-minimizing bias; a case where the domain's own nature pushes back on this pattern's general advice.
- **Denormalized read models** — for read-heavy navigation needs (show a dashboard combining data reachable across many objects), build a purpose-built, denormalized read model instead of adding write-side associations just to serve a read — keeping the write-side aggregate graph minimal while still answering rich queries efficiently (related to the CQRS mention in `ddd-evans/10`).

## When to use it
Apply deliberate, minimized association design in any nontrivial domain model — actively ask, for every reference you're about to add, "which direction does the domain actually need, and is it unbounded or should it be qualified/queried instead?"

## When NOT to use it
Within a single aggregate, don't over-apply this caution — the root referencing its own internal entities directly (`Order` to `OrderLine`) is exactly the kind of tight, intentional coupling an aggregate boundary is meant to allow; the minimization concerns here are really about *cross*-aggregate and cross-module references, not internal aggregate structure.

## Key takeaways / mental model
Every stored, navigable reference is a promise to keep two things in sync forever and a coupling point that makes each side harder to understand alone — treat adding one the same way you'd treat adding a public API, not as a free reflection of "these things are related" in the real world.

## Self-check questions
1. Why does removing `Customer.orders` in favor of `order_repository.find_by_customer(customer_id)` reduce coupling? What specifically no longer needs to be kept in sync?
2. In the course-enrollment example, what specific new requirement (enrollment date, grade) was the signal that the association needed to become its own entity?
3. Give an example of an association within a domain you know that's currently bidirectional. Would narrowing it to one direction lose anything real, or was the bidirectionality unexamined default?
4. Why is minimizing associations mostly a concern *across* aggregate boundaries rather than within a single aggregate's own internal structure?

## References
- Domain-Driven Design: Tackling Complexity in the Heart of Software (Eric Evans), Chapter 5: "A Model Expressed in Software" (Associations section).
