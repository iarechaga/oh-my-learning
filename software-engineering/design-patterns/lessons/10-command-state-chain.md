---
id: design-patterns/10
subject: design-patterns
title: "Behavioral: Command, State, Chain of Responsibility"
slug: command-state-chain
status: drafted
mastery:
seniority: senior
source: Design Patterns (Gamma, Helm, Johnson, Vlissides), Chapter 5
prerequisites: [design-patterns/09]
created: 2026-08-10
updated: 2026-08-10
---

# Behavioral: Command, State, Chain of Responsibility

## TL;DR
Command turns a request (an action plus its parameters) into a standalone object, enabling queuing, logging, undo, and decoupling the invoker from the receiver. State lets an object change its behavior entirely by swapping its internal state object, replacing a large conditional with polymorphism. Chain of Responsibility passes a request along a chain of potential handlers until one handles it, decoupling the sender from knowing which handler will actually process it.

## The idea
These three patterns each turn something usually implicit — an action, a mode, a decision about who's responsible — into an explicit, first-class object. That reification is the common thread: once "add this item," "editing mode," or "who should handle this" becomes an object rather than a hardcoded piece of control flow, it can be stored, passed around, composed, and varied in ways that wouldn't be possible if it stayed implicit in the code's structure.

## How it works

### Command — reify a request as an object
Instead of directly calling a method to perform an action, wrap the action (and everything needed to perform it — the receiver, the parameters) in a Command object with a standard `execute()` method. The object issuing the request (the invoker) doesn't need to know anything about what the command actually does or which receiver it affects.

**Worked example — enabling undo, which direct method calls can't do for free:**
```
class Command:
    def execute(self): raise NotImplementedError
    def undo(self): raise NotImplementedError

class AddTextCommand(Command):
    def __init__(self, document, text):
        self.document, self.text = document, text
    def execute(self): self.document.append(self.text)
    def undo(self): self.document.remove(self.text)

class CommandHistory:
    def __init__(self): self.history = []
    def execute(self, command: Command):
        command.execute()
        self.history.append(command)
    def undo_last(self):
        if self.history: self.history.pop().undo()

history = CommandHistory()
history.execute(AddTextCommand(doc, "hello"))
history.undo_last()   # generic, works for ANY command type, because Command objects carry their own undo logic
```
`CommandHistory` implements undo/redo generically, for *any* current or future command type, because each command carries its own execution and reversal logic — this genericity would be far harder to achieve if actions were just direct method calls with no object representing them, since there'd be nothing to store in a history list in the first place.

### State — swap an object's behavior by swapping its internal state object
When an object's behavior depends heavily on a "mode" or "status" it's in, and every method must check that mode with conditionals (`if self.state == "editing": ... elif self.state == "readonly": ...`), State replaces the conditional-checking with polymorphism: each mode becomes its own class implementing a shared interface, and the object delegates to whichever state object it currently holds — directly echoing `clean-code/12`'s "repeated conditional type-checking suggests missing polymorphism" smell, applied specifically to *mode/status* rather than *type*.

**Worked example.**
```
class DocumentState:
    def edit(self, doc, text): raise NotImplementedError

class DraftState(DocumentState):
    def edit(self, doc, text): doc.content += text

class PublishedState(DocumentState):
    def edit(self, doc, text): raise PermissionError("cannot edit a published document")

class Document:
    def __init__(self):
        self.state: DocumentState = DraftState()
        self.content = ""
    def edit(self, text): self.state.edit(self, text)
    def publish(self): self.state = PublishedState()   # behavior changes entirely by swapping state
```
`Document.edit()` never checks "what mode am I in" via a conditional — it delegates entirely to whichever `DocumentState` object it currently holds, and `publish()` changes the document's entire behavior with one line (swapping the state object), rather than needing to update a scattered set of mode-checking conditionals across every method.

### Chain of Responsibility — pass a request along a chain until someone handles it
When several objects could potentially handle a request, and which one actually will isn't known (or fixed) in advance, Chain of Responsibility links them in a sequence: each handler either processes the request or passes it to the next handler in the chain, and the sender only needs a reference to the *first* handler, with no knowledge of the full chain or which link will ultimately handle it.

**Worked example.**
```
class SupportHandler:
    def __init__(self, next_handler=None): self.next = next_handler
    def handle(self, ticket):
        if self.can_handle(ticket):
            self.resolve(ticket)
        elif self.next:
            self.next.handle(ticket)
        else:
            raise Exception("no handler available")

class Tier1Support(SupportHandler):
    def can_handle(self, ticket): return ticket.severity == "low"
    def resolve(self, ticket): print("resolved by Tier 1")

class Tier2Support(SupportHandler):
    def can_handle(self, ticket): return ticket.severity == "medium"
    def resolve(self, ticket): print("resolved by Tier 2")

chain = Tier1Support(next_handler=Tier2Support())
chain.handle(some_ticket)   # caller has no idea, and doesn't need to know, which tier actually resolves it
```
The caller submits a ticket to the *chain*, not to a specific tier — adding a `Tier3Support` handler, or reordering the chain, requires no change at all to the code that submits tickets, only to how the chain is assembled at the composition root (echoing `clean-code/11`).

## Pros
- Command enables generic undo/redo, request queuing/logging, and full decoupling of invoker from receiver, none of which are achievable with plain, un-reified method calls.
- State eliminates scattered mode-checking conditionals, isolating each mode's behavior into its own class and making adding a new mode a matter of adding one class, not editing every conditional.
- Chain of Responsibility decouples a sender from needing to know which specific handler (if any) will process a request, and lets the chain's composition change independently of the sending code.

## Cons
- Command adds a class per distinct action, which is disproportionate overhead for simple, one-off actions with no genuine need for undo, logging, or queuing.
- State can obscure the full picture of "what are all the possible modes and how do they relate" if the state classes are scattered and not clearly organized together, compared to a single (if messier) conditional block a reader could scan in one place.
- Chain of Responsibility offers no guarantee a request will actually be handled by *anyone* if the chain is misconfigured or incomplete — a silent-failure risk that requires deliberate handling (e.g., a final catch-all handler) to avoid.

## Alternatives
- **Direct method calls with a manually-implemented undo stack** (storing enough state to reverse an action, without a full Command object) — simpler for a small, fixed set of actions where genericity across action types isn't needed.
- **A single dispatch table/dictionary mapping mode to behavior**, instead of full State-pattern classes — sometimes a lighter-weight way to replace mode-checking conditionals when the behavior per mode is simple enough not to need a full class.
- **Middleware pipelines** (a common web-framework generalization of Chain of Responsibility) — apply the same "pass along until handled" idea specifically to request/response processing, often with a more structured, framework-provided registration mechanism than a hand-rolled chain.

## When to use it
Use Command when you need undo/redo, action queuing, logging of executed actions, or full decoupling between something triggering an action and something performing it. Use State when an object's behavior is heavily conditioned on a mode that changes over its lifetime and mode-checking conditionals are scattered across several methods. Use Chain of Responsibility when several handlers could potentially process a request and the sender shouldn't need to know which one will.

## When NOT to use it
Don't wrap simple, one-off actions in full Command objects if there's no real need for undo, queuing, or decoupling beyond what a direct method call already provides. Don't apply State if an object only has two simple, rarely-changing modes where a single boolean check is clearer than a full class hierarchy. Don't use Chain of Responsibility if there's really only ever one fixed, known handler — that's just a direct call with extra indirection.

## Key takeaways / mental model
Ask: "would I benefit from treating this action as a storable, passable object (Command)? Is this object's behavior scattered across mode-checking conditionals that polymorphism could replace (State)? Do I have several potential handlers where the sender genuinely shouldn't need to know which one applies (Chain of Responsibility)?"

## Self-check questions
1. Using the `CommandHistory` example, explain specifically why undo/redo would be much harder to implement generically without reifying actions as Command objects.
2. Rewrite the `Document` state-machine example using a single conditional-based approach instead of State, and identify what becomes harder to extend.
3. Give an example from your own domain where Chain of Responsibility would be appropriate, and explain what would go wrong if the sender had to know the full handler chain directly.
4. Describe a situation where introducing Command would be clear overkill for a simple action.

## References
- Design Patterns: Elements of Reusable Object-Oriented Software (Gamma, Helm, Johnson, Vlissides), Chapter 5: "Behavioral Patterns" (Command, State, Chain of Responsibility sections).
