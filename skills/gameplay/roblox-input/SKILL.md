---
name: roblox-input
description: "Use when handling Roblox touch, gamepad, keyboard, mouse or motion input, on-screen action buttons, or cross-platform action binding."
when_to_use: "Also when a button fires by accident, controls don't work on mobile or console, a controller gets stuck in a menu, or button prompts show the wrong key."
last_reviewed: 2026-11-27
sources:
  - https://devforum.roblox.com/t/the-correct-way-to-design-mobile-buttons/2494558
  - https://create.roblox.com/docs/reference/engine/classes/UserInputService
  - https://create.roblox.com/docs/reference/engine/enums/PreferredInput
  - https://create.roblox.com/docs/input/mobile
  - https://create.roblox.com/docs/production/publishing/console-guidelines
  - https://create.roblox.com/docs/reference/engine/classes/ContextActionService
  - https://create.roblox.com/docs/reference/engine/classes/Tool
  - https://create.roblox.com/docs/studio/controller-emulator
  - https://create.roblox.com/docs/input/input-action-system
  - https://create.roblox.com/docs/input/micro-gamepad
  - https://create.roblox.com/docs/reference/engine/classes/InputActionLabel
  - https://create.roblox.com/docs/reference/engine/classes/ProximityPrompt
  - original
  - https://create.roblox.com/docs/projects/server-authority
  - https://create.roblox.com/docs/ui/3D-drag-detectors
  - https://create.roblox.com/docs/ui/ui-drag-detectors
---

# Roblox Input

## When to Load

Touch, gamepad, keyboard, mouse or motion input, on-screen action buttons, cross-platform binding. Client-only; Server Authority simulation input uses the Input Action System.

## Quick Reference

- **Events:** `InputBegan/Changed/Ended` give `(input, gameProcessedEvent)`; filter it for gameplay. Wheel fires only `InputChanged`.
- **Bindings:** new work uses the Input Action System (`InputContext` > `InputAction` > `InputBinding`); CAS `BindAction` is planned for deprecation, so migrate when touched. Server Authority: `RunService:BindToSimulation()`.
- **Hybrid aware:** show controls from `UserInputService.PreferredInput`, observed live, not `TouchEnabled` cached once.
- **Touch buttons:** fire only for touches that began on the button. Place from the measured jump button in `PlayerGui.TouchGui`.
- **Gate gameplay:** block attacks while a game window is open, a `TextBox` is focused, `GuiService.MenuIsOpen`, or `GuiService.SelectedObject` is set.
- **Cancel is not release:** holds cancel on window open, `Cancel`, unequip, focus loss, input switch or pad disconnect.
- **Gamepad tools:** R2 activates tools; `Tool.ManualActivationOnly = true` disables it. Aim from screen center, not `GetMouseLocation()`.
- **Hints:** `InputActionLabel`, `GetStringForKeyCode(key, Abbreviated)`, `GetImageForKeyCode`; never hardcode Xbox names.
- **TV remote:** D-pad, centre (`ButtonA`), back (`ButtonB`); `PreferredInput.MicroGamepad` isn't set yet, so detect a pad without thumbsticks.
- **Locked mouse:** popups need a key; click windows show `Modal` + `MouseIconEnabled`; `ClickablePrompt = false`.
- **Test:** Device Simulator + Controller Emulator; focus: `roblox-gui`.

> Details: [references/full.md](references/full.md)
