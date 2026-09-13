# Changelog

All notable changes to `roblox-brain` are documented here.

## [1.8.0] - 2026-09-13

### Added

- UI: the styling system (`StyleSheet`, `StyleLink`, `StyleDerive`, `StyleRule`, `StyleQuery`, `$token` usage and the one-sheet-per-tree limit), flex layout with `UIFlexItem` and `UIListLayout.HorizontalFlex`/`VerticalFlex`, and per-corner `UICorner` radii with their beta gate.
- Luau: new type-solver features (`keyof`, `rawkeyof`, `setmetatable<T, M>`, `type function`, `read` members) with the `UseNewLuauTypeSolver` gate, native code generation gates and instruction ceilings, `@deprecated` syntax, the Lua 5.1 sandbox restrictions, the naming conventions, and a deprecated API catalog (`spawn`, `delay`, `Body*` movers, `LoadAnimation`, `tick()`, `SetPrimaryPartCFrame`, `Part.Velocity`).
- Data: right-to-be-forgotten deletion templates and their 30-day windows, `DataStoreGetOptions.UseCache`, `BatchGetAsync` (ordered stores), version history (`ListVersionsAsync`/`GetVersionAsync`/`GetVersionAtTimeAsync`/`RemoveVersionAsync`), per-server and per-experience budget formulas, storage limits, and `Player.User` as the domain-scoped identity value.
- Security: `BanAsync`/`UnbanAsync`/`GetBanHistoryAsync` with their config dictionary, the `BanningEnabled` gate, device-block semantics and their limits, sandboxed capabilities (`Instance.Sandboxed`, `Instance.Capabilities`), and client-triggerable interaction instances (`ProximityPrompt`, `ClickDetector`, `DragDetector`) treated as untrusted input.
- Networking: what does and does not survive a remote call (functions, metatables, mixed tables, `nil` truncation, table copies) and the Server Authority settings bundle with `RunService:SetPredictionMode`.
- Cloud: the experience secrets store (`HttpService:GetSecret`) covering non-printable `Secret` values, prefix/suffix transforms, per-experience secret count and domain allowlists, and the local playtest failure mode.
- Tooling: a verification procedure for API claims that works without launching Studio, using the raw creator-docs markdown suffix and the engine class YAML that the drift registry checks against.

### Changed

- Performance: the claim that compressed image formats reduce texture memory is replaced with the documented guidance (match image resolution to on-screen size, trim sheets, transcoding happens on upload). The light-count and remote-fire-rate figures are now labeled practitioner heuristics instead of engine limits, and the documented MicroProfiler frame-time thresholds are listed.
- Studio MCP: the legacy `set_active_studio` note is reworded to match the current tool set, which routes by `studio_id`.
- Reference infrastructure: API drift registry expanded to 78 entries; the vendor note records the two MIT skill sources reviewed for this pass and the claims rejected from them.

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
