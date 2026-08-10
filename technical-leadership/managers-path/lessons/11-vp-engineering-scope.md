---
id: managers-path/11
subject: managers-path
title: 'VP of engineering scope: multi-org alignment and execution'
slug: vp-engineering-scope
status: drafted
mastery:
seniority: principal
source: The Manager's Path (Camille Fournier), Chapter 8 - Executive Leadership
prerequisites: [managers-path/10]
created: 2026-08-10
updated: 2026-08-10
---

# VP of engineering scope: multi-org alignment and execution

## TL;DR
A VP of Engineering owns the execution engine of the entire engineering organization - turning company strategy into a coordinated multi-director roadmap, building the processes and metrics that make delivery predictable at scale, and representing engineering as a peer to other executive functions - trading almost all remaining hands-on technical involvement for organizational and cross-functional leverage.

## The idea
Where a director designs and coordinates a set of teams, a VP of Engineering operates a level up: coordinating multiple directors, each responsible for their own set of teams, so the whole engineering org executes coherently against company-level goals. Fournier frames this role as fundamentally an execution and alignment role - the VP's job is less about any single technical decision and much more about whether engineering as a whole is predictable, well-prioritized, and trusted by the rest of the company (product, sales, finance, the CEO) to deliver on commitments.

This is also the level where the leader becomes a full peer to non-engineering executives - a VP of Engineering sits with the VP of Product, VP of Sales, and CFO and has to speak credibly about business trade-offs (cost, timeline, risk, headcount) in terms those peers actually use, not just engineering terms. The technical depth built at earlier levels now mostly shows up as *credibility* and *judgment* - knowing when an engineering estimate or risk claim from below is trustworthy - rather than as direct technical decision-making.

## How it works

### Translate company strategy into an engineering execution plan
Company strategy ("we're betting on enterprise customers this year") doesn't automatically tell each team what to build - the VP's job includes translating that strategy into a prioritized, sequenced engineering roadmap across all the directors' orgs, resolving where different directors' teams would otherwise compete for the same scarce resources (senior engineers, a shared platform team's capacity, a hard deadline that only one initiative can actually hit). Concrete example: two directors both have projects that need the same three senior engineers on the data platform team this quarter. The VP's job is to make the trade-off explicit and defensible against the company's actual priorities, not let it be resolved by whichever director is more persistent or whichever project screams loudest.

### Build organization-wide metrics and predictability
At this scale, a VP can't personally verify each team's status by walking around - they need systems that surface reliable signal: delivery predictability metrics (how often committed work actually ships on time), quality/incident metrics, headcount and hiring pipeline health, and engagement/retention signals across the org. Fournier's caution here is that metrics chosen carelessly get gamed or optimized in ways that damage the underlying thing they were meant to measure (e.g., a raw "story points shipped" metric incentivizes inflating estimates); good org-level metrics need to be chosen and interpreted with real care, and treated as directional signals for further investigation, not absolute truth.

### Represent engineering credibly to peer executive functions
A VP of Engineering routinely has to negotiate with a VP of Sales who wants a custom feature promised to a big customer, or a CFO who wants headcount cut, or a CEO who wants an aggressive public timeline. Doing this well requires genuine fluency in the other functions' concerns (revenue impact, cost structure, competitive risk) alongside engineering's own constraints, and the credibility to say "no" or "not by then" persuasively when it's the right call - credibility built from a track record of engineering actually delivering on the commitments the VP does make. A VP who over-promises to avoid short-term friction with peers erodes that credibility for every future negotiation.

### Develop the director layer, mirroring the manager-of-managers pattern one level up
Just as a manager-of-managers coaches managers rather than managing their reports directly (`managers-path/08`), a VP coaches directors on organization design, cross-team planning, and their own people-management chops, rather than personally redesigning team boundaries or sitting in on individual 1:1s. The VP's visibility into any single team is now several layers removed, which makes deliberately built signal (skip-level conversations, director performance reviews, org health surveys) even more essential than at the director level.

## Pros
- Creates coherent, company-aligned execution across an entire engineering org, resolving resource conflicts and priority tensions that no single director could resolve alone.
- Builds engineering's credibility and influence with the rest of the executive team, which materially affects engineering's ability to get resourcing, protect technical investment, and shape company strategy rather than just receive it.
- Establishes org-wide systems (metrics, planning cadences, leadership development) that make the organization's output predictable and resilient beyond any single leader's personal attention.

## Cons
- Very high leverage but very low direct visibility - real problems on individual teams are now four-plus layers removed and can persist a long time before reaching the VP through normal channels.
- Cross-functional negotiation is a genuinely different skill from engineering management, and some technically excellent leaders struggle to build the credibility and communication style needed with non-engineering peers.
- Org-wide metrics are easy to design badly, and bad metrics actively distort behavior at scale in ways that are hard to detect and reverse once entrenched.

## Alternatives
- **VP of Engineering with a strong Chief of Staff / VP of Engineering Operations** - delegate significant execution/metrics/process ownership to a dedicated operations role, freeing the VP to focus more on strategy and cross-functional relationships; adds a coordination role but scales well in large orgs.
- **Co-VP or split VP model (e.g., VP Product Engineering + VP Platform Engineering)** - split VP scope by domain rather than having one person own all of engineering; reduces any single VP's span but requires very tight alignment between the co-VPs to avoid the org fragmenting.
- **Flatter reporting directly to CTO with no VP layer** - in smaller companies, directors may report directly to a CTO who also carries VP-level execution responsibility; works at smaller scale, breaks down as the org grows past what one person can track (see `managers-path/12` for how CTO scope differs).

## When to use it
Once an org has grown to multiple directors whose teams' work needs company-level prioritization and resourcing trade-offs, and needs a single accountable owner for engineering's overall delivery predictability and its relationship with the rest of the executive team.

## When NOT to use it
Don't create a VP layer purely to match a competitor's org chart or as a title reward for a strong director - the role only makes sense once there's a genuine multi-director coordination and cross-functional-negotiation problem to solve; before that point, it adds a layer without a corresponding need. And don't let a VP retreat into pure process/metrics work disconnected from genuine engineering judgment - the credibility this role depends on is built on real, well-informed technical and organizational judgment, not just dashboards.

## Key takeaways / mental model
A VP of Engineering's leverage comes from making the whole org's execution trustworthy to the rest of the company - build the systems (metrics, planning, director development) that make delivery predictable at scale, and spend your personal credibility carefully in cross-functional negotiations, because it's the currency this role runs on.

## Self-check questions
1. Two directors' teams are both competing for the same scarce senior engineers this quarter. What information would you need to make the trade-off, and how would you make the decision defensible to both directors?
2. Why does Fournier warn that org-wide metrics chosen carelessly can be actively harmful, not just unhelpful? Give an example of a metric that could be gamed.
3. What is the practical difference between a VP of Engineering's technical involvement and a director's, given both are several steps removed from hands-on coding?
4. Describe what "spending credibility" looks like in a negotiation with a VP of Sales who wants an aggressive, engineering-unrealistic delivery date. What happens to future negotiations if the VP of Engineering just says yes to avoid friction?

## References
- The Manager's Path (Camille Fournier), Chapter 8: "Executive Leadership".
