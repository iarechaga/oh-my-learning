---
id: sre/10
subject: sre
title: Postmortems and Organizational Learning from Failure
slug: postmortems-learning
status: drafted
mastery:
seniority: senior
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 15-16
prerequisites: [sre/09]
created: 2026-08-10
updated: 2026-08-10
---

# Postmortems and Organizational Learning from Failure

## TL;DR
A postmortem is a written record of an incident that focuses on *what happened and why the system allowed it*, explicitly avoiding blame on individuals — because a blame-oriented postmortem teaches people to hide mistakes and route around scrutiny, while a blameless one teaches the organization to surface and fix the structural conditions that made the incident possible. The postmortem's value is entirely in the follow-up: action items that actually get done, not the document itself.

## The idea
Every organization has incidents; the difference between organizations that get more reliable over time and those that keep repeating the same failures is usually not incident *frequency* but what happens *after* — whether the organization extracts and acts on the lesson, or moves on without changing anything structural. A postmortem is SRE's mechanism for making that extraction deliberate and durable rather than left to individual memory.

The "blameless" framing is not a soft, feel-good add-on — it's load-bearing for the mechanism to work at all. If a postmortem is used to identify who to discipline, engineers rationally learn to minimize what they disclose, obscure timelines, and avoid being the one who reports a near-miss. That directly destroys the organization's ability to learn, because most of the useful signal (what almost went wrong, what a person nearly did that would have made it worse, what confusing state the tooling put them in) only surfaces if the person involved trusts that describing it honestly won't be used against them.

## How it works

### The trigger: when a postmortem is required
The book recommends postmortems be triggered by objective criteria, not manager discretion — commonly: any incident with an SLO/error-budget impact above a threshold (e.g., burns more than X% of the monthly budget), any incident involving data loss, any incident requiring emergency response/paging, or any incident where the response itself revealed a process gap (even if user impact was small). Fixed, objective triggers prevent postmortems from being skipped selectively for incidents someone would rather not examine closely.

### The required structure
A good postmortem contains, at minimum:
- **Summary** — one paragraph: what broke, user impact, duration.
- **Impact** — quantified: error-budget minutes consumed (tie directly to `sre/04`'s math), number of users/requests affected, any data loss.
- **Root cause(s)** — usually plural; real incidents rarely have one single cause, they have a chain of conditions that each individually seemed fine.
- **Detailed timeline** — timestamped, factual: when the problem started, when it was detected, when each mitigation step was taken, when it was resolved.
- **What went well / what went poorly / where we got lucky** — a deliberately broader lens than just "what broke," because "we got lucky" items (a coincidence that limited the blast radius) are often the most important signal that the system is more fragile than the observed outcome suggests.
- **Action items** — concrete, owned, dated follow-ups, each tied to a specific finding.

**Worked example — a compressed timeline.** A caching layer misconfiguration causes 15 minutes of 60% error rate:
```
14:02 - Config change deployed to caching layer (intended: increase TTL; actual: set TTL to 0)
14:03 - Cache hit rate drops from 94% to 2%; database load spikes
14:05 - Database connection pool saturates; error rate begins climbing
14:06 - Alert fires (fast-burn error-budget alert, per sre/07)
14:08 - On-call acknowledges, begins investigation
14:14 - Root cause identified (the config change)
14:17 - Rollback deployed
14:19 - Error rate returns to baseline
```
From this timeline alone, several non-obvious findings emerge: 12 minutes elapsed between the bad deploy and the alert firing at 14:06 largely because the alert was tuned as a fast-burn (1-hour window) rather than catching it in the first minute — a finding that feeds directly into `sre/07`'s alert-tuning work. And 8 minutes elapsed between acknowledgment and root-cause identification, pointing to a missing piece of observability (config-change history wasn't visible on the same dashboard as the error-rate graph) rather than an on-call skill gap — this is the "blameless" reframe in action: the finding is "the tooling didn't surface a relevant change," not "the on-call engineer was slow."

### Root cause as a chain, not a single point
The book pushes back on "the root cause was the bad config change" as too shallow. A better analysis asks, at each step, "why did this condition exist, and what let it propagate?" — often called the "five whys" technique, applied loosely: Why did the error rate spike? Because cache hit rate collapsed. Why did the config change cause that? Because TTL=0 wasn't caught by any validation. Why wasn't it caught? Because there was no automated check for that config field. Why wasn't there a check? Because config validation coverage was never prioritized as a project. This chain surfaces multiple independent, addressable action items (add field-level config validation; add config-change annotations to the error-rate dashboard; tune the alert's detection window) instead of stopping at "someone made a typo," which produces no actionable fix at all (typos will always happen; systems should be defended against them).

### Making action items actually happen
A postmortem's value is zero if its action items don't get done. The book recommends: each action item gets a named owner and a due date, is entered into the same tracking system as regular engineering work (not a separate, easily-ignored "postmortem backlog"), and — for the highest-severity incidents — is reviewed at a fixed cadence (e.g., a monthly reliability review) until closed. **Worked example.** Of the three action items from the timeline above, the config-validation one is prioritized against the next sprint's other work using the same backlog and stakeholders as feature work (echoing `sre/01`'s point that reliability work and feature work compete for the same resourcing, openly, rather than reliability work being an unfunded side project).

### Blameless doesn't mean consequence-free
An important nuance: "blameless" means the *postmortem process* doesn't punish individuals for honest disclosure — it does not mean there's never any organizational consequence for a pattern of problems (e.g., a service with chronically poor test coverage causing repeated incidents might genuinely need a resourcing or prioritization conversation). The distinction is between examining *systemic* conditions (which can lead to real organizational changes) versus scapegoating an *individual* for an outcome that the system's design made likely regardless of who was on shift that day.

## Pros
- Blamelessness measurably increases the honesty and completeness of incident reports, because engineers aren't incentivized to hide or minimize what happened.
- The "chain of causes" framing (vs. single root cause) surfaces multiple independent, addressable fixes instead of one shallow, un-actionable conclusion.
- Tying action items into normal engineering backlogs with owners and dates converts the postmortem from a historical record into an actual reliability-improvement engine.

## Cons
- Requires genuine cultural commitment from leadership; a single postmortem used punitively (even once) can permanently damage trust in the "blameless" label for the whole organization.
- Writing a good postmortem (accurate timeline, honest "what went poorly," well-scoped action items) takes real time and skill — a rushed, superficial postmortem provides little of the learning value.
- Action items compete with feature work for the same engineering capacity; without genuine prioritization discipline, postmortem findings pile up unaddressed and the practice degrades into paperwork.

## Alternatives
- **No formal postmortem, informal "we'll remember for next time"** — zero process overhead, but relies entirely on individual memory and informal conversation, which reliably fails to propagate lessons beyond the specific people involved in the incident, especially as teams grow or turn over.
- **Blame-oriented incident review (identify who was responsible)** — can feel satisfying organizationally ("someone is accountable"), but as this lesson argues, actively degrades the honesty and completeness of future incident reports, undermining the entire learning loop.
- **Root-cause-only report with no "what went well / got lucky" section** — narrower and faster to produce, but misses the often-more-valuable signal about near-misses and hidden fragility that a broader lens surfaces.

## When to use it
Write a postmortem for any incident meeting your organization's objective trigger criteria (SLO impact threshold, data loss, paging), and treat the "blameless" framing as non-negotiable — one punitive exception undermines the practice broadly, not just for that one incident.

## When NOT to use it
Don't run a full formal postmortem process for trivial, no-impact events that don't meet the trigger criteria — reserve the time investment for incidents that actually threaten the SLO or reveal a real gap. Don't accept a postmortem that stops at a single shallow root cause ("a typo") without asking why the system allowed that typo to matter — that's a missed opportunity even when the process itself was nominally followed.

## Key takeaways / mental model
A postmortem's job is to convert one bad day into durable, structural improvement — but only if it's honest (blameless), goes deep enough (chain of causes, not one root cause), and its action items actually get resourced like real engineering work. Judge a postmortem practice not by how many documents exist, but by whether the same class of incident keeps recurring.

## Self-check questions
1. A postmortem concludes "the root cause was the on-call engineer pushing an unreviewed config change." Critique this conclusion using the "chain of causes" framing from this lesson, and propose at least two deeper, more actionable findings it might be missing.
2. Explain, using a concrete mechanism (not just "people get scared"), how a single punitive use of a postmortem can degrade the honesty of every future postmortem at the organization.
3. What's the difference between "blameless" and "consequence-free" as this lesson defines them? Give an example of a legitimate organizational consequence that doesn't violate blamelessness.
4. A team has written 12 postmortems over the past year, each with 3-4 action items, but the same category of incident (database connection pool exhaustion) has recurred four times. What does this suggest is broken in the postmortem *process* itself, separate from the quality of any individual postmortem document?

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 15 ("Postmortem Culture: Learning from Failure") and Chapter 16 ("Tracking Outages").
- See also: `sre/09` (incident command, which produces the raw timeline a postmortem is built from), `sre/04` (error budgets, quantifying impact), and `devops-reliability/devops-handbook` (forthcoming) for the broader continual-learning culture this practice is one implementation of.
