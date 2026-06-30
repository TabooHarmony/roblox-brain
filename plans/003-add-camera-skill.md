# Plan 003: Add roblox-camera skill (camera types, CFrame, custom controllers)

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat e494289..HEAD -- skills/ skill_index.md README.md`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding.

## Status

- **Priority**: P2
- **Effort**: M
- **Risk**: LOW
- **Depends on**: none
- **Category**: direction
- **Planned at**: commit `e494289`, 2026-06-29

## Why this matters

Camera systems are fundamental to any 3D Roblox game, and the repo has no skill for it. The `roblox-architecture` skill mentions "CameraController.client.lua" in a folder layout example but provides zero guidance on camera types, CFrame manipulation, or custom camera controllers. An agent asked "how do I make a third-person camera?" or "how do I do a camera cutscene?" has nothing to load.

## Current state

The repo follows a progressive disclosure pattern (same as Plan 002).

**Frontmatter pattern** (from `skills/roblox-lighting/SKILL.md`):
```yaml
---
name: roblox-camera
description: >
  Camera types, CFrame manipulation, custom camera controllers, first/third
  person, camera subject, cutscenes, screen shakes.
last_reviewed: 2026-06-29
sources:
  - https://github.com/Roblox/creator-docs (camera categories)
---
```

**Body pattern** (from `skills/roblox-lighting/SKILL.md`):
- `## When to Load`
- `## Quick Reference`
- Bottom hand-off line

**Existing references to camera**: `skills/roblox-architecture/references/full.md` line 192 mentions "The Camera (each client has a local `Workspace.CurrentCamera`)" and line 140 mentions "Camera controllers" but neither points to a skill.

## Commands you will need

| Purpose | Command | Expected on success |
|-----------|--------|---------------------|
| Validate  | `python3 validate_skills.py` | "Validated 30 skills" (if 002 done first) or 29 |
| Check size| `wc -c skills/roblox-camera/SKILL.md` | under 3000 |

## Scope

**In scope** (the only files you should create/modify):
- `skills/roblox-camera/SKILL.md` (create)
- `skills/roblox-camera/references/full.md` (create)
- `skill_index.md` (add row)
- `README.md` (add row, update count)

**Out of scope** (do NOT touch):
- Any other skill files
- `roblox-architecture` (optionally add a cross-reference pointer, but keep it minimal)

## Git workflow

- Branch: `advisor/003-add-camera-skill`
- Commit per logical unit.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Create SKILL.md

Create `skills/roblox-camera/SKILL.md` with:
- Frontmatter with name, description (under 150 chars), last_reviewed, sources
- `## When to Load` — when to use camera systems
- `## Quick Reference` covering:
  - **Camera object**: `workspace.CurrentCamera` — each client has their own. `Camera.CameraType` enum (Custom, Fixed, Attach, Watch, Follow, Track, Scriptable).
  - **Key properties**: `CameraSubject` (what the camera follows), `CFrame` (position + rotation), `FieldOfView`, `ViewportSize`, `NearPlaneZ`, `FarPlaneZ`.
  - **Custom camera**: Set `CameraType = Enum.CameraType.Scriptable` then set `CFrame` every frame via `RunService.RenderStepped`. Full control.
  - **First person**: `player.CameraMode = Enum.CameraMode.LockFirstPerson`. Or force by setting camera CFrame to head position.
  - **Third person**: Default. `player.CameraMinZoomDistance` / `CameraMaxZoomDistance` control zoom range. Mouse wheel adjusts.
  - **CFrame math**: `CFrame.new(pos)` for position, `CFrame.lookAt(eye, target)` to point at something, `CFrame * CFrame.Angles(x,y,z)` for rotation, `CFrame:Lerp(target, alpha)` for smooth transitions.
  - **Cutscenes**: TweenService on camera CFrame, or manual lerp loop. Set CameraType to Scriptable during cutscene, restore after.
  - **Screen shake**: Offset camera CFrame by random small amounts per frame, decay over time.
  - **Raycasting from camera**: `Camera:ScreenPointToRay(x, y, depth)` for mouse-to-world, `Camera:WorldToViewportPoint(position)` for world-to-screen.
  - **Pitfalls**: Camera must be set on client (LocalScript), not server. RenderStepped for camera CFrame (not Heartbeat — visual lag). Restore CameraType after cutscenes or player is stuck. `CameraSubject` must be set for Follow/Attach types. Don't set CFrame on server — it won't replicate smoothly.
- Bottom hand-off line

**Verify**: `wc -c skills/roblox-camera/SKILL.md` → under 3000

### Step 2: Create references/full.md

Create `skills/roblox-camera/references/full.md` with:
- `# Roblox Camera — Full Reference`
- `## Camera Object` — how to get the camera, per-client nature, CameraType enum table with all values and when to use each
- `## Camera Properties` — full table: CameraSubject, CFrame, FieldOfView, ViewportSize, NearPlaneZ, FarPlaneZ, HeadLocked, DiagonalFieldOfView
- `## Custom Camera Controller` — full code example: Scriptable camera with RenderStepped loop, mouse orbit, zoom
- `## First Person** — CameraMode.LockFirstPerson, FOV tricks, head opacity
- `## Third Person** — zoom distance limits, shoulder cam, offset CFrame
- `## CFrame Math` — CFrame.new, CFrame.lookAt, CFrame.Angles, CFrame * CFrame multiplication, Lerp, CFrame:Inverse(), ToObjectSpace/ToWorldSpace for relative positioning
- `## Cutscenes** — TweenService camera CFrame example, Scriptable toggle, player input lock during cutscene, restore after
- `## Screen Shake** — implementation pattern with intensity + decay, example function
- `## Raycasting from Camera** — ScreenPointToRay, WorldToViewportPoint, mouse-to-world raycast pattern
- `## Camera in MCP Context** — how to manipulate camera via Studio MCP execute_luau (set CurrentCamera properties, run in Play mode)
- `## Pitfalls** — client-only, RenderStepped vs Heartbeat, restore CameraType, CameraSubject requirements, server replication

**Verify**: `test -f skills/roblox-camera/references/full.md && echo exists` → "exists"

### Step 3: Add to skill_index.md

Add a new row in the "Building & UI" section (after roblox-input or roblox-lighting):
```markdown
| `roblox-camera` | Camera types, CFrame math, custom controllers, first/third person, cutscenes, screen shake |
```

### Step 4: Update README.md

Update skill count (29→30 if 002 done first, or 28→30 if both done together). Add row in "Building & UI" table.

### Step 5: Final verification

**Verify**:
```
python3 validate_skills.py                 → passes
wc -c skills/roblox-camera/SKILL.md         → under 3000
test -f skills/roblox-camera/references/full.md && echo exists  → "exists"
grep "roblox-camera" skill_index.md         → 1 match
```

## Done criteria

ALL must hold:

- [ ] `skills/roblox-camera/SKILL.md` exists, under 3000 chars, has frontmatter + Quick Reference
- [ ] `skills/roblox-camera/references/full.md` exists
- [ ] `python3 validate_skills.py` exits 0
- [ ] `skill_index.md` has a roblox-camera row
- [ ] `README.md` has the new skill in the table and count is updated
- [ ] No files outside the in-scope list are modified
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:
- Any API name doesn't match the official Roblox creator docs (verify CameraType enum, Camera properties against https://create.roblox.com/docs).
- The SKILL.md exceeds 3000 chars (trim, move to full.md).
- The CFrame math examples are incorrect (verify with Luau syntax — CFrame.lookAt, not CFrame.lookAt with wrong arg order).

## Maintenance notes

- Cross-reference from `roblox-architecture` camera section to this skill.
- `roblox-animation-vfx` may reference this for cutscene camera work.
- Update `last_reviewed` when verifying against current docs.
