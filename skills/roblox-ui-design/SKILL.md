---
name: roblox-ui-design
description: "Use for Roblox UI composition, hierarchy, visual systems, style inheritance, accessibility, and design review."
last_reviewed: 2026-07-26
sources:
  - https://create.roblox.com/docs/production/publishing/adaptive-design
  - https://create.roblox.com/docs/production/publishing/accessibility
  - https://create.roblox.com/docs/ui/styling
  - original
---

# Roblox UI Visual Design

## When to Load

Load for UI design or review. Existing style and art direction take priority. Otherwise derive a restrained system from the game fantasy and screen job. Load `roblox-gui` for mechanics.

## Quick Reference

### Establish the visual system

1. Inspect existing surfaces, type roles, borders, depth, icons, spacing, and action colors. Reuse consistent tokens.
2. If no style exists, name the screen job and game fantasy before choosing colors, fonts, or decoration.
3. Define a small token set: background, surface, raised surface, text, muted text, accent, danger, border, radius, spacing, and type roles.
4. Choose density from the task and device. A HUD, inventory grid, settings list, and purchase prompt should not share one topology.
5. Use simulator styling only when the game or art direction calls for it. The full reference keeps an optional recipe.

### Core principles

- **Topology:** choose single-focus, collection, compare, HUD, list, or another justified shape. Do not force every task into a centered modal.
- **Hierarchy:** one object, state, or action gets the strongest contrast and scale. Quiet secondary content.
- **Flow:** each repeated flow has one owner: `UIListLayout`, `UIGridLayout`, or shared-column math.
- **Density:** size the complete panel around useful content. Do not stretch shells or add metadata to occupy space.
- **Bounds:** sum widths, gaps, padding, borders, and minimums. Keep strokes and backings inside parents.
- **Alignment:** use shared layouts, fixed icon slots, and matching anchors.
- **State:** active, available, locked, completed, selected, and disabled states need more than color.
- **Input:** design hover only where it exists. Touch, gamepad focus, keyboard, and reduced motion need equivalent feedback.
- **Verification:** inspect representative target viewports for clipping, overflow, dead space, type, hierarchy, and focus order.

### Neutral fallback

Use one restrained surface and border language, one display role, one body role, and one accent. Let game content, artwork, and action importance create identity. Prefer readable contrast and clear grouping over thick outlines, ornamental depth, or genre assumptions.

### Anti-patterns

Oversized shells, guessed offsets in managed layouts, drifting actions, blank item boxes, color-only state, mouse-only feedback, decoration before hierarchy, and a familiar simulator skin pasted over unrelated art direction.

> Style inference, optional simulator recipe, composition, interaction states, and QA: [references/full.md](references/full.md)
