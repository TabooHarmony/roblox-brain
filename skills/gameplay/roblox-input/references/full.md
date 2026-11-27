# Roblox Input: Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

Both `UserInputService` (UIS) and `ContextActionService` (CAS) are client-only. They work in `LocalScript`, `ModuleScript` required by a `LocalScript`, or `Script` with `RunContext` set to `Client`. Server-side calls silently no-op.

## Input Action System and Server Authority

For a Server Authority project, inputs that affect the core simulation should use Roblox's Input Action System (`InputAction` and `InputContext`) rather than traditional `UserInputService.InputBegan` or a continuous `RemoteEvent` stream. Store the current action state where the shared simulation can read it, then process synchronized movement or physics through `RunService:BindToSimulation()` (requires `Workspace.UseFixedSimulation` enabled in Studio) so client prediction and server rollback use the same input history.

<!-- temporal: 2026-11 --> **`ContextActionService` binding is planned for deprecation.** Its class page now says `BindAction` and the related binding methods aren't recommended for new work and are planned for deprecation, and points to the Input Action System. Keep existing CAS bindings working (the CAS sections below still document them) and migrate when you touch them. Do not use the binding choice as a security boundary; the server still validates the resulting action and its game-specific permissions.

### Input Action System essentials

- **Instances, not script bindings.** An `InputContext` groups `InputAction`s; each action holds `InputBinding`s (a key, a gamepad button, a touch `UIButton`). One `Pressed`/`Released` handler works on every device; read analog actions with `GetState()`.
- **Default player scripts.** `Workspace.PlayerScriptsUseInputActionSystem` is set in Studio, not by scripts. With it on, the default `PlayerModule` is injected under `StarterPlayer` and character controls run through input actions, so code that requires `PlayerScripts.PlayerModule` to read the move vector can silently get nothing. Find the movement action in your place's tree rather than hardcoding a path.
- **Block or override keys while a menu is open** by enabling a higher-`Priority` `InputContext` with `Sink` that binds those keys. A `KeyCode` binding ignores its `UIButton`. Avoid the deprecated `InputAction:Fire()`.
- **Input Action Manager (beta).** <!-- temporal: 2026-11 --> **Window > Input > Input Action Manager** is a matrix editor for contexts, actions and bindings. It scans existing input instances into the grid and puts new ones in an `Inputs` folder in `ReplicatedStorage`. Yellow warnings mark a missing binding; red warnings mark a duplicate binding. Audit with it before shipping a cross-platform update.

## UserInputService: Properties

| Property | Type | Notes |
|----------|------|-------|
| `KeyboardEnabled` / `MouseEnabled` | bool | Physical keyboard/mouse present |
| `TouchEnabled` | bool | Touchscreen present (mobile + some laptops) |
| `GamepadEnabled` | bool | Any supported gamepad connected |
| `AccelerometerEnabled` / `GyroscopeEnabled` | bool | Mobile sensors present |
| `VREnabled` | bool | VR headset active |
| `PreferredInput` | Enum.PreferredInput | Primary input the player is likely using now: `KeyboardAndMouse`, `Gamepad`, `Touch` or `MicroGamepad` (`MicroGamepad` is not set yet for TV remotes; see Micro Gamepads and TV Remotes). Changes during a session; observe it with `GetPropertyChangedSignal`. Better than per-device flags on hybrids. |
| `MouseBehavior` | Enum.MouseBehavior | `Default`, `LockCenter`, `LockCurrentPosition` |
| `MouseDeltaSensitivity` | number | 0–10, sensitivity multiplier for mouse-movement deltas (`GetMouseDelta()`, `InputChanged`); does not affect the cursor icon or the player's own camera-sensitivity setting |
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
| `GetDeviceAcceleration()` / `GetDeviceGravity()` | InputObject | Current mobile sensor reading; `input.Position` carries the force per local device axis |
| `GetDeviceRotation()` | (InputObject, CFrame) | Rotation-delta InputObject + current device orientation CFrame |
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
- `DeviceGravityChanged(gravity: InputObject)`: fires when accelerometer present + `AccelerometerEnabled`. Read `gravity.Position` (Vector3 gravity force per device axis).
- `DeviceRotationChanged(rotation: InputObject, cframe: CFrame)`: fires when gyroscope present. `rotation.Position`/`rotation.Delta` carry rotation values; `cframe` is the device's current orientation.
- `DeviceAccelerationChanged(acceleration: InputObject)`: fires when accelerometer present. Read `acceleration.Position` (force per device axis).

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

For new work, prefer an `InputAction` over both (see Input Action System essentials). In existing CAS code:

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

-- W key + d-pad up on any gamepad + mobile button
CAS:BindAction("MoveUp", handleMoveUp, true,
    Enum.KeyCode.W,
    Enum.KeyCode.DPadUp -- digital gamepad alternative
)
```

Gate handlers on `state`, not on `input.KeyCode`: touch-button input also arrives with `KeyCode.Unknown`, so a key-code filter on the start path would drop mobile presses too. Call `UnbindAction` on context exit; the `Cancel` delivery then clears the running state.

`Enum.PlayerActions` is deprecated in favor of `Enum.KeyCode` and should not be used in new work; its items are `CharacterForward`/`CharacterBackward`/`CharacterLeft`/`CharacterRight`/`CharacterJump` (no `MoveUp`/`MoveForward`/`Jump` members — old examples using those fail on lookup). Bind explicit `Enum.KeyCode` entries per platform instead, as above.

For analog movement, process changing values rather than treating the stick as a digital Begin/End button. `ContextActionService` can report `Change`; `UserInputService.InputChanged` also exposes stick updates through `input.KeyCode == Enum.KeyCode.Thumbstick1` and `input.Position` (see the deadzone pattern below). Use `GetGamepadState()` to initialize held input, or keep the character controller's default movement. The example above uses a digital d-pad binding, not an analog controller.

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

`DragDetector` (3D; parent under a `BasePart` or `Model`) and `UIDragDetector` (2D; parent under any `GuiObject`) make objects draggable via all input types (mouse, touch, gamepad, VR), often with zero code. Both work in Studio edit mode while the Select/Move/Scale/Rotate tools (and, for UI, UI-editor plugins) are not active. Sources: create.roblox.com/docs/ui/3D-drag-detectors, create.roblox.com/docs/ui/ui-drag-detectors.

### Choosing a detector

| Need | Use |
|------|-----|
| Click/hover only, no motion | `ClickDetector` (`MouseClick`) |
| Drag a 3D part/model, optionally with physics response | `DragDetector` |
| Drag/rotate a UI element (sliders, spinners, inventory icons) | `UIDragDetector` |

`DragDetector` is the general-purpose option: it inherits `ClickDetector` members (`MouseClick`, `RightMouseClick`, `MouseHoverEnter`/`MouseHoverLeave`, `CursorIcon`, `MaxActivationDistance`), supports 3D dragging of anchored parts (exact placement on release) and unanchored parts (constraint-force physics), and is highly scriptable (`Scriptable` drag style, custom constraint functions). `UIDragDetector` is the newer UI-only counterpart; prefer it over hand-rolled `GuiObject` input tracking for 2D drags. Both expose the same event trio, so knowledge transfers. (*practitioner*: UIDragDetector fully released Dec 2025, announced Aug 2024; source: devforum.roblox.com/t/introducing-uidragdetectors-released/3109263.)

### DragDetector essentials

Default behavior: draggable in the ground plane. Key properties (defaults): `DragStyle` (`TranslatePlane`), `Axis` (world Y; changing it updates `Orientation` and vice versa), `ResponseStyle` (`Geometric`), `RunLocally` (false), `Enabled` (true).

`DragStyle` (Enum.DragDetectorDragStyle): `TranslateLine` (1D along `Axis`), `TranslatePlane` (2D perpendicular to `Axis`), `TranslatePlaneOrLine`/`TranslateLineOrPlane` (2D or 1D, modifier toggles), `TranslateViewPlane` (always faces the camera, updates live), `RotateAxis`, `RotateTrackball`, `Scriptable` (custom function), `BestForDevice` (per-input default).

`ResponseStyle` (Enum.DragDetectorResponseStyle):
- `Geometric`: object is moved exactly; unanchored parts are temporarily anchored during the drag and restored on release.
- `Physical`: unanchored parts are moved by constraint forces; tune `Responsiveness` (10), `MaxForce` (10000000), `MaxTorque` (10000), `ApplyAtCenterOfMass` (false = force at the clicked point).
- `Custom`: object does not move; `DragFrame` still updates and events still fire, so drive movement yourself.

Limits: `MinDragTranslation`/`MaxDragTranslation` (Vector3) and `MinDragAngle`/`MaxDragAngle` (`RotateAxis` only) impede motion but are not constraints. When using limits, set `ReferenceInstance` first; without a reference frame, limits re-anchor to the object's own pose on each drag.

Direction/reference: `Axis`/`Orientation` set the direction of motion; `ReferenceInstance` defines the reference frame; `DragFrame` (CFrame) is expressed relative to it and readable via `GetPropertyChangedSignal("DragFrame")` or `GetReferenceFrame()`.

Permissions: `PermissionPolicy` = `Nobody` | `Everybody` (default) | `Scriptable` plus `SetPermissionPolicyFunction(function(player, part) -> boolean)`. Missing function or invalid return blocks everyone.

Replication: `RunLocally=false` (default) → the client interprets input and the SERVER performs the drag: event connections and registered functions belong in server `Script`s. `RunLocally=true` → client-local: use `LocalScript`s and RemoteEvents to propagate changes.

Events: `DragStart(playerWhoDragged: Player, cursorRay: Ray, viewFrame: CFrame, hitFrame: CFrame, clickedPart: BasePart, ...)`, `DragContinue(playerWhoDragged, cursorRay, viewFrame, ...)`, `DragEnd(playerWhoDragged)`. Modifier keys for dual-mode styles: `KeyboardModeSwitchKeyCode`/`GamepadModeSwitchKeyCode`/`VRSwitchKeyCode` (default LeftControl / ButtonR1 / ButtonL2).

Scripting hooks: `SetDragStyleFunction(fn)` with `DragStyle = Scriptable`: `fn(cursorRay: Ray) -> CFrame?` returning the desired pivot CFrame in world space (`nil` = don't move). `AddConstraintFunction(priority, fn): RBXScriptConnection`: `fn(proposedMotion: CFrame) -> CFrame`, chained by priority; `Disconnect()` to remove. `RestartDrag()` re-evaluates the drag after changing `DragStyle`/`Axis`/`SecondaryAxis`.

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

`DragStyle` (Enum.UIDragDetectorDragStyle): `TranslatePlane` (default, free 2D), `TranslateLine` (1D along `DragAxis: Vector2`), `Rotate`, `Scriptable`. `ResponseStyle` (Enum.UIDragDetectorResponseStyle): `Offset` (default; applies motion to the parent's `Position` Offset), `Scale`, `CustomOffset`/`CustomScale` (UI does not move; `DragUDim2` still updates and events still fire; read `DragUDim2`/`DragRotation` to drive logic yourself).

Limits and bounds: `MinDragTranslation`/`MaxDragTranslation` (UDim2), `MinDragAngle`/`MaxDragAngle` (`Rotate`), `BoundingUI` (a `GuiBase2d`, e.g. a container Frame) with `BoundingBehavior` (`Automatic` default | `EntireObject` | `HitPoint`), and `ReferenceUIInstance` to re-anchor axes/origin. Speed: `SelectionModeDragSpeed` (UDim2), `SelectionModeRotateSpeed` (deg/sec), `UIDragSpeedAxisMapping`.

Events: `DragStart(inputPosition: Vector2)`, `DragContinue(inputPosition: Vector2)`, `DragEnd(inputPosition: Vector2)`. For custom logic, connect `DragContinue` and read the parent's `Position` (or `DragUDim2` under Custom styles): the same callback pattern as a `.Activated` button handler.

Scripting hooks: `SetDragStyleFunction(fn)` with `Scriptable`: `fn(inputPosition: Vector2) -> UDim2, float, [relativity, space]`; `DragSpace` (`Parent` | `LayerCollector`) and `DragRelativity` (`Absolute` | `Relative`) define return semantics. `AddConstraintFunction` chains like the 3D detector but passes UDim2 + float. `GetReferencePosition()`/`GetReferenceRotation()` read the reference origin. Event connections and registered functions run client-side (`LocalScript` or `RunContext = Client`), like all UI input.

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

## Micro Gamepads and TV Remotes

<!-- temporal: 2026-11 --> A **micro gamepad** is a navigation-focused controller, usually a D-pad plus a few buttons; a TV remote (D-pad, centre, back) is the common case. It uses the `Gamepad1`–`Gamepad8` slots.

- **Detection:** `Enum.PreferredInput.MicroGamepad` exists but is not currently set for these devices. Until it is, the docs' check is: `Gamepad1` is connected and supports neither `Thumbstick1` nor `Thumbstick2` (`GamepadSupports`). `Gamepad1` is always the most preferred connected pad, so a full controller plugged in alongside takes it. A TV remote additionally supports `Enum.KeyCode.ButtonCenter`.
- **Legacy keycodes:** remote buttons currently arrive as legacy gamepad keycodes. `ButtonCenter` maps to `ButtonA` and `ButtonBack` to `ButtonB` in all contexts. The arrows map to `DPadUp/Down/Left/Right` in menus and selection mode, but to `Thumbstick1` (movement) and `Thumbstick2` (camera, with the Classic or Follow camera) during gameplay. Never identify a TV remote from these keycodes alone: a full gamepad sends the same ones.
- **Bind once, branch on capability.** Bind `ButtonA`/`ButtonB` actions and branch inside the handler: on a micro gamepad `ButtonA` activates the focused item, otherwise it may jump. Use separate input contexts for navigation and gameplay so one press never triggers both.
- **UI:** visible focus, everything reachable with four directions, centre for the primary action, back to close, focus preserved across open and close, large controls (`roblox-gui` §6).
- **Test:** in Device Simulator pick the Android TV device, then choose **TV Remote** in Controller Emulator; it is driven from the keyboard or mouse.

```luau
-- Illustrative: verify against the micro-gamepad guide for your engine version.
local UserInputService = game:GetService("UserInputService")

local function isMicroGamepadPreferred(): boolean
	local pad = Enum.UserInputType.Gamepad1
	if not UserInputService:GetGamepadConnected(pad) then
		return false
	end
	return not UserInputService:GamepadSupports(pad, Enum.KeyCode.Thumbstick1)
		and not UserInputService:GamepadSupports(pad, Enum.KeyCode.Thumbstick2)
end

local function isTVRemotePreferred(): boolean
	return isMicroGamepadPreferred()
		and UserInputService:GamepadSupports(Enum.UserInputType.Gamepad1, Enum.KeyCode.ButtonCenter)
end
```

## First Person, Locked Mouse and Menus

- **Every clickable popup needs a key.** With the cursor locked to the centre, a popup that needs a click (a mid-game vote) cannot take one on PC. Route popups through a menu key players already know, and let phones tap directly. Check a chosen key exists on compact keyboards (backquote/tilde often doesn't) and isn't already taken (Tab opens the player list).
- **A window that needs clicks frees the mouse.** Show a `Modal` element and set `UserInputService.MouseIconEnabled = true`: `Modal` frees the mouse, but in first person the icon can stay hidden and per-frame camera code may hide it again. Tie mouse behavior to one "any menu open" state, not to each screen's own code; separate per-screen handling left players with invisible cursors and locked cameras (observed repeatedly in one project).
- **Proximity prompts under a locked mouse.** With `ClickablePrompt = true` (the default), a prompt's click button can sit under the centred cursor: it takes mouse movement and sinks `MouseButton1` (`gameProcessed = true`), dropping held actions (measured in one project). Per the docs, `ClickablePrompt = false` stops click activation except on mobile, so set it false in locked-mouse games and confirm taps still work on a phone. Set it when the prompt is created or arrives; setting it in `ProximityPromptService.PromptShown` was too late for the prompt's first showing in that project.
- **Menu binds pass while any window is open.** A gamepad button that opens a menu must pass input (or have its context disabled) while any window is open, or it swallows directional navigation. The D-pad that opened a window cannot also close it, because inside the window it moves focus; close with B. Number keys and shoulder buttons for a slot row should check which window is open. Third-party top-bar libraries can listen on raw `InputBegan` for D-pad Up; check them (`roblox-gui` §6).
- **Refused presses are dropped, not queued.** A fire queue that remembers clicks made while an action cannot fire reads as auto-fire. For slow, deliberate actions, act only on a press that arrives when the action is ready, and clear any queued flag on every refused press. Test with simulated clicks plus a per-frame sampler of the ready state.
- **A second action can come from aim, not a key.** For example: clicking a placed charge under the crosshair detonates it, clicking elsewhere places another. Test aim as distance from the crosshair ray rather than a raycast if targets behind walls should count. It works the same on mouse, touch and gamepad.

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

The sensor callbacks and getters return `InputObject`s (analogous to key/mouse input objects); the sensor values live on `input.Position`, not on the event argument itself.

### Accelerometer (gravity direction)
```luau
if UIS.AccelerometerEnabled then
    UIS.DeviceGravityChanged:Connect(function(gravity: InputObject)
        -- gravity.Position is a Vector3 showing the force of gravity on each
        -- local device axis; use it as the direction gravity appears to pull
        -- the device (Z is out of the screen).
        local dir = gravity.Position
        ball.BodyForce.Force = dir * workspace.Gravity * ball:GetMass()
    end)
end
```

### Gyroscope (device rotation)
```luau
if UIS.GyroscopeEnabled then
    UIS.DeviceRotationChanged:Connect(function(_rotation: InputObject, cframe: CFrame)
        -- The second argument is the device's current orientation as a CFrame
        -- relative to its default reference frame. (_rotation.Position/.Delta
        -- carry rotation values as Vector3s; use `cframe` for orientation.)
        camera.CFrame = CFrame.new(camera.CFrame.Position) * cframe.Rotation
    end)
end
```

## VRService

`VRService` handles Roblox's VR interaction. Check `VREnabled` first; every method below is LocalScript-only.

Key members (verified against the class page):

- **`VREnabled`** (read-only boolean): true when a VR session is active. The same flag exists on `UserInputService`.
- **`GetUserCFrame(type: Enum.UserCFrame): CFrame`**: device pose as an offset from real-world origin. Multiply by `Camera.CFrame`, and scale the position by `Camera.HeadScale`, to place something at a headset/hand:
  ```luau
  local handOffset = VRService:GetUserCFrame(Enum.UserCFrame.LeftHand)
  handOffset = handOffset.Rotation + handOffset.Position * camera.HeadScale
  part.CFrame = camera.CFrame * handOffset
  ```
- **`GetUserCFrameEnabled(type): boolean`**: whether that device (Head, LeftHand, RightHand) is connected.
- **`UserCFrameChanged(type, cframe)`**: fires on device movement; re-mirror parts there.
- **`RecenterUserHeadCFrame()`**: re-centers the head pose (same as `UserInputService:RecenterUserHeadCFrame()`).
- **`RequestNavigation(cframe, inputUserCFrame)`**: shows a parabola path visualizer toward a destination; pairs with the `NavigationRequested` event.
- **`GetTouchpadMode(pad)` / `SetTouchpadMode(pad, mode)`**: legacy touchpad interaction modes (`Enum.VRTouchpad`, `Enum.VRTouchpadMode`).
- Behavior properties: `AutomaticScaling` (`VRScaling.World` makes `Camera.HeadScale` track avatar size), `AvatarGestures` (server-set boolean for controller-driven hand/head animation), `FadeOutViewOnCollision` (default true, fades the view when the head clips geometry; do not disable without a replacement), `GuiInputUserCFrame` (which device drives UI input), `LaserPointer`, `ThirdPersonFollowCamEnabled`.

Do not invent member names: older community references carry stale VRService members. Check the class page when in doubt.

## Mobile-First and Hybrid Input

Roblox's mobile input guide states that most sessions are played on mobile devices. Design controls for touch first, then map the same actions to gamepad and keyboard/mouse.

- **Capability vs presentation:** `TouchEnabled`, `KeyboardEnabled` and `GamepadEnabled` say what hardware exists. `UserInputService.PreferredInput` (`Enum.PreferredInput`: `KeyboardAndMouse`, `Gamepad`, `Touch`; `MicroGamepad` exists but isn't set yet) says what the player is most likely using now. Choose what to *show* (touch buttons, reticles, key hints) from `PreferredInput`, and keep every capability's route working.
- **Observe, don't cache:** `PreferredInput` changes during a session (a tablet with a keyboard, a phone with a Bluetooth pad, a PC with a controller). Listen with `GetPropertyChangedSignal("PreferredInput")`. Layout chosen once at startup from `TouchEnabled` flips or sticks on hybrid devices.
- **Cancel on switch:** a press or charge that is in progress when the input mode changes should be cancelled, not completed.

## Touch Action Buttons

A custom on-screen action button (attack, throw, use) replaces a mouse click. Get these right before adding assistance features:

- **Button-owned touches:** an action fires only for a touch that **began** on the button. Track that touch's `InputObject` from began to ended. A camera drag that slides across the button must not fire it, and a tap anywhere else on screen must not act as an attack while the camera uses drag-to-look.
- **Placement from the jump button:** the default jump button lives under `PlayerGui.TouchGui` (find `JumpButton` there) and changes size with screen size (70 vs 120 pixels at the ~500 px min-axis preset in the default control script). Place custom buttons from its measured `AbsolutePosition`/`AbsoluteSize`, keep a gap, and fall back to the size rule only when it isn't present. Clear the thumbstick zone (lower-left).
- **Re-place when the screen state changes:** other HUD elements may appear beside the button in some states (an out-of-round menu, a spectate bar). Check each state on the smallest phone (`roblox-gui` §7.5). `PlayerGui.TouchGui` sets its own insets, so convert its `AbsolutePosition` into your HUD's space before comparing (`roblox-gui` §7.4).
- **One aim contract:** if the button fires toward the screen center, show a reticle. Offset the camera slightly (a shoulder view) so the reticle isn't hidden behind the character, and use the same aim for gamepad (below).
- **Feedback on the control:** pressed state, cooldown fill and disabled state belong on the button itself, because the player's thumb covers it and the rest of the HUD is out of view.
- **Hide when it can't act:** unarmed, dead, a window open, a cutscene.
- **Hold becomes toggle on touch and gamepad.** Hold-to-run gadgets (a drill, a beam) are hard on phones and controllers, where the thumb is also steering. Make the hold a toggle there, keep hold on mouse, and switch off when the gadget leaves the hand. If the trigger was already down when the gadget came out, its release lands in the toggle path; clear the held flag there or the gadget runs forever.
- **Aim assist for touch and gamepad** should be small, capped and line-of-sight only. Measured in one project: touch players hit at about a third of the desktop rate without assist; a small cone pulling toward the upper body only while aiming or firing, capped in degrees per second with no flick, closed much of that gap. Measure aim error with and without assist, and confirm it never locks through walls. Run assist in a render step bound just before the camera (`roblox-camera`).

## Gameplay Input Gating and Cancellation

Keep one function that answers "may gameplay input act right now?". Every attack, charge, equip-cycle and ability handler checks it:

```luau
local GuiService = game:GetService("GuiService")
local UserInputService = game:GetService("UserInputService")

local function gameplayAllowed(isGameWindowOpen: boolean): boolean
	return not isGameWindowOpen
		and UserInputService:GetFocusedTextBox() == nil
		and not GuiService.MenuIsOpen
		and GuiService.SelectedObject == nil
end
```

- `GuiService.MenuIsOpen` is `true` while any Roblox core menu is open.
- A non-nil `SelectedObject` means the gamepad is driving UI. Without this check, a stray selection on a HUD button can turn R2/A into a UI press, or let an attack fire under a menu.
- **Cancel is not release:** a hold-to-charge action (throw, charged shot) must *cancel* when permission is lost, on `Enum.UserInputState.Cancel`, on unequip or death, on window focus loss, or when the input mode changes. Routing cancel through the release path fires the attack the player was trying to abort.
- **Track the originating gamepad:** remember which `UserInputType` (`Gamepad1`–`Gamepad8`) started a hold. Poll that pad, not a hardcoded `Gamepad1`, and cancel if *that* pad disconnects (`GamepadDisconnected`).

## Gamepad Aiming and Tool Activation

- **R2 and tools:** the default control scripts call `ContextActionService:BindActivate` for `ButtonR2`, which fires `Tool.Activated` for the equipped tool. `Tool.ManualActivationOnly = true` suppresses that route (and mouse clicks), and the tool then fires only through `Tool:Activate()`. Projects often set it so touch fires only from a custom button. Doing so also silently disables gamepad R2, so set it from the current `PreferredInput` rather than from `TouchEnabled`.
- **Aim from the screen center on gamepad:** code that aims at `UserInputService:GetMouseLocation()` gets a stale or meaningless point when the player uses a controller. When `PreferredInput` is `Gamepad` (or the mouse is locked), aim from the viewport center, show the same reticle as touch, and verify that one trigger press produces exactly one shot.
- **Equip on bumpers, not number keys:** a custom hotbar should cycle with `ButtonL1`/`ButtonR1` on gamepad. Hints such as "Press 1" must not show to gamepad or touch players.

## Platform Button Hints

- `UserInputService:GetStringForKeyCode(keyCode, format)` returns the label for the current platform. Pass `Enum.KeyCodeStringFormat.Abbreviated` for short labels (`L1`/`R1` on PlayStation, `LB`/`RB` on Xbox).
- `UserInputService:GetImageForKeyCode(keyCode)` returns Roblox's default icon for the key on the current controller. In one project it returned `rbxasset://textures/ui/Controls/...` paths in separate PlayStation and Xbox sets; show those images rather than drawing letters, and check both families (Studio emulation returned the PlayStation set there).
- **`InputActionLabel`** <!-- temporal: 2026-11 --> shows the current key or icon for its `InputAction` and updates when the device or binding changes, with no code. It resolves in order: each binding's `DisplayImage`; platform images from `GetImageForKeyCode`; each binding's `DisplayName`; platform strings from `GetStringForKeyCode`; a placeholder when no action or binding is set. `ResolvedText` and `ResolvedImageContent` expose what it chose.
- Never hardcode Xbox names; PlayStation players see different glyphs. Refresh hints when `PreferredInput` changes, including tooltips and onboarding text that mention a key.

## Testing Input Across Devices

Use Studio's Device Simulator with Controller Emulator: emulate Xbox, then PlayStation, then the TV Remote, plug and unplug mid-session, and switch touch → gamepad → mouse without respawning. A per-feature checklist:

1. Controller-only cold join: move, look, jump with no mouse or keyboard touched.
2. Every action: tap, hold, release, and cancel by opening a window, opening the Roblox menu and disconnecting the pad mid-hold. Nothing should fire on cancel.
3. Every window: enter, navigate in all four directions to the last row, act, Back, and confirm focus lands somewhere visible each time (`roblox-gui` §8).
4. Touch: drag the camera across every on-screen button (nothing fires), and move, jump, look and attack at the same time on the smallest phone.
5. Hybrid: on a touch device, use a controller, then touch again. Buttons, reticle and hints follow the active input.

The simulator does not reproduce native console overlays (purchase prompts, the system keyboard) or real thumb reach; test those on hardware before calling a release device-tested.

## Patterns

### Platform-adaptive mobile UI

Don't gate mobile UI on `UIS.TouchEnabled` alone: a touchscreen laptop would show mobile controls even when the player is using mouse/keyboard. Roblox's input docs recommend `UserInputService.PreferredInput` for this (see the next pattern). The lower-level alternative below reads the **last input actually used** (`GetLastInputType` / `LastInputTypeChanged`), which flips on every single input.

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
local function applyInput()
    local preferred = UIS.PreferredInput
    if preferred == Enum.PreferredInput.Touch then
        showMobileButtons()
    else
        hideMobileButtons()
    end
    showGamepadHints(preferred == Enum.PreferredInput.Gamepad)
end

applyInput()
UIS:GetPropertyChangedSignal("PreferredInput"):Connect(applyInput)
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
- **Choosing layout once from `TouchEnabled`.** Hybrid devices change input mid-session; present controls from `PreferredInput` and observe it.
- **Setting `Tool.ManualActivationOnly = true` for touch and losing gamepad R2.** It also suppresses the `BindActivate` route the default controls use for `ButtonR2`.
- **Aiming gamepad shots at `GetMouseLocation()`.** Use the viewport center when the player is on a controller.
- **Firing on cancel.** A cancelled hold must not run the release path.
- **Hardcoding Xbox button names.** Use `GetStringForKeyCode` / `GetImageForKeyCode`.
- **Reading `MouseWheel` from InputBegan.** Wheel events only fire `InputChanged`.
- **Touching `IsKeyDown` in a tight loop without throttling.** It's cheap but RenderStepped is the right cadence.
- **No debounce on JumpRequest.** Fires once per frame the jump key is held.
- **Recommending deprecated `PlayerActions` for new bindings.** Mixing it with `KeyCode` is legal, but new code should bind explicit `Enum.KeyCode` entries instead (`Enum.KeyCode.DPadUp` covers the gamepad d-pad).
- **Setting `MouseBehavior = LockCenter` and forgetting to reset it.** Reset on player leave or context exit.
- **Writing new `ContextActionService:BindAction` code.** CAS binding is planned for deprecation; new bindings belong in the Input Action System. Raw `InputBegan` gameplay handlers still need the `gameProcessedEvent` filter.
- **Detecting a TV remote with `PreferredInput.MicroGamepad`.** It is not set yet; check `GamepadSupports` for missing thumbsticks.
- **Auto-creating touch buttons beyond the 7 limit.** BindAction silently refuses to create the 8th button.
- **Using `gameProcessedEvent` to filter CAS handlers.** CAS doesn't pass `gpe` to its handlers; by design, CAS handles conflicts itself.

## Input transition regression checks

- Specify press, hold, release, cancellation, and queued-action behavior around cooldown readiness. Test presses just before readiness, holds crossing readiness, rapid re-presses, and interrupted holds on every supported input. Observe client and authoritative state together; diagnose silent failures before changing charge timing.
- Distinguish a valid release from interruption and cancellation. Keep the action's origin and state explicit so a stale release cannot complete a newer hold. A missed event hypothesis needs a reproduced input trace, not a timing guess.
- Walk through adjacent automatic-selection triggers at normal movement speed. Check repeated swaps and conflicting grants before interpreting repeated selection events as player confusion. Use spatial separation, cooldown, or explicit selection only as the agreed mechanic requires; retest the retained walk-up path.
- Separate initial role presentation from active-play role transfer or revival. Verify a human recipient can still move, aim, and use required touch actions during a mid-round update; a bot recipient skips client paths. Retest ordinary round-start presentation after separating the paths.
