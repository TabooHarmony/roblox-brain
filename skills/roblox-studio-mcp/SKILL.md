---
name: roblox-studio-mcp
description: "Use when working with Roblox Studio through built-in MCP for scripts, scenes, generated assets, input, or playtesting."
last_reviewed: 2026-07-12
sources:
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/studio/mcp.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/parts/procedural-models.md
  - https://create.roblox.com/docs/reference/engine/classes/ProceduralModel
---

# Roblox Studio MCP

## When to Load

Load when working with Roblox Studio through its MCP server: inspecting or editing scripts, building maps and props, generating or inserting assets, debugging, or playtesting. Skip for standalone code generation with no Studio connection.

## Quick Reference

**Bridge first.** Two Studio MCP bridges exist: the **official** (built into Studio, closed-source) and **[chrrxs's](https://github.com/Chrrxs/robloxstudio-mcp)** (`chrrxs/robloxstudio-mcp`, MIT). Detect which is connected (`tools/list`; chrrxs's exposes `get_connected_instances`/`eval_*`/`multiplayer_*`; official exposes `list_roblox_studios`/`set_active_studio`).

### Bootstrap before mutation
1. `list_roblox_studios` and identify the target.
2. `set_active_studio` with the returned ID when selection matters.
3. `get_studio_state` and confirm Edit/Client/Server availability.
4. Inspect the target tree and scripts before changing them.

Pass `datamodel_type` only where the tool requires it: `Edit` for edit-time, `Client`/`Server` for runtime. Do not guess from a previous session.

### Capabilities
- **Inspect:** `search_game_tree`, `inspect_instance`, `script_search`, `script_read`, `script_grep`
- **Edit/execute:** `multi_edit`, `execute_luau`
- **Assets:** search and insert existing assets; `generate_mesh`, `generate_material`, `generate_procedural_model`, `wait_job_finished`, `store_image`, `upload_image`
- **Play/evidence:** `start_stop_play`, `get_console_output`, `screen_capture`, input simulation, `subagent`

Other bridges alias asset tools (e.g. `search_creator_store`/`insert_from_creator_store`).

### Execution contract
```text
discover → select Studio/context → inspect → mutate in bounded batches
→ read back → playtest → evidence → clean up or report fallback
```

### Reliability rules
- `execute_luau` is stateless. Re-acquire references every call.
- Read before write and read back after every script, asset, or geometry mutation.
- Generate or insert assets only after choosing between reuse, procedural generation, mesh/material generation, and native fallback.
- When generation returns an ID, call `wait_job_finished` before dependent edits.
- Keep large scripts in `multi_edit` chunks, not one oversized execution payload.
- If MCP is absent, provide offline Luau and state what was not verified.

> Full tool mappings, live-schema differences, asset workflows, evidence recipes, and recovery rules: [references/full.md](references/full.md)
