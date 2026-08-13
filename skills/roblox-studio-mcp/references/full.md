# Roblox Studio MCP — Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

Two Studio MCP bridges are in active use. The official Roblox Studio MCP server is built into Studio. The [`chrrxs/robloxstudio-mcp`](https://github.com/Chrrxs/robloxstudio-mcp) bridge (MIT, npm) is an open-source alternative with the same core plus runtime debugging, multiplayer playtests, profiling, and per-instance routing. This reference covers both, and the first thing to do is detect which bridge you are on. Do not assume official-only tool names work on the chrrxs bridge, or vice versa.

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

## Bridge Detection

Before using any tool, confirm which bridge is connected. Do not guess from a previous session.

- **Official bridge** (built into Studio): connect via `mcp.bat` on Windows or `StudioMCP` on macOS. Tool names follow the official creator-docs (`list_roblox_studios`, `set_active_studio`, `start_stop_play`, `get_console_output`, `script_read`, `multi_edit`, `execute_luau`, `search_asset`, `insert_asset`). It is closed-source but documented.
- **chrrxs bridge** ([`chrrxs/robloxstudio-mcp`](https://github.com/Chrrxs/robloxstudio-mcp), npm, MIT): tool names follow its open-source definitions (`get_connected_instances`, `get_file_tree`, `eval_server_runtime`, `eval_client_runtime`, `solo_playtest`, `multiplayer_playtest`, `manage_instance`, `get_runtime_logs`, `breakpoints`, `capture_script_profiler`, `capture_micro_profiler`, `get_memory_breakdown`, `get_scene_analysis`, `get_roblox_docs`, `get_roblox_skills`, and official-compatible names like `execute_luau`). Supports per-call `instance_id` routing and per-peer runtime logs.
- **Detect:** call `tools/list` (or `list_roblox_studios` / `get_connected_instances`). The presence of `get_connected_instances`, `eval_*`, or `multiplayer_*` identifies the chrrxs bridge. The presence of `list_roblox_studios`/`set_active_studio` with official tool names identifies the official bridge.

## Capability Matrix

| Capability | Official bridge | chrrxs bridge |
|------------|-----------------|----------------|
| Tree/script inspection, `execute_luau`, asset search/insert | ✅ | ✅ |
| Multi-instance routing | `list_roblox_studios` + `set_active_studio` (session switch) | `get_connected_instances` + per-call `instance_id` (fine-grained) |
| Open/close a specific Studio window per place | via Studio manually | `manage_instance` |
| Runtime Luau eval with game require-cache | ❌ | `eval_server_runtime` / `eval_client_runtime` |
| Live breakpoints without pausing | ❌ | `breakpoints` |
| Per-peer logs (server, client-N) | `get_console_output` (single log) | `get_runtime_logs` (per peer) |
| Solo / multiplayer playtest | `start_stop_play` (single client) | `solo_playtest` / `multiplayer_playtest` |
| CPU profiler / memory breakdown / scene analysis | ❌ | `capture_script_profiler`, `capture_micro_profiler`, `get_memory_breakdown`, `get_scene_analysis` |
| Fetch Roblox docs / Roblox-authored skills as tools | `http_get` / `skill` | `get_roblox_docs` / `get_roblox_skills` |

Treat this matrix as a map, not a guarantee. Bridges update. Inspect the live tool list before relying on a specific name; route by capability first, then confirm the exact tool name on the connected bridge.

## Multi-Place Routing

Multi-place work (Lobby + Game + Tutorial open in separate Studio windows) is supported on **both** bridges, with different mechanics:

- **Official bridge:** call `list_roblox_studios` to list open Studio instances (name, ID, active status). Call `set_active_studio` with the target ID. Subsequent tool calls then target that instance. Switching back requires another `set_active_studio`.
- **chrrxs bridge:** call `get_connected_instances` to list available IDs. Pass `instance_id` on each tool call to route that single call. Omit `instance_id` only when exactly one instance is connected; when multiple are connected it is required. `manage_instance` can launch, inspect, or close a specific Studio window (baseplate, local file, published place, or place revision).

### Wrong-Place Checklist

Before mutating in a multi-place session, confirm the target:

1. List instances: `list_roblox_studios` (official) or `get_connected_instances` (chrrxs).
2. Confirm which Place id/name you actually intend to edit (e.g. the user said Lobby, not Game).
3. On the chrrxs bridge, pass the correct `instance_id` on every call. Do not omit it when multiple places are connected.
4. On the official bridge, set the active instance and re-check `get_studio_state` on that instance.
5. Read the target (tree/script/property) and verify it exists in the intended place before writing.
6. If a call returns "not found" or an unexpected object, stop and re-list. Never assume the active instance is the one you want.

## Structured Playtest Pattern

The strongest playtest workflow uses a visible test artifact, not just "start play, read console." The pattern is bridge-agnostic: inject a test script that emits explicit START/FINISHED signals, run it, poll for the signal, stop, clean up, and report a summary.

1. **Plan the assertion** — what must be true? (e.g. `SpawnLocation` exists above the ground, the NPC reaches its target, the button opens the shop.)
2. **Inject the test** — on the chrrxs bridge use `eval_server_runtime` (or `eval_client_runtime` for client-side) to run Luau that sets a flag or prints a guard-signal when the assertion passes or fails. On the official bridge, create a temporary script in `ServerScriptService` (or use `subagent` with type `playtest`).
3. **Start play** — `solo_playtest` (chrrxs) or `start_stop_play` (official). Prefer Run mode (F8, server-only) for server-side logic; use Play mode (F5) when client behavior or rendering matters.
4. **Poll** — read logs (`get_runtime_logs` per peer on chrrxs, `get_console_output` on official) looking for the FINISHED signal, with a timeout (e.g. 60s default, max 300s).
5. **Stop and clean up** — always stop the playtest (`stop` on `solo_playtest`/`multiplayer_playtest`, or `start_stop_play` with `is_start: false`). Delete any injected temporary test script.
6. **Report** — produce a short artifact: status (passed/failed), test name, mode, duration, signal count, and the relevant log tail. This is what "evidence" means for playtesting.

### Playtest Discipline (from real-field bug reports)

- **Never auto-start a playtest as a debugging reflex.** Starting play mode unprompted (e.g. to "see what happens") is how sessions get stuck. Only start when there is a concrete assertion to check.
- **If you start it, verify the stop.** A playtest that fails to stop corrupts the session (observed on multiple bridges in the wild). After stopping, confirm state via `get_studio_state` (official) or the playtest status action (chrrxs) before continuing.
- **Treat a stuck playtest as a known failure state:** if a stop command does not take effect, report it, do not silently continue. Restarting Studio or the MCP client may be required.
- **Timeout + cleanup:** always bound a test with a timeout and always remove injected scripts, so no test residue survives.

## [chrrxs Bridge](https://github.com/Chrrxs/robloxstudio-mcp): Underutilized Tools Worth Surfacing

The chrrxs bridge ships much more than the official core. Weighted by what actually helps real work:

- **`eval_server_runtime` / `eval_client_runtime`** — run Luau inside a live playtest's VM with the same `require` cache as game scripts. This is the single best way to inspect live state (module state, runtime values) without restarting.
- **`multiplayer_playtest`** — start/inspect/stop multi-client playtests (1-8 players). Use when the question is "is this actually working with 2+ players" (co-op, remotes, replication). This is the biggest capability gap vs the official bridge.
- **`get_runtime_logs`** — per-peer logs (server, client-N), including boot-time output and structured `LogService` data. Better than a single console scrollback for finding which peer emitted an error.
- **`breakpoints`** — instrument live code and record execution without pausing the playtest. Use for "did this line run?" questions.
- **`capture_script_profiler` / `capture_micro_profiler`** — CPU timings on server or client. Use when the user asks "why is this slow" in a specific context.
- **`get_memory_breakdown` / `get_scene_analysis`** — memory and scene attribution per peer.
- **`manage_instance`** — launch/inspect/close Studio windows per place; the enabler for scripted multi-place workflows.
- **`get_roblox_docs` / `get_roblox_skills`** — fetch official engine API docs and Roblox-authored skills as Markdown. Use instead of web search when the question is "what does this API do."

When these are available, prefer them over weaker fallbacks: per-peer logs over a single console, runtime eval over guessing state, multiplayer playtest over a solo-only check.

## Multiplayer Testing Awareness

Multiplayer behavior is core development work, and agents under-cover it. Whenever the user asks whether a game feature works with friends, or any request touches remotes, replication, co-op, or shared state:

- **Official bridge:** no native multiplayer tool. `start_stop_play` plus manual `StudioTestService` access is not exposed; for actual multiplayer verification, use Studio's built-in test players manually, or route the user to a bridge that exposes it.
- **chrrxs bridge:** use `multiplayer_playtest` (start with `numPlayers`, add players, leave a client, end). Combine with `get_runtime_logs` to check per-peer state and `eval_client_runtime` to inspect a specific client.
- **Fallback:** if the bridge cannot run multiple clients, say so plainly and give the user the manual Studio test-player path. Do not claim multiplayer verification you did not do.

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
