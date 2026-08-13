---
id: agent-evaluation/03
subject: agent-evaluation
title: "LLM-as-Judge: Design, Calibration, and Known Biases"
slug: llm-as-judge
status: drafted
mastery:
seniority: senior
source: "Li et al., \"Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge,\" arXiv:2406.07791 (2024); \"Self-Preference Bias in LLM-as-a-Judge,\" arXiv:2410.21819 (2024, NeurIPS Safe Generative AI Workshop); \"Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies in LLM-as-a-Judge Pipelines,\" arXiv:2604.23178 (2026); Anthropic Engineering: Writing effective tools for AI agents (2025-09-11)"
durability: durable
prerequisites: [agent-evaluation/01]
created: 2026-08-10
updated: 2026-08-10
---

# LLM-as-Judge: Design, Calibration, and Known Biases

## TL;DR
`agent-evaluation/01` established that agent correctness needs criteria, not exact match, because there is often no single right output. LLM-as-judge is the technique of using a second model to apply those criteria at scale: it reads a task, a response (or a full trajectory), and a rubric, and outputs a verdict or score. It is far cheaper than human review and scales to thousands of evaluations, but it inherits a specific, well-documented set of biases - position bias, verbosity bias, and self-preference bias - that can silently invalidate a judge's verdicts if the judge isn't designed and calibrated to resist them.

## The idea
Once you accept that agent tasks need judgment rather than string comparison, the question becomes: whose judgment, at what cost, at what scale? Human expert review is the gold standard for quality but does not scale - a team cannot manually grade ten thousand evaluation runs after every prompt change. LLM-as-judge closes that gap by using a capable model, given an explicit rubric, to grade another model's (or agent's) output. This works well enough to be the default scoring method behind most modern agent evaluation pipelines, but "works well enough" hides an important caveat: the judge is itself an LLM, subject to the same sampling and pattern-matching behavior as the model it's grading, and it turns out to have systematic, reproducible blind spots that have nothing to do with the quality of the response it's grading. Treating a judge's verdict as ground truth without accounting for these biases reintroduces exactly the kind of silent measurement error that `agent-evaluation/02` warns about in benchmarks - except now the error is baked into your scoring mechanism itself, not just your task set.

This is where calibrating a judge is a genuine engineering discipline, not a one-line prompt. It shares the core discipline of `technical-leadership/how-to-measure-anything`: before trusting a number, you have to understand exactly what's producing it and where it can mislead you.

## How it works

### The basic judge pattern
A minimal LLM-as-judge setup has three parts: a **rubric** (explicit criteria for what counts as good - "correctness," "did not fabricate information," "used the requested tone"), the **candidate response(s)** to grade, and a **judge prompt** that asks the judge model to apply the rubric and emit a structured verdict (a score, a pass/fail, or a ranking between two candidates). The judge can operate in absolute mode (score one response against the rubric alone) or comparative mode (given two responses, say which better satisfies the rubric). Comparative judging is common in preference-style evaluation and, as the biases below show, is also where some of the sharpest failure modes live.

### Bias #1: position bias - the judge favors where an answer sits, not what it says
A 2024 large-scale study evaluated 15 LLM judges across two benchmark suites and 22 tasks, generating over 150,000 individual judgments, specifically to measure whether comparative judges are influenced by which position (first or second) a candidate response appears in within the judge's prompt. The finding: position bias is real, systematic, and not explainable by random variation - it "varies significantly across judges and tasks" and is most pronounced when the quality gap between the two candidates is small, while being only weakly related to how long each candidate's text is.

Concretely: give a judge model candidate A and candidate B of similar quality, ask "which is better, respond only with A or B," and you can flip the verdict a meaningful fraction of the time simply by swapping which slot (first or second) each candidate is placed in - without changing either response's content at all. A judge that isn't checked for this can produce an evaluation pipeline that quietly prefers "whichever variant we happen to list first" rather than "whichever variant is actually better," which is catastrophic if that judge is gating a model or prompt rollout decision.

**Mitigation:** run each comparison twice with positions swapped and require agreement (or average the two verdicts) before trusting a comparative result; report position-swap consistency as a judge-quality metric, not just raw pass rate.

### Bias #2: verbosity bias - the judge rewards length, not correctness
Judges have been documented to prefer semantically equivalent responses that are simply longer or more elaborated, independent of whether the extra length adds information. In practice this means an agent (or a prompt-tuning process) that learns "the judge scores higher when I add more caveats, more restated context, more hedging language" can game the judge without becoming more correct - and because the judge is the thing gating what "correct" means in the pipeline, this drift can go undetected for a long time. Research specifically comparing bias types has found multimodal judges to be even more susceptible to verbosity bias than to position bias, suggesting this is not a minor edge case but one of the largest sources of judge unreliability across setups.

**Mitigation:** include an explicit rubric criterion that penalizes unnecessary length or restatement, and periodically test the judge with a pair of responses that are deliberately equal in correctness but different in length, checking whether the judge still calls it a tie.

### Bias #3: self-preference bias - the judge favors its own kind of output
A 2024 study asked whether a judge model (GPT-4, in the study) systematically favors responses more similar to what it would itself produce, even when a human evaluator would not. The mechanism the researchers isolated is notable: the judge's preference correlated with the **perplexity** of the candidate text under the judge's own model - text that is more "expected" or fluent to the judge (lower perplexity) scored higher, regardless of whether it was actually generated by the judge model itself or by a different model that happens to write in a similar register. In other words, self-preference bias is not (only) "the judge recognizes and favors its own literal outputs" - it's "the judge favors text that reads like something it would have written," which means using the *same* model family as both the response-generator and the judge is a specific, avoidable source of inflated scores.

**Concrete failure mode:** if you use GPT-4 to both generate candidate agent responses in an A/B test and to judge which candidate is better, the judge has a documented tendency to score the GPT-4-family candidate higher than an equally good candidate from a different model family, purely because the GPT-4-family text is more fluent to a GPT-4 judge - inflating your measured win rate for reasons unrelated to actual quality.

**Mitigation:** use a judge from a different model family than any of the systems being evaluated when comparing across model families; when that isn't possible, treat same-family comparisons as directionally suggestive only, and validate a sample against human judgment before trusting the margin.

### Worked example: designing a judge for a support-ticket-triage agent
Suppose you're grading an agent that reads a support ticket and drafts a reply. A naive judge prompt - "here are two draft replies, which is better?" - is exposed to all three biases at once: position bias (which draft is listed first), verbosity bias (a longer, more hedge-y draft can outscore a tighter, equally correct one), and self-preference bias (if the same model drafted both candidates and also judges them). A calibrated version: (1) define an explicit rubric - factually correct, resolves the customer's actual question, matches the requested tone, no unnecessary padding; (2) run each pairwise comparison twice with positions swapped, discard or flag disagreements; (3) use a judge model from a different family than the draft-generating model; (4) periodically spot-check a sample of judge verdicts against a human reviewer to catch drift. None of this makes the judge perfect, but each step closes one specific, documented failure mode rather than trusting the raw verdict.

### Calibration is ongoing, not a one-time setup
Because judge biases are properties of the judge model itself, they can shift when you swap judge models, update the judge model's version, or change the rubric's wording. A 2026 systematic evaluation of bias-mitigation strategies across LLM-as-judge pipelines treats this explicitly as a pipeline design problem, not a solved one - comparing multiple mitigation techniques rather than presenting a single fix, which reflects that no single technique currently closes all three biases at once. Practically, this means a judge setup needs the same maintenance discipline as any other measurement instrument: periodic recalibration against human judgment, not "we validated it once and now trust it forever."

## Pros
- Scales evaluation to volumes (thousands of runs after every change) that human review cannot match at any reasonable cost or turnaround time.
- Can apply consistent, explicit rubric criteria across every evaluated response, which is more repeatable than ad hoc human review with no shared rubric.
- Improves over time as judge models improve, and can be combined with human spot-checks to catch drift cheaply rather than requiring full human re-grading.

## Cons
- Inherits documented, systematic biases (position, verbosity, self-preference) that can silently distort verdicts in ways that look like signal but are actually artifacts of the judge's own behavior.
- A judge from the same model family as the system under evaluation can inflate scores for that system specifically, biasing any cross-model comparison that isn't controlled for this.
- Judge calibration is ongoing maintenance work, not a one-time setup - rubric wording, judge model version, and mitigation techniques all need periodic revalidation against human judgment.

## Alternatives
- **Human expert review** - avoids all three documented judge biases, at the cost of not scaling past a small evaluation set and introducing its own inter-rater variance; often used specifically to *calibrate* an LLM judge rather than to replace it.
- **Multi-judge and debate-based evaluation** (`agent-evaluation/07`) - uses multiple judge models, sometimes arguing a case to each other, to reduce reliance on any single judge's biases; more expensive per evaluation, and does not eliminate biases shared across judge models trained similarly.
- **Rubric-only automated scoring (no LLM in the loop)** - programmatic checks against a rubric (keyword presence, structural checks, test-suite pass/fail) avoid judge bias entirely because there's no judge, but only work for criteria that are checkable without natural-language understanding, which excludes most open-ended quality judgments.

## When to use it
Use LLM-as-judge when you need to score open-ended, natural-language agent output at a volume human review can't sustain, and you're willing to invest in the mitigations above (position-swap testing, cross-family judge selection, periodic human calibration). It's the right default for most agent evaluation pipelines once a rubric can be written down explicitly.

## When NOT to use it
Do not use a same-family judge to compare a same-family candidate against a different model's output without accounting for self-preference bias - the comparison is contaminated by construction. Do not run single-pass comparative judging (no position swap) on close-quality candidates and treat the verdict as reliable - position bias is documented to be strongest exactly when the quality gap is small, which is precisely when you need the verdict to be trustworthy. And don't skip periodic human-calibration spot-checks on a judge that's gating a real rollout decision; an uncalibrated judge is a plausible-looking number with an unknown, possibly large, error bar.

## Key takeaways / mental model
An LLM judge is a measurement instrument, and every measurement instrument has documented sources of systematic error - for LLM judges, those are position bias (favors slot, not substance), verbosity bias (favors length, not correctness), and self-preference bias (favors text that reads like the judge's own family, via lower perplexity, regardless of actual quality). Designing a judge means engineering around each of these explicitly - swap positions, penalize padding, use a different model family, and keep validating against humans - not trusting a single verdict at face value.

## Self-check questions
1. You run a comparative judge once per pair and always list your new model's response first. Even if your new model is genuinely no better than the baseline, what would you expect to observe in the win-rate numbers, and why?
2. Explain the mechanism behind self-preference bias in your own words: is it that the judge literally recognizes its own outputs, or something else? Why does that distinction matter for choosing a judge model?
3. A rubric for grading customer-support replies includes "thoroughness" as a criterion. Why might this specific wording make the judge more susceptible to verbosity bias than a rubric that says "answers the customer's question completely, without unnecessary restatement"?
4. Your team judges every agent response with GPT-4, and your agent itself is also built on GPT-4. Design a validation step that would tell you whether self-preference bias is inflating your measured quality scores.
5. Why does position bias being "strongest when the quality gap is small" make it more dangerous, rather than less, for real evaluation pipelines?

## References
- Li et al., "Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge," arXiv:2406.07791 (2024), https://arxiv.org/abs/2406.07791
- "Self-Preference Bias in LLM-as-a-Judge," arXiv:2410.21819 (2024, NeurIPS Safe Generative AI Workshop), https://arxiv.org/abs/2410.21819
- "Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies in LLM-as-a-Judge Pipelines," arXiv:2604.23178 (2026), https://arxiv.org/pdf/2604.23178
- [Anthropic Engineering: Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (2025-09-11)
