---
id: ddd-distilled/03
subject: ddd-distilled
title: Bounded contexts and context maps
slug: bounded-contexts-and-context-maps
status: drafted
mastery:
seniority: mid
source: Domain-Driven Design Distilled (Vaughn Vernon), Chapter 4 "Context Mapping" (concept introduced in Ch.2)
prerequisites: [ddd-distilled/01, ddd-distilled/02]
created: 2026-08-10
updated: 2026-08-10
---

# Bounded contexts and context maps

## TL;DR
A bounded context is an explicit boundary — usually matching a subsystem, service, or
module — within which a particular model and its ubiquitous language apply consistently
and unambiguously. A context map is a diagram (and a set of documented relationships)
showing how multiple bounded contexts in a system relate to and integrate with each
other. Together they answer "where does one model end and another begin, and how do they
talk to each other?"

## The idea
Software systems of any real size cannot have one unified model of "the business."
Different parts of a business genuinely think about the same real-world thing
differently, and forcing one model to serve everyone produces a bloated, contradictory
mess — a "big ball of mud" where a `Product` class has fields for pricing, warehouse
location, marketing copy, and tax classification, maintained by four different teams who
keep breaking each other's assumptions.

A bounded context solves this by giving each distinct model an explicit boundary: inside
the boundary, terms mean one specific thing (this is where `ddd-distilled/02`'s
ubiquitous language actually lives); outside the boundary, the same word might mean
something else entirely, and that's fine, because nothing crosses the boundary without a
deliberate translation. In the retail example from `ddd-distilled/02`, "Product" in the
catalog context (name, description, images, category) and "Product" in the
inventory context (SKU, quantity on hand, warehouse bin) are different models that
happen to share an English word — each is correct *within its own bounded context*.

A context map is the strategic-level tool for reasoning about a *system* of bounded
contexts: which ones exist, how they're related (who depends on whom, who has more
influence over the shared language at the integration point), and what integration
pattern each relationship uses. Without an explicit context map, integration
relationships tend to be accidental and asymmetric in ways nobody chose deliberately —
the context map makes the choice visible and intentional.

## How it works

### Identifying a bounded context
A bounded context is typically discovered, not designed top-down: watch for a word that
means different things in different conversations (the "Product" or "Customer" pattern),
or for a team/subsystem boundary that already exists organizationally. A useful test:
if you gathered the people who work on one part of the system and asked them to define a
core term, would they give one consistent answer? If yes, you're likely inside one
bounded context. If the room splits into two camps with different definitions, you've
probably found the seam between two bounded contexts.

### Context mapping relationship patterns
Vernon (drawing on Evans) catalogs several standard relationship types between bounded
contexts. The important ones to know:

- **Partnership** — two teams succeed or fail together; they coordinate closely and
  evolve their contexts' integration jointly. High trust, high coordination cost.
- **Shared Kernel** — two contexts deliberately share a small subset of the model (e.g.,
  a shared `Money` value object) to avoid duplicating something both need identically.
  Requires careful, low-frequency-of-change code shared between teams — changes to the
  kernel require both teams' agreement.
- **Customer–Supplier** — one context (the supplier) provides data/functionality that a
  downstream context (the customer) depends on, and the customer's needs have real
  influence over the supplier's roadmap (e.g., an internal pricing-engine team building
  features specifically because the checkout team needs them).
- **Conformist** — a downstream context has no influence over an upstream one (e.g.,
  integrating with a big vendor's API) and simply conforms to whatever model the
  upstream exposes, translating nothing.
- **Anticorruption Layer (ACL)** — a downstream context protects its own model from an
  upstream context's model by translating at the boundary, so the upstream's design
  decisions (including bad ones) never leak into the downstream's domain model. This is
  the pattern you reach for when integrating with a legacy system or a third-party API
  whose model doesn't match your own domain language.
- **Open Host Service** — a context exposes a well-defined, published protocol/API
  designed for multiple consumers, rather than a bespoke integration per consumer.
- **Separate Ways** — two contexts have no meaningful integration; duplicating small
  amounts of logic independently is cheaper than coordinating.

### Worked example — an e-commerce context map
A mid-size e-commerce company has: **Catalog** (product info, search), **Inventory**
(stock levels, warehouse), **Pricing** (dynamic pricing, promotions), **Checkout**
(cart, order placement), **Fulfillment** (packing, shipping), and **Payments** (via a
third-party processor).

- Checkout depends on Pricing and Inventory to build an order — if the Pricing team
  ships features because Checkout specifically needs them (e.g., "expose a
  bulk-discount-eligibility check"), that's a **Customer–Supplier** relationship with
  Checkout as customer.
- Checkout integrates with the third-party payment processor's API by wrapping it in an
  **Anticorruption Layer** — a `PaymentGateway` interface in Checkout's own domain
  language ("authorize", "capture", "refund") that internally translates to the vendor's
  API shapes and error codes, so a future processor swap doesn't ripple through
  Checkout's domain model.
- Catalog and Inventory might use **Separate Ways** for certain low-value duplicated data
  (e.g., both keeping a cached product name) if keeping them perfectly synchronized isn't
  worth the coordination cost.
- Fulfillment consumes Order data published by Checkout via an **Open Host Service**
  (a documented order-events API) rather than a bespoke point-to-point integration,
  because multiple downstream contexts (Fulfillment, Analytics, Customer Notifications)
  all need the same order data.

Drawing this as a diagram — boxes for each bounded context, labeled arrows for each
relationship type — turns implicit, historically-accreted integration decisions into an
explicit, reviewable strategic artifact. It also often reveals problems: an
undocumented, ad hoc integration that turns out to be an accidental Conformist
relationship the team never chose deliberately, for instance.

### Worked example — finding a context boundary via a vocabulary clash
A healthcare scheduling system had one `Appointment` model shared between the
patient-facing booking UI and the clinical billing system. Billing needed
`Appointment.status` to track CPT-code-eligible states (`completed`, `no-show`,
`billable`); the booking UI needed states like `requested`, `confirmed`, `rescheduled`.
Developers kept adding statuses to one shared enum until it had 14 values, most
irrelevant to either side. Recognizing this as two bounded contexts — **Scheduling**
(patient-facing, its own `Appointment` with booking-relevant states) and **Billing**
(its own `BillableEncounter` with billing-relevant states), integrated via a domain event
`AppointmentCompleted` published from Scheduling and consumed by Billing — resolved the
mess. Each context now has a small, coherent model instead of one bloated compromise.

## Pros
- Keeps each model small, coherent, and locally consistent — a bounded context's model
  only needs to make sense for its own concerns, not for every stakeholder in the
  company simultaneously.
- Makes integration decisions explicit and reviewable instead of accidental; the context
  map is a genuinely useful architecture-level communication artifact for onboarding and
  for planning changes.
- Tends to align cleanly with team ownership boundaries and deployable units (services),
  which makes bounded contexts a natural fit for microservice decomposition when that
  architecture is otherwise justified.
- The Anticorruption Layer pattern specifically protects a well-modeled core domain from
  being distorted by a legacy or third-party system's design choices.

## Cons
- Drawing boundaries wrong (too fine-grained) creates excessive integration overhead —
  translation and coordination costs between contexts that didn't need to be separate.
- Drawing boundaries wrong (too coarse) reproduces the "big ball of mud" problem this
  concept exists to solve.
- Context mapping relationship types (Partnership, Conformist, ACL, etc.) require real
  organizational/political honesty about power dynamics between teams — naming a
  relationship "Conformist" can be an uncomfortable conversation.
- A context map, like the ubiquitous language it documents, goes stale if not revisited;
  treating it as a one-time diagram rather than a living artifact reduces its value over
  time.

## Alternatives
- **A single shared model / monolithic domain model** — simpler to reason about for
  genuinely small systems or very early-stage products where the cost of premature
  boundary-drawing outweighs the cost of a temporarily tangled model; many teams
  deliberately start here and extract bounded contexts later (see `ddd-distilled/09` on
  incremental adoption).
- **Service boundaries drawn purely by technical/infrastructure concerns** (e.g., "one
  service per database table," "one service per team headcount") — faster to decide but
  frequently misaligned with actual domain seams, producing chatty, tightly-coupled
  services that don't actually reduce complexity.
- **Data mesh / domain-oriented data ownership** — a related idea from the data
  engineering world that borrows bounded-context-style thinking for data products
  specifically; worth knowing as an adjacent pattern if the system in question is
  data-platform-shaped rather than transactional-service-shaped.

## When to use it
Use explicit bounded contexts whenever a system has more than one team, more than one
genuinely distinct sub-problem, or has already accumulated evidence of vocabulary clashes
(the "Product means different things to different people" smell). Draw a context map
whenever you're planning integration between two or more contexts, onboarding a new
engineer to a multi-service system, or diagnosing why two teams keep breaking each
other's assumptions.

## When NOT to use it
Don't split a small, single-team, single-model system into multiple bounded contexts
preemptively — that's the "distributed monolith" failure mode, where you pay integration
overhead for a boundary that doesn't yet correspond to a real seam in the domain. Start
with one context and extract new ones as the vocabulary-clash or team-boundary evidence
actually appears; `ddd-distilled/09` covers this incremental discovery process directly.

## Key takeaways / mental model
Ask "would a domain expert, standing here, agree on what this word means?" — where the
answer changes from yes to no, that's a bounded context boundary. Once you have two or
more contexts, the context map is how you make their relationship (who leads, who
follows, who translates) a deliberate engineering decision instead of an accident of
integration history.

## Self-check questions
1. Explain, in your own words, why "Product" can correctly mean different things in a
   Catalog context and an Inventory context without that being a design flaw.
2. Pick two systems (or subsystems) you've worked with that integrate with each other.
   Which context-mapping relationship pattern (Partnership, Customer-Supplier,
   Conformist, ACL, Open Host Service, Separate Ways) best describes their actual
   relationship — and was that relationship chosen deliberately or did it just happen?
3. Why is an Anticorruption Layer specifically useful when integrating with a legacy
   system or third-party vendor, as opposed to a Partnership relationship?
4. What symptom would tell you that you've drawn a bounded context boundary in the wrong
   place — either too fine or too coarse?

## References
- Domain-Driven Design Distilled (Vaughn Vernon), Chapter 4: "Context Mapping" (bounded
  context introduced in Chapter 2, "Strategic Design with Bounded Contexts and
  Ubiquitous Language").
- For the full catalog of context-mapping patterns and deeper case studies, see
  `domain-modeling/ddd-evans` and `domain-modeling/implementing-ddd`.
