# roblox architecture: full reference

This is an original implementation guide built around Roblox's data model and client/server runtime. It is deliberately framework-neutral.

## When to Load

Use this reference when a project is growing beyond a few scripts, when a feature crosses the client/server boundary, or when startup order and ownership are unclear.

## 1. Start with ownership

Choose a home based on who must be allowed to run or read the code.

| Location | Typical contents | Boundary |
| --- | --- | --- |
| `ServerScriptService` | game rules, services, receipt handling | server only |
| `ServerStorage` | server-only templates and private assets | server only |
| `ReplicatedStorage` | shared modules, remotes, public definitions | replicated to clients |
| `StarterPlayerScripts` | per-player controllers and input | client |
| `StarterGui` | UI templates | cloned to each player's `PlayerGui` |
| `Workspace` | live replicated instances | visible to clients unless protected elsewhere |

A location is not a security feature if the object is replicated. Never put a secret, service credential, or authoritative reward table in a replicated container.

## 2. A small feature layout

A feature should be easy to find and have one obvious server owner.

```text
ReplicatedStorage
└── Shared
    ├── Types
    ├── Net
    └── Util
ServerScriptService
├── Boot.server.luau
└── Services
    ├── InventoryService.luau
    └── RoundService.luau
StarterPlayer
└── StarterPlayerScripts
    ├── Boot.client.luau
    └── Controllers
        ├── InventoryController.luau
        └── RoundController.luau
```

The exact folders are less important than the rule: shared code stays side-effect-light, server services own state, and client controllers translate input into requests or presentation.

## 3. Explicit startup

Do not rely on filesystem order or accidental `require` order. A bootstrapper can pass a shared context and make dependencies visible.

```luau
-- ServerScriptService/Boot.server.luau
local servicesFolder = script.Parent.Services
local serviceNames = { "InventoryService", "RoundService" }
local services = {}

for _, name in serviceNames do
    services[name] = require(servicesFolder[name])
end

local context = { Services = services }

for _, name in serviceNames do
    local service = services[name]
    if service.Init then
        service:Init(context)
    end
end

for _, name in serviceNames do
    local service = services[name]
    if service.Start then
        task.spawn(function()
            service:Start(context)
        end)
    end
end
```

Use `Init` for wiring references and validation. Use `Start` for work that may connect events, yield, or begin loops. If startup order matters, represent it in the list or split the phases rather than hiding it in a module's top-level code.

## 4. ModuleScript contracts

A module should answer three questions:

1. What state does it own?
2. Which functions are public?
3. Which side is allowed to call it?

Prefer a narrow returned table over exporting every helper.

```luau
-- ServerScriptService/Services/InventoryService.luau
local InventoryService = {}
local inventories: {[Player]: {[string]: number}} = {}

function InventoryService:Init()
    -- connect dependencies here
end

function InventoryService:GetCount(player: Player, itemId: string): number
    local inventory = inventories[player]
    return inventory and inventory[itemId] or 0
end

function InventoryService:Remove(player: Player, itemId: string, amount: number): boolean
    local inventory = inventories[player]
    local current = inventory and inventory[itemId]
    if not current or amount < 1 or current < amount then
        return false
    end
    inventory[itemId] = current - amount
    return true
end

return InventoryService
```

Keep module top-level code cheap. A `require` can yield when another module does work at load time, and two modules that require each other can deadlock or observe half-initialized state.

## 5. Client/server boundaries

A request is not a command to obey. A client can fire any replicated `RemoteEvent`, send malformed arguments, and alter its own local state. The server should validate the request, look up trusted configuration, apply the result, and replicate the outcome.

```luau
-- ServerScriptService/Services/InventoryService.luau
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local buyItem = ReplicatedStorage.Shared.Net.BuyItem

buyItem.OnServerEvent:Connect(function(player, itemId)
    if typeof(itemId) ~= "string" then
        return
    end

    local definition = ItemDefinitions[itemId]
    if not definition or definition.Price < 0 then
        return
    end

    -- Read currency and grant the item from server-owned state.
    InventoryService:Purchase(player, definition)
end)
```

The client may predict an animation or optimistically update a button, but it must reconcile with the server response. Do not accept client-supplied damage, price, ownership, reward, or teleport destination as authoritative data.

## 6. Remotes and shared definitions

Keep remotes in a stable shared location and treat their names and argument shapes as an API. For each remote, document:

- direction: client to server, server to client, or both;
- argument types and size limits;
- authorization and ownership checks;
- cooldown or quota;
- response or failure behavior.

`RemoteFunction` is appropriate for a short request that genuinely needs a response. Avoid making a server call wait on an untrusted client callback. For most gameplay requests, an event plus an explicit result event is easier to time out and observe.

## 7. Cross-module communication

Use direct calls for a stable dependency. Use a signal or bindable event when the publisher should not know its consumers. Do not introduce a global event bus merely to avoid drawing a dependency graph.

Good boundaries:

- `RoundService` owns round state and exposes `GetPhase` and `StartRound`.
- `InventoryService` owns inventory mutation and emits `ItemChanged`.
- `InventoryController` listens and renders UI; it never edits the authoritative inventory table.

## 8. Testing and growth

A project is ready to split a module when one of these becomes true:

- it owns a separate lifecycle or persistence boundary;
- it has a distinct server/client contract;
- tests need to exercise it without booting unrelated systems;
- the current module has multiple unrelated reasons to change.

Keep pure validation and calculation functions separate from Roblox instance wiring. They can run under a headless Luau test tool, while integration tests run in Studio.

## Architecture checklist

- [ ] Every persistent or authoritative state owner is server-side.
- [ ] Replicated folders contain no secrets or trust decisions.
- [ ] Startup order is explicit and observable.
- [ ] Module contracts are narrow and do not form circular requires.
- [ ] Every remote has type, authorization, size, and rate checks.
- [ ] Client prediction cannot grant value or bypass a server decision.
- [ ] Shutdown and player-removal paths release connections and save state.
