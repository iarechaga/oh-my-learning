---
id: elegant-puzzle/11
subject: elegant-puzzle
title: Managing incidents and reliability as organizational practice
slug: incident-and-reliability-practice
status: drafted
mastery:
seniority: staff
source: An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Managing Incidents" and "On-Call"
prerequisites: [elegant-puzzle/01, elegant-puzzle/03]
created: 2026-08-10
updated: 2026-08-10
---

# Managing incidents and reliability as organizational practice

## TL;DR
Reliability is an organizational design problem as much as a technical one: how you structure incident response, how you run postmortems, and how you staff on-call determine your actual reliability at least as much as your architecture does, and each has predictable failure modes when treated as an afterthought rather than a designed system.

## The idea
It's tempting to treat reliability purely as an engineering problem -- better redundancy, better testing, better monitoring. But two organizations with identical architecture can have very different real-world reliability depending on how well they respond when something does break, how honestly they learn from what broke, and whether on-call is sustainable enough that the people responding are alert and not burned out. Larson treats incident management, postmortems, and on-call as organizational systems with their own design choices and failure modes, the same lens applied throughout this subject to teams and planning.

## How it works

### Incident response: clear roles beat improvisation under pressure
During a live incident, ambiguity about who's doing what is expensive -- multiple people investigating the same lead while nobody drives customer communication, or everyone waiting for someone else to make the call to escalate. A designed incident-response process assigns roles explicitly and in advance (an Incident Commander who coordinates and makes calls but doesn't necessarily debug directly, a technical lead who drives the investigation, a communications lead who updates stakeholders) so that during the actual incident, people fall into pre-defined roles instead of improvising a structure under time pressure, when it's hardest to think clearly. **Worked example.** Without defined roles, a major outage has six engineers all independently investigating in the same Slack thread, duplicating effort, while the VP asks three different people for a status update and gets three different, half-formed answers. With defined roles, the Incident Commander owns a single source of truth on status, assigns specific investigation threads to specific people to avoid duplication, and is the sole point of contact for stakeholder updates -- the technical work is the same, but the coordination overhead drops sharply.

### Postmortems: blameless, and structurally so
A postmortem's value depends entirely on whether people tell the truth about what happened, and people don't tell the truth about their own mistakes in a process that assigns individual blame -- so a blameless postmortem culture isn't just a nicety, it's a precondition for the process producing accurate information at all. "Blameless" doesn't mean no accountability; it means the analysis focuses on *why the system made this error easy to make* (missing alert, unclear runbook, a dangerous default) rather than *who made it*, because the same error will happen again to a different person as long as the underlying condition remains, regardless of how the first person is treated. A good postmortem produces specific, owned, tracked action items -- not just a narrative of what happened -- and treats "what made this mistake easy" as the central question.

### On-call: a scarce, exhaustible resource, not free capacity
On-call is often treated as something engineers absorb on top of their regular workload at no real cost, but disrupted sleep, context-switching out of deep work, and the background stress of being pageable have real costs to both wellbeing and daytime productivity -- on-call is functionally consuming capacity, not a free addition to it. Managing it well means the same span/scope thinking as `elegant-puzzle/03`: a rotation needs enough people (generally at least 4-6) to keep any individual's frequency sustainable, page volume needs to be actively managed down (chronic high page volume is itself a signal something needs fixing, not just tolerated), and on-call compensation or time-off-in-lieu should reflect that it's real, costly work.

**Worked example.** A 3-person team runs its own on-call rotation, meaning each engineer is on-call one week in three. Page volume is high enough that being on-call routinely disrupts sleep multiple nights a week. Attrition on the team is unusually high, and exit interviews cite on-call burden repeatedly -- yet leadership initially reads this as a hiring problem ("we need to backfill faster") rather than an on-call design problem. The actual fix is reducing page volume (fixing the noisy alerts generating unnecessary pages) and growing the rotation size (merging with an adjacent team's on-call, per `elegant-puzzle/05`) so no individual carries the load as often.

### Page volume as a reliability signal, not just an on-call comfort issue
A high volume of pages is diagnostic of underlying system health, not merely an on-call-experience problem to smooth over with compensation: it usually means alerting thresholds are miscalibrated (paging for things that don't need immediate human action) or genuine reliability problems are being tolerated rather than fixed. Treating repeated pages for the same root cause as acceptable background noise, rather than as a signal demanding a real fix, both burns out on-call and hides real reliability debt.

## Pros
- Clear incident roles reduce coordination overhead exactly when it's most costly -- during a live outage, under time pressure.
- Blameless postmortems produce more accurate root-cause analysis, because people report what actually happened rather than a version edited to minimize their own blame.
- Treating on-call as a managed, budgeted resource protects both individual wellbeing and, indirectly, incident-response quality (a rested on-call engineer makes better decisions during a real incident).

## Cons
- Formal incident-response roles and processes have setup and training overhead, and can feel like unnecessary ceremony for genuinely small, low-stakes incidents.
- "Blameless" culture is easy to state and hard to actually sustain -- it erodes quickly the moment leadership visibly punishes someone for an honestly-reported mistake, even once, and rebuilding trust after that is slow.
- Reducing page volume and growing rotation size both require real investment (fixing noisy alerts, restructuring team boundaries) that competes with feature work and is easy to deprioritize until attrition or a major incident forces the issue.

## Alternatives
- **Ad hoc incident response (whoever's around jumps in)** -- no process overhead, works fine for organizations small enough that a handful of people naturally self-coordinate, but degrades into the duplicated-effort, unclear-ownership problem above as the org and incident complexity grow.
- **Blame-assigning postmortems / individual accountability reviews** -- explicitly examines who made the mistake and holds them accountable; can feel more satisfying to leadership seeking accountability, but reliably suppresses honest reporting in future incidents, which degrades the org's ability to learn over time.
- **Follow-the-sun or fully outsourced on-call (e.g., a dedicated SRE/NOC team handles all paging)** -- removes the burden from feature teams entirely; reduces individual on-call burden but can create a knowledge gap where the people paged aren't the people who understand the system best, slowing resolution and reducing the feedback loop that motivates fixing root causes.

## When to use it
Build formal incident-response roles once incidents are frequent or severe enough that ad hoc coordination is visibly failing (duplicated work, confused stakeholder communication). Run blameless postmortems for any incident with real customer or business impact. Actively manage on-call rotation size and page volume as soon as a rotation exists at all, before burnout symptoms appear.

## When NOT to use it
Don't build heavyweight incident-command process for trivial, low-impact issues -- reserve formal roles for incidents above a defined severity threshold, so the process doesn't become its own source of overhead for problems that don't need it.

## Key takeaways / mental model
Reliability is produced as much by how you respond and learn as by what you build. Ask three questions of any reliability system: are roles clear enough that people don't have to improvise coordination under pressure, does the postmortem process actually produce honest information, and is on-call sized and tuned so the humans running it stay effective rather than burning out.

## Self-check questions
1. Describe what goes wrong during a live incident when roles aren't pre-assigned, using a concrete scenario. What's the specific coordination cost?
2. Why does a blameless postmortem culture produce more accurate root-cause information than one that assigns individual blame? What's the mechanism, not just the platitude?
3. A team's on-call rotation has high attrition and leadership wants to fix it by hiring more engineers onto the team. Using this lesson's framing, what would you check before agreeing that's the right fix?
4. High page volume on a service is treated as "just how this system is" and on-call engineers are compensated extra for the burden. What's the risk of treating high page volume this way instead of as a reliability signal demanding a fix?

## References
- An Elegant Puzzle: Systems of Engineering Management (Will Larson), "Managing Incidents" and "On-Call", Part V.
