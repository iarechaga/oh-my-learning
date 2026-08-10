---
id: philosophy-of-software-design/04
subject: philosophy-of-software-design
title: Information Hiding and Leakage
slug: information-hiding
status: drafted
mastery:
seniority: senior
source: A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 5
prerequisites: [philosophy-of-software-design/03, clean-code/06]
created: 2026-08-10
updated: 2026-08-10
---

# Information Hiding and Leakage

## TL;DR
Deep modules (`philosophy-of-software-design/03`) are achieved primarily through information hiding — a module encapsulating a design decision entirely within itself, so nothing outside needs to know it. Information *leakage* is the specific, checkable failure mode where a single design decision is reflected in more than one module's interface, even if each module's own internals are otherwise well-encapsulated — a subtler and more common problem than exposing raw internal fields.

## The idea
`clean-code/06` already established the basic idea of hiding an object's internal representation behind behavior. Ousterhout's treatment goes further, focusing specifically on **design decisions** as the unit that should be hidden, and introducing a specific, checkable diagnostic — information leakage — for detecting when a decision has escaped its intended module even though no internal *field* was technically exposed.

**Information hiding**, precisely: a module should encapsulate a piece of knowledge (a design decision, an implementation choice) so that other modules do not need to know it to use this one correctly. This is stronger than "don't expose your fields" — it's "don't let any *decision* about how you work internally become something other modules must independently know or assume."

**Information leakage**, precisely: leakage occurs when a design decision is reflected in the interfaces (not necessarily the internals) of *multiple* modules — meaning changing that one decision requires modifying more than one module, even though each module individually looks well-encapsulated. This is the concrete, checkable test the chapter gives you: **if a single design decision affects the interface of more than one module, that decision has leaked.**

## How it works

### Leakage without exposed internals — the subtle case
A module can pass every naive "encapsulation" check (no public fields, clean getters/setters, well-named methods) and *still* leak information, if a design decision it makes is nonetheless reflected in how another module's interface is shaped.

**Worked example.** A file-parsing system split into a `FileReader` class and a `RecordParser` class, where `FileReader` reads raw bytes and `RecordParser` parses them into structured records. Both classes look individually well-encapsulated — no exposed fields, clean method signatures. But suppose the file format uses a specific record-delimiter byte, and *both* classes independently need to know what that delimiter is (`FileReader` to know where to split raw chunks; `RecordParser` to know where one record's bytes end) — if the delimiter value is hardcoded (or separately configured) in both classes, the design decision "records are delimited by byte X" has leaked across two module interfaces, even though neither class exposes an internal field publicly. Changing the delimiter now requires finding and updating it in both places — this is change amplification (`philosophy-of-software-design/01`) caused specifically by leakage, not by any obviously "unencapsulated" code.

**The fix**: centralize the delimiter knowledge in exactly one place — perhaps a shared `RecordFormat` object that both `FileReader` and `RecordParser` receive, so the decision lives in one location and both modules depend on that one source rather than independently encoding the same fact. This is structurally identical to `pragmatic-programmer/03`'s DRY principle, but framed here specifically around *design decisions reflected in interfaces*, which is a more general and often more subtle version of the same underlying concern than DRY's more code-text-focused framing.

### Temporal decomposition — a specific, common cause of leakage
Ousterhout names a specific, easy-to-fall-into anti-pattern: splitting a module's structure to match the *order operations happen in* (temporal decomposition) rather than the *knowledge each piece genuinely owns*. "First we read the file, then we parse it, then we validate it" looks like a natural decomposition, but if "read" and "parse" both need to know the record-delimiter fact (as in the example above), splitting along that temporal seam has separated two pieces of code that share a design decision, guaranteeing leakage — the seam should instead follow where knowledge naturally lives, which sometimes doesn't align neatly with execution order at all.

### Leakage between a caller and a callee, not just between peer modules
Leakage isn't limited to two peer classes — it also occurs when a caller must know something about a callee's internal decisions to use it correctly, even if that knowledge isn't a literal shared constant. If a caller must know "call `initialize()` before `process()`, and you must call `close()` exactly once when done, in that specific order" — that ordering *decision* has leaked into the caller's required knowledge, even though it's expressed as documentation/convention rather than a duplicated constant. `clean-code/11`'s construction/use separation and this lesson's leakage concept converge here: a caller needing detailed knowledge of a callee's required call sequence is a form of leaked design decision (the sequencing was an internal implementation choice that should, ideally, have been hidden behind a single call, per `philosophy-of-software-design/03`'s deep-module standard).

### Detecting leakage — a practical checklist
Ousterhout's practical diagnostic questions, useful to run against any pair of modules you suspect might be too intertwined:
1. If I change this specific decision (a format, a threshold, an ordering requirement), how many modules' interfaces (not just internals) would I need to touch?
2. Does understanding module A require me to also understand something about module B's internal implementation, beyond A's own stated interface?
3. Did I split these modules by *execution order* rather than by *which one genuinely owns this piece of knowledge*?

Any "yes, more than one" or "yes, I do" answer to these is a concrete, actionable signal of leakage, pointing at exactly which decision needs to be re-centralized and where.

## Pros
- Gives a more general, more precise diagnostic than "don't expose fields" — catches leakage even between modules that both look individually well-encapsulated.
- Directly explains a specific, common, and otherwise hard-to-name root cause of change amplification (`philosophy-of-software-design/01`), turning a vague "this feels coupled" into a checkable question about which decision leaked and where.
- Naming temporal decomposition as a specific anti-pattern gives a concrete alternative lens for module boundaries, beyond "split by size" or "split by what happens first."

## Cons
- Detecting leakage between modules that both look superficially clean requires deliberately asking "what design decision does this reflect, and does another module also reflect it" — a habit that takes real practice to apply reliably, unlike a mechanically checkable rule.
- Fixing leakage sometimes requires restructuring module boundaries substantially (moving a decision's ownership entirely, not just editing one file), a nontrivial refactoring cost once the leakage has already shaped a codebase's structure.
- Not every shared piece of information between modules is leakage in the harmful sense — some genuinely shared, essential facts about a domain (e.g., a currency's ISO code) are legitimately known by multiple modules without that being a design flaw; distinguishing essential shared knowledge from leaked design decisions requires judgment.

## Alternatives
- **DRY** (`pragmatic-programmer/03`) — a narrower, more code-focused version of essentially the same underlying concern (duplicated knowledge), useful as a first-pass heuristic before reaching for the more general, interface-focused leakage lens.
- **Bounded contexts** (see `domain-modeling/ddd-evans`) — a coarser-grained, domain-level version of the same principle, deciding which business concepts and rules "belong" to which part of a larger system, at a scale beyond individual classes/modules.
- **Interface Segregation Principle** (see `software-engineering/clean-architecture`) — addresses a related but distinct concern (clients shouldn't depend on interface members they don't use), complementary to but not the same question as whether a design decision has leaked across module boundaries.

## When to use it
Run the leakage diagnostic whenever you notice a change requiring edits to more than one module for what feels like it should be a single, localized decision, or whenever you're deciding where to draw a new module boundary — check whether you're splitting by execution order (risky) versus by genuine knowledge ownership (safer).

## When NOT to use it
Don't treat every piece of information shared between two modules as leakage — some domain facts are legitimately, harmlessly known in more than one place without representing an escaped design decision; the test is specifically whether a *decision* (not an essential domain fact) is redundantly reflected in multiple interfaces.

## Key takeaways / mental model
For any design decision, ask: "if I changed this tomorrow, how many modules' interfaces — not just internals — would I need to touch?" More than one is leakage, and the fix is finding where that decision should actually live as a single, owned piece of knowledge, then having every other consumer depend on that one source instead of independently encoding the same fact.

## Self-check questions
1. Using the file-parser example, explain precisely how leakage occurred even though neither `FileReader` nor `RecordParser` exposed any public fields.
2. What is temporal decomposition, and why does splitting by execution order tend to produce leakage specifically?
3. Give an example from your own code of a caller needing to know a callee's required call-order (an implicit sequencing decision leaking into the caller's required knowledge).
4. Describe a case where two modules share information that is NOT leakage — a legitimately shared domain fact rather than an escaped design decision. What distinguishes it from true leakage?

## References
- A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 5: "Information Hiding (and Leakage)".
