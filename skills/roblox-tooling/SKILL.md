---
name: roblox-tooling
description: >
  Built-in Studio MCP orchestration, luau-lsp integration, mcp-roblox-docs usage.
  How the AI drives Studio directly.
last_reviewed: 2026-05-22
---

<!-- Source: brockmartin/roblox-game-skill (MIT), rewritten for built-in MCP only -->

# Roblox Tooling Reference

## Overview

Load this reference when:

- Performing MCP operations (executing Luau, reading/writing instances, managing assets)
- Autonomous building (scaffolding game structure, generating systems, iterating)
- Debugging via Studio (reading console output, tracing errors, applying fixes)
- Project exploration (understanding an existing place file's architecture)

This covers the built-in Studio MCP server, mcp-roblox-docs for API lookup, luau-lsp for diagnostics, and offline workflows.

## luau-lsp (Agent-Side Diagnostics)

The internal `luau-check` extension hooks `.luau` file writes and runs `luau-lsp analyze` automatically. Diagnostics inject into the next agent turn.

Agent uses the CLI binary. The VS Code extension and Studio Companion Plugin are for humans, not agent onboarding.

```
luau-lsp analyze path/to/file.luau --formatter plain
```

Output format: `path.luau:line:col severity: message`

Soft gate at handoff: do not claim "done" with unresolved error-level diagnostics.

## mcp-roblox-docs (API Reference)

Live API lookup via MCP. Registered during /setup if `uvx` is available.

Use for: class members, properties, methods, events, enums, FastFlags. Never enumerate these in skills.

## Built-in Studio MCP (6 Tools)

The official Roblox MCP server ships with Studio. No install required. Enable via the Assistant widget (View → Assistant → MCP toggle).

| Tool | Purpose | Notes |
|------|---------|-------|
| `run_code` | Execute Luau inside Studio | Primary workhorse for all operations |
| `insert_model` | Insert a model from Creator Store | Takes asset ID, inserts into Workspace |
| `get_console_output` | Read Studio output/console log | Error detection and debug loops |
| `start_stop_play` | Toggle playtest mode | Single tool handles both start and stop |
| `run_script_in_play_mode` | Execute code during playtest | Stops playtest when script finishes |
| `get_studio_mode` | Check Edit vs Play mode | Always call before mode-sensitive ops |

### Workflow Adaptations

Since the built-in server lacks exploration tools (`get_file_tree`, `grep_scripts`), compensate with `run_code`:

```luau
-- Traverse DataModel and print structure
local function printTree(instance, depth)
    depth = depth or 0
    local indent = string.rep("  ", depth)
    print(`{indent}{instance.Name} [{instance.ClassName}]`)
    for _, child in instance:GetChildren() do
        printTree(child, depth + 1)
    end
end
printTree(game:GetService("ServerScriptService"), 0)
```

Read results via `get_console_output`. Build search logic inline via `run_code` instead of relying on dedicated search tools.

## Offline Mode

When no MCP server is connected, generate self-contained Luau code blocks for copy-paste into Studio.

### Conventions

- Label every script block with its target service/folder and script type
- Group related scripts with section headers
- Provide a setup checklist listing manual steps (e.g., "Create a RemoteEvent named 'DamageEvent' in ReplicatedStorage")

## Orchestration Patterns

### Autonomous Build

1. **SCAFFOLD** - `run_code` to print current hierarchy → plan structure → `run_code` to create folders/instances
2. **GENERATE** - For each system: `run_code` to create Script/LocalScript/ModuleScript instances, wire RemoteEvents
3. **INSERT ASSETS** - `insert_model` for Creator Store assets, position via `run_code`
4. **TEST** - `start_stop_play` → `get_console_output` → `start_stop_play` to stop
5. **ITERATE** - Fix errors → return to step 4 (max 5 iterations)

### Debug Loop

Bounded retries (max 5 iterations):

1. **DETECT** - `get_console_output` → parse for script name, line, error type
2. **LOCATE** - `run_code` to print script source → analyze root cause
3. **FIX** - Generate corrected code → `run_code` to replace script source (create undo waypoint first)
4. **VERIFY** - `start_stop_play` → `get_console_output` → check if error persists
5. **ITERATE** - If persists and attempts < 5 → step 2; if resolved → report; if ≥ 5 → report findings

### Project Exploration

1. **STRUCTURE** - `run_code` to traverse and print full hierarchy
2. **SCRIPTS** - `run_code` to find all Script/LocalScript/ModuleScript instances, print sources of key scripts
3. **ARCHITECTURE** - Map module dependencies, remotes, data flow from printed output
4. **REPORT** - Summarize services, script count, architecture, potential issues

## Safety Guidelines

### Pre-Operation Checks

1. **Check Studio mode** - call `get_studio_mode` before any operation. Do not modify DataModel during playtest.
2. **Create undo waypoints** before bulk or destructive operations:
   ```luau
   game:GetService("ChangeHistoryService"):SetWaypoint("Before: description")
   ```
3. **Read before write** - inspect script source before overwriting.
4. **Verify instance existence** - check target path resolves before modifying.

### Destructive Operation Safeguards

- Deleting instances: confirm with user before `:Destroy()` on named/significant instances.
- Overwriting scripts: log previous source before replacing.
- Clearing containers: never `:ClearAllChildren()` on services without explicit user confirmation.

### Playtest Safety

- Do not modify DataModel while playtest is active (changes lost when playtest ends).
- Use `run_script_in_play_mode` for runtime testing during play mode.
- Always stop playtest before applying fixes.

## Best Practices

- Batch related reads/writes in a single `run_code` call to minimize round-trips.
- Always read script source before modifying; apply targeted changes, not blind overwrites.
- After modification, verify with `get_console_output` or a playtest.
- Create `ChangeHistoryService:SetWaypoint()` before batches or experimental changes.

## Anti-Patterns

- Running code without checking Studio state → always `get_studio_mode` first
- Bulk changes without undo points → set waypoint before any destructive operation
- Blind script overwrites → read source first, merge or confirm replacement
- Ignoring error output → always check console, enter debug loop on errors
- Using third-party MCP servers → built-in only, no boshyxd or community servers