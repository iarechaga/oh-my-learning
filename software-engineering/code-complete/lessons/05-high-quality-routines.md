---
id: code-complete/05
subject: code-complete
title: High-Quality Routines
slug: high-quality-routines
status: drafted
mastery:
seniority: junior
source: Code Complete, 2nd ed. (Steve McConnell), Chapter 7
prerequisites: [clean-code/03]
created: 2026-08-10
updated: 2026-08-10
---

# High-Quality Routines

## TL;DR
A routine (function/method/procedure) earns "high quality" through several checkable, largely independent properties: a strong cohesive reason for existing, a good name, well-managed parameters, and clear documentation of what it does and doesn't guarantee — this chapter's contribution over `clean-code/03` is a more exhaustive, checklist-style treatment of exactly what makes a routine reliable to call without reading its source.

## The idea
`clean-code/03` argued functions should be small and do one thing. This chapter, from a different book with a slightly more exhaustive, checklist-oriented style, asks a related but distinct question: **given that a routine exists, what specifically makes it safe and pleasant for someone else to call, without reading its implementation first?** The answer is a cluster of concrete properties — a defensible reason to exist as a separate routine at all, good parameter design, a clear and honest name, and known behavior at its boundaries — each independently checkable, forming a practical quality checklist rather than one single design principle.

## How it works

### Valid reasons for a routine to exist
McConnell lists several legitimate reasons to factor logic into its own named routine, useful because "should this be its own function?" isn't always answered by "does it do one thing" alone:
- **Reduce complexity** — hide a chunk of logic behind a name so callers don't hold its details in mind (directly `code-complete/02`).
- **Avoid duplicate code** — the DRY motivation (`pragmatic-programmer/03`).
- **Support subclassing / polymorphism** — a routine exists specifically to be overridden.
- **Hide sequences/ordering** — encapsulate a multi-step sequence (initialize-then-configure-then-start) behind one call so callers can't accidentally get the order wrong.
- **Hide data structures** — expose behavior instead of a raw structure (echoing `clean-code/06`).
- **Improve portability/isolate volatile logic** — a routine that isolates platform-specific or likely-to-change code (echoing `code-complete/03`'s "identify what varies" heuristic).

Naming the specific reason clarifies whether extracting something into its own routine is actually justified, versus done reflexively without a real payoff.

### Parameter design — a checklist of its own
- **Order parameters consistently across related routines** — if several routines take `(user, options)`, don't have one take `(options, user)`; inconsistent ordering is a silent source of bugs (passing arguments in the wrong order, especially when types coincidentally match) and forces callers to double-check every call site instead of relying on a learned convention.
- **Use all parameters** — an unused parameter is a signal the routine's purpose has drifted, or that it was copy-pasted from another routine without full cleanup; either way, it's worth investigating rather than ignoring.
- **Limit the number of parameters** — echoing `clean-code/03`'s argument-count preference, with the same underlying rationale (fewer combinations to reason about and test).
- **Put status/error variables last** (in languages/conventions where output parameters are used) — a convention that helps a reader scan a call and immediately spot which parameter carries the pass/fail result, without hunting for it among the "real" inputs.

### Routine names should describe everything the routine does
This restates and sharpens `clean-code/02`'s naming discipline specifically for routines: if a routine's name is `calculateTotal()` but it also, as a side effect, writes to a log file and sends an analytics event, the name is incomplete — it describes only one of three things the routine actually does, and a caller relying on the name alone (reasonably, since that's the point of a good name) would have no way to know about the other two effects. McConnell's specific test: could you write an accurate, complete one-sentence description of the routine using only its name? If genuinely not, either the name needs to grow more honest, or (usually the better fix, per `clean-code/03`) the routine should be split so each piece's name can be complete and accurate on its own.

### How long should a routine be?
McConnell reviews empirical studies here (a point of interest for calibrating against `clean-code/03`'s more aggressive "4-6 lines" instinct): the evidence he cites doesn't support "shorter is always better" as an absolute law — routines up to roughly 100-200 lines have, in some studied codebases, shown no worse (sometimes better) defect rates than very short ones, provided the routine still does one cohesive thing. The chapter's actual conclusion is more nuanced than a specific number either way: **length by itself is a weak predictor of quality; cohesion and complexity (per `code-complete/02`) are the real drivers**, and a routine should be exactly as long as it needs to be to do its one job clearly — not artificially shortened to hit a line-count target, and not artificially padded either.

### Defensive coding at a routine's boundary
A high-quality routine explicitly validates its inputs at the boundary (echoing `pragmatic-programmer/09`'s preconditions) rather than silently trusting the caller, and documents (in a comment or, better, in a checkable type/contract) what it guarantees on return and what it does on invalid input — this is developed fully in `code-complete/06`, but it starts here as a property of what makes a routine "high quality" in the first place.

## Pros
- A checklist of concrete, independently-verifiable properties is easier to apply consistently (and to teach to newer engineers) than a single abstract principle like "do one thing."
- Consistent parameter ordering and complete, honest naming directly reduce the chance of call-site bugs and misunderstandings.
- The evidence-based, nuanced take on routine length prevents over-applying an arbitrary line-count rule at the expense of genuinely cohesive but somewhat longer routines.

## Cons
- A long checklist of properties, applied mechanically without understanding the underlying rationale (cognitive load, per `code-complete/02`) for each, can become box-ticking rather than genuine quality improvement.
- The "routines up to 100-200 lines aren't necessarily worse" finding is easy to misuse as license for genuinely poorly-factored, low-cohesion long functions that happen to not show up as "bad" in whatever narrow defect-rate study is being cited.
- Consistent parameter ordering across many routines requires ongoing team discipline and is easy to let drift, especially across a codebase with many contributors over time.

## Alternatives
- **Clean Code's more aggressive "4-6 lines" guidance** (`clean-code/03`) — a stricter, more opinionated stance on the same underlying concern; the tension between the two books' specific numeric guidance is itself a useful reminder that the *length* isn't the real target — cohesion and clarity are, and reasonable authors can disagree about how aggressively to optimize for brevity specifically.
- **Type systems / contracts enforcing parameter correctness** — rely on compiler-checked types (a distinct `UserId` type instead of a bare `int`) to catch argument-order mistakes mechanically, rather than relying purely on naming/ordering conventions and human vigilance.
- **Named/keyword arguments (where the language supports them)** — sidestep the "consistent ordering" concern somewhat by making call sites explicit about which value maps to which parameter, regardless of position.

## When to use it
Run through this chapter's checklist (valid reason to exist, honest complete name, consistent and minimal parameters, validated boundaries) whenever writing or reviewing a routine meant to be called by more than one place, or that will live long enough to be called by code you haven't written yet.

## When NOT to use it
Don't chase an arbitrary line-count target for its own sake — a routine's length should follow from doing one cohesive thing clearly, not from satisfying a specific number either book prescribes. Don't apply the full checklist ceremony to genuinely trivial, obviously-correct private helper routines with a single, immediately-visible caller.

## Key takeaways / mental model
For any routine, ask: "do I have a specific, nameable reason this exists as its own routine, does its name describe everything it actually does, and are its parameters ordered and minimal in a way a caller can trust without reading the source?" Length is a secondary concern — cohesion and honesty of the interface are the real quality signals.

## Self-check questions
1. Pick a routine from your own code and identify which of McConnell's "valid reasons for a routine to exist" applies to it. If none clearly apply, should it exist as a separate routine at all?
2. Find a routine whose name doesn't fully describe everything it does. Would you fix this by renaming it, or by splitting it? What determines which is the better fix?
3. Why does McConnell's evidence-based take on routine length complicate a simple "always keep functions under N lines" rule? What's the actual underlying driver of quality instead?
4. Give an example of inconsistent parameter ordering across related functions you've seen (or could imagine), and describe the bug risk it creates.

## References
- Code Complete, 2nd ed. (Steve McConnell), Chapter 7: "High-Quality Routines".
