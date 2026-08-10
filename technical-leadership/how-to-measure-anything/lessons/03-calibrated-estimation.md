---
id: how-to-measure-anything/03
subject: how-to-measure-anything
title: Calibrated estimation and confidence intervals
slug: calibrated-estimation
status: drafted
mastery:
seniority: senior
source: How to Measure Anything (Douglas W. Hubbard), Chapter 5
prerequisites: [how-to-measure-anything/02]
created: 2026-08-10
updated: 2026-08-10
---

# Calibrated estimation and confidence intervals

## TL;DR
A calibrated estimator gives ranges such that, across many estimates, their stated confidence level actually matches reality — a 90% confidence interval should contain the true value about 90% of the time. Most people are wildly overconfident by default (their "90% CI" is right only 40-60% of the time), but calibration is a trainable skill, not an innate trait.

## The idea
When an engineer says "I'm 90% confident this migration takes between 3 and 5 weeks," that statement is testable: if we collected 100 such 90% estimates from that person across different tasks, about 90 of the true outcomes should fall inside their stated ranges. In practice, when Hubbard (and independently, decades of psychological research: Tversky, Kahneman, Lichtenstein, Fischhoff) tested this, most untrained people's "90% CI" ranges only contain the true answer 40-60% of the time — they are overconfident, stating ranges far too narrow for the confidence level they claim. This matters enormously for engineering estimation: a "90% confident" sprint estimate that's actually calibrated at 45% means the team is systematically blindsided by overruns, not because estimation is impossible, but because the estimators were never calibrated. The good news, replicated across many studies, is that calibration training reliably improves this skill within a few hours, and it transfers across domains once learned — it's a general skill in expressing genuine uncertainty honestly, not domain expertise.

## How it works

### The calibration test
Ask an estimator a series of trivia questions with a numeric or true/false answer (e.g., "In what year was the transistor invented? Give a range you're 90% confident contains the true year.") across ~20-30 questions from varied domains. A perfectly calibrated person gets about 90% of their ranges containing the true answer, and about 90% of their true/false 90%-confidence statements correct. Score people, then run calibration training (below), then re-test — scores reliably move toward true calibration.

### Calibration training techniques
Hubbard describes several specific techniques that work:
- **Equivalent bet test.** For a range estimate, ask: "would you rather bet on your stated range containing the true value, or spin a wheel with a 90% chance of winning the same prize?" If you'd take the wheel over your own range, your range is too narrow — widen it until you're truly indifferent between the two bets. This converts a fuzzy feeling of confidence into a comparison against a known, calibrated reference (the wheel), which is much easier for people to reason about honestly.
- **Anchor and reconsider.** State an initial range, then explicitly ask "what would have to be true for the real answer to be *outside* this range, on the low end? On the high end?" Actively imagining a scenario that breaks your range (e.g., "the migration takes only 1 week if we just proxy through the old system instead of rewriting" or "it takes 12 weeks if the auth service turns out to have undocumented dependencies") surfaces plausible extremes that a first-pass estimate typically misses, and pushes the range wider and more honest.
- **Decompose before estimating** (developed fully in `how-to-measure-anything/04`) — estimating sub-components separately, each with its own calibrated range, and combining them, tends to produce better-calibrated totals than estimating the whole thing in one leap.
- **Track your own track record.** Estimators who log their stated ranges against actual outcomes over time and review the log develop calibration faster than those who estimate once and move on — the feedback loop is what trains the skill.

### Worked example: calibrating a story-point-to-hours estimate
A senior engineer is asked, "how many engineer-hours will it take to migrate the payments service off the legacy queue?" Their gut answer: "about 80 hours." Applying calibration:
- **Equivalent bet test:** "Would you bet $100 on the true value being between 70 and 90 hours, versus a 90%-odds wheel spin for the same $100?" The engineer hesitates — they'd take the wheel. That signals the range [70, 90] is too narrow for 90% confidence.
- **Widen and re-test:** they widen to [40, 200] hours. Now the bet feels roughly equivalent to the wheel — they've reached genuine 90% confidence.
- **Anchor and reconsider, low end:** "What would make it only 40 hours?" — if the new queue client is a drop-in replacement with no schema changes, and there's an existing internal library for it. Plausible, so 40 stays as a reasonable low bound.
- **Anchor and reconsider, high end:** "What would push it past 200?" — if the legacy queue turns out to have three undocumented downstream consumers that break silently, requiring a phased dual-write rollout. Also plausible — so the range should probably extend even higher, to maybe 280.
Final calibrated range: 90% CI of [40, 280] hours. This is a far cry from the confident-sounding but poorly-calibrated "80 hours" the engineer started with — and it is far more useful input to a Monte Carlo model (`how-to-measure-anything/07`) or a go/no-go decision, because it honestly represents what the estimator actually knows and doesn't know.

### Reading and using a confidence interval correctly
A 90% CI of [40, 280] hours does **not** mean "40 to 280 hours, uniformly likely." It typically means values near the center (roughly 100-150) are more probable than values near the edges, and the true value has a 5% chance of falling below 40 and a 5% chance of falling above 280. This distinction matters when the interval feeds into further calculations (e.g., Monte Carlo simulation in `how-to-measure-anything/07`), where the *shape* of the distribution (often modeled as lognormal for time/cost estimates, since they're bounded below by zero and can have a long right tail) matters, not just its endpoints.

## Pros
- Converts vague confidence ("pretty sure," "fairly confident") into an falsifiable, trackable number that can be tested and improved over time.
- Well-calibrated ranges are dramatically more useful decision inputs than false-precision point estimates, because they honestly convey what is and isn't known.
- The skill transfers: someone calibrated on trivia questions is measurably better calibrated on work estimates too, so training is a one-time organizational investment with broad payoff.

## Cons
- Calibration training takes real time (Hubbard-style workshops run several hours) and requires people to sit with the discomfort of being shown their own overconfidence.
- Ranges are a harder sell than point numbers to stakeholders and executives who want a single number for a slide or a commitment — requires deliberate communication (e.g., "P50/P90" framing) to land well.
- Calibration can still be undermined by systematic organizational incentives (e.g., padding estimates to avoid blame, or sandbagging to look like a hero later) — calibration training fixes the honesty of the *probability judgment*, not incentive-driven distortion of the *stated* number.

## Alternatives
- **Three-point estimation (PERT: optimistic/most-likely/pessimistic)** — a lighter-weight structured alternative common in project management; faster to teach but doesn't include the explicit calibration-testing feedback loop, so it's prone to the same overconfidence bias if the three points aren't elicited carefully.
- **Reference class forecasting** — instead of (or alongside) subjective calibrated ranges, look at the actual outcome distribution of similar past projects ("the last 8 migrations of this type took between 60 and 340 hours") and anchor on that; often more accurate than pure expert judgment alone, especially for well-populated reference classes, and pairs well with calibrated estimation as a sanity check.
- **Delphi method** — aggregate multiple experts' calibrated estimates anonymously across rounds, converging on a group range; reduces individual bias and anchoring but is slower and more process-heavy than a single calibrated estimator.

## When to use it
Any time a number is needed for a decision and no hard data exists yet — sprint/project estimates, cost projections, risk assessments, or any input to a Monte Carlo model (`how-to-measure-anything/07`). Especially valuable before a big, hard-to-reverse technical bet, where an honest range (not false precision) should drive the go/no-go call.

## When NOT to use it
Don't use subjective calibrated estimation where real historical or measured data is cheaply available — pulling actual query logs, deployment histories, or incident data is a stronger measurement than even a well-calibrated guess, and should be preferred (see `how-to-measure-anything/06` on sampling). Also skip formal calibration ritual for trivial, low-stakes estimates where the cost of the exercise exceeds any decision value.

## Key takeaways / mental model
An estimate is only useful if its stated confidence is honest. Before trusting any "90% confident" range — your own or someone else's — run the equivalent-bet test mentally: would you actually take a 90%-odds wheel spin over betting on that range? If not, the range is too narrow, and the estimator (possibly you) is not yet calibrated.

## Self-check questions
1. State a 90% confidence range for something you'll need to estimate this week (a task's hours, a metric's next value). Apply the equivalent-bet test to it — does it hold up, or is it too narrow?
2. Explain why a "90% confident" estimate that turns out right only 50% of the time across many trials is a calibration failure, not bad luck.
3. Your team lead gives a single-number estimate ("this will take 3 weeks") for a project with real technical unknowns. What two calibration questions would you ask them to surface a more honest range?
4. Why does decomposing an estimate into parts (previewed here, covered fully in lesson 04) tend to produce better-calibrated totals than estimating the whole in one leap?

## References
- How to Measure Anything: Finding the Value of Intangibles in Business (Douglas W. Hubbard), Chapter 5: "Calibrated Estimates: How Much Do You Know Now?"
