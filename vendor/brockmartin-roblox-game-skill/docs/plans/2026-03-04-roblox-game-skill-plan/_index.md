# Implementation Plan: Roblox Game Claude Code Skill

**Date:** 2026-03-04
**Design:** [Design Document](../2026-03-04-roblox-game-skill-design.md)
**Target:** `/Users/brockmartin/.claude/skills/roblox-game/`

---

## Goal

Implement the `roblox-game` Claude Code skill — a 30-file Router + Reference Library skill that serves as the ultimate Roblox game development companion with MCP Studio integration, genre templates, guided workflows, and deep reference knowledge.

## Constraints

- SKILL.md must stay under 200 lines (router only, no heavy content)
- Each reference file follows the standard structure: Overview, Core Concepts, Implementation Patterns, Best Practices, Anti-Patterns, Sharp Edges
- Each genre template follows: Genre Overview, Architecture Blueprint, Core Systems (Luau code), Progression Design, Monetization Strategy, Performance Considerations, Launch Checklist
- All Luau code must be production-ready, secure, and follow Roblox best practices
- MCP orchestration must support 3 modes (full/standard/offline) with graceful fallback
- Skill must be self-contained (no dependencies on game-design or game-monetization skills)

## Phases

### Phase 1: Foundation (Tasks 001-002)
Establish the skill directory and write the core SKILL.md router.

### Phase 2: Core References (Tasks 003-010)
Write the 8 foundational reference files that cover the essential Roblox development knowledge.

### Phase 3: Specialized References (Tasks 011-018)
Write the 8 specialized reference files covering systems, design, tooling, and sharp edges.

### Phase 4: Genre Templates (Tasks 019-025)
Write the universal scaffold and 6 genre-specific templates.

### Phase 5: Workflows (Tasks 026-032)
Write the 7 guided workflow files.

---

## Execution Plan

### Phase 1: Foundation
- [Task 001: Create skill directory structure](./task-001-create-directory-structure.md)
- [Task 002: Write SKILL.md router](./task-002-write-skill-router.md)

### Phase 2: Core References
- [Task 003: Write luau-mastery.md](./task-003-luau-mastery.md)
- [Task 004: Write architecture-patterns.md](./task-004-architecture-patterns.md)
- [Task 005: Write mcp-orchestration.md](./task-005-mcp-orchestration.md)
- [Task 006: Write security-hardening.md](./task-006-security-hardening.md)
- [Task 007: Write datastore-persistence.md](./task-007-datastore-persistence.md)
- [Task 008: Write gui-systems.md](./task-008-gui-systems.md)
- [Task 009: Write performance-optimization.md](./task-009-performance-optimization.md)
- [Task 010: Write monetization-systems.md](./task-010-monetization-systems.md)

### Phase 3: Specialized References
- [Task 011: Write combat-systems.md](./task-011-combat-systems.md)
- [Task 012: Write inventory-systems.md](./task-012-inventory-systems.md)
- [Task 013: Write game-design-roblox.md](./task-013-game-design-roblox.md)
- [Task 014: Write tooling-ecosystem.md](./task-014-tooling-ecosystem.md)
- [Task 015: Write animation-vfx.md](./task-015-animation-vfx.md)
- [Task 016: Write multiplayer-networking.md](./task-016-multiplayer-networking.md)
- [Task 017: Write testing-patterns.md](./task-017-testing-patterns.md)
- [Task 018: Write sharp-edges.md](./task-018-sharp-edges.md)

### Phase 4: Genre Templates
- [Task 019: Write game-scaffold.md](./task-019-game-scaffold.md)
- [Task 020: Write genre-simulator.md](./task-020-genre-simulator.md)
- [Task 021: Write genre-tycoon.md](./task-021-genre-tycoon.md)
- [Task 022: Write genre-obby.md](./task-022-genre-obby.md)
- [Task 023: Write genre-rpg.md](./task-023-genre-rpg.md)
- [Task 024: Write genre-horror.md](./task-024-genre-horror.md)
- [Task 025: Write genre-battle-royale.md](./task-025-genre-battle-royale.md)

### Phase 5: Workflows
- [Task 026: Write new-game.md workflow](./task-026-workflow-new-game.md)
- [Task 027: Write debug-loop.md workflow](./task-027-workflow-debug-loop.md)
- [Task 028: Write performance-audit.md workflow](./task-028-workflow-performance-audit.md)
- [Task 029: Write security-audit.md workflow](./task-029-workflow-security-audit.md)
- [Task 030: Write publish-checklist.md workflow](./task-030-workflow-publish-checklist.md)
- [Task 031: Write monetization-audit.md workflow](./task-031-workflow-monetization-audit.md)
- [Task 032: Write code-review.md workflow](./task-032-workflow-code-review.md)

---

## Dependency Graph

```
Task 001 (directory) ──┬── Task 002 (SKILL.md)
                       │
                       ├── Tasks 003-010 (core refs, all parallel)
                       │
                       ├── Tasks 011-018 (specialized refs, all parallel)
                       │
                       ├── Tasks 019-025 (genre templates, all parallel)
                       │
                       └── Tasks 026-032 (workflows, all parallel)
```

**Key dependency:** Task 001 is the only blocker. All other tasks (002-032) depend only on Task 001 and can run in parallel. Task 002 (SKILL.md) should be written first to establish the routing contract, but is not a technical blocker for reference/template/workflow files.

## Parallelization Strategy

- **Max parallelism:** Tasks 003-032 are all independent and can be executed by parallel agents
- **Recommended batches:** Group by phase for review checkpoints
- **Phase 1:** Sequential (001 → 002)
- **Phases 2-5:** All tasks within and across phases can run in parallel
