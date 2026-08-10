---
id: seeking-sre/10
subject: seeking-sre
title: Reliability in Regulated and High-Risk Environments
slug: reliability-regulated-environments
status: drafted
mastery:
seniority: staff
source: Seeking SRE (David Blank-Edelman, ed.), essay on adapting SRE practice for finance, healthcare, and other regulated industries
prerequisites: [seeking-sre/02, sre/03]
created: 2026-08-10
updated: 2026-08-10
---

# Reliability in Regulated and High-Risk Environments

## TL;DR
In regulated industries (finance, healthcare, and similar), several SRE defaults need explicit modification, not wholesale abandonment: blameless culture must coexist with formal individual accountability requirements, error budgets need a compliance floor that overrides normal release-governance trade-offs, and postmortems need a dual-audience format (internal learning plus an auditable external-facing record) — the underlying SRE principles still apply, but the naive, unmodified version of each practice can create real regulatory or patient-safety exposure.

## The idea
Most of this subject's practices (error budgets, blameless postmortems, on-call sustainability, toil triage) assume a context where the main cost of unreliability is business cost — lost revenue, damaged trust — and where the org has full discretion over its own risk tolerance. Regulated industries add a second, non-negotiable constraint layer: some reliability failures carry legal, regulatory, or safety consequences that no error budget can trade away, and some transparency practices (fully blameless, no individual accountability trail) can directly conflict with regulatory requirements for auditable accountability.

The book's framing here isn't "SRE doesn't apply in finance and healthcare" — it's that a team applying SRE in these contexts needs to explicitly identify which practices need a compliance-aware modification, and get that modification right, rather than either ignoring the regulatory reality (dangerous) or assuming SRE simply doesn't fit and abandoning its useful parts (wasteful).

## How it works

### The compliance floor beneath error budgets
A normal error budget (`sre/04`) treats the SLO as a target the organization chose and can, in principle, trade off against feature velocity. In a regulated context, some reliability failures cross into **hard compliance floors** that aren't tradeable at all — for example, a healthcare system's patient-data access logging must be available essentially without exception (a regulatory requirement, not a business preference), regardless of what the "normal" error budget for that subsystem would otherwise tolerate. The practical adaptation: separate a service's SLIs into two tiers — a normal, tradeable error budget tier for most functionality, and a zero-tolerance compliance tier for the specific functions where a breach isn't a budget event but an incident requiring immediate escalation and, often, mandatory external reporting. Conflating the two tiers (treating a compliance breach as "just" a budget event) is a common and serious mistake.

### Reconciling blamelessness with accountability requirements
`seeking-sre/05` builds internal psychological safety by ensuring root-cause analysis never terminates at a person's name. Regulated industries often have a formal, legally-mandated accountability requirement (e.g., financial services regulations requiring a documented, named responsible party for certain classes of system change; healthcare requiring an auditable record of who accessed what and when). These aren't actually in conflict if handled deliberately: the internal postmortem culture stays blameless in its *learning* function (root-cause analysis still goes past "a person made a mistake" to the systemic gap), while a **separate, structurally distinct compliance record** — required regardless of the postmortem's internal culture — captures the factual, named-individual audit trail regulators require. The critical discipline is keeping these two documents' purposes clearly separated in how they're used: the compliance record is a factual log, not a performance-management input, and the postmortem's blameless learning process is not weakened by the fact that a parallel factual record also exists.

### Worked example: a financial services incident
A trading platform experiences an outage caused by an engineer's misconfigured deployment. Two parallel processes run:
- **Internal blameless postmortem**: root-cause analysis finds the actual systemic gap (the deployment tool allowed a config change to bypass the normal review gate under a specific rarely-used flag), and the action items fix that gap; the engineer is treated exactly as `seeking-sre/05` prescribes, with the same protection from informal punishment.
- **Regulatory incident record**: a separate, formally required filing documents what happened, when, who initiated the change, and what controls were or weren't in place, because financial regulators require this regardless of the company's internal culture — this record exists to satisfy an external accountability requirement, not to punish the engineer internally.
The two processes don't contradict each other as long as the organization is disciplined about keeping the regulatory record's existence from leaking back into performance reviews or informal blame — which requires exactly the structural separation `seeking-sre/05` recommends between incident response and performance management, now with an added, non-negotiable external reporting obligation layered on top.

### Extra rigor on toil and automation in high-risk functions
`seeking-sre/08`'s "good enough" partial-fix philosophy for toil needs a carve-out for regulated, high-risk functions: a shortcut automation fix for a patient-safety-critical alerting pipeline or a financial transaction-integrity check deserves the more rigorous, comprehensive treatment even at real cost to a small team's capacity, because the cost of a shortcut failing in these specific functions is categorically higher than normal toil-reduction trade-offs assume. The practical rule: tag toil items touching compliance-tier functionality explicitly, and exclude them from the "good enough, 80% effort" default triage.

### On-call and escalation in regulated contexts
Sustainable on-call boundaries (`seeking-sre/04`) still apply, but regulated environments often require faster, more formal escalation paths for compliance-tier incidents specifically — e.g., a mandatory notification to a compliance officer or a regulator within a defined time window (sometimes as short as a few hours) once a qualifying incident is confirmed. This means the on-call runbook needs an explicit, rehearsed branch: "if this incident touches [the compliance-tier list], escalate immediately to [named compliance contact], independent of normal severity triage," so that the urgency of external reporting deadlines isn't discovered live during an already-stressful incident.

## Pros
- Lets regulated organizations retain the real benefits of SRE practice (learning-oriented postmortems, sustainable on-call, structured incident response) instead of either ignoring risk (dangerous) or abandoning SRE entirely (wasteful).
- The two-tier SLI/error-budget split makes the difference between "normal trade-off" and "non-negotiable compliance floor" explicit and legible to engineers making release decisions.
- Structurally separating the compliance record from the blameless postmortem protects psychological safety while still satisfying external accountability requirements.

## Cons
- Adds real process overhead (dual-track documentation, compliance-aware escalation paths) that smaller regulated companies may struggle to resource well.
- Getting the tier boundary wrong (treating something as tradeable that's actually a hard compliance floor, or vice versa) can create genuine legal or safety exposure — this isn't a place where "good enough" triage is acceptable.
- Requires close, ongoing collaboration between engineering and legal/compliance functions that don't always share vocabulary or priorities, adding coordination cost beyond what this subject's other lessons assume.

## Alternatives
- **Treat all reliability work as compliance-tier (maximal caution everywhere)** — avoids the risk of mis-tiering but is usually unaffordable in practice, since it removes the trade-off flexibility (error budgets, "good enough" toil fixes) that makes SRE practice sustainable at all; typically only viable for very small, narrowly-scoped, entirely safety-critical systems.
- **Fully separate compliance function with no integration into SRE practice** — a dedicated compliance team handles regulatory requirements entirely independently of the engineering reliability practice; simpler organizationally but risks exactly the kind of disconnect (engineers unaware of which functions are compliance-tier) this lesson's integrated approach is designed to prevent.
- **External compliance consulting/audit engagement to define the tiering** — bringing in outside expertise to define the compliance-tier boundary and the required processes, especially useful for a company navigating a regulatory framework for the first time; higher upfront cost but reduces the risk of a costly mis-tiering mistake.

## When to use it
Apply this dual-tier adaptation as soon as any part of your system touches a regulated function (financial transactions, health data, safety-critical control systems) — even if most of the company's services are ordinary and don't need it. Scope the compliance tier narrowly and explicitly rather than applying it broadly out of caution, which would erode the practical benefits of normal error-budget trade-offs elsewhere.

## When NOT to use it
Don't apply compliance-tier rigor to reliability work that has no actual regulatory or safety stakes just because the company operates in a regulated industry generally — an internal marketing analytics dashboard at a healthcare company doesn't need the same treatment as the patient-data access system, and treating everything as compliance-tier wastes the flexibility this subject's other practices depend on.

## Key takeaways / mental model
Split your SLIs into two tiers before anything else: normal (tradeable, governed by the usual error-budget mechanics) and compliance-tier (non-negotiable, governed by external requirements). Keep the blameless postmortem's learning function separate from the factual, sometimes named-individual regulatory record it may need to sit alongside — the two aren't in conflict as long as you keep them structurally distinct. Give compliance-tier toil and on-call escalation extra rigor, deliberately, rather than applying this subject's normal small-team shortcuts uniformly.

## Self-check questions
1. A team's patient-data logging system experiences a brief outage. Explain why this shouldn't be handled purely as a normal error-budget event, and describe the two-track process (learning versus compliance record) this lesson recommends instead.
2. How does the lesson reconcile blameless postmortem culture with a legal requirement for a named, individual accountability record? Is this a genuine contradiction, or can both coexist — and how?
3. Why does the lesson argue against treating all reliability work at a regulated company as compliance-tier, even though the caution might seem safer?
4. Design a compliance-tier escalation branch for an on-call runbook at a financial services company, including what triggers it and who gets notified.

## References
- Seeking SRE (David Blank-Edelman, ed.), essay on adapting SRE practice for finance, healthcare, and other regulated industries.
- See also `sre/03` (SLOs, the mechanism this lesson's two-tier split modifies) and `seeking-sre/05` (psychological safety, whose structural separation of incident response from performance management this lesson extends with a compliance record).
