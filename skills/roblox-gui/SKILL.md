---
name: roblox-gui
description: GUI systems, layout, responsiveness, cross-platform UI. ScreenGuis, UIListLayout, constraint-based design.
last_reviewed: 2026-05-22
---

<!-- Source: brockmartin/roblox-game-skill (MIT) -->

# Roblox GUI/UI Systems Reference

## 1. Overview

Load this reference when working on any UI-related task in Roblox:

- Building menus (main menu, pause menu, settings)
- HUDs (health bars, minimaps, ammo counters, score displays)
- Shops and inventory screens
- Notification and toast systems
- Dialog and popup windows
- Any 2D or 3D-attached interface elements

All GUI code runs on the **client** (LocalScripts). UI objects live under `StarterGui` at edit time and are cloned into each player's `PlayerGui` at runtime.

---

## Quick Reference

**Load Full Reference below only when you need specific layout examples or implementation patterns.**

Key rules:
- Mobile-first: design for phone, scale up. Touch targets minimum 48x48px.
- Scale (0-1 proportional) for position/size. Offset only for fixed padding/icons.
- Container Frame Rule: every logical group gets a Frame with layout modifier inside.
- UIListLayout/UIGridLayout: set on parent Frame, children auto-arrange. AutomaticSize on parent.
- ScreenGui.ResetOnSpawn = false for persistent UI. IgnoreGuiInset = true for fullscreen.
- ZIndex for layering within same ScreenGui. DisplayOrder for ScreenGui priority.
- Never use absolute pixel sizes for main containers. UISizeConstraint for min/max bounds.
- ScrollingFrame: set CanvasSize or AutomaticCanvasSize. UIListLayout inside for content.
- Common AI mistake: forgetting to set LayoutOrder on children when using layout modifiers.
- For complex stateful UI (shops, inventories, settings), consider reactive frameworks like Fusion (dphfox/Fusion, MIT) or React-Lua (jsdotlua/react).

---

## Full Reference

## Design Guidelines

<!-- Guidelines sourced from Roblox DevForum, official docs, and community standards -->

### Container Frame Rule
<!-- Source: epochzx, Roblox DevForum -->

**Never place UI elements directly under a ScreenGui.** Always create a transparent Container Frame as the first child with `Size = {1,0},{1,0}` and `BackgroundTransparency = 1`. Its `AbsoluteSize` always matches screen resolution.

```luau
local container = Instance.new("Frame")
container.Name = "Container"
container.Size = UDim2.new(1, 0, 1, 0)
container.BackgroundTransparency = 1
container.BorderSizePixel = 0
container.Parent = screenGui
-- All UI children go under container, not directly under screenGui
```

### Scale vs Offset
<!-- Source: uiuxartist (Roblox Staff), DevForum -->

- **Scale** = percentage of parent (responsive). Use for Size and Position.
- **Offset** = fixed pixels. Use for pixel-perfect icons, small graphics, UIStroke.
- **UIStroke** does NOT support Scale - only Offset.
- **UICorner** DOES support Scale (`UDim.new(0.5, 0)` = 50% radius).
- **Hybrid pattern**: start pure Scale, add Offset for minimum size, reduce Scale.

```luau
-- Scale for responsive sizing
frame.Size = UDim2.new(0.5, 0, 0, 40)  -- 50% width, 40px height

-- Offset for UIStroke (Scale not supported)
stroke.Thickness = 2  -- always Offset

-- UICorner supports Scale
corner.CornerRadius = UDim.new(0, 8)    -- Offset
corner.CornerRadius = UDim.new(0.5, 0)  -- Scale (50% of smallest axis)
```

### Mobile-First Principles
<!-- Source: Roblox official docs - Adaptive Design Guidelines -->
<!-- https://create.roblox.com/docs/production/publishing/adaptive-design -->

- **50%+ of Roblox players are on mobile.** Design touch-first.
- Minimum touch target: **~0.15 width scale** (≈44-48px).
- Account for notches via `ScreenGui.ScreenInsets`.
- Don't place UI in the top 58px (Roblox top bar) or bottom virtual controls.
- **Test with Device Emulator** before publishing (View → Device Emulator).

### Typography
<!-- Source: PictureFolder, Roblox DevForum (119 likes) -->
<!-- "Designing UI - Tips and Best Practices" -->

- **Two fonts max**: Display (headers/buttons) + Body (descriptions).
- **Gotham** is the de facto modern Roblox font.
- **NEVER** pure white (`#FFFFFF`) on pure black (`#000000`). Use off-white (`#F0F0F0`) on dark gray (`#1E1E1E`).
- **Size hierarchy**: bigger/bolder = more important.

### Color
<!-- Source: DevForum "Modern UI Colour Schemes" -->

- Dark palette: `20,20,20` (Modern Black) to `35,35,35` (Very Light). Don't go lighter than 35.
- Grey base + accent colors for interactive elements.
- **Pick a palette and stick to it.** Consistency > variety.

### Common AI UI Mistakes

| Mistake | Fix |
|---------|-----|
| Elements directly under ScreenGui | Use a Container Frame child |
| Pure Scale only | Too small on mobile - add Offset minimums |
| Pure Offset only | Breaks on different resolutions |
| Pure white on pure black text | Use off-white on dark gray |
| Ignoring mobile players | 50%+ are mobile; design touch-first |
| Text-heavy UI for young audiences | Use icons, images, minimal text |
| UI overlapping top bar / chat / leaderboard | Respect safe areas (top 58px, bottom 100px) |
| Not testing with Device Emulator | Always test before publishing |

---

## 2. GUI Hierarchy

### ScreenGui (2D Overlay)

The primary container for all 2D UI. Placed in `StarterGui`; Roblox copies it into each player's `PlayerGui` on spawn.

```luau
local Players = game:GetService("Players")
local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "MainHUD"
screenGui.ResetOnSpawn = false -- survives respawn
screenGui.DisplayOrder = 10   -- higher renders on top
screenGui.IgnoreGuiInset = true -- extends behind top bar
screenGui.Parent = playerGui
```

**Key Properties:**

| Property | Purpose |
|---|---|
| `DisplayOrder` | Controls layering. Higher values render on top of lower values. |
| `ResetOnSpawn` | `true` (default): destroyed and re-cloned on respawn. Set to `false` for persistent UI (shops, settings). |
| `IgnoreGuiInset` | `true`: UI extends behind the top bar (CoreGui area). Use for fullscreen overlays. |
| `Enabled` | Toggle visibility without destroying. |

### SurfaceGui (On Part Surfaces)

Renders UI on a Part's surface. Used for in-world signs, screens, control panels.

```luau
local surfaceGui = Instance.new("SurfaceGui")
surfaceGui.Face = Enum.NormalId.Front
surfaceGui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
surfaceGui.PixelsPerStud = 50
surfaceGui.Parent = workspace.SignPart
-- Also set surfaceGui.Adornee = workspace.SignPart if parented elsewhere
```

### BillboardGui (Floating in 3D)

Always faces the camera. Used for nametags, damage numbers, quest markers.

```luau
local billboardGui = Instance.new("BillboardGui")
billboardGui.Size = UDim2.new(0, 200, 0, 50)
billboardGui.StudsOffset = Vector3.new(0, 3, 0) -- above the part
billboardGui.AlwaysOnTop = false -- occluded by 3D geometry
billboardGui.MaxDistance = 100   -- hides beyond this range
billboardGui.Adornee = workspace.NPC.Head
billboardGui.Parent = workspace.NPC.Head
```

### Display Order Hierarchy

```
DisplayOrder 100  -- Modal dialogs (on top of everything)
DisplayOrder 50   -- Notifications / toasts
DisplayOrder 10   -- HUD elements
DisplayOrder 1    -- Background UI
```

---

## 3. Core UI Elements

### Frame

Container for grouping and styling. No text or image by default.

```luau
local frame = Instance.new("Frame")
frame.Size = UDim2.new(0.3, 0, 0.4, 0)         -- 30% width, 40% height
frame.Position = UDim2.new(0.5, 0, 0.5, 0)      -- centered (with AnchorPoint)
frame.AnchorPoint = Vector2.new(0.5, 0.5)
frame.BackgroundColor3 = Color3.fromRGB(30, 30, 40)
frame.BackgroundTransparency = 0.1
frame.BorderSizePixel = 0
frame.Parent = screenGui
```

### TextLabel / TextButton

```luau
local label = Instance.new("TextLabel")
label.Size = UDim2.new(1, 0, 0, 40)
label.Text = "Score: 0"
label.TextColor3 = Color3.fromRGB(255, 255, 255)
label.TextScaled = true
label.Font = Enum.Font.GothamBold
label.BackgroundTransparency = 1
label.Parent = frame

local button = Instance.new("TextButton")
button.Size = UDim2.new(0.5, 0, 0, 50)
button.Text = "Purchase"
button.TextColor3 = Color3.fromRGB(255, 255, 255)
button.BackgroundColor3 = Color3.fromRGB(0, 170, 80)
button.Font = Enum.Font.GothamBold
button.TextSize = 18
button.Parent = frame

button.Activated:Connect(function()
    -- Activated works for mouse click, touch tap, and gamepad
end)
```

> Use `Activated` instead of `MouseButton1Click` for cross-platform support.

### ImageLabel / ImageButton

```luau
local icon = Instance.new("ImageLabel")
icon.Size = UDim2.new(0, 64, 0, 64)
icon.Image = "rbxassetid://123456789"
icon.ScaleType = Enum.ScaleType.Fit
icon.BackgroundTransparency = 1
icon.Parent = frame
```

### ScrollingFrame

See **section 14 (ScrollingFrame Patterns)** for full coverage including AutomaticCanvasSize, UIListLayout integration, and elastic overscroll.

### ViewportFrame

Renders 3D content inside a 2D GUI (item previews, character displays).

```luau
local viewport = Instance.new("ViewportFrame")
viewport.Size = UDim2.new(0, 200, 0, 200)
viewport.BackgroundColor3 = Color3.fromRGB(20, 20, 20)
viewport.Parent = frame

-- Clone a model into the viewport
local previewModel = workspace.SwordModel:Clone()
previewModel.Parent = viewport

-- Add a camera
local camera = Instance.new("Camera")
camera.CFrame = CFrame.new(Vector3.new(0, 2, 5), Vector3.new(0, 1, 0))
camera.Parent = viewport
viewport.CurrentCamera = camera
```

### Layout Modifiers

| Modifier | Purpose |
|---|---|
| `UIListLayout` | Arranges children in a vertical or horizontal list |
| `UIGridLayout` | Arranges children in a grid |
| `UIPageLayout` | Swipeable pages (one child visible at a time) |
| `UIPadding` | Inner padding on a container |
| `UICorner` | Rounded corners |
| `UIStroke` | Outline/border effect |
| `UIGradient` | Color gradient on an element |
| `UISizeConstraint` | Min/max pixel size |
| `UIAspectRatioConstraint` | Locks width/height ratio |

```luau
-- Rounded corners
local corner = Instance.new("UICorner")
corner.CornerRadius = UDim.new(0, 8)
corner.Parent = frame

-- Stroke/border
local stroke = Instance.new("UIStroke")
stroke.Color = Color3.fromRGB(255, 255, 255)
stroke.Thickness = 2
stroke.Transparency = 0.5
stroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
stroke.Parent = frame

-- Gradient
local gradient = Instance.new("UIGradient")
gradient.Color = ColorSequence.new(
    Color3.fromRGB(50, 50, 80),
    Color3.fromRGB(20, 20, 40)
)
gradient.Rotation = 90
gradient.Parent = frame

-- Padding
local padding = Instance.new("UIPadding")
padding.PaddingLeft = UDim.new(0, 12)
padding.PaddingRight = UDim.new(0, 12)
padding.PaddingTop = UDim.new(0, 12)
padding.PaddingBottom = UDim.new(0, 12)
padding.Parent = frame
```

---

## 4. Layout Systems

### UIListLayout

Arranges children sequentially. Best for menus, sidebars, chat messages, vertical/horizontal lists.

```luau
local listLayout = Instance.new("UIListLayout")
listLayout.FillDirection = Enum.FillDirection.Vertical
listLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
listLayout.VerticalAlignment = Enum.VerticalAlignment.Top
listLayout.SortOrder = Enum.SortOrder.LayoutOrder
listLayout.Padding = UDim.new(0, 8) -- gap between items
listLayout.Parent = frame
```

Children are sorted by their `LayoutOrder` property (lower values first).

### UIGridLayout

Arranges children in rows and columns. Best for inventories, shops, icon grids.

```luau
local gridLayout = Instance.new("UIGridLayout")
gridLayout.CellSize = UDim2.new(0, 80, 0, 80)
gridLayout.CellPadding = UDim2.new(0, 8, 0, 8)
gridLayout.FillDirection = Enum.FillDirection.Horizontal
gridLayout.FillDirectionMaxCells = 4 -- 4 columns, then wrap
gridLayout.SortOrder = Enum.SortOrder.LayoutOrder
gridLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
gridLayout.Parent = scrollFrame
```

### UIPageLayout

Shows one child at a time with animated page transitions. Best for tabbed menus, tutorials, onboarding flows.

```luau
local pageLayout = Instance.new("UIPageLayout")
pageLayout.Animated = true
pageLayout.EasingStyle = Enum.EasingStyle.Quad
pageLayout.EasingDirection = Enum.EasingDirection.InOut
pageLayout.TweenTime = 0.3
pageLayout.Circular = false    -- cannot loop from last to first
pageLayout.Padding = UDim.new(0, 0)
pageLayout.Parent = frame

-- Navigate pages
pageLayout:JumpToIndex(0)
pageLayout:Next()
pageLayout:Previous()
pageLayout:JumpTo(someChildFrame)
```

### When to Use Each

| Scenario | Layout |
|---|---|
| Vertical menu, chat log, leaderboard | `UIListLayout` |
| Inventory grid, shop items, emoji picker | `UIGridLayout` |
| Settings tabs, tutorial slides, shop categories | `UIPageLayout` |
| HUD element pinned to a corner | Absolute positioning (no layout) |
| Overlapping elements (health bar segments) | Absolute positioning |

### Absolute vs Layout-Driven

- **Absolute positioning**: Set `Position` and `Size` directly. Use for HUD elements pinned to specific screen locations.
- **Layout-driven**: Add a layout object as a child. The layout overrides children's `Position`. Use for dynamic lists where content count changes.

You can nest both: a frame with absolute position containing children managed by a UIListLayout.

---

## 5. Responsive Design

Scale vs Offset rules are in **Design Guidelines** above. This section covers constraints and adaptive patterns.

### UISizeConstraint

Prevents elements from becoming too small on phones or too large on ultrawide monitors.

```luau
local sizeConstraint = Instance.new("UISizeConstraint")
sizeConstraint.MinSize = Vector2.new(200, 150)
sizeConstraint.MaxSize = Vector2.new(600, 450)
sizeConstraint.Parent = frame
```

### UIAspectRatioConstraint

Locks an element's aspect ratio so it does not stretch.

```luau
local aspect = Instance.new("UIAspectRatioConstraint")
aspect.AspectRatio = 16 / 9
aspect.AspectType = Enum.AspectType.FitWithinMaxSize
aspect.DominantAxis = Enum.DominantAxis.Width
aspect.Parent = frame
```

### Adapting to Screen Size

```luau
local camera = workspace.CurrentCamera

local function adaptUI()
    local viewportSize = camera.ViewportSize
    local isPortrait = viewportSize.Y > viewportSize.X
    local isSmallScreen = viewportSize.X < 600

    if isSmallScreen then
        frame.Size = UDim2.new(0.95, 0, 0.8, 0)  -- nearly fullscreen on mobile
    elseif isPortrait then
        frame.Size = UDim2.new(0.7, 0, 0.5, 0)
    else
        frame.Size = UDim2.new(0.3, 0, 0.4, 0)   -- standard desktop
    end
end

camera:GetPropertyChangedSignal("ViewportSize"):Connect(adaptUI)
adaptUI()
```

---

## 6. Animation with TweenService

### TweenInfo

```luau
local TweenService = game:GetService("TweenService")

-- TweenInfo.new(time, easingStyle, easingDirection, repeatCount, reverses, delayTime)
local tweenInfo = TweenInfo.new(
    0.5,                           -- duration in seconds
    Enum.EasingStyle.Quad,         -- easing curve
    Enum.EasingDirection.Out,      -- direction
    0,                             -- repeat count (0 = no repeat, -1 = infinite)
    false,                         -- reverses
    0                              -- delay before starting
)
```

**Common Easing Styles:**

| Style | Use Case |
|---|---|
| `Quad` | General-purpose, smooth |
| `Back` | Slight overshoot, bouncy buttons |
| `Elastic` | Springy, attention-grabbing |
| `Bounce` | Bouncing effect at the end |
| `Linear` | Constant speed, progress bars |
| `Sine` | Gentle, subtle motion |
| `Exponential` | Dramatic acceleration/deceleration |

### Tweening UI Properties

```luau
-- Slide in from the right
frame.Position = UDim2.new(1.5, 0, 0.5, 0)

local slideIn = TweenService:Create(frame, TweenInfo.new(0.4, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
    Position = UDim2.new(0.5, 0, 0.5, 0),
})
slideIn:Play()

-- Fade in
frame.BackgroundTransparency = 1
local fadeIn = TweenService:Create(frame, TweenInfo.new(0.3), {
    BackgroundTransparency = 0,
})
fadeIn:Play()

-- Color transition
local colorShift = TweenService:Create(frame, TweenInfo.new(0.5), {
    BackgroundColor3 = Color3.fromRGB(255, 50, 50),
})
colorShift:Play()

-- Size pulse
local pulse = TweenService:Create(button, TweenInfo.new(0.6, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true), {
    Size = UDim2.new(0.55, 0, 0, 55),
})
pulse:Play()
```

### Chaining Tweens

```luau
local step1 = TweenService:Create(frame, TweenInfo.new(0.3), {
    Position = UDim2.new(0.5, 0, 0.5, 0),
})
local step2 = TweenService:Create(frame, TweenInfo.new(0.2), {
    Size = UDim2.new(0.4, 0, 0.5, 0),
})

step1.Completed:Connect(function()
    step2:Play()
end)
step1:Play()
```

### Common UI Animation Recipes

```luau
-- Bounce entrance
local function bounceIn(element: GuiObject)
    element.Size = UDim2.new(0, 0, 0, 0)
    element.AnchorPoint = Vector2.new(0.5, 0.5)
    local tween = TweenService:Create(element, TweenInfo.new(0.5, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
        Size = UDim2.new(0.3, 0, 0.4, 0),
    })
    tween:Play()
    return tween
end

-- Fade + scale dismiss
local function dismiss(element: GuiObject): RBXScriptSignal
    local tween = TweenService:Create(element, TweenInfo.new(0.25, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
        Size = UDim2.new(0, 0, 0, 0),
        BackgroundTransparency = 1,
    })
    tween:Play()
    return tween.Completed
end
```

---

## 7. Input Handling

### UserInputService

Low-level input detection. Best for keyboard shortcuts, mouse tracking, detecting input type.

```luau
local UserInputService = game:GetService("UserInputService")

-- Keyboard input
UserInputService.InputBegan:Connect(function(input: InputObject, gameProcessed: boolean)
    if gameProcessed then return end -- ignore if typing in a TextBox, etc.

    if input.KeyCode == Enum.KeyCode.E then
        toggleInventory()
    elseif input.KeyCode == Enum.KeyCode.Escape then
        togglePauseMenu()
    end
end)

-- Mouse position
local mousePos = UserInputService:GetMouseLocation() -- Vector2

-- Detect platform
local isMobile = UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled
local isConsole = UserInputService.GamepadEnabled

-- Hide mouse cursor
UserInputService.MouseIconEnabled = false
```

### ContextActionService

Higher-level action binding. Automatically generates mobile buttons. Best for game actions (interact, reload, sprint).

```luau
local ContextActionService = game:GetService("ContextActionService")

local function onInteract(actionName: string, inputState: Enum.UserInputState, inputObject: InputObject)
    if inputState == Enum.UserInputState.Begin then
        interactWithNearestObject()
    end
    return Enum.ContextActionResult.Sink -- consume the input
end

-- Bind to E key, touch button auto-created on mobile
ContextActionService:BindAction("Interact", onInteract, true, Enum.KeyCode.E)

-- Customize the mobile button
ContextActionService:SetPosition("Interact", UDim2.new(0.8, 0, 0.5, 0))
ContextActionService:SetTitle("Interact", "E")
ContextActionService:SetImage("Interact", "rbxassetid://123456789")

-- Unbind when no longer needed
ContextActionService:UnbindAction("Interact")
```

### When to Use Each

| Service | Best For |
|---|---|
| `UserInputService` | Global hotkeys, mouse tracking, detecting input device type, custom cursor |
| `ContextActionService` | In-game actions that need mobile buttons, context-sensitive controls (e.g., "interact" only near objects) |
| `GuiButton.Activated` | UI button clicks (already cross-platform) |

---

## 8. Common UI Patterns (Skeletons)

### Shop Interface

**Problem:** Display purchasable items in a grid with hover feedback and server-validated purchase.

**Structure:**
- ScrollingFrame + UIGridLayout (container)
  - Frame per item (card)
    - ImageLabel (icon)
    - TextLabel (name + price)
    - TextButton (buy) with hover tween

**Key properties:** UIGridLayout.CellSize for responsive cards, UICorner for rounded edges, TweenService for hover color shift. Purchase via RemoteFunction (server validates, returns success/fail).

### Health Bar

**Problem:** Show player health with color thresholds and damage trail effect.

**Structure:**
- Frame (container, dark background)
  - Frame (damage trail, red, tweens to match fill with delay)
  - Frame (fill, green→yellow→red based on %)

**Key logic:** On health change, tween fill Size.X.Scale to `health/maxHealth`. Color lerp between green/yellow/red at thresholds (0.6, 0.3). Damage trail: delay 0.3s then tween to match fill.

### Notification Toast

**Problem:** Temporary message that slides in, stays briefly, slides out.

**Structure:**
- Frame (anchored off-screen right)
  - TextLabel (message)
  - UICorner + UIStroke

**Key logic:** Tween Position from off-screen to visible, task.delay(3), tween back out, Destroy. Queue multiple toasts with vertical offset.

### Dialog / Popup System

**Problem:** Modal dialog with backdrop, title, body, confirm/cancel buttons.

**Structure:**
- Frame (backdrop, full-screen, semi-transparent black)
  - Frame (dialog card, centered, 0.4x0.3 scale)
    - TextLabel (title)
    - TextLabel (body)
    - Frame (button row)
      - TextButton (confirm)
      - TextButton (cancel)

**Key logic:** Show/hide by toggling Visible + tween BackgroundTransparency on backdrop. Return result via Promise or callback. Destroy on close.

---
## 9. Best Practices

### Positioning and Sizing

- **Always use Scale** for `Position` and `Size` to support all screen resolutions.
- **Use Offset** only for small fixed-pixel elements (icon sizes, padding, border thickness).
- **Always set AnchorPoint** when centering elements: `AnchorPoint = Vector2.new(0.5, 0.5)`.
- **Use UISizeConstraint** to set minimum and maximum sizes so UI does not become unusable on small screens or absurdly large on ultrawide monitors.

### Style and Theme Consistency

- Define colors, fonts, and sizes as constants at the top of your module.
- Create a UI style/theme module that all scripts reference.

```luau
-- UITheme.luau (ModuleScript in ReplicatedStorage)
local Theme = {
    Colors = {
        Background = Color3.fromRGB(25, 25, 35),
        Surface = Color3.fromRGB(40, 40, 55),
        Primary = Color3.fromRGB(0, 150, 70),
        Danger = Color3.fromRGB(200, 40, 40),
        TextPrimary = Color3.fromRGB(255, 255, 255),
        TextSecondary = Color3.fromRGB(180, 180, 190),
        Accent = Color3.fromRGB(255, 215, 0),
    },
    Fonts = {
        Title = Enum.Font.GothamBold,
        Body = Enum.Font.Gotham,
        Mono = Enum.Font.RobotoMono,
    },
    TextSizes = {
        Title = 24,
        Subtitle = 18,
        Body = 14,
        Small = 12,
    },
    CornerRadius = UDim.new(0, 8),
    Padding = UDim.new(0, 12),
}

return Theme
```

### Accessibility

- Minimum text size of **14pt** for body text; 12pt only for tertiary labels.
- Maintain **high contrast** between text and background (white on dark, dark on light).
- Use `TextScaled = true` with `TextWrapped = true` sparingly; prefer explicit `TextSize` for control.
- Provide visual feedback on all interactive elements (hover color change, press scale).
- Support gamepad navigation with `GuiService:Select()` for console players.

### Performance: GUI Pooling

For scrolling lists with many items (inventory, leaderboard), reuse GUI elements instead of creating/destroying them.

```luau
local pool: { Frame } = {}

local function getCard(): Frame
    local card = table.remove(pool)
    if not card then
        card = createNewCard() -- only create if pool is empty
    end
    card.Visible = true
    return card
end

local function returnCard(card: Frame)
    card.Visible = false
    card.Parent = nil
    table.insert(pool, card)
end
```

### General

- Set `ScreenGui.Enabled = false` when a UI is not visible rather than destroying and recreating it.
- Use `Activated` on buttons instead of `MouseButton1Click` for cross-platform support.
- Disconnect event connections when UI is destroyed to prevent memory leaks.
- Keep UI logic in ModuleScripts; keep LocalScripts thin (just wiring).
- Always validate purchases on the server. The client UI is only for display.

---

## 10. Anti-Patterns

### Hardcoded pixel positions

```luau
-- BAD: breaks on different resolutions
frame.Position = UDim2.new(0, 500, 0, 300)
frame.Size = UDim2.new(0, 400, 0, 200)

-- GOOD: responsive
frame.Position = UDim2.new(0.5, 0, 0.5, 0)
frame.Size = UDim2.new(0.3, 0, 0.25, 0)
frame.AnchorPoint = Vector2.new(0.5, 0.5)
```

### Creating new GUIs every frame

```luau
-- BAD: creates garbage every frame, causes lag
RunService.RenderStepped:Connect(function()
    local label = Instance.new("TextLabel")
    label.Text = `Score: ${score}`
    label.Parent = screenGui
end)

-- GOOD: update existing element
RunService.RenderStepped:Connect(function()
    scoreLabel.Text = `Score: ${score}`
end)
```

### Not cleaning up event connections

```luau
-- BAD: connection persists after UI is removed, leaks memory
button.Activated:Connect(function()
    doSomething()
end)

-- GOOD: store and disconnect
local connection = button.Activated:Connect(function()
    doSomething()
end)

-- When done:
connection:Disconnect()

-- OR use :Once() for single-fire events
button.Activated:Once(function()
    doSomething()
end)
```

### Blocking the UI thread with yields

```luau
-- BAD: freezes the entire UI
button.Activated:Connect(function()
    task.wait(5) -- nothing else can happen for 5 seconds
    label.Text = "Done"
end)

-- GOOD: use task.delay or task.spawn for async work
button.Activated:Connect(function()
    button.Active = false
    task.spawn(function()
        -- do async work
        task.wait(5)
        label.Text = "Done"
        button.Active = true
    end)
end)
```

### Trusting client UI for game logic

```luau
-- BAD: client decides if purchase succeeds
button.Activated:Connect(function()
    coins -= item.price  -- client-side deduction, exploitable
end)

-- GOOD: server validates everything
button.Activated:Connect(function()
    local success = purchaseRemote:InvokeServer(itemId)
    if success then
        updateCoinsDisplay()
    end
end)
```

### Ignoring mobile and gamepad

```luau
-- BAD: only works with mouse
button.MouseButton1Click:Connect(handler)

-- GOOD: works on mouse, touch, and gamepad
button.Activated:Connect(handler)
```

---

## 11. Mobile-First Design

78% of Roblox traffic is mobile. Design for touch first, adapt for desktop/gamepad.

### Touch Targets

- Minimum touch target: **44×44 px** (Apple guideline) or **48×48 dp** (Material Design)
- Buttons smaller than 44px are frustrating on phones
- Scale buttons 1.4× on touch devices:

```luau
local UserInputService = game:GetService("UserInputService")

local function isTouchDevice(): boolean
    return UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled
end

-- Apply at UI creation time
if isTouchDevice() then
    button.Size = UDim2.new(button.Size.X.Scale * 1.4, 0, button.Size.Y.Scale * 1.4, 0)
end
```

### PreferredInput API (2025+)

Modern approach to input detection. Use instead of checking individual booleans:

```luau
local preferred = UserInputService.PreferredInput
-- Enum.PreferredInput values:
--   Touch, MouseAndKeyboard, Gamepad, None

if preferred == Enum.PreferredInput.Touch then
    -- enlarge buttons, simplify layout
elseif preferred == Enum.PreferredInput.Gamepad then
    -- highlight focused element, add navigation hints
end

UserInputService:GetPropertyChangedSignal("PreferredInput"):Connect(function()
    -- re-adapt UI when input method changes
end)
```

### Safe Areas and Screen Real Estate

- Top bar takes **58px**. Use `ScreenGui.IgnoreGuiInset = true` for fullscreen, but don't put critical content behind it.
- Bottom of screen has virtual controls on mobile. Keep interactive elements above the bottom 100px.
- Use the **Device Emulator** in Studio (View → Device Emulator) to test phone/tablet views before shipping.

### Mobile Layout Rules

- Prefer vertical layouts over horizontal on mobile (scrolling down is natural)
- Avoid sidebars - use bottom sheets or full-screen overlays instead
- Use `UIScale` to zoom entire UI proportionally on small screens:

```luau
local uiScale = Instance.new("UIScale")
uiScale.Scale = math.min(1, camera.ViewportSize.X / 1080) -- reference width
uiScale.Parent = screenGui
```

### Gamepad Navigation

For console players:

```luau
local GuiService = game:GetService("GuiService")

-- Set the initially selected object when opening a menu
GuiService.SelectedObject = myButton

-- On menu close, clear selection
GuiService.SelectedObject = nil
```

Source: Roblox Adaptive Design Guidelines (create.roblox.com/docs/production/publishing/adaptive-design)

---

## 12. Text Handling

### AutomaticSize vs TextScaled

**Do NOT use `TextScaled = true`.** It makes text unreadably small on mobile and truncates text that doesn't fit.

Use `AutomaticSize` instead. It resizes the UI element to fit the text at a consistent, readable font size:

```luau
-- BAD: text scales to fit, becomes unreadable on small screens
label.TextScaled = true

-- GOOD: label grows/shrinks to fit text at fixed readable size
label.TextSize = 16
label.TextWrapped = true
label.AutomaticSize = Enum.AutomaticSize.Y -- height adjusts to content
```

### UITextSizeConstraint

If you must use `TextScaled`, always add a constraint:

```luau
local textSizeConstraint = Instance.new("UITextSizeConstraint")
textSizeConstraint.MaxTextSize = 24
textSizeConstraint.MinTextSize = 12 -- NEVER below 9 (official hard rule)
textSizeConstraint.Parent = label
```

### Text Truncation

```luau
label.TextTruncate = Enum.TextTruncate.AtEnd -- shows "..." when text overflows
label.TextWrapped = true -- wrap instead of truncate for multi-line content
```

### Calculating Text Size Programmatically

```luau
local TextService = game:GetService("TextService")

local bounds = TextService:GetTextSize(
    "Hello World",
    16,                -- TextSize
    Enum.Font.Gotham,
    Vector2.new(200, math.huge) -- max width, unlimited height
)
-- bounds.X = actual width, bounds.Y = actual height
```

Source: Roblox Size Modifiers & Constraints docs (create.roblox.com/docs/ui/size-modifiers)

---

## 13. UI Styling (StyleEditor)

Roblox ships a CSS-like styling system (2025+). Use it for consistent theming.

### Style Tokens

Named values (like CSS variables). Define once, reference everywhere.

### Style Rules with Selectors

```luau
-- Style rules can target by class, tag, name, state, modifier, query
-- Similar to CSS selectors
```

### When to Use StyleEditor vs Code Themes

| Approach | Best For |
|----------|----------|
| Studio StyleEditor | Static UI built visually, team collaboration on design |
| Code-based UITheme module | Dynamic UI built in code, programmatic theming |

Both can coexist. StyleEditor is the "build in Studio" answer; code themes are the "build in code" answer.

Source: Roblox UI Styling docs (create.roblox.com/docs/ui/styling)

---

## 14. ScrollingFrame Patterns

### AutomaticCanvasSize (Use This)

```luau
-- BAD: manually calculating canvas size
scrollFrame.CanvasSize = UDim2.new(0, 0, 0, listLayout.AbsoluteContentSize.Y)

-- GOOD: engine handles it automatically
scrollFrame.AutomaticCanvasSize = Enum.AutomaticSize.Y
scrollFrame.ScrollingDirection = Enum.ScrollingDirection.Y
```

### ScrollingFrame + UIListLayout

The most common pattern - a scrollable list:

```luau
local scrollFrame = Instance.new("ScrollingFrame")
scrollFrame.Size = UDim2.new(1, 0, 1, 0)
scrollFrame.BackgroundTransparency = 1
scrollFrame.ScrollBarThickness = 6
scrollFrame.AutomaticCanvasSize = Enum.AutomaticSize.Y
scrollFrame.ScrollingDirection = Enum.ScrollingDirection.Y
scrollFrame.Parent = container

local listLayout = Instance.new("UIListLayout")
listLayout.FillDirection = Enum.FillDirection.Vertical
listLayout.Padding = UDim.new(0, 8)
listLayout.SortOrder = Enum.SortOrder.LayoutOrder
listLayout.Parent = scrollFrame

-- Add items as children of scrollFrame
-- They auto-arrange vertically, scrollFrame auto-sizes
```

### ScrollingFrame + UIGridLayout

For scrollable grids (inventory, shop):

```luau
local scrollFrame = Instance.new("ScrollingFrame")
scrollFrame.AutomaticCanvasSize = Enum.AutomaticSize.Y
scrollFrame.ScrollingDirection = Enum.ScrollingDirection.Y
scrollFrame.Parent = container

local gridLayout = Instance.new("UIGridLayout")
gridLayout.CellSize = UDim2.new(0, 80, 0, 80)
gridLayout.CellPadding = UDim2.new(0, 8, 0, 8)
gridLayout.FillDirectionMaxCells = 4 -- 4 columns
gridLayout.SortOrder = Enum.SortOrder.LayoutOrder
gridLayout.Parent = scrollFrame
```

### Elastic Overscroll

The bouncy effect on iOS/Android. Enabled by default. Disable if unwanted:

```luau
scrollFrame.ElasticBehavior = Enum.ElasticBehavior.Never
```

Source: Roblox Scrolling Frames docs (create.roblox.com/docs/ui/scrolling-frames)

---

## Sources

- Roblox Adaptive Design Guidelines: create.roblox.com/docs/production/publishing/adaptive-design
- Roblox Size Modifiers & Constraints: create.roblox.com/docs/ui/size-modifiers
- Roblox UI Styling: create.roblox.com/docs/ui/styling
- Roblox Scrolling Frames: create.roblox.com/docs/ui/scrolling-frames
- Roblox List & Flex Layouts: create.roblox.com/docs/ui/list-flex-layouts
- Roblox Grid & Table Layouts: create.roblox.com/docs/ui/grid-table-layouts
- DevForum: Designing UI - Tips and Best Practices (Roblox Staff)
- DevForum: Design Mobile First
- DevForum: GUI Optimization Tips
- DevForum: epochzx - Container Frame Rule for ScreenGui
- DevForum: uiuxartist (Roblox Staff) - Scale vs Offset guidelines
- DevForum: PictureFolder - UI Design Tips and Best Practices (119 likes)
- DevForum: Modern UI Colour Schemes - dark palette guidelines
- Fusion: github.com/dphfox/Fusion (MIT)
- Vide: github.com/centau/vide (MIT)
- brockmartin/roblox-game-skill (MIT) - base content
