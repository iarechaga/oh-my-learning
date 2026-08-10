---
id: enterprise-patterns/01
subject: enterprise-patterns
title: Layering and the Enterprise Application
slug: layering
status: drafted
mastery:
seniority: mid
source: Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 1
prerequisites: [clean-architecture/08]
created: 2026-08-10
updated: 2026-08-10
---

# Layering and the Enterprise Application

## TL;DR
Fowler's foundational three-layer split — Presentation (interacting with the user/other systems), Domain (business logic and rules), Data Source (talking to the database or other persistence mechanisms) — is the concrete, older ancestor of the same separation-of-concerns idea `clean-architecture/08`'s dependency rule formalizes more strictly. This subject's whole catalog is organized around choices *within* the Domain layer (how business logic is structured) and *within* the Data Source layer (how objects map to storage) — layering is what makes discussing those choices independently meaningful.

## The idea
Enterprise applications — the broad, historically dominant category of business software this book targets (order processing, billing, HR systems, insurance claims) — share a recurring shape: they're heavily data-centric, they have substantial business rules governing that data, and they need to present that data and those rules to users (or other systems) through some interface. Fowler's layering separates these three concerns explicitly, precisely so that decisions about one (which UI framework, which database) don't have to entangle with decisions about another (what the business rules actually are) — directly the same underlying goal as `clean-architecture/08`'s dependency rule, developed independently and earlier, with a somewhat looser (three-layer, not four-circle) structure.

## How it works

### The three layers, precisely
- **Presentation** — everything concerned with handling interaction with whoever (or whatever) is using the system: rendering a UI, handling an HTTP request, formatting a response for an API consumer. This layer knows about the domain (it needs to display domain data), but the domain should not know about it (echoing `clean-architecture/11`'s "the web is a detail").
- **Domain** (also called Business Logic) — the actual rules, calculations, and validations that encode what the business does — directly corresponds to `clean-architecture/07`'s Entities and Use Cases, though Fowler's book, being older and somewhat less prescriptive about the internal split, treats "domain logic" more as a single conceptual layer whose *internal* organization (Transaction Script vs. Domain Model, `enterprise-patterns/02`) is itself a major design decision this subject explores.
- **Data Source** — everything concerned with getting data into and out of persistent storage: SQL queries, ORM mapping code, file I/O. Corresponds to `clean-architecture/11`'s "the database is a detail," and the specific patterns for structuring this layer (Active Record, Data Mapper, Table Data Gateway) are a major focus of this subject's later lessons.

### Why layering specifically helps enterprise applications
Enterprise applications have a specific characteristic that makes layering especially valuable: they tend to have substantial logic in *all three* layers simultaneously (unlike, say, a simple scientific computation program, which might have almost no meaningful "presentation" layer, or a simple content-display website, which might have almost no meaningful "domain" layer) — meaning all three axes of complexity (`philosophy-of-software-design/01`) are simultaneously present and need independent management, and a system that entangles them pays the compounded cost of all three tangled together.

**Worked example — a violation and its fix.** A common anti-pattern in enterprise systems: business validation logic embedded directly inside a web controller (Presentation layer), because it was convenient to write it right where the HTTP request was being handled. This means the validation logic can't be reused by a different Presentation mechanism (a batch job processing the same kind of data, a different API version) without duplicating it, and it means testing the validation logic requires spinning up the whole web request-handling machinery — directly the coupling problem `clean-architecture/11` names for the web specifically, here framed through this subject's slightly earlier, looser three-layer vocabulary. The fix: move the validation logic into the Domain layer, where it's reusable by any Presentation mechanism and testable in isolation.

### Layering versus this subject's own internal choices
A useful framing for the rest of this subject: the three-layer split itself is largely settled, uncontroversial architectural wisdom by this point (and this subject assumes it as a starting point, much as `clean-architecture` assumes the dependency rule) — what's genuinely *interesting* and worth a whole pattern catalog is the set of choices *within* each layer: how should the Domain layer itself be internally structured (`enterprise-patterns/02`-`03`)? How should the Data Source layer actually talk to the database (`enterprise-patterns/04`-`06`)? How do objects crossing the Domain/Data-Source boundary get correctly, efficiently mapped (`enterprise-patterns/07`-`10`)? This subject's remaining lessons are organized around exactly these within-layer decisions.

### Layering doesn't mean strict, one-directional dependencies by itself
A subtlety worth noting relative to `clean-architecture/08`'s more rigorous dependency rule: Fowler's original three-layer model, as commonly implemented in the era and style this book documents, doesn't always enforce as strict an inward-only dependency direction as Clean Architecture's four circles do — many classic enterprise patterns (Active Record, `enterprise-patterns/05`, being the clearest example) deliberately let the Domain layer's objects know something about persistence, trading some of the Dependency Rule's strict purity for developer convenience and less mapping code. This subject's later lessons will make this specific trade-off explicit wherever a pattern makes it (Active Record versus Data Mapper being the central such choice, `enterprise-patterns/05`-`06`) — layering here is a real, valuable separation, but not automatically as strict as `clean-architecture`'s more modern, more rigorously-enforced version.

## Pros
- Separating Presentation, Domain, and Data Source lets each layer's technology and structure evolve independently, and lets Domain logic be reused across multiple Presentation mechanisms.
- Concentrating business rules in one layer makes them independently testable without needing a running UI or a live database connection.
- Provides the shared vocabulary this entire subject's pattern catalog is organized around — every later lesson's patterns live within, or govern the boundary between, these three layers.

## Cons
- The three-layer split, on its own, doesn't prescribe *how* to structure the Domain or Data Source layers internally — those remain open, consequential decisions this subject's later lessons address.
- Some classic enterprise patterns (Active Record specifically) intentionally relax the strict separation between Domain and Data Source for convenience, meaning "layered" doesn't automatically imply the same rigor as `clean-architecture/08`'s dependency rule.
- For a genuinely simple application with thin logic in one or more layers, imposing the full three-layer discipline can be disproportionate ceremony, echoing this whole broader subject's repeated caution against over-applying structure without evidenced need.

## Alternatives
- **Clean Architecture's four-circle model** (`clean-architecture/08`) — a stricter, more rigorously enforced, more modern evolution of the same underlying separation, with an explicit inward-only dependency rule and formal boundary-crossing mechanism.
- **Two-layer split (merging Domain and Data Source)** — appropriate for very simple, mostly-CRUD applications where domain logic is thin enough that a dedicated, separate Domain layer adds little value beyond what Active Record-style merged objects already provide.
- **Hexagonal Architecture / Ports and Adapters** — a closely related, largely equivalent framing to Clean Architecture, using different terminology (ports/adapters) for essentially the same layered-boundary idea.

## When to use it
Apply the three-layer split to any application with substantial logic in more than one of the three areas (presentation, business rules, persistence) — which describes the large majority of real-world "enterprise" business applications this book targets.

## When NOT to use it
Don't impose the full three-layer discipline on a genuinely thin, simple application where one or more layers barely exist in practice — a basic content-display site with negligible domain logic, for instance, gains little from a formally separated Domain layer.

## Key takeaways / mental model
Before writing any piece of logic, ask which of the three layers it genuinely belongs to: does it format/display something (Presentation), does it encode a business rule or calculation (Domain), or does it talk to storage (Data Source)? Keeping that classification honest, even under the convenience pressure of "it's easier to just put it here," is what makes the rest of this subject's patterns meaningful.

## Self-check questions
1. Using the validation-logic example, explain precisely why embedding business validation in a web controller creates a reuse and testability problem, and how moving it to the Domain layer fixes both.
2. How does this subject's three-layer model relate to, and differ in strictness from, `clean-architecture/08`'s four-circle dependency rule?
3. Why does Fowler note that Active Record deliberately relaxes the Domain/Data-Source separation? What's being traded for what?
4. Describe a genuinely simple application where imposing the full three-layer split would be disproportionate, and explain what a simpler structure would look like instead.

## References
- Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 1: "Layering".
