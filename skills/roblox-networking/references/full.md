# roblox networking: full reference

> Code examples are illustrative. Adapt them to your project and verify in Studio before production use.

Networking is an API boundary, not a trust boundary. Anything running in a player's client can be inspected, modified, or called outside the intended UI flow.

## When to Load

Use this when creating or reviewing remotes, synchronizing gameplay state, or hardening a server handler. Choose the authority model before designing continuous movement or physics.

## 0. Server Authority model

Server Authority is an opt-in Roblox model configured through `Workspace.AuthorityMode = Server` and its required replication, fixed-simulation, streaming, and input settings. The server owns the authoritative core simulation while clients predict input and recover from misprediction through rollback and resimulation.

For simulation-affecting input, use the Input Action System (`InputAction` and `InputContext`) and mirror synchronized logic through `RunService:BindToSimulation()` (requires `Workspace.UseFixedSimulation` enabled in Studio). Use `RemoteEvent` for discrete requests or notifications, not as a replacement for the continuous input path. The model does not remove server-side validation for custom attacks, purchases, teleports, permissions, or other game-specific actions.

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

### Numeric and string poison checks

Two cheap checks belong next to every `typeof` guard because both defeat naive validation and both kill DataStore saves downstream:

- **NaN / infinity:** `NaN ~= NaN`, so equality guards pass it through, and comparisons like `amount < limit` return false for `NaN`, skipping range checks silently. Reject with `x ~= x or math.abs(x) == math.huge`.
- **Malformed UTF-8:** client-supplied strings may contain invalid byte sequences that DataStores refuse to serialize. `utf8.len(s)` returns `nil` plus an error position for malformed input; reject when it does not return a count.

Rejecting these at the remote boundary protects both the gameplay logic and the persistence layer (`roblox-data` covers the save-side contract).

## 3. Keep outcomes server-owned

The client may request "attack target X" or "buy item Y." It must not request "deal 100 damage" or "subtract 20 coins." The server calculates the result from current state.

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

Unreliable events are not a free bandwidth or latency upgrade. Roblox may drop them, does not guarantee ordering against other traffic, and documents a 1000-byte payload ceiling. Under Server Authority, RemoteEvents may also be observed out of order relative to property and attribute updates. If ordering matters, use one explicit state channel or carry a version/request identifier. Never use unreliable events for currency, inventory, purchases, damage, or any result that must arrive exactly once.

```luau
-- ReplicatedStorage/Remotes/Effects is an UnreliableRemoteEvent.
local Effects = game:GetService("ReplicatedStorage").Remotes.Effects

-- The event carries presentation data only. The server still decides whether
-- the underlying gameplay action happened.
Effects:FireAllClients("MuzzleFlash", muzzlePosition, direction)
```

For typed wrappers, `RbxUtil` exposes `TypedRemote` and `Comm`. They can improve discoverability and middleware structure, but they do not validate attacker-controlled values for you. Keep the server contract and validation visible at the handler boundary.

## 7. Measure packet budgets

Track both payload size and frequency. A small payload fired every frame can be worse than a larger payload sent occasionally. The community `RemotePacketSizeCounter` resource is useful for estimating supported datatype sizes and testing the 1000-byte unreliable-event ceiling, but its own documentation notes that some Roblox encoding behavior is undocumented and has edge cases.

Record at least:

- remote name and direction;
- calls per second;
- estimated bytes per call and bytes per second;
- reliable versus unreliable transport;
- player count and representative latency.

Do this in a test place with realistic load. A local ping measurement is not a network-budget benchmark.

## 7a. Replicate state to subscribed clients

For a state object that many clients must observe, avoid re-sending whole tables per change. Keep the state server-owned and let clients subscribe by a token or name; each client receives an initial snapshot plus delta updates for only the fields that changed. Community replication modules (e.g. Replica, successor to ReplicaService, https://devforum.roblox.com/t/replica-server-to-client-state-replication-module/3216980) implement this pattern; you can also build it with a single state RemoteEvent carrying a versioned delta. Keep creation and mutation server-side so the client subscription is a read-only mirror.

## 7b. Shrink payloads with binary serialization

When a high-frequency remote exceeds budget, replace high-precision tables with compact typed fields. Pick the smallest precision that reads correctly per field (a quantized `CFrame` or low-bit float for positions, a small integer for counters) rather than always sending 64-bit values. Community serialization modules (e.g. Bitstream, https://devforum.roblox.com/t/bitstream-%E2%80%93-binary-framework/4788654) provide typed, precision-varied formats; keep a schema/version so both sides agree on field order and size. Prefer this for replaceable, high-frequency data (positions, aim), not for state that must be exactly once and easily debugged.

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

## 10. Text chat: TextChatService (modern) and legacy Chat

[TextChatService](https://create.roblox.com/docs/reference/engine/classes/TextChatService) is the current chat system. The legacy chat system was retired April 30, 2025: Roblox auto-migrates experiences still on `ChatVersion.LegacyChatService`, and custom integrations that bypass TextChatService break or get moderated ([migration announcement](https://devforum.roblox.com/t/migrate-to-textchatservice-removing-support-for-legacy-chat-and-custom-chat-systems/3237100), [status update](https://devforum.roblox.com/t/update-on-legacy-chat-deprecation-and-textchatservice-migration/3376880)). <!-- temporal: 2025-05 --> `TextChatService.ChatVersion` is not scriptable; set it in Studio. Never build new chat features on the legacy `Chat` service.

### Instance tree

Default runtime tree when `TextChatService.CreateDefaultTextChannels` and `CreateDefaultCommands` are true (both are Studio properties, not scriptable):

- `TextChatService.TextChannels` (Folder): `RBXGeneral` (player messages), `RBXSystem` (system messages; red when `TextChatMessage.Metadata` contains "Error"), `RBXTeam[BrickColor]` per team, `RBXWhisper:[UserId1]_[UserId2]` per whisper pair.
- `TextChatService.TextChatCommands` (Folder): `RBXClearCommand`, `RBXEmoteCommand`, `RBXHelpCommand`, `RBXMuteCommand`, `RBXTeamCommand`, `RBXWhisperCommand`, and others (`/e`, `/t`, `/w`, `/mute`, ...).
- Configuration singletons directly under `TextChatService`: `ChatWindowConfiguration`, `ChatInputBarConfiguration`, `BubbleChatConfiguration`, `ChannelTabsConfiguration`.

You can add your own `TextChannel` and `TextChatCommand` instances even with defaults on. A `TextChatCommand` must be parented to `TextChatService` to function.

### Client/server split ([TextChannel](https://create.roblox.com/docs/reference/engine/classes/TextChannel))

- `TextChannel:SendAsync(message, metadata)` — client only. Sends a player message to the server; the engine filters it server-side, and clients receive "the result of the filtered message from the server". Metadata over 200 characters means the message is not delivered.
- `TextChannel:DisplaySystemMessage(message, metadata)` — client only. Visible only to that local user and **not** automatically filtered or localized.
- `TextChannel.MessageReceived` / `TextChatService.MessageReceived` — client only.
- `TextChannel:AddUserAsync(userId)` — server only. Adds a `TextSource`; returns `nil, false` when the user has chat off or is not in the server.
- Server-side delivery control: `TextChannel.ShouldDeliverCallback(message, textSource)` (return `false` to withhold from a recipient) plus `TextChatService:CanUserChatAsync` / `CanUsersChatAsync` / `CanUsersDirectChatAsync` for platform permission gates.

`OnIncomingMessage` (on both `TextChatService` and `TextChannel`) is documented client-only: it decorates or replaces messages for display by returning `TextChatMessageProperties`; returning `nil` leaves the message unchanged. `TextChatService.OnIncomingMessage` runs before any `TextChannel.OnIncomingMessage`. Define each callback exactly once — multiple bindings override one another nondeterministically. Messages are not replicated to a custom UI by themselves; the default chat UI consumes `MessageReceived` for you, and a custom UI must render those payloads itself.

### Filtering rules

- Player messages sent via `TextChannel:SendAsync` are filtered by the engine server-side; do not double-filter before `SendAsync`.
- `DisplaySystemMessage` strings are not filtered. Static developer-authored text is fine. If a system message embeds player input (names, item names), filter that input server-side with `TextService:FilterStringAsync` first — the same rule as any other user-generated text.

### Example: custom channel plus `/heal` command

```luau
-- ServerScriptService (server)
local TextChatService = game:GetService("TextChatService")
local Players = game:GetService("Players")

local battleChannel = Instance.new("TextChannel")
battleChannel.Name = "Battle"
battleChannel.Parent = TextChatService.TextChannels

local healCommand = Instance.new("TextChatCommand")
healCommand.Name = "HealCommand"
healCommand.PrimaryAlias = "/heal"
healCommand.Parent = TextChatService.TextChatCommands

healCommand.Triggered:Connect(function(textSource: TextSource, unfilteredText: string)
	local player = Players:GetPlayerByUserId(textSource.UserId)
	if not player then return end
	-- unfilteredText is attacker-controlled: parse/validate before use.
	-- Apply the heal server-side; check cooldown and permission here.
end)

Players.PlayerAdded:Connect(function(player)
	battleChannel:AddUserAsync(player.UserId)
end)
```

```luau
-- StarterPlayerScripts (client)
local TextChatService = game:GetService("TextChatService")

local channels = TextChatService:WaitForChild("TextChannels")
local battleChannel = channels:WaitForChild("Battle")

battleChannel.MessageReceived:Connect(function(message: TextChatMessage)
	print(message.Text) -- default UI renders messages; a custom UI mirrors this
end)

-- Local confirmation that only this user sees:
battleChannel:DisplaySystemMessage("You are healed", "Heal")

TextChatService.OnIncomingMessage = function(message: TextChatMessage)
	if string.find(message.Metadata, "Error") then
		local props = Instance.new("TextChatMessageProperties")
		return props -- decorate error messages here
	end
	return nil
end
```

When a sent message matches a `TextChatCommand` alias, the command sinks it server-side: `Triggered` fires and the message is not replicated to other users.

### Legacy Chat (deprecated — migration reference only)

- `Chat:Chat(partOrCharacter, message, color?)` fires `Chat.Chatted` and drives the legacy bubble-chat LocalScript. Replace with `TextChatService:DisplayBubble()` and `BubbleChatConfiguration`.
- `Chat:FilterStringAsync` / `Chat:FilterStringForBroadcast` filter legacy chat text; the client-side call form is deprecated. Replace with server-side `TextService:FilterStringAsync` ([Chat](https://create.roblox.com/docs/reference/engine/classes/Chat)).
- `Chat:RegisterChatCallback` (`OnServerReceivingMessage`, `OnClientFormattingMessage`) customizes the legacy Luau chat pipeline. There is no 1:1 port; re-model the logic on `TextChannel.ShouldDeliverCallback` and the `OnIncomingMessage` callbacks.

## Networking checklist

- [ ] Every remote has a documented contract.
- [ ] Server handlers validate type, range, ownership, state, and rate.
- [ ] Trusted values come from server definitions or server state.
- [ ] Long work cannot be forced through an unbounded `RemoteFunction`.
- [ ] Reliable and unreliable transports are chosen by data semantics, not by a blanket performance claim.
- [ ] Packet size and fire rate are measured for high-frequency remotes.
- [ ] Player cleanup removes limiter, subscription, and connection state.
- [ ] Suspicion handling tolerates false positives and does not expose private data.

## Community ecosystem (leads, not sources)

Top-sorted DevForum canon for networking libraries. Verify status in-thread; several are archived.

- State replication: [Replica](https://devforum.roblox.com/t/replica-server-to-client-state-replication-module/3216980) (2024, current favorite; pairs with ProfileStore per [PlayerState](https://devforum.roblox.com/t/playerstate-profilestore-replica-without-the-headache/3766568)); [ReplicaService](https://devforum.roblox.com/t/replicate-your-states-with-replicaservice-networking-system/894736) older.
- Remote tooling: [Packet](https://devforum.roblox.com/t/packet-networking-library/3573907) (2025), [Warp](https://devforum.roblox.com/t/warp-very-fast-powerful-networking-library/2779813) (2024), [BridgeNet](https://devforum.roblox.com/t/bridgenet-insanely-optimized-easy-to-use-networking-library-full-of-utilities-now-with-roblox-ts-v199-beta/1909935) (legacy).
- Case study: [60x bandwidth reduction in Astro Force](https://devforum.roblox.com/t/how-we-reduced-bandwidth-usage-by-60x-in-astro-force-roblox-rts/1202300) — the practical RTS-scale optimization write-up.
- [StreamX is DEPRECATED](https://devforum.roblox.com/t/deprecated-streamx-reduce-lag-and-prevent-map-cloning/1992484) — do not recommend; example of a once-canonical library that died.
