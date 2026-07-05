# Roblox Server & Shared Data — Full Reference

> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

## OrderedDataStore

### Overview

OrderedDataStore is a sortable variant of DataStore. Keys must be positive integers (typically UserId). Used primarily for leaderboards.

### API

| Method | Purpose |
|--------|---------|
| `GetSortedAsync(ascending, pageSize, minValue, maxValue)` | Get sorted pages of entries |
| `SetAsync(key, value)` | Set a key's value (key must be positive integer) |
| `IncrementAsync(key, delta)` | Atomically increment a key's value |
| `RemoveAsync(key)` | Remove an entry |
| `UpdateAsync(key, transformFunction)` | Atomic read-modify-write |

### Leaderboard Implementation

```luau
local DataStoreService = game:GetService("DataStoreService")
local coinStore = DataStoreService:GetOrderedDataStore("LeaderboardCoins")

-- Update player's score
local function updateScore(userId: number, coins: number)
    local success, err = pcall(function()
        coinStore:SetAsync(userId, coins)
    end)
    if not success then warn("Leaderboard update failed:", err) end
end

-- Fetch top 10
local function getTopPlayers(count: number): {any}
    local success, pages = pcall(function()
        return coinStore:GetSortedAsync(false, count)
    end)
    if not success then return {} end
    return pages:GetCurrentPage()
end

-- Iterate all pages
local function processAllEntries(callback)
    local pages = coinStore:GetSortedAsync(false, 100)
    while true do
        for _, entry in pages:GetCurrentPage() do
            callback(entry.key, entry.value)
        end
        if pages.IsFinished then break end
        pages:AdvanceToNextPageAsync()
    end
end
```

### Key Rules
- Keys MUST be positive integers — use `player.UserId`
- Values must be numbers — no strings, tables, or nested data
- Separate from player DataStore — different key space, different purpose
- `GetSortedAsync` returns pages, not a flat list — use pagination
- Rate limits apply same as regular DataStores

## MessagingService

### Overview

Real-time communication between server instances. Fire-and-forget — no delivery guarantee, no ordering guarantee.

### API

| Method | Purpose |
|--------|---------|
| `SubscribeAsync(topic, callback)` | Listen for messages on a topic |
| `PublishAsync(topic, message)` | Broadcast to all servers subscribed to topic |

### Server Registration Pattern

```luau
local MessagingService = game:GetService("MessagingService")
local jobId = game.JobId

-- Announce this server is alive
local function announceServer()
    local serverInfo = {
        jobId = jobId,
        playerCount = #game.Players:GetPlayers(),
        capacity = game.Players.MaxPlayers,
    }
    pcall(function()
        MessagingService:PublishAsync("ServerHeartbeat", serverInfo)
    end)
end

-- Listen for heartbeats from other servers
local activeServers = {}
MessagingService:SubscribeAsync("ServerHeartbeat", function(message)
    local data = message.Data
    activeServers[data.jobId] = {
        playerCount = data.playerCount,
        lastSeen = os.time(),
    }
end)

-- Heartbeat loop
task.spawn(function()
    while true do
        announceServer()
        -- Clean stale servers (no heartbeat in 30s)
        for id, info in activeServers do
            if os.time() - info.lastSeen > 30 then
                activeServers[id] = nil
            end
        end
        task.wait(10)
    end
end)
```

### Cross-Server Player Migration

```luau
-- When a player leaves, notify other servers to release any shared locks
game.Players.PlayerRemoving:Connect(function(player)
    pcall(function()
        MessagingService:PublishAsync("PlayerLeft", {
            userId = player.UserId,
            fromServer = jobId,
        })
    end)
end)
```

### Key Rules
- Messages are fire-and-forget — design for idempotency
- No ordering guarantee — handle out-of-order messages gracefully
- Rate limit: ~10 + 150 * (CCU + 1) messages per minute
- Message size limited — keep payloads small
- `message.Data` contains the published payload
- Subscribe callbacks run in a separate thread — use pcall

## GlobalDataStore

### Overview

GlobalDataStore is the same DataStore API but used for shared, non-player state. No session locking. Use `UpdateAsync` for atomic operations on shared counters.

### Guild/Clan Data Pattern

```luau
local DataStoreService = game:GetService("DataStoreService")
local guildStore = DataStoreService:GetDataStore("GuildData")

local function getGuild(guildId: string): table?
    local success, data = pcall(function()
        return guildStore:GetAsync("guild_" .. guildId)
    end)
    if success then return data end
    return nil
end

local function updateGuild(guildId: string, callback: (data: table) -> table)
    local key = "guild_" .. guildId
    local success, err = pcall(function()
        guildStore:UpdateAsync(key, function(oldData)
            local data = oldData or { members = {}, createdAt = os.time() }
            return callback(data)
        end)
    end)
    if not success then warn("Guild update failed:", err) end
end

-- Add member atomically
updateGuild("guild123", function(data)
    table.insert(data.members, { userId = 456, role = "member", joinedAt = os.time() })
    return data
end)
```

### Atomic Counter Pattern

```luau
local counterStore = DataStoreService:GetDataStore("GlobalCounters")

local function incrementCounter(name: string, delta: number)
    pcall(function()
        counterStore:UpdateAsync("counter_" .. name, function(oldValue)
            return (oldValue or 0) + delta
        end)
    end)
end
```

### Key Rules
- Always use `UpdateAsync` for shared state — `SetAsync` can lose updates
- Never store Instances — serialize to primitives
- Same rate limits as player DataStores
- No session locking — don't use for player data
- Key naming: use prefixes to namespace (`guild_`, `counter_`, `season_`)

## Persistent World State

### Building/Construction Games

Serialize player-built structures as tables, store per-player or globally:

```luau
-- Serialize a built structure
local function serializeBuild(building: Model): table
    local parts = {}
    for _, part in building:GetDescendants() do
        if part:IsA("BasePart") then
            table.insert(parts, {
                class = part.ClassName,
                cf = {part.CFrame:GetComponents()},
                size = {part.Size.X, part.Size.Y, part.Size.Z},
                color = {part.Color.R, part.Color.G, part.Color.B},
                material = part.Material.Name,
            })
        end
    end
    return { name = building.Name, parts = parts }
end
```

### Season/Event Data

```luau
local seasonStore = DataStoreService:GetDataStore("SeasonData")

local function getSeasonInfo(): table
    local success, data = pcall(function()
        return seasonStore:GetAsync("current_season")
    end)
    if success and data then return data end
    return { season = 1, startedAt = os.time(), endsAt = os.time() + 604800 }
end
```

## Pitfalls

- **MessagingService delivery**: not guaranteed. If a server misses a message, it's gone. Design for eventual consistency.
- **GlobalDataStore rate limits**: same as player DataStores. Don't use for high-frequency updates.
- **OrderedDataStore key type**: must be positive integer. Using string keys throws an error.
- **Lost updates with SetAsync**: always use `UpdateAsync` for shared state. `SetAsync` overwrites without reading.
- **Serialization**: DataStores only store JSON-compatible types (string, number, boolean, table, nil). No Instances, no functions, no userdata.
- **Cross-server timing**: MessagingService has latency. Don't rely on it for time-critical operations.
