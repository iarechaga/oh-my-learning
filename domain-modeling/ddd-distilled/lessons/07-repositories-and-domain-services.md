---
id: ddd-distilled/07
subject: ddd-distilled
title: Repositories and domain services
slug: repositories-and-domain-services
status: drafted
mastery:
seniority: mid
source: Domain-Driven Design Distilled (Vaughn Vernon), Chapter 5 "Tactical Design with Aggregates" (repositories and services as supporting tactical patterns)
prerequisites: [ddd-distilled/06]
created: 2026-08-10
updated: 2026-08-10
---

# Repositories and domain services

## TL;DR
A **repository** provides the illusion of an in-memory collection of aggregates — `add`,
`get by ID`, `remove` — hiding persistence mechanics behind a domain-shaped interface, so
the rest of the domain model never talks to a database directly. A **domain service**
holds a piece of domain logic that doesn't naturally belong to any single entity or value
object, typically because it coordinates across multiple aggregates or needs external
domain knowledge that isn't any one object's responsibility alone.

## The idea
Once you have well-designed aggregates (`ddd-distilled/06`), two gaps remain. First: how
does code actually *load* and *save* an aggregate without domain logic getting tangled up
with SQL, ORMs, or HTTP calls to a database service? Second: what do you do with a piece
of business logic that genuinely spans multiple aggregates, or needs no aggregate-specific
state at all, and so doesn't fit naturally as a method on any one entity or value object?

Both patterns exist to keep the domain model *pure* — expressed in domain terms, free of
infrastructure concerns, and free of logic awkwardly forced onto an object that doesn't
own it. This purity is what makes ubiquitous language (`ddd-distilled/02`) hold all the
way down to the code, not just at the entity level.

## How it works

### Repositories
A repository is defined by an interface expressed entirely in domain vocabulary and
aggregate types — `OrderRepository.findById(orderId): Order`, `OrderRepository.save(order)`
— with the *implementation* of that interface (SQL queries, an ORM, a document store, an
in-memory map for tests) living outside the domain layer, typically in an infrastructure
module. The domain layer only ever depends on the interface.

Rules of thumb:
- **One repository per aggregate root**, not per table and not per entity inside an
  aggregate — you never need an `OrderLineRepository`, because `OrderLine` isn't
  independently reachable outside the `Order` aggregate (`ddd-distilled/06`).
- The repository returns and accepts fully-formed aggregate instances, not raw rows or
  DTOs — callers work with `Order`, never with a database row shape.
- Queries that don't map onto "get the aggregate by its identity" (e.g., "find all orders
  placed in the last 24 hours for reporting") are often better served by a separate
  read-model/query mechanism rather than stretching the repository interface to become a
  general-purpose query API — keeping repositories narrow (this connects to the eventual
  consistency and read-model ideas in `ddd-distilled/08`).

**Worked example.** An `OrderRepository` interface:
```
interface OrderRepository {
    findById(orderId: OrderId): Order | null
    save(order: Order): void
    nextIdentity(): OrderId
}
```
A checkout use case calls `orderRepository.findById(id)`, gets back a real `Order`
aggregate with all its business methods available, calls `order.addLineItem(...)` (which
enforces the aggregate's invariants, per `ddd-distilled/06`), and calls
`orderRepository.save(order)`. Nothing in the checkout use-case code, or in the `Order`
aggregate itself, knows or cares whether `save` writes to Postgres, DynamoDB, or an
in-memory test double — that's the entire point. Swapping the storage technology later
touches only the repository's implementation, never the domain model or the use cases
that depend on the interface.

### Domain services
A domain service holds business logic that:
- **Spans multiple aggregates** — e.g., "transfer funds between two accounts" genuinely
  involves two `Account` aggregates and doesn't belong on either one alone (putting a
  `transferTo(otherAccount)` method on `Account` would force one aggregate to reach into
  and mutate another directly, violating the aggregate boundary rules from
  `ddd-distilled/06`). A `FundsTransferService.transfer(fromAccountId, toAccountId,
  amount)` domain service coordinates the operation, typically by loading both
  aggregates via their repositories, invoking a debit method on one and a credit method
  on the other, each within its own aggregate's invariant-protected boundary.
- **Needs no aggregate-specific state** — e.g., "calculate shipping cost given a
  destination, weight, and carrier rate table" is pure domain logic (real business
  rules, real domain vocabulary) but has no natural home on any single entity; a
  `ShippingCostCalculator` domain service is a stateless, side-effect-free unit
  expressing exactly that rule.
- **Needs external domain knowledge that isn't naturally any one object's job** — e.g.,
  "is this loan applicant's requested amount within the fraud-risk threshold for their
  profile" might consult multiple data points and an external policy that doesn't belong
  to the `LoanApplication` entity itself.

**Worked example — a domain service vs. a misplaced entity method.** A naive design puts
`order.applyDiscountCode(code, catalogService)` directly on `Order`, reaching out to an
external catalog lookup mid-method. A cleaner design has a `DiscountEligibilityService`
domain service that takes the order and the discount code, consults whatever it needs
(catalog data, customer tier), and returns a `DiscountResult` value object
(`ddd-distilled/05`); the `Order` aggregate then has a narrow, pure method
`order.applyDiscount(discountResult)` that only knows how to apply an already-computed
result to its own state. This keeps `Order`'s own methods free of external dependencies
and keeps the cross-cutting eligibility logic in one clearly-named, testable place.

### Distinguishing a domain service from an application service
A common point of confusion: **domain services** contain business/domain logic and use
domain vocabulary (`FundsTransferService`, `ShippingCostCalculator`). **Application
services** (sometimes called use-case handlers or command handlers) sit one layer up —
they orchestrate a whole use case (load aggregates via repositories, call domain
methods/domain services, save results, publish domain events per `ddd-distilled/08`,
handle transactions) but contain no business rules of their own. Mixing the two —
letting business rule logic leak into an application service, or letting an application
service's orchestration concerns (transaction handling, DTO mapping for an API response)
leak into a domain service — is a common source of the "logic scattered everywhere"
problem this whole pattern set exists to prevent.

## Pros
- Repositories keep the domain model free of persistence-technology details, which makes
  the domain layer testable with fast in-memory fakes and makes swapping storage
  technology a contained, low-risk change.
- Domain services give a proper home to real business logic that would otherwise be
  awkwardly bolted onto an entity that doesn't own it, or duplicated across several
  entities.
- Both patterns keep the ubiquitous language (`ddd-distilled/02`) consistent all the way
  into infrastructure-adjacent code, instead of "domain terms in the entities, generic
  CRUD terms everywhere else."
- Narrow, per-aggregate repository interfaces reinforce correct aggregate boundaries
  (`ddd-distilled/06`) — there's no way to accidentally query into another aggregate's
  internals if the repository API doesn't expose that.

## Cons
- Overusing domain services is a common failure mode — logic that actually belongs on an
  entity (and would be better encapsulated there) sometimes gets pulled out into a
  service reflexively, producing an anemic-model smell where entities become thin data
  holders and all real behavior lives in services (see `software-engineering/clean-code`,
  `clean-code/06`, on the general anemic-model risk).
- Repository interfaces that grow too many specialized query methods ("just add one more
  finder method") gradually turn into a general-purpose query API, undermining the
  narrow, aggregate-shaped contract that made them useful in the first place.
- The repository abstraction adds an indirection layer that has real cost for very simple
  CRUD subdomains where a direct data-access call would be simpler and clearer — worth
  reserving for aggregates that actually warrant the ceremony (`ddd-distilled/04`).
- Coordinating multiple aggregates inside one domain service, inside one transaction, can
  quietly reintroduce the same contention problems that small aggregates were designed
  to avoid — cross-aggregate domain services should usually favor eventual consistency
  via domain events (`ddd-distilled/08`) over a single large transaction wherever the
  business can tolerate it.

## Alternatives
- **Active Record pattern** (the aggregate/entity itself knows how to save and load
  itself, common in frameworks like Rails or Django ORM) — simpler for small CRUD apps,
  but couples the domain model directly to persistence technology, which repositories
  exist specifically to avoid; a poor fit once the domain model gets non-trivial.
- **Generic CRUD/DAO layer with no aggregate awareness** — a data-access-object per table
  rather than per aggregate; simpler to generate/scaffold but tends to leak persistence
  shape (individual tables/rows) into calling code instead of hiding it behind the
  aggregate boundary.
- **Putting cross-aggregate logic directly in application/use-case code** instead of a
  named domain service — acceptable for a one-off, simple coordination, but loses the
  benefit of a well-named, independently testable, reusable unit once the logic is
  non-trivial or used from more than one use case.

## When to use it
Use a repository for every aggregate root in a bounded context you're modeling
deliberately. Reach for a domain service specifically when logic spans multiple
aggregates or genuinely has no natural single-entity home — and always try the "does this
belong on the entity instead" question first, since misplaced domain services are a more
common mistake than missing ones.

## When NOT to use it
Skip repositories for generic/simple CRUD subdomains where direct, simple data access is
clearer and the aggregate ceremony (`ddd-distilled/04`, `ddd-distilled/06`) wasn't
warranted in the first place. Skip a domain service if the logic in question actually
fits naturally as a method on one entity or value object — reaching for a service by
default, instead of asking whether the object itself should own the behavior, is the
single most common misuse of this pattern.

## Key takeaways / mental model
Repository = "give the domain model amnesia about how it's persisted" — one per aggregate
root, domain-shaped interface, infrastructure-shaped implementation kept out of sight.
Domain service = "a home for real business logic that doesn't belong to any one object" —
reach for it only after asking whether an entity or value object should own the behavior
instead, and keep it distinct from application-service orchestration logic.

## Self-check questions
1. Why is it a design smell to have an `OrderLineRepository` in a system where `Order` is
   the aggregate root and `OrderLine` lives only inside it?
2. Walk through the fund-transfer example. Why can't `transferTo()` simply live as a
   method on the `Account` entity?
3. What's the difference between a domain service and an application service? Give an
   example of logic that would clearly belong to each.
4. A teammate keeps adding new finder methods to a repository interface ("findByStatus",
   "findByCustomerAndDateRange", "findTopSpenders"). What's the risk, and what
   alternative would you suggest for query-heavy needs like these?
5. Describe a case where putting logic into a domain service, instead of onto an entity,
   would actually be the wrong call — i.e., a case of domain-service overuse.

## References
- Domain-Driven Design Distilled (Vaughn Vernon), Chapter 5: "Tactical Design with
  Aggregates" (repositories and domain services as supporting tactical patterns).
- For a deeper treatment of repository implementation strategies and application-service
  layering, see `domain-modeling/implementing-ddd`.
