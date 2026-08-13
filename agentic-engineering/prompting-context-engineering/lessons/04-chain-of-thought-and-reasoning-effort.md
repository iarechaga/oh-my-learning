---
id: prompting-context-engineering/04
subject: prompting-context-engineering
title: "Chain-of-Thought and Reasoning Effort: What Actually Helps and What's Theater"
slug: chain-of-thought-and-reasoning-effort
status: drafted
mastery:
seniority: mid
source: "Kojima et al., Large Language Models are Zero-Shot Reasoners (arXiv:2205.11916, 2022); Turpin et al., Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting (NeurIPS 2023); Sprague et al., To CoT or not to CoT? A Meta-Analysis (2025, arXiv:2409.12183); Arcuschin et al., Chain-of-Thought Reasoning In The Wild Is Not Always Faithful (arXiv:2503.08679, 2025); vendor docs on reasoning-effort controls (OpenAI, Anthropic, Google, 2026)"
durability: durable
prerequisites: [prompting-context-engineering/03]
created: 2026-08-10
updated: 2026-08-10
---

# Chain-of-Thought and Reasoning Effort: What Actually Helps and What's Theater

## TL;DR
Chain-of-thought (CoT) prompting - asking a model to produce intermediate reasoning steps before its final answer - reliably improves accuracy on tasks with real multi-step structure, especially mathematical and symbolic reasoning, by giving the autoregressive process more tokens to condition later steps on. But CoT is not free, not universally helpful, and not a transcript of what the model "actually thought": research through 2025 shows it provides little or negative benefit on many non-symbolic tasks, and that the visible reasoning trace can be an unfaithful, post-hoc-sounding rationalization rather than the true causal path to the answer. Modern "reasoning-effort" controls productize CoT as a dial, but the same caveats about when it helps still apply - more thinking tokens is not automatically better.

## The idea
Lesson 01 established that autoregressive generation conditions each token on everything before it, including tokens the model itself just produced. Chain-of-thought prompting exploits this directly: if you get the model to write out intermediate reasoning steps before its final answer, the final answer is now conditioned on that intermediate reasoning as part of its own input, rather than being produced "in one shot" straight from the question. For tasks that genuinely decompose into steps - arithmetic, multi-hop logic, code tracing - this measurably helps, because the model effectively gets to "show its work" and each step narrows the space of plausible next steps, similar to how a person doing long division writes out intermediate remainders instead of guessing the final quotient directly.

The idea exists because early large language models performed surprisingly badly on multi-step problems when asked to answer directly, and dramatically better when prompted to reason step by step first - this was one of the most influential empirical findings in early prompting research (Kojima et al., 2022, showed that simply appending "Let's think step by step" raised accuracy on the MultiArith benchmark from 17.7% to 78.7% for one model, with no other change to the prompt). The idea's popularity created a natural next question that took years of follow-up research to answer honestly: does this generalize to *all* reasoning-flavored tasks, and does the visible reasoning trace mean what it appears to mean? The honest answer to both, as of 2025-2026 research, is no - and this lesson exists to teach the boundary, not just the technique.

## How it works

### The mechanism: more conditioning tokens, not "more thinking" in a human sense
When a model produces "Let's think step by step: first, 12% of 250 is 30. Then, 250 - 30 = 220. So the answer is 220," each of those intermediate tokens becomes part of the input for predicting the next one - including the final answer. This is not the model pausing to "think" in the way a human pauses; it is the model generating additional tokens that constrain the token-prediction problem for the tokens that follow. A model asked to jump straight to "220" has to get the entire computation right in the implicit process that produces a single token's probability distribution; a model that writes out "30" as an intermediate token gets to condition the next steps on that already-committed intermediate result, which is a strictly easier prediction problem at each step. This is the durable mechanistic reason CoT helps at all, independent of any particular vendor's implementation.

### Where CoT reliably helps: symbolic, multi-step, decomposable tasks
A 2025 meta-analysis aggregating over 100 papers (Sprague et al., "To CoT or not to CoT?") found that CoT's gains concentrate heavily in tasks involving mathematics and formal/symbolic logic, where the task has a genuine step-by-step structure that benefits from being made explicit. On these tasks, CoT gains are large and consistent - often tens of percentage points, echoing Kojima et al.'s original results.

### Where CoT does little or hurts: non-symbolic tasks
The same meta-analysis found that on tasks involving general knowledge retrieval, "soft" commonsense reasoning, and other non-symbolic domains, CoT prompting produced minimal improvement and sometimes measurably worse performance than direct answering. This runs against the assumption - common among practitioners who generalized from CoT's early math-benchmark success - that "asking the model to reason" is a universally safe default to improve quality. It is not: for tasks where there is no real multi-step computation to make explicit, forcing the model to generate a reasoning trace can introduce noise, invite the model to talk itself into a worse answer through spurious-sounding logic, or simply waste tokens and latency on a step that isn't doing real work.

**Worked example - CoT on the wrong kind of task.** Consider a simple factual-retrieval question: "What is the capital of Australia?" A direct-answer prompt reliably returns "Canberra." A CoT-style prompt ("Let's think step by step about the capital of Australia") has no genuine multi-step computation to decompose - there's no chain of intermediate facts that need to be derived - so the model may generate a plausible-sounding but unnecessary reasoning trace ("Australia is a country in Oceania... many people mistakenly think Sydney is the capital, but the actual capital is..."), which does not improve the odds of getting "Canberra" right and can occasionally introduce an opening for the model to reason itself toward an incorrect but confident-sounding correction. This is the exact pattern the meta-analysis captures at scale: CoT is not a universal accuracy button, and applying it reflexively to every prompt is measurable waste on a large fraction of real tasks, not a safe default.

### The faithfulness problem: the reasoning trace is not a transcript of causation
A separate and more unsettling line of research asks a different question: even when CoT *does* correlate with better accuracy, does the visible reasoning trace actually describe the process that produced the answer? Turpin et al. (2023) showed that when a model's answer is covertly biased by an irrelevant feature of the prompt (e.g., the answer choices being reordered so the "correct-looking" option is always A), the model's CoT will confidently justify the biased answer using seemingly sound reasoning, without ever mentioning the actual (irrelevant) feature that swayed it. The explanation is fluent, plausible, and wrong about its own causation.

Follow-up work through 2025 (e.g., Arcuschin et al., "Chain-of-Thought Reasoning In The Wild Is Not Always Faithful," 2025) found this is not a rare adversarial artifact: even under natural, non-adversarial prompting, production models exhibit measurable unfaithfulness, in two recognizable patterns:
- **Implicit post-hoc rationalization** - the model reaches a conclusion through processes it doesn't verbalize, then writes a CoT trace that reads as if the conclusion followed logically from the stated steps.
- **Unfaithful illogical shortcuts** - the CoT trace contains reasoning that is visibly invalid on inspection, yet the model still lands on a correct-looking answer, meaning the trace didn't actually drive the outcome despite the presentation as if it did.

Reported unfaithfulness rates varied substantially by model and evaluation, from single digits up to double-digit percentages on weaker/smaller models, dropping close to zero (but not reaching exactly zero) on the strongest reasoning-oriented models at the time of the study. The trend of "better models are more faithful, but never perfectly faithful" is the durable takeaway - not any specific percentage, which is model- and benchmark-specific and will keep shifting.

**Why this matters practically, not just philosophically.** If you use a model's CoT trace as a debugging tool ("let me read its reasoning to understand why it got this wrong") or as an audit trail in a safety-critical or compliance context ("the model's stated reasoning shows it considered X before deciding Y"), faithfulness research says you should treat that trace as evidence, not proof. It is useful signal - genuinely wrong reasoning steps often do correlate with wrong answers - but a clean-looking reasoning trace does not guarantee the answer was actually derived that way, and a model can be systematically wrong about its own process while sounding perfectly convincing about it.

### Reasoning-effort controls: productized CoT, still bounded by the same limits
> **Example (2026):** Several vendors expose an explicit control that trades latency/cost for more internal deliberation before the final answer - e.g., a reasoning-effort setting with tiers like low/medium/high (or similar), or an extended-thinking mode with a token budget or effort level. The exact parameter name, tiers, and mechanism differ by vendor and change over time (as of 2026, some vendors have moved from a raw thinking-token budget toward a coarser effort-level knob) - treat any specific parameter name as a dated example, not the concept itself; see `landscape-snapshot` for current specifics.

The durable concept underneath these knobs is simply "spend more inference-time compute generating intermediate tokens before committing to a final answer" - mechanically the same lever as prompted CoT, just exposed as a first-class API parameter instead of something you elicit via prompt wording, and typically using reasoning processes and training the model saw during its own training rather than a raw prompt trick. This has two consequences worth internalizing:
1. **The same task-dependent payoff curve applies.** Cranking reasoning effort to maximum on a simple factual-lookup or classification task usually buys you latency and cost, not accuracy, for the same reason prompted CoT doesn't help non-symbolic tasks - there's no genuine multi-step computation for the extra tokens to do useful work on.
2. **The same faithfulness caveat applies, arguably more so.** Many reasoning-effort implementations summarize, redact, or otherwise don't expose the raw internal reasoning trace verbatim, which is a further reason not to treat whatever trace *is* shown as a complete or literal causal account.

**Worked example - a wasted reasoning-effort budget.** A team building a customer-intent classifier (route to billing/technical/other) sets a reasoning-effort parameter to its highest tier "to be safe," on the theory that more reasoning can only help. They measure: classification accuracy is statistically indistinguishable from the low-effort setting (both around 89% on their eval set), but median latency per request goes from ~400ms to ~2.8s, and per-request cost roughly triples due to billed reasoning tokens. This is the CoT-doesn't-help-non-symbolic-tasks finding showing up as a production cost bug: the task is closer to pattern classification than multi-step derivation, so extra deliberation tokens aren't doing work that changes the outcome - they're pure overhead. The fix isn't "turn reasoning off entirely and hope," it's benchmarking effort levels against the specific task the way you'd benchmark any other tunable parameter, rather than defaulting to maximum on the assumption that reasoning is a free accuracy dial.

### A practical decision procedure
1. **Does the task have genuine multi-step or symbolic structure** (arithmetic, multi-hop logic, code tracing, planning with dependencies)? If yes, CoT/reasoning-effort is a strong candidate.
2. **Is the task closer to retrieval, classification, or "soft" judgment** (fact lookup, sentiment, simple routing, style transfer)? If yes, default to a lower reasoning-effort setting or none, and verify empirically before adding more.
3. **Regardless of (1) or (2), if you plan to use the reasoning trace as an explanation, audit trail, or debugging signal**, treat it as suggestive, not authoritative - corroborate with independent evidence (does the stated reasoning actually match behavior under controlled perturbation, similar to how Turpin et al. tested it) before trusting it as a causal account.
4. **Measure, don't assume.** Because the payoff is task-dependent and vendor mechanisms keep changing, the only durable practice is running your own small benchmark (accuracy vs. latency/cost) at a couple of reasoning-effort levels on your actual task distribution, rather than picking a level by intuition or defaulting to maximum "to be safe."

## Pros
- Large, well-replicated accuracy gains on genuinely multi-step and symbolic tasks, with a mechanistic explanation (more conditioning tokens) that holds across vendors and model generations.
- Reasoning-effort controls make this lever tunable and inspectable (to varying degrees) without requiring custom prompt engineering.
- A visible reasoning trace, even when imperfectly faithful, is still useful debugging signal in aggregate and often correlates with correctness even if it isn't a literal causal transcript.

## Cons
- Minimal or negative benefit on many non-symbolic tasks (retrieval, commonsense, soft judgment), where it wastes tokens, latency, and cost.
- The reasoning trace can be an unfaithful, fluent-sounding rationalization rather than the actual cause of the answer - a documented finding across both adversarial and natural prompting conditions.
- Higher reasoning effort increases latency and cost roughly monotonically, so misapplying it (defaulting to "high" everywhere) is a direct, measurable production cost with no guaranteed accuracy return.
- Because reasoning-effort mechanisms and their exposed traces are vendor-specific and evolving rapidly, building product logic that depends on the literal content or availability of a reasoning trace is fragile.

## Alternatives
- **Direct answering (no CoT)** — preferable for simple classification, retrieval, or short-form tasks where benchmarking shows no CoT benefit; cheaper and faster, and avoids the faithfulness pitfalls entirely since there's no trace to misplace trust in.
- **Structured decomposition / explicit sub-task pipelines** (breaking a task into separate, verifiable API calls or tool calls rather than one free-form reasoning trace) — preferable when correctness of each intermediate step actually matters and needs to be checked or logged individually, since each step becomes an independently inspectable, verifiable output rather than an unverified span of prose inside one trace.
- **Self-consistency / multiple-sample voting** (generate several independent CoT traces and take the majority answer) — preferable when the task benefits from CoT but individual traces are noisy; trades additional cost/latency for robustness, and is a documented technique in the broader prompting-technique literature (see lesson 03's source, *The Prompt Report*) alongside plain single-pass CoT.
- **External verification/tool use** (have the model check its own arithmetic with a calculator tool, or verify a claim against a retrieved source) — preferable whenever ground truth is checkable, since it replaces "trust the reasoning trace" with "verify the output," sidestepping the faithfulness problem entirely for the checkable parts of a task.

## When to use it
Use CoT or a moderate reasoning-effort setting for tasks with real multi-step or symbolic structure - math, multi-hop logic, planning, code tracing, anything with a genuine intermediate-state computation. Use it when you've empirically verified a lift on your own task, not just because the task "sounds like it involves reasoning." Use higher reasoning effort selectively, on the subset of requests that are actually hard, rather than uniformly.

## When NOT to use it
Don't default to CoT or maximum reasoning effort for retrieval, classification, formatting, or short factual tasks without first measuring - the research consensus by 2025-2026 is that this class of task sees little or negative benefit, only added cost and latency. Don't treat a model's reasoning trace as a reliable audit trail or explanation in a compliance-sensitive or safety-critical context without independent corroboration; faithfulness research shows fluent-sounding traces can misrepresent the model's actual process, even absent any adversarial intent.

## Key takeaways / mental model
CoT works by turning "produce the right answer in one shot" into "produce intermediate tokens that make the right answer an easier next-token prediction" - which is a real, mechanistic lever, not magic, and it pays off precisely where genuine multi-step computation exists to be decomposed. It is not a free accuracy dial, and it is not a window into the model's "true thoughts" - treat the trace as useful but unverified signal, and treat reasoning-effort settings the way you'd treat any other tunable inference parameter: benchmark it on your actual task before defaulting to "more."

## Self-check questions
1. A teammate proposes turning on maximum reasoning effort for every request "since it can only help." Using the Sprague et al. meta-analysis finding, explain when this reasoning is wrong and sketch the experiment you'd run to check.
2. Explain, mechanically (in terms of autoregression from lesson 01), why writing out an intermediate step like "250 * 0.12 = 30" actually changes the probability of the model getting the next step right, rather than just being cosmetic.
3. Your team wants to use a model's CoT trace as an audit log to explain loan-approval decisions to a regulator. What does the Turpin et al. and Arcuschin et al. research imply about the risk of relying on this trace as-is, and what would you add to make the audit trail more trustworthy?
4. Given a task that mixes both symbolic sub-steps (computing a discount) and soft judgment sub-steps (assessing whether a complaint sounds urgent), how would you decide whether to apply CoT to the whole task, part of it, or none of it?
5. A benchmark shows CoT improves your task's accuracy from 80% to 88%, but you can't tell whether the improvement comes from genuinely better reasoning or from the model getting more chances to "self-correct" a first guess. Propose one experiment (referencing the faithfulness literature) that would help distinguish these explanations.

## References
- Kojima, Gu, Reid, Matsuo, and Iwasawa, "Large Language Models are Zero-Shot Reasoners" (arXiv:2205.11916, 2022), https://arxiv.org/abs/2205.11916
- Turpin, Michael, Perez, and Bowman, "Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting" (NeurIPS 2023), https://papers.neurips.cc/paper_files/paper/2023/file/ed3fea9033a80fea1376299fa7863f4a-Paper-Conference.pdf
- Sprague et al., "To CoT or not to CoT? Chain-of-thought helps mainly on math and symbolic reasoning" (ICLR 2025, arXiv:2409.12183), https://arxiv.org/pdf/2409.12183
- Arcuschin et al., "Chain-of-Thought Reasoning In The Wild Is Not Always Faithful" (arXiv:2503.08679, 2025), https://arxiv.org/abs/2503.08679
- FutureAGI, "LLM Reasoning 2026: o3, GPT-5, Claude Thinking, R1" (2026), https://futureagi.com/blog/llm-reasoning-2025/
