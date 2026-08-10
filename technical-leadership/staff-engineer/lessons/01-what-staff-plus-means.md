---
id: staff-engineer/01
subject: staff-engineer
title: What staff-plus means and how impact is evaluated
slug: what-staff-plus-means
status: drafted
mastery:
seniority: staff
source: Staff Engineer: Leadership Beyond the Management Track (Will Larson), Introduction and Chapter 1
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# What staff-plus means and how impact is evaluated

## TL;DR
"Staff-plus" is a shorthand for the tier of individual-contributor (IC) roles above senior engineer — staff, senior staff, principal, distinguished, and so on — where the job stops being "write more code, faster" and becomes "make the organization's engineering effective at a scale beyond what you can personally touch." Impact at this level is judged not by lines of code or tickets closed but by leverage: how much better other engineers, teams, and the business perform because you exist.

## The idea
Most engineering ladders have an implicit assumption baked in below senior: you get better by doing more of the same thing, faster and with fewer mistakes. A senior engineer writes more reliable code, unblocks themselves more often, and needs less oversight than a mid-level engineer, but the *shape* of the job — write code, review code, fix bugs, ship features — stays the same from junior to senior.

Staff-plus breaks that pattern. The job stops being about personal throughput and starts being about organizational throughput. A staff engineer who spends a quarter heads-down writing a single feature, however well-crafted, has usually under-performed relative to a staff engineer who spent that quarter identifying that three teams were about to independently build incompatible solutions to the same problem, wrote a short design doc, and got them aligned on one approach before any code was written. The second engineer wrote far less code and produced far more value, because their output was leverage rather than volume.

This creates a real problem for companies: the criteria that made someone a great senior engineer (fast, correct, self-directed execution) do not predict whether they will be a great staff engineer (judgment about what's worth doing, ability to influence people who don't report to them, willingness to operate with less certainty over longer time horizons). Larson wrote the book precisely because, as of the early 2020s, most companies had no shared, explicit definition of what staff-plus engineers actually do — the title existed on organization charts, but the day-to-day job was invented independently, badly, by each new staff engineer through trial and error. This lesson (and the rest of the subject) exists to shortcut that trial and error.

## How it works

### The three-part definition of staff-plus scope
Larson defines staff-plus roles as sitting at the intersection of three things:
1. **Scope beyond a single team.** A senior engineer's scope is usually their team's roadmap. A staff engineer's scope is a *problem area* — reliability across the payments stack, the migration off a legacy monolith, the developer-experience story for the whole engineering org — that no single team owns end to end.
2. **Complexity that requires judgment, not just skill.** The technical problems staff engineers pick up are the ones without a known playbook: ambiguous, cross-cutting, politically loaded, or requiring trade-offs between teams that have conflicting incentives.
3. **Organizational trust.** Staff-plus engineers are given latitude — to set direction, to say no to a VP's pet project, to represent engineering in a room without a manager present — because their judgment has been proven over time. This trust is earned, not granted by title, and it can be spent down by bad calls.

If any one of these three is missing — someone with cross-team scope but no real trust, or deep technical complexity confined to one team — the role isn't really operating as staff-plus yet, whatever the job title says.

### How impact is actually evaluated
Because the job is leverage, not volume, the evaluation questions change:
- **Not:** "How many projects did they ship?" **But:** "Did the organization avoid a costly mistake, or move faster, because of a decision they made?"
- **Not:** "How much code did they write?" **But:** "How many other engineers now make better decisions because of a document, review, or piece of mentorship they provided?"
- **Not:** "Are they busy?" **But:** "Did they work on the highest-leverage problem available, or a comfortable one?"

**Worked example.** Two staff engineers at the same company, same quarter:
- Engineer A rewrites their team's caching layer, cutting p99 latency by 30%. High-quality, visible, personally executed work — the kind of thing that would have gotten them promoted from mid to senior.
- Engineer B notices that four teams are each about to build their own retry/backoff logic for calls to a flaky downstream service, each slightly wrong in a different way. They spend two weeks writing a shared library, a design doc explaining the failure modes it handles, and personally review each team's integration. No single line of code they wrote goes into a customer-facing feature.

By senior-engineer evaluation criteria, A looks more impressive. By staff-plus criteria, B's work is more valuable: it prevented four separate outages-in-waiting, saved roughly eight team-weeks of duplicated effort, and left behind institutional knowledge (the design doc) that keeps paying off after B moves to the next problem. This is the leverage lens the rest of this subject teaches you to apply to your own work.

### Impact compounds through other people
The mechanism behind leverage is almost always "worked through other people." A staff engineer's calendar looks different from a senior engineer's: more 1:1s with engineers on teams they don't manage, more design-review comments, more time spent writing documents meant to be read by people who will never talk to the author directly. This isn't overhead distracting from "real work" — for a staff-plus engineer, this *is* the real work, because it's the mechanism by which one person's judgment reaches a hundred engineers instead of just their own hands.

## Pros
- Gives engineers who don't want to manage people a legitimate, well-defined path to senior organizational influence and compensation.
- Concentrates judgment on the hardest, highest-ambiguity problems in exactly the people who have the technical depth and organizational memory to handle them well.
- Creates a feedback loop where good decisions get systematized (via docs, tools, mentorship) instead of staying locked in one person's head.

## Cons
- The leverage-based definition is inherently harder to measure than "tickets closed," which makes performance reviews, promotion cases, and even day-to-day self-assessment genuinely ambiguous — reasonable people can disagree about whether a given quarter was high-impact.
- Because impact is diffuse and delayed, it's easy for a staff-plus engineer to drift into looking busy (many meetings, many docs) without actually moving anything that matters — see `staff-engineer/12` on this trap.
- Companies without a clear staff-plus definition (which was most companies before this book, and many still) leave new staff engineers to reinvent the job by trial and error, which wastes the company's investment in them and is demoralizing for the engineer.

## Alternatives
- **Pure technical-depth ladders (e.g., "Distinguished Engineer as the best coder in the building")** — some companies define staff-plus almost entirely around technical depth rather than organizational leverage; this works for research-heavy or deeply technical domains but tends to under-value the influence and alignment work Larson argues is central to the role at most product companies.
- **Management as the only senior path** — the traditional alternative to a staff-plus ladder is simply funneling all senior engineers into people management. This conflates two genuinely different skill sets (people management vs. technical leadership) and pushes engineers who are excellent at the latter but uninterested in or bad at the former either into a job they don't want or out of the company.
- **Title inflation without scope change** — some companies hand out "staff" titles as a retention lever without changing what the person actually does day to day. This produces a "staff engineer" who is really a senior engineer with a bigger number on their offer letter, and it erodes the credibility of the title across the industry.

## When to use it
Use this lens — leverage over volume, organizational scope over team scope — whenever you're evaluating your own priorities as a senior-plus engineer, writing a promotion case, or trying to understand why "just work harder/write more code" stopped being the advice that helped you grow.

## When NOT to use it
Don't apply staff-plus evaluation criteria to yourself prematurely if you're not yet operating with cross-team scope and organizational trust — chasing "leverage" work before you've built a track record of excellent execution at the team level tends to produce vague, unaccountable-looking work rather than real influence. Build the trust first (see `staff-engineer/05`).

## Key takeaways / mental model
Ask of any week's work: "if I disappeared, would only my own output be missing, or would other people's decisions get worse too?" Senior-engineer impact disappears with the engineer. Staff-plus impact should persist in the judgment, tools, and alignment left behind in other people.

## Self-check questions
1. Think of a piece of work you did in the last few months. Was its impact personal (it stopped existing the moment you stopped working on it) or organizational (it changed how other people work, even after you moved on)? What would have made it more of the latter?
2. Why does Larson argue that "write more code, faster" is *not* the right growth advice past senior engineer, when it was exactly the right advice from junior to senior?
3. Describe a situation where the three-part definition (cross-team scope, judgment-requiring complexity, organizational trust) would say someone with a "staff engineer" title is not actually operating as staff-plus yet. What's missing?
4. Give an example of "looking busy" (many meetings, many docs) versus "being high-leverage" at your own company. What's the concrete difference in outcome between the two?

## References
- Staff Engineer: Leadership Beyond the Management Track (Will Larson), Introduction and Chapter 1: "What is a staff engineer?"
