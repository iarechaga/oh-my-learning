---
id: sre/07
subject: sre
title: Monitoring and Alerting Design for Actionable Signals
slug: monitoring-alerting
status: drafted
mastery:
seniority: senior
source: Site Reliability Engineering (Beyer, Jones, Petoff, Murphy), Chapter 6 and 10
prerequisites: [sre/02, sre/04]
created: 2026-08-10
updated: 2026-08-10
---

# Monitoring and Alerting Design for Actionable Signals

## TL;DR
Good monitoring answers "what's broken and why" using a small set of symptom-based signals — the four golden signals: latency, traffic, errors, and saturation — rather than paging on every internal metric that moves. Good alerting fires only when a human must act *right now*, because every false or non-actionable page trains on-call engineers to distrust and eventually ignore the pager, which is more dangerous than having no alert at all.

## The idea
It's trivial to instrument a system to emit thousands of metrics — every queue depth, every cache hit ratio, every thread pool size. The hard problem monitoring actually needs to solve is much narrower: with limited human attention (especially at 3am), which small number of signals tell you the system is failing its users *right now*, and which of those failures require a human to act immediately versus one that can wait for business hours or resolve itself?

The book's core distinction is between **symptoms** (what the user is experiencing — e.g., elevated error rate, slow responses) and **causes** (why — e.g., a specific database shard is overloaded, a bad config was pushed). Alerting should page on symptoms, because symptoms are what determine whether users are actually being hurt, and there are combinatorially fewer symptom-alerts than there are possible causes. Causes are for debugging *after* a symptom-alert fires, using dashboards and logs, not for generating separate pages of their own.

## How it works

### The four golden signals
The book's compact framework for what to monitor on any user-facing service:
1. **Latency** — the time to service a request. Crucially, split successful-request latency from failed-request latency (a fast error and a slow success are very different signals mixed together in one average would hide each).
2. **Traffic** — demand on the system, measured in a domain-relevant unit (HTTP requests/second, transactions/second, concurrent streaming sessions).
3. **Errors** — the rate of requests that fail, explicitly or implicitly (e.g., a 200-status response containing the wrong content is an implicit error the raw status-code count would miss).
4. **Saturation** — how "full" the service is relative to its resource limits (memory, CPU, I/O, or a more service-specific constraint like available connection-pool slots); the signal that predicts future degradation before it becomes a current error.

**Worked example.** A checkout API's golden-signal dashboard: latency (p50 = 40ms, p99 = 380ms), traffic (2,400 requests/sec, typical for this time of day), errors (0.02% 5xx rate), saturation (application server pool at 62% of max connections, database connection pool at 71%). None of these individually might be alarming, but if saturation on the DB connection pool trends from 71% to 95% over 10 minutes while traffic stays flat, that's a leading indicator (rising saturation with flat traffic implies something is holding connections longer than usual, e.g., a slow query) worth investigating before it becomes a user-facing error spike.

### Multi-window, multi-burn-rate alerting on error budgets
The most refined alerting technique in the book ties alerts directly to error-budget consumption rate (`sre/04`) rather than a fixed threshold. A "burn rate" of 1x means the service is consuming its error budget exactly as fast as the SLO allows (i.e., it's on pace to just barely meet the SLO by the end of the window); a burn rate of 10x means it's burning budget ten times faster than sustainable.

**Worked example.** A service has a 99.9% SLO over a 28-day window (40.32-minute budget). A fast, severe outage burns budget quickly: if 100% of traffic fails, the service burns its *entire* 28-day budget in just 40.32 minutes — a burn rate of `28 days / 40.32 minutes ≈ 1,000x`. The book recommends alerting on **combinations** of burn rate and window length, because a single threshold can't catch both fast, severe problems and slow, creeping ones without either paging too late or too often:
- **Fast burn**: burn rate ≥ 14.4x sustained over a 1-hour window — catches an outage severe enough to exhaust 2% of the monthly budget in an hour; page immediately.
- **Slow burn**: burn rate ≥ 6x sustained over a 6-hour window — catches a smaller, ongoing degradation that would still exhaust the budget well before month's end if left unaddressed; page, but with less urgency.
- **Very slow burn**: burn rate ≥ 1x sustained over 3 days — catches a persistent low-grade problem that a human should look at during business hours, often via a ticket rather than a page.

This multi-window approach directly solves a real tension: a short-window-only alert (e.g., "page if error rate > 1% for 5 minutes") is fast to detect real outages but generates false pages on brief, self-resolving blips; a long-window-only alert is robust to blips but detects real outages far too slowly. Requiring the burn rate to hold over *both* a short and a corroborating longer window (a common refinement: require both the 1-hour and a shorter 5-minute window to show the fast-burn rate before paging) gets fast detection without the noise.

### The three properties of a good alert
The book's practical bar for whether an alert should exist at all:
- **Precision** — of all the times this alert fires, what fraction represent a real, current problem? Low precision (lots of false positives) trains engineers to ignore the pager.
- **Recall** — of all the real problems that occurred, what fraction did this alert actually catch? Low recall means real user-impacting problems go unnoticed.
- **Detection time and reset time** — how fast does it fire once a real problem starts, and how fast does it clear once the problem is resolved (a slow-to-clear alert keeps someone needlessly engaged after the fire is out).

**Worked example — a bad alert, fixed.** "Page if any single server's CPU exceeds 90%" fires dozens of times a week on a large fleet, mostly during harmless, self-resolving load spikes with no user impact (low precision) — and gets muted or ignored within a month. Replacing it with a symptom-based, burn-rate alert on the service's actual error-rate SLI (as above) both reduces false pages dramatically (high precision) and reliably catches the cases where high CPU actually does cause user-facing errors or latency (retained recall) — because it's now measuring the thing that actually matters to users, not a proxy that only sometimes correlates with harm.

### Ticket vs. page: routing by urgency
Not every detected problem needs to interrupt someone's sleep. The book's routing split:
- **Page** — needs human action within minutes; something is actively harming users right now (e.g., fast error-budget burn).
- **Ticket** — needs human action, but not urgently; can be picked up during business hours (e.g., slow error-budget burn, a certificate expiring in 20 days).
- **Log only / dashboard** — informational, useful for debugging a paged incident or spotting long-term trends, but never interrupts anyone on its own.

Misrouting in either direction is costly: routing a ticket-level issue as a page burns on-call trust and sleep for no benefit; routing a page-level issue as a ticket means real user harm goes unaddressed for hours.

## Pros
- Symptom-based, golden-signal monitoring scales to complex systems without requiring a human to know every internal failure mode in advance.
- Burn-rate alerting directly ties paging urgency to actual user/business impact (via the SLO), rather than an arbitrary static threshold disconnected from what matters.
- A precision/recall-driven alert review process gives teams a concrete way to prune noisy alerts instead of accumulating them indefinitely.

## Cons
- Requires a trustworthy SLI/SLO already in place (`sre/02`, `sre/03`) — burn-rate alerting is meaningless without one, so teams without mature SLOs can't use the technique directly.
- Multi-window burn-rate alerting is more complex to configure and reason about than a simple static threshold, and requires monitoring infrastructure capable of computing rolling windows efficiently.
- Even well-designed alerts need ongoing maintenance as the system changes — an alert tuned for last year's traffic pattern can silently become imprecise as the service evolves.

## Alternatives
- **Cause-based alerting (alert on every internal component's health)** — catches problems closer to their root cause and can be faster to diagnose once paged, but produces far more alerts, most of which correlate poorly with actual user impact, and doesn't scale as the number of internal components grows.
- **Static threshold alerting (fixed % error rate or latency cutoff)** — simple to set up and reason about, but disconnected from the SLO's actual budget-burn implications; a threshold that's fine on a low-traffic day can be a serious SLO violation on a high-traffic day, and vice versa.
- **Anomaly-detection / ML-based alerting** — can catch unusual patterns a fixed rule wouldn't anticipate, but is harder to reason about, debug, and trust during an incident, and often needs significant tuning to avoid its own false-positive problems.

## When to use it
Use golden-signal, symptom-based monitoring as the default dashboard and alerting foundation for any user-facing service, and layer multi-window burn-rate alerting on top once a trustworthy SLO exists. Route every alert deliberately as page/ticket/log-only based on real urgency, and periodically review each page's precision and recall.

## When NOT to use it
Don't build sophisticated burn-rate alerting before you have a real SLO to burn against — start with SLIs/SLOs first (`sre/02`, `sre/03`). Don't alert on internal cause-level metrics (a specific cache's hit ratio, a specific thread pool's queue length) as pages by default — reserve those for dashboards used to diagnose an already-paged, symptom-level incident, not to generate their own pages.

## Key takeaways / mental model
Monitor symptoms (the four golden signals), diagnose causes. Page only when a human must act now to protect users or the error budget; route everything else to a ticket or a dashboard. If an alert's precision or recall is bad, fix or remove it — a pager nobody trusts is worse than no pager at all.

## Self-check questions
1. A service pages on "any 5xx response in the last minute." Using the precision/recall framework, explain what's likely wrong with this alert and redesign it using burn-rate thinking against a stated SLO.
2. Why does the book recommend requiring a burn-rate alert to hold over both a short and a longer corroborating window, rather than a single window? What failure mode does each window guard against on its own?
3. Classify each of the following as page / ticket / log-only, and justify: (a) error-budget burn rate of 20x sustained for 10 minutes, (b) a TLS certificate expiring in 25 days, (c) a single server's disk at 80% full with no growth trend, (d) error-budget burn rate of 1.2x sustained for 2 days.
4. Explain, with the checkout-API saturation example, why "saturation" is a useful golden signal to watch even when latency and error rate both currently look fine.

## References
- Site Reliability Engineering: How Google Runs Production Systems (Beyer, Jones, Petoff, Murphy), Chapter 6 ("Monitoring Distributed Systems") and Chapter 10 ("Practical Alerting from Time-Series Data").
- See also: `sre/04` (error budgets, which multi-window burn-rate alerting is built on) and `devops-reliability/devops-handbook` (forthcoming) for broader telemetry and feedback-loop practices this lesson's monitoring design feeds into.
