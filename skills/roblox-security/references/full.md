# Roblox Security & Anti-Exploit


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

Use this skill when designing security systems, auditing existing code for vulnerabilities, or hardening a game against common exploit vectors.

## Core Principle

**The client is compromised. Always.** Exploiters run arbitrary Luau on the client via injection tools. Every LocalScript, every ReplicatedStorage module, and every client-side value is readable and writable by attackers. The server is the source of truth, but the implementation depends on the authority model.

## Authority Models

### Classic replication

Validate client requests and custom movement against server-owned state. Do not trust client-reported damage, currency, inventory, permissions, or positions. Network ownership is a physics simulation choice, not a complete security boundary.

### Server Authority

Server Authority is an opt-in Roblox model configured through `Workspace.AuthorityMode = Server` and the required replication, fixed-simulation, streaming, and input settings. The server remains authoritative for core gameplay while clients predict input and recover from misprediction through rollback and resimulation.

For Server Authority projects:

- put synchronized simulation logic in `RunService:BindToSimulation()`;
- use the Input Action System for inputs that affect the core simulation;
- do not write simulation-access properties such as `BasePart.CFrame` from a `Heartbeat` handler as a substitute for authoritative simulation;
- keep validation for custom attacks, dashes, teleports, purchases, permissions, and other game-specific actions at the server boundary;
- use `RunService:SetPredictionMode()` only when the game's prediction policy needs explicit control.

See the [Server Authority model](https://create.roblox.com/docs/projects/server-authority) and [advanced techniques](https://create.roblox.com/docs/projects/server-authority/techniques).

## Exploit Vectors & Mitigations

### Movement and physics exploits

| Attack | How it works | Mitigation |
|--------|-------------|------------|
| Speed or fly exploit | Client attempts to control movement outside the game's allowed state | In Server Authority, use the engine's server-authoritative simulation and prediction model. In classic projects, validate custom movement transitions with tolerance for seats, respawns, teleports, and correction. |
| Teleport or noclip | Client requests or produces an impossible game-specific transition | Validate the requested action and the server's state, rather than blindly snapping `CFrame` every frame. Record suspicion and investigate repeated violations instead of punishing one lag spike. |

Do not copy a blanket `Heartbeat` position checker into a Server Authority project. The server already owns the authoritative simulation, and writing simulation-access properties outside the simulation callback can error. If a classic project needs custom movement checks, keep the checker aware of legitimate state transitions and clean all per-player state on `PlayerRemoving`.

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
    if quantity ~= quantity or math.abs(quantity) == math.huge then return false end
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
[ ] The authority model is documented and its required Workspace settings are verified
[ ] All RemoteEvent handlers validate types of EVERY argument
[ ] All RemoteEvent handlers have rate limiting
[ ] DataStore operations use session locking
[ ] No client-side currency/inventory mutations
[ ] MarketplaceService purchases verified via ProcessReceipt
[ ] No sensitive logic in LocalScripts or ReplicatedStorage

HIGH (exploitable if missing):
[ ] Custom movement and action transitions are validated without fighting the selected authority model
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

Even with server authority, add sanity checks for values that should be bounded. These protect custom state and remote arguments; they are not a replacement for the Server Authority simulation model:

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
- **Don't over-validate movement** — too strict = legitimate players get false-flagged on lag spikes, and blanket checks fight Server Authority prediction. Use the selected model's simulation path and tolerate legitimate corrections.
- **Don't rely on client-side anti-cheat** — exploiters disable it first
