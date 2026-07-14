# roblox gui: full reference

The most reliable Roblox UI is layout-driven, state-aware, and tested at more than one aspect ratio. The examples below use native UI objects and do not require a UI framework.

## 1. Choose the container

- `ScreenGui`: a 2D overlay attached to a player's screen.
- `SurfaceGui`: controls rendered on a part or attachment.
- `BillboardGui`: a camera-facing label or panel in the 3D world.
- `ViewportFrame`: a UI region that renders a 3D model preview.

Set `DisplayOrder` deliberately when multiple `ScreenGui` instances overlap. Use `ResetOnSpawn` only when the UI should survive character respawn. Do not set `IgnoreGuiInset` globally without checking how the layout interacts with Roblox's top-bar and safe-area behavior.

## 2. Build from containers

Give each visual region a container with one responsibility: header, content, footer, or modal. Put a layout object inside the container that owns repeated children.

```luau
local panel = Instance.new("Frame")
panel.Name = "InventoryPanel"
panel.AnchorPoint = Vector2.new(0.5, 0.5)
panel.Position = UDim2.fromScale(0.5, 0.5)
panel.Size = UDim2.fromScale(0.8, 0.75)
panel.BackgroundColor3 = Color3.fromRGB(25, 28, 36)
panel.Parent = screenGui

local padding = Instance.new("UIPadding")
padding.PaddingTop = UDim.new(0, 16)
padding.PaddingBottom = UDim.new(0, 16)
padding.PaddingLeft = UDim.new(0, 16)
padding.PaddingRight = UDim.new(0, 16)
padding.Parent = panel

local list = Instance.new("UIListLayout")
list.Padding = UDim.new(0, 8)
list.SortOrder = Enum.SortOrder.LayoutOrder
list.Parent = panel
```

Use `LayoutOrder` as data, not as a visual afterthought. If children are created dynamically, assign their order in the view model or row constructor.

## 3. Scale and offset

`UDim2` combines proportional `Scale` with fixed `Offset`. A common pattern is scale for the outer region and offset for internal padding:

```luau
local card = Instance.new("Frame")
card.AnchorPoint = Vector2.new(0.5, 1)
card.Position = UDim2.fromScale(0.5, 0.94)
card.Size = UDim2.new(0.86, 0, 0, 120)

local sizeLimit = Instance.new("UISizeConstraint")
sizeLimit.MinSize = Vector2.new(260, 96)
sizeLimit.MaxSize = Vector2.new(720, 220)
sizeLimit.Parent = card
```

Use `UIAspectRatioConstraint` for shapes that must remain square or maintain a fixed ratio. Keep text containers bounded so a translated or long string cannot expand the entire screen unexpectedly.

## 4. Text and images

Choose one sizing policy for each text region:

- fixed `TextSize` plus a layout constraint when the content is controlled;
- `TextScaled` only when the allowed range is bounded by `UITextSizeConstraint`;
- `AutomaticSize` when the parent has room to grow and the layout can respond.

Test long strings, empty strings, and missing images. A missing asset should produce a useful placeholder, not a layout collapse. Avoid putting essential game state only in color or iconography.

## 5. Scrolling content

A `ScrollingFrame` needs a clear canvas policy. For a vertical list, put a `UIListLayout` inside it and use `AutomaticCanvasSize = Enum.AutomaticSize.Y` when the project does not need to calculate canvas size manually.

```luau
local scroll = Instance.new("ScrollingFrame")
scroll.Size = UDim2.fromScale(1, 1)
scroll.AutomaticCanvasSize = Enum.AutomaticSize.Y
scroll.CanvasSize = UDim2.fromScale(0, 0)
scroll.ScrollBarThickness = 6
scroll.Parent = content

local list = Instance.new("UIListLayout")
list.Padding = UDim.new(0, 6)
list.SortOrder = Enum.SortOrder.LayoutOrder
list.Parent = scroll
```

Do not nest an automatically growing scroll region inside another automatic scroll region unless the interaction is intentional and tested.

## 6. UI state and server state

The UI should render a snapshot or view model. It may request an action, but the server response determines the final display.

```luau
local state = {
    busy = false,
    selectedId = nil,
}

local function render()
    buyButton.Active = not state.busy and state.selectedId ~= nil
    spinner.Visible = state.busy
end

buyButton.Activated:Connect(function()
    if state.busy or not state.selectedId then
        return
    end
    state.busy = true
    render()
    BuyItem:FireServer(state.selectedId)
end)

PurchaseResult.OnClientEvent:Connect(function(ok, message)
    state.busy = false
    statusLabel.Text = message
    render()
end)
```

Do not grant currency, inventory, or ownership because a local button handler ran. The UI is an input surface, not a trust boundary.

## 7. Input and interaction

Use `Activated` for buttons when possible. Use `ContextActionService` for actions that should map across keyboard, gamepad, and touch. Use `UserInputService` when you need raw device details or gesture tracking.

Every interactive control needs:

- a visible state for hover, press, disabled, and focus where the platform supports it;
- a clear label or tooltip;
- a route that works without precise mouse aiming;
- a debounced action that cannot issue duplicate requests while busy.

## 8. Gamepad focus and selection

Gamepad support is not complete when a button merely reacts to `Activated`. The player also needs a predictable focus path:

```luau
local GuiService = game:GetService("GuiService")

playButton.Selectable = true
settingsButton.Selectable = true

-- Set this when opening the menu, not every frame.
GuiService.SelectedObject = playButton
```

For larger menus, group related controls and define explicit directional behavior where automatic selection is ambiguous. Test selection entering and leaving nested containers, covered elements, modal dialogs, and a changing list. Roblox's current directional-selection behavior includes ancestor grouping, covered-element handling, and improved analog-stick navigation. The official `focus-navigation` repository is a read-only mirror and is best treated as an optional reference rather than a mandatory dependency.

React Luau is another optional reference for state-driven, declarative UI. Do not introduce it into a small native UI merely to avoid writing a few render functions.

## 9. Animation and cleanup

Tween a small set of properties and cancel or replace the previous tween when state changes. Keep connections and tweens owned by the screen or row they affect. Destroy temporary UI when the owning feature closes.

```luau
local TweenService = game:GetService("TweenService")
local modal = screenGui.Modal -- CanvasGroup
local openTween = TweenService:Create(
    modal,
    TweenInfo.new(0.18, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
    { GroupTransparency = 0 }
)

openTween:Play()
```

If the object can be destroyed before the tween completes, connect cleanup to the owner's lifetime rather than assuming `Completed` will always run.

## 10. Shops, dialogs, and notifications

A practical UI flow is:

1. render a neutral/loading state;
2. load or receive the data model;
3. allow one action at a time per row or transaction;
4. show a success, failure, or retry state;
5. refresh from authoritative state after the action.

Do not close a purchase dialog merely because a prompt was opened. Wait for the purchase or server result, and handle cancellation.

## 11. Safe areas and cross-device review

Do not choose `ScreenInsets`, `IgnoreGuiInset`, or `ClipToDeviceSafeArea` from a single Studio viewport. Test the actual target combinations and record which elements intentionally sit under or outside Roblox core UI.

Test at minimum:

- narrow phone portrait;
- wide phone or tablet landscape;
- desktop mouse/keyboard;
- gamepad navigation;
- console safe-area and top-bar behavior;
- mobile cutout/notch and on-screen keyboard behavior;
- a long localized string;
- a missing or delayed asset;
- respawn and UI reopening;
- low frame rate while a list is updating.

A layout that looks correct at one Studio viewport size is not finished. Capture the intended states and compare them after changing the viewport and preferred input.

## UI checklist

- [ ] Containers use layout objects and constraints instead of scattered pixel positions.
- [ ] Text growth, clipping, and scrolling have an explicit policy.
- [ ] Buttons expose disabled and busy states.
- [ ] UI actions are safe to repeat or are debounced.
- [ ] Server responses, not local optimism, determine durable state.
- [ ] The interface works with touch, mouse, keyboard, and gamepad where relevant.
- [ ] All temporary connections, tweens, and rows have an owner lifetime.
