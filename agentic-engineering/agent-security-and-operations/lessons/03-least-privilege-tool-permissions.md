---
id: agent-security-and-operations/03
subject: agent-security-and-operations
title: Least-Privilege Tool Permissions and Scoped Credentials
slug: least-privilege-tool-permissions
status: drafted
mastery:
seniority: senior
source: "OWASP GenAI Security Project: Top 10 for LLM Applications 2025, LLM06 Excessive Agency (published 2024-11-18, https://owasp.org/www-project-top-10-for-large-language-model-applications/); Model Context Protocol specification, Authorization (2025-11-25 / 2026-07-28 revisions, https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization); Anthropic, Claude Code Security and Permissions docs (2026, https://code.claude.com/docs/en/security and https://code.claude.com/docs/en/permissions); Cloud Security Alliance Labs, Agentic MCP Security Best Practices Guide v1 (2026, https://labs.cloudsecurityalliance.org/agentic/agentic-mcp-security-best-practices-v1/); RFC 8707, Resource Indicators for OAuth 2.0"
durability: durable
prerequisites: [model-context-protocol/05]
created: 2026-08-10
updated: 2026-08-10
---

# Least-Privilege Tool Permissions and Scoped Credentials

## TL;DR
Because no layer of defense against prompt injection is individually sufficient (`agent-security-and-operations/02`), the layer that matters most is the one that does not depend on the model behaving correctly at all: give an agent only the tools, scopes, and credentials its current task actually requires, so that even a fully "convinced" model - one that has swallowed an injected instruction whole - is structurally unable to do more damage than its narrow privilege allows. This is the classic principle of least privilege from decades of systems security, applied to a new kind of caller: one whose "intent" is inferred from natural language and can be manipulated by an adversary who never touches your infrastructure directly.

## The idea
`agent-security-and-operations/01` and `/02` established that you cannot reliably stop a model from being *convinced* to attempt something malicious - the instruction/data boundary is soft, and defense-in-depth reduces but never eliminates that risk. Least-privilege tool permissions attacks a different variable entirely: instead of trying to stop the model from wanting to do something bad, it makes sure the model's wanting is *irrelevant*, because the tool call it would need to make either doesn't exist in its toolset, doesn't have the scope required, or is fronted by a credential that structurally cannot perform the action requested.

This reframes the entire problem. OWASP's 2025 Top 10 names this failure mode directly as **LLM06: Excessive Agency** and breaks its root cause into three parts: **excessive functionality** (the agent has tools it doesn't need for its actual job - a summarization agent that also happens to have a `delete_record` tool nobody uses), **excessive permissions** (the agent's tools are individually justified, but each one is scoped far beyond what any single task needs - a `read_customer_record` tool that can read *every* customer instead of just the ones relevant to the current ticket), and **excessive autonomy** (the agent can complete high-impact actions without any checkpoint, regardless of whether its permissions are otherwise reasonable). All three are design-time decisions made by the people building the agent, not by the model at runtime - which is exactly why they are fixable in a way that "stop the model from being manipulated" is not.

The mental shift required is the same one distributed-systems security made decades ago with service accounts and API scopes: never ask "can I trust this caller's intent," because you cannot verify intent from natural language reliably; ask instead "what is the smallest set of capabilities this caller needs to do its legitimate job, and can I make everything outside that set structurally unreachable." An agent is just a new, unusually persuadable kind of caller - the same discipline applies, with the added twist that the caller's own judgment about what it needs cannot be trusted as an input to the scoping decision, because that judgment is exactly what an attacker is trying to manipulate.

## How it works

### Scoping along three axes: tools, data, and credentials
Least privilege for an agent is not a single knob; it composes across three independent axes, and a real design should tighten all three, not just one:

- **Tool-level scoping** - which named tools/functions does the agent's toolset even expose. The support-ticket agent from `agent-security-and-operations/01` needed `send_email` for legitimate customer replies; the fix that most directly closed that lesson's attack was never available in that lesson, because it required weighing that legitimate need against the exfiltration risk - this lesson supplies that weighing, below.
- **Scope-level restriction within a tool** - a tool being present does not mean it must be unrestricted. `search_internal_docs` and `read_customer_record` can each be parameterized so the agent can only query records tied to the ticket it is actively handling, not the entire customer database - the same "reduce OAuth scopes to only what's needed, drop write scopes when only read access is required" pattern the Model Context Protocol's 2025-11-25 authorization specification formalizes for MCP servers generally (`model-context-protocol/05` covers the audience-binding and OAuth 2.1 mechanics this rests on).
- **Credential-level binding** - the credential a tool call actually executes against should itself be scoped, short-lived, and revocable, independent of whatever the agent's toolset nominally allows. Even if a tool call somehow escapes its intended scope, a credential that is audience-bound to one specific resource (RFC 8707 resource indicators) and expires in minutes rather than being a long-lived static API key limits the blast radius of any single compromised call.

### Worked example: re-scoping the support-ticket agent from lesson 01
Recall the injected instruction from `agent-security-and-operations/01`: a ticket body containing a fake "SYSTEM NOTE" asking the agent to compile a summary of the last 20 tickets' customer data and email it to an external address. Three least-privilege redesigns, each closing the attack at a different axis, are worth comparing directly:

**Redesign A - tool-level removal.** If the agent's job is strictly "read this one ticket, look up docs relevant to it, draft a reply for a human to send," it never needed `send_email` as an autonomous tool at all - a human sends the actual reply. With `send_email` removed from the toolset entirely, the injected instruction has no tool call available to execute it, regardless of whether the model "believes" the note. This is the strongest fix when the tool genuinely isn't required for the task, but it isn't always available - many real support agents do need to send email autonomously as their core function.

**Redesign B - scope restriction within the tool.** If `send_email` must stay (the agent's actual job is to auto-reply to customers), scope it so it can only send to the email address already on file for *the ticket currently being handled*, never an arbitrary address supplied in tool arguments or inferred from ticket content. The injected instruction's target address (`audit-log@ext-billing-review.example`) does not match ticket #48213's customer record, so a correctly scoped tool rejects the call before it executes - the model can still be "convinced," but the tool it calls refuses to act outside its scope.

**Redesign C - data-access restriction.** Scope `search_internal_docs` and any ticket-lookup tool so a single agent invocation can only see the ticket it was invoked for, never "the last 20 tickets." Even if Redesign B were somehow bypassed, there would be no other customers' data reachable from this invocation's context to exfiltrate in the first place - the tool call to gather it fails structurally.

```
Attack step                    Stopped by
----------------------------   ------------------------------------
call send_email to attacker    Redesign A: tool doesn't exist
                                Redesign B: recipient scope rejects
                                            non-ticket-owner address

call search_internal_docs      Redesign C: scope limited to this
for 20 other customers'                    ticket only, no other
records                                     records reachable
```

None of the three redesigns required detecting the injected text at all - each closes the attack purely by making the tool call the attacker needed structurally unavailable or invalid, which is exactly the property that makes tool-permission scoping the most load-bearing layer in the defense-in-depth stack from `agent-security-and-operations/02`.

### Credential scoping: why the MCP authorization model matters here specifically
`model-context-protocol/05` covered why MCP treats a server as an OAuth 2.1 resource server rather than trusting client-asserted identity, and why tokens are audience-bound via RFC 8707 resource indicators to prevent a token minted for one server being replayed against another. That mechanism is not just an authentication nicety; it is a direct least-privilege control for exactly the agent-security threat model this subject builds. Consider an agent connected to two MCP servers at once - a low-risk documentation-search server and a high-risk CRM server with write access. Under the audience-binding model, a token minted for the documentation server is cryptographically useless if presented to the CRM server, so even if an injected instruction convinces the model to try routing a documentation-server credential at the CRM tool (a confused-deputy attempt), the CRM server's own audience check rejects it. Combine this with per-connection scoped tokens - time-limited, scope-restricted, revocable without needing the agent's cooperation, per current MCP security guidance from the Cloud Security Alliance's 2026 agentic MCP best-practices work - and a compromised or manipulated single tool call has a credential that cannot reach further than the one connection it was minted for, cannot persist past its short expiry, and can be revoked centrally the moment anomalous behavior is detected, all independent of whether the model itself was ever "cured" of the injected instruction.

> **Example (2026):** Anthropic's Claude Code documentation describes permission rules configured per-tool and per-directory (an allow/deny list checked before Bash commands or file edits execute) plus a sandboxed bash tool with filesystem and network isolation - a concrete instance of tool- and scope-level least privilege enforced outside the model. The exact configuration surface (settings files, sandbox boundaries, allow/deny syntax) differs per product; check current vendor documentation for specifics.

### The trade-off least privilege always makes: friction versus safety
Every tightening described above has a real cost. Redesign A (removing `send_email`) means every reply now needs a human in the loop, which is slower and does not scale to high ticket volume - a direct preview of the trade-off `agent-security-and-operations/04` develops fully. Redesign C (scoping data access to one ticket at a time) means the agent cannot spot patterns across tickets that might genuinely be useful (a legitimate fraud-detection use case might want exactly the cross-ticket visibility this redesign removes). Least privilege is not "always scope everything down as far as possible" - it is "scope to the smallest privilege that still lets the agent do its actual, current job," which requires an honest accounting of what the job actually needs, done at design time, before any tool is granted.

## Pros
- Does not depend on the model behaving correctly, unlike input filtering or system-prompt instructions - it closes the attack even when every earlier defense-in-depth layer (`agent-security-and-operations/02`) has already failed.
- Composable across three independent axes (tools, scopes, credentials), so a gap in one axis (an overly broad tool) can still be caught by another (a scoped credential) - genuine defense-in-depth within this single layer, not just a single control.
- Aligns with decades of mature distributed-systems security practice (service accounts, OAuth scopes, short-lived tokens) rather than requiring novel, unproven agent-specific mechanisms - the MCP authorization model (`model-context-protocol/05`) is a direct application of exactly this lineage.

## Cons
- Real engineering cost: defining the minimal scope for every tool and every task shape requires deliberate design work up front, and it is easy to either over-scope out of convenience (grant broad access "just in case") or under-scope in a way that breaks legitimate functionality.
- Scoping has to be revisited every time a new tool, a new task shape, or a new integration is added - permissions drift toward over-broad by default unless someone actively audits and tightens them, the same "permission creep" problem that afflicts human access control in any organization.
- Very tight scoping can force more human-in-the-loop checkpoints or reduce what the agent can accomplish autonomously, directly trading capability and speed for safety - a trade-off that has to be made deliberately, not avoided by scoping everything maximally loose "to keep things simple."

## Alternatives
- **Trust-the-model / instruction-only defenses** — relying on system-prompt instructions and the model's trained preference for developer content, covered and rejected as insufficient on their own in `agent-security-and-operations/01` and `/02`; least-privilege scoping is what those lessons point to as the more durable layer.
- **Human-in-the-loop approval on every action** — instead of scoping what the agent *can* do, require a human to approve every attempt regardless of scope; more conservative than least privilege alone, but does not scale and is the subject of its own trade-offs in `agent-security-and-operations/04` - often used *together* with least privilege (approval gates specifically on the narrow set of high-impact actions that remain in scope) rather than as a replacement for it.
- **Post-hoc monitoring and revocation** — grant broad access but detect and shut down misuse after the fact via anomaly monitoring and audit logs; catches damage after it starts rather than preventing it, and is a reasonable complement to least privilege (per `agent-security-and-operations/02`'s output-monitoring layer) but a poor substitute for not granting the excess access in the first place.

## When to use it
Apply least-privilege scoping to every agent that holds any tool with real-world side effects (sending data, spending money, modifying or deleting records) - which, per `agent-security-and-operations/01`, is exactly the population of agents where the lethal trifecta and indirect injection risk actually bite. Scope at design time, before the agent ships, and re-scope every time a new tool or a broader task shape is added.

## When NOT to use it
An agent with genuinely no side-effecting tools (pure question-answering over a fixed, trusted knowledge source) gains little from elaborate credential scoping, since there is no privileged action to restrict - proportionate effort here is minimal. Be wary, though, of "we'll scope it later once we see what it actually needs" as a permanent policy for a production agent with real tool access; that ordering inverts the security benefit, since the gap between shipping with broad access and later tightening it is exactly the window where excessive agency (LLM06) causes real damage.

## Key takeaways / mental model
Stop asking whether the model can be trusted to want the right thing - per `agent-security-and-operations/01` and `/02`, you cannot fully answer that question, and betting the agent's safety on the answer being "yes" is the mistake. Ask instead, for every tool, every scope, and every credential: "if this exact call were made by a fully compromised, adversarially-controlled process, what is the worst it could do?" Then shrink that worst case to the smallest footprint that still lets the agent do its actual job - across tools (does it even need this?), scopes (does it need *all* of this, or just the slice relevant to its current task?), and credentials (is this bound tightly enough that a leak or a misdirected call can't reach further than intended?). This is the layer that holds even when every earlier layer has already failed.

## Self-check questions
1. Using the three-redesign worked example, explain which axis of scoping (tool-level, scope-level, or credential-level) would be the *only* one still standing if an attacker somehow obtained a valid, unexpired MCP credential for the CRM server directly - and what that implies about needing more than one axis scoped at once.
2. OWASP's LLM06 splits excessive agency into excessive functionality, excessive permissions, and excessive autonomy. Give one concrete example of each, distinct from this lesson's worked example, drawn from a different kind of agent (e.g., a coding agent or a research agent).
3. A teammate argues "we should just grant our agent broad access now and tighten it later once we understand real usage patterns." Using this lesson's account of what least privilege actually defends against, explain what window of risk that ordering creates and why it matters more for an agent than for a typical human employee's access request.
4. Explain, using RFC 8707 audience binding from `model-context-protocol/05`, why a stolen or misdirected credential scoped to one MCP server is not automatically useful against a second MCP server the same agent is also connected to.
5. Design a least-privilege tool/scope/credential plan for a coding agent whose job is "open pull requests that fix flaky tests, for a human to review and merge." What tools does it need, what should each be scoped to, and what should it explicitly not be able to do on its own?

## References
- [OWASP GenAI Security Project, Top 10 for LLM Applications 2025 (PDF)](https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf), published 2024-11-18 (LLM06: Excessive Agency)
- [Model Context Protocol specification, Authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization), 2025-11-25 revision
- [Anthropic, Claude Code Security documentation](https://code.claude.com/docs/en/security), 2026
- [Cloud Security Alliance Labs, Agentic MCP Security Best Practices Guide v1](https://labs.cloudsecurityalliance.org/agentic/agentic-mcp-security-best-practices-v1/), 2026
- RFC 8707, Resource Indicators for OAuth 2.0
- `model-context-protocol/05`, Authorization and Statelessness in Agent Protocols (companion lesson on the OAuth 2.1 / audience-binding mechanics this lesson builds on)
