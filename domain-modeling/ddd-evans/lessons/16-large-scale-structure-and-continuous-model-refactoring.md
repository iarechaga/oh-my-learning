---
id: ddd-evans/16
subject: ddd-evans
title: Large-scale structure and continuous model refactoring
slug: large-scale-structure-and-continuous-model-refactoring
status: drafted
mastery:
seniority: staff
source: Domain-Driven Design (Eric Evans), Part III-IV, Chapters 12, 16
prerequisites: [ddd-evans/13, ddd-evans/14, ddd-evans/15]
created: 2026-08-10
updated: 2026-08-10
---

# Large-scale structure and continuous model refactoring

## TL;DR
Large-scale structure gives an organization a shared, coarse-grained vocabulary for how the whole system (across many bounded contexts) fits together — like a small set of named "responsibility layers" or system-wide roles — while continuous refactoring toward deeper insight is the ongoing discipline of revising models, at every scale, as the team's domain understanding genuinely improves, rather than treating any model as finished.

## The idea
A single bounded context (`ddd-evans/14`) has its own coherent model, but a large system made of dozens of contexts still needs *some* way for people to orient themselves at a higher level than "read every context's individual model." Without any system-wide structure, a large system feels like an undifferentiated pile of contexts with no overall shape — nobody can answer "roughly where would functionality like X live?" without deep, specific knowledge of every part.

Large-scale structure addresses this with lightweight, high-level organizing patterns applied *across* contexts — not a rigid, imposed hierarchy, but a small set of named roles or layers, applied loosely, that give a newcomer or an architect a rough mental map of a large system without needing to understand every context's internals. Evans is careful that this must stay lightweight: an overly rigid large-scale structure imposed too early or too strictly becomes its own straightjacket, actively fighting the natural, model-driven boundaries that should emerge from actual domain understanding (per `ddd-evans/14`) rather than from an architect's a priori diagram.

Continuous refactoring toward deeper insight is the underlying discipline that makes all of this sustainable over a system's life: models — at the class level, the aggregate level, the bounded-context level, and the large-scale-structure level — are never "done." As the team's understanding of the domain deepens (through more knowledge crunching, `ddd-evans/01`, and more experience with the system in production), earlier modeling decisions that seemed correct at the time are revisited and improved, even when that means real, sometimes painful, restructuring work.

## How it works

### Example large-scale structure pattern: Evolving Order / responsibility layers
One structure Evans describes is dividing a system into a small number of broad conceptual "responsibility layers" that most objects can be roughly assigned to — for instance, separating a system into layers like *Decision-support* (analytics, reporting, informing human judgment), *Policy* (rules governing what's allowed), *Operations* (day-to-day execution), and *Potential* (raw capability/infrastructure). This isn't a technical layering like `ddd-evans/03`'s presentation/application/domain/infrastructure split — it's a domain-level, coarse structure describing what *kind of responsibility* a given part of the domain holds, useful for orienting a newcomer ("oh, this bounded context is mostly Operations-layer, that one's mostly Policy") without prescribing implementation details.

### Worked example: applying a lightweight structure to a logistics system
A logistics company's many bounded contexts (route optimization, driver scheduling, billing, customer notifications, warehouse management) could be loosely mapped: route optimization and driver scheduling as *Operations* (day-to-day execution of the core business); a compliance-rules context as *Policy* (governing what routes/schedules are even allowed); a business-intelligence context as *Decision-support* (informing strategic choices, not executing them); and generic infrastructure services as *Potential*. This mapping doesn't change any single context's internal model — it gives the wider organization (including people outside engineering) a shared, coarse vocabulary for talking about "where does this initiative mostly live" without requiring everyone to understand fifteen bounded contexts' internals in detail.

### The danger of over-applying large-scale structure
A team once imposed a strict five-layer large-scale structure on their entire system before any bounded contexts had actually been identified through real knowledge crunching — architects drew the layers first, then tried to force every new feature to fit neatly into exactly one predetermined layer. This inverted the proper order: large-scale structure is meant to be a lightweight, descriptive summary discovered *from* well-modeled bounded contexts, not a rigid, prescriptive scaffold imposed *before* those contexts exist. Features that genuinely spanned two layers were awkwardly contorted to fit one, producing worse models than if the structure had simply been left loose or applied more sparingly, exactly the "straightjacket" failure mode the book warns about.

### Continuous refactoring toward deeper insight
The book's closing methodological point, spanning every scale from a single value object up through bounded contexts and large-scale structure: a model is a hypothesis, continuously tested against real use and real conversation with domain experts, and revised — sometimes substantially — as understanding deepens. This is not the same as ordinary refactoring for code cleanliness; it's refactoring driven specifically by a *new domain insight*, often surfaced by a difficulty in extending the current model, a domain expert's offhand correction, or a bug that turns out to reveal a conceptual gap rather than just an implementation slip.

**Worked example — a deep model refactoring triggered by insight, not by a bug report:**
An insurance system originally modeled `Policy` as having a single `status` field cycling through `Active -> Lapsed -> Cancelled`. Over time, handling edge cases (a policy that's technically active but in a grace period after a missed payment; a policy cancelled by the insurer versus voluntarily by the customer, which have different legal and financial consequences) required an accumulating pile of extra boolean flags and special-case conditionals layered on top of the simple status field. Eventually a domain expert, asked to clarify one of these edge cases directly, revealed that what the team had been treating as "special cases of Active" were actually distinct, named domain concepts the business already had precise language for: `GracePeriod`, `InsurerCancellation`, `VoluntaryCancellation`. Refactoring `Policy` to model these explicitly (rather than as flags bolted onto a generic status field) wasn't a bug fix — it was a genuine deepening of the model's insight, discovered through the accumulated friction of forcing real distinctions into an oversimplified structure, exactly the process this lesson describes as the engine of long-term model quality. This same story — friction with the current model surfacing a hidden, more precise domain concept — echoes the "Enrollment" example from `ddd-evans/11` and the "Leg" example from `ddd-evans/01`; it's the same underlying discipline recurring at every scale of the model, from a single association up through an entire aggregate's state machine.

### Making room for continuous refactoring organizationally
This discipline only survives if a team's process actually allows for it — a roadmap with no slack for "we discovered our model of X was subtly wrong and it's worth fixing now" will accumulate exactly the kind of awkward, bolted-on special-casing the `Policy` example shows, because there's never officially sanctioned time to act on a deepened insight when it appears. The book's implicit organizational claim is that protecting this capacity, especially for the core domain (`ddd-evans/13`), is not gold-plating — it's the mechanism by which a model's quality compounds over a system's life instead of merely degrading under accumulating special cases.

## Pros
- Large-scale structure gives a big system a shared, coarse orientation vocabulary without forcing premature or overly rigid decisions about individual contexts' internals.
- Continuous refactoring toward deeper insight keeps a model's quality compounding over the system's life, rather than accumulating awkward special-casing indefinitely.
- Both practices reinforce the book's throughline: the model is a living hypothesis under continuous test, not an artifact finished once and then merely implemented.

## Cons
- Large-scale structure imposed too early or too rigidly actively fights natural, insight-driven model evolution, producing worse designs than no structure at all — a real and common failure mode.
- Continuous refactoring toward deeper insight requires organizational slack and trust that many delivery-pressured teams simply don't protect, making the discipline aspirational rather than practiced in many real organizations.
- Distinguishing "this refactor reflects genuine deepened domain insight" from "this refactor is just architect-driven taste or fashion" requires real judgment and can be a source of legitimate, hard-to-resolve disagreement on a team.

## Alternatives
- **No system-wide structure at all** — let each bounded context stand alone with no shared coarse vocabulary; simpler and avoids the straightjacket risk entirely, but leaves large systems with no shared orientation map, which becomes a real onboarding and cross-team-communication cost as the system grows.
- **Rigid, upfront enterprise architecture layering** — impose a strict, detailed layering model across the whole organization before contexts are understood; the book explicitly warns this produces the over-constrained failure mode described above rather than the lightweight orientation aid large-scale structure is meant to be.
- **Scheduled "model health" refactoring sprints** — a more process-driven way some teams try to protect capacity for continuous refactoring, setting aside dedicated time rather than relying on ad hoc opportunism; can work, but risks becoming disconnected from where genuine domain insight is actually accumulating if not tied to real discovery moments.

## When to use it
Apply a lightweight large-scale structure once a system has grown to enough bounded contexts that cross-context orientation has become a genuine, recurring problem — and always derive the structure from contexts that already exist and are reasonably well understood, never impose it in advance of that understanding. Protect capacity for continuous refactoring toward deeper insight on an ongoing basis, especially within the core domain (`ddd-evans/13`).

## When NOT to use it
Skip large-scale structure for a system small enough that a handful of bounded contexts are already easy to hold in mind without a coarser map — imposing one adds ceremony with no real orientation benefit at that scale.

## Key takeaways / mental model
Large-scale structure is a map drawn *after* the territory is understood, describing it loosely for newcomers — not a blueprint imposed *before* the territory exists. Continuous refactoring toward deeper insight is the recognition that "the model is correct now" is never a permanently true statement — protect the organizational capacity to act when a real, friction-driven insight surfaces, at every scale from a single value object up through the whole system's large-scale structure.

## Self-check questions
1. Why did imposing a strict five-layer structure before any bounded contexts existed produce worse outcomes than applying a loose structure after contexts were understood?
2. In the insurance `Policy` example, what specific friction (accumulating flags and special cases) signaled that a deeper model refactoring was needed, rather than just another patch?
3. What's the difference between ordinary code-cleanliness refactoring and "refactoring toward deeper insight" as this lesson describes it?
4. Why does the book connect protecting organizational slack for continuous refactoring specifically to the core domain (`ddd-evans/13`) rather than treating it as equally important everywhere?

## References
- Domain-Driven Design: Tackling Complexity in the Heart of Software (Eric Evans), Chapter 12: "Digging Deeper: How to Get Broader Applicability" (refactoring toward deeper insight) and Chapter 16: "Large-Scale Structure".
