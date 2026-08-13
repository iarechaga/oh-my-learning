---
id: model-context-protocol/02
subject: model-context-protocol
title: "MCP Architecture: Hosts, Clients, and Servers"
slug: mcp-architecture
status: drafted
mastery:
seniority: mid
source: "Model Context Protocol specification: Architecture (spec.modelcontextprotocol.io, 2026); Model Context Protocol Blog: The 2026-07-28 Specification (2026); modelcontextprotocol.io: Build an MCP server tutorial (2026)"
durability: durable
prerequisites: [model-context-protocol/01]
created: 2026-08-10
updated: 2026-08-10
---

# MCP Architecture: Hosts, Clients, and Servers

## TL;DR
MCP splits every integration into three distinct roles: a **host** (the AI application the user actually uses, e.g. a chat client or IDE), one or more **clients** living inside that host (each maintaining a dedicated 1:1 connection to exactly one server), and **servers** (the programs that expose a tool or data source's capabilities over the protocol). This host/client/server split, not just "there's a client and a server," is what makes the M+N story from `model-context-protocol/01` actually work: a server never needs to know which host it's plugged into, and a host can plug into any number of servers by spinning up one client per connection.

## The idea
`model-context-protocol/01` established *why* a shared protocol beats bespoke per-pair integrations. This lesson is about the specific shape of that protocol: who talks to whom, over what transport, and what has to happen before a single tool call can occur. Getting this shape right is what makes the reuse promise real - if "client" and "server" were just a generic two-party relationship, you would still need custom logic in the host for every kind of server it talks to. MCP avoids that by keeping the client itself generic (it only needs to speak the protocol) and pushing everything server-specific behind the server's own boundary, isolated one connection at a time.

## How it works

### The three roles, and why there are three, not two
- **Host** - the user-facing AI application: Claude Desktop, an IDE like Cursor or VS Code with MCP support, a custom agent CLI, or any application built with an MCP-aware SDK. The host owns the LLM conversation, decides which servers to connect to, and is responsible for surfacing tool-use approvals to the user (per the tool-call round trip from `tool-use-agentic-loop/01` - the host is the "your application code" side of that round trip).
- **Client** - a component living *inside* the host, one per server connection. The client's entire job is protocol mechanics: sending and receiving JSON-RPC 2.0 messages, negotiating capabilities, and translating what the server exposes into a form the host can hand to the model. A client is not shared across servers - each client maintains exactly one dedicated connection to exactly one server, so a host connected to 5 servers runs 5 client instances internally.
- **Server** - a lightweight program that exposes a specific capability set (tools, resources, and/or prompts - `model-context-protocol/03`) to whichever client connects to it. A server does not know what host it's embedded in, does not maintain relationships with multiple hosts simultaneously per connection, and does not need any code specific to Claude Desktop versus Cursor versus a custom agent - it only needs to speak MCP correctly.

The reason this is three roles rather than a plain client-server pair is precisely the M+N argument: the *client* role is what a host builder writes once, generically, and reuses for every server it ever connects to; the *server* role is what a tool builder writes once, generically, and it works with every host that implements a client. If "client" logic were entangled with "host" logic, a host would still need bespoke code per server, defeating the point.

```
        HOST (e.g. an IDE with MCP support)
        +--------------------------------------------------+
        |  LLM conversation loop                            |
        |                                                    |
        |   [Client A] ---- 1:1 connection ----> [Server: GitHub]
        |   [Client B] ---- 1:1 connection ----> [Server: Postgres]
        |   [Client C] ---- 1:1 connection ----> [Server: Filesystem]
        +--------------------------------------------------+
```
Three servers here need zero knowledge of each other or of this specific host; swap this host for a different one, and the same three servers connect unmodified through that host's own client implementations.

### Transport: stdio versus HTTP, and what each is for
The client-server connection needs an actual transport to carry JSON-RPC 2.0 messages back and forth, and MCP defines two primary ones, chosen for different deployment shapes:
- **stdio (standard input/output)** - the host launches the server as a local subprocess and communicates over its stdin/stdout streams. This is the natural fit when the server needs direct access to something local - the filesystem, a local database, local credentials - and it avoids network exposure entirely, since the "connection" never leaves the machine.
- **Streamable HTTP** - the server runs as an independent, possibly remote, network-accessible process, and the client connects over HTTP. This is the natural fit for a server that's centrally hosted (e.g. a company's internal CRM server that many employees' hosts should reach) or for a third-party server you don't run yourself.

**Worked example - choosing a transport.** A developer building a personal coding agent wants it to read files in the current project and also query the company's shared analytics warehouse. The filesystem capability ships as a stdio server - launched as a subprocess right on the developer's machine, no network exposure needed for local file access. The analytics-warehouse capability ships as an HTTP server run centrally by the data team - one server instance serves every employee's host, rather than each developer needing local database credentials and a locally-running server. Both connect to the same host through the same client abstraction; only the transport underneath differs, and the host code that talks to "a server" does not need to change based on which transport is in play.

### Connection lifecycle: capability negotiation before any tool call
Before a client can invoke anything on a server, the two sides go through a lifecycle so that neither assumes a capability the other doesn't actually support. Historically (through the 2025-era stateful protocol core) this was a three-phase handshake:
1. **Initialization** - the client sends an `initialize` request declaring the protocol version it speaks and the capabilities it supports; the server responds with the protocol version and capabilities *it* supports (tools? resources? prompts? which optional features?). The two sides converge on the intersection of what both support.
2. **Operation** - normal request/response traffic: the client lists and calls tools, reads resources, fetches prompts, per `model-context-protocol/03`.
3. **Shutdown** - graceful termination of the connection.

> **Example (Aug 2026):** the MCP specification's 2026-07-28 revision restructured this lifecycle around a stateless protocol core - the persistent `initialize`/`initialized` handshake and the server-side session identifier it used to require are gone, replaced by self-describing requests that carry protocol version, client identity, and capabilities as metadata on every call, rather than negotiated once and remembered. Capability negotiation as a *concept* (neither side assumes an untested capability) is durable; whether it happens once per persistent session or freshly on every request is the kind of detail that has already changed once and may change again - check the current spec revision for which model is in force. `model-context-protocol/05` covers why this statelessness shift matters specifically for scaling servers.

### One client, one server: what this constrains, and why it's a feature
Because each client maintains exactly one connection to exactly one server, a server exposing "read GitHub issues" and a server exposing "query Postgres" are architecturally isolated from each other inside the host - the host, not either server, is the only place that combines their capabilities into one agent's toolset. This is a deliberate security and reasoning boundary, not an accidental limitation: a compromised or misbehaving server cannot directly see or influence another server's connection, because there is no shared state between clients beyond what the host itself explicitly aggregates. A host wanting to offer 10 servers' worth of capability runs 10 independent client connections and merges the results only at the point where it hands a combined tool list to the model - the isolation is per-connection by construction, not by convention.

## Pros
- The host/client/server split lets a tool builder write one server, reusable by every conformant host, and a host builder write one generic client mechanism, reusable for every conformant server - the architectural mechanism that actually delivers the M+N story from `model-context-protocol/01`.
- Per-connection isolation between servers gives you a natural security boundary: one server's failure or compromise doesn't automatically leak into another server's connection.
- Transport choice (stdio vs. HTTP) lets the same architecture cover both "purely local capability" and "centrally hosted, shared capability" without changing how the host or the model-facing tool-call mechanics work.

## Cons
- Every server connection is a separate process (stdio) or a separate network endpoint (HTTP) the host has to manage, monitor, and handle failures for - more servers means more moving parts to keep alive, not a single "the integration layer" to reason about.
- Because a client is 1:1 with a server, any coordination *across* servers (e.g. "use the GitHub server's result to decide what to query in the Postgres server") has to happen in the host/model layer above both connections - the protocol itself gives you no cross-server primitive.
- The lifecycle's move toward statelessness (2026-07-28) is a genuine architectural discontinuity for anyone who built against the earlier stateful session model - code that assumed a persistent `Mcp-Session-Id` needs to change, which is exactly the kind of dated detail this lesson flags rather than treats as permanent.

## Alternatives
- **A monolithic host with tools hardcoded in-process** — no client/server split at all; the host's own codebase directly implements every tool. Simpler for a small, fixed tool set the host author fully controls, but reintroduces the M x N problem the moment a second host wants the same tools.
- **A single shared server exposing everything** — instead of one server per tool/data source, one large server multiplexes many capabilities behind one connection. Reduces the number of connections a host manages, but concentrates failure and trust: a bug or compromise in that one server now affects every capability behind it, unlike per-server isolation.
- **Direct SDK/library integration (no protocol at all)** — the host calls a tool's official SDK directly in-process, no client-server boundary. Can be lower-latency for a capability that only ever needs to run inside that specific host's process (e.g. calling a local Python library), but is exactly the bespoke-per-pair pattern `model-context-protocol/01` argues against once more than one host wants the same capability.

## When to use it
Use the full host/client/server architecture whenever you're building either side of a *reusable* integration: a host meant to work with more than one server, or a server meant to be reachable from more than one host. Choose stdio when the capability is inherently local (filesystem, local credentials, a local dev tool) and HTTP when the capability is centrally hosted or needs to serve many hosts/users from one running instance.

## When NOT to use it
Don't reach for a full MCP client/server split inside a single application where the "tool" is a function that only ever needs to run in-process for that one application, with no plausible reuse by another host - the isolation and transport machinery is overhead with no offsetting benefit there, per the same one-off case flagged in `model-context-protocol/01`.

## Key takeaways / mental model
Three roles, not two: **host** (the application, owns the model conversation and the user relationship) contains one **client** per **server** connection, each client-server pair isolated and 1:1. A server never needs to know its host; a client never needs to know another client's server. Transport (stdio for local, HTTP for remote/shared) is an implementation choice underneath that split, not a change to the roles themselves. Before any capability is used, both sides negotiate what they mutually support - historically as a persistent handshake, and as of the 2026-07-28 spec revision, via self-describing per-request metadata instead.

## Self-check questions
1. A host is connected to 4 MCP servers. One server's process crashes mid-session. Using the architecture in this lesson, explain exactly what is and is not affected - what happens to the other 3 servers' connections, and what the host has to do to recover the 4th.
2. Why does the client live inside the host rather than being a separate standalone process the host talks to? What would break about the "write the client once, reuse for any server" promise if the client itself were server-specific?
3. You're deciding whether a new internal capability should be an stdio server or an HTTP server. It needs to read a laptop-local `.env` file, but your team also wants a shared, centrally-run version for CI pipelines. Design an approach given the two-transport model in this lesson.
4. A teammate claims "since a server can't see another server's connection, MCP guarantees one server can't affect another's behavior at all." Is that true? Point to where in the architecture such an effect *could* still occur (hint: think about what the host does after it collects results from both).

## References
- [Model Context Protocol specification: Architecture](https://spec.modelcontextprotocol.io/specification/architecture/)
- [Model Context Protocol Blog: The 2026-07-28 Specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [modelcontextprotocol.io: Build an MCP server](https://modelcontextprotocol.io/docs/develop/build-server)
