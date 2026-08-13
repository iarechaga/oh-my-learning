---
id: landscape-snapshot/03
subject: landscape-snapshot
title: "Interoperability Protocols Beyond MCP: What Else Exists Today"
slug: interoperability-protocols-beyond-mcp
status: drafted
mastery:
seniority: mid
source: "Linux Foundation, A2A Protocol Surpasses 150 Organizations press release (2026); Google Open Source Blog, A year of open collaboration: Celebrating the anniversary of A2A (2026); IBM, What is Agent Communication Protocol (ACP)? (2026); Boldare, ACP Explained: AI Agent Orchestration in 2026 (2026); Zylos Research, Agent Interoperability Protocols 2026: MCP, A2A, ACP and the Path to Convergence (2026); Google Cloud Blog, Announcing Agent Payments Protocol (AP2) (2025); Crossmint, Agentic payments protocols compared (2026); Medium (Vishal Mysore), A2A, MCP, AG-UI, A2UI: The Essential 2026 AI Agent Protocol Stack (2026); agent-network-protocol.com, ANP - Agent Network Protocol (2026)"
durability: perishable
next_review: 2026-11
prerequisites: [model-context-protocol/03]
created: 2026-08-10
updated: 2026-08-10
---

# Interoperability Protocols Beyond MCP: What Else Exists Today

## TL;DR
`model-context-protocol/03` covers MCP's own primitives - how one client and one server exchange tools, resources, and prompts. MCP solves exactly one layer of the interoperability problem: agent-to-tool connectivity. As of August 2026, a small set of other protocols solve adjacent layers that MCP was never designed for - agent-to-agent coordination across organizational boundaries (A2A, now the clear leader, with the once-competing ACP having merged into it), UI-facing streaming (AG-UI), and agent-initiated payments (AP2 and x402) - while a fully decentralized alternative (ANP) remains early-stage and not yet enterprise-adopted.

> **Snapshot date: August 2026.** This lesson is tagged `durability: perishable` and reviewed quarterly (`next_review: 2026-11`) - treat every specific product name, version, and number below as accurate as of the date above, not as a permanent fact. See `agent-docs/fast-moving-domain-policy.md`.

## The idea
`model-context-protocol/03` establishes that MCP standardizes three primitives - tools, resources, prompts - for one client talking to one server, with each primitive assigned a different controller (model, application, or user). That framing answers "how does an agent get context and take actions" but deliberately leaves several other questions open: how do two independent *agents*, built by different teams or vendors, discover and talk to each other; how does an agent stream rich, structured updates to a human-facing UI in real time; and how does an agent actually pay for something. Each of those is a different interoperability problem, and as of 2026 each has at least one protocol converging toward "the" answer - though, as with any live standards process, some of that convergence is settled and some is still contested.

The single most important structural fact for a practitioner today: these protocols are not competitors to MCP, and mostly not competitors to each other either - they occupy different layers of the same stack. Confusing "which protocol should I use" with "which protocol is best" is the most common mistake; the right question is almost always "which layer of the problem am I solving."

## How it works

### Layer 1 recap: MCP handles agent-to-tool (not covered further here)
Per `model-context-protocol/03`, MCP standardizes tools (model-invoked), resources (application-controlled context), and prompts (user-invoked templates) between one client and one server. Nothing below replaces this layer; everything below sits above or beside it.

### Layer 2: agent-to-agent coordination - A2A, and the now-deprecated ACP
**A2A (Agent2Agent Protocol)**, announced by Google in April 2025 and donated to the Linux Foundation in mid-2025, is the clear leader for cross-agent, cross-vendor coordination as of 2026. It reached a stable 1.0 spec in April 2026 with enterprise features including Signed Agent Cards (cryptographic identity verification for agents) and multi-tenancy support, and reports over 150 supporting organizations at its one-year mark, with deep integration across all three major clouds (Azure AI Foundry, Bedrock AgentCore, Google Cloud) and SDKs in Python, JavaScript, Java, Go, and .NET. A2A solves the problem MCP does not: letting an agent built by one team hand a task, or coordinate on a task, with an agent built by a different team or company, without either side needing the other's internal tool implementation.

**ACP (Agent Communication Protocol)**, originally an IBM/BeeAI project pursuing a REST-native alternative to A2A, is no longer an independent option: IBM announced in September 2025 that ACP would merge into A2A under the Linux Foundation, its repo is now archived, and 2026 practitioner guidance is explicit that "there is no reason to adopt ACP today" - new projects should go straight to A2A. This is included here specifically as a worked example of the churn this subject exists to track: a protocol that was actively recommended in comparisons as recently as early 2025 was fully deprecated within about a year.

**Caveat on adoption depth:** multiple 2026 sources caution that supporter counts and integration announcements do not by themselves establish how many teams are running A2A in *production* at meaningful scale - the protocol has legitimate formal governance and real production deployments in specific verticals (supply chain, financial services, insurance, IT operations), but "widely supported" and "widely and deeply used" are different claims, and the sources reviewed for this lesson do not fully resolve the gap between them.

### Layer 2 (decentralized alternative): ANP
**ANP (Agent Network Protocol)** takes a structurally different approach from A2A: rather than a protocol brokered through named organizations and centrally-issued identity, ANP builds decentralized authentication using W3C Decentralized Identifiers (DIDs) and JSON-LD graphs, aiming for open-network agent discovery without relying on any centralized identity system - positioning itself, in its own white paper submitted to the W3C in November 2025, as "the HTTP of the Agentic Web era." As of 2026, sources describe ANP as technically compelling but not yet ecosystem-ready, lagging well behind A2A in enterprise adoption, with A2A's Signed Agent Cards covering a more centralized but currently more practical slice of the same trust problem ANP is trying to solve in a fully decentralized way.

### Layer 3: agent-to-UI streaming - AG-UI
**AG-UI (Agent-User Interaction Protocol)**, released by CopilotKit in early 2025, solves a problem neither MCP nor A2A addresses: how an agent streams rich, structured updates - partial text, tool-call results, UI-specific state - to a human-facing frontend in real time, standardizing what teams previously hand-built with ad hoc WebSocket or server-sent-event plumbing. Where MCP is about an agent reaching outward to tools and A2A is about one agent reaching sideways to another agent, AG-UI is about an agent reaching "upward" to the human-facing interface that displays its work.

### Layer 4: agent-initiated payments - AP2 and x402
Two protocols address a problem category MCP, A2A, and AG-UI all leave open: an agent that needs to actually *pay* for something.
- **AP2 (Agent Payments Protocol)**, from Google with over 60 partners, defines the trust and authorization layer for agent-led payments using cryptographically signed mandates, and supports both traditional card payments and, via its x402 extension, crypto payments.
- **x402**, created by Coinbase, revives the long-dormant HTTP 402 status code to enable instant stablecoin micropayments over plain HTTP, purpose-built for machine-to-machine transactions and API monetization; it has notable production traction as of 2026 (Stripe integrated x402 support on Base in February 2026, Cloudflare supports x402 transactions), and a 2026 A2A x402 extension, built with Coinbase, Ethereum Foundation, and MetaMask, provides a production-ready path for agent-based crypto payments specifically within A2A-coordinated systems.

These two protocols are described in 2026 sources as complementary rather than competing: a real system might use AP2 for authorization/consent and x402 for the actual machine-to-machine settlement.

### Comparison table

| Protocol | Layer solved | Status as of Aug 2026 | Relationship to MCP |
| --- | --- | --- | --- |
| MCP (Anthropic) | Agent-to-tool | Established de facto standard | (baseline, not "beyond") |
| A2A (Google, now Linux Foundation) | Agent-to-agent | Stable 1.0, broad cloud integration, 150+ supporting orgs | Complementary layer, not competing |
| ACP (IBM/AGNTCY) | Agent-to-agent (REST-native) | **Deprecated** - merged into A2A, repo archived | Superseded, do not adopt new |
| ANP | Agent-to-agent (decentralized) | Early-stage, technically compelling, not enterprise-ready | Complementary layer, competing with A2A specifically |
| AG-UI (CopilotKit) | Agent-to-UI | Established for frontend streaming use cases | Complementary layer, not competing |
| AP2 (Google + 60 partners) | Payment authorization | Actively adopted, multiple protocol extensions | Complementary layer, not competing |
| x402 (Coinbase) | Payment settlement (crypto) | Real production traction (Stripe, Cloudflare integrations) | Complementary layer, not competing |

## Pros
- Each protocol above targets a genuinely distinct layer, so adopting one rarely forecloses adopting another - a system can legitimately run MCP for tools, A2A for cross-agent coordination, AG-UI for the frontend, and AP2/x402 for payments simultaneously.
- The A2A/ACP consolidation is a concrete, verifiable example of the standards ecosystem actually converging rather than permanently fragmenting - useful evidence against the pessimistic assumption that every new protocol just adds permanent noise.
- Linux Foundation stewardship of both MCP-adjacent (A2A, formerly ACP) governance gives practitioners a single place to track the agent-to-agent layer's evolution going forward, lowering the cost of staying current.

## Cons
- The pace of churn is real, not hypothetical: ACP was a live recommendation in comparisons roughly a year before this lesson's snapshot date and is fully archived now - the same could happen to any protocol named here before `next_review`.
- "Number of supporting organizations" and "GitHub stars" are, as of 2026 sources, explicitly called out as insufficient signals of production depth - a protocol can look adopted in press coverage while remaining thin in actual production usage, and the sources available for this lesson could not fully close that gap.
- Running multiple protocols in one system (MCP + A2A + AG-UI + a payments protocol) is real integration and operational surface area, even when each protocol individually is well-specified - the "just add another protocol" framing understates the cost of maintaining four separate specs' worth of client/server code.

## Alternatives
- **Building bespoke point-to-point integrations instead of adopting any standard protocol** - still defensible for a small, fixed set of internal agents under one team's control, where the coordination overhead of a general protocol isn't justified; becomes a liability the moment a third party's agent needs to interoperate.
- **Waiting for further consolidation before adopting an agent-to-agent protocol** - reasonable for teams with low urgency and Recent history (the ACP deprecation) as a reason for caution; the cost is forgoing A2A's current, real production integrations (Azure AI Foundry, Bedrock AgentCore, Google Cloud) in the meantime.
- **ANP's fully decentralized model instead of A2A's more centralized one** - preferable specifically for use cases that cannot tolerate any centralized identity broker (open agent marketplaces, adversarial-trust environments), at the cost of adopting a protocol sources describe as not yet ecosystem-ready.

## When to use it
Reach for this lesson when deciding which *additional* protocol, beyond MCP, a system actually needs: agent-to-agent coordination across an organizational boundary points to A2A (not ACP, which is deprecated); a human-facing frontend that needs structured live updates points to AG-UI; a system where an agent needs to authorize or settle a payment points to AP2 and/or x402. Check each protocol's status row in the comparison table first - this is precisely the kind of decision where "was this true a year ago" and "is this true now" can diverge.

## When NOT to use it
Do not adopt ACP for any new project - it is explicitly deprecated as of 2026, and its own maintainers direct new adopters to A2A. Do not treat "beyond MCP" protocols as a checklist to adopt uniformly; a system that only ever talks to its own tools has no agent-to-agent, UI-streaming, or payment problem to solve, and adding any of these protocols without a corresponding real need only adds integration surface area for no benefit, contradicting `model-context-protocol/03`'s point that different problems deserve different, deliberately-chosen primitives rather than one-size-fits-all machinery. Do not cite this lesson's "150+ supporting organizations" or similar adoption figures as proof of deep production usage without independently verifying your specific vendor's or partner's actual production maturity with that protocol - 2026 sources reviewed for this lesson explicitly flag that headline adoption counts and production depth are different claims.

## Key takeaways / mental model
MCP solves agent-to-tool; everything in this lesson solves a different layer - agent-to-agent (A2A, with ACP deprecated into it and ANP as an early-stage decentralized alternative), agent-to-UI (AG-UI), or agent-to-payment (AP2, x402). When evaluating whether to adopt a new protocol, first identify which layer it claims to solve and check whether you already have an unmet need at that layer - and always check whether the specific protocol under discussion is still the live recommendation or has already gone the way ACP did.

## Self-check questions
1. A colleague proposes using ACP for a new cross-vendor agent-coordination project because "it's REST-native and simpler than A2A." What do you tell them, and why does this exact scenario matter for how this subject is maintained?
2. Explain, in one sentence each, what layer MCP, A2A, AG-UI, and AP2/x402 each solve, and why a system can legitimately need all four at once without redundancy.
3. ANP and A2A both address agent-to-agent coordination, but take structurally different approaches to identity and trust. What is that structural difference, and what does it predict about which use cases would prefer ANP even while it remains less enterprise-ready than A2A?
4. Sources for this lesson explicitly note that "150+ supporting organizations" does not, by itself, establish production depth. Propose one concrete way you'd verify a protocol's actual production maturity before committing your team's architecture to it.

## References
- Linux Foundation, "A2A Protocol Surpasses 150 Organizations, Lands in Major Cloud Platforms, and Sees Enterprise Production Use in First Year" (2026), https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year
- Google Open Source Blog, "A year of open collaboration: Celebrating the anniversary of A2A" (2026), https://opensource.googleblog.com/2026/04/a-year-of-open-collaboration-celebrating-the-anniversary-of-a2a.html
- IBM, "What is Agent Communication Protocol (ACP)?" (2026), https://www.ibm.com/think/topics/agent-communication-protocol
- Boldare, "ACP Explained: AI Agent Orchestration in 2026" (2026), https://www.boldare.com/blog/agent-communication-protocol-acp-explained-what-it-is-and-why-it-matters/
- Zylos Research, "Agent Interoperability Protocols 2026: MCP, A2A, ACP and the Path to Convergence" (2026), https://zylos.ai/research/2026-03-26-agent-interoperability-protocols-mcp-a2a-acp-convergence/
- Zylos Research, "Agent-to-Agent Interoperability Protocols: A2A, ACP, and ANP in Production" (2026), https://zylos.ai/research/2026-04-18-agent-to-agent-interoperability-protocols/
- Medium (Vishal Mysore), "A2A, MCP, AG-UI, A2UI: The Essential 2026 AI Agent Protocol Stack" (2026), https://medium.com/@visrow/a2a-mcp-ag-ui-a2ui-the-essential-2026-ai-agent-protocol-stack-ee0e65a672ef
- ag-ui-protocol/ag-ui, GitHub repository (accessed Aug 2026), https://github.com/ag-ui-protocol/ag-ui
- agent-network-protocol.com, "ANP - Agent Network Protocol" (accessed Aug 2026), https://agent-network-protocol.com/
- Google Cloud Blog, "Announcing Agent Payments Protocol (AP2)" (2025), https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol
- Crossmint, "Agentic payments protocols compared: Which is best for your AI agents? (MPP, ACP, AP2, x402)" (2026), https://www.crossmint.com/learn/agentic-payments-protocols-compared
- `agentic-engineering/model-context-protocol/lessons/03-mcp-primitives.md`, this repository - the durable MCP-primitives lesson this lesson supplies adjacent-protocol context for
