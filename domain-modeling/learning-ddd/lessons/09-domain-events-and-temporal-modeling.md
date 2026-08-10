---
id: learning-ddd/09
subject: learning-ddd
title: Domain events and temporal modeling
slug: domain-events-and-temporal-modeling
status: drafted
mastery:
seniority: senior
source: Learning Domain-Driven Design (Vlad Khononov), Part II, Chapter 6 (continued) and Chapter 7 - "Domain Events" and "Event-Sourced Domain Model"
prerequisites: [learning-ddd/08, learning-ddd/06]
created: 2026-08-10
updated: 2026-08-10
---

# Domain events and temporal modeling

## TL;DR
A domain event is an immutable record of something significant that happened in the business, named in past tense ("Order Placed," "Subscription Cancelled") - the same vocabulary event storming (`learning-ddd/06`) surfaces, now made a first-class part of the domain model. Domain events are the mechanism aggregates (`learning-ddd/08`) use to communicate across their boundaries without collapsing into one giant transaction, and, taken further, can become the *primary* source of truth for an aggregate's state (event sourcing) rather than just a notification mechanism.

## The idea
`learning-ddd/08` established that aggregates should be small, and that cross-aggregate coordination should be eventual, not transactional. Domain events are the concrete mechanism that makes "eventual" actually work: when an aggregate's state changes in a way that matters to the rest of the system, it emits an event describing exactly what happened. Other aggregates, other bounded contexts (`learning-ddd/11`), or purely reactive processes (event-storming's purple "Policy" notes from `learning-ddd/06`) can react to that event - updating their own state, triggering a side effect, or simply recording that it occurred - without the originating aggregate needing to know or care who's listening.

This is also a shift in how state itself is thought about: instead of asking only "what is true right now," domain events let a system answer "what happened, in what order, and why did the current state come to be this way" - what Khononov calls temporal modeling. Some business needs (audit trails, financial reconciliation, "undo," analytics on process flow) genuinely require this history, not just a current snapshot - and for those needs, event sourcing (storing the events themselves as the system of record, deriving current state by replaying them) becomes attractive, though it is a significant additional commitment, not a default choice.

## How it works

### Domain events as notification: the common case
An aggregate, having validated and applied a change to itself, emits an event describing what happened. The event is a simple, immutable data structure - not a command, not a request, just a fact.

**Worked example - SaaS billing.**
```
class Subscription {
  cancel(reason: CancellationReason): SubscriptionCancelled {
    if (this.status !== SubscriptionStatus.Active) {
      throw new CannotCancelInactiveSubscriptionError();
    }
    this.status = SubscriptionStatus.Cancelled;
    this.cancelledAt = now();
    return new SubscriptionCancelled(this.id, reason, this.cancelledAt);
  }
}
```
The `SubscriptionCancelled` event is then published (via an outbox, message broker, or in-process event bus - mechanics belong to `learning-ddd/11`). Independent listeners react without the `Subscription` aggregate knowing they exist: a Billing-Reconciliation process issues a final prorated credit; a Retention-Analytics process records the cancellation reason for churn analysis; a Notifications process sends a "sorry to see you go" email. None of this logic lives inside `Subscription.cancel()` - which stays focused purely on its own invariant (you can't cancel an already-cancelled subscription) - and none of these three reactions need to happen in the same transaction as the cancellation itself, matching `learning-ddd/08`'s guidance that cross-aggregate effects should be eventual, not transactional.

### Worked example - logistics: a Policy from event storming becomes code
Recall `learning-ddd/06`'s event-storming discovery: "whenever Item Backordered AND 48 hours pass with no resupply, automatically Cancel Line Item." This purple "Policy" sticky note becomes, in code, a listener subscribed to the `ItemBackordered` domain event, running on a delay/timer, which issues a `CancelLineItem` command against the `Order` aggregate if the condition still holds after 48 hours. The domain event is what makes this automatic reaction possible without the `Order` aggregate itself needing to know anything about resupply timers - that responsibility lives entirely in the policy/listener, a separate, independently testable and independently changeable piece of the system.

### Worked example - healthcare: domain events crossing a bounded-context boundary
When a `ProviderCancelled` event fires inside the Scheduling bounded context, a listener in a separate Patient-Communications bounded context (`learning-ddd/03`) reacts by sending an SMS - without Scheduling needing to know Patient-Communications exists, only that "something happened that other parts of the system might care about" is worth publishing. This is exactly the Open Host Service pattern from `learning-ddd/04` in action: Scheduling publishes a stable, well-defined event as its public contract; any number of downstream contexts can subscribe without Scheduling being aware of or coupled to any of them.

### Event Sourcing: events as the system of record, not just a notification
In an event-sourced aggregate, the *only* thing persisted is the ordered sequence of domain events; current state is derived by replaying them (or from a cached "snapshot" for efficiency), rather than storing a mutable current-state row.

**Worked example - re-modeling the Subscription aggregate as event-sourced.**
```
class Subscription {
  static fromHistory(events: DomainEvent[]): Subscription {
    const sub = new Subscription();
    for (const e of events) sub.apply(e);   // replay each event to rebuild state
    return sub;
  }
  cancel(reason: CancellationReason) {
    if (this.status !== SubscriptionStatus.Active) {
      throw new CannotCancelInactiveSubscriptionError();
    }
    this.raise(new SubscriptionCancelled(this.id, reason, now()));
  }
  private apply(event: DomainEvent) {
    if (event instanceof SubscriptionCancelled) {
      this.status = SubscriptionStatus.Cancelled;
      this.cancelledAt = event.occurredAt;
    }
    // ... other event types
  }
}
```
Now the *entire history* of every subscription - every upgrade, downgrade, pause, and cancellation, in order, with timestamps and reasons - is the actual system of record, not a side effect. This directly answers questions a current-state-only model cannot: "show me every subscription that was upgraded and then cancelled within 30 days" (a churn-analysis question), or "reconstruct exactly what this subscription's state was on the date of a disputed invoice" (an audit/compliance question) - both become straightforward replay-and-filter operations over the event log, rather than requiring the team to have anticipated and stored those specific fields in advance.

## Pros
- Decouples aggregates and bounded contexts in time as well as in space: a listener doesn't need to be running (or even exist yet) at the moment an event is published, if events are durably queued - a new feature can start reacting to *past* events it wasn't originally designed for, without touching the originating aggregate at all.
- Directly implements the automated "Policy" behaviors discovered in event storming (`learning-ddd/06`), turning discovered business rules into isolated, independently testable listeners.
- Event sourcing (the temporal-modeling extension) provides a complete, tamper-evident audit trail "for free" - valuable for regulated domains (healthcare, finance) where reconstructing past state or proving what happened and when is a real, recurring business need.
- Enables replaying history to rebuild new read models or fix bugs retroactively (replay events through corrected logic) - a capability a current-state-only system simply doesn't have.

## Cons
- Adds real asynchronous-systems complexity: eventual consistency (`learning-ddd/10`), the need for reliable delivery (outbox pattern, idempotent handlers), and harder-to-trace causality when debugging ("why did X happen" now means tracing a chain of events and listeners instead of reading one function call stack).
- Event sourcing specifically is a significant commitment: schema evolution of event types over years is a genuinely hard problem (old events must remain interpretable as the model evolves), querying "current state" efficiently requires either replay-on-read (slow) or maintained snapshots/read models (more infrastructure), and the team must design events carefully upfront since past events are typically treated as immutable history, not freely rewritable.
- Overusing domain events for things that are really just internal implementation details (rather than genuinely significant business facts) creates event-notification sprawl that's as hard to follow as the tangled procedural code it was meant to replace.
- Not every subdomain needs temporal modeling at all - most supporting and generic subdomains (`learning-ddd/02`) are well served by simple current-state storage with no event history whatsoever.

## Alternatives
- **Plain current-state persistence with no domain events** - simpler, adequate for subdomains with no cross-aggregate reactions to coordinate and no audit/history requirement; the right default for most supporting and generic subdomains.
- **Change Data Capture (CDC) on the database** - derives an event-like stream from database row changes after the fact, rather than the domain model explicitly raising meaningful business events; captures *that* something changed but not reliably *why* in business terms, making it a weaker foundation for the Policy-driven reactions this lesson covers.
- **Explicit audit-log tables bolted onto a current-state model** - captures history for compliance without committing to full event sourcing; less architecturally invasive, but the audit log is usually a side effect maintained separately rather than the actual source of truth, so it can drift from real state if not disciplined.
- **`ddd-evans`'s original Domain Events concept** (added in later editions/community extensions of Evans's work) and Greg Young's original event-sourcing writing - foundational sources Khononov builds on and modernizes with the explicit connection back to event storming's vocabulary.

## When to use it
Use plain domain events (notification, not sourcing) whenever an aggregate's change needs to trigger a reaction elsewhere - another aggregate, another bounded context, or an automated policy discovered in event storming. Reach for full event sourcing specifically when a core subdomain has a genuine, recurring business need for complete history, audit trail, or "what was true at time T" queries - a decision that should be deliberate and informed by the subdomain's classification (`learning-ddd/02`), not adopted as a default architectural style.

## When NOT to use it
Don't event-source a subdomain with no real historical-query or audit need just because it seems architecturally sophisticated - the replay/snapshot/schema-evolution overhead is a poor trade for a subdomain (most supporting and generic ones) that only ever needs to know its current state. Also avoid publishing a domain event for every trivial internal state change; reserve them for facts genuinely meaningful to some other part of the business or system, matching the significance bar event storming applies when selecting which facts belong on the timeline.

## Key takeaways / mental model
A domain event answers "what happened, described in the ubiquitous language, that some other part of the system might legitimately care about?" Publish one whenever that answer is yes, and let listeners - not the originating aggregate - own the reaction. Only escalate to full event sourcing when the business genuinely needs the *history itself* as a first-class asset, not merely as a byproduct of debugging convenience.

## Self-check questions
1. Take a business process you know and identify one domain event it should emit, and at least two independent listeners that would plausibly react to it without needing to know about each other.
2. Why does emitting a domain event from an aggregate (rather than the aggregate directly calling into other aggregates' methods) matter for keeping aggregate boundaries small, per `learning-ddd/08`?
3. Explain the difference between "domain events as a notification mechanism" and "event sourcing." What does event sourcing give you that plain domain events plus current-state storage does not?
4. Give an example of a subdomain where event sourcing would be a poor fit despite sounding architecturally appealing, and explain why plain current-state storage serves it better.

## References
- Learning Domain-Driven Design (Vlad Khononov), Part II, Chapter 6: "Aggregates" (Domain Events) and Chapter 7: "Trade-Offs of Different Models" (Event-Sourced Domain Model).
- Domain-Driven Design (Eric Evans, 2003) and community extensions on Domain Events - see `domain-modeling/ddd-evans`.
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 8, "Domain Events" - see `domain-modeling/implementing-ddd`.
