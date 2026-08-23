---
id: tool-use-agentic-loop/09
subject: tool-use-agentic-loop
title: "Computer Use: Screen-Based Perception and Action as a Tool Modality"
slug: computer-use-as-a-tool-modality
status: drafted
mastery:
seniority: senior
source: "Anthropic Platform docs: Computer use tool (2026); Anthropic Platform docs: Browser use tool (2026); Google AI for Developers: Computer use, Gemini API (2026); OSU NLP Group: UGround - Universal Visual Grounding for GUI Agents (2024-2026); arXiv: OS Agents - A Survey on MLLM-based Agents for General Computing Devices Use (2025)"
durability: durable
prerequisites: [tool-use-agentic-loop/01, tool-use-agentic-loop/02]
created: 2026-08-13
updated: 2026-08-13
---

# Computer Use: Screen-Based Perception and Action as a Tool Modality

## TL;DR
`tool-use-agentic-loop/01` and `02` cover function calling: the model emits a typed argument into a schema you designed, and your code executes a named function against it. Computer use is a structurally different tool modality for the same round-trip idea - instead of a typed argument, the model perceives the world through a screenshot or an accessibility-tree read; instead of a named function call, it acts by synthesizing a click, keystroke, or drag aimed at a location on screen. That shift introduces a genuinely new hard problem function calling never has: **grounding** - mapping a semantic intent ("click Submit") onto an actual pixel coordinate or UI element - because nothing in this modality is pre-typed the way a schema's arguments are.

## The idea
Function calling works because the interface is designed in advance: you, the developer, wrote a schema with a closed set of typed fields, so the model's only job is to pick values that fit a space you already defined. That precondition holds whenever the target system exposes an API. It does not hold for the vast majority of software a human actually uses day to day - a decades-old internal tool with no API, a third-party SaaS product that never shipped one, a native desktop application, a web app whose only "interface" is the one rendered for human eyes. Computer use exists to automate exactly that long tail: instead of asking a system to expose a curated, typed interface, you give the model the same interface a human already has - a screen to look at and a mouse/keyboard to act with - and let it operate that interface directly.

This is not "function calling with a different action list." The three-part contract from lesson 01 (name, description, schema) still exists, but the *arguments* the model must produce no longer live in a space you defined - they live in a space defined by whatever happens to be rendered on screen at that moment, which changes at runtime and which the model has never seen the internal representation of. Perceiving that space (screenshot pixels, or a tree of UI elements) and then producing an action that correctly lands within it are two new steps with no equivalent in a `get_weather(location: string)` call, where the "location" the model must produce was always just a string it could reason about in the abstract.

## How it works

### Perception: two different grounding strategies
A computer-use system has to decide how the model perceives the target surface before it decides what actions look like, and there are two structurally different answers in current use:
- **Screenshot-based (pixel) grounding** - the model is given a rendered image of the screen and must visually parse it the way a human would, then predict a pixel coordinate for its intended action. This works on literally anything that can be rendered - a native app, a video game, a PDF viewer, a legacy Java client - because it makes no assumption about the target software cooperating at all.
- **Accessibility-tree / structural grounding** - the model is instead given a semi-structured read of the interface (the same accessibility tree or DOM screen readers use, or HTML for a web page): a list of named, typed elements like `button "Submit" [ref_4]` or `textbox "Search" [ref_3]`. The model acts by referencing an element ID rather than a coordinate.

> **Example (Aug 2026):** one vendor ships both strategies side by side as separate tools - a "computer use" tool that works purely from screenshots and coordinates for desktop-wide automation, and a "browser use" tool that reads the accessibility tree first and falls back to screenshot coordinates only for canvas-like content it can't otherwise reference. See `landscape-snapshot/08` for current products and how they split this decision.

The trade-off is fundamental, not vendor-specific. Structural grounding produces references that are stable across layout reflows (a button keeps the same accessibility label even if a redesign moves it ten pixels), cost far fewer tokens per turn than a full screenshot, and are less error-prone because the model is matching text to text rather than predicting a coordinate on a bitmap. But structural grounding only works where a usable structural representation exists at all - many native desktop apps expose incomplete or missing accessibility trees, and canvas-rendered or heavily custom-styled web UIs often expose none. Pixel grounding is the universal fallback precisely because it requires nothing from the target software except that it can be rendered - the cost is that the model is now doing a real visual-perception task, not a text-matching one, every single turn.

### Action: a small, fixed vocabulary composed at runtime
Function calling gives the model as many narrow, purpose-built tools as you choose to define - `book_flight`, `cancel_order`, `send_email`. Computer use gives the model a small, fixed set of generic primitives instead - click, type, key-press, scroll, drag - the same primitives a human's hand performs, because no one pre-built a `book_flight` action for an application that never exposed one. The model has to *compose* a sequence of these primitives to reach any higher-level outcome, the same way a person clicks into a field, types a value, and clicks a button to submit a form, rather than invoking one atomic call for the whole transaction.

**Worked example - contrast with lesson 01's round trip.** In lesson 01, booking a flight through a well-designed `book_flight(origin, destination, date)` tool is a single round trip: one call, one structured result. The equivalent computer-use task against a booking website with no API might be: screenshot -> click the origin field -> type "SFO" -> screenshot to confirm the autocomplete list appeared -> click the correct suggestion -> click the destination field -> type "JFK" -> screenshot -> click the date picker -> click the correct day -> screenshot -> click "Search". A task that was one tool call under function calling becomes ten-plus perception-and-action turns under computer use, with no reduction in what actually happened in the world - only a difference in whether an API existed to shortcut it.

### Grounding as the specific new hard problem
Grounding is the step with no function-calling equivalent: turning "click the blue Submit button in the top right" into an actual coordinate or element reference the runtime can execute. Under structural grounding this is closer to what lesson 02 already covers (matching a request against named, described elements). Under pixel grounding it is a genuine spatial-perception problem, and the mechanics of that problem are concrete and fragile.

**Worked example - coordinate scaling.** A screenshot is rarely sent to the model at the device's native resolution; vendor docs recommend downscaling to bounded dimensions (for example, capping the long edge and total pixel count) to control image-token cost and stay within model image limits. The model then predicts a coordinate *in the downscaled image's coordinate space* - and the calling application must scale that coordinate back up to the real screen's resolution before executing the click. Miss that scaling step, or get the factor slightly wrong (a common failure on high-DPI/Retina displays reporting a 2x pixel ratio), and every click lands at a consistent, silent offset from its intended target - not a crash, just a wrong click that looks plausible in the model's own reasoning trace. This is exactly the class of failure function calling cannot produce: an argument like `"unit": "celsius"` is either the string the schema expected or it is not, with no equivalent geometric distortion possible.

> **Example (Aug 2026):** vendors differ on the coordinate convention itself - one uses raw screenshot pixel coordinates with origin at the top-left; another normalizes to a fixed 0-1000 range the caller must rescale to the real viewport. The convention is swappable per vendor; the underlying problem - the model outputs a number, and something downstream must correctly map that number onto a real location - is the durable part. See `landscape-snapshot/08`.

### The perception-action loop and its cost profile
Lesson 01's five-step round trip (send -> model emits intent -> you execute -> you re-inject result -> model continues) still describes computer use structurally, but the loop's *shape* changes in ways that matter operationally:
- **It is fine-grained and mostly serial.** A single click can change the entire visible state of the screen (a modal opens, a page navigates, an autocomplete list appears), so the model generally cannot act confidently multiple steps ahead of what it has actually observed - unlike `tool-use-agentic-loop/04`'s independent, parallelizable tool calls, computer-use actions are usually issued a small batch at a time and then re-verified with a fresh screenshot, because the environment is not idempotent between actions the way most API calls are.
- **Each turn is expensive relative to a typed call.** A screenshot alone can run to roughly a thousand or more input tokens depending on resolution, before the model has done anything - a cost with no equivalent for a `{"location": "San Francisco, CA"}` argument, which costs a handful of tokens regardless of how complex the underlying task is.
- **Verification is part of the loop, not an afterthought.** Because an action's success can only be confirmed by observing the resulting state, well-built computer-use loops deliberately end action batches with a fresh perception step (another screenshot or tree read) specifically to check whether the intended effect actually happened, rather than trusting that "the click was sent" means "the click succeeded."

### Failure modes unique to this modality
- **Misgrounding / misclick** - the predicted coordinate or element reference is close to, but not exactly, the intended target (dense toolbars, small icons, ambiguous duplicate-looking buttons), producing an action that looks reasonable in the model's stated intent but has no analog to a schema-validation failure - there is no "invalid click" error to catch defensively the way an out-of-enum string can be caught.
- **Stale-state action** - the model reasons about a screenshot taken before a previous action's effect finished rendering (a page still loading, an animation mid-transition) and issues the next action against a screen state that no longer exists by the time it executes.
- **Visual distribution shift** - a UI that renders with an unfamiliar theme, an unusual resolution, a custom font, or a layout the underlying vision model has poor coverage of degrades pixel-grounding accuracy in a way that is hard to predict in advance and has no equivalent "the schema was wrong" diagnosis.
- **On-screen prompt injection** - because the model is instructed to treat everything rendered on the screen as ground truth about the world, adversarial text embedded in a webpage or document the model is asked to look at can be interpreted as an instruction rather than as content, a risk qualitatively larger than the tool-result injection risk in lesson 01, because the "trusted" input channel and the "untrusted" data channel are the literal same pixels with no structural separation between them. Current vendor tooling addresses this with automatic classifiers that flag suspicious screenshots for human confirmation rather than solving it structurally.

## Pros
- Generalizes to any software with a visual interface, including the long tail that will never expose a public API - this is the one tool modality that can automate legacy, third-party, or purely visual targets at all.
- Requires no cooperation or schema-maintenance from the target application - the interface being automated is whatever a human already uses, so it doesn't go stale the way a hand-built integration against a private API can.
- Composes a small set of general primitives into arbitrary higher-level behavior, rather than requiring a bespoke function to be written and maintained for every distinct action.

## Cons
- Far higher token and latency cost per step than a typed function call, because every turn typically carries a full (or near-full) image rather than a few dozen tokens of structured argument.
- Grounding accuracy is fundamentally a perception problem rather than a schema-conformance problem, so its failure rate is less predictable and harder to defensively validate than an out-of-schema argument from lesson 01.
- Structurally more serial than parallel-tool-call patterns (`tool-use-agentic-loop/04`), since most actions require re-observing the world before the next one is safe to issue.
- A meaningfully larger prompt-injection surface, since the model must treat arbitrary on-screen content as trustworthy signal about world state with no channel separation between "instruction" and "data."

## Alternatives
- **Structured function calling / API integration** (`tool-use-agentic-loop/01`, `02`) — strictly preferable whenever the target system exposes an API: cheaper per turn, faster, and it removes the grounding problem entirely because arguments live in a space you defined rather than one you have to perceive at runtime.
- **Accessibility-tree/DOM-only automation without any pixel fallback** (classic RPA/browser-scripting tooling) — cheaper and more reliable than pixel grounding when the target is a well-formed web page or a well-instrumented native app, but brittle when the target lacks a usable structural representation, and typically can't fall back to "just look at the pixels" the way hybrid tools do.
- **Hybrid grounding that reads structure first and falls back to pixels** — recovers most of structural grounding's stability while retaining pixel grounding's universality for the content that has none; costs some of the implementation complexity of maintaining two grounding paths instead of one.

## When to use it
Reach for computer use when the task genuinely requires operating software that offers no programmatic interface at all - legacy internal tools, third-party products with no API, workflows that span several unrelated desktop applications a human currently stitches together by hand - or as an explicit fallback path when building and maintaining a bespoke function-calling integration for a target isn't feasible. It is also the right modality any time the task's own definition is "operate this software the way a human currently does," because that is precisely the interface computer use targets.

## When NOT to use it
Skip it whenever the target system exposes an API - use `tool-use-agentic-loop/01`/`02`'s structured tool calling instead, since it is cheaper, faster, and simply does not have a grounding problem to fail on. Avoid it for latency- or cost-sensitive high-volume workloads, since the per-turn cost of screenshot-driven perception dwarfs a typed argument. And do not deploy it unattended against irreversible or high-stakes actions (payments, account changes, deletions) without an explicit human-confirmation gate - misgrounding and stale-state actions are documented, current failure modes, not theoretical edge cases.

## Key takeaways / mental model
Function calling and computer use answer the same underlying question - "how does a model's output become a real action in the world?" - with two different perceive/act pairs. Function calling: **perceive = a typed argument you already defined; act = a named function call; the hard problem = schema conformance (lesson 01/02).** Computer use: **perceive = a screenshot or accessibility-tree read of a world you did not define; act = a synthesized click/keystroke aimed at a location in that world; the hard problem = grounding - correctly mapping intent onto that location.** Reach for computer use only when the world genuinely offers no typed interface to call instead, because that missing interface, not any new model capability, is the entire reason this modality exists.

## Self-check questions
1. Walk through lesson 01's `get_weather` round trip and a computer-use "click Submit" action side by side. At exactly which step does a typed argument turn into a perception-plus-coordinate problem, and why does that step have no equivalent in the `get_weather` example?
2. A colleague suggests "just wire up a `click_submit_button` function tool so the model doesn't need to ground anything." Explain why this misses the point of when computer use is the right modality to reach for in the first place.
3. Someone claims "computer use is just function calling with a different action list." Using the grounding problem specifically, explain what is structurally wrong with that framing.
4. Given that a screenshot can cost on the order of a thousand-plus input tokens versus a handful of tokens for a typed argument, and that computer-use actions are usually verified with a fresh screenshot after each small batch, explain why `tool-use-agentic-loop/04`'s parallel-tool-call pattern does not straightforwardly apply to a multi-step computer-use task.
5. Name the two grounding strategies covered in this lesson, and describe one concrete situation where each one fails on its own.
6. Explain why on-screen prompt injection is a qualitatively different risk from the tool-result injection risk implicit in lesson 01's round trip, in terms of what channel the untrusted content arrives on.

## References
- [Anthropic Platform docs: Computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [Anthropic Platform docs: Browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool)
- [Google AI for Developers: Computer use, Gemini API](https://ai.google.dev/gemini-api/docs/computer-use)
- OSU NLP Group, "UGround: Universal Visual Grounding for GUI Agents" (2024-2026), https://osu-nlp-group.github.io/UGround/
- arXiv, "OS Agents: A Survey on MLLM-based Agents for General Computing Devices Use" (2025), https://arxiv.org/pdf/2508.04482
- `agentic-engineering/landscape-snapshot/lessons/08-computer-use-products-today.md`, this repository - current products implementing this modality
