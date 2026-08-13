---
id: landscape-snapshot/01
subject: landscape-snapshot
title: "Coding Agent Products Today: Terminal, IDE, and Cloud Options"
slug: coding-agent-products-today
status: drafted
mastery:
seniority: mid
source: "niteagent.com, AI Coding Agents 2026: The State of Play (2026); Lushbinary, AI Coding Agents 2026: Claude Code vs Antigravity 2.0 vs Codex vs Cursor vs Kiro vs Copilot vs Windsurf (2026); Cursor Docs, Models & Pricing (accessed Aug 2026); GitHub, Copilot Pricing and Coding Agent docs (2026); VentureBeat, Devin 2.0 is here (2025); digitalapplied.com, Windsurf Is Now Devin Desktop (2026); Amazon Q Developer pricing pages, superblocks.com and pricepertoken.com (2026); blakecrosley.com, Codex CLI vs Claude Code 2026 (2026)"
durability: perishable
next_review: 2026-11
prerequisites: [agentic-software-engineering/01]
created: 2026-08-10
updated: 2026-08-10
---

# Coding Agent Products Today: Terminal, IDE, and Cloud Options

## TL;DR
`agentic-software-engineering/01` teaches the three durable execution models - IDE-integrated, terminal-native, and cloud/async. This lesson names who currently builds each one: Claude Code and OpenAI Codex CLI for terminal-native; Cursor, GitHub Copilot, and Devin Desktop (formerly Windsurf) for IDE-integrated; Devin, Copilot's coding agent, and Codex Cloud for cloud/async - plus Amazon Q Developer, which spans several of these inside AWS's ecosystem. Prices, model line-ups, and even company names (Windsurf became Devin Desktop mid-2026) are moving targets; the execution-model framework from `agentic-software-engineering/01` is what should still be true after every name below has changed again.

> **Snapshot date: August 2026.** This lesson is tagged `durability: perishable` and reviewed quarterly (`next_review: 2026-11`) - treat every specific product name, version, and number below as accurate as of the date above, not as a permanent fact. See `agent-docs/fast-moving-domain-policy.md`.

## The idea
`agentic-software-engineering/01` argues that the choice of execution model - how tightly the agentic loop is coupled to live human attention - is an engineering decision, not a brand preference. That lesson deliberately avoided naming products so it stays true regardless of which vendor wins any given quarter. This lesson is the paired, disposable half: it names the actual products a mid-level engineer would evaluate today, sorted into the same three models, so the durable framework has something concrete to apply to right now.

The market as of August 2026 has consolidated somewhat compared to 2024-2025's proliferation of point tools - most notably Cognition (maker of Devin) acquiring Windsurf in mid-2025 and rebranding it "Devin Desktop" in June 2026 - but it has also fragmented along a new axis: several products now let you plug in *any* frontier model (Claude, GPT, Gemini) rather than shipping with one fixed model, which decouples "which product's harness do I use" from "which model does the reasoning."

## How it works

### Terminal-native agents
These run as a CLI process with real shell access against your actual checkout, per `agentic-software-engineering/01`'s Model 2.

- **Claude Code** (Anthropic) - the terminal-native agent most closely associated with this pattern; runs against the actual filesystem and shell, supports subagents and per-subagent model selection, and is bundled into Claude subscription plans rather than sold standalone. Pricing (Aug 2026): Pro $17-20/mo, Max 5x $100/mo, Max 20x $200/mo, Team Standard ~$20-25/user/mo, Team Premium ~$100-125/user/mo, plus pay-per-token API billing with no monthly minimum. Anthropic doubled paid-plan usage limits in May 2026.
- **OpenAI Codex CLI** (OpenAI) - the terminal/local counterpart to OpenAI's cloud Codex offering (below); bundled into ChatGPT plans (Plus $20/mo, Pro 5x $100/mo added April 2026) with token-based billing that took effect in April 2026. Local CLI runs are cheaper per task than cloud runs because there is no sandboxed-container fee on top of token cost.

### IDE-integrated agents
These run as an editor fork or extension proposing inline diffs for the human to accept, per `agentic-software-engineering/01`'s Model 1.

- **Cursor** (Anysphere) - a VS Code fork with the largest community and most polished UX among IDE-integrated agents as of 2026; ships its own first-party model, Composer 2.5, tuned to deliver near-frontier coding performance at a fraction of the cost of routing every call through Claude Opus or GPT-5, alongside a model pool that includes Grok 4.5/4.6 and third-party frontier models. Pricing: Hobby (free, limited), Pro $20/mo, Pro+ $60/mo, Ultra $200/mo (for all-day agent workflows), Business $40/user/mo. As of June 2026, paid seats split usage into two pools - a cheaper Composer/Auto pool and a pricier third-party-API pool (Claude, GPT, Gemini) - to give more headroom at the same price.
- **GitHub Copilot** (GitHub/Microsoft) - the incumbent IDE-integrated agent by installed base, with an "agent mode" and a separate autonomous "coding agent" (below, under cloud/async) in the same product family. Pricing restructured June 1, 2026 from Premium Request Units to token-based "GitHub AI Credits"; inline completions remain free on paid plans and don't draw from the credit pool, while chat/agent mode/code review/CLI do. Plans: Free, Pro $10/mo, Pro+ $39/mo, Max $100/mo, Business $19/seat, Enterprise $39/seat. 2026 additions include agentic code review (March 2026, gathers full project context and can hand fixes to the coding agent) and GitHub Spark, a natural-language app builder exclusive to Pro+ and Enterprise.
- **Devin Desktop** (Cognition) - Windsurf's successor brand after Cognition's July 2025 acquisition and June 2, 2026 rebrand; shipped as an over-the-air update to existing Windsurf installs with accounts, plans, extensions, and MCP connections carried over automatically. Positions itself as a "cockpit for every coding agent" - i.e., a host IDE that can run Devin's own agent or delegate to others - rather than a single fixed model harness.

### Cloud/async agents
These run detached on remote infrastructure, taking a ticket-shaped task and returning a pull request, per `agentic-software-engineering/01`'s Model 3.

- **Devin** (Cognition) - the product most associated with defining this category; works from Slack messages, GitHub issues, or Jira tickets, plans the task, writes code, runs tests, and iterates unattended. Pricing uses Agent Compute Units (ACUs), a normalized measure of VM time, inference, and bandwidth: Core $20/mo (entry tier, cut from $500/mo at the 2.0 relaunch), Team $500/mo including 250 ACUs at $2/ACU, and custom Enterprise pricing.
- **GitHub Copilot coding agent** - assign an issue, receive a PR; available on Pro, Pro+, Business, and Enterprise plans, drawing from the same AI Credits pool as Copilot's other agentic features. Described in 2026 coverage as the IDE-adjacent product closest to Devin's fully autonomous shape while remaining inside the GitHub review workflow.
- **OpenAI Codex Cloud** - the detached counterpart to Codex CLI: isolated containers with full repo access, shell, and test runner, billed with a container fee layered on top of token costs, versus the cheaper token-only local CLI path. Both draw from the same ChatGPT-plan quota structure.

### Spans multiple models: Amazon Q Developer
Amazon Q Developer (AWS) does not map cleanly onto one execution model - it offers editor completions and chat (IDE-integrated), an agent that plans/builds/fixes across a codebase from VS Code, JetBrains, or the AWS Console, and a "transformation agent" for large-scale, ticket-like modernization work (closer to cloud/async in spirit, though it runs from inside AWS tooling rather than a fully detached queue). Pricing: Free tier (unlimited completions, 50 agent interactions/month), Pro $19/user/mo (unlimited agent interactions, enterprise governance features). 2026 coverage cites the April 2025 agent update reaching 66% on SWE-bench Verified and 49% on SWT-bench - see `landscape-snapshot/04` for what those specific benchmark numbers do and don't tell you, and note that SWE-bench Verified itself has faced contamination criticism in 2026 (also covered there).

### Comparison table

| Product | Execution model(s) | Entry pricing (Aug 2026) | Standout feature |
| --- | --- | --- | --- |
| Claude Code (Anthropic) | Terminal-native | Bundled in Pro $17-20/mo | Subagents with per-subagent model choice |
| OpenAI Codex CLI / Cloud | Terminal-native + cloud/async | Bundled in ChatGPT Plus $20/mo | Shared quota across local and cloud execution |
| Cursor (Anysphere) | IDE-integrated | Free (Hobby) / Pro $20/mo | First-party Composer 2.5 model, split usage pools |
| GitHub Copilot | IDE-integrated + cloud/async | Free / Pro $10/mo | Deepest GitHub-native review/PR integration |
| Devin Desktop (Cognition) | IDE-integrated (multi-agent host) | Carries over Windsurf plans | Rebranded "cockpit" that can host other agents |
| Devin (Cognition) | Cloud/async | Core $20/mo (ACU-metered) | Full unattended lifecycle from a Slack/Jira ticket |
| Amazon Q Developer (AWS) | IDE-integrated + cloud/async-leaning | Free tier / Pro $19/user/mo | AWS-native modernization/transformation agent |

Sources disagree on exact current SWE-bench-style scores per product and on how directly Devin Desktop and Windsurf's old tiers map - treat the table's "standout feature" column, not any specific benchmark percentage, as the durable takeaway from this snapshot.

## Pros
- A mid-level engineer today can pick a terminal-native, IDE-integrated, or cloud/async product for nearly any budget, from a free tier (Copilot Free, Cursor Hobby, Amazon Q Free) up to enterprise-metered options (Devin Team, Copilot Enterprise).
- Convergence toward "bring your own model" (Cursor's third-party pool, Copilot's multi-model chat, Devin Desktop hosting other agents) means the execution-model choice from `agentic-software-engineering/01` is increasingly decoupled from which frontier model does the reasoning - you can usually change one without the other.
- Real competitive pressure has driven entry-tier prices down sharply since 2025 (Devin's Core tier fell from $500/mo to $20/mo at the 2.0 relaunch), lowering the bar for experimenting with cloud/async execution specifically.

## Cons
- Names and even company boundaries are shifting fast enough to outdate a lesson like this one within months - Windsurf becoming Devin Desktop mid-2026 is exactly the kind of change `next_review` exists to catch.
- Pricing models differ in kind, not just amount (flat subscription vs. ACU-metered vs. token-metered vs. credit-pool), making apples-to-apples cost comparison across products genuinely hard without running your own workload through each.
- Benchmark claims cited in vendor and press coverage (e.g., Amazon Q's SWE-bench Verified score) should be read through `landscape-snapshot/04` before being used to choose a product - the underlying benchmark's own reliability is contested as of 2026.

## Alternatives
- **`agentic-software-engineering/01`'s durable execution-model framework alone, with no specific product chosen yet** - preferable when you need to reason about the trade-off itself (how much live attention a task deserves) before committing to any vendor; that lesson is the one to reread once this one is stale.
- **Building a custom harness on a raw model API instead of any packaged product** - preferable for teams with unusual security, on-prem, or workflow requirements none of the above products fit off the shelf, at the cost of building and maintaining your own agent loop.
- **Not using an agentic coding product at all, sticking to autocomplete-only tooling** - still reasonable for teams in early evaluation, regulated codebases without sandboxing, or workloads where the review overhead of any of the above isn't yet justified.

## When to use it
Use this lesson when you need a concrete, current shortlist to start evaluating - "which terminal-native agent should I trial this quarter," "what does Cursor cost at the tier I'd actually use," "is Devin's ACU pricing cheaper than a flat Copilot seat for our workload." Pair it with `agentic-software-engineering/01` to first confirm which execution model actually fits the task before picking a specific product within that model.

## When NOT to use it
Do not treat any number or feature claim here as still true without checking `next_review` and, ideally, the vendor's own current pricing page - by the nature of this subject (`agent-docs/fast-moving-domain-policy.md`), this table is expected to be wrong somewhere within a quarter. Do not use this lesson to make an architectural argument about *why* one execution model suits a task better than another - that argument belongs in `agentic-software-engineering/01`, which will still be correct long after this lesson is rewritten.

## Key takeaways / mental model
Every product named here is one current instance of one of three durable execution models. When evaluating a new option that isn't listed - or when this list is stale - first classify it: does a human watch every diff (IDE-integrated), does it run locally over a whole task before reporting back (terminal-native), or does it run fully unattended and hand back a finished PR (cloud/async)? That classification, from `agentic-software-engineering/01`, is what survives this lesson's expiration; the vendor names and prices are what `next_review` exists to refresh.

## Self-check questions
1. Pick one product from each of the three execution-model categories above. For each, name the one feature that most clearly signals which model it belongs to.
2. Amazon Q Developer doesn't fit cleanly into one execution model. Using the diagnostic from `agentic-software-engineering/01` ("how much live attention does this task deserve"), explain why a single product can legitimately span more than one model.
3. Devin's pricing uses Agent Compute Units instead of a flat monthly fee. What does that pricing shape imply about how cloud/async execution's costs behave differently from an IDE-integrated subscription's costs?
4. This lesson is dated August 2026 with a November 2026 review. Name two concrete things (a product rename, a pricing change, a new entrant) that would make a row in this lesson's comparison table wrong before that review date - and explain why none of them would make `agentic-software-engineering/01` wrong.

## References
- niteagent.com, "AI Coding Agents 2026: The State of Play - CLI, IDE, and Cloud Agents Compared" (2026), https://niteagent.com/blog/2026-05-21-ai-coding-agents-state-of-play/
- Lushbinary, "AI Coding Agents 2026: Claude Code vs Antigravity 2.0 vs Codex vs Cursor vs Kiro vs Copilot vs Windsurf - Pricing & Features Compared" (2026), https://lushbinary.com/blog/ai-coding-agents-comparison-cursor-windsurf-claude-copilot-kiro-2026/
- Cursor Docs, "Models & Pricing" (accessed Aug 2026), https://cursor.com/docs/models-and-pricing
- IntuitionLabs, "Claude Subscription Plans & Pricing 2026: $20 to $200/mo" (2026), https://intuitionlabs.ai/articles/claude-pricing-plans-api-costs
- Automation Atlas, "GitHub Copilot Pricing 2026 Explained" (2026), https://automationatlas.io/answers/github-copilot-pricing-explained-2026/
- NxCode, "GitHub Copilot 2026: Complete Guide to Pricing, Agent Mode" (2026), https://www.nxcode.io/resources/news/github-copilot-complete-guide-2026-features-pricing-agents
- VentureBeat, "Devin 2.0 is here: Cognition slashes price of AI software engineer to $20 per month from $500" (2025), https://venturebeat.com/programming-development/devin-2-0-is-here-cognition-slashes-price-of-ai-software-engineer-to-20-per-month-from-500
- digitalapplied.com, "Windsurf Is Now Devin Desktop: What Users Should Do" (2026), https://www.digitalapplied.com/blog/windsurf-becomes-devin-desktop-ide-migration-2026
- superblocks.com, "Amazon Q Developer: Pricing, Features and Alternatives in 2026" (2026), https://www.superblocks.com/blog/amazon-qdeveloper-pricing
- pricepertoken.com, "Amazon Q Developer Pricing 2026" (2026), https://pricepertoken.com/coding-assistants/amazon-q-developer
- blakecrosley.com, "Codex CLI vs Claude Code 2026: Architecture, Pricing, and China Access" (2026), https://blakecrosley.com/blog/codex-vs-claude-code-2026
- `agentic-engineering/agentic-software-engineering/lessons/01-where-coding-agents-run.md`, this repository - the durable execution-model framework this lesson supplies current examples for
