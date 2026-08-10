---
id: managers-path/10
subject: managers-path
title: 'Director scope: organization design and cross-team planning'
slug: director-scope
status: drafted
mastery:
seniority: principal
source: The Manager's Path (Camille Fournier), Chapter 7 - Managing Multiple Teams
prerequisites: [managers-path/08, managers-path/09]
created: 2026-08-10
updated: 2026-08-10
---

# Director scope: organization design and cross-team planning

## TL;DR
A director's scope shifts from managing people directly to designing the organization itself - team boundaries, ownership lines, and cross-team planning processes - so that multiple teams can execute coherently on a shared set of goals without the director personally coordinating every interaction between them.

## The idea
By the director level, most of a leader's direct reports are managers (see `managers-path/08`), and the unit of work is no longer a team but a *set* of teams that must collaborate, share dependencies, and sometimes compete for the same resources. The core new skill is organization design: deciding how to draw team boundaries so that ownership is clear, dependencies between teams are minimized where possible, and each team has a mission that's both meaningful on its own and coherent with the larger goal. Conway's Law - the observation that a system's architecture tends to mirror the communication structure of the organization that builds it - becomes directly actionable at this level: a director who draws team boundaries badly (splitting a tightly-coupled system across two teams that don't communicate well) will, predictably, get a badly-coupled system back, no matter how good the individual engineers are.

Cross-team planning is the second core skill: getting multiple teams, each with their own manager and priorities, aligned on a shared roadmap where dependencies are visible and sequenced correctly, rather than each team planning in isolation and discovering conflicts only when a promised dependency slips.

## How it works

### Draw team boundaries around ownership, not just headcount
A director deciding how to split, say, a 30-person org into teams needs to think about what each team can own end-to-end - ideally a team owns a coherent piece of the system (a service, a domain) with minimal cross-team dependencies for its regular work, because every cross-team dependency is a coordination tax paid on every project that touches it. Concrete example: splitting a checkout system into a "front-end checkout UI" team and a "back-end payments" team, when the two must ship in lockstep for almost every feature, creates constant coordination overhead; splitting instead around "checkout" as one team owning both layers for a coherent slice of the domain, with a separate "shared payments infrastructure" team providing a stable API, reduces that overhead by aligning ownership with how work actually flows.

### Use Conway's Law deliberately, not just observe it
Since system architecture tends to mirror org communication structure, a director can use this proactively: if the target architecture is a set of loosely-coupled services, design the org as a set of loosely-coupled teams with clear APIs between them first, rather than hoping a tightly-coupled org will somehow produce a loosely-coupled system. This is sometimes called the "inverse Conway maneuver" - restructure the org to get the architecture you want, rather than only accepting the architecture the current org structure implies.

### Build a cross-team planning process that surfaces dependencies early
Without a deliberate process, cross-team dependencies surface as surprises mid-quarter ("we didn't know we were blocked on your team's API until now"). A director's job includes establishing a planning rhythm - a quarterly planning cycle where teams declare what they need from each other, a shared roadmap visible across teams, a forum where conflicting priorities get negotiated explicitly - so dependencies are identified and sequenced before teams commit to a quarter's work, not discovered after. Concrete example: at quarterly planning, Team A's roadmap depends on an API from Team B that Team B hadn't prioritized. A working cross-team planning process surfaces this in a shared planning meeting in week one of the cycle, letting the director (or the two managers) negotiate a resequencing; without such a process, it surfaces in week eight as a blown deadline.

### Balance team-level autonomy against org-level coherence
Too much central control from the director (dictating every team's roadmap in detail) slows teams down and disengages the managers underneath, who lose ownership of their own team's priorities. Too little (every team purely sets its own priorities with no cross-team lens) produces duplicated effort, conflicting architecture decisions, and unaddressed shared infrastructure that no single team is incentivized to own. A director's judgment call is finding the right balance for the org's current maturity - generally, more central coordination when teams are new or dependencies are high, more autonomy as teams and their interfaces mature.

## Pros
- Deliberate organization design reduces the ongoing coordination tax that comes from poorly-drawn team boundaries, compounding in saved time across every future project.
- A working cross-team planning process surfaces dependency risk early, when it's cheap to resequence, instead of late, when it causes missed commitments.
- Using Conway's Law proactively gives a director a lever over system architecture that operates at the org level, complementing (not replacing) the technical strategy work in `managers-path/09`.

## Cons
- Reorganizing team boundaries has real human cost - changing who someone works with and what they own is disruptive, and doing it too often erodes trust and team identity.
- Cross-team planning processes add real overhead (planning meetings, shared roadmap maintenance) that can become bureaucratic if not kept lightweight and genuinely useful.
- Getting the autonomy/coherence balance wrong in either direction has slow-to-detect costs - too much autonomy shows up as duplicated effort discovered months later; too much control shows up as disengaged managers whose demotivation is easy to misattribute to other causes.

## Alternatives
- **Fully centralized planning (PMO-driven)** - a dedicated program/project management function drives all cross-team sequencing centrally; can work well for very large, complex, interdependent programs but adds a layer between the director and the actual technical trade-offs.
- **Fully autonomous team model (e.g., "two-pizza teams" with minimal cross-team process)** - each team owns its full domain end-to-end with almost no formal cross-team planning; works well when team boundaries are drawn well enough that dependencies are genuinely rare, breaks down when they aren't.
- **Platform team model** - a dedicated team builds shared infrastructure/tooling consumed by product teams as an internal product with its own roadmap and SLAs, rather than ad hoc cross-team dependencies; reduces coordination tax for shared concerns at the cost of the platform team's own prioritization overhead.

## When to use it
Once a director is responsible for multiple teams whose work genuinely interacts - shared systems, shared roadmap goals, or shared constrained resources - and needs both the org structure and the planning process to make that interaction predictable rather than accidental.

## When NOT to use it
Don't reorganize team boundaries reactively every time a cross-team friction surfaces - frequent reorgs cost more in disruption than most individual coordination problems are worth; reserve structural changes for patterns of friction, not one-off incidents. And don't impose heavyweight, centralized cross-team planning on teams whose work genuinely doesn't interact much - that just adds coordination overhead with no corresponding coherence benefit.

## Key takeaways / mental model
Team boundaries are an architecture decision, not just an HR one - Conway's Law means the org chart will show up in the system's shape whether or not you plan for it, so design boundaries and planning rhythms deliberately around the coherence and architecture you actually want.

## Self-check questions
1. Explain Conway's Law and the "inverse Conway maneuver" in your own words, with an example from a system you know.
2. A cross-team dependency surfaces as a surprise in week eight of a quarter, blowing a deadline. What process gap does this reveal, and how would you fix it going forward?
3. Describe a case where more team autonomy would be the right call, and a case where more centralized coordination would be, and explain what's different between them.
4. Your org is considering splitting one team into two along a new boundary. What questions would you ask about ownership and dependencies before deciding where to draw the line?

## References
- The Manager's Path (Camille Fournier), Chapter 7: "Managing Multiple Teams".
