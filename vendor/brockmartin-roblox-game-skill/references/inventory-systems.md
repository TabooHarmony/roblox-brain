# Roblox Inventory Systems Reference

---

## 1. Overview

Inventory systems manage the lifecycle of items a player owns, equips, trades, and consumes. Load and initialize the inventory system when:

- **Building inventory UI** -- The player opens their backpack, equipment screen, or any item management interface.
- **Items and equipment** -- The player picks up loot, equips gear, or consumes items during gameplay.
- **Trading** -- Two players negotiate and swap items in a secure, server-validated transaction.
- **Shops and stores** -- The player buys from or sells to NPC vendors.

The core principle is **server authority**: the server owns all inventory state, and the client is only a rendering layer. Every mutation flows through the server, which validates ownership, capacity, and legality before committing changes.

---

## 2. Item Data Architecture

### Item Definitions (Shared Schema)

Item definitions are static, read-only templates that describe what an item *is*. Store them in a shared `ModuleScript` inside `ReplicatedStorage` so both server and client can reference them without duplication.

```luau
-- ReplicatedStorage/Shared/ItemDefinitions.luau
local ItemDefinitions = {
    [1001] = {
        Id = 1001,
        Name = "Iron Sword",
        Description = "A sturdy blade forged from iron.",
        Rarity = "Common",
        Category = "Weapon",
        Stats = { Attack = 10, Speed = 1.2 },
        Icon = "rbxassetid://123456789",
        Stackable = false,
        MaxStack = 1,
    },
    [1002] = {
        Id = 1002,
        Name = "Health Potion",
        Description = "Restores 50 HP.",
        Rarity = "Common",
        Category = "Consumable",
        Stats = { HealAmount = 50 },
        Icon = "rbxassetid://123456790",
        Stackable = true,
        MaxStack = 99,
    },
    [2001] = {
        Id = 2001,
        Name = "Dragon Helmet",
        Description = "Helm forged from dragon scales.",
        Rarity = "Legendary",
        Category = "Helmet",
        Stats = { Defense = 45, FireResist = 20 },
        Icon = "rbxassetid://123456791",
        Stackable = false,
        MaxStack = 1,
    },
    [2002] = {
        Id = 2002,
        Name = "Leather Boots",
        Description = "Light boots that increase movement speed.",
        Rarity = "Uncommon",
        Category = "Boots",
        Stats = { Defense = 5, Speed = 1.5 },
        Icon = "rbxassetid://123456792",
        Stackable = false,
        MaxStack = 1,
    },
}

return ItemDefinitions
```

### Item Instances (Player-Specific Data)

An item instance is a player's copy of an item. It references the definition by `itemId` and stores instance-specific data like quantity, durability, or enchantments. Never duplicate the full definition into instance data.

```luau
-- Example item instance stored in a player's inventory slot
{
    itemId = 1001,          -- references ItemDefinitions[1001]
    quantity = 1,           -- always 1 for non-stackable
    metadata = {
        durability = 85,    -- instance-specific
        enchantments = { "Sharpness II" },
        uuid = "a1b2c3d4",  -- unique instance identifier for trading/logging
    },
}
```

Key rules:
- `itemId` is the only link to the definition. All display data (name, icon, stats) comes from `ItemDefinitions[itemId]`.
- `metadata` holds mutable, instance-specific state.
- Generate a `uuid` for non-stackable items so individual copies are distinguishable (critical for trading and logging).

---

## 3. Inventory Storage

### Server-Side Inventory Table

The server maintains each player's inventory as a Luau table. Two common layouts exist and can be combined.

**Slot-based (fixed slots):**

Used for equipment where each slot has a specific purpose. Slots are keyed by name.

```luau
local equipment = {
    Weapon = nil,       -- one item instance or nil
    Helmet = nil,
    Armor = nil,
    Boots = nil,
    Accessory1 = nil,
    Accessory2 = nil,
}
```

**List-based (dynamic backpack):**

Used for general inventory where items fill sequential slots up to a capacity limit.

```luau
local backpack = {
    -- [slotIndex] = itemInstance
    [1] = { itemId = 1002, quantity = 10, metadata = {} },
    [2] = { itemId = 1001, quantity = 1, metadata = { durability = 100, uuid = "x1y2" } },
    -- slots 3..maxSlots are nil (empty)
}
```

### Capacity and Overflow

```luau
local MAX_BACKPACK_SLOTS = 30

local function getUsedSlotCount(backpack: { [number]: any }): number
    local count = 0
    for _ in backpack do
        count += 1
    end
    return count
end

local function hasSpace(backpack: { [number]: any }): boolean
    return getUsedSlotCount(backpack) < MAX_BACKPACK_SLOTS
end
```

Overflow handling strategies:
- **Reject** -- Refuse the action and notify the player ("Inventory full").
- **Mailbox / overflow stash** -- Store overflow items in a secondary collection the player can retrieve later.
- **Drop to ground** -- Spawn the item in the world near the player (risky if other players can loot it).

Always check capacity *before* committing an add operation. Never silently discard items.

---

## 4. Equipment System

### Equip Slots

```luau
local EQUIP_SLOTS = {
    "Weapon",
    "Helmet",
    "Armor",
    "Boots",
    "Accessory1",
    "Accessory2",
}

-- Map item categories to valid equip slots
local CATEGORY_TO_SLOT: { [string]: { string } } = {
    Weapon    = { "Weapon" },
    Helmet    = { "Helmet" },
    Armor     = { "Armor" },
    Boots     = { "Boots" },
    Accessory = { "Accessory1", "Accessory2" },
}
```

### Equip Flow

1. **Validate ownership** -- Confirm the item exists in the player's backpack.
2. **Validate slot compatibility** -- Ensure the item's category matches the target slot.
3. **Unequip current** -- If the target slot is occupied, move the current item back to backpack (requires space check).
4. **Remove from backpack** -- Take the item out of the backpack slot.
5. **Place in equip slot** -- Assign the item instance to the equipment table.
6. **Apply stat bonuses** -- Recalculate the player's stats.
7. **Update visuals** -- Attach the Tool or Accessory to the character model.

### Unequip Flow

Reverse of equip: validate backpack has space, remove from equip slot, add to backpack, remove stat bonuses, remove visual.

### Code Example

```luau
-- Inside InventoryManager (see full module in Section 11)

local function getItemDef(itemId: number)
    return ItemDefinitions[itemId]
end

local function findBackpackSlot(playerData, itemId: number, uuid: string?): number?
    for slot, item in playerData.backpack do
        if item.itemId == itemId then
            if uuid == nil or (item.metadata and item.metadata.uuid == uuid) then
                return slot
            end
        end
    end
    return nil
end

local function findEmptyBackpackSlot(playerData): number?
    for i = 1, MAX_BACKPACK_SLOTS do
        if playerData.backpack[i] == nil then
            return i
        end
    end
    return nil
end

function InventoryManager.equip(player: Player, backpackSlot: number, equipSlot: string): (boolean, string?)
    local playerData = InventoryManager._getPlayerData(player)
    if not playerData then
        return false, "Player data not found"
    end

    local item = playerData.backpack[backpackSlot]
    if not item then
        return false, "No item in that backpack slot"
    end

    local def = getItemDef(item.itemId)
    if not def then
        return false, "Unknown item"
    end

    -- Validate slot compatibility
    local validSlots = CATEGORY_TO_SLOT[def.Category]
    if not validSlots or not table.find(validSlots, equipSlot) then
        return false, "Item cannot be equipped in that slot"
    end

    -- If slot is occupied, ensure we have room to unequip
    local currentEquip = playerData.equipment[equipSlot]
    if currentEquip then
        local emptySlot = findEmptyBackpackSlot(playerData)
        if not emptySlot then
            return false, "Inventory full, cannot unequip current item"
        end
        -- Move current equipment to backpack
        playerData.backpack[emptySlot] = currentEquip
    end

    -- Move item from backpack to equipment
    playerData.equipment[equipSlot] = item
    playerData.backpack[backpackSlot] = nil

    -- Recalculate stats
    InventoryManager._recalculateStats(player)

    -- Update character visuals
    InventoryManager._updateVisuals(player, equipSlot, item)

    return true, nil
end
```

### Visual Updates

```luau
function InventoryManager._updateVisuals(player: Player, equipSlot: string, item: any?)
    local character = player.Character
    if not character then return end

    if equipSlot == "Weapon" then
        -- Remove existing tool
        for _, tool in character:GetChildren() do
            if tool:IsA("Tool") and tool:GetAttribute("EquipSlot") == "Weapon" then
                tool:Destroy()
            end
        end
        -- Add new tool if item provided
        if item then
            local def = getItemDef(item.itemId)
            local toolTemplate = ServerStorage.Tools:FindFirstChild(def.Name)
            if toolTemplate then
                local tool = toolTemplate:Clone()
                tool:SetAttribute("EquipSlot", "Weapon")
                tool.Parent = character
            end
        end
    elseif equipSlot == "Helmet" or equipSlot == "Armor" or equipSlot == "Boots" then
        -- Handle Accessories attached to the Humanoid
        local humanoid = character:FindFirstChildOfClass("Humanoid")
        if not humanoid then return end

        -- Remove old accessory for this slot
        for _, acc in character:GetChildren() do
            if acc:IsA("Accessory") and acc:GetAttribute("EquipSlot") == equipSlot then
                acc:Destroy()
            end
        end
        -- Add new accessory
        if item then
            local def = getItemDef(item.itemId)
            local accTemplate = ServerStorage.Accessories:FindFirstChild(def.Name)
            if accTemplate then
                local acc = accTemplate:Clone()
                acc:SetAttribute("EquipSlot", equipSlot)
                humanoid:AddAccessory(acc)
            end
        end
    end
end
```

---

## 5. Loot / Drop Systems

### Rarity Weights

Standard rarity tiers with drop weights:

| Rarity    | Weight | Approximate Chance |
|-----------|--------|--------------------|
| Common    | 60     | 60%                |
| Uncommon  | 25     | 25%                |
| Rare      | 10     | 10%                |
| Epic      | 4      | 4%                 |
| Legendary | 1      | 1%                 |

### Drop Tables

Each enemy or chest defines a drop table listing which items can drop and at what rarity:

```luau
local DropTables = {
    Goblin = {
        { itemId = 1001, rarity = "Common" },
        { itemId = 1002, rarity = "Common" },
        { itemId = 1003, rarity = "Uncommon" },
        { itemId = 2001, rarity = "Legendary" },
    },
    TreasureChest = {
        { itemId = 1003, rarity = "Uncommon" },
        { itemId = 1004, rarity = "Rare" },
        { itemId = 2001, rarity = "Epic" },
        { itemId = 2002, rarity = "Legendary" },
    },
}
```

### Weighted Random Selection Algorithm

```luau
local RARITY_WEIGHTS: { [string]: number } = {
    Common = 60,
    Uncommon = 25,
    Rare = 10,
    Epic = 4,
    Legendary = 1,
}

local function weightedRandomPick(dropTable: { { itemId: number, rarity: string } }): number?
    -- Build weighted entries
    local entries = {}
    local totalWeight = 0
    for _, entry in dropTable do
        local weight = RARITY_WEIGHTS[entry.rarity] or 0
        if weight > 0 then
            totalWeight += weight
            table.insert(entries, { itemId = entry.itemId, weight = weight })
        end
    end

    if totalWeight == 0 then
        return nil
    end

    -- Roll
    local roll = math.random() * totalWeight
    local cumulative = 0
    for _, entry in entries do
        cumulative += entry.weight
        if roll <= cumulative then
            return entry.itemId
        end
    end

    -- Fallback (should not reach here)
    return entries[#entries].itemId
end
```

### Pity System (Guaranteed Drop After N Attempts)

Prevents extreme bad luck by guaranteeing a rare+ drop after a threshold of attempts with no rare+ drop.

```luau
local PITY_THRESHOLD = 50  -- guarantee rare+ after 50 kills with none

local pityCounters: { [number]: number } = {}  -- [playerId] = count since last rare+

local function rollWithPity(player: Player, dropTable): number?
    local userId = player.UserId
    pityCounters[userId] = pityCounters[userId] or 0

    local itemId = weightedRandomPick(dropTable)
    if not itemId then return nil end

    local def = getItemDef(itemId)
    local isRarePlus = def and (
        def.Rarity == "Rare" or def.Rarity == "Epic" or def.Rarity == "Legendary"
    )

    if isRarePlus then
        pityCounters[userId] = 0
        return itemId
    end

    pityCounters[userId] += 1

    if pityCounters[userId] >= PITY_THRESHOLD then
        -- Force a rare+ drop
        local rareItems = {}
        for _, entry in dropTable do
            local r = entry.rarity
            if r == "Rare" or r == "Epic" or r == "Legendary" then
                table.insert(rareItems, entry.itemId)
            end
        end
        if #rareItems > 0 then
            pityCounters[userId] = 0
            return rareItems[math.random(1, #rareItems)]
        end
    end

    return itemId
end
```

---

## 6. Trading System

### Trade Flow

1. **Player A sends trade request** to Player B (via RemoteEvent).
2. **Player B accepts** the request, opening the trade window for both.
3. **Both players add/remove items** to their offer. Each change is sent to the server and validated.
4. **Both players confirm** ("Ready" / "Lock in").
5. **Server validates** both players still own all offered items, both have inventory space for incoming items, and neither set of items has changed since confirmation.
6. **Atomic swap** -- server removes all offered items from both players and grants the received items. If any step fails, the entire trade is rolled back.
7. **Trade logged** with timestamp, both player IDs, and item details for dispute resolution.

### Trade Logging

```luau
local function logTrade(
    playerA: Player,
    playerB: Player,
    itemsFromA: { any },
    itemsFromB: { any }
)
    local entry = {
        timestamp = os.time(),
        playerA = { userId = playerA.UserId, name = playerA.Name },
        playerB = { userId = playerB.UserId, name = playerB.Name },
        fromA = itemsFromA,
        fromB = itemsFromB,
    }
    -- Persist to a DataStore or external logging service
    local success, err = pcall(function()
        local TradeLogStore = DataStoreService:GetDataStore("TradeLogs")
        local key = `trade_{entry.timestamp}_{playerA.UserId}_{playerB.UserId}`
        TradeLogStore:SetAsync(key, entry)
    end)
    if not success then
        warn("[TradeLog] Failed to log trade:", err)
    end
end
```

### Code Example -- Trade Execution

```luau
function InventoryManager.executeTrade(
    playerA: Player,
    playerB: Player,
    offerA: { { backpackSlot: number } },
    offerB: { { backpackSlot: number } }
): (boolean, string?)
    local dataA = InventoryManager._getPlayerData(playerA)
    local dataB = InventoryManager._getPlayerData(playerB)
    if not dataA or not dataB then
        return false, "Player data not found"
    end

    -- 1. Validate all offered items still exist
    local itemsFromA = {}
    for _, offer in offerA do
        local item = dataA.backpack[offer.backpackSlot]
        if not item then
            return false, "Player A missing offered item"
        end
        table.insert(itemsFromA, { slot = offer.backpackSlot, item = item })
    end

    local itemsFromB = {}
    for _, offer in offerB do
        local item = dataB.backpack[offer.backpackSlot]
        if not item then
            return false, "Player B missing offered item"
        end
        table.insert(itemsFromB, { slot = offer.backpackSlot, item = item })
    end

    -- 2. Validate both have space for incoming items
    local freeA = 0
    local freeB = 0
    for i = 1, MAX_BACKPACK_SLOTS do
        if dataA.backpack[i] == nil then freeA += 1 end
        if dataB.backpack[i] == nil then freeB += 1 end
    end

    -- After removing offered items, they gain slots back
    local netSpaceA = freeA + #itemsFromA - #itemsFromB
    local netSpaceB = freeB + #itemsFromB - #itemsFromA
    if netSpaceA < 0 then
        return false, "Player A does not have enough inventory space"
    end
    if netSpaceB < 0 then
        return false, "Player B does not have enough inventory space"
    end

    -- 3. Atomic swap -- remove all first, then grant all
    -- Remove from A
    for _, entry in itemsFromA do
        dataA.backpack[entry.slot] = nil
    end
    -- Remove from B
    for _, entry in itemsFromB do
        dataB.backpack[entry.slot] = nil
    end

    -- Grant B's items to A
    for _, entry in itemsFromB do
        local emptySlot = findEmptyBackpackSlot(dataA)
        if not emptySlot then
            -- Rollback: this should not happen given the space check above
            warn("[Trade] Critical: space check passed but no slot found. Rolling back.")
            -- Restore all items (rollback logic)
            for _, e in itemsFromA do dataA.backpack[e.slot] = e.item end
            for _, e in itemsFromB do dataB.backpack[e.slot] = e.item end
            return false, "Trade failed unexpectedly"
        end
        dataA.backpack[emptySlot] = entry.item
    end

    -- Grant A's items to B
    for _, entry in itemsFromA do
        local emptySlot = findEmptyBackpackSlot(dataB)
        if not emptySlot then
            warn("[Trade] Critical: space check passed but no slot found. Rolling back.")
            for _, e in itemsFromA do dataA.backpack[e.slot] = e.item end
            for _, e in itemsFromB do dataB.backpack[e.slot] = e.item end
            return false, "Trade failed unexpectedly"
        end
        dataB.backpack[emptySlot] = entry.item
    end

    -- 4. Log the trade
    logTrade(playerA, playerB, itemsFromA, itemsFromB)

    return true, nil
end
```

---

## 7. Shop / Store System

### NPC Shop Definition

```luau
local ShopDefinitions = {
    WeaponSmith = {
        name = "Grog's Weapons",
        items = {
            { itemId = 1001, buyPrice = 100, sellPrice = 40 },
            { itemId = 1005, buyPrice = 500, sellPrice = 200 },
            { itemId = 1006, buyPrice = 2000, sellPrice = 800 },
        },
    },
    Alchemist = {
        name = "Elara's Potions",
        items = {
            { itemId = 1002, buyPrice = 25, sellPrice = 10 },
            { itemId = 1007, buyPrice = 75, sellPrice = 30 },
        },
    },
}
```

### Purchase Flow (Atomic)

1. Validate the shop and item exist.
2. Validate the player has enough currency.
3. Validate the player has inventory space.
4. Deduct currency.
5. Grant item.

If any step fails, nothing changes. Steps 4 and 5 must both succeed or both be reverted.

```luau
function InventoryManager.buyFromShop(
    player: Player,
    shopId: string,
    itemIndex: number,
    quantity: number
): (boolean, string?)
    local shop = ShopDefinitions[shopId]
    if not shop then
        return false, "Shop not found"
    end

    local listing = shop.items[itemIndex]
    if not listing then
        return false, "Item not in shop"
    end

    local totalCost = listing.buyPrice * quantity
    local playerData = InventoryManager._getPlayerData(player)
    if not playerData then
        return false, "Player data not found"
    end

    -- Validate currency
    if playerData.currency < totalCost then
        return false, "Not enough currency"
    end

    -- Validate space / stackability
    local def = getItemDef(listing.itemId)
    if not def then
        return false, "Unknown item"
    end

    if def.Stackable then
        -- Find existing stack or need a new slot
        local existingSlot = nil
        for slot, item in playerData.backpack do
            if item.itemId == listing.itemId then
                if item.quantity + quantity <= def.MaxStack then
                    existingSlot = slot
                    break
                end
            end
        end
        if existingSlot then
            playerData.currency -= totalCost
            playerData.backpack[existingSlot].quantity += quantity
            return true, nil
        end
    end

    -- Need a new slot (non-stackable or no existing stack with room)
    local emptySlot = findEmptyBackpackSlot(playerData)
    if not emptySlot then
        return false, "Inventory full"
    end

    -- Commit (atomic: currency deduction + item grant)
    playerData.currency -= totalCost
    playerData.backpack[emptySlot] = {
        itemId = listing.itemId,
        quantity = quantity,
        metadata = {},
    }

    return true, nil
end
```

### Sell Flow

```luau
function InventoryManager.sellToShop(
    player: Player,
    shopId: string,
    backpackSlot: number,
    quantity: number
): (boolean, string?)
    local shop = ShopDefinitions[shopId]
    if not shop then
        return false, "Shop not found"
    end

    local playerData = InventoryManager._getPlayerData(player)
    if not playerData then
        return false, "Player data not found"
    end

    local item = playerData.backpack[backpackSlot]
    if not item then
        return false, "No item in that slot"
    end

    -- Find sell price from shop listing
    local sellPrice = nil
    for _, listing in shop.items do
        if listing.itemId == item.itemId then
            sellPrice = listing.sellPrice
            break
        end
    end
    if not sellPrice then
        return false, "This shop does not buy that item"
    end

    if item.quantity < quantity then
        return false, "Not enough of that item"
    end

    -- Commit
    local totalValue = sellPrice * quantity
    item.quantity -= quantity
    if item.quantity <= 0 then
        playerData.backpack[backpackSlot] = nil
    end
    playerData.currency += totalValue

    return true, nil
end
```

---

## 8. DataStore Integration

### Serialization

Inventory data must be serialized into DataStore-safe format. Rules:

- No Instance references (no `tool`, `accessory`, or any Roblox object).
- Convert everything to plain tables of numbers, strings, and booleans.
- Prefer item ID references over storing full definition data. Definitions live in code; only instance data goes to the DataStore.

```luau
local function serializeInventory(playerData): { [string]: any }
    local serialized = {
        currency = playerData.currency,
        backpack = {},
        equipment = {},
    }

    for slot, item in playerData.backpack do
        serialized.backpack[tostring(slot)] = {
            itemId = item.itemId,
            qty = item.quantity,
            meta = item.metadata or {},
        }
    end

    for slotName, item in playerData.equipment do
        if item then
            serialized.equipment[slotName] = {
                itemId = item.itemId,
                qty = item.quantity,
                meta = item.metadata or {},
            }
        end
    end

    return serialized
end

local function deserializeInventory(saved: { [string]: any }): { [string]: any }
    local playerData = {
        currency = saved.currency or 0,
        backpack = {},
        equipment = {
            Weapon = nil,
            Helmet = nil,
            Armor = nil,
            Boots = nil,
            Accessory1 = nil,
            Accessory2 = nil,
        },
    }

    if saved.backpack then
        for slotStr, data in saved.backpack do
            local slot = tonumber(slotStr)
            if slot then
                playerData.backpack[slot] = {
                    itemId = data.itemId,
                    quantity = data.qty or 1,
                    metadata = data.meta or {},
                }
            end
        end
    end

    if saved.equipment then
        for slotName, data in saved.equipment do
            playerData.equipment[slotName] = {
                itemId = data.itemId,
                quantity = data.qty or 1,
                metadata = data.meta or {},
            }
        end
    end

    return playerData
end
```

### Handling Large Inventories

- **DataStore limit**: 4MB per key (4,194,304 bytes).
- Each item slot serializes to roughly 50-200 bytes depending on metadata. A 500-slot inventory with moderate metadata is well under 1MB.
- If inventories grow very large, split across multiple DataStore keys (e.g., `inv_backpack`, `inv_equipment`, `inv_overflow`).
- Use `HttpService:JSONEncode()` to estimate payload size before saving:

```luau
local HttpService = game:GetService("HttpService")

local function estimateSize(data: any): number
    local json = HttpService:JSONEncode(data)
    return #json
end
```

### Save and Load

```luau
local DataStoreService = game:GetService("DataStoreService")
local InventoryStore = DataStoreService:GetDataStore("PlayerInventory_v1")

local function savePlayerInventory(player: Player)
    local playerData = InventoryManager._getPlayerData(player)
    if not playerData then return end

    local serialized = serializeInventory(playerData)
    local key = `player_{player.UserId}`

    local success, err = pcall(function()
        InventoryStore:SetAsync(key, serialized)
    end)

    if not success then
        warn(`[Inventory] Failed to save for {player.Name}: {err}`)
    end
end

local function loadPlayerInventory(player: Player): { [string]: any }
    local key = `player_{player.UserId}`
    local success, saved = pcall(function()
        return InventoryStore:GetAsync(key)
    end)

    if success and saved then
        return deserializeInventory(saved)
    else
        -- Return default new-player inventory
        return {
            currency = 0,
            backpack = {},
            equipment = {
                Weapon = nil,
                Helmet = nil,
                Armor = nil,
                Boots = nil,
                Accessory1 = nil,
                Accessory2 = nil,
            },
        }
    end
end
```

---

## 9. Best Practices

- **Server owns all inventory state.** The client renders what the server tells it. Every add, remove, equip, trade, and purchase is a server operation.
- **Validate every operation.** Check ownership, quantities, capacity, and item existence before every mutation. Never trust client-supplied item data.
- **Log item transactions.** Record every significant inventory change (trades, purchases, loot drops, item deletions) with timestamps and player IDs. This is essential for player support and detecting exploits.
- **Handle edge cases explicitly:**
  - Full inventory on loot: notify the player, use overflow storage, or drop on ground.
  - Disconnect during trade: cancel the trade, return all items. Never leave items in limbo.
  - Disconnect during save: use `PlayerRemoving` plus `game:BindToClose()` to ensure saves complete.
  - Duplicate item IDs: use UUIDs for non-stackable items so copies are distinguishable.
- **Item versioning for balance changes.** When you change item stats (nerf/buff), update `ItemDefinitions` in code. Since instances only store `itemId`, all players automatically see new stats on next session. If you need to preserve old versions, add a `version` field to instance metadata.
- **Use `UpdateAsync` over `SetAsync` for saves when data contention is possible.** `UpdateAsync` provides atomic read-modify-write to avoid overwriting concurrent changes.
- **Debounce saves.** Do not save on every inventory change. Save periodically (every 60-120 seconds) and on `PlayerRemoving`.

---

## 10. Anti-Patterns

**Client-side inventory (exploitable):**
Never store the "real" inventory on the client. An exploiter can modify LocalScripts and RemoteEvents to give themselves any item. The client should only have a *read-only mirror* for UI rendering.

**Trusting client item data:**
Never accept full item definitions from the client (e.g., "I have an item with 9999 Attack"). The client sends an action ("equip slot 3") and the server looks up what is actually in slot 3.

**Not validating trades server-side:**
If the server does not verify both players own the items they are offering at the moment of execution, a player can offer an item, then drop it, and still "trade" it -- duplicating the item.

**No overflow handling:**
If loot is granted without checking capacity, items either vanish silently (data loss) or the system errors. Always check before granting, and handle the full case gracefully.

**Storing full item definitions in DataStore:**
Storing name, description, stats, and icon per instance wastes space and causes data drift when definitions change. Store only `itemId` and instance-specific metadata.

**Using string keys for backpack slots in runtime:**
Keep numeric keys at runtime for fast iteration. Convert to string keys only during serialization (DataStore requires string keys for dictionary-style tables).

**No save retry / no BindToClose:**
If the save on `PlayerRemoving` fails and there is no `BindToClose` fallback, data is lost when the server shuts down.

---

## 11. Complete InventoryManager Module

A full, self-contained `InventoryManager` module combining all systems above.

```luau
-- ServerScriptService/Modules/InventoryManager.luau
local DataStoreService = game:GetService("DataStoreService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ServerStorage = game:GetService("ServerStorage")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemDefinitions = require(ReplicatedStorage.Shared.ItemDefinitions)

local InventoryStore = DataStoreService:GetDataStore("PlayerInventory_v1")

--------------------------------------------------------------------------------
-- Constants
--------------------------------------------------------------------------------

local MAX_BACKPACK_SLOTS = 30

local EQUIP_SLOTS = { "Weapon", "Helmet", "Armor", "Boots", "Accessory1", "Accessory2" }

local CATEGORY_TO_SLOT: { [string]: { string } } = {
    Weapon    = { "Weapon" },
    Helmet    = { "Helmet" },
    Armor     = { "Armor" },
    Boots     = { "Boots" },
    Accessory = { "Accessory1", "Accessory2" },
}

local RARITY_WEIGHTS: { [string]: number } = {
    Common    = 60,
    Uncommon  = 25,
    Rare      = 10,
    Epic      = 4,
    Legendary = 1,
}

local PITY_THRESHOLD = 50

--------------------------------------------------------------------------------
-- Module
--------------------------------------------------------------------------------

local InventoryManager = {}

-- Private state: [userId] = playerData
local playerDataCache: { [number]: any } = {}
local pityCounters: { [number]: number } = {}

--------------------------------------------------------------------------------
-- Internal Helpers
--------------------------------------------------------------------------------

local function getItemDef(itemId: number)
    return ItemDefinitions[itemId]
end

function InventoryManager._getPlayerData(player: Player)
    return playerDataCache[player.UserId]
end

local function findEmptyBackpackSlot(playerData): number?
    for i = 1, MAX_BACKPACK_SLOTS do
        if playerData.backpack[i] == nil then
            return i
        end
    end
    return nil
end

local function findStackableSlot(playerData, itemId: number, addQty: number): number?
    local def = getItemDef(itemId)
    if not def or not def.Stackable then
        return nil
    end
    for slot, item in playerData.backpack do
        if item.itemId == itemId and item.quantity + addQty <= def.MaxStack then
            return slot
        end
    end
    return nil
end

local function generateUUID(): string
    return HttpService:GenerateGUID(false)
end

--------------------------------------------------------------------------------
-- Serialization
--------------------------------------------------------------------------------

local function serializeInventory(playerData): { [string]: any }
    local serialized = {
        currency = playerData.currency,
        backpack = {},
        equipment = {},
    }
    for slot, item in playerData.backpack do
        serialized.backpack[tostring(slot)] = {
            itemId = item.itemId,
            qty = item.quantity,
            meta = item.metadata or {},
        }
    end
    for slotName, item in playerData.equipment do
        if item then
            serialized.equipment[slotName] = {
                itemId = item.itemId,
                qty = item.quantity,
                meta = item.metadata or {},
            }
        end
    end
    return serialized
end

local function deserializeInventory(saved: { [string]: any }?): { [string]: any }
    if not saved then
        return {
            currency = 0,
            backpack = {},
            equipment = {
                Weapon = nil, Helmet = nil, Armor = nil,
                Boots = nil, Accessory1 = nil, Accessory2 = nil,
            },
        }
    end

    local playerData = {
        currency = saved.currency or 0,
        backpack = {},
        equipment = {
            Weapon = nil, Helmet = nil, Armor = nil,
            Boots = nil, Accessory1 = nil, Accessory2 = nil,
        },
    }

    if saved.backpack then
        for slotStr, data in saved.backpack do
            local slot = tonumber(slotStr)
            if slot then
                playerData.backpack[slot] = {
                    itemId = data.itemId,
                    quantity = data.qty or 1,
                    metadata = data.meta or {},
                }
            end
        end
    end

    if saved.equipment then
        for slotName, data in saved.equipment do
            playerData.equipment[slotName] = {
                itemId = data.itemId,
                quantity = data.qty or 1,
                metadata = data.meta or {},
            }
        end
    end

    return playerData
end

--------------------------------------------------------------------------------
-- Save / Load
--------------------------------------------------------------------------------

function InventoryManager.save(player: Player)
    local playerData = playerDataCache[player.UserId]
    if not playerData then return end

    local serialized = serializeInventory(playerData)
    local key = `player_{player.UserId}`

    local success, err = pcall(function()
        InventoryStore:SetAsync(key, serialized)
    end)
    if not success then
        warn(`[InventoryManager] Save failed for {player.Name}: {err}`)
    end
end

function InventoryManager.load(player: Player)
    local key = `player_{player.UserId}`
    local success, saved = pcall(function()
        return InventoryStore:GetAsync(key)
    end)

    local playerData
    if success then
        playerData = deserializeInventory(saved)
    else
        warn(`[InventoryManager] Load failed for {player.Name}, using defaults`)
        playerData = deserializeInventory(nil)
    end

    playerDataCache[player.UserId] = playerData
    pityCounters[player.UserId] = 0
end

function InventoryManager.unload(player: Player)
    InventoryManager.save(player)
    playerDataCache[player.UserId] = nil
    pityCounters[player.UserId] = nil
end

--------------------------------------------------------------------------------
-- Add / Remove Items
--------------------------------------------------------------------------------

function InventoryManager.addItem(
    player: Player,
    itemId: number,
    quantity: number?,
    metadata: { [string]: any }?
): (boolean, string?)
    local playerData = InventoryManager._getPlayerData(player)
    if not playerData then
        return false, "Player data not loaded"
    end

    local def = getItemDef(itemId)
    if not def then
        return false, "Unknown item ID"
    end

    local qty = quantity or 1

    -- Try stacking first
    if def.Stackable then
        local stackSlot = findStackableSlot(playerData, itemId, qty)
        if stackSlot then
            playerData.backpack[stackSlot].quantity += qty
            return true, nil
        end
    end

    -- Need a new slot
    local emptySlot = findEmptyBackpackSlot(playerData)
    if not emptySlot then
        return false, "Inventory full"
    end

    local meta = metadata or {}
    if not def.Stackable and not meta.uuid then
        meta.uuid = generateUUID()
    end

    playerData.backpack[emptySlot] = {
        itemId = itemId,
        quantity = qty,
        metadata = meta,
    }

    return true, nil
end

function InventoryManager.removeItem(
    player: Player,
    backpackSlot: number,
    quantity: number?
): (boolean, string?)
    local playerData = InventoryManager._getPlayerData(player)
    if not playerData then
        return false, "Player data not loaded"
    end

    local item = playerData.backpack[backpackSlot]
    if not item then
        return false, "No item in that slot"
    end

    local qty = quantity or item.quantity
    if item.quantity < qty then
        return false, "Not enough quantity"
    end

    item.quantity -= qty
    if item.quantity <= 0 then
        playerData.backpack[backpackSlot] = nil
    end

    return true, nil
end

--------------------------------------------------------------------------------
-- Equip / Unequip
--------------------------------------------------------------------------------

function InventoryManager._recalculateStats(player: Player)
    local playerData = InventoryManager._getPlayerData(player)
    if not playerData then return end

    local totalStats: { [string]: number } = {}

    for _, slotName in EQUIP_SLOTS do
        local item = playerData.equipment[slotName]
        if item then
            local def = getItemDef(item.itemId)
            if def and def.Stats then
                for stat, value in def.Stats do
                    totalStats[stat] = (totalStats[stat] or 0) + value
                end
            end
        end
    end

    -- Apply stats to player (implementation depends on your stat system)
    -- Example: store on leaderstats or a custom Attributes system
    for stat, value in totalStats do
        player:SetAttribute(`EquipStat_{stat}`, value)
    end

    playerData.calculatedStats = totalStats
end

function InventoryManager._updateVisuals(player: Player, equipSlot: string, item: any?)
    local character = player.Character
    if not character then return end

    if equipSlot == "Weapon" then
        for _, tool in character:GetChildren() do
            if tool:IsA("Tool") and tool:GetAttribute("EquipSlot") == "Weapon" then
                tool:Destroy()
            end
        end
        if item then
            local def = getItemDef(item.itemId)
            if def then
                local toolTemplate = ServerStorage:FindFirstChild("Tools")
                    and ServerStorage.Tools:FindFirstChild(def.Name)
                if toolTemplate then
                    local tool = toolTemplate:Clone()
                    tool:SetAttribute("EquipSlot", "Weapon")
                    tool.Parent = character
                end
            end
        end
    else
        local humanoid = character:FindFirstChildOfClass("Humanoid")
        if not humanoid then return end

        for _, acc in character:GetChildren() do
            if acc:IsA("Accessory") and acc:GetAttribute("EquipSlot") == equipSlot then
                acc:Destroy()
            end
        end
        if item then
            local def = getItemDef(item.itemId)
            if def then
                local accTemplate = ServerStorage:FindFirstChild("Accessories")
                    and ServerStorage.Accessories:FindFirstChild(def.Name)
                if accTemplate then
                    local acc = accTemplate:Clone()
                    acc:SetAttribute("EquipSlot", equipSlot)
                    humanoid:AddAccessory(acc)
                end
            end
        end
    end
end

function InventoryManager.equip(
    player: Player,
    backpackSlot: number,
    equipSlot: string
): (boolean, string?)
    local playerData = InventoryManager._getPlayerData(player)
    if not playerData then
        return false, "Player data not loaded"
    end

    if not table.find(EQUIP_SLOTS, equipSlot) then
        return false, "Invalid equip slot"
    end

    local item = playerData.backpack[backpackSlot]
    if not item then
        return false, "No item in that backpack slot"
    end

    local def = getItemDef(item.itemId)
    if not def then
        return false, "Unknown item"
    end

    local validSlots = CATEGORY_TO_SLOT[def.Category]
    if not validSlots or not table.find(validSlots, equipSlot) then
        return false, "Item cannot go in that slot"
    end

    -- Handle currently equipped item
    local currentEquip = playerData.equipment[equipSlot]
    if currentEquip then
        local emptySlot = findEmptyBackpackSlot(playerData)
        if not emptySlot then
            return false, "Inventory full, cannot unequip current item"
        end
        playerData.backpack[emptySlot] = currentEquip
        InventoryManager._updateVisuals(player, equipSlot, nil)
    end

    playerData.equipment[equipSlot] = item
    playerData.backpack[backpackSlot] = nil

    InventoryManager._recalculateStats(player)
    InventoryManager._updateVisuals(player, equipSlot, item)

    return true, nil
end

function InventoryManager.unequip(player: Player, equipSlot: string): (boolean, string?)
    local playerData = InventoryManager._getPlayerData(player)
    if not playerData then
        return false, "Player data not loaded"
    end

    local item = playerData.equipment[equipSlot]
    if not item then
        return false, "Nothing equipped in that slot"
    end

    local emptySlot = findEmptyBackpackSlot(playerData)
    if not emptySlot then
        return false, "Inventory full"
    end

    playerData.backpack[emptySlot] = item
    playerData.equipment[equipSlot] = nil

    InventoryManager._recalculateStats(player)
    InventoryManager._updateVisuals(player, equipSlot, nil)

    return true, nil
end

--------------------------------------------------------------------------------
-- Loot / Drops
--------------------------------------------------------------------------------

local function weightedRandomPick(dropTable: { { itemId: number, rarity: string } }): number?
    local entries = {}
    local totalWeight = 0
    for _, entry in dropTable do
        local weight = RARITY_WEIGHTS[entry.rarity] or 0
        if weight > 0 then
            totalWeight += weight
            table.insert(entries, { itemId = entry.itemId, weight = weight })
        end
    end

    if totalWeight == 0 then
        return nil
    end

    local roll = math.random() * totalWeight
    local cumulative = 0
    for _, entry in entries do
        cumulative += entry.weight
        if roll <= cumulative then
            return entry.itemId
        end
    end

    return entries[#entries].itemId
end

function InventoryManager.rollLoot(
    player: Player,
    dropTable: { { itemId: number, rarity: string } }
): (boolean, number?, string?)
    local userId = player.UserId
    pityCounters[userId] = pityCounters[userId] or 0

    local itemId = weightedRandomPick(dropTable)
    if not itemId then
        return false, nil, "Empty drop table"
    end

    local def = getItemDef(itemId)
    local isRarePlus = def and (
        def.Rarity == "Rare" or def.Rarity == "Epic" or def.Rarity == "Legendary"
    )

    if isRarePlus then
        pityCounters[userId] = 0
    else
        pityCounters[userId] += 1
        if pityCounters[userId] >= PITY_THRESHOLD then
            local rareItems = {}
            for _, entry in dropTable do
                local r = entry.rarity
                if r == "Rare" or r == "Epic" or r == "Legendary" then
                    table.insert(rareItems, entry.itemId)
                end
            end
            if #rareItems > 0 then
                pityCounters[userId] = 0
                itemId = rareItems[math.random(1, #rareItems)]
            end
        end
    end

    local success, err = InventoryManager.addItem(player, itemId)
    if not success then
        return false, itemId, err
    end

    return true, itemId, nil
end

--------------------------------------------------------------------------------
-- Trading
--------------------------------------------------------------------------------

function InventoryManager.executeTrade(
    playerA: Player,
    playerB: Player,
    slotsFromA: { number },
    slotsFromB: { number }
): (boolean, string?)
    local dataA = InventoryManager._getPlayerData(playerA)
    local dataB = InventoryManager._getPlayerData(playerB)
    if not dataA or not dataB then
        return false, "Player data not found"
    end

    -- Snapshot items for validation and rollback
    local itemsA = {}
    for _, slot in slotsFromA do
        local item = dataA.backpack[slot]
        if not item then
            return false, `Player A missing item in slot {slot}`
        end
        table.insert(itemsA, { slot = slot, item = item })
    end

    local itemsB = {}
    for _, slot in slotsFromB do
        local item = dataB.backpack[slot]
        if not item then
            return false, `Player B missing item in slot {slot}`
        end
        table.insert(itemsB, { slot = slot, item = item })
    end

    -- Space check
    local freeA, freeB = 0, 0
    for i = 1, MAX_BACKPACK_SLOTS do
        if dataA.backpack[i] == nil then freeA += 1 end
        if dataB.backpack[i] == nil then freeB += 1 end
    end

    if (freeA + #itemsA - #itemsB) < 0 then
        return false, "Player A lacks inventory space"
    end
    if (freeB + #itemsB - #itemsA) < 0 then
        return false, "Player B lacks inventory space"
    end

    -- Remove all offered items
    for _, entry in itemsA do
        dataA.backpack[entry.slot] = nil
    end
    for _, entry in itemsB do
        dataB.backpack[entry.slot] = nil
    end

    -- Grant B's items to A
    for _, entry in itemsB do
        local emptySlot = findEmptyBackpackSlot(dataA)
        if not emptySlot then
            -- Rollback
            for _, e in itemsA do dataA.backpack[e.slot] = e.item end
            for _, e in itemsB do dataB.backpack[e.slot] = e.item end
            return false, "Trade failed: space error during swap"
        end
        dataA.backpack[emptySlot] = entry.item
    end

    -- Grant A's items to B
    for _, entry in itemsA do
        local emptySlot = findEmptyBackpackSlot(dataB)
        if not emptySlot then
            -- Rollback
            for _, e in itemsA do dataA.backpack[e.slot] = e.item end
            for _, e in itemsB do dataB.backpack[e.slot] = e.item end
            return false, "Trade failed: space error during swap"
        end
        dataB.backpack[emptySlot] = entry.item
    end

    -- Log trade
    pcall(function()
        local TradeLogStore = DataStoreService:GetDataStore("TradeLogs")
        local key = `trade_{os.time()}_{playerA.UserId}_{playerB.UserId}`
        TradeLogStore:SetAsync(key, {
            timestamp = os.time(),
            playerA = playerA.UserId,
            playerB = playerB.UserId,
            fromA = slotsFromA,
            fromB = slotsFromB,
        })
    end)

    return true, nil
end

--------------------------------------------------------------------------------
-- Shop
--------------------------------------------------------------------------------

local ShopDefinitions = {}

function InventoryManager.registerShop(shopId: string, shopData: any)
    ShopDefinitions[shopId] = shopData
end

function InventoryManager.buyFromShop(
    player: Player,
    shopId: string,
    itemIndex: number,
    quantity: number?
): (boolean, string?)
    local shop = ShopDefinitions[shopId]
    if not shop then
        return false, "Shop not found"
    end

    local listing = shop.items[itemIndex]
    if not listing then
        return false, "Item not in shop"
    end

    local qty = quantity or 1
    local totalCost = listing.buyPrice * qty
    local playerData = InventoryManager._getPlayerData(player)
    if not playerData then
        return false, "Player data not loaded"
    end

    if playerData.currency < totalCost then
        return false, "Not enough currency"
    end

    local def = getItemDef(listing.itemId)
    if not def then
        return false, "Unknown item"
    end

    -- Try stacking
    if def.Stackable then
        local stackSlot = findStackableSlot(playerData, listing.itemId, qty)
        if stackSlot then
            playerData.currency -= totalCost
            playerData.backpack[stackSlot].quantity += qty
            return true, nil
        end
    end

    local emptySlot = findEmptyBackpackSlot(playerData)
    if not emptySlot then
        return false, "Inventory full"
    end

    playerData.currency -= totalCost
    playerData.backpack[emptySlot] = {
        itemId = listing.itemId,
        quantity = qty,
        metadata = {},
    }

    return true, nil
end

function InventoryManager.sellToShop(
    player: Player,
    shopId: string,
    backpackSlot: number,
    quantity: number?
): (boolean, string?)
    local shop = ShopDefinitions[shopId]
    if not shop then
        return false, "Shop not found"
    end

    local playerData = InventoryManager._getPlayerData(player)
    if not playerData then
        return false, "Player data not loaded"
    end

    local item = playerData.backpack[backpackSlot]
    if not item then
        return false, "No item in that slot"
    end

    local sellPrice = nil
    for _, listing in shop.items do
        if listing.itemId == item.itemId then
            sellPrice = listing.sellPrice
            break
        end
    end
    if not sellPrice then
        return false, "Shop does not buy that item"
    end

    local qty = quantity or item.quantity
    if item.quantity < qty then
        return false, "Not enough quantity"
    end

    local totalValue = sellPrice * qty
    item.quantity -= qty
    if item.quantity <= 0 then
        playerData.backpack[backpackSlot] = nil
    end
    playerData.currency += totalValue

    return true, nil
end

--------------------------------------------------------------------------------
-- Lifecycle Hooks (call from a server Script)
--------------------------------------------------------------------------------

function InventoryManager.init()
    Players.PlayerAdded:Connect(function(player)
        InventoryManager.load(player)
    end)

    Players.PlayerRemoving:Connect(function(player)
        InventoryManager.unload(player)
    end)

    game:BindToClose(function()
        for _, player in Players:GetPlayers() do
            InventoryManager.save(player)
        end
    end)
end

return InventoryManager
```

### Usage from a Server Script

```luau
-- ServerScriptService/InventoryServer.server.luau
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local InventoryManager = require(script.Parent.Modules.InventoryManager)

InventoryManager.init()

-- Register shops
InventoryManager.registerShop("WeaponSmith", {
    name = "Grog's Weapons",
    items = {
        { itemId = 1001, buyPrice = 100, sellPrice = 40 },
    },
})

-- Wire up RemoteEvents
local Remotes = ReplicatedStorage:WaitForChild("Remotes")

Remotes.EquipItem.OnServerEvent:Connect(function(player, backpackSlot, equipSlot)
    if typeof(backpackSlot) ~= "number" or typeof(equipSlot) ~= "string" then
        return
    end
    local success, err = InventoryManager.equip(player, backpackSlot, equipSlot)
    Remotes.EquipResult:FireClient(player, success, err)
end)

Remotes.UnequipItem.OnServerEvent:Connect(function(player, equipSlot)
    if typeof(equipSlot) ~= "string" then return end
    local success, err = InventoryManager.unequip(player, equipSlot)
    Remotes.UnequipResult:FireClient(player, success, err)
end)

Remotes.BuyItem.OnServerEvent:Connect(function(player, shopId, itemIndex, quantity)
    if typeof(shopId) ~= "string" or typeof(itemIndex) ~= "number" then return end
    local qty = if typeof(quantity) == "number" then quantity else 1
    local success, err = InventoryManager.buyFromShop(player, shopId, itemIndex, qty)
    Remotes.BuyResult:FireClient(player, success, err)
end)

Remotes.SellItem.OnServerEvent:Connect(function(player, shopId, backpackSlot, quantity)
    if typeof(shopId) ~= "string" or typeof(backpackSlot) ~= "number" then return end
    local qty = if typeof(quantity) == "number" then quantity else 1
    local success, err = InventoryManager.sellToShop(player, shopId, backpackSlot, qty)
    Remotes.SellResult:FireClient(player, success, err)
end)
```
