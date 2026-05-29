---
name: roblox-code-review
description: "Code review with security, performance, and monetization lenses for Roblox projects"
last_reviewed: 2026-05-27
---

# /code-review - Code Quality Review

Review Roblox projects with security, performance, and monetization lenses. Apply relevant lenses based on what changed — not all every time. Full details: `references/full.md`.

## When to Load

- User runs `/code-review` or asks for code review on Roblox/Luau code
- User asks to audit security, performance, networking, monetization, or data persistence
- User asks about Roblox best practices for remotes, data saving, or code organization

## Quick Reference

### 8-Step Review
1. **Project Scan** — scripts, folders, naming, Rojo/Wally/Studio
2. **Organization** — correct services, PascalCase modules, no orphans
3. **Code Quality** — `wait()`→`task.wait()`, `spawn()`→`task.spawn()`, `delay()`→`task.delay()`, globals
4. **Architecture** — single responsibility, no circular requires, server/client split
5. **Security** — validate remotes server-side, no client-trusted state, rate-limit
6. **Performance** — consolidate Heartbeat, cache services, disconnect events
7. **Report** — Grade A-F. Severity: Critical/High/Medium/Low
8. **Refactor** — Immediate → Short-term → Long-term

### Remote Types
- **RemoteEvent** — fire-and-forget | **RemoteFunction** — blocking, sparse, never per-frame
- **UnreliableRemoteEvent** — loss-tolerant VFX/position ONLY, never currency/inventory/damage

### Security
- Validate remotes: `typeof()`, range, cooldown, authorization
- State changes server-authoritative. No sensitive data in ReplicatedStorage
- Rate-limit all remotes per-player

### Performance
- `wait()`/`spawn()`/`delay()` → `task.*`. One Heartbeat per script
- Parts: <50K mobile, <200K PC. MeshParts > Unions
- Disconnect every `:Connect()`. Batch remotes. Cache GetService()

### Networking
- Remotes under `ReplicatedStorage.Remotes.{Category}`, PascalCase VerbNoun
- Separate reliable (state) from unreliable (cosmetics). FireClient > FireAllClients

### Data Persistence
- **Always ProfileStore**, never raw DataStoreService
- Template: DataVersion, defaults, JSON-only types. Reconcile() after load
- Session lock: AddUserId, ListenToRelease, ForceLoad
- Lifecycle: PlayerAdded→load, PlayerRemoving→sync+release, BindToClose→parallel

### Monetization
- Map GamePasses/DevProducts. ProcessReceipt: grant then confirm
- Pricing: Entry 25-49R, Mid 99-199R, Premium 499-999R
- Flag: loot odds, FOMO, pay-to-win, dark patterns
