---
id: prompting-context-engineering/03
subject: prompting-context-engineering
title: "Core Prompting Techniques: Few-Shot, Role, and Output Formatting"
slug: core-prompting-techniques
status: drafted
mastery:
seniority: mid
source: "arXiv:2406.06608 The Prompt Report: A Systematic Survey of Prompting Techniques (2024, rev. 2025); Anthropic Claude Docs: Be clear, direct, and detailed (2026); Anthropic, Prompt engineering best practices for 2026 (2026); PromptHub, The Few Shot Prompting Guide (2025)"
durability: durable
prerequisites: [prompting-context-engineering/02]
created: 2026-08-10
updated: 2026-08-10
---

# Core Prompting Techniques: Few-Shot, Role, and Output Formatting

## TL;DR
Three techniques do most of the practical work in everyday prompting: **few-shot examples** (showing the model input/output pairs so it infers the pattern rather than having it described), **role prompting** (framing the model's persona/expertise to shift tone and depth), and **explicit output formatting** (telling the model exactly what shape the response must take). Each works through in-context learning - the model conditions its next-token predictions on patterns present in the prompt itself, without any weight updates - and each has diminishing returns, failure modes, and a point past which more isn't better.

## The idea
Lesson 01 established that a model produces its next token by conditioning on everything in its input. That single mechanical fact is the foundation for **in-context learning**: if you place a pattern in the input - "here is an example of the task done correctly, twice" - the model's next-token predictions shift toward continuing that pattern, without any retraining. This is different from how a junior engineer might assume prompting works ("politely ask the model to be smart"); it's closer to programming by demonstration than to persuasion.

Few-shot, role, and formatting are the three highest-leverage, lowest-cost levers built on this mechanism, because they require no infrastructure beyond writing a better prompt string. Choosing between them - and knowing when each one stops paying off - is the first real skill in prompt engineering, above and beyond "write clear instructions" (which lesson 02's role structure already covers).

## How it works

### Few-shot prompting: teaching by example, not by description
A **zero-shot** prompt describes the task in words only ("classify this review as positive or negative"). A **few-shot** prompt instead (or additionally) shows the model a handful of worked input/output pairs and lets it infer the task's shape from the pattern:

```
Classify the sentiment of each review as positive or negative.

Review: "The battery life is incredible, lasts two full days."
Sentiment: positive

Review: "Arrived broken and support never responded."
Sentiment: negative

Review: "Decent screen but the software update bricked my settings."
Sentiment:
```

The model completes "Sentiment:" by pattern-matching against the two demonstrations, not by reasoning from a definition of "sentiment" - this is precisely why few-shot prompting is powerful for tasks that are easier to demonstrate than to specify precisely (exact output format, tone, edge-case handling, a house style) and comparatively weak for tasks that require genuine multi-step reasoning the examples don't actually exercise.

**How many examples, and why more isn't strictly better.** Research surveyed in *The Prompt Report* (Schulhoff et al., 2024/2025) and corroborated by later practitioner benchmarking finds that the biggest jump comes from going 0 -> 1 -> a handful of examples, with returns flattening out after roughly 3-5 examples for many tasks - past that point, additional examples mostly cost tokens rather than buying accuracy, though newer "many-shot" work shows that once context windows are large enough to fit hundreds or thousands of examples, performance for some tasks keeps climbing again in that much higher-volume regime. For everyday application prompting, the practical rule of thumb converges around 3-5 well-chosen examples, not "as many as you can fit."

**Example selection matters more than example count.** Examples that closely resemble the actual distribution of inputs the model will see in production teach the pattern more reliably than generic or unusually easy examples. A few-shot classifier trained (via examples) only on clear-cut cases will generalize poorly to the ambiguous cases that make up most of real traffic - the classic mismatch between "examples that were easy to write" and "examples that represent the hard part of the task."

**Worked example - measuring the effect.** Suppose you're building a support-ticket router with three categories (billing, technical, other) and you A/B test three prompt variants on a held-out set of 200 tickets:
- Zero-shot (task description only): 71% routing accuracy.
- Few-shot with 2 examples (one per two of the three categories): 82% accuracy.
- Few-shot with 5 examples (covering all three categories, including one deliberately ambiguous case): 91% accuracy.
- Few-shot with 15 examples (same distribution, just more of them): 92% accuracy.

The jump from 0 to 2 examples (+11 points) and from 2 to 5 (+9 points, largely from finally covering the third category and an ambiguous edge case) dwarfs the jump from 5 to 15 (+1 point). This pattern - large gains from the first few well-chosen, category-covering examples, then a flattening curve - is exactly what the research above describes, and it's the concrete reason "just add more examples" is rarely the right lever once you're past a handful.

### Role prompting: framing, not identity
Role prompting assigns the model a persona or expertise framing ("You are a senior security engineer reviewing this pull request for vulnerabilities") to shift the register, vocabulary, and depth of the response. Mechanically, this works the same way as few-shot: the role text is more input tokens the model conditions on, and roles in its training data are correlated with certain vocabulary, thoroughness, and conventions (a "senior security engineer" persona in training data tends to co-occur with terms like "attack surface," "least privilege," and specific vulnerability classes), so invoking the role nudges generation toward that register.

Role prompting is genuinely useful for calibrating tone, depth, and audience ("explain this to a curious 10-year-old" vs. "explain this to a distributed-systems PhD") and for narrowing which of many plausible response styles the model should pick. It is not a way to grant the model capabilities it doesn't have - telling a model "you are a expert mathematician who never makes arithmetic errors" does not measurably reduce its arithmetic error rate, because the persona shifts style and framing, not the underlying computation the model performs to get an answer. Treating role prompting as a capability upgrade, rather than a framing tool, is a common and costly misunderstanding.

**Worked example.** Compare:

```
Prompt A: "Explain how database indexes work."
Prompt B: "You are a senior backend engineer mentoring a new hire
           who has never worked with databases before. Explain how
           database indexes work, using an analogy they'd recognize
           from everyday life."
```

Prompt A tends to produce a reasonably technical, textbook-style answer. Prompt B - same underlying question - reliably produces a more scaffolded answer with an analogy and checks for the audience's starting knowledge, because the role framing constrains which register of "explain how indexes work" the model continues. Neither answer is more *correct*; the role changed the shape and audience-fit of the response, which is exactly what role prompting is for.

### Output formatting: specifying the shape, not just the content
Left unconstrained, a model will pick a reasonable-looking but unpredictable output shape - sometimes prose, sometimes a bulleted list, sometimes with a preamble ("Sure, here's the answer:") that a downstream parser doesn't expect. Explicit output formatting closes that gap by stating the exact shape required: a specific JSON schema, a fixed set of headers, a word limit, "answer with only the number, no explanation."

This matters most wherever the output feeds a program rather than a human - if code downstream does `json.loads(response)`, an unrequested preamble sentence breaks the pipeline outright. Three practical formatting levers, in increasing order of reliability:
1. **Describe the format in prose** ("respond in JSON with keys `category` and `confidence`") - works often, but is the least reliable, since the model is free to add commentary or drift from the schema on edge cases.
2. **Show a formatted example** (few-shot combined with formatting: demonstrate one complete, correctly-shaped output) - meaningfully more reliable than prose description alone, because the model is now pattern-matching a concrete shape, not inferring one from a description.
3. **Use the vendor's structured-output / constrained-decoding feature**, where the API mechanically restricts which tokens can be generated at each step so the output is guaranteed to match a schema - the most reliable of the three, because it is enforced at the sampling level rather than requested in the prompt. This mechanism, and why it beats even well-formatted free-form prompting, is the entire subject of lesson 05 in this subject; this lesson only needs the general principle that specifying format explicitly (in whatever form) beats leaving it implicit.

**Worked example - the cost of implicit formatting.** A team ships a prompt that ends with "Return the result as JSON." In production, roughly 6% of responses arrive as ```` ```json\n{...}\n``` ```` (wrapped in a markdown code fence) instead of raw JSON, and roughly 2% include a leading sentence like "Here's the JSON you requested:" before the object. Both variants fail a naive `json.loads()` call. The fix - showing one complete example response with no fence and no preamble, plus an explicit instruction "output only the JSON object, no markdown fence, no explanation" - drops the failure rate to under 0.5% in this team's testing, without changing the underlying task at all. This is a formatting reliability problem, not a task-comprehension problem, and it's fixed by tightening the specification of the shape, not by re-explaining the task.

### Combining the three
These techniques compose. A production prompt commonly uses all three at once: a role framing in the system message ("You are a triage assistant for a SaaS billing team"), few-shot examples demonstrating both the task and the exact output shape, and an explicit formatting instruction as a final safety net. Each addresses a different axis of ambiguity - role addresses *tone/depth*, few-shot addresses *task pattern*, formatting addresses *output shape* - and stacking them is normal, not redundant.

## Pros
- All three techniques require no infrastructure beyond a better prompt string - no fine-tuning, no new tooling, fast to iterate.
- Few-shot examples are often more precise than prose descriptions for tasks that are easier to show than to define (style, edge-case handling, exact category boundaries).
- Explicit formatting dramatically reduces downstream parsing failures at near-zero cost.

## Cons
- Few-shot examples cost tokens on every single call (they must be resent every time, per lesson 01) - at scale, this is a real, ongoing cost and latency tax, not a one-time investment.
- Role prompting is easy to over-trust as a capability lever rather than a framing lever, leading teams to "prompt away" accuracy problems that actually need a different fix (better examples, a different model, tool use).
- Prose-only formatting instructions remain probabilistic - even a well-written formatting instruction has a nonzero failure rate under real-world input variance, which is exactly why constrained decoding (lesson 05) exists as a stronger mechanism.
- Badly chosen or biased few-shot examples can leak an unintended pattern into the output (e.g., if all your positive-sentiment examples happen to be long and all your negative ones short, the model can start using length as a shortcut cue instead of actual sentiment).

## Alternatives
- **Fine-tuning on labeled examples** — moves the "teaching by example" outside the prompt entirely, into the model weights. Preferable when you have thousands of examples, need the behavior to be extremely robust, and can absorb training cost/complexity; few-shot prompting is preferable for smaller example sets, faster iteration, and when the task or format may still change.
- **Constrained decoding / structured output APIs** (lesson 05) — a strictly stronger alternative to prose-based output formatting when the vendor supports it, because it's enforced at the token-sampling level rather than requested. Preferable whenever available and the schema is expressible in the vendor's constraint format; prose formatting remains a fallback for vendors or output shapes that don't support constraints.
- **Retrieval-augmented example selection** — instead of a fixed set of few-shot examples, dynamically retrieve the most relevant examples per input from a larger example bank. Preferable at scale, when the input distribution is broad enough that no fixed 3-5 examples cover it well; adds retrieval infrastructure that a fixed few-shot prompt doesn't need.

## When to use it
Reach for few-shot examples when the task is easier to demonstrate than to specify in words, or when you've observed the model getting the *shape* of the task wrong even though it understands the *description*. Reach for role prompting when you need to calibrate tone, audience, or depth rather than change what's being asked. Reach for explicit output formatting any time the output feeds another program, or when consistency of shape matters as much as content.

## When NOT to use it
Don't reach for more few-shot examples to fix a task the model is failing at conceptually (e.g., multi-step arithmetic, obscure factual recall) - examples teach pattern-matching, not missing capability, and piling on examples for a capability gap wastes tokens without fixing the underlying problem (see lesson 06 on the limits of prompting). Don't use role prompting as a substitute for giving the model the actual information or tools it needs to be accurate - a "senior expert" persona does not compensate for missing context. Don't rely on prose-only formatting when a constrained-decoding option exists and the stakes of a malformed response are high (an automated pipeline, not a human reading the output).

## Key takeaways / mental model
All three techniques are instances of the same lever from lesson 01: **shaping the token sequence the model conditions on**. Few-shot shapes the *pattern* (what the task looks like when done right), role shapes the *register* (whose voice and depth level to continue in), and formatting shapes the *output structure* (what shape the completion should take). None of them add capability the model doesn't have; all three reduce ambiguity about what a "correct-looking continuation" is. When a prompt underperforms, diagnose which of these three axes is actually ambiguous before reaching for more of any one of them.

## Self-check questions
1. Your few-shot sentiment classifier performs well on clear-cut reviews but poorly on sarcastic or mixed ones. Using the "examples teach pattern, not capability" framing, explain why adding 10 more clear-cut examples probably won't fix this, and what would.
2. A colleague adds "You are a world-class Python expert who never writes bugs" to a code-generation prompt and reports no measurable change in bug rate. Explain why, mechanically, this is the expected outcome rather than a surprising one.
3. Design a few-shot prompt (sketch the structure, not full text) for extracting structured line items from a receipt, and justify how many examples you'd include and why, referencing the diminishing-returns pattern from this lesson.
4. Your JSON-output prompt fails to parse about 5% of the time in production due to markdown code fences and preambles. Rank the three formatting levers from this lesson by expected reliability improvement, and explain why the ranking holds.
5. You're deciding between adding 3 more few-shot examples versus switching to a constrained-decoding structured-output API for a schema-validation-critical pipeline. What factors would push you toward each option?

## References
- Schulhoff et al., "The Prompt Report: A Systematic Survey of Prompting Techniques" (arXiv:2406.06608, 2024, rev. 2025), https://arxiv.org/abs/2406.06608
- Anthropic Claude Docs, "Be clear, direct, and detailed" (2026), https://console.anthropic.com/docs/en/build-with-claude/prompt-engineering/be-clear-and-direct
- Anthropic, "Prompt engineering best practices for 2026" (2026), https://claude.com/blog/best-practices-for-prompt-engineering
- PromptHub, "The Few Shot Prompting Guide" (2025), https://www.prompthub.us/blog/the-few-shot-prompting-guide
