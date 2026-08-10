# Clean Code - Subject Summary

A comprehensive recap of *Clean Code: A Handbook of Agile Software Craftsmanship*,
concept by concept.

**Progress note:** all 12 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom: what
clean code is, then the building blocks (names, functions, comments, formatting), then
structure, error handling, boundaries, tests, classes, systems, and smells.

## Foundations

- **[clean-code/01] What clean code is and why it matters** - working code and clean
  code aren't the same; the 10:1 read-to-write ratio makes readability the dominant
  cost. Avoid the "wading through mud" trajectory.
  ([lesson](lessons/01-what-clean-code-is.md))

## Building blocks

- **[clean-code/02] Meaningful names** - names should reveal intent without needing a
  comment; avoid disinformation, noise words, and encodings; match name length to
  scope. ([lesson](lessons/02-meaningful-names.md))
- **[clean-code/03] Functions: small, one thing, one level** - small functions, one
  abstraction level each, few arguments, no hidden side effects, no flag arguments; the
  Stepdown Rule for reading top to bottom. ([lesson](lessons/03-functions.md))
- **[clean-code/04] Comments: good, bad, and unnecessary** - a comment is an admission
  the code didn't say enough; prefer fixing the code (name, extraction) over
  compensating with a comment; comments rot, code doesn't.
  ([lesson](lessons/04-comments.md))
- **[clean-code/05] Formatting and vertical/horizontal ordering** - vertical distance
  signals relatedness; horizontal spacing signals precedence; automate the convention
  with a formatter so the team never debates it. ([lesson](lessons/05-formatting.md))

## Structure and boundaries

- **[clean-code/06] Objects and data structures** - objects hide data behind behavior
  (easy to add types, hard to add operations); data structures expose data with no
  behavior (opposite trade-off); never build a hybrid by accident.
  ([lesson](lessons/06-objects-and-data-structures.md))
- **[clean-code/07] Error handling without clutter** - separate error handling from the
  happy path; prefer exceptions with real context over silently-ignorable error codes;
  never return or pass null. ([lesson](lessons/07-error-handling.md))
- **[clean-code/08] Boundaries and third-party code** - wrap third-party APIs behind a
  narrow interface sized to your needs; use learning tests to both understand a library
  and detect breaking changes on upgrade. ([lesson](lessons/08-boundaries.md))

## Tests, classes, and systems

- **[clean-code/09] Clean tests and the F.I.R.S.T. rules** - dirty tests are worse than
  no tests; one concept per test, Build-Operate-Check structure, and Fast/Independent/
  Repeatable/Self-validating/Timely. ([lesson](lessons/09-clean-tests.md))
- **[clean-code/10] Classes: cohesion and SRP in the small** - a class should have one
  reason to change; low cohesion (methods that don't share fields) signals a class
  bundling multiple responsibilities. ([lesson](lessons/10-classes.md))
- **[clean-code/11] Systems and separating construction from use** - don't let a class
  both construct and use its collaborators; push construction to a composition root or
  factory via dependency injection. ([lesson](lessons/11-systems.md))
- **[clean-code/12] Code smells and heuristics** - a curated catalog of fast,
  pattern-recognition signals (duplication, feature envy, speculative generality, ...)
  that point back to this subject's underlying principles; heuristics, not laws.
  ([lesson](lessons/12-code-smells-heuristics.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
