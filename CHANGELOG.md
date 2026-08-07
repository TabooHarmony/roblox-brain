# Changelog

All notable changes to `roblox-brain` are documented here.

## [1.3.0] - 2026-08-07

### Added

- Predictive Streaming guidance, including spawn prefetching and CFrame return optimization.
- Studio-beta instance-reference attributes and streaming-aware `ObjectValue` behavior.
- Ads Manager Open Cloud API guidance with test-stage and credential boundaries.
- Roblox agent documentation indexes for Engine, Open Cloud, full docs, and deprecated APIs.
- Current Recommended-for-You guidance for retention, monetization, and Home impressions.
- Tag-driven composition with `CollectionService`, plus player-route and spawn acceptance in existing architecture and building skills.
- Mesh-backed prop acceptance with `SurfaceAppearance`, collision, provenance, and representative quality-level readback.

### Changed

- Added failure-oriented checks for custom loading, receipt retries, feature-slice review, and large-place readback.
- Added validation for public catalog drift, annotated Luau fences, empty or future-dated metadata, and exact identifier tethers.
- Inventoried the release-driving official sources and added a live check for `Workspace.PredictiveStreamingMode` scriptability.
- Updated GitHub Actions to current Node 24-based runtimes.

## [1.2.1] - 2026-07-29

### Fixed

- Corrected six behavioral claims flagged by community audit in analytics, building, camera, monetization, and performance.

## [1.2.0] - 2026-07-26

### Added

- Added `roblox-growth-design` for evidence-backed discovery, positioning, onboarding, retention, experiments, packaging, and LiveOps diagnosis.
- Added Luau compilation, claim-to-teaching-file tethering, negative validator tests, and exact installed-content comparison to the release contract.

### Changed

- Reworked architecture around feature ownership, explicit dependencies, bounded startup, and client/server authority instead of service/controller hierarchy.
- Rewrote Luau core and patterns to remove generic tutorials, framework defaults, inheritance catalogues, and misleading lifecycle advice.
- Replaced the universal publish checklist with change-scoped, evidence-backed release gates.
- Consolidated Roblox OAuth guidance into `roblox-cloud` and production footguns into their owning domain skills.
- Converted `roblox-code-review` to a thin router and made the README the human-facing catalogue.
- Corrected current analytics, networking, localization, lighting, camera, pathfinding, streaming, monetization, and Server Authority claims.

### Removed

- Removed the generic `roblox-debug` skill. Debugging methodology belongs to the host agent rather than a Roblox-specific knowledge package.
- Removed `roblox-oauth` after its Roblox-specific material moved into `roblox-cloud`.
- Removed `roblox-sharp-edges` after its concrete hazards moved into networking, data, monetization, architecture, performance, and Luau skills.
- Removed the generated `skill_index.md`, its generator, the duplicated code-review reference, and the hidden-loop analytics batcher example.

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
