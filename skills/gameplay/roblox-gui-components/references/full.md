# roblox gui components: full reference

> Code examples are illustrative. Adapt them to your project and verify in Studio before production use.

This file covers the parts of a UI that hold state: windows and menus, shops and dialogs, HUD widgets, text entry, lists and grids, effects, reactive libraries and legacy migration. Where things go on the screen (safe areas, mobile-first layout, console and TV, gamepad focus) is in `roblox-gui`. Styling is deliberately neutral here: follow the project's existing look.

## 1. Text content

### Truncation and overflow policy

`TextWrapped` wraps text within the element; `TextTruncate` controls what happens when wrapped text still does not fit:

- `Enum.TextTruncate.None` (default): overflow is clipped silently.
- `Enum.TextTruncate.AtEnd`: replaces overflow with `...`, cutting at a word boundary where possible.
- `Enum.TextTruncate.SplitWord`: replaces overflow with `...` mid-word, using narrow cells better.

Truncation is per line: with wrapping on, it truncates the final visible line. A fixed-size inventory slot can use `TextWrapped = true` + `TextTruncate = AtEnd` so a long name degrades gracefully, while a heading uses `TextScaled` bounded by `UITextSizeConstraint`. `TextFits` tells you whether the current text overflows, and `MaxVisibleGraphemes` hard-limits displayed graphemes without reflowing. Localized strings run longer than English; test truncation with a long translated string.

### Changing text needs a fixed box

A chip whose text changes (a `m:ss` timer, a vote count, a currency total) needs a fixed width, or it resizes and wraps around its text every tick. Measure the widest expected value with `TextService:GetTextBoundsAsync` and size the chip for it. Measure any added count against an existing caption before placing it inside a slot.

### RichText is a rendering mode, not a data format

Enable `RichText` per object (`TextLabel`, `TextButton`, `TextBox`) and write markup into `Text` (`<b>`, `<i>`, `<font color="#FF7800">`, `<br/>`, escapes `&lt;`/`&amp;`). Two trust rules:

- Never enable `RichText` for strings containing player input or other untrusted text. Tags in such strings render as styling: a player can inject `<font color="...">` to imitate system messages. Escape (`&lt;`) or strip before display; store plain text and apply tags only at render time from trusted code.
- Localization strips rich-text tags from translated strings: re-apply tags to localized variants manually.

### Prices

Show Robux prices with the Robux icon rather than the text "R$". Observed in one project: built-in Roblox fonts render the private-use character U+E002 (`"\u{E002}"` in Luau) as the Robux icon in a `TextLabel`; confirm it renders in your chosen font. On world signs, put an `ImageLabel` with the icon before the number. Search the codebase for `R$` before shipping a shop. Price and policy rules: `roblox-monetization`.

## 2. Window and menu state machine

Most menu bugs are lifecycle bugs: a window that opens twice, a close tween that finishes after a reopen, focus left on a hidden button, the mouse still locked behind a shop. Give every window one controller with explicit states and route *every* open path (button, key, world prompt, server push, tutorial) through it.

```luau
local TweenService = game:GetService("TweenService")
local GuiService = game:GetService("GuiService")

type State = "Closed" | "Opening" | "Open" | "Closing"

local Window = {}
Window.__index = Window

export type Window = typeof(setmetatable({} :: {
	root: GuiObject,
	group: CanvasGroup,
	state: State,
	token: number,
	tween: Tween?,
	cleanups: { () -> () },
	returnFocus: GuiObject?,
	firstFocus: () -> GuiObject?,
	onOpen: (self: any) -> (),
}, Window))

function Window.new(root: GuiObject, group: CanvasGroup, firstFocus: () -> GuiObject?, onOpen: (any) -> ()): Window
	return setmetatable({
		root = root,
		group = group,
		state = "Closed" :: State,
		token = 0,
		tween = nil,
		cleanups = {},
		returnFocus = nil,
		firstFocus = firstFocus,
		onOpen = onOpen,
	}, Window)
end

-- Everything an open window creates (connections, temporary hides, input
-- grabs) registers an undo here, so one close path releases all of it.
function Window.own(self: Window, undo: () -> ())
	table.insert(self.cleanups, undo)
end

function Window._play(self: Window, transparency: number, done: () -> ())
	if self.tween then
		self.tween:Cancel() -- a reopen mid-close must not let the old tween finish
	end
	self.token += 1
	local myToken = self.token
	local tween = TweenService:Create(self.group, TweenInfo.new(0.15), { GroupTransparency = transparency })
	self.tween = tween
	tween.Completed:Connect(function(playbackState)
		if myToken == self.token and playbackState == Enum.PlaybackState.Completed then
			self.tween = nil
			done()
		end
	end)
	tween:Play()
end

function Window.open(self: Window)
	if self.state == "Open" or self.state == "Opening" then
		return -- idempotent: a second open path is a no-op, not a second window
	end
	self.state = "Opening"
	self.returnFocus = GuiService.SelectedObject
	self.root.Visible = true
	self.onOpen(self) -- fill content, register cleanups, place by measurement
	self:_play(0, function()
		self.state = "Open"
		GuiService.SelectedObject = self.firstFocus() -- a control visible right now
	end)
end

function Window.close(self: Window)
	if self.state == "Closed" or self.state == "Closing" then
		return
	end
	self.state = "Closing"
	for index = #self.cleanups, 1, -1 do
		self.cleanups[index]() -- undo in reverse order of acquisition
	end
	table.clear(self.cleanups)
	local back = self.returnFocus
	self.returnFocus = nil
	GuiService.SelectedObject = if back and back.Visible and back:IsDescendantOf(game) then back else nil
	self:_play(1, function()
		self.state = "Closed"
		self.root.Visible = false
	end)
end

return Window
```

Rules the controller enforces:

- **One owner, idempotent transitions.** A second `open()` while opening is a no-op; a `close()` mid-open cancels the open tween through the token, so a stale `Completed` can never flip state back.
- **Acquire through `own()`.** Anything the window changes outside itself is registered with its undo: a mouse release, `GuiService.TouchControlsEnabled = false`, a hidden HUD element, a camera mode, a connection. Close runs the undos in reverse. This also covers destruction: call `close()` from the window's `Destroying` handler and from character respawn.
- **Restore only what the window owns.** When hiding other UI, record each element's prior state and restore only the state still owned by this mode. Do not blanket re-enable every screen, or a stale snapshot reopens a menu the player closed.
- **Layer, don't stack.** Keep a small stack of open windows so Back and a full-screen modal close the top one first. A menu key bound with `ContextActionService` should return `Pass` while *any* window is open, not only its own, or it swallows directional navigation inside another window (`roblox-input`).
- **Place before open, not at open-time cache.** A window that closes mid-tween and restores the position it had at open will reuse a stale position after a resize, so the next open lands off-screen. Compute the fitted position just before each open (`roblox-gui` §7.4). When you fix a fit or open rule in one window, grep every sibling window's fit and open code for the same rule in the same pass.
- **Release input in first person.** In a first-person or shift-lock game a window that needs clicks must free the mouse: show a `Modal` element (a visible `GuiButton` with `Modal = true`) and set `UserInputService.MouseIconEnabled = true`, because per-frame camera code can hide the icon again. Tie mouse behavior to one "any window open" state, not to each screen's own code (`roblox-input`).

### Outside-click close and modal covers

A full-screen invisible button that closes a menu on an outside click also catches clicks on the menu's empty areas, because a plain `Frame` lets input through. Set `Active = true` on the panel and keep the panel above the button (`ZIndex` under `ZIndexBehavior.Sibling`). A full-screen cover without a `Modal` button leaves the first-person mouse locked to the centre, so its cards cannot be clicked; put a `Modal` button under the cover.

### Exposure and timed UI

- For timed teaching, define when the instruction counts as seen. Accrue time only while it is actually visible; pause or cancel behind menus, death screens or other hiding states.
- Coalesce repeated updates for one countdown or event into one owned presentation rather than spawning a toast per tick. Bound simultaneous notices.
- When two overlays can show the same value at once (a vote bar's timer and a big countdown), let one widget own the number while both are up.
- Separate structural placement from input-specific affordances: update buttons, reticles and hints for the current input without moving navigation between opposite screen edges on hybrid input changes.

## 3. UI state and server state

The UI renders a snapshot or view model. It may request an action, but the server response determines the final display.

```luau
local HttpService = game:GetService("HttpService")

local state = {
	requestId = nil :: string?, -- non-nil while a purchase is pending or its outcome is unknown
	selectedId = nil :: string?,
	-- True once the timeout window closed without a correlated answer. The
	-- request stays recorded so the UI blocks a FRESH same-intent purchase
	-- that could double-spend one that may still have committed.
	unresolved = false,
}

local function render()
	local busy = state.requestId ~= nil
	buyButton.Active = not busy and not state.unresolved and state.selectedId ~= nil
	spinner.Visible = busy and not state.unresolved
end

local REQUEST_TIMEOUT = 8 -- seconds; bounds both the request and the refresh

buyButton.Activated:Connect(function()
	if state.requestId or not state.selectedId then
		return
	end
	state.requestId = HttpService:GenerateGUID(false)
	local myId = state.requestId -- token: only THIS purchase's timers act
	render()
	BuyItem:FireServer(myId, state.selectedId)

	-- Silence can mean a lost request OR a committed purchase whose response never arrived.
	task.delay(REQUEST_TIMEOUT, function()
		if state.requestId ~= myId then
			return -- resolved, or a newer purchase owns the state
		end
		statusLabel.Text = "Purchase outcome unknown. Refreshing..."
		RefreshPurchases:FireServer(myId) -- reconcile; never blind-retry
		task.delay(REQUEST_TIMEOUT, function()
			if state.requestId == myId then
				state.unresolved = true -- keep Buy blocked; reconciliation can still settle it
				statusLabel.Text = "Purchase outcome unknown. Check your inventory later."
				render()
			end
		end)
	end)
end)

PurchaseResult.OnClientEvent:Connect(function(id, ok, message)
	if id ~= state.requestId then
		return -- stale, duplicate, or already-reconciled result
	end
	state.requestId = nil
	state.unresolved = false
	statusLabel.Text = message
	render()
end)

-- Only a snapshot that echoes the pending request id settles it; an unrelated
-- background snapshot sent before the purchase committed must not.
InventorySync.OnClientEvent:Connect(function(snapshot)
	if state.requestId then
		if snapshot.reconciledRequestId ~= state.requestId then
			return
		end
		state.requestId = nil
		state.unresolved = false
	end
	statusLabel.Text = snapshot.ownsItem and "Purchased" or "Not purchased"
	render()
end)
```

Do not grant currency, inventory or ownership because a local button handler ran. The UI is an input surface, not a trust boundary. Correlate each request with an id, treat "no response yet" as a bounded unknown, and reconcile against authoritative state: a timed-out purchase may still have committed. In Server Authority projects, the client may render predicted state that is later corrected by rollback; keep durable displays tied to confirmed state and mark optimistic feedback as pending.

### What drives a HUD readout

- **One timer source.** Drive every on-screen countdown from the same authoritative timer the server uses (a replicated end time, not a local `for i = 20, 1, -1`). A death screen that counts down 20 seconds while the server respawns after 5 is a visible mismatch. Treat a transition (death feedback, spectate or lobby, next round) as a sequence and verify each step, not just that each screen exists.
- **Predicted readouts for the held item.** Status UI that reads server attributes only shows what the server publishes. For the item in hand (ammo, cooldown), drive the readout from the client's own predicted state, which also moves on the shot with no lag; keep server attributes for things that change while stowed. Test under simulated latency (`roblox-debugging`).
- **Keep screens ignorant of networking.** One pattern that scales: screens read a session object's values and call its actions, and one adapter maps replicated state and remotes into that session. It becomes the only UI file to change when a remote changes, and a sample adapter with made-up data lets every screen be previewed and clicked through offline.

## 4. Input and interaction

Use `Activated` for buttons when possible. Use `ContextActionService` for UI-only actions that map across keyboard, gamepad and touch. For gameplay-affecting input in a Server Authority project, use `InputAction`/`InputContext`. Use `UserInputService` for raw device details or gestures (`roblox-input`).

Every interactive control needs:

- a visible state for hover, press, disabled and focus where the platform supports it (gamepad focus as hover: `roblox-gui` §6);
- a clear label or tooltip;
- a route that works without precise mouse aiming;
- a debounced action that cannot issue duplicate requests while busy.

### Reliable hover (MouseEnter/MouseLeave pitfalls)

`GuiObject.MouseEnter`/`MouseLeave` only re-check hover when the mouse moves, so they can miss when content scrolls under a stationary cursor or occasionally fail to fire `MouseLeave`. For reliable hover, poll the cursor each frame and fire your own enter/leave on transitions (practitioner pattern; DevForum lead "REAL MouseEnter/MouseLeave for GuiObjects", https://devforum.roblox.com/t/real-mouseentermouseleave-for-guiobjects-they-actually-fire/3980310). Prefer `PlayerGui:GetGuiObjectsAtPosition()` over hardcoded offsets, and disconnect with the owning UI's lifetime.

`UserInputService:GetMouseLocation()` returns raw pixels that do not account for the GUI inset, while `GetGuiObjectsAtPosition()` expects coordinates after the inset (see `GuiService:GetGuiInset()`). Subtract the top-left inset before the hit test. This conversion follows the docs but has not been live-verified with every `IgnoreGuiInset`/`ScreenInsets` combination; measure on the real layout.

```luau
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local GuiService = game:GetService("GuiService")

local playerGui = Players.LocalPlayer:WaitForChild("PlayerGui")

local hovered = false
local connection = RunService.RenderStepped:Connect(function()
	local pos = UserInputService:GetMouseLocation()
	local inset = GuiService:GetGuiInset()
	local isOver = false
	for _, obj in playerGui:GetGuiObjectsAtPosition(pos.X - inset.X, pos.Y - inset.Y) do
		if obj == frame then
			isOver = true
			break
		end
	end
	if isOver ~= hovered then
		hovered = isOver
		if isOver then onEnter() else onLeave() end
	end
end)
-- window:own(function() connection:Disconnect() end)
```

### Tap versus drag on one slot

A slot that both taps and drags should take its tap from its own press and release, not `Activated`, which also fires after a drag. Start in the button's `InputBegan`, then read `UserInputService.InputChanged`/`InputEnded`, because the pointer leaves the button. A touch `InputObject` stays the same object across phases, so compare it by identity; a mouse press must be matched to `MouseMovement` by type. Work in deltas divided by the row's `UIScale`, and cancel any neighbour tween still writing `Position` when a slot becomes the dragged one. `UIDragDetector` handles many drag cases with no code (`roblox-input`). (Pattern from one project's notes; not yet verified in Play there.)

## 5. Text entry: focus lifecycle and mobile submit

A `TextBox` takes focus by click, tap or gamepad selection; only then does keyboard input reach it.

- `Focused` fires on gain (user input or `CaptureFocus()`); `FocusLost(enterPressed, inputThatCausedFocusLoss)` fires on loss. `:IsFocused()` and `UserInputService:GetFocusedTextBox()` check current state.
- `:CaptureFocus()` when a dialog opens; `:ReleaseFocus()` (optionally `:ReleaseFocus(true)` so the following `FocusLost` reports `enterPressed = true`) when something more important reclaims the keyboard. `CaptureFocus` only works on the client.
- `ClearTextOnFocus` defaults to true; set false for editable fields. `MultiLine` lets Enter insert newlines (so Enter alone never submits).
- Mobile/console: `ReturnPressedFromOnScreenKeyboard` may also fire. Route it and Enter-submission through one deduplicated submit path.

Allow one submission per edit attempt, reset that guard when a new attempt starts, and disable submission while a request is in flight. Test hardware Enter, on-screen Return, clicking away and programmatic release on real devices.

### Filtering and rate limits for player text

- Any text shown to other players (names, signs, notes) must pass `TextService:FilterStringAsync()` on the server before display, and saved text must be filtered again when displayed. A `TextBox`'s `Text` is unfiltered input. Never set `RichText = true` on a field that renders player text.
- **Chat must use `TextChatService`.** Any surface where players can hold a back-and-forth conversation in under 60 seconds counts as chat (`roblox-text-chat`). Rate-limit every other player-editable text surface that others can see to one submission per player per 60 seconds, enforced on the server.
- **Temporary text limits.** <!-- temporal: 2026-11 --> When Roblox detects conversations outside `TextChatService`, it limits the game for at least 24 hours (Creator Hub banner and an email to the owner): every feature that collects, filters and shows player text to others is limited to one submission per player per 60 seconds, and extra submissions display as ⏱️⏱️⏱️. Lifting it needs a fix plus a new version of the root place; it returns if the behavior continues.

## 6. Scrolling content

A `ScrollingFrame` needs a clear canvas policy. For a vertical list, put a `UIListLayout` inside it and use `AutomaticCanvasSize = Enum.AutomaticSize.Y`.

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
list.VerticalAlignment = Enum.VerticalAlignment.Top
list.Parent = scroll
```

Set `VerticalAlignment = Top` inside a `ScrollingFrame`: a list centred vertically makes the frame open scrolled to the middle or with content floating mid-canvas (observed). Open each scroll list once on a phone to check where it starts. Do not nest an automatically growing scroll region inside another unless the interaction is intentional and tested.

## 7. Grids of uniform cells (UIGridLayout)

When cells should wrap and every cell shares one size, use `UIGridLayout` (inventory slots, icon palettes, card walls):

```luau
local grid = Instance.new("UIGridLayout")
grid.CellSize = UDim2.new(0, 64, 0, 64)
grid.CellPadding = UDim2.new(0, 8, 0, 8) -- default {0,5},{0,5}
grid.SortOrder = Enum.SortOrder.LayoutOrder
grid.Parent = inventoryFrame
```

`UIGridLayout` controls child `Size` and `Position`; per-child sizes are ignored unless a `UIConstraint` on the child overrides `CellSize` (a `UISizeConstraint` with a larger `MinSize` spans several cells).

- `FillDirectionMaxCells`: max cells per row/column before wrapping (0 = fill the parent; 1 = a single column/row).
- `StartCorner` (`Enum.StartCorner`): which corner layout starts from.
- `FillDirection`: `Horizontal` (default) or `Vertical`.

Read-only `AbsoluteCellCount` and `AbsoluteCellSize` report the resolved layout. For tabular data where a mid-row break is wrong, use `UITableLayout`.

## 8. Pagination (UIPageLayout)

A `UIPageLayout` parented to a `GuiObject` stacks its children as full-size pages; only the current page is visible. Members: `JumpTo(page)`, `JumpToIndex(index)`, `Next()`, `Previous()`, and `CurrentPage`. Set `Circular = true` to wrap, and tune `TweenTime`, `EasingStyle`, `EasingDirection` (`Animated = false` for instant snaps). It provides no buttons:

```luau
local layout = Instance.new("UIPageLayout")
layout.TweenTime = 0.25
layout.EasingStyle = Enum.EasingStyle.Quad
layout.Parent = pageContainer

nextButton.Activated:Connect(function() layout:Next() end)
prevButton.Activated:Connect(function() layout:Previous() end)
layout.PageEnter:Connect(function(page)
	updateDots(page) -- one dot per child; highlight CurrentPage
end)
```

`PageEnter`/`PageLeave` fire on transitions and `Stopped` when a tween settles. `ScrollWheelInputEnabled`, `TouchInputEnabled` and `GamepadInputEnabled` control built-in panning.

## 9. Shops, dialogs and notifications

A practical flow:

1. render a neutral/loading state;
2. load or receive the data model;
3. allow one action at a time per row or transaction;
4. show a success, failure or retry state;
5. refresh from authoritative state after the action.

Do not close a purchase dialog merely because a prompt opened. Wait for the purchase or server result, and handle cancellation (`roblox-monetization`). For a refused request (not enough currency), refuse on the spot from the same shared rules the server uses; for an accepted one, wait for replicated state before playing the success feedback.

### Reward and payout feedback

- Show a payout's size with numbers, not object counts. One pattern: grow the coin count per burst with the log of the amount (roughly 5–20), roll the counter toward the real value, and show a `+X` beside it that sums every increase and fades a moment after the last.
- To hand world coins to the HUD, take each coin's viewport point with `Camera:WorldToViewportPoint` (which matches a ScreenGui with `IgnoreGuiInset = true`), fly a GUI coin on a curve into the icon, then punch the icon with a short `UIScale` tween.
- Effects shorter than a screenshot's latency need a repeatable capture: fire the signal in a loop, or freeze it (`roblox-studio-mcp`).

## 10. Animation, fades and cleanup

Tween a small set of properties and cancel or replace the previous tween when state changes (the controller in §2 does this with a token). Keep connections and tweens owned by the screen or row they affect. Destroy temporary UI when the owning feature closes. If an object can be destroyed before its tween completes, clean up through the owner's lifetime, not `Completed`.

- **Looping tweens park at the end.** A looping tween with `DelayTime` holds its object at the end position between loops, so decorative motion should start and end outside its clip frame.
- **Don't keep a whole screen inside a `CanvasGroup` just to fade it.** A `CanvasGroup` draws its content into a texture whose resolution the client's quality level caps, so text and images go soft (observed on desktop at lower quality). Hold the screen in a plain `Frame` and reparent it into a `CanvasGroup` only for the fade. A `UIGradient` on a `CanvasGroup` tints everything inside it; put a gradient on a backdrop frame inside the group instead.
- **Motion that is driven by one clock is testable.** Make reveal animations a function of elapsed time, so a capture at a given second is repeatable.
- Respect `GuiService.ReducedMotionEnabled`.

### Deprecated tween/transparency APIs and their replacements

- `TweenPosition`, `TweenSize`, `TweenSizeAndPosition` → `TweenService:Create()` on `Position`, `Size`, or both. `TweenService` is cancellable and has a `Completed` event; the old methods return only a boolean.
- `GuiObject.Transparency` → `BackgroundTransparency` and, for text objects, `TextTransparency` separately.
- Also deprecated on `GuiObject`: `Draggable` → `UIDragDetector`; `BackgroundColor`/`BorderColor` (BrickColor) → `BackgroundColor3`/`BorderColor3`; `FontSize` → `TextSize`.

```luau
-- Before: frame:TweenPosition(UDim2.fromScale(0.5, 0.2), Enum.EasingDirection.Out, Enum.EasingStyle.Quad, 0.25, true)
local TweenService = game:GetService("TweenService")
TweenService:Create(
	frame,
	TweenInfo.new(0.25, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
	{ Position = UDim2.fromScale(0.5, 0.2) }
):Play()
```

## 11. Effects: UIGradient and ParticleEmitter2D

### UIGradient shapes

`UIGradient.Type` (`Enum.GradientType`):

| Type | Shape | Notes |
|---|---|---|
| `Linear` | straight line | `Rotation` sets direction, `Offset` position |
| `Radial` | circle from the centre | radius is `(width + height) / 4`; `Rotation` has no effect |
| `Elliptical` | ellipse fitted to the element | radii are half the width and height; `Rotation` rotates the axes |
| `Conical` | clockwise sweep around the centre | `Rotation` sets the start angle |

`UIGradient.Scale` multiplies the gradient's extent (default 1 = the sequence spans the element once; below 1 compresses it, clamped at 0.001; above 1 shows only part). `TileMode` (`Enum.GradientTileMode`: `Clamp`, `Repeat`, `Mirror`) decides what fills the remaining area. Performance notes from the class page: avoid a `UIGradient` on objects with a text stroke, and avoid setting `Color` and `Transparency` often, because the sequence rebuilds; animate `Offset` or `Rotation` instead. `UIGradient` applies to `Frame`, text labels and buttons, image labels and buttons, `Path2D` and `ViewportFrame`, but not `ScrollingFrame` or `TextBox`.

```luau
local TweenService = game:GetService("TweenService")

-- A shine that sweeps by animating Offset, not by rewriting Color each frame.
local shine = Instance.new("UIGradient")
shine.Type = Enum.GradientType.Linear
shine.Rotation = 20
shine.Transparency = NumberSequence.new({
	NumberSequenceKeypoint.new(0, 1),
	NumberSequenceKeypoint.new(0.5, 0.4),
	NumberSequenceKeypoint.new(1, 1),
})
shine.Offset = Vector2.new(-1, 0)
shine.Parent = buttonFace

TweenService:Create(shine, TweenInfo.new(0.6), { Offset = Vector2.new(1, 0) }):Play()
```

### ParticleEmitter2D (beta)

<!-- temporal: 2026-11 --> `ParticleEmitter2D` emits 2D image particles from any `GuiObject` in a `ScreenGui`, `SurfaceGui` or `BillboardGui` (sparkles, bursts, glows). It is a beta ("UI Particles"); enable it in Studio's Beta Features before relying on it.

- **Emission:** `Enabled` plus `Rate` for continuous emission, or `Emit()` for a one-off burst (works while disabled). `Clear()` removes live particles; disabling only stops new ones.
- **Look:** `TextureContent`, `Color` (`ColorSequence` over lifetime), `Size` (`NumberSequence`, in offset units, representing half the rendered size), `Transparency`, `Squash`, `Blend` (0 normal, 1 additive), `Brightness`, `LightInfluence` (only for world UI: a `SurfaceGui`, or a `BillboardGui` without `AlwaysOnTop`).
- **Motion:** `Lifetime`, `Speed` (offset units per second), `Acceleration`, `Drag`, `Rotation`, `RotSpeed`.
- **Region:** `EmissionAngle`, `SpreadAngle`, `EmissionMode` (`Point` or `BoundingBox`), `EmissionOffset`, `EmissionSpread`.
- **Flipbooks:** `FlipbookLayout`, `FlipbookMode`, `FlipbookFramerate`, `FlipbookStartRandom`, `FlipbookBlendFrames`.
- **Other:** `LockedToParent` makes particles follow the parent; `TimeScale` (0–1) slows the effect (0 freezes it for a capture); `ZIndex` orders particles against other UI. Particles render above the parent's strokes and inset shadows.

Fade particles at the start and end of their lifetime to avoid popping. Treat a burst like any other owned effect: emit from the window controller and `Clear()` it on close.

## 12. Reactive UI libraries: scope, lifetime and lists

Native instances are the default. Some projects use a reactive library — [Fusion](https://elttob.uk/Fusion/0.3/) (0.3 line), [Vide](https://github.com/centau/vide), [Fluid](https://github.com/ffrostfall/fluid) (Vide-derived, MIT, v0.6.5) or React-Luau. Follow the project's existing choice. The rules below are library-neutral; per-library notes were verified against each repo (2026-10).

### Two lifetimes: session state vs screen state

- Session-length state (player stats, settings, currency display) lives in a module created once per session. Screens consume it; they do not own it.
- Per-open UI gets a fresh reactive scope/root each time it opens and is destroyed on close (or, if every screen is built once at join, its effects are paused and resumed by the window controller in §2).
- Putting mutable game state inside a screen's scope destroys it on the first close. Putting screen widgets in a session scope leaks them.

### Who cleans up what

- **Fusion (0.3):** constructors register destructors into the scope you pass; `doCleanup` destroys contents in reverse order. `Hydrate` inserts the target instance into the scope, so scope cleanup destroys a hydrated designer instance; clone it first if it must survive.
- **Vide:** `cleanup()` runs when the scope reruns or is destroyed. Instances only need to be unparented for memory to be freed, so a screen teardown should still unparent its root.
- **Fluid:** `root()`'s destructor tears down the reactive graph but does not destroy instances made by `create()` (verified in source). A screen opened in a loop leaks instances unless the tree root calls `cleanup(instance)` or unparents manually.
- For any library: name the single root teardown call per screen, and verify instances are actually removed on close.

### Derived state vs effects

- A value that is a pure function of other state should be derived (computed), not stored and written by three code paths that drift. Do not wrap constants in reactive machinery.
- Side effects do not belong in derived computations. Fusion's docs say recalculations "might be postponed or cancelled" and warn against computeds "for things like playing sound effects". Put side effects in explicit observers/effects, and expect their callbacks at surprising times (during teardown, before parenting).
- **Create effects in the component body.** Observed with Vide in one project: an effect, derive or spring created inside another effect, or inside a function passed as a child or property, was recreated on every update. The same project saw effects run twice in Studio under Vide's strict mode, so any effect that plays a sound or starts a tween needs its own guard against double runs.

### Keyed list rendering

- Per-entry scopes must be keyed by identity, not array position, or a reorder rebuilds rows that should have moved.
- Visible order comes from `LayoutOrder`; hash-map output order is arbitrary.
- Vide's `values()` errors on duplicate values under strict mode and warns duplicates "can cause unexpected behavior" otherwise. Deduplicate first.
- Exit animations need an explicit leaving-grace (delayed destruction while the tween plays), not an ad-hoc debounce.

### The reopen leak test

Any screen that opens and closes should pass this (original procedure):

1. Record the descendant count of the screen's container, and your own connection count, at baseline.
2. Open and close the screen 10 times in a loop.
3. Assert both return to baseline.
4. Repeat with the screen closed mid-animation and mid-network-response, the two states that expose teardown-order bugs.

```luau
-- Command-bar or test-runner check against the §2 controller.
local function leakCheck(window, container: Instance, cycles: number)
	local before = #container:GetDescendants()
	for _ = 1, cycles do
		window:open()
		task.wait(0.05) -- close mid-open on purpose
		window:close()
		task.wait(0.3)
	end
	local after = #container:GetDescendants()
	assert(after == before, `leaked {after - before} instances over {cycles} cycles`)
end
```

## 13. Building large UIs

- **Don't build rarely opened UI at join.** Measured in one project: an admin window of about 1.4k instances cost 55 ms built in place versus 24 ms built detached plus 17 ms to attach; setting `Parent` was 62% of build time. Build big windows outside the live ScreenGui and parent each once, on first open or spread over frames.
- **Spread `ViewportFrame` renders** over several frames, drawing the rest at once if the menu opens first.
- **Meshes in a `ViewportFrame` can take seconds to appear** after Play starts while their content is generated (observed). Wait before judging an empty preview broken. A kit image that never loads in your place may be restricted (`roblox-studio-mcp`); swap it for your own upload rather than debugging it forever.
- In Studio, a game-wide `DescendantAdded` probe inflates parenting cost further, so profile without one.

## 14. World and 3D media

### Selection outlines (SelectionBox)

`SelectionBox` renders a 3D box outline around its `Adornee` (from `InstanceAdornment`); it captures no input. Style with `LineThickness`, `Color3`, and `SurfaceColor3`/`SurfaceTransparency`. Prefer `Highlight` for fill/outline effects on non-primitive geometry.

```luau
local Players = game:GetService("Players")

local box = Instance.new("SelectionBox")
box.LineThickness = 0.05
box.Color3 = Color3.new(1, 1, 0)
box.SurfaceTransparency = 1
box.Parent = workspace

local mouse = Players.LocalPlayer:GetMouse()
mouse.Move:Connect(function()
	box.Adornee = mouse.Target -- nil when pointing at nothing
end)
```

### Decals (Decal, Texture)

`Decal` draws one image on one face of a part; `Texture` tiles it via `StudsPerTileU/V` and `OffsetStudsU/V`. The image property `Texture` (ContentId) is deprecated in favor of `ColorMap`/`ColorMapContent` but still works. `Transparency`, `Color3` and `Face` are runtime-writable. Uploaded images go through moderation; a failed review renders nothing, so ship a placeholder. Texture size limits: `roblox-building`.

```luau
local decal = Instance.new("Decal")
decal.Face = Enum.NormalId.Front
decal.Texture = "rbxassetid://699259085"
decal.Parent = part
```

### Video (VideoFrame, VideoPlayer)

`VideoFrame` is the simple path: parent it to a `SurfaceGui` and set `Video` to a video asset. Control with `Play()`, `Pause()`, `Looped`, `Volume`; wait for `IsLoaded` (or `Loaded`) before playing.

`VideoPlayer` is the wire-based source: set `VideoContent`, then wire it to a `VideoDisplay` in a `SurfaceGui` for visuals and an `AudioEmitter` for sound. It adds `PlaybackSpeed`, `TimePosition`, `LoadAsync()` and `PlayFailed`. Prefer `VideoFrame` unless you need the wire split.

```luau
local gui = Instance.new("SurfaceGui")
gui.Parent = screenPart

local video = Instance.new("VideoFrame")
video.Size = UDim2.fromScale(1, 1)
video.Looped = true
video.Video = "rbxassetid://5608359401"
video.Parent = gui

if not video.IsLoaded then
	video.Loaded:Wait()
end
video:Play()
```

## 15. Component checklist

- [ ] Every window has one controller; all open paths go through it; open and close are idempotent.
- [ ] Everything a window changes outside itself is released on close, destroy and respawn.
- [ ] Buttons expose disabled and busy states; actions are debounced and correlated with request ids.
- [ ] Server responses, not local optimism, determine durable state; countdowns read the authoritative timer.
- [ ] Player text is filtered on the server, rate-limited if others can see it, and chat goes through `TextChatService`.
- [ ] Lists keep focus and scroll position across rebuilds; scrolling lists start at the top.
- [ ] The reopen leak test passes, including close mid-animation.

## Community ecosystem (leads, not sources)

Top-sorted DevForum canon for UI libraries. Verify status in-thread before recommending.

- [TopbarPlus v3](https://devforum.roblox.com/t/topbarplus-v340-construct-topbar-icons-with-ease-customise-them-with-themes-dropdowns-captions-labels-and-more/1017485): the top-bar icon standard. Check its controller bindings (`roblox-gui` §6).
- [Iris](https://devforum.roblox.com/t/iris-immediate-mode-ui-library-based-on-dear-imgui/2302802): Dear ImGui-style immediate mode, good for debug tools, not player-facing polish.
- [Screen3D](https://devforum.roblox.com/t/screen3d-a-3d-ui-framework-that-just-works/3273671) (2024); [Text+](https://devforum.roblox.com/t/text-custom-fonts-advanced-control/3521684) (2025) custom fonts.
- [Satchel](https://devforum.roblox.com/t/satchel-open-source-modern-backpack-system/2451549): open-source inventory/backpack, study-grade.
- [Vanilla 3](https://devforum.roblox.com/t/vanilla-3-the-pragmatic-icon-set-for-roblox-studio/935745): an icon set.
- [ViewportFrame masking](https://devforum.roblox.com/t/viewportframe-masking/2964839) (2024), heavily cited for UI VFX.
- Design theory: [UI Design Starter Guide](https://devforum.roblox.com/t/ui-design-starter-guide/53461).
- [Mobile button placement tutorial](https://devforum.roblox.com/t/the-correct-way-to-design-mobile-buttons/2494558): collisions with default thumbstick/jump controls. Treat its coordinates as dated examples.
- Custom chat replacements (for example NovaChat) must still meet `TextChatService` rules and the May 2027 platform-integrated chat change (`roblox-text-chat`).
