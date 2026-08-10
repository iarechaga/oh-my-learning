---
id: enterprise-patterns/13
subject: enterprise-patterns
title: Session State Patterns
slug: session-state
status: drafted
mastery:
seniority: mid
source: Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 3
prerequisites: [enterprise-patterns/01]
created: 2026-08-10
updated: 2026-08-10
---

# Session State Patterns

## TL;DR
A web application's individual requests are inherently stateless, but a user's overall interaction (a shopping cart, a multi-step form, login status) needs continuity across many requests — session state is where that continuity lives. Three placement choices exist: Client Session State (store it in the client — cookies, hidden form fields), Server Session State (keep it in server memory/cache, tied to a session ID), and Database Session State (persist it to a database) — each trading off differently between server memory pressure, scalability across multiple servers, and resilience to server restarts.

## The idea
HTTP's stateless-by-design nature (each request is independent, with no inherent memory of previous requests from the same user) creates a specific, foundational problem for any application needing continuity across multiple requests — nearly universal for real applications (a shopping cart persisting across page views, a logged-in user staying logged in). Session state is the general name for whatever mechanism bridges this gap, and *where* that state physically lives is a genuine, consequential architectural decision with real trade-offs, not an incidental implementation detail.

## How it works

### Client Session State — the client carries its own state
The server sends state back to the client with each response (in a cookie, in hidden form fields, in a client-side token), and the client sends it back with each subsequent request — the server itself holds nothing between requests, remaining genuinely, fully stateless.

**Trade-off.** The server scales trivially (any server can handle any request, since no server-side session data needs to be found or shared — directly enabling simple horizontal scaling, `architecture/system-design`) — but the amount of state that can practically be stored is limited (cookies have size limits), and any state visible to the client can potentially be tampered with unless properly signed/encrypted, and every request now carries the overhead of transmitting that state back and forth.

### Server Session State — the server remembers, keyed by a session ID
The server stores session data in its own memory (or an attached cache like Redis), and sends the client only a small opaque session ID (typically via a cookie); the client sends that ID back with each request, and the server looks up the corresponding state.

**Trade-off.** Can hold arbitrarily large, complex state without any client-side size limit, and nothing sensitive is exposed to the client — but this reintroduces genuine server-side state, which complicates horizontal scaling: if session data lives in one specific server's memory, subsequent requests from the same user must be routed back to that *same* server (session affinity/"sticky sessions" at the load balancer, see `architecture/system-design`'s load-balancing lesson), or the session data must be stored somewhere all servers can access (a shared cache), adding infrastructure complexity and a potential single point of failure/bottleneck.

### Database Session State — persisted, durable, shared
Session data is written to a database (or a durable, shared cache), keyed by session ID, giving any server access to any session's data by querying the shared store, and surviving a server restart since the data isn't tied to any specific server's memory.

**Trade-off.** Most resilient and most naturally compatible with horizontal scaling (any server can serve any request, since session data isn't tied to a specific server's memory at all) — but adds a database round trip to (potentially) every single request, a real latency cost that Server Session State's in-memory lookup avoids.

### Choosing among the three — matching to actual scale and durability needs
**Worked example — a progression many real systems actually follow as they grow.** A small application starts with Server Session State (simple, fast, in-memory, adequate for a single server or a small number of servers with sticky sessions). As the application scales to many servers and sticky-session routing becomes a genuine operational headache (uneven load distribution, a server restart losing all its sessions), the team migrates to Database Session State (typically backed by a fast, shared cache like Redis rather than a full relational database, to keep the latency cost manageable) — trading a small amount of added per-request latency for genuine, unconstrained horizontal scalability and resilience to individual server restarts.

Client Session State is chosen specifically when the state involved is genuinely small (a few key-value pairs — a cart item count, a display preference) and the horizontal-scaling and no-server-state benefits are worth the client-side size and tamper-risk constraints — many modern applications use it specifically for authentication tokens (JWTs) precisely for this reason, alongside Database/cache-backed session state for larger, more sensitive data.

## Pros
- Client Session State enables the simplest possible horizontal scaling, since the server holds no state that needs to be found or shared across servers.
- Server Session State offers the fastest access to session data (no database round trip) for applications that can tolerate sticky sessions or run on a small, stable number of servers.
- Database Session State provides the best resilience (survives server restarts) and unconstrained horizontal scalability, at the cost of a per-request database/cache round trip.

## Cons
- Client Session State is limited in size and requires careful signing/encryption to prevent tampering, and transmits the state's full size on every request.
- Server Session State complicates horizontal scaling (requiring sticky sessions or a shared cache) and loses all session data if the specific server holding it restarts or crashes.
- Database Session State's added round-trip latency, on every request, can be a real performance cost if not mitigated by a sufficiently fast, well-tuned shared cache.

## Alternatives
- **Stateless authentication tokens (JWTs) as a specific instance of Client Session State** — a common, modern, standardized approach specifically for authentication/authorization state, self-contained and signed, avoiding server-side session storage for that specific concern.
- **Sticky sessions with a shared cache as a fallback** — a hybrid approach some systems use, preferring fast in-memory Server Session State when a user's requests happen to land on the same server, falling back to a shared cache lookup when they don't.
- **Event sourcing / CQRS for session-like state** (see `architecture/microservices-patterns`) — a more elaborate approach for systems where the "session" concept itself needs richer history/audit capabilities than a simple key-value session store provides.

## When to use it
Use Client Session State for small, non-sensitive-or-properly-signed state where horizontal scaling simplicity is a priority. Use Server Session State for smaller-scale applications where sticky sessions or a small server count make its resilience trade-off acceptable. Use Database Session State once genuine horizontal scale and resilience to server restarts matter more than the added per-request latency.

## When NOT to use it
Don't use Client Session State for large or sensitive data that shouldn't be exposed to (or trusted from) the client, even if signed. Don't rely on Server Session State for a system that needs to scale across many servers without sticky-session complexity, or that needs to survive individual server restarts without losing user sessions.

## Key takeaways / mental model
Ask: "how large is the state, how sensitive is it, and how much does this system need to scale horizontally or survive individual server failures?" Small, non-sensitive, scale-friendly state favors the client; larger or more sensitive state favors the server, with the specific choice between in-memory and database-backed server storage determined by how much horizontal scale and restart-resilience you actually need.

## Self-check questions
1. Explain, using the sticky-sessions concept, why Server Session State complicates horizontal scaling compared to Client or Database Session State.
2. Describe the progression a growing application might follow from Server Session State to Database Session State, and explain what specific operational pain triggers that migration.
3. Why are JWTs a specific, modern instance of Client Session State, and what specific concern (among the three patterns' trade-offs) makes them well-suited to authentication specifically?
4. For a system you're familiar with, identify which session-state pattern it actually uses, and assess whether that choice fits its actual scale and durability needs.

## References
- Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 3: "State Persistence Patterns" (Client Session State, Server Session State, Database Session State sections).
