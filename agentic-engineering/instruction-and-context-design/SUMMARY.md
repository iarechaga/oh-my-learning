# Instruction & Context Design - Subject Summary

A comprehensive recap of this subject, concept by concept.

**Progress note:** all 11 lessons are `drafted`; none have been discussed yet, so
mastery is pending across the board and no weak spots are recorded. This summary will
gain depth (especially on the concepts you find hard) as discussions happen - the
"Focus areas" section at the bottom will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom
(dependency-ordered).

## Part I - The Shape of the Problem

- **[instruction-and-context-design/01] The scaffolding surface** - an agent's
  behavior is shaped by a set of distinct instruction surfaces (system prompt, project
  config, tool descriptions, skills, hooks), each with its own load timing, cost, and
  reach; the same instruction on the wrong surface either wastes budget every turn or
  silently never gets read. ([lesson](lessons/01-the-scaffolding-surface.md))
- **[instruction-and-context-design/02] Structured metadata as cheap signal** - a
  tiny, structured header lets tooling and the model answer cheap relevance questions
  without paying the cost of the full body - the mechanism that makes deferred loading
  actually work. ([lesson](lessons/02-structured-metadata-as-cheap-signal.md))
- **[instruction-and-context-design/03] Always-loaded vs on-demand** - every piece of
  content is either permanently resident (paid every turn, guaranteed present) or
  deferred (paid only when needed, never guaranteed present); deciding where to draw
  that line is one of the highest-leverage choices in scaffolding design.
  ([lesson](lessons/03-always-loaded-vs-on-demand.md))
- **[instruction-and-context-design/04] Designing trigger descriptions** - the core
  lesson of the subject: deciding whether deferred content is relevant is usually the
  model itself making a judgment call over a short description, not an index lookup -
  writing a description that fires correctly is a distinct, learnable skill.
  ([lesson](lessons/04-designing-trigger-descriptions.md))

## Part II - Where Deferred Loading Breaks, and How to Write for It

- **[instruction-and-context-design/05] Failure modes of deferred loading** - the
  triggering judgment call fails in three distinct ways - over-triggering, under-
  triggering, and ambiguity/collision - each with its own symptom and fix.
  ([lesson](lessons/05-failure-modes-of-deferred-loading.md))
- **[instruction-and-context-design/06] Writing instructions that survive being read
  out of order** - a deferred document may load in any order, alongside unrelated
  material; write every loadable unit as if it might be the only thing currently in
  clear attention, not a chapter that leans on what came before.
  ([lesson](lessons/06-writing-instructions-that-survive-out-of-order-reading.md))

## Part III - Skills, and the Full Set of Primitives

- **[instruction-and-context-design/07] What a skill is** - a self-contained,
  independently-triggerable packet of instructions loaded in full only on match; worth
  building when a need recurs, is expensive to reconstruct, and is describable enough
  to actually be found. ([lesson](lessons/07-what-a-skill-is.md))
- **[instruction-and-context-design/08] Authoring a skill end to end** - four
  sequential decisions - scope, trigger description, body structure, inline-vs-file
  split - and skipping any one produces a skill that never fires, fires too often, or
  fires correctly and then gives bad guidance.
  ([lesson](lessons/08-authoring-a-skill-end-to-end.md))
- **[instruction-and-context-design/09] Evaluating whether a skill actually works** -
  "works" decomposes into three separable questions (correct triggering, correct
  depth, correct resulting behavior), and a skill can pass any two and still fail the
  third silently. ([lesson](lessons/09-evaluating-whether-a-skill-works.md))
- **[instruction-and-context-design/10] Hooks, commands, and deterministic levers** -
  every cue-driven mechanism is either model-judged (a trigger description reasoned
  about) or deterministic (a hook or command that fires regardless of model judgment);
  the choice is really about what must never fail to happen versus what should happen
  when it makes sense.
  ([lesson](lessons/10-hooks-commands-and-deterministic-levers.md))
- **[instruction-and-context-design/11] Choosing the right primitive** - a decision
  framework across instructions, tools, skills, hooks, and commands, deliberately
  incomplete: MCP servers and subagents still have to be weighed in once those
  subjects exist. ([lesson](lessons/11-choosing-the-right-primitive.md))

## Focus areas

None yet - no discussions have been held. After each discussion, the recorded weak
spots and misconceptions will be aggregated here, with extra detail on the concepts
rated `shaky` or `not-yet`.
