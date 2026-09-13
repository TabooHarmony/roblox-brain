# Roblox Security & Anti-Exploit


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

Use this skill when designing security systems, auditing existing code for vulnerabilities, or hardening a game against common exploit vectors.

## Core Principle

**The client is compromised. Always.** Exploiters run arbitrary Luau on the client via injection tools. Every LocalScript, every ReplicatedStorage module, and every client-side value is readable and writable by attackers. The server is the source of truth, but the implementation depends on the authority model.

## Authority Models

### Classic replication

Validate client requests and custom movement against server-owned state. Do not trust client-reported damage, currency, inventory, permissions, or positions. Network ownership is a physics simulation choice, not a complete security boundary.

### Server Authority

Server Authority is an opt-in Roblox model configured through `Workspace.AuthorityMode = Server` and the required replication, fixed-simulation, streaming, and input settings. The server remains authoritative for core gameplay while clients predict input and recover from misprediction through rollback and resimulation.

For Server Authority projects:

- put synchronized simulation logic in `RunService:BindToSimulation()` (requires `Workspace.UseFixedSimulation` enabled in Studio);
- use the Input Action System for inputs that affect the core simulation;
- do not write simulation-access properties such as `BasePart.CFrame` from a `Heartbeat` handler as a substitute for authoritative simulation;
- keep validation for custom attacks, dashes, teleports, purchases, permissions, and other game-specific actions at the server boundary;
- use `RunService:SetPredictionMode()` only when the game's prediction policy needs explicit control.

See the [Server Authority model](https://create.roblox.com/docs/projects/server-authority) and [advanced techniques](https://create.roblox.com/docs/projects/server-authority/techniques).

### Server Authority migration reality check

The official docs read like a flag flip, but the real cost depends on how much simulation you author. Practitioner experience is two-sided, so do not assume either extreme:

- **Stock/off-the-shelf characters with little custom simulation:** migration can be genuinely simple. A beta tester who ran the API for over a year described flipping the switch for stock Humanoids as a minor change in most cases.
- **Authored simulation (fighting games, custom movement/physics, rollback-style mechanics):** budget like a rewrite, not a configuration change. One practitioner porting a rollback fighter that was already simulation-compatible spent over a month getting back to feature parity, and warns the integration is not something you can cleanly undo once started. If the project cannot afford that, prefer classic replication with server-side validation instead.

Practical constraints once you commit:

- **Sources of truth must be independent and deterministic.** Reconstruct state from synchronized `time()`-derived keys, not from live attributes. Keep a per-frame snapshot of the minimum state needed to resimulate, and after a rollback discard snapshots newer than the reconciled frame.
- **Attributes are the serialization channel and they budget hard.** The attribute payload is roughly 1 KiB; a few CFrames or Vector3s can consume it. Pack dense numeric state into bit flags (32 bits per value; split a 64-bit Lua number with `math.fmod` if you need two) instead of storing floats.
- **Client input can be rolled back.** Do not rely on a single input event reaching the simulation. Re-parse buffered input each frame so a misprediction retries instead of dropping the action, and expect a small input delay buffer in real-time games.
- **Side effects are the sharpest edge.** Anything non-deterministic (UI toggles, spawns, one-shot events) fires again on resimulation unless transitions are idempotent. Beta testers call side effects the biggest pain point and recommend observing attribute changes during `PreRender` rather than reacting inside the simulation where you cannot tell a re-run from a first run.

Practitioner-sourced synthesis (not official API documentation): the nightmare account that motivated this is at <https://devforum.roblox.com/t/server-authority-client-beta-was-a-damn-nightmare-heres-some-advice/4712758>; the official [Server Authority model](https://create.roblox.com/docs/projects/server-authority) and [advanced techniques](https://create.roblox.com/docs/projects/server-authority/techniques) docs remain the API source of truth.

### Settings bundle and debug surface

Server Authority is only real when the whole settings bundle travels together. Setting `Workspace.AuthorityMode = Enum.AuthorityMode.Server` automatically sets the other five; verify all six during review because a place file can drift:

1. `Workspace.AuthorityMode` = `Enum.AuthorityMode.Server`
2. `Workspace.NextGenerationReplication` enabled
3. `Workspace.PlayerScriptsUseInputActionSystem` enabled
4. `Workspace.SignalBehavior` = `Enum.SignalBehavior.Deferred`
5. `Workspace.UseFixedSimulation` enabled
6. `Workspace.StreamingEnabled` enabled

Debug surface for review sessions:

- Studio ships a server authority visualization overlay for review sessions, but its shortcuts, counters, and per-reason input-drop tallies are not documented on the pages reviewed here. Do not quote specific numbers from it as if they were published thresholds; describe what you observed instead.
- Read prediction state from the scriptable surface instead: `RunService:SetPredictionMode()` forces prediction for a given instance and is client-only, and `Instance.PredictionMode` reflects the mode applied to that instance.

Misprediction and rollback are normal operation in this model, not defects: clients cannot predict other players' inputs, so corrections should be small and imperceptible when tuned.

## Exploit Vectors & Mitigations

### Movement and physics exploits

| Attack | How it works | Mitigation |
|--------|-------------|------------|
| Speed or fly exploit | Client attempts to control movement outside the game's allowed state | In Server Authority, use the engine's server-authoritative simulation and prediction model. In classic projects, validate custom movement transitions with tolerance for seats, respawns, teleports, and correction. |
| Teleport or noclip | Client requests or produces an impossible game-specific transition | Validate the requested action and the server's state, rather than blindly snapping `CFrame` every frame. Record suspicion and investigate repeated violations instead of punishing one lag spike. |

Do not copy a blanket `Heartbeat` position checker into a Server Authority project. The server already owns the authoritative simulation, and writing simulation-access properties outside the simulation callback can error. If a classic project needs custom movement checks, keep the checker aware of legitimate state transitions and clean all per-player state on `PlayerRemoving`.

### Server-side anticheat (classic replication)

Server-side anticheats detect movement abuse by checking sustained airborne time and jump-ceiling violations (flight), horizontal velocity above a threshold using relative velocity so moving platforms don't false-flag (speed), single-tick jumps and accumulated positional drift (teleport), raycasts through collidable geometry (noclip), and consecutive angular/linear velocity spikes (fling). Structure checks as small modules exposing an id, weight, state, and a `check(state, delta)` function; tune thresholds with a ~1.5x multiplier to absorb replication quirks, and add a history record that lowers thresholds for repeat offenders. Treat these as weakening measures, not a silver bullet: subtle sub-threshold exploits slip through, and Server Authority remains the robust answer for physics-based exploits.

*Community/practitioner content (lead: https://devforum.roblox.com/t/sinas-serverside-anticheat-102/4801833).*

### Remote Exploits

| Attack | How it works | Mitigation |
|--------|-------------|------------|
| Remote spam | Fire remotes at extreme rates | Per-player rate limiter |
| Argument spoofing | Send wrong types/values | Validate every argument type and range |
| Remote sniffing | Read remote names to reverse-engineer API | Doesn't matter if validation is solid |
| Replay attack | Re-fire a valid remote call | Idempotency checks, transaction IDs |

For the rate limiter and argument validation implementations, see `roblox-networking`.

### Economy Exploits

| Attack | How it works | Mitigation |
|--------|-------------|------------|
| Item duplication | Race condition in trade/save | Session locking, atomic operations |
| Negative purchase | Send negative quantity to gain items | Validate quantity > 0 server-side |
| Transaction replay | Replay a purchase remote | Unique transaction IDs, check if already processed |
| DataStore rollback | Exploit save timing to duplicate | Session locking with server JobId |

### DataStore Exploits

| Attack | How it works | Mitigation |
|--------|-------------|------------|
| Save spam | Force repeated saves to exhaust budget | Server-controlled save intervals only |
| Session hijack | Fake session to duplicate across servers | Session lock with JobId verification |
| BindToClose skip | Exploit shutdown timing | BindToClose with parallel saves + timeout |
| Unsaveable payload | Remote accepts Instance/userdata into saved tables; save throws and rolls back | Validate every persisted field's type at the remote boundary; never store client-supplied tables unvalidated |
| Malformed string | Invalid UTF-8 bytes pass type checks but fail serialization | `utf8.len(value)` must return a count before persisting client strings |
| NaN rollback | NaN smuggled through settings remotes breaks serializers or comparisons, rolling back saves | Reject `x ~= x` and infinities wherever client numbers enter persisted state |

Practitioner lead: TheGreatSageEqualToHeaven's "Data store vulnerabilities" gist documents these rollback vectors found in major titles. Treat as community research, not official documentation.

## Security Audit Checklist

Run through this for every game before publish:

```
CRITICAL (game-breaking if missing):
[ ] All game state is server-authoritative
[ ] The authority model is documented and its required Workspace settings are verified
[ ] All RemoteEvent handlers validate types of EVERY argument
[ ] All RemoteEvent handlers have rate limiting
[ ] DataStore operations use session locking
[ ] No client-side currency/inventory mutations
[ ] MarketplaceService purchases verified via ProcessReceipt
[ ] No sensitive logic in LocalScripts or ReplicatedStorage

HIGH (exploitable if missing):
[ ] Custom movement and action transitions are validated without fighting the selected authority model
[ ] BindToClose saves protected against data loss
[ ] Trading system uses atomic operations
[ ] No trusting client-reported values (damage, position, items)
[ ] RemoteFunction return values not trusted by server
[ ] ProximityPrompt/ClickDetector/DragDetector handlers validated like remotes
[ ] DragDetector.RunLocally is false or its client path is re-validated server-side
[ ] Ban flows use the native Players ban API with appeal path documented

MEDIUM (quality/fairness):
[ ] Cooldowns enforced server-side (not just client UI)
[ ] Leaderboard values computed server-side
[ ] Anti-AFK detection for reward systems
[ ] Chat filter applied (TextService:FilterStringAsync)
```

## Patterns

### Never Trust Client Values

```luau
-- BAD: Client tells server how much damage to deal
DamageRemote.OnServerEvent:Connect(function(player, target, damage)
    target.Humanoid:TakeDamage(damage) -- exploiter sends 999999
end)

-- GOOD: Server computes damage from game state
AttackRemote.OnServerEvent:Connect(function(player, targetId)
    local weapon = getEquippedWeapon(player)
    if not weapon then return end
    local target = resolveTarget(targetId)
    if not target then return end
    if not isInRange(player, target, weapon.Range) then return end
    if not checkCooldown(player, weapon) then return end

    local damage = weapon.BaseDamage * getDamageMultiplier(player)
    target.Humanoid:TakeDamage(damage)
end)
```

### Session Locking

Do not implement session ownership as a bare `game.JobId` field. A lock without
expiry, heartbeat, stale-owner handling, and crash recovery can block a profile
forever. Use a maintained profile library, or implement the complete protocol
described in `roblox-data`. Do not layer a second lock over a library that
already owns the profile lifecycle.

### Sanity Checks (Defense in Depth)

Even with server authority, add sanity checks for values that should be bounded. These protect custom state and remote arguments; they are not a replacement for the Server Authority simulation model:

```luau
-- Clamp values that should never exceed known bounds
local function sanitizePlayerStats(stats)
    stats.Level = math.clamp(stats.Level, 1, MAX_LEVEL)
    stats.Gold = math.max(stats.Gold, 0) -- never negative
    stats.Health = math.clamp(stats.Health, 0, stats.MaxHealth)
    return stats
end
```

## Native Enforcement APIs (Player Bans)

The Players class ships a native ban API: `Players:BanAsync`, `Players:UnbanAsync`, and `Players:GetBanHistoryAsync`, all gated by the `Players.BanningEnabled` property, which cannot be set from Luau and must be toggled in Studio's Players properties window. All three are server-only: client calls error, and Studio/Team Test runs do not apply bans to production. Each performs an HTTP call to backend services that is throttled and can fail; batch calls over `UserIds` retry per ID and aggregate failures into one error message (`failure for UserId {}`), so wrap calls in `pcall`. They also back the [User Restrictions Open Cloud API](https://create.roblox.com/docs/cloud/reference/UserRestriction) for third-party moderation tooling.

### BanAsync config (BanConfigType)

| Field | Type | Rules |
|-------|------|-------|
| `UserIds` | array (required) | UserIds to ban. Max size 50. |
| `Duration` | integer (required) | Seconds. `-1` = permanent. `0` and all other negative values are invalid. |
| `DisplayReason` | string (required) | Shown in the error modal when the banned user tries to join. Max 400 characters, text filtered. |
| `PrivateReason` | string (required) | Internal notes returned by `GetBanHistoryAsync`. Max 1000 characters, not filtered, never shared with the client. |
| `ApplyToUniverse` | boolean (optional, default `true`) | `false` limits the ban to the calling place. Banning someone in the start place excludes them from the whole universe regardless. |
| `ExcludeAltAccounts` | boolean (optional, default `false`) | `true` disables propagation to suspected alternate accounts. |
| `ApplyDeviceBlock` | boolean (optional, default `false`) | Blocks the banned user's device from rejoining for 24 hours after the ban. Only `UnbanAsync` lifts a device block; unbanning through the Open Cloud API or Creator Hub does not. |

### UnbanAsync and GetBanHistoryAsync

- `Players:UnbanAsync(config)` takes `{UserIds (max 50), ApplyToUniverse}`. An unban only lifts bans with the same scope: a universe-level unban does not invalidate a place-level ban and vice versa.
- `Players:GetBanHistoryAsync(userId)` returns `BanHistoryPages` (inherits `Pages`). Use it to escalate: count prior bans and previous `Duration` values, and read `PrivateReason` notes, when computing the next ban length.

### Escalation ladder pattern

Pair detection with the native API instead of kicking in a loop. Illustrative shape:

```luau
-- ServerScriptService. Detection modules feed scores; the ladder decides.
local REPRIEVES = { [1] = 3600, [2] = 86400 } -- 1h, then 24h; third strike permanent

local function enforce(player: Player, detectorId: string)
    local history = Players:GetBanHistoryAsync(player.UserId)
    local strikes = #history:GetCurrentPage() + 1 -- iterate Pages for full history

    local duration = REPRIEVES[strikes] or -1
    local config: BanConfigType = {
        UserIds = { player.UserId },
        Duration = duration, -- -1 = permanent; 0 and other negatives are invalid
        DisplayReason = "Violated server rules (action: " .. detectorId .. ")",
        PrivateReason = detectorId .. " | strike " .. strikes,
        ApplyToUniverse = true,
        ExcludeAltAccounts = false,
        ApplyDeviceBlock = strikes >= 3,
    }
    local ok, err = pcall(Players.BanAsync, Players, config)
    if not ok then warn("ban failed:", err) end -- throttled HTTP can fail per UserId
end
```

`Players.BanningEnabled` must be on for all three methods; verify it in Studio before shipping a flow that depends on them.

Enforcement is a product decision, not an automatic response. Bans carry appeal implications, `DisplayReason` is filtered and shown to real users, and false positives from lag or tuning mistakes are permanent records in ban history. The docs themselves direct you to publish experience rules and provide an appeal path. Log detection context first, keep thresholds forgiving, and reserve permanent bans for clear violations. <!-- temporal: 2026-09 -->

## Client-Triggerable Interaction Instances

`ProximityPrompt`, `ClickDetector`, and `DragDetector` are remote-equivalent attack surfaces: the engine delivers a client interaction to a server-side callback with a `Player` argument, so exploiters can trigger them without your UI and outside your intended flow. The exploit table above covers only `RemoteEvent`s; these belong in the same audit.

| Instance | Server-facing entry point | What the server must validate |
|----------|---------------------------|-------------------------------|
| `ProximityPrompt` | `Triggered(playerWhoTriggered)`, `TriggerEnded(playerWhoTriggered)` | Rate/hold logic is client-assisted: `HoldDuration` gating happens on the client, so re-check state, cooldown, and entitlements server-side on every trigger. |
| `ClickDetector` | `MouseClick(playerWhoClicked)` | Distance: `MaxActivationDistance` (studs) bounds where the engine shows the prompt, but treat a click received beyond server-computed range as spoofed state, not just UI noise. |
| `DragDetector` | `DragStart` / `DragContinue` / `DragEnd` | Drag limits (`MaxDragTranslation`, `MinDragTranslation`, `MaxDragAngle`, `MinDragAngle`) impede motion generation, they are not constraints; clamp final positions server-side. |

`DragDetector.RunLocally` (default `false`) deserves special attention. When `false`, drag signals replicate to the server, which processes cursor rays, mutates the data model, and replicates results onward; the server still owns the outcome, so validate it. When `true`, the client processes those signals itself and does not replicate them; resulting changes reach the server only through your own `RemoteEvent` plumbing, which puts the entire burden back on remote validation. Treat `RunLocally = true` like any client-authored input channel and re-derive the result server-side.

## Script Sandboxing and Capabilities

Sandboxing is a defense-in-depth layer for code you did not write: toolbox models, plugin-supplied or community-contributed scripts, and player-authored code. It is experimental (client beta) and complements, never replaces, server-side validation.

- Enable per place: `Workspace.SandboxedInstanceMode` must move from `Default` to `Experimental` in Studio before `Sandboxed` does anything.
- `Instance.Sandboxed` (on Models, Folders, Scripts, and their descendants) marks a sandboxed container; scripts inside can only act per `Instance.Capabilities`, a `SecurityCapabilities` set spanning execution control (`RunClientScript`, `RunServerScript`), instance access, Luau functionality, and engine API access.
- `Instance.IsInSandbox` is read-only and Studio-only, reporting whether an instance sits in a sandboxed container.
- Missing capabilities fail with explicit errors (for example "lacking capability AccessOutsideWrite"), and scripts without an execution capability fail to start with a warning.
- Scope guard: the capability set for nested containers is the intersection with the outer container; sandboxed scripts cannot fire events or call functions on unsandboxed instances with larger capability sets.
- The docs advise avoiding the `AccessOutsideWrite` capability because sandboxing guarantees weaken when scripts can reach any instance.

Reviewed against the [Script capabilities](https://create.roblox.com/docs/scripting/capabilities) page, whose example capabilities (`AccessOutsideWrite`, `CreateInstances`, `Network`, `RunServerScript`, `RunClientScript`) are the verified member names. <!-- temporal: 2026-09 -->

## What NOT to Do

- **Don't obfuscate client code**: it doesn't stop exploiters and makes debugging harder
- **Don't use _G for security state**: it's globally readable and writable
- **Don't kick without logging**: you need data to distinguish false positives from real exploits
- **Don't over-validate movement**: too strict = legitimate players get false-flagged on lag spikes, and blanket checks fight Server Authority prediction. Use the selected model's simulation path and tolerate legitimate corrections.
- **Don't rely on client-side anti-cheat**: exploiters disable it first

## Community ecosystem (leads, not sources)

- Threat history: [Exploiting Explained](https://devforum.roblox.com/t/exploiting-explained/170977) (2.9k likes — executor timeline doc); [2025 mass hacking operation PSA](https://devforum.roblox.com/t/psa-to-all-roblox-developers-massive-hacking-operation-taking-over-massive-front-page-games/3913726); [Delta Executor detection](https://devforum.roblox.com/t/instant-detection-of-delta-executor-patched/3971400) (note: patched = fingerprint rotates).
- Backdoors: [remove backdoors](https://devforum.roblox.com/t/how-to-remove-backdoors-from-your-game/511548); [malicious scripts/plugins clearing](https://devforum.roblox.com/t/clearing-your-game-of-malicious-scripts-plugins-and-backdoors/511830).
- Posture: [How you should secure your game](https://devforum.roblox.com/t/how-you-should-secure-your-game-a-beginner-guide-for-secure-networking-and-developing-anticheats/351775); [Client anti-cheats aren't as bad as you think](https://devforum.roblox.com/t/client-anti-cheats-arent-as-bad-as-you-think/2471974) (detector-not-punisher framing).
