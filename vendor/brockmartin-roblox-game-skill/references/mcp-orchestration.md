# MCP Studio Integration Reference

## Overview

Load this reference whenever performing any of the following:

- **MCP operations** — executing Luau code, reading/writing instances, managing assets via MCP tools
- **Autonomous building** — scaffolding game structure, generating systems, iterating on builds
- **Debugging via Studio** — reading console output, tracing errors, applying fixes in-place
- **Project exploration** — understanding an existing place file's architecture and script layout

This reference defines how Claude detects, selects, and orchestrates MCP tools to drive Roblox Studio directly.

---

## MCP Detection

On every session start or when Studio interaction is requested, detect which MCP server is available by probing for characteristic tool names.

### Community Server (boshyxd/robloxstudio-mcp)

**Detect by looking for these tools:** `execute_luau`, `get_file_tree`, `grep_scripts`, `create_build`, `search_objects`, `get_instance_properties`, `get_script_source`

If any of these tools are present, operate in **Full Mode** (39 tools).

### Official Server (Roblox/studio-rust-mcp-server)

**Detect by looking for these tools:** `run_code`, `insert_model`, `get_console_output`, `start_stop_play`, `run_script_in_play_mode`, `get_studio_mode`

If these tools are present but community tools are not, operate in **Standard Mode** (6 tools).

### No MCP Tools Detected

If neither server's tools are available, operate in **Offline Mode** — generate copy-paste Luau code and filesystem structures instead.

### Detection Priority

If both servers are detected, prefer the **Community Server** for its broader toolset. Fall back to individual Official Server tools only when a community equivalent is unavailable or failing.

---

## Full Mode (Community Server — 39 Tools)

### Exploration

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `get_file_tree` | Returns the full instance hierarchy of the place | First step in any project exploration; understanding overall structure |
| `get_project_structure` | Returns a higher-level structural overview | Quick orientation before diving into specifics |
| `search_objects` | Find instances by name or class across the tree | Locating specific parts, models, scripts, or UI elements |
| `get_instance_properties` | Read all properties of a specific instance | Inspecting configuration, checking values before modification |
| `get_instance_children` | List direct children of an instance | Navigating the hierarchy incrementally |
| `grep_scripts` | Search across all scripts for a pattern | Finding references, tracing function calls, locating bugs |
| `get_script_source` | Read the full source of a specific script | Understanding implementation before editing |
| `search_by_property` | Find instances matching a property value | Locating all anchored parts, all red-colored bricks, etc. |
| `get_class_info` | Get Roblox API info for a class | Checking available properties/methods before writing code |
| `get_selection` | Get the currently selected instance(s) in Studio | Context-aware operations on what the user has selected |

### Building

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `execute_luau` | Run arbitrary Luau code inside Studio | The primary workhorse — create instances, modify properties, run any logic |
| `create_build` | Generate a structured build from a specification | Scaffolding rooms, maps, or complex instance trees from a plan |
| `import_build` | Import a previously exported build | Restoring saved structures or applying templates |
| `export_build` | Export a subtree to a reusable format | Saving work for reuse, creating templates, backing up before changes |
| `import_scene` | Import a complete scene definition | Loading pre-built environments or level layouts |

### Testing

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `start_playtest` | Begin a playtest session in Studio | Validating changes, testing gameplay, triggering runtime behavior |
| `stop_playtest` | End the current playtest session | After gathering output or when done testing |
| `get_playtest_output` | Read console/output from the playtest | Checking for errors, reading print statements, validating behavior |

### Assets (Creator Store)

| Tool | Purpose | When to Use |
|------|---------|-------------|
| Creator Store `search` | Search the Creator Store for models, audio, etc. | Finding assets to populate a scene |
| Creator Store `details` | Get metadata for a specific asset | Checking asset info before insertion |
| Creator Store `thumbnail` | Get the thumbnail/preview image of an asset | Visual verification before inserting |
| Creator Store `insert` | Insert an asset from the Creator Store into the place | Adding models, meshes, audio, images, etc. |
| Creator Store `preview` | Preview an asset before committing to insertion | Evaluating suitability |

### History

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `undo` | Undo the last change via ChangeHistoryService | Rolling back a mistake, reverting after a failed experiment |
| `redo` | Redo a previously undone change | Re-applying a reverted change |

### Bulk Operations

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `mass_get_property` | Read a property from many instances at once | Auditing values across the place (e.g., all part sizes) |
| Batch operations | Execute multiple related changes in sequence | Bulk renaming, bulk property updates, mass restructuring |

---

## Standard Mode (Official Server — 6 Tools)

When only the official Roblox MCP server is available, operate with this reduced but capable toolset.

| Tool | Purpose | Notes |
|------|---------|-------|
| `run_code` | Execute Lua/Luau code inside Studio | Equivalent to `execute_luau` — primary workhorse |
| `insert_model` | Insert a model from the Creator Store | Takes an asset ID; inserts into Workspace by default |
| `get_console_output` | Read Studio's output/console log | Use for error detection and debug loops |
| `start_stop_play` | Toggle playtest mode on/off | Single tool handles both start and stop |
| `run_script_in_play_mode` | Execute code during an active playtest | Automatically stops the playtest when the script finishes |
| `get_studio_mode` | Check whether Studio is in Edit or Play mode | Always call before mode-sensitive operations |

### Standard Mode Workflow Adaptations

Since Standard Mode lacks exploration tools (`get_file_tree`, `grep_scripts`, etc.), compensate by:

- Using `run_code` with scripts that traverse the DataModel and return structure as printed output
- Reading `get_console_output` to capture the results of exploratory scripts
- Building instance-search logic inline via `run_code` instead of relying on `search_objects`

Example — exploring structure in Standard Mode:

```lua
-- Run via run_code to mimic get_file_tree
local function printTree(instance, indent)
    indent = indent or 0
    print(string.rep("  ", indent) .. instance.ClassName .. ": " .. instance.Name)
    for _, child in ipairs(instance:GetChildren()) do
        printTree(child, indent + 1)
    end
end
printTree(game)
```

Then read the output via `get_console_output`.

---

## Offline Mode

When no MCP server is connected, generate self-contained Luau code blocks that the user can copy-paste into Studio manually.

### Script Output Format

Always include clear placement instructions:

```
-- ==============================================
-- SCRIPT: WeaponSystem
-- PLACE IN: ServerScriptService
-- TYPE: Script (server-side)
-- ==============================================

local WeaponSystem = {}
-- ... implementation ...
return WeaponSystem
```

### For Rojo Users

When the user mentions Rojo, Wally, or a filesystem-based workflow, output a directory structure:

```
src/
├── server/
│   ├── WeaponSystem.server.luau
│   └── DataManager.server.luau
├── client/
│   ├── InputHandler.client.luau
│   └── UIController.client.luau
├── shared/
│   ├── Constants.luau
│   └── Utils.luau
└── default.project.json
```

Include the `default.project.json` mapping when creating new projects or restructuring existing ones.

### Offline Conventions

- Label every script block with its target service/folder
- Use `ModuleScript`, `Script`, or `LocalScript` type annotations
- Group related scripts together with a section header
- Provide a setup checklist at the end listing manual steps (e.g., "Create a RemoteEvent named 'DamageEvent' in ReplicatedStorage")

---

## Orchestration Patterns

### Autonomous Build

A full build cycle from specification to working game systems.

```
1. SCAFFOLD
   ├── get_file_tree / get_project_structure  →  understand current state
   ├── Plan instance hierarchy based on requirements
   └── create_build / execute_luau  →  create folder structure and placeholder instances

2. GENERATE CORE SYSTEMS
   ├── For each system (e.g., combat, inventory, UI):
   │   ├── Generate server scripts  →  execute_luau to create and populate Script instances
   │   ├── Generate client scripts  →  execute_luau to create and populate LocalScript instances
   │   └── Generate shared modules  →  execute_luau to create and populate ModuleScript instances
   └── Wire up RemoteEvents/RemoteFunctions between client and server

3. INSERT ASSETS
   ├── Search Creator Store for needed models/audio
   └── Insert and position assets in the scene

4. TEST
   ├── start_playtest
   ├── get_playtest_output  →  read console for errors
   └── stop_playtest

5. FIX & ITERATE
   ├── grep_scripts to find error source
   ├── get_script_source to read the problematic script
   ├── execute_luau to apply the fix
   └── Return to step 4 (max 5 iterations)
```

### Debug Loop

Systematic error resolution with bounded retries.

```
1. DETECT
   ├── get_console_output / get_playtest_output  →  capture errors
   └── Parse error messages for script name, line number, error type

2. LOCATE
   ├── grep_scripts with error-related keywords
   ├── get_script_source for the identified script
   └── Analyze surrounding code for root cause

3. FIX
   ├── Generate corrected code
   ├── execute_luau to replace the script source
   └── Create an undo waypoint before applying

4. VERIFY
   ├── start_playtest (or re-run the specific code path)
   ├── get_playtest_output  →  check if error persists
   └── stop_playtest

5. ITERATE OR REPORT
   ├── If error persists and attempts < 5  →  return to step 2
   ├── If error resolved  →  report success
   └── If attempts >= 5  →  report findings and suggest manual investigation
```

### Bulk Modification

Safe large-scale changes across many instances.

```
1. SEARCH
   ├── search_objects / search_by_property  →  identify all targets
   └── mass_get_property  →  read current values for audit

2. PLAN
   ├── Review the list of affected instances
   ├── Confirm the change is correct (log count and sample values)
   └── Create undo waypoint via execute_luau:
       game:GetService("ChangeHistoryService"):SetWaypoint("Before bulk edit")

3. EXECUTE
   ├── execute_luau with a loop over all targets
   └── Apply changes in batches if count > 100

4. VERIFY
   ├── mass_get_property  →  confirm new values
   ├── Spot-check a few instances via get_instance_properties
   └── Report: "Changed X instances, verified Y samples"
```

### Project Exploration

Understanding an unfamiliar place file.

```
1. STRUCTURE
   ├── get_file_tree  →  full hierarchy
   └── get_project_structure  →  high-level layout

2. SCRIPTS
   ├── Identify all scripts via search_objects (ClassName = "Script" / "LocalScript" / "ModuleScript")
   ├── get_script_source for key scripts (main systems, entry points)
   └── grep_scripts for patterns like "require", "RemoteEvent", "BindableEvent"

3. ARCHITECTURE
   ├── Map module dependencies (who requires whom)
   ├── Map client-server communication (RemoteEvents/Functions)
   └── Identify data flow (DataStores, player data, state management)

4. REPORT
   └── Summarize: services used, script count, system architecture, potential issues
```

---

## Safety Guidelines

### Pre-Operation Checks

1. **Check Studio mode** before any operation — call `get_studio_mode` (Official) or infer from context (Community). Do not execute build code while a playtest is active.
2. **Create undo waypoints** before any bulk or destructive operation:
   ```lua
   game:GetService("ChangeHistoryService"):SetWaypoint("Before: <description>")
   ```
3. **Read before write** — always inspect a script's current source before overwriting it.
4. **Verify instance existence** before modifying — check that the target path resolves to a real instance.

### Destructive Operation Safeguards

- **Deleting instances**: Always confirm with the user before calling `:Destroy()` on named or significant instances. Deleting anonymous/temporary parts is fine without confirmation.
- **Overwriting scripts**: Log the previous source (or at least its length and key function names) before replacing.
- **Clearing containers**: Never call `:ClearAllChildren()` on services (Workspace, ServerScriptService, etc.) without explicit user confirmation.

### Playtest Safety

- Do not run `execute_luau` / `run_code` to modify the DataModel while a playtest is active — changes will be lost when the playtest ends.
- Use `run_script_in_play_mode` (Official) for runtime testing during play mode.
- Always `stop_playtest` before applying fixes discovered during testing.

---

## Best Practices

### Batch Related Operations

Group related reads and writes to minimize round-trips:

```lua
-- Instead of 5 separate execute_luau calls:
local part1 = workspace:FindFirstChild("Part1")
local part2 = workspace:FindFirstChild("Part2")
local part3 = workspace:FindFirstChild("Part3")
part1.BrickColor = BrickColor.new("Bright red")
part2.BrickColor = BrickColor.new("Bright red")
part3.BrickColor = BrickColor.new("Bright red")
```

### Read Before Write

Always understand the current state before making changes:

```
1. get_script_source("ServerScriptService.GameManager")
2. Analyze the existing code
3. execute_luau to apply targeted modifications (not blind overwrites)
```

### Verify After Modify

Confirm that changes took effect:

```
1. execute_luau  →  make the change
2. get_instance_properties  →  confirm the new value
   OR
3. start_playtest  →  confirm runtime behavior
```

### Use Undo Waypoints Strategically

Create waypoints at meaningful boundaries, not after every micro-change:

- Before a batch of related changes (one waypoint for "Add combat system")
- Before experimental changes that might need rollback
- Before any operation the user might want to undo as a unit

---

## Anti-Patterns

### Running Code Without Checking Studio State

**Wrong:**
```
execute_luau("workspace.Part.Position = Vector3.new(0, 10, 0)")
-- Might fail if Studio is in Play mode and Part doesn't exist in the play DataModel
```

**Right:**
```
1. get_studio_mode  →  confirm Edit mode
2. execute_luau(...)
```

### Bulk Changes Without Undo Points

**Wrong:**
```
execute_luau("for _, v in workspace:GetDescendants() do if v:IsA('Part') then v:Destroy() end end")
-- No way to recover
```

**Right:**
```
1. execute_luau: ChangeHistoryService:SetWaypoint("Before cleanup")
2. execute_luau: perform the bulk delete
3. Verify results
```

### Assuming Tool Availability

**Wrong:**
```
-- Calling grep_scripts when only the Official server is connected
-- Tool will not be found; operation fails
```

**Right:**
```
1. Detect which server is available (see MCP Detection above)
2. Use only the tools confirmed to exist
3. Fall back to run_code + get_console_output workarounds in Standard Mode
```

### Blind Script Overwrites

**Wrong:**
```
execute_luau: set script.Source to entirely new code without reading the original
-- Loses existing work, custom modifications, comments
```

**Right:**
```
1. get_script_source  →  read current implementation
2. Understand what exists
3. Merge new logic with existing code or confirm full replacement with user
```

### Ignoring Error Output

**Wrong:**
```
1. execute_luau(code)
2. Assume success and move on
```

**Right:**
```
1. execute_luau(code)
2. Check return value / output for errors
3. If error: enter Debug Loop pattern
```
