# Roblox Testing Patterns Reference

## 1. Overview

Load this reference when:

- Writing unit or integration tests for Roblox game modules
- Setting up test infrastructure for a new or existing project
- Configuring CI/CD pipelines for automated linting, formatting, and test runs
- Refactoring modules to improve testability
- Debugging failures caught during playtesting or production monitoring

Testing in Roblox is non-trivial because game code depends heavily on engine services (`Players`, `DataStoreService`, `ReplicatedStorage`, etc.) that are unavailable outside Studio. The patterns here show how to write testable code, mock those services, and automate verification at every stage of development.

---

## 2. TestEZ Framework

### Installation via Wally

Add TestEZ as a dev dependency in `wally.toml`:

```toml
[dev-dependencies]
TestEZ = "roblox/testez@0.4.1"
```

Run `wally install` and the package lands in `DevPackages/`. Sync it into Studio via your Rojo project file (typically under `ReplicatedStorage.DevPackages`).

### Test File Conventions

- Test files use the suffix `.spec.luau` (e.g., `CurrencyManager.spec.luau`).
- Each spec file lives alongside or mirrors the module it tests.
- TestEZ discovers specs by recursively scanning a root container you point it at.

### Core Syntax

```luau
return function()
    describe("CurrencyManager", function()
        local CurrencyManager

        beforeEach(function()
            -- Fresh module state before every test
            CurrencyManager = require(script.Parent.CurrencyManager)
        end)

        afterEach(function()
            -- Teardown: reset any shared state
        end)

        it("should initialize a player with zero gold", function()
            local data = CurrencyManager.newPlayerData()
            expect(data.gold).to.equal(0)
        end)

        it("should add currency correctly", function()
            local data = CurrencyManager.newPlayerData()
            CurrencyManager.addGold(data, 100)
            expect(data.gold).to.equal(100)
        end)

        it("should never allow negative gold", function()
            local data = CurrencyManager.newPlayerData()
            CurrencyManager.addGold(data, 50)
            CurrencyManager.removeGold(data, 999)
            expect(data.gold).to.equal(0)
        end)
    end)
end
```

### Assertion API Highlights

```luau
expect(value).to.equal(expected)          -- strict equality
expect(value).to.be.ok()                  -- truthy
expect(value).to.be.a("table")            -- type check
expect(value).never.to.equal(unexpected)  -- negation
expect(function()
    error("boom")
end).to.throw()                           -- error expected
expect(value).to.be.near(3.14, 0.01)      -- float tolerance
```

### Running Tests Inside Studio

Create a test runner script in `ServerScriptService`:

```luau
local TestEZ = require(game.ReplicatedStorage.DevPackages.TestEZ)
local results = TestEZ.TestBootstrap:run({
    game.ReplicatedStorage.Shared,       -- scan these containers
    game.ServerScriptService.Server,
})
```

---

## 3. Unit Testing ModuleScripts

Unit tests target **pure logic** — functions that take inputs and return outputs without touching engine APIs.

### Good Candidates for Unit Testing

| Module Type | Examples |
|---|---|
| Damage calculation | `calculateDamage(baseDmg, armor, crit)` |
| Inventory operations | `addItem(inventory, itemId, qty)` |
| Data transforms | `serializeLoadout(loadout)` / `deserializeLoadout(raw)` |
| Config validators | `validateWeaponConfig(config)` |
| Math/utility | `clamp`, `lerp`, `formatNumber` |

### Pattern: Test a Pure Module

Module under test (`DamageCalc.luau`):

```luau
local DamageCalc = {}

function DamageCalc.calculate(baseDamage: number, armor: number, isCrit: boolean): number
    local reduction = math.clamp(armor / 100, 0, 0.75)
    local damage = baseDamage * (1 - reduction)
    if isCrit then
        damage *= 2
    end
    return math.floor(damage)
end

return DamageCalc
```

Spec (`DamageCalc.spec.luau`):

```luau
return function()
    local DamageCalc = require(script.Parent.DamageCalc)

    describe("calculate", function()
        it("should apply armor reduction", function()
            -- 50 armor = 50% reduction on 100 base = 50
            expect(DamageCalc.calculate(100, 50, false)).to.equal(50)
        end)

        it("should cap armor reduction at 75%", function()
            expect(DamageCalc.calculate(100, 200, false)).to.equal(25)
        end)

        it("should double damage on crit", function()
            expect(DamageCalc.calculate(100, 0, true)).to.equal(200)
        end)

        it("should floor the result", function()
            expect(DamageCalc.calculate(33, 10, false)).to.equal(29)
        end)
    end)
end
```

### Keep Modules Testable

The key rule: **avoid calling `game:GetService()` or accessing `game.*` directly inside functions you want to unit test.** Extract engine interactions to the boundary and pass data in.

```luau
-- BAD: untestable, reaches into the engine
function Module.getPlayerHealth(player)
    local char = player.Character
    local humanoid = char:FindFirstChildOfClass("Humanoid")
    return humanoid.Health
end

-- GOOD: testable, accepts the value it needs
function Module.isLowHealth(currentHealth: number, threshold: number): boolean
    return currentHealth <= threshold
end
```

---

## 4. Dependency Injection for Testability

When a module must interact with a Roblox service, inject the service as a parameter instead of hard-coding `game:GetService()`.

### Pattern: Constructor Injection

```luau
local InventoryManager = {}
InventoryManager.__index = InventoryManager

-- Accept services through the constructor
function InventoryManager.new(dataStoreService, messagingService)
    local self = setmetatable({}, InventoryManager)
    self._dataStore = dataStoreService:GetDataStore("Inventory")
    self._messaging = messagingService
    return self
end

function InventoryManager:saveInventory(playerId: number, inventory: { [string]: number })
    local key = "inv_" .. tostring(playerId)
    self._dataStore:SetAsync(key, inventory)
end

function InventoryManager:loadInventory(playerId: number): { [string]: number }
    local key = "inv_" .. tostring(playerId)
    return self._dataStore:GetAsync(key) or {}
end

return InventoryManager
```

### Production Wiring

```luau
local DataStoreService = game:GetService("DataStoreService")
local MessagingService = game:GetService("MessagingService")
local InventoryManager = require(path.to.InventoryManager)

local manager = InventoryManager.new(DataStoreService, MessagingService)
```

### Test Wiring (inject mocks)

```luau
local MockDataStoreService = require(script.Parent.Mocks.MockDataStoreService)
local InventoryManager = require(script.Parent.InventoryManager)

local manager = InventoryManager.new(MockDataStoreService.new(), mockMessaging)
```

### Alternative: Module-Level Injection via `.init()`

For modules that are singletons rather than classes:

```luau
local Module = {}
local _players = nil

function Module.init(playersService)
    _players = playersService
end

function Module.getPlayerCount(): number
    return #_players:GetPlayers()
end

return Module
```

---

## 5. Mocking Roblox Services

### Mock Players Service

```luau
local MockPlayers = {}
MockPlayers.__index = MockPlayers

function MockPlayers.new()
    local self = setmetatable({}, MockPlayers)
    self._players = {}
    self.PlayerAdded = MockSignal.new()
    self.PlayerRemoving = MockSignal.new()
    return self
end

function MockPlayers:GetPlayers()
    return self._players
end

function MockPlayers:addFakePlayer(mockPlayer)
    table.insert(self._players, mockPlayer)
    self.PlayerAdded:Fire(mockPlayer)
end

function MockPlayers:removeFakePlayer(mockPlayer)
    local idx = table.find(self._players, mockPlayer)
    if idx then
        table.remove(self._players, idx)
        self.PlayerRemoving:Fire(mockPlayer)
    end
end

return MockPlayers
```

### Mock Signal (for RBXScriptSignal-like behavior)

```luau
local MockSignal = {}
MockSignal.__index = MockSignal

function MockSignal.new()
    return setmetatable({ _connections = {} }, MockSignal)
end

function MockSignal:Connect(callback)
    table.insert(self._connections, callback)
    return {
        Disconnect = function(conn)
            local idx = table.find(self._connections, callback)
            if idx then
                table.remove(self._connections, idx)
            end
        end,
    }
end

function MockSignal:Fire(...)
    for _, cb in self._connections do
        task.spawn(cb, ...)
    end
end

return MockSignal
```

### Mock DataStoreService (In-Memory)

```luau
local MockDataStore = {}
MockDataStore.__index = MockDataStore

function MockDataStore.new()
    return setmetatable({ _data = {} }, MockDataStore)
end

function MockDataStore:GetAsync(key)
    return self._data[key]
end

function MockDataStore:SetAsync(key, value)
    self._data[key] = value
end

function MockDataStore:UpdateAsync(key, transformFunction)
    local old = self._data[key]
    self._data[key] = transformFunction(old)
end

function MockDataStore:RemoveAsync(key)
    self._data[key] = nil
end

-- ------------------------------------------------

local MockDataStoreService = {}
MockDataStoreService.__index = MockDataStoreService

function MockDataStoreService.new()
    return setmetatable({ _stores = {} }, MockDataStoreService)
end

function MockDataStoreService:GetDataStore(name)
    if not self._stores[name] then
        self._stores[name] = MockDataStore.new()
    end
    return self._stores[name]
end

return MockDataStoreService
```

### Mock MarketplaceService

```luau
local MockMarketplaceService = {}
MockMarketplaceService.__index = MockMarketplaceService

function MockMarketplaceService.new(ownedGamepasses: { [number]: boolean }?)
    local self = setmetatable({}, MockMarketplaceService)
    self._ownedPasses = ownedGamepasses or {}
    self.PromptGamePassPurchaseFinished = MockSignal.new()
    return self
end

function MockMarketplaceService:UserOwnsGamePassAsync(_userId, gamePassId)
    return self._ownedPasses[gamePassId] == true
end

return MockMarketplaceService
```

---

## 6. Integration Testing

Integration tests verify that **multiple modules work together correctly** — data flows across boundaries and side effects happen as expected.

### Pattern: DataManager + InventoryManager

```luau
return function()
    local MockDataStoreService = require(script.Parent.Mocks.MockDataStoreService)
    local DataManager = require(script.Parent.DataManager)
    local InventoryManager = require(script.Parent.InventoryManager)

    describe("DataManager + InventoryManager integration", function()
        local mockDSS
        local dataMgr
        local invMgr

        beforeEach(function()
            mockDSS = MockDataStoreService.new()
            dataMgr = DataManager.new(mockDSS)
            invMgr = InventoryManager.new(mockDSS)
        end)

        it("should persist inventory through save/load cycle", function()
            local playerId = 12345
            local inventory = { Sword = 1, Shield = 2, Potion = 10 }

            invMgr:saveInventory(playerId, inventory)
            local loaded = invMgr:loadInventory(playerId)

            expect(loaded.Sword).to.equal(1)
            expect(loaded.Shield).to.equal(2)
            expect(loaded.Potion).to.equal(10)
        end)

        it("should return empty inventory for new player", function()
            local loaded = invMgr:loadInventory(99999)
            expect(next(loaded)).to.equal(nil)
        end)
    end)
end
```

### Testing RemoteEvent Flows

For end-to-end remote flows in a test environment, create mock remotes:

```luau
local MockRemoteEvent = {}
MockRemoteEvent.__index = MockRemoteEvent

function MockRemoteEvent.new()
    local self = setmetatable({}, MockRemoteEvent)
    self.OnServerEvent = MockSignal.new()
    self.OnClientEvent = MockSignal.new()
    return self
end

function MockRemoteEvent:FireServer(...)
    self.OnServerEvent:Fire(nil, ...) -- nil = fake player in test
end

function MockRemoteEvent:FireClient(_player, ...)
    self.OnClientEvent:Fire(...)
end

function MockRemoteEvent:FireAllClients(...)
    self.OnClientEvent:Fire(...)
end

return MockRemoteEvent
```

Usage in a test:

```luau
it("should process purchase request and respond", function()
    local remote = MockRemoteEvent.new()
    local responded = false

    -- Simulate server handler
    remote.OnServerEvent:Connect(function(_player, itemId)
        -- Server validates and responds
        local success = ShopManager:tryPurchase(itemId, playerData)
        remote:FireClient(nil, success, itemId)
    end)

    -- Capture client response
    remote.OnClientEvent:Connect(function(success, itemId)
        responded = true
        expect(success).to.equal(true)
        expect(itemId).to.equal("Sword")
    end)

    remote:FireServer("Sword")
    expect(responded).to.equal(true)
end)
```

---

## 7. MCP-Powered Testing

When Roblox Studio MCP tools are available, use them for automated smoke testing without leaving your editor.

### Automated Smoke Test Workflow

```
1. start_playtest()
   - Launches a local test server in Studio

2. wait 5-10 seconds for game initialization

3. get_playtest_output()
   - Captures Output window logs
   - Look for: errors, warnings, "Script timeout" messages

4. Analyze the output
   - Any red error lines?  -> investigate and fix
   - Module load failures? -> check requires and paths
   - DataStore errors?     -> check mock/fallback setup

5. stop_playtest()
   - Ends the session cleanly
```

### Iterative Debugging Loop with MCP

```
REPEAT:
    1. Apply code fix
    2. start_playtest()
    3. get_playtest_output() — scan for the specific error you are fixing
    4. If error persists → stop_playtest(), refine fix, go to 1
    5. If error gone     → stop_playtest(), move on
```

### Checking for Specific Errors

After `get_playtest_output()`, filter for critical patterns:

- `"error"` or `"Error"` — runtime errors
- `"attempt to index nil"` — missing references
- `"Infinite yield possible"` — WaitForChild timeouts
- `"HTTP 429"` — DataStore throttling
- `"not a valid member"` — API misuse or renamed properties

---

## 8. Manual Testing Workflows

Automated tests do not cover everything. Use this checklist for manual playtesting:

### Pre-Release Checklist

- [ ] **Mobile playtest** — Touch controls work, UI fits small screens, no overlapping buttons
- [ ] **Multi-player test** (Studio local server, 2+ players) — Replication works, no desync, RemoteEvents fire correctly
- [ ] **Edge cases**:
  - Disconnect mid-save (does data persist or rollback cleanly?)
  - Rejoin immediately after leaving
  - Rapid-fire actions (spam click buy button, spam attack)
  - Inventory at max capacity
- [ ] **Monetization flow**:
  - Game pass ownership detection works
  - Developer product purchase prompt appears
  - Receipt processing completes and grants items
  - Duplicate receipt handling (idempotent processing)
- [ ] **First-time user experience** — New player gets default data, tutorial triggers, no errors in output
- [ ] **Performance** — MicroProfiler shows no frame spikes on spawn, no memory leaks during extended play

### Studio Test Server (Multi-Player)

1. File -> Test -> Start (set player count to 2+)
2. Each client window is a separate player instance
3. Server window shows server-side output
4. Verify: leaderboards update for both, chat works, interactions replicate

---

## 9. Test Organization

### Rojo Project Structure (Recommended)

```
project/
  src/
    server/
      DataManager.luau
      InventoryManager.luau
      CurrencyManager.luau
    shared/
      DamageCalc.luau
      Utils.luau
    client/
      UIController.luau
  tests/
    server/
      DataManager.spec.luau
      InventoryManager.spec.luau
      CurrencyManager.spec.luau
    shared/
      DamageCalc.spec.luau
      Utils.spec.luau
    mocks/
      MockDataStoreService.luau
      MockPlayers.luau
      MockSignal.luau
      MockRemoteEvent.luau
    init.spec.luau            -- test runner entry
  wally.toml
  default.project.json
```

### Studio-Only Structure

```
ServerScriptService/
  Tests/
    TestRunner (Script)
    Specs/
      CurrencyManager.spec
      DamageCalc.spec
    Mocks/
      MockDataStoreService
      MockPlayers
```

### Naming Conventions

| Convention | Example |
|---|---|
| Spec file suffix | `CurrencyManager.spec.luau` |
| Mock file prefix | `MockDataStoreService.luau` |
| Describe block | `describe("CurrencyManager")` |
| Test name | `it("should deduct gold on purchase")` |

---

## 10. CI/CD Integration

### Running Tests Headlessly with Lune

[Lune](https://lune-org.github.io/docs) is a standalone Luau runtime that can execute TestEZ specs outside of Roblox Studio.

Create a test runner script (`run-tests.luau`):

```luau
local process = require("@lune/process")
local fs = require("@lune/fs")

-- Require TestEZ (bundled or installed via pesde/wally for lune)
local TestEZ = require("./DevPackages/TestEZ")

-- Point TestEZ at your spec files
local results = TestEZ.TestBootstrap:run({
    -- List directories containing .spec.luau files
    "./tests/server",
    "./tests/shared",
})

if results.failureCount > 0 then
    process.exit(1)
end
```

### GitHub Actions Workflow

```yaml
name: Roblox CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Aftman (toolchain manager)
        uses: ok-nick/setup-aftman@v0.4.2

      - name: Install Wally packages
        run: wally install

      - name: Selene lint
        run: selene src/ tests/

      - name: StyLua format check
        run: stylua --check src/ tests/

      - name: Run TestEZ tests via Lune
        run: lune run run-tests.luau

      - name: Build Roblox place file
        run: rojo build default.project.json -o game.rbxl
```

### Aftman Tool Versions (`aftman.toml`)

```toml
[tools]
rojo = "rojo-rbx/rojo@7.4.4"
wally = "UpliftGames/wally@0.3.2"
selene = "Kampfkarren/selene@0.27.1"
stylua = "JohnnyMorganz/StyLua@0.20.0"
lune = "lune-org/lune@0.8.9"
```

---

## 11. Best Practices

### Test Critical Paths First

Prioritize tests for code where bugs cost the most:

1. **Data save/load** — A bug here can wipe player progress. Test serialization, deserialization, migration, and edge cases (empty data, corrupt data).
2. **Purchases and monetization** — Receipt processing must be idempotent. Test duplicate receipts, test granting after purchase, test failure recovery.
3. **Combat damage / core gameplay math** — Players notice immediately when damage numbers are wrong. Test crit, armor, buffs, edge values.
4. **Server-side validation** — Every RemoteEvent handler that accepts client input must validate. Test with out-of-range values, wrong types, and nil.

### General Guidelines

- **Keep tests fast.** Each test should run in milliseconds. If a test needs `task.wait()`, you are likely testing integration-level behavior — separate it from unit tests.
- **One assertion focus per test.** A test named `"should add gold"` should test adding gold, not also test removing gold and checking the balance format.
- **Test server-side validation independently.** Do not rely on the client sending correct data. Write tests that call server validation functions with malicious inputs.
- **Write a test before fixing a bug.** Reproduce the bug in a failing test first, then fix the code until the test passes. This prevents regressions.
- **Use deterministic data.** Avoid `math.random()` in tests. Use fixed seed values or hardcoded inputs so failures are reproducible.
- **Reset state in `beforeEach`.** Never let one test depend on the side effects of another.

---

## 12. Anti-Patterns

### Testing Only Manually in Studio

**Problem:** You click around in Studio, it seems to work, you ship. A week later an edge case surfaces in production.

**Fix:** Write automated tests for core logic. Manual playtesting supplements automated tests; it does not replace them.

### No Tests for Monetization Code

**Problem:** Receipt processing is written once, never tested, and breaks silently. Players pay real money and receive nothing.

**Fix:** Unit test `processReceipt` with mock MarketplaceService. Test duplicate receipts, test every product ID, test failure paths.

### Untestable Tightly-Coupled Modules

**Problem:**

```luau
-- Everything is hardcoded; impossible to test without a live game
function Module.onPlayerJoin()
    local player = game.Players.LocalPlayer
    local data = game:GetService("DataStoreService"):GetDataStore("Main"):GetAsync(player.UserId)
    local gui = player.PlayerGui:WaitForChild("MainUI")
    gui.GoldLabel.Text = tostring(data.gold)
end
```

**Fix:** Break it apart. Pure logic in one module, engine glue in another. Inject services.

```luau
-- Pure logic (testable)
function CurrencyFormatter.formatGold(gold: number): string
    return tostring(gold)
end

-- Glue code (thin, not unit tested, covered by integration/manual tests)
function UIController.updateGoldDisplay(player, gold)
    local gui = player.PlayerGui:WaitForChild("MainUI")
    gui.GoldLabel.Text = CurrencyFormatter.formatGold(gold)
end
```

### Tests That Depend on Execution Order

**Problem:** Test B passes only if Test A runs first because A sets up shared state.

**Fix:** Use `beforeEach` to create fresh state for every test. Each test must be independently runnable.

### Ignoring Flaky Tests

**Problem:** A test sometimes passes and sometimes fails. The team marks it as "known flaky" and ignores it.

**Fix:** Flaky tests usually indicate shared mutable state, timing issues, or race conditions. Fix the root cause or delete the test — a flaky test is worse than no test because it erodes trust in the suite.

---

## Full Example: CurrencyManager with Tests

### Module (`CurrencyManager.luau`)

```luau
local CurrencyManager = {}
CurrencyManager.__index = CurrencyManager

export type CurrencyData = {
    gold: number,
    gems: number,
}

function CurrencyManager.new(dataStoreService)
    local self = setmetatable({}, CurrencyManager)
    self._store = dataStoreService:GetDataStore("Currency")
    self._cache = {} :: { [number]: CurrencyData }
    return self
end

function CurrencyManager.newPlayerData(): CurrencyData
    return {
        gold = 0,
        gems = 0,
    }
end

function CurrencyManager:loadPlayer(playerId: number): CurrencyData
    local raw = self._store:GetAsync("currency_" .. tostring(playerId))
    local data = raw or CurrencyManager.newPlayerData()
    self._cache[playerId] = data
    return data
end

function CurrencyManager:savePlayer(playerId: number)
    local data = self._cache[playerId]
    if data then
        self._store:SetAsync("currency_" .. tostring(playerId), data)
    end
end

function CurrencyManager:getGold(playerId: number): number
    local data = self._cache[playerId]
    return if data then data.gold else 0
end

function CurrencyManager:addGold(playerId: number, amount: number): boolean
    if amount <= 0 then
        return false
    end
    local data = self._cache[playerId]
    if not data then
        return false
    end
    data.gold += amount
    return true
end

function CurrencyManager:removeGold(playerId: number, amount: number): boolean
    if amount <= 0 then
        return false
    end
    local data = self._cache[playerId]
    if not data then
        return false
    end
    if data.gold < amount then
        return false -- insufficient funds
    end
    data.gold -= amount
    return true
end

function CurrencyManager:transferGold(fromId: number, toId: number, amount: number): boolean
    if not self:removeGold(fromId, amount) then
        return false
    end
    if not self:addGold(toId, amount) then
        -- Rollback
        self:addGold(fromId, amount)
        return false
    end
    return true
end

return CurrencyManager
```

### Test (`CurrencyManager.spec.luau`)

```luau
return function()
    local MockDataStoreService = require(script.Parent.Parent.Mocks.MockDataStoreService)
    local CurrencyManager = require(script.Parent.CurrencyManager)

    describe("CurrencyManager", function()
        local mockDSS
        local manager

        beforeEach(function()
            mockDSS = MockDataStoreService.new()
            manager = CurrencyManager.new(mockDSS)
        end)

        describe("newPlayerData", function()
            it("should return zero gold and zero gems", function()
                local data = CurrencyManager.newPlayerData()
                expect(data.gold).to.equal(0)
                expect(data.gems).to.equal(0)
            end)
        end)

        describe("loadPlayer", function()
            it("should return default data for a new player", function()
                local data = manager:loadPlayer(1001)
                expect(data.gold).to.equal(0)
                expect(data.gems).to.equal(0)
            end)

            it("should return saved data for an existing player", function()
                -- Pre-populate the mock store
                local store = mockDSS:GetDataStore("Currency")
                store:SetAsync("currency_1001", { gold = 500, gems = 10 })

                local data = manager:loadPlayer(1001)
                expect(data.gold).to.equal(500)
                expect(data.gems).to.equal(10)
            end)
        end)

        describe("savePlayer", function()
            it("should persist data to the store", function()
                manager:loadPlayer(1001)
                manager:addGold(1001, 250)
                manager:savePlayer(1001)

                -- Verify by reading directly from the mock store
                local store = mockDSS:GetDataStore("Currency")
                local raw = store:GetAsync("currency_1001")
                expect(raw.gold).to.equal(250)
            end)

            it("should do nothing for an unloaded player", function()
                -- Should not error
                manager:savePlayer(9999)
            end)
        end)

        describe("addGold", function()
            it("should increase gold by the given amount", function()
                manager:loadPlayer(1001)
                local ok = manager:addGold(1001, 100)
                expect(ok).to.equal(true)
                expect(manager:getGold(1001)).to.equal(100)
            end)

            it("should accumulate across multiple calls", function()
                manager:loadPlayer(1001)
                manager:addGold(1001, 50)
                manager:addGold(1001, 75)
                expect(manager:getGold(1001)).to.equal(125)
            end)

            it("should reject zero amount", function()
                manager:loadPlayer(1001)
                local ok = manager:addGold(1001, 0)
                expect(ok).to.equal(false)
                expect(manager:getGold(1001)).to.equal(0)
            end)

            it("should reject negative amount", function()
                manager:loadPlayer(1001)
                local ok = manager:addGold(1001, -50)
                expect(ok).to.equal(false)
            end)

            it("should fail for unloaded player", function()
                local ok = manager:addGold(9999, 100)
                expect(ok).to.equal(false)
            end)
        end)

        describe("removeGold", function()
            it("should decrease gold by the given amount", function()
                manager:loadPlayer(1001)
                manager:addGold(1001, 200)
                local ok = manager:removeGold(1001, 50)
                expect(ok).to.equal(true)
                expect(manager:getGold(1001)).to.equal(150)
            end)

            it("should reject removal exceeding balance", function()
                manager:loadPlayer(1001)
                manager:addGold(1001, 30)
                local ok = manager:removeGold(1001, 50)
                expect(ok).to.equal(false)
                expect(manager:getGold(1001)).to.equal(30) -- unchanged
            end)

            it("should reject zero amount", function()
                manager:loadPlayer(1001)
                local ok = manager:removeGold(1001, 0)
                expect(ok).to.equal(false)
            end)

            it("should reject negative amount", function()
                manager:loadPlayer(1001)
                local ok = manager:removeGold(1001, -10)
                expect(ok).to.equal(false)
            end)
        end)

        describe("transferGold", function()
            it("should move gold from one player to another", function()
                manager:loadPlayer(1001)
                manager:loadPlayer(1002)
                manager:addGold(1001, 500)

                local ok = manager:transferGold(1001, 1002, 200)
                expect(ok).to.equal(true)
                expect(manager:getGold(1001)).to.equal(300)
                expect(manager:getGold(1002)).to.equal(200)
            end)

            it("should fail if sender has insufficient funds", function()
                manager:loadPlayer(1001)
                manager:loadPlayer(1002)
                manager:addGold(1001, 50)

                local ok = manager:transferGold(1001, 1002, 100)
                expect(ok).to.equal(false)
                expect(manager:getGold(1001)).to.equal(50)  -- unchanged
                expect(manager:getGold(1002)).to.equal(0)   -- unchanged
            end)

            it("should fail if recipient is not loaded", function()
                manager:loadPlayer(1001)
                manager:addGold(1001, 500)

                local ok = manager:transferGold(1001, 9999, 100)
                expect(ok).to.equal(false)
                expect(manager:getGold(1001)).to.equal(500) -- rollback
            end)
        end)

        describe("getGold", function()
            it("should return 0 for unloaded player", function()
                expect(manager:getGold(9999)).to.equal(0)
            end)
        end)
    end)
end
```
