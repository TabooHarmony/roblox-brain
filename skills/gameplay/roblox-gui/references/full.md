# roblox gui: full reference (layout, devices, focus)

> Code examples are illustrative. Adapt them to your project and verify in Studio before production use.

This file covers where UI goes and how it adapts: containers, scale, safe areas, mobile-first layout, console and TV, gamepad focus, and cross-device checks. Menus, shops, dialogs, HUD widgets, text entry, lists, grids, effects and legacy migration are in `roblox-gui-components`.

The most reliable Roblox UI is layout-driven, state-aware, and tested at more than one aspect ratio. The examples use native UI objects and do not require a UI framework.

## 1. Choose the container

- `ScreenGui`: a 2D overlay attached to a player's screen.
- `SurfaceGui`: controls rendered on a part or attachment.
- `BillboardGui`: a camera-facing label or panel in the 3D world.
- `ViewportFrame`: a UI region that renders a 3D model preview (its camera: `roblox-camera`, `ViewportCamera`).

Set `DisplayOrder` deliberately when multiple `ScreenGui` instances overlap. For UI templates in `StarterGui`, set `ResetOnSpawn = false` and keep the `ScreenGui` a direct child of `StarterGui` to clone it once and preserve it across respawns. Templates with `ResetOnSpawn = true` (the default), or nested indirectly under `StarterGui`, are deleted and re-cloned on respawn. Do not set `IgnoreGuiInset` globally without checking how the layout interacts with the top bar (§7.4).

`ZIndexBehavior`: under `Sibling`, children always draw above their parent and `ZIndex` only orders siblings; under `Global`, `ZIndex` compares across the whole ScreenGui. Observed in one project: a UI kit's reflection frame drew over its own button face when the kit was mocked in a fresh ScreenGui left on `Global`. Match the `ZIndexBehavior` the kit was built for.

A `Folder` is only a container. GUI objects under a Folder inside a ScreenGui still render (observed once), so hide or disable templates before parenting them into a live hierarchy, or keep templates in `ReplicatedStorage`.

### World UI (BillboardGui and SurfaceGui)

- **Size billboard children with pure scale.** Inside a stud-sized `BillboardGui`, children sized in pixel offsets, or with a pixel minimum, do not shrink with distance; at normal viewing distance a card can overflow and balloon across the screen (observed). Use scale sizes plus `TextScaled`, keep `ClipsDescendants` on, and check near, normal and far distances.
- **Keep billboards off walls.** A billboard turns to face the camera, so one anchored close to a wall sinks half into it at an angle. Keep the anchor at least half the billboard's width off the wall.
- **Fading:** verify `CanvasGroup` fades on world UI in your target runtime. If group transparency does not reach rendered descendants, tween each text, background and stroke transparency and disable the billboard when hidden (observed once; verify before relying on either path).
- **Short-lived world popups** (damage or cash floats) can be drawn in their own `ScreenGui` instead (`ResetOnSpawn = false`, `IgnoreGuiInset = true`), placed every frame from `Camera:WorldToViewportPoint`. Measured in one project: a respawn deleted a Folder parented straight to `PlayerGui` that held popup billboards, and Studio screenshot capture did not show those billboards at all, while a `SurfaceGui` on the same part did. Check alignment by firing popups at the camera's look point and comparing against the crosshair.

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

### Layout modifiers have side effects

Observed across several projects:

- A `UIPadding` on a button also insets its child frames, so a cooldown overlay comes out narrower than the slot. Leave padding off buttons that hold overlay children, and size the text to fit instead.
- A slot's own `UIScale` changes its footprint inside a `UIListLayout` and moves its neighbours. Place animated slots by position with a centre anchor rather than letting the list re-flow every frame.
- Only one `UIScale` applies per object. Remove a UI kit's built-in `UIScale` when your controller scales the same object.

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

Use `UIAspectRatioConstraint` for shapes that must keep a ratio. Keep text containers bounded so a translated or long string cannot expand the whole screen.

### A fixed design stage scaled with UIScale

Some projects author at one resolution (for example 1920×1080) and scale a stage to the screen by the tighter of width and height. Centre menus on that stage over a full-bleed backdrop, and pin HUD elements to the stage edges so they still reach the corners on wide screens. Two traps:

- **`UITextSizeConstraint` ignores `UIScale`.** `MaxTextSize`/`MinTextSize` are in screen pixels. A stage scaled up 1.8× on PC kept its text at the unscaled cap, so labels looked small in their boxes, while on phones (scale below 1) the same labels filled (observed in two projects). Scale each cap with the stage's `UIScale` (store the base value in an attribute), or drop the constraint from text that should scale. `TextScaled` also stops at 100 px.
- **Keep the top-left corner clear in game.** Roblox's menu and chat buttons sit there and the chat window opens under them (§7.2). Put a logo right of those buttons and shrink or hide it when room runs out.

## 4. Text sizing policy

Choose one sizing policy for each text region:

- fixed `TextSize` plus a layout constraint when the content is controlled;
- `TextScaled` only when the allowed range is bounded by `UITextSizeConstraint` (and see §3 for `UIScale`);
- `AutomaticSize` when the parent has room to grow and the layout can respond.

Test long strings, empty strings, and missing images. A missing asset should produce a placeholder, not a layout collapse. Do not put essential game state only in color or iconography. Truncation, RichText and price glyphs: `roblox-gui-components` §1.

## 5. Clipping and rotation

`GuiObject.ClipsDescendants` clips descendant GUI objects at the container's bounds. Rotation changes the rules:

- Clipping of **rotated descendants** (non-zero `Rotation`) works only when `StarterGui.ClipsDescendantsSupportsRotation` is enabled (a `RolloutState` set in Studio). When it is not enabled and the container or any ancestor is rotated, `ClipsDescendants` is ignored and descendants render regardless.
- Clipping **by** a rotated container, and clipping by rounded corners (`UICorner`), is not supported even with that flag. A tilted card with `ClipsDescendants = true` spills its children. Keep clipping containers unrotated and rotate only the inner content, or use a `CanvasGroup` when you need clipping on a rotated or rounded shape.
- Rotating a Frame rotates its descendant frames with it (checked live in one project), so a badge drawn from several frames can wiggle as one without a `CanvasGroup`.
- A `CanvasGroup` clips its descendants to its bounds. An outline or shadow drawn outside the group's box is cut off, so inset the content inside the group. For its texture-resolution cost, see `roblox-gui-components` §10.

## 6. Gamepad focus and selection

Gamepad support is not complete when a button merely reacts to `Activated`. The player also needs a predictable focus path:

```luau
local GuiService = game:GetService("GuiService")

playButton.Selectable = true
settingsButton.Selectable = true

-- Set this when opening the menu, not every frame.
GuiService.SelectedObject = playButton
```

For larger menus, group related controls and define explicit directional behavior where automatic selection is ambiguous. Test selection entering and leaving nested containers, covered elements, modal dialogs, and a changing list. Roblox's directional selection includes ancestor grouping, covered-element handling, and analog-stick navigation. The official `focus-navigation` repository is a read-only mirror; treat it as an optional reference. React Luau is another optional reference for declarative UI; do not introduce it into a small native UI to avoid writing a few render functions.

### Focus ownership

Most controller bugs are focus bugs, not missing bindings. Give every view one owner of `GuiService.SelectedObject`:

- **Entry:** when a view opens on gamepad, select a control visible in the *current* sub-view (the active tab's first actionable item), not a fixed "Claim" or "Buy" button a tab switch may have hidden. Re-check after every tab switch, page change and list rebuild. One working rule: pick the top-left selectable, interactable button, treating rows within about 4 px as one row.
- **Boundary:** set `SelectionGroup = true` on a window's root and `SelectionBehaviorUp/Down/Left/Right = Enum.SelectionBehavior.Stop` on edges where focus must not escape. With the default `Escape`, navigation can leave the window and land on HUD buttons behind it.
- **Lost focus:** when `SelectedObject` becomes nil while a window is open (its button was destroyed or hidden), restore a visible control on a deferred call rather than in the same frame.
- **Rebuilt lists:** remember the selected item's id before a list is destroyed and recreated (equip, purchase, filter). Afterwards, select the matching new row or a visible fallback, and keep the scroll position.
- **Back:** B/Circle unwinds one layer at a time: an inner overlay closes before its window, and the window before gameplay. Non-modal panels that take input (results, spectate controls, offers) need their own Back route.
- **Exit:** on close, restore the control that opened the view if it still exists and is visible, otherwise clear the selection. When the player switches away from gamepad (`PreferredInput` changes), clear stale game selection.
- **No stealing:** automatic panels (offers, notifications, spectate changes) must not move focus while another view owns it.
- **Stray selection blocks gameplay:** while `SelectedObject` is set, gamepad buttons drive UI. A selection left on a HUD button after a menu closes can swallow the attack or jump press. Clear it when gameplay resumes, and include "is a GUI selected?" in the gameplay input gate (`roblox-input`).
- **Third-party top-bar libraries** can bind global gamepad keys. One popular top-bar library binds D-pad Up to select its icons, which pulls focus out of any open window. Check its controller-binding settings.

### Focus feedback

- `GuiObject.SelectionGained` and `SelectionLost` pass the previous/new object and a `GuiNavigationDirection` (`Up`, `Down`, `Left`, `Right`, `Forward`, `Backward`, or `None` when selection did not change through navigation). Treat gained/lost as hover in button feedback, or controller focus has no hover state.
- Roblox's default selection outline is thin. A custom `PlayerGui.SelectionImageObject` (for example a frame a few pixels larger on each side with a `UICorner` and a white `UIStroke`) reads better on a TV. Restore the previous value on cleanup.
- Show button glyphs only while `UserInputService.PreferredInput` is `Gamepad`, and re-check on change (`roblox-input`).

Make the main destinations reachable in a few presses. Console navigation is sequential, so add shortcuts for key actions (for example a bumper that opens the main menu) instead of making players traverse the whole HUD.

## 7. Mobile-first layout and cross-device review

Roblox's mobile input guide states that the majority of sessions are played on mobile devices. Design every screen for a small landscape phone first, then let it grow for tablet, desktop and TV. A layout designed at 1080p and shrunk to a phone ends up with tap targets and text too small to use.

### 7.1 Design order

1. **Smallest supported landscape phone** (iPhone SE/7 class, about 667×375 points), with the touch controls showing.
2. **Common phones** (about 780–850 × 360–390). Notches and home-bar insets live here.
3. **Tablet** (1024×768 and 960×600 class). Check that the layout grows instead of stretching. Check tablets separately: one pass tuned for phones overcorrected and made tablet buttons too small.
4. **Desktop** with mouse and keyboard.
5. **Console/TV** with a controller at 1080p and 4K (§8).

Fix each layout before moving to the next, and re-check the phone after every change.

### 7.2 What Roblox already occupies

| Region | Owner | How to read it |
|---|---|---|
| Top bar | Roblox menu, chat and backpack buttons | `GuiService:GetGuiInset()` for the inset; `GuiService.TopbarInset` (a `Rect`) for the free strip beside Roblox's buttons. It changes at runtime; listen with `GetPropertyChangedSignal("TopbarInset")`. |
| Device cutouts | Notch, camera hole, rounded corners | `ScreenGui.ScreenInsets` (§7.3) |
| Movement zone | Thumbstick (the dynamic thumbstick accepts touches across much of the left side) | Treat the lower-left area as reserved |
| Jump button | Bottom-right | Measure it from `PlayerGui.TouchGui` (§7.4, `roblox-input`) |
| Chat window and player list | Upper-left and upper-right on desktop | Leave room, or move your HUD when they are open |

Anything else in the lower-right competes with the jump button and with camera drags. With the thumbstick and action buttons on the left and right edges, top-centre is usually the free space for new HUD elements.

### 7.3 Safe-area containers

`Enum.ScreenInsets` per `ScreenGui`:

- `CoreUISafeInsets`: avoids device cutouts **and** Roblox core UI. The docs recommend it for interactive and important UI.
- `DeviceSafeInsets`: avoids cutouts only. Use it when you place content beside the top-bar buttons.
- `TopbarSafeInsets`: the free strip in the top bar.
- `None`: the full screen. Use it only for non-interactive content (backgrounds, vignettes, flashes) and for things that must sit at the true screen centre.

`ScreenGui.ClipToDeviceSafeArea` defaults to `true`, which clips descendants at the safe area. `SafeAreaCompatibility` defaults to `FullscreenExtension`; for new work the docs recommend choosing `ScreenInsets` per container.

Field measurements (one project, desktop and a notched phone preset):

- **The canvas is smaller than the screen.** A ScreenGui with `IgnoreGuiInset = true` still reported `ScreenInsets = DeviceSafeInsets` by default. On a notched 780×360 phone it drew in a 685×338 canvas offset from the screen edge, and anything past the canvas was clipped. Do layout maths on the ScreenGui's `AbsoluteSize`, not the device resolution.
- **Crosshairs need the true centre.** Give a crosshair or screen-centre marker its own ScreenGui with `ScreenInsets = None`, or it is offset by the cutout.
- **`TopbarSafeInsets` is lopsided.** Roblox's buttons take more room on the left, so a pill centred in that strip sat at 63% of a phone's width. For a top-centre widget, use `ScreenInsets = None` with `IgnoreGuiInset = true`, put Y at the middle of `GuiService.TopbarInset`, put X at the screen centre clamped inside `TopbarInset.Min.X..Max.X` (converted to the ScreenGui's canvas), and re-place on `TopbarInset` and size changes. If the widget is wider than the strip in its widest state, drop a chip rather than skip the clamp, or it slides under the top-left buttons. In first person on PC the mouse is locked, so a top-bar widget also needs a key.

### 7.4 Place by measurement, not by offset

On a crowded phone, a fixed offset that clears its neighbour at one size overlaps it at another. Read the neighbour's real bounds (`AbsolutePosition` and `AbsoluteSize`) and position against them. Re-run the placement while the element is visible: neighbours move with screen size, input mode and game state.

**`AbsolutePosition` is one shared space.** Measured in Studio with a 58 px top bar (`GetGuiInset()` = 0, 58): `AbsolutePosition` is always measured from below the top-bar inset, whatever `IgnoreGuiInset` is. A frame at `Position = (0, 11)` in a ScreenGui with `IgnoreGuiInset = true` reads `AbsolutePosition.Y = -47`, and that ScreenGui reads `AbsolutePosition = (0, -58)`. With `IgnoreGuiInset = false` the same frame reads 11 and sits at screen y 69. So screen-space Y is `AbsolutePosition.Y + GuiService:GetGuiInset().Y` in both cases, and elements in different ScreenGuis can be compared directly in `AbsolutePosition` space.

```luau
local GuiService = game:GetService("GuiService")

-- Screen-space top edge. AbsolutePosition is measured from below the top-bar
-- inset for every ScreenGui, so always add the inset.
local function screenTop(object: GuiObject): number
	return object.AbsolutePosition.Y + GuiService:GetGuiInset().Y
end

-- Keep `element` (a direct child of its ScreenGui, AnchorPoint.Y = 1) at least
-- `gap` pixels above `below`. Both are compared in AbsolutePosition space, which
-- every ScreenGui shares, then converted into the element's ScreenGui canvas.
local function keepAbove(element: GuiObject, home: UDim2, below: GuiObject, gap: number)
	local screen = element:FindFirstAncestorWhichIsA("ScreenGui")
	if not screen or not below.Visible then
		element.Position = home
		return
	end
	local limit = below.AbsolutePosition.Y - screen.AbsolutePosition.Y - gap
	local homeBottom = screen.AbsoluteSize.Y * home.Y.Scale + home.Y.Offset
	if homeBottom > limit then
		element.Position = UDim2.new(home.X, UDim.new(0, math.floor(limit)))
	else
		element.Position = home
	end
end
```

The same idea works sideways. When a bottom bar and a corner control would meet on a narrow screen, slide the bar toward the free side by exactly the overlap (bounded so it never enters the thumbstick zone), rather than shrinking everything.

**Custom touch buttons from the jump button.** Size and place custom action buttons from Roblox's own jump button, read at runtime, and show them only while `PreferredInput` is `Touch`. `PlayerGui.TouchGui` uses its own insets, so its canvas can start below the top bar (measured 685×280 on one phone) while a HUD ScreenGui with `DeviceSafeInsets` and `IgnoreGuiInset` is taller (685×338). Compare in `AbsolutePosition` space, or convert explicitly (for example `jump.AbsolutePosition.Y + hud.AbsoluteSize.Y - touchGui.AbsoluteSize.Y`). `TouchGui` can appear after your first layout, so re-fit on `PlayerGui.ChildAdded` for `TouchGui` and whenever `PreferredInput` becomes `Touch`. Details: `roblox-input`.

### 7.5 Overlap comes from state combinations

Screens rarely overlap in their default state. They overlap when a feature shows two elements together for the first time: a held weapon's touch button plus the out-of-round menu, a spectate bar plus the hotbar, a toast plus a timer warning. For each feature:

- List the HUD states it can appear in (lobby, alive, eliminated, spectating, results, a window open) and which elements show in each.
- Check every pair that can be visible at the same moment, on the smallest phone with touch controls showing. Measure rendered bounds of adjacent controls and confirm every action stays reachable.
- After adding a state, re-run the device matrix (§9) for the states it touches.

### 7.6 Windows, text and touch targets on small screens

- **Fit windows to the usable area:** the viewport minus the top inset and any reserved columns.
- **Phone windows sit under the top bar.** On a landscape phone the top bar takes about 58 px, so a usable window cannot sit beside it, and sliding a centred window sideways to clear Roblox's buttons reads as a layout bug. Put the window's top under `TopbarInset.Max.Y` (plus any icon overhang), centre it on the canvas width, and hide the HUD it would collide with while open. `GuiService.TouchControlsEnabled = false` hides the thumbstick and jump button; restore it on close and on cleanup. Dim the rest with a scrim, and keep money visible (for example in the window header). A refresh loop that sets `Visible` on every pass undoes a one-off hide, so fold the new condition into that loop.
- **Measure rendered sizes:** one scale-to-fit factor shrinks every target and font together. A 900×580 window fitted to an 844×390 phone renders at roughly 0.6×, so a 58-pixel close button becomes about 34 pixels and 18-pixel text about 11. Check `AbsoluteSize` and rendered text at the smallest supported screen.
- **Reflow instead of shrinking:** use fewer grid columns, move a side preview into a detail view, scroll, or put rarely used options one level deeper. Shrink decoration before tap targets.
- **Size text from real measurements:** `TextService:GetTextBoundsAsync` with `GetTextBoundsParams.Font` set to the label's `FontFace`; the legacy `GetTextSize` takes a `Font` enum and can mis-size `FontFace` text. Leave room for `UIStroke`.

## 8. Console and TV

From Roblox's console guidelines and the `GuiService` reference:

- **Design for 8–10 feet away:** develop for lower resolutions first, scale with relative sizes and `UISizeConstraint`, and use `GuiService.ViewportDisplaySize == Enum.DisplaySize.Large` (most TVs) to scale text and targets up.
- **Keep content in the TV-safe area:** some TVs crop the edges, so inset interactive and important UI from every edge.
- **Don't use `GuiService:IsTenFootInterface()` to detect a console.** It is deprecated and hardcoded to `true` on consoles. Use `ViewportDisplaySize` for layout and `UserInputService.PreferredInput` for controls.
- **Disable the chat window** for console games.
- **Navigation:** every element must be reachable with the four directions plus select and back, and key actions should take only a few presses.
- **TV remotes (micro gamepads):** a TV remote gives a D-pad, a centre button and a back button, nothing more. Make every item reachable by four directions, put the primary action on centre (it arrives as `ButtonA`), use back (`ButtonB`) consistently, preserve focus across open and close, and use large controls. Detection and bindings: `roblox-input`.
- **Button prompts must match the controller:** `roblox-input` covers `GetStringForKeyCode`, `GetImageForKeyCode` and `InputActionLabel`.
- **Accessibility:** respect `GuiService.PreferredTextSize` and `GuiService.ReducedMotionEnabled`.
- **Content maturity:** console releases need content maturity information.

## 9. Cross-device verification

Studio's **Device Simulator** (formerly Device Emulator; the new toolbar version is a beta enabled under **File > Beta Features > New Device Simulator**) sits above the 3D viewport in edit and play mode and switches the screen, pixel density, on-screen keyboard and platform your experience believes it is running on. Phones are grouped Flagship, Mid-range and Entry level; you can also create custom devices. **Display scaling** chooses whether the viewport preserves pixel count or physical size; calibrate once to judge tap targets at physical size. **Controller Emulator** (Device Simulator toolbar or the Emulation tab) emulates Xbox and PlayStation pads, VR, handhelds and, with an Android TV device selected, a TV Remote. Selecting a console or TV device switches the emulator to the matching controller. Roblox's built-in `rbx-device-simulator-lua` Studio skill can drive presets and captures for an agent (`roblox-studio-mcp`).

A practical matrix for every UI change:

- smallest supported phone (667×375 class) with touch controls;
- a mid-range Android phone (about 780×360) and a current iPhone (about 844×390);
- a tablet (1024×768 or 960×600);
- desktop 1920×1080 with mouse;
- console at 1080p and 4K with an Xbox controller, then a PlayStation controller; Android TV with the TV Remote.

Practical notes:

- **Prefer device presets to raw resolution overrides.** Confirm `UserInputService.PreferredInput` is `Touch` before judging a touch layout.
- **Set the device before Play.** UI code that reads `TouchEnabled` once at load keeps the desktop layout when the simulator is switched mid-session. That is your code, not a simulator bug, but restart the playtest with the device set first before judging it.
- **Measure, then look.** Read `AbsolutePosition`/`AbsoluteSize` of the elements that could collide, then take screenshots to judge readability.
- **Test the states, not just the screen** (§7.5): open a window, get eliminated, spectate, show two toasts, open chat, and focus a text box so the on-screen keyboard is up.
- **Test phones at Entry-level density,** and use physical-size mode to judge tap targets.
- **Check what the simulator can't fake:** a real phone (thumb reach, the notch) and a real TV (overscan, sofa distance).

Also test a long localized string, a missing or delayed asset, respawn and reopening, and low frame rate while a list updates.

## 10. Custom loading flow

1. Create the replacement UI from a `LocalScript` in `ReplicatedFirst` before calling `RemoveDefaultLoadingScreen()`.
2. Treat `game:IsLoaded()` and `game.Loaded` as DataModel readiness, not proof that every asset is ready.
3. Use `ContentProvider:PreloadAsync()` only for a bounded critical set (loading-screen images, key menu art, the spawn area), with timeout and fallback. Roblox's performance guide warns that over-preloading lengthens load times.
4. Gate controls and the first playable state explicitly. Do not move the character from the client as a loading lock.
5. Restore changed controls, CoreGui state, camera state and temporary connections on success, timeout, cancellation and respawn.

`PreloadAsync`'s list parameter is named `contentIdList`, and its callback reports each asset's content string and `Enum.AssetFetchStatus`. Its docs describe instances; field measurements show content-ID strings are accepted too (one project warmed sounds by id and cut start-up cost from 19 ms to 1.3 ms instead of creating a throwaway instance per take). Use instances when you need a per-instance status tied to an existing object. For audio, the string-form status reported `Failure` while the sound loaded fine (`roblox-audio`), so confirm with `Sound.IsLoaded` or `TimeLength`. A failed or moderated image silently renders as nothing; check each `AssetFetchStatus`.

## 11. Existing style, contrast and visual verification

Follow the project's existing components, typography roles, colors, spacing and interaction states. Do not impose a genre palette or invent a new design system for one screen. If there is no art direction, make the smallest readable provisional choice and show it to the owner; a working instance tree is not proof the UI looks right.

**Contrast helpers (`Color3`):** `Color3:GetLuminance()` returns WCAG 2.1 relative luminance (0–1); `a:GetContrastRatio(b)` returns the WCAG contrast ratio (1–21, symmetric); `background:GetContrastingColor(...)` returns whichever candidate has the highest contrast (with no arguments it picks between black and white, ties going to black). Use them to choose readable label colors over dynamic backgrounds (team colors, rarity colors) instead of hand-picking.

```luau
-- Pick a readable text color for any rarity background.
local function labelColorFor(background: Color3): Color3
	return background:GetContrastingColor(Color3.new(1, 1, 1), Color3.fromRGB(20, 20, 20))
end

local ratio = Color3.fromRGB(255, 200, 0):GetContrastRatio(Color3.new(1, 1, 1))
-- WCAG AA asks for 4.5:1 for body text; check before shipping a pale-on-pale label.
```

Test the actual screen over bright and dark game scenes, not only a blank Studio canvas. Check clipping, contrast, gameplay visibility, and each rendered state (active, selected, disabled, purchase pending). Hover is not available on every device; focus and touch must still work. Check `GuiService.ReducedMotionEnabled` before adding motion-heavy feedback.

## 12. Shared styling and flex, when needed

For an existing stylesheet-based project, extend its tokens and rules rather than setting conflicting per-instance properties. Roblox `StyleSheet` rules attach to a UI tree with `StyleLink`; `StyleQuery` can adapt to size, preferred input, text size or reduced motion. For a one-off UI, direct properties may be simpler. See the [official styling guide](https://create.roblox.com/docs/ui/styling).

Flex is built into `UIListLayout` (`HorizontalFlex` or `VerticalFlex`); `UIFlexItem` customizes a child. There is no `UIFlexLayout` instance. Use flex only when a row or column needs flexible space. If items spread apart unexpectedly, inspect the layout's flex alignment before adding offsets. Keep `SortOrder = LayoutOrder` and set each child's `LayoutOrder` when order matters. See the [official list/flex guide](https://create.roblox.com/docs/ui/list-flex-layouts).

## 13. UI checklist

- [ ] Containers use layout objects and constraints instead of scattered pixel positions.
- [ ] Text growth, clipping, and scrolling have an explicit policy.
- [ ] Designed on the smallest supported landscape phone first; checked on the device matrix (§9) in every state the change touches.
- [ ] Interactive UI sits in `CoreUISafeInsets` (or a deliberate alternative) and clears the thumbstick zone, jump button and top bar by measurement in `AbsolutePosition` space.
- [ ] The interface works with touch, mouse, keyboard, gamepad and, for TV, a remote's D-pad, centre and back.
- [ ] Gamepad: visible entry focus, a selection boundary, layered Back, and focus restored after rebuilds and on close.
- [ ] Rotated or rounded containers that must clip use a `CanvasGroup`.
- [ ] Text colors pass a contrast check over their real backgrounds.
- [ ] Component-level checks (busy states, debounced actions, owned lifetimes): `roblox-gui-components`.
