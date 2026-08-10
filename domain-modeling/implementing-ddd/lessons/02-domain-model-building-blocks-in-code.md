---
id: implementing-ddd/02
subject: implementing-ddd
title: Domain model building blocks in code
slug: domain-model-building-blocks-in-code
status: drafted
mastery:
seniority: mid
source: Implementing Domain-Driven Design (Vaughn Vernon), Chapter 5 (Entities), Chapter 6 (Value Objects), Chapter 7 (Services), Chapter 9 (Modules)
prerequisites: [implementing-ddd/01]
created: 2026-08-10
updated: 2026-08-10
---

# Domain model building blocks in code

## TL;DR
Entities, value objects, domain services, and modules are the four load-bearing building blocks of a tactical DDD codebase; getting their responsibilities and boundaries right — entities carry identity and lifecycle, value objects carry immutable measurement/description, domain services hold logic that doesn't belong to any one entity, and modules group by domain meaning rather than technical layer — determines whether the rest of the tactical toolkit (aggregates, repositories, events) has a sound foundation to sit on.

## The idea
Evans's building blocks (`ddd-evans`) are conceptual categories; Vernon's chapters translate each one into concrete code-level rules that keep the categories from blurring into each other, which is the failure mode that actually happens in practice. The most common tactical DDD bug isn't "we forgot to use a value object" — it's "we used an entity where a value object belonged," or "we put domain logic in an application service instead of the entity it's about," or "we organized code by technical layer (`controllers/`, `services/`, `models/`) instead of by the domain concepts a reader actually needs to reason about together." This lesson distills the rules that keep those distinctions crisp, because every other tactical pattern in this subject (aggregates, repositories, domain events) assumes you already know when something is an entity versus a value object versus a service.

## How it works

### Entities: identity, mutability, and a lifecycle
An entity is defined by a thread of continuity and identity, not by its attribute values — two entities with identical attributes are still different entities if their identities differ (two `Customer` records with the same name and address are still two different customers). Concretely: an entity needs a stable identity (often a generated `CustomerId` value object, not a raw database auto-increment `long`, so identity survives independent of the persistence mechanism — see `implementing-ddd/05`), and equality is defined by identity comparison, never by comparing every attribute.

**Worked example — a forum/collaboration tool.** A `Discussion` entity has an identity (`DiscussionId`) that persists across its lifecycle: created, renamed, closed, reopened. Two discussions titled "Sprint Planning" are different entities if they have different `DiscussionId`s — renaming one doesn't turn it into the other, and `discussion1.equals(discussion2)` must compare `DiscussionId`, not title.

```
class Discussion {
    private final DiscussionId id;
    private String title;
    private DiscussionStatus status;

    void rename(String newTitle) { this.title = requireNonBlank(newTitle); }
    void close() { this.status = DiscussionStatus.CLOSED; }

    @Override
    public boolean equals(Object o) {
        return o instanceof Discussion && ((Discussion) o).id.equals(this.id);
    }
}
```

### Value objects: immutability, measurement, and structural equality
A value object has no identity of its own — it's defined entirely by its attributes, is immutable once created (any "change" produces a new instance rather than mutating in place), and equality is structural (all attributes equal → objects equal). Value objects are how you avoid "primitive obsession" — raw strings, ints, and decimals scattered through the model that silently allow invalid states (a `Money` represented as a bare `double` can be added to a `double` representing a percentage with no compiler complaint).

**Worked example — shipping.** A `ShippingAddress` value object bundles street, city, postal code, and country, validates itself at construction (a `ShippingAddress` that fails postal-code-format validation for its country simply cannot exist), and is replaced wholesale, never mutated, when the customer updates their address:

```
final class ShippingAddress {
    private final String street, city, postalCode, countryCode;
    ShippingAddress(String street, String city, String postalCode, String countryCode) {
        this.countryCode = requireValidCountry(countryCode);
        this.postalCode = requireValidPostalCode(postalCode, this.countryCode);
        this.street = street; this.city = city;
    }
    // no setters — "changing" an address means constructing a new ShippingAddress
}
```
A `Money` value object similarly bundles amount and currency together and refuses to be constructed with a negative amount for a domain where negative money is nonsensical — pushing invariant enforcement to the earliest possible point, construction, rather than scattering `if (amount < 0)` checks across every call site.

### Domain services: logic that doesn't belong to one entity or value object
Some domain logic genuinely spans multiple entities and doesn't fit naturally as a method on any single one — forcing it onto one entity anyway produces an awkward, misleading API (e.g. an `Account.transferTo(otherAccount, amount)` method that has to reach into a second aggregate it shouldn't own). A domain service expresses that logic as a first-class, stateless operation named with a verb from the ubiquitous language.

**Worked example — banking.** A `FundsTransferService` domain service coordinates a transfer between two `Account` aggregates — withdrawing from one, depositing to the other, and (per `implementing-ddd/04`'s "one aggregate per transaction" rule) doing so via two separate transactional operations coordinated through domain events rather than a single method mutating both aggregates directly:

```
class FundsTransferService {
    void transfer(Account from, Account to, Money amount) {
        from.withdraw(amount); // raises MoneyWithdrawn domain event
        to.deposit(amount);    // raises MoneyDeposited domain event, consumed asynchronously
    }
}
```
The danger Vernon flags: domain services are easy to overuse as a dumping ground for logic that's too lazy to place correctly. If a piece of logic legitimately concerns a single entity or value object's own data, it belongs *on* that object, not extracted into a service — a `FundsTransferService.calculateInterest(account)` that only touches `account`'s own fields should be `account.calculateInterest()` instead. This distinguishes a *domain service* (stateless coordination logic in the model layer, expressed in the ubiquitous language) from an *application service* (`implementing-ddd/09`), which orchestrates use cases, transactions, and infrastructure — a common and costly confusion.

### Modules: organize by domain meaning, not technical layer
A module (package/namespace) should group things a domain expert would recognize as belonging together — `discussion` containing `Discussion`, `DiscussionId`, `Comment`, `DiscussionRepository` — rather than grouping by technical role (`entities/`, `repositories/`, `services/` at the top level, each containing pieces of every unrelated concept mixed together). Layer-first organization forces a reader to jump across five folders to understand one concept; concept-first organization keeps everything about `Discussion` in one place, with technical role as a sub-detail.

## Pros
- Clear entity/value-object/service boundaries prevent the two most common tactical bugs: identity-based objects compared by value (subtle equality bugs) and value-like objects treated as mutable shared state (spooky-action-at-a-distance bugs when one reference is mutated and every holder of that reference sees the change).
- Value objects push validation to construction time, making illegal states genuinely unrepresentable rather than merely "checked for" at scattered call sites.
- Domain-meaning-first module organization keeps a bounded context's code navigable as it grows, and makes bounded context extraction (splitting a module into its own service later) far less disruptive than untangling a layer-first structure would be.

## Cons
- Overusing value objects for genuinely trivial fields (wrapping every string in a single-field class) adds ceremony without proportional benefit — judgment is needed about which primitives actually carry domain rules worth enforcing.
- Domain services are easy to misuse as an escape hatch for logic that's inconvenient to place correctly, quietly draining behavior out of entities and value objects until the model degrades into an anemic domain model (data-only entities orbited by service classes doing all the work) — the exact anti-pattern DDD's tactical patterns exist to prevent.
- Getting module boundaries wrong early (organizing by layer out of habit, especially in teams coming from a framework-first, MVC-flavored background) is a structural decision that's expensive to unwind once a codebase has grown around it.

## Alternatives
- **Anemic domain model** — entities as plain data holders (getters/setters only), all logic in service classes; simpler to reason about for CRUD-shaped subdomains (see `implementing-ddd/01`'s "supporting/generic subdomain" guidance) but actively harmful for a core domain, since it defeats the entire purpose of rich tactical modeling.
- **Functional-core, imperative-shell** — model domain logic as pure functions over immutable data (a natural fit with value objects) rather than as methods on mutable entity objects; popular in functional languages and increasingly in typed functional-adjacent styles within OO languages, trading entity-style mutation for explicit state-transition functions.
- **ORM-driven modeling** — let the persistence framework's entity conventions (JPA `@Entity`, ActiveRecord) dictate the object model directly; faster to start for CRUD-heavy systems, but tends to erode the entity/value-object distinction because ORMs are historically weak at representing value objects as first-class immutable types (see `implementing-ddd/08`).

## When to use it
Any time you're modeling a core domain (per `implementing-ddd/01`'s distillation) with real behavioral rules — reach for entities where identity and lifecycle matter, value objects wherever a concept is fully described by its attributes, domain services only when logic genuinely spans objects, and concept-first modules from day one.

## When NOT to use it
For a generic or thin supporting subdomain with no real behavioral complexity, the full ceremony (wrapping every field in a value object, agonizing over entity-vs-service placement) is wasted effort — a simpler, more CRUD-shaped design is appropriate there, consistent with the distillation principle from `implementing-ddd/01`.

## Key takeaways / mental model
Ask three questions of any new domain concept: "does it need a stable identity across time, or is it fully described by its current values?" (entity vs. value object); "if it's behavior, does it belong to exactly one entity's own data, or does it span several?" (entity method vs. domain service); "does this file belong next to the other things a domain expert would mention in the same breath?" (module organization).

## Self-check questions
1. Take a `User` concept from a system you know. Which of its data belongs on the entity itself, and which pieces are better modeled as value objects (e.g. an email address, a shipping address)? Justify with the identity-vs-value distinction.
2. Give an example of logic that was placed on an entity but should have been a domain service, and one that was placed in a domain service but should have been on an entity. What symptom revealed the misplacement?
3. Why does structural (attribute) equality matter for value objects specifically, and why would that same equality rule be a bug if applied to an entity?
4. Describe how you'd reorganize a layer-first codebase (`controllers/`, `services/`, `models/`) into concept-first modules, and name one risk in doing that migration on a live codebase.

## References
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 5: "Entities".
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 6: "Value Objects".
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 7: "Services".
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 9: "Modules".
