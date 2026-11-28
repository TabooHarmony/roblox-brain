# roblox networking: full reference

> Code examples are illustrative. Adapt them to your project and verify in Studio before production use.

Networking is an API boundary, not a trust boundary. Anything running in a player's client can be inspected, modified, or called outside the intended UI flow.

## When to Load

Use this when creating or reviewing remotes, synchronizing gameplay state, or hardening a server handler. Choose the authority model before designing continuous movement or physics.

## 0. Server Authority model

Server Authority is an opt-in Roblox model configured through `Workspace.AuthorityMode = Server` and its required replication, fixed-simulation, streaming, and input settings. The server owns the authoritative core simulation while clients predict input and recover from misprediction through rollback and resimulation.

For simulation-affecting input, use the Input Action System (`InputAction` and `InputContext`) and mirror synchronized logic through `RunService:BindToSimulation()` (requires `Workspace.UseFixedSimulation` enabled in Studio). Use `RemoteEvent` for discrete requests or notifications, not as a replacement for the continuous input path. The model does not remove server-side validation for custom attacks, purchases, teleports, permissions, or other game-specific actions.

### Settings bundle and debug surface

Server Authority is only real when the whole settings bundle travels together. Setting `Workspace.AuthorityMode = Enum.AuthorityMode.Server` automatically sets the other five; verify all six during review because a place file can drift:

1. `Workspace.AuthorityMode` = `Enum.AuthorityMode.Server`
2. `Workspace.NextGenerationReplication` enabled
3. `Workspace.PlayerScriptsUseInputActionSystem` enabled
4. `Workspace.SignalBehavior` = `Enum.SignalBehavior.Deferred`
5. `Workspace.UseFixedSimulation` enabled
6. `Workspace.StreamingEnabled` enabled

Misprediction and rollback are normal operation, not defects: clients cannot predict other players' inputs, so corrections should be small and imperceptible when tuned. On a detected misprediction the client resets to the server's authoritative state and resimulates its predicted frames.

Debug surface for review sessions:

- Studio ships a server authority visualization overlay for review sessions, but its shortcuts, counters, and per-reason input-drop tallies are not documented on the pages reviewed here. Do not quote specific numbers from it as if they were published thresholds; describe what you observed instead.
- Read prediction state from the scriptable surface instead: `RunService:SetPredictionMode()` forces prediction for a given instance and is client-only, and `Instance.PredictionMode` reflects the mode applied to that instance.

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

## 2a. What survives a remote call

Remote arguments are serialized, not shared. Verified against the [remote events and functions](https://create.roblox.com/docs/scripting/events/remote) docs:

| What you send | What arrives | Consequence |
|---------------|--------------|-------------|
| Function | `nil` | Functions are not replicated; the receiving argument is `nil`. |
| Table with a metatable | Plain table, metatable lost | All metatable information is stripped in transfer; `__index`-backed methods are gone on arrival. |
| Mixed table (numeric + string keys) | Mangled data | Pass all key-value (dictionary) or all numeric indices, never both. Non-string indices (Instance, userdata, function) are converted to strings. |
| Table with `nil` in an index | Truncated payload | Avoid `nil` values in any index of a passed table. |
| Table | Copy, not a reference | Table identity differs on arrival and on return; mutating a "shared" table only mutates the local copy. |
| Instance only the sender can see | `nil` | Server-only instances (e.g. under `ServerStorage`) and client-created parts are not replicable across the boundary. |

Practical consequences:

- **Type checking:** a `typeof` guard per argument is only the entry check. Because functions arrive as `nil`, non-string keys get stringified, and any "table" can be any shape, validate the fields and values of every table against the contract, not just its type.
- **State sharing:** tables arrive as copies, so remotes cannot share mutable state. Keep authoritative state on the server and replicate explicit snapshots or deltas, or send stable identifiers (`UserId`, item ids) and re-resolve them from server state.

## 3. Keep outcomes server-owned

The client may request "attack target X" or "buy item Y." It must not request "deal 100 damage" or "subtract 20 coins." The server calculates the result from current state.

For combat, check at least:

- the attacker is alive and allowed to act;
- the target exists and is in the relevant world or match;
- the weapon is equipped and its cooldown has elapsed;
- the reported position is plausible for the player's character;
- the target is within server-calculated range or line of sight when required.

A client-side hit effect is presentation. The server's damage decision is the game result.

## 3a. Latency-aware hit validation: shared clock, bounded rewinds

When the outcome depends on *when* something happened (melee swings, projectiles, dashes), the server's
view of the world is stale by about one round-trip. The mechanics below use one clock and two
validation strategies; all claims are verified against the [Workspace docs](https://create.roblox.com/docs/reference/engine/classes/Workspace#GetServerTimeNow)
unless labeled practitioner.

**The shared clock: `workspace:GetServerTimeNow()`.** Available on client and server, it returns the
client's (or server's) best approximation of server time as a Unix timestamp. Its documented
properties are exactly what a validator needs — and what it does *not* guarantee defines your
tolerances:

- Monotonic: the value never decreases on a connection.
- Smoothed to move at the same rate as the local clock to within 0.6%.
- It is an *approximation*: clients disagree with the server by a small offset that includes their
  network delay, not by a fixed published number. Practitioner threads report a few milliseconds of
  variation on healthy connections ([accuracy thread](https://devforum.roblox.com/t/about-how-accurate-is-getservertimenow/3926695));
  treat that as community data, not a spec. Sizing your window must come from your own latency
  measurements (see the budget method in §7a).
- It throws on a client that isn't connected, and the docs explicitly say it is **not secure** for
  things like timed rewards — track those server-side.

**Never trust a client timestamp as proof.** A client can send any number it likes, including a
`GetServerTimeNow()` value it captured earlier or fabricated. The timestamp is *context*, never
*authorization*: an echoed timestamp proves nothing on its own. Server-side time arithmetic
(`GetServerTimeNow()` on the server, `os.clock()` for intervals) is the only clock that decides
outcomes; `tick()` and client `os.time()` never authorize anything. A fabricated timestamp can still
be *plausible*, so the defense is bounding + cross-checks, not the timestamp itself:

1. **Freshness bound:** reject claims whose stamp is older than your max tolerance
   (`now - stamp > MAX_LATENCY_WINDOW` → reject or flag). Practitioner rollback systems use a
   configurable cap (e.g. 0.5 s) plus an interpolation-buffer addend for character replication delay
   ([RollbackHitbox write-up](https://devforum.roblox.com/t/rollbackhitbox-server-authoritative-lag-compensation-for-roblox-shooters-open-source/4553295)
   — practitioner design, verify before adoption). A client that always claims the oldest allowed
   stamp is the expected adversarial case, which is why the rewind window is a deliberate tradeoff,
   not a security boundary: a bigger window is more forgiving and more abusable; pick it from
   measured RTT distribution plus the interpolation buffer, and accept that the abusable tail exists.
2. **In-flight event matching:** keep a small set of server-initiated or previously-seen events
   (swing id, projectile id) and require the claim to reference one; unknown or reused ids reject.
3. **Plausibility cross-checks:** attacker alive and cooled down; claimed origin within a bounded
   distance of the attacker's *server-observed* position; target range/LOS checked against server
   state.

**Dynamic targets vs static geometry — re-validate the right thing.** For static geometry (walls,
terrain), the server can simply re-raycast from the claimed origin: the geometry cannot have moved,
so a server raycast is the ground truth and beats trusting the client's hit call. For *dynamic*
targets, a server re-raycast against current positions silently punishes every high-latency player:
the target has moved on since the client's frame. Instead validate plausibility with tolerance —
range at claim time, LOS from the rewound viewpoint, and for deterministic paths reconstruct the
projectile position from stamp delta × known speed and check claimed victims against the reconstructed
volume with a few studs of slack. Failure of a tolerance check is suspicion, not proof: score it
(§8) rather than punishing one packet.

```luau
-- Server: melee swing validation (illustrative; tune from your own latency data)
type Swing = { id: string, stamp: number, origin: Vector3, target: Model? }

local MAX_AGE = 0.35 -- freshness window: re-derive from measured RTT + interpolation buffer
local pending = {} -- [player] = { [swingId] = expiry } filled when the swing anim starts

local function validateSwing(player: Player, claim: Swing): boolean
    local now = workspace:GetServerTimeNow() -- server-side read is authoritative
    local entry = pending[player]
    local swing = entry and entry[claim.id]
    if not swing or now > swing.expiry then
        return false -- unknown, reused, or expired swing id: reject without punishment
    end
    entry[claim.id] = nil -- consume: a swing id cannot be replayed
    if typeof(claim.stamp) ~= "number" or claim.stamp ~= claim.stamp
        or now - claim.stamp > MAX_AGE or claim.stamp > now + 0.25 then
        return false -- stale or future-stamped: reject
    end
    local char = player.Character
    if not char then return false end
    local root = char:FindFirstChild("HumanoidRootPart") :: BasePart?
    if not root or (root.Position - claim.origin).Magnitude > 8 then
        return false -- claimed origin implausible vs server-observed position
    end
    return true -- damage itself is computed server-side from server state
end
```

Note what the example does *not* do: it never compares `claim.stamp` to the client's word about
latency, never grants damage because a timestamp "looks right", and never punishes on a single
failure — an expired swing id from a laggy client is indistinguishable from a forged one, so both
just get a `false`.

## 3b. Prediction that stays honest

<!-- temporal: 2026-11 -->

These patterns come from custom prediction layers (not Server Authority). Unless marked otherwise, each was **measured in one project**: verify it in your own game under the Studio network simulator.

**Ack every predicted command.** Suppose the client applies a hit locally and the server silently drops it. That client keeps the change forever, and a later snapshot can wipe hits still in flight.

- Give each command a small sequence number. The server acks every one, accepted or refused, and with a refusal also sends the authoritative state.
- The client keeps unacked commands and replays them over each snapshot.
- Remote sends to one player arrive in order. So an ack for N means older unacked commands were dropped (by a rate limiter, for example) and must be resynced.
- Sequence numbers only move forward; a u16 that wraps needs a wrap-aware compare.

**Rate limits that fit real latency.**

- At 100 ms ping with jitter, a fixed per-hit cooldown rejected about half of normal swings. A small token bucket fixed it: bank 2 hits and refill at the tool's rate. One working set used 1.15x the weapon rate with a burst of 3.
- A timer that runs on both sides drifts by the message delay. The server's reload starts when the message arrives, so the client's ends a frame or two sooner.
  - Accept messages within a small window of the timer's end (0.1 s held up to 80 ms jitter).
  - Always reply to refusals.
  - Test from the timer's last frame, not just from a fresh weapon.
- For melee, a server cooldown longer than the client's full swing silently eats every other swing (count wind-up through recovery, including the miss path). Give slow weapons a long swing, not a long cooldown.
- Some networking libraries drop rate-limited requests before the handler and send no reply. The client's call then returns its timeout value only after the full response timeout.
  - Debounce buttons so normal use never hits the limit.
  - Raise the timeout for requests that wait on a save.

**Predict cosmetics, not consequences.** An effect that plays only on the server's message waits a full round trip: 190–290 ms, even point blank on a phone. Switching between reliable and unreliable sends made no difference.

- Predict the shooter's own effect locally, keyed by the attack sequence the server echoes back.
- Skip the server's copy for the same shooter and sequence, cancel on a refused ack, and expire unconfirmed guesses.
- Keep anything that changes the world (destruction, currency, score) on the server's message.
- Treat a hit, absorbed damage, and a confirmed death as distinct outcomes. A shield or a remaining life must never trigger death UI, death camera, or broadcasts.

**Make thrown and spawned objects feel immediate.**

- **Hitscan shown as a projectile.** The server waits the flight time before applying the blast, every client draws the same flight, and the instant impact puff is skipped.
- **Server-spawned debris.** Run the same deterministic split on the client and show a local stand-in under a temporary id.
  - Fly the stand-in with the server's launch velocity and gravity, then adopt the real id by a deterministic key (seed and size).
  - Never ease straight onto the replicated body: it lags by a round trip plus interpolation. A 0.3 s blend threw pieces back upward at 240 ms ping.
  - Keep the local flight until both copies land (cap it at about 1.2 s), then ease across.
  - Expire unconfirmed guesses after about 2 s with a resync.
- **Slow server-side destruction.** At the blast, hide doomed parts on the client with `LocalTransparencyModifier = 1`. Reset it when they become debris.

**Clock-driven movers.** For objects on fixed paths (moving targets, platforms, patrols), make position a pure function of `workspace:GetServerTimeNow()` and the path data.

- Clients draw the position every frame from that function, so the server sends no positions.
- The server moves the body only right before a hit check or a raycast that crosses the path. It also sets `AssemblyLinearVelocity`, so lag-tolerant checks account for the mover's speed.

```luau
-- Illustrative: verify against your own path data.
local function moverPosition(origin: Vector3, axis: Vector3, amplitude: number, period: number): Vector3
	local t = workspace:GetServerTimeNow()
	return origin + axis * (math.sin(t * 2 * math.pi / period) * amplitude)
end
```

**One shared rules module.** Put weapon state in one pure module that the client runs to predict and the server runs to check: magazine, cooldown, a short press buffer, and reload start, finish, and cancel. Fold stats through one shared function on both sides.

- Refill ammo on the shared timer, not an animation marker. Then a faster-reload upgrade only changes clip playback speed.
- Scalable hitboxes follow the same rule: one module serves the client pick, the server check, NPC shooters, and debug drawing (`roblox-security`).

**State as data, not remotes.** Replicate match state as one match folder or entity with attributes:

- mode, phase, and round
- phase end time as `GetServerTimeNow()` (0 for no clock)
- results

Clients compute timers locally. Only the start and leave requests need client events, and the server re-validates both.

**Look pitch for third-person views.** Put the actor's look pitch in the action packet the server relays, instead of replicating the camera: one signed byte in degrees, clamped to ±90 and NaN-checked.

**Server Authority reports.** From the [release thread](https://devforum.roblox.com/t/full-release-ship-fair-and-competitive-games-with-server-authority/4727993):

- Staff clarified (2026-07-09) that the default PlayerScripts use `BindToSimulation` for avatar movement, while a sample shooting flow still uses RemoteEvents. Choose the sync path per mechanic.
- Developers reported (2026-08-25) visible correction jitter under latency. Test collisions and prediction under the network simulator before you ship.
- The `StreamingEnabled` requirement is documented (§0).

## 3c. Packets, payloads, and ids

- **One-byte length prefixes wrap.** Buffer packet libraries may encode short strings with a u8 length, so a string over 255 bytes silently wraps (401 became 145).
  - In one case the client read truncated JSON, parsed the leftover bytes as the next packet id, and dropped every packet in each batch. Controls gated on "state ready" then did nothing.
  - Use the library's long-string type (u16 length) for JSON and any user text, and assert payload sizes on the sender.
  - The symptom is a repeating nil-index error inside the library's read code.
- **Typed decoding checks types, not ranges.** Numbers can still be NaN, infinite, or negative, so keep the §2 poison checks even after an IDL.
- **Self-describing blobs.** A replicated data blob must carry everything needed to decode it: scale, version, and grid cell size belong in the header. A client that looked up the cell size by template name drew an unknown piece at 1/8 size.
- **Entity ids from clients.** When remotes name ECS entities by server id, check three things: the id is a whole number, the entity is alive, and it has the components the remote expects. Map ids through the replicator's lookup.
- **Tool actions right after an equip.** Send the tool identifier and check that it's in the player's inventory or character. Don't count on a replicated equipped-state property arriving first.
- **Instance arguments.** An instance-shaped table, or a path string such as `GetFullName()`, is neither an instance nor an authorization. Check `typeof(x) == "Instance"`, the class, the ancestry, and that this player may act on it ([DevForum thread on instance safety](https://devforum.roblox.com/t/instance-safety-in-remote-events-functions/4700771), 2026-06-24).
- **Effect broadcasts.** For combat VFX, the server validates the action first: movement, cooldown, ownership. Then it broadcasts a small effect id, and clients render a local template. A debounce alone doesn't prove the action was legitimate ([thread](https://devforum.roblox.com/t/how-should-i-prevent-exploiters-spamming-my-remoteevent-for-vfx-replication/4749010), 2026-07-21).
- **Remotes are server-owned.** Create and parent RemoteEvents from server code before clients wait on them; on the client, use `WaitForChild` with a timeout. Recreating or reparenting remotes because a client asks, or once per joining player, is unsafe and disconnects listeners. Diagnose replication timing instead ([thread](https://devforum.roblox.com/t/replicatedstorage-failing-to-replicate-remoteeventsfunctions/4830130), 2026-08-28).
- **Map-loaded gate.** When the server clones a map in at runtime, stamp the map model with its descendant count. A client holding that many descendants has the whole map, so the match can wait for every client before starting. Under streaming, this only works for models that stream atomically or persistently.

## 3d. First-person and character ownership

The client controls its own character, so changes it makes there can replicate.

- In first person, hide the local character with `LocalTransparencyModifier`, never by removing parts. A client that removes parts of its own character can delete them on the server too.
- Animation tracks the owning client plays on its own character replicate to everyone, so don't play local-only cosmetic tracks there.
- On characters that are combat targets, turn `CanQuery` off for accessories. Raycasts then reach the head instead of hats and hair (`roblox-security`).

## 3e. Server facts and social queries (official)

<!-- temporal: 2026-11 -->

- `DataModel.ServerRegion` is the server's three-letter IATA airport code, for example `IAD`, `LHR`, or `NRT`. It's empty in Studio, on the client, or when the region is unknown. Use it for logs, region labels, and analytics, never for trust.
- `Player:GetFriendsInServerAsync()` yields and returns the player's friends in the current server, excluding the player.
- `Player:GetFriendsInUniverseAsync()` returns the local player's friends across the universe, with each friend's place and server, for "join friend" UI. Routing still goes through `TeleportService` options (`roblox-cloud`).
- Wrap both calls in `pcall`, since they're network requests.

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

## 6a. Same-side bindable boundaries

`BindableEvent`/`BindableFunction` never cross the client-server boundary — they connect scripts on the same side. Their argument rules mirror remotes and break code the same way:

- Tables are copied, not referenced: the receiver gets a new table, so identity checks fail and mutations don't propagate back.
- Metatables are stripped in transit; non-string keys can be mangled. Re-attach behavior after delivery, or pass a plain id and look the object up on the receiving side.

Semantics:

- `BindableEvent:Fire()` does not yield; each connected listener runs in its own thread. A listener erroring or yielding neither breaks nor blocks the firer, and listener completion order is not guaranteed.
- `BindableFunction:Invoke()` yields the caller until `OnInvoke` returns, exactly like `RemoteFunction`. Assign `OnInvoke` once — with multiple assignments only the last one executes.

Use bindables to decouple same-side modules (server-to-server signals, client-to-client UI events). They are not a "safe remote": anything crossing clients must still go through a `RemoteEvent` with full validation.

## 7. Measure packet budgets

Track both payload size and frequency. A small payload fired every frame can be worse than a larger
payload sent occasionally. The community `RemotePacketSizeCounter` resource is useful for estimating
supported datatype sizes and testing the 1000-byte unreliable-event ceiling, but its own documentation
notes that some Roblox encoding behavior is undocumented and has edge cases.

Record at least:

- remote name and direction;
- calls per second;
- estimated bytes per call and bytes per second;
- reliable versus unreliable transport;
- player count and representative latency.

Do this in a test place with realistic load. A local ping measurement is not a network-budget
benchmark.

## 7a. Payload/rate budget method (with recipients, fanout, and diffs)

The per-event rows above only matter summed into a *budget*, and the budget lives per direction per
server. Build it deliberately, from measured numbers — never from a library's benchmark table:

1. **Enumerate every remote** with: fire rate at max realistic concurrency (peak fight, not average),
   bytes per call measured in a test place (§7), and — the step most budgets skip — **recipients per
   call**. `FireAllClients` multiplies bytes by the player count and fanout is the dominant term for
   broadcast events; a 200-byte event to 40 players every frame is ~19 KB/frame ≈ 1.1 MB/s.
2. **Classify each event** replaceable (unreliable-eligible; a newer value supersedes a lost one) vs
   must-arrive (reliable, and then count its retransmission cost under packet loss too). Reuse the §6
   decision; the budget does not change it.
3. **Budget per direction:** client→server traffic scales per player (N players = N uplinks); server
  →client scales per recipient (N players × recipients per event). Compare against the Developer
   Console's measured baseline under load, not a number someone quoted.
4. **Snapshot vs diff:** for state many clients observe, send a full snapshot only on join (and after
   a replaceable-data gap), then per-tick diffs of changed fields (see "Replicate state to subscribed
   clients" below). A diff that always includes 90% of fields is a snapshot with extra steps —
   measure the actual changed-field distribution before believing the diff is small.
5. **Unreliable cap as a hard invariant:** every unreliable event payload must stay under the
   documented 1000-byte ceiling — payloads over it are *dropped*, not truncated ([UnreliableRemoteEvent
   docs](https://create.roblox.com/docs/reference/engine/classes/UnreliableRemoteEvent)). Encoding
   makes pre-fire size hard to predict (buffers and other types compress), so verify by test firing
   and reading Studio's over-limit warning, not by counting your table's fields. Put the check in
   review: any new unreliable event gets a measured payload size next to its definition.
6. **Re-verify after changes:** a budget built once rots silently. Re-run the §7 measurement when a
   remote's rate, payload, or recipient set changes, and when player-count ceilings change.

## 7b. Replicate state to subscribed clients

For a state object that many clients must observe, avoid re-sending whole tables per change. Keep the state server-owned and let clients subscribe by a token or name; each client receives an initial snapshot plus delta updates for only the fields that changed. Community replication modules (e.g. Replica, successor to ReplicaService, https://devforum.roblox.com/t/replica-server-to-client-state-replication-module/3216980) implement this pattern; you can also build it with a single state RemoteEvent carrying a versioned delta. Keep creation and mutation server-side so the client subscription is a read-only mirror.

## 7c. Shrink payloads with binary serialization

When a high-frequency remote exceeds budget, replace high-precision tables with compact typed fields. Pick the smallest precision that reads correctly per field (a quantized `CFrame` or low-bit float for positions, a small integer for counters) rather than always sending 64-bit values. Community serialization modules (e.g. Bitstream, https://devforum.roblox.com/t/bitstream-%E2%80%93-binary-framework/4788654) provide typed, precision-varied formats; keep a schema/version so both sides agree on field order and size. Prefer this for replaceable, high-frequency data (positions, aim), not for state that must be exactly once and easily debugged.

## 7d. Typed IDL / generated network modules (blink et al.)

Schema-first compilers (blink, Zap, and similar IDL tools) generate the remote plumbing from a
declarative schema: typed payloads, compact buffer encoding, and compile-checked call sites. Adopt by
criteria, not fashion:

- **Adopt when:** payloads have grown beyond a handful of fields across many remotes, multiple people
  (or agents) edit the wire contract, or bandwidth actually shows in the budget from §7a. For a game
  with five remotes, a raw `RemoteEvent` layer plus the validation discipline of §2 is simpler and has
  one less build dependency. Follow the project's existing choice if it already has one.
- **Pin the schema, verify the regen.** Pin the compiler's version the same way as any tool
  (`roblox-tooling` version-pinning). Run codegen in CI on every change to the schema or its inputs,
  and gate on the *generated artifact*, not just the exit code: assert the output files exist,
  regenerate cleanly, and diff-check in review. A stale generated module that still compiles is the
  classic silent failure — hand-edited types drift from the schema and nobody notices until a payload
  misreads. A generator may also exit 0 on partial failure classes, so "it didn't error" is not
  evidence the module matches the schema.
- **Malicious read-side validation is still yours.** Generators validate the *writer's* side at
  compile time and (per blink's documented behavior) validate incoming builtin-primitive data before
  it reaches handlers. That is not a security boundary: struct/map/enum-shaped values are not fully
  checked by such tools, and **every client argument remains attacker-controlled** regardless of the
  type system — a schema guarantees shape, never semantics. State checks, cooldowns, range, and
  server-owned outcomes (§2, §3) still apply at every handler, including generated ones. Compression
  also makes traffic harder to snoop with RemoteSpy, which is a nuisance-reduction, not a defense:
  assume payloads are still readable to a determined attacker.
- **Call modes are per-event decisions.** A schema declares per event whether it is reliable or
  unreliable and which listener API exists (e.g. blink's `Call: SingleSync/ManySync/SingleAsync/
  ManyAsync/Polling`, with sync listeners documented as unable to yield). Pin each event's mode to its
  delivery requirement (§6 rules) and verify against the pinned version's docs, not memory — mode
  semantics and limits change between compiler versions.
- **The 1000-byte unreliable cap is not compiler-enforced.** An IDL will happily emit an unreliable
  event whose serialized payload exceeds the ceiling, and Roblox drops such payloads silently at
  runtime (§7a). Add a build-time or CI size check on unreliable event definitions (measured or
  worst-case serialized size), because neither the schema nor the type system will catch it.
- **Failure modes to watch:** schema changes that rename a field silently mismatch deployed older
  clients (version the wire, not just the module); generators that re-order struct fields change the
  binary layout (regenerate both sides atomically); and per-VM codegen output must not be hand-edited,
  which is exactly what the CI regen gate above exists to catch.

## 7e. Platform ceiling vs application rate limits

The engine's own transport ceiling is not your rate limit. [RemoteEvent](https://create.roblox.com/docs/reference/engine/classes/RemoteEvent) and `UnreliableRemoteEvent` each document
**approximately 500 requests per second, per client**, with the pool **shared
among all remote events of the same type**, so a burst across many remotes is what trips it, not one
hot remote. Reliable events can buffer when no listener is attached; unreliable events may be dropped. Do not confuse missing-listener diagnostics with proof of a throttle.

Operator guidance: treat this approximate transport ceiling as a limit to stay well below, not a target:

- Keep your application budget an order of magnitude below it — the §4 per-player throttle intervals
  (≥ 0.2 s per action) already cap a single remote around 5 req/s, and a client's *total* FireServer
  rate across all remotes should stay well under tens per second.
- Reserve headroom for bursts: UI spam, death loops, and auto-fire exploits all draw from the same
  shared pool; your throttling should reject the request before the engine drops it silently.
- Server→client sends (`FireClient`/`FireAllClients`) are not documented against this per-client
  client→server limit; their cost is measured as bandwidth budget (§7a), not invocation rate.

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

### Edit-mode network mock

Client code that requires a network module fails to load in edit mode (no player, no server). Wrap the network layer so edit mode gets a local loopback instead, and keep the wrapper behind one module boundary so call sites never branch on context themselves:

```luau
-- Network/init.luau
local RunContext = require(Shared.RunContext)
local Network

if RunContext.IsEdit then
    Network = require(script.mock) :: any -- loopback events/functions
else
    Network = require(Packages.YourNetworkLayer)
end

return Network
```

The mock implements the same surface (`Event`, `Function`, or your project's equivalents) but fires signals locally instead of over remotes. Client and shared modules can then run and be exercised in Studio without a play session, and remote-specific bugs stay confined to code that actually runs online. The same split pattern applies to any server-only dependency a client-facing module would otherwise touch. Note the loopback skips real serialization and validation, so behavior differences found in edit mode are not conclusive: re-test through real remotes before shipping.

## 10. Text chat: TextChatService (modern) and legacy Chat

> For chat features (channels, commands, bubble chat, filtering and compliance), load `roblox-text-chat`. This section keeps the replication and server-authority summary.

[TextChatService](https://create.roblox.com/docs/reference/engine/classes/TextChatService) is the current chat system. The legacy chat system was retired April 30, 2025: Roblox auto-migrates experiences still on `ChatVersion.LegacyChatService`, and custom integrations that bypass TextChatService break or get moderated ([migration announcement](https://devforum.roblox.com/t/migrate-to-textchatservice-removing-support-for-legacy-chat-and-custom-chat-systems/3237100), [status update](https://devforum.roblox.com/t/update-on-legacy-chat-deprecation-and-textchatservice-migration/3376880)). <!-- temporal: 2025-05 --> `TextChatService.ChatVersion` is not scriptable; set it in Studio. Never build new chat features on the legacy `Chat` service.

### Instance tree

Default runtime tree when `TextChatService.CreateDefaultTextChannels` and `CreateDefaultCommands` are true (both are Studio properties, not scriptable):

- `TextChatService.TextChannels` (Folder): `RBXGeneral` (player messages), `RBXSystem` (system messages; red when `TextChatMessage.Metadata` contains "Error"), `RBXTeam[BrickColor]` per team, `RBXWhisper:[UserId1]_[UserId2]` per whisper pair.
- `TextChatService.TextChatCommands` (Folder): `RBXClearCommand`, `RBXEmoteCommand`, `RBXHelpCommand`, `RBXMuteCommand`, `RBXTeamCommand`, `RBXWhisperCommand`, and others (`/e`, `/t`, `/w`, `/mute`, ...).
- Configuration singletons directly under `TextChatService`: `ChatWindowConfiguration`, `ChatInputBarConfiguration`, `BubbleChatConfiguration`, `ChannelTabsConfiguration`.

You can add your own `TextChannel` and `TextChatCommand` instances even with defaults on. A `TextChatCommand` must be parented to `TextChatService` to function.

### Client/server split ([TextChannel](https://create.roblox.com/docs/reference/engine/classes/TextChannel))

- `TextChannel:SendAsync(message, metadata)` (client only). Sends a player message to the server; the engine filters it server-side, and clients receive "the result of the filtered message from the server". Metadata over 200 characters means the message is not delivered.
- `TextChannel:DisplaySystemMessage(message, metadata)` (client only). Visible only to that local user and **not** automatically filtered or localized.
- `TextChannel.MessageReceived` / `TextChatService.MessageReceived` (client only).
- `TextChannel:AddUserAsync(userId)` (server only). Adds a `TextSource`; returns `nil, false` when the user has chat off or is not in the server.
- Server-side delivery control: `TextChannel.ShouldDeliverCallback(message, textSource)` (return `false` to withhold from a recipient) plus `TextChatService:CanUserChatAsync` / `CanUsersChatAsync` / `CanUsersDirectChatAsync` for platform permission gates.

`OnIncomingMessage` (on both `TextChatService` and `TextChannel`) is documented client-only: it decorates or replaces messages for display by returning `TextChatMessageProperties`; returning `nil` leaves the message unchanged. `TextChatService.OnIncomingMessage` runs before any `TextChannel.OnIncomingMessage`. Define each callback exactly once: multiple bindings override one another nondeterministically. Messages are not replicated to a custom UI by themselves; the default chat UI consumes `MessageReceived` for you, and a custom UI must render those payloads itself.

### Filtering rules

- Player messages sent via `TextChannel:SendAsync` are filtered by the engine server-side; do not double-filter before `SendAsync`.
- `DisplaySystemMessage` strings are not filtered. Static developer-authored text is fine. If a system message embeds player input (names, item names), filter that input server-side with `TextService:FilterStringAsync` first; the same rule applies as for any other user-generated text.

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

### Legacy Chat (deprecated; migration reference only)

- `Chat:Chat(partOrCharacter, message, color?)` fires `Chat.Chatted` and drives the legacy bubble-chat LocalScript. Replace with `TextChatService:DisplayBubble()` and `BubbleChatConfiguration`.
- `Chat:FilterStringAsync` / `Chat:FilterStringForBroadcast` filter legacy chat text; the client-side call form is deprecated. Replace with server-side `TextService:FilterStringAsync` ([Chat](https://create.roblox.com/docs/reference/engine/classes/Chat)).
- `Chat:RegisterChatCallback` (`OnServerReceivingMessage`, `OnClientFormattingMessage`) customizes the legacy Luau chat pipeline. There is no 1:1 port; re-model the logic on `TextChannel.ShouldDeliverCallback` and the `OnIncomingMessage` callbacks.

## Networking checklist

- [ ] Every remote has a documented contract.
- [ ] Server handlers validate type, range, ownership, state, and rate.
- [ ] Handlers never rely on remote tables being references: state is re-resolved server-side.
- [ ] Handlers do not assume functions, metatables, or mixed-key tables survive the boundary.
- [ ] Trusted values come from server definitions or server state.
- [ ] Long work cannot be forced through an unbounded `RemoteFunction`.
- [ ] Reliable and unreliable transports are chosen by data semantics, not by a blanket performance claim.
- [ ] Packet size and fire rate are measured for high-frequency remotes.
- [ ] Payload/rate budget exists per direction (rate × bytes × recipients); snapshot-on-join + diffs for observed state.
- [ ] Unreliable payloads verified under the 1000-byte ceiling by test firing, not field counting.
- [ ] Time-sensitive claims validated with a shared clock (`GetServerTimeNow`), freshness bounds, and in-flight ids; client timestamps never authorize outcomes on their own.
- [ ] Static geometry re-raycasts server-side; dynamic targets validated with tolerance, not current-position raycasts.
- [ ] If a typed IDL/generator is used: version pinned, CI regen gate on generated output, read-side semantic validation intact at handlers, unreliable size check in CI.
- [ ] Player cleanup removes limiter, subscription, and connection state.
- [ ] Suspicion handling tolerates false positives and does not expose private data.
- [ ] Server Authority projects: the six-setting bundle verified and prediction/rollback behavior understood before review sign-off.

## Community ecosystem (leads, not sources)

Top-sorted DevForum canon for networking libraries. Verify status in-thread; several are archived.

- State replication: [Replica](https://devforum.roblox.com/t/replica-server-to-client-state-replication-module/3216980) (2024, current favorite; pairs with ProfileStore per [PlayerState](https://devforum.roblox.com/t/playerstate-profilestore-replica-without-the-headache/3766568)); [ReplicaService](https://devforum.roblox.com/t/replicate-your-states-with-replicaservice-networking-system/894736) older.
- Remote tooling: [Packet](https://devforum.roblox.com/t/packet-networking-library/3573907) (2025), [Warp](https://devforum.roblox.com/t/warp-very-fast-powerful-networking-library/2779813) (2024), [BridgeNet](https://devforum.roblox.com/t/bridgenet-insanely-optimized-easy-to-use-networking-library-full-of-utilities-now-with-roblox-ts-v199-beta/1909935) (legacy).
- Case study: [60x bandwidth reduction in Astro Force](https://devforum.roblox.com/t/how-we-reduced-bandwidth-usage-by-60x-in-astro-force-roblox-rts/1202300), the practical RTS-scale optimization write-up.
- [StreamX is DEPRECATED](https://devforum.roblox.com/t/deprecated-streamx-reduce-lag-and-prevent-map-cloning/1992484): do not recommend; example of a once-canonical library that died.

## Resolve accepted combat outcomes before consequences

Resolve target eligibility and damage interception in the authoritative combat owner before sending death presentation, granting hit rewards, or applying attacker penalties. Return an explicit rejected, survived, or eliminated outcome as appropriate to the game's rules. A raycast or physics contact is only a candidate hit; a shield or remaining life can turn an accepted contact into a survived outcome.

Test invalid targets, protected targets, nonlethal accepted hits, and final hits through both human and bot attack paths. Observe the victim's own client and the attacker's consequences. A surviving player must not receive a lethal camera/control path, and a rejected contact must not apply a penalty meant for a valid hit.
