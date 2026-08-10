---
id: ddd-evans/10
subject: ddd-evans
title: Repositories for persistence ignorance
slug: repositories-for-persistence-ignorance
status: drafted
mastery:
seniority: senior
source: Domain-Driven Design (Eric Evans), Part II, Chapter 6
prerequisites: [ddd-evans/08]
created: 2026-08-10
updated: 2026-08-10
---

# Repositories for persistence ignorance

## TL;DR
A repository presents domain code with a collection-like interface for retrieving and storing aggregates by identity, hiding all the actual persistence mechanics (SQL, ORM sessions, caching, network calls) behind an interface the domain layer defines and the infrastructure layer implements.

## The idea
Domain code that needs an `Order` shouldn't have to know or care whether that order lives in Postgres, DynamoDB, an in-memory cache, or a remote microservice — mixing persistence mechanics into domain logic (`ddd-evans/02`, `ddd-evans/03`) recreates exactly the layering violation those lessons exist to prevent, and it makes the domain layer untestable without a real database. A repository is the answer: it exposes a small, intention-revealing interface — conceptually "a collection of aggregates" — with methods like `find_by_id`, `save`, or domain-specific queries (`find_overdue_invoices()`), while everything about *how* those operations actually happen is hidden behind the interface.

The critical structural detail, tying directly back to `ddd-evans/03`'s layered architecture: the repository's *interface* is defined in the domain layer (because the domain layer is what needs it), while its *implementation* lives in the infrastructure layer. This is dependency inversion in action — the domain layer never imports a database driver; the infrastructure layer imports the domain layer's interface and fulfills it.

## How it works

### Interface in the domain layer, implementation in infrastructure
```
# domain layer
class OrderRepository(Protocol):
    def find_by_id(self, order_id: OrderId) -> Order: ...
    def save(self, order: Order) -> None: ...
    def find_pending_for_customer(self, customer_id: CustomerId) -> list[Order]: ...
```
```
# infrastructure layer
class PostgresOrderRepository(OrderRepository):
    def __init__(self, connection):
        self._conn = connection

    def find_by_id(self, order_id: OrderId) -> Order:
        row = self._conn.query_one("SELECT * FROM orders WHERE id = %s", order_id.value)
        lines = self._conn.query("SELECT * FROM order_lines WHERE order_id = %s", order_id.value)
        return OrderFactory.reconstitute(row, lines)   # see ddd-evans/09

    def save(self, order: Order) -> None:
        with self._conn.transaction():
            self._conn.execute("UPDATE orders SET status = %s WHERE id = %s", order.status, order.id.value)
            self._save_lines(order)
```
Note that `find_pending_for_customer` is named for what the domain needs to ask ("which orders are pending"), not how the query is executed — the method name is drawn from the ubiquitous language (`ddd-evans/01`), not from SQL vocabulary. A repository is not a generic `execute_query(sql)` escape hatch; each method should represent a genuine domain-meaningful retrieval need.

### One repository per aggregate root, not per table
Because aggregates (`ddd-evans/08`) are the transactional/consistency unit, repositories should be scoped one-per-aggregate-root — `OrderRepository` handles loading and saving whole `Order` aggregates (including their internal `OrderLine`s), but there is no separate `OrderLineRepository`, because `OrderLine` is never independently addressable outside its aggregate root. This mirrors the aggregate access rule exactly: if external code can't hold a reference to an `OrderLine` directly, it also shouldn't be able to query for one directly.

### Repositories return real domain objects, not raw rows or DTOs
`find_by_id` returns a fully-formed `Order` aggregate — with its invariants intact, its behavior available (`order.submit()` works immediately) — not a dictionary of column values that calling code has to convert. This is what "persistence ignorance" means in practice: the caller interacts with a real domain object and has no idea, and no need to know, what storage technology produced it. Testing domain and application logic becomes straightforward with a fake, in-memory implementation of the same interface:
```
class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._orders: dict[OrderId, Order] = {}

    def find_by_id(self, order_id: OrderId) -> Order:
        return self._orders[order_id]

    def save(self, order: Order) -> None:
        self._orders[order.id] = order
```
Application-layer use cases (`ddd-evans/02`, `ddd-evans/03`) can be fully unit-tested against `InMemoryOrderRepository`, with zero database setup, zero network calls, and fast, deterministic test runs — while the real `PostgresOrderRepository` is exercised separately by a smaller number of integration tests that verify the SQL actually works.

### Worked example: a repository query that leaks the wrong abstraction
A team once added `OrderRepository.find_by_raw_sql(sql: str)` as an "escape hatch" for a reporting feature that needed a complex, ad-hoc query. This immediately broke persistence ignorance — calling code now had to know SQL syntax and the physical schema, and the method couldn't be implemented at all by the `InMemoryOrderRepository` test double. The better fix was either a dedicated, named repository method expressing the actual domain question being asked (`find_orders_exceeding_value_in_period(...)`), or — more honestly, since bespoke reporting queries often don't belong to any one aggregate's natural lifecycle — a separate read-only reporting/query service outside the repository abstraction entirely, decoupled from the aggregate-persistence concern (a pattern sometimes called CQRS, elaborated further in `implementing-ddd`).

## Pros
- Domain and application logic become testable without any real database, dramatically speeding up the test suite and making tests deterministic.
- Swapping persistence technology (a new database, a caching layer, a migration to a different storage engine) touches only the infrastructure-layer implementation, never domain or application code.
- Enforces the aggregate boundary at the query level too, not just at the in-memory object-reference level — you literally cannot query for an internal entity directly if no repository method exposes one.

## Cons
- Designing a good repository interface (which domain-meaningful queries does the domain actually need?) takes real thought; a repository that grows an unbounded pile of ad-hoc query methods becomes its own maintenance burden.
- Can create a performance tax if naively implemented — loading a whole aggregate (including internals never actually needed for a given operation) when only a single field was required; usually solvable with targeted read-only query methods for reporting, without violating the write-side aggregate discipline.
- Some ORMs make the interface/implementation split awkward, tempting teams to expose ORM-specific query objects directly through what's nominally a repository interface, quietly reintroducing the coupling this pattern exists to prevent.

## Alternatives
- **Active Record** — domain objects that persist themselves directly (`order.save()`), collapsing the repository abstraction into the entity itself; simpler for small CRUD-heavy systems, but blurs the domain/infrastructure boundary and makes the domain layer hard to test without a real database.
- **Data Mapper without a repository abstraction** — use an ORM's session/unit-of-work directly from application code instead of wrapping it in a dedicated repository interface; less ceremony, but exposes ORM-specific concepts to application code and loses the clean swap-ability and fake-implementation testability a repository interface provides.
- **CQRS (Command Query Responsibility Segregation)** — split the write side (repositories loading/saving whole aggregates, as in this lesson) from the read side (dedicated, denormalized query models built for specific UI/reporting needs, bypassing the aggregate abstraction entirely for reads); a natural complement to repositories once read needs diverge significantly from the aggregate's natural shape, discussed further in `implementing-ddd`.

## When to use it
Use repositories for every aggregate root in a system that has meaningful business rules worth protecting and testing in isolation from infrastructure — which, per `ddd-evans/02` and `ddd-evans/08`, is most aggregates in a nontrivial domain.

## When NOT to use it
For simple, rule-free CRUD entities with no aggregate invariants to protect, a repository is largely ceremony over what an ORM's default data-access layer already provides — the benefit of persistence ignorance is proportional to how much domain logic actually needs isolating from infrastructure.

## Key takeaways / mental model
Think of a repository as "a fake, well-behaved in-memory collection that happens to be durable" — from the domain layer's point of view, `orders.find_by_id(id)` should feel exactly like indexing into a big in-memory dictionary of `Order` objects, with all the complexity of actually making that durable hidden entirely on the other side of the interface.

## Self-check questions
1. Why does the `OrderRepository` interface live in the domain layer while `PostgresOrderRepository` lives in infrastructure? What would break if it were the other way around?
2. Why shouldn't there be a separate `OrderLineRepository`, given that `OrderLine` is a real class in the codebase?
3. What went wrong with the `find_by_raw_sql` escape hatch example, and what are the two alternative fixes discussed, and when would you reach for each?
4. Explain how `InMemoryOrderRepository` makes an application-layer use case testable without a database, and what kind of bug that test *cannot* catch that an integration test against the real implementation would.

## References
- Domain-Driven Design: Tackling Complexity in the Heart of Software (Eric Evans), Chapter 6: "The Life Cycle of a Domain Object" (Repositories section).
