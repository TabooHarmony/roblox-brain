# Task 002: Write SKILL.md Router

**depends-on:** 001
**phase:** 1 - Foundation
**files:** `SKILL.md`

## Description

Write the main SKILL.md file — the lightweight router/dispatcher. Must stay under 200 lines. This is the entry point that detects context and routes to appropriate reference/template/workflow files.

## What To Do

1. Write YAML frontmatter with: name (`roblox-game`), description (trigger keywords for Roblox, Luau, game development), version, schema
2. Write Identity/Philosophy section — expert Roblox developer persona, tone, approach
3. Write MCP Detection Logic — instructions for detecting which MCP server is available (community 39 tools = "full", official 6 tools = "standard", none = "offline") and adapting behavior
4. Write Routing Table — map user intents to specific reference/template/workflow files to load. Cover all 16 routing paths from the design doc
5. Write Core Quick Reference — the essential 20% of Roblox knowledge (service hierarchy, script placement rules, RemoteEvent basics, DataStore basics)
6. Write Sharp Edges Summary — top 5 critical gotchas always visible (DataStore data loss, client trust, memory leaks, RemoteEvent flooding, mobile part count)
7. Ensure total line count stays under 200

## Verification

- File exists at `/Users/brockmartin/.claude/skills/roblox-game/SKILL.md`
- Line count is under 200 (`wc -l`)
- YAML frontmatter parses correctly
- All 16 routing paths from the design doc are represented
- MCP detection logic covers all 3 modes
- Top 5 sharp edges are included
