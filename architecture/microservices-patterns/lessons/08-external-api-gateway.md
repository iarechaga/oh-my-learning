---
id: microservices-patterns/08
subject: microservices-patterns
title: "External API Patterns and the API Gateway"
slug: external-api-gateway
status: drafted
mastery:
seniority: senior
source: "Microservices Patterns (Chris Richardson), Chapter 8"
prerequisites: [microservices-patterns/03]
created: 2026-07-01
updated: 2026-07-01
---

# External API Patterns and the API Gateway

## TL;DR
In a microservices system, external clients should rarely call many internal services
directly. An API gateway gives clients one stable entry point, composes data at the
edge, and centralizes edge concerns like authentication and rate limiting. The BFF
variant takes this further by exposing client-specific APIs for mobile, web, and
partner use cases without leaking internal service boundaries.

## The idea
External clients are not all the same.

A mobile app running on spotty 4G wants fewer round-trips, smaller payloads, and
responses shaped for small screens.

A web client often needs richer data for larger layouts and can tolerate somewhat
larger payloads.

A third-party integrator needs stable contracts, explicit quotas, and stricter
security boundaries.

If each of those clients calls internal microservices directly, problems appear fast:

- Clients become coupled to your service decomposition.
- Client code learns internal topology and endpoint details.
- Requests become chatty: N remote calls over high-latency networks.
- Every service must individually handle external-facing concerns.

The API gateway pattern solves this by creating a single external entry point.

Clients call the gateway. The gateway routes, composes, translates, and enforces edge
policies. Internal services stay focused on business capability, not public API
orchestration.

## How it works

### API gateway pattern: single entry point plus edge orchestration
At a high level, the gateway sits between external clients and internal services.

It exposes a client-facing API surface and internally fans requests out to the right
services.

The core jobs are:

1. Request routing: map incoming path, method, tenant, or header to a target service.
2. API composition: call multiple services and merge into one response.
3. Protocol translation: for example, public REST to internal gRPC.

The key architectural value is indirection. Clients depend on a stable facade, while
you can evolve internal service boundaries over time.

### Edge functions: put cross-cutting concerns at the boundary
The gateway is often the right place for concerns that are external, repeated, and
policy-driven.

Common edge functions include:

- Authentication and authorization checks before traffic reaches services.
- Rate limiting per client app, user, API key, or partner.
- Caching of safe-to-cache responses to reduce load and latency.
- Request shaping, such as field filtering or pagination defaults.
- Metrics, logs, and trace context injection for observability.

This does not mean all logic belongs at the edge. Business rules should stay in
domain services. The gateway should enforce policies and shape traffic, not own core
business invariants.

### BFF variant: one facade per client type
A single shared gateway can become a compromise API that satisfies nobody.

The Backends-for-Frontends pattern splits gateway responsibilities by client type,
for example:

- Mobile BFF: small payloads, fewer fields, aggressive composition.
- Web BFF: richer payloads for desktop layouts.
- Public API BFF: stable versioned contract, strict quotas and auditing.

BFFs reduce cross-team contention. Mobile and web teams can evolve their edge APIs
independently while still relying on shared internal services.

### API composition at gateway vs separate composition service
You can compose data in two places:

1. In the gateway itself.
2. In a dedicated composition service behind the gateway.

Composing in the gateway is simpler at first. It minimizes hops and keeps edge logic
close to routing.

But composition can grow complex: fallback logic, partial failures, data shaping,
versioning, and performance tuning. When that grows beyond light edge orchestration,
extracting a dedicated composition service can keep the gateway thin and easier to
operate.

Practical rule:

- Keep lightweight join logic in gateway/BFF.
- Move heavy domain-aware orchestration into dedicated backend services.

### Ownership and the monolith-at-the-edge risk
Because all external traffic flows through it, the gateway attracts changes from many
teams.

Without discipline, one shared gateway becomes an edge monolith:

- Huge config or codebase touched by everyone.
- Long release queues and merge conflicts.
- Slow deploy cadence tied to many unrelated changes.
- A performance bottleneck and organizational bottleneck.

You avoid this by clear ownership boundaries:

- Platform team owns base gateway platform, security defaults, observability, and
  traffic policy primitives.
- Product/client teams own their BFF logic and client-specific response shaping.
- Contracts and SLOs are explicit between BFFs and internal services.

### Implementation options: product gateway vs framework gateway
There are two common implementation paths.

Off-the-shelf API gateway products (managed or self-hosted):

- Strong for standardized capabilities: auth plugins, rate limiting, dashboards,
  policy management.
- Faster operational start when needs are conventional.
- Can become restrictive for complex composition logic.

Code-first gateway/BFF using an application framework:

- Maximum flexibility for custom composition and response shaping.
- Easier to use normal language tooling, tests, and deployment pipelines.
- Requires stronger engineering discipline to avoid re-implementing commodity edge
  features poorly.

Many teams use a hybrid approach: product gateway for baseline edge enforcement,
plus framework-based BFFs for client-specific composition.

### Worked example 1 - Baseline topology and traffic shape
Suppose FTGO exposes services such as Order, Kitchen, Delivery, Consumer, and
Accounting.

Without a gateway, each client must know multiple service URLs.

With a gateway, all north-south traffic enters one edge API first.

```text
                External clients

  Mobile App       Web SPA         3rd-party Partner
      |               |                    |
      +---------------+--------------------+
                      |
                      v
              +----------------+
              |  API Gateway   |
              +----------------+
                |    |    |   |
                v    v    v   v
             Order Kitchen Delivery Consumer
                |
                v
             Accounting
```

Result: clients stop depending on internal service decomposition and call one entry
point instead.

### Worked example 2 - Mobile get order details composed at the edge
A mobile screen needs a compact "order details" response:

- Order summary from Order service.
- Kitchen status from Kitchen service.
- ETA and courier location from Delivery service.

If the mobile app calls each service directly, it performs three remote calls over a
mobile network and must merge responses locally.

With a gateway, it does one call:

`GET /mobile/orders/8172/details`

Execution flow:

1. Gateway authenticates the user token and checks per-user rate limits.
2. Gateway calls Order, Kitchen, and Delivery concurrently.
3. Gateway applies a response deadline of 600 ms.
4. If Kitchen is late, gateway returns partial data with `kitchenStatus: "unknown"`.
5. Gateway returns one compact mobile-shaped payload.

```text
Mobile -> Gateway : GET /mobile/orders/8172/details
Gateway -> Order  : getOrder(8172)
Gateway -> Kitchen: getKitchenStatus(8172)
Gateway -> Delivery: getDeliveryETA(8172)
Order --> Gateway : {id, total, items}
Kitchen --> Gateway: {status: PREPARING}
Delivery --> Gateway: {etaMinutes: 14, courier: "Carlos"}
Gateway --> Mobile: {id, total, status, etaMinutes}
```

Round-trips over the mobile network drop from N to 1. Internal fan-out still exists,
but over faster and more reliable datacenter links.

### Worked example 3 - BFF split for different response shapes
Now split one shared gateway into two BFFs.

Mobile wants summary-first data. Web wants richer structure for detailed components.

```text
Mobile App ----> Mobile BFF ----> Order/Kitchen/Delivery
Web SPA   ----> Web BFF    ----> Order/Kitchen/Delivery/Accounting
```

For the same order `8172`, mobile BFF returns:

```text
{
  "orderId": "8172",
  "status": "OUT_FOR_DELIVERY",
  "etaMinutes": 14
}
```

Web BFF returns:

```text
{
  "order": {"id": "8172", "items": [...], "subtotal": 33.50},
  "kitchen": {"status": "READY", "station": "PIZZA-02"},
  "delivery": {"courier": "Carlos", "etaMinutes": 14},
  "payments": {"authorized": true, "method": "VISA"}
}
```

Both clients use the same core services, but each gets the shape and payload size it
actually needs.

## Pros
- Reduces client coupling to internal service boundaries.
- Cuts chatty client traffic, especially valuable on mobile networks.
- Centralizes edge security, quotas, and observability concerns.
- Enables protocol translation and progressive backend evolution.
- Supports client-specific APIs through BFFs without duplicating domain services.

## Cons
- Adds another hop, so there is always some latency overhead.
- Can become a single organizational bottleneck if shared and unmanaged.
- Risk of edge monolith when too much business logic drifts into gateway code.
- Operational complexity: scaling, high availability, and policy governance.
- If gateway is down and not redundant, all external traffic is down.

## Alternatives
- **Clients call services directly**: simple for very small systems, but it exposes
  internal topology, duplicates edge concerns, and increases chatty traffic.
- **A single shared gateway vs per-client BFFs**: one shared gateway is simpler to run
  at first; per-client BFFs improve autonomy and response fit as client needs diverge.
- **GraphQL as a composition/BFF alternative**: can give clients flexible query shape
  and reduce over-fetching, but still needs strong edge governance and schema design.
- **A service mesh**: valuable for east-west service-to-service concerns, but it does
  not replace the API gateway job at the north-south external edge.

## When to use it
Use an API gateway (often with BFFs) when most of these are true:

- You have multiple external client types with different payload needs.
- Clients currently make many calls to render one screen or operation.
- You need consistent external auth, rate limiting, and API policy enforcement.
- Internal services change frequently and you want a stable external facade.
- You need to shield internal protocols and topology from external consumers.

## When NOT to use it
Avoid introducing a full gateway layer when:

- The system is small, with one backend service and one client.
- Latency budget is so strict that every extra hop is unacceptable.
- Team maturity is too low to operate edge infrastructure safely yet.
- You are using a gateway as a place to hide bad service design instead of fixing
  boundaries and domain responsibilities.

## Key takeaways / mental model
Think of the API gateway as the external adapter boundary for a microservices backend.

North-south traffic enters through this adapter, which enforces policies and shapes
client-friendly APIs. Internal services stay focused on business capabilities.

If one gateway has to satisfy very different clients, split into BFFs.

Keep the edge thin: route, compose lightly, translate, and enforce policy.
Do not turn it into a second monolith.

Service mesh and API gateway are complementary, not competing:
gateway for north-south edge traffic, mesh for east-west internal traffic.

## Self-check questions
1. You see a mobile app making 7 API calls to load one screen. How would you redesign
   that flow with an API gateway, and what data would you compose at the edge?
2. Your web and mobile teams keep fighting over response shape changes in one shared
   gateway. What BFF split would you propose, and what would each team own?
3. In FTGO, a partner API consumer needs strict quotas and long-lived versioned
   contracts. What would your public API edge look like, and why?
4. A gateway endpoint now contains heavy pricing business rules and DB joins. Is this
   still good edge logic or a smell? What would you move, and where?
5. If an architect says "we deployed a service mesh, so we can remove the API gateway,"
   how would you explain the category error in one minute?
6. You must choose between an off-the-shelf gateway product and a framework-based BFF.
   What criteria would drive your decision in a senior-level design review?

## References
- Microservices Patterns (Chris Richardson), Chapter 8: "External API patterns"
- [microservices-patterns/03 - Inter-Process Communication Patterns](03-ipc-patterns.md)
- [system-design/07 - API gateways and reverse proxies](../../system-design/lessons/07-api-gateways-proxies.md)
