---
name: roblox-gui
description: "Use when building or fixing Roblox UI layout that must work on phones, tablets, desktop and console: HUDs, safe areas, focus, TV."
when_to_use: "Also when changing or reviewing any UI, or when UI overlaps, is cut off, too small, misplaced or unreadable on mobile, a phone, tablet, TV or with a controller, or a notch or top bar covers it."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/ui
  - https://create.roblox.com/docs/ui/position-and-size
  - https://create.roblox.com/docs/ui/styling
  - https://create.roblox.com/docs/ui/list-flex-layouts
  - https://create.roblox.com/docs/input/mobile
  - https://create.roblox.com/docs/input/micro-gamepad
  - https://create.roblox.com/docs/production/publishing/console-guidelines
  - https://create.roblox.com/docs/studio/device-simulator
  - https://create.roblox.com/docs/studio/controller-emulator
  - https://create.roblox.com/docs/reference/engine/classes/GuiService
  - https://create.roblox.com/docs/reference/engine/classes/ScreenGui
  - https://create.roblox.com/docs/reference/engine/classes/StarterGui
  - https://create.roblox.com/docs/reference/engine/classes/GuiObject
  - https://create.roblox.com/docs/reference/engine/datatypes/Color3
  - https://create.roblox.com/docs/reference/engine/enums/GuiNavigationDirection
  - https://create.roblox.com/docs/reference/engine/classes/ContentProvider
  - https://create.roblox.com/docs/performance-optimization/improve
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/includes/ui/clipping.md
  - https://raw.githubusercontent.com/Roblox/focus-navigation/main/README.md
  - https://devforum.roblox.com/t/what-are-the-best-ui-screeninset-settings-for-buttons/3519333
  - https://devforum.roblox.com/t/screenguiscreeninsets-topbarinsets-regression/4047230
  - original
---

# roblox gui

## When to Load

Where UI goes and how it adapts: containers, scale, safe areas, mobile-first layout, console and TV, gamepad focus. Menus, shops, dialogs, HUD widgets, text entry, lists and effects: `roblox-gui-components`.

## Quick Reference

- Mobile first: design on the smallest landscape phone with touch controls, then grow (full.md §7).
- Reserve top bar, thumbstick, jump, chat. Interactive UI in `CoreUISafeInsets`; the canvas is smaller than the screen, so lay out on the ScreenGui's `AbsoluteSize`.
- `AbsolutePosition` is measured from below the top bar for every ScreenGui: screen Y = `AbsolutePosition.Y + GetGuiInset().Y`. Compare elements in that shared space (§7.4).
- Check element pairs that can show together; reflow, don't shrink.
- `UITextSizeConstraint` ignores `UIScale`; scale the caps with the stage.
- Rotated or `UICorner` containers don't clip; use a `CanvasGroup` (§5).
- Gamepad: one `SelectedObject` owner, `SelectionGroup` bounds, deferred focus restore, layered Back (§6).
- Console/TV: TV-safe area, `ViewportDisplaySize`, no chat window; TV remote = D-pad, centre, back.
- Contrast: `Color3:GetContrastRatio`, `GetContrastingColor`.
- Test: Device Simulator + Controller Emulator; set the device before Play.

> Details: [references/full.md](references/full.md)
