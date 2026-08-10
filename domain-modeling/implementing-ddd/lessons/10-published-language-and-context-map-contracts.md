---
id: implementing-ddd/10
subject: implementing-ddd
title: Published language and context-map contracts
slug: published-language-and-context-map-contracts
status: drafted
mastery:
seniority: staff
source: Implementing Domain-Driven Design (Vaughn Vernon), Chapter 3: Context Maps
prerequisites: [implementing-ddd/03]
created: 2026-08-10
updated: 2026-08-10
---

# Published language and context-map contracts

## TL;DR
A context map names, for every pair of related bounded contexts, the specific integration relationship between them (Partnership, Customer/Supplier, Conformist, Anti-Corruption Layer, Open Host Service with Published Language, Shared Kernel, Separate Ways) — making explicit, on paper and in the org chart, power dynamics and coupling that would otherwise stay implicit and cause friction only discovered when something breaks.

## The idea
Once a system has more than one bounded context (`implementing-ddd/03`), those contexts inevitably need to exchange information — and the *nature* of that exchange relationship varies enormously depending on team dynamics, who has authority over the shared contract, and how much either side is willing to accommodate the other. Two teams that trust each other and coordinate closely can share a contract collaboratively (Partnership); a team consuming a well-established external API has no influence over its shape and must simply accept it (Conformist); a team publishing an API for many consumers needs to commit to a stable, well-documented contract (Open Host Service with Published Language) rather than letting every consumer negotiate a bespoke integration. Evans catalogued these relationship patterns (see `ddd-evans`); Vernon's contribution is treating the context map as a living, essential architectural artifact that a team draws explicitly and keeps current — not an academic exercise, but the document that answers "who breaks if this contract changes, and who has to accommodate whom."

## How it works

### The core relationship patterns, and when each applies
- **Partnership** — two teams' contexts succeed or fail together; they coordinate releases and evolve their shared contract collaboratively, with roughly equal say. Appropriate when both contexts are core to the same larger initiative and no team has more authority than the other.
- **Customer/Supplier** — one context (supplier) provides functionality another (customer) depends on, and the customer has enough organizational leverage to influence the supplier's roadmap and priorities (e.g. an internal platform team building for a specific, prioritized product team).
- **Conformist** — the downstream context has no leverage over the upstream (a third-party SaaS API, or a powerful internal team with its own priorities that won't accommodate you) and simply accepts the upstream model as-is, translating nothing, adapting its own model to match.
- **Anti-Corruption Layer (ACL)** — the downstream context accepts the upstream's contract exists but refuses to let the upstream's model leak into its own — it builds an explicit translation layer at the boundary (`implementing-ddd/11`) so its internal model stays clean and independent of the upstream's design choices, even bad ones.
- **Open Host Service (OHS) with Published Language (PL)** — the upstream context publishes a well-defined, documented, versioned protocol/schema (the Published Language) that any number of downstream consumers can integrate against, rather than negotiating a bespoke contract per consumer; this is the pattern that scales when many contexts need to integrate with one.
- **Shared Kernel** — two teams explicitly agree to share a small, deliberately limited subset of the model (and its code), coordinating any change to that shared piece tightly; used sparingly, when the integration cost of full separation exceeds the coordination cost of sharing.
- **Separate Ways** — two contexts have no meaningful integration need; explicitly deciding *not* to integrate, and duplicating minor overlapping functionality independently rather than paying an integration cost for a relationship not worth having.

### Worked example — e-commerce platform context map
*Catalog* (upstream) publishes an Open Host Service with a Published Language — a documented product-data contract — because many downstream contexts (*Pricing*, *Search*, *Recommendations*) need product data and it doesn't scale for *Catalog* to negotiate a bespoke contract with each. *Pricing* and *Checkout* have a Partnership relationship, since a pricing model change (new discount stacking rules) and checkout's ability to apply it usually ship together and are owned by teams collaborating closely. *Payments* uses a third-party PSP (payment service provider) API the team has zero influence over — that's a Conformist-at-best relationship toward the external vendor, mediated internally through an Anti-Corruption Layer (`implementing-ddd/11`) so the vendor's clunky API shapes don't leak into the domain model.

### The Published Language as a concrete artifact
Vernon is specific that a Published Language isn't just "the API" — it's a deliberately designed, documented data format/schema (often, but not necessarily, decoupled from any single technology — a versioned JSON schema, a Protobuf/Avro definition, an industry-standard format) that's explicitly the contract, versioned and evolved with backward-compatibility discipline, distinct from whatever internal representation the publishing context actually uses. A domain event (`implementing-ddd/07`) that crosses a bounded-context boundary is a very common form a Published Language takes.

### Drawing and maintaining the map
A context map is typically a simple diagram — boxes for bounded contexts, labeled arrows for relationships — but its value comes from being *current* and *honest*, not from formal notation. Vernon recommends drawing it collaboratively with the teams involved (since it encodes real organizational relationships, not just technical ones) and revisiting it whenever a new integration is added or an existing relationship's power dynamic shifts (a Conformist relationship toward a vendor that later becomes willing to negotiate custom contract terms should be re-labeled, since that changes the appropriate integration strategy).

## Pros
- Makes coupling and power dynamics between teams explicit and discussable, instead of leaving them as tribal knowledge that only surfaces painfully when an upstream team ships a breaking change with no warning.
- Gives a team a vocabulary to justify integration-effort decisions to stakeholders ("we need an ACL here because we're a Conformist to a vendor API we don't control") rather than the decision looking like unnecessary extra engineering work.
- Scales integration strategy deliberately — Open Host Service with Published Language specifically solves the "many consumers, one producer" scaling problem that ad hoc point-to-point contracts don't.

## Cons
- Requires organizational honesty that's sometimes politically uncomfortable — labeling a relationship "Conformist" toward another internal team is effectively saying "we have no leverage over them," which can be an awkward thing to put in writing.
- A context map can go stale quickly in a fast-moving organization if no one owns keeping it updated, at which point it becomes actively misleading rather than merely unhelpful.
- Choosing the wrong relationship pattern (e.g. treating a vendor relationship as a Partnership when it's really Conformist) leads to wasted effort trying to negotiate contract changes with a party that has no intention of accommodating you.

## Alternatives
- **Informal, undocumented integration agreements** — teams coordinate integration details ad hoc over chat/meetings with no written context map; faster to start for a small number of contexts owned by closely-collaborating teams, but the relationship's actual power dynamic stays tribal knowledge and tends to surface painfully only when someone new joins or an upstream team changes its contract without warning.
- **API gateway / service mesh contracts as the only documentation** — rely on API gateway route definitions or service-mesh configuration as the de facto record of what talks to what; captures the technical wiring but not the *relationship* (who accommodates whom, who has leverage), which is the actually load-bearing information a context map is meant to convey.
- **Single shared API-design guild/standard** — instead of naming a distinct relationship per context pair, impose one uniform API design standard across the whole organization and expect every context to conform to it; reduces the need to reason about per-relationship dynamics, but flattens genuinely different power dynamics (a Partnership vs. a Conformist-to-a-vendor relationship) into one-size-fits-all tooling that doesn't fit every case.

## When to use it
Whenever two or more bounded contexts (`implementing-ddd/03`) need to exchange data or trigger behavior in each other — before writing the integration code, name the relationship explicitly, because the relationship determines the right integration pattern (ACL, OHS/PL, Shared Kernel, etc.), not the other way around.

## When NOT to use it
For a single-team, single-bounded-context system with no external integrations, a formal context map is unnecessary ceremony — there's nothing to map. It also adds limited value for genuinely one-off, low-stakes integrations where "Separate Ways" or a quick point-to-point call is clearly sufficient and unlikely to need renegotiation.

## Key takeaways / mental model
Before writing any integration code between two bounded contexts, ask: "who has the leverage here — do we shape the contract together, does the other side dictate it to us, or do we publish it for many others to consume?" That answer names the context-map relationship, and the relationship — not personal preference — should determine whether you build an ACL, adopt Conformist, negotiate a Partnership, or publish an Open Host Service.

## Self-check questions
1. Pick two systems/services you've worked with that integrate with each other. Which context-map relationship best describes their actual dynamic, and how would you know if you had it wrong?
2. Why does an Open Host Service with Published Language scale better than negotiating a bespoke contract per consumer, and at what point does a Customer/Supplier or Partnership integration stop scaling that way?
3. A team is a Conformist toward a legacy internal system they have no influence over, but that legacy system's model is actively harmful to copy into their own domain model. What pattern addresses that specific tension, and why is Conformist alone insufficient?
4. Describe a scenario where "Separate Ways" — deliberately not integrating two contexts, even though they have some conceptual overlap — is the right call.

## References
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 3: "Context Maps".
- Domain-Driven Design (Eric Evans) — Part IV, "Strategic Design" — the original context-map relationship patterns; see `ddd-evans`.
