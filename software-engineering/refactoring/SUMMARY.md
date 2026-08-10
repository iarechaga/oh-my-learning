# Refactoring - Subject Summary

A comprehensive recap of *Refactoring: Improving the Design of Existing Code*, 2nd ed.
(Martin Fowler), concept by concept.

**Progress note:** all 12 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
principles and the safety net first, then smells, then the refactoring catalog grouped
by purpose.

## Principles and the safety net

- **[refactoring/01] What refactoring is (and is not)** - restructuring without changing
  observable behavior, in small individually-verified steps; not a rewrite, not mixed
  with feature work (the "two hats"). ([lesson](lessons/01-what-refactoring-is.md))
- **[refactoring/02] Why refactor, and when** - "make the change easy, then make the
  easy change"; the Rule of Three; opportunistic, boy-scout-rule refactoring over
  dedicated cleanup sprints. ([lesson](lessons/02-why-and-when.md))
- **[refactoring/03] Tests as the safety net** - refactoring's behavior-preservation
  promise is only verifiable with fast tests that check behavior, not implementation;
  characterization tests when none exist yet. ([lesson](lessons/03-tests-safety-net.md))
- **[refactoring/04] Code smells: a catalog** - Fowler's original smell catalog, each
  paired with the specific named refactoring that fixes it - the index to the rest of
  this subject. ([lesson](lessons/04-code-smells.md))

## The refactoring catalog, by purpose

- **[refactoring/05] Composing methods (extract/inline)** - Extract Function is the
  most fundamental refactoring; Inline Function is its precise inverse for
  interfaces that no longer earn their keep. ([lesson](lessons/05-composing-methods.md))
- **[refactoring/06] Moving features between objects** - Move Function/Field fix
  Feature Envy and Shotgun Surgery; Extract/Inline Class adjust class granularity.
  ([lesson](lessons/06-moving-features.md))
- **[refactoring/07] Organizing data** - Encapsulate Variable protects a seam;
  Replace Primitive with Object gives bare values domain constraints; Change
  Value/Reference decides shared identity. ([lesson](lessons/07-organizing-data.md))
- **[refactoring/08] Simplifying conditional logic** - Decompose Conditional names
  confusing logic; guard clauses flatten nesting; Replace Conditional with
  Polymorphism fixes repeated type-switches. ([lesson](lessons/08-simplifying-conditionals.md))
- **[refactoring/09] Refactoring APIs and parameters** - safe signature migration via
  an intermediate step; Introduce Parameter Object for Data Clumps; Remove Flag
  Argument. ([lesson](lessons/09-refactoring-apis.md))
- **[refactoring/10] Dealing with inheritance** - Pull Up/Push Down Method/Field fix
  sibling duplication and misplaced members; Replace Superclass with Delegate migrates
  away from a fragile-base-class relationship. ([lesson](lessons/10-inheritance.md))

## Scaling up, and the bigger picture

- **[refactoring/11] Big refactorings and breaking dependencies** - the same
  small-steps discipline sustained over a long migration; branch by abstraction and
  parallel change (expand-contract) instead of a long-lived branch.
  ([lesson](lessons/11-big-refactorings.md))
- **[refactoring/12] Refactoring, architecture, and YAGNI** - refactoring reduces the
  relative cost of an architectural decision being wrong later, which is what makes
  YAGNI a rational bet rather than recklessness.
  ([lesson](lessons/12-refactoring-architecture-yagni.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
