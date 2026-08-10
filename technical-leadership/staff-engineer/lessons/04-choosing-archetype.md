---
id: staff-engineer/04
subject: staff-engineer
title: Choosing an archetype that matches business and organizational needs
slug: choosing-archetype
status: drafted
mastery:
seniority: staff
source: Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 2 and "Getting Started"
prerequisites: [staff-engineer/02, staff-engineer/03]
created: 2026-08-10
updated: 2026-08-10
---

# Choosing an archetype that matches business and organizational needs

## TL;DR
An archetype (`staff-engineer/02`) that fits your strengths but doesn't match what the organization currently needs will stall your impact and your promotion case; the reverse — an archetype the org needs but you're a poor fit for — will burn you out. Choosing well means matching personal strengths against a candid read of organizational need, and being willing to revisit the choice as both change.

## The idea
It's tempting to treat archetype choice as purely a matter of self-knowledge: "I like deep architecture work, so I'll be an Architect." That's necessary but not sufficient. Organizational need is the other half of the equation, and it's the half people skip because it's less pleasant to assess — it requires an honest look at what the company actually has too little of right now, which may not be the glamorous option.

A company in the middle of a security crisis needs Solvers, not Architects drafting a five-year API standard. A company with one enormous, badly-coupled monolith and six teams stepping on each other constantly needs an Architect more than another embedded Tech Lead. A CTO drowning in technical decisions they can't personally evaluate needs a Right Hand. Picking an archetype that's personally comfortable but organizationally unneeded produces work that's technically excellent and organizationally invisible — exactly the trap `staff-engineer/01` warns about, where effort doesn't translate into evaluated impact because it isn't solving the problem anyone with promotion authority actually cares about.

## How it works

### Step 1 — Inventory your own strengths and preferences honestly
Ask candidly: do you do your best work embedded with one team over a long horizon (Tech Lead), or thinking about a domain in the abstract across many teams (Architect)? Do you thrive on ambiguity and short, intense engagements (Solver), or do you prefer sustained ownership over instant triage? Do you want the visibility and pace of working directly with an executive (Right Hand), or do you prefer more autonomy over your own agenda? These preferences are real constraints — forcing yourself into an archetype that fights your natural working style for years is a recipe for burnout, however organizationally justified it looks on paper.

### Step 2 — Read organizational need without flattering yourself
This is the step people skip. Concrete signals to look for:
- **Repeated cross-team incidents or duplicated effort** → signals an Architect gap.
- **A team or project chronically behind, understaffed on technical direction** → signals a Tech Lead gap.
- **A pattern of fires that keep needing an outsider to unstick** → signals a Solver gap.
- **An executive making high-stakes technical calls with no technical thought partner** → signals a Right Hand gap.

The honest version of this exercise sometimes concludes "the organization most needs an Architect, and I am much better suited to being a Tech Lead" — that's a real and useful conclusion, not a failure of the exercise.

### Step 3 — Reconcile the gap
When personal fit and organizational need don't line up, there are three honest options, not one forced answer:
1. **Stretch toward the need**, accepting temporary discomfort because the organizational gap is severe enough to be worth it (e.g., taking on Solver work during a genuine crisis even though you prefer sustained ownership).
2. **Find or create a role that matches your fit elsewhere** — a different team, a different company, or advocating for someone else on the team who's better suited to the needed archetype while you continue in yours.
3. **Negotiate a hybrid** — most real staff-plus roles are a primary archetype with real traces of a second; you might commit 70% to Tech Lead work you're strong at and 30% to the Architect-shaped gap you've identified, rather than fully switching.

**Worked example.** A staff engineer strongly prefers Architect-style work — long-horizon standards, cross-team design review — and is good at it. But their company just had two consecutive security incidents traced to inconsistent auth handling across teams, and the CTO is explicitly asking "who can own fixing this now, this quarter." The Architect instinct says "write the long-term standard." The organizational need says "stop the bleeding first." The right move, per Larson's framing, is to recognize this is a Solver-shaped moment (urgent, cross-team, needs someone parachuted in) and take it on for one quarter — while explicitly scoping it as temporary and different from their usual mode, so it doesn't quietly become their permanent identity. Once resolved, they hand the long-term auth standard work (an Architect-shaped follow-up) either back to themselves in their preferred mode, or to someone else, and return to their primary archetype.

### Archetype choice is not permanent
Organizational needs shift — a reorg, an incident, a new executive, a market shift can all change which archetype is scarce. Revisiting the choice every six to twelve months (not constantly, which would prevent building any track record in one mode) keeps the fit honest over time, rather than assuming the archetype chosen at promotion time is fixed forever.

## Pros
- Prevents the common failure mode of doing excellent work in an archetype nobody needed, which is invisible to promotion committees and leadership regardless of its technical quality.
- Gives engineers and their managers a structured conversation ("what does the org need, what do you want") instead of an implicit, unexamined default.
- Makes archetype mismatch (a known source of staff-plus burnout and stalled careers) diagnosable and nameable instead of a vague feeling of "something's off."

## Cons
- Organizational need is genuinely hard to read accurately, especially from inside one team — it requires visibility (attending planning and incidents across teams, talking to multiple managers) that not every engineer has easy access to.
- Constantly chasing organizational need over personal fit is exhausting and unsustainable — a purely need-driven career, with no weight given to what energizes the person, burns people out (`staff-engineer/12`).
- The "signals" for each archetype gap are heuristics, not a formula; two people can look at the same organizational data and reasonably disagree about which archetype is actually most needed.

## Alternatives
- **Let the organization assign the archetype** — a manager or director explicitly decides what kind of staff engineer they need and hires or develops toward that; removes the ambiguity of self-assessment but risks a mismatch if the assigning manager doesn't know the engineer's actual working style well.
- **Optimize purely for personal fit, ignore organizational need** — some engineers deliberately choose the archetype that suits them and seek out (or wait for) an organization that happens to need exactly that; slower and more selective, but avoids the burnout risk of stretching into an ill-fitting archetype.
- **Rotate through archetypes deliberately** — some staff-plus engineers intentionally spend a year or two in each archetype (Tech Lead, then Solver, then Architect) to build broad range before settling; this trades short-term depth in any one mode for long-term versatility.

## When to use it
Use this exercise whenever you're choosing your next role, negotiating scope with a new manager, evaluating a job offer, or noticing that your current archetype feels stuck despite strong personal effort — it's a diagnostic for exactly that stuck feeling.

## When NOT to use it
Don't over-rotate on organizational need moment to moment — chasing whichever archetype is trendiest that quarter prevents building the sustained track record in any one mode that promotion cases and deep expertise both require. Reassess on a roughly six-to-twelve-month cadence, not weekly.

## Key takeaways / mental model
Draw two columns: "what I'm naturally good at and energized by" and "what the organization is currently starved for." The best staff-plus moves live where those columns overlap. When they don't overlap, name the gap explicitly and choose deliberately — stretch, relocate, or hybridize — rather than drifting into whichever archetype felt most comfortable by default.

## Self-check questions
1. Using the four signals in this lesson (repeated cross-team incidents, a chronically under-directed team, recurring fires, an under-supported executive), which archetype does your own organization currently need most? Does that match the archetype you're actually operating in?
2. Describe a time (yours or someone else's) where personal archetype preference and organizational need clearly diverged. Which of the three reconciliation options (stretch, relocate, hybrid) was chosen, and was it the right call in hindsight?
3. Why is it important to explicitly scope a "stretch" into a needed-but-uncomfortable archetype as temporary, rather than letting it quietly become permanent?
4. Why does Larson caution against reassessing archetype fit too frequently, even though organizational need does genuinely shift over time?

## References
- Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 2: "The staff archetypes," and the "Getting Started as a Staff Engineer" material.
