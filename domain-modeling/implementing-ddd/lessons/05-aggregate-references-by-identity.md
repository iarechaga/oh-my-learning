---
id: implementing-ddd/05
subject: implementing-ddd
title: Aggregate references by identity
slug: aggregate-references-by-identity
status: drafted
mastery:
seniority: senior
source: Implementing Domain-Driven Design (Vaughn Vernon), Chapter 10: Aggregates (identity references)
prerequisites: [implementing-ddd/04]
created: 2026-08-10
updated: 2026-08-10
---

# Aggregate references by identity

## TL;DR
One aggregate should never hold a direct object reference to another aggregate's root or internals — only its identity (a value-object ID); this single rule is what actually makes small aggregate boundaries (`implementing-ddd/04`) hold, because an object reference is a standing invitation to reach across the boundary and mutate the other aggregate inside the same transaction.

## The idea
It's tempting, and often the ORM-idiomatic default, for an `Order` aggregate to hold a `Customer customer` field pointing directly at a live `Customer` object — lazy-loaded, navigable, convenient for a view template that wants `order.getCustomer().getName()`. Vernon argues this convenience is exactly the mechanism by which aggregate boundaries erode in practice: once `Order` holds a live reference to `Customer`, nothing stops application code (or, worse, a later developer under deadline pressure) from writing `order.getCustomer().applyDiscount()` — mutating the `Customer` aggregate from inside a transaction that's nominally about `Order`. Now two aggregates are being modified in one transaction, silently violating the "one aggregate per transaction" rule from `implementing-ddd/04`, and the ORM's cascade/lazy-load machinery has effectively merged two aggregates back into one giant implicit aggregate — with none of the small-aggregate benefits and all of the large-aggregate costs. The fix is structural, not just a coding convention: `Order` should hold a `CustomerId`, a plain value object, not a `Customer`. To do anything with the customer, application code must explicitly fetch it through its own repository (`implementing-ddd/08`) — a deliberate, visible, separate operation that cannot silently smuggle a cross-aggregate mutation into a single transaction.

## How it works

### The mechanism: identity as the only crossing point
Every aggregate root has an identity — a value object like `CustomerId`, `OrderId`, `ProductId` — typically a wrapped UUID or a domain-meaningful key, never a raw primitive (wrapping it prevents accidentally passing an `OrderId` where a `CustomerId` was expected, a class of bug the type system catches for free). Any *other* aggregate that needs to refer to this one stores only that identity value object, nothing else.

**Worked example — e-commerce order fulfillment.**
```
// Wrong — direct object reference, invites cross-aggregate mutation
class Order {
    private Customer customer;      // live reference into another aggregate
    private List<LineItem> items;
}

// Right — identity reference only
class Order {
    private CustomerId customerId;  // opaque value object, no navigable behavior
    private List<LineItem> items;
}
```
With only `customerId` available, code that wants customer details must go through `CustomerRepository.findById(order.customerId())` explicitly — a visible, separate fetch, in its own right, that makes clear "I am now working with a second aggregate" rather than hiding that fact behind a field access that looks free.

### Consequence 1 — cross-aggregate data for display is assembled, not navigated
A checkout confirmation page needs the customer's name and the order's line items together. Rather than navigating `order.getCustomer().getName()`, application code fetches both aggregates independently (or, more commonly at scale, reads from a denormalized read model built for exactly this purpose — see `implementing-ddd/14`) and assembles a DTO for the view. This is more code than a navigable object graph, but it makes the aggregate boundary real rather than aspirational.

### Consequence 2 — cross-aggregate business rules are enforced via domain services or events, not navigation
A rule like "an order cannot be placed for a customer whose account is suspended" spans two aggregates. With identity-only references, this can't be a method that reaches from `Order` into `Customer` — it has to be explicit coordination: an application service (`implementing-ddd/09`) fetches the `Customer` aggregate by the `CustomerId` supplied in the command, checks its suspension status, and only then instructs the `Order` aggregate to proceed. The rule is enforced at the orchestration layer, not smuggled into the aggregate's own methods.

**Worked example — a forum/collaboration tool.** A `Comment` aggregate references its `Discussion` by `DiscussionId` only. Enforcing "a comment cannot be added to a locked discussion" requires the application service to fetch the `Discussion` aggregate, check its lock status, and only then create the `Comment` — two separate reads/aggregate fetches coordinated explicitly, rather than `comment.discussion.isLocked()` reaching across a live reference.

### Consequence 3 — serialization and caching become simpler and safer
Aggregates that hold only identity references serialize trivially (no risk of an infinite object graph, no accidental over-fetching of an entire related aggregate when only the ID was needed) and are safe to cache independently — caching an `Order` doesn't risk caching a stale, embedded copy of `Customer` data that then silently diverges from the source of truth.

## Pros
- Makes the "one aggregate per transaction" discipline from `implementing-ddd/04` structurally enforced rather than merely a convention developers can forget under pressure — there's no live reference to accidentally mutate.
- Decouples aggregates for independent evolution, caching, and serialization; an aggregate can be loaded, cached, or moved to a different service (see `implementing-ddd/03`) without needing to resolve or transport a graph of other aggregates along with it.
- Makes cross-aggregate coordination visible in the code — a reader can see every place two aggregates are used together, because it always requires an explicit second fetch, rather than being hidden behind transparent object navigation.

## Cons
- More verbose application-layer code: every cross-aggregate read requires an explicit fetch (or a purpose-built read model) instead of free navigation through an object graph, which feels like a regression compared to ORM-idiomatic code for developers used to that style.
- Naively fetching a second aggregate by ID inside a loop (N+1 query patterns) is an easy performance trap if not paired with batching, caching, or a proper read-model strategy for display purposes.
- Requires discipline across the whole team — a single place where someone adds a convenient object reference "just this once" reopens the cross-aggregate mutation risk this rule exists to prevent, and ORMs often make the "correct" identity-only mapping more awkward to configure than the "wrong" cascade-everything default.

## Alternatives
- **Direct object references with disciplined code review** — allow live references but rely entirely on team discipline and review to prevent cross-aggregate mutation; fragile at scale (the failure mode is silent and easy to miss in review) and not recommended by Vernon except possibly within a very small, tightly disciplined team.
- **Denormalized read models for cross-aggregate display** — instead of fetching a second aggregate by ID for display purposes, maintain a purpose-built read model (`implementing-ddd/14`) updated asynchronously from domain events, avoiding the N+1 fetch problem entirely at the cost of eventual consistency and extra infrastructure.
- **GraphQL/BFF-layer aggregation** — push cross-aggregate assembly out of the domain layer entirely into an API gateway or backend-for-frontend layer that fetches from multiple bounded contexts (`implementing-ddd/03`) and stitches results together for the client, keeping each context's aggregates fully decoupled from the others' identities beyond what the gateway needs.

## When to use it
Always, for every aggregate-to-aggregate relationship within a bounded context, and especially wherever aggregates might later be split across services (`implementing-ddd/03`) — identity references are what makes that split possible without a rewrite.

## When NOT to use it
Within the internals of a single aggregate — between its root and its own child entities/value objects — direct object references are correct and expected; this rule applies specifically at aggregate-to-aggregate boundaries, not inside one aggregate's own object graph.

## Key takeaways / mental model
If you can navigate from one aggregate to another via a field access without an explicit repository call, the aggregate boundary isn't real — it's decorative. Identity-only references force every cross-aggregate interaction to be a visible, separate act, which is what actually keeps "one aggregate per transaction" true in code, not just in a diagram.

## Self-check questions
1. Find a place (in any codebase you know) where one entity holds a direct object reference to another that is arguably a separate aggregate. What would change, concretely, if that reference were replaced with an identity-only reference?
2. Why does an ORM's lazy-loading and cascading-save behavior make it easier to accidentally violate this rule than to follow it?
3. Design a checkout confirmation view that needs both `Order` and `Customer` data, using identity-only references. What are two different strategies for assembling that view, and what's the trade-off between them?
4. A cross-aggregate business rule ("cannot place an order for a suspended customer") needs enforcing. Where does that enforcement logic live if `Order` cannot navigate to `Customer` directly?

## References
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 10: "Aggregates" (identity-reference guidance).
