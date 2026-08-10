---
id: implementing-ddd/01
subject: implementing-ddd
title: Distilling strategic design into implementation decisions
slug: distilling-strategic-design-into-implementation-decisions
status: drafted
mastery:
seniority: senior
source: Implementing Domain-Driven Design (Vaughn Vernon), Chapter 1: Getting Started with DDD
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# Distilling strategic design into implementation decisions

## TL;DR
Strategic DDD (bounded contexts, ubiquitous language, subdomains) tells you *where* to draw boundaries and *what* deserves deep modeling effort; Vernon's contribution is turning those strategic decisions into concrete, checkable implementation choices — a project can follow every tactical pattern in the book and still fail if it never distilled the strategic picture first.

## The idea
Eric Evans's original book (see `ddd-evans`) gives you a vocabulary and a set of strategic tools: the domain is decomposed into subdomains (core, supporting, generic), each subdomain gets a bounded context with its own ubiquitous language, and a context map records how those contexts relate. What Evans's book does not give you, in much operational detail, is *how to actually build the thing* — what an aggregate root class looks like in a real codebase, how a repository is wired to a database, how one service calls another without silently coupling their models together. Vernon's book exists to close that gap: it is explicitly a field guide for teams who already accept DDD's premises and need to know which knobs to turn when writing code, running a project, and making architecture decisions under real constraints (legacy systems, distributed teams, existing infrastructure).

The core insight this lesson anchors is: **tactical patterns without strategic distillation produce a well-engineered mess.** You can write beautiful aggregates, immaculate repositories, and a tidy layered architecture, and still ship a system that models the wrong thing with excruciating precision — because nobody first asked "what is the core domain, and what actually deserves this level of care?" Distillation (a term Evans uses, that Vernon operationalizes) means ruthlessly identifying which parts of the domain are the reason the business exists (the *core domain*) versus parts that are necessary but not differentiating (*supporting subdomains*) versus parts that are pure commodity (*generic subdomains*, e.g. authentication, invoicing you could buy off the shelf). Implementation effort should track that distillation: hand-rolled rich domain models for the core, simpler CRUD-ish code for supporting subdomains, and off-the-shelf or minimal-effort solutions for generic ones.

## How it works

### Step 1 — Identify the core domain before writing any code
Vernon opens with a scenario: a project team defaults to modeling everything with equal care, including subdomains that are functionally interchangeable with any competitor's software (user account management, generic billing). The fix is a strategic distillation exercise — literally listing subdomains and classifying each as core / supporting / generic — done with domain experts before architecture decisions are locked in. For a hypothetical online collaboration/scrum tool (a running example Vernon uses across the book), the *core domain* is the product backlog and sprint planning model — the thing customers pay for and competitors differ on. Tenant/user management is a *supporting subdomain* (necessary, not differentiating). Authentication could be a *generic subdomain* — bought or borrowed rather than built.

### Step 2 — Let the core domain drive the bounded context boundaries
Once you know what's core, bounded context boundaries (`implementing-ddd/03`) follow: the core domain gets its own bounded context with a rich ubiquitous language and, usually, its own team. Vernon is explicit that bounded context boundaries should track team boundaries and language boundaries, not database schemas or convenient module folders — a distinction that becomes operationally important once you get to context mapping (`implementing-ddd/10`) and integration (`implementing-ddd/12`).

### Step 3 — Calibrate tactical investment to strategic classification
This is the practical payoff: once a subdomain is classified, the implementation decision is largely made for you.
- **Core domain**: full tactical toolkit — rich aggregates (`implementing-ddd/04`), domain events (`implementing-ddd/07`), possibly event sourcing (`implementing-ddd/13`) if audit/replay matters, careful repository design (`implementing-ddd/08`). This is where the team's best engineers and most design time should go.
- **Supporting subdomain**: simpler, often transaction-script or thin-anemic-model code is acceptable. Don't build an elaborate aggregate hierarchy for a subdomain that will never need to evolve much.
- **Generic subdomain**: buy, don't build, when possible (an off-the-shelf auth provider, a commercial billing API). If you must build it, treat it as infrastructure, not domain modeling.

**Worked example — an e-commerce platform.** Classify: *checkout and inventory allocation logic* (how the business decides what's sellable, in what order items reserve stock, how promotions stack) is core — it's exactly where the business differentiates and where bugs cost real revenue; invest heavily in aggregates and events here. *Customer support ticketing* is supporting — necessary, generic-shaped, low differentiation; a straightforward CRUD service is fine. *Payment gateway integration* is generic — don't reinvent PCI-compliant payment processing; integrate a vendor via an anti-corruption layer (`implementing-ddd/11`) and move on.

### Step 4 — Revisit the distillation as the domain is understood better
Distillation isn't a one-time meeting. As implementation proceeds and domain experts see the model reflected in working software, the core/supporting/generic classification often shifts — a subdomain thought to be generic turns out to hide genuine domain complexity worth investing in. Vernon frames this as ongoing collaboration between developers and domain experts, not a phase that ends once architecture is decided.

## Pros
- Prevents the single most common DDD failure mode: uniform tactical rigor applied to a domain that was never triaged, which wastes engineering effort on low-value subdomains while starving the actual core domain of attention.
- Gives teams and stakeholders a shared, defensible vocabulary for saying "no, we're not building a bespoke solution for that — it's generic, buy it" — turning a subjective architecture argument into a strategic classification exercise.
- Scales investment decisions across a whole system, not just a single bounded context, which is essential once an organization has more than one team building DDD software.

## Cons
- Classifying a subdomain as core/supporting/generic requires real domain expertise and honest conversations with the business — teams without access to domain experts, or without the political capital to say "this isn't worth building well," struggle to do this step at all.
- Misclassification is expensive in both directions: over-investing tactical machinery in a generic subdomain wastes effort; under-investing in something that turns out to be core produces a brittle model exactly where the business needed flexibility.
- The classification can become stale as the business evolves (a supporting subdomain becomes core after a strategic pivot), and there's no automated signal that forces a re-classification — it depends on the team staying close to the business.

## Alternatives
- **Uniform architecture regardless of domain classification** — simpler to reason about and staff (every subdomain gets the same layered architecture and review bar), but wastes effort on low-value code and under-serves the core; common in teams new to DDD who haven't yet trusted the distillation exercise.
- **Domain Storytelling / Event Storming as the distillation mechanism** — rather than a classification meeting, run collaborative modeling workshops (event storming) with domain experts to *discover* the core domain empirically, from the events and pain points that surface; often produces a more accurate classification than an armchair discussion, at the cost of needing facilitation skill and stakeholder time.
- **Wardley Mapping** — a strategy tool from outside the DDD literature that classifies capabilities by evolutionary stage (genesis, custom-built, product, commodity) rather than core/supporting/generic; conceptually parallel and sometimes used alongside DDD distillation to justify build-vs-buy decisions with a visual map stakeholders outside engineering can read.

## When to use it
At the start of any DDD initiative, before committing to bounded context boundaries or tactical patterns, and again whenever a system's scope grows (new subdomain, acquisition, pivot). It is the first thing to do, not an afterthought layered onto an existing architecture.

## When NOT to use it
For genuinely small systems with a single, obvious core and no supporting cast (a single-purpose internal tool), formal distillation is overhead — just build it well. It's also the wrong first move when the team has no access to domain experts at all; in that situation, invest first in getting that access, because distillation performed by engineers alone, without domain input, tends to reflect technical convenience rather than actual business value.

## Key takeaways / mental model
Before writing a single aggregate, ask: "is this subdomain the reason customers choose us, or is it necessary plumbing, or is it something anyone could buy?" Tactical DDD patterns are a budget, not a mandate — spend the budget on the core domain, and don't feel obligated to spend it everywhere.

## Self-check questions
1. Pick a system you've worked on. Classify three of its subdomains as core, supporting, or generic, and justify each classification using a concrete business fact (not a technical one).
2. A team has built a beautifully layered, aggregate-rich architecture for a subdomain that turns out to be generic (e.g. an internally-built time-tracking module identical to any commercial product). What is the cost of that decision, beyond the wasted build time?
3. How would you convince a stakeholder to "buy, not build" for a generic subdomain when the team has strong engineers eager to build it themselves?
4. Distillation can drift as a business evolves. Describe a realistic scenario where a supporting subdomain becomes core, and how a team would notice that shift is happening.

## References
- Implementing Domain-Driven Design (Vaughn Vernon), Chapter 1: "Getting Started with DDD".
- Domain-Driven Design (Eric Evans) — Part IV, "Strategic Design" — for the original core/supporting/generic and distillation vocabulary this chapter operationalizes; see `ddd-evans`.
