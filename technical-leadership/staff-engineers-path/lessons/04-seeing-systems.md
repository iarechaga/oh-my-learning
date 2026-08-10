---
id: staff-engineers-path/04
subject: staff-engineers-path
title: "Seeing systems, not components: broad technical context"
slug: seeing-systems
status: drafted
mastery:
seniority: staff
source: The Staff Engineer's Path (Tanya Reilly), Chapter 2 - "Three maps" (the topographical map)
prerequisites: [staff-engineers-path/02]
created: 2026-08-10
updated: 2026-08-10
---

# Seeing systems, not components: broad technical context

## TL;DR
Staff engineers need a working mental map of the *whole* technical landscape they operate in — not deep expertise in every system, but enough breadth to know what exists, roughly how it works, who owns it, and where the sharp edges are — so they can reason about cross-system consequences that someone with only local context would miss.

## The idea
A senior engineer's expertise is typically deep and narrow: they know their team's service intimately, down to the code. That depth is valuable but structurally blind to a whole class of problems — the ones that live in the *interactions between* systems, not inside any one of them. A staff engineer needs a complementary kind of knowledge: broad, shallower, but covering the whole topology, so they can answer questions like "if we change this API's retry behavior, what three other systems downstream will start behaving differently?" — a question that requires knowing those three systems exist at all, which nobody with only local depth would know to ask.

Reilly calls this the "topographical map": a mental model of the technical terrain — services, data flows, ownership boundaries, and the informal, undocumented quirks ("that queue backs up every Black Friday and everyone just knows to watch it") that never make it into architecture diagrams.

## How it works

### Building the map deliberately
This context doesn't arrive passively; it has to be built through deliberate effort, because no single team's day-to-day work exposes you to the rest of the org's systems.
- **Read what exists** — architecture docs, RFCs, postmortems (especially postmortems: they reveal the failure modes and hidden dependencies that clean documentation omits), on-call runbooks from other teams.
- **Talk to people outside your team** — cross-team 1:1s, sitting in on another team's design review, asking "what's the scariest part of your system?" in a hallway conversation. Postmortem reviews across the org are a particularly efficient way to learn several systems' failure modes at once.
- **Follow the data, not the org chart** — trace an actual request or a piece of data through its full lifecycle across services; the org chart tells you who owns what, but tracing data flow tells you how systems actually depend on each other, which is often surprising and rarely matches the tidy architecture diagram.
- **Revisit and update** — the map goes stale; systems get replaced, ownership moves, quirks get fixed. A staff engineer periodically refreshes their mental map rather than trusting a two-year-old understanding.

**Worked example.** A staff engineer is asked to review a proposal to add a synchronous call from the checkout service to a recommendations service (to personalize a post-purchase upsell). A reviewer with only checkout-team depth sees a small, clean addition: "adds 20ms, looks fine." A staff engineer with a broader topographical map recalls, from a postmortem she read months earlier, that the recommendations service has no SLO and has had two multi-hour outages this year, both times because a *different* upstream team added a synchronous dependency on it without recommendations' owners knowing. She flags this — not because she's a recommendations expert, but because her broad map told her "recommendations = fragile, no SLO, has burned people before" was a fact worth carrying around, even without deep knowledge of its internals.

### Depth vs. breadth: a trade-off, not a replacement
Broad context does not replace deep expertise — it complements it. A staff engineer typically retains genuine depth in one or two areas (their own team's system, or a domain they came from) while deliberately trading some depth elsewhere for breadth. This is a real trade-off: time spent building a topographical map of ten systems is time not spent going deeper on any one of them. The judgment call is in the register: staff engineers err a level shallower and a level broader than senior engineers, on purpose.

### Recognizing the limits of your own map
A broad map is necessarily approximate and gets stale; the discipline includes knowing when to say "I have rough context here, but you should loop in someone with real depth on system X before we commit" rather than pretending your shallow knowledge is sufficient to make the call alone. Using the map well means using it to know *who to ask*, not just what you already know.

## Pros
- Surfaces cross-system risks that no single team's expert would catch, because the risk lives in the gap between systems, not inside either one.
- Makes a staff engineer a much more effective reviewer, sponsor, and technical-direction author — most of the value in `staff-engineers-path/05` and `staff-engineers-path/09` depends on having this broader map to reason from.
- Builds a natural network across the org (the people you talked to while building the map become the people you call when you need a fast answer), which compounds over time.

## Cons
- Breadth genuinely costs depth; a staff engineer who over-invests in breadth can lose enough hands-on sharpness to lose technical credibility on their own team's system.
- The map decays continuously — systems change faster than any one person can track, so staying current is ongoing overhead, not a one-time investment.
- Overconfidence in a shallow map is dangerous: mistaking "I read a doc about this system once" for "I understand this system well enough to make the call" leads to bad recommendations delivered with unearned confidence.

## Alternatives
- **Rely entirely on deep specialists per system, coordinated by a program/project manager** — trades the staff engineer's cross-system technical judgment for process-driven coordination; works when cross-system technical trade-offs are rare or simple, breaks down when the hard part of a decision *is* the cross-system technical trade-off.
- **Formal architecture registries/service catalogs** — tooling-based approaches (service catalogs, dependency graphs, architecture decision record repositories) that make some of this context discoverable without a person having to hold it all in their head; valuable, but the "quirks and undocumented failure modes" part of the topographical map rarely makes it into a catalog and still requires the human network.
- **Rotational programs** — some orgs deliberately rotate senior/staff engineers across teams for a quarter at a time specifically to build this kind of broad context faster than organic exposure would; more disruptive but faster and deeper than passive reading.

## When to use it
Build and actively maintain a broad technical map whenever your role requires reviewing, sponsoring, or directing work that spans more than your own team — which is most staff-level work. Prioritize breadth-building around systems your own team frequently interacts with or depends on.

## When NOT to use it
Don't chase broad context for its own sake in systems you'll never touch or influence — that's collecting trivia, not building leverage. And don't let breadth-building become an excuse to avoid deep, hands-on work entirely; a staff engineer with zero remaining depth anywhere loses the technical credibility that makes their broad judgment trusted in the first place (see `staff-engineers-path/01` on how the pillars reinforce each other).

## Key takeaways / mental model
Think of your technical knowledge as two axes: depth (how well you know one system) and breadth (how many systems you have working knowledge of, including their failure modes and owners). Senior engineers optimize depth; staff engineers deliberately trade some depth for breadth, retaining real depth in one or two areas, because the highest-value staff problems live in the gaps between systems that only a broad map can see.

## Self-check questions
1. Pick a system outside your own team that you interact with indirectly. What do you actually know about its failure modes, ownership, and quirks — and how would you find out what you don't know?
2. Explain, in your own words, why a proposal that looks safe from inside one team's context can be dangerous from a cross-system view. Use an example different from the recommendations-service one in this lesson.
3. How would you recognize you've traded away too much depth for breadth? What would that failure look like in practice?
4. Describe two concrete, low-cost habits you could adopt this month to start building a broader topographical map of your organization's systems.

## References
- The Staff Engineer's Path (Tanya Reilly), Chapter 2: "Three maps" (topographical map).
