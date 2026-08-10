---
id: code-complete/04
subject: code-complete
title: "Working Classes: Cohesion and Abstraction"
slug: working-classes
status: drafted
mastery:
seniority: mid
source: Code Complete, 2nd ed. (Steve McConnell), Chapter 6
prerequisites: [code-complete/03, clean-code/10]
created: 2026-08-10
updated: 2026-08-10
---

# Working Classes: Cohesion and Abstraction

## TL;DR
A "good working class" presents a small, well-abstracted interface (a Good Abstract Data Type, in McConnell's terms) that hides its implementation completely, and its members should be strongly related — three specific, checkable kinds of cohesion (functional, sequential, communicational) are worth naming explicitly, because vague "cohesion" talk is harder to apply than a concrete taxonomy.

## The idea
`clean-code/10` established cohesion as "do the methods/fields belong together." This chapter goes a level more concrete, giving McConnell's practical taxonomy for *what kind* of cohesion a class actually has — useful because not all cohesion is equally strong, and naming the specific kind helps you judge whether a class is genuinely well-designed or just superficially organized.

McConnell also introduces the **Abstract Data Type (ADT)** framing as the goal for a well-designed class: think of the class not as "a bag of related methods" but as a genuinely new *type* with its own well-defined operations, hiding completely how those operations are implemented — a `Stack` class should let callers push/pop/peek without any awareness of whether it's backed by an array, a linked list, or something else, and that implementation should be swappable without any caller code changing.

## How it works

### The cohesion taxonomy, from strongest to weakest useful kinds
- **Functional cohesion (strongest, the goal)** — every part of the class works together toward exactly one well-defined task. A `Stack` class where every method (`push`, `pop`, `peek`, `isEmpty`) exists purely in service of "being a stack" is functionally cohesive.
- **Sequential cohesion** — outputs of one part feed as inputs to the next, like stages in a pipeline (`pragmatic-programmer/12`). Acceptable, and often unavoidable for genuinely pipeline-shaped logic, but weaker than functional cohesion because the parts are related by data flow order rather than by all serving one single unified purpose.
- **Communicational cohesion** — parts operate on the same data but don't otherwise depend on each other's logic (e.g., several unrelated report-generation methods that all happen to read the same underlying dataset). Weaker still — the *only* thing tying them together is shared data, not shared purpose, which is a much looser bond and a common source of the "low cohesion, split this class" smell from `clean-code/12`.
- **(Weaker kinds — temporal, logical, coincidental cohesion)** — the book catalogs progressively weaker/worse forms (grouped just because they happen at the same time, or grouped under one artificial "type code" switch, or grouped with no real reason at all) as anti-patterns to actively avoid, not options to choose among.

**Worked example.** A `ReportGenerator` class with methods `generate_pdf()`, `generate_csv()`, `send_email_summary()`, and `log_generation_event()`, all operating on the same `report_data` field:
- This is at best communicationally cohesive — the methods share data but don't meaningfully depend on each other's logic; `generate_pdf` doesn't need `send_email_summary` to have run, and vice versa.
- Splitting it into `PdfReportRenderer`, `CsvReportRenderer`, `ReportEmailer`, and `ReportEventLogger` — each functionally cohesive around exactly one task — is a strict cohesion upgrade, directly mirroring `clean-code/10`'s worked example, now with the taxonomy to name precisely *why* the original grouping was weak (communicational, not functional).

### Good Abstract Data Types hide implementation completely
The ADT framing's specific, checkable test: **can the implementation be swapped without any caller code changing?** If yes, the abstraction is genuinely complete. If callers need to know (even indirectly, through behavior they depend on) whether a `Stack` is array-backed or linked-list-backed — say, because they rely on a specific performance characteristic or a subtle ordering quirk of one particular implementation — the abstraction is leaking, and the class isn't yet a "good working class" by this chapter's standard.

**Worked example — a leaky ADT:**
```
class Stack:
    def __init__(self):
        self._items = []      # exposed directly as a public attribute
    def push(self, item): self._items.append(item)
    def pop(self): return self._items.pop()

# caller code, elsewhere, reaching past the intended interface:
stack.items[0]  # directly indexes internal storage — now coupled to "it's a list"
```
If `_items` (or an equivalent unprotected field) is accessible and callers use it directly, swapping the internal representation (say, to a `collections.deque` for performance) risks breaking every caller that reached past the intended `push`/`pop` interface — the class was never a genuine ADT, just a thin, leaky wrapper around exposed internals.

### Minimize the public interface, and separate "must-know" from "nice-to-know"
McConnell's specific guidance for interface design: expose the smallest set of public members that satisfies genuine caller needs, and be deliberate about which methods are the class's actual contract (must-know) versus incidental conveniences that happen to be public but that callers shouldn't rely on as load-bearing (nice-to-know, ideally marked or documented as such, or better, just kept private). A bloated public interface — even one where the *implementation* is otherwise well-hidden — still increases the cognitive load (`code-complete/02`) of understanding how to use the class correctly.

## Pros
- The specific cohesion taxonomy gives a checkable vocabulary for *why* a class's cohesion is weak, beyond a vague "this class feels wrong."
- The ADT "can the implementation be swapped without callers changing" test is a concrete, verifiable check for whether encapsulation is genuinely complete, not just nominally present.
- A minimized public interface directly reduces the cognitive load a caller needs to learn to use a class correctly.

## Cons
- Achieving genuinely complete implementation-hiding (the ADT ideal) sometimes has real costs — a fully opaque abstraction can hide performance characteristics callers actually need to know about to use the class correctly at scale.
- Classifying a class's cohesion type precisely (functional vs. sequential vs. communicational) requires careful analysis that's sometimes ambiguous in practice, especially for classes that are mostly but not perfectly one kind.
- Minimizing the public interface too aggressively can force callers into awkward workarounds if a genuinely useful, safe operation is kept private out of excess caution.

## Alternatives
- **Duck typing / structural typing (no formal ADT enforcement)** — in dynamically-typed languages, "ADT-like" behavior is often achieved by convention rather than compiler-enforced encapsulation, trading some safety for flexibility.
- **Interfaces/protocols as the explicit contract, separate from any concrete class** — formalizes the "callers depend on the interface, not the implementation" idea at the language level (see `software-engineering/clean-architecture`'s dependency inversion), going a step further than a single well-encapsulated class.
- **Value objects / immutable data with no behavior** (see `clean-code/06`'s data-structure style) — for cases where the "type" genuinely has no meaningful behavior beyond holding data, a plain immutable structure may be more honest than forcing an ADT shape onto it.

## When to use it
Apply the cohesion taxonomy whenever evaluating whether a class should be split — naming the specific weak-cohesion type (usually communicational, in practice) makes the case for splitting concrete rather than just a feeling. Apply the "can the implementation be swapped" test to any class meant to represent a reusable abstraction, especially ones with multiple callers.

## When NOT to use it
Don't force full ADT-style opacity onto a class that's genuinely meant to be a transparent, behavior-free data holder (see `clean-code/06`) — that's the wrong tool for that job. Don't treat sequential or communicational cohesion as automatically disqualifying if the domain genuinely is pipeline-shaped or genuinely does need several operations over one shared dataset with no cleaner split available.

## Key takeaways / mental model
Ask two concrete questions about any class: "what specific kind of cohesion holds this together — functional, sequential, or just 'shares the same data'?" and "could I swap this class's internal implementation without any caller noticing?" A "yes, functional" and a "yes, swappable" together are the signature of a genuinely good working class.

## Self-check questions
1. Classify the cohesion type of a class from your own code using McConnell's taxonomy (functional, sequential, communicational, or weaker). What would it take to upgrade it toward functional cohesion?
2. Using the `Stack` example, explain concretely what makes an ADT's abstraction "leaky," and how you'd fix it.
3. Why does a minimized public interface reduce cognitive load even when the implementation is already fully hidden?
4. Give an example of a case where full implementation-hiding (the ADT ideal) actually hid information a caller legitimately needed, and how you'd resolve that tension.

## References
- Code Complete, 2nd ed. (Steve McConnell), Chapter 6: "Working Classes".
