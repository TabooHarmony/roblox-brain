# Roblox Input: Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

Both `UserInputService` (UIS) and `ContextActionService` (CAS) are client-only. They work in `LocalScript`, `ModuleScript` required by a `LocalScript`, or `Script` with `RunContext` set to `Client`. Server-side calls silently no-op.

## Input Action System and Server Authority

For a Server Authority project, inputs that affect the core simulation should use Roblox's Input Action System (`InputAction` and `InputContext`) rather than traditional `UserInputService.InputBegan` or a continuous `RemoteEvent` stream. Store the current action state where the shared simulation can read it, then process synchronized movement or physics through `RunService:BindToSimulation()` (requires `Workspace.UseFixedSimulation` enabled in Studio) so client prediction and server rollback use the same input history.

`ContextActionService` remains useful for UI-only actions and classic projects. Do not use the UI binding choice as a security boundary; the server still validates the resulting action and its game-specific permissions.

## UserInputService: Properties

| Property | Type | Notes |
|----------|------|-------|
| `KeyboardEnabled` / `MouseEnabled` | bool | Physical keyboard/mouse present |
| `TouchEnabled` | bool | Touchscreen present (mobile + some laptops) |
| `GamepadEnabled` | bool | Any supported gamepad connected |
| `AccelerometerEnabled` / `GyroscopeEnabled` | bool | Mobile sensors present |
| `VREnabled` | bool | VR headset active |
| `PreferredInput` | Enum.UserInputType | Device the player is **currently using most**. Better than per-device flags on hybrids. |
| `MouseBehavior` | Enum.MouseBehavior | `Default`, `LockCenter`, `LockCurrentPosition` |
| `MouseDeltaSensitivity` | number | 0–1, sensitivity multiplier |
| `MouseIcon` / `MouseIconEnabled` / `MouseIconContent` | string/bool | Custom cursor (AssetId, ContentText) |
| `OnScreenKeyboardPosition` / `OnScreenKeyboardSize` / `OnScreenKeyboardVisible` | Vector2/bool | Mobile/console on-screen keyboard state |
| `ModalEnabled` | bool | Block all input while a modal is active |
| `UserHeadCFrame` / `GetUserCFrame()` | CFrame | VR head pose |

## UserInputService: Methods (selection)

| Method | Returns | Use for |
|--------|---------|---------|
| `IsKeyDown(KeyCode)` | bool | Held keyboard keys |
| `IsMouseButtonPressed(UserInputType)` | bool | Held mouse buttons |
| `IsGamepadButtonDown(UserInputType, KeyCode)` | bool | Held gamepad buttons |
| `GetKeysPressed()` | InputObject[] | All held keyboard inputs |
| `GetMouseButtonsPressed()` | InputObject[] | All held mouse buttons |
| `GetMouseDelta()` | Vector2 | Per-frame mouse movement |
| `GetMouseLocation()` | Vector2 | Mouse position in viewport |
| `GetLastInputType()` | Enum.UserInputType | Last input across all devices |
| `GetConnectedGamepads()` | UserInputType[] | Currently connected gamepads |
| `GetGamepadState(UserInputType)` | InputObject[] | All active inputs on a gamepad |
| `GetGamepadConnected(UserInputType)` | bool | Is a specific pad slot connected |
| `GetDeviceAcceleration()` / `GetDeviceGravity()` / `GetDeviceRotation()` | Vector3 | Current mobile sensor readings |
| `GetFocusedTextBox()` | TextBox? | Currently-focused text input (if any) |
| `GetStringForKeyCode(KeyCode)` / `GetImageForKeyCode(KeyCode)` | string | Display labels for key bindings |
| `RecenterUserHeadCFrame()` | () | Reset VR head to current look direction |

## UserInputService: Events

### Discrete (Began → Ended)
- `InputBegan(input: InputObject, gameProcessedEvent: boolean)`: fires when input starts. Does NOT fire for mouse wheel.
- `InputChanged(input, gameProcessedEvent)`: fires while input is changing (mouse move, thumbstick, wheel, drag).
- `InputEnded(input, gameProcessedEvent)`: fires when input stops.

All three only fire when the Roblox client window has focus.

### Touch (high-level gestures)
- `TouchTap`, `TouchTapInWorld` (world-space position), `TouchPan`, `TouchPinch`, `TouchRotate`, `TouchSwipe`, `TouchLongPress`, `TouchDrag`.

### Touch (raw)
- `TouchStarted`, `TouchMoved`, `TouchEnded`. Use raw events when you need per-touch tracking across multiple fingers.

### Gamepad
- `GamepadConnected(UserInputType)`, `GamepadDisconnected(UserInputType)`.

### Mobile sensors
- `DeviceGravityChanged(Vector3, rotation)`: fires when accelerometer present + `AccelerometerEnabled`.
- `DeviceRotationChanged(CFrame, rotation, CFrame)`: fires when gyroscope present.
- `DeviceAccelerationChanged(Vector3, acceleration)`: fires when accelerometer present.

### Player state
- `JumpRequest()`: fires on jump key press. Fires multiple times per jump; debounce.
- `LastInputTypeChanged(Enum.UserInputType)`: when the active input device changes.
- `PointerAction(Enum.PointerAction, Vector2, number)`: middle-click navigation.

### UI focus
- `TextBoxFocused(TextBox)`, `TextBoxFocusReleased(TextBox)`: track when text input gains/loses focus.

### Window
- `WindowFocused()`, `WindowFocusReleased()`: fires when the Roblox window gains/loses OS focus.

### VR
- `UserCFrameChanged(Enum.UserCFrame, CFrame)`: head/hand motion in VR.

## InputObject

Properties you read off the input arg:
- `UserInputType`: Keyboard, MouseButton1..3, MouseWheel, MouseMovement, Touch, Gamepad1..8, Accelerometer, Gyro, etc.
- `KeyCode`: the specific key/button (e.g. `Enum.KeyCode.Space`, `Enum.KeyCode.ButtonA`).
- `UserInputState`: `Begin`, `Change`, `End`, `Cancel`. `Cancel` fires when input was in progress and another action bound over it.
- `Position`: Vector2 in viewport (mouse, touch).
- `Delta`: Vector3 (mouse/gamepad movement this frame).

Note: when `Cancel` fires, the `InputObject` is `UserInputType.None` / `KeyCode.Unknown`.

## ContextActionService

### BindAction

Signature: `BindAction(actionName: string, handler: Function, createTouchButton: boolean, ...inputTypes)`.

The handler receives `(actionName, inputState, inputObject)` and returns `Enum.ContextActionResult`:
- `Sink`: consume the input. Stops propagation.
- `Pass`: let lower-priority bindings also receive it.

Bindings form a **stack**: most recent binding on the same input wins. When you unbind, the previous binding takes over. Use `BindActionAtPriority` to force ordering (higher priority first).

**Touch button auto-creation**: set `createTouchButton=true` and an `ImageButton` is auto-added under `PlayerGui.ContextActionGui.ContextButtonFrame`. Max 7 buttons per screen. First binding creates the ScreenGui + Frame automatically.

### Full signature table

| Method | Purpose |
|--------|---------|
| `BindAction(name, handler, createTouchButton, ...inputs)` | Standard binding |
| `BindActionAtPriority(name, handler, createTouchButton, priority, ...inputs)` | Force order via priority |
| `BindActionToInputTypes(name, handler, createTouchButton, inputTypesList, ...)` | Bind from an array of input types |
| `BindActivate(...)` | Bind to the player's "Activate" button (used for Tools) |
| `UnbindAction(name)` | Remove a binding |
| `UnbindActivate()` | Remove activate binding |
| `UnbindAllActions()` | Clear everything |
| `GetButton(name)` | Get the auto-created `ImageButton` for customization |
| `GetBoundActionInfo(name)` | Inspect what a name is currently bound to |
| `GetAllBoundActionInfo()` | All currently-bound actions (for debugging) |
| `SetTitle`/`SetImage`/`SetPosition`/`SetDescription` | Customize a mobile button's appearance |
| `GetCurrentLocalToolIcon()` | Currently-equipped tool icon (for CAS-owned GUI) |

### Action handler return values

```luau
local function handleAction(actionName: string, inputState: Enum.UserInputState, input: InputObject)
    if inputState == Enum.UserInputState.Begin then
        -- start something
    elseif inputState == Enum.UserInputState.End then
        -- stop it
    elseif inputState == Enum.UserInputState.Cancel then
        -- we were unbound mid-action; clean up
    end

    -- Return Sink to consume, Pass to fall through
    return Enum.ContextActionResult.Sink
end
```

### Tool-equip pattern (the canonical CAS use case)

```luau
-- Place this LocalScript inside a Tool
local CAS = game:GetService("ContextActionService")
local ACTION_RELOAD = "Reload"

local function handleAction(actionName, inputState, _input)
    if actionName == ACTION_RELOAD and inputState == Enum.UserInputState.Begin then
        print("Reloading!")
    end
end

tool.Equipped:Connect(function()
    CAS:BindAction(ACTION_RELOAD, handleAction, true, Enum.KeyCode.R)
end)

tool.Unequipped:Connect(function()
    CAS:UnbindAction(ACTION_RELOAD)
end)
```

### Bind vs InputBegan: when to use which

Use `ContextActionService.BindAction` when:
- The action only exists in a context (holding tool, sitting in seat, near door).
- You want automatic conflict resolution with chat/text input.
- You want automatic mobile touch buttons.

Use `UserInputService.InputBegan` when:
- The action is always available (movement, inventory toggle).
- You need raw per-frame state (thumbstick position, mouse delta).
- You're handling complex multi-input logic that doesn't map cleanly to "contexts."

## Cross-Platform Binding Pattern

Bind one logical action to keyboard + gamepad + touch in one call:

```luau
local moving = false

local function handleMoveUp(_name, state, _input)
    -- Process stop states FIRST, before any key-code filtering:
    -- ContextActionService delivers End/Cancel with KeyCode.Unknown
    -- (e.g. unbound mid-press, synthesized touch-button release), and a
    -- key-code gate would skip the stop path and strand the action active.
    if state == Enum.UserInputState.End or state == Enum.UserInputState.Cancel then
        moving = false -- idempotent: safe even if Begin never ran
        return Enum.ContextActionResult.Sink
    end
    if state == Enum.UserInputState.Begin then
        moving = true
    end
    return Enum.ContextActionResult.Sink
end

-- W key + left thumbstick up on any gamepad + mobile button
CAS:BindAction("MoveUp", handleMoveUp, true,
    Enum.KeyCode.W,
    Enum.PlayerActions.MoveUp   -- also binds default WASD / stick
)
```

Gate handlers on `state`, not on `input.KeyCode`: touch-button input also arrives with `KeyCode.Unknown`, so a key-code filter on the start path would drop mobile presses too. Call `UnbindAction` on context exit; the `Cancel` delivery then clears the running state.

For movement bindings, prefer `Enum.PlayerActions` (e.g. `MoveForward`, `Jump`); they automatically bind to WASD, arrows, left stick, and d-pad across platforms.

## UI Focus and Directional Selection

`ContextActionService` maps gameplay actions. It does not design the focus graph for menus. For native UI navigation:

```luau
local GuiService = game:GetService("GuiService")

firstButton.Selectable = true
secondButton.Selectable = true
GuiService.SelectedObject = firstButton
```

Set `SelectedObject` when a menu opens or a modal takes control, and clear or restore it when that owner closes. For ambiguous layouts, use selection groups and explicit directional behavior where the current UI API supports them. Test gamepad, keyboard arrows, covered elements, nested containers, and dynamic list updates. The Roblox `focus-navigation` repository provides a richer optional focus model with React integration; it is not required for native selection.

## Dragging: DragDetector and UIDragDetector

`DragDetector` (3D; parent under a `BasePart` or `Model`) and `UIDragDetector` (2D; parent under any `GuiObject`) make objects draggable via all input types — mouse, touch, gamepad, VR — often with zero code. Both work in Studio edit mode while the Select/Move/Scale/Rotate tools (and, for UI, UI-editor plugins) are not active. Sources: create.roblox.com/docs/ui/3D-drag-detectors, create.roblox.com/docs/ui/ui-drag-detectors.

### Choosing a detector

| Need | Use |
|------|-----|
| Click/hover only, no motion | `ClickDetector` (`MouseClick`) |
| Drag a 3D part/model, optionally with physics response | `DragDetector` |
| Drag/rotate a UI element (sliders, spinners, inventory icons) | `UIDragDetector` |

`DragDetector` is the general-purpose option: it inherits `ClickDetector` members (`MouseClick`, `RightMouseClick`, `MouseHoverEnter`/`MouseHoverLeave`, `CursorIcon`, `MaxActivationDistance`), supports 3D dragging of anchored parts (exact placement on release) and unanchored parts (constraint-force physics), and is highly scriptable (`Scriptable` drag style, custom constraint functions). `UIDragDetector` is the newer UI-only counterpart — prefer it over hand-rolled `GuiObject` input tracking for 2D drags. Both expose the same event trio, so knowledge transfers. (*practitioner*: UIDragDetector fully released Dec 2025, announced Aug 2024 — devforum.roblox.com/t/introducing-uidragdetectors-released/3109263.)

### DragDetector essentials

Default behavior: draggable in the ground plane. Key properties (defaults): `DragStyle` (`TranslatePlane`), `Axis` (world Y; changing it updates `Orientation` and vice versa), `ResponseStyle` (`Geometric`), `RunLocally` (false), `Enabled` (true).

`DragStyle` (Enum.DragDetectorDragStyle): `TranslateLine` (1D along `Axis`), `TranslatePlane` (2D perpendicular to `Axis`), `TranslatePlaneOrLine`/`TranslateLineOrPlane` (2D or 1D, modifier toggles), `TranslateViewPlane` (always faces the camera, updates live), `RotateAxis`, `RotateTrackball`, `Scriptable` (custom function), `BestForDevice` (per-input default).

`ResponseStyle` (Enum.DragDetectorResponseStyle):
- `Geometric`: object is moved exactly; unanchored parts are temporarily anchored during the drag and restored on release.
- `Physical`: unanchored parts are moved by constraint forces — tune `Responsiveness` (10), `MaxForce` (10000000), `MaxTorque` (10000), `ApplyAtCenterOfMass` (false = force at the clicked point).
- `Custom`: object does not move; `DragFrame` still updates and events still fire — drive movement yourself.

Limits: `MinDragTranslation`/`MaxDragTranslation` (Vector3) and `MinDragAngle`/`MaxDragAngle` (`RotateAxis` only) impede motion but are not constraints. When using limits, set `ReferenceInstance` first — without a reference frame, limits re-anchor to the object's own pose on each drag.

Direction/reference: `Axis`/`Orientation` set the direction of motion; `ReferenceInstance` defines the reference frame — `DragFrame` (CFrame) is expressed relative to it and readable via `GetPropertyChangedSignal("DragFrame")` or `GetReferenceFrame()`.

Permissions: `PermissionPolicy` = `Nobody` | `Everybody` (default) | `Scriptable` plus `SetPermissionPolicyFunction(function(player, part) -> boolean)`. Missing function or invalid return blocks everyone.

Replication: `RunLocally=false` (default) → the client interprets input and the SERVER performs the drag: event connections and registered functions belong in server `Script`s. `RunLocally=true` → client-local: use `LocalScript`s and RemoteEvents to propagate changes.

Events: `DragStart(playerWhoDragged: Player, cursorRay: Ray, viewFrame: CFrame, hitFrame: CFrame, clickedPart: BasePart, ...)`, `DragContinue(playerWhoDragged, cursorRay, viewFrame, ...)`, `DragEnd(playerWhoDragged)`. Modifier keys for dual-mode styles: `KeyboardModeSwitchKeyCode`/`GamepadModeSwitchKeyCode`/`VRSwitchKeyCode` (default LeftControl / ButtonR1 / ButtonL2).

Scripting hooks: `SetDragStyleFunction(fn)` with `DragStyle = Scriptable` — `fn(cursorRay: Ray) -> CFrame?` returning the desired pivot CFrame in world space (`nil` = don't move). `AddConstraintFunction(priority, fn): RBXScriptConnection` — `fn(proposedMotion: CFrame) -> CFrame`, chained by priority; `Disconnect()` to remove. `RestartDrag()` re-evaluates the drag after changing `DragStyle`/`Axis`/`SecondaryAxis`.

```luau
-- Drawer: slide along its own axis, clamped (illustrative)
local detector = Instance.new("DragDetector")
detector.DragStyle = Enum.DragDetectorDragStyle.TranslateLine
detector.ResponseStyle = Enum.DragDetectorResponseStyle.Geometric
detector.ReferenceInstance = dresserBody -- stable frame for the limits
detector.MinDragTranslation = Vector3.zero
detector.MaxDragTranslation = Vector3.new(0, 0, -4) -- open distance
detector.Parent = drawer

detector.DragStart:Connect(function(player, ray, viewFrame, hitFrame, clickedPart)
    print(player.Name, "started dragging", clickedPart.Name)
end)
detector.DragEnd:Connect(function(player)
    -- e.g. RemoteEvent to the server to latch state / play a sound
end)
```

### UIDragDetector essentials

`DragStyle` (Enum.UIDragDetectorDragStyle): `TranslatePlane` (default, free 2D), `TranslateLine` (1D along `DragAxis: Vector2`), `Rotate`, `Scriptable`. `ResponseStyle` (Enum.UIDragDetectorResponseStyle): `Offset` (default; applies motion to the parent's `Position` Offset), `Scale`, `CustomOffset`/`CustomScale` (UI does not move; `DragUDim2` still updates and events still fire — read `DragUDim2`/`DragRotation` to drive logic yourself).

Limits and bounds: `MinDragTranslation`/`MaxDragTranslation` (UDim2), `MinDragAngle`/`MaxDragAngle` (`Rotate`), `BoundingUI` (a `GuiBase2d`, e.g. a container Frame) with `BoundingBehavior` (`Automatic` default | `EntireObject` | `HitPoint`), and `ReferenceUIInstance` to re-anchor axes/origin. Speed: `SelectionModeDragSpeed` (UDim2), `SelectionModeRotateSpeed` (deg/sec), `UIDragSpeedAxisMapping`.

Events: `DragStart(inputPosition: Vector2)`, `DragContinue(inputPosition: Vector2)`, `DragEnd(inputPosition: Vector2)`. For custom logic, connect `DragContinue` and read the parent's `Position` (or `DragUDim2` under Custom styles) — the same callback pattern as a `.Activated` button handler.

Scripting hooks: `SetDragStyleFunction(fn)` with `Scriptable` — `fn(inputPosition: Vector2) -> UDim2, float, [relativity, space]`; `DragSpace` (`Parent` | `LayerCollector`) and `DragRelativity` (`Absolute` | `Relative`) define return semantics. `AddConstraintFunction` chains like the 3D detector but passes UDim2 + float. `GetReferencePosition()`/`GetReferenceRotation()` read the reference origin. Event connections and registered functions run client-side (`LocalScript` or `RunContext = Client`), like all UI input.

```luau
-- Volume slider: handle drags along X inside its container (illustrative)
local handle = script.Parent            -- Frame inside a container Frame
local detector = Instance.new("UIDragDetector")
detector.DragStyle = Enum.UIDragDetectorDragStyle.TranslateLine
detector.DragAxis = Vector2.new(1, 0)   -- X only
detector.ResponseStyle = Enum.UIDragDetectorResponseStyle.Scale
detector.BoundingUI = handle.Parent     -- confine to container bounds
detector.Parent = handle

detector.DragContinue:Connect(function(_inputPos)
    local value = math.clamp(handle.Position.X.Scale, 0, 1)
    -- apply `value` to game state (volume, fill bar, etc.)
end)
```

## Gamepad Deep Dive

### Detection
```luau
if UIS.GamepadEnabled then
    for _, pad in ipairs(UIS:GetConnectedGamepads()) do
        print("Connected pad:", pad)  -- Enum.UserInputType.Gamepad1..8
    end
end

UIS.GamepadConnected:Connect(function(pad)
    print("Connected:", pad)
end)
UIS.GamepadDisconnected:Connect(function(pad)
    print("Disconnected:", pad)
end)
```

### Reading inputs (event-style)
```luau
UIS.InputBegan:Connect(function(input, gpe)
    if input.UserInputType == Enum.UserInputType.Gamepad1 and input.KeyCode == Enum.KeyCode.ButtonA then
        if gpe then return end  -- UI consumed it
        print("A pressed on pad 1")
    end
end)
```

### Reading inputs (poll-style for held-state)
```luau
RunService.RenderStepped:Connect(function()
    if UIS:IsGamepadButtonDown(Enum.UserInputType.Gamepad1, Enum.KeyCode.ButtonR2) then
        -- accelerate
    end

    local state = UIS:GetGamepadState(Enum.UserInputType.Gamepad1)
    for _, input in ipairs(state) do
        if input.KeyCode == Enum.KeyCode.Thumbstick1 then
            -- input.Position is the stick direction
        end
    end
end)
```

### Thumbstick deadzone
Sticks report a small non-zero value at rest. Apply a deadzone:
```luau
local function applyDeadzone(stick: Vector2, dz: number): Vector2
    if stick.Magnitude < dz then return Vector2.zero end
    return (stick - stick.Unit * dz) / (1 - dz)
end
```

### Common gamepad buttons (KeyCode enum)
- Face: `ButtonA`, `ButtonB`, `ButtonX`, `ButtonY`
- Shoulders: `ButtonL1`, `ButtonR1`, `ButtonL2`, `ButtonR2` (triggers)
- Sticks: `ButtonL3`, `ButtonR3` (click), `Thumbstick1`, `Thumbstick2` (axes)
- D-pad: `DPadUp`, `DPadDown`, `DPadLeft`, `DPadRight`
- System: `ButtonStart`, `ButtonSelect`

## Touch Deep Dive

### High-level gestures
- `TouchTap`: brief single-finger tap.
- `TouchTapInWorld`: same, with the world-space hit position (via `Camera:ScreenPointToRay`).
- `TouchPan`: drag with one finger. Use for camera rotation/zoom in mobile games.
- `TouchPinch`: two-finger pinch. Use for zoom.
- `TouchRotate`: two-finger rotate gesture.
- `TouchSwipe`: quick directional swipe.
- `TouchLongPress`: held touch.
- `TouchDrag`: continuous drag (useful for inventory drag-and-drop).

### Multi-touch tracking
Use raw `TouchStarted`/`TouchMoved`/`TouchEnded` and maintain your own per-touch state by `input` instance.

## Mobile Sensors

### Accelerometer (gravity direction)
```luau
if UIS.AccelerometerEnabled then
    UIS.DeviceGravityChanged:Connect(function(gravity, _rot)
        -- gravity is a unit Vector3 pointing in the direction gravity appears
        -- to pull on the device. Z is out of screen.
        ball.BodyForce.Force = gravity * workspace.Gravity * ball:GetMass()
    end)
end
```

### Gyroscope (device rotation)
```luau
if UIS.GyroscopeEnabled then
    UIS.DeviceRotationChanged:Connect(function(cframe, _rot, _prev)
        -- cframe represents the device's orientation in world space
        camera.CFrame = CFrame.new(camera.CFrame.Position) * (cframe - Vector3.new(0,0,0))
    end)
end
```

## VRService

`VRService` handles Roblox's VR interaction. Check `VREnabled` first; every method below is LocalScript-only.

Key members (verified against the class page):

- **`VREnabled`** (read-only boolean) — true when a VR session is active. The same flag exists on `UserInputService`.
- **`GetUserCFrame(type: Enum.UserCFrame): CFrame`** — device pose as an offset from real-world origin. Multiply by `Camera.CFrame`, and scale the position by `Camera.HeadScale`, to place something at a headset/hand:
  ```luau
  local handOffset = VRService:GetUserCFrame(Enum.UserCFrame.LeftHand)
  handOffset = handOffset.Rotation + handOffset.Position * camera.HeadScale
  part.CFrame = camera.CFrame * handOffset
  ```
- **`GetUserCFrameEnabled(type): boolean`** — whether that device (Head, LeftHand, RightHand) is connected.
- **`UserCFrameChanged(type, cframe)`** — fires on device movement; re-mirror parts there.
- **`RecenterUserHeadCFrame()`** — re-centers the head pose (same as `UserInputService:RecenterUserHeadCFrame()`).
- **`RequestNavigation(cframe, inputUserCFrame)`** — shows a parabola path visualizer toward a destination; pairs with the `NavigationRequested` event.
- **`GetTouchpadMode(pad)` / `SetTouchpadMode(pad, mode)`** — legacy touchpad interaction modes (`Enum.VRTouchpad`, `Enum.VRTouchpadMode`).
- Behavior properties: `AutomaticScaling` (`VRScaling.World` makes `Camera.HeadScale` track avatar size), `AvatarGestures` (server-set boolean for controller-driven hand/head animation), `FadeOutViewOnCollision` (default true, fades the view when the head clips geometry — do not disable without a replacement), `GuiInputUserCFrame` (which device drives UI input), `LaserPointer`, `ThirdPersonFollowCamEnabled`.

Do not invent member names: older community references carry stale VRService members. Check the class page when in doubt.

## Patterns

### Platform-adaptive mobile UI

Don't gate mobile UI on `UIS.TouchEnabled` alone: a touchscreen laptop would show mobile controls even when the player is using mouse/keyboard. Roblox core scripts detect the **last input actually used** (`GetLastInputType` / `LastInputTypeChanged`), which adapts instantly when a player switches devices mid-session.

```luau
local UIS = game:GetService("UserInputService")
local frame = script.Parent -- mobile button container

local function updateInput()
    local last = UIS:GetLastInputType()
    if last == Enum.UserInputType.Focus then return end -- app focus, not an input
    frame.Visible = (last == Enum.UserInputType.Touch)
end

updateInput()
UIS.LastInputTypeChanged:Connect(updateInput)
```

For placement, anchor to the safe area (a child `ScreenGui` with `ScreenInsets = DeviceSafeInsets` gives the safe `AbsolutePosition`/`AbsoluteSize`). Keep custom buttons out of the thumbstick zone (left edge) and don't hard-place them relative to the default jump button, which swaps size/position at a ~500px min-axis preset.

```luau
-- Recompute position from the safe-area screen size each frame
local RS = game:GetService("RunService")
RS.RenderStepped:Connect(function()
    if not frame.Visible then return end
    local size = frame.Screen.AbsoluteSize
    local minAxis = math.min(size.X, size.Y)
    local buttonSize = (minAxis <= 500) and 70 or 120
    frame.Size = UDim2.fromOffset(buttonSize, buttonSize)
    frame.Position = UDim2.new(1, -(buttonSize * 1.5 - 10), 1, -buttonSize * 1.75)
end)
```

### Switch UI on PreferredInput change
```luau
UIS.LastInputTypeChanged:Connect(function(newType)
    if newType == Enum.UserInputType.Touch then
        showMobileButtons()
    elseif newType == Enum.UserInputType.Keyboard then
        hideMobileButtons()
    end
end)
```

### Camera mouse-look (client-only)
```luau
local camera = workspace.CurrentCamera
local ROT_SPEED = 0.003
local x, y = 0, 0

UIS.InputChanged:Connect(function(input, gpe)
    if gpe then return end
    if input.UserInputType == Enum.UserInputType.MouseMovement then
        x = x - input.Delta.X * ROT_SPEED
        y = math.clamp(y - input.Delta.Y * ROT_SPEED, -1.4, 1.4)
        camera.CFrame = CFrame.new(camera.CFrame.Position) * CFrame.Angles(y, x, 0)
    end
end)
```

### Touch camera drag
```luau
-- One finger owns the drag: identify it by its InputObject instance, which
-- stays the same across that touch's Started/Moved/Ended events.
local activeTouch: InputObject? = nil
local lastPos = Vector2.zero

UIS.TouchStarted:Connect(function(input, gpe)
    if gpe then return end
    if activeTouch then return end -- a second finger never hijacks the drag
    activeTouch = input
    lastPos = input.Position
end)

UIS.TouchMoved:Connect(function(input, gpe)
    if input ~= activeTouch or gpe then return end
    local delta = input.Position - lastPos
    -- rotate camera by delta
    lastPos = input.Position
end)

UIS.TouchEnded:Connect(function(input)
    if input ~= activeTouch then return end -- a different finger lifting is ignored
    activeTouch = nil
end)

-- Clear ownership on teardown so a stale touch can't block future drags.
script.Destroying:Connect(function()
    activeTouch = nil
end)
```

### Disable default jump and handle custom
```luau
humanoid:SetStateEnabled(Enum.HumanoidStateType.Jumping, false)

UIS.JumpRequest:Connect(function()
    if canJump() then
        humanoid.Jump = true
    end
end)
```

## Common Mistakes

- **Forgetting `gameProcessedEvent` filter.** If `gpe==true` in InputBegan, a UI element (button, text box, chat) already consumed it. Filter out for gameplay.
- **Using `UserInputService` on the server.** Silently no-ops. Use `LocalScript`.
- **Not un-binding on context exit.** Stale bindings fire even after the player leaves the context. Call `UnbindAction` in cleanup.
- **Hard-coding platform assumptions.** Check `TouchEnabled` / `GamepadEnabled` at runtime; don't assume desktop-only.
- **Reading `MouseWheel` from InputBegan.** Wheel events only fire `InputChanged`.
- **Touching `IsKeyDown` in a tight loop without throttling.** It's cheap but RenderStepped is the right cadence.
- **No debounce on JumpRequest.** Fires once per frame the jump key is held.
- **Mixing `PlayerActions` with `KeyCode` in a single binding.** Use one or the other, not both. `PlayerActions` maps to the platform's natural input.
- **Setting `MouseBehavior = LockCenter` and forgetting to reset it.** Reset on player leave or context exit.
- **Bypassing `ContextActionService` because it "feels indirect."** Most gameplay bindings should use CAS: it correctly handles chat/text-box conflicts for free.
- **Auto-creating touch buttons beyond the 7 limit.** BindAction silently refuses to create the 8th button.
- **Using `gameProcessedEvent` to filter CAS handlers.** CAS doesn't pass `gpe` to its handlers; by design, CAS handles conflicts itself.