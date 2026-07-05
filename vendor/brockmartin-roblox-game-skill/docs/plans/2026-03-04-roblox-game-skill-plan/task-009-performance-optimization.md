# Task 009: Write performance-optimization.md

**depends-on:** 001
**phase:** 2 - Core References
**files:** `references/performance-optimization.md`

## Description

Write a comprehensive performance optimization reference covering part count, script optimization, memory management, network optimization, and mobile-specific concerns.

## What To Do

1. **Overview** — When to load (game runs slowly, mobile optimization, performance audit)
2. **Performance Targets** — Frame rate targets (60fps desktop, 30fps mobile), memory budgets, network bandwidth limits
3. **Part Count Optimization** — Max 500 parts per model, scene limits (~10,000), unions for reducing count, MeshParts vs regular parts, StreamingEnabled for large maps
4. **Script Optimization** — Avoid RunService.Heartbeat abuse (consolidate to one), use task.wait() not wait(), cache GetService calls, avoid repeated Instance:FindFirstChild in loops, table pre-allocation
5. **Memory Management** — Disconnect events when done (connection:Disconnect()), destroy instances properly, avoid reference cycles, Instance.Destroying for cleanup, debris service for timed cleanup
6. **Network Optimization** — Minimize RemoteEvent data size, batch related remotes, use UnreliableRemoteEvent for non-critical updates (positions), compression for large data
7. **Rendering Optimization** — Level of Detail (LOD), draw distance, particle count limits, beam/trail limits, texture resolution
8. **Mobile-Specific** — Lower part counts, simplified effects, touch-optimized UI, reduced draw distance, memory-efficient assets, testing on low-end devices
9. **Profiling Tools** — MicroProfiler usage (Ctrl+F6), F9 Developer Console, Stats service, memory usage tracking
10. **Best Practices** — Profile before optimizing, optimize hot paths first, use spatial queries over brute force, pool reusable objects
11. **Anti-Patterns** — Premature optimization, creating instances in Heartbeat, large uncompressed data over network, not testing on mobile

## Verification

- File exists at `references/performance-optimization.md`
- Concrete numbers for limits (part counts, frame rates, memory)
- MicroProfiler usage documented
- Mobile optimization section included
- At least 5 specific optimization techniques with Luau code
