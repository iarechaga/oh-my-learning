---
id: model-context-protocol/03
subject: model-context-protocol
title: "MCP Primitives: Tools, Resources, and Prompts"
slug: mcp-primitives
status: drafted
mastery:
seniority: mid
source: "Model Context Protocol specification: server-concepts docs (modelcontextprotocol.io, 2026); Speakeasy: What are MCP resources? (2026); Speakeasy: What are MCP prompts? (2026); Stacktree: MCP tools vs resources vs prompts - a decision table (2026)"
durability: durable
prerequisites: [model-context-protocol/02]
created: 2026-08-10
updated: 2026-08-10
---

# MCP Primitives: Tools, Resources, and Prompts

## TL;DR
A server's capabilities are described through exactly three named primitives, each with a different intended controller and a different protocol shape: **tools** (model-invoked actions, the same "function calling" mechanism from `tool-use-agentic-loop/01` now delivered over the wire), **resources** (application-controlled, read-only context the client fetches and attaches, not something the model decides to "call"), and **prompts** (user-controlled, reusable templates a human explicitly triggers, often surfaced as slash commands). Picking the wrong primitive for a capability - e.g. modeling read-only reference data as a tool - creates real, avoidable friction; the three exist because "give the model information" and "let the model take an action" and "let the user kick off a known workflow" are three different problems with three different trust models.

## The idea
`tool-use-agentic-loop/01` established that a tool call is structured output the model emits and your application executes. MCP's **tools** primitive is exactly that mechanism, standardized over the client-server connection from `model-context-protocol/02` - a server declares tools with the same name/description/JSON-Schema contract you already know, and the client relays the model's tool-call intent to the server and the server's result back. But MCP was not designed only to move existing tool-call mechanics onto the network; it also standardizes two things function calling never covered: how a server hands the model *reference material* without pretending that's an action, and how a *human* (not the model) explicitly kicks off a known, reusable workflow. Those became resources and prompts respectively, and the distinction is not cosmetic - each primitive has a different *controller*, and that controller determines who decides when it fires.

| Primitive | Controlled by | Analogous to | Fires when |
| --- | --- | --- | --- |
| Tools | The model | A function call | The model decides an action is needed |
| Resources | The application/client | A GET request or a file read | The host attaches it, or the user picks it |
| Prompts | The user | A slash command / macro | The human explicitly invokes it |

## How it works

### Tools: the model decides, per `tool-use-agentic-loop/01`, now server-hosted
An MCP server exposing a tool declares it with the familiar `name`, `description`, and `inputSchema` (JSON Schema) - discoverable via a `tools/list` request and invoked via `tools/call`. Everything from `tool-use-agentic-loop/01` and `02` about model-driven selection, argument-schema conformance, and description quality applies unchanged; the only thing that moved is *where the function actually lives* - not in your application's own codebase, but behind a server the client talks to over stdio or HTTP.

**Worked example.** A `github` MCP server declares a tool `create_issue` with `inputSchema` requiring `repo`, `title`, and an optional `body`. The host's client calls `tools/list`, gets this definition back, and hands it to the model in the exact three-part-contract shape from `tool-use-agentic-loop/01`. When a user says "file a bug for the login timeout," the model emits a `tools/call` request for `create_issue` with the arguments filled in; the client relays it to the GitHub server, which does the actual GitHub API call and returns a result the model never directly touched. Nothing about the model's decision-making changed by going through MCP - what changed is that the same `create_issue` tool is now reusable, unmodified, by any other host that connects an MCP client to this same server.

### Resources: the application decides, because not everything is an action
A resource is read-only, addressable data a server exposes - file contents, a database schema, log output, a document - each identified by a URI (e.g. `file:///project/README.md` or a custom scheme like `postgres://schema/orders`). A client discovers them via `resources/list` and fetches content via `resources/read`; servers can optionally support `resources/subscribe` so a client is notified when a resource's content changes, and a `notifications/resources/list_changed` event when the *set* of available resources itself changes.

The reason resources are a separate primitive rather than "just make it a tool called `read_file`" is about *who decides when it happens*. A tool call is the model's decision, made fresh, from the conversation, every time - which means if the model doesn't think to call `read_file`, the content simply never enters context. A resource can instead be attached by the *host application itself*, independent of the model's judgment: an IDE host can automatically attach "the file currently open in the editor" as a resource on every turn, or present a resource picker so the user explicitly selects which files ground the conversation, without ever depending on the model correctly deciding to call a tool for it. This matters most for context that should reliably be present - reference data the task genuinely requires - rather than context that's situationally useful and fine to leave to the model's judgment.

**Worked example.** A documentation MCP server exposes every page of a product's docs as resources, `docs://api/authentication`, `docs://api/rate-limits`, and so on. A support-bot host, when a user opens a ticket tagged "auth issue," has its own application logic (not the model) fetch and attach `docs://api/authentication` via `resources/read` before the model ever sees the user's message - guaranteeing the model is grounded in the right reference material regardless of whether it would have thought to ask for it. Compare this to modeling the same docs as a `search_docs` tool: correct in principle, but now contingent on the model choosing to call it, which per `tool-use-agentic-loop/02`'s discussion of tool-selection ambiguity is not a given, especially under a crowded tool list.

### Prompts: the user decides, as a reusable, named workflow
A prompt is a server-defined, reusable template - a name, an optional description, and a typed list of arguments (each with its own name, description, and whether it's required) - that a *human* explicitly triggers, commonly surfaced by hosts as a slash command (e.g. `/analyze-code`). A client discovers them via `prompts/list` and invokes one via `prompts/get`, passing argument values; the server returns a fully formed prompt (often a sequence of messages, potentially referencing resources) that the host inserts into the conversation.

The distinction from tools here is again about the controller: a prompt does not wait for the model to decide it's relevant - it exists so a human can reliably kick off a known-good workflow ("review this PR the way our team always does it," "summarize today's incidents") without having to retype or reconstruct that workflow's exact framing every time. It is closer to a saved macro than to a callable function.

**Worked example.** A code-review MCP server defines a prompt `review-pr` with a required argument `pr_number`. In a host that surfaces prompts as slash commands, a developer types `/review-pr 482`; the client calls `prompts/get` with `{name: "review-pr", arguments: {pr_number: "482"}}`, and the server returns a pre-built message sequence - e.g. "Fetch PR #482's diff [referencing a resource] and evaluate it against our team's review checklist: ..." - which becomes the actual conversation turn. No model judgment was involved in deciding *whether* this workflow should run; the developer decided that, explicitly, by typing the command.

### Choosing the right primitive: a decision the server author makes, not a formality
Because each primitive carries a different controller, mismatching a capability to the wrong primitive has a concrete failure mode, not just a stylistic cost:
- Modeling read-only reference data (documentation, schemas, static config) as a **tool** makes its inclusion contingent on the model's per-turn judgment to call it - exactly the tool-selection risk `tool-use-agentic-loop/02` warns about - when a **resource**, attachable deterministically by the host, would guarantee it's present when needed.
- Modeling a genuine side-effecting action (send a message, create a ticket, run a query) as a **resource** is a category error - resources are defined as read-only, and a host may reasonably auto-attach or cache them, which is actively dangerous if "reading" one secretly mutates state.
- Modeling a human-triggered, opinionated workflow as a bare **tool** the model might spontaneously decide to call removes the human's deliberate control over *when* that specific, curated workflow runs - a **prompt** exists precisely to keep that decision with the user.

## Pros
- Three distinct controllers (model / application / user) map cleanly onto three distinct real needs - action, grounding data, and human-initiated workflow - instead of forcing every capability through a single "callable function" shape.
- Resources let a host guarantee reliable grounding without depending on the model's tool-selection judgment, directly mitigating a known failure mode from `tool-use-agentic-loop/02`.
- Prompts give server authors a way to distribute *curated, reusable* workflows (not just raw capabilities) to every host that connects, the same M+N reuse story as tools and resources, applied to "a good way to ask for this."

## Cons
- Client and host support for resources and prompts has historically lagged tool support in the ecosystem - a server author cannot assume every host surfaces a resource picker or prompt slash-commands as richly as it surfaces tool calls, so tools remain the safest lowest-common-denominator primitive to lead with.
- Three primitives is three things to design well, not one - a server author has to correctly judge which primitive each capability belongs to (per the decision guidance above), and getting it wrong produces the friction described there rather than an obvious error.
- Subscriptions (`resources/subscribe`) and list-changed notifications add real implementation and connection-management complexity for a server author, for a benefit (live-updating context) that not every use case needs.

## Alternatives
- **Model everything as a tool** — simplest mental model for a server author (one primitive, one contract), and works everywhere tools work; loses the reliable-grounding guarantee of resources and the human-controlled-invocation guarantee of prompts, reintroducing the failure modes described above.
- **Push all context into the system prompt at connection time, skip resources entirely** — works for small, static reference material, but doesn't scale to large, changing, or selectively relevant data, and gives up the subscribe/list-changed live-update mechanism resources provide.
- **Build workflow templates into the host application itself, not as MCP prompts** — a host can hardcode its own slash commands independent of any server; simpler for host-specific workflows, but loses the reuse benefit of a server-distributed prompt that works identically across every host that connects to it.

## When to use it
Use **tools** for anything genuinely action-shaped, where the model's judgment about *whether* to act is exactly what you want. Use **resources** for reference data the task should reliably be grounded in, especially when you don't want correctness to depend on the model remembering to ask for it. Use **prompts** for a known-good, reusable workflow a human should be able to invoke deliberately and repeatably, without re-explaining it in prose each time.

## When NOT to use it
Don't reach for resources or prompts to solve problems tools already solve well in your specific host - if your host's client and UI only meaningfully support tool calls today, forcing a design onto resources/prompts that the host can't actually surface well is optimizing for a primitive taxonomy over what actually works for your users. Equally, don't stretch a single monolithic tool to cover "fetch reference data" and "take an action" and "run a curated workflow" just to avoid implementing more than one primitive - the resulting tool's description and schema will fight the ambiguity-reduction guidance from `tool-use-agentic-loop/02`.

## Key takeaways / mental model
Ask "who decides when this fires?" - the model deciding mid-conversation means **tool**; the application deciding to attach it regardless of the model's judgment means **resource**; the user deciding to explicitly invoke a known workflow means **prompt**. All three are discoverable (`*/list`) and invokable (`tools/call`, `resources/read`, `prompts/get`) through the same client-server connection from `model-context-protocol/02`, but they exist as three primitives, not one, because those three controllers have genuinely different failure modes when a capability is placed in the wrong one.

## Self-check questions
1. A server author models their product's entire API reference (hundreds of pages) as a single tool `search_docs(query)`. Using the reliable-grounding argument from this lesson, explain a concrete scenario where this choice causes the model to give a wrong answer that a resource-based design would have prevented.
2. Explain why "send a Slack message" must never be modeled as a resource, tying your answer to the read-only assumption resources make and what a host is allowed to assume it can safely do with a resource (like auto-attach or cache it).
3. A team builds a prompt `deploy-to-prod` that, when invoked, causes the server to immediately run a production deployment - no further confirmation. What primitive-selection mistake does this repeat from question 2, applied to prompts instead of resources?
4. You're deciding between exposing a database schema as a resource (`resources/read`) versus a tool (`get_schema()`). Both are technically readable either way. Using the "who decides when this fires" framing, argue for whichever you'd pick, and identify one concrete situation where the other choice would actually be better.
5. A host only implements the tools primitive, not resources or prompts. What does a server author lose, specifically, by only being able to reach that host through tools - and what workaround (imperfect) could they use within the tools primitive alone?

## References
- [Model Context Protocol: server concepts documentation](https://modelcontextprotocol.io/docs/learn/server-concepts)
- [Speakeasy: What are MCP resources?](https://www.speakeasy.com/mcp/core-concepts/resources/)
- [Speakeasy: What are MCP prompts?](https://www.speakeasy.com/mcp/core-concepts/prompts)
- [Stacktree: MCP tools vs resources vs prompts - a decision table](https://stacktr.ee/blog/mcp-resources-vs-tools-vs-prompts)
