---
id: how-to-measure-anything/04
subject: how-to-measure-anything
title: "Decomposition: breaking fuzzy variables into observable parts"
slug: decomposition-of-variables
status: drafted
mastery:
seniority: senior
source: How to Measure Anything (Douglas W. Hubbard), Chapter 5, Chapter 8
prerequisites: [how-to-measure-anything/03]
created: 2026-08-10
updated: 2026-08-10
---

# Decomposition: breaking fuzzy variables into observable parts

## TL;DR
When a quantity feels too fuzzy to estimate directly, break it into smaller sub-quantities that are individually easier to estimate or observe, then recombine them mathematically. Decomposition almost always narrows your final uncertainty, because errors in independent sub-estimates partially cancel out rather than compounding the way a single wild guess does.

## The idea
Direct estimation of a large, fuzzy quantity ("how much value would improving our CI pipeline speed create this year?") produces very wide, poorly-calibrated ranges because the human mind doesn't have a good intuitive model for a number that large and abstract. Fermi famously estimated "how many piano tuners are in Chicago" not by guessing the answer directly, but by breaking it into a chain of smaller quantities he *could* reason about: population of Chicago, households per piano, pianos tuned per tuner per year, and so on — then multiplying them back together. Hubbard applies this same Fermi-decomposition discipline to business and engineering quantities. The reason this works statistically, not just intuitively, is that when you decompose a quantity into several roughly-independent sub-estimates and each sub-estimate has some error, the errors tend to partially offset each other when recombined (some sub-estimates land high, some land low), whereas a single direct guess has all its error in one place with nothing to offset it.

## How it works

### The decomposition procedure
1. **Identify the quantity you actually need** (tie it to a decision — see `how-to-measure-anything/05`).
2. **Express it as a formula** of smaller, more observable or more easily estimable quantities — usually a product, sum, or ratio.
3. **Estimate or measure each sub-quantity independently**, using calibrated ranges (`how-to-measure-anything/03`) or real data (`how-to-measure-anything/06`) where available.
4. **Recombine** the sub-estimates through the formula, propagating uncertainty (this is usually done with Monte Carlo simulation once ranges are involved — see `how-to-measure-anything/07`).
5. **Sanity-check** the recombined result against any direct intuition you have; large mismatches are a signal one of the sub-estimates or the formula itself is wrong.

### Worked example: value of improving CI pipeline speed
Direct question: "what's the annual value of cutting our CI pipeline from 25 minutes to 8 minutes?" Estimated directly, most engineers would produce a very wide, low-confidence guess ("somewhere between nothing and a lot"). Decompose instead:

- **Number of CI runs per day** — pull from CI system logs: measured directly, 340 runs/day (not an estimate — real data).
- **Time saved per run** — 25 min - 8 min = 17 minutes saved per run (measured/assumed from the proposed change).
- **Fraction of that wait time that is actively blocking an engineer** (vs. them context-switching to other work) — this is the fuzziest sub-quantity; calibrated estimate from 4 engineers surveyed: 90% CI of [30%, 60%], center ~45%.
- **Fully-loaded engineer cost per minute** — from HR/finance data: average fully-loaded cost $185,000/year / (220 working days x 8 hours x 60 min) ≈ $1.75/minute (measured, not estimated).
- **Recombine:** 340 runs/day x 17 min saved x 45% blocking fraction x $1.75/min x 220 working days/year ≈ 340 x 17 x 0.45 x 1.75 x 220 ≈ **$1,001,000/year** in recovered engineer time, with a 90% CI (propagating the [30%,60%] blocking-fraction uncertainty through the rest, which are comparatively firm numbers) of roughly **$670,000 to $1,340,000/year**.

Compare this to a direct guess of "probably worth a few hundred thousand a year, maybe" — decomposition turned a vague intuition into a defensible range built from mostly-measured components, with only one genuinely fuzzy input (the blocking fraction) isolated and explicitly flagged as the place further measurement would help most (this connects to value of information in `how-to-measure-anything/09`: that blocking-fraction variable is exactly the one worth measuring better, e.g., by instrumenting actual engineer activity during CI waits, rather than surveying).

### Choosing the right decomposition (and avoiding a bad one)
Not every decomposition helps. A good decomposition satisfies two properties:
- **The sub-quantities are individually easier to estimate or measure than the whole** — if a sub-quantity is just as fuzzy as the original, you haven't gained anything, you've just relocated the fuzziness.
- **The sub-quantities are reasonably independent** — if two sub-estimates are driven by the same underlying uncertainty (e.g., "adoption rate" and "engagement rate" both really depend on "how good is the UX," and you elicit them from the same uninformed source), their errors will move together rather than cancel, and you lose the error-cancellation benefit that makes decomposition powerful in the first place.

A bad decomposition example: breaking "developer productivity gain from switching to language X" into "gain per developer x number of developers," where "gain per developer" is *just as hard to estimate directly* as the original quantity was — this decomposition adds a multiplication step without adding any real information.

### Decomposition also works for events and probabilities, not just quantities
The same logic applies to probability estimates. "What's the probability this migration causes a customer-visible outage?" decomposes into: P(a breaking bug ships) x P(it isn't caught in staging) x P(it isn't caught by canary/rollback before broad impact). Estimating each conditional probability separately (each grounded in something more concrete — staging catch rate from the last 20 releases, canary rollback speed from incident history) is far more tractable than eyeballing the compound probability directly, and it also tells you which stage of the pipeline is the weakest link worth investing in.

## Pros
- Converts an intractable, low-confidence direct guess into a set of smaller, more tractable, often partially-measurable sub-estimates.
- Frequently reveals that some sub-quantities are already known or cheaply measurable (as in the CI example, run counts and cost-per-minute), leaving only a small, identifiable, genuinely uncertain residual to actually estimate.
- Surfaces exactly which sub-quantity drives most of the remaining uncertainty, directly informing where further measurement effort (lesson 09) should go.

## Cons
- Takes more upfront modeling effort than a single gut-check number, which can feel like overkill for low-stakes decisions.
- A flawed formula (wrong relationship between sub-quantities, or double-counting) can produce a confidently-wrong final number that looks more credible than a guess precisely because it's decomposed — false rigor is a real risk.
- Decomposing into non-independent sub-quantities gives a false sense of precision without the real error-cancellation benefit, as discussed above.

## Alternatives
- **Direct calibrated estimation** (`how-to-measure-anything/03`) of the whole quantity — faster, and sometimes sufficient when the quantity is already something the estimator has good intuition about (e.g., an experienced engineer estimating a familiar type of task).
- **Reference class / analogy-based estimation** — instead of decomposing structurally, find a comparable past case and scale it ("the last CI speed-up project saved about $700k, ours is similar in scope") — faster, but only works when a good analog exists.
- **Pure statistical modeling from historical data** — when enough historical data exists (e.g., a large dataset of past project outcomes), regression or other statistical models can estimate the quantity directly from data rather than a manually constructed decomposition formula; more rigorous but requires a dataset that often doesn't exist for one-off decisions.

## When to use it
When a quantity feels too large, abstract, or unfamiliar to estimate directly with any confidence — most "value of X initiative" and "cost of Y risk" business-case questions engineering leaders face. Especially valuable when some of the sub-quantities are things you can pull from existing systems (logs, ticketing, finance data) rather than guess.

## When NOT to use it
Skip decomposition when the direct quantity is already something the estimator has strong, well-calibrated intuition about (an experienced team lead estimating a familiar sprint's hours) — decomposing a well-understood quantity adds process without adding accuracy. Also avoid it when you can't find sub-quantities that are meaningfully more independent or more tractable than the original — in that case you're just adding arithmetic, not information.

## Key takeaways / mental model
When a number feels too big or fuzzy to guess, don't guess harder — break it into a formula of smaller pieces, measure or estimate each piece on its own terms, and multiply/sum them back together. The goal isn't more precision on paper; it's isolating which piece is genuinely uncertain so you know exactly where to spend further measurement effort.

## Self-check questions
1. Take a fuzzy value-estimation question from your own work ("what's the value of migrating to service X," "what's the cost of our current on-call load") and decompose it into at least three sub-quantities. Which of those sub-quantities can you actually pull from existing data rather than guess?
2. Explain why decomposing into non-independent sub-quantities undermines the error-cancellation benefit of decomposition. Give an example of two sub-quantities that would be too correlated to decompose usefully.
3. Walk through the CI pipeline worked example above and identify: which inputs were measured, which were estimated, and which single input contributed most to the final range's width.
4. Describe a decomposition you've seen (in your work or elsewhere) that added false precision rather than real insight. What made it a bad decomposition?

## References
- How to Measure Anything: Finding the Value of Intangibles in Business (Douglas W. Hubbard), Chapter 5: "Calibrated Estimates," and Chapter 8: "The Transition: From What to Measure to How to Measure."
