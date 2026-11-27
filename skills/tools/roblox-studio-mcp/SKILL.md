---
name: roblox-studio-mcp
description: "Use when working in Roblox Studio through MCP: editing scripts or scenes, generating assets, playtesting, screenshots, or input."
when_to_use: "Also for any Studio playtest, checking a change in game, reading runtime logs, device-simulator screenshots, and verifying a fix in Studio."
last_reviewed: 2026-10-14
sources:
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/studio/mcp.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/studio/testing-modes.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/projects/assets/privacy.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/parts/procedural-models.md
  - https://create.roblox.com/docs/reference/engine/classes/ProceduralModel
  - original
---

# Roblox Studio MCP

## When to Load

Load for Studio MCP work: scripts, scenes, assets, debugging, or playtesting. Skip for standalone code generation.

## Quick Reference

**Route by capability first.** Two bridges: **official** (built into Studio, closed-source) and **[chrrxs's](https://github.com/Chrrxs/robloxstudio-mcp)** (MIT). Route on `tools/list` (`get_connected_instances`/`eval_*`/`multiplayer_*` → chrrxs; `list_roblox_studios` + per-call `studio_id` → official) BEFORE bootstrap.

### Bootstrap before mutation
1. Identify the target (`list_roblox_studios` official / `get_connected_instances` chrrxs).
2. Pass `studio_id` (official) or `instance_id` (chrrxs) on every call.
3. `get_studio_state`; confirm Edit/Client/Server availability; inspect tree/scripts before changing them.

### Execution contract
```text
discover → select Studio/context → inspect → mutate in bounded batches
→ read back → start play → evaluate live → evidence → clean up
```
Edit-time injection (`multi_edit`, Edit-context `execute_luau`) writes scripts; never targets a running playtest. Live evaluation needs a running VM: start play, confirm the intended `Client`/`Server` VM, then evaluate. Pass `datamodel_type` only where required.

### Capabilities
Full tool table in full.md. Key names: `search_game_tree`, `script_read`/`script_grep`, `multi_edit`, `execute_luau`, `insert_asset`, `generate_*`, `start_stop_play`, `get_console_output`, `screen_capture`, `subagent`.

### Trust boundaries
Inspect scripts in imported assets before execution. Never run imported code from `execute_luau`. For blank textures or meshes, read Output and check Restricted asset access in Creator Dashboard. See full.md for details.

### Reliability rules
- `execute_luau` is stateless: re-acquire references every call.
- Read before write; read back after every script, asset, or geometry mutation.
- Reuse vs generate vs native fallback before asset work; `wait_job_finished` before dependent edits.
- Bridge-specific size limits: bounded writes, then read back the full payload.
- No MCP: give offline Luau; state what was not verified.

> Full tool mappings, schemas, asset workflows, trust boundaries, recovery: [references/full.md](references/full.md)
