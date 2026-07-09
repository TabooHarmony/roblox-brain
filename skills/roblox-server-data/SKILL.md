---
name: roblox-server-data
description: "Use for Roblox server or cross-server data: OrderedDataStore leaderboards, MessagingService, world state, seasons, or guilds."
last_reviewed: 2026-07-04
sources:
  - https://create.roblox.com/docs/reference/engine/classes/OrderedDataStore
  - https://create.roblox.com/docs/reference/engine/classes/MessagingService
  - https://create.roblox.com/docs/reference/engine/classes/GlobalDataStore
---

# Roblox Server & Shared Data

## When to Load

Load for server-level or cross-server data: leaderboards (OrderedDataStore), cross-server messaging (MessagingService), shared world state, persistent non-player data, season/guild data. For player data (DataStore, ProfileStore, session locking), use `roblox-data`.

## Quick Reference

### OrderedDataStore (Leaderboards)
- Sortable DataStore. Keys must be positive integers (use UserId).
- `GetSortedAsync(ascending, pageSize, minValue, maxValue)` → sorted pages
- For leaderboards ONLY — not player data

```luau
local store = DataStoreService:GetOrderedDataStore("LeaderboardCoins")
store:SetAsync(player.UserId, playerCoins)
local top10 = store:GetSortedAsync(false, 10):GetCurrentPage()
```

### MessagingService (Cross-Server)
- Real-time communication between server instances
- `SubscribeAsync(topic, callback)` / `PublishAsync(topic, message)`
- No delivery guarantee — design for idempotency

```luau
MessagingService:SubscribeAsync("ServerShutdown", function(msg) print(msg.Data) end)
MessagingService:PublishAsync("ServerShutdown", "server-" .. game.JobId)
```

### GlobalDataStore (Shared State)
- Non-player shared state: guild data, season config, global counters
- Same API as DataStore but different conceptual use
- Use `UpdateAsync` for atomic read-modify-write (prevents race conditions)
- Never use for player data — no session locking

### Persistent World State Patterns
- **Building/construction games**: serialize player-built structures to DataStore, reload on join
- **Season/leaderboard data**: OrderedDataStore for rankings, GlobalDataStore for season metadata
- **Guild/clan data**: GlobalDataStore with guild ID as key, MessagingService for real-time guild chat
- **Economy counters**: GlobalDataStore for server-wide currency totals, UpdateAsync for atomic increments

### Cross-Server Patterns
- Server registration: publish server info on start, heartbeat on interval
- Player migration: notify old server to release locks via MessagingService
- Global events: publish to all servers, each handles locally

### Pitfalls
- MessagingService is fire-and-forget — no delivery guarantee, no ordering
- GlobalDataStore has same rate limits as player DataStores — don't spam
- OrderedDataStore keys MUST be positive integers (use UserId)
- Never store Instances — serialize to primitives first
- UpdateAsync for any shared counter to prevent lost updates

**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
