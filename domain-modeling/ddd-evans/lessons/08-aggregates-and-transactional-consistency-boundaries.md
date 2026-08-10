---
id: ddd-evans/08
subject: ddd-evans
title: Aggregates and transactional consistency boundaries
slug: aggregates-and-transactional-consistency-boundaries
status: drafted
mastery:
seniority: senior
source: Domain-Driven Design (Eric Evans), Part II, Chapter 6
prerequisites: [ddd-evans/04, ddd-evans/05]
created: 2026-08-10
updated: 2026-08-10
---

# Aggregates and transactional consistency boundaries

## TL;DR
An aggregate is a cluster of entities and value objects treated as one unit for the purpose of data changes, with a single entity — the aggregate root — as the only object external code is allowed to hold a reference to; the aggregate's boundary is also the transactional consistency boundary, and invariants spanning objects inside it must hold at the end of every transaction.

## The idea
Without an explicit consistency boundary, a rich object graph becomes dangerous: if any code anywhere can reach in and modify any object at any depth (an `OrderLine` buried three levels inside an `Order`), nothing can guarantee that cross-object invariants ("the sum of line totals must equal the order total," "an order can't have more shipped items than ordered items") stay true. Each individual modification might look locally reasonable, but the *aggregate* invariant — the rule that only makes sense in terms of the whole cluster — can silently break because no single piece of code was responsible for protecting it.

Evans's answer: designate one entity in a cluster as the **aggregate root**. External objects may hold a reference only to the root, never directly to any internal member. All modifications to anything inside the aggregate must go through the root's own methods, which means the root — and only the root — is responsible for enforcing every invariant that spans its internals. This turns "keep this multi-object rule true" from a distributed, unenforceable hope into a locally enforceable guarantee, and it gives you a natural, defensible transaction boundary: load one aggregate, modify it through its root, save it, in one transaction — never split a single business-meaningful change across multiple aggregates in the same transaction.

## How it works

### Root, boundary, and access rule
```
class Order:                          # aggregate root
    def __init__(self, order_id: OrderId):
        self.id = order_id
        self._lines: list[OrderLine] = []   # internal member, never exposed directly
        self._status = OrderStatus.DRAFT

    def add_line(self, product_id: ProductId, quantity: int, unit_price: Money) -> None:
        if self._status != OrderStatus.DRAFT:
            raise OrderNotEditableError()
        self._lines.append(OrderLine(product_id, quantity, unit_price))

    def total(self) -> Money:
        return sum((line.subtotal() for line in self._lines), Money.zero())

    def lines(self) -> tuple["OrderLine", ...]:
        return tuple(self._lines)   # read-only view, not the live mutable list
```
External code never does `order._lines.append(...)` directly — it calls `order.add_line(...)`, and the root is the only place that enforces "you can't add lines to a non-draft order." Even the read accessor (`lines()`) returns an immutable snapshot rather than the live internal list, closing off a common leak where returning a mutable collection lets outside code bypass the root's rules entirely by mutating the collection directly.

### Worked example: why the boundary matters — a broken invariant without it
Suppose `OrderLine` were externally addressable and some other part of the system held a direct reference to one and mutated its `quantity` without going through `Order`. `Order.total()` — if it's a cached field rather than computed live — would now silently disagree with the sum of its lines, and any rule like "an order over $10,000 requires manager approval" could be bypassed by a change nobody routed through the approval check. The aggregate boundary exists precisely to make this class of bug structurally impossible: if `OrderLine` is never reachable except through `Order`, there is no code path that can create this inconsistency.

### One aggregate, one transaction — a hard rule with real consequences
The book's guidance is strict: a single transaction should touch at most one aggregate. If a business operation seems to require atomically updating two aggregates at once, that's a signal either that the aggregate boundaries are drawn wrong (the two objects should actually be one aggregate) or that the operation doesn't actually need synchronous atomicity and should be modeled as eventual consistency via a domain event instead.

**Worked example — inventory and orders:**
A naive design might make `Order` and `Product` (with its `stockLevel`) part of one aggregate, so that placing an order can atomically decrement stock. But `Product` is touched by every order concurrently — making it part of every `Order` aggregate creates a massive contention hotspot (every order placement would lock the same `Product` row) and conflates two genuinely separate consistency concerns: "is this order internally valid" and "do we have enough stock." The better design keeps `Order` and `Product` as separate aggregates, and handles stock decrement via an `OrderPlaced` domain event consumed asynchronously (or via a short, separate transaction) by the inventory side — accepting that stock and order counts might be briefly, eventually consistent rather than perfectly atomic, in exchange for far better concurrency and a cleaner, honestly-scoped aggregate boundary.

### Sizing aggregates: small by default
A common early mistake is drawing aggregate boundaries too large — treating an entire `Customer` with all their `Orders`, `PaymentMethods`, and `SupportTickets` as one aggregate "because they're related." This creates enormous lock contention (loading/saving the whole graph for any small change) and conflates unrelated invariants. The book's guidance, reinforced heavily in later DDD community practice (see `implementing-ddd` for a much stronger "aggregates should be small" stance from Vaughn Vernon's later book), is to draw the smallest boundary that still protects a genuine, atomic invariant — often a single entity with a few small value objects, referencing other aggregates only by their ID, not by direct object reference.

### Referencing other aggregates by identity, not by object reference
```
class Order:
    def __init__(self, order_id: OrderId, customer_id: CustomerId):
        self.id = order_id
        self.customer_id = customer_id     # reference by ID, not by holding a Customer object
```
`Order` needs to know *which* customer placed it, but it should not hold a live, navigable reference to a full `Customer` aggregate — that would blur the transactional boundary (should saving an `Order` also cascade-save changes to `Customer`?) and tempt code into reaching across the boundary to mutate `Customer` state from inside `Order`-related code. Referencing by ID keeps the boundary honest and connects directly to `ddd-evans/11`'s discussion of navigation trade-offs.

## Pros
- Makes cross-object invariants actually enforceable — one root, one place responsible, instead of a hope distributed across every caller.
- Gives a natural, principled transaction and locking boundary, which is also usually the right boundary for optimistic-concurrency version checks.
- Small, well-drawn aggregates minimize contention and make the system easier to scale and reason about under concurrent load.

## Cons
- Drawing the boundary correctly is genuinely hard and often gotten wrong on the first attempt (too big, causing contention; too small, failing to protect a real invariant) — expect to revise it as understanding deepens.
- Enforces a strict "no direct external references to internals" discipline that requires vigilance in languages without strong encapsulation, and that ORMs sometimes fight against by default (lazy-loading full object graphs can invite exactly the boundary violations this pattern forbids).
- Cross-aggregate operations that used to be "just one transaction" now require eventual consistency and event-driven coordination, which is a genuine complexity increase, not just a stylistic change — teams need to be comfortable reasoning about brief windows of inconsistency.

## Alternatives
- **No aggregate discipline — a flat object graph with no protected boundaries** — simplest to start with, but as shown above, offers no structural guarantee that cross-object invariants stay true; works only for genuinely simple domains with few or no such invariants.
- **Database-transaction-scripts spanning multiple tables** — enforce invariants via database constraints and application-level transactions across many tables directly, bypassing the object-model boundary; can work but loses the domain-layer expressiveness this whole building-block chapter is built around, and pushes invariant logic into SQL rather than the model.
- **Saga / process-manager pattern** — for cross-aggregate business processes that must eventually reach a consistent state (like the inventory-decrement example), a saga explicitly orchestrates a sequence of local transactions and compensating actions; a natural companion to small aggregates plus domain events, elaborated further in `implementing-ddd`.

## When to use it
Use aggregates whenever a domain has genuine cross-object invariants that must hold true at the end of every transaction — most nontrivial business domains have at least a few of these (an order's total matching its lines, a cart's item count matching available inventory reservations, an account balance never going negative).

## When NOT to use it
For simple CRUD entities with no cross-object invariants to protect (a standalone `Tag` or `Category` with no internal structure), forcing an aggregate-root ceremony onto a single, simple entity is unnecessary — every entity technically *is* a trivial one-object aggregate, but the interesting design work only shows up once there's a real invariant spanning multiple objects to protect.

## Key takeaways / mental model
An aggregate boundary is a promise: "everything inside here is guaranteed consistent at the end of every transaction, and the only door in is the root." Draw that boundary around the smallest cluster of objects that share a genuine, atomic invariant — not around "things that seem related" — and reference everything else by ID.

## Self-check questions
1. Why is it dangerous to return a live, mutable reference to an aggregate's internal collection (like `order._lines`) from a getter, even if external code "usually" behaves and only reads it?
2. In the inventory example, why does making `Order` and `Product` one aggregate create a concurrency problem specifically, not just a modeling-elegance problem?
3. What's the practical difference between an aggregate referencing another aggregate by ID versus by direct object reference, in terms of what invariants each design can and can't enforce?
4. Take a domain you know and identify a case where you'd be tempted to make one large aggregate. What's the actual atomic invariant (if any) that justifies the boundary, and could it be smaller?

## References
- Domain-Driven Design: Tackling Complexity in the Heart of Software (Eric Evans), Chapter 6: "The Life Cycle of a Domain Object" (Aggregates section).
