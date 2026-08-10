# The DevOps Handbook

A comprehensive recap of *The DevOps Handbook* by Gene Kim, Jez Humble, Patrick
Debois, and John Willis, concept by concept. This subject turns the Three Ways
(dramatized narratively in `phoenix-project/05`-`07`) into a concrete implementation
program: flow mechanics first, then feedback architecture, then organizational
learning and governance.

Progress note: all 16 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded yet. This page
will gain depth (especially on the concepts the learner finds hard) as discussions
happen - the last section below will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
the implementation model first, then flow-oriented technical practices (the First
Way), then feedback practices (the Second Way), then continual-learning and
organizational practices (the Third Way plus governance and measurement).

## The implementation model

- **[devops-handbook/01] Applying the Three Ways as an implementation model** - the
  Phoenix Project's narrative Three Ways translated into an ordered, measurable
  program of technical practices; Flow before Feedback before Continual Learning,
  because each depends on the one before it being in place.
  ([lesson](lessons/01-three-ways-implementation-model.md))
- **[devops-handbook/02] Value stream mapping for software delivery** - map every
  step a change takes from commit to production, separating process time from wait
  time, to find where lead time is actually being lost (usually queueing, not work).
  ([lesson](lessons/02-value-stream-mapping.md))

## The First Way: flow (Part III)

- **[devops-handbook/03] Small batch sizes and limiting work in process** - smaller
  batches and explicit WIP limits shrink blast radius, speed diagnosis, and
  (counter-intuitively) increase real throughput by reducing multitasking cost.
  ([lesson](lessons/03-small-batches-wip-limits.md))
- **[devops-handbook/04] Version control for code, infrastructure, and config** -
  every artifact that determines production behavior belongs in version control,
  not just application code, or it becomes an untracked source of drift and
  incidents. ([lesson](lessons/04-version-control-everything.md))
- **[devops-handbook/05] Continuous integration as a quality gate** - frequent
  merges to trunk plus an automated, fast, trusted build-and-test pipeline replace
  scheduled "integration hell" with continuous, low-risk integration.
  ([lesson](lessons/05-continuous-integration.md))
- **[devops-handbook/06] Continuous delivery and deployment pipeline design** -
  extends CI all the way to "always deployable" (or, with continuous deployment,
  "always deployed"), using canary rollouts and feature flags to make frequent
  deployment safer than infrequent deployment.
  ([lesson](lessons/06-continuous-delivery-pipelines.md))
- **[devops-handbook/07] Trunk-based development and release cadence** - short-lived
  branches and daily integration avoid the compounding integration debt of
  long-lived branches; feature flags decouple deployment cadence from user-facing
  release cadence. ([lesson](lessons/07-trunk-based-release-cadence.md))
- **[devops-handbook/08] Shift-left security and compliance in delivery flow** -
  automated security and compliance checks embedded in the pipeline catch issues
  in minutes at commit time, instead of weeks later via a manual gatekeeping
  review. ([lesson](lessons/08-shift-left-security-compliance.md))
- **[devops-handbook/09] Infrastructure as code and immutable infrastructure** -
  version-controlled infrastructure definitions plus never-patch-in-place, rebuild-
  and-replace practice eliminate configuration drift as a category of problem.
  ([lesson](lessons/09-infrastructure-as-code-immutable.md))

## The Second Way: feedback (Part IV)

- **[devops-handbook/10] Telemetry foundations: logs, metrics, traces, and events**
  - the four telemetry types answer different questions (what happened, how's the
  system doing, where in the request path, what changed) and a genuinely
  observable system needs all four, correlated together.
  ([lesson](lessons/10-telemetry-foundations.md))
- **[devops-handbook/11] Production monitoring and actionable alerting** - alert on
  user-visible symptoms, not every internal fluctuation; route to whoever can act;
  treat every unnecessary page as a bug in the alert rule.
  ([lesson](lessons/11-monitoring-actionable-alerting.md))
- **[devops-handbook/12] Fast incident feedback into engineering work** - detection
  only matters if it reaches, fast, the engineer who can fix root cause; developers
  carrying their own pager and protected capacity for incident-derived fixes close
  that loop. ([lesson](lessons/12-incident-feedback-loops.md))

## The Third Way: continual learning, governance, and measurement (Part V-VI)

- **[devops-handbook/13] Blameless postmortems and systemic root cause analysis** -
  separate the proximate human trigger from the systemic conditions that let it
  cause damage; fix the system, not the individual, and protect the psychological
  safety that makes honest, fast reporting possible.
  ([lesson](lessons/13-blameless-postmortems.md))
- **[devops-handbook/14] Enabling team topologies and platform capabilities** - not
  every team should look the same: stream-aligned, platform, enabling, and
  complicated-subsystem teams each serve a distinct purpose, and platform teams
  must be run with genuine self-service, product-management discipline to actually
  reduce cognitive load. ([lesson](lessons/14-enabling-teams-platform.md))
- **[devops-handbook/15] Governance through standards and self-service controls** -
  shift governance from manual per-change approval to automated, pre-agreed
  guardrails that make the easy path the compliant path, reserving human review for
  genuinely novel or high-risk changes.
  ([lesson](lessons/15-governance-self-service-controls.md))
- **[devops-handbook/16] Measuring outcomes: delivery performance and reliability
  metrics** - deployment frequency, lead time, MTTR, and change failure rate,
  tracked together, disprove the assumed speed/stability trade-off and diagnose
  which practice from this subject to invest in next.
  ([lesson](lessons/16-delivery-reliability-metrics.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
