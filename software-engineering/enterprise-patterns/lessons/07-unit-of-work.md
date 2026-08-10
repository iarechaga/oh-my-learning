---
id: enterprise-patterns/07
subject: enterprise-patterns
title: Unit of Work
slug: unit-of-work
status: drafted
mastery:
seniority: senior
source: Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 11
prerequisites: [enterprise-patterns/06]
created: 2026-08-10
updated: 2026-08-10
---

# Unit of Work

## TL;DR
A Unit of Work tracks every object that's been read, created, modified, or deleted during one logical business transaction, then commits all the necessary database changes together, in one coordinated batch, at the end — solving the specific problem Data Mapper's separation creates: once domain objects can no longer just call their own `save()` (as Active Record's could), *something* needs to know which objects actually changed and need persisting.

## The idea
`enterprise-patterns/06` noted that Data Mapper typically requires a companion pattern to track changes, since domain objects themselves no longer carry a `save()` method. Unit of Work is that companion: a single object, scoped to one business transaction (a request, a use case execution), that acts as the coordinator — every domain object touched during that transaction registers itself with the Unit of Work, and at the end, the Unit of Work figures out exactly what SQL needs to run, in what order, to make the database consistent with all the changes that happened, and executes it as a single coordinated commit.

## How it works

### Tracking three kinds of changes
A Unit of Work maintains three lists during a transaction: **new** objects (to be inserted), **dirty** objects (already existing, but modified, to be updated), and **removed** objects (to be deleted). As business logic runs, objects register themselves into the appropriate list — often via a mechanism where the domain object or its Mapper calls something like `unit_of_work.register_dirty(customer)` whenever a change happens.

**Worked example.**
```
class UnitOfWork:
    def __init__(self):
        self.new_objects, self.dirty_objects, self.removed_objects = [], [], []
    def register_new(self, obj): self.new_objects.append(obj)
    def register_dirty(self, obj):
        if obj not in self.dirty_objects: self.dirty_objects.append(obj)
    def register_removed(self, obj): self.removed_objects.append(obj)
    def commit(self):
        for obj in self.new_objects: mapper_for(obj).insert(obj)
        for obj in self.dirty_objects: mapper_for(obj).update(obj)
        for obj in self.removed_objects: mapper_for(obj).delete(obj)

# during a business transaction:
uow = UnitOfWork()
customer = customer_mapper.find(id, uow)     # loaded, tracked
customer.apply_discount()                     # a business operation that changes state
uow.register_dirty(customer)                  # explicitly marked as changed
new_order = Order(customer, items)
uow.register_new(new_order)                   # a newly-created object

uow.commit()                                   # ONE coordinated set of SQL statements, at the end
```
Business logic (`apply_discount()`, creating `new_order`) proceeds without immediately triggering any database writes — those are deferred and batched until `commit()`, at which point the Unit of Work knows the complete, final set of changes needed and can execute them together, in the correct order, as a single database transaction.

### Why batching commits at the end matters
Without a Unit of Work, each individual change (a discount applied, a new order created) might trigger its own immediate, separate database write — multiplying round trips to the database and, worse, risking an inconsistent database state if the business transaction fails partway through (some changes committed, others not, with no coordinated rollback). Batching everything into one `commit()`, wrapped in a single database transaction, ensures **all-or-nothing** consistency — either every change from this business transaction succeeds together, or (if something fails) the database transaction rolls back and none of them take effect, directly connecting to `architecture/ddia`'s treatment of transactional atomicity.

### Determining commit order — a subtler responsibility
A Unit of Work's `commit()` can't simply execute inserts, updates, and deletes in arbitrary order — foreign-key constraints often require a specific sequence (a `Customer` must be inserted before an `Order` referencing that customer's ID can be inserted). Sophisticated Unit of Work implementations compute a correct ordering based on the actual dependency relationships between the registered objects, rather than relying on registration order alone — a genuinely nontrivial piece of logic that most hand-rolled implementations either simplify (relying on careful, correct registration order) or delegate to database-level deferred constraint checking.

### Unit of Work as (usually) an implicit, framework-provided concept in modern practice
Most developers today don't hand-write a `UnitOfWork` class explicitly — this pattern's core idea is what a typical ORM's "session" or "context" object (SQLAlchemy's `Session`, Hibernate's `Session`, Entity Framework's `DbContext`) actually *is* under the hood: an object you load and modify domain objects through, which silently tracks what's changed, and which you eventually call `.commit()` or `.save_changes()` on to flush all accumulated changes together. Recognizing this connects directly practical, everyday ORM usage back to the underlying pattern this lesson names explicitly.

## Pros
- Batches all of a business transaction's database changes into one coordinated commit, providing atomicity (all-or-nothing consistency) and reducing the number of separate round trips to the database.
- Decouples business logic from immediately triggering database writes, letting business logic proceed and be tested without needing every intermediate state to be separately persisted.
- Explains and demystifies what a mainstream ORM's "session"/"context" object is actually doing internally, deepening practical understanding of tools most developers already use daily.

## Cons
- Computing a correct commit order for interdependent objects (respecting foreign-key constraints) is a genuinely nontrivial responsibility that naive hand-rolled implementations can get wrong.
- Deferred writes mean bugs related to persistence (a constraint violation, a duplicate key) surface only at `commit()` time, potentially far from the business-logic code that actually caused the problem — a version of `pragmatic-programmer/08`'s "the further a bug travels from its source, the harder to diagnose" concern.
- Adds a layer of tracking machinery that's pure overhead for a genuinely simple, single-object-per-transaction use case where a direct save would be equally correct and much simpler.

## Alternatives
- **Direct, immediate saves per operation** (as Active Record naturally does, `enterprise-patterns/05`) — simpler for genuinely simple, single-object transactions, at the cost of losing Unit of Work's batched atomicity guarantee for transactions spanning multiple objects.
- **Database-level transaction management alone**, with explicit, manually-sequenced save calls inside a transaction block — achieves similar atomicity without a formal change-tracking object, at the cost of requiring the developer to manually track and correctly sequence every save call themselves.
- **Event sourcing** (see `architecture/microservices-patterns`) — a fundamentally different approach to tracking and persisting changes, recording a sequence of domain events rather than tracking and diffing object state, appropriate for systems needing a full audit history of every change.

## When to use it
Use Unit of Work whenever a single business transaction involves changes to multiple objects that must succeed or fail together, especially when paired with Data Mapper (`enterprise-patterns/06`) where no individual domain object has its own `save()` method to call directly.

## When NOT to use it
Don't hand-roll a Unit of Work when your ORM's existing session/context object already provides this capability — reserve custom implementation for genuinely unusual persistence needs an ORM doesn't handle well. Don't introduce this pattern's tracking overhead for genuinely simple, single-object transactions where Active Record's direct-save approach is equally correct and simpler.

## Key takeaways / mental model
Ask, for any business transaction: "does this involve changes to multiple objects that need to succeed or fail together?" If yes, a Unit of Work (explicit or, more commonly, your ORM's session object) is what coordinates that atomicity — business logic registers changes as they happen, and one final commit makes them all real together.

## Self-check questions
1. Using the `UnitOfWork` example, explain what would go wrong (in terms of consistency) if `apply_discount()` and creating `new_order` each triggered an immediate, separate database write instead of being batched.
2. Why does determining commit order matter, and what specific database constraint would be violated by committing in the wrong order?
3. Identify the "Unit of Work" in an ORM you've used (SQLAlchemy's Session, Django's transaction management, etc.) and describe how its behavior matches this pattern's description.
4. Describe a case where deferred writes (via Unit of Work) made a persistence bug harder to diagnose than it would have been with immediate, per-operation saves.

## References
- Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 11: "Object-Relational Behavioral Patterns" (Unit of Work section).
