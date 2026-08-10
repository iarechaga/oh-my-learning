---
id: implementing-ddd/08
subject: implementing-ddd
title: Repositories and persistence-mapping strategies
slug: repositories-and-persistence-mapping-strategies
status: drafted
mastery:
seniority: senior
source: Implementing Domain-Driven Design (Vaughn Vernon), Chapter 12: Repositories
prerequisites: [implementing-ddd/02, implementing-ddd/04]
created: 2026-08-10
updated: 2026-08-10
---

# Repositories and persistence-mapping strategies

## TL;DR
A repository gives the domain model the illusion of an in-memory collection of aggregates while hiding all persistence mechanics behind it; the discipline that keeps this useful rather than leaky is that a repository operates on whole aggregates only (never child entities individually) and its interface is defined in domain terms in the model layer, even though its implementation lives in infrastructure.

## The idea
Before repositories, persistence logic tends to leak into the domain model as scattered SQL, ORM-session calls, or query-builder invocations mixed directly into methods that are supposed to express business logic — the domain model ends up littered with concerns ("did I remember to flush the session?", "is this within a transaction?") that have nothing to do with the actual business rules being expressed. A repository is Evans's answer: an interface, expressed in the ubiquitous language of the aggregate it manages (`OrderRepository`, not `OrderDao` or generic `Repository<Order>` with SQL leaking through), offering collection-like operations — `add`, `findById`, sometimes a small set of domain-meaningful queries — that make the aggregate behave, from the domain model's point of view, like it's just sitting in an in-memory collection. Vernon's chapter goes further than Evans's original treatment by working through the concrete persistence-mapping mechanics: how a repository interacts with ORMs, how it enforces the aggregate boundary (`implementing-ddd/04`) at the persistence layer, and how repository design interacts with eventual consistency and event publication.

## How it works

### Rule 1 — One repository per aggregate root, never per entity
Since only aggregate roots are addressable from outside the aggregate (`implementing-ddd/04`, `implementing-ddd/05`), only aggregate roots get repositories. A `LineItem` inside an `Order` aggregate has no `LineItemRepository` — it's loaded, saved, and queried only as part of loading and saving the `Order` aggregate root that owns it.

**Worked example — order fulfillment.**
```
interface OrderRepository {
    Optional<Order> findById(OrderId id);
    void add(Order order);
    List<Order> findByCustomerAwaitingFulfillment(CustomerId customerId);
}
```
`findByCustomerAwaitingFulfillment` is named in domain terms — a developer reading it knows exactly what it returns without inspecting a SQL query — and it returns *whole* `Order` aggregates (with all their `LineItem`s loaded), never a partial projection mixing pieces of unrelated aggregates.

### Rule 2 — Define the interface in the domain/model layer, implement it in infrastructure
The `OrderRepository` interface lives alongside the `Order` aggregate in the domain model; the concrete implementation (`JpaOrderRepository`, `PostgresOrderRepository`) lives in an infrastructure module and is injected wherever the domain/application layer needs it. This is the Dependency Inversion Principle applied specifically to persistence: the domain model depends on an abstraction it owns, and infrastructure depends on (implements) that abstraction — never the other way around. It's what keeps the domain model testable without a real database (a fake/in-memory `OrderRepository` implementation is enough for unit tests) and swappable (changing from Postgres to a different store touches only the infrastructure module).

### Rule 3 — Persistence-mapping strategy depends on the aggregate's needs
Vernon walks through several strategies:
- **ORM-mapped aggregates** (JPA/Hibernate-style) — convenient for straightforward relational mapping, but requires care to avoid the ORM's own conventions (cascading saves, lazy-loading proxies) leaking the aggregate boundary — e.g. configuring the ORM so a `LineItem` cannot be loaded or saved independently of its owning `Order`, even though the ORM would happily let you do that by default.
- **Hand-rolled SQL/mapping** — more code, but total control over exactly what's loaded and saved, useful when an aggregate's shape doesn't map cleanly onto an ORM's assumptions, or when performance-sensitive queries need hand-tuned SQL.
- **Document-store mapping** — an aggregate maps naturally onto a single JSON document in a document database (MongoDB, DynamoDB) — often the most natural fit conceptually, since "one aggregate, one consistency boundary" maps directly onto "one document, one atomic write."
- **Event-sourced persistence** — instead of storing current state, store the sequence of events that produced it, reconstructing state by replay (see `implementing-ddd/13`) — a repository in this style has a fundamentally different `findById` (replay events) and `add`/`save` (append new events) implementation, but the same domain-facing interface shape.

### Rule 4 — Repository operations are transaction-scoped, and events are published around persistence
Since one aggregate is modified per transaction (`implementing-ddd/04`), a repository's `add`/`save` call typically happens inside a transaction boundary managed by the application service (`implementing-ddd/09`), and events raised by the aggregate during that operation (`implementing-ddd/07`) are collected and published either within the same transaction (via a transactional outbox, ensuring the event is never lost if the process crashes right after commit) or immediately after commit succeeds.

**Worked example — banking.**
```
class WithdrawFundsService {
    @Transactional
    void handle(WithdrawFundsCommand cmd) {
        Account account = accountRepository.findById(cmd.accountId())
            .orElseThrow(() -> new AccountNotFoundException(cmd.accountId()));
        account.withdraw(cmd.amount());       // raises FundsWithdrawn internally
        accountRepository.save(account);      // persists new balance
        eventPublisher.publish(account.pullEvents()); // publishes FundsWithdrawn, ideally via outbox
    }
}
```

### Rule 5 — Collection-oriented vs. persistence-oriented repository style
Vernon distinguishes a *collection-oriented* repository (behaves like an in-memory `Set` — `add`, and later mutations to the returned object are automatically tracked and persisted on transaction commit, common with ORMs using a unit-of-work/session pattern) from a *persistence-oriented* repository (explicit `save`/`update` calls required after mutation, no automatic dirty-tracking). Both are valid; the choice usually follows from the underlying persistence technology (ORMs favor collection-oriented; hand-rolled SQL or document stores usually favor persistence-oriented, explicit save calls), and a codebase should pick one style and apply it consistently rather than mixing both, which confuses callers about whether a mutation needs an explicit save.

## Pros
- Gives the domain model a clean, testable seam — domain and application logic can be tested against an in-memory fake repository with zero database dependency, dramatically speeding up the test suite for the core domain.
- Enforces the aggregate boundary at the persistence layer, not just in the object model — a well-designed repository interface makes it structurally awkward to load or save part of an aggregate independently of the whole.
- Isolates persistence-technology decisions (which database, which ORM, whether to event-source) behind a stable interface, so that changing the underlying storage strategy is a contained, infrastructure-layer change rather than a domain-wide rewrite.

## Cons
- Naive repository queries (`findByCustomerAwaitingFulfillment` loading full aggregates including every line item) can be inefficient for read-heavy use cases that only need a few fields — this is exactly the pressure that motivates CQRS read models (`implementing-ddd/14`) as a complementary pattern rather than stretching the repository to serve every query shape.
- ORM cascading/lazy-loading defaults actively fight the "aggregate-boundary-only" discipline, requiring explicit configuration effort to prevent the ORM from allowing child-entity access that should be forbidden.
- Repository interfaces can accumulate query-method sprawl over time (`findByX`, `findByY`, `findByXAndY...`) if every reporting or display need is routed through the aggregate repository instead of a dedicated read model — a symptom that a system has outgrown pure repository-based reads.

## Alternatives
- **Active Record pattern** — the aggregate/entity itself knows how to load and save itself (`order.save()` rather than `repository.save(order)`); simpler for small CRUD-shaped systems (common in Rails/Django-style frameworks) but tightly couples the domain object to persistence mechanics, undermining the testability and boundary-enforcement benefits repositories provide — reasonable for a generic/supporting subdomain (`implementing-ddd/01`), weak for a core domain.
- **Data Access Object (DAO) per table** — expose CRUD operations per database table rather than per aggregate; more granular and closer to the relational schema, but breaks the "operate on whole aggregates only" discipline and reintroduces the risk of loading/saving partial aggregate state.
- **CQRS with separate read/write models** — keep the repository purely for the write side (loading an aggregate to execute a command) and serve all queries through dedicated, denormalized read models instead of repository query methods — see `implementing-ddd/14` for when this split becomes worth the added infrastructure.

## When to use it
For every aggregate root in a core or supporting domain (`implementing-ddd/01`) that needs persistence — define the repository interface in the domain layer, keep operations scoped to whole aggregates, and pick a mapping strategy that matches the aggregate's natural shape and the team's operational needs.

## When NOT to use it
For read-heavy queries that don't map to loading a whole aggregate for a business operation (dashboards, reports, list views), don't force them through the aggregate repository — that's a signal for a dedicated read model (`implementing-ddd/14`) instead, which can be denormalized and optimized for exactly the shape the read needs.

## Key takeaways / mental model
A repository should make the rest of the domain model forget the database exists — if calling code ever needs to think about SQL, sessions, or lazy-loading proxies to use a repository correctly, the abstraction is leaking. The test: could you swap the concrete implementation for an in-memory fake without touching a single line of domain or application logic? If not, the boundary isn't clean yet.

## Self-check questions
1. Explain why a repository should only expose operations on whole aggregate roots, never on child entities, using a concrete example of what could go wrong if a `LineItemRepository` existed alongside `OrderRepository`.
2. Why does defining the repository interface in the domain layer (with the implementation in infrastructure) matter for testability, specifically?
3. Compare collection-oriented and persistence-oriented repository styles. Which would you choose for a hand-rolled SQL implementation, and why?
4. A repository method `findOrdersForDashboard()` is added, returning heavily denormalized data unrelated to any single aggregate's natural shape. What does that addition signal about the system's needs, and what alternative pattern would you reach for instead?

## References
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 12: "Repositories".
- Domain-Driven Design (Eric Evans) — the original Repository pattern definition; see `ddd-evans`.
