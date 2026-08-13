---
id: landscape-snapshot/05
subject: landscape-snapshot
title: Model Capability Tiers and Pricing Today
slug: model-capability-tiers-and-pricing-today
status: drafted
mastery:
seniority: mid
source: "Anthropic, Claude API pricing documentation (accessed August 2026, platform.claude.com/docs/en/about-claude/pricing); OpenAI, Developer API pricing documentation (accessed August 2026, developers.openai.com/api/docs/pricing); OpenAI, GPT-5.6 launch and Terra/Luna price-drop announcements (July 2026, openai.com/index/gpt-5-6 and OpenAI Developer Community, July 30 2026); Google, Gemini Developer API pricing documentation (accessed August 2026, ai.google.dev/gemini-api/docs/pricing); CloudZero, Gemini pricing in 2026 (2026); FelloAI, Gemini Pricing 2026 (2026)"
durability: perishable
next_review: 2026-11
prerequisites: [agent-security-and-operations/05]
created: 2026-08-10
updated: 2026-08-10
---

# Model Capability Tiers and Pricing Today

## TL;DR
As of August 2026, the three major frontier-model providers each sell three-ish capability tiers at roughly comparable price bands: a flagship reasoning tier (Claude Opus 5, GPT-5.6 Sol, Gemini 3.1 Pro) around $2-5 input / $12-30 output per million tokens, a balanced mid-tier (Claude Sonnet 5, GPT-5.6 Terra, Gemini 3.6 Flash) around $1.50-2 input / $7.50-12 output, and a budget tier (Claude Haiku 4.5, GPT-5.6 Luna, Gemini 3.5 Flash-Lite) around $0.20-1 input / $1.20-5 output. `agent-security-and-operations/05` teaches the durable discipline (routing, caching, budgets) that makes these tiers useful; this lesson supplies the concrete numbers that discipline is applied to right now.

> **Snapshot date: August 2026.** This lesson is tagged `durability: perishable` and reviewed quarterly (`next_review: 2026-11`) - treat every specific product name, version, and number below as accurate as of the date above, not as a permanent fact. See `agent-docs/fast-moving-domain-policy.md`.

## The idea
`agent-security-and-operations/05` establishes that an agent's cost is driven by call count, context size, and model tier - and that routing each call to the cheapest tier that can reliably do the job is the single highest-leverage cost lever available. That lesson deliberately used illustrative round numbers ($3/$15 per million tokens) rather than real vendor prices, precisely so it would stay true regardless of what any vendor charges this month. This lesson is the other half of that deal: it names the real tiers, the real prices, and the real trade-offs among them, on the explicit understanding that it will need re-verifying every quarter.

Why three tiers, consistently, across three unrelated companies? Not coincidence - it reflects a shared engineering reality. Serving a frontier-scale model costs meaningfully more per token than serving a smaller, faster model, and the majority of real agentic workloads are dominated by narrow, repetitive sub-tasks (classify this, extract that, pick a tool) that a small model handles just as correctly as a large one, for a fraction of the cost. Every major provider has converged on offering a flagship model for the minority of calls that genuinely need deep reasoning, a mid-tier model that is the default choice for most production work, and a budget model priced low enough that routing high-volume narrow calls to it is close to free. Naming the three tiers by capability role, rather than by any single vendor's brand name, is what lets this lesson generalize across providers even as the specific model names inside each tier change release to release.

## How it works

### The three tiers, compared

| Tier | Anthropic (Aug 2026) | OpenAI (Aug 2026) | Google (Aug 2026) | Typical use case |
| --- | --- | --- | --- | --- |
| Flagship / reasoning | Claude Opus 5 - $5 / $25 per MTok | GPT-5.6 Sol - $5 / $30 per MTok | Gemini 3.1 Pro - $2 / $12 per MTok (up to 200k context; $4 / $18 above 200k) | Multi-step agentic coding, ambiguous reasoning, reconciling conflicting tool results, tasks where a wrong answer is expensive |
| Balanced / mid-tier | Claude Sonnet 5 - $2 / $10 per MTok | GPT-5.6 Terra - $2 / $12 per MTok | Gemini 3.6 Flash - $1.50 / $7.50 per MTok | The default choice for most production agent work: tool orchestration, synthesis, everyday coding and writing tasks |
| Budget / high-volume | Claude Haiku 4.5 - $1 / $5 per MTok | GPT-5.6 Luna - $0.20 / $1.20 per MTok | Gemini 3.5 Flash-Lite - $0.30 / $2.50 per MTok | Narrow classification, tool-selection, summarization, and other high-volume steps in an agentic loop where accuracy needs are modest |

(Prices are USD per million tokens, input / output, standard non-batch, non-cached rates. See References for the exact pages these were read from.)

**Reading the table like an engineer, not a shopper.** The columns are not directly substitutable line items - each vendor's tokenizer counts tokens differently (Anthropic's Claude 4.7-and-later models, for instance, use a newer tokenizer that produces roughly 30% more tokens for the same text than the previous one), so a lower headline per-token price does not automatically mean a lower per-task price. `agent-security-and-operations/05`'s worked example - a five-step agentic loop costing under a nickel - is the right unit of comparison: benchmark actual tasks end to end on the actual tokenizer, not headline rates in isolation.

### Cost-reduction levers that apply on top of the table
Every provider in the table offers at least two of the same three discounts `agent-security-and-operations/05` names generically:
- **Prompt caching.** Anthropic's cache-hit rate is 0.1x the base input price (a 5-minute cache write costs 1.25x base input; a 1-hour write costs 2x), meaning caching pays for itself after one read on a short cache or two reads on a long one. Google's Gemini API offers context caching in a comparable range ($0.03-$2.00 per million tokens depending on tier and duration). This is the real-world instance of the caching lever `agent-security-and-operations/05` teaches in the abstract.
- **Batch processing.** Anthropic's Batch API discounts both input and output tokens by 50% versus standard rates (e.g., Claude Sonnet 5 drops from $2/$10 to $1/$5 per MTok in batch mode). OpenAI's GPT-5.6 tiers carry the same 50% batch discount (GPT-5.6 Sol: $2.50/$15 batch vs. $5/$30 standard). Google offers an equivalent batch discount. None of this is free - batch mode trades immediacy for price, which is exactly the trade-off `agent-security-and-operations/05`'s "Alternatives" section names.
- **Fast mode / premium latency, the inverse lever.** Anthropic's Fast mode for Claude Opus 5 (research preview as of August 2026) doubles standard pricing to $10/$50 per MTok in exchange for significantly faster output - a reminder that the tier table has a even-more-expensive edge for teams optimizing for latency over cost, not just a cheaper edge for teams optimizing the other way.

### A worked comparison: routing a five-step loop today
Take `agent-security-and-operations/05`'s five-step worked example (a plan step, three tool-call-plus-verification steps, and a final synthesis step) and route it against real August 2026 pricing instead of illustrative numbers. Routing the narrow tool-selection steps to a budget-tier model (Claude Haiku 4.5 or GPT-5.6 Luna) and reserving the flagship tier only for the final synthesis step, versus running every step on the flagship tier, reproduces the same order-of-magnitude gap that lesson teaches abstractly: at Anthropic's current rates, Haiku 4.5 input tokens cost one-fifth of Opus 5's, and output tokens cost one-fifth as well, so a loop that routes correctly can land far below a loop that defaults every call to the flagship model - while the accuracy cost for a narrow tool-selection step routed to the budget tier is typically close to zero, per `agent-security-and-operations/05`'s Lever 1.

### What changed since the last plausible snapshot, as an illustration of the churn itself
This lesson's own research turned up a live example of why the `next_review` cadence exists: OpenAI's GPT-5.6 family launched with Terra at $2.50/$15 and Luna at $1/$6 per MTok, then cut Terra's price by 20% and Luna's by 80% on July 30, 2026 - three weeks before this lesson's snapshot date. A source dated earlier that same month (referencing an OpenAI "GPT-5.5" family with different tier names entirely) was already stale by the time this lesson was written. That is not a research failure on this lesson's part - it is the expected shape of this domain, and exactly why every claim above carries a snapshot date rather than being asserted as a fact.

## Pros
- A three-tier structure that is now stable across all three major providers makes cross-vendor cost comparison tractable - the routing discipline from `agent-security-and-operations/05` translates directly, regardless of which provider a team standardizes on.
- Budget-tier pricing has fallen sharply and consistently (Luna's 80% July 2026 cut is one instance of a broader trend); routing narrow, high-volume steps to the cheapest tier is now cheap enough that the main blocker is often engineering time to implement routing, not the tier's price itself.
- Every provider's documentation is a live, authoritative primary source (see References) - unlike many perishable facts, this specific one has a canonical place to re-check it that does not require guessing which secondary source to trust.

## Cons
- Tier names and exact prices change on a timescale of weeks, not quarters (see the GPT-5.6 Terra/Luna cut above) - any number in this lesson older than a few months should be treated as probably wrong until re-verified, which is exactly what `next_review: 2026-11` exists to force.
- Headline per-token prices are not directly comparable across vendors because tokenizers differ (Anthropic's 4.7+ tokenizer alone produces ~30% more tokens for equivalent text than its predecessor) - a naive price-per-token comparison can favor the wrong vendor for a given real workload.
- Long-context pricing is a second, easy-to-miss axis: Gemini 3.1 Pro's price doubles above a 200k-token context threshold, a step-function most flat per-token comparisons omit entirely.

## Alternatives
- **Open-weight models self-hosted on owned or rented GPU infrastructure** - trades per-token vendor pricing for fixed infrastructure cost and operational ownership; the right call specifically when volume is high and predictable enough that the crossover point favors owning the hardware, which the token-economics discipline in `agent-security-and-operations/05` can help estimate but this lesson does not itself size.
- **Third-party model routers and gateways** that automatically select a tier per call based on observed accuracy - operationalizes the routing lever from `agent-security-and-operations/05` without hand-writing routing logic, at the cost of an added dependency and another vendor relationship to track.
- **Enterprise/negotiated pricing** - all three providers in the table offer volume discounts or custom terms above the standard published rates; relevant once usage is large enough that sales engagement is worth the overhead, and a reason the published per-token numbers in this lesson are an upper bound for high-volume teams, not a floor.

## When to use it
Use this table as a starting point when choosing which tier to route a given call type to, or when sizing a budget cap per `agent-security-and-operations/05`'s Lever 3 - but re-verify the exact numbers against the primary pricing pages in References before committing to a number in a cost model, since even a few weeks' staleness has already been shown (in this lesson's own research) to be enough to make a number wrong.

## When NOT to use it
Do not cite a specific price from this lesson in a document with a shelf life longer than this lesson's own `next_review` date without re-checking it first - that turns a deliberately perishable snapshot into an accidentally-load-bearing fact. Do not use this lesson to make an architectural or durable engineering decision (e.g., "always use three tiers") - that decision belongs to `agent-security-and-operations/05`, which states the tier-routing pattern in a form that survives this lesson going stale.

## Key takeaways / mental model
Three tiers - flagship, balanced, budget - each roughly aligned across Anthropic, OpenAI, and Google as of August 2026, at price ratios of roughly 5-25x between the cheapest and most expensive tier per provider. The pattern (three tiers, route by task complexity) is durable and belongs to `agent-security-and-operations/05`; the specific names and numbers in this table are not durable and belong here, with an explicit expiration date. When in doubt about whether a number in this lesson is still current, the answer is: check the primary source in References, don't trust memory - including this lesson's own memory of itself past its `next_review` date.

## Self-check questions
1. Without looking at the table, name the three capability tiers this lesson identifies and one representative model from each of the three providers as of the snapshot date.
2. A colleague wants to compare Claude Sonnet 5's $2/$10 per-MTok price directly against Gemini 3.6 Flash's $1.50/$7.50 to decide which is cheaper for a specific workload. What does this lesson say is missing from that comparison, and why can it change the answer?
3. Explain, using the OpenAI GPT-5.6 Terra/Luna price cut described in this lesson, why `next_review: 2026-11` is set to three months out rather than, say, one year.
4. A production agent's loop has a narrow tool-selection step and a final synthesis step. Using this lesson's tier table, propose a routing assignment for August 2026 pricing, and justify it using the lever from `agent-security-and-operations/05` this lesson operationalizes.
5. What is the practical difference between this lesson's `durability: perishable` tag and `agent-security-and-operations/05`'s `durability: durable` tag, given that both lessons discuss cost?

## References
- [Anthropic, Claude API pricing documentation](https://platform.claude.com/docs/en/about-claude/pricing) (accessed August 2026)
- [OpenAI, Developer API pricing documentation](https://developers.openai.com/api/docs/pricing) (accessed August 2026)
- [OpenAI, Previewing GPT-5.6 Sol](https://openai.com/index/previewing-gpt-5-6-sol/) and [GPT-5.6 launch announcement](https://openai.com/index/gpt-5-6/)
- [OpenAI Developer Community, Announcing a major price drop for 5.6 Terra and Luna and Fast mode for 5.6-Sol](https://community.openai.com/t/announcing-a-major-price-drop-for-5-6-terra-and-luna-and-fast-mode-for-5-6-sol/1388484) (July 30, 2026)
- [Google, Gemini Developer API pricing documentation](https://ai.google.dev/gemini-api/docs/pricing) (accessed August 2026)
- [CloudZero, Gemini pricing in 2026](https://www.cloudzero.com/blog/gemini-pricing/) (2026, for Gemini 3.1 Pro tiered context pricing not yet reflected on the primary pricing page at fetch time)
- `agent-security-and-operations/05` Token Economics, for the durable routing/caching/budget discipline this lesson supplies current numbers for.
