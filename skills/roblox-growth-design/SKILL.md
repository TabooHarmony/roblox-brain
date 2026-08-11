---
name: roblox-growth-design
description: "Use for growth diagnosis, discovery, retention, onboarding, experiments, LiveOps, and packaging."
last_reviewed: 2026-08-11
sources:
  - https://create.roblox.com/docs/discovery
  - https://create.roblox.com/docs/production/game-design/analytics-essentials
  - https://create.roblox.com/docs/production/analytics/acquisition
  - https://create.roblox.com/docs/production/analytics/retention
  - https://create.roblox.com/docs/production/analytics/engagement
  - https://create.roblox.com/docs/production/analytics/monetization
  - https://create.roblox.com/docs/production/experiments
  - https://create.roblox.com/docs/production/game-design/core-loops
  - https://create.roblox.com/docs/production/game-design/onboarding
  - https://create.roblox.com/docs/production/game-design/liveops-planning
  - https://create.roblox.com/docs/production/game-design/liveops-essentials
  - https://create.roblox.com/docs/production/game-design/content-updates
  - https://create.roblox.com/docs/production/game-design/monetization-foundations
  - https://create.roblox.com/docs/production/game-design/season-pass-design
  - https://create.roblox.com/docs/production/publishing/experience-icons
  - https://create.roblox.com/docs/production/publishing/thumbnails
  - https://create.roblox.com/docs/production/publishing/accessibility
  - https://create.roblox.com/docs/production/monetization/regional-pricing
  - https://create.roblox.com/docs/production/monetization/price-optimization
  - https://devforum.roblox.com/t/boost-your-discovery-by-building-games-people-want-to-play/4779042
  - https://qptr.io
  - https://creatorexchange.io
  - original
---

# Roblox Growth Design

## When to Load

Load for growth, discovery, retention, onboarding, packaging, or LiveOps; route implementation to domain skills.

## Quick Reference

### Diagnose before prescribing

1. Ask for dashboard, release, acquisition, and session evidence. Never invent metrics.
2. Find the narrowest broken transition: impression→play, join→control, action→payoff, return, or purchase.
3. Write a falsifiable hypothesis: **If Y changes because evidence Z, X should move without harming G.**
4. Prefer one test with a primary metric, counter-metrics, MDE, and decision rule.
5. Stop for safety, severe regressions, or invalid instrumentation; avoid significance peeking.

<!-- temporal: 2026-07 -->
### Home diagnosis

- Low Play-Through Rate (PTR, was QPTR): packaging readability, promise accuracy, or audience mismatch. Also check Experience Detail Page CTR.
- High First-Play Bounce Rate (negative stat): misleading package/clickbait, join failure, performance, confusing FTUE, or delayed payoff.
- Low D1: core loop, onboarding, stability, goals, or first payoff.
- Low D7/D30: progression, variety, social value, LiveOps, endgame, or exhaustion.
- Low conversion/ARPPU: product fit, value communication, friction, catalog depth, or concentration.
- Low 7-day spend days / play days per user: consumables, purchase pathways, or event cadence.

These are hypotheses, not one-to-one causes. Segment and test. Per-stat tactics in full.md §3–§6.

### Algorithm hotspots (2026)

- Cold traffic: ads are the cheapest, least-qualified players; Home algo ranks the qualified audience. Launch stats look bad on ad players — don't panic.
- Ranking: genre-wide first, then against "experiences with similar players." That second benchmark is the real competition.
- Ads do not buy Home placement; meaningful stat-improving updates do. 28-day signals (D1, D2–7, D8–28) — updates take days to show.
- Beta mode hides a game from Home; tune metrics on cheap ad traffic before opening to the algo.
- The 500 highly-engaged-player requirement (official): all-ages games start 16+ only until 500 highly engaged age-checked plays within 60 days. Definition (official, evolving): account tenure + playtime in your game + a purchase anywhere on Roblox in the last 60 days. 100 = publishing-fee refund threshold (separate). Ads serve 16+ automatically. Home impressions accelerate the count fastest.
- Experience detail page matters: put your best thumbnails and a gameplay description there; it feeds overall play-through.

### Monetization mental model (practitioner)

- Convert valuable one-time game passes into consumables (repeat-purchase dev products) — they pump 7-day spend days per user and solve recurring pain.
- Products must be must-haves that solve a pain (effort grind, losing progress AFK, FOMO, status). Limiteds with real scarcity outsell unlimited cosmetics.
- Place products at points of interest with high foot traffic, and time prompts at the decision moment (e.g., 2x offline earnings at the collect point).
- Give players multiple purchase pathways: HUD shop icon, "+" next to currency, and a cash-shop popup after repeated failed buys.
- After shipping, check collateral damage: playtime, D1, D7, FTUE, and in-game economy.

### Guardrails

Use accurate metadata. Avoid dark patterns, deceptive odds, coercive scarcity, and "whale" targeting. Treat moderation, abuse, accessibility, localization, performance, and economy health as constraints.

> Full signal definitions, positioning, FTUE, packaging, social design, monetization mental model, algorithm mechanics, LiveOps, and audit workflow: [references/full.md](references/full.md)
