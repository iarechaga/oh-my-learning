---
id: thinking-fast-and-slow/08
subject: thinking-fast-and-slow
title: Confirmation bias and coherence illusions
slug: confirmation-and-coherence
status: drafted
mastery:
seniority: senior
source: Thinking, Fast and Slow (Daniel Kahneman), Part I, Chapter 4, and Part III, Chapters 7-9
prerequisites: [thinking-fast-and-slow/01, thinking-fast-and-slow/03]
created: 2026-08-10
updated: 2026-08-10
---

# Confirmation bias and coherence illusions

## TL;DR
System 1 doesn't evaluate evidence neutrally — it builds the most coherent story it can from whatever information is currently available, actively suppresses doubt, and generates confidence proportional to how *coherent* that story feels, not to how much or how reliable the evidence actually is. This produces two linked failures: we search for and favor evidence that confirms what we already believe, and we feel confident even when the story was built from very little, or very unreliable, information.

## The idea
Kahneman names this "What You See Is All There Is" (WYSIATI) — System 1 constructs the best possible story from currently available information and, critically, does not flag when that information is thin, unrepresentative, or missing key facts. It doesn't compute "how much evidence is there" or "how reliable is this evidence" as separate steps before generating a conclusion; it just makes the best coherent narrative out of whatever's in front of it, and *that coherence itself* is what generates confidence. Confirmation bias is the natural downstream consequence: once System 1 has settled on a coherent story, System 1's associative machinery preferentially retrieves and generates further information consistent with that story, and disconfirming information is harder to notice, easier to dismiss, and less "available" (`thinking-fast-and-slow/05`) than confirming information.

## How it works

### WYSIATI: quantity and quality of evidence don't gate confidence
The core insight is that confidence is generated from coherence, not from evidence sufficiency. A conclusion built from three consistent, low-quality anecdotes can feel just as certain as one built from a rigorous statistical analysis — because the *feeling* of confidence tracks how well the story hangs together internally, not how much you actually know. Kahneman notes this explains why people can form strong, confident opinions on the basis of remarkably little information: System 1 simply doesn't have a mechanism for registering "I should be uncertain because I'm missing important information I don't even know I'm missing."

**Engineering example:** an engineer reviews a bug report, forms a theory in the first two minutes ("this is definitely a race condition in the cache layer"), and from that point on interprets every subsequent log line through that theory's lens. If the theory happens to be wrong, the engineer's confidence doesn't dip proportionally — it often stays high, because each new piece of evidence gets fit into the existing coherent story (WYSIATI), rather than triggering a re-evaluation of whether the story itself was right.

### Confirmation bias: seeking and favoring supportive evidence
Once a hypothesis exists, people disproportionately search for evidence that would confirm it, interpret ambiguous evidence as confirming, and give disconfirming evidence less weight or explain it away. This is not usually a deliberate act of dishonesty — it's how coherence-seeking System 1 naturally behaves, and System 2 rarely intervenes because doing so requires actively generating the disconfirming case, which is effortful and feels unnecessary once a satisfying story already exists.

**Worked example — architecture decision confirmation:** a tech lead proposes microservices for a new system, believing it will improve team autonomy. In design review, they naturally ask questions like "how would this modular boundary help us scale the team?" (confirming) rather than "what specific coordination costs will this impose that a monolith wouldn't have?" (disconfirming). Both questions are legitimate and relevant, but confirmation bias means the first kind of question gets asked far more often and answered more thoroughly than the second, systematically biasing the resulting decision toward the initially preferred option.

**Worked example — postmortem confirmation:** if an incident commander forms an early theory ("this looks like the deploy from an hour ago"), team members subsequently reviewing logs tend to interpret ambiguous signals as consistent with that theory rather than actively hunting for evidence of alternative causes — this is a well-documented failure mode in incident response, which is why mature incident processes explicitly assign someone to argue against the leading theory.

### Halo effect: coherence bleeds across unrelated dimensions
A specific, well-studied instance of coherence-seeking: once you form a positive (or negative) impression of someone or something on one dimension, that impression colors your judgment of *unrelated* dimensions too, because System 1 wants a single coherent overall picture rather than independently evaluated ones. Kahneman describes how a person who behaves confidently and articulately in a job interview is subsequently judged as likely smarter, more competent, and more trustworthy across dimensions the interview never actually tested.

**Engineering example — the halo effect in code review:** a pull request from an engineer with a strong reputation gets less scrutiny on its actual logic than an identical PR from a newer or less-established engineer — the halo of "this person is generally excellent" bleeds into "so this specific change is probably fine," even though the reviewer hasn't actually verified the specific change any more carefully. This is a well-known, real source of uneven code review rigor and a fairness problem in engineering teams.

### Illusion of validity and the pundit problem
Kahneman describes long-running research (Philip Tetlock's studies of expert political forecasters) showing that self-assured, confident experts who build clear, coherent narrative explanations were *less* accurate in their predictions than more hedging, self-doubting experts who considered multiple competing hypotheses — precisely because a single coherent story is fragile (built from whatever fits) while considering multiple hypotheses forces confrontation with disconfirming evidence.

**Engineering application:** an architect who presents one confident, singular narrative for why a design will work is often less reliable than one who explicitly lays out two or three competing failure scenarios and reasons about each — not because confidence is inherently bad, but because building a single coherent story is exactly the process that suppresses awareness of what's missing.

## Pros
- Coherence-seeking is what makes System 1 useful at all — without the drive to build a single sensible story from partial information, ordinary situations (a partially observed system, an ambiguous bug report) would be paralyzing rather than quickly navigable.
- Naming the halo effect explicitly gives teams a concrete, addressable fairness lever in code review and performance evaluation: deliberately blind or structure reviews to reduce reputation bleed-through.
- The WYSIATI framing gives a sharp, memorable self-check question — "what am I not seeing, that I don't even know I'm not seeing?" — that's directly actionable before any confident decision.

## Cons
- Actively generating disconfirming evidence for your own hypothesis is effortful (System 2 work) and socially awkward (it can look like undermining your own idea or someone else's), so the fix is costly to apply consistently, not just intellectually simple.
- Structured devil's-advocate processes, if applied ritualistically without real intent, can become theater (a token "red team" step that doesn't actually change the outcome) rather than a genuine coherence-breaking intervention.
- Overcorrecting into chronic self-doubt about every conclusion is paralyzing and itself has real cost — the goal is targeted skepticism on high-stakes conclusions, not blanket distrust of all fast judgment.

## Alternatives
- **Devil's advocate / red-teaming** — formally assign someone the role of arguing against the leading hypothesis, specifically to force the disconfirming search that confirmation bias otherwise suppresses; effective when taken seriously, weak when performative.
- **Structured analytic techniques (e.g., Analysis of Competing Hypotheses, used in intelligence analysis)** — explicitly lay out multiple hypotheses side by side and score each against the same evidence, instead of building one coherent narrative and testing it in isolation; more effortful but directly targets WYSIATI's single-story bias.
- **Blind or structured review processes** — remove identity/reputation information before evaluating code, designs, or performance, specifically to prevent the halo effect from substituting for direct evaluation of the actual work.

## When to use it
Watch for confirmation bias and the halo effect specifically in high-stakes, hard-to-reverse evaluative decisions: architecture reviews, incident root-cause determination, performance calibration, and any situation where one person's early, confident framing could steer the whole group's subsequent evidence-gathering.

## When NOT to use it
Don't apply heavyweight disconfirmation processes (formal red-teaming, structured competing-hypothesis analysis) to routine, low-stakes, easily-reversible decisions — the overhead isn't justified when being wrong is cheap and quickly correctable through normal iteration.

## Key takeaways / mental model
Notice when a conclusion feels confidently "obvious" and ask: "What evidence would change my mind, and have I actually looked for it — or have I only been looking for things that confirm what I already believe?" Separately, notice when your judgment of one thing (a person, a system) might be bleeding, unearned, into your judgment of something unrelated (the halo effect) and evaluate that unrelated thing on its own terms.

## Self-check questions
1. Describe a recent debugging session where you formed an early theory. Did you notice yourself interpreting ambiguous evidence as confirming that theory rather than actively looking for evidence against it?
2. Explain the halo effect using a concrete code-review example from your own team, and propose one process change that would reduce it.
3. Why does WYSIATI mean that confidence and evidence quantity/quality can be completely decoupled? Give an example where you (or someone you know) were highly confident based on surprisingly little actual evidence.
4. Tetlock's research found confident, single-narrative-building experts were less accurate forecasters than hedging, multiple-hypothesis-holding ones. How would you apply this finding to how your team runs architecture reviews?

## References
- Thinking, Fast and Slow (Daniel Kahneman), Part I: Chapter 4 ("The Associative Machine"); Part III: Chapters 7-9 ("A Machine for Jumping to Conclusions," "How Judgments Happen," "Answering an Easier Question").
