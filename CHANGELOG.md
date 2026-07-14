# Changelog

All notable changes to `roblox-brain` are documented here.

## [1.1.0] - 2026-07-14

### Changed

- Removed the generic `roblox-economy` skill. Its Roblox-specific material is already covered by monetization, analytics, networking, and security.
- Refreshed Server Authority guidance across security, networking, physics, NPC AI, animation/VFX, input, and UI references.

## [1.0.0] - 2026-07-13

Initial public release of the Roblox Studio skill library.

### Added

- 31 focused skills covering Luau, architecture, networking, data, UI, physics, animation, audio, lighting, cloud, tooling, localization, debugging, and publishing.
- `roblox-ui-design` for simulator-style defaults, existing-style inheritance, visual hierarchy, composition, density, and bounded layouts.
- Progressive disclosure through compact `SKILL.md` files and deeper `references/full.md` references.
- Roblox Studio MCP guidance for scripting, scene inspection, generated assets, runtime checks, and evidence-based workflows.
- Current guidance for UnreliableRemoteEvent, packet budgets, ProfileStore, MemoryStore queues, gamepad focus, Parallel Luau, pathfinding performance, and Creator Rewards.

### Improved

- Server-authoritative networking, validation, rate limits, and NaN or infinity handling.
- Data persistence guidance for session ownership, migrations, failed saves, and profile lifecycle.
- Cross-platform UI guidance for safe areas, responsive layouts, gamepad navigation, and accessibility.
- Monetization guidance for Passes, Developer Products, receipts, subscriptions, policy checks, and Creator Rewards.
- Tooling guidance for Rojo, Wally, Selene, StyLua, Lune, optional RbxUtil modules, and archived-tool caveats.

### Quality and provenance

- Added skill structure validation, regression tests, API drift checks, source URL checks, and version pin checks.
- Added package installation checks for the published skill set.
- Re-authored overlapping material independently and removed the unlicensed upstream snapshot.
- Kept source URLs and temporal platform claims visible for future maintenance.

### Scope

This release is a practical starting point for Roblox Studio work, not a complete reference for every Roblox API or game genre. Platform behavior and policy can change, so current Creator Hub documentation remains authoritative.
