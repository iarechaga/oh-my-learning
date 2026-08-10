---
id: seeking-sre/12
subject: seeking-sre
title: The Future of SRE as a Socio-Technical Discipline
slug: future-of-sre
status: drafted
mastery:
seniority: principal
source: Seeking SRE (David Blank-Edelman, ed.), closing essay on where SRE goes as it spreads beyond hyperscale companies
prerequisites: [seeking-sre/11]
created: 2026-08-10
updated: 2026-08-10
---

# The Future of SRE as a Socio-Technical Discipline

## TL;DR
As SRE practice spreads far beyond the hyperscale companies that originated it, its long-term identity is shifting from "a specific team structure and toolset borrowed from Google" toward "a general discipline of socio-technical systems thinking" — the durable, transferable core isn't the SLO math or the specific org chart, but the habit of treating reliability as inseparable from the humans, incentives, and organizational structures that produce (or undermine) it, and that shift has real implications for how the discipline should keep evolving.

## The idea
This closing lesson steps back from the operational adaptations covered across the rest of this subject (adoption models, ownership, on-call, culture, hiring, toil, planning, regulation, measurement) to ask a higher-order question: what is SRE actually *for*, once you strip away the specifics that only apply at Google's scale? The book's answer, echoed across many of its essays and made explicit in the closing material: SRE's most durable and portable contribution isn't a specific practice (error budgets are useful but not universal) — it's a **way of thinking about reliability as a socio-technical property**, meaning reliability is jointly produced by technical systems and the human/organizational systems around them, and neither can be optimized in isolation without breaking the other.

This reframing matters because it changes what "practicing SRE" means as the discipline keeps spreading into contexts increasingly unlike Google's: a five-person startup, a regulated healthcare system, a nonprofit with almost no ops budget, an organization built primarily around AI/ML systems whose failure modes barely resemble the request-serving systems SRE was originally designed around. If SRE is "Google's specific practices," it stops applying in most of these contexts. If SRE is "socio-technical reliability thinking," it always applies, though its concrete implementation must be reinvented every time.

## How it works

### From "borrowed practices" to "transferable principles"
Track the pattern across this subject's lessons: `seeking-sre/01` showed the org-chart model itself has to be reinvented per company size. `seeking-sre/04` and `seeking-sre/08` showed the *specific mechanisms* for sustainable on-call and toil reduction change dramatically with headcount. `seeking-sre/10` showed the practices need real modification in regulated contexts. What stays constant across every one of these adaptations is not any specific practice, but a small set of underlying **principles**: reliability failures usually have systemic, not individual, root causes; humans under sustained unsustainable load will eventually produce worse outcomes regardless of their skill; visibility (of toil, of error budgets, of near-misses) is a precondition for improvement; and trade-offs between reliability and velocity are real and should be made explicitly, not by default or by accident. The future of SRE, in this framing, is less about codifying more specific practices and more about getting better at teaching and transferring *this underlying judgment* into wildly different contexts.

### The discipline's expansion into new technical domains
As of the mid-2020s, SRE-adjacent thinking is visibly expanding into domains the original Google SRE book never addressed directly: reliability of ML/AI systems (where failure modes include silent model drift and data quality degradation rather than clean binary up/down states), reliability of data pipelines and analytics infrastructure (where "correct but late" and "fast but wrong" are both failure modes SLOs weren't originally designed to capture cleanly), and reliability of increasingly automated, agentic systems where a "human on-call" model itself may need rethinking if the system is expected to detect and remediate its own failures with only human oversight rather than direct human action. The socio-technical framing still applies here — these systems still fail because of a mix of technical and human/organizational factors — but the specific SLIs, escalation models, and even the definition of "incident" have to be substantially reinvented, not copy-pasted from request-serving-system SRE.

### Worked example: applying the principles, not the practices, to a new domain
A company operating a recommendation-ML pipeline wants to "do SRE" for it. Copying request-serving SRE literally (define an SLO on API latency and error rate for the serving endpoint) captures only part of the real reliability picture — the model could be serving fast, error-free responses that are silently wrong because of upstream data drift, which a latency/error-rate SLO would never catch. Applying the underlying *principles* instead: identify the real socio-technical failure modes specific to this system (who would notice data drift, how fast, and what human process exists to respond), build visibility for the actual risk (data-quality monitoring, not just latency), and define an "incident" broadly enough to include "the model is technically up but producing bad recommendations," with an on-call and escalation model tailored to that reality (probably involving a data scientist, not just an infrastructure engineer, in the response). This is SRE thinking genuinely applied to a new domain, not SRE practices copy-pasted onto a domain they weren't built for.

### The organizational-maturity trajectory, one more time, at the meta level
Just as `seeking-sre/03` described incident response maturing through stages, the book suggests the discipline of SRE itself, industry-wide, is maturing through an analogous arc: an early stage of literal imitation (companies trying to copy Google's specific practices regardless of fit), a middle stage of adaptation (this subject's core content — reshaping practices to fit smaller/different organizations, which is roughly where the industry broadly sits as of the mid-2020s), and a maturing stage of genuine principle-level thinking, where practitioners reason from the underlying socio-technical logic to invent whatever the specific practice needs to be for their context, rather than adapting someone else's practice. Recognizing which stage your *own organization's* SRE maturity is in — literal imitation, adaptation, or genuine principle-level reasoning — is itself a useful, higher-order diagnostic, echoing but one level up from the staged model in `seeking-sre/03`.

### What doesn't change: the human cost of getting this wrong
Whatever technical domain SRE expands into next, one thing the book is emphatic stays constant: the human cost of poorly-designed reliability practice (unsustainable on-call, blame-driven culture, reliability work that's structurally impossible to prioritize) doesn't shrink just because the underlying technology changes. A badly-run ML-reliability on-call rotation burns people out exactly as thoroughly as a badly-run traditional one; the specific alerts and escalation paths are new, but the sustainability math (`seeking-sre/04`) and the cultural mechanics (`seeking-sre/05`) are not new problems requiring new solutions — they're the same problems requiring the same underlying discipline, applied to a new technical surface.

## Pros
- A principles-first framing keeps SRE thinking relevant as the discipline spreads into contexts (small companies, new technical domains, regulated industries) the original practices weren't designed for.
- Gives practitioners a diagnostic for their own organizational maturity (imitation, adaptation, principle-level reasoning) that's useful for planning what to invest in next.
- Avoids the trap of treating any specific practice (error budgets, a particular on-call structure) as permanently canonical, keeping the discipline able to evolve rather than calcify.

## Cons
- "Principles, not practices" is harder to teach and onboard new practitioners into than a concrete practice checklist — it requires genuine judgment that takes longer to develop than following a template.
- Without any concrete practices as a starting scaffold, an organization new to reliability work may struggle to get started at all; the adapted practices this subject covers remain a necessary on-ramp even under a principles-first philosophy.
- The claim that SRE is maturing industry-wide toward principle-level thinking is itself somewhat speculative and harder to verify than the more concrete, testable claims in earlier lessons of this subject.

## Alternatives
- **Treat SRE as a fixed, canonical practice set (Google's playbook), resist further evolution** — provides stability and a shared, well-documented vocabulary across the industry, but risks the discipline becoming increasingly irrelevant as it's applied to contexts (small teams, new technical domains) it wasn't designed for, which is the exact failure mode this subject as a whole has been arguing against.
- **Let each domain (ML reliability, data pipeline reliability) develop its own entirely separate discipline with its own vocabulary, disconnected from SRE** — avoids awkward practice-transplantation, but forfeits the genuinely transferable socio-technical lessons (sustainable on-call, blameless culture, visibility-first toil management) that took the SRE discipline years to learn, forcing each new domain to relearn them independently.
- **Wait for a new canonical text/framework to emerge for each new domain before acting** — lower risk of getting the adaptation wrong, but cedes the ground to whoever moves first and defines the vocabulary and defaults for that domain, which then becomes the new thing later practitioners have to adapt or unlearn.

## When to use it
Reach for principle-level reasoning (not practice-copying) whenever you're applying reliability thinking to a genuinely new context this subject hasn't already covered — a new technical domain, an organizational shape none of these lessons anticipated, or a scale extreme enough that even the "adapted for smaller orgs" versions here don't quite fit.

## When NOT to use it
Don't reach for principle-level first-principles reasoning when a concrete, well-adapted practice from this subject already fits your situation — reinventing sustainable on-call design from scratch when `seeking-sre/04` already gives you a workable adaptation is wasted effort; use the concrete lessons where they apply, and reserve principle-level reasoning for the genuine gaps.

## Key takeaways / mental model
The org chart, the specific SLO math, and the on-call tooling are all borrowed, adaptable surface details. What's genuinely durable about SRE, as it keeps spreading into contexts its originators never anticipated, is the underlying socio-technical habit: reliability is jointly produced by systems and the humans/organizations around them, root causes are usually systemic not individual, visibility precedes improvement, and reliability/velocity trade-offs should be explicit. When you hit a context none of this subject's specific adaptations quite fit, reason from those principles rather than forcing a copy-paste of a practice built for a different context.

## Self-check questions
1. A company copies Google's SRE practices literally for its ML recommendation pipeline (an SLO on API latency and error rate only) and later discovers this missed a real reliability failure (silent data drift). Diagnose what went wrong using this lesson's framing, and redesign the approach.
2. What does it mean, concretely, for an organization to be at the "adaptation" stage of SRE maturity versus the "principle-level reasoning" stage? Give an example of a decision that would look different at each stage.
3. The lesson claims the human cost of bad reliability practice "doesn't shrink just because the underlying technology changes." Defend or challenge this claim using a scenario involving a genuinely new technical domain.
4. Why does the lesson argue that "principles, not practices" is harder to onboard new practitioners into, and what would you do to make a principles-first approach more teachable to a junior engineer new to reliability work?

## References
- Seeking SRE (David Blank-Edelman, ed.), closing essay on where SRE goes as it spreads beyond hyperscale companies.
- See also `seeking-sre/01` through `seeking-sre/11` for the concrete adaptations this closing lesson generalizes from, and `seeking-sre/11` specifically for the measurement discipline that verifies whether a principle-level adaptation is actually working.
