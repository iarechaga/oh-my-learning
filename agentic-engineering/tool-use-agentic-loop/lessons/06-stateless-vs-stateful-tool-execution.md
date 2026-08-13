---
id: tool-use-agentic-loop/06
subject: tool-use-agentic-loop
title: "Stateless vs Stateful Tool Execution and Retries"
slug: stateless-vs-stateful-tool-execution
status: drafted
mastery:
seniority: senior
source: "Model Context Protocol Blog: The 2026-07-28 Specification (2026); Mervin Praison: Stateful vs Stateless MCP - Sticky Sessions Are Gone (2026); AWS ML Blog: Introducing stateful MCP client capabilities on Amazon Bedrock AgentCore Runtime (2026); Stripe API docs: Idempotent Requests (long-standing industry pattern, referenced via secondary sources 2026)"
durability: durable
prerequisites: [tool-use-agentic-loop/02]
created: 2026-08-10
updated: 2026-08-10
---

# Stateless vs Stateful Tool Execution and Retries

## TL;DR
A tool call can either carry everything it needs in the request itself (stateless - any server instance can handle it, and repeating it is usually safe) or depend on server-side context accumulated from prior calls (stateful - it must land on the same instance as before, and repeating it out of order can corrupt that context). This is the same stateless-vs-stateful trade-off distributed systems have faced for decades, applied to agent tool execution - and it directly determines whether a retry after a failed or ambiguous call is safe to issue automatically or requires real judgment.

## The idea
An agent calling tools is, underneath the model-facing abstraction, a distributed system: the harness (lesson 05) is a client, each tool is a service it calls over some boundary (a function call, an HTTP request, an MCP server), and that boundary can fail in all the ordinary ways network calls fail - timeouts, dropped responses, partial completion. When a call fails or times out, the harness has to decide whether to retry it (part of lesson 07's territory), but *whether retrying is even safe* depends entirely on a design decision made when the tool was built: does this tool's execution depend only on the arguments in this one request, or does it depend on server-side state built up from previous requests in this session?

This is not a new problem invented by agents - it is the decades-old stateless-vs-stateful service design question from distributed systems, and the vocabulary carries over directly. A stateless service treats every request as self-contained: nothing about how it's processed depends on which instance handles it or what requests came before. A stateful service keeps context across requests - a session, a connection, an in-progress transaction - which means requests are no longer interchangeable: request 2 might only make sense in light of request 1 having already happened on that same instance. Agent tool execution inherits this distinction directly, and it inherits the operational consequences too: stateless tools are trivially retriable and horizontally scalable; stateful tools are neither, without extra machinery.

## How it works

### Stateless tool execution
A stateless tool call is fully determined by its arguments: given the same input, it produces the same class of outcome regardless of which server instance handles it or what happened on any previous call. "Get the current weather for Tokyo," "convert this amount from USD to EUR," "search this document for a keyword" - each of these carries everything the tool needs in the one request. No server-side memory of prior calls is required to process it correctly.

This has a direct, practical payoff: any instance of the tool's backend can serve any request, so load-balancing is trivial (plain round-robin works, no session affinity needed), horizontal autoscaling works without special configuration, and - most relevant to this lesson - **retrying is usually safe by default** for read-only stateless operations, because repeating an identical request either produces the same read again or, for many designs, the same effect again with no compounding harm.

> **Example (Aug 2026):** the Model Context Protocol's 2026-07-28 specification update moved the protocol's core toward a stateless request/response model - removing the persistent session-initialization handshake and adding self-describing headers so that any server instance can serve any request without needing sticky routing to a specific instance that "remembers" the session. This mirrors, at the tool-protocol layer, exactly the same stateless-service design trade-off described generically above: check current MCP spec docs for the precise mechanics, since this area is actively evolving.

### Stateful tool execution
A stateful tool call depends on context that isn't fully present in the request itself - it was established by a prior call and lives on the server (or in a specific instance's memory) between calls. Consider a coding-agent tool that clones a git repository once, then offers subsequent tools ("list files," "read file," "run tests") that operate against that already-cloned local copy rather than re-specifying the repository URL and re-cloning on every call. The clone is session state: call 2 ("read file X") only makes sense in light of call 1 ("clone this repo") having already happened, and it has to reach the same server instance that holds that clone on disk - a different instance, with no clone present, cannot serve it correctly no matter what arguments accompany the request.

Stateful execution buys real efficiency (you don't re-clone a large repository on every single file read) at a real operational cost: the harness or infrastructure needs session affinity (routing every call for a given session to the same backend instance), explicit session lifecycle management (creating the session, keeping it alive, tearing it down and freeing resources when done), and - the part most relevant here - retries are no longer trivially safe, because a retried call might be replaying an action against state that has already moved on since the original attempt.

### Why the distinction changes what a safe retry looks like
This is the crux for agent engineering specifically. When a tool call fails ambiguously - the harness gets a timeout and genuinely does not know whether the tool executed before the response was lost - the safe response differs sharply by which kind of tool it is:

**Stateless read**: retry freely. "Get current weather for Tokyo" timed out; calling it again either gets the same answer or a slightly newer one - no harm either way, because nothing about the world was changed by the call, and nothing about the retry's correctness depends on the previous attempt's fate.

**Stateless write, not idempotent by design**: retrying is dangerous without further protection. "Charge this customer $50" timed out - the harness cannot tell whether the charge went through before the connection dropped. A naive retry risks a duplicate charge. This is where the underlying distributed-systems reality has to be named precisely: a network call has no way to distinguish "the request never arrived" from "the request arrived, executed, and only the acknowledgment was lost." Because of this, truly exactly-once delivery across an unreliable network is not achievable in general - the practical, industry-standard fallback for decades has been to accept **at-least-once delivery** (a caller may resend a request that already succeeded) and push the responsibility for correctness onto the receiver via **idempotency**: design the operation so that executing it two or more times with the same identifying key produces the same end state and the same returned result as executing it once. The common mechanism is an idempotency key - a unique identifier the caller attaches to the logical operation (not to each network attempt); the receiving service stores a short-lived record of "key X already ran, here was its result" and, on a retry carrying the same key, returns the stored result instead of re-executing the side effect. (Building this protection deliberately into tool design - rather than discovering its absence in production - is the subject of lesson 07.)

**Stateful call**: retrying is unsafe without understanding what state the retry would land on. If "clone the repo" partially succeeded before timing out, retrying blindly might clone into an already-partially-populated directory and corrupt it, or might correctly re-run against a clean slate - the right behavior depends entirely on what state actually exists server-side right now, which the harness cannot know from the failed response alone. Safe retry of a stateful operation generally requires either checking current state before retrying (e.g., "does the clone directory already exist and is it valid?") or making the *stateful setup step itself* idempotent (e.g., "clone if not already present, otherwise no-op") - which is really applying the idempotency-key idea to the specific operation that establishes the state, not a different technique.

### Worked example: designing the retry policy for a mixed tool set
Consider an agent with three tools: `search_docs` (stateless read), `submit_expense_report` (stateless write, side-effecting), and `open_terminal_session` + `run_command` (stateful - `run_command` executes against whatever shell state `open_terminal_session` established, including current working directory and any environment variables set by prior commands in the same session).

```
Tool                    Kind                  Safe default on timeout
------------------------------------------------------------------------
search_docs             stateless, read       retry automatically, no
                                               precaution needed

submit_expense_report   stateless, write      retry ONLY if the tool was
                                               built with an idempotency
                                               key; otherwise the harness
                                               must check whether the
                                               report already exists
                                               before resubmitting

run_command              stateful             retry is unsafe in general -
(after open_terminal_                          a partially-run command
session)                                       (e.g., `rm` that half-
                                                completed) could leave the
                                                session's state in a
                                                condition a naive re-run
                                                doesn't account for; the
                                                harness needs to inspect
                                                current state or require
                                                the command itself to be
                                                safely re-runnable
```

The table makes the operational point concrete: "just retry on failure" as a blanket harness policy is correct for exactly one of these three tools by default, silently unsafe for the other two unless each has been deliberately engineered (or the harness deliberately checks state) to make retrying safe.

### The scaling angle: why this also isn't just a correctness question
Beyond retry safety, statelessness versus statefulness governs how a tool-serving system scales and recovers. A stateless tool's backend can be scaled horizontally with a plain load balancer and no coordination, and a crashed instance can be replaced with a fresh one with zero data loss, because no instance holds anything that matters beyond the current request. A stateful tool's backend needs session affinity (every call for a session must reach the instance holding that session's state) and a recovery story for what happens when that specific instance crashes mid-session (the state is lost unless it was checkpointed somewhere durable) - real infrastructure cost that has nothing to do with the model's reasoning quality and everything to do with how the tool layer was built.

## Pros
- **Stateless tools**: trivial to scale, load-balance, and retry; failure recovery is simple because there's no session-specific state to lose or reconcile; easier to test in isolation since every call is self-contained.
- **Stateful tools**: substantially more efficient for workloads with real setup cost (cloning a large repo once instead of per-call, maintaining a database connection, holding an authenticated session) - avoiding redundant setup work on every single call.

## Cons
- **Stateless tools**: any workload with genuine setup cost forces that cost to be paid repeatedly (or re-derived from arguments) on every call if there's no session to amortize it across, which can be a real performance and cost tax for tools whose "state" would otherwise be cheap to keep around.
- **Stateful tools**: retries are unsafe by default and need deliberate engineering to make safe; horizontal scaling needs session-affinity infrastructure; a crashed instance can lose session state unless explicitly checkpointed; the harness has to manage session lifecycle (create, keep-alive, teardown) as extra surface area that can itself fail.

## Alternatives
- **Externalize the state instead of keeping it in the tool server.** Move what would be session state into a durable, addressable store (a database row, a file on shared storage) that any stateless instance can read given an identifier passed in the request - this converts what looks like a stateful problem into a stateless one at the cost of the extra round-trip to fetch/persist that state. Often the right move for state that outlives a single agent session (see the retrieval/memory lesson in the context-engineering subject) but adds latency and infrastructure that a truly ephemeral, short-lived session doesn't need.
- **Session affinity with checkpointing** - keep the tool stateful, but periodically persist its state to durable storage so a crashed instance's session can be reconstructed elsewhere rather than lost outright. A middle ground: keeps the performance benefit of in-memory state for the common case while bounding the cost of a crash.
- **Idempotency keys as a narrower fix** (covered in depth in lesson 07) - doesn't eliminate statefulness, but neutralizes the specific "is this retry safe" problem for write operations regardless of whether the underlying tool is stateless or stateful, by making repeated execution with the same key a no-op after the first success.

## When to use it
Default to stateless tool design whenever the per-call setup cost is low or the call is naturally self-contained (most read operations, most single-shot lookups and conversions) - the operational simplicity and retry safety are worth far more than the setup cost they'd save. Reach for stateful tool design deliberately when setup cost is genuinely high relative to the calls that reuse it (cloning a large repository, establishing an authenticated connection to an expensive-to-open resource, maintaining an interactive shell or REPL across many commands) and the session is naturally short-lived and owned by one agent run at a time.

## When NOT to use it
Do not default to stateful tool design "because it's more efficient" without weighing the retry-safety and scaling cost against the setup cost it actually saves - for most tool calls in most agents, that setup cost is small enough that statelessness's operational simplicity wins outright. And never treat "the tool is stateless" as license to skip idempotency design on write operations - statelessness makes retries *simpler to reason about*, not automatically *safe*; a stateless tool that charges a credit card is still unsafe to blindly retry unless it was explicitly built with an idempotency key (lesson 07).

## Key takeaways / mental model
Ask one question about any tool before deciding how its failures should be handled: does executing this call correctly require anything that isn't in the request itself? If no - it's stateless, any instance can serve it, and reads are safe to retry freely. If yes - it's stateful, it must land on the instance holding its state, and retries need to account for what state actually exists right now, not just what the original request said. Either way, "stateless" is not a synonym for "automatically safe to retry" the moment the call has a side effect - that safety has to be engineered deliberately (idempotency), which is where lesson 07 picks up.

## Self-check questions
1. Classify each of the following as stateless or stateful, and justify: (a) a tool that translates a string from English to French, (b) a tool that adds an item to a shopping cart tied to a session ID established by an earlier "start_checkout" call, (c) a tool that queries a customer's current account balance by account number.
2. Explain, in distributed-systems terms, why "exactly-once delivery" is not achievable in general across an unreliable network, and what practical guarantee the industry substitutes for it instead.
3. A tool named `create_ticket` has no idempotency protection and is stateless. It times out during a call. What's unsafe about retrying it automatically, despite it being stateless? What would you need to add to make the retry safe?
4. Your agent uses a stateful `open_database_transaction` / `execute_query` / `commit_transaction` tool sequence. The instance holding the transaction crashes mid-sequence. What are the harness's realistic options, and what does each cost?
5. A teammate argues "we should make every tool stateful so it can cache expensive setup work and be faster." Give the strongest counter-argument from this lesson, specifically about what stateful design costs in terms of retry safety and scaling, and describe one situation where making the tool stateless plus caching the expensive setup externally would get most of the speed benefit without those costs.

## References
- [Model Context Protocol Blog: The 2026-07-28 Specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [Mervin Praison: Stateful vs Stateless MCP - Sticky Sessions Are Gone](https://mer.vin/2026/07/stateful-vs-stateless-mcp-sticky-sessions-gone/)
- [AWS Machine Learning Blog: Introducing stateful MCP client capabilities on Amazon Bedrock AgentCore Runtime](https://aws.amazon.com/blogs/machine-learning/introducing-stateful-mcp-client-capabilities-on-amazon-bedrock-agentcore-runtime/)
- [Google Developers Blog: Scaling AI Agent Infrastructure with the MCP Stateless updates](https://developers.googleblog.com/scaling-ai-agent-infrastructure-with-the-mcp-stateless-updates/)
