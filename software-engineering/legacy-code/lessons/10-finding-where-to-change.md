---
id: legacy-code/10
subject: legacy-code
title: Finding What and Where to Change
slug: finding-where-to-change
status: drafted
mastery:
seniority: mid
source: Working Effectively with Legacy Code (Michael C. Feathers), Chapter 17
prerequisites: [legacy-code/06]
created: 2026-08-10
updated: 2026-08-10
---

# Finding What and Where to Change

## TL;DR
Before you can apply any of this subject's techniques, you need to actually locate the specific code responsible for a specific behavior — Feathers recommends **reasoning about effects** (tracing forward from a cause to its consequences, or backward from an observed effect to its cause) combined with disciplined use of search tools, rather than reading a large, unfamiliar codebase linearly from the top.

## The idea
A quietly foundational skill this whole subject assumes but rarely states explicitly until this lesson: none of the seam-finding, characterization-testing, or dependency-breaking techniques matter if you can't first locate the *specific* code responsible for the behavior you need to change or understand. In an unfamiliar, large legacy codebase, "just read through it" doesn't scale — you need a more targeted, effect-driven search strategy.

## How it works

### Reasoning forward: "if I change this, what else changes?"
Starting from a specific piece of code you're considering modifying, trace *forward* through its callers and dependents to understand the full scope of what else might be affected — directly the same question `philosophy-of-software-design/01`'s change-amplification symptom asks, but used here as an *investigative technique* rather than just a diagnostic label. Tools that help: "find usages" / "find references" IDE features, grep/code search for a function or field's name, and — where available — static call-graph analysis.

**Worked example.** Before changing how `Order.total` is calculated, trace forward: which methods call `calculate_total()`? Which of *those* methods are, in turn, called by something else that might depend on the exact numeric result (a report, an audit log, a downstream billing integration)? This forward trace is what reveals the true scope of "if I change this one function, what's actually affected" — often larger, or differently-shaped, than an initial guess based on just reading the one function in isolation.

### Reasoning backward: "where does this observed behavior actually come from?"
Starting from an observed effect (a specific line in a UI, a specific value in an output, a specific bug report describing wrong behavior), trace *backward* to find the code responsible for producing it — this is the more common starting point for a bug fix or a "why does this field show the wrong value" investigation, and it requires a different search strategy than forward reasoning: starting from a distinctive string, label, or format visible in the actual output, and searching the codebase for where that string/format is produced.

**Worked example.** A bug report says a report's "Total Due" field shows an incorrect value. Backward reasoning: search the codebase for the literal string `"Total Due"` (a label likely to appear directly in the source, in a template, or in a constant) to find the rendering code, then trace backward from there to whatever computation actually produces the number being rendered — a much more targeted starting point than trying to guess which of dozens of financial-calculation functions might be responsible, based on function names alone.

### Combining both directions, and knowing when to stop
Real investigations often alternate between forward and backward reasoning: backward from an observed bug to find a suspect calculation, then forward from that calculation to check whether other, currently-correct behaviors also depend on it (and would need to remain correct after your fix). Knowing when you've traced *enough* — rather than continuing to trace indefinitely, chasing every possible transitive dependency — is itself a judgment call, informed by `legacy-code/06`'s point that comprehension-building should be scoped specifically to the task at hand, not an attempt to understand the entire system.

### Search tooling as a disciplined practice, not an afterthought
Feathers stresses treating code search as a deliberate, repeatable practice rather than an occasional, ad hoc activity: know your tools (IDE "find usages," full-text search across the repository, git history search for when a specific behavior was introduced) well enough to reach for the *right* one immediately for a given question, rather than defaulting to manually reading files top-to-bottom because it's the only technique you're fluent in. A specific, useful technique: searching git history/blame for *when* a specific line or behavior was introduced (and reading the associated commit message and any linked ticket) can recover the original *intent* behind a confusing piece of code far faster than trying to reverse-engineer that intent from the code alone.

### Effect-sketching as a byproduct of the search
As you trace forward or backward, Feathers recommends jotting down a simple, informal "effect sketch" — a short list or diagram of what calls what, and what depends on what, specifically for the area you're investigating — directly connecting to `legacy-code/06`'s lightweight, task-scoped comprehension sketches. This isn't separate documentation to maintain; it's a disposable, working artifact that captures what you've learned during the search itself, useful for the current task and safely discarded afterward.

## Pros
- Effect-based reasoning (forward and backward) is dramatically more targeted and time-efficient than linear, top-to-bottom reading of an unfamiliar codebase.
- Backward reasoning from a distinctive observed string/value is often the fastest way to locate the specific code responsible for a bug, especially in a large, unfamiliar system.
- Combining search-tool fluency with git-history investigation frequently recovers lost design intent faster than trying to infer it from the code's current state alone.

## Cons
- Effect-based search techniques work best when the codebase has distinctive, searchable strings/names to search from — heavily abstracted or dynamically-generated output can make backward reasoning from an observed value much harder.
- Knowing when to stop tracing (forward or backward) requires judgment that's easy to get wrong in either direction — stopping too early risks missing a genuinely affected dependent; continuing too long wastes time on transitively-related but practically-irrelevant code.
- Relying heavily on tooling (IDE features, code search) requires those tools to actually work well for the codebase's language/structure — some legacy codebases (heavy reflection, dynamic dispatch, generated code) resist accurate static "find usages" results, requiring more manual verification.

## Alternatives
- **Linear, top-to-bottom reading of the relevant module** — sometimes still the right choice for a genuinely small, self-contained module where effect-tracing tooling wouldn't meaningfully speed things up.
- **Asking someone who already has the context** (echoing `code-complete/12`'s point about knowledge distributed across a team) — often faster than independent investigation, when someone with direct experience of the specific area is actually available.
- **Adding targeted logging/tracing and observing real execution** — a dynamic, runtime alternative to static forward/backward reasoning, useful specifically when the actual call path taken for a given input isn't obvious from reading the code alone (e.g., due to heavy polymorphism or dynamic dispatch).

## When to use it
Use forward reasoning when you're considering changing a specific piece of code and need to understand its full blast radius. Use backward reasoning when you're starting from an observed behavior (a bug, a specific output) and need to find the code responsible. Combine both, and keep a disposable effect-sketch, for any nontrivial investigation in unfamiliar legacy code.

## When NOT to use it
Don't over-invest in exhaustive forward/backward tracing for a change whose scope is already obviously small and well-understood. Don't rely purely on static search tooling in codebases where dynamic dispatch or reflection make "find usages" results unreliable — verify with runtime observation (logging, a debugger) when static results seem incomplete or suspicious.

## Key takeaways / mental model
When you need to change or understand a specific behavior in unfamiliar legacy code, don't start reading top-to-bottom — start from either the cause (trace forward: what does this affect?) or the effect (trace backward: what produces this?), using search tools deliberately, and stop once you've covered what's actually relevant to your specific task.

## Self-check questions
1. Describe a recent investigation where you traced backward from an observed bug to its cause. What was your starting search term, and how did you know when you'd found the right code?
2. Explain the difference between forward and backward reasoning, and give an example of a situation where you'd need to use both in the same investigation.
3. Why can searching git history/blame sometimes recover design intent faster than reading the current code alone?
4. Describe a case where static "find usages" tooling gave misleading or incomplete results, and how you verified the real behavior instead.

## References
- Working Effectively with Legacy Code (Michael C. Feathers), Chapter 17: "It Takes Forever to Make a Change" (reasoning about effects; finding what to change).
