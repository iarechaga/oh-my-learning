---
id: model-context-protocol/07
subject: model-context-protocol
title: "MCP in a Multi-Agent System: Shared Tooling Across Agents"
slug: mcp-in-a-multi-agent-system
status: drafted
mastery:
seniority: staff
source: "Pluralsight: Multi-agent systems with MCP - Building AI teams that share tools (2026); Speakeasy: A practical guide to the architectures of agentic applications (2026); Model Context Protocol Blog: The 2026-07-28 Specification (2026); TrueFoundry: Multi-Agent System with MCP - A Complete Guide (2026)"
durability: durable
prerequisites: [model-context-protocol/03]
created: 2026-08-10
updated: 2026-08-10
---

# MCP in a Multi-Agent System: Shared Tooling Across Agents

## TL;DR
When more than one agent exists in a system, each agent needing its own bespoke integration to every tool, resource, and data source recreates the M×N problem lesson 01 solved for a single agent - except now M is agents times integrations, not just clients times integrations. MCP's answer is unchanged in kind: a shared tooling layer that any agent in the system can connect to as a client, so tool integrations are built once and reused across every agent that needs them, rather than once per agent. This lesson stands on its own using only what tool-use-agentic-loop and lessons 01-04 already established; it connects forward to - but does not require having read - a separate `multi-agent-orchestration` subject that covers how agents coordinate with each other, which is a different problem from what this lesson covers.

## The idea
Everything in lessons 01 through 04 was framed around a single agent connecting to MCP servers. Nothing about MCP's architecture - hosts, clients, servers, primitives - actually assumes there's only one agent in the picture, and it's worth being explicit about why, because the moment a system has multiple agents (a research agent and a writing agent, a triage agent and several specialist agents it delegates to, a fleet of agents each handling a different customer), a new version of the original M×N problem appears if tooling isn't shared deliberately.

Recall lesson 01's framing: without a shared protocol, each pairing of (agent, tool) needs its own bespoke integration, and the number of integrations grows as agents × tools rather than agents + tools. That math doesn't change when "agent" specifically means "one of several agents in a multi-agent system" instead of "the one agent in a single-agent system" - if a system has 5 agents and each needs its own hand-rolled connector to the same internal ticketing API, the same CRM, and the same file-search tool, that's 15 bespoke integrations to build and maintain, most of it duplicate work, even though there are really only 3 distinct capabilities involved.

The durable architectural point is: **MCP servers are a shared, external capability layer, not something owned by any one agent.** An MCP server exposing "search the company wiki" doesn't know or care whether it's being called by a single-agent coding assistant, a research agent inside a larger pipeline, or three different specialist agents in the same multi-agent system - it's a stable service boundary (lesson 02's host/client/server architecture) that any conforming client can connect to. This is precisely analogous to how a shared internal REST API, or a shared database, serves many services in an ordinary microservices architecture without each service needing its own private copy of the data or logic behind it - the same "shared infrastructure, not point-to-point wiring" principle, applied to tool access for agents specifically.

## How it works

### The scaling problem, restated for multiple agents
Picture a customer-support system with three agents, each with a distinct job: a **triage agent** (reads an incoming ticket and classifies it), a **billing agent** (handles account and payment questions), and an **escalation agent** (drafts a summary for a human when a ticket needs to be escalated). All three plausibly need to look up the customer's account record. Without a shared tooling layer, each agent's own harness would need its own bespoke connector to the account-lookup system - three separate integrations to build, test, version, and keep working when that system's API changes, even though the underlying capability ("look up an account by ID") is identical every time.

With a shared MCP server exposing `lookup_account(account_id)`, all three agents' hosts connect to the *same* server as MCP clients (lesson 02's host-client-server architecture applies per agent, not once for the whole system - each agent's host still runs its own client that opens its own connection). The integration - talking to the account system's actual API, handling its auth, its rate limits, its schema quirks - is built once, inside the server. Every agent that needs account lookups gets it by connecting to that one server, the same way three different microservices in an ordinary backend would each call the same internal API rather than each reimplementing account lookup against the underlying database directly.

```
Without a shared tooling layer          With a shared MCP server
-----------------------------           -----------------------------
Triage agent  --- bespoke ---> Accounts  Triage agent  ---\
Billing agent --- bespoke ---> Accounts  Billing agent ----+--> MCP server
Escalation    --- bespoke ---> Accounts  Escalation    ---/      (Accounts)
                                                                     |
3 integrations to build & maintain                          1 integration,
for 1 real capability                                        3 clients reuse it
```

### Worked example: what changes (and what doesn't) when a new agent is added
Suppose the same support system later adds a fourth agent - a **refunds agent** that also needs account lookups, plus a new capability, `check_payment_method(account_id)`, that none of the other three agents need.

- **Account lookup**: the refunds agent's host simply connects as another client to the *existing* accounts MCP server. Nothing about that server changes. This is the direct payoff of the shared layer: adding a new agent that needs an existing capability costs a connection, not a new integration.
- **Payment-method check**: this is new capability, so it genuinely requires new server-side work - but the design choice that matters is *where* that work goes. Adding it as a new tool on the existing accounts server (if it's a closely related capability, same underlying system, same trust boundary) versus standing up a new, narrowly-scoped server for it (if it touches a more sensitive system, like lesson 04's discussion of designing tool granularity and lesson 06's least-privilege-by-server-selection) is exactly the same server-design judgment call lessons 04-06 already cover - multi-agent systems don't introduce a new kind of decision here, they just raise the stakes of getting it right, because more agents now depend on however that decision plays out.

### Why per-agent duplication is worse, not just redundant, at multi-agent scale
Duplicated integrations in a multi-agent system aren't merely wasted engineering effort - they create a specific new failure mode: **drift**. If the triage agent's bespoke accounts connector and the billing agent's bespoke accounts connector are two separate pieces of code, they can silently diverge - one gets updated when the underlying account system changes its schema, the other doesn't, and now two agents in the same system disagree about what a customer's account record looks like, with no single place to find or fix the discrepancy. A shared MCP server collapses this to one place: when the underlying account system changes, the server is updated once, and every agent connected to it picks up the fix simultaneously and consistently, the same way fixing a bug in a shared library propagates to every caller at once, versus fixing it in one of several forked copies and hoping someone remembers to port the fix everywhere else.

This connects to the authorization model from lesson 05 in a way that specifically matters once multiple agents are involved: because tokens are audience-bound to a specific MCP server (not to a specific agent), the accounts server can enforce one consistent access policy regardless of which agent - triage, billing, escalation, or refunds - is asking, rather than trusting each agent's own harness to enforce that policy correctly and consistently on its own. Centralizing the capability also centralizes where its access rules live and are actually enforced.

### Where this connects to multi-agent orchestration (without requiring it)
A separate concern - not covered by this lesson, and covered instead by the `multi-agent-orchestration` subject once it exists - is how agents in a system coordinate *with each other*: how a triage agent hands a ticket off to a billing agent, how results flow back to whichever agent needs them next, how a supervising agent decides which specialist to invoke. That is a fundamentally different problem from what this lesson addresses. This lesson is about agents sharing access to *external* capabilities (tools, resources, data sources outside the agent system); orchestration is about agents communicating and coordinating *with each other* inside the system. A system can have excellent shared MCP tooling and terrible agent-to-agent coordination, or vice versa - they're orthogonal design axes, and reading this lesson gives you the shared-tooling half of a multi-agent architecture even before the orchestration half has been written up. When `multi-agent-orchestration/02` exists, the natural next step is seeing how a shared MCP layer interacts with whatever coordination pattern that subject settles on - but nothing here depends on that subject's specific answers.

## Pros
- One integration serves every agent that needs the capability, eliminating the agents-times-tools duplication that would otherwise recreate lesson 01's M×N problem at the multi-agent level.
- A single enforcement point for access policy (lesson 05's audience-bound tokens, lesson 04's scoping) means every agent connected to a server is subject to the same, consistently-applied rules, rather than each agent's harness having to get authorization right independently.
- Fixing or updating the underlying capability happens once, and every connected agent benefits simultaneously - no drift between agents that should agree on the same data or behavior.
- New agents that need an existing capability are cheap to onboard - a connection, not a new integration.

## Cons
- A shared server becomes a shared dependency: if it goes down or is misbehaving, every agent that relies on it is affected simultaneously, rather than the blast radius being contained to whichever agent had the bespoke bug.
- Centralizing a capability behind one server can create a throughput bottleneck if many agents call it heavily and concurrently - the server's own scaling story (lesson 05's stateless-core design) has to actually hold up under multi-agent load, not just single-agent load.
- Getting server granularity wrong (one server trying to serve capabilities that different agents should have very different trust levels for) can quietly weaken the least-privilege story from lesson 06 - a server built for one agent's needs and then reused by a higher-risk agent may end up over-scoped for that second use case.
- This lesson describes a durable architectural principle, but the concrete mechanics of how agents *discover which shared servers exist* and *coordinate around shared state* in a large multi-agent deployment are still an actively evolving area of practice as of 2026 - treat the specifics as less settled than MCP's core client-server model itself.

## Alternatives
- **Give each agent its own private tool integrations** — the simplest thing to reason about for a system with very few agents and very little capability overlap, but reintroduces the M×N problem the moment agents or shared capabilities grow, and risks the drift failure mode described above.
- **A single "super-agent" with all capabilities instead of multiple specialized agents** — sidesteps the shared-tooling question entirely by not having multiple agents in the first place; trades away whatever benefits led to a multi-agent design (separation of concerns, independent scaling, focused context per agent) for architectural simplicity - a valid choice when those benefits don't actually apply to the system in question.
- **Agent-to-agent protocols (e.g., A2A) alongside MCP** — addresses the orthogonal orchestration problem named above (agents talking to each other) rather than the shared-tooling problem this lesson covers; the two are frequently used together, not as substitutes for each other, and the current interoperability landscape connecting them is covered in `landscape-snapshot/03`.

## When to use it
Design a shared MCP tooling layer whenever more than one agent in a system needs access to the same underlying capability - which is the common case the moment a system has more than one agent at all, since agents rarely need entirely disjoint tool sets. This is also the moment to apply lesson 04's server-design judgment deliberately, because a server built for shared, multi-agent use has to hold up under more concurrent load and more varied trust requirements than a server built for one agent's private use.

## When NOT to use it
For a system with genuinely one agent, or with multiple agents whose tool needs never overlap at all, building a shared layer ahead of any actual second consumer is premature abstraction - lesson 01's cost-benefit reasoning about when M×N actually becomes painful still applies; don't build shared infrastructure for a duplication problem that doesn't yet exist. And don't reach for a shared MCP server as a substitute for actual agent-to-agent coordination - if what a system needs is agents handing off tasks and results to each other, that's the orchestration problem this lesson explicitly does not solve, and forcing it through a shared tool server produces an awkward, indirect version of coordination that a proper orchestration pattern would handle directly.

## Key takeaways / mental model
A multi-agent system is still, from any one agent's point of view, just an agent connecting to MCP servers exactly as lessons 02-04 described - the only thing that changes is that the *same* server now has *multiple* clients, one per agent that needs it, instead of one. Treat MCP servers as shared external infrastructure - built once, enforced consistently, reused freely - the same instinct that leads to shared internal APIs and shared databases in ordinary backend systems, applied to the tools and data sources an agent system depends on. Keep this cleanly separate in your head from agent-to-agent orchestration: sharing a tool is not the same problem as agents talking to each other, even though both show up together in most real multi-agent systems.

## Self-check questions
1. A system has four agents, each currently maintaining its own bespoke connector to the same internal search API. Explain, in M×N terms, what a shared MCP server changes here and what it does not change.
2. Two agents in a multi-agent system disagree about a customer's current account status - one says active, one says suspended - even though both claim to be reading from "the same" underlying system. Using the drift failure mode from this lesson, what architectural choice most likely caused this, and how would a shared MCP server prevent it going forward?
3. Explain why "agents sharing an MCP tooling layer" and "agents coordinating with each other via an orchestration pattern" are described in this lesson as orthogonal problems rather than the same problem. Give an example of a system that has one without the other.
4. A shared accounts MCP server, originally built for a low-risk triage agent, is now being connected to by a new, higher-privilege refunds agent that needs broader account-modification capability. What risk does this reuse introduce, and which earlier lesson's principle should govern the fix?
5. A colleague argues that a single "super-agent" with every capability built in would avoid the shared-tooling design problem entirely. Under what conditions would you agree that's the right call, and under what conditions would you push back?

## References
- [Pluralsight: Multi-agent systems with MCP - Building AI teams that share tools](https://www.pluralsight.com/resources/blog/ai-and-data/multi-agent-systems-mcp-AI)
- [Speakeasy: A practical guide to the architectures of agentic applications](https://www.speakeasy.com/mcp/using-mcp/ai-agents/architecture-patterns)
- [Model Context Protocol Blog: The 2026-07-28 Specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [TrueFoundry: Multi-Agent System with MCP - A Complete Guide](https://www.truefoundry.com/blog/multi-agent-system-with-mcp)
