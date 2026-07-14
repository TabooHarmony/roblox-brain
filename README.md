<div align="center">

# roblox-brain 🧠

**A practical skill library for Roblox Studio coding agents.**

Works with Codex, Claude Code, OpenCode, Cursor, and other tools that support agent skills.

[![CI](https://img.shields.io/github/actions/workflow/status/TabooHarmony/roblox-brain/ci.yml?branch=main&label=ci)](https://github.com/TabooHarmony/roblox-brain/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-31-blue.svg)](skills)
[![Roblox](https://img.shields.io/badge/Roblox-Luau-red.svg)](https://create.roblox.com/docs/luau)
[![Agent Skills](https://img.shields.io/badge/agent_skills-compatible-purple.svg)](skill_index.md)
[![skills.sh](https://skills.sh/b/TabooHarmony/roblox-brain)](https://skills.sh/TabooHarmony/roblox-brain)

</div>

## What this is

`roblox-brain` gives an AI coding agent focused Roblox Studio knowledge without forcing every task through one framework. Each skill starts small and expands only when the task needs deeper examples or API details.

- 31 focused skills across Luau, architecture, networking, UI, physics, data, monetization, localization, tooling, and publishing.
- Compact `SKILL.md` entry points with deeper `references/full.md` material.
- Guidance grounded in Roblox Creator Hub documentation, compatible external tools, and original synthesis.
- Local validation, source checks, API-drift checks, version-pin checks, and copy-paste Luau probes.

## Install

```bash
# install the full library
npx skills add TabooHarmony/roblox-brain

# install one skill
npx skills add TabooHarmony/roblox-brain --skill roblox-building
```

You can also copy an individual `SKILL.md` into `.claude/skills/`, `.opencode/skills/`, `.cursor/skills/`, or another compatible skill directory.

## How the content is organized

Skills use **progressive disclosure** so an agent can start with a small context window and load detail only when needed:

```text
skills/roblox-gui/
├── SKILL.md              # quick reference
└── references/
    └── full.md           # examples, API notes, and edge cases
```

1. **Index:** `skill_index.md` shows what is available.
2. **Quick reference:** the relevant `SKILL.md` gives the default rules and routing.
3. **Full reference:** `references/full.md` supplies implementation details when the task needs them.

## Skills (31)

### Core language and architecture

| Skill | What it covers |
| --- | --- |
| `roblox-luau-core` | Luau syntax, tables, control flow, string patterns, math, scope, closures, idioms, and sharp edges |
| `roblox-luau-types` | Types, generics, narrowing, inference, sealed/unsealed tables, exports, and Roblox-aware typing |
| `roblox-luau-patterns` | Metatables, inheritance, async patterns, module structure, services, and Roblox idioms |
| `roblox-architecture` | Service hierarchy, client/server boundaries, module contracts, and startup design |
| `roblox-sharp-edges` | High-impact production footguns involving data, remotes, purchases, lifecycle, and scale |

### Economy and monetization

| Skill | What it covers |
| --- | --- |
| `roblox-economy` | Currencies, faucets, sinks, inflation control, time-to-earn, trading, and economy integration |
| `roblox-monetization` | Game Passes, Developer Products, receipts, subscriptions, policy checks, and purchase recovery |

### Systems and networking

| Skill | What it covers |
| --- | --- |
| `roblox-networking` | Server-authoritative networking, remote validation, rate limits, and exploit resistance |
| `roblox-security` | Anti-exploit design, movement, remote, economy, and data hardening |
| `roblox-data` | Player persistence, schemas, migrations, retries, and session ownership |
| `roblox-server-data` | OrderedDataStore, MessagingService, global state, and cross-server coordination |
| `roblox-analytics` | Custom events, economy tracking, funnels, rate limits, and event taxonomy |
| `roblox-npc-ai` | Pathfinding, state machines, detection, spawning, and network ownership |

### Performance and runtime

| Skill | What it covers |
| --- | --- |
| `roblox-performance` | Profiling, optimization, pooling, streaming, mobile performance, and budgets |

### Building and UI

| Skill | What it covers |
| --- | --- |
| `roblox-building` | Roblox geometry, maps, props, generated assets, MCP workflows, and acceptance gates |
| `roblox-physics` | Constraints, vehicles, ragdolls, projectiles, elevators, and network ownership |
| `roblox-gui` | Screen, surface, and world UI; layout, responsiveness, input, and UI state |
| `roblox-ui-design` | Visual UI design with simulator defaults, existing-style inheritance, composition, hierarchy, and bounded layout |
| `roblox-animation-vfx` | Animations, particles, beams, trails, tweens, camera feedback, and cleanup |
| `roblox-lighting` | Lighting, atmosphere, post-processing, mood presets, and day/night cycles |
| `roblox-audio` | SoundService, spatial audio, music systems, SFX, ambient layers, and volume management |
| `roblox-input` | UserInputService, ContextActionService, keyboard, mouse, gamepad, and touch |
| `roblox-camera` | Camera types, CFrame math, custom controllers, cutscenes, and screen shake |

### MCP and cloud

| Skill | What it covers |
| --- | --- |
| `roblox-studio-mcp` | Studio MCP capabilities, bridge-neutral routing, reliability, building, and testing workflows |
| `roblox-cloud` | Open Cloud REST APIs, API keys, webhooks, HttpService, and rate limits |
| `roblox-oauth` | OAuth 2.0, PKCE, token lifecycle, scopes, and app registration |

### Workflow and tooling

| Skill | What it covers |
| --- | --- |
| `roblox-debug` | Iterative debugging for Luau and Roblox issues |
| `roblox-code-review` | Reviews through security, performance, correctness, and monetization lenses |
| `roblox-publish-checklist` | Pre-publish verification and release gates |
| `roblox-tooling` | Rojo, Wally, Selene, StyLua, Lune, Aftman, sourcemaps, and CI |
| `roblox-localization` | LocalizationService, translation tables, locale handling, and auto-translation |

## Recommended MCP servers

- **[Roblox Studio MCP](https://create.roblox.com/docs/studio/mcp):** use the official server or a compatible community bridge. The skills route by capability and do not require one specific bridge.
- **[mcp-roblox-docs](https://github.com/n4tivex/mcp-roblox-docs):** runtime Roblox API reference, installable with `uvx mcp-roblox-docs`.
- **[codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp):** local codebase memory and structural search.

## Contributing

PRs are welcome. Useful contributions include:

- correcting an API reference or deprecated pattern;
- adding a focused production pattern;
- expanding examples from a compatible license, explicit permission, or original work;
- keeping skills small, non-overlapping, and practical.

Before opening a PR, run:

```bash
python3 validate_skills.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 verify_api_drift.py
python3 verify_source_urls.py
python3 verify_version_pins.py
```

## Contributors

- **[MrFearTick](https://github.com/MrFearTick):** code references, networking, and monetization expansion

## Release notes

See [CHANGELOG.md](CHANGELOG.md) for the v1.0.0 release notes.

## License

MIT
