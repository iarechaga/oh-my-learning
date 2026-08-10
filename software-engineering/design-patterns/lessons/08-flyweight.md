---
id: design-patterns/08
subject: design-patterns
title: "Structural: Flyweight"
slug: flyweight
status: drafted
mastery:
seniority: senior
source: Design Patterns (Gamma, Helm, Johnson, Vlissides), Chapter 4
prerequisites: [design-patterns/07]
created: 2026-08-10
updated: 2026-08-10
---

# Structural: Flyweight

## TL;DR
Flyweight reduces memory use when a program needs vast numbers of similar objects, by splitting each object's state into a shareable, immutable part (kept in one pooled instance) and a context-specific part (kept separately, passed in at use time) — trading a small amount of design complexity for a large reduction in memory footprint, specifically when object count is genuinely the bottleneck.

## The idea
Some programs need to represent an enormous number of logically-similar objects — every character in a word processor's document, every tree in a forest-rendering engine, every tile on a game map. If each of these were a fully independent object holding all its own state, memory use would scale linearly (or worse) with count, and for large enough counts, that becomes the actual bottleneck. Flyweight's insight: much of each object's state is often **identical across many instances** (every "e" glyph in a document shares the same font, shape, and rendering data; only its position on the page differs) — so split state into two categories and stop duplicating the shared part.

## How it works

### Intrinsic state (shared) vs. extrinsic state (context-specific)
- **Intrinsic state** — the part of an object's state that's independent of context and can be safely shared across many logical "instances" without any of them noticing (a character glyph's shape, a tree species' texture and mesh data).
- **Extrinsic state** — the part that varies per usage context and cannot be shared (a specific character's x/y position on a page, a specific tree's coordinates in the forest).

Flyweight keeps exactly one shared object per distinct combination of intrinsic state (pooled and reused), and requires the extrinsic state to be supplied by the calling code at the point of use, rather than stored inside the shared object at all.

**Worked example.** Rendering a forest of 1,000,000 trees, where there are only 3 distinct tree *species* (each with its own mesh and texture data — genuinely large, expensive-to-duplicate intrinsic state) but 1,000,000 distinct *positions*:
```
class TreeType:                                     # the Flyweight — intrinsic state only
    def __init__(self, mesh, texture):
        self.mesh = mesh        # large, shared, identical across all trees of this species
        self.texture = texture
    def render(self, x, y):                          # extrinsic state passed in, not stored
        draw_mesh_at(self.mesh, self.texture, x, y)

class TreeTypeFactory:
    _pool = {}
    @staticmethod
    def get(species) -> TreeType:
        if species not in TreeTypeFactory._pool:
            TreeTypeFactory._pool[species] = TreeType(load_mesh(species), load_texture(species))
        return TreeTypeFactory._pool[species]

class Tree:                                         # holds only the extrinsic state
    def __init__(self, species, x, y):
        self.type = TreeTypeFactory.get(species)     # shared reference, not a copy
        self.x, self.y = x, y
    def render(self):
        self.type.render(self.x, self.y)
```
Without Flyweight, 1,000,000 `Tree` objects would each duplicate a full mesh+texture — an enormous, likely infeasible memory footprint. With Flyweight, there are only 3 actual `TreeType` (Flyweight) instances in memory, shared by reference across all 1,000,000 `Tree` objects, each of which stores only its small, genuinely per-instance `x`/`y` — a dramatic memory reduction, entirely from recognizing that most of each tree's "identity" was actually shared, not unique.

### The factory's role: ensuring sharing actually happens
Flyweight almost always pairs with a factory (echoing `design-patterns/03`) whose specific job is ensuring that requesting a Flyweight for a given intrinsic-state combination always returns the *same* pooled instance rather than constructing a new one each time — without this pooling factory, the pattern provides no benefit at all, since the whole savings comes specifically from *not* duplicating identical intrinsic state.

### Flyweight objects should be immutable
Because a single Flyweight instance is shared across potentially many different usage contexts simultaneously, it must not be mutated after creation — if one caller could change a shared `TreeType`'s texture, every other tree sharing that same pooled `TreeType` instance would be silently affected too, an instance of the shared-mutable-state hazard `pragmatic-programmer/11` warns about, here arising specifically from the pattern's own sharing mechanism rather than from concurrency.

## Pros
- Can produce dramatic memory savings specifically when a program genuinely needs to represent very large numbers of objects with substantially shared state.
- Cleanly separates "what's truly unique about this instance" from "what's actually shared," which can clarify a domain model even independent of the memory benefit.
- The factory-enforced pooling makes the sharing explicit and centrally managed, rather than relying on ad hoc, error-prone manual deduplication.

## Cons
- Adds real design complexity (splitting state into two categories, threading extrinsic state through method calls that would otherwise just read an object's own field) that's pure overhead if object count was never actually a memory problem.
- Requires strict immutability discipline on the shared intrinsic state — a single accidental mutation silently corrupts every context sharing that instance, a subtle and hard-to-trace bug class.
- Modern memory capacity and garbage collectors have raised the threshold at which object-count memory pressure actually becomes a real problem — many programs that might have needed Flyweight decades ago no longer do, making the pattern less broadly applicable today than it was when cataloged.

## Alternatives
- **Plain, fully independent objects with no sharing** — simpler, and entirely adequate unless object count and per-object memory footprint genuinely combine into a measured problem; per `code-complete/14`'s measure-first discipline, don't apply Flyweight speculatively.
- **Value objects / structs with automatic sharing via language-level interning** — some languages/runtimes automatically intern certain immutable values (small integers, some strings), achieving a Flyweight-like benefit for those specific types without any explicit pattern implementation.
- **Database/external storage for the shared data, with only a reference/ID held per instance** — for extremely large counts (beyond what even a pooled in-memory Flyweight comfortably handles), offloading shared state entirely to a database or cache, keyed by a shared identifier, rather than keeping even pooled instances in application memory.

## When to use it
Use Flyweight specifically when profiling (per `code-complete/14`'s measure-first discipline) shows that a large number of similar objects is a genuine, measured memory bottleneck, and a meaningful fraction of each object's state is truly shareable (identical across many instances) rather than genuinely unique per instance.

## When NOT to use it
Don't apply Flyweight speculatively "in case memory becomes a problem" for object counts that are actually modest, or where most state genuinely is unique per instance (little to share) — the pattern's complexity cost isn't justified without a measured, real need. Don't use Flyweight if you can't guarantee the shared intrinsic state will remain immutable throughout the program's life.

## Key takeaways / mental model
Before reaching for Flyweight, ask: "have I actually measured that object count is a memory bottleneck, and is a genuinely large fraction of each object's state truly identical across many instances?" If either answer is no, this pattern's complexity isn't earning its keep yet.

## Self-check questions
1. Using the forest-rendering example, explain precisely what memory savings Flyweight provides and why a naive per-tree object wouldn't provide it.
2. Why must Flyweight instances be immutable, and what bug would arise if that discipline were violated?
3. Describe a domain from your own experience with a large number of similar objects where Flyweight might apply, and identify what would be intrinsic versus extrinsic state.
4. Why does the lesson insist you should measure before applying Flyweight, rather than applying it as a default optimization?

## References
- Design Patterns: Elements of Reusable Object-Oriented Software (Gamma, Helm, Johnson, Vlissides), Chapter 4: "Structural Patterns" (Flyweight section).
- See also: `code-complete/14` (Refactoring and Code-Tuning Strategies) for the measure-first discipline this pattern's application should follow.
