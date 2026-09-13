---
name: roblox-ui-design
description: "Use for Roblox UI composition, hierarchy, visual systems, style inheritance, accessibility, and design review."
last_reviewed: 2026-09-13
sources:
  - https://create.roblox.com/docs/production/publishing/adaptive-design
  - https://create.roblox.com/docs/ui/styling
  - https://create.roblox.com/docs/ui/list-flex-layouts
  - https://create.roblox.com/docs/reference/engine/classes/UIFlexItem
  - https://create.roblox.com/docs/reference/engine/classes/UICorner
  - original
---

# Roblox UI Visual Design

## When to Load

Load for UI design or review. Existing art direction takes priority; otherwise derive a restrained system from game fantasy and screen job. Load `roblox-gui` for mechanics.

## Quick Reference

### Establish the visual system

1. Inspect existing surfaces, type roles, borders, depth, icons, spacing, and action colors; reuse tokens.
2. If no style exists, name the screen job and game fantasy before choosing colors or decoration.
3. Define a small token set: surfaces, text roles, accent, danger, border, radius, spacing.
4. Match density to task and device; a HUD, inventory grid, and purchase prompt need different topologies.

### Core principles

- **Topology:** one justified shape per screen job; not everything is a centered modal.
- **Hierarchy:** one object or action gets the strongest contrast and scale.
- **Flow:** one owner per repeated flow: `UIListLayout`, `UIGridLayout`, or shared-column math.
- **Density:** size panels around useful content, not viewport space.
- **Bounds:** sum widths, gaps, padding, borders, and minimums.
- **Alignment:** shared layouts, fixed icon slots, matching anchors.
- **State:** active, locked, selected, and disabled states need more than color.
- **Input:** hover only where it exists; touch, gamepad, keyboard, and reduced motion need equivalents.
- **Verification:** inspect target viewports for clipping, overflow, hierarchy, and focus order.

### Styling, flex, and corners

- Stylesheets: `StyleSheet` rules attach via `StyleLink`, overriding properties globally. Tokens are sheet attributes used as `$Token`; themes swap via `StyleDerive`. Prefer styles for shared values, `:Hover` states, and `@Query` rules (input, text size, reduced motion).
- Flex: `UIListLayout.HorizontalFlex`/`VerticalFlex` at container level, `UIFlexItem` per child. No `UIFlexLayout` class exists.
- Per-corner `UICorner` radii (`TopLeftRadius` etc.) need the New UI Capabilities beta; never style `CornerRadius` and individual radii together.

### Neutral fallback

One restrained surface and border language, one display role, one body role, one accent. Prefer readable contrast over ornamental depth.

### Anti-patterns

Oversized shells, guessed offsets in managed layouts, blank item boxes, color-only state, mouse-only feedback, decoration before hierarchy.

> Stylesheets, flex, per-corner radii, composition, states, and QA: [references/full.md](references/full.md)
