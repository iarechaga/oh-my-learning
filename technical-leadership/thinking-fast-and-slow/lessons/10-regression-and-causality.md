---
id: thinking-fast-and-slow/10
subject: thinking-fast-and-slow
title: Regression to the mean and causal misattribution
slug: regression-and-causality
status: drafted
mastery:
seniority: senior
source: Thinking, Fast and Slow (Daniel Kahneman), Part III, Chapters 17-18
prerequisites: [thinking-fast-and-slow/06]
created: 2026-08-10
updated: 2026-08-10
---

# Regression to the mean and causal misattribution

## TL;DR
Any measurement with a random/noise component will tend to be followed by a measurement closer to the average — not because of anything that was done in between, but purely from statistics. Because System 1 insists on causal explanations for everything (`thinking-fast-and-slow/08`), we routinely invent causal stories (a intervention "worked," a person "learned their lesson") to explain what is actually just regression to the mean.

## The idea
Any measured quantity that combines a stable "true" component with a random, noisy component will, on average, be followed by a next measurement closer to the mean of the distribution — this is a mathematical necessity, not an empirical pattern that could turn out otherwise. It exists because an extreme observation is disproportionately likely to include a large positive (or negative) noise contribution on top of the true value, and noise, by definition, doesn't repeat in the same direction next time. Kahneman highlights this because System 1 has no native intuition for regression — it demands causal stories for every pattern it notices, and when an extreme result is followed by a more average one, the mind reaches for "something must have caused the improvement/decline" rather than the correct, un-narratable explanation: statistical noise.

## How it works

### The flight-instructor discovery
Kahneman's own formative example: while training Israeli Air Force flight instructors, he explained the psychological research showing praise improves performance and punishment doesn't. An experienced instructor pushed back: pilots who are praised for an exceptionally smooth landing typically do worse on their next landing, while pilots who are harshly criticized for a terrible landing typically do better next time — so, the instructor argued, punishment works and praise doesn't. Kahneman recognized this was regression to the mean, not a real causal effect of praise or criticism: an exceptionally smooth landing is partly skill and partly a lucky combination of conditions (noise); the "luck" part doesn't repeat, so the next landing regresses toward the pilot's average, appearing as "decline" right after praise. Symmetrically, an exceptionally bad landing includes unlucky noise that also doesn't repeat, so the next landing improves on average, appearing as "improvement" right after criticism — with zero causal contribution from the criticism itself.

### Regression as a mathematical necessity, not an empirical finding
The key conceptual point is that regression to the mean is *guaranteed* whenever a measurement has a random component and is not perfectly correlated with the next measurement — it doesn't require any special explanation, and looking for a causal mechanism behind it is a category error. The rate of regression depends on how noisy vs. stable the underlying quantity is: a highly-skill-dominated, low-noise metric regresses only slightly; a highly noise-dominated metric regresses heavily, closer to the full distance back to the mean.

### Engineering example: sprint velocity and "improvement" theater
**Worked example — velocity swings:** a team has an unusually low-velocity sprint (say, 60% of their typical points, due to several unrelated unlucky factors — a teammate out sick, an unexpectedly gnarly bug, a flaky CI day). Management responds with a "productivity intervention" (a new process, tighter check-ins). The next sprint's velocity rebounds to 95% of typical. The intervention gets credited with the "fix" — but a substantial part of that rebound would have happened anyway, purely from regression to the mean, since an unusually bad sprint is partly bad luck that doesn't repeat. Distinguishing "the intervention worked" from "this was regression" requires a control (did teams *without* the intervention also rebound similarly?) that almost never exists in practice, which is exactly why this misattribution is so common and so hard to catch from the inside.

**Worked example — performance review "improvement" after a bad quarter:** an engineer has an unusually rough quarter (multiple production incidents traced to their changes, several unlucky in nature — a flaky third-party dependency, an ambiguous spec they weren't given clear ownership to clarify). They're put on a performance improvement plan (PIP). The following quarter, their incident count returns to normal. The PIP gets credited — but some or most of the "improvement" may be regression: an unusually bad quarter partly reflects one-off bad luck that wouldn't have repeated whether or not a PIP existed. This doesn't mean PIPs never cause real improvement — it means the *observed* improvement is not, by itself, evidence the PIP caused anything, because regression alone would have produced a similar-looking pattern.

**Worked example — "our top performer plateaued" narrative:** an engineer who has an extraordinary first six months (fast promotion track, standout project) often appears to "slow down" or "plateau" afterward — this is frequently regression to the mean of their true underlying performance level, not an actual decline, but managers and the engineer themselves often construct anxious causal narratives ("did they lose motivation? did the promotion change something?") for what may be a purely statistical pattern.

### The correlation-causation trap, and regression as one specific instance
More broadly, this lesson connects to the general danger of inferring causation from correlation or from before/after comparisons without a control group. Regression to the mean is a particularly sneaky instance because it *specifically* produces a plausible-looking causal pattern (extreme result -> intervention -> improvement) exactly when there was no intervention effect at all, which is precisely the situation where causal stories feel most compelling (see WYSIATI, `thinking-fast-and-slow/08`).

### How to recognize regression risk
The diagnostic questions: (1) Was the initial observation unusually extreme relative to this entity's normal range? (2) Does the underlying quantity plausibly have a meaningful noise/luck component (yes for sprint velocity, incident counts, quarterly sales, individual game performance; less so for a controlled lab measurement with tight replication)? (3) Is there a control group or counterfactual that didn't receive the intervention, to check whether the "improvement" also happens without it? If (1) and (2) are true and (3) is absent, be very suspicious of any causal story built around the observed change.

## Pros
- Recognizing regression to the mean is a cheap, powerful skeptic's tool: it lets you question "our fix worked" narratives without needing to disprove them outright — just asking "was the before-measurement unusually extreme, and is there a control?" often reveals the causal claim was never actually supported.
- It protects people from unfair causal blame or credit — an engineer whose bad quarter partly reflects bad luck deserves that context in a performance conversation, and a process change that "worked" partly by luck shouldn't be over-credited and rolled out company-wide without a real controlled comparison.
- Understanding this pattern generally improves statistical literacy across many organizational decisions beyond the examples here — sales figures, customer satisfaction swings, individual athlete/performer "slumps" and "hot streaks."

## Cons
- Distinguishing real causal improvement from regression to the mean rigorously requires a control group or a designed comparison, which is often impractical or expensive to set up in a normal engineering org — you frequently can't get certainty, only informed suspicion.
- Overusing "that's probably just regression to the mean" as a reflexive dismissal can also be wrong and can demotivate genuinely effective interventions or unfairly dismiss real skill/effort — the tool cuts both ways and needs actual reasoning about noise levels, not blanket skepticism.
- The concept is genuinely counterintuitive and hard to explain to stakeholders in the moment ("no, the PIP might not have caused the improvement" is an unwelcome, hard-to-land message in a live performance conversation).

## Alternatives
- **A/B testing / controlled experiments** — the direct fix for the underlying inferential problem: run the intervention on a randomly selected subset and compare to a control group that didn't get it, which is the only reliable way to distinguish a real effect from regression.
- **Longer observation windows / trend analysis instead of single before/after snapshots** — looking at a rolling trend over many data points, rather than reacting to one extreme point followed by one more-average point, reduces the chance of over-reacting to noise in the first place.
- **Statistical process control (e.g., control charts from manufacturing quality methods)** — explicitly models the expected noise band around a metric so that a single extreme point is recognized as within normal variance, rather than triggering a causal-story-generating intervention.

## When to use it
Apply regression skepticism whenever you're tempted to credit (or blame) an intervention based on a single before/after comparison, especially when the "before" measurement was unusually extreme — sprint velocity swings, individual incident-count spikes, quarterly metric blips, standout or subpar individual performance periods.

## When NOT to use it
Don't use "it's probably just regression to the mean" to dismiss genuinely well-evidenced, controlled results (a properly randomized A/B test showing a sustained effect isn't regression, it's a real measured effect) — the concept applies specifically to uncontrolled before/after comparisons around extreme starting points, not to all improvement claims generally.

## Key takeaways / mental model
Before crediting or blaming any intervention for a change that followed an unusually extreme starting point, ask: "Would this have improved/declined anyway, just from statistical noise regressing toward the average — and do I have a control group to actually rule that out?" If you can't answer the control-group question, hold the causal claim loosely.

## Self-check questions
1. Explain the flight-instructor story in your own words: why did punished pilots seem to improve and praised pilots seem to decline, with zero real causal effect from either?
2. Describe a real "our intervention worked" story from your own team (a process change, a new tool, a performance plan) that followed an unusually extreme starting metric. How would you check whether it was a real effect or regression to the mean?
3. Why is the *presence* of a plausible causal story (the intervention, the criticism, the PIP) not, by itself, evidence that the story is actually correct? Connect your answer to WYSIATI from `thinking-fast-and-slow/08`.
4. Give an example of a metric in your engineering context that has a large noise component (and thus regresses heavily) versus one that's mostly stable/skill-driven (and thus regresses little). What does that difference imply about how much weight to put on a single data point from each?

## References
- Thinking, Fast and Slow (Daniel Kahneman), Part III: Chapters 17-18 ("Regression to the Mean," "Taming Intuitive Predictions").
