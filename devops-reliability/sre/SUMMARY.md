# Site Reliability Engineering

A comprehensive recap of *Site Reliability Engineering: How Google Runs Production
Systems* (Beyer, Jones, Petoff, Murphy), concept by concept. This subject builds
reliability as an engineering discipline: it starts with measurement and control
loops (SLIs, SLOs, error budgets), moves through day-2 operations (toil, automation,
monitoring, on-call, incidents, postmortems, capacity, releases), extends into
data-pipeline-specific reliability and failure-cascade defenses, and ends with the
cross-team and organizational-maturity questions that only appear once reliability
practice has to scale across many services and teams.

Progress note: all 16 lessons are `drafted`; none have been discussed yet, so mastery
is pending across the board and no weak spots are recorded yet. This page will gain
depth (especially on the concepts the learner finds hard) as discussions happen - the
last section below will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom: the
measurement foundation first (what SRE is, SLIs, SLOs, error budgets), then day-2
operations (toil, automation, monitoring, on-call, incidents, postmortems, capacity,
releases), then system-level failure mechanics (data pipelines, cascading failure),
then cross-team and organizational scaling.

## Measurement and control loop

- **[sre/01] What SRE is and how it differs from traditional operations** - SRE
  staffs operations with software-engineer-caliber hires, caps manual "toil" work at
  50% of an SRE's time, and replaces political dev-vs-ops tension with one objective,
  shared number: the error budget. Not a rename of sysadmin, not "DevOps done right,"
  not just more automation. ([lesson](lessons/01-what-sre-is.md))
- **[sre/02] Service level indicators (SLIs): measuring user-visible behavior** - a
  precisely defined ratio of good events to valid events, measured as close to the
  user as feasible; the foundation every downstream mechanism (SLOs, error budgets,
  alerting) inherits errors from if defined sloppily. Covers the four common SLI
  categories (availability, latency, throughput, freshness) and why latency SLIs use
  percentiles, never averages. ([lesson](lessons/02-service-level-indicators.md))
- **[sre/03] Service level objectives (SLOs): target-setting for reliability** - a
  deliberate, sub-100% target on an SLI over a defined window, chosen where the cost
  of the next "nine" starts to exceed its benefit to users. Covers user-journey vs.
  component SLOs, the multiplicative effect of dependency chains, and internal vs.
  external SLA margins. ([lesson](lessons/03-service-level-objectives.md))
- **[sre/04] Error budgets as a release-governance mechanism** - `100% - SLO` turned
  into a spendable quantity (e.g., a 99.9% SLO over 28 days = 40.32 minutes of
  allowed badness), with a pre-agreed policy for what happens at zero: releases
  freeze until the SLO recovers. The value is almost entirely in leadership actually
  honoring that policy under pressure. ([lesson](lessons/04-error-budgets.md))

## Day-2 operations

- **[sre/05] Toil: identifying, quantifying, and prioritizing elimination** - toil is
  precisely manual, repetitive, automatable, tactical, no-enduring-value work that
  scales linearly with growth - not just "work you dislike." The six-property
  checklist and growth-weighted prioritization keep automation investment
  evidence-based rather than a vague complaint response.
  ([lesson](lessons/05-toil-elimination.md))
- **[sre/06] Automation strategy for repetitive operational work** - automation is an
  investment with a real payback horizon, not an unconditional good; the five-level
  maturity ladder (manual -> ad hoc scripts -> owned software -> platform-native ->
  autonomous) separates automating mechanical execution (safer, do it early) from
  automating judgment/decisions (riskier, earn trust first).
  ([lesson](lessons/06-automation-strategy.md))
- **[sre/07] Monitoring and alerting design for actionable signals** - the four
  golden signals (latency, traffic, errors, saturation) for what to watch; multi-window,
  multi-burn-rate alerting ties paging urgency directly to error-budget consumption
  rate rather than an arbitrary static threshold, solving the fast-detection-vs-noise
  tradeoff a single threshold can't. ([lesson](lessons/07-monitoring-alerting.md))
- **[sre/08] On-call engineering: rotations, load, and sustainability** - on-call
  load is a budget like toil or error budget: a 6-8 person rotation, caps of roughly
  2 significant incidents and 25-30% active-engagement time per shift, explicit
  compensation, and a defined primary/secondary escalation path keep the practice
  sustainable rather than quietly burning people out.
  ([lesson](lessons/08-on-call-engineering.md))
- **[sre/09] Incident command and coordinated response** - separating Incident
  Commander (owns prioritization), Operations Lead (directs technical mitigation),
  and Communications Lead (owns status updates) prevents the two classic large-incident
  failure modes: conflicting parallel fixes and silently-fixed-but-unreported
  problems. Scales from a one-person incident to a fifty-person one using the same
  role structure. ([lesson](lessons/09-incident-command.md))
- **[sre/10] Postmortems and organizational learning from failure** - blameless,
  chain-of-causes (not single-root-cause) postmortems with owned, dated action items
  tracked in the normal engineering backlog are what actually convert a bad day into
  durable improvement. Blameless does not mean consequence-free at the systemic
  level. ([lesson](lessons/10-postmortems-learning.md))
- **[sre/11] Capacity planning and demand forecasting** - provisioning deliberate
  headroom for peak demand, demand growth, and correlated failure scenarios (e.g.,
  losing an availability zone), validated by real load testing rather than assumed
  per-server throughput, and checked for non-obvious bottlenecks (a downstream
  database, not just the application tier). ([lesson](lessons/11-capacity-planning.md))
- **[sre/12] Release engineering and progressive delivery safety** - canary +
  staged rollout + fast automated rollback + hermetic, reproducible builds converts
  most bad-change incidents from full-blast-radius events into small, error-budget-cheap
  ones; config changes deserve the same rigor as code deploys.
  ([lesson](lessons/12-release-engineering.md))

## System-level failure mechanics

- **[sre/13] Data processing reliability and pipeline operations** - a pipeline that
  exits successfully hasn't told you whether its output is correct; freshness,
  completeness, and correctness SLIs (ideally checked against an independent source
  of truth), idempotent processing, and replayability from retained raw input are
  what make bugs discoverable and recoverable instead of silently corrupting
  downstream data. ([lesson](lessons/13-data-processing-reliability.md))
- **[sre/14] Handling overload and cascading failure** - cascading failures are
  caused by the system's own defensive reflexes (immediate retries, thundering-herd
  recovery) concentrating load onto something already struggling; load shedding,
  circuit breakers, and backoff-with-jitter all work by making the system fail a
  little, on purpose and early, instead of completely, later and everywhere.
  ([lesson](lessons/14-overload-cascading-failure.md))

## Cross-team and organizational scaling

- **[sre/15] Multi-team reliability interfaces and support boundaries** - past a
  certain scale, reliability is an interface problem between teams: PRR-style
  criteria allocate scarce dedicated SRE capacity, error-budget impact is charged to
  whoever the user experienced the failure through while fixes are owned by whoever
  caused it, and explicit SLO/escalation contracts between dependent teams prevent
  confusion during multi-team incidents.
  ([lesson](lessons/15-multi-team-reliability-interfaces.md))
- **[sre/16] Evolving SRE practices with service maturity** - the right rigor level
  for every earlier practice in this subject (SLO tightness, on-call formality,
  release automation, dedicated SRE engagement) is a function of a service's current
  scale and criticality, not a fixed target; watch concrete signals (rising toil,
  repeated postmortem findings, outgrown on-call load, growing downstream
  dependency) for when a service has outgrown its current stage, since both
  premature over-investment and reactive under-investment are real, symmetric costs.
  ([lesson](lessons/16-sre-practice-maturity.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
