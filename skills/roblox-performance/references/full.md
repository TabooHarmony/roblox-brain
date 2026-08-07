# Roblox Performance — Full Reference


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

## Static Place Triage

When starting from a static `.rbxl` or `.rbxm`, use structure to choose runtime specimens rather than declaring the place fast or slow:

1. Partition the inspection by map root, zone, or runtime container. Record instance counts and bounds for each scope.
2. Flag `MeshPart`, `UnionOperation`, and `SurfaceAppearance` for asset, material, collision, and device-quality review.
3. Flag `ParticleEmitter`, `Beam`, `Trail`, `Highlight`, lights, and post-processing for visual-density and overdraw review.
4. Flag high-frequency scripts, remotes, and large replicated containers for server, network, and join-time review.
5. Confirm the suspected cost with Scene Analysis, the Developer Console, MicroProfiler, and a representative low-end device.

The static patterns that motivate this triage are presence signals only. A class count is not a frame-time, memory, or quality benchmark, and absence from a parsed artifact does not prove that runtime code or external tooling is absent.

### Triage order from shipped-game patterns

<!-- temporal: 2026-08 -->

In shipped Roblox games, effects, input, UI motion, and persistence routinely sit in the same feature, so cross-surface specimens are more useful than isolated class totals. Choose a bounded specimen along one of the paths the game actually exercises:

- **effect path:** emitter or beam creation → owner/lifetime → cleanup → device measurement;
- **interaction path:** input/action → UI or world feedback → remote or simulation request → confirmed state;
- **persistence path:** remote or purchase request → server authority → DataStore mutation → retry/shutdown behavior.

This is a prioritization heuristic for profiling and review, not proof that any one implementation is good or bad.

## Optimization Patterns

### Object Pooling

```luau
local Pool = {}
Pool.__index = Pool

function Pool.new(template: Instance, initialSize: number)
    local self = setmetatable({
        _template = template,
        _available = {},
        _active = {},
    }, Pool)

    for i = 1, initialSize do
        local obj = template:Clone()
        obj.Parent = nil
        table.insert(self._available, obj)
    end
    return self
end

function Pool:get(): Instance
    local obj = table.remove(self._available)
    if not obj then
        obj = self._template:Clone()
    end
    self._active[obj] = true
    return obj
end

function Pool:release(obj: Instance)
    self._active[obj] = nil
    obj.Parent = nil
    -- Reset state here
    table.insert(self._available, obj)
end
```

### Throttled Updates

```luau
-- Instead of updating every frame, batch at fixed intervals
local TICK_RATE = 1/10 -- 10 updates per second
local accumulated = 0

RunService.Heartbeat:Connect(function(dt)
    accumulated += dt
    if accumulated < TICK_RATE then return end
    accumulated -= TICK_RATE

    -- Do expensive work here (runs 10x/sec, not 60x)
    updateAllNPCs()
end)
```

### Distance-Based Relevance Filtering

```luau
-- This reduces expensive updates after discovery; the scan itself remains O(n).
local ACTIVATION_RANGE = 100

local function getActiveEntities(playerPosition: Vector3): {Instance}
    local active = {}
    for _, entity in allEntities do
        if (entity.Position - playerPosition).Magnitude < ACTIVATION_RANGE then
            table.insert(active, entity)
        end
    end
    return active
end
```

For large populations or frequent queries, use a real spatial index such as a
grid or spatial hash. Choose its cell size from the query radius and movement
pattern; this linear filter is not spatial partitioning.

### Lazy Loading

```luau
-- Don't load everything at once
-- Stream content as player approaches
local loaded = {}

local function ensureLoaded(zoneName: string)
    if loaded[zoneName] then return end
    loaded[zoneName] = true

    local zone = ServerStorage.Zones:FindFirstChild(zoneName)
    if zone then
        zone:Clone().Parent = workspace.ActiveZones
    end
end
```

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
- `StreamingTargetRadius` — maximum target distance; Studio default is 1024 studs.
- `StreamingMinRadius` — highest-priority radius; Studio default is 64 studs.
- `StreamingIntegrityMode` — behavior when a player enters an incompletely streamed region.

These settings are not scriptable. Tune them in Studio from measurements on
representative devices; do not assume a smaller radius is automatically better.

**Gotcha**: `workspace:FindFirstChild("DistantPart")` returns nil if the part is streamed out. Use `WaitForChild` with timeout, or design systems that don't depend on distant parts existing on the client.

### Predictive Streaming

<!-- temporal: 2026-08 -->

`Workspace.PredictiveStreamingMode` (Studio-only, not scriptable) opts streaming-enabled games into proactive loading, launched 2026-07: the engine anticipates player movement and streams in areas before arrival, reducing pause-and-pop-in. `Default` currently behaves the same as `Disabled`.

Initial features: spawn prefetching (temporary streaming foci at likely respawn locations on death) and CFrame return optimization (a temporary focus where a player CFrame-teleported away, covering enter/leave loops between hubs, buildings, and sublevels). Predictions are additive and expire; the engine skips them on resource-constrained devices.

Do not re-implement what the engine predicts for you; use `Player:RequestStreamAroundAsync()` or `Player:AddReplicationFocus()` when you need deterministic control, e.g. teleporting to a specific region.

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
