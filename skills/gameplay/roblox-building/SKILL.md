---
name: roblox-building
description: "Use when building or editing geometry, maps, props, or generated assets with MCP or standalone Luau."
when_to_use: "Also for fixing map gaps, z-fighting, scale, collisions or players escaping the map, placing store assets, and reviewing a map layout."
last_reviewed: 2026-11-27
sources:
  - original
  - https://create.roblox.com/docs/en-us/projects/assets/privacy.md
  - https://devforum.roblox.com/t/large-scale-roblox-terrain-the-ultimate-guide/405672
  - https://devforum.roblox.com/t/a-complete-guide-to-editableimages/3858566
  - https://create.roblox.com/docs/reference/engine/classes/EditableImage
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/studio/mcp.md
  - https://create.roblox.com/docs/production/game-design/core-loops
  - https://create.roblox.com/docs/production/game-design/onboarding
  - https://create.roblox.com/docs/production/game-design/onboarding-techniques
  - https://create.roblox.com/docs/projects/assets/toolbox
  - https://create.roblox.com/docs/scripting/security/third-party-vulnerabilities
  - https://create.roblox.com/docs/assistant/guide
  - https://create.roblox.com/docs/parts/custom-terrain-materials
  - https://create.roblox.com/docs/reference/engine/classes/EditableMesh
  - https://create.roblox.com/docs/art/modeling/cage-meshes
---

# Roblox Building

## When to Load

Geometry, props, maps and spatial onboarding via MCP or Luau.

## Quick Reference

### MCP Build Mode
Inspect Workspace/assets; name root, origin, dimensions. Build in phases with readback; verify tree, view, traversal.

### Asset Choice
- Search project and Toolbox first; check creator, price, fit. Read script counts, not descriptions.
- Paid/cross-owner: disclose creator, ID, price, rights first. See `roblox-security`.
- MCP: `generate_procedural_model`, `generate_mesh`, `generate_material`; wait for jobs.
- Blank texture/invisible mesh: usually a missing experience grant. See `roblox-studio-mcp`.

### Meshes and terrain
- A MeshPart from an `EditableMesh` keeps using it: destroy the mesh only after that MeshPart. Budget is per device: share meshes, upload static ones.
- Use `EditableMesh` batch APIs (`BatchAdd`, `BatchSetValues`). Centre vertices on the part origin.
- Expanded Terrain: `Terrain:SetMaterialSlot` (slots 2-63).

### Player Scale
Player ~5 studs | Door 4w×7h | Ceiling 10-14 | Counter 3.5-4 | Seat 1.5 | Path 6+

### Spatial Rules
- Name dimensions; offset sub-parts from anchor CFrames, never guessed coordinates.
- Snap to 0.125/0.25/0.5 studs. Build complex CSG near origin, then `PivotTo` the destination.
- Set anchoring, collision, shadows, material explicitly.

### Acceptance
**Prop:** named model, pivot, scale, bounds, materials, collision, anchoring, provenance.
**Map:** root/origin, zones, landmarks, spawns, traversal, bounds.
**Evidence:** readback, view when supported, playtest results.

### Anti-Patterns
Guessing coordinates | unanchored props | coplanar overlaps (inset 0.01) | silent CSG failure | claims without readback

**Details:** `references/full.md`.
