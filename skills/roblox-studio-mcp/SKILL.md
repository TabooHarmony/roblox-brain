---
name: roblox-studio-mcp
description: Studio MCP server tools, execute_luau, script_read/multi_edit, reliability patterns, workflows.
last_reviewed: 2026-05-27
sources:
  - https://github.com/MaximumADHD/Roblox-Client-Tracker
  - https://github.com/Roblox/creator-docs
---

# Roblox Studio MCP

## When to Load

Load when working with Roblox Studio via its built-in MCP server — script editing, scene building, playtesting, or debugging. Provides direct access to the data model, Luau execution, asset generation, and player simulation tools. Skip if generating standalone scripts without a Studio connection.

## Quick Reference

**Tools by category:**
- **Scripts:** `script_read`, `multi_edit`, `script_search`, `script_grep`
- **Data model:** `search_game_tree`, `inspect_instance`, `explore_subagent`
- **Execute:** `execute_luau` (stateless — re-acquire refs every call)
- **Playtest:** `start_stop_play`, `console_output`, `screen_capture`, `playtest_subagent`
- **Input sim:** `character_navigation`, `keyboard_input`, `mouse_input`
- **Assets:** `generate_mesh`, `generate_material`, `generate_procedural_model`, `insert_from_creator_store`
- **Session:** `list_roblox_studios`, `set_active_studio`

**Critical reliability patterns:**
1. `execute_luau` is stateless — re-acquire all references every call
2. Silent failures — verify after creation (`FindFirstChild` check)
3. Script truncation — chunk writes for >300 lines; read back to verify
4. Batching — 10-20 parts/call safe, one script/call, verify after batches
5. Ground truth — never guess coords/sizes; always READ current state

**Core workflows:**
- **Script dev:** `search_game_tree` → `script_read` → `multi_edit` → `script_read` (verify) → `start_stop_play` + `console_output`
- **Build geometry:** `search_game_tree` → `execute_luau` (create) → `execute_luau` (verify count) → `screen_capture`
- **Debug:** `start_stop_play` → `console_output` → `inspect_instance` → `multi_edit` → `start_stop_play`
- **Playtest:** `start_stop_play` → `character_navigation` → `keyboard_input`/`mouse_input` → `console_output` + `screen_capture`

**MCP mode detection:**
- **Official** (built-in): full tool set including `execute_luau`, `multi_edit`, `search_game_tree`
- **Community** (Chrrxs): `execute_luau`, `get_file_tree`, `grep_scripts`, `create_build`
- **No MCP**: pure code generation — provide copy-paste-ready scripts

> Full tool descriptions, code examples, and setup instructions: [references/full.md](references/full.md)
