---
name: roblox-server-data
description: "Use for Roblox server or cross-server data: OrderedDataStore leaderboards, MessagingService, world state, seasons, or guilds."
last_reviewed: 2026-09-13
sources:
  - https://create.roblox.com/docs/reference/engine/classes/OrderedDataStore
  - https://create.roblox.com/docs/reference/engine/classes/MessagingService
  - https://create.roblox.com/docs/reference/engine/classes/MemoryStoreService
  - https://create.roblox.com/docs/reference/engine/classes/DataStoreService
  - https://create.roblox.com/docs/cloud-services/data-stores/right-to-be-forgotten
  - https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits
---

# Roblox Server & Shared Data

## When to Load

Load for server-level or cross-server data: leaderboards (OrderedDataStore), cross-server messaging (MessagingService), queues and sorted maps (MemoryStoreService), shared world state, non-player persistence, season or guild data. For player data, use `roblox-data`; for Open Cloud, use `roblox-cloud`.

## Quick Reference

### OrderedDataStore (Leaderboards)
- Sortable DataStore. Keys are strings (`tostring(UserId)`); values are integers used for sorting.
- `GetSortedAsync(ascending, pageSize, minValue, maxValue)` → sorted pages
- `BatchGetAsync(keys)`: multi-key read, ordered stores only; missing keys are omitted
- Budget: poll `GetRequestBudgetForRequestType(OrderedWrite)` before bursts (per server: 30 + numPlayers x 5 writes/min)
- For leaderboards only, never for player saves
- Keep the user ID a static substring in keys (`player_<UserId>`) so RTBF templates match; hashed keys make erasure manual

### MessagingService (Cross-Server)
- `SubscribeAsync` / `PublishAsync`; no delivery or ordering guarantee, so design for idempotency.

### GlobalDataStore (Shared State)
- Persistent non-player state (guilds, seasons, counters). Use `UpdateAsync`; never for player session data.

### MemoryStoreService (Temporary Coordination)
- Queues and sorted maps for expiring matchmaking, leases, coordination.
- Remove a read batch only after successful, idempotent processing.

### Cross-Server Patterns
- Register servers with expiring heartbeats; use MessagingService for notifications.

### User Identity
- New code identifies users with `player.User` (`User.Id`, `DomainType`, `DomainId`); `UserId` stays valid. Domain IDs are per-experience, so keep cross-server keys on `UserId` and never mix the two.

### Pitfalls
- MessagingService: fire-and-forget, unordered, cross-server latency; not for time-critical work
- GlobalDataStore: same rate limits as player DataStores
- Never store Instances; serialize to primitives first
- `SetAsync` overwrites without reading; use `UpdateAsync` for shared counters

**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
