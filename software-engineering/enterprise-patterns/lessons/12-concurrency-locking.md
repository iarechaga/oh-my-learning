---
id: enterprise-patterns/12
subject: enterprise-patterns
title: "Concurrency: Optimistic vs Pessimistic Locking"
slug: concurrency-locking
status: drafted
mastery:
seniority: senior
source: Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 13
prerequisites: [enterprise-patterns/07, pragmatic-programmer/11]
created: 2026-08-10
updated: 2026-08-10
---

# Concurrency: Optimistic vs Pessimistic Locking

## TL;DR
When two users might edit the same record at nearly the same time — a genuine, common concern for enterprise applications with many concurrent users — Optimistic Offline Lock detects a conflict only at save time (via a version number), letting both users read and edit freely and rejecting only the second save if it's now stale; Pessimistic Offline Lock prevents the conflict from ever occurring by acquiring an explicit lock the moment editing begins, blocking a second user from even starting to edit the same record.

## The idea
`pragmatic-programmer/11` addressed concurrency within a single process's shared mutable state (multiple threads). This lesson addresses a related but distinct problem specific to enterprise applications: concurrency across *user sessions*, potentially spanning minutes (a user opens an edit form, thinks about it, then submits) — the classic "lost update" problem, where User A loads a record, User B loads the same record, User B saves their changes, then User A saves their own changes, silently overwriting User B's without either user ever being told a conflict occurred.

## How it works

### The lost-update problem, precisely
```
Time 1: User A loads Customer #42 (credit_limit: 1000)
Time 2: User B loads Customer #42 (credit_limit: 1000)     -- same starting data
Time 3: User B changes credit_limit to 1500, saves.          -- now 1500 in the database
Time 4: User A changes credit_limit to 1200 (based on the STALE 1000 they loaded), saves.
Result: credit_limit is now 1200 -- User B's change to 1500 is silently, completely lost
```
Neither user did anything wrong individually — each correctly read, then correctly wrote, their own view of the data. The problem is purely a consequence of the *time gap* between reading and writing, during which the underlying data changed without either user's knowledge — directly analogous to `pragmatic-programmer/11`'s shared-mutable-state race, but stretched across a much longer timescale (user-think-time, not microseconds) and across sessions rather than threads.

### Optimistic Offline Lock — detect the conflict at save time
Add a version number (or a timestamp) to each record. When a user loads a record, they receive its current version. When they save, the save operation checks whether the version they're saving *against* still matches the current version in the database — if it doesn't (meaning someone else saved a change in between), the save is rejected, and the user is told to reload and reapply their change.

**Worked example.**
```sql
UPDATE customers
SET credit_limit = 1200, version = 6
WHERE id = 42 AND version = 5;   -- the version User A loaded

-- if User B already saved and bumped the version to 6, this WHERE clause matches ZERO rows
-- the application checks rows_affected == 0 and knows the save was rejected due to a conflict
```
User A's save fails cleanly and detectably (zero rows affected, rather than silently succeeding and overwriting), and the application can inform User A their data is stale and ask them to reload and reconsider their change in light of User B's update — the conflict is *caught*, not silently lost, at the cost of occasionally requiring a user to redo work when a genuine conflict occurs.

### Pessimistic Offline Lock — prevent the conflict from occurring at all
Rather than detecting a conflict after the fact, acquire an explicit lock the moment a user *begins* editing a record — a second user attempting to begin editing the same record is blocked (or informed the record is currently locked) *before* they can even start making changes, eliminating the possibility of the lost-update scenario entirely, by preventing the concurrent-edit window from ever opening in the first place.

**Trade-off versus Optimistic.** Pessimistic locking guarantees no lost updates ever occur, but at a real cost: a lock held across a user's think-time (potentially minutes, or — if a user simply closes their browser without releasing the lock — indefinitely, requiring a timeout mechanism) blocks *every* other user from editing that record for that entire duration, even in the common case where no actual conflict would have occurred. This directly mirrors the classic lock-granularity and contention trade-offs from `pragmatic-programmer/11`'s concurrency discussion, now at the scale of user sessions rather than threads: broad, long-held locks reduce concurrency (throughput) to guarantee correctness, even when most of the time no actual conflict was going to happen anyway.

### Choosing between them — a question about actual contention rates
The deciding factor is empirical, not purely theoretical: **how often do multiple users genuinely, actually try to edit the exact same record concurrently?** For most enterprise applications, genuine same-record concurrent edits are rare relative to total edit volume — most records are edited by one user at a time, with no real overlap — making Optimistic Locking's "detect rarely, and cheaply, at save time" approach the better fit: the cost of an occasional rejected save (a rare event) is far lower than the cost of every single edit paying Pessimistic Locking's full locking overhead (a cost paid on *every* edit, even the overwhelming majority that would never have actually conflicted). Pessimistic Locking is reserved for situations with genuinely high, frequent contention on the same specific records, where preventing the conflict outright is worth its broader throughput cost.

## Pros
- Optimistic Locking has low overhead for the common case (no actual conflict) and scales well, since it doesn't hold any resource locked during a user's potentially-long think-time.
- Pessimistic Locking provides an absolute guarantee against lost updates, with no possibility of a rejected save ever surprising a user after they've done their editing work.
- Both patterns solve the lost-update problem in a principled, well-understood way, rather than leaving it to chance or requiring ad hoc, application-specific workarounds.

## Cons
- Optimistic Locking requires the user to redo work when a genuine conflict does occur, and requires careful UX design to communicate the conflict clearly rather than just failing confusingly.
- Pessimistic Locking risks records becoming stuck, locked indefinitely if a user abandons their edit session without releasing the lock (browser crash, network loss) — requiring a timeout or explicit lock-expiration mechanism to avoid permanently blocking other users.
- Choosing the wrong pattern for your actual contention rate produces either unnecessary user friction (Pessimistic Locking applied where conflicts are rare) or an unpleasant surprise rate of rejected saves (Optimistic Locking applied where conflicts are frequent).

## Alternatives
- **Last-write-wins, with no conflict detection at all** — the naive default many systems start with; simplest, but silently accepts the lost-update problem this whole lesson exists to prevent, appropriate only when the data's staleness genuinely doesn't matter (e.g., a view counter, not a financial balance).
- **Conflict-free replicated data types (CRDTs)** (see `architecture/ddia`, `architecture/distributed-systems`) — a fundamentally different approach for specific data structures that can be merged automatically without conflict, sidestepping the need for either locking strategy for the specific kinds of data they support.
- **Operational transformation** (used in real-time collaborative editors) — a more sophisticated technique for merging genuinely concurrent, fine-grained edits (character-by-character) rather than treating a whole record as a single unit that either conflicts or doesn't.

## When to use it
Use Optimistic Offline Lock as the default choice for most enterprise applications, where genuine same-record concurrent edits are relatively rare. Use Pessimistic Offline Lock specifically for situations with high, frequent, known contention on the same specific records, where preventing the conflict outright is worth its throughput cost.

## When NOT to use it
Don't use Pessimistic Locking by default for low-contention data, where it would impose unnecessary blocking overhead on the overwhelming majority of edits that would never have actually conflicted. Don't rely on last-write-wins for data where staleness genuinely matters (financial balances, inventory counts) — that's accepting the lost-update problem, not solving it.

## Key takeaways / mental model
Ask: "how often, in practice, do multiple users genuinely try to edit this exact same record at the same time?" Rare contention favors Optimistic Locking's cheap, save-time detection. Frequent, known contention on specific records favors Pessimistic Locking's guaranteed prevention, accepting its throughput cost as the price of that guarantee.

## Self-check questions
1. Walk through the lost-update scenario step by step, and explain precisely how Optimistic Locking's version check would have caught it.
2. Describe the specific risk Pessimistic Locking introduces (a stuck, indefinitely-locked record) and how you'd mitigate it.
3. Why is the choice between Optimistic and Pessimistic Locking fundamentally an empirical question about contention rates, rather than a purely theoretical one?
4. Give an example of data in a system you know where last-write-wins (no conflict detection at all) would be an acceptable, deliberate choice, and explain why staleness doesn't matter there.

## References
- Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 13: "Concurrency" (Optimistic Offline Lock and Pessimistic Offline Lock sections).
- See also: `pragmatic-programmer/11` (Concurrency and Temporal Coupling) for the related, finer-grained (thread-level) concurrency concerns this lesson extends to the session/transaction scale.
