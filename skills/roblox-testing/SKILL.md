---
name: roblox-testing
description: "Use when writing Roblox unit or integration tests, mocking services, setting up Lune CI, or designing code for dependency injection and testability."
last_reviewed: 2026-05-27
sources:
  - https://raw.githubusercontent.com/brockmartin/roblox-game-skill/main/references/testing-patterns.md
  - https://github.com/Roblox/testez
---

## When to Load

Load when writing unit/integration tests, mocking Roblox services, setting up CI/CD with Lune, or refactoring code for testability via dependency injection. Hand off to `roblox-luau-core` for syntax, `roblox-luau-types` for type design, `roblox-luau-patterns` for architecture, `roblox-security` for validation.

## Quick Reference

### TestEZ (BDD framework)

- Install: `[dev-dependencies] TestEZ = "roblox/testez@0.4.1"` in `wally.toml`
- Files: `*.spec.luau`, co-located with source
- Blocks: `describe` → `it` → `beforeEach`/`afterEach`
- Assertions: `expect(x).to.equal(y)`, `.to.be.near(n, ε)`, `.to.throw()`

### Dependency Injection

```luau
-- BAD: untestable outside Studio
local store = game:GetService("DataStoreService"):GetDataStore("PlayerData")
-- GOOD: inject dependency
local function saveData(player, data, dataStore)
    dataStore:SetAsync("player_" .. player.UserId, data)
end
-- Module init pattern:
function Manager.init(dataStoreService)
    _dss = dataStoreService or game:GetService("DataStoreService")
end
```

### Mocking Essentials

```luau
-- MockDataStore: in-memory Get/Set/Update
local M = {}
function M.new() return setmetatable({_data={}}, {__index=M}) end
function M:GetAsync(k) return self._data[k] end
function M:SetAsync(k,v) self._data[k]=v end
function M:GetDataStore() return self end
-- MockRemoteEvent: OnServerEvent + FireServer
-- MockSignal: Connect/Fire with Connected flag
```

### CI/CD with Lune

```toml
# aftman.toml
[tools]
lune = "lune-org/lune@0.8.0"
```

Pipeline: `selene src/` → `stylua --check src/` → `luau-lsp analyze` → `lune run tests/run.luau`

```luau
-- tests/run.luau
local TestEZ = require("@testez")
local results = TestEZ.TestBootstrap:run({game:GetService("ReplicatedStorage")}, TestEZ.Reporters.TextReporter)
if results.failureCount > 0 then os.exit(1) end
```

### Testing Priority

1. DataStore save/load round-trips (prevents data loss)
2. Monetization ProcessReceipt (idempotency)
3. Core math (damage, buffs, economy)
4. Server validation (remote exploits)

### Pitfalls

- `beforeEach` to reset state; never `game:GetService()` in logic
- Tests must be order-independent; CI needs mocks; commit `wally.lock`
**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
