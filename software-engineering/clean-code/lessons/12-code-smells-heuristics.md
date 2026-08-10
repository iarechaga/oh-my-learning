---
id: clean-code/12
subject: clean-code
title: Code Smells and Heuristics
slug: code-smells-heuristics
status: drafted
mastery:
seniority: senior
source: Clean Code (Robert C. Martin), Chapter 17
prerequisites: [clean-code/02, clean-code/03, clean-code/10]
created: 2026-08-10
updated: 2026-08-10
---

# Code Smells and Heuristics

## TL;DR
A code smell is a fast, pattern-recognition-level signal ("this looks like trouble") that something probably needs attention — not a proof of a defect, and not a mechanical rule to apply blindly. The value of learning a catalog of smells is developing the *instinct* to notice them quickly during everyday reading and reviewing, then using judgment (not the smell alone) to decide whether and how to act.

## The idea
Every principle covered earlier in this subject (naming, function size, cohesion, error handling, boundaries) implies a corresponding "smell": a symptom you can notice quickly, often before you've consciously articulated *which* principle it violates. This closing chapter compiles those symptoms into a reference catalog — not because memorizing a list is the goal, but because a trained eye that recognizes "duplicate code" or "large class" or "feature envy" at a glance, while just reading through a file for an unrelated reason, catches far more real problems than one that only checks for violations when explicitly asked to review for them.

Crucially, the book frames smells as *heuristics*, not laws: a smell is evidence worth investigating, not an automatic verdict. Some smelly-looking code is genuinely fine given its context (a short-lived script, a deliberately simple hardcoded value); some clean-looking code hides a real problem no smell catalog captures. Judgment sits above the checklist.

## How it works

### A representative sample of the catalog, organized by what they point back to
- **Duplicated code** — the most fundamental smell in the book's own ranking; directly the DRY violation from `pragmatic-programmer/03`. Every instance of near-identical logic is a candidate for extraction into one shared abstraction.
- **Long function / large class** — directly `clean-code/03`'s "small, one thing" and `clean-code/10`'s cohesion arguments, viewed as smells rather than principles: size alone isn't the problem, but size is often a visible proxy for "doing more than one thing."
- **Feature envy** — a method that uses another object's data/methods more than its own, a strong sign that the method (or the logic within it) actually belongs on the *other* class instead — directly related to the Law of Demeter (`pragmatic-programmer/10`) and to `clean-code/06`'s object/data-structure distinction.
- **Inappropriate intimacy** — two classes that reach deeply into each other's internals, coupling them far more tightly than their stated relationship suggests — an orthogonality violation (`pragmatic-programmer/04`) at the class-design level.
- **Comments as a deodorant** — a comment explaining confusing code is a smell that the code itself, not the comment, needs fixing — directly `clean-code/04`'s central argument, restated here as a smell to notice rather than a principle to apply.
- **Dead code** — code that's never executed (unreachable branches, unused functions) but still sits in the codebase, adding reading cost with zero functional benefit and, per `pragmatic-programmer/02`'s broken-windows logic, implicitly signaling that leaving unused things around is acceptable.
- **Speculative generality** — an abstraction (an interface, a configurable parameter, a plugin hook) built for a flexibility need that doesn't actually exist yet, only imagined — the "abstraction-itis" the `pragmatic-programmer/05` lesson on reversibility explicitly warned against, restated here as a smell to notice in review.
- **Switch statements / repeated conditional type-checking** scattered across many places — a smell suggesting a missing polymorphic design; connects to `clean-code/06`'s point that adding a new type under a data-structure style requires touching every conditional, and that this cost sometimes indicates the design should shift toward object/polymorphic style instead.

### The right way to use a smell: as a trigger for a question, not an answer
Detecting a smell should prompt a specific question, not an automatic action:
- Duplicated code -> "is this genuinely the same knowledge (per `pragmatic-programmer/03`'s knowledge-not-text framing), or coincidentally similar text?"
- A long function -> "does it genuinely do more than one nameable thing, or is it one thing that's just inherently a bit long (e.g., a big but flat switch/dispatch table)?"
- Feature envy -> "should this behavior actually move to the class whose data it's using, or is there a legitimate reason it lives here instead?"

Answering these questions requires understanding the underlying principle the smell points back to (which is why this chapter comes last in the book, and last in this subject's dependency order) — the smell alone only tells you *where to look*, not *what's actually wrong* or *what to do about it*.

### Smells compound — and interact with the broken-windows dynamic
A codebase riddled with multiple smells rarely has them independently: feature envy often coexists with inappropriate intimacy (the same underlying misplaced-responsibility problem, viewed from two angles); dead code and speculative generality often coexist (a flexibility mechanism built "just in case," whose case never arrived, quietly becoming both unused and a source of confusion). Recognizing one smell is often the fastest way to notice you're standing in the middle of several related ones — and, per `pragmatic-programmer/02`, an unaddressed cluster of smells signals "nobody's watching here" to the next person who touches this code, inviting more of the same.

## Pros
- A trained eye for smells catches real problems during ordinary reading, far more cheaply than a scheduled, deliberate quality audit.
- The catalog gives a team shared vocabulary ("this has feature envy," "this is speculative generality") that speeds up code review conversations, replacing vague "this feels off" with a specific, nameable concern.
- Because smells point back to underlying principles, learning the catalog reinforces and cross-links everything else in this subject rather than being a separate, isolated topic.

## Cons
- Treating smells as mechanical rules ("duplicated code always must be removed," "any function over 10 lines is too long") produces the exact dogmatic over-application this chapter explicitly warns against.
- A smell is a heuristic with real false positives — code that looks smelly can be genuinely appropriate for its specific, narrow context, and reflexively "fixing" it can introduce unnecessary abstraction or complexity.
- Building genuine pattern-recognition fluency with a smell catalog takes real repeated exposure across many real codebases — reading the list once doesn't produce the instinct the book is actually after.

## Alternatives
- **Static analysis / automated smell detection tools** — mechanically flag some smells (duplicated code blocks, function length, cyclomatic complexity) at scale, catching what's checkable automatically, but missing the more judgment-dependent smells (feature envy, speculative generality) that require understanding intent, not just structure.
- **Code review as the primary smell-detection mechanism** — relies on human reviewers noticing smells during review rather than during ordinary reading; effective but bottlenecked on reviewer attention and experience, and misses smells in code nobody happens to review carefully.
- **Refactoring's more formal, actionable catalog** (see `software-engineering/refactoring`) — Fowler's catalog pairs each smell with a specific, named, mechanical refactoring technique to address it, going a step further than this chapter's more descriptive "here's what to notice" treatment.

## When to use it
Apply smell-recognition continuously, during ordinary reading and reviewing — not just during scheduled refactoring sessions. Use a detected smell as the trigger to ask the underlying "is this actually a problem here, and why" question, referencing the specific principle (DRY, cohesion, Demeter, etc.) it points back to.

## When NOT to use it
Don't treat any single smell as automatically disqualifying without judgment — check whether the specific context (short lifespan, genuinely proven need for flexibility, a flat but cohesive long function) makes the "smelly" code actually appropriate before "fixing" it. Don't rely solely on a smell catalog for quality assurance in place of automated tooling that can catch the mechanically-checkable subset far more consistently and cheaply than manual review.

## Key takeaways / mental model
A smell is a fast pattern-match that says "look here," not a verdict that says "this is definitely wrong." Build the instinct to notice the catalog's items quickly during normal reading, then always follow up with the specific underlying question the smell points back to before deciding whether, and how, to act.

## Self-check questions
1. Pick three smells from the catalog above and, for each, state the specific underlying principle (from this subject or `pragmatic-programmer`) it connects back to.
2. Give an example of code that "smells" (e.g., looks like duplicated code, or a long function) but is actually appropriate for its context. What made it appropriate despite the smell?
3. Explain feature envy using a concrete example, and describe how you'd decide whether to move the behavior to the other class.
4. Why does the book place this chapter last, after all the individual principle-focused chapters, rather than first as a quick-reference cheat sheet?

## References
- Clean Code: A Handbook of Agile Software Craftsmanship (Robert C. Martin), Chapter 17: "Smells and Heuristics".
- See also: `software-engineering/refactoring` for Fowler's more formal smell-to-refactoring catalog.
