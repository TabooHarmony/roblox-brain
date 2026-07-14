---
name: roblox-server-data
description: "Use for Roblox server or cross-server data: OrderedDataStore leaderboards, MessagingService, world state, seasons, or guilds."
last_reviewed: 2026-07-13
sources:
  - https://create.roblox.com/docs/reference/engine/classes/MemoryStoreService
  - https://create.roblox.com/docs/reference/engine/classes/MemoryStoreQueue
  - https://devforum.roblox.com/t/partyservice-plus-party-matchmaking-framework/4668883
---

# Roblox Server & Shared Data

## When to Load

Load for server-level or cross-server data: leaderboards (OrderedDataStore), cross-server messaging (MessagingService), temporary queues and sorted maps (MemoryStoreService), shared world state, persistent non-player data, season/guild data. For player data (DataStore, ProfileStore, session locking), use `roblox-data`.

## Quick Reference

### OrderedDataStore (Leaderboards)
- Sortable DataStore. Keys are strings; use a stable key such as `tostring(UserId)`.
- Values are integers used for sorting; choose the sign and ordering intentionally.
- `GetSortedAsync(ascending, pageSize, minValue, maxValue)` → sorted pages
- For leaderboards ONLY — not player data

```luau
local D = game:GetService("DataStoreService")
local store = D:GetOrderedDataStore("LeaderboardCoins")
store:SetAsync(tostring(player.UserId), playerCoins)
local top10 = store:GetSortedAsync(false, 10):GetCurrentPage()
```

### MessagingService (Cross-Server)
- Real-time server communication: `SubscribeAsync` / `PublishAsync`
- No delivery or ordering guarantee; design for idempotency.

### GlobalDataStore (Shared State)
- Persistent non-player state such as guilds, seasons, and counters.
- Use `UpdateAsync`; never use it for player session data.

### MemoryStoreService (Temporary Coordination)
- Queues and sorted maps for expiring matchmaking, leases, and coordination.
- Remove a read batch only after successful, idempotent processing.
- Use MessagingService or TeleportData for notification and handoff.

### Persistent World State Patterns
- **Building games**: serialize player-built structures to DataStore and reload on join
- **Seasons/leaderboards**: OrderedDataStore for rankings, GlobalDataStore for metadata
- **Guilds**: GlobalDataStore by guild ID, MessagingService for live updates
- **Economy counters**: GlobalDataStore + `UpdateAsync` for atomic increments

### Cross-Server Patterns
- Register servers with expiring heartbeats; use MessagingService for notifications.

### Pitfalls
- MessagingService is fire-and-forget — no delivery guarantee, no ordering
- GlobalDataStore has same rate limits as player DataStores — don't spam
- OrderedDataStore keys are strings; values are integers used for sorting
- Never store Instances — serialize to primitives first
- UpdateAsync for any shared counter to prevent lost updates

**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
