---
id: learning-ddd/04
subject: learning-ddd
title: Context maps and relationship patterns
slug: context-maps-and-relationship-patterns
status: drafted
mastery:
seniority: senior
source: Learning Domain-Driven Design (Vlad Khononov), Part I, Chapter 3 (continued) - "Context Mapping"
prerequisites: [learning-ddd/02, learning-ddd/03]
created: 2026-08-10
updated: 2026-08-10
---

# Context maps and relationship patterns

## TL;DR
A context map is a diagram of a system's bounded contexts and, critically, the *power dynamics and cooperation style* of the relationships between them - not just "these two things talk to each other" but "who is upstream, who is downstream, and how much influence does the downstream side have over the upstream model." Naming the relationship pattern explicitly (Partnership, Customer-Supplier, Conformist, Anticorruption Layer, Open Host Service, and others) turns an implicit, often-contentious integration into a deliberate, negotiated design decision.

## The idea
Once bounded contexts exist (`learning-ddd/03`), they still need to cooperate - an Order context needs to know about Inventory availability; a Billing context needs data from Subscription Management. How that cooperation happens is not a purely technical question (REST vs. messaging - that's `learning-ddd/11`); it is fundamentally an **organizational and power question**: which team's model wins when the two contexts disagree, and how much protective translation does the downstream side maintain against upstream changes it doesn't control?

Khononov (building on Evans's original context-mapping patterns) organizes relationships along an upstream/downstream axis. The **upstream** context influences or dictates terms; the **downstream** context depends on and must adapt to the upstream's model or API. The relationship *pattern* describes the social contract governing that dependency - whether it's negotiated as equals, imposed unilaterally, or mediated through a deliberate translation layer.

## How it works

### The core patterns

**Partnership** - two teams succeed or fail together; they coordinate closely and evolve their contexts' interfaces in lockstep, with mutual veto power over breaking changes. Appropriate when two contexts are tightly interdependent and owned by teams that can realistically coordinate release schedules (e.g., a small startup's Checkout and Payment contexts, both owned by overlapping engineers). Example: an e-commerce company's Checkout and Fraud-Scoring contexts, built by the same small team, where a change to the checkout flow and a change to fraud-signal collection are frequently co-designed in the same planning session.

**Shared Kernel** - two contexts deliberately share a small, explicitly-agreed common model (a subset of code or schema) that both teams jointly own and change together. High coordination cost, so kept intentionally small. Example: a shared `Money` value object (currency + amount + rounding rules) used identically by both a Billing context and a Payout context, because divergence there would cause real financial-reconciliation bugs.

**Customer-Supplier** - a formalized upstream/downstream relationship where the downstream (customer) has organized influence over the upstream (supplier) team's roadmap - the supplier plans around the customer's needs, similar to an internal product/vendor relationship, but both sides have genuine negotiating power. Example: an internal Payments Platform team (upstream/supplier) that takes roadmap input from the several product teams (downstream/customers) that depend on it, prioritizing their needs in planning.

**Conformist** - the downstream context simply adopts the upstream's model wholesale, with no translation layer, because the downstream has no negotiating power (or the cost of translating isn't worth it). Common when integrating with a large external platform. Example: a small company integrating with a major cloud provider's IAM model conforms to that provider's role/permission vocabulary directly rather than trying to negotiate changes or build a translation layer around it.

**Anticorruption Layer (ACL)** - the downstream context builds an explicit translation layer that converts the upstream's model into the downstream's own clean, purpose-fit model, so the upstream's design quirks, legacy structure, or future changes don't leak into and corrupt the downstream's domain model. Example: a modern Order-Management context integrating with a 20-year-old legacy ERP system wraps every call to the ERP behind an ACL that translates the ERP's cryptic status codes and denormalized fields into the Order-Management context's own clean `OrderStatus` value object - so if the ERP is ever replaced, only the ACL needs to change, not the domain model.

**Open Host Service (OHS)** - the upstream context publishes a well-designed, intentionally stable public API/protocol meant to serve many downstream consumers, rather than negotiating a bespoke integration with each one. Often paired with a **Published Language** - a documented, versioned schema (e.g., a public API's JSON schema, or an industry-standard format like HL7 in healthcare) that formalizes the OHS's contract. Example: a Shipping-Rates context exposes a stable, versioned REST API used identically by Checkout, the mobile app backend, and a third-party marketplace integration, rather than maintaining three separate bespoke integrations.

**Separate Ways** - the pragmatic decision that two contexts do not need to integrate at all; any apparent overlap is small enough that duplicating a little logic independently is cheaper than building and maintaining an integration. Example: an internal admin-reporting tool and the customer-facing product both need "count of active users" but compute it independently, from different sources, because the two numbers don't need to reconcile and the integration cost isn't worth it.

**Big Ball of Mud** - not a pattern to adopt deliberately, but a name for the state where no boundaries or relationships have been consciously designed at all - included on the map as a diagnostic label for "this part of the system needs the analysis in `learning-ddd/03` applied to it before its relationships can even be named."

### Worked example - building a context map for a logistics company
Contexts: Route Planning (core), Fleet Maintenance (supporting), Customer Notifications (supporting), Billing (core), Third-Party Carrier Integration (generic-ish, external).

- Route Planning <-> Fleet Maintenance: **Partnership** - both owned by the operations engineering team, changes to vehicle-availability data and route algorithms are co-designed.
- Route Planning -> Customer Notifications: **Open Host Service** - Route Planning publishes a stable "shipment status changed" event stream that Notifications (and potentially future consumers) subscribe to, without Route Planning needing to know who's listening.
- Billing -> Third-Party Carrier Integration: **Anticorruption Layer** - the external carrier APIs have inconsistent, carrier-specific rate and surcharge formats; Billing wraps them behind an ACL that normalizes everything into the company's own `ShippingCost` model before it ever touches Billing's domain logic.
- Fleet Maintenance -> a government vehicle-inspection regulatory API: **Conformist** - the company has zero influence over the regulator's data model and integrating cheaply matters more than translating it.

### Worked example - SaaS billing and a payment processor
Subscription Management (core, internal) integrates with Stripe (external, generic per `learning-ddd/02`). This is a textbook **Anticorruption Layer** situation: Stripe's API models (customers, payment methods, invoices, subscription objects) are excellent for Stripe's general-purpose use case but don't match this company's specific billing vocabulary (e.g., Stripe's "subscription" concept doesn't natively capture this company's seat-based proration rules). The ACL translates Stripe's webhooks and API responses into the company's own domain events and models, so a future payment-processor migration only touches the ACL.

## Pros
- Makes an otherwise invisible, often unconsciously-adopted power dynamic between teams explicit and negotiable, surfacing conflicts (e.g., "we've been Conformists to a team that should be treating us as a Customer") before they cause chronic friction.
- Gives teams a shared vocabulary for integration design reviews - "should this be an ACL or should we just Conform?" is a concrete, answerable design question.
- Directly informs the integration mechanism choice in `learning-ddd/11` and the deployment/team topology questions in `learning-ddd/14`.
- Surfaces where translation investment (ACLs) is worth its cost versus where it's overkill (Conformist is fine).

## Cons
- Requires honest organizational self-assessment - naming a relationship "Conformist" can feel (or be) an admission of low negotiating power, which is sometimes politically uncomfortable to state plainly.
- A context map is a living document; if it isn't revisited as team structures and priorities change, it silently goes stale and stops matching reality.
- Overuse of Anticorruption Layers "just in case" adds real translation-code maintenance burden for integrations that were never actually going to change underneath you.
- The taxonomy can be applied too mechanically - forcing every relationship into a named pattern when the actual situation is a hybrid or doesn't cleanly fit any single label.

## Alternatives
- **No explicit context map, ad hoc integration** - the default in most codebases; works until the number of contexts and cross-team dependencies grows past what individual engineers can hold in their heads, at which point integration decisions become inconsistent and political friction goes unaddressed.
- **Pure service-mesh/API-gateway-level governance** - manages the technical/network aspects of service-to-service calls (rate limiting, auth, routing) but says nothing about the deeper question of whose model wins conceptually; complements, but does not replace, context mapping.
- **`ddd-evans`'s original nine-pattern catalog** - Evans's original terminology (this lesson's patterns descend directly from it); Khononov's treatment streamlines and re-orders the patterns for practical adoption alongside the subdomain classification from `learning-ddd/02`.

## When to use it
Draw (or update) a context map whenever a new bounded context is introduced, whenever an integration between two existing contexts is being designed or is causing recurring friction, and as a periodic architecture review artifact for any system with more than a couple of bounded contexts and more than one team.

## When NOT to use it
Skip formal context mapping for a single-team, single-bounded-context system - there's no cross-context relationship to map yet. Also avoid over-formalizing the map into permanent governance documentation for a fast-moving early-stage system where contexts and teams are still being discovered; a lightweight, frequently-redrawn sketch serves better than a heavyweight artifact nobody updates.

## Key takeaways / mental model
For every pair of bounded contexts that need to cooperate, ask three questions in order: **(1)** Is one side upstream (dictating terms) or are they equals (Partnership/Shared Kernel)? **(2)** If upstream/downstream, does the downstream have real negotiating power (Customer-Supplier) or none (Conformist/ACL)? **(3)** If the downstream has no power but the upstream's model is a poor fit or a legacy risk, is a translation layer (ACL) worth its maintenance cost, or is straight conformance good enough? The answers name the relationship pattern - and naming it makes the previously-implicit power dynamic something the team can consciously choose, not just inherit.

## Self-check questions
1. Pick two bounded contexts (or services) you've worked with that integrate. Which relationship pattern actually describes their relationship today? Is that the pattern the team would choose deliberately, or did it happen by default?
2. Why would a team choose an Anticorruption Layer over simply Conforming to an upstream model, given that an ACL costs more to build and maintain?
3. Explain the difference between Customer-Supplier and Conformist in terms of who has influence over the upstream team's roadmap.
4. Describe a situation where "Separate Ways" - deliberately not integrating two contexts - is the right call, even though the two contexts have some conceptual overlap.

## References
- Learning Domain-Driven Design (Vlad Khononov), Part I, Chapter 3: "Context Mapping".
- Domain-Driven Design (Eric Evans, 2003), Part IV, "Strategic Design" - see `domain-modeling/ddd-evans`.
- Implementing Domain-Driven Design (Vaughn Vernon) - context mapping in practice, see `domain-modeling/implementing-ddd`.
