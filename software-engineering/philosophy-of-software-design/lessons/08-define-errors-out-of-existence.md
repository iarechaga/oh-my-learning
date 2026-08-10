---
id: philosophy-of-software-design/08
subject: philosophy-of-software-design
title: Define Errors (and Special Cases) Out of Existence
slug: define-errors-out-of-existence
status: drafted
mastery:
seniority: senior
source: A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 10
prerequisites: [philosophy-of-software-design/06, clean-code/07]
created: 2026-08-10
updated: 2026-08-10
---

# Define Errors (and Special Cases) Out of Existence

## TL;DR
Exception/error-handling code is disproportionately expensive to write, test, and maintain relative to how much of it typically exists — so before writing a `try`/`catch` or a special-case check, ask whether the interface or semantics could instead be redefined so the "error" condition simply doesn't need special handling at all. Sometimes the cheapest, most robust fix for an error path is to make the error impossible by construction, rather than to handle it well.

## The idea
`clean-code/07` treated error handling as something to structure cleanly once you've decided you need it. This chapter asks a prior, more radical question: **do you need it at all, or can the situation be redefined so it isn't an error in the first place?** Ousterhout's empirical claim, echoing this subject's broader complexity framework (`philosophy-of-software-design/01`): exception-handling code is one of the largest sources of complexity in real systems, disproportionate to its actual line count, because each exception path represents an additional, separately-reasoned-about branch of behavior that's exercised rarely (making it hard to test thoroughly, per `pragmatic-programmer/13`'s point about under-tested error paths) and that every caller and every future maintainer must nonetheless account for.

## How it works

### The core technique: redefine the semantics so the special case vanishes
Rather than asking "how do I handle this error well," ask "can I change what this operation *means* so that this input or condition is simply not an error anymore?"

**Worked example — the book's own touchstone: deleting a range in a text editor.** Consider a `deleteRange(start, end)` operation on a document, and the edge case where `start == end` (an empty range) or where the range partially extends past the document's actual content:
- **Handling the error explicitly**: check for the empty-range case and raise `InvalidRangeError`, forcing every caller to catch or pre-validate before calling. Check for the out-of-bounds case and raise a different error, forcing more caller-side handling.
- **Defining the error out of existence**: define `deleteRange(start, end)` to simply delete whatever *actually exists* within the given bounds, clamped to the document's real extent, and to be a no-op (not an error) when the effective range is empty. Now every call to `deleteRange` — with a valid range, an empty range, or a range partially outside the document — succeeds uniformly, with no special-case branch anywhere, and no caller ever needs to pre-check or catch anything for these situations.

This is a genuinely different design decision, not just cleaner error-handling *code* for the same semantics — the operation's actual contract changed to make the "error" case a normal, valid, well-defined input instead of an exceptional one.

### A second worked example: file deletion
Deleting a file that doesn't exist is a classic case where two different systems make opposite choices, illustrating the trade-off directly:
- **Unix's `rm`** on a nonexistent file returns an error ("no such file or directory") — treating "delete something that isn't there" as an error condition every caller must handle.
- **An idempotent "ensure absent" semantics** instead defines "delete" as "ensure this file does not exist" — succeeding whether the file existed beforehand or not, with the same end state either way. Many modern APIs and infrastructure-as-code tools (deliberately) choose this framing specifically because it eliminates an entire class of caller-side "check if it exists first, then delete, and handle the race condition where it disappeared between my check and my delete" complexity (echoing `pragmatic-programmer/11`'s temporal-coupling concerns) — the redefinition doesn't just simplify the code, it removes an entire TOCTOU (time-of-check to time-of-use) race-condition risk class along with it.

### When this technique doesn't apply — genuine errors still need genuine handling
The chapter is explicit that not every error can or should be defined away — a payment that genuinely fails due to insufficient funds is a real, meaningful error that callers genuinely need to know about and react to differently than success; redefining it away (e.g., silently treating a failed charge as "successfully charged $0") would hide information callers need, which is precisely the caution `code-complete/06`'s defensive-programming lesson and `clean-code/07`'s "don't return null to hide a real absence" both raise from a different angle. The technique applies specifically to cases where the "error" is really just an **edge case of otherwise-normal behavior** (an empty range, a nonexistent file to delete) rather than a **genuinely exceptional, meaningfully-different outcome** the caller needs to distinguish and react to.

### The test for whether a redefinition is legitimate, versus hiding a real problem
A practical discriminating question: after the redefinition, does any caller ever *need* to know whether the special case occurred, in order to make a different decision? If truly no caller needs that distinction (deleting an already-deleted file: no caller cares whether it existed before, only that it's gone now), redefining the error away is a legitimate simplification. If some caller genuinely does need to know (a payment failure: the caller absolutely needs to know it failed, to avoid, say, shipping a physical product without having actually been paid), the "error" is real and must be surfaced, not defined away.

## Pros
- Eliminates entire classes of error-handling code (and the testing burden that comes with it) by removing the special case from existence, rather than merely handling it more cleanly.
- Often removes subtler, harder-to-spot risks alongside the obvious code simplification — the file-deletion example's TOCTOU race is a good instance of a bonus benefit beyond just "less code."
- Produces interfaces that are easier to use correctly, since callers no longer need to pre-check conditions or wrap calls in error handling for situations that are no longer errors at all.

## Cons
- Misapplied, this technique can silently hide genuinely important information from callers who actually needed to know a special case occurred — a serious correctness risk if judged wrong.
- Redefining an operation's semantics is a real design decision with its own trade-offs and possible surprises for callers used to the "error" framing (e.g., a caller who expects `rm` to fail loudly on a typo'd filename might be surprised by silent success under an "ensure absent" redefinition) — documentation and clear naming become more important, not less, once semantics are changed this way.
- Not every error condition has a clean redefinition available — some are genuinely, irreducibly exceptional, and forcing a redefinition where none naturally exists can produce awkward, unintuitive semantics.

## Alternatives
- **Comprehensive, well-structured exception handling** (`clean-code/07`) — the right tool for errors that are genuinely meaningful and must be surfaced to callers, rather than defined away; complementary to this chapter's technique, not competing with it, since the two apply to different categories of situation.
- **Defensive validation with graceful degradation** (`code-complete/06`) — handling an invalid input by substituting a sensible default or a neutral value, a related but distinct technique from redefining the operation's actual semantics so the input is no longer invalid at all.
- **Total/partial function distinctions** (a functional-programming framing) — some functional languages and libraries formalize "this operation is defined for all inputs" (total) versus "this operation may fail for some inputs" (partial) as a type-level distinction, offering a more structured way to reason about which operations are good candidates for this chapter's technique.

## When to use it
Apply this technique whenever you're about to write error-handling code for a condition that, on reflection, no caller actually needs to distinguish from the normal case — ask whether redefining the operation's semantics (make it idempotent, clamp/normalize inputs, treat "already in the target state" as success) removes the special case cleanly.

## When NOT to use it
Don't redefine away an error condition that carries information a caller genuinely needs to make a different decision — that's hiding a real problem, not simplifying a fake one. Be especially cautious redefining operations whose current, error-raising behavior callers may already depend on (changing established semantics can itself be a breaking change, echoing `pragmatic-programmer/05`'s reversibility concerns).

## Key takeaways / mental model
Before writing error-handling code for a special case, ask: "does any caller actually need to know this special case happened, to make a different decision?" If not, look for a redefinition of the operation's semantics that makes the special case a normal, well-defined outcome instead — that's usually cheaper and more robust than handling the error well.

## Self-check questions
1. Using the `deleteRange` example, explain precisely what semantic change eliminated the need for error handling, and confirm no caller genuinely needed to distinguish the special case.
2. Contrast Unix `rm`'s error-on-missing-file behavior with an "ensure absent" idempotent redefinition. What race condition does the redefinition eliminate, beyond just simplifying caller code?
3. Give an example of an error that should NOT be defined out of existence, and explain what information a caller would lose if it were.
4. Describe a special case in your own code that currently requires explicit handling. Could it be redefined away? What would the new semantics need to guarantee for that redefinition to be safe?

## References
- A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 10: "Define Errors Out Of Existence".
