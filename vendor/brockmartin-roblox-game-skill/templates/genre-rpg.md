# RPG Genre Template

## 1. Genre Overview

**Core Loop:** Quest → Fight → Loot → Level Up → Explore New Area

The RPG genre revolves around character progression. Players accept quests from NPCs, battle enemies to earn XP and loot, level up to grow stronger, allocate stat points, and unlock new zones with tougher challenges and better rewards. A compelling RPG hooks players through a steady drip of meaningful upgrades and narrative context for every action.

**Reference Games:**
- **Blox Fruits** — Devil-fruit combat powers, open-world zones gated by level, boss fights, grinding loops
- **Vesteria** — Classic MMORPG structure with classes, skill trees, party dungeons, and a quest-driven storyline

**Key Pillars:**
1. **Progression** — Every session should feel like forward movement (XP, gear, story)
2. **Choice** — Stat allocation, skill trees, gear loadouts, quest branching
3. **Exploration** — Level-gated zones that reward curiosity
4. **Combat** — Skill-based fights with stat-influenced outcomes

---

## 2. Architecture Blueprint

```
ServerScriptService/
  ├── CharacterStatsService.lua    -- HP, MP, STR, DEF, SPD, Level, XP, stat points
  ├── QuestService.lua             -- Quest accept/track/complete/reward pipeline
  ├── NPCService.lua               -- NPC spawning, AI state machine, loot drops
  ├── DialogService.lua            -- Dialog sequences, choice trees, quest giver hooks
  ├── ZoneService.lua              -- Zone definitions, level gates, streaming control
  └── CombatService.lua            -- Damage calculation, hit detection, cooldowns

ReplicatedStorage/
  ├── Modules/
  │   ├── CharacterStats.lua       -- Shared stat definitions and formulas
  │   ├── QuestDefinitions.lua     -- Quest data tables (objectives, rewards)
  │   ├── NPCDefinitions.lua       -- NPC stat blocks, spawn configs
  │   ├── DialogTrees.lua          -- Dialog node graphs
  │   ├── SkillTreeData.lua        -- Skill tree layouts and costs
  │   └── ZoneDefinitions.lua      -- Zone metadata (level range, enemies, resources)
  ├── Remotes/
  │   ├── StatsRemotes.lua         -- AllocateStat, GetStats
  │   ├── QuestRemotes.lua         -- AcceptQuest, CompleteQuest, GetActiveQuests
  │   ├── DialogRemotes.lua        -- StartDialog, SelectChoice
  │   └── ZoneRemotes.lua          -- RequestZoneEntry
  └── Types/
      └── RPGTypes.lua             -- Shared type definitions

StarterPlayerScripts/
  ├── StatsController.lua          -- Client-side stat display, stat allocation UI
  ├── QuestController.lua          -- Quest tracker HUD, objective markers
  ├── DialogController.lua         -- Dialog box UI, choice buttons
  └── ZoneController.lua           -- Zone transition effects, minimap

StarterGui/
  ├── StatsHUD/                    -- HP/MP bars, level indicator
  ├── QuestTracker/                -- Active quest objectives
  ├── DialogBox/                   -- NPC conversation window
  ├── InventoryUI/                 -- Gear and items
  └── SkillTreeUI/                 -- Skill tree allocation panel
```

**Key Modules:**

| Module | Responsibility |
|---|---|
| **CharacterStats** | Manages HP, MaxHP, MP, STR, DEF, SPD, Level, XP, StatPoints. All mutations server-side. |
| **QuestManager** | Tracks quest state per player: available, active, completed. Validates objective progress. |
| **NPCSystem** | Spawns NPCs from spawn points. Runs AI state machines. Handles death and loot drops. |
| **DialogManager** | Drives NPC conversations. Supports linear sequences and branching choice nodes. |
| **ZoneManager** | Enforces level requirements for zone entry. Manages zone streaming and transitions. |
| **SkillTree** | Skill point allocation, prerequisite checking, ability unlocking. |

---

## 3. Core Systems

### 3.1 Character Stat System and Leveling

```luau
--[[
  CharacterStats (ModuleScript in ReplicatedStorage/Modules)
  Shared stat definitions, XP formula, and level-up logic.
  All stat mutations happen on the server via CharacterStatsService.
]]

local CharacterStats = {}

-- Stat template for a new character
function CharacterStats.newCharacter(): CharacterData
    return {
        Level = 1,
        XP = 0,
        StatPoints = 0,

        -- Core stats
        MaxHP = 100,
        HP = 100,
        MaxMP = 50,
        MP = 50,
        STR = 10,  -- Affects physical damage
        DEF = 5,   -- Reduces incoming damage
        SPD = 5,   -- Affects movement speed and dodge chance
    }
end

-- XP required to reach the next level from the current level
-- Formula: floor(100 * 1.5 ^ (level - 1))
function CharacterStats.xpToNextLevel(level: number): number
    return math.floor(100 * 1.5 ^ (level - 1))
end

-- Per-level-up stat increases (base growth before stat point allocation)
local LEVEL_UP_BONUSES = {
    MaxHP = 10,
    MaxMP = 5,
}

-- Process XP gain. Returns true if at least one level-up occurred.
function CharacterStats.addXP(stats: CharacterData, amount: number): boolean
    assert(amount > 0, "XP amount must be positive")

    stats.XP += amount
    local leveled = false

    while stats.XP >= CharacterStats.xpToNextLevel(stats.Level) do
        stats.XP -= CharacterStats.xpToNextLevel(stats.Level)
        stats.Level += 1
        leveled = true

        -- Apply base stat growth
        stats.MaxHP += LEVEL_UP_BONUSES.MaxHP
        stats.MaxMP += LEVEL_UP_BONUSES.MaxMP

        -- Grant stat points for allocation
        stats.StatPoints += 3

        -- Heal to full on level up
        stats.HP = stats.MaxHP
        stats.MP = stats.MaxMP
    end

    return leveled
end

-- Allocate a stat point. Returns true on success.
local ALLOCATABLE_STATS = { STR = true, DEF = true, SPD = true, MaxHP = true, MaxMP = true }

function CharacterStats.allocateStat(stats: CharacterData, statName: string): boolean
    if stats.StatPoints <= 0 then
        return false
    end

    if not ALLOCATABLE_STATS[statName] then
        return false
    end

    stats[statName] += 1
    stats.StatPoints -= 1
    return true
end

-- Calculate physical damage dealt
function CharacterStats.calculateDamage(attackerSTR: number, defenderDEF: number, baseDamage: number): number
    local raw = baseDamage + (attackerSTR * 1.5)
    local reduction = defenderDEF * 0.8
    return math.max(1, math.floor(raw - reduction))
end

-- Type definition
export type CharacterData = {
    Level: number,
    XP: number,
    StatPoints: number,
    MaxHP: number,
    HP: number,
    MaxMP: number,
    MP: number,
    STR: number,
    DEF: number,
    SPD: number,
}

return CharacterStats
```

```luau
--[[
  CharacterStatsService (Script in ServerScriptService)
  Server authority over all character stats. Handles XP gain, level-up,
  stat allocation, and replication to clients.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CharacterStats = require(ReplicatedStorage.Modules.CharacterStats)

local allocateStatRemote = ReplicatedStorage.Remotes.AllocateStat :: RemoteEvent
local getStatsRemote = ReplicatedStorage.Remotes.GetStats :: RemoteFunction
local statsUpdatedRemote = ReplicatedStorage.Remotes.StatsUpdated :: RemoteEvent
local levelUpRemote = ReplicatedStorage.Remotes.LevelUp :: RemoteEvent

-- Per-player stat storage (replace with ProfileService for persistence)
local playerStats: { [Player]: CharacterStats.CharacterData } = {}

local function initPlayer(player: Player)
    playerStats[player] = CharacterStats.newCharacter()
    statsUpdatedRemote:FireClient(player, playerStats[player])
end

local function cleanupPlayer(player: Player)
    -- Save to DataStore here before clearing
    playerStats[player] = nil
end

Players.PlayerAdded:Connect(initPlayer)
Players.PlayerRemoving:Connect(cleanupPlayer)

-- Initialize already-connected players (for late script load)
for _, player in Players:GetPlayers() do
    if not playerStats[player] then
        initPlayer(player)
    end
end

-- Client requests stat allocation
allocateStatRemote.OnServerEvent:Connect(function(player: Player, statName: unknown)
    local stats = playerStats[player]
    if not stats then return end

    -- Validate input type
    if typeof(statName) ~= "string" then return end

    if CharacterStats.allocateStat(stats, statName) then
        statsUpdatedRemote:FireClient(player, stats)
    end
end)

-- Client requests current stats
getStatsRemote.OnServerInvoke = function(player: Player)
    return playerStats[player]
end

-- Public API for other server scripts
local CharacterStatsService = {}

function CharacterStatsService.getStats(player: Player): CharacterStats.CharacterData?
    return playerStats[player]
end

function CharacterStatsService.grantXP(player: Player, amount: number)
    local stats = playerStats[player]
    if not stats then return end

    local leveled = CharacterStats.addXP(stats, amount)
    statsUpdatedRemote:FireClient(player, stats)

    if leveled then
        levelUpRemote:FireClient(player, stats.Level)
    end
end

function CharacterStatsService.takeDamage(player: Player, amount: number)
    local stats = playerStats[player]
    if not stats then return end

    stats.HP = math.max(0, stats.HP - amount)
    statsUpdatedRemote:FireClient(player, stats)

    if stats.HP <= 0 then
        -- Handle player death (respawn logic)
        task.defer(function()
            stats.HP = stats.MaxHP
            stats.MP = stats.MaxMP
            statsUpdatedRemote:FireClient(player, stats)
        end)
    end
end

return CharacterStatsService
```

### 3.2 Quest System

```luau
--[[
  QuestDefinitions (ModuleScript in ReplicatedStorage/Modules)
  Defines all quests, their objectives, and rewards.
]]

local QuestDefinitions = {}

export type ObjectiveType = "kill" | "collect" | "talk"

export type Objective = {
    type: ObjectiveType,
    target: string,       -- Enemy name, item name, or NPC name
    amount: number,       -- How many to kill/collect (1 for talk)
    description: string,  -- Human-readable objective text
}

export type QuestReward = {
    xp: number,
    gold: number?,
    items: { string }?,  -- Item IDs to grant
}

export type QuestDef = {
    id: string,
    name: string,
    description: string,
    levelRequired: number,
    giverNPC: string,           -- NPC who gives this quest
    turnInNPC: string,          -- NPC who accepts completion (often same as giver)
    objectives: { Objective },
    rewards: QuestReward,
    prerequisiteQuestId: string?,  -- Must complete this quest first
}

-- Quest registry
QuestDefinitions.quests = {
    ["quest_first_hunt"] = {
        id = "quest_first_hunt",
        name = "First Hunt",
        description = "Prove your worth by hunting slimes in the Starter Meadow.",
        levelRequired = 1,
        giverNPC = "Elder Moran",
        turnInNPC = "Elder Moran",
        objectives = {
            {
                type = "kill",
                target = "Slime",
                amount = 5,
                description = "Defeat 5 Slimes",
            },
        },
        rewards = { xp = 150, gold = 50 },
    },

    ["quest_herb_gathering"] = {
        id = "quest_herb_gathering",
        name = "Herb Gathering",
        description = "Collect healing herbs for the village healer.",
        levelRequired = 2,
        giverNPC = "Healer Aria",
        turnInNPC = "Healer Aria",
        objectives = {
            {
                type = "collect",
                target = "HealingHerb",
                amount = 3,
                description = "Collect 3 Healing Herbs",
            },
        },
        rewards = { xp = 200, gold = 75, items = { "potion_small" } },
        prerequisiteQuestId = "quest_first_hunt",
    },

    ["quest_village_report"] = {
        id = "quest_village_report",
        name = "Report to the Captain",
        description = "Deliver the healer's report to Captain Brynn at the outpost.",
        levelRequired = 3,
        giverNPC = "Healer Aria",
        turnInNPC = "Captain Brynn",
        objectives = {
            {
                type = "talk",
                target = "Captain Brynn",
                amount = 1,
                description = "Speak with Captain Brynn",
            },
        },
        rewards = { xp = 100, gold = 25 },
        prerequisiteQuestId = "quest_herb_gathering",
    },
} :: { [string]: QuestDef }

function QuestDefinitions.get(questId: string): QuestDef?
    return QuestDefinitions.quests[questId]
end

return QuestDefinitions
```

```luau
--[[
  QuestService (Script in ServerScriptService)
  Server-side quest state machine: accept, track progress, complete, grant rewards.
  Never trust client claims of objective completion.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local QuestDefinitions = require(ReplicatedStorage.Modules.QuestDefinitions)
-- Assumes CharacterStatsService is accessible for XP rewards
local CharacterStatsService = require(script.Parent.CharacterStatsService)

local acceptQuestRemote = ReplicatedStorage.Remotes.AcceptQuest :: RemoteEvent
local questUpdatedRemote = ReplicatedStorage.Remotes.QuestUpdated :: RemoteEvent
local getActiveQuestsRemote = ReplicatedStorage.Remotes.GetActiveQuests :: RemoteFunction

export type QuestProgress = {
    questId: string,
    objectiveProgress: { number },  -- Parallel array to quest objectives
    completed: boolean,
    turnedIn: boolean,
}

export type PlayerQuestState = {
    active: { [string]: QuestProgress },
    completed: { [string]: boolean },  -- questId → true
}

-- Per-player quest state (replace with DataStore persistence)
local playerQuestStates: { [Player]: PlayerQuestState } = {}

local QuestService = {}

local function initPlayer(player: Player)
    playerQuestStates[player] = {
        active = {},
        completed = {},
    }
end

local function cleanupPlayer(player: Player)
    -- Save to DataStore here
    playerQuestStates[player] = nil
end

Players.PlayerAdded:Connect(initPlayer)
Players.PlayerRemoving:Connect(cleanupPlayer)

for _, player in Players:GetPlayers() do
    if not playerQuestStates[player] then
        initPlayer(player)
    end
end

-- Check if a player meets the prerequisites for a quest
local function canAcceptQuest(player: Player, questDef: QuestDefinitions.QuestDef): boolean
    local state = playerQuestStates[player]
    if not state then return false end

    -- Already active or completed
    if state.active[questDef.id] or state.completed[questDef.id] then
        return false
    end

    -- Level check
    local stats = CharacterStatsService.getStats(player)
    if not stats or stats.Level < questDef.levelRequired then
        return false
    end

    -- Prerequisite check
    if questDef.prerequisiteQuestId and not state.completed[questDef.prerequisiteQuestId] then
        return false
    end

    return true
end

-- Accept a quest
acceptQuestRemote.OnServerEvent:Connect(function(player: Player, questId: unknown)
    if typeof(questId) ~= "string" then return end

    local questDef = QuestDefinitions.get(questId)
    if not questDef then return end
    if not canAcceptQuest(player, questDef) then return end

    local state = playerQuestStates[player]

    -- Initialize progress (all objectives start at 0)
    local progress: QuestProgress = {
        questId = questId,
        objectiveProgress = {},
        completed = false,
        turnedIn = false,
    }
    for i = 1, #questDef.objectives do
        progress.objectiveProgress[i] = 0
    end

    state.active[questId] = progress
    questUpdatedRemote:FireClient(player, "accepted", questId, progress)
end)

-- Get active quests (client request)
getActiveQuestsRemote.OnServerInvoke = function(player: Player)
    local state = playerQuestStates[player]
    if not state then return {} end
    return state.active
end

-- Server API: Record a kill for quest objectives
function QuestService.onEnemyKilled(player: Player, enemyName: string)
    local state = playerQuestStates[player]
    if not state then return end

    for questId, progress in state.active do
        if progress.completed then continue end

        local questDef = QuestDefinitions.get(questId)
        if not questDef then continue end

        for i, objective in questDef.objectives do
            if objective.type == "kill" and objective.target == enemyName then
                if progress.objectiveProgress[i] < objective.amount then
                    progress.objectiveProgress[i] += 1
                    QuestService._checkCompletion(player, questId, progress, questDef)
                    questUpdatedRemote:FireClient(player, "progress", questId, progress)
                end
            end
        end
    end
end

-- Server API: Record an item collection for quest objectives
function QuestService.onItemCollected(player: Player, itemName: string)
    local state = playerQuestStates[player]
    if not state then return end

    for questId, progress in state.active do
        if progress.completed then continue end

        local questDef = QuestDefinitions.get(questId)
        if not questDef then continue end

        for i, objective in questDef.objectives do
            if objective.type == "collect" and objective.target == itemName then
                if progress.objectiveProgress[i] < objective.amount then
                    progress.objectiveProgress[i] += 1
                    QuestService._checkCompletion(player, questId, progress, questDef)
                    questUpdatedRemote:FireClient(player, "progress", questId, progress)
                end
            end
        end
    end
end

-- Server API: Record an NPC talk for quest objectives
function QuestService.onNPCTalked(player: Player, npcName: string)
    local state = playerQuestStates[player]
    if not state then return end

    for questId, progress in state.active do
        if progress.completed then continue end

        local questDef = QuestDefinitions.get(questId)
        if not questDef then continue end

        for i, objective in questDef.objectives do
            if objective.type == "talk" and objective.target == npcName then
                if progress.objectiveProgress[i] < objective.amount then
                    progress.objectiveProgress[i] += 1
                    QuestService._checkCompletion(player, questId, progress, questDef)
                    questUpdatedRemote:FireClient(player, "progress", questId, progress)
                end
            end
        end
    end
end

-- Check if all objectives are met
function QuestService._checkCompletion(
    player: Player,
    questId: string,
    progress: QuestProgress,
    questDef: QuestDefinitions.QuestDef
)
    for i, objective in questDef.objectives do
        if progress.objectiveProgress[i] < objective.amount then
            return
        end
    end
    progress.completed = true
    questUpdatedRemote:FireClient(player, "ready", questId, progress)
end

-- Server API: Turn in a completed quest at the correct NPC
function QuestService.turnInQuest(player: Player, questId: string, npcName: string): boolean
    local state = playerQuestStates[player]
    if not state then return false end

    local progress = state.active[questId]
    if not progress or not progress.completed or progress.turnedIn then
        return false
    end

    local questDef = QuestDefinitions.get(questId)
    if not questDef then return false end
    if questDef.turnInNPC ~= npcName then return false end

    -- Grant rewards
    CharacterStatsService.grantXP(player, questDef.rewards.xp)
    -- Gold and item rewards would go through InventoryService (not shown)

    -- Mark as turned in and completed
    progress.turnedIn = true
    state.active[questId] = nil
    state.completed[questId] = true

    questUpdatedRemote:FireClient(player, "turnedIn", questId, nil)
    return true
end

-- Server API: Get available quests from a specific NPC for a player
function QuestService.getAvailableQuestsFromNPC(player: Player, npcName: string): { QuestDefinitions.QuestDef }
    local available = {}
    for _, questDef in QuestDefinitions.quests do
        if questDef.giverNPC == npcName and canAcceptQuest(player, questDef) then
            table.insert(available, questDef)
        end
    end
    return available
end

return QuestService
```

### 3.3 NPC System

```luau
--[[
  NPCService (Script in ServerScriptService)
  Spawns NPCs from spawn points, runs a basic AI state machine:
    Idle → Patrol → Chase → Attack → Return
  Handles health, death, respawn, and loot drops.
]]

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local CHASE_RANGE = 40
local ATTACK_RANGE = 5
local RETURN_RANGE = 60  -- Distance from spawn before forced return
local PATROL_RADIUS = 15
local RESPAWN_DELAY = 30

export type NPCState = "idle" | "patrol" | "chase" | "attack" | "returning" | "dead"

export type NPCData = {
    name: string,
    model: Model,
    humanoid: Humanoid,
    spawnPoint: Vector3,
    state: NPCState,

    -- Stats
    maxHP: number,
    hp: number,
    damage: number,
    xpReward: number,

    -- Loot table: { { itemId: string, dropChance: number } }
    lootTable: { { itemId: string, dropChance: number } },

    -- AI internals
    target: Player?,
    patrolTarget: Vector3?,
    lastAttackTime: number,
    attackCooldown: number,
    idleTimer: number,
}

local activeNPCs: { NPCData } = {}

local NPCService = {}

function NPCService.spawnNPC(config: {
    name: string,
    modelTemplate: Model,
    spawnPosition: Vector3,
    maxHP: number,
    damage: number,
    xpReward: number,
    lootTable: { { itemId: string, dropChance: number } }?,
    attackCooldown: number?,
}): NPCData
    local model = config.modelTemplate:Clone()
    model:PivotTo(CFrame.new(config.spawnPosition))
    model.Parent = workspace.NPCs

    local humanoid = model:FindFirstChildOfClass("Humanoid")
    assert(humanoid, "NPC model must contain a Humanoid")

    humanoid.MaxHealth = config.maxHP
    humanoid.Health = config.maxHP

    local npc: NPCData = {
        name = config.name,
        model = model,
        humanoid = humanoid,
        spawnPoint = config.spawnPosition,
        state = "idle",
        maxHP = config.maxHP,
        hp = config.maxHP,
        damage = config.damage,
        xpReward = config.xpReward,
        lootTable = config.lootTable or {},
        target = nil,
        patrolTarget = nil,
        lastAttackTime = 0,
        attackCooldown = config.attackCooldown or 2,
        idleTimer = 0,
    }

    -- Listen for damage
    humanoid.HealthChanged:Connect(function(newHealth)
        npc.hp = newHealth
        if newHealth <= 0 then
            NPCService._onDeath(npc)
        end
    end)

    table.insert(activeNPCs, npc)
    return npc
end

-- Find the closest player within range
local function findClosestPlayer(position: Vector3, range: number): Player?
    local closest: Player? = nil
    local closestDist = range

    for _, player in Players:GetPlayers() do
        local character = player.Character
        if not character then continue end

        local root = character:FindFirstChild("HumanoidRootPart")
        if not root then continue end

        local dist = (root.Position - position).Magnitude
        if dist < closestDist then
            closest = player
            closestDist = dist
        end
    end

    return closest
end

-- Get NPC's current position
local function getNPCPosition(npc: NPCData): Vector3?
    local root = npc.model:FindFirstChild("HumanoidRootPart")
    return if root then root.Position else nil
end

-- AI state machine tick
local function updateNPC(npc: NPCData, dt: number)
    if npc.state == "dead" then return end

    local pos = getNPCPosition(npc)
    if not pos then return end

    local distFromSpawn = (pos - npc.spawnPoint).Magnitude

    -- Force return if too far from spawn
    if distFromSpawn > RETURN_RANGE and npc.state ~= "returning" then
        npc.state = "returning"
        npc.target = nil
    end

    if npc.state == "idle" then
        npc.idleTimer += dt
        -- Look for nearby players
        local player = findClosestPlayer(pos, CHASE_RANGE)
        if player then
            npc.target = player
            npc.state = "chase"
            return
        end
        -- Start patrolling after idle period
        if npc.idleTimer > 3 then
            local offset = Vector3.new(
                math.random() * PATROL_RADIUS * 2 - PATROL_RADIUS,
                0,
                math.random() * PATROL_RADIUS * 2 - PATROL_RADIUS
            )
            npc.patrolTarget = npc.spawnPoint + offset
            npc.state = "patrol"
            npc.idleTimer = 0
        end

    elseif npc.state == "patrol" then
        if not npc.patrolTarget then
            npc.state = "idle"
            return
        end
        npc.humanoid:MoveTo(npc.patrolTarget)
        -- Check for nearby players while patrolling
        local player = findClosestPlayer(pos, CHASE_RANGE)
        if player then
            npc.target = player
            npc.state = "chase"
            return
        end
        -- Reached patrol target
        if (pos - npc.patrolTarget).Magnitude < 3 then
            npc.state = "idle"
            npc.patrolTarget = nil
        end

    elseif npc.state == "chase" then
        if not npc.target or not npc.target.Character then
            npc.target = nil
            npc.state = "returning"
            return
        end
        local targetRoot = npc.target.Character:FindFirstChild("HumanoidRootPart")
        if not targetRoot then
            npc.target = nil
            npc.state = "returning"
            return
        end
        local dist = (targetRoot.Position - pos).Magnitude
        if dist > CHASE_RANGE * 1.5 then
            -- Target escaped
            npc.target = nil
            npc.state = "returning"
        elseif dist <= ATTACK_RANGE then
            npc.state = "attack"
        else
            npc.humanoid:MoveTo(targetRoot.Position)
        end

    elseif npc.state == "attack" then
        if not npc.target or not npc.target.Character then
            npc.target = nil
            npc.state = "returning"
            return
        end
        local targetRoot = npc.target.Character:FindFirstChild("HumanoidRootPart")
        if not targetRoot then
            npc.target = nil
            npc.state = "returning"
            return
        end
        local dist = (targetRoot.Position - pos).Magnitude
        if dist > ATTACK_RANGE then
            npc.state = "chase"
            return
        end
        -- Attack on cooldown
        local now = tick()
        if now - npc.lastAttackTime >= npc.attackCooldown then
            npc.lastAttackTime = now
            local targetHumanoid = npc.target.Character:FindFirstChildOfClass("Humanoid")
            if targetHumanoid then
                targetHumanoid:TakeDamage(npc.damage)
            end
        end

    elseif npc.state == "returning" then
        npc.humanoid:MoveTo(npc.spawnPoint)
        -- Heal while returning
        npc.hp = math.min(npc.maxHP, npc.hp + dt * 10)
        npc.humanoid.Health = npc.hp
        if (pos - npc.spawnPoint).Magnitude < 5 then
            npc.hp = npc.maxHP
            npc.humanoid.Health = npc.maxHP
            npc.state = "idle"
        end
    end
end

function NPCService._onDeath(npc: NPCData)
    npc.state = "dead"

    -- Determine who killed it (last player to deal damage, simplified here)
    local killer = npc.target
    if killer then
        -- Grant XP
        local CharacterStatsService = require(script.Parent.CharacterStatsService)
        CharacterStatsService.grantXP(killer, npc.xpReward)

        -- Notify quest system
        local QuestService = require(script.Parent.QuestService)
        QuestService.onEnemyKilled(killer, npc.name)

        -- Roll loot drops
        for _, loot in npc.lootTable do
            if math.random() <= loot.dropChance then
                -- Grant item via InventoryService (not shown)
            end
        end
    end

    -- Remove model
    npc.model:Destroy()

    -- Schedule respawn
    task.delay(RESPAWN_DELAY, function()
        npc.hp = npc.maxHP
        npc.state = "idle"
        npc.target = nil
        -- Re-clone and re-insert the model (simplified)
    end)
end

-- Main AI loop
RunService.Heartbeat:Connect(function(dt)
    for _, npc in activeNPCs do
        updateNPC(npc, dt)
    end
end)

return NPCService
```

### 3.4 Dialog System

```luau
--[[
  DialogTrees (ModuleScript in ReplicatedStorage/Modules)
  Defines NPC conversation trees with sequential lines and branching choices.
  Nodes can trigger quest offers or quest turn-ins.
]]

local DialogTrees = {}

export type DialogAction = {
    type: "offerQuest" | "turnInQuest" | "openShop" | "none",
    questId: string?,
    shopId: string?,
}

export type DialogChoice = {
    text: string,
    nextNodeId: string?,  -- nil = end conversation
    action: DialogAction?,
}

export type DialogNode = {
    id: string,
    speaker: string,
    lines: { string },            -- Shown sequentially (click to advance)
    choices: { DialogChoice }?,    -- nil = auto-advance or end
    nextNodeId: string?,           -- If no choices, go here next (nil = end)
    action: DialogAction?,         -- Action triggered when node is displayed
}

export type DialogTree = {
    npcName: string,
    startNodeId: string,
    nodes: { [string]: DialogNode },
}

DialogTrees.trees = {
    ["Elder Moran"] = {
        npcName = "Elder Moran",
        startNodeId = "greeting",
        nodes = {
            ["greeting"] = {
                id = "greeting",
                speaker = "Elder Moran",
                lines = {
                    "Welcome, young adventurer.",
                    "Our village has been troubled by slimes in the meadow.",
                },
                choices = {
                    { text = "I'll help!", nextNodeId = "accept_quest", action = { type = "offerQuest", questId = "quest_first_hunt" } },
                    { text = "Not right now.", nextNodeId = "decline" },
                },
            },
            ["accept_quest"] = {
                id = "accept_quest",
                speaker = "Elder Moran",
                lines = { "Brave soul! Defeat 5 slimes and return to me." },
            },
            ["decline"] = {
                id = "decline",
                speaker = "Elder Moran",
                lines = { "Come back when you are ready." },
            },
        },
    },
} :: { [string]: DialogTree }

function DialogTrees.get(npcName: string): DialogTree?
    return DialogTrees.trees[npcName]
end

return DialogTrees
```

```luau
--[[
  DialogService (Script in ServerScriptService)
  Manages active dialog sessions. Validates transitions server-side.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local DialogTrees = require(ReplicatedStorage.Modules.DialogTrees)

local startDialogRemote = ReplicatedStorage.Remotes.StartDialog :: RemoteEvent
local dialogNodeRemote = ReplicatedStorage.Remotes.DialogNode :: RemoteEvent
local selectChoiceRemote = ReplicatedStorage.Remotes.SelectChoice :: RemoteEvent
local dialogEndRemote = ReplicatedStorage.Remotes.DialogEnd :: RemoteEvent

-- Active dialog sessions per player
local activeSessions: { [Player]: { tree: DialogTrees.DialogTree, currentNodeId: string } } = {}

-- Player initiates conversation with NPC
startDialogRemote.OnServerEvent:Connect(function(player: Player, npcName: unknown)
    if typeof(npcName) ~= "string" then return end
    if activeSessions[player] then return end  -- Already in dialog

    local tree = DialogTrees.get(npcName)
    if not tree then return end

    local startNode = tree.nodes[tree.startNodeId]
    if not startNode then return end

    activeSessions[player] = { tree = tree, currentNodeId = tree.startNodeId }
    dialogNodeRemote:FireClient(player, startNode)
end)

-- Player selects a dialog choice
selectChoiceRemote.OnServerEvent:Connect(function(player: Player, choiceIndex: unknown)
    if typeof(choiceIndex) ~= "number" then return end

    local session = activeSessions[player]
    if not session then return end

    local currentNode = session.tree.nodes[session.currentNodeId]
    if not currentNode or not currentNode.choices then return end

    local choice = currentNode.choices[choiceIndex]
    if not choice then return end

    -- Handle action from the choice
    if choice.action then
        handleAction(player, choice.action)
    end

    -- Advance to next node or end
    if choice.nextNodeId then
        local nextNode = session.tree.nodes[choice.nextNodeId]
        if nextNode then
            session.currentNodeId = choice.nextNodeId

            if nextNode.action then
                handleAction(player, nextNode.action)
            end

            dialogNodeRemote:FireClient(player, nextNode)

            -- If no choices and no nextNodeId, end after displaying
            if not nextNode.choices and not nextNode.nextNodeId then
                task.delay(0, function()
                    activeSessions[player] = nil
                    dialogEndRemote:FireClient(player)
                end)
            end
        else
            activeSessions[player] = nil
            dialogEndRemote:FireClient(player)
        end
    else
        activeSessions[player] = nil
        dialogEndRemote:FireClient(player)
    end
end)

function handleAction(player: Player, action: DialogTrees.DialogAction)
    if action.type == "offerQuest" and action.questId then
        -- Trigger quest offer UI on client (quest acceptance goes through QuestService)
    elseif action.type == "turnInQuest" and action.questId then
        local QuestService = require(script.Parent.QuestService)
        local session = activeSessions[player]
        if session then
            QuestService.turnInQuest(player, action.questId, session.tree.npcName)
        end
    elseif action.type == "openShop" and action.shopId then
        -- Open shop UI on client
    end
end

return nil
```

### 3.5 Zone / Map System

```luau
--[[
  ZoneDefinitions (ModuleScript in ReplicatedStorage/Modules)
  Metadata for each zone: level range, enemies, resources, connections.
]]

local ZoneDefinitions = {}

export type ZoneDef = {
    id: string,
    name: string,
    levelRange: { min: number, max: number },
    enemies: { string },          -- Enemy names that spawn here
    resources: { string },        -- Gatherable resource names
    connectedZones: { string },   -- Zone IDs this zone connects to
    spawnPosition: Vector3,       -- Where players appear when entering
}

ZoneDefinitions.zones = {
    ["starter_meadow"] = {
        id = "starter_meadow",
        name = "Starter Meadow",
        levelRange = { min = 1, max = 5 },
        enemies = { "Slime", "Goblin Scout" },
        resources = { "HealingHerb", "Wood" },
        connectedZones = { "dark_forest" },
        spawnPosition = Vector3.new(0, 5, 0),
    },
    ["dark_forest"] = {
        id = "dark_forest",
        name = "Dark Forest",
        levelRange = { min = 5, max = 15 },
        enemies = { "Wolf", "Forest Troll", "Dark Mage" },
        resources = { "IronOre", "Mushroom" },
        connectedZones = { "starter_meadow", "crystal_caves" },
        spawnPosition = Vector3.new(500, 5, 0),
    },
    ["crystal_caves"] = {
        id = "crystal_caves",
        name = "Crystal Caves",
        levelRange = { min = 15, max = 30 },
        enemies = { "Crystal Golem", "Cave Bat Swarm", "Shadow Wraith" },
        resources = { "Crystal Shard", "Mithril Ore" },
        connectedZones = { "dark_forest" },
        spawnPosition = Vector3.new(1000, 5, 0),
    },
} :: { [string]: ZoneDef }

return ZoneDefinitions
```

```luau
--[[
  ZoneService (Script in ServerScriptService)
  Enforces level-gated zone entry. Teleports players who meet requirements.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ZoneDefinitions = require(ReplicatedStorage.Modules.ZoneDefinitions)
local CharacterStatsService = require(script.Parent.CharacterStatsService)

local requestZoneEntryRemote = ReplicatedStorage.Remotes.RequestZoneEntry :: RemoteEvent
local zoneEntryResultRemote = ReplicatedStorage.Remotes.ZoneEntryResult :: RemoteEvent

requestZoneEntryRemote.OnServerEvent:Connect(function(player: Player, zoneId: unknown)
    if typeof(zoneId) ~= "string" then return end

    local zoneDef = ZoneDefinitions.zones[zoneId]
    if not zoneDef then return end

    local stats = CharacterStatsService.getStats(player)
    if not stats then return end

    if stats.Level < zoneDef.levelRange.min then
        zoneEntryResultRemote:FireClient(player, false, "denied", zoneDef.levelRange.min)
        return
    end

    -- Teleport player to zone spawn
    local character = player.Character
    if character then
        local root = character:FindFirstChild("HumanoidRootPart")
        if root then
            root.CFrame = CFrame.new(zoneDef.spawnPosition)
        end
    end

    zoneEntryResultRemote:FireClient(player, true, zoneDef.id, nil)
end)
```

---

## 4. Progression Design

### XP Curve

| Level | XP to Next | Cumulative XP |
|---|---|---|
| 1 | 100 | 0 |
| 2 | 150 | 100 |
| 3 | 225 | 250 |
| 5 | 506 | 862 |
| 10 | 3,844 | 8,488 |
| 15 | 29,193 | 66,430 |
| 20 | 221,689 | 509,607 |
| 25 | 1,683,670 | 3,876,894 |

**Formula:** `XP_needed = floor(100 * 1.5 ^ (level - 1))`

This exponential curve keeps early levels fast (minutes) and late levels rewarding (hours). Tune the base (100) and growth factor (1.5) to adjust pacing.

### Stat Scaling Per Level

- **Base growth (automatic):** +10 MaxHP, +5 MaxMP per level
- **Stat points (player choice):** 3 points per level into STR, DEF, SPD, MaxHP, or MaxMP
- **Soft caps:** Consider diminishing returns above 100 in any single stat to encourage diversification

### Gear Tiers

| Tier | Color | Stat Multiplier | Drop Source |
|---|---|---|---|
| **Common** | White | 1.0x | All enemies |
| **Uncommon** | Green | 1.3x | Level 5+ enemies |
| **Rare** | Blue | 1.7x | Level 15+ enemies, quest rewards |
| **Epic** | Purple | 2.2x | Bosses, rare drops |
| **Legendary** | Gold | 3.0x | World bosses, raid clears |

**Stat ranges per tier (example sword at level 10):**
- Common: STR +3-5
- Uncommon: STR +5-8
- Rare: STR +8-12, bonus effect (e.g., +2% crit)
- Epic: STR +12-18, bonus effect, socket slot
- Legendary: STR +18-25, unique passive ability, 2 socket slots

### Skill Trees

- Each class (Warrior, Mage, Ranger) has its own skill tree
- Earn 1 skill point per 2 levels
- Skills have prerequisite skills (tree structure)
- Active skills (abilities with cooldowns) and passive skills (stat bonuses, procs)
- Respec available for gold cost (increases each time)

---

## 5. Monetization Strategy

| Product | Type | Price Range | Impact |
|---|---|---|---|
| **2x XP Boost** | GamePass | 299-499 Robux | Doubles XP gain permanently. Does not affect stat points or gear drops. |
| **Exclusive Class** | GamePass | 499-799 Robux | Unique class (e.g., Shadow Knight) with its own skill tree. Balanced to be different, not stronger. |
| **Exclusive Weapon** | GamePass | 199-399 Robux | Cosmetically unique weapon with stats equivalent to an Uncommon-tier drop of the player's level. |
| **Expanded Inventory** | GamePass | 149-299 Robux | Double inventory slots (e.g., 20 → 40). Quality-of-life, not power. |
| **Cosmetic Bundles** | Developer Product | 99-299 Robux | Skins, particle effects, name colors. No gameplay impact. |
| **Premium Quest Line** | GamePass | 399-599 Robux | Exclusive story content with unique cosmetic rewards. XP/gold rewards match free quests. |
| **Pet Companion** | GamePass | 299-499 Robux | Auto-loot, small XP bonus (+5%), cosmetic variety. |

**Guidelines:**
- Never gate core progression behind purchases
- XP boosts are the highest-converting RPG monetization product
- Cosmetics have the best long-term revenue and lowest churn impact
- Avoid "pay to win" perception: premium gear should never exceed what free players can earn

---

## 6. Performance Considerations

### NPC Count Management
- **Despawn distant NPCs:** If a player is more than 200 studs from an NPC's spawn zone, despawn the NPC model. Re-spawn when a player enters range.
- **NPC pool limit:** Cap active NPC count per zone (e.g., 30 max). Use a spawn queue when at capacity.
- **Stagger AI ticks:** Do not update all NPC AI on every frame. Rotate through subsets (e.g., update 10 NPCs per Heartbeat).

### LOD for NPCs
- **Close (< 50 studs):** Full model, animations, name tag
- **Medium (50-150 studs):** Simplified mesh, no accessories, name tag
- **Far (150-200 studs):** Billboard sprite or no visual, AI still ticks at reduced rate
- **Beyond 200 studs:** Despawned entirely

### Zone Streaming
- Enable `Workspace.StreamingEnabled = true`
- Set `StreamingTargetRadius` to match zone sizes (256-512 studs)
- Use `StreamingMinRadius` to keep the immediate area loaded (64 studs)
- Place zone barriers as non-streamed persistent parts
- Preload assets for adjacent zones when player approaches a zone gate

### General Tips
- Use `CollectionService` tags for batch operations on NPCs and collectibles
- Pool frequently created/destroyed objects (damage numbers, loot pickups)
- Limit particle emitters on mobile: reduce `Rate` and `Lifetime` per platform
- Profile with MicroProfiler regularly; target < 16ms server Heartbeat

---

## 7. Launch Checklist

### Balance Testing
- [ ] XP curve feels right: levels 1-5 in first 20 minutes, noticeable slowdown by level 10
- [ ] No stat allocation that trivializes content (e.g., all-DEF making player invincible)
- [ ] Gear drops feel rewarding but not game-breaking
- [ ] Boss difficulty scales with expected level and gear tier
- [ ] Economy sinks: gold spent on respecs, potions, repairs balances quest gold income

### Quest Flow Verification
- [ ] Every quest can be accepted, progressed, and completed without soft-locks
- [ ] Prerequisite chains work correctly (quest B unavailable until quest A is turned in)
- [ ] Quest objective counters increment correctly for kill, collect, and talk types
- [ ] Quest rewards (XP, gold, items) are granted exactly once on turn-in
- [ ] Quest tracker UI updates in real-time as objectives progress

### NPC Pathfinding Check
- [ ] NPCs do not get stuck on terrain geometry
- [ ] NPCs return to spawn point after losing a target
- [ ] NPCs heal to full HP when returning to spawn
- [ ] NPC aggro range does not pull through walls or floors
- [ ] NPCs respawn correctly after death (correct position, full HP, proper delay)

### Security Audit
- [ ] All stat mutations are server-authoritative (no client → server stat writes)
- [ ] Quest completion validated server-side (client cannot claim false objective progress)
- [ ] Zone entry level checks are server-side (client cannot bypass level gates)
- [ ] RemoteEvent payloads validated for type and range on every handler
- [ ] Rate limiting on stat allocation, quest accept, and zone entry remotes

### Data Persistence
- [ ] Player stats save on leave and load on join (use ProfileService/ProfileStore)
- [ ] Quest progress persists across sessions
- [ ] Inventory and gear persist across sessions
- [ ] Graceful handling of DataStore failures (retry with backoff, warn player)

### Performance Validation
- [ ] Server Heartbeat stays under 16ms with 20+ players
- [ ] NPC count per zone stays within budget
- [ ] StreamingEnabled tested on low-end mobile devices
- [ ] No memory leaks from NPC spawn/despawn cycles (check with MicroProfiler)

### Player Experience
- [ ] Tutorial quest teaches core mechanics (move, attack, quest accept, level up)
- [ ] Clear UI indicators for: quest givers, level-gated zones, objectives
- [ ] Death and respawn flow is smooth (no disorientation)
- [ ] Loading screens or zone transitions feel polished
