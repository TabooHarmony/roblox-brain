---
name: roblox-performance
description: "Use when profiling Roblox performance or diagnosing FPS, memory, network, mobile, or hot-path problems."
last_reviewed: 2026-09-19
sources:
  - https://create.roblox.com/docs/en-us/performance-optimization/microprofiler
  - https://create.roblox.com/docs/en-us/reference/engine/libraries/debug
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
- **Script Profiler (Ctrl+Alt+F5)**: Per-script CPU and heap.
- **Custom labels**: `debug.profilebegin`/`debug.profileend` name hot regions in the MicroProfiler; `debug.setmemorycategory` names thread memory in the console. Gate behind a flag (full.md).

### Performance Targets
| Metric | Starting target | Investigate at |
|--------|-----------------|----------------|
| Server heartbeat | < 16ms | > 33ms |
| Client FPS (desktop) | 60 | < 30 |
| Client FPS (mobile) | 45 | < 30 |
| Memory | device-specific | sustained growth |

"Expensive" means the profiler shows it on a hot frame path (raycasts, clones, large finds, replication-heavy writes). Throttle from measurements, not a universal number; re-profile after shipping. Micro-optimizations live in `roblox-luau-patterns`.

### Parallel Luau
- Use Actors only after profiling identifies isolatable CPU work.
- Workers compute; synchronize before restricted DataModel writes.
- SharedTable and mutexes add coordination cost; they do not replace ownership boundaries.

### Object Pooling
Pre-clone and reuse. Canonical pool code (token-lease ownership): `roblox-luau-patterns`.

### StreamingEnabled Essentials
- **On by default**. Container-scoped: only Workspace descendants stream. `ModelStreamingBehavior = Improved` streams non-BasePart descendants with their parent Model; Legacy streams only BaseParts.
- **Streamed-out = parented to nil**, not destroyed. Luau refs persist if it streams back.
- **Config (Studio)**: target defaults 1024, min 64; set `StreamingIntegrityMode`; tune from data.
- **Gotcha**: `FindFirstChild("DistantPart")` returns nil if streamed out. Use WaitForChild with timeout.

### Mobile
- Profile geometry, textures, particles, UI, shadows on low-end devices.

> Full reference with code examples and API tables: [references/full.md](references/full.md)
