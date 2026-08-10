---
id: sre/05
subject: sre
title: "Toil: Identifying, Quantifying, and Prioritizing Elimination"
slug: toil-elimination
status: drafted
mastery:
seniority: senior
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 5
prerequisites: [sre/01]
created: 2026-08-10
updated: 2026-08-10
---

# Toil: Identifying, Quantifying, and Prioritizing Elimination

## TL;DR
Toil is operational work that is manual, repetitive, automatable, tactical, devoid of enduring value, and scales linearly with service growth — not "any work you dislike." Google caps toil at 50% of an SRE's time specifically because unchecked toil grows to consume 100% of a team's capacity as a service scales, silently squeezing out the engineering work that would have prevented that growth in the first place.

## The idea
Every operations team accumulates recurring manual tasks: restarting a stuck process, manually provisioning a new customer's resources, hand-editing a config for each new deployment, running a script to clear a queue backlog. Individually these feel small. The trap is that they *compound*: as the service grows (more customers, more deployments, more edge cases), the volume of this work grows too — often linearly with traffic or headcount — while the team's capacity to do it does not grow at the same rate. Eventually the team is spending all its time keeping up with manual work and has none left to build the automation or architecture fixes that would reduce that work. This is the toil trap, and it's why the book treats toil identification and elimination as a first-class, resourced engineering priority rather than an unavoidable cost of running things.

The crucial reframe: toil is not "operational work" in general, and it's not defined by being unpleasant. Plenty of operational work is valuable engineering (writing a runbook, designing a rollback strategy, tuning an alert). Toil is specifically the *subset* of operational work with a defined set of properties — and the definition matters because it's what lets a team argue, with evidence, "this specific task should be automated" instead of "ops work in general is bad."

## How it works

### The six defining properties of toil
The book gives a precise checklist. Work is toil to the extent it is:
1. **Manual** — a human is doing something a machine could do (typing commands, clicking through a UI), not designing or deciding.
2. **Repetitive** — the same or similar task recurs, not a one-time novel problem.
3. **Automatable** — a machine could do it as well as (or better than) a human, given engineering investment; if it genuinely requires human judgment every time, it isn't automatable toil (though it may still be a target for better tooling/decision support).
4. **Tactical** — reactive, interrupt-driven work responding to events, rather than strategic, planned engineering.
5. **No enduring value** — completing the task doesn't leave the system in a permanently better state; the same problem recurs and must be solved again. (Contrast: writing a migration script that permanently removes a class of manual work *is* enduring value, even though writing it once felt like "ops work.")
6. **Scales linearly with service growth** — as traffic, users, or infrastructure grow, the volume of this task grows proportionally, unlike engineering work whose *value* scales with the system but whose *required effort* doesn't have to.

Work that satisfies most or all six is toil. Work that's manual but non-repetitive (a one-off migration), or repetitive but strategic (a weekly architecture review), is not toil by this definition — this precision is what keeps the concept from becoming a catch-all complaint bucket.

### Worked example: is this toil?
**Task: "Provision storage quota for a new internal team requesting access to a shared cluster."** Walk it through the checklist:
- Manual? Yes — an SRE runs a script and edits a config file by hand.
- Repetitive? Yes — happens roughly 3 times a week as new teams onboard.
- Automatable? Yes — the inputs (team name, requested quota, cluster) are well-defined and the logic (validate against a quota policy, apply the config, notify the requester) doesn't require human judgment.
- Tactical? Yes — it's a reactive response to an incoming request, not planned work.
- No enduring value? Yes — provisioning team #47 leaves the system no better positioned to provision team #48; the same manual steps repeat.
- Scales linearly? Yes — quota requests grow roughly with headcount growth across the company.

Verdict: this is toil, and a strong automation candidate (a self-service provisioning tool with policy-based limits). Contrast with **"investigating a novel data-corruption bug reported once by a customer"** — manual, yes, but not repetitive, not clearly automatable (requires judgment), and resolving it (if the root cause is fixed in code) has enduring value. Not toil — this is core engineering work, even though it's also reactive and unplanned.

### Quantifying toil
The book recommends teams track toil explicitly, typically via time-tracking during on-call shifts or periodic surveys ("what fraction of your week was spent on toil vs. engineering?"), rolled up per-person and per-team. **Worked example.** A 6-person SRE team tracks time for a month: total capacity is 6 people x 40 hours x 4 weeks = 960 hours. If the team logs 460 hours on toil-classified tasks (interrupt-driven manual provisioning, restarting stuck jobs, manual failovers), that's 460/960 = **48% toil** — right at the edge of Google's 50% cap. If next quarter that number is 65% because a new product launch tripled manual onboarding requests, that's a quantifiable, visible signal (not a vague complaint) that triggers the policy response: reallocate people, or prioritize automating the specific tasks driving the increase.

### Prioritizing which toil to eliminate first
Not all toil is equally worth automating — building automation itself costs engineering time, so it needs to pay back. A simple prioritization framework: `estimated hours saved per month x probability the task volume keeps growing`, weighed against the estimated engineering cost to automate. **Worked example.** Two toil candidates:
- Task A: manual log rotation on 3 legacy servers, costing 2 hours/month, stable (not growing), and the servers are slated for decommission in 6 months.
- Task B: manual customer-quota provisioning, costing 20 hours/month, and growing 15%/quarter as the company scales.

Task B is the clear priority even though both are "toil" — the payback period is shorter and the growth trend means the cost compounds if left alone, while Task A is a shrinking, bounded cost not worth the engineering investment to automate away before it disappears on its own.

### The trap of "toil creep" via undocumented exceptions
A subtle failure mode: a task starts as legitimate engineering work (a novel migration) but is repeated with minor variations often enough that it quietly becomes toil without anyone noticing, because each instance "feels" different. The book's guidance: periodically re-audit recurring tasks against the six-property checklist rather than assuming a task's original classification still holds — toil frequently sneaks in through this route as a service matures and its edge cases become well-trodden.

## Pros
- Gives teams a precise, defensible vocabulary to argue for automation investment ("this specific recurring task meets the toil definition and costs N hours/month") instead of vague complaints about workload.
- The 50% cap (`sre/01`) creates an organizational forcing function: toil growth becomes a visible resourcing problem rather than something that silently consumes a team.
- Directly informs automation prioritization (`sre/06`) with quantified, comparable data instead of gut feel about what's most annoying.

## Cons
- Measuring toil accurately requires disciplined time-tracking, which is itself a small tax on the team and easy to do sloppily (self-reported time estimates are notoriously biased).
- The six-property definition, while precise, requires judgment calls in ambiguous cases (is this task "automatable" with reasonable effort, or only in theory?) — teams can disagree in good faith.
- Automating toil away has an upfront engineering cost that competes with other roadmap priorities; a team under-resourced even for engineering work may struggle to ever "buy down" its toil despite correctly identifying it.

## Alternatives
- **Treat all operational work as an undifferentiated cost center to be minimized generally** — simpler to talk about, but loses the precision that lets a team distinguish "this is worth automating" from "this is valuable, if reactive, engineering work" — risks either automating the wrong things or dismissing real engineering as "just ops."
- **Outsource repetitive operational work to a separate team or vendor** — removes the toil from the engineering team's plate, but doesn't eliminate the underlying manual work or its linear scaling; often just relocates the toil trap to a team with less power to fix its root cause.
- **Accept toil as a fixed cost of scale with no cap or elimination goal** — the pre-SRE default; risks the toil trap consuming the team's entire capacity as the service grows, with no structural forcing function to stop it.

## When to use it
Apply the toil framework to any recurring operational task an SRE or on-call engineer performs, especially once total operational load starts crowding out planned engineering work. Use the six-property checklist explicitly when arguing for or against automating a specific task — it keeps the conversation evidence-based.

## When NOT to use it
Don't apply the "toil" label loosely to any work someone finds tedious or unglamorous — the definition is precise for a reason, and diluting it (e.g., calling all on-call work "toil") undermines its usefulness as a prioritization tool. Also don't chase eliminating low-volume, non-growing toil ahead of higher-cost, growing toil purely because it's easy to automate — prioritize by projected cost, not by ease of the automation project.

## Key takeaways / mental model
Ask six questions of any recurring task: manual? repetitive? automatable? tactical? no enduring value? scales with growth? If most are yes, it's toil, and it will keep growing unless something is built to eliminate it. The 50% cap isn't a target to hit exactly — it's a tripwire: crossing it means the team's growth trajectory has outpaced its ability to keep the system healthy by hand, and something (automation investment, headcount, architecture) needs to change.

## Self-check questions
1. A team spends 10 hours/week manually rotating TLS certificates for 40 internal services because the renewal process isn't automated. Walk through the six-property toil checklist and argue whether this is toil.
2. Explain why "investigating a novel, one-off data corruption bug" is not toil even though it is manual, unplanned, and tedious.
3. Given two toil candidates with equal current monthly cost, one shrinking and one growing 20%/quarter, which should a team prioritize automating first, and why does the growth trend matter more than current cost alone?
4. A team reports 30% toil in its first quarterly measurement and 55% in its second, driven by a new product launch. Using the SRE model from `sre/01`, describe two different organizational responses this data should trigger.

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 5 ("Eliminating Toil").
- See also: `sre/01` (the 50% toil cap as org policy), `sre/06` (automation strategy for eliminating identified toil), and `devops-reliability/devops-handbook` (forthcoming) for broader flow/waste-reduction framing toil overlaps with.
