---
name: roblox-input
description: "Use when handling Roblox keyboard, mouse, gamepad, touch, motion input, or cross-platform action binding."
last_reviewed: 2026-07-13
sources:
  - https://create.roblox.com/docs/reference/engine/classes/UserInputService
  - https://create.roblox.com/docs/reference/engine/classes/ContextActionService
  - https://create.roblox.com/docs/reference/engine/enums/UserInputType
  - https://create.roblox.com/docs/reference/engine/classes/GuiService
  - https://create.roblox.com/docs/reference/engine/classes/GuiObject
  - https://raw.githubusercontent.com/Roblox/focus-navigation/main/README.md
---

## When to Load

Load for keyboard, mouse, gamepad, touch, motion, or cross-platform action binding. Client-side only.

## Quick Reference

**Core events** (`UserInputService`): `InputBegan`, `InputChanged`, `InputEnded` fire as `(input: InputObject, gameProcessedEvent: boolean)`. `InputBegan` does NOT fire for mouse wheel. Events only fire while the client window is focused.

**Platform detection** (cache at startup): `KeyboardEnabled`, `MouseEnabled`, `TouchEnabled`, `GamepadEnabled`, `AccelerometerEnabled`, `GyroscopeEnabled`, `VREnabled`, `PreferredInput` (the device the player is currently using most).

**Polling queries** (cheaper than events for held-state):

```luau
UIS:IsKeyDown(Enum.KeyCode.W)
UIS:IsMouseButtonPressed(Enum.UserInputType.MouseButton1)
UIS:IsGamepadButtonDown(Enum.UserInputType.Gamepad1, Enum.KeyCode.ButtonA)
local dx, dy = UIS:GetMouseDelta()
```

**Prefer `ContextActionService` over `InputBegan`** for gameplay — free conflict resolution (chat won't steal H) and free mobile buttons:

```luau
local CAS = game:GetService("ContextActionService")

local function onAction(name, state, _input)
    if name == "Jump" and state == Enum.UserInputState.Begin then
        humanoid.Jump = true
    end
end

CAS:BindAction("Jump", onAction, true,
    Enum.KeyCode.Space, Enum.KeyCode.ButtonA)
```

`BindAction(name, handler, createTouchButton, ...inputTypes)`. Handler returns `ContextActionResult.Sink` to consume, `.Pass` to fall through.

**Gamepad UI focus:** gameplay bindings and menu selection are separate. Set `GuiService.SelectedObject`, mark controls `Selectable`, and test nested/modal navigation. Use Focus Navigation only when native selection is insufficient.

**Gamepad**: `GetConnectedGamepads()` → `Gamepad1`..`Gamepad8`. Listen to `GamepadConnected`/`Disconnected`.

**Touch gestures**: `TouchTap`, `TouchPan`, `TouchPinch`, `TouchRotate`, `TouchSwipe`, `TouchLongPress`, `TouchDrag`. Raw: `TouchStarted`/`TouchMoved`/`TouchEnded`.

**Pitfalls**:
- `gameProcessedEvent=true` in InputBegan → UI consumed it. Filter for gameplay.
- `BindAction` is stack-based: most-recent wins. Use `BindActionAtPriority`.
- Client-only. Server scripts silently no-op.
- `JumpRequest` fires multiple times per jump — debounce.
- Mouse wheel only fires `InputChanged`.

Full event tables: `references/full.md`.
