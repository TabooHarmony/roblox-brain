---
name: roblox-performance
description: "Use when profiling or fixing Roblox performance: low FPS, lag, memory, network load, slow phones, hot paths."
when_to_use: "Also when the game stutters, phones overheat or crash, server heartbeat drops, before adding many parts/effects/UI, and when auditing performance before release."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/en-us/performance-optimization/microprofiler
  - https://create.roblox.com/docs/en-us/reference/engine/libraries/debug
  - https://devforum.roblox.com/t/huge-memory-leak-prevention-for-everyone-or-most-people-atleast/3099605
  - https://devforum.roblox.com/t/full-release-of-parallel-luau-v1/1836187
  - https://luau.org/performance
  - https://create.roblox.com/docs/reference/engine/classes/Actor
  - https://create.roblox.com/docs/reference/engine/datatypes/SharedTable
  - https://create.roblox.com/docs/scripting/multithreading
---

# Roblox Performance

## When to Load

Use for profiling and performance budgets. Pooling and lifecycle patterns: `roblox-luau-patterns`.

## Quick Reference

### Profiling Tools
- **MicroProfiler (Ctrl+F6)**: Frame breakdown of scripts, physics, rendering.
- **Developer Console (F9)**: Memory, network, rendering, and server stats.
- **Script Profiler (Ctrl+Alt+F5)**: Per-script CPU and heap.
- **Labels**: `debug.profilebegin`/`debug.profileend` mark regions; `debug.setmemorycategory` labels memory. Gate instrumentation behind a flag.

### Performance Targets
| Metric | Starting target | Investigate at |
|--------|-----------------|----------------|
| Server heartbeat | < 16ms | > 33ms |
| Client FPS (desktop) | 60 | < 30 |
| Client FPS (mobile) | 45 | < 30 |
| Memory | device-specific | sustained growth |

Optimize measured hot paths, not folklore. Throttle from measurements; re-profile after shipping.

### Parallel Luau
- Use Actors only after profiling identifies isolatable CPU work.
- Workers compute; synchronize before restricted DataModel writes.
- Do not rely on shared module state across Actors. `SendMessage` copies data; SharedTable supports shared state and atomic updates.

### Hot-loop cost model
- Luau optimizes global imports; avoid folklore function hoisting/unrolling. Environment impurity can disable optimizations. Profile allocations as well as CPU; GC cost may occur later.

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
