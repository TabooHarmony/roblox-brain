---
name: roblox-gui
description: "Use when building Roblox menus, HUDs, shops, notifications, dialogs, or responsive cross-platform UI."
last_reviewed: 2026-07-13
sources:
  - https://create.roblox.com/docs/ui
  - https://create.roblox.com/docs/ui/position-and-size
  - https://create.roblox.com/docs/input
  - https://create.roblox.com/docs/reference/engine/classes/GuiService
  - https://create.roblox.com/docs/reference/engine/classes/GuiObject
  - https://create.roblox.com/docs/reference/engine/classes/ScreenGui
  - https://create.roblox.com/docs/projects/server-authority
  - https://create.roblox.com/docs/input/input-action-system
  - https://raw.githubusercontent.com/Roblox/focus-navigation/main/README.md
  - https://devforum.roblox.com/t/introducing-improvements-to-directional-ui-selection-on-gamepad/3864317
  - https://devforum.roblox.com/t/what-are-the-best-ui-screeninset-settings-for-buttons/3519333
  - https://devforum.roblox.com/t/screenguiscreeninsets-topbarinsets-regression/4047230
  - https://raw.githubusercontent.com/Roblox/react-luau/main/README.md
  - original
---

# roblox gui

## When to Load

Load when building a HUD, menu, shop, dialog, notification, or UI attached to a 3D object.

## Quick Reference

- Use `ScreenGui` for screen overlays, `SurfaceGui` for a surface, and `BillboardGui` for floating world labels.
- Let `UIListLayout`, `UIGridLayout`, and constraints own repeated layout. Avoid per-frame pixel positioning.
- Use `Scale` for responsive structure and `Offset` for deliberate padding or fixed-size details.
- Design for touch and gamepad as well as mouse and keyboard. Bind gameplay actions with `ContextActionService` where it fits.
- For gamepad UI, define a selected entry point and deliberate directional behavior. `GuiService.SelectedObject` plus `Selectable` is the native baseline; the Roblox Focus Navigation library is an optional reference for richer focus trees.
- Keep UI state separate from the server state that it displays. A button is not an authority boundary.
- In Server Authority projects, a UI may show predicted state that is later corrected. Keep durable inventory, currency, and ownership displays tied to confirmed state, and use the Input Action System for gameplay-affecting input.
- Make scrolling, text growth, clipping, and safe-area behavior explicit before adding polish.

**Need the details?** Load `references/full.md` for layout recipes and UI lifecycle patterns.
