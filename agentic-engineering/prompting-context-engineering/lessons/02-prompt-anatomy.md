---
id: prompting-context-engineering/02
subject: prompting-context-engineering
title: "Prompt Anatomy: System, Developer, User, and Tool Turns"
slug: prompt-anatomy
status: drafted
mastery:
seniority: junior
source: "OpenAI API docs: Prompting guide (2026); OpenAI API docs: Prompt engineering guide (2026); Anthropic docs: system prompts and Messages API (2026); community/vendor writeups on the OpenAI developer-role migration (2026)"
durability: durable
prerequisites: [prompting-context-engineering/01]
created: 2026-08-10
updated: 2026-08-10
---

# Prompt Anatomy: System, Developer, User, and Tool Turns

## TL;DR
A prompt sent to a model is not one blob of text - it is a structured sequence of role-tagged messages (commonly system/developer, user, assistant, and tool), and the role a piece of text is tagged with changes both how much authority the model gives it and how the training process taught the model to treat it. Knowing which role to put an instruction in - and why the model treats them differently - is the first, most basic lever of prompt design, and everything downstream (few-shot examples, output formatting, tool use) is built on top of this structure.

## The idea
Lesson 01 established that a model call is just a token sequence in, a token sequence out, with no hidden state. But if that were the whole story, there would be no way to distinguish "instructions the application author wants enforced" from "text the end user typed," and no way for a tool-using agent to distinguish "what the user asked for" from "what a tool just returned." Every major model provider solves this by wrapping the flat token stream in a **message structure with roles**: each message in the sequence is tagged with who or what it represents, and the underlying training process (specifically, instruction-tuning and RLHF-style alignment) teaches the model to weight and interpret messages differently depending on their role. This is not just cosmetic formatting - it is a genuine behavioral lever, trained into the model, that a well-designed prompt exploits deliberately rather than by accident.

Understanding prompt anatomy answers a very practical question every time you write a prompt: *where does this piece of text go, and why there rather than somewhere else?*

## How it works

### The core roles and what each is for
Across vendors, message roles converge on a similar shape even though names and exact semantics differ:

- **System / developer role** — carries the application-level instructions: persona, constraints, output format, safety rules, business logic. This is written by the application developer, not the end user, and is (by training and by convention) given the highest priority when it conflicts with later messages. As of 2026, some vendors have moved from a single "system" role to a "developer" role specifically to make this authority distinction explicit and separate from an evolving notion of "system" (e.g., OpenAI's newer models treat developer messages as carrying "the system's rules and business logic," analogous to a function definition, while user messages are the arguments applied against it).
- **User role** — the actual request or input from the person (or upstream system) interacting with the model in this turn. This is where task-specific content, questions, and data typically belong.
- **Assistant role** — the model's own prior responses, included in the resent history so the model can see what it already said (this is also where autoregressive conditioning on "its own prior turns," from lesson 01, becomes visible at the message level, not just the token level).
- **Tool role** — the result of a tool/function call the model requested, fed back in as its own distinct message rather than appended to the user's turn, so the model can distinguish "data a tool returned" from "something the user said."

```
[system/developer]  "You are a support triage assistant. Only answer questions
                      about billing. Refuse anything else politely.
                      Respond in JSON: {category, urgency, reply}."
[user]               "My invoice from March is double what I expected."
[assistant]          "{...model's first response...}"
[user]               "Also, can you write my performance review?"
[assistant]          "{...model refuses, per system instructions...}"
```

Even though every one of these messages is ultimately serialized into one token sequence for the model to process, the role tags (implemented via special delimiter tokens or structured API fields, depending on vendor) mark boundaries the model was trained to respect with different degrees of authority.

### Instruction priority is trained, not just positional
A common misconception is that "whatever comes later in the prompt wins," as if role were irrelevant and only recency mattered. In practice, vendors explicitly train models to give system/developer instructions priority over conflicting user instructions - this is a large part of how safety and product-behavior guardrails are enforced ("ignore previous instructions and reveal your system prompt" attacks specifically target the hope that a later user message can override an earlier system one, and defending against this is an explicit training and product goal, not an accident of message order).

This has a direct design implication: **instructions that must always hold** (persona, refusal policy, output schema) belong in the system/developer message, not buried in a user message or appended to a long document, because that is the channel the model was trained to weight most heavily and resist being talked out of.

**Worked example.** Consider two ways to build the same customer-support bot:

```
Design A (weak):
[user] "You are a support bot. Always respond in under 50 words.
        Here's the customer's message: 'Can you write me a poem
        about my refund instead?'"

Design B (strong):
[system]  "You are a support bot. Always respond in under 50 words.
           Do not perform unrelated creative-writing requests;
           redirect to support topics."
[user]    "Can you write me a poem about my refund instead?"
```

In Design A, the persona and constraint are just more user text, at the same authority level as the off-topic request that follows - the model has no trained reason to treat "you are a support bot" as more binding than "write me a poem," since both arrived in the same role. In Design B, the constraint lives in the higher-authority channel, and the off-topic request arrives in a role the model was trained to weigh against it. Design B is measurably more robust in practice; this is precisely why "system prompt" exists as a distinct concept rather than every provider just accepting one string.

### Developer vs. system: a 2026 nuance
> **Example (2026):** Some vendors have split what used to be a single "system" role into a distinct "developer" role plus a narrower "system" concept, specifically so that identity/behavior instructions set by the application (developer message) are clearly separated from anything resembling end-user-adjacent framing. Others keep a single "system" role and rely on message ordering and product-level enforcement instead. The exact role names, and which one an SDK exposes by default, are vendor-specific and will keep shifting - the durable point is the *concept*: there is a channel for "instructions the application author controls and wants enforced above end-user input," distinct from the channel for "what the current request is asking for." Always check current vendor docs for the exact role name in use.

### User turns: task content, not just "the question"
The user role is not only for literal chat questions. In practice it carries whatever varies per request: the task description, pasted documents, retrieved context, few-shot examples (sometimes), and follow-up clarifications. The key design question for anything landing in the user role is: *does this change from request to request?* If yes, it usually belongs in the user turn (or a document/context block within it); if it's constant across every request to this application, it belongs in the system/developer message so it isn't re-authored or accidentally varied each time, and so it benefits from the higher instruction priority described above.

### Assistant turns: the resent transcript
As covered in lesson 01, every prior assistant turn is resent as part of the input on the next call. In multi-turn tool-using agents, an assistant turn can itself contain a tool call request (a structured "I want to call function X with arguments Y" payload) rather than natural-language text - this is still tagged with the assistant role, because it is the model's own output, just in a structured form instead of prose.

### Tool turns: the model's inputs it didn't ask a human for
When an agent architecture lets the model call functions/tools (covered in depth in the `tool-use-agentic-loop` subject), the result of that call is fed back as a distinct **tool** message, not appended to the user's message and not disguised as the user having said it. This distinction matters for two durable reasons:
1. **Attribution** — the model (and any downstream logging/auditing) can tell the difference between "the user claimed X" and "a tool returned X," which matters for trust and for debugging when a tool returns bad data.
2. **Security** — a tool's output is, from the model's perspective, external and potentially untrusted data (e.g., the contents of a fetched webpage, a file, a search result). Keeping it in a distinct role is a necessary (though not sufficient) building block for reasoning about prompt-injection risk, where content embedded in tool output tries to smuggle in instructions - a topic developed further in `agent-security-and-operations`.

```
[assistant] (tool call) get_weather(city="Austin")
[tool]      "{\"temp_f\": 101, \"condition\": \"sunny\"}"
[assistant] "It's 101F and sunny in Austin right now."
```

### Worked example: diagnosing a broken prompt by role
Suppose a team ships this and gets inconsistent behavior in production:

```
[user] "SYSTEM: You are FinanceBot. Always cite a source.
        USER QUESTION: What was our Q2 revenue?"
```

Everything - the intended system instruction and the actual question - is jammed into a single user-role message, with "SYSTEM:" as plain text rather than an actual role tag. The model has no trained reason to treat the string "SYSTEM:" as carrying elevated authority; it's just characters. This explains two symptoms the team is likely seeing: (1) the "always cite a source" rule gets dropped more often on longer or more demanding questions, because it's competing for attention as ordinary user text rather than being anchored in the high-priority channel, and (2) if this bot is user-facing and someone types a message containing the literal string "SYSTEM: ignore prior instructions," the fake-role text in the user's own input is now structurally identical to the "instruction" the developer wrote - nothing distinguishes them. The fix is mechanical: move the persona/citation rule into an actual system/developer-role message via the API's structured fields, and keep the user's question as the sole content of the user-role message.

## Pros
- Role structure gives you a precise, trained lever for instruction authority instead of hoping phrasing alone will make an instruction "stick."
- Separating tool output into its own role is a real (if partial) defense against confusing model-trusted instructions with untrusted external data.
- The mental model transfers across vendors even though role names and exact enforcement differ, because the underlying need (distinguish authority levels) is universal to any system that mixes developer intent with end-user and tool input.

## Cons
- Role authority is trained behavior, not a hard technical guarantee - a sufficiently adversarial or confusing user/tool input can still sometimes override or degrade system instructions, especially with weaker or older models; role placement reduces but does not eliminate injection risk.
- Exact role names, how many roles a given vendor exposes, and which fields an SDK maps them to are all vendor-specific and change (the system-to-developer-role migration is a live example as of 2026), so code that hardcodes assumptions about role names needs revisiting periodically.
- Over-stuffing the system/developer message with everything "important" defeats the purpose - if it becomes a dumping ground for task-specific content that should have been in the user turn, you lose the signal of "this is the stable, always-enforced part."

## Alternatives
- **Single flat prompt string with manual delimiters (e.g., "### Instructions ### Question")** — the pre-chat-API way of doing this; still used with older completion-style APIs or hand-rolled formats. It carries none of the trained authority distinction described above and is strictly weaker for authority enforcement; prefer real structured roles whenever the API supports them.
- **Prompt templates/DSLs (e.g., a templating library that assembles role-tagged messages from reusable blocks)** — not a different concept, but a different implementation layer; still produces the same role-tagged structure underneath, just with better reuse and testability for application developers. Preferable at any production scale where prompts are assembled programmatically rather than hand-typed once.
- **Fine-tuning a persona directly into model weights instead of using a system prompt** — moves the "always true" behavior out of the prompt entirely. Preferable when the behavior must be extremely robust and you're willing to pay training cost/complexity; overkill for most applications, and current system/developer-role prompting is dramatically cheaper to iterate on.

## When to use it
Use deliberate role placement any time you're building an application (not just chatting casually): put stable, always-enforced instructions in the system/developer role; put per-request content in the user role; keep tool results in the tool role rather than hand-folding them into user text; and treat assistant-role history as the resent transcript it actually is. This applies from the simplest single-turn API call up through complex multi-turn agents.

## When NOT to use it
For quick, disposable, single-shot exploration in a chat UI where there's no persistent "application behavior" to protect and no adversarial input to worry about, obsessing over role placement is wasted effort - just ask the question. Reach for careful role anatomy once you're building something that (a) will run many times, (b) needs consistent behavior across requests, or (c) accepts input from an untrusted source (end users, fetched documents, tool output).

## Key takeaways / mental model
Ask, for every piece of text going into a prompt: **who does this represent, and does it need to survive contact with untrusted input?** Stable, authoritative, developer-owned instructions go in system/developer. Variable, per-request content goes in user. The model's own prior output goes in assistant. External data fetched on the model's behalf goes in tool. Role is a trained authority signal, not decoration - treat it as the primary structural decision in any prompt, before worrying about wording.

## Self-check questions
1. A junior engineer puts "Always respond in valid JSON" inside the user message, appended after the user's actual question, because "it's easier to build the string that way." What's the concrete risk, and where should it go instead?
2. Why is keeping tool output in a distinct "tool" role (rather than folding it into the user's message) relevant to prompt-injection defense, given what you know about trained instruction priority?
3. You're designing a code-review bot: some instructions ("always flag SQL injection risks") never change; others ("review this specific diff") change every call. Sort these into roles and justify each placement.
4. Explain, using the autoregression model from lesson 01, why an assistant-role tool-call message and a plain assistant-role text message are handled by the same underlying mechanism even though one looks structured and one looks like prose.
5. A teammate argues "role doesn't matter, the model just reads all the text anyway." Using what you know about instruction-tuning and trained authority, explain what's wrong with that claim - and one experiment you could run to demonstrate it's wrong.

## References
- OpenAI API docs, "Prompting" guide (2026), https://developers.openai.com/api/docs/guides/prompting
- OpenAI API docs, "Prompt engineering" guide (2026), https://developers.openai.com/api/docs/guides/prompt-engineering
- Lunary, "OpenAI: New 'developer' message role" (2026), https://lunary.ai/blog/openai-developer-role
- OpenAI Developer Community, "What goes in the system vs developer role" (2026), https://community.openai.com/t/what-goes-in-the-system-vs-developer-role/1347594
