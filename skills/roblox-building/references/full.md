# Building 3D in Roblox — Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

Use this skill when creating physical geometry in Roblox Studio — via MCP or standalone scripts. Covers single objects, room-scale structures, and multi-zone maps.

## MCP Mode (if using MCP bridge)

MCP code execution is stateless. Every call is a blank slate.

1. **Variables don't persist** between calls.
2. **Object references are lost** between calls.
3. **Fix**: Re-acquire references at the start of EVERY call.

```luau
-- MUST be at the start of every MCP call
local model = workspace:FindFirstChild("MyBuild")
if not model then
    model = Instance.new("Model")
    model.Name = "MyBuild"
    model.Parent = workspace
end
```

**Ground Truth Rule**: Never guess coordinates from chat history. If you need the position/size of a previously created part, READ it from workspace first:

```luau
local existing = model:FindFirstChild("TableTop")
if existing then
    print(existing.CFrame, existing.Size) -- read before calculating offsets
end
```

## Player Scale Reference

- Player height: ~5 studs
- Doorway: 4 wide × 7 tall
- Ceiling height: 10-14 studs (rooms), 16+ (halls)
- Table/counter top: 3.5-4 studs from floor
- Seat height: ~1.5 studs from floor
- Paths: minimum 6 studs wide (10+ for main roads)
- Stair step: 1 stud rise, 1.5 stud run

## Build Process

### Objects (single Model)

1. **Assess** — Do you know the components, scale, and style? If not, ask.
2. **Plan** — Declare dimensions as named variables. Choose an anchor part.
3. **Build** — Generate parts with relative positioning. Split across calls if >20 parts.
4. **Verify** — Run validation (check Anchored, below-floor, default colors).

### Maps (multi-zone)

1. **Layout** — Define total size, zone breakdown, gameplay type. If any is vague, ask.
2. **Ground** — Floor planes, boundaries, Origin anchor, folder hierarchy.
3. **Zone shells** — Floor sections, walls, dividers per zone.
4. **Landmarks** — Orientation structures (towers, fountains, trees).
5. **Fill** — Props, furniture, vegetation per zone.
6. **Environment** — Lighting, Atmosphere, SpawnLocations.

## Spatial Patterns

### Geometric Manifest (named dimensions, no magic numbers)

```luau
local Def = {
    Width = 6.0,
    Depth = 3.0,
    Height = 2.8,
    TopThickness = 0.2,
    LegSize = 0.3,
    LegInset = 0.1,
}
```

### Relative Positioning (anchor pattern)

All sub-parts position relative to an anchor part's CFrame. Never use hardcoded world coordinates.

```luau
local top = Instance.new("Part")
top.Size = Vector3.new(Def.Width, Def.TopThickness, Def.Depth)
top.CFrame = CFrame.new(0, Def.Height - Def.TopThickness / 2, 0)
top.Anchored = true
top.Parent = model

-- Legs relative to top
local legH = Def.Height - Def.TopThickness
local leg = Instance.new("Part")
leg.Size = Vector3.new(Def.LegSize, legH, Def.LegSize)
local ox = Def.Width / 2 - Def.LegSize / 2 - Def.LegInset
local oz = Def.Depth / 2 - Def.LegSize / 2 - Def.LegInset
leg.CFrame = top.CFrame * CFrame.new(ox, -(Def.TopThickness / 2 + legH / 2), oz)
leg.Anchored = true
leg.Parent = model
```

### Grid Snapping

Snap dimensions to consistent increments (0.125, 0.25, or 0.5 studs). Avoid arbitrary decimals like 0.333 or 1.17 which compound into visible gaps.

## CSG (Union / Subtract)

### The Epsilon Rule

Cutters MUST slightly overlap boundaries they cut through. Coplanar surfaces cause Z-fighting or leave microscopic skins.

```luau
local EPSILON = 0.05

-- Hole through a 1-stud thick wall
local wall = Instance.new("Part")
wall.Size = Vector3.new(10, 10, 1)

local cutter = Instance.new("Part")
-- Add EPSILON*2 to the axis passing through the wall
cutter.Size = Vector3.new(2, 2, 1 + EPSILON * 2)
cutter.CFrame = wall.CFrame
```

### Safe CSG Wrapper

CSG operations are async and can fail. Always pcall, verify, and clean up.

```luau
local success, result = pcall(function()
    return basePart:SubtractAsync({cutterPart})
end)

if success and result and result:IsA("BasePart") then
    result.CFrame = basePart.CFrame -- preserve exact transform
    result.UsePartColor = true
    result.Color = basePart.Color
    result.Material = basePart.Material
    result.Name = basePart.Name
    result.Anchored = true
    result.Parent = basePart.Parent

    basePart:Destroy()
    cutterPart:Destroy()
else
    warn("CSG failed:", result)
    cutterPart:Destroy()
end
```

### CSG Rules

- Keep CSG trees shallow. Don't subtract from a part that was already unioned multiple times.
- Perform complex CSG near origin (0,0,0), then PivotTo() the final model to its destination. Floating-point precision degrades far from origin.
- GeometryService only supports Part and PartOperation. NOT MeshPart or Terrain.
- Set `CollisionFidelity = Enum.CollisionFidelity.Box` on decorative unions for performance.

## Platform Quirks

### Cylinder Orientation

Cylinders extend along the **X-axis** by default. To stand one upright:

```luau
local pillar = Instance.new("Part")
pillar.Shape = Enum.PartType.Cylinder
pillar.Size = Vector3.new(10, 2, 2) -- Length, Diameter, Diameter
pillar.CFrame = CFrame.new(0, 5, 0) * CFrame.Angles(0, 0, math.pi / 2)
```

### WedgePart Orientation

The zero-height edge (tip) points toward +Z by default.

| Desired tip direction | Rotation |
|---|---|
| Up (+Y) | `CFrame.Angles(-math.pi/2, 0, 0)` |
| Down (-Y) | `CFrame.Angles(math.pi/2, 0, 0)` |
| Forward (+Z) | none |
| Backward (-Z) | `CFrame.Angles(math.pi, 0, 0)` |

### Neon Material

Neon glows visually but does NOT cast light on surroundings. Add a PointLight/SpotLight as a child for actual illumination.

### Default Part Properties

Always set explicitly:
- `Anchored = true` (defaults to false!)
- `CanCollide = true` (false for small decorative clutter)
- `CastShadow = true` (false for invisible triggers)

## Anti-Patterns

- **Guessing coordinates** — Read from workspace, don't rely on chat memory.
- **Unanchored parts** — They fall. Always set Anchored = true.
- **Hardcoded world positions** — Use relative offsets from anchor CFrame.
- **Block-only for organic shapes** — Use CSG, Cylinders, Spheres, WedgeParts.
- **Silent CSG failures** — Always pcall and verify result is BasePart.
- **Building everything in one call** — Split by phase. 20-30 parts per call max.
- **Floating geometry** — All structures must connect to ground or parent structure.
- **Default colors** — Always set explicit Color and Material. Default gray = unfinished.

## Validation Script

Run after building to catch common issues:

```luau
local TARGET = "MyBuild" -- change to your model/folder name
local root = workspace:FindFirstChild(TARGET)
if not root then print("[ERROR] " .. TARGET .. " not found"); return end

local errors, warnings, parts = 0, 0, 0
for _, desc in ipairs(root:GetDescendants()) do
    if desc:IsA("BasePart") then
        parts += 1
        if not desc.Anchored then
            print("[ERROR] " .. desc:GetFullName() .. " not Anchored")
            errors += 1
        end
        if desc.Position.Y - desc.Size.Y / 2 < -0.5 then
            print("[WARN] " .. desc.Name .. " below floor")
            warnings += 1
        end
        if desc.Color == Color3.new(163/255, 162/255, 165/255) and desc.Material == Enum.Material.Plastic then
            print("[WARN] " .. desc.Name .. " uses default color/material")
            warnings += 1
        end
    end
end
print(string.format("Parts: %d | Errors: %d | Warnings: %d", parts, errors, warnings))
```

If any errors: fix and re-verify. Warnings are advisory.

## Map Folder Structure

```
workspace/
  MapName/                  (Folder)
    Origin                  (invisible anchor at 0,0,0)
    Terrain/                (ground planes)
    Zone_Spawn/
      Floor
      Walls/
      Props/
    Zone_Arena/
    Landmarks/
    Lighting/               (PointLights, SpotLights)
    Spawns/                 (SpawnLocation instances)
```
