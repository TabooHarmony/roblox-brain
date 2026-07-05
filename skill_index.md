# Skill Index

Compact index of all roblox-brain skills (~2,800 tokens). Load this at startup to know what's available, then load specific skills as needed.

## Core Language & Architecture

| Skill | Description |
|-------|-------------|
| `roblox-luau-core` | Luau language fundamentals: syntax, tables, control flow, string patterns, math, idioms, scope, closures, sharp edges, and JS-to-Luau translation. |
| `roblox-luau-types` | Luau type system: annotations, generics, narrowing, inference philosophy, sealed/unsealed tables, exports, and Roblox-aware typing. |
| `roblox-luau-patterns` | OOP with metatables, inheritance, async (Promises, pcall), module structure, service pattern. |
| `roblox-architecture` | Service hierarchy, 7 foundational patterns, cross-platform input. Client-server architecture, module patterns, framework options. |
| `roblox-sharp-edges` | 13 production footguns ranked by severity. Data loss, exploits, memory leaks, mobile perf. |

## Economy & Monetization

| Skill | Description |
|-------|-------------|
| `roblox-economy` | Currency design, faucets/sinks, inflation control, time-to-earn, trading systems. |
| `roblox-monetization` | ProcessReceipt correctness, prompt APIs, purchase reconciliation, session-lock interaction. |

## Systems & Networking

| Skill | Description |
|-------|-------------|
| `roblox-networking` | Server-authoritative networking, RemoteEvent validation, rate limiting, exploit prevention, security hardening. |
| `roblox-security` | Anti-exploit design, server authority, RemoteEvent validation, rate limiting, audit checklist. |
| `roblox-data` | DataStores, ProfileStore, session locking, data persistence patterns. |
| `roblox-server-data` | OrderedDataStore, MessagingService, GlobalDataStore, cross-server state, persistent world data. |
| `roblox-analytics` | Roblox AnalyticsService: custom events, economy tracking, funnels, rate limits, event taxonomy. |
| `roblox-npc-ai` | Pathfinding, state machines, NPC detection (LOS/FOV), spawn systems, enemy AI patterns. |

## Performance & Runtime

| Skill | Description |
|-------|-------------|
| `roblox-performance` | Profiler, microprofiler, optimization patterns, object pooling, StreamingEnabled, memory. |

## Building & UI

| Skill | Description |
|-------|-------------|
| `roblox-building` | 3D builds via MCP, CSG operations, spatial coordination, Part properties, map design. |
| `roblox-physics` | Constraints, VehicleSeat, ragdoll, projectiles, Attachment patterns, network ownership. |
| `roblox-gui` | GUI systems, layout, responsiveness, cross-platform UI. ScreenGuis, UIListLayout, constraint-based design. |
| `roblox-animation-vfx` | Animations, particles, tweens, ContentProvider, visual effects. |
| `roblox-lighting` | Lighting service, Atmosphere, post-processing (Bloom, ColorCorrection), day/night cycle. |
| `roblox-audio` | SoundService, SoundGroup mixer, spatial audio, 3D positioned sound, music systems, SFX patterns. |
| `roblox-input` | UserInputService, ContextActionService, keyboard/mouse/gamepad/touch, cross-platform input binding. |
| `roblox-camera` | Camera object, CameraType enum, CFrame math, custom controllers, first/third person, cutscenes, screen shake. |

## MCP & Cloud

| Skill | Description |
|-------|-------------|
| `roblox-studio-mcp` | Studio MCP server tools, execute_luau, script_read/multi_edit, reliability patterns, workflows. |
| `roblox-cloud` | Open Cloud REST API, API keys, webhooks, HttpService constraints, scope selection. |
| `roblox-oauth` | OAuth 2.0 flows, PKCE, authorization code, token lifecycle, scope selection, Open Cloud auth. |

## Workflow

| Skill | Description |
|-------|-------------|
| `roblox-debug` | Iterative debug loop for Luau/Roblox issues |
| `roblox-code-review` | Code review with security, performance, and monetization lenses for Roblox projects |
| `roblox-publish-checklist` | Pre-publish verification gauntlet for Roblox games |
| `roblox-testing` | TestEZ, mocking Roblox services, dependency injection, CI/CD with Lune, test patterns. |
| `roblox-tooling` | Rojo, Wally, Selene, StyLua, Lune, Aftman, luau-lsp, filesystem workflows, CI pipeline. |

## Localization

| Skill | Description |
|-------|-------------|
| `roblox-localization` | LocalizationService, translation tables, locale detection, auto-translation, country/region handling. |
