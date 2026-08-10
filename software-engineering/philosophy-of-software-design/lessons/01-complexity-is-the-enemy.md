---
id: philosophy-of-software-design/01
subject: philosophy-of-software-design
title: "Complexity Is the Enemy: Symptoms and Causes"
slug: complexity-is-the-enemy
status: drafted
mastery:
seniority: mid
source: A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapters 2-3
prerequisites: [code-complete/02]
created: 2026-08-10
updated: 2026-08-10
---

# Complexity Is the Enemy: Symptoms and Causes

## TL;DR
Ousterhout gives complexity a precise operational definition — anything about a system's structure that makes it harder to understand and modify — and names three specific causes: change amplification, cognitive load, and unknown unknowns. Every design technique in this subject is a direct response to one or more of these three, which makes them worth memorizing precisely, not just as a vague "keep things simple" slogan.

## The idea
`code-complete/02` already argued complexity is the root problem construction practices exist to manage, largely through the lens of human working-memory limits. Ousterhout's book, which this subject is built around, sharpens that same core claim into a much more precise, actionable framework — and it's useful to hold both books' framings in tension (as the subject's own README notes), because Ousterhout occasionally reaches *opposite* practical conclusions from Clean Code on specifics like function length, precisely because he's optimizing the same underlying goal (manage complexity) via a somewhat different theory of what actually drives it.

Ousterhout's definition: **complexity is anything related to the structure of a software system that makes it hard to understand and modify.** Note what this definition deliberately excludes — it's not about how hard a *problem domain* is, and it's not about raw lines of code; it's specifically about *structure*, and specifically about the practical consequences (understanding, modifying) that structure produces for the people working with it.

## How it works

### Three symptoms — how complexity shows up in practice
- **Change amplification** — a seemingly simple change requires modifications in many different places. If fixing "update the tax rate" requires touching five files because the rate is duplicated (echoing `pragmatic-programmer/03`'s DRY concern), that's change amplification, and it's a directly observable, measurable symptom you can point to in a specific codebase.
- **Cognitive load** — how much a developer needs to know to complete a task. This isn't about a system's intrinsic difficulty; it's about how much of that difficulty a specific piece of code's structure exposes to someone trying to make a change, echoing `code-complete/02`'s working-memory framing but naming it as a distinct, separately-measurable symptom of complexity rather than complexity's sole definition.
- **Unknown unknowns** — it's unclear what code must be modified to complete a task, or what information is even relevant. This is the most dangerous symptom, because change amplification and cognitive load are at least *visible* once you're doing the work — unknown unknowns mean you don't even know there's a problem until something breaks later, in production, because a required change was invisible from where you were looking.

**Worked example.** A team adds a new payment method and, mid-implementation, discovers a currency-formatting rule that lives in a completely unrelated analytics module, silently depended on by the payment flow through an implicit assumption nobody documented. This is a textbook unknown-unknown: the connection wasn't visible from reading the payment code, wasn't caught by tests (which didn't know to test for it), and only surfaced because someone happened to notice the analytics numbers looked wrong after shipping — the single most expensive kind of complexity symptom, because by the time it's discovered, it's already caused a real, live problem.

### Two causes — where complexity actually comes from
Ousterhout identifies two root causes that produce the three symptoms above:
- **Dependencies** — a piece of code cannot be understood and modified in isolation; a change requires understanding or modifying other, related code as well. Some dependencies are unavoidable (echoing `code-complete/02`'s "essential complexity"), but many are accidental, and accidental dependencies are the primary lever this subject's techniques (deep modules, information hiding) pull on.
- **Obscurity** — important information is not obvious. This isn't the same as a dependency existing — it's that a *real* dependency exists but isn't visible or discoverable from where a developer is looking, which is precisely what turns an ordinary dependency into an unknown-unknown. A well-documented, clearly-named dependency is still a dependency (and still costs something), but it's not obscure — a developer can find and account for it. An *undocumented*, unnamed dependency buried in an unrelated module is both a dependency and obscurity simultaneously, and is disproportionately more dangerous than either alone.

### Complexity is incremental, not a single big decision
A crucial, practically important claim: complexity rarely accumulates from one bad decision — it accumulates from many small ones, each individually reasonable-seeming at the time ("just this one shortcut," echoing `pragmatic-programmer/02`'s broken-windows theory), whose combined effect over time is a system where every task suffers from change amplification, cognitive load, and unknown unknowns simultaneously. This has a direct practical implication Ousterhout returns to repeatedly through the rest of the book: because complexity accumulates incrementally, it must be *fought* incrementally too — there is no single refactor that "fixes" complexity once and for all; it requires continuous, disciplined attention to every individual design decision, similar in spirit to `pragmatic-programmer/15`'s argument that quality habits only work as sustained team norms, not one-time interventions.

### Why this framework matters practically, beyond the vocabulary
Naming the specific symptom and cause of a design problem you're looking at turns a vague "this feels bad" into an actionable diagnosis: "this change required touching six files" is change amplification, caused by a duplicated/scattered dependency — the fix is centralizing that dependency (DRY, `pragmatic-programmer/03`). "I had to read four unrelated modules to understand this one function" is cognitive load, caused by insufficiently hidden dependencies — the fix is better information hiding (`philosophy-of-software-design/04`). Having this precise vocabulary is what lets the rest of this subject's techniques be *targeted* fixes for a specific diagnosed problem, rather than generically-applied "best practices."

## Pros
- A precise, three-symptom/two-cause framework converts a vague complaint ("this code is bad") into a specific, actionable diagnosis pointing toward a specific fix.
- Naming unknown unknowns as the most dangerous symptom correctly prioritizes attention toward the failure mode that's hardest to detect before it causes real damage.
- Framing complexity as incremental and continuous (not a single event) sets realistic expectations for how design quality is actually maintained over a codebase's life.

## Cons
- The framework, while precise, still requires judgment to apply — deciding whether a given dependency is "essential" or "accidental," or whether information is genuinely "obscure" versus just unfamiliar to a particular reader, isn't always clear-cut.
- Diagnosing unknown unknowns specifically is inherently hard by definition (you don't know what you don't know) — the framework names the danger but doesn't, on its own, give you a way to systematically find them before they bite.
- Treating complexity purely as a structural, code-level property can undersell genuinely essential domain complexity that no amount of restructuring will eliminate (echoing `code-complete/02`'s essential-vs-accidental distinction).

## Alternatives
- **Cyclomatic complexity and other computable metrics** (`code-complete/11`) — a narrower, more mechanically measurable proxy for one facet (roughly, cognitive load from control flow specifically) of Ousterhout's broader three-symptom framework, useful as an automatable complement rather than a substitute.
- **Cognitive load theory from `code-complete/02`** — a closely related but less structurally specific framing, focused primarily on working-memory limits rather than distinguishing change amplification, obscurity, and unknown unknowns as separate mechanisms.
- **Technical debt as a financial metaphor** — a different vocabulary for roughly the same underlying phenomenon (accumulated design shortcuts costing more over time), emphasizing the compounding-cost angle over Ousterhout's structural-diagnosis angle.

## When to use it
Use this three-symptom framework whenever evaluating whether a piece of code or a proposed design is "too complex" — rather than relying on a vague feeling, identify specifically which symptom (change amplification, cognitive load, unknown unknowns) is present and which cause (dependency, obscurity) is producing it, then target the fix at that specific cause.

## When NOT to use it
Don't use "complexity" as a catch-all criticism without being able to name the specific symptom and cause — an imprecise complaint can't be reliably acted on, and per this lesson's own framework, precision is exactly what makes the diagnosis useful.

## Key takeaways / mental model
When something about a codebase feels wrong, ask two questions in sequence: "which symptom is this — am I touching many places for one change, holding too much in my head, or discovering a dependency I didn't know existed?" and then "is the underlying cause a real dependency, obscurity, or both?" The answers point directly at which of this subject's later techniques actually applies.

## Self-check questions
1. Classify a real frustration you've had with a codebase using Ousterhout's three symptoms — was it change amplification, cognitive load, or an unknown unknown?
2. Explain the difference between a dependency and obscurity, and give an example of a dependency that is NOT obscure (well-documented, easy to find) versus one that is.
3. Why does the book argue complexity accumulates from many small decisions rather than one big one, and what does that imply about how to fight it?
4. Why are unknown unknowns considered the most dangerous of the three symptoms?

## References
- A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 2: "The Nature of Complexity" and Chapter 3: "Working Code Isn't Enough" (complexity-definition portions).
