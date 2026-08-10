---
id: building-microservices/16
subject: building-microservices
title: "Security in a Microservice System"
slug: security
status: drafted
mastery: 
seniority: senior
source: "Building Microservices, 2nd ed. (Sam Newman), Chapter 11"
prerequisites: [building-microservices/06]
created: 2026-08-10
updated: 2026-08-10
---

# Security in a Microservice System

## TL;DR
A microservices system multiplies the number of network calls and trust boundaries compared to a monolith, so security has to be **defense in depth** — every service-to-service call authenticated and authorized, not just the system's external perimeter. Concretely this means service-to-service authentication (mTLS, service identity), disciplined secrets management, and abandoning the "trusted internal network" assumption in favor of a **zero-trust** posture, where no call is implicitly trusted just because it originates inside your own infrastructure.

## The idea
In a monolith, most of the "attack surface" that matters is the external perimeter — the boundary between the outside world and the single application process. Once inside that process, one function calling another doesn't need to authenticate itself; it's all the same trusted codebase running as one unit.

Decompose that monolith into a dozen independently-deployed services (Lesson 01), and something important changes: what used to be an in-process function call is now a network call between two separate processes, potentially on different machines, potentially crossing team or even organizational boundaries. Every one of those calls is now a place an attacker who has compromised *one* service, or who has gained any foothold on the internal network, could attempt to reach further into the system — impersonating a legitimate service, reading data it shouldn't, or escalating from one small breach into system-wide compromise.

The traditional assumption this breaks is the **"trusted internal network"** model — historically, many systems protected only the perimeter (a firewall, an API gateway with authentication) and assumed that once a request was "inside," it could be trusted, because getting inside was supposed to be hard. Newman is explicit that this assumption is dangerous in a microservices system, for two compounding reasons: there are now vastly more internal network calls (more surface for something to go wrong), and a single compromised service, a leaked credential, or a misconfigured internal endpoint can give an attacker exactly the "inside" position the old model implicitly trusted. Modern practice replaces this with **zero-trust**: no call is trusted just because of where it originates; every call, internal or external, is authenticated and authorized on its own merits.

## How it works

### Defense in depth: security at every boundary, not just the perimeter

The core discipline: apply security controls (authentication, authorization, encryption, input validation) at *every* service boundary, not only at the outermost edge where external traffic enters. Concretely, this means: `api-gateway` authenticating the external client is necessary but not sufficient — `order-service` calling `payment-service` also needs its own authentication and authorization check, `payment-service` calling `inventory-service` needs the same, and so on for every hop, so that a compromise or bug at any single layer doesn't grant free rein over everything behind it.

The reasoning: if only the perimeter is defended, then any successful breach of the perimeter (or any request that reaches the internal network through some other path — a misconfigured internal tool, a compromised dependency, an insider) has unrestricted access to every internal service, because nothing internal was checking. With defense in depth, a breach of one service is contained to what that service itself was authorized to do and reach — the blast radius is bounded, much like the bulkhead pattern from Lesson 14 bounds resource-exhaustion blast radius, applied here to security blast radius instead.

### Service-to-service authentication: mTLS and service identity

If every call needs to be authenticated, services need a way to prove *which service* is calling, not just that a request arrived. The standard mechanism is **mutual TLS (mTLS)**: both sides of a connection present a certificate proving their identity, not just the client verifying the server's certificate (as in ordinary one-way TLS used for a browser talking to a website). This gives the receiving service cryptographic proof of which service is calling it — `payment-service` can verify a call genuinely came from `order-service` (or whichever specific service's certificate signed the connection), not from an arbitrary process that happened to reach it on the internal network.

Each service is issued its own **service identity** (typically as a certificate, often provisioned and rotated automatically by supporting infrastructure — a service mesh, discussed below, or a dedicated identity/PKI system) — the software equivalent of a username specific to that service, used for every outbound call it makes. This identity is then the basis for **authorization**: even after `payment-service` verifies a call really came from `order-service`, it still needs to decide whether `order-service` is *allowed* to call the specific operation being requested (e.g., `order-service` might be permitted to call `authorizePayment` but not `issueRefund`, if refunds are meant to be triggered only by a dedicated `refund-service` or by an authenticated human operator).

### Secrets management

Services need credentials to talk to each other and to external systems — database passwords, API keys, TLS private keys, service-identity certificates. Hardcoding these into source code or configuration files checked into version control is a classic, still-common mistake: a leaked repository (or even just overly broad internal repository access) then leaks live credentials, and rotating a compromised credential that's scattered across a dozen services' config files is slow and error-prone exactly when speed matters most.

The standard practice: a dedicated **secrets management** system (e.g., a vault-style service) that stores credentials centrally, encrypted at rest, and issues them to services at runtime (via a short-lived token or a securely-fetched value, not baked into a deployed artifact), with fine-grained access control over which service can fetch which secret, and an audit log of every access. This also enables **credential rotation** — regularly replacing credentials, even without a known compromise, to limit how long a leaked or stolen credential remains useful — which is far more practical when credentials are centrally managed and dynamically fetched than when they're hardcoded and scattered across many services' deployed configuration.

### Worked example: containing a compromised service

Suppose an attacker finds and exploits a vulnerability in `recommendation-service` (a comparatively low-stakes, "customers also bought" widget) and gains the ability to execute arbitrary calls from within it.

**Without defense in depth (trusted-internal-network model):** `recommendation-service`, now under attacker control, can freely call any other internal service — including `payment-service` and `customer-data-service` — because internal calls were never individually authenticated or authorized; being "inside" the network was treated as sufficient trust. The attacker pivots from a minor, low-value service compromise into full access to payment and customer data.

**With defense in depth (mTLS + per-call authorization):** `recommendation-service`'s compromised identity can still make calls, but every call is authenticated (verified as genuinely coming from `recommendation-service`'s identity) and authorized against what `recommendation-service` is actually permitted to do. If `recommendation-service` was never granted authorization to call `payment-service` or `customer-data-service` in the first place (because it has no legitimate business reason to), those calls are rejected regardless of the compromise — the blast radius is contained to whatever `recommendation-service` itself was legitimately allowed to touch (likely just read access to product/catalog data), not the whole system.

### Service meshes as supporting infrastructure

Implementing mTLS, service identity issuance/rotation, and per-call authorization consistently across dozens of services, in every service's own code, is a lot of repeated, security-critical work to get right independently in every codebase — and a single team getting it wrong undermines the whole system's defense-in-depth posture. A **service mesh** (a dedicated infrastructure layer, often implemented as a sidecar proxy deployed alongside each service — connecting back to the deployment/orchestration concepts from Lesson 10) is a common way to apply these controls uniformly and centrally: the mesh handles mTLS, identity, and authorization policy enforcement at the infrastructure layer, so individual service teams don't each need to correctly re-implement security-critical networking code themselves. This is analogous to how a service mesh can also apply the resilience patterns from Lesson 14 (timeouts, retries, circuit breaking) consistently at the infrastructure layer rather than in each service's application code.

## Pros
- **Defense in depth** bounds the blast radius of any single service's compromise, rather than letting it become full internal network compromise.
- **mTLS/service identity** gives cryptographic, verifiable proof of which service is calling, closing the gap left by "trusted because it's internal" assumptions.
- **Centralized secrets management** enables fast credential rotation and removes hardcoded, leak-prone credentials from source code and config files.
- **A service mesh** applies these controls consistently across the whole system without every team re-implementing security-critical logic independently.

## Cons
- **Real implementation and operational overhead** — mTLS certificate issuance/rotation, authorization policy definition and maintenance, and secrets infrastructure are all real systems that must themselves be built, secured, and kept running reliably.
- **Latency and complexity cost** — mTLS handshakes and authorization checks on every internal call add (typically small but nonzero) latency and failure modes to every hop, on top of the resilience concerns from Lesson 14.
- **Policy sprawl** — as the number of services and their permitted call relationships grows, the set of authorization rules ("who can call whom, for what") itself becomes something that needs active management and review, or it drifts out of sync with what services actually need.

## Alternatives
- **Perimeter-only security (API gateway authentication, internal network trusted)** — simpler to implement, adequate for very small, low-risk internal systems with minimal blast-radius concerns, but explicitly the model this lesson argues against for any system of real scale or sensitivity, given how easily a single internal compromise or misconfiguration bypasses it entirely.
- **Network segmentation without per-call authentication** (VLANs/subnets restricting which services can reach which, without cryptographic identity per call) — a partial improvement over pure perimeter security, and often used as a complementary layer, but doesn't give the fine-grained, verifiable, per-call authorization that mTLS plus service identity provides, and is easier to misconfigure or bypass than cryptographic identity checks.

## When to use it
- Any microservices system handling sensitive data (customer PII, payment data, credentials) or operating in a regulated environment — defense in depth, service-to-service auth, and proper secrets management should be baseline, non-negotiable practice.
- Any system where a single compromised service having free rein over the rest of the internal network would be an unacceptable risk — which, in practice, describes most production systems of meaningful size.

## When NOT to use it
- A very small, internal-only, low-stakes system (e.g., an internal admin tool with two services, no sensitive data, tightly controlled access already) may reasonably defer the full mTLS/service-mesh investment initially — but the underlying zero-trust principle (don't assume internal calls are safe by default) is worth adopting in spirit even before the full infrastructure is in place, since retrofitting it later, across many already-deployed services, is significantly more work than building it in from early on.

## Key takeaways / mental model
More services means more network calls means more places a call could be malicious or compromised — security has to move from "guard the front door" to "verify everyone, everywhere, every time," which is what defense in depth and zero-trust mean concretely. mTLS plus service identity answers "who is really calling?"; per-call authorization answers "are they allowed to do this?"; centralized secrets management keeps the credentials that back both of those answers safe and rotatable. The payoff is a system where compromising one low-value service doesn't hand an attacker the keys to everything behind it.

## Self-check questions
1. Why does the "trusted internal network" assumption become more dangerous as a monolith is decomposed into more microservices, rather than staying equally risky?
2. What does mTLS prove that ordinary (one-way) TLS does not, and why does that matter for service-to-service calls specifically?
3. In the `recommendation-service` compromise worked example, what specifically stops the attacker from reaching `payment-service`, and why would a perimeter-only security model have failed to stop it?
4. Why is hardcoding a database credential into a service's checked-in configuration file a security risk beyond "someone might read the code," and what does centralized secrets management do to reduce that risk?

## References
- *Building Microservices*, 2nd ed. (Sam Newman, O'Reilly 2021), Chapter 11: "Security"
- Related: `system-design/13` (Security: Authentication and Authorization) for the broader authn/authz vocabulary (OAuth2/OIDC, RBAC/ABAC) this lesson applies at the service-to-service level; `building-microservices/10` (Deployment) for the service-mesh-capable orchestration infrastructure this lesson's controls are often built on.
