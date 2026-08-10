---
id: how-to-measure-anything/08
subject: how-to-measure-anything
title: Bayesian updates and integrating new evidence
slug: bayesian-updates
status: drafted
mastery:
seniority: staff
source: How to Measure Anything (Douglas W. Hubbard), Chapter 10
prerequisites: [how-to-measure-anything/02, how-to-measure-anything/06]
created: 2026-08-10
updated: 2026-08-10
---

# Bayesian updates and integrating new evidence

## TL;DR
Bayesian updating is the disciplined way to combine what you already believed (your prior) with new evidence to arrive at a revised belief (your posterior) — and it explains quantitatively why a small amount of new data should shift a strong prior only a little, while the same small amount of data should shift a weak, uninformed prior a lot.

## The idea
Most people update their beliefs on new evidence inconsistently: sometimes over-reacting to a single new data point (throwing out months of trend data because of one bad week), sometimes under-reacting (dismissing a strong new signal because it contradicts an entrenched opinion). Bayes' theorem gives a mathematically principled alternative: your revised belief (posterior) is a weighted combination of your prior belief and the new evidence, where the weights are determined by how confident (strong/informative) each one is. A prior built from years of solid historical data should barely move in response to one small, noisy new sample. A prior that was really just a shrug ("we have no idea") should move a lot in response to even a small amount of real evidence. This isn't a matter of taste — Bayes' theorem specifies exactly how much each should move, given their respective strengths, and it's the formal foundation underneath the intuitive "measurement narrows uncertainty" framing from `how-to-measure-anything/02`.

## How it works

### The core mechanism, in plain terms
Bayes' theorem: posterior probability is proportional to (prior probability) x (likelihood of the new evidence given that hypothesis). In practice, for continuous estimates (like the calibrated ranges from lesson 03), a convenient and widely-used approximation treats both the prior and the new evidence as normal (or lognormal) distributions, each with a mean and a variance (a measure of how confident/narrow they are). The posterior mean is then a **variance-weighted average** of the prior mean and the new evidence's mean — the more confident (narrower-variance) source pulls the answer more toward itself.

Simplified formula for combining two normal estimates: if the prior has mean μ₁ and variance σ₁², and the new evidence has mean μ₂ and variance σ₂², the posterior mean is:

μ_post = (μ₁/σ₁² + μ₂/σ₂²) / (1/σ₁² + 1/σ₂²)

Note the structure: each mean is weighted by the *inverse* of its variance (its "precision") — so a very confident (low-variance) source dominates, and a very uncertain (high-variance) source contributes little, exactly matching the intuition above.

### Worked example: updating an incident-rate estimate after a small sample
A platform team has a long-standing prior belief, built from 3 years of incident history, that the mean weekly incident count for a particular service is 2.0 incidents/week, with fairly high confidence (variance corresponding to a 90% CI of roughly [1.6, 2.4]).

After a major refactor, the team wants to know: has the incident rate actually changed? They observe the first 4 weeks post-refactor: 1, 3, 1, 2 incidents — sample mean 1.75/week. Naively, someone might say "the new data shows 1.75, so the new rate is 1.75" — discarding 3 years of prior evidence in favor of 4 noisy data points. That's a classic over-reaction error.

Applying Bayesian updating instead: the 4-week sample is itself noisy (with only 4 observations of a naturally variable process, its own estimate of the mean has wide variance — call it a 90% CI of roughly [0.9, 2.6], reflecting how uncertain a mean estimated from just 4 samples is). Combining the strong prior (μ₁=2.0, narrow variance) with the weak new evidence (μ₂=1.75, wide variance) using the variance-weighted formula pulls the posterior only modestly toward the new data — the posterior mean lands around **1.93 incidents/week**, much closer to the strong prior than to the noisy 4-week sample, and the posterior's confidence interval narrows only slightly from the prior's. This is the mathematically correct amount to update: real evidence that the rate improved, but nowhere near enough evidence yet to conclude a large change happened. If the team instead waited and collected 20 weeks of post-refactor data averaging 1.75/week, the new evidence's own variance would shrink substantially (more samples = more confident estimate), and *then* the posterior would shift much closer to 1.75 — correctly reflecting that stronger evidence deserves more weight.

### Why this matters for engineering leadership decisions
This directly counters two common and opposite failure modes seen in engineering orgs:
- **Reacting to noise:** declaring a process "fixed" or "broken" based on one good/bad sprint, one week of metrics, or one incident, without weighing it against the historical baseline's strength. Bayesian updating formalizes "how much should this one data point actually move my belief," which is usually "not much" for a single noisy observation against a well-established baseline.
- **Ignoring real signal:** dismissing new evidence entirely because "our historical data says X" when the new evidence, while limited, is actually strong enough (large enough sample, or high enough quality) to warrant real updating — Bayesian updating quantifies exactly when new evidence has earned enough weight to shift the belief meaningfully, rather than leaving that judgment to gut feel or organizational inertia.

### Sequential updating
A powerful property of Bayesian updating is that it composes: today's posterior becomes tomorrow's prior. As more evidence arrives (week 5, week 6, ...), each new batch updates the current belief rather than requiring you to recompute from scratch with all historical data at once. This makes it a natural fit for ongoing monitoring situations — a metric's belief state evolves incrementally as new data streams in, always properly weighted by how much is already known versus how much is newly observed.

## Pros
- Provides a principled, quantitative answer to "how much should this new data change what we believe," resolving arguments between over-reacting and under-reacting camps.
- Naturally incorporates prior knowledge (historical baselines, expert judgment, past similar cases) rather than discarding it every time new data arrives, which is both more accurate and more efficient (small new samples are still useful, not wasted).
- Composes cleanly for ongoing monitoring — each new observation updates the current belief incrementally rather than requiring a full re-analysis.

## Cons
- Requires an explicit prior, which can feel uncomfortably subjective to teams used to "the data speaks for itself" framing — critics sometimes (unfairly) dismiss Bayesian methods as "just making up a number to start."
- The math, while not advanced, is an extra step most engineering teams don't have built into their existing dashboards or spreadsheets, creating an adoption barrier similar to Monte Carlo simulation (`how-to-measure-anything/07`).
- A badly chosen or badly justified prior can bias results if not made explicit and open to challenge — the method's power depends on the prior itself being honest (ideally calibrated per lesson 03), not an unexamined assumption smuggled in.

## Alternatives
- **Frequentist hypothesis testing (p-values, significance thresholds)** — the more commonly taught statistical approach; asks "how surprising is this data if nothing changed" rather than directly producing an updated belief about the value itself; often harder to interpret correctly for decision-making and doesn't naturally incorporate prior knowledge the way Bayesian updating does.
- **Simple moving averages / exponential smoothing** — a common ad hoc practice (e.g., "let's just track a rolling 4-week average") that implicitly does a crude form of weighting old vs. new data, but without an explicit, justified weighting scheme tied to actual confidence levels — Bayesian updating makes that weighting principled instead of arbitrary.
- **"Just look at the trend line"** — the most common real-world alternative, useful for very obvious, large, sustained shifts, but prone to both noise-chasing and confirmation bias when the shift is subtle or the sample is small, exactly the situations where formal Bayesian updating adds the most value.

## When to use it
When new evidence arrives that might update an existing belief with real decision consequences — post-change monitoring (did this refactor/process change actually help), integrating a new small measurement into a long-standing estimate, or combining expert judgment (a prior) with early experimental data. Especially valuable whenever the new sample size is small enough that naive "just use the new number" reasoning would be a mistake.

## When NOT to use it
Skip formal Bayesian updating when you have no meaningful prior at all (a genuinely new, never-before-observed situation) — in that case, the new evidence essentially *is* the prior for the next update, and the formal machinery adds little beyond what calibrated estimation (`how-to-measure-anything/03`) already provides. Also skip it for large-sample situations where the new evidence is already far stronger than the prior — at that point the posterior converges to the new data's estimate anyway, and the extra computation isn't worth the effort.

## Key takeaways / mental model
A new data point doesn't replace what you already knew — it should shift your belief by an amount proportional to how strong the new evidence is relative to how strong your prior belief already was. Before reacting to any new number, ask: how confident was I before, how confident is this new evidence, and does the math actually justify how much I'm about to update?

## Self-check questions
1. Your team's on-call load has averaged 8 pages/week for the past year (strong prior). Last week there were 15 pages. Would a Bayesian approach have you conclude the on-call load has fundamentally changed? What additional evidence would change that answer?
2. Explain, in your own words, why a well-established prior should move only a little in response to a single small new sample, using the variance-weighted formula's structure (not just intuition).
3. Describe a real situation from your work where you (or your team) over-reacted to a single noisy data point. How would explicit Bayesian reasoning have changed the response?
4. Why does "today's posterior becomes tomorrow's prior" make Bayesian updating well-suited to ongoing metric monitoring rather than one-off analysis?

## References
- How to Measure Anything: Finding the Value of Intangibles in Business (Douglas W. Hubbard), Chapter 10: "Bayes: Adding to What You Know Now."
