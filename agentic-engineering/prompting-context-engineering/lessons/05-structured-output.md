---
id: prompting-context-engineering/05
subject: prompting-context-engineering
title: "Structured Output: Constrained Decoding and Why It Beats Free-Form Parsing"
slug: structured-output
status: drafted
mastery:
seniority: mid
source: "OpenAI docs: Structured model outputs (2026); OpenAI docs: Function calling (2026); Anthropic docs: Structured Outputs (2026); zeroentropy.dev: Constrained decoding (2026); arXiv:2502.05111 Flexible and Efficient Grammar-Constrained Decoding (2025); arXiv:2501.10868 JSONSchemaBench (2025); arXiv:2408.02442 Let Me Speak Freely? (2024)"
durability: durable
prerequisites: [prompting-context-engineering/03]
created: 2026-08-10
updated: 2026-08-10
---

# Structured Output: Constrained Decoding and Why It Beats Free-Form Parsing

## TL;DR
An LLM generates text one token at a time from a probability distribution; constrained decoding masks that distribution at every step so only tokens matching a schema, grammar, or regex can ever be chosen, which turns "the model produced valid JSON" from a probabilistic hope into a mechanical guarantee. This is different from - and strictly stronger than - asking nicely in a prompt for JSON and then parsing the reply.

## The idea
Every application that hands an LLM's output to another program - a database insert, a function call, a downstream API - needs that output to be machine-parseable, not just human-readable. For years the default technique was **prompt-and-parse**: tell the model "respond only in JSON matching this shape," get back text, run it through `JSON.parse`, and write a retry loop for when parsing fails. This works most of the time, and "most of the time" is exactly the problem. A pipeline that silently drops or retries on a 2-5% failure rate is a pipeline with an invisible tax that shows up as flaky tests, mystery support tickets, and support-cost spikes at 3 a.m. when a slightly unusual input nudges the model into adding a trailing comment or wrapping the JSON in prose.

The underlying cause is structural, not a matter of better wording. An LLM does not "decide to write JSON" and then execute that decision faithfully - it samples the next token from a probability distribution over its entire vocabulary, one token at a time, and nothing in that sampling step inherently forbids picking a token that breaks the JSON grammar. A system prompt shifts the *probabilities* toward well-formed output; it does not remove the illegal tokens from the distribution. Constrained decoding removes them. Instead of asking the model to behave, it changes what the model is *allowed* to emit at each step, so the invalid paths simply do not exist in the search space.

This reframes structured output from a prompting problem into a decoding-time architecture problem - which is why it belongs in this subject as its own concept rather than as a bullet point under "prompting techniques."

## How it works

### Two different mechanisms, often confused
There are two distinct techniques that get lumped together as "structured output," and the distinction matters for reasoning about guarantees:

1. **Prompt-based formatting (soft constraint).** You describe the desired shape in the system or user prompt ("respond with a JSON object containing `name` and `age`"), sometimes reinforced with few-shot examples (lesson 03). The model tries to comply because it was trained on instruction-following and because the prompt biases its next-token probabilities toward compliant tokens. Nothing prevents non-compliance; you are relying on the model's learned behavior.
2. **Constrained (grammar-guided) decoding (hard constraint).** The inference engine maintains a formal grammar (typically compiled from a JSON Schema, a regex, or a context-free grammar) and, at every decoding step, computes which tokens in the vocabulary would keep the output a valid continuation of that grammar. Every other token's probability (technically its logit) is set to negative infinity before sampling, so it has zero chance of being chosen. The model can still choose *which* valid token to emit - it retains its "creative" choice among legal options - but it cannot choose an illegal one.

Prompt-based formatting is necessary but not sufficient: even with constrained decoding turned on, you still write a clear prompt/schema description so the model's *content* (which fields to fill, what values to pick) is good. Constrained decoding guarantees the *shape*; it says nothing about whether the values inside that shape are correct, complete, or non-hallucinated. Both layers matter and address different failure classes.

### The mechanics: masking the vocabulary, one token at a time
Concretely, the engine compiles a schema (say, a JSON Schema requiring `{"name": string, "age": integer}`) into a state machine - a finite automaton for simple grammars, or a pushdown automaton / Earley parser for recursive structures like nested objects and arrays. At each decoding step:

```
Step N: model has generated so far:  {"name": "Ada", "age":
Current grammar state: expecting a JSON number (integer), then '}'

Vocabulary before masking:  [ "1", "2", ... "Ada", "true", "}", "\"", ... ]  (~100K+ tokens)
Grammar-valid tokens now:   [ "0","1",...,"9", " " (leading space), "-" ]     (a small subset)

Mask: set logit = -infinity for every token NOT in the valid set
Sample from the remaining (masked) distribution -> model picks "3", "0"
Continue until grammar reaches an accepting state (sees closing "}")
```

The model's underlying weights and its probability estimates over "plausible" tokens are untouched - masking happens *after* the model computes its distribution and *before* sampling. This is why constrained decoding does not require retraining or fine-tuning the model: it is a decode-time filter layered on top of any model that exposes token-level logits.

### Worked example: computing the reliability gap
Suppose you are extracting structured records from 50,000 support tickets a day, each requiring a JSON object with 6 fields. Assume prompt-and-parse achieves 97% first-try valid JSON (a realistic, even generous, number for a moderately complex schema per industry benchmarking such as JSONSchemaBench-style evaluations), while constrained decoding achieves effectively 100% schema-valid output (the standard result reported by vendors and grammar-decoding libraries as of 2026, since malformed output is structurally impossible, not just unlikely).

- Prompt-and-parse: 50,000 x 3% = **1,500 tickets/day** fail parsing and need a retry, a fallback parser, or a dropped record.
- Each retry costs a second full model call. At an illustrative $0.01/call, that is **$15/day** in pure retry cost, plus the latency of a second round trip for every one of those 1,500 tickets, plus whatever downstream logic has to special-case "parse failed."
- Constrained decoding: **0 tickets/day** fail on shape (some may still have wrong *content*, e.g. a hallucinated field value - that is a separate problem, see "Cons" below).

At small scale a 3% failure rate is a nuisance you patch with a retry loop. At the scale most production agentic systems operate (hundreds of thousands to millions of structured extractions per day), that 3% becomes a standing operational cost and a source of silent data loss whenever the retry loop itself has a bug or a rate limit.

### Worked example: why free-form parsing breaks in ways prompts can't prevent
Consider asking a model, purely via prompt instructions, to output a JSON array of product recommendations. A plausible failure is the model prefacing its answer with a courteous sentence:

```
Here are three great picks based on your preferences:
[
  {"id": "sku_1029", "reason": "matches your stated budget"},
  {"id": "sku_2044", "reason": "top-rated in category"},
  {"id": "sku_3811", "reason": "frequently bought together"}
]
```

`JSON.parse()` on the full string throws immediately - the leading sentence is not valid JSON. You can mitigate this with regex extraction of the first `[...]` block, but that is now a second parser you maintain, with its own edge cases (what if the model emits *two* bracketed blocks, one in an example inside its explanation?). Under constrained decoding, the grammar for "a JSON array matching this schema" simply does not include a token sequence for "Here are three great picks" as a legal prefix - the very first token is forced to be `[` (or whitespace then `[`), so the preface cannot exist in the output at all. The failure mode is not patched after the fact; it is made structurally unreachable.

### Where the technique lives in practice
As of 2026, constrained decoding for structured output is offered by every major model provider and by the open-source serving stack, though the exact API surface differs by vendor and changes over time - treat any specific product name here as a dated, swappable example, not the concept itself.

> **Example (Aug 2026):** OpenAI's API offers a `response_format` / structured-outputs mode with reported 100% schema-compliance in vendor evaluations (versus roughly 86% for plain function-calling JSON and lower for unconstrained JSON mode). Anthropic's API offers a comparable structured-outputs mode. Open-source serving engines (vLLM, SGLang, TensorRT-LLM) commonly use libraries such as XGrammar or llguidance to do grammar-constrained decoding with reported sub-100-microsecond per-token overhead. Check current vendor docs for exact guarantees and supported schema subsets - they evolve every few months.

### Constrained decoding and reasoning: an interaction to watch
A subtlety worth internalizing: forcing a rigid output grammar from the very first token can conflict with a model's need to "think" before answering (chain-of-thought, covered in lesson 04). If you constrain the *entire* response to a terse JSON object, you may be cutting off the reasoning tokens that would have produced a better answer. The common pattern is to let the model reason freely first (unconstrained or lightly constrained), then constrain only a final, clearly delimited answer block to the schema - separating "let it think" from "make the final answer machine-readable" rather than constraining the whole generation from token one.

## Pros
- **Mechanical guarantee, not a probability.** Schema-valid output every time, eliminating an entire class of parsing failures rather than reducing their frequency.
- **Removes a whole layer of defensive code.** No regex extraction, no "strip markdown fences," no retry-on-parse-failure loop.
- **Composability.** A guaranteed shape lets you chain structured outputs directly into typed downstream code (deserialize straight into a class/struct) without a validation gate in between.
- **Often near-zero latency/throughput cost** with modern engines (finite-state or Earley-based maskers add microseconds per token, not seconds), so the reliability gain is close to free at inference time.

## Cons
- **Guarantees shape, not truth.** A constrained model can still emit a perfectly schema-valid JSON object with a hallucinated field value - the classic "confidently wrong but well-formatted" failure. Structured output is not a hallucination fix.
- **Schema expressiveness limits.** Very complex or deeply recursive schemas, or schemas requiring cross-field constraints ("field B must be greater than field A"), may not be fully expressible in the grammar formats supported by a given engine; you may need to fall back to post-hoc validation for those constraints.
- **Some research suggests format restrictions can measurably hurt reasoning-heavy task accuracy** when the constraint is applied too early or too rigidly, by cutting off the token sequences a model would otherwise use to "think" (see arXiv:2408.02442). This is mitigated, not eliminated, by constraining only the final answer segment.
- **Engine/vendor support varies.** Not every model, every hosting provider, or every schema feature (e.g. `oneOf`, recursive `$ref`) is uniformly supported; portability across providers is not guaranteed as of 2026.
- **A false sense of security.** Teams sometimes treat "the JSON parsed" as "the extraction is correct" and skip content-level evaluation entirely, because the shape-level failure mode they used to see (parse errors) has disappeared.

## Alternatives
- **Free-form generation + a validation/repair loop** - ask for JSON in the prompt, validate against a schema after the fact, and re-prompt with the validation error on failure. Preferable only when the serving stack genuinely has no constrained-decoding support (e.g. a model you cannot control decoding for, or a purely prompt-only API), or for exploratory/low-volume use where the retry cost is negligible.
- **Few-shot examples alone** (lesson 03) to bias the model toward a format, with no hard enforcement. Cheaper to implement, weaker guarantee; reasonable for prototypes, risky in production.
- **A second "extractor" model or deterministic parser** that turns unconstrained natural-language output into structured data downstream. Useful when the generating model cannot be constrained at all (e.g. a third-party chat UI with no API-level control), at the cost of an extra hop and its own failure surface.
- **Fine-tuning the model on the target format** so it reliably emits correct shape without explicit grammar enforcement. Reduces but does not eliminate malformed output, is far more expensive to set up and maintain than turning on a decoding flag, and is only worth it when constrained decoding is unavailable for your serving stack.

## When to use it
Use constrained/structured output whenever a model's response feeds directly into code: function-call arguments, database records, API request bodies, form-filling, classification labels drawn from a fixed enum, or any pipeline stage where a downstream parser would otherwise throw on malformed input. It is close to a default-on choice in 2026 for any agentic system with tool use, since tool-call arguments are exactly this kind of machine-consumed output.

## When NOT to use it
Skip it for the model's free-form, human-facing prose - a chat reply, an explanation, a piece of creative writing - where forcing rigid structure would degrade quality with no downstream parser to benefit. Also be cautious applying a tight constraint to the *entire* output of a task that genuinely benefits from open-ended reasoning before it commits to an answer (see the chain-of-thought interaction above); constrain the final answer segment, not the whole generation, in those cases. And do not treat it as a substitute for evaluating whether the *content* is correct - pair it with the same content-quality checks (evals, spot review, downstream business-rule validation) you would use for any generated output.

## Key takeaways / mental model
Think of prompt-and-parse as "ask politely and check afterward" and constrained decoding as "make the wrong answer physically impossible to produce." The former is a probability you are shrinking through better wording; the latter is a search-space restriction that removes the bad outcomes from existence. Constrained decoding solves the *shape* problem completely and the *truth* problem not at all - you still need everything else in this subject (clear prompts, good context, retrieval where relevant) to make sure the correctly-shaped answer is also a correct one.

## Self-check questions
1. Your team is deciding whether to add constrained decoding to a pipeline that currently does prompt-and-parse with a 4% JSON-parse failure rate, processing 200,000 requests/day. Walk through the operational cost of the current failure rate versus what changes (and doesn't change) if you switch.
2. A colleague says "we switched to structured outputs, so we can turn off our field-level validation." Explain what's wrong with that reasoning using the shape-vs-truth distinction.
3. You need a model to output a deeply nested, recursive schema (a file-tree structure with arbitrary depth) and the serving engine's grammar support is limited to non-recursive JSON Schema. What are your options?
4. Why might forcing a rigid output schema from the very first generated token hurt accuracy on a task that requires multi-step reasoning, and what's the standard mitigation?
5. Design a small worked comparison (with made-up but realistic numbers) showing the retry cost of prompt-and-parse versus the near-zero shape-failure cost of constrained decoding at two different volumes: 1,000 requests/day and 1,000,000 requests/day. At what point, if any, does the operational argument for constrained decoding become undeniable?

## References
- [OpenAI docs: Structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [OpenAI docs: Function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [OpenAI: Introducing Structured Outputs in the API](https://openai.com/index/introducing-structured-outputs-in-the-api/)
- [zeroentropy.dev: Constrained decoding - forcing LLM output to a grammar](https://zeroentropy.dev/concepts/constrained-decoding/)
- arXiv:2502.05111 - Flexible and Efficient Grammar-Constrained Decoding
- arXiv:2501.10868 - JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language Models
- arXiv:2408.02442 - Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models
- arXiv:2603.03305 - The Hidden Cost of Structured Generation in LLMs: Draft-Conditioned Constrained Decoding
