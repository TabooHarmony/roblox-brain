---
name: roblox-networking
description: >
  Server-authoritative networking, RemoteEvent validation, rate limiting, exploit prevention,
  security hardening.
last_reviewed: 2026-05-22
---

<!-- Source: brockmartin/roblox-game-skill (MIT) -->

# Roblox Networking & Security Reference

---

## Overview

**Load this reference when:**

- Validating RemoteEvent/RemoteFunction input on the server
- Implementing rate limiting or anti-exploit measures
- Designing server-authoritative systems (damage, currency, inventory)
- Hardening existing networking code against exploiters

This document covers server-side validation, rate limiting, suspicion scoring, and server-authoritative design patterns. For player lifecycle (PlayerAdded/Removing), see **roblox-architecture**.

---

## Quick Reference

**Load Full Reference below only when you need specific validation module code or rate limiting implementations.**

Key rules:
- NEVER trust the client. Every RemoteEvent arg is attacker-controlled.
- Validate: type, range, ownership, cooldown on EVERY server handler.
- Server-authoritative: server decides outcomes. Client is display-only.
- Rate limit all remotes. Per-player cooldown table minimum.
- Damage: server calculates from weapon stats + distance + cooldown. Never accept damage values from client.
- Currency: all math server-side. Client displays only.
- Movement: validate distance/speed against physics. Flag teleportation.
- Use `t` library for composable type checks on remote args.
- Suspicion scoring: accumulate violations, kick/ban at threshold. Don't instant-kick on first offense.
- Exploiters can: fire any remote, read all client code, modify any client state, speed/fly/teleport.

---

## Full Reference

## Security Hardening

### Never Trust the Client

Every RemoteEvent payload is attacker-controlled. Validate type, range, ownership, and cooldown on the server for every request.

- **Modify any LocalScript** -- injecting code, changing variables, hooking functions.
- **Fire any RemoteEvent with arbitrary arguments** -- types, values, and counts are all attacker-controlled.
- **Speed hack, fly, and teleport** -- the character's physics can be overridden entirely on the client.
- **See all client-accessible code** -- anything in `StarterPlayerScripts`, `StarterGui`, `ReplicatedStorage`, or `ReplicatedFirst` is fully readable.
- **Read and modify any client-side state** -- health displays, cooldown timers, UI flags.
- **Intercept and replay network traffic** -- RemoteSpy tools let exploiters see every remote call and replay or modify them.

**The client is a display layer, not a trusted authority.** It renders the world and collects input. The server decides what actually happens.

A useful mental model: treat every `RemoteEvent:FireServer()` call as if it were an HTTP request from an anonymous stranger on the internet. Validate everything. Assume nothing.

---

### RemoteEvent Validation Patterns

> **For runtime type checking, the `t` library is vendored** at `vendor/t/t.lua` (osyrisrblx/t v3.1.1, MIT). It provides composable type checks (`t.string`, `t.number`, `t.interface({...})`) that are cleaner than manual typeof() chains. The agent can place it when relevant.

### The Problem

A bare remote handler like this is exploitable:

```luau
-- BAD: No validation at all
DamageRemote.OnServerEvent:Connect(function(player, targetName, damage)
    local target = Players:FindFirstChild(targetName)
    target.Character.Humanoid:TakeDamage(damage)
end)
```

An exploiter can fire this with any target name and any damage value, instantly killing anyone.

### Production-Ready Validation Module

Place this in `ServerScriptService`:

```luau
-- ServerScriptService/Modules/RemoteValidator.luau

local RemoteValidator = {}

--[[ -----------------------------------------------------------------------
    Type Checking
    Validates that arguments match expected types.
----------------------------------------------------------------------- ]]

type TypeSpec = string | (value: any) -> boolean

function RemoteValidator.checkType(value: any, expected: TypeSpec): boolean
    if typeof(expected) == "function" then
        return expected(value)
    end
    return typeof(value) == expected
end

function RemoteValidator.validateArgs(
    args: { any },
    schema: { { name: string, type: TypeSpec, optional: boolean? } }
): (boolean, string?)
    for i, spec in schema do
        local value = args[i]

        if value == nil then
            if not spec.optional then
                return false, `Missing required argument: {spec.name}`
            end
            continue
        end

        if not RemoteValidator.checkType(value, spec.type) then
            return false, `Invalid type for {spec.name}: expected {tostring(spec.type)}, got {typeof(value)}`
        end
    end

    -- Reject extra arguments that were not declared in the schema
    if #args > #schema then
        return false, `Too many arguments: expected {#schema}, got {#args}`
    end

    return true, nil
end

--[[ -----------------------------------------------------------------------
    Range Checking
    Validates that numeric values fall within acceptable bounds.
----------------------------------------------------------------------- ]]

function RemoteValidator.checkRange(value: number, min: number, max: number): boolean
    return typeof(value) == "number"
        and value == value -- NaN check
        and value >= min
        and value <= max
end

function RemoteValidator.checkIntegerRange(value: number, min: number, max: number): boolean
    return RemoteValidator.checkRange(value, min, max)
        and math.floor(value) == value
end

--[[ -----------------------------------------------------------------------
    Cooldown Tracking
    Per-player, per-action cooldown enforcement.
----------------------------------------------------------------------- ]]

local cooldowns: { [Player]: { [string]: number } } = {}

function RemoteValidator.checkCooldown(player: Player, action: string, cooldownSeconds: number): boolean
    local now = os.clock()
    local playerCooldowns = cooldowns[player]

    if not playerCooldowns then
        playerCooldowns = {}
        cooldowns[player] = playerCooldowns
    end

    local lastUsed = playerCooldowns[action]
    if lastUsed and (now - lastUsed) < cooldownSeconds then
        return false
    end

    playerCooldowns[action] = now
    return true
end

function RemoteValidator.clearPlayerCooldowns(player: Player)
    cooldowns[player] = nil
end

--[[ -----------------------------------------------------------------------
    Existence Checks
    Validates that targets, objects, and instances actually exist.
----------------------------------------------------------------------- ]]

function RemoteValidator.playerExists(playerName: string): Player?
    local Players = game:GetService("Players")
    return Players:FindFirstChild(playerName) :: Player?
end

function RemoteValidator.characterAlive(player: Player): boolean
    local character = player.Character
    if not character then
        return false
    end

    local humanoid = character:FindFirstChildOfClass("Humanoid")
    if not humanoid then
        return false
    end

    return humanoid.Health > 0
end

function RemoteValidator.instanceExists(parent: Instance, name: string, className: string?): Instance?
    local child = parent:FindFirstChild(name)
    if not child then
        return nil
    end

    if className and not child:IsA(className) then
        return nil
    end

    return child
end

--[[ -----------------------------------------------------------------------
    Authorization
    Checks if a player is allowed to perform an action.
----------------------------------------------------------------------- ]]

function RemoteValidator.playerOwnsItem(player: Player, itemId: string, inventoryFolder: Folder?): boolean
    local folder = inventoryFolder or player:FindFirstChild("Inventory") :: Folder?
    if not folder then
        return false
    end

    return folder:FindFirstChild(itemId) ~= nil
end

function RemoteValidator.playerHasAttribute(player: Player, attribute: string, expectedValue: any?): boolean
    local value = player:GetAttribute(attribute)
    if expectedValue ~= nil then
        return value == expectedValue
    end
    return value ~= nil
end

--[[ -----------------------------------------------------------------------
    Distance Check
    Validates that two positions are within an acceptable range.
----------------------------------------------------------------------- ]]

function RemoteValidator.withinRange(posA: Vector3, posB: Vector3, maxDistance: number): boolean
    return (posA - posB).Magnitude <= maxDistance
end

function RemoteValidator.playerWithinRange(player: Player, targetPos: Vector3, maxDistance: number): boolean
    local character = player.Character
    if not character then
        return false
    end

    local root = character:FindFirstChild("HumanoidRootPart")
    if not root then
        return false
    end

    return RemoteValidator.withinRange(root.Position, targetPos, maxDistance)
end

--[[ -----------------------------------------------------------------------
    Cleanup
----------------------------------------------------------------------- ]]

game:GetService("Players").PlayerRemoving:Connect(function(player)
    RemoteValidator.clearPlayerCooldowns(player)
end)

return RemoteValidator
```

### Using the Validation Module

```luau
-- ServerScriptService/RemoteHandlers/DamageHandler.server.luau

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Validator = require(ServerScriptService.Modules.RemoteValidator)
local DamageRemote = ReplicatedStorage.Remotes.DealDamage

local MAX_DAMAGE = 50
local DAMAGE_COOLDOWN = 0.5 -- seconds
local ATTACK_RANGE = 15    -- studs

local ARG_SCHEMA = {
    { name = "targetPlayer", type = "Instance" },
    { name = "damage",       type = "number" },
}

DamageRemote.OnServerEvent:Connect(function(player: Player, ...: any)
    local args = { ... }

    -- 1. Validate argument types
    local valid, err = Validator.validateArgs(args, ARG_SCHEMA)
    if not valid then
        warn(`[DamageHandler] {player.Name}: {err}`)
        return
    end

    local targetPlayer: Player = args[1]
    local damage: number = args[2]

    -- 2. Validate the target is actually a Player
    if not targetPlayer:IsA("Player") then
        return
    end

    -- 3. Validate damage range
    if not Validator.checkIntegerRange(damage, 1, MAX_DAMAGE) then
        warn(`[DamageHandler] {player.Name}: damage out of range ({damage})`)
        return
    end

    -- 4. Cooldown check
    if not Validator.checkCooldown(player, "DealDamage", DAMAGE_COOLDOWN) then
        return
    end

    -- 5. Verify attacker is alive
    if not Validator.characterAlive(player) then
        return
    end

    -- 6. Verify target is alive
    if not Validator.characterAlive(targetPlayer) then
        return
    end

    -- 7. Range check -- attacker must be near the target
    local targetRoot = targetPlayer.Character and targetPlayer.Character:FindFirstChild("HumanoidRootPart")
    if not targetRoot then
        return
    end

    if not Validator.playerWithinRange(player, targetRoot.Position, ATTACK_RANGE) then
        warn(`[DamageHandler] {player.Name}: target out of range`)
        return
    end

    -- 8. Authorization -- verify the player has a weapon equipped
    local character = player.Character
    local weapon = character and character:FindFirstChildOfClass("Tool")
    if not weapon or not weapon:GetAttribute("CanDealDamage") then
        warn(`[DamageHandler] {player.Name}: no valid weapon equipped`)
        return
    end

    -- 9. Server calculates actual damage (never trust client damage value directly)
    local serverDamage = math.min(damage, weapon:GetAttribute("MaxDamage") or MAX_DAMAGE)

    -- 10. Apply damage
    local targetHumanoid = targetPlayer.Character:FindFirstChildOfClass("Humanoid")
    if targetHumanoid then
        targetHumanoid:TakeDamage(serverDamage)
    end
end)
```

---

### Server-Authoritative Design

The server owns all game state. The client requests actions; the server decides outcomes.

### Movement Validation

```luau
-- ServerScriptService/Security/MovementValidator.server.luau

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local MAX_SPEED = 50             -- studs per second (walk + sprint + tolerance)
local MAX_VERTICAL_SPEED = 100   -- studs per second (jumping/falling tolerance)
local VIOLATION_THRESHOLD = 5    -- strikes before action
local CHECK_INTERVAL = 0.5       -- seconds between checks

local playerData: { [Player]: {
    lastPosition: Vector3,
    lastCheck: number,
    violations: number,
} } = {}

Players.PlayerAdded:Connect(function(player)
    player.CharacterAdded:Connect(function(character)
        local root = character:WaitForChild("HumanoidRootPart")
        playerData[player] = {
            lastPosition = root.Position,
            lastCheck = os.clock(),
            violations = 0,
        }
    end)
end)

Players.PlayerRemoving:Connect(function(player)
    playerData[player] = nil
end)

RunService.Heartbeat:Connect(function()
    local now = os.clock()

    for player, data in playerData do
        if (now - data.lastCheck) < CHECK_INTERVAL then
            continue
        end

        local character = player.Character
        if not character then
            continue
        end

        local root = character:FindFirstChild("HumanoidRootPart")
        if not root then
            continue
        end

        local dt = now - data.lastCheck
        local displacement = root.Position - data.lastPosition
        local horizontalSpeed = Vector3.new(displacement.X, 0, displacement.Z).Magnitude / dt
        local verticalSpeed = math.abs(displacement.Y) / dt

        if horizontalSpeed > MAX_SPEED or verticalSpeed > MAX_VERTICAL_SPEED then
            data.violations += 1
            warn(`[MovementValidator] {player.Name}: speed violation #{data.violations} (h={math.floor(horizontalSpeed)}, v={math.floor(verticalSpeed)})`)

            if data.violations >= VIOLATION_THRESHOLD then
                -- Teleport player back to last valid position
                root.CFrame = CFrame.new(data.lastPosition)
                -- Or kick for persistent abuse:
                -- player:Kick("Movement anomaly detected.")
            end
        else
            -- Decay violations over time for legitimate edge cases
            data.violations = math.max(0, data.violations - 1)
            data.lastPosition = root.Position
        end

        data.lastCheck = now
    end
end)
```

### Damage Validation

```luau
-- Server decides damage, not the client.

local function calculateDamage(attacker: Player, weapon: Tool, target: Player): number?
    local weaponConfig = WeaponDatabase[weapon.Name]
    if not weaponConfig then
        return nil
    end

    -- Server checks weapon cooldown
    local lastFire = weapon:GetAttribute("LastFired") or 0
    if os.clock() - lastFire < weaponConfig.Cooldown then
        return nil
    end

    -- Server checks range
    local attackerRoot = attacker.Character and attacker.Character:FindFirstChild("HumanoidRootPart")
    local targetRoot = target.Character and target.Character:FindFirstChild("HumanoidRootPart")
    if not attackerRoot or not targetRoot then
        return nil
    end

    local distance = (attackerRoot.Position - targetRoot.Position).Magnitude
    if distance > weaponConfig.Range then
        return nil
    end

    -- Server calculates damage
    weapon:SetAttribute("LastFired", os.clock())
    return weaponConfig.BaseDamage
end
```

### Currency Transactions

```luau
-- WRONG: Client tells server how much to add
CurrencyRemote.OnServerEvent:Connect(function(player, amount)
    player.leaderstats.Gold.Value += amount -- exploiter sends 999999
end)

-- RIGHT: Server calculates the reward
QuestCompleteRemote.OnServerEvent:Connect(function(player, questId)
    -- Validate quest ID type
    if typeof(questId) ~= "string" then
        return
    end

    -- Server checks quest state
    local questData = PlayerQuestData[player]
    if not questData or not questData[questId] then
        return
    end

    if questData[questId].completed then
        return -- already claimed
    end

    -- Server looks up the reward from its own data
    local questConfig = QuestDatabase[questId]
    if not questConfig then
        return
    end

    -- Server awards the reward
    questData[questId].completed = true
    player.leaderstats.Gold.Value += questConfig.Reward
end)
```

### Inventory Operations

```luau
-- Server-side trade validation
local function executeTrade(playerA: Player, playerB: Player, itemIdA: string, itemIdB: string): boolean
    -- Both players must be alive and in range
    if not Validator.characterAlive(playerA) or not Validator.characterAlive(playerB) then
        return false
    end

    -- Verify ownership on the server
    local invA = playerA:FindFirstChild("Inventory")
    local invB = playerB:FindFirstChild("Inventory")
    if not invA or not invB then
        return false
    end

---

## Rate Limiting

Roblox's built-in throttle (~500 req/sec per client) is NOT a substitute for custom rate limiting. Players can still spam remotes at hundreds of requests per second. You need application-level throttling.

### Pattern 1: Per-Player Cooldown Table

Simple and effective for most games. Each remote has a minimum time between calls per player.

```luau
local cooldowns: {[Player]: {[string]: number}} = {}
local COOLDOWN = 0.2 -- seconds between calls

local function isThrottled(player: Player, remoteName: string): boolean
    local now = os.clock()
    if not cooldowns[player] then
        cooldowns[player] = {}
    end

    local lastCall = cooldowns[player][remoteName]
    if lastCall and (now - lastCall) < COOLDOWN then
        return true -- throttled
    end

    cooldowns[player][remoteName] = now
    return false
end

-- Clean up when player leaves
Players.PlayerRemoving:Connect(function(player)
    cooldowns[player] = nil
end)

-- Usage
BuyItem.OnServerEvent:Connect(function(player, itemId)
    if isThrottled(player, "BuyItem") then return end
    -- process purchase
end)
```

### Pattern 2: Declarative Remote Definitions

Define all remotes in one place with rate limits, validation, and allowed states. Cleaner than scattered OnServerEvent handlers.

```luau
type RemoteDef = {
    RateLimit: number?,
    Validate: (Player, ...any) -> boolean,
    Handler: (Player, ...any) -> (),
}

local Remotes: {[string]: RemoteDef} = {
    BuyItem = {
        RateLimit = 0.5,
        Validate = function(player, itemId)
            return typeof(itemId) == "string" and #itemId < 50
        end,
        Handler = function(player, itemId)
            -- process purchase
        end,
    },
    EquipTool = {
        RateLimit = 0.3,
        Validate = function(player, toolId)
            return typeof(toolId) == "string"
        end,
        Handler = function(player, toolId)
            -- equip tool
        end,
    },
}

-- Wire up automatically
for name, def in Remotes do
    local remote = ReplicatedStorage:WaitForChild(name)
    remote.OnServerEvent:Connect(function(player, ...)
        if def.RateLimit and isThrottled(player, name) then return end
        if not def.Validate(player, ...) then return end
        def.Handler(player, ...)
    end)
end
```

### Pattern 3: Suspicion Scoring

For high-stakes games. Track suspicious behavior over time instead of hard-blocking.

```luau
local suspicion: {[Player]: number} = {}
local SUSPICION_THRESHOLD = 10
local DECAY_RATE = 1 -- points lost per second

local function addSuspicion(player: Player, amount: number, reason: string)
    suspicion[player] = (suspicion[player] or 0) + amount
    if suspicion[player] >= SUSPICION_THRESHOLD then
        warn(`High suspicion for {player.Name}: {reason}`)
    end
end

-- In remote handler
BuyItem.OnServerEvent:Connect(function(player, itemId)
    if isThrottled(player, "BuyItem") then
        addSuspicion(player, 2, "rate limit exceeded")
        return
    end
    -- normal processing
end)

-- Decay suspicion over time
task.spawn(function()
    while true do
        task.wait(1)
        for player, score in suspicion do
            suspicion[player] = math.max(0, score - DECAY_RATE)
        end
    end
end)
```

### What NOT to Do

```luau
-- BAD: no rate limiting at all
BuyItem.OnServerEvent:Connect(function(player, itemId)
    -- exploiter can call this 1000 times/second
    grantItem(player, itemId)
end)

-- BAD: client-side rate limiting (exploiter bypasses)
-- Rate limiting MUST be server-side
```

Source: Roblox Server-Side Detection Guide (Roblox/creator-docs, MIT), DevForum rate limiting patterns
