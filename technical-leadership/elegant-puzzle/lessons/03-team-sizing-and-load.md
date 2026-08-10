---
id: elegant-puzzle/03
subject: elegant-puzzle
title: Team sizing, composition, and cognitive load
slug: team-sizing-and-load
status: drafted
mastery:
seniority: staff
source: An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Sizing Teams" and "Introducing Yourself and Your Team"
prerequisites: [elegant-puzzle/01]
created: 2026-08-10
updated: 2026-08-10
---

# Team sizing, composition, and cognitive load

## TL;DR
A team's size and composition determine its throughput and health as much as the skill of the people on it: too few engineers per manager starves execution, too many overloads the manager's ability to coach and unblock; too narrow a scope wastes context-switching, too broad a scope exceeds what any team can hold in its head. Sizing a team is a deliberate design decision with knowable failure modes on both sides, not something you back into.

## The idea
Managers commonly treat team size as an outcome of hiring luck rather than a design parameter to control. But every team sits somewhere on two independent axes: how many people report to the manager (span of control), and how much surface area the team owns (scope). Both axes have a sweet spot, and both failure directions -- too small/narrow and too large/broad -- produce predictable, recognizable symptoms. Recognizing which failure mode you're looking at tells you exactly what lever to pull.

## How it works

### Span of control: the manager-to-report ratio
A manager has a finite amount of attention. Larson's rule of thumb from the book: roughly 6-8 direct reports is a sustainable steady-state span for a manager who is also expected to do other work (planning, cross-team coordination, their own growth); this can stretch higher (8-10+) for a manager doing pure people-management with no other major responsibility, and should shrink for a new manager still learning the role, or for reports who need heavy hands-on coaching (very junior engineers, someone struggling with performance).

**Symptom of too few reports (e.g., 2-3):** the manager either invents busywork to fill time, over-manages (micromanaging reports who don't need it), or the company is paying management overhead disproportionate to output -- and the manager role itself becomes a poor use of a skilled individual who could otherwise be an IC or manage more people.

**Symptom of too many reports (e.g., 12+ for a hands-on manager):** 1:1s become rushed status updates instead of real coaching, the manager becomes a bottleneck on decisions because they can't context-switch fast enough across that many people's work, and underperformance goes unnoticed longer because there isn't enough individual attention to catch it early.

### Scope: how much a team owns
Independent of headcount, a team's *scope* -- how many distinct systems, products, or problem areas it's responsible for -- has its own sweet spot. A team that owns too narrow a scope (one small service, fully staffed) has idle capacity and low job satisfaction from lack of variety and ownership. A team that owns too broad a scope (five unrelated systems) forces constant context switching, no one develops deep expertise in any one area, and on-call load spikes because the team can't specialize.

**Worked example.** A 6-person payments team owns: the checkout service, the fraud-detection pipeline, and also inherited the legacy invoicing system after its original team was disbanded. Symptom: velocity on checkout (the actual business priority) drops, because engineers rotate onto invoicing on-call and legacy bug fixes instead. The fix isn't "hire more people" (that just grows a team whose scope is still incoherent); it's narrowing scope -- move invoicing to a different team or explicitly deprioritize/sunset it -- so the remaining headcount concentrates on one coherent area.

### Cognitive load as the underlying resource being allocated
Team Topologies-style thinking (which Larson's framing anticipates) treats **cognitive load** as the scarce resource a team-sizing decision is actually managing: how much can a given group of people hold in their heads at once -- the domain knowledge, the operational quirks, the number of interfaces to other systems -- before quality and speed both degrade. Two teams of equal headcount can have wildly different effective capacity if one owns a single cohesive domain and the other owns four unrelated ones. This is why "just add headcount" doesn't fix an overloaded team if the scope itself is incoherent: more people sharing an incoherent scope still each carry the same excessive cognitive load individually, because ownership, on-call rotations, and context don't average out across people the way raw task count does.

### The two independent dials, together
| | Narrow scope | Broad scope |
|---|---|---|
| **Small headcount** | Healthy small team, or under-resourced for its ambitions | Overloaded: too much to hold in head per person |
| **Large headcount** | Underutilized, manager span too wide for the actual work | Needs splitting (see `elegant-puzzle/05`) -- large AND broad rarely stays coherent |

Diagnosing a struggling team means locating it on this grid before reaching for a fix, because "hire more" only helps the underutilized-headcount cells and actively worsens the cognitive-load problem if scope isn't also addressed.

## Pros
- Turns a vague complaint ("this team feels stretched") into a specific, falsifiable diagnosis (span problem vs. scope problem vs. both).
- Prevents the reflexive "just hire more" response, which often doesn't fix -- and can worsen -- a scope-driven overload.
- Gives managers a proactive tool: check span and scope on a regular cadence, before a team visibly breaks.

## Cons
- Ratios like "6-8 reports" are rules of thumb, not laws; the right number depends heavily on report seniority, manager experience, and how much non-people-management work the manager also does.
- Scope is harder to measure than headcount -- there's no single number for "how much cognitive load," so this requires qualitative judgment, not just counting.
- Rebalancing scope usually means moving ownership across team boundaries, which has real transition costs (see `elegant-puzzle/05`) that this framework doesn't itself solve.

## Alternatives
- **Team Topologies' four team types and interaction modes** -- a more formalized vocabulary (stream-aligned, platform, enabling, complicated-subsystem teams) for the same scope-and-cognitive-load problem; worth learning if you need a shared language across an org, but Larson's simpler span/scope framing is often enough for a single manager's decision.
- **Two-pizza teams (Amazon)** -- a hard headcount cap (roughly 6-10 people) as the primary lever, with scope implicitly following from whatever that headcount can cover; simpler to apply uniformly but ignores that some domains genuinely need more or fewer people regardless of the pizza-count heuristic.
- **Pure hiring-plan-driven sizing** -- size teams to match a headcount budget handed down from finance/leadership rather than to match scope; administratively simple, but decouples team size from the actual work, reliably producing the overload/underload symptoms above.

## When to use it
Apply this whenever you're forming a new team, evaluating whether a struggling team needs more people versus less scope, or deciding whether a manager's span of control is sustainable. It's also the right first check whenever someone proposes "just hire more engineers" as the fix for a slow team.

## When NOT to use it
Don't use headcount/scope analysis as the explanation for every team problem -- a well-sized, well-scoped team can still struggle from unclear priorities, poor technical decisions, or interpersonal conflict, none of which sizing fixes. Treat this as one diagnostic lens among several, not the universal one.

## Key takeaways / mental model
Plot any struggling team on the span-vs-scope grid before proposing a fix: is the manager overloaded with reports, or is the team overloaded with incoherent scope, or both? "Hire more people" only ever addresses the first; the second requires narrowing what the team owns, not growing who's on it.

## Self-check questions
1. A manager has 4 direct reports and complains of being overwhelmed. Given the span-of-control framing, what other factors (beyond headcount) would you check before concluding the span itself is the problem?
2. Describe a team you've been on or observed that owned too broad a scope. What symptom showed up first -- velocity, on-call burden, or something else -- and would adding headcount have fixed it?
3. Why can two teams with identical headcount have very different effective capacity? Use the cognitive-load idea in your answer.
4. Your VP proposes solving a slow-moving team's problems by adding 3 more engineers. Using the grid in this lesson, what question would you ask before agreeing?

## References
- An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Sizing Teams" and "Introducing Yourself and Your Team", Part I.
