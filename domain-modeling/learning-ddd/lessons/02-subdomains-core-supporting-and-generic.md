---
id: learning-ddd/02
subject: learning-ddd
title: "Subdomains: core, supporting, and generic"
slug: subdomains-core-supporting-and-generic
status: drafted
mastery:
seniority: senior
source: Learning Domain-Driven Design (Vlad Khononov), Part I, Chapter 2 - "Strategic Design: Subdomains"
prerequisites: [learning-ddd/01]
created: 2026-08-10
updated: 2026-08-10
---

# Subdomains: core, supporting, and generic

## TL;DR
The **problem space** of a business decomposes into subdomains, each classified as **core** (the company's actual competitive advantage), **supporting** (necessary but not differentiating, often simple), or **generic** (a solved problem shared across industries, best bought not built). This classification, made explicit and revisited over time, is the single most important input to where a team spends its scarcest resource: deep modeling effort.

## The idea
`learning-ddd/01` established that complexity should not be treated uniformly. This lesson gives that idea a concrete vocabulary and a repeatable classification exercise. A **subdomain** is a distinct area of business activity - a natural decomposition of "everything the business does" into coherent chunks (e.g., for a logistics company: route optimization, fleet maintenance, customer notifications, billing, driver payroll). Subdomains exist in the **problem space** - they describe the business as it is, independent of how software will eventually be structured to address it. This is a crucial and often-missed distinction: subdomains are not the same thing as the bounded contexts you will design in the **solution space** (`learning-ddd/03`), even though a well-designed system often ends up with a bounded context per subdomain.

Khononov's three-way classification:

- **Core domain** - what makes the company competitive. If this part of the system were mediocre, the business would lose to competitors. It is complex *and* differentiating. Deserves the best engineers, the closest collaboration with domain experts, and the deepest tactical modeling (`learning-ddd/07`, `learning-ddd/08`).
- **Supporting subdomain** - necessary for the business to function, requires some custom logic (so it usually can't be bought off the shelf as-is), but does not itself win or lose customers. Often simpler business logic than the core; a straightforward implementation (even Transaction Script - `learning-ddd/07`) is usually adequate.
- **Generic subdomain** - a solved problem that is essentially identical across companies and industries: authentication, payment processing, sending email, PDF generation, calendar scheduling primitives. The right move is almost always to buy or adopt an existing solution rather than build one - building here burns engineering effort with zero competitive return.

## How it works

### Step 1: enumerate the business's activities
Talk to domain experts and stakeholders, not just read existing code (existing code reflects old decisions, not necessarily current business reality). List everything the business does as a set of named activities.

**Worked example - e-commerce company:** product catalog management, search and discovery, inventory tracking, dynamic pricing/promotions, cart and checkout, payment processing, order fulfillment routing, shipping-carrier integration, returns and refunds, customer support, seller (marketplace) onboarding, fraud detection, recommendation engine.

### Step 2: classify each by "would losing this hurt us competitively, and is it hard?"
Walk each activity through both axes.

- **Dynamic pricing/promotions** - hard (real-time, data-driven, competitor-aware) and differentiating (directly drives margin and conversion versus competitors) -> **core**.
- **Fraud detection** - hard and, for a marketplace with thin margins, genuinely differentiating (losses from fraud directly hit the bottom line and customer trust) -> **core** (though for a low-fraud-risk B2B catalog seller, this might instead be supporting).
- **Recommendation engine** - could be core (if personalization is the company's stated strategy, e.g., a company betting its growth on AI-driven merchandising) or generic (if it's just "show similar items," bought from a vendor). Classification is context-dependent, not universal.
- **Inventory tracking** - necessary, has real logic (reservation, backorder handling), but a competitor doing inventory tracking "well" doesn't by itself win customers -> **supporting**.
- **Order fulfillment routing** - depends on the company: for a logistics-optimized retailer (e.g., one competing on delivery speed), this is core; for most retailers using a third-party fulfillment network, it's supporting.
- **Payment processing** - regulated, well-solved industry-wide (PCI compliance, card networks) -> **generic**; use Stripe/Adyen/Braintree rather than building card handling.
- **Customer support ticketing** - generic; use Zendesk or similar.
- **Sending email/SMS receipts** - generic; use a transactional email API.

### Worked example - SaaS billing platform
Following on from `learning-ddd/01`'s SaaS billing example: usage metering and tiered/overage billing rules are **core** (this is the company's actual pricing strategy, encoded in software, and a worse implementation directly loses deals to competitors with more flexible billing). Invoice PDF generation is **generic** (use a templating library). Customer account/team management (inviting teammates, roles) is **supporting** - necessary, has some custom logic (role hierarchies specific to how this product's teams work), but is not what customers are buying the product for.

### Worked example - healthcare scheduling
Provider-conflict resolution and wait-time optimization (from `learning-ddd/01`) is **core** for a hospital network competing on patient throughput. Insurance eligibility verification is **generic** - the rules are set by insurers, not the hospital, and third-party eligibility-check APIs exist and are good enough; building a bespoke eligibility engine wastes effort re-solving an externally-defined problem. Patient record storage and basic scheduling calendar mechanics are **supporting** - necessary infrastructure with some domain-specific nuance (recurring appointments, resource booking) but not itself the hospital's differentiator.

### Step 3: let classification drive investment, not the reverse
Once subdomains are classified, resourcing decisions follow: core subdomains get the most senior engineers and the tightest domain-expert collaboration loop (this feeds directly into event storming - `learning-ddd/06` - and ubiquitous language work - `learning-ddd/05`); generic subdomains get a procurement conversation instead of a design conversation; supporting subdomains get competent-but-modest implementations, often intentionally using simpler patterns (`learning-ddd/07`) so the team doesn't over-invest.

### Step 4: revisit periodically
Classification is a snapshot, not a permanent label. A capability that starts generic can become core if a company decides to differentiate on it (cloud infrastructure was generic for Amazon's retail business until AWS became a core business in its own right). A capability that starts core can decay into supporting or even generic as the whole industry catches up and it stops being a differentiator (many companies' basic e-commerce checkout flows are now "supporting" - table stakes, not a competitive edge, even though checkout used to be a serious differentiator in the early 2000s).

## Pros
- Turns an abstract "focus on what matters" mantra into a concrete labeling exercise stakeholders can actually do together.
- Directly informs the boundaries drawn in `learning-ddd/03` - subdomains are the natural seams a solution-space design should respect, even if the eventual bounded-context map doesn't mirror them one-to-one.
- Prevents the two most expensive modeling mistakes: gold-plating a generic problem, and treating a core differentiator as routine CRUD.
- Gives a shared vocabulary ("that's generic, why are we building it?") that de-escalates build-vs-buy arguments.

## Cons
- Requires real access to business strategy and domain experts; an engineering-only exercise risks misclassifying based on technical difficulty alone rather than competitive relevance.
- Boundaries between subdomains are often fuzzier in practice than the clean examples above suggest, especially in businesses that haven't yet articulated their strategy clearly.
- Classification can become political - teams may lobby for their area to be labeled "core" for prestige or headcount reasons, independent of whether it's actually true.
- Static once-a-year labeling misses drift; without a habit of revisiting, classifications go stale exactly when they matter most (during a strategic pivot).

## Alternatives
- **Skip classification, treat all subdomains uniformly** - simpler to explain but reproduces the anti-pattern named in `learning-ddd/01`: wasted effort everywhere, under-investment nowhere it's needed.
- **Wardley Mapping** - maps components on an evolution axis (genesis/custom-built to commodity) rather than a core/supporting/generic label; more granular and visual, often used alongside subdomain classification for strategic planning rather than as a replacement.
- **`ddd-evans`'s Core Domain / Generic Subdomain vocabulary** - Evans's original two-and-a-half-way split (Core Domain, with "Generic Subdomains" and looser support concepts); Khononov's three-way split with an explicit "supporting" category is the more usable, complete version for teams doing this exercise today.
- **`implementing-ddd`'s treatment** - Vaughn Vernon's *Implementing Domain-Driven Design* covers the same classification with an emphasis on how it should shape team structure, foreshadowing `learning-ddd/14`.

## When to use it
Use it at the start of any greenfield initiative (before deciding on bounded contexts or architecture), and periodically for existing systems - especially before a major re-architecture, before staffing decisions, and whenever the business articulates a new strategic bet (a new subdomain may need to be reclassified as core).

## When NOT to use it
Don't force the exercise onto a system too small or too early-stage to have a discoverable strategy yet - an early-stage startup validating product-market fit may not yet know which subdomain will become its differentiator, and over-formalizing the classification too early can lock in a wrong guess. In that situation, keep the system simple and flexible everywhere until the differentiator becomes clear from real usage and market feedback.

## Key takeaways / mental model
For every subdomain, ask: "if a competitor implemented this identically to us, would customers notice or care?" If yes, it's core - invest your best people and deepest modeling there. If it must be custom but customers wouldn't notice a competent-but-unremarkable implementation, it's supporting. If any competent team anywhere could build the same thing (or already has, as a product you can buy), it's generic - buy it and move on.

## Self-check questions
1. Take a system you know well and classify three of its subdomains as core, supporting, or generic. Justify each with the "would a competitor's identical implementation matter to customers" test.
2. Give an example of a capability that moved from generic to core (or vice versa) as a company's strategy changed, and explain what changed.
3. Why is subdomain classification described as belonging to the "problem space" rather than the "solution space" - and why does that distinction matter when you later design bounded contexts in `learning-ddd/03`?
4. A stakeholder insists their team's subsystem is "core" because it's technically the hardest part of the codebase. What follow-up question would you ask to test that claim?

## References
- Learning Domain-Driven Design (Vlad Khononov), Part I, Chapter 2: "Strategic Design: Subdomains".
- Domain-Driven Design (Eric Evans, 2003), Core Domain and Generic Subdomains - see `domain-modeling/ddd-evans`.
- Implementing Domain-Driven Design (Vaughn Vernon) - see `domain-modeling/implementing-ddd`.
