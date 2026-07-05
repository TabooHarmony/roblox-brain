# Roblox Security Hardening Reference

## 1. Overview

Load this reference when:

- Building or modifying `RemoteEvent` / `RemoteFunction` handlers
- Handling player input that affects game state
- Designing currency, inventory, or trading systems
- Conducting security reviews of existing game code
- Implementing anti-cheat or anti-exploit measures
- Auditing what data is exposed to clients

Every system that crosses the client-server boundary is an attack surface. This document provides production-ready patterns to harden those surfaces.

---

## 2. The Golden Rule: Never Trust the Client

Exploiters can:

- **Modify any LocalScript** -- injecting code, changing variables, hooking functions.
- **Fire any RemoteEvent with arbitrary arguments** -- types, values, and counts are all attacker-controlled.
- **Speed hack, fly, and teleport** -- the character's physics can be overridden entirely on the client.
- **See all client-accessible code** -- anything in `StarterPlayerScripts`, `StarterGui`, `ReplicatedStorage`, or `ReplicatedFirst` is fully readable.
- **Read and modify any client-side state** -- health displays, cooldown timers, UI flags.
- **Intercept and replay network traffic** -- RemoteSpy tools let exploiters see every remote call and replay or modify them.

**The client is a display layer, not a trusted authority.** It renders the world and collects input. The server decides what actually happens.

A useful mental model: treat every `RemoteEvent:FireServer()` call as if it were an HTTP request from an anonymous stranger on the internet. Validate everything. Assume nothing.

---

## 3. RemoteEvent Validation Patterns

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
    if type(expected) == "function" then
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
    return type(value) == "number"
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

## 4. Server-Authoritative Design

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

    local itemA = invA:FindFirstChild(itemIdA)
    local itemB = invB:FindFirstChild(itemIdB)
    if not itemA or not itemB then
        return false
    end

    -- Session lock to prevent double-grant
    if itemA:GetAttribute("Locked") or itemB:GetAttribute("Locked") then
        return false
    end

    itemA:SetAttribute("Locked", true)
    itemB:SetAttribute("Locked", true)

    -- Perform the swap atomically
    itemA.Parent = invB
    itemB.Parent = invA

    itemA:SetAttribute("Locked", nil)
    itemB:SetAttribute("Locked", nil)

    return true
end
```

---

## 5. Common Exploit Vectors and Defenses

### Speed Hacks

**What exploiters do:** Modify `Humanoid.WalkSpeed` or directly set `HumanoidRootPart.Velocity` on the client.

**Defense:** Server-side movement validation (see Movement Validation above). Compare position deltas over time against the maximum possible speed. Do not rely on reading `Humanoid.WalkSpeed` from the server -- exploiters can desync the client state.

```luau
-- Simple per-heartbeat speed check
local displacement = (currentPos - lastPos).Magnitude
local maxAllowed = MAX_SPEED * deltaTime * 1.5 -- 1.5x tolerance for physics jitter
if displacement > maxAllowed then
    -- Flag violation
end
```

### Fly Hacks

**What exploiters do:** Apply upward `BodyVelocity` or `BodyForce`, or set `HumanoidRootPart.Anchored = false` with custom flight scripts.

**Defense:** Raycast downward from the character to check ground contact. Allow reasonable air time for jumps and falls but flag sustained flight.

```luau
local function isGrounded(character: Model): boolean
    local root = character:FindFirstChild("HumanoidRootPart")
    if not root then
        return false
    end

    local rayOrigin = root.Position
    local rayDirection = Vector3.new(0, -10, 0) -- 10 studs down
    local params = RaycastParams.new()
    params.FilterDescendantsInstances = { character }
    params.FilterType = Enum.RaycastFilterType.Exclude

    local result = workspace:Raycast(rayOrigin, rayDirection, params)
    return result ~= nil
end

-- Track air time per player
local airTime: { [Player]: number } = {}
local MAX_AIR_TIME = 5 -- seconds before flagging

RunService.Heartbeat:Connect(function(dt)
    for _, player in Players:GetPlayers() do
        local character = player.Character
        if not character then continue end

        if isGrounded(character) then
            airTime[player] = 0
        else
            airTime[player] = (airTime[player] or 0) + dt
            if airTime[player] > MAX_AIR_TIME then
                warn(`[FlyDetect] {player.Name}: airborne for {math.floor(airTime[player])}s`)
                -- Take action: teleport to ground, kick, etc.
            end
        end
    end
end)
```

### Teleport Exploits

**What exploiters do:** Set `HumanoidRootPart.CFrame` directly to teleport anywhere.

**Defense:** Track position each heartbeat. If the distance moved in one frame exceeds what is physically possible, flag it.

```luau
local MAX_FRAME_DISTANCE = 100 -- studs (generous for lag spikes)

local function checkTeleport(player: Player, lastPos: Vector3, currentPos: Vector3): boolean
    local distance = (currentPos - lastPos).Magnitude
    if distance > MAX_FRAME_DISTANCE then
        warn(`[TeleportDetect] {player.Name}: moved {math.floor(distance)} studs in one frame`)
        return true -- violation
    end
    return false
end
```

### Currency Manipulation

**What exploiters do:** Fire remotes that add currency, or modify `leaderstats` values (only visible client-side but may confuse poorly written systems).

**Defense:** All currency lives server-side. The client never sends an amount. The server calculates rewards based on verified game events.

```luau
-- Currency is only modified through trusted server functions
local function awardCurrency(player: Player, amount: number, reason: string)
    assert(amount > 0, "Award amount must be positive")
    assert(amount == math.floor(amount), "Award amount must be an integer")
    assert(amount <= 10000, "Suspiciously large award") -- sanity cap

    local gold = player.leaderstats and player.leaderstats:FindFirstChild("Gold")
    if not gold then return end

    gold.Value += amount

    -- Log for auditing
    print(`[Currency] {player.Name} +{amount} gold ({reason})`)
end
```

### Item Duplication

**What exploiters do:** Fire the same reward remote multiple times quickly, exploit race conditions in trades, disconnect mid-transaction.

**Defense:** Session locking and idempotency keys.

```luau
local claimedRewards: { [Player]: { [string]: boolean } } = {}

local function claimReward(player: Player, rewardId: string): boolean
    local claimed = claimedRewards[player]
    if not claimed then
        claimed = {}
        claimedRewards[player] = claimed
    end

    -- Idempotency: already claimed
    if claimed[rewardId] then
        return false
    end

    -- Mark as claimed BEFORE granting (prevents race condition)
    claimed[rewardId] = true

    -- Grant the reward
    local reward = RewardDatabase[rewardId]
    if reward then
        grantItem(player, reward.ItemId)
    end

    return true
end
```

### RemoteSpy

**What exploiters do:** Use tools like RemoteSpy or SimpleSpy to see every `RemoteEvent` and `RemoteFunction` call, learn the API, then fire remotes manually.

**Defense:** You cannot prevent RemoteSpy. Instead:

- Minimize the number of remotes (smaller attack surface).
- Validate every argument on every remote.
- Do not rely on the client calling remotes in a specific order.
- Do not include sensitive data in remote payloads.

### Noclip

**What exploiters do:** Disable collision on their character to walk through walls.

**Defense:** For critical areas (vaults, admin rooms, restricted zones), use server-side boundary checks rather than relying on physical walls.

```luau
local RESTRICTED_ZONE_CENTER = Vector3.new(100, 5, 200)
local RESTRICTED_ZONE_RADIUS = 30

local function isInRestrictedZone(position: Vector3): boolean
    return (position - RESTRICTED_ZONE_CENTER).Magnitude < RESTRICTED_ZONE_RADIUS
end

-- Check periodically
RunService.Heartbeat:Connect(function()
    for _, player in Players:GetPlayers() do
        local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
        if not root then continue end

        if isInRestrictedZone(root.Position) then
            if not player:GetAttribute("HasZoneAccess") then
                -- Teleport them out
                root.CFrame = CFrame.new(RESTRICTED_ZONE_CENTER + Vector3.new(RESTRICTED_ZONE_RADIUS + 5, 0, 0))
                warn(`[Noclip] {player.Name}: entered restricted zone without access`)
            end
        end
    end
end)
```

---

## 6. Data Exposure Prevention

### What NOT to put in ReplicatedStorage

`ReplicatedStorage` is fully readable by every client. Never store:

- **Admin command lists or logic** -- put in `ServerScriptService`
- **Secret keys or API tokens** -- put in `ServerScriptService` or `ServerStorage`
- **Server configuration** (spawn rates, drop tables, economy tuning) -- put in `ServerStorage`
- **Anti-cheat detection logic** -- put in `ServerScriptService`
- **Complete item databases with hidden stats** -- only replicate what the client needs to display

### Safe placement guide

| Content | Location |
|---|---|
| Client UI scripts | `StarterGui` / `StarterPlayerScripts` |
| Shared types/constants (non-sensitive) | `ReplicatedStorage` |
| Remote definitions | `ReplicatedStorage` |
| Server game logic | `ServerScriptService` |
| Server data (configs, databases) | `ServerStorage` |
| Admin tools | `ServerScriptService` / `ServerStorage` |

### Minimize Remote Payloads

```luau
-- BAD: Sending full player data to everyone
UpdateRemote:FireAllClients({
    name = player.Name,
    gold = player.leaderstats.Gold.Value,
    secretInventory = getFullInventory(player),
    adminLevel = player:GetAttribute("AdminLevel"),
    ipAddress = player:GetAttribute("IP"), -- never do this
})

-- GOOD: Send only what the specific client needs
UpdateRemote:FireClient(player, {
    gold = player.leaderstats.Gold.Value,
})
```

### Never Send Other Players' Private Data

Each client should only receive data about other players that is meant to be public (name, team, visible equipment). Never broadcast:

- Other players' currency balances (unless it is a public leaderboard)
- Other players' inventory contents
- Other players' admin status
- Any internal player IDs or session tokens

---

## 7. Rate Limiting Patterns

### Production-Ready Rate Limiter

```luau
-- ServerScriptService/Modules/RateLimiter.luau

local Players = game:GetService("Players")

local RateLimiter = {}

--[[ Configuration per action ]]
export type RateLimitConfig = {
    maxRequests: number,   -- max requests in the window
    windowSeconds: number, -- time window in seconds
    cooldownSeconds: number?, -- optional cooldown after hitting the limit
    kickAfterViolations: number?, -- kick after this many limit hits (nil = never)
    kickMessage: string?,  -- custom kick message
}

--[[ Internal tracking ]]
type PlayerActionData = {
    timestamps: { number },    -- ring buffer of request timestamps
    violations: number,        -- number of times the player hit the limit
    cooldownUntil: number,     -- os.clock() when cooldown expires
}

local tracking: { [Player]: { [string]: PlayerActionData } } = {}

local DEFAULT_KICK_MESSAGE = "Too many requests. Please try again later."

--[[ -----------------------------------------------------------------------
    Core Rate Limiting
----------------------------------------------------------------------- ]]

function RateLimiter.check(player: Player, action: string, config: RateLimitConfig): boolean
    local now = os.clock()

    -- Initialize player tracking
    if not tracking[player] then
        tracking[player] = {}
    end

    local playerActions = tracking[player]

    if not playerActions[action] then
        playerActions[action] = {
            timestamps = {},
            violations = 0,
            cooldownUntil = 0,
        }
    end

    local data = playerActions[action]

    -- Check if player is in cooldown
    if now < data.cooldownUntil then
        return false
    end

    -- Prune timestamps outside the window
    local windowStart = now - config.windowSeconds
    local pruned = {}
    for _, ts in data.timestamps do
        if ts > windowStart then
            table.insert(pruned, ts)
        end
    end
    data.timestamps = pruned

    -- Check if at the limit
    if #data.timestamps >= config.maxRequests then
        data.violations += 1

        -- Apply cooldown if configured
        if config.cooldownSeconds then
            data.cooldownUntil = now + config.cooldownSeconds
        end

        -- Kick for persistent abuse
        if config.kickAfterViolations and data.violations >= config.kickAfterViolations then
            local message = config.kickMessage or DEFAULT_KICK_MESSAGE
            warn(`[RateLimiter] Kicking {player.Name}: {data.violations} violations on "{action}"`)
            task.defer(function()
                player:Kick(message)
            end)
        else
            warn(`[RateLimiter] {player.Name}: rate limited on "{action}" (violation #{data.violations})`)
        end

        return false
    end

    -- Record this request
    table.insert(data.timestamps, now)
    return true
end

--[[ -----------------------------------------------------------------------
    Flood Detection
    Detects rapid-fire requests that exceed a burst threshold.
----------------------------------------------------------------------- ]]

function RateLimiter.checkBurst(player: Player, action: string, maxBurst: number, burstWindowSeconds: number): boolean
    local now = os.clock()

    if not tracking[player] then
        tracking[player] = {}
    end

    local burstAction = action .. "__burst"
    local playerActions = tracking[player]

    if not playerActions[burstAction] then
        playerActions[burstAction] = {
            timestamps = {},
            violations = 0,
            cooldownUntil = 0,
        }
    end

    local data = playerActions[burstAction]

    -- Prune old timestamps
    local windowStart = now - burstWindowSeconds
    local pruned = {}
    for _, ts in data.timestamps do
        if ts > windowStart then
            table.insert(pruned, ts)
        end
    end
    data.timestamps = pruned

    table.insert(data.timestamps, now)

    if #data.timestamps > maxBurst then
        data.violations += 1
        return false
    end

    return true
end

--[[ -----------------------------------------------------------------------
    Convenience: Wrap a RemoteEvent with rate limiting
----------------------------------------------------------------------- ]]

function RateLimiter.wrapRemote(
    remote: RemoteEvent,
    config: RateLimitConfig,
    handler: (player: Player, ...any) -> ()
)
    remote.OnServerEvent:Connect(function(player: Player, ...: any)
        if not RateLimiter.check(player, remote.Name, config) then
            return
        end

        handler(player, ...)
    end)
end

--[[ -----------------------------------------------------------------------
    Cleanup
----------------------------------------------------------------------- ]]

Players.PlayerRemoving:Connect(function(player)
    tracking[player] = nil
end)

return RateLimiter
```

### Using the Rate Limiter

```luau
local RateLimiter = require(ServerScriptService.Modules.RateLimiter)

-- Simple usage: 10 requests per 5 seconds, kick after 3 violations
RateLimiter.wrapRemote(ShootRemote, {
    maxRequests = 10,
    windowSeconds = 5,
    cooldownSeconds = 2,
    kickAfterViolations = 3,
    kickMessage = "Firing too fast. Disconnected.",
}, function(player, ...)
    -- Handle the shoot action (already rate-limited)
    handleShoot(player, ...)
end)

-- Manual usage with burst detection
ChatRemote.OnServerEvent:Connect(function(player, message)
    -- Standard rate limit: 5 messages per 10 seconds
    if not RateLimiter.check(player, "Chat", {
        maxRequests = 5,
        windowSeconds = 10,
        cooldownSeconds = 5,
        kickAfterViolations = 5,
    }) then
        return
    end

    -- Burst detection: no more than 3 messages in 1 second
    if not RateLimiter.checkBurst(player, "Chat", 3, 1) then
        warn(`[Chat] {player.Name}: burst detected`)
        return
    end

    -- Process message
    processChat(player, message)
end)
```

---

## 8. Obfuscation vs Real Security

**Obfuscation is NOT security.** It is a speed bump, not a wall.

| Approach | What it does | Does it work? |
|---|---|---|
| Obfuscating LocalScripts | Makes code harder to read | No. Deobfuscators exist. Determined exploiters will reverse it. |
| Renaming RemoteEvents to random strings | Makes remotes harder to find | No. RemoteSpy shows the calls regardless of the name. |
| Encrypting remote payloads | Makes payloads harder to read | No. The client must have the decryption key, so the exploiter has it too. |
| Hiding remotes in nested folders | Makes remotes harder to browse | No. `game:GetDescendants()` finds everything. |
| Server-side validation | Rejects invalid requests | **Yes.** This is real security. |

The only security that works is **server-side validation**. The client is enemy territory. Any code running on the client is the exploiter's code. Any data sent from the client is the exploiter's data.

Obfuscation can be used as a minor deterrent against casual script kiddies, but it must never be relied upon. If your game breaks when someone reads your client code, your security model is wrong.

---

## 9. Best Practices

1. **Validate everything server-side.** Every remote argument, every action, every state change.

2. **Minimize remote surface area.** Fewer remotes means fewer attack vectors. Combine related actions into single remotes with action types when practical.

3. **Use sanity checks liberally.** If a value should be between 1 and 100, check it. If a player should be alive, check it. If an item should exist, check it.

4. **Log suspicious activity.** Do not just silently reject bad requests. Log them with the player name and details. Patterns in logs reveal exploit attempts.

5. **Rate limit everything.** Every remote should have a rate limit. No legitimate player fires 100 requests per second.

6. **Use server-side cooldowns.** Client-side cooldowns are cosmetic. The server must enforce timing.

7. **Session-lock items during transactions.** Prevent duplication by marking items as locked before transferring them.

8. **Separate read and write operations.** Clients can request to see data. Clients can request to perform actions. These should be different remotes with different validation.

9. **Keep server code in ServerScriptService/ServerStorage.** Never let game logic leak to the client.

10. **Test with exploit tools.** Use RemoteSpy on your own game (in Studio or a test place) to see what an exploiter sees. Fire bad data at your remotes and verify they reject it.

---

## 10. Anti-Patterns

### Trusting Client Positions

```luau
-- BAD: Client tells server where they are
MoveRemote.OnServerEvent:Connect(function(player, position)
    player.Character.HumanoidRootPart.CFrame = CFrame.new(position)
end)

-- GOOD: Server reads position from the character directly
-- and validates it against expected movement speed
```

### Client-Side Currency

```luau
-- BAD: Client sends amount to add
AddGoldRemote.OnServerEvent:Connect(function(player, amount)
    player.leaderstats.Gold.Value += amount
end)

-- GOOD: Server determines reward based on game event
local function onEnemyKilled(player, enemyType)
    local reward = EnemyRewards[enemyType]
    if reward then
        player.leaderstats.Gold.Value += reward
    end
end
```

### Unvalidated Remote Arguments

```luau
-- BAD: No validation at all
EquipRemote.OnServerEvent:Connect(function(player, itemName)
    equipItem(player, itemName)
end)

-- GOOD: Full validation chain
EquipRemote.OnServerEvent:Connect(function(player, itemName)
    if typeof(itemName) ~= "string" then return end
    if #itemName > 100 then return end -- sanity check
    if not Validator.playerOwnsItem(player, itemName) then return end
    if not Validator.checkCooldown(player, "Equip", 0.5) then return end
    equipItem(player, itemName)
end)
```

### Exposing Admin Remotes

```luau
-- BAD: Admin remote in ReplicatedStorage with client-side check
-- (exploiter just fires it directly, bypassing the UI check)
AdminKickRemote.OnServerEvent:Connect(function(player, targetName)
    local target = Players:FindFirstChild(targetName)
    if target then
        target:Kick("Kicked by admin")
    end
end)

-- GOOD: Admin remote with server-side authorization
AdminKickRemote.OnServerEvent:Connect(function(player, targetName)
    if not ADMIN_LIST[player.UserId] then
        warn(`[Admin] Unauthorized admin attempt by {player.Name} ({player.UserId})`)
        return
    end
    if typeof(targetName) ~= "string" then return end
    local target = Players:FindFirstChild(targetName)
    if target then
        target:Kick("Kicked by admin")
    end
end)
```

### Security Through Obscurity

```luau
-- BAD: "They'll never guess the remote name"
local remote = Instance.new("RemoteEvent")
remote.Name = "x7f2k9_internal_do_not_use"
remote.Parent = ReplicatedStorage

-- This is not security. RemoteSpy reveals it instantly.
-- The name does not matter. The validation does.
```

---

## Quick Checklist

Before shipping any remote-connected feature, verify:

- [ ] All arguments are type-checked with `typeof()`
- [ ] All numeric values are range-checked (including NaN: `value == value`)
- [ ] A server-side cooldown prevents rapid firing
- [ ] The player is authorized to perform the action
- [ ] The target/object exists before operating on it
- [ ] The server calculates outcomes (damage, rewards, prices) -- never the client
- [ ] No sensitive data is exposed in `ReplicatedStorage` or remote payloads
- [ ] Rate limiting is in place
- [ ] Suspicious activity is logged with player identification
- [ ] Extra arguments beyond the schema are rejected
