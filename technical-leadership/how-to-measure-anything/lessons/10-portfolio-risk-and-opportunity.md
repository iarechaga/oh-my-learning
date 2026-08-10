---
id: how-to-measure-anything/10
subject: how-to-measure-anything
title: Quantifying risk and opportunity in portfolio decisions
slug: portfolio-risk-and-opportunity
status: drafted
mastery:
seniority: principal
source: How to Measure Anything (Douglas W. Hubbard), Chapter 6, Chapter 11
prerequisites: [how-to-measure-anything/07, how-to-measure-anything/09]
created: 2026-08-10
updated: 2026-08-10
---

# Quantifying risk and opportunity in portfolio decisions

## TL;DR
When you're choosing across a portfolio of bets (roadmap initiatives, infrastructure investments, technical migrations) rather than a single yes/no decision, the right unit of analysis is the combined risk/return distribution of the whole portfolio, not each project's individual expected value — because uncorrelated risks partially cancel across a portfolio the way a single project's internal risk cannot, and ignoring this leads to systematically wrong prioritization.

## The idea
Engineering leadership decisions rarely happen one at a time in isolation — a VP of Engineering is typically choosing among a slate of possible investments (platform work, migrations, new capabilities, risk-reduction efforts) under a shared, limited budget of engineering capacity. A common mistake is ranking projects purely by their individual expected value (from Monte Carlo modeling, lesson 07) and funding the top N until the budget runs out. This ignores two things a portfolio view captures that a project-by-project view cannot: (1) **risk correlation** — several projects that are individually medium-risk but fail for the *same underlying reason* (e.g., they all depend on the same fragile legacy system, or all assume the same optimistic hiring plan) create concentrated portfolio risk that isn't visible project-by-project; (2) **diversification value** — a portfolio of several independent, moderate-return, moderate-risk bets can have a better overall risk-adjusted outcome than a portfolio concentrated in one "safe-looking" giant bet, because uncorrelated failures don't happen simultaneously. This is the same logic as financial portfolio theory (Markowitz), applied to a technical/organizational investment portfolio instead of stocks.

## How it works

### Step 1: model each candidate investment as a distribution, not a point value
Using Monte Carlo simulation (`how-to-measure-anything/07`), each candidate roadmap item (a migration, a platform investment, a new feature bet) is represented not by a single "expected value" number but by its full output distribution — median, spread, and probability of a negative outcome.

### Step 2: identify correlations across the portfolio
For each pair of candidate investments, ask: do they share underlying risk drivers? Two migrations that both depend on the same under-documented legacy authentication system share a correlated risk — if that system turns out to be worse than expected, both projects are likely to blow their estimates simultaneously. Two investments that depend on entirely different systems and different teams are largely independent — their risks are much less likely to materialize together.

### Worked example: choosing among four roadmap bets under a shared budget
A staff/principal-level planning exercise: an org has capacity for roughly 3 of 4 candidate initiatives this year, each modeled via Monte Carlo (lesson 07) with a median expected value and a 90% CI:

| Initiative | Median value | 90% CI | Shares risk driver with |
|---|---|---|---|
| A: Migrate to new cloud provider | +$800k | [-$300k, +$1.9M] | C (same platform team capacity) |
| B: Build internal deployment platform | +$140k | [-$60k, +$410k] | (independent) |
| C: Consolidate 3 microservices | +$350k | [-$100k, +$700k] | A (same platform team capacity) |
| D: Adopt new observability stack | +$220k | [-$40k, +$480k] | (independent) |

Ranking by median value alone (a naive project-by-project view) picks A, C, D — the three highest medians — and funds those. But A and C share a risk driver: both depend heavily on the same platform team's limited capacity. If that team is overcommitted (a real, correlated risk — not two independent 1-in-10 risks, but effectively one 1-in-10 risk that hits both projects at once), funding both A and C concentrates portfolio risk in a way that funding A and B (a similar combined median value, but statistically independent) would not. A portfolio view — running a combined Monte Carlo simulation across all funded initiatives together, explicitly modeling the shared platform-team-capacity variable as a single correlated input feeding into both A's and C's outcomes — would show that the [A, C, D] portfolio has a meaningfully wider combined 90% CI and a higher probability of a "many things go wrong at once" bad-year outcome than the [A, B, D] portfolio, even though [A, C, D] has a slightly higher combined median. Depending on the organization's risk tolerance, [A, B, D] may be the better choice specifically *because* of this correlation, not despite its slightly lower expected value.

### Step 3: express portfolio risk tolerance explicitly
A key input a principal-level leader must supply (and often the part actually missing from most planning processes) is the organization's risk tolerance: how much downside variance is acceptable in exchange for a given amount of expected upside? This mirrors a financial risk-aversion parameter. A cash-constrained startup with no room for a bad year should weight downside risk heavily even at the cost of expected value; a well-capitalized company optimizing for long-term expected growth can tolerate more portfolio variance for higher expected return. Making this trade-off explicit and quantified — rather than leaving it as an unstated, inconsistently-applied gut feeling that shifts project to project — is itself one of the highest-leverage things a technical leader measuring at the portfolio level can do.

### The efficient frontier concept, applied
Financial portfolio theory's key output — the efficient frontier, the set of portfolios that maximize expected return for each level of risk — translates directly: given a set of candidate initiatives (each with a modeled return distribution and known/estimated correlations), you can compute, for any target capacity budget, which combination of initiatives maximizes expected value for a given acceptable level of downside risk. In practice at the engineering-leadership level this is rarely done with full mathematical rigor, but even a rough, directional version (explicitly flagging correlated bets and consciously trading a bit of expected value for diversification) captures most of the practical benefit over pure expected-value ranking.

## Pros
- Surfaces hidden concentration risk (multiple initiatives quietly depending on the same fragile system, same team, or same optimistic assumption) that project-by-project evaluation misses entirely.
- Makes an organization's actual risk tolerance explicit and consistent across decisions, instead of an inconsistent gut feeling that varies by which executive is in the room.
- Naturally supports a "some bets should be small and independent" diversification argument that's often hard to make persuasively with intuition alone, but falls out cleanly from the quantified portfolio view.

## Cons
- Requires Monte Carlo models (lesson 07) for each candidate initiative plus honest correlation estimates between them — a real analytical lift that most orgs' planning cycles don't budget time for.
- Correlation estimates between initiatives are themselves uncertain, often based on qualitative judgment ("these two both depend on the platform team") rather than hard data, which limits the precision of the resulting portfolio analysis — still valuable directionally, but shouldn't be oversold as precise.
- Can be misused to justify an overly conservative, diversification-obsessed portfolio that avoids any large, high-conviction bet — sometimes concentrated risk is the right call (e.g., an existential competitive threat justifying an all-in bet), and portfolio theory shouldn't override that kind of strategic judgment.

## Alternatives
- **Simple expected-value ranking (rank and cut)** — the common default; much simpler to run and communicate, and adequate when candidate initiatives are genuinely independent and risk tolerance is roughly uniform across them — the portfolio approach's added value is smallest in that case.
- **Strategic/qualitative prioritization frameworks (RICE, weighted scoring)** — faster, more common in product/roadmap planning; useful for a first pass at a large backlog, but doesn't capture correlated risk or true expected-value magnitude the way a quantified portfolio model does.
- **Real options / staged investment** — instead of committing to a full initiative upfront, structure it as a series of smaller decision points with off-ramps (build a prototype, then decide) — reduces portfolio risk by design rather than by selection, complementary to (not a replacement for) explicit portfolio-level correlation analysis.

## When to use it
When allocating a shared, limited pool of engineering capacity or budget across several candidate initiatives, especially at the staff/principal level where the leader is accountable for the org's overall risk-adjusted outcome, not any single project's success. Particularly valuable when candidate initiatives plausibly share underlying risk drivers (same team, same fragile dependency, same market assumption) that wouldn't be visible from separate project-level business cases.

## When NOT to use it
Skip full portfolio-risk modeling for a small number of clearly independent, low-stakes decisions, or when there is effectively no real choice to make (only one viable option, or capacity for all candidates) — the analytical overhead isn't repaid. Also be cautious about over-relying on this framework when a decision genuinely calls for concentrated conviction (a strategic bet-the-company move) rather than diversification — portfolio theory optimizes for risk-adjusted return, not for strategic necessity.

## Key takeaways / mental model
Don't evaluate roadmap bets one at a time and rank by expected value alone — ask which candidate bets secretly share the same underlying risk, and whether the organization's actual risk tolerance is being applied consistently. A portfolio of independent moderate bets can beat a portfolio of individually-impressive but correlated ones, even at the same combined expected value.

## Self-check questions
1. List 3-4 current or recent initiatives in your organization's roadmap. Do any of them share an underlying risk driver (same team, same dependency, same unproven assumption)? What would a correlated failure of that shared driver look like?
2. Explain why a portfolio of two correlated bets with combined expected value $1M is generally worse (from a risk-adjusted standpoint) than a portfolio of two independent bets with the same combined expected value.
3. How would you go about estimating the risk tolerance your organization should apply to a portfolio decision, given its financial position (e.g., runway, growth stage)?
4. Describe a real situation where concentrating on one big, correlated bet was actually the right strategic call despite the portfolio-risk argument against it. What made it right in that case?

## References
- How to Measure Anything: Finding the Value of Intangibles in Business (Douglas W. Hubbard), Chapter 6: "Quantifying Risk Through Modeling," and Chapter 11: "Preference and Attitudes: The Softer Side of Measurement" (risk tolerance and utility).
