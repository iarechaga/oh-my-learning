# Seeking SRE

A comprehensive recap of *Seeking SRE* (David Blank-Edelman, ed.), concept by concept.
This subject takes classic SRE mechanics (`sre/*`: SLOs, error budgets, on-call,
postmortems) and asks how they hold up outside Google's specific scale — different
company sizes, team shapes, regulatory contexts, and human systems. It reads best after
at least `sre/03`, `sre/04`, `sre/08`, and `sre/10`, since this subject adapts rather
than reintroduces that baseline mechanics.

Progress note: all 12 lessons are `drafted`; none have been discussed yet, so mastery
is pending across the board and no weak spots are recorded yet. This page will gain
depth (especially on the concepts the learner finds hard) as discussions happen - the
last section below will fill in from discussion records.

See the progress table in [README.md](README.md). Reading order is top to bottom:
adoption and ownership choices first, then incident-response and cultural maturity,
then organizational-scaling and strategic concerns.

## Adaptation choices: models and ownership

- **[seeking-sre/01] Choosing an SRE adoption model for your organization** - SRE is a
  practice set separable from Google's specific org chart; pick among embedded,
  centralized/platform, consulting/enablement, or hybrid models based on current
  headcount and service count, and revisit the choice as the company grows.
  ([lesson](lessons/01-sre-adoption-models.md))
- **[seeking-sre/02] Defining reliability ownership between product and platform teams**
  - most real incidents live in a contested middle zone between clearly-product and
  clearly-platform; resolve it in advance with a written interface contract (committed
  SLOs, required notice) rather than arguing live during an outage.
  ([lesson](lessons/02-reliability-ownership-models.md))

## Human and cultural practices

- **[seeking-sre/03] Evolving incident response maturity over time** - a four-stage
  ladder (founder/hero-led, ad hoc on-call, structured rotation with runbooks, measured
  and continuously improving); the common mistakes are staying in an early stage too
  long or importing a later stage's heavyweight process before the org is ready for it.
  ([lesson](lessons/03-incident-response-maturity.md))
- **[seeking-sre/04] Building sustainable on-call culture and boundaries** - sustainable
  on-call is about pager load per person, not just having a rotation; track pages per
  shift explicitly, and use toil reduction, rotation widening, or scope narrowing when
  headcount can't grow to meet Google-scale target ratios.
  ([lesson](lessons/04-on-call-culture-boundaries.md))
- **[seeking-sre/05] Psychological safety and blameless reliability culture** - a
  blameless postmortem template is not the same as a blameless culture; genuine safety
  is a track record built through costly, credible signals (leadership disclosing their
  own mistakes, live language redirection, root-cause analysis that never terminates at
  a person's name) that has to survive a real, expensive test.
  ([lesson](lessons/05-psychological-safety-blamelessness.md))
- **[seeking-sre/06] Reliability communication with executives and stakeholders** -
  error budgets only govern release decisions if the people who can override them
  understand the trade-off in business vocabulary (revenue, risk, precedent), not
  engineering vocabulary (SLOs, budget percentages); build a standing translation habit
  and a recurring, proactive reliability review.
  ([lesson](lessons/06-reliability-stakeholder-communication.md))

## Scaling the organization

- **[seeking-sre/07] Hiring and developing SRE capabilities** - Google's hiring bar
  assumes a talent pipeline most companies lack; the higher-leverage move at smaller
  scale is growing SRE capability from engineers who already have deep system context,
  reserving external hiring for genuinely rare, hard-to-build expertise.
  ([lesson](lessons/07-hiring-developing-sre.md))
- **[seeking-sre/08] Managing toil at organizational scale** - a 5-person team can't
  afford Google's comprehensive-automation approach to toil; triage by
  frequency-times-fix-cost, prefer 80%-effective "good enough" fixes over full
  automation, and keep an explicit, revisited list of toil the team is knowingly
  tolerating. ([lesson](lessons/08-org-scale-toil-management.md))
- **[seeking-sre/09] Embedding reliability in product planning and prioritization** -
  reliability structurally loses feature-by-feature prioritization fights because its
  payoff (incidents that didn't happen) is invisible; fix the structure with reserved
  roadmap capacity, error-budget-linked scheduling rules, or joint OKRs, not by winning
  the argument harder. ([lesson](lessons/09-reliability-in-product-planning.md))

## Strategic and long-horizon concerns

- **[seeking-sre/10] Reliability in regulated and high-risk environments** - finance,
  healthcare, and similar contexts need explicit modifications, not abandonment, of SRE
  defaults: a compliance floor beneath the normal error budget, a structurally separate
  factual accountability record alongside the blameless postmortem, and extra rigor on
  toil and escalation for compliance-tier functions.
  ([lesson](lessons/10-reliability-regulated-environments.md))
- **[seeking-sre/11] Measuring SRE program impact and organizational health** - raw
  uptime is a weak, gameable single metric; triangulate outcome metrics (SLO attainment
  trend), process-health metrics (postmortem completion, pager load), and leading
  indicators (near-miss reporting, toil trend) to tell whether a program is durably
  working or just producing a good-looking number.
  ([lesson](lessons/11-sre-program-impact.md))
- **[seeking-sre/12] The future of SRE as a socio-technical discipline** - as SRE spreads
  beyond hyperscale companies and into new technical domains (ML, data pipelines,
  agentic systems), its durable core is not any specific practice but the underlying
  socio-technical principles (systemic root causes, sustainability, visibility, explicit
  trade-offs) that every adaptation in this subject has been an instance of.
  ([lesson](lessons/12-future-of-sre.md))

## Focus areas (aggregated weak spots)

None yet - discussions have not started for this subject.
