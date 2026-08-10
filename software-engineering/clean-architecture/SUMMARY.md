# Clean Architecture - Subject Summary

A comprehensive recap of *Clean Architecture: A Craftsman's Guide to Software
Structure and Design* (Robert C. Martin), concept by concept.

**Progress note:** all 13 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
paradigms and SOLID first, then component principles, then architecture boundaries and
the dependency rule.

## Paradigms and SOLID

- **[clean-architecture/01] What "good architecture" is for** - minimize the human
  effort to build and maintain a system; defer expensive-to-reverse decisions by
  keeping options open, echoing `pragmatic-programmer/05`.
  ([lesson](lessons/01-what-architecture-is-for.md))
- **[clean-architecture/02] The three paradigms** - structured programming removes
  undisciplined jumps; OO removes undisciplined function pointers, enabling safe
  polymorphism; functional removes assignment, eliminating races by construction.
  ([lesson](lessons/02-programming-paradigms.md))
- **[clean-architecture/03] SRP and OCP** - SRP is "one actor," not "one thing";
  OCP means adding behavior via new code, never modifying existing working code.
  ([lesson](lessons/03-srp-ocp.md))
- **[clean-architecture/04] LSP, ISP, and DIP** - substitutability protects OCP's
  polymorphism; don't force unused interface dependencies; invert the source-code
  dependency to point opposite the control flow. ([lesson](lessons/04-lsp-isp-dip.md))

## Component principles

- **[clean-architecture/05] Component cohesion (REP, CCP, CRP)** - release-together,
  change-together, and don't-force-unused-dependence pull in different directions;
  lean CCP early, CRP once reuse is evidenced. ([lesson](lessons/05-component-cohesion.md))
- **[clean-architecture/06] Component coupling (ADP, SDP, SAP)** - no dependency
  cycles; depend toward stability; a stable component should be stable because it's
  abstract, not merely untouchable. ([lesson](lessons/06-component-coupling.md))

## Business rules and the dependency rule

- **[clean-architecture/07] Business rules: entities and use cases** - Entities hold
  general rules that would matter with any app; Use Cases hold this specific app's
  orchestration; both stay framework-free. ([lesson](lessons/07-business-rules.md))
- **[clean-architecture/08] The dependency rule and clean-architecture layers** -
  source-code dependencies point only inward; control flow can still go outward via
  an inner-circle-owned interface. ([lesson](lessons/08-dependency-rule.md))
- **[clean-architecture/09] Boundaries and the humble object pattern** - not every
  boundary is worth its cost; where one side is inherently untestable (rendering,
  I/O), split out a humble wrapper and push logic into a tested class.
  ([lesson](lessons/09-boundaries-humble-object.md))
- **[clean-architecture/10] Policy, level, and the direction of dependencies** -
  level = distance from a system's inputs/outputs; higher-level policy should never
  depend on lower-level policy. ([lesson](lessons/10-policy-and-level.md))
- **[clean-architecture/11] The database and the web are details** - the data model
  is not the storage mechanism; the delivery mechanism is not the business purpose;
  both should stay swappable outer-circle details.
  ([lesson](lessons/11-details-database-web.md))
- **[clean-architecture/12] The main component and partial boundaries** - `Main` is
  the one place allowed to know every concrete detail; partial boundaries capture
  some future-proofing cheaply when a full boundary isn't yet justified.
  ([lesson](lessons/12-main-component-partial-boundaries.md))
- **[clean-architecture/13] Screaming architecture and test boundaries** - top-level
  structure should scream the business, not the framework; tests should depend on
  stable interfaces, not volatile internals. ([lesson](lessons/13-screaming-architecture.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
