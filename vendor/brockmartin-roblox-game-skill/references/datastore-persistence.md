# Roblox Data Persistence Reference

## 1. Overview

Data persistence in Roblox means saving player progress so it survives across sessions. Every time a player joins, the server loads their data from the cloud; every time they leave (or periodically), it saves back.

**When data flows:**

```
Player Joins  -->  Server loads from DataStore  -->  Populate in-game objects
Player Plays  -->  Data lives in server memory   -->  Auto-save on interval
Player Leaves -->  Server saves to DataStore     -->  Data persists for next session
```

**Data architecture decisions:**

| Approach | Best For | Complexity |
|----------|----------|------------|
| Raw DataStoreService | Simple games, prototypes | Low |
| ProfileService | Production games, session safety | Medium |
| Custom wrapper | Specific advanced requirements | High |

**Prerequisite:** Enable API Services in Roblox Studio under **Game Settings > Security > Enable Studio Access to API Services**. Without this, DataStore calls will fail in Studio testing.

---

## 2. DataStoreService Basics

DataStoreService is the built-in Roblox API for cloud key-value storage. Each DataStore is identified by a name, and each entry is identified by a string key.

### Core Methods

| Method | Purpose | Notes |
|--------|---------|-------|
| `GetDataStore(name)` | Get/create a named DataStore | Returns DataStore object |
| `GetAsync(key)` | Read a value | Returns nil if key doesn't exist |
| `SetAsync(key, value)` | Write a value (overwrites) | No conflict protection |
| `UpdateAsync(key, callback)` | Atomic read-modify-write | **Preferred for saves** |
| `RemoveAsync(key)` | Delete a key | Returns the old value |

`UpdateAsync` is preferred over `SetAsync` because it is atomic -- it reads the current value, lets you transform it, and writes it back in a single operation. This prevents race conditions where two servers overwrite each other.

### Basic Save/Load (Complete Example)

```luau
-- ServerScript in ServerScriptService
local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")

local playerDataStore = DataStoreService:GetDataStore("PlayerData_v1")

-- Default data for new players
local DEFAULT_DATA = {
    Cash = 0,
    Level = 1,
    Experience = 0,
    Inventory = {},
}

-- In-memory cache: Player -> data table
local playerDataCache: { [Player]: { [string]: any } } = {}

local function loadPlayerData(player: Player): { [string]: any }?
    local key = "Player_" .. player.UserId

    local success, result = pcall(function()
        return playerDataStore:GetAsync(key)
    end)

    if not success then
        warn(`[DataStore] Failed to load data for {player.Name}: {result}`)
        return nil
    end

    -- Merge with defaults so new fields get default values
    local data = result or {}
    for field, default in DEFAULT_DATA do
        if data[field] == nil then
            data[field] = default
        end
    end

    return data
end

local function savePlayerData(player: Player): boolean
    local data = playerDataCache[player]
    if not data then
        return false
    end

    local key = "Player_" .. player.UserId

    local success, err = pcall(function()
        playerDataStore:UpdateAsync(key, function(_oldData)
            return data
        end)
    end)

    if not success then
        warn(`[DataStore] Failed to save data for {player.Name}: {err}`)
        return false
    end

    return true
end

-- Load on join
Players.PlayerAdded:Connect(function(player: Player)
    local data = loadPlayerData(player)

    if not data then
        -- Kick if data fails to load to prevent overwriting with defaults
        player:Kick("Failed to load your data. Please rejoin.")
        return
    end

    playerDataCache[player] = data
    -- Set up leaderstats, UI, etc. using data
end)

-- Save on leave
Players.PlayerRemoving:Connect(function(player: Player)
    savePlayerData(player)
    playerDataCache[player] = nil
end)

-- Auto-save every 5 minutes
task.spawn(function()
    while true do
        task.wait(300)
        for player, _data in playerDataCache do
            task.spawn(savePlayerData, player)
        end
    end
end)

-- Save all on server shutdown
game:BindToClose(function()
    local threads: { thread } = {}
    for player, _data in playerDataCache do
        local t = task.spawn(savePlayerData, player)
        table.insert(threads, t)
    end
    -- BindToClose has a 30-second timeout; parallel saves finish faster
    -- task.spawn already fires them concurrently, so just wait briefly
    task.wait(5)
end)
```

---

## 3. Leaderstats Pattern

The "leaderstats" pattern is the standard Roblox convention for showing player stats on the in-game leaderboard (the tab/playerlist).

**How it works:** Create a Folder named exactly `"leaderstats"` inside the Player object. Add IntValue or StringValue children -- their names and values appear on the leaderboard automatically.

### Leaderstats with DataStore Persistence

```luau
-- ServerScript in ServerScriptService
local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")

local dataStore = DataStoreService:GetDataStore("LeaderstatsData_v1")

local function setupLeaderstats(player: Player, data: { [string]: number })
    local leaderstats = Instance.new("Folder")
    leaderstats.Name = "leaderstats"
    leaderstats.Parent = player

    local cash = Instance.new("IntValue")
    cash.Name = "Cash"
    cash.Value = data.Cash or 0
    cash.Parent = leaderstats

    local level = Instance.new("IntValue")
    level.Name = "Level"
    level.Value = data.Level or 1
    level.Parent = leaderstats
end

local function getLeaderstatsData(player: Player): { [string]: number }
    local leaderstats = player:FindFirstChild("leaderstats")
    if not leaderstats then
        return {}
    end

    return {
        Cash = leaderstats:FindFirstChild("Cash") and leaderstats.Cash.Value or 0,
        Level = leaderstats:FindFirstChild("Level") and leaderstats.Level.Value or 1,
    }
end

local function savePlayer(player: Player)
    local data = getLeaderstatsData(player)
    local key = "Player_" .. player.UserId

    local success, err = pcall(function()
        dataStore:UpdateAsync(key, function()
            return data
        end)
    end)

    if not success then
        warn(`[Leaderstats] Save failed for {player.Name}: {err}`)
    end
end

Players.PlayerAdded:Connect(function(player: Player)
    local key = "Player_" .. player.UserId

    local success, data = pcall(function()
        return dataStore:GetAsync(key)
    end)

    if not success then
        player:Kick("Data load error. Please rejoin.")
        return
    end

    setupLeaderstats(player, data or {})
end)

Players.PlayerRemoving:Connect(savePlayer)

-- Auto-save interval
task.spawn(function()
    while true do
        task.wait(300)
        for _, player in Players:GetPlayers() do
            task.spawn(savePlayer, player)
        end
    end
end)

-- BindToClose for server shutdown
game:BindToClose(function()
    for _, player in Players:GetPlayers() do
        task.spawn(savePlayer, player)
    end
    task.wait(5)
end)
```

**Key points:**
- The folder MUST be named `"leaderstats"` (lowercase, exact spelling).
- Use `IntValue` for numbers, `StringValue` for text.
- Changes to these Value objects update the leaderboard in real time.
- Leaderstats are visible to all players -- do not put sensitive data here.

---

## 4. ProfileService

ProfileService is the community-standard library for production-grade data persistence. It solves critical problems that raw DataStore usage does not handle.

### Why Use It

| Feature | Raw DataStore | ProfileService |
|---------|--------------|----------------|
| Session locking | Manual (hard) | Automatic |
| Auto-save | Manual | Built-in |
| Schema migration | Manual | Supported |
| Data corruption protection | None | Built-in |
| Retry logic | Manual | Built-in |
| BindToClose handling | Manual | Automatic |

### Installation

**With Wally (recommended):**

```toml
# wally.toml
[dependencies]
ProfileService = "madstudioroblox/profileservice@1.4.0"
```

Run `wally install`, then require from the Packages folder.

**Manual:** Download from GitHub and place the ProfileService ModuleScript into ServerScriptService or ReplicatedStorage.

### Complete ProfileService Setup

```luau
-- ServerScript in ServerScriptService
local Players = game:GetService("Players")
local ServerScriptService = game:GetService("ServerScriptService")

local ProfileService = require(ServerScriptService.Packages.ProfileService)
-- Adjust the require path based on where you installed it

-- Define the profile template (default data for new players)
local PROFILE_TEMPLATE = {
    DataVersion = 1,
    Cash = 0,
    Level = 1,
    Experience = 0,
    Inventory = {},
    Settings = {
        MusicVolume = 0.5,
        SFXVolume = 0.8,
    },
    Statistics = {
        TotalPlayTime = 0,
        GamesPlayed = 0,
    },
}

-- Create the ProfileStore (wraps a DataStore)
local ProfileStore = ProfileService.GetProfileStore("PlayerProfiles_v1", PROFILE_TEMPLATE)

-- Active profiles cache
local Profiles: { [Player]: typeof(ProfileStore:LoadProfileAsync("")) } = {}

local function onProfileLoaded(player: Player, profile)
    -- Session lock: if the profile was stolen by another server, release and kick
    profile:AddUserId(player.UserId) -- GDPR compliance
    profile:Reconcile() -- Fills in missing fields from PROFILE_TEMPLATE

    profile:ListenToRelease(function()
        Profiles[player] = nil
        player:Kick("Your data was loaded on another server. Please rejoin.")
    end)

    -- Check if player is still in game (they may have left during async load)
    if not player:IsDescendantOf(Players) then
        profile:Release()
        return
    end

    -- Store and set up the player
    Profiles[player] = profile

    -- Example: set up leaderstats from profile data
    local leaderstats = Instance.new("Folder")
    leaderstats.Name = "leaderstats"
    leaderstats.Parent = player

    local cash = Instance.new("IntValue")
    cash.Name = "Cash"
    cash.Value = profile.Data.Cash
    cash.Parent = leaderstats

    local level = Instance.new("IntValue")
    level.Name = "Level"
    level.Value = profile.Data.Level
    level.Parent = leaderstats
end

Players.PlayerAdded:Connect(function(player: Player)
    local profile = ProfileStore:LoadProfileAsync(
        "Player_" .. player.UserId,
        "ForceLoad" -- Wait until the session lock is acquired
    )

    if profile == nil then
        player:Kick("Unable to load your data. Please rejoin.")
        return
    end

    onProfileLoaded(player, profile)
end)

Players.PlayerRemoving:Connect(function(player: Player)
    local profile = Profiles[player]
    if profile then
        -- Sync leaderstats back to profile before release
        local leaderstats = player:FindFirstChild("leaderstats")
        if leaderstats then
            profile.Data.Cash = leaderstats.Cash.Value
            profile.Data.Level = leaderstats.Level.Value
        end

        profile:Release()
    end
end)

-- Helper to get a player's profile from other scripts
-- Export this via a ModuleScript in production
local function getProfile(player: Player)
    return Profiles[player]
end
```

### Accessing Profile Data From Other Scripts

```luau
-- In another ServerScript or ModuleScript
local function addCash(player: Player, amount: number)
    local profile = getProfile(player)
    if not profile then
        return
    end

    profile.Data.Cash += amount

    -- Also update leaderstats if visible
    local leaderstats = player:FindFirstChild("leaderstats")
    if leaderstats and leaderstats:FindFirstChild("Cash") then
        leaderstats.Cash.Value = profile.Data.Cash
    end
end
```

---

## 5. Session Locking Explained

### The Problem

Without session locking, data corruption can occur during server hops:

```
Timeline:
  t=0   Player is on Server A, data loaded
  t=1   Player teleports to Server B
  t=2   Server B starts loading player data from DataStore
  t=3   Server A fires PlayerRemoving, starts saving data
  t=4   Server B finishes loading (gets STALE data)
  t=5   Server A finishes saving (writes LATEST data)
  t=6   Server B eventually saves its stale copy, OVERWRITING the latest data

Result: Player loses progress from Server A session
```

### The Solution

Session locking ensures that only one server can own a player's data at a time:

```
Timeline with Session Locking:
  t=0   Server A loads profile, acquires session lock
  t=1   Player teleports to Server B
  t=2   Server B tries to load -- sees lock owned by Server A, WAITS
  t=3   Server A fires PlayerRemoving, saves data, RELEASES lock
  t=4   Server B detects lock released, acquires lock, loads LATEST data

Result: No data loss
```

### How ProfileService Implements It

1. When `LoadProfileAsync` is called, ProfileService writes a session lock tag (server JobId) to the DataStore entry.
2. If another server already holds the lock, ProfileService either waits ("ForceLoad") or gives up ("Steal").
3. The locking server periodically refreshes the lock via auto-save.
4. On `profile:Release()`, the lock is cleared and the data is saved.
5. If a server crashes without releasing, the lock expires after a timeout (~30 minutes by default), and another server can then claim it.

**You do NOT need to implement session locking manually.** ProfileService handles all of this. This is the primary reason to use it over raw DataStoreService.

---

## 6. Data Schema Design

### Flat vs. Nested Structure

**Flat (simple games):**

```luau
local PROFILE_TEMPLATE = {
    Cash = 0,
    Level = 1,
    Wins = 0,
    Losses = 0,
}
```

**Nested (complex games):**

```luau
local PROFILE_TEMPLATE = {
    DataVersion = 1,
    Currency = {
        Cash = 0,
        Gems = 0,
        Tickets = 0,
    },
    Progression = {
        Level = 1,
        Experience = 0,
        Prestige = 0,
    },
    Inventory = {
        Swords = {},    -- Array of item IDs or item tables
        Armor = {},
        Consumables = {},
    },
    Quests = {
        Active = {},
        Completed = {},
    },
    Settings = {
        MusicVolume = 0.5,
        SFXVolume = 0.8,
        ShowTutorial = true,
    },
}
```

### Versioning Your Schema

Always include a `DataVersion` field. This lets you detect and migrate old data formats.

```luau
local PROFILE_TEMPLATE = {
    DataVersion = 3,   -- Increment when schema changes
    -- ... fields ...
}
```

### Default Values for New Fields

When you add new fields, existing players will not have them. Use `Reconcile()` (ProfileService) or manual merging (raw DataStore) to fill in defaults:

```luau
-- Manual merge approach (raw DataStore)
local function applyDefaults(data: { [string]: any }, defaults: { [string]: any })
    for key, default in defaults do
        if data[key] == nil then
            if typeof(default) == "table" then
                data[key] = table.clone(default)
            else
                data[key] = default
            end
        end
    end
    return data
end
```

### Type Safety Tips

- Use consistent types per field. If `Cash` is a number, never save it as a string.
- Arrays should contain uniform types (`{ number }`, not mixed).
- Avoid storing `nil` explicitly -- DataStore omits nil keys, which can cause confusion. Use sentinel values (e.g., `0`, `""`, `false`) instead.
- Remember: DataStore serializes to JSON internally. Only JSON-compatible types work: `number`, `string`, `boolean`, `table` (arrays and dictionaries). No Instances, Vector3s, CFrames, or other Roblox types directly.

---

## 7. Data Migration

When your data schema changes, you need to migrate existing player data to the new format.

### Migration Strategy

1. Check `DataVersion` when data is loaded.
2. Apply migration functions sequentially (v1 -> v2, v2 -> v3, etc.).
3. Update `DataVersion` to current.

### Complete Migration Example

```luau
-- DataMigrations module
local DataMigrations = {}

-- Each migration transforms data from version N to version N+1
local migrations: { [number]: (data: { [string]: any }) -> { [string]: any } } = {}

-- v1 -> v2: Split "Money" into "Cash" and "Gems"
migrations[1] = function(data)
    if data.Money then
        data.Cash = data.Money
        data.Gems = 0
        data.Money = nil
    end
    return data
end

-- v2 -> v3: Move settings out of flat structure into nested table
migrations[2] = function(data)
    data.Settings = {
        MusicVolume = data.MusicVolume or 0.5,
        SFXVolume = data.SFXVolume or 0.8,
    }
    data.MusicVolume = nil
    data.SFXVolume = nil
    return data
end

-- v3 -> v4: Add Quests system and rename "Wins" to "Statistics.Wins"
migrations[3] = function(data)
    data.Quests = {
        Active = {},
        Completed = {},
    }
    data.Statistics = data.Statistics or {}
    data.Statistics.Wins = data.Wins or 0
    data.Wins = nil
    return data
end

local CURRENT_VERSION = 4

function DataMigrations.migrate(data: { [string]: any }): { [string]: any }
    local version = data.DataVersion or 1

    if version > CURRENT_VERSION then
        warn(`[Migration] Data version {version} is newer than code version {CURRENT_VERSION}`)
        return data
    end

    while version < CURRENT_VERSION do
        local migrator = migrations[version]
        if migrator then
            data = migrator(data)
            print(`[Migration] Migrated data from v{version} to v{version + 1}`)
        end
        version += 1
    end

    data.DataVersion = CURRENT_VERSION
    return data
end

return DataMigrations
```

### Using Migrations With ProfileService

```luau
-- After loading the profile, before using the data:
local profile = ProfileStore:LoadProfileAsync("Player_" .. player.UserId, "ForceLoad")
if profile then
    profile.Data = DataMigrations.migrate(profile.Data)
    profile:Reconcile() -- Fill in any remaining missing defaults
end
```

---

## 8. OrderedDataStore

`OrderedDataStore` is a special DataStore type that stores integer values and supports sorted queries. It is the standard way to build global leaderboards.

### Complete Leaderboard Implementation

```luau
-- ServerScript in ServerScriptService
local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")

local cashLeaderboard = DataStoreService:GetOrderedDataStore("CashLeaderboard")

local LEADERBOARD_SIZE = 100
local UPDATE_INTERVAL = 120  -- seconds

-- Update a player's score in the leaderboard
local function updateLeaderboardScore(userId: number, score: number)
    local success, err = pcall(function()
        cashLeaderboard:SetAsync(tostring(userId), score)
    end)

    if not success then
        warn(`[Leaderboard] Failed to update score for {userId}: {err}`)
    end
end

-- Fetch the top N entries from the leaderboard
local function getTopPlayers(count: number): { { UserId: number, Score: number, Rank: number } }
    local results = {}

    local success, pages = pcall(function()
        return cashLeaderboard:GetSortedAsync(
            false,   -- isAscending: false = highest first
            count    -- pageSize
        )
    end)

    if not success then
        warn(`[Leaderboard] Failed to fetch leaderboard: {pages}`)
        return results
    end

    local currentPage = pages:GetCurrentPage()
    local rank = 0

    for _, entry in currentPage do
        rank += 1
        table.insert(results, {
            UserId = tonumber(entry.key),
            Score = entry.value,
            Rank = rank,
        })
    end

    -- If you need more pages:
    -- while not pages.IsFinished do
    --     pages:AdvanceToNextPageAsync()
    --     for _, entry in pages:GetCurrentPage() do
    --         rank += 1
    --         table.insert(results, { ... })
    --     end
    -- end

    return results
end

-- Populate a SurfaceGui or Billboard leaderboard (example with a Frame)
local function displayLeaderboard(surfaceGui: SurfaceGui, entries: { { UserId: number, Score: number, Rank: number } })
    local container = surfaceGui:FindFirstChild("Container")
    if not container then
        return
    end

    -- Clear old entries
    for _, child in container:GetChildren() do
        if child:IsA("Frame") then
            child:Destroy()
        end
    end

    for _, entry in entries do
        -- Get player name (works for offline players too)
        local success, name = pcall(function()
            return Players:GetNameFromUserIdAsync(entry.UserId)
        end)

        if success then
            local row = Instance.new("Frame")
            row.Name = "Rank_" .. entry.Rank
            row.Size = UDim2.new(1, 0, 0, 30)
            row.LayoutOrder = entry.Rank
            row.Parent = container

            local rankLabel = Instance.new("TextLabel")
            rankLabel.Text = `#{entry.Rank}`
            rankLabel.Size = UDim2.new(0.15, 0, 1, 0)
            rankLabel.Parent = row

            local nameLabel = Instance.new("TextLabel")
            nameLabel.Text = name
            nameLabel.Size = UDim2.new(0.55, 0, 1, 0)
            nameLabel.Position = UDim2.new(0.15, 0, 0, 0)
            nameLabel.Parent = row

            local scoreLabel = Instance.new("TextLabel")
            scoreLabel.Text = tostring(entry.Score)
            scoreLabel.Size = UDim2.new(0.3, 0, 1, 0)
            scoreLabel.Position = UDim2.new(0.7, 0, 0, 0)
            scoreLabel.Parent = row
        end
    end
end

-- Periodic leaderboard update loop
task.spawn(function()
    while true do
        -- Update scores for all online players
        for _, player in Players:GetPlayers() do
            local leaderstats = player:FindFirstChild("leaderstats")
            if leaderstats and leaderstats:FindFirstChild("Cash") then
                task.spawn(updateLeaderboardScore, player.UserId, leaderstats.Cash.Value)
            end
        end

        -- Fetch and display updated leaderboard
        task.wait(5) -- Brief delay for scores to propagate
        local topPlayers = getTopPlayers(LEADERBOARD_SIZE)

        -- Update all leaderboard displays in the world
        -- (Replace with your actual SurfaceGui references)
        -- displayLeaderboard(workspace.LeaderboardPart.SurfaceGui, topPlayers)

        task.wait(UPDATE_INTERVAL)
    end
end)
```

**Important:** OrderedDataStore only supports **integer** values. If you need decimal scores, multiply by a factor (e.g., store `score * 100`).

---

## 9. Cross-Server Data

### MessagingService (Real-Time Pub/Sub)

For real-time communication between servers (announcements, events, cross-server trading).

```luau
local MessagingService = game:GetService("MessagingService")

-- Subscribe to a topic
local connection = MessagingService:SubscribeAsync("GlobalAnnouncement", function(message)
    local data = message.Data -- The payload
    local sent = message.Sent -- Timestamp when sent (Unix time)

    -- Broadcast to all players on this server
    for _, player in Players:GetPlayers() do
        -- Show announcement UI, etc.
    end
end)

-- Publish to a topic (reaches all servers)
local success, err = pcall(function()
    MessagingService:PublishAsync("GlobalAnnouncement", {
        Text = "Double XP weekend starts now!",
        Duration = 3600,
    })
end)
```

**MessagingService limits:**
- Message size: 1 KB max
- Messages per server: 150 + 60 * playerCount per minute
- Subscriptions per server: 5 + 2 * playerCount
- Messages are NOT persisted -- only online servers receive them.

### GlobalDataStore for Shared State

For persistent cross-server state (global counters, server-wide events):

```luau
local globalStore = DataStoreService:GetDataStore("GlobalState")

-- Atomically increment a global counter
local function incrementGlobalCounter(key: string, amount: number): number?
    local success, newValue = pcall(function()
        return globalStore:UpdateAsync(key, function(old)
            return (old or 0) + amount
        end)
    end)

    if success then
        return newValue
    end
    return nil
end

-- Example: Track total enemies defeated across all servers
local totalDefeated = incrementGlobalCounter("TotalEnemiesDefeated", 1)
```

---

## 10. Best Practices

### Auto-Save Interval

Save every 5 minutes (300 seconds). This balances data safety against rate limits.

```luau
local AUTO_SAVE_INTERVAL = 300

task.spawn(function()
    while true do
        task.wait(AUTO_SAVE_INTERVAL)
        for player, _data in playerDataCache do
            task.spawn(savePlayerData, player)
        end
    end
end)
```

### Save on PlayerRemoving

Always save when a player disconnects:

```luau
Players.PlayerRemoving:Connect(function(player: Player)
    savePlayerData(player)
    playerDataCache[player] = nil
end)
```

### BindToClose Handler (Critical)

`game:BindToClose` fires when the server is shutting down. You have **30 seconds** to save all data before the server terminates. Use `task.spawn` for parallel saves.

```luau
-- Complete BindToClose handler
game:BindToClose(function()
    -- If running in Studio, don't wait long
    if game:GetService("RunService"):IsStudio() then
        task.wait(1)
        return
    end

    local finished = Instance.new("BindableEvent")
    local allPlayers = Players:GetPlayers()
    local remaining = #allPlayers

    if remaining == 0 then
        return
    end

    for _, player in allPlayers do
        task.spawn(function()
            -- Save player data
            savePlayerData(player)

            remaining -= 1
            if remaining <= 0 then
                finished:Fire()
            end
        end)
    end

    -- Wait for all saves to complete, or timeout after 25 seconds
    -- (leave 5-second buffer before the 30-second hard limit)
    task.delay(25, function()
        finished:Fire()
    end)

    finished.Event:Wait()
    finished:Destroy()
end)
```

### Retry Failed Saves

```luau
local MAX_RETRIES = 3
local RETRY_DELAY = 2

local function saveWithRetry(player: Player): boolean
    for attempt = 1, MAX_RETRIES do
        local success = savePlayerData(player)
        if success then
            return true
        end

        if attempt < MAX_RETRIES then
            warn(`[DataStore] Retry {attempt}/{MAX_RETRIES} for {player.Name}`)
            task.wait(RETRY_DELAY * attempt) -- Exponential-ish backoff
        end
    end

    warn(`[DataStore] All retries failed for {player.Name}`)
    return false
end
```

### Validate Data Before Saving

```luau
local function validateData(data: { [string]: any }): boolean
    if typeof(data) ~= "table" then
        return false
    end

    -- Check critical fields exist and have correct types
    if typeof(data.Cash) ~= "number" or data.Cash < 0 then
        return false
    end

    if typeof(data.Level) ~= "number" or data.Level < 1 then
        return false
    end

    return true
end

local function safeSave(player: Player)
    local data = playerDataCache[player]
    if not data or not validateData(data) then
        warn(`[DataStore] Invalid data for {player.Name}, skipping save`)
        return
    end

    savePlayerData(player)
end
```

---

## 11. Anti-Patterns

### Saving Too Frequently

**Wrong:**
```luau
-- DO NOT DO THIS: saving on every coin pickup
coinTouched:Connect(function(player)
    player.Data.Cash += 1
    dataStore:SetAsync("Player_" .. player.UserId, player.Data) -- Rate limit hit
end)
```

**Right:** Modify in-memory data immediately, rely on periodic auto-save.

**DataStore rate limits:** `60 + numPlayers * 10` requests per minute per DataStore. With 50 players, that is 560 requests/min total -- or about 11 per player per minute. Saving once per 5 minutes uses only 0.2 per player per minute.

### Not Handling DataStore Errors

**Wrong:**
```luau
-- DO NOT DO THIS: unprotected call
local data = dataStore:GetAsync(key) -- Will error and break the script
```

**Right:**
```luau
local success, data = pcall(function()
    return dataStore:GetAsync(key)
end)

if not success then
    warn("DataStore error:", data)
    -- Handle gracefully
end
```

### Storing Instance References

**Wrong:**
```luau
-- DO NOT DO THIS: Instances are not serializable
data.Weapon = workspace.Sword -- Will fail or produce garbage
data.Character = player.Character -- Same problem
```

**Right:** Store serializable identifiers.
```luau
data.WeaponId = "IronSword"
data.EquippedSlots = { "Helmet_01", "Armor_03" }
```

### Exceeding Key Size Limits

| Limit | Value |
|-------|-------|
| Key name length | 50 characters |
| Value size per key | 4,194,304 bytes (4 MB) |
| DataStore name length | 50 characters |

If you're approaching 4 MB, split data across multiple keys:

```luau
-- Split by category
local coreStore = DataStoreService:GetDataStore("PlayerCore")
local inventoryStore = DataStoreService:GetDataStore("PlayerInventory")
local questStore = DataStoreService:GetDataStore("PlayerQuests")
```

---

## 12. Sharp Edges

### Rate Limits

DataStore requests are throttled per-server, not per-player:

| Operation | Budget per Minute |
|-----------|-------------------|
| GetAsync | 60 + numPlayers * 10 |
| SetAsync / UpdateAsync | 60 + numPlayers * 10 |
| GetSortedAsync | 5 + numPlayers * 2 |
| SetAsync on OrderedDataStore | 5 + numPlayers * 2 |

Exceeding these results in requests being queued or erroring. Plan save intervals accordingly.

### Eventual Consistency

DataStore reads are eventually consistent. After a `SetAsync`, a `GetAsync` from another server may briefly return stale data. `UpdateAsync` on the same key is atomic within a single call, but across keys or across servers there is no transaction guarantee.

### BindToClose 30-Second Timeout

When a Roblox server shuts down, `BindToClose` callbacks are given at most **30 seconds** to finish. After that, the server process is killed regardless. If you have many players, you MUST save in parallel using `task.spawn`, not sequentially.

```luau
-- BAD: Sequential saves with 50 players could take > 30 seconds
for _, player in Players:GetPlayers() do
    savePlayerData(player) -- Each call might take 0.5-2 seconds
end

-- GOOD: Parallel saves complete in the time of the slowest single save
for _, player in Players:GetPlayers() do
    task.spawn(savePlayerData, player)
end
task.wait(25) -- Wait with buffer
```

### Data Loss from Race Conditions Without Session Locking

Without session locking (i.e., using raw DataStore), the following scenario causes data loss:

1. Player leaves Server A. `PlayerRemoving` fires, save begins.
2. Player joins Server B before Server A's save completes.
3. Server B loads stale data (Server A hasn't finished writing yet).
4. Server A finishes saving. Server B later saves its stale copy, overwriting Server A's save.

**Mitigation:** Use ProfileService (preferred) or implement manual session locking with `UpdateAsync` by writing a lock field containing the server's `game.JobId` and checking it before loading.

### Studio Testing Gotchas

- `PlayerRemoving` does NOT fire when you press Stop in Studio. Data will not save on exit during testing unless you also test via `BindToClose`.
- DataStore calls fail in Studio unless **Enable Studio Access to API Services** is checked in Game Settings > Security.
- Studio and live game share the same DataStore if using the same place. Use different DataStore names or a prefix for testing:

```luau
local RunService = game:GetService("RunService")
local PREFIX = RunService:IsStudio() and "Dev_" or ""
local dataStore = DataStoreService:GetDataStore(PREFIX .. "PlayerData_v1")
```

### Other Pitfalls

- **NaN values:** If a NaN (not a number) sneaks into your data (e.g., `0/0`), `SetAsync`/`UpdateAsync` will error silently or corrupt the entry. Validate numeric fields.
- **Empty tables:** An empty table `{}` can deserialize as either an array or a dictionary depending on context. Be consistent.
- **Key naming:** Keys are case-sensitive. `"Player_123"` and `"player_123"` are different keys. Standardize your key format.
- **UpdateAsync callback:** The callback passed to `UpdateAsync` must be pure (no yields, no side effects). It may be called multiple times if there is contention. Return `nil` to cancel the update.
