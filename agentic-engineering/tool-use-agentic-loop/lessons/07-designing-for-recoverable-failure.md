---
id: tool-use-agentic-loop/07
subject: tool-use-agentic-loop
title: "Designing for Recoverable Failure: Idempotency, Timeouts, and Retry Budgets"
slug: designing-for-recoverable-failure
status: drafted
mastery:
seniority: senior
source: "Claude Platform Docs: Claude API errors (2026); Temporal Docs: Basic agentic loop with Claude and tool calling - AI Cookbook (2026); arXiv:2608.02645 Verified Tool Calls Improve LLM Agent Reliability Under Non-Atomic Failures (2026); Fastio: AI Agent Idempotent Operations - A Guide for Developers (2026); TianPan.co: Idempotency Is Not Optional in LLM Pipelines (2026)"
durability: durable
prerequisites: [tool-use-agentic-loop/06]
created: 2026-08-10
updated: 2026-08-10
---

# Designing for Recoverable Failure: Idempotency, Timeouts, and Retry Budgets

## TL;DR
A tool call can fail in three different places - before the side effect happened, during it, or after it happened but before the result got back to the model - and each failure point demands a different response. Retrying blindly turns a network hiccup into a duplicated charge or a doubled email; never retrying turns a transient blip into a task the agent silently abandons. Designing for recoverable failure means classifying the failure, bounding how hard you retry, and making the underlying operation safe to repeat - the same reliability toolkit distributed systems have used for decades, now applied to a model that decides, on its own, when to call a tool again.

## The idea
Lesson 06 established that tool execution can be stateless (pure function of its inputs, safe to call again) or stateful (mutates something external - a database row, an email inbox, a payment ledger). The moment a tool is stateful, "just retry on failure" stops being an obviously safe default, because the LLM issuing the retry has no built-in concept of "did that actually happen." It only sees an error, a timeout, or silence, and its instinct - reinforced by training on helpful, persistent problem-solving - is to try again.

This is not a hypothetical problem. Reported failure rates for tool calls in production agent systems land around 15-30% due to timeouts, validation errors, or transient infrastructure issues, and every one of those is a decision point: retry, don't retry, or retry differently. Distributed systems engineering solved a structurally identical problem decades ago - a client that doesn't know whether its request reached the server before the connection dropped. The vocabulary transfers directly: **idempotency** (repeating an operation has the same effect as doing it once), **exponential backoff with jitter** (space out retries so they don't stack into a thundering herd), and **retry budgets** (a hard ceiling on how much retrying a given operation is allowed to cost, in attempts, time, or money). What's new is that the client issuing the retry is a language model choosing, in natural language, whether to call the tool again - which means the *harness* around the model, not the model itself, has to enforce the parts that must never depend on a probabilistic judgment call.

## How it works

### Where a tool call can fail, and why the failure point changes the right response
A tool call has three phases: **the request goes out**, **the side effect happens (or doesn't)**, and **the result comes back**. A failure can happen at any of the three boundaries, and each implies something different about whether the side effect actually occurred:

```
 Agent                    Network                  Tool / External System
   |--- call: charge($50) --->|                            |
   |                          |--- request ---------------->|
   |                          |                              | [A] fails here:
   |                          |                              |     side effect
   |                          |                              |     never happened
   |                          |<-- (charge processed) -------|
   |                          |                              | [B] fails here:
   |                          |                              |     side effect DID
   |                          |                              |     happen, response lost
   |<--- timeout / no reply --|                              |
```

- **[A] Failure before the side effect.** The request never reached the tool, or the tool rejected it outright (a 4xx validation error, a malformed argument). Nothing happened. Retrying is safe and usually correct - but only after fixing whatever caused the rejection, if it was a validation error rather than a transient one.
- **[B] Failure after the side effect, before the response.** The charge went through, the email sent, the row got written - but the network dropped, the tool process crashed, or the call timed out before the model heard back. From the model's point of view this is indistinguishable from case A: both look like "no response." Retrying naively now double-charges the customer or sends the email twice.
- **A third, quieter case:** the tool returns *successfully* but with a result the agent doesn't parse correctly (a partial JSON payload, a truncated stream), and the model - unable to tell "no answer" from "an answer I didn't understand" - proceeds as if the call failed. This is functionally identical to case B for retry-safety purposes: something may have already happened.

The core design principle: **you cannot tell cases A and B apart from the client side after the fact, so you must make the operation safe to run twice regardless of which one occurred.** That is what idempotency buys you - it collapses the distinction that the network refuses to reliably preserve.

### Worked example: idempotency keys for a stateful tool
Consider a `create_refund(order_id, amount)` tool. Called twice by mistake, it must not refund twice. The fix is a **stable idempotency key** attached to the operation, not to the transport:

1. When the agent decides to call `create_refund`, the harness (not the model) generates or derives a key - commonly a hash of the semantically meaningful arguments (`order_id` + `amount` + a caller-scoped nonce for the *original* decision, not the retry) or a UUID minted once per logical intent and reused across retries of that same intent.
2. The refund service, on receiving a request, checks whether it has already processed that idempotency key. If yes, it returns the *stored result* of the original execution instead of processing again - no new refund is issued, and the caller still gets a valid, matching response.
3. If the model calls `create_refund` again after a timeout, it presents the same key (the harness ensures this, since the model doesn't need to invent a new key for a genuine retry - only for a genuinely new refund). The service recognizes the key, and the second call is a safe no-op that returns the first call's result.

The load-bearing design decision is *what the key is derived from*. A key derived from wall-clock time or a fresh random value on every attempt provides no protection - it just gives every duplicate call a unique identity and lets it through. A key derived from the *intent* (these specific arguments, this specific triggering event) and held stable across retries of that intent is what makes the retry safe. This mirrors exactly how idempotency keys work in payment APIs and message queues: the key names the *decision*, not the *attempt*.

### Worked example: retryable vs. non-retryable errors, and why conflating them is expensive
An agent's tool layer receives an error from a downstream API. Blind "retry on any failure" logic wastes budget and can make things worse. The distinction that matters:

- **Retryable (transient):** rate limits (429), server errors (5xx), connection timeouts, DNS blips. These may succeed on a later attempt with no change in the request. Retry with exponential backoff and jitter (e.g., 1s, 2s, 4s, 8s, each with +/-20% random jitter so many concurrent agents don't retry in lockstep and create a synchronized retry storm on the already-struggling service).
- **Non-retryable (permanent):** 400 (malformed request), 401/403 (auth/permissions), 404 (resource does not exist), most validation errors. Retrying the identical request produces the identical failure - the fix is to change the request (often by feeding the error back to the model so it corrects its arguments) or to stop and surface the problem, not to hammer the endpoint.

Concretely: a tool wrapper that retries a 404 three times before giving up has spent three round-trips (and three chances for the model to burn reasoning tokens interpreting each failure) on an error that was never going to resolve itself. A tool wrapper that never retries a 429 abandons a task that a five-second wait would have completed. Getting this classification right at the harness layer - so the model sees "this needs different arguments" versus "this will likely work if tried again" as distinct signals - is worth more than any amount of prompt engineering telling the model to "be persistent but not too persistent."

### Worked example: retry budgets as a hard ceiling, not a suggestion
Even fully idempotent, correctly classified retries need a ceiling, because "safe to retry" is not the same as "worth retrying forever." A retry budget bounds a single tool call (or a single logical operation) along one or more axes:
- **Attempt count** - e.g., stop after 3 attempts, matching the common circuit-breaker pattern (closed -> open after N consecutive failures -> half-open probe after a cooldown -> closed again if the probe succeeds).
- **Wall-clock time** - e.g., stop retrying a single tool call after 30 seconds total, regardless of how many attempts that allowed.
- **Cost** - relevant when the tool itself has a per-call cost (a paid search API, a code-execution sandbox charged by the second).

Where this differs from a plain circuit breaker in a traditional microservice is that the *caller* deciding to retry is a language model reasoning in natural language, not a fixed piece of retry logic. That means the retry budget has to live in the harness, enforced in code, independent of what the model "decides" to do - because a model mid-conversation, told an operation failed, will often propose trying again, again, and has no innate sense of "we've spent our budget on this." A harness that lets the model's own judgment be the only retry limiter has, in practice, no retry limiter.

## Pros
- **Prevents duplicated side effects.** Idempotency keys make "the network is uncertain about what happened" a non-issue for correctness, instead of a source of double charges or duplicate messages.
- **Recovers from genuinely transient failures automatically**, improving task success rate without any change to the model or the prompt - a 429 that resolves in two seconds no longer derails the whole task.
- **Bounds the cost of failure.** A retry budget caps how much a single flaky tool call can cost in time, attempts, or money, independent of the model's own persistence.
- **Reuses a mature, well-understood toolkit** (idempotency keys, exponential backoff with jitter, circuit breakers) instead of inventing bespoke reliability mechanics for agents.

## Cons
- **Idempotency has to be designed into the tool itself**, often on the far side of an API you don't control. A third-party tool with no idempotency-key support cannot be made safely retryable from the client side alone - you can only reduce the retry-storm risk, not eliminate the duplication risk.
- **Correct error classification requires per-tool knowledge.** A blanket "retry on any 5xx" policy is a reasonable default but breaks down for APIs whose 5xx sometimes means "already partially applied" - domain knowledge of the specific tool is often unavoidable.
- **Adds real engineering surface.** Key generation, a dedup store, backoff/jitter tuning, and budget enforcement are all extra code paths that need their own tests and monitoring - non-trivial for a fast-moving agent prototype.
- **Silent over-retrying still degrades UX even when it's "safe.**" A user watching an agent visibly stall for 30 seconds retrying a call that idempotency protected from corruption still experienced a bad interaction; safety and responsiveness are separate goals.

## Alternatives
- **Compensating actions (sagas)** - instead of preventing duplicate effects, allow them and undo them: if a refund tool can't be made idempotent, pair it with a `list_recent_refunds` check-before-call, or an explicit `cancel_refund` compensator the agent can invoke if it later confirms a duplicate happened. Preferable when the underlying system genuinely cannot support idempotency keys.
- **At-most-once by design (fire-and-forget with no retry)** - simply never retry a stateful call automatically; surface the failure to the model or the user and let a human or a higher-level planner decide. Preferable for high-stakes, low-frequency operations (e.g., "delete this production database") where a silent automatic retry is more dangerous than a task that stops and asks.
- **Human confirmation before the effect, not after the failure** - move the safety net earlier: require explicit approval before any non-idempotent, high-consequence tool call executes at all, so a bad retry is never possible because the risky call only ever fires once, deliberately. Preferable when the operation is rare enough that added latency from a confirmation step is cheap relative to the cost of getting it wrong.
- **Read-only verification tool** - give the agent a cheap way to check current state before deciding whether to act (e.g., `get_refund_status(order_id)` before calling `create_refund`), so the agent's own reasoning - not just the harness - can detect "this already happened" and skip the duplicate call. Preferable as a complement to idempotency keys, not a replacement, since it depends on the model reliably choosing to check first.

## When to use it
Apply idempotency keys, retryable/non-retryable classification, and retry budgets to every tool that has a side effect outside the conversation - anything that writes, sends, charges, deletes, or otherwise changes state in a system the agent doesn't fully control. This is non-negotiable once an agent runs with any autonomy (no human confirming every single call), because that is exactly when a silent double-execution goes unnoticed until it shows up as a support ticket or a duplicate transaction days later.

## When NOT to use it
Skip the machinery for genuinely stateless, side-effect-free tools (a calculator, a read-only lookup, a pure computation) - retrying those has no correctness cost, so a simple bounded retry-with-backoff is enough and idempotency keys add complexity with no payoff. Also do not over-engineer a human-supervised prototype where every tool call is confirmed by a person before it fires - the human confirmation step is already the safety net, and building a full idempotency layer underneath it before you know which tools will actually ship to unsupervised use is premature investment.

## Key takeaways / mental model
Treat every stateful tool call the way a distributed-systems engineer treats a network write to a service they don't control: assume the response can be lost even when the side effect succeeded, so make the *operation* safe to repeat (idempotency), not just the retry logic forgiving. Classify failures before reacting to them - transient gets a bounded, jittered retry; permanent gets a different request or a stop. And keep the ceiling on retrying (attempts, time, or cost) enforced in code the model doesn't control, because a model's own judgment about "should I try this again" is a reasonable signal to consult, never a safe substitute for a hard budget.

## Self-check questions
1. An agent calls a `send_invoice(customer_id, amount)` tool. The call times out after 20 seconds with no response. The agent's next message says "That seems to have failed, let me try again." What two questions do you need answered before deciding whether that retry is safe, and how would you design the tool so the answer doesn't matter?
2. Explain why a retry budget enforced entirely through prompt instructions ("please don't retry more than 3 times") is a weaker guarantee than one enforced in the harness's tool-calling code. What failure mode does the prompt-only version leave open?
3. A tool wrapper currently retries every error type identically with the same exponential backoff. Walk through what goes wrong for (a) a 401 authentication error and (b) a 429 rate limit, under that identical-treatment policy, and describe the fix for each.
4. Design an idempotency key for a `book_meeting(attendees, start_time, duration)` tool call that an agent might retry after a timeout. What should the key be derived from, and what would go wrong if you derived it from the current timestamp instead?
5. A teammate argues that since the underlying payment API doesn't support idempotency keys, there's nothing to be done and retries should simply be disabled for that tool. Do you agree? What alternative from this lesson would you propose instead, and what trade-off does it introduce?

## References
- [Claude API errors - Claude Platform Docs](https://platform.claude.com/docs/en/api/errors)
- [Basic agentic loop with Claude and tool calling - Temporal AI Cookbook](https://docs.temporal.io/ai-cookbook/agentic-loop-tool-call-claude-python)
- arXiv:2608.02645 - Verified Tool Calls Improve LLM Agent Reliability Under Non-Atomic Failures
- [Fastio: AI Agent Idempotent Operations - A Guide for Developers](https://fast.io/resources/ai-agent-idempotent-operations/)
- [TianPan.co: Idempotency Is Not Optional in LLM Pipelines](https://tianpan.co/blog/2026-04-20-idempotency-llm-pipelines)
- `agentic-engineering/tool-use-agentic-loop/lessons/06-stateless-vs-stateful-tool-execution.md` (prerequisite: stateless vs. stateful tool classification)
