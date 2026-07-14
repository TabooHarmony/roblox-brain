---
name: roblox-ui-design
description: "Roblox UI design with simulator default and existing-style inheritance. Use with `roblox-gui`."
last_reviewed: 2026-07-13
sources:
  - https://create.roblox.com/docs/production/publishing/adaptive-design
  - https://create.roblox.com/docs/production/publishing/accessibility
  - https://create.roblox.com/docs/ui/styling
  - [original]
---

# Roblox UI Visual Design

## When to Load

Load for Roblox UI design/review. No style source: use the simulator default. Existing UI/reference: preserve its style while applying these rules. Load `roblox-gui` for mechanics.

## Quick Reference

### Style

Existing UI/reference > explicit art direction > default.

For existing style, inspect surfaces, fonts, borders, depth, icons, spacing, and action colors. Reuse those tokens. Borrow style, not broken geometry. Do not import conflicting simulator conventions.

### Core Principles

- **Topology:** choose composition from the job: single-focus, collection, compare, HUD, list, or another justified shape. Do not force every task into one modal.
- **Hierarchy:** one focal object, state, or action gets the strongest contrast and scale. Quiet secondary content.
- **Flow:** each repeated flow has one owner: `UIListLayout`, `UIGridLayout`, or shared-column math. Do not mix layout objects with guessed offsets.
- **Density:** size the complete panel around useful content. Do not stretch shells or add metadata to fill space.
- **Bounds:** sum widths, gaps, padding, borders, and minimums. Keep content, strokes, and backings inside parents.
- **Alignment:** use shared layouts, fixed icon slots, and matching anchors. Do not independently offset paired icons and labels.
- **State:** active, available, locked, completed, and disabled states need structural/textual differences. Color is not the only signal.
- **Verification:** inspect the target viewport for clipping, overflow, dead space, type, and hierarchy. A valid tree is not proof of good composition.

### Default

Default: bold, layered, toy-like UI over 3D gameplay.

- Base: charcoal/warm brown. Green = claim/buy; red = danger/close; yellow = premium; blue = navigation/currency; purple = rare.
- Display: `FredokaOne` (cute) or `Oswald` (action); body: `BuilderSans`.
- Display type covers titles, section labels, item names, and key stats. Secondary values stay clean and smaller. Outline title and primary CTA only.
- Use one neutral outline per surface. Backings share the radius or stay inset. Put color in fills, active insets, or small cues, not every perimeter.
- Content cards need a centered focal icon/art placeholder. Do not leave item grids blank.

### Anti-Patterns

Oversized shells, wide panels around narrow stacks, fixed offsets in auto-sized flows, drifting actions, colored outlines on every card, blank item boxes, independent icon/label offsets, or simulator styling pasted over an existing identity.

> Full specs and QA checklist: [references/full.md](references/full.md)
