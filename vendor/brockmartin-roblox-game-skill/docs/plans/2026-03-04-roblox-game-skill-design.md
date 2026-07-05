# Roblox Game Skill — Design Document

**Date:** 2026-03-04
**Status:** Approved
**Skill Name:** `roblox-game`

---

## Vision

Build the ultimate Roblox game development Claude Code skill — a self-contained, full-lifecycle development companion that serves all skill levels (beginner to expert) with deep Luau expertise, autonomous game building via MCP Studio integration, and comprehensive knowledge of game design, monetization, security, and performance optimization.

## Target Users

Universal — progressive complexity serving all levels:
- **Beginners:** Guided workflows, templates, clear explanations
- **Intermediate:** Architecture patterns, best practices, genre blueprints
- **Expert:** Performance optimization, security hardening, advanced patterns, MCP automation

## Key Design Decisions

1. **Architecture:** Router + Reference Library (Approach B) — lightweight SKILL.md dispatcher with lazy-loaded references
2. **Self-contained:** No dependencies on other skills (game-design, game-monetization). All knowledge is inline.
3. **MCP Integration:** Support both official Roblox MCP server (6 tools) and community server (39 tools) with graceful fallback to offline mode
4. **Genre Support:** Router pattern with lazy-loaded genre-specific templates
5. **Full Lifecycle:** Architecture → Code → Design → Monetization → Optimization → Testing → Deployment

---

## Architecture

### File Structure (30 files)

```
roblox-game/
├── SKILL.md                              # ~200 lines, router/dispatcher
├── references/
│   ├── luau-mastery.md                   # Luau language deep dive
│   ├── architecture-patterns.md          # Game structure, services, modules
│   ├── mcp-orchestration.md              # MCP Studio integration (3 modes)
│   ├── security-hardening.md             # Anti-exploit, server validation
│   ├── datastore-persistence.md          # DataStore, ProfileService, session locking
│   ├── gui-systems.md                    # UI/UX, ScreenGui, BillboardGui, tweens
│   ├── performance-optimization.md       # Memory, parts, scripts, mobile
│   ├── monetization-systems.md           # GamePasses, DevProducts, Ads, DevEx
│   ├── combat-systems.md                 # Hitboxes, state machines, WCS
│   ├── inventory-systems.md              # Items, trading, storage patterns
│   ├── game-design-roblox.md             # Core loops, retention, genre theory
│   ├── tooling-ecosystem.md              # Rojo, Wally, Selene, StyLua, Git
│   ├── animation-vfx.md                  # Animation, particles, Trail, Beam
│   ├── multiplayer-networking.md         # Matchmaking, lobbies, TeleportService
│   ├── testing-patterns.md              # TestEZ, MCP testing, CI/CD
│   └── sharp-edges.md                    # Severity-rated critical gotchas
├── templates/
│   ├── game-scaffold.md                  # Universal base game structure
│   ├── genre-simulator.md                # Simulator architecture + code
│   ├── genre-tycoon.md                   # Tycoon architecture + code
│   ├── genre-obby.md                     # Obby architecture + code
│   ├── genre-rpg.md                      # RPG architecture + code
│   ├── genre-horror.md                   # Horror architecture + code
│   └── genre-battle-royale.md            # Battle royale architecture + code
└── workflows/
    ├── new-game.md                       # Build a game from scratch
    ├── debug-loop.md                     # Iterative MCP debugging
    ├── performance-audit.md              # Performance profiling workflow
    ├── security-audit.md                 # Security review workflow
    ├── publish-checklist.md              # Pre-publish verification
    ├── monetization-audit.md             # Revenue optimization review
    └── code-review.md                    # Code quality review
```

### SKILL.md Design (~200 lines)

The router contains:
1. **Identity/Philosophy** — Expert Roblox developer persona
2. **MCP Detection** — Auto-detect which MCP server is available (full/standard/offline)
3. **Routing Table** — Map user intent to reference/template/workflow files
4. **Core Quick Reference** — Top 20% of knowledge covering 80% of use cases
5. **Sharp Edges Summary** — Top 5 critical gotchas always visible

### Routing Logic

| User Intent | Loaded Files |
|---|---|
| "Build a simulator/tycoon/RPG..." | `workflows/new-game.md` + `templates/genre-{type}.md` + `templates/game-scaffold.md` |
| "Fix this bug" / debugging | `workflows/debug-loop.md` + `references/mcp-orchestration.md` |
| "How do I save data?" | `references/datastore-persistence.md` |
| "Make combat system" | `references/combat-systems.md` + `references/security-hardening.md` |
| "Add a shop/gamepass" | `references/monetization-systems.md` + `references/gui-systems.md` |
| "Optimize performance" | `workflows/performance-audit.md` + `references/performance-optimization.md` |
| "Security review" | `workflows/security-audit.md` + `references/security-hardening.md` |
| "Set up Rojo/external tools" | `references/tooling-ecosystem.md` |
| General Luau question | `references/luau-mastery.md` |
| Game design question | `references/game-design-roblox.md` |
| Ready to publish | `workflows/publish-checklist.md` |
| Review monetization | `workflows/monetization-audit.md` |
| Review code quality | `workflows/code-review.md` |
| Animation/VFX | `references/animation-vfx.md` |
| Multiplayer/networking | `references/multiplayer-networking.md` |
| Testing | `references/testing-patterns.md` |

---

## MCP Integration Design

### Three Modes

**Mode: `full`** — Community Server (boshyxd/robloxstudio-mcp, 39 tools)
- Full project exploration (file tree, script grep, object search)
- Autonomous building (execute Luau, create/import builds)
- Iterative debugging (playtest → console → fix → repeat)
- Bulk operations (mass property changes, object creation)
- Creator Store integration (search, insert models)
- Undo/redo support

**Mode: `standard`** — Official Server (Roblox/studio-rust-mcp-server, 6 tools)
- Code execution via `run_code`
- Model insertion via `insert_model`
- Console reading via `get_console_output`
- Play mode control via `start_stop_play`
- Test scripts via `run_script_in_play_mode`
- State checking via `get_studio_mode`

**Mode: `offline`** — No MCP
- Pure Luau code generation with placement instructions
- Copy-paste ready code blocks
- Step-by-step manual instructions
- Rojo-compatible file structure output

### MCP Detection

On skill invocation:
1. Check available MCP tools in tool list
2. Detect community server tools (39 tools) → `full` mode
3. Detect official server tools (6 tools) → `standard` mode
4. No MCP tools detected → `offline` mode
5. All workflows adapt behavior based on mode

### Autonomous Build Workflow (MCP modes)

```
User: "Build me a pet simulator with 3 zones"
  1. Scaffold game structure via MCP
  2. Generate and insert core systems (DataStore, pet system, zones, GUI)
  3. Start playtest via MCP
  4. Read console output for errors
  5. Fix errors and re-test (iterate until clean)
  6. Report summary of what was built + next steps
```

---

## Reference File Content Design

### Content Structure (each reference follows):
1. Overview (when to use this reference)
2. Core Concepts (essentials)
3. Implementation Patterns (with full Luau code)
4. Best Practices
5. Anti-Patterns (what NOT to do)
6. Sharp Edges (gotchas specific to this topic)

### Genre Template Structure (each template follows):
1. Genre Overview (what makes it work, core loop)
2. Architecture Blueprint (folder structure, key modules)
3. Core Systems (full Luau code for each system)
4. Progression Design (leveling, unlocks, zones)
5. Monetization Strategy (genre-appropriate passes/products)
6. Performance Considerations (genre-specific bottlenecks)
7. Launch Checklist (genre-specific pre-publish items)

### Sharp Edges System

Severity-rated gotchas following established pattern:
- **SE-1 (Critical):** DataStore data loss from improper session handling
- **SE-2 (Critical):** Client-side currency manipulation (never trust client)
- **SE-3 (High):** Memory leaks from undisconnected event listeners
- **SE-4 (High):** RemoteEvent flooding / DDoS
- **SE-5 (Medium):** Part count explosion on mobile
- **SE-6 (Medium):** Yielding in module require chains

---

## Workflow Designs

### 1. `workflows/new-game.md`
Guided game creation from scratch:
1. Detect/ask genre → load genre template
2. Ask about scope (MVP vs full vision)
3. Generate architecture blueprint
4. MCP: scaffold in Studio / Offline: output files
5. Generate core systems one by one
6. MCP: playtest and iterate / Offline: provide instructions
7. Summary + next steps

### 2. `workflows/debug-loop.md`
Iterative debugging:
1. Gather error info (user or MCP console)
2. MCP: grep scripts for relevant code / Offline: ask user
3. Root cause analysis
4. Generate fix
5. MCP: apply + playtest + verify / Offline: provide fix
6. Iterate until resolved

### 3. `workflows/performance-audit.md`
Performance profiling:
1. MCP: scan project structure / Offline: ask for MicroProfiler data
2. Check for common bottlenecks
3. MCP: grep for anti-patterns
4. Generate prioritized optimization list
5. Apply fixes or provide code
6. Re-test and measure

### 4. `workflows/security-audit.md`
Security review:
1. MCP: scan all RemoteEvents/RemoteFunctions
2. Check server-side validation on each remote
3. Identify client-trusted logic
4. Check for exploit vulnerabilities
5. Generate hardened code
6. Verify no sensitive data exposed

### 5. `workflows/publish-checklist.md`
Pre-publish verification checklist covering DataStore, security, mobile compat, monetization, metadata, analytics.

### 6. `workflows/monetization-audit.md`
Revenue optimization:
1. Review GamePass/DevProduct offerings
2. Analyze pricing strategy
3. Check for missing monetization opportunities
4. Evaluate premium payout eligibility
5. Review ad placement (Rewarded Video Ads)
6. Generate recommendations

### 7. `workflows/code-review.md`
Code quality review:
1. Scan for code smells and anti-patterns
2. Check naming conventions and organization
3. Validate module architecture
4. Flag security issues
5. Check for memory leaks
6. Rate overall quality with actionable feedback

---

## Technical Stack Reference

### Roblox Development
- **Language:** Luau (Lua 5.1 derivative with types, performance enhancements)
- **IDE:** Roblox Studio
- **External Tooling:** Rojo (filesystem sync), Wally (package manager), Selene (linter), StyLua (formatter)
- **Frameworks:** Knit (services/controllers), ProfileService (data persistence), TestEZ (testing)
- **MCP Servers:** Official (Roblox/studio-rust-mcp-server), Community (boshyxd/robloxstudio-mcp)

### Key Roblox Services
- Players, Workspace, ReplicatedStorage, ServerStorage, ServerScriptService
- TweenService, RunService, UserInputService, ContextActionService
- DataStoreService, MarketplaceService, TeleportService, MessagingService

---

## Success Criteria

1. **Completeness:** Covers every major aspect of Roblox game development
2. **Token Efficiency:** SKILL.md stays under 200 lines; references lazy-loaded
3. **MCP Integration:** Seamless experience across all three modes
4. **Code Quality:** All generated Luau code is production-ready, secure, and follows best practices
5. **Universality:** Useful for beginners (guided workflows) through experts (deep references)
6. **Autonomy:** Can build a complete game from a description in MCP mode
7. **Genre Coverage:** 6 genre blueprints with full architecture and code
