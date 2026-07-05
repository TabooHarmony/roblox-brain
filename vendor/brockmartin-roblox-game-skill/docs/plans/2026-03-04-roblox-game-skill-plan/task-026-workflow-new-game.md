# Task 026: Write new-game.md Workflow

**depends-on:** 001
**phase:** 5 - Workflows
**files:** `workflows/new-game.md`

## Description

Write the guided game creation workflow — the flagship workflow that walks users through building a complete game from scratch.

## What To Do

1. **Step 1: Genre Detection** — Detect genre from user message or ask via multiple choice (Simulator, Tycoon, Obby, RPG, Horror, Battle Royale, Custom)
2. **Step 2: Load Genre Template** — Instructions to load `templates/game-scaffold.md` + `templates/genre-{type}.md`
3. **Step 3: Scope Definition** — Ask user: MVP (core loop only) vs Full Vision (all systems). Adjust complexity accordingly
4. **Step 4: Architecture Generation** — Generate the folder structure and module list based on genre + scope
5. **Step 5: Scaffold** — MCP mode: Create Instance tree in Studio via execute_luau. Offline mode: Output file structure with instructions
6. **Step 6: Core Systems** — Generate each core system one at a time. After each, in MCP mode: insert and test. In offline mode: output code
7. **Step 7: Integration Test** — MCP mode: Start playtest, check console, fix errors, iterate. Offline mode: Provide testing checklist
8. **Step 8: Summary** — List everything built, suggest next steps (polish, monetization, more content)

Each step must have clear MCP/offline branching.

## Verification

- File exists at `workflows/new-game.md`
- All 8 steps documented
- MCP and offline paths for every step
- Genre detection handles all 6 genres + custom
- Step-by-step is actionable and unambiguous
