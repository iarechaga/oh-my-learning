---
id: building-microservices/02
subject: building-microservices
title: "Modelling Services Around Business Domains"
slug: modelling-services
status: drafted
mastery: 
seniority: senior
source: "Building Microservices, 2nd ed. (Sam Newman), Chapter 2"
prerequisites: [building-microservices/01]
created: 2026-08-10
updated: 2026-08-10
---

# Modelling Services Around Business Domains

## TL;DR
Find service boundaries by modeling the business domain, not the technology stack: group the code, data, and behavior that change together for the same business reason into one service, and separate what changes for different reasons. Domain-Driven Design's **bounded context** is the tool Newman leans on — each bounded context becomes a strong candidate for a service boundary.

## The idea
Once you've accepted that microservices are the right trade-off (Lesson 01), the next and much harder question is: *where do you cut?* Cut in the wrong place and you get services that are constantly calling each other back and forth for a single business operation (tight coupling, poor cohesion — Lesson 03), or services that have to change in lockstep because they modeled the same concept differently.

The instinctive first cut for many engineers is **technical layering**: a "presentation service," a "business logic service," a "data access service." This feels natural because it mirrors how monolithic codebases are often organized internally (controllers / services / repositories). But it's usually the wrong axis to split on for microservices, because a single business change — "add a discount code field to checkout" — now requires changing all three layers, which means changing and redeploying three services together. You've recreated the monolith's coordination problem, just with network calls added on top.

The better axis, which Newman adopts from Eric Evans's *Domain-Driven Design* (DDD), is to split along **business capability boundaries**: group together the things that serve one cohesive piece of business functionality, regardless of technical layer, and separate things that serve different business functions even if they look technically similar.

DDD gives two ideas that make this concrete:

- **Domain model** — a model of the business's concepts and rules, expressed in the language the business actually uses (the "ubiquitous language"). Not a generic CRUD schema — a model of *this specific business's* view of, say, "Order," "Customer," and "Payment."
- **Bounded context** — the key insight is that a single term like "Customer" does not mean the same thing everywhere in a large business. To Sales, a Customer is a lead with a pipeline stage and a sales rep. To Billing, a Customer is a billing address, a payment method, and an invoice history. To Support, a Customer is a ticket history and an SLA tier. Each of these is a different, internally-consistent model of "Customer" that only needs to make sense *within its own context*. A **bounded context** is the boundary within which a particular model (and its vocabulary) is consistent and unambiguous — outside that boundary, the same word can mean something else entirely, and that's fine.

Bounded contexts are Newman's recommended unit for drawing service boundaries: one bounded context, one service (or a small, cohesive cluster of services), each with its own internal model of the shared concepts it cares about, talking to other bounded contexts only through explicit, translated interfaces.

## How it works

### Finding bounded contexts: event storming and domain vocabulary

Newman does not prescribe one mechanical algorithm, but the practical technique widely used alongside his approach (and one he references favorably) is **event storming**: get people who understand the business in a room, and map out the significant business events in the domain — things that happened, phrased in past tense: `OrderPlaced`, `PaymentAuthorized`, `InventoryReserved`, `OrderShipped`, `RefundIssued`. You cluster these events, and the clusters of related events, commands, and the entities they act on tend to reveal the natural seams in the domain — those seams are your bounded-context (and service) candidates.

A second, complementary signal: look for words that are used differently by different groups of people (like "Customer" above). Every place the same word carries a genuinely different meaning and different data is a hint that you're looking at two different bounded contexts that happen to share vocabulary on the surface.

### Worked example: decomposing an e-commerce order flow

Take a simplified e-commerce domain. A customer browses a catalog, adds items to a cart, checks out, pays, and the order gets fulfilled and shipped. Walking through it as a sequence of business events:

```
CustomerRegistered -> ItemBrowsed -> ItemAddedToCart -> CheckoutStarted
-> OrderPlaced -> PaymentAuthorized -> InventoryReserved
-> OrderShipped -> DeliveryConfirmed
```

Clustering these by "who owns the decisions and data around this cluster of events, and what vocabulary do they use":

- **Catalog** — owns `ItemBrowsed`, product data, pricing, search. Vocabulary: SKU, product, price, category. Nobody outside Catalog needs to know how search ranking works.
- **Cart** — owns `ItemAddedToCart`, `CheckoutStarted`. A cart is ephemeral, per-session state distinct from a placed order. Vocabulary: cart, line item, quantity.
- **Ordering** — owns `OrderPlaced`. Once checkout completes, a Cart becomes an immutable Order — a genuinely different concept with different lifecycle rules (a cart can be abandoned and mutated freely; a placed order is a record of commitment). Vocabulary: order, order line, order status.
- **Payments** — owns `PaymentAuthorized`. A distinct concern with its own regulatory and security requirements (PCI compliance), naturally isolated. Vocabulary: payment method, authorization, capture, refund.
- **Inventory** — owns `InventoryReserved`. Tracks stock levels and reservations; must handle concurrent reservation races. Vocabulary: SKU, stock level, reservation, backorder.
- **Fulfillment/Shipping** — owns `OrderShipped`, `DeliveryConfirmed`. Vocabulary: shipment, carrier, tracking number, delivery window.

Notice "Customer" would show up differently again here: Ordering cares about a customer's shipping address and order history; Payments cares about a customer's stored payment methods; if there's a separate Marketing or CRM context, it cares about a customer's engagement and segments. Rather than one giant shared `Customer` table that all of these read and write (which recreates the shared-database anti-pattern from Lesson 07), each bounded context keeps *its own* slice of customer data relevant to its concerns, and they reference the same customer by a shared identifier (a `customer_id`), not a shared schema.

The resulting candidate service boundaries — `catalog-service`, `cart-service`, `order-service`, `payment-service`, `inventory-service`, `shipping-service` — mirror the domain's natural seams, not a technical layering. A checkout flow now involves calls across `cart-service`, `order-service`, `payment-service`, and `inventory-service`, but each service's *internal* logic stays cohesive: everything that changes when "how we calculate shipping cost" changes lives in `shipping-service` alone.

### Context maps: how bounded contexts relate

DDD also gives a way to describe *how* bounded contexts depend on each other, called a **context map**. A few relationship patterns worth knowing:

- **Customer/Supplier** — one context (the supplier, e.g. Inventory) provides data the other (the customer, e.g. Ordering) depends on; the supplier has some obligation to consider the customer's needs when it changes.
- **Conformist** — the downstream context just accepts the upstream model as-is with no negotiation (common when depending on a large external system you can't influence).
- **Anti-corruption layer (ACL)** — the downstream context translates the upstream model into its own internal model at the boundary, so upstream's concepts and quirks don't leak into (and pollute) the downstream domain model. This is the standard tool for integrating with a legacy system or a third-party API without letting its shape dictate your own.

For example, if `order-service` needs data from a crusty legacy inventory mainframe with an awkward XML interface, it should not let that XML shape leak into its own domain model. It puts an anti-corruption layer at the integration point that translates the legacy format into `order-service`'s own clean internal notion of "available stock," so a future change to (or replacement of) the legacy system doesn't ripple through `order-service`'s core logic.

### Getting the boundary wrong, and what it costs

If instead you had modeled "Customer" as one shared service used by everyone (Sales, Billing, Support, Ordering, Payments), every one of those teams would need to negotiate schema changes with every other team before shipping — you'd have rebuilt the monolith's coordination bottleneck, just now with network calls in between. This is the most common real-world mistake: reaching for a single generic "entity service" (`customer-service`, `product-service`) that becomes a de facto shared database with an API in front of it, and a single point of coordination for the whole organization.

## Pros
- **Boundaries track how the business actually changes**, so most feature work touches one service, not several — this is what actually preserves independent deployability (Lesson 01).
- **Vocabulary stays unambiguous inside a service** — no more one field meaning three different things depending on who wrote it.
- **Natural fit with team ownership** — a bounded context is a coherent unit a single team can understand end-to-end (sets up Lesson 17, Conway's Law).
- **Legacy and third-party integration is contained** via anti-corruption layers, instead of leaking outward.

## Cons
- **Requires real domain expertise up front** — you need people who understand the business, not just the code, and that conversation takes real time (event storming workshops, domain experts in the room).
- **Boundaries can still be wrong**, especially early in a product's life when the domain itself is still being discovered — and getting them wrong is expensive to fix post-decomposition (Lesson 04 covers how to migrate when this happens).
- **More services usually means more integration points to design and maintain** (context maps, ACLs) — there's real design work at every boundary, not just inside each service.

## Alternatives
- **Technical-layer decomposition** (presentation/business-logic/data-access as separate services) — easier to identify mechanically, but as shown above it tends to force cross-service changes for single business features; generally rejected by Newman as an anti-pattern for service boundaries (it's fine as *internal* layering within one service).
- **Entity/CRUD services** (one service per database table or per noun: `customer-service`, `product-service`, `order-service` as thin CRUD wrappers) — looks domain-driven on the surface but usually isn't, because it splits by data shape rather than by business capability and vocabulary; commonly ends up as a disguised shared database.
- **Team-boundary-first decomposition** — start from existing team structure rather than the domain and let services follow teams. Sometimes pragmatic (Lesson 17 covers the inverse-Conway angle), but risks encoding accidental historical team boundaries into your architecture rather than the domain's real seams.

## When to use it
- Any time you are drawing (or redrawing) service boundaries for a system of real business complexity — this is the default, recommended approach.
- When integrating with legacy systems or third parties, to keep their models from leaking into your own domain.
- When a shared term ("Customer," "Product," "Order") is clearly being used with different meanings by different parts of the organization — a strong signal a boundary already exists informally and should be made explicit.

## When NOT to use it
- Extremely simple domains with one obvious, uncontested model of every entity — the full DDD/event-storming exercise is overkill for a small, well-understood system; a lighter pass at boundaries is fine.
- Very early-stage products where the domain is still being invented week to week — premature bounded-context modeling can lock in boundaries around a domain understanding that will be wrong in a month; better to stay in a modular monolith (Lesson 01) until the domain settles.

## Key takeaways / mental model
Model the business, not the tech stack. A bounded context is a zone where a word means one specific thing — draw your service boundaries at the edges of those zones, not at the edges of your technical layers or your database tables. When the same word means different things to different people in the org, that's not sloppiness to clean up with a shared definition — it's a signal pointing at a real boundary.

## Self-check questions
1. Why does a "presentation / business-logic / data-access" split into three services usually fail to deliver independent deployability, even though it looks like clean separation of concerns?
2. In the e-commerce example, why does "Customer" not get modeled as a single shared service, and what do Ordering and Payments do instead to reference the same underlying person?
3. What is an anti-corruption layer for, and where would you put one when integrating with a legacy system whose data model you don't control?
4. A team wants one `entity-service` per database table (`customer-service`, `product-service`, `order-service`) because "it maps cleanly to our schema." What's the risk with this approach, using the vocabulary from this lesson?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 2: "The Evolutionary Architect" and Chapter 4: "Trade-Offs" (domain-driven decomposition discussion)
- Eric Evans, *Domain-Driven Design: Tackling Complexity in the Heart of Software* (Addison-Wesley, 2003) — origin of bounded context and context mapping, referenced throughout Newman's decomposition chapters.
