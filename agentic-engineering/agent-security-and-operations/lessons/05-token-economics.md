---
id: agent-security-and-operations/05
subject: agent-security-and-operations
title: "Token Economics: Model Routing, Caching, and Budget Design"
slug: token-economics
status: drafted
mastery:
seniority: senior
source: "Zylos Research, AI Agent Cost Optimization: Token Economics and FinOps in Production (Feb 2026); Zylos Research, AI Agent Cost Engineering: Production Token Economics (May 2026); Correlation One, How to Manage AI Token Costs in the Enterprise: The 2026 Playbook (2026); Anthropic, Prompt caching documentation (2026, platform.claude.com); Fastio, AI Agent Token Cost Optimization: Complete Guide for 2026"
durability: durable
prerequisites: [tool-use-agentic-loop/06]
created: 2026-08-10
updated: 2026-08-10
---

# Token Economics: Model Routing, Caching, and Budget Design

## TL;DR
An agent costs meaningfully more to run than a chat interface doing the same nominal task, because a single agent turn hides a multi-step loop of planning, tool selection, execution, and verification calls that a chatbot never makes - 2026 industry data puts the multiplier at roughly 3-10x more LLM calls per completed task. Controlling that cost is an engineering discipline with concrete levers - routing each call to the cheapest model that can do that specific step correctly, caching the parts of the prompt that repeat across calls, and setting explicit budgets that fail a run rather than let it silently overrun - not a matter of hoping the vendor's per-token price keeps falling faster than usage grows.

## The idea
Least-privilege permissions (`agent-security-and-operations/03`) and human-in-the-loop gates (`agent-security-and-operations/04`) both work by constraining what an agent is allowed to *do*. Token economics constrains something orthogonal: what an agent is allowed to *cost* to do it. The two problems interact only at the margins (an over-permissioned agent can also be a wastefully expensive one, if it re-fetches things it should have cached), but they are fundamentally different failure modes - a permission failure produces a wrong or dangerous action; a cost failure produces a correct action that was needlessly, sometimes catastrophically, expensive to reach.

The reason this needs to be an explicit design discipline rather than an afterthought is that agentic workloads are structurally different from the chat interfaces most teams' cost intuitions were built on. A chat completion is one call: user message in, model response out. An agentic loop for the same nominal task might involve the model deciding what tool to call, the tool executing, the result coming back into context, the model deciding what to do next, and this repeating for several turns before a final answer - and `tool-use-agentic-loop/06`'s stateless-vs-stateful distinction means some of those calls may also be retried, each retry its own token spend. Each of those intermediate steps is a full model call with its own input and output tokens, and unlike a chat turn, the growing context (everything decided and executed so far) gets re-sent as input on every subsequent step. Cost, in other words, grows with the *length and shape of the reasoning process*, not just with the size of the final answer - which is precisely why an unmanaged agent's cost curve looks nothing like a chat product's.

## How it works

### Why agents cost more than chat, concretely
2026 industry data converges on agents making roughly 3-10x more LLM calls than a simple chatbot completing an analogous task, because a single user-facing request can trigger planning, tool selection, tool execution, result verification, and final response generation as separate model invocations. An unconstrained agent working a non-trivial software-engineering task has been reported to cost on the order of $5-8 in API fees alone for that one task - a figure with no equivalent in chat-based pricing intuition, where a single exchange rarely approaches that cost. The lever compounding this: output tokens are priced substantially higher than input tokens across major providers in 2026, with a median output-to-input cost ratio around 4:1 and some premium reasoning-tier models reaching roughly 8:1 - so an agent that reasons verbosely at every step (writing out long chain-of-thought before each tool call) pays that premium repeatedly across the whole loop, not once.

**Worked example.** A five-step agentic task (plan, three tool calls with verification, final synthesis) where each step sends roughly 2,000 input tokens (accumulated context) and generates 300 output tokens, using illustrative Aug-2026 round pricing of $3 per million input tokens and $15 per million output tokens (a 5:1 ratio, representative of a mid-tier model - see `landscape-snapshot/05` for actual current vendor numbers):

```
Step    Input tokens   Output tokens   Input cost   Output cost   Step cost
----------------------------------------------------------------------------
1 Plan       500             150        $0.0015       $0.00225    $0.00375
2 Tool 1    1,200            250        $0.0036       $0.00375    $0.00735
3 Tool 2    2,000            250        $0.0060       $0.00375    $0.00975
4 Tool 3    2,800            250        $0.0084       $0.00375    $0.01215
5 Synthesis 3,600            400        $0.0108       $0.00600    $0.01680
----------------------------------------------------------------------------
Total                                                              $0.0498
```
Five steps, under a nickel - but notice input tokens more than 7x from step 1 to step 5, because each step re-sends the accumulated context of everything decided so far. Scale this to a fifty-step agent working a complex, multi-file coding task, and both the step count and the per-step context size grow, which is exactly how a single task lands in the multi-dollar range reported industry-wide.

### Lever 1: model routing by task complexity
Not every step in an agentic loop needs the most capable (and most expensive) model available. Routing sends each call to the cheapest model class that can reliably perform that specific step, reserving the frontier model for the steps that actually need its reasoning depth. 2026 practitioner data frames this as the single highest-leverage lever available: a task routed to a frontier reasoning model can cost on the order of 190x more than the same task handled by an appropriately sized smaller model, when the smaller model would have produced an equally correct result.

**Worked example.** An agent's loop has three call types: (a) classifying which tool to call next given a short menu of options - a narrow, well-defined decision; (b) synthesizing a final user-facing answer from gathered results - requires nuanced language and judgment; (c) an occasional escalation step where the agent must reconcile genuinely conflicting tool results - requires real reasoning. Routing (a) to a small, fast model, (b) to a mid-tier model, and reserving a frontier reasoning model for (c) alone can cut the loop's blended cost sharply versus running every step on the frontier model - while the accuracy cost is close to zero for (a), since tool selection from a short menu is exactly the kind of narrow task smaller models handle reliably. The judgment call is verifying, per call type, that the cheaper model's error rate on that specific narrow task doesn't erase the savings by causing costly retries or wrong tool calls downstream.

### Lever 2: prompt and response caching
Much of what gets re-sent as "input tokens" on every step of an agentic loop is identical or near-identical to what was sent on the previous step - the system prompt, tool definitions, and the stable prefix of the accumulated context. Caching lets the provider store that stable prefix once and charge a steep discount for reusing it on subsequent calls, rather than re-billing the full input price every time. As of 2026, a cache hit on Anthropic's API costs roughly 10% of the standard input token price; writing to the cache costs a premium (about 1.25x standard input price for a 5-minute cache, about 2x for a longer-lived 1-hour cache), meaning caching pays for itself after as little as one cache read for a short-lived cache or two reads for a longer one. Practitioner reporting puts realistic savings from correctly configured caching at 50-90% of token spend on the cached portion, and combining caching with model routing is reported to deliver 70-85% total cost reduction from an unoptimized baseline within a single engineering sprint.

**Worked example, extending the five-step loop above.** If the system prompt and tool definitions (a stable 1,500-token prefix present in every one of the five steps' input) are cached after step 1's cache write, steps 2-5 pay roughly 10% of standard input price on that 1,500-token portion instead of full price, while only the genuinely new context (the growing conversation tail) is billed at full input price. On the numbers above, this can turn a large share of the $0.033 total input cost into a small fraction of that - the exact savings depend on how much of each step's input is the stable, cacheable prefix versus newly accumulated context, which is precisely why cache design (what goes in the stable prefix, what varies per call) is itself an engineering decision, not something that happens automatically.

### Lever 3: explicit budget design
Routing and caching reduce cost per task; budget design bounds the cost of a task that goes wrong. An agent stuck in a reasoning loop, retrying a failing tool call repeatedly, or pursuing an unexpectedly long investigative path will keep consuming tokens until something stops it - and "something stops it" needs to be an explicit, enforced limit, not an assumption that the agent will naturally converge. The common levers are a hard cap on total tokens or dollar spend per run (the harness aborts and surfaces the partial result once the cap is hit), a cap on loop iterations or tool calls independent of token count (catching a cheap-but-infinite loop that a dollar cap alone wouldn't catch quickly), and per-task or per-user rate limits that bound how many expensive runs can execute in a given window.

**Worked example.** A support-triage agent budgeted at $0.15 per ticket (chosen because the support team's cost-per-ticket target for human agents is roughly $2, leaving comfortable headroom) hits a malformed ticket that causes it to loop between two tool calls without making progress. Without a budget cap, this run could run indefinitely, consuming tokens (and, if the loop includes a paid third-party API tool call, external cost too) until a person notices. With a hard cap enforced at $0.15 or 15 tool calls (whichever comes first, per the two-level design above), the harness aborts the run, logs the malformed-ticket case for human review, and the blast radius of the failure is bounded to a known, small, budgeted amount rather than an open-ended one - and it does so independently of whether the underlying issue is a token-cost runaway or a cheap-but-infinite loop, which is why both a dollar cap and an iteration cap are worth setting rather than relying on either alone.

### The enterprise-reality check: falling prices, rising spend
It is tempting to treat token economics as a problem that solves itself as vendor prices fall - and per-token prices genuinely have fallen sharply, roughly 67% year-over-year by 2026 industry estimates. But 73% of enterprises reportedly exceeded their original AI cost projections in the most recent fiscal year despite that price decline, because absolute spend is driven by usage volume, and agentic workloads consume orders of magnitude more tokens per completed task than the conversational interfaces most initial budget estimates were built on. The practical implication: budget planning for agent deployments has to model usage growth and the agent-specific call multiplier explicitly, not extrapolate from a chat product's historical token spend - a mistake that shows up as a budget overrun months later rather than as an immediate, catchable error.

## Pros
- Model routing and caching are largely mechanical, sprint-sized engineering work (not a research problem) that 2026 data reports delivering 70-85% cost reduction combined, on an unoptimized baseline - a high-leverage, low-risk starting point.
- Explicit budget caps convert an open-ended cost failure mode (a stuck agent burning tokens indefinitely) into a bounded, known-worst-case one, the same way a circuit breaker bounds a cascading system failure.
- Cost telemetry, once instrumented, becomes a debugging signal in its own right - a step or task whose cost spikes unexpectedly is often also the step where something is going functionally wrong (excess retries, runaway context growth), so cost observability and correctness observability reinforce each other (see `agent-security-and-operations/06`).

## Cons
- Routing to a cheaper model for a step that actually needed more capability trades a visible cost saving for an invisible accuracy loss that may not surface until it causes a costly downstream retry or a wrong final action - the savings have to be verified against task-specific accuracy, not assumed.
- Caching only pays off for genuinely stable, reused prefixes; caching content that changes on every call (or expires before it's reused) pays the cache-write premium without ever recovering it in cheap reads.
- A hard budget cap that aborts mid-task can leave a task in a half-completed, inconsistent state if the abort isn't paired with the same rollback/idempotency discipline covered for tool retries (`tool-use-agentic-loop/06`) - bounding cost is not the same as bounding damage from an incomplete action.
- Optimizing for lowest cost per call can conflict with latency or reliability goals (a cheaper model might have higher variance or slower failover), so cost is one axis in a multi-objective trade-off, not the only one.

## Alternatives
- **Flat-rate or subscription pricing instead of per-token metering** - some deployments negotiate fixed-cost access rather than metered token billing, trading the ability to optimize per-call cost for budget predictability; appropriate when usage volume is stable and predictable enough that the metering discipline in this lesson would add engineering overhead without much payoff.
- **Batch processing for non-latency-sensitive work** - providers commonly offer a substantial discount (roughly 50% as of 2026) for asynchronous batch API calls versus real-time calls; the right lever specifically when the task does not need an immediate response, which most human-in-the-loop-gated approval workflows (`agent-security-and-operations/04`) and many background agent tasks genuinely don't.
- **Reducing call count through better task decomposition, not just cheaper calls** - sometimes the highest-leverage fix isn't routing or caching an existing five-step loop but redesigning it to need three steps instead, addressing the root multiplier (`tool-use-agentic-loop/06`'s cost of over-fine-grained tool decomposition) rather than making each of the five steps cheaper.

## When to use it
Apply model routing wherever an agentic loop has call types with genuinely different reasoning demands - narrow classification or selection steps almost always tolerate a cheaper model; apply caching wherever a stable prefix (system prompt, tool definitions, retrieved reference material) repeats across multiple calls in the same session; set explicit budget caps on every production agent run, without exception, since the downside of a missing cap (an unbounded runaway) is asymmetric with the cost of adding one.

## When NOT to use it
Do not route a step to a cheaper model without measuring that step's task-specific accuracy on the cheaper model first - the 190x cost multiplier for frontier models is only a saving if the cheaper model actually gets that specific call right at an acceptable rate; a cheap model that causes retries or wrong actions can cost more overall than the frontier model would have. Do not cache content that changes on nearly every call (defeats the mechanism) or that contains anything session-specific which shouldn't leak across cached contexts. And do not treat a budget cap as a substitute for fixing the underlying loop or retry logic that's causing runaway cost in the first place - the cap bounds the damage of a given failure, it does not diagnose or fix it.

## Key takeaways / mental model
An agent's cost is a function of how many model calls its loop makes, how much accumulated context each call re-sends, and which model tier each call runs on - not a single per-request price the way chat cost intuition suggests. Attack all three axes deliberately: route each call to the cheapest model that reliably handles that specific step, cache the stable, repeated portion of context rather than re-billing it every step, and cap total spend per run so a stuck or runaway agent fails cheap and loud instead of expensive and silent. Falling per-token prices do not make this discipline optional - rising usage volume from agentic workloads outpaces the price decline for most organizations, which is exactly why 2026 data shows most enterprises overshooting their AI cost projections despite cheaper tokens.

## Self-check questions
1. Explain, using the five-step worked example, why an agentic loop's input-token cost grows faster than its output-token cost as the loop progresses, and what that implies about where caching has the most leverage.
2. A teammate proposes routing every call in an agent's loop to the cheapest available model "to save money." What is the missing verification step before that change is safe to ship, and what failure mode does skipping it risk?
3. Your team has correctly implemented prompt caching but is seeing minimal savings. List two concrete reasons the cache might not be paying off, referencing how cache pricing works.
4. Design a two-level budget cap (dollar cap and iteration cap) for a research agent that investigates open customer complaints, and justify why one cap alone would be insufficient using a specific failure scenario.
5. Why did 73% of enterprises reportedly exceed their AI cost projections in the most recent fiscal year despite token prices falling roughly 67% year-over-year? Answer in terms of what changed on the usage side, not the price side.
6. A budget cap aborts an agent mid-task after it has already completed two of five planned write operations. What does this lesson say is the risk here, and which other lesson's discipline does the fix depend on?

## References
- [Zylos Research, AI Agent Cost Optimization: Token Economics and FinOps in Production (Feb 2026)](https://zylos.ai/research/2026-02-19-ai-agent-cost-optimization-token-economics/)
- [Zylos Research, AI Agent Cost Engineering: Production Token Economics (May 2026)](https://zylos.ai/research/2026-05-02-ai-agent-cost-engineering-token-economics/)
- [Correlation One, How to Manage AI Token Costs in the Enterprise: The 2026 Playbook](https://www.correlation-one.com/blog/how-to-manage-ai-token-costs-in-the-enterprise-the-2026-playbook)
- [Anthropic, Prompt caching documentation](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Fastio, AI Agent Token Cost Optimization: Complete Guide for 2026](https://fast.io/resources/ai-agent-token-cost-optimization/)
