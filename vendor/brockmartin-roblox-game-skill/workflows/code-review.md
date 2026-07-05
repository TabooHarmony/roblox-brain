# Code Review Workflow

A step-by-step guided workflow for performing a comprehensive code review of a Roblox game project.

---

## Step 1: Project Scan

Understand the project structure and scope before reviewing code.

### MCP Full (Rojo/Argon project on disk)

- Use `get_project_structure` to map the full source tree.
- Use `get_file_tree` to get a detailed file listing with sizes and types.
- Note:
  - Total number of scripts (Server, Client, Module).
  - Directory organization pattern.
  - Project file format (Rojo `default.project.json`, Argon config, or raw `.lua` files).
  - Any configuration files, READMEs, or documentation.

### MCP Standard (partial access)

- Use available MCP tools to read the directory structure.
- List all script files and their locations.

### Offline (no MCP / in-Studio only)

- Ask the user to provide:
  - Screenshot or listing of the Explorer hierarchy (ServerScriptService, ReplicatedStorage, StarterPlayer, etc.).
  - Number of scripts in each container.
  - Any notable organizational patterns they use.
- Alternatively, ask the user to paste key scripts for review.

---

## Step 2: Organization Review

Evaluate whether scripts are in the correct locations and the project follows clean organizational patterns.

### Script Placement Rules

| Script Type | Correct Location | Notes |
|-------------|-----------------|-------|
| Server Scripts | `ServerScriptService` | Never in ReplicatedStorage or Workspace |
| Server Modules | `ServerScriptService` or `ServerStorage` | Must not be accessible to clients |
| Client Scripts (LocalScripts) | `StarterPlayerScripts`, `StarterCharacterScripts`, or `StarterGui` | Purpose determines location |
| Shared Modules | `ReplicatedStorage` | Used by both server and client |
| Client-only Modules | `ReplicatedStorage` or `StarterPlayerScripts` | No server logic |

### Folder Structure

- Are scripts organized into logical folders (e.g., `Services/`, `Controllers/`, `Components/`, `UI/`)?
- Is there a consistent naming convention (PascalCase for modules, camelCase for variables)?
- Are related scripts grouped together or scattered?

### Service Usage

- Is `game:GetService()` used consistently (not `game.ServiceName` which is deprecated-style)?
- Are services cached at the top of each script?

### Red Flags

- Scripts directly in `Workspace` (runs on server but easily found by exploiters in the hierarchy).
- ModuleScripts in `ReplicatedFirst` (unusual, verify intentional).
- Server logic in `ReplicatedStorage` (accessible to clients).
- Orphaned scripts (not parented to a running container — they will not execute).

---

## Step 3: Code Quality Scan

Search for deprecated APIs, anti-patterns, and code quality issues.

### MCP Search (grep_scripts for each pattern)

#### Deprecated APIs

| Pattern | Replacement | Severity |
|---------|------------|----------|
| `wait(` | `task.wait(` | Medium |
| `spawn(` | `task.spawn(` | Medium |
| `delay(` | `task.delay(` | Medium |
| `coroutine.wrap` / `coroutine.resume` | `task.spawn` / `task.defer` | Low |

#### Anti-Patterns

| Pattern | Issue | Fix |
|---------|-------|-----|
| Global variables (no `local` keyword) | Pollutes global scope, causes bugs | Always use `local` |
| Missing type annotations | Reduces readability, no Luau type checking | Add `: type` annotations |
| String concatenation in loops (`..`) | Creates garbage, slow in hot paths | Use `table.concat` or string interpolation |
| `Instance.new("X")` then `.Parent = Y` | Two replication events | Pass parent as second arg or set parent last after configuring properties |
| Nested `WaitForChild` chains | Fragile, slow, blocks thread | Cache references, use module-level variables |
| `pcall` without error handling | Silently swallows errors | Log or handle the error: `local ok, err = pcall(...)` |
| Magic numbers | Unclear intent | Use named constants |

#### Duplicate Code

- Search for repeated code blocks (similar function bodies across scripts).
- Flag opportunities to extract into shared ModuleScripts.

### Offline Review

- Ask the user to paste scripts one at a time.
- Review each for the patterns above.

---

## Step 4: Architecture Review

Evaluate the overall code architecture for maintainability and scalability.

### Module Boundaries

- Do ModuleScripts have clear, single responsibilities?
- Are module APIs clean (small public surface, implementation hidden)?
- Do modules return a table of functions (standard pattern) or use other patterns?

```lua
-- GOOD: Clean module pattern
local InventoryService = {}

function InventoryService.addItem(player, itemId, quantity)
    -- implementation
end

function InventoryService.removeItem(player, itemId, quantity)
    -- implementation
end

return InventoryService
```

### Dependency Direction

- Dependencies should flow one direction: Scripts -> Modules, not Modules -> Scripts.
- Higher-level modules should depend on lower-level modules, not the reverse.
- Example of correct layering:
  ```
  ServerScript (entry point)
    -> GameService (orchestration)
      -> InventoryModule (domain logic)
        -> DataModule (persistence)
  ```

### Circular Requires

- Search for circular `require()` chains (Module A requires Module B which requires Module A).
- Circular requires cause subtle bugs and initialization order issues in Roblox.
- Fix by extracting shared logic into a third module or using dependency injection.

### Event Architecture

- How do scripts communicate? Direct requires, events, or a message bus?
- Is there a consistent pattern, or is communication ad-hoc?
- Evaluate if BindableEvents are used appropriately for decoupling.

---

## Step 5: Security Quick-Check

A focused security scan (for a full audit, use the Security Audit workflow).

### Unvalidated Remotes

- Search for `OnServerEvent:Connect` and `OnServerInvoke` handlers.
- For each handler, check: Does it validate argument types before using them?
- Flag any handler that directly uses client-provided data without checks.

### Client-Trusted Logic

- Search client scripts for patterns that indicate the client is authoritative:
  - Client modifying `leaderstats` values.
  - Client computing damage/rewards and sending results to server.
  - Client setting its own position via remotes.

### Quick Severity Assessment

- **Critical**: Unvalidated remote that modifies currency, inventory, or stats.
- **High**: Client-computed damage or rewards.
- **Medium**: Missing type checks on non-critical remotes.
- **Low**: Missing cooldowns on low-impact remotes.

---

## Step 6: Performance Quick-Check

A focused performance scan (for a full audit, use the Performance Audit workflow).

### Heartbeat Abuse

- Count `RunService.Heartbeat:Connect()` calls across all scripts.
- Flag scripts with multiple Heartbeat connections.
- Flag Heartbeat handlers that do heavy work (raycasting, table iteration, Instance queries).

### Part Count

- If accessible, count total BaseParts in Workspace.
- Check if StreamingEnabled is on for large maps.

### Memory Leaks

- Search for `:Connect(` where the connection is not stored in a variable.
- Search for `PlayerAdded` handlers that create connections without cleanup in `PlayerRemoving`.
- Search for `Instance.new` without a corresponding `:Destroy()` path.

### Quick Severity Assessment

- **Critical**: Unbounded memory growth (leaking connections per player join).
- **High**: Multiple expensive Heartbeat handlers.
- **Medium**: Deprecated API usage in hot paths.
- **Low**: Uncached GetService calls.

---

## Step 7: Quality Report

Compile findings into a graded quality report.

### Grading Criteria

| Grade | Description |
|-------|-------------|
| **A** | Excellent. Clean architecture, no deprecated APIs, proper validation, good module boundaries. Minor suggestions only. |
| **B** | Good. Mostly clean with some deprecated API usage or minor organizational issues. No security or performance problems. |
| **C** | Acceptable. Functional but has notable code quality issues, some architectural concerns, or minor security gaps. Needs improvement before scaling. |
| **D** | Poor. Significant issues: deprecated APIs throughout, weak architecture, security vulnerabilities, or performance problems. Requires substantial refactoring. |
| **F** | Critical. Major security vulnerabilities, memory leaks, no validation on remotes, or fundamental architectural problems that will cause failures at scale. |

### Report Format

```
## Code Review Report

### Overall Grade: [A-F]

### Organization: [A-F]
- [Findings with file paths and specific issues]

### Code Quality: [A-F]
- [Findings by severity]

### Architecture: [A-F]
- [Findings with dependency diagrams if relevant]

### Security: [A-F] (quick-check)
- [Findings with severity]

### Performance: [A-F] (quick-check)
- [Findings with severity]

### Summary Statistics
- Total scripts reviewed: X
- Deprecated API usages: X
- Unvalidated remotes: X
- Potential memory leaks: X
- Circular dependencies: X
- Duplicate code instances: X

### Top 5 Priority Fixes
1. [Most impactful fix with specific code suggestion]
2. ...
3. ...
4. ...
5. ...
```

---

## Step 8: Refactoring Suggestions

Provide actionable refactoring recommendations ordered by impact.

### Categories

#### Quick Wins (< 30 minutes each)

- Replace deprecated APIs (`wait` -> `task.wait`, etc.).
- Cache `GetService` calls at script top.
- Add type annotations to function signatures.
- Replace magic numbers with named constants.
- Fix `Instance.new` parent-last pattern.

#### Structural Improvements (1-3 hours each)

- Extract duplicate code into shared modules.
- Reorganize scripts into proper containers.
- Add validation to unprotected remotes.
- Disconnect leaked event connections.
- Break up oversized scripts (over 300 lines) into focused modules.

#### Architectural Changes (half-day to multi-day)

- Introduce a service/controller architecture pattern.
- Implement proper dependency injection to resolve circular requires.
- Add a centralized event/message bus for cross-system communication.
- Implement a data layer abstraction over raw DataStore calls.
- Add a state management pattern for complex game state.

### For Each Suggestion

Provide:
1. **What** to change.
2. **Why** it matters (impact on maintainability, performance, or security).
3. **How** to implement it (specific code example or pattern).
4. **Effort** estimate (quick win / moderate / significant).

If MCP write access is available, offer to apply Quick Win fixes directly.
