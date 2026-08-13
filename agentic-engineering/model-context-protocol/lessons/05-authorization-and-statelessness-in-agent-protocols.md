---
id: model-context-protocol/05
subject: model-context-protocol
title: Authorization and Statelessness in Agent Protocols: Why It Matters for Scaling
slug: authorization-and-statelessness-in-agent-protocols
status: drafted
mastery:
seniority: senior
source: "Model Context Protocol Blog: The 2026-07-28 Specification and its Changelog (2026); Descope: Diving Into the MCP Authorization Specification (2026); Google Developers Blog: Scaling AI Agent Infrastructure with the MCP Stateless updates (2026); Microsoft Community Hub: MCP Just Went Stateless (2026); Stack Overflow Blog: Is that allowed? Authentication and authorization in Model Context Protocol (2026)"
durability: durable
prerequisites: [model-context-protocol/04]
created: 2026-08-10
updated: 2026-08-10
---

# Authorization and Statelessness in Agent Protocols: Why It Matters for Scaling

## TL;DR
MCP treats an MCP server as an OAuth 2.1 resource server rather than trusting the client's word for who is calling, and it treats a connection as a sequence of self-contained requests rather than a sticky session tied to one server process. Both design choices exist for the same underlying reason: an MCP server is meant to run as ordinary, horizontally scaled infrastructure, and neither "trust the caller" nor "remember the caller" survives contact with a load balancer serving thousands of concurrent agent sessions across many server instances.

## The idea
Lesson 04 treated an MCP server as a service you design like any other backend: idempotency, scoped credentials, versioning. Two of those design pressures deserve a lesson of their own because they are not incidental implementation details - they are the two places where the protocol had to make an explicit, load-bearing architectural choice, and both choices trace back to the same constraint: MCP servers are expected to run at the scale of ordinary web infrastructure, not as one-off long-running processes with a single trusted caller.

**Authorization** is the "who is allowed to do this" problem. An MCP server sits between an agent and something valuable - a company's Jira, a production database, a payment system - and if it just trusts whatever the client claims about the calling user, any client-side bug or malicious client turns the server into an open door to that valuable resource. MCP's answer, formalized as of the OAuth 2.1-based authorization framework in the spec, is to stop treating the MCP server as its own identity provider and instead treat it as a **resource server**: something that validates tokens issued by a separate, trusted authorization server, the same shape every mature web API has used for a decade.

**Statelessness** is the "does correctly serving this request require remembering the last one" problem - the same distinction lesson 05 of `tool-use-agentic-loop` introduced generically for tool execution, now applied at the protocol layer itself, not just to individual tools. Early MCP transports required the server to hold a session (`Mcp-Session-Id`) tied to one specific process for the life of a connection. That works fine for a single developer running a local server on their laptop; it breaks down the moment an organization wants to run that server as a fleet behind a load balancer, because now every request for a given session has to find its way back to the one process that remembers it - the exact "session affinity" cost that lesson covered generically for stateful tools, now shown to apply to the protocol's own connection model, not just to individual tool calls.

Both problems share a root cause: the protocol was originally designed against the mental model of "one agent, one long-lived local server process," and once MCP servers started being deployed as real internet-facing infrastructure - shared across many users, scaled across many instances, sitting behind corporate identity systems - that original mental model had to be replaced with the same patterns the rest of distributed web infrastructure already uses: token-based authorization delegated to a real identity provider, and request-level statelessness that lets any instance serve any request.

## How it works

### The authorization model: MCP server as resource server, not identity provider
Under the OAuth 2.1-based authorization framework the MCP specification defines, three roles are kept strictly separate:

- **The authorization server** - an external identity provider (a company's SSO, Okta, Auth0, or similar) that authenticates the human user and issues access tokens. The MCP server does not do this itself.
- **The MCP server (resource server)** - validates the access token presented with each request and enforces what it's allowed to authorize, but never handles the user's actual credentials and never decides identity on its own.
- **The MCP client (OAuth client)** - obtains a token from the authorization server on the user's behalf (via the standard OAuth 2.1 authorization-code flow with PKCE - Proof Key for Code Exchange, required because most MCP clients are public clients that cannot hold a secret safely) and presents it to the MCP server on every call.

This is a deliberate application of a well-worn pattern (the same separation of concerns underlying "log in with Google" on any third-party website) to a new context: instead of every MCP server having to build and secure its own login system, it delegates authentication entirely to a real identity provider and limits its own job to "is this token valid, and what does it authorize."

The detail that matters most in practice is **token audience binding**, via resource indicators (RFC 8707). A token is minted for a *specific* MCP server, not for "whoever presents it." The MCP server must check that a token's audience claim actually names it before accepting the token. Without this check, a classic **confused-deputy** vulnerability opens up: an agent legitimately holds a token scoped to Server A (say, a low-risk documentation search server), and a malicious or buggy Server B - one the agent also happens to be connected to - replays that same token against Server A's API, or worse, a malicious Server A tries to use a token the agent obtained for Server A against some *other* service the agent trusts, tricking a trusted intermediary into acting on the attacker's behalf using credentials that were never meant for it. Binding every token to exactly one intended recipient closes that hole: a token minted for Server A is worthless if presented to Server B, because Server B's audience check rejects it outright.

> **Example (as of the 2026-07-28 spec revision):** the specification requires clients to record which authorization server issued a given credential and forbids reusing that credential with a different authorization server; it also requires validating the `iss` (issuer) parameter in the authorization response against the recorded issuer before redeeming an authorization code. Both are concrete, dated instances of the same underlying principle - never let a credential or a code minted in one trust context be replayed in another. Check the current spec for the exact mechanics, since this area continues to tighten.

### Worked example: why "just trust the client" fails at scale
Imagine an MCP server exposing `read_customer_record(customer_id)` against a CRM, deployed for an entire sales organization of 400 people.

**Naive design (no real authorization):** the client sends `{"customer_id": "C-4821", "user_email": "alice@company.com"}` and the server trusts the `user_email` field to decide what Alice is allowed to see. Any client - including a compromised browser extension acting as an MCP client, or a bug in a client the sales team didn't audit - can put any email address in that field and read any customer's record as anyone. There is no real access control here at all; it's a suggestion box.

**MCP's authorization model:** Alice's MCP client obtains a short-lived OAuth access token from the company's real identity provider, scoped to Alice's identity and audience-bound to this specific CRM MCP server. Every `read_customer_record` call carries that token. The server validates the token's signature, checks its audience matches itself, checks it hasn't expired, and only then looks up what Alice - the token's actual, IdP-verified subject - is authorized to see. A compromised client can still misuse *Alice's own* legitimate access, but it cannot forge access as someone else, and a token stolen from a different MCP server is useless here because the audience check rejects it.

### Why statelessness is the scaling half of the same story
Consider that same CRM MCP server now needs to serve 400 concurrent salespeople reliably, with instances that can be added, removed, or restarted without anyone noticing.

**Session-bound design (pre-2026-07-28 model):** the client opens a connection, the server hands back an `Mcp-Session-Id`, and every subsequent request in that session must be routed to the *same* server process that issued it - because that process is the one holding whatever context the session accumulated. This forces "sticky" load balancing (routing by session ID rather than round-robin), means a crashed instance drops every session it was holding, and means autoscaling has to account for "don't kill an instance that's mid-session" - real infrastructure complexity that mirrors, one-for-one, the stateful-tool cost described generically in `tool-use-agentic-loop/06`.

**Stateless-core design (2026-07-28 spec):** the `initialize`/`notifications/initialized` handshake and the session-ID header are removed entirely. Every request carries its own protocol version and capabilities; nothing about correctly serving request N depends on which process served request N-1. A request can land on any healthy instance behind a plain round-robin load balancer, an instance can be recycled mid-traffic with zero session loss, and horizontal autoscaling works with the same off-the-shelf infrastructure any ordinary stateless HTTP API uses - no custom session-affinity layer required. Where a server genuinely needs cross-call state (a long-running task, a multi-step workflow), the spec pushes that into an explicit, server-minted handle passed back as an ordinary argument on the next call - state made visible and portable across instances, rather than implicit and pinned to one process, which is exactly the "externalize the state" alternative `tool-use-agentic-loop/06` names generically for any stateful tool.

```
Before (session-bound)                 After (stateless core)
------------------------------         ------------------------------
Client -> initialize -> Server A       Client -> request (self-describing,
          gets Mcp-Session-Id                    carries version + a
Client -> tool call    -> MUST route             server-minted handle if
          (Session-Id)    to Server A             continuing prior work)
                                                  -> ANY healthy instance
Server A restarts -> session lost      Instance recycled -> next request
                                                  just lands elsewhere,
                                                  nothing lost
```

### Worked example: what breaks (and what doesn't) when an instance dies
A company runs its internal MCP server fleet at 6 instances behind a load balancer, handling roughly 50 requests/second at peak. One instance is terminated mid-traffic - a routine autoscaling event, not an incident.

- **Under session affinity:** every in-flight session pinned to that instance breaks. If 200 concurrent sessions happened to be routed there, all 200 clients see failures and must re-`initialize` from scratch, re-establishing whatever context they had. The on-call engineer has to reason about "how many sessions does losing this instance cost us" before every scale-down.
- **Under the stateless core:** the requests that were in flight to that instance fail (an ordinary, expected class of failure any HTTP client already retries), but no other session anywhere is affected, because no other request depended on that instance's memory. The next request from any client - including one that was talking to the terminated instance - is served correctly by whichever instance the load balancer happens to route it to. Scaling down is a non-event operationally.

## Pros
- Authorization delegated to a real identity provider means MCP servers don't each reinvent (and each potentially get wrong) their own login and access-control system - security-critical code lives in one audited place instead of being duplicated across every server an organization deploys.
- Audience-bound tokens close the confused-deputy hole - a stolen or misdirected token is useless against any server it wasn't minted for, which matters enormously once an agent is routinely connected to many MCP servers at once (lesson 07).
- A stateless protocol core lets MCP servers scale exactly like ordinary stateless web services: round-robin load balancing, painless autoscaling, and instance failure that costs nothing beyond the in-flight requests to that one instance.
- Explicit, server-minted handles for the state that genuinely needs to persist across calls make that state visible and portable, instead of hidden inside one process's memory.

## Cons
- OAuth 2.1 with PKCE and audience-bound tokens is meaningfully more upfront engineering than "just check an API key" - every MCP server that wants to be taken seriously in an organization now needs proper token validation, not a shortcut.
- Statelessness pushes real complexity onto the server's *data model*: anything that used to be implicit in-process memory (an open transaction, a partially built result set) now has to be designed as an explicit handle the client carries and passes back, which is extra design work compared to just leaving it in memory.
- The spec in this area has changed multiple times in under two years (session-based, to Streamable HTTP, to the fully stateless core) - teams that hard-coded assumptions from an earlier revision have had to do real migration work more than once.
- None of this eliminates the need for authorization *decisions* (what should Alice actually be allowed to see) - it only fixes *authentication and scaling*; access-control policy is still the deploying organization's job (lesson 04's least-privilege scoping, and `agent-security-and-operations/03`).

## Alternatives
- **API keys with no real identity behind them** — simpler to stand up, but collapses "who is this" and "what are they allowed to do" into one static, hard-to-rotate, hard-to-scope secret; fine for a personal local server, unacceptable for anything multi-user or internet-facing.
- **mTLS (mutual TLS) for server-to-server trust** — authenticates *which machine* is calling rather than *which user*, so it solves a different problem; often layered underneath OAuth for service-to-service legs rather than replacing user-level authorization.
- **Sticky sessions with sufficient over-provisioning** — you can keep the old session-affinity model and simply throw enough redundant capacity at it to tolerate instance loss; this trades real infrastructure cost and operational fragility for avoiding the migration work of adopting the stateless core, and does not scale as cleanly as the load-balancer-agnostic approach.

## When to use it
Adopt full OAuth 2.1 authorization and design for the stateless core whenever an MCP server is shared across more than one user, deployed as internet-facing or organization-facing infrastructure, or expected to scale beyond a single process - which describes essentially every MCP server an organization runs in production rather than on one developer's laptop.

## When NOT to use it
A purely local, single-user MCP server (a developer's own laptop tool connecting to their own filesystem) does not need OAuth's full machinery - a much lighter local-trust model is proportionate, and the spec does not force internet-scale authorization onto that case. Similarly, a genuinely single-instance, low-traffic internal tool may reasonably defer the stateless-core migration if the operational cost of session affinity is trivial at its scale - but that decision should be revisited the moment the server needs to be shared or scaled, not left as a permanent assumption.

## Key takeaways / mental model
Ask two separate questions about any MCP server you deploy: "who is allowed to call this, and how do I know?" (authorization - answered by delegating to a real identity provider and binding tokens to this server's audience) and "does correctly serving this request require remembering the last one?" (statelessness - answered by pushing any needed cross-call state into an explicit, server-minted handle rather than process memory). Both questions have the same payoff: they are what let an MCP server be run as ordinary, boring, horizontally scaled infrastructure instead of a fragile, hand-held, single-process trust boundary.

## Self-check questions
1. A teammate proposes an MCP server that authenticates callers by checking a `user_id` field the client includes in the request body. Explain, using the confused-deputy scenario, exactly what goes wrong and how audience-bound OAuth tokens close that hole.
2. Your team's MCP server currently issues an `Mcp-Session-Id` and expects every subsequent request from a client to include it. A colleague wants to add autoscaling. What specifically has to change in the server's design before autoscaling behind a plain round-robin load balancer is safe, and why?
3. A long-running MCP tool (say, a report that takes 10 minutes to generate) needs to let the client check back later for the result. Design this in a way that is consistent with a stateless protocol core - what does the server return immediately, and what does the client do with it?
4. Explain why PKCE specifically matters for MCP clients as opposed to a traditional confidential server-side OAuth client, and what property of most MCP clients makes it non-optional.
5. A security reviewer asks: "if an MCP server's authorization is fully delegated to an external identity provider, what is the MCP server actually still responsible for getting right?" Give a complete answer.

## References
- [Model Context Protocol Blog: The 2026-07-28 Specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [Model Context Protocol: Key Changes (2026-07-28 changelog)](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- [Descope: Diving Into the MCP Authorization Specification](https://www.descope.com/blog/post/mcp-auth-spec)
- [Google Developers Blog: Scaling AI Agent Infrastructure with the MCP Stateless updates](https://developers.googleblog.com/scaling-ai-agent-infrastructure-with-the-mcp-stateless-updates/)
- [Microsoft Community Hub: MCP Just Went Stateless - What the 2026 Spec Changes About Scaling on App Service](https://techcommunity.microsoft.com/blog/appsonazureblog/mcp-just-went-stateless-%E2%80%94-what-the-2026-spec-changes-about-scaling-on-app-servic/4530222)
- [Stack Overflow Blog: Is that allowed? Authentication and authorization in Model Context Protocol](https://stackoverflow.blog/2026/01/21/is-that-allowed-authentication-and-authorization-in-model-context-protocol/)
