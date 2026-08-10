# Working Effectively with Legacy Code - Subject Summary

A comprehensive recap of *Working Effectively with Legacy Code* (Michael C. Feathers),
concept by concept.

**Progress note:** all 12 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom: the
mental model and seams first, then dependency-breaking and characterization, then the
recurring "I need to change X but..." scenarios.

## The mental model and seams

- **[legacy-code/01] What legacy code is: the change dilemma** - legacy code =
  code without tests, precisely, independent of age or style; the chicken-and-egg
  problem of needing tests to change safely and needing to change to add tests.
  ([lesson](lessons/01-the-change-dilemma.md))
- **[legacy-code/02] Seams and enabling points** - a seam is a place to alter behavior
  without editing the code there; object seams (via constructor/parameter injection)
  are the most useful and most common in OO code.
  ([lesson](lessons/02-seams.md))
- **[legacy-code/03] Characterization tests** - lock in what code actually does, not
  what it should do, discovered by running it and observing real output; bugs get
  captured too, deliberately, for now. ([lesson](lessons/03-characterization-tests.md))

## Dependency-breaking

- **[legacy-code/04] Sensing and separation** - two distinct reasons to substitute a
  dependency: making an invisible value observable (sensing) vs. isolating from a
  costly/unreliable real dependency (separation). ([lesson](lessons/04-sensing-and-separation.md))
- **[legacy-code/05] Breaking dependencies (the toolkit)** - Parameterize Constructor
  (with a safe default), Extract Interface, and Subclass and Override as the core,
  low-risk techniques for creating a seam where none exists.
  ([lesson](lessons/05-breaking-dependencies.md))

## Recurring "I need to..." scenarios

- **[legacy-code/06] It takes forever to make a change** - diagnose whether the real
  bottleneck is comprehension, structural change amplification, or lack of a safety
  net - each needs a different, targeted fix. ([lesson](lessons/06-slow-to-change.md))
- **[legacy-code/07] Adding a feature to untested code** - the disciplined sequence:
  find the point of change, characterize existing behavior, write a failing test for
  the feature, implement minimally, refactor only afterward.
  ([lesson](lessons/07-adding-a-feature.md))
- **[legacy-code/08] I can't get this class into a test harness** - four specific
  reasons (constructor side effects, hard-to-construct parameters, side-effect-
  triggering construction, global/singleton dependencies), each with its matched fix.
  ([lesson](lessons/08-class-into-harness.md))
- **[legacy-code/09] I can't run a method in a test harness** - visibility, complex
  setup preconditions, and hidden resource dependencies each need Extract Method or a
  test-specific factory/seam, not reflexively making things public.
  ([lesson](lessons/09-method-into-harness.md))
- **[legacy-code/10] Finding what and where to change** - reasoning forward (what does
  this affect?) and backward (what produces this?) from a specific point, using search
  tools deliberately, instead of reading linearly.
  ([lesson](lessons/10-finding-where-to-change.md))
- **[legacy-code/11] Dependency-breaking techniques catalog** - Extract and Override
  Call/Factory Method/Getter for one buried dependency; Replace Global Reference with
  Getter and Introduce Static Setter for singleton-heavy code.
  ([lesson](lessons/11-techniques-catalog.md))
- **[legacy-code/12] Working with big, tangled methods** - sketch structure first,
  characterize the whole method coarsely, then extract and verify one section at a
  time, starting with the least-entangled piece.
  ([lesson](lessons/12-big-tangled-methods.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
