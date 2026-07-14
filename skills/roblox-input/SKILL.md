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
  - https://create.roblox.com/docs/projects/server-authority
  - https://create.roblox.com/docs/input/input-action-system
  - https://raw.githubusercontent.com/Roblox/focus-navigation/main/README.md
---

## When to Load

Load for keyboard, mouse, gamepad, touch, motion, or cross-platform action binding. Client-side only. For simulation-affecting input in a Server Authority project, use the Input Action System rather than traditional input events.

## Quick Reference

**Core events** (`UserInputService`): `InputBegan`, `InputChanged`, `InputEnded` fire as `(input: InputObject, gameProcessedEvent: boolean)`. `InputBegan` does NOT fire for mouse wheel. Events only fire while the client window is focused.

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

**Server Authority:** use `InputAction`/`InputContext` for inputs that affect the core simulation, store the input state where the synchronized simulation can read it, and process it through `RunService:BindToSimulation()`. `ContextActionService` remains appropriate for UI-only or classic-project actions.

**Gamepad UI focus:** separate gameplay bindings from menu selection. Set `GuiService.SelectedObject`, mark controls `Selectable`, and test nested/modal navigation.

**Gamepad:** use `GetConnectedGamepads()` and listen to connection changes.

**Touch:** use high-level gesture events or raw `TouchStarted`/`TouchMoved`/`TouchEnded` when tracking fingers.

**Pitfalls**:
- `gameProcessedEvent=true` in InputBegan → UI consumed it. Filter for gameplay.
- `BindAction` is stack-based: most-recent wins. Use `BindActionAtPriority`.
- Client-only. Server scripts silently no-op.
- `JumpRequest` fires multiple times per jump — debounce.
- Mouse wheel only fires `InputChanged`.

Full event tables and polling methods: `references/full.md`.
