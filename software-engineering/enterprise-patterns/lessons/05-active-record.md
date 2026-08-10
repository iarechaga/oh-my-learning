---
id: enterprise-patterns/05
subject: enterprise-patterns
title: Active Record
slug: active-record
status: drafted
mastery:
seniority: mid
source: Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 10
prerequisites: [enterprise-patterns/04, clean-code/06]
created: 2026-08-10
updated: 2026-08-10
---

# Active Record

## TL;DR
Active Record merges Row Data Gateway with domain logic into one class per table — an object that both holds business rules *and* knows how to save and load itself from the database. This deliberately sacrifices `clean-architecture/11`'s "the database is a detail" separation for a large reduction in mapping code and conceptual overhead, making it the right, pragmatic choice specifically when domain logic is thin and closely mirrors the database's table structure.

## The idea
`enterprise-patterns/04` presented Row Data Gateway as a pure, business-logic-free data-access wrapper, explicitly meant to be paired with a *separate* Domain Model layer holding the actual business rules. Active Record asks: what if, for many simple domains, that separation isn't actually worth its cost? Active Record's answer: merge the two into a single class — the object *is* both the row-wrapper and the business object simultaneously.

## How it works

### The merged structure
```
class Customer:                          # Active Record: one class, both roles
    def __init__(self, id, name, credit_limit, is_vip):
        self.id, self.name = id, name
        self.credit_limit, self.is_vip = credit_limit, is_vip

    # --- business logic (would live in a separate Domain Model class otherwise) ---
    def discount_rate(self):
        return 0.1 if self.is_vip else 0

    # --- data access (would live in a separate Row Data Gateway otherwise) ---
    @staticmethod
    def find(id):
        row = db.query("SELECT * FROM customers WHERE id = ?", id)
        return Customer(row["id"], row["name"], row["credit_limit"], row["is_vip"])
    def save(self):
        db.execute("UPDATE customers SET name=?, credit_limit=?, is_vip=? WHERE id=?",
                   self.name, self.credit_limit, self.is_vip, self.id)
```
One `Customer` class handles both concerns that `enterprise-patterns/04`'s Row Data Gateway and a separate Domain Model would otherwise split across two classes — a `customer.save()` call and a `customer.discount_rate()` call both operate on the exact same object, with no translation step between "the business object" and "the data-access wrapper" needed at all.

### Why this trade-off is often worth making — and precisely when
The cost this merge accepts is exactly `clean-architecture/11`'s warning: the domain object now knows it's persisted, and its shape is at least loosely bound to the database table's shape (one field per column, roughly). For many real applications — especially ones whose domain logic genuinely is fairly close to CRUD (create, read, update, delete) with relatively simple validation and calculation rules, and relatively little need for a rich, deeply-linked object graph — this cost is small, and the benefit (dramatically less code, no separate mapping layer, no Data Mapper complexity, `enterprise-patterns/06`) is large. This is precisely why Active Record is the pattern underlying most popular, developer-friendly ORMs (Ruby on Rails's ActiveRecord library, Django's ORM, Laravel's Eloquent) — it optimizes for developer productivity on the common case, at the cost of architectural purity that many applications simply don't need.

### Where Active Record starts to strain
As business logic grows more complex — richer validation rules with many interacting conditions, calculations spanning multiple related objects, logic that doesn't map neatly onto "operations on one table's worth of fields" — Active Record objects start accumulating both business logic and persistence concerns in ways that begin violating `clean-code/10`'s cohesion principle (the class now has at least two genuinely distinct reasons to change: a business-rule change and a schema/persistence change, echoing `clean-architecture/03`'s SRP "one actor" test directly). This is the specific signal that a migration toward a separated Domain Model + Data Mapper structure (`enterprise-patterns/06`) is worth considering — not because Active Record is "wrong," but because the domain's complexity has grown past the point where the trade-off it makes remains favorable.

**Worked example of the strain.** A `Customer` Active Record class that starts accumulating: complex multi-tier discount logic depending on order history across several other tables, validation rules requiring cross-referencing several other Active Record objects, and business rules that have nothing to do with any single row's own fields — at this point, the "one class, one table, one business concept" assumption Active Record depends on for its simplicity starts to break down, and the class becomes simultaneously a data-access object *and* an increasingly awkward home for logic that doesn't naturally fit "operations on this row."

### Active Record and testability
A specific, practical cost worth naming explicitly: because Active Record objects know how to persist themselves, testing business logic on an Active Record object can tempt hitting a real (or real-ish, in-memory) database just to construct a valid instance — unless the object's constructor and business methods are carefully kept independent of any actual database call (echoing `legacy-code/08`'s "constructor does too much" testability concern). Disciplined Active Record usage keeps business-logic methods (like `discount_rate()` above) completely free of any database access, so they remain fast, isolated unit-testable, even though the *same class* also has separate methods (`find`, `save`) that do touch the database.

## Pros
- Dramatically reduces the amount of mapping/translation code needed compared to a separated Domain Model + Data Mapper structure, especially valuable for CRUD-heavy applications.
- Lowers the learning curve and conceptual overhead for developers, since there's only one object to think about per business concept, not two (a domain object and a separate persistence wrapper).
- Underlies most popular, productive, developer-friendly ORMs, meaning understanding this pattern explains a huge amount of how mainstream web-application development actually works in practice.

## Cons
- Couples the domain object's shape to the database schema, and couples business logic to persistence — exactly the separation `clean-architecture/11` argues is valuable to maintain, deliberately given up here.
- As business logic complexity grows, Active Record classes risk accumulating multiple, genuinely distinct reasons to change (business rules and persistence structure), violating SRP (`clean-architecture/03`).
- Testing business logic requires discipline to keep it separate from any actual database call, since the same class also holds persistence methods that do touch the database.

## Alternatives
- **Data Mapper** (`enterprise-patterns/06`) — the separated alternative, keeping domain objects completely ignorant of persistence, at the cost of substantially more mapping code and conceptual overhead — the right choice once Active Record's merged structure starts to strain under genuine business-logic complexity.
- **Row Data Gateway plus a separate, thin domain layer** (`enterprise-patterns/04`) — a partial separation, keeping the Gateway's data access pure while still allowing a relatively simple domain layer on top, without the full complexity of a genuine Data Mapper.
- **Table Module** (`enterprise-patterns/03`) — for domains that don't need per-row objects at all, sidestepping the Active-Record-versus-Data-Mapper choice entirely by organizing around whole tables instead.

## When to use it
Use Active Record for applications whose domain logic is relatively close to CRUD, with simple-to-moderate validation and calculation rules that map naturally onto individual rows/tables — the common case for many real-world applications, and the reason most productivity-focused web frameworks default to this pattern.

## When NOT to use it
Don't force Active Record onto a domain with genuinely rich, cross-cutting business logic that doesn't map naturally onto individual rows — once the strain signals from this lesson appear (multi-object validation, logic unrelated to any single row's fields, growing SRP violations), migrate the relevant logic toward a separated Domain Model and Data Mapper instead.

## Key takeaways / mental model
Ask: "is my domain logic simple enough, and close enough to CRUD on individual rows, that merging business rules and persistence into one class costs little and saves a lot?" If yes, Active Record is the pragmatic, productive choice. If business logic complexity is genuinely rich and cross-cutting, the merge's cost outweighs its convenience, and a separated Domain Model is worth its extra structure.

## Self-check questions
1. Using the `Customer` example, identify which methods are "business logic" and which are "data access," and explain why Active Record deliberately doesn't separate them into different classes.
2. Describe the specific strain signal (per this lesson) that would tell you it's time to migrate from Active Record to a separated Domain Model.
3. Why does disciplined Active Record usage require keeping business-logic methods free of direct database calls, even though the same class has other methods that do touch the database?
4. Name a popular ORM/framework you're aware of that implements Active Record, and describe one specific way its conventions reflect this pattern's trade-offs.

## References
- Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 10: "Data Source Architectural Patterns" (Active Record section).
