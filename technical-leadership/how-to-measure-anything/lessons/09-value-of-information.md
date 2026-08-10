---
id: how-to-measure-anything/09
subject: how-to-measure-anything
title: Value of information and when measurement is worth the cost
slug: value-of-information
status: drafted
mastery:
seniority: staff
source: How to Measure Anything (Douglas W. Hubbard), Chapter 7
prerequisites: [how-to-measure-anything/05, how-to-measure-anything/07]
created: 2026-08-10
updated: 2026-08-10
---

# Value of information and when measurement is worth the cost

## TL;DR
The value of a measurement is the expected reduction in loss it enables by helping you avoid a wrong decision, and it can be calculated *before* you take the measurement — which tells you exactly which uncertain variables are actually worth spending time or money to measure, and which ones you should stop worrying about because more precision on them wouldn't change what you do.

## The idea
Teams routinely misallocate measurement effort: they spend weeks building a precise dashboard for a variable that barely affects the decision, while leaving a genuinely decision-critical variable as an unexamined guess. Hubbard's fix is to compute the **Expected Value of Information (EVI)** for each uncertain variable before deciding what to measure. The core insight, sometimes called the **measurement inversion** (introduced in `how-to-measure-anything/02`): the variables that feel most urgent to measure precisely are often not the ones with the highest information value, and vice versa. EVI gives a principled, quantitative way to decide where your limited measurement budget (time, money, attention) delivers the most decision-improving value — often revealing that a single cheap measurement on the right variable is worth more than an expensive study on the wrong one.

## How it works

### The core calculation: Expected Value of Perfect Information (EVPI)
For a binary or discrete decision under uncertainty, EVPI is the expected loss you'd avoid if you magically knew the true value of an uncertain variable *before* deciding, compared to deciding under current uncertainty.

Simplified worked example: a team is deciding whether to migrate a legacy service to a new platform. The migration costs $300,000 (certain). The benefit depends on an uncertain variable: whether the legacy platform's vendor will raise support costs by a large amount next year. Current belief (from partial market signals): 40% chance the vendor raises costs by $600,000/year (making migration clearly worth it), 60% chance costs stay roughly flat (making migration a net loss of $300,000 with no offsetting benefit).

- **Expected value without more information**, deciding now: expected value of migrating = 0.4 x $600,000 + 0.6 x (-$300,000)... but actually you'd only choose to migrate if migrating is the better *expected* choice overall, so first compute: expected value of migrating = 0.4($600,000 - $300,000) + 0.6(-$300,000) = 0.4($300,000) + 0.6(-$300,000) = $120,000 - $180,000 = -$60,000. Expected value of *not* migrating = $0. Since -$60,000 < $0, the rational choice today, under current uncertainty, is **don't migrate**.
- **Expected value with perfect information**: if you knew for certain which scenario was true before deciding, you'd migrate only in the 40% scenario (net gain $300,000) and not migrate in the 60% scenario (net $0). Expected value with perfect information = 0.4 x $300,000 + 0.6 x $0 = $120,000.
- **EVPI = (expected value with perfect information) - (expected value of the best decision without it)** = $120,000 - $0 = **$120,000**.

This means: it is worth spending up to $120,000 to find out, with certainty, whether the vendor will raise prices — anything you could do to learn that (e.g., escalate a direct conversation with the vendor's account team, review contract renewal language, talk to peer companies using the same vendor) is worth pursuing if it costs meaningfully less than $120,000. If the only available way to find out costs $250,000 (e.g., a expensive legal/consulting engagement), it's *not* worth it — better to decide under the current uncertainty.

### From EVPI to realistic partial information
Perfect information is rarely available — real measurements are noisy and partial, narrowing uncertainty rather than eliminating it (as established in lesson 02). The **Expected Value of Imperfect Information (EVII)** scales EVPI down based on how much a realistic measurement would actually narrow the uncertainty. A rough but practically useful heuristic Hubbard offers: if a proposed measurement would cut the current uncertainty range roughly in half, it typically captures a meaningful fraction (often very roughly around a third to half, depending on the specific distribution) of the full EVPI — enough that, in the vendor example, even an imperfect signal (a candid conversation with the vendor's competitor, worth maybe 30% of the full $120,000 ≈ $36,000 in expected value) is still well worth pursuing if it costs a few hours of a manager's time.

### Applying EVI to prioritize a measurement backlog
This is the direct, high-leverage engineering-leadership use case: when facing a list of uncertain variables feeding into a roadmap or architecture decision, compute (even roughly) the EVPI for each before deciding what to measure first.

Worked example: a staff engineer planning a platform investment has three uncertain inputs feeding the decision model from lesson 07 (deployment platform ROI): (a) time saved per deploy, (b) annual maintenance cost, (c) one-time build cost. Running a quick sensitivity pass on the Monte Carlo model (varying each input across its range while holding the others fixed) shows that varying "one-time build cost" across its 90% CI swings the net-value outcome by roughly $400,000, while varying "time saved per deploy" across its range swings it by only about $60,000. Even though the team's instinct was to interview more engineers to pin down "time saved per deploy" more precisely (it felt like the most human, most talked-about number), the EVI analysis says the build-cost estimate — currently a rough guess — is where a real scoping exercise (a 2-week technical spike, costing maybe $15,000 in engineer time) would deliver far more decision value than further refining the time-saved estimate. This is the measurement inversion in action: the variable that felt most worth measuring wasn't the one that actually mattered most to the decision.

## Pros
- Directly answers "is this measurement worth doing" with a number, instead of leaving it to instinct or to whoever is loudest about wanting more data.
- Frequently redirects measurement effort toward high-leverage variables that intuition would have overlooked (the measurement inversion), improving decisions without necessarily spending more total effort on measurement.
- Provides a principled stopping rule: once a variable's EVI is near zero (further precision wouldn't change the decision), stop measuring it and move on — countering the tendency to over-invest in reassurance-seeking analysis.

## Cons
- Computing EVI rigorously requires a decision model (thresholds, payoffs, probabilities) to already exist, which is itself work — teams without any structured decision model must build one first, adding upfront cost before the EVI payoff is realized.
- The EVPI/EVII numbers are themselves estimates built on other estimates (the probabilities and payoffs feeding in), so they carry their own uncertainty — useful for prioritization and rough magnitude, less useful as a precise budget figure.
- Can be politically awkward: EVI analysis sometimes reveals that a stakeholder's pet metric or favorite data project has near-zero decision value, which is a harder conversation than simply agreeing to build it.

## Alternatives
- **Gut-feel prioritization of measurement effort** — the default in most organizations; faster to start but systematically falls prey to the measurement inversion, over-investing in intuitively appealing but low-leverage measurements.
- **"Measure everything cheaply available" approach** — instrument broadly and see what's useful later; avoids the upfront decision-model cost of EVI, but risks wasted effort on decision-irrelevant data and can produce dashboard sprawl (see the failure mode described in `how-to-measure-anything/05`).
- **Real options valuation** — a more advanced financial framework, related to value-of-information, that values the *option* to gather information and delay a decision explicitly as a financial instrument; more rigorous for large capital investment decisions but heavier-weight than Hubbard's EVI approach for typical engineering decisions.

## When to use it
Whenever facing a real decision with several uncertain inputs and a limited budget (time, money, attention) for reducing that uncertainty — deciding what to prototype, what to survey, what to instrument, or what data-gathering spike to run before a major technical or organizational bet. Especially valuable when a team's instinct about "what we should measure" hasn't been checked against what actually drives the decision.

## When NOT to use it
Skip formal EVI calculation for low-stakes, cheap-to-reverse decisions, where the cost of doing the EVI analysis itself exceeds any plausible benefit — just decide and observe. Also skip it when a measurement is nearly free and instantaneous to obtain (e.g., a number already sitting in an existing dashboard) — there's no real cost/value trade-off to analyze when the "cost" of the measurement is close to zero; just look at the number.

## Key takeaways / mental model
Before investing in reducing uncertainty about any variable, ask two questions: how much would knowing this variable precisely change my expected outcome (EVPI), and how much would the specific measurement I'm considering actually narrow my uncertainty about it? Multiply those together, roughly, and compare to the measurement's cost. Don't measure the variable that feels most uncertain — measure the variable whose uncertainty costs you the most if you get the decision wrong.

## Self-check questions
1. Walk through the vendor cost-increase worked example above and recompute EVPI if the probability of a price increase were 25% instead of 40% (with the same $600,000 benefit and $300,000 cost). Does the recommended action change?
2. Explain the "measurement inversion" using your own recent example: a variable your team wanted to measure precisely that (on reflection) had low decision leverage, and one that had high leverage but was under-measured.
3. A colleague wants to run a full user survey (2 weeks of effort) to nail down a number that a quick sensitivity check shows barely affects the final decision. How would you use EVI reasoning to redirect that effort?
4. Why is EVII (imperfect information) usually more relevant in practice than EVPI (perfect information), and roughly how does a measurement's expected uncertainty reduction relate to how much of the full EVPI it captures?

## References
- How to Measure Anything: Finding the Value of Intangibles in Business (Douglas W. Hubbard), Chapter 7: "The AIE Approach: Expected Value of Information."
