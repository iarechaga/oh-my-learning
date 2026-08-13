# Model Context Protocol & Agent Interoperability - Subject Summary

A comprehensive recap of this subject, concept by concept.

**Progress note:** all 7 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom
(dependency-ordered).

## Concepts

- **[model-context-protocol/01] Why MCP exists** - without a shared protocol, M
  applications and N tools need M x N bespoke integrations; MCP replaces that grid
  with a single open interface any host can speak and any server can implement once,
  turning M x N into M + N. ([lesson](lessons/01-why-mcp-exists.md))
- **[model-context-protocol/02] MCP architecture** - three roles, not two: a host (the
  AI application), one client per connection living inside the host, and servers that
  expose capabilities - the split that lets a server stay ignorant of which host it's
  plugged into. ([lesson](lessons/02-mcp-architecture.md))
- **[model-context-protocol/03] MCP primitives** - tools (model-invoked), resources
  (application-controlled, read-only), and prompts (user-triggered templates) - three
  different trust models for three different problems; picking the wrong one creates
  real friction. ([lesson](lessons/03-mcp-primitives.md))
- **[model-context-protocol/04] Building an MCP server** - making a server spec-
  compliant is easy; making it work well means non-obvious trade-offs in tool
  granularity, result size against the context budget, and recoverable error design.
  ([lesson](lessons/04-building-an-mcp-server.md))
- **[model-context-protocol/05] Authorization and statelessness in agent protocols** -
  MCP treats a server as an OAuth 2.1 resource server and a connection as self-
  contained requests rather than a sticky session, both so a server can run as
  ordinary horizontally-scaled infrastructure.
  ([lesson](lessons/05-authorization-and-statelessness-in-agent-protocols.md))
- **[model-context-protocol/06] Discovering and trusting third-party MCP servers** -
  installing a third-party server is running someone else's code inside your agent's
  loop; registry verification answers authenticity, not behavioral trustworthiness -
  tool descriptions and results can still be engineered to hijack an agent.
  ([lesson](lessons/06-discovering-and-trusting-mcp-servers.md))
- **[model-context-protocol/07] MCP in a multi-agent system** - with multiple agents,
  each needing its own bespoke integrations recreates the M x N problem at a larger
  scale; a shared tooling layer any agent can connect to solves it the same way, once,
  reused everywhere. ([lesson](lessons/07-mcp-in-a-multi-agent-system.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on the concepts
rated `shaky` or `not-yet`.
