---
name: roblox-building
description: "Use when building Roblox geometry or maps with MCP or scripts, including CSG, spatial coordination, scale, and platform quirks."
last_reviewed: 2026-05-27
sources: [original]
---

## When to Load

Load when building physical geometry in Roblox Studio — via MCP or standalone scripts. Covers CSG operations, spatial coordination, and platform quirks. See `references/full.md` for complete patterns, build process, and validation scripts.

## Quick Reference

### MCP Mode (if using MCP bridge)
Every MCP call is a blank slate. Re-acquire refs at start of EVERY call. Never guess coords from chat — READ from workspace first.

```luau
local model = workspace:FindFirstChild("MyBuild")
if not model then model = Instance.new("Model"); model.Name = "MyBuild"; model.Parent = workspace end
```

### Player Scale
Player ~5 | Door: 4w×7h | Ceiling: 10-14 (rooms) | Counter: 3.5-4 | Seat: 1.5 | Path: 6+ wide

### Spatial Patterns
- **Geometric Manifest**: Named dims table (`Def = {Width=6, Depth=3, ...}`), no magic numbers
- **Relative Positioning**: All sub-parts offset from anchor CFrame, never hardcoded world coords
- **Grid Snapping**: Snap to 0.125/0.25/0.5 stud increments

### CSG Essentials
- **Epsilon Rule**: Cutters overlap boundaries by ~0.05 studs (coplanar = Z-fighting)
- **Safe Wrapper**: `pcall` SubtractAsync/UnionAsync, verify `result:IsA("BasePart")`, copy CFrame/Color/Material
- **Rules**: Shallow trees. Build near origin, PivotTo destination. No MeshPart/Terrain. `CollisionFidelity.Box` on decorative unions

### Platform Quirks
- **Cylinders**: Extend X-axis. Rotate 90° Z for upright | **Wedges**: Tip +Z default, `-π/2` X = up
- **Neon**: Glows no light — add PointLight child | **Defaults**: Always `Anchored=true`, explicit Color/Material

### Anti-Patterns
Guessing coords | Unanchored | Hardcoded positions | Block-only | Silent CSG fails | >30 parts/call | Default gray

### Build Process (Objects)
Assess → Plan (named dims, anchor) → Build (relative offsets, ≤20 parts/call) → Validate

### Build Process (Maps)
Layout → Ground (floors, Origin) → Zone shells → Landmarks → Fill props → Environment (lighting, spawns)

### Map Folder Structure
`workspace/MapName/` → `Origin` (0,0,0), `Terrain/`, `Zone_*/` (Floor, Walls/, Props/), `Landmarks/`, `Lighting/`, `Spawns/`
