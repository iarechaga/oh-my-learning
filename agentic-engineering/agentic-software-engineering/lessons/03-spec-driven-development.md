---
id: agentic-software-engineering/03
subject: agentic-software-engineering
title: "Spec-Driven Development: Specs as the Source of Truth"
slug: spec-driven-development
status: drafted
mastery:
seniority: senior
source: "GitHub, spec-kit repository and documentation (released Sep 2025, accessed Aug 2026), https://github.com/github/spec-kit; MarkTechPost, \"Meet GitHub Spec-Kit: An Open Source Toolkit for Spec-Driven Development with AI Coding Agents\" (May 2026), https://www.marktechpost.com/2026/05/08/meet-github-spec-kit-an-open-source-toolkit-for-spec-driven-development-with-ai-coding-agents/; Sean Grove (OpenAI), \"The New Code,\" talk at AI Engineer World's Fair (2025), transcript https://lawwu.github.io/transcripts/8rABwKRsec4.html; Help Net Security, \"Package hallucination: LLMs may deliver malicious code to careless devs\" (Apr 2025), https://www.helpnetsecurity.com/2025/04/14/package-hallucination-slopsquatting-malicious-code/"
durability: durable
prerequisites: [agentic-software-engineering/02]
created: 2026-08-10
updated: 2026-08-10
---

# Spec-Driven Development: Specs as the Source of Truth

## TL;DR
Spec-driven development (SDD) treats a versioned, structured specification - not the generated code - as the primary artifact humans and agents work against: the spec is written and reviewed first, a technical plan and task breakdown are derived from it, and code is generated and regenerated as the spec's *expression*, not the other way around. It emerged in 2025 specifically as a response to three documented failure modes of unconstrained agentic coding - intent drift, context decay, and unverifiable output - that `agentic-software-engineering/02` covers as symptoms and this lesson covers as a structural fix.

## The idea
`agentic-software-engineering/02` established that controlled agent use means verifying an agent's output *after* it's generated - reading the diff, checking edge cases, confirming APIs exist. That works, but it has a scaling problem: review effort grows with the size and ambiguity of what you're reviewing, and a short natural-language prompt like "add login" is so underspecified that the agent has to *invent* dozens of decisions (session length, password requirements, error messages, what happens on a duplicate email) that the prompt never actually stated. Reviewing after the fact means discovering, diff by diff, which of those invented decisions you actually agree with - and on a large or fast-moving codebase, that discovery process breaks down in three specific, named ways:

- **Intent drift**: an underspecified prompt gets a plausible-sounding implementation that satisfies the literal words but not the actual intent, because the agent filled every gap with a "reasonable default" that reflects what's common in training data, not what this specific team or product actually wants.
- **Context decay**: as a codebase grows past what fits usefully in the agent's working context, it starts silently contradicting earlier decisions it can no longer see - reintroducing a pattern the team deliberately moved away from, or ignoring a constraint documented three files away.
- **Unverifiable output**: without explicit, checkable acceptance criteria, there is no principled way to know whether a given output is "done" or merely "looks done" - the exact "almost right, but not quite" complaint that was the top developer frustration in 2025 survey data (`agentic-software-engineering/02`).

Spec-driven development's answer is to move the point of human control *upstream*, before generation, rather than relying entirely on catching problems downstream in review. If the specification itself captures the actual intent, the acceptance criteria, and the constraints explicitly - and is reviewed and agreed on *before* any code is written - then the agent has dramatically less room to invent unwanted defaults, has a durable artifact to check its own context against as the codebase grows, and produces output that can be verified mechanically against stated criteria rather than judged by feel. This was articulated prominently in 2025 by figures inside AI labs themselves - one widely cited framing put it as "we keep the generated code and delete the prompt... like you shred the source and then very carefully version control the binary," arguing the spec, not the code, deserves to be the artifact under real version control and review. Practically, this produced concrete open-source tooling in 2025 (spec templates, CLIs, and structured workflows) built specifically to make "write the spec first" a repeatable practice rather than a one-off discipline.

## How it works

### The core phases
Spec-driven workflows, as they crystallized in 2025-2026 tooling, generally move through four stages, each producing an artifact the next stage consumes:

1. **Specify** - capture the *what and why* in a structured document: user stories, requirements, explicit non-goals, acceptance criteria. This is reviewed and refined by humans before anything else happens - it is deliberately *not* a prompt, because a prompt is meant to be thrown away and a spec is meant to be kept and versioned.
2. **Plan** - translate the spec into a technical approach: architecture, chosen libraries, data model, how it fits the existing system. This is where technology-specific decisions enter, kept separate from the *what* so the same spec could, in principle, support more than one technical plan.
3. **Tasks** - break the plan into small, independently checkable units of work, each with a clear definition of done that traces back to a specific piece of the spec.
4. **Implement** - the agent (or a human) executes each task, and each task's output is checked against its own stated acceptance criterion, not against a vague sense of whether the diff "looks right."

### Worked example: "add login" under a prompt-first vs spec-first workflow
**Prompt-first (what SDD reacts against):** the engineer types "add a login page" and hands it to an agent. The agent has to invent: what fields (email+password? username?), what happens on failure (generic error? field-specific?), whether there's rate limiting, session duration, what "logged in" unlocks. It picks plausible defaults for all of them, in one pass, and the engineer discovers which defaults they disagree with only by reading the finished diff - by which point the disagreement is a rewrite, not a redirect.

**Spec-first:** the specify phase produces something like:
```
Requirement: users can log in with email + password.
Acceptance criteria:
  - AC1: valid credentials -> redirected to /dashboard, session
         persists 24h
  - AC2: invalid credentials -> generic "invalid email or
         password" error (do not reveal which field was wrong)
  - AC3: 5 failed attempts from one IP in 10 minutes -> locked
         out for 15 minutes
  - AC4: password field is never logged, in any log level
Non-goals: SSO, "remember me," password reset (separate spec)
```
Every one of those lines is a decision the prompt-first version of this task left implicit and the agent would have had to invent. Writing them down *before* generation means the human's actual intent (don't leak which field was wrong; rate-limit; never log passwords) is the thing the agent generates against, not a hope the agent guesses correctly. The plan phase then picks, say, a specific session-token library and rate-limiting approach; the tasks phase breaks this into "implement AC1+AC2 happy/error path," "implement AC3 rate limiting," "implement AC4 log redaction," each independently testable; and the implement phase produces code the human (or an automated check) can verify line by line against a numbered acceptance criterion instead of against a vague "does this seem like a login page."

### Worked example: catching context decay across a growing codebase
A team has, over several months, standardized on a specific error-handling convention: every API handler returns a typed `Result<T, ApiError>` rather than throwing. A prompt-first agent asked to "add a new endpoint" three months and forty files later may never see the file where that convention was decided, and will plausibly reach for a `try/catch` instead, because that's the more common pattern in general training data. A spec that states "all handlers follow the `Result<T, ApiError>` convention (see `conventions/error-handling.md`)" as a standing constraint - reused across every future spec in the project, not re-derived from scratch each time - gives the agent (and the human reviewer) a fixed, checkable reference point that does not decay just because it scrolled out of a chat context window. This is precisely the mechanism by which spec-driven development addresses context decay: the constraint lives in a durable, referenced document, not in the fading memory of a long-running conversation.

### Verifying against a spec, mechanically
Because each task traces to a specific, numbered acceptance criterion, verification stops being "read the diff and decide if it feels right" (the vibe-coding failure mode from `agentic-software-engineering/02`) and becomes "for AC3, does a sixth failed login attempt within 10 minutes actually get locked out - yes or no." That's a testable, often literally automatable, question. This is also where spec-driven development directly blunts the hallucinated-API risk: a spec that names the actual internal libraries and conventions to use (rather than leaving the agent to guess a plausible-sounding one) removes much of the ambiguity that produces confidently wrong package or API references in the first place.

## Pros
- Moves the expensive part of human judgment - deciding what's actually wanted - to before generation, when it's cheap to change a sentence, instead of after, when it's a rewrite of a diff.
- Produces durable, versioned, referenceable artifacts (specs, acceptance criteria, conventions) that survive context-window limits and outlive any single chat session or agent run, directly countering context decay.
- Makes "is this done" a checkable question against stated criteria rather than a subjective read of the diff, which scales review effort down as task count goes up.
- Specs are reusable across regenerations - if the implementation needs to change frameworks or be redone by a different agent, the spec (the actual intent) doesn't have to be reverse-engineered from old code.

## Cons
- Writing a good spec is real, non-trivial work - underspecifying is exactly the prompt-first failure mode wearing a spec's clothing, and a spec with the same gaps as a bad prompt buys none of these benefits.
- Adds process overhead before any code exists, which is a poor trade for small, cheap-to-verify, or genuinely exploratory tasks - the same tasks `agentic-software-engineering/02` places at the vibe-coding end of the spectrum.
- Specs can themselves drift out of sync with the code they supposedly govern if nothing enforces that they're updated together - a stale spec is arguably worse than no spec, because it creates false confidence that intent is captured when it no longer is.
- Requires the team to actually maintain specs as first-class, reviewed artifacts (not a one-time ritual before the "real work" of coding begins), which is a cultural and process commitment, not just a tooling choice.

## Alternatives
- **Controlled agent use with after-the-fact review, no formal spec** (`agentic-software-engineering/02`) — lighter weight, appropriate when tasks are small enough or low-stakes enough that reviewing the finished diff is cheap and reliable; spec-driven development is the heavier tool for when that stops being true.
- **Plan-then-execute workflows without a durable spec artifact** (`agentic-software-engineering/04`) — decomposes a task into ordered steps before execution, which shares SDD's "decide before generating" instinct, but typically produces a disposable task list rather than a versioned, reusable specification document; SDD is the stricter, more durable version of the same underlying idea.
- **Traditional upfront requirements documents (pre-agent era)** — the general practice of writing requirements before building is decades older than coding agents; what's specific to SDD is treating the spec as an artifact the *agent* generates and regenerates against directly, with acceptance criteria structured for mechanical verification, not just human sign-off.

## When to use it
Reach for spec-driven development on work that is large, ambiguous, long-lived, or expensive to get subtly wrong - new features with real acceptance criteria, changes to established conventions in a growing codebase, anything where "almost right" would be genuinely costly to discover late. It is also the right response to the specific pain of context decay: any task spanning enough of a codebase that no single agent context window can hold the relevant history benefits from a durable spec that doesn't depend on that context window.

## When NOT to use it
Skip spec-driven development for small, cheap-to-verify, or genuinely exploratory work - a throwaway prototype, a one-line bug fix with an obvious correct answer, a spike meant to answer one narrow question. Writing a structured spec for these is the same mismatch as applying full controlled-agent-use rigor to disposable code (`agentic-software-engineering/02`): real overhead for a task whose stakes don't justify it. Also be wary of adopting SDD's ceremony without its substance - a spec document that's as vague as the prompt it replaced ("build a good login page") captures none of the benefit and just adds a step.

## Key takeaways / mental model
Spec-driven development is not "write documentation before coding" restated - it is a direct structural response to three named, observed failure modes of unconstrained agentic coding: intent drift (the agent fills gaps you never actually specified), context decay (the agent forgets constraints that scrolled out of view), and unverifiable output (there's no checkable definition of done). The mental model: **the spec is the thing you actually control and version; the code is a regenerable expression of it.** If you find yourself unable to say, in one sentence, what would make a given piece of agent output "wrong" versus "right," you're missing the acceptance criterion a spec would have forced you to write down before generation - and that gap is exactly where intent drift lives.

## Self-check questions
1. A teammate says "we already write requirements docs before big features, so we're already doing spec-driven development." What specifically would be missing from a traditional requirements doc for it to actually function as an SDD spec in the sense this lesson describes?
2. Walk through the "add login" worked example and identify one acceptance criterion (AC1-AC4) that, if omitted from the spec, would most plausibly reproduce the exact "almost right, but not quite" failure mode from `agentic-software-engineering/02`. Justify your choice.
3. Explain, using the error-handling-convention example, why a spec referencing `conventions/error-handling.md` addresses context decay in a way that simply having a longer agent context window would not fully solve.
4. Your team is under deadline pressure and someone proposes skipping the specify phase for a payment-refund feature "just this once, we know what we want." Using this lesson's when-NOT-to-use-it guidance and the stakes framing from `agentic-software-engineering/02`, argue for or against that shortcut.
5. A spec says "handle errors gracefully." Is this a usable acceptance criterion under the spec-driven model described in this lesson? If not, rewrite it as one, and explain what made the original version fail.

## References
- GitHub, spec-kit repository (released Sep 2025, accessed Aug 2026), https://github.com/github/spec-kit
- MarkTechPost, "Meet GitHub Spec-Kit: An Open Source Toolkit for Spec-Driven Development with AI Coding Agents" (May 2026), https://www.marktechpost.com/2026/05/08/meet-github-spec-kit-an-open-source-toolkit-for-spec-driven-development-with-ai-coding-agents/
- Sean Grove (OpenAI), "The New Code," AI Engineer World's Fair (2025), transcript https://lawwu.github.io/transcripts/8rABwKRsec4.html
- Help Net Security, "Package hallucination: LLMs may deliver malicious code to careless devs" (Apr 2025), https://www.helpnetsecurity.com/2025/04/14/package-hallucination-slopsquatting-malicious-code/
- InfoWorld, "Spec-driven AI coding with GitHub's Spec Kit" (2025/2026), https://www.infoworld.com/article/4062524/spec-driven-ai-coding-with-githubs-spec-kit.html
