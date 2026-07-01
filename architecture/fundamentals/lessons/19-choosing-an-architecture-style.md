---
id: fundamentals/19
subject: fundamentals
title: Choosing an Architecture Style
slug: choosing-an-architecture-style
status: drafted
mastery:
seniority: senior
source: Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 19
prerequisites: [fundamentals/03, fundamentals/08, fundamentals/09, fundamentals/18]
created: 2026-06-30
updated: 2026-06-30
---

# Choosing an Architecture Style

## TL;DR
Choosing an architecture style isn't about finding a single best option. It's a matching process where you align your domain's architectural characteristics, organization constraints, team topology, risk profile, and evolutionary path with the capabilities of monolithic or distributed styles.

## The idea
Teams often default to whatever style is trendy, usually microservices, or whatever they built last. This leads to severe mismatches. An architecture style is a structural pattern that shapes how code and data are organized, deployed, and scaled. 

No single style excels at everything. A style that offers extreme scalability might introduce painful complexity and high operational costs. A simple style might restrict your growth or make independent deployments impossible. 

The architect's job is to move past hype and objectively match the business needs to the right structural style. This requires looking at:
1. Architectural characteristics (what the system must do well, like performance or elasticity).
2. Physical and financial constraints (budgets, legacy systems, database limits).
3. Team topology (how your engineering department is organized).
4. Risk tolerance (what kind of failures or delays the business can accept).
5. Evolution paths (how easily you can change your mind later).

## How it works

The selection process is structured. You shouldn't jump to a style immediately. Instead, follow these steps:

```
[Identify Quality Attributes] -> [Apply Constraints & Topology] -> [Assess Style Matrix] -> [Select Style & Path]
```

### Step 1: List and Prioritize Your Architectural Characteristics
You can't support thirty different characteristics at once. Focus on the top three to five attributes that are truly critical for business success. These are defined in `fundamentals/03`.
- If you run an online retail checkout during Black Friday, you need elasticity and scalability.
- If you build a medical device controller, you need safety and reliability.
- If you build a startup MVP with limited funding, you need agility, testability, and low cost.

### Step 2: Evaluate Style Capabilities
Each architectural style has a native set of strengths and weaknesses. You can map them on a score card.

Score Scale:
- High (3): Native support, minimal effort to achieve.
- Medium (2): Supported, but requires careful design or adds overhead.
- Low (1): Not supported, or requires immense custom effort and introduces heavy friction.

| Style | Partitioning | Agility | Deployability | Scalability | Elasticity | Performance | Fault Tolerance | Cost | Complexity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Layered (Monolith)** | Technical | Low | Low | Low | Low | Medium | Low | High | Low |
| **Pipeline (Monolith)** | Technical | Low | Low | Low | Low | Medium | Low | High | Low |
| **Microkernel (Monolith)** | Domain/Tech | Medium | Medium | Low | Low | High | Low | High | Low |
| **Modular Monolith** | Domain | High | Medium | Medium | Low | High | Low | High | Medium |
| **Service-Based** | Domain | High | Medium | Medium | Medium | Medium | Medium | Medium | Medium |
| **Event-Driven** | Domain | High | High | High | High | Medium | High | Low | High |
| **Space-Based** | Domain | Medium | Medium | High | High | High | High | Low | High |
| **Microservices** | Domain | High | High | High | Medium | Low | High | Low | High |

Note: Cost rating represents how cost-effective the style is (High score means lower financial/operational cost). Complexity rating represents simplicity (High score means it's simpler/less complex).

### Step 3: Overlay Organizational and Team Topology
Conway's Law states that organizations design systems that copy their communication structures.
- If you have three small teams working in different time zones, choosing a single layered monolith will cause severe delivery bottlenecks. A modular monolith or service-based architecture matches their boundaries much better.
- If your teams are highly specialized by technology (such as a database team, a backend team, and a frontend team), a layered style matches your current structure. To adopt microservices, you'll first have to reorganize into cross-functional product teams.

### Step 4: Map the Evolution Path
Architectures must evolve as businesses grow. You should choose a style that lets you defer high-complexity decisions.
- A common pattern is starting with a Modular Monolith. It keeps complexity low when the domain is poorly understood, but establishes strict component boundaries.
- As specific domains scale, you can peel them off into independent services, transitioning toward a Service-Based or Event-Driven style.

### Worked Example: "FastShop" E-Commerce Modernization
FastShop is an e-commerce platform migrating away from a decaying single-database layered monolith.

#### Context and Constraints:
1. Checkout transactions peak at 3000 requests per second during sales.
2. The inventory catalog changes constantly and must reflect real-time stock.
3. The development department has 24 engineers split into 3 teams: Product Catalog, Checkout, and Fulfillment.
4. The system operates on a tight cloud budget, making massive cluster footprints unacceptable.
5. The checkout flow must remain highly performant (under 150ms p95 latency) and highly available.

#### Applying the Selection Process:

1. **Prioritized Characteristics**:
   - High Scalability and Elasticity (for checkout spikes).
   - High Performance (checkout response times).
   - Team Autonomy (deployability for the 3 teams).
   - Low to Medium Cost.

2. **Evaluating Options**:
   - *Microservices*: Provides high scalability and team autonomy, but the distributed network hops will degrade latency, and the overhead of managing 20+ microservices exceeds the cloud budget and team skills.
   - *Space-Based*: Solves the checkout scale perfectly through in-memory data grids, but it's excessively complex and expensive to implement for the catalog and fulfillment domains.
   - *Service-Based Architecture*: We can partition the monolith into three coarse-grained, domain-aligned services: Catalog, Checkout, and Fulfillment.

3. **Refining the Selection**:
   Instead of a single uniform style, FastShop selects a hybrid approach:
   - The overall platform uses a **Service-Based Architecture**. This matches the 3-team structure perfectly and allows independent deployments of Catalog, Checkout, and Fulfillment.
   - The Checkout service uses a **Modular Monolith** pattern internally with a local relational cache, protecting its performance.
   - FastShop uses asynchronous **Event-Driven** messaging between Checkout and Fulfillment. When Checkout completes a purchase, it publishes an event, and Fulfillment processes it asynchronously. This isolates checkout from fulfillment failures.

This hybrid matches their exact constraints without incurring the extreme costs of full microservices.

## Pros
- Avoids cargo-culting and helps teams reject trendy patterns that don't fit their needs.
- Prevents expensive re-architecting work by identifying organizational mismatches early.
- Integrates Conway's Law into technical decisions instead of fighting it.
- Creates an objective, defensible framework for explaining style choices to stakeholders.

## Cons
- Requires deep honesty about team capabilities and organization maturity.
- It is difficult to map characteristics when business requirements are vague or change constantly.
- Scorecards can tempt teams into fake precision or numeric manipulation to justify pre-selected favorites.

## Alternatives
- **Default Monolith First**: Always start with a monolithic structure and defer style choices until scale demands it. This is safe but can lead to spaghetti code if component boundaries are not enforced early.
- **Microservices by Default**: Always build distributed microservices from day one. This simplifies scaling later but introduces massive early-stage complexity and high infrastructure costs.
- **Framework-Driven Selection**: Let the primary development framework dictate the system's structure. This speeds up early delivery but tightly couples your business to a specific tool's limits.

## When to use it
Use this matching process during major system redesigns, when planning a migration from a monolith, when splitting teams, or when business scaling requirements shift dramatically.

## When NOT to use it
Don't run a full style evaluation for small features, minor products, or early-stage exploratory MVPs where survival is the only priority and the architecture is highly temporary.

## Key takeaways / mental model
Software architecture is the art of matching business problems to structural styles. You cannot pick a style without evaluating its impact on your team topology, budget, and development speed.

1. No single style is a universal solution.
2. Conway's Law is a hard constraint: match your architecture to your team boundaries.
3. Don't pay the distributed systems complexity tax unless you actually need the scalability.
4. Establish clear boundaries early so you can evolve the style as your constraints change.

## Self-check questions
1. Why does Conway's Law make a highly distributed microservices style risky for a single, small development team?
2. Which architectural styles prioritize low cost and simplicity over high scalability and elasticity?
3. How does the concept of a hybrid style help solve conflicting requirements in a multi-team organization?
4. In the FastShop example, what are the primary trade-offs of choosing a Service-Based style over a Microservices style?

## References
- Fundamentals of Software Architecture (Richards & Ford, O'Reilly 2nd ed. 2025), Chapter 19
- [03-architectural-characteristics.md](03-architectural-characteristics.md)
- [08-architecture-quanta.md](08-architecture-quanta.md)
- [09-monolithic-vs-distributed-architecture.md](09-monolithic-vs-distributed-architecture.md)
