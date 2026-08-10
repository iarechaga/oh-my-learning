---
id: refactoring/01
subject: refactoring
title: What Refactoring Is (and Is Not)
slug: what-refactoring-is
status: drafted
mastery:
seniority: junior
source: Refactoring, 2nd ed. (Martin Fowler), Chapter 1-2
prerequisites: [clean-code/01]
created: 2026-08-10
updated: 2026-08-10
---

# What Refactoring Is (and Is Not)

## TL;DR
Refactoring is a disciplined technique for restructuring existing code's internal design without changing its observable external behavior — applied in small, verifiable steps, each one individually safe enough that you could stop at any point without leaving the code broken. It is precisely not "rewriting," "cleaning up while also adding a feature," or "any code change that happens to improve things."

## The idea
The word "refactoring" gets used loosely in everyday conversation to mean almost any code improvement — but Fowler's book, and this subject, use it in a specific, narrower, technically precise sense that's worth pinning down exactly, because the precision is what makes refactoring *safe* and *disciplined* rather than just a vague aspiration to write better code.

**Fowler's definition, precisely:** refactoring is the process of changing a software system's internal structure without changing its observable, external behavior — done through a series of small, behavior-preserving transformations, each individually verified (via tests, per `refactoring/03`) before moving to the next. The two halves of this definition are both load-bearing: "changing internal structure" (not adding features, not fixing bugs — those are different activities) and "without changing external behavior" (verified, not assumed) are what separate genuine refactoring from a rewrite, a redesign, or an ordinary feature change that happens to touch a lot of code.

## How it works

### The two-hats metaphor
Fowler's own framing device: when working on code, you're always wearing one of two hats, and you should be able to say, at any given moment, which one you currently have on. **Adding function**: you're adding new capability, and the system's observable behavior *should* change as a result — you're not refactoring right now. **Refactoring**: you're restructuring, and the system's observable behavior must *not* change — if you also want to add a feature, that's a separate activity, done with the other hat on, ideally in a separate commit.

**Why the separation matters, concretely.** If you mix the two — refactoring a function's internals while simultaneously adding a new parameter that changes its behavior — and something breaks, you can no longer tell whether the break came from the restructuring (which should have been behavior-preserving and therefore safe) or from the new behavior (which was expected to change something, so a test failure there is potentially legitimate, not necessarily a refactoring bug). Keeping the hats separate means every test failure during a refactoring step is unambiguous: if behavior was supposed to stay identical and a test now fails, the refactoring step itself introduced a bug, full stop — there's no ambiguity to untangle.

### Small steps, each independently safe
Refactoring isn't one big transformation — it's a *sequence* of small, individually-verified transformations (many with their own names, cataloged throughout the rest of this subject: Extract Function, Rename Variable, Move Method). The discipline is that after *each* small step, the code should compile/run and all tests should pass — you should never be more than one small step away from a known-good state. This is what makes refactoring genuinely lower-risk than a rewrite: at any point, if you decide to stop, or if you discover the direction isn't working, you're standing on solid, tested ground, not in the middle of an incomplete, partially-broken transformation.

**Worked example.** Refactoring a large function into several smaller ones (echoing `clean-code/03`) is done as a sequence of individual Extract Function steps, one piece at a time, running tests after each extraction — not as one large, all-at-once rewrite of the function into its final decomposed form. If step 3 of 6 reveals a problem (an extracted piece turns out to need information not easily available at that call site), you can stop, back up to the last known-good state, and reconsider — because you never committed to the full transformation in one irreversible leap.

### Refactoring is not rewriting
A rewrite starts from the requirements/behavior and builds new code to satisfy them, typically discarding much of the old implementation. Refactoring starts from the *existing, working* code and transforms its structure incrementally, at every step preserving the exact behavior that was already there (bugs included, unless the bug fix is explicitly and separately called out as a *different* activity, not part of the refactoring itself). This is a deliberate, important distinction: refactoring does not fix bugs as a side effect — if you discover a bug while refactoring, the disciplined move is to note it, finish or pause the refactoring at a safe point, and address the bug as its own separate, hat-swapped activity, precisely so behavior-preservation stays a clean, verifiable guarantee throughout the refactoring itself.

### Why the discipline matters even though it can feel slower
A common objection: "isn't it faster to just rewrite this messy function from scratch, now that I understand what it should do?" Sometimes, yes — but the incremental, behavior-preserving discipline earns its keep specifically when the existing code's *actual* behavior (including undocumented edge cases nobody remembers, and possibly including latent bugs other code has come to silently depend on) is not fully known or trusted. A rewrite risks silently dropping or altering behavior nobody thought to specify because nobody fully audited it; a disciplined refactoring, verified step by step against the *existing* behavior (via tests), cannot silently drop anything, because each step is checked against what was already there, not against someone's possibly-incomplete mental model of what should be there.

## Pros
- Small, individually-verified steps mean you're never more than one step from a known-good state, dramatically lowering the risk of a large, all-at-once transformation.
- Separating "adding function" from "refactoring" (the two-hats discipline) makes every test failure during a refactoring step unambiguous — it's a refactoring bug, not a legitimate behavior change to investigate separately.
- Because each step preserves the code's actual, existing behavior (not a reconstructed mental model of what the behavior should be), refactoring is less likely than a rewrite to silently drop undocumented edge-case behavior other code depends on.

## Cons
- The discipline of truly small, individually-verified steps takes more patience and more moment-to-moment attention than either "just clean it up in one big pass" or a from-scratch rewrite — it's easy to skip steps under time pressure, at the cost of the safety guarantee.
- Refactoring genuinely depends on having tests (or some other reliable way to verify behavior is preserved) already in place — see `refactoring/03` and `software-engineering/legacy-code` for what to do when they don't exist yet.
- For code that's genuinely fundamentally wrong for its current requirements (not just poorly structured, but solving a problem that's since changed entirely), a rewrite may legitimately be the better choice — refactoring optimizes for preserving what's there, which isn't always the right optimization target.

## Alternatives
- **A full rewrite** — appropriate when the existing code's actual behavior is poorly understood, poorly trusted, or simply no longer the right behavior at all (requirements have moved on enough that "preserve current behavior" isn't even a useful goal) — see `refactoring/12`'s discussion of when refactoring versus a bigger architectural change is the right call.
- **Strangler fig pattern** (see `architecture/evolutionary-architectures`) — an architectural-scale alternative for gradually replacing a large system, running old and new in parallel and shifting traffic over time, rather than either a full rewrite or in-place refactoring of the existing codebase.
- **Leaving the code as-is** — sometimes the correct choice, when a piece of code is rarely touched, works correctly, and the cost of any restructuring (even disciplined refactoring) exceeds its benefit — see `refactoring/02`'s treatment of when refactoring is actually worth doing.

## When to use it
Use refactoring specifically when you need to change a codebase's internal structure while preserving its existing, trusted behavior — most commonly as a deliberate precursor to adding a feature more easily (`refactoring/02`), or as an ongoing discipline for keeping a frequently-changed codebase healthy over time.

## When NOT to use it
Don't call something "refactoring" if it also changes observable behavior — that's a feature change, a bug fix, or both, and should be treated (and reviewed, and tested) as such, separately from any genuine refactoring happening alongside it. Don't reach for incremental refactoring when the existing code's behavior is fundamentally wrong for current needs and a rewrite is genuinely the better-fitting tool.

## Key takeaways / mental model
Before starting any code change, ask: "which hat am I wearing right now — am I changing what this does, or how it's structured, but definitely not both at once?" And commit to the discipline that every individual refactoring step, verified against tests, leaves the code in a known-good, unchanged-behavior state before you take the next one.

## Self-check questions
1. Explain, in your own words, why mixing "adding function" and "refactoring" in the same change makes test failures ambiguous, using a concrete example.
2. Why does the book insist refactoring proceeds in small, individually-verified steps rather than one larger transformation? What specific risk does that discipline reduce?
3. Describe a situation where a full rewrite would genuinely be a better choice than incremental refactoring, and explain why.
4. If you discover a real bug while in the middle of a refactoring step, what's the disciplined way to handle it, according to this lesson?

## References
- Refactoring: Improving the Design of Existing Code, 2nd ed. (Martin Fowler), Chapter 1: "Refactoring: A First Example" and Chapter 2: "Principles in Refactoring".
