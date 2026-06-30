# Roblox Sharp Edges — Full Reference

> Every entry here represents a real production footgun that has caused data loss, exploits,
> crashes, or hours of debugging in Roblox games.
>
> **Severity Levels:**
> - **Critical** - Data loss, security breach, or revenue loss. Fix before shipping.
> - **High** - Server instability, degraded experience, or exploit surface. Fix in current sprint.
> - **Medium** - Correctness bugs, performance issues, or dev confusion. Fix before scale.
> - **Low** - Code quality, maintainability, or minor timing issues. Fix when convenient.

---

## SE-1 | Critical | DataStore Data Loss from Session Handling

**See roblox-data → Session Locking and ProfileStore for full details.**

When a player server-hops, the old server may still be saving while the new server loads stale data. ProfileStore handles session locking automatically - only one server owns a player's data at a time. Never use raw DataStoreService for player data without session locking.

---

## SE-2 | Critical | Client-Side Currency Manipulation

**See roblox-networking → Security Hardening for full details.**

Currency and all authoritative game state must live exclusively on the server. Never accept currency amounts from the client. The server computes all transactions internally and pushes display-only updates to the client. This is the single most common exploit in Roblox games.

---

## SE-3 | Critical | ProcessReceipt Mishandling

**See roblox-monetization → ProcessReceipt for full details.**

`MarketplaceService.ProcessReceipt` must return `PurchaseGranted` ONLY after the item is granted AND saved. If you return `PurchaseGranted` before granting, the player loses Robux. If you don't return it, Roblox retries on every join - potentially granting duplicates. Grant first, save second, return third.

---

## SE-4 | High | Memory Leaks from Undisconnected Events

### Problem

Every `:Connect()` returns an `RBXScriptConnection`. If you never `:Disconnect()` it, the connection persists for the script's lifetime - even after the object is destroyed. In per-player systems, memory grows linearly with every player who has ever joined.

### Symptoms

- Server memory climbs steadily over time.
- Server FPS degrades after hours.
- Callbacks fire for players who left.

### Solution

Use the **Trove** module (Sleitnick/RbxUtil, install via Wally) to group connections per-player and clean them all on `PlayerRemoving`:

```luau
local Players = game:GetService("Players")
local Trove = require(game.ReplicatedStorage.Packages.Trove)

local playerTroves: { [Player]: typeof(Trove.new()) } = {}

local function onPlayerAdded(player: Player)
    local trove = Trove.new()
    playerTroves[player] = trove

    trove:Connect(player.CharacterAdded, function(character)
        local humanoid = character:WaitForChild("Humanoid")
        trove:Connect(humanoid.Died, function()
            task.wait(3)
            player:LoadCharacter()
        end)
    end)
end

local function onPlayerRemoving(player: Player)
    local trove = playerTroves[player]
    if trove then
        trove:Clean()
        playerTroves[player] = nil
    end
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)
```

---

## SE-5 | High | RemoteEvent Flooding

### Problem

RemoteEvents have no built-in rate limiting. Exploiters can fire thousands of times per second, flooding the server with DataStore calls, instance creation, or raycasts.

### Solution

Implement per-player, per-remote rate limiting on the server. See **roblox-networking → Rate Limiting** for production patterns.

Minimal inline example:

```luau
local lastFire: { [Player]: number } = {}
local COOLDOWN = 0.1

AttackRemote.OnServerEvent:Connect(function(player: Player, targetId: number)
    local now = os.clock()
    if lastFire[player] and now - lastFire[player] < COOLDOWN then return end
    lastFire[player] = now
    -- process attack
end)
```

---

## SE-6 | High | BindToClose Timeout

**See roblox-data → Best Practices (BindToClose Handler) for full details.**

`game:BindToClose()` gives at most 30 seconds. If using ProfileStore, this is automatic. If using raw DataStore, save all players in parallel with `task.spawn` - sequential saves with 50 players will timeout.

---

## SE-7 | Medium | Part Count on Mobile

Mobile devices struggle above ~10,000 visible parts. Enable **StreamingEnabled** and configure `StreamingMinRadius`/`StreamingTargetRadius`. Use `ModelStreamingMode` to mark distant models as Opportunistic and gameplay-critical models as Persistent.

See **roblox-runtime → StreamingEnabled** for configuration details.

---

## SE-8 | Medium | Yielding in Module Require

### Problem

`require()` executes the module body synchronously. If it yields (`WaitForChild`, `task.wait`, HTTP), every script requiring that module blocks. Two modules requiring each other with yields = deadlock.

### Solution

Never yield in a module body. Use Init/Start lifecycle:

```luau
local CombatSystem = {}

function CombatSystem:Init()
    -- WaitForChild is safe here (called by bootstrap, not during require)
    self._remotes = game.ReplicatedStorage:WaitForChild("Remotes", 10)
end

function CombatSystem:Start()
    -- Connect events after all modules are Init'd
end

return CombatSystem
```

Bootstrap script calls `:Init()` on all modules, then `:Start()` on all modules.

---

## SE-9 | Medium | Table Length with Nil Gaps

### Problem

`#` is only reliable for sequence tables (consecutive integer keys, no nil gaps). Setting `tbl[3] = nil` creates a hole; `#tbl` may return any valid boundary.

### Solution

- Never set array elements to `nil`. Use `table.remove()` to shift elements.
- Use generalized iteration (`for _, v in tbl do`) instead of `for i = 1, #tbl`.
- For sparse data, use dictionary keys instead of integer indices.

---

## SE-10 | Low | Deprecated wait()/spawn()/delay()

**See roblox-luau-patterns → Task Library for full details.**

Replace `wait()` → `task.wait()`, `spawn()` → `task.spawn()`, `delay()` → `task.delay()`. Legacy functions have minimum yield issues, unpredictable timing, and swallow errors.

---

## SE-11 | Medium | Infinite Yield Warning

### Problem

`WaitForChild(name)` without a timeout yields forever if the child never appears. Common with renamed instances, StreamingEnabled, or race conditions.

### Solution

Always pass a timeout. Handle `nil` return:

```luau
local folder = ReplicatedStorage:WaitForChild("Weapons", 10)
if not folder then
    warn("[Init] Weapons folder not found after 10s")
    return
end
```

---

## SE-12 | Low | String Patterns vs Regex

### Problem

Luau uses Lua string patterns, not regex. `\d` doesn't work - use `%d`. Escape with `%` not `\`. No alternation (`|`), no non-greedy `*?` (use `-` instead), no lookahead.

### Key Differences

- Digits: `%d` not `\d`
- Word chars: `%w` not `\w`
- Whitespace: `%s` not `\s`
- Escape special chars: `%.` not `\.`
- Non-greedy: `.-` not `.*?`
- Literal `%`: `%%`

---

## SE-13 | Medium | Local Function Declaration Order

### Problem

Luau has no hoisting. A `local function` is invisible to code above its declaration. AI assistants frequently place helper functions below the functions that call them, causing nil-value runtime errors.

### Rule

**Callees above callers. Always.** If `functionA()` calls `helperB()`, then `helperB` must be declared first.

```luau
-- BAD: helperB is nil when functionA runs
local function functionA()
    helperB() -- ERROR: attempt to call a nil value
end

local function helperB()
    print("I'm a helper")
end

-- GOOD: helper declared first
local function helperB()
    print("I'm a helper")
end

local function functionA()
    helperB() -- works
end
```

### When you need mutual recursion

Use forward declaration:

```luau
local functionB -- forward declare
local function functionA()
    functionB()
end
function functionB() -- note: no 'local' (already declared above)
    functionA()
end
```
