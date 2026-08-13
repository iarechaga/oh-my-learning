# Tool Use & the Agentic Loop - Subject Summary

A comprehensive recap of this subject, concept by concept.

**Progress note:** all 8 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom
(dependency-ordered).

## Part I - Calling One Tool

- **[tool-use-agentic-loop/01] Function calling mechanics** - a tool call is a
  specially-structured chunk of model output text, not the model reaching out and
  executing code; the calling application parses and executes it, then feeds the
  result back in as ordinary text on the next call.
  ([lesson](lessons/01-function-calling-mechanics.md))
- **[tool-use-agentic-loop/02] Designing tool schemas** - a tool's name, description,
  and JSON-Schema-typed arguments are the entire interface the model has to decide
  whether and how to call it; most "wrong tool" or "made-up value" failures are schema
  design failures, not model failures.
  ([lesson](lessons/02-designing-tool-schemas.md))
- **[tool-use-agentic-loop/03] The agentic loop** - what makes something an *agent*
  rather than a single tool call is that the round trip (emit, execute, feed result
  back) repeats under the model's own judgment; conventionally described as plan, act,
  observe, repeat - the load-bearing structure under the rest of this subject.
  ([lesson](lessons/03-the-agentic-loop.md))

## Part II - Composing and Hardening the Loop

- **[tool-use-agentic-loop/04] Parallel vs sequential tool calls** - executing
  independent tool calls concurrently cuts latency to roughly the slowest single call
  instead of the sum of all of them, but the moment calls share a data or state
  dependency, parallel execution stops being an optimization and becomes a correctness
  bug. ([lesson](lessons/04-parallel-vs-sequential-tool-calls.md))
- **[tool-use-agentic-loop/05] Harness vs scaffolding** - the harness is the
  execution/control layer that calls the model, dispatches tool calls, and decides
  when to stop; the scaffolding is what the model works from on a given turn -
  instructions, tools, format. Most agent-quality problems are one layer's problem
  wearing the other layer's disguise.
  ([lesson](lessons/05-harness-vs-scaffolding.md))
- **[tool-use-agentic-loop/06] Stateless vs stateful tool execution** - a stateless
  call carries everything it needs and is generally safe to retry; a stateful call
  depends on server-side context from prior calls and can corrupt that context if
  retried out of order - directly determining whether a retry is automatic or needs
  judgment. ([lesson](lessons/06-stateless-vs-stateful-tool-execution.md))
- **[tool-use-agentic-loop/07] Designing for recoverable failure** - a tool call can
  fail before, during, or after its side effect, and each failure point needs a
  different response; recoverable failure means classifying the failure, bounding
  retries, and making the operation safe to repeat - distributed-systems reliability
  applied to a model that decides on its own when to retry.
  ([lesson](lessons/07-designing-for-recoverable-failure.md))
- **[tool-use-agentic-loop/08] When to stop** - an agentic loop with no explicit stop
  condition fails expensively, not gracefully; fixed caps, cost/time budgets,
  no-progress detection, confidence self-assessment, and human checkpoints each catch
  a different failure, and staff-level judgment is choosing which combination to
  compose for a task's blast radius. ([lesson](lessons/08-when-to-stop.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on the concepts
rated `shaky` or `not-yet`.
