---
name: roblox-testing
description: "Use when writing, running, or fixing Roblox tests: TestService, Jest Lua, Lune, multi-client playtests, CI via Open Cloud."
when_to_use: "Also when a fix keeps coming back, tests pass but the game is broken, adding unit tests to a module, testing remotes or saves, QA before release, running tests from CI or an agent, or a weapon breaks on the second shot."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/reference/engine/classes/TestService
  - https://create.roblox.com/docs/reference/engine/classes/TestCase
  - https://create.roblox.com/docs/reference/engine/classes/StudioTestService
  - https://create.roblox.com/docs/projects/file-based-workflows
  - https://lune-org.github.io/docs/
  - original
---

# Roblox Testing

## When to Load

Making code testable and running tests at each layer. Toolchain and CI wiring: `roblox-tooling`. Studio driving: `roblox-studio-mcp`. Release gates: `roblox-publish-checklist`.

## Quick Reference

### Layers

- **Pure Luau** (Lune, Jest Lua): rules, math, economy, encoders. Fast, runs on every commit.
- **`TestService`**: real engine inside a Studio playtest or Team Test server.
- **Multi-client**: `StudioTestService` or Server & Clients, up to 8 clients.
- **CI**: Open Cloud Luau Execution on a published place version.

### Testable code

Pure modules take values and return values. Inject services, time (`now`), and `Random`. Share one rules module between client and server. Test the contract, not internals.

<!-- temporal: 2026-11 -->
### TestService (official)

- `Enabled` is true only in Play, Play Here, Run, and Team Test. Elsewhere every method throws, so guard with `if not TestService.Enabled then return end`.
- `RegisterSuite(name, {Tags, TimeoutSec})` → `suite:RegisterTest(name, function(test, context) ... end)`. Default timeout 30 s.
- `test:Check(actual, expected, msg?)` continues; `test:Require` stops. Tables compare deeply, NaN never equals, Instances by identity.
- `context:Skip(reason)` skips (fails if a check already failed).
- `RunTestsAsync({Suite, TestId, NamePattern, IncludeTags})` runs one at a time; one run at once.
- Pass only if `result.Status == Enum.TestRunStatus.Pass`; treat `NoTests` as failure in CI.
- `TestId` is opaque: read it, don't build it.

### CI (official)

`POST .../places/{placeId}/luau-execution-session-tasks` (scope `universe.place.luau-execution-session:write`).

- No physics; scripts don't auto-run.
- **DataStores are real**: use a test universe.
- Limits: 5 min runtime, 4 MB script and return.
- Return counts and gate on them.

### What breaks (observed)

- Handler-only tests pass while the real client path is broken: test through the real sender, and walk every server early return.
- Fire each tool 5+ times with reload and swap; log every server rejection.
- Test timers from their last frame, under simulated latency.
- Verify multiplayer claims with two accounts plus a server-side log.

> Runner code, result types, Lune spec, CI task, QA checklist: [references/full.md](references/full.md)
