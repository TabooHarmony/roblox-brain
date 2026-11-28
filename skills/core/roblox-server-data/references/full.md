# Roblox Server & Shared Data: Full Reference

> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

## OrderedDataStore

### Overview

OrderedDataStore is a sortable variant of DataStore. Keys are strings, while values are integers used for ordering. Use a stable string key such as `tostring(UserId)` for player leaderboards.

### API

| Method | Purpose |
|--------|---------|
| `GetSortedAsync(ascending, pageSize, minValue, maxValue)` | Get sorted pages of entries |
| `SetAsync(key, value)` | Set a key's value (key is a string; value is an integer) |
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
        coinStore:SetAsync(tostring(userId), coins)
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
- Keys MUST be strings; use a stable representation such as `tostring(player.UserId)`
- Values must be integers used for sorting; do not store strings, tables, or nested data
- Separate from player DataStore (different key space, different purpose)
- `GetSortedAsync` returns pages, not a flat list; use pagination
- Rate limits apply same as regular DataStores

### Batch reads: `BatchGetAsync`

`GlobalDataStore:BatchGetAsync(keys, options?)` retrieves multiple ordered-data-store keys in a single request. Per the docs it is currently only supported on `OrderedDataStore`; calling it on a standard `GlobalDataStore` or `DataStore` throws an error. Unlike `GetAsync`, it returns no `DataStoreKeyInfo`, because ordered stores do not support versioning or metadata. <!-- temporal: 2026-09 -->

- Returns a dictionary mapping each key to a table with a `value` field (for example `coins = { value = 100 }`).
- Keys that do not exist or have empty values are omitted from the result, not returned as nil.
- The `keys` array needs at least one key, at most a server-configured maximum (default 100). Exceeding it throws.
- Each call counts against the ordered read budget based on the number of keys requested.

```luau
local keys = {"player_111", "player_222", "player_333"}
local success, results = pcall(function()
    return coinStore:BatchGetAsync(keys)
end)
if success then
    for _, key in keys do
        local entry = results[key]
        if entry then
            print(key .. " : " .. tostring(entry.value))
        else
            print(key .. " has no saved entry")
        end
    end
end
```

### Reading request budgets

`DataStoreService:GetRequestBudgetForRequestType(requestType)` returns the number of requests the current place can still make for a `DataStoreRequestType` (for ordered stores: `OrderedRead`, `OrderedWrite`, `OrderedList`, `OrderedRemove`). Requests beyond the budget are throttled. Poll it before bursts instead of assuming quota headroom; ordered writes default to only 30 + numPlayers x 5 per minute per server.

```luau
local function waitForBudget(requestType: Enum.DataStoreRequestType)
    while DataStoreService:GetRequestBudgetForRequestType(requestType) <= 0 do
        task.wait(1)
    end
end

waitForBudget(Enum.DataStoreRequestType.OrderedWrite)
```

Quota formulas (read, write, list, remove; experience-level and per-server) and the rest of the limits tables are in the `roblox-data` full reference, section Limits and quotas.

### Leaderboard Alternatives: Cached DataStore

OrderedDataStore is the canonical primitive, but a leaderboard can instead be stored in a standard `DataStore` kept fully loaded in memory, with writes coalesced into batched `UpdateAsync` saves. This "cached board" model trades storage size and in-memory footprint for O(1) rank lookup of arbitrary players (OrderedDataStore only exposes ~100 entries/page) and lets you define custom ordering and non-integer/custom value types. Prefer it when arbitrary-player rank lookup, custom ranking, or API-request throttling (batching many queued saves into a few writes) outweigh a smaller, paginated board. Community leaderboard modules (e.g. Leaderboards+, https://devforum.roblox.com/t/leaderboards-the-ultimate-module-for-global-leaderboards/4706939) are a lead for this pattern.

## MessagingService

### Overview

Real-time communication between server instances. Fire-and-forget: no delivery guarantee, no ordering guarantee.

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
- Messages are fire-and-forget; design for idempotency
- No ordering guarantee; handle out-of-order messages gracefully
- Rate limit: 600 + 240 * (players in server) messages per minute
- Message size limited; keep payloads small
- `message.Data` contains the published payload
- Subscribe callbacks run in a separate thread; wrap them in pcall

### Receive limits and capacity planning <!-- temporal: 2026-10 -->

Send limits are per-server, but **receive** limits scale with server count and bind the whole game.
Current official limits (per minute unless noted; subject to change):

| Limit | Value |
|-------|-------|
| Messages sent per game server | 600 + 240 × players in server |
| Messages received per topic | 40 + 80 × number of servers |
| Messages received for entire game | 400 + 200 × number of servers |
| Subscriptions per game server | 20 + 8 × players in server |
| Subscribe requests per game server | 240 |
| Topic / message size | 80 chars / 1 KiB |

Planning consequences:

- **Compute the receive budget at your max server count before choosing a fan-out design.** A
  broadcast topic's per-topic cap (40+80×N) grows slower than the demand from N servers each
  publishing, and the game-wide cap (400+200×N) is shared by *every* topic. At 100 servers the
  game-wide cap is 20,400 msgs/min; a single hot topic at 90 servers caps at 7,240/min.
- **The subscriber count is also capped** (20+8×players per server): own and clean up subscriptions; avoid creating duplicate subscriptions for every player.
- **Subscribe churn is throttled separately** (240 req/min per server): reconnect storms after
  throttling must back off, not retry in a loop.
- Prefer *pull over push* at scale: instead of broadcasting state to every server, hold shared state
  in MemoryStore and let servers read on demand; reserve MessagingService for low-frequency events.
- Handle `PublishAsync` errors with bounded backoff. Do not infer non-delivery from a missing acknowledgement; retries must use the same idempotency key (see the ack pattern above).

## GlobalDataStore

### Overview

GlobalDataStore is the same DataStore API but used for shared, non-player state. No session locking. Use `UpdateAsync` for atomic operations on shared counters.

### Guild/Clan Data Pattern

```luau
local DataStoreService = game:GetService("DataStoreService")
local guildStore = DataStoreService:GetDataStore("GuildData")

-- Tagged outcome so failure and absence stay distinct:
-- (true, data) -> read succeeded, guild exists
-- (true, nil)  -> read succeeded, guild not created yet (legitimate nil)
-- (false, err) -> DataStore outage; do NOT treat this as "no guild"
-- Never silently return nil on error.
local function getGuild(guildId: string): (boolean, any)
    return pcall(function()
        return guildStore:GetAsync("guild_" .. guildId)
    end)
end

local ok, data = getGuild("guild123")
if not ok then
    -- DataStore failure: retry, back off, or serve stale cache. Do not create/overwrite.
elseif data then
    print("guild name", data.name)
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

-- Tagged outcome: returns (false, err) instead of just failing silently; the
-- caller decides whether to retry, queue, or alert. Errors are preserved, not swallowed.
local function incrementCounter(name: string, delta: number): (boolean, any)
    local ok, err = pcall(function()
        counterStore:UpdateAsync("counter_" .. name, function(oldValue)
            return (oldValue or 0) + delta
        end)
    end)
    if not ok then
        warn(("counter increment failed for %s: %s"):format(name, tostring(err)))
    end
    return ok, err
end
```

### Key Rules
- Always use `UpdateAsync` for shared state: `SetAsync` can lose updates
- Never store Instances; serialize to primitives
- Same rate limits as player DataStores
- No session locking, so don't use it for player data
- Key naming: use prefixes to namespace (`guild_`, `counter_`, `season_`)
- Read helpers must preserve failure information: tag outcomes (ok/error/missing) or return `(success, data-or-err)`; never collapse an outage into nil, and never synthesize authoritative-looking fallback data on a failed read
- Cross-owner atomicity: per-key atomicity does not span profiles or services; for the two-profile exchange limit, quiescence, and recovery patterns, see `roblox-data` full reference, section Cross-owner atomicity limits

## MemoryStoreService

MemoryStore is for temporary, high-throughput coordination. Its values expire, so it is a poor place for authoritative player progress or a permanent leaderboard.

### Quotas and request-unit budgeting <!-- temporal: 2026-10 -->

All MemoryStore quotas apply at the **game level, not per server** — every server in the experience
draws from the same pool, so a fleet of servers sharing one hot structure can throttle each other.

| Quota | Value | Notes |
|-------|-------|-------|
| Request units | 1000 + 120 × concurrent users per minute | Applies to every `MemoryStoreService` API call, game-wide |
| Memory size | 64 KB + 1.2 KB × users | Users leaving take ~8 days to stop counting (traceback period) |
| Structure size | 100 MB / 1,000,000 items | Per sorted map or queue |
| Item value | 32 KB | Shard, compress, or split values beyond this |
| Default TTL | 45 days | For `AddAsync`/`SetAsync`; set the shortest workable expiry so eviction frees quota |

Request-unit costs are **not uniform** — batch-style calls bill per result, which is where budgets
break:

- `SortedMap:GetRangeAsync()` and `Queue:ReadAsync()`: one unit **per returned item** (empty result =
  1 unit); a queue read also consumes +1 unit every 2 s while it waits on `waitTimeout`.
- `HashMap:UpdateAsync()`: minimum 2 units.
- `HashMap:ListItemsAsync()`: partitions scanned + items returned.

Planning rules:

- Budget request units against the **game-level** formula (1000+120×CCU), not a per-server number. At
  high CCU the shared budget can still be consumed by many independent polling loops; account for
  per-item charges and waiting reads, not just calls.
- For high-frequency reads, a per-item-billed range read is the expensive path — keep page sizes
  small, and prefer hash-map `GetAsync` (1 unit) over wide range scans where a key lookup suffices.
- When the memory quota is hit, writes fail while reads/deletes succeed: expire aggressively and
  delete processed queue items promptly, or new `AddAsync` calls fail until eviction.
- Request-unit throttling raises an error response; treat it like the queue retry cases below —
  back off game-wide, since retrying from more servers makes the shared shortage worse.

### Queue pattern

Processor contract: `processMatchRequest(request)` returns `true` only when the
batch's durable effect has fully succeeded, and returns `false` or throws when
it has not. `drain` removes the read batch only when every request returned
`true`. If any request fails, the whole batch stays queued; redelivery must be
safe, so processing stays idempotent and includes a stable request identifier.

```luau
local MemoryStoreService = game:GetService("MemoryStoreService")
local queue = MemoryStoreService:GetQueue("Matchmaking", 30)

local function enqueue(request: table)
    return pcall(function()
        queue:AddAsync(request, 60, 0)
    end)
end

-- Contract: processMatchRequest(request) returns true on success.
-- Returning false or throwing means "did not complete"; drain then
-- keeps the batch queued instead of removing it.
local function drain(maxItems: number): (boolean, any)
    local ok, items, readId = pcall(function()
        return queue:ReadAsync(maxItems, false, 0)
    end)
    if not ok then
        -- items holds the error message here; propagate it instead of
        -- returning silently and losing the failure.
        return false, items
    end

    local allSucceeded = true
    for _, request in items do
        -- Capture BOTH pcall's ok AND the processor's return value: the
        -- contract is "returns true on success", so a false return is a
        -- failed batch too. Capturing only pcall's first result lets a
        -- false-returning processor have its batch removed anyway.
        local requestOk, processed = pcall(function()
            return processMatchRequest(request)
        end)
        if not requestOk or processed ~= true then
            allSucceeded = false
        end
    end

    -- Remove only when every request durably succeeded. A failed batch is
    -- left queued (invisible until the timeout expires) and must be safe
    -- to redeliver: process idempotently.
    if allSucceeded and #items > 0 then
        local removed = pcall(function()
            queue:RemoveAsync(readId)
        end)
        if not removed then
            return false, "batch processed but RemoveAsync failed; it will be redelivered"
        end
    elseif not allSucceeded then
        return false, "one or more requests failed; batch left queued"
    end
    return true
end
```

### Queue retries and duplication

`ReadAsync` makes items temporarily invisible to other readers. A crashed worker can therefore leave work to reappear later. Make processing idempotent, include a request or match identifier, and remove an item only after the durable or teleport-side effect has succeeded. Keep the invisibility timeout long enough for the work but short enough to recover from a dead server.

Two failure classes live inside "processing failed":

- **The work clearly did not happen**: retry only transient failures and normally let the original item become visible again. Do not re-add it while the original remains queued. Terminal validation failures need an explicit discard/dead-letter policy.
- **The outcome is unknown** (the handler acted, then the server crashed, or the durable write timed out): re-adding and reprocessing may duplicate the effect. The guard is an **idempotency key inside the payload** (or a durable done-marker keyed by it), not careful timing: the processor must be able to detect "this request id already completed" and return success without repeating the effect. Redelivery after a crash then collapses to a no-op instead of a double grant.

Queue retries after a successful `RemoveAsync` are a contradiction: removal is the success signal, and a failed `RemoveAsync` means the batch will be redelivered — so removal failures are retried (they leave the work queued), while *post-success* retries must never exist for the effect itself.

### Sorted-map mechanics

Use a sorted map for short-lived records keyed by a stable identifier, such as server heartbeats or matchmaking candidates. Set an expiration on every entry and clean stale values when reading. Do not confuse a sorted map with `OrderedDataStore`: MemoryStore entries expire and are intended for coordination, not historical persistence.

```luau
local MemoryStoreService = game:GetService("MemoryStoreService")
local map = MemoryStoreService:GetSortedMap("ActiveServers")

-- Writes carry the sort key: SetAsync(key, value, expiration, sortKey).
local ok = pcall(function()
	map:SetAsync(serverId, { players = #game.Players:GetPlayers() }, 45, 0)
end)

-- Paging uses exclusive bounds built from the LAST returned item's key and
-- sortKey, not a page index. Advance the bound after each page;
-- repeating the previous bound fetches the same range again.
-- This is a moving live view, not a consistent multi-page snapshot.
local exclusiveLowerBound = nil -- nil = start from the very first item
while true do
	local okRead, items = pcall(function()
		return map:GetRangeAsync(Enum.SortDirection.Ascending, 100, exclusiveLowerBound)
	end)
	if not okRead or #items == 0 then break end
	for _, item in items do
		-- item.key, item.value, item.sortKey
	end
	if #items < 100 then break end -- short page = end of map
	exclusiveLowerBound = { key = items[#items].key, sortKey = items[#items].sortKey }
end
```

Cursor facts that break naive implementations:

- For the cursor pattern above, use `{ key = ..., sortKey = ... }` from the last item. The API also accepts a bound with just one field. Ascending pages advance the exclusive lower bound; descending pages advance the exclusive upper bound. A cursor identifies the composite ordering position, not two independent exclusion tests.
- A short page (`#items < count`) is the end-of-map signal. Do not loop until the bound errors.
- Sort keys are numbers or strings, not booleans. Numeric sort keys precede strings, which precede missing sort keys; ties use the item's string key. Keep the sort-key type consistent per map.
- **Heartbeat pattern**: heartbeat = short expiry (tens of seconds) + the owning server re-`SetAsync`ing its entry on a fixed interval. Cleanup-on-close is an optimization, not the correctness guarantee — crash expiry is what removes a dead server's entry.

### Choosing a cross-server store (decision table)

| Need | Use | Why not the alternatives |
|---|---|---|
| Persistent player/profile records | `DataStore` | MemoryStore expires; MessagingService is not state |
| Rank queries over persistent data | `OrderedDataStore` | values must be integers; no versioning |
| Live ordered views, leases, presence, tickets (TTL) | MemoryStore **sorted map** | DataStore has no TTL-sorted listing |
| Point lookups on live data; paged enumeration with `ListItemsAsync` | MemoryStore **hash map** | sorted map adds sort cost you don't need |
| Signals/commands between live servers | `MessagingService` | all stores are state, not delivery |
| Hot-key contention | shard by key prefix + virtual shards | single-key writes serialize |

Choose sharding from measured contention, request budgets, and documented store limits; do not infer hidden partition boundaries from an item count.

### MessagingService request/response (ack pattern)

Broadcast and migration notifications above are fire-and-forget. When a server must know whether another server *acted* on a command, add correlation and treat "no ack" correctly. The following sender/receiver fragments are illustrative, not one runnable script: install subscriptions before publishing, validate payloads and routing, protect API calls with `pcall`, and own subscription/task cleanup.

```luau
local pending = {} -- reqId -> { sentAt = os.clock() }

-- Sender
local reqId = HttpService:GenerateGUID(false)
pending[reqId] = { sentAt = os.clock() }
MessagingService:PublishAsync("PartyInvite", { reqId = reqId, toUserId = toUserId, kind = "invite" })

-- Receiver (other server): validate, act, ack the same correlation id
MessagingService:SubscribeAsync("PartyInvite", function(message)
	local data = message.Data
	if data.kind == "inviteAck" then
		local p = pending[data.reqId]
		if p then pending[data.reqId] = nil end
		return
	end
	-- ... validate and act on the invite, then:
	MessagingService:PublishAsync("PartyInvite", { reqId = data.reqId, kind = "inviteAck", accepted = accepted })
end)

-- Sender timeout sweep: unknown outcome, not "receiver did nothing"
task.spawn(function()
	while true do
		for reqId, p in pending do
			if os.clock() - p.sentAt > ACK_TIMEOUT then
				pending[reqId] = nil
				-- Absence of an ack does NOT mean the command was not executed:
				-- the receiver may have acted and died before acking. The effect
				-- itself must therefore be idempotent by reqId, so the recovery
				-- path can replay the same operation safely instead of guessing
				-- which side of the act/ack gap the failure landed on.
			end
		end
		task.wait(1)
	end
end)
```

Design consequence: because the ack channel is best effort, the *operation* must be idempotent by correlation id. A timeout-retry must be able to replay the same operation without double-granting; for value-granting operations, keep the durable receipt pattern of `roblox-monetization` (grant and record the id in one durable operation, ack only after persistence).

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

-- Tagged outcome: (true, data) on a successful read, (false, err) on failure.
-- A successful read with nil data means no season has been written yet.
-- Never synthesize a fallback season here: fabricated data ({ season = 1, ... })
-- gets consumed as authoritative and silently corrupts rewards and schedules.
local function getSeasonInfo(): (boolean, any)
    return pcall(function()
        return seasonStore:GetAsync("current_season")
    end)
end

local ok, season = getSeasonInfo()
if not ok then
    -- Read failed: retry, serve a cached copy, or fail the request.
    -- Do not fall back to invented season state.
elseif season then
    -- Normal path: use the stored season data.
else
    -- Read succeeded but no season exists yet: bootstrap the first season
    -- with an explicit write, don't fabricate one for this request.
end
```

## Native PlayerList leaderboards (official)

<!-- temporal: 2026-11 -->

The PlayerList has three views:

- **Here** reads `leaderstats` for players in the current server.
- **Friends** and **Global** (beta) read one OrderedDataStore that you register in Creator Hub.

Rules for the persistent views:

- Each player has one numeric score, keyed by user ID.
- Your server code writes the scores. The platform never writes them.
- Each experience can have one active persistent leaderboard. Deactivating it hides the leaderboard but keeps the data.

To use them, keep writing the same OrderedDataStore your own boards use, keyed by `tostring(player.UserId)`, and register it.

You still need your own UI for weekly or seasonal boards.

## Weekly boards keyed by ISO week

This pattern was observed in one project.

- **Key a new OrderedDataStore per ISO week in UTC**, for example `KillsWeek_2026-W48`.
  - Use the ISO year, not the calendar year: 1 January 2027 falls in week 2026-W53.
  - Credit each score to the week it happened, even when the flush runs after the reset.
- **Batch increments per store and player.** Flush on a timer, on `PlayerRemoving`, and in `BindToClose`. Keep failed or over-budget writes in the batch for the next flush.
- **Read the top pages on a timer into a server cache.** Show a player's own count as the stored value plus their unflushed batch.
- **In Studio, swap in an in-memory store with the same methods**, so playtests never touch real boards.

```luau
-- Illustrative ISO-8601 week key (UTC); unit-test the year boundaries.
local function isoWeekKey(prefix: string, unix: number): string
	local t = os.date("!*t", unix) :: any
	local wday = (t.wday + 5) % 7 + 1 -- Monday = 1 ... Sunday = 7
	-- The Thursday of this week decides the ISO year.
	local thursday = unix + (4 - wday) * 86400
	local th = os.date("!*t", thursday) :: any
	local week = math.floor((th.yday - 1) / 7) + 1
	return string.format("%s_%d-W%02d", prefix, th.year, week)
end
```

Test it against known dates: 2026-12-31 → 2026-W53 and 2027-01-04 → 2027-W01.

## MemoryStore quota recovery and scopes (official)

<!-- temporal: 2026-11 -->

- **At the quota, writes that would increase usage fail.** Set expirations so usage falls on its own.
- **To recover, flush the scope through Open Cloud**: `POST https://apis.roblox.com/cloud/v2/universes/{universeId}/memory-store:flush?scope=LIVE` (or `TEST`; the default is `LIVE`).
  - A flush clears **every** queue, sorted map, and hash map in that scope.
  - It's a long-running operation. Poll Get Memory Store Flush Operation until it's done. The returned operation path already includes `cloud/v2`, so don't prepend it again.
- **Studio and production use isolated scopes.** Studio tests can't see live data.
- **Extended Services can raise the quota**, with throttling at the budget.
- **Return values:**
  - `MemoryStoreHashMap:SetAsync` returns a boolean: `true` means it overwrote an existing key.
  - `MemoryStoreSortedMap:GetSizeAsync` returns the item count.

## MessagingService from outside the game (official)

`MessagingService:PublishAsync` has an Open Cloud equivalent: `POST /cloud/v2/universes/{universeId}:publishMessage`.

Messages published that way reach live servers, but not Studio playtests (observed). Test a messaging-driven LiveOps action, such as a compensation grant, on a private live server. Announce it before you send, because it reaches real players. Keys and scopes are in `roblox-cloud`.

## Pitfalls

- **MessagingService delivery**: not guaranteed. If a server misses a message, it's gone. Design for eventual consistency.
- **GlobalDataStore rate limits**: same as player DataStores. Don't use for high-frequency updates.
- **OrderedDataStore key type**: must be a string, such as `tostring(UserId)`. Values must be integers used for sorting.
- **Lost updates with SetAsync**: always use `UpdateAsync` for shared state. `SetAsync` overwrites without reading.
- **Serialization**: DataStores only store JSON-compatible types (string, number, boolean, table, nil). No Instances, no functions, no userdata.
- **Cross-server timing**: MessagingService has latency. Don't rely on it for time-critical operations.
- **RTBF template matching**: leaderboard keys that embed the user ID as a static string (for example `player_<UserId>`) can be matched by automated right-to-be-forgotten deletion templates; hashed or random keys cannot, making erasure manual. See the `roblox-data` full reference, section Right-to-be-forgotten deletion templates.

## User identity in shared data

Keep leaderboard keys and cross-server payloads on a documented, consistent identity scheme; don't mix `UserId`-based keys with domain-scoped `User.Id` keys. For the identity distinction, serialization, and migration implications, see `roblox-data` §1a.

## Feature-state and operational-delivery checks

- Define configuration precedence and behavior for an explicit true, explicit false, absent key, failed read, cached value, and first server startup. If absence falls back to a code default, do not encode an intentional enabled state merely by deleting its override. Choose a safe initial state for each feature; a parked feature must not become active transiently during a failed read.
- Include persisted overrides in release and rollback manifests. Test cold start with failed configuration access, later successful refresh, and code-default changes; report the observed state of serving servers separately from the desired control-plane state.
- Name operational stages separately: command accepted, server executed, message dispatched, client rendered, and user acknowledged. A backend or server acknowledgement proves only its own stage. Verify display on the intended viewport with representative text length and duration before claiming the player saw an announcement; treat human acknowledgement as unknown unless it was actually collected.
