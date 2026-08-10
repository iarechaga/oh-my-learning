---
id: managers-path/02
subject: managers-path
title: Tech lead responsibilities and hybrid leadership
slug: tech-lead-responsibilities
status: drafted
mastery:
seniority: senior
source: The Manager's Path (Camille Fournier), Chapter 3 - Tech Lead
prerequisites: [managers-path/01]
created: 2026-08-10
updated: 2026-08-10
---

# Tech lead responsibilities and hybrid leadership

## TL;DR
The tech lead role is a hybrid: still a hands-on individual contributor, but now also responsible for a team's technical direction, project coordination, and the "glue work" of turning a set of tasks into a coherent plan. It is the first role where "getting the team to succeed" starts to matter as much as "writing good code yourself."

## The idea
A tech lead is not yet a manager - they usually have no formal authority over anyone's performance review, compensation, or hiring - but they are expected to make or broker the technical decisions that shape what the rest of the team builds, and to make sure the team's work adds up to something coherent rather than a pile of individually-good pull requests that don't fit together. This is a genuinely awkward, dual-identity role: half the job still looks like senior IC work (writing code, reviewing designs, debugging hard problems), and half the job is now about other people's work - unblocking them, translating requirements, negotiating scope with product, making sure nobody is duplicating effort or building something that contradicts a decision made in a meeting they weren't in.

Fournier is explicit that this role commonly goes wrong in one of two directions: tech leads who spend 100% of their time coding and treat the "lead" part as an afterthought, leaving the team directionless and drowning in undecided architecture questions, or tech leads who stop coding entirely and become a bottleneck-manager without the authority or training to actually manage - annoying everyone by making all the decisions without any of the people-management skill to do it well. The job is to hold both halves at once.

## How it works

### The tech lead is the technical glue, not just the strongest engineer
Being the best individual coder on the team does not automatically make someone a good tech lead - the job requires seeing across the whole project rather than the deepest single piece of it. Concretely: when a team is building a new payments feature, the strongest IC might go deep into the trickiest edge case in currency rounding, while the tech lead's job is to make sure the *overall* design - how the payments service talks to the ledger service, what the rollout plan is, who owns the on-call after launch - is coherent, even if that means the tech lead personally writes less of the trickiest code.

### Delegate the interesting work, not just the boring work
A common trap: a new tech lead keeps the most technically interesting parts of the project for themselves ("I'll do the tricky caching layer") and hands off the boring plumbing to the rest of the team, because letting go of interesting work feels like a loss. Fournier's guidance is the opposite: deliberately delegate some of the *interesting* work too, both because the team needs the growth opportunity (this is where `managers-path/01` mentoring turns into direct project ownership for others) and because the tech lead who hoards interesting work becomes a single point of failure and a bottleneck on everything routed through their attention.

### Own the "70% design" and broker disagreement
The tech lead is usually responsible for driving a design to roughly 70% certainty - enough that the team can start building without every last decision nailed down - and then for resolving disagreements when two strong engineers want to go different directions. A worked example: two engineers disagree over whether a new service should be synchronous REST or an async queue. The tech lead's job isn't to have the "right" answer waiting - it's to run a short, time-boxed decision process (list the actual constraints: latency budget, failure-mode tolerance, team's existing operational experience), make the call, write it down, and move the team forward, rather than letting the debate run indefinitely or silently picking a side without explaining why.

### Communicate outward as well as inward
A tech lead represents the team's technical status to stakeholders outside the team - a PM asking "will this ship on time," another team asking "can we depend on your new API," a skip-level manager asking "what's actually blocking you." This outward communication responsibility is new relative to a pure IC role, and it requires translating technical detail into a level of abstraction the audience actually needs (a PM doesn't need the caching strategy; they need to know if the date is at risk and why).

## Pros
- Gives an engineer real leadership practice - technical decision-making, coordination, stakeholder communication - while still writing code and staying technically sharp.
- Improves team output by reducing duplicated or contradictory work, since someone is explicitly responsible for coherence.
- A strong low-stakes proving ground for whether someone wants to pursue formal management (`managers-path/03`) or would rather stay a deep technical IC track (architect, staff engineer).

## Cons
- Ambiguous authority: a tech lead can be expected to "own" outcomes without the formal levers (hiring, firing, compensation, performance management) that would make ownership easier to exercise.
- Easy to overload: doing both substantial IC work and full coordination/communication work in the same 40 hours is often not actually possible, and something quietly gives - usually either the code quality or the team's coherence.
- Can create friction with peers who don't formally report to the tech lead but are expected to defer to their technical calls - the tech lead has to lead through influence and clear reasoning, not authority.

## Alternatives
- **Staff/principal engineer (no coordination duties)** - a deep technical IC track that skips the team-coordination and stakeholder-communication responsibilities entirely, for engineers who want maximum technical depth without the hybrid split; the two roles often coexist on the same team.
- **Engineering manager owning the same team** - moves the coordination and people responsibilities into a formal management role with real authority (see `managers-path/03`), trading away most hands-on coding time.
- **Rotating tech lead** - some teams rotate the tech lead role periodically (e.g., every 6-12 months) specifically to spread the leadership experience around and avoid any one person becoming an indispensable bottleneck.

## When to use it
When a team needs technical coherence and coordination but is not large enough, or the person is not experienced enough, to justify a dedicated non-coding management role - typically a single team of 4-8 engineers working on a defined set of related projects.

## When NOT to use it
Don't put someone in a tech lead role as an "informal promotion" with no actual change in expectations or support - if the org doesn't explicitly carve out time for the coordination half of the job, the person will default back to pure IC work under deadline pressure and the "lead" responsibilities will silently not happen. Also avoid the role for someone who has shown no interest in or aptitude for the mentoring skills in `managers-path/01` - technical excellence alone doesn't transfer into this hybrid role.

## Key takeaways / mental model
A tech lead's job is best captured as "keep the whole project bigger than any one person's code in your head" - trade some personal coding depth for team-wide coherence, delegate interesting work on purpose, and use influence and clear decision-making instead of authority you don't have.

## Self-check questions
1. Why does Fournier warn against a tech lead keeping all the interesting technical work for themselves, even though it's tempting and often produces the best individual code?
2. Two engineers on your team disagree on a technical approach and it's stalling the sprint. As tech lead, what's your process for resolving it (not just "who's right")?
3. What is the concrete difference in formal authority between a tech lead and an engineering manager, and how does that change how each should resolve a disagreement?
4. Give an example of "outward communication" a tech lead needs to do that a pure IC role would not require.

## References
- The Manager's Path (Camille Fournier), Chapter 3: "Tech Lead".
