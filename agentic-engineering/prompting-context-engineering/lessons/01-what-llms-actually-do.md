---
id: prompting-context-engineering/01
subject: prompting-context-engineering
title: What LLMs Actually Do: Tokens, Context Windows, and Autoregression
slug: what-llms-actually-do
status: drafted
mastery:
seniority: junior
source: "Anthropic support docs: How large is the Anthropic API's context window? (2026); Hugging Face LLM Course: Byte-Pair Encoding tokenization (2026); Sebastian Raschka: Implementing a BPE Tokenizer From Scratch (2025); Morph: Claude Context Window Size 2026 (2026)"
durability: durable
prerequisites: []
created: 2026-08-10
updated: 2026-08-10
---

# What LLMs Actually Do: Tokens, Context Windows, and Autoregression

## TL;DR
A large language model is a function that repeatedly predicts the single most-likely next token given everything before it, one token at a time, until it decides to stop. It has no persistent memory between separate calls, no built-in notion of "the conversation so far" beyond whatever text you re-send it, and a hard limit - the context window - on how many tokens (input plus output combined) it can process in one call. Almost everything else in prompting and context engineering is a consequence of these three facts.

## The idea
It is tempting to think of a chatbot as a program that "remembers" you, "understands" your question, and "decides" to answer. Functionally, none of that is how the underlying mechanism works, and the gap between the mental model and the mechanism is where most beginner mistakes in prompting come from - sending too little context and being surprised the model "forgot" something, sending too much and being surprised it got confused, or assuming a fact stated once will still shape behavior ten pages of conversation later.

The actual mechanism is narrower and more mechanical than the conversational interface suggests: at each step, the model takes a sequence of tokens as input and outputs a probability distribution over "what token comes next." It samples one token from that distribution, appends it to the sequence, and repeats. That is the entire generative act, repeated thousands of times to produce a paragraph. Everything a model "knows" about the current exchange - your system prompt, the conversation history, any documents you pasted in, the model's own prior turns - has to be physically present in that token sequence on every single call, because the model does not retain anything from one call to the next. Understanding this reframes prompting from "communicating with an entity" to "constructing the exact input string that makes the next-token predictions come out the way you want."

## How it works

### Tokens are the model's actual alphabet
A model does not read characters or words. It reads tokens - chunks of text produced by a tokenizer, typically using an algorithm called byte-pair encoding (BPE) or a close variant. BPE builds its vocabulary by starting from individual bytes/characters and iteratively merging the most frequent adjacent pair into a new symbol, repeating until it reaches a target vocabulary size (commonly in the tens of thousands to ~100K+ entries across major model families as of 2026). The result is a fixed vocabulary of subword chunks: common short words often become a single token ("the", "and"), longer or rarer words split into multiple pieces ("tokenization" might become `token` + `ization`), and unfamiliar strings (unusual names, code identifiers, non-English text, base64 blobs) tend to fragment into many small tokens.

This has concrete, practical consequences:
- **Token count != word count or character count.** English prose averages roughly 3/4 of a token per word (so ~100 tokens ≈ 75 words), but this ratio swings a lot: dense code, non-English text, and unusual identifiers can run closer to one token per character in the worst case.
- **Cost and limits are counted in tokens, not characters.** API pricing and context-window limits are both denominated in tokens, so a string that "looks short" in your editor can be token-expensive if it's full of rare subwords.
- **The model can be genuinely bad at character-level tasks.** Because the model operates on token chunks rather than individual letters, tasks like "count the letters in this word" or "reverse this string" are harder for it than you'd expect from something that seems to read text fluently - it isn't seeing individual letters as first-class units.

**Worked example.** Suppose you're deciding whether to paste a 40-page PDF (roughly 20,000 words of English prose) into a prompt versus a 2,000-line JSON config file of similar file size. The prose, at ~0.75 tokens/word, costs about 20,000 / 0.75 ≈ 26,700 tokens. The JSON, with its repeated punctuation, quoted keys, and structured-but-irregular tokens, commonly runs closer to 1.3-1.5 tokens per "word-like" unit - a 2,000-line file with ~15,000 space-separated chunks could easily cost 20,000-22,000 tokens despite being "less text" by eye. Token budgeting has to be done in tokens, and when in doubt you measure with the vendor's actual tokenizer rather than estimating from word count.

### Autoregression: next-token prediction, repeated
"Autoregressive" generation means the model predicts token N+1 conditioned on tokens 1..N (the entire sequence so far, including its own previously generated tokens), then treats the newly extended sequence as the new input for predicting token N+2, and so on.

```
Step 1: [system][user: "What is 2+2?"]                    -> predict token: "The"
Step 2: [system][user: "What is 2+2?"][assistant: "The"]  -> predict token: " answer"
Step 3: [...][assistant: "The answer"]                     -> predict token: " is"
Step 4: [...][assistant: "The answer is"]                  -> predict token: " 4"
Step 5: [...][assistant: "The answer is 4"]                -> predict token: "."
Step 6: [...][assistant: "The answer is 4."]                -> predict: <stop>
```

Each arrow is one full forward pass through the model. Generating a 500-token response means running this prediction step roughly 500 times, each one conditioned on everything before it (including the tokens the model itself just emitted in this response). This is why a model can appear to "commit" to a bad early answer and then justify it - once "The answer is 5" (wrong) has been emitted, the next prediction step is conditioned on that text being true, and there is no backtracking. It is also why streaming output is a natural fit for these systems: tokens really are produced one at a time in sequence, not computed all at once and revealed gradually.

Sampling at each step is not always "pick the single most likely token" - a `temperature` parameter and related settings (top-p / top-k) control how much randomness is injected into the choice, trading determinism for variety. At temperature 0, the model deterministically (or near-deterministically) picks the highest-probability token every time; at higher temperatures, it samples more broadly from the distribution, which is why the same prompt can produce different wording on different runs.

### No memory between calls: the illusion of conversation
An LLM API call is stateless: the model has no persistent storage of "this user," "our last conversation," or "what I said five minutes ago" that survives outside a single request. What creates the feeling of a continuous conversation is that the calling application (a chat UI, an agent harness) resends the entire conversation transcript - system prompt, every prior user and assistant turn, any tool calls and their results - as part of the input on every new call.

```
Call 1 input:  [system] + [user turn 1]
Call 1 output: [assistant turn 1]

Call 2 input:  [system] + [user turn 1] + [assistant turn 1] + [user turn 2]
Call 2 output: [assistant turn 2]

Call 3 input:  [system] + [user turn 1] + [assistant turn 1] + [user turn 2]
               + [assistant turn 2] + [user turn 3]
Call 3 output: [assistant turn 3]
```

Every call re-sends the entire growing history. This has two important corollaries. First, if a fact was never included in the resent transcript - because it fell outside the context window, was summarized away, or was simply never written down - the model has no way to know it, no matter how "obviously" it was established earlier in a human sense of "the conversation." Second, this is why the input token count (and therefore the cost and latency) of a long-running chat or agent session grows with every turn: turn 50 re-sends turns 1-49 in full, unless something in the system actively trims, summarizes, or otherwise manages that growing history (a topic covered later in this subject under context engineering).

**Worked example - the cost of a growing chat.** Suppose each user/assistant turn pair averages 300 tokens, and a system prompt is a fixed 800 tokens. By turn 10, the input to the API call is 800 + (9 prior turn-pairs x 300) = 800 + 2,700 = 3,500 tokens, even though the user only just typed one short new message. By turn 40, it's 800 + (39 x 300) = 12,500 input tokens for that single call. If nothing intervenes, a long enough session eventually re-sends more history than fits in the context window at all - the concrete failure mode that later lessons on context management exist to prevent.

### The context window: a hard, finite ceiling
The context window is the maximum number of tokens a single model call can process, counting the input (system prompt + conversation history + any retrieved documents + tool definitions + tool outputs) and the output (the response being generated) together against one shared ceiling (the exact accounting - whether input and output share one pool or have separate limits - varies by vendor and is a perishable detail, not a durable one; check current docs).

> **Example (mid-2026):** context window sizes vary widely and change often across vendors and model tiers - as of mid-2026, flagship models from several vendors advertise context windows in the 200K-1M token range, with the largest windows generally reserved for a vendor's flagship tier and gated by additional cost or latency at the high end. Treat any specific number as a snapshot, not a durable fact - see `landscape-snapshot` for current figures.

The window being "finite" is not just a soft inconvenience; it is a hard cutoff. If the constructed input exceeds the limit, the call fails outright (or the application silently truncates something, which is worse, because it fails quietly). This is why "just paste the whole codebase in" stops being a viable strategy past a certain project size, and why techniques like retrieval, summarization, and compaction (covered later in this subject) exist at all: they are ways of fitting the input that actually matters inside a budget that does not grow just because your task got bigger.

A second, subtler property: even within the window, a model's ability to use information is not perfectly uniform across the whole context. Very long contexts can suffer from position-dependent effects where information buried in the middle of a long input is used less reliably than information near the start or end (this is explored in depth in later lessons on context failure modes). The practical implication for this lesson is narrower: "fits in the context window" is necessary but not sufficient for "the model will actually use it well."

### Putting it together: why this lesson underlies everything else
Every technique in the rest of this domain is a response to one of these three mechanics:
- Because the model only sees tokens, prompt engineering is partly an exercise in token-efficient communication (concise instructions, well-chosen examples) rather than natural-language politeness.
- Because generation is autoregressive and conditioned on its own prior output, techniques that get the model to "think" through intermediate steps before committing to an answer (chain-of-thought, covered in lesson 04) work by changing what the model is conditioning on when it produces the final answer.
- Because there is no memory between calls and the context window is finite, the entire second half of this subject - context engineering, retrieval, compaction, sub-agent handoff - exists to manage what gets included in that resent, budget-constrained input on every call.

## Pros
- A precise mental model (predict-the-next-token, no hidden memory, finite window) makes model behavior far more predictable and debuggable than treating the system as a black box with intentions.
- Understanding tokenization explains otherwise-mysterious cost and capability quirks (why code costs more per "line" than prose, why the model struggles with letter-counting).
- Once you internalize "everything must be resent," the reasons for expensive-seeming techniques (caching, summarization, retrieval) become self-evident rather than arbitrary.

## Cons
- The mechanism is genuinely counter-intuitive relative to how conversational interfaces present the model, so this mental shift takes deliberate unlearning, especially for anyone who has only used chat UIs.
- Token-level reasoning does not fully explain higher-level behaviors (why a particular phrasing produces better answers, why chain-of-thought helps on some tasks and not others) - those need additional concepts layered on top, covered later in this subject.
- Exact tokenizer behavior, exact context-window sizes, and exact position-dependent recall quality are all vendor- and model-specific and change over time, so the mechanism is durable but the numbers attached to it are not.

## Alternatives
- **Anthropomorphic mental model ("the AI understands and remembers")** — useful shorthand in casual conversation, actively harmful when debugging why a model "forgot" something or produced inconsistent output across a long session; avoid it as an engineering model.
- **Treating the model as a deterministic function/API with fixed outputs** — closer to correct for temperature-0 usage, but still misses the token-vs-word distinction and the finite-window constraint; insufficient on its own for capacity planning.
- **Full mechanistic understanding of transformer internals (attention, embeddings, training)** — more accurate and more complete than this lesson, but not necessary to use prompting and context engineering well; overkill for the practical goal of this subject, useful if you later want to reason about *why* position-dependent recall or emergent behaviors happen.

## When to use it
Use this mental model every time you're deciding what to put in a prompt, debugging why a model gave a surprising answer, estimating cost or latency, or designing any system (chatbot, agent, RAG pipeline) that manages a growing amount of context across multiple calls. It is the correct default lens for any prompting or context-engineering decision.

## When NOT to use it
You don't need to reason at the token/autoregression level for one-off, short, single-turn prompts where cost and context size are obviously nowhere near any limit - in that regime, plain-language intuition about "what a clear instruction looks like" is enough, and burning attention on token-counting is wasted effort. Reach for the deeper mechanism when things get long, expensive, multi-turn, or surprising.

## Key takeaways / mental model
Think of an LLM call as: **(fixed vocabulary of tokens) -> (one deterministic-or-sampled prediction step, repeated) -> (no state kept afterward)**. Every call is a fresh function invocation over whatever token sequence you constructed; "conversation" is an illusion created by the calling application re-sending history; "memory" is just "did you include it in this call's input, and did it fit." If you can't answer "what tokens is the model actually seeing right now, in what order," you don't yet have a debuggable model of what's happening.

## Self-check questions
1. A teammate says "the model should remember that I told it my name is Priya three messages ago." Explain, mechanically, why that might fail, and what would have to be true for it to work.
2. You have a 900,000-character log file and a 200K-token context window. Roughly why might this not fit even though 900,000 characters "sounds smaller" than 200,000 of anything - and what would you need to measure to know for sure?
3. Why does asking a model "how many R's are in 'strawberry'" sometimes trip it up, in terms of what the model actually sees as input?
4. You're building a chat app and notice your per-message API cost keeps climbing turn over turn even though users are typing short messages. Explain why, using the autoregression/no-memory model from this lesson.
5. A model at temperature 0 gives a different answer to the exact same prompt on two different days. List two mechanistic explanations consistent with everything in this lesson (hint: think about what "the same prompt" might not account for, and what vendors change over time).

## References
- Anthropic support docs: "How large is the Anthropic API's context window?" (2026), https://support.anthropic.com/en/articles/8606395-how-large-is-the-anthropic-api-s-context-window
- Hugging Face LLM Course: "Byte-Pair Encoding tokenization" (2026), https://huggingface.co/learn/llm-course/en/chapter6/5
- Sebastian Raschka, "Implementing A Byte Pair Encoding (BPE) Tokenizer From Scratch" (2025), https://sebastianraschka.com/blog/2025/bpe-from-scratch.html
- Morph, "Claude Context Window Size (2026): 1M Tokens on Opus 4.8 & Sonnet 5" (2026), https://www.morphllm.com/claude-context-window
