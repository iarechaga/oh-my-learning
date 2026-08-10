---
id: elegant-puzzle/10
subject: elegant-puzzle
title: Feedback systems and performance management
slug: feedback-and-performance-systems
status: drafted
mastery:
seniority: staff
source: An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Giving Feedback" and "Managing Underperformance"
prerequisites: [elegant-puzzle/09]
created: 2026-08-10
updated: 2026-08-10
---

# Feedback systems and performance management

## TL;DR
Feedback and performance management work best as a continuous, low-latency system (frequent, specific, close-to-the-event feedback) rather than a once-or-twice-a-year batch process; underperformance is handled well when it's named early, tied to specific, agreed-upon evidence, and given a real, time-boxed chance to improve, not sprung on someone at review time.

## The idea
A performance-review cycle that happens once or twice a year has an enormous latency problem: feedback about something that happened in February, delivered in a June review, arrives too late for the person to have adjusted their behavior in the intervening months, and by then neither party remembers the specifics well enough to discuss it usefully. Treating feedback as a system means minimizing that latency -- delivering signal close to the event it's about, in small, frequent doses, so course-correction happens continuously rather than in an annual batch. Performance management -- specifically, handling underperformance -- follows the same logic: waiting until a formal review to name a problem that's been visible for months is unfair to the employee (who had no chance to fix it) and expensive to the org (months of continued underperformance that better, earlier feedback could have addressed).

## How it works

### Feedback: frequent, specific, close to the event
Effective feedback names a specific behavior or outcome ("in yesterday's design review, you dismissed Priya's alternative without engaging with her reasoning"), not a vague trait ("you're not collaborative enough") -- specific feedback is actionable because the person knows exactly what to do differently next time, while trait-level feedback leaves them guessing which of many possible behaviors to change. Delivering it close to the event (same week, ideally) means the details are fresh for both parties and the person still has many upcoming opportunities to apply the correction, rather than receiving it long after most of the relevant opportunities have passed.

**Positive feedback matters as much as corrective feedback.** A feedback system that only fires when something's wrong teaches people to dread feedback conversations and gives them no signal about what to keep doing. Naming specific things that went well, with the same specificity as corrective feedback, reinforces good behavior and builds the trust that makes corrective feedback land better when it's needed.

### The SBI-style structure for a hard conversation
A useful structure for delivering corrective feedback: **Situation** (when and where), **Behavior** (what specifically was observed, factually, not interpreted), **Impact** (what effect it had). "In yesterday's planning meeting (situation), you interrupted three different people mid-sentence to redirect to your own point (behavior), which meant we didn't hear two proposals that might have changed the plan (impact)." This structure keeps feedback anchored to observable fact rather than character judgment, which is both more accurate and far less likely to trigger a defensive reaction that shuts down the conversation before the person can actually hear it.

### Underperformance: name it early, with specific evidence
The single biggest failure mode in managing underperformance is delay: a manager notices a pattern, hopes it resolves on its own, avoids the uncomfortable conversation, and by the time it's formally addressed (often at review time), months have passed with no chance for the employee to course-correct, and often no memory of the specific incidents that would make the feedback concrete. Larson's guidance: name the pattern the first time it's clearly recognizable, with specific evidence, not the first time it becomes undeniable.

### A real improvement plan has structure, not just a warning
Once underperformance is named, an effective response has: specific, observable success criteria (not "improve your communication" but "in the next three sprint plannings, come with a written proposal reviewed by a peer before presenting"); a defined, bounded timeframe (typically 30-60-90 days, not open-ended); regular check-ins within that window (not just a single re-evaluation at the end); and clarity about the consequence if the criteria aren't met, stated up front rather than as a surprise at the end. A plan missing any of these pieces tends to fail either the employee (unclear what "success" would even have looked like) or the organization (the process drags indefinitely with no resolution).

**Worked example.** An engineer has repeatedly shipped code with insufficient test coverage, flagged in code review each time but never structurally addressed. A named, specific improvement plan: "over the next 6 weeks, every PR you submit must include tests covering the changed logic before requesting review; we'll check in every two weeks; if this pattern continues past the 6 weeks, the next step is [specific consequence]." This gives the employee an unambiguous target and a real chance, and gives the manager (and, if needed, HR) clear, contemporaneous documentation of what was communicated and when.

### Feedback and performance management as an org-level system, not just an interpersonal skill
Beyond any single manager's skill at delivering feedback, the org needs a system that ensures this happens consistently: regular 1:1 cadences that create a natural venue for frequent feedback, a performance-review process calibrated across managers (`elegant-puzzle/09`) so that "meets expectations" means the same thing regardless of manager, and psychological safety norms that make it normal to give and receive feedback without it being read as a crisis every time.

## Pros
- Frequent, low-latency feedback lets people course-correct while there's still time for it to matter, instead of learning about a months-old problem too late to act on it.
- Naming underperformance early, with specific evidence, is fairer to the employee than a surprise negative review, and gives them an actual chance to improve.
- A structured improvement plan protects both the employee (clear target, real chance) and the organization (documented, defensible process if it ultimately doesn't work out).

## Cons
- Frequent, specific feedback takes real time and emotional energy from managers, especially corrective feedback, which many managers avoid delivering promptly precisely because it's uncomfortable.
- Overly frequent or excessively granular feedback can tip into micromanagement, undermining the autonomy that lets skilled people do their best work.
- Formal improvement plans, done wrong (vague criteria, no real check-ins, treated as a pre-decided path to termination rather than a genuine chance), can become a box-checking exercise that doesn't actually help anyone and damages trust across the team when others see it happen.

## Alternatives
- **Annual/semi-annual review cycles only** -- lower manager overhead day-to-day, but reintroduces the latency problem this lesson describes: feedback arrives too late to be actionable, and underperformance goes unaddressed for the longest possible stretch.
- **360-degree feedback processes** -- gather feedback from peers, reports, and other stakeholders in addition to the manager, giving a broader, more triangulated signal, especially useful for catching blind spots a single manager wouldn't see; heavier-weight and slower than direct manager feedback, so best used to supplement continuous feedback, not replace it.
- **Radical Candor-style "challenge directly, care personally" framing** -- a specific philosophy for how to deliver feedback (Kim Scott's framework), emphasizing directness paired with visible personal care; compatible with and complementary to the SBI structure above, focused more on tone and relationship than on process structure.

## When to use it
Build frequent, specific feedback into regular 1:1 cadences for every report, and name underperformance the first time a pattern is clearly recognizable rather than waiting for a formal review cycle. Use a structured improvement plan whenever informal feedback on a specific issue hasn't produced change after a reasonable, explicit attempt.

## When NOT to use it
Don't escalate straight to a formal improvement plan for a single mistake or a first occurrence of an issue -- that's disproportionate and erodes trust; informal, specific feedback is the right first tool, with a formal plan reserved for a pattern that's persisted despite that informal feedback.

## Key takeaways / mental model
Treat feedback latency as a cost: the longer between the event and the feedback, the less useful it is and the more it costs to hear. For underperformance specifically, ask "would this person be surprised by this being named at review time?" -- if yes, that's a sign it should have been named much earlier, with specific evidence, while there was still time to act on it.

## Self-check questions
1. Rewrite a vague piece of feedback ("be more proactive") into a specific, SBI-structured version using a plausible concrete scenario.
2. Why does delaying corrective feedback to a formal review cycle harm both the employee and the organization? Name both costs specifically.
3. Design the four required components of a real improvement plan for a hypothetical case of an engineer who consistently misses sprint commitments. What would make this plan real rather than a box-checking exercise?
4. A manager says "I give feedback constantly, but nothing changes." What would you check about how that feedback is being delivered before assuming the employee is the problem?

## References
- An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Giving Feedback" and "Managing Underperformance", Part IV.
