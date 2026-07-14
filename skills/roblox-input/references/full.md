# Roblox Input — Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

Both `UserInputService` (UIS) and `ContextActionService` (CAS) are client-only. They work in `LocalScript`, `ModuleScript` required by a `LocalScript`, or `Script` with `RunContext` set to `Client`. Server-side calls silently no-op.

## UserInputService — Properties

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

## UserInputService — Methods (selection)

| Method | Returns | Use for |
|--------|---------|---------|
| `IsKeyDown(KeyCode)` | bool | Held keyboard keys |
| `IsMouseButtonPressed(UserInputType)` | bool | Held mouse buttons |
| `IsGamepadButtonDown(UserInputType, KeyCode)` | bool | Held gamepad buttons |
| `GetKeysPressed()` | {KeyCode, InputObject}[] | All held keys (with `InputObject` for key-up detection) |
| `GetMouseButtonsPressed()` | InputObject[] | All held mouse buttons |
| `GetMouseDelta()` | (number, number) | Per-frame mouse movement |
| `GetMouseLocation()` | Vector2 | Mouse position in viewport |
| `GetLastInputType()` | Enum.UserInputType | Last input across all devices |
| `GetConnectedGamepads()` | UserInputType[] | Currently connected gamepads |
| `GetGamepadState(UserInputType)` | InputObject[] | All active inputs on a gamepad |
| `GetGamepadConnected(UserInputType)` | bool | Is a specific pad slot connected |
| `GetDeviceAcceleration()` / `GetDeviceGravity()` / `GetDeviceRotation()` | Vector3 | Current mobile sensor readings |
| `GetFocusedTextBox()` | TextBox? | Currently-focused text input (if any) |
| `GetStringForKeyCode(KeyCode)` / `GetImageForKeyCode(KeyCode)` | string | Display labels for key bindings |
| `RecenterUserHeadCFrame()` | () | Reset VR head to current look direction |

## UserInputService — Events

### Discrete (Began → Ended)
- `InputBegan(input: InputObject, gameProcessedEvent: boolean)` — fires when input starts. Does NOT fire for mouse wheel.
- `InputChanged(input, gameProcessedEvent)` — fires while input is changing (mouse move, thumbstick, wheel, drag).
- `InputEnded(input, gameProcessedEvent)` — fires when input stops.

All three only fire when the Roblox client window has focus.

### Touch (high-level gestures)
- `TouchTap`, `TouchTapInWorld` (world-space position), `TouchPan`, `TouchPinch`, `TouchRotate`, `TouchSwipe`, `TouchLongPress`, `TouchDrag`.

### Touch (raw)
- `TouchStarted`, `TouchMoved`, `TouchEnded`. Use raw events when you need per-touch tracking across multiple fingers.

### Gamepad
- `GamepadConnected(UserInputType)`, `GamepadDisconnected(UserInputType)`.

### Mobile sensors
- `DeviceGravityChanged(Vector3, rotation)` — fires when accelerometer present + `AccelerometerEnabled`.
- `DeviceRotationChanged(CFrame, rotation, CFrame)` — fires when gyroscope present.
- `DeviceAccelerationChanged(Vector3, acceleration)` — fires when accelerometer present.

### Player state
- `JumpRequest()` — fires on jump key press. Fires multiple times per jump — debounce.
- `LastInputTypeChanged(Enum.UserInputType)` — when the active input device changes.
- `PointerAction(Enum.PointerAction, Vector2, number)` — middle-click navigation.

### UI focus
- `TextBoxFocused(TextBox)`, `TextBoxFocusReleased(TextBox)` — track when text input gains/loses focus.

### Window
- `WindowFocused()`, `WindowFocusReleased()` — fires when the Roblox window gains/loses OS focus.

### VR
- `UserCFrameChanged(Enum.UserCFrame, CFrame)` — head/hand motion in VR.

## InputObject

Properties you read off the input arg:
- `UserInputType` — Keyboard, MouseButton1..3, MouseWheel, MouseMovement, Touch, Gamepad1..8, Accelerometer, Gyro, etc.
- `KeyCode` — the specific key/button (e.g. `Enum.KeyCode.Space`, `Enum.KeyCode.ButtonA`).
- `UserInputState` — `Begin`, `Change`, `End`, `Cancel`. `Cancel` fires when input was in progress and another action bound over it.
- `Position` — Vector2 in viewport (mouse, touch).
- `Delta` — Vector3 (mouse/gamepad movement this frame).

Note: when `Cancel` fires, the `InputObject` is `UserInputType.None` / `KeyCode.Unknown`.

## ContextActionService

### BindAction

Signature: `BindAction(actionName: string, handler: Function, createTouchButton: boolean, ...inputTypes)`.

The handler receives `(actionName, inputState, inputObject)` and returns `Enum.ContextActionResult`:
- `Sink` — consume the input. Stops propagation.
- `Pass` — let lower-priority bindings also receive it.

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

### Bind vs InputBegan — when to use which

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
local function handleMoveUp(name, state, input)
    if input.KeyCode == Enum.KeyCode.Unknown then return Enum.ContextActionResult.Pass end
    if state == Enum.UserInputState.Begin then
        -- start moving up
    else
        -- stop
    end
    return Enum.ContextActionResult.Sink
end

-- W key + left thumbstick up on any gamepad + mobile button
CAS:BindAction("MoveUp", handleMoveUp, true,
    Enum.KeyCode.W,
    Enum.PlayerActions.MoveUp   -- also binds default WASD / stick
)
```

For movement bindings, prefer `Enum.PlayerActions` (e.g. `MoveForward`, `Jump`) — they automatically bind to WASD, arrows, left stick, and d-pad across platforms.

## UI Focus and Directional Selection

`ContextActionService` maps gameplay actions. It does not design the focus graph for menus. For native UI navigation:

```luau
local GuiService = game:GetService("GuiService")

firstButton.Selectable = true
secondButton.Selectable = true
GuiService.SelectedObject = firstButton
```

Set `SelectedObject` when a menu opens or a modal takes control, and clear or restore it when that owner closes. For ambiguous layouts, use selection groups and explicit directional behavior where the current UI API supports them. Test gamepad, keyboard arrows, covered elements, nested containers, and dynamic list updates. The Roblox `focus-navigation` repository provides a richer optional focus model with React integration; it is not required for native selection.

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
- `TouchTap` — brief single-finger tap.
- `TouchTapInWorld` — same, with the world-space hit position (via `Camera:ScreenPointToRay`).
- `TouchPan` — drag with one finger. Use for camera rotation/zoom in mobile games.
- `TouchPinch` — two-finger pinch. Use for zoom.
- `TouchRotate` — two-finger rotate gesture.
- `TouchSwipe` — quick directional swipe.
- `TouchLongPress` — held touch.
- `TouchDrag` — continuous drag (useful for inventory drag-and-drop).

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

## Patterns

### Platform-adaptive UI
```luau
local Platform = {
    HasKeyboard = UIS.KeyboardEnabled,
    HasMouse    = UIS.MouseEnabled,
    IsTouch     = UIS.TouchEnabled,
    IsGamepad   = UIS.GamepadEnabled,
}

if Platform.IsTouch then
    showMobileButtons()
elseif Platform.IsGamepad then
    showGamepadPrompts()
end
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
local dragging = false
local lastPos = Vector2.zero

UIS.TouchStarted:Connect(function(input, gpe)
    if gpe then return end
    dragging = true
    lastPos = input.Position
end)

UIS.TouchChanged:Connect(function(input, gpe)
    if not dragging or gpe then return end
    local delta = input.Position - lastPos
    -- rotate camera by delta
    lastPos = input.Position
end)

UIS.TouchEnded:Connect(function() dragging = false end)
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
- **Bypassing `ContextActionService` because it "feels indirect."** Most gameplay bindings should use CAS — it correctly handles chat/text-box conflicts for free.
- **Auto-creating touch buttons beyond the 7 limit.** BindAction silently refuses to create the 8th button.
- **Using `gameProcessedEvent` to filter CAS handlers.** CAS doesn't pass `gpe` to its handlers — by design, CAS handles conflicts itself.