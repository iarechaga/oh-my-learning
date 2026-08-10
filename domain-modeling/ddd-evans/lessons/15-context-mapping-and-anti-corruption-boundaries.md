---
id: ddd-evans/15
subject: ddd-evans
title: Context mapping and anti-corruption boundaries
slug: context-mapping-and-anti-corruption-boundaries
status: drafted
mastery:
seniority: staff
source: Domain-Driven Design (Eric Evans), Part IV, Chapter 14
prerequisites: [ddd-evans/14]
created: 2026-08-10
updated: 2026-08-10
---

# Context mapping and anti-corruption boundaries

## TL;DR
A context map documents, honestly, how bounded contexts (`ddd-evans/14`) actually relate to each other — which team is upstream/downstream of which, and under what integration pattern — and an anti-corruption layer is the specific defensive technique for protecting a downstream context's model from being deformed by an upstream context's model that it doesn't control and shouldn't have to mirror.

## The idea
Declaring bounded contexts isn't enough on its own — real systems have dozens of contexts that depend on each other in various ways, with various degrees of power, trust, and technical debt on each side. A context map makes those relationships explicit rather than left as tribal knowledge: which context can dictate terms to which (upstream/downstream), whether the relationship is cooperative or adversarial, and what specific integration pattern bridges them. Without an explicit map, teams discover the true nature of their dependencies the hard way — usually during an incident, when an upstream team's "small" schema change breaks a downstream team that had no idea it was relying on undocumented behavior.

The most consequential single pattern on a context map is the **anti-corruption layer (ACL)**: when your context depends on an upstream system whose model is poorly designed, legacy, third-party, or simply philosophically different from yours, you don't let that upstream model leak directly into your domain layer. Instead, you build a translation layer at the boundary that converts the upstream's concepts into your own context's clean, well-modeled terms — protecting your model's integrity from a model you don't control and can't fix.

## How it works

### Context map relationship patterns
- **Partnership** — two teams' contexts succeed or fail together; they coordinate closely and mutually adjust their interfaces as needed. Requires high trust and tight coordination.
- **Shared kernel** — two contexts deliberately share a small, explicitly agreed subset of the model (some shared code or schema) because the overlap is small and stable enough that duplicating it would be worse than a carefully managed shared piece. Any change to the shared kernel requires both teams' agreement — it's a shared, jointly-owned liability, not a free convenience.
- **Customer/Supplier** — a clear upstream (supplier) and downstream (customer) relationship where the downstream team has real influence over the upstream team's roadmap (perhaps through a shared organization and a negotiation process), so upstream changes account for downstream needs.
- **Conformist** — the downstream team has no influence over the upstream team (a large vendor, a different powerful internal team) and simply conforms to whatever model the upstream provides, accepting its shape as-is rather than fighting it. Simpler to build initially, but the downstream context's model quality is now hostage to the upstream's design choices.
- **Anti-corruption layer** — the downstream team refuses to conform; instead it builds an explicit translation layer so its own domain model stays clean regardless of what the upstream looks like. More work than conforming, but protects the downstream context's design integrity.
- **Open host service / published language** — the upstream team, recognizing it has many downstream consumers, deliberately publishes a well-documented, stable public interface/protocol (rather than letting each downstream figure out translation independently), reducing the ACL burden for everyone depending on it.
- **Separate ways** — the two contexts decide integration isn't worth the cost at all, and simply don't integrate, duplicating whatever small overlap exists independently.

### Worked example: an anti-corruption layer around a legacy inventory system
Suppose a modern `ordering` bounded context needs stock-availability data from a twenty-year-old legacy inventory system whose API represents everything as flat, poorly-named codes (`ITM_STAT` values of `"A"`, `"B"`, `"H"` meaning "available," "backordered," "held," with no further documentation, and quantities represented as signed integers where negative means something specific to that legacy system's internal accounting quirks). Without an ACL, this legacy vocabulary and its quirks would leak directly into the `ordering` context's domain layer — `if legacyStockCode == "B"` scattered through `Order`-related business logic, coupling the modern context's model integrity to a system it has zero control over and that could change its undocumented behavior at any time.

```
# anti-corruption layer, living at the boundary of the ordering context
class LegacyInventoryAdapter:
    def stock_status_for(self, product_id: ProductId) -> StockStatus:
        raw = self._legacy_client.get_item_status(product_id.legacy_code())
        return self._translate(raw)

    def _translate(self, raw: LegacyItemStatus) -> StockStatus:
        mapping = {"A": StockStatus.AVAILABLE, "B": StockStatus.BACKORDERED, "H": StockStatus.ON_HOLD}
        if raw.code not in mapping:
            raise UnrecognizedLegacyStatusError(raw.code)
        return mapping[raw.code]
```
`Order` and every other class inside the `ordering` context only ever sees a clean `StockStatus` enum expressed in the `ordering` context's own ubiquitous language (`ddd-evans/01`) — none of them know or care that the underlying system uses single-letter codes with idiosyncratic history. If the legacy system's API changes, or if it's eventually replaced entirely, only `LegacyInventoryAdapter` needs to change; the entire rest of the `ordering` domain layer is insulated.

### Choosing the right relationship, not defaulting to the most defensive one
Building a full anti-corruption layer for every single upstream dependency is expensive, and not always warranted — the choice of relationship pattern should reflect the actual situation:
- If the upstream is well-designed, actively maintained with your needs in mind, and trustworthy, **conformist** or **open host service** consumption may be perfectly fine and considerably cheaper than building a translation layer for no real protective benefit.
- If the upstream is poorly modeled, legacy, unreliable, or has interests that diverge from yours (a third-party vendor optimizing for their own roadmap, not yours), an **anti-corruption layer** earns its cost by protecting your model's integrity.
- If two contexts are tightly coupled by necessity and coordination is realistic, **partnership** or a carefully scoped **shared kernel** can be cheaper and more honest than pretending they're fully independent.

### Worked example: the context map exposes a hidden organizational risk
A team drew their context map honestly for the first time and discovered that their core-domain `pricing` context (`ddd-evans/13` — a genuinely differentiating part of the business) was in a **conformist** relationship with a third-party tax-calculation vendor, meaning the vendor's data model shaped how the core domain's pricing rules were expressed, with no protective layer in between. Once visualized on the map, this was recognized as a serious mismatch — a core domain, which per `ddd-evans/13` deserves the most design investment and protection, was structurally hostage to an external vendor's undocumented API changes. The map itself, simply by making the relationship explicit and visible, drove the decision to invest in an anti-corruption layer around the tax vendor specifically because of the core-domain classification — a decision that wouldn't have been made consciously without the map surfacing the mismatch.

## Pros
- Makes cross-context dependencies and power dynamics explicit and discussable, instead of implicit and only discovered during incidents.
- Anti-corruption layers let a downstream context maintain design integrity and supple design (`ddd-evans/12`) regardless of how poorly modeled or unstable an upstream dependency is.
- Provides a shared vocabulary (partnership, conformist, ACL, etc.) for architecture discussions about integration, replacing ad hoc, inconsistent descriptions of the same handful of real patterns.

## Cons
- Building and maintaining an anti-corruption layer is genuine ongoing engineering work — translation code, tests for the translation itself, and effort kept in sync with upstream changes.
- Drawing an honest context map requires organizational visibility and candor that can be politically uncomfortable — accurately describing a relationship as "conformist" to a more powerful team can surface uncomfortable power dynamics.
- Overusing ACLs defensively, even against trustworthy, well-designed upstream dependencies, adds unnecessary translation overhead for no real protective benefit.

## Alternatives
- **Conformist consumption without any translation layer** — appropriate specifically when the upstream is trustworthy and well-modeled, as discussed above; cheaper, but only safe under those conditions.
- **Shared kernel** — appropriate for tightly coupled contexts where duplicating a small, stable overlap would genuinely be worse than jointly managing a shared piece; requires unusually high inter-team trust and coordination discipline to avoid becoming a source of coupling-related friction itself.
- **API gateway / BFF (backend-for-frontend) patterns** — a related but distinct integration technique from the broader software-architecture world, sometimes used to achieve similar translation goals at a different layer (presentation-facing aggregation rather than domain-model protection); complementary to, not a replacement for, an ACL protecting the domain layer specifically.

## When to use it
Draw a context map whenever a system has more than a couple of bounded contexts interacting, so the team has an honest, shared picture of dependencies. Reach specifically for an anti-corruption layer whenever a downstream context (especially a core domain, per `ddd-evans/13`) depends on an upstream model that's poorly designed, unstable, or outside your influence.

## When NOT to use it
Don't build an anti-corruption layer reflexively against every dependency — for a trustworthy, well-modeled, cooperative upstream, the translation-layer cost isn't justified by a protection benefit that isn't actually needed; conformist or open-host-service consumption is the right, cheaper call there.

## Key takeaways / mental model
The context map answers "who actually has power over whom, and how do we bridge the gap honestly?" The anti-corruption layer answers "how do I keep my model clean when I don't control, and can't trust, the model on the other side of this dependency?" Reach for the ACL specifically where the model on the other side would otherwise deform your own if allowed to leak in directly.

## Self-check questions
1. In the legacy inventory example, what specific coupling would exist if `LegacyInventoryAdapter` didn't exist and `"B"`/`"H"` status codes leaked directly into `Order`-related business logic?
2. Explain the difference between a "conformist" relationship and an "anti-corruption layer" relationship, and describe a real (or plausible) situation where each would be the right call.
3. Why did discovering that the `pricing` context was "conformist" toward a tax vendor matter more, specifically, because `pricing` was previously classified as a core domain (`ddd-evans/13`)?
4. What organizational, not just technical, value does an honestly-drawn context map provide, beyond documenting integration code?

## References
- Domain-Driven Design: Tackling Complexity in the Heart of Software (Eric Evans), Chapter 14: "Maintaining Model Integrity" (Context Map, Anti-Corruption Layer, and relationship-pattern sections).
