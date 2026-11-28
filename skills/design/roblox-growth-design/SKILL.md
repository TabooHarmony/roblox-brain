---
name: roblox-growth-design
description: "Use for Roblox growth diagnosis: reading stats, Home recommendations, retention, onboarding, experiments, and Kids & Select."
when_to_use: "Also when CCU, D1/D7, playtime or Home recommendations are low, planning an A/B test, reading the Creator Dashboard, judging a small sample, or auditing why a game isn't growing."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/discovery
  - https://create.roblox.com/docs/discovery-faq
  - https://create.roblox.com/docs/production/publishing/kids-and-select
  - https://create.roblox.com/docs/production/game-design/analytics-essentials
  - https://create.roblox.com/docs/production/experiments
  - https://create.roblox.com/docs/production/configs
  - https://create.roblox.com/docs/production/game-design/onboarding
  - https://www.copyright.gov/title17/92chap2.html
  - original
---

# Roblox Growth Design

## When to Load

Diagnosing why a game isn't growing: stats, Home recommendations, retention, onboarding, experiments. Cadence, events, ads, packaging: `roblox-liveops`. Instrumentation: `roblox-analytics`.

## Quick Reference

### Diagnose before prescribing

1. Ask for dashboard, release, acquisition, and session evidence. Never invent metrics.
2. Find the narrowest broken transition: impression→play, join→control, action→payoff, return, purchase.
3. Hypothesis: **if Y changes because of Z, X should move without harming G.**
4. One test: primary metric, guardrails, detectable effect, decision rule. Experiments run 14–60 days (official).

### Small samples: imprecise, not noise

- Show the denominator ("D1 4/37") and the uncertainty.
- Keep diagnosis (where players drop) apart from keep/kill verdicts.
- Split 50/50 by UserId in one build, or compare matched weekday/hour blocks.
- Count exposure: who actually saw the feature.

<!-- temporal: 2026-11 -->
### Home model (official)

- Ranking uses only users acquired organically from Recommended for You. Ads don't affect RFY ranking.
- Top signals: play through rate, first-play bounce, play days (D1, D2–7, D8–28), playtime per user.
- Per-user averages over a moving window: no penalty for a weak start.
- A custom thumbnail is required for Home impressions.
- Drops can be seasonality (Saturday peak) or faster competitors.

### Metric → first suspects

- Low PTR: packaging, promise, audience.
- High bounce: join failure, performance, misleading package.
- Low D1: core loop, onboarding, first goal.
- Low D7/D30: progression, variety, social, endgame.
- Low conversion: product fit, value clarity.

Hypotheses only: segment and test.

### Kids & Select (official, 2026-11)

All-ages games start 16+ only until **100** highly engaged age-checked players within 60 days. 25 is the separate fee-refund threshold.

### Guardrails

Accurate metadata; no dark patterns or whale targeting. Live config keys override code defaults.

> Evidence limits, signals, FTUE, positioning, audit: [references/full.md](references/full.md)
