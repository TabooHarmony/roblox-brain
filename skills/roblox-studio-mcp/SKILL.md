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

### Bootstrap before mutation
1. `list_roblox_studios` and identify the target.
2. `set_active_studio` with the returned ID when selection matters.
3. `get_studio_state` and confirm Edit/Client/Server availability.
4. Inspect the target tree and scripts before changing them.

Use the actual exposed schema. Pass `datamodel_type` only where the tool requires it: `Edit` for edit-time changes, `Client` or `Server` for runtime operations. Do not guess from a previous session.

### Capabilities
- **Inspect:** `search_game_tree`, `inspect_instance`, `script_search`, `script_read`, `script_grep`
- **Edit/execute:** `multi_edit`, `execute_luau`
- **Assets:** search and insert existing assets; `generate_mesh`, `generate_material`, `generate_procedural_model`, `wait_job_finished`, `store_image`, `upload_image`
- **Play/evidence:** `start_stop_play`, `get_console_output`, `screen_capture`, `character_navigation`, `user_keyboard_input`, `user_mouse_input`, `subagent`

The docs use names such as `search_asset` and `insert_asset`; other bridges may expose aliases such as `search_creator_store` and `insert_from_creator_store`. Route by capability, then inspect the live schema.

### Execution contract
```text
discover → select Studio/context → inspect → mutate in bounded batches
→ read back → playtest when needed → inspect console/visual evidence
→ clean up or report the exact fallback
```

### Reliability rules
- `execute_luau` is stateless. Re-acquire references every call.
- Read before write and read back after every script, asset, or geometry mutation.
- Generate or insert assets only after choosing between reuse, procedural generation, mesh/material generation, and native fallback.
- Treat generation as asynchronous when a generation ID is returned; call `wait_job_finished` with that `generationId` before dependent edits.
- Keep large scripts in `multi_edit` chunks, not one oversized execution payload.
- If MCP is absent or a capability is unavailable, provide complete offline Luau and state what was not verified.

> Full tool mappings, live-schema differences, asset workflows, evidence recipes, and recovery rules: [references/full.md](references/full.md)
