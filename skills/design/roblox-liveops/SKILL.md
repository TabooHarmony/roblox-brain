---
name: roblox-liveops
description: "Use for Roblox LiveOps and launch: update cadence, events, season passes, notifications, sponsored ads, icons, thumbnails, titles."
when_to_use: "Also when planning an update or event, ads waste money or CTR is low, CCU spikes then dies, a thumbnail or title isn't working, players don't return after an event, or choosing a game name."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/production/game-design/liveops-essentials
  - https://create.roblox.com/docs/production/game-design/liveops-planning
  - https://create.roblox.com/docs/production/game-design/content-updates
  - https://create.roblox.com/docs/production/game-design/season-pass-design
  - https://create.roblox.com/docs/production/promotion/experience-events
  - https://create.roblox.com/docs/production/promotion/experience-notifications
  - https://create.roblox.com/docs/production/promotion/ads-manager
  - https://create.roblox.com/docs/production/promotion/search-ads
  - https://create.roblox.com/docs/production/promotion/rewarded-video-playbook
  - https://create.roblox.com/docs/production/publishing/experience-icons
  - https://create.roblox.com/docs/production/publishing/thumbnails
  - https://create.roblox.com/docs/production/publishing/publish-games-and-places
  - https://create.roblox.com/docs/discovery
  - https://create.roblox.com/docs/production/promotion/content-ratings
  - https://qptr.io
  - https://creatorexchange.io
  - original
---

# Roblox LiveOps and Launch

## When to Load

Load when planning what ships after launch and how players find it: cadence, events, season content, notifications, ads, packaging. Diagnosing stats and experiments: `roblox-growth-design`. Products: `roblox-monetization`. Notification code: `roblox-cloud`.

## Quick Reference

### Cadence (official)

- Four update types: content cadence, major updates, quality of life, bug fixes. Blend all four.
- Cadence releases: art-led, under 3 weeks of effort, every 2–4 weeks, not instantly consumable.
- Plan each event: target KPI, player actions, economy impact, communication timing, hourly monitoring, and what remains afterward.
- Field practice: one target stat per update; patches ship any time.

### Season passes (official)

About one month long, at least one week of rest between seasons, about ten tiers, auto-enroll, a visible Season UI, a worthwhile final reward. A feature package exists.

<!-- temporal: 2026-11 -->
### Events and notifications (official)

- Up to 10 ongoing or upcoming events; use a unique event thumbnail.
- Trending Events needs an active event started within 7 days and 1,000+ RSVPs.
- Event joins carry the event ID in `GameJoinContext`.
- Update announcements: 60 chars, at most once every 3 days.
- Notifications reach opted-in 13+ users. Check `CanPromptOptInAsync` before `PromptOptIn`.

### Ads (official)

- Objectives: Plays, Earnings, Qualify for Kids and Select.
- Up to 10 thumbnails per campaign, evenly distributed. Ads show on Home and search.
- **Ads don't affect RFY ranking.**
- Plays and earnings report with up to 48 h delay; first-join attribution lasts 30 days.

### Ads (field reports)

- Ad players are cold traffic: stats look worse than Home's. Spend sets speed, not ceiling.
- Run steady, modest daily budgets in one continuous campaign; let the learning phase finish.
- Judge creatives after 1,000+ impressions. Split desktop and mobile.
- Treat rising Home traffic as a reason to test a cut, not to stop blindly.

### Packaging (official)

- Icon: square, ≥512×512.
- Thumbnails: 16:9, 1920×1080, under 3 MB, 2–5 active for personalization.
- A custom thumbnail is required for Home.
- Search every candidate title for collisions; clickbait that raises bounce is a loss.

> Cadence detail, launch trajectories, ad traps, creative choices, title checks: [references/full.md](references/full.md)
