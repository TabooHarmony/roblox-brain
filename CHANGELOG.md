# Changelog

All notable changes to `roblox-brain` are documented here.

## [Unreleased]

### Added

- Pass free trials, live December 2, 2026. Starting a trial fires `PromptGamePassPurchaseFinished` with success, and `UserOwnsGamePassAsync` returns `true` while the trial lasts. Permanent rewards must check `GetPassOwnershipAsync().Owned`, and pass benefits must come from a live ownership check rather than a cached or saved one.
- The `roblox-studio-mcp` skill now verifies private UI on both clients of a two-client test (thanks to Deworix, #6).

### Fixed

- `roblox-cloud` taught the deprecated reserved-server flow (`ShouldReserveServer`, `ReservedServerAccessCode`, `ReserveServerAsync`). It now uses a server-generated GUID in `TeleportOptions.ReservedServerId`, covers `VipServerId` and migration, and explains that `TeleportAsync` can now be tested in Studio Test and Team Test, with the differences from production listed.
- `roblox-growth-design` gave old Kids and Select numbers. The evaluation threshold is now 100 highly engaged players (it was 500, then 250), and the expedited review fee is 50,000 R$ (it was 100,000). The 2-month Plus or Premium subscription alternative to the publishing fee is now mentioned.
- `roblox-performance` claimed `PlayerCharacterDestroyBehavior` defaults to `Disabled` and that it never destroys the `Player` object. Both claims were unsourced. `Enabled` destroys both old characters and departed `Player` objects, and `Default` follows the engine default, which can change.
- The docs replaced the `NotScriptable` tag on streaming settings and `SoundService.DefaultListenerLocation` with the `PluginOrOpenCloud` capability. The skills now say these can be set from Studio, plugins, or Open Cloud Luau execution, but not by game scripts. The drift checker has a new `property_has_capability` check for this.
- The validator could crash a reader thread on Windows while decoding `luau-compile` output, and two tests read skill files with the system encoding. Both now use UTF-8.
- Replaced the dead pesde manifest source URL; pesde's docs moved out of its repo.

## [2.3.1] - 2026-10-14

### Fixed

- The architecture field notes gave the wrong limit for `NumberValue`. The 9.22e18 ceiling belongs to `IntValue`, which holds a signed 64-bit integer. `NumberValue` holds a double: magnitude up to about 1.79e308, but whole numbers are stored exactly only to 2^53, about 9 quadrillion. Both engine definitions are linked.
- The mirror snapshot regression tests wrote their fixtures in text mode and hashed a fixed LF byte string, so the suite reported a false identity mismatch on Windows. Fixtures now write the same bytes they hash, and the tests pass on every platform.

## [2.3.0] - 2026-10-14

### Added

- Mobile-first GUI guidance: design order from the smallest landscape phone, the screen regions Roblox UI already occupies, safe-area containers, measured placement, overlaps caused by state combinations, reflowing small-screen windows, console and TV rules, and a device matrix for the Simulator and Controller Emulator.
- Cross-device input guidance: gamepad focus ownership (entry focus, selection boundaries, focus after list rebuilds, layered Back, restoring focus on close), hybrid presentation from `PreferredInput`, touch action buttons, a single gameplay input gate, cancelling held actions, gamepad tool activation, platform button hints, and a cross-device test checklist.
- First-session onboarding traces alongside analytics funnels, with bounded collection, save ownership, privacy, retention, and offline analysis guidance.
- Monetization guidance for subscriptions, Robux transfer receipts, dynamic prices, and price-aware gifting, plus centralized Game Pass benefits and purchase refresh handling.
- Reuse-first integration guidance for proven project modules.
- Feature-level threat modeling, and Luau pitfalls around literal search, Unicode, binary strings, and repeat loops.
- Remote transport and bindable boundaries, cross-server receive limits, and shared MemoryStore quota planning.
- Text entry, grid layout, truncation, RichText safety, and legacy GUI API migration guidance.
- Editor-safe source changes, undo recordings, Script Sync conflict handling, untrusted place-content boundaries, and asset-permission diagnosis.
- Lessons from a full build, launch, and live-ops cycle of a round-based game, across the collaboration, Studio MCP, publishing, tooling, and analytics skills.

### Changed

- Every skill's description now triggers on changing, fixing, debugging, reviewing, and auditing, not only on building, and each skill gains a `when_to_use` line of symptom phrases ("data not saving", "UI overlaps on mobile", "controller stuck in a menu"). `validate_skills.py` accepts the optional field, and AGENTS.md documents the convention.
- Removed individual community attributions and community-sourced field notes from `roblox-architecture`, `roblox-tooling`, and `roblox-growth-design`; the underlying guidance stays as field-reported synthesis, without named contributors.

### Fixed

- `roblox-input`: `PreferredInput` is typed `Enum.PreferredInput`, not `Enum.UserInputType`, and the example now observes `PreferredInput`.

## [2.2.0] - 2026-10-02

### Added

- Expanded Luau guidance on metatable behavior, coroutine lifecycles, failure handling, buffer layouts, and type refinements, with worked examples.
- Added profiling and Parallel Luau guidance on allocation costs, Actor messaging, SharedTable updates, and snapshot ownership.
- Expanded networking guidance with latency-aware hit validation, shared clocks, bandwidth budgeting, and typed schema workflows.
- Added reactive UI lifecycle and cleanup guidance, plus ECS adoption, system ordering, query pitfalls, and replication identity mapping.
- Added teleport handoff and recovery workflows, scheduled restart handling, durable acknowledgements, and cross-server retry and paging patterns.
- Added audience-specific text filtering and AnimationTrack blending, playback, and cleanup guidance.
- Expanded testing and package workflows, including runtime limits, CI result checks, version ranges, realm conflicts, and publish previews.
- Added Rojo syncback, pesde/Wally interoperability, and modern raycast filtering guidance.

### Changed

- Tooling guidance distinguishes Wally CLI release age from registry activity, uses the project's existing manager or Rokit, and updates the example Rojo and Selene pins.
- Removed an unsupported ECS project-status claim and corrected pesde attribution.

### Fixed

- Corrected mobile sensor callback signatures, gravity and rotation examples, and the mouse sensitivity range.
- Replaced invalid movement enum items with explicit keyboard, digital gamepad, and touch bindings.
- Corrected GUI respawn persistence guidance and documented inset-adjusted hover hit-testing, with live Studio verification still required.
- Corrected LineForce attachment roles and the condition under which its force cap applies.
- Corrected `vector.lerp` availability and removed the blanket claim that passing a table to a function seals it.

## [2.1.0] - 2026-09-25

### Added

- `roblox-animation-vfx` now covers effect composition, impact timing, flipbook textures, mesh and UI-based effects, and checking readability and performance in play.

### Changed

- Refined the design skills for a cleaner, more direct read.

### Fixed

- The README release badge now shows the latest release instead of sticking at v1.7.0.

## [2.0.0] - 2026-09-24

### Added

- `roblox-game-design`: core loops, tutorials, level pacing, economies, game feel, and making repetitive play satisfying. Includes guidance for Roblox's Today's Picks and Moments.
- `roblox-player-psychology`: first-session behavior, rewards, streaks, pricing, RNG and pity systems, and community-building.
- GUI: styling with `StyleSheet`/`StyleLink` and `StyleQuery`, plus flex layouts using `UIListLayout` and `UIFlexItem`.
- Luau: new type-solver features including `keyof`, `type function`, and `read` members; native code generation limits; and guidance on deprecated APIs such as `spawn`, `tick()`, and legacy body movers.
- Data: account-deletion templates, version history, data-store budgets, and `Player.User` identity guidance.
- Security: bans, sandboxed scripts, and server checks for interactions triggered through prompts, clicks, and dragging.
- Networking: what survives a remote call and how to configure Server Authority.
- Cloud: use experience secrets with `HttpService:GetSecret` rather than putting keys in scripts.

### Changed

- Skills are grouped into four installable libraries: `core` (10), `gameplay` (10), `design` (5), and `tools` (4). Installing the repository still installs all 29. Paths to individual skill folders have changed.
- `roblox-gui` takes over practical styling, layout, and visual checks from `roblox-ui-design`, without prescribing a visual style.
- Building now covers finding and inspecting Toolbox assets before making a replacement from scratch.
- Building also covers Studio Assistant's texture restyling, imported-mesh segmentation, and image previews, without treating those editor actions as MCP tools.
- Growth design now covers launch ads, thumbnail tests, and reading organic traffic and retention after launch.
- Architecture now asks agents to trace a feature from input through UI and remotes to saved state, rather than assuming that matching folder names mean the feature works.
- Performance now distinguishes documented engine limits from rules of thumb and corrects the texture-memory advice.
- Studio MCP guidance now routes calls to a specific Studio instance with `studio_id`.
- Repository checks and the API drift registry now live in `scripts/`; contributor commands and CI use the new paths.

### Removed

- `roblox-code-review` as a standalone router skill. Use the domain skill relevant to the change instead.
- `roblox-ui-design` as a standalone skill. The practical GUI guidance remains in `roblox-gui`, but its full visual-design reference was not carried over.

### Fixed

- Lighting guidance now reflects current Creator Hub metadata: `LightingStyle` and `PrioritizeLightingQuality` are script-writable; deprecated `Technology` is not.
- Analytics now reflects the documented limit of 10 economy resource types, not 5.
- Monetization now recognizes `BindReceiptHandler` with `Enum.ReceiptType.DeveloperProduct` as a Developer Product receipt path alongside `ProcessReceipt`. Both still require a durable, idempotent grant before acknowledging a purchase.
- Tooling no longer suggests archived TestEZ in the example package manifest; existing projects can keep using it.

## [1.7.0] - 2026-09-06

### Added

- Coverage for 23 previously undocumented foundational classes: `EncodingService` and the Math library (luau-core), `EditableImage`/`EditableMesh` procedural geometry and painting (building), `DragDetector`/`UIDragDetector` (input), `TextChatService` routing (networking), `TeleportService` and `BadgeService` with `AwardBadgeAsync` deprecation status (cloud), `UIPageLayout`, `SelectionBox`, `Decal`, and `VideoPlayer` (gui), `HumanoidDescription`, `BodyColors`, `Shirt`, and `Pants` (npc-ai), `LineForce` and `IKControl` (physics), the `ValueBase` family (luau-patterns), `PhysicsService` collision groups, `ProximityPrompt`/`ProximityPromptService`, and `VRService` (physics/interaction).
- New design contracts in the architecture and Studio MCP references: cross-owner durability limits and recovery contracts, per-call mutation records with destination preflight, and a regression/negative-control test suite.
- Luau: `const` keyword documentation (Luau 0.711) replacing the stale "const is not Luau syntax" note.
- Tooling: TS/ECS/package-manager reality checks with receipts (rbxts static at 3.0.0 since 2023, dialect-vs-vanilla caveat, Script Sync release status, Fusion vendor stance); ECS architecture section.

### Changed

- Reference infrastructure hardened: API drift registry expanded to 61 entries pinning new claims; mirror snapshots now verified by SHA-256 against cached bytes before their retrieval dates are trusted.
- Test suite isolation: mirror/drift tests no longer touch the real developer cache or network; `validate_skills.py` no longer silently drops structural validator errors.
- Data skills de-overlapped: `roblox-data` / `roblox-server-data` / `roblox-cloud` boundaries cross-linked; micro-optimizations moved from performance to `roblox-luau-patterns`.
- Studio MCP: official bridge synced to per-call `studio_id` routing.
- Security: Server Authority migration reality check (cheap for stock characters, rewrite-scale for authored simulation).

### Fixed

- Data persistence: migrations now run before the schema version is stamped; `addCoins` reports cancellation honestly via tagged failure outcomes; deep-copied templates so nested defaults are not shared between profiles; acquisition deadlines enforced; committed balance logged, not pending.
- Physics: homing steering no longer squares speed on degenerate vectors; antiparallel rotation clamped.
- Camera: cutscene snapshot restores the correct humanoid when the character changed mid-cutscene; shake rebase strips stale offsets only while the camera still holds our last written CFrame.
- GUI/monetization: purchase timeout retains the request ID so a correlated response can still resolve (no unsafe retry); spinner stops and buying stays blocked while unresolved.
- Lifecycle: pool lease validation rejects unowned objects; owned ragdoll cleanup and state restoration; effect cancellation replaced correctly.
- Server data: queue drain honors the processor's explicit `false` return, not just the `pcall` boolean.
- Validators and tests: error aggregation no longer silently drops structural failures; interrupted-fetch tests restore monkeypatched state; mirror metadata stamping and hash verification corrected.

## [1.6.0] - 2026-08-22

### Added

- New skill: `roblox-collaboration-mode` (skill count now 29). Sets initiative level before any Roblox task: when to act, when to warn, which decisions need the user. Description tuned so hosts discover it on autonomous build requests.