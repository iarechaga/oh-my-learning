---
id: model-context-protocol/01
subject: model-context-protocol
title: "Why MCP Exists: The M x N Integration Problem"
slug: why-mcp-exists
status: drafted
mastery:
seniority: mid
source: "Anthropic: Introducing the Model Context Protocol (Nov 2024); Linux Foundation press release: Formation of the Agentic AI Foundation (Dec 2025); Model Context Protocol Blog: MCP joins the Agentic AI Foundation (Dec 9, 2025)"
durability: durable
prerequisites: [tool-use-agentic-loop/01, tool-use-agentic-loop/02]
created: 2026-08-10
updated: 2026-08-10
---

# Why MCP Exists: The M x N Integration Problem

## TL;DR
`tool-use-agentic-loop/01` and `02` covered how a single model calls a single tool, given a name, a description, and a schema you wrote by hand. MCP exists because "by hand, per model, per tool" does not scale: without a shared protocol, every AI application that wants to talk to every data source or service needs its own custom integration code, producing M times N bespoke integrations for M applications and N tools. MCP replaces that grid with a single, open interface that any host can speak and any server can implement once, turning M x N integration work into M + N.

## The idea
Tool calling, as covered in the previous two lessons, tells you how a *single* model invokes a *single*, already-wired-up function. It says nothing about how that function's definition, authentication, and result-formatting code got into your application in the first place - and in a world with many AI applications (a chat client, an IDE plugin, a customer-support bot, a coding agent) and many things those applications want to reach (Slack, GitHub, a Postgres database, a company's internal CRM), somebody has to write the glue code connecting each pair.

Do that naively and you get a combinatorial problem. If your AI application wants to use N different tools, you write N integrations. If M different AI applications all want to use those same N tools, and each application has its own way of registering tools, formatting results, and handling auth, you don't get M + N integrations - you get M x N, because Slack's integration code for "Claude Desktop" is a different codebase from Slack's integration code for "Cursor," even though both are, at bottom, "let an LLM read and post Slack messages." Every new AI application that wants to reach existing tools has to reimplement every tool's integration from scratch; every new tool that wants to be reachable by existing AI applications has to write a bespoke connector for each one. This is exactly the N-to-N wiring problem software engineering has solved before with standard interfaces - ODBC standardizing database access, POSIX standardizing OS syscalls, HTTP standardizing client-server communication - and MCP is that move applied to "connecting AI applications to external context and capabilities." Anthropic's original framing (Nov 2024) was explicit about this: MCP is "a new standard for connecting AI assistants to the systems where data lives," replacing fragmented, per-integration connectors with one protocol.

## How it works

### Counting the integrations, with and without a shared protocol
Concretely: suppose there are 5 AI applications (Claude Desktop, an IDE agent, a customer-support bot, a coding CLI, a voice assistant) and 8 tools/data sources they might each want to reach (GitHub, Slack, Postgres, a filesystem, Google Drive, Jira, a company CRM, a vector database).

- **Without a shared protocol:** each application-tool pair needs its own integration, because there is no common interface either side can assume the other speaks. That is `5 x 8 = 40` distinct integrations. Add a 9th tool, and every one of the 5 applications needs a new integration written specifically for it - `+5` integrations for `+1` tool. Add a 6th application, and it needs its own integration for all 8 existing tools before it can reach any of them - `+8` integrations for `+1` application. The cost of growth is multiplicative in whichever side is smaller.
- **With a shared protocol:** each tool is wrapped once, by *someone* (its own maintainer, the tool vendor, or a third party), as an MCP server that speaks the protocol - not to any specific application, just to "MCP." Each application implements the MCP *client* side once - not per tool, just "MCP." That is `5 + 8 = 13` integration efforts total: 8 servers, 5 clients. Add a 9th tool: one new server, `+1`. Add a 6th application: one new client, `+1`. Growth is additive, in whichever side changed.

At this small scale the gap (40 vs. 13) is already real; it does not stay small. At `M = 50` applications and `N = 200` tools - a plausible size for a real ecosystem, since public MCP directories already list well over ten thousand servers as of December 2025 - the ungoverned grid is `50 x 200 = 10,000` bespoke integrations, versus `50 + 200 = 250` protocol-conformant implementations. The ratio between the two approaches (`M x N` vs. `M + N`) grows without bound as the ecosystem grows; that growing gap, not a fixed multiplier, is the actual argument for standardization.

### What each side actually builds instead
The M+N split is only real if what an application or tool builds *once* is genuinely reusable across every counterpart, which is what the protocol's client-host-server split (detailed in `model-context-protocol/02`) is designed to guarantee:
- A tool/data-source maintainer builds **one MCP server**: a program that exposes that tool's capabilities (its tools, resources, and/or prompts, per `model-context-protocol/03`) through the protocol's standard message format. It does not know or care which AI application will eventually connect to it.
- An AI-application builder builds **one MCP client integration** into their host application: the logic to discover, connect to, and invoke *any* conformant MCP server. It does not know or care which specific tools it will eventually be pointed at.
- Because both sides target the protocol rather than each other, a server written by the Postgres team and a client written by an unrelated IDE vendor interoperate correctly the first time they are pointed at each other, with zero coordination between the two teams - the entire value proposition of a shared interface standard.

### Why this needed to be an open, jointly governed standard - not one vendor's format
A protocol only delivers the M+N benefit if both sides can actually assume the other implements it, which requires the specification to be genuinely shared rather than controlled by one participant with an incentive to change it unilaterally. Anthropic originally published MCP as an open specification in November 2024; by December 9, 2025, Anthropic donated MCP's governance to the Linux Foundation as the founding project of the newly formed Agentic AI Foundation (AAIF), co-founded with Block and OpenAI and backed by Google, Microsoft, AWS, Cloudflare, and Bloomberg, specifically to keep the protocol "open, neutral, and community-driven" as it becomes shared infrastructure rather than one company's product. By that point MCP reported over 97 million monthly SDK downloads and roughly 10,000 active servers, with first-class client support already shipped in Claude, ChatGPT, Cursor, Gemini, Microsoft Copilot, and Visual Studio Code - evidence that the M+N bet had actually paid off in practice, not just in theory, which is why this subject treats MCP-the-protocol itself as a durable, entrenched capability rather than a single vendor's swappable product.

## Pros
- Converts multiplicative integration cost (M x N) into additive cost (M + N), and the gap between the two grows, not shrinks, as the ecosystem grows.
- Decouples tool builders from application builders entirely - neither has to coordinate with, or even know about, the other, as long as both conform to the same specification.
- A neutral governance body (the Linux Foundation via the AAIF) removes the risk that the shared interface becomes a single vendor's leverage point, which is what would have made competing AI application vendors reluctant to adopt it in the first place.

## Cons
- A shared protocol is necessarily a lowest-common-denominator interface; a tool with capabilities that don't map cleanly onto MCP's primitives (tools/resources/prompts, `model-context-protocol/03`) may still need bespoke, non-MCP integration for its most unusual features.
- Someone still has to write and maintain each MCP server - the protocol eliminates the *M x N multiplication*, it does not eliminate the *N* server-authoring effort itself, and a low-quality or unmaintained server is exactly as unreliable as a low-quality bespoke integration would have been.
- Standardization takes time to pay off: for a single application talking to a single bespoke internal tool it will only ever use once, writing one direct integration is genuinely simpler and faster than standing up an MCP server and client for a "market" of one.

## Alternatives
- **Bespoke per-pair integrations (the pre-MCP default)** — direct, custom code between one application and one tool; faster to ship for a single pair, but is exactly the M x N cost this lesson quantifies once more than a couple of applications or tools are involved.
- **A single vendor's proprietary plugin/connector format** — e.g. an application-specific plugin API that only that application's ecosystem can use; solves discovery and some standardization within one vendor's world, but does not eliminate the M x N problem across vendors, and concentrates governance risk in one company rather than a neutral body.
- **Agent-to-agent protocols (covered in `landscape-snapshot/03`, a later subject)** — MCP standardizes an agent-to-tool/data connection; a separate class of protocols standardizes agent-to-agent communication, a related but distinct interoperability problem MCP does not solve by itself.

## When to use it
Reach for MCP (over a bespoke integration) as soon as more than one AI application might reasonably want to use a tool, or more than one tool might reasonably need to be reachable from an application you're building - which in practice is most production agentic systems, since even a single internal tool today often needs to be reachable from a chat assistant, a CLI agent, and an IDE plugin within a year. Building to the shared protocol from the start avoids having to retrofit standardization later once bespoke integrations have already proliferated.

## When NOT to use it
Skip MCP for a genuinely one-off, single-pair integration with no realistic prospect of reuse - a throwaway script that calls one internal API for one internal tool, where standing up a server, handling its lifecycle, and implementing a client is pure overhead compared to a direct function call. The M+N argument only pays off once M or N is meaningfully greater than one; for M=1, N=1, direct integration is strictly simpler.

## Key takeaways / mental model
Without a shared protocol, connecting **M** applications to **N** tools costs **M x N** bespoke integrations, and that cost grows multiplicatively as either side grows. A shared protocol lets each tool be wrapped once (a server) and each application implement the client side once, dropping the cost to **M + N** - additive growth instead of multiplicative. MCP is that shared protocol for the agent-to-tool/data connection, made credible as a long-term bet by neutral, cross-vendor governance (Linux Foundation / AAIF) rather than single-vendor control.

## Self-check questions
1. A startup has 3 internal AI tools (a support bot, an internal Slack bot, and a code-review agent) and wants each to reach 6 internal systems (a ticketing system, a wiki, a database, two SaaS tools, and an internal API). Calculate the integration cost with and without a shared protocol, and say at what combination of applications and tools the difference stops being worth the overhead of standardizing.
2. A colleague says "MCP just means every tool needs a wrapper, so it hasn't actually saved any work - the total number of integration efforts is basically the same." Where exactly does this reasoning go wrong? Use the M x N vs. M + N framing to correct it.
3. Explain, in terms of the M x N problem, why it mattered that MCP was donated to a neutral foundation rather than remaining fully controlled by the company that created it - what specifically would have been at risk if it hadn't been?
4. Your team is deciding whether to build a bespoke direct integration or an MCP server for a tool that, today, only one internal agent uses. What question would you ask about the next 12 months before deciding, and why does that question matter more than the tool's current usage?

## References
- [Anthropic: Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol)
- [Linux Foundation: Announces the Formation of the Agentic AI Foundation (AAIF)](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)
- [Model Context Protocol Blog: MCP joins the Agentic AI Foundation](https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/)
- [Anthropic: Donating the Model Context Protocol and establishing the Agentic AI Foundation](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)
