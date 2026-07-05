---
name: roblox-analytics
description: >
  Roblox AnalyticsService: custom events, economy tracking, funnels, rate limits, event taxonomy.
last_reviewed: 2026-05-24
sources:
  - https://create.roblox.com/docs/reference/engine/classes/AnalyticsService
---

# Roblox Analytics Reference

## When to Load

Load when tracking player behavior, economy events, or funnels; building custom event instrumentation; or understanding AnalyticsService rate limits and batching.

## Quick Reference

**Load Full Reference below only when you need specific API signatures or implementation patterns.**

Key rules:
- Use `AnalyticsService` (built-in). No third-party analytics SDK needed.
- Three event types: Custom (counters/values), Economy (currency flow), Funnel (step progression)
- Rate limit: 120 + (20 × CCU) calls per minute. Batch where possible.
- Max 100 custom events, 10 economy resource types, 10 funnels, 3 custom fields per event.
- Log events AFTER successful operations, not on attempt (avoids inflated metrics).
- Custom fields (up to 3) let you slice data without burning event cardinality.
- Economy events track sources (earned) and sinks (spent) separately.
- Funnel events must fire steps in order. Skipped steps break the funnel.
- Events appear on Creator Hub dashboard after ~24 hours. Use "View Events" for real-time validation.
- Server-side logging preferred for accuracy. Client-side only for UI interaction tracking.

---
**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
