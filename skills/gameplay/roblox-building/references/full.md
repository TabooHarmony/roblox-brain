# Building 3D in Roblox: Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

Use this skill when creating physical geometry in Roblox Studio (via MCP or standalone scripts). Covers single objects, room-scale structures, and multi-zone maps.

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

## MCP Build Contract

Use the shared `roblox-studio-mcp` session contract. Before changing a place:

1. List/select the intended Studio and call `get_studio_state`.
2. Confirm the target datamodel and inspect `Workspace`, existing map roots, coordinate conventions, scripts, and reusable assets.
3. Declare a build root, origin, named dimensions, asset manifest, and acceptance gates.
4. Apply one bounded phase at a time. Re-acquire references in every stateless `execute_luau` call.
5. Read back the tree and properties before starting the next phase.
6. Start play only when runtime behavior matters. Capture console, navigation, and visual evidence, then stop play.

Keep a one-line mutation record per mutating step (target, pre-state, intended change, compensating action) and reconcile ambiguous tool timeouts by reading the target back before retrying; destructive tests must confirm actual store and endpoint destinations rather than trusting the place label. Full pattern: `roblox-studio-mcp`.

If a capability is unavailable, switch to the offline Luau path and identify the missing evidence instead of claiming the build was verified.

## Asset-Aware Prop Workflow

**Toolbox is a production asset source, not just a shortcut for prototypes.** Check existing project assets and Studio's Toolbox (Creator Store and your/group inventory) before generating a replacement for a common prop, mesh, material, sound, or UI asset. Roblox's [Toolbox guide](https://create.roblox.com/docs/projects/assets/toolbox) covers category search, creator/price filters, detail previews, and insertion; its [building curriculum](https://create.roblox.com/docs/tutorials/curriculums/core/building/apply-polished-assets) demonstrates reusing a Creator Store asset library to replace greybox scenery. Choose the least risky source that fits the game's scale, style, and gameplay:

1. **Find candidates:** search the project first, then Toolbox/Creator Store or creator inventory by category and purpose; narrow by creator, asset type, price, and rating. Inspect the detail page's creator, previews, description, script count, and geometry complexity. Popularity and a verified creator are signals, not proof of safety or fit. If the available tool cannot show details, inspect the asset in Studio before accepting it.
2. **Decide before insertion:** compare a plausible asset with building it. Use existing or Store assets when they fit without heavy rework; build a custom asset when the mechanic, style, permissions, or performance needs demand it. Record asset ID, creator/source, type, price, usage rights, and intended parent. For cross-owner or paid results, show these to the user and get explicit consent before insertion or purchase.
3. **Inspect the inserted model:** read its entire hierarchy before play. Check Scripts/LocalScripts/ModuleScripts, package links, and nested assets; remove or disable code the game does not need. For needed code, inspect what it does, especially obfuscation, remote asset loads, and requests for sensitive capabilities. Roblox warns that [third-party models can contain backdoors](https://create.roblox.com/docs/scripting/security/third-party-vulnerabilities), and a [DevForum cleanup guide](https://devforum.roblox.com/t/clearing-your-game-of-malicious-scripts-plugins-and-backdoors/511830) shows why scanning script descendants and checking plugin provenance matter. Do not treat a scanner, rating, or sandbox as a clean bill of health; see `roblox-security` for code isolation.
4. **Fit and test:** parent under the intended build root; verify pivot, size/player scale, collisions, anchoring, materials, textures, dependent asset permissions, and scripts after insertion. Compare with the project's visual language. Playtest traversal and the asset's behavior; a model that looks right in the thumbnail can break movement or load without its dependencies.
5. **Procedural:** use `generate_procedural_model` for configurable primitive-part props, buildings, scenery, and image-guided blockouts. Pass meaningful `partNames` and user requirements as the prompt. The tool may auto-insert the result.
6. **Mesh:** use `generate_mesh` for a custom textured prop. Bound the size and triangle budget; do not treat the returned mesh as accepted until inspected.
7. **Material:** use `generate_material`, then apply and verify its returned base material and material-variant name on target parts.
8. **Image:** use `store_image` for permitted local PNG/JPG references or `upload_image` for a permitted source accepted by the live schema. Never upload external content without permission.
9. **Asset privacy (diagnosis before repair):** if an inserted or referenced image, decal, or mesh renders blank/invisible or the Output shows an asset-permission error, check the documented [asset privacy system](https://create.roblox.com/docs/projects/assets/privacy), before assuming file corruption. Owners can opt into creating Images/Decals/Meshes as **Restricted**; a game without a needed permission cannot load them, and the Output error is clickable and names the asset. Diagnose in this order: read the exact Output error → check the asset's privacy state in Creator Dashboard (Configure → Permissions) → grant the **experience** (universe ID) permission — collaborator sharing alone is not enough for runtime. Remember: insertion into a place auto-grants that experience permission and the grant is irreversible, Open Use is irreversible, and a `Decal`'s state is tied to its `Image` dependency (a restricted child inside a loaded model can still be the missing piece). See `roblox-studio-mcp` "Private-asset permission diagnosis."
10. **Wait:** if a generation returns a job ID, call `wait_job_finished` with its `generationId` before dependent edits. Follow the live tool schema because some generation tools complete or insert automatically.
11. **Place:** parent the result under the named build root, set pivot/transform, and read back class, descendants, bounds, materials, collision, anchoring, and asset provenance.
12. **Fallback:** use native Parts, CSG, primitives, and coherent materials when reuse or generation is unavailable, slow, rejected, or visually unsuitable.

Generated assets are candidates. Structural and visual review are still required.

### Studio Assistant generation (not the MCP tool list)

Roblox's [Studio Assistant guide](https://create.roblox.com/docs/assistant/guide) and [feature announcement](https://devforum.roblox.com/t/introducing-new-texture-generation-tools-segment-any-mesh-and-image-previews/4890084) describe these editor workflows. Use them when an agent can operate Studio's Assistant UI or guide a person through it; check the live tool list before assuming an MCP client can call them.

- **Restyle existing meshes:** select one or more meshes and use the ribbon button, right-click **Generate > Texture**, or Assistant's `/generate_texture`. Iterate on the generated texture, then export it to a texturing program for further editing if needed. Check the mesh and appearance afterward rather than assuming generation preserved every detail.
- **Segment imported meshes:** select the `MeshPart` itself, then use `/segment_mesh` in Assistant. Name up to five parts; suggested names for familiar objects can improve results. Run the command again on a part if you need finer division. This is an early-preview feature; the guide says it replaces the original mesh in Workspace, so inspect the new hierarchy, materials, collisions, and behavior before proceeding.
- **Preview before generating:** for text-prompt `/generate_mesh` or `/generate_procedural_model`, review the suggested part names and choose from four generated image previews before creating the final model. A supplied hint image guides the model but currently skips that four-preview step. This is an Assistant UI flow, not a promise that MCP `generate_mesh` exposes preview selection.

## Mesh-Backed Geometry

`MeshPart` is a `BasePart` with a custom mesh. Treat the visible mesh, its appearance, and its collision shape as separate review surfaces:

- read back `MeshId`/`MeshContent`, `MeshSize`, transform, bounds, `Anchored`, `CanCollide`, `CanTouch`, `CanQuery`, and `CollisionFidelity`;
- inspect a child `SurfaceAppearance` and its `ColorMap`, normal, metalness, roughness, and emissive maps when present; PBR appearance depends on device and graphics quality, so preview representative quality levels;
- do not imply that a runtime script can repair `MeshId` or most PBR maps. Resolve authoring/import issues before placement, then verify after insertion;
- record source and intended use for each non-original mesh. A repeated asset key may indicate reuse, but static equality is not proof of license or quality.

Use native Parts or CSG for simple collision and blockout geometry. Use a separate low-cost collision model when the visible mesh is large, detailed, or non-interactive. Let measured playtests and profiling, not class counts, decide performance changes.

## EditableImage and EditableMesh (runtime pixel/vertex editing)

`EditableImage` and `EditableMesh` are runtime-editable image and mesh objects (not `Instance`s, so `Instance.new` does not work). Create them through `AssetService`:

```luau
local AssetService = game:GetService("AssetService")

-- from scratch (synchronous)
local image = AssetService:CreateEditableImage({ Size = Vector2.new(256, 256) })

-- from an owned asset (async, may throw on permission/network failure)
local loaded = AssetService:CreateEditableImageAsync(Content.fromUri(assetUri))
```

Hard constraints (official):

- Creation APIs can return `nil` when the device is out of `Editable*` memory budget. Always nil-check before use. Destroy an `EditableMesh` only when no MeshPart still uses it (see lifetime below); destroy finished `EditableImage`s that nothing displays.
- In published experiences the creator must be 13+, ID-verified, and have the "Allow Mesh / Image APIs" toggle on (Game Settings → Security). Loading assets works only for assets the experience owner (or group) owns.
- `Editable*` objects do not replicate. Each client/server boundary needs its own creation; replicating edits means sending your own data (and you are then responsible for moderation of user-generated content, so prefer seed/slider parameters over free-form pixel replication).
- `EditableImage` size is fixed at creation. `EditableMesh` created from an asset is fixed-size by default (cheaper; positions/attributes editable, topology not). Non-fixed meshes: 60,000 vertex / 20,000 triangle limit.

Rendering to UI: wrap with `Content.fromObject(image)` and assign to `ImageLabel.ImageContent` (or `MeshPart.TextureContent` / `MeshPart.MeshContent`). Practitioner tip: set `ResampleMode` to `Pixelated` for crisp low-resolution renders.

Pixel work uses the `buffer` library, 4 bytes per pixel RGBA, row-major:

```luau
local w, h = image.Size.X, image.Size.Y
local px = buffer.create(w * h * 4)
for y = 0, h - 1 do
    for x = 0, w - 1 do
        local i = (y * w + x) * 4
        buffer.writeu8(px, i, r) buffer.writeu8(px, i + 1, g)
        buffer.writeu8(px, i + 2, b) buffer.writeu8(px, i + 3, 255)
    end
end
image:WritePixelsBuffer(Vector2.zero, image.Size, px)
```

Practitioner guidance (devforum, unverified by us):

- Pack a pixel as one `u32` write where possible instead of four `u8` writes; batch per-row and write once per frame. A one-`EditableImage`-update-per-frame limit has been reported, so profile before assuming per-frame writes are free.
- Expensive per-pixel loops (raycast renderers, fractals) benefit from Parallel Luau: compute row buffers inside Actors, then `task.synchronize` before `WritePixelsBuffer` (it is not callable in parallel).
- For painting on meshes: `EditableMesh:RaycastLocal` gives the hit UV, then draw at that coordinate on the paired `EditableImage` (`DrawImageTransformed` for cropping/rotation, `DrawCircle`/`DrawRectangle`/`DrawLine` for shapes).
- `EditableMesh` IDs (vertex/face/UV/normal) are stable but unordered with holes; iterate `GetVertices()`/`GetFaces()` results, never `1..count`. Use the batch APIs below over per-element calls for bulk edits; re-derive collision via `AssetService:CreateMeshPartAsync` at the end of a conceptual edit, not per hit (field-measured: a visual rebuild took 0.5 ms, a collision rebuild 15-19 ms).

### EditableMesh lifetime, budget and batch APIs

**A MeshPart built from an EditableMesh keeps referencing it.** Verified in Studio (November 2026): a MeshPart from `AssetService:CreateMeshPartAsync(Content.fromObject(editableMesh))` keeps `MeshContent.SourceType == Object`. After `editableMesh:Destroy()`, `CreateEditableMeshAsync(meshPart.MeshContent)` reads back 0 vertices, although `MeshPart.Size` is unchanged. So destroy an EditableMesh only when no MeshPart still uses it, or after destroying that MeshPart. A displayed mesh stays alive and keeps counting against the editable memory budget; to keep geometry permanently, upload or publish it as an asset instead.

**The budget is shared per device.** Field-measured: a Studio client allowed only about 8 growable meshes (`AssetService:CreateEditableMesh()`) at once, further creates returning nil, while 300 fixed-size copies fit. In another project eleven static decor props filled the budget and later gameplay meshes failed to build ("EditableMesh budget is full"), silently breaking a core action. Practice:

- Build growable, copy with `CreateEditableMeshAsync(Content.fromObject(mesh), { FixedSize = true })`, then destroy the growable one once nothing displays it. Fixed-size meshes still allow position and color edits (dents, tints), not topology, and `Clear()` throws on them.
- Many MeshParts can share one mesh: calling `CreateMeshPartAsync` twice on the same content and `:Clone()` of the result both work. Build each look once.
- A mesh that never changes at runtime belongs in an uploaded asset: no editable budget, instant to appear. After adding decor, exercise gameplay paths and search logs for "budget".

**Batch APIs (2026-10).** `EditableMesh` now has batch methods that replace per-element loops: `BatchAdd(Enum.MeshAttribute.X, data)` creates vertices, normals, UVs, colors or faces and returns their ids in order; `BatchGetValues(ids)` / `BatchSetValues(ids, values)` read and write positions, normals, UVs, colors or alphas (`BatchSetValues(normalIds, nil)` resets normals to auto-computed); `BatchGetFaceAttributes`, `BatchSetFaceAttributes`, `BatchGetVertexAttributes`, `BatchGetVertexFaceAttributes`, `BatchSetVertexFaceAttributes` handle per-corner ids; `BatchRemove(faceIds)` removes faces (follow with `RemoveUnused()`). `AddFace(...)` accepts a triangle or a quad (a quad counts as 2 triangles) and, for a vertex already on another face, reuses that face's normal, UV and color ids, which gives smooth shading by default. <!-- temporal: 2026-11 -->

```luau
-- Illustrative: build a flat grid of triangles with batch calls.
local AssetService = game:GetService("AssetService")

local function buildGrid(n: number, step: number): EditableMesh?
    local mesh = AssetService:CreateEditableMesh()
    if not mesh then
        return nil -- editable budget exhausted
    end
    local positions = {}
    local half = n * step / 2
    for z = 0, n do
        for x = 0, n do
            -- Centre vertices on the part origin (see "fixed-size centring" below).
            table.insert(positions, Vector3.new(x * step - half, 0, z * step - half))
        end
    end
    local v = mesh:BatchAdd(Enum.MeshAttribute.Vertex, positions)
    local faces = {}
    for z = 0, n - 1 do
        for x = 0, n - 1 do
            local i = z * (n + 1) + x + 1
            table.insert(faces, { v[i], v[i + n + 1], v[i + n + 2] })
            table.insert(faces, { v[i], v[i + n + 2], v[i + 1] })
        end
    end
    mesh:BatchAdd(Enum.MeshAttribute.Face, faces)
    return mesh
end
```

**Field-measured EditableMesh lessons.**

- **Deformable props need inner vertices.** Give faces where hits land an even grid (about 0.12-0.22 studs); a plain box has none to push. Avoid triangle-fan caps, which dent into starbursts.
- **Give dented faces their own normals and colors.** Baked meshes share normals and colors across faces, so moving one vertex reshades many. Copy per-corner normals and colors on the growable mesh before the fixed-size copy, recompute touched face normals from `(v2 - v1):Cross(v3 - v1)`, and re-smooth only dented corners.
- **A MeshPart stretches its mesh to `Size`.** After a dent changes the bounds, set `Part.Size = mesh:GetSize()` and offset by `mesh:GetCenter()`.
- **Centre fixed-size vertices on the part origin** (for example -2..2, not 0..4); an offset mesh drew shifted from its part.
- **`RaycastLocal(origin, direction)` uses the direction's length and hits back faces.** Start outside the mesh (hit point plus normal) and keep only hits whose face faces the ray, or thin shells report the far wall.
- **Bake explicit per-corner normals.** Without them, automatic normals smooth across welded vertices and light bleeds across sharp corners; chunked shells with unwelded seams then shade differently. An undamaged mesh that is already stripey means the bake is wrong.
- **`CreateMeshPartAsync` defaults to Plastic,** whose PBR grain shows over flat vertex colors; set `SmoothPlastic` for flat-colored generated meshes.
- **Cost is per mesh, not per face:** about 44 ms per `CreateMeshPartAsync` regardless of size. Keep small groups (under about 30 Parts) as Parts, and show cheap box stand-ins while a long bake runs.
- **Runtime MeshParts from EditableMesh cast no shadow in Studio** even with `CastShadow = true`; a Part beside them did. Check shadows on a live client before using them for large world props.

### EditableImage: projected sampling, decals and publishing (2026-10/11)

- `EditableImage:SampleImageProjected` was added for projected sampling; read its reference page before use.
- `AssetService:CreateDecalAsync({ ... })` builds a `Decal` from color and PBR maps, each a `Content.fromObject(editableImage)`; asset ids and URIs are not accepted (load images with `CreateEditableImageAsync` first). The decal comes back unparented: set `Face` and parent it to a part.
- `AssetService:PromptCreatePlatformContentAsync(player, editableImage, Enum.AssetType.Image)` (server only) shows a publish dialog that saves a player's creation to their inventory. `PromptCreateAssetAsync` is gone from the reference. You remain responsible for moderating what players make. <!-- temporal: 2026-11 -->

## Player Scale Reference

- Player height: ~5 studs
- Doorway: 4 wide × 7 tall
- Ceiling height: 10-14 studs (rooms), 16+ (halls)
- Table/counter top: 3.5-4 studs from floor
- Seat height: ~1.5 studs from floor
- Paths: minimum 6 studs wide (10+ for main roads)
- Stair step: 1 stud rise, 1.5 stud run

## Custom terrain materials (Expanded Terrain, 2026-11)

With **Expanded Terrain** enabled on `Workspace` (per place, off by default; the place must reopen, and in Team Create you must exit and wait about 15 s), terrain supports up to 62 custom paintable materials, each a base material plus an optional `MaterialVariant` and a color tint, so several shades of grass can coexist instead of overriding one base material globally. Expanded Terrain also shrinks terrain's share of place size and improves terrain streaming and load. Places edited during early access still need the property set, or custom materials can show as grass. <!-- temporal: 2026-11 -->

- **Studio:** Terrain Editor material picker → **+**; manage in Window → 3D → Terrain Materials Manager. Changing a material updates all terrain using it; deleting a used one paints that terrain bright purple.
- **Scripts:** `Terrain:SetMaterialSlot(slotIndex, baseMaterial, materialVariantName, color)` configures slots `2`-`63` (`0` Air and `1` Water are reserved); pass `""` for a tint-only slot. `GetMaterialSlot` returns base material, variant name and color (nil when unset); `ResetMaterialSlot` clears it, and voxels still referencing it render an invalid-material indicator. Voxels reference slots through the `SolidMaterialIndex` channel of `ReadVoxelChannels`/`WriteVoxelChannels`. It throws if the variant name doesn't exist for that base material in `MaterialService`.
- **Limits from the docs:** a `MaterialVariant`'s custom physical properties are not yet respected in slots; Team Create terrain edits can mesh wrongly; with a small streaming radius, terrain thinner than 16 voxels can vanish on clients, and thinning terrain saves little memory under Expanded Terrain; heightmap and colormap imports may differ from before.

```luau
-- Illustrative: a tinted grass slot, then paint one voxel region with it.
local terrain = workspace.Terrain
terrain:SetMaterialSlot(2, Enum.Material.Grass, "", Color3.fromRGB(96, 140, 60))
print(terrain:GetMaterialSlot(2)) -- Grass, "", color
```

**Terrain placement (field-measured).** Raycasts miss terrain written in the same frame, so wait a frame after writing before placing on it. Smooth terrain's visible surface sat about 1-1.5 studs above the occupancy written, so place props on a terrain raycast hit, tilted to the hit normal and sunk slightly, never on heightfield maths.

## Cage meshes (WrapTarget / WrapLayer)

Cage meshes are invisible low-resolution surfaces that let one mesh deform over another; they power layered accessories and work on any `MeshPart` as long as all paired cages share identical UVs. Only paired cages interact, unlike collisions. In Studio, a `MeshPart` with a child `WrapTarget` is a target (authored in Blender as a render mesh plus `<Name>_OuterCage`); a `MeshPart` with a child `WrapLayer` wraps over a target (render mesh plus `<Name>_InnerCage` and `<Name>_OuterCage`). To apply a deformation, parent the target and layered `MeshPart`s in one `Model` and connect them with a `WeldConstraint`. Runtime creation and reshaping of cages is covered by the in-experience avatar creation docs. Use this for clothing-like props, armor that fits several body shapes, or one caged mesh reused on many differently shaped targets.

## Placement, orientation and measurement (field-measured)

- **Yaw direction:** `CFrame.Angles(0, theta, 0).LookVector` is `(-sin theta, 0, -cos theta)`, so a model whose front is local -Z faces +X at `theta = -math.pi/2`. A swapped table put a wall of fixtures backwards. After placing rotated fixtures, read back a child's world position against its parent.
- **`Model:GetBoundingBox` is oriented to the pivot** (the `PrimaryPart`'s if present, otherwise `WorldPivot`), so a rotated model can look unchanged when you compare bounds. Measure world extents from part corners when checking rotation.
- **Measure reference layouts from the place file.** When walking an `.rbxlx`, take bounds from `BasePart` CFrames only: Attachments carry local CFrames near the origin and stretch spans to hundreds of studs. Read the `SpawnLocation` rotation to know which way players face. Compare content by target size, not count.
- **Anchor placed props and record their support.** Unanchored props placed at a tilt or stacked slid within seconds (a quarter of a pile slid off when only its base was anchored). Anchor display props and piles, and store what each rests on (for example `HeldBy` attributes) so breaking the support releases them; "rests on top" misses wall-mounted items. Verify with a server check comparing each body to its marker after several seconds.
- **Size interactables for eye height.** A default avatar's eye is about 4.5 studs up. Counter-height displays (3.5-4.6 studs) put 61% of targets at or above eye level in one map. Keep tops about 2.5 studs and target centres 1.5-4.5, measured by a script over placement markers. Cross-walls of 8-10 studs hide what's behind while tall landmarks still show.
- **Blockouts get playtested as games.** Every gate on the walking path must be open or breakable before handover; list the ones sealed on purpose.

## Mesh maps, z-fighting and materials (field-measured)

- **Coplanar overlaps z-fight even at tiny offsets** (a top 0.005 studs below its neighbour flickered). Inset one of each overlapping pair by about 0.01 studs. Before baking or importing, scan for coplanar overlapping same-facing triangles (normals within 0.999, plane distance within 0.003) and fail the build on any; one model went from 388 overlaps to 0. Skip break-edge rim strips whose adjacent faces differ by more than about 30 degrees. Common causes: trim bands flush with a plate, stacked bottoms sharing a plane, posts as wide as the panel they meet.
- **Low-poly mesh maps:** set meshes `CanCollide` and `CanQuery` false and put an invisible box or wedge Part under anything that sticks out half a stud or more, so shots and movement hit predictable shapes. Join meshes by group and material, split any group over 20,000 triangles (the documented per-mesh limit), and turn off shadows on overhead meshes so covered maps stay lit.
- **Upload static meshes as `.glb` Models through Open Cloud** so Roblox processes them into MeshParts with collision data; save the result as a committed `.rbxm` and skip re-upload when the source hash is unchanged. Download the processed copy and match each MeshPart to its source node by bounds.
- **Vertex colors through mesh upload:** in one project the upload path linearised OBJ vertex colors (sRGB to linear) while Roblox displayed the stored value as sRGB, so meshes rendered darker (70,160,240 stored as 15,89,222). Read stored colors back with `CreateEditableMeshAsync(Content.fromUri(meshId))` and `GetColor`; to match a picked color, run each channel through linear-to-sRGB before writing the file (`c <= 0.0031308` → `12.92c`, else `1.055c^(1/2.4) - 0.055`).
- **Recolorable patterns without SurfaceAppearance:** a MeshPart's `Color` shows through transparent pixels of its `TextureID`, and scripts can set `TextureID` at runtime. Box-project UVs at a fixed studs-per-tile on every model so one texture tiles the same everywhere, and scale tiling by `Size / MeshSize` when scaling a model.
- **`MaterialVariant.ColorMap` is plugin-only** (PluginSecurity read and write); keep texture ids your runtime code needs in your own data module.
- **Creator Store descriptions are not evidence.** Packs that said "No scripts" contained 6-8 scripts and audio. Read the asset's script flag and instance counts before inserting.
- **Inspect generated or imported art from top, bottom and the facing side** before calling it fixed; triangle counts don't show a wrong shape. For world imports end to end, see `roblox-world-import-pipeline`.

## Build Process

### Objects (single Model)

1. **Assess**: Do you know the components, scale, and style? If not, ask.
2. **Plan**: Declare dimensions as named variables. Choose an anchor part.
3. **Build**: Generate parts with relative positioning. Split across calls if >20 parts.
4. **Verify**: Run validation (check Anchored, below-floor, default colors).

### Maps (multi-zone)

1. **Layout**: Define total size, zone breakdown, gameplay type. If any is vague, ask.
2. **Ground**: Floor planes, boundaries, Origin anchor, folder hierarchy.
3. **Zone shells**: Floor sections, walls, dividers per zone.
4. **Landmarks**: Orientation structures (towers, fountains, trees).
5. **Fill**: Props, furniture, vegetation per zone.
6. **Environment**: Lighting, Atmosphere, SpawnLocations.

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
- GeometryService supports Part, PartOperation, and MeshPart. Terrain is NOT supported.
- Set `CollisionFidelity = Enum.CollisionFidelity.Box` on decorative unions for performance.

## Terrain Import Workflow

Roblox's built-in terrain sculpting is fine for small worlds but tedious for large open-world landscapes (tutorial guide: Large-Scale Roblox Terrain). The proven external pipeline: generate a landscape in a desktop terrain tool, import as an OBJ mesh, then convert to voxel terrain so it streams with the engine.

1. Generate: Quadspinner Gaea (free tier, 1k map resolution) with a Primitive → Displace → Erosion node graph. Add a Mesher node at the end, export as `.tor` then OBJ.
2. Optimize (optional): import OBJ into Blender, apply a Decimate modifier down to ~50-200k faces if the mesh is too heavy to import (note: too few triangles = holes after voxel conversion).
3. Import into Studio: use the OBJ Importer plugin (converts vertex data to wedges/parts) in a blank place; this bypasses Roblox's OBJ polygon limit.
4. Convert to terrain: run a part-to-voxel conversion script over the imported parts. Heightmap import is faster and supports higher resolutions, but the selective material-painting step below only works on the mesh path.

**Material painting:** with the mesh path you can paint materials automatically by slope and altitude (e.g. rock on steep slopes, grass on flats), then the voxel conversion preserves the painted result. For imported heightmaps, paint via a color map that adheres to Roblox's colormap material set instead.

Gaea is resource-hungry (8-16 GB RAM recommended; Studio uses a lot during import). Lower-end hardware can still manage the 1k free-tier resolution.

> Heightmaps cannot represent overhangs or caves; use the mesh path for those.

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

- **Guessing coordinates**: Read from workspace, don't rely on chat memory.
- **Unanchored parts**: They fall. Always set Anchored = true.
- **Hardcoded world positions**: Use relative offsets from anchor CFrame.
- **Block-only for organic shapes**: Use CSG, Cylinders, Spheres, WedgeParts.
- **Silent CSG failures**: Always pcall and verify result is BasePart.
- **Building everything in one call**: Split by phase. 20-30 parts per call max.
- **Floating geometry**: All structures must connect to ground or parent structure.
- **Default colors**: Always set explicit Color and Material. Default gray = unfinished.

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

        -- For MeshPart, read back MeshId/MeshContent. If the asset manifest
        -- expects PBR, inspect child SurfaceAppearance maps in Studio or
        -- plugin tooling; ordinary runtime scripts may not access most maps.
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

## Acceptance Gates

Before calling a prop complete, verify:

- exactly one named model under the intended build root
- pivot and bounding box are sensible at player scale
- every structural part has deliberate anchoring, collision, material, and color
- no loose or duplicate parts remain
- generated or inserted assets have recorded provenance and were read back after placement

Before calling a map phase complete, verify:

- the map root and `Origin` are present
- zone floors and landmarks are inside the intended bounds
- each named spawn has a navigable return path, is not inside collision or facing a wall, and, when the design declares a fixed session population, spawn count matches it
- main paths are reachable and wide enough
- geometry is connected to the ground or a parent structure
- bounds calculations exclude `Baseplate`, `Terrain`, and default `SpawnLocation` unless intentionally included

## Player-Facing Route Acceptance

Treat a map as a player path, not only a geometry tree:

1. Draw the main route as nodes and edges: spawn, first action, decision points, checkpoints, goals, returns, and exits.
2. From every spawn, verify that the next landmark or affordance is visible, the camera is not inside geometry, and the player is not facing a wall or hazard.
3. Give each critical action a readable world cue and feedback. Route prompts and input to their owning skills rather than encoding progress in decoration alone.
4. Check the return path and recovery from falls, death, wrong turns, and interrupted traversal.
5. Playtest from the player camera at representative movement speeds. A top-down editor view cannot prove wayfinding or spatial onboarding.

Use runtime observation or a small funnel to judge onboarding success. Static route structure can reveal what to test, not whether players understand it.

For world interactions, prefer `ProximityPrompt` when cross-device button or hold semantics fit. Use `ClickDetector` for simple click interactions and `Touched` only when physical contact is the mechanic. `BillboardGui`, `SurfaceGui`, and `Highlight` provide cues, not authority. Validate outcomes on the server from current distance, state, cooldown, and ownership.

## Large-Place Readback

For a large root, do not use an unbounded "dump everything" readback as the only check. Partition the inspection by build root or zone and collect:

- instance and descendant counts, plus bounds and pivot for each scope;
- class counts for structural and effect-heavy classes such as `MeshPart`, `UnionOperation`, `SurfaceAppearance`, `Attachment`, and `ParticleEmitter`;
- anchoring, collision, and query-state exceptions;
- repeated mesh, texture, and image references that may deserve deduplication review;
- the smallest representative set of paths needed to investigate each exception.

Use the report to choose the next bounded inspection or playtest. Static counts are triage signals, not proof of quality, usability, memory use, or frame rate. Confirm performance concerns with Scene Analysis, the Developer Console, MicroProfiler, and representative devices.

## Evidence Recipes

- **Structural:** return counts, classes, paths, bounds, pivots, materials, anchoring errors, collision errors, and asset IDs from an edit-time inspection.
- **Visual:** use `screen_capture` with a deliberate camera position when supported. If capture fails or hangs, report that and retain structural evidence rather than inventing visual conclusions.
- **Runtime:** start play, navigate to the spawn and a representative landmark, exercise the relevant interaction, collect console output, and stop play. A clean console is evidence of no observed errors, not proof of all behavior.
- **Recovery:** if a phase fails, preserve the last verified phase, remove only the disposable failed output, and retry with a smaller batch or native fallback.

## Community ecosystem (leads, not sources)

### Interaction prompts: ProximityPrompt and ProximityPromptService

`ProximityPrompt` (parent to a `BasePart`, `Attachment`, or `Model`) renders a built-in interaction prompt (key hint + label) and fires `Triggered` when the player interacts; no GUI code needed. Default `RequiresLineOfSight = true` and `MaxActivationDistance = 10`. `HoldDuration` makes the player hold the key; `GamepadKeyCode`/`Style` control presentation. `ObjectText`/`ActionText` are the sub-label and main label. `KeyboardKeyCode`/`ClickablePrompt` customize input.

`ProximityPromptService` is the manager: `Enabled` toggles all prompts, `MaxPromptsVisible` (default 16) caps simultaneous prompts, `MaxIndicatorsVisible` (default 16, clamped 0-64) caps opt-in distance indicators. Events: `PromptShown`/`PromptHidden` (client-side visibility), `PromptTriggered(prompt, player)` fires on completed interaction (key press, or after `HoldDuration` hold), `PromptTriggerEnded`, `PromptButtonHoldBegan`/`PromptButtonHoldEnded` (hold-progress UI), plus `IndicatorShown`/`IndicatorHidden` for custom indicator UI (indicators only appear when a prompt sets `MaxIndicatorDistance > 0`). Listen globally on the service to avoid per-prompt wiring:

```luau
local PPS = game:GetService("ProximityPromptService")
PPS.PromptTriggered:Connect(function(prompt, player)
    handleInteraction(prompt, player) -- one connection for every prompt in the game
end)
```

Server scripts can also create and configure prompts programmatically; `TriggerEnded` on the prompt itself pairs with `Triggered` for release-to-cancel mechanics.

- [Large-Scale Roblox Terrain: the ultimate guide](https://devforum.roblox.com/t/large-scale-roblox-terrain-the-ultimate-guide/405672) (84k views): still the terrain-at-scale reference.
- [Realistic oceans via mesh deformation](https://devforum.roblox.com/t/realistic-oceans-using-mesh-deformation/1159345); [greedy meshing explainer](https://devforum.roblox.com/t/consume-everything-how-greedy-meshing-works/452717).
- [Free texture sites](https://devforum.roblox.com/t/free-texture-sites/70131) (174k views); [City Loader plugin](https://devforum.roblox.com/t/city-loader-plugin-templates-for-real-life-buildingscities-in-studio/696886).

## Generated-map and interaction regression checks

- After a representative room or map is approved, record its reusable dimensions, materials, prop sourcing, lighting, traversal and validation choices before building siblings. Keep the approved reference intact unless its changes are requested.
- After resizing or changing layout dimensions, revalidate dependent walls, floors, foundations, openings, fences, prop offsets, spawns, and activity zones. Inspect joins and exterior boundaries from player height as well as overview cameras; fix the generator when generated geometry is wrong.
- Scan for unintended coincident faces and overlapping trim across the complete generated scene, then inspect corners, door lintels, floor/ceiling seams and junctions in motion. An automated overlap report is a candidate list, not proof that the scene is free of flicker or gaps.
- Traverse doorways, ladders, hatches, landings, and return routes with representative supported avatars in the installed geometry. Check entry, body clearance, and stepping off both ends. Treat nominal dimensions as planning estimates, not traversal proof.
- Compare maps with the same definition of accessible floor, obstacle clearance, ceiling height, connectivity, and camera conditions. Inspect the extraction method before comparing results. Outer bounding boxes and similar area do not establish similar playable space or spaciousness.
- Match an activity's eligibility zone to the visible area players understand as part of it, including where its interaction can actually activate. Exercise all edges; define separate entry/exit thresholds where jitter would repeatedly revoke equipment or reset progress. Record exit causes separately.
- Before reusing a cloned prop, inspect its tags, attributes, prompts, scripts, references, and descendants. Confirm only the intended discovery systems attach behavior; appearance alone does not establish a clean clone.
- Derive rebuild bounds from canonical geometry, excluding earlier generated barriers, helpers, and validation zones. Run the generator twice on a temporary copy and compare instance counts, dimensions and behavior; repeated regeneration must not expand its own input bounds.
