---
id: thinking-fast-and-slow/04
subject: thinking-fast-and-slow
title: Anchoring and adjustment bias
slug: anchoring-and-adjustment
status: drafted
mastery:
seniority: senior
source: Thinking, Fast and Slow (Daniel Kahneman), Part III, Chapter 11
prerequisites: [thinking-fast-and-slow/01, thinking-fast-and-slow/03]
created: 2026-08-10
updated: 2026-08-10
---

# Anchoring and adjustment bias

## TL;DR
Any number you're exposed to right before making a numerical estimate pulls your final answer toward it — even when the number is random, irrelevant, or you know it's irrelevant. In engineering, this means the first estimate spoken in a planning meeting, the ticket's original story-point guess, or even an unrelated number on the screen quietly sets the ceiling and floor for every subsequent estimate.

## The idea
Anchoring exists because estimating an unknown quantity is a hard question (`thinking-fast-and-slow/03`), and when a candidate number is already available, System 1 substitutes an easy question — "is the true value more or less than this number?" — and then makes an insufficient adjustment away from it. The adjustment stops too early because it, too, is effortful (System 2's job) and System 2 is lazy (`thinking-fast-and-slow/02`) — it stops adjusting as soon as the estimate feels plausible, not when it's actually correct. This matters because anchors don't need to be relevant, true, or even consciously registered to work — which makes anchoring one of the most exploitable (and self-inflicted) biases in any negotiation or estimation process.

## How it works

### The classic demonstration: the wheel of fortune experiment
Tversky and Kahneman's original study spun a rigged wheel (fixed to stop at either 10 or 65) in front of participants, then asked: "What is your best guess of the percentage of African nations in the UN?" Participants who saw the wheel land on 65 guessed a median of 45%; participants who saw it land on 10 guessed a median of 25%. The wheel was visibly random and had nothing to do with the UN — participants knew this — yet the anchor still shifted their answer by 20 percentage points. This is the signature of anchoring: it works even when the anchor is known to be uninformative.

### Two mechanisms: insufficient adjustment, and priming
Kahneman describes two distinct routes to the same effect. **Insufficient adjustment** happens when you deliberately start from the anchor and adjust (System 2 engaged, but stops too soon — this is the "anchoring-as-adjustment" original theory). **Anchoring-as-priming** happens even without any deliberate adjustment: the anchor number activates compatible information in memory (a high anchor selectively brings to mind reasons the true value could be high), biasing the final judgment automatically, via System 1, with no conscious adjustment step at all. Both mechanisms point to the same practical lesson — anchors work whether or not you're trying to resist them.

**Worked example — real estate agents:** in one of the book's studies, professional real estate agents toured a house and gave a valuation. Half were shown a listing price well above a reasonable estimate; half were shown one well below. Despite being experts who insisted price tags didn't influence their professional judgment, their estimates were anchored by roughly 41% of the difference between the high and low list prices — expertise did not eliminate the effect, and the agents were unaware it had happened to them.

### Anchoring in engineering estimation
**Worked example — sprint planning:** a ticket is created with a placeholder estimate of "3 points" by whoever filed it, before the team has actually discussed scope. In planning poker, even though everyone reveals estimates "simultaneously," the visible original ticket number, or the first person to say a number out loud, anchors the group discussion — final estimates cluster near that number even when a careful breakdown would justify 8 or 13 points. The fix used by disciplined teams (silent, simultaneous estimate reveal, discuss only when there's disagreement) exists specifically to break this anchor.

**Worked example — negotiating a delivery date:** a stakeholder asks "can this ship by Friday?" Even if Friday is unrealistic, simply having heard "Friday" anchors the engineer's own mental estimate — they're now unconsciously asking "how much later than Friday will this be" rather than "how long will this actually take from scratch," and the two questions produce systematically different (and the first, systematically lower) answers. This is why senior engineers are taught to give an independent bottom-up estimate *before* hearing any suggested date, not after.

**Worked example — salary negotiation:** whichever party states a number first in a compensation negotiation anchors the entire subsequent discussion — a first offer of $180k vs. $150k for a similar role shifts the final settled number by a large fraction of that $30k gap, even though "fair market value" is, in principle, an anchor-independent fact.

### Anchors compound: the "anchoring index"
Anchoring effects are measured by an "anchoring index" — the percentage of the gap between a high and low anchor that shows up in the final estimates. Values in the 30-60% range are typical across many domains (real estate, charitable donations, legal damage awards). The practical implication: anchors aren't a small nudge, they routinely account for a third to half of the variance in a "considered" numeric judgment — larger than most people would ever guess about themselves.

## Pros
- Anchors can be used deliberately and constructively: opening a negotiation with a well-justified, ambitious-but-defensible first number is a legitimate, well-documented tactic — you are the one setting the anchor others adjust from.
- Understanding the mechanism gives a cheap, high-leverage debiasing move: get independent estimates *before* any number is mentioned (see `thinking-fast-and-slow/14`), which is a low-cost process change with a large, well-evidenced payoff.
- Because anchoring is so consistent and well-replicated (unlike some other biases in this literature), it's one of the more trustworthy, actionable findings to build process around.

## Cons
- Anchoring is resistant to willpower and awareness — the real estate agents *knew* about anchoring risk and were still measurably anchored; you cannot reliably "just not be anchored" through effort alone.
- It's easy to overcorrect into paranoia about every number mentioned in a meeting, which slows down otherwise-healthy discussion; the mitigation is structural (silent estimation, independent first passes) not "never say a number out loud."
- Anchoring interacts with power dynamics — a junior engineer hearing a senior engineer's off-hand number gets anchored more strongly than a peer would, which can silently suppress legitimately different (and possibly more accurate) independent judgment.

## Alternatives
- **Reference-class forecasting (Flyvbjerg)** — instead of anchoring on an arbitrary first number, deliberately anchor on the *actual historical outcome distribution* of similar past projects; this converts an uncontrolled anchor into a deliberately chosen, evidence-based one (used heavily in `thinking-fast-and-slow/07`'s planning fallacy discussion).
- **Delphi method / structured independent elicitation** — collect estimates from multiple people independently and anonymously before any discussion, specifically to prevent early anchors (including social anchors like "what did the senior engineer say") from contaminating the group.
- **Range/interval estimation instead of point estimation** — asking for a 10th/90th percentile range rather than a single number reduces (though does not eliminate) anchoring, because a single point estimate is more anchor-sensitive than a deliberately considered range.

## When to use it
Recognize anchoring risk any time a number is going to be spoken before independent estimates are formed — sprint planning, delivery-date negotiation, salary negotiation, incident severity rating, story-point sizing. Deliberately sequence these conversations so independent judgments happen first, or deliberately set a favorable anchor yourself when you're the one negotiating.

## When NOT to use it
Don't treat "no anchor was given" as proof an estimate is unbiased — anchors can be implicit (the previous sprint's velocity, the ticket's default point value, a competitor's stated timeline) and still operate even when no explicit number was spoken; the absence of an obvious anchor doesn't mean the estimate is anchor-free.

## Key takeaways / mental model
Before any number-based judgment, ask: "what number did I hear or see most recently, and could my estimate just be a small adjustment away from it rather than an independent answer?" If a meaningful decision depends on an accurate estimate, get it *before* any number is mentioned, not after — sequencing beats willpower here.

## Self-check questions
1. Explain why the real estate agents' expertise didn't protect them from anchoring, and what that implies about "just be more careful" as a mitigation strategy.
2. Design a concrete process change for your team's sprint planning that would reduce anchoring on the ticket's original point estimate.
3. In a negotiation over a project deadline, would you rather state a number first or wait to hear the other side's number first? Justify your answer using the anchoring index concept.
4. A stakeholder says "I was thinking this would take about two weeks — what do you think?" What's wrong with directly answering that question, and what would you do instead?

## References
- Thinking, Fast and Slow (Daniel Kahneman), Part III: Chapter 11, "Anchors".
