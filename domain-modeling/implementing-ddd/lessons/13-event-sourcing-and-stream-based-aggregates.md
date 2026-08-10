---
id: implementing-ddd/13
subject: implementing-ddd
title: Event sourcing and stream-based aggregates
slug: event-sourcing-and-stream-based-aggregates
status: drafted
mastery:
seniority: staff
source: Implementing Domain-Driven Design (Vaughn Vernon), Chapter 8 (Domain Events) and Chapter 12 (Repositories) — event-sourced persistence
prerequisites: [implementing-ddd/04, implementing-ddd/07, implementing-ddd/08]
created: 2026-08-10
updated: 2026-08-10
---

# Event sourcing and stream-based aggregates

## TL;DR
Event sourcing persists an aggregate as the ordered sequence of domain events that produced its current state, rather than persisting current state directly — the aggregate's "true" data is the event stream, and current state is a derived, rebuildable projection obtained by replaying that stream; it's a powerful but heavyweight choice, reserved for aggregates where a complete, trustworthy history is itself a business requirement.

## The idea
Conventional persistence (`implementing-ddd/08`) stores an aggregate's *current* state and overwrites it on every update — the fact that an account's balance was $500 yesterday and is $300 today is lost the moment the update commits, unless a separate audit log was built to capture it. Event sourcing inverts this: instead of storing state, you store the complete sequence of events that ever happened to the aggregate (`FundsDeposited`, `FundsWithdrawn`, `FundsWithdrawn`, ...) and derive current state by replaying those events in order, from the beginning, every time the aggregate needs to be loaded (or, in practice, from the most recent snapshot forward, for performance). This isn't a cosmetic difference — it changes what "the aggregate" fundamentally *is*: not a row of current values, but a story, told chronologically, of everything that ever happened to it. Vernon frames this as a natural extension of the domain events pattern (`implementing-ddd/07`) — once an aggregate is already raising a complete, meaningful event for every state change, event sourcing is "just" persisting those events as the system of record instead of persisting a derived current-state snapshot as the system of record.

## How it works

### The core mechanism: apply, don't set
An event-sourced aggregate's state-changing methods don't mutate fields directly — they validate the operation is currently legal, then construct an event describing what happened, and apply that event to update internal state via a dedicated `apply` method. Loading the aggregate means replaying every event in its stream through that same `apply` method, from an empty initial state, arriving at current state as a pure function of history.

**Worked example — banking (Account aggregate, event-sourced).**
```
class Account {
    private AccountId id;
    private Money balance = Money.ZERO;
    private final List<DomainEvent> uncommittedEvents = new ArrayList<>();

    void withdraw(Money amount) {
        if (balance.isLessThan(amount)) throw new InsufficientFundsException(id);
        apply(new FundsWithdrawn(id, amount, Instant.now()));
    }

    // Called both for new events (recording) and during replay (rebuilding)
    private void apply(DomainEvent event) {
        if (event instanceof FundsWithdrawn e) this.balance = this.balance.subtract(e.amount());
        if (event instanceof FundsDeposited e) this.balance = this.balance.add(e.amount());
        uncommittedEvents.add(event);
    }

    static Account rehydrate(AccountId id, List<DomainEvent> history) {
        Account account = new Account(id);
        history.forEach(account::apply);   // rebuild state by replaying history
        account.uncommittedEvents.clear();  // replayed events are not "new"
        return account;
    }
}
```
Loading `Account` from the repository means fetching its event stream and calling `rehydrate` — there is no `accounts` table with a `balance` column as the system of record; the event store *is* the system of record.

### Snapshots: the performance escape hatch
Replaying thousands of events every time a long-lived aggregate is loaded gets slow. The standard mitigation is periodic snapshotting: persist a serialized current-state snapshot every N events, and on load, fetch the most recent snapshot plus only the events *after* it, replaying just that tail rather than the entire history. Snapshots are a pure optimization — they must be derivable entirely from the event stream and safely discardable/rebuildable without losing any information, never a second, independent system of record.

### What event sourcing buys you beyond persistence mechanics
- **A complete, trustworthy audit trail for free** — since the event stream *is* the data, "what happened to this account, in order, and when" is always available with no separate audit-logging effort, which matters directly for regulated domains (banking, healthcare).
- **Temporal queries** — "what was this aggregate's state as of last Tuesday" is a replay-up-to-a-point-in-time operation, not a feature that has to be specially engineered into a current-state-only system.
- **Natural fit for CQRS read models** — the event stream is exactly the input a read-model projector (`implementing-ddd/14`) needs to build and rebuild denormalized views; event-sourced write models and CQRS read models are frequently paired, though each can be adopted independently of the other.
- **Debugging/incident forensics** — reproducing exactly how an aggregate reached a buggy state is a matter of replaying its actual event history, rather than guessing from a single current-state snapshot what sequence of operations could have produced it.

### What it costs
- **Query complexity for anything other than "load this aggregate by ID"** — event stores are not naturally good at "find all accounts with balance over $10,000" the way a relational table with a `balance` column is; such queries require either replaying every aggregate (infeasible at scale) or maintaining a separate read model (`implementing-ddd/14`) purely for querying, meaning event sourcing in practice almost always pairs with CQRS.
- **Schema evolution of events themselves is hard** — once events are durably persisted as the system of record, you can't simply "migrate the schema" the way you'd alter a table; old events must remain interpretable forever (or be explicitly upcasted/versioned) since replaying history requires understanding every event shape that was ever recorded.
- **A genuinely different mental model for the whole team** — developers, ops, and support staff used to reasoning about "the current row in the database" need to learn to reason about "the current state is a replay of history," which is a real, ongoing cognitive cost, not a one-time learning curve.

**Worked example — order fulfillment, where NOT to event-source.** A simple `Order` aggregate with no regulatory audit requirement, no need for temporal queries, and straightforward CRUD-shaped state transitions gains little from event sourcing — conventional current-state persistence (`implementing-ddd/08`) is simpler to build, query, and reason about, and the team should resist reaching for event sourcing here "because it's more sophisticated." Compare this to a `LedgerAccount` aggregate in the same system's accounting subdomain, where a complete, immutable, auditable transaction history is a genuine, named business/regulatory requirement — that's exactly the case event sourcing is built for.

## Pros
- A complete, immutable, and inherently trustworthy history of every change, which is a genuine business asset (audit, compliance, debugging, temporal analysis) rather than a byproduct.
- Domain events, already a first-class part of the tactical toolkit (`implementing-ddd/07`), become the *actual* persistence mechanism rather than a secondary notification layer bolted onto conventional persistence — reducing duplication between "what we persist" and "what we notify others about."
- Pairs naturally with CQRS (`implementing-ddd/14`) to support arbitrarily many, independently-optimized read models rebuilt from the same authoritative event history.

## Cons
- Querying anything other than "current state of one aggregate by ID" is hard without a paired read model, making event sourcing almost never adopted in isolation from CQRS in practice.
- Event schema evolution is a genuinely hard, ongoing engineering problem — old events must remain replayable indefinitely, requiring careful versioning/upcasting discipline that most teams underestimate at first.
- A substantial shift in team mental model and tooling (specialized event stores, replay/rehydration logic, snapshotting) that raises the bar for onboarding and operational maturity compared to conventional CRUD-style persistence.

## Alternatives
- **Conventional current-state persistence with a separate audit log** — persist current state as usual, but also log significant changes to a separate append-only audit table; captures much of the audit-trail benefit without event sourcing's full architectural commitment, appropriate when audit is a nice-to-have rather than the system of record's actual truth.
- **Change Data Capture (CDC) as a pseudo-event-source** — derive an event-like stream by tailing the database's transaction log rather than the aggregate explicitly raising events; gives some of event sourcing's downstream benefits (feeding read models, `implementing-ddd/14`) without redesigning the write model, at the cost of the "events" being row-change facts rather than genuine business-meaningful facts.
- **Periodic full-state snapshots without event history** — simply persist current state on every change (conventional persistence) and take periodic full backups/snapshots for disaster recovery; much simpler, but offers none of event sourcing's fine-grained, queryable, business-meaningful history.

## When to use it
For aggregates in a core domain (`implementing-ddd/01`) with a genuine, specific need for a complete, trustworthy history — regulatory audit requirements, financial ledgers, anything where "how did we get to this state" is itself a business question the system must answer, and where the team has (or is willing to build) the operational maturity for event-store infrastructure and paired read models.

## When NOT to use it
For straightforward aggregates with no real audit/temporal-query requirement, and especially for teams new to DDD or without existing event-store/CQRS infrastructure — conventional current-state persistence (`implementing-ddd/08`) is simpler, cheaper, and entirely sufficient; adopting event sourcing "because it seems more rigorous" without a concrete need is a classic case of over-engineering.

## Key takeaways / mental model
Event sourcing answers one specific question really well: "what is the complete, trustworthy history of everything that happened to this aggregate, and can I reconstruct its state at any point in that history?" If no one actually needs that question answered for a given aggregate, event sourcing is solving a problem you don't have, at a real and ongoing cost.

## Self-check questions
1. Take an aggregate from a system you know. Would event sourcing it provide genuine business value (a real audit/temporal-query need), or would it just be architectural novelty? Justify with a concrete scenario.
2. Explain why event sourcing almost always ends up paired with CQRS read models in practice, rather than being adopted alone.
3. What specifically makes event schema evolution harder for an event-sourced aggregate than for a conventionally-persisted one? Give a concrete example of a schema change that would be easy in one and hard in the other.
4. Describe how snapshotting improves event-sourced aggregate load performance, and why a snapshot must always be fully derivable from (and discardable in favor of) the underlying event stream.

## References
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 8: "Domain Events" (events as persistence).
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 12: "Repositories" (event-sourced repository implementations).
