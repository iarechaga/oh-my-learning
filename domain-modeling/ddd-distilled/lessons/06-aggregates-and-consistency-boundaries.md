---
id: ddd-distilled/06
subject: ddd-distilled
title: Aggregates and consistency boundaries
slug: aggregates-and-consistency-boundaries
status: drafted
mastery:
seniority: senior
source: Domain-Driven Design Distilled (Vaughn Vernon), Chapter 5 "Tactical Design with Aggregates"
prerequisites: [ddd-distilled/05]
created: 2026-08-10
updated: 2026-08-10
---

# Aggregates and consistency boundaries

## TL;DR
An aggregate is a cluster of entities and value objects treated as a single unit for the
purpose of data changes, with one designated **aggregate root** as the only entry point,
and a boundary that defines what must be transactionally (immediately) consistent versus
what can be eventually consistent. Getting aggregate boundaries right — Vernon's central
tactical-design advice — usually means **smaller than you'd guess**: one aggregate per
true invariant that must hold instantly, referencing other aggregates by identity rather
than by direct object reference.

## The idea
Once you have entities and value objects (`ddd-distilled/05`), you need a way to decide:
when a use case changes several related objects at once, which of those changes must
succeed or fail together, atomically, right now — and which can happen slightly later,
safely, without the whole operation blocking on it? Answering that question badly is one
of the most common and expensive DDD mistakes.

The naive instinct is to model a large object graph as one big aggregate — e.g., an
`Order` aggregate that contains every `OrderLine`, the full `Customer` record, the
`ShippingAddress`, `PaymentDetails`, and `InventoryReservation`s all nested inside one
root, because "they're all related to the order." This produces a huge transactional
unit: loading the order means loading everything, saving any small change means locking
and rewriting the whole graph, and two users touching unrelated parts of the same order
concurrently now contend for the same lock. Vernon's core teaching (echoing lessons
learned industry-wide after Evans's original, looser guidance) is: **aggregates should be
as small as possible**, built around one specific invariant that truly needs atomic
consistency, with everything else referenced by ID and coordinated through eventual
consistency (`ddd-distilled/08`) instead of forced into the same transaction.

## How it works

### The aggregate root and its rules
- Every aggregate has exactly one **root entity** — the only object external code is
  allowed to hold a reference to or call methods on directly. Objects inside the
  aggregate (other entities, value objects) are only reachable through the root.
- All invariants (business rules that must always hold) that the aggregate is
  responsible for are enforced by the root's methods — external code never reaches in
  and mutates an inner object directly, because that would bypass the root's invariant
  checks.
- References **out** of an aggregate to other aggregates are by **identity only** (an ID,
  not a live object reference) — this is what keeps aggregates decoupled and small; you
  don't pull a whole `Customer` aggregate inside an `Order` aggregate, you hold a
  `customerId`.
- One aggregate = one transaction, in the common case. A single use case should typically
  modify exactly one aggregate instance per transaction; if it seems to need to modify
  two, that's usually a sign either the boundary is drawn wrong, or the second change
  should happen via eventual consistency (`ddd-distilled/08`) rather than the same
  transaction.

### Worked example — an e-commerce order, drawn too big vs. right-sized
**Too big (common mistake):** `Order` aggregate root containing the full `Customer`
entity, every `OrderLine`, `ShippingAddress`, `PaymentMethod`, and live
`InventoryReservation` objects for every line item, all inside one transactional
boundary. Consequence: adding a single line item to the order requires loading and
locking the entire graph, including inventory reservation state that has nothing to do
with the invariant "an order's line items and total must be consistent." Two customer
service reps working on different parts of the same order (one updating shipping
address, one checking payment status) contend unnecessarily.

**Right-sized:** `Order` aggregate root contains only `OrderLine` value objects and the
order's own state (status, total, list of line items) — the true invariant here is "the
order's total must always equal the sum of its line items' amounts, and line items can
only be modified while the order is in `Draft` status." `customerId`, `shippingAddressId`
are held as plain identity references, not embedded objects. `PaymentDetails` becomes its
own separate aggregate (`Payment`), coordinated with `Order` via a domain event
(`OrderPlaced` triggers payment processing, `ddd-distilled/08`) rather than living inside
the same transaction. `InventoryReservation` is its own aggregate too, for the same
reason — reserving stock for line item A and line item B don't need to succeed or fail
atomically together with each other, and definitely don't need to be atomic with,
say, updating the shipping address.

### Worked example — identifying the true invariant
A ride-hailing `Trip` aggregate: what actually needs atomic consistency? "A trip cannot
transition to `InProgress` unless it currently has an assigned driver and is in
`DriverEnRoute` status" — that's a real invariant, enforced by a `Trip.startTrip()`
method on the root that checks preconditions before allowing the transition. What does
*not* need to be in the same aggregate: the driver's current location (changes
extremely frequently, belongs to a `DriverLocation` aggregate or a separate
fast-changing store entirely, updated independently and read by the matching/tracking
logic via eventual consistency) and the rider's payment method (belongs to the rider's
own account aggregate, referenced by ID, coordinated at trip-completion time via a domain
event rather than embedded in `Trip`). Bundling driver location updates (happening every
few seconds) into the same aggregate as trip status would create massive write
contention for no invariant-preserving benefit.

### Sizing heuristic
Vernon's practical heuristic: **model a true invariant, and design a small aggregate that
protects it — resist the urge to add anything to the aggregate that isn't required by
that specific invariant.** If you find yourself unsure whether two entities belong in the
same aggregate, ask: "if these two changed at the exact same moment from two different
requests, would allowing them to be briefly inconsistent with each other cause a real
business problem, or just look slightly odd for a moment?" If it's a real business
problem (the order total not matching its line items, ever, even briefly) — same
aggregate. If it's just cosmetic staleness (the customer's displayed loyalty tier being
one event behind their latest purchase) — separate aggregates, coordinated eventually.

### Referencing other aggregates
Because references between aggregates are by ID, retrieving related data across
aggregates typically requires a repository lookup (`ddd-distilled/07`) or a
read-optimized query/projection built specifically for that purpose, rather than
navigating an in-memory object graph. This is a deliberate trade: you give up
convenient graph navigation in exchange for small, independently-lockable, independently-
scalable transactional units. For UI screens that need to show data assembled from
several aggregates (an order summary page showing order + customer name + shipping
status), the common answer is a dedicated read model/query, not stitching aggregates
together live — this connects directly to how domain events (`ddd-distilled/08`) are
often used to keep denormalized read models in sync.

## Pros
- Small, well-drawn aggregates minimize lock contention and enable independent scaling
  and independent evolution of different parts of a domain.
- Concentrating invariant enforcement inside the aggregate root makes "can this system
  ever be in an invalid state" a local, auditable question about one class, rather than a
  system-wide search for every place that might mutate related data.
- ID-only references between aggregates keep the object graph shallow, which keeps
  loading, serialization, and reasoning about any single aggregate cheap.
- Forces an explicit, deliberate answer to "what actually needs to be atomic" instead of
  defaulting to "everything, because it's convenient in one transaction."

## Cons
- Getting aggregate boundaries wrong (still too large, a very common failure even among
  experienced teams) reintroduces the contention and coupling problems this pattern
  exists to solve — sizing aggregates well is a genuinely hard skill that takes practice
  and iteration.
- Cross-aggregate consistency becomes eventual, not immediate, which pushes real
  complexity into managing temporary inconsistency windows and into domain events
  (`ddd-distilled/08`) — some business stakeholders find "eventually consistent" an
  uncomfortable answer at first and need it explained concretely.
- Assembling data spanning multiple aggregates for a UI or report requires extra query
  or read-model machinery instead of a simple graph traversal, adding architectural
  surface area.
- Overcorrecting toward extremely tiny aggregates (a separate aggregate per field) adds
  needless transaction and coordination overhead in the other direction — the goal is
  "as small as the true invariant demands," not "as small as possible unconditionally."

## Alternatives
- **One large object graph / no aggregate boundaries** — the default in many
  ORM-driven codebases (navigate freely via object references, save whatever you touched).
  Simple to start with, but the contention and blast-radius problems described above tend
  to appear as soon as the system has real concurrent load or grows past a small team.
- **Database-transaction-scoped consistency with no domain concept of aggregate** —
  relying purely on database transactions/locks without an explicit domain boundary
  concept; works, but the "what should be atomic" decision ends up implicit in whatever
  queries happen to run inside one transaction, rather than being a deliberate, named,
  reviewable domain design decision.
- **CQRS with fully separate write and read models** — a complementary pattern, not
  really a competing alternative: aggregates typically serve as the write-side
  consistency boundary, while a separate read model (built via domain events,
  `ddd-distilled/08`) serves cross-aggregate query needs. Worth knowing as the natural
  next step once aggregate boundaries force read concerns out of the write model.

## When to use it
Use explicit aggregate design for any entity cluster in your core (or carefully-modeled
supporting) domain where genuine business invariants must hold — anywhere you'd otherwise
be tempted to wrap several database writes in one big transaction "just to be safe."
Draw the aggregate boundary around the specific invariant, and keep it as small as that
invariant requires.

## When NOT to use it
Skip aggregate ceremony for generic/simple CRUD data with no real invariants to protect —
a single entity with straightforward validation is enough. Also don't force a
single-transaction design across data that doesn't actually need atomic consistency just
because it's "related" — that's the oversized-aggregate mistake this lesson spends most
of its worked examples warning against. And treat lock contention or serialization
conflicts observed under load on a particular aggregate as a strong signal to re-examine
whether it's drawn too large — it's one of the few DDD design decisions with a fairly
direct, measurable operational symptom.

## Key takeaways / mental model
An aggregate is not "the objects for this feature" or "this database table plus its
child tables" — it is the smallest cluster of objects that must change together,
atomically, to protect one real business invariant. When in doubt, make it smaller and
reference the rest by ID; you can always coordinate across aggregates with domain events
later, but an oversized aggregate is expensive to split once contention and coupling have
already accreted around it.

## Self-check questions
1. Take the "Order too big vs. right-sized" example. Explain, specifically, why
   `PaymentDetails` doesn't belong inside the `Order` aggregate even though every order
   has payment details.
2. What concrete production symptom (think: database behavior under concurrent load)
   would tip you off that an aggregate has been drawn too large?
3. Describe the rule about referencing other aggregates ("by identity, not by object
   reference") and explain what problem it prevents.
4. For a hotel booking system, would you put `Room` availability and a guest's
   `Reservation` in the same aggregate? Walk through the invariant-identification
   question from the lesson to justify your answer.
5. Why does Vernon's guidance ("aggregates should usually be small, often a single
   entity") represent a correction to how DDD was commonly practiced after Evans's
   original book? What real-world pain motivated that correction?

## References
- Domain-Driven Design Distilled (Vaughn Vernon), Chapter 5: "Tactical Design with
  Aggregates".
- For extensive aggregate-sizing case studies and the historical "aggregates were too
  big" industry lesson, see `domain-modeling/implementing-ddd` and
  `domain-modeling/ddd-evans`.
