# Task 027: Write debug-loop.md Workflow

**depends-on:** 001
**phase:** 5 - Workflows
**files:** `workflows/debug-loop.md`

## Description

Write the iterative debugging workflow — Claude's autonomous debug loop using MCP.

## What To Do

1. **Step 1: Error Gathering** — MCP: get_console_output or get_playtest_output. Offline: Ask user to paste error/output
2. **Step 2: Code Discovery** — MCP: grep_scripts / get_script_source to find relevant code. Offline: Ask user to share relevant scripts
3. **Step 3: Root Cause Analysis** — Analyze the error against common Roblox issues (load sharp-edges.md). Categorize: syntax, runtime, logic, security, performance
4. **Step 4: Generate Fix** — Produce corrected Luau code with explanation of what was wrong
5. **Step 5: Apply & Test** — MCP: execute_luau to apply fix + start_playtest + get_playtest_output. Offline: Provide code and manual test instructions
6. **Step 6: Verify** — Check if error is resolved. If not, return to Step 1 with new information
7. **Step 7: Summary** — Document what the bug was, root cause, and fix applied

Include guidance for maximum iteration count (5 attempts before escalating to user).

## Verification

- File exists at `workflows/debug-loop.md`
- Iterative loop is clearly defined
- MCP and offline paths for every step
- Maximum iteration safeguard included
- Common Roblox error categories documented
