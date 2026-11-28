---
name: roblox-server-data
description: "Use when building or fixing Roblox cross-server data: OrderedDataStore leaderboards, MessagingService, MemoryStore, world state, seasons."
when_to_use: "Also for global leaderboards, cross-server announcements or events, matchmaking queues, shared counters, and reviewing non-player persistence."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/reference/engine/classes/MemoryStoreSortedMap
  - https://create.roblox.com/docs/reference/engine/classes/OrderedDataStore
  - https://create.roblox.com/docs/reference/engine/classes/MessagingService
  - https://create.roblox.com/docs/reference/engine/classes/MemoryStoreService
  - https://create.roblox.com/docs/reference/engine/classes/DataStoreService
  - https://create.roblox.com/docs/cloud-services/data-stores/right-to-be-forgotten
  - https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits
  - original
---

# Roblox Server & Shared Data

## When to Load

Load for leaderboards, messaging, MemoryStore coordination, world state, seasons, or guilds. Player persistence: `roblox-data`; Open Cloud: `roblox-cloud`.

## Quick Reference

### OrderedDataStore (Leaderboards)
- Sortable DataStore: string keys (`tostring(UserId)`), integer sort values; `GetSortedAsync` → pages; `BatchGetAsync` multi-key read (missing keys omitted).
- Budget bursts via `GetRequestBudgetForRequestType(OrderedWrite)` (per server: 30 + numPlayers×5 writes/min).
- PlayerList Friends/Global (beta) read one registered OrderedDataStore. Weekly: a store per ISO week.
- Leaderboards only, never player saves. Keep `player_<UserId>` a static key substring so RTBF templates match.

### MessagingService (Cross-Server)
- `SubscribeAsync` / `PublishAsync`; no delivery or ordering guarantee — design for idempotency.
- Request/response: `{reqId}` correlation + ack + timeout; no ack ≠ not executed — replay same reqId, don't double-grant.
- Budget receives, not just sends (full.md). <!-- temporal: 2026-10 -->

### GlobalDataStore (Shared State)
- Non-player state (guilds, seasons, counters) via `UpdateAsync`; not player sessions.

### MemoryStoreService (Temporary Coordination)
- Queues and sorted maps for expiring matchmaking, leases, coordination.
- Remove a read batch only after successful, idempotent processing.
- Sorted-map paging: last item's `{key, sortKey}` = next exclusive bound. Quotas are **game-level** (one shared pool): request units 1000+120×CCU/min, memory 64 KB+1.2 KB/user, value ≤32 KB, TTL 45 days; batch calls bill per item. <!-- temporal: 2026-10 -->

- At quota, growing writes fail; Open Cloud `memory-store:flush` clears the scope.

### Cross-Server Patterns
- Expiring server heartbeats; notify via MessagingService.

### User Identity
- Identify users with `player.User` (`User.Id`, `DomainType`, `DomainId`); `UserId` stays valid. Domain IDs are per-experience: key cross-server data on `UserId`.

### Pitfalls
- GlobalDataStore: same rate limits as player DataStores
- Never store Instances; use `UpdateAsync` for shared counters
> Store selection and workflows: [references/full.md](references/full.md)
