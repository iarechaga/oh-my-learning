---
id: implementing-ddd/11
subject: implementing-ddd
title: Anti-corruption layers and translation boundaries
slug: anti-corruption-layers-and-translation-boundaries
status: drafted
mastery:
seniority: staff
source: Implementing Domain-Driven Design (Vaughn Vernon), Chapter 3 (Context Maps) and Chapter 13 (Integrating Bounded Contexts)
prerequisites: [implementing-ddd/03, implementing-ddd/10]
created: 2026-08-10
updated: 2026-08-10
---

# Anti-corruption layers and translation boundaries

## TL;DR
An anti-corruption layer (ACL) is a deliberate translation boundary between your bounded context and an upstream system whose model you don't control and don't want leaking in — it converts the upstream's data/vocabulary into your own ubiquitous language at the point of entry, so the rest of your model never has to know the upstream's shapes, quirks, or legacy baggage exist.

## The idea
When your bounded context integrates with an upstream system — a legacy monolith, a third-party vendor API, an internal team's context you're a Conformist toward (`implementing-ddd/10`) — the path of least resistance is to let the upstream's data shapes flow straight through into your domain model: deserialize their JSON directly into what becomes your `Order` class, reuse their enum values, adopt their field names. This feels efficient at first (less mapping code to write) but it means your model is no longer really yours — it's shaped by someone else's design decisions, including whatever technical debt, historical accidents, or vocabulary mismatches that upstream system carries. Vernon calls this corruption, echoing Evans, because the pollution is exactly the kind bounded contexts (`implementing-ddd/03`) exist to prevent — except this time the boundary being violated is the boundary between *your* clean model and an external one, not between two of your own contexts. An anti-corruption layer is the explicit fix: a translation boundary, usually implemented as an adapter plus a translator, that converts everything crossing from the upstream system into your own model's vocabulary and shape before your domain logic ever touches it.

## How it works

### Structure: Facade, Adapter, Translator
A typical ACL has three collaborating pieces:
1. **Facade** — a simplified entry point your own code calls, hiding the fact that a translation and an external call are happening behind it.
2. **Adapter** — handles the mechanics of talking to the upstream system (HTTP client, SOAP client, legacy database query) — the technical integration detail.
3. **Translator** — converts the upstream's raw response shape into your own domain model's types (value objects, enums, aggregates) — the actual anti-corruption work.

**Worked example — e-commerce integrating a legacy warehouse system.** The legacy system exposes inventory data as `{ "itmCd": "SKU123", "qtyOnHnd": 42, "whseLoc": "A-14-3", "stat": "A" }` — cryptic field names, a single-character status code (`A` = available, `H` = held, `D` = discontinued) with no documented enum, mixing warehouse-internal concerns into what your `Inventory` bounded context actually needs.
```
// Adapter: talks to the legacy system, returns its raw shape
class LegacyWarehouseAdapter {
    LegacyInventoryRecord fetch(String itemCode) { ... }  // raw { itmCd, qtyOnHnd, whseLoc, stat }
}

// Translator: converts raw legacy shape into YOUR domain vocabulary
class LegacyInventoryTranslator {
    StockLevel translate(LegacyInventoryRecord raw) {
        return new StockLevel(
            new Sku(raw.itmCd()),
            new Quantity(raw.qtyOnHnd()),
            translateStatus(raw.stat())   // 'A'/'H'/'D' -> your own StockStatus enum
        );
    }
    private StockStatus translateStatus(String legacyCode) {
        return switch (legacyCode) {
            case "A" -> StockStatus.AVAILABLE;
            case "H" -> StockStatus.ON_HOLD;
            case "D" -> StockStatus.DISCONTINUED;
            default -> throw new UnknownLegacyStatusException(legacyCode);
        };
    }
}

// Facade: what your domain/application code actually calls
class InventoryLookupFacade {
    StockLevel lookUp(Sku sku) {
        return translator.translate(adapter.fetch(sku.value()));
    }
}
```
Everything downstream of `InventoryLookupFacade` deals only in `StockLevel`, `Sku`, `StockStatus` — your own domain vocabulary — with zero knowledge that `itmCd` or the single-character status codes exist.

### Deciding what to translate — and what to intentionally drop
A well-designed ACL is not a 1:1 field mapping — it's an opportunity to translate only what your bounded context actually needs, in the shape it needs. If the legacy system provides twelve fields and your `Inventory` context genuinely needs three, the translator produces a `StockLevel` value object with three fields, not twelve — resisting the temptation to carry the rest through "just in case," which would let upstream complexity leak in by volume even if each individual field were named well.

### ACLs and error/failure translation
The upstream system's failure modes (timeouts, malformed responses, legacy-specific error codes) also need translation — your domain/application code shouldn't have to catch a `SoapFaultException` or interpret a legacy error code directly; the ACL should translate failures into your own exception vocabulary (`InventoryLookupFailedException`) so calling code deals with concepts from its own model, consistently, regardless of which upstream system is behind the ACL.

**Worked example — banking integrating a third-party credit bureau API.** The credit bureau returns a proprietary risk score on an odd 300-950 scale with vendor-specific tier labels (`"PRIME_PLUS"`, `"SUBPRIME_TIER_2"`). An ACL translates this into your own `CreditRisk` value object with a normalized `RiskTier` enum meaningful in your own domain's ubiquitous language, and if the bureau is unreachable, the ACL translates that into your own `CreditCheckUnavailable` domain-level signal rather than letting a vendor-specific HTTP exception type propagate into your domain/application code.

## Pros
- Keeps your bounded context's model genuinely clean and independent, letting it evolve on your own schedule even if the upstream system is legacy, poorly designed, or slow to change — the ACL absorbs that instability at a single, well-understood boundary.
- Concentrates all upstream-specific knowledge (field names, quirky enums, error codes) in one place, making it far easier to update when the upstream system changes its contract — one translator to fix, not scattered call sites throughout the domain model.
- Makes testing the rest of your domain model trivial with respect to the upstream system — mock the ACL's facade interface, and your domain logic never needs a real (or even fake) upstream system to be exercised in tests.

## Cons
- Real, non-trivial engineering cost: writing and maintaining a translation layer is extra code that a direct pass-through integration wouldn't need, and it has to be kept in sync as either side's model evolves.
- Can become a performance bottleneck or an added point of failure if not designed carefully (an ACL making a synchronous call per request, for example) — sometimes it needs its own caching or asynchronous strategy layered on top.
- Overusing the pattern — building an elaborate ACL for a trivial, stable, well-designed upstream API that would cause no real corruption if consumed directly — is wasted engineering effort; judgment is needed about which upstream integrations actually pose a corruption risk worth guarding against.

## Alternatives
- **Conformist integration (no translation)** — accept the upstream's model as-is, adapting your own model to match it directly; appropriate when the upstream is well-designed, unlikely to change in disruptive ways, and adapting to it is genuinely cheaper than translating away from it (see `implementing-ddd/10`).
- **Shared Kernel** — instead of translating at a boundary, explicitly share a subset of the model/code with the upstream team, coordinating changes jointly; only viable when there's a real collaborative relationship with the upstream team, which is rarely the case for legacy systems or external vendors.
- **Strangler-fig migration** — rather than maintaining a permanent ACL against a legacy system indefinitely, use the ACL as a deliberately temporary seam while incrementally replacing the legacy system's functionality behind it, eventually removing both the legacy system and the ACL once migration completes.

## When to use it
Whenever integrating with an upstream system whose model is outside your control, actively low-quality, legacy, or simply philosophically different from your own bounded context's model — especially when that upstream feeds a core domain (`implementing-ddd/01`) you need to keep clean and stable.

## When NOT to use it
Skip the ACL when the upstream system's model is genuinely well-designed, stable, and close enough to your own vocabulary that translation would just be needless indirection — or for a Partnership-style relationship (`implementing-ddd/10`) where both sides are actively co-designing the contract and corruption risk is low by construction.

## Key takeaways / mental model
Ask, at any integration point: "if this upstream system changed its data shapes or vocabulary tomorrow, how much of my own domain model would have to change with it?" If the honest answer is "a lot, because their shapes flow straight through," that's the corruption an ACL exists to prevent — put a translator at the boundary so the blast radius of an upstream change is contained to one place.

## Self-check questions
1. Describe an integration you've built (or seen) where an upstream system's raw data shape flowed directly into the internal model with no translation layer. What broke, or could have broken, when the upstream changed?
2. Why should an ACL's translator produce only the fields your bounded context actually needs, rather than a complete 1:1 mapping of everything the upstream provides?
3. Explain why translating the upstream's *failure modes*, not just its success-path data, is part of a complete anti-corruption layer.
4. When would building an ACL be over-engineering for a given integration? What signals would tell you the upstream poses low corruption risk?

## References
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 3: "Context Maps" (Anti-Corruption Layer pattern).
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 13: "Integrating Bounded Contexts".
- Domain-Driven Design (Eric Evans) — the original Anti-Corruption Layer pattern; see `ddd-evans`.
