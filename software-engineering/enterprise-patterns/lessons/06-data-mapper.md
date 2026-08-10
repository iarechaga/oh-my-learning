---
id: enterprise-patterns/06
subject: enterprise-patterns
title: Data Mapper
slug: data-mapper
status: drafted
mastery:
seniority: senior
source: Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 10
prerequisites: [enterprise-patterns/05, clean-architecture/11]
created: 2026-08-10
updated: 2026-08-10
---

# Data Mapper

## TL;DR
Data Mapper is a separate layer of code whose only job is translating between a domain object (which knows nothing about the database) and the database's own tabular representation — the exact, fuller-strength realization of `clean-architecture/11`'s "the database is a detail" principle, at the cost of a substantial mapping layer Active Record avoids by not separating these concerns in the first place.

## The idea
`enterprise-patterns/05` established Active Record's pragmatic merge of business logic and persistence; Data Mapper is the alternative for when that merge's cost (coupling domain objects to the database schema, SRP violations as logic grows) outweighs its benefit (less code). Data Mapper's core discipline: **domain objects have zero knowledge that a database exists at all** — no `save()` method, no knowledge of table names or columns, nothing. A completely separate set of Mapper objects handles the entire translation in both directions.

## How it works

### The structure — domain objects are pure, mappers do all the translation
```
class Customer:                            # pure domain object — NO database awareness whatsoever
    def __init__(self, name, credit_limit, is_vip):
        self.name, self.credit_limit, self.is_vip = name, credit_limit, is_vip
    def discount_rate(self):
        return 0.1 if self.is_vip else 0

class CustomerMapper:                       # ALL persistence knowledge lives here, separately
    def find(self, id) -> Customer:
        row = db.query("SELECT * FROM customers WHERE id = ?", id)
        return Customer(row["name"], row["credit_limit"], row["is_vip"])
    def save(self, customer: Customer, id):
        db.execute("UPDATE customers SET name=?, credit_limit=?, is_vip=? WHERE id=?",
                   customer.name, customer.credit_limit, customer.is_vip, id)
```
`Customer` here is precisely `clean-architecture/07`'s Entity — a plain object expressing only business concepts, with zero coupling to any specific storage mechanism. `CustomerMapper` holds all the SQL and all the translation logic between `Customer`'s in-memory shape and the `customers` table's actual columns — if the database schema changes (a column renamed, a new normalization), only `CustomerMapper` needs to change; `Customer` and every piece of business logic that uses it remain completely untouched.

### Why this separation earns its cost specifically for complex domain models
The value of this full separation compounds specifically as the domain model gets richer: a `Customer` with many relationships (orders, addresses, a wishlist), inheritance hierarchies (`enterprise-patterns/09`), and business logic that spans many linked objects benefits enormously from being able to evolve its *in-memory* object structure independently of the *database* structure — the object graph can be shaped purely around what makes business sense (deeply nested, richly linked, following domain concepts) while the database schema stays shaped around what makes storage/query sense (normalized tables, foreign keys, indexes) — and the Mapper layer absorbs the entire cost of reconciling these two, often quite different, shapes.

**Worked example of a shape mismatch Data Mapper handles cleanly.** A `Customer` domain object might have `customer.orders` as a simple, navigable list of `Order` objects — a natural, business-meaningful representation. The database, meanwhile, stores orders in a separate `orders` table with a `customer_id` foreign key, and querying "all orders for this customer" requires a specific SQL join or a separate query entirely. `CustomerMapper` (or a closely related `OrderMapper`) absorbs this translation — `customer.orders` remains simple and natural in the domain model, while all the actual SQL join/query complexity needed to populate it lives entirely inside the mapping layer, never leaking into `Customer` itself or into any business logic that navigates `customer.orders`.

### Data Mapper typically works alongside Unit of Work and Identity Map
Data Mapper rarely stands entirely alone in a real system — it's commonly paired with **Unit of Work** (`enterprise-patterns/07`, tracking which objects have changed and need saving) and **Identity Map** (`enterprise-patterns/08`, ensuring the same database row always maps to the same in-memory object instance) — both of which become necessary specifically *because* Data Mapper's separation means there's no longer a single object (as in Active Record) whose `save()` method you can just call directly; something else needs to track what's changed and coordinate saving it, and something needs to prevent loading the same row into two different, inconsistently-updated object instances.

### The cost, honestly assessed
The mapping layer's cost is real and substantial: for every domain object type, you're writing (or generating, via an ORM) a corresponding Mapper with the full translation logic in both directions — for a large domain model, this is a significant amount of code, even though each individual piece is conceptually simple. This is precisely the cost `enterprise-patterns/05`'s Active Record deliberately avoids paying, and precisely why Data Mapper is worth its cost specifically once the domain model's complexity has grown enough that Active Record's merge starts to strain (per that lesson's specific strain signals).

## Pros
- Domain objects remain completely free of persistence knowledge, fully satisfying `clean-architecture/11`'s "the database is a detail" principle and making business logic trivially unit-testable with zero database involvement.
- Lets the in-memory object graph and the database schema evolve independently, each shaped for its own purposes (business meaning versus storage/query efficiency) rather than being forced to match each other.
- Concentrates all schema-mapping knowledge in one well-defined layer, so a schema change touches only the relevant Mappers, never the domain objects or business logic built on top of them.

## Cons
- Substantially more code than Active Record for the same domain, even before accounting for the additional Unit of Work and Identity Map machinery that typically accompanies it.
- Requires real design discipline and skill to get the domain-to-schema mapping right, especially for complex relationships and inheritance hierarchies (`enterprise-patterns/09`-`10`).
- For a genuinely simple domain, this pattern's separation provides little benefit relative to its substantial cost — precisely the case where Active Record is the more proportionate choice.

## Alternatives
- **Active Record** (`enterprise-patterns/05`) — the simpler, merged alternative, appropriate for genuinely simple domains where the mapping layer's cost isn't justified.
- **A mature ORM implementing Data Mapper** (Hibernate, SQLAlchemy's classical mapping mode, Doctrine) — automates the bulk of the mapping code this pattern would otherwise require hand-writing, letting a team gain Data Mapper's separation benefit without hand-maintaining every individual Mapper class.
- **Table Module** (`enterprise-patterns/03`) with a Table Data Gateway (`enterprise-patterns/04`) — sidesteps the whole Active-Record-versus-Data-Mapper question by not using individually-instantiated domain objects at all.

## When to use it
Use Data Mapper once a domain model's complexity, richness of relationships, or divergence between natural object shape and natural storage shape has grown enough that Active Record's merged structure would strain — or whenever `clean-architecture/11`'s full database-independence guarantee is a genuine, evidenced architectural requirement (e.g., a credible plan to support multiple database backends).

## When NOT to use it
Don't build a full, hand-written Data Mapper layer for a simple domain that maps naturally onto its database tables — that's the case Active Record handles with far less code and complexity. Prefer a mature ORM's built-in mapping capabilities over hand-rolling Data Mapper from scratch unless you have a genuinely unusual mapping need an ORM doesn't handle well.

## Key takeaways / mental model
Ask: "does my domain object's natural, business-meaningful shape genuinely diverge from what makes sense for storage, and is that divergence significant enough to justify a full translation layer?" If yes, Data Mapper's cost is worth paying. If the domain's shape and the database's shape are naturally close, that divergence-driven cost isn't there to justify, and Active Record remains the simpler, more proportionate choice.

## Self-check questions
1. Using the `Customer`/`CustomerMapper` example, explain precisely what knowledge lives in the Mapper that Active Record would instead put directly on the domain object.
2. Describe the `customer.orders` example, and explain what specific translation complexity the Mapper layer absorbs that would otherwise leak into the domain object or business logic.
3. Why does Data Mapper typically require Unit of Work and Identity Map as companions, when Active Record doesn't need them in the same way?
4. Given a domain you're familiar with, assess whether its natural object shape diverges enough from its natural storage shape to justify Data Mapper's cost, or whether Active Record would be more proportionate.

## References
- Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 10: "Data Source Architectural Patterns" (Data Mapper section).
- See also: `clean-architecture/11` (The Database and the Web Are Details) for the architectural principle this pattern most fully realizes.
