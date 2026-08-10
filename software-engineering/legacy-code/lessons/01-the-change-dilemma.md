---
id: legacy-code/01
subject: legacy-code
title: "What Legacy Code Is: The Change Dilemma"
slug: the-change-dilemma
status: drafted
mastery:
seniority: mid
source: Working Effectively with Legacy Code (Michael C. Feathers), Chapter 1
prerequisites: [refactoring/03]
created: 2026-08-10
updated: 2026-08-10
---

# What Legacy Code Is: The Change Dilemma

## TL;DR
Feathers defines "legacy code" precisely as *code without tests* — not old code, not badly-written code, not code you personally dislike. This definition matters because it names the exact, specific problem this whole subject solves: you can't safely refactor (`refactoring/03`'s core requirement) without a safety net, and legacy code, by this definition, is exactly the code that doesn't have one yet.

## The idea
"Legacy code" is used loosely in casual conversation to mean roughly "old code," "code I don't like," or "code someone else wrote." Feathers deliberately rejects all of these informal meanings in favor of one precise, actionable definition: **code without tests.** This precision matters enormously for what follows in this subject, because it identifies the *exact* property that makes safe change hard, independent of the code's age, style, or authorship — brand-new code written yesterday with zero tests is, by this definition, already legacy code, with exactly the same change-dilemma this subject addresses; elegant, well-organized, decades-old code with a comprehensive test suite is not.

**The change dilemma, precisely:** to change code safely, you generally want tests verifying it still behaves correctly after the change (echoing `refactoring/03`'s safety-net argument). But to *get* those tests in place, you often need to change the code first — to make it testable at all (breaking a hard dependency on a database, a network call, a global singleton, per `design-patterns/05`'s Singleton-testability critique). This is the dilemma the book's title names: **you need to change it to test it, and you need to test it to change it safely** — a genuine chicken-and-egg problem that this subject's techniques (seams, characterization tests, dependency-breaking) exist specifically to resolve.

## How it works

### Why "code without tests" is the right definition, not "old code" or "bad code"
- **Age is neither necessary nor sufficient.** A ten-year-old, well-tested codebase is easy to change safely, by this book's definition, despite its age — it's not "legacy" in the sense that matters. A brand-new module built last week with zero tests is exactly as risky to change as any decades-old untested system, because the *actual* risk factor (no automated way to verify behavior is preserved) is identical.
- **Subjective code quality is neither necessary nor sufficient.** Code you find ugly or poorly organized, but which has thorough tests, is still safely changeable — you can refactor it toward better structure with confidence, verified at each step (`refactoring/01`). Code that looks clean and well-organized but has zero tests is still risky to change, because "looks clean" and "is verified to behave correctly" are entirely different properties, and only the second one actually protects you from silently breaking something.

### The specific risk untested code poses, precisely named
Without tests, changing code means you're relying entirely on manual inspection, manual testing, or simply hoping nothing breaks — for anything beyond the most trivial change, this doesn't scale, and it fails silently: a broken assumption or an overlooked edge case doesn't announce itself, it just ships, and you find out later, in production, at a much higher cost than an immediate test failure would have imposed (directly echoing `pragmatic-programmer/08`'s "the further a bug travels from its source, the more expensive it is" point). This is the concrete cost the change dilemma imposes, and it's why the book treats getting a safety net in place as a genuinely urgent, foundational priority — not a nice-to-have that can be indefinitely deferred.

### Resolving the dilemma: seams, not a full rewrite
The chicken-and-egg problem (need tests to change safely, need to change to add tests) isn't actually unsolvable — it just requires a more careful, more surgical approach than either "write tests for the whole system before touching anything" (often impractical for a large legacy system) or "just change it carefully and hope" (unsafe). The book's resolution, developed fully in `legacy-code/02`, is to find **seams** — specific points where behavior can be altered without editing the code in that exact spot — which let you insert *just enough* test coverage around the *specific* piece of code you actually need to change, without needing to make the entire system testable first. This is the key insight that makes the dilemma tractable: you don't need comprehensive tests for the whole system, you need a targeted safety net for the specific area you're about to touch.

### The dilemma matters most at the moment of a first, real change request
It's worth being explicit about *when* this dilemma actually bites: not while code sits untouched (an untested module that's never modified poses no immediate risk, echoing `refactoring/02`'s "don't refactor code you're not touching" guidance) — the dilemma becomes concrete and urgent the moment a real business requirement demands a change to that specific, untested code. This reframes the whole subject's techniques as targeted, on-demand tools you reach for exactly when you need to safely change something untested — not a general, unbounded mandate to retroactively test an entire legacy system before doing anything else.

## Pros
- A precise, behavior-based definition ("code without tests") gives an actionable, checkable criterion for identifying exactly which code needs this subject's techniques, rather than relying on a vague, subjective "this feels legacy" judgment.
- Naming the change dilemma explicitly clarifies why "just be careful" isn't an adequate substitute for tests, and why "just add tests everywhere first" isn't always practical either — setting up the rest of the subject's more surgical, targeted approach.
- Framing legacy status as independent of age or subjective quality prevents wasted effort "modernizing" well-tested old code that doesn't actually need this subject's specific interventions, while correctly flagging brand-new untested code as an equally real risk.

## Cons
- The precise definition, while useful, can feel counterintuitive at first if you're used to "legacy" meaning "old" — communicating this reframing to non-technical stakeholders (who may use "legacy" to mean something different) takes some deliberate effort.
- Identifying that code is "legacy" by this definition doesn't, on its own, tell you *how* to resolve the change dilemma for a specific piece of code — that requires the seam-finding and dependency-breaking techniques covered in the rest of this subject.
- The definition doesn't distinguish between code that's untested but simple and low-risk (where the dilemma barely matters in practice) and code that's untested and genuinely complex/critical (where it matters enormously) — some judgment about actual risk is still needed on top of the binary "tested or not" criterion.

## Alternatives
- **"Legacy code" as any code predating the current team/technology stack** — the more common, informal usage this chapter deliberately rejects; useful for organizational/staffing conversations, but not useful for deciding which specific techniques a piece of code actually needs.
- **Technical-debt scoring systems** — attempt to quantify code quality/risk along multiple dimensions (complexity, duplication, test coverage) rather than Feathers' single, binary tests-or-not criterion; more nuanced, but also more complex to apply consistently.
- **Age- or ownership-based legacy classification** (e.g., "anything not touched by the current team in the last year") — a pragmatic, organizationally-convenient proxy some teams use, though it can both over- and under-count relative to Feathers' precise, behavior-focused definition.

## When to use it
Apply Feathers' definition whenever deciding whether a piece of code needs this subject's specific techniques before you can change it safely: if it lacks tests and you need to modify it, you're facing the change dilemma, regardless of the code's age or how well-written it otherwise looks.

## When NOT to use it
Don't apply this subject's full toolkit preemptively to untested code you have no current need to change — per `refactoring/02`'s "don't refactor code you're not touching," resolving the change dilemma is worth the effort specifically when you're about to make a real change, not as a standing, unbounded obligation to retroactively test everything.

## Key takeaways / mental model
Whenever you're about to change a piece of code, ask one specific, binary question: "does this have tests verifying its current behavior?" If not, you're facing the change dilemma by Feathers' precise definition — regardless of the code's age, elegance, or reputation — and the rest of this subject's techniques (seams, characterization tests, dependency-breaking) are the tools for resolving it safely.

## Self-check questions
1. Explain, in your own words, why Feathers rejects "old code" as the definition of legacy code, using a concrete example of new-but-untested code and old-but-well-tested code.
2. What is the change dilemma, precisely, and why can't it be resolved simply by "writing tests first, then changing the code"?
3. Why does the book argue this dilemma is most acute specifically at the moment of a real change request, rather than for untouched code sitting idle?
4. Describe a piece of code you've worked with that fits Feathers' precise definition of legacy code, regardless of its age or how well-organized it looked.

## References
- Working Effectively with Legacy Code (Michael C. Feathers), Chapter 1: "Changing Software".
