---
id: staff-engineer/02
subject: staff-engineer
title: "Staff archetypes: tech lead, architect, solver, and right hand"
slug: staff-archetypes
status: drafted
mastery:
seniority: staff
source: Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 2
prerequisites: [staff-engineer/01]
created: 2026-08-10
updated: 2026-08-10
---

# Staff archetypes: tech lead, architect, solver, and right hand

## TL;DR
Larson identifies four recurring patterns ("archetypes") that staff-plus jobs tend to fall into — Tech Lead, Architect, Solver, and Right Hand — distinguished by where they sit organizationally and what kind of problem they spend most of their time on. No archetype is more senior than another; they're different shapes of the same seniority, and most staff-plus engineers are a primary archetype with traces of a second.

## The idea
"Staff engineer" sounds like one job, but observing real staff-plus engineers across companies reveals wildly different day-to-day realities: one spends all day embedded in a single team's planning and code review, another spends all day in design reviews for teams they've never worked on, another gets dropped into whichever part of the company is on fire that month, and another works almost exclusively as a technical extension of a VP or CTO. These aren't different levels of seniority — they're different *shapes* the same underlying seniority takes depending on what the organization needs and what the individual is good at.

Naming these archetypes matters for two practical reasons. First, it helps you recognize what kind of staff-plus role you're actually in (or being offered), so you can evaluate fit honestly instead of assuming "staff engineer" means the same job everywhere. Second, it gives you language for a mismatch: a lot of staff-plus dissatisfaction and stalled promotions come from someone trying to operate in an archetype the organization doesn't need or doesn't recognize, covered in `staff-engineer/04`.

## How it works

### Tech Lead
Embedded in a single team (or a small cluster of closely related teams), the Tech Lead archetype pairs technical direction with the team's engineering manager, who handles people management while the Tech Lead handles technical scope: architecture decisions, breaking down ambiguous work into a plan, unblocking teammates, and representing the team's technical state to other stakeholders. This is the most common entry point into staff-plus, because it's the most direct extension of strong senior-engineer work — the scope just widens from "my own tasks" to "my team's technical direction."

**Worked example.** A Tech Lead on a checkout team spends a sprint not writing feature code but: sketching three architecture options for supporting a new payment provider, running a design review with the team to pick one, breaking the chosen option into eight tickets sized for different engineers' skill levels, and pairing with the newest hire on the trickiest ticket. The team ships faster and with fewer surprises than if everyone had started coding independently — that's the leverage.

### Architect
Responsible for the direction, quality, and coherence of a *technical domain* (not a team) — think "data platform architect" or "the person accountable for API design consistency across twenty services." Architects spend more time on documents, review, and long-horizon planning than on any single team's day-to-day execution; their success shows up as consistency and quality across work they didn't personally do. This archetype requires the most credibility, since an architect's authority rests entirely on other teams voluntarily following their guidance — they rarely have any formal power to compel it.

**Worked example.** An Architect notices that six different services have each built their own ad hoc retry logic, pagination scheme, and error-response shape, making the API surface inconsistent for every external consumer. They write a company-wide API design standard, socialize it through review with each team's tech lead, and spend the next two quarters consulting on individual designs to make sure new work actually follows it — without writing a single line of any team's production code.

### Solver
Deployed against whatever the hardest, most urgent, most ambiguous problem currently is — often without a fixed team at all. Solvers move between fires: a security incident, a stalled migration, a project that's quietly failed and needs an outsider's clear-eyed assessment. This archetype requires unusually broad technical range (because the next problem is unpredictable) and comfort with short-term, high-intensity engagements rather than long-term ownership.

**Worked example.** A critical data pipeline has been "six weeks from done" for five months. A Solver is assigned to it for three weeks, discovers the real blocker is an unstated disagreement between two teams about data ownership (not a technical problem at all), gets the disagreement resolved in a single meeting with the right people in the room, and hands the now-unblocked, now-technically-straightforward project back to its original team. The Solver's contribution was diagnosis and organizational unblocking, not code.

### Right Hand
Operates as a technical extension of a senior executive (VP of Engineering, CTO), taking on whatever the executive needs eyes and judgment on: evaluating a risky proposal before it reaches the executive, representing the executive's priorities in rooms the executive can't be in, doing deep technical due diligence on an acquisition. This archetype requires the deepest organizational trust of the four, because it depends on the executive being willing to delegate judgment calls that they would otherwise have to make themselves. It's also the archetype most tied to a specific relationship — a Right Hand's effectiveness often depends heavily on the trust built with one particular executive, which makes it more fragile if that executive leaves.

**Worked example.** A CTO is deciding whether to acquire a startup, largely for its technology. A Right Hand spends a week doing technical due diligence — reading the codebase, interviewing the startup's engineers, assessing how much rework the integration will need — and delivers a blunt private assessment the CTO uses to negotiate price and plan the post-acquisition integration.

### Comparing the four
| Archetype | Primary scope | Main activity | Authority source |
| --- | --- | --- | --- |
| Tech Lead | One team / small cluster | Planning, unblocking, architecture for the team | Team trust, paired with an EM |
| Architect | A technical domain across teams | Standards, design review, documents | Domain credibility |
| Solver | Whatever is most broken right now | Diagnosis, short-term intense engagement | Track record of fixing hard things |
| Right Hand | An executive's priorities | Due diligence, representing the exec | Direct executive trust |

## Pros
- Gives staff-plus engineers and their managers shared vocabulary to describe a role honestly instead of a vague "does staff-y things."
- Makes career conversations concrete: an engineer can say "I want to move from Tech Lead toward Architect" and both sides know roughly what that shift entails.
- Helps companies notice gaps — e.g., realizing they have five Tech Leads and zero Architects, and their cross-team consistency problems are a direct consequence.

## Cons
- Real people rarely fit one archetype perfectly; forcing a rigid label onto someone who's genuinely a blend can feel reductive or inaccurate.
- The archetypes describe common patterns at the companies Larson interviewed (mostly larger tech companies); very small companies may not have distinct enough scope for the archetypes to cleanly apply.
- Archetype fit can change involuntarily — a reorg can turn a Tech Lead's team into three teams overnight, effectively forcing an Architect-shaped job on someone who never chose it.

## Alternatives
- **A single undifferentiated "staff engineer" job description** — the common alternative (and the default before this book), where the archetype is left implicit and each staff engineer negotiates their own scope from scratch; this is exactly the ambiguity Larson is naming and solving for.
- **Formal sub-titles per archetype** (e.g., "Staff Architect" as a distinct title from "Staff Engineer") — some companies encode the archetype directly into the title; this adds clarity but also rigidity, and can create unnecessary title-change friction when someone's actual work shifts archetype.
- **Domain-specific ladders** (e.g., separate "Technical Fellow" tracks in research-heavy orgs) — companies with a strong individual-research culture sometimes define archetypes closer to "expert investigator" than any of Larson's four; useful context, but outside this book's frame.

## When to use it
Use the archetypes when evaluating a staff-plus job offer or internal role (ask directly: "which archetype is this?"), when writing your own promotion narrative (frame your impact in the archetype's terms), or when a manager is trying to figure out what kind of staff-plus hire or internal promotion the team actually needs.

## When NOT to use it
Don't use the archetypes as a rigid box that forces you to abandon useful work outside your primary archetype — a Tech Lead who spots a cross-team inconsistency should still write the standard even though that's "Architect work." The archetypes describe the center of gravity of a role, not a fence around it.

## Key takeaways / mental model
Ask two questions about any staff-plus role: "what is the scope — a team, a domain, whatever's broken, or an executive's priorities?" and "what's the primary activity — planning and unblocking, standards and review, diagnosis and short engagements, or due diligence and representation?" The answers place the role on Larson's map, and mismatches between what a role needs and what an engineer wants to do are the single most common source of staff-plus dissatisfaction.

## Self-check questions
1. Which archetype best describes a staff-plus role you've seen (your own, a colleague's, or one from a job posting)? Which parts of the description fit cleanly, and which parts don't fit any single archetype?
2. Why does the Solver archetype require unusually broad technical range compared to the other three? What's the risk of putting someone with narrow, deep expertise into a Solver role?
3. Explain why the Right Hand archetype is described as the most fragile of the four — fragile with respect to what?
4. A company has three staff engineers, all effectively operating as Tech Leads on different teams, and complains that "nobody is thinking about cross-team consistency." Using this lesson's framework, what's actually missing from their staff-plus bench?

## References
- Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 2: "The staff archetypes."
