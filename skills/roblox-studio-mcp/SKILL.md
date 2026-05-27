---
name: roblox-studio-mcp
description: >
  Official Roblox Studio MCP server tools reference. What each tool does, how to use it,
  reliability patterns, and workflows for script editing, building, playtesting, and debugging.
  Use when the AI has an MCP connection to Roblox Studio.
last_reviewed: 2026-05-27
---

# Roblox Studio MCP

The official Roblox Studio MCP server is built into Studio. It provides direct access to the data model, script editing, code execution, asset generation, and playtesting. This skill documents every tool and the patterns for using them reliably.

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
| `generate_mesh` | Generate a textured 3D mesh from a description. |
| `generate_material` | Generate a custom material or texture. |
| `generate_procedural_model` | Generate procedural models that scale and adapt automatically. |
| `insert_from_creator_store` | Insert assets, plugins, and models from the Creator Store. |

### Data Model Exploration

| Tool | What it does |
|------|-------------|
| `explore_subagent` | Investigate the place in parallel, returns a compact summary. |
| `search_game_tree` | Explore instance hierarchy as flat JSON. Filter by path, type, keywords. |
| `inspect_instance` | Detailed info about a specific instance: properties, attributes, children summary. |

### Luau Execution

| Tool | What it does |
|------|-------------|
| `execute_luau` | Run Luau code in Studio. Returns result or error. |

### Playtesting

| Tool | What it does |
|------|-------------|
| `start_stop_play` | Start or stop playtesting. |
| `console_output` | Retrieve output logs while the game is running. |
| `screen_capture` | Capture the current Studio viewport in Play mode. |
| `playtest_subagent` | Spawn a test character that runs through gameplay scenarios. |

### Player Input Simulation

| Tool | What it does |
|------|-------------|
| `character_navigation` | Move the player character to a position or instance. |
| `keyboard_input` | Simulate key presses, holds, and text input. |
| `mouse_input` | Simulate mouse clicks, movement, and scrolling. |

### Session Management

| Tool | What it does |
|------|-------------|
| `list_roblox_studios` | List all connected Studio instances (name, ID, active status). |
| `set_active_studio` | Set which Studio instance receives subsequent tool calls. |

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

When writing scripts via `multi_edit` or `execute_luau` with `script.Source = ...`, long scripts may silently truncate. For scripts over ~300 lines:

1. Split into logical chunks
2. Write each chunk separately using string concatenation
3. After writing, read back the last 10-20 lines to verify no truncation

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

## Workflows

### Script Development

1. **Explore** — Use `search_game_tree` to understand existing structure
2. **Read** — Use `script_read` to understand existing code before modifying
3. **Write** — Use `multi_edit` to create or modify scripts
4. **Verify** — Use `script_read` to confirm the write succeeded
5. **Test** — Use `start_stop_play` + `console_output` to test

### Building Geometry

1. **Plan** — Use `search_game_tree` to see what exists
2. **Build** — Use `execute_luau` to create parts (see roblox-building skill)
3. **Verify** — Use `execute_luau` to count parts and check properties
4. **Visual check** — Use `screen_capture` in play mode to see the result

### Debugging

1. **Reproduce** — `start_stop_play` to enter play mode
2. **Observe** — `console_output` to read errors/warnings
3. **Inspect** — `inspect_instance` or `execute_luau` to check runtime state
4. **Fix** — `multi_edit` to patch the script
5. **Retest** — `start_stop_play` again

### Playtesting

1. Start play mode with `start_stop_play`
2. Navigate with `character_navigation`
3. Interact with `keyboard_input` / `mouse_input`
4. Observe with `console_output` and `screen_capture`
5. Stop with `start_stop_play`

## MCP Mode Detection

Different MCP servers provide different tool sets. Detect what's available:

- **Official Roblox MCP** (built into Studio): `execute_luau`, `multi_edit`, `script_read`, `search_game_tree`, `start_stop_play`, `generate_mesh`, etc.
- **Community MCP** (Chrrxs/robloxstudio-mcp): `execute_luau`, `get_file_tree`, `grep_scripts`, `create_build`, plus per-peer execution.
- **No MCP**: Pure code generation only. Provide copy-paste-ready scripts.

Adapt your approach based on what tools are actually available. If a tool call fails with "not found", fall back gracefully.

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

Quick connect supports: Codex CLI, Claude Code, Claude Desktop, Cursor, Gemini CLI, VS Code.
