---
name: roblox-gui
description: GUI systems, layout, responsiveness, cross-platform UI. ScreenGuis, UIListLayout, constraint-based design.
last_reviewed: 2026-05-22
sources:
  - https://github.com/brockmartin/roblox-game-skill (MIT)
---

# Roblox GUI/UI Systems Reference

## When to Load

Load when building any 2D/3D-attached UI: menus, HUDs, shops, notifications, dialogs. Covers ScreenGui setup, layout, responsiveness, cross-platform scaling.

## Quick Reference

**Load Full Reference below only when you need specific layout examples or implementation patterns.**

Key rules:
- Mobile-first: design for phone, scale up. Touch targets minimum 48x48px.
- Scale (0-1 proportional) for position/size. Offset only for fixed padding/icons.
- Container Frame Rule: every logical group gets a Frame with layout modifier inside.
- UIListLayout/UIGridLayout: set on parent Frame, children auto-arrange. AutomaticSize on parent.
- ScreenGui.ResetOnSpawn = false for persistent UI. IgnoreGuiInset = true for fullscreen.
- ZIndex for layering within same ScreenGui. DisplayOrder for ScreenGui priority.
- Never use absolute pixel sizes for main containers. UISizeConstraint for min/max bounds.
- ScrollingFrame: set CanvasSize or AutomaticCanvasSize. UIListLayout inside for content.
- Common AI mistake: forgetting to set LayoutOrder on children when using layout modifiers.
- For complex stateful UI (shops, inventories, settings), consider reactive frameworks like Fusion (dphfox/Fusion, MIT) or React-Lua (jsdotlua/react).
**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
