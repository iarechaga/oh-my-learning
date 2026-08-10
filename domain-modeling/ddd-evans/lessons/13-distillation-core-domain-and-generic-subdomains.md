---
id: ddd-evans/13
subject: ddd-evans
title: "Distillation: core domain and generic subdomains"
slug: distillation-core-domain-and-generic-subdomains
status: drafted
mastery:
seniority: staff
source: Domain-Driven Design (Eric Evans), Part IV, Chapters 15-16
prerequisites: [ddd-evans/01, ddd-evans/07, ddd-evans/12]
created: 2026-08-10
updated: 2026-08-10
---

# Distillation: core domain and generic subdomains

## TL;DR
Not every part of a system deserves equal design investment — distillation is the deliberate process of identifying the **core domain** (the small part that actually differentiates the business and justifies the whole system's existence) and separating it, structurally and in team attention, from **generic subdomains** (necessary but undifferentiated problems solved the same way at any company) and **supporting subdomains** (specific to this business but not competitively differentiating).

## The idea
Most real systems are large, and most of that size is not where the interesting, valuable modeling work lives. A logistics company's system needs authentication, sends emails, generates PDF invoices, manages user permissions — none of that is what makes the company competitively different from any other logistics company. What actually differentiates it might be a genuinely novel approach to route optimization, or a unique way of pricing based on real-time capacity. That's the core domain: the part where deep modeling investment (all of `ddd-evans/12`'s supple-design techniques) pays off disproportionately, because it's the part the business's success actually depends on getting right.

Evans's warning is that teams routinely spread their best people and their best design effort evenly across the whole system, or worse, spend disproportionate effort on generic infrastructure concerns (an elegant permissions system) while the actual core domain gets whatever time is left over, modeled hastily by whoever's available. Distillation is the corrective discipline: explicitly identify what's core, protect it fiercely, and treat everything else as a candidate for buying, using an off-the-shelf library, outsourcing, or building with deliberately minimal investment.

## How it works

### Classifying subdomains
1. **Core domain** — the part that differentiates the business competitively and is genuinely hard to get right; this is where the company's best modeling talent and design effort should concentrate.
2. **Supporting subdomain** — necessary, specific to this business, but not a competitive differentiator; worth a real (but not extravagant) custom model, often simpler than the core domain's.
3. **Generic subdomain** — a problem solved essentially the same way everywhere, with no business-specific nuance (authentication, invoicing/PDF generation, generic address validation); strong candidate for an off-the-shelf library, SaaS product, or vendored solution rather than custom-built code.

### Worked example: a logistics company
- **Core domain**: real-time route optimization accounting for live traffic, driver hours regulations, and delivery-window commitments — this is what makes the company's on-time delivery rate beat competitors, and it deserves the company's best engineers and the full weight of `ddd-evans/12`'s supple-design investment.
- **Supporting subdomain**: driver scheduling and shift management — genuinely specific to this business's operational rules (union contracts, regional labor law), but not itself a competitive differentiator; worth a solid, purpose-built model, but not the deepest design investment in the system.
- **Generic subdomain**: user authentication, email notifications, PDF invoice generation — solved identically by thousands of companies; using an off-the-shelf identity provider (Auth0, Okta) and a transactional email service instead of building these in-house frees the team's limited design attention for the core domain where it actually matters.

A team that spends three sprints building an elegant custom permissions system while the route-optimization core domain is modeled by whoever had free time that week has inverted the priority distillation is meant to enforce.

### The distillation techniques
- **Core domain document / "the vision"**: a short, explicit written statement of what the core domain is and why it matters, kept visible to the whole team, so new features and refactoring priorities are judged against it — "does this change strengthen the core domain, or is it spending core-domain-quality effort on something generic?"
- **Segregating cohesive mechanisms**: pull generic, complex-but-not-domain-specific *mechanisms* (a constraint-solving algorithm, a graph-traversal utility) out of domain classes into separate, reusable, well-tested modules of their own, so the core domain's classes stay expressive and focused on business rules rather than being cluttered by generic algorithmic machinery that has nothing to do with the domain itself. This connects to `ddd-evans/07`'s module-boundary discipline: a "generic mechanisms" module is itself a legitimate, cleanly separated module.
- **Abstract core**: for very large or complex core domains, distill even further — factor out the most fundamental, abstract concepts and relationships (often expressible as interfaces or a small set of abstract base classes) that capture the essential structure, separate from the many concrete variations built on top of it.

### Worked example: segregating a generic mechanism out of the core domain
A route-optimization core domain initially had its shortest-path graph-traversal algorithm implemented as private methods scattered inside the `RouteOptimizer` class, tangled together with genuinely business-specific rules (driver-hours limits, delivery-window penalties). This made `RouteOptimizer` hard to read — a developer trying to understand the business rule "penalize routes that violate a delivery window" had to wade through generic graph-traversal code to find it. Segregating the traversal algorithm into a separate, generic `WeightedGraphSolver` module (no domain vocabulary at all, purely algorithmic) let `RouteOptimizer` shrink down to code that reads almost entirely in business terms — configuring the solver with domain-specific weights and constraints, rather than implementing the traversal itself. The core domain got measurably more "supple" (`ddd-evans/12`) purely by removing generic machinery that never belonged there.

### Distillation drives investment and staffing decisions, not just code structure
The point isn't only architectural — it's organizational. Once a core domain is explicitly identified, it should visibly get the most experienced developers, the most rigorous knowledge-crunching effort (`ddd-evans/01`) with domain experts, and the highest bar for design quality (`ddd-evans/12`). Generic subdomains, correspondingly, are legitimate candidates for junior developers, for buying rather than building, or for outsourcing — treating every subdomain with equal design ceremony wastes scarce senior attention on parts of the system where it doesn't actually move the needle.

## Pros
- Focuses scarce design and staffing effort where it has the most competitive impact, instead of spreading it evenly (and therefore thinly) across the whole system.
- Provides an explicit, shared, arguable criterion ("is this core?") for prioritization debates that would otherwise be decided by whoever's loudest or whichever code happens to be most visible.
- Legitimizes buying/outsourcing generic subdomains without guilt — not every part of the system needs to be built with the same rigor, and pretending otherwise wastes effort.

## Cons
- Identifying the true core domain requires real business insight and honest self-assessment — teams often misjudge what's actually core, especially early on, or resist admitting a beloved, heavily-invested-in subsystem is actually just generic infrastructure.
- Core domains can shift over time as business strategy changes; a subdomain correctly classified as "supporting" two years ago might become core after a strategic pivot, requiring the classification (and the investment that follows it) to be revisited.
- Segregating generic mechanisms out of the core domain adds real refactoring work upfront, which can be hard to justify against feature-delivery pressure in the short term even though it pays off over the system's life.

## Alternatives
- **Uniform investment across the whole system** — the unexamined default; simpler to reason about ("just do good work everywhere"), but this lesson's entire argument is that it wastes scarce senior design effort on parts of the system where it doesn't matter competitively.
- **Wardley mapping / strategic value-chain analysis** — a related but distinct strategic technique (from outside the DDD tradition) for classifying which capabilities are differentiating versus commodity, useful as a complementary lens alongside core-domain distillation, especially for organization-wide (not just single-system) prioritization decisions.
- **Domain storytelling / event storming for scope discovery** — modern techniques (see `learning-ddd`) that can help surface which parts of a domain are actually complex and differentiating versus which are simple and generic, feeding into the same distillation decision this lesson describes.

## When to use it
Apply distillation deliberately on any system large enough to contain both genuinely differentiating business logic and substantial generic/supporting machinery — which is most systems past early-stage prototypes, and especially any system where design effort is visibly being spread too thin across too many equally-weighted concerns.

## When NOT to use it
For a small system that *is* the core domain in its entirety (a tool built around one single differentiating idea, with minimal supporting infrastructure), formal subdomain classification is unnecessary ceremony — there's nothing to triage because there's no generic bulk to separate out.

## Key takeaways / mental model
Ask of every part of the system: "if a competitor perfectly copied this piece, would customers care?" If yes, it's core, and it deserves the team's best modeling effort and best people. If no — if it's necessary but interchangeable with what any other company would build the same way — it's generic or supporting, and it's a legitimate candidate for minimal custom investment, buying, or outsourcing.

## Self-check questions
1. Pick a system you've worked on and classify its major subsystems into core, supporting, and generic. Did the team's actual staffing and design effort match that classification, or was it inverted?
2. In the route-optimization example, why does segregating the graph-traversal algorithm into its own generic module make the core domain more supple (`ddd-evans/12`), specifically?
3. Describe a scenario where a subdomain correctly classified as "supporting" two years ago should now be reclassified as "core." What business change would trigger that?
4. Why does the book treat "buy instead of build" for a generic subdomain as a legitimate design decision rather than a cop-out?

## References
- Domain-Driven Design: Tackling Complexity in the Heart of Software (Eric Evans), Chapter 15: "Distillation" and Chapter 16: "Large-Scale Structure" (Core Domain framing).
