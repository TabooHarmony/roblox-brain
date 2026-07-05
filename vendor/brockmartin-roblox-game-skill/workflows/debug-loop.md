# Iterative Debugging Workflow

A structured loop for diagnosing and fixing Roblox game bugs. Adapts to MCP Full, MCP Standard, and Offline environments. Caps at 5 iterations before escalating to the user.

---

## Step 1: Error Gathering

Collect the raw error output so there is concrete diagnostic data to work with.

### MCP Full
- Call `get_playtest_output` to retrieve runtime errors from the most recent playtest session.
- If no playtest is active, fall back to `get_console_output` to read the Studio output panel.

### MCP Standard
- Call `get_console_output` to read whatever is currently in the output panel.

### Offline
- Ask the user to paste the **full error message** including:
  - The error text itself.
  - The stack trace (script name, line number).
  - Any preceding warnings that may provide context.

### What to capture
- Exact error string (e.g., `ServerScriptService.CombatHandler:42: attempt to index nil with 'Character'`).
- Script path and line number.
- Whether the error fires once, intermittently, or in a loop.
- Client vs. server origin.

---

## Step 2: Code Discovery

Locate and read the source code surrounding the error.

### MCP Full
- Use `grep_scripts` with keywords from the error (function name, variable, service) to find all relevant scripts.
- Use `get_script_source` on each match to read the full source.

### MCP Standard
- Use `run_code` to print script contents via Luau:
  ```lua
  local src = game:GetService("ServerScriptService"):FindFirstChild("CombatHandler")
  if src then print(src.Source) end
  ```

### Offline
- Ask the user to share the contents of every script referenced in the stack trace.
- Also request any scripts that call into or are called by the erroring script (upstream/downstream).

### What to look for
- The exact line cited in the error.
- 10-20 lines of surrounding context for control flow.
- Related modules that feed data into the erroring function (require chains, event connections).

---

## Step 3: Root Cause Analysis

Categorize the error into one of the following buckets. Cross-reference with `references/luau-mastery.md` and `references/security-hardening.md` for common Roblox gotchas.

### Syntax Error
- Missing `end`, `then`, or `do`.
- Mismatched parentheses or brackets.
- Typo in keyword (e.g., `fucntion` instead of `function`).
- **Fix pattern:** Correct the typo or add the missing token. Luau's error message usually points directly at the problem.

### Runtime Error
- **Nil reference:** Accessing a property on a value that is `nil`. Common causes:
  - `Player.Character` before the character has loaded.
  - `FindFirstChild` returning `nil` and the result used without a guard.
  - Remote event payload that the client did not send.
- **Type mismatch:** Passing a string where a number is expected, or vice versa.
- **Missing service:** Calling `GetService` with a misspelled service name.
- **Fix pattern:** Add nil guards, type checks, or WaitForChild with a timeout.

### Logic Error
- Code runs without errors but produces wrong behavior.
- Incorrect calculation (damage formula, cooldown timer, currency math).
- Wrong conditional logic (using `or` instead of `and`, inverted boolean).
- Event fires but the handler does the wrong thing.
- **Fix pattern:** Trace the data flow step by step with print statements or breakpoints to find where actual values diverge from expected values.

### Security Issue
- Client sending unvalidated data through RemoteEvents.
- Trusting `Player.Character.Humanoid.Health` from the client.
- Missing server-side sanity checks on purchase amounts, damage values, or item IDs.
- **Fix pattern:** Move authority to the server. Validate every remote argument. See `references/security-hardening.md`.

### Performance Issue
- Server or client frame rate dropping.
- Memory climbing over time (leak).
- High part count, excessive raycasting, or unthrottled loops.
- Runaway `RenderStepped` / `Heartbeat` connections that never disconnect.
- **Fix pattern:** Profile with MicroProfiler, reduce unnecessary computation, pool objects, debounce events. See `references/performance-optimization.md`.

---

## Step 4: Generate Fix

Produce corrected Luau code. Every fix must include:

1. **What was wrong** -- a plain-language explanation of the bug.
2. **Why the fix works** -- the specific change and the reasoning behind it.
3. **The corrected code** -- full function or block, not just a one-line diff, so it can be dropped in without ambiguity.

### Fix guidelines
- Preserve the original code's style and naming conventions.
- Do not introduce unrelated refactors in the same fix (keep the diff minimal and focused).
- If the fix requires a new guard or validation, explain what happens when the guard triggers (e.g., early return, warning log, fallback value).
- If the bug is in a pattern that appears in multiple scripts, note all locations so they can all be patched.

---

## Step 5: Apply and Test

### MCP Full
1. Call `execute_luau` to inject the corrected code into the running session or update the script source.
2. Call `start_playtest` to launch a new playtest.
3. Call `get_playtest_output` to capture output and check for the original error.

### MCP Standard
1. Call `run_code` to apply the fix:
   ```lua
   local script = game:GetService("ServerScriptService"):FindFirstChild("CombatHandler")
   script.Source = [[ --[[ corrected source here ]] ]]
   ```
2. Call `start_stop_play` to restart the playtest.
3. Call `get_console_output` to read the results.

### Offline
1. Provide the corrected code in a fenced Luau block.
2. Give step-by-step manual testing instructions:
   - Where to paste the code (which script, which service).
   - How to trigger the scenario that caused the bug.
   - What output or behavior to look for to confirm the fix.

---

## Step 6: Verify

Check whether the original error is resolved.

### Error is gone
- Confirm no new errors were introduced by scanning the full output (not just filtering for the original error string).
- If clean, proceed to Step 7.

### Error persists or a new error appears
- Capture the new diagnostic info.
- Return to **Step 1** with the updated error data.
- On each iteration, append findings to a running log:
  ```
  Iteration 1: Nil reference on Character -- added WaitForChild guard -- error persists (different line).
  Iteration 2: ...
  ```

### Iteration cap
- **Maximum 5 iterations.** If the bug is not resolved after 5 passes:
  - Stop attempting automatic fixes.
  - Present the user with a **findings summary**:
    - Each iteration's hypothesis, attempted fix, and result.
    - Remaining theories that have not been tested.
    - Suggested next steps (e.g., enable MicroProfiler, add verbose logging, isolate in a minimal repro place).

---

## Step 7: Summary

Once the bug is resolved, document the outcome. This serves as a record for future debugging and helps prevent recurrence.

### Template

```
## Bug Report

**Error:** [exact error message]
**Script:** [full script path]
**Line:** [line number]

**Root Cause Category:** [Syntax | Runtime | Logic | Security | Performance]

**Root Cause Description:**
[Plain-language explanation of why the bug occurred.]

**Fix Applied:**
[Description of the change. Include the key code diff or corrected block.]

**Iterations Required:** [1-5]

**Preventive Advice:**
- [Actionable recommendation to avoid this class of bug in the future.]
- [E.g., "Always nil-check Player.Character before accessing Humanoid."]
- [E.g., "Validate all RemoteEvent arguments on the server before processing."]
```

### After documenting
- If the bug revealed a pattern that should be caught earlier, suggest adding a lint rule, a helper function, or a note to the project's coding conventions.
- If the root cause was a common Roblox gotcha, verify it is covered in the relevant reference docs (`luau-mastery.md`, `security-hardening.md`, `performance-optimization.md`). If not, flag it for addition.
