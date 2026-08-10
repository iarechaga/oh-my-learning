---
id: managers-path/05
subject: managers-path
title: Giving feedback and managing performance conversations
slug: feedback-and-performance
status: drafted
mastery:
seniority: staff
source: The Manager's Path (Camille Fournier), Chapter 4 - Managing People
prerequisites: [managers-path/04]
created: 2026-08-10
updated: 2026-08-10
---

# Giving feedback and managing performance conversations

## TL;DR
Feedback works only when it is specific, timely, and delivered as an ongoing habit rather than saved up for a formal review - by the time an annual review happens, both positive and negative feedback should already be old news to the report, not a surprise.

## The idea
The single biggest feedback failure Fournier calls out is the "surprise" - a performance review, or worse a performance improvement plan (PIP) or termination, that lands as news to the person receiving it. If a manager has been sitting on concerns for months and only raises them at a formal review, that is a management failure, not a performance failure: the report was denied months of opportunity to actually improve, because nobody told them there was a problem while it was still fixable. Feedback's entire value is in its timeliness - the closer it is to the behavior it addresses, the more useful and less emotionally loaded it is for the recipient to act on.

The second core idea is that feedback must be specific and behavioral, not a vague trait judgment. "You need to be more of a team player" gives the recipient nothing actionable - what should they actually do differently tomorrow? "In yesterday's design review, you interrupted Sam twice before he finished his point, and the team moved on without hearing his idea" is specific enough to change behavior, because it names the exact moment and the exact effect, without requiring the recipient to guess what the manager actually meant.

## How it works

### Positive feedback is not optional or secondary
New managers often over-focus on corrective feedback because it feels like "the real work" of managing performance, and under-deliver positive feedback because it feels less urgent. Fournier's guidance: specific positive feedback is just as important - it tells someone what to keep doing (which is just as useful as knowing what to stop doing) and it's what makes the harder, corrective feedback land well later, because the relationship isn't purely associated with criticism. Concrete example: instead of a generic "good job this sprint," say "the way you broke the migration into small, reversible steps meant we caught the schema issue before it hit production - that's exactly the caution I want to see on risky changes."

### Use a structure that separates observation from judgment
A useful pattern (not unique to this book but consistent with its advice): state the specific, observable behavior, then the concrete impact it had, then what you'd like to see instead. "When the deploy went out without a rollback plan (behavior), we had no fast way back when it broke checkout for twenty minutes (impact) - going forward, I want every production deploy to have a written rollback step before it ships (ask)." This avoids vague character judgments ("you're careless") that the recipient can only get defensive about, not act on.

### Corrective feedback needs to happen close to the event, not batched
If an engineer repeatedly ships code without tests, the manager who mentions it once at the next monthly 1:1, after it's happened five times, has let a fixable pattern become an established habit and a much harder conversation. The fix is raising it the first or second time it happens, specifically and kindly, while it's still a small correction rather than a pattern requiring a formal process.

### Formal performance management (PIPs) is a last resort, not a surprise tool
When informal, ongoing feedback hasn't produced a change, and the gap is serious enough to threaten the person's role, a formal performance improvement plan documents specific expectations, a timeline, and support offered - but it should never be the report's first indication that there's a serious problem. Fournier is direct that a PIP sprung on someone with no prior warning is a sign the manager failed at the ongoing-feedback habit, not that the report suddenly failed. A well-run PIP has clear, measurable goals, a defined check-in cadence, and genuine support (not just a paper trail to justify a decision already made).

### Calibrate feedback to the person and the relationship
Some people want direct, blunt feedback; others need it delivered more gently to actually hear it rather than shut down defensively. This isn't about lowering the bar of honesty - it's about packaging the same honest content so it actually lands, which requires knowing the person (built through the 1:1 trust loop in `managers-path/04`).

## Pros
- Prevents the single most damaging management failure - a report blindsided by a negative review or a PIP with no prior warning - which destroys trust in the manager and often the company.
- Specific, behavioral feedback is directly actionable, unlike vague trait-based feedback, so it actually changes behavior rather than just producing defensiveness.
- Regular positive feedback reinforces good patterns and makes the relationship resilient enough to absorb necessary corrective conversations without it feeling purely punitive.

## Cons
- Requires real-time attention and discipline - it's easy to let small issues slide "this once" repeatedly until they've compounded into a real problem that's now harder to raise.
- Delivering specific, honest feedback well is a skill that takes practice; done poorly (too vague, too harsh, too infrequent) it can damage trust rather than build it.
- Cultural and individual variation in how feedback lands means there's no single script that works for everyone - requires ongoing calibration per person.

## Alternatives
- **360-degree feedback processes** - gather feedback from peers, not just the manager, giving a fuller picture and reducing reliance on any single observer's blind spots; heavier-weight and typically used for formal review cycles rather than day-to-day correction.
- **Radical Candor's "Care Personally, Challenge Directly" framework** (Kim Scott) - a complementary model for calibrating how directness and personal care combine in a single piece of feedback; useful as a lens on top of Fournier's specificity/timeliness advice.
- **Peer feedback / code review as feedback channel** - distributes some feedback delivery away from the manager entirely (e.g., strong code review culture correcting technical habits), reducing the manager's sole burden but requiring a healthy team culture to work well (see `managers-path/06`).

## When to use it
Continuously - both positive and corrective feedback should be a running habit tied to specific events (ideally within days), not saved for scheduled reviews. Use the more formal PIP process only after repeated informal feedback has failed to produce change and the gap is serious enough to threaten the role.

## When NOT to use it
Don't deliver feedback as a vague trait judgment ("be more proactive") without a specific behavioral example - it will not produce change and often produces resentment instead. Don't stack up months of unaddressed issues and deliver them all at a formal review - that is precisely the "surprise" failure this lesson is built to prevent, and by the time it happens the report has lost the chance to fix things while it still mattered.

## Key takeaways / mental model
Nothing in a formal review should be new information - feedback's whole value is in being specific, behavioral, and close to the event it addresses; treat it as a constant low-grade habit, not a quarterly event, and the hard conversations become smaller and less shocking when they do have to happen.

## Self-check questions
1. Rewrite this vague piece of feedback into specific, behavioral feedback: "You need to communicate better with the team."
2. Why does Fournier treat a surprise PIP or negative review as a failure of the manager, not (only) the employee?
3. A report on your team keeps missing small details in code review that create bugs later. Walk through how and when you'd raise this, using the observation/impact/ask structure.
4. How does the 1:1 trust loop from `managers-path/04` change how corrective feedback is likely to land, compared to a manager who rarely talks to the report one-on-one?

## References
- The Manager's Path (Camille Fournier), Chapter 4: "Managing People".
