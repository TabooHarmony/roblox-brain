---
name: roblox-debugging
description: "Use when a Roblox bug needs finding: reproduce, isolate client or server, read logs, use the debugger and profilers, verify the fix."
when_to_use: "Also when something is broken, errors, stops working, lags, works in Studio but not live, works solo but not with friends, a fix didn't stick, or the agent must prove a bug is really fixed."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/studio/debugging
  - https://create.roblox.com/docs/studio/output
  - https://create.roblox.com/docs/studio/developer-console
  - https://create.roblox.com/docs/studio/optimization/scriptprofiler
  - https://create.roblox.com/docs/performance-optimization/microprofiler
  - https://create.roblox.com/docs/studio/network-simulator
  - https://create.roblox.com/docs/reference/engine/classes/Logger
  - https://create.roblox.com/docs/reference/engine/classes/LogService
  - https://create.roblox.com/docs/cloud/guides/error-reporting
  - original
---

# Roblox Debugging

## When to Load

Any bug hunt: wrong behavior, errors, lag, "works in Studio but not live". Studio MCP mechanics: `roblox-studio-mcp`; shared-machine rules: `roblox-collaboration-mode`; performance work: `roblox-performance`; Luau errors: `roblox-luau-core`.

## Quick Reference

1. **Confirm the build and place.** Right Studio window, place and version, fresh code (not a stale require cache or old publish).
2. **Reproduce** with exact steps, device, player count and state. No repro, no fix: add logging and wait.
3. **Read before running.** Read the code path and list candidate causes; feel bugs are usually found by reading.
4. **Isolate** client vs server, one player vs several, Studio vs live, fresh vs real player state.
5. **Observe:** Output, Developer Console (F9), `LogService:GetLogger` structured logs, breakpoints and logpoints (with Client/Server context), Watch and Call Stack.
6. **Measure lag** with the Script Profiler, MicroProfiler and Network Simulator; never guess.
7. **Smallest test:** call the function live with a stand-in target instead of playing a match.
8. **Fix one cause,** then verify by looking, on the real client path, and with two clients for anything shared.
9. **Live errors:** Error Report in the Creator Dashboard and the Error Reporting Open Cloud API.
10. **Report honestly:** what was verified, how, and what wasn't.

> Method, tools, field pitfalls, code: [references/full.md](references/full.md)
