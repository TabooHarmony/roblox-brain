# Roblox Sharp Edges (Gotchas) Reference

> **Purpose:** Save you from disaster. Every entry here represents a real production footgun
> that has caused data loss, exploits, crashes, or hours of debugging in Roblox games.
>
> **Severity Levels:**
> - **Critical** — Data loss, security breach, or revenue loss. Fix before shipping.
> - **High** — Server instability, degraded experience, or exploit surface. Fix in current sprint.
> - **Medium** — Correctness bugs, performance issues, or dev confusion. Fix before scale.
> - **Low** — Code quality, maintainability, or minor timing issues. Fix when convenient.

---

## Table of Contents

| ID    | Severity | Title                                      |
|-------|----------|--------------------------------------------|
| SE-1  | Critical | DataStore Data Loss from Session Handling  |
| SE-2  | Critical | Client-Side Currency Manipulation          |
| SE-3  | Critical | ProcessReceipt Mishandling                 |
| SE-4  | High     | Memory Leaks from Undisconnected Events    |
| SE-5  | High     | RemoteEvent Flooding                       |
| SE-6  | High     | BindToClose Timeout                        |
| SE-7  | Medium   | Part Count on Mobile                       |
| SE-8  | Medium   | Yielding in Module Require                 |
| SE-9  | Medium   | Table Length with Nil Gaps                  |
| SE-10 | Low      | Deprecated wait()/spawn()/delay()          |
| SE-11 | Medium   | Infinite Yield Warning                     |
| SE-12 | Low      | String Patterns vs Regex                   |

---

## SE-1 | Critical | DataStore Data Loss from Session Handling

### Description

When a player server-hops (teleports between places) or rapidly reconnects, the old server
may still be in the middle of saving their data while the new server loads and reads from
the DataStore. This creates a race condition: the new server reads stale data, the old
server overwrites with its version, or both servers write conflicting data. The result is
permanent data loss — items, currency, and progress silently vanish.

### Symptoms

- Players report lost items or currency after teleporting.
- Data reverts to a previous state after server-hopping.
- Intermittent data loss that is nearly impossible to reproduce locally.
- Bug reports spike after adding teleportation features.

### Solution

Use **ProfileService** (or its successor **ProfileStore**) which implements session locking.
A session lock ensures only one server can own a player's data at a time. The new server
waits for the old server to release the lock before loading. If the old server crashes,
the lock expires after a timeout and the new server claims it.

Never roll your own save/load with raw `DataStoreService` for player data unless you
implement session locking yourself.

### Code Example

```luau
-- ServerScriptService/PlayerDataService.luau
-- Using ProfileService for session-locked player data

local Players = game:GetService("Players")
local ServerScriptService = game:GetService("ServerScriptService")
local ProfileService = require(ServerScriptService.Libs.ProfileService)

local PROFILE_TEMPLATE = {
    Coins = 0,
    Gems = 0,
    Inventory = {},
    Level = 1,
    Experience = 0,
}

local DATASTORE_NAME = "PlayerData_v1"

local ProfileStore = ProfileService.GetProfileStore(DATASTORE_NAME, PROFILE_TEMPLATE)
local Profiles: { [Player]: typeof(ProfileStore:LoadProfileAsync("")) } = {}

local PlayerDataService = {}

function PlayerDataService.getProfile(player: Player)
    return Profiles[player]
end

function PlayerDataService.start()
    local function onPlayerAdded(player: Player)
        -- Session locking happens automatically inside LoadProfileAsync.
        -- If another server holds the lock, this yields until it releases.
        local profile = ProfileStore:LoadProfileAsync(
            "Player_" .. player.UserId,
            "ForceLoad" -- Steal the lock if the other server is unresponsive
        )

        if profile == nil then
            -- Profile could not be loaded (DataStore outage, etc.)
            player:Kick("Unable to load your data. Please rejoin.")
            return
        end

        -- Guard: player may have left while we were loading
        if not player:IsDescendantOf(Players) then
            profile:Release()
            return
        end

        -- If the profile is released (session stolen by another server), kick
        profile:ListenToRelease(function()
            Profiles[player] = nil
            player:Kick("Your data was loaded on another server. Please rejoin.")
        end)

        Profiles[player] = profile
    end

    local function onPlayerRemoving(player: Player)
        local profile = Profiles[player]
        if profile then
            profile:Release() -- Releases session lock AND saves
            Profiles[player] = nil
        end
    end

    Players.PlayerAdded:Connect(onPlayerAdded)
    Players.PlayerRemoving:Connect(onPlayerRemoving)

    -- Handle players already in game (studio edge case)
    for _, player in Players:GetPlayers() do
        task.spawn(onPlayerAdded, player)
    end
end

return PlayerDataService
```

---

## SE-2 | Critical | Client-Side Currency Manipulation

### Description

Any value stored on or transmitted to the client can be read and modified by exploiters.
If your game stores currency in a `NumberValue` inside the player's character, a
`leaderstats` IntValue, or sends the balance via a RemoteEvent for the client to "hold,"
an exploiter can set that value to anything they want. The server then trusts it.

This is the single most common exploit in Roblox games.

### Symptoms

- Players with impossibly high currency (999,999,999 coins after playing for 2 minutes).
- Economy collapse — items that should be rare are owned by everyone.
- Leaderboard entries with absurd values.
- Reports of "hackers" in your game from legitimate players.

### Solution

Currency and all authoritative game state **must live exclusively on the server.** The
client should only receive read-only display values. Never accept currency amounts from
the client. Never let the client tell the server "set my coins to X." Instead, the server
computes all transactions internally and pushes the result to the client for display only.

### Code Example

```luau
-- ServerScriptService/CurrencyService.luau
-- All currency logic is server-authoritative. The client NEVER sends a balance.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlayerDataService = require(script.Parent.PlayerDataService)

-- Remote used ONLY to push display updates to the client
local CurrencyChanged = ReplicatedStorage.Remotes.CurrencyChanged :: RemoteEvent

local CurrencyService = {}

-- Server-only: Add currency. Called by server systems (quests, shops, etc.)
function CurrencyService.addCoins(player: Player, amount: number): boolean
    assert(typeof(amount) == "number", "Amount must be a number")
    assert(amount > 0, "Amount must be positive")
    assert(amount == math.floor(amount), "Amount must be an integer")
    assert(amount <= 1_000_000, "Amount exceeds single-transaction limit")

    local profile = PlayerDataService.getProfile(player)
    if not profile then
        return false
    end

    profile.Data.Coins += amount

    -- Push display update to client (client cannot modify this)
    CurrencyChanged:FireClient(player, "Coins", profile.Data.Coins)
    return true
end

-- Server-only: Spend currency. Returns true if successful, false if insufficient.
function CurrencyService.spendCoins(player: Player, amount: number): boolean
    assert(typeof(amount) == "number", "Amount must be a number")
    assert(amount > 0, "Amount must be positive")
    assert(amount == math.floor(amount), "Amount must be an integer")

    local profile = PlayerDataService.getProfile(player)
    if not profile then
        return false
    end

    if profile.Data.Coins < amount then
        return false -- Insufficient funds
    end

    profile.Data.Coins -= amount
    CurrencyChanged:FireClient(player, "Coins", profile.Data.Coins)
    return true
end

function CurrencyService.getCoins(player: Player): number
    local profile = PlayerDataService.getProfile(player)
    return if profile then profile.Data.Coins else 0
end

return CurrencyService
```

```luau
-- StarterPlayerScripts/CurrencyDisplay.client.luau
-- Client ONLY listens for display updates. It never sends currency data.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local CurrencyChanged = ReplicatedStorage.Remotes.CurrencyChanged :: RemoteEvent

local localPlayer = Players.LocalPlayer
local playerGui = localPlayer:WaitForChild("PlayerGui")

CurrencyChanged.OnClientEvent:Connect(function(currencyName: string, newValue: number)
    -- Update UI display only
    local label = playerGui:FindFirstChild(currencyName .. "Label", true)
    if label and label:IsA("TextLabel") then
        label.Text = tostring(newValue)
    end
end)
```

---

## SE-3 | Critical | ProcessReceipt Mishandling

### Description

`MarketplaceService.ProcessReceipt` is the callback Roblox calls when a player completes a
developer product purchase. If you do not return `Enum.ProductPurchaseDecision.PurchaseGranted`,
Roblox will **retry the callback** on every server the player joins — potentially granting
the item multiple times. If you return `PurchaseGranted` *before* actually granting the item
and the grant fails, the player loses their Robux with nothing to show for it.

This is real-money revenue at stake.

### Symptoms

- Players receive duplicate items from a single purchase.
- Players are charged but never receive their item (Roblox thinks it was granted).
- Purchase receipts pile up and spam the callback on every join.
- Customer support tickets about missing purchases.

### Solution

1. Check if the purchase was already recorded (idempotency).
2. **Grant the item/currency first.**
3. **Save the grant to the DataStore.**
4. Only THEN return `PurchaseGranted`.
5. If anything fails, return `NotProcessedYet` so Roblox retries later.

### Code Example

```luau
-- ServerScriptService/GamepassAndProductHandler.luau

local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")

local PlayerDataService = require(script.Parent.PlayerDataService)
local CurrencyService = require(script.Parent.CurrencyService)

local PRODUCTS = {
    [123456789] = {
        name = "100 Coins",
        grant = function(player: Player): boolean
            return CurrencyService.addCoins(player, 100)
        end,
    },
    [987654321] = {
        name = "500 Coins",
        grant = function(player: Player): boolean
            return CurrencyService.addCoins(player, 500)
        end,
    },
}

local function processReceipt(
    receiptInfo: {
        PlayerId: number,
        ProductId: number,
        PurchaseId: string,
        CurrencySpent: number,
        PlaceIdWherePurchased: number,
    }
): Enum.ProductPurchaseDecision

    -- 1. Find the player in the server
    local player = Players:GetPlayerByUserId(receiptInfo.PlayerId)
    if not player then
        -- Player left; return NotProcessedYet so Roblox retries when they rejoin
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    -- 2. Wait for their profile to load
    local profile = PlayerDataService.getProfile(player)
    if not profile then
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    -- 3. Check idempotency — was this PurchaseId already granted?
    if table.find(profile.Data.ProcessedReceipts, receiptInfo.PurchaseId) then
        -- Already granted; tell Roblox to stop retrying
        return Enum.ProductPurchaseDecision.PurchaseGranted
    end

    -- 4. Look up and execute the grant
    local productConfig = PRODUCTS[receiptInfo.ProductId]
    if not productConfig then
        warn("[ProcessReceipt] Unknown ProductId:", receiptInfo.ProductId)
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    local grantSuccess = productConfig.grant(player)
    if not grantSuccess then
        -- Grant failed (maybe profile released mid-grant); retry later
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    -- 5. Record the PurchaseId so we never double-grant
    table.insert(profile.Data.ProcessedReceipts, receiptInfo.PurchaseId)

    -- Keep the receipts list from growing forever (keep last 100)
    if #profile.Data.ProcessedReceipts > 100 then
        table.remove(profile.Data.ProcessedReceipts, 1)
    end

    -- 6. ONLY NOW tell Roblox the purchase is complete
    return Enum.ProductPurchaseDecision.PurchaseGranted
end

MarketplaceService.ProcessReceipt = processReceipt
```

---

## SE-4 | High | Memory Leaks from Undisconnected Events

### Description

Every call to `:Connect()` on a Roblox event returns an `RBXScriptConnection`. If you do not
store and eventually `:Disconnect()` these connections, they persist for the lifetime of the
script — even if the object the event belongs to is destroyed. In long-running server scripts,
this means connections accumulate over hours, consuming memory and executing stale callbacks
on objects that should be garbage collected.

This is especially dangerous in per-player systems: if you connect events when a player joins
but never disconnect them when the player leaves, memory grows linearly with every player who
has ever been in the server.

### Symptoms

- Server memory usage climbs steadily over time (visible in Developer Console).
- Server FPS degrades after running for several hours.
- Callbacks fire for players who left the game.
- Eventual server crash from out-of-memory.

### Solution

Store every connection and disconnect it during cleanup. Use a **Maid** or **Trove** (Janitor)
pattern to group connections and clean them all at once. For per-player systems, create one
Maid per player and clean it on `PlayerRemoving`.

### Code Example

```luau
-- Shared/Trove.luau (simplified cleanup utility)

local Trove = {}
Trove.__index = Trove

function Trove.new()
    return setmetatable({
        _objects = {},
    }, Trove)
end

-- Add a connection, instance, or cleanup function
function Trove:Add(object: any): any
    table.insert(self._objects, object)
    return object
end

-- Shorthand: connect an event and track the connection
function Trove:Connect(signal: RBXScriptSignal, callback: (...any) -> ()): RBXScriptConnection
    local connection = signal:Connect(callback)
    table.insert(self._objects, connection)
    return connection
end

-- Destroy everything tracked by this Trove
function Trove:Clean()
    for _, object in self._objects do
        if typeof(object) == "RBXScriptConnection" then
            object:Disconnect()
        elseif typeof(object) == "Instance" then
            object:Destroy()
        elseif typeof(object) == "function" then
            object()
        end
    end
    table.clear(self._objects)
end

return Trove
```

```luau
-- ServerScriptService/PlayerSetup.luau
-- Demonstrates per-player cleanup to prevent memory leaks

local Players = game:GetService("Players")
local Trove = require(game.ReplicatedStorage.Shared.Trove)

local playerTroves: { [Player]: typeof(Trove.new()) } = {}

local function onPlayerAdded(player: Player)
    local trove = Trove.new()
    playerTroves[player] = trove

    -- All connections go through the trove
    trove:Connect(player.CharacterAdded, function(character)
        local humanoid = character:WaitForChild("Humanoid")

        -- This connection is ALSO tracked — cleaned when the trove cleans
        trove:Connect(humanoid.Died, function()
            print(player.Name, "died — respawning in 3 seconds")
            task.wait(3)
            player:LoadCharacter()
        end)
    end)

    -- Track created instances too
    local billboard = trove:Add(Instance.new("BillboardGui"))
    billboard.Name = "PlayerLabel"
    billboard.Parent = player.Character and player.Character:FindFirstChild("Head")
end

local function onPlayerRemoving(player: Player)
    local trove = playerTroves[player]
    if trove then
        trove:Clean() -- Disconnects ALL connections, destroys ALL instances
        playerTroves[player] = nil
    end
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)
```

---

## SE-5 | High | RemoteEvent Flooding

### Description

RemoteEvents and RemoteFunctions have no built-in rate limiting. An exploiter can fire a
RemoteEvent thousands of times per second. If your server handler does any nontrivial work
(DataStore calls, instance creation, raycasting), this floods the server and causes lag for
every player. In extreme cases, it crashes the server entirely.

### Symptoms

- Sudden server lag spikes that correlate with a specific player being in the server.
- Server crash logs showing thousands of remote calls per frame.
- Exploiters triggering actions (attacks, item pickups) faster than humanly possible.
- DataStore throttling from excessive save/load calls triggered by remote spam.

### Solution

Implement a per-player, per-remote rate limiter on the server. Drop requests that exceed
the limit. Optionally kick repeat offenders.

### Code Example

```luau
-- ServerScriptService/RateLimiter.luau

local RateLimiter = {}
RateLimiter.__index = RateLimiter

export type Config = {
    maxRequests: number,  -- Max requests allowed in the window
    windowSeconds: number, -- Time window in seconds
    kickAfter: number?,    -- Kick player after this many violations (nil = never)
}

function RateLimiter.new(config: Config)
    return setmetatable({
        _config = config,
        _playerData = {} :: { [Player]: { count: number, windowStart: number, violations: number } },
    }, RateLimiter)
end

function RateLimiter:check(player: Player): boolean
    local now = os.clock()
    local data = self._playerData[player]

    if not data then
        data = { count = 0, windowStart = now, violations = 0 }
        self._playerData[player] = data
    end

    -- Reset window if expired
    if now - data.windowStart >= self._config.windowSeconds then
        data.count = 0
        data.windowStart = now
    end

    data.count += 1

    if data.count > self._config.maxRequests then
        data.violations += 1

        if self._config.kickAfter and data.violations >= self._config.kickAfter then
            player:Kick("Rate limit exceeded.")
        end

        return false -- Request denied
    end

    return true -- Request allowed
end

function RateLimiter:removePlayer(player: Player)
    self._playerData[player] = nil
end

return RateLimiter
```

```luau
-- ServerScriptService/CombatRemotes.luau

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RateLimiter = require(script.Parent.RateLimiter)

local AttackRemote = ReplicatedStorage.Remotes.Attack :: RemoteEvent

-- Allow 10 attack requests per second; kick after 5 violations
local attackLimiter = RateLimiter.new({
    maxRequests = 10,
    windowSeconds = 1,
    kickAfter = 5,
})

AttackRemote.OnServerEvent:Connect(function(player: Player, targetId: number)
    if not attackLimiter:check(player) then
        return -- Silently drop the request
    end

    -- Validate and process the attack (server-authoritative)
    -- ...
end)

Players.PlayerRemoving:Connect(function(player)
    attackLimiter:removePlayer(player)
end)
```

---

## SE-6 | High | BindToClose Timeout

### Description

`game:BindToClose()` gives you **at most 30 seconds** to run cleanup code before Roblox
forcefully shuts down the server. If you save player data sequentially (one player at a time),
and each save takes 1-2 seconds due to DataStore latency, you can only save 15-30 players
before the timeout. In a 50-player server, the rest lose their data.

### Symptoms

- Data loss specifically during server shutdowns (updates, Roblox maintenance).
- No data loss during normal play, only when the server closes.
- Players who were "last" in the save queue lose data more often.
- Studio testing works fine (only 1 player to save).

### Solution

Save all players **in parallel** using `task.spawn`. Do not yield between player saves.
Collect all save threads and wait for them to complete (or hit the 30-second deadline).

### Code Example

```luau
-- ServerScriptService/ShutdownHandler.luau

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local PlayerDataService = require(script.Parent.PlayerDataService)

local IS_STUDIO = RunService:IsStudio()

game:BindToClose(function()
    -- In Studio, BindToClose fires on stop — skip if no real players
    if IS_STUDIO then
        task.wait(1)
        return
    end

    local savingPlayers = Players:GetPlayers()
    if #savingPlayers == 0 then
        return
    end

    -- Save ALL players in parallel
    local completed = 0
    local total = #savingPlayers

    for _, player in savingPlayers do
        task.spawn(function()
            -- ProfileService:Release() handles save + session unlock
            local profile = PlayerDataService.getProfile(player)
            if profile then
                profile:Release()
            end
            completed += 1
        end)
    end

    -- Wait until all saves complete OR we approach the 30s deadline
    local deadline = os.clock() + 27 -- Leave 3s buffer
    while completed < total and os.clock() < deadline do
        task.wait(0.1)
    end

    if completed < total then
        warn(
            string.format(
                "[Shutdown] Saved %d/%d players before timeout!",
                completed,
                total
            )
        )
    else
        print(string.format("[Shutdown] All %d players saved successfully.", total))
    end
end)
```

---

## SE-7 | Medium | Part Count on Mobile

### Description

Mobile devices (especially low-end Android phones and older iPads) have significantly less
GPU and CPU headroom than desktop PCs. A map with 50,000 parts may run at 60 FPS on desktop
but 10 FPS on mobile. Roblox's renderer must process every part for shadows, lighting, and
physics. Exceeding roughly 10,000 visible parts on mobile causes frame drops, overheating,
and crashes.

### Symptoms

- Good FPS on desktop/console, unplayable on phones.
- Mobile crash reports with no obvious scripting error.
- Players on mobile complain about lag in specific areas of the map.
- Battery drain reports from mobile players.

### Solution

- Keep visible part count under **10,000** for mobile targets.
- Enable **StreamingEnabled** to only load geometry near the player.
- Use **MeshPart** and **unions** to reduce draw calls.
- Configure **LOD** (Level of Detail) for distant objects.
- Use the **MicroProfiler** to identify rendering bottlenecks.

### Code Example

```luau
-- Workspace configuration (set via Properties or a setup script)

-- Enable StreamingEnabled on Workspace
local Workspace = game:GetService("Workspace")

-- StreamingEnabled must be set before the game starts (in Studio properties)
-- These properties control streaming behavior at runtime:
Workspace.StreamingMinRadius = 128   -- Always load parts within 128 studs
Workspace.StreamingTargetRadius = 256 -- Try to load parts within 256 studs
Workspace.StreamingPauseMode = Enum.StreamingPauseMode.ClientPhysicsPause

-- ModelStreamingMode on individual models controls their streaming behavior:
-- Example: Mark a distant mountain as "Opportunistic" so it unloads aggressively
local distantMountain = Workspace:FindFirstChild("DistantMountain")
if distantMountain and distantMountain:IsA("Model") then
    distantMountain.ModelStreamingMode = Enum.ModelStreamingMode.Opportunistic
end

-- Mark important gameplay models as "Persistent" so they never unload
local spawnArea = Workspace:FindFirstChild("SpawnArea")
if spawnArea and spawnArea:IsA("Model") then
    spawnArea.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
end

-- LOD via RenderFidelity on MeshParts
-- Automatic: Roblox picks LOD based on distance (recommended)
-- Performance: Always use lowest LOD
-- Precise: Always use highest LOD
for _, meshPart in Workspace:GetDescendants() do
    if meshPart:IsA("MeshPart") then
        meshPart.RenderFidelity = Enum.RenderFidelity.Automatic
    end
end
```

---

## SE-8 | Medium | Yielding in Module Require

### Description

When you `require()` a ModuleScript, Luau executes the module body **synchronously** on the
requiring thread. If the module body contains a yielding call (`WaitForChild`, `task.wait`,
an HTTP request, etc.), **every script that requires this module blocks** until the yield
resolves. If two modules require each other and both yield, you get a deadlock. If the yield
never resolves (e.g., `WaitForChild` on a nonexistent child), the game never loads.

### Symptoms

- Game takes abnormally long to start.
- Scripts appear to hang during loading with no errors.
- Adding a new `require()` to a module causes unrelated scripts to break.
- Circular dependency deadlocks that are extremely hard to debug.

### Solution

**Never yield in a module's body.** The module body should only define functions and return
a table. Use an explicit `:Init()` and `:Start()` lifecycle pattern. A bootstrap script
calls `Init()` on all modules first (for setup), then `Start()` on all modules (for runtime
logic that may depend on other modules being initialized).

### Code Example

```luau
-- WRONG: Yielding in module body
-- local MyModule = {}
-- local someInstance = workspace:WaitForChild("ImportantThing") -- BLOCKS ALL REQUIRERS
-- function MyModule.doSomething()
--     return someInstance.Name
-- end
-- return MyModule

-- CORRECT: No yields in module body; use Init/Start pattern
-- ReplicatedStorage/Shared/CombatSystem.luau

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CombatSystem = {}

local weaponConfig: Folder? = nil
local remotes: Folder? = nil

-- Init: called first, safe to reference other modules but DO NOT start gameplay logic
function CombatSystem:Init()
    -- WaitForChild is fine here because Init is called by the bootstrap,
    -- not during require()
    weaponConfig = ReplicatedStorage:WaitForChild("WeaponConfig", 10)
    remotes = ReplicatedStorage:WaitForChild("Remotes", 10)

    if not weaponConfig then
        error("[CombatSystem] WeaponConfig folder not found!")
    end
end

-- Start: called after ALL modules have Init'd. Safe to connect events and run logic.
function CombatSystem:Start()
    if remotes then
        local attackRemote = remotes:FindFirstChild("Attack")
        if attackRemote and attackRemote:IsA("RemoteEvent") then
            attackRemote.OnServerEvent:Connect(function(player, ...)
                CombatSystem:_handleAttack(player, ...)
            end)
        end
    end
end

function CombatSystem:_handleAttack(player: Player, targetId: number)
    -- Combat logic here
end

return CombatSystem
```

```luau
-- ServerScriptService/Bootstrap.server.luau
-- Orchestrates module initialization in the correct order

local modules = {
    require(script.Parent.Services.PlayerDataService),
    require(script.Parent.Services.CurrencyService),
    require(script.Parent.Services.CombatSystem),
    require(script.Parent.Services.ShopService),
}

-- Phase 1: Init all modules (order-independent setup)
for _, mod in modules do
    if mod.Init then
        mod:Init()
    end
end

-- Phase 2: Start all modules (gameplay logic, event connections)
for _, mod in modules do
    if mod.Start then
        mod:Start()
    end
end

print("[Bootstrap] All systems initialized and started.")
```

---

## SE-9 | Medium | Table Length with Nil Gaps

### Description

The `#` (length) operator in Luau is only reliable for **sequence tables** — arrays with
consecutive integer keys starting at 1 and no `nil` gaps. If you remove an element by setting
it to `nil` (e.g., `myTable[3] = nil`), the table now has a hole. The `#` operator may return
any valid boundary — it could return 2, or 5, or any index where `t[n] ~= nil` and
`t[n+1] == nil`. This is not a bug; it is defined behavior that catches many developers off
guard.

### Symptoms

- `for i = 1, #tbl` skips elements or processes fewer than expected.
- Inventory displays missing items that exist in the data.
- Random off-by-one errors that seem to "fix themselves" after a while.
- Different behavior on different servers for the same data.

### Solution

- **Never set array elements to `nil`.** Use `table.remove()` to shift elements down.
- Use `ipairs()` for ordered iteration — it stops at the first `nil`.
- If you need sparse data, use a dictionary (string keys) and iterate with `pairs()`.
- Track array length explicitly if you must use sparse arrays.

### Code Example

```luau
-- DANGEROUS: Using # on a table with nil gaps
local inventory = { "Sword", "Shield", nil, "Potion", "Bow" }
print(#inventory) -- Could print 2 or 5 — UNRELIABLE

-- SAFE PATTERN 1: Use table.remove instead of setting nil
local items = { "Sword", "Shield", "Helmet", "Potion" }
-- Remove "Helmet" (index 3) — shifts "Potion" down to index 3
table.remove(items, 3)
print(#items) -- Reliably prints 3: { "Sword", "Shield", "Potion" }

-- SAFE PATTERN 2: Use ipairs for iteration (stops at first nil)
local data = { 10, 20, nil, 40 }
local sum = 0
for _, value in ipairs(data) do
    sum += value -- Only adds 10 + 20 = 30; stops before nil
end

-- SAFE PATTERN 3: Use a dictionary for sparse data
local equippedSlots: { [string]: string } = {
    Head = "Crown",
    -- Chest is intentionally empty (key absent, not nil)
    Legs = "Iron Greaves",
    Feet = "Boots",
}

for slot, item in equippedSlots do
    print(slot, item) -- Iterates all entries; no nil confusion
end

-- SAFE PATTERN 4: Track length explicitly for sparse arrays
local SparseArray = {}
SparseArray.__index = SparseArray

function SparseArray.new()
    return setmetatable({ _data = {}, _length = 0 }, SparseArray)
end

function SparseArray:push(value: any)
    self._length += 1
    self._data[self._length] = value
end

function SparseArray:removeAt(index: number)
    -- Swap with last element to avoid shifting
    self._data[index] = self._data[self._length]
    self._data[self._length] = nil
    self._length -= 1
end

function SparseArray:length(): number
    return self._length -- Always accurate
end
```

---

## SE-10 | Low | Deprecated wait()/spawn()/delay()

### Description

The legacy global functions `wait()`, `spawn()`, and `delay()` have been deprecated in favor
of the `task` library. The old functions have significant problems:

- `wait()` has a **minimum yield of ~0.03 seconds** regardless of the argument. `wait(0)` does
  not resume next frame — it waits at least 1-2 frames.
- `spawn()` defers execution to a **later resumption cycle** with unpredictable timing, and
  errors in spawned threads are swallowed silently.
- `delay()` has the same timing imprecision as `wait()`, compounding the delay.

The `task` library replacements are faster, more predictable, and produce proper error
tracebacks.

### Symptoms

- Timers are consistently slightly off (animations feel "sluggish").
- `wait(0)` does not resume immediately as expected.
- Errors inside `spawn()` callbacks silently disappear, making debugging painful.
- Legacy code that "mostly works" but has subtle timing bugs.

### Solution

Replace all legacy calls with their `task` equivalents:

| Legacy       | Replacement        | Behavior                                       |
|--------------|--------------------|-------------------------------------------------|
| `wait(n)`    | `task.wait(n)`     | Resumes after `n` seconds (min 1 frame)         |
| `spawn(fn)`  | `task.spawn(fn)`   | Runs immediately on a new thread                |
| `delay(n,fn)`| `task.delay(n,fn)` | Runs `fn` after `n` seconds on a new thread     |
| —            | `task.defer(fn)`   | Runs next resumption cycle (replaces `spawn`)    |
| —            | `task.cancel(th)`  | Cancels a thread created by task.delay/defer     |

### Code Example

```luau
-- DEPRECATED (do not use)
-- wait(1)
-- spawn(function() doWork() end)
-- delay(5, function() cleanup() end)

-- CORRECT: task library equivalents
task.wait(1) -- Yields for exactly 1 second (or the closest frame boundary)

task.spawn(function()
    -- Runs IMMEDIATELY on a new thread
    -- Errors properly propagate to the output
    doExpensiveWork()
end)

task.delay(5, function()
    -- Runs after exactly 5 seconds
    performCleanup()
end)

-- task.defer: runs on the NEXT resumption cycle (useful when you need to yield
-- the current thread briefly but resume ASAP)
task.defer(function()
    -- Runs next cycle — equivalent to the old spawn() timing
    -- but with proper error handling
    initializeSystem()
end)

-- task.cancel: cancel a deferred or delayed thread
local delayedThread = task.delay(10, function()
    print("This will never print if cancelled")
end)

-- Cancel it before it fires
task.cancel(delayedThread)

-- Practical example: countdown timer
local function startCountdown(seconds: number, onTick: (remaining: number) -> ())
    return task.spawn(function()
        for i = seconds, 1, -1 do
            onTick(i)
            task.wait(1) -- Precise 1-second intervals
        end
        onTick(0)
    end)
end

local countdownThread = startCountdown(10, function(remaining)
    print("Time left:", remaining)
end)

-- Can cancel the countdown early if needed
-- task.cancel(countdownThread)
```

---

## SE-11 | Medium | Infinite Yield Warning

### Description

`Instance:WaitForChild(name)` without a timeout parameter will yield the current thread
**forever** if the child never appears. Roblox will print an "Infinite yield possible" warning
after 5 seconds, but the thread remains stuck. If this happens in a critical path (like a
module body or initialization script), the entire system hangs silently. The warning is easy
to miss in a noisy output log.

This is especially common when:
- A developer renames an instance but forgets to update code referencing the old name.
- StreamingEnabled is on and the instance has not streamed in yet.
- The instance is created dynamically and a race condition prevents its creation.

### Symptoms

- "Infinite yield possible" warnings in output (often ignored or missed).
- Scripts that appear to "do nothing" — they are actually stuck yielding.
- Features that work in Studio but fail in live servers (due to streaming or load order).
- Debugging shows the script is alive but never progresses past a specific line.

### Solution

**Always pass a timeout** to `WaitForChild`. Handle the `nil` return when the timeout expires.
Use the timeout to fail fast and log a meaningful error instead of hanging forever.

### Code Example

```luau
-- DANGEROUS: No timeout — hangs forever if "WeaponSystem" doesn't exist
-- local weaponSystem = ReplicatedStorage:WaitForChild("WeaponSystem")

-- SAFE: Timeout with error handling
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local WAIT_TIMEOUT = 5 -- seconds

local function safeWaitForChild(
    parent: Instance,
    childName: string,
    timeout: number?
): Instance?
    local child = parent:WaitForChild(childName, timeout or WAIT_TIMEOUT)

    if not child then
        warn(
            string.format(
                "[safeWaitForChild] '%s' not found in '%s' after %d seconds. "
                    .. "Check that it exists and is spelled correctly.",
                childName,
                parent:GetFullName(),
                timeout or WAIT_TIMEOUT
            )
        )
    end

    return child
end

-- Usage: gracefully handle missing instances
local weaponFolder = safeWaitForChild(ReplicatedStorage, "Weapons", 10)
if not weaponFolder then
    -- Fall back, disable the feature, or error out early
    error("[Init] Cannot start without Weapons folder!")
end

-- Chain safely
local swordConfig = weaponFolder and safeWaitForChild(weaponFolder, "SwordConfig")
if swordConfig then
    print("Sword damage:", swordConfig:GetAttribute("Damage"))
end

-- For client scripts with StreamingEnabled, instances may not be streamed in yet.
-- Use WaitForChild with a generous timeout:
local function waitForStreamedModel(name: string): Model?
    local model = safeWaitForChild(workspace, name, 30) -- 30s for streaming
    if not model then
        warn(name, "did not stream in within 30 seconds")
    end
    return model :: Model?
end
```

---

## SE-12 | Low | String Patterns vs Regex

### Description

Luau uses **Lua string patterns**, not regular expressions. Developers coming from
JavaScript, Python, or other languages instinctively write `\d`, `\w`, `\s`, etc. These
do not work in Luau. Luau patterns use `%` as the escape character instead of `\`, and
the character classes have different names.

Additionally, Luau patterns lack many regex features: no alternation (`|`), no non-greedy
quantifiers (`*?`), no lookahead/lookbehind, and no capture groups with quantifiers.

### Symptoms

- `string.match(str, "\\d+")` returns `nil` when you expect digits.
- Pattern matches silently fail (no error, just no match).
- Developers waste time debugging "broken" patterns that are actually just wrong syntax.
- Overly complex workarounds for things regex handles in one line.

### Solution

Learn the Luau pattern equivalents. Here is the mapping:

| Regex  | Luau Pattern | Meaning                        |
|--------|-------------|--------------------------------|
| `\d`   | `%d`        | Digit (0-9)                    |
| `\D`   | `%D`        | Non-digit                      |
| `\w`   | `%w`        | Alphanumeric (letter or digit) |
| `\W`   | `%W`        | Non-alphanumeric               |
| `\s`   | `%s`        | Whitespace                     |
| `\S`   | `%S`        | Non-whitespace                 |
| `\b`   | No direct equivalent | Word boundary          |
| `.`    | `.`         | Any character (same)           |
| `\.`   | `%.`        | Literal dot                    |
| `[a-z]`| `%l`        | Lowercase letter               |
| `[A-Z]`| `%u`        | Uppercase letter               |
| `[a-zA-Z]` | `%a`   | Any letter                     |
| `*?`   | `-`         | Lazy/non-greedy match          |
| `\(`   | `%(`        | Literal parenthesis            |

### Code Example

```luau
local testString = "Player_123 scored 456 points on 2026-03-04!"

-- WRONG (regex habits):
-- string.match(testString, "\\d+")     -- Returns nil, not "123"
-- string.match(testString, "\\w+")     -- Returns nil
-- string.match(testString, "[\\d-]+")  -- Returns nil

-- CORRECT (Luau patterns):

-- Extract first number
local firstNumber = string.match(testString, "%d+")
print(firstNumber) -- "123"

-- Extract all numbers
for num in string.gmatch(testString, "%d+") do
    print("Found number:", num) -- "123", "456", "2026", "03", "04"
end

-- Extract a date pattern (YYYY-MM-DD)
local year, month, day = string.match(testString, "(%d+)-(%d+)-(%d+)")
print(year, month, day) -- "2026", "03", "04"

-- Extract a word (alphanumeric sequence)
local firstWord = string.match(testString, "%a+")
print(firstWord) -- "Player"

-- Match the player name format "Player_NNN"
local playerName = string.match(testString, "%a+_%d+")
print(playerName) -- "Player_123"

-- Lazy (non-greedy) match: use `-` instead of `*?`
local htmlish = "<tag>content</tag>"
local greedy = string.match(htmlish, "<(.+)>")      -- "tag>content</tag" (greedy)
local lazy = string.match(htmlish, "<(.-)>")         -- "tag" (non-greedy)
print("Greedy:", greedy)
print("Lazy:", lazy)

-- Escaping special characters: use % not \
local version = "v2.5.1"
local major, minor, patch = string.match(version, "v(%d+)%.(%d+)%.(%d+)")
print(major, minor, patch) -- "2", "5", "1"

-- Common gotcha: matching a literal percent sign requires %%
local discount = "Save 20% today!"
local pct = string.match(discount, "(%d+)%%")
print(pct) -- "20"
```

---

## Quick Reference: Severity at a Glance

```
CRITICAL (fix before shipping):
  SE-1  DataStore session locking        → Use ProfileService
  SE-2  Client-side currency             → Server-authoritative only
  SE-3  ProcessReceipt order             → Grant THEN PurchaseGranted

HIGH (fix in current sprint):
  SE-4  Undisconnected events            → Trove/Maid pattern
  SE-5  RemoteEvent flooding             → Per-player rate limiter
  SE-6  BindToClose 30s timeout          → Parallel saves with task.spawn

MEDIUM (fix before scale):
  SE-7  Mobile part count                → StreamingEnabled + <10K parts
  SE-8  Yielding in module require       → Init/Start lifecycle pattern
  SE-9  Table # with nil gaps            → table.remove or explicit length
  SE-11 Infinite yield WaitForChild      → Always pass timeout parameter

LOW (fix when convenient):
  SE-10 Deprecated wait/spawn/delay      → task.wait/spawn/delay
  SE-12 String patterns vs regex         → %d not \d, % not \
```
