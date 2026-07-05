# Task 028: Write performance-audit.md Workflow

**depends-on:** 001
**phase:** 5 - Workflows
**files:** `workflows/performance-audit.md`

## Description

Write the performance profiling workflow.

## What To Do

1. **Step 1: Project Scan** — MCP: get_project_structure + grep_scripts for known anti-patterns (wait(), RunService loops). Offline: Ask for MicroProfiler data
2. **Step 2: Part Audit** — MCP: search_objects to count parts, check for unanchored parts. Offline: Ask user to check Explorer part count
3. **Step 3: Script Audit** — Check for: multiple Heartbeat connections, excessive RemoteEvent usage, tight loops, unindexed table operations
4. **Step 4: Memory Audit** — Check for: undisconnected events, unreferenced instances, large data tables
5. **Step 5: Network Audit** — Check RemoteEvent frequency, data size per event, unnecessary replication
6. **Step 6: Priority Report** — Generate prioritized list: Critical (causes crashes/unplayable) → High (noticeable lag) → Medium (suboptimal) → Low (minor)
7. **Step 7: Apply Fixes** — MCP: apply fixes + retest. Offline: provide fixes with instructions
8. **Step 8: Before/After** — Document improvements made

## Verification

- File exists at `workflows/performance-audit.md`
- Covers parts, scripts, memory, and network
- Prioritized output format
- Specific anti-patterns to grep for listed
