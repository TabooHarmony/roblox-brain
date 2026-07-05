# Task 005: Write mcp-orchestration.md

**depends-on:** 001
**phase:** 2 - Core References
**files:** `references/mcp-orchestration.md`

## Description

Write the MCP Studio integration reference — the killer feature that enables Claude to directly interact with Roblox Studio. Must cover all three modes and provide clear orchestration patterns.

## What To Do

1. **Overview** — When to load this reference (any MCP-related operation, autonomous building, debugging via Studio)
2. **MCP Detection** — Detailed instructions for detecting which server is available:
   - Community server (boshyxd/robloxstudio-mcp): look for tools like `get_file_tree`, `grep_scripts`, `execute_luau`, `create_build`
   - Official server (Roblox/studio-rust-mcp-server): look for `run_code`, `insert_model`, `get_console_output`, `start_stop_play`
   - No MCP tools: offline mode
3. **Full Mode (39 tools)** — Complete tool catalog organized by category:
   - Exploration: get_file_tree, get_project_structure, search_objects, get_instance_properties, get_instance_children, grep_scripts, get_script_source
   - Building: execute_luau, create_build, import_build, export_build
   - Testing: start_playtest, stop_playtest, get_playtest_output
   - Assets: search Creator Store, insert models
   - History: undo, redo
   - Bulk ops: mass property changes, batch operations
4. **Standard Mode (6 tools)** — Each tool with usage patterns: run_code, insert_model, get_console_output, start_stop_play, run_script_in_play_mode, get_studio_mode
5. **Offline Mode** — Code generation patterns: how to format output for copy-paste, Rojo file structure output, step-by-step manual instructions
6. **Orchestration Patterns** — Multi-step workflows:
   - Autonomous build: scaffold → generate → test → fix → iterate
   - Debug loop: console → grep → analyze → fix → retest
   - Bulk modification: search → plan → execute → verify
7. **Safety Guidelines** — Always check Studio mode before operations, use undo points before bulk changes, confirm destructive operations
8. **Best Practices** — Batch related operations, read before write, verify after modify
9. **Anti-Patterns** — Running code without checking Studio state, making bulk changes without undo points, assuming tool availability

## Verification

- File exists at `references/mcp-orchestration.md`
- All 3 modes documented with specific tool names
- Community server's 39 tools categorized
- Official server's 6 tools detailed
- At least 3 orchestration patterns with step-by-step flows
- Safety guidelines included
