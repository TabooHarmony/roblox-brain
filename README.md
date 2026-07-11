# roblox-brain

[![CI](https://img.shields.io/github/actions/workflow/status/TabooHarmony/roblox-brain/ci.yml?branch=main&label=ci)](https://github.com/TabooHarmony/roblox-brain/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-30-blue.svg)](skills)
[![Roblox](https://img.shields.io/badge/Roblox-Luau-red.svg)](https://create.roblox.com/docs/luau)
[![Agent Skills](https://img.shields.io/badge/agent_skills-compatible-purple.svg)](skill_index.md)

Give your AI coding agent a Roblox brain.

30 curated skills that make AI assistants competent at Roblox/Luau game development. Works with Codex, Claude Code, OpenCode, Cursor, or anything that supports agent skills.

## What you get

- 30 focused skills covering Luau, architecture, networking, UI, physics, data, monetization, localization, tooling, and publishing.
- Compact `SKILL.md` files for quick context, with deeper `references/full.md` files when the agent needs examples or API tables.
- Source-tracked guidance from Roblox creator-docs, attributed external references, and original patterns.
- Local validation plus API drift checks for high-risk claims (deprecations, property existence) against live Roblox creator-docs. The registry is curated, not comprehensive — expand it when adding new API claims to skills.

## Install

```bash
# all skills
npx skills add TabooHarmony/roblox-brain

# one skill
npx skills add TabooHarmony/roblox-brain --skill roblox-building
```

Or just copy any `SKILL.md` into your project's skill directory (`.claude/skills/`, `.opencode/skills/`, `.cursor/skills/`, etc).

## Architecture

Each skill uses a **progressive disclosure** design to keep context lean. Skills are designed to be loaded in this order — platforms that respect the SKILL.md entry point will load efficiently; others may load all files at once (content is still correct, just less context-efficient).

```
skills/roblox-gui/
├── SKILL.md              (~600 tokens, quick reference only)
└── references/
    └── full.md           (up to ~10,000 tokens, complete documentation)
```

1. **Level 1: Index**: Agent reads `skill_index.md` (all skills, ~2,800 tokens) to know what's available
2. **Level 2: Quick Reference**: Agent loads `SKILL.md` for the relevant skill (~600 tokens). This is enough for most tasks.
3. **Level 3: Full Reference**: Agent reads `references/full.md` when it needs detailed code examples, API tables, or edge cases

## Skills (30)

### Core Language & Architecture

| Skill | What it does |
|-------|-------------|
| `roblox-luau-core` | Luau syntax, tables, control flow, string patterns, math, idioms, scope, closures, sharp edges, JS to Luau translation |
| `roblox-luau-types` | Type system, generics, narrowing, inference philosophy, sealed/unsealed tables, exports, Roblox-aware typing |
| `roblox-luau-patterns` | OOP with metatables, inheritance, async (Promises, pcall, coroutines), module structure, service pattern, Roblox idioms |
| `roblox-architecture` | Service hierarchy, 7 foundational patterns, client-server architecture, module patterns |
| `roblox-sharp-edges` | 13 production footguns ranked by severity. Data loss, exploits, memory leaks, mobile perf |

### Economy & Monetization

| Skill | What it does |
|-------|-------------|
| `roblox-economy` | Currencies, faucets/sinks, inflation control, time-to-earn, trading, monetization integration |
| `roblox-monetization` | ProcessReceipt correctness, prompt APIs, purchase reconciliation, session-lock interaction |

### Systems & Networking

| Skill | What it does |
|-------|-------------|
| `roblox-networking` | Server-authoritative networking, RemoteEvent validation, rate limiting, exploit prevention |
| `roblox-security` | Anti-exploit design, movement/remote/economy exploits, audit checklist, hardening patterns |
| `roblox-data` | DataStores, ProfileStore, session locking, data persistence patterns |
| `roblox-server-data` | OrderedDataStore, MessagingService, GlobalDataStore, cross-server state, persistent world data |
| `roblox-analytics` | AnalyticsService: custom events, economy tracking, funnels, rate limits, event taxonomy |
| `roblox-npc-ai` | Pathfinding, state machines, detection (LOS/FOV), spawn systems, network ownership |

### Performance & Runtime

| Skill | What it does |
|-------|-------------|
| `roblox-performance` | Profiling tools, optimization patterns, object pooling, StreamingEnabled, mobile optimization, budgets |

### Building & UI

| Skill | What it does |
|-------|-------------|
| `roblox-building` | Build 3D objects and maps via MCP. CSG patterns, spatial coordination, player scale, platform quirks |
| `roblox-physics` | Constraints, vehicles, ragdoll, projectiles, elevators, network ownership |
| `roblox-gui` | GUI systems, layout, responsiveness, cross-platform UI. ScreenGuis, UIListLayout, constraints |
| `roblox-animation-vfx` | Animations, particles, tweens, ContentProvider, visual effects |
| `roblox-lighting` | Lighting, atmosphere, post-processing, mood presets, day/night cycle, zone transitions |
| `roblox-audio` | SoundService, spatial audio, music systems, SFX patterns, ambient layering, volume management |
| `roblox-input` | UserInputService, ContextActionService, keyboard/mouse/gamepad/touch, cross-platform input binding |
| `roblox-camera` | Camera object, CameraType, CFrame math, custom controllers, first/third person, cutscenes, screen shake |

### MCP & Cloud

| Skill | What it does |
|-------|-------------|
| `roblox-studio-mcp` | Official Studio MCP server tool catalog, reliability patterns, and workflows for scripting, building, and testing |
| `roblox-cloud` | Open Cloud REST APIs, API keys, webhooks, HttpService constraints, rate limits |
| `roblox-oauth` | OAuth 2.0 flows, PKCE, token lifecycle, scope selection, app registration |

### Workflow

| Skill | What it does |
|-------|-------------|
| `roblox-debug` | Iterative debug loop for Luau/Roblox issues |
| `roblox-code-review` | Code review with security, performance, and monetization lenses |
| `roblox-publish-checklist` | Pre-publish verification gauntlet |
| `roblox-tooling` | Rojo, Wally, Selene, StyLua, Lune, Aftman. Filesystem-based workflows and editor setup |

### Localization

| Skill | What it does |
|-------|-------------|
| `roblox-localization` | LocalizationService, translation tables, locale detection, auto-translation, country/region handling |

## Recommended MCP Servers

- **[Roblox Studio MCP](https://create.roblox.com/docs/studio/mcp)**: Use the official Studio MCP or your preferred community bridge. `roblox-brain` does not require a specific MCP server.
- **[mcp-roblox-docs](https://github.com/n4tivex/mcp-roblox-docs)**: Roblox API reference at runtime. `uvx mcp-roblox-docs`
- **[codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)**: Local codebase memory and structural search.

## Contributors

- **[MrFearTick](https://github.com/MrFearTick)**: Code references, networking + monetization expansion

## Contributing

PRs welcome. Good contributions:
- Fix incorrect API references or deprecated patterns
- Add high-value patterns from production games
- Expand reference code (must come from a compatible license or explicit reuse permission, or be original)
- Keep skills focused, non-overlapping, and practical. All skill submissions must pass `validate_skills.py`.


## License

MIT
