---
id: designing-distributed-systems/02
subject: designing-distributed-systems
title: "The Sidecar Pattern"
slug: sidecar
status: drafted
mastery:
seniority: mid
source: "Designing Distributed Systems (Brendan Burns), Chapter 2"
prerequisites: [designing-distributed-systems/01]
created: 2026-07-01
updated: 2026-07-01
---

# The Sidecar Pattern

## TL;DR
The sidecar pattern packages a main application container and a helper container together in one pod or machine so the helper can add capabilities without changing application code.
The two containers share local resources (localhost networking and volumes), so the sidecar can act very close to the app while still being independently built and versioned.

## The idea
You often need to add infrastructure behavior around an application that you do not want to rewrite.
Maybe the app is legacy.
Maybe it is owned by another team.
Maybe changing it would create risky release work across many services.

The sidecar pattern solves this by saying: keep the app container focused on business logic, and attach a second container that handles an operational concern.
Typical concerns are TLS termination, log and metrics export, and config synchronization.

The intuition is simple:
if two containers live in the same pod, they are close enough to behave like one unit from a deployment perspective, but separate enough to preserve clean ownership boundaries.
They share fate and lifecycle as one pod, yet each image can have its own source repo, build pipeline, and release cadence.

In Kubernetes terms, the pod is the scheduling unit.
Inside that pod, containers share a network namespace, which means localhost is shared.
They can also share volumes, which means one container can write files that another reads.
This creates a strong local integration point without forcing code-level coupling.

## How it works

### The pod is the unit, not the container
The sidecar pattern only makes sense when you reason at pod level.
The pod defines what starts together, restarts together, and gets placed together on a node.
That pod gives you two key sharing properties.

First, shared network namespace.
If your app listens on `:8080`, the sidecar can call `http://127.0.0.1:8080`.
No service discovery is needed between those two containers.
Localhost is enough.

Second, shared volumes.
If both containers mount the same `emptyDir` or projected config volume, one can write files that the other consumes.
That is the mechanism behind sidecars that generate certificates, materialize config, or transform log files.

The sidecar is therefore "near-process" in behavior but still a separate process boundary.
That split is the value: local integration plus independent packaging.

### Canonical use 1 - Add HTTPS/TLS to a legacy app
Assume you run `orders-api`, a legacy binary that only speaks HTTP on port 8080.
You cannot safely change it this quarter.
You still need encrypted inbound traffic.

A sidecar proxy container (for example nginx or Envoy) can listen on 443, terminate TLS, and forward plain HTTP to `localhost:8080`.
The app remains untouched.
Certificates, ciphers, and rotation policy live in sidecar config.

This is powerful because security hardening can now move on security timelines, not on application rewrite timelines.
If policy changes from TLS 1.2 to TLS 1.3 only, you usually update the sidecar image and config, not the app image.

### Canonical use 2 - Log and metrics collection
Many application teams do not want to embed every vendor SDK for logging and metrics.
Doing so tightly couples app code to observability plumbing.
A sidecar can decouple that concern.

Example:
`payments-app` writes JSON logs to `/var/log/app/app.log`.
A sidecar tails that file, enriches lines with pod metadata, batches records, and ships to a central backend.
Another sidecar (or the same one, depending on scope) scrapes local metrics and forwards them.

The app keeps emitting simple logs and metrics.
Routing, retry, backoff, buffering, and protocol translation are delegated.

### Canonical use 3 - Dynamic config reloading
Some systems need config updates without restarting the main app.
The app reads `/etc/config/app.conf` from a shared volume.
A config sidecar watches a remote source (Git, S3, config service, or secret store), validates updates, then writes new config atomically.

The app either watches file changes itself or receives a local signal through a small control endpoint.
This gives near-real-time config updates while avoiding direct remote dependency from app code.

This pattern is common when you want stronger guardrails.
The sidecar can reject malformed config before the main process sees it.
That keeps bad config from crashing production traffic paths.

### Parameterized, reusable sidecars
A good sidecar is generic and parameterized, not app-specific.
You package one sidecar image and reuse it across many workloads.
Differences are injected through environment variables, mounted files, and startup arguments.

For example, a reusable TLS sidecar might accept:
- `UPSTREAM_HOST=127.0.0.1`
- `UPSTREAM_PORT=8080`
- `TLS_CERT_PATH=/etc/tls/tls.crt`
- `TLS_KEY_PATH=/etc/tls/tls.key`
- `TLS_MIN_VERSION=1.2`

Now the same sidecar image can front dozens of services by changing only config values.
That reuse is why sidecars scale organizationally.
Platform teams maintain one hardened implementation.
Application teams consume it as a standard building block.

### Deployment and upgrade independence in practice
Main and sidecar share pod lifecycle, but they do not need shared build lifecycle.
You can build sidecar image `platform/tls-proxy:v1.7.2` in a different repository from app image `orders-api:v3.14.0`.

At deployment time, one pod spec references both image tags.
If a CVE appears in the TLS library, you bump sidecar tag to `v1.7.3` and roll workload pods.
The app binary hash can remain identical.

That is what "independent upgrade" means here:
independent image and release ownership, with coordinated pod rollout at deploy time.
The runtime unit is shared, but the engineering ownership boundaries stay separate.

### Worked example 1 - Pod shape and local resource sharing
Assume a Kubernetes pod named `orders-pod` with two containers:
- `orders-app` on `:8080`
- `tls-sidecar` on `:443`

Both mount a shared volume `shared-config` at `/etc/shared`.
The sidecar has cert files and forwards to the app over localhost.

```text
+--------------------------------------------------------------+
| Pod: orders-pod                                              |
|   Shared network namespace (localhost)                       |
|   Shared volume: /etc/shared (emptyDir or projected volume)  |
|                                                              |
|   +----------------------+      localhost      +-----------+ |
|   | tls-sidecar          |  https :443         | orders-app| |
|   | nginx/envoy          | ------------------->| http :8080| |
|   | certs at /etc/shared |<--------------------|           | |
|   +----------------------+                     +-----------+ |
|                                                              |
+--------------------------------------------------------------+
```

Client traffic enters on 443.
The sidecar terminates TLS, then proxies clear HTTP to app on localhost.
No external service hop exists between sidecar and app.
That keeps latency low and avoids extra network policy complexity.

### Worked example 2 - Step-by-step trace of dynamic config reload
Scenario:
`catalog-app` reads `/etc/config/app.conf` every 10 seconds.
`config-sidecar` watches a remote config document every 30 seconds.
Both share an `emptyDir` mounted at `/etc/config`.

1. At `10:00:00`, sidecar fetches config version `42` from the central config API.
2. Sidecar validates schema and business constraints (for example, timeout range 50-2000 ms).
3. Sidecar writes `/etc/config/app.conf.tmp` with the new content.
4. Sidecar performs atomic rename from `.tmp` to `/etc/config/app.conf`.
5. App polling loop sees file mtime changed at next check (`10:00:10`).
6. App reloads in-memory settings without process restart.
7. If sidecar cannot validate version `43`, it keeps last good file and emits an error metric.

Important detail:
the sidecar becomes the policy gate.
It prevents bad config from reaching the app.
Without this, every app would need duplicate validation and rollback logic.

### Worked example 3 - Independent sidecar upgrade with zero app code change
Scenario:
`invoice-app` image is pinned at `registry/acme/invoice-app:2.4.1`.
Sidecar image is `registry/platform/tls-proxy:1.9.0`.
Security team discovers OpenSSL CVE affecting `1.9.0`.

Upgrade sequence:
1. Platform team publishes `tls-proxy:1.9.1` with patched OpenSSL.
2. Deployment manifest changes one field: sidecar image tag from `1.9.0` to `1.9.1`.
3. Rolling update replaces pods gradually (for example maxUnavailable=1, maxSurge=1).
4. New pods run `invoice-app:2.4.1` unchanged with `tls-proxy:1.9.1`.
5. Health checks verify proxy and app endpoints.
6. Rollout completes with no app rebuild, no app code diff, no app retest matrix expansion beyond interface contract.

This is the operational payoff.
You can patch infrastructure concerns quickly without waiting for business release windows.

### Practical design rules for sidecars
A sidecar works best when responsibilities are narrow.
Do one concern well.
Do not pile unrelated platform logic into one giant helper container.

Prefer explicit contracts between app and sidecar:
- fixed localhost ports
- documented file paths
- explicit startup ordering assumptions
- health probes for both containers

Treat sidecar failure modes as first-class:
if sidecar crashes, can app keep serving?
Should pod restart?
Should traffic fail closed (secure but unavailable) or fail open (available but less safe)?
Your choice depends on the concern.
TLS sidecars usually fail closed.
Non-critical log shipping sidecars might fail open with bounded local buffering.

Finally, remember that sidecar pattern is a single-node composition pattern.
It optimizes local augmentation of one workload instance.
It is not a generic replacement for system-wide services.

## Pros
- **No app modification required** - Add infrastructure capabilities to legacy or third-party apps without touching their code.
- **Strong separation of concerns** - Business logic stays in app container; operational concerns live in dedicated helper containers.
- **Reusable platform components** - One parameterized sidecar image can be shared across many workloads.
- **Independent release ownership** - Platform teams can patch and evolve sidecars on their cadence while app teams keep stable app versions.
- **Low-latency integration** - Shared localhost and shared volumes provide close coupling where needed without source-code coupling.
- **Incremental modernization path** - You can improve security and operability first, then refactor app internals later.

## Cons
- More moving parts per pod increase operational complexity, debugging surface, and resource overhead.
- App and sidecar can create hidden coupling through undocumented ports, file formats, or timing assumptions.
- Sidecar failures can take down the whole pod if lifecycle and probes are configured poorly.
- Resource limits are harder to tune because multiple containers compete for CPU and memory on one node.
- Security posture must include inter-container trust boundaries, not just external traffic.
- Too many sidecars per pod can become a "micro-monolith pod" that is hard to reason about.

## Alternatives
- **Bake capability into the app** - Simplest runtime topology (one container), but couples infrastructure logic to business code and release cycle.
- **Shared library inside the app** - Reuses code in-process, but ties you to language/runtime and still requires app rebuilds for infra changes.
- **Separate remote service** - Centralizes concern across many apps, but adds network hop, service discovery, and independent availability dependency.
- **Node-level agent (DaemonSet)** - One helper per node can reduce per-pod overhead, but has weaker per-workload isolation and less app-specific customization.

## When to use it
Use sidecars when you need to augment each workload instance with a local capability that should evolve separately from app code.
Typical signs are legacy apps, platform standardization goals, and repeated cross-cutting needs like TLS handling, config materialization, or telemetry shipping.

Use it when locality matters.
If the helper must talk to the app over localhost or share files with minimal latency and no cross-network dependency, sidecar is usually the cleanest choice.

Use it when team boundaries justify it.
If a platform or security team owns the helper behavior while product teams own business logic, sidecar preserves ownership without forcing one team into another's codebase.

## When NOT to use it
Do not use a sidecar when the capability is purely internal business logic that belongs inside the app itself.
Adding a sidecar there only increases complexity.

Do not use it when one centralized remote service is clearly better.
If the concern has no need for pod-local communication and benefits from global aggregation, a remote service may be simpler to operate.

Do not use sidecars as a dumping ground for unrelated concerns.
If you are adding many loosely related sidecars just to avoid touching app code, you are likely masking architecture debt.

Avoid it for extremely resource-constrained environments where each extra container meaningfully harms density.
In those cases a node agent or in-app integration may be more efficient.

## Key takeaways / mental model
Think of a sidecar as a "plug-in backpack" strapped to one app instance.
The app walks, the backpack walks with it.
The backpack can carry TLS, config sync, or telemetry gear, but it should not become a second app.

Rules of thumb:
keep sidecars narrow in scope, prefer explicit local contracts (ports and files), and version sidecars as reusable platform products.
If the concern must be local to each app instance and independently upgradable, sidecar is a strong fit.
If the concern is global, stateless, and equally useful as a shared endpoint, prefer a remote service.

## Self-check questions
1. You own a legacy service that only exposes HTTP on `:8080`, but compliance now requires TLS 1.3. How would you apply a sidecar, and what exact contracts between app and sidecar would you define to keep ownership clean?
2. Your team wants to move log shipping from app code to a sidecar. What failure policy (fail open vs fail closed) would you choose, and how would that choice change probes, buffering, and alerting?
3. A config sidecar writes `/etc/config/app.conf` from a remote source. Describe the safest write-and-reload sequence that avoids partial-file reads and bad-config rollouts.
4. Platform team patched `tls-sidecar` for a CVE. Explain how you would roll out the sidecar upgrade while proving the app binary and behavior stayed unchanged.
5. You notice a pod now has four sidecars for unrelated concerns and frequent restart storms. Which signals indicate the sidecar pattern is being misused, and what redesign options would you evaluate first?
6. For a new capability request, how would you decide between sidecar, shared library, remote service, and node-level agent, given constraints on latency, ownership, language diversity, and operational cost?

## References
- Designing Distributed Systems (Brendan Burns), Chapter 2: "The Sidecar Pattern"
- [designing-distributed-systems/01 - Why Distributed Patterns](01-why-distributed-patterns.md)
- [system-design/15 - Observability: logging, metrics, tracing](../../system-design/lessons/15-observability.md)
