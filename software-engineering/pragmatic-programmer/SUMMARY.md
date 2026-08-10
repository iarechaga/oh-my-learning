# The Pragmatic Programmer - Subject Summary

A comprehensive recap of *The Pragmatic Programmer* (20th Anniversary ed.), concept by
concept.

**Progress note:** all 15 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom
(dependency-ordered): philosophy first, then core techniques, then design, delivery,
and pragmatic projects.

## Philosophy

- **[pragmatic-programmer/01] The pragmatic philosophy and taking responsibility** -
  own the quality of your work; offer options instead of excuses; be a catalyst for
  change and a trusted advisor. ([lesson](lessons/01-pragmatic-philosophy.md))
- **[pragmatic-programmer/02] Software entropy and the broken-windows theory** -
  unaddressed small problems normalize more decay; fix it now or board it up
  (track it visibly) - never leave it silent and unmarked.
  ([lesson](lessons/02-software-entropy.md))

## Core techniques

- **[pragmatic-programmer/03] DRY and the evils of duplication** - DRY is about
  duplicated *knowledge*, not duplicated text; find the single source of truth for
  every fact the system depends on. ([lesson](lessons/03-dry-duplication.md))
- **[pragmatic-programmer/04] Orthogonality and decoupling** - a change to one module
  shouldn't ripple into unrelated modules; test orthogonality by asking how many files
  a small change touches. ([lesson](lessons/04-orthogonality.md))
- **[pragmatic-programmer/05] Reversibility and tracer bullets** - rank decisions by
  how expensive they'd be to undo, and design escape hatches for the expensive ones;
  use tracer bullets (real, thin, end-to-end slices) to surface unknowns early.
  ([lesson](lessons/05-reversibility-tracer-bullets.md))
- **[pragmatic-programmer/06] Prototyping and estimating** - prototype to learn one
  thing, then throw the code away; estimate by decomposing, stating assumptions, and
  giving ranges, and track your own calibration over time.
  ([lesson](lessons/06-prototyping-estimating.md))
- **[pragmatic-programmer/07] The power of plain text and the shell** - plain text
  outlives specific tools and is diffable, composable, and debuggable; shell fluency
  multiplies leverage over it. ([lesson](lessons/07-plain-text-shell.md))
- **[pragmatic-programmer/08] Debugging and rubber ducking** - debug scientifically:
  hypothesis, discriminating test, fix the cause not the symptom; explain problems out
  loud to surface hidden assumptions. ([lesson](lessons/08-debugging.md))

## Design

- **[pragmatic-programmer/09] Design by Contract and assertive programming** -
  preconditions/postconditions/invariants make it mechanically clear whose bug a
  failure is; assert liberally on internal assumptions, never on expected/recoverable
  conditions. ([lesson](lessons/09-design-by-contract.md))
- **[pragmatic-programmer/10] Decoupling: the Law of Demeter and configuration** -
  don't reach through an object's collaborators to their collaborators; ask the object
  the real question instead. Pull volatile business/environment values into
  configuration. ([lesson](lessons/10-decoupling-demeter.md))
- **[pragmatic-programmer/11] Concurrency and temporal coupling** - question every
  implicit "A then B" ordering before introducing concurrency; protect shared mutable
  state with narrow, explicit synchronization.
  ([lesson](lessons/11-concurrency-temporal-coupling.md))
- **[pragmatic-programmer/12] Transforming programming and error handling** - model
  code as a pipeline of transformations with clear input/output shapes; choose an
  error strategy (crash / no-result / bounded retry / propagate-with-context)
  deliberately per stage. ([lesson](lessons/12-transforming-programming.md))

## Delivery and pragmatic projects

- **[pragmatic-programmer/13] Pragmatic testing and property-based testing** - test
  ruthlessly at multiple granularities; every bug found becomes a permanent test;
  property-based testing generates inputs to find edge cases humans miss.
  ([lesson](lessons/13-pragmatic-testing.md))
- **[pragmatic-programmer/14] Requirements and the requirements pit** - users describe
  processes/workarounds, not underlying needs; dig for the policy behind the process
  and document concrete, falsifiable scenarios instead of abstract prose.
  ([lesson](lessons/14-requirements.md))
- **[pragmatic-programmer/15] Pragmatic teams and pride in your work** - individual
  habits only compound into real quality if the whole team shares them as norms;
  automate what must be reliable; build a culture where shipping subpar work feels
  genuinely uncomfortable. ([lesson](lessons/15-pragmatic-teams.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
