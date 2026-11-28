---
name: roblox-analytics
description: "Use when adding, changing, or auditing Roblox analytics: AnalyticsService events, economy, funnels, onboarding traces, rate limits."
when_to_use: "Also when reading stats, tracking where players drop off, measuring an update or experiment, instrumenting a feature, or checking events are logged correctly."
last_reviewed: 2026-10-14
sources:
  - https://create.roblox.com/docs/reference/engine/classes/AnalyticsService
  - https://create.roblox.com/docs/production/analytics/event-types
  - https://create.roblox.com/docs/production/analytics/custom-fields
  - https://create.roblox.com/docs/production/analytics/analytics-dashboard
  - https://create.roblox.com/docs/production/analytics/monetization
  - https://create.roblox.com/docs/creator-rewards
  - https://devforum.roblox.com/t/creator-rewards-is-live/3838257
  - https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits
  - https://create.roblox.com/docs/cloud-services/data-stores/right-to-be-forgotten
  - https://create.roblox.com/docs/cloud/reference/features/storage
  - https://create.roblox.com/docs/reference/engine/classes/DataModel
  - original
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/production/analytics/retention.md
---

# Roblox Analytics Reference

## When to Load

Load when tracking player behavior, economy events, funnels, or onboarding traces, or building `AnalyticsService` instrumentation.

## Quick Reference

Key rules:
- Built-in `AnalyticsService`; no third-party SDK.
- Event types: Custom (counters/values), Economy (currency flow), Funnel (step progression)
- Rate limit: 120 + (20 × CCU) calls/minute. Batch where possible.
- Economy events report committed changes; diagnostic events can record failed attempts.
- Report the balance the committed mutation RETURNED; never recompute it from the `leaderstats` replica — re-adding double-counts.
- Economy events track sources (earned) and sinks (spent) separately.
- Funnel steps need not fire in order; skipped steps back-fill when a later step logs.
- Dashboard ~24-hour delay; "View Events" validates in real time.
- Server-side logging preferred; client-side only for UI interaction tracking.
- Creator Rewards: no AnalyticsService grant event. Track leading indicators (session duration, onboarding, referrals); Creator Dashboard owns payouts.
- First-session traces: bounded buffer, shared save owner, RTBF + retention. Eligibility from player history, not missing traces; attempts matter. full.md §8.

**Economy health (decision layer):**
- Instrument from day one; you cannot backfill history.
- Log source AND sink per currency with SKUs + the mutation's returned balance.
- Health signals: sink/source ratio, inflation, whale concentration, elasticity, sink sufficiency, D1/D7 cohorts. Thresholds are heuristics.
- Economy breaks: verify events, read narrowest broken signal, change ONE lever, re-check.

**Cross-refs:** `roblox-growth-design` (audit workflow); `roblox-liveops` (event KPIs); `roblox-monetization` (purchase funnel).

**Need more detail?** `references/full.md`: code examples, API tables, edge cases.
