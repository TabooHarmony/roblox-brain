---
name: roblox-building
description: "Use when building geometry, maps, props, or generated assets with MCP or standalone Luau."
last_reviewed: 2026-08-07
sources:
  - original
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/studio/mcp.md
  - https://create.roblox.com/docs/reference/engine/classes/MeshPart
  - https://create.roblox.com/docs/reference/engine/classes/SurfaceAppearance
  - https://create.roblox.com/docs/tutorials/use-case-tutorials/ui/proximity-prompts
  - https://create.roblox.com/docs/production/game-design/design-for-roblox
  - https://create.roblox.com/docs/production/game-design/core-loops
  - https://create.roblox.com/docs/production/game-design/onboarding
  - https://create.roblox.com/docs/production/game-design/onboarding-techniques
---

# Roblox Building

## When to Load

Load for Roblox geometry, props, maps, routes, landmarks, or spatial onboarding via MCP or Luau. See `references/full.md` for complete patterns.

## Quick Reference

### MCP Build Mode
1. Discover Studio, Workspace, and existing asset conventions.
2. Name the build root, origin, coordinates, and asset manifest.
3. Build in bounded phases and read back each asset, script, or geometry batch.
4. Validate structure, capture a deliberate view, and playtest traversal.

### Asset Choice
- Inspect and reuse a compatible existing asset first.
- For Creator Store, cross-owner, or paid assets, surface source, creator, price, and licensing before insertion.
- Use `generate_procedural_model` for blockouts, `generate_mesh` for textured props, and `generate_material` for surfaces.
- For meshes, read back `MeshPart`/`SurfaceAppearance`, bounds, collision fidelity, anchoring, and provenance; preview representative quality levels.
- Use image tools only for permitted inputs and wait for the returned job before dependent work.
- Fall back to native Parts/CSG and report unavailable or unsuitable generation.

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
**Evidence:** structural readback plus screenshot when supported, console/runtime result when playtested.

### Anti-Patterns
Guessing coordinates | unanchored or duplicate parts | hardcoded world positions | silent CSG failure | oversized batches | claims without readback

**Need detail?** Load `references/full.md` for CSG wrappers, map structure, validation scripts, asset recipes, and evidence workflows.
