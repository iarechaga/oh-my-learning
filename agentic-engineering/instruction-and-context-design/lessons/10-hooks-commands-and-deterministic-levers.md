---
id: instruction-and-context-design/10
subject: instruction-and-context-design
title: "Hooks, Slash Commands, and Other Deterministic Levers vs Model-Judged Triggers"
slug: hooks-commands-and-deterministic-levers
status: drafted
mastery:
seniority: senior
source: "Claude Code Docs: Automate actions with hooks (2026); Claude Code Docs: Hooks reference (2026); Anthropic Platform Docs: Agent Skills overview (2026); genaiunplugged: Claude Code Skills, Commands, Hooks & Agents Guide (2026); Totalum blog: Claude Code Skills in 2026 - vs Hooks, vs Subagents, vs MCP (2026)"
durability: durable
prerequisites: [instruction-and-context-design/04]
created: 2026-08-10
updated: 2026-08-10
---

# Hooks, Slash Commands, and Other Deterministic Levers vs Model-Judged Triggers

## TL;DR
Every mechanism that gets an agent to do something on cue falls into one of two categories: it fires because the model *decided* the situation called for it (a trigger description it reasoned about), or it fires because *code outside the model* detected an event and ran regardless of what the model would have chosen (a hook on a lifecycle event, a command invoked by explicit human keystroke). The first category is flexible and improves as the model improves; the second is boring, predictable, and never skipped - and the choice between them is really a choice about what "must never fail to happen" versus "should happen when it makes sense" in your system.

## The idea
Lesson 04 established that a skill's trigger is a description the model reasons about: given the current request, does this match? That's a genuinely powerful mechanism - it scales to situations nobody explicitly programmed for, because the model is doing real inference over the request's meaning, not matching a fixed pattern. But it inherits the model's probabilistic nature. A well-written trigger description fires reliably in the vast majority of matching cases and stays silent in the vast majority of non-matching cases - "vast majority" is the ceiling, not "always," because the underlying decision is inference, not lookup (lesson 05 covers exactly how that reliability breaks down).

Some things cannot tolerate "vast majority." A rule that must hold with zero exceptions - block every commit containing a secret, format every file the same way, log every tool call for audit - cannot be implemented as "ask the model to remember to do this," because a probabilistic system asked to enforce a hard guarantee will, eventually, forget, get distracted by a more locally-salient part of the request, or reason its way to a plausible-sounding exception. This is the same probabilistic-vs-deterministic tension that shows up whenever a hard business rule gets phrased as a prompt instruction instead of enforced in code - the model can be told the rule, but telling is not enforcing.

The practical answer isn't "always prefer deterministic mechanisms" - a system built entirely from hard-coded triggers loses everything that makes an agent worth having over a script: judgment over the request's actual meaning, handling of cases nobody anticipated, and doing the right thing in situations too varied to enumerate as explicit conditions. The skill is knowing which lever the requirement actually calls for, and building systems that mix both deliberately rather than defaulting to whichever one you reached for first.

## How it works

### Two lifecycle triggers, one shared property
Two mechanisms - a lifecycle hook and an explicit command - sit on the deterministic side, and they share the property that matters most: neither one asks the model whether to run. They differ in *who* or *what* initiates them:

- **A lifecycle hook** fires when code outside the model detects a defined event has occurred - a tool is about to run, a tool just finished, a session is starting, a response is about to be returned. The event detection is mechanical (did this specific thing happen, yes or no), and the hook runs every time that event fires, with no judgment call in between. The model doesn't decide whether the hook runs; the harness does, based on what actually happened.
- **An explicit command** (a slash command, or equivalent named-invocation mechanism) fires when a human deliberately types it. There's no ambiguity to resolve and no inference to perform - the human already decided what they want; the command is a shortcut that inserts a known block of instructions or runs a known procedure, rather than the model interpreting a natural-language request and guessing whether this is the moment for it.

Both are deterministic in the sense that matters here: given the triggering condition (the event fired; the human typed the command), the action happens, full stop - no reasoning step where the model might decide the situation doesn't quite warrant it. Compare this to a skill's trigger description, which is model-judged: even a well-written description is a routing rule the model *evaluates*, not a switch that *closes*.

### Worked example: the same requirement implemented three ways
Take a concrete requirement - "every time a file is edited, run the project's formatter on it" - and walk it through all three mechanisms to see what changes:

- **As an instruction in always-loaded guidance:** "Remember to run the formatter after editing files." This relies on the model recalling the instruction, at the right moment, on every single edit, across a long session where a hundred other things are also competing for attention. It will work often. It will also, eventually, get skipped - not because the model is broken, but because remembering an unenforced side-instruction on every relevant occasion, indefinitely, is not what probabilistic instruction-following guarantees.
- **As a skill triggered by description:** "Use when the user asks to format or clean up code." This only fires when the *request itself* sounds like a formatting task - it does nothing for the much more common case where formatting should follow silently after an unrelated edit the user asked for. Wrong tool for this requirement: the trigger condition here isn't "did the user ask for formatting," it's "did a file just get edited," and that's not naturally phrased as a request-matching description at all.
- **As a lifecycle hook on the file-edit event:** the hook is configured to run after every edit event, unconditionally, executing the formatter as a subprocess. It fires the same way whether the model "remembered" or not, because remembering was never part of the mechanism - the harness detected the event and ran the code. This is the only one of the three that actually satisfies "every time," because it doesn't route through the model's judgment at all.

The lesson generalizes: if a requirement's success criterion is "this must happen on every occurrence of a mechanical event, regardless of what else is going on in the conversation," a hook is very likely the right primitive, and phrasing it as an instruction (loaded or not) is solving a determinism problem with a probabilistic tool.

> **Example (Aug 2026):** one 2026 coding-agent CLI implements hooks as user-defined shell commands the harness runs at defined lifecycle points - before a tool executes, after a tool executes, at session start, before the agent returns a response, among others - explicitly to get "deterministic control: certain actions always happen rather than relying on the LLM to choose to run them." The same product also supports a variant where the hook's job is itself a judgment call too fine-grained for a fixed shell script (e.g., "is this specific bash command dangerous enough to block") - in that case the hook still fires deterministically on the event, but hands the judgment portion to a small model call as its evaluation step, keeping the *firing* deterministic while letting the *decision inside* stay model-judged. Treat the exact event names and configuration format as this one product's current implementation, not a universal standard - verify specifics against current docs for whichever harness you're using.

### Worked example: why a command isn't just "a skill you have to ask for"
It's tempting to think of an explicit command as simply a skill with worse ergonomics - the human has to remember to type it instead of the model figuring it out. That framing misses what the human-initiated trigger actually buys: certainty about *when*, at the cost of the human doing the routing instead of the model. This trade is correct whenever the action is high-stakes enough that you don't want the model's judgment call about *whether now is the moment* in the loop at all - a command to cut a release, a command to run a destructive cleanup script, a command to submit a final report. For all of these, "the model decided this was probably the right moment" is a worse property than "a human explicitly said so," independent of how good the model's judgment usually is. Conversely, forcing every recurring, low-stakes, pattern-matchable task into a command that a human must remember to type reintroduces exactly the repetition-avoidance problem skills exist to solve (lesson 07) - if the situation reliably signals itself in the request's own wording, model-judged triggering is less friction and no less safe.

### A simple decision heuristic
Ask, in order: (1) Does this need to happen on every occurrence of a detectable event, with zero tolerance for a missed occurrence? If yes, a hook. (2) Does this need to happen only when a human explicitly decides now is the moment, with no ambiguity about intent? If yes, a command. (3) Otherwise - the situation is recognizable from the request's own content, tolerates the model reasoning about whether it applies, and benefits from not requiring the human to remember an exact invocation - a model-judged trigger (a skill's description, or an always-loaded instruction if it's small and universal enough per lesson 03). This ordering matters: check for a hard determinism requirement *before* reaching for a model-judged mechanism, because retrofitting determinism onto something that started as "please remember to..." is a common and avoidable rework cycle.

## Pros
- **Hooks and commands provide guarantees a model-judged trigger structurally cannot** - "this always runs on this event" and "this only runs when explicitly asked" are properties enforced by code, not by asking the model to behave consistently.
- **Auditability.** A hook's firing is a discrete, loggable event tied to a mechanical condition; a command's firing is tied to an explicit human action. Both are far easier to reason about after the fact than "the model decided to load this skill" - useful for compliance, debugging, and building trust in what the system actually did.
- **Offloads a decision the model doesn't need to make.** Every requirement correctly moved to a hook or command is one less thing competing for the model's limited, imperfect attention across a long session - narrowing what the model has to judge correctly improves reliability of everything it still has to judge.

## Cons
- **Rigidity is the mirror image of the guarantee.** A hook fires on its exact configured event whether or not that's actually the right moment in this specific case, and a command requires the human to remember to invoke it - neither one adapts to nuance the way a model-judged trigger can, so forcing genuinely context-dependent behavior into a hook produces a rule that's technically always-on but frequently wrong for the situation.
- **Commands push the routing burden onto the human**, which is friction and a real cost for anything recurring enough that the human would rather not have to remember an exact name or flag - this is precisely the case model-judged triggering was built to remove.
- **Hooks are extra surface to secure and maintain.** Code that runs automatically and unconditionally on an event is also code that runs automatically and unconditionally if misconfigured or compromised - a bad hook has no model-level judgment step to catch an obviously wrong situation before acting.
- **Proliferating commands or hooks without a clear inventory recreates the discoverability problem instructions were trying to solve** - a human who doesn't remember a command exists gets no benefit from it, and a hook nobody remembers configuring becomes mystery behavior when someone later asks "why did this just happen."

## Alternatives
- **Always-loaded instruction, unenforced** - the cheapest option and adequate for a rule where an occasional miss is a minor, recoverable inconvenience rather than a real failure; wrong for anything where a miss is a real problem (see the formatter example and the compliance framing above).
- **Model-judged skill trigger** - the right choice when the triggering condition is naturally expressed in the content of a request and the cost of an occasional missed or extra invocation is low; covered fully in lessons 04, 07, and 08.
- **Fully external automation with no agent involvement at all** (a cron job, a CI pipeline step, a pre-commit git hook running outside any agent session) - preferable when the task needs zero judgment whatsoever and an agent's presence in the loop adds cost or latency without adding value; the agent-level hook is the right choice specifically when the deterministic action needs to be interleaved with, or informed by, what the agent is doing in that same session.

## When to use it
Reach for a hook when a requirement's correctness depends on it firing on literally every occurrence of a mechanical, detectable event, and reach for a command when a requirement's correctness depends on a human's explicit, unambiguous decision that now is the moment - especially for anything destructive, hard to undo, or costly to trigger by mistake. Use both together with model-judged triggers rather than picking one mechanism for an entire system: a well-designed agent setup typically has a small number of hard-guaranteed hooks, a small number of explicit commands for high-stakes human-gated actions, and a larger number of model-judged skills and instructions for everything else.

## When NOT to use it
Don't reach for a hook to implement behavior that genuinely needs situational judgment - a hook has no way to say "usually, but not in this specific case," and forcing that nuance into a fixed condition produces a rule that fires confidently in the wrong situations. Don't reach for a command for anything recurring and easily recognizable from the request's own wording - requiring a human to remember an exact command name for something the model could reliably infer from context reintroduces friction the model-judged mechanisms exist to remove, and if nobody remembers the command exists, it provides zero benefit.

## Key takeaways / mental model
Sort every "make this happen automatically" requirement by asking who or what is allowed to decide it should fire: if the answer must be "code, unconditionally, on this exact event" - a hook. If the answer must be "a human, explicitly, right now" - a command. If the answer can be "the model, reasoning about whether this situation matches" - a model-judged trigger, and that's most of the time, because most requirements benefit from judgment more than they need an ironclad guarantee. The recurring failure to watch for is phrasing a hard-guarantee requirement as an instruction and hoping the model remembers - that's asking a probabilistic system to deliver a deterministic property it structurally cannot promise.

## Self-check questions
1. A team wants every agent-generated commit message to include a specific compliance footer, with zero exceptions ever. A junior engineer proposes adding this as a line in the always-loaded system instructions. Using this lesson's framing, explain why that's the wrong mechanism and what you'd build instead.
2. Contrast a skill's trigger description with a lifecycle hook's triggering condition: both "fire" on some signal, but what's structurally different about how each one decides to fire, and why does that difference matter for a requirement with zero tolerance for misses?
3. A recurring task ("generate this week's status report") is currently implemented as a command the user has to remember to type every Friday. Argue for and against converting it to a model-judged skill trigger instead, and state what evidence would settle the question.
4. Explain, in your own words, why a hook that runs a judgment call through a small model call internally is still considered "deterministic" at the level that matters for this lesson's framing, even though a model is involved somewhere in the mechanism.
5. Give an example (not from this lesson) of a requirement you'd implement as a hook, one you'd implement as a command, and one you'd leave as a model-judged skill trigger, and justify each choice using the decision heuristic from this lesson.

## References
- [Claude Code Docs: Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide)
- [Anthropic Platform Docs: Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [genaiunplugged: Claude Code Skills, Commands, Hooks & Agents Guide](https://genaiunplugged.substack.com/p/claude-code-skills-commands-hooks-agents)
- [Totalum blog: Claude Code Skills in 2026 - The Complete Guide (vs Hooks, vs Subagents, vs MCP)](https://www.totalum.app/blog/claude-code-skills-totalum)
- `agentic-engineering/instruction-and-context-design/lessons/04-designing-trigger-descriptions.md` (prerequisite: model-judged trigger design)
- `agentic-engineering/instruction-and-context-design/lessons/07-what-a-skill-is.md` (when a recurring need is worth a skill at all)
- `agentic-engineering/prompting-context-engineering/lessons/06-limits-of-prompting.md` (the probabilistic-vs-deterministic enforcement tension referenced throughout)
