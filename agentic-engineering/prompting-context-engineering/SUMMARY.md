# Prompting & Context Engineering - Subject Summary

A comprehensive recap of the foundation subject of the `agentic-engineering` domain,
concept by concept.

**Progress note:** all 10 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom
(dependency-ordered).

## Part I - Crafting a Single Prompt

- **[prompting-context-engineering/01] What LLMs actually do** - an LLM is a function
  that repeatedly predicts the next token given everything before it, has no memory
  between separate calls, and has a hard, finite context window (input + output
  combined). Nearly every other concept in this domain is a consequence of these three
  facts. ([lesson](lessons/01-what-llms-actually-do.md))
- **[prompting-context-engineering/02] Prompt anatomy** - a prompt is a structured
  sequence of role-tagged messages (system/developer, user, assistant, tool), and the
  role a piece of text is tagged with changes how much authority the model gives it -
  the first, most basic lever of prompt design.
  ([lesson](lessons/02-prompt-anatomy.md))
- **[prompting-context-engineering/03] Core prompting techniques** - few-shot examples,
  role prompting, and explicit output formatting all work through in-context learning;
  each has diminishing returns and failure modes past a point.
  ([lesson](lessons/03-core-prompting-techniques.md))
- **[prompting-context-engineering/04] Chain-of-thought and reasoning effort** - CoT
  reliably helps on tasks with real multi-step/symbolic structure, but through 2025 the
  research shows little or negative benefit elsewhere, and that the visible reasoning
  trace can be an unfaithful, post-hoc rationalization rather than the true causal
  path - more thinking tokens is not automatically better.
  ([lesson](lessons/04-chain-of-thought-and-reasoning-effort.md))
- **[prompting-context-engineering/05] Structured output** - constrained decoding masks
  the model's token distribution at every generation step so only schema-valid tokens
  can be chosen, turning "the model produced valid JSON" from a probabilistic hope
  into a mechanical guarantee - strictly stronger than asking nicely and parsing the
  reply. ([lesson](lessons/05-structured-output.md))
- **[prompting-context-engineering/06] The limits of prompting** - prompting changes
  what you ask the model to do, not what it's capable of, what it knows, or what it can
  act on; diagnosing whether a failure is a capability gap, a missing affordance, a
  context gap, or a decomposition/reliability problem is the senior-level skill this
  lesson teaches. ([lesson](lessons/06-limits-of-prompting.md))

## Part II - Engineering the Context Across a Session

- **[prompting-context-engineering/07] Context engineering as a discipline** - the
  pivot of the subject: a context window is a finite, shared budget where every token
  competes for attention and pushes something else out, not a bucket to fill. From here
  the unit of engineering is the whole session, not one prompt.
  ([lesson](lessons/07-context-engineering-as-a-discipline.md))
- **[prompting-context-engineering/08] Context failure modes** - a cluttered context
  window fails through at least four nameable mechanisms - poisoning, distraction,
  confusion, and clash - and naming the mechanism tells you which fix applies.
  ([lesson](lessons/08-context-failure-modes.md))
- **[prompting-context-engineering/09] Retrieval and memory** - retrieval (fetching
  exactly what's relevant right now) and persistent memory (carrying facts across
  sessions) are related but distinct answers to a context window that's small relative
  to everything an agent might need to know; neither retrieval nor a bigger window is
  a universal winner. ([lesson](lessons/09-retrieval-and-memory.md))
- **[prompting-context-engineering/10] Context compaction and sub-agent handoff** - two
  structurally different escape hatches for a long-running task approaching its context
  budget: compacting the current thread's history, or handing remaining work to a fresh
  context. They are not interchangeable defaults, and choosing wrong quietly caps how
  far a long-horizon task can go. ([lesson](lessons/10-context-compaction-and-handoff.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on the concepts
rated `shaky` or `not-yet`.
