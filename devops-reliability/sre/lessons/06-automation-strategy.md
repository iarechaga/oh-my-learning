---
id: sre/06
subject: sre
title: Automation Strategy for Repetitive Operational Work
slug: automation-strategy
status: drafted
mastery:
seniority: senior
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 7
prerequisites: [sre/05]
created: 2026-08-10
updated: 2026-08-10
---

# Automation Strategy for Repetitive Operational Work

## TL;DR
Automation is how identified toil (`sre/05`) actually gets eliminated, but the book is explicit that automation is a means, not an end — badly designed automation can encode a bad process at scale, or become its own maintenance burden that outweighs the toil it removed. The book's framing of automation as a maturity progression (from purely manual, through automation of the mundane parts, up to autonomous systems) gives a strategy for deciding what to automate and in what order.

## The idea
"Just automate it" is easy advice and frequently wrong advice if applied without judgment. Automation has a real cost: it must be built, tested, documented, and — critically — *maintained* as the underlying system evolves. A brittle automation script that breaks silently every time the service's config format changes can be worse than the manual process it replaced, because now someone has to debug the automation *and* still do the task manually when it fails, with less institutional knowledge of how to do it by hand since the automation has atrophied that skill.

Google's framing, drawn from its own internal evolution, is that automation should be pursued deliberately and incrementally, targeting the specific toil identified as highest-value to eliminate (per `sre/05`'s prioritization), rather than automating everything indiscriminately or, at the other extreme, resisting automation because "it's faster to just do it by hand this once."

## How it works

### The maturity ladder: from manual to autonomous
The book describes automation maturity roughly as a progression:
1. **No automation** — a human performs every step by hand, every time.
2. **Externally maintained automation (ad hoc scripts)** — a human writes a script to help with a task, but the script is one-off, undocumented, and not owned or tested as real software; it lives on someone's laptop or a shared bastion host.
3. **Internally maintained, "productionized" automation** — the automation is treated as real software: version-controlled, tested, code-reviewed, owned by the team, with clear inputs/outputs and failure handling. This is the level the book pushes teams toward for anything beyond trivial, rarely-run tasks.
4. **Externally provided, generic automation/systems** — the task is eliminated entirely because the underlying platform now handles it natively (e.g., a cluster orchestrator handles failover so no team-specific failover script is needed at all).
5. **Autonomous systems** — the system observes its own state and takes corrective action without human initiation each time (e.g., autoscaling reacting to load, automatic canary rollback on SLO regression).

**Worked example — the same task moving up the ladder.** Consider "restart a stuck worker process when its health check fails":
- Level 1: an on-call engineer notices the alert, SSHes in, and restarts the process by hand.
- Level 2: someone writes a `restart_worker.sh` script that does the SSH + restart, shared informally, but nobody owns it, it's not tested, and it silently breaks when the process's name changes in a later release.
- Level 3: the team builds and owns a proper restart tool, code-reviewed, with logging, alerting on repeated failures (so it doesn't mask a real underlying bug by endlessly restarting), and a runbook.
- Level 4: the team migrates workers onto an orchestrator (e.g., a container scheduler) that natively restarts failed health checks — the team-specific tool becomes unnecessary.
- Level 5: the orchestrator additionally detects a *pattern* of repeated restarts on one host and automatically drains and replaces that host without a human being paged at all.

Each step reduces toil further, but also raises the stakes of a bug in the automation itself — a level-5 autonomous system that misfires can take much broader action, much faster, than a human ever would, which is exactly why the book insists on treating automation as real software (testing, review, monitoring its own behavior) as it climbs this ladder.

### Automate the decision, not just the action — carefully
A key distinction: automating the mechanical steps of a task ("run these three commands") is safer and easier to get right than automating the *decision* of when to take action ("should we fail over now?"). The book's guidance is to automate mechanical execution readily, but to be far more cautious automating judgment calls, especially ones with a high blast radius, until the decision logic has been proven reliable through extensive human-in-the-loop use.

**Worked example.** A database failover: automating "execute a failover once triggered" (promote the replica, update DNS, drain connections from the old primary) is a good level-3 automation candidate — the mechanical steps are well-understood and repeatable. Automating "decide autonomously whether the primary has actually failed vs. is just slow" is much riskier — a false-positive failover triggered by a network blip can cause a worse outage than the blip itself (a classic cascading-failure trigger, see `sre/14`). Google's real systems often automate the *execution* long before they trust automation with the *detection/decision* step, and even then usually keep a human-approval gate on the highest-blast-radius decisions.

### Designing automation to fail safely
Automation should be built assuming it will eventually encounter a situation its author didn't anticipate. Good automation: fails loudly (alerts rather than silently retrying forever), has a circuit breaker that stops after N consecutive failures rather than repeating a damaging action indefinitely, and leaves an audit trail so a human can reconstruct what it did. **Worked example.** An auto-remediation script that restarts a crashing service is given a cap: "if this has already restarted the same process 3 times in 10 minutes, stop and page a human instead of restarting a 4th time" — without this cap, the automation would happily crash-loop-restart forever, masking a real bug (e.g., a bad deploy) that actually needs a human to roll back, and potentially making things worse (e.g., repeated restarts causing a thundering-herd reconnection storm from clients, see `sre/14`).

### Cost-benefit before building
Before automating, the book recommends estimating: engineering hours to build and maintain the automation vs. toil-hours saved over a realistic horizon, informed by the growth-trend prioritization from `sre/05`. **Worked example.** Automating the quota-provisioning toil from `sre/05` (20 hours/month, growing 15%/quarter) might cost an estimated 80 engineering hours to build a self-service tool properly (with validation, auth, and audit logging). Payback: at 20 hours/month saved, that's a 4-month payback even before accounting for growth — a strong case to build it. Contrast with automating a task costing 2 hours/month with no growth trend, where the same 80-hour build cost would take over 3 years to pay back — very likely not worth it; the manual process is cheaper as long as it stays small.

## Pros
- Directly reduces toil (`sre/05`) at scale, letting operational capacity keep pace with service growth instead of scaling linearly with it.
- Encoding a process as tested, reviewed software makes it more consistent and less error-prone than ad hoc human execution, especially under incident stress.
- Frees engineering time for higher-leverage work, compounding: each automation investment can pay for the next.

## Cons
- Automation is itself software that must be maintained; poorly maintained automation can silently rot and fail exactly when needed most (during an incident, under unusual conditions).
- Automating a decision (not just an action) before it's well-understood risks large-blast-radius mistakes executed faster and more confidently than a cautious human would make them.
- Upfront engineering cost competes directly with other roadmap priorities and doesn't always pay back — automating low-volume or shrinking toil is often a net loss.

## Alternatives
- **Runbooks / documented manual procedures** — codifies the *knowledge* of how to do a task without automating the execution; lower upfront cost, keeps a human in the loop for judgment, but doesn't reduce the time cost of repetitive execution the way automation does. A reasonable intermediate step (level 2-ish) before investing in full automation.
- **Fully autonomous self-healing systems** — the far end of the maturity ladder (level 5); powerful at scale but requires very high confidence in the decision logic and strong safeguards (circuit breakers, audit trails) before it's safe to trust with high-blast-radius actions.
- **Outsourcing the task to a managed platform/vendor** — similar to level 4 on the ladder; can eliminate the toil entirely by changing who's responsible for it, at the cost of losing direct control and sometimes at real financial cost.

## When to use it
Prioritize automation for toil identified via `sre/05`'s framework as high-cost and growing, and climb the maturity ladder deliberately: mechanical actions first, judgment/decision automation only once the underlying logic is well-proven. Always design automation with explicit failure limits (circuit breakers, alerting on repeated failures) rather than assuming it will always work as intended.

## When NOT to use it
Don't automate low-volume, non-growing, or one-off tasks where the engineering cost to build and maintain automation exceeds any realistic payback. Don't automate a high-blast-radius *decision* (not just an action) before it's been reliably exercised with a human in the loop — premature decision-automation is a common source of severe, fast-moving incidents (see `sre/14`'s cascading-failure mechanics for what happens when automated reactions to a problem make it worse).

## Key takeaways / mental model
Automation is an investment with a real cost and a real payback horizon — evaluate it like one, using the toil data from `sre/05`. Climb the maturity ladder in order: automate mechanical execution before automating judgment, and never ship automation without a way for it to fail safely and loudly rather than silently or catastrophically.

## Self-check questions
1. Explain why the book treats automating a *decision* (e.g., "should we fail over?") as materially riskier than automating an *action* (e.g., "execute this failover once triggered"), and give an example of how automating the decision prematurely could backfire.
2. A team wants to automate a task costing 3 hours/month with a flat (non-growing) trend, estimated at 60 engineering hours to build properly. Using the cost-benefit approach from this lesson, would you recommend building it? What additional information would change your answer?
3. Design a safety mechanism (in plain terms, not code) for an auto-remediation script that restarts a crashing service, such that it cannot mask a real underlying bug by restarting forever.
4. Where on the five-level automation maturity ladder would you place a Kubernetes Horizontal Pod Autoscaler reacting to CPU load, and why does that placement matter for how much you'd trust it to run unsupervised?

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 7 ("The Evolution of Automation at Google").
- See also: `sre/05` (toil identification and prioritization, which feeds automation targeting) and `sre/14` (cascading failures, for what happens when automated reactions amplify rather than dampen a problem).
