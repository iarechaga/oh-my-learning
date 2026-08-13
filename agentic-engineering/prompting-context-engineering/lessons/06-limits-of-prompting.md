---
id: prompting-context-engineering/06
subject: prompting-context-engineering
title: "The Limits of Prompting: Why Some Failures Aren't Prompt Problems"
slug: limits-of-prompting
status: drafted
mastery:
seniority: senior
source: "arXiv:2602.09947 Trustworthy Agentic AI Requires Deterministic Architectural Boundaries (2026); arXiv:2604.04990 Architecture Without Architects (2026); arXiv:2604.27891 In-Context Prompting Obsoletes Agent Orchestration for Procedural Tasks (2026); arXiv:2601.01743 AI Agent Systems: Architectures, Applications, and Evaluation (2026); Anthropic docs: Effective context engineering for AI agents (2025); k2view blog: RAG vs prompt engineering (2026)"
durability: durable
prerequisites: [prompting-context-engineering/04, prompting-context-engineering/05]
created: 2026-08-10
updated: 2026-08-10
---

# The Limits of Prompting: Why Some Failures Aren't Prompt Problems

## TL;DR
Prompting changes what you ask the model to do; it cannot change what the model is capable of doing, what it knows, or what it can act on. When an agent fails, the fix is only sometimes a better prompt - it is often a missing tool, a missing piece of context, a task too large for one reasoning pass, or a decision that genuinely needs a deterministic rule rather than a probabilistic judgment. Diagnosing which bucket a failure falls into is the senior-level skill this lesson teaches; getting it wrong means iterating on prompts forever against a wall that prompting cannot climb.

## The idea
Lessons 02 through 05 built up a real toolbox: prompt anatomy, few-shot and role framing, chain-of-thought, structured output. Applied well, these techniques close a large and genuine gap between "a model that could theoretically do the task" and "a model that reliably does the task, in the format you need, with the reasoning you want." It is tempting to treat that toolbox as universal - to respond to every disappointing output by rewording the instructions, adding another example, telling the model to "be more careful," or bolting on a longer chain-of-thought nudge.

That instinct has a ceiling, and the ceiling is structural, not a matter of trying harder. A prompt is an instruction given to a fixed model, at inference time, using only what fits in that one call's context. It cannot:
- teach the model a fact or a skill it was never trained on and that isn't present in the current context,
- give the model access to information or systems outside that context window,
- make a single forward pass reliably perform a task that genuinely requires many independent, verifiable steps with intermediate checks,
- turn a probabilistic, sometimes-wrong judgment into a deterministic, always-correct one.

Recognizing this ceiling is what separates prompt *tinkering* (rewording indefinitely, hoping the next phrasing works) from prompt *engineering with architectural judgment* (correctly routing a failure to the fix that actually addresses its cause). This lesson exists precisely to set up why the rest of the `agentic-engineering` domain exists: tool use gives models capabilities prompting cannot; context engineering (lessons 07-10 here) manages what the model can see; multi-agent orchestration decomposes tasks too large for one pass; instruction and context design engineers the scaffolding around the model. None of those are "better prompting" - they are different layers of the system, and a failure at one layer is not fixable by tuning another.

## How it works

### A diagnostic framework: four buckets for "the prompt didn't work"
When an agent produces a wrong, incomplete, or unsafe output, ask which of these four things actually happened before touching the prompt:

1. **Capability gap** - the model does not know the fact, does not have the skill, or the answer requires information that was never in its training data and isn't in the current context. No phrasing of the question changes what the model knows.
2. **Missing affordance** - the model would do the right thing *if it could act on the world*, but it has no tool to check a live price, query a database, run code, or send a message. The model can only describe what it would do; it cannot do it.
3. **Context gap** - the relevant information exists and the model could use it, but it simply is not present in this call's context window. This is a context-engineering failure (lesson 07), not a prompting failure - the fix is to *put the right information there*, not to phrase the request differently around its absence.
4. **Decomposition/reliability gap** - the task requires many sequential or parallel steps, each with room for error, and asking for the whole thing in one shot compounds per-step error rates into an unacceptable overall failure rate. This needs task decomposition, intermediate verification, or multi-agent orchestration - not a single better-worded mega-prompt.

Only a fifth category is a genuine prompting problem: the model *has* the knowledge, the access, the context, and the task is small enough for one pass, but the instructions are ambiguous, underspecified, or poorly formatted - the actual domain of lessons 02-05.

### Worked example: capability gap dressed up as a prompt problem
A team asks a model, via careful prompting with detailed instructions and three few-shot examples, to answer "what is our current AWS spend this month, broken down by service?" The model returns a plausible-looking table with numbers - and every number is fabricated, because the model has no access to the team's AWS billing console and was never trained on this team's private account data. No prompt improvement fixes this: better wording produces a *more confident-sounding* fabrication, not a correct one, because confidence and correctness are independent properties of a hallucinated answer. The team iterated for two days on prompt phrasing before recognizing this was bucket 2 (missing affordance) - the fix was giving the agent a tool that calls the AWS Cost Explorer API, at which point the same simple prompt worked on the first try, because the model now had something true to report instead of something to guess.

### Worked example: context gap masquerading as capability gap
A support-ticket triage agent is asked to route tickets to the right team, and it keeps misrouting billing disputes to the technical-support queue. The instinct is to add more explicit routing rules to the system prompt ("if the ticket mentions a charge, refund, or invoice, route to Billing"). This helps marginally but the error rate stays high, because the actual missing piece is the customer's account tier and recent billing history - a Tier-3 enterprise customer's "charge" complaints route differently than a self-serve customer's. That data exists in the company's CRM, but it was never being fetched into context; the agent was guessing from ticket text alone. Once the pipeline retrieves the account record and includes it in context (a context-engineering fix, lesson 07), the *same* routing prompt performs far better - the rules were never the problem, the missing context was.

### Worked example: decomposition gap - when one prompt can't carry the task
Consider asking a single model call to "refactor this 40-file codebase to switch from REST to GraphQL, update all the tests, and write a migration guide." Even with a long context window and a superb system prompt, single-pass reliability compounds badly across many independent decisions: if each of 40 file-level changes has even a 90% chance of being individually correct, the probability that *all* 40 are simultaneously correct is 0.9^40 ~ 1.5%. This is the same compounding-probability logic as tail-latency amplification in distributed systems (see `architecture/ddia/lessons/01`) applied to reasoning steps instead of network calls: independent per-step success rates multiply, and the aggregate success rate collapses even when each step looks individually solid. No single prompt - however well written - repeals this arithmetic. What works is decomposing the task into stages with intermediate verification (change one file, run its tests, confirm, move to the next), which is exactly what tool use, the agentic loop, and multi-agent orchestration (later subjects in this domain) are built to do. A prompt cannot substitute for an architecture that checks its own work along the way.

### Worked example: when the "fix" needs to be deterministic, not probabilistic
A financial-approval agent is prompted extensively - with examples, explicit thresholds, and warnings - to "never approve a transaction over $10,000 without human sign-off." Under normal conditions it complies. Under adversarial or unusual phrasing (a request that frames the transaction differently, splits it, or embeds conflicting instructions inside data the agent is processing), it occasionally does not. This is not a prompt-wording bug to iterate away - a model's output remains fundamentally probabilistic, and probabilistic compliance with a hard business rule is not the same guarantee as enforcing that rule outside the model. Current research on agentic-AI trustworthiness argues exactly this: certain safety and compliance boundaries need deterministic architectural enforcement - a code-level check that blocks the transaction API call above $10,000 regardless of what the model decided - not a stronger prompt asking the model to please not do that. The prompt is still worth having (it reduces how often the deterministic gate even gets triggered), but it cannot be the *only* line of defense for a rule that must never break.

## Pros
- **Prevents wasted iteration.** Correctly diagnosing "this isn't a prompt problem" stops teams from burning days rewording instructions against a structural ceiling.
- **Points to the actual fix faster.** The four-bucket framework routes a failure to tool design, context engineering, task decomposition, or deterministic guardrails - each a well-understood fix, once correctly identified.
- **Sets honest expectations with stakeholders.** "We need to build a retrieval pipeline" is a more useful statement to a stakeholder than "we're still tuning the prompt," even though the second sounds cheaper and faster.
- **Establishes when NOT to trust the model alone**, which is foundational judgment for building anything safety- or compliance-adjacent.

## Cons
- **Diagnosis takes real effort.** Distinguishing "the model is confused because of a bad prompt" from "the model is confused because the information genuinely isn't there" requires deliberately testing with the information present, which is extra work compared to just rewording.
- **Can be used as an excuse.** "This isn't a prompting problem" is sometimes true and sometimes a convenient way to avoid the harder work of writing a genuinely clear prompt; the framework must be applied honestly, not defensively.
- **The boundary moves over time.** What counts as a capability gap today may close as models improve (a fact once unknown might now be in training data); a diagnosis made in 2026 is not guaranteed to hold in 2028. Revisit assumptions, don't assume a gap is permanent.
- **Over-architecting is its own failure mode.** Reaching immediately for multi-agent orchestration or a deterministic guardrail for a problem that a clearer prompt would have solved wastes engineering effort in the opposite direction.

## Alternatives
- **Iterative prompt refinement** - still the right first move for genuine bucket-5 (ambiguous instructions) failures; do not skip it reflexively in favor of heavier architecture. Preferable whenever the model plausibly has the knowledge, access, and context, and the task is small enough for one pass.
- **Fine-tuning or continued pretraining** - addresses a genuine capability gap by changing the model's weights rather than what you tell it at inference time. Preferable when the same capability gap recurs constantly, at high volume, and retrieval/tool access can't supply it (e.g. teaching a house style or a narrow classification skill baked into every call).
- **Retrieval-augmented generation** (previewed here, covered fully in lesson 09) - addresses a context gap by fetching the missing information at inference time instead of retraining. Preferable when the missing information changes often (so baking it into weights would go stale) or is too large to fit in any context window.
- **Human-in-the-loop review** - addresses a reliability gap by adding a verification step outside the model entirely. Preferable when the cost of a wrong answer is high and no amount of decomposition gets the automated success rate high enough to run unsupervised.

## When to use it
Run this diagnostic every time an agent underperforms, before touching the prompt: could a well-informed human with the *same* information the model had, and the *same* tools the model had, have done better? If yes, look at instructions and formatting first. If a well-informed human would have failed too because they didn't know something, couldn't access something, or the task was too big for one uninterrupted attempt - fix that instead.

## When NOT to use it
Do not use this framework to avoid writing a clear prompt in the first place; most early-stage agent failures genuinely are bucket-5 (ambiguous instructions, missing examples, wrong output format) and are cheaper to fix than any architectural change. Reach for tool use, retrieval, decomposition, or deterministic guardrails only after you have evidence - not a hunch - that the model had what it needed and still failed.

## Key takeaways / mental model
A prompt is a request made to a fixed model with a fixed context. It can shape *how* the model uses what it has; it cannot supply what the model doesn't have. When something fails, ask in order: does the model know this? can it act on this? is the needed information actually in context? is this one atomic step or many compounding ones? does this decision need a guarantee stronger than "usually right"? Only when all five answers come back clean does the fix belong back in the prompt.

## Self-check questions
1. An agent is asked to summarize a company's Q3 financial results and gives a plausible but factually wrong summary. Walk through the four-bucket diagnostic to figure out what's actually broken, and describe what evidence would let you tell capability gap apart from context gap.
2. A teammate has spent a week trying different phrasings of a system prompt to stop an agent from occasionally leaking a customer's other-customer data into a support response. Using the deterministic-vs-probabilistic distinction, explain why prompting alone is the wrong lever here and what you'd build instead.
3. Using the independent-step-compounding math from the codebase-refactor example, calculate the aggregate success probability of a 10-step agentic task where each step has a 95% independent success rate. What does this imply about single-pass-versus-decomposed task design at that step count?
4. Give an example of a failure that looks like a capability gap on the surface but is actually a context gap. What test would distinguish the two?
5. A stakeholder asks "why can't we just tell it to be more careful?" for a task that is actually a decomposition-gap failure. How would you explain, in one or two sentences, why that instruction doesn't fix the underlying problem?

## References
- arXiv:2602.09947 - Trustworthy Agentic AI Requires Deterministic Architectural Boundaries
- arXiv:2604.04990 - Architecture Without Architects: How AI Coding Agents Shape Software Architecture
- arXiv:2604.27891 - In-Context Prompting Obsoletes Agent Orchestration for Procedural Tasks
- arXiv:2601.01743 - AI Agent Systems: Architectures, Applications, and Evaluation
- [Anthropic docs: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [k2view blog: RAG vs prompt engineering - Getting the best of both worlds](https://www.k2view.com/blog/rag-vs-prompt-engineering/)
- `architecture/ddia/lessons/01-reliability-scalability-maintainability.md` (tail-latency amplification, for the compounding-probability analogy)
