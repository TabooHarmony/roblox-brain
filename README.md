# roblox-brain

Give your AI coding agent a Roblox brain.

Curated skills that make AI assistants competent at Roblox/Luau game development. Works with Codex, Claude Code, OpenCode, Cursor, or anything that supports agent skills.

## Install

```bash
# all skills
npx skills add TabooHarmony/roblox-brain

# one skill
npx skills add TabooHarmony/roblox-brain --skill roblox-building
```

Or just copy any `SKILL.md` into your project's skill directory (`.claude/skills/`, `.opencode/skills/`, `.cursor/skills/`, etc).

## Skills

### Core

| Skill | What it does |
|-------|-------------|
| `roblox-luau-mastery` | Luau language fundamentals, type system, OOP, deprecation table, error patterns |
| `roblox-architecture` | Service hierarchy, 7 foundational patterns, client-server architecture, module patterns |
| `roblox-sharp-edges` | 12 production footguns ranked by severity. Data loss, exploits, memory leaks, mobile perf |
| `roblox-runtime` | StreamingEnabled, performance optimization, memory management, object pooling, mobile targets |

### Systems

| Skill | What it does |
|-------|-------------|
| `roblox-networking` | Server-authoritative networking, RemoteEvent validation, rate limiting, exploit prevention |
| `roblox-data` | DataStores, ProfileStore, session locking, data persistence patterns |
| `roblox-monetization` | ProcessReceipt correctness, prompt APIs, purchase reconciliation, session-lock interaction |
| `roblox-analytics` | AnalyticsService: custom events, economy tracking, funnels, rate limits, event taxonomy |

### Building

| Skill | What it does |
|-------|-------------|
| `roblox-building` | Build 3D objects and maps via MCP. CSG patterns, spatial coordination, player scale, platform quirks, validation |
| `roblox-gui` | GUI systems, layout, responsiveness, cross-platform UI. ScreenGuis, UIListLayout, constraint-based design |
| `roblox-animation-vfx` | Animations, particles, tweens, ContentProvider, visual effects |

### Workflow

| Skill | What it does |
|-------|-------------|
| `roblox-debug` | Iterative debug loop for Luau/Roblox issues |
| `roblox-code-review` | Code review with security, performance, and monetization lenses |
| `roblox-publish-checklist` | Pre-publish verification gauntlet |

## Recommended MCP Servers

These aren't required but they make the AI significantly better at Roblox work:

- **[robloxstudio-mcp](https://github.com/Chrrxs/robloxstudio-mcp)** — Execute Luau in Studio, inspect instance trees, read/write properties. The AI can directly interact with your game.
- **[mcp-roblox-docs](https://github.com/BusyCityGuy/mcp-roblox-docs)** — Roblox API reference at runtime. The AI queries class docs instead of guessing at stale properties. `uvx mcp-roblox-docs`
- **[mcp-server-tree-sitter](https://github.com/nicobailon/mcp-server-tree-sitter)** — Code analysis, dependency graphs, symbol search. Structural understanding of your project without reading every file.
- **[duckduckgo-mcp-server](https://github.com/nickclyde/duckduckgo-mcp-server)** — Web search + content fetch. DevForum solutions, asset references, code patterns. `uvx duckduckgo-mcp-server`

## What this is NOT

This is not a plugin, not a package manager, not a framework. It's just markdown files that teach AI agents how to write good Roblox code. The skills contain patterns, rules, references, and .luau examples that the AI loads on demand.

## Contributing

PRs welcome. Good contributions:
- Fix incorrect API references or deprecated patterns
- Add high-value patterns from production games
- Expand reference code (must be MIT/Apache sourced or original)

Keep skills focused, non-overlapping, and practical.

## License

MIT
