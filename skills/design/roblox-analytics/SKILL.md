---
name: roblox-analytics
description: "Use when adding, changing, or auditing Roblox analytics: AnalyticsService events, economy, funnels, onboarding traces, rate limits."
when_to_use: "Also when reading stats, tracking where players drop off, measuring an update or experiment, instrumenting a feature, or checking events are logged correctly."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/reference/engine/classes/AnalyticsService
  - https://create.roblox.com/docs/production/analytics/event-types
  - https://create.roblox.com/docs/production/analytics/custom-fields
  - https://create.roblox.com/docs/production/analytics/analytics-dashboard
  - https://create.roblox.com/docs/production/analytics/monetization
  - https://create.roblox.com/docs/creator-rewards
  - https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits
  - https://create.roblox.com/docs/cloud-services/data-stores/right-to-be-forgotten
  - https://create.roblox.com/docs/cloud/reference/features/storage
  - https://create.roblox.com/docs/reference/engine/classes/DataModel
  - original
  - https://create.roblox.com/docs/production/analytics/journey-events
---

# Roblox Analytics Reference

## When to Load

Load when tracking player behavior, economy events, funnels, or onboarding traces, or building `AnalyticsService` instrumentation.

## Quick Reference

Key rules:
- Built-in `AnalyticsService`; no SDK.
- Event types: Custom, Economy, Funnel, Journey (branching paths, `LogJourneyEvent`). `Fire*` methods are deprecated.
- Rate limit: 120 + (20 × CCU) calls/minute. Batch where possible.
- Economy events report committed changes; diagnostic events can record failed attempts.
- Report the balance the committed mutation RETURNED; never recompute it from the `leaderstats` replica — re-adding double-counts.
- Economy events track sources (earned) and sinks (spent) separately.
- Funnel steps need not fire in order; skipped steps back-fill when a later step logs.
- Dashboard ~24-hour delay; "View Events" validates in real time.
- Server-side logging preferred; client-side only for UI interaction tracking.
- Creator Rewards: no grant event; track leading indicators. Dashboard owns payouts.
- First-session traces: bounded buffer, shared save owner, RTBF + retention. Eligibility from player history, not missing traces; attempts matter. full.md §8.

**Economy health (decision layer):**
- Instrument from day one; you cannot backfill history.
- Log source AND sink per currency with SKUs + the mutation's returned balance.
- Health signals: sink/source ratio, inflation, concentration, elasticity, D1/D7 cohorts (heuristic thresholds).
- Economy breaks: verify events, read narrowest broken signal, change ONE lever, re-check.

- Segments (`GetPlayerSegmentsAsync`: `UserAcquisitionSource`, `EngagementLevel`) are for measuring, not reordering the store. One analytics module; count sales from server receipts; test UserId hashes before A/B (full.md §9–10).

**Cross-refs:** `roblox-growth-design` (audit workflow); `roblox-liveops` (event KPIs); `roblox-monetization` (purchase funnel).

**Details:** `references/full.md`.
