---
id: enterprise-patterns/09
subject: enterprise-patterns
title: "Object-Relational Structural Mapping (Inheritance)"
slug: or-structural-mapping
status: drafted
mastery:
seniority: senior
source: Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 12
prerequisites: [enterprise-patterns/06]
created: 2026-08-10
updated: 2026-08-10
---

# Object-Relational Structural Mapping (Inheritance)

## TL;DR
Relational tables have no native concept of inheritance, so mapping an object-oriented inheritance hierarchy (a `Payment` base class with `CreditCardPayment` and `BankTransferPayment` subclasses) onto tables requires choosing among three specific strategies, each with a real trade-off: Single Table Inheritance (one table, nullable columns for subclass-specific fields), Class Table Inheritance (one table per class, joined by a shared key), and Concrete Table Inheritance (one table per concrete class, with shared fields duplicated across each).

## The idea
This is one of the most concrete, technically detailed "impedance mismatch" problems between object-oriented design and relational storage — a direct consequence of choosing Domain Model (`enterprise-patterns/02`) with genuine inheritance hierarchies, then needing Data Mapper (`enterprise-patterns/06`) to persist that hierarchy. Relational databases model flat rows in tables; OO inheritance models a hierarchy of increasingly specific types — reconciling these two fundamentally different shapes requires a deliberate choice, and each of the three standard choices trades off differently between simplicity, storage efficiency, and query performance.

## How it works

### Single Table Inheritance — one table, nullable columns for everything
Every class in the hierarchy shares one table, with a column for every field any subclass might need, most of which are `NULL` for rows that don't apply to that particular subclass, plus a discriminator column identifying which concrete subclass each row represents.

```sql
CREATE TABLE payments (
    id INT, amount DECIMAL, payment_type VARCHAR,   -- discriminator column
    card_number VARCHAR NULL,      -- only used when payment_type = 'credit_card'
    bank_account VARCHAR NULL      -- only used when payment_type = 'bank_transfer'
);
```
**Trade-off**: simplest possible schema, and querying across the whole hierarchy (e.g., "total amount across all payment types") requires no joins at all — but the table accumulates many `NULL` columns as the hierarchy grows, wastes storage on unused columns per row, and offers no database-level constraint preventing a `bank_transfer` row from having a `card_number` value by mistake (that validation has to live entirely in application code).

### Class Table Inheritance — one table per class, joined by a shared key
Each class in the hierarchy (including the base class) gets its own table, holding only the fields specific to that level, joined together via a shared primary key.

```sql
CREATE TABLE payments (id INT, amount DECIMAL);                          -- base class fields
CREATE TABLE credit_card_payments (payment_id INT, card_number VARCHAR); -- subclass-specific fields
CREATE TABLE bank_transfer_payments (payment_id INT, bank_account VARCHAR);
```
**Trade-off**: no wasted `NULL` columns, and the schema directly mirrors the OO hierarchy's actual structure — but retrieving a full `CreditCardPayment` object requires a join across two tables (`payments` and `credit_card_payments`), and querying across the whole hierarchy for a base-class field is straightforward (query `payments` alone), while querying for a subclass-specific field across the whole hierarchy requires joining in the relevant subclass table specifically.

### Concrete Table Inheritance — one table per concrete class, no sharing
Each concrete (instantiable, leaf-level) class gets its own table containing *all* its fields, including ones inherited from the base class — no shared base table at all, meaning base-class fields are duplicated across every concrete subclass's table.

```sql
CREATE TABLE credit_card_payments (id INT, amount DECIMAL, card_number VARCHAR);
CREATE TABLE bank_transfer_payments (id INT, amount DECIMAL, bank_account VARCHAR);
```
**Trade-off**: retrieving a specific concrete object needs no join at all (fastest single-object read) — but querying across the *whole* hierarchy (e.g., "total amount across all payment types") requires a `UNION` across every concrete table, and any change to a base-class field requires modifying every concrete table's schema, since there's no single shared table holding it once.

### Choosing among the three — the actual deciding factors
- **How deep and stable is the hierarchy?** A shallow, stable hierarchy (few subclasses, rarely changing) tolerates Single Table Inheritance's `NULL`-column cost reasonably well; a deep or frequently-changing hierarchy accumulates unmanageable numbers of nullable columns under that strategy.
- **How often do you query across the whole hierarchy versus a specific subclass?** Frequent whole-hierarchy queries favor Single Table Inheritance (no joins/unions needed) or Class Table Inheritance (simple base-table-only queries for base-class fields); frequent specific-subclass queries favor Concrete Table Inheritance (no join needed to get a full concrete object).
- **How much do subclasses actually diverge in their fields?** Subclasses sharing most fields, differing only slightly, tolerate Single Table Inheritance's shared-table approach well; subclasses with substantially different, largely non-overlapping fields make Single Table Inheritance's wasted-`NULL`-columns problem worse, favoring Class or Concrete Table Inheritance instead.

**Worked example of the trade-off in practice.** A payment system with just two payment types, rarely changing, where most reports need totals across *all* payment types (rarely needing type-specific fields): Single Table Inheritance is likely the pragmatic choice — the modest `NULL`-column waste is a small price for avoiding joins on the frequent, whole-hierarchy queries. A more complex system with ten increasingly divergent payment subtypes, each with substantially different fields, and frequent type-specific reporting: Class Table Inheritance likely offers the better balance, avoiding Single Table Inheritance's excessive nullable-column sprawl while still allowing efficient base-class-only queries.

## Pros
- Naming the three specific strategies gives a precise vocabulary for a decision that's otherwise easy to make unconsciously (defaulting to whatever an ORM happens to pick) without understanding the trade-off actually being made.
- Each strategy is a genuinely reasonable choice under the right circumstances — there's no universally "best" one, only a best fit for a specific hierarchy's shape and query patterns.
- Understanding these strategies explains a specific, common ORM configuration decision (most ORMs let you choose among these three explicitly) that would otherwise seem like arbitrary framework configuration.

## Cons
- Single Table Inheritance's `NULL`-column accumulation can become a genuine storage and clarity problem for deep, divergent hierarchies.
- Class Table Inheritance's joins add real query complexity and performance cost, especially for hierarchies queried very frequently.
- Concrete Table Inheritance's duplicated base-class fields across every concrete table create a real DRY violation (`pragmatic-programmer/03`) at the schema level, requiring coordinated changes across multiple tables whenever a base-class field changes.

## Alternatives
- **Avoiding OO inheritance in the domain model entirely**, using composition instead (echoing `design-patterns/02`'s general preference) — sidesteps the entire object-relational inheritance mapping problem by not having an inheritance hierarchy to map in the first place.
- **Document/NoSQL storage** (see `data-engineering/seven-databases`) — some document databases handle heterogeneous, hierarchy-like data more naturally than relational tables, sidestepping this specific impedance mismatch at the cost of different trade-offs elsewhere.
- **A mature ORM's built-in inheritance-mapping configuration** — most ORMs (Hibernate, SQLAlchemy, Entity Framework) support all three strategies as configuration options, letting a team choose deliberately without hand-writing the mapping/query logic for whichever strategy they pick.

## When to use it
Use Single Table Inheritance for shallow, stable, field-similar hierarchies queried frequently as a whole. Use Class Table Inheritance for hierarchies with substantially divergent subclass fields, where the schema clarity benefit outweighs the join cost. Use Concrete Table Inheritance when subclass-specific queries dominate and cross-hierarchy queries are rare.

## When NOT to use it
Don't default to whichever strategy an ORM happens to pick without deliberately considering your hierarchy's actual shape and query patterns — the choice has real, lasting performance and schema-clarity consequences. Don't force an OO inheritance hierarchy (and its corresponding mapping complexity) onto a domain that could be modeled more simply with composition instead.

## Key takeaways / mental model
For any inheritance hierarchy you need to persist, ask: "how deep and divergent is this hierarchy, and do I query it more often as a whole or by specific subtype?" Let the answer point you toward Single Table (shallow, similar, whole-hierarchy queries), Class Table (divergent, mixed queries), or Concrete Table (subtype-specific queries dominate) Inheritance.

## Self-check questions
1. Using the payment-hierarchy example, explain the specific trade-off each of the three strategies makes, in terms of storage waste, join/union cost, and schema-change coordination.
2. Given a hierarchy with 15 increasingly divergent subclasses, queried mostly by specific subtype, which strategy would you choose, and why?
3. Why does Concrete Table Inheritance create a schema-level DRY violation, and what practical problem does that cause when a base-class field needs to change?
4. Describe a hierarchy from your own domain and walk through which of the three strategies best fits its actual shape and query patterns.

## References
- Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 12: "Object-Relational Structural Patterns" (Single Table, Class Table, and Concrete Table Inheritance sections).
