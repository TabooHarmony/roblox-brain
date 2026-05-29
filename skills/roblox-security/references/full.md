# Roblox Security & Anti-Exploit

Use this skill when designing security systems, auditing existing code for vulnerabilities, or hardening a game against common exploit vectors.

## Core Principle

**The client is compromised. Always.** Exploiters run arbitrary Luau on the client via injection tools. Every LocalScript, every ReplicatedStorage module, every client-side value is readable and writable by attackers. The server is the only source of truth.

## Exploit Vectors & Mitigations

### Movement Exploits

| Attack | How it works | Mitigation |
|--------|-------------|------------|
| Speed hack | Client moves faster than WalkSpeed allows | Server-side velocity check per Heartbeat |
| Teleport | Client sets HumanoidRootPart.CFrame directly | Server tracks last valid position, reject jumps > threshold |
| Fly hack | Client removes gravity/collision | Server checks if player is grounded or has valid flight state |
| Noclip | Client passes through CanCollide parts | Server raycasts between positions to detect wall passes |

```luau
-- Server-side movement validation (basic)
local MAX_SPEED = 16 * 1.5 -- WalkSpeed + tolerance
local MAX_TELEPORT = 50 -- studs per check

local lastPositions: {[Player]: Vector3} = {}

game:GetService("RunService").Heartbeat:Connect(function()
    for _, player in Players:GetPlayers() do
        local char = player.Character
        if not char then continue end
        local root = char:FindFirstChild("HumanoidRootPart")
        if not root then continue end

        local pos = root.Position
        local last = lastPositions[player]
        if last then
            local dist = (pos - last).Magnitude
            if dist > MAX_TELEPORT then
                -- Snap back to last valid position
                root.CFrame = CFrame.new(last)
            end
        end
        lastPositions[player] = pos
    end
end)
```

### Remote Exploits

| Attack | How it works | Mitigation |
|--------|-------------|------------|
| Remote spam | Fire remotes at extreme rates | Per-player rate limiter |
| Argument spoofing | Send wrong types/values | Validate every argument type and range |
| Remote sniffing | Read remote names to reverse-engineer API | Doesn't matter if validation is solid |
| Replay attack | Re-fire a valid remote call | Idempotency checks, transaction IDs |

```luau
-- Rate limiter pattern
local rateLimits: {[Player]: {[string]: number}} = {}
local RATE_LIMIT = 10 -- calls per second

local function checkRate(player: Player, remoteName: string): boolean
    local now = os.clock()
    local playerLimits = rateLimits[player]
    if not playerLimits then
        playerLimits = {}
        rateLimits[player] = playerLimits
    end

    local lastCall = playerLimits[remoteName] or 0
    if now - lastCall < 1 / RATE_LIMIT then
        return false -- rate limited
    end
    playerLimits[remoteName] = now
    return true
end

-- Argument validation pattern
local function validatePurchase(player: Player, itemId: unknown, quantity: unknown): boolean
    if typeof(itemId) ~= "string" then return false end
    if typeof(quantity) ~= "number" then return false end
    if quantity ~= math.floor(quantity) then return false end -- must be integer
    if quantity < 1 or quantity > 99 then return false end -- sane range
    if not ITEM_CATALOG[itemId] then return false end -- item must exist
    return true
end
```

### Economy Exploits

| Attack | How it works | Mitigation |
|--------|-------------|------------|
| Item duplication | Race condition in trade/save | Session locking, atomic operations |
| Negative purchase | Send negative quantity to gain items | Validate quantity > 0 server-side |
| Transaction replay | Replay a purchase remote | Unique transaction IDs, check if already processed |
| DataStore rollback | Exploit save timing to duplicate | Session locking with server JobId |

### DataStore Exploits

| Attack | How it works | Mitigation |
|--------|-------------|------------|
| Save spam | Force repeated saves to exhaust budget | Server-controlled save intervals only |
| Session hijack | Fake session to duplicate across servers | Session lock with JobId verification |
| BindToClose skip | Exploit shutdown timing | BindToClose with parallel saves + timeout |

## Security Audit Checklist

Run through this for every game before publish:

```
CRITICAL (game-breaking if missing):
[ ] All game state is server-authoritative
[ ] All RemoteEvent handlers validate types of EVERY argument
[ ] All RemoteEvent handlers have rate limiting
[ ] DataStore operations use session locking
[ ] No client-side currency/inventory mutations
[ ] MarketplaceService purchases verified via ProcessReceipt
[ ] No sensitive logic in LocalScripts or ReplicatedStorage

HIGH (exploitable if missing):
[ ] Player movement is server-validated
[ ] BindToClose saves protected against data loss
[ ] Trading system uses atomic operations
[ ] No trusting client-reported values (damage, position, items)
[ ] RemoteFunction return values not trusted by server

MEDIUM (quality/fairness):
[ ] Cooldowns enforced server-side (not just client UI)
[ ] Leaderboard values computed server-side
[ ] Anti-AFK detection for reward systems
[ ] Chat filter applied (TextService:FilterStringAsync)
```

## Patterns

### Never Trust Client Values

```luau
-- BAD: Client tells server how much damage to deal
DamageRemote.OnServerEvent:Connect(function(player, target, damage)
    target.Humanoid:TakeDamage(damage) -- exploiter sends 999999
end)

-- GOOD: Server computes damage from game state
AttackRemote.OnServerEvent:Connect(function(player, targetId)
    local weapon = getEquippedWeapon(player)
    if not weapon then return end
    local target = resolveTarget(targetId)
    if not target then return end
    if not isInRange(player, target, weapon.Range) then return end
    if not checkCooldown(player, weapon) then return end

    local damage = weapon.BaseDamage * getDamageMultiplier(player)
    target.Humanoid:TakeDamage(damage)
end)
```

### Session Locking

```luau
-- Prevent data duplication across servers
local function acquireSessionLock(player: Player, data): boolean
    local lockKey = "SessionLock_" .. player.UserId
    local currentLock = data:GetMetadata().SessionLock

    if currentLock and currentLock ~= game.JobId then
        -- Another server owns this data
        -- Either wait for expiry or kick
        return false
    end

    data:SetMetadata({SessionLock = game.JobId})
    return true
end
```

### Sanity Checks (Defense in Depth)

Even with server authority, add sanity checks for values that should be bounded:

```luau
-- Clamp values that should never exceed known bounds
local function sanitizePlayerStats(stats)
    stats.Level = math.clamp(stats.Level, 1, MAX_LEVEL)
    stats.Gold = math.max(stats.Gold, 0) -- never negative
    stats.Health = math.clamp(stats.Health, 0, stats.MaxHealth)
    return stats
end
```

## What NOT to Do

- **Don't obfuscate client code** — it doesn't stop exploiters and makes debugging harder
- **Don't use _G for security state** — it's globally readable and writable
- **Don't kick without logging** — you need data to distinguish false positives from real exploits
- **Don't over-validate movement** — too strict = legitimate players get false-flagged on lag spikes. Use tolerance.
- **Don't rely on client-side anti-cheat** — exploiters disable it first
