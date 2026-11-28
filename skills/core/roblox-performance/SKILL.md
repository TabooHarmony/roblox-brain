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
  - https://create.roblox.com/docs/workspace/streaming/frustum
  - https://create.roblox.com/docs/workspace/streaming/slim
  - https://create.roblox.com/docs/scripting/transparent-batching
  - https://create.roblox.com/docs/performance-optimization/improve
  - original
---

# Roblox Performance

## When to Load

Use for profiling and performance budgets. Pooling and lifecycle: `roblox-luau-patterns`.

## Quick Reference

### Profiling Tools
- MicroProfiler (Ctrl+F6), Developer Console (F9), Script Profiler (Ctrl+Alt+F5).
- `debug.profilebegin`/`debug.profileend` labels; `debug.setmemorycategory`. Gate behind a flag.

### Targets
Server heartbeat < 16ms (investigate > 33ms); client 60 FPS desktop, 45 mobile (investigate < 30); no sustained memory growth.

### Measure right
- Studio caps an unfocused playtest client near 15 FPS; solo mixes server and client; the Studio server can tick ~20 Hz. Profile a local server + 1 client and compare per-action CPU.
- Cap per-frame work by `os.clock()` time, not count. Build Parts in an unparented Folder, parent once.
- Draw calls follow unique meshes/materials; identical meshes instance. Measure before converting Parts to MeshParts.

### Parallel Luau and hot loops
- Actors only for profiled, isolatable CPU work; synchronize before DataModel writes. `SendMessage` copies; SharedTable shares with atomics.
- Luau optimizes global imports; skip folklore hoisting. Profile allocations too; GC cost lands later.

### StreamingEnabled Essentials
- **On by default**. Container-scoped: only Workspace descendants stream. `ModelStreamingBehavior = Improved` streams non-BasePart descendants with their parent Model; Legacy streams only BaseParts.
- **Streamed-out = parented to nil**, not destroyed. Luau refs persist if it streams back.
- **Config (Studio)**: target 1024, min 64; set `StreamingIntegrityMode`.
- **Gotcha**: `FindFirstChild("DistantPart")` returns nil if streamed out. Remote instance refs can arrive nil: send ids.
- New: `Player.FrustumStreaming` (server-only), SLIM `Model.LevelOfDetail`, `DataModel.ServerLowMemoryWarning`.

> Full reference with code examples and API tables: [references/full.md](references/full.md)
