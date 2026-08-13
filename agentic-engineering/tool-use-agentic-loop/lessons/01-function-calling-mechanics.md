---
id: tool-use-agentic-loop/01
subject: tool-use-agentic-loop
title: "Function Calling Mechanics: How Models Choose and Emit Tool Calls"
slug: function-calling-mechanics
status: drafted
mastery:
seniority: mid
source: "Anthropic Platform docs: Tool use with Claude / How tool use works (2026); OpenAI Platform docs: Function calling guide (2026); Morph: OpenAI Function Calling - Complete Guide for Agent Builders (2026); RockB: LLM Function Calling and Tool Use Guide 2026 - OpenAI, Anthropic, Google (2026)"
durability: durable
prerequisites: [prompting-context-engineering/03]
created: 2026-08-10
updated: 2026-08-10
---

# Function Calling Mechanics: How Models Choose and Emit Tool Calls

## TL;DR
"Tool use" or "function calling" is not the model reaching out and executing code. The model only ever emits tokens; a tool call is a specially-structured chunk of output text (conventionally JSON) naming a function and its arguments, which the *calling application* - not the model - parses and actually executes. The result is then fed back in as ordinary text on the next call, because (per `prompting-context-engineering/01`) the model has no memory and no side channel to the outside world except the tokens you send it and the tokens it sends back.

## The idea
`prompting-context-engineering/03` covered how a well-chosen prompt, including a handful of in-context examples, steers a model's next-token predictions toward the output shape you want. Function calling is that exact mechanism applied to a very specific, high-stakes output shape: instead of steering the model toward "write a helpful paragraph," you steer it toward "emit a syntactically valid, schema-conforming description of which function to call and with what arguments."

The problem function calling solves is real and structural. A language model's only superpower is producing text conditioned on other text; it cannot look up today's stock price, query a database, run code, or send an email, because none of those things are text-generation. Before structured tool use existed, the workaround was to ask the model to describe, in prose, what it would do ("I would check the weather API for San Francisco") and have a human or a fragile regex parse that prose to trigger an action - unreliable, because natural language is not a stable interface for machine parsing. Function calling replaces "describe an action in prose" with "emit an action in a schema the calling program can parse deterministically." The model is not given a new capability; the *application* is given a reliable signal for when and how to invoke a capability it already has.

## How it works

### The three-part contract: name, description, schema
Every tool a model can call is defined by exactly three things, all supplied by you (the developer), not discovered by the model at runtime:
- a **name** the model must emit verbatim to invoke it,
- a **description** in plain language explaining what the tool does and when to use it,
- an **input schema** (near-universally JSON Schema) declaring the argument names, types, and which are required.

Nothing else about the tool is visible to the model. It cannot see your function's source code, your database schema, or your API's rate limits - it can only see what you wrote in these three fields. This matters practically: the model's decision of *whether* and *how* to call a tool is only as good as the English description you wrote, because that description is the only signal distinguishing "use this tool" from "answer from what I already know" or "use a different tool." (Writing good schemas and descriptions is the whole subject of the next lesson, `tool-use-agentic-loop/02`.)

**Worked example - a minimal tool definition** (schema shape shared, with field-name differences, across major vendors as of 2026):
```json
{
  "name": "get_weather",
  "description": "Get the current weather for a given location.",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {"type": "string", "description": "City and state, e.g. San Francisco, CA"}
    },
    "required": ["location"]
  }
}
```
This is sent alongside the conversation on every single call where the tool should be available - it is not "installed" once and remembered; per the statelessness lesson, if you omit it from a call, the model has no idea the tool exists for that call.

### The five-step round trip
A single tool call, end to end, is five discrete steps across two separate model invocations:

```
Step 1 (you)     -> send: [system] + [tool definitions] + [user message]
Step 2 (model)   -> emits: ordinary text tokens, UNTIL it starts emitting a
                    structured "I want to call tool X with arguments Y" block,
                    then STOPS generating (it does not "wait" - the API call
                    simply ends and returns control to your code)
Step 3 (you)     -> your application code parses that structured block,
                    executes the actual function/API call yourself
Step 4 (you)     -> send: everything from step 1 + the model's step-2 output
                    + a new block containing the tool's result, as a NEW
                    API call
Step 5 (model)   -> emits: ordinary text tokens again, now conditioned on
                    having "seen" the tool's result in its input
```

The critical detail, easy to miss: steps 2 and 5 are *two separate calls to the model*, and the model does nothing between them. It is not paused mid-thought waiting for an answer; the entire conversation - including its own prior "I'll call this tool" output and the result you fetched - is re-serialized as input text for a fresh, independent forward pass in step 5, exactly as described in the no-memory-between-calls mechanics of `prompting-context-engineering/01`. The model does not know the tool executed successfully, quickly, or at all except insofar as that information is present as text in the next call's input.

**Worked example - the get_weather round trip, using representative 2026 vendor conventions:**
1. You send the `get_weather` tool definition above plus the user message "What's the weather in San Francisco?"
2. The model's response is not free text; it is a structured call block, e.g. `{"type": "tool_use", "name": "get_weather", "input": {"location": "San Francisco, CA"}}`, and the API call ends with a status flag indicating "the model wants a tool run" rather than "the model is done talking" (vendors expose this as something like a `stop_reason: "tool_use"` field or a `finish_reason: "tool_calls"` field - the presence of the signal is durable, the exact field name is not).
3. Your code reads `location: "San Francisco, CA"`, calls whatever *your* weather API actually is, and gets back `"15 degrees Celsius, partly cloudy"`.
4. You send a new call containing the full prior conversation, the model's tool-call block, and a new block pairing that result back to the specific call that requested it (typically via an ID the model issued in step 2, so the model can tell which result answers which call if several were in flight).
5. The model, now "seeing" the weather as plain text in its input, emits: "The current weather in San Francisco is 15 degrees Celsius with partly cloudy skies."

Nothing about steps 3 or the weather API itself was ever "known" to the model - it only ever manipulated tokens describing an intent to call, and tokens describing a result.

### Controlling whether and which tool gets called
Because a tool call is just a probability-weighted output choice like any other token sequence, whether the model calls a tool at all is controllable the same way any generation behavior is controllable - through explicit constraints, not just prompting:
- **Automatic** (commonly the default): the model decides per-turn whether the request is better served by calling a tool or answering directly, based on matching the user's need against each tool's description.
- **Forced/required**: the calling application can constrain the model to must call *some* tool, or *one specific named* tool, or explicitly forbid tool calls this turn - useful when your application logic already knows a tool call is needed and doesn't want to gamble on the model's judgment call.
- **Parallel vs. single**: some vendors allow (or must be explicitly told to allow/disallow) the model to emit *several* tool-call blocks in one response, to be executed together rather than one round trip at a time - covered in depth, with its correctness trade-offs, in `tool-use-agentic-loop/04`.

### Argument-schema conformance is not automatically guaranteed
Because the arguments are produced by the same next-token sampling process as any other text, a model can - especially under ambiguous prompts, weaker models, or higher sampling temperature - emit an argument value that doesn't strictly satisfy the schema (a missing required field, a string where a number was declared, a plausible-looking but invented value for a parameter the user never specified). Multiple vendors as of 2026 offer an opt-in "strict" or constrained-decoding mode that mechanically restricts sampling to only tokens that keep the output schema-valid, closing this gap at some cost (often incompatibility with parallel tool calls, or added latency). Without strict mode, your application must still validate the parsed arguments before executing anything against them - the schema is a *request* to the model, not a guarantee from it, unless you've explicitly turned on the stricter mode.

## Pros
- Turns "the model wants to do something in the world" into a deterministic, machine-parseable event instead of prose the application has to guess-parse, which is what makes reliable agentic systems possible at all.
- Decouples capability from the model: any function you can write and describe becomes something the model can invoke, without retraining or fine-tuning.
- The three-part contract (name/description/schema) is a small, auditable surface - you can reason about exactly what information the model had available when it decided to call (or not call) a tool.

## Cons
- The model's tool-selection quality is bounded by how well you wrote the description and schema - vague or overlapping tool descriptions produce wrong-tool or no-tool-call failures that look like "the model is confused" but are really a specification problem.
- Every tool definition you include costs input tokens on every single call where it's available (per the context-window-as-budget framing in `prompting-context-engineering/07`), so tool availability is itself a context-budgeting decision, not a free switch to flip on.
- Without strict/constrained decoding, argument conformance is probabilistic, not guaranteed - production systems must validate parsed arguments defensively regardless of how well-specified the schema looks.

## Alternatives
- **Prose-parsing / regex-based action extraction (pre-2023 pattern)** — ask the model to describe its intended action in free text and parse it with brittle string matching; superseded almost entirely by structured tool use because natural language is not a stable machine interface.
- **Fine-tuning a model on a fixed action space** — bakes a small, closed set of actions directly into model weights instead of describing them per-call; can reduce per-call token overhead for a stable, unchanging tool set, but loses the flexibility of adding/removing/versioning tools without retraining, which structured tool use gives you for free.
- **Deterministic rule-based dispatch (no model in the loop for the decision)** — a classic if/else or intent-classifier router picks the function to call; cheaper and fully predictable for narrow, well-enumerated intents, but doesn't scale to open-ended requests where the right action depends on nuanced understanding of free-form user input.

## When to use it
Reach for structured tool/function calling whenever a task requires the model's output to trigger a real action or retrieve real information outside its training data and the current context - looking up live data, performing a calculation precisely, reading or writing a file, calling an internal API. It is the correct default mechanism (over prose-parsing) any time reliability of the "what does the model want to do" signal matters.

## When NOT to use it
Skip tool definitions entirely for requests fully answerable from the model's own knowledge and the context already provided - creative writing, summarizing text already in the prompt, general explanation. Every tool definition is a real, recurring token cost and a real chance of a wrong or unnecessary tool call; don't wire up a calculator tool for a model that can already reliably do the arithmetic you're asking for, and don't give a chat assistant fifteen tools "just in case" when the conversation only ever needs three.

## Key takeaways / mental model
A tool call is output, not action: **(model emits structured intent) -> (your code executes it) -> (your code re-injects the result as input) -> (model continues, now conditioned on that result)**. The model never touches the outside world directly; your application is the hands, the model is only ever deciding, from tokens, what it would like the hands to do next - and it makes that decision no differently than it decides any other next token, by pattern-matching your tool's name, description, and schema against the conversation so far.

## Self-check questions
1. A tool call "fails silently" - the model calls `get_weather` with `location: "SF"` but your weather API expects full state names and errors out. Walk through, step by step, what the model does and does not know at each stage, and what you would change to fix it.
2. Why can't the model just "call the API itself" the way a backend service would? Answer in terms of what a model fundamentally is (tie back to `prompting-context-engineering/01`).
3. Your agent has 40 tools defined, each with a 150-token description, and the model keeps picking the wrong tool among three similar ones. Using only the concepts in this lesson (not lesson 02's schema-design techniques), name two mechanisms available to you to reduce ambiguity right now.
4. A colleague says "forcing tool_choice to a specific tool removes the need for a good description, since the model has no choice anyway." Is that true? Justify your answer using the round-trip mechanics above.
5. Explain why a tool call and its result must be two separate API calls rather than one, given what you know about autoregressive generation and statelessness.

## References
- [Anthropic Platform docs: Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [OpenAI Platform docs: Function calling guide](https://platform.openai.com/docs/guides/function-calling)
- Morph, "OpenAI Function Calling: Complete Guide for Agent Builders (2026)" (2026), https://www.morphllm.com/openai-function-calling
- RockB, "LLM Function Calling and Tool Use Guide 2026: OpenAI, Anthropic, Google" (2026), https://baeseokjae.github.io/posts/llm-function-calling-tool-use-guide-2026/
