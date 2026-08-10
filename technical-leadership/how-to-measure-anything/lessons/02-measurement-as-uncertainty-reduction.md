---
id: how-to-measure-anything/02
subject: how-to-measure-anything
title: Measurement as uncertainty reduction, not perfect precision
slug: measurement-as-uncertainty-reduction
status: drafted
mastery:
seniority: senior
source: How to Measure Anything (Douglas W. Hubbard), Chapter 2-3
prerequisites: [how-to-measure-anything/01]
created: 2026-08-10
updated: 2026-08-10
---

# Measurement as uncertainty reduction, not perfect precision

## TL;DR
Measurement is not "obtaining an exact number" — it is any observation that reduces your uncertainty about a quantity, even if the result is still a range. A measurement that narrows your estimate from "somewhere between 0 and 10,000 hours" to "somewhere between 2,000 and 4,000 hours" is a real, useful measurement even though it never produces a single precise figure.

## The idea
Most engineers implicitly define "measure" the way a lab scientist measures the mass of an object: instrument, precision, a number with small error bars. That definition sets an impossibly high bar for business and organizational questions ("measure the ROI of this migration," "measure the risk of this vendor") and leads people to conclude those things can't be measured at all, so they don't try. Hubbard redefines measurement formally, borrowing from decision theory and information theory: **a measurement is an observation that quantifiably reduces uncertainty, expressed as a probability**. You start with a prior state of uncertainty (a wide range of plausible values), and a measurement is anything — an estimate, a small sample, an expert judgment, a proxy — that narrows that range, even partially. Under this definition, an educated guess from someone with relevant experience is a measurement (a weak one). A single data point sampled at random is a measurement. A full statistically powered study is also a measurement — just a much stronger one. They differ in *how much* uncertainty they remove, not in whether they qualify as measurement at all.

## How it works

### Uncertainty as a probability distribution, not a single unknown number
Before you measure anything, you already have *some* information — call it your prior. If asked "how many hours will migrating our monolith to microservices take," almost nobody would say "I have absolutely no idea, it could be 1 hour or 10 billion hours." Most engineers would instinctively rule out both extremes: probably not less than 500 hours, probably not more than 50,000 hours. That range — even before any formal measurement — already encodes real information. The goal of measurement is to narrow that range further, and to attach calibrated probabilities to values within it (formalized fully in `how-to-measure-anything/03`).

### Worked example: estimating the ROI of a proposed caching layer
An engineering team debates adding a caching layer to reduce database load. Someone says "we can't know the ROI, it's not measurable in advance."
- **Prior state of uncertainty:** the team estimates the caching layer will reduce database costs somewhere between $0 and $8,000/month (a very wide, low-information range) and cost between 200 and 800 engineering-hours to build and maintain (a wide range too).
- **First measurement — cheap:** pull the last 90 days of database query logs (an afternoon of work) and find that 62% of DB load comes from 8 highly repetitive read queries with low staleness tolerance. This single observation dramatically narrows the plausible savings range: the theoretical maximum saving is now bounded by 62% of the current $6,500/month DB spend ≈ $4,000/month, so the true range collapses from "$0-$8,000" to roughly "$1,500-$4,000/month" (accounting for cache miss rates and partial coverage).
- **Second measurement — still cheap:** a 2-day prototype cache in front of the top 2 queries measures a real 71% hit rate in staging traffic. That narrows the estimate further to roughly $2,200-$3,200/month in savings.
Neither step gave a single exact number. Both were real measurements: each one materially reduced the width of the plausible range, which is exactly what the decision-maker needed to compare against the ~$40,000 fully-loaded cost of building it (400 hours x $100/hr) and decide whether to proceed. Waiting for "certainty" would have meant never deciding.

### The "measurement inversion" — why intuition about measurement cost is usually backwards
Hubbard observes a consistent pattern he calls the *measurement inversion*: the variables people most want to measure precisely (e.g., a project's total ROI) are usually the ones with the least economic value in additional precision, while the variables people almost never bother measuring (e.g., a single upstream assumption feeding into many downstream estimates) often have the highest value of additional information. A small measurement on a high-leverage input variable (like the DB query concentration above) can collapse more uncertainty in the final decision than an expensive, precise measurement of a low-leverage one. This connects directly to value-of-information (`how-to-measure-anything/09`): the right question is never "can I get an exact number" but "which measurement, however partial, moves my decision-relevant uncertainty the most per unit of cost."

### Quantifying "how much uncertainty was reduced"
Formally, Hubbard expresses uncertainty as a range with a stated confidence level — most often a 90% confidence interval (CI): a range you believe has a 90% chance of containing the true value. Reduction in uncertainty is the narrowing of that range's width (or more rigorously, the reduction in variance / entropy of the underlying distribution). If your 90% CI for "hours to migrate the monolith" was [500, 50,000] before talking to the two engineers who did a similar migration last year, and becomes [3,000, 9,000] afterward, you measured something real — you reduced the range's log-width by roughly 80% — even though you still don't have a single number.

## Pros
- Removes the false binary of "measured vs. not measured," replacing it with "how much did this reduce our uncertainty, at what cost" — a much more useful decision frame.
- Makes cheap, fast, informal measurements legitimate and worth doing, instead of waiting for an expensive definitive study that may never happen.
- Directly compatible with probabilistic decision-making tools (Monte Carlo, Bayesian updating) covered later in this subject, since it already frames knowledge as a distribution, not a point value.

## Cons
- Communicating "we reduced uncertainty from X to Y" is a harder sell to stakeholders who expect and want a single confident number — requires deliberate expectation-setting.
- Without discipline, "uncertainty reduction" can become an excuse to never commit to a number at all, stalling decisions instead of enabling them.
- Requires the audience to be comfortable reasoning in ranges and probabilities, which is a genuine skill gap in many engineering and business cultures.

## Alternatives
- **Point-estimate culture (single "best guess" numbers)** — common in ad hoc planning; faster to communicate but hides the actual uncertainty and produces false confidence (a $2M project estimate presented as exactly $2,143,000 implies precision nobody actually has).
- **"We need more data before we can say anything"** — the opposite failure mode: refusing to state even a wide range until data is perfect, which throws away the real information already available from prior knowledge and expert judgment.
- **Six Sigma / formal statistical process control** — a much more rigorous, industrial-grade uncertainty-reduction discipline appropriate for repeated manufacturing-style processes; usually overkill for one-off business or engineering decisions, where Hubbard's lighter-weight approach fits better.

## When to use it
Any time a decision is being delayed or defaulted to opinion because "we don't have the data" or "it's not measurable precisely." Reframe to: what is our current range of uncertainty, and what is the cheapest observation that would narrow it enough to matter for this decision.

## When NOT to use it
When the decision doesn't actually depend on narrowing uncertainty further — e.g., the range is already narrow enough that any value within it leads to the same choice (see `how-to-measure-anything/09` on when the value of additional information is near zero). Also skip elaborate uncertainty framing for trivial, reversible, low-stakes calls, where "just decide and observe the outcome" is faster and cheaper than any formal measurement.

## Key takeaways / mental model
Every measurement is a probability-narrowing operation, not a precision-achieving one. Before designing any measurement effort, state your current range (even a rough one) explicitly, then ask what the cheapest next observation is that would narrow it enough to change or confirm the decision.

## Self-check questions
1. Pick a current uncertain estimate at work (a project timeline, a budget, a headcount need). State your current 90% confidence range for it explicitly, out loud, before reading further in this subject.
2. Explain the "measurement inversion" in your own words and give an example from your own work where you or your team over-invested in precision on a low-leverage variable.
3. A colleague says "the survey only had 12 responses, that's not statistically valid, it tells us nothing." Using this lesson's definition of measurement, is that true? Why or why not?
4. Describe a case where narrowing uncertainty further would NOT have changed the decision. How would you have recognized that in advance?

## References
- How to Measure Anything: Finding the Value of Intangibles in Business (Douglas W. Hubbard), Chapter 2: "An Intuitive Measurement Habit," and Chapter 3: "The Illusion of Intangibles: Why Immeasurables Aren't."
