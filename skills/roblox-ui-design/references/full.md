## Full Reference

> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

## Design Philosophy

This skill uses a simulator-based visual language by default: boxed, bold, toy-like interfaces with semantic color blocking, icon-led navigation, and dense cards. That default fits the common Roblox game made with AI. It is not a universal visual requirement.

When an existing project UI, screenshot, theme, or component library is available, its visual language takes priority. Preserve its palette, font roles, casing, border/radius language, depth treatment, icon treatment, spacing rhythm, and action colors. Do not import simulator conventions that conflict with it. Borrow style tokens and vocabulary, not broken geometry. Existing style answers “how it looks”; the core rules below answer “how it is organized.”

The visual language exists because Roblox UI overlays a moving 3D world, players need to parse information instantly, and touch targets must be large. Thin borders, subtle shadows, and generous whitespace can fail in this context, but an existing project may intentionally use a different treatment. Apply the project’s style while preserving hierarchy, density, containment, and readability.

## Default Visual Specs

These 1080p values are simulator defaults inferred from shipped game screenshots, not official specifications. An existing project’s measured tokens override them.

### Core UI Principles

Use these regardless of visual style:

1. **Identify the screen job.** Choose single-focus, collection, compare, HUD, list, or another topology from the content. Do not force every task into a centered modal.
2. **Establish focal hierarchy.** One object, state, or action gets the strongest contrast and scale. Secondary information becomes quieter through size, value, grouping, or position.
3. **Let content own dimensions.** The complete useful stack determines panel size. Auto-sized panels include title, content, and actions. Do not stretch a shell to fill the viewport or add metadata to occupy space.
4. **Give each flow one owner.** A `UIListLayout`, `UIGridLayout`, or explicit shared-column calculation owns repeated content. Do not mix a layout object with guessed child Y offsets.
5. **Check bounds mathematically.** Sum child widths, gaps, padding, borders, and minimum sizes before assigning a row or grid. Keep strokes and rear backings inside the intended visual bounds.
6. **Align related content as a unit.** Use parent-owned layout, matching anchors, and fixed icon slots. Do not independently offset an icon, label, and value until they appear centered by accident.
7. **Make state legible.** Active, available, locked, completed, and disabled states need differences in text, value, structure, or iconography. Color may support state but must not be the only signal.
8. **Verify at the target viewport.** Inspect the actual render for clipping, overflow, empty space, unreadable type, and hierarchy. A valid instance tree is not proof of a good composition.

### Existing UI Condition

When the task modifies or extends an existing project UI:

- Inspect the existing screen or component source before designing. Record its surface colors, typography roles, casing, corner and border language, depth, icon treatment, spacing rhythm, and action hierarchy.
- Reuse existing theme tokens, constructors, component names, and layout conventions when they are available. Do not create a second visual system for one new screen.
- Preserve intentional identity, including unusual but consistent choices. Do not “improve” a style into the simulator default just because it is familiar.
- Preserve the style language, not accidental geometry. Fix overflow, weak hierarchy, broken alignment, and oversized shells using the core principles above.
- If the style source is incomplete, infer only the missing tokens from the nearest existing components. Fall back to the simulator default only for genuinely unspecified decisions.

### Borders

In the simulator default, thick dark outlines are the primary depth mechanism. An existing project may use a different border language.

- Major panel outline: 4-6px dark charcoal or black
- Card borders: 3-5px
- Outlined text stroke: 2-4px depending on text size
- Border color: dark charcoal `#1A1A1A` to `#2D2D2D`, not pure black

Test borders over: sky, grass, dark interior, particle effects, avatar, bright event lighting. A border that looks heavy on a blank canvas is usually correct during gameplay.

### Corner Radius

Use radius hierarchy, not one value everywhere:

- Major modal: 6-12px (boxy)
- Inventory card: 4-10px
- Compact icon button: 8-12px
- Pill CTA or search field: half the component height
- Badge: circular
- Combat/action tab: optionally angular or slanted

Applying the same radius to every nested element erases hierarchy. A square outer shell with rounded inner cards (Blox Fruits) is stronger than uniform 16px rounding everywhere.

### Typography

Two font roles: one expressive display face, one neutral body face.

**Display fonts** (titles, headers, prices):
- `FredokaOne`: simulator, cute, collection game. Players associate it with simulator games.
- `Oswald`: action, horror, tense, condensed. Community-identified in DOORS.
- `SourceSans` or `SourceSansBold`: neutral alternative

**Body fonts** (quantities, descriptions, controls):
- `BuilderSans`: current platform default, safe choice
- `Nunito`: friendly alternative for casual games

**Gotham is deprecated.** Roblox introduced Builder Font in 2024 and deprecated Gotham and Arial. Do not use Gotham for new UI unless matching an existing Gotham-based interface.

Typography treatment:
- Bold or extra-bold weight for display
- White or very light fill
- Outline the title and primary CTA; keep body labels and secondary values clean
- Short labels, not paragraphs
- Centered text for titles and button labels
- Left-aligned for list item names

```luau
-- Outlined title text
local title = Instance.new("TextLabel")
title.Font = Enum.Font.FredokaOne
title.TextSize = 36
title.TextColor3 = Color3.fromRGB(255, 255, 255)
title.Text = "PET SHOP"

local stroke = Instance.new("UIStroke")
stroke.Color = Color3.fromRGB(26, 26, 26)
stroke.Thickness = 3
stroke.Parent = title
```

### Icon Slots and Accent Variety

Text-only stat rows read like forms. Reserve a 40-48px icon tile at the left when the screen needs it. When no verified art asset exists, use a temporary emoji/glyph `TextLabel` inside the tile; do not invent asset IDs. Keep placeholders quiet unless they represent the active state.

Use one dominant accent and at most two supporting accents per screen. Accents belong on the primary action, active state, or a small icon/edge cue. Keep repeated cards neutral by default; do not color every outline or turn rarity into a rainbow. Color must reinforce hierarchy, not replace it.

### Focus and Density

Give one object, state, or action the strongest contrast and scale. Secondary items should be smaller, quieter, or grouped. Size panels around the complete useful content; do not stretch a shell to fill the viewport or add metadata just to occupy space. Empty slots and secondary values must not compete with the focal interaction.

### Color

Color is semantic, not decorative. Each strong color has a job:

| Role | Color | Example |
|------|-------|---------|
| Base/neutral | Dark charcoal or brown | Panel background |
| Buy/claim/available | Green | Purchase buttons |
| Close/sell/danger | Red | Close button, delete |
| Premium/featured | Yellow or orange | VIP, featured items |
| Navigation/currency | Blue | Category tabs, coins |
| Rare/special/luck | Purple or rainbow | Rarity cards, special items |

Use a small semantic palette. One dominant accent and up to two supporting accents are usually enough; the base surface stays neutral. Saturation goes on the primary action or active state, not on every card outline, label, and border.

```luau
local Theme = {
    Base      = Color3.fromHex("2D2A26"),  -- dark warm neutral
    Border    = Color3.fromHex("1A1A1A"),  -- dark charcoal
    Green     = Color3.fromHex("3DBB4A"),  -- buy/claim
    Red       = Color3.fromHex("D94040"),  -- close/danger
    Yellow    = Color3.fromHex("F5C531"),  -- premium/featured
    Blue      = Color3.fromHex("3D7BCC"),  -- navigation/currency
    Purple    = Color3.fromHex("9B4DD9"),  -- rare/special
    Text      = Color3.fromRGB(255, 255, 255),
    TextDim   = Color3.fromRGB(180, 180, 180),
}
```

### Depth Model

Pick one depth approach, do not stack them all:

**Option A: Cartoon depth (Pet Sim style)**
- Dark outline on structural surfaces and primary controls
- Rear backing shares the foreground corner radius or stays inset
- Small offset shadow (2-4px down/right)
- Lighter inner edge or top highlight
- Stud texture on structural elements
- No glass blur, no neon glow

**Option B: Rarity depth (Blox Fruits style)**
- Colored border only when rarity is a meaningful state
- Prefer solid fill; use a gradient only when the art direction explicitly calls for it
- Subtle glow only on rare items
- Illustrated item art carries visual interest
- No soft ambient shadows

**Option C: Graphic flat (DOORS style)**
- Thick border, solid fill, no shadow
- High contrast duotone palette
- Flat pictogram icons
- Depth comes from overlapping and scale, not effects

```luau
-- Native cartoon depth: rear backing + outlined foreground surface.
local backing = Instance.new("Frame")
backing.Size = UDim2.new(1, 4, 1, 4)
backing.Position = UDim2.fromOffset(3, 3)
backing.BackgroundColor3 = Theme.Border
backing.BorderSizePixel = 0
backing.Parent = parent

local card = Instance.new("Frame")
card.Size = UDim2.new(1, 0, 1, 0)
card.BackgroundColor3 = Theme.Base
card.BorderSizePixel = 0
card.Parent = parent

local border = Instance.new("UIStroke")
border.Color = Theme.Border
border.Thickness = 4
border.Parent = card
```

### Stud Texture

Stud texture makes flat panels look like Roblox bricks. It is the cheapest way to connect UI to the game world.

**Where to apply:**
- Header bar
- Outer frame
- Navigation rail
- Selected state highlight

**Where NOT to apply:**
- Every single panel and button (creates visual noise)
- Content cards (keep them quiet)
- Text labels

**How to create:**
Use a tiled stud texture image as an `ImageLabel` background. Avoid a gradient unless the supplied art direction explicitly uses one. Keep stud contrast subtle: 5-12% lighter or darker than the base fill.

```luau
-- Stud texture header
local header = Instance.new("Frame")
header.Size = UDim2.new(1, 0, 0, 52)
header.BackgroundColor3 = Theme.Base

local studTexture = Instance.new("ImageLabel")
studTexture.Size = UDim2.new(1, 0, 1, 0)
studTexture.Image = "rbxassetid://0" -- replace with actual stud texture
studTexture.ScaleType = Enum.ScaleType.Tile
studTexture.TileSize = UDim2.new(0, 32, 0, 32)
studTexture.ImageTransparency = 0.88 -- very subtle
studTexture.BackgroundTransparency = 1
studTexture.Parent = header
```

Do not invent asset IDs. Use a verified asset, a procedural texture, or ask the user for a stud texture image.

### Density

Roblox UI is dense. Players need simultaneous access to currencies, inventory, shop, rewards, and gameplay. Sparse layouts feel unfinished.

**Desktop zoning:**
- Currencies and persistent status: screen edges (top, bottom corners)
- Hotbar or loadout: bottom of screen
- Category navigation: left rail of modal
- Item grid: center of modal
- Primary action (buy, claim, play): large, obvious, colored
- 3D world: visible around modal, not fully blocked

**Mobile zoning:**
- Reduce columns (2-3 instead of 4-5)
- Enlarge category controls and close button
- Consider full-screen modal instead of partial
- Explicit touch controls where desktop uses keys
- Respect `ScreenInsets.CoreUISafeInsets`

```luau
-- Responsive column count
local GuiService = game:GetService("GuiService")
local camera = workspace.CurrentCamera

local function getColumns(): number
    local vp = camera.ViewportSize
    if vp.X < 700 then return 2 end
    if vp.X < 1280 then return 3 end
    return 5
end
```

## Layout Pattern

### Choose Topology Before Components

The screen's job determines its shape. Do not start every interface with a wide modal, a left rail, and a grid.

| Screen job | Composition | Visual priority |
|---|---|---|
| Single-focus moment | Compact portrait panel, vertical stack | Focal object, then primary action |
| Collection | Wide panel, filters plus grid/list | Item imagery and scan rhythm |
| Compare/progression | Split panel, selection plus detail | Selected item and upgrade action |
| HUD | Edge-anchored zones around gameplay | Critical status and next action |

### Single-Focus Modal

Use this for egg hatching, daily rewards, opening crates, claim moments, and confirmations.

```
        +----------------------+
        |       TITLE          |
        |                      |
        |       [FOCAL]        |
        |                      |
        |    [ PRIMARY CTA ]   |
        |    [ secondary ]     |
        +----------------------+
```

- Make the panel compact and portrait-oriented. Size it around the stack, not a universal viewport percentage.
- Give the focal object the largest visual area. The title supports it; it does not become a full-width competing bar.
- Keep the primary action visually attached to the focal object. Put secondary actions below it and make them quieter.
- For one simple cost, put the cost in the primary CTA text or a compact sublabel. Do not add a separate currency row that competes with the action.
- Use one repeated gap scale. Do not hand-place each child with unrelated absolute Y offsets.
- Use `UIListLayout` for the stack or `UIGridLayout` for collections. Let one layout object own flow; use absolute positioning only for intentional overlays.
- A horizontal action row is optional. If used, its children must fit inside the available inner width; use a layout object instead of offsets that exceed the parent.
- The complete stack, including the actions, must determine the panel height. Do not bottom-anchor an auto-sized action group with a fixed negative offset.
- For an automatic-height modal, center with `AnchorPoint = Vector2.new(0.5, 0.5)` and `UDim2.fromScale(0.5, 0.5)`. Do not estimate the center with a hardcoded Y offset.
- Add `UISizeConstraint` or `UIAspectRatioConstraint` where the panel must remain bounded across display sizes.

```luau
-- Content-driven vertical flow. The panel shape follows this stack.
-- The complete stack drives the panel height. Do not anchor children from the bottom.
modal.Size = UDim2.new(0, 360, 0, 0)
modal.AutomaticSize = Enum.AutomaticSize.Y
modal.AnchorPoint = Vector2.new(0.5, 0.5)
modal.Position = UDim2.fromScale(0.5, 0.5)

local stack = Instance.new("Frame")
stack.Name = "ContentStack"
stack.Size = UDim2.new(1, 0, 0, 0)
stack.AutomaticSize = Enum.AutomaticSize.Y
stack.BackgroundTransparency = 1
stack.Parent = modal

local padding = Instance.new("UIPadding")
padding.PaddingLeft = UDim.new(0, 24)
padding.PaddingRight = UDim.new(0, 24)
padding.PaddingTop = UDim.new(0, 20)
padding.PaddingBottom = UDim.new(0, 20)
padding.Parent = stack

local flow = Instance.new("UIListLayout")
flow.FillDirection = Enum.FillDirection.Vertical
flow.HorizontalAlignment = Enum.HorizontalAlignment.Center
flow.SortOrder = Enum.SortOrder.LayoutOrder
flow.Padding = UDim.new(0, 12)
flow.Parent = stack
```

### Collection Modal

- Title bar and close button may span the shell, but the content should use the available width.
- Add a rail only when there are real categories to navigate. Do not spend half the panel on navigation for three buttons.
- Use a dense grid when items are the product. Give imagery or a glyph placeholder the dominant area of each card; do not leave item slots as empty boxes.
- Keep filters and currencies secondary to the item grid.
- Size the grid and shell around the card content. Do not stretch a sparse grid into a large empty panel.

### Compare/Progression Panel

Use this for upgrades and loadouts. It is a compact compare surface, not a default web form.

- Use the project’s depth treatment. In the simulator default, keep the outer panel layered with rear backing, foreground surface, thick outline, and a distinct header or inset.
- Make each stat row a bounded surface or an intentional project-style separator. Do not let text float without enough contrast.
- Reserve a 40-48px icon tile at the left of each row. Use a temporary emoji/glyph placeholder when assets are unavailable.
- Give every row the same usable width and three columns after the icon: fixed stat label, fixed level/status, fixed action.
- Use `UIListLayout` for row flow, then explicit child widths for the shared columns. Ensure widths plus gaps fit the usable row width; do not let label length move the action button.
- Use one dominant accent and up to two supporting accents, repeated in icon tiles or row strips. Keep the panel base neutral.
- The action column is the strongest color block. Keep the close action separate and quieter than upgrades.

```luau
-- Shared compare columns. Every row uses the same widths.
local columns = { label = 132, level = 82, action = 104 }
local rowWidth = columns.label + columns.level + columns.action + 24
-- Build each row at rowWidth, then reuse the same child widths.
```

### Card Anatomy

Each item card contains exactly:
- One large item image or glyph placeholder (the focal child)
- One short name (1-3 words), using the display font
- One price or value
- One obvious action button (buy, equip, claim)
- Optional: a small rarity/active-state edge, quantity badge, or lock icon. Do not color the full outline by default.

Do not add explanatory paragraphs, secondary descriptions, or extra metadata. The player should parse each card in under 1 second.

```luau
local function createCard(parent, item)
    local card = Instance.new("Frame")
    card.Size = UDim2.new(0, 120, 0, 140)
    card.BackgroundColor3 = Theme.Base
    card.BorderSizePixel = 0
    card.Parent = parent

    -- Rarity border
    local border = Instance.new("UIStroke")
    border.Color = item.rarityColor or Theme.Border
    border.Thickness = 3
    border.Parent = card

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 8)
    corner.Parent = card

    -- Item image (largest element)
    local image = Instance.new("ImageLabel")
    image.Size = UDim2.new(0.8, 0, 0.5, 0)
    image.Position = UDim2.new(0.1, 0, 0.05, 0)
    image.BackgroundTransparency = 1
    image.Image = item.imageId
    image.Parent = card

    -- Item name (short, outlined)
    local name = Instance.new("TextLabel")
    name.Size = UDim2.new(1, 0, 0, 24)
    name.Position = UDim2.new(0, 0, 0.58, 0)
    name.BackgroundTransparency = 1
    name.Font = Enum.Font.FredokaOne
    name.TextSize = 16
    name.TextColor3 = Theme.Text
    name.Text = item.name
    name.TextScaled = true
    name.Parent = card

    local nameStroke = Instance.new("UIStroke")
    nameStroke.Color = Theme.Border
    nameStroke.Thickness = 2
    nameStroke.Parent = name

    -- Price
    local price = Instance.new("TextLabel")
    price.Size = UDim2.new(0.6, 0, 0, 20)
    price.Position = UDim2.new(0.05, 0, 0.78, 0)
    price.BackgroundTransparency = 1
    price.Font = Enum.Font.BuilderSans
    price.TextSize = 14
    price.TextColor3 = Theme.Yellow
    price.Text = item.price
    price.TextXAlignment = Enum.TextXAlignment.Left
    price.Parent = card

    -- Buy button
    local buy = Instance.new("TextButton")
    buy.Size = UDim2.new(0.3, 0, 0, 28)
    buy.Position = UDim2.new(0.65, 0, 0.78, 0)
    buy.BackgroundColor3 = Theme.Green
    buy.Text = "Buy"
    buy.Font = Enum.Font.BuilderSansBold
    buy.TextSize = 14
    buy.TextColor3 = Theme.Text
    buy.BorderSizePixel = 0
    buy.Parent = card

    local buyCorner = Instance.new("UICorner")
    buyCorner.CornerRadius = UDim.new(0, 6)
    buyCorner.Parent = buy

    local buyStroke = Instance.new("UIStroke")
    buyStroke.Color = Theme.Border
    buyStroke.Thickness = 2
    buyStroke.Parent = buy

    return card
end
```

## Interaction States

Every interactive element needs at minimum: resting, hover, pressed, selected, disabled/locked.

Commerce controls may also need: affordable vs unaffordable, claimable, newly unlocked, limited-time, notification present.

Roblox feedback is overt, not subtle:
- Button squash or scale (0.9-0.95x on press)
- Brightness or outline change
- Selected tab elevation
- Notification badges
- Reward bursts or currency fly-up
- Click, hover, and transition sounds

Motion should be fast: 80-180ms. No transition should delay shopping or claiming.

```luau
local TweenService = game:GetService("TweenService")
local GuiService = game:GetService("GuiService")

local function wireStates(button, defaultColor, pressedColor)
    local baseSize = button.Size

    button.MouseEnter:Connect(function()
        TweenService:Create(button, TweenInfo.new(0.1), {
            BackgroundColor3 = pressedColor,
            Size = UDim2.new(baseSize.X.Scale, baseSize.X.Offset * 1.05,
                            baseSize.Y.Scale, baseSize.Y.Offset * 1.05)
        }):Play()
    end)

    button.MouseLeave:Connect(function()
        TweenService:Create(button, TweenInfo.new(0.1), {
            BackgroundColor3 = defaultColor,
            Size = baseSize
        }):Play()
    end)

    button.MouseButton1Down:Connect(function()
        TweenService:Create(button, TweenInfo.new(0.08), {
            Size = UDim2.new(baseSize.X.Scale, baseSize.X.Offset * 0.92,
                            baseSize.Y.Scale, baseSize.Y.Offset * 0.92)
        }):Play()
    end)

    button.MouseButton1Up:Connect(function()
        TweenService:Create(button, TweenInfo.new(0.1), {
            Size = baseSize
        }):Play()
    end)
end

-- Reduced motion: check GuiService.ReducedMotionEnabled and skip tweens
```

## Mobile Adaptation

Mobile is not desktop scaled down. Change the layout:

- 2-3 columns instead of 4-5
- Full-screen modal instead of partial
- Larger category controls and close button
- Collapse icon rail into a horizontal scroll bar
- Touch actions where desktop uses keyboard
- `ScreenInsets.CoreUISafeInsets` for safe areas
- Minimum touch target: 48x48 pixels

```luau
screenGui.ScreenInsets = Enum.ScreenInsets.CoreUISafeInsets

-- Minimum touch size
local minSize = Instance.new("UISizeConstraint")
minSize.MinSize = Vector2.new(48, 48)
minSize.Parent = button
```

## Visual QA

### Test Over the Game World

A polished screenshot on a blank background is not a valid Roblox UI test. Check:

- [ ] UI is legible over sky, grass, dark interior, particles, and bright lighting
- [ ] Borders are visible against the 3D background
- [ ] Text outlines keep text readable over varied backgrounds
- [ ] Modal does not fully block critical gameplay view
- [ ] Bottom hotbar remains accessible under modals

### Test States

- [ ] Every button has resting, hover, pressed, selected, disabled
- [ ] Commerce buttons show affordable vs unaffordable
- [ ] Locked items have a clear locked state
- [ ] Notification badges appear where relevant
- [ ] No transition delays the player's next action

### Test Mobile

- [ ] 2-3 columns, not 4-5
- [ ] Close and buy buttons in thumb reach
- [ ] Safe areas respected
- [ ] No tiny text or micro-touch-targets

### Anti-Generic Audit

Before finalizing, check:

- [ ] Does this UI look like it belongs to a specific game, or could it be from any game?
- [ ] Is the radius the same on every nested element? (If yes, fix it)
- [ ] Are borders appropriate to the project style and readable over the 3D world?
- [ ] Is the layout dense enough, or does it feel empty for a Roblox game?
- [ ] Are colors semantic (green=buy, red=close) or just decorative?
- [ ] Are icons custom and consistent, or emoji/generic?
- [ ] Does the font match the game genre?
- [ ] Would a player recognize this game from its UI alone?

## What NOT to Do

- Same radius on every nested element (kills hierarchy)
- Thin or thick borders that conflict with the project style or disappear over the intended background
- Unstructured whitespace that leaves useful content floating
- Effects that conflict with the project style or substitute for hierarchy
- Emoji for navigation icons
- Decorative or inconsistent color without semantic meaning
- Unjustified sparse layout or paragraphs of explanatory text
- Glassmorphism, blur effects, neon glow without semantic meaning
- Gotham font for new UI (deprecated by Roblox 2024)
- Pure white on pure black (use off-white on dark charcoal/brown)
- Scaling desktop layout down to mobile without changing layout

## Source Notes

- Visual patterns, measurements, and color semantics: original synthesis from analysis of Pet Simulator 99, Grow a Garden, Blox Fruits, DOORS, Tower Defense Simulator, Adopt Me, and Blade Ball UI screenshots, DevForum discussions, and community UI pack analysis (2026-07)
- Adaptive design and accessibility guidance: [Roblox Creator Docs](https://create.roblox.com/docs/production/publishing/adaptive-design) (CC-BY-4.0)
- Font deprecation (Gotham/Arial, Builder Font introduction): verified against current Roblox creator docs, 2026-07
- UIShadow properties (BlurRadius, Offset, Transparency, Color, Spread): verified against [Roblox Creator Docs](https://create.roblox.com/docs/ui/styling) (CC-BY-4.0)
- Stud UI grammar, pack market analysis, and anti-clone guidance: original synthesis from BuiltByBit marketplace analysis and DevForum community discussions (2026-07)
