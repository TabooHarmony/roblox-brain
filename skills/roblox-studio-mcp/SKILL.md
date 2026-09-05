---
name: roblox-studio-mcp
description: "Use when working with Roblox Studio through built-in MCP for scripts, scenes, generated assets, input, or playtesting."
last_reviewed: 2026-08-21
sources:
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/studio/mcp.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/parts/procedural-models.md
  - https://create.roblox.com/docs/reference/engine/classes/ProceduralModel
---

# Roblox Studio MCP

## When to Load

Load for Studio MCP work: scripts, scenes, assets, debugging, or playtesting. Skip for standalone code generation.

## Quick Reference

**Route by capability first.** Two Studio MCP bridges exist: the **official** (built into Studio, closed-source) and **[chrrxs's](https://github.com/Chrrxs/robloxstudio-mcp)** (MIT). Route on `tools/list` (`get_connected_instances`/`eval_*`/`multiplayer_*` → chrrxs; `list_roblox_studios` + per-call `studio_id` → official) BEFORE bridge-specific bootstrap.

### Bootstrap before mutation
1. Identify the target via `list_roblox_studios` (official) or `get_connected_instances` (chrrxs).
2. Pass the target's `studio_id` (official) or `instance_id` (chrrxs) on every tool call.
3. `get_studio_state` and confirm Edit/Client/Server availability.
4. Inspect the target tree and scripts before changing them.

### Execution contract
```text
discover → select Studio/context → inspect → mutate in bounded batches
→ read back → start play → evaluate live → evidence → clean up
```

Edit-time injection (`multi_edit`, Edit-context `execute_luau`) writes scripts; it never targets a running playtest. Live evaluation targets a running VM: start play, wait for the intended `Client`/`Server` VM, then evaluate there. A stopped VM is never a live-evaluation target. Pass `datamodel_type` only where the tool requires it; do not guess from a previous session.

### Capabilities
Inspect (`search_game_tree`, `inspect_instance`, `script_read`, `script_grep`), edit/execute (`multi_edit`, `execute_luau`), assets (`search_asset`/`insert_asset`, `generate_*` with `wait_job_finished`, `store_image`/`upload_image`), play/evidence (`start_stop_play`, `get_console_output`, `screen_capture`, input simulation, `subagent`).

### Reliability rules
- `execute_luau` is stateless: re-acquire references every call.
- Read before write; read back after every script, asset, or geometry mutation.
- Choose reuse vs generation vs native fallback before asset work.
- Call `wait_job_finished` before edits that depend on a generation job.
- Command-size limits are bridge-specific. Split large scripts into separate bounded `multi_edit`/`execute_luau` writes (or supported multi-edit operations), then read back the full payload to verify.
- If MCP is absent, provide offline Luau and state what was not verified.

> Full tool mappings, live schemas, asset workflows, and recovery rules: [references/full.md](references/full.md)
