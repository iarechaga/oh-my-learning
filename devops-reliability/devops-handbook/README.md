# The DevOps Handbook

This subject is the practical implementation guide for making software delivery both
faster and safer in real organizations. It takes the Three Ways from principle to
concrete operating practices: delivery pipelines, fast feedback through telemetry,
and deliberate learning loops that improve reliability over time. The sequence moves
from flow mechanics to feedback architecture to organizational learning.

**Source book:** *The DevOps Handbook* - Gene Kim, Jez Humble, Patrick Debois, John Willis (IT Revolution, 2021).

**Seniority baseline:** senior (lessons range mid->staff).

**How to use this subject:** read a lesson on your own, then ask to *discuss
`devops-handbook/<NN>`* (e.g. *"discuss `devops-handbook/03`"*). Ordered by dependency: establish flow and deployment foundations first, then observability and feedback, then continual-learning and org practices.

**Cross-subject prerequisites** where relevant: `phoenix-project/05`, `phoenix-project/06`, and `phoenix-project/07` anchor the Three Ways this subject operationalizes.

## Concepts

| ID  | Concept | Seniority | Status | Mastery | Last discussed | Lesson | Records |
| --- | ------- | --------- | ------ | ------- | -------------- | ------ | ------- |
| 01  | Applying the Three Ways as an implementation model | senior | drafted | — | — | [lesson](lessons/01-three-ways-implementation-model.md) | — |
| 02  | Value stream mapping for software delivery | senior | drafted | — | — | [lesson](lessons/02-value-stream-mapping.md) | — |
| 03  | Small batch sizes and limiting work in process | mid | drafted | — | — | [lesson](lessons/03-small-batches-wip-limits.md) | — |
| 04  | Version control for code, infrastructure, and config | mid | drafted | — | — | [lesson](lessons/04-version-control-everything.md) | — |
| 05  | Continuous integration as a quality gate | mid | drafted | — | — | [lesson](lessons/05-continuous-integration.md) | — |
| 06  | Continuous delivery and deployment pipeline design | senior | drafted | — | — | [lesson](lessons/06-continuous-delivery-pipelines.md) | — |
| 07  | Trunk-based development and release cadence | senior | drafted | — | — | [lesson](lessons/07-trunk-based-release-cadence.md) | — |
| 08  | Shift-left security and compliance in delivery flow | senior | drafted | — | — | [lesson](lessons/08-shift-left-security-compliance.md) | — |
| 09  | Infrastructure as code and immutable infrastructure | senior | drafted | — | — | [lesson](lessons/09-infrastructure-as-code-immutable.md) | — |
| 10  | Telemetry foundations: logs, metrics, traces, events | mid | drafted | — | — | [lesson](lessons/10-telemetry-foundations.md) | — |
| 11  | Production monitoring and actionable alerting | senior | drafted | — | — | [lesson](lessons/11-monitoring-actionable-alerting.md) | — |
| 12  | Fast incident feedback into engineering work | senior | drafted | — | — | [lesson](lessons/12-incident-feedback-loops.md) | — |
| 13  | Blameless postmortems and systemic root cause analysis | senior | drafted | — | — | [lesson](lessons/13-blameless-postmortems.md) | — |
| 14  | Enabling team topologies and platform capabilities | staff | drafted | — | — | [lesson](lessons/14-enabling-teams-platform.md) | — |
| 15  | Governance through standards and self-service controls | staff | drafted | — | — | [lesson](lessons/15-governance-self-service-controls.md) | — |
| 16  | Measuring outcomes: delivery performance and reliability metrics | staff | drafted | — | — | [lesson](lessons/16-delivery-reliability-metrics.md) | — |

**Status:** `drafted` (lesson written) - `discussed` (at least one discussion held).
**Mastery:** `solid` - `partial` - `shaky` - `not-yet` - set from the most recent
discussion's verdict; empty until first discussed.
**Seniority:** `junior` - `mid` - `senior` - `staff` - `principal` - the band whose job the concept anchors.
