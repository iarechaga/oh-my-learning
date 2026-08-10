---
id: thinking-fast-and-slow/11
subject: thinking-fast-and-slow
title: "Prospect theory: value functions and loss aversion"
slug: prospect-theory
status: drafted
mastery:
seniority: senior
source: Thinking, Fast and Slow (Daniel Kahneman), Part IV, Chapters 25-27
prerequisites: [thinking-fast-and-slow/01]
created: 2026-08-10
updated: 2026-08-10
---

# Prospect theory: value functions and loss aversion

## TL;DR
People don't evaluate outcomes in absolute terms — they evaluate gains and losses *relative to a reference point* (usually the status quo), and losses hurt roughly twice as much as equivalent gains feel good. This one asymmetry — loss aversion — reshapes risk-taking, negotiation, and change-management behavior across engineering organizations far more than most people realize.

## The idea
Classical economic theory (expected utility theory) assumes people evaluate choices based on final wealth/outcome states, and that a dollar gained and a dollar lost carry symmetric weight. Kahneman and Tversky's prospect theory, developed through extensive experiments in the late 1970s (work that contributed to Kahneman's 2002 Nobel Prize in Economics), showed this is empirically false in two major ways: people evaluate outcomes relative to a *reference point*, not in absolute terms, and the psychological impact of losses is significantly larger than equivalent gains. Prospect theory exists because it better predicts actual human choices under risk than expected utility theory does — it's a *descriptive* model of how people decide, not a claim about what's rational.

## How it works

### The value function: three key properties
Kahneman describes an S-shaped "value function" with three defining properties, each demonstrated experimentally.

**1. Reference dependence.** Value is assigned to *changes* in wealth or well-being relative to a reference point (usually the current state, or an expectation), not to absolute final states. A $50,000 salary feels very different depending on whether your reference point is a previous $40,000 salary (a gain, feels good) or a previous $60,000 salary (a loss, feels bad) — even though $50,000 is $50,000 either way.

**2. Diminishing sensitivity.** The subjective impact of a change gets smaller the further you are from the reference point, in both directions — the difference between $0 and $100 gained feels much larger than the difference between $1,000 and $1,100 gained, even though both are $100. This produces the S-shape: concave (risk-averse) for gains, convex (risk-seeking) for losses.

**3. Loss aversion.** The most consequential property: losses loom larger than equivalent gains — roughly by a factor of about 2 to 2.5, based on many experiments (e.g., most people require a possible gain of around $200 to accept a coin-flip gamble that could lose $100). This asymmetry is the single most robust and widely-cited finding of the whole book.

### The endowment effect: ownership creates a new reference point
Once you own something, it becomes your reference point, and giving it up registers as a loss — which, by loss aversion, is felt more strongly than the equivalent gain of acquiring it in the first place would have been. In the book's classic mug experiment, subjects given a coffee mug demanded roughly twice as much money to sell it as other subjects, who didn't own the mug, were willing to pay to buy an identical one — the same object, valued very differently purely based on which side of "ownership" you're on.

**Engineering example — sunset a legacy system:** a team that has "owned" a legacy internal tool for years will resist deprecating it with an intensity disproportionate to its actual current utility, because losing the tool (even one that's genuinely obsolete) registers as a loss against their reference point of "we have this tool," while the team that would benefit from the replacement hasn't yet formed a reference point around it, so gaining it doesn't feel proportionally as strong. This asymmetry — not stubbornness — is a major reason legacy system migrations meet more resistance than their objective merits would predict.

**Engineering example — status quo bias in tooling and process:** proposing to replace a familiar (if imperfect) CI pipeline, code style, or workflow triggers resistance disproportionate to the actual cost/benefit analysis, because the current setup is the reference point, and any friction during migration registers as an immediate, vivid loss, while the (larger, but deferred and abstract) long-term gains from the new system don't carry equivalent psychological weight until they, too, become the new reference point.

### Risk-seeking in the domain of losses
Because the value function is convex (risk-seeking) below the reference point, people facing a sure loss often gamble to avoid it, even when the gamble has a worse expected value than accepting the loss — this is the mechanism behind the loss-frame result in the Asian disease problem (`thinking-fast-and-slow/09`).

**Engineering example — the "just ship it, we're already late" trap:** a project that's already badly over deadline (a "loss" relative to the reference point of the original commitment) often triggers risk-seeking behavior — skipping testing, deploying on a Friday, cutting corners that would never be accepted if the project were on time — because the team is trying to avoid the *sure, registered loss* of admitting further delay, and is willing to gamble on a worse expected outcome (a production incident) to avoid that certain, immediate loss. This mirrors the "break-even effect" documented in gambling and trading research: people take excessive risks specifically when trying to get back to even after a loss.

**Engineering example — sunk-cost-adjacent architecture decisions:** a team that invested six months building a custom framework, and is now facing evidence it should be scrapped for an off-the-shelf alternative, frequently keeps investing further (a form of loss-averse, risk-seeking-to-avoid-the-loss behavior) rather than accepting the sunk cost as a realized loss and cutting over — the psychological pain of formally registering the loss is often larger than the rational expected cost of continuing to throw good effort after bad.

### Loss aversion in negotiation and change management
Because losses are felt roughly twice as strongly as equivalent gains, negotiations and organizational change efforts that are framed purely around gains ("here's what you'll get") consistently underperform ones that also explicitly address losses ("here's what you're worried about losing, and here's how we're addressing it") — ignoring the loss side of a change leaves the most psychologically potent objection unaddressed.

**Engineering example — reorg or team restructuring:** engineers who are moved to a new team, even one that is objectively a better fit for their skills and career growth, frequently resist the change strongly — not necessarily because the new team is worse, but because the move registers as a loss of the current team's familiar relationships, codebase knowledge, and status, and that loss is felt more acutely than the (real, but not-yet-experienced) gains of the new assignment. Change management that explicitly acknowledges and mitigates the loss side (preserving some continuity, giving people agency in the transition) performs measurably better than change management that only pitches the upside.

## Pros
- Loss aversion explains a huge amount of otherwise-puzzling resistance to good ideas (deprecating tools, migrations, reorgs) as a predictable psychological pattern rather than irrationality or stubbornness, which makes it manageable rather than just frustrating.
- The reference-point concept gives leaders a concrete lever: you can shift how a change is received by deliberately managing what the "reference point" is framed as (e.g., anchoring expectations early, before the current state becomes entrenched as the reference point).
- It's one of the most empirically robust findings in behavioral economics, replicated across many domains (finance, consumer behavior, negotiation), so it's a trustworthy foundation to build organizational practice on.

## Cons
- Loss aversion can be misused to justify excessive caution or resistance to genuinely necessary change ("people will feel a loss" becomes an excuse to never deprecate anything) rather than as a factor to actively manage through communication and transition design.
- The exact loss-aversion ratio (commonly cited as ~2x) varies significantly across domains, individuals, and stakes — treating it as a precise, universal constant rather than a general directional tendency overstates the theory's precision.
- Reference points themselves are not fixed or objective — they can be manipulated (by whoever controls the framing) in ways that shade into manipulation rather than honest communication, an ethical tension shared with `thinking-fast-and-slow/09`.

## Alternatives
- **Expected utility theory (classical)** — the normative baseline prospect theory was built to outperform descriptively; still useful as a benchmark for "what a purely rational risk-neutral or risk-averse agent would do," even though it doesn't predict actual human behavior as well.
- **Regret theory** — an alternative descriptive model focused specifically on anticipated regret as the driver of risk preferences, rather than the gain/loss value function; useful in contexts (like conservative technical bets) where "avoiding a decision I'd later regret" is a more accurate description of the driving motivation than pure loss aversion.
- **Cumulative prospect theory (Tversky and Kahneman's own later refinement)** — extends the original theory with more accurate probability-weighting for multiple-outcome gambles; more mathematically complete but more complex to apply informally.

## When to use it
Apply prospect-theory thinking whenever you're managing organizational change (migrations, reorgs, tool deprecations, process changes) or negotiating — explicitly identify what the audience's current reference point is, address the loss side directly rather than only pitching gains, and expect resistance proportional to perceived loss, not to objective merit.

## When NOT to use it
Don't use loss aversion as a blanket excuse to avoid ever proposing disruptive-but-necessary changes, and don't rely on it as a precise predictive formula (exact percentages, exact ratios) for a specific individual or team's reaction — it's a strong directional prior, not a calculator.

## Key takeaways / mental model
Before proposing any change, ask: "What is the audience's current reference point, and what will they perceive themselves as losing — even if the net expected value is clearly positive?" Address that loss explicitly and early; a change proposal that only lists gains is missing the psychologically heavier half of the argument.

## Self-check questions
1. Explain the mug experiment (endowment effect) and connect it to a real resistance-to-change episode you've seen in an engineering org (a tool deprecation, a process change, a reorg).
2. Why does a team that's already behind schedule often take on more risk (skipping tests, rushing a deploy) rather than less? Connect your answer to the shape of the value function in the loss domain.
3. Describe a change-management communication you've seen (or given) that only pitched gains and ignored the loss side. How would you rewrite it to address loss aversion directly?
4. Is loss aversion at roughly a 2x ratio a precise, reliable number you'd use to justify a specific business decision, or a general directional tendency? Explain the difference and why it matters for how you apply this lesson.

## References
- Thinking, Fast and Slow (Daniel Kahneman), Part IV: Chapters 25-27 ("Bernoulli's Errors," "Prospect Theory," "The Endowment Effect").
