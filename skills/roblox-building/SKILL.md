---
name: roblox-building
description: "Use when building Roblox geometry, maps, props, or generated assets with MCP or standalone Luau."
last_reviewed: 2026-07-12
sources:
  - original
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/studio/mcp.md
---

## When to Load

Load when building physical geometry, maps, props, or environment assets in Roblox Studio through MCP or standalone scripts. Covers spatial planning, CSG, generated/reused assets, scale, and verification. See `references/full.md` for complete patterns.

## Quick Reference

### MCP Build Mode
1. Discover Studio/context, then inspect Workspace and existing asset conventions.
2. Establish a named build root, origin, coordinate system, and geometry/asset manifest.
3. Build in bounded phases: ground → zone shells → landmarks → props → environment.
4. Read back after every asset, script, or geometry batch before continuing.
5. Validate structure, capture a deliberate view, and playtest traversal when relevant.

### Asset Choice
- Inspect and reuse a compatible existing asset first.
- Use `search_asset` + `insert_asset` for Creator Store assets when provenance and licensing are acceptable.
- For cross-owner or paid assets, surface creator/source/price and get explicit consent before insertion.
- Use `generate_procedural_model` for configurable primitive-part props and blockouts.
- Use `generate_mesh` for custom textured props and `generate_material` for surface variants.
- Use `store_image`/`upload_image` only for permitted images; pass a returned `generationId` to `wait_job_finished` before dependent work.
- Fall back to native Parts/CSG and report unavailable or unsuitable generation.

### Player Scale
Player ~5 studs | Door 4w×7h | Ceiling 10-14 | Counter 3.5-4 | Seat 1.5 | Path 6+

### Spatial Rules
- Named dimensions manifest, no magic numbers.
- Offset sub-parts from anchor CFrames, not guessed world coordinates.
- Snap to 0.125/0.25/0.5 studs.
- Build complex CSG near origin, then `PivotTo` the destination.
- Set `Anchored`, `CanCollide`, `CastShadow`, `Color`, and `Material` explicitly.

### Acceptance
**Prop:** named model, pivot, scale, bounds, materials, collision, anchoring, no loose parts, asset provenance.
**Map:** root/origin, zones, landmarks, spawns, path widths, traversal, and bounds checks excluding Baseplate/Terrain/SpawnLocation.
**Evidence:** structural readback plus screenshot when supported, console/runtime result when playtested.

### Anti-Patterns
Guessing coords | unanchored parts | hardcoded world positions | silent CSG failures | >20-30 parts/call | default gray | claiming generation succeeded without readback

**Need detail?** Load `references/full.md` for CSG wrappers, map structure, validation scripts, asset recipes, and evidence workflows.
