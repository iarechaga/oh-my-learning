---
id: how-to-measure-anything/06
subject: how-to-measure-anything
title: Sampling methods for fast, low-cost evidence gathering
slug: sampling-methods
status: drafted
mastery:
seniority: senior
source: How to Measure Anything (Douglas W. Hubbard), Chapter 9
prerequisites: [how-to-measure-anything/02, how-to-measure-anything/03]
created: 2026-08-10
updated: 2026-08-10
---

# Sampling methods for fast, low-cost evidence gathering

## TL;DR
Small, cheap, non-exhaustive samples reduce uncertainty far more than most people expect — a sample of even 5-10 items, correctly reasoned about, can rule out a large fraction of the plausible range for a quantity, and the marginal value of each additional sample drops off quickly (the "law of diminishing returns" for sample size, called the "diminishing returns" or "square root" rule).

## The idea
Engineers often refuse to sample at all ("a survey of 8 users tells us nothing statistically significant") or, at the other extreme, assume useful measurement requires a large, expensive, fully powered study. Both instincts are wrong for most business decisions. Hubbard's central counter-intuitive result, borrowed from statistics but rarely taught this way, is the **rule of five**: if you take a random sample of just 5 items from a population and look at the range from the smallest to the largest value, there is a 93.75% chance that the true median of the whole population lies somewhere within that range. This holds regardless of the population's size or distribution shape, as long as the sample is reasonably random. Five data points — not fifty, not five hundred — already meaningfully bounds your uncertainty for many real questions. This doesn't mean five samples is always enough (it depends on how narrow a range the decision requires — see `how-to-measure-anything/09` on value of information), but it recalibrates the instinct that "small samples tell you nothing," which causes many measurement efforts to never start at all.

## How it works

### The rule of five
Take any 5 random, independent samples from a population. Sort them. The interval [min, max] of those 5 values has a 93.75% chance of containing the population median. Proof sketch: for the true median to fall outside your sample's range, all 5 samples would need to land on the same side of the median (all above, or all below) — each individual sample has a 50% chance of being above the median, so the chance all 5 land above is 0.5^5 = 3.125%, and symmetrically 3.125% for all landing below; 100% - 3.125% - 3.125% = 93.75%. This logic requires only that each sample is independently more likely than not to fall on either side of the median — it does not require knowing the population's distribution shape, its size, or anything about its variance.

**Worked example:** you want to know the typical (median) time engineers spend in code review per week, to decide whether to invest in review-tooling improvements. Instead of instrumenting everyone or running a company-wide survey, you randomly message 5 engineers: they report 3.5, 6, 2, 9, and 4 hours/week. Sorted: [2, 3.5, 4, 6, 9]. By the rule of five, you can say with 93.75% confidence that the true median across the whole engineering org is somewhere between 2 and 9 hours/week. That's a real, decision-useful range obtained in about 20 minutes of Slack messages — enough, for instance, to confirm review time is a meaningful chunk of the work week and worth further investigation, without needing a full survey yet.

### Random sampling vs. convenience sampling — the bias trap
The rule of five (and sampling generally) only works if the sample is genuinely representative — ideally randomly selected from the full population you care about. A common and costly mistake is convenience sampling: messaging the 5 engineers you happen to talk to most, who are disproportionately likely to be on your own team, at a similar seniority, or otherwise correlated in ways that bias the result. If you want the median code-review time across the whole 200-person engineering org, draw randomly from the full roster (e.g., using a random number generator against the employee directory), not from your Slack DMs. A small truly-random sample beats a large convenience sample for avoiding systematic bias, because a large biased sample just gives you a precise, confident, wrong answer.

### Stratified sampling for known subgroup differences
When you already suspect a population has meaningfully different subgroups (e.g., backend vs. frontend engineers likely have different code review loads, or engineers on different-sized teams have different on-call burden), stratified sampling — drawing separate small random samples from each subgroup and combining them — gives a more accurate and more informative picture than one pooled random sample of the same total size. Worked example: instead of 5 random engineers from the whole org, draw 5 from backend and 5 from frontend separately. If backend shows [4, 6, 7, 9, 12] hours and frontend shows [1, 2, 2.5, 3, 4] hours, you've not only bounded the overall median but discovered the two groups don't overlap at all — a much more actionable finding (the tooling investment should probably target backend review load specifically) than a single pooled range would have revealed.

### Population proportion sampling (a second common case)
A different but equally common measurement need is estimating a proportion (e.g., "what fraction of production incidents in the last year were caused by missing test coverage on the changed code path?"). For proportions, the relevant statistical tool is the standard error of a proportion, roughly sqrt(p(1-p)/n). Worked example: you sample 20 incidents at random from the last year's incident log (out of, say, 140 total) and find 7 were caused by missing test coverage — a sample proportion of 35%. The approximate 90% CI, using the standard error formula and a z-value of 1.645 for 90% confidence, is 35% +/- 1.645 x sqrt(0.35 x 0.65 / 20) ≈ 35% +/- 17.5%, i.e., roughly [17.5%, 52.5%]. That's a wide range from just 20 samples, but it's already enough to answer a coarse decision question like "is this worth investing in test-coverage tooling" if the threshold for action is, say, "more than 15% of incidents." To narrow the range further (e.g., to make a more precise ROI case), the standard error shrinks with the square root of sample size — quadrupling the sample from 20 to 80 roughly halves the width of the confidence interval, which is the diminishing-returns pattern that makes very large samples rarely worth their cost for most internal engineering decisions.

## Pros
- Small samples are dramatically more informative than intuition suggests, making fast measurement realistic even under real time and budget constraints.
- The rule of five requires no statistical software, distributional assumptions, or specialized training — it's usable in a single conversation or planning meeting.
- Sampling (especially of existing logs, tickets, or incident records) is often nearly free, since the population already exists in a system of record — the cost is just the analyst's time to pull and read a random subset.

## Cons
- All sampling methods are only as good as the randomness of the draw; convenience or self-selected samples (e.g., a voluntary survey with a 12% response rate) can be badly biased in ways that are easy to overlook.
- The rule of five bounds the *median*, not the mean, and not the full shape of the distribution — for decisions sensitive to tail risk (rare but severe outcomes), five samples are not remotely enough (see `how-to-measure-anything/10` on portfolio risk).
- Diminishing returns cut both ways: it's tempting to over-invest in ever-larger samples for reassurance, when the decision-relevant uncertainty was already resolved at n=20 or n=30 — recognizing "enough" requires tying sample size back to the decision (`how-to-measure-anything/09`).

## Alternatives
- **Full census / instrumentation** — measuring 100% of the population (e.g., instrumenting every code review with automatic time tracking) removes sampling uncertainty entirely, but at much higher engineering and privacy cost; appropriate when the decision is high-stakes and ongoing, not one-off.
- **Expert calibrated estimation alone** (`how-to-measure-anything/03`) — when even a small sample is infeasible to obtain (e.g., no historical data exists yet), a calibrated expert range is the fallback, though it should be replaced by real sampling as soon as it's cheaply possible.
- **A/B testing / controlled experiment** — for questions about causal effect (not just population characteristics), a designed experiment with random assignment to treatment/control is a stronger method than observational sampling, though it requires the ability to actually intervene, which isn't always available.

## When to use it
Whenever you need a rough-but-real answer to "what's typical" or "what fraction of X has property Y" and full data collection is expensive or slow — pulling a random slice of logs, tickets, incidents, or messaging a handful of random team members. Especially valuable as the *first* measurement step before deciding whether a larger, more expensive data-collection effort is even worth it.

## When NOT to use it
Don't rely on small-sample methods (including the rule of five) when the decision is sensitive to tail behavior or rare events rather than central tendency — a handful of samples will almost never contain a rare catastrophic outcome, so they systematically understate tail risk (use historical severity data or Monte Carlo modeling instead, `how-to-measure-anything/07` and `how-to-measure-anything/10`). Also avoid convenience samples dressed up as random ones — if you can't credibly claim the sample was drawn without selection bias, the confidence-interval math doesn't apply.

## Key takeaways / mental model
Five genuinely random samples already rule out roughly 94% of the ways your intuition about a population's median could be wrong. Before assuming "we don't have enough data," ask whether you could pull even a small truly random sample from something you already have (logs, tickets, a roster) — the answer is often yes, and it's usually enough to move a decision forward.

## Self-check questions
1. Pick a quantity at work you'd like to know the typical value of (time-to-review, incident resolution time, deployment frequency). Describe how you'd draw a genuinely random sample of 5, and what population you'd be sampling from.
2. Explain, without looking back at this lesson, why the rule of five gives 93.75% confidence rather than some other number.
3. A survey link is posted in the team Slack channel and 12 of 60 engineers respond. Is this a valid random sample? What biases might it carry, and how would they likely skew the result?
4. Why does the rule of five bound the median but say little about tail risk? Give an example of a decision where that distinction would matter.

## References
- How to Measure Anything: Finding the Value of Intangibles in Business (Douglas W. Hubbard), Chapter 9: "Sampling Reality: How Observing Some Things Tells Us about All Things."
