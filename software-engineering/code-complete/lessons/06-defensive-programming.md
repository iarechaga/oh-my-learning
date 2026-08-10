---
id: code-complete/06
subject: code-complete
title: Defensive Programming
slug: defensive-programming
status: drafted
mastery:
seniority: mid
source: Code Complete, 2nd ed. (Steve McConnell), Chapter 8
prerequisites: [code-complete/05, pragmatic-programmer/09]
created: 2026-08-10
updated: 2026-08-10
---

# Defensive Programming

## TL;DR
Defensive programming means protecting a routine from invalid data regardless of where that invalid data came from — validating inputs at trust boundaries, using assertions for conditions that should be impossible, and deciding deliberately how to handle bad input (reject it, correct it, or propagate an error) rather than letting garbage silently flow through and corrupt state further downstream.

## The idea
Code doesn't just fail because of bugs in its own logic — it also fails because it receives data it wasn't designed to handle: a malformed API request, a corrupted file, a caller who violated a precondition (`pragmatic-programmer/09`), or a value that was valid when it was created but has since become stale or invalid. Defensive programming is the discipline of protecting your routine at its boundary, checking what actually arrives rather than assuming it matches what you expect, so that a problem originating elsewhere doesn't propagate silently into your routine's logic and corrupt further state downstream — directly echoing `pragmatic-programmer/08`'s point that the further a bug travels from its source before being noticed, the more expensive it is to diagnose.

Crucially, this chapter's defensive programming and `pragmatic-programmer/09`'s Design by Contract are complementary, not identical: DbC is about establishing an explicit, checkable contract between routines (a shared vocabulary of preconditions/postconditions/invariants); defensive programming is the broader practice of protecting a routine against violations of that contract (or against any other bad input) regardless of whether a formal contract exists, including cases where the "bad" input comes from a source you can't fully trust or control (user input, external services, corrupted persisted data).

## How it works

### Distinguish where a check belongs: boundary of the system vs. between trusted internal routines
McConnell draws a useful distinction: validate rigorously at the boundary where your system receives data from the outside world (user input, an external API, a file read from disk) — this data is genuinely untrusted and *must* be checked. Between routines *you control internally*, that have already validated their inputs once at the boundary, redundant re-validation everywhere is often unnecessary overhead — the goal is validating *once*, at the actual point where untrusted data enters, not defensively re-checking the same already-validated data at every internal hop (which would itself become its own kind of clutter, echoing `clean-code/07`'s "don't clutter the happy path" concern).

**Worked example.** An HTTP handler receives a JSON payload with a `discount_percentage` field. Validate rigorously here — is it present, numeric, within 0-100? Once validated, pass a properly-typed, already-checked `DiscountPercentage` value object (see `domain-modeling`) through the rest of the internal call chain — internal routines that receive this value object can trust it's valid by construction (the value object's constructor itself enforced the range), rather than each one separately re-checking "is this actually between 0 and 100" redundantly at every hop.

### Assertions for "this should be impossible" conditions
Directly extending `pragmatic-programmer/09`: use assertions for internal-consistency conditions that represent a bug in *your own* code if violated — not for expected, external bad input (that's validation's job, producing a graceful error, not a crash). McConnell's specific guidance sharpens the distinction: **assertions document and check assumptions about your own program's correctness; input validation protects against the outside world's unpredictability.** Conflating them — asserting on user input, or silently validating-and-ignoring what should be an impossible internal state — misapplies both tools.

### Three deliberate strategies for handling bad input
Echoing and extending `pragmatic-programmer/12`'s per-stage error-strategy framing, McConnell names specific tactics for what to do once invalid data is detected:
1. **Return a neutral value** — e.g., return an empty result rather than propagating an error, when the calling context can reasonably treat "no valid data" as an unremarkable case.
2. **Substitute the next valid piece of data / skip and continue** — appropriate in batch/stream processing where one bad record shouldn't halt processing of the rest (echoing `pragmatic-programmer/13`'s "collect all validation errors, don't crash on the first" pattern).
3. **Return an error code / raise an exception, and let the caller decide** — appropriate when the calling context is in a better position to decide the right recovery action than the routine detecting the problem.

Which strategy is right depends entirely on context — the chapter's point isn't "always do X," it's "deliberately pick one of these, for a stated reason, rather than defaulting to whichever happens to be easiest to code at the moment."

### Barricades: contain corruption instead of letting it spread
A specific architectural technique: designate certain modules/layers as "safe" zones that only ever receive pre-validated data, with a **barricade** — a validation layer — sitting between the safe zone and any untrusted input source. Everything inside the barricade can assume clean, validated data and use assertions freely for internal-consistency checks (since genuinely bad *external* data can no longer reach that far); everything outside the barricade must do full defensive validation, because that's precisely where untrusted data is still in play.

**Worked example.** A web application's controller layer is the barricade: it validates and sanitizes all incoming request data before it's allowed to reach the domain/service layer. Inside the domain layer, functions can assert on their inputs (`assert amount > 0`) as an internal-consistency check, confident that the barricade already rejected genuinely malformed input before it got this far — if an assertion fires inside the domain layer, that's now unambiguously a bug in the domain layer or the barricade itself, not a case of "the user typed something weird," which narrows the debugging search space significantly.

### Defensive programming and performance — know when to relax it
The chapter also acknowledges a genuine tension: exhaustive validation and assertions everywhere have real runtime cost, which matters in hot paths. The practical resolution (consistent with the barricade idea): validate thoroughly at trust boundaries where data genuinely could be wrong, and rely on assertions (which can often be stripped in optimized production builds, per `pragmatic-programmer/09`'s caution about not relying on their side effects) rather than full validation logic deep inside already-barricaded, performance-sensitive internal code.

## Pros
- Validating once at a genuine trust boundary, then trusting validated data internally, avoids both silent corruption *and* wasteful, redundant re-validation everywhere.
- The barricade concept gives a concrete, checkable architectural pattern for where "defensive" and "trusting" code should each live.
- Deliberately chosen bad-input-handling strategies (neutral value, skip-and-continue, propagate) produce more predictable, context-appropriate behavior than ad hoc, inconsistent handling scattered across a codebase.

## Cons
- Determining where the "trust boundary" actually is in a complex, multi-service system takes real architectural analysis — get it wrong (assume something is barricaded when it isn't) and defensive programming's core promise (contained corruption) silently fails.
- Over-applying full defensive validation everywhere, ignoring the barricade idea, adds real performance and readability overhead without a corresponding safety benefit.
- Choosing the wrong bad-input strategy (e.g., silently substituting a neutral value when the caller actually needed to know about the failure) can hide real problems just as effectively as no defensive programming at all — this chapter's tactics are not automatically safe merely because they're "defensive."

## Alternatives
- **Type systems enforcing validity by construction** (smart constructors, value objects that can't be instantiated in an invalid state) — push some of defensive programming's runtime-check burden into the type system, catching a subset of invalid-state problems at compile time instead of at runtime.
- **Schema validation at system boundaries** (JSON Schema, protobuf-defined contracts) — formalize and automate the "validate rigorously at the boundary" half of this lesson, reducing reliance on hand-written validation code for that specific concern.
- **Fail-fast, crash-everywhere philosophies** (some functional/Erlang-style "let it crash" systems) — deliberately choose *not* to defensively handle many error conditions at all, relying instead on process-level supervision and restart to recover, a very different philosophy appropriate in specific fault-tolerant architectural contexts (see `architecture/distributed-systems`).

## When to use it
Apply rigorous validation at every genuine trust boundary (user input, external API responses, data read from files/queues you don't fully control) and reserve assertions for internal-consistency checks on data you've already validated once. Use the barricade concept explicitly when designing a system's layers, to decide where defensive checks are actually necessary versus redundant.

## When NOT to use it
Don't re-validate the same already-checked data at every internal call site inside a barricaded, trusted zone — that's redundant defensive overhead with no corresponding safety benefit, and it clutters the happy path (`clean-code/07`). Don't use assertions in place of real input validation for data that genuinely originates from an untrusted external source.

## Key takeaways / mental model
Ask, for any check you're about to add: "is this protecting against something a barricade upstream should already have caught, or is this genuinely the first point this specific data is being checked?" Validate thoroughly and deliberately at the latter; trust and simplify at the former, using assertions only to catch genuine internal bugs.

## Self-check questions
1. Identify the actual trust boundary in a system you've worked on. Is validation concentrated there, or scattered redundantly throughout the codebase?
2. Explain the difference between an assertion and input validation using this chapter's distinction, and give an example of each being misapplied (used where the other belonged).
3. Describe the barricade pattern in your own words, and give an example of a system where the barricade is missing or leaky.
4. Which of the three bad-input-handling strategies (neutral value, skip-and-continue, propagate) would you choose for a batch job importing 100,000 customer records with a handful of malformed rows, and why?

## References
- Code Complete, 2nd ed. (Steve McConnell), Chapter 8: "Defensive Programming".
- See also: `pragmatic-programmer/09` (Design by Contract and Assertive Programming) for the complementary contract-based framing.
