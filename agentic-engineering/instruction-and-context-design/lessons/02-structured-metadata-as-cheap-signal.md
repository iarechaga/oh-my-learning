---
id: instruction-and-context-design/02
subject: instruction-and-context-design
title: "Structured Metadata as Cheap Signal: Front Matter, Schemas, and Machine-Readable Config"
slug: structured-metadata-as-cheap-signal
status: drafted
mastery:
seniority: mid
source: "Anthropic platform docs: Skill authoring best practices (2026); Anthropic platform docs: Agent Skills overview (2026); Anthropic engineering blog: Writing effective tools for AI agents (2025)"
durability: durable
prerequisites: [instruction-and-context-design/01]
created: 2026-08-10
updated: 2026-08-10
---

# Structured Metadata as Cheap Signal: Front Matter, Schemas, and Machine-Readable Config

## TL;DR
A tiny, structured, machine-readable header - a handful of key-value fields sitting in front of a much larger body of prose - lets both tooling and the model itself answer cheap questions ("does this exist, is it relevant, what does it need") without paying the token cost of the full content. This pattern (front matter, JSON schemas, config blocks) is what makes the always-loaded/on-demand split from lesson 01 actually work in practice: the metadata is what's always loaded; the body is what's deferred.

## The idea
Lesson 01 established that an agent's instructions live on several distinct surfaces, and that some of those surfaces (skills, tool bodies, on-demand documents) are only pulled into context when relevant. But "only load it when relevant" raises an immediate mechanical question: relevant according to *what*? Something has to represent each deferred piece of content cheaply enough to sit in the always-loaded budget, so that a decision about whether to load the rest can even be made. That cheap representative is structured metadata.

The core insight is a separation of concerns between two very different kinds of content: a small amount of *data about the content* (its name, a description of what it does and when it applies, maybe its inputs/outputs) versus the *content itself* (the actual instructions, code, or knowledge). The metadata is written once, stays tiny, and is cheap enough to keep permanently in context for every candidate piece of deferred content - tens or hundreds of them, if needed. The body is written once and can be arbitrarily large, because it is never paid for until something has already decided, from the metadata alone, that it's worth reading. This is the same discovery-then-fetch pattern used throughout computing (a search index versus the documents it indexes, a function signature versus its implementation) applied to the specific problem of letting a model decide, cheaply, what to read next.

## How it works

### The two-tier cost structure
Structured metadata only earns its keep if it is dramatically cheaper than the content it describes, and if it's expressive enough to support a real relevance judgment. Concretely, for a well-designed piece of deferred content:

```
Tier                Token cost      When paid              Who reads it
---------------------------------------------------------------------------
Metadata (name +    ~50-150 tokens  Always, every turn      Model, to decide
description)                        the surface is active   relevance
Body (instructions)  100s-1000s of  Only when metadata      Model, once
                      tokens         judged it relevant       triggered
Bundled resources     unbounded      Only when the body      Model, if the
(reference files,                    explicitly references    body's own
 scripts, schemas)                   them                      references say to
```

> **Example (Aug 2026):** in the Agent Skills open standard, a skill's YAML front matter (`name` and `description`) is loaded into every session's system prompt at roughly 100 tokens per skill, while the full instruction body is only read - by the model issuing a file-read command - once that skill is judged relevant to the current request; further reference files bundled with the skill cost nothing at all until the model's own exploration reads them. This specific mechanism (a VM filesystem the model navigates with shell commands) is one concrete implementation of the tiered-cost idea; the durable point is the tiering itself, not this exact plumbing.

The three-tier structure matters because it lets the number of "candidate things the agent could know about" scale far beyond what could ever fit as full content in a context window. A hundred candidate skills at ~100 tokens of metadata each is 10,000 tokens - a real but bounded cost. A hundred candidate skills at their full body size, all loaded permanently, could easily be hundreds of thousands of tokens - well past what any budget in lesson prompting-context-engineering/07 would tolerate.

### What makes metadata "cheap" in more than just tokens
Token cost is only part of it. Structured metadata (as opposed to unstructured prose that happens to be short) is cheap in a second, equally important way: it's *parseable*. A YAML or JSON front-matter block with fixed field names (`name:`, `description:`, `prerequisites:`) can be extracted, validated, indexed, and displayed by ordinary code without any model call at all. This is exactly how this repository's own tooling works:

> **Example (Aug 2026):** in this repository, every lesson file carries YAML front matter with fields like `id`, `subject`, `seniority`, and `status`. A plain Python script (`scripts/generate_catalog.py`) parses that front matter across every lesson file and regenerates the root `CATALOG.md` index - no model involved, because the metadata is structured enough for ordinary code to consume directly. The lesson body itself (the prose under "## The idea", "## How it works", and so on) is exactly the part that script never touches; it's unstructured prose meant for a human or a model to read, not for a parser to extract fields from.

This is the general pattern: structured metadata does double duty. It's cheap enough for a model to keep permanently in its own context (supporting the relevance-judgment use case from lesson 01), and it's regular enough for deterministic tooling to consume without any model in the loop at all (supporting indexing, validation, and generation use cases that have nothing to do with an agent's runtime behavior).

### Worked example: what belongs in metadata versus body
Consider designing the metadata for a piece of deferred content - say, a reusable procedure for handling database migrations. A first draft might try to cram everything in:

```yaml
# Too much in metadata - defeats the purpose
---
name: db-migrations
description: |
  This covers our migration process. First you check the schema
  version, then you check for pending migrations, then you run
  them one at a time with --dry-run first, then you check output
  for warnings about foreign key constraints, then... [800 more words]
---
```

This fails the cost test - the "metadata" is now expensive enough that keeping it always-loaded reproduces exactly the problem structured metadata exists to avoid. A well-scoped version keeps metadata to *just* what's needed to answer the relevance question, and defers everything else:

```yaml
---
name: db-migrations
description: >
  Runs database schema migrations safely, including dry-run
  validation and foreign-key constraint checks. Use when the user
  asks to run, write, or review a database migration, or mentions
  schema changes to a table.
---
```

The full 800-word procedure - the actual step-by-step - belongs in the body, read only once this ~40-word description has already done its job of getting the content selected. This split is the practical answer to "how much detail should the description have": enough to support an accurate relevance judgment (lesson 04 covers this in depth), and not one token more.

### Worked example: schemas as metadata for tool arguments
The same tiering shows up in tool/function definitions, not just skills. A tool's *name and one-line description* is metadata about the tool's existence and purpose - cheap, always visible when the tool is available. Its *argument schema* (a JSON Schema specifying parameter names, types, and constraints) is a second, more detailed layer of metadata - richer than the name/description pair, but still far cheaper than a body of prose explaining the same constraints:

```json
{
  "name": "create_calendar_event",
  "description": "Creates a calendar event. Use when the user asks to schedule, book, or add a meeting or event.",
  "input_schema": {
    "type": "object",
    "properties": {
      "start_time": {"type": "string", "format": "date-time"},
      "end_time":   {"type": "string", "format": "date-time"},
      "attendees":  {"type": "array", "items": {"type": "string", "format": "email"}}
    },
    "required": ["start_time", "end_time"]
  }
}
```

Anthropic's own published guidance on tool design treats this schema as load-bearing signal in exactly the structured-metadata sense: precise, unambiguous field names and types (`start_time` as an ISO datetime, not a vague `time` string) let the model construct a correct call without any additional prose explaining the format - the structure itself carries information that would otherwise have to be spelled out in expensive natural language. The same source reports that refining tool descriptions and schemas (not the underlying model) produced measurable jumps in a coding agent's benchmark performance, evidence that this metadata layer is not cosmetic - it materially changes whether the model uses the tool correctly.

### Machine-readable config as a third variant
A related but distinct use of structured metadata is machine-readable *configuration* - fields that aren't primarily there to help the model decide relevance, but to let deterministic code (the harness, a build script, a CI check) drive behavior without any model judgment at all. This repository's lesson front matter mixes both: `description`-shaped fields like a skill's trigger text are metadata *for the model*; fields like `status: drafted` or `prerequisites: [...]` are metadata *for tooling* - they drive `generate_catalog.py`'s output and could drive dependency-ordering logic, and no model needs to read them for that to work. Recognizing which kind of metadata you're authoring - model-facing signal versus tooling-facing config - avoids a common mistake: writing a field in prose that a human finds readable but that a parser can't reliably extract, when a fixed key-value pair would have served the tooling use case far better.

## Pros
- **Massively cheaper discovery.** A relevance judgment over metadata costs a small, roughly constant amount per candidate, letting an agent's effective library of deferred knowledge scale to hundreds of entries without touching the always-loaded budget in any serious way.
- **Machine-consumable for free.** Structured fields can be validated, indexed, diffed, and rendered by ordinary code, decoupling "keep the catalog/index correct" from any model call - this is strictly more reliable than asking a model to summarize a body of content into a description on the fly, every time.
- **Forces a useful discipline on authors.** Having to compress a piece of content down into a ~50-150 token description is a good check on scope: content that can't be honestly summarized that small is often really two pieces of content that should be split (a symptom, not just a metadata-writing problem).
- **Decouples relevance-judgment quality from body quality.** You can iterate on a description's triggering accuracy independently of the underlying procedure's correctness, which makes debugging under-triggering or over-triggering (lesson 05) far more tractable than if the two were tangled together in one blob of prose.

## Cons
- **A second thing to keep in sync.** Metadata that drifts from what the body actually does (a description says "use for X" but the body was updated to also handle Y) creates exactly the kind of quiet mismatch that causes under-triggering - the cost of the pattern is an ongoing maintenance obligation, not a one-time authoring cost.
- **Compressing well is a real skill, not a formality.** A vague or overly broad description defeats the entire mechanism (this is the core subject of lesson 04); writing good structured metadata is harder than it looks and is worth deliberate effort, not boilerplate.
- **Schema/format rigidity has a floor.** Fixed key names and types are great for tooling but can't express everything a human-readable paragraph could - some nuance genuinely needs prose, and forcing it into rigid fields can lose information or produce awkward, over-engineered schemas for content that didn't need one.
- **Not free at scale either.** Even at ~100 tokens each, metadata for a very large number of candidates (hundreds to low thousands) starts to matter; the tiering reduces the problem, it doesn't eliminate the need to still think about budget once the candidate count gets large.

## Alternatives
- **No metadata layer; summarize content on demand with a model call** - avoids authoring structured fields up front, but costs a model call (latency and money) every time relevance needs to be judged, and produces inconsistent summaries run to run. Reasonable only for small, ad hoc, one-off situations, not for a stable library of reusable content.
- **Full-text search / keyword indexing over the body content** - cheap to build with standard tooling and doesn't require an author to hand-write a description at all. Fails to capture "when to use this," which is a judgment about intent and context, not just term overlap - lesson 04 covers in depth why keyword matching under- and over-fires compared to a model reading a well-written description.
- **Load everything, always** - the simplest possible design, no metadata layer needed at all. Directly reproduces the token-budget problem this whole subject exists to solve; viable only when the total candidate content is small enough to fit comfortably in the always-loaded budget (see lesson 03 for exactly where that line sits).

## When to use it
Use a structured-metadata layer whenever you're building any form of on-demand or deferred content - skills, tool definitions, retrievable documents, a catalog of reusable procedures - and the number of candidates is more than a handful. It's also worth adopting purely for the tooling benefit (deterministic parsing, validation, generation) even in cases where model-facing relevance-judgment isn't the primary goal, any time you want indexes, dashboards, or checks to stay correct without manual upkeep.

## When NOT to use it
Skip building a metadata layer for a single piece of content, or for a small, fixed handful of items that will simply all be always-loaded anyway - the overhead of maintaining a separate description in sync with the body isn't worth it below a certain count. Also avoid over-engineering the schema itself: a two-field front matter (name, description) is often sufficient, and adding a dozen rigid config fields "just in case" before any tooling actually consumes them is speculative complexity with no present payoff.

## Key takeaways / mental model
Think of structured metadata as a library's card catalog, not the books themselves: a fixed-format card (author, title, one-line description, call number) costs almost nothing to keep in a drawer you can flip through in seconds, while the book it describes might be four hundred pages you only pull off the shelf once the card convinces you it's the right one. The discipline is keeping the card honest and small - if the card starts trying to summarize every chapter, it's stopped being a card and become a second, worse copy of the book. Every deferred piece of content in an agent system needs exactly this kind of card: cheap enough to keep on permanent display, accurate enough to make the fetch-or-skip decision correctly.

## Self-check questions
1. A colleague writes a skill description that's 600 tokens long because "I want to make sure the model has everything it needs to decide." Using this lesson's cost-tiering argument, explain what's wrong with that reasoning and what should happen to that 600 tokens instead.
2. You maintain a catalog of 40 reusable procedures, each with front matter. What two categories of consumer read that front matter, and why does designing for both change how you'd write the fields compared to designing for just one?
3. Design a minimal metadata schema (list the fields, not full prose) for a hypothetical "customer support macro" library, where each macro handles one type of support ticket. What's model-facing signal, and what's tooling-facing config?
4. A tool's argument schema requires a `user_id` field typed as a string with no further constraint, and the agent frequently passes an email address where an internal numeric ID was expected. Using the reasoning from the schema worked example, what would you change, and why is that a metadata fix rather than a body/prompt fix?
5. Explain the difference between metadata drifting out of sync with its body (a maintenance failure) and metadata that was too vague from the start (an authoring failure). Why does distinguishing them matter for how you'd fix each?

## References
- [Anthropic platform docs: Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic platform docs: Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Anthropic engineering blog: Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- This repository's own lesson front matter and `scripts/generate_catalog.py` (accessed 2026-08)
