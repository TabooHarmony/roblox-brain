---
name: roblox-camera
description: Camera object, CameraType enum, CFrame math, custom controllers, first/third person, cutscenes, screen shake.
last_reviewed: 2026-06-29
sources:
  - https://create.roblox.com/docs/reference/engine/classes/Camera
  - https://create.roblox.com/docs/reference/engine/enums/CameraType
  - https://create.roblox.com/docs/reference/engine/datatypes/CFrame
---

## When to Load

Load when scripting custom camera behavior (cutscenes, third-person follow, custom rotation), manipulating `CFrame` for placement/rotation, raycasting from the screen, or building a non-default player view. Client-only.

## Quick Reference

**The Camera**: `workspace.CurrentCamera` — one per client. Set `CameraType = Scriptable` to disable defaults and take full control. Without it, defaults overwrite your CFrame every frame.

**CameraType**: `Fixed`, `Attach`/`Watch`/`Track`/`Follow` (subject-following), `Custom` (default), `Scriptable` (no default), `Orbital` (fixed Y, rotates around player). `CameraSubject` cannot be `nil` — setting it reverts.

**Key properties**: `CFrame`, `CameraSubject`, `FieldOfView` (deg), `FieldOfViewMode` (`Vertical`/`Diagonal`), `NearPlaneZ`, `ViewportSize`, `HeadLocked`, `HeadScale`, `Focus`.

**CFrame essentials**:

```luau
CFrame.new(pos)
CFrame.lookAt(at, lookAt, up?)                 -- preferred over deprecated CFrame.new(pos, lookAt)
CFrame.Angles(rx, ry, rz)                      -- XYZ Euler (radians)
cf * Vector3.new(0, 0, 10)                     -- local offset → world
cf:Lerp(goal, alpha)                           -- 0..1 linear interp
cf.LookVector / RightVector / UpVector         -- world-space unit axes
```

**Custom camera loop** — always `RenderStepped`, never `Heartbeat`:

```luau
camera.CameraType = Enum.CameraType.Scriptable
RunService.RenderStepped:Connect(function(dt)
    local desired = CFrame.lookAt(head.Position - offset, head.Position)
    camera.CFrame = camera.CFrame:Lerp(desired, math.min(dt * 10, 1))
end)
```

**Raycasting from camera**: `camera:ScreenPointToRay(mx, my)` (accounts for GUI inset) vs `camera:ViewportPointToRay(mx, my)` (raw, NO inset). `ScreenPointToRay` returns a unit Ray (1 stud) — multiply `Direction` by length for actual raycast.

**Pitfalls**:
- Client-only. Server sets silently dropped.
- Without `Scriptable`, defaults overwrite your CFrame every frame.
- `RenderStepped` for camera (visual sync). `Heartbeat` adds 1-frame lag.
- `Camera.CFrame` lacks VR head rotation — use `GetRenderCFrame()` for true view.
- `SetRoll` is outdated — apply roll via `CFrame.Angles(0, 0, roll)` on CFrame.
- `CameraSubject = nil` reverts to previous.
- `CFrame.new(pos, lookAt)` is legacy (back-compat only) — use `CFrame.lookAt(at, lookAt)` for new code.
- `ScreenPointToRay` ≠ `ViewportPointToRay` (GUI inset). Use `ScreenPointToRay` for mouse input.

See `references/full.md` for first/third-person recipes, cutscenes, screen shake, mouse-look, full API.