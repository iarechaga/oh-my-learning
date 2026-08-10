---
id: refactoring/04
subject: refactoring
title: "Code Smells: A Catalog"
slug: code-smells
status: drafted
mastery:
seniority: mid
source: Refactoring, 2nd ed. (Martin Fowler), Chapter 3
prerequisites: [clean-code/12, refactoring/02]
created: 2026-08-10
updated: 2026-08-10
---

# Code Smells: A Catalog

## TL;DR
Fowler's smell catalog is the original source `clean-code/12` draws from, and its distinguishing feature is that nearly every smell is explicitly paired with one or more *named refactorings* that address it — turning "I notice this problem" directly into "here's the specific technique to fix it," which is this subject's whole organizing structure for the lessons that follow.

## The idea
`clean-code/12` already introduced code smells as fast, pattern-recognition-level signals worth noticing during ordinary reading. This lesson revisits the same underlying concept from its original source, with a specific emphasis this subject needs going forward: **each smell here is a doorway into a specific corner of the refactoring catalog** — recognizing "this is Duplicated Code" or "this is a Long Parameter List" isn't just a diagnosis, it's a pointer to exactly which named refactoring techniques (covered in `refactoring/05` through `refactoring/11`) are the standard, well-understood fix.

## How it works

### The smell-to-refactoring pairing, worked through several examples
- **Duplicated Code** -> Extract Function (pull the shared logic into one named place), or Pull Up Method (if the duplication is across sibling subclasses) — covered in `refactoring/05` and `refactoring/10`.
- **Long Function** -> Extract Function repeatedly, or Replace Temp with Query, or Decompose Conditional — covered in `refactoring/05` and `refactoring/08`.
- **Long Parameter List** -> Introduce Parameter Object (group related parameters into one object) or Replace Parameter with Query — covered in `refactoring/09`.
- **Divergent Change** (one module changes for many different, unrelated reasons — the inverse framing of `clean-code/10`'s cohesion argument) -> Split Phase or Extract Class, separating the unrelated reasons for change into their own modules.
- **Shotgun Surgery** (a single conceptual change requires touching many different modules — the opposite symptom from Divergent Change, but arising from the same underlying problem: a design decision scattered across modules, echoing `philosophy-of-software-design/01`'s change-amplification and `philosophy-of-software-design/04`'s leakage) -> Move Function/Move Field to consolidate the scattered pieces into one place — covered in `refactoring/06`.
- **Feature Envy** (a method that uses another object's data more than its own — see `clean-code/12`) -> Move Function, relocating the method to the class whose data it actually depends on — covered in `refactoring/06`.
- **Data Clumps** (the same small group of values — e.g., a street/city/postal-code trio — always travels together as separate parameters/fields, never formalized as its own concept) -> Extract Class or Introduce Parameter Object, giving the clump its own named type — covered in `refactoring/07` and `refactoring/09`.
- **Primitive Obsession** (using primitives — bare strings, ints — where a small dedicated value type would better capture domain constraints, echoing `code-complete/07`'s "most restrictive representation" guidance) -> Replace Primitive with Object — covered in `refactoring/07`.
- **Switch Statements repeated across the codebase** (echoing `clean-code/12`'s and `clean-code/06`'s type-checking smell) -> Replace Conditional with Polymorphism — covered in `refactoring/08`.
- **Comments used to explain confusing code** (directly `clean-code/04`'s point) -> Extract Function with a name that makes the comment unnecessary, per the "code should say what the comment was saying" principle both books share here.

### Why this pairing structure matters for how you'll use this subject
The rest of this subject is organized by *purpose* (composing methods, moving features, organizing data, and so on) rather than purely by smell — but the mental habit this chapter builds is what makes that catalog useful in practice: you don't refactor "in general," you notice a *specific smell*, which points you toward a *specific* refactoring technique appropriate for that specific problem, rather than reaching for a vague, undirected "let's improve this" impulse. Learning to recognize the smell is, in a real sense, learning the *index* to the rest of this subject's catalog.

### Smells often co-occur and compound
Just as `clean-code/12` noted, smells rarely appear in isolation — Divergent Change and Shotgun Surgery are, in a sense, two faces of the same underlying leakage problem (`philosophy-of-software-design/04`) viewed from opposite directions (one module doing too much vs. one decision scattered across too many modules); Data Clumps and Primitive Obsession often coexist (a clump of primitives that should have been both grouped *and* given a proper domain-specific type). Recognizing one smell is frequently the fastest way to notice you're standing in the middle of several related ones, all traceable to the same root design decision gone slightly wrong.

## Pros
- Directly pairs each smell with a specific, named, well-understood refactoring technique, converting a vague "this feels bad" into a concrete, actionable next step.
- Provides the organizing index for the rest of this subject's refactoring catalog, making the catalog navigable by symptom rather than requiring you to already know which technique you need.
- Reinforces and cross-links smells already introduced in `clean-code/12`, deepening understanding by connecting them to concrete fixes rather than leaving them as descriptive-only observations.

## Cons
- As with `clean-code/12`'s caution, a smell is a heuristic, not an automatic verdict — reflexively applying the paired refactoring to every instance of a smell, without checking whether it's genuinely appropriate in context, risks the exact over-application this whole subject's `refactoring/12` (on YAGNI and restraint) warns against.
- Some smells (Shotgun Surgery especially) require broader architectural judgment to fix well, not just a mechanical application of Move Function — the smell points you toward a category of fix, not a guaranteed, one-size-fits-all solution.
- Learning to reliably recognize the less obvious smells (Divergent Change, Data Clumps, Primitive Obsession) takes real repeated exposure across genuine codebases, more than a one-time reading of the catalog provides.

## Alternatives
- **Clean Code's smell catalog** (`clean-code/12`) — largely overlapping in content, less explicitly tied to named refactoring techniques for each smell, more oriented toward general code-quality judgment than this subject's specific fix-pairing structure.
- **Automated smell-detection tooling** — mechanically flags some smells (duplication, long functions, high complexity per `code-complete/11`) at scale, complementary to but not a full substitute for the judgment-dependent smells (Feature Envy, Divergent Change) tooling struggles to detect reliably.
- **Architecture-level smell catalogs** (see `architecture/hard-parts`, `architecture/evolutionary-architectures`) — a coarser-grained, system-level version of the same underlying idea, naming recurring *architectural* problems and their corresponding fixes, at a scale beyond this subject's class/function-level focus.

## When to use it
Apply smell-recognition continuously during ordinary reading and reviewing, and use a recognized smell as the trigger to look up and apply the specifically-paired refactoring technique from this subject's later lessons, rather than improvising an ad hoc fix.

## When NOT to use it
Don't mechanically apply a smell's paired refactoring without confirming the smell is genuinely a problem in its specific context — some smelly-looking code is appropriate for its narrow, stable, unlikely-to-change situation, echoing `clean-code/12`'s own caution against treating heuristics as laws.

## Key takeaways / mental model
When you notice a smell, don't just note "this is bad" — ask "which named refactoring, from this subject's catalog, is specifically paired with this smell?" That question is what turns pattern recognition into concrete, disciplined action.

## Self-check questions
1. Pick three smells from this catalog and, for each, name the specific refactoring technique paired with it and explain why that technique addresses the smell's underlying problem.
2. Explain the relationship between Divergent Change and Shotgun Surgery — how are they two faces of the same underlying issue?
3. Give an example from your own code of Data Clumps or Primitive Obsession, and describe what Extract Class or Replace Primitive with Object would look like applied to it.
4. Why is recognizing a smell only the first step, not the whole solution, according to this lesson?

## References
- Refactoring: Improving the Design of Existing Code, 2nd ed. (Martin Fowler), Chapter 3: "Bad Smells in Code".
- See also: `clean-code/12` (Code Smells and Heuristics) for the closely related, overlapping catalog this lesson builds on and re-anchors to specific refactoring techniques.
