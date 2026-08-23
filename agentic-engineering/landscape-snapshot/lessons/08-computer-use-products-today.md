---
id: landscape-snapshot/08
subject: landscape-snapshot
title: Computer Use Products Today
slug: computer-use-products-today
status: drafted
mastery:
seniority: mid
source: "Anthropic Platform docs: Computer use tool and Browser use tool (accessed Aug 2026); Google AI for Developers: Computer use, Gemini API (accessed Aug 2026); OpenAI, Introducing Operator (2025) and Platform docs: Pricing, computer-use-preview (accessed Aug 2026); Presenc AI, OpenAI Operator Update Tracker: From Operator to ChatGPT Agent (2026) (2026); browser-use/browser-use GitHub repository and GitHub Stars Leaderboard (2026); browserbase/stagehand GitHub repository and Browserbase, Stagehand (accessed Aug 2026); Skyvern-AI/skyvern GitHub repository and skyvern.com (accessed Aug 2026)"
durability: perishable
next_review: 2026-11
prerequisites: [tool-use-agentic-loop/09]
created: 2026-08-13
updated: 2026-08-13
---

# Computer Use Products Today

## TL;DR
`tool-use-agentic-loop/09` teaches computer use as a durable tool modality - screen-based perception paired with synthesized clicks/keystrokes, and grounding as its defining hard problem. As of August 2026, all three frontier labs ship it: Anthropic's Computer Use tool (pure screenshot/pixel, plus a separate Browser Use tool that grounds on the accessibility tree first), OpenAI's ChatGPT Agent mode (the consumer-facing successor to the retired Operator, backed by a developer-facing `computer-use-preview` model), and Google's Gemini computer-use capability now built into Gemini 3.5/3.7 Flash. Alongside them, three open-source frameworks - Browser Use, Stagehand, and Skyvern - let you build the same loop yourself against any model. Every product, price, and status below is dated; see `next_review`.

> **Snapshot date: August 2026.** This lesson is tagged `durability: perishable` and reviewed quarterly (`next_review: 2026-11`) - treat every specific product name, version, and number below as accurate as of the date above, not as a permanent fact. See `agent-docs/fast-moving-domain-policy.md`.

## The idea
`tool-use-agentic-loop/09` deliberately avoided naming any product so its account of grounding, perception strategies, and failure modes stays true no matter which vendor's offering wins any given quarter. This lesson is the paired, disposable half: it names who currently ships computer use, on what models, at what price, and with which grounding strategy, so a reader deciding what to actually build against today has something concrete to evaluate.

The market as of August 2026 has a consistent shape across vendors: a first-party computer-use capability bundled into (or layered on top of) the vendor's flagship consumer product, a separate developer-facing API/tool for building custom agents, and - because computer use is comparatively easy to reimplement against any capable vision-language model - a healthy open-source layer that lets you swap in whichever model you prefer rather than being locked to one vendor's harness. All three labs currently also label some or all of their offering "preview," a signal worth taking literally given the failure modes `tool-use-agentic-loop/09` documents.

## How it works

### Anthropic: Computer Use tool and Browser Use tool
Anthropic ships two distinct tools rather than one, reflecting the two grounding strategies covered in `tool-use-agentic-loop/09`:
- **Computer Use tool** - pure screenshot/pixel grounding across a whole desktop: `screenshot`, `zoom`, click/drag variants, `scroll`, `type`, `key`, and `wait`, executed against a containerized environment you provide. Coordinates are in screenshot-pixel space with origin top-left; the calling application is responsible for scaling coordinates back up if the screenshot was downscaled to fit model image limits. Supported on Claude Opus 5, Sonnet 5, and several other current-generation models, available via the Claude API, AWS/Bedrock (beta), Google Cloud (beta), and Microsoft Foundry (beta). Reached general availability on claude.ai in March 2026. Screenshots run roughly 1,000-1,800 input tokens each; there is no separate computer-use surcharge beyond standard per-model token pricing (Claude Sonnet 5 at $2/$10 per million input/output tokens, Opus 5 at $5/$25 - see `landscape-snapshot/05`).
- **Browser Use tool** - reads the accessibility tree (elements, forms, tabs) first and grounds actions on stable element references (e.g., clicking `ref_4` rather than a coordinate), falling back to raw viewport coordinates only for canvas-like content with no structural representation. Scoped to in-page/browser tasks rather than whole-desktop automation. Anthropic's own documentation frames the choice explicitly: browser use for tasks that stay inside a webpage and benefit from stable references, computer use for anything spanning native desktop applications.
- Both tools include automatic prompt-injection classifiers that flag suspicious screenshots for user confirmation, addressing the on-screen-injection risk from `tool-use-agentic-loop/09`.

### OpenAI: ChatGPT Agent (consumer) and computer-use-preview (developer)
OpenAI's browser-control product has changed shape twice since its 2025 launch as a standalone product called Operator. The standalone Operator surface was shut down on August 31, 2025, and its capabilities were absorbed into ChatGPT itself as "agent mode" - selectable from the composer on paid ChatGPT plans starting at Plus ($20/mo), rather than requiring the $200/mo Pro tier Operator originally launched on. For developers building custom agents rather than using ChatGPT directly, the underlying vision-grounded model is exposed through the OpenAI Agents SDK as `computer-use-preview`, priced separately from OpenAI's general chat-model tiers at $3/million input tokens and $12/million output tokens (Batch API gives a 50% discount). ChatGPT Agent requires human confirmation before sensitive actions such as payments and form submissions with real-world consequences.

### Google: Gemini computer use, now built into the flagship Flash line
Google's computer-use tool moved in 2026 from a standalone preview model into a built-in capability of its main consumer-facing models: Gemini 3.5 Flash and the newer 3.7 Flash (recommended as of this snapshot) both support it natively, alongside 3.5 Flash-Lite and a legacy 2.5 preview model, so no separate model swap is required to use it. It targets three environments - browser, Android-optimized mobile, and desktop OS-level cursor control - and uses normalized 0-1000 coordinates that the caller must rescale to the real viewport, a different convention from Anthropic's raw-pixel coordinates (see `tool-use-agentic-loop/09` for why this convention detail is the swappable part, not the durable one). Gemini 3.x actions carry an `intent` field explaining the model's reasoning per step, and the platform supports configurable safety policies plus a `require_confirmation` decision the caller must honor before proceeding. Google's own documentation still labels Computer Use a "Preview" capability as of this snapshot and explicitly recommends against using it for critical decisions, sensitive data, or hard-to-reverse actions. No dedicated computer-use price premium was found in current documentation; it appears billed at the hosting model's standard per-token rate (Gemini 3.5 Flash: roughly $1.50 input / $9 output per million tokens per one pricing aggregator - see the flag below on this figure).

### Open source: Browser Use, Stagehand, Skyvern
Three open-source frameworks let you assemble the same perception-action loop against any model you choose, rather than a single vendor's fixed harness:
- **Browser Use** - a Python-first framework where the model drives the browser step by step from a natural-language goal; reported at roughly 100,000 GitHub stars by mid-2026 (exact counts vary by source and month - see the flag below), with a cited 89.1% success rate on the WebVoyager benchmark.
- **Stagehand** (Browserbase) - a hybrid framework exposing four primitives (`act`, `extract`, `observe`, `agent`) so a developer writes the deterministic parts of an automation in code and hands only the ambiguous parts to the model, rather than letting the model drive the entire flow. Stagehand v3, released February 2026, is a full rewrite communicating directly with the browser over the Chrome DevTools Protocol.
- **Skyvern** (AGPL-3.0) - combines computer vision and LLM reasoning instead of hard-coded selectors specifically to stay robust to site redesigns, and is positioned as the strongest of the three on "write"-heavy tasks - logging in (including 2FA/TOTP flows), filling forms, downloading files - reporting 85.85% on WebVoyager. The core engine is free to self-host against any LLM provider (OpenAI, Anthropic, Gemini, or a local Ollama model); a managed cloud tier adds CAPTCHA solving, proxies, and compliance features across Free, Hobby ($29/mo), Pro ($149/mo), and custom Enterprise plans.

### Comparison table

| Product | Grounding strategy | Access / entry cost (Aug 2026) | Status | Standout feature |
| --- | --- | --- | --- | --- |
| Claude Computer Use (Anthropic) | Pixel/screenshot, whole desktop | Standard Claude token pricing (Sonnet 5 $2/$10 per MTok); API/Bedrock/GCP/Foundry | GA on claude.ai since March 2026 | Paired sibling Browser Use tool for accessibility-tree grounding |
| Claude Browser Use (Anthropic) | Accessibility tree + pixel fallback | Same as above | GA-adjacent, browser-scoped | Stable element references survive layout reflows |
| ChatGPT Agent / computer-use-preview (OpenAI) | Pixel/screenshot, browser-focused | ChatGPT Plus $20/mo (consumer); API $3/$12 per MTok (developer) | Operator retired Aug 2025, folded into ChatGPT Agent | Human-confirmation gate before sensitive actions |
| Gemini computer use (Google) | Normalized 0-1000 pixel coordinates | Built into Gemini 3.5/3.7 Flash at standard rates | Labeled Preview | Native to browser, mobile, and desktop environments in one API |
| Browser Use (open source) | Pixel + DOM, model-agnostic | Free, self-hosted; bring your own model | Actively developed | ~100K GitHub stars; strong goal-driven autonomy |
| Stagehand (Browserbase, open source) | Hybrid code + AI primitives | Free, self-hosted; bring your own model | v3 shipped Feb 2026 | Deterministic flow control with AI only where needed |
| Skyvern (open source, AGPL-3.0) | Computer vision + LLM, model-agnostic | Free self-hosted; managed cloud from $29/mo | Actively developed | Best-in-class on write-heavy tasks (logins, forms, 2FA) |

**Flagged discrepancies:** sources disagree on Browser Use's exact GitHub star count within 2026 (reports range from roughly 78,000 in February to 86,000 in April to over 100,000 by June/July), consistent with genuinely fast, ongoing growth rather than a data error - treat the count as "tens of thousands and climbing," not a fixed number. Gemini's per-token computer-use pricing was not found stated as a distinct line item in Google's own documentation; the $1.50/$9 per-million-token figure cited above comes from a third-party pricing aggregator for the underlying Gemini 3.5 Flash model, not an official computer-use-specific price - verify against `ai.google.dev` pricing pages directly before relying on it.

## Pros
- All three frontier labs now ship computer use as a documented, generally-or-near-generally-available product rather than a research demo, and every one of them pairs it with an explicit human-confirmation gate for consequential actions - the safety framing from `tool-use-agentic-loop/09` is showing up in shipped products, not just papers.
- The open-source layer (Browser Use, Stagehand, Skyvern) means the grounding strategy and the underlying model are decoupled from any single vendor's harness - you can point any of the three at Anthropic, OpenAI, Google, or a local model.
- Real differentiation exists between products on grounding strategy specifically (pure pixel vs. hybrid structural), so `tool-use-agentic-loop/09`'s durable distinction is directly usable to choose a product rather than being purely academic.

## Cons
- Google's offering is still explicitly labeled "Preview" as of this snapshot, and OpenAI's underlying model carries "-preview" in its own name - both vendors are telling you directly not to treat this as production-hardened yet.
- Pricing is not apples-to-apples: Anthropic bills computer use at standard model token rates with no surcharge, OpenAI prices its developer-facing computer-use model separately from its chat models, and Google's computer-use-specific pricing could not be confirmed from primary sources in this pass - see the flagged discrepancy above.
- Company and product names have already shifted once within the last year (Operator to ChatGPT Agent), and the open-source landscape is growing fast enough that a specific star count or benchmark score is stale within weeks, not months.

## Alternatives
- **`tool-use-agentic-loop/09`'s durable modality framework alone, with no product chosen yet** — preferable when you need to reason about whether computer use is the right modality for a task at all before committing to a vendor; that lesson stays correct after every name below has changed.
- **Structured function calling against a real API** (`tool-use-agentic-loop/01`, `02`) — still the right default whenever the target system has one; nothing in this lesson's product list changes that recommendation.
- **A self-hosted open-source stack instead of any vendor's first-party product** — preferable for teams wanting model choice, on-prem deployment, or workflows none of the first-party offerings fit, at the cost of building and maintaining the harness yourself (mitigated by Browser Use, Stagehand, or Skyvern rather than writing one from scratch).

## When to use it
Use this lesson when you need a concrete, current shortlist - "which computer-use product should I trial this quarter," "does Anthropic's or Google's coordinate convention match what I'm already scaling for," "is Skyvern's login-handling strong enough to skip building that myself." Pair it with `tool-use-agentic-loop/09` to first confirm the task actually needs this modality (no API exists) before picking a specific product.

## When NOT to use it
Do not treat any status, price, or benchmark figure here as still true without checking `next_review` and the vendor's own current documentation - two of the three frontier offerings are explicitly labeled preview as of this snapshot and are the most likely rows in this table to change first. Do not use this lesson to argue about *why* computer use is or isn't the right modality for a task - that argument belongs in `tool-use-agentic-loop/09`, which stays correct regardless of how this product list ages.

## Key takeaways / mental model
Every product named here is one current instance of the durable perceive/act/ground pattern from `tool-use-agentic-loop/09`. When evaluating a new option not listed here, or once this list is stale, first classify it on that lesson's terms: does it ground on pixels, on structure, or both - and is it a first-party vendor product, a developer API, or a model-agnostic open-source harness? That classification survives this lesson's expiration; the specific names, prices, and preview labels are exactly what `next_review` exists to refresh.

## Self-check questions
1. Name one product in this lesson that uses pixel-only grounding and one that uses hybrid structural grounding. What does `tool-use-agentic-loop/09` predict about the trade-off between them, and does this lesson's account of each product match that prediction?
2. OpenAI's Operator was retired as a standalone product in 2025 and folded into ChatGPT Agent. Using the durable framework from `tool-use-agentic-loop/09`, explain why this kind of rename does not invalidate anything that lesson teaches.
3. Two of the three frontier vendors label their computer-use offering "Preview" as of this snapshot. What does that status suggest about which of `tool-use-agentic-loop/09`'s failure modes (misgrounding, stale-state actions, distribution shift, on-screen injection) you should expect to encounter, and why?
4. This lesson flags a discrepancy in Browser Use's GitHub star count and in Gemini's computer-use pricing. For each, explain in one sentence why the disagreement is more likely to reflect real-world change or documentation gaps than a data error.
5. This lesson is dated August 2026 with a November 2026 review. Name two concrete things (a product merge, a pricing change, a preview label lifting) that would make a row in the comparison table wrong before that review date.

## References
- [Anthropic Platform docs: Computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [Anthropic Platform docs: Browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool)
- [Google AI for Developers: Computer use, Gemini API](https://ai.google.dev/gemini-api/docs/computer-use)
- OpenAI, "Introducing Operator" (2025), https://openai.com/index/introducing-operator/
- [OpenAI Platform docs: Pricing](https://developers.openai.com/api/docs/pricing)
- economize.cloud, "computer-use-preview pricing - OpenAI" (accessed Aug 2026), https://www.economize.cloud/resources/open-ai/pricing/computer-use-preview/
- Presenc AI, "OpenAI Operator Update Tracker: From Operator to ChatGPT Agent (2026)" (2026), https://presenc.ai/research/openai-operator-update-tracker-2026
- GitHub, browser-use/browser-use (accessed Aug 2026), https://github.com/browser-use/browser-use
- GitHub Stars Leaderboard, browser-use/browser-use (2026), https://githublb.vercel.app/repo/browser-use/browser-use
- GitHub, browserbase/stagehand (accessed Aug 2026), https://github.com/browserbase/stagehand
- Browserbase, "Stagehand" (accessed Aug 2026), https://www.browserbase.com/stagehand
- GitHub, Skyvern-AI/skyvern (accessed Aug 2026), https://github.com/skyvern-ai/skyvern
- Skyvern, product and blog pages (accessed Aug 2026), https://www.skyvern.com/
- `agentic-engineering/tool-use-agentic-loop/lessons/09-computer-use-as-a-tool-modality.md`, this repository - the durable modality this lesson supplies current examples for
- `agentic-engineering/landscape-snapshot/lessons/05-model-capability-tiers-and-pricing-today.md`, this repository - current per-model token pricing referenced above
