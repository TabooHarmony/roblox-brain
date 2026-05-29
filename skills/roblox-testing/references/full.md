# Roblox Testing Patterns — Full Reference

## Decision Rules

- Test pure logic first (math, data transforms, validators), engine-dependent code second
- Never call `game:GetService()` inside logic functions; inject dependencies instead
- Use TestEZ for BDD-style tests; use Lune for headless CI runs
- Prioritize testing: DataStore persistence > Monetization > Core math > Server validation
- Every test must be independent; use `beforeEach` to reset shared state
- Tests that only pass in Studio are integration tests, not unit tests

## Philosophy

Roblox code is hard to test because the engine APIs aren't available outside Studio. The solution is to separate your logic from the engine:

1. **Pure functions** take inputs, return outputs, touch nothing else. Easy to test.
2. **Engine boundaries** are thin wrappers that call `game:GetService()`, `workspace`, etc. Keep them thin.
3. **Dependency injection** means passing services as parameters instead of reaching into the global `game` object.

If a function reads `player.Character.Humanoid.Health` directly, it's untestable outside Studio. If it accepts `currentHealth: number` as a parameter, it's trivially testable.

---

## TestEZ Framework

### Conventions

- Use the `.spec.luau` suffix for test files
- Place test files alongside the modules they test
- Core blocks: `describe`, `it`, `beforeEach`, `afterEach`

### Assertion Examples

```luau
describe("Calculator", function()
    it("should add two numbers", function()
        expect(add(2, 3)).to.equal(5)
    end)

    it("should handle floating point", function()
        expect(add(0.1, 0.2)).to.be.near(0.3, 0.01)
    end)

    it("should throw on invalid input", function()
        expect(function()
            add("a", 1)
        end).to.throw()
    end)
end)
```

---

## Dependency Injection — Extended Examples

### Constructor Injection

```luau
-- BAD: reaches into game, untestable outside Studio
local function saveData(player, data)
    local store = game:GetService("DataStoreService"):GetDataStore("PlayerData")
    store:SetAsync("player_" .. player.UserId, data)
end

-- GOOD: injected dependency, testable anywhere
local function saveData(player, data, dataStore)
    dataStore:SetAsync("player_" .. player.UserId, data)
end

-- In production: saveData(player, data, realStore)
-- In tests: saveData(player, data, mockStore)
```

### Module-Level Injection

```luau
local DataManager = {}
local _dataStoreService -- injected

function DataManager.init(dataStoreService)
    _dataStoreService = dataStoreService or game:GetService("DataStoreService")
end

function DataManager.save(player, data)
    local store = _dataStoreService:GetDataStore("PlayerData")
    store:SetAsync("player_" .. player.UserId, data)
end

return DataManager
```

---

## Mocking Roblox Services — Extended Examples

### Mock DataStoreService

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

function MockDataStore:UpdateAsync(key, transformFn)
    local current = self._data[key]
    local result = transformFn(current)
    self._data[key] = result
    return result
end

function MockDataStore:GetDataStore(name)
    return self
end
```

### Mock Signal (Event Simulation)

```luau
local MockSignal = {}
MockSignal.__index = MockSignal

function MockSignal.new()
    return setmetatable({ _connections = {} }, MockSignal)
end

function MockSignal:Connect(callback)
    local connection = {
        Connected = true,
        Disconnect = function(self)
            self.Connected = false
        end
    }
    table.insert(self._connections, { callback = callback, connection = connection })
    return connection
end

function MockSignal:Fire(...)
    for _, entry in self._connections do
        if entry.connection.Connected then
            entry.callback(...)
        end
    end
end
```

### Mock RemoteEvent

```luau
local MockRemoteEvent = {}
MockRemoteEvent.__index = MockRemoteEvent

function MockRemoteEvent.new()
    return setmetatable({
        _serverCallbacks = {},
        _clientCallbacks = {},
    }, MockRemoteEvent)
end

function MockRemoteEvent:OnServerEvent(callback)
    table.insert(self._serverCallbacks, callback)
end

function MockRemoteEvent:FireServer(...)
    for _, cb in self._serverCallbacks do
        task.spawn(cb, ...)
    end
end
```

---

## Integration Testing

### RemoteEvent Flows

```luau
describe("CombatService", function()
    it("should apply damage on valid attack", function()
        local mockRemote = MockRemoteEvent.new()
        local combatService = CombatService.new(mockRemote)

        mockRemote:FireServer("player1", "goblin", 25)

        expect(combatService:getHealth("goblin")).to.equal(75)
    end)
end)
```

### Persistence Cycles

```luau
describe("Data persistence cycle", function()
    it("should round-trip player data", function()
        local mockStore = MockDataStore.new()
        DataManager.init(mockStore)
        InventoryManager.init(DataManager)

        DataManager.save(player, { gold = 100 })
        local loaded = DataManager.load(player)

        expect(loaded.gold).to.equal(100)
    end)
end)
```

---

## CI/CD with Lune — Extended

### GitHub Actions Pipeline

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4

      - name: Install Aftman
        run: |
          curl -LsSf https://raw.githubusercontent.com/nicbarker/aftman/main/install.sh | sh
          echo "$HOME/.aftman/bin" >> $GITHUB_PATH

      - name: Install tools
        run: aftman install

      - name: Lint with Selene
        run: selene src/

      - name: Format check with StyLua
        run: stylua --check src/

      - name: Type check with luau-lsp
        run: luau-lsp analyze --settings .luaurc src/

      - name: Run tests
        run: lune run tests/run.luau
```

### Lune Test Runner Script

```lua
-- tests/run.luau
local TestEZ = require("@testez")
local results = TestEZ.TestBootstrap:run(
    { game:GetService("ReplicatedStorage") },
    TestEZ.Reporters.TextReporter
)

if results.failureCount > 0 then
    os.exit(1)
end
```

---

## MCP-Powered Smoke Tests

Use Studio MCP tools to automate basic smoke tests:

1. `start_stop_play` → enter play mode
2. Wait for initialization
3. `console_output` → scan for errors ("Infinite yield", "HTTP 429", "attempt to index nil")
4. `screen_capture` → visual verification
5. `start_stop_play` → stop play mode

---

## Priority: What to Test First

| Priority | Path | Why |
|----------|------|-----|
| 1 | DataStore save/load | Prevents player progress wipes |
| 2 | Monetization (ProcessReceipt) | Ensures players receive what they buy |
| 3 | Core math (damage, buffs, economy) | Catches balance-breaking bugs |
| 4 | Server validation (remotes) | Catches exploit vectors |

---

## Common Pitfalls

1. **Flaky tests from shared mutable state.** Use `beforeEach` to reset all state before each test.
2. **Tightly coupled code.** Hardcoding `game.Players.LocalPlayer` makes code untestable outside Studio.
3. **Order dependency.** Tests must run independently in any order.
4. **Manual-only testing.** Leads to regressions in edge cases that automated tests catch.
5. **Testing engine APIs in unit tests.** Unit tests should test logic; integration tests test engine interaction.
6. **Not committing `wally.lock`.** Causes non-reproducible installs across environments.
7. **Running TestEZ in external CI without mocks.** Engine-dependent tests will error immediately.

## Quality Checklist

- [ ] Pure logic functions have unit tests with mocked dependencies
- [ ] DataStore save/load cycles have round-trip tests
- [ ] Monetization flow has idempotency tests (ProcessReceipt called twice)
- [ ] RemoteEvent handlers validate argument types in tests
- [ ] CI pipeline runs lint (Selene), format (StyLua), type check (luau-lsp), and tests (Lune)
- [ ] `wally.lock` is committed
- [ ] No `game:GetService()` calls inside testable logic functions
