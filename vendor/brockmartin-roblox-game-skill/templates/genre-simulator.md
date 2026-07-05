# Simulator Genre Template

---

## 1. Genre Overview

**Load this template when:** Building a simulator-genre Roblox game (collect, upgrade, unlock, prestige).

### The Core Loop

Simulators are the highest-grossing and most-played genre on Roblox. Every simulator follows a tightly coupled feedback loop:

```
COLLECT --> UPGRADE --> UNLOCK ZONES --> PRESTIGE/REBIRTH
   ^                                          |
   |__________________________________________|
        (reset with permanent multiplier)
```

1. **Collect** -- The player taps, clicks, or auto-collects a resource (coins, gems, fruit, honey, fish). This is the atomic action repeated thousands of times per session.
2. **Upgrade** -- Collected currency buys permanent multipliers (click power, auto-collect speed, luck, storage capacity). Each upgrade makes collecting faster.
3. **Unlock Zones** -- Currency thresholds gate new areas. Each zone has better resource nodes, rarer pets, and higher yields. Zones create visible goals on the horizon.
4. **Prestige/Rebirth** -- The player resets most progress in exchange for a permanent multiplier that stacks across rebirths. This extends the game's lifespan by orders of magnitude.

### Why Simulators Are Addictive

- **Numbers going up** -- Humans are wired to enjoy watching quantities grow. The bigger the numbers, the more dopamine. Start at 1 coin/tap and scale to millions.
- **Collection completionism** -- Pet indexes, badge walls, zone completion percentages. Players want to fill every slot.
- **Visible progression** -- New zones, bigger pets, flashier effects. Every session should feel like a step forward.
- **Social comparison** -- Leaderboards, rare pets displayed overhead, exclusive zones. Players flex on each other.
- **Idle accumulation** -- Auto-collect and offline rewards ensure the player always has something waiting when they return.

### Reference Games

| Game | Notable Mechanic |
|---|---|
| **Pet Simulator 99** | Massive pet collection with merging, enchanting, and tiered rarity. Eggs with visible odds. |
| **Bee Swarm Simulator** | Deep progression with unique bee abilities, quests, and zone-gated content. |
| **Blox Fruits** | Action-combat hybrid with fruit collection, leveling, and zone progression across seas. |
| **Anime Defenders** | Tower defense + simulator hybrid with unit gacha, upgrading, and wave-based progression. |
| **Muscle Legends** | Classic click-to-grow with rebirths, pets, and zone unlocks. |

---

## 2. Architecture Blueprint

Build on the base scaffold from `templates/game-scaffold.md`. The following extends it with simulator-specific modules.

### Folder Structure

```
game
+-- ServerScriptService
|   +-- Main.server.lua                  -- Bootstrapper: requires and inits all services
|   +-- Services/
|   |   +-- CollectionService.lua        -- Resource node spawning, collection logic, multiplier application
|   |   +-- PetService.lua               -- Egg hatching, pet inventory, equip/unequip, leveling, merging
|   |   +-- ZoneService.lua              -- Zone unlock checks, zone gates, zone-specific resource tables
|   |   +-- UpgradeService.lua           -- Permanent upgrade purchases, multiplier calculations
|   |   +-- PrestigeService.lua          -- Rebirth logic, requirement checks, permanent multiplier grants
|   |   +-- ShopService.lua              -- GamePass/DevProduct handling, shop validation
|   |   +-- DataService.lua              -- ProfileService/ProfileStore wrapper for player data
|   |   +-- LeaderboardService.lua       -- Global leaderboards (rebirths, total collected, rarest pet)
|   +-- Components/
|       +-- ResourceNode.lua             -- Server-side resource node behavior (respawn, depletion)
|       +-- ZoneGate.lua                 -- Zone entry validation, teleportation
+-- ServerStorage
|   +-- Assets/
|   |   +-- Pets/                        -- Pet models (Common/ Uncommon/ Rare/ Epic/ Legendary/)
|   |   +-- Eggs/                        -- Egg models per zone
|   |   +-- ResourceNodes/              -- Resource node models per zone
|   |   +-- Zones/                       -- Zone map chunks (streamed on demand)
|   +-- Modules/
|       +-- DataSchema.lua               -- Player data shape, defaults, migrations
|       +-- PetDefinitions.lua           -- All pet stats, rarity, zone availability
|       +-- UpgradeDefinitions.lua       -- Upgrade costs, multipliers, max levels
|       +-- ZoneDefinitions.lua          -- Zone unlock costs, resource tables, spawn configs
+-- ReplicatedStorage
|   +-- Remotes/
|   |   +-- CollectResource (RemoteEvent)
|   |   +-- HatchEgg (RemoteEvent)
|   |   +-- EquipPet (RemoteEvent)
|   |   +-- UnequipPet (RemoteEvent)
|   |   +-- BuyUpgrade (RemoteEvent)
|   |   +-- Prestige (RemoteEvent)
|   |   +-- UnlockZone (RemoteEvent)
|   |   +-- GetPlayerData (RemoteFunction)
|   +-- Modules/
|   |   +-- Constants.lua                -- Shared constants (max pets equipped, max storage, rarity colors)
|   |   +-- Types.lua                    -- Shared type definitions
|   |   +-- FormatNumber.lua             -- Number abbreviation (1.2M, 3.4B, 5.6T)
|   +-- Assets/
|       +-- Effects/                     -- Collection particles, hatch animations, prestige VFX
|       +-- UI/                          -- Shared UI prefabs
+-- StarterGui
|   +-- HUD (ScreenGui)
|   |   +-- CurrencyDisplay.Frame       -- Shows coins, gems, rebirth count
|   |   +-- CollectionCounter.Frame     -- Floating +coin text
|   +-- PetMenu (ScreenGui)             -- Pet inventory grid, equip/unequip, pet details
|   +-- ShopMenu (ScreenGui)            -- Upgrades, eggs, GamePasses, DevProducts
|   +-- ZoneMenu (ScreenGui)            -- Zone map with unlock status
|   +-- PrestigeMenu (ScreenGui)        -- Rebirth confirmation, multiplier preview
|   +-- Controllers/
|       +-- HUDController.client.lua
|       +-- PetMenuController.client.lua
|       +-- ShopController.client.lua
|       +-- CollectionController.client.lua  -- Click/tap detection, VFX triggers
+-- StarterPlayer
|   +-- StarterPlayerScripts/
|       +-- ClientMain.client.lua        -- Client bootstrapper
|       +-- Controllers/
|           +-- InputController.lua      -- Click/tap input handling
|           +-- CameraController.lua     -- Zone-aware camera
|           +-- PetDisplayController.lua -- Render equipped pets following player
+-- Workspace
    +-- Zones/
    |   +-- Zone1_Grasslands/
    |   |   +-- ResourceNodes/           -- Folder of clickable resource parts
    |   |   +-- EggStation.Model         -- Where players hatch eggs
    |   |   +-- ZoneGate_Zone2.Model     -- Gate to next zone
    |   +-- Zone2_Desert/
    |   +-- Zone3_Arctic/
    |   +-- Zone4_Volcano/
    |   +-- Zone5_Space/
    +-- Spawn/
```

### Key Module Responsibilities

| Module | Side | Responsibility |
|---|---|---|
| `CollectionService` | Server | Validates collection requests, applies multipliers, awards currency |
| `PetService` | Server | Hatches eggs with weighted RNG, manages pet inventory, equip slots, leveling |
| `ZoneService` | Server | Validates zone unlock purchases, manages zone gates, tracks unlocked zones |
| `UpgradeService` | Server | Validates upgrade purchases, calculates composite multiplier |
| `PrestigeService` | Server | Validates prestige requirements, resets progress, applies permanent multiplier |
| `ShopService` | Server | Handles GamePass/DevProduct purchases, currency packs |
| `DataService` | Server | ProfileService wrapper for save/load, session locking, data migrations |
| `CollectionController` | Client | Detects clicks/taps on resource nodes, fires RemoteEvent, plays VFX |
| `PetDisplayController` | Client | Renders equipped pets following the player character |

---

## 3. Core Systems (Luau Code)

All code below is server-authoritative. The client sends intent; the server validates and mutates state.

### 3.1 Data Schema

Define the player data shape. All systems read from and write to this structure.

```luau
-- ServerStorage/Modules/DataSchema.lua
local DataSchema = {}

function DataSchema.getDefaults(): { [string]: any }
    return {
        -- Currency
        Coins = 0,
        Gems = 0,
        TotalCoinsEarned = 0,

        -- Upgrades (level-based, starting at 0)
        Upgrades = {
            ClickPower = 0,
            AutoCollectSpeed = 0,
            Luck = 0,
            StorageCapacity = 0,
        },

        -- Pets
        Pets = {},          -- array of PetData: { Id, Name, Rarity, Level, XP, Equipped }
        MaxPetStorage = 25,
        MaxEquipped = 3,

        -- Zones
        UnlockedZones = { "Zone1_Grasslands" },
        CurrentZone = "Zone1_Grasslands",

        -- Prestige
        Rebirths = 0,
        TotalRebirths = 0,

        -- Timestamps
        LastLogin = 0,
        PlayTime = 0,
    }
end

return DataSchema
```

### 3.2 Collection Mechanic

Players click/tap resource nodes to collect currency. The amount is multiplied by upgrades, pets, rebirths, and GamePasses.

```luau
-- ServerScriptService/Services/CollectionService.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local CollectionService = {}

-- Dependencies (injected via init)
local DataService
local UpgradeService
local PetService

-- Configuration
local BASE_COLLECT_AMOUNT = 1
local COLLECTION_COOLDOWN = 0.2 -- seconds between collections per player
local MAX_COLLECT_DISTANCE = 15

-- Rate limiting
local lastCollectTime: { [number]: number } = {}

function CollectionService.init(services)
    DataService = services.DataService
    UpgradeService = services.UpgradeService
    PetService = services.PetService
end

function CollectionService.start()
    local collectRemote = ReplicatedStorage.Remotes:FindFirstChild("CollectResource")
    if not collectRemote then
        collectRemote = Instance.new("RemoteEvent")
        collectRemote.Name = "CollectResource"
        collectRemote.Parent = ReplicatedStorage.Remotes
    end

    collectRemote.OnServerEvent:Connect(function(player: Player, nodeInstance: Instance)
        CollectionService._handleCollect(player, nodeInstance)
    end)

    Players.PlayerRemoving:Connect(function(player: Player)
        lastCollectTime[player.UserId] = nil
    end)
end

function CollectionService._handleCollect(player: Player, nodeInstance: Instance)
    -- Type validation
    if typeof(nodeInstance) ~= "Instance" then
        return
    end

    -- Verify node exists and is a valid resource node
    if not nodeInstance:IsA("BasePart") then
        return
    end
    if not nodeInstance:GetAttribute("ResourceNode") then
        return
    end
    if nodeInstance:GetAttribute("Depleted") then
        return
    end

    -- Rate limiting
    local userId = player.UserId
    local now = os.clock()
    local lastTime = lastCollectTime[userId] or 0
    if now - lastTime < COLLECTION_COOLDOWN then
        return
    end
    lastCollectTime[userId] = now

    -- Distance check
    local character = player.Character
    if not character then
        return
    end
    local primaryPart = character:FindFirstChild("HumanoidRootPart")
    if not primaryPart then
        return
    end
    local distance = (primaryPart.Position - nodeInstance.Position).Magnitude
    if distance > MAX_COLLECT_DISTANCE then
        return
    end

    -- Calculate collection amount with all multipliers
    local amount = CollectionService._calculateAmount(player, nodeInstance)

    -- Award currency
    local data = DataService.getData(player)
    if not data then
        return
    end
    data.Coins += amount
    data.TotalCoinsEarned += amount

    -- Deplete node temporarily
    CollectionService._depleteNode(nodeInstance)

    -- Notify client for VFX
    local collectRemote = ReplicatedStorage.Remotes.CollectResource
    collectRemote:FireClient(player, nodeInstance, amount)
end

function CollectionService._calculateAmount(player: Player, nodeInstance: Instance): number
    local data = DataService.getData(player)
    if not data then
        return BASE_COLLECT_AMOUNT
    end

    -- Base amount from node's zone
    local zoneMultiplier = nodeInstance:GetAttribute("ZoneMultiplier") or 1

    -- Click power upgrade multiplier
    local clickMultiplier = UpgradeService.getMultiplier(player, "ClickPower")

    -- Pet bonus (sum of equipped pet boosts)
    local petMultiplier = PetService.getEquippedBoost(player)

    -- Rebirth multiplier: 1 + 0.1 * rebirths
    local rebirthMultiplier = 1 + 0.1 * (data.Rebirths or 0)

    -- GamePass multiplier (2x coins if owned)
    local gamePassMultiplier = 1
    if player:GetAttribute("CoinMultiplier") then
        gamePassMultiplier = player:GetAttribute("CoinMultiplier")
    end

    local total = BASE_COLLECT_AMOUNT
        * zoneMultiplier
        * clickMultiplier
        * petMultiplier
        * rebirthMultiplier
        * gamePassMultiplier

    return math.floor(total)
end

function CollectionService._depleteNode(nodeInstance: Instance)
    nodeInstance:SetAttribute("Depleted", true)
    nodeInstance.Transparency = 0.8

    local respawnTime = nodeInstance:GetAttribute("RespawnTime") or 3

    task.delay(respawnTime, function()
        if nodeInstance and nodeInstance.Parent then
            nodeInstance:SetAttribute("Depleted", false)
            nodeInstance.Transparency = 0
        end
    end)
end

return CollectionService
```

**Client-side collection controller** (click detection and VFX):

```luau
-- StarterGui/Controllers/CollectionController.client.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")

local player = Players.LocalPlayer
local mouse = player:GetMouse()

local collectRemote = ReplicatedStorage:WaitForChild("Remotes"):WaitForChild("CollectResource")

-- VFX: floating +coins text
local function showCollectVFX(node: Instance, amount: number)
    local billboard = Instance.new("BillboardGui")
    billboard.Size = UDim2.fromOffset(100, 40)
    billboard.StudsOffset = Vector3.new(0, 3, 0)
    billboard.Adornee = node
    billboard.Parent = player.PlayerGui

    local label = Instance.new("TextLabel")
    label.Size = UDim2.fromScale(1, 1)
    label.BackgroundTransparency = 1
    label.Text = "+" .. tostring(amount)
    label.TextColor3 = Color3.fromRGB(255, 215, 0)
    label.TextScaled = true
    label.Font = Enum.Font.GothamBold
    label.Parent = billboard

    -- Animate upward and fade
    local tweenService = game:GetService("TweenService")
    local tweenInfo = TweenInfo.new(0.8, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)

    tweenService:Create(billboard, tweenInfo, {
        StudsOffset = Vector3.new(0, 6, 0),
    }):Play()

    tweenService:Create(label, tweenInfo, {
        TextTransparency = 1,
    }):Play()

    task.delay(0.8, function()
        billboard:Destroy()
    end)
end

-- Click/tap to collect
local function onInputBegan(input: InputObject, gameProcessed: boolean)
    if gameProcessed then
        return
    end

    local isClick = input.UserInputType == Enum.UserInputType.MouseButton1
    local isTap = input.UserInputType == Enum.UserInputType.Touch

    if not isClick and not isTap then
        return
    end

    local target = mouse.Target
    if not target then
        return
    end
    if not target:GetAttribute("ResourceNode") then
        return
    end
    if target:GetAttribute("Depleted") then
        return
    end

    collectRemote:FireServer(target)
end

-- Listen for server confirmation to play VFX
collectRemote.OnClientEvent:Connect(function(node: Instance, amount: number)
    showCollectVFX(node, amount)
end)

UserInputService.InputBegan:Connect(onInputBegan)
```

### 3.3 Pet / Companion System

Full production-ready pet system: egg hatching with weighted rarity, pet inventory, equip/unequip, leveling, and storage.

**Pet definitions (shared config):**

```luau
-- ServerStorage/Modules/PetDefinitions.lua
local PetDefinitions = {}

-- Rarity weights (must sum to 100 within each egg)
PetDefinitions.Rarities = {
    Common    = { Color = Color3.fromRGB(180, 180, 180), Weight = 60 },
    Uncommon  = { Color = Color3.fromRGB(50, 200, 50),   Weight = 25 },
    Rare      = { Color = Color3.fromRGB(50, 100, 255),  Weight = 10 },
    Epic      = { Color = Color3.fromRGB(160, 50, 255),  Weight = 4  },
    Legendary = { Color = Color3.fromRGB(255, 200, 50),  Weight = 1  },
}

-- Pet catalog: keyed by pet ID
PetDefinitions.Pets = {
    -- Zone 1 Pets
    dog   = { Name = "Dog",   Rarity = "Common",    BaseBoost = 1.05, Zone = "Zone1_Grasslands", Model = "Dog"   },
    cat   = { Name = "Cat",   Rarity = "Common",    BaseBoost = 1.05, Zone = "Zone1_Grasslands", Model = "Cat"   },
    bunny = { Name = "Bunny", Rarity = "Uncommon",  BaseBoost = 1.15, Zone = "Zone1_Grasslands", Model = "Bunny" },
    fox   = { Name = "Fox",   Rarity = "Rare",      BaseBoost = 1.30, Zone = "Zone1_Grasslands", Model = "Fox"   },
    eagle = { Name = "Eagle", Rarity = "Epic",      BaseBoost = 1.60, Zone = "Zone1_Grasslands", Model = "Eagle" },
    dragon= { Name = "Dragon",Rarity = "Legendary", BaseBoost = 2.00, Zone = "Zone1_Grasslands", Model = "Dragon"},

    -- Zone 2 Pets
    cactus_cat = { Name = "Cactus Cat", Rarity = "Common",    BaseBoost = 1.10, Zone = "Zone2_Desert", Model = "CactusCat" },
    scorpion   = { Name = "Scorpion",   Rarity = "Uncommon",  BaseBoost = 1.25, Zone = "Zone2_Desert", Model = "Scorpion"  },
    sphinx     = { Name = "Sphinx",     Rarity = "Rare",      BaseBoost = 1.50, Zone = "Zone2_Desert", Model = "Sphinx"    },
    phoenix    = { Name = "Phoenix",    Rarity = "Epic",      BaseBoost = 1.80, Zone = "Zone2_Desert", Model = "Phoenix"   },
    anubis     = { Name = "Anubis",     Rarity = "Legendary", BaseBoost = 2.50, Zone = "Zone2_Desert", Model = "Anubis"    },
}

-- Egg definitions: which pets can hatch from which egg
PetDefinitions.Eggs = {
    BasicEgg = {
        Name = "Basic Egg",
        Cost = 100,
        Zone = "Zone1_Grasslands",
        Pets = { "dog", "cat", "bunny", "fox", "eagle", "dragon" },
    },
    DesertEgg = {
        Name = "Desert Egg",
        Cost = 5000,
        Zone = "Zone2_Desert",
        Pets = { "cactus_cat", "scorpion", "sphinx", "phoenix", "anubis" },
    },
}

-- Leveling: XP required per level
-- Formula: xpRequired = baseXP * level^1.5
PetDefinitions.LevelConfig = {
    BaseXP = 50,
    MaxLevel = 25,
    BoostPerLevel = 0.02, -- each level adds 2% to base boost
}

return PetDefinitions
```

**Pet service (server-side, production-ready):**

```luau
-- ServerScriptService/Services/PetService.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")
local Players = game:GetService("Players")
local HttpService = game:GetService("HttpService")

local PetDefinitions = require(ServerStorage.Modules.PetDefinitions)

local PetService = {}

-- Dependencies
local DataService

-- Rate limiting
local hatchCooldowns: { [number]: number } = {}
local HATCH_COOLDOWN = 1.0

function PetService.init(services)
    DataService = services.DataService
end

function PetService.start()
    local remotes = ReplicatedStorage.Remotes

    local hatchRemote = remotes:FindFirstChild("HatchEgg") or Instance.new("RemoteEvent")
    hatchRemote.Name = "HatchEgg"
    hatchRemote.Parent = remotes

    local equipRemote = remotes:FindFirstChild("EquipPet") or Instance.new("RemoteEvent")
    equipRemote.Name = "EquipPet"
    equipRemote.Parent = remotes

    local unequipRemote = remotes:FindFirstChild("UnequipPet") or Instance.new("RemoteEvent")
    unequipRemote.Name = "UnequipPet"
    unequipRemote.Parent = remotes

    hatchRemote.OnServerEvent:Connect(function(player: Player, eggId: string)
        PetService._handleHatch(player, eggId)
    end)

    equipRemote.OnServerEvent:Connect(function(player: Player, petUUID: string)
        PetService._handleEquip(player, petUUID)
    end)

    unequipRemote.OnServerEvent:Connect(function(player: Player, petUUID: string)
        PetService._handleUnequip(player, petUUID)
    end)

    Players.PlayerRemoving:Connect(function(player: Player)
        hatchCooldowns[player.UserId] = nil
    end)
end

-------------------------------------------------
-- EGG HATCHING with weighted rarity RNG
-------------------------------------------------

function PetService._handleHatch(player: Player, eggId: string)
    -- Type validation
    if typeof(eggId) ~= "string" then
        return
    end

    -- Rate limiting
    local userId = player.UserId
    local now = os.clock()
    if (hatchCooldowns[userId] or 0) > now - HATCH_COOLDOWN then
        return
    end
    hatchCooldowns[userId] = now

    -- Validate egg exists
    local eggDef = PetDefinitions.Eggs[eggId]
    if not eggDef then
        return
    end

    -- Validate player data
    local data = DataService.getData(player)
    if not data then
        return
    end

    -- Check pet storage capacity
    if #data.Pets >= data.MaxPetStorage then
        ReplicatedStorage.Remotes.HatchEgg:FireClient(player, nil, "PET_STORAGE_FULL")
        return
    end

    -- Check zone unlock
    local zoneUnlocked = false
    for _, zone in data.UnlockedZones do
        if zone == eggDef.Zone then
            zoneUnlocked = true
            break
        end
    end
    if not zoneUnlocked then
        return
    end

    -- Check and deduct cost
    if data.Coins < eggDef.Cost then
        return
    end
    data.Coins -= eggDef.Cost

    -- Roll for pet using weighted rarity
    local rolledPetId = PetService._rollPet(eggDef, player)
    local petDef = PetDefinitions.Pets[rolledPetId]

    -- Create pet instance data
    local newPet = {
        UUID = HttpService:GenerateGUID(false),
        Id = rolledPetId,
        Name = petDef.Name,
        Rarity = petDef.Rarity,
        Level = 1,
        XP = 0,
        Equipped = false,
    }

    table.insert(data.Pets, newPet)

    -- Notify client with hatched pet data
    ReplicatedStorage.Remotes.HatchEgg:FireClient(player, newPet, "SUCCESS")
end

function PetService._rollPet(eggDef: { Pets: { string } }, player: Player): string
    -- Build weighted pool from pets in this egg
    local pool: { { petId: string, weight: number } } = {}
    local totalWeight = 0

    for _, petId in eggDef.Pets do
        local petDef = PetDefinitions.Pets[petId]
        if petDef then
            local rarityInfo = PetDefinitions.Rarities[petDef.Rarity]
            if rarityInfo then
                local weight = rarityInfo.Weight

                -- Apply luck multiplier: boosts rare+ drop rates
                local data = DataService.getData(player)
                if data then
                    local luckLevel = data.Upgrades.Luck or 0
                    -- Luck increases rare weights, decreases common weights
                    if petDef.Rarity ~= "Common" then
                        weight = weight * (1 + luckLevel * 0.05)
                    end
                end

                -- Apply 2x luck GamePass
                if player:GetAttribute("LuckyEgg") and petDef.Rarity ~= "Common" then
                    weight = weight * 2
                end

                totalWeight += weight
                table.insert(pool, { petId = petId, weight = totalWeight })
            end
        end
    end

    -- Weighted random selection
    local roll = math.random() * totalWeight
    for _, entry in pool do
        if roll <= entry.weight then
            return entry.petId
        end
    end

    -- Fallback: return first pet
    return eggDef.Pets[1]
end

-------------------------------------------------
-- EQUIP / UNEQUIP
-------------------------------------------------

function PetService._handleEquip(player: Player, petUUID: string)
    if typeof(petUUID) ~= "string" then
        return
    end

    local data = DataService.getData(player)
    if not data then
        return
    end

    -- Count currently equipped
    local equippedCount = 0
    local targetPet = nil

    for _, pet in data.Pets do
        if pet.Equipped then
            equippedCount += 1
        end
        if pet.UUID == petUUID then
            targetPet = pet
        end
    end

    if not targetPet then
        return
    end

    if targetPet.Equipped then
        return -- already equipped
    end

    if equippedCount >= data.MaxEquipped then
        return -- no slots available
    end

    targetPet.Equipped = true

    -- Notify client to render pet following player
    ReplicatedStorage.Remotes.EquipPet:FireClient(player, targetPet)
end

function PetService._handleUnequip(player: Player, petUUID: string)
    if typeof(petUUID) ~= "string" then
        return
    end

    local data = DataService.getData(player)
    if not data then
        return
    end

    for _, pet in data.Pets do
        if pet.UUID == petUUID and pet.Equipped then
            pet.Equipped = false
            ReplicatedStorage.Remotes.UnequipPet:FireClient(player, petUUID)
            return
        end
    end
end

-------------------------------------------------
-- PET LEVELING
-------------------------------------------------

function PetService.addPetXP(player: Player, petUUID: string, xpAmount: number)
    local data = DataService.getData(player)
    if not data then
        return
    end

    for _, pet in data.Pets do
        if pet.UUID == petUUID then
            local config = PetDefinitions.LevelConfig
            if pet.Level >= config.MaxLevel then
                return
            end

            pet.XP += xpAmount
            local requiredXP = config.BaseXP * pet.Level ^ 1.5

            while pet.XP >= requiredXP and pet.Level < config.MaxLevel do
                pet.XP -= requiredXP
                pet.Level += 1
                requiredXP = config.BaseXP * pet.Level ^ 1.5
            end

            return
        end
    end
end

-------------------------------------------------
-- STAT CALCULATIONS
-------------------------------------------------

function PetService.getEquippedBoost(player: Player): number
    local data = DataService.getData(player)
    if not data then
        return 1
    end

    local totalBoost = 1

    for _, pet in data.Pets do
        if pet.Equipped then
            local petDef = PetDefinitions.Pets[pet.Id]
            if petDef then
                local config = PetDefinitions.LevelConfig
                local levelBonus = 1 + (pet.Level - 1) * config.BoostPerLevel
                totalBoost *= petDef.BaseBoost * levelBonus
            end
        end
    end

    return totalBoost
end

function PetService.getPetCount(player: Player): number
    local data = DataService.getData(player)
    if not data then
        return 0
    end
    return #data.Pets
end

return PetService
```

### 3.4 Zone System

Zones unlock with currency thresholds. Each zone has better resources and exclusive eggs/pets.

```luau
-- ServerStorage/Modules/ZoneDefinitions.lua
local ZoneDefinitions = {}

ZoneDefinitions.Zones = {
    Zone1_Grasslands = {
        Name = "Grasslands",
        Order = 1,
        UnlockCost = 0,            -- Starting zone, free
        ResourceMultiplier = 1,
        RespawnTime = 3,
        NodeCount = 20,
    },
    Zone2_Desert = {
        Name = "Desert",
        Order = 2,
        UnlockCost = 10000,
        ResourceMultiplier = 5,
        RespawnTime = 2.5,
        NodeCount = 25,
    },
    Zone3_Arctic = {
        Name = "Arctic",
        Order = 3,
        UnlockCost = 100000,
        ResourceMultiplier = 25,
        RespawnTime = 2,
        NodeCount = 30,
    },
    Zone4_Volcano = {
        Name = "Volcano",
        Order = 4,
        UnlockCost = 1000000,
        ResourceMultiplier = 125,
        RespawnTime = 1.5,
        NodeCount = 35,
    },
    Zone5_Space = {
        Name = "Space",
        Order = 5,
        UnlockCost = 10000000,
        ResourceMultiplier = 625,
        RespawnTime = 1,
        NodeCount = 40,
    },
}

return ZoneDefinitions
```

```luau
-- ServerScriptService/Services/ZoneService.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local ZoneDefinitions = require(ServerStorage.Modules.ZoneDefinitions)

local ZoneService = {}

local DataService

function ZoneService.init(services)
    DataService = services.DataService
end

function ZoneService.start()
    local unlockRemote = ReplicatedStorage.Remotes:FindFirstChild("UnlockZone")
        or Instance.new("RemoteEvent")
    unlockRemote.Name = "UnlockZone"
    unlockRemote.Parent = ReplicatedStorage.Remotes

    unlockRemote.OnServerEvent:Connect(function(player: Player, zoneId: string)
        ZoneService._handleUnlock(player, zoneId)
    end)
end

function ZoneService._handleUnlock(player: Player, zoneId: string)
    if typeof(zoneId) ~= "string" then
        return
    end

    local zoneDef = ZoneDefinitions.Zones[zoneId]
    if not zoneDef then
        return
    end

    local data = DataService.getData(player)
    if not data then
        return
    end

    -- Check if already unlocked
    for _, unlockedZone in data.UnlockedZones do
        if unlockedZone == zoneId then
            return
        end
    end

    -- Check if previous zone is unlocked (enforce sequential unlock)
    local previousUnlocked = false
    for prevId, prevDef in ZoneDefinitions.Zones do
        if prevDef.Order == zoneDef.Order - 1 then
            for _, unlockedZone in data.UnlockedZones do
                if unlockedZone == prevId then
                    previousUnlocked = true
                    break
                end
            end
            break
        end
    end

    if zoneDef.Order > 1 and not previousUnlocked then
        return
    end

    -- Check cost
    if data.Coins < zoneDef.UnlockCost then
        return
    end

    -- Deduct and unlock
    data.Coins -= zoneDef.UnlockCost
    table.insert(data.UnlockedZones, zoneId)

    ReplicatedStorage.Remotes.UnlockZone:FireClient(player, zoneId, "SUCCESS")
end

function ZoneService.isZoneUnlocked(player: Player, zoneId: string): boolean
    local data = DataService.getData(player)
    if not data then
        return false
    end

    for _, zone in data.UnlockedZones do
        if zone == zoneId then
            return true
        end
    end
    return false
end

return ZoneService
```

### 3.5 Upgrade System

Permanent multipliers purchased with currency. Cost scales exponentially.

```luau
-- ServerStorage/Modules/UpgradeDefinitions.lua
local UpgradeDefinitions = {}

-- cost = BaseCost * CostMultiplier ^ currentLevel
UpgradeDefinitions.Upgrades = {
    ClickPower = {
        Name = "Click Power",
        Description = "Increases coins per click",
        BaseCost = 50,
        CostMultiplier = 1.35,
        MaxLevel = 100,
        MultiplierPerLevel = 0.15,  -- each level adds 15% to collection
    },
    AutoCollectSpeed = {
        Name = "Auto Collect",
        Description = "Automatically collects nearby resources",
        BaseCost = 200,
        CostMultiplier = 1.50,
        MaxLevel = 50,
        MultiplierPerLevel = 0.10,
    },
    Luck = {
        Name = "Luck",
        Description = "Increases rare pet drop rates",
        BaseCost = 500,
        CostMultiplier = 1.60,
        MaxLevel = 30,
        MultiplierPerLevel = 0.05,  -- 5% boost to rare weights per level
    },
    StorageCapacity = {
        Name = "Pet Storage",
        Description = "Increases maximum pet storage",
        BaseCost = 300,
        CostMultiplier = 1.40,
        MaxLevel = 40,
        MultiplierPerLevel = 5,     -- adds 5 storage slots per level (used differently)
    },
}

return UpgradeDefinitions
```

```luau
-- ServerScriptService/Services/UpgradeService.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local UpgradeDefinitions = require(ServerStorage.Modules.UpgradeDefinitions)

local UpgradeService = {}

local DataService

function UpgradeService.init(services)
    DataService = services.DataService
end

function UpgradeService.start()
    local buyRemote = ReplicatedStorage.Remotes:FindFirstChild("BuyUpgrade")
        or Instance.new("RemoteEvent")
    buyRemote.Name = "BuyUpgrade"
    buyRemote.Parent = ReplicatedStorage.Remotes

    buyRemote.OnServerEvent:Connect(function(player: Player, upgradeId: string)
        UpgradeService._handleBuy(player, upgradeId)
    end)
end

function UpgradeService._handleBuy(player: Player, upgradeId: string)
    if typeof(upgradeId) ~= "string" then
        return
    end

    local upgradeDef = UpgradeDefinitions.Upgrades[upgradeId]
    if not upgradeDef then
        return
    end

    local data = DataService.getData(player)
    if not data then
        return
    end

    local currentLevel = data.Upgrades[upgradeId] or 0
    if currentLevel >= upgradeDef.MaxLevel then
        return
    end

    -- Exponential cost: baseCost * multiplier ^ level
    local cost = math.floor(upgradeDef.BaseCost * upgradeDef.CostMultiplier ^ currentLevel)
    if data.Coins < cost then
        return
    end

    data.Coins -= cost
    data.Upgrades[upgradeId] = currentLevel + 1

    -- Special handling for storage capacity upgrade
    if upgradeId == "StorageCapacity" then
        data.MaxPetStorage = 25 + (currentLevel + 1) * 5
    end

    ReplicatedStorage.Remotes.BuyUpgrade:FireClient(player, upgradeId, currentLevel + 1, data.Coins)
end

function UpgradeService.getMultiplier(player: Player, upgradeId: string): number
    local data = DataService.getData(player)
    if not data then
        return 1
    end

    local upgradeDef = UpgradeDefinitions.Upgrades[upgradeId]
    if not upgradeDef then
        return 1
    end

    local level = data.Upgrades[upgradeId] or 0
    return 1 + level * upgradeDef.MultiplierPerLevel
end

function UpgradeService.getCost(player: Player, upgradeId: string): number?
    local upgradeDef = UpgradeDefinitions.Upgrades[upgradeId]
    if not upgradeDef then
        return nil
    end

    local data = DataService.getData(player)
    if not data then
        return nil
    end

    local currentLevel = data.Upgrades[upgradeId] or 0
    if currentLevel >= upgradeDef.MaxLevel then
        return nil
    end

    return math.floor(upgradeDef.BaseCost * upgradeDef.CostMultiplier ^ currentLevel)
end

return UpgradeService
```

### 3.6 Prestige / Rebirth System

Reset progress for a permanent multiplier. Escalating requirements keep players pushing further each cycle.

```luau
-- ServerScriptService/Services/PrestigeService.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local DataSchema = require(ServerStorage.Modules.DataSchema)

local PrestigeService = {}

local DataService

-- Rebirth requirement: baseRequirement * multiplier ^ currentRebirths
local BASE_REQUIREMENT = 10000
local REQUIREMENT_MULTIPLIER = 2.5
local MAX_REBIRTHS = 100

function PrestigeService.init(services)
    DataService = services.DataService
end

function PrestigeService.start()
    local prestigeRemote = ReplicatedStorage.Remotes:FindFirstChild("Prestige")
        or Instance.new("RemoteEvent")
    prestigeRemote.Name = "Prestige"
    prestigeRemote.Parent = ReplicatedStorage.Remotes

    prestigeRemote.OnServerEvent:Connect(function(player: Player)
        PrestigeService._handlePrestige(player)
    end)
end

function PrestigeService._handlePrestige(player: Player)
    local data = DataService.getData(player)
    if not data then
        return
    end

    if data.Rebirths >= MAX_REBIRTHS then
        return
    end

    -- Calculate requirement for next rebirth
    local requirement = PrestigeService.getRequirement(data.Rebirths)

    if data.TotalCoinsEarned < requirement then
        ReplicatedStorage.Remotes.Prestige:FireClient(player, "INSUFFICIENT", requirement)
        return
    end

    -- Store persistent values before reset
    local newRebirths = data.Rebirths + 1
    local totalRebirths = data.TotalRebirths + 1
    local pets = data.Pets          -- Pets survive rebirth
    local maxPetStorage = data.MaxPetStorage

    -- Reset to defaults
    local defaults = DataSchema.getDefaults()
    for key, value in defaults do
        -- Only reset non-persistent fields
        if key ~= "Pets" and key ~= "MaxPetStorage"
            and key ~= "Rebirths" and key ~= "TotalRebirths"
            and key ~= "LastLogin" and key ~= "PlayTime" then
            data[key] = value
        end
    end

    -- Restore persistent data
    data.Rebirths = newRebirths
    data.TotalRebirths = totalRebirths
    data.Pets = pets
    data.MaxPetStorage = maxPetStorage

    -- Unequip all pets on rebirth (zones reset, pets may be zone-locked)
    for _, pet in data.Pets do
        pet.Equipped = false
    end

    -- Notify client
    local newMultiplier = PrestigeService.getMultiplier(newRebirths)
    ReplicatedStorage.Remotes.Prestige:FireClient(player, "SUCCESS", newRebirths, newMultiplier)
end

function PrestigeService.getRequirement(currentRebirths: number): number
    return math.floor(BASE_REQUIREMENT * REQUIREMENT_MULTIPLIER ^ currentRebirths)
end

function PrestigeService.getMultiplier(rebirths: number): number
    -- Each rebirth gives +10% permanent multiplier
    -- Formula: 1 + 0.1 * rebirths
    return 1 + 0.1 * rebirths
end

return PrestigeService
```

### 3.7 Server Bootstrapper

Wire everything together with the `init/start` pattern to avoid circular dependencies.

```luau
-- ServerScriptService/Main.server.lua
local ServerStorage = game:GetService("ServerStorage")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

-- Create Remotes folder if it does not exist
if not ReplicatedStorage:FindFirstChild("Remotes") then
    local folder = Instance.new("Folder")
    folder.Name = "Remotes"
    folder.Parent = ReplicatedStorage
end

-- Require all services
local DataService       = require(script.Parent.Services.DataService)
local CollectionService = require(script.Parent.Services.CollectionService)
local PetService        = require(script.Parent.Services.PetService)
local ZoneService       = require(script.Parent.Services.ZoneService)
local UpgradeService    = require(script.Parent.Services.UpgradeService)
local PrestigeService   = require(script.Parent.Services.PrestigeService)
local ShopService       = require(script.Parent.Services.ShopService)

-- Build services table for dependency injection
local services = {
    DataService       = DataService,
    CollectionService = CollectionService,
    PetService        = PetService,
    ZoneService       = ZoneService,
    UpgradeService    = UpgradeService,
    PrestigeService   = PrestigeService,
    ShopService       = ShopService,
}

-- Init phase: inject dependencies (no cross-calls yet)
for _, service in services do
    if service.init then
        service.init(services)
    end
end

-- Start phase: connect events, begin game logic
for _, service in services do
    if service.start then
        service.start()
    end
end

print("[Simulator] All services initialized and started")
```

---

## 4. Progression Design

### Currency Curves

Use exponential scaling so early upgrades feel cheap and late upgrades feel aspirational.

```
Upgrade Cost Formula:
  cost(level) = baseCost * costMultiplier ^ level

Examples (ClickPower, baseCost=50, multiplier=1.35):
  Level 0 -> 1:   50 coins
  Level 5 -> 6:   222 coins
  Level 10 -> 11: 985 coins
  Level 20 -> 21: 19,385 coins
  Level 50 -> 51: 14,830,476 coins
```

### Zone Unlock Costs

Zones should take progressively longer to unlock. The player should feel the stretch but never feel stuck for more than 10-15 minutes of active play.

| Zone | Unlock Cost | Approx. Time to Unlock |
|---|---|---|
| Zone 1 (Grasslands) | Free | Instant |
| Zone 2 (Desert) | 10,000 | 5-8 minutes |
| Zone 3 (Arctic) | 100,000 | 15-25 minutes |
| Zone 4 (Volcano) | 1,000,000 | 45-90 minutes |
| Zone 5 (Space) | 10,000,000 | 3-6 hours |

Each zone multiplies resource yield by 5x so progress rate increases with the player.

### Rebirth Multiplier Formula

```
Multiplier = 1 + 0.1 * rebirths

Examples:
  0 rebirths: 1.0x (no bonus)
  1 rebirth:  1.1x
  5 rebirths: 1.5x
  10 rebirths: 2.0x
  25 rebirths: 3.5x
  50 rebirths: 6.0x

Rebirth Requirement:
  requirement(n) = 10,000 * 2.5^n

  Rebirth 1: 10,000 total coins earned
  Rebirth 2: 25,000
  Rebirth 5: 976,563
  Rebirth 10: 95,367,432
```

### Pet Rarity Drop Rates

Base rates (before luck modifiers):

| Rarity | Weight | Effective % |
|---|---|---|
| Common | 60 | 60% |
| Uncommon | 25 | 25% |
| Rare | 10 | 10% |
| Epic | 4 | 4% |
| Legendary | 1 | 1% |

**Luck modifier:** Each Luck upgrade level adds 5% to non-Common weights. The Lucky Egg GamePass doubles non-Common weights. After modifiers, weights are re-normalized.

```
Example with Luck level 5 + Lucky Egg:
  Common:    60       (unchanged)
  Uncommon:  25 * 1.25 * 2 = 62.5
  Rare:      10 * 1.25 * 2 = 25
  Epic:       4 * 1.25 * 2 = 10
  Legendary:  1 * 1.25 * 2 = 2.5

  After normalization (total = 160):
  Common:    37.5%
  Uncommon:  39.1%
  Rare:      15.6%
  Epic:       6.3%
  Legendary:  1.6%
```

### Pet Leveling XP Curve

```
XP required for level N:
  xp(level) = baseXP * level ^ 1.5

  Level 1 -> 2:   50 XP
  Level 5 -> 6:   559 XP
  Level 10 -> 11: 1,581 XP
  Level 20 -> 21: 4,472 XP
  Level 25 (max): cap
```

---

## 5. Monetization Strategy

Simulators monetize through a mix of permanent GamePasses and consumable Developer Products. The goal is to make free players feel progression while giving paying players a satisfying speed boost.

### GamePasses (One-Time Purchases)

| GamePass | Robux | What It Does |
|---|---|---|
| **2x Coins** | 249 | Doubles all coin collection permanently |
| **Lucky Egg** | 199 | 2x luck for rare pet hatches |
| **Auto Collect** | 499 | Automatically collects nearby resources every few seconds |
| **VIP Zone** | 399 | Access to an exclusive zone with unique pets and 10x resources |
| **Extra Pet Slots** | 149 | +3 equipped pet slots (from 3 to 6) |
| **Triple Hatch** | 299 | Hatch 3 pets per egg instead of 1 |

### Developer Products (Repeatable Purchases)

| Product | Robux | What It Does |
|---|---|---|
| **1,000 Coins** | 49 | Instant currency |
| **10,000 Coins** | 199 | Best value currency pack |
| **100,000 Coins** | 799 | Whale currency pack |
| **Auto-Hatch (10 min)** | 25 | Temporarily auto-hatches eggs |
| **Instant Rebirth** | 99 | Skips rebirth requirement once |

### Placement Strategy

- **First 2 minutes:** No purchase prompts. Let the player experience the core loop.
- **After Zone 1 egg hatch:** Show Lucky Egg GamePass upsell (contextual, the player just hatched their first pet).
- **At Zone 2 gate:** "Unlock faster with 2x Coins!" soft prompt if the player lingers.
- **After first rebirth:** Auto Collect GamePass prompt (the player now understands the grind).
- **Shop GUI:** Always available via HUD button. Never force open.

### Ethical Guidelines

- Display exact pet rarity percentages on every egg.
- Free players can reach all non-VIP zones.
- No pay-to-win: GamePasses speed up progression, not gate it.
- Respect declined prompts: 60-second cooldown before re-prompting.

---

## 6. Performance Considerations

### Pet Rendering (Many Pets On Screen)

In a populated server, dozens of players may each have 3-6 pets equipped. Rendering full 3D pet models for every player kills frame rate on mobile.

**Solution: LOD (Level of Detail) pet rendering**

```luau
-- Client-side pet display with distance-based LOD
local function updatePetDisplay(petModel: Model, distanceToCamera: number)
    if distanceToCamera < 50 then
        -- Full model: mesh, animations, particles
        petModel:SetAttribute("LOD", "Full")
        for _, part in petModel:GetDescendants() do
            if part:IsA("BasePart") then
                part.Transparency = 0
            end
        end
    elseif distanceToCamera < 150 then
        -- Billboard only: replace 3D model with a flat image
        petModel:SetAttribute("LOD", "Billboard")
        for _, part in petModel:GetDescendants() do
            if part:IsA("BasePart") and part.Name ~= "Root" then
                part.Transparency = 1
            end
        end
        -- Show BillboardGui with pet icon instead
    else
        -- Hidden: too far to matter
        petModel:SetAttribute("LOD", "Hidden")
        for _, part in petModel:GetDescendants() do
            if part:IsA("BasePart") then
                part.Transparency = 1
            end
        end
    end
end
```

**Rules of thumb:**
- Only render full pet models for the local player's pets and nearby players (within 50 studs).
- Use `BillboardGui` with a 2D icon for pets 50-150 studs away.
- Hide pets beyond 150 studs entirely.
- Limit particle effects to 1 emitter per pet maximum on mobile.

### Zone Streaming

Enable `StreamingEnabled` in Workspace properties. This is critical for simulators with large zone maps.

```
Workspace.StreamingEnabled = true
Workspace.StreamingMinRadius = 128    -- minimum loaded area
Workspace.StreamingTargetRadius = 256 -- ideal loaded area
Workspace.StreamingPauseMode = Default
```

**Zone design rules:**
- Each zone should be a separate `Model` or `Folder` in Workspace. Roblox streams them in and out based on player proximity.
- Place zone gates at the boundary so streaming has time to load the next zone before the player arrives.
- Do not use `StreamingEnabled = false` just because things "pop in." Instead, add loading zones or transition tunnels between areas.

### Particle Effect Budget

| Device Tier | Max Particles Per Zone | Max Emitters Visible |
|---|---|---|
| Mobile / Low-end | 200 | 5 |
| Console / Mid-range | 500 | 15 |
| Desktop / High-end | 1000 | 30 |

Detect device tier with a simple heuristic:

```luau
local function getDeviceTier(): string
    local platform = UserInputService.TouchEnabled
    if platform then
        return "Low"
    end

    local quality = settings().Rendering.QualityLevel
    if quality == Enum.QualityLevel.Automatic then
        return "Mid"
    elseif quality.Value <= 4 then
        return "Low"
    elseif quality.Value <= 7 then
        return "Mid"
    else
        return "High"
    end
end
```

### General Performance Rules for Simulators

- Keep total part count under 10,000 in any loaded area. Use MeshParts over Unions.
- Resource nodes should be simple single-part objects with a `ClickDetector` or Attribute tag, not complex models.
- Debounce collection requests (0.2s server-side cooldown). Do not let rapid-fire clicks flood the server.
- Clean up player data from memory tables on `PlayerRemoving` to prevent memory leaks.
- Use `Workspace.SignalBehavior = Enum.SignalBehavior.Deferred` for better performance with many connections.

---

## 7. Launch Checklist

Simulator-specific items to verify before publishing. Check these in addition to the general launch checklist from `workflows/publish-checklist.md`.

### First 10 Minutes

- [ ] Player collects their first resource within 5 seconds of spawning.
- [ ] First upgrade is purchasable within 30 seconds of play.
- [ ] First egg hatch happens within 2 minutes.
- [ ] Zone 2 gate is visible from spawn (creates aspirational goal).
- [ ] Currency counter and upgrade shop are immediately obvious in the HUD.
- [ ] A tooltip or tutorial guides the player to click their first resource node.

### Rebirth Flow

- [ ] Rebirth button appears only when the requirement is met (not before).
- [ ] Confirmation dialog warns the player what resets and what persists.
- [ ] After rebirth, the player feels noticeably faster (multiplier is tangible).
- [ ] Rebirth counter is visible on the HUD and leaderboard.
- [ ] Pets survive rebirth. Zone unlocks reset. Upgrades reset. Coins reset.

### Pet System

- [ ] Rarity percentages are displayed on every egg tooltip.
- [ ] Legendary drop at 1% means roughly 1 in 100 hatches. Test with 1,000 hatches and verify distribution.
- [ ] Pet equip/unequip is responsive (under 200ms round trip).
- [ ] Pet storage full state is handled gracefully with a clear message.
- [ ] Duplicate pets are allowed (players collect many of the same pet).

### Zone Progression

- [ ] Zone unlock costs are achievable without purchase. Test on a fresh account with no GamePasses.
- [ ] Each zone visually distinct (different biome, colors, skybox, music).
- [ ] Zone gate prevents entry without unlock (server validates, not just client).
- [ ] Resource nodes in later zones give proportionally more currency.

### Monetization

- [ ] All GamePasses grant correctly on purchase (test mid-session purchase).
- [ ] All DevProducts process correctly with idempotency (test double-receipt scenario).
- [ ] 2x Coins stacks multiplicatively with other multipliers.
- [ ] No purchase prompts in the first 2 minutes of play.
- [ ] Shop displays accurate prices and descriptions.

### Data Persistence

- [ ] Player data saves on leave, at intervals, and on server shutdown.
- [ ] Data loads correctly on rejoin (coins, pets, upgrades, zone unlocks, rebirths all preserved).
- [ ] Session locking prevents data duplication across servers (use ProfileService/ProfileStore).
- [ ] Data migration strategy exists for future schema changes.

### Performance

- [ ] Mobile frame rate stays above 30 FPS with 20 players in the same zone.
- [ ] Pet LOD system activates correctly at distance thresholds.
- [ ] StreamingEnabled is on. Zones load/unload without visible pop-in during normal play.
- [ ] Memory usage stays stable over 30+ minutes of play (no leaks from pet spawning/despawning).
