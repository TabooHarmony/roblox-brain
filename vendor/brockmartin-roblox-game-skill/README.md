# roblox-game — Claude Code Skill

The ultimate Roblox game development Claude Code skill. A self-contained, full-lifecycle development companion that serves all skill levels with deep Luau expertise, autonomous game building via MCP Studio integration, and comprehensive knowledge of game design, monetization, security, and performance optimization.

## Stats

- **31 files** | **30,677 lines** | **1.0 MB**
- 121-line SKILL.md router with lazy-loaded references
- 3-mode MCP Studio integration (full/standard/offline)

## Architecture

**Router + Reference Library** — lightweight SKILL.md dispatcher with lazy-loaded deep knowledge.

```
roblox-game/
├── SKILL.md                    # Router (121 lines, 18 routing paths)
├── references/                 # 16 deep reference files
│   ├── luau-mastery.md
│   ├── architecture-patterns.md
│   ├── mcp-orchestration.md
│   ├── security-hardening.md
│   ├── datastore-persistence.md
│   ├── gui-systems.md
│   ├── performance-optimization.md
│   ├── monetization-systems.md
│   ├── combat-systems.md
│   ├── inventory-systems.md
│   ├── game-design-roblox.md
│   ├── tooling-ecosystem.md
│   ├── animation-vfx.md
│   ├── multiplayer-networking.md
│   ├── testing-patterns.md
│   └── sharp-edges.md
├── templates/                  # 7 game templates
│   ├── game-scaffold.md        # Universal base (any genre)
│   ├── genre-simulator.md      # Pet Simulator style
│   ├── genre-tycoon.md         # Retail Tycoon style
│   ├── genre-obby.md           # Tower of Hell style
│   ├── genre-rpg.md            # Blox Fruits style
│   ├── genre-horror.md         # Doors style
│   └── genre-battle-royale.md  # Battle royale style
└── workflows/                  # 7 guided workflows
    ├── new-game.md             # Build a game from scratch
    ├── debug-loop.md           # Iterative MCP debugging
    ├── performance-audit.md    # Performance profiling
    ├── security-audit.md       # Security review
    ├── publish-checklist.md    # Pre-publish verification
    ├── monetization-audit.md   # Revenue optimization
    └── code-review.md          # Code quality review
```

## Features

### MCP Studio Integration (3 Modes)

| Mode | Server | Tools | Capabilities |
|------|--------|-------|-------------|
| **Full** | boshyxd/robloxstudio-mcp | 39 | Project exploration, autonomous building, iterative debugging, bulk ops, Creator Store |
| **Standard** | Roblox/studio-rust-mcp-server | 6 | Code execution, model insertion, console reading, play mode control |
| **Offline** | None | 0 | Pure Luau code generation with placement instructions |

Auto-detects which server is available and adapts all workflows accordingly.

### Genre Templates

Each template includes complete, production-ready Luau code for every core system:

- **Simulator** — Collection, pet system (hatching + rarity), zones, upgrades, prestige/rebirth
- **Tycoon** — Plot claiming, droppers/collectors, button pad purchasing, income, tiers
- **Obby** — Checkpoints, 5 obstacle types, timer/speedrun, leaderboards
- **RPG** — Character stats + leveling, quest system, NPC AI, dialog trees, zones
- **Horror** — Atmosphere control, monster AI (5-state FSM), event sequencer, jumpscares, flashlight
- **Battle Royale** — Match lifecycle, shrinking storm, loot spawning, elimination tracking, spectator

### Guided Workflows

- **New Game** — Build a complete game from a description in 8 steps
- **Debug Loop** — Iterative error detection and fixing (max 5 attempts)
- **Performance Audit** — Part count, script, memory, and network analysis
- **Security Audit** — RemoteEvent validation, client trust, data exposure review
- **Publish Checklist** — 60+ item pre-launch verification across 10 categories
- **Monetization Audit** — GamePass, DevProduct, Premium, and Ad optimization
- **Code Review** — A-F quality rating with specific fixes

### Deep References

16 reference files covering every aspect of Roblox development:
- Luau language mastery with type system and OOP patterns
- Game architecture (services, client-server, modules, frameworks)
- Security hardening (never trust client, validation, rate limiting)
- DataStore persistence (ProfileService, session locking, migration)
- And 12 more specialized topics

### Sharp Edges

12 severity-rated gotchas that save you from disaster (Critical → Low):
- DataStore data loss, client-side currency, ProcessReceipt bugs
- Memory leaks, RemoteEvent flooding, BindToClose timeout
- And 6 more common pitfalls with Luau code fixes

## Usage

The skill is automatically invoked when you mention Roblox, Luau, game development, or any related keyword in Claude Code.

**Example prompts:**
- "Build me a pet simulator with 3 zones"
- "How do I save player data in Roblox?"
- "Review my game's security"
- "Optimize this game for mobile"
- "Add a shop system with GamePasses"

## Installation

Already installed at `~/.claude/skills/roblox-game/`. The skill is detected automatically by Claude Code.

## Design Documents

See `docs/plans/` for the full design document and 32-task implementation plan.
