---
id: ddd-evans/01
subject: ddd-evans
title: Knowledge crunching and ubiquitous language
slug: knowledge-crunching-and-ubiquitous-language
status: drafted
mastery:
seniority: mid
source: Domain-Driven Design (Eric Evans), Part I, Chapters 1-2
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# Knowledge crunching and ubiquitous language

## TL;DR
Software gets its value from modeling a domain usefully, not from clever code. Knowledge crunching is the collaborative, iterative process of digesting messy domain knowledge into a model; ubiquitous language is the discipline of using that model's exact vocabulary — no translation layer — in speech, code, tests, and diagrams alike.

## The idea
Most software failures aren't technical failures — they're modeling failures. A team builds a system that technically works but doesn't actually capture how the business thinks about its own domain, so every new feature requires reverse-engineering intent from code that speaks a different language than the domain experts do. Evans's core claim is that the model isn't a diagram you draw once during analysis and then discard — it's a living, evolving asset that the code itself should embody, and it can only stay useful if the whole team (developers and domain experts) is constantly refining it together.

Two ideas do the heavy lifting here:

**Knowledge crunching** is what happens when developers and domain experts sit together, repeatedly, and squeeze a vague, messy understanding of the business into a sharper model — the same way you'd crunch raw data into a useful summary. It's not a single requirements-gathering meeting; it's an ongoing conversation where the developers ask "why" until they understand the domain well enough to challenge the expert's mental model, and the expert corrects the developers' misunderstandings until a shared, more rigorous model emerges. The knowledge doesn't flow one way (expert to developer transcription) — it's genuinely collaborative, and often the *developers* end up finding gaps or contradictions in how the experts themselves described the domain, because turning something into an unambiguous model exposes hand-waving that ordinary conversation tolerates.

**Ubiquitous language** is the practical output and ongoing discipline: pick the vocabulary that names the concepts in the model, and use those exact words everywhere — domain experts use them when describing requirements, developers use them in class names, method names, and variable names, QA uses them in test names, and nobody maintains a private "business terms map to code terms" translation table in their head. The translation layer is the enemy: every time a developer mentally converts "the customer wants to expedite an order" into `Shipment.setPriorityFlag(true)`, that translation step is a place where meaning silently leaks or drifts, and it means the code can no longer be read as a direct expression of the domain.

## How it works

### The knowledge-crunching cycle
1. A developer and a domain expert discuss a scenario ("what happens when a customer cancels a partially-shipped order?").
2. The developer proposes a model fragment — a sketch of objects, relationships, and rules — often on a whiteboard, in whatever notation is fastest (UML is optional; a box-and-arrow sketch is fine).
3. The domain expert reacts: "no, that's not right, a partially-shipped order can't be fully cancelled, only the unshipped items can be cancelled" — this is the crunch, the moment a vague verbal description gets forced into something precise enough to be wrong or right.
4. The model is revised. Crucially, the *language* used to describe the revised model becomes the term going forward: "partial cancellation" becomes a first-class concept, not just a sentence.
5. Repeat, continuously, for the life of the project — not just during a discovery phase.

### Worked example: an insurance claims domain
Suppose the initial requirement is "the system should let adjusters process claims." That sentence hides enormous ambiguity. Knowledge crunching forces specificity:
- Developer: "What does 'process' mean exactly — is it one step or several?"
- Expert: "Well, first it's *submitted*, then an adjuster does an *assessment*, and depending on the assessment it's either *approved*, *denied*, or sent for *further investigation*."
- Developer: "Can an approved claim go back to investigation?"
- Expert: "No — once approved, it's locked, we'd have to open a *new* claim referencing the old one, we call that a *supplemental claim*."

That five-minute exchange has already produced real domain vocabulary — `Claim`, `Assessment`, `Submitted`, `Approved`, `Denied`, `UnderInvestigation`, `SupplementalClaim` — that becomes class names, enum values, and state-machine transitions directly, not "ticket status codes" invented by a developer guessing at business rules. This connects directly to `ddd-evans/02`: the domain layer's classes should read like this vocabulary, not like a generic CRUD schema.

### Worked example: the language exposes a hidden concept
A team building a shipping system kept saying "the route the cargo takes." A domain expert casually mentioned "well, a *leg* is a straight run between two ports — a route is a sequence of legs." Nobody had modeled `Leg` because it hadn't come up in the requirements doc. Once "leg" entered the shared vocabulary, the model gained a real class, and rules about connection times and customs regulations attached naturally to `Leg` instead of being scattered as edge-case conditionals inside `Route`. This is knowledge crunching working exactly as intended: the language surfaces a concept the initial model was missing, and the code afterward changes to include it explicitly.

### Enforcing the language in artifacts
Ubiquitous language isn't just a conversational nicety — it must show up in:
- **Code**: class names (`SupplementalClaim`, not `ClaimV2`), method names (`assess()`, not `processStep2()`).
- **Tests**: test names and fixtures use the same nouns and verbs as the domain expert.
- **Diagrams and documents**: any UML or sketch shared with domain experts uses the same terms as the code — if a diagram says "Order" and the code says "PurchaseRequest," that's a language fork, and it will eventually cause a costly miscommunication.
- **Bug reports and standup conversations**: if a developer says "the flag isn't getting set" instead of "the claim isn't getting approved," the language is already drifting away from the domain and toward implementation detail, which is a warning sign that the model itself may be leaking, see `ddd-evans/02`.

### When the language reveals disagreement, don't paper over it
Sometimes crunching surfaces that two departments use the same word to mean different things — "customer" might mean "the person who placed the order" to sales and "the billing entity" to finance. This is often the first sign you need `ddd-evans/14` (bounded contexts): rather than forcing one universal definition, you draw an explicit boundary and let each context have its own precise, locally ubiquitous language for "Customer."

## Pros
- Aligns code directly with how the business actually talks about itself, dramatically reducing the "impedance mismatch" between requirements conversations and implementation.
- Surfaces hidden domain concepts and hidden disagreements early, when they're cheap to resolve, rather than after they've calcified into schema and API contracts.
- Makes onboarding new developers faster — the domain vocabulary is discoverable directly in the code rather than living only in senior engineers' heads or a stale wiki.
- Makes conversations with domain experts about behavior (not implementation) possible, because both sides can point at the same nouns and verbs.

## Cons
- Requires sustained access to domain experts — if they're unavailable or disengaged, knowledge crunching degrades into developers guessing at the domain, which reintroduces exactly the gap this practice exists to close.
- Rigor takes real time and can feel slow compared to just writing code against a requirements doc; the payoff is not immediate.
- Language that's precise for developers can feel unnaturally formal to domain experts in casual conversation, creating friction if not handled with some flexibility (a glossary, not a straitjacket).
- Doesn't scale to a single universal vocabulary across a large organization — different parts of a large business genuinely mean different things by the same word, which is exactly why bounded contexts (`ddd-evans/14`) exist as a companion pattern, not an alternative.

## Alternatives
- **Traditional requirements documents / BRDs written by business analysts** — a one-way handoff from analyst to developer; faster upfront but loses the iterative correction loop, and the resulting vocabulary is whatever the analyst happened to write down, not something battle-tested against the actual code's behavior.
- **Event storming** — a more modern, workshop-style technique (not in the original book, developed later by Alberto Brandolini) that achieves a similar knowledge-crunching effect but through a structured sticky-note exercise mapping domain events; often faster to run with a large group. See `learning-ddd` for a treatment centered on this and other modern discovery techniques.
- **Data-modeling-first approaches** — start from the database schema or API contract and let vocabulary follow from field names; this inverts the relationship this lesson argues for (language should drive the model, not the other way around) and tends to produce anemic, storage-shaped models rather than behavior-shaped ones.

## When to use it
Use knowledge crunching and ubiquitous language whenever the domain has real complexity worth capturing precisely — anywhere business rules, not just data storage, are the hard part of the system. It's especially valuable at project kickoff and whenever a new feature touches unfamiliar territory of the domain.

## When NOT to use it
For a domain that's genuinely simple — a CRUD admin panel with no real business rules, a data pipeline that just moves records around — the overhead of formal knowledge crunching exceeds its value; a lighter-weight conversation is enough, and forcing heavyweight ceremony onto a trivial domain is itself a violation of matching effort to complexity, a theme this whole book returns to (see `ddd-evans/13` on recognizing where complexity does and doesn't live).

## Key takeaways / mental model
The model is not documentation *about* the code — the model *is* the code (or as close to it as the implementation language allows), and the language is the thread that keeps model, code, and domain-expert conversation from silently diverging into three different mental pictures of the same system.

## Self-check questions
1. Describe a time (in any codebase you've worked on) where the code's vocabulary diverged from the business's vocabulary. What problems did that translation gap cause?
2. In the insurance claims example, why does "SupplementalClaim" deserve to be its own concept rather than just adding a `supplementalOf` field to `Claim`?
3. A domain expert and a developer disagree on what "active customer" means. Is this a bug to fix immediately, or a signal pointing toward another pattern? Which one, and why?
4. Why does the book insist the language must appear in code, not just in documentation or diagrams?

## References
- Domain-Driven Design: Tackling Complexity in the Heart of Software (Eric Evans), Chapter 1: "Crunching Knowledge" and Chapter 2: "Communication and the Use of Language".
