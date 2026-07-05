# Luau Language Reference

## Overview

Load this reference when the task involves:

- General Luau syntax questions or code generation
- Type system usage, annotations, or generics
- Roblox-specific API patterns (services, events, instances)
- OOP design with metatables and module-based classes
- Async/concurrent programming (coroutines, Promises, task library)
- Performance optimization or idiomatic Luau style
- Debugging common pitfalls (1-based indexing, nil in tables, deprecated APIs)

Luau is Roblox's fork of Lua 5.1 with gradual typing, performance improvements, and additional built-in functions. It is NOT standard Lua 5.1 — it has its own type system, generics, `continue` keyword, compound assignment operators (`+=`, `-=`, etc.), string interpolation, and other extensions.

---

## Core Concepts

### Variables

All variables should be declared `local`. Global variables pollute the shared environment and cause hard-to-trace bugs.

```luau
-- Correct: always use local
local playerName = "Alice"
local score = 0
local isAlive = true

-- Constants use UPPER_CASE by convention
local MAX_HEALTH = 100
local RESPAWN_TIME = 5

-- Multiple assignment
local x, y, z = 1, 2, 3

-- Compound assignment (Luau extension, not in Lua 5.1)
score += 10
score -= 5
score *= 2
score /= 2
```

### Functions

```luau
-- Standard function declaration
local function calculateDamage(baseDamage: number, multiplier: number): number
    return baseDamage * multiplier
end

-- Anonymous function / closure
local onHit = function(target: Part)
    target:Destroy()
end

-- Variadic functions
local function logMessage(prefix: string, ...: any)
    local args = { ... }
    local message = prefix .. ": " .. table.concat(args, ", ")
    print(message)
end

-- Functions are first-class values
local function applyToAll(items: { Instance }, action: (Instance) -> ())
    for _, item in items do
        action(item)
    end
end

-- Multiple return values
local function getPosition(): (number, number, number)
    return 10, 20, 30
end

local x, y, z = getPosition()
```

### Tables

Tables are the only compound data structure in Luau. They serve as arrays, dictionaries, objects, and namespaces.

```luau
-- Array (sequential integer keys, 1-based)
local fruits = { "apple", "banana", "cherry" }
print(fruits[1]) --> "apple"
print(#fruits)   --> 3

-- Dictionary (string keys)
local player = {
    name = "Alice",
    health = 100,
    inventory = {},
}
print(player.name)       --> "Alice"
print(player["health"])  --> 100

-- Mixed table (legal but discouraged — see Sharp Edges)
-- Avoid mixing array and dictionary parts

-- Nested tables
local config = {
    graphics = {
        quality = "high",
        shadows = true,
    },
    audio = {
        volume = 0.8,
        music = true,
    },
}
print(config.graphics.quality) --> "high"

-- Table as a namespace / module
local MathUtils = {}

function MathUtils.lerp(a: number, b: number, t: number): number
    return a + (b - a) * t
end

function MathUtils.clampedLerp(a: number, b: number, t: number): number
    return MathUtils.lerp(a, b, math.clamp(t, 0, 1))
end
```

### Control Flow

```luau
-- if / elseif / else
local health = 50
if health <= 0 then
    print("Dead")
elseif health < 30 then
    print("Critical")
else
    print("Alive")
end

-- Numeric for (start, end, step)
for i = 1, 10 do
    print(i)
end

for i = 10, 1, -1 do
    print(i) -- countdown
end

-- Generic for with ipairs (array iteration, respects order)
local items = { "sword", "shield", "potion" }
for index, item in ipairs(items) do
    print(index, item)
end

-- Generalized iteration (Luau extension — preferred over ipairs/pairs)
for index, item in items do
    print(index, item)
end

-- Dictionary iteration
local stats = { health = 100, mana = 50, stamina = 75 }
for key, value in stats do
    print(key, value)
end

-- while loop
local count = 0
while count < 10 do
    count += 1
end

-- repeat-until loop (condition checked AFTER body, body always runs at least once)
local attempts = 0
repeat
    attempts += 1
    local success = attempts >= 3
until success

-- continue (Luau extension — skips to next iteration)
for i = 1, 10 do
    if i % 2 == 0 then
        continue
    end
    print(i) -- prints odd numbers only
end

-- break exits the loop
for i = 1, 100 do
    if i > 10 then
        break
    end
    print(i)
end
```

### String Manipulation

```luau
-- String interpolation (Luau extension — backtick strings)
local name = "Alice"
local level = 42
local message = `{name} reached level {level}!`
print(message) --> "Alice reached level 42!"

-- Expressions in interpolation
local price = 19.99
local tax = 0.08
print(`Total: ${price * (1 + tax)}`) --> "Total: $21.5892"

-- Concatenation (use sparingly — see Anti-Patterns)
local greeting = "Hello, " .. name .. "!"

-- Common string functions
print(string.len("hello"))           --> 5
print(string.upper("hello"))         --> "HELLO"
print(string.lower("HELLO"))         --> "hello"
print(string.sub("hello", 2, 4))     --> "ell"
print(string.rep("ab", 3))           --> "ababab"
print(string.reverse("hello"))       --> "olleh"
print(string.byte("A"))              --> 65
print(string.char(65))               --> "A"
print(string.find("hello world", "world")) --> 7 11
print(string.format("%.2f", 3.14159))     --> "3.14"

-- String patterns (NOT regex — see Common Idioms section)
local matched = string.match("score: 42", "%d+")
print(matched) --> "42"

-- string.split (Luau extension)
local parts = string.split("a,b,c", ",")
-- parts = {"a", "b", "c"}
```

### Math Operations

```luau
-- Arithmetic
local sum = 10 + 5       --> 15
local diff = 10 - 5      --> 5
local product = 10 * 5   --> 50
local quotient = 10 / 3  --> 3.3333...
local intDiv = 10 // 3   --> 3 (floor division, Luau extension)
local remainder = 10 % 3 --> 1
local power = 2 ^ 10     --> 1024

-- Math library
print(math.abs(-5))              --> 5
print(math.ceil(3.2))            --> 4
print(math.floor(3.8))           --> 3
print(math.max(1, 5, 3))         --> 5
print(math.min(1, 5, 3))         --> 1
print(math.sqrt(16))             --> 4
print(math.pi)                   --> 3.14159...
print(math.huge)                 --> inf
print(math.clamp(15, 0, 10))     --> 10 (Luau extension)
print(math.sign(-7))             --> -1 (Luau extension)
print(math.round(3.5))           --> 4 (Luau extension)

-- Random numbers
print(math.random())             --> [0, 1) float
print(math.random(10))           --> [1, 10] integer
print(math.random(5, 15))        --> [5, 15] integer

-- For better randomness, use Random.new()
local rng = Random.new()
print(rng:NextNumber())          --> [0, 1) float
print(rng:NextInteger(1, 100))   --> [1, 100] integer

-- Trigonometry (radians)
print(math.sin(math.pi / 2))    --> 1
print(math.cos(0))               --> 1
print(math.rad(180))             --> pi
print(math.deg(math.pi))        --> 180
```

---

## Type System

Luau uses **gradual typing**: types are optional and can be added incrementally. The type checker runs at analysis time and does not affect runtime behavior.

### Basic Type Annotations

```luau
-- Variable annotations
local name: string = "Alice"
local health: number = 100
local isAlive: boolean = true
local data: any = nil -- opt out of type checking

-- Function parameter and return types
local function add(a: number, b: number): number
    return a + b
end

-- Optional parameters
local function greet(name: string, title: string?): string
    if title then
        return `{title} {name}`
    end
    return name
end
```

### Table Types

```luau
-- Array type
local scores: { number } = { 100, 95, 87 }

-- Dictionary type
local config: { [string]: boolean } = {
    shadows = true,
    particles = false,
}

-- Typed table / record
type PlayerData = {
    name: string,
    level: number,
    inventory: { string },
    stats: {
        health: number,
        mana: number,
    },
}

local player: PlayerData = {
    name = "Alice",
    level = 10,
    inventory = { "sword", "shield" },
    stats = {
        health = 100,
        mana = 50,
    },
}
```

### Union and Intersection Types

```luau
-- Union type: value can be one of several types
local id: string | number = "abc123"
id = 42 -- also valid

-- Optional is shorthand for T | nil
local nickname: string? = nil -- equivalent to string | nil

-- Useful for function returns that may fail
local function findPlayer(name: string): Player | nil
    -- ...
    return nil
end
```

### Type Narrowing and Guards

```luau
-- typeof narrows types (Roblox-aware, preferred over type())
local function process(value: string | number)
    if typeof(value) == "string" then
        -- value is narrowed to string here
        print(string.upper(value))
    else
        -- value is narrowed to number here
        print(value * 2)
    end
end

-- Instance type checking with :IsA()
local function handlePart(instance: Instance)
    if instance:IsA("BasePart") then
        -- instance is narrowed to BasePart
        instance.Anchored = true
        instance.BrickColor = BrickColor.new("Bright red")
    end
end

-- assert for non-nil narrowing
local function getPlayerData(player: Player): PlayerData
    local leaderstats = player:FindFirstChild("leaderstats")
    assert(leaderstats, "Player missing leaderstats")
    -- leaderstats is now narrowed to non-nil
    return parseStats(leaderstats)
end
```

### Generics

```luau
-- Generic function
local function first<T>(list: { T }): T?
    return list[1]
end

local name = first({ "Alice", "Bob" }) -- inferred as string?
local num = first({ 1, 2, 3 })         -- inferred as number?

-- Generic type alias
type Result<T> = {
    success: boolean,
    value: T?,
    error: string?,
}

local function fetchData(): Result<PlayerData>
    return {
        success = true,
        value = { name = "Alice", level = 10, inventory = {}, stats = { health = 100, mana = 50 } },
        error = nil,
    }
end

-- Generic class-like pattern
type Stack<T> = {
    items: { T },
    push: (self: Stack<T>, value: T) -> (),
    pop: (self: Stack<T>) -> T?,
    peek: (self: Stack<T>) -> T?,
}
```

### Type Exports

```luau
-- In a ModuleScript, export types for other modules to use
-- File: ReplicatedStorage/Types.lua

export type WeaponData = {
    name: string,
    damage: number,
    rarity: "Common" | "Rare" | "Epic" | "Legendary",
    durability: number,
}

export type InventorySlot = {
    item: WeaponData?,
    quantity: number,
}

-- Consumers import with require
-- File: ServerScriptService/WeaponService.lua
local Types = require(game.ReplicatedStorage.Types)

local function createWeapon(name: string, damage: number): Types.WeaponData
    return {
        name = name,
        damage = damage,
        rarity = "Common",
        durability = 100,
    }
end
```

### Common Roblox Types

```luau
-- Instance hierarchy types
local part: Part = Instance.new("Part")
local model: Model = Instance.new("Model")
local player: Player = game.Players.LocalPlayer
local character: Model = player.Character or player.CharacterAdded:Wait()
local humanoid: Humanoid = character:FindFirstChildWhichIsA("Humanoid") :: Humanoid

-- Value types (these are NOT instances — they are value types / structs)
local position: Vector3 = Vector3.new(10, 5, 0)
local rotation: CFrame = CFrame.new(0, 10, 0) * CFrame.Angles(0, math.rad(90), 0)
local color: Color3 = Color3.fromRGB(255, 0, 0)
local size: Vector2 = Vector2.new(100, 50)
local region: Region3 = Region3.new(Vector3.new(-10, 0, -10), Vector3.new(10, 20, 10))
local ray: Ray = Ray.new(Vector3.new(0, 10, 0), Vector3.new(0, -1, 0))
local udim2: UDim2 = UDim2.new(0.5, 0, 0.5, 0)

-- Enum types
local material: Enum.Material = Enum.Material.Grass
local partType: Enum.PartType = Enum.PartType.Ball
```

---

## Roblox-Specific Patterns

### Instance Creation and Manipulation

```luau
-- Creating instances
local part = Instance.new("Part")
part.Name = "Floor"
part.Size = Vector3.new(50, 1, 50)
part.Position = Vector3.new(0, 0, 0)
part.Anchored = true
part.Material = Enum.Material.Grass
part.BrickColor = BrickColor.new("Bright green")
part.Parent = workspace -- ALWAYS set Parent last for performance

-- Cloning
local clone = part:Clone()
clone.Name = "FloorCopy"
clone.Position = Vector3.new(0, 0, 60)
clone.Parent = workspace

-- Destroying
part:Destroy() -- removes from hierarchy and disconnects all events
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

### RemoteEvents and RemoteFunctions

```luau
-- Server-client communication

-- SERVER SIDE
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local damageEvent = Instance.new("RemoteEvent")
damageEvent.Name = "DamageEvent"
damageEvent.Parent = ReplicatedStorage

-- Listen for client requests
damageEvent.OnServerEvent:Connect(function(player: Player, targetName: string, amount: number)
    -- ALWAYS validate client input on the server
    if typeof(targetName) ~= "string" then
        return
    end
    if typeof(amount) ~= "number" or amount < 0 or amount > 100 then
        return
    end

    local target = Players:FindFirstChild(targetName)
    if not target then
        return
    end

    -- Process validated request
    applyDamage(target, amount)
end)

-- Fire to a specific client
damageEvent:FireClient(somePlayer, "You took damage!", 25)

-- Fire to all clients
damageEvent:FireAllClients("Boss spawned!", bossPosition)

-- CLIENT SIDE
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local damageEvent = ReplicatedStorage:WaitForChild("DamageEvent")

-- Listen for server messages
damageEvent.OnClientEvent:Connect(function(message: string, data: any)
    print(message)
end)

-- Send request to server
damageEvent:FireServer("EnemyA", 50)
```

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

function Weapon.new(name: string, damage: number, durability: number): Weapon
    local self = setmetatable({}, Weapon)
    self.name = name
    self.damage = damage
    self.durability = durability
    self.maxDurability = durability
    return self
end

function Weapon.attack(self: Weapon, target: Humanoid): boolean
    if self.durability <= 0 then
        warn(`{self.name} is broken!`)
        return false
    end

    target:TakeDamage(self.damage)
    self.durability -= 1
    return true
end

function Weapon.repair(self: Weapon)
    self.durability = self.maxDurability
end

function Weapon.toString(self: Weapon): string
    return `{self.name} (DMG: {self.damage}, DUR: {self.durability}/{self.maxDurability})`
end

-- Usage
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

function Entity.takeDamage(self: Entity, amount: number)
    self.health = math.max(0, self.health - amount)
end

function Entity.isAlive(self: Entity): boolean
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

function Enemy.attackTarget(self: Enemy, target: Entity)
    local distance = (target.position - self.position).Magnitude
    if distance <= self.aggroRange then
        target:takeDamage(self.attackDamage)
    end
end

-- Usage
local goblin = Enemy.new("Goblin", 50, Vector3.new(0, 0, 0), 10)
goblin:takeDamage(20)       -- inherited from Entity
goblin:attackTarget(player) -- defined on Enemy
print(goblin:isAlive())     -- inherited from Entity
```

### Module-Based Service Pattern

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

The `Promise` library is the community-standard for async control flow in Roblox. It must be installed as a module (e.g., via Wally or manually).

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

## Common Idioms

### Table Operations

```luau
-- table.insert: append to array
local queue = {}
table.insert(queue, "task1")
table.insert(queue, "task2")
-- queue = {"task1", "task2"}

-- table.insert at index: insert at position (shifts others right)
table.insert(queue, 1, "urgent")
-- queue = {"urgent", "task1", "task2"}

-- table.remove: remove by index (shifts others left), returns removed value
local removed = table.remove(queue, 1) --> "urgent"

-- table.remove without index removes last element
local last = table.remove(queue) --> "task2"

-- table.find: search for value in array (returns index or nil)
local fruits = { "apple", "banana", "cherry" }
local index = table.find(fruits, "banana") --> 2
local missing = table.find(fruits, "grape") --> nil

-- table.sort: in-place sort
local numbers = { 5, 3, 8, 1, 9 }
table.sort(numbers) -- ascending by default
-- numbers = {1, 3, 5, 8, 9}

-- Custom sort comparator
local players = {
    { name = "Alice", score = 150 },
    { name = "Bob", score = 200 },
    { name = "Charlie", score = 100 },
}
table.sort(players, function(a, b)
    return a.score > b.score -- descending by score
end)

-- table.concat: join array elements into string
local parts = { "Hello", "world", "!" }
print(table.concat(parts, " ")) --> "Hello world !"

-- table.freeze / table.isfrozen (Luau extension — immutable tables)
local CONFIG = table.freeze({
    MAX_PLAYERS = 50,
    ROUND_TIME = 300,
    MAP_SIZE = 500,
})
-- CONFIG.MAX_PLAYERS = 100 --> ERROR: attempt to modify a frozen table

-- table.clone (Luau extension — shallow copy)
local original = { 1, 2, 3, sub = { 4, 5 } }
local copy = table.clone(original)
copy[1] = 99
print(original[1]) --> 1 (not affected)
-- NOTE: sub-tables are still shared references (shallow copy)

-- table.move (copy elements between tables or within a table)
local src = { 10, 20, 30, 40, 50 }
local dst = {}
table.move(src, 2, 4, 1, dst) -- copy src[2..4] into dst starting at dst[1]
-- dst = {20, 30, 40}

-- table.clear (Luau extension — remove all keys, keep table reference)
local t = { 1, 2, 3 }
table.clear(t) -- t is now empty but same reference

-- Deep copy utility (not built-in — write your own)
local function deepCopy<T>(original: T): T
    if typeof(original) ~= "table" then
        return original
    end
    local copy = table.clone(original :: any)
    for key, value in copy do
        if typeof(value) == "table" then
            copy[key] = deepCopy(value)
        end
    end
    return copy :: T
end
```

### String Patterns

Luau uses **Lua patterns**, which are NOT regular expressions. They are simpler and more limited.

```luau
-- Character classes
-- %a  letters          %A  non-letters
-- %d  digits           %D  non-digits
-- %l  lowercase        %L  non-lowercase
-- %u  uppercase        %U  non-uppercase
-- %w  alphanumeric     %W  non-alphanumeric
-- %s  whitespace       %S  non-whitespace
-- %p  punctuation      %P  non-punctuation
-- .   any character
-- %%  literal %

-- Quantifiers
-- *   0 or more (greedy)
-- +   1 or more (greedy)
-- -   0 or more (lazy)
-- ?   0 or 1

-- string.match: extract matches
local year, month, day = string.match("2026-03-04", "(%d+)-(%d+)-(%d+)")
print(year, month, day) --> "2026" "03" "04"

-- string.gmatch: iterate over all matches
local text = "score=100, level=42, health=75"
for key, value in string.gmatch(text, "(%w+)=(%d+)") do
    print(key, value)
end

-- string.gsub: replace matches
local cleaned = string.gsub("Hello   World", "%s+", " ")
print(cleaned) --> "Hello World"

-- Escaping pattern characters: use % before special chars
-- Special chars: ( ) . % + - * ? [ ] ^ $
local escaped = string.gsub("file.txt", "%.", "_")
print(escaped) --> "file_txt"

-- Anchors
-- ^ matches start of string
-- $ matches end of string
local isEmail = string.match("user@example.com", "^%w+@%w+%.%w+$") ~= nil
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

### Math Helpers

```luau
-- Clamping values
local health = math.clamp(currentHealth, 0, MAX_HEALTH)

-- Linear interpolation
local function lerp(a: number, b: number, t: number): number
    return a + (b - a) * t
end

-- Mapping a value from one range to another
local function map(value: number, inMin: number, inMax: number, outMin: number, outMax: number): number
    return outMin + (outMax - outMin) * ((value - inMin) / (inMax - inMin))
end

-- Distance between two Vector3s
local distance = (posA - posB).Magnitude

-- Normalized direction
local direction = (target - origin).Unit

-- Rounding to decimal places
local function roundTo(value: number, places: number): number
    local factor = 10 ^ places
    return math.round(value * factor) / factor
end
print(roundTo(3.14159, 2)) --> 3.14
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
function Weapon.getDurability(self: Weapon): number end

-- UPPER_CASE: constants
local MAX_HEALTH = 100
local RESPAWN_DELAY = 5
local DEFAULT_SPEED = 16

-- Prefix private members with underscore (convention, not enforced)
function MyClass._internalMethod(self: MyClass) end
local _cachedValue = nil
```

### Module Structure

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

### General Guidelines

- Use `local` for every variable and function declaration.
- Add type annotations on all public module function signatures.
- Use `task.wait()` / `task.spawn()` / `task.delay()` / `task.defer()` instead of deprecated globals.
- Use `typeof()` instead of `type()` for Roblox-aware type checking.
- Set `Instance.Parent` last after configuring all properties (avoids unnecessary replication and change events).
- Clean up event connections and instances when no longer needed to avoid memory leaks.
- Validate all data received from clients on the server. Never trust the client.
- Use `pcall` / `xpcall` around any call that can fail (DataStores, HTTP, etc.).
- Prefer `string.format()` or string interpolation over `..` concatenation in hot paths.
- Use `table.freeze()` for configuration tables that should not be modified.

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

-- GOOD: string interpolation for small, fixed concatenations is fine
local name = `{firstName} {lastName}`
```

### Global Variables

```luau
-- BAD: pollutes shared environment, hard to track, no type checking
score = 0
function updateScore(amount)
    score += amount
end

-- GOOD: local variables, module scope
local score = 0
local function updateScore(amount: number)
    score += amount
end
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

```luau
-- BAD: applying client values without validation
remoteEvent.OnServerEvent:Connect(function(player, damage, targetName)
    local target = Players:FindFirstChild(targetName)
    target.Character.Humanoid:TakeDamage(damage) -- client controls damage!
end)

-- GOOD: validate everything, use server-authoritative logic
remoteEvent.OnServerEvent:Connect(function(player: Player, targetName: unknown)
    -- Type validation
    if typeof(targetName) ~= "string" then
        return
    end

    -- Existence validation
    local target = Players:FindFirstChild(targetName)
    if not target or not target.Character then
        return
    end

    local targetHumanoid = target.Character:FindFirstChildOfClass("Humanoid")
    if not targetHumanoid then
        return
    end

    -- Server calculates damage based on attacker's weapon, not client data
    local weapon = getEquippedWeapon(player)
    if not weapon then
        return
    end

    -- Range check
    local attackerPos = player.Character and player.Character:GetPivot().Position
    local targetPos = target.Character:GetPivot().Position
    if not attackerPos or (attackerPos - targetPos).Magnitude > weapon.range then
        return
    end

    -- Cooldown check
    if not canAttack(player) then
        return
    end

    targetHumanoid:TakeDamage(weapon.damage)
end)
```

---

## Sharp Edges

### 1-Based Indexing

Luau arrays are 1-indexed. The first element is `array[1]`, not `array[0]`.

```luau
local items = { "first", "second", "third" }
print(items[1]) --> "first"
print(items[0]) --> nil (NOT an error, just nil)

-- Off-by-one errors are common when porting from other languages
for i = 1, #items do -- correct: 1 to length
    print(items[i])
end
```

### The `#` Operator and Nil Gaps

The `#` (length) operator is only reliable for **contiguous arrays** with no nil gaps.

```luau
-- Reliable: contiguous array
local a = { 1, 2, 3, 4, 5 }
print(#a) --> 5 (correct)

-- UNRELIABLE: array with nil gap
local b = { 1, 2, nil, 4, 5 }
print(#b) --> could be 2 or 5 (undefined behavior!)

-- The length operator finds ANY valid boundary where t[n] ~= nil and t[n+1] == nil
-- With gaps, multiple boundaries exist, and the result is unpredictable

-- SAFE: if you need to handle sparse data, use a dictionary with explicit count
local sparse: { [number]: string } = {}
local count = 0
sparse[1] = "a"
count += 1
sparse[5] = "e"
count += 1
-- Use count, not #sparse
```

### Nil in Tables

```luau
-- Setting a table value to nil REMOVES the key
local t = { a = 1, b = 2, c = 3 }
t.b = nil
-- t is now { a = 1, c = 3 } — "b" key no longer exists

-- This means you cannot store nil as a meaningful value in a table
-- Use a sentinel value instead if you need to distinguish "absent" from "nil"
local NONE = newproxy(false) -- unique sentinel
local cache = {}
cache["key"] = NONE -- means "we checked, value is absent"
-- cache["other"] is nil, meaning "we haven't checked yet"

-- nil in arrays causes gaps (see # operator issue above)
local list = { 1, 2, 3 }
list[2] = nil -- creates a gap — DO NOT DO THIS
-- Use table.remove(list, 2) instead to shift elements down
```

### Metatables: Powerful but Error-Prone

```luau
-- Common mistake: forgetting __index
local MyClass = {}
-- Missing: MyClass.__index = MyClass

function MyClass.new()
    return setmetatable({}, MyClass)
end

function MyClass.doSomething(self: any)
    print("doing something")
end

local obj = MyClass.new()
obj:doSomething() --> ERROR: attempt to call a nil value
-- Because __index is not set, method lookup fails

-- Common mistake: using . instead of : for method definitions
function MyClass.method(self: any) end  -- explicit self (works with both . and :)
function MyClass:method() end            -- implicit self (syntactic sugar)
-- Both are valid, but be consistent. The explicit self style with type annotation
-- is preferred in modern Luau for better type checking.

-- Common mistake: modifying the metatable instead of the instance
function MyClass.setName(self: any, name: string)
    -- BAD: this sets it on the class table, shared by all instances!
    MyClass.name = name

    -- GOOD: set on the instance
    self.name = name
end
```

### Equality and Type Coercion

```luau
-- Luau does NOT coerce types in comparisons (unlike JavaScript)
print(0 == "0")    --> false
print(1 == true)   --> false
print("" == false) --> false

-- Only nil and false are falsy
-- 0, "", and empty tables are TRUTHY
if 0 then print("0 is truthy") end         --> prints
if "" then print("empty string is truthy") end --> prints
if {} then print("empty table is truthy") end  --> prints

-- This means you cannot use `if value then` to check for empty strings or zero
-- Be explicit:
if value ~= nil and value ~= "" then end
if value ~= nil and value ~= 0 then end
```

### Table Reference Semantics

```luau
-- Tables are passed and assigned by REFERENCE, not by value
local original = { 1, 2, 3 }
local alias = original
alias[1] = 99
print(original[1]) --> 99 (both point to the same table)

-- To get an independent copy, use table.clone (shallow) or a deep copy function
local copy = table.clone(original)
copy[1] = 0
print(original[1]) --> 99 (unaffected)

-- But nested tables are still shared in a shallow clone
local nested = { data = { 1, 2, 3 } }
local shallowCopy = table.clone(nested)
shallowCopy.data[1] = 99
print(nested.data[1]) --> 99 (shared reference!)
-- Use a deep copy for nested structures
```

### Scope and Closures

```luau
-- Common loop closure bug
local functions = {}
for i = 1, 5 do
    functions[i] = function()
        return i
    end
end
-- In Luau, each loop iteration creates a new 'i' variable,
-- so this actually works correctly (unlike some other languages)
print(functions[1]()) --> 1
print(functions[5]()) --> 5

-- But watch out with while loops — the variable is shared
local fns = {}
local i = 1
while i <= 5 do
    fns[i] = function()
        return i
    end
    i += 1
end
print(fns[1]()) --> 6 (all functions share the same 'i' which is now 6)

-- Fix: capture the value in a local
local fns2 = {}
local j = 1
while j <= 5 do
    local captured = j
    fns2[j] = function()
        return captured
    end
    j += 1
end
print(fns2[1]()) --> 1 (correct)
```
