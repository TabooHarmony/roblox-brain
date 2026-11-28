---
name: roblox-liveops
description: "Use for Roblox LiveOps and launch: update cadence, events, season passes, notifications, sponsored ads, icons, thumbnails, titles."
when_to_use: "Also when planning an update or event, ads waste money or CTR is low, CCU spikes then dies, a thumbnail or title isn't working, players don't return after an event, or choosing a game name."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/production/game-design/liveops-essentials
  - https://create.roblox.com/docs/production/game-design/season-pass-design
  - https://create.roblox.com/docs/production/promotion/experience-events
  - https://create.roblox.com/docs/production/promotion/ads-manager
  - https://create.roblox.com/docs/production/publishing/thumbnails
  - original
---

# Roblox LiveOps and Launch

## When to Load

Planning what ships after launch and how players find it: cadence, events, seasons, notifications, ads, packaging. Stats and experiments: `roblox-growth-design`. Products: `roblox-monetization`.

## Quick Reference

### Cadence (official)

- Four update types: content cadence, major updates, quality of life, bug fixes.
- Cadence releases: art-led, under 3 weeks of effort, every 2–4 weeks, not instantly consumable.
- Per event: target KPI, player actions, economy impact, communication, hourly monitoring.
- Field practice: one target stat per update; patches ship any time.

### Season passes (official)

About one month, a week of rest between seasons, about ten tiers, auto-enroll, a visible Season UI, a worthwhile final reward.

<!-- temporal: 2026-11 -->
### Events and notifications (official)

- Up to 10 ongoing or upcoming events, each with its own thumbnail.
- Trending Events: started within 7 days, 1,000+ RSVPs.
- Event joins carry the event ID in `GameJoinContext`.
- Update announcements: 60 chars, once every 3 days.
- Notifications: opted-in 13+ users; `CanPromptOptInAsync` before `PromptOptIn`.

### Ads (official)

- Objectives: Plays, Earnings, Qualify for Kids and Select.
- Up to 10 thumbnails per campaign, evenly distributed; Home and search.
- **Ads don't affect RFY ranking.** Plays report with up to 48 h delay.

### Ads (field reports)

- Ad players are cold traffic; spend sets speed, not ceiling.
- Steady daily budget, one continuous campaign; let learning finish.
- Judge creatives after 1,000+ impressions; split desktop and mobile.

### Packaging (official)

- Icon square, ≥512×512. Thumbnails 16:9, 1920×1080, under 3 MB, 2–5 active.
- A custom thumbnail is required for Home.
- Search candidate titles for collisions; clickbait that raises bounce loses.

> Cadence, launch shapes, ad traps, creative, titles: [references/full.md](references/full.md)
