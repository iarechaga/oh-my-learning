---
id: devops-handbook/09
subject: devops-handbook
title: Infrastructure as Code and Immutable Infrastructure
slug: infrastructure-as-code-immutable
status: drafted
mastery:
seniority: senior
source: The DevOps Handbook (Kim, Humble, Debois, Willis), Part III
prerequisites: [devops-handbook/04]
created: 2026-08-10
updated: 2026-08-10
---

# Infrastructure as Code and Immutable Infrastructure

## TL;DR
Infrastructure as code (IaC) means defining servers, networks, and environments in version-controlled, machine-readable definitions instead of configuring them by hand; immutable infrastructure takes this further by never patching a running server in place — instead building a new one from the updated definition and replacing the old one — eliminating configuration drift as a category of problem entirely.

## The idea
Manually configured servers accumulate what practitioners call "snowflakes": each one is subtly different because of small, undocumented hand-applied changes made under time pressure over months or years — a package upgraded here, a config tweaked there, a one-off fix applied to just this one box during an incident. No two snowflakes are quite alike, nobody has a complete record of what makes any particular one different, and reproducing one (for disaster recovery, for scaling, for debugging) becomes guesswork. IaC's fix is to make the server's *definition*, not the server itself, the authoritative artifact — and immutable infrastructure takes the logical next step: if the definition is authoritative, a running server that no longer matches it isn't a server to "fix," it's a server to *replace* with a fresh one built correctly from the definition.

## How it works

### Infrastructure as code: the mechanism
Instead of an engineer SSHing into a server and running commands, infrastructure is described declaratively in a file, checked into version control (per `devops-handbook/04`), and applied by a tool that reconciles actual state with the declared state.

**Worked example — a Terraform-style definition in prose.**
```
resource "web_server" "app" {
  count           = 4
  instance_type   = "medium"
  image           = "app-image:v1.8.2"
  security_group  = "web-sg"
  min_healthy     = 3
}

resource "database" "primary" {
  engine          = "postgres-14"
  storage_gb      = 200
  backup_schedule = "daily-02:00-UTC"
}
```
This file is the single source of truth for "what our infrastructure should look like." Scaling from 4 to 6 web servers is a one-line diff (`count = 6`), reviewed in a PR exactly like an application code change, applied by re-running the tool — not a manual click-through in a cloud console that no one records. Anyone can read the file and know exactly what's running, without needing to log into the actual environment.

### Immutable infrastructure: the mechanism
Immutability changes *how* a change like "upgrade the app to v1.8.3" gets applied. The mutable approach would SSH into each of the 4 running servers and upgrade the package in place — fast, but now that server's actual state depends on the order and success of that manual operation, and if it partially fails, you have two servers on v1.8.2 and two on v1.8.3 with no easy way to know which is which. The immutable approach changes the image version in the definition (`image = "app-image:v1.8.3"`), builds 4 brand-new servers from that updated image, health-checks them, routes traffic to the new ones, and terminates the old ones — the old servers are never touched, only replaced.

**Worked example — diagnosing a drift problem the immutable way avoids.** A team using mutable servers notices one server in a fleet of 6 behaving oddly — slightly higher error rate, slightly different response times. Investigation eventually reveals that server was manually patched during an incident 8 months ago and never got a subsequent routine update that the other 5 did receive, because the patch script assumed a clean starting state that this server no longer had. Diagnosing this took two days. Under immutable infrastructure, this specific failure mode cannot occur: every server currently running was built from the same definition at the same image version — if the definition specifies `v1.8.3`, every server is genuinely, verifiably `v1.8.3`, because none of them were ever individually patched.

### The prerequisite this practice has on version control and CI/CD
Immutable infrastructure only works because of `devops-handbook/04` (the definition is the single source of truth) and connects directly into `devops-handbook/06`'s deployment pipeline (rebuilding and replacing servers becomes just another pipeline stage, canaried and health-checked the same way an application deploy is). Without disciplined version control, "immutable" infrastructure just means you've lost a server you can no longer reproduce when it eventually needs replacing.

### Handling state: the hard part of immutability
The obvious objection: databases hold state, and you can't just "throw away and rebuild" a stateful server the way you can a stateless web server. The Handbook's practical answer is to separate the fleet into stateless components (web/app servers — fully immutable, rebuilt freely) and stateful components (databases, message queues — managed with a different discipline: replication, backups, and carefully orchestrated migrations rather than naive replace-in-place), and to push as much state as possible out of individual servers and into managed, purpose-built stateful services, precisely so that the majority of the fleet *can* be treated as disposable and immutable.

## Pros
- Eliminates configuration drift and snowflake servers as a category of problem — every running instance is verifiably identical because none were individually hand-modified.
- Makes infrastructure changes reviewable, diffable, and revertible exactly like application code changes, via the same PR and pipeline discipline.
- Disaster recovery becomes dramatically simpler: rebuilding an entire environment from scratch is a tested, routine pipeline operation, not a stressful, error-prone manual reconstruction under incident pressure.

## Cons
- Requires real tooling investment (IaC tooling, image-building pipelines, orchestration for zero-downtime replacement) that's non-trivial to set up well.
- Stateful components genuinely can't be treated the same way as stateless ones — teams that try to naively apply "just replace it" to a database learn this the hard way, usually via data loss.
- Rebuild-and-replace, even when automated, has a real time and resource cost per change (spinning up new instances, health-checking, draining old ones) compared to an in-place patch — a cost worth paying for the safety it buys, but not literally free.

## Alternatives
- **Configuration management tools applied to long-lived (mutable) servers** (Ansible/Chef/Puppet run repeatedly against existing servers) — a middle-ground practice: infrastructure is still defined as code and applied by tooling, but existing servers are patched in place rather than replaced, retaining some drift risk but requiring less rebuild infrastructure than full immutability.
- **Manual runbook-based server configuration** — the traditional alternative this practice replaces entirely; retained today mostly for legacy environments where full IaC migration hasn't yet happened.
- **Serverless / fully managed platforms** — sidesteps server-level immutability concerns entirely by removing the concept of a "server you manage" altogether; trades operational control for reduced infrastructure surface area to reason about.

## When to use it
Use IaC as a baseline practice for essentially any infrastructure footprint beyond a single trivial environment. Push toward full immutability for stateless components (web/app tiers) especially in environments with meaningful scale or compliance requirements around configuration integrity.

## When NOT to use it
Don't force naive "replace in place" immutability onto genuinely stateful components (databases, anything holding data that can't simply be rebuilt from a definition) without a proper stateful-service management discipline (replication, backups, tested migrations) underneath — that's how immutability turns into a data-loss incident rather than a safety improvement.

## Key takeaways / mental model
Ask of any running server: "if I don't know exactly why it's slightly different from its siblings, could I even find out?" Under a mutable model, often not. Under immutable infrastructure, the question doesn't arise, because "slightly different from its siblings without a corresponding definition change" isn't a state the system can get into.

## Self-check questions
1. Using the 8-month-old manually-patched server example, explain specifically why immutable infrastructure makes that failure mode structurally impossible, not just less likely.
2. Why is disciplined version control (`devops-handbook/04`) a hard prerequisite for immutable infrastructure, rather than just a nice complementary practice?
3. A junior engineer proposes applying full immutability (replace, don't patch) to the team's primary production database the same way they do for web servers. What's wrong with that plan, and what should they do instead?
4. How does immutable infrastructure change what a disaster-recovery drill looks like, compared to a mutable-server environment?

## References
- The DevOps Handbook (Kim, Humble, Debois, Willis), Part III: "The First Way: Technical Practices of Flow."
- See also: `devops-handbook/04` (version control everything, the prerequisite for treating definitions as authoritative) and `devops-handbook/06` (deployment pipeline design, where rebuild-and-replace becomes a pipeline stage).
