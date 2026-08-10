---
id: how-to-measure-anything/07
subject: how-to-measure-anything
title: Monte Carlo simulation for decision uncertainty
slug: monte-carlo-simulation
status: drafted
mastery:
seniority: staff
source: How to Measure Anything (Douglas W. Hubbard), Chapter 6, Chapter 10
prerequisites: [how-to-measure-anything/03, how-to-measure-anything/04]
created: 2026-08-10
updated: 2026-08-10
---

# Monte Carlo simulation for decision uncertainty

## TL;DR
Monte Carlo simulation combines multiple uncertain input ranges (from decomposition and calibrated estimation) by repeatedly sampling random values from each input's distribution, running them through the decision formula thousands of times, and reading the resulting distribution of outcomes — turning a chain of "it depends" ranges into one usable probability distribution over the final answer, including the probability of a bad outcome.

## The idea
Once you've decomposed a fuzzy quantity into sub-quantities (`how-to-measure-anything/04`) and calibrated a range for each (`how-to-measure-anything/03`), you still face a combination problem: if "hours to build" is [40, 280] and "hourly cost" is [$90, $150] and "probability of a costly rework" is [10%, 35%], what's the *distribution* of total project cost? You cannot just multiply the midpoints together — that throws away all the uncertainty information and, worse, is mathematically wrong whenever the formula involves anything other than simple addition (multiplying several uncertain ranges together, in particular, produces a result *wider and more skewed* than naive midpoint math suggests, because the extremes can compound). Monte Carlo simulation solves this by brute force: instead of solving the combination analytically, a computer randomly draws one value from each input's probability distribution, plugs them into the formula, records the result, and repeats this 10,000 or 100,000 times. The resulting spread of 10,000 outcomes *is* the answer's probability distribution — you can read off its median, its 90% CI, and critically, the probability it exceeds any specific threshold (e.g., "probability the project costs more than $500,000").

## How it works

### Step by step
1. **For each input variable, specify a probability distribution**, not just a range. Common choices: normal distribution (symmetric, most values near the center — good for measurement error), lognormal (skewed right, can't go below zero — good for time and cost estimates, which have a hard floor and an open-ended tail), uniform (all values in a range equally likely — used when you genuinely have no reason to prefer any value over another, or as a conservative default), or a discrete distribution for binary/categorical events (e.g., 20% chance of a specific rework scenario).
2. **Write the formula** connecting inputs to the output, exactly as in decomposition (`how-to-measure-anything/04`).
3. **Run N trials** (typically 10,000+): each trial draws one random value per input (respecting each input's distribution shape) and computes the formula's output for that combination.
4. **Aggregate the N outputs** into a distribution: plot a histogram, read off percentiles (median, 90% CI), and compute the probability of crossing any decision-relevant threshold.
5. **Sensitivity analysis**: examine which input variable's variation correlates most with variation in the output — this tells you which input is most worth measuring better next (feeding directly into `how-to-measure-anything/09`).

### Worked example: should we build a custom internal deployment platform?
A staff engineer is evaluating whether to invest in a custom internal deployment platform versus continuing with the current semi-manual process. The relevant formula: **Net annual value = (time saved per deploy x deploys per year x cost per engineer-hour) - annual maintenance cost - one-time build cost amortized over 3 years**.

Calibrated input ranges (each as a distribution, not just a range):
- **Time saved per deploy:** lognormal, 90% CI [8, 35] minutes (center ~18 min) — estimated from 4 engineers who've used similar platforms elsewhere.
- **Deploys per year:** measured directly from CI logs — not uncertain, fixed at 2,400/year.
- **Cost per engineer-hour:** normal, 90% CI [$85, $115] (center $100), from finance data with minor uncertainty about overhead allocation.
- **Annual maintenance cost:** lognormal, 90% CI [$15,000, $60,000] (center ~$30,000) — uncertain because it depends on how much ongoing work the platform needs, informed by 3 similar internal tools' historical maintenance costs.
- **One-time build cost:** lognormal, 90% CI [$120,000, $400,000] (center ~$220,000) — the most uncertain input, since it hasn't been scoped in detail yet.

Running 10,000 Monte Carlo trials with these distributions (each trial: draw a random minute-saved value, a random cost-per-hour, a random maintenance cost, and a random build cost, then compute net annual value) produces an output distribution rather than a single number. A representative result: median net annual value = **+$140,000/year**, 90% CI of **[-$60,000, +$410,000]**, and critically, **the simulation shows a 22% probability that net annual value is negative** — i.e., roughly a 1-in-5 chance this investment loses money relative to the status quo. That 22% figure is something no single point-estimate calculation could have produced, and it's exactly the number a VP needs to make a genuinely informed go/no-go call, rather than seeing only a reassuring "expected value: +$140k."

### Why this beats "expected value" alone
A pure expected-value calculation (multiply the midpoints, or compute a probability-weighted average) can produce the same "+$140,000" headline number, but discards the shape of the risk entirely. Two projects can have the same expected value while one has a tight, low-risk distribution and the other has this platform's wide range including a real chance of loss. Decision-makers — especially at higher seniority, making bigger bets — usually care about that difference (this connects directly to `how-to-measure-anything/10` on portfolio risk and opportunity, where the full distribution, not just its mean, drives good portfolio-level choices).

### Correlated inputs
A common modeling mistake is treating inputs as independent when they're not. In the example above, if "build cost" runs high, "maintenance cost" is also likely to run high (a more complex, expensive-to-build platform is usually also more expensive to maintain) — these two inputs are correlated, not independent. A naive Monte Carlo that samples them independently understates the true tail risk (the scenario where *both* costs are bad simultaneously is more likely than independent sampling implies). Handling this requires either explicitly modeling the correlation (e.g., drawing a shared "project complexity" factor that influences both build and maintenance cost draws) or, at minimum, flagging the limitation when presenting results.

## Pros
- Correctly propagates uncertainty through arbitrarily complex formulas (multiplications, conditionals, thresholds) where simple midpoint math is provably wrong.
- Produces a full output distribution, enabling direct answers to risk questions ("what's the probability of loss") that a single expected-value number cannot answer.
- Sensitivity analysis on the trial outputs directly identifies which input is worth measuring more precisely, closing the loop back into value-of-information thinking (`how-to-measure-anything/09`).

## Cons
- Garbage in, garbage out: a Monte Carlo model is only as good as the input distributions fed into it — a beautifully simulated model built on badly uncalibrated ranges produces a precise-looking but wrong answer, which can be more dangerous than an obviously rough guess.
- Requires either spreadsheet tooling (e.g., Excel with a Monte Carlo add-in, or a simple script) and enough numerical literacy on the team to build and sanity-check the model, which is a real adoption barrier.
- Ignoring correlations between inputs (as discussed above) is an easy and common modeling error that understates real risk, especially tail risk.

## Alternatives
- **Analytical error propagation** — for simple formulas (mostly sums, or products of independent normal distributions), closed-form statistical formulas can propagate uncertainty without simulation; faster to compute but breaks down quickly for realistic formulas with conditionals, skewed distributions, or correlated inputs, where Monte Carlo is more robust and general.
- **Scenario analysis (best/worst/most-likely case)** — a much lighter-weight, spreadsheet-friendly alternative that presents 3 discrete scenarios instead of a full distribution; easier to communicate but loses the probability information (you don't know if "worst case" is a 1% or 40% likelihood) that Monte Carlo provides.
- **Decision trees** — better suited than Monte Carlo when the uncertainty is primarily about a small number of discrete branching events (e.g., "vendor renews contract or doesn't," "regulatory approval granted or not") rather than continuous ranges; Monte Carlo and decision trees are often combined in practice.

## When to use it
Any time a decision's outcome depends on combining several uncertain inputs through a non-trivial formula, especially when the decision-maker needs to know not just the expected value but the probability of a bad outcome — build-vs-buy calls, migration cost/benefit analysis, infrastructure investment cases, and any "should we make this bet" question with real variance across plausible outcomes.

## When NOT to use it
Skip Monte Carlo when the formula is simple enough (pure addition of roughly independent, roughly normal inputs) that analytical methods give an equally good answer with less setup. Also skip it, or treat its output with heavy skepticism, when the input distributions themselves are little more than uncalibrated guesses — simulating garbage inputs 10,000 times just produces a professional-looking histogram of garbage, and can create false confidence that's worse than presenting the raw uncertainty honestly.

## Key takeaways / mental model
When several uncertain numbers combine through a formula, don't collapse each range to its midpoint and multiply — that discards real information and is often mathematically wrong. Simulate: draw randomly from each input's real distribution thousands of times, and read the probability of the outcomes you actually care about (including the bad ones) off the resulting spread.

## Self-check questions
1. Take the decomposed CI-pipeline value estimate from lesson 04. Which of its inputs would you model as normal, lognormal, or uniform distributions in a Monte Carlo simulation, and why?
2. Explain why multiplying the midpoints of several uncertain ranges together tends to understate the true uncertainty of the combined result.
3. In the internal deployment platform example, why does the "22% probability of negative net value" matter more to a risk-aware VP than the "+$140,000 expected value" headline alone?
4. Describe two inputs in a real decision you've faced that were likely correlated with each other. What would naively treating them as independent have done to your risk estimate?

## References
- How to Measure Anything: Finding the Value of Intangibles in Business (Douglas W. Hubbard), Chapter 6: "Quantifying Risk Through Modeling," and Chapter 10: "Bayes: Adding to What You Know Now."
