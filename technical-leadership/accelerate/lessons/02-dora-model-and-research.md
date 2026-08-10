---
id: accelerate/02
subject: accelerate
title: The DORA model and validated research approach
slug: dora-model-and-research
status: drafted
mastery:
seniority: senior
source: Accelerate (Forsgren, Humble, Kim), Chapter 2 "Measuring Performance" and Chapter 12 "The Science Behind This Book"
prerequisites: [accelerate/01]
created: 2026-08-10
updated: 2026-08-10
---

# The DORA model and validated research approach

## TL;DR
The DORA research program used rigorous survey science — validated psychometric instruments, latent variable modeling, and multi-year replication — to move claims about "what makes software delivery good" from anecdote and opinion to statistically defensible findings. Understanding the method matters because it tells you how much weight to put on the conclusions, and how to evaluate similar claims elsewhere.

## The idea
Most engineering-practice advice is opinion dressed as wisdom: "we did X at Google and it worked, so you should too." That kind of claim has an obvious problem — it's a sample size of one, with no control group, no way to separate what X actually caused from what merely correlated with a talented team, ample funding, or product-market fit. The DORA research program (State of DevOps Reports, later academically published, culminating in *Accelerate*) set out to do better: build a research methodology capable of distinguishing what actually predicts performance from what merely correlates with it in a handful of admired companies.

The approach borrows tools from social science and organizational psychology rather than computer science: large-sample surveys, validated latent-construct measurement, and structural equation modeling (SEM) to test whether a hypothesized causal model fits the observed data better than plausible alternatives. This is unusual in the software engineering literature, where "best practice" claims are typically unfalsifiable folklore. It is also why the book's claims replicate — the same core findings (that certain technical, process, and cultural capabilities predict delivery performance, and delivery performance predicts organizational performance) held up across multiple independent survey years and tens of thousands of respondents, not just one lucky sample.

## How it works

### Why self-reported survey data, and why that's defensible
A natural objection: "isn't self-reported survey data unreliable? People might over-report their deployment frequency or under-report failures." The research team addressed this directly:
- They validated their measurement instruments against objective data where possible (e.g., comparing self-reported deployment frequency against actual deployment logs in a subset of organizations) and found strong correlation.
- They used multi-item scales for constructs that are hard to measure with a single question (e.g., "organizational culture" is measured with the multi-item Westrum organizational culture instrument, `accelerate/09`, not a single "is your culture good?" question) — this is standard psychometric practice for measuring latent (unobservable-directly) constructs, and it reduces the noise any single question introduces.
- They ran the survey across multiple independent years with different respondent pools and found the same relationships — a single skewed sample would not replicate.

### Latent variables and structural equation modeling
A "latent variable" is a construct you can't measure directly with one question — like "organizational performance" or "culture" — so you infer it from several correlated indicator questions (e.g., profitability, market share, productivity, customer satisfaction, all rolled into one "organizational performance" latent construct). SEM lets the researchers specify a hypothesized causal structure (capabilities -> delivery performance -> organizational performance -> noncommercial outcomes) and test statistically whether the data is consistent with that structure, versus alternative orderings (e.g., maybe organizational performance causes delivery performance, not the other way around). This is what separates *Accelerate*'s claims from a simple correlation table: the model was tested against plausible alternative causal directions and the hypothesized direction fit best.

**Worked example — testing a causal direction:** Suppose you observe that companies with high delivery performance also report high profitability. Two causal stories are consistent with that single correlation:
1. Good delivery capability -> better products, faster iteration -> more profit.
2. Being profitable -> more budget for tooling and headcount -> better delivery metrics (reverse causation).

SEM, combined with theoretically-grounded model specification and multi-year data, lets the researchers test which structure the data supports better, and additionally lets them include control variables (company size, industry, "primarily a technology company" or not) to rule out obvious confounds. The reported finding — capabilities drive delivery performance which drives organizational performance — held up under this scrutiny across years, which is much stronger evidence than a single cross-sectional correlation.

### Clustering into performance profiles, not a single score
Rather than publish one composite "DevOps score," DORA clustered organizations by their pattern across the four key metrics (`accelerate/03`, `accelerate/04`) into performance profiles: Low, Medium, High, and (in later years) Elite. This matters methodologically because it avoids arbitrarily weighting the four metrics into one number (which would embed the researchers' opinion about relative importance) — instead, cluster analysis lets the *data* reveal that organizations naturally group into these bands, with elite performers distinctly separated from the rest on all four metrics simultaneously, not just trading off one for another.

### What "validated" does and doesn't mean here
It's worth being precise: the research demonstrates strong, replicated statistical association and a causal model that best fits the data among the alternatives tested — this is about as strong a claim as survey-based organizational research can support. It is not a randomized controlled trial (you cannot randomly assign real companies to "adopt continuous delivery" vs. "don't" and observe outcomes) — so residual uncertainty about unmeasured confounds always remains, and the authors are careful to describe findings as "predicts" and "is associated with," not as proven mechanical laws.

## Pros
- Replaces "trust the expert" or "trust the case study" with a method that can be scrutinized, replicated, and falsified — this is why the four key metrics (`accelerate/03`, `accelerate/04`) have become an industry standard rather than one firm's opinion.
- Multi-year replication protects against a single skewed sample driving the conclusions.
- Explicit modeling of latent constructs (culture, delivery performance) is more rigorous than the single ad hoc metrics often used in engineering organizations.

## Cons
- Survey-based research, however well validated, still relies on self-report; it can't fully substitute for direct instrumentation of your own systems.
- SEM and psychometric methods are unfamiliar to most engineering audiences, so the rigor is easy to take on faith rather than actually understand — which ironically reproduces the "trust the expert" problem the method was designed to avoid.
- The model describes what predicts performance in the aggregate, cross-organization; it does not diagnose your specific organization's bottleneck without you doing local measurement too.

## Alternatives
- **Single-company case studies (e.g., "How Netflix does X")** — richer contextual detail about one organization, but no ability to separate causal drivers from confounds; useful for inspiration, not for generalizable claims.
- **Internal instrumentation only (no survey, pure telemetry)** — objectively measures your own systems without self-report bias, but can't tell you what predicts performance *across* organizations, only what's happening in yours; best combined with the DORA framework, not a replacement for it.
- **Expert consensus / best-practice frameworks (e.g., early ITIL, CMMI)** — codify what experienced practitioners believe works, but historically lacked empirical validation against actual performance outcomes, which is precisely the gap DORA's methodology was built to close.

## When to use it
Reach for this understanding of the research method when you need to defend *why* the DORA metrics and capability model deserve more trust than a competing framework or a consultant's opinion — and when evaluating any new "best practice" claim, ask whether it has anything like this level of validation behind it.

## When NOT to use it
Don't treat the DORA findings as literally proven causal laws that apply deterministically to your specific organization — they are strong, replicated, cross-organization statistical patterns, which is different from a guarantee about your team. Also don't use "well the research is just a survey" as a reason to dismiss the findings outright; that objection was directly anticipated and addressed by the methodology (multi-item validated scales, cross-validation against objective data, multi-year replication).

## Key takeaways / mental model
When you see a claim like "high performers are 2x more profitable," ask three questions before trusting it: (1) how was the underlying construct measured — one question or a validated multi-item scale? (2) was the causal direction actually tested against alternatives, or just assumed? (3) did the finding replicate across independent samples? DORA's research answers all three; most "best practice" advice in the industry answers none.

## Self-check questions
1. Explain why measuring "organizational performance" with a single survey question would be weaker evidence than the multi-item latent-variable approach DORA used.
2. A colleague says "correlation isn't causation" to dismiss the DORA findings. What specific methodological choices did the researchers make to address that exact objection, beyond just having a large sample?
3. Why did DORA cluster organizations into performance profiles (Low/Medium/High/Elite) instead of publishing a single composite score?
4. What is the difference between "this predicts organizational performance across a large sample" and "this guarantees success for your specific team"? Why does that distinction matter when you cite this research to your leadership?

## References
- Accelerate: The Science of Lean Software and DevOps (Forsgren, Humble, Kim), Chapter 2: "Measuring Performance", Chapter 12: "The Science Behind This Book".
