---
id: microservices-patterns/10
subject: microservices-patterns
title: "Production-Ready Services"
slug: production-ready-services
status: drafted
mastery:
seniority: senior
source: "Microservices Patterns (Chris Richardson), Chapter 11"
prerequisites: [microservices-patterns/03]
created: 2026-07-01
updated: 2026-07-01
---

# Production-Ready Services

## TL;DR
Business logic working is necessary but not enough.
A service is production-ready only when it is observable, secure in how identity flows, and configurable from outside the code.
At microservice scale, these concerns must be standardized, or operations become fragile.

## The idea
Many teams think they are done when feature tests are green.
In production, this is where the real work starts.

A service that correctly creates an order can still be unsafe if:

- nobody can tell why latency spiked
- downstream calls cannot be correlated in logs
- any internal hop can trust forged identity
- config changes require rebuilds or risky manual edits

These are cross-cutting concerns, sometimes called operational "-ilities".
They are not side details.
They are what let a service survive real traffic, incidents, and audits.

The core pattern is simple:
keep business logic local to each service, but make observability, security, and configuration consistent everywhere.
Doing each concern by hand in each service does not scale.
It creates drift, incident chaos, and security gaps.

## How it works

### Pillar 1 - Observability patterns
Observability is your ability to explain what happened and why, even for failures you did not predict.
In microservices, one user request crosses many services, so no single log file tells the full story.

#### Health check API
Each service exposes a health endpoint, often `/health`, but this usually maps to two checks:

- **Liveness:** is the process alive enough to keep running?
- **Readiness:** can this instance safely receive traffic now?

Liveness should be shallow and local.
Readiness can include dependencies required to serve requests, such as a database or message broker.

If you put deep dependency checks into liveness, a temporary dependency outage can cause restart storms.
If you put no dependency checks into readiness, traffic is sent to broken instances.

#### Application metrics
Metrics summarize behavior over time and support alerting.
Baseline service metrics should include request rate, error rate, and latency distribution.

Do not rely on average latency alone.
You need percentiles like p95 and p99 to expose tail latency.
For FTGO, "Order p99 over 1500ms" is far more actionable than "average is 180ms".

Add dependency metrics too: call latency to Kitchen, Delivery, Payment, and datastore operations.
Many incidents are dependency failures disguised as "slow service".

#### Distributed tracing
Distributed tracing links all work for one request using a single trace ID.
Each service creates spans for local operations, with parent-child span relationships.

Trace propagation is mandatory.
If Service A calls Service B without forwarding trace context, your trace breaks.
Then root cause analysis turns into guesswork.

With proper propagation, you can answer:

- which service added most latency
- where retries started
- where errors first appeared

#### Log aggregation
Logs remain critical, but only if they are structured and centralized.

Pattern:

1. emit structured logs (key-value fields)
2. include stable fields (`service`, `env`, `trace_id`, `request_id`, severity)
3. aggregate centrally
4. query by trace ID, user, endpoint, and error code

Without aggregation, you debug container by container.
Without structure, search quality collapses.

#### Exception tracking
Exception tracking groups repeated failures so teams see patterns, not noise.
Instead of reading 10,000 stack traces, you get issue clusters with frequency, first seen, and affected release.
This is essential right after deploys when regressions appear quickly.

#### Audit logging
Audit logs are not normal debug logs.
They capture sensitive business and security actions with actor, action, target, time, and outcome.

Examples for FTGO:

- who changed courier payout details
- who granted an elevated role
- who canceled order `order-7842`

Audit logs need stricter retention and access controls than ordinary logs.

### Worked example 1 - Request path with trace ID + JWT through gateway -> service A -> service B
```text
Client -> API Gateway -> Order Service -> Kitchen Service

Client request:
POST /orders
Authorization: Bearer <JWT>

Gateway:
- authenticates client
- creates trace_id=abc-123, span_id=gw-1
- forwards headers:
    trace_id: abc-123
    parent_span_id: gw-1
    authorization: Bearer <JWT>

Order Service:
- validates JWT signature + exp
- reads claims sub=consumer-123, roles=[CONSUMER]
- creates span_id=ord-9 (parent gw-1)
- logs trace_id=abc-123
- calls Kitchen with same trace_id + JWT

Kitchen Service:
- validates JWT again
- creates span_id=kit-4 (parent ord-9)
- logs trace_id=abc-123

Result: end-to-end correlation via trace_id=abc-123, identity preserved via JWT.
```

### Worked example 2 - Distributed trace assembly across 3 services with span IDs
```text
Trace ID: abc-123

[span-100] Gateway receive /orders
  |
  +-- [span-210] Order createOrder()
  |      |
  |      +-- [span-211] Order DB insert
  |      |
  |      +-- [span-212] call Kitchen /tickets
  |             |
  |             +-- [span-310] Kitchen reserveCapacity()
  |
  +-- [span-220] call Delivery /assign
         |
         +-- [span-410] Delivery selectCourier()

If span-310 is slow, total checkout latency rises even when Gateway and Order are healthy.
```

### Pillar 2 - Security: identity propagation with access tokens
In production microservices, identity should flow with each call.
The common pattern is:

1. API gateway authenticates external user once.
2. Gateway forwards signed access token (JWT) internally.
3. Each service verifies token integrity.
4. Each service authorizes using claims and local policy.

#### Why not re-authenticate at every hop?
If every service re-runs full authentication against the identity provider, one user request can trigger many auth round trips.
This adds latency, increases auth-system load, and can create cascading failures.

Token propagation avoids that fan-out.
But this does not mean blind trust.
Every service still verifies signature, expiry, issuer, and audience.

So the rule is:

- do not re-authenticate login flow at each hop
- do verify token validity at each hop

#### Claims and authorization
JWT claims give portable identity context.
Example claims: subject (`sub`), roles, scopes, tenant, issuer, expiry.

Order Service and Kitchen Service may both accept the same JWT, but they enforce different permissions.
Identity propagation is shared.
Authorization decisions stay local.

#### Token propagation for sync and async paths
For sync HTTP/RPC calls, propagate token and trace headers.
For async messaging, put identity context in message headers/metadata and validate before side effects.

Typical async metadata:

- `auth_token` or secure token reference
- `sub=consumer-123`
- `roles=[CONSUMER]`
- `trace_id=abc-123`

### Worked example 3 - JWT claims validated at two services
```text
JWT payload (signed)
{
  "iss": "https://auth.ftgo.example",
  "aud": "ftgo-services",
  "sub": "consumer-123",
  "roles": ["CONSUMER"],
  "exp": 1782892800
}

Order Service validation:
1) signature valid
2) exp not expired
3) aud includes ftgo-services
4) role CONSUMER allowed for createOrder

Delivery Service validation:
1) same signature checks
2) same exp checks
3) issuer trusted
4) role CONSUMER allowed for trackOrder, denied for assignCourier

Same token, independent authorization at each service boundary.
```

### Pillar 3 - Configuration: externalized, environment-aware, secret-safe
Config must be external to code so the same artifact runs across environments.
Values that commonly differ by environment:

- dependency endpoints
- timeout and retry policy
- feature flags
- queue/topic names

Example:

- dev `payment.timeout_ms=3000`
- prod `payment.timeout_ms=800`

No code rebuild should be needed to make that change.

#### Config distribution models
Two common models:

- **Pull config server:** service fetches config at startup or polling interval.
- **Push config server:** platform pushes config updates to services.

Pull is simpler and common.
Push can reduce update delay but requires robust delivery and rollback controls.

#### Secrets handling
Secrets are a special config class.
Never treat API keys and passwords like ordinary env vars in shared files.

Core practices:

- do not commit secrets
- store encrypted in a secret manager
- grant least-privilege access per service identity
- rotate on schedule and after incidents
- redact secrets from logs and traces

### Platform consistency contract
Production-readiness scales when teams follow a platform contract:

- health checks behave consistently
- telemetry fields are standardized
- token verification rules are uniform
- config and secrets come from approved systems

This reduces drift and keeps incidents diagnosable under pressure.

## Pros
- Faster incident diagnosis through shared trace IDs, structured logs, and useful metrics.
- Stronger service-to-service security from consistent token verification and claim usage.
- Safer operations from externalized config and controlled secret handling.
- Better team scalability because platform standards replace per-service reinvention.

## Cons
- Requires upfront platform engineering investment.
- Adds operational complexity (sampling, key rotation, config rollout controls).
- Poor telemetry design can create high noise and storage cost.
- Shared observability and config infrastructure becomes critical infrastructure.

## Alternatives
- **Build each concern into every service by hand (does not scale)** - maximum local control, but duplication and drift grow quickly.
- **A service mesh / sidecar to offload observability+security** - moves parts of telemetry and policy to infrastructure sidecars, similar to the sidecar pattern in designing-distributed-systems; less app code burden, more platform complexity.
- **A shared platform library** - centralizes implementation in code libraries; pragmatic for many teams, but weaker when services use many languages/runtimes.
- **Session-per-service auth vs token propagation** - each service does its own session/auth exchange; can improve immediate revocation semantics but usually increases coupling and latency.

## When to use it
Use this pattern when you run multiple collaborating services in real production, especially with frequent deploys, sensitive data, and strict uptime expectations.
If incidents currently require hero debugging, standardizing these three pillars is a high-leverage move.

## When NOT to use it
Do not implement full platform-grade machinery for tiny throwaway prototypes or one-off internal scripts with no reliability or compliance requirements.
Even then, keep a migration path so observability, token propagation, and externalized config can be added before growth.

## Key takeaways / mental model
Treat every service as two products:

1. business behavior
2. operational behavior

Observability answers: what happened, where, and why.
Security answers: who is calling, and what are they allowed to do.
Configuration answers: what can change safely per environment without rebuilding.

If these are inconsistent across services, your system is brittle.
If these are standardized, you can ship faster with less operational risk.

## Self-check questions
1. FTGO checkout latency spikes only for some requests. Which combination of metrics, logs, and tracing data would you inspect first, and why?
2. In gateway -> Order -> Kitchen, why is authenticate-once-plus-verify-every-hop usually safer and more scalable than full re-authentication at each hop?
3. How would you design liveness and readiness for a service that can run without its database for a short period but cannot serve writes?
4. An async consumer receives `OrderCreated` without identity metadata. What security and audit risks does this create, and what headers should be required?
5. Your team changed `payment.timeout_ms` in prod and caused an outage. What config governance steps (validation, staged rollout, rollback) would prevent recurrence?
6. Two services validate the same JWT but allow different actions. Explain why this is expected in a good design, not a contradiction.

## References
- Microservices Patterns (Chris Richardson), Chapter 11: "Developing production-ready services"
- [system-design/15 - Observability: logging, metrics, tracing](../../system-design/lessons/15-observability.md)
- [system-design/13 - Security: authentication and authorization](../../system-design/lessons/13-security-auth.md)
