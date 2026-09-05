---
name: roblox-analytics
description: "Use when tracking player behavior, economy events, or funnels with AnalyticsService, including event taxonomy, rate limits, and batching."
last_reviewed: 2026-08-11
sources:
  - https://create.roblox.com/docs/reference/engine/classes/AnalyticsService
  - https://create.roblox.com/docs/production/analytics/custom-fields
  - https://create.roblox.com/docs/production/analytics/analytics-dashboard
  - https://create.roblox.com/docs/production/analytics/monetization
  - https://create.roblox.com/docs/creator-rewards
  - https://devforum.roblox.com/t/creator-rewards-is-live/3838257
---

# Roblox Analytics Reference

## When to Load

Load when tracking player behavior, economy events, or funnels, or when building AnalyticsService instrumentation.

## Quick Reference

**Full Reference below: load only for API signatures or implementation patterns.**

Key rules:
- Use `AnalyticsService` (built-in). No third-party analytics SDK needed.
- Three event types: Custom (counters/values), Economy (currency flow), Funnel (step progression)
- Rate limit: 120 + (20 × CCU) calls per minute. Batch where possible.
- Max 100 custom events, 5 unique currency types, 10 funnels, 3 custom fields per event.
- Log events AFTER successful operations, not on attempt. Failed attempts log nothing.
- Report the balance the authoritative mutation RETURNED at commit, unchanged. Never recompute it from the `leaderstats` replica: it already reflects the grant; re-adding double-counts.
- Custom fields (up to 3) slice data without burning event cardinality.
- Economy events track sources (earned) and sinks (spent) separately.
- Funnel steps need not fire in order; skipped intermediate steps are auto-back-filled as completed when a later step logs.
- Events appear on Creator Hub dashboard after ~24 hours. Use "View Events" for real-time validation.
- Prefer server-side logging for accuracy; client-side only for UI interaction tracking.
- Creator Rewards: no AnalyticsService grant event. Analytics for leading indicators (session duration, onboarding, referral milestones); Creator Dashboard for payout attribution.

**Economy health (decision layer):**
- Instrument from day one; you cannot backfill history when the economy breaks.
- Log source AND sink per currency with SKUs + the committed mutation's returned balance.
- Health signals: sink/source ratio, inflation (`CurrencySources - CurrencySinks`), whale concentration (high ARPPU + low ARPDAU), price elasticity, sink sufficiency, D1/D7 cohorts. Thresholds are heuristics, not Roblox statements.
- Economy breaks: verify events exist + correct, read narrowest broken signal, change ONE lever, re-check. Telemetry reports what broke; the user owns the design decision.

**Cross-refs:** `roblox-growth-design` for audit workflow; `roblox-monetization` for the purchase funnel.

**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
