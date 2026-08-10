---
id: enterprise-patterns/11
subject: enterprise-patterns
title: "Web Presentation (MVC, Page/Front Controller)"
slug: web-presentation
status: drafted
mastery:
seniority: mid
source: Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 4
prerequisites: [enterprise-patterns/03]
created: 2026-08-10
updated: 2026-08-10
---

# Web Presentation (MVC, Page/Front Controller)

## TL;DR
Model-View-Controller separates the domain's data/logic (Model), how it's displayed (View), and how user input is handled and translated into calls on the Model (Controller) — the specific, historically foundational Presentation-layer (`enterprise-patterns/01`) pattern nearly every web framework builds on. Page Controller has one controller per web page/action; Front Controller routes every request through one central entry point, which is friendlier to cross-cutting concerns (authentication, logging) applied uniformly.

## The idea
`enterprise-patterns/01` established that Presentation is one of the three fundamental layers, and this lesson gives its most historically influential, still near-universal internal structure: MVC, plus a specific, consequential choice about *how requests get routed to the right controller logic* in the first place (Page Controller versus Front Controller).

## How it works

### MVC — the three roles, precisely
- **Model** — the domain data and logic (an Order, a Customer, the business rules governing them) — corresponds directly to this subject's earlier Domain-layer lessons (`enterprise-patterns/02`-`03`). The Model should know nothing about how it's displayed.
- **View** — responsible purely for rendering the Model's data into a specific output format (HTML, JSON, a PDF) — should contain minimal logic beyond formatting/display decisions, echoing `clean-architecture/09`'s Humble Object pattern directly: the View is the "humble," barely-tested side, deliberately kept free of substantial logic.
- **Controller** — receives user input (an HTTP request, a form submission), decides what it means in terms of the Model (which Use Case/Service Layer call to make, per `enterprise-patterns/03`), invokes it, and selects which View should render the result.

**Why the separation matters practically.** Without this separation, a single piece of code handling a web request often ends up doing all three jobs entangled together — parsing input, deciding business logic, and generating HTML output all in one function. This makes it hard to reuse the same business logic for a different View (a JSON API alongside an HTML page) or to test the business logic without simulating an HTTP request and parsing HTML output — directly the same coupling problem `clean-architecture/11`'s "the web is a detail" argument names, here addressed at the finer grain of how the Presentation layer itself is internally organized.

### Page Controller — one controller per page/action
Each distinct page or URL/action has its own dedicated controller class or function, directly responsible for handling that specific request.

```
class ShowOrderController:
    def handle(self, request):
        order = order_service.find(request.params["id"])
        return OrderView.render(order)

class SubmitOrderController:
    def handle(self, request):
        result = order_service.place_order(request.form_data)
        return ConfirmationView.render(result)
```
**Trade-off**: simple, direct, easy to understand for any single page in isolation (echoing Transaction Script's `enterprise-patterns/02` simplicity trade-off, applied to controllers specifically) — but cross-cutting concerns that should apply to *every* request (authentication checks, logging, a consistent error-handling format) must be individually added to every single Page Controller, risking duplication or, worse, an easily-forgotten omission on some new controller.

### Front Controller — one central entry point for every request
A single, central controller receives *every* incoming request, and is responsible for common preprocessing (authentication, logging, request parsing) before dispatching to whatever specific handler logic the request actually needs.

```
class FrontController:
    def handle(self, request):
        authenticate(request)           # applied ONCE, uniformly, to every request
        log_request(request)
        handler = self.route(request.path)   # dispatch to the specific logic needed
        return handler.execute(request)
```
**Trade-off**: cross-cutting concerns are guaranteed to apply uniformly to every request, since they live in the one shared entry point rather than needing to be repeated in every individual page-specific controller — but the Front Controller itself, and its routing mechanism, can become a complex piece of infrastructure in its own right, and understanding "what happens when a request comes in" now requires tracing through the Front Controller's dispatch logic rather than reading one self-contained Page Controller directly.

### Why nearly every modern web framework uses Front Controller
Almost every mainstream web framework today (Django, Rails, Spring, Express) implements Front Controller as its core request-handling mechanism, with individual "controllers"/"views"/"handlers" the framework then dispatches to — meaning most developers today interact with a *framework-provided* Front Controller and rarely need to build the pattern from scratch, but understanding it explains *why* frameworks are structured the way they are (a central routing table, middleware/filter chains for cross-cutting concerns applied uniformly) rather than each individual page handling its own authentication and logging independently.

## Pros
- MVC's separation lets the same Model/business logic be reused by multiple Views (an HTML page and a JSON API), and lets business logic be tested without simulating a full HTTP request/response cycle.
- Front Controller guarantees cross-cutting concerns apply uniformly to every request, eliminating the risk of forgetting to add authentication or logging to some new Page Controller.
- Both patterns are foundational to nearly every modern web framework, so understanding them explains a huge amount of how real-world web development infrastructure is actually organized.

## Cons
- MVC's View should stay logic-light (Humble Object, `clean-architecture/09`), but the discipline to actually keep it that way — resisting the temptation to add "just a little" business logic directly in a template — requires ongoing vigilance.
- Page Controller's simplicity comes at the cost of duplicating cross-cutting concerns across every controller, or risking an inconsistently-applied concern if some controller is missed.
- Front Controller's central dispatch mechanism, while solving the cross-cutting-concern problem, becomes its own piece of nontrivial infrastructure that needs to be well-understood — debugging routing issues requires tracing through the Front Controller's logic specifically.

## Alternatives
- **Model-View-Presenter (MVP)** and **Model-View-ViewModel (MVVM)** — related UI-architecture patterns, common especially in desktop and mobile application development, that further refine the split between View and the logic that populates it, addressing some of MVC's ambiguity about exactly how much logic a "Controller" should hold.
- **Server-rendered templates with embedded logic** (no formal MVC separation) — simpler for genuinely small, simple sites, at the cost of the reuse and testability problems MVC's separation specifically addresses.
- **API-first architectures with a thin, framework-provided Front Controller and no server-rendered Views at all** — increasingly common in modern web development, where the "View" role shifts entirely to a separate client-side application consuming a JSON API, with the server-side Presentation layer reduced mostly to Controller and Model concerns.

## When to use it
Use MVC's separation for any web (or similarly interactive) application with meaningful business logic that should be reusable and independently testable from its presentation. Use Front Controller (in practice, almost always via an existing framework) whenever cross-cutting concerns need to apply consistently across many different pages/endpoints.

## When NOT to use it
Don't force a heavy, formal MVC structure onto a genuinely tiny, single-page, logic-free display of static content, where the separation provides negligible benefit. Don't hand-roll a custom Front Controller when an existing, mature web framework already provides one — reserve custom infrastructure work for genuinely unusual routing/dispatch needs a framework doesn't handle well.

## Key takeaways / mental model
For any Presentation-layer code, ask: "is this deciding what to do (Controller), computing/holding data (Model), or just formatting output (View)?" Keep those three questions answered by different pieces of code. And ask whether a given concern (auth, logging) needs to apply uniformly everywhere — if so, it belongs in your Front Controller's shared dispatch path, not repeated in every individual page handler.

## Self-check questions
1. Using the `ShowOrderController` example, explain what would need to change to reuse the same underlying business logic for a JSON API endpoint instead of an HTML page.
2. Describe a cross-cutting concern (beyond authentication and logging) that would be easy to forget under Page Controller but guaranteed under Front Controller.
3. Why does nearly every modern web framework implement Front Controller internally, and what do individual "controllers" in such a framework actually correspond to in this pattern's terms?
4. Give an example of business logic leaking into a View (a template) that you've seen in real code, and explain what moving it to the Model or Controller would look like.

## References
- Patterns of Enterprise Application Architecture (Martin Fowler), Chapter 4: "Web Presentation" (Model View Controller, Page Controller, and Front Controller sections).
