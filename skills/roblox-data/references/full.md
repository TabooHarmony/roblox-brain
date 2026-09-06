# roblox data persistence: full reference

> Code examples are illustrative. Adapt them to your project and verify in Studio before production use.

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
    -- Deep-construct: table.clone(TEMPLATE) is shallow and would alias the
    -- nested `inventory` and `settings` tables across every profile built
    -- from the template (mutating one player's inventory would corrupt all).
    local data = table.clone(TEMPLATE)
    data.inventory = {}
    data.settings = table.clone(TEMPLATE.settings)
    return data
end
```

Every nested table must be rebuilt per call so no two profiles share a subtable. Write a small deep-copy helper or construct nested defaults explicitly; after loading, never mutate nested tables that might still be shared with the template. Never store Instances, functions, connections, threads, cyclic references, or values the DataStore serializer cannot represent.

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

Use `UpdateAsync` when the new value depends on the stored value. The transform should be deterministic, small, and safe to run more than once if the service retries it. The migration it runs must already be in scope, so define `migrate` before this function (see the migration snippet in `## 6. Migration`):

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

local function addCoins(userId: number, amount: number): boolean
    -- Reject NaN, infinity, non-integers, and out-of-range amounts.
    if amount ~= amount or amount == math.huge or amount == -math.huge then
        return false
    end
    if amount % 1 ~= 0 or amount < 0 or amount > 1_000_000 then
        return false
    end

    local ok, committed = pcall(function()
        return store:UpdateAsync("player_" .. tostring(userId), function(old)
            -- Migrate BEFORE mutating: stamping the version without running
            -- migrations would mark an old record as current while its fields
            -- are still missing, and would silently downgrade a future record.
            if old ~= nil then
                if type(old) ~= "table" then
                    return nil -- unsupported shape: cancel the write, escalate
                end
                local version = tonumber(old.version) or 0
                if version > CURRENT_VERSION then
                    return nil -- future schema: cancel the write, do not downgrade
                end
            end
            local data = migrate(old)
            data.coins = (data.coins or 0) + amount
            data.version = CURRENT_VERSION -- stamp only after migration
            return data
        end)
    end)
    -- A cancelled transform (nil return) makes UpdateAsync return nil: the
    -- write never happened, so report failure even though pcall succeeded.
    -- Returning the bare pcall flag would report success without granting.
    return ok and committed ~= nil
end
```

Do not perform network calls, yield, or mutate external state inside the transform callback. If the callback returns `nil`, the update is cancelled and the stored value remains unchanged; use that deliberately for unsupported schemas. A cancelled or failed write must surface to callers and observability rather than silently reporting success.

## 5a. Cross-owner atomicity limits

The guarantees above are per profile. One `UpdateAsync` either commits its whole transform or none of it, and one session owner serializes writes to one key. None of that extends across profiles, across keys, or across services. Name the boundary in any design that crosses it:

- **Atomic receipt recording for one profile is not an atomic exchange between two profiles.** A receipt ID and its grant can be one durable write for one key. There is no DataStore primitive that debits one profile and credits another in a single commit, so any transfer is two or more independent writes with a crash window between them. The same limit applies to a profile paired with any other durable record, such as a shared guild store or global counter (see `roblox-server-data`).
- **A proposed multi-owner transfer must either explicitly exclude the guarantee or show a durable operation identity plus recovery state.** Excluding it means the design states that a crash between the two writes loses or duplicates value. Supporting it means writing a transfer record with a stable operation ID, both owners, the amount, and a state field before the first mutation, so recovery can find half-completed transfers and finish or reverse them. A small idempotent operation record like this is enough; no generic transaction framework is required or assumed.
- **Administrative or external mutation must coordinate with the active owner.** An Open Cloud write, backend script, or manual editor fix applied while a live server still owns the session will be overwritten by that owner's next save. Either route the change through the active owner, or use a documented quiescence protocol: confirm the session is released and cannot be re-acquired mid-repair, mutate, then let the next owner load the repaired data (see `roblox-cloud` for the API-key side).
- **Webhook acceptance is not completion.** For Roblox webhooks received off-platform, durable acceptance and deduplication must not acknowledge away an event before its work is recoverable. If the dedup marker is durable but the grant or enqueue behind it is not, the success response converts a retryable delivery into silent loss (see `roblox-cloud`).

### Worked failure sequence

Each case names its recovery owner, or is labeled unsupported.

**(a) Debit committed, credit absent.** A transfer debits player A, then the server crashes before crediting player B. Recovery owner: the transfer coordinator, through the durable operation record written before the debit. Recovery is a restart or periodic sweep that reads `pending` records, checks both profiles against the operation ID, and completes the credit or refunds the debit, then marks the record `done` or `reversed`. Every step must be idempotent by operation ID so a crash during recovery is safe to retry. Without such a record this flow is unsupported: two session-locked profiles cannot be reconciled after the crash, and the design must document that exclusion instead of shipping the loss.

```luau
-- Durable operation identity, illustrative shape only
local transfer = {
    id = "xfer_0f3e",   -- stable operation ID, generated once
    from = 111,
    to = 222,
    amount = 500,
    state = "pending",  -- pending -> done | reversed
}
-- 1. Write the transfer record durably before any mutation.
-- 2. Debit A via UpdateAsync (skip if already debited for this id).
-- 3. Credit B via UpdateAsync (skip if already credited for this id).
-- 4. Mark the record done.
-- Recovery: sweep pending records and resume at the first incomplete step.
```

**(b) Owner save after external repair.** A support script repairs a value through Open Cloud while player A's live server still owns the session. The owner's next autosave writes its stale in-memory copy and the repair is gone. Coordination requirement: the actor performing the external mutation is the recovery owner and must quiesce the session first, meaning verify the lock is released, prevent re-acquisition during the repair window, apply the fix, then let the next owner load. If quiescence is impossible, the mutation must be routed through the active owner instead; writing anyway does not risk the loss, it guarantees it.

**(c) Dedup written, enqueue absent.** A webhook receiver records the notification ID in a durable dedup store, then crashes before the grant or enqueue is durable. If Roblox redelivers, the dedup hit drops the event: acknowledged but never acted on. Recovery owner: the receiver's own worker, and the fix is ordering. Make the work record itself the dedup record by writing the job or grant keyed by notification ID in one durable write before acking, or write the work record first and keep the worker idempotent by notification ID. A durable work record without an ack is safe, because the worker can still process or retry it; the reverse order is the loss.

## 6. Migration

Migrate data after it is loaded and before gameplay sees it. Each migration should be small, ordered, and testable; the `migrate` shown with `addCoins` in `## 5. Atomic updates` is the pattern:

Stamping the version is part of each migration step, never a substitute for it: a write that bumps `version` without running the migrations leaves fields missing while the record claims to be current. Conversely, if a stored version is newer than `CURRENT_VERSION`, refuse the write rather than overwriting unknown schema. Keep old-field handling until every supported record has migrated or until a deliberate data-retention policy says it can be removed. Test migrations against missing fields, old nested shapes, extra fields, and malformed values.

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

-- Supplying a Cancel callback disables ProfileStore's built-in acquisition
-- timeout, so the example enforces its own bounded deadline.
local ACQUISITION_TIMEOUT = 30

local function loadPlayer(player: Player)
    local startedAt = os.clock()
    local profile = PlayerStore:StartSessionAsync(tostring(player.UserId), {
        Cancel = function()
            -- Called repeatedly while the session waits to acquire the lock.
            -- `closing` is a shutdown flag set inside BindToClose (see the
            -- Save lifecycle section).
            return player:IsDescendantOf(Players) == false -- player left
                or closing -- stop acquiring during shutdown
                or os.clock() - startedAt > ACQUISITION_TIMEOUT -- deadline elapsed
        end,
    })

    if profile == nil then
        -- Bounded acquisition failure: the player left, the server is
        -- shutting down, or the deadline elapsed under contention. Do not
        -- treat nil as a new empty profile, and do not assume the abandoned
        -- acquisition is interrupted instantly. Proceed without a profile
        -- (limited or read-only mode) or kick, per the project's policy.
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

The important behavior is the failure path. `StartSessionAsync()` can return `nil`; never treat that as a new empty profile. Supplying a `Cancel` callback also disables ProfileStore's built-in acquisition timeout, so a custom `Cancel` must include its own elapsed-time deadline; without one, a connected player contending for a locked profile can wait forever. Keep the deadline bounded and define what happens on failure (proceed without a profile or kick). `Steal = true` bypasses session protection and belongs only in controlled debugging, not normal joins. Use `ProfileStore.Mock` in Studio when live API access is enabled but writes must remain ephemeral.

Use `ProfileStore:MessageAsync(profileKey, message)` only for critical profile-targeted delivery, such as an offline paid gift that must be delivered later, and receive it with `profile:MessageHandler(...)`. For best-effort live announcements, use MessagingService instead. Profiles also expose critical-state and error signals; route them to observability rather than silently continuing as if saves were healthy.

## 9. Data safety checklist

- [ ] A failed load cannot overwrite an existing record with defaults.
- [ ] One server owns a mutable player profile at a time.
- [ ] Store keys and schema versions are stable and documented.
- [ ] `UpdateAsync` is used for read-modify-write operations.
- [ ] Retries are finite, backoff is bounded, and failures are observable.
- [ ] Migrations are idempotent and tested against old records.
- [ ] Template-derived profiles never share nested default tables.
- [ ] Version stamps are only written after migrations run; records newer than `CURRENT_VERSION` are rejected, not downgraded.
- [ ] Custom session-acquisition `Cancel` callbacks include an explicit elapsed-time deadline.
- [ ] Player removal and server shutdown release or save profiles.
- [ ] No client-provided value bypasses server validation before persistence.
- [ ] Persisted numbers are checked for NaN/infinity; persisted strings pass `utf8.len`.
- [ ] Client-supplied nested tables are re-validated field by field before saving.

Before destructive tests (wipe scripts, migration replays, bulk-key writes), confirm the actual destinations: exact DataStore, OrderedDataStore, and MemoryStore names, plus Open Cloud endpoints or webhooks the code calls. A test-place label is not isolation; a shared store name reaches production records. Keep a mutation record with a compensating action per `roblox-studio-mcp`.

## Community ecosystem (leads, not sources)

Top-sorted DevForum canon for datastore libraries. Verify current status in-thread before recommending; do not lift code without license.

- Lineage: [DataStore2](https://devforum.roblox.com/t/how-to-use-datastore2-data-store-caching-and-data-loss-prevention/136317) (2018, historical) → [ProfileService](https://devforum.roblox.com/t/save-your-player-data-with-profileservice-datastore-module/667805) (2020) → [ProfileStore](https://devforum.roblox.com/t/profilestore-save-your-player-data-easy-datastore-module/3190543) (2024, current standard; already integrated above).
- [Stop using SetAsync()](https://devforum.roblox.com/t/stop-using-setasync-to-save-player-data/276457) — the canonical anti-pattern post; session-locking rationale.
- [Suphi's DataStore Module](https://devforum.roblox.com/t/suphis-datastore-module/2425597) — lighter alternative; [DataDelve](https://devforum.roblox.com/t/datadelve-%E2%80%94-easy-free-datastore-editor/3067950) — free datastore editor for debugging live data.
- [DataPredict](https://devforum.roblox.com/t/datapredict%E2%84%A2-3-years-release-242-revenue-game-optimization-using-machine-learning-deep-learning-and-reinforcement-learning-100-models/2196446) — ML toolkit on datastore analytics, relevant to `roblox-analytics`/growth work.
