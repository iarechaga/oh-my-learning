---
id: instruction-and-context-design/09
subject: instruction-and-context-design
title: "Evaluating Whether a Skill Actually Works"
slug: evaluating-whether-a-skill-works
status: drafted
mastery:
seniority: senior
source: "Anthropic Platform Docs: Agent Skills overview (2026); Anthropic engineering blog: Equipping agents for the real world with Agent Skills (2025); Langfuse blog: Evaluating AI Agent Skills (Feb 2026); Confident AI: LLM Agent Evaluation Metrics in 2026 (2026); FutureAGI: Evaluating AI Agent Skills - A Skill-Tree Playbook (2026)"
durability: durable
prerequisites: [instruction-and-context-design/08]
created: 2026-08-10
updated: 2026-08-10
---

# Evaluating Whether a Skill Actually Works

## TL;DR
A skill that reads well is not the same as a skill that works. "Working" decomposes into three separable questions - did it trigger when it should have (and stay silent when it shouldn't), did it load the right depth of material once triggered, and did it actually change the agent's behavior correctly - and each question needs its own evidence, because a skill can pass any two of these and still fail the third silently.

## The idea
Lesson 08 covered how to author a skill: a trigger description, a body, and supporting files, loaded progressively so only what's needed enters context. Authoring produces an artifact you can read and judge as prose - does the description sound right, is the body well-organized, are the examples clear. None of that tells you whether the skill functions correctly when a real agent, in a real session, has to decide whether to reach for it and then follow it.

This gap matters more for skills than for most software artifacts because a skill's two moving parts - "should this fire" and "did the agent act on it correctly" - are both judged by the same probabilistic reasoning process that produces every other agent decision. There's no compiler that rejects a skill whose description is almost-but-not-quite specific enough, and no unit test framework ships by default that checks whether an agent, given a prompt that should trigger the skill, actually triggers it. If you don't build that evidence deliberately, you're deploying a skill on faith - and skills fail in ways that are individually rare per invocation but compound across a fleet of sessions, so "it seemed to work when I tried it twice" is not evidence, it's an anecdote.

Evaluating a skill is a narrower, more mechanical instance of general agent evaluation (covered in the `agent-evaluation` subject): instead of scoring an agent's overall task performance, you're isolating one loadable unit and asking whether *it specifically* is pulling its weight, in the same way a unit test isolates one function rather than scoring the whole program's output.

## How it works

### The three questions, and why they're separable
1. **Did it trigger correctly?** Given a set of prompts that should invoke the skill, does it fire? Given prompts that should *not* invoke it, does it stay silent? This is a description-quality question (lesson 04), and it can be checked without ever looking at what the skill's body says - you're testing the routing decision, not the payload.
2. **Did it load the right depth?** Once triggered, did the agent read the parts of the skill it actually needed - the SKILL.md body, and any referenced supporting files - or did it stop short (skip a file it needed) or over-read (pull in reference material irrelevant to the task, wasting context)? This is specific to skills built with progressive disclosure (lesson 08): a skill with bundled FORMS.md/REFERENCE.md files can trigger correctly and still under-deliver if the agent never opens the file with the actual answer.
3. **Did it produce correct behavior?** Given the skill fired and loaded the right material, did the agent's subsequent actions actually follow the guidance - right tool calls, right sequencing, right output format, right edge-case handling? This is the question closest to traditional task evaluation, and it's the one most existing agent-eval tooling already measures.

These are separable because failures at each layer look identical from the outside ("the task came out wrong") but need completely different fixes. A skill that never triggers needs a better description (question 1's fix). A skill that triggers but the agent doesn't consult its reference file needs a clearer pointer inside the body, or a body that states the requirement more assertively, not a better trigger (question 2's fix). A skill that triggers and loads fully but still produces wrong output needs the *content* rewritten - clearer steps, a corrected example, an explicit warning about a known pitfall (question 3's fix). Debugging at the wrong layer - rewriting a description when the real problem is that step 4 of the body is ambiguous - wastes iteration cycles the same way debugging the wrong harness/scaffolding layer does (`tool-use-agentic-loop/05`).

### Worked example: building a trigger-accuracy test set
Say you've authored a skill for generating a weekly status report from a project's issue tracker. To evaluate question 1 (triggering), build two prompt sets, not one:
- **Positive set** - prompts that should fire the skill: "write this week's status update," "can you summarize what shipped," "I need the weekly report for stakeholders." Run each through the agent and record whether the skill loaded.
- **Negative set** - prompts that sound adjacent but should NOT fire it: "what's the status of ticket #482" (a single-issue lookup, not a report), "summarize this PDF for me" (summarization, but the wrong domain), "write a report on Q3 revenue" (a report, but not this skill's report). Run each and record whether the skill stayed silent.

A skill that fires on 9/10 positive prompts but also fires on 3/10 negative prompts has a description that's too broad - probably a verb like "summarize" or "report" used generically instead of scoped to the specific trigger condition (lesson 04's core lesson: the description is a routing rule, not a summary of what the skill does). One documented real-world case: a team narrowed a skill's description to be more "abstract" for readability, and trigger accuracy dropped immediately - abstraction that reads better to a human author routes worse to the model, because the model is pattern-matching the request against the description's literal wording, not inferring intent the way a human reader would.

### Worked example: catching a silent depth failure
Consider a skill for filling out a multi-field PDF form, structured with a SKILL.md that says "see FORMS.md for the full field reference" and a bundled FORMS.md containing the actual field names and validation rules. In one documented evaluation run, the agent triggered the skill correctly but never opened FORMS.md - instead it *invented* plausible-looking field names and CLI flags that didn't exist, because the SKILL.md body didn't make consulting FORMS.md feel mandatory before acting. The task's final output looked superficially reasonable (a filled form was produced) but every field name was wrong. This is a pure depth failure: triggering worked, behavior-execution mechanics worked, but the agent skipped the layer of progressive disclosure that held the actually-correct information. The fix wasn't a better trigger or a rewritten example - it was making the body state explicitly, before any instructions to act, that FORMS.md must be read first for any field-level operation.

Depth failures are the hardest of the three to catch from output alone, because the output can look fluent and confident while being fabricated from the model's prior knowledge instead of the skill's actual reference material - the same over-trust-in-priors failure that under-triggering produces at the whole-skill level (lesson 05), just occurring one level deeper, inside a single skill's own supporting files.

### Worked example: a wording change that broke 90%+ of runs
A subtler class of behavior failure: content that is technically correct but easy to misread under time pressure. One documented case involved a single word in a skill's supporting reference - a parameter documented as "optional" that was, in the actual system being described, effectively mandatory for the common case. That one word caused failures in more than 90% of test runs, because the agent, reading "optional," reasonably chose to omit the parameter, and the downstream system silently accepted the incomplete request and produced wrong results rather than erroring loudly. This is why evaluating a skill can't stop at "does it read clearly to me" - clarity to a human author and unambiguous instruction-following by a model are different properties, and the gap between them only surfaces under systematic testing, not a single read-through.

### Choosing evaluation methods per question
- **Triggering (question 1):** cheap to automate. Run the positive/negative prompt sets through the actual agent+skill setup and check a binary "did it load" signal (traceable via logs or tool-call inspection) - no need for a judge model, this is closer to a classification metric (precision/recall over the two prompt sets).
- **Depth (question 2):** requires tracing, not just final output - you need to see which files the agent actually opened during the run, not just what it produced. This is exactly the kind of thing that's invisible from the final answer alone and only shows up in the trajectory (the full sequence of tool calls and file reads).
- **Behavior (question 3):** for tasks with a checkable ground truth (a specific field value, a schema-valid output), direct comparison works. For open-ended output (report tone, summary quality), an LLM-as-judge pass is the more common 2026 practice - a second model, given a rubric, scores the output - but a judge model has its own calibration limits, so pair it with periodic manual spot-checks of individual traces rather than trusting the aggregate score blind.

> **Example (Aug 2026):** the Claude Platform docs describe skill loading in three explicit stages - metadata always loaded, SKILL.md body loaded only when triggered, and bundled files loaded only when referenced - which is precisely the boundary this lesson's three questions map onto: triggering evaluates stage 1-to-2, depth evaluates stage 2-to-3, and behavior evaluates what the agent does once it has whatever it loaded. Treat this three-stage architecture as one concrete, inspectable illustration of the general progressive-disclosure pattern from lesson 08 - other harnesses draw the stage boundaries differently, but the "what loaded, when, and did the agent use it" evaluation shape still applies.

## Pros
- **Localizes failures to a fixable layer** instead of a vague "the skill didn't work," turning debugging into a targeted edit (fix the description vs. fix the body vs. fix a supporting file) rather than a guess-and-rewrite cycle.
- **Catches failures that look fine on a single manual try.** Depth failures and subtle wording bugs both produce fluent, plausible-looking output on any individual run; only a test set surfaces the failure rate.
- **Reusable as regression protection.** Once a positive/negative prompt set and a behavior rubric exist, re-running them after any edit to the skill catches regressions before they reach production use, the same way a test suite protects a codebase.

## Cons
- **Building good negative test cases is genuinely hard** - a negative set that's too easy (obviously unrelated prompts) doesn't actually stress-test the description's boundary, and a realistic near-miss set takes real effort to construct and keeps needing new entries as usage patterns emerge.
- **Depth and trajectory evaluation requires tracing infrastructure** that a lot of setups don't have by default - you need visibility into which files an agent actually opened, not just what it said, which is more instrumentation than checking final output alone.
- **LLM-as-judge scoring inherits the judge model's own blind spots and biases**, and can produce a confidently wrong aggregate score that looks like solid evidence until someone manually reads a sample of the underlying traces.
- **Evaluation has an ongoing cost**, not a one-time cost - a skill that scored well when authored can drift out of correctness as the underlying system it describes changes (a CLI flag gets renamed, an API's optional/mandatory fields change), and nothing re-runs the evaluation automatically unless someone wires that up.

## Alternatives
- **No formal evaluation; ship and watch for user complaints** - the cheapest option, and defensible for a low-stakes personal skill used by one person who will notice and fix it fast if it misbehaves. Fails badly the moment a skill is shared across a team or used unattended, because silent under-triggering and depth failures produce no error message for anyone to notice.
- **Single manual smoke test at authoring time** - run the skill once against the prompt you had in mind while writing it, confirm it looks right, ship it. Catches gross breakage (skill doesn't fire at all) but is exactly the practice that misses the two documented failure classes above (an abstraction-driven trigger regression, a single misleading word) because both produced fluent-looking output on the easy case the author already had in mind.
- **Full production agent-evaluation pipeline** (traced datasets, automated experiments, judge-model scoring, dashboards) - the most rigorous option, appropriate when a skill is business-critical or used at volume across many users; disproportionate ceremony for most individual or small-team skills, where a lightweight prompt-set-plus-spot-check is enough signal for the actual stakes involved.

## When to use it
Evaluate a skill formally before sharing it beyond yourself, before relying on it for anything with real consequences (a skill that touches production data, sends communications, or makes decisions with cost), and any time you edit an existing skill's description or body - edits are exactly when regressions get introduced silently. At minimum, build the positive/negative trigger test even for a personal skill; it's the cheapest of the three checks and catches the most common failure mode (lesson 05's under-triggering and over-triggering).

## When NOT to use it
Don't build a full evaluation harness for a skill you're actively iterating on in the same session where you're still discovering what the description and body should even say - premature testing infrastructure on unstable content is wasted effort; get the shape right through a few manual tries first, then evaluate once it's stable enough to be worth protecting from regression. Also skip heavyweight judge-model scoring for skills whose output has a simple, directly checkable ground truth (a specific value, a schema match) - that's solvable with plain assertion-style comparison, and reaching for an LLM judge there adds cost and its own noise without adding accuracy.

## Key takeaways / mental model
Think of a skill as having three independent gates it must pass through, in sequence, on every invocation: did the router (the description) let it through when it should have and keep it out when it shouldn't; did the agent actually open the files it needed once inside; did it act correctly on what it read. A failure at any gate produces the same symptom from outside - the task came out wrong, or a skill "wasn't used" - but each gate's failure needs a different fix, and only deliberate testing (positive/negative trigger sets, trace inspection for depth, output checking or judge scoring for behavior) tells you which gate actually failed. A skill that "seemed to work" on one manual try has been checked at none of these gates rigorously - fluent, confident-looking output is not evidence any of them passed.

## Self-check questions
1. A skill for drafting release notes fires correctly on "write release notes for this version" but also fires on "summarize what changed in this PR," which is a different, unrelated task. Which of the three evaluation questions does this failure belong to, and what's the first thing you'd change?
2. You run a skill twice by hand, it looks correct both times, and you ship it. Three weeks later a teammate reports it silently used stale field names from a reference file that was updated but never re-read correctly. What evaluation practice from this lesson would have caught this before shipping, and why didn't "it worked when I tried it" catch it?
3. Explain why a skill can score perfectly on triggering (question 1) and still produce systematically wrong output, using the FORMS.md worked example as your evidence.
4. A colleague proposes using an LLM-as-judge to score every dimension of a skill's quality (triggering, depth, and behavior) in one pass, to save engineering effort. What's the specific risk in collapsing the three questions into a single judge score, and what would you keep as a separate, non-judge-based check regardless?
5. You're deciding whether to build a full traced-dataset evaluation pipeline for a skill only you use, versus a personal skill your whole team now depends on. Walk through how the answer changes and why, referencing the cost/stakes trade-off from this lesson.

## References
- [Anthropic Platform Docs: Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Anthropic engineering blog: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Langfuse blog: Evaluating AI Agent Skills (Feb 2026)](https://langfuse.com/blog/2026-02-26-evaluate-ai-agent-skills)
- [Confident AI: LLM Agent Evaluation Metrics in 2026](https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide)
- [FutureAGI: Evaluating AI Agent Skills in 2026 - A Skill-Tree Playbook](https://futureagi.com/blog/evaluating-ai-agent-skills-2026)
- `agentic-engineering/instruction-and-context-design/lessons/08-authoring-a-skill-end-to-end.md` (prerequisite)
- `agentic-engineering/instruction-and-context-design/lessons/04-designing-trigger-descriptions.md` and `05-failure-modes-of-deferred-loading.md` (trigger-quality background referenced throughout)
- Cross-links to `agent-evaluation` subject for the general evaluation methodology this lesson specializes to a single skill.
