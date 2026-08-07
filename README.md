<div align="center">

# roblox-brain 🧠

**A practical skill library for Roblox Studio coding agents.**

Works with Codex, Claude Code, OpenCode, Cursor, and other tools that support agent skills.

[![CI](https://img.shields.io/github/actions/workflow/status/TabooHarmony/roblox-brain/ci.yml?branch=main&label=ci)](https://github.com/TabooHarmony/roblox-brain/actions/workflows/ci.yml)
[![GitHub Release](https://img.shields.io/github/v/release/TabooHarmony/roblox-brain?display_name=tag&sort=semver)](https://github.com/TabooHarmony/roblox-brain/releases)
[![License](https://img.shields.io/github/license/TabooHarmony/roblox-brain)](LICENSE)
[![skills.sh](https://skills.sh/b/TabooHarmony/roblox-brain)](https://skills.sh/TabooHarmony/roblox-brain)

</div>

## What this is

`roblox-brain` gives an AI coding agent focused Roblox Studio knowledge without forcing every task through one framework. Each skill starts small and expands only when the task needs deeper examples or API details.

- 28 focused skills across Luau, architecture, game design, networking, UI, physics, data, monetization, localization, tooling, and publishing.
- Guidance grounded in Roblox Creator Hub documentation, compatible external tools, and original synthesis.

## Install

```bash
# install the full library
npx skills add TabooHarmony/roblox-brain

# install one skill
npx skills add TabooHarmony/roblox-brain --skill roblox-building
```

You can also copy an individual `SKILL.md` into `.claude/skills/`, `.codex/skills/`, `.cursor/skills/`, or another compatible skill directory.

## Skills (28)

### Core language and architecture

| Skill | What it covers |
| --- | --- |
| `roblox-luau-core` | Luau syntax, tables, control flow, string patterns, scope, closures, idioms, and language traps |
| `roblox-luau-types` | Types, generics, narrowing, inference, sealed/unsealed tables, exports, and Roblox-aware typing |
| `roblox-luau-patterns` | Module boundaries, object lifecycles, signals, scheduling, fallible calls, and cleanup |
| `roblox-architecture` | Feature ownership, runtime location, dependencies, startup, and client/server authority |


### Game design and growth

| Skill | What it covers |
| --- | --- |
| `roblox-growth-design` | Discovery, positioning, onboarding, retention, experiments, packaging, LiveOps, and growth diagnosis |

### Monetization

| Skill | What it covers |
| --- | --- |
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
| `roblox-ui-design` | Content-led visual systems, existing-style inheritance, optional simulator styling, composition, and hierarchy |
| `roblox-animation-vfx` | Animations, particles, beams, trails, tweens, camera feedback, and cleanup |
| `roblox-lighting` | Lighting, atmosphere, post-processing, mood presets, and day/night cycles |
| `roblox-audio` | SoundService, spatial audio, music systems, SFX, ambient layers, and volume management |
| `roblox-input` | UserInputService, ContextActionService, keyboard, mouse, gamepad, and touch |
| `roblox-camera` | Camera types, CFrame math, custom controllers, cutscenes, and screen shake |

### MCP and cloud

| Skill | What it covers |
| --- | --- |
| `roblox-studio-mcp` | Studio MCP capabilities, bridge-neutral routing, reliability, building, and testing workflows |
| `roblox-cloud` | Open Cloud REST APIs, API keys, OAuth 2.0, PKCE, webhooks, HttpService, and token lifecycle |

### Workflow and tooling

| Skill | What it covers |
| --- | --- |
| `roblox-code-review` | Reviews through security, performance, correctness, and monetization lenses |
| `roblox-publish-checklist` | Change-scoped release gates, evidence, dashboard checks, and rollback readiness |
| `roblox-tooling` | Rojo, Wally, Selene, StyLua, Lune, Aftman, sourcemaps, and CI |
| `roblox-localization` | LocalizationService, translation tables, locale handling, and auto-translation |

## How the content is organized

Skills use **progressive disclosure** so an agent can start with a small context window and load detail only when needed:

```text
skills/roblox-gui/
├── SKILL.md              # quick reference
└── references/
    └── full.md           # examples, API notes, and edge cases
```

1. **Discovery:** the host reads skill names and descriptions from `SKILL.md` frontmatter.
2. **Quick reference:** the selected `SKILL.md` gives default rules and routing.
3. **Full reference:** linked `references/full.md` material is loaded only when the task needs it.

## Recommended MCP servers

- **[Roblox Studio MCP](https://create.roblox.com/docs/studio/mcp):** use the official server or a [community fork with additional features](https://github.com/Chrrxs/robloxstudio-mcp).
- **[codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp):** local codebase memory and structural search, saves a lot of tokens.

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

- **[MrFearTick](https://www.roblox.com/users/1880599950/profile):** code references, networking, and monetization expansion
- **[eeyq](https://www.roblox.com/users/192217155/profile):** content and references for the `roblox-growth-design` skill


## License

MIT
