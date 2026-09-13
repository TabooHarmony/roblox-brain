---
name: roblox-data
description: "Use when implementing player data persistence with DataStore, session ownership, schemas, migrations, or save and load flows."
last_reviewed: 2026-09-13
sources:
  - https://create.roblox.com/docs/cloud-services/data-stores
  - https://create.roblox.com/docs/cloud-services/data-stores-vs-memory-stores
  - https://create.roblox.com/docs/cloud-services/memory-stores
  - https://create.roblox.com/docs/cloud-services/data-stores/data-stores-manager
  - https://create.roblox.com/docs/cloud-services/data-stores/right-to-be-forgotten
  - https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits
  - https://create.roblox.com/docs/cloud-services/data-stores/versioning-listing-and-caching
  - https://create.roblox.com/docs/reference/engine/classes/DataStoreService
  - https://raw.githubusercontent.com/MadStudioRoblox/ProfileStore/main/README.md
  - https://madstudioroblox.github.io/ProfileStore/api/
  - https://devforum.roblox.com/t/profilestore/3190543
  - original
---

# roblox data persistence

## When to Load

Load when designing player saves, schema migrations, retries, shutdown handling, or session ownership. Use `roblox-server-data` for ordered leaderboards, messaging, and world data; `roblox-cloud` for Open Cloud.

## Quick Reference

- Define a serializable template and a version field before storing player state. Deep-copy templates so nested defaults are not shared, and run migrations before stamping the version.
- Use `UpdateAsync` for read-modify-write; handle throttling and transient errors.
- Prevent two servers from mutating the same profile at once: a session-ownership wrapper or an equivalent protocol.
- With ProfileStore: `StartSessionAsync`, `Profile.OnSessionEnd`, `EndSession` as documented; no `Steal` for normal loads; `ProfileStore.Mock` for Studio tests.
- Save on meaningful changes and lifecycle boundaries; `PlayerRemoving` alone is not sufficient. Use `BindToClose` to finish pending work.
- Store primitives, arrays, dictionaries; convert Instances/userdata/functions/cyclic tables first. Validate persisted numbers (no NaN/inf), strings (`utf8.len`), and nested tables: one bad value fails the whole write.
- RTBF: keep the user ID as a static substring in keys (`player_<UserId>`) so `{UserId}` deletion templates can match; hashed or random keys make erasure manual.
- `GetAsync` serves a 4-second local cache (`DataStoreGetOptions.UseCache`, default `true`); verify writes with `UseCache = false`.
- Poll `DataStoreService:GetRequestBudgetForRequestType` for live headroom; quotas scale with concurrent users (experience reads: 300 + concurrentUsers x 40/min).
- New code identifies users with `player.User` (`User.Id`, `DomainType`, `DomainId`); `UserId` remains valid, but never mix the two IDs in one key scheme.

**Need the details?** Load `references/full.md` for a framework-neutral persistence design.
