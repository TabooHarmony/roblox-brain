---
name: roblox-gui-fusion
description: Fusion 0.3 game UI - shop, inventory, settings screens. Reactive declarative patterns for Roblox.
last_reviewed: 2026-05-24
---

<!-- Source patterns: VirtualButFake/fusion-components (MIT), dphfox/Fusion docs -->

# Roblox GUI with Fusion

## Quick Reference

**Framework:** Fusion 0.3 (dphfox/Fusion, MIT). Vendored at `.opencode/vendor/fusion/`.

**Require path:** The AI must resolve the Fusion require path based on the project:
- If `Packages/Fusion` exists (Wally) → `require(ReplicatedStorage.Packages.Fusion)`
- If `.opencode/vendor/fusion` exists (this plugin) → `require(ReplicatedStorage[".opencode"].vendor.fusion)` or wherever the project root maps in the DataModel
- If Fusion is elsewhere → match the existing require pattern in the project

**When to use this skill:**
- Building new game UI screens from scratch (shop, inventory, settings, etc.)
- Any UI with dynamic state (item lists, toggles, selections, animations)

**When NOT to use this skill:**
- Project already has established UI patterns (raw Instance, Roact, Vide) → follow existing patterns instead
- Simple static HUD with no state → use raw Instance (see `roblox-gui` skill)

**Routing logic for the AI:**
- If the project has existing Fusion code → match its patterns, use these references for architecture only
- If the project has existing non-Fusion UI → do NOT introduce Fusion, follow what's there
- If the project has no UI yet (greenfield) → use these references as starting templates, adapt colors/data

**Key design rules (framework-agnostic, always apply):**
- Mobile-first: design for phone, scale up. Touch targets minimum 48x48px.
- Scale (0-1 proportional) for position/size. Offset only for fixed padding/icons.
- Container Frame Rule: every logical group gets a Frame with layout modifier inside.
- UIListLayout/UIGridLayout for auto-arrangement. AutomaticSize on parent.
- ScreenGui.ResetOnSpawn = false for persistent UI. IgnoreGuiInset = true for fullscreen.
- Dark palette: off-white text on dark gray (never pure white on pure black).
- Never use absolute pixel sizes for main containers. UISizeConstraint for min/max bounds.
- ScrollingFrame: AutomaticCanvasSize. UIListLayout inside for content.

---

## Fusion 0.3 Patterns

### Core idioms

```luau
local Fusion = require(path.to.Fusion)
local scoped = Fusion.scoped
local peek = Fusion.peek
local Children = Fusion.Children
local OnEvent = Fusion.OnEvent

-- Create a scope (manages cleanup of all objects created within it)
local scope = scoped(Fusion)

-- Reactive state
local count = scope:Value(0)

-- Derived state (re-computes when dependencies change)
local label = scope:Computed(function(use)
    return "Count: " .. use(count)
end)

-- Create instances (reactive properties auto-update)
local gui = scope:New "ScreenGui" {
    Parent = playerGui,
    [Children] = {
        scope:New "TextLabel" {
            Text = label,
            Size = UDim2.fromOffset(200, 50),
        },
    },
}

-- Animate any value
local smoothPos = scope:Spring(position, 25) -- speed 25

-- Read without subscribing (in callbacks)
local currentCount = peek(count)

-- Cleanup everything in the scope
scope:doCleanup()
```

### Component pattern

```luau
local function Button(scope: Fusion.Scope, props: {
    Text: Fusion.UsedAs<string>,
    OnClick: () -> (),
    Color: Fusion.UsedAs<Color3>?,
})
    local isHovering = scope:Value(false)

    return scope:New "TextButton" {
        Text = props.Text,
        BackgroundColor3 = scope:Spring(scope:Computed(function(use)
            local base = if props.Color then use(props.Color) else Color3.fromRGB(80, 140, 255)
            return if use(isHovering) then base:Lerp(Color3.new(1,1,1), 0.1) else base
        end), 25),
        [OnEvent "Activated"] = props.OnClick,
        [OnEvent "MouseEnter"] = function() isHovering:set(true) end,
        [OnEvent "MouseLeave"] = function() isHovering:set(false) end,
        [Children] = { scope:New "UICorner" { CornerRadius = UDim.new(0, 6) } },
    }
end
```

### List rendering (ForPairs)

```luau
-- Renders a UI element for each item. Automatically adds/removes as data changes.
scope:ForPairs(items, function(use, itemScope, index, item)
    return index, itemScope:New "TextLabel" {
        Text = item.Name,
        LayoutOrder = index,
    }
end)
```

---

## References

Full production-quality screen implementations are in `references/`:

- **shop.luau** - Item grid, currency header, purchase confirmation modal, server-validated buy flow
- **inventory.luau** - Owned items grid with rarity borders, equip/unequip, detail panel, empty slots
- **settings-menu.luau** - Tabbed sections, sliders with drag, toggle switches, dropdown selects

Each reference is self-contained and demonstrates:
- Scope-based memory management
- Component composition (small functions returning instances)
- Reactive state driving UI updates
- Spring animations for smooth transitions
- ForPairs for dynamic lists
- Modal/overlay patterns
- Typed props for clear interfaces

---

## Sources

- Fusion: github.com/dphfox/Fusion (MIT, 764★)
- Fusion docs: elttob.uk/Fusion/latest
- Component patterns: VirtualButFake/fusion-components (MIT, 31 components)
- Fusion 0.3 release notes: github.com/dphfox/Fusion/releases/tag/v0.3-beta
