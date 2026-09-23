---
name: roblox-gui
description: "Use when building Roblox menus, HUDs, shops, notifications, dialogs, or responsive cross-platform UI."
last_reviewed: 2026-08-31
sources:
  - https://create.roblox.com/docs/ui
  - https://create.roblox.com/docs/ui/position-and-size
  - https://create.roblox.com/docs/ui/styling
  - https://create.roblox.com/docs/ui/list-flex-layouts
  - https://create.roblox.com/docs/input
  - https://create.roblox.com/docs/reference/engine/classes/GuiService
  - https://create.roblox.com/docs/reference/engine/classes/GuiObject
  - https://create.roblox.com/docs/reference/engine/classes/ScreenGui
  - https://create.roblox.com/docs/projects/server-authority
  - https://create.roblox.com/docs/input/input-action-system
  - https://create.roblox.com/docs/reference/engine/classes/ReplicatedFirst
  - https://create.roblox.com/docs/reference/engine/classes/ContentProvider
  - https://create.roblox.com/docs/reference/engine/classes/UIPageLayout
  - https://create.roblox.com/docs/reference/engine/classes/SelectionBox
  - https://create.roblox.com/docs/reference/engine/classes/Decal
  - https://create.roblox.com/docs/reference/engine/classes/VideoPlayer
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

- `ScreenGui` overlays; `SurfaceGui` on surfaces; `BillboardGui` for world labels.
- Let `UIListLayout`, `UIGridLayout`, and constraints own repeated layout. Avoid per-frame pixel positioning.
- Use `Scale` for responsive structure and `Offset` for deliberate padding or fixed-size details.
- Design for touch and gamepad as well as mouse and keyboard. Bind gameplay actions with `ContextActionService` where it fits.
- For gamepad UI, set a selected entry point and test directional focus. `GuiService.SelectedObject` is the native baseline.
- Reuse the project's visual language; let the owner choose art direction. Verify the UI over the game world.
- Keep UI state separate from the server state that it displays. A button is not an authority boundary.
- Server Authority UI may show corrected predictions. Show confirmed inventory and currency; route gameplay input through the Input Action System.
- Make scrolling, text growth, clipping, and safe-area behavior explicit before adding polish.
- Build custom loading UI in `ReplicatedFirst`; never use a client-side character teleport as the readiness gate.

**Need the details?** Load `references/full.md` for layout recipes and UI lifecycle patterns.
