# Tycoon Genre Template

---

## 1. Genre Overview

**Load this template when:** Building a tycoon-style game where players earn currency, purchase buildings/machines, and expand a personal base.

### Core Loop

```
Earn --> Purchase --> Build --> Automate --> Expand --> (Prestige)
```

1. **Earn** -- Currency flows in from droppers (active) and buildings (passive).
2. **Purchase** -- Player steps on button pads to buy new structures.
3. **Build** -- Purchased models spawn onto the player's plot in predefined positions.
4. **Automate** -- Upgraded droppers and auto-collectors reduce manual effort.
5. **Expand** -- Higher tiers unlock new plot sections, machines, and income sources.
6. **Prestige (optional)** -- Reset progress for a permanent multiplier, extending replayability.

### Reference Games

| Game | Notable Mechanic |
|---|---|
| Retail Tycoon 2 | Customer AI, supply chain, store layout freedom |
| Restaurant Tycoon 2 | Staff management, recipe unlocks, decoration rating |
| Theme Park Tycoon 2 | Ride placement, guest happiness, park rating |
| Lumber Tycoon 2 | Resource harvesting, open-world building |
| My Restaurant | Conveyor-style food delivery, tiered upgrades |

### What Makes Tycoons Work

- **Visible progress.** Players see their base grow physically. Each purchase adds geometry to the world.
- **Low skill floor.** Walk onto a pad, spend currency, watch something appear. Accessible to all ages.
- **Satisfying feedback loops.** Dropper parts clinking into collectors, cash registers ringing, buildings popping into existence.
- **Session flexibility.** Players can leave and return; passive income accumulates (if implemented).
- **Social comparison.** Adjacent plots let players see each other's progress, driving aspiration.

---

## 2. Architecture Blueprint

### Module Overview

```
ServerScriptService/
  TycoonServer.server.lua          -- Bootstrapper: requires and inits all modules
  Services/
    TycoonManager.lua              -- Orchestrates tycoon lifecycle (create, assign, reset)
    PlotSystem.lua                 -- Plot claiming, boundaries, ownership tracking
    DropperSystem.lua              -- Spawns dropper parts on intervals, manages conveyors
    ButtonPadManager.lua           -- TouchPart purchase pads, cost checks, model spawning
    UpgradeTree.lua                -- Tiered unlock dependencies and progression
    IncomeManager.lua              -- Passive + active income calculation and distribution
    PrestigeSystem.lua             -- Optional prestige/rebirth logic

ServerStorage/
  TycoonAssets/
    Plots/
      Plot1.Model                  -- Complete plot template with all pad positions
    Buildings/
      Tier1/
        BasicDropper.Model
        SmallCollector.Model
        Conveyor.Model
      Tier2/
        AdvancedDropper.Model
        LargeCollector.Model
      Tier3/
        MegaDropper.Model
        AutoCollector.Model

ReplicatedStorage/
  Remotes/
    TycoonRemotes/                 -- Folder for all tycoon-related remotes
      CurrencyUpdate (RemoteEvent)
      BuildingPurchased (RemoteEvent)
      PrestigeRequest (RemoteEvent)
  Modules/
    TycoonConfig.lua               -- Shared config: building costs, income rates, tier data
    TycoonTypes.lua                -- Type definitions shared between client and server

StarterGui/
  TycoonHUD (ScreenGui)
    CurrencyDisplay.Frame
    UpgradePanel.Frame
    PrestigeButton.Frame

StarterPlayer/
  StarterPlayerScripts/
    TycoonClient.client.lua        -- Client bootstrapper
    Controllers/
      TycoonUIController.lua       -- Updates HUD, listens for currency changes
      DropperEffects.lua           -- Client-side VFX for dropper parts (optional)
```

### Data Flow

```
[Dropper] --spawns Part--> [Conveyor] --moves Part--> [Collector] --fires event-->
[IncomeManager] --adds currency--> [Player Data] --fires remote--> [Client HUD]
```

### Key Architectural Decisions

| Decision | Rationale |
|---|---|
| All currency math is server-side | Prevents exploiters from giving themselves money (SE-2) |
| Building models stored in ServerStorage | Clients cannot inspect unreleased buildings or manipulate templates |
| Button pads use server-side Touched | Client Touched events are not authoritative; server validates proximity |
| Dropper parts are server-owned | Physics authority stays on server to prevent teleporting parts |
| Config is in ReplicatedStorage | Client needs costs/names for UI display; server validates against same source |

---

## 3. Core Systems

### 3.1 Shared Configuration

Place in `ReplicatedStorage/Modules/TycoonConfig.lua`:

```luau
-- ReplicatedStorage/Modules/TycoonConfig.lua
local TycoonConfig = {}

-- Building definitions: id -> data
-- Cost scaling: each tier roughly 3-5x the previous
TycoonConfig.Buildings = {
    -- Tier 1 (Starter)
    BasicDropper = {
        displayName = "Basic Dropper",
        tier = 1,
        cost = 100,
        incomePerDrop = 5,
        dropInterval = 2.0,
        modelName = "BasicDropper",
        prerequisite = nil, -- no prerequisite
        order = 1,
    },
    Conveyor = {
        displayName = "Conveyor Belt",
        tier = 1,
        cost = 200,
        incomePerDrop = 0, -- conveyors don't generate income directly
        dropInterval = 0,
        modelName = "Conveyor",
        prerequisite = "BasicDropper",
        order = 2,
    },
    SmallCollector = {
        displayName = "Small Collector",
        tier = 1,
        cost = 350,
        incomePerDrop = 0, -- collector converts parts to currency
        dropInterval = 0,
        modelName = "SmallCollector",
        prerequisite = "Conveyor",
        order = 3,
    },

    -- Tier 2 (Mid-game)
    AdvancedDropper = {
        displayName = "Advanced Dropper",
        tier = 2,
        cost = 2_500,
        incomePerDrop = 25,
        dropInterval = 1.5,
        modelName = "AdvancedDropper",
        prerequisite = "SmallCollector",
        order = 4,
    },
    LargeCollector = {
        displayName = "Large Collector",
        tier = 2,
        cost = 5_000,
        incomePerDrop = 0,
        dropInterval = 0,
        modelName = "LargeCollector",
        prerequisite = "AdvancedDropper",
        order = 5,
    },
    PassiveIncomeBuilding = {
        displayName = "Cash Register",
        tier = 2,
        cost = 10_000,
        incomePerDrop = 0,
        dropInterval = 0,
        passiveIncome = 50, -- per interval
        passiveInterval = 10,
        modelName = "CashRegister",
        prerequisite = "LargeCollector",
        order = 6,
    },

    -- Tier 3 (Late-game)
    MegaDropper = {
        displayName = "Mega Dropper",
        tier = 3,
        cost = 50_000,
        incomePerDrop = 150,
        dropInterval = 1.0,
        modelName = "MegaDropper",
        prerequisite = "PassiveIncomeBuilding",
        order = 7,
    },
    AutoCollector = {
        displayName = "Auto Collector",
        tier = 3,
        cost = 100_000,
        incomePerDrop = 0,
        dropInterval = 0,
        modelName = "AutoCollector",
        prerequisite = "MegaDropper",
        order = 8,
    },
}

-- Prestige configuration
TycoonConfig.Prestige = {
    enabled = true,
    minimumEarnings = 500_000, -- must earn this much before prestige is available
    multiplierPerPrestige = 0.25, -- +25% income per prestige level
    maxPrestigeLevel = 20,
}

-- Dropper part settings
TycoonConfig.Dropper = {
    partSize = Vector3.new(1, 1, 1),
    partColor = Color3.fromRGB(255, 215, 0), -- gold
    maxPartsPerPlot = 50, -- performance cap
    partLifetime = 15, -- seconds before auto-destroy if uncollected
}

-- Plot settings
TycoonConfig.Plot = {
    maxPlots = 8, -- max concurrent tycoons
    plotSpacing = 100, -- studs between plot centers
}

return TycoonConfig
```

### 3.2 Plot Assignment System

Place in `ServerScriptService/Services/PlotSystem.lua`:

```luau
-- ServerScriptService/Services/PlotSystem.lua
--
-- Manages tycoon plot claiming. Each player gets exactly one plot.
-- Plots are pre-built Model instances in Workspace with a "ClaimPad" TouchPart
-- or auto-assigned on join.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local TycoonConfig = require(ReplicatedStorage.Modules.TycoonConfig)

local PlotSystem = {}

-- State
local plots: { [number]: { -- plotIndex -> plot data
    model: Model,
    owner: Player?,
    ownerId: number?,
    spawnCFrame: CFrame,
    buildingAnchors: { [string]: CFrame }, -- buildingId -> world CFrame for placement
} } = {}

local playerPlots: { [Player]: number } = {} -- player -> plotIndex

--------------------------------------------------------------------------------
-- INITIALIZATION
--------------------------------------------------------------------------------

function PlotSystem.init()
    local plotsFolder = workspace:FindFirstChild("Plots")
    if not plotsFolder then
        plotsFolder = Instance.new("Folder")
        plotsFolder.Name = "Plots"
        plotsFolder.Parent = workspace
    end

    -- Find or create plot slots
    -- Expects Workspace.Plots to contain Model instances named "Plot1", "Plot2", etc.
    -- Each plot model should have:
    --   - A PrimaryPart (used as the base reference point)
    --   - A "ClaimPad" Part (optional, for walk-on claiming)
    --   - "ButtonPads" Folder containing TouchPart pads for each building
    --   - "Buildings" Folder (initially empty, buildings spawn here)

    for i = 1, TycoonConfig.Plot.maxPlots do
        local plotModel = plotsFolder:FindFirstChild("Plot" .. i)
        if plotModel and plotModel:IsA("Model") then
            local primaryPart = plotModel.PrimaryPart
            if not primaryPart then
                warn("[PlotSystem] Plot" .. i .. " has no PrimaryPart, skipping")
                continue
            end

            -- Index building anchor positions from ButtonPads
            local anchors: { [string]: CFrame } = {}
            local buttonPadsFolder = plotModel:FindFirstChild("ButtonPads")
            if buttonPadsFolder then
                for _, pad in buttonPadsFolder:GetChildren() do
                    if pad:IsA("BasePart") then
                        -- Pad name matches building ID (e.g., "BasicDropper")
                        -- The building spawns at the pad's position
                        anchors[pad.Name] = pad.CFrame
                    end
                end
            end

            plots[i] = {
                model = plotModel,
                owner = nil,
                ownerId = nil,
                spawnCFrame = primaryPart.CFrame + Vector3.new(0, 5, 0),
                buildingAnchors = anchors,
            }

            -- Wire up optional ClaimPad touch detection
            local claimPad = plotModel:FindFirstChild("ClaimPad")
            if claimPad and claimPad:IsA("BasePart") then
                claimPad.Touched:Connect(function(hit)
                    local character = hit.Parent
                    if not character then return end
                    local humanoid = character:FindFirstChildOfClass("Humanoid")
                    if not humanoid then return end
                    local player = Players:GetPlayerFromCharacter(character)
                    if not player then return end

                    PlotSystem.claimPlot(player, i)
                end)
            end
        end
    end
end

--------------------------------------------------------------------------------
-- PLOT CLAIMING
--------------------------------------------------------------------------------

function PlotSystem.claimPlot(player: Player, plotIndex: number): boolean
    -- Already owns a plot
    if playerPlots[player] then
        return false
    end

    local plot = plots[plotIndex]
    if not plot then
        return false
    end

    -- Plot already claimed
    if plot.owner then
        return false
    end

    -- Claim it
    plot.owner = player
    plot.ownerId = player.UserId
    playerPlots[player] = plotIndex

    -- Visual feedback: change claim pad color or hide it
    local claimPad = plot.model:FindFirstChild("ClaimPad")
    if claimPad then
        claimPad.Transparency = 1
        claimPad.CanCollide = false
    end

    -- Set ownership label
    local billboardGui = plot.model:FindFirstChild("OwnerLabel")
    if billboardGui and billboardGui:IsA("BillboardGui") then
        local label = billboardGui:FindFirstChildOfClass("TextLabel")
        if label then
            label.Text = player.DisplayName .. "'s Tycoon"
        end
    end

    -- Teleport player to their plot spawn
    local character = player.Character
    if character and character.PrimaryPart then
        character:PivotTo(plot.spawnCFrame)
    end

    print("[PlotSystem] " .. player.Name .. " claimed Plot" .. plotIndex)
    return true
end

--------------------------------------------------------------------------------
-- AUTO-ASSIGN (call on PlayerAdded if not using walk-on claiming)
--------------------------------------------------------------------------------

function PlotSystem.autoAssign(player: Player): boolean
    if playerPlots[player] then
        return true -- already has a plot
    end

    for index, plot in plots do
        if not plot.owner then
            return PlotSystem.claimPlot(player, index)
        end
    end

    warn("[PlotSystem] No available plots for " .. player.Name)
    return false
end

--------------------------------------------------------------------------------
-- QUERIES
--------------------------------------------------------------------------------

function PlotSystem.getPlayerPlotIndex(player: Player): number?
    return playerPlots[player]
end

function PlotSystem.getPlotData(plotIndex: number)
    return plots[plotIndex]
end

function PlotSystem.getPlotModel(player: Player): Model?
    local index = playerPlots[player]
    if not index then return nil end
    local plot = plots[index]
    return plot and plot.model or nil
end

function PlotSystem.getBuildingAnchor(player: Player, buildingId: string): CFrame?
    local index = playerPlots[player]
    if not index then return nil end
    local plot = plots[index]
    if not plot then return nil end
    return plot.buildingAnchors[buildingId]
end

--------------------------------------------------------------------------------
-- RELEASE (on player leave or prestige)
--------------------------------------------------------------------------------

function PlotSystem.releasePlot(player: Player)
    local index = playerPlots[player]
    if not index then return end

    local plot = plots[index]
    if not plot then return end

    -- Clear spawned buildings
    local buildingsFolder = plot.model:FindFirstChild("Buildings")
    if buildingsFolder then
        for _, child in buildingsFolder:GetChildren() do
            child:Destroy()
        end
    end

    -- Reset claim pad
    local claimPad = plot.model:FindFirstChild("ClaimPad")
    if claimPad then
        claimPad.Transparency = 0
        claimPad.CanCollide = true
    end

    -- Reset label
    local billboardGui = plot.model:FindFirstChild("OwnerLabel")
    if billboardGui and billboardGui:IsA("BillboardGui") then
        local label = billboardGui:FindFirstChildOfClass("TextLabel")
        if label then
            label.Text = "Unclaimed"
        end
    end

    -- Clear state
    plot.owner = nil
    plot.ownerId = nil
    playerPlots[player] = nil

    print("[PlotSystem] Released Plot" .. index .. " from " .. player.Name)
end

--------------------------------------------------------------------------------
-- CLEANUP
--------------------------------------------------------------------------------

function PlotSystem.onPlayerRemoving(player: Player)
    PlotSystem.releasePlot(player)
end

return PlotSystem
```

### 3.3 Button Pad Purchase System

Place in `ServerScriptService/Services/ButtonPadManager.lua`:

```luau
-- ServerScriptService/Services/ButtonPadManager.lua
--
-- Manages TouchPart button pads on each tycoon plot.
-- When a player steps on a pad:
--   1. Verify they own the plot
--   2. Check prerequisites (upgrade tree)
--   3. Deduct currency
--   4. Spawn the building model at the pad location
--   5. Disable the pad
--   6. Enable the next pad(s) in the unlock chain

local Players = game:GetService("Players")
local ServerStorage = game:GetService("ServerStorage")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local TycoonConfig = require(ReplicatedStorage.Modules.TycoonConfig)

-- These modules are injected via init() to avoid circular requires
local PlotSystem
local IncomeManager
local DropperSystem

local ButtonPadManager = {}

-- Track which buildings each player has purchased
local playerBuildings: { [Player]: { [string]: boolean } } = {}

-- Debounce per player to prevent double-purchases
local purchaseDebounce: { [Player]: boolean } = {}

--------------------------------------------------------------------------------
-- INITIALIZATION
--------------------------------------------------------------------------------

function ButtonPadManager.init(modules: {
    PlotSystem: any,
    IncomeManager: any,
    DropperSystem: any,
})
    PlotSystem = modules.PlotSystem
    IncomeManager = modules.IncomeManager
    DropperSystem = modules.DropperSystem
end

--------------------------------------------------------------------------------
-- SETUP PADS FOR A PLAYER'S PLOT
--------------------------------------------------------------------------------

function ButtonPadManager.setupPads(player: Player)
    local plotModel = PlotSystem.getPlotModel(player)
    if not plotModel then
        warn("[ButtonPadManager] No plot found for " .. player.Name)
        return
    end

    playerBuildings[player] = {}

    local buttonPadsFolder = plotModel:FindFirstChild("ButtonPads")
    if not buttonPadsFolder then
        warn("[ButtonPadManager] No ButtonPads folder in plot for " .. player.Name)
        return
    end

    -- Set up each pad
    for _, pad in buttonPadsFolder:GetChildren() do
        if not pad:IsA("BasePart") then continue end

        local buildingId = pad.Name
        local buildingData = TycoonConfig.Buildings[buildingId]
        if not buildingData then
            warn("[ButtonPadManager] No config for building: " .. buildingId)
            continue
        end

        -- Create cost label on the pad
        ButtonPadManager._createPadLabel(pad, buildingData)

        -- Initially hide pads that have prerequisites not yet met
        if buildingData.prerequisite then
            pad.Transparency = 1
            pad.CanCollide = false
            -- Hide the BillboardGui too
            local gui = pad:FindFirstChildOfClass("BillboardGui")
            if gui then gui.Enabled = false end
        end

        -- Connect touch event (server-side)
        pad.Touched:Connect(function(hit)
            ButtonPadManager._onPadTouched(player, pad, buildingId, hit)
        end)
    end

    -- Show the first pad(s) that have no prerequisites
    ButtonPadManager._refreshPadVisibility(player)
end

--------------------------------------------------------------------------------
-- PAD TOUCH HANDLER
--------------------------------------------------------------------------------

function ButtonPadManager._onPadTouched(
    plotOwner: Player,
    pad: BasePart,
    buildingId: string,
    hit: BasePart
)
    -- Debounce check
    if purchaseDebounce[plotOwner] then return end

    -- Identify who touched the pad
    local character = hit.Parent
    if not character then return end
    local humanoid = character:FindFirstChildOfClass("Humanoid")
    if not humanoid or humanoid.Health <= 0 then return end
    local touchPlayer = Players:GetPlayerFromCharacter(character)
    if not touchPlayer then return end

    -- Only the plot owner can purchase on their plot
    if touchPlayer ~= plotOwner then return end

    -- Already purchased this building
    if playerBuildings[plotOwner] and playerBuildings[plotOwner][buildingId] then
        return
    end

    local buildingData = TycoonConfig.Buildings[buildingId]
    if not buildingData then return end

    -- Check prerequisite
    if buildingData.prerequisite then
        if not playerBuildings[plotOwner][buildingData.prerequisite] then
            return -- prerequisite not met
        end
    end

    -- Check currency
    local playerCurrency = IncomeManager.getCurrency(plotOwner)
    if playerCurrency < buildingData.cost then
        return -- cannot afford
    end

    -- Set debounce
    purchaseDebounce[plotOwner] = true

    -- Deduct currency
    IncomeManager.addCurrency(plotOwner, -buildingData.cost)

    -- Mark as purchased
    playerBuildings[plotOwner][buildingId] = true

    -- Spawn the building model
    ButtonPadManager._spawnBuilding(plotOwner, buildingId, buildingData, pad)

    -- Disable the pad
    pad.Transparency = 1
    pad.CanCollide = false
    local gui = pad:FindFirstChildOfClass("BillboardGui")
    if gui then gui.Enabled = false end

    -- If this building is a dropper, register it with DropperSystem
    if buildingData.incomePerDrop > 0 and buildingData.dropInterval > 0 then
        DropperSystem.registerDropper(plotOwner, buildingId, buildingData)
    end

    -- If this building has passive income, register it with IncomeManager
    if buildingData.passiveIncome and buildingData.passiveIncome > 0 then
        IncomeManager.registerPassiveSource(plotOwner, buildingId, buildingData)
    end

    -- Reveal any pads whose prerequisite is this building
    ButtonPadManager._refreshPadVisibility(plotOwner)

    -- Notify client
    local currencyRemote = ReplicatedStorage:FindFirstChild("Remotes")
        and ReplicatedStorage.Remotes:FindFirstChild("TycoonRemotes")
        and ReplicatedStorage.Remotes.TycoonRemotes:FindFirstChild("BuildingPurchased")
    if currencyRemote then
        currencyRemote:FireClient(plotOwner, buildingId, buildingData.displayName)
    end

    print("[ButtonPadManager] " .. plotOwner.Name .. " purchased " .. buildingData.displayName
        .. " for $" .. buildingData.cost)

    -- Release debounce after a short delay
    task.delay(0.5, function()
        purchaseDebounce[plotOwner] = nil
    end)
end

--------------------------------------------------------------------------------
-- SPAWN BUILDING MODEL
--------------------------------------------------------------------------------

function ButtonPadManager._spawnBuilding(
    player: Player,
    buildingId: string,
    buildingData: any,
    pad: BasePart
)
    -- Find the template model in ServerStorage
    local tierFolder = ServerStorage:FindFirstChild("TycoonAssets")
        and ServerStorage.TycoonAssets:FindFirstChild("Buildings")
        and ServerStorage.TycoonAssets.Buildings:FindFirstChild("Tier" .. buildingData.tier)

    if not tierFolder then
        warn("[ButtonPadManager] Missing tier folder: Tier" .. buildingData.tier)
        return
    end

    local template = tierFolder:FindFirstChild(buildingData.modelName)
    if not template then
        warn("[ButtonPadManager] Missing model: " .. buildingData.modelName)
        return
    end

    local plotModel = PlotSystem.getPlotModel(player)
    if not plotModel then return end

    local buildingsFolder = plotModel:FindFirstChild("Buildings")
    if not buildingsFolder then
        buildingsFolder = Instance.new("Folder")
        buildingsFolder.Name = "Buildings"
        buildingsFolder.Parent = plotModel
    end

    -- Clone and position the building
    local building = template:Clone()
    building.Name = buildingId

    -- Use the anchor CFrame from the plot, falling back to pad position
    local anchorCFrame = PlotSystem.getBuildingAnchor(player, buildingId) or pad.CFrame
    if building:IsA("Model") and building.PrimaryPart then
        building:PivotTo(anchorCFrame)
    elseif building:IsA("BasePart") then
        building.CFrame = anchorCFrame
    end

    building.Parent = buildingsFolder
end

--------------------------------------------------------------------------------
-- PAD VISIBILITY (show pads whose prerequisites are met)
--------------------------------------------------------------------------------

function ButtonPadManager._refreshPadVisibility(player: Player)
    local plotModel = PlotSystem.getPlotModel(player)
    if not plotModel then return end

    local buttonPadsFolder = plotModel:FindFirstChild("ButtonPads")
    if not buttonPadsFolder then return end

    local owned = playerBuildings[player] or {}

    for _, pad in buttonPadsFolder:GetChildren() do
        if not pad:IsA("BasePart") then continue end

        local buildingId = pad.Name
        local buildingData = TycoonConfig.Buildings[buildingId]
        if not buildingData then continue end

        -- Skip already purchased
        if owned[buildingId] then continue end

        -- Show pad if prerequisite is met (or has no prerequisite)
        local prereqMet = (buildingData.prerequisite == nil)
            or (owned[buildingData.prerequisite] == true)

        if prereqMet then
            pad.Transparency = 0
            pad.CanCollide = true
            local gui = pad:FindFirstChildOfClass("BillboardGui")
            if gui then gui.Enabled = true end
        end
    end
end

--------------------------------------------------------------------------------
-- PAD LABEL (BillboardGui showing cost)
--------------------------------------------------------------------------------

function ButtonPadManager._createPadLabel(pad: BasePart, buildingData: any)
    -- Skip if a label already exists (pre-placed in Studio)
    if pad:FindFirstChildOfClass("BillboardGui") then return end

    local billboard = Instance.new("BillboardGui")
    billboard.Name = "PadLabel"
    billboard.Size = UDim2.new(0, 200, 0, 80)
    billboard.StudsOffset = Vector3.new(0, 3, 0)
    billboard.AlwaysOnTop = true
    billboard.Parent = pad

    local nameLabel = Instance.new("TextLabel")
    nameLabel.Name = "NameLabel"
    nameLabel.Size = UDim2.new(1, 0, 0.5, 0)
    nameLabel.BackgroundTransparency = 1
    nameLabel.Text = buildingData.displayName
    nameLabel.TextColor3 = Color3.new(1, 1, 1)
    nameLabel.TextScaled = true
    nameLabel.Font = Enum.Font.GothamBold
    nameLabel.Parent = billboard

    local costLabel = Instance.new("TextLabel")
    costLabel.Name = "CostLabel"
    costLabel.Size = UDim2.new(1, 0, 0.5, 0)
    costLabel.Position = UDim2.new(0, 0, 0.5, 0)
    costLabel.BackgroundTransparency = 1
    costLabel.Text = "$" .. tostring(buildingData.cost)
    costLabel.TextColor3 = Color3.fromRGB(85, 255, 85)
    costLabel.TextScaled = true
    costLabel.Font = Enum.Font.GothamBold
    costLabel.Parent = billboard
end

--------------------------------------------------------------------------------
-- QUERIES
--------------------------------------------------------------------------------

function ButtonPadManager.hasBuilding(player: Player, buildingId: string): boolean
    local owned = playerBuildings[player]
    return owned ~= nil and owned[buildingId] == true
end

function ButtonPadManager.getOwnedBuildings(player: Player): { [string]: boolean }
    return playerBuildings[player] or {}
end

--------------------------------------------------------------------------------
-- CLEANUP
--------------------------------------------------------------------------------

function ButtonPadManager.onPlayerRemoving(player: Player)
    playerBuildings[player] = nil
    purchaseDebounce[player] = nil
end

return ButtonPadManager
```

### 3.4 Dropper / Collector System

Place in `ServerScriptService/Services/DropperSystem.lua`:

```luau
-- ServerScriptService/Services/DropperSystem.lua
--
-- Manages dropper parts: spawning at intervals, conveyor movement,
-- and collector detection. When a dropper part reaches a collector,
-- it is destroyed and currency is awarded.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Debris = game:GetService("Debris")

local TycoonConfig = require(ReplicatedStorage.Modules.TycoonConfig)

local PlotSystem -- injected via init()
local IncomeManager -- injected via init()

local DropperSystem = {}

-- Active droppers per player
local playerDroppers: { [Player]: {
    [string]: { -- buildingId
        thread: thread?,
        active: boolean,
        buildingData: any,
    }
} } = {}

-- Part count per player (for performance cap)
local playerPartCount: { [Player]: number } = {}

--------------------------------------------------------------------------------
-- INITIALIZATION
--------------------------------------------------------------------------------

function DropperSystem.init(modules: { PlotSystem: any, IncomeManager: any })
    PlotSystem = modules.PlotSystem
    IncomeManager = modules.IncomeManager
end

--------------------------------------------------------------------------------
-- REGISTER A NEW DROPPER
--------------------------------------------------------------------------------

function DropperSystem.registerDropper(
    player: Player,
    buildingId: string,
    buildingData: any
)
    if not playerDroppers[player] then
        playerDroppers[player] = {}
        playerPartCount[player] = 0
    end

    -- Prevent duplicate registration
    if playerDroppers[player][buildingId] then return end

    local dropperInfo = {
        thread = nil,
        active = true,
        buildingData = buildingData,
    }
    playerDroppers[player][buildingId] = dropperInfo

    -- Start the dropper loop
    dropperInfo.thread = task.spawn(function()
        DropperSystem._dropperLoop(player, buildingId, dropperInfo)
    end)
end

--------------------------------------------------------------------------------
-- DROPPER LOOP
--------------------------------------------------------------------------------

function DropperSystem._dropperLoop(
    player: Player,
    buildingId: string,
    dropperInfo: any
)
    local buildingData = dropperInfo.buildingData

    while dropperInfo.active do
        task.wait(buildingData.dropInterval)

        if not dropperInfo.active then break end
        if not player.Parent then break end -- player left

        -- Performance cap: don't spawn more parts if at limit
        local currentCount = playerPartCount[player] or 0
        if currentCount >= TycoonConfig.Dropper.maxPartsPerPlot then
            continue
        end

        -- Find the dropper model in the player's plot to get spawn position
        local plotModel = PlotSystem.getPlotModel(player)
        if not plotModel then break end

        local buildingsFolder = plotModel:FindFirstChild("Buildings")
        if not buildingsFolder then continue end

        local dropperModel = buildingsFolder:FindFirstChild(buildingId)
        if not dropperModel then continue end

        -- Find the "DropPoint" attachment or part inside the dropper model
        local dropPoint = dropperModel:FindFirstChild("DropPoint", true)
        if not dropPoint then continue end

        local spawnPosition: Vector3
        if dropPoint:IsA("Attachment") then
            spawnPosition = dropPoint.WorldPosition
        elseif dropPoint:IsA("BasePart") then
            spawnPosition = dropPoint.Position
        else
            continue
        end

        -- Spawn the dropper part
        local part = Instance.new("Part")
        part.Name = "DropperPart"
        part.Size = TycoonConfig.Dropper.partSize
        part.Color = TycoonConfig.Dropper.partColor
        part.Material = Enum.Material.Neon
        part.Position = spawnPosition
        part.Anchored = false
        part.CanCollide = true
        part.Parent = buildingsFolder

        -- Store income value as an attribute on the part
        part:SetAttribute("IncomeValue", buildingData.incomePerDrop)
        part:SetAttribute("OwnerUserId", player.UserId)

        -- Track part count
        playerPartCount[player] = (playerPartCount[player] or 0) + 1

        -- Auto-destroy after lifetime (cleanup if it falls off or gets stuck)
        Debris:AddItem(part, TycoonConfig.Dropper.partLifetime)

        -- Decrement count when part is destroyed
        part.Destroying:Connect(function()
            local count = playerPartCount[player]
            if count then
                playerPartCount[player] = math.max(0, count - 1)
            end
        end)
    end
end

--------------------------------------------------------------------------------
-- COLLECTOR SETUP (call after a collector building is placed)
-- The collector model should contain a "CollectorZone" Part with .Touched wired.
--------------------------------------------------------------------------------

function DropperSystem.setupCollector(player: Player, buildingId: string)
    local plotModel = PlotSystem.getPlotModel(player)
    if not plotModel then return end

    local buildingsFolder = plotModel:FindFirstChild("Buildings")
    if not buildingsFolder then return end

    local collectorModel = buildingsFolder:FindFirstChild(buildingId)
    if not collectorModel then return end

    -- Find the CollectorZone part inside the collector model
    local collectorZone = collectorModel:FindFirstChild("CollectorZone", true)
    if not collectorZone or not collectorZone:IsA("BasePart") then
        warn("[DropperSystem] No CollectorZone found in " .. buildingId)
        return
    end

    collectorZone.Touched:Connect(function(hit)
        if hit.Name ~= "DropperPart" then return end

        local incomeValue = hit:GetAttribute("IncomeValue")
        local ownerUserId = hit:GetAttribute("OwnerUserId")
        if not incomeValue or not ownerUserId then return end

        -- Verify this part belongs to this player's tycoon
        if ownerUserId ~= player.UserId then return end

        -- Award currency
        IncomeManager.addCurrency(player, incomeValue)

        -- Destroy the part
        hit:Destroy()
    end)
end

--------------------------------------------------------------------------------
-- STOP ALL DROPPERS (for prestige or leave)
--------------------------------------------------------------------------------

function DropperSystem.stopAll(player: Player)
    local droppers = playerDroppers[player]
    if not droppers then return end

    for _, info in droppers do
        info.active = false
        if info.thread then
            task.cancel(info.thread)
            info.thread = nil
        end
    end
end

--------------------------------------------------------------------------------
-- CLEANUP
--------------------------------------------------------------------------------

function DropperSystem.onPlayerRemoving(player: Player)
    DropperSystem.stopAll(player)
    playerDroppers[player] = nil
    playerPartCount[player] = nil
end

return DropperSystem
```

### 3.5 Income Manager

Place in `ServerScriptService/Services/IncomeManager.lua`:

```luau
-- ServerScriptService/Services/IncomeManager.lua
--
-- Tracks player currency, handles passive income ticks, and
-- syncs currency updates to the client.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local IncomeManager = {}

-- Player currency state
local playerCurrency: { [Player]: number } = {}

-- Passive income sources per player
local passiveSources: { [Player]: {
    [string]: { -- buildingId
        income: number,
        interval: number,
        thread: thread?,
        active: boolean,
    }
} } = {}

-- Income multiplier (from prestige, gamepasses, etc.)
local playerMultipliers: { [Player]: number } = {}

--------------------------------------------------------------------------------
-- INITIALIZATION
--------------------------------------------------------------------------------

function IncomeManager.init()
    -- Nothing needed here; currency is set up per-player via setupPlayer
end

--------------------------------------------------------------------------------
-- PLAYER SETUP
--------------------------------------------------------------------------------

function IncomeManager.setupPlayer(player: Player, savedCurrency: number?)
    playerCurrency[player] = savedCurrency or 0
    playerMultipliers[player] = 1.0
    passiveSources[player] = {}

    -- Create leaderstats for display
    local leaderstats = Instance.new("Folder")
    leaderstats.Name = "leaderstats"
    leaderstats.Parent = player

    local cashValue = Instance.new("IntValue")
    cashValue.Name = "Cash"
    cashValue.Value = playerCurrency[player]
    cashValue.Parent = leaderstats

    -- Sync to client
    IncomeManager._syncToClient(player)
end

--------------------------------------------------------------------------------
-- CURRENCY OPERATIONS
--------------------------------------------------------------------------------

function IncomeManager.getCurrency(player: Player): number
    return playerCurrency[player] or 0
end

function IncomeManager.addCurrency(player: Player, amount: number)
    local current = playerCurrency[player] or 0
    local multiplier = playerMultipliers[player] or 1.0

    -- Apply multiplier only to positive income (not to deductions)
    local adjusted = amount
    if amount > 0 then
        adjusted = math.floor(amount * multiplier)
    end

    playerCurrency[player] = math.max(0, current + adjusted)

    -- Update leaderstats
    local leaderstats = player:FindFirstChild("leaderstats")
    if leaderstats then
        local cashValue = leaderstats:FindFirstChild("Cash")
        if cashValue then
            cashValue.Value = playerCurrency[player]
        end
    end

    -- Sync to client HUD
    IncomeManager._syncToClient(player)
end

function IncomeManager.setMultiplier(player: Player, multiplier: number)
    playerMultipliers[player] = multiplier
end

function IncomeManager.getMultiplier(player: Player): number
    return playerMultipliers[player] or 1.0
end

--------------------------------------------------------------------------------
-- PASSIVE INCOME
--------------------------------------------------------------------------------

function IncomeManager.registerPassiveSource(
    player: Player,
    buildingId: string,
    buildingData: any
)
    if not passiveSources[player] then
        passiveSources[player] = {}
    end

    if passiveSources[player][buildingId] then return end -- already registered

    local sourceInfo = {
        income = buildingData.passiveIncome,
        interval = buildingData.passiveInterval or 10,
        thread = nil,
        active = true,
    }
    passiveSources[player][buildingId] = sourceInfo

    -- Start passive income loop
    sourceInfo.thread = task.spawn(function()
        while sourceInfo.active and player.Parent do
            task.wait(sourceInfo.interval)
            if not sourceInfo.active then break end
            if not player.Parent then break end
            IncomeManager.addCurrency(player, sourceInfo.income)
        end
    end)
end

function IncomeManager.stopAllPassive(player: Player)
    local sources = passiveSources[player]
    if not sources then return end

    for _, info in sources do
        info.active = false
        if info.thread then
            task.cancel(info.thread)
            info.thread = nil
        end
    end
end

--------------------------------------------------------------------------------
-- CLIENT SYNC
--------------------------------------------------------------------------------

function IncomeManager._syncToClient(player: Player)
    local remotesFolder = ReplicatedStorage:FindFirstChild("Remotes")
    if not remotesFolder then return end
    local tycoonRemotes = remotesFolder:FindFirstChild("TycoonRemotes")
    if not tycoonRemotes then return end
    local currencyRemote = tycoonRemotes:FindFirstChild("CurrencyUpdate")
    if not currencyRemote then return end

    currencyRemote:FireClient(player, playerCurrency[player] or 0)
end

--------------------------------------------------------------------------------
-- CLEANUP
--------------------------------------------------------------------------------

function IncomeManager.onPlayerRemoving(player: Player)
    IncomeManager.stopAllPassive(player)

    -- Return current currency for saving
    local finalCurrency = playerCurrency[player] or 0

    playerCurrency[player] = nil
    playerMultipliers[player] = nil
    passiveSources[player] = nil

    return finalCurrency
end

return IncomeManager
```

### 3.6 Server Bootstrapper

Place in `ServerScriptService/TycoonServer.server.lua`:

```luau
-- ServerScriptService/TycoonServer.server.lua
--
-- Bootstrapper: requires all tycoon modules, wires them together,
-- and handles player lifecycle.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

-- Create remotes
local remotesFolder = ReplicatedStorage:FindFirstChild("Remotes")
if not remotesFolder then
    remotesFolder = Instance.new("Folder")
    remotesFolder.Name = "Remotes"
    remotesFolder.Parent = ReplicatedStorage
end

local tycoonRemotes = Instance.new("Folder")
tycoonRemotes.Name = "TycoonRemotes"
tycoonRemotes.Parent = remotesFolder

local currencyRemote = Instance.new("RemoteEvent")
currencyRemote.Name = "CurrencyUpdate"
currencyRemote.Parent = tycoonRemotes

local buildingRemote = Instance.new("RemoteEvent")
buildingRemote.Name = "BuildingPurchased"
buildingRemote.Parent = tycoonRemotes

-- Require modules
local Services = ServerScriptService:FindFirstChild("Services")
local PlotSystem = require(Services.PlotSystem)
local IncomeManager = require(Services.IncomeManager)
local DropperSystem = require(Services.DropperSystem)
local ButtonPadManager = require(Services.ButtonPadManager)

-- Init phase (no cross-module calls yet)
PlotSystem.init()
IncomeManager.init()
DropperSystem.init({ PlotSystem = PlotSystem, IncomeManager = IncomeManager })
ButtonPadManager.init({
    PlotSystem = PlotSystem,
    IncomeManager = IncomeManager,
    DropperSystem = DropperSystem,
})

-- Player lifecycle
local function onPlayerAdded(player: Player)
    -- TODO: Load saved data from DataStore here
    local savedCurrency = 0 -- replace with DataStore load
    local savedBuildings = {} -- replace with DataStore load

    -- Set up income tracking
    IncomeManager.setupPlayer(player, savedCurrency)

    -- Auto-assign a plot
    local assigned = PlotSystem.autoAssign(player)
    if not assigned then
        warn("[Tycoon] Could not assign plot to " .. player.Name)
        return
    end

    -- Set up button pads on their plot
    ButtonPadManager.setupPads(player)

    -- Restore previously purchased buildings (on rejoin)
    -- for buildingId in savedBuildings do
    --     ButtonPadManager.restoreBuilding(player, buildingId)
    -- end
end

local function onPlayerRemoving(player: Player)
    -- Get final currency for saving
    local finalCurrency = IncomeManager.onPlayerRemoving(player)

    -- TODO: Save finalCurrency and owned buildings to DataStore here

    -- Clean up all systems
    DropperSystem.onPlayerRemoving(player)
    ButtonPadManager.onPlayerRemoving(player)
    PlotSystem.onPlayerRemoving(player)
end

-- Connect
for _, player in Players:GetPlayers() do
    task.spawn(onPlayerAdded, player)
end
Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)

print("[Tycoon] Server initialized")
```

---

## 4. Progression Design

### Cost Scaling

Use **exponential scaling** to pace progression. Each tier should feel meaningfully more expensive than the last, creating a satisfying sense of investment.

| Tier | Cost Range | Income Range (per drop/tick) | Time to Earn (approx) |
|---|---|---|---|
| Tier 1 (Starter) | $100 - $500 | $5 - $10 | 0 - 10 minutes |
| Tier 2 (Mid-game) | $2,500 - $15,000 | $25 - $75 | 15 - 45 minutes |
| Tier 3 (Late-game) | $50,000 - $250,000 | $150 - $500 | 1 - 3 hours |
| Tier 4 (End-game) | $500,000 - $2,000,000 | $1,000 - $5,000 | 3 - 8 hours |

**Scaling formula:**

```
cost(tier) = baseCost * (scaleFactor ^ (tier - 1))
```

Example with `baseCost = 100` and `scaleFactor = 5`:

```
Tier 1: 100
Tier 2: 500
Tier 3: 2,500
Tier 4: 12,500
Tier 5: 62,500
```

### Unlock Order

Structure the unlock tree as a **linear chain with branches**:

```
BasicDropper --> Conveyor --> SmallCollector
                                  |
                          AdvancedDropper --> LargeCollector --> CashRegister
                                                                     |
                                                              MegaDropper --> AutoCollector
                                                                     |
                                                              (Branch) Decoration items
```

**Design rules:**
- Every tier begins with a new dropper (the income source).
- Collectors are the currency conversion point -- no collector means dropper parts pile up.
- Passive income buildings provide income without dropper interaction.
- Decorations/cosmetics branch off the main line as optional purchases.

### Prestige / Rebirth System

When the player reaches a total earnings threshold, they can **prestige**:

1. All buildings are destroyed and currency resets to 0.
2. The player gains a permanent income multiplier (e.g., +25% per level).
3. New prestige-exclusive buildings or cosmetics may unlock.
4. A prestige counter/badge displays on their plot.

**Prestige balancing:**

| Prestige Level | Multiplier | Required Total Earnings |
|---|---|---|
| 1 | 1.25x | $500,000 |
| 2 | 1.50x | $1,500,000 |
| 3 | 1.75x | $5,000,000 |
| 5 | 2.25x | $25,000,000 |
| 10 | 3.50x | $500,000,000 |

Each prestige should feel faster than the previous one due to the multiplier, but the required earnings threshold grows faster to maintain challenge.

---

## 5. Monetization Strategy

For complete implementation details, load `references/monetization-systems.md`.

### GamePasses (One-Time, Permanent)

| GamePass | Price (Robux) | Effect |
|---|---|---|
| **Auto-Collect** | 249 | Dropper parts automatically convert to currency without reaching the collector |
| **2x Income** | 499 | All income (dropper + passive) is doubled |
| **VIP** | 149 | Exclusive plot decoration, name color, VIP badge |
| **Extra Plot Area** | 349 | Unlocks an additional build zone on the player's plot |

### Developer Products (Repeatable)

| Product | Price (Robux) | Effect |
|---|---|---|
| **$10,000 Cash** | 49 | Instant currency injection |
| **$100,000 Cash** | 249 | Larger currency injection |
| **Skip Tier** | 99 | Instantly unlocks the next building in the tree |
| **Instant Prestige** | 199 | Prestige without meeting the earnings requirement |

### Monetization Placement

- **Auto-Collect prompt** appears after the player manually collects 50 dropper parts (they understand the pain point).
- **2x Income prompt** appears contextually when the player cannot afford a building ("Need more cash? 2x Income makes everything faster.").
- **Cash products** are available in a shop GUI accessible at any time, never force-prompted.
- **Skip Tier** only appears in the upgrade tree UI next to locked buildings.

### Revenue Estimate

```
Conservative (1,000 DAU, 2% conversion, avg $100 Robux purchase):
  Daily: 1,000 * 0.02 * 100 = 2,000 Robux
  Monthly: ~60,000 Robux (~$210 USD)

Moderate (10,000 DAU, 3% conversion, avg $150 Robux purchase):
  Daily: 10,000 * 0.03 * 150 = 45,000 Robux
  Monthly: ~1,350,000 Robux (~$4,725 USD)
```

---

## 6. Performance Considerations

### The Dropper Part Problem

Tycoons generate **many small parts** from droppers. With 8 plots each running 3 droppers at 1-second intervals, that is 24 new parts per second entering the Workspace. Without management, this kills framerate -- especially on mobile.

### Mitigation Strategies

| Strategy | Implementation |
|---|---|
| **Per-plot part cap** | `TycoonConfig.Dropper.maxPartsPerPlot = 50`. Stop spawning when the cap is reached. |
| **Part lifetime** | `Debris:AddItem(part, 15)`. Parts auto-destroy after 15 seconds if uncollected. |
| **Instant collection** | Auto-Collect GamePass bypasses part spawning entirely -- just ticks currency. |
| **Batch collection** | Collector processes all touching parts per heartbeat instead of per-touch-event. |
| **Client-side VFX** | Dropper part visuals can be client-side (UnreliableRemoteEvent for spawn position), with only the collector hit being server-authoritative. |
| **StreamingEnabled** | Enable `Workspace.StreamingEnabled` so players only load nearby tycoons, not all 8. |
| **MeshPart optimization** | Use simple Part primitives for dropper parts, not MeshParts or Unions. |

### StreamingEnabled Configuration

```
Workspace.StreamingEnabled = true
Workspace.StreamingMinRadius = 128    -- studs guaranteed loaded
Workspace.StreamingTargetRadius = 256 -- studs attempted
StreamingIntegrityMode = Enum.StreamingIntegrityMode.PauseOutsideLoadedArea
```

With plots spaced 100 studs apart, a player only loads their own plot and the two nearest neighbors, not all 8.

### Memory Management Checklist

- [ ] Every `.Touched` connection is cleaned up when the plot is released
- [ ] Dropper loop threads are cancelled via `task.cancel()` on player leave
- [ ] Passive income threads are cancelled on player leave
- [ ] `playerPartCount` is decremented when parts are destroyed (use `Destroying` event)
- [ ] `playerBuildings`, `playerCurrency`, `playerMultipliers` tables are nil-ed on leave
- [ ] Cloned building models are destroyed when the plot is released

---

## 7. Launch Checklist

### Tycoon-Specific Items

- [ ] **Plot count matches max players.** If `Players.MaxPlayers = 8`, provide at least 8 plots. Warn or queue players if all plots are taken.
- [ ] **Cost curve tested end-to-end.** Play through the entire progression as a free player. Time each tier. Adjust costs if any tier takes more than 30 minutes without purchases.
- [ ] **Dropper parts clean up reliably.** Join, AFK for 10 minutes, confirm parts are not piling up indefinitely. Check `playerPartCount` stays under the cap.
- [ ] **Plot release works on disconnect.** Leave the game, rejoin, confirm the old plot is available and clean.
- [ ] **Data persistence implemented.** Currency and owned buildings save on leave and restore on rejoin. Use ProfileService or ProfileStore (see SE-1 in SKILL.md).
- [ ] **Prestige resets correctly.** All buildings removed, currency zeroed, multiplier applied, dropper/passive threads stopped and restarted.
- [ ] **GamePasses grant correctly.** Test Auto-Collect (parts skip physics), 2x Income (verify doubled amounts), VIP cosmetics.
- [ ] **Developer Products grant correctly.** Purchase cash packs, verify idempotent `ProcessReceipt`, check `PurchaseHistory` DataStore.
- [ ] **Mobile-friendly.** Test on a low-end device. Confirm steady 30+ FPS with all droppers running. Enable StreamingEnabled.
- [ ] **Button pads respond on all devices.** Touch, click, and gamepad all trigger pad purchases. Test the `.Touched` event fires reliably.
- [ ] **No currency exploits.** Disconnect the client from the internet mid-purchase. Rapidly touch pads. Fire fake RemoteEvents. Confirm the server rejects all invalid requests.
- [ ] **Leaderboard visible.** `leaderstats` displays correctly on the player list.
- [ ] **Plot ownership label visible.** BillboardGui shows owner name from a reasonable distance.
- [ ] **Sound effects present.** Purchase sound on pad activation, dropper spawn sound, collector collection sound, prestige fanfare.
- [ ] **Tutorial / first-time experience.** New players are guided to their first pad. Consider a brief arrow or highlight pointing to the first purchase.

### General Launch Items

Refer to `workflows/publish-checklist.md` for the full publish workflow including game icon, thumbnails, description, social links, and Roblox review submission.
