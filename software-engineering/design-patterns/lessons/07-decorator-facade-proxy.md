---
id: design-patterns/07
subject: design-patterns
title: "Structural: Decorator, Facade, Proxy"
slug: decorator-facade-proxy
status: drafted
mastery:
seniority: mid
source: Design Patterns (Gamma, Helm, Johnson, Vlissides), Chapter 4
prerequisites: [design-patterns/06]
created: 2026-08-10
updated: 2026-08-10
---

# Structural: Decorator, Facade, Proxy

## TL;DR
Decorator adds behavior to an individual object at runtime by wrapping it in a same-interface layer, without subclassing and without affecting other instances of the same class. Facade provides one simple, high-level interface over a complex set of subsystems, hiding their internal complexity from most callers. Proxy stands in for another object, controlling access to it — for lazy loading, access control, remote communication, or caching — while presenting the same interface as the real object.

## The idea
All three wrap or stand in front of another object, but for three different reasons: Decorator wraps to *add behavior* on top of what's already there; Facade wraps a whole *subsystem* to make it simpler to use; Proxy wraps a single object to *control access* to it, transparently to the caller.

## How it works

### Decorator — add behavior without subclassing, composably
Instead of creating a new subclass for every combination of optional behavior (echoing Bridge's combinatorial-explosion problem, `design-patterns/06`), Decorator wraps an object in another object implementing the *same* interface, adding behavior before/after delegating to the wrapped object — and decorators can be stacked, combining behaviors freely at runtime.

**Worked example.**
```
class Coffee:
    def cost(self) -> float: raise NotImplementedError

class SimpleCoffee(Coffee):
    def cost(self): return 2.0

class MilkDecorator(Coffee):
    def __init__(self, coffee: Coffee): self.coffee = coffee
    def cost(self): return self.coffee.cost() + 0.5

class SyrupDecorator(Coffee):
    def __init__(self, coffee: Coffee): self.coffee = coffee
    def cost(self): return self.coffee.cost() + 0.3

order = SyrupDecorator(MilkDecorator(SimpleCoffee()))
order.cost()  # 2.8 — milk and syrup added, in the order wrapped, no MilkSyrupCoffee subclass needed
```
Adding a third topping doesn't require a new `MilkSyrupWhippedCreamCoffee` subclass — it's just another decorator wrapped around the existing chain, composed at runtime, for exactly one specific order, without affecting any other `Coffee` instance elsewhere in the system.

### Facade — one simple interface over a complex subsystem
When a subsystem has many classes with intricate interactions (a multi-step video-encoding pipeline, an operating-system-level API with dozens of calls needed for one common task), Facade provides a single, simplified entry point covering the common cases, without removing the ability to reach the subsystem's full API directly for callers who genuinely need that level of control.

**Worked example.**
```
class VideoConverterFacade:
    def convert_to_mp4(self, input_path):
        codec = CodecFactory.get_codec(input_path)
        decoder = Decoder(codec)
        raw_frames = decoder.decode(input_path)
        encoder = Mp4Encoder(bitrate=DEFAULT_BITRATE)
        return encoder.encode(raw_frames)

# caller — one call, no need to know about codecs, decoders, or encoders directly:
VideoConverterFacade().convert_to_mp4("input.mov")
```
Most callers never need `CodecFactory`, `Decoder`, or `Mp4Encoder` directly — the Facade hides that whole subsystem behind one call, directly reducing cognitive load (`code-complete/02`) for the common case, while the underlying classes remain available for callers with genuinely advanced needs the Facade doesn't cover.

### Proxy — a stand-in that controls access, transparently
Proxy implements the *same interface* as a "real" object it represents, but adds a layer of control around access to that real object — the caller can't tell the difference between talking to the proxy and talking to the real thing, which is precisely the point.

Several distinct, named sub-kinds of Proxy address different needs:
- **Virtual Proxy** — defers creating an expensive real object until it's actually needed (lazy loading). A document viewer might use a virtual proxy for embedded images, only actually loading pixel data from disk the first time the image is scrolled into view, not when the document first opens.
- **Protection Proxy** — checks access permissions before forwarding a call to the real object, without the real object itself needing any awareness of the access-control logic.
- **Remote Proxy** — represents an object that lives in a different process or on a different machine, hiding the network communication behind a normal-looking local method call (the basis of many RPC frameworks — see `architecture/distributed-systems`).
- **Caching Proxy** — intercepts calls, returns a cached result when available, and only forwards to the real object on a cache miss, entirely transparent to the caller.

**Worked example (Virtual Proxy).**
```
class Image:
    def render(self): raise NotImplementedError

class RealImage(Image):
    def __init__(self, path):
        self.pixels = load_from_disk(path)  # expensive, happens at construction
    def render(self): display(self.pixels)

class LazyImageProxy(Image):
    def __init__(self, path):
        self.path = path
        self._real_image = None
    def render(self):
        if self._real_image is None:                      # deferred until first actual use
            self._real_image = RealImage(self.path)
        self._real_image.render()
```
Callers hold a `LazyImageProxy` exactly as if it were a `RealImage` — the expensive disk load only happens on the first genuine `render()` call, not eagerly at construction, with zero change needed to any calling code.

### Distinguishing the three from each other, and from Adapter (`design-patterns/06`)
A quick disambiguation, since all four wrapping-style patterns can superficially look similar in code: Adapter changes the *interface* to match what a caller expects (translation); Decorator keeps the *same* interface but *adds* behavior; Facade simplifies access to *many* classes behind one interface; Proxy keeps the *same* interface as one specific object and controls *access* to it. The structural code often looks nearly identical (a class implementing an interface, holding a reference to another object) — the distinguishing factor is always **intent**, echoing `design-patterns/01`'s point that a pattern is defined by the problem it solves, not by its code shape alone.

## Pros
- Decorator composes behavior flexibly at runtime, per-instance, without the subclass explosion a fixed inheritance hierarchy would require.
- Facade meaningfully reduces the cognitive load (`code-complete/02`) of using a complex subsystem for its common cases, without removing advanced access for callers who need it.
- Proxy transparently adds cross-cutting concerns (laziness, access control, caching, remote communication) without the real object or its callers needing any awareness of that added behavior.

## Cons
- Long decorator chains can become hard to reason about and debug — tracing a bug through five stacked decorators requires stepping through each layer.
- A Facade can become a de facto "god object" if it accumulates convenience methods for every possible use case over time, drifting toward the low-cohesion problem `clean-code/10` warns about.
- Proxy's core value (transparency) is also a risk: a caller genuinely unaware they're talking to a Remote Proxy might not account for network failure modes a purely local call would never have, an instance of the "leaky abstraction" concern `clean-code/06` and `architecture/distributed-systems`'s fallacies-of-distributed-computing lesson both raise.

## Alternatives
- **Mixins/traits** — an alternative way to compose behavior onto a class, applied at class-definition time rather than Decorator's runtime, per-instance composition — different trade-off (compile-time, whole-class vs. runtime, per-instance).
- **Middleware/interceptor chains** (common in web frameworks) — a related, framework-level generalization of the Decorator idea, applied specifically to request/response processing pipelines.
- **AOP (Aspect-Oriented Programming)** — a more systemic alternative to Proxy for injecting cross-cutting concerns (logging, transactions, access control) across many classes at once, rather than wrapping one object at a time.

## When to use it
Use Decorator when you need to add optional, combinable behavior to individual instances without a subclass explosion. Use Facade when a subsystem's full complexity is overkill for the common case most callers actually need. Use Proxy when you need to transparently control access to an object — deferring its creation, checking permissions, caching, or bridging a remote boundary — without callers needing to know.

## When NOT to use it
Don't stack more than a few decorators without a very clear reason — deep decorator chains hurt debuggability disproportionately to the flexibility gained. Don't let a Facade absorb every possible convenience method over time without checking whether it's still cohesively "one simple entry point" or has become an unmanaged catch-all. Don't use a transparent Proxy (especially Remote Proxy) if the underlying operation's failure modes are meaningfully different from a normal local call and callers genuinely need to know that distinction to handle errors correctly.

## Self-check questions
1. Using the coffee example, explain why Decorator avoids the subclass explosion that a fixed inheritance hierarchy of topping combinations would require.
2. Give an example of a Facade from a library or framework you've used, and describe what subsystem complexity it hides.
3. Name the specific kind of Proxy (Virtual, Protection, Remote, or Caching) that would best solve each of these: (a) lazy-loading a large file, (b) restricting who can call a delete operation, (c) calling a service on another server.
4. Explain, in your own words, how Decorator and Proxy can look nearly identical in code but differ in intent.

## References
- Design Patterns: Elements of Reusable Object-Oriented Software (Gamma, Helm, Johnson, Vlissides), Chapter 4: "Structural Patterns" (Decorator, Facade, Proxy sections).
