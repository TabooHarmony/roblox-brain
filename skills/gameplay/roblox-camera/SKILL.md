---
name: roblox-camera
description: "Use when scripting or fixing Roblox camera behavior: CFrame placement, screen raycasts, first/third-person, shoulder views, cutscenes."
when_to_use: "Also when the camera clips through walls, jitters, aims wrong on touch or gamepad, or needs a death cam or spectate view."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/reference/engine/classes/Camera
  - https://create.roblox.com/docs/reference/engine/enums/CameraType
  - https://create.roblox.com/docs/reference/engine/datatypes/CFrame
  - https://create.roblox.com/docs/reference/engine/classes/ViewportCamera
  - https://create.roblox.com/docs/reference/engine/classes/Player
  - https://create.roblox.com/docs/workspace/camera/free-camera
  - original
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine/classes/WorldRoot.yaml
---

# Roblox Camera

## When to Load

Custom camera behavior (cutscenes, follow, shoulder or orthographic views), `CFrame` placement, screen raycasts, shake and recoil, or a non-default player view. Client-only.

## Quick Reference

- `workspace.CurrentCamera`, one per client. `CameraType = Scriptable` takes full control; otherwise defaults overwrite your CFrame every frame. `CameraSubject` can't be `nil`.
- Types: `Custom` (default), `Scriptable`, `Fixed`, `Follow`/`Track`/`Watch`/`Attach`, `Orbital`.
- Properties: `CFrame`, `FieldOfView`, `FieldOfViewMode`, `NearPlaneZ`, `ViewportSize` (safe area), `Focus`; `ProjectionType = Orthographic` + `OrthographicSize`/`OrthographicMode`.
- CFrame: `CFrame.lookAt(pos, target)`, `CFrame.Angles(rx, ry, rz)`, `cf * offset`, `cf:Lerp(goal, a)`. `CFrame.new(pos, lookAt)` is legacy; `SetRoll` is outdated.
- Custom loop on `PreRender` (not `Heartbeat`):

```luau
camera.CameraType = Enum.CameraType.Scriptable
RunService.PreRender:Connect(function(dt)
    local desired = CFrame.lookAt(head.Position - offset, head.Position)
    camera.CFrame = camera.CFrame:Lerp(desired, math.min(dt * 10, 1))
end)
```

- Rays: `ScreenPointToRay` (with GUI inset) vs `ViewportPointToRay` (without); unit length, so scale `Direction`.
- Render order: assist at `Enum.RenderPriority.Camera.Value - 1`, overlays at `+ 1`.
- Rotational kicks drift the default camera's aim: remove at `Camera - 2`, re-apply at `Camera + 3`. Additive offsets pile up on `Scriptable`.
- Fast subjects: velocity-led follow on an anchored proxy part.
- `ViewportCamera` for `ViewportFrame`s (replicates); `Player:GetCameraState()` under Server Authority.
- VR: `GetRenderCFrame()` for the true view.

> Details: [references/full.md](references/full.md)
