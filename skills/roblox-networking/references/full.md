# roblox networking: full reference

Networking is an API boundary, not a trust boundary. Anything running in a player's client can be inspected, modified, or called outside the intended UI flow.

## When to Load

Use this when creating or reviewing remotes, synchronizing gameplay state, or hardening a server handler. Choose the authority model before designing continuous movement or physics.

## 0. Server Authority model

Server Authority is an opt-in Roblox model configured through `Workspace.AuthorityMode = Server` and its required replication, fixed-simulation, streaming, and input settings. The server owns the authoritative core simulation while clients predict input and recover from misprediction through rollback and resimulation.

For simulation-affecting input, use the Input Action System (`InputAction` and `InputContext`) and mirror synchronized logic through `RunService:BindToSimulation()`. Use `RemoteEvent` for discrete requests or notifications, not as a replacement for the continuous input path. The model does not remove server-side validation for custom attacks, purchases, teleports, permissions, or other game-specific actions.

## 1. Define the request contract

Write the contract before writing the handler:

- who may call it;
- argument types and maximum sizes;
- what game state must be true;
- how often a player may call it;
- what the server sends back on success or failure.

Put remotes in a predictable replicated folder. Keep configuration tables shared only when their contents are safe for clients to read.

```luau
-- ReplicatedStorage/Shared/Net.luau
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local remotes = ReplicatedStorage:WaitForChild("Remotes")

return {
    ClaimQuest = remotes:WaitForChild("ClaimQuest"),
    BuyItem = remotes:WaitForChild("BuyItem"),
}
```

## 2. Validate at the server boundary

`typeof` checks are only the first layer. Validate the value against server state and trusted definitions.

```luau
local function validItemRequest(player: Player, itemId: unknown, amount: unknown): (boolean, string?)
    if typeof(itemId) ~= "string" or #itemId > 40 then
        return false, "bad item id"
    end
    if typeof(amount) ~= "number"
        or amount ~= amount
        or math.abs(amount) == math.huge
        or amount % 1 ~= 0
        or amount < 1
        or amount > 20 then
        return false, "bad amount"
    end

    local item = ItemDefinitions[itemId]
    if not item or not item.Tradeable then
        return false, "item unavailable"
    end

    if InventoryService:GetCount(player, itemId) < amount then
        return false, "not owned"
    end
    return true
end

TradeRemote.OnServerEvent:Connect(function(player, itemId, amount)
    local ok = validItemRequest(player, itemId, amount)
    if not ok then
        return
    end
    InventoryService:Remove(player, itemId, amount)
end)
```

Do not send a detailed failure reason to an untrusted caller if it reveals private state. Log enough context for operators without logging secrets or raw payloads indefinitely.

## 3. Keep outcomes server-owned

The client may request “attack target X” or “buy item Y.” It must not request “deal 100 damage” or “subtract 20 coins.” The server calculates the result from current state.

For combat, check at least:

- the attacker is alive and allowed to act;
- the target exists and is in the relevant world or match;
- the weapon is equipped and its cooldown has elapsed;
- the reported position is plausible for the player's character;
- the target is within server-calculated range or line of sight when required.

A client-side hit effect is presentation. The server's damage decision is the game result.

## 4. Per-player throttling

Use a monotonic clock and clean entries when players leave. A limiter should reject bursts without turning normal network jitter into a ban.

```luau
local Players = game:GetService("Players")
local lastCall: {[Player]: {[string]: number}} = {}
local intervalByAction = {
    BuyItem = 0.25,
    ClaimQuest = 0.5,
}

local function allowed(player: Player, action: string): boolean
    local now = os.clock()
    local playerCalls = lastCall[player]
    if not playerCalls then
        playerCalls = {}
        lastCall[player] = playerCalls
    end

    local previous = playerCalls[action]
    local interval = intervalByAction[action] or 0.2
    if previous and now - previous < interval then
        return false
    end
    playerCalls[action] = now
    return true
end

Players.PlayerRemoving:Connect(function(player)
    lastCall[player] = nil
end)
```

For expensive work, add a token or queue budget as well as a simple cooldown. The limit should be attached to the action, not copied blindly to every remote.

## 5. RemoteFunction cautions

A `RemoteFunction` makes one side wait for a response. Use it for a small query with a clear timeout strategy, not for a long-running transaction or a callback that can block server work.

Prefer this shape for mutations:

1. client fires a request event;
2. server validates and applies it;
3. server sends an acknowledgement or replicates the changed state.

If a request must be idempotent, include a server-checked request identifier and retain only the small amount of history needed to reject duplicates.

## 6. Choose the remote semantics

Use the least powerful transport that preserves the gameplay contract:

- `RemoteEvent` for reliable messages such as inventory mutations, accepted hits, and state transitions. Its delivery is not a general ordering guarantee relative to property or attribute replication.
- `UnreliableRemoteEvent` for replaceable snapshots, aim previews, particles, sound cues, and other data that is stale as soon as a newer update exists.
- `RemoteFunction` only for short request-response queries with bounded work and an explicit failure path.

Unreliable events are not a free bandwidth or latency upgrade. Roblox may drop them, does not guarantee ordering against other traffic, and documents a 900-byte payload ceiling. Under Server Authority, RemoteEvents may also be observed out of order relative to property and attribute updates. If ordering matters, use one explicit state channel or carry a version/request identifier. Never use unreliable events for currency, inventory, purchases, damage, or any result that must arrive exactly once.

```luau
-- ReplicatedStorage/Remotes/Effects is an UnreliableRemoteEvent.
local Effects = game:GetService("ReplicatedStorage").Remotes.Effects

-- The event carries presentation data only. The server still decides whether
-- the underlying gameplay action happened.
Effects:FireAllClients("MuzzleFlash", muzzlePosition, direction)
```

For typed wrappers, `RbxUtil` exposes `TypedRemote` and `Comm`. They can improve discoverability and middleware structure, but they do not validate attacker-controlled values for you. Keep the server contract and validation visible at the handler boundary.

## 7. Measure packet budgets

Track both payload size and frequency. A small payload fired every frame can be worse than a larger payload sent occasionally. The community `RemotePacketSizeCounter` resource is useful for estimating supported datatype sizes and testing the 900-byte unreliable-event ceiling, but its own documentation notes that some Roblox encoding behavior is undocumented and has edge cases.

Record at least:

- remote name and direction;
- calls per second;
- estimated bytes per call and bytes per second;
- reliable versus unreliable transport;
- player count and representative latency.

Do this in a test place with realistic load. A local ping measurement is not a network-budget benchmark.

## 8. Movement and physics checks

Do not compare a client's position to a fixed speed threshold without accounting for legitimate teleports, seats, network ownership, respawns, and server corrections. In a Server Authority project, do not add a blanket `Heartbeat` CFrame correction loop; keep synchronized movement logic in `BindToSimulation()` and validate only custom movement or action transitions. In classic projects, use server-side state transitions and tolerance windows. A suspicious score is usually safer than an immediate kick:

- collect several independent violations;
- clear or decay the score after normal behavior;
- notify operators or apply a limited response at a threshold;
- never let the score itself grant or remove valuable items.

## 9. Client/server test matrix

Test handlers without the expected UI path:

- wrong types and oversized strings;
- missing or foreign instance references;
- requests before the player is loaded;
- duplicate and out-of-order requests;
- rapid bursts;
- player removal during a request;
- legitimate high-latency and respawn cases.

The goal is not to make the client impossible to modify. The goal is to make modification unable to create an unearned authoritative outcome.

## Networking checklist

- [ ] Every remote has a documented contract.
- [ ] Server handlers validate type, range, ownership, state, and rate.
- [ ] Trusted values come from server definitions or server state.
- [ ] Long work cannot be forced through an unbounded `RemoteFunction`.
- [ ] Reliable and unreliable transports are chosen by data semantics, not by a blanket performance claim.
- [ ] Packet size and fire rate are measured for high-frequency remotes.
- [ ] Player cleanup removes limiter, subscription, and connection state.
- [ ] Suspicion handling tolerates false positives and does not expose private data.
