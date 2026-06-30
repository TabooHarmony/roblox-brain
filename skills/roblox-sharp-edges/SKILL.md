---
name: roblox-sharp-edges
description: >
  13 production footguns ranked by severity. Data loss, exploits, memory leaks, mobile perf.
last_reviewed: 2026-05-22
sources:
  - https://github.com/brockmartin/roblox-game-skill (MIT)
---

## When to Load

When writing or reviewing Roblox Luau code that handles player data, remote events, monetization, or memory management. Consult before shipping to catch the most common production footguns before they cause data loss or exploits. Full details for each edge case are in `references/full.md`.

## Quick Reference

| # | Sev | Problem | Fix |
|---|-----|---------|-----|
| SE-1 | 🔴 | DataStore session conflict on server-hop | Use ProfileStore (session locking) |
| SE-2 | 🔴 | Client sends currency amount | Server-authoritative state only |
| SE-3 | 🔴 | ProcessReceipt returns before grant | Grant → save → return PurchaseGranted |
| SE-4 | 🟠 | Events never disconnected | Trove pattern (RbxUtil) per player |
| SE-5 | 🟠 | RemoteEvent spam from exploiters | Per-player rate limiter on server |
| SE-6 | 🟠 | BindToClose 30s timeout | Parallel saves with task.spawn |
| SE-7 | 🟡 | >10K parts kills mobile FPS | StreamingEnabled + model streaming |
| SE-8 | 🟡 | require() yields/blocks callers | Init/Start lifecycle pattern |
| SE-9 | 🟡 | #table wrong with nil gaps | table.remove, not tbl[i]=nil |
| SE-10 | 🔵 | wait()/spawn()/delay() deprecated | Use task.wait/spawn/delay |
| SE-11 | 🟡 | WaitForChild no timeout → hang | Always pass timeout, handle nil |
| SE-12 | 🔵 | Regex syntax doesn't work in Luau | Lua patterns: %d not \\d, .- not .*? |
| SE-13 | 🟡 | Functions used before declared | Callees above callers (no hoisting) |

**Legend:** 🔴 Critical &nbsp; 🟠 High &nbsp; 🟡 Medium &nbsp; 🔵 Low
