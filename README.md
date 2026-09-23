<div align="center">

# roblox-brain 🧠

**Roblox Studio skills for AI coding agents.**

29 skills across four libraries. Install what you need, or take the whole set.

[![CI](https://img.shields.io/github/actions/workflow/status/TabooHarmony/roblox-brain/ci.yml?branch=main&label=ci)](https://github.com/TabooHarmony/roblox-brain/actions/workflows/ci.yml)
[![GitHub Release](https://img.shields.io/github/v/release/TabooHarmony/roblox-brain?display_name=tag&sort=semver)](https://github.com/TabooHarmony/roblox-brain/releases)
[![License](https://img.shields.io/github/license/TabooHarmony/roblox-brain)](LICENSE)
[![skills.sh](https://skills.sh/b/TabooHarmony/roblox-brain)](https://skills.sh/TabooHarmony/roblox-brain)

</div>

## Pick a library

| | Library | Skills | For |
| :-- | :-- | --: | :-- |
| 🧱 | **Core** | 10 | Luau, architecture, networking, security, data, performance |
| 🎮 | **Gameplay** | 10 | Building, physics, NPCs, camera, input, GUI, and presentation |
| 🎨 | **Design** | 5 | Game design, player behavior, growth, analytics, monetization |
| 🛠️ | **Tools** | 4 | Studio MCP, project tooling, Open Cloud, publishing |

Start with **Core** for general development. Add the others when the task calls for them. Each skill has a short entry point and a deeper reference with examples and API details.

## Install

**All 29 skills:**

```bash
npx skills add TabooHarmony/roblox-brain
```

**One library:**

```bash
npx skills add TabooHarmony/roblox-brain/skills/core
# or: gameplay, design, tools
```

**One skill:**

```bash
npx skills add TabooHarmony/roblox-brain --skill roblox-building
```

Manual install: copy the **whole skill directory**, including `references/full.md`, into your agent's skills folder. For example: `cp -r skills/design/roblox-growth-design ~/.claude/skills/`. This also works with `.codex/skills/` and `.cursor/skills/`. Copying only `SKILL.md` leaves the reference missing.

## Skills (29)

Expand a library to see its skills. The full-repo install includes all four.

<details>
<summary><strong>🧱 Core</strong> · 10 skills · Luau and development foundations</summary>

| Skill | Covers |
| :-- | :-- |
| `roblox-collaboration-mode` | Peer vs autonomous working mode, risk-scaled initiative, and surfacing uncertainty before domain work |
| `roblox-luau-core` | Luau syntax, tables, control flow, string patterns, scope, closures, idioms, and language traps |
| `roblox-luau-types` | Types, generics, narrowing, inference, sealed/unsealed tables, exports, and Roblox-aware typing |
| `roblox-luau-patterns` | Module boundaries, object lifecycles, signals, scheduling, fallible calls, and cleanup |
| `roblox-architecture` | Feature ownership, runtime location, dependencies, startup, and client/server authority |
| `roblox-networking` | Server-authoritative networking, remote validation, rate limits, and exploit resistance |
| `roblox-security` | Anti-exploit design, movement, remote, economy, and data hardening |
| `roblox-data` | Player persistence, schemas, migrations, retries, session ownership, and budgets |
| `roblox-server-data` | OrderedDataStore, MessagingService, global state, and cross-server coordination |
| `roblox-performance` | Profiling, optimization, pooling, streaming, and mobile performance |

</details>

<details>
<summary><strong>🎮 Gameplay</strong> · 10 skills · What players see and do</summary>

| Skill | Covers |
| :-- | :-- |
| `roblox-building` | Geometry, maps, props, generated assets, and build verification |
| `roblox-physics` | Constraints, vehicles, ragdolls, projectiles, and network ownership |
| `roblox-npc-ai` | Pathfinding, state machines, detection, spawning, and network ownership |
| `roblox-camera` | Camera types, CFrame math, custom controllers, cutscenes, and screen shake |
| `roblox-input` | Keyboard, mouse, gamepad, touch, and action binding |
| `roblox-gui` | Screen, surface, and world UI; layout, responsiveness, input, state, and visual verification |
| `roblox-animation-vfx` | Animations, particles, beams, trails, tweens, and camera feedback |
| `roblox-lighting` | Lighting, atmosphere, post-processing, and day/night cycles |
| `roblox-audio` | SoundService, spatial audio, music systems, and SFX |
| `roblox-localization` | Translation tables, locale handling, and auto-translation |

</details>

<details>
<summary><strong>🎨 Design</strong> · 5 skills · Play, retention, and economy</summary>

| Skill | Covers |
| :-- | :-- |
| `roblox-game-design` | Core loops, tutorials, levels, economy structure, and game feel |
| `roblox-player-psychology` | First-minute psychology, reward schedules, pricing, RNG/pity, and community loops |
| `roblox-growth-design` | Discovery, positioning, retention, experiments, packaging, and LiveOps |
| `roblox-analytics` | Custom events, economy tracking, funnels, and event taxonomy |
| `roblox-monetization` | Game Passes, Developer Products, receipts, subscriptions, and policy checks |

</details>

<details>
<summary><strong>🛠️ Tools</strong> · 4 skills · Studio and shipping</summary>

| Skill | Covers |
| :-- | :-- |
| `roblox-studio-mcp` | Studio MCP capabilities, reliability, building, and testing workflows |
| `roblox-tooling` | Rojo, Wally, Selene, StyLua, Lune, Aftman, and CI |
| `roblox-cloud` | Open Cloud REST APIs, API keys, OAuth, webhooks, and token lifecycle |
| `roblox-publish-checklist` | Change-scoped release gates, evidence, dashboard checks, and rollback readiness |

</details>

## How it works

An agent discovers the skill descriptions, loads the relevant `SKILL.md`, then opens `references/full.md` only when it needs the detail:

```text
skills/gameplay/roblox-gui/
├── SKILL.md              # quick reference
└── references/
    └── full.md           # examples and API notes
```

The guidance draws on Roblox Creator Hub documentation, compatible external tools, and original synthesis.

## Studio connection

For agents working directly in Studio, [chrrxs/robloxstudio-mcp](https://github.com/Chrrxs/robloxstudio-mcp) provides runtime debugging, multiplayer playtests, profiling, and per-instance routing. The built-in [Roblox Studio MCP](https://create.roblox.com/docs/studio/mcp) is another option.

## Contributing

Corrections, production patterns, and examples with compatible sourcing are welcome. Keep skills focused and practical. Before opening a PR, run:

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/verify_api_drift.py
python3 scripts/verify_source_urls.py
python3 scripts/verify_version_pins.py
```

## Contributors

- [MrFearTick](https://www.roblox.com/users/1880599950/profile): code references, networking, and monetization expansion
- [eeyq](https://www.roblox.com/users/192217155/profile): content and references for `roblox-growth-design`

## License

MIT
