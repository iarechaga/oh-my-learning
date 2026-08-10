---
id: staff-engineer/08
subject: staff-engineer
title: "Operating rhythms: planning, reviews, and executive communication"
slug: operating-rhythms
status: drafted
mastery:
seniority: senior
source: Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 6 ("Staying aligned with the organization")
prerequisites: [staff-engineer/01, staff-engineer/06]
created: 2026-08-10
updated: 2026-08-10
---

# Operating rhythms: planning, reviews, and executive communication

## TL;DR
Staff-plus engineers stay aligned with an organization they can't personally observe end to end by plugging into its recurring rhythms — planning cycles, design/architecture reviews, and executive updates — rather than relying on ad hoc, one-off conversations; these rhythms are the mechanism by which cross-team judgment stays current and visible over time, not a bureaucratic tax on "real work."

## The idea
A senior engineer can stay aligned with reality by simply paying attention to their own team: the sprint board, the team's Slack channel, their manager's 1:1s. That doesn't scale to staff-plus scope — an organization spanning many teams changes faster than any individual can track through informal osmosis alone. Without a deliberate mechanism for staying current, a staff-plus engineer's mental model of "what's actually happening across the org" quietly goes stale, and decisions get made on outdated information.

Recurring rhythms solve this by converting "staying aligned" from a one-time effort into an amortized, low-friction habit: a standing planning cycle you contribute to every quarter, a design-review forum you attend every week, a monthly or quarterly update you write for leadership. Each individual instance is cheap; the compounding value is a mental model of the organization that stays current automatically, plus a standing channel through which your own judgment reaches leadership and vice versa.

## How it works

### Planning cycles
Most companies run some recurring planning cadence (quarterly OKRs, roadmap reviews, budget cycles). For a staff-plus engineer, showing up to these isn't optional attendance — it's the primary forum where cross-team priorities get set, trade-offs get made explicit, and a staff engineer's cross-team perspective (informed by the scope-expansion work of `staff-engineer/03`) can actually shape what multiple teams commit to, before commitments are locked in rather than after. Waiting until after a planning cycle locks in priorities to raise a cross-team concern means fighting an uphill battle against sunk-cost momentum; raising it *during* planning means it's one of several options genuinely still on the table.

**Worked example.** During quarterly planning, three team roadmaps each independently include "improve service reliability" as a top-line goal, without visibility into each other's plans. A staff engineer who reviews all three draft roadmaps (because they attend the cross-team planning review) notices this and proposes consolidating into one shared reliability initiative with a single owner instead of three redundant, uncoordinated efforts — a trade-off only visible from the vantage point the planning rhythm provides.

### Design and architecture reviews
A standing forum where teams present significant technical decisions before committing to them lets a staff-plus engineer apply cross-team judgment (spotting an inconsistency with another team's approach, a missed edge case from a domain the presenting team doesn't have visibility into, a duplicated effort) at the point where it's cheapest to change — before implementation, not after. Attending regularly (not just when personally invited) is what builds the pattern-recognition described in `staff-engineer/03` — seeing many designs across many teams is how a staff engineer notices the recurring problems no single team would notice on its own.

Effective participation in review is calibrated: raising every stylistic preference erodes the influence needed for the comments that actually matter (see `staff-engineer/07` on spending influence carefully), while staying silent on real cross-cutting risks wastes the whole point of attending. A good habit is to ask "would this decision look different if the presenting team could see what I can see across the org?" before commenting — if yes, the comment is worth spending influence on; if it's a personal stylistic preference, it usually isn't.

### Executive communication
Executives make resourcing and prioritization decisions based substantially on what reaches them — and what reaches them by default is filtered through whoever is closest to them, which is not automatically the most accurate technical picture. A regular update (written, not just ad hoc) from a staff-plus engineer with genuine cross-team technical visibility gives executives a channel of technical ground truth they wouldn't otherwise reliably get, and gives the staff engineer's own judgment a route to influence decisions made above the level of any single team's manager.

**What makes executive communication effective, concretely:**
- **Brevity and structure over completeness.** An executive update is read in minutes, not studied — lead with the one or two things that actually need their attention, not a comprehensive log of everything that happened.
- **Named trade-offs, not just status.** "Project X is 80% done" is a status update; "Project X is 80% done, and the remaining 20% requires a decision from you about whether to delay launch by two weeks or ship with a known gap in Y" is the kind of update that actually uses an executive's time and authority for what only they can do.
- **Consistency.** A once-off update after a crisis reads as alarm; a genuinely useful update is regular enough that executives learn to expect and rely on it as a real information channel, and irregular enough alarm bells still stand out precisely because the baseline is calm and routine.

### The cost of skipping rhythms
Engineers who skip these recurring forums — treating them as overhead that gets in the way of "real" technical work — end up making cross-team recommendations based on stale information, get surprised by decisions that were made in a planning cycle they didn't attend, and lose the standing channel to leadership that a consistent update builds. This is a common failure mode specifically for engineers with a strong individual-contributor instinct to prioritize heads-down work over what looks like "meetings" — but for staff-plus scope, the rhythms are not a distraction from the job; they largely are the job's information infrastructure.

## Pros
- Keeps a staff-plus engineer's mental model of the organization current without requiring constant ad hoc effort — the cost is amortized into a predictable, recurring habit.
- Creates standing channels (to peers via review, to leadership via updates) that make influence (`staff-engineer/07`) easier to exercise because the relationship and the visibility already exist before they're urgently needed.
- Surfaces cross-team problems (duplicated effort, conflicting plans) while they're still cheap to fix, at the planning or design stage rather than after implementation.

## Cons
- Real time cost — a full slate of planning cycles, review forums, and regular executive updates can consume a meaningful fraction of a week, competing directly with heads-down technical work.
- Low-value if attended passively — showing up without applying the cross-team lens (just listening, never commenting, never actually reading other teams' pre-reads) captures little of the benefit for a real time cost.
- Executive communication done poorly (too frequent, too vague, or alarmist) can burn the very channel it's meant to build, making leadership tune out future updates.

## Alternatives
- **Relying entirely on your manager to relay information both directions** — lower time cost, but creates a bottleneck and a game-of-telephone distortion; works for team-scoped roles but doesn't scale to genuinely cross-team staff-plus judgment.
- **Ad hoc, as-needed check-ins instead of a regular rhythm** — lower overhead when things are calm, but means the relationship and shared context have to be rebuilt from scratch every time something urgent comes up, which is slower exactly when speed matters most.
- **A dedicated chief-of-staff or program-manager role handling cross-team coordination** — some larger orgs employ a non-engineering role specifically for cross-team planning coordination, which can reduce the coordination burden on staff engineers, but doesn't substitute for the technical judgment a staff engineer's own participation in review brings.

## When to use it
Build these rhythms once you're operating with cross-team scope (`staff-engineer/03`) and need your judgment to reach leadership and peer teams reliably — pick a small number of high-value recurring forums (not every possible meeting) and attend them consistently enough to build real pattern-recognition and a real channel.

## When NOT to use it
Don't over-subscribe to every recurring forum available "just in case" — attending planning, review, and reporting rhythms for domains you have no real judgment to contribute to is wasted time for you and diluted attention for everyone else in the room. Pick the rhythms that intersect with your actual scope.

## Key takeaways / mental model
Treat organizational alignment like a system that needs a regular heartbeat, not a one-time sync: pick the few recurring forums (planning, review, executive update) that intersect your actual scope, attend them consistently, and use each one to both pull current information in and push your cross-team judgment out — skipping the heartbeat doesn't save time, it just moves the cost to later, in the form of stale decisions and missed alignment.

## Self-check questions
1. List the recurring rhythms (planning cycles, review forums, reporting cadences) that exist at your own organization. Which ones intersect your actual scope, and which are you either missing (and should join) or over-attending (and could skip)?
2. In the worked planning-cycle example, why does noticing the duplicated "reliability" goal during planning matter more than noticing it after all three teams have already started work?
3. Rewrite a vague status update ("Project X is going fine") into an executive-ready update that names a real trade-off requiring the executive's decision, per this lesson's criteria.
4. Why does the lesson argue that skipping recurring forums doesn't save time overall, just defers the cost? What does the deferred cost actually look like in practice?

## References
- Staff Engineer: Leadership Beyond the Management Track (Will Larson), Chapter 6: "Staying aligned with the organization" and related material on staff-plus operating cadence.
