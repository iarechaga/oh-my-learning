---
id: philosophy-of-software-design/02
subject: philosophy-of-software-design
title: Working Code Is Not Enough (Strategic vs Tactical)
slug: strategic-vs-tactical
status: drafted
mastery:
seniority: senior
source: A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 3
prerequisites: [philosophy-of-software-design/01]
created: 2026-08-10
updated: 2026-08-10
---

# Working Code Is Not Enough (Strategic vs Tactical)

## TL;DR
Tactical programming optimizes for getting the current feature working as fast as possible; strategic programming treats good design as a first-class goal alongside working code, accepting slightly slower short-term progress in exchange for a codebase that stays fast to change. Ousterhout's empirical claim is specific and strong: the payoff from strategic investment is realized within *months*, not years — this isn't a long-term-only argument.

## The idea
This chapter names and sharpens a tension `pragmatic-programmer/01` and `clean-code/01` both gestured at, but Ousterhout draws the line more explicitly and defends a specific, falsifiable timeline claim. **Tactical programming**: the immediate goal is to make something work — a feature, a bug fix — and design quality is a secondary concern addressed "later" (often never). **Strategic programming**: investing time in good design is treated as being just as important as making the current thing work, on the premise that it's the only path to a system that stays easy to work in.

The chapter's most quotable, specific claim: tactical programming isn't even a good *short-term* strategy — the book's own data and experience suggest that a team investing roughly 10-20% of its time in design (strategic investment) pays that cost back within a few months, not years, because the compounding cost of skipped design decisions (echoing `philosophy-of-software-design/01`'s change amplification and unknown unknowns) accelerates faster than most engineers intuitively expect.

## How it works

### The "tactical tornado" — a specific, recognizable anti-pattern
Ousterhout names a specific archetype: an engineer who ships features at an impressively fast rate, is celebrated for velocity, and leaves behind a wake of design debt that *other* people (often quieter, less individually visible engineers) spend disproportionate time cleaning up after. The tactical tornado looks highly productive by any metric that only counts shipped features, while being a net negative for the team's overall velocity once the cleanup cost (borne by others, and therefore invisible in the tornado's own metrics) is properly attributed.

**Worked example.** An engineer ships a new reporting feature in two days by copy-pasting an existing report's logic and hardcoding a dozen values specific to the new report's requirements (echoing `pragmatic-programmer/03`'s impatient duplication). Measured narrowly ("did the feature ship, and how fast"), this looks like strong individual performance. Measured properly (accounting for the fact that a business-rule change three months later now requires updating a dozen near-duplicate report implementations, a task that would have taken one edit had the original logic been properly factored), the *actual* total cost attributable to that fast two-day delivery is far higher than it appeared — it just showed up on someone else's timeline, and often much later, making the causal link hard to trace back to the original decision.

### The specific, testable "months, not years" claim
Unlike some design-quality arguments that lean on abstract, hard-to-verify long-term claims, Ousterhout is specific: he argues the crossover point — where a strategically-designed system's velocity overtakes a tactically-built one's — happens within a matter of months for a typical, actively-developed project, not the multi-year horizon some engineers (and most short-term incentive structures) implicitly assume. This specificity matters practically: it directly counters the common objection "we can't afford to slow down for design, we need to ship now" by reframing the actual trade-off as "slightly slower this sprint, meaningfully faster within the quarter" rather than "slower now for a payoff so distant it might never arrive."

### Incremental, continuous investment — not a big upfront design phase
Directly connecting to `philosophy-of-software-design/01`'s point that complexity accumulates incrementally: strategic programming isn't about a big design phase before coding starts (echoing the Big-Design-Up-Front trap `pragmatic-programmer/05` warns against) — it's about consistently spending a modest, sustained fraction of *every* task's time on design quality, even when under deadline pressure, rather than treating design as a separate phase that gets cut first whenever a deadline tightens. The 10-20% figure isn't a one-time investment — it's a standing tax paid on every task, which is precisely what makes it sustainable rather than something to sacrifice under pressure.

### Recognizing which mode you (or your team) are actually in
A practical, checkable test the chapter implies: track, honestly, how often "we'll clean this up later" actually happens versus how often the "later" never arrives. If a team's actual behavior consistently defers design investment under any deadline pressure, and "later" cleanup is rare in practice, that team is tactical regardless of what it says about its values — strategic programming is defined by what actually happens under pressure, not by stated intentions when there's no pressure at all.

## Pros
- Reframes the design-quality debate around a specific, falsifiable timeline (months, not years), directly countering the most common objection to investing in design under deadline pressure.
- Naming the "tactical tornado" pattern makes an otherwise-invisible cost (individually fast, collectively expensive) visible and discussable in concrete terms.
- Treating strategic investment as continuous and incremental (not a big upfront phase) makes it sustainable rather than something that gets cut whenever pressure increases.

## Cons
- The "months, not years" claim, while more specific than most similar arguments, is still drawn from Ousterhout's own experience and isn't universally validated across every kind of project, team, or domain — genuinely short-lived projects may never reach the claimed crossover point at all.
- Correctly attributing the "tactical tornado" cost requires organizational visibility into who actually bears cleanup costs later, which many teams' metrics and incentive structures don't track — the pattern can be real and still go unrecognized for a long time.
- A rigid 10-20% design-investment rule, applied without judgment, could itself become a box-ticking ritual disconnected from whether design attention is actually being spent on the highest-leverage problems.

## Alternatives
- **Pure tactical programming, with periodic dedicated "cleanup" phases** — an explicit acknowledgment of tactical debt with scheduled repayment, which the chapter (and `pragmatic-programmer/02`'s broken-windows argument) both suggest tends to fail in practice, since cleanup phases are the first thing cut under continued pressure.
- **Fully deliberate technical-debt tracking and prioritization** — treating design shortcuts as explicitly logged, prioritized debt items rather than either ignoring them (pure tactical) or continuously preventing them (pure strategic) — a middle path some organizations adopt.
- **Time-boxed "spike then rebuild" workflows** (echoing `pragmatic-programmer/06`'s prototyping) — deliberately go fully tactical for an explicitly-scoped exploratory phase, then rebuild strategically once the design is actually understood, rather than mixing the two philosophies within a single piece of production code.

## When to use it
Apply strategic investment continuously, as a standing practice on every task, especially for code with a real expected lifespan and more than one future contributor. Recognize a "tactical tornado" pattern (celebrated fast shipping with a growing, someone-else's-problem cleanup trail) as a signal worth raising, even when the tornado's individual metrics look good.

## When NOT to use it
For genuinely short-lived, throwaway code (a prototype meant to be discarded per `pragmatic-programmer/06`, a one-off migration script), tactical programming is the *correct* choice — the payoff window strategic investment needs to materialize never arrives for code that won't exist long enough to benefit from it.

## Key takeaways / mental model
Ask, honestly, of your own recent work: "when deadline pressure hit, did design investment survive, or was it the first thing cut?" If it's consistently the first thing cut, you're tactical regardless of your stated values — and per this chapter's central claim, that's not even the faster path once you look past the current sprint.

## Self-check questions
1. Describe a "tactical tornado" pattern you've witnessed (or, honestly, been part of), and estimate — as best you can — where the deferred cost eventually showed up.
2. Why does the chapter's "months, not years" framing matter for winning a real argument about deadline trade-offs, compared to a vaguer "good design pays off long-term" claim?
3. Explain why strategic programming is described as continuous and incremental rather than a big upfront design phase, and connect this to `philosophy-of-software-design/01`'s claim about how complexity accumulates.
4. Under what circumstances is tactical programming actually the *correct* choice, not just an excusable shortcut?

## References
- A Philosophy of Software Design, 2nd ed. (John Ousterhout), Chapter 3: "Working Code Isn't Enough".
