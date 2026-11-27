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
  - https://create.roblox.com/docs/production/analytics/acquisition
  - https://create.roblox.com/docs/production/analytics/retention
  - https://create.roblox.com/docs/production/analytics/engagement
  - https://create.roblox.com/docs/production/analytics/monetization
  - https://create.roblox.com/docs/production/experiments
  - https://create.roblox.com/docs/cloud/guides/experiments
  - https://create.roblox.com/docs/production/configs
  - https://create.roblox.com/docs/production/game-design/core-loops
  - https://create.roblox.com/docs/production/game-design/onboarding
  - https://create.roblox.com/docs/production/game-design/monetization-foundations
  - https://create.roblox.com/docs/production/publishing/accessibility
  - https://create.roblox.com/docs/production/monetization/price-optimization
  - https://create.roblox.com/docs/production/monetization/developer-exchange
  - https://devforum.roblox.com/t/boost-your-discovery-by-building-games-people-want-to-play/4779042
  - https://www.copyright.gov/title17/92chap2.html
  - https://copyright.gov/circs/circ30.pdf
  - original
---

# Roblox Growth Design

## When to Load

Load to diagnose why a game isn't growing: stats, Home recommendations, retention, onboarding, experiments. Cadence, events, ads, and packaging: `roblox-liveops`. Instrumentation: `roblox-analytics`.

## Quick Reference

### Diagnose before prescribing

1. Ask for dashboard, release, acquisition, and session evidence. Never invent metrics.
2. Find the narrowest broken transition: impression→play, join→control, action→payoff, return, purchase.
3. Hypothesis: **if Y changes because of evidence Z, X should move without harming G.**
4. One test: primary metric, guardrails, detectable effect (MDE), decision rule.
5. Experiments run 14–60 days (official); don't decide on day one or stop on a lucky line.

### Small samples: imprecise, not noise

- Show the denominator ("D1 4/37") and the uncertainty with every rate.
- Keep diagnostic evidence (where players drop) apart from keep/kill verdicts.
- Split 50/50 by UserId inside one build; else compare matched weekday and hour blocks.
- Count exposure: how many players actually saw the feature.

<!-- temporal: 2026-11 -->
### Home model (official)

- Ranking uses only users acquired organically from Recommended for You. Ads don't affect RFY ranking.
- Top signals: play through rate, first-play bounce, play days (D1, D2–7, D8–28), playtime per user. Then co-play, qualified sessions, spend days, Robux spent.
- Signals are per-user averages over a moving window: no penalty for a weak start.
- A custom thumbnail is required for Home impressions.
- Drops can come from seasonality (Saturday peak) or faster-improving competitors.

### Metric → first suspects

- Low PTR: packaging, promise, audience mismatch.
- High bounce: join failure, performance, misleading package, delayed payoff.
- Low D1: core loop, onboarding, first goal, stability.
- Low D7/D30: progression, variety, social value, endgame.
- Low conversion/ARPPU: product fit, value clarity, catalog depth.

These are hypotheses: segment and test.

### Kids & Select (official, 2026-11)

All-ages games start 16+ only until **100** highly engaged age-checked players within 60 days. 25 is the fee-refund threshold, a separate gate.

### Guardrails

Accurate metadata. No dark patterns, deceptive odds, or whale targeting. Live config keys override code defaults: log effective tuning.

> Experiments, evidence limits, signal details, FTUE, positioning, audit workflow: [references/full.md](references/full.md)
