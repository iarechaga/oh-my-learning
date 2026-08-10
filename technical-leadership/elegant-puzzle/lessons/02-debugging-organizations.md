---
id: elegant-puzzle/02
subject: elegant-puzzle
title: Debugging organizations with systems thinking
slug: debugging-organizations
status: drafted
mastery:
seniority: staff
source: An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Organizations are the Way They Are for a Reason" and related essays
prerequisites: [elegant-puzzle/01]
created: 2026-08-10
updated: 2026-08-10
---

# Debugging organizations with systems thinking

## TL;DR
Organizations are the way they are for a reason -- usually a locally rational response to some past incentive, constraint, or crisis -- so debugging one means tracing a symptom back to that structural cause the same way you'd trace a production bug back to its root cause, rather than treating the symptom as an isolated character flaw of the people currently in the system.

## The idea
When something in an org looks obviously dumb -- a process everyone hates, a metric everyone games, a team that never ships on time -- the natural instinct is to assume the people involved are incompetent or that nobody has noticed the problem. Larson's argument is the opposite default assumption: assume the current state is a rational (if now-outdated) equilibrium given the incentives, history, and constraints that produced it, and go find what those were. This is the same discipline as production debugging: you don't assume the server is "just being weird," you assume there's a deterministic chain of cause and effect and you trace it. Organizations rarely have irrational actors at every layer; they have rational actors responding to the incentives and information they actually have, which can add up to a collectively bad outcome (a classic multi-agent systems problem, not a discipline problem).

## How it works

### Assume rationality, then find the constraint
Start from: "given what this team/person could see and was measured on, what made this the sensible choice?" A team that ships buggy code might be under a quarterly OKR that only counts features shipped, never counts defects found later -- so from inside that incentive structure, cutting corners is the locally rational move, even though it's globally bad. The fix targets the incentive (change what's measured), not a lecture about caring more about quality.

### Trace forward from a past decision
Many present-day oddities are fossils of a past decision that made sense at a different scale. A company of 30 engineers might not have needed a formal API-review process because everyone sat near each other and any conflicting change got caught in hallway conversation. At 300 engineers, the same lack of process produces silent breaking changes -- not because anyone got worse at their job, but because the informal mechanism that used to catch the problem stopped scaling long before anyone noticed it was load-bearing. Debugging means asking: "what informal mechanism used to compensate for the lack of formal structure here, and at what scale did it stop working?"

### Distinguish "broken" from "no longer fit for this scale"
A process that was correct at 20 people can be actively harmful at 200 -- not because it was ever wrong, but because organizations are scale-dependent systems, the same way an algorithm that's fine at N=100 can be unusable at N=1,000,000. The debugging question isn't "is this good or bad," it's "what scale was this designed for, and have we outgrown it?"

### Use "5 whys" on org symptoms, not just incidents
Take a concrete symptom -- "the mobile team keeps missing deadlines" -- and ask why, repeatedly, refusing to stop at the first answer:
1. Why? Estimates are consistently wrong.
2. Why? Scope keeps growing mid-sprint.
3. Why? Product keeps adding requirements after commitment.
4. Why? There's no agreed cutoff point where scope locks before an estimate is given.
5. Why? Planning and scoping happen in the same meeting, so nothing forces a scope-freeze moment.

The fix that falls out is structural -- separate the scoping conversation from the commitment conversation -- not "the mobile team needs to estimate better," which is the answer you'd have landed on by stopping at why #1.

### Watch for the symptom that moves instead of disappearing
When you "fix" a bottleneck and a new one appears immediately somewhere adjacent, that's diagnostic: it tells you the original fix addressed a downstream symptom of a deeper constraint (often total organizational capacity, or a single team everyone depends on) rather than the constraint itself. Treat a moved bottleneck as a clue pointing at the real cause, not as proof the fix failed.

## Pros
- Produces durable fixes instead of a string of one-off patches that keep needing to be redone.
- Depersonalizes conflict: framing a problem as "this incentive structure produces this behavior" is far easier for people to hear and act on than "you are the problem," and it's usually more accurate.
- Builds organizational memory -- understanding *why* something exists prevents you from reintroducing the same failure mode later when redesigning it.

## Cons
- Takes real investigative time; under deadline pressure, the "just fix the symptom now, investigate later" option is sometimes correct and "later" is often never.
- Assuming rationality can be taken too far and used to excuse genuinely broken behavior or bad-faith actors -- it's a strong prior, not an absolute law.
- Requires access to history and context (why was this built this way originally) that's often lost when the people who made the original decision have left.

## Alternatives
- **Symptom-level firefighting** -- fix what's visibly broken right now without asking why; faster in the moment, but the same symptom typically resurfaces because the structural cause is untouched.
- **Wholesale reorg / clean-slate redesign** -- discard the existing structure and start over rather than debug it; sometimes justified (see `elegant-puzzle/12`), but throws away whatever the old structure was correctly solving for, and that knowledge has to be relearned the hard way.
- **External consultant audit** -- bring in outside opinion to diagnose the org; useful for a truly fresh, unbiased perspective, but consultants lack the local incentive history insiders have and can misdiagnose structural fossils as current dysfunction.

## When to use it
Use this whenever a process, team boundary, or behavior looks obviously wrong from the outside and you're tempted to blame the people currently doing it. It's especially valuable before a reorg or process change, so you don't accidentally remove a mechanism that's quietly doing necessary work.

## When NOT to use it
Don't use this as a way to endlessly rationalize genuinely bad behavior or to avoid a needed, direct conversation about individual performance -- some problems really are about a specific person's skill or conduct, and dressing that up as a "systems issue" just delays the necessary intervention.

## Key takeaways / mental model
When something in the org looks dumb, ask "what was this a rational answer to?" before asking "who's responsible for this being broken?" Trace the symptom back with repeated "why," and treat a bottleneck that moves instead of disappearing as a sign you haven't found the real constraint yet.

## Self-check questions
1. Pick a process at your company that people complain about. What incentive, constraint, or past crisis would make that process the locally rational choice when it was introduced?
2. Run a 5-whys on a recurring complaint you've heard ("we always miss deadlines," "code review takes forever"). Where does the chain actually stop, and is that a structural cause or a personal one?
3. Describe a time you fixed a bottleneck and a new one appeared right next to it. What did that tell you about where the real constraint was?
4. When is "assume rationality" the wrong first move -- give a concrete example where the right call actually was to address an individual's behavior directly.

## References
- An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Organizations are the Way They Are for a Reason" and related essays in Part I.
