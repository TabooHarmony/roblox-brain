# Changelog

All notable changes to `roblox-brain` are documented here.

## [2.0.0] - Unreleased

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
- Growth design now covers launch ads, thumbnail tests, and reading organic traffic and retention after launch.
- Architecture now asks agents to trace a feature from input through UI and remotes to saved state, rather than assuming that matching folder names mean the feature works.
- Performance now distinguishes documented engine limits from rules of thumb and corrects the texture-memory advice.
- Studio MCP guidance now routes calls to a specific Studio instance with `studio_id`.

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
