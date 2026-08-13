---
id: agentic-software-engineering/01
subject: agentic-software-engineering
title: "Where Coding Agents Run: Terminal, IDE, and Cloud Execution Models"
slug: where-coding-agents-run
status: drafted
mastery:
seniority: mid
source: "Practitioner surveys of 2026 agentic coding tooling (niteagent.com, webidroid.com, augmentcode.com - accessed Aug 2026); tool-use-agentic-loop/03 (this repository) for the underlying loop mechanics"
durability: durable
prerequisites: [tool-use-agentic-loop/03]
created: 2026-08-10
updated: 2026-08-10
---

# Where Coding Agents Run: Terminal, IDE, and Cloud Execution Models

## TL;DR
A coding agent is just an agentic loop (`tool-use-agentic-loop/03`) whose tools happen to be "read file," "edit file," "run shell command," and "run tests." What differs between products is *where that loop physically executes and who is watching it run*: inline in an editor next to a human, standalone in a terminal against a real filesystem, or detached on a remote machine working through a queue of tasks. These are three durable execution models with genuinely different trust, feedback-loop, and workflow implications - not just three brands of the same thing.

## The idea
Once you accept that a coding agent is "an agentic loop with file and shell tools" (`tool-use-agentic-loop/03`), an obvious question follows: does that loop need a human staring at every diff as it happens, or can it run unattended for twenty minutes and hand back a finished pull request? The answer determines *where* the loop can usefully live, and that turns out to sort into three recurring shapes, independent of which specific product implements them.

The three models differ along a single underlying axis: **how tightly the loop's iterations are coupled to a human's live attention**. IDE-integrated agents assume the human is watching every edit and can interrupt mid-thought. Terminal-native agents assume the human delegates a task, then checks back periodically - attention is loose but the session is still synchronous and local. Cloud/async agents assume the human is absent for the whole run - the loop has to make every decision itself and simply report back when done, the way a colleague might after being asked to "take a look at this and open a PR." None of these is more "advanced" than the others; each trades autonomy for oversight in a different place, and each fits different tasks.

This matters at the mid-level because choosing where to run an agent is itself an engineering decision with real consequences - not a preference of taste. Running a large, ambiguous refactor in an IDE-integrated agent burns your live attention on hundreds of micro-approvals; running a one-line typo fix through a cloud/async agent adds review latency and PR overhead to a task that took ten seconds to verify by eye. Matching the model to the task is the actual skill this lesson teaches.

## How it works

### Model 1: IDE-integrated (inline, human-paced)
The agent runs as an extension or fork of the editor itself, with access to the open buffer, cursor position, and surrounding project context, and it typically proposes each edit (or small batch of edits) for the human to accept, reject, or modify before the next step proceeds.

- **Feedback loop:** tightest possible - the human sees the diff the instant it's proposed, often line by line, and can redirect before the agent commits to a direction.
- **Context available to the agent:** whatever the editor exposes - open files, sometimes the whole workspace index, cursor location, recent edits - but rarely a full independent shell environment.
- **Typical unit of work:** a function, a small refactor, an autocomplete-scale suggestion, a single file's changes.

> **Example (Aug 2026):** several IDE-integrated products ship as full editor forks (open a modified VS Code build) while others ship as extensions inside an existing editor; the split between "fork the IDE" and "extend the IDE" is itself a shifting implementation detail, not the durable part of this model.

### Model 2: Terminal-native (local, session-paced)
The agent runs as a CLI process against the actual repository on disk, with real shell access - it can run arbitrary commands, not just file edits, and it operates over a whole multi-step task (per `tool-use-agentic-loop/03`) before coming back to the human, rather than proposing one edit at a time.

- **Feedback loop:** medium - the human delegates a task ("fix the failing test," "add input validation to this endpoint") and checks in every several iterations, not every single edit, though most terminal agents still ask for explicit approval before destructive shell commands.
- **Context available to the agent:** the full local environment - it can run the actual test suite, inspect actual git history, install actual dependencies, and observe real command output, not just editor-visible state.
- **Typical unit of work:** a self-contained task spanning multiple files and several tool calls - closer to "what a human would do in one focused work session" than one keystroke.

### Model 3: Cloud/async (remote, detached)
The agent runs on infrastructure the human doesn't have a terminal open to - typically triggered from a task description, a ticket, or a chat message - and works through the full loop unattended, submitting a pull request or a diff for review only once it believes the task is complete.

- **Feedback loop:** loosest - review happens after the fact, at PR granularity, the same way a human would review a colleague's contribution; there is no live steering during execution.
- **Context available to the agent:** whatever the platform provisions for it (its own sandboxed checkout, its own compute), which means it can run for much longer without consuming the human's local machine or attention, but the human also cannot glance over its shoulder mid-task.
- **Typical unit of work:** a full ticket-sized deliverable - "implement this feature," "fix this bug report" - evaluated as a finished artifact, not as a sequence of edits.

> **Example (Aug 2026):** cloud/async products commonly integrate at the level of "assign a ticket, get a PR back," mirroring how an engineering team already assigns work to a human contributor; the specific product lineup offering this changes often, but the assign-and-review shape is what's durable. This model is the launching point for `agentic-software-engineering/06`, which covers what changes once *trust calibration* - not mechanics - becomes the central problem.

### Worked example: routing the same task through all three models
Task: "The `/checkout` endpoint doesn't validate that `quantity` is a positive integer, causing a 500 error on bad input."

- **IDE-integrated:** the engineer opens `checkout.py`, places the cursor near the handler, and asks the agent to add validation. The agent proposes a five-line diff inline; the engineer reads it in three seconds, accepts, and moves on. Total elapsed human attention: under a minute, fully synchronous.
- **Terminal-native:** the engineer runs the agent from the CLI with the task description. The agent reads `checkout.py`, greps for how validation is done elsewhere in the codebase (to match existing conventions), writes the fix, writes a test for negative and zero quantities, runs the test suite, and reports back. The engineer was free to do something else for the few minutes this took, then reviews a small, self-verified diff.
- **Cloud/async:** the engineer files this as a ticket assigned to the agent. Minutes later (constrained by remote compute, not local attention) a pull request appears with the fix, a test, and a description referencing the original bug report. The engineer reviews it exactly as they would a junior teammate's PR - at their own convenience, not synchronously.

The underlying agentic loop (plan, act, observe, repeat) is identical in all three cases. What changed is only *how much of that loop happened while a human was watching*, and that single variable is what should drive which model you reach for.

### The diagnostic: how much live attention does this task deserve?
A practical rule of thumb: the right execution model tracks how *verifiable at a glance* the result will be, not how big the task is. A large but mechanical rename across 200 files is easy to verify in bulk (good fit for terminal-native or even cloud/async, checked by running the test suite). A three-line change to authentication logic is small but demands the tightest possible scrutiny (better suited to IDE-integrated, where the human sees the exact diff before it lands) - size and required oversight are not the same axis, and conflating them is the most common mis-routing mistake.

## Pros
- Matching model to task lets each strength compound: IDE-integrated protects flow state for exploratory work, terminal-native trades a little live attention for real shell-level verification (tests actually run), cloud/async frees human attention entirely for tasks that tolerate after-the-fact review.
- All three models share the same underlying loop mechanics, so skills, prompts, and failure-mode intuition (`tool-use-agentic-loop/03`, `agentic-software-engineering/02`) largely transfer between them.
- Terminal-native and cloud/async models can run genuinely long, multi-step tasks (installing dependencies, running full test suites, iterating on failures) that IDE-integrated agents, constrained to editor-visible state, typically cannot.

## Cons
- IDE-integrated agents' tight feedback loop costs the human continuous attention - it does not scale to running many tasks in parallel.
- Terminal-native and especially cloud/async agents can drift further from intent before anyone notices, precisely because oversight is looser; a cloud/async agent can spend its entire run pursuing a subtly wrong interpretation of the ticket with nobody able to redirect it until the PR lands.
- Cloud/async review happens at the coarsest grain (a whole PR), which can hide problems that would have been obvious as an inline diff - a reviewer skimming a 400-line PR is less likely to catch a subtle logic error than an engineer watching each line get proposed.
- Fragmented tooling: an organization using all three models needs review conventions, permissions, and trust norms for each, which is real process overhead beyond just picking a tool.

## Alternatives
- **No agent at all, manual editing** — still correct for work that requires judgment the task's stakes don't justify delegating, or in codebases/environments where agent tooling isn't yet trusted or permitted (regulated code, no sandboxing available).
- **Pair programming with another human, agent as an unused option** — appropriate when the task is primarily about knowledge transfer or team alignment, where the value is in two humans thinking together, not in generating a diff quickly.
- **Fixed CI/CD automation (linters, codemods, scripted refactors)** — for genuinely mechanical, well-specified transformations, a deterministic tool is cheaper, faster, and fully reproducible; reaching for an agentic loop (in any execution model) for a task with one known-in-advance sequence of steps is unnecessary machinery, per the diagnostic in `tool-use-agentic-loop/03`.

## When to use it
Use IDE-integrated agents for small, exploratory, or judgment-heavy edits where you want to review every step as it happens. Use terminal-native agents for self-contained tasks that benefit from real shell verification (running tests, installing packages, checking build output) and where you're willing to trade live attention for a session you can step away from. Use cloud/async agents for well-specified, ticket-sized work where after-the-fact PR review is an acceptable and normal way to receive the result - the same bar you'd apply to a remote teammate's contribution.

## When NOT to use it
Do not route a task through cloud/async or terminal-native execution just because it's available if the task is high-stakes and hard to verify after the fact (security-sensitive logic, data migrations, anything where a subtly wrong result is expensive to detect once merged) - use IDE-integrated or manual editing instead, where a human's eyes are on every step. Conversely, do not force large, well-defined, low-ambiguity batches of work through an IDE-integrated agent's one-diff-at-a-time cadence - that wastes the human's attention on approvals that terminal-native or cloud/async execution could handle with equivalent safety via automated tests.

## Key takeaways / mental model
All three execution models run the same agentic loop from `tool-use-agentic-loop/03`; they differ only in how tightly that loop is coupled to live human attention - tight (IDE-integrated), loose-but-synchronous (terminal-native), or fully detached (cloud/async). Route a task by asking "how verifiable will this be after the fact, and how much do I need to watch it happen," not by which tool is trendiest. This axis - live attention versus after-the-fact review - is also the same axis `agentic-software-engineering/02` uses to distinguish vibe coding from controlled agent use, and the one `agentic-software-engineering/06` returns to when async agents make trust calibration, not mechanics, the central problem.

## Self-check questions
1. Your team needs to rename a widely used internal API across 150 files with no behavior change, verified entirely by the existing test suite passing. Which execution model fits best, and why does task size alone not answer this question?
2. A teammate wants to route a change to payment-processing logic through a cloud/async agent to "save time," planning to review the PR when it lands. Using the live-attention axis from this lesson, explain what specifically goes wrong with that plan even if the final diff looks correct.
3. Explain why an IDE-integrated agent and a cloud/async agent can be running the exact same underlying agentic loop (per `tool-use-agentic-loop/03`) and yet require completely different review habits from the human.
4. A terminal-native agent reports "all tests pass" after a multi-file refactor. What does the terminal-native model's access to a real shell let you trust about that claim that an IDE-integrated agent's claim of the same words would not, by default, earn?

## References
- niteagent.com, "AI Coding Agents 2026: The State of Play - CLI, IDE, and Cloud Agents Compared" (2026), https://niteagent.com/blog/2026-05-21-ai-coding-agents-state-of-play/
- webidroid.com, "Terminal-Native Coding Agents: A Developer's Guide to 2026 Tooling" (2026), https://webidroid.com/blog/terminal-native-coding-agents/
- Augment Code, "9 Best AI Coding Agent Desktop Apps in 2026" (2026), https://www.augmentcode.com/tools/best-ai-coding-agent-desktop-apps
- `tool-use-agentic-loop/03`, this repository - underlying plan/act/observe loop mechanics
