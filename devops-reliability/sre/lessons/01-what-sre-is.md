---
id: sre/01
subject: sre
title: What SRE Is and How It Differs from Traditional Operations
slug: what-sre-is
status: drafted
mastery:
seniority: mid
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 1-2
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# What SRE Is and How It Differs from Traditional Operations

## TL;DR
Site Reliability Engineering (SRE) is what happens when you ask software engineers to run production: instead of a separate ops team hand-managing servers, SREs treat operations as a software problem, applying engineering rigor, automation, and measurable targets to keep systems reliable. The defining move is replacing subjective "keep it up" pressure with an objective, shared number — the error budget — that both product and reliability goals answer to.

## The idea
Before SRE, most companies split "build" and "run" into two organizations with opposed incentives. Product/development teams were rewarded for shipping features fast. Operations teams were rewarded for nothing breaking. Because every change is a source of risk, these incentives point in opposite directions: dev wants velocity, ops wants a change freeze. The two teams end up in a permanent tug-of-war, usually resolved by whichever team has more organizational power that quarter, not by any principled tradeoff.

Google's answer, formalized by Ben Treynor Sloss around 2003 and documented in this book, was to stop treating "keep production reliable" as a separate discipline from "write good software," and instead staff operations with software engineers who are given an operations mandate. The SRE team writes code to eliminate the repetitive work operations teams traditionally did by hand (deployments, failovers, capacity changes), and it uses one explicit, quantitative artifact — the error budget (`sre/04`) — to arbitrate the dev-velocity-vs-stability tension instead of leaving it to politics.

The core intuition: **reliability is a feature with a cost, not an absolute virtue.** A system that is more reliable than its users need is wasting engineering effort that could have gone into features; a system that is less reliable than its users need is actively losing them. SRE's job is to find and hold that target deliberately, not to maximize uptime unconditionally.

## How it works

### The org-design move: cap ops work, mandate engineering
Google enforces this philosophy with a concrete policy: SRE teams cap the time spent on manual, operational ("ops") work — collectively called toil (`sre/05`) — at **50% of an SRE's time**, with the rest reserved for engineering work that reduces future ops load (automation, tooling, architecture improvements). If a team's toil load exceeds that cap, excess operational work is expected to flow back to the product development team that owns the service, and management is expected to reallocate people or change practices. This 50% cap is a forcing function: it makes "operations load is growing unsustainably" visible as a resourcing problem instead of letting it silently swallow the team.

### The staffing move: hire engineers, not administrators
SREs are hired to the same bar as the company's software engineers (the book states roughly 50-60% of Google's SRE hires are engineers who could also work on product teams, with the rest coming from systems-engineering backgrounds with unusually strong software skills). This matters mechanically: a team of engineers looks at a repetitive manual task and defaults to automating it, because writing code is their comparative advantage, whereas a team of administrators defaults to executing the task well by hand. The skill mix determines the team's instinctive response to growing operational load.

### The five defining practices
The book operationalizes "treat ops as a software problem" into five concrete SRE behaviors, each of which becomes its own lesson in this subject:
1. **Careful, quantitative target-setting** — define what "reliable enough" means numerically, via SLIs (`sre/02`) and SLOs (`sre/03`), instead of an implicit "never go down."
2. **A shared risk currency** — the error budget (`sre/04`) converts the SLO into a spendable quantity that governs release pace for both dev and SRE.
3. **Toil elimination as a first-class goal** — headcount doesn't scale linearly with traffic if repetitive work is automated away (`sre/05`, `sre/06`).
4. **Monitoring built for action, not noise** — alerts fire only on symptoms a human must act on now (`sre/07`).
5. **Blameless postmortems as the primary learning loop** — failures are treated as inputs to system improvement, not occasions for blame (`sre/10`).

### Worked example: the same incident, two org models
Imagine a checkout service that has an outage costing $40,000 in lost orders over 20 minutes. In a traditional ops model, the postmortem (if one happens at all) often ends at "the on-call engineer should have caught this sooner" — a conclusion that changes nothing structural. Under the SRE model, the same incident produces: an SLO breach recorded against the service's error budget (concrete, numeric); a blameless postmortem (`sre/10`) that surfaces the missing alert or the untested rollback path as the *root cause*; and a follow-up engineering ticket to fix that gap, prioritized against feature work using the same backlog and the same team. The org structure — one team, one set of incentives, one budget — is what turns "who's to blame" into "what do we build next."

### What SRE is not
It's worth being precise about the boundary, because "SRE" is often used loosely:
- **Not a rename of sysadmin.** A sysadmin team optimizes for keeping today's system running; an SRE team optimizes for making the system need less manual keeping-running over time, and is judged on both reliability *and* the engineering investment that reduces future toil.
- **Not "DevOps done right."** DevOps (see `devops-reliability/devops-handbook`) is a cultural movement describing goals — breaking down dev/ops silos, fast feedback, continual learning — that many organizations pursue. SRE is one concrete, opinionated implementation of those goals, with specific mechanisms (error budgets, the 50% toil cap, blameless postmortems). You can do DevOps without SRE's specific mechanisms; SRE is Google's answer to the same underlying problem DevOps names.
- **Not just "more automation."** Automation (`sre/06`) is a tool SRE uses, not the definition of SRE. A team that automates deployments but has no SLOs, no error budget, and blame-driven postmortems is not practicing SRE as this book defines it.

## Pros
- Replaces political tug-of-war over release pace with one objective, shared number (the error budget), reducing friction between product and reliability goals.
- Aligns incentives: the same team benefits from both shipping and reliability, so neither is externalized onto "someone else's problem."
- Scales operations headcount sub-linearly with traffic growth, because toil elimination is a mandated, resourced goal rather than an aspiration.

## Cons
- Requires organizational buy-in most companies don't have on day one: it needs engineering-caliber hires in an "ops" role, and leadership willing to let an error budget actually stop releases.
- The 50% toil cap and engineer-staffing model are expensive — they assume a company can afford to pay software-engineer salaries for what looks like an operations function.
- Doesn't work well bolted onto an org that keeps dev and ops as separately measured, separately incentivized teams; the model depends on shared ownership, not just a renamed job title.

## Alternatives
- **Traditional operations/sysadmin team** — a dedicated ops org focused on keeping systems running, typically without an engineering mandate to reduce its own future workload; simpler to staff, but toil grows roughly linearly with system complexity and traffic.
- **DevOps (cultural movement, no specific mechanism)** — pursues the same dev/ops-silo-breaking goals as SRE but leaves the *how* open; a team can adopt DevOps practices (CI/CD, shared on-call) without SRE's specific error-budget mechanism. See `devops-reliability/devops-handbook`.
- **Full "you build it, you run it" with no dedicated reliability function** — product engineers carry their own pagers with no separate SRE org at all; works at small scale, but without SLOs/error budgets as an explicit governance layer, reliability work tends to lose every prioritization fight against features.

## When to use it
Adopt the SRE model when a service is large or critical enough that reliability failures have real business cost, and when the organization can commit to the two hard parts: staffing operations with engineers, and actually letting an error budget slow down releases when it's exhausted. It pays off fastest in systems with enough scale that toil would otherwise grow without bound.

## When NOT to use it
Don't adopt the full model for a small team or an early-stage product where iteration speed matters more than formal reliability targets, or where you can't credibly staff an engineering-caliber operations function — the overhead of SLOs, error budgets, and dedicated postmortem process can outweigh the benefit before the system or the org is big enough to need it. A lighter-weight DevOps-style approach (shared on-call, good monitoring, no formal error budget) is often the right precursor.

## Key takeaways / mental model
SRE = "operations, run by engineers, governed by a number." The number (the error budget, derived from an SLO) is what turns the dev-vs-ops tension from a political fight into a shared, objective constraint both teams optimize against together. Everything else in this subject — toil, automation, monitoring, on-call, postmortems — is a mechanism that either produces that number or acts on it.

## Self-check questions
1. A traditional ops team and an SRE team both experience a bad outage. Describe one structural difference in what happens next (not just "who gets blamed") that follows directly from the SRE org model.
2. Why does Google specifically staff SRE with software-engineer-caliber hires rather than experienced system administrators? What would go wrong with the model if the team lacked that skill mix?
3. Is a company that has fast CI/CD, shared on-call, and blameless postmortems, but no SLOs or error budget, "doing SRE" by this lesson's definition? Justify your answer.
4. Give a concrete example of a small startup where adopting full SRE (formal SLOs, 50% toil cap, dedicated error-budget governance) would likely be a net loss, and explain what lighter-weight practice you'd recommend instead.

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 1 ("Introduction") and Chapter 2 ("The Production Environment at Google, from the Viewpoint of an SRE").
- See also: `devops-reliability/devops-handbook` for the broader cultural DevOps movement SRE is one implementation of, and `devops-reliability/seeking-sre` (forthcoming) for how SRE practice evolves once adopted across an organization.
