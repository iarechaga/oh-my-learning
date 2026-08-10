---
id: enterprise-patterns/04
subject: enterprise-patterns
title: "Data Source: Row Data Gateway and Table Data Gateway"
slug: data-source-gateways
status: drafted
mastery:
seniority: senior
source: Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 10
prerequisites: [enterprise-patterns/01, clean-code/08]
created: 2026-08-10
updated: 2026-08-10
---

# Data Source: Row Data Gateway and Table Data Gateway

## TL;DR
A Gateway is an object that wraps access to an external resource (most commonly a database) behind a plain, purpose-built interface — the enterprise-patterns-specific instance of `clean-code/08`'s general boundary-wrapping principle. Row Data Gateway gives one object per database row, exposing just that row's columns as fields/properties, with no business logic. Table Data Gateway gives one object per table, holding all the SQL for that table's CRUD operations, shared across every row.

## The idea
Once you've decided how to organize domain logic (`enterprise-patterns/02`-`03`), you still need to decide how the Data Source layer (`enterprise-patterns/01`) itself is structured — specifically, how SQL and database access get wrapped so the rest of the system doesn't need to write raw SQL scattered throughout. Both patterns in this lesson are **Gateways** in Fowler's specific sense: simple, single-purpose wrapper objects with no business logic of their own, purely translating between "the shape the database wants" and "a plain object/structure the rest of the code can use" — directly `clean-code/08`'s boundary-wrapping principle, specialized for database access specifically.

## How it works

### Row Data Gateway — one object instance per database row
Exactly one Gateway instance corresponds to exactly one row, exposing that row's columns as simple properties, plus basic `insert`/`update`/`delete` operations for that specific row — but critically, **no business logic** lives here; it's purely a data-access wrapper, deliberately kept "dumb."

**Worked example.**
```
class CustomerGateway:                 # one instance per customer row
    def __init__(self, id, name, credit_limit):
        self.id, self.name, self.credit_limit = id, name, credit_limit
    @staticmethod
    def find(id):
        row = db.query("SELECT * FROM customers WHERE id = ?", id)
        return CustomerGateway(row["id"], row["name"], row["credit_limit"])
    def update(self):
        db.execute("UPDATE customers SET name=?, credit_limit=? WHERE id=?",
                   self.name, self.credit_limit, self.id)
```
This looks superficially similar to a Domain Model object, but the key distinguishing feature is the *absence* of business logic — `CustomerGateway` has no `discount_rate()` method, no business rules at all; it's purely a data-access convenience wrapping one row, meant to be *used by* a separate Domain Model layer (or Transaction Script procedures) that adds the actual business logic on top, keeping the "translate to/from SQL" concern cleanly separated from "apply business rules."

### Table Data Gateway — one object per table, not per row
Rather than one instance per row, Table Data Gateway has a *single* object (often effectively a singleton in practice, though not necessarily using the `design-patterns/05` Singleton pattern specifically) responsible for all CRUD SQL related to one table, taking and returning simple data structures (dictionaries, DTOs, or a result set) rather than individually-instantiated per-row objects.

**Worked example.**
```
class CustomerTableGateway:            # ONE instance, handles ALL customer rows
    def find(self, id) -> dict:
        return db.query("SELECT * FROM customers WHERE id = ?", id)
    def find_all_vip(self) -> list[dict]:
        return db.query("SELECT * FROM customers WHERE is_vip = 1")
    def update(self, id, name, credit_limit):
        db.execute("UPDATE customers SET name=?, credit_limit=? WHERE id=?", name, credit_limit, id)
```
This fits especially naturally alongside Table Module (`enterprise-patterns/03`), since both are already organized around "the whole table" rather than "an individual row" — a `CustomerTableModule` and a `CustomerTableGateway` pair naturally, one holding table-oriented business logic, the other holding table-oriented SQL.

### Choosing between the two — matching the Gateway to the domain-logic pattern
This is the direct data-access counterpart to `enterprise-patterns/02`-`03`'s domain-logic choice: **Row Data Gateway pairs naturally with Domain Model** (one row-wrapper instance feeding one domain object instance, echoing the same "one object per real-world thing" granularity), while **Table Data Gateway pairs naturally with Table Module or Transaction Script** (both of which think in terms of whole tables or whole transactions, not individual per-row objects). Choosing a Gateway pattern that mismatches your domain-logic pattern (e.g., pairing Table Data Gateway with a rich Domain Model) works, but produces friction — you'd be constantly converting between the Gateway's table-shaped dictionaries and your domain objects' individual instances, an unnecessary translation cost the matched pairing avoids.

### Both Gateways keep SQL out of the rest of the codebase
The shared, essential value of both patterns, regardless of which one you pick: raw SQL strings live in exactly one place per table (inside that table's Gateway), rather than scattered across every piece of code that happens to need that table's data. This is directly `pragmatic-programmer/03`'s DRY principle and `clean-code/08`'s boundary-wrapping applied specifically to SQL — a schema change (a renamed column, a new constraint) requires updating exactly one Gateway class, not hunting down every scattered raw-SQL query string across the codebase.

## Pros
- Both patterns concentrate all SQL for a given table into one well-defined place, eliminating scattered raw-SQL strings throughout the rest of the codebase.
- Row Data Gateway's clean separation from business logic keeps data-access code simple, dumb, and easy to verify by inspection — echoing `clean-architecture/09`'s Humble Object pattern applied to the data-access boundary.
- Table Data Gateway's whole-table orientation avoids unnecessary per-row object instantiation overhead for logic that's naturally table/batch-shaped.

## Cons
- Row Data Gateway, applied to a system with a genuinely large number of distinct entity types, means writing (or generating) a lot of nearly-identical boilerplate Gateway classes, one per table.
- Table Data Gateway's dictionary/result-set-shaped return values are less type-safe and less self-documenting than Row Data Gateway's or Domain Model's proper objects, pushing more responsibility onto callers to know which keys/columns exist.
- Hand-writing either pattern for a large schema is tedious and error-prone relative to using an existing ORM that automates much of this — which is precisely why most modern development reaches for a mature ORM rather than hand-rolling these patterns from scratch (though understanding them explains what the ORM is actually doing underneath).

## Alternatives
- **Active Record** (`enterprise-patterns/05`) — merges the Gateway and the domain object into a single class, adding business logic directly to what would otherwise be a pure Row Data Gateway — a deliberate simplification trading Data-Source/Domain separation for less code and less mapping ceremony.
- **Data Mapper** (`enterprise-patterns/06`) — a more sophisticated alternative specifically for pairing with a rich Domain Model, handling the full complexity of mapping a genuinely object-graph-shaped domain onto relational tables, beyond what a simple Row/Table Gateway alone can cleanly manage.
- **A mature, off-the-shelf ORM** (Hibernate, SQLAlchemy, ActiveRecord-the-library, Entity Framework) — automates the mechanical generation of Gateway-like or Data-Mapper-like code, letting a team benefit from these patterns' underlying ideas without hand-writing every table's Gateway class manually.

## When to use it
Use Row Data Gateway when pairing with a Domain Model that needs one object per real-world entity instance. Use Table Data Gateway when pairing with Table Module or Transaction Script, where whole-table, batch-oriented operations are the natural shape of the work.

## When NOT to use it
Don't hand-write either pattern for a large, evolving schema when a mature ORM would automate the same underlying idea far more reliably and with less ongoing maintenance burden — reserve hand-written Gateways for cases with genuinely unusual data-access needs an ORM doesn't handle well, or for learning/understanding what an ORM does underneath.

## Key takeaways / mental model
Match your Gateway pattern to your domain-logic pattern: per-row objects (Row Data Gateway) for Domain Model, whole-table operations (Table Data Gateway) for Table Module or Transaction Script. Either way, the goal is the same: concentrate all of one table's SQL into exactly one place, kept free of business logic.

## Self-check questions
1. Using the `CustomerGateway` example, explain why it deliberately contains no business logic, and where that logic should live instead.
2. Explain why Table Data Gateway pairs naturally with Table Module but would create friction if paired with a rich Domain Model.
3. Describe what happens to a codebase's SQL organization if Gateways are NOT used and raw SQL is instead written wherever it's needed. What specific problem does concentrating it into Gateways solve?
4. Why do most modern teams use a mature ORM rather than hand-writing these patterns, and what do you still gain from understanding them even when using an ORM?

## References
- Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 10: "Data Source Architectural Patterns" (Row Data Gateway and Table Data Gateway sections).
