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

Scrollable container for lists and grids.

```luau
local scroll = Instance.new("ScrollingFrame")
scroll.Size = UDim2.new(1, 0, 1, 0)
scroll.CanvasSize = UDim2.new(0, 0, 0, 0)           -- set dynamically
scroll.AutomaticCanvasSize = Enum.AutomaticSize.Y     -- auto-grow vertically
scroll.ScrollBarThickness = 6
scroll.ScrollBarImageColor3 = Color3.fromRGB(200, 200, 200)
scroll.BackgroundTransparency = 1
scroll.Parent = frame
```

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

### Scale vs Offset

`UDim2` has two components: `Scale` (proportion of parent, 0-1) and `Offset` (fixed pixels).

```luau
-- BAD: hardcoded pixels, breaks on different screens
frame.Size = UDim2.new(0, 400, 0, 300)
frame.Position = UDim2.new(0, 100, 0, 50)

-- GOOD: proportional, adapts to any screen
frame.Size = UDim2.new(0.3, 0, 0.4, 0)
frame.Position = UDim2.new(0.5, 0, 0.5, 0)
frame.AnchorPoint = Vector2.new(0.5, 0.5)
```

**Rule:** Use Scale for Position and Size. Use Offset only for small fixed elements (icons, padding, stroke thickness).

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

## 8. Common UI Patterns

### Shop Interface

A complete shop system with a grid of items, currency display, and purchase flow.

```luau
-- LocalScript in StarterPlayerScripts or StarterGui
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

-- Remote for server-validated purchases
local purchaseRemote = ReplicatedStorage:WaitForChild("PurchaseItem")
local getCoinsRemote = ReplicatedStorage:WaitForChild("GetCoins")

--------------------------------------------------------------------------------
-- Data
--------------------------------------------------------------------------------

local SHOP_ITEMS = {
    { id = "sword", name = "Iron Sword", price = 100, icon = "rbxassetid://111111111" },
    { id = "shield", name = "Oak Shield", price = 150, icon = "rbxassetid://222222222" },
    { id = "potion", name = "Health Potion", price = 50, icon = "rbxassetid://333333333" },
    { id = "boots", name = "Speed Boots", price = 200, icon = "rbxassetid://444444444" },
    { id = "ring", name = "Power Ring", price = 300, icon = "rbxassetid://555555555" },
    { id = "cape", name = "Shadow Cape", price = 500, icon = "rbxassetid://666666666" },
}

--------------------------------------------------------------------------------
-- Create GUI Structure
--------------------------------------------------------------------------------

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "ShopGui"
screenGui.ResetOnSpawn = false
screenGui.DisplayOrder = 20
screenGui.Enabled = false
screenGui.Parent = playerGui

-- Dark overlay behind shop
local overlay = Instance.new("Frame")
overlay.Name = "Overlay"
overlay.Size = UDim2.new(1, 0, 1, 0)
overlay.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
overlay.BackgroundTransparency = 0.4
overlay.BorderSizePixel = 0
overlay.Parent = screenGui

-- Main shop panel
local shopPanel = Instance.new("Frame")
shopPanel.Name = "ShopPanel"
shopPanel.Size = UDim2.new(0.6, 0, 0.7, 0)
shopPanel.Position = UDim2.new(0.5, 0, 0.5, 0)
shopPanel.AnchorPoint = Vector2.new(0.5, 0.5)
shopPanel.BackgroundColor3 = Color3.fromRGB(25, 25, 35)
shopPanel.BorderSizePixel = 0
shopPanel.Parent = screenGui

local panelCorner = Instance.new("UICorner")
panelCorner.CornerRadius = UDim.new(0, 12)
panelCorner.Parent = shopPanel

local panelStroke = Instance.new("UIStroke")
panelStroke.Color = Color3.fromRGB(80, 80, 120)
panelStroke.Thickness = 2
panelStroke.Parent = shopPanel

local panelPadding = Instance.new("UIPadding")
panelPadding.PaddingLeft = UDim.new(0, 16)
panelPadding.PaddingRight = UDim.new(0, 16)
panelPadding.PaddingTop = UDim.new(0, 16)
panelPadding.PaddingBottom = UDim.new(0, 16)
panelPadding.Parent = shopPanel

-- Header bar
local header = Instance.new("Frame")
header.Name = "Header"
header.Size = UDim2.new(1, 0, 0, 50)
header.BackgroundTransparency = 1
header.Parent = shopPanel

local titleLabel = Instance.new("TextLabel")
titleLabel.Size = UDim2.new(0.5, 0, 1, 0)
titleLabel.Text = "SHOP"
titleLabel.Font = Enum.Font.GothamBold
titleLabel.TextSize = 28
titleLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
titleLabel.TextXAlignment = Enum.TextXAlignment.Left
titleLabel.BackgroundTransparency = 1
titleLabel.Parent = header

local coinsLabel = Instance.new("TextLabel")
coinsLabel.Name = "CoinsLabel"
coinsLabel.Size = UDim2.new(0.3, 0, 1, 0)
coinsLabel.Position = UDim2.new(0.5, 0, 0, 0)
coinsLabel.Text = "0 Coins"
coinsLabel.Font = Enum.Font.GothamBold
coinsLabel.TextSize = 22
coinsLabel.TextColor3 = Color3.fromRGB(255, 215, 0)
coinsLabel.TextXAlignment = Enum.TextXAlignment.Right
coinsLabel.BackgroundTransparency = 1
coinsLabel.Parent = header

local closeButton = Instance.new("TextButton")
closeButton.Name = "CloseButton"
closeButton.Size = UDim2.new(0, 40, 0, 40)
closeButton.Position = UDim2.new(1, 0, 0, 0)
closeButton.AnchorPoint = Vector2.new(1, 0)
closeButton.Text = "X"
closeButton.Font = Enum.Font.GothamBold
closeButton.TextSize = 20
closeButton.TextColor3 = Color3.fromRGB(255, 255, 255)
closeButton.BackgroundColor3 = Color3.fromRGB(180, 40, 40)
closeButton.BorderSizePixel = 0
closeButton.Parent = header

local closeCorner = Instance.new("UICorner")
closeCorner.CornerRadius = UDim.new(0, 8)
closeCorner.Parent = closeButton

-- Scrolling item grid
local scrollFrame = Instance.new("ScrollingFrame")
scrollFrame.Name = "ItemGrid"
scrollFrame.Size = UDim2.new(1, 0, 1, -60)
scrollFrame.Position = UDim2.new(0, 0, 0, 60)
scrollFrame.AutomaticCanvasSize = Enum.AutomaticSize.Y
scrollFrame.ScrollBarThickness = 6
scrollFrame.ScrollBarImageColor3 = Color3.fromRGB(120, 120, 160)
scrollFrame.BackgroundTransparency = 1
scrollFrame.BorderSizePixel = 0
scrollFrame.Parent = shopPanel

local gridLayout = Instance.new("UIGridLayout")
gridLayout.CellSize = UDim2.new(0, 140, 0, 180)
gridLayout.CellPadding = UDim2.new(0, 12, 0, 12)
gridLayout.FillDirection = Enum.FillDirection.Horizontal
gridLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
gridLayout.SortOrder = Enum.SortOrder.LayoutOrder
gridLayout.Parent = scrollFrame

local gridPadding = Instance.new("UIPadding")
gridPadding.PaddingTop = UDim.new(0, 8)
gridPadding.Parent = scrollFrame

--------------------------------------------------------------------------------
-- Create Item Cards
--------------------------------------------------------------------------------

local function createItemCard(itemData: { id: string, name: string, price: number, icon: string }, layoutOrder: number): Frame
    local card = Instance.new("Frame")
    card.Name = itemData.id
    card.LayoutOrder = layoutOrder
    card.BackgroundColor3 = Color3.fromRGB(40, 40, 55)
    card.BorderSizePixel = 0

    local cardCorner = Instance.new("UICorner")
    cardCorner.CornerRadius = UDim.new(0, 8)
    cardCorner.Parent = card

    local cardStroke = Instance.new("UIStroke")
    cardStroke.Color = Color3.fromRGB(60, 60, 90)
    cardStroke.Thickness = 1
    cardStroke.Parent = card

    -- Item icon
    local icon = Instance.new("ImageLabel")
    icon.Name = "Icon"
    icon.Size = UDim2.new(0.6, 0, 0, 70)
    icon.Position = UDim2.new(0.5, 0, 0, 10)
    icon.AnchorPoint = Vector2.new(0.5, 0)
    icon.Image = itemData.icon
    icon.ScaleType = Enum.ScaleType.Fit
    icon.BackgroundTransparency = 1
    icon.Parent = card

    -- Item name
    local nameLabel = Instance.new("TextLabel")
    nameLabel.Name = "ItemName"
    nameLabel.Size = UDim2.new(0.9, 0, 0, 22)
    nameLabel.Position = UDim2.new(0.5, 0, 0, 88)
    nameLabel.AnchorPoint = Vector2.new(0.5, 0)
    nameLabel.Text = itemData.name
    nameLabel.Font = Enum.Font.GothamBold
    nameLabel.TextSize = 14
    nameLabel.TextColor3 = Color3.fromRGB(230, 230, 230)
    nameLabel.TextTruncate = Enum.TextTruncate.AtEnd
    nameLabel.BackgroundTransparency = 1
    nameLabel.Parent = card

    -- Price label
    local priceLabel = Instance.new("TextLabel")
    priceLabel.Name = "Price"
    priceLabel.Size = UDim2.new(0.9, 0, 0, 20)
    priceLabel.Position = UDim2.new(0.5, 0, 0, 112)
    priceLabel.AnchorPoint = Vector2.new(0.5, 0)
    priceLabel.Text = tostring(itemData.price) .. " Coins"
    priceLabel.Font = Enum.Font.Gotham
    priceLabel.TextSize = 13
    priceLabel.TextColor3 = Color3.fromRGB(255, 215, 0)
    priceLabel.BackgroundTransparency = 1
    priceLabel.Parent = card

    -- Buy button
    local buyButton = Instance.new("TextButton")
    buyButton.Name = "BuyButton"
    buyButton.Size = UDim2.new(0.8, 0, 0, 32)
    buyButton.Position = UDim2.new(0.5, 0, 1, -10)
    buyButton.AnchorPoint = Vector2.new(0.5, 1)
    buyButton.Text = "BUY"
    buyButton.Font = Enum.Font.GothamBold
    buyButton.TextSize = 14
    buyButton.TextColor3 = Color3.fromRGB(255, 255, 255)
    buyButton.BackgroundColor3 = Color3.fromRGB(0, 150, 70)
    buyButton.BorderSizePixel = 0
    buyButton.Parent = card

    local buyCorner = Instance.new("UICorner")
    buyCorner.CornerRadius = UDim.new(0, 6)
    buyCorner.Parent = buyButton

    -- Hover effect
    buyButton.MouseEnter:Connect(function()
        TweenService:Create(buyButton, TweenInfo.new(0.15), {
            BackgroundColor3 = Color3.fromRGB(0, 180, 85),
        }):Play()
    end)

    buyButton.MouseLeave:Connect(function()
        TweenService:Create(buyButton, TweenInfo.new(0.15), {
            BackgroundColor3 = Color3.fromRGB(0, 150, 70),
        }):Play()
    end)

    -- Purchase handler
    buyButton.Activated:Connect(function()
        buyButton.Text = "..."
        buyButton.Active = false

        local success = purchaseRemote:InvokeServer(itemData.id)

        if success then
            buyButton.Text = "OWNED"
            buyButton.BackgroundColor3 = Color3.fromRGB(80, 80, 80)
            updateCoins()
        else
            buyButton.Text = "BUY"
            buyButton.Active = true

            -- Flash red to indicate failure
            TweenService:Create(buyButton, TweenInfo.new(0.1), {
                BackgroundColor3 = Color3.fromRGB(200, 50, 50),
            }):Play()
            task.delay(0.3, function()
                TweenService:Create(buyButton, TweenInfo.new(0.2), {
                    BackgroundColor3 = Color3.fromRGB(0, 150, 70),
                }):Play()
            end)
        end
    end)

    card.Parent = scrollFrame
    return card
end

-- Populate grid
for i, item in SHOP_ITEMS do
    createItemCard(item, i)
end

--------------------------------------------------------------------------------
-- Open / Close Logic
--------------------------------------------------------------------------------

local function updateCoins()
    local coins = getCoinsRemote:InvokeServer()
    coinsLabel.Text = tostring(coins) .. " Coins"
end

local function openShop()
    screenGui.Enabled = true
    updateCoins()

    -- Animate in
    shopPanel.Size = UDim2.new(0, 0, 0, 0)
    overlay.BackgroundTransparency = 1

    TweenService:Create(overlay, TweenInfo.new(0.25), {
        BackgroundTransparency = 0.4,
    }):Play()

    TweenService:Create(shopPanel, TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
        Size = UDim2.new(0.6, 0, 0.7, 0),
    }):Play()
end

local function closeShop()
    local fadeTween = TweenService:Create(overlay, TweenInfo.new(0.2), {
        BackgroundTransparency = 1,
    })
    local shrinkTween = TweenService:Create(shopPanel, TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
        Size = UDim2.new(0, 0, 0, 0),
    })

    fadeTween:Play()
    shrinkTween:Play()

    shrinkTween.Completed:Connect(function()
        screenGui.Enabled = false
    end)
end

closeButton.Activated:Connect(closeShop)
overlay.InputBegan:Connect(function(input)
    if input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch then
        closeShop()
    end
end)

-- Toggle with B key
local UserInputService = game:GetService("UserInputService")
UserInputService.InputBegan:Connect(function(input, gameProcessed)
    if gameProcessed then return end
    if input.KeyCode == Enum.KeyCode.B then
        if screenGui.Enabled then
            closeShop()
        else
            openShop()
        end
    end
end)
```

### Health Bar

A smooth health bar with color transitions and damage feedback.

```luau
-- LocalScript in StarterPlayerScripts or StarterGui
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

--------------------------------------------------------------------------------
-- Create Health Bar GUI
--------------------------------------------------------------------------------

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "HealthBarGui"
screenGui.ResetOnSpawn = true
screenGui.DisplayOrder = 5
screenGui.IgnoreGuiInset = false
screenGui.Parent = playerGui

-- Container
local container = Instance.new("Frame")
container.Name = "HealthBarContainer"
container.Size = UDim2.new(0.25, 0, 0, 28)
container.Position = UDim2.new(0.5, 0, 0.92, 0)
container.AnchorPoint = Vector2.new(0.5, 0.5)
container.BackgroundColor3 = Color3.fromRGB(20, 20, 20)
container.BorderSizePixel = 0
container.Parent = screenGui

local containerCorner = Instance.new("UICorner")
containerCorner.CornerRadius = UDim.new(0, 6)
containerCorner.Parent = container

local containerStroke = Instance.new("UIStroke")
containerStroke.Color = Color3.fromRGB(60, 60, 60)
containerStroke.Thickness = 2
containerStroke.Parent = container

local sizeConstraint = Instance.new("UISizeConstraint")
sizeConstraint.MinSize = Vector2.new(180, 24)
sizeConstraint.MaxSize = Vector2.new(500, 36)
sizeConstraint.Parent = container

-- Damage flash layer (behind the fill, shows briefly on damage)
local damageBar = Instance.new("Frame")
damageBar.Name = "DamageBar"
damageBar.Size = UDim2.new(1, 0, 1, 0)
damageBar.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
damageBar.BorderSizePixel = 0
damageBar.ZIndex = 1
damageBar.Parent = container

local damageCorner = Instance.new("UICorner")
damageCorner.CornerRadius = UDim.new(0, 6)
damageCorner.Parent = damageBar

-- Main health fill
local fillBar = Instance.new("Frame")
fillBar.Name = "FillBar"
fillBar.Size = UDim2.new(1, 0, 1, 0)
fillBar.BackgroundColor3 = Color3.fromRGB(0, 200, 80)
fillBar.BorderSizePixel = 0
fillBar.ZIndex = 2
fillBar.Parent = container

local fillCorner = Instance.new("UICorner")
fillCorner.CornerRadius = UDim.new(0, 6)
fillCorner.Parent = fillBar

local fillGradient = Instance.new("UIGradient")
fillGradient.Color = ColorSequence.new(
    Color3.fromRGB(255, 255, 255),
    Color3.fromRGB(200, 200, 200)
)
fillGradient.Rotation = 90
fillGradient.Parent = fillBar

-- Health text
local healthText = Instance.new("TextLabel")
healthText.Name = "HealthText"
healthText.Size = UDim2.new(1, 0, 1, 0)
healthText.Text = "100 / 100"
healthText.Font = Enum.Font.GothamBold
healthText.TextSize = 14
healthText.TextColor3 = Color3.fromRGB(255, 255, 255)
healthText.TextStrokeTransparency = 0.5
healthText.TextStrokeColor3 = Color3.fromRGB(0, 0, 0)
healthText.BackgroundTransparency = 1
healthText.ZIndex = 3
healthText.Parent = container

--------------------------------------------------------------------------------
-- Color Thresholds
--------------------------------------------------------------------------------

local COLOR_HIGH   = Color3.fromRGB(0, 200, 80)   -- green  (> 60%)
local COLOR_MEDIUM = Color3.fromRGB(230, 180, 0)   -- yellow (30%-60%)
local COLOR_LOW    = Color3.fromRGB(200, 40, 40)    -- red    (< 30%)

local function getHealthColor(fraction: number): Color3
    if fraction > 0.6 then
        return COLOR_HIGH
    elseif fraction > 0.3 then
        -- Lerp between yellow and green
        local t = (fraction - 0.3) / 0.3
        return COLOR_MEDIUM:Lerp(COLOR_HIGH, t)
    else
        -- Lerp between red and yellow
        local t = fraction / 0.3
        return COLOR_LOW:Lerp(COLOR_MEDIUM, t)
    end
end

--------------------------------------------------------------------------------
-- Update Logic
--------------------------------------------------------------------------------

local currentTween: Tween? = nil
local damageTween: Tween? = nil

local function updateHealthBar(health: number, maxHealth: number)
    local fraction = math.clamp(health / maxHealth, 0, 1)
    local targetColor = getHealthColor(fraction)

    healthText.Text = string.format("%d / %d", math.ceil(health), maxHealth)

    -- Cancel any running tween
    if currentTween then
        currentTween:Cancel()
    end

    -- Smooth fill tween
    currentTween = TweenService:Create(fillBar, TweenInfo.new(0.4, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
        Size = UDim2.new(fraction, 0, 1, 0),
        BackgroundColor3 = targetColor,
    })
    currentTween:Play()

    -- Damage trail: the red bar shrinks slower, creating a "trailing" effect
    if damageTween then
        damageTween:Cancel()
    end
    damageTween = TweenService:Create(damageBar, TweenInfo.new(0.8, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
        Size = UDim2.new(fraction, 0, 1, 0),
    })
    task.delay(0.3, function()
        if damageTween then
            damageTween:Play()
        end
    end)

    -- Low health pulse effect
    if fraction <= 0.25 then
        local pulse = TweenService:Create(container, TweenInfo.new(0.5, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true), {
            BackgroundTransparency = 0.3,
        })
        pulse:Play()
        container:SetAttribute("PulseTween", true)
    else
        -- Stop pulsing
        if container:GetAttribute("PulseTween") then
            container:SetAttribute("PulseTween", false)
            TweenService:Create(container, TweenInfo.new(0.2), {
                BackgroundTransparency = 0,
            }):Play()
        end
    end

    -- Screen flash on significant damage
    if fraction < 0.5 then
        local flash = Instance.new("Frame")
        flash.Size = UDim2.new(1, 0, 1, 0)
        flash.BackgroundColor3 = Color3.fromRGB(255, 0, 0)
        flash.BackgroundTransparency = 0.7
        flash.BorderSizePixel = 0
        flash.ZIndex = 10
        flash.Parent = screenGui

        local flashTween = TweenService:Create(flash, TweenInfo.new(0.3), {
            BackgroundTransparency = 1,
        })
        flashTween:Play()
        flashTween.Completed:Connect(function()
            flash:Destroy()
        end)
    end
end

--------------------------------------------------------------------------------
-- Connect to Character Health
--------------------------------------------------------------------------------

local function onCharacterAdded(character: Model)
    local humanoid = character:WaitForChild("Humanoid")

    -- Initialize
    updateHealthBar(humanoid.Health, humanoid.MaxHealth)

    -- Listen for changes
    humanoid.HealthChanged:Connect(function(newHealth: number)
        updateHealthBar(newHealth, humanoid.MaxHealth)
    end)
end

if player.Character then
    onCharacterAdded(player.Character)
end
player.CharacterAdded:Connect(onCharacterAdded)
```

### Notification Toast

```luau
local TweenService = game:GetService("TweenService")
local Players = game:GetService("Players")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "NotificationGui"
screenGui.ResetOnSpawn = false
screenGui.DisplayOrder = 50
screenGui.Parent = playerGui

-- Container for stacking toasts
local toastContainer = Instance.new("Frame")
toastContainer.Name = "ToastContainer"
toastContainer.Size = UDim2.new(0.3, 0, 0.5, 0)
toastContainer.Position = UDim2.new(1, -16, 0, 16)
toastContainer.AnchorPoint = Vector2.new(1, 0)
toastContainer.BackgroundTransparency = 1
toastContainer.Parent = screenGui

local listLayout = Instance.new("UIListLayout")
listLayout.FillDirection = Enum.FillDirection.Vertical
listLayout.VerticalAlignment = Enum.VerticalAlignment.Top
listLayout.Padding = UDim.new(0, 8)
listLayout.SortOrder = Enum.SortOrder.LayoutOrder
listLayout.Parent = toastContainer

local function showToast(message: string, duration: number?, color: Color3?)
    duration = duration or 3
    color = color or Color3.fromRGB(40, 40, 60)

    local toast = Instance.new("Frame")
    toast.Size = UDim2.new(1, 0, 0, 50)
    toast.BackgroundColor3 = color
    toast.BackgroundTransparency = 1
    toast.BorderSizePixel = 0
    toast.LayoutOrder = tick() -- newer toasts go below
    toast.Parent = toastContainer

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 8)
    corner.Parent = toast

    local stroke = Instance.new("UIStroke")
    stroke.Color = Color3.fromRGB(100, 100, 140)
    stroke.Thickness = 1
    stroke.Transparency = 1
    stroke.Parent = toast

    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, -24, 1, 0)
    label.Position = UDim2.new(0, 12, 0, 0)
    label.Text = message
    label.Font = Enum.Font.GothamBold
    label.TextSize = 14
    label.TextColor3 = Color3.fromRGB(255, 255, 255)
    label.TextTransparency = 1
    label.TextXAlignment = Enum.TextXAlignment.Left
    label.BackgroundTransparency = 1
    label.Parent = toast

    -- Slide in
    local slideIn = TweenService:Create(toast, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
        BackgroundTransparency = 0.1,
    })
    local textIn = TweenService:Create(label, TweenInfo.new(0.3), { TextTransparency = 0 })
    local strokeIn = TweenService:Create(stroke, TweenInfo.new(0.3), { Transparency = 0.5 })

    slideIn:Play()
    textIn:Play()
    strokeIn:Play()

    -- Auto-dismiss
    task.delay(duration, function()
        local fadeOut = TweenService:Create(toast, TweenInfo.new(0.3), { BackgroundTransparency = 1 })
        local textOut = TweenService:Create(label, TweenInfo.new(0.3), { TextTransparency = 1 })
        fadeOut:Play()
        textOut:Play()
        fadeOut.Completed:Connect(function()
            toast:Destroy()
        end)
    end)
end

-- Usage
showToast("Quest completed: Defeat 10 Goblins!")
showToast("Not enough coins!", 4, Color3.fromRGB(140, 30, 30))
```

### Dialog / Popup System

```luau
local TweenService = game:GetService("TweenService")
local Players = game:GetService("Players")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "DialogGui"
screenGui.ResetOnSpawn = false
screenGui.DisplayOrder = 100 -- above everything
screenGui.Enabled = false
screenGui.Parent = playerGui

local overlay = Instance.new("Frame")
overlay.Size = UDim2.new(1, 0, 1, 0)
overlay.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
overlay.BackgroundTransparency = 1
overlay.BorderSizePixel = 0
overlay.Parent = screenGui

local dialogFrame = Instance.new("Frame")
dialogFrame.Name = "DialogFrame"
dialogFrame.Size = UDim2.new(0.35, 0, 0, 180)
dialogFrame.Position = UDim2.new(0.5, 0, 0.5, 0)
dialogFrame.AnchorPoint = Vector2.new(0.5, 0.5)
dialogFrame.BackgroundColor3 = Color3.fromRGB(35, 35, 50)
dialogFrame.BorderSizePixel = 0
dialogFrame.Parent = screenGui

Instance.new("UICorner", dialogFrame).CornerRadius = UDim.new(0, 12)
local dStroke = Instance.new("UIStroke")
dStroke.Color = Color3.fromRGB(90, 90, 130)
dStroke.Thickness = 2
dStroke.Parent = dialogFrame

local dialogTitle = Instance.new("TextLabel")
dialogTitle.Name = "Title"
dialogTitle.Size = UDim2.new(0.9, 0, 0, 36)
dialogTitle.Position = UDim2.new(0.5, 0, 0, 16)
dialogTitle.AnchorPoint = Vector2.new(0.5, 0)
dialogTitle.Text = "Confirm"
dialogTitle.Font = Enum.Font.GothamBold
dialogTitle.TextSize = 22
dialogTitle.TextColor3 = Color3.fromRGB(255, 255, 255)
dialogTitle.BackgroundTransparency = 1
dialogTitle.Parent = dialogFrame

local dialogMessage = Instance.new("TextLabel")
dialogMessage.Name = "Message"
dialogMessage.Size = UDim2.new(0.85, 0, 0, 50)
dialogMessage.Position = UDim2.new(0.5, 0, 0, 56)
dialogMessage.AnchorPoint = Vector2.new(0.5, 0)
dialogMessage.Text = "Are you sure?"
dialogMessage.Font = Enum.Font.Gotham
dialogMessage.TextSize = 16
dialogMessage.TextColor3 = Color3.fromRGB(200, 200, 210)
dialogMessage.TextWrapped = true
dialogMessage.BackgroundTransparency = 1
dialogMessage.Parent = dialogFrame

local confirmBtn = Instance.new("TextButton")
confirmBtn.Name = "ConfirmButton"
confirmBtn.Size = UDim2.new(0.4, 0, 0, 40)
confirmBtn.Position = UDim2.new(0.27, 0, 1, -20)
confirmBtn.AnchorPoint = Vector2.new(0.5, 1)
confirmBtn.Text = "Confirm"
confirmBtn.Font = Enum.Font.GothamBold
confirmBtn.TextSize = 16
confirmBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
confirmBtn.BackgroundColor3 = Color3.fromRGB(0, 150, 70)
confirmBtn.BorderSizePixel = 0
confirmBtn.Parent = dialogFrame
Instance.new("UICorner", confirmBtn).CornerRadius = UDim.new(0, 8)

local cancelBtn = Instance.new("TextButton")
cancelBtn.Name = "CancelButton"
cancelBtn.Size = UDim2.new(0.4, 0, 0, 40)
cancelBtn.Position = UDim2.new(0.73, 0, 1, -20)
cancelBtn.AnchorPoint = Vector2.new(0.5, 1)
cancelBtn.Text = "Cancel"
cancelBtn.Font = Enum.Font.GothamBold
cancelBtn.TextSize = 16
cancelBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
cancelBtn.BackgroundColor3 = Color3.fromRGB(100, 100, 110)
cancelBtn.BorderSizePixel = 0
cancelBtn.Parent = dialogFrame
Instance.new("UICorner", cancelBtn).CornerRadius = UDim.new(0, 8)

type DialogOptions = {
    title: string,
    message: string,
    confirmText: string?,
    cancelText: string?,
}

local function showDialog(options: DialogOptions): boolean
    dialogTitle.Text = options.title
    dialogMessage.Text = options.message
    confirmBtn.Text = options.confirmText or "Confirm"
    cancelBtn.Text = options.cancelText or "Cancel"

    screenGui.Enabled = true

    -- Animate in
    overlay.BackgroundTransparency = 1
    dialogFrame.Size = UDim2.new(0, 0, 0, 0)

    TweenService:Create(overlay, TweenInfo.new(0.2), { BackgroundTransparency = 0.5 }):Play()
    TweenService:Create(dialogFrame, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
        Size = UDim2.new(0.35, 0, 0, 180),
    }):Play()

    -- Wait for user response using a BindableEvent
    local resolveEvent = Instance.new("BindableEvent")
    local result = false

    local confirmConn: RBXScriptConnection
    local cancelConn: RBXScriptConnection

    confirmConn = confirmBtn.Activated:Connect(function()
        result = true
        resolveEvent:Fire()
    end)

    cancelConn = cancelBtn.Activated:Connect(function()
        result = false
        resolveEvent:Fire()
    end)

    resolveEvent.Event:Wait()
    confirmConn:Disconnect()
    cancelConn:Disconnect()
    resolveEvent:Destroy()

    -- Animate out
    TweenService:Create(overlay, TweenInfo.new(0.15), { BackgroundTransparency = 1 }):Play()
    local closeTween = TweenService:Create(dialogFrame, TweenInfo.new(0.15, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
        Size = UDim2.new(0, 0, 0, 0),
    })
    closeTween:Play()
    closeTween.Completed:Wait()

    screenGui.Enabled = false

    return result
end

-- Usage:
-- local confirmed = showDialog({
--     title = "Delete Item",
--     message = "This will permanently delete your Legendary Sword. This cannot be undone.",
--     confirmText = "Delete",
--     cancelText = "Keep",
-- })
-- if confirmed then
--     deleteItem()
-- end
```

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
    label.Text = "Score: " .. score
    label.Parent = screenGui
end)

-- GOOD: update existing element
RunService.RenderStepped:Connect(function()
    scoreLabel.Text = "Score: " .. score
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
