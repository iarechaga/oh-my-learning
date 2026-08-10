---
id: devops-handbook/04
subject: devops-handbook
title: Version Control for Code, Infrastructure, and Config
slug: version-control-everything
status: drafted
mastery:
seniority: mid
source: The DevOps Handbook (Kim, Humble, Debois, Willis), Part III
prerequisites: [devops-handbook/03]
created: 2026-08-10
updated: 2026-08-10
---

# Version Control for Code, Infrastructure, and Config

## TL;DR
Every artifact that determines production behavior — application code, infrastructure definitions, configuration values, database schemas, pipeline definitions — belongs in version control, not just application code; anything that can drift outside version control becomes an untracked, unrepeatable source of production incidents.

## The idea
Most engineers accept "put your code in git" as obvious. The Handbook's actual claim is broader and less obvious: production behavior is determined by far more than application code — it's also determined by which OS packages are installed, which environment variables are set, which feature flags are on, which database migration has run, which load-balancer routing rule is active, and which CI pipeline script built the artifact. If any of those live outside version control (a value someone SSH'd in and changed by hand, a config edited directly in a cloud console), you've lost the ability to know what's actually running, to reproduce it, or to roll it back — which is exactly the situation that turns a small mistake into an untraceable outage.

## How it works

### The core mechanism: version control as the single source of truth
The rule is not "use git" as ritual — it's that the version-controlled repository becomes the *only* authoritative description of desired state, and everything running in production should be derivable from it. This is what makes infrastructure as code (`devops-handbook/09`) possible at all: you can't treat infrastructure as code if the actual infrastructure can silently diverge from what's checked in.

**Worked example — the untracked config disaster.** An engineer under pressure SSHes into a production server and bumps a database connection-pool size from 20 to 100 to fix an immediate performance issue. It works. Three weeks later, that server gets replaced during a routine autoscaling event, and the replacement boots with the old config value of 20 baked into the deployment template — because the fix was never committed anywhere. The performance problem returns, and nobody remembers the earlier fix or why it mattered, because there's no commit, no PR, no history — just a fix that existed only in one running process's memory of its own state.

**The version-controlled alternative.** The same fix, made instead as a one-line change to a checked-in config file (`db_pool_size: 100` in a repo), goes through a PR, gets a reviewer who asks "why 100, why not 50?", produces a commit message and diff that documents *why* the change happened, and survives every future server replacement because new servers are built *from* that file, not from a state someone happened to leave running.

### Why this extends beyond application code
- **Infrastructure definitions** (Terraform, CloudFormation, Kubernetes manifests) — version-controlling these is what makes `devops-handbook/09` possible: you can diff, review, and roll back an infrastructure change exactly like a code change.
- **Configuration and feature flags** — even values that change frequently (a flag toggled hourly) should have their *definition* and *default* in version control, with runtime overrides logged and auditable, so you can always answer "what config was active at time T."
- **Database schema migrations** — stored as ordered, versioned migration scripts (not manual `ALTER TABLE` run once by hand) so the schema's history is reconstructable and repeatable across environments.
- **Pipeline and automation scripts** — the CI/CD pipeline definition itself (`devops-handbook/06`) is code and belongs in the same repo discipline; a pipeline edited ad hoc in a CI tool's web UI has the exact same drift problem as a server edited by hand.

### The trunk-based development connection
Version-controlling everything is a prerequisite for `devops-handbook/07`'s trunk-based development and for `devops-handbook/09`'s immutable infrastructure: you can only safely tear down and rebuild a server from scratch (immutability) if its complete desired state — packages, config, code — is captured in version control and nowhere else. Without that discipline, "immutable" infrastructure just means you've lost a snowflake server you can no longer reproduce.

### The audit and compliance side-benefit
Version control's commit history is also the compliance answer the Handbook connects to `devops-handbook/08` and `devops-handbook/15`: "who changed what, when, and why" becomes a query against git log and PR history instead of a manual change-log spreadsheet someone has to remember to update — turning an auditor's request from a scramble into a `git log` command.

## Pros
- Every production-affecting change becomes reviewable, diffable, and revertible — a rollback is "redeploy the previous commit," not "try to remember what it looked like before."
- Produces an audit trail for free, which materially reduces the manual burden of compliance and incident investigation.
- Removes the single-point-of-failure of tribal knowledge ("only Dave knows the real prod config") by making the true state a shared, queryable artifact.

## Cons
- Requires discipline and tooling investment to version-control things that are naturally mutable at runtime (feature flag states, autoscaling group sizes) without making the system rigid or the repo noisy with every runtime fluctuation.
- Secrets (API keys, passwords) must NOT go directly into version control in plaintext — this practice requires a complementary secrets-management approach (vaults, encrypted secrets, injected at deploy time) or it becomes a security liability rather than a safety net.
- Migrating a team from ad hoc, hand-edited production state to fully version-controlled state is itself a real project — it's not free to retrofit onto an existing snowflake environment.

## Alternatives
- **Configuration management databases (CMDBs) as source of truth** — an older ITSM-style approach where a separate database (not version control) records desired state; harder to diff/review changes and typically decoupled from the actual deployment mechanism, so drift between "recorded" and "actual" is common.
- **Manual runbooks / documented procedures** — describe how to configure a server in prose rather than as executable, versioned definitions; readable by humans but not machine-enforceable, and prose drifts out of sync with reality faster than code does.
- **GitOps** — a stricter, more automated version of this same idea, where a reconciliation controller continuously enforces that running infrastructure matches the version-controlled definition, closing the loop this lesson only argues for manually.

## When to use it
Apply this to any artifact whose value materially affects production behavior: application code, IaC definitions, config defaults, schema migrations, pipeline scripts, alerting rule definitions. If a change to it could cause or fix an incident, it belongs in version control.

## When NOT to use it
Don't force truly ephemeral, non-authoritative runtime state into version control just for the sake of the rule — a request-scoped cache value or a metric's current reading doesn't belong there; only the *definitions and defaults* that govern behavior do. Never commit raw secrets in plaintext — use a secrets manager and version-control only the *reference* to where a secret lives.

## Key takeaways / mental model
Ask of any production-affecting value: "if this server died right now, could I rebuild an identical replacement purely from what's checked into version control?" If the honest answer is no, something important is living only in a human's memory or a running process's undocumented state — and that's the gap this practice exists to close.

## Self-check questions
1. Explain, using the connection-pool example, why "the fix worked" is not sufficient evidence that a production change was handled safely.
2. Why is version-controlling everything a prerequisite for immutable infrastructure (`devops-handbook/09`) specifically, rather than just a nice-to-have alongside it?
3. A teammate argues "our feature flags change too often to version control — it would flood the repo with commits." How would you address the underlying concern without abandoning the version-control discipline for flag *definitions*?
4. Why must secrets be explicitly excluded from this practice's "put everything in version control" rule, and what does the correct alternative look like?

## References
- The DevOps Handbook (Kim, Humble, Debois, Willis), Part III: "The First Way: Technical Practices of Flow."
- See also: `devops-handbook/09` (infrastructure as code, immutable infrastructure) and `devops-handbook/07` (trunk-based development).
