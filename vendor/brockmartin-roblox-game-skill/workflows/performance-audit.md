# Performance Audit Workflow

A step-by-step guided workflow for auditing and optimizing performance in a Roblox game project.

---

## Step 1: Project Scan

Gather baseline information about the project structure and identify common anti-patterns.

### MCP Full (Rojo/Argon project on disk)

- Use `get_project_structure` to map the full source tree.
- Use `grep_scripts` to scan for known anti-patterns:
  - `wait()` — deprecated; should be `task.wait()`.
  - Count `.Heartbeat` connections across all scripts.
  - `Instance.new` inside loops (mass instantiation without pooling).
  - `while true do` tight loops without yielding.
  - `game:GetService` called repeatedly instead of cached at top of script.
- Record file paths and line numbers for every finding.

### MCP Standard (partial access)

- Use available MCP tools to read script files.
- Manually search content for the same anti-patterns listed above.

### Offline (no MCP / in-Studio only)

- Ask the user to provide:
  - Total script count (ServerScriptService, StarterPlayerScripts, StarterCharacterScripts).
  - MicroProfiler screenshots or data (`Ctrl+F6` in Studio).
  - Output of the Script Performance widget (`View > Script Performance`).
- Review any pasted code for the anti-patterns listed above.

---

## Step 2: Part Audit

Evaluate the workspace part count and physics complexity.

1. **Count parts** — Total `BasePart` descendants under `Workspace`.
   - Under 10,000: acceptable for most genres.
   - 10,000-50,000: needs StreamingEnabled or aggressive culling.
   - Over 50,000: critical — redesign required.
2. **Unanchored parts** — Search for `BasePart` instances where `Anchored == false` that are not intentionally physics-driven. Each unanchored part costs physics simulation time.
3. **MeshPart triangle counts** — Flag any MeshPart with excessively high polygon counts (over 10,000 triangles per mesh).
4. **Transparency abuse** — Parts with `Transparency = 1` that still have `CanCollide = true` should use `CanQuery`/`CanTouch` instead and be removed from the render pipeline.
5. **Union complexity** — Flag large CSG unions (UnionOperations) that could be replaced with MeshParts for better performance.

---

## Step 3: Script Audit

Review runtime script behavior for CPU-heavy patterns.

1. **Multiple Heartbeat connections** — A single script should rarely have more than one `RunService.Heartbeat` connection. Multiple connections in the same script indicate fragmented update logic that should be consolidated.
2. **Tight loops** — `while true do` or `while task.wait() do` loops running faster than necessary. Most game loops only need 1/30s or 1/60s granularity.
3. **Uncached GetService** — Every `game:GetService("X")` call in a function body (not at the top of the script) is a repeated lookup. Cache services as locals at the top of the script.
4. **Deprecated API usage**:
   - `wait()` -> `task.wait()`
   - `spawn()` -> `task.spawn()`
   - `delay()` -> `task.delay()`
5. **String concatenation in loops** — Repeated `..` concatenation in hot paths; recommend `table.concat`.
6. **Excessive `FindFirstChild` / `WaitForChild` chains** — Deep chains like `workspace:FindFirstChild("A"):FindFirstChild("B"):FindFirstChild("C")` are fragile and slow. Cache references.

---

## Step 4: Memory Audit

Identify memory leaks and resource retention issues.

1. **Undisconnected events** — Search for `:Connect(` calls where the returned `RBXScriptConnection` is never stored or `:Disconnect()`ed. Especially critical in:
   - `PlayerAdded` / `PlayerRemoving` handlers that create per-player connections.
   - `CharacterAdded` handlers.
   - Any connection made inside a loop or repeated function.
2. **Unreferenced instances** — `Instance.new()` calls where the instance is created but never parented (orphaned in memory) or parented to nil without cleanup.
3. **Debris misuse** — Using `Debris:AddItem()` with excessively long lifetimes (over 60 seconds) or not using it at all for temporary effects.
4. **Value object accumulation** — ObjectValues, IntValues, etc. created dynamically but never destroyed.
5. **Table growth** — Lua tables that grow unboundedly (e.g., logging every frame to a table without pruning).

---

## Step 5: Network Audit

Evaluate network traffic patterns for bandwidth and replication efficiency.

1. **RemoteEvent frequency** — Search for `RemoteEvent:FireServer()` or `RemoteEvent:FireAllClients()` calls inside `Heartbeat`, `RenderStepped`, or tight loops. Remotes should fire at controlled rates (typically no more than 10-20 times per second per remote).
2. **Data sizes** — Flag remotes that send:
   - Large tables (over 50 keys).
   - Full instance references when only a property is needed.
   - String data that could be encoded as numbers/enums.
3. **FireAllClients vs. FireClient** — `FireAllClients` sending player-specific data that should use `FireClient` to individual players.
4. **Attribute replication** — Excessive use of `Instance:SetAttribute()` on replicated instances causes network churn. Evaluate if attributes change too frequently.
5. **Replicated instance creation** — `Instance.new` on the server in hot paths replicates to all clients. Consider client-side VFX where possible.

---

## Step 6: Priority Report

Compile all findings into a prioritized report.

### Format

```
## Performance Audit Report

### Critical (fix before shipping)
- [Finding]: [File:Line] — [Description and impact]

### High (significant impact on player experience)
- [Finding]: [File:Line] — [Description and impact]

### Medium (noticeable under load)
- [Finding]: [File:Line] — [Description and impact]

### Low (minor optimization opportunity)
- [Finding]: [File:Line] — [Description and impact]

### Summary
- Total findings: X
- Estimated part count: X
- Heartbeat connections: X
- Potential memory leaks: X
- Network hotspots: X
```

Prioritization criteria:
- **Critical**: Causes crashes, server lag above 100ms, or client FPS below 30 on target hardware.
- **High**: Measurable frame drops, memory growth over time, or bandwidth spikes.
- **Medium**: Suboptimal patterns that degrade under load (20+ players).
- **Low**: Code quality / best practice improvements with minor perf benefit.

---

## Step 7: Apply Fixes

For each finding, either apply the fix directly or provide the corrected code.

- **Direct fix**: If MCP write access is available and the fix is safe (e.g., replacing `wait()` with `task.wait()`), apply it and note the change.
- **Code suggestion**: For architectural changes (e.g., consolidating Heartbeat connections, implementing object pooling), provide the refactored code with explanation.
- **Manual step**: For Studio-only fixes (e.g., anchoring parts, reducing mesh complexity), provide clear instructions for the user.

Always preserve existing behavior. Performance fixes must not change game logic.

---

## Step 8: Before/After Summary

Present a clear comparison of the project state before and after the audit.

```
## Before/After Summary

| Metric                  | Before | After  | Change  |
|------------------------|--------|--------|---------|
| Anti-pattern instances | X      | X      | -X      |
| Heartbeat connections  | X      | X      | -X      |
| Potential memory leaks | X      | X      | -X      |
| Deprecated API calls   | X      | X      | -X      |
| Network hotspots       | X      | X      | -X      |
| Estimated part count   | X      | X      | (note)  |

### Changes Applied
1. [File] — [What was changed and why]
2. ...

### Remaining Manual Steps
1. [What the user needs to do in Studio]
2. ...
```

If fixes were not applied (code-only suggestions), note which items remain unresolved and their priority.
