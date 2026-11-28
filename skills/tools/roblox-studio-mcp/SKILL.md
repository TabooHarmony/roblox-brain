---
name: roblox-studio-mcp
description: "Use when working in Roblox Studio through MCP: editing scripts or scenes, generating assets, playtesting, screenshots, or input."
when_to_use: "Also for any Studio playtest, checking a change in game, reading runtime logs, device-simulator screenshots, and verifying a fix in Studio."
last_reviewed: 2026-11-27
sources:
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/studio/mcp.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/studio/testing-modes.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/projects/assets/privacy.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/parts/procedural-models.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/studio/mcp-open-cloud.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/assistant/skills.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/studio/cli.md
  - original
---

# Roblox Studio MCP

## When to Load

Studio MCP work: scripts, scenes, assets, playtests, captures, input, Open Cloud through Studio. Skip for standalone code generation. Shared-machine rules: `roblox-collaboration-mode`; bug-hunt method: `roblox-debugging`.

## Quick Reference

**Route by capability first.** Official bridge (built into Studio) vs **[chrrxs's](https://github.com/Chrrxs/robloxstudio-mcp)** (MIT). On `tools/list`: `get_connected_instances`/`eval_*`/`multiplayer_*` → chrrxs; `list_roblox_studios` + per-call `studio_id` → official.

### Bootstrap before mutation
1. Identify the target (`list_roblox_studios` / `get_connected_instances`); pass `studio_id` or `instance_id` on every call.
2. `get_studio_state`: is someone already playing? Confirm Edit/Client/Server; inspect before changing.

```text
discover → select Studio/context → inspect → mutate in bounded batches
→ read back → start play → evaluate live → evidence → clean up
```
Edit-time writes never target a running playtest; live evaluation needs a confirmed running VM.

### Official tools (Nov 2026)
`search_game_tree`, `script_read`/`script_grep`, `multi_edit`, `execute_luau`, `generate_*` (mesh, material, animation, avatar; `wait_job_finished` before dependent edits), `insert_asset`, `start_stop_play`, `get_console_output`, `screen_capture` (video in playtests), `save_place` (never publishes), `open_cloud_invoke` (per-game permissions, no API key), `submit_feedback`. Trust `tools/list`.

### Rules
- Load the built-in `rbx-*` skill for its area; never shadow it.
- `open_cloud_invoke` writes and live data store access need the user's yes.
- `execute_luau` is stateless and may use its own require cache. A bare `Unknown error` may still have run: re-read state.
- Captures lie when Studio isn't rendering; logs may hold only the edit peer. Confirm before claiming.
- Never run imported assets' code.
- No MCP: give offline Luau; state what was not verified.

> Tool tables, Open Cloud, simulators, field notes: [references/full.md](references/full.md)
