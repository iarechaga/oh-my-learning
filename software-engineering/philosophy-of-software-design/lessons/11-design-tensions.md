---
id: philosophy-of-software-design/11
subject: philosophy-of-software-design
title: Design Tensions and When Principles Conflict
slug: design-tensions
status: drafted
mastery:
seniority: senior
source: A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 21 and synthesis across the book
prerequisites: [philosophy-of-software-design/03, philosophy-of-software-design/05, philosophy-of-software-design/06]
created: 2026-08-10
updated: 2026-08-10
---

# Design Tensions and When Principles Conflict

## TL;DR
Nearly every design principle in this subject (and its Clean Code counterpart) has situations where following it fully would violate another, equally valid principle — the skill this closing lesson develops is recognizing the tension explicitly and making a deliberate, judged trade-off, rather than mechanically applying whichever principle you happened to think of first.

## The idea
A recurring theme across this whole subject, made explicit here: design principles are heuristics that generally point toward good outcomes, not laws that can be mechanically combined without ever conflicting. Deep modules (`philosophy-of-software-design/03`) push toward consolidation; general-purpose design (`philosophy-of-software-design/05`) pushes toward flexibility that can add interface surface; pulling complexity downward (`philosophy-of-software-design/06`) pushes toward absorbing more into fewer places. Each is individually sound, and yet situations regularly arise where satisfying one fully means violating another — this chapter's job is to name the most common of these tensions explicitly, so you can recognize them as *genuine trade-offs requiring judgment*, not as evidence that you've misapplied one of the principles.

## How it works

### Tension 1: General-purpose vs. special-purpose
`philosophy-of-software-design/05` argued for somewhat-general-purpose modules; but a module made *more* general to serve a wider variety of callers usually needs a *more complex* interface to accommodate that variety (more parameters, more configuration options) — which can push it toward shallower (`philosophy-of-software-design/03`), not deeper, exactly counter to the deep-module ideal. A module tailored precisely to one caller's exact need, by contrast, can have a very simple, narrow interface (deep, relative to its narrow scope) — but at the cost of the reusability `philosophy-of-software-design/05` values.

**Worked example.** A caching module: a special-purpose `UserProfileCache` (caches exactly one specific data shape, one specific eviction policy) can have an extremely simple interface (`get(user_id)`, `invalidate(user_id)`) — deep relative to its narrow job. A general-purpose `Cache<K, V>` usable for any key/value type, with configurable eviction policies, TTLs, and size limits, is far more broadly reusable, but its interface is necessarily more complex (more type parameters, more configuration) — shallower, relative to any single specific use. Neither is unconditionally "right"; the correct choice depends on whether a second, genuinely different caller with different needs is expected soon (favoring general-purpose) or not (favoring the simpler special-purpose module).

### Tension 2: Pull complexity downward vs. keep modules independent/deep
`philosophy-of-software-design/06` argued for absorbing complexity into a lower module rather than pushing it onto callers — but sometimes the complexity being absorbed genuinely belongs to a *different* concern than the module's core purpose, and stuffing it in anyway to spare callers can violate the module's own single-purpose depth, producing exactly the low-cohesion problem `clean-code/10` warns against, dressed up as "pulling complexity down."

**Worked example.** An `HttpClient` module absorbing not just connection/retry logic (clearly its own concern) but also business-specific response caching logic for one particular API it happens to be used with most often — "pulling complexity down" to spare that one caller from handling caching itself, but at the cost of bloating `HttpClient` with a concern (business-specific caching policy) that doesn't belong to "being an HTTP client" at all, and that other callers of the same `HttpClient` for unrelated APIs now have to carry as unused baggage in the interface. The better trade-off here is usually a separate, purpose-built caching layer *composed with* the HTTP client, not absorbed into it — recognizing that "pull complexity down" has a limit at the boundary of what a module's core purpose actually is.

### Tension 3: Consistency vs. the best fit for a specific case
`philosophy-of-software-design/10` and `code-complete/08` both argue for codebase-wide naming/pattern consistency — but a specific situation occasionally has a genuinely better-fitting name, structure, or pattern that deviates from the established convention. Rigidly prioritizing consistency in every single case, even where it's clearly suboptimal for a specific situation, can itself become counterproductive dogmatism; but abandoning consistency too readily whenever a "better" local option appears erodes the very benefit consistency provides.

### There's no formula — the actual skill is recognizing tension exists at all
The chapter's real, if somewhat humbling, conclusion: there's no higher-order principle that automatically resolves these tensions for you — experienced designers aren't people who've found a way to avoid the trade-offs, they're people who've developed the judgment to weigh them well in context, case by case. The single most valuable, teachable habit this closing lesson pushes for isn't a resolution rule — it's simply **noticing when two principles you'd otherwise apply automatically are actually pulling in opposite directions**, and treating that recognition as the moment for deliberate, explicit judgment (ideally informed by discussion with a teammate, echoing `code-complete/12`'s review-catches-what-solo-work-misses argument) rather than defaulting unconsciously to whichever principle happened to come to mind first.

### A meta-technique for weighing a genuine tension: ask what's most expensive to get wrong, and what's most reversible
When a real tension is identified, one practical tiebreaker (echoing `pragmatic-programmer/05`'s reversibility framing): which side of the trade-off is cheaper to reverse later if you're wrong? If the general-purpose-vs-specific tension is genuinely unresolved, and the module is easy to refactor later once a second real caller appears, leaning special-purpose *now* and generalizing *later, once genuinely needed* (echoing the Rule of Three) is often the lower-risk default — not because general-purpose design is wrong, but because deferring a hard-to-reverse commitment until you have real evidence is usually the safer bet than guessing early.

## Pros
- Naming design tensions explicitly prevents the false sense that any single principle can be applied mechanically without judgment, which is a more honest and ultimately more useful mental model than treating principles as unconditional rules.
- Recognizing a tension in the moment, rather than after the fact, allows a deliberate trade-off decision rather than an accidental, unexamined one.
- The reversibility-based tiebreaker gives a concrete, actionable default for genuinely unresolved tensions, rather than leaving you stuck without any way to decide.

## Cons
- "It requires judgment" is, honestly, a less satisfying and less immediately actionable answer than a crisp rule — this chapter's guidance is inherently harder to apply mechanically than most of the more specific techniques earlier in this subject.
- Different experienced engineers can reasonably weigh the same tension differently, meaning this chapter doesn't eliminate legitimate design disagreement, only makes the disagreement's actual source easier to identify and discuss productively.
- Overemphasizing "there's always a tension, use judgment" risks becoming an excuse to avoid applying any principle rigorously at all, if not paired with genuine effort to first understand each principle deeply on its own terms (as the rest of this subject aims to build).

## Alternatives
- **A fixed, no-exceptions priority ordering of principles** (e.g., "always prefer deep modules over general-purpose design when they conflict") — simpler to apply consistently, but risks producing systematically bad outcomes in the specific situations where the deprioritized principle was actually the more important consideration.
- **Pure case-by-case intuition with no explicit framework** — what many experienced designers actually do in practice, but harder to teach, articulate, or apply consistently across a team without the vocabulary this subject's principles provide as a shared reference.
- **Architecture Decision Records** (see `architecture/fundamentals`) — for larger-scale tensions, formally documenting the trade-off considered and the reasoning behind the chosen resolution, making the judgment call reviewable and revisitable later rather than an implicit, undocumented decision.

## When to use it
Apply this chapter's tension-recognition habit whenever two principles from this subject seem to be pulling toward different designs for the same piece of code — pause and explicitly name which two principles are in tension, rather than silently picking one without examining the trade-off.

## When NOT to use it
Don't invoke "it's just a design tension, use judgment" to avoid genuinely learning and applying any individual principle rigorously first — the tensions in this chapter are meaningful specifically because the underlying principles are each individually sound; treating everything as an unresolvable judgment call without first understanding the principles well is a cop-out, not the nuanced stance this chapter is actually recommending.

## Key takeaways / mental model
When a design decision feels harder than it should, check whether two principles you'd normally apply automatically are actually in tension for this specific case. Name both sides explicitly, and when genuinely stuck, default toward whichever choice is cheaper to reverse later if it turns out wrong.

## Self-check questions
1. Using the caching module example, explain the specific tension between general-purpose design and module depth, and describe the deciding factor that would push you toward one or the other for a specific real situation.
2. Describe a real design decision you've made where, in hindsight, you were unconsciously resolving a tension between two principles without recognizing it as such. What would explicitly naming the tension have changed?
3. Why does the chapter argue there's no higher-order rule that resolves every tension, and why is that itself a useful (not merely disappointing) conclusion?
4. Using the reversibility tiebreaker, work through a genuine tension from your own experience and decide which side to lean toward, explaining why based on reversibility specifically.

## References
- A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 21: "Conclusion" and design-tension synthesis drawn across the book's principles.
