# roblox data persistence: full reference

This guide uses raw `DataStoreService` concepts and does not require a particular profile library. If the project already uses a session-locking wrapper, keep its lifecycle and failure semantics instead of mixing two ownership systems.

## 1. Choose the storage primitive

- **Player data store:** mutable per-player state such as inventory, settings, and progression.
- **Ordered data store:** sorted numeric values for leaderboards. It is not a substitute for a player's profile.
- **MessagingService:** short-lived cross-server notifications, not durable storage.
- **MemoryStoreService:** temporary, expiring coordination or queues. Do not treat it as permanent player data.

Keep the store name, schema version, and key format in one module. Use stable keys such as `player_<UserId>` and convert numeric IDs to strings at the boundary.

## 2. Define a serializable schema

A template makes missing fields predictable and gives migrations a target.

```luau
local CURRENT_VERSION = 3

local TEMPLATE = {
    version = CURRENT_VERSION,
    coins = 0,
    inventory = {},
    settings = {
        music = true,
        sensitivity = 1,
    },
}

local function cloneTemplate()
    return table.clone(TEMPLATE)
end
```

Do not use a shallow clone when nested tables will be mutated. Write a small deep-copy helper or construct nested defaults explicitly. Never store Instances, functions, connections, threads, cyclic references, or values the DataStore serializer cannot represent.

## 3. Read with bounded retries

Retries must be finite and observable. Use exponential backoff with jitter and stop when the server is shutting down.

```luau
local DataStoreService = game:GetService("DataStoreService")
local store = DataStoreService:GetDataStore("PlayerData_v3")

local function readPlayer(userId: number): (boolean, any)
    local key = "player_" .. tostring(userId)
    local delaySeconds = 1

    for attempt = 1, 4 do
        local ok, value = pcall(function()
            return store:GetAsync(key)
        end)
        if ok then
            return true, value
        end
        task.wait(delaySeconds + math.random() * 0.25)
        delaySeconds *= 2
    end

    return false, nil
end
```

A failed read is not an empty profile. Keep the player in a safe loading state or fail the join rather than overwriting an existing record with defaults.

## 4. Session ownership

Two live servers must not both believe they own the same mutable profile. A wrapper may implement locks, heartbeat, and release handling. If implementing the protocol yourself, define:

- an owner token that identifies the live server;
- an expiry or heartbeat policy;
- the behavior when a lock is fresh, stale, or ambiguous;
- how release is recorded;
- what happens if the server crashes between a write and a release.

Do not silently take a lock just because a player is joining. A false takeover can lose progress from the original server. If the project uses a library such as ProfileStore, read its current documentation and use its release signals rather than reaching into internal fields.

## 5. Atomic updates

Use `UpdateAsync` when the new value depends on the stored value. The transform should be deterministic, small, and safe to run more than once if the service retries it.

```luau
local function addCoins(userId: number, amount: number): boolean
    if amount < 0 or amount > 1_000_000 then
        return false
    end

    local ok = pcall(function()
        store:UpdateAsync("player_" .. tostring(userId), function(old)
            local data = old or cloneTemplate()
            data.coins = (data.coins or 0) + amount
            data.version = CURRENT_VERSION
            return data
        end)
    end)
    return ok
end
```

Do not perform network calls, yield, or mutate external state inside the transform callback. If the callback returns `nil`, the update is cancelled; use that deliberately.

## 6. Migration

Migrate data after it is loaded and before gameplay sees it. Each migration should be small, ordered, and testable.

```luau
local function migrate(data)
    data = data or cloneTemplate()
    data.version = data.version or 1

    if data.version < 2 then
        data.coins = data.coins or data.gold or 0
        data.gold = nil
        data.version = 2
    end
    if data.version < 3 then
        data.settings = data.settings or { music = true, sensitivity = 1 }
        data.version = 3
    end

    return data
end
```

Keep old-field handling until every supported record has migrated or until a deliberate data-retention policy says it can be removed. Test migrations against missing fields, old nested shapes, extra fields, and malformed values.

## 7. Save lifecycle

A practical lifecycle is:

1. load before enabling gameplay;
2. hold the profile in memory while the player is active;
3. mark dirty when state changes, then autosave at a bounded interval;
4. release or final-save on `PlayerRemoving`;
5. flush pending work from `BindToClose`.

Use one save coordinator per player. Multiple unrelated systems writing the same key create ordering races and make failures impossible to reason about.

```luau
local Players = game:GetService("Players")
local closing = false
local active = {}

local function releasePlayer(player: Player)
    local profile = active[player]
    active[player] = nil
    if profile then
        profile:Release() -- wrapper-specific; use the project's actual API
    end
end

Players.PlayerRemoving:Connect(releasePlayer)

game:BindToClose(function()
    closing = true
    for player in Players:GetPlayers() do
        releasePlayer(player)
    end
end)
```

The example shows ownership, not a complete save library. Add timeouts, completion tracking, and an explicit policy for failed final saves.

## 8. ProfileStore integration (optional)

ProfileStore is a player-oriented wrapper, not a replacement for OrderedDataStore, MemoryStoreService, or global state. If a project uses it, follow its current lifecycle instead of layering a second lock protocol around it:

```luau
local Players = game:GetService("Players")
local ProfileStore = require(path.to.ProfileStore)

local TEMPLATE = { version = 1, coins = 0, inventory = {} }
local PlayerStore = ProfileStore.New("PlayerData", TEMPLATE)
local Profiles: {[Player]: any} = {}

local function loadPlayer(player: Player)
    local profile = PlayerStore:StartSessionAsync(tostring(player.UserId), {
        Cancel = function()
            return player:IsDescendantOf(Players) == false
        end,
    })

    if profile == nil then
        player:Kick("Your data session could not be opened. Please rejoin.")
        return
    end

    profile:AddUserId(player.UserId)
    profile:Reconcile()
    Profiles[player] = profile

    profile.OnSessionEnd:Connect(function()
        Profiles[player] = nil
        if player:IsDescendantOf(Players) then
            player:Kick("Your data session ended. Please rejoin.")
        end
    end)
end

local function releasePlayer(player: Player)
    local profile = Profiles[player]
    Profiles[player] = nil
    if profile then
        profile:EndSession()
    end
end

Players.PlayerAdded:Connect(loadPlayer)
Players.PlayerRemoving:Connect(releasePlayer)
```

The important behavior is the failure path. `StartSessionAsync()` can return `nil`; never treat that as a new empty profile. `Steal = true` bypasses session protection and belongs only in controlled debugging, not normal joins. Use `ProfileStore.Mock` in Studio when live API access is enabled but writes must remain ephemeral.

Use `profile:MessageAsync()` only for critical profile-targeted delivery, such as an offline paid gift that must be delivered later. For best-effort live announcements, use MessagingService instead. Profiles also expose critical-state and error signals; route them to observability rather than silently continuing as if saves were healthy.

## 9. Data safety checklist

- [ ] A failed load cannot overwrite an existing record with defaults.
- [ ] One server owns a mutable player profile at a time.
- [ ] Store keys and schema versions are stable and documented.
- [ ] `UpdateAsync` is used for read-modify-write operations.
- [ ] Retries are finite, backoff is bounded, and failures are observable.
- [ ] Migrations are idempotent and tested against old records.
- [ ] Player removal and server shutdown release or save profiles.
- [ ] No client-provided value bypasses server validation before persistence.
