# Code Complete - Subject Summary

A comprehensive recap of *Code Complete*, 2nd ed. (Steve McConnell), concept by
concept.

**Progress note:** all 14 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
foundational metaphors and design first, then variables and routines, then defensive
construction and quality.

## Foundations and design

- **[code-complete/01] Software construction and metaphors** - your implicit metaphor
  for "what building software is like" shapes your process; scale planning rigor to a
  project's actual stakes (doghouse vs. skyscraper).
  ([lesson](lessons/01-construction-metaphors.md))
- **[code-complete/02] Managing complexity as the core problem** - human working memory
  is small and fixed; nearly every construction practice exists to reduce what a reader
  must hold in mind at once. ([lesson](lessons/02-managing-complexity.md))
- **[code-complete/03] Design in construction (heuristics)** - design is iterative, not
  algorithmic; find real-world objects, identify what varies and encapsulate it, always
  sketch a second candidate design. ([lesson](lessons/03-design-in-construction.md))
- **[code-complete/04] Working classes: cohesion and abstraction** - McConnell's
  cohesion taxonomy (functional > sequential > communicational) and the Abstract Data
  Type test: could the implementation be swapped with no caller noticing?
  ([lesson](lessons/04-working-classes.md))

## Routines, variables, and naming

- **[code-complete/05] High-quality routines** - a checklist for routine quality: a
  defensible reason to exist, consistent minimal parameters, an honest complete name;
  length is a weak quality predictor on its own.
  ([lesson](lessons/05-high-quality-routines.md))
- **[code-complete/06] Defensive programming** - validate rigorously at real trust
  boundaries, trust validated data internally (the barricade pattern), and choose a
  deliberate bad-input strategy. ([lesson](lessons/06-defensive-programming.md))
- **[code-complete/07] Using variables and data effectively** - minimize scope and
  span, one variable one purpose, prefer the most restrictive representation that fits.
  ([lesson](lessons/07-variables-and-data.md))
- **[code-complete/08] Naming variables well** - booleans should read as yes/no
  questions, loop variables need real names once loops grow, and team-wide naming
  consistency matters as much as individual name quality.
  ([lesson](lessons/08-naming-variables.md))

## Control flow and complexity

- **[code-complete/09] Organizing straight-line code and conditionals** - order
  statements to match true dependencies; put the common case first; avoid double
  negatives. ([lesson](lessons/09-organizing-code-conditionals.md))
- **[code-complete/10] Controlling loops and unusual control structures** - keep loop
  bodies small enough to see whole; minimize and surface exit conditions; `goto` is
  rarely but occasionally still the clearest option.
  ([lesson](lessons/10-loops-control-structures.md))
- **[code-complete/11] Taming deep nesting and complexity metrics** - cyclomatic
  complexity gives the "how much must I hold in mind" intuition a computable, testable
  number. ([lesson](lessons/11-taming-complexity.md))

## Quality practices at construction time

- **[code-complete/12] Collaborative construction and code reviews** - human review
  catches a class of shared-blind-spot and design defects testing structurally cannot;
  formal inspections through lightweight PR review are a spectrum.
  ([lesson](lessons/12-collaborative-construction.md))
- **[code-complete/13] Developer testing** - use your structural knowledge of the code
  to target boundaries and independent paths (informed by cyclomatic complexity);
  doesn't replace independent review. ([lesson](lessons/13-developer-testing.md))
- **[code-complete/14] Refactoring and code-tuning strategies** - refactoring
  (structure, same behavior) and tuning (speed, possibly worse structure) are different
  goals; measure before and after tuning, never mix the two in one change.
  ([lesson](lessons/14-refactoring-code-tuning.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
