# Domain-Driven Design Distilled

A compact recap of *Domain-Driven Design Distilled* by Vaughn Vernon, concept by
concept. This subject is the fast on-ramp to DDD: enough strategic and tactical
vocabulary to build a correct mental map before going deeper in
`domain-modeling/ddd-evans`, `domain-modeling/implementing-ddd`, or
`domain-modeling/learning-ddd`.

Progress note: all 9 lessons are `drafted`; none have been discussed yet, so mastery
is pending across the board and no weak spots are recorded yet. This page will gain
depth (especially on the concepts the learner finds hard) as discussions happen - the
last section below will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom: quick
strategic framing first (what DDD is, language, boundaries, distillation), then tactical
essentials (entities, aggregates, repositories/services, events), then adoption guidance
for real, existing systems.

## Strategic framing

- **[ddd-distilled/01] What DDD is and when to use it** - a discipline for aligning code
  structure with how the business actually thinks, applied selectively where the payoff
  (a genuinely complex, differentiating domain) justifies it; triage before tactical
  modeling. ([lesson](lessons/01-what-ddd-is-and-when-to-use-it.md))
- **[ddd-distilled/02] Ubiquitous language and collaborative modeling** - a shared
  vocabulary built jointly with domain experts, consistent within a bounded context (not
  globally), kept in sync with the code through ongoing conversation, not a frozen
  glossary. ([lesson](lessons/02-ubiquitous-language-and-collaborative-modeling.md))
- **[ddd-distilled/03] Bounded contexts and context maps** - explicit boundaries within
  which one model and language apply consistently; context maps document how contexts
  relate (Partnership, Customer-Supplier, Conformist, Anticorruption Layer, Open Host
  Service, Separate Ways). ([lesson](lessons/03-bounded-contexts-and-context-maps.md))
- **[ddd-distilled/04] Distilling the core domain** - sort subdomains into core
  (competitive differentiator, deep investment), supporting (necessary but not
  differentiating), and generic (buy, don't build) so effort matches business impact.
  ([lesson](lessons/04-distilling-the-core-domain.md))

## Tactical building blocks

- **[ddd-distilled/05] Entities and value objects** - entities have persistent identity
  that outlives attribute changes; value objects are fully described by their
  attributes, immutable, compared by value. Getting this split right underlies every
  later tactical pattern. ([lesson](lessons/05-entities-and-value-objects.md))
- **[ddd-distilled/06] Aggregates and consistency boundaries** - a cluster of entities
  and value objects with one root as the sole entry point, sized around one true
  invariant; keep aggregates small, reference other aggregates by identity only.
  ([lesson](lessons/06-aggregates-and-consistency-boundaries.md))
- **[ddd-distilled/07] Repositories and domain services** - repositories give the domain
  model an in-memory-collection illusion over persistence (one per aggregate root);
  domain services hold logic that spans aggregates or has no natural single-entity home.
  ([lesson](lessons/07-repositories-and-domain-services.md))
- **[ddd-distilled/08] Domain events and eventual consistency** - immutable, past-tense
  facts that carry coordination across aggregate and bounded-context boundaries;
  consistency is instant inside an aggregate, eventual across boundaries - design for the
  gap explicitly. ([lesson](lessons/08-domain-events-and-eventual-consistency.md))

## Adoption in the real world

- **[ddd-distilled/09] Strategic redesign and incremental adoption** - context-map an
  existing (often legacy) system to find implicit boundaries already present; use event
  storming to discover process and vocabulary fast; extract toward the target boundaries
  incrementally (module first, service later) instead of a big-bang rewrite.
  ([lesson](lessons/09-strategic-redesign-and-incremental-adoption.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
