---
id: how-to-measure-anything/01
subject: how-to-measure-anything
title: Why "intangibles" are usually measurable enough for decisions
slug: intangibles-are-measurable
status: drafted
mastery:
seniority: senior
source: How to Measure Anything (Douglas W. Hubbard), Chapter 1-2
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# Why "intangibles" are usually measurable enough for decisions

## TL;DR
"That's intangible, you can't measure it" is almost always false — it confuses "I don't currently know how to measure this" with "this cannot be observed to differ." If something matters to a decision, it must have some observable effect on the world, and that effect can be measured, at least well enough to reduce uncertainty and make a better decision than guessing.

## The idea
Engineering and product leaders reject measurement constantly with variations of "you can't quantify developer happiness," "you can't measure architectural quality," or "you can't put a number on brand reputation." Hubbard's core provocation is: if the thing is completely unmeasurable — if it has literally zero observable consequences — then by definition it cannot matter to any decision, because a decision-relevant thing must, by the very fact that it's relevant, produce some difference in outcomes that could in principle be detected. If developer happiness matters, it shows up somewhere: attrition, time-to-hire replacements, code review turnaround, sick days, exit interview themes, applicant referral rates. If architectural quality matters, it shows up in defect rates, deployment frequency, time to onboard a new engineer, or incident frequency. The perceived unmeasurability usually comes from three specific, fixable misconceptions, not from the thing being genuinely beyond observation.

The three misconceptions Hubbard names:
1. **Concept of measurement is wrong.** People assume measurement means achieving certainty — a single exact number with zero error. Actually measurement is any observation that reduces uncertainty, even partially.
2. **Object of measurement is misunderstood.** People try to measure "quality" or "reputation" as one big fuzzy blob instead of asking what specifically they mean, and what decision hinges on it.
3. **Methods of measurement are unknown.** People assume that because *they* don't know how to measure something, no method exists — but many methods (calibrated estimation, sampling, proxies, controlled experiments) are well established outside their own field.

## How it works

### Step 1: Ask "what do you mean by X?"
Take a claim like "we need to measure code quality." That word hides several different things a leader might actually care about: fewer production incidents, faster onboarding of new hires, lower long-term maintenance cost, easier feature addition. Each of these has directly observable proxies (incident count per quarter, weeks-to-first-merged-PR for new hires, hours spent on bug fixes vs. features). The reason "code quality" feels immeasurable is that it was never decomposed into what it actually means in context. This decomposition step is developed fully in lesson `how-to-measure-anything/04`, but the mental move starts here: intangibility is usually a symptom of vagueness, not of true unmeasurability.

### Step 2: Ask "what is the decision this would inform?"
A measurement with no decision attached is trivia. If your VP asks "how do we measure engineering culture?", the answer depends entirely on what decision is on the table. If the decision is "should we invest $2M in a platform team to reduce toil," the measurement that matters is toil hours per engineer per week and their downstream effect on delivery — not an abstract culture score. Tying every measurement to a specific decision (developed in `how-to-measure-anything/05`) filters out 90% of the "impossible to measure" complaints, because most of what people ask to measure was never going to change a decision anyway.

### Step 3: Ask "if this thing existed and varied, how would that variation show up?"
This is Hubbard's key move for anything that still feels abstract. Take "team trust." If trust is genuinely higher on Team A than Team B, what would you expect to observe as a *consequence*? Probably: less time spent double-checking each other's work, more willingness to raise concerns in retros (measurable via sentiment tagging of retro notes or simply counting raised concerns), lower rates of silently reverted decisions, faster consensus in design reviews (measurable in review thread length or time-to-approval). None of these individually *is* trust, but each is a partial, noisy observation of it — and several partial noisy observations combined reduce uncertainty a lot, even without ever directly "seeing" trust.

### Worked example: "Is our on-call rotation sustainable?" (engineering leadership)
A staff engineer is told "on-call burnout is intangible, we just have to go by vibes." Apply the method:
- **What do we mean?** Burnout, operationally, means: engineers dreading/avoiding on-call, degraded response quality, attrition risk.
- **What decision hinges on it?** Whether to hire another engineer into the rotation (cost: ~$180k/yr loaded) versus investing in reducing alert volume (cost: ~3 sprint-weeks of toil reduction work).
- **How would it show up if real?** Pages per week per engineer, percentage of pages resolved outside working hours, self-reported dread on a 1-5 scale in a lightweight quarterly survey (5 questions, 3 minutes), rotation opt-out requests, attrition of on-call-eligible engineers vs. non-eligible engineers over the last 4 quarters.
None of these alone is "burnout." But if pages/week is 12 (vs. an industry-informed comfortable threshold of ~2-3), 40% of pages land after 10pm, and 3 of 8 rotation engineers have asked to be removed in the last two quarters — that is a strong, decision-actionable, *quantified* signal, obtained without ever having a perfect definition of "burnout."

## Pros
- Breaks the paralysis of "we can't act because we can't measure it," which otherwise defaults decisions to whoever argues loudest (HiPPO — highest paid person's opinion).
- Forces precision about what a stakeholder actually means, which alone often resolves half the disagreement before any data collection starts.
- Cheap to start: the reframing costs nothing and often reveals that useful proxy data already exists in ticketing systems, calendars, or surveys.

## Cons
- Overzealous decomposition can produce a pile of proxies that individually mean little and collectively give false confidence if not combined carefully (see Bayesian updating in `how-to-measure-anything/08`).
- Stakeholders sometimes resist because "intangible" is being used defensively — to avoid accountability for a decision — and a measurement proposal threatens that. This is a political problem, not a measurement problem, and no amount of methodology fixes it alone.
- Choosing bad proxies (e.g., lines of code as a proxy for productivity) can be worse than no measurement, because a bad number often displaces the vaguer-but-more-honest judgment it replaced.

## Alternatives
- **Refuse to measure and decide by expert judgment alone** — sometimes appropriate for genuinely one-off, low-stakes, or truly ambiguous decisions where the cost of measuring exceeds any plausible benefit (see `how-to-measure-anything/09` on value of information); the mistake is treating this as the default rather than a deliberate choice.
- **Full formal metrics program before any decision is made** — the opposite failure: building an elaborate dashboard for something that never actually needed to be measured, which wastes effort the decomposition-first approach in this lesson would have prevented.
- **OKR-style qualitative-plus-confidence scoring** — some orgs use a hybrid of narrative plus a self-rated confidence score instead of a real measurement; it's faster to produce but doesn't reduce uncertainty the way an actual observation does — useful as a stopgap, not a substitute.

## When to use it
Whenever someone declares a decision-relevant factor "impossible to measure" — culture, quality, risk, morale, technical debt, brand. Use it as the very first move before reaching for any statistical technique: it reframes the problem from "is this measurable" (almost always yes) to "what specifically should we observe, and is it worth the cost" (the real question).

## When NOT to use it
Don't invoke this reframing as an excuse to measure things with no attached decision — chasing measurability for its own sake burns time and credibility. Also skip it for decisions that are genuinely reversible and cheap to try directly (just run the experiment / ship the change and observe the outcome) rather than building an elaborate proxy-measurement plan first.

## Key takeaways / mental model
"Immeasurable" almost always decomposes into "vaguely defined" plus "no decision attached" plus "I haven't thought about how it would show up in observable data." Answer those three questions — what do you mean, what decision depends on it, how would it show up if real — and a path to a useful (not perfect) measurement almost always appears.

## Self-check questions
1. Pick something your team currently calls "impossible to measure" (e.g., "technical debt," "team velocity," "stakeholder trust"). Walk through the three questions from this lesson and propose at least three observable proxies.
2. Explain, in your own words, why something that has zero observable consequences cannot matter to any decision.
3. A colleague says "customer delight is a feeling, you literally cannot put a number on a feeling." How would you respond using this lesson's framework, without being dismissive of the underlying concern?
4. Give an example from your own experience where a proxy measurement was worse than no measurement at all. What made it worse?

## References
- How to Measure Anything: Finding the Value of Intangibles in Business (Douglas W. Hubbard), Chapter 1: "The Challenge of Intangibles," and Chapter 2: "An Intuitive Measurement Habit: Eratosthenes, Enrico, and Emily."
