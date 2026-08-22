# Roblox Performance: Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

Detailed performance targets, profiling guides, optimization patterns, and platform-specific guidance.

## Starting Performance Targets

These are investigation thresholds, not Roblox platform limits. Replace them
with measurements from representative devices and your experience's workload.

### Server
| Metric | Starting target | Investigate at |
|--------|-----------------|----------------|
| Heartbeat time | < 16ms (60Hz) | > 33ms (below 30Hz) |
| Script time | < 10ms/frame | > 20ms |
| Memory | stable baseline | sustained growth |
| Network out | measured baseline | congestion or latency |
| DataStore budget | query `GetRequestBudgetForRequestType()` | low budget per request type |

### Client
| Metric | Starting target | Investigate at |
|--------|-----------------|----------------|
| FPS (desktop) | 60 | < 30 |
| FPS (mobile) | 45 | < 30 |
| Memory | stable device-tier baseline | sustained growth or OS termination |
| Load time | < 10s to playable | > 20s |
| Input latency | < 100ms | > 200ms |

## Profiling Tools

### MicroProfiler (Ctrl+F6)
Per-frame breakdown of time spent in scripts, physics, rendering. The primary tool for finding what's actually slow.

- Server: View → MicroProfiler
- Client: Ctrl+F6 toggles the profiler; Ctrl+Alt+F6 opens its detailed timeline
- Look for: long bars in "Script" category, physics spikes, render thread stalls

### Developer Console (F9)
- **Stats**: Memory, network, render stats
- **Server Stats** (game owner): Server-side metrics
- **Script Performance**: Per-script CPU time

### Script Profiler (Ctrl+Alt+F5)
- Per-script CPU usage and heap allocations
- Identifies which scripts are hot

## Parallel Luau

Parallel Luau is a worker model, not a switch that makes an existing script faster. An `Actor` provides an isolation boundary for scripts that can run concurrently. The useful shape is usually:

1. the serial coordinator gathers small, immutable inputs;
2. workers perform expensive math, visibility tests, or simulation calculations;
3. workers return raw results;
4. the coordinator synchronizes and applies Roblox instance changes.

```luau
local bindable = script.Parent:WaitForChild("Work")

bindable.Event:ConnectParallel(function(input)
    local result = expensivePureCalculation(input)

    -- DataModel writes and other restricted operations belong back in serial.
    task.synchronize()
    script.Parent.Result.Value = result
end)
```

The code above is illustrative. Keep the parallel section free of instance writes unless the current API explicitly permits the operation. Avoid moving a large mutable object graph between the coordinator and workers. Actor setup, synchronization, and contention can cost more than the work being offloaded.

The practical rule is: profile first, isolate a pure or read-heavy calculation, compare against the serial version, and keep the parallel path only if the MicroProfiler shows a real win on target hardware.

## Common Performance Issues

### Scripts

| Problem | Symptom | Fix |
|---------|---------|-----|
| Heartbeat loop over many instances | Server frame time spike | Event-driven or batch with yielding |
| Repeated workspace lookups | Unnecessary overhead | Cache references in variables |
| Table allocation in hot paths | GC pressure, frame spikes | Reuse preallocated tables |
| String concatenation in loops | O(n²) allocation | `table.concat()` |
| Signal over-subscription | Many listeners on one event | Batch or partition |
| Unthrottled RenderStepped | Client FPS drop | Only use for camera/input, throttle everything else |
| require() in loops | Repeated module resolution | Cache module reference outside loop |

### Memory

| Problem | Symptom | Fix |
|---------|---------|-----|
| Undisconnected events | Memory grows over time | Trove/Maid pattern, disconnect on cleanup |
| Orphaned instances | Memory never freed | Destroy() instances, nil references |
| Large tables never cleared | Lua GC can't collect | Set to nil or use weak tables |
| Excessive cloning | Memory spikes on spawn | Object pooling |
| Uncompressed images | High texture memory | Use compressed formats, reduce resolution |

#### Player/Character objects are NOT auto-destroyed

`PlayerRemoving` and `CharacterRemoving` fire, but the engine does not destroy the Player or Character instances. If you hold attributes, connections, or references on them, that memory stays on the server for the life of the process, a slow leak that grows with every join/leave and eventually crashes long-lived servers.

The pattern: disconnect/destroy each player's resources in those events, and destroy the instance when you are done with it. Defer the destroy (the removal event may still run cleanup) and wrap in `pcall` so cleanup can't error mid-list.

```luau
local Players = game:GetService("Players")

local function destroyDeferred(instance: Instance)
    task.defer(pcall, instance.Destroy, instance)
end

local function onCharacterRemoving(character: Model)
    -- disconnect character-owned connections, clear attributes
    destroyDeferred(character)
end

Players.PlayerAdded:Connect(function(player)
    player.CharacterRemoving:Connect(onCharacterRemoving)
end)

Players.PlayerRemoving:Connect(function(player)
    -- disconnect player-owned connections, clear attributes
    destroyDeferred(player)
    -- player is about to leave; no need to keep the object alive
end)
```

Notes:
- The same leak exists on the client (e.g. Player/character references from LocalScripts); clean up there too.
- `Workspace.PlayerCharacterDestroyBehavior` (default `Disabled`) controls whether the engine destroys characters on removal. Even if set to destroy, don't rely on it for the Player object, and explicit cleanup is harmless.

### Rendering

| Problem | Symptom | Fix |
|---------|---------|-----|
| High part count | Low FPS, draw call bound | Merge static geometry, use MeshParts |
| Transparent part stacking | Overdraw, GPU bound | Reduce layers, use CanvasGroup for UI |
| Excessive particles | Mobile FPS death | Cap ParticleEmitter.Rate, reduce on mobile |
| Too many dynamic lights | Frame time spike | Limit to 4-6 active lights per area |
| Post-processing stacking | GPU overhead | One BloomEffect, one ColorCorrection max |

### Network

| Problem | Symptom | Fix |
|---------|---------|-----|
| Frequent RemoteEvent fires | Bandwidth spike | Batch updates, throttle to 10-20/sec |
| Large payloads | Lag spike on fire | Send IDs not full objects, compress data |
| Replicating unnecessary instances | Join time slow | Keep Workspace lean, use ServerStorage |
| Unthrottled property changes | Network saturation | Batch property changes, use attributes |

### Replay / Delta State Recording

A replay system stores compact per-delta state changes rather than full frames: record only the authoritative fields that change each tick (CFrame, velocity, health, anim), delta/dict-encode against the prior frame, then compress (e.g. ZStd) and chunk the stream for storage. Store an integrity hash (e.g. HMAC-SHA256) so chunks can't be tampered with, and version the protocol so older replays stay decodeable as the format evolves. Reconstruction happens at playback on the client, keeping the stored footprint near the delta+compression size rather than raw per-frame snapshots. [Community lead: "ReplayCore" by lathienvu7, https://devforum.roblox.com/t/replaycore-a-modern-open-source-replay-system-for-roblox/4803450; label as practitioner design and verify specifics before adoption.]

## Optimization Patterns

Code-level micro-optimizations (object pooling, throttled updates,
distance-based relevance filtering, lazy loading) now live in
`roblox-luau-patterns` §10. Apply them only where the profiler shows cost.
The engine-side counterparts stay in this skill: StreamingEnabled tuning and
detect-platform guidance are under Mobile-Specific Optimization below.

## Mobile-Specific Optimization

Optimize for representative low-end mobile devices, not universal object caps:

- **Geometry**: Profile visible parts and triangles; use StreamingEnabled where appropriate.
- **Textures**: Match resolution to on-screen size and inspect texture memory.
- **Particles**: Measure active particle cost and reduce rate/lifetime on constrained devices.
- **UI**: Profile hierarchy and `CanvasGroup` use; CanvasGroup itself has rendering cost.
- **Shadows**: Profile lighting and shadow settings on each target tier.
- **Streaming**: Tune radii in Studio against pop-in, memory, and bandwidth.

### StreamingEnabled

StreamingEnabled is **on by default** for new places. Scoping is container-based: streaming applies exclusively to descendants of `Workspace`. Instances in `ReplicatedStorage`, `ReplicatedFirst`, etc. never stream.

With `ModelStreamingBehavior = Improved` (recommended), a Model streams in only when one of its BasePart descendants is eligible, and the model's non-BasePart descendants (Folders, Scripts, ValueObjects) stream in alongside it. A Model with no BasePart descendants replicates at join and is exempt from streaming out. In Legacy mode (default), non-BasePart descendants replicate at join and only BaseParts stream in/out.

When instances stream out, they are **parented to nil** (not destroyed). Luau references persist if they stream back in. Removal signals fire, but local-only property changes may be lost.

Configuration:
- `StreamingTargetRadius`: maximum target distance; Studio default is 1024 studs.
- `StreamingMinRadius`: highest-priority radius; Studio default is 64 studs.
- `StreamingIntegrityMode`: behavior when a player enters an incompletely streamed region.

These settings are not scriptable. Tune them in Studio from measurements on
representative devices; do not assume a smaller radius is automatically better.

**Gotcha**: `workspace:FindFirstChild("DistantPart")` returns nil if the part is streamed out. Use `WaitForChild` with timeout, or design systems that don't depend on distant parts existing on the client.

### Predictive Streaming (2026-07)

`Workspace.PredictiveStreamingMode` is Studio-only and not scriptable. `Default` currently behaves like `Disabled`; `Enabled` lets the engine prefetch likely destinations for streaming-enabled experiences.

Spawn prefetching creates small temporary streaming foci at possible respawn locations after a player dies. CFrame return optimization keeps the area a player just left streamed in for a likely near-term return. Predictions are additive and temporary, so remeasure memory and bandwidth on representative devices.

### Detect Platform

```luau
local UserInputService = game:GetService("UserInputService")

local isMobile = UserInputService.TouchEnabled
    and not UserInputService.KeyboardEnabled

if isMobile then
    -- StreamingEnabled is set in Studio (ReadOnly from scripts).
    -- Reduce particle counts, disable expensive effects
end
```

## Performance Budget Template

Illustrative allocation for a 60 FPS target. Replace every number with measured
project budgets before enforcing it:

```
SERVER BUDGET (per Heartbeat frame, 16ms total):
  Physics:     4ms
  Scripts:     8ms
  Replication: 2ms
  Overhead:    2ms

CLIENT BUDGET (per render frame, 16ms for 60fps):
  Render:      8ms
  Scripts:     4ms
  Physics:     2ms
  UI:          1ms
  Overhead:    1ms

MEMORY BUDGET:
  Set per tested device tier; watch sustained growth and OS termination.

NETWORK BUDGET:
  Set from measured gameplay traffic and latency; rate-limit per action semantics.
```
