---
name: roblox-data
description: "Use when writing, changing, debugging, or auditing Roblox player saves: DataStore, ProfileStore, session locks, schemas, migrations."
when_to_use: "Also when data is lost, rolled back, duplicated or not saving, when adding a field to the save, changing currency or inventory storage, or reviewing save code."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/reference/engine/classes/DataModel
  - https://create.roblox.com/docs/cloud-services/data-stores
  - https://create.roblox.com/docs/cloud-services/data-stores-vs-memory-stores
  - https://create.roblox.com/docs/cloud-services/memory-stores
  - https://create.roblox.com/docs/cloud-services/data-stores/data-stores-manager
  - https://create.roblox.com/docs/cloud-services/data-stores/right-to-be-forgotten
  - https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits
  - https://create.roblox.com/docs/cloud-services/data-stores/versioning-listing-and-caching
  - https://create.roblox.com/docs/reference/engine/classes/DataStoreService
  - https://raw.githubusercontent.com/MadStudioRoblox/ProfileStore/main/README.md
  - https://devforum.roblox.com/t/profilestore/3190543
  - original
---

# roblox data persistence

## When to Load

Load for player saves, migrations, retries, shutdowns, or session ownership. Leaderboards/messaging/world data: `roblox-server-data`; Open Cloud: `roblox-cloud`.

## Quick Reference

- Define a serializable template and a version field before storing player state. Deep-copy templates so nested defaults are not shared; migrate, then reconcile missing fields against the template. Scope store names by environment (`PlayerData_Studio`) so Studio writes stay out of production.
- Use `UpdateAsync` for read-modify-write; handle throttling and transient errors.
- Prevent concurrent profile mutation with a session-ownership protocol.
- With ProfileStore: `StartSessionAsync`, `Profile.OnSessionEnd`, `EndSession` as documented; no `Steal` for normal loads; `ProfileStore.Mock` for ephemeral Studio writes.
- Save on meaningful changes and lifecycle boundaries; `PlayerRemoving` alone is not sufficient; `BindToClose` finishes pending work.
- Store primitives/arrays/dictionaries; convert Instances/userdata/functions/cyclic tables first. Validate numbers (no NaN/inf), strings (`utf8.len`), nested tables: one bad value fails the write.
- RTBF: keep the user ID as a static substring in keys (`player_<UserId>`) so `{UserId}` deletion templates match; hashed/random keys make erasure manual.
- `GetAsync` serves a 4-second local cache (`DataStoreGetOptions.UseCache`, default `true`); verify writes with `UseCache = false`.
- Poll `DataStoreService:GetRequestBudgetForRequestType` for live headroom; quotas scale with concurrent users (experience reads: 300 + CCU x 40/min).
- New code identifies users with `player.User` (`User.Id`, `DomainType`, `DomainId`); `UserId` remains valid, but never mix the two IDs in one key scheme.
- `InvalidJson` = nesting >400. Offline earnings, serials: full.md §8b. Traces: `roblox-analytics` §8.

> Persistence workflows: [references/full.md](references/full.md)
