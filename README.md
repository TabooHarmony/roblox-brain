# roblox-brain

Give your AI coding agent a Roblox brain.

29 curated skills that make AI assistants competent at Roblox/Luau game development. Works with Codex, Claude Code, OpenCode, Cursor, or anything that supports agent skills.

## Install

```bash
# all skills
npx skills add TabooHarmony/roblox-brain

# one skill
npx skills add TabooHarmony/roblox-brain --skill roblox-building
```

Or just copy any `SKILL.md` into your project's skill directory (`.claude/skills/`, `.opencode/skills/`, `.cursor/skills/`, etc).

## Architecture

Each skill uses a **progressive disclosure** design to keep context lean:

```
skills/roblox-gui/
├── SKILL.md              (~600 tokens — quick reference only)
└── references/
    └── full.md           (~8,000 tokens — complete documentation)
```

**How agents consume this:**

1. **Level 1 — Index**: Agent reads `skill_index.md` (all 28 skills, ~2,800 tokens) to know what's available
2. **Level 2 — Quick Reference**: Agent loads `SKILL.md` for the relevant skill (~600 tokens). This is enough for most tasks.
3. **Level 3 — Full Reference**: Agent reads `references/full.md` when it needs detailed code examples, API tables, or edge cases

**Why this matters:** Loading 3 skills costs ~1,800 tokens instead of ~25,000 tokens. No more 3x slowdown.

### Validation

Run `python validate_skills.py` to check all skills comply with the size contract:

- SKILL.md under 3,000 chars
- Description under 150 chars
- Required frontmatter fields (name, description, last_reviewed)
- `## Quick Reference` section present
- No `## Full Reference` in SKILL.md (must be in references/)

## Skills (29)

### Core Language & Architecture

| Skill | What it does |
|-------|-------------|
| `roblox-luau-mastery` | Router to the three Luau skills below |
| `roblox-luau-core` | Luau syntax, tables, control flow, string patterns, math, idioms, scope, closures, sharp edges, JS→Luau translation |
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

### MCP & Cloud

| Skill | What it does |
|-------|-------------|
| `roblox-studio-mcp` | Official Studio MCP server: all 20 tools, reliability patterns, workflows for scripting/building/testing |
| `roblox-cloud` | Open Cloud REST APIs, API keys, webhooks, HttpService constraints, rate limits |
| `roblox-oauth` | OAuth 2.0 flows, PKCE, token lifecycle, scope selection, app registration |

### Workflow

| Skill | What it does |
|-------|-------------|
| `roblox-debug` | Iterative debug loop for Luau/Roblox issues |
| `roblox-code-review` | Code review with security, performance, and monetization lenses |
| `roblox-publish-checklist` | Pre-publish verification gauntlet |
| `roblox-testing` | TestEZ, mocking Roblox services, dependency injection, CI/CD with Lune |
| `roblox-tooling` | Rojo, Wally, Selene, StyLua, Lune, Aftman. Filesystem-based workflows and editor setup |

## Recommended MCP Servers

- **[robloxstudio-mcp](https://github.com/Chrrxs/robloxstudio-mcp)**: Community Roblox Studio MCP fork with per-peer execute_luau and additional tools.
- **[mcp-roblox-docs](https://github.com/n4tivex/mcp-roblox-docs)**: Roblox API reference at runtime. `uvx mcp-roblox-docs`
- **[mcp-server-tree-sitter](https://github.com/wrale/mcp-server-tree-sitter)**: Code analysis, dependency graphs, symbol search.
- **[luau-lsp](https://github.com/JohnnyMorganz/luau-lsp)**: Expose Luau type checking, diagnostics, and completions to your AI agent via MCP. Catches type errors before runtime.

## Contributors

- **[MrFearTick](https://github.com/MrFearTick)**: Code references, networking + monetization expansion

## Contributing

PRs welcome. Good contributions:
- Fix incorrect API references or deprecated patterns
- Add high-value patterns from production games
- Expand reference code (must be MIT/Apache sourced or original)

Keep skills focused, non-overlapping, and practical. All skills must pass `validate_skills.py`.

## License

MIT
