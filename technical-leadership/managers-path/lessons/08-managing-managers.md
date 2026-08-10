---
id: managers-path/08
subject: managers-path
title: Managing managers and creating leadership layers
slug: managing-managers
status: drafted
mastery:
seniority: principal
source: The Manager's Path (Camille Fournier), Chapter 7 - Managing Multiple Teams
prerequisites: [managers-path/03, managers-path/05, managers-path/06]
created: 2026-08-10
updated: 2026-08-10
---

# Managing managers and creating leadership layers

## TL;DR
Managing managers requires a second identity shift as sharp as the IC-to-manager one: your job becomes coaching other managers' judgment rather than managing individual engineers directly, and your success now depends on decisions being made well two levels away from you, by people whose day-to-day work you mostly don't see.

## The idea
Just as the IC-to-manager transition requires giving up personally solving every technical problem, the manager-to-manager-of-managers transition requires giving up personally solving every people problem. A manager-of-managers who still wants to run every 1:1, resolve every piece of team conflict, and make every hiring call personally is not actually operating at the new level - they're either duplicating their reports' jobs (undermining the reports' authority and growth) or becoming an unscalable bottleneck as the org grows underneath them.

Fournier frames this level as managing through other managers' judgment rather than managing individuals directly: the manager-of-managers' primary tool is now coaching - helping their reports (who are themselves managers) get better at 1:1s, feedback, hiring, and team health, rather than doing those things directly for the reports' teams. This requires trusting a layer of indirection that most new manager-of-managers find uncomfortable at first, because it means real problems on a team below can exist for a while before the manager-of-managers even hears about them - and the fix isn't to bypass the layer, it's to coach the manager in that seat to see and handle it well.

## How it works

### Coach managers, don't manage their reports for them
When a manager-of-managers learns that an engineer two levels down is struggling, the instinct might be to step in directly. Fournier's guidance is almost always to work through the manager in between instead: ask that manager what they've noticed, coach them on how to run the feedback conversation (`managers-path/05`), and follow up on whether it happened - rather than having the conversation yourself. Concrete example: a manager-of-managers hears secondhand that an engineer is unhappy. Rather than pulling that engineer aside personally, they ask the engineer's direct manager, "What have you heard from them in 1:1s? What's your read?" - and if the direct manager hasn't picked up on it, that becomes a coaching moment about deepening trust in their own 1:1s, not a cue to take over.

### Evaluate managers on their team's outcomes and their own management craft, not just team happiness
A manager-of-managers needs signal on how well each manager underneath them is actually doing the job - are their 1:1s substantive, is feedback happening in a timely way, is hiring bar being held, is the team healthy by the diagnostics in `managers-path/06`. This requires deliberately gathering signal the manager-of-managers doesn't automatically see: skip-level 1:1s with individual engineers, watching how a manager runs a hiring debrief, reviewing how a manager handled a real conflict after the fact. Fournier warns against relying solely on "does the team seem happy" as a proxy - a team can seem fine on the surface while a manager quietly avoids all hard conversations, and the gaps only surface later as attrition or a blown deadline.

### Build and protect leadership layers deliberately
As an org grows, someone has to decide where new management layers get created, and getting this wrong causes real damage: too few managers and each one is spread too thin to do the individual-level work well (1:1s become rushed or infrequent); too many layers and decisions slow down, information degrades as it passes through each hop, and the org accumulates coordination overhead disproportionate to its size. A useful heuristic from the book: a manager with more than roughly 7-10 direct reports usually can't sustain quality 1:1s and individual attention, which is the practical trigger for splitting a team and creating a new management layer - not org-chart aesthetics.

### Resist becoming the de facto manager of your grandreports
A specific, easy-to-fall-into trap: a manager-of-managers who is more experienced or technically stronger than the managers underneath them starts fielding questions and making calls that should route through the intermediate manager, because it's faster in the moment. Over time this erodes the intermediate manager's authority and standing with their own team - the team learns to skip them and go straight to the manager-of-managers, which is corrosive to the intermediate manager's ability to lead. The discipline is redirecting ("Have you talked to your manager about this?") even when personally jumping in would be faster.

## Pros
- Multiplies leadership capacity across an org far beyond what any single manager could personally oversee, by developing other managers rather than personally handling everything.
- Creates a real growth path for managers to develop into (managing managers is a distinct, learnable skill, not just "management but bigger"), building organizational depth.
- Surfaces systemic issues (a manager who consistently struggles with feedback, a pattern of attrition across multiple teams) that are invisible from inside any single team.

## Cons
- Real loss of direct visibility - problems on a team two levels down can exist and grow for a while before reaching the manager-of-managers, especially if the intermediate manager is avoiding or hiding them.
- Coaching another manager's judgment is slower and less certain than directly fixing a problem yourself, and requires real restraint under pressure to actually let the intermediate manager own the outcome.
- Evaluating manager quality requires deliberately built signal-gathering (skip-levels, debrief observation) that takes real time and can feel, to the intermediate manager, like being second-guessed if not handled carefully.

## Alternatives
- **Flatter org with wider spans of control** - avoid adding a management layer at all by having one manager oversee a larger group directly; keeps communication paths shorter but caps out once span of control exceeds what one person can give real individual attention to (Fournier's ~7-10 heuristic).
- **Player-coach manager-of-managers** - stays hands-on with some individual technical or people work alongside managing managers; can work briefly during a transition but tends to break down for the same reasons a pure IC-manager hybrid breaks down at scale (see `managers-path/03`).
- **Matrix/dotted-line management** - splits authority between a "who you report to" manager and a project or functional lead; adds coordination flexibility for cross-functional work at the cost of clearer single-threaded accountability.

## When to use it
Once a manager's own reports include other managers - typically triggered organizationally when a single manager's team has grown past the point of sustainable direct 1:1 attention (Fournier's rough 7-10 heuristic) and needs to be split into sub-teams each led by their own manager.

## When NOT to use it
Don't add a management layer purely for title/leveling reasons when the org is still small enough for one manager to give every report real individual attention - premature layering adds communication overhead and dilutes the manager-of-managers' own relationship with the actual engineering work and people. And don't bypass an intermediate manager "just this once because it's faster" as a habit - even occasional bypassing, repeated, quietly trains the org to route around that manager.

## Key takeaways / mental model
At this level, your job is the quality of other managers' judgment, not the day-to-day of their teams - build deliberate visibility (skip-levels, debrief observation) instead of direct control, coach rather than take over, and treat span-of-control limits as the real trigger for adding a layer, not org-chart symmetry.

## Self-check questions
1. You hear secondhand that an engineer two levels below you is unhappy. Walk through what you would (and would not) do first, and why.
2. Why does Fournier warn against evaluating a manager's performance mainly by "does their team seem happy"? What better signals would you gather instead, and how?
3. What is the practical heuristic this lesson gives for when a team should split into two, each with its own manager? Why is that the right trigger instead of a fixed org-chart ratio?
4. Describe a scenario where being more technically capable than the manager underneath you creates a real temptation to bypass them - and what the cost of doing so repeatedly would be.

## References
- The Manager's Path (Camille Fournier), Chapter 7: "Managing Multiple Teams".
