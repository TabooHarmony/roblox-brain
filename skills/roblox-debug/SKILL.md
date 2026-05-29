---
name: roblox-debug
description: "Iterative debug loop for Luau/Roblox issues"
last_reviewed: 2026-05-27
---

## When to Load

Load when diagnosing errors, crashes, or unexpected behavior in Roblox/Luau code. Provides a structured 7-step iterative debug loop with a max of 5 iterations before escalating. Works in both file-sync and MCP modes.

## Quick Reference

### 7-Step Debug Loop (max 5 iterations)

**1. Error Gathering** — Get exact error message, stack trace (script + line), trigger condition (join/action/timer). Use MCP for console output if available.

**2. Code Discovery** — Read relevant script(s). Search for error text, function names, or script from stack trace.

**3. Root Cause Analysis** — Categorize: Syntax (missing `end`) · Runtime (nil, destroyed Instance) · Logic (wrong calc/condition) · Security (client-side logic) · Performance (timeout, memory). Load `roblox-sharp-edges` for known gotchas. Find the exact line + true root cause.

**4. Generate Fix** — Produce corrected Luau. Explain what was wrong, why fix works, related code to check. Flag architectural changes.

**5. Apply & Test** — Write fix to file. MCP verify if available. In offline mode: before/after diff + manual test instructions.

**6. Verify** — Resolved → Step 7. New errors → back to Step 1. Same error → new hypothesis, back to Step 3. Iteration 5 → escalate with full diagnosis.

**7. Summary** — Document: bug description · root cause · fix applied · verification · related risks · prevention pattern. If systemic, recommend `/code-review`.

### Escalation (at iteration 5)
Output: all attempted fixes + why rejected, remaining hypotheses, recommended next steps (manual investigation, DevForum search, etc.).

📖 Full reference: `references/full.md`
