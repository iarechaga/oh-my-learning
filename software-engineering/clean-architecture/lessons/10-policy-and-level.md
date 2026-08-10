---
id: clean-architecture/10
subject: clean-architecture
title: Policy, Level, and the Direction of Dependencies
slug: policy-and-level
status: drafted
mastery:
seniority: senior
source: Clean Architecture (Robert C. Martin), Chapter 19
prerequisites: [clean-architecture/08]
created: 2026-08-10
updated: 2026-08-10
---

# Policy, Level, and the Direction of Dependencies

## TL;DR
Martin defines a component's "level" precisely as its distance from the system's inputs and outputs — not its position in a conventional layer diagram, and not how "important" it feels. Higher-level policy (further from inputs/outputs, closer to the core business decision) should never depend on lower-level policy (closer to the actual mechanics of getting data in and out) — this gives a rigorous, checkable rule for deciding which of two related pieces of policy should depend on the other, beyond the more intuitive but less precise "business logic vs. detail" framing.

## The idea
`clean-architecture/08`'s dependency rule established that inner circles shouldn't depend on outer ones — but within a single circle, or when comparing two pieces of business logic that both seem like "policy," how do you decide which one is more fundamental, and therefore which one the other should depend on? Martin's answer is a specific, precise definition of **level**: **a component's level is the distance from the inputs and outputs of the system.** The component closest to the raw inputs and outputs (parsing a keystroke, formatting a pixel) is lowest-level; the component encoding the most abstract, input/output-independent business decision is highest-level.

## How it works

### Level, precisely defined — and why "further from I/O" is the right criterion
Martin's specific example: an encryption program's core policy is "read a character, transform it, write the transformed character" — the *transformation algorithm* itself (say, a specific cipher) is genuinely independent of *how* characters are read or written (from a file, from a network socket, from stdin) — it operates purely on the abstract concept of "a stream of characters in, a stream of characters out." This transformation policy is **higher-level** than the character-reading and character-writing code, precisely because it's further removed from the actual, concrete mechanics of I/O — it would remain exactly the same, unchanged, no matter which specific I/O mechanism eventually supplies or consumes those characters.

**Why this matters as a *dependency direction* rule, not just a description.** Higher-level components (further from I/O, encoding more fundamental policy) should never depend on lower-level components (closer to I/O, encoding more specific mechanism) — the transformation algorithm should not need to know or care whether characters come from a file or a socket. If it did — if the cipher's code directly called a file-reading function — you couldn't reuse that same cipher logic with a different I/O source without modifying the cipher itself, exactly the kind of unnecessary coupling `clean-architecture/04`'s DIP and `clean-architecture/08`'s dependency rule both exist to prevent, now given a more precise, general criterion (distance from I/O) for deciding *which* of two components is the "higher" one whose independence should be protected.

### Worked example — applying level to decide a dependency's direction
Consider a reporting system with two pieces of logic that both, informally, look like "business rules": (a) "a financial report's numbers must be rounded to two decimal places and formatted with a currency symbol" and (b) "the specific layout of a PDF report, including page breaks and headers." Both feel like policy, but applying the level test: (a) is genuinely further from any specific I/O mechanism — the rounding-and-formatting rule for currency values is the same true business fact regardless of whether the result ends up in a PDF, a CSV, or a JSON API response. (b) is much closer to a specific output mechanism (PDF rendering specifically) — it's a lower-level policy, tightly bound to one particular output format's concrete constraints (physical page size, specific layout conventions).

By the level rule, (a) should be higher-level than (b), and the dependency should point from (b) to (a) — the PDF-layout logic can depend on (and call) the currency-formatting rule, but the currency-formatting rule should never need to know anything about PDF page breaks or headers. This gives a precise, checkable way to resolve what might otherwise be an ambiguous "which of these two pieces of business logic is more fundamental" debate.

### Distinguishing level from the more common, looser "business logic vs. technical detail" framing
The looser framing (used informally throughout much of this subject and the broader industry) tends to treat "business logic" as a single, undifferentiated blob, all equally "high-level" relative to any technical detail. Martin's level concept refines this: **not all business logic is at the same level.** Two pieces of logic can both be genuine business rules and still have a meaningful, checkable ordering between them, based specifically on which is further from a system's actual inputs and outputs — the currency-formatting-versus-PDF-layout example shows this precisely: both are "business rules" in a loose sense, but one is clearly higher-level than the other by the more precise criterion.

### Policy at different levels still obeys the same dependency-inversion mechanism
When a genuinely higher-level policy does need something from a lower-level one (the PDF layout logic needs to actually render text, which is inherently close to output), the fix is the same DIP mechanism already established (`clean-architecture/04`, `clean-architecture/08`): the higher-level policy defines the interface it needs, and the lower-level mechanism implements it — level, in this sense, is really the more general, precise underlying reason *why* the Dependency Rule's inner/outer circle structure works in the first place, rather than a separate, competing concept.

## Pros
- Gives a precise, checkable criterion (distance from I/O) for resolving ambiguous cases where two pieces of code both seem like "business logic," but one should clearly depend on the other.
- Explains, more generally and more rigorously, *why* the Dependency Rule's circles are ordered the way they are — level is the underlying principle, and the circles are one specific, concrete application of it.
- Prevents accidentally coupling a genuinely fundamental, reusable business rule to a specific, narrow output/input mechanism that happens to be adjacent to it in the code.

## Cons
- Determining exactly how "close to I/O" a given piece of logic is requires judgment, and isn't always as clean and unambiguous as the encryption or currency-formatting examples suggest — some logic genuinely straddles the line.
- The level concept, while precise in principle, is less immediately intuitive to apply day-to-day than the simpler "business logic vs. technical detail" heuristic most engineers already use — it requires deliberate practice to internalize.
- Over-applying level-based separation to logic that will never plausibly need to be reused independently of its current context (e.g., a PDF-layout detail that will genuinely never serve any other output format) can produce unnecessary structural ceremony.

## Alternatives
- **The simpler "business logic vs. technical detail" heuristic** — sufficient for many day-to-day decisions, and what most of this subject's earlier lessons implicitly rely on; level is a sharper, more rigorous refinement specifically useful when that simpler heuristic produces ambiguous or contested results.
- **Domain-driven design's layering of domain services, application services, and infrastructure** (see `domain-modeling/ddd-evans`) — a related, if less precisely quantified, way of ordering business logic by its distance from technical concerns.
- **Explicit architectural layering diagrams with named layers** (see `architecture/fundamentals`) — a more prescriptive, coarser-grained alternative that assigns level implicitly via a fixed set of named layers, rather than deriving it case by case from the distance-from-I/O criterion.

## When to use it
Apply the level criterion specifically when two pieces of logic both seem like legitimate "policy" but you're unsure which should depend on the other — ask which is genuinely closer to the system's actual inputs/outputs, and let the higher-level one (further from I/O) be the one depended upon, never the reverse.

## When NOT to use it
Don't apply the full level analysis to every single dependency decision in a codebase — for most everyday cases, the simpler "business logic vs. detail" heuristic is sufficient, and reserving level's more rigorous analysis for genuinely ambiguous cases keeps the technique's overhead proportionate to its actual value.

## Key takeaways / mental model
When deciding which of two pieces of logic should depend on the other, ask: "which of these is further from the system's actual inputs and outputs?" The one further away is higher-level, and it should never depend on the one closer to I/O — that dependency should always point the other way, using DIP if a direct call is needed.

## Self-check questions
1. Using the encryption example, explain precisely why the transformation algorithm is higher-level than the character-reading/writing code, using the distance-from-I/O criterion.
2. Apply the level test to the currency-formatting versus PDF-layout example, and explain why both are "business logic" yet have a clear, non-symmetric dependency ordering between them.
3. Describe a case from your own code where two pieces of business logic seemed equally "important" but, on reflection using the level criterion, one was clearly higher-level than the other.
4. Why does Martin's level concept refine, rather than replace, the simpler "business logic vs. technical detail" heuristic most engineers already use?

## References
- Clean Architecture: A Craftsman's Guide to Software Structure and Design (Robert C. Martin), Chapter 19: "Policy and Level".
