---
id: model-context-protocol/04
subject: model-context-protocol
title: "Building an MCP Server: Design Choices That Matter"
slug: building-an-mcp-server
status: drafted
mastery:
seniority: senior
source: "Anthropic Engineering: Code execution with MCP - building more efficient AI agents (2026); modelcontextprotocol.io: Build an MCP server tutorial (2026); Checkmarx: MCP Security - Risks, Real Incidents & Controls (2026); Cloud Security Alliance: Agentic MCP Security Best Practices Guide (2026)"
durability: durable
prerequisites: [model-context-protocol/03]
created: 2026-08-10
updated: 2026-08-10
---

# Building an MCP Server: Design Choices That Matter

## TL;DR
Making an MCP server *work* (respond correctly to `tools/list` and `tools/call`) is the easy part; making it work *well* is a set of non-obvious design trade-offs - how many tools to expose and at what granularity, how much of an underlying API to surface directly versus wrap in higher-level workflow tools, how to keep large results from flooding the model's context, and how to fail in a way the model can actually recover from. Get these wrong and a technically spec-compliant server still produces an agent that picks the wrong tool, drowns on results, or can't recover from an error - the same failure modes `tool-use-agentic-loop/02` covers for hand-written tools, now at the scale of an entire server's worth of capabilities.

## The idea
`model-context-protocol/03` established what a tool, resource, or prompt *is*, structurally. This lesson is about the judgment calls a server author makes once the primitives are chosen: given a real underlying system (an API with 200 endpoints, a database with dozens of tables, a service with both simple reads and complex multi-step workflows), what do you actually expose, and how? These are genuinely senior-level decisions - there is rarely one right answer, only trade-offs between coverage, token cost, and model reliability, and the wrong call doesn't throw an error, it just quietly makes the agent worse at using your server. A server that is technically spec-compliant but designed without these trade-offs in mind is the MCP-scale version of the badly-described single tool from `tool-use-agentic-loop/02` - correct mechanism, unreliable behavior.

## How it works

### Coverage versus workflow tools: two philosophies, and why they trade off
A server wrapping a real API faces an immediate design fork:
- **Comprehensive coverage** - expose one MCP tool per underlying API endpoint (or close to it). This gives the agent maximum flexibility to compose operations in ways you didn't anticipate, at the cost of a large, granular tool list the model has to search through and correctly sequence itself.
- **Curated workflow tools** - expose fewer, higher-level tools that each perform a multi-step task end-to-end (e.g. one `deploy_and_verify` tool instead of separate `build`, `push`, `deploy`, `check_health` tools). This reduces the decision space the model has to search per turn (echoing the consolidation guidance in `tool-use-agentic-loop/02`) and lets you bake in the correct sequencing and error handling once, in code, rather than trusting the model to reconstruct it every time - at the cost of flexibility for tasks that don't fit the workflow you anticipated.

**Worked example.** A CI/CD platform's MCP server could expose 40 tools mirroring its REST API one-for-one (`list_pipelines`, `get_pipeline`, `create_run`, `get_run_status`, `cancel_run`, `list_artifacts`, ...), or it could expose 6 workflow tools (`run_pipeline_and_wait`, `rollback_last_deploy`, `diagnose_failed_run`, ...) that each internally call several of those 40 endpoints in a known-good sequence. The 40-tool version lets an agent handle a request the server author never anticipated (say, "list all failed runs from the last week and cancel any still queued") by composing primitives; the 6-tool version handles the 6 anticipated workflows more reliably (correct sequencing, no risk of the model forgetting to check status before declaring success) but simply cannot serve a request outside those 6 shapes without falling back to whatever primitive tools you also expose alongside them. Most production servers land on a mix: a modest set of workflow tools for the common, high-stakes paths, plus a smaller set of general primitives for flexibility - not purely one philosophy or the other.

### Context cost is not just the tool list - it's every result, every time
`tool-use-agentic-loop/02` already established that verbose descriptions cost tokens on every call a tool is *offered* in. A server-scale version of this problem is worse: every tool *result* also flows back through the model's context, on every call the tool is actually *used*, and a server wrapping a real system routinely has results far larger than a hand-written tool would. Anthropic's engineering team documented a concrete case (2026): an agent downloading a meeting transcript and attaching it to a Salesforce record had that transcript's full content pass through the model's context twice - once on the way out of the transcript tool, once on the way into the Salesforce tool - adding on the order of 50,000 tokens for a two-hour meeting, for content the model never actually needed to read, only to relay.

**Worked example - the scale of the problem, and one mitigation.** The same engineering write-up describes an agent connected to thousands of tools across many MCP servers needing "hundreds of thousands of tokens before reading a request" just to load every tool's definition up front - before a single tool call happens. Their proposed mitigation reframes the interaction: instead of every tool definition being loaded directly into context, the agent explores a filesystem-like index of available tools and loads only the definitions relevant to the current task, and instead of every intermediate result round-tripping through the model, results are filtered and processed in a code-execution environment before only the relevant summary returns to the model. Applied to a case with 5 servers' worth of typical tool use, they report reducing token usage from roughly 150,000 tokens down to roughly 2,000 - a 98.7% reduction - for the same underlying task. The lesson generalizes even without adopting that exact architecture: a server author should treat "what does a typical result look like, and how big is it" as a design question with the same seriousness as the input schema, not an afterthought.

### Designing results the model can actually use, not just parse
Beyond raw size, *what shape* a result takes affects whether the model can reason about it well on the next turn, echoing the "tool output shape is part of schema design" point from `tool-use-agentic-loop/02`, now applied to results a real backend system produces:
- Prefer **stable, human/model-readable identifiers** (slugs, names) over opaque internal IDs the model has no way to reason about or usefully reference back to the user.
- Support **filtering and pagination** on any tool that could plausibly return a large collection, rather than a single "return everything" call - both to control token cost and because a model asked to find one needle in a 500-item unfiltered dump is doing unnecessary, error-prone work a well-designed API would have done for it.
- Return **focused, task-relevant fields**, not a raw pass-through of the underlying system's full response - a server author has the context (this is a tool for an agent, not a debugging dump) that the underlying API's original designer didn't have.

### Actionable errors: designing for recovery, not just correctness
When a tool call fails - invalid input, a downstream API error, a permissions issue - the error message becomes the model's *only* signal for what to do next, exactly as a tool's description is its only signal for whether to call it in the first place (per `tool-use-agentic-loop/01`'s framing that everything the model knows about a tool is what you told it). A bare `Error: 403` or a raw stack trace gives the model nothing to act on beyond guessing or giving up. An actionable error states what went wrong in terms the model can reason about and, where possible, what to try instead - e.g. `"Cannot create issue: repo 'internal-tools' not found or not accessible with current credentials. Available repos: infra-scripts, api-gateway."` rather than a bare `404`. The difference is not cosmetic: the first version gives the model a concrete next action (retry against a listed, accessible repo, or tell the user); the second gives it nothing to work with except retrying blindly or stopping.

### Trust boundaries and least privilege, decided at design time
A server author decides, at build time, what credentials the server holds and what scope those credentials have - and that decision determines the blast radius of every subsequent failure mode, including ones outside the server's own bugs (`model-context-protocol/06` covers the trust question for servers you *didn't* build; this is the same principle from the builder's side). A server that authenticates with a broadly-scoped API token because it was convenient turns "the model picked a slightly wrong tool" or "an upstream tool description was manipulated to trigger an unintended call" (a known attack pattern as of 2026, sometimes called tool poisoning) into "attacker-controlled or model-error-driven access to everything that token can reach," rather than a narrowly contained mistake. Scoping credentials to the minimum the server's actual tools need, and requiring explicit user confirmation before any tool call that deletes data, sends external communications, spends money, or modifies infrastructure, are both design-time decisions, not something bolted on after the server ships.

## Pros
- Deliberate tool granularity (workflow tools vs. raw coverage) is a lever a server author fully controls, unlike model-side tool-selection quality, which is only ever probabilistically influenced.
- Investing in result shaping and pagination pays for itself immediately in reduced context cost and improved model reasoning quality, and compounds as the server's tool set or user base grows.
- Actionable error design turns failures from dead ends into recoverable moments, materially improving an agent's end-to-end task success rate without touching the model at all.

## Cons
- Workflow tools bake in assumptions about what the "common case" looks like; a request outside that assumption either falls back to less-reliable primitive tools or isn't served at all, and guessing wrong about which workflows are common is a real, costly design mistake.
- Result filtering and pagination add real implementation complexity to every tool, not just the ones that turn out to need it - a server author has to decide this per tool, and over-applying it to already-small results is pure overhead.
- Least-privilege credential scoping is often in direct tension with "make the server maximally useful out of the box" - a broadly scoped credential requires zero setup friction, while a properly scoped one requires the server author (or its deployer) to do real access-control work before the server is useful at all.

## Alternatives
- **A thin, mechanical wrapper generated directly from an OpenAPI spec** — fast to stand up, gives full endpoint coverage automatically, but inherits none of the judgment calls this lesson covers (no workflow consolidation, no result shaping, no tailored error messages) and typically needs significant follow-up work before it performs well in practice.
- **Code-execution-based tool access** (per the Anthropic engineering approach cited above) — instead of every tool definition and every result flowing through the model's context directly, the agent writes and runs code against a tool API, loading definitions and filtering results on demand; a more involved architecture than a conventional MCP server, but a substantially different answer to the same context-cost problem for very large tool libraries.
- **Human-in-the-loop tooling with no autonomous execution** — every tool call requires explicit human approval before it runs, trading agent autonomy for a strong safety backstop; appropriate for the highest-stakes actions regardless of how well-designed the server otherwise is, but not a substitute for good tool/result design on the vast majority of lower-stakes calls.

## When to use it
Apply this lesson's design discipline - deliberate granularity, result shaping, actionable errors, least-privilege credentials - to any MCP server meant for real, repeated production use, especially one wrapping a system with many endpoints, large result payloads, or side-effecting operations. The larger the underlying system and the higher the stakes of its actions, the more these choices matter and the more they cost to retrofit later.

## When NOT to use it
Don't over-engineer a server wrapping a tiny, low-stakes, read-only API (three endpoints, small results, nothing destructive) with heavy workflow consolidation, pagination machinery, and elaborate error taxonomies - that discipline is solving a scale and risk problem the server doesn't have yet, at a real cost in build time, mirroring the "don't over-invest" guidance in `tool-use-agentic-loop/02` for simple tool sets.

## Key takeaways / mental model
A spec-compliant server and a *good* server are different achievements. Treat four decisions as first-class design work, not implementation detail: **granularity** (coverage vs. curated workflows - and usually some of both), **result shape** (size, filtering, identifiers a model can reason about), **error design** (does a failure give the model a next action or a dead end), and **trust boundary** (what can this server's credentials actually reach, and what requires explicit human confirmation before it happens). Each is a lever you control that shapes agent reliability as much as, or more than, the model itself does.

## Self-check questions
1. You're building a server for an internal HR system with 25 API endpoints. Walk through how you'd decide which subset becomes workflow tools versus raw coverage tools, and name one concrete request you'd expect to fail gracefully under a pure-workflow-tools design.
2. A tool returns a 300-field raw JSON dump for "get employee record." Using the result-shaping guidance in this lesson, redesign its output for a common use case ("look up an employee's manager and start date"), and explain what you'd cut and why cutting it is safe.
3. Contrast a `403 Forbidden` error with an actionable error message for the same underlying failure. Walk through what the model does differently on its next turn in each case, tying your answer back to the round-trip mechanics from `tool-use-agentic-loop/01`.
4. Your server currently uses one broadly-scoped API credential for simplicity. A tool-poisoning-style attack (a manipulated tool description from an unrelated server in the same host) tricks the model into invoking one of your tools in an unintended way. Explain how credential scoping changes the actual damage this causes, even though the attack didn't originate in your server at all.
5. A teammate wants to add a `get_everything(entity_id)` mega-tool that returns the full underlying object for any entity in the system, "so the model always has what it needs." Evaluate this against both the granularity and result-shaping guidance in this lesson - what does it get right, and what failure mode does it likely reintroduce?

## References
- [Anthropic Engineering: Code execution with MCP - building more efficient AI agents](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [modelcontextprotocol.io: Build an MCP server](https://modelcontextprotocol.io/docs/develop/build-server)
- [Checkmarx: MCP Security - Risks, Real Incidents & Controls (2026)](https://checkmarx.com/learn/mcp-security-risks-real-world-incidents-and-security-controls/)
- [Cloud Security Alliance: Agentic MCP Security Best Practices Guide](https://labs.cloudsecurityalliance.org/agentic/agentic-mcp-security-best-practices-v1/)
