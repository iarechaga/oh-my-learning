---
id: evolutionary-architectures/06
subject: evolutionary-architectures
title: "Evolutionary Data"
slug: evolutionary-data
status: drafted
mastery: 
seniority: senior
source: "Building Evolutionary Architectures, 2nd ed. (Ford, Parsons, Kua, Sadalage), Chapter 6"
prerequisites: [evolutionary-architectures/05, hard-parts/02]
created: 2026-08-10
updated: 2026-08-10
---

# Evolutionary Data

## TL;DR
Databases need to evolve with the same rigor as application code: versioned, incremental,
reversible schema migrations (typically via the **expand/contract** pattern), applied
through the same kind of pipeline discipline as code changes. A **shared database
between services** is evolvability's single worst enemy — it recreates the tight static
coupling that quantum boundaries (`evolutionary-architectures/05`) exist to avoid, and no
amount of application-layer decoupling can fix a shared-schema problem.

## The idea

### Why data is the hard part of evolution
It's relatively easy to evolve application code: refactor a function, redeploy, and if
something's wrong, roll back to the previous version — the old code simply stops
running. Data doesn't behave this way. A schema change is applied to data that already
exists, was written under the old assumptions, and often can't simply be "rolled back"
without data loss (you can't un-write a NOT NULL constraint's effect on rows that were
already saved without a value, once you drop the column that used to hold the default).

This asymmetry — code is stateless and disposable, data is stateful and precious — is
why the book devotes a full chapter to it and why "evolutionary data" deserves separate
treatment from "evolutionary code." An evolutionary architecture that only thinks about
code structure and ignores schema evolution will hit a wall the first time a data model
needs to change under load, in production, without downtime.

### The core discipline: treat schema changes like code changes
The book's central move is to apply the same practices that make code evolvable to the
database:
- **Version control** — every schema change is a numbered, ordered migration script
  checked into source control, not an ad hoc manual `ALTER TABLE` run by hand against
  production.
- **Incremental, small changes** — one migration does one thing, the same way a good PR
  changes one thing, so each step is reviewable and its blast radius is contained.
- **Automated, repeatable application** — migrations run through the deployment pipeline
  (`evolutionary-architectures/04`), the same way code does, not through a manual runbook
  a human executes by hand (error-prone, unrepeatable, and impossible to fitness-function
  against).
- **Reversibility, where possible** — a migration should ideally have a defined "down"
  path, even if reverting a destructive change (like a dropped column) means restoring
  from backup rather than a clean automated rollback.

This is **database refactoring**: a structural change to the database schema that
preserves both its behavior (semantics stay correct) and its data (nothing is lost),
applied the same disciplined, incremental, verified way a code refactor is.

## How it works

### The expand/contract pattern
The core technique for evolving a schema without downtime or breaking consumers who
haven't yet updated to expect the new shape.

**The problem it solves**: if you have multiple consumers of a table (your own app's
several running instances during a rolling deploy, or several different services in a
shared-nothing-but-still-migrating-together scenario), you cannot atomically flip both
the schema and every consumer's code at the exact same instant. There will always be a
window where old code and new code (or old and new schema) coexist. A naive migration
("rename column `email` to `email_address` in one step") breaks every consumer still
expecting the old name during that window.

**The pattern**, in three phases:

1. **Expand** — add the new structure *alongside* the old one, without removing
   anything. Example: add a new column `email_address`, leave the old `email` column in
   place. Backfill `email_address` from `email` for existing rows. At this point, both
   the old and new schema shapes are simultaneously valid; nothing has broken.
2. **Migrate (dual-write / transition)** — update application code to write to *both*
   columns (or better, write to the new column and keep the old one in sync via a
   trigger or a background job), while still being able to read from either. Deploy this
   incrementally across instances — during the rollout, some instances run old code
   (reading/writing `email`), some run new code (reading/writing `email_address`), and
   because both columns are kept in sync, both versions see consistent data. Once every
   consumer has been updated and verified to use the new column exclusively (verify this
   with a fitness function — e.g., a query or log-based check confirming zero reads of
   the old column), this phase is complete.
3. **Contract** — once you've confirmed (not assumed) that nothing reads the old
   structure anymore, remove it: drop the old `email` column. This step is only safe once
   step 2's verification is done — contracting too early is what causes outages.

**Worked example, step by step**: An `orders` table has a single `status` column storing
a free-text string (`"pending"`, `"shipped"`, etc.). The team wants to move to a proper
enum-backed `status_id` foreign key referencing a new `order_statuses` lookup table, for
data integrity.

- *Expand*: create `order_statuses` table, populate it with the known status values.
  Add a nullable `status_id` column to `orders`. Backfill `status_id` for all existing
  rows by joining on the current `status` string. Both `status` (old) and `status_id`
  (new) now exist and are populated.
- *Migrate*: deploy application code that writes both `status` and `status_id` on every
  order update (dual write), and switch reads to use `status_id` where convenient,
  falling back to `status` where not yet updated. Roll this out incrementally — during
  the rollout window, old pods keep working against `status` alone; new pods use both.
  Add a fitness function: a scheduled query asserting `status` and `status_id` never
  diverge for any row (catches a dual-write bug immediately, rather than silently
  corrupting data). Once all reads have migrated to `status_id` (verified — e.g., via
  query logging or an explicit feature-flag rollout tracked to 100%), this phase ends.
- *Contract*: drop the `status` column. Remove the now-dead dual-write code path.

At every step, the system remains queryable and correct; no single deploy requires every
consumer to change atomically, and each step is small enough to verify and roll back
independently — this *is* incremental, guided change (per `evolutionary-architectures/01`)
applied to data specifically.

### Why a shared database is evolvability's worst enemy
Connect this directly to `evolutionary-architectures/05` (quanta): a shared database
between two otherwise-separate services is a maximally strong form of static coupling.
It means:
- Neither service can independently change its data model, because the other service's
  code depends on the current shape (columns, types, constraints) whether or not that
  dependency was ever documented — schema is an implicit, unversioned API.
- The expand/contract pattern still technically works, but now the "consumers" you must
  track and verify before contracting span *organizational* boundaries — different
  teams, different deploy schedules, different awareness of the change — turning a
  single-team migration into a cross-team coordination project every time.
- Any fitness function trying to assert "service X can deploy independently" is false as
  long as a shared schema exists underneath it, exactly as in the quantum-mismatch
  example in `evolutionary-architectures/05`.

The book's blunt framing: if you want two components to be separately evolvable
(separate quanta), they need separate data stores. There is no clever schema trick that
substitutes for actual data ownership separation — the coupling is structural, not
cosmetic, and application-layer abstractions (an ORM, a repository pattern) sitting on
top of a shared table do not remove the underlying coupling; they just hide it from the
code while it still governs deployment reality.

### Database refactoring vs. application refactoring: the parity, and where it breaks
The parity: both should be small, incremental, automated, version-controlled, tested,
and pipeline-deployed. Where it breaks:
- **Rollback asymmetry**: reverting application code to a previous version is usually
  just redeploying an old artifact. Reverting a destructive schema change (a dropped
  column, a data-transforming migration) may require restoring from a backup or running
  a compensating migration that reconstructs lost information — sometimes it's simply
  not possible to fully undo. This is why the "contract" phase of expand/contract is
  deliberately the *last*, most cautious step, done only after real verification.
  never a "we'll just roll it back if it's wrong" leap.
- **State accumulates; code doesn't**: a bug in application code affects requests going
  forward; a bug in a migration can corrupt data that then persists and compounds (every
  subsequent read/write operates on now-wrong data) until someone notices and repairs
  it — which is why the dual-write consistency-check fitness function in the worked
  example above matters: it catches divergence immediately rather than after it has
  silently accumulated for weeks.

## Pros
- Makes schema evolution safe, incremental, and verifiable instead of a scary, rare,
  all-hands "migration weekend."
- Expand/contract enables zero-downtime schema changes even with multiple consumers or
  a rolling deployment.
- Forces explicit data ownership decisions, which directly improves quantum boundaries
  and overall system evolvability (per `evolutionary-architectures/05`).
- Fitness functions on data consistency (like the dual-write check) catch data
  corruption immediately rather than letting it compound silently.

## Cons
- Expand/contract adds real complexity and calendar time compared to a single
  `ALTER TABLE` — you're running three phases (and dual-write code) instead of one
  migration.
- Requires discipline to actually complete the "contract" phase — teams frequently do
  the expand and migrate steps and then never clean up the old structure, leaving
  permanent cruft (dead columns, dual-write code nobody trusts enough to remove).
- Splitting a shared database into per-service stores (to fix the coupling problem) is
  itself a major, risky migration project — the fix is expensive even though the
  ongoing cost of not fixing it is usually higher.
- Some databases/ORMs make dual-write and backward-compatible schema changes more
  awkward than others; the pattern is universal but the tooling support varies.

## Alternatives
- **Big-bang schema migration (single downtime window)** — take the system offline,
  apply the full schema change, bring it back up. Differs by trading zero-downtime and
  incrementality for simplicity; can be acceptable for internal tools or systems with a
  genuine, tolerable maintenance window, but doesn't scale to systems with continuous
  availability requirements or many independent consumers.
- **Schema-on-read / schemaless stores (e.g., a document database with no enforced
  schema)** — defer structure validation to the application rather than the database.
  Differs by moving the evolvability problem from "migrate the schema" to "handle every
  historical document shape in application code forever," which is its own form of
  technical debt if not actively managed (old shapes accumulate and every reader must
  keep handling all of them).
- **Database views as a compatibility shim** — create a view presenting the old schema
  shape on top of a changed underlying table, letting old consumers keep working without
  code changes. Differs by pushing the compatibility work into the database layer
  instead of application code; useful for read-only consumers you don't control, but
  doesn't help with writes and adds its own maintenance burden.

## When to use it
- Any schema change to a table with more than one deployed consumer version in flight at
  once (which is essentially always true for anything using rolling deploys) —
  expand/contract should be closer to your default than the exception.
- When splitting a shared database into per-service ownership, as the primary
  step-by-step technique for moving data and consumers over safely.

## When NOT to use it
- A genuinely single-consumer, single-deploy-unit database with a maintenance window
  the business accepts may not need the full three-phase ceremony for every change —
  a straightforward migration with a downtime window can be the pragmatic choice, as
  long as that trade-off is deliberate, not accidental.
- Don't reach for expand/contract as a substitute for actually separating a shared
  database when quantum independence is the real goal — it makes any single migration
  safer, but it doesn't remove the underlying cross-team coupling problem described
  above; only actual data-ownership separation does that.

## Key takeaways / mental model
Treat the database schema as a versioned, incrementally-evolving artifact with the same
discipline as application code — but respect the asymmetry that data is stateful and
often not cleanly reversible, so migrations move in careful phases (expand, migrate,
contract) rather than one atomic leap. And remember the structural point that connects
this lesson to quanta: a shared database is not a data-modeling inconvenience, it's a
hard coupling that makes two "services" one real deployment unit, no matter what the
architecture diagram says. If you want independent evolution, you need independent data.

## Self-check questions
1. Why can't database schema changes simply be "rolled back" the same way a bad code
   deploy can?
2. Walk through the three phases of expand/contract for a concrete schema change of your
   choosing, and explain what could go wrong if you skipped straight to "contract."
3. Why is a shared database between two services considered the worst form of static
   coupling, worse than a shared library?
4. What role does a fitness function play during the "migrate" phase of expand/contract?
5. Give an example of a case where a single-step, downtime-window migration would be a
   reasonable, deliberate choice instead of expand/contract.

## References
- *Building Evolutionary Architectures*, 2nd ed. (Ford, Parsons, Kua, Sadalage,
  O'Reilly 2022), Chapter 6: Evolutionary Data
- `evolutionary-architectures/05` (architectural coupling and quanta) — shared-database
  coupling is a direct instance of the static coupling discussed there.
- `hard-parts/02` (architecture quantum and static coupling) — data ownership as a
  quantum property.
