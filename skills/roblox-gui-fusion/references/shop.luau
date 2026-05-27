--[[
    Shop Screen — Fusion 0.3
    Source patterns: VirtualButFake/fusion-components (MIT), dphfox/Fusion docs
    Ported to Fusion 0.3 scoped syntax.
    
    A complete shop interface with:
    - Scrollable item grid (UIGridLayout)
    - Item cards with icon, name, price
    - Purchase confirmation modal
    - Currency display header
    - Server-validated purchase flow via RemoteFunction
    
    ADAPT THIS:
    - Replace ITEMS table with your game's item data
    - Replace purchaseRemote with your RemoteFunction
    - Adjust grid CellSize and colors to match your theme
    - Add categories/tabs by wrapping the grid in a tab component
    
    Requires: Fusion 0.3 (wally: elttob/fusion@0.3.0)
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

-- Adjust this path to match your project structure:
-- Wally:    require(ReplicatedStorage.Packages.Fusion)
-- Custom:   require(game.ReplicatedStorage.Fusion)
-- Vendored: (default, from roblox-opencode setup)
local Fusion = require(ReplicatedStorage[".opencode"].vendor.fusion)
local scoped = Fusion.scoped
local peek = Fusion.peek
local Children = Fusion.Children
local OnEvent = Fusion.OnEvent

--------------------------------------------------------------------------------
-- Types
--------------------------------------------------------------------------------

export type ShopItem = {
    Id: string,
    Name: string,
    Price: number,
    Icon: string?, -- rbxassetid:// or placeholder color
    Owned: boolean?,
}

type ShopProps = {
    Items: Fusion.Value<{ ShopItem }>,
    Currency: Fusion.Value<number>,
    OnPurchase: (itemId: string) -> boolean, -- returns success
    Visible: Fusion.Value<boolean>,
}

--------------------------------------------------------------------------------
-- Theme constants
--------------------------------------------------------------------------------

local COLORS = {
    Background = Color3.fromRGB(20, 20, 28),
    Surface = Color3.fromRGB(30, 30, 42),
    SurfaceHover = Color3.fromRGB(40, 40, 55),
    Primary = Color3.fromRGB(80, 140, 255),
    PrimaryHover = Color3.fromRGB(100, 160, 255),
    Danger = Color3.fromRGB(220, 60, 60),
    Text = Color3.fromRGB(240, 240, 245),
    TextSecondary = Color3.fromRGB(160, 160, 175),
    TextMuted = Color3.fromRGB(100, 100, 115),
    Accent = Color3.fromRGB(255, 200, 50),
    Owned = Color3.fromRGB(60, 180, 80),
    Backdrop = Color3.fromRGB(0, 0, 0),
}

local FONT = {
    Title = Font.new("rbxasset://fonts/families/GothamSSm.json", Enum.FontWeight.Bold),
    Body = Font.new("rbxasset://fonts/families/GothamSSm.json", Enum.FontWeight.Medium),
    Small = Font.new("rbxasset://fonts/families/GothamSSm.json", Enum.FontWeight.Regular),
}

--------------------------------------------------------------------------------
-- Item Card component
--------------------------------------------------------------------------------

local function ItemCard(scope: Fusion.Scope, item: ShopItem, onClick: () -> ())
    local isHovering = scope:Value(false)

    return scope:New "TextButton" {
        Name = "ItemCard_" .. item.Id,
        BackgroundColor3 = scope:Spring(scope:Computed(function(use)
            return if use(isHovering) then COLORS.SurfaceHover else COLORS.Surface
        end), 30),
        AutoButtonColor = false,
        Text = "",
        LayoutOrder = 0,

        [OnEvent "Activated"] = onClick,
        [OnEvent "MouseEnter"] = function()
            isHovering:set(true)
        end,
        [OnEvent "MouseLeave"] = function()
            isHovering:set(false)
        end,

        [Children] = {
            scope:New "UICorner" { CornerRadius = UDim.new(0, 8) },
            scope:New "UIPadding" {
                PaddingTop = UDim.new(0, 8),
                PaddingBottom = UDim.new(0, 8),
                PaddingLeft = UDim.new(0, 8),
                PaddingRight = UDim.new(0, 8),
            },
            scope:New "UIListLayout" {
                FillDirection = Enum.FillDirection.Vertical,
                HorizontalAlignment = Enum.HorizontalAlignment.Center,
                Padding = UDim.new(0, 6),
                SortOrder = Enum.SortOrder.LayoutOrder,
            },

            -- Icon placeholder (colored frame or ImageLabel)
            scope:New "Frame" {
                Name = "IconFrame",
                BackgroundColor3 = COLORS.Background,
                Size = UDim2.new(1, 0, 0, 60),
                LayoutOrder = 1,
                [Children] = {
                    scope:New "UICorner" { CornerRadius = UDim.new(0, 6) },
                    if item.Icon then scope:New "ImageLabel" {
                        Image = item.Icon,
                        BackgroundTransparency = 1,
                        Size = UDim2.new(1, -8, 1, -8),
                        Position = UDim2.fromOffset(4, 4),
                        ScaleType = Enum.ScaleType.Fit,
                    } else nil,
                },
            },

            -- Item name
            scope:New "TextLabel" {
                Name = "ItemName",
                BackgroundTransparency = 1,
                Size = UDim2.new(1, 0, 0, 16),
                FontFace = FONT.Body,
                Text = item.Name,
                TextColor3 = COLORS.Text,
                TextSize = 13,
                TextTruncate = Enum.TextTruncate.AtEnd,
                TextXAlignment = Enum.TextXAlignment.Center,
                LayoutOrder = 2,
            },

            -- Price or "Owned" badge
            scope:New "TextLabel" {
                Name = "Price",
                BackgroundTransparency = 1,
                Size = UDim2.new(1, 0, 0, 14),
                FontFace = FONT.Small,
                Text = if item.Owned then "Owned" else tostring(item.Price),
                TextColor3 = if item.Owned then COLORS.Owned else COLORS.Accent,
                TextSize = 12,
                TextXAlignment = Enum.TextXAlignment.Center,
                LayoutOrder = 3,
            },
        },
    }
end

--------------------------------------------------------------------------------
-- Purchase Modal component
--------------------------------------------------------------------------------

local function PurchaseModal(
    scope: Fusion.Scope,
    visible: Fusion.Value<boolean>,
    selectedItem: Fusion.Value<ShopItem?>,
    onConfirm: () -> (),
    onCancel: () -> ()
)
    return scope:New "Frame" {
        Name = "PurchaseModal",
        BackgroundColor3 = COLORS.Backdrop,
        BackgroundTransparency = scope:Spring(scope:Computed(function(use)
            return if use(visible) then 0.4 else 1
        end), 25),
        Size = UDim2.new(1, 0, 1, 0),
        Visible = scope:Computed(function(use)
            return use(visible)
        end),
        ZIndex = 100,

        [Children] = {
            -- Centered dialog card
            scope:New "Frame" {
                Name = "DialogCard",
                AnchorPoint = Vector2.new(0.5, 0.5),
                Position = UDim2.fromScale(0.5, 0.5),
                Size = UDim2.new(0, 280, 0, 160),
                BackgroundColor3 = COLORS.Surface,

                [Children] = {
                    scope:New "UICorner" { CornerRadius = UDim.new(0, 12) },
                    scope:New "UIPadding" {
                        PaddingTop = UDim.new(0, 16),
                        PaddingBottom = UDim.new(0, 16),
                        PaddingLeft = UDim.new(0, 16),
                        PaddingRight = UDim.new(0, 16),
                    },
                    scope:New "UIListLayout" {
                        FillDirection = Enum.FillDirection.Vertical,
                        HorizontalAlignment = Enum.HorizontalAlignment.Center,
                        Padding = UDim.new(0, 12),
                        SortOrder = Enum.SortOrder.LayoutOrder,
                    },

                    -- Title
                    scope:New "TextLabel" {
                        BackgroundTransparency = 1,
                        Size = UDim2.new(1, 0, 0, 20),
                        FontFace = FONT.Title,
                        Text = "Confirm Purchase",
                        TextColor3 = COLORS.Text,
                        TextSize = 16,
                        LayoutOrder = 1,
                    },

                    -- Description
                    scope:New "TextLabel" {
                        BackgroundTransparency = 1,
                        Size = UDim2.new(1, 0, 0, 32),
                        FontFace = FONT.Small,
                        Text = scope:Computed(function(use)
                            local item = use(selectedItem)
                            if not item then return "" end
                            return `Buy {item.Name} for {item.Price} coins?`
                        end),
                        TextColor3 = COLORS.TextSecondary,
                        TextSize = 14,
                        TextWrapped = true,
                        LayoutOrder = 2,
                    },

                    -- Button row
                    scope:New "Frame" {
                        BackgroundTransparency = 1,
                        Size = UDim2.new(1, 0, 0, 36),
                        LayoutOrder = 3,
                        [Children] = {
                            scope:New "UIListLayout" {
                                FillDirection = Enum.FillDirection.Horizontal,
                                HorizontalAlignment = Enum.HorizontalAlignment.Center,
                                Padding = UDim.new(0, 12),
                                VerticalAlignment = Enum.VerticalAlignment.Center,
                            },

                            -- Cancel
                            scope:New "TextButton" {
                                Name = "CancelBtn",
                                BackgroundColor3 = COLORS.Background,
                                Size = UDim2.new(0, 100, 0, 32),
                                FontFace = FONT.Body,
                                Text = "Cancel",
                                TextColor3 = COLORS.TextSecondary,
                                TextSize = 14,
                                AutoButtonColor = false,
                                [OnEvent "Activated"] = onCancel,
                                [Children] = { scope:New "UICorner" { CornerRadius = UDim.new(0, 6) } },
                            },

                            -- Confirm
                            scope:New "TextButton" {
                                Name = "ConfirmBtn",
                                BackgroundColor3 = COLORS.Primary,
                                Size = UDim2.new(0, 100, 0, 32),
                                FontFace = FONT.Body,
                                Text = "Buy",
                                TextColor3 = COLORS.Text,
                                TextSize = 14,
                                AutoButtonColor = false,
                                [OnEvent "Activated"] = onConfirm,
                                [Children] = { scope:New "UICorner" { CornerRadius = UDim.new(0, 6) } },
                            },
                        },
                    },
                },
            },
        },
    }
end

--------------------------------------------------------------------------------
-- Shop Screen (main export)
--------------------------------------------------------------------------------

local function ShopScreen(props: ShopProps)
    local scope = scoped(Fusion)

    local selectedItem: Fusion.Value<ShopItem?> = scope:Value(nil)
    local modalVisible = scope:Value(false)

    local screenGui = scope:New "ScreenGui" {
        Name = "ShopScreen",
        ResetOnSpawn = false,
        IgnoreGuiInset = true,
        Enabled = props.Visible,
        DisplayOrder = 10,
        Parent = Players.LocalPlayer:WaitForChild("PlayerGui"),

        [Children] = {
            -- Main container
            scope:New "Frame" {
                Name = "Container",
                BackgroundColor3 = COLORS.Background,
                Size = UDim2.new(1, 0, 1, 0),

                [Children] = {
                    scope:New "UIPadding" {
                        PaddingTop = UDim.new(0, 60), -- below top bar
                        PaddingBottom = UDim.new(0, 12),
                        PaddingLeft = UDim.new(0, 16),
                        PaddingRight = UDim.new(0, 16),
                    },
                    scope:New "UIListLayout" {
                        FillDirection = Enum.FillDirection.Vertical,
                        Padding = UDim.new(0, 12),
                        SortOrder = Enum.SortOrder.LayoutOrder,
                    },

                    -- Header: title + currency
                    scope:New "Frame" {
                        Name = "Header",
                        BackgroundTransparency = 1,
                        Size = UDim2.new(1, 0, 0, 32),
                        LayoutOrder = 1,
                        [Children] = {
                            scope:New "TextLabel" {
                                BackgroundTransparency = 1,
                                Size = UDim2.new(0.5, 0, 1, 0),
                                FontFace = FONT.Title,
                                Text = "Shop",
                                TextColor3 = COLORS.Text,
                                TextSize = 22,
                                TextXAlignment = Enum.TextXAlignment.Left,
                            },
                            scope:New "TextLabel" {
                                BackgroundTransparency = 1,
                                AnchorPoint = Vector2.new(1, 0),
                                Position = UDim2.fromScale(1, 0),
                                Size = UDim2.new(0.5, 0, 1, 0),
                                FontFace = FONT.Body,
                                Text = scope:Computed(function(use)
                                    return tostring(use(props.Currency)) .. " coins"
                                end),
                                TextColor3 = COLORS.Accent,
                                TextSize = 16,
                                TextXAlignment = Enum.TextXAlignment.Right,
                            },
                        },
                    },

                    -- Scrollable item grid
                    scope:New "ScrollingFrame" {
                        Name = "ItemGrid",
                        BackgroundTransparency = 1,
                        Size = UDim2.new(1, 0, 1, -44),
                        LayoutOrder = 2,
                        AutomaticCanvasSize = Enum.AutomaticSize.Y,
                        ScrollingDirection = Enum.ScrollingDirection.Y,
                        ScrollBarThickness = 4,
                        ScrollBarImageColor3 = COLORS.TextMuted,
                        CanvasSize = UDim2.new(0, 0, 0, 0),

                        [Children] = {
                            scope:New "UIGridLayout" {
                                CellSize = UDim2.new(0, 110, 0, 130),
                                CellPadding = UDim2.new(0, 10, 0, 10),
                                FillDirection = Enum.FillDirection.Horizontal,
                                FillDirectionMaxCells = 0,
                                HorizontalAlignment = Enum.HorizontalAlignment.Center,
                                SortOrder = Enum.SortOrder.LayoutOrder,
                            },

                            scope:ForPairs(props.Items, function(use, itemScope, index, item)
                                return index, ItemCard(itemScope, item, function()
                                    if not item.Owned then
                                        selectedItem:set(item)
                                        modalVisible:set(true)
                                    end
                                end)
                            end),
                        },
                    },
                },
            },

            -- Purchase confirmation modal
            PurchaseModal(scope, modalVisible, selectedItem, function()
                local item = peek(selectedItem)
                if item then
                    props.OnPurchase(item.Id)
                end
                modalVisible:set(false)
                selectedItem:set(nil)
            end, function()
                modalVisible:set(false)
                selectedItem:set(nil)
            end),
        },
    }

    return screenGui, scope
end

return ShopScreen
