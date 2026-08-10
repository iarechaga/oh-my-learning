---
id: ddd-distilled/01
subject: ddd-distilled
title: What DDD is and when to use it
slug: what-ddd-is-and-when-to-use-it
status: drafted
mastery:
seniority: junior
source: Domain-Driven Design Distilled (Vaughn Vernon), Chapter 1 "DDD for Me"
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# What DDD is and when to use it

## TL;DR
Domain-Driven Design is a set of practices for modeling software so that the code's
structure, names, and boundaries mirror how the business actually thinks and talks about
its problem. It is not a framework, a layered architecture, or a folder-naming
convention — it is a discipline for keeping the model and the code honest about a
specific, bounded slice of a business, applied where the payoff (a genuinely hard,
differentiating problem) justifies the investment.

## The idea
Most software eventually accumulates a gap between "what the business actually does" and
"what the code actually says." Requirements get translated by an analyst, then again by a
developer, then squeezed into whatever data model or framework convention was already in
place — and each translation loses precision. Six months later, a bug shows up because
the code's notion of "cancel an order" doesn't match what "cancel" means to the person in
the warehouse, and nobody notices until it costs money.

DDD exists to close that gap deliberately. Its core claim is that the *domain* — the
subject-matter problem the software exists to solve (insurance underwriting, ride
matching, loan origination) — deserves to be modeled explicitly and continuously refined
in collaboration with the people who understand it best (domain experts), and that the
resulting model should be visible directly in the code, not buried under generic
technical abstractions. Eric Evans introduced these ideas in *Domain-Driven Design*
(2003); Vaughn Vernon's *Domain-Driven Design Distilled* (this subject's source book) is
a compact, practitioner-oriented tour of the same ideas written over a decade later, once
the community had learned which parts mattered most in practice.

DDD is best understood as two intertwined halves:
- **Strategic design** — deciding *where* to draw boundaries: which parts of a large
  system are the differentiating "core domain" worth deep modeling investment, and how
  separately-modeled parts of a system relate to each other (`ddd-distilled/03`,
  `ddd-distilled/04`).
- **Tactical design** — the building blocks used *inside* a boundary once you've decided
  to model something carefully: entities, value objects, aggregates, domain services,
  domain events (`ddd-distilled/05` through `ddd-distilled/08`).

Crucially, DDD is not "always model everything this carefully." Most of a real system is
not the differentiating part — it's supporting or generic machinery (user auth, invoicing,
email delivery) that can be bought, borrowed, or built quickly and shallowly. DDD's
strategic half exists precisely to help you tell the two apart so you don't over-invest
everywhere (`ddd-distilled/04`).

## How it works

### The three questions DDD asks before any tactical modeling begins
Vernon frames the primer around three big strategic questions, and this lesson is really
about question one:

1. **What is the core domain, and is it even worth a deep model?** (`ddd-distilled/04`)
2. **How is the problem broken into bounded contexts, and how do they relate?**
   (`ddd-distilled/03`, `ddd-distilled/04`)
3. **What language does the team use, and is it consistent within each context?**
   (`ddd-distilled/02`)

Only after these are reasonably answered does it make sense to reach for entities,
aggregates, and events — applying tactical patterns before you know where your
boundaries are is a common and expensive mistake (see "When NOT to use it" below).

### Worked example — a ride-hailing company deciding where DDD applies
Imagine a ride-hailing startup building: rider-driver matching, dynamic pricing, trip
tracking, driver background checks, payments, and a marketing website.

- **Matching and dynamic pricing** are where the company actually competes — the
  algorithms and the domain rules here (how surge pricing responds to demand, how a
  driver is matched to a rider given ETA, rating, and vehicle type) are unique,
  change constantly, and directly drive revenue. This is a strong candidate for the
  **core domain**: worth a rich model, worth your best engineers, worth ongoing
  refinement with product/ops experts.
- **Background checks** matter (compliance risk) but the *logic* of "is this person
  eligible to drive" is largely dictated by regulation and a third-party vendor API —
  supporting, not core.
- **Payments** could be entirely outsourced to Stripe; the domain logic here is thin —
  generic subdomain.
- **The marketing website** has essentially no domain complexity worth modeling — plain
  CMS territory.

DDD says: pour deep modeling effort, ubiquitous language work, and careful aggregate
design into matching/pricing. Everything else gets "good enough" software engineering
without the DDD ceremony. This triage is what `ddd-distilled/04` teaches in detail; this
lesson just establishes that the triage itself is the first DDD skill, not an
afterthought.

### Worked example — recognizing when DDD would have helped after the fact
A team building an insurance claims system used one generic `Claim` database table with
30 nullable columns shared across auto, home, and health claims, because "a claim is a
claim." Six months in, a rule change for auto claims ("total loss threshold changed from
70% to 75% of vehicle value") required a conditional that only made sense for auto rows,
bolted onto code shared by all three claim types, and it silently broke health-claim
validation logic that happened to read the same nullable field for something unrelated.
A DDD-informed team would have asked, early: is "claim" actually one concept, or do auto,
home, and health claims belong to different bounded contexts with their own models and
their own definition of what a claim even *is*? That question — not any specific pattern
like Entity or Aggregate — is the value DDD would have added here.

## Pros
- Aligns code vocabulary with business vocabulary, which reduces translation errors and
  makes it easier for domain experts to review whether the software actually does what
  they mean (`ddd-distilled/02`).
- Directs scarce senior-engineering and design effort at the parts of the system that
  actually differentiate the business, instead of spreading effort evenly.
- Produces boundaries (bounded contexts) that tend to map cleanly onto team boundaries
  and deployable units, which pays off again at the architecture and organizational
  level (Conway's Law working *for* you instead of against you).
- Makes change safer over time in the core domain, because a model built around real
  domain concepts flexes the way the business's understanding evolves, rather than
  requiring a rewrite every time a database-table shortcut breaks down.

## Cons
- Real up-front cost: workshops, glossary work, and iteration with domain experts take
  calendar time that a team under deadline pressure may not feel they have.
- Requires access to genuine domain experts — if no one in the room actually understands
  the business deeply, DDD collaborative modeling has nothing to work with.
- Easy to over-apply: teams that read about aggregates and value objects sometimes apply
  them to every CRUD screen in the system, adding ceremony with no matching payoff
  (`ddd-distilled/04` gives the antidote — the core/supporting/generic split).
- The vocabulary itself (bounded context, aggregate, ubiquitous language) has a learning
  curve, and misapplied terminology can make a team *sound* like it's doing DDD while
  actually just adding layers of indirection.

## Alternatives
- **Plain pragmatic/CRUD design** — model straight off the database schema with thin
  service layers. Perfectly fine, and often *preferable*, for supporting/generic
  subdomains where there is no real domain complexity to capture (`ddd-distilled/04`).
- **Domain modeling without full DDD ceremony** — some teams borrow just ubiquitous
  language and bounded contexts (the strategic half) without adopting aggregates,
  domain events, or repositories (the tactical half). This is a legitimate lightweight
  adoption path, and is essentially what `ddd-distilled/09` calls incremental adoption.
- **Data-driven / anemic-model architectures** (e.g., a straightforward layered
  architecture with services operating on plain data objects) — simpler to onboard new
  engineers into, but loses the self-validating, rule-enforcing behavior that rich
  domain models (`ddd-distilled/05`, `ddd-distilled/06`) provide; usually fine until the
  business rules get complex enough that validation logic starts scattering across many
  services.

## When to use it
Reach for DDD when: the domain is genuinely complex (lots of business rules, edge cases,
and terminology that domain experts argue about), the system is expected to live and
evolve for years, correctness/consistency of business rules matters a lot (regulated
industries, financial transactions, safety-critical logic), and — most importantly —
domain experts are actually available to collaborate. The strategic half (bounded
contexts, ubiquitous language) is cheap enough that it's worth applying even to modest
projects; the tactical half is worth the ceremony specifically in the core domain.

## When NOT to use it
Skip DDD's heavier tactical machinery for CRUD-shaped features, thin integration glue,
internal tooling with a handful of users, prototypes/spikes meant to be thrown away, or
any subdomain that's genuinely generic (auth, billing you could buy off the shelf,
notification delivery). Applying aggregates and domain events to a settings page or an
admin dashboard is pure ceremony with no corresponding payoff — the "distilling the core
domain" skill in `ddd-distilled/04` exists precisely to stop this over-application before
it starts.

## Key takeaways / mental model
DDD is a *triage-then-model* discipline, not a pattern catalog to apply uniformly. First
decide where the business complexity and differentiation actually live (strategic
design); only then invest tactical modeling effort there, in proportion to how much that
part of the system matters. If you remember one sentence: "model deeply where it's core,
model cheaply everywhere else — and figure out which is which by talking to the people
who actually know the domain."

## Self-check questions
1. Pick a system you've worked on. Which parts would you call core domain, and which
   supporting or generic? What would change about how you'd build each part differently
   if you applied that split deliberately?
2. A junior engineer says "we're doing DDD" because they renamed their `UserService`
   class to `UserAggregate`. What's missing from that claim, given what DDD actually is?
3. Why does DDD insist on collaboration with domain experts specifically, rather than
   just having senior engineers infer the domain from requirements documents?
4. Give an example (real or hypothetical) of a project where applying full DDD tactical
   patterns would be a mistake, and explain what you'd do instead.

## References
- Domain-Driven Design Distilled (Vaughn Vernon), Chapter 1: "DDD for Me".
- For the foundational, book-length treatment of these ideas, see `domain-modeling/ddd-evans`
  (Eric Evans's original text) and `domain-modeling/implementing-ddd` (Vernon's
  full-length implementation guide) — this subject is deliberately the fast on-ramp;
  those two go far deeper on every pattern introduced here.
