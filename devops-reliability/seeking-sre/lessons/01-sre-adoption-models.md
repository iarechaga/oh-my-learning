---
id: seeking-sre/01
subject: seeking-sre
title: Choosing an SRE Adoption Model for Your Organization
slug: sre-adoption-models
status: drafted
mastery:
seniority: staff
source: Seeking SRE (David Blank-Edelman, ed.), essay on adopting SRE without Google's scale
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# Choosing an SRE Adoption Model for Your Organization

## TL;DR
There is no single "correct" SRE org chart — Google's centralized, headcount-heavy SRE org is one point in a design space, not the definition of SRE. The real decision is which of a handful of adoption models (embedded, centralized/platform, consulting/enablement, or hybrid) matches your company's size, growth rate, and existing team trust, and that choice should be revisited as the company changes rather than treated as permanent.

## The idea
"SRE" is frequently conflated with "the specific organizational structure Google uses for SRE," but the practices (SLOs, error budgets, blameless postmortems, toil reduction) are separable from the org chart that implements them. Google's model — a dedicated SRE org with its own hiring bar, sitting between product engineering and infrastructure, gatekeeping production access — evolved under conditions most companies never have: hundreds of internal services, a multi-decade head start, and enough headcount to staff dedicated reliability teams per major product area. A 40-person startup or a 300-person mid-size company copying that structure literally usually produces a cargo cult: a "SRE team" of two people who are actually just ops-with-a-rebrand, disconnected from product teams, drowning in tickets, unable to influence architecture early enough to matter.

The book's core reframe: adoption is a **model selection problem**. You're choosing where reliability expertise sits relative to the teams that build features, and that placement has predictable trade-offs in influence, scalability, and burnout risk. Picking the wrong model for your current size and culture is a common, expensive mistake — not because the practices are wrong, but because the org structure carrying them doesn't fit.

## How it works

### The four common models
**1. Embedded SRE.** SRE engineers sit inside product teams (e.g., one SRE embedded in the Payments team, another in Search). They write code, own the on-call rotation for that service, and are subject-matter experts on that team's reliability posture specifically.
- *Fits*: small-to-mid companies (roughly 50-300 engineers) with a handful of critical services, where you can't yet afford a standalone team and need reliability expertise close to the code that changes fastest.
- *Failure mode*: embedded SREs get pulled into feature work by their product manager because there's no separate reporting line protecting their time, and "SRE" quietly becomes "the engineer who also does ops." Six months later the on-call rotation is unsustainable because no one owns cross-team reliability standards.

**2. Centralized/platform SRE.** A single SRE team owns shared infrastructure (CI/CD, observability platform, incident tooling) and sets reliability standards that product teams must meet, but doesn't operate product services directly.
- *Fits*: mid-to-large companies (300+ engineers) with enough services that per-team reliability work would duplicate effort — building one good deploy pipeline once beats each team building its own badly.
- *Failure mode*: becomes a bottleneck/gatekeeper team that product engineers resent ("we need SRE's sign-off to deploy"), especially if the platform team is under-resourced relative to the number of teams depending on it. Also risks losing context on any single service's actual failure modes.

**3. Consulting/enablement SRE.** A small team of experienced SREs doesn't own any service's on-call, but works time-boxed engagements with product teams — help design the SLOs, review the architecture for a launch, run a postmortem facilitation, then move on to the next team.
- *Fits*: companies that want SRE *practices* spread everywhere without hiring an SRE per team; works well when product engineers are willing owners of their own reliability once shown how.
- *Failure mode*: practices decay after the consulting engagement ends if there's no ongoing accountability mechanism (no one re-checks the SLO six months later); the consulting team can become "the fire brigade" that only gets called in after an incident rather than proactively.

**4. Hybrid.** A small central team (tooling, standards, incident command bench) plus embedded reliability champions in each product team who aren't full-time SRE but carry the SLO/on-call/postmortem responsibilities with central support.
- *Fits*: most mid-size companies eventually land here — it captures shared-tooling economies of scale from centralized while keeping product-team context from embedded.
- *Failure mode*: role ambiguity — "champions" without formal SRE title or promotion path get deprioritized under delivery pressure, and the central team has no authority to prevent it.

### Worked example: a 120-engineer fintech startup
Company X has 120 engineers across 8 product teams, no dedicated SRE org, and reliability currently means "whoever wrote the service gets paged." They're considering hiring their first 3 SRE hires. Two mistakes to avoid:
- Hiring 3 SREs and immediately calling them "the SRE team," expecting them to operate all 8 teams' services 24/7 — this recreates Google's centralized ops model at 1/50th the headcount and burns the new hires out within two quarters (3 people cannot sustainably rotate on-call for 8 independently-changing services).
- Embedding all 3 individually into the 3 highest-revenue teams with no shared standards — six months later, each team has a different definition of "P1 incident," a different postmortem template, and duplicated tooling.
The better move: hybrid from day one. The 3 SREs form a small central function that builds one shared incident-tooling and SLO-dashboarding baseline and defines one postmortem template, while spending 60% of their time rotating through the 2-3 highest-risk product teams as embedded reliability leads for a fixed 2-quarter engagement, explicitly transferring on-call ownership back to the product team with documented runbooks before rotating to the next team.

### Revisiting the choice as the company grows
The model that fit at 50 engineers usually doesn't fit at 500. A concrete trigger-based approach: reassess the model whenever (a) headcount roughly triples, (b) a second business-critical product line launches, or (c) the current model has produced two or more burnout-driven SRE departures in a year — each is a signal the current structure's assumptions no longer hold.

## Pros
- Matches reliability investment to the org's actual size and risk profile instead of importing a structure built for a different scale.
- Makes the trade-offs (influence vs. coverage, standardization vs. context) explicit and choosable rather than accidental.
- Gives a diagnostic vocabulary for *why* an existing SRE effort is struggling (usually: wrong model for current size, not "SRE doesn't work here").

## Cons
- Model selection is genuinely hard to get right on the first try, and organizational restructuring is costly and disruptive to do often.
- Hybrid models — the most commonly recommended default — carry real role-ambiguity risk if central leadership doesn't actively protect embedded champions' time.
- Requires a leader with enough organizational authority to actually implement the chosen model against competing delivery pressure; the model on paper and the model in practice diverge without that sponsorship.

## Alternatives
- **No dedicated reliability function at all, reliability as everyone's implicit job** — viable only at very small scale (under ~20 engineers, single product) where informal communication substitutes for structure; stops working as soon as headcount or service count grows past what one shared mental model can hold.
- **Full Google-style centralized SRE org with its own hiring bar and gatekeeping** — appropriate only once you have Google-like scale (many independent services, enough headcount to staff dedicated teams per major area); importing it earlier is the most common failure mode this lesson warns against.
- **Outsourced/managed reliability (e.g., a vendor-run NOC or an MSP)** — can substitute for in-house SRE for narrowly-defined operational coverage (after-hours alert triage) but doesn't substitute for the architectural and cultural work (SLOs, blameless postmortems, error budgets) this subject covers; best treated as a supplement, not a replacement.

## When to use it
Use this model-selection framing any time you're standing up SRE for the first time, or diagnosing why an existing SRE effort feels ineffective. Explicitly name which of the four models you're choosing (or hybridizing) and why, tied to current headcount, service count, and org trust — don't let the model be an accident of who got hired first.

## When NOT to use it
Don't spend cycles on formal model selection at genuinely tiny scale (a five-person startup pre-product-market-fit) — reliability there is better served by lightweight practices (see `seeking-sre/08` on toil at small-team scale) than by organizational design. And don't treat the chosen model as permanent — the biggest anti-pattern in this space is a company still running an embedded model at 800 engineers because no one revisited the choice.

## Key takeaways / mental model
Ask three questions before choosing a model: how many independently-changing critical services do we have, how much headcount can we dedicate to reliability specifically, and how much organizational trust does that team need to actually change how product teams work? Embedded trades coverage for context; centralized trades context for standardization; consulting trades ownership for reach; hybrid tries to blend all three and requires the most active management to avoid role ambiguity.

## Self-check questions
1. A 60-engineer company hires its first SRE and puts them on a rotating 24/7 pager for all 12 of the company's services. Which adoption-model mistake is this, and what would you recommend instead?
2. Your centralized platform SRE team is described by product engineers as "the team that blocks our deploys." Which model failure mode does this describe, and what's one structural change that would address it without abandoning centralization entirely?
3. What are the two most likely triggers that should prompt a company to revisit its SRE adoption model, and why does each one break the assumptions of the current model?
4. Why does the lesson argue that a consulting/enablement model risks practices "decaying" after an engagement ends, and what would you build into the engagement to prevent that?

## References
- Seeking SRE (David Blank-Edelman, ed.), essay on adopting SRE without Google's scale.
- See also `seeking-sre/02` for how ownership boundaries get negotiated once a model is chosen, and `seeking-sre/07` for hiring implications of each model.
