---
name: roblox-data
description: "Use when implementing player data persistence with DataStore, session ownership, schemas, migrations, or save and load flows."
last_reviewed: 2026-07-13
sources:
  - https://create.roblox.com/docs/cloud-services/data-stores
  - https://create.roblox.com/docs/cloud-services/data-stores-vs-memory-stores
  - https://create.roblox.com/docs/cloud-services/memory-stores
  - https://create.roblox.com/docs/cloud-services/data-stores/data-stores-manager
  - https://create.roblox.com/docs/reference/engine/classes/DataStoreService
  - https://raw.githubusercontent.com/MadStudioRoblox/ProfileStore/main/README.md
  - https://madstudioroblox.github.io/ProfileStore/api/
  - https://devforum.roblox.com/t/profilestore/3190543
  - original
---

# roblox data persistence

## When to Load

Load when designing player saves, schema migrations, retries, shutdown handling, session ownership, or cross-server state. Use `roblox-server-data` for ordered leaderboards, messaging, and global world data.

## Quick Reference

- Define a serializable template and a version field before storing player state.
- Use `UpdateAsync` for read-modify-write operations and handle throttling or transient errors.
- Prevent two servers from mutating the same player's profile at once, either with a well-understood wrapper or an equivalent session protocol.
- If using ProfileStore, use `StartSessionAsync`, `Profile.OnSessionEnd`, and `EndSession` as documented. Do not use its `Steal` option for normal player loading.
- Use `ProfileStore.Mock` for Studio tests that must not write live DataStore keys.
- Save on meaningful changes and on lifecycle boundaries, but do not assume `PlayerRemoving` alone is sufficient.
- Use `BindToClose` to finish pending work within Roblox's shutdown window.
- Store primitives, arrays, and dictionaries. Convert Instances, userdata, functions, and cyclic tables first.

**Need the details?** Load `references/full.md` for a framework-neutral persistence design.
