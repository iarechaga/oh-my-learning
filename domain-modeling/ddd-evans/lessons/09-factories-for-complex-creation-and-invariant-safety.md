---
id: ddd-evans/09
subject: ddd-evans
title: Factories for complex creation and invariant safety
slug: factories-for-complex-creation-and-invariant-safety
status: drafted
mastery:
seniority: senior
source: Domain-Driven Design (Eric Evans), Part II, Chapter 6
prerequisites: [ddd-evans/08]
created: 2026-08-10
updated: 2026-08-10
---

# Factories for complex creation and invariant safety

## TL;DR
A factory encapsulates the knowledge needed to create a complex object or aggregate in a single, valid, invariant-satisfying step, so that an aggregate can never exist in a partially-constructed, invalid state at any point external code can observe it.

## The idea
Entities and aggregates (`ddd-evans/04`, `ddd-evans/08`) are supposed to guarantee their own invariants at all times. But construction is a special, dangerous moment: building a complex aggregate often requires several steps — creating internal entities, wiring up value objects, choosing an initial state — and if those steps are exposed to calling code as a sequence of individual calls, there's a window where the object exists but is invalid, and any code running during that window (or any code that creates the object but forgets a step) can end up with a broken aggregate.

A factory takes responsibility for that whole sequence and exposes only a single, atomic-looking creation operation that either produces a fully valid object or raises an error — never anything in between. This might be a static factory method, a dedicated factory class, or (for simple cases) just a well-designed constructor — the concept matters more than the specific mechanism, and the book is explicit that for simple objects a constructor is entirely sufficient and a separate factory class would be needless ceremony.

## How it works

### When a constructor is enough
For an object with a small, fixed set of required fields and no complex assembly logic, a constructor that validates its arguments *is* the factory — no separate class needed:
```
class Money:
    def __init__(self, amount: Decimal, currency: str):
        if amount < 0:
            raise NegativeMoneyError()
        self.amount = amount
        self.currency = currency
```
This already guarantees `Money` can never be negative — there is no other way to construct one. Introducing a `MoneyFactory` class here would be pure ceremony with zero benefit.

### When you need a real factory: assembling a multi-entity aggregate
Consider creating an `Order` aggregate that must start with at least one line item, a valid shipping address, and a customer-specific pricing tier applied to each line — multiple pieces of logic that don't belong scattered across calling code every time an order is created.
```
class OrderFactory:
    def __init__(self, pricing_service: PricingService):
        self._pricing = pricing_service

    def create_order(self, customer: Customer, items: list[tuple[ProductId, int]], shipping_address: Address) -> Order:
        if not items:
            raise EmptyOrderError("An order must have at least one item")
        order = Order(OrderId.generate(), customer.id, shipping_address)
        for product_id, quantity in items:
            unit_price = self._pricing.price_for(product_id, customer.loyalty_tier())
            order.add_line(product_id, quantity, unit_price)
        return order
```
Every caller that needs a new `Order` goes through `create_order`, which guarantees: at least one item, a priced-correctly line for each item, a valid address (validated inside `Address`'s own constructor per `ddd-evans/05`). There is no code path in the entire system that can produce an `Order` missing any of these guarantees, because the only door in is this one method. Compare this to the alternative — calling code doing `order = Order(...); order.add_line(...); order.add_line(...)` directly, several times, at several different call sites — where any one of those call sites could forget a step, apply the wrong pricing logic, or leave the order genuinely empty, and nothing would catch it until much later (or never).

### Worked example: reconstituting an aggregate from storage
Factories aren't only for brand-new objects — they're also the right place to handle **reconstitution**: rebuilding an aggregate from data loaded out of a database, which has its own invariant-safety concerns distinct from first-time creation (for instance, you generally do *not* want to re-run "must have at least one item" validation when reloading an order that's being cancelled and might legitimately have had all its items removed by a prior operation). Repositories (`ddd-evans/10`) typically delegate to a factory (or a dedicated reconstitution method) specifically so that "create new" and "rebuild from storage" invariant rules can differ without duplicating assembly logic:
```
class OrderRepository:
    def find_by_id(self, order_id: OrderId) -> Order:
        row = self._db.query_order(order_id)
        return OrderFactory.reconstitute(row.id, row.customer_id, row.lines, row.status)
```

### Factories and aggregate boundaries work together
A factory for a multi-entity aggregate should itself only ever construct within one aggregate boundary at a time (`ddd-evans/08`) — a factory that reaches across and also constructs or modifies a *different* aggregate as a side effect of building this one is quietly violating the "one transaction, one aggregate" discipline, just moved into the factory instead of the calling code. If creating one aggregate seems to require simultaneously creating or modifying another, that's often the same signal as in `ddd-evans/08`: consider whether an event-driven, eventually-consistent handoff is more honest than forcing it into one factory call.

## Pros
- Makes "partially constructed, invalid object" a state that's simply unreachable by any calling code, closing off a whole category of bugs at the source.
- Centralizes assembly knowledge (which pricing rule applies, what the default initial state is) in one place instead of duplicating it at every call site that creates the object.
- Separates "how do I build a valid instance" from "what does this instance do once it exists," keeping the entity/aggregate's own methods focused on behavior rather than assembly logic.

## Cons
- Adds an extra class/indirection layer that's pure overhead for simple objects where a validating constructor is already sufficient — the book explicitly warns against over-applying this pattern.
- A poorly-scoped factory can become a dumping ground for unrelated creation logic across many different aggregate types, becoming its own maintenance burden.
- Reconstitution logic (rebuilding from storage) and first-creation logic can be tempting to merge into one method for the sake of fewer files, which reintroduces exactly the invariant-mismatch problem factories are meant to prevent.

## Alternatives
- **A well-designed constructor** — sufficient and preferable for objects with simple, fixed assembly and no cross-cutting dependencies (like the `Money` example) — don't build a factory class where a constructor will do.
- **Builder pattern** — useful when an object has many optional parameters and constructing it via one large constructor call would be unreadable; trades atomic single-call construction for a fluent multi-step API, which reopens (in a controlled way) the "intermediate invalid state" question this lesson is about, so the builder itself needs a final `build()`/`validate()` step that enforces invariants before returning.
- **ORM-driven default construction (no-arg constructor plus setters)** — common in frameworks that require a default constructor for object-relational mapping; directly conflicts with this pattern's goal, since it necessarily permits a transient invalid intermediate state, and typically needs to be isolated to the persistence-mapping layer rather than exposed as the domain object's public construction API.

## When to use it
Use a factory (dedicated class or static method) whenever creating a valid instance requires multiple steps, cross-object coordination, or a decision (which pricing tier, which initial state) that shouldn't be duplicated at every call site.

## When NOT to use it
Skip a dedicated factory for objects with simple, self-contained construction — a validating constructor already satisfies the goal, and adding a factory class on top is unnecessary indirection with no additional invariant-safety benefit.

## Key takeaways / mental model
The test for whether you need a factory: "can I imagine two different call sites constructing this object slightly differently, in a way that would leave it invalid or inconsistent with a sibling instance?" If yes, centralize construction in a factory. If the object is trivially, obviously always valid from a simple constructor, you don't need one.

## Self-check questions
1. Why does the book distinguish "reconstituting an aggregate from storage" from "creating a brand-new aggregate," and why might their invariant checks legitimately differ?
2. Take the `OrderFactory.create_order` example: what specific bug becomes possible if calling code is instead allowed to build an `Order` via direct `Order(...)` + repeated `add_line()` calls at will?
3. When is a plain validating constructor the right choice instead of a separate factory class? Give an example from a domain you know.
4. Why should a factory avoid reaching across aggregate boundaries (`ddd-evans/08`) to construct or modify a second aggregate as a side effect?

## References
- Domain-Driven Design: Tackling Complexity in the Heart of Software (Eric Evans), Chapter 6: "The Life Cycle of a Domain Object" (Factories section).
