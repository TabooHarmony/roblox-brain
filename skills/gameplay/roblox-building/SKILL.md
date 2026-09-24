---
name: roblox-building
description: "Use when building geometry, maps, props, or generated assets with MCP or standalone Luau."
last_reviewed: 2026-08-31
sources:
  - original
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
---

# Roblox Building

## When to Load

Load for geometry, props, maps, and spatial onboarding via MCP or Luau.

## Quick Reference

### MCP Build Mode
1. Inspect Studio, Workspace, and existing assets.
2. Name the root, origin, dimensions, and assets.
3. Build in phases; read back each batch.
4. Verify the tree, view, and traversal.

### Asset Choice
- Search project assets and Toolbox before generating. Check type, creator, price, scripts, and fit.
- Before paid or cross-owner insertion, disclose creator, ID, price, and rights. Inspect scripts and dependencies; remove unneeded code and test in scene. See `roblox-security`.
- MCP: `generate_procedural_model`, `generate_mesh`, `generate_material`.
- Studio Assistant previews models, restyles textures, and segments imported meshes. These aren't confirmed MCP tools; see full reference.
- Check mesh bounds, collision, PBR, and quality levels.
- Use permitted images; wait for jobs to finish.
- `EditableImage`/`EditableMesh` have permission and memory limits.
- Use native Parts/CSG when reuse or generation is unsuitable.

### Player Scale
Player ~5 studs | Door 4w×7h | Ceiling 10-14 | Counter 3.5-4 | Seat 1.5 | Path 6+

### Spatial Rules
- Name dimensions; offset sub-parts from anchor CFrames, not guessed world coordinates.
- Snap to 0.125/0.25/0.5 studs.
- Build complex CSG near origin, then `PivotTo` the destination.
- Set anchoring, collision, shadows, color, and material explicitly.

### Acceptance
**Prop:** named model, pivot, scale, bounds, materials, collision, anchoring, no loose parts, asset provenance.
**Map:** root/origin, zones, landmarks, spawns/return paths, path widths, traversal, and bounds checks excluding Baseplate/Terrain/SpawnLocation.
**Evidence:** readback, a view when supported, and playtest results.

### Anti-Patterns
Guessing coordinates | unanchored or duplicate parts | hardcoded world positions | silent CSG failure | oversized batches | claims without readback

**Details:** `references/full.md` covers maps, validation, and assets.
