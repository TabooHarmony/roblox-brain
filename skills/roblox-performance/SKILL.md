---
name: roblox-performance
description: "Use when profiling Roblox performance or diagnosing FPS, memory, network, mobile, or hot-path problems."
last_reviewed: 2026-08-21
sources:
  - https://create.roblox.com/docs/performance-optimization
  - https://devforum.roblox.com/t/huge-memory-leak-prevention-for-everyone-or-most-people-atleast/3099605
  - https://devforum.roblox.com/t/full-release-of-parallel-luau-v1/1836187
---

# Roblox Performance

## When to Load

Use when profiling, diagnosing lag, or setting performance budgets. For code-level micro-optimizations (pooling, throttling, relevance filtering, lazy loading) load `roblox-luau-patterns`; this skill measures and tunes the engine.

## Quick Reference

### Profiling Tools
- **MicroProfiler (Ctrl+F6)**: Per-frame breakdown: scripts, physics, rendering. Primary tool for finding what's slow.
- **Developer Console (F9)**: Stats tab: memory, network, render stats. Server Stats for server-side metrics.
- **Script Profiler (Ctrl+Alt+F5)**: Per-script CPU usage and heap allocations.

### Performance Targets
| Metric | Starting target | Investigate at |
|--------|-----------------|----------------|
| Server heartbeat | < 16ms | > 33ms |
| Client FPS (desktop) | 60 | < 30 |
| Client FPS (mobile) | 45 | < 30 |
| Memory | device-specific | sustained growth |

"Expensive" means the profiler shows it on a hot frame path (raycasts, clones, large finds, replication-heavy writes). Throttle by judgment from measurements, not a universal number, and re-measure after shipping: profile before and after on representative devices and confirm the targeted metric moved without regressions. Micro-optimizations live in `roblox-luau-patterns`.

### Parallel Luau
- Use Actors only after profiling identifies isolatable CPU work.
- Workers compute; synchronize before restricted DataModel writes.
- SharedTable and mutexes add coordination cost; they do not replace ownership boundaries.

### Object Pooling
```luau
-- Core pattern: pre-clone, reuse, avoid GC pressure
local Pool = {}
function Pool:get(): Instance
    return table.remove(self._available) or self._template:Clone()
end
function Pool:release(obj: Instance)
    obj.Parent = nil
    table.insert(self._available, obj)
end
```

### StreamingEnabled Essentials
- **On by default**. Container-scoped: only Workspace descendants stream. `ModelStreamingBehavior = Improved` streams non-BasePart descendants with their parent Model; Legacy streams only BaseParts.
- **Streamed-out = parented to nil**, not destroyed. Luau refs persist if it streams back.
- **Config (Studio)**: target defaults 1024, min 64; set `StreamingIntegrityMode`; tune from data.
- **Gotcha**: `FindFirstChild("DistantPart")` returns nil if streamed out. Use WaitForChild with timeout.

### Mobile
- Profile geometry, textures, particles, UI, and shadows on low-end devices.

> Full reference with code examples and API tables: [references/full.md](references/full.md)
