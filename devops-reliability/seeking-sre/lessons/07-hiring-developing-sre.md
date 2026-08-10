---
id: seeking-sre/07
subject: seeking-sre
title: Hiring and Developing SRE Capabilities
slug: hiring-developing-sre
status: drafted
mastery:
seniority: staff
source: Seeking SRE (David Blank-Edelman, ed.), essay on building SRE talent without Google's applicant pool or infrastructure scale
prerequisites: [seeking-sre/01]
created: 2026-08-10
updated: 2026-08-10
---

# Hiring and Developing SRE Capabilities

## TL;DR
Copying Google's SRE hiring bar (deep distributed-systems expertise, competitive coding interviews against a huge applicant pool) is usually the wrong strategy for a smaller company — the higher-leverage approach is mostly growing SRE capability internally from strong generalist engineers who already understand your systems, supplemented by narrowly-targeted external hires for genuine skill gaps, because the scarcest and most valuable SRE trait at small scale is deep context on *your* specific systems, which no external hire arrives with.

## The idea
Google's SRE hiring model assumes a talent pipeline most companies don't have: enormous applicant volume, a globally recognized brand that attracts specialists, and internal systems complex and unique enough that a dedicated SRE discipline with its own hiring ladder makes sense. A 150-person company posting a job titled "Site Reliability Engineer" competes for a small, expensive pool of candidates who may have deep distributed-systems chops but zero context on the company's actual stack, and who often expect Google-like tooling and headcount that doesn't exist yet — a mismatch that produces expensive hires who are frustrated within two quarters.

The book's reframe: at smaller scale, SRE is more often a **capability you grow inside existing engineers** than a **role you recruit externally** for wholesale. This doesn't mean never hiring externally — it means being deliberate about which parts of the capability are genuinely best bought (rare, deep specialist knowledge) versus built (system context, process discipline, incident judgment).

## How it works

### What's cheap to build internally vs. genuinely hard to buy
**Cheap to build internally**: incident response process discipline (`seeking-sre/03`), postmortem facilitation skill, on-call judgment, SLO-setting for your own services, basic toil-reduction instincts. These all benefit enormously from deep context on your specific systems — a mid-level engineer who's owned a service for a year and gets trained in these skills usually outperforms an external senior SRE hire who's never seen your codebase, for at least the first six months.

**Genuinely hard to build internally, worth targeted external hiring**: deep expertise in a specific technology your team hasn't operated before (e.g., first-time Kubernetes migration, first-time multi-region database), large-scale distributed-systems failure-mode pattern recognition earned from having seen many different companies' outages, or genuinely novel practice-design work (building an SLO framework from scratch when no one internally has done it before).

### Worked example: growing versus buying at a 200-person company
A 200-person company decides it needs "more SRE." Two competing plans:
- *Buy-heavy plan*: hire 4 external SRE specialists, form a new team, expect them to define and operate reliability practices for the whole engineering org within two quarters. Risk: the new hires spend the first two quarters just learning the existing systems (which the org has zero documentation for, because tribal knowledge lived in the heads of the product engineers who built them), and meanwhile product engineers resent a new team parachuting in with opinions about systems they don't yet understand.
- *Build-heavy plan*: identify the 4-6 product engineers across teams who already show reliability instincts (they write good postmortems unprompted, they care about their service's on-call load), formally invest in their SRE skill development (dedicated time, mentorship, maybe one external senior SRE hire specifically to mentor and design the practice framework), and grow them into embedded or hybrid reliability roles (`seeking-sre/01`) over 2-3 quarters. This is slower to show results but produces reliability practitioners with deep system context from day one, and the one external specialist hire is used for maximum leverage (designing the framework, mentoring) rather than diluted across operational firefighting they don't yet have context for.
The book's clear preference, for most companies below a few hundred engineers, is closer to the second plan, with external hiring reserved for the specific, narrow gaps the first plan tries to solve with headcount alone.

### A leveling framework without Google's infrastructure scale
Google's SRE leveling (from an SRE handling a single well-understood service up to principal engineers designing reliability strategy across the whole company) assumes an unusually deep ladder. Smaller companies still benefit from *some* leveling, scaled down:
- **Junior/associate SRE-capable engineer**: owns on-call and SLOs for one service competently, writes good postmortems with light guidance.
- **Senior SRE-capable engineer**: owns reliability trade-offs across a small cluster of related services, mentors others, designs runbooks and escalation policy.
- **Staff-level reliability lead**: shapes org-wide practice (adoption model choices per `seeking-sre/01`, ownership boundaries per `seeking-sre/02`, executive communication per `seeking-sre/06`).
A company doesn't need five distinct levels to make this useful — even a 3-tier version gives engineers a visible growth path within reliability work, which matters because without one, your best-developed internal reliability talent is a flight risk to companies that do offer a formal SRE career ladder.

### Interviewing for reliability capability without a Google-style bar
Instead of testing distributed-systems trivia or asking candidates to whiteboard a system they've never operated, the book favors scenario-based interviewing grounded in judgment: walk a candidate through a realistic incident from your own systems (anonymized), and evaluate their diagnostic questions, their instinct to look for systemic causes rather than blame, and how they'd prioritize a fix versus a workaround under time pressure. This screens for exactly the judgment that transfers, regardless of whether the candidate has ever seen your specific tech stack before.

## Pros
- Avoids expensive, high-attrition-risk external hires who lack the system context that's actually the scarcest resource at small scale.
- Builds a visible growth path for existing engineers, improving retention of people who are already effective and already understand your systems.
- Concentrates scarce external-specialist hiring on the specific gaps (novel technology, novel practice design) where it has the most leverage.

## Cons
- Slower to show results than hiring a ready-made external team, which can be a hard sell to leadership under pressure to "fix reliability now."
- Requires genuine investment (dedicated time, mentorship, sometimes an external hire specifically to mentor) — growing capability isn't free just because it isn't a big headcount line item.
- Risks under-investing in genuinely rare expertise if "grow internally" is used as an excuse to avoid a necessary, narrowly-scoped specialist hire (e.g., a first-time multi-region database migration really does benefit from someone who's done it before).

## Alternatives
- **Buy-heavy: hire a fully-formed external SRE team wholesale** — faster to stand up on paper, appropriate when the company has genuine urgency (a major reliability crisis threatening the business) and can't wait for internal growth timelines; carries the context-gap and resentment risks described above.
- **Contract/consulting engagements instead of hiring** — bring in external SRE expertise time-boxed to design the practice framework (see the consulting model in `seeking-sre/01`) without a permanent headcount commitment; good for one-time practice-design gaps, weaker for ongoing operational capability.
- **Cross-training via rotation programs (engineers rotate through a central SRE function temporarily)** — spreads capability broadly across the org rather than concentrating it in a few people; effective at scale but requires enough central-function maturity to run a rotation program well.

## When to use it
Default to internal capability-building for most reliability skill gaps at companies under a few hundred engineers, reserving external hiring for genuinely rare expertise (novel technology, practice design from scratch) or genuine urgency that internal growth timelines can't meet.

## When NOT to use it
Don't rely purely on internal growth when facing a genuinely novel technical challenge no one internally has ever handled (first large-scale multi-region migration, first real security-incident response at scale) — that's exactly the "hard to build, worth buying" case this lesson carves out. And don't stretch a single external senior hire so thin doing hands-on firefighting that they never get to do the higher-leverage mentoring and framework-design work that justified hiring externally in the first place.

## Key takeaways / mental model
Ask, for any reliability skill gap: is this deep system context (cheap to build internally, expensive to buy) or rare specialist expertise (expensive to build internally, worth buying)? Default to growing your own for the former, hire narrowly and deliberately for the latter, and give internally-grown reliability talent a visible leveling path so your best people don't leave for a company with a more formal SRE ladder.

## Self-check questions
1. A company hires 4 external SRE specialists expecting them to fix reliability within two quarters, but the new hires spend most of that time just learning undocumented systems. What does this lesson say went wrong, and what would the "build" alternative have looked like?
2. Give an example of a skill gap that genuinely is "hard to build internally, worth buying," and explain why system context wouldn't substitute for it.
3. Why does the lesson recommend scenario-based interviewing (walking through a real, anonymized incident) over distributed-systems trivia questions when screening for reliability capability at a smaller company?
4. Your best internally-grown reliability engineer is being recruited by a competitor with a formal SRE career ladder. What does this lesson suggest you should have already had in place to reduce that risk?

## References
- Seeking SRE (David Blank-Edelman, ed.), essay on building SRE talent without Google's applicant pool or infrastructure scale.
- See also `seeking-sre/01` (adoption models, since the model chosen shapes what kind of hiring makes sense) and `seeking-sre/03` (incident response maturity, a core internally-buildable skill referenced here).
