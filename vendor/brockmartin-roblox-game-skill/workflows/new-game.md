# Workflow: New Game Creation

## Overview

This is the guided workflow for building a complete Roblox game from scratch. It walks the user through genre selection, scoping, architecture, scaffolding, core system generation, integration testing, and a final summary with next steps.

**Trigger:** User wants to build a new game, create a game, or start a project.

**Prerequisites:** MCP mode must already be detected per SKILL.md (Full, Standard, or Offline).

---

## Step 1: Genre Detection

Attempt to detect the game genre automatically from the user's message. If detection fails, ask via multiple choice.

### Keyword Matching

Scan the user's message for these keywords (case-insensitive). Match the first genre that hits:

| Genre | Keywords |
|---|---|
| Simulator | simulator, sim, clicking, rebirth, prestige, idle, grind, farm |
| Tycoon | tycoon, factory, build, base, dropper, conveyor, empire |
| Obby | obby, obstacle, parkour, jump, platformer, tower, stages |
| RPG | rpg, quest, adventure, dungeon, story, level up, class, mmorpg, open world |
| Horror | horror, scary, escape, survive, monster, fear, dark, haunted |
| Battle Royale | battle royale, pvp, arena, fight, last standing, deathmatch, shooter, fps |

### If Detected

Confirm with the user:

> I detected **{Genre}** from your description. I will use the {Genre} template to structure your game. Does that sound right, or would you prefer a different genre?

Proceed to Step 2 on confirmation.

### If Not Detected

Present a multiple-choice prompt:

> What type of game are you building?
>
> 1. **Simulator** -- Click, collect, upgrade, rebirth loops
> 2. **Tycoon** -- Build a base/factory, earn currency, expand
> 3. **Obby** -- Obstacle course with stages/checkpoints
> 4. **RPG** -- Quests, combat, leveling, story-driven adventure
> 5. **Horror** -- Atmospheric scares, survival, escape scenarios
> 6. **Battle Royale** -- PvP combat, last player/team standing
> 7. **Custom** -- I have something unique in mind (describe it)

If the user selects **Custom**, skip genre-specific templates in Step 2 and use only the universal scaffold. Gather a short description of their concept to inform architecture decisions.

---

## Step 2: Load Genre Template

Load the appropriate template files based on the detected genre.

### Always Load

Read `templates/game-scaffold.md` -- this contains the universal base structure that every game needs:
- Folder hierarchy (ServerScriptService, ReplicatedStorage, etc.)
- DataManager boilerplate
- Remote event setup
- Loading screen
- Core configuration module

### Genre-Specific Load

Read the genre template based on the detected type:

| Genre | Template File |
|---|---|
| Simulator | `templates/genre-simulator.md` |
| Tycoon | `templates/genre-tycoon.md` |
| Obby | `templates/genre-obby.md` |
| RPG | `templates/genre-rpg.md` |
| Horror | `templates/genre-horror.md` |
| Battle Royale | `templates/genre-battle-royale.md` |
| Custom | No genre template -- use only the scaffold |

### What to Extract

From the loaded templates, identify:
- **Core systems** -- the modules that define this genre's gameplay
- **Required RemoteEvents** -- client-server communication channels
- **Data schema** -- what player data needs to be saved
- **UI screens** -- what ScreenGuis are needed
- **Workspace layout** -- what the 3D world needs (spawn points, arenas, stages, etc.)

---

## Step 3: Scope Definition

Ask the user to choose the project scope. This determines how many systems to build and how polished the output will be.

### Prompt

> How much do you want to build right now?
>
> **A) MVP (Minimum Viable Product)**
> Core gameplay loop only. I will build the 3-5 essential systems that make the game playable. No monetization, minimal UI, no polish. Great for prototyping and testing your concept fast.
>
> **B) Full Vision**
> Complete game with all systems: core loop, monetization (game passes, dev products), polished UI, settings, leaderboards, mobile support, and content. This takes longer but produces a shippable game.

### Scope Adjustments

**MVP scope includes:**
- DataManager (save/load)
- 1-2 genre-defining systems (e.g., Simulator: ClickSystem + RebirthSystem)
- Basic HUD (currency display, core stats)
- RemoteEvent wiring
- Minimal Workspace setup

**Full Vision adds:**
- All genre systems from the template
- MonetizationManager (game passes, developer products, receipt processing)
- Complete UI suite (shop, settings, inventory, leaderboards)
- Mobile input support
- Loading screen with asset preloading
- Sound/music system
- Admin commands (optional)
- Anti-cheat basics (rate limiting, server validation)

Store the scope choice for use in Steps 4-6.

---

## Step 4: Architecture Generation

Generate the complete project architecture based on genre + scope. Present it to the user for approval before building.

### Output Format

Present a structured plan with:

1. **Folder structure** -- the full Instance hierarchy that will be created
2. **Script manifest** -- every Script, LocalScript, and ModuleScript with:
   - Name
   - Type (Script / LocalScript / ModuleScript)
   - Location (which service/folder)
   - One-line description of its purpose
3. **RemoteEvent list** -- every RemoteEvent/RemoteFunction with direction and purpose
4. **Data schema** -- the player data structure that will be saved/loaded

### Example Architecture Output

```
=== PROJECT ARCHITECTURE: Simulator Game (MVP) ===

FOLDER STRUCTURE:
game
+-- ServerScriptService
|   +-- Main (Script) -- bootstrapper, requires and inits all server modules
|   +-- Services/
|       +-- DataManager (ModuleScript) -- save/load player data via ProfileService pattern
|       +-- ClickService (ModuleScript) -- handle click actions, calculate earnings
|       +-- RebirthService (ModuleScript) -- prestige/rebirth logic and rewards
+-- ReplicatedStorage
|   +-- Remotes/
|   |   +-- ClickAction (RemoteEvent) -- client -> server: player clicked
|   |   +-- RebirthRequest (RemoteEvent) -- client -> server: rebirth request
|   |   +-- UpdateStats (RemoteEvent) -- server -> client: send updated stats
|   +-- Modules/
|   |   +-- Constants (ModuleScript) -- shared game constants
|   |   +-- Types (ModuleScript) -- shared type definitions
+-- StarterGui
|   +-- HUD (ScreenGui)
|       +-- HUDController (LocalScript) -- update currency/stats display
+-- StarterPlayer
|   +-- StarterPlayerScripts
|       +-- ClientMain (LocalScript) -- client bootstrapper, input handling
+-- Workspace
    +-- SpawnLocation
    +-- ClickArea (Part) -- where players click to earn

SCRIPT MANIFEST:
1. Main               | Script       | ServerScriptService      | Bootstrapper: requires and initializes all services
2. DataManager        | ModuleScript | ServerScriptService/Services | Player data save/load with session locking
3. ClickService       | ModuleScript | ServerScriptService/Services | Processes clicks, calculates earnings with multipliers
4. RebirthService     | ModuleScript | ServerScriptService/Services | Handles rebirth: checks requirements, resets, grants bonuses
5. Constants          | ModuleScript | ReplicatedStorage/Modules    | Shared constants (base earnings, rebirth costs, etc.)
6. Types              | ModuleScript | ReplicatedStorage/Modules    | Shared Luau type definitions
7. HUDController      | LocalScript  | StarterGui/HUD               | Listens for stat updates, renders currency/multiplier display
8. ClientMain         | LocalScript  | StarterPlayerScripts         | Handles input, fires click events, manages client state

DATA SCHEMA:
{
    clicks: number,
    currency: number,
    rebirths: number,
    multiplier: number,
    lastSave: number,
}
```

### Ask for Approval

> Here is the architecture I will build. Review the script list and folder structure. Would you like to:
> - **Proceed** -- start building
> - **Add** something (describe what)
> - **Remove** something (tell me which script/system)
> - **Modify** the scope

Do not proceed to Step 5 until the user approves.

---

## Step 5: Scaffold

Create the folder structure and empty script instances in Studio (or output placement instructions for offline users).

### MCP Full Mode

Use `execute_luau` to create the entire Instance tree. Execute a single comprehensive script that:

1. Creates all Folders
2. Creates all Script/LocalScript/ModuleScript instances with placeholder sources
3. Creates all RemoteEvent/RemoteFunction instances
4. Sets up the Workspace layout (SpawnLocation, any genre-specific parts)

```lua
-- Example scaffold pattern for execute_luau:
game:GetService("ChangeHistoryService"):SetWaypoint("Before: Game Scaffold")

-- Create folder structure
local function ensureFolder(parent, name)
    local folder = parent:FindFirstChild(name)
    if not folder then
        folder = Instance.new("Folder")
        folder.Name = name
        folder.Parent = parent
    end
    return folder
end

local SSS = game:GetService("ServerScriptService")
local RS = game:GetService("ReplicatedStorage")

local services = ensureFolder(SSS, "Services")
local remotes = ensureFolder(RS, "Remotes")
local modules = ensureFolder(RS, "Modules")

-- Create scripts with placeholder source
local function createScript(className, name, parent, source)
    local s = Instance.new(className)
    s.Name = name
    s.Source = source or "-- TODO: " .. name
    s.Parent = parent
    return s
end

-- Create remotes
local function createRemote(name, className)
    local r = Instance.new(className or "RemoteEvent")
    r.Name = name
    r.Parent = remotes
    return r
end

-- ... create all instances per the architecture plan
```

After execution, verify the structure exists by calling `get_file_tree` or `search_objects`.

### MCP Standard Mode

Use `run_code` to create the same Instance tree. The approach is identical to Full Mode but uses `run_code` instead of `execute_luau`. After execution, verify by running a tree-print script via `run_code` and reading `get_console_output`.

```lua
-- Verification script for Standard Mode (run via run_code):
local function printTree(instance, indent)
    indent = indent or 0
    print(string.rep("  ", indent) .. instance.ClassName .. ": " .. instance.Name)
    for _, child in ipairs(instance:GetChildren()) do
        printTree(child, indent + 1)
    end
end
printTree(game:GetService("ServerScriptService"))
printTree(game:GetService("ReplicatedStorage"))
printTree(game:GetService("StarterGui"))
printTree(game:GetService("StarterPlayer"))
```

Then read `get_console_output` to confirm the structure matches the plan.

### Offline Mode

Output the complete folder structure with explicit placement instructions using the offline script format from `references/mcp-orchestration.md`:

```
=== SCAFFOLD INSTRUCTIONS ===

Create the following hierarchy in Roblox Studio.
For each item, right-click the parent -> Insert Object -> select the type shown.

1. ServerScriptService
   +-- Services (Folder)
       +-- DataManager (ModuleScript)
       +-- ClickService (ModuleScript)
       +-- RebirthService (ModuleScript)
   +-- Main (Script)

2. ReplicatedStorage
   +-- Remotes (Folder)
       +-- ClickAction (RemoteEvent)
       +-- RebirthRequest (RemoteEvent)
       +-- UpdateStats (RemoteEvent)
   +-- Modules (Folder)
       +-- Constants (ModuleScript)
       +-- Types (ModuleScript)

3. StarterGui
   +-- HUD (ScreenGui) [set ResetOnSpawn = false]
       +-- HUDController (LocalScript)

4. StarterPlayer > StarterPlayerScripts
   +-- ClientMain (LocalScript)

5. Workspace
   +-- SpawnLocation (SpawnLocation)
```

Include a note: "Create all instances first. I will provide the code for each script in the next step."

---

## Step 6: Core Systems

Generate each core system one at a time, in dependency order. Always start with DataManager since most other systems depend on it.

### Generation Order

Follow this dependency chain:

1. **Constants / Types** (shared modules, no dependencies)
2. **DataManager** (depends on Constants for schema defaults)
3. **Genre-specific systems** (depend on DataManager for reading/writing player data)
4. **Client scripts** (depend on Remotes and shared modules)
5. **UI controllers** (depend on Remotes and client infrastructure)
6. **Main bootstrapper** (requires and initializes all server modules)

### Per-System Process

For each system:

#### MCP Full Mode

1. Generate the complete Luau source code for the module
2. Use `execute_luau` to set the script's Source property:
   ```lua
   local script = game:GetService("ServerScriptService").Services.DataManager
   script.Source = [=[
       -- full module source here
   ]=]
   ```
3. Check the `execute_luau` return for errors
4. If errors, fix the code and re-apply
5. Confirm success before moving to the next system

#### MCP Standard Mode

1. Generate the complete Luau source code
2. Use `run_code` to set the script's Source property (same pattern as Full Mode)
3. Read `get_console_output` to check for any immediate errors
4. Fix and re-apply if needed
5. Confirm success before moving to the next system

#### Offline Mode

Output each system as a complete, copy-paste-ready code block with the standard header format:

```
-- ==============================================
-- SCRIPT: DataManager
-- PLACE IN: ServerScriptService > Services
-- TYPE: ModuleScript
-- DEPENDENCIES: Constants
-- ==============================================

local DataManager = {}
-- ... full implementation ...
return DataManager
```

After outputting each system, briefly explain what it does and how it connects to other systems.

### Code Quality Requirements

Every generated system must follow these rules (from SKILL.md and references):

- **Never trust the client** -- all validation server-side
- **Use pcall for DataStore operations** -- handle failures gracefully
- **Use task library** -- `task.wait()`, `task.spawn()`, `task.delay()` (never deprecated `wait()`)
- **Disconnect events on cleanup** -- store connections, disconnect on player removal
- **Type annotations** -- use Luau types on function signatures
- **Rate limiting** -- server-side cooldowns on all RemoteEvent handlers
- **No circular dependencies** -- use the init() pattern if modules need cross-references

---

## Step 7: Integration Test

After all systems are built, run an integration test to verify the game works end-to-end.

### MCP Full Mode

Execute the following test loop (max 5 attempts):

```
ATTEMPT 1 of 5:

1. start_playtest
2. Wait 5-10 seconds for initialization
3. get_playtest_output
4. Parse output for errors:
   - "error" or "Error" -- runtime errors
   - "attempt to index nil" -- missing references
   - "Infinite yield possible" -- WaitForChild timeouts
   - "is not a valid member" -- API misuse
   - "ServerScriptService.Main:X: ..." -- script-specific errors
5. stop_playtest

IF errors found:
   - Identify the failing script and line number
   - get_script_source for the failing script
   - Generate a fix
   - execute_luau to apply the fix
   - Return to step 1 (next attempt)

IF no errors:
   - Report success
   - Proceed to Step 8
```

If all 5 attempts are exhausted with unresolved errors:
- Report what was fixed and what remains broken
- Provide the error messages and suspected causes
- Suggest manual investigation steps

### MCP Standard Mode

Same loop as Full Mode, adapted for Standard tools:

```
ATTEMPT 1 of 5:

1. get_studio_mode -- confirm we are in Edit mode
2. start_stop_play -- start playtest
3. Wait 5-10 seconds
4. get_console_output -- capture errors
5. start_stop_play -- stop playtest

IF errors found:
   - Use run_code to read the failing script source:
     print(game:GetService("ServerScriptService").Services.DataManager.Source)
   - Read get_console_output for the printed source
   - Generate a fix
   - run_code to apply the fix
   - Return to step 1 (next attempt)

IF no errors:
   - Report success
   - Proceed to Step 8
```

### Offline Mode

Provide a manual testing checklist the user can follow in Studio:

```
=== INTEGRATION TEST CHECKLIST ===

After inserting all scripts into Studio, run a playtest (F5) and verify:

[ ] Game starts without errors in the Output window
[ ] Player data initializes correctly (check Output for DataManager logs)
[ ] Core gameplay loop works:
    [ ] {genre-specific action} produces the expected result
    [ ] Currency/stats update correctly on screen
    [ ] {genre-specific progression} triggers at the right threshold
[ ] Rejoin test: leave and rejoin -- data persists correctly
[ ] No "Infinite yield possible" warnings in Output
[ ] No "attempt to index nil" errors in Output

COMMON ISSUES & FIXES:

1. "X is not a valid member of Y"
   -> A child instance is missing. Check that all Remotes and Folders exist.
   -> Use WaitForChild() instead of direct indexing for replicated instances.

2. "attempt to index nil with 'Connect'"
   -> A RemoteEvent was not created. Check ReplicatedStorage > Remotes.

3. "Infinite yield possible on WaitForChild"
   -> The instance name does not match. Check spelling and capitalization.

4. Data not saving
   -> Studio does not persist DataStore data between sessions by default.
   -> Enable "Enable Studio Access to API Services" in Game Settings > Security.
```

---

## Step 8: Summary

After successful testing (or after providing the offline checklist), present a complete summary of everything built.

### Summary Format

```
=== BUILD COMPLETE: {Genre} Game ({Scope}) ===

SYSTEMS BUILT:
1. DataManager         -- Player data persistence with session locking
2. {System2}           -- {one-line description}
3. {System3}           -- {one-line description}
...

SCRIPTS CREATED: {count}
- Server Scripts: {count}
- Client Scripts: {count}
- Shared Modules: {count}

REMOTE EVENTS: {count}
- {list each with direction and purpose}

DATA SCHEMA:
{the player data structure}

FEATURES WORKING:
- {list each working feature}
```

### Suggested Next Steps

Based on the scope and genre, suggest 4-6 concrete next steps. Tailor suggestions to what was NOT built:

**If MVP scope, suggest:**
- Add monetization (game passes for multipliers, developer products for currency)
- Polish UI (animations, better layouts, mobile-friendly sizing)
- Add more content (items, levels, areas, enemies)
- Add a leaderboard (OrderedDataStore-based)
- Add sound effects and music
- Add mobile input support (touch buttons, gesture controls)

**If Full Vision scope, suggest:**
- Optimize for mobile (reduce part count, test on low-end devices)
- Add analytics (track retention, monetization, progression)
- Set up automated testing (TestEZ specs for core logic)
- Create a content pipeline (easy way to add new items/levels)
- Run a security audit (load `workflows/security-audit.md`)
- Prepare for publishing (load `workflows/publish-checklist.md`)

### Close with Routing

Remind the user they can invoke other workflows:

> Your game is built. Here is what you can do next:
> - "Add a shop system" -- I will load the monetization references
> - "Debug an error" -- I will enter the debug loop
> - "Review security" -- I will run a security audit
> - "Optimize performance" -- I will run a performance audit
> - "Prepare to publish" -- I will walk through the publish checklist

---

## Mode Reference Quick Card

Use this to quickly determine tool usage at each step:

| Step | Full Mode | Standard Mode | Offline Mode |
|---|---|---|---|
| 1. Genre | Conversation | Conversation | Conversation |
| 2. Templates | Read template files | Read template files | Read template files |
| 3. Scope | Conversation | Conversation | Conversation |
| 4. Architecture | Conversation | Conversation | Conversation |
| 5. Scaffold | `execute_luau` + `get_file_tree` | `run_code` + `get_console_output` | Output placement instructions |
| 6. Core Systems | `execute_luau` per script | `run_code` per script | Output code blocks |
| 7. Test | `start_playtest` + `get_playtest_output` + `stop_playtest` | `start_stop_play` + `get_console_output` | Manual checklist |
| 8. Summary | Conversation | Conversation | Conversation |
