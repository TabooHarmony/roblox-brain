---
name: roblox-growth-design
description: "Use for growth diagnosis, discovery, retention, onboarding, experiments, LiveOps, and packaging."
last_reviewed: 2026-08-07
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

- Low QPTR: packaging readability, promise accuracy, or audience mismatch.
- Bounce under 3 min: join failure, performance, confusing FTUE, or delayed payoff.
- Low D1: core loop, onboarding, stability, goals, or first payoff.
- Low D7/D30: progression, variety, social value, LiveOps, endgame, or exhaustion.
- Low conversion/ARPPU: product fit, value communication, friction, catalog depth, or concentration.

These are hypotheses, not one-to-one causes. Segment and test. Per-stat tactics in full.md §3–§6.

### Guardrails

Use accurate metadata. Avoid dark patterns, deceptive odds, coercive scarcity, and "whale" targeting. Treat moderation, abuse, accessibility, localization, performance, and economy health as constraints.

> Full signal definitions, positioning, FTUE, packaging, social design, and audit workflow: [references/full.md](references/full.md)
