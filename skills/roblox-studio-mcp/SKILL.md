---
name: roblox-studio-mcp
description: "Use when working with Roblox Studio through built-in MCP for scripts, data-model inspection, Luau, assets, input, or playtesting."
last_reviewed: 2026-05-27
sources:
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/studio/mcp.md
---

# Roblox Studio MCP

## When to Load

Load when working with Roblox Studio via its built-in MCP server — script editing, scene building, playtesting, or debugging. Provides direct access to the data model, Luau execution, asset generation, and player simulation tools. Skip if generating standalone scripts without a Studio connection.

## Quick Reference

**Tools by category:**
- **Scripts:** `script_read`, `multi_edit`, `script_search`, `script_grep`
- **Data model:** `search_game_tree`, `inspect_instance`, `subagent`
- **Execute:** `execute_luau` (stateless — re-acquire refs every call)
- **Playtest:** `get_studio_state`, `start_stop_play`, `get_console_output`, `screen_capture`
- **Input sim:** `character_navigation`, `user_keyboard_input`, `user_mouse_input`
- **Assets:** `generate_mesh`, `generate_material`, `generate_procedural_model`, `wait_job_finished`, `search_asset`, `insert_asset`, `upload_image`, `store_image`
- **Docs:** `http_get`, `skill`
- **Session:** `list_roblox_studios`, `set_active_studio`

**Critical reliability patterns:**
1. `execute_luau` is stateless — re-acquire all references every call
2. Silent failures — verify after creation (`FindFirstChild` check)
3. Script truncation — chunk writes for >300 lines; read back to verify
4. Batching — 10-20 parts/call safe, one script/call, verify after batches
5. Ground truth — never guess coords/sizes; always READ current state

**Core workflows:**
- **Script dev:** `search_game_tree` → `script_read` → `multi_edit` → `script_read` (verify) → `start_stop_play` + `get_console_output`
- **Build geometry:** `search_game_tree` → `execute_luau` (create) → `execute_luau` (verify count) → `screen_capture`
- **Debug:** `start_stop_play` → `get_console_output` → `inspect_instance` → `multi_edit` → `start_stop_play`
- **Playtest:** `start_stop_play` → `character_navigation` → `user_keyboard_input`/`user_mouse_input` → `get_console_output` + `screen_capture`

**MCP mode detection:**
- **Official** (built-in): use the current tool catalog exposed by Studio, including `execute_luau`, `multi_edit`, and `search_game_tree`
- **Other MCP:** inspect the tools actually exposed by the connected server; do not assume the official names are available
- **No MCP**: pure code generation — provide copy-paste-ready scripts

> Full tool descriptions, code examples, and setup instructions: [references/full.md](references/full.md)
