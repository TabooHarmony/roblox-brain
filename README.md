<div align="center">

# roblox-brain 🧠

**A practical skill library for Roblox Studio coding agents.**

Works with Codex, Claude Code, Cursor, Roblox Assistant, and other tools that support agent skills.

[![CI](https://img.shields.io/github/actions/workflow/status/TabooHarmony/roblox-brain/ci.yml?branch=main&label=ci)](https://github.com/TabooHarmony/roblox-brain/actions/workflows/ci.yml)
[![GitHub Release](https://img.shields.io/github/v/release/TabooHarmony/roblox-brain?display_name=tag&sort=semver)](https://github.com/TabooHarmony/roblox-brain/releases)
[![License](https://img.shields.io/github/license/TabooHarmony/roblox-brain)](LICENSE)
[![skills.sh](https://skills.sh/b/TabooHarmony/roblox-brain)](https://skills.sh/TabooHarmony/roblox-brain)

</div>

## Choose what to install

`roblox-brain` gives AI agents focused Roblox Studio guidance without forcing every task through one framework. Each skill starts small and expands only when the task needs deeper examples or API details. The guidance draws on Roblox Creator Hub documentation, compatible external tools, and original synthesis.

- **Core:** Luau, architecture, networking, security, data, and performance. A good starting point for general development.
- **Gameplay:** Building, physics, NPCs, camera, input, GUI, animation, lighting, audio, and localization.
- **Design:** Game design, player behavior, growth, analytics, and monetization.
- **Tools:** Studio MCP, project tooling, Open Cloud, and publishing.

Start with the library you need. You can add others later, or install all skills at once.

## Install

```bash
# everything
npx skills add TabooHarmony/roblox-brain

# one library
npx skills add TabooHarmony/roblox-brain/skills/core
npx skills add TabooHarmony/roblox-brain/skills/gameplay
npx skills add TabooHarmony/roblox-brain/skills/design
npx skills add TabooHarmony/roblox-brain/skills/tools

# or one named skill
npx skills add TabooHarmony/roblox-brain --skill roblox-building
```


To install manually, copy the whole skill directory, not just the file. A `SKILL.md` is an entry point, not the whole skill: skills link `references/full.md` for depth and examples, and a file-only copy loses that material.

```bash
# whole directory, references included
cp -r skills/design/roblox-growth-design ~/.claude/skills/
```

Works the same for `.codex/skills/`, `.cursor/skills/`, and other compatible skill directories. A directory copy is self-contained: everything the entry point links ships with it. If an agent hits a link to a `references/full.md` that was not copied, the right response is to say the reference is missing and ask the user to copy that skill's whole directory from this repo. Never summarize reference material that is not there, and never present it as loaded.

## Skills (29)

Each library can be installed alone. `core` is the general development baseline; add the others for the work at hand. The full-repo install still includes all 29.

### Core (`skills/core/`, 10)

| Skill | What it covers |
| --- | --- |
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

### Gameplay (`skills/gameplay/`, 10)

| Skill | What it covers |
| --- | --- |
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

### Design (`skills/design/`, 5)

| Skill | What it covers |
| --- | --- |
| `roblox-game-design` | Core loops, tutorials, levels, economy structure, and game feel |
| `roblox-player-psychology` | First-minute psychology, reward schedules, pricing, RNG/pity, and community loops |
| `roblox-growth-design` | Discovery, positioning, retention, experiments, packaging, and LiveOps |
| `roblox-analytics` | Custom events, economy tracking, funnels, and event taxonomy |
| `roblox-monetization` | Game Passes, Developer Products, receipts, subscriptions, and policy checks |

### Tools (`skills/tools/`, 4)

| Skill | What it covers |
| --- | --- |
| `roblox-studio-mcp` | Studio MCP capabilities, reliability, building, and testing workflows |
| `roblox-tooling` | Rojo, Wally, Selene, StyLua, Lune, Aftman, and CI |
| `roblox-cloud` | Open Cloud REST APIs, API keys, OAuth, webhooks, and token lifecycle |
| `roblox-publish-checklist` | Change-scoped release gates, evidence, dashboard checks, and rollback readiness |

## How the content is organized

Skills use **progressive disclosure** so an agent can start with a small context window and load detail only when needed:

```text
skills/gameplay/roblox-gui/
├── SKILL.md              # quick reference
└── references/
    └── full.md           # examples, API notes, and edge cases
```

1. **Discovery:** the host reads skill names and descriptions from `SKILL.md` frontmatter.
2. **Quick reference:** the selected `SKILL.md` gives default rules and routing.
3. **Full reference:** linked `references/full.md` material is loaded only when the task needs it.

## Recommended tooling

- **[chrrxs/robloxstudio-mcp](https://github.com/Chrrxs/robloxstudio-mcp):** the recommended Studio MCP server. Open source (MIT), and adds runtime debugging, multiplayer playtests, profiling, per-instance routing, and more. The official [Roblox Studio MCP](https://create.roblox.com/docs/studio/mcp) built into Studio works fine as well if you prefer the built-in option.

## Contributing

PRs are welcome. Useful contributions include:

- correcting an API reference or deprecated pattern;
- adding a focused, widely applicable production pattern;
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
