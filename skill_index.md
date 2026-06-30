# Skill Index

Compact index of all roblox-brain skills (~2,800 tokens). Load this at startup to know what's available, then load specific skills as needed.

## Core Language & Architecture

| Skill | Description |
|-------|-------------|
| `roblox-luau-mastery` | Router to the three Luau skills below. Load for Luau language guidance. |
| `roblox-luau-core` | Luau syntax, tables, string patterns, math, idioms, scope, closures, sharp edges, JS→Luau |
| `roblox-luau-types` | Type system, generics, narrowing, inference, sealed/unsealed tables, --!strict mode |
| `roblox-luau-patterns` | OOP with metatables, inheritance, async (Promises, pcall), module structure, service pattern |
| `roblox-architecture` | Service hierarchy, 7 foundational patterns, cross-platform input, client-server architecture |
| `roblox-sharp-edges` | 13 production footguns: DataStore loss, client currency exploit, ProcessReceipt, memory leaks |

## Economy & Monetization

| Skill | Description |
|-------|-------------|
| `roblox-economy` | Currency design, faucets/sinks, inflation control, time-to-earn, trading systems |
| `roblox-monetization` | ProcessReceipt correctness, prompt APIs, GamePass, DeveloperProducts, purchase reconciliation |

## Systems & Networking

| Skill | Description |
|-------|-------------|
| `roblox-networking` | Server-authoritative networking, RemoteEvent/RemoteFunction validation, rate limiting |
| `roblox-security` | Anti-exploit design, server authority, RemoteEvent validation, rate limiting, audit checklist |
| `roblox-data` | DataStores, ProfileStore, session locking, data persistence, UpdateAsync patterns |
| `roblox-analytics` | AnalyticsService custom events, economy tracking, funnels, player behavior metrics |
| `roblox-npc-ai` | Pathfinding, state machines, NPC detection (LOS/FOV), spawn systems, enemy AI patterns |

## Performance & Runtime

| Skill | Description |
|-------|-------------|
| `roblox-performance` | Profiler, microprofiler, optimization patterns, object pooling, StreamingEnabled, memory |

## Building & UI

| Skill | Description |
|-------|-------------|
| `roblox-building` | 3D builds via MCP, CSG operations, spatial coordination, Part properties, map design |
| `roblox-physics` | Constraints, VehicleSeat, ragdoll, projectiles, Attachment patterns, network ownership |
| `roblox-gui` | ScreenGui layout, UIListLayout, Scale vs Offset, responsive design, mobile-first, ScrollingFrame |
| `roblox-animation-vfx` | Animation tracks, Animator API, ParticleEmitter, Beam, TweenService, Highlight, visual juice |
| `roblox-lighting` | Lighting service, Atmosphere, post-processing (Bloom, ColorCorrection), day/night cycle |
| `roblox-audio` | SoundService, SoundGroup mixer, spatial audio, 3D positioned sound, music systems, SFX patterns |
| `roblox-input` | UserInputService, ContextActionService, keyboard/mouse/gamepad/touch, cross-platform input binding |

## MCP & Cloud

| Skill | Description |
|-------|-------------|
| `roblox-studio-mcp` | Studio MCP server tools, execute_luau, script_read/multi_edit, reliability patterns, workflows |
| `roblox-cloud` | Open Cloud REST API, API keys, webhooks, HttpService constraints, scope selection |
| `roblox-oauth` | OAuth 2.0 flows, PKCE, authorization code, token lifecycle, scope selection, Open Cloud auth |

## Workflow

| Skill | Description |
|-------|-------------|
| `roblox-debug` | Iterative debug loop for Luau/Roblox issues, pcall error handling, stack traces |
| `roblox-code-review` | Code review checklist: security, performance, networking, data persistence, monetization lenses |
| `roblox-publish-checklist` | Pre-publish checks: security, performance, data persistence, monetization, mobile, accessibility |
| `roblox-testing` | TestEZ, mocking Roblox services, dependency injection, CI/CD with Lune, test patterns |
| `roblox-tooling` | Rojo, Wally, Selene, StyLua, Lune, Aftman, luau-lsp, filesystem workflows, CI pipeline |
