---
id: designing-distributed-systems/04
subject: designing-distributed-systems
title: "The Adapter Pattern"
slug: adapter
status: drafted
mastery:
seniority: mid
source: "Designing Distributed Systems (Brendan Burns), Chapter 4"
prerequisites: [designing-distributed-systems/02]
created: 2026-07-01
updated: 2026-07-01
---

# The Adapter Pattern

## TL;DR
The adapter pattern is a single-node pattern where you run a helper container next to an application container, and that helper converts whatever odd, app-specific interface the app exposes into one standard interface the platform expects. The app can keep speaking its native format; the adapter translates it at the edge. This lets the rest of the system treat every service the same for metrics, logs, and health checks.

Adapter is about normalizing what the app exposes. Ambassador is different: ambassador brokers what the app calls outbound.

## The idea
In a real platform, different applications expose different interfaces:

- one app exports metrics as plain text lines like `queries_total 42`
- another emits XML stats at `/stats.xml`
- another only writes counters into a local file
- one app logs as key=value fragments
- another logs in free-form sentences
- one app can be health-checked on `/ready`
- another needs a custom TCP probe and a cache ping

If your platform tooling assumes one standard - for example Prometheus metrics format, structured JSON logs, and `/healthz` - your platform becomes full of exceptions. Every scraper, log pipeline, and health monitor must carry per-app special cases.

The adapter pattern removes those special cases from the platform. You put the special logic close to the app, in a nearby container, and expose only the standard interface outward.

Think of it as local translation:

- app internals stay app-specific
- adapter understands app-specific details
- platform only sees standard contracts

This pattern is often confused with sidecar and ambassador, so keep the roles sharp:

- sidecar: adds helper behavior to the pod (broad category)
- ambassador: handles outbound calls from app to external services
- adapter: normalizes inbound-facing or platform-facing interface exposed by the app

In short: adapter standardizes what the app presents, so everything outside can stay generic.

## How it works

### Core mechanics
The adapter runs in the same pod as the application, so they share fast local communication. The adapter can read local files, query localhost endpoints, or inspect local sockets that are not exposed outside the pod.

The flow is usually:

1. App emits native signal in its own format.
2. Adapter reads/scrapes/parses that signal locally.
3. Adapter transforms and validates it.
4. Adapter re-exposes a standard interface.
5. Platform tooling consumes only the standard interface.

Because the transformation is local, platform systems do not need per-app branching logic. They call one shape everywhere.

### Canonical use 1: monitoring normalization
Monitoring stacks want consistent metrics. Prometheus, for example, expects a specific text exposition format with type/help metadata and one metric-per-line structure.

But applications often emit metrics in ad-hoc formats:

- compact key-value blobs
- unlabeled counters dumped to logs
- custom endpoints that do not match exposition rules

An adapter can scrape the app-native source and expose `/metrics` in standard Prometheus format. Then Prometheus scrape configs remain uniform across services.

Important detail: the adapter should own mapping rules explicitly. Example mappings:

- native `queries_total` -> Prometheus `app_queries_total`
- native `latency_ms_p95` -> Prometheus `app_request_latency_ms{quantile="0.95"}`
- native service identifier -> Prometheus label `service="checkout"`

The platform never needs to know these rules. Only the adapter does.

### Canonical use 2: logging normalization
Central log systems work best with structured logs, usually JSON with stable keys. Many apps do not emit that:

- mixed plain English and timestamps
- inconsistent severity labels (`WARN`, `warning`, `W`)
- no request IDs
- stack traces in multiline formats that break indexing

A logging adapter can:

- parse raw lines
- map levels to a fixed set
- attach missing metadata (service, pod, env)
- output clean JSON on a standard stream

This moves parse complexity to the edge, once per app type. Downstream storage and query layers stay simple and consistent.

### Canonical use 3: health check normalization
Schedulers and load balancers want a stable health endpoint, often `/healthz` returning clear status semantics.

Apps vary widely:

- some only have `/status` with ambiguous text
- some are healthy only if DB and cache checks pass
- some require an internal RPC check

The adapter can probe app-specific signals and publish one normalized `/healthz` contract.

Example behavior:

- adapter calls `http://127.0.0.1:8080/status`
- adapter pings local dependency or parses status payload
- adapter applies policy (for example, degrade if cache unreachable > 30s)
- adapter exposes `200 OK` with `{"status":"ok"}` or `503` with reason

Now probes are identical across services even though internals differ.

### Worked example 1: topology and data flow
Below is a concrete single-pod layout where app signals are private and standardized output is public.

```text
                     Pod boundary
+--------------------------------------------------------------+
|                                                              |
|  +-------------------+      localhost/volume      +--------+ |
|  | App container     | --------------------------> |Adapter| |
|  |                   |                             |container|
|  | - /internal-mets  | <-------------------------- |        | |
|  | - raw app.log     |    optional probe feedback  |        | |
|  | - /status-custom  |                             +---+----+ |
|  +-------------------+                                 |      |
|                                                        |      |
|                                              standard interfaces
|                                                        |      |
|                                    /metrics  /healthz  stdout |
+--------------------------------------------------------+------+
                                                         |
                                                         v
                                             Platform components
                                   (Prometheus, log collector, probes)
```

Key point: only the adapter output crosses into platform tooling. App-native endpoints stay internal.

### Worked example 2: metrics normalization trace
Suppose an app exposes this custom metrics endpoint:

```text
GET /internal-metrics
service=checkout
queries_total 42
errors_total 3
latency_p95_ms 187
```

Prometheus cannot rely on this format directly. The adapter does a deterministic transformation.

Step-by-step:

1. Adapter scrapes `http://127.0.0.1:8080/internal-metrics` every 10s.
2. Adapter parses each line by known schema (`name value`).
3. Adapter prefixes names to avoid collisions (`app_`).
4. Adapter maps p95 into a named gauge metric.
5. Adapter adds fixed label `service="checkout"`.
6. Adapter serves `/metrics` in exposition format.

Result exposed by adapter:

```text
# HELP app_queries_total Total number of queries processed by app
# TYPE app_queries_total counter
app_queries_total{service="checkout"} 42

# HELP app_errors_total Total number of failed queries in app
# TYPE app_errors_total counter
app_errors_total{service="checkout"} 3

# HELP app_latency_p95_ms 95th percentile request latency in milliseconds
# TYPE app_latency_p95_ms gauge
app_latency_p95_ms{service="checkout"} 187
```

Now every service can be scraped the same way: `GET /metrics` on adapter port. Reuse is the win: write this adapter once for this app type, deploy it anywhere that app runs.

### Worked example 3: raw log line to structured JSON
Suppose the app writes this messy line:

```text
2026/07/01 10:22:45 INFO checkout req=9f2 usr=381 action=pay amount=92.10USD took=187ms msg="payment accepted"
```

This is hard to query reliably because keys and value formats are inconsistent. The adapter parses and normalizes it into a strict JSON schema.

Transformation choices:

- timestamp -> ISO 8601 field `ts`
- `INFO` -> lowercase `level`
- `req` -> `request_id`
- `usr` -> `user_id`
- `amount=92.10USD` -> separate numeric `amount` and currency `currency`
- `took=187ms` -> numeric `duration_ms`
- add static context (`service`, `environment`)

Output emitted by adapter:

```text
{"ts":"2026-07-01T10:22:45Z","level":"info","service":"checkout","environment":"prod","request_id":"9f2","user_id":"381","action":"pay","amount":92.10,"currency":"USD","duration_ms":187,"message":"payment accepted"}
```

From the log backend's perspective, every service now has the same keys. Dashboards and alerts become reusable templates instead of per-service custom parsing rules.

### Design guidance for robust adapters
Adapters are simple in concept, but poor design can create hidden risk. Good adapter design follows a few rules.

1. Keep mapping logic explicit and versioned.
   - Store field mappings as reviewed config or code.
   - Avoid vague regex-only pipelines that silently drift.

2. Fail transparently, not silently.
   - Expose adapter self-metrics: parse failures, dropped lines, last successful scrape timestamp.
   - Emit clear error events when input format changes.

3. Bound resource cost.
   - Adapters run per pod, so CPU/memory overhead multiplies by replica count.
   - Keep parsing lightweight and avoid unbounded buffers.

4. Prefer deterministic transformations.
   - Same input should produce same output.
   - Deterministic mapping makes incidents debuggable.

5. Keep adapter scope narrow.
   - Normalize interface, do not re-implement business logic.
   - If adapter starts owning domain decisions, boundaries are wrong.

### Reuse model: one adapter per app type
The most important economic property of the pattern is reuse.

You do not write one adapter per pod instance. You write one adapter implementation per app interface shape. Then reuse it across all deployments of that app type.

Example:

- `checkout-adapter:v2` used by all checkout deployments
- `inventory-adapter:v1` used by all inventory deployments

Platform components stay unchanged because they always consume standard interfaces. New app types require only local adapter work, not platform-wide rewiring.

This gives local flexibility + global uniformity:

- app teams can evolve internals
- platform teams keep one stable ingestion/probe contract

## Pros
- Uniform platform contracts without forcing immediate app rewrites.
- Reduced complexity in central monitoring/logging/probe systems.
- Strong separation of concerns: app team owns app internals, platform sees standard outputs.
- Reusability by app type: once an adapter is built, all deployments of that type benefit.
- Lower migration risk for legacy apps that cannot easily change observability interfaces.

## Cons
- Extra moving part per pod (more images, config, and runtime overhead).
- Potential failure point: if adapter breaks, observability or probe signal can degrade.
- Mapping drift risk when app output changes but adapter rules are not updated.
- Added operational work to version and test adapter behavior.
- Can hide technical debt if used forever instead of improving app-native interfaces where feasible.

## Alternatives
- **Modify the app to emit standard formats directly.**
  - Best long-term simplicity when you control the code and can change it safely.
  - Removes one container and one translation hop.

- **A shared instrumentation library.**
  - Put standard metric/log/health emitters in a common library used by all services.
  - Works well when language stack is homogeneous and teams can adopt common runtime dependencies.

- **Central server-side transformation/ETL.**
  - Send raw data centrally, then normalize in ingestion pipelines.
  - Reduces per-pod overhead but can make central pipeline complex and app-specific again.

- **Agreeing on a standard so no adapter is needed.**
  - Organization-wide standards (formats, schemas, endpoint contracts) can eliminate many adapters.
  - Hard to enforce quickly in heterogeneous or legacy-heavy environments.

## When to use it
Use adapter when you need platform uniformity but application interfaces are heterogeneous today.

Good fit signals:

- legacy or third-party app cannot be modified easily
- multiple languages/frameworks emit different observability formats
- platform team wants one probe/scrape/log ingestion contract everywhere
- you need near-term consistency without a full rewrite program

It is especially useful in transitional architectures: adapters buy consistency now while teams gradually modernize internals.

## When NOT to use it
Avoid adapter when direct standardization is cheaper and sustainable.

Common no-go cases:

- you fully control app code and can emit standard metrics/logs/health directly with little effort
- you are adding adapters everywhere out of habit, even for brand new services
- adapter logic is growing into domain behavior rather than interface normalization
- per-pod overhead is significant at very high scale and central transformation is demonstrably simpler

Rule of thumb: adapter is a bridge, not an excuse to keep interfaces chaotic forever.

## Key takeaways / mental model
Treat adapter as an interface normalizer at the pod boundary.

- It converts app-specific outward signals into platform-standard outward contracts.
- It protects platform simplicity from application heterogeneity.
- It is local translation, not outbound brokering.

Quick mental check:

- Are you standardizing what this app exposes? -> adapter.
- Are you helping this app call external services? -> ambassador.

If you remember only one sentence, use this: adapter lets every service look the same to the platform without forcing every service to be built the same internally.

## Self-check questions
1. Your platform expects Prometheus `/metrics`, but a legacy app exposes `GET /stats` with custom lines. Sketch exactly where adapter logic should live and what contract the platform should consume.
2. You see a team proposing ambassador to solve inconsistent log formats. Why is that the wrong pattern, and what failure mode might this confusion cause?
3. An adapter currently maps `WARN`, `warning`, and `W` to `warn`. What observability risks appear if this mapping silently fails after an app update, and how would you detect it quickly?
4. At 800 replicas, each adapter uses 40 MB memory and 30 millicores CPU. How would you reason about whether to keep per-pod adapters or move transformation centrally?
5. Given a raw line `2026/07/01 11:00:00 ERR svc=billing req=a12 msg="db timeout"`, propose a normalized JSON output schema and explain which fields should be mandatory.
6. You are designing a new service from scratch under one language stack with a shared instrumentation SDK. Under what conditions would you skip adapter entirely, and what trade-off are you accepting?

## References
- Designing Distributed Systems (Brendan Burns), Chapter 4: "The Adapter Pattern"
- [designing-distributed-systems/02 - The Sidecar Pattern](02-sidecar.md)
- [system-design/15 - Observability: logging, metrics, tracing](../../system-design/lessons/15-observability.md)
