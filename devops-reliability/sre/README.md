# Site Reliability Engineering: How Google Runs Production Systems

This subject teaches reliability as an engineering discipline, not an operations
afterthought. You will build from measurable reliability targets into on-call,
incident response, release engineering, and organizational interfaces that keep
services dependable at scale. The sequence starts with measurement and control loops,
then moves to day-2 operations, and ends with cross-team reliability governance.

**Source book:** *Site Reliability Engineering: How Google Runs Production Systems* - Betsy Beyer, Chris Jones, Jennifer Petoff, Niall Murphy (O'Reilly, 2016).

**Seniority baseline:** senior (lessons range mid->staff).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`sre/<NN>`* (e.g. *"discuss `sre/03`"*). Ordered by dependency: define and measure reliability first, operate incidents and toil reduction next, then scale reliability practices across teams.

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | What SRE is and how it differs from traditional operations | mid | drafted | — | — | [lesson](lessons/01-what-sre-is.md) | — |
| 02  | Service level indicators (SLIs): measuring user-visible behavior | mid | drafted | — | — | [lesson](lessons/02-service-level-indicators.md) | — |
| 03  | Service level objectives (SLOs): target-setting for reliability | senior | drafted | — | — | [lesson](lessons/03-service-level-objectives.md) | — |
| 04  | Error budgets as a release-governance mechanism | senior | drafted | — | — | [lesson](lessons/04-error-budgets.md) | — |
| 05  | Toil: identifying, quantifying, and prioritizing elimination | senior | drafted | — | — | [lesson](lessons/05-toil-elimination.md) | — |
| 06  | Automation strategy for repetitive operational work | senior | drafted | — | — | [lesson](lessons/06-automation-strategy.md) | — |
| 07  | Monitoring and alerting design for actionable signals | senior | drafted | — | — | [lesson](lessons/07-monitoring-alerting.md) | — |
| 08  | On-call engineering: rotations, load, and sustainability | senior | drafted | — | — | [lesson](lessons/08-on-call-engineering.md) | — |
| 09  | Incident command and coordinated response | senior | drafted | — | — | [lesson](lessons/09-incident-command.md) | — |
| 10  | Postmortems and organizational learning from failure | senior | drafted | — | — | [lesson](lessons/10-postmortems-learning.md) | — |
| 11  | Capacity planning and demand forecasting | senior | drafted | — | — | [lesson](lessons/11-capacity-planning.md) | — |
| 12  | Release engineering and progressive delivery safety | senior | drafted | — | — | [lesson](lessons/12-release-engineering.md) | — |
| 13  | Data processing reliability and pipeline operations | senior | drafted | — | — | [lesson](lessons/13-data-processing-reliability.md) | — |
| 14  | Handling overload and cascading failure | senior | drafted | — | — | [lesson](lessons/14-overload-cascading-failure.md) | — |
| 15  | Multi-team reliability interfaces and support boundaries | staff | drafted | — | — | [lesson](lessons/15-multi-team-reliability-interfaces.md) | — |
| 16  | Evolving SRE practices with service maturity | staff | drafted | — | — | [lesson](lessons/16-sre-practice-maturity.md) | — |

**Status:** `drafted` (lesson written) - `discussed` (at least one discussion held).
**Mastery:** `solid` - `partial` - `shaky` - `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Seniority:** `junior` - `mid` - `senior` - `staff` - `principal` - the band whose job the concept anchors.
