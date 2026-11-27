---
name: roblox-gui-components
description: "Use when building or fixing Roblox menus, shops, dialogs, HUD widgets, text entry, lists, grids, UI effects, or reactive UI code."
when_to_use: "Also when a menu opens twice or won't close, UI leaks after reopening, a purchase button double-buys, a countdown is wrong, a list jumps, text overflows, a TextBox won't submit, or old Tween/legacy UI code needs migrating."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/ui
  - https://create.roblox.com/docs/ui/2D-particle-emitters
  - https://create.roblox.com/docs/ui/appearance-modifiers
  - https://create.roblox.com/docs/ui/temporary-limits
  - https://create.roblox.com/docs/chat/guidelines
  - https://create.roblox.com/docs/reference/engine/classes/UIGradient
  - https://create.roblox.com/docs/reference/engine/enums/GradientType
  - https://create.roblox.com/docs/reference/engine/enums/GradientTileMode
  - https://create.roblox.com/docs/reference/engine/classes/ParticleEmitter2D
  - https://create.roblox.com/docs/reference/engine/classes/TextBox
  - https://create.roblox.com/docs/reference/engine/classes/UIGridLayout
  - https://create.roblox.com/docs/reference/engine/classes/UIPageLayout
  - https://create.roblox.com/docs/reference/engine/classes/Decal
  - https://create.roblox.com/docs/reference/engine/classes/VideoPlayer
  - https://create.roblox.com/docs/projects/server-authority
  - https://raw.githubusercontent.com/Roblox/react-luau/main/README.md
  - https://raw.githubusercontent.com/dphfox/Fusion/main/README.md
  - https://raw.githubusercontent.com/centau/vide/main/README.md
  - https://raw.githubusercontent.com/ffrostfall/fluid/main/README.md
  - original
---

# roblox gui components

## When to Load

Stateful UI: windows, menus, shops, dialogs, HUD readouts, text entry, lists, grids, effects, reactive libraries, legacy migration. Screen placement, safe areas and focus: `roblox-gui`. Styling stays neutral: follow the project's look.

## Quick Reference

- **One controller per window:** states `Closed/Opening/Open/Closing`, idempotent `open()`/`close()`, a token that cancels stale tweens. Route every open path through it (full.md §2).
- **Own what you change:** register an undo for each outside change (mouse release, `TouchControlsEnabled`, hidden HUD, connections); close, destroy and respawn run them in reverse.
- **Server decides:** correlate requests by id, block while pending, reconcile on timeout, never blind-retry purchases (§3).
- Countdowns read the authoritative end time; held-item readouts use client prediction.
- First person: a window needing clicks shows a `Modal` button and sets `MouseIconEnabled`.
- Player text: server `FilterStringAsync`, 60 s rate limit if others see it; chat only via `TextChatService` (`roblox-text-chat`).
- `ScrollingFrame` list: `VerticalAlignment = Top`; keep focus and scroll across rebuilds.
- Effects: `UIGradient.Type` (`Linear/Radial/Elliptical/Conical`) + `TileMode`; animate `Offset`, not `Color`. `ParticleEmitter2D` (beta) for UI sparkles.
- Reactive UI: session vs screen scope, effects in the body, keyed lists, reopen leak test.

> Details: [references/full.md](references/full.md)
