---
name: roblox-performance
description: "Use when profiling Roblox performance or diagnosing FPS, memory, network, mobile, or hot-path problems, including MicroProfiler and optimization."
last_reviewed: 2026-05-27
sources:
  - https://create.roblox.com/docs/performance-optimization
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
| Metric | Target | Hard Limit |
|--------|--------|------------|
| Server heartbeat | < 16ms | < 33ms |
| Client FPS (desktop) | 60 | 30 |
| Client FPS (mobile) | 45 | 30 |
| Memory (mobile) | < 800MB | < 1.2GB |

### Optimization Patterns
- **Throttle Heartbeat** — Batch expensive work at fixed intervals (10/sec, not 60)
- **Cache references** — Store workspace lookups in variables, avoid repeated FindFirstChild
- **Spatial partitioning** — Distance-based activation instead of checking all entities
- **Lazy loading** — Stream content from ServerStorage as player approaches

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
- **Config**: `StreamingTargetRadius` (start 256, tune down for mobile), `StreamingMinRadius` (~64).
- **Gotcha**: `FindFirstChild("DistantPart")` returns nil if streamed out. Use WaitForChild with timeout.

### Mobile Quick Wins
- Keep < 5000 visible parts. Textures max 512x512. Cap particles at 50 emitters.
- Use CanvasGroup for UI batching. Consider disabling GlobalShadows.
**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
