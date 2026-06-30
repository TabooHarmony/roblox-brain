# Roblox Camera — Full Reference

Camera work is **client-only**. `workspace.CurrentCamera`, `CFrame` setters, and `RenderStepped` callbacks must run in a `LocalScript` or `Script` with `RunContext = Client`. Server scripts silently drop camera writes.

## The Camera Object

Each client has exactly one camera, accessible at `workspace.CurrentCamera`. Other `Camera` instances exist for `ViewportFrame`s (mini-map, security camera, etc.) but `CurrentCamera` is the player's main view.

### CameraType Enum

| Value | Behavior | Requires CameraSubject? |
|-------|----------|------------------------|
| `Fixed` (0) | Stationary. | No |
| `Attach` (1) | Moves with subject at a fixed offset; rotates as subject rotates. | Yes |
| `Watch` (2) | Stationary, rotates to keep subject centered. | Yes |
| `Track` (3) | Moves with subject's position, doesn't auto-rotate. | Yes |
| `Follow` (4) | Moves with subject + rotates to keep centered. | Yes |
| `Custom` (5) | Default mode used by Roblox core scripts. | No |
| `Scriptable` (6) | No default behavior. You set `CFrame` manually. | No |
| `Orbital` (7) | Fixed Y position, rotates around player. | Yes |

`Attach`, `Watch`, `Track`, `Follow`, and `Orbital` all require a valid `CameraSubject`. Without one, behavior is undefined.

### CameraSubject

Set to the local `Humanoid` by default for character following (with `Humanoid.CameraOffset` applied). Can also be set to a `BasePart` (e.g. a `VehicleSeat`).

```luau
-- Restore default
camera.CameraSubject = player.Character:FindFirstChildWhichIsA("Humanoid")
```

`CameraSubject = nil` reverts to the previous value (you cannot set it to nil).

## Camera Properties (full)

| Property | Type | Notes |
|----------|------|-------|
| `CFrame` | CFrame | Position + orientation. Defaults overwrite this unless `Scriptable`. |
| `CameraSubject` | Instance | Humanoid, BasePart, etc. |
| `CameraType` | CameraType | See enum above. |
| `FieldOfView` | float (degrees) | 1–120. Vertical FOV when `FieldOfViewMode = Vertical`. |
| `FieldOfViewMode` | Enum.FieldOfViewMode | `Vertical` or `Diagonal`. |
| `DiagonalFieldOfView` | float (degrees) | Read when `FieldOfViewMode = Diagonal`. |
| `MaxAxisFieldOfView` | float (degrees) | Read when `FieldOfViewMode = Diagonal`. |
| `NearPlaneZ` | float (studs) | Near clipping plane. |
| `ViewportSize` | Vector2 | Pixel size of the viewport. |
| `HeadLocked` | bool | VR: locks view to head. |
| `HeadScale` | float | VR: scales head CFrame. |
| `Focus` | CFrame | CFrame the camera points at (managed by CameraType logic, not by you). |
| `VRTiltAndRollEnabled` | bool | VR-only. |
| `CoordinateFrame` | CFrame | Hidden alias for `CFrame`. Use `CFrame`. |

## Camera Methods (full)

| Method | Returns | Use |
|--------|---------|-----|
| `GetRenderCFrame()` | CFrame | The "true" rendered CFrame, including VR head rotation not reflected in `.CFrame`. |
| `GetRoll()` | float (radians) | Roll set via `SetRoll` (not roll manually applied via CFrame). |
| `SetRoll(rollAngle)` | () | **Outdated** — apply roll via `CFrame.Angles(0, 0, roll)` on CFrame instead. |
| `ScreenPointToRay(x, y, depth?)` | Ray | Unit ray from screen pixel coords. Accounts for GUI inset. |
| `ViewportPointToRay(x, y, depth?)` | Ray | Unit ray from device-safe viewport coords. Does NOT account for GUI inset. |
| `WorldToScreenPoint(worldPos)` | Vector3 | `(x, y, onScreen)`. Pixels accounting for GUI inset. |
| `WorldToViewportPoint(worldPos)` | Vector3 | `(x, y, onScreen)` in device-safe viewport coords. |
| `GetPartsObscuringTarget(castPoints, ignoreList)` | {BasePart} | Parts obscuring the camera's view of given world points. |
| `ZoomToExtents()`, `Interpolate(...)` | () | Editor camera methods — not for gameplay cameras. |
| `PanUnits`, `TiltUnits`, `GetPanSpeed`, `GetTiltSpeed` | various | Editor viewport camera controls. |

### Event

`InterpolationFinished` — fires when `Interpolate` completes.

## ScreenPointToRay vs ViewportPointToRay

The two are NOT interchangeable:

| Method | Coordinates | GUI inset? | Use when |
|--------|-------------|-----------|----------|
| `ScreenPointToRay(x, y)` | Pixel coords, origin = top-left **below** top bar | Yes | Mouse picking, player-facing UI clicks |
| `ViewportPointToRay(x, y)` | Device-safe pixel coords, origin = top-left of Roblox top bar | No | Raw device input, drawing in viewport space |

Both return a **unit Ray** (1 stud long). To get an actual raycast, multiply `Direction`:

```luau
local unitRay = camera:ScreenPointToRay(mouseX, mouseY)
local result = workspace:Raycast(unitRay.Origin, unitRay.Direction * 500)
```

`ScreenPointToRay` only works for `workspace.CurrentCamera`. ViewportFrame cameras have an initial `(1,1)` viewport size that doesn't update until you set them as CurrentCamera.

## CFrame Math

### Constructors

| Constructor | Notes |
|-------------|-------|
| `CFrame.new()` | Identity at origin. |
| `CFrame.new(pos: Vector3)` | Position only, identity rotation. |
| `CFrame.new(x, y, z)` | Position only. |
| `CFrame.new(x, y, z, qX, qY, qZ, qW)` | Position + quaternion rotation. |
| `CFrame.new(x, y, z, R00, R01, ..., R22)` | Position + raw 3x3 rotation matrix. |
| `CFrame.new(pos, lookAt)` | **Deprecated** — use `CFrame.lookAt`. |
| `CFrame.lookAt(at, lookAt, up?)` | Construct at `at` oriented toward `lookAt`. Optional `up` defaults to `(0,1,0)`. Fails if `lookAt` directly above `at` (use `lookAlong`). |
| `CFrame.lookAlong(at, direction, up?)` | Construct at `at` oriented along `direction`. |
| `CFrame.fromRotationBetweenVectors(from, to)` | Rotation that maps `from` to `to`. |
| `CFrame.fromEulerAngles(rx, ry, rz, order?)` | Euler angles (radians), default XYZ. |
| `CFrame.fromEulerAnglesXYZ(rx, ry, rz)` | XYZ order (== `CFrame.Angles`). |
| `CFrame.fromEulerAnglesYXZ(rx, ry, rz)` | YXZ order. |
| `CFrame.Angles(rx, ry, rz)` | XYZ Euler, shorthand. |
| `CFrame.fromOrientation(rx, ry, rz)` | YXZ Euler, shorthand. |
| `CFrame.fromAxisAngle(axis: Vector3, angle: number)` | Rotation around an arbitrary axis. |
| `CFrame.fromMatrix(pos, xVector, yVector, zVector)` | From explicit basis vectors. |

### Properties

| Property | Type | Notes |
|----------|------|-------|
| `Position` | Vector3 | Position component. |
| `Rotation` | Vector3 | Euler angles (radians). |
| `X`, `Y`, `Z` | number | Components of `Position`. |
| `LookVector` | Vector3 | -Z axis in world space. Forward. |
| `RightVector` | Vector3 | X axis in world space. |
| `UpVector` | Vector3 | Y axis in world space. |
| `XVector`, `YVector`, `ZVector` | Vector3 | Same as Right/Up/-LookVector. |

### Methods

| Method | Returns | Use |
|--------|---------|-----|
| `cf:Inverse()` | CFrame | Inverse. |
| `cf:Lerp(goal, alpha)` | CFrame | Linear interp 0..1. |
| `cf:Orthonormalize()` | CFrame | Renormalize (fix drift from many small ops). |
| `cf:ToWorldSpace(...cfs)` | CFrame(s) | `= cf * other`. |
| `cf:ToObjectSpace(worldCf)` | CFrame | `= cf:Inverse() * worldCf`. |
| `cf:PointToWorldSpace(p)` | Vector3 | Treats `p` as position. |
| `cf:PointToObjectSpace(p)` | Vector3 | Inverse for positions. |
| `cf:VectorToWorldSpace(v)` | Vector3 | Treats `v` as direction (no translation). |
| `cf:VectorToObjectSpace(v)` | Vector3 | Inverse for directions. |
| `cf:GetComponents()` | (number×12) | Flatten to 12 numbers. |
| `cf:ToEulerAngles()` | (rx, ry, rz) | XYZ Euler. |
| `cf:ToEulerAnglesXYZ()` | (rx, ry, rz) | XYZ Euler. |
| `cf:ToEulerAnglesYXZ()` | (rx, ry, rz) | YXZ Euler. |
| `cf:ToOrientation()` | (rx, ry, rz) | YXZ Euler. |
| `cf:ToAxisAngle()` | (axis, angle) | Decompose into axis-angle. |
| `cf:FuzzyEq(other, epsilon?)` | bool | Approximate equality. |
| `cf:AngleBetween(other)` | float | Angle between two CFrame orientations. |

`BasePart.CFrame` is auto-orthonormalized, but `CFrame` math operations can drift; call `:Orthonormalize()` before passing to APIs that don't auto-normalize.

### Math Operations

| Op | Type | Returns |
|----|------|---------|
| `cf + cf` | CFrame | Sum of components (rarely the right choice). |
| `cf - cf` | CFrame | Difference. |
| `cf * cf` | CFrame | Composition: rotate/translate by right operand in left's space. |
| `cf * Vector3` | Vector3 | Point: position transformed. |
| `cf / cf` | CFrame | Right-multiplied by inverse. |

## Custom Camera Controllers

### Smooth follow (third person)

```luau
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")

local player = Players.LocalPlayer
local camera = workspace.CurrentCamera

local OFFSET = Vector3.new(0, 4, 12)
local SMOOTH = 8

camera.CameraType = Enum.CameraType.Scriptable

RunService.RenderStepped:Connect(function(dt)
    local character = player.Character
    if not character then return end
    local root = character:FindFirstChild("HumanoidRootPart")
    if not root then return end

    local target = root.CFrame * CFrame.new(0, 2, 0)
    local desired = CFrame.lookAt(target.Position + OFFSET, target.Position)

    local alpha = math.min(dt * SMOOTH, 1)
    camera.CFrame = camera.CFrame:Lerp(desired, alpha)
end)
```

### First-person

```luau
camera.CameraType = Enum.CameraType.Scriptable

RunService.RenderStepped:Connect(function()
    local head = character:FindFirstChild("Head")
    if not head then return end
    camera.CFrame = head.CFrame + Vector3.new(0, 0.5, 0)
end)
```

For real first-person you also want to hide the local head: set the head's `LocalTransparencyModifier = 1` (client-only) on the local character, or render with a `FirstPersonAccessory` rig.

### Third-person with adjustable zoom (mouse wheel)

```luau
local zoomDist = 12
local MIN_ZOOM, MAX_ZOOM = 2, 30

UIS.InputChanged:Connect(function(input, gpe)
    if gpe then return end
    if input.UserInputType == Enum.UserInputType.MouseWheel then
        zoomDist = math.clamp(zoomDist - input.Position.Z * 2, MIN_ZOOM, MAX_ZOOM)
    end
end)
```

### Orbital camera (fixed Y, mouse-look)

```luau
local yaw, pitch = 0, 0
local DIST = 12
local PITCH_LIMIT = math.rad(80)

UIS.InputChanged:Connect(function(input, gpe)
    if gpe then return end
    if input.UserInputType == Enum.UserInputType.MouseMovement then
        yaw   = yaw   - input.Delta.X * 0.003
        pitch = math.clamp(pitch - input.Delta.Y * 0.003, -PITCH_LIMIT, PITCH_LIMIT)
    end
end)

RunService.RenderStepped:Connect(function(_dt)
    local root = character.HumanoidRootPart
    local orbit = CFrame.Angles(0, yaw, 0) * CFrame.Angles(pitch, 0, 0)
    local offset = orbit.LookVector * DIST
    camera.CFrame = CFrame.lookAt(root.Position + offset, root.Position)
end)
```

### Mouse-look (FPS)

```luau
local ROT_SPEED = 0.003
local PITCH_LIMIT = math.rad(89)
local yaw, pitch = 0, 0

UIS.InputBegan:Connect(function(input, _gpe)
    if input.UserInputType == Enum.UserInputType.MouseButton2 then
        UIS.MouseBehavior = Enum.MouseBehavior.LockCenter
    end
end)
UIS.InputEnded:Connect(function(input)
    if input.UserInputType == Enum.UserInputType.MouseButton2 then
        UIS.MouseBehavior = Enum.MouseBehavior.Default
    end
end)

UIS.InputChanged:Connect(function(input, gpe)
    if gpe then return end
    if input.UserInputType == Enum.UserInputType.MouseMovement then
        yaw   = yaw   - input.Delta.X * ROT_SPEED
        pitch = math.clamp(pitch - input.Delta.Y * ROT_SPEED, -PITCH_LIMIT, PITCH_LIMIT)
    end
end)

RunService.RenderStepped:Connect(function()
    if not character:FindFirstChild("Head") then return end
    local head = character.Head
    camera.CFrame = CFrame.new(head.Position) * CFrame.Angles(0, yaw, 0) * CFrame.Angles(pitch, 0, 0)
end)
```

## Cutscenes

### Basic tween

```luau
local TweenService = game:GetService("TweenService")
local camera = workspace.CurrentCamera

camera.CameraType = Enum.CameraType.Scriptable

local tweenInfo = TweenInfo.new(2, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut)
local targetCFrame = CFrame.lookAt(Vector3.new(0, 20, 30), Vector3.new(0, 5, 0))

local tween = TweenService:Create(camera, tweenInfo, {CFrame = targetCFrame})
tween:Play()
tween.Completed:Wait()

camera.CameraType = Enum.CameraType.Custom
```

### Multi-shot cutscene with input lock

```luau
local function playCutscene(cameraPath: {CFrame}, duration: number)
    camera.CameraType = Enum.CameraType.Scriptable
    local humanoid = character:FindFirstChildWhichIsA("Humanoid")
    humanoid.WalkSpeed = 0
    humanoid.JumpPower = 0

    for _, target in ipairs(cameraPath) do
        local info = TweenInfo.new(duration / #cameraPath, Enum.EasingStyle.Sine)
        local tween = TweenService:Create(camera, info, {CFrame = target})
        tween:Play()
        tween.Completed:Wait()
    end

    humanoid.WalkSpeed = 16
    humanoid.JumpPower = 50
    camera.CameraType = Enum.CameraType.Custom
end
```

### Screen shake

```luau
local shakeActive = false
local shakeIntensity = 0
local baseCFrame: CFrame

local function startShake(intensity: number, duration: number)
    shakeActive = true
    shakeIntensity = intensity
    baseCFrame = camera.CFrame

    task.spawn(function()
        local t = 0
        while t < duration do
            t += task.wait()
            shakeIntensity = intensity * (1 - t / duration)
        end
        shakeActive = false
        camera.CFrame = baseCFrame
    end)
end

RunService.RenderStepped:Connect(function()
    if not shakeActive then return end
    local offset = CFrame.new(
        (math.random() - 0.5) * shakeIntensity,
        (math.random() - 0.5) * shakeIntensity,
        (math.random() - 0.5) * shakeIntensity
    )
    camera.CFrame = baseCFrame * offset
end)
```

## World ↔ Screen Conversion

```luau
-- World to screen (with GUI inset)
local screenPos, onScreen = camera:WorldToScreenPoint(worldPos)
-- screenPos.X, screenPos.Y are pixel coordinates (accounting for GUI inset)
-- onScreen = true if point is within the visible viewport
-- screenPos.Z > 0 means in front of camera

-- World to viewport (raw device coords)
local viewportPos, onScreen = camera:WorldToViewportPoint(worldPos)
```

## Mouse-to-World Raycast Pattern

```luau
local function mouseHit(mouseX, mouseY, maxDist)
    local unitRay = camera:ScreenPointToRay(mouseX, mouseY)
    return workspace:Raycast(unitRay.Origin, unitRay.Direction * maxDist)
end

local result = mouseHit(mouse.X, mouse.Y, 1000)
if result then
    local hitPart = result.Instance
    local hitPos = result.Position
    local hitNormal = result.Normal
    -- ...
end
```

## Camera in Studio MCP

When scripting a camera via `execute_luau` in Studio (Play mode), set the camera on the active client. Useful for testing cutscenes:

```luau
-- In execute_luau, the local script context is the editing client
local camera = workspace.CurrentCamera
camera.CameraType = Enum.CameraType.Scriptable
camera.CFrame = CFrame.lookAt(Vector3.new(0, 50, 50), Vector3.zero)
```

For non-Play testing (Edit mode), `CurrentCamera` exists but the perspective doesn't render the way gameplay does — Scriptable camera changes won't be visible until Play.

## Common Mistakes

- **Camera work on the server.** Silently dropped. Must be in `LocalScript` or client `RunContext`.
- **Forgetting `CameraType = Scriptable`.** Defaults overwrite your CFrame every frame.
- **Using `Heartbeat` instead of `RenderStepped` for camera.** Adds 1 frame of lag.
- **Setting `CameraSubject = nil` "expecting it to detach".** It reverts to previous value.
- **Reading `Camera.CFrame` in VR for gameplay math.** Use `GetRenderCFrame()` for true view (includes head rotation).
- **Using `SetRoll` because it's convenient.** It's outdated; apply roll via `CFrame.Angles(0, 0, roll)` on CFrame.
- **`CFrame.new(pos, lookAt)` because old tutorials say so.** Deprecated. Use `CFrame.lookAt(at, lookAt)`.
- **Confusing `ScreenPointToRay` with `ViewportPointToRay`.** GUI inset handling differs. Use `ScreenPointToRay` for mouse input.
- **Forgetting to restore `CameraType` after a cutscene.** Player is stuck.
- **Trying to `Raycast` with the unit Ray directly.** It's only 1 stud long. Multiply `Direction` by the actual distance.
- **Modifying the local head in first-person without `LocalTransparencyModifier`.** Players see their own head blocking the view. Use `LocalTransparencyModifier = 1`, not `Transparency` (Transparency replicates).
- **Setting `Humanoid.JumpPower = 0` to disable jump in a cutscene.** Remember to restore it. Or use `Humanoid:SetStateEnabled(Enum.HumanoidStateType.Jumping, false)`.
- **Trying to set Camera.CFrame every frame without clearing the render connection on player respawn.** Stale references after respawn. Reconnect in `CharacterAdded`.
