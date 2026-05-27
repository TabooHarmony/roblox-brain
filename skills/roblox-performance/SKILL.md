---
name: roblox-performance
description: >
  Performance profiling and optimization for Roblox. Server frame time, client FPS,
  memory management, network bandwidth, Luau-specific optimization, asset budgets.
  Use when diagnosing lag, optimizing hot paths, or setting performance budgets.
last_reviewed: 2026-05-27
---

# Roblox Performance

Use this skill when profiling, diagnosing lag, optimizing code, or setting performance budgets.

## Performance Targets

### Server
| Metric | Target | Hard Limit |
|--------|--------|-----------|
| Heartbeat time | < 16ms (60Hz) | < 33ms (30Hz) |
| Script time | < 10ms/frame | < 20ms |
| Memory | < 2GB typical | ~3.5GB available |
| Network out | < 50KB/s per player | — |
| DataStore budget | 60 + (players × 10) req/min | per Get/Set type |

### Client
| Metric | Target | Minimum |
|--------|--------|---------|
| FPS (desktop) | 60 | 30 |
| FPS (mobile) | 45 | 30 |
| Memory (mobile) | < 800MB | < 1.2GB (crash zone) |
| Memory (desktop) | < 1.5GB | < 3GB |
| Load time | < 10s to playable | < 20s |
| Input latency | < 100ms | < 200ms |

## Profiling Tools

### MicroProfiler (Ctrl+F6)
Per-frame breakdown of time spent in scripts, physics, rendering. The primary tool for finding what's actually slow.

- Server: View → MicroProfiler
- Client: Ctrl+Alt+F6 during playtest
- Look for: long bars in "Script" category, physics spikes, render thread stalls

### Developer Console (F9)
- **Stats**: Memory, network, render stats
- **Server Stats** (game owner): Server-side metrics
- **Script Performance**: Per-script CPU time

### Script Profiler (Ctrl+Alt+F5)
- Per-script CPU usage and heap allocations
- Identifies which scripts are hot

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

### Spatial Partitioning

```luau
-- Don't check all entities against all entities
-- Use distance-based activation
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

Mobile is 60%+ of Roblox players. Optimize for it specifically:

- **Part count**: Keep under 5000 visible parts. Use StreamingEnabled.
- **Textures**: Max 512x512 for most textures. 1024 only for hero assets.
- **Particles**: Cap at 50 total active emitters. Reduce Rate on mobile.
- **UI**: Use CanvasGroup to batch UI rendering. Avoid deep nesting.
- **Shadows**: Consider disabling GlobalShadows on mobile or reducing ShadowSoftness.
- **Draw distance**: Reduce via StreamingEnabled MinRadius/TargetRadius.

### StreamingEnabled

StreamingEnabled is **on by default** for new places. Only `BaseParts` and their descendants stream in/out. Other instances (Folders, ValueObjects, RemoteEvents, ModuleScripts) load during initial join and never stream.

When instances stream out, they are **parented to nil** (not destroyed). Luau references persist if they stream back in. Removal signals fire, but local-only property changes may be lost.

Configuration:
- `StreamingTargetRadius` — radius (studs) engine keeps loaded. Start at 256, tune down for mobile.
- `StreamingMinRadius` — guaranteed radius. Set ~64 for nearby content.
- `StreamingPauseMode` — what happens during load (Default, Disabled, ClientPhysicsPause).

**Gotcha**: `workspace:FindFirstChild("DistantPart")` returns nil if the part is streamed out. Use `WaitForChild` with timeout, or design systems that don't depend on distant parts existing on the client.

### Detect Platform

```luau
local UserInputService = game:GetService("UserInputService")

local isMobile = UserInputService.TouchEnabled
    and not UserInputService.KeyboardEnabled

if isMobile then
    -- Reduce quality settings
    workspace.StreamingEnabled = true
    -- Reduce particle counts, disable expensive effects
end
```

## Performance Budget Template

Set these before building, enforce during development:

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
  Mobile:      600MB max (leave headroom for OS)
  Desktop:     1.5GB max

NETWORK BUDGET:
  Per player:  30KB/s average, 100KB/s burst
  RemoteEvents: max 20 fires/sec per remote
```
