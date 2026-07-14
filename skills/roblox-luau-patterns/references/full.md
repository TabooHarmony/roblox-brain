# Luau Patterns & Architecture


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

## When to Load

Load this skill when the task involves:

- Designing classes with metatables (constructors, methods, inheritance)
- Async control flow (Promises, coroutines, pcall/xpcall, retry patterns)
- Module structure and organization (service pattern, singletons)
- Roblox-specific patterns (Instance creation, service access, events, task library)
- Choosing between architectural approaches (OOP vs modules vs flat functions)
- Error handling strategy (pcall wrapping, fallbacks, retry logic)

**Hand off to other skills when:**

- Pure syntax, tables, string patterns, sharp edges → `roblox-luau-core`
- Type annotations, generics, inference, strictness → `roblox-luau-types`
- Networking, data persistence, security → `roblox-networking`, `roblox-data`, `roblox-security`
- Performance profiling and optimization → `roblox-performance`

## Decision Rules

- Use metatable OOP when you need multiple instances with shared behavior
- Use module singletons (flat table with functions) for services that exist once
- Use a Promise library for async chains when the project already has one; otherwise use `task` and explicit error handling.
- Prefer `task.*` over deprecated globals (`wait`, `spawn`, `delay`) unconditionally
- Set `Instance.Parent` last after configuring all properties
- Clean up connections and instances when no longer needed (memory leaks are silent killers)
- Validate all data received from clients on the server

## Philosophy

Roblox games are long-running, stateful applications. Patterns should optimize for:

1. **Clarity over cleverness.** A new team member should understand the code structure in minutes.
2. **Cleanup by default.** Every connection, instance, and timer should have a clear owner and a clear destruction path.
3. **Fail gracefully.** DataStores, HTTP, and remote calls can all fail. Wrap them. Have fallbacks.
4. **Server authority.** The server is the source of truth. Clients request, servers validate and execute.

### Recommended Libraries

These open-source libraries are common options, not requirements. If the project already has an equivalent or uses different conventions, follow the existing patterns. Prefer vanilla `task`, `pcall`, `RBXScriptConnection`, `RemoteEvent`, and explicit tables when adding a dependency would not pay for itself.

- **Promise** (evaera/roblox-lua-promise) — async control flow, retry, chaining.
- **Trove** ([Sleitnick/RbxUtil](https://github.com/Sleitnick/RbxUtil)) — cleanup/lifecycle management.
- **Signal** (Sleitnick/RbxUtil) — typed custom signals.
- **Comm** (Sleitnick/RbxUtil) — typed client-server remotes and middleware.
- **TypedRemote** (Sleitnick/RbxUtil) — typed RemoteEvent, RemoteFunction, and UnreliableRemoteEvent builders.
- **Component** (Sleitnick/RbxUtil) — CollectionService tag binding with lifecycle.
- **Concur** (Sleitnick/RbxUtil) — cancellable concurrent task handling.
- **BufferUtil** (Sleitnick/RbxUtil) — buffer-oriented serialization helpers.
- **ProfileStore** (loleris/MadStudioRoblox) — session-locked DataStore with retry.
- **t** (osyrisrblx/t) — runtime type checking for remote validation and schemas.

RbxUtil is a useful maintained specimen because its repository includes tests, CI, generated API docs, and small modules that can be adopted independently. Do not import the whole collection by default. Read the module's current API and use only the piece that pays for its dependency and learning cost.

Do not treat archived frameworks as current defaults. Knit and Warp are useful historical references only; Jolt is a newer networking specimen that explicitly needs more testing. Prefer vanilla Luau and Roblox APIs when the project does not need a framework.

---

## OOP Patterns

### Metatable-Based Classes

```luau
-- Standard OOP pattern using metatables
local Weapon = {}
Weapon.__index = Weapon

export type Weapon = typeof(setmetatable(
    {} :: {
        name: string,
        damage: number,
        durability: number,
        maxDurability: number,
    },
    Weapon
))

-- Constructor uses . (static - no instance yet)
function Weapon.new(name: string, damage: number, durability: number): Weapon
    local self = setmetatable({}, Weapon)
    self.name = name
    self.damage = damage
    self.durability = durability
    self.maxDurability = durability
    return self
end

-- Methods use : (self is implicit, don't write it as a parameter)
function Weapon:attack(target: Humanoid): boolean
    if self.durability <= 0 then
        warn(`{self.name} is broken!`)
        return false
    end

    target:TakeDamage(self.damage)
    self.durability -= 1
    return true
end

function Weapon:repair()
    self.durability = self.maxDurability
end

function Weapon:toString(): string
    return `{self.name} (DMG: {self.damage}, DUR: {self.durability}/{self.maxDurability})`
end

-- Usage: . for constructor, : for methods
local sword = Weapon.new("Iron Sword", 25, 100)
sword:attack(targetHumanoid)
print(sword:toString())
```

### Inheritance via Metatable Chaining

```luau
-- Base class
local Entity = {}
Entity.__index = Entity

export type Entity = typeof(setmetatable(
    {} :: {
        name: string,
        health: number,
        maxHealth: number,
        position: Vector3,
    },
    Entity
))

function Entity.new(name: string, health: number, position: Vector3): Entity
    local self = setmetatable({}, Entity)
    self.name = name
    self.health = health
    self.maxHealth = health
    self.position = position
    return self
end

function Entity:takeDamage(amount: number)
    self.health = math.max(0, self.health - amount)
end

function Entity:isAlive(): boolean
    return self.health > 0
end

-- Derived class
local Enemy = {}
Enemy.__index = Enemy
setmetatable(Enemy, { __index = Entity }) -- inherit from Entity

export type Enemy = typeof(setmetatable(
    {} :: {
        name: string,
        health: number,
        maxHealth: number,
        position: Vector3,
        -- Enemy-specific fields
        attackDamage: number,
        aggroRange: number,
    },
    Enemy
))

function Enemy.new(name: string, health: number, position: Vector3, attackDamage: number): Enemy
    -- Call the parent constructor logic manually
    local self = setmetatable({}, Enemy) :: any
    self.name = name
    self.health = health
    self.maxHealth = health
    self.position = position
    self.attackDamage = attackDamage
    self.aggroRange = 50
    return self
end

function Enemy:attackTarget(target: Entity)
    local distance = (target.position - self.position).Magnitude
    if distance <= self.aggroRange then
        target:takeDamage(self.attackDamage)
    end
end

-- Usage: inherited methods also use :
local goblin = Enemy.new("Goblin", 50, Vector3.new(0, 0, 0), 10)
goblin:takeDamage(20)       -- inherited from Entity
goblin:attackTarget(player) -- defined on Enemy
print(goblin:isAlive())     -- inherited from Entity
```

### When to Use OOP vs Modules

- **OOP (metatables):** Multiple instances with shared behavior. Enemies, weapons, UI components, data models.
- **Module singleton:** One instance, acts as a service. CombatService, InventoryManager, MatchManager.
- **Flat functions:** Stateless utilities. Math helpers, string formatters, validation functions.

---

## Module-Based Service Pattern

```luau
-- A common Roblox pattern: modules that act as singletons/services
-- File: ServerScriptService/Services/CombatService.lua

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local CombatService = {}

local activeBuffs: { [Player]: { string } } = {}

function CombatService.init()
    Players.PlayerRemoving:Connect(function(player: Player)
        activeBuffs[player] = nil -- cleanup on leave
    end)
end

function CombatService.calculateDamage(attacker: Player, baseDamage: number): number
    local multiplier = 1.0
    local buffs = activeBuffs[attacker]
    if buffs then
        for _, buff in buffs do
            if buff == "strength" then
                multiplier += 0.5
            end
        end
    end
    return math.floor(baseDamage * multiplier)
end

function CombatService.addBuff(player: Player, buffName: string)
    if not activeBuffs[player] then
        activeBuffs[player] = {}
    end
    table.insert(activeBuffs[player], buffName)
end

function CombatService.removeBuff(player: Player, buffName: string)
    local buffs = activeBuffs[player]
    if not buffs then
        return
    end
    local index = table.find(buffs, buffName)
    if index then
        table.remove(buffs, index)
    end
end

return CombatService
```

### Module Structure Template

```luau
-- Standard module template
-- File: ReplicatedStorage/Modules/InventoryManager.lua

-- Services at the top
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

-- Dependencies
local Types = require(ReplicatedStorage.Shared.Types)
local Signal = require(ReplicatedStorage.Packages.Signal)

-- Constants
local MAX_SLOTS = 20
local STACK_LIMIT = 99

-- Module table
local InventoryManager = {}

-- Private state
local inventories: { [Player]: Types.Inventory } = {}

-- Public API with type annotations
function InventoryManager.getInventory(player: Player): Types.Inventory?
    return inventories[player]
end

function InventoryManager.addItem(player: Player, itemId: string, quantity: number): boolean
    local inventory = inventories[player]
    if not inventory then
        return false
    end
    -- ... implementation
    return true
end

-- Initialization
function InventoryManager.init()
    Players.PlayerAdded:Connect(function(player: Player)
        inventories[player] = { slots = {}, gold = 0 }
    end)

    Players.PlayerRemoving:Connect(function(player: Player)
        inventories[player] = nil
    end)
end

return InventoryManager
```

---

## Roblox-Specific Patterns

### Instance Creation

```luau
-- Create, configure, then ALWAYS set Parent last (avoids replication race)
local part = Instance.new("Part")
part.Name = "Floor"
part.Size = Vector3.new(50, 1, 50)
part.Anchored = true
part.Parent = workspace -- Parent last!
```

### Service Access

```luau
-- GetService is the canonical way to access Roblox services
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")
local HttpService = game:GetService("HttpService")
local CollectionService = game:GetService("CollectionService")
local PhysicsService = game:GetService("PhysicsService")
local MarketplaceService = game:GetService("MarketplaceService")
local DataStoreService = game:GetService("DataStoreService")
local Debris = game:GetService("Debris")

-- Services should be declared at the top of each script
-- and stored in local variables for performance and clarity
```

### Event Connections

```luau
-- Connecting to events returns an RBXScriptConnection
local Players = game:GetService("Players")

local connection: RBXScriptConnection
connection = Players.PlayerAdded:Connect(function(player: Player)
    print(`{player.Name} joined the game`)
end)

-- Disconnecting when no longer needed (prevents memory leaks)
connection:Disconnect()

-- One-shot connection with :Once()
Players.PlayerAdded:Once(function(player: Player)
    print(`First player to join: {player.Name}`)
    -- Automatically disconnects after firing once
end)

-- Waiting for an event to fire (yields the current thread)
local player = Players.PlayerAdded:Wait()
print(`{player.Name} joined`)

-- Common event patterns
local RunService = game:GetService("RunService")

-- Heartbeat fires every frame after physics (use for most game logic)
RunService.Heartbeat:Connect(function(deltaTime: number)
    -- deltaTime is seconds since last frame
end)

-- Stepped fires every frame before physics
RunService.Stepped:Connect(function(elapsedTime: number, deltaTime: number)
    -- use for input processing or pre-physics logic
end)

-- Property change events
local part = workspace:FindFirstChild("MyPart") :: Part
part:GetPropertyChangedSignal("Position"):Connect(function()
    print(`Part moved to {part.Position}`)
end)

-- Child events
workspace.ChildAdded:Connect(function(child: Instance)
    print(`New child: {child.Name}`)
end)
```

### Instance Tree Traversal

```luau
-- FindFirstChild: returns first direct child with name (or nil)
local head = character:FindFirstChild("Head")
if head then
    print("Found head")
end

-- FindFirstChild with recursive flag
local sword = workspace:FindFirstChild("Sword", true) -- searches entire subtree

-- FindFirstChildOfClass: by ClassName
local humanoid = character:FindFirstChildOfClass("Humanoid")

-- FindFirstChildWhichIsA: by class hierarchy (includes inherited classes)
local basePart = model:FindFirstChildWhichIsA("BasePart")

-- WaitForChild: yields until child exists (with optional timeout)
local tool = player.Backpack:WaitForChild("Sword")
local toolOrNil = player.Backpack:WaitForChild("Sword", 5) -- 5 second timeout

-- GetChildren: returns array of direct children
local children = workspace:GetChildren()
for _, child in children do
    print(child.Name)
end

-- GetDescendants: returns array of ALL descendants (recursive)
local allParts: { BasePart } = {}
for _, descendant in workspace:GetDescendants() do
    if descendant:IsA("BasePart") then
        table.insert(allParts, descendant)
    end
end

-- Filtering with CollectionService (tag-based)
local CollectionService = game:GetService("CollectionService")
local enemies = CollectionService:GetTagged("Enemy")
for _, enemy in enemies do
    print(enemy.Name)
end

-- Listen for tagged instances
CollectionService:GetInstanceAddedSignal("Enemy"):Connect(function(instance)
    setupEnemy(instance)
end)

CollectionService:GetInstanceRemovedSignal("Enemy"):Connect(function(instance)
    cleanupEnemy(instance)
end)
```

### Task Library

The `task` library is the modern replacement for deprecated globals `wait()`, `spawn()`, and `delay()`.

```luau
-- task.wait: yields the current thread for a duration (returns actual elapsed time)
local elapsed = task.wait(2) -- waits ~2 seconds
print(`Actually waited {elapsed} seconds`)

-- task.spawn: runs a function immediately in a new thread (resumes caller after)
task.spawn(function()
    print("This runs immediately in a new coroutine")
    task.wait(5)
    print("This runs 5 seconds later")
end)
print("This also runs immediately, after the spawned function yields")

-- task.delay: runs a function after a delay
task.delay(3, function()
    print("This runs after 3 seconds")
end)

-- task.defer: runs a function at the end of the current resumption cycle
-- Useful for deferring work without a delay
task.defer(function()
    print("This runs after the current thread and any task.spawn calls finish")
end)

-- task.cancel: cancels a thread created by task.spawn or task.delay
local thread = task.delay(10, function()
    print("This will never run")
end)
task.cancel(thread)

-- task.synchronize / task.desynchronize: for Parallel Luau
-- task.synchronize() -- switch to serial execution
-- task.desynchronize() -- switch to parallel execution
```

---

## Async Patterns

### pcall and xpcall for Error Handling

```luau
-- pcall wraps a function call and catches errors
local success, result = pcall(function()
    return game:GetService("DataStoreService"):GetDataStore("PlayerData")
end)

if success then
    print("Got data store:", result)
else
    warn("Failed to get data store:", result)
end

-- pcall with arguments (passed after the function)
local success, data = pcall(dataStore.GetAsync, dataStore, "player_123")

-- xpcall provides a custom error handler with stack trace
local success, result = xpcall(function()
    error("Something went wrong")
end, function(err)
    -- err is the error message
    warn("Error:", err)
    warn("Stack:", debug.traceback())
    return err -- returned as 'result' if success is false
end)

-- Pattern: retry with pcall
local function retryAsync<T>(maxAttempts: number, delayBetween: number, fn: () -> T): T?
    for attempt = 1, maxAttempts do
        local success, result = pcall(fn)
        if success then
            return result
        end
        if attempt < maxAttempts then
            warn(`Attempt {attempt} failed: {result}. Retrying in {delayBetween}s...`)
            task.wait(delayBetween)
        else
            warn(`All {maxAttempts} attempts failed. Last error: {result}`)
        end
    end
    return nil
end

-- Usage: retry DataStore calls
local data = retryAsync(3, 1, function()
    return dataStore:GetAsync("player_123")
end)
```

### Coroutines

```luau
-- Coroutines allow cooperative multitasking
local function producer(): ()
    for i = 1, 5 do
        coroutine.yield(i)
    end
end

local co = coroutine.create(producer)
for i = 1, 5 do
    local success, value = coroutine.resume(co)
    print(value) --> 1, 2, 3, 4, 5
end

-- coroutine.wrap creates a function that resumes automatically
local nextValue = coroutine.wrap(producer)
print(nextValue()) --> 1
print(nextValue()) --> 2

-- Practical example: staggered initialization
local function initSystems(systems: { { name: string, init: () -> () } })
    for _, system in systems do
        task.spawn(function()
            local success, err = pcall(system.init)
            if not success then
                warn(`Failed to initialize {system.name}: {err}`)
            else
                print(`{system.name} initialized`)
            end
        end)
    end
end
```

### Promise Pattern (roblox-lua-promise)

A Promise library is a common option for async control flow in Roblox. If your project uses one, install it as a module (for example via Wally or manually); otherwise use native `task`/`pcall` patterns.

```luau
local Promise = require(ReplicatedStorage.Packages.Promise)

-- Creating a Promise
local function loadPlayerData(player: Player)
    return Promise.new(function(resolve, reject, onCancel)
        local key = `player_{player.UserId}`

        -- Support cancellation
        local cancelled = false
        onCancel(function()
            cancelled = true
        end)

        local success, data = pcall(dataStore.GetAsync, dataStore, key)
        if cancelled then
            return
        end

        if success then
            resolve(data or {})
        else
            reject(`Failed to load data: {data}`)
        end
    end)
end

-- Chaining promises
loadPlayerData(player)
    :andThen(function(data)
        print("Data loaded:", data)
        return processData(data)
    end)
    :andThen(function(processed)
        applyData(player, processed)
    end)
    :catch(function(err)
        warn("Error:", err)
    end)
    :finally(function()
        print("Load attempt complete")
    end)

-- Promise.all: wait for multiple promises
Promise.all({
    loadPlayerData(player),
    loadInventory(player),
    loadSettings(player),
}):andThen(function(results)
    local data, inventory, settings = results[1], results[2], results[3]
    -- All loaded successfully
end):catch(function(err)
    warn("One or more loads failed:", err)
end)

-- Promise.race: first to resolve wins
Promise.race({
    fetchFromPrimary(),
    Promise.delay(5):andThen(function()
        return fetchFromBackup()
    end),
})

-- Promise.retry
Promise.retry(function()
    return loadPlayerData(player)
end, 3):andThen(function(data)
    print("Loaded after retry")
end)

-- Wrapping yielding code in a Promise
local function waitForCharacter(player: Player)
    return Promise.new(function(resolve)
        local character = player.Character or player.CharacterAdded:Wait()
        resolve(character)
    end)
end
```

---

## Best Practices

### Naming Conventions

```luau
-- PascalCase: classes, modules, services, types, enums
local CombatService = {}
local WeaponManager = require(script.WeaponManager)
type PlayerData = { name: string, level: number }

-- camelCase: variables, function names, method names, parameters
local playerHealth = 100
local function calculateDamage(baseDamage: number): number end
function Weapon:getDurability(): number end

-- UPPER_CASE: constants
local MAX_HEALTH = 100
local RESPAWN_DELAY = 5
local DEFAULT_SPEED = 16

-- Prefix private methods with underscore (convention, not enforced)
function MyClass:_internalMethod() end
local _cachedValue = nil
```

### Method Definitions

- Use `:` (colon) for instance methods - self is implicit
- Use `.` (dot) for constructors and static methods - self must be explicit

```luau
-- : for instance methods (self is implicit)
function MyClass:methodName()
    -- self refers to the instance
end

-- . for constructors and static methods (self must be explicit)
function MyClass.new()
    local self = setmetatable({}, MyClass)
    return self
end

-- Calling conventions match definition
obj:methodName()        -- colon: self passed implicitly
MyClass.new()           -- dot: no self
```

**Key rule:** `:` is syntactic sugar for `.` with automatic `self` injection. `obj:method(a)` is equivalent to `obj.method(obj, a)`.

### General Guidelines

- Use `local` for every variable and function declaration.
- Add type annotations on all public module function signatures.
- Use `task.wait()` / `task.spawn()` / `task.delay()` / `task.defer()` instead of deprecated globals.
- Use `typeof()` instead of `type()` for Roblox-aware type checking.
- Set `Instance.Parent` last after configuring all properties (avoids unnecessary replication and change events).
- Clean up event connections and instances when no longer needed to avoid memory leaks.
- Validate all data received from clients on the server. Never trust the client.
- Use `pcall` / `xpcall` around any call that can fail (DataStores, HTTP, etc.).
- Use backtick interpolation (`{expr}`) for all string building. Never use `..` concatenation.
- Use `table.freeze()` for configuration tables that should not be modified.
- Never use Luau reserved keywords as identifiers.
- Declare local functions before they are called - Luau has no hoisting.

---

## Anti-Patterns

### Deprecated Global Functions

```luau
-- BAD: deprecated, unpredictable resume timing, no cancellation
wait(2)
spawn(function() end)
delay(2, function() end)

-- GOOD: modern task library equivalents
task.wait(2)
task.spawn(function() end)
task.delay(2, function() end)
```

### Polling Instead of Events

```luau
-- BAD: polling wastes CPU cycles
while true do
    local target = findNearestEnemy()
    if target then
        attack(target)
    end
    task.wait(0.1)
end

-- GOOD: use events or Heartbeat with state checks
local RunService = game:GetService("RunService")
RunService.Heartbeat:Connect(function(dt: number)
    local target = findNearestEnemy()
    if target then
        attack(target)
    end
end)

-- GOOD: use events when possible
CollectionService:GetInstanceAddedSignal("Enemy"):Connect(function(enemy)
    onEnemySpawned(enemy)
end)
```

### String Concatenation in Loops

```luau
-- BAD: creates a new string every iteration (O(n^2) memory)
local result = ""
for i = 1, 1000 do
    result = result .. tostring(i) .. ","
end

-- GOOD: collect into table, join once (O(n))
local parts = {}
for i = 1, 1000 do
    table.insert(parts, tostring(i))
end
local result = table.concat(parts, ",")
```

### Missing pcall on Fallible Calls

```luau
-- BAD: crashes the script if the call fails
local data = dataStore:GetAsync("key")
local response = HttpService:RequestAsync({ Url = "https://api.example.com" })

-- GOOD: wrap in pcall
local success, data = pcall(dataStore.GetAsync, dataStore, "key")
if not success then
    warn("DataStore read failed:", data)
    data = {} -- fallback
end

local success, response = pcall(HttpService.RequestAsync, HttpService, {
    Url = "https://api.example.com",
})
if not success then
    warn("HTTP request failed:", response)
end
```

### Trusting Client Input

For server-authoritative validation patterns (type checking, range checking, ownership, rate limiting), see `roblox-networking` → Client Validation.

**Core rule:** Never trust client input. Every `OnServerEvent` handler must validate types, ranges, and ownership before processing.

---

## Common Mistakes

- Forgetting `MyClass.__index = MyClass` (methods won't resolve)
- Setting properties on the class table instead of `self` (shared across all instances)
- Not cleaning up connections on object destruction (memory leaks)
- Using raw coroutines where Promises would give better error propagation
- Calling `:Destroy()` without disconnecting signals first (Trove solves this)
- Forgetting pcall around DataStore/HTTP calls (silent script death)
- Using `wait()` instead of `task.wait()` (deprecated, unpredictable timing)
- Setting Parent before configuring properties (replication race)

## Quality Checklist

- [ ] Classes have `__index` set correctly
- [ ] Constructors use `.`, methods use `:`
- [ ] All fallible calls wrapped in pcall/xpcall
- [ ] Event connections have a clear cleanup path
- [ ] Instance.Parent set last
- [ ] No deprecated globals (wait/spawn/delay)
- [ ] Module has clear public API vs private state
- [ ] Async chains have error handling (`:catch()` or pcall)
- [ ] Player data cleaned up on PlayerRemoving
