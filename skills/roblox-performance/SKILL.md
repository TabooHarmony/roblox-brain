---
name: roblox-performance
description: "Use when profiling Roblox performance or diagnosing FPS, memory, network, mobile, or hot-path problems, including MicroProfiler and optimization."
last_reviewed: 2026-07-26
sources:
  - https://create.roblox.com/docs/performance-optimization
  - https://devforum.roblox.com/t/full-release-of-parallel-luau-v1/1836187
  - https://devforum.roblox.com/t/best-uses-of-parallel-luau/3530516
---

# Roblox Performance

## When to Load

Use when profiling, diagnosing lag, optimizing hot paths, or setting performance budgets. Load if the user mentions FPS drops, memory issues, network bandwidth, or mobile optimization.

## Quick Reference

### Profiling Tools
- **MicroProfiler (Ctrl+F6)** — Per-frame breakdown: scripts, physics, rendering. Primary tool for finding what's slow.
- **Developer Console (F9)** — Stats tab: memory, network, render stats. Server Stats for server-side metrics.
- **Script Profiler (Ctrl+Alt+F5)** — Per-script CPU usage and heap allocations.

### Performance Targets
| Metric | Starting target | Investigate at |
|--------|-----------------|----------------|
| Server heartbeat | < 16ms | > 33ms |
| Client FPS (desktop) | 60 | < 30 |
| Client FPS (mobile) | 45 | < 30 |
| Memory | device-specific | sustained growth |

### Optimization Patterns
- **Throttle Heartbeat** — Batch expensive work at fixed intervals (10/sec, not 60)
- **Cache references** — Store workspace lookups in variables, avoid repeated FindFirstChild
- **Relevance filtering** — Skip expensive updates for distant entities; a broad scan is still O(n)
- **Lazy loading** — Stream content from ServerStorage as player approaches

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
- **On by default** for new places. Only BaseParts stream; Folders, ModuleScripts, RemoteEvents load at join.
- **Streamed-out = parented to nil**, not destroyed. Luau refs persist if it streams back.
- **Config (Studio)**: target defaults 1024, min 64; set `StreamingIntegrityMode`; tune from data.
- **Gotcha**: `FindFirstChild("DistantPart")` returns nil if streamed out. Use WaitForChild with timeout.

### Mobile Checks
- Profile geometry, textures, particles, UI, and shadows on representative low-end devices.

**MCP verification:** collect a baseline and inspect runtime counters after changes.
**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
