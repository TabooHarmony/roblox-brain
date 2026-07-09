# Skill Index

Compact index of all roblox-brain skills (~2,800 tokens). Load this at startup to know what's available, then load specific skills as needed.

## Core Language & Architecture

| Skill | Description |
|-------|-------------|
| `roblox-luau-core` | Use for Luau syntax, tables, control flow, string patterns, math, scope, closures, idioms, or porting code from JavaScript or Python. |
| `roblox-luau-types` | Use for Luau annotations, generics, unions, narrowing, strictness, sealed tables, module type exports, or typed metatables. |
| `roblox-luau-patterns` | Use for Luau metatable classes, inheritance, Promises, coroutines, pcall, module structure, services, and Roblox coding patterns. |
| `roblox-architecture` | Use when starting or refactoring a Roblox project, choosing service or module structure, or making client-server architecture decisions. |
| `roblox-sharp-edges` | Use before shipping or reviewing Roblox code involving player data, remotes, monetization, or memory to catch high-impact production footguns. |

## Economy & Monetization

| Skill | Description |
|-------|-------------|
| `roblox-economy` | Use when designing Roblox currencies, rewards, faucets, sinks, trading, marketplaces, or inflation controls. |
| `roblox-monetization` | Use when implementing Roblox GamePasses, Developer Products, Premium payouts, purchase reconciliation, or monetization policy checks. |

## Systems & Networking

| Skill | Description |
|-------|-------------|
| `roblox-networking` | Use when validating RemoteEvent or RemoteFunction arguments, adding rate limits, designing server-authoritative systems, or preventing exploits. |
| `roblox-security` | Use when auditing Roblox code for exploit vectors or hardening movement, remotes, economy, and DataStore flows. |
| `roblox-data` | Use when implementing player data persistence with DataStore or ProfileStore, session locking, schemas, migrations, or save and load flows. |
| `roblox-server-data` | Use for Roblox server or cross-server data: OrderedDataStore leaderboards, MessagingService, world state, seasons, or guilds. |
| `roblox-analytics` | Use when tracking player behavior, economy events, or funnels with AnalyticsService, including event taxonomy, rate limits, and batching. |
| `roblox-npc-ai` | Use when creating Roblox NPCs or enemies with pathfinding, state machines, line-of-sight or FOV detection, spawns, or AI update loops. |

## Performance & Runtime

| Skill | Description |
|-------|-------------|
| `roblox-performance` | Use when profiling Roblox performance or diagnosing FPS, memory, network, mobile, or hot-path problems, including MicroProfiler and optimization. |

## Building & UI

| Skill | Description |
|-------|-------------|
| `roblox-building` | Use when building Roblox geometry or maps with MCP or scripts, including CSG, spatial coordination, scale, and platform quirks. |
| `roblox-physics` | Use when building Roblox vehicles, ragdolls, projectiles, elevators, constraints, forces, or other physics-driven gameplay. |
| `roblox-gui` | Use when building Roblox menus, HUDs, shops, notifications, dialogs, or responsive cross-platform UI. |
| `roblox-animation-vfx` | Use when implementing Roblox character animations, particles, beams, trails, tweens, camera shake, or other visual effects. |
| `roblox-lighting` | Use when configuring Roblox lighting, Atmosphere, time-of-day cycles, or post-processing effects. |
| `roblox-audio` | Use when implementing Roblox audio playback, spatial sound, music, sound effects, SoundGroups, or dynamic audio effects. |
| `roblox-input` | Use when handling Roblox keyboard, mouse, gamepad, touch, motion input, or cross-platform action binding. |
| `roblox-camera` | Use when scripting Roblox camera behavior, CFrame placement, screen raycasts, first or third-person views, or cutscenes. |

## MCP & Cloud

| Skill | Description |
|-------|-------------|
| `roblox-studio-mcp` | Use when working with Roblox Studio through built-in MCP for scripts, data-model inspection, Luau, assets, input, or playtesting. |
| `roblox-cloud` | Use when working with Roblox Open Cloud REST APIs, API keys, webhooks, or HttpService calls to cloud endpoints. |
| `roblox-oauth` | Use when implementing Roblox OAuth 2.0 for Open Cloud, including app registration, PKCE, token exchange, refresh, revocation, or scopes. |

## Workflow

| Skill | Description |
|-------|-------------|
| `roblox-debug` | Use when diagnosing Roblox or Luau errors, crashes, or unexpected behavior with an iterative reproduce, inspect, fix, and verify loop. |
| `roblox-code-review` | Use when reviewing Roblox or Luau code for security, performance, monetization, data persistence, or architecture risks. |
| `roblox-publish-checklist` | Use before publishing or updating a Roblox game to check data, security, performance, monetization, mobile, metadata, social, and analytics. |
| `roblox-testing` | Use when writing Roblox unit or integration tests, mocking services, setting up Lune CI, or designing code for dependency injection and testability. |
| `roblox-tooling` | Use when configuring Roblox tooling such as Rojo, Wally, Selene, StyLua, Lune, Aftman, luau-lsp, or CI/CD. |

## Localization

| Skill | Description |
|-------|-------------|
| `roblox-localization` | Use when implementing Roblox multi-language support, translation tables, auto-translation, locale-specific content, or region detection. |
