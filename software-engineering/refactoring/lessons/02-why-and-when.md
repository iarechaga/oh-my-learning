---
id: refactoring/02
subject: refactoring
title: Why Refactor, and When
slug: why-and-when
status: drafted
mastery:
seniority: mid
source: Refactoring, 2nd ed. (Martin Fowler), Chapter 2
prerequisites: [refactoring/01]
created: 2026-08-10
updated: 2026-08-10
---

# Why Refactor, and When

## TL;DR
Refactor for a specific, immediate purpose tied to work you're already doing — most commonly "make the change I need to make easier before I make it" — not as an open-ended, unscheduled quality initiative. Fowler's "Rule of Three" and the "opportunistic refactoring" habit (clean up whatever you touch, per `pragmatic-programmer/02`'s boy-scout framing) give concrete triggers for when refactoring actually earns its cost.

## The idea
`philosophy-of-software-design/02` already argued strategic design investment pays back within months, but that's a claim about a general posture, not a decision procedure for any *specific* moment. This chapter gets concrete: refactoring, done as a scheduled, separate "quality improvement" initiative disconnected from any actual feature work, is a hard sell to justify and easy to deprioritize under pressure — Fowler's practical answer is to tie refactoring tightly to work already happening, so it never needs its own separate justification or its own separate time slot.

## How it works

### "Make the change easy, then make the easy change"
Fowler's own memorable framing (often attributed to Kent Beck) for the single most common, most justifiable reason to refactor: before implementing a feature that would be awkward given the code's *current* structure, first refactor the code into a shape where the feature is straightforward to add, *then* add it. The refactoring step is justified entirely by the feature it enables — it's not an abstract quality improvement, it's a concrete precondition for the actual task at hand.

**Worked example.** Adding a new discount type to an order-processing system whose discount logic is currently one large, nested `if`/`elif` chain hardcoded for two existing discount types. Rather than jamming a third `elif` branch into the already-strained conditional (making it worse, and violating `code-complete/11`'s complexity-metric caution), first refactor the conditional into a polymorphic Strategy structure (`design-patterns/09`) — a refactoring justified purely by the fact that it makes adding the third discount type trivial afterward, rather than by any abstract "this code should be cleaner" argument.

### Rule of Three
A specific, concrete threshold for when duplication (or a similar pattern) justifies refactoring: the first time you see something, just do it. The second time you see something similar, note the duplication but resist refactoring yet — you don't yet have enough evidence about the actual shape of the abstraction. The third time, refactor — by now you have enough real, concrete examples to design a genuinely well-fitting abstraction, rather than guessing at one prematurely (echoing `pragmatic-programmer/05`'s reversibility caution against speculative generality).

### Opportunistic refactoring — clean up whatever you touch
Directly connecting to `pragmatic-programmer/02`'s "no broken windows" boy-scout principle: whenever you're already in a piece of code for any reason (adding a feature, fixing a bug, even just reading it to understand something else), take the opportunity to make small, safe improvements to whatever you notice nearby, even if it's unrelated to your primary task — a confusing name, a small piece of duplication, a slightly-too-long function. This is deliberately opposed to scheduling refactoring as a separate, dedicated activity: opportunistic refactoring piggybacks on work that's happening anyway, so it never competes for its own dedicated time slot that stakeholders might reasonably question or deprioritize.

**A specific discipline for opportunistic refactoring**: keep it genuinely small and low-risk, and keep it in a *separate commit* from your primary change (echoing `refactoring/01`'s "different hats" principle) — an opportunistic cleanup that balloons into a large, unrelated restructuring, bundled into the same commit as your actual bug fix, makes the change harder to review and riskier to revert if something goes wrong, defeating the purpose of doing it opportunistically and safely in the first place.

### Refactoring to understand code
A distinct, less obvious trigger: sometimes the *reason* to refactor is that the current structure is hard to understand, and the act of refactoring (renaming things as you figure out what they actually mean, extracting pieces as you identify their real boundaries) is itself how you build understanding of unfamiliar or legacy code — the refactoring's value here isn't primarily the resulting code quality, it's the comprehension gained through the process of doing it, which then pays off directly when you make the actual change you came to make.

### When NOT to refactor
Fowler is explicit that refactoring has real costs (time, risk of introducing a subtle bug even with tests, review overhead) and isn't free — a few specific "don't bother" signals worth naming:
- **Code you're not touching and don't need to understand.** If a module works, is never going to be modified, and you have no reason to read its internals, refactoring it provides no benefit to anyone — it's pure cost.
- **Code about to be replaced or deleted entirely.** Refactoring something scheduled for deletion or a full rewrite is wasted effort — see `refactoring/12`'s discussion of refactoring versus a larger architectural change.
- **When you don't have (and can't quickly get) a safety net.** Refactoring without tests to verify behavior preservation is a fundamentally different, riskier activity — see `refactoring/03` and `software-engineering/legacy-code` for what to do first in that case, rather than refactoring blind.

## Pros
- Tying refactoring to concrete, already-justified work (an upcoming feature, a bug investigation) removes the need to separately justify "quality time" to stakeholders who might otherwise question it.
- The Rule of Three prevents premature, speculative abstraction by requiring real evidence (three genuine occurrences) before committing to a specific generalized design.
- Opportunistic refactoring, kept small and separately committed, compounds over time (echoing `pragmatic-programmer/02`'s broken-windows-prevention argument) without ever requiring a dedicated "refactoring sprint" that's vulnerable to being deprioritized.

## Cons
- Purely opportunistic, feature-driven refactoring can leave genuinely important but rarely-touched parts of a codebase permanently un-refactored, since nothing ever triggers working on them.
- The Rule of Three's "wait for the third occurrence" discipline occasionally means living with mild duplication for longer than feels comfortable, which requires some tolerance for short-term imperfection in exchange for a better-informed eventual abstraction.
- Determining whether a specific refactoring is genuinely "in service of" an upcoming change, versus a tangent that should be deferred, requires judgment that's easy to get wrong under time pressure (rationalizing a much larger cleanup than the actual task needs).

## Alternatives
- **Dedicated refactoring/tech-debt sprints** — an explicit, scheduled alternative to opportunistic refactoring; the chapter (and `pragmatic-programmer/02`'s broken-windows argument) both suggest these tend to be the first thing cut under continued delivery pressure, making them a less reliable long-term strategy than the tightly-coupled, opportunistic approach this lesson favors.
- **A formal technical-debt backlog with prioritized tickets** — makes deferred refactoring work visible and trackable (echoing `pragmatic-programmer/02`'s "board it up" discipline), a reasonable complement to opportunistic refactoring for larger items that don't fit naturally into any single feature's scope.
- **Continuous, small-scale refactoring enforced by team norms** (`pragmatic-programmer/15`) — treats refactoring less as an individually-triggered activity and more as an always-on cultural expectation, which this lesson's opportunistic approach is really one concrete instantiation of.

## When to use it
Refactor when it makes an upcoming change genuinely easier, when you've hit a genuine third occurrence of a repeated pattern, when refactoring itself is how you're building understanding of unfamiliar code you need to change, or opportunistically (in small, separately-committed increments) whenever you're already touching nearby code for another reason.

## When NOT to use it
Don't refactor code you're not touching, don't need to understand, and have no other reason to be near. Don't refactor code that's about to be deleted or entirely rewritten. Don't refactor without a safety net (tests) in place first — get the safety net in place as its own first step (see `refactoring/03`, `software-engineering/legacy-code`) rather than refactoring blind.

## Key takeaways / mental model
Ask, before refactoring: "does this refactoring make a change I'm already committed to easier, or am I refactoring for its own abstract sake with no concrete, near-term payoff in view?" The former is almost always justified; the latter needs a much stronger case.

## Self-check questions
1. Using the discount-type example, explain why refactoring the conditional into a Strategy pattern is justified by the upcoming feature rather than by an abstract quality argument.
2. Walk through the Rule of Three using a real or hypothetical example: what would you do on the first, second, and third occurrence of a similar pattern?
3. Why does the book recommend keeping opportunistic refactoring changes in a separate commit from your primary change?
4. Describe a piece of code you've encountered that was correctly left un-refactored, according to this lesson's "when not to" criteria. What made refactoring it not worth doing?

## References
- Refactoring: Improving the Design of Existing Code, 2nd ed. (Martin Fowler), Chapter 2: "Principles in Refactoring" (Why Should We Refactor?; When Should We Refactor? sections).
