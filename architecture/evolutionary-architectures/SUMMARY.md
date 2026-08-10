# Building Evolutionary Architectures - Subject Summary

A comprehensive recap of the evolutionary-architectures subject, concept by concept.
This subject is the change-over-time layer of the architecture track: how to build
(and retrofit) architectures that can absorb requirement changes cheaply and safely,
using fitness functions as the automated, objective guardrails that keep change
*guided* rather than accidental.

**Source book:** *Building Evolutionary Architectures*, 2nd edition - Neal Ford,
Rebecca Parsons, Patrick Kua, and Pramod Sadalage (O'Reilly, 2022).

**Progress note:** all 9 lessons are `drafted`; none discussed yet, so mastery is
pending and no weak spots are recorded. See the table in [README.md](README.md).
Reading order is top to bottom (dependency-ordered): the definition and fitness
functions first, then incremental change and coupling, then data, then the
higher-band retrofitting/pitfalls/governance lessons.

## Foundations: what evolutionary architecture is, and how it's guided

- **[01] What an evolutionary architecture is** - the formal definition ("guided,
  incremental change across multiple dimensions"); why "evolvable" beats "future-proof"
  as a goal (you can't reliably predict change, but you can build the capacity to
  absorb it cheaply); the biological-evolution metaphor and where it breaks down
  (software evolution is *directed*, not random, unlike natural selection); the
  last-responsible-moment principle for decision timing. ([lesson](lessons/01-what-evolutionary-architecture-is.md))
- **[02] Fitness functions** - the core mechanism that makes change "guided": an
  objective, automatable integrity check for an architectural characteristic, borrowed
  from the genetic-algorithm concept of the same name. Anatomy of a fitness function
  (characteristic, mechanism, trigger, criterion, consequence); worked examples
  (dependency-direction check, performance-budget CI gate, security-scan gate).
  ([lesson](lessons/02-fitness-functions.md))
- **[03] Categories of fitness functions** - the taxonomy: atomic vs. holistic
  (single-component vs. cross-cutting scope), triggered vs. continual (event-driven vs.
  always-on), static vs. dynamic (fixed vs. context-sensitive thresholds), plus
  domain-specific and temporal variants. Most teams' fitness-function suites cluster in
  the cheap corner (atomic/triggered/static), systematically under-covering
  cross-cutting and non-deploy-triggered regressions. ([lesson](lessons/03-fitness-function-categories.md))

## Mechanism: how change actually moves, and where its boundaries are

- **[04] Incremental change (deployment pipelines)** - the delivery mechanism for
  evolutionary change: staged, automated pipelines (build -> test -> fitness functions
  -> deploy) that make fitness-function feedback fast enough to be useful. Distinguishes
  incremental *development* (small PRs) from incremental *deployment* (actually
  shipping them independently) - having only the first doesn't give you evolutionary
  architecture. Pipeline speed is structural, not a productivity nicety: slow pipelines
  reintroduce large-blast-radius risk and stale feedback. ([lesson](lessons/04-incremental-change.md))
- **[05] Architectural coupling and quanta** - the architecture quantum (an
  independently deployable artifact with high functional cohesion, high internal static
  coupling, and its own operational data) as the *real* boundary for independent
  evolution, regardless of what the repo/container layout or org chart suggests.
  Recaps static vs. dynamic coupling from `hard-parts/02`-`03` and shows how shared
  databases or tight synchronous calls silently merge intended-separate services into
  one real quantum. ([lesson](lessons/05-coupling-and-quanta.md))
- **[06] Evolutionary data** - schema changes need the same discipline as code changes:
  versioned, incremental, pipeline-applied migrations, via the expand/contract pattern
  (add the new structure, dual-write/transition, then remove the old structure once
  verified) for zero-downtime evolution. A shared database between services is the
  single worst form of static coupling and the primary obstacle to genuine quantum
  independence - no application-layer abstraction fixes it. ([lesson](lessons/06-evolutionary-data.md))

## Practice: retrofitting, failure modes, and governing at scale

- **[07] Building evolvable architectures (retrofitting)** - staff-level material: most
  real systems weren't designed for evolvability, so retrofitting means (1)
  evidence-based discovery of the *actual* coupling and quanta (tracing DB access, call
  graphs, deploy correlation - not trusting diagrams), (2) prioritizing which
  characteristics get fitness functions first based on real incident history, and (3)
  incremental, strangler-fig-style decoupling using the same expand/contract discipline
  as data migrations, generalized to architecture as a whole. ([lesson](lessons/07-building-evolvable-architectures.md))
- **[08] Evolutionary architecture pitfalls and antipatterns** - five named failure
  modes: the last 10% trap (generic solutions get disproportionately hard to finish),
  inappropriate governance (uniform standards applied across heterogeneous quanta),
  resume-driven development (technology chosen for career capital over fit), vendor
  lock-in as evolvability debt (accumulated dependence on a vendor's roadmap), and
  treating fitness functions as a one-time setup rather than a living practice. Each
  undermines "guided" change in a distinct, recognizable way. ([lesson](lessons/08-pitfalls-antipatterns.md))
- **[09] Governing and building an evolutionary practice** - the highest-band lesson:
  governance should be fitness-function-driven, not document-driven, because
  document-driven governance doesn't scale past a handful of teams. Covers ownership
  (quantum-local fitness functions owned by the owning team; genuinely cross-cutting
  ones like security/compliance owned centrally), review cadence (preventing the
  one-time-setup antipattern), and the core org-scale trade-off of balancing governance
  rigor against team autonomy - scoped per quantum rather than applied uniformly.
  ([lesson](lessons/09-governance-practice.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on concepts rated
`shaky` or `not-yet`.
