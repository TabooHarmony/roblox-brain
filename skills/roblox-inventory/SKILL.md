---
name: roblox-inventory
description: >
  Inventory, item, and equipment systems for Roblox. Data schemas, slot management,
  stacking, rarity, equip/unequip, drag-and-drop, loot tables, crafting.
  Use when building any item-based system.
last_reviewed: 2026-05-27
---

# Roblox Inventory & Item Systems

Use this skill when building inventory, equipment, loot, crafting, or any item management system.

## Data Schema Design

### Item Definition (shared config)

```luau
-- ReplicatedStorage/ItemDefs.luau
export type ItemDef = {
    id: string,
    name: string,
    description: string,
    icon: string, -- asset ID
    rarity: "Common" | "Uncommon" | "Rare" | "Epic" | "Legendary",
    maxStack: number, -- 1 for equipment, 64 for consumables, etc.
    category: "Weapon" | "Armor" | "Consumable" | "Material" | "Quest",
    sellPrice: number,
    tradeable: boolean,
    stats: {[string]: number}?, -- optional stat bonuses
}

local Items: {[string]: ItemDef} = {
    wooden_sword = {
        id = "wooden_sword",
        name = "Wooden Sword",
        description = "A basic training sword.",
        icon = "rbxassetid://123456",
        rarity = "Common",
        maxStack = 1,
        category = "Weapon",
        sellPrice = 10,
        tradeable = true,
        stats = {damage = 5, speed = 1.2},
    },
    health_potion = {
        id = "health_potion",
        name = "Health Potion",
        description = "Restores 50 HP.",
        icon = "rbxassetid://789012",
        rarity = "Common",
        maxStack = 20,
        category = "Consumable",
        sellPrice = 5,
        tradeable = true,
    },
}

return Items
```

### Player Inventory (save data)

```luau
export type InventorySlot = {
    itemId: string,
    quantity: number,
    metadata: {[string]: any}?, -- enchantments, durability, unique ID
}

export type PlayerInventory = {
    slots: {InventorySlot},
    maxSlots: number,
    equipped: {
        weapon: string?,    -- itemId or nil
        armor: string?,
        accessory: string?,
    },
}

-- Default for new players
local DEFAULT_INVENTORY: PlayerInventory = {
    slots = {},
    maxSlots = 20,
    equipped = {weapon = nil, armor = nil, accessory = nil},
}
```

## Core Operations (Server-Side)

All inventory mutations MUST happen on the server. Client only displays.

### Add Item

```luau
local function addItem(inventory: PlayerInventory, itemId: string, quantity: number): (boolean, string?)
    local def = ItemDefs[itemId]
    if not def then return false, "Invalid item" end

    -- Try to stack with existing
    for _, slot in inventory.slots do
        if slot.itemId == itemId and slot.quantity < def.maxStack then
            local canAdd = math.min(quantity, def.maxStack - slot.quantity)
            slot.quantity += canAdd
            quantity -= canAdd
            if quantity <= 0 then return true, nil end
        end
    end

    -- Add to new slots
    while quantity > 0 do
        if #inventory.slots >= inventory.maxSlots then
            return false, "Inventory full"
        end
        local stackSize = math.min(quantity, def.maxStack)
        table.insert(inventory.slots, {itemId = itemId, quantity = stackSize})
        quantity -= stackSize
    end

    return true, nil
end
```

### Remove Item

```luau
local function removeItem(inventory: PlayerInventory, itemId: string, quantity: number): boolean
    -- First check if player has enough
    local total = 0
    for _, slot in inventory.slots do
        if slot.itemId == itemId then
            total += slot.quantity
        end
    end
    if total < quantity then return false end

    -- Remove from slots (back to front to avoid index shifting)
    for i = #inventory.slots, 1, -1 do
        local slot = inventory.slots[i]
        if slot.itemId == itemId then
            local toRemove = math.min(quantity, slot.quantity)
            slot.quantity -= toRemove
            quantity -= toRemove
            if slot.quantity <= 0 then
                table.remove(inventory.slots, i)
            end
            if quantity <= 0 then break end
        end
    end

    return true
end
```

### Equip/Unequip

```luau
local function equipItem(inventory: PlayerInventory, slotIndex: number): (boolean, string?)
    local slot = inventory.slots[slotIndex]
    if not slot then return false, "Invalid slot" end

    local def = ItemDefs[slot.itemId]
    if not def then return false, "Invalid item" end

    local equipSlot: string
    if def.category == "Weapon" then equipSlot = "weapon"
    elseif def.category == "Armor" then equipSlot = "armor"
    else return false, "Cannot equip this item" end

    -- Unequip current if any
    local currentEquipped = inventory.equipped[equipSlot]
    if currentEquipped then
        -- Add back to inventory
        addItem(inventory, currentEquipped, 1)
    end

    -- Equip new
    inventory.equipped[equipSlot] = slot.itemId
    removeItem(inventory, slot.itemId, 1)

    return true, nil
end
```

## Loot Tables

### Weighted Random

```luau
export type LootEntry = {
    itemId: string,
    weight: number,     -- relative probability
    minQuantity: number,
    maxQuantity: number,
}

export type LootTable = {
    entries: {LootEntry},
    guaranteedDrops: {LootEntry}?, -- always drop these
    rollCount: number,             -- how many times to roll
}

local function rollLootTable(lootTable: LootTable): {{itemId: string, quantity: number}}
    local drops = {}

    -- Guaranteed drops first
    if lootTable.guaranteedDrops then
        for _, entry in lootTable.guaranteedDrops do
            local qty = math.random(entry.minQuantity, entry.maxQuantity)
            table.insert(drops, {itemId = entry.itemId, quantity = qty})
        end
    end

    -- Weighted random rolls
    local totalWeight = 0
    for _, entry in lootTable.entries do
        totalWeight += entry.weight
    end

    for _ = 1, lootTable.rollCount do
        local roll = math.random() * totalWeight
        local cumulative = 0
        for _, entry in lootTable.entries do
            cumulative += entry.weight
            if roll <= cumulative then
                local qty = math.random(entry.minQuantity, entry.maxQuantity)
                table.insert(drops, {itemId = entry.itemId, quantity = qty})
                break
            end
        end
    end

    return drops
end
```

### Rarity Weights (typical distribution)

| Rarity | Weight | Drop Rate |
|--------|--------|-----------|
| Common | 60 | ~60% |
| Uncommon | 25 | ~25% |
| Rare | 10 | ~10% |
| Epic | 4 | ~4% |
| Legendary | 1 | ~1% |

## Crafting

```luau
export type Recipe = {
    result: {itemId: string, quantity: number},
    ingredients: {{itemId: string, quantity: number}},
    craftTime: number?, -- seconds, nil = instant
}

local function canCraft(inventory: PlayerInventory, recipe: Recipe): boolean
    for _, ingredient in recipe.ingredients do
        local count = countItem(inventory, ingredient.itemId)
        if count < ingredient.quantity then
            return false
        end
    end
    return true
end

local function craft(inventory: PlayerInventory, recipe: Recipe): (boolean, string?)
    if not canCraft(inventory, recipe) then
        return false, "Missing ingredients"
    end

    -- Remove ingredients
    for _, ingredient in recipe.ingredients do
        removeItem(inventory, ingredient.itemId, ingredient.quantity)
    end

    -- Add result
    local success, err = addItem(inventory, recipe.result.itemId, recipe.result.quantity)
    if not success then
        -- Rollback: give ingredients back
        for _, ingredient in recipe.ingredients do
            addItem(inventory, ingredient.itemId, ingredient.quantity)
        end
        return false, err
    end

    return true, nil
end
```

## Client Display Pattern

The client reads inventory state from the server (via attributes, ValueObjects, or RemoteFunction) and renders it. Never mutate inventory on the client.

```luau
-- Client: request inventory data
local GetInventory = ReplicatedStorage.Remotes.GetInventory

local function refreshUI()
    local data = GetInventory:InvokeServer()
    -- data = {slots = {...}, equipped = {...}, maxSlots = N}

    for i, slot in data.slots do
        local icon = ItemDefs[slot.itemId].icon
        local quantity = slot.quantity
        updateSlotUI(i, icon, quantity)
    end
end

-- Client: request action (server validates)
local UseItem = ReplicatedStorage.Remotes.UseItem
UseItem:FireServer(slotIndex)
-- Server processes, then client refreshes UI
```

## Common Mistakes

- **Client-side inventory mutations**: Exploiters give themselves items. ALL changes server-side.
- **No stack limit check**: Allows infinite stacking, breaks economy.
- **No "inventory full" handling**: Items vanish silently. Always check before adding.
- **Saving item references instead of IDs**: Instances can't be saved to DataStore. Save string IDs.
- **No rollback on failed operations**: If crafting adds result but ingredients weren't removed (error), you've duplicated items.
- **Trusting client slot index**: Validate that the slot exists and contains what the client claims.
- **No unique IDs for tradeable items**: Without unique IDs, you can't track duplication exploits.
