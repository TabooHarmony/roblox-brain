# Roblox Game Architecture Reference

---

## 1. Overview

**Load this reference when:**

- Starting a new Roblox game from scratch and need to decide where code and assets live
- Organizing or refactoring an existing codebase that has grown unwieldy
- Answering architecture questions: "Where should this script go?", "How should client talk to server?", "How do I structure modules?"
- Onboarding onto a Roblox project and need to understand the standard conventions
- Choosing between a flat script layout and a framework like Knit

This document covers the Roblox data model, service hierarchy, script types, client-server communication, module patterns, framework options, folder organization, best practices, and anti-patterns.

---

## 2. Core Concepts

### The Data Model

Roblox games are built on a **tree of Instances**. Every object (parts, scripts, UI elements, sounds) is an Instance that lives somewhere in a hierarchy rooted at `game` (class `DataModel`). The hierarchy determines behavior: a `Script` placed in `ServerScriptService` runs on the server, but the same `Script` placed in `StarterPlayerScripts` will not run at all (only `LocalScript` and client-side `Script` run there).

### Client vs. Server Execution

| Aspect | Server | Client |
|---|---|---|
| **Runs on** | Roblox datacenter (one instance per game server) | Each player's device |
| **Script types** | `Script` (Luau), `ModuleScript` (when required by a server script) | `LocalScript`, `ModuleScript` (when required by a local script) |
| **Trust level** | Authoritative -- owns game state, data stores, physics arbitration | Untrusted -- can be exploited; never trust client input blindly |
| **Access** | Can see everything in the data model | Cannot see `ServerScriptService` or `ServerStorage` |

### Replication Model

Roblox automatically replicates (syncs) parts of the data model from server to clients:

- **Server to all clients:** Anything in `Workspace`, `ReplicatedStorage`, `ReplicatedFirst`, `Lighting`, `SoundService`, `Chat`, and `Teams` is visible to every connected client.
- **Server-only (hidden from clients):** `ServerScriptService` and `ServerStorage` are never sent to clients. This is the correct place for server logic and secret assets.
- **Per-player:** Each player gets their own `PlayerGui` (cloned from `StarterGui`), `PlayerScripts` (cloned from `StarterPlayerScripts`), `StarterGear` (cloned from `StarterPack`), and `Backpack`.
- **Client to server:** Clients can modify their own character and certain local objects, but those changes do **not** replicate to the server unless the server has granted network ownership of that instance.

**Key rule:** If the server creates or changes an instance in a replicated container, all clients see it. If a client creates something locally, only that client sees it (unless the server replicates it).

---

## 3. Service Hierarchy

### ServerScriptService

**Purpose:** Contains `Script` instances that run exclusively on the server. Clients cannot see or access anything inside.

**Use for:**
- Core game logic (round systems, match management, scoring)
- Data persistence (DataStoreService calls)
- Server-side validation of player actions
- Anti-cheat enforcement
- NPC/AI controllers
- Server-side modules required only by server scripts

```
ServerScriptService/
  GameManager.server.lua        -- Script: round system
  DataManager.server.lua        -- Script: save/load player data
  Modules/
    CombatService.lua           -- ModuleScript: damage calculations
    ShopService.lua             -- ModuleScript: purchase validation
```

### ServerStorage

**Purpose:** A server-only container for assets and modules that clients should never see or download.

**Use for:**
- Map models that get cloned into Workspace on demand
- Enemy/NPC models before spawning
- Server-only ModuleScripts (utility libraries, data schemas)
- Templates that should not exist on the client until needed

```
ServerStorage/
  Maps/
    DesertArena.rbxm
    ForestArena.rbxm
  Templates/
    Loot/
      CommonChest.rbxm
  Modules/
    DataSchema.lua
```

### ReplicatedStorage

**Purpose:** Shared container visible to both server and client. Content is replicated to every client on join.

**Use for:**
- `RemoteEvent` and `RemoteFunction` instances (the communication bridge)
- Shared `ModuleScript` modules (utilities, constants, types, shared classes)
- Assets both sides reference (item models, particle effects, shared animations)
- Configuration values / game settings that both sides need

```
ReplicatedStorage/
  Remotes/
    DamageEvent.RemoteEvent
    ShopPurchase.RemoteFunction
  Modules/
    ItemData.lua                -- shared item definitions
    MathUtils.lua               -- shared utility functions
    Types.lua                   -- shared type definitions
  Assets/
    Effects/
      HitEffect.rbxm
```

### ReplicatedFirst

**Purpose:** Scripts here run on the client **before** anything else loads. Content replicates to clients first.

**Use for:**
- Loading screens (show UI while the game streams in)
- Early client initialization
- Keeping it minimal -- only what is needed before the game fully loads

```
ReplicatedFirst/
  LoadingScreen.client.lua      -- LocalScript: shows loading UI
```

### StarterGui

**Purpose:** UI template container. On each player spawn (or respawn, depending on `ResetOnSpawn`), the contents are **cloned** into that player's `PlayerGui`.

**Use for:**
- HUD elements (health bars, score displays, minimaps)
- Menu screens (settings, inventory, shop)
- UI-controlling LocalScripts that live inside ScreenGui

```
StarterGui/
  HUD.ScreenGui
    HealthBar.Frame
    ScoreLabel.TextLabel
    HUDController.client.lua    -- LocalScript managing HUD updates
  ShopMenu.ScreenGui
    ShopController.client.lua
```

> **Note:** Set `ScreenGui.ResetOnSpawn = false` for persistent UI that should not re-clone on character respawn.

### StarterPlayer / StarterPlayerScripts

**Purpose:** `LocalScript` instances here are cloned into each player's `PlayerScripts` folder once on join. They persist across respawns.

**Use for:**
- Camera controllers
- Input handling systems
- Client-side game managers
- Music/ambient sound controllers

```
StarterPlayer/
  StarterPlayerScripts/
    CameraController.client.lua
    InputManager.client.lua
    ClientBootstrap.client.lua
```

### StarterPlayer / StarterCharacterScripts

**Purpose:** Scripts here are cloned into the player's `Character` model each time the character spawns. They are destroyed when the character dies.

**Use for:**
- Per-character behaviors (footstep sounds, animation controllers)
- Character-specific effects (trails, auras)
- Anything that should reset on death

```
StarterPlayer/
  StarterCharacterScripts/
    FootstepSounds.client.lua
    AnimationController.client.lua
```

### StarterPack

**Purpose:** `Tool` instances here are cloned into each player's `Backpack` on spawn.

**Use for:**
- Default weapons or items every player starts with
- Tools with embedded LocalScripts and Scripts

```
StarterPack/
  Sword.Tool
    SwordClient.client.lua
    SwordServer.server.lua
    Handle.Part
```

### Workspace

**Purpose:** The 3D world. Everything visible in the game exists here at runtime: parts, models, terrain, cameras.

**Use for:**
- The physical game world (terrain, buildings, decorations)
- Spawned entities at runtime (cloned from ServerStorage)
- The Camera (each client has a local `Workspace.CurrentCamera`)

**Do NOT place Scripts directly in Workspace.** Use `ServerScriptService` instead. Workspace scripts are accessible to exploiters and create organizational chaos.

---

## 4. Script Types

### Script (Server Script)

- **Runs on:** Server
- **Valid containers:** `ServerScriptService`, `ServerStorage` (when parented under certain conditions), `Workspace` (discouraged)
- **File convention:** `*.server.lua` in Rojo projects
- **Access:** Full access to server APIs (`DataStoreService`, `MessagingService`, `HttpService`, etc.)

```lua
-- ServerScriptService/GameManager.server.lua
local Players = game:GetService("Players")

Players.PlayerAdded:Connect(function(player)
    print(player.Name .. " joined the server")
end)
```

### LocalScript (Client Script)

- **Runs on:** Client (the specific player's device)
- **Valid containers:** `StarterPlayerScripts`, `StarterCharacterScripts`, `StarterGui`, `StarterPack`, a player's `Backpack`, `PlayerGui`, `PlayerScripts`, or `Character`
- **File convention:** `*.client.lua` in Rojo projects
- **Access:** Client APIs (`UserInputService`, `ContextActionService`, `Camera`, local player's GUI)

```lua
-- StarterPlayerScripts/InputManager.client.lua
local UserInputService = game:GetService("UserInputService")

UserInputService.InputBegan:Connect(function(input, gameProcessed)
    if gameProcessed then return end
    if input.KeyCode == Enum.KeyCode.E then
        print("Player pressed E")
    end
end)
```

### ModuleScript

- **Runs on:** Whichever side `require()`s it (server if required by a Script, client if required by a LocalScript)
- **Valid containers:** Anywhere, but location determines who can access it
  - `ServerScriptService` or `ServerStorage` -- server-only modules
  - `ReplicatedStorage` -- shared modules (accessible by both sides)
  - `StarterPlayerScripts` -- client-only modules
- **File convention:** `*.lua` (no `.server` or `.client` suffix) in Rojo projects
- **Returns:** Exactly one value (typically a table/dictionary acting as a module)

```lua
-- ReplicatedStorage/Modules/MathUtils.lua
local MathUtils = {}

function MathUtils.lerp(a: number, b: number, t: number): number
    return a + (b - a) * t
end

function MathUtils.clamp(value: number, min: number, max: number): number
    return math.max(min, math.min(max, value))
end

return MathUtils
```

**Requiring:**
```lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local MathUtils = require(ReplicatedStorage.Modules.MathUtils)

local result = MathUtils.lerp(0, 100, 0.5) -- 50
```

---

## 5. Client-Server Communication

### RemoteEvent (Async, One-Way)

Use for fire-and-forget messages. The sender does not wait for a response.

**Server to Client:**
```lua
-- ReplicatedStorage/Remotes/NotifyEvent (RemoteEvent instance)

-- SERVER: fire to one client
local NotifyEvent = game:GetService("ReplicatedStorage").Remotes.NotifyEvent

NotifyEvent:FireClient(player, "You picked up a coin!", 1)

-- SERVER: fire to ALL clients
NotifyEvent:FireAllClients("A boss has spawned!")
```

```lua
-- CLIENT: listen for server messages
local NotifyEvent = game:GetService("ReplicatedStorage").Remotes.NotifyEvent

NotifyEvent.OnClientEvent:Connect(function(message, amount)
    print("Server says:", message, amount)
end)
```

**Client to Server:**
```lua
-- CLIENT: fire to server
local DamageEvent = game:GetService("ReplicatedStorage").Remotes.DamageEvent
DamageEvent:FireServer(targetId, 25)
```

```lua
-- SERVER: listen for client messages (player is auto-injected as first arg)
local DamageEvent = game:GetService("ReplicatedStorage").Remotes.DamageEvent

DamageEvent.OnServerEvent:Connect(function(player, targetId, damage)
    -- ALWAYS validate! Never trust the client.
    if not isValidTarget(targetId) then return end
    if damage > MAX_ALLOWED_DAMAGE then return end

    applyDamage(player, targetId, damage)
end)
```

### RemoteFunction (Sync, Two-Way / Request-Response)

Use when the caller needs a return value. **Only use `InvokeServer` (client calling server).** Avoid `InvokeClient` because if the client disconnects or errors, the server thread hangs.

```lua
-- CLIENT: request data from server
local GetInventory = game:GetService("ReplicatedStorage").Remotes.GetInventory

local inventory = GetInventory:InvokeServer()
for _, item in inventory do
    print(item.Name, item.Quantity)
end
```

```lua
-- SERVER: handle the request
local GetInventory = game:GetService("ReplicatedStorage").Remotes.GetInventory

GetInventory.OnServerInvoke = function(player)
    -- player is auto-injected
    local data = DataManager.getPlayerData(player)
    return data.Inventory
end
```

> **Warning:** Never use `RemoteFunction:InvokeClient()`. If the client's callback errors or the player leaves, the server-side calling thread yields forever. Use `RemoteEvent` pairs instead if you need server-to-client request/response.

### BindableEvent (Same-Side Communication)

Use for decoupled communication between scripts on the **same** side (server-to-server or client-to-client). Does not cross the network boundary.

```lua
-- SERVER: script A fires, script B listens
local RoundEndEvent = Instance.new("BindableEvent")
RoundEndEvent.Name = "RoundEndEvent"
RoundEndEvent.Parent = game:GetService("ServerScriptService")

-- Script A
RoundEndEvent:Fire("Team Alpha", 15)

-- Script B
RoundEndEvent.Event:Connect(function(winningTeam, score)
    print(winningTeam .. " won with " .. score .. " points")
end)
```

### UnreliableRemoteEvent (High-Frequency, Loss-Tolerant)

Use for data that is sent very frequently where occasional packet loss is acceptable. Roblox may drop packets to reduce bandwidth. Ideal for cosmetic/visual updates.

**Use cases:** Character facing direction, cursor position, cosmetic effects, real-time position hints.

**Do NOT use for:** Damage, purchases, state changes, anything where a missed packet causes bugs.

```lua
-- ReplicatedStorage/Remotes/CursorPosition (UnreliableRemoteEvent instance)

-- CLIENT: send cursor position every frame
local RunService = game:GetService("RunService")
local CursorEvent = game:GetService("ReplicatedStorage").Remotes.CursorPosition

RunService.RenderStepped:Connect(function()
    local mousePos = UserInputService:GetMouseLocation()
    CursorEvent:FireServer(mousePos)
end)
```

```lua
-- SERVER: relay to other players
CursorEvent.OnServerEvent:Connect(function(player, mousePos)
    -- Relay to everyone except the sender
    for _, otherPlayer in Players:GetPlayers() do
        if otherPlayer ~= player then
            CursorEvent:FireClient(otherPlayer, player, mousePos)
        end
    end
end)
```

### Communication Summary Table

| Type | Direction | Blocking? | Reliable? | Use Case |
|---|---|---|---|---|
| `RemoteEvent` | Client <-> Server | No | Yes | Actions, notifications, state changes |
| `RemoteFunction` | Client -> Server only (safe) | Yes (yields) | Yes | Data requests, queries |
| `BindableEvent` | Same side | No | N/A (local) | Decoupled same-side messaging |
| `BindableFunction` | Same side | Yes (yields) | N/A (local) | Same-side request/response |
| `UnreliableRemoteEvent` | Client <-> Server | No | No | High-frequency cosmetic data |

---

## 6. Module Script Architecture

### Basic Module Pattern

Every ModuleScript returns a single table. Functions and data are fields on that table.

```lua
-- ReplicatedStorage/Modules/InventoryModule.lua
local InventoryModule = {}

local playerInventories: { [Player]: { [string]: number } } = {}

function InventoryModule.init()
    -- Called once during startup to wire up connections
    game:GetService("Players").PlayerRemoving:Connect(function(player)
        playerInventories[player] = nil
    end)
end

function InventoryModule.addItem(player: Player, itemId: string, quantity: number)
    local inv = playerInventories[player]
    if not inv then
        inv = {}
        playerInventories[player] = inv
    end
    inv[itemId] = (inv[itemId] or 0) + quantity
end

function InventoryModule.getItem(player: Player, itemId: string): number
    local inv = playerInventories[player]
    if not inv then return 0 end
    return inv[itemId] or 0
end

function InventoryModule.getAll(player: Player): { [string]: number }
    return playerInventories[player] or {}
end

return InventoryModule
```

### The `require()` Pattern

```lua
-- ServerScriptService/Main.server.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

-- Shared modules (both sides can require these)
local ItemData = require(ReplicatedStorage.Modules.ItemData)

-- Server-only modules
local InventoryModule = require(ServerStorage.Modules.InventoryModule)

-- Initialize modules that need setup
InventoryModule.init()
```

**Key facts about `require()`:**
- The module runs **once**. Subsequent `require()` calls return the cached result.
- The module runs in the **context** of the first requirer (server or client).
- If a server Script requires a module in `ReplicatedStorage`, it runs on the server. If a LocalScript requires the same module, a separate client-side copy runs.

### Avoiding Circular Dependencies

Circular dependencies occur when Module A requires Module B, and Module B requires Module A. This causes an infinite loop or returns `nil`.

**Problem:**
```lua
-- ModuleA.lua
local ModuleB = require(script.Parent.ModuleB) -- ModuleB hasn't finished loading
-- ...
return ModuleA

-- ModuleB.lua
local ModuleA = require(script.Parent.ModuleA) -- ModuleA hasn't finished loading
-- ...
return ModuleB
```

**Solution 1: Deferred initialization with `init()` pattern**
```lua
-- ModuleA.lua
local ModuleA = {}
local ModuleB -- forward declaration

function ModuleA.init(modules)
    ModuleB = modules.ModuleB
end

function ModuleA.doSomething()
    ModuleB.helper()
end

return ModuleA
```

```lua
-- Main.server.lua (the bootstrapper)
local ModuleA = require(path.to.ModuleA)
local ModuleB = require(path.to.ModuleB)

-- Wire up cross-references after all modules are loaded
local modules = { ModuleA = ModuleA, ModuleB = ModuleB }
ModuleA.init(modules)
ModuleB.init(modules)

-- Now start the game
ModuleA.start()
```

**Solution 2: Dependency inversion -- extract shared logic into a third module**

Instead of A and B depending on each other, extract the shared concern into module C that both depend on. Dependencies flow in one direction.

**Solution 3: Event-driven decoupling with BindableEvents**

Instead of calling directly into another module, fire a BindableEvent that the other module listens to. Neither module requires the other.

### OOP Module Pattern (Class-based)

```lua
-- ReplicatedStorage/Modules/Weapon.lua
local Weapon = {}
Weapon.__index = Weapon

export type Weapon = typeof(setmetatable({} :: {
    name: string,
    damage: number,
    cooldown: number,
    _lastFired: number,
}, Weapon))

function Weapon.new(name: string, damage: number, cooldown: number): Weapon
    local self = setmetatable({}, Weapon)
    self.name = name
    self.damage = damage
    self.cooldown = cooldown
    self._lastFired = 0
    return self
end

function Weapon.canFire(self: Weapon): boolean
    return (os.clock() - self._lastFired) >= self.cooldown
end

function Weapon.fire(self: Weapon): number?
    if not self:canFire() then
        return nil
    end
    self._lastFired = os.clock()
    return self.damage
end

return Weapon
```

```lua
-- Usage
local Weapon = require(ReplicatedStorage.Modules.Weapon)
local sword = Weapon.new("Iron Sword", 25, 0.8)

if sword:canFire() then
    local dmg = sword:fire()
end
```

---

## 7. Framework Patterns

### Knit Framework

Knit provides a structured way to define **Services** (server) and **Controllers** (client) with automatic networking.

**Server Service:**
```lua
-- ServerScriptService/Services/CoinService.lua
local Knit = require(game:GetService("ReplicatedStorage").Packages.Knit)

local CoinService = Knit.CreateService({
    Name = "CoinService",

    -- Declare client-exposed API
    Client = {
        CoinCollected = Knit.CreateSignal(), -- auto-creates RemoteEvent
    },
})

function CoinService.Client:GetCoins(player)
    -- Client calls this via controller; auto-creates RemoteFunction
    return self.Server:_getCoins(player)
end

function CoinService:_getCoins(player)
    return playerCoins[player] or 0
end

function CoinService:KnitStart()
    -- Runs after all services are initialized
end

function CoinService:KnitInit()
    -- Runs first, set up state here
end

return CoinService
```

**Client Controller:**
```lua
-- StarterPlayerScripts/Controllers/CoinController.lua
local Knit = require(game:GetService("ReplicatedStorage").Packages.Knit)

local CoinController = Knit.CreateController({
    Name = "CoinController",
})

function CoinController:KnitStart()
    local CoinService = Knit.GetService("CoinService")

    -- Call server method (yields, returns value)
    local coins = CoinService:GetCoins()
    print("I have", coins, "coins")

    -- Listen for server signal
    CoinService.CoinCollected:Connect(function(amount)
        print("Collected", amount, "coins!")
    end)
end

return CoinController
```

**Bootstrapper:**
```lua
-- ServerScriptService/KnitServer.server.lua
local Knit = require(game:GetService("ReplicatedStorage").Packages.Knit)

-- Load all services
for _, module in script.Parent.Services:GetChildren() do
    if module:IsA("ModuleScript") then
        require(module)
    end
end

Knit.Start():andThen(function()
    print("Knit server started")
end):catch(warn)
```

### Single Script Architecture (SSA)

One Script on the server, one LocalScript on the client. Each requires a "loader" module that initializes all other modules in order.

```lua
-- ServerScriptService/Main.server.lua
require(game:GetService("ServerStorage").Loader)
```

```lua
-- ServerStorage/Loader.lua
local Loader = {}

local modules = {
    require(script.Parent.Modules.DataService),
    require(script.Parent.Modules.CombatService),
    require(script.Parent.Modules.ShopService),
}

-- Init phase (no cross-dependencies yet)
for _, mod in modules do
    if mod.init then mod:init() end
end

-- Start phase (all modules available)
for _, mod in modules do
    if mod.start then mod:start() end
end

return Loader
```

### Comparison

| Aspect | No Framework (Manual) | Single Script Architecture | Knit |
|---|---|---|---|
| **Complexity** | Low | Medium | Medium-High |
| **Boilerplate** | Minimal | Low | Moderate |
| **Networking** | Manual RemoteEvent setup | Manual | Automatic (Services expose Client API) |
| **Learning curve** | Just Roblox APIs | Small pattern to learn | Framework-specific concepts |
| **Scalability** | Degrades without discipline | Good with init/start pattern | Good, enforced structure |
| **Dependency management** | Manual require chains | Centralized loader | Built-in service discovery |
| **Community adoption** | Universal | Common | Popular but third-party |
| **Best for** | Jams, small projects, learning | Medium projects, teams wanting control | Larger projects, teams wanting convention |

---

## 8. Folder Organization

### Small Game (Simple / Flat)

For game jams, prototypes, or games with under ~10 scripts.

```
game
+-- ServerScriptService
|   +-- GameManager.server.lua
|   +-- DataHandler.server.lua
+-- ServerStorage
|   +-- Maps/
+-- ReplicatedStorage
|   +-- Remotes/
|   |   +-- DamageEvent (RemoteEvent)
|   |   +-- ShopPurchase (RemoteFunction)
|   +-- SharedConfig.lua (ModuleScript)
+-- ReplicatedFirst
|   +-- LoadingScreen.client.lua
+-- StarterGui
|   +-- HUD (ScreenGui)
+-- StarterPlayer
|   +-- StarterPlayerScripts
|       +-- CameraController.client.lua
+-- Workspace
    +-- Map/
    +-- SpawnLocations/
```

### Medium Game (Modular)

Organized into feature folders. Each feature has its own server module, client module, and shared definitions.

```
game
+-- ServerScriptService
|   +-- Main.server.lua               -- Bootstrapper: requires and inits all modules
|   +-- Services/
|   |   +-- CombatService.lua
|   |   +-- DataService.lua
|   |   +-- ShopService.lua
|   |   +-- RoundService.lua
|   +-- Components/
|       +-- LootDrop.lua
|       +-- DoorSystem.lua
+-- ServerStorage
|   +-- Assets/
|   |   +-- Maps/
|   |   +-- NPCs/
|   +-- Modules/
|       +-- DataSchema.lua
+-- ReplicatedStorage
|   +-- Remotes/                       -- All RemoteEvents/Functions here
|   +-- Modules/
|   |   +-- ItemData.lua
|   |   +-- Constants.lua
|   |   +-- Types.lua
|   |   +-- MathUtils.lua
|   +-- Assets/
|       +-- Effects/
|       +-- Animations/
+-- ReplicatedFirst
|   +-- LoadingScreen.client.lua
+-- StarterGui
|   +-- HUD (ScreenGui)
|   +-- ShopMenu (ScreenGui)
|   +-- SettingsMenu (ScreenGui)
+-- StarterPlayer
|   +-- StarterPlayerScripts
|       +-- ClientMain.client.lua      -- Client bootstrapper
|       +-- Controllers/
|           +-- CameraController.lua
|           +-- InputController.lua
|           +-- UIController.lua
+-- Workspace
    +-- World/
    +-- Lighting/
```

### Large Game (Framework-Based with Rojo)

Uses a framework (e.g., Knit), Rojo for file sync, and a strict folder convention. File system mirrors the Roblox hierarchy.

```
src/
+-- server/                            --> syncs to ServerScriptService
|   +-- KnitServer.server.lua          -- Knit bootstrapper
|   +-- services/
|   |   +-- PlayerDataService.lua
|   |   +-- CombatService.lua
|   |   +-- EconomyService.lua
|   |   +-- MatchService.lua
|   |   +-- LeaderboardService.lua
|   +-- components/
|       +-- Destructible.lua
|       +-- Interactable.lua
+-- client/                            --> syncs to StarterPlayerScripts
|   +-- KnitClient.client.lua          -- Knit bootstrapper
|   +-- controllers/
|   |   +-- InputController.lua
|   |   +-- CameraController.lua
|   |   +-- UIController.lua
|   |   +-- SoundController.lua
|   +-- ui/
|       +-- components/
|       |   +-- Button.lua
|       |   +-- HealthBar.lua
|       +-- screens/
|           +-- ShopScreen.lua
|           +-- InventoryScreen.lua
+-- shared/                            --> syncs to ReplicatedStorage
|   +-- modules/
|   |   +-- ItemData.lua
|   |   +-- Constants.lua
|   |   +-- Types.lua
|   |   +-- Util.lua
|   +-- network/
|   |   +-- Remotes.lua                -- Central remote definitions
|   +-- assets/
+-- serverStorage/                     --> syncs to ServerStorage
|   +-- assets/
|   |   +-- maps/
|   |   +-- npcs/
|   +-- modules/
|       +-- DataSchema.lua
+-- starterGui/                        --> syncs to StarterGui
|   +-- HUD.gui.lua
+-- first/                             --> syncs to ReplicatedFirst
    +-- Loading.client.lua
```

---

## 9. Best Practices

### Separation of Concerns

Each script or module should have a single, clear responsibility. A `CombatService` handles damage and health. A `DataService` handles saving and loading. They communicate via well-defined interfaces, not by reaching into each other's internals.

### Single Responsibility

One module = one job. If a module handles inventory AND crafting AND trading, split it into `InventoryModule`, `CraftingModule`, and `TradingModule`.

### Minimal Coupling

Modules should depend on abstractions (function calls, events), not on internal state of other modules. If module A needs data from module B, A calls `B.getData()` rather than reading `B._internalTable` directly.

### Server Owns State

The server is the **single source of truth** for all game state. Clients render and predict, but the server validates and authorizes.

```lua
-- BAD: Client decides damage and tells server
-- Client: FireServer("DealDamage", target, 9999)  -- exploiter sets 9999

-- GOOD: Client tells server "I attacked target", server calculates damage
-- Client: FireServer("AttackRequest", targetId)
-- Server: validates range, cooldown, calculates damage from weapon stats
```

### Validate All Client Input

Every `OnServerEvent` and `OnServerInvoke` handler must validate:
- **Type checking:** Is the argument the expected type? (`typeof(value) == "string"`)
- **Range checking:** Is the number within expected bounds?
- **Ownership checking:** Does this player have permission to perform this action?
- **Rate limiting:** Is this player sending requests too fast?

```lua
RemoteEvent.OnServerEvent:Connect(function(player, targetId, ...)
    -- Type check
    if typeof(targetId) ~= "string" then return end

    -- Existence check
    local target = findEntityById(targetId)
    if not target then return end

    -- Range check
    local character = player.Character
    if not character then return end
    local distance = (character.PrimaryPart.Position - target.Position).Magnitude
    if distance > MAX_INTERACTION_RANGE then return end

    -- Process the valid request
    processAction(player, target)
end)
```

### Use ModuleScripts Everywhere

Avoid putting game logic directly in Scripts or LocalScripts. Instead, keep Scripts/LocalScripts as thin bootstrappers that require and initialize ModuleScripts. This makes code reusable, testable, and organized.

### Centralize Remote Definitions

Create all RemoteEvents and RemoteFunctions in one place rather than scattering `Instance.new("RemoteEvent")` across multiple scripts.

```lua
-- ServerScriptService/CreateRemotes.server.lua (runs first)
local remoteFolder = Instance.new("Folder")
remoteFolder.Name = "Remotes"
remoteFolder.Parent = game:GetService("ReplicatedStorage")

local remotes = {
    "DamageEvent",
    "ShopPurchase",
    "ChatMessage",
    "PlayerReady",
}

for _, name in remotes do
    local remote = Instance.new("RemoteEvent")
    remote.Name = name
    remote.Parent = remoteFolder
end
```

### Use Types and Constants

Define shared constants and Luau types in `ReplicatedStorage` so both sides use the same definitions.

```lua
-- ReplicatedStorage/Modules/Constants.lua
local Constants = {
    MAX_HEALTH = 100,
    WALK_SPEED = 16,
    SPRINT_SPEED = 24,
    MAX_INVENTORY_SLOTS = 20,
    INTERACTION_RANGE = 10,

    ItemRarity = {
        Common = 1,
        Uncommon = 2,
        Rare = 3,
        Epic = 4,
        Legendary = 5,
    },
}

return Constants
```

---

## 10. Anti-Patterns

### God Scripts

**Problem:** One massive script (500+ lines) that handles spawning, combat, data, UI, and everything else. Impossible to debug, modify, or collaborate on.

**Fix:** Break into ModuleScripts with clear responsibilities. The main script becomes a thin bootstrapper.

### Circular Requires

**Problem:** Module A requires Module B, which requires Module A. Causes one of them to receive an incomplete (empty table) reference.

**Fix:** Use the `init()` pattern (Section 6), dependency inversion, or event-driven decoupling.

### Server Logic in ReplicatedStorage

**Problem:** Placing server-only game logic modules in `ReplicatedStorage`. Exploiters can read the source code, understand validation logic, and craft exploits.

**Fix:** Keep server logic in `ServerScriptService` or `ServerStorage`. Only put genuinely shared code (types, constants, utilities) in `ReplicatedStorage`.

### Scripts in Workspace

**Problem:** Placing Scripts directly as children of Workspace or models in Workspace. These are visible to clients (exploiters can read them), are hard to find during development, and create organizational debt.

**Fix:** Put all server scripts in `ServerScriptService`. If you need a script to reference a specific model, have the script in `ServerScriptService` and use a path reference or CollectionService tag to find the model.

### Not Using ModuleScripts

**Problem:** Duplicating logic across multiple Scripts/LocalScripts instead of extracting shared code into ModuleScripts.

**Fix:** If two scripts share logic, extract it into a ModuleScript in the appropriate location (`ReplicatedStorage` for shared, `ServerStorage` for server-only).

### Trusting Client Data

**Problem:** Server blindly applies whatever the client sends (damage values, item quantities, positions).

**Fix:** The server must independently validate and calculate. The client sends **intent** ("I want to attack this target"), not **outcome** ("I dealt 500 damage").

### Polling Instead of Events

**Problem:** Using `while true do wait(1)` loops to check if something changed, instead of connecting to events.

**Fix:** Use `.Changed`, `.GetPropertyChangedSignal()`, `RemoteEvent`, or `BindableEvent` to react to changes.

```lua
-- BAD: polling
while true do
    task.wait(1)
    if player.Character and player.Character.Humanoid.Health <= 0 then
        handleDeath()
    end
end

-- GOOD: event-driven
humanoid.Died:Connect(function()
    handleDeath()
end)
```

### Overusing RemoteFunctions

**Problem:** Using `RemoteFunction` for everything, including fire-and-forget actions that do not need a return value. Each `InvokeServer` call yields the client thread until the server responds.

**Fix:** Use `RemoteEvent` for actions that do not need a response. Reserve `RemoteFunction` for when the client genuinely needs data back from the server.

### Ignoring `task` Library

**Problem:** Using deprecated `wait()`, `spawn()`, and `delay()` which have throttling issues and unclear behavior.

**Fix:** Use the `task` library: `task.wait()`, `task.spawn()`, `task.delay()`, `task.defer()`.

```lua
-- BAD
wait(1)
spawn(function() doWork() end)

-- GOOD
task.wait(1)
task.spawn(function() doWork() end)
```
