# Model Context Protocol & Agent Interoperability

Why a standard protocol for connecting agents to tools and data emerged, how MCP is
architected (hosts, clients, servers), its core primitives, and what it takes to build
a server, secure it, and trust one you didn't build. Closes with the wider
interoperability picture beyond MCP specifically.

**Sources:** the Model Context Protocol specification and its governing body's
documentation, primary vendor documentation on MCP adoption, and dated practitioner
write-ups. No single canonical book exists for this field. See each lesson's `source:`
front matter for its specific citations, and
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`model-context-protocol/<NN>`* (e.g. *"discuss `model-context-protocol/03`"*). Concepts
are ordered by dependency, so top-to-bottom is a sensible reading order.

**Seniority baseline:** mid (lessons range mid->staff).

**Durability:** durable - MCP itself is treated as an entrenched capability (governed
under the Linux Foundation, adopted across major model providers), not a fad; concrete
spec-version and ecosystem details are dated inline and the current alternative-protocol
landscape lives in `landscape-snapshot/03`. See
[agent-docs/fast-moving-domain-policy.md](../../agent-docs/fast-moving-domain-policy.md)
for the judgment call this rests on.

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Why MCP exists: the M×N integration problem | mid | drafted | — | — | [lesson](lessons/01-why-mcp-exists.md) | — |
| 02  | MCP architecture: hosts, clients, and servers | mid | drafted | — | — | [lesson](lessons/02-mcp-architecture.md) | — |
| 03  | MCP primitives: tools, resources, and prompts | mid | drafted | — | — | [lesson](lessons/03-mcp-primitives.md) | — |
| 04  | Building an MCP server: design choices that matter | senior | drafted | — | — | [lesson](lessons/04-building-an-mcp-server.md) | — |
| 05  | Authorization and statelessness in agent protocols: why it matters for scaling | senior | drafted | — | — | [lesson](lessons/05-authorization-and-statelessness-in-agent-protocols.md) | — |
| 06  | Discovering and trusting third-party MCP servers | senior | drafted | — | — | [lesson](lessons/06-discovering-and-trusting-mcp-servers.md) | — |
| 07  | MCP in a multi-agent system: shared tooling across agents | staff | drafted | — | — | [lesson](lessons/07-mcp-in-a-multi-agent-system.md) | — |

**Status:** `drafted` (lesson written) · `discussed` (at least one discussion held).
**Mastery:** `solid` · `partial` · `shaky` · `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Cross-subject prerequisites**: `01` builds on `tool-use-agentic-loop/01-02`; `07`
depends on `multi-agent-orchestration/02` and is best read after it. All named per
lesson in front matter and prose.
