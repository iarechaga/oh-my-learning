---
id: tool-use-agentic-loop/02
subject: tool-use-agentic-loop
title: "Designing Tool Schemas: JSON Schema, Typed Arguments, and Description Quality"
slug: designing-tool-schemas
status: drafted
mastery:
seniority: mid
source: "Anthropic Platform docs: Define tools (2026); Anthropic Engineering: Writing tools for agents (2025); explainx.ai: Tool Definition and Schema Design for AI Agents - 2026 Guide (2026); apxml: Best Practices for Tool Input and Output Schemas (2026)"
durability: durable
prerequisites: [tool-use-agentic-loop/01]
created: 2026-08-10
updated: 2026-08-10
---

# Designing Tool Schemas: JSON Schema, Typed Arguments, and Description Quality

## TL;DR
A tool's name, description, and JSON-Schema-typed arguments are the *entire* interface the model has to decide whether to call it and how to fill in its arguments - it never sees your source code. Tool schema design is API design for a consumer that cannot ask clarifying questions mid-decision, doesn't read separate documentation, and forms every belief about what a tool does from three text fields you control. Most "the model picked the wrong tool" or "the model made up a value" failures are schema-design failures, not model failures.

## The idea
`tool-use-agentic-loop/01` established the three-part contract - name, description, input schema - and the mechanical round trip a tool call goes through. This lesson is about *authoring* that contract well, because the mechanism working correctly (a valid `tool_use` block getting parsed and executed) is a completely separate question from the *right* tool getting called with the *right* arguments.

Think about the asymmetry with human API consumers. A human engineer integrating a REST API can read separate prose documentation, run a debugger, ask a Slack channel, or infer intent from a well-known convention ("this is probably a pagination parameter, it's called `page`"). A model deciding whether to call `get_stock_price` versus `get_stock_history` versus answering from its own knowledge has none of that: it sees the `name`, `description`, and `input_schema` fields you wrote, in the same context window as everything else competing for its attention (per the context-budget framing in `prompting-context-engineering/07`), and it has to make a probabilistic judgment call from that alone, every single time the tool is offered. A vague description doesn't just under-inform a human reader who can go look something up - it directly increases the chance of a wrong or hallucinated tool call, because the model has nowhere else to look.

## How it works

### The schema has two audiences, and they want different things
An `input_schema` is real JSON Schema, valid enough that many implementations will also mechanically validate the model's output against it. But its *primary* audience is the model reading it as part of a prompt, not a validator parsing it as data. This produces a genuine design tension:
- **Terse fields are good for the machine-validation half** - short property names, minimal nesting, keep token cost down.
- **Rich descriptions are good for the model-comprehension half** - every property benefits from its own `description`, not just the top-level tool description, because the model uses per-field descriptions to decide *what value* to put there, not just *whether* to call the tool.

**Worked example - the same field, badly and well specified:**
```json
// Badly specified: the model has to guess format, units, and validity
{"ticker": {"type": "string"}}

// Well specified: format, and disambiguating example, are explicit
{"ticker": {"type": "string", "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."}}
```
The second version costs a handful of extra tokens and materially reduces the chance the model passes a company name ("Apple") where a ticker ("AAPL") was expected.

### Type constraints do real work: enums, required, and nesting
JSON Schema gives you more than "string vs. number" - and the stricter you can honestly be, the less room there is for the model to guess wrong:
- **`enum`** restricts a field to a fixed set of valid values, e.g. `"unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}`. This is stronger than describing the valid values in prose, because it removes an entire class of "close but invalid" outputs (`"Celsius"`, `"C"`, `"metric"`) that a prose description alone cannot fully prevent.
- **`required`** declares which arguments must be present before your code can safely execute the call; anything not listed is optional, and the model may omit it, infer a plausible default, or ask the user, depending on model and ambiguity (per the "missing required parameter" behavior noted in vendor docs - larger/more capable models tend to ask, smaller ones are more likely to guess).
- **Nested objects and arrays** let you model genuinely structured inputs (a list of line items, a filter object with sub-fields) rather than flattening everything into loosely-related top-level strings - but each level of nesting is a place the model can produce a malformed shape, so nesting should track genuine structure in the domain, not be added for its own sake.

**Worked example - required vs. optional changing model behavior.** A `book_flight` tool with `origin`, `destination`, and `date` all `required` will, when the user says "book me a flight to Denver" without a date, either force the model to ask a follow-up question (desirable) or - on a weaker model, under pressure to produce *some* tool call - guess a date (undesirable and dangerous for a booking action). Marking `date` optional with a description like `"date": {"type": "string", "description": "Departure date in YYYY-MM-DD. Omit if the user has not specified one - do not guess."}` gives the model an explicit, in-schema instruction not to fabricate the value, which is a stronger signal than hoping the system prompt's general tone discourages guessing.

### Description quality is the single highest-leverage lever you have
Across current vendor guidance, one recommendation recurs above all others: write extremely detailed tool descriptions - what the tool does, when to use it, when *not* to use it, what each parameter means, and any caveats about what the tool does *not* return. A commonly cited rule of thumb is a minimum of three to four sentences per tool description, more for complex tools - which is a striking contrast with ordinary software documentation conventions, precisely because this is the model's *only* source of truth about the tool.

**Worked example - side by side (adapted from current vendor guidance):**
```json
// Poor: leaves open questions about format, scope, and applicability
{
  "name": "get_stock_price",
  "description": "Gets the stock price for a ticker.",
  "input_schema": {"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}
}

// Good: states scope, valid input format, output format, and explicit non-scope
{
  "name": "get_stock_price",
  "description": "Retrieves the current stock price for a given ticker symbol. The ticker symbol must be a valid symbol for a publicly traded company on a major US stock exchange like NYSE or NASDAQ. The tool will return the latest trade price in USD. It should be used when the user asks about the current or most recent price of a specific stock. It will not provide any other information about the stock or company.",
  "input_schema": {
    "type": "object",
    "properties": {"ticker": {"type": "string", "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."}},
    "required": ["ticker"]
  }
}
```
The "good" version is roughly four times longer and costs real tokens on every call it's offered in - that cost is the trade-off this lesson is teaching you to make deliberately, not accidentally.

### Naming and consolidation shape the decision, before description even matters
Two structural choices determine how hard the model's job is *before* it reads a single description:
- **Disjoint, unambiguous names.** Tools named `delete_user`, `remove_user`, and `purge_user` invite wrong-tool selection because their names alone don't establish a clear boundary; if you find yourself writing a paragraph to explain the difference between two tools, that is a signal to rename, merge, or remove one of them rather than to write a longer description.
- **Namespacing at scale.** Once a tool library spans multiple services, prefixing names by service or resource (`github_list_prs`, `slack_send_message`) keeps tool selection unambiguous as the library grows, and matters even more once tools are being dynamically discovered/loaded rather than all listed up front.
- **Consolidation over proliferation.** Rather than one narrow tool per action (`create_pr`, `review_pr`, `merge_pr`), current vendor guidance recommends grouping related operations into a single tool with an `action` or `operation` discriminator parameter where it makes sense - fewer, more capable tools reduce the size of the decision space the model has to search on every turn. This is a judgment call, not an absolute: over-consolidating unrelated capabilities into one tool "to save tokens" trades a token savings for a correctness cost, because the model now has to get a second decision (which action?) right inside the first.

### Tool *output* shape is part of schema design too
Schema design does not stop at the input side. What a tool *returns* becomes the model's input on the very next call (per the round-trip mechanics of lesson 01), so it is subject to the exact same context-budget discipline as anything else entering the window: return stable, semantic identifiers (slugs, human-readable names) rather than opaque internal IDs the model cannot reason about, and include only the fields the model actually needs for its next decision. A tool that dumps an entire raw API response (hundreds of fields, deeply nested, mostly irrelevant) back into context is spending tokens and diluting attention on low-signal content just as surely as an over-included document would in ordinary context engineering.

### Optional structured examples, for schemas prose can't fully disambiguate
For tools with complex, nested, or format-sensitive inputs, some vendors support an explicit examples field alongside the schema (separate from natural-language few-shot examples in the prompt itself) - concrete, schema-valid sample inputs shown directly next to the schema definition. These exist because some structural patterns (which fields co-occur, how a discriminator field changes which other fields are relevant) are easier to demonstrate than to describe fully in prose, at a modest additional token cost per example.

## Pros
- Tight schemas materially reduce two of the most common agent failure modes at their source: wrong-tool selection and invalid/hallucinated arguments.
- The investment is legible and testable - you can write a battery of "does the model pick tool X for input Y" checks against a schema the same way you'd unit-test an API contract.
- Good schema design pays compounding dividends as a tool library grows: the discipline of disjoint names and clear scope boundaries is what keeps a 5-tool agent's reliability from collapsing once it becomes a 50-tool agent.

## Cons
- Verbose, well-specified descriptions cost real input tokens on every call the tool is offered in, which competes directly with the rest of the context budget (`prompting-context-engineering/07`) - this is a genuine trade-off, not a free improvement.
- Over-consolidating tools into fewer, larger multi-action schemas can shift ambiguity from "which tool" to "which action within this tool," which is not always a net win and needs its own testing.
- There is no fully mechanical way to know a description is "good enough" short of empirical evaluation against real or representative queries - schema quality is judged by measured tool-selection accuracy, not by a checklist alone.

## Alternatives
- **Minimal/terse schemas relying on the model's general world knowledge** — cheaper in tokens, and sometimes adequate for extremely common, unambiguous tools (a single well-known `get_current_time` tool rarely needs four sentences) - but fails as soon as the tool's behavior, scope, or format has anything non-obvious about it.
- **Enforced strict/constrained decoding** (`strict: true` or equivalent, noted in lesson 01) — guarantees schema-conformant output mechanically rather than relying on the model interpreting the schema correctly; complements good description-writing rather than replacing it, since strict mode guarantees the *shape* of the arguments, not that they're the *semantically correct* values for the user's actual intent.
- **A router/classifier model or rules engine in front of tool selection** — resolves "which tool" via a separate, purpose-built mechanism before the main model ever sees a tool menu, useful at very large tool-library scale; adds a separate component to build, maintain, and keep in sync with the tool library itself.

## When to use it
Invest deliberately in schema and description quality for any tool whose misuse has a real cost - ambiguous scope with a sibling tool, an action with side effects (writes, sends, deletes), or a format-sensitive argument (dates, IDs, units). The more consequential or confusable the tool, the more the extra sentences of description and the tighter the enum/required constraints pay for themselves.

## When NOT to use it
Don't over-invest in exhaustive descriptions and heavy structural constraints for a small number of clearly distinct, low-stakes, read-only tools in a simple agent - a two-tool assistant with `get_weather` and `get_time` doesn't need namespacing conventions or a consolidated `action` parameter; that machinery is solving a problem (ambiguity at scale) the system doesn't yet have, and the extra tokens and complexity are pure cost until the tool library actually grows into it.

## Key takeaways / mental model
Treat every tool definition as **the entire spec a stranger will ever get**, because that is literally true for the model: no source code, no separate docs, no chance to ask a clarifying question outside the conversation itself. Write the name to establish a clear, disjoint boundary; write the description like you're warning a new hire about exactly what this does, when to use it, when not to, and what it doesn't do; use `enum` and `required` to remove entire classes of invalid guesses rather than just describing validity in prose; and remember that what a tool *returns* becomes the model's next input, so keep it as high-signal as the arguments you demanded going in.

## Self-check questions
1. You have two tools, `search_orders` and `find_order`, with near-identical one-line descriptions. The model keeps calling the wrong one. Using only concepts from this lesson, list two structurally different fixes (not "write a longer description") and explain why each reduces ambiguity.
2. A `create_ticket` tool has a `priority` field typed as a free-form string. Redesign that one field using a JSON Schema construct from this lesson, and explain what specific failure mode it prevents that a better description alone would not.
3. Your team wants to add 30 new tools to an agent that currently has 6. Walk through which three structural principles from this lesson you'd apply before writing a single new description, and why order matters here.
4. A tool's description is excellent, but the tool's *output* is a raw 200-field API response dump. Explain, using the context-budget framing from `prompting-context-engineering/07`, why this is still a schema-design problem even though the input schema is fine.
5. Give a concrete example of a field where marking it `required` would cause harm, and explain what the model is likely to do differently when it's `optional` with a "do not guess" instruction in its description versus when it's silently `required`.

## References
- [Anthropic Platform docs: Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools)
- [Anthropic Engineering: Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- explainx.ai, "Tool Definition and Schema Design for AI Agents: 2026 Guide" (2026), https://www.explainx.ai/blog/tool-definition-schema-design-context-engineering-2026
- apxml, "Best Practices for Tool Input and Output Schemas" (2026), https://apxml.com/courses/building-advanced-llm-agent-tools/chapter-1-llm-agent-tooling-foundations/tool-input-output-schemas
