# Roblox Studio MCP — Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

The official Roblox Studio MCP server is built into Studio. It provides direct access to the data model, script editing, code execution, asset generation, and playtesting.

## Available Tools

### Scripts

| Tool | What it does |
|------|-------------|
| `script_read` | Read scripts by dot-notation path (e.g. `game.ServerScriptService.MyScript`). Supports line ranges. |
| `multi_edit` | Apply multiple edits to a script. Creates the script if the path doesn't exist. |
| `script_search` | Fuzzy search for scripts by name. Returns up to 10 results. |
| `script_grep` | Search for a string pattern across all scripts. Returns up to 50 matches. |

### Asset & Content Generation

| Tool | What it does |
|------|-------------|
| `generate_mesh` | Generate a textured 3D mesh from a description. Inspect the returned result before placement. |
| `generate_material` | Generate a material variant; apply the returned base material and variant name to parts. |
| `generate_procedural_model` | Generate a configurable primitive-part model, optionally from a reference image URI per the official procedural-models docs. |
| `wait_job_finished` | Wait on a returned generation ID when a dependent action needs completion. |
| `search_asset` / `search_creator_store` | Search Creator Store or creator inventory, depending on the bridge. |
| `insert_asset` / `insert_from_creator_store` | Insert a known asset ID or Creator Store result. |
| `upload_image` | Upload permitted images from a bridge-supported source, such as documented HTTP URLs, and return asset references. |
| `store_image` | Convert a permitted local image into a URI for another generation tool. |

### Data Model Exploration

| Tool | What it does |
|------|-------------|
| `subagent` | Launch a specialized exploration or playtest subagent. |
| `search_game_tree` | Explore instance hierarchy as flat JSON. Filter by path, type, keywords. |
| `inspect_instance` | Detailed info about a specific instance: properties, attributes, children summary. |

### Luau Execution

| Tool | What it does |
|------|-------------|
| `execute_luau` | Run Luau code in Studio. Returns result or error. |

### Playtesting

| Tool | What it does |
|------|-------------|
| `get_studio_state` | Get Studio play state and available data-model contexts. |
| `start_stop_play` | Start or stop playtesting. |
| `get_console_output` | Retrieve output logs while the game is running. |
| `screen_capture` | Capture a Studio viewport. Edit-mode capture was verified on the connected bridge; some bridges may hang or time out in Play mode, so keep a CUA screenshot fallback. |

### Player Input Simulation

| Tool | What it does |
|------|-------------|
| `character_navigation` | Move the player character to a position or instance. |
| `user_keyboard_input` | Simulate key presses, holds, and text input. |
| `user_mouse_input` | Simulate mouse clicks, movement, and scrolling. |

### Session Management

| Tool | What it does |
|------|-------------|
| `list_roblox_studios` | List all connected Studio instances (name, ID, active status). |
| `set_active_studio` | Set which Studio instance receives subsequent tool calls. |

## Session and Datamodel Contract

1. Call `list_roblox_studios` before assuming Studio is connected.
2. Use `set_active_studio` with the returned ID when more than one instance exists or the active flag is not the intended target.
3. Call `get_studio_state` and record the current mode plus available datamodels.
4. Select `Edit` for persistent tree/script changes. Use `Client` or `Server` only for operations whose live schema permits them.
5. Inspect the relevant tree and scripts before mutation. After mutation, read back the script, instance, or asset result.

`datamodel_type` is not universal. The live server requires it for some datamodel-scoped calls, while session management, play control, and some inspection tools expose different schemas. Inspect `tools/list` and the tool description instead of blindly adding or omitting it.

The connected server exposed the official `search_asset`/`insert_asset` names. Other bridges may use `search_creator_store`/`insert_from_creator_store` or another mapping. Treat these as capability mappings, not guaranteed simultaneous tools.

### Observed live schema notes (2026-07-12)

<!-- temporal: 2026-07-12 -->

These were verified against the connected Studio server and must be rechecked when the bridge updates:

- `execute_luau`: `code` plus `datamodel_type` for `Edit`, `Client`, or `Server` where supported.
- `multi_edit`: `file_path`, optional `className` when creating, and ordered `edits` using `old_string`/`new_string`.
- `start_stop_play`: `is_start`; it does not use an `action` string.
- `screen_capture`: `capture_id` is required; camera position/look-at are optional.
- `wait_job_finished`: `generationId` is required; use it before dependent edits when generation is asynchronous.
- `search_asset`: query is optional; useful filters include `scope`, `assetType`, `maxResults`, price/source filters, and verified-creator filtering.
- `insert_asset`: `assetId` is required; `assetName`, `assetType`, and `parentPath` are optional but improve deterministic placement.
- `get_console_output`, `list_roblox_studios`, and `set_active_studio` expose their own schemas rather than a universal datamodel argument.

### Documentation and Skills

| Tool | What it does |
|------|-------------|
| `http_get` | Fetch allowed Roblox documentation pages. |
| `skill` | Retrieve detailed guidance for supported Roblox skills. |

## MCP Reliability Patterns

### Statelessness

`execute_luau` is stateless. Every call is a blank slate. Variables and references do not persist between calls.

```luau
-- ALWAYS re-acquire references at the start of every execute_luau call
local model = workspace:FindFirstChild("MyModel")
if not model then
    model = Instance.new("Model")
    model.Name = "MyModel"
    model.Parent = workspace
end
```

### Silent Failures

`execute_luau` may return success even when objects weren't created (parent doesn't exist, name collision, etc). Always verify after creation:

```luau
-- Create then verify
local part = Instance.new("Part")
part.Name = "Floor"
part.Parent = workspace.MapRoot

-- Verify it exists
local check = workspace.MapRoot:FindFirstChild("Floor")
print(check and "OK" or "FAILED: Floor not created")
```

### Script Truncation

When writing scripts via `multi_edit` or `execute_luau` with `script.Source = ...`, the connected bridge has an observed command-code limit around 4-5 KB as of 2026-07-12. This is bridge-specific, not an official Roblox limit; recheck after bridge updates. For larger modules:

1. Split into logical chunks or write the module with `multi_edit`
2. Execute only a short `require()` or test call
3. Read back the tail to verify no truncation

```luau
-- Chunked write pattern
local s = game.ServerScriptService.MyScript
local part1 = [=[
-- chunk 1: services and config
local Players = game:GetService("Players")
...
]=]
local part2 = [=[
-- chunk 2: main logic
...
]=]
s.Source = part1 .. part2
```

### Batching

- **Part creation**: 10-20 parts per call (safe), 25-50 with loops (risky)
- **Script writes**: one script per call for reliability
- **Property changes**: batch related changes in one call
- **Verification**: always verify after creation batches

### Ground Truth Rule

Never guess coordinates, sizes, or property values from chat history. If you need current state, READ it:

```luau
local part = workspace.MapRoot:FindFirstChild("Tower")
if part then
    print("Position:", part.Position)
    print("Size:", part.Size)
    print("CFrame:", part.CFrame)
end
```

## Asset Generation Workflow

Use this order for a map or prop:

1. Inspect the project for an existing compatible asset and its conventions.
2. Search the Creator Store or creator inventory when reuse is appropriate. Record the asset ID, type, source, price, and intended parent. For cross-owner or paid results, surface the creator/source and get explicit consent before insertion.
3. Use `generate_procedural_model` for configurable primitive-part props, buildings, scenery, or reference-image-driven blockouts. The live tool may insert the model automatically; inspect its returned result and workspace placement.
4. Use `generate_mesh` for a custom textured prop. Bound the requested size and triangle budget, then inspect the returned asset before using it in a player-facing scene.
5. Use `generate_material` for a surface variant. Apply its returned base material and variant name to the intended parts, then verify both properties.
6. Use `store_image` for a permitted local PNG/JPG reference, or `upload_image` for a permitted source accepted by the live schema. Pass the returned URI only to a tool whose live schema accepts it.
7. If a generation returns a job ID, call `wait_job_finished` with its `generationId` before dependent edits. Follow the tool's live description when it reports that generation is already complete or auto-inserted.
8. Parent and place the result explicitly, inspect its class, descendants, bounds, pivot, materials, collision, anchoring, and provenance, then capture evidence.

Generated content is a candidate, not an acceptance decision. Keep a native Parts/CSG fallback for unavailable, slow, rejected, or visually unsuitable generation. Never upload or publish an image or asset without permission and never claim a generated asset is production-ready without structural and visual review.

## Workflows

### Script Development

1. **Explore** — Use `search_game_tree` to understand existing structure
2. **Read** — Use `script_read` to understand existing code before modifying
3. **Write** — Use `multi_edit` to create or modify scripts
4. **Verify** — Use `script_read` to confirm the write succeeded
5. **Test** — Use `start_stop_play` + `get_console_output` to test

### Building Geometry

1. **Plan** — Inspect the existing tree, origin, map root, coordinate conventions, and current assets.
2. **Choose** — Reuse a compatible asset, generate a procedural model/mesh/material, or use native Parts/CSG as fallback.
3. **Build** — Use the asset tool or `execute_luau` in bounded phases; use `multi_edit` for persistent builder scripts.
4. **Verify** — Read back the model, counts, bounds, pivots, classes, materials, anchoring, collision, and parent paths.
5. **Evidence** — Capture a deliberate view when supported; otherwise report structural evidence and the capture limitation.

### Map and Prop Evidence

- **Prop:** named model, pivot, player scale, bounding box, materials, collision, anchoring, no loose parts, and asset provenance.
- **Map:** root/origin, zones, floors, landmarks, spawns, path widths, connected traversal, and excluded Baseplate/Terrain/SpawnLocation filters in bounds checks.
- **Runtime:** start play, navigate or interact, inspect console output, then stop play. Do not leave a test session running.

### Debugging

1. **Reproduce** — `start_stop_play` to enter play mode
2. **Observe** — `get_console_output` to read errors/warnings
3. **Inspect** — `inspect_instance` or `execute_luau` to check runtime state
4. **Fix** — `multi_edit` to patch the script
5. **Retest** — `start_stop_play` again

### Playtesting

1. Start play mode with `start_stop_play`
2. Navigate with `character_navigation`
3. Interact with `user_keyboard_input` / `user_mouse_input`
4. Observe with `get_console_output` and capture before or after Play when supported. If Play-mode capture times out, use the CUA screenshot fallback.
5. Stop with `start_stop_play`

## MCP Mode Detection

Different MCP servers expose different names and schemas. Call `tools/list` and route by capability:

- **Official docs baseline:** session selection, tree/script inspection, `multi_edit`, `execute_luau`, play control, console/visual evidence, input simulation, and generated/searchable assets.
- **Observed connected server (2026-07-12):** `search_asset`/`insert_asset`; other bridges may expose `search_creator_store`/`insert_from_creator_store`.
- **No MCP or missing capability:** generate complete offline Luau, identify the intended insertion path, and state exactly what was not inspected or tested.

If a call fails with "not found", an invalid context, a stale session, or an unavailable generation job, stop assuming the workflow succeeded. Re-discover state, choose a supported fallback, or report the blocker with the tool response.

## Setup Reference

### Windows
```json
{
  "mcpServers": {
    "Roblox_Studio": {
      "command": "cmd.exe",
      "args": ["/c", "%LOCALAPPDATA%\\Roblox\\mcp.bat"]
    }
  }
}
```

### macOS
```json
{
  "mcpServers": {
    "Roblox_Studio": {
      "command": "/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP"
    }
  }
}
```

### Enable in Studio
1. Open Assistant
2. Click ... > Manage MCP Servers
3. Turn on "Enable Studio as MCP server"

Quick connect supports: Antigravity, Codex CLI, Claude Code, Claude Desktop, Cursor, Gemini CLI, and Visual Studio Code.
