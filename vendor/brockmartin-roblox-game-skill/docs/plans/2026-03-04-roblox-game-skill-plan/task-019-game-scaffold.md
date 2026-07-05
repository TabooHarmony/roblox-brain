# Task 019: Write game-scaffold.md

**depends-on:** 001
**phase:** 4 - Genre Templates
**files:** `templates/game-scaffold.md`

## Description

Write the universal base game scaffold template — the starting point for any Roblox game regardless of genre.

## What To Do

1. **Overview** — Universal game foundation applicable to all genres
2. **Folder Structure** — Standard game organization:
   - ServerScriptService/: GameManager, DataManager, RemoteHandlers
   - ServerStorage/: ItemDefinitions, MapAssets
   - ReplicatedStorage/: SharedModules, RemoteEvents folder, RemoteFunctions folder, Assets
   - StarterGui/: MainGui
   - StarterPlayer/StarterPlayerScripts/: ClientController
   - StarterPlayer/StarterCharacterScripts/: CharacterSetup
3. **Core Modules (Luau code for each):**
   - GameManager — Game lifecycle, initialization, state management
   - DataManager — Player data save/load using ProfileService pattern
   - RemoteManager — Centralized remote event creation and validation
   - ClientController — Client-side initialization and UI management
4. **Boilerplate Systems:**
   - Player join/leave handling
   - Leaderstats setup
   - Basic data save/load
   - Remote event structure
5. **MCP Scaffold Instructions** — How to create this structure via MCP (execute_luau commands to create the Instance tree)
6. **Manual Setup Instructions** — Step-by-step for Studio-only developers

All code must be production-ready, typed, and secure.

## Verification

- File exists at `templates/game-scaffold.md`
- Folder structure covers all standard Roblox services
- Core modules include complete Luau code
- Both MCP and manual setup paths documented
- Code uses type annotations and follows best practices
