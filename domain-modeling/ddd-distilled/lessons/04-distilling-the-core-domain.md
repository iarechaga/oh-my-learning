---
id: ddd-distilled/04
subject: ddd-distilled
title: Distilling the core domain
slug: distilling-the-core-domain
status: drafted
mastery:
seniority: senior
source: Domain-Driven Design Distilled (Vaughn Vernon), Chapter 3 "Strategic Design with Subdomains"
prerequisites: [ddd-distilled/03]
created: 2026-08-10
updated: 2026-08-10
---

# Distilling the core domain

## TL;DR
"Distillation" is the strategic exercise of sorting a system's bounded contexts (or
candidate subdomains) into **core**, **supporting**, and **generic**, so that scarce
modeling effort, senior engineering talent, and design rigor go where they actually move
the business's competitive needle — instead of being spread evenly across a system where
most of it doesn't matter equally.

## The idea
Not every part of a system deserves the same investment. A company's differentiating
advantage — the reason customers choose them over a competitor — usually lives in a
small slice of the overall system. Everything else exists to support that slice, or is
common infrastructure that every company in the industry needs and gets no advantage
from building uniquely. Treating all of it as equally important is a resourcing mistake:
it means your best engineers might spend months perfecting an internal admin tool while
the actual differentiator gets whatever attention is left over.

Vernon's distillation vocabulary gives this triage a name and a process:

- **Core domain** — the part of the system that is the primary reason the business is in
  business, or the part that most directly creates competitive advantage. This deserves
  your best people, the deepest modeling investment (rich tactical patterns — entities,
  aggregates, domain events), and the most iteration with domain experts.
- **Supporting subdomain** — necessary for the business to function, connects to or
  enables the core domain, but is not itself a source of competitive advantage. Worth
  building well, but with a lighter model and less ceremony than the core.
- **Generic subdomain** — a problem that's been solved the same way across the whole
  industry (authentication, payment processing, email delivery, PDF generation). No
  competitive advantage comes from building this yourself; the default move is to buy,
  use an open-source library, or outsource it, not to model it deeply in-house.

Distillation is not a one-time classification exercise done at project kickoff — a
subdomain's category can shift as the business strategy shifts (a company that starts
treating its logistics/fulfillment as a competitive differentiator, rather than a cost
center, effectively promotes it from supporting to core), and revisiting the
classification periodically is part of keeping strategic design honest.

## How it works

### The classification exercise
For each bounded context or candidate subdomain, ask: **if we did this significantly
better than every competitor, would customers pick us because of it?** If yes, it's core.
Then ask: **is this something the business must have to operate, that customers don't
choose us for on its own merits?** If yes, supporting. Finally: **is this a solved
problem the whole industry does essentially the same way?** If yes, generic.

This exercise is best done *with* people who understand company strategy, not by
engineers guessing — distillation is as much a business-strategy conversation as a
technical one, which is why Vernon places it alongside bounded contexts and ubiquitous
language as strategic (not tactical) design.

### Worked example — a fintech lending platform
- **Underwriting / credit-risk decisioning** — the proprietary rules and models that
  decide who gets approved, at what rate, with what terms. This is the company's actual
  product; two lenders offering similar rates differentiate mainly on underwriting speed
  and accuracy. **Core domain.** Deep tactical modeling justified: rich `LoanApplication`
  aggregate (`ddd-distilled/06`), domain events for each underwriting decision stage
  (`ddd-distilled/08`), heavy investment in getting the ubiquitous language exactly right
  with underwriting experts.
- **Document collection and verification (KYC/identity checks)** — necessary, regulated,
  but the actual verification logic is largely delegated to third-party identity
  verification vendors. **Supporting subdomain** — build a clean integration and
  workflow around it, but don't reinvent identity verification.
- **Payment processing / ACH transfers** — every fintech needs this, none differentiate
  on it, and mature vendors (Stripe, Plaid, Dwolla) solve it well. **Generic subdomain**
  — buy, don't build.
- **Internal HR/payroll tools** — necessary for the company to function as an
  organization, zero connection to the lending product. **Generic**, arguably not even
  worth building — buy off-the-shelf software.

The engineering consequence of this classification is concrete: underwriting gets a
senior team, deliberate aggregate design, and ongoing collaborative modeling sessions.
Document verification gets a competent integration engineer and a reasonably clean
workflow, reusing a vendor. Payment processing gets whatever the vendor's SDK provides
wrapped in a thin anticorruption layer (`ddd-distilled/03`). No one spends a quarter
perfecting the payroll tool's domain model.

### Worked example — a mistake corrected by distillation
A logistics startup initially treated its **route optimization algorithm** as supporting
("we just need routes generated, doesn't need to be fancy") and put its best engineers on
building an elaborate **driver-facing mobile app UI** instead, reasoning that a polished
app was what customers would notice. Eighteen months later, they realized competitors
were winning contracts specifically because their routes were meaningfully more
fuel/time-efficient — routing was the actual differentiator, the UI was merely
supporting. Redistilling and reallocating senior engineering effort to the routing
algorithm (now correctly classified core) was a late but necessary correction. The
lesson: misclassifying core as supporting is a strategic error with real cost, and it's
worth revisiting the classification explicitly rather than assuming yesterday's answer
still holds.

### Distillation and bounded contexts together
Distillation usually operates on the same units as bounded contexts (`ddd-distilled/03`)
— a core/supporting/generic subdomain often *is* a bounded context, or maps closely to
one — but the two questions are logically distinct: bounded-context analysis asks "where
are the model boundaries," distillation asks "how much investment does each boundary
deserve." A context map annotated with core/supporting/generic labels on each box is a
genuinely useful combined artifact.

## Pros
- Directs limited senior-engineering time and design rigor where it has outsized
  business impact, instead of spreading it evenly (or worse, spending it disproportionately
  on whatever's loudest or most visible, like a UI).
- Gives an explicit, defensible answer to "why are we buying this instead of building
  it" (generic subdomains) and "why is this small part of the system getting so much
  design attention" (core domain) — useful for engineering-leadership conversations and
  budget justification.
- Prevents the DDD over-application failure mode described in `ddd-distilled/01` — it's
  the concrete mechanism that stops teams from applying aggregates and domain events
  everywhere.
- Encourages periodic reassessment, which keeps engineering investment aligned with
  changing business strategy rather than frozen at a stale, kickoff-time judgment.

## Cons
- Requires genuine business-strategy insight, not just technical judgment — engineers
  alone often misjudge what's actually core (the routing-algorithm example above is a
  common shape of mistake, usually in the direction of overvaluing user-visible polish).
- Classification can be organizationally contentious: telling a team their subsystem is
  "generic, go buy a vendor" can read as a judgment on the team's work, requiring careful
  communication.
- Categories can be genuinely ambiguous, especially for supporting-vs-core boundary
  cases, and reasonable people disagree — there's no formula, only a structured
  conversation.
- A stale classification (not revisited as strategy shifts) actively misdirects
  investment, arguably worse than having no classification at all because it creates
  false confidence.

## Alternatives
- **Uniform investment across all subsystems** — simpler to reason about and avoids the
  political friction of classification, but wastes scarce senior talent and often
  under-invests in the actual differentiator; this is the default failure mode
  distillation exists to correct.
- **Pure cost-center/profit-center financial classification** — a coarser,
  finance-department-driven version of the same idea, useful as an input but usually too
  blunt to guide subsystem-level engineering decisions on its own.
- **Wardley Mapping** — a related strategic technique from the broader business-strategy
  world that maps components by evolution stage (genesis to commodity) and value chain
  position; produces similar buy-vs-build guidance from a different angle and pairs well
  with distillation for teams that want a visual, evolution-aware view.

## When to use it
Apply distillation at the start of any project with more than a couple of subsystems, and
revisit it at major strategy inflection points (a pivot, a new competitive threat, an
acquisition). It's especially valuable input to hiring and staffing decisions (put your
strongest engineers on core) and to build-vs-buy decisions (default to buy for anything
confidently classified generic).

## When NOT to use it
Skip formal distillation for genuinely tiny systems with one subdomain and no meaningful
internal boundaries — there's nothing to triage. Also be wary of using distillation as a
one-time, permanent label; treating a subdomain's classification as immutable is itself a
misuse of the technique.

## Key takeaways / mental model
Ask three questions per subsystem: would customers choose us because of this
(core)? Is it necessary infrastructure for the business, but not why they choose us
(supporting)? Is it a solved industry-wide problem with no competitive angle (generic)?
Then invest — senior people, deep modeling, ongoing collaborative refinement — in direct
proportion to the answer, and don't be afraid to reclassify when strategy changes.

## Self-check questions
1. Take a system you know well and classify its major subsystems as core, supporting, or
   generic. Would your organization's actual staffing and design investment match that
   classification today?
2. Explain why "the part of the system customers interact with most" is not the same
   question as "the part of the system that is core domain" — give an example where
   they diverge (like the logistics UI-vs-routing example above).
3. Why might a subdomain's classification legitimately change over time? Give a
   hypothetical example of a supporting subdomain being promoted to core.
4. A colleague argues distillation is "just prioritization with extra vocabulary." What
   would you say distillation adds beyond generic prioritization — specifically in terms
   of how it changes tactical modeling decisions in `ddd-distilled/05` and
   `ddd-distilled/06`?

## References
- Domain-Driven Design Distilled (Vaughn Vernon), Chapter 3: "Strategic Design with
  Subdomains".
- For deeper strategic-design case studies and the original core-domain vocabulary, see
  `domain-modeling/ddd-evans`.
