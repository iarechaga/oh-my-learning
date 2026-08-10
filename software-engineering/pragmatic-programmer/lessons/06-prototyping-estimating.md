---
id: pragmatic-programmer/06
subject: pragmatic-programmer
title: Prototyping and Estimating
slug: prototyping-estimating
status: drafted
mastery:
seniority: mid
source: The Pragmatic Programmer (20th Anniversary ed., Hunt & Thomas), Chapter 2
prerequisites: [pragmatic-programmer/05]
created: 2026-08-10
updated: 2026-08-10
---

# Prototyping and Estimating

## TL;DR
Prototype to learn something specific and throw the code away; don't confuse a prototype with production code. Estimate by decomposing the work, stating assumptions explicitly, giving a range (not a false-precision single number), and tracking your own accuracy over time to calibrate future estimates.

## The idea
Two closely related pragmatic techniques for dealing with uncertainty *before* committing real engineering effort: prototyping resolves uncertainty about "will this approach even work," and estimating quantifies uncertainty about "how long/expensive will this take," so stakeholders can make informed trade-offs rather than get an artificially confident number that turns out to be fiction.

Both fail the same way when done badly: a prototype that quietly becomes production code carries all its shortcuts into shipped software; an estimate presented as a precise commitment ("14.5 days") rather than a probabilistic range misleads everyone into planning around false certainty.

## How it works

### Prototyping: answer one question, then delete the code
A good prototype targets a *specific* unresolved question — architecture feasibility, UI/UX flow, a performance assumption, a third-party API's actual behavior — and is built to answer only that question as cheaply as possible: hardcoded data instead of a real database, no error handling, no styling, throwaway scripts instead of maintainable modules.

The critical discipline: **the code is disposable.** The book is blunt that prototypes should be discarded, not "cleaned up into" production code, because a prototype's shortcuts (no error handling, no edge cases, no tests) are invisible debt once the prototype is dressed up and shipped — nobody remembers which corners were cut once the code looks finished.

**Worked example.** A team is unsure whether a client-side spreadsheet-like grid can render 100,000 rows without freezing the browser. Prototype: a single HTML file, hardcoded array of 100,000 fake rows, the bare minimum rendering logic (maybe virtualized scrolling, maybe not) — no auth, no API, no styling. Fifteen minutes with dev tools' performance profiler answers the real question: yes/no, and if no, by how much and what's the practical ceiling. The prototype is then deleted; the real grid component is built properly, informed by what was learned, but sharing zero lines with the throwaway.

Contrast with a **tracer bullet** (Lesson 05): a tracer bullet is the real skeleton, kept and extended; a prototype is scaffolding, built and torn down. Confusing the two — building "real" infrastructure quality into a prototype, or throwing away a tracer bullet's integration work — wastes effort in both directions.

### Estimating: decompose, assume explicitly, range instead of point
The book's estimating technique has three parts:
1. **Decompose the task** into pieces small enough that each piece's uncertainty is bounded — "build the feature" is unestimable; "write the migration, build the API endpoint, wire the UI, write tests, handle three known edge cases" is estimable piece by piece.
2. **State your assumptions out loud**, in writing, next to the estimate — "assumes the existing auth middleware already validates the token we need" or "assumes no new infra provisioning is required." When an assumption turns out false later, the estimate's failure has a traceable, defensible cause instead of looking like the estimator was simply wrong.
3. **Give a range, not a point estimate.** "3-5 days" communicates real uncertainty; "4 days" invites everyone (including your future self) to treat 4 as a guarantee. The width of the range should reflect your actual confidence — a well-understood task gets a narrow range, a risky/novel one gets a wide range, and that width is itself useful information to a planner.

**Worked example.** Estimating "add CSV export to the reports page":
- Decomposition: (a) determine which report data needs exporting and its shape, (b) build server-side CSV generation for that shape, (c) add a UI trigger/download flow, (d) handle large-report streaming so we don't OOM on a 500k-row export, (e) tests.
- Assumptions stated: "assumes reports are already computed as structured objects, not rendered HTML we'd need to scrape; assumes we don't need to support Excel-specific quirks, just RFC 4180 CSV."
- Range: (a) 0.5 day, (b) 1-2 days, (c) 0.5 day, (d) 1-3 days *— this is the risky, novel piece, hence the wide range — depends on whether existing report queries already stream or would need rework*, (e) 0.5-1 day. Total: **3.5-7 days**, with an explicit note that (d) is the swing factor to watch.

### Track your own calibration
The book recommends keeping a personal record of estimate vs. actual over many tasks. Most engineers are systematically biased in a consistent direction (usually optimistic, sometimes wildly so for unfamiliar work) — and that bias is a fixable, *measurable* multiplier once you track it, rather than a character flaw to feel bad about. If your estimates for backend tasks run 1.4x over actuals on average, multiply future backend estimates by 1.4 and you've converted a psychological blind spot into an engineering correction factor.

## Pros
- Prototyping surfaces feasibility and design problems for a fraction of the cost of discovering them mid-build.
- Range-based, assumption-labeled estimates are more honest and more useful for planning than false-precision numbers, and they protect the estimator when reality diverges from a stated assumption.
- Tracking calibration turns "I'm bad at estimating" into a correctable, quantified skill.

## Cons
- Throwaway-code discipline is hard to enforce under deadline pressure — "just ship the prototype, we don't have time to redo it" is a common and costly failure mode.
- Ranges and stated assumptions can be politically uncomfortable — some organizations pressure engineers for single numbers and treat ranges as evasiveness.
- Decomposition-based estimating still fails badly on tasks with a genuinely unknown unknown (the risky assumption you didn't even think to state), since you can't range something you didn't know to question.

## Alternatives
- **Story points / relative sizing (Agile estimation)** — estimate relative complexity instead of absolute time, deferring the time conversion to team velocity. Reduces the "false precision" problem differently, by never claiming a time unit at all until aggregated.
- **Spike tasks** — a time-boxed, Agile-flavored cousin of prototyping: "spend at most 1 day investigating X," which bounds the cost of the investigation itself, not just the eventual build.
- **No-estimate / flow-based delivery** — some teams (especially Kanban-influenced ones) skip task-level estimation entirely and manage via throughput/cycle-time metrics instead, useful when the overhead of estimating repeatedly outweighs its planning value.

## When to use it
Prototype whenever a real, specific technical or UX question is unresolved and cheap experimentation can answer it faster than debate or documentation research. Estimate with decomposition-plus-range whenever a stakeholder needs a planning input — but push back on a demand for a false-precision single number.

## When NOT to use it
Don't prototype when the path is already well-understood by the team (see Lesson 05's tracer-bullet guidance) — it's wasted motion. Don't produce a detailed decomposed estimate for a task so small that the estimating effort exceeds the task itself; a quick gut-check range is proportionate there.

## Key takeaways / mental model
Prototype to *learn*, and delete what you built to learn it. Estimate by breaking work down, writing down what you're assuming, and giving a range whose width honestly reflects your uncertainty — then track how your ranges perform over time so your calibration actually improves.

## Self-check questions
1. Describe a time a prototype "accidentally" became production code, and what problems that caused later.
2. Walk through decomposing an estimate for a task you've recently done, including at least one explicitly stated assumption.
3. Why is a range more useful to a planner than a single number, even though a single number "feels" more decisive?
4. If your personal calibration data showed your estimates for unfamiliar-tech tasks run 2x over actuals, how would you use that going forward?

## References
- The Pragmatic Programmer, 20th Anniversary Edition (David Thomas & Andrew Hunt), Chapter 2: "A Pragmatic Approach" (Prototypes and Post-it Notes; Estimating sections).
