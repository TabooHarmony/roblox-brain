---
name: roblox-luau-patterns
description: "Use when writing or refactoring Roblox Luau modules, object lifecycles, signals, task scheduling, pcall, and cleanup."
when_to_use: "Also for memory leaks, connections never disconnected, duplicate handlers after respawn, task.spawn/defer/delay misuse, retries, and reviewing module structure."
last_reviewed: 2026-11-27
sources:
  - https://luau-lang.org/
  - https://luau.org/library
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine/libraries/coroutine.yaml
  - https://create.roblox.com/docs/reference/engine/classes/ObjectValue
  - https://create.roblox.com/docs/reference/engine/classes/StringValue
  - https://create.roblox.com/docs/reference/engine/classes/CFrameValue
  - https://devforum.roblox.com/t/studio-beta-reference-instances-directly-with-attributes/4753441
  - https://raw.githubusercontent.com/Kampfkarren/kampfkarren-luau-guidelines/main/README.md
  - original
---

# Luau Patterns

## When to Load

Module shapes, ownership, scheduling, failure contracts. Semantics: `roblox-luau-core`; types: `roblox-luau-types`; startup: `roblox-architecture`.

## Quick Reference

### Choose a shape

- **Plain functions:** default for stateless transformation or validation.
- **Module with private state:** one subsystem owner, not a manager class for namespacing.
- **Object with metatable:** many independent values share behavior and lifecycle.
- **Existing library:** follow the project's; don't add Promise, signal or framework dependencies for one call site.

Constructors use `.`, methods `:`; mutable fields live on the instance.

### Make ownership visible

Connections, instances and tasks need cleanup owners; disconnect or cancel at teardown. Type signal payloads (`Signal<T...>`).

Configure before parenting to hide partial state; this does not order replication. `coroutine.finally` (2026-10 reference) runs cleanup when a thread finishes, errors or is cancelled.

### Preserve failure semantics

```luau
local ok, value = pcall(dataStore.GetAsync, dataStore, key)
if not ok then
    return nil, `read failed: {value}`
end
return value, nil -- value may legitimately be nil
```

Keep "returned nil" distinct from "failed". Retry only operations safe to repeat.

### Naming and return contracts

Mark yielding functions `Async`, keep return counts consistent, prefer named module exports; respect existing contracts.

### Schedule deliberately

Use `task.*`, never `wait()`. Prefer a state-change signal to polling.

### Spread work across frames (field-measured)

- Start a budgeted worker with `task.defer` so it sees the whole batch; check the budget inside each step.
- Clamp `dt` in timers. Watch the peak: one atomic swap ignores any budget.
- Count completions: a budget can hide an infinite loop. Add a no-progress guard.
- Sliced walks need inputs that don't change between slices; invalidate caches narrowly.

### Review

Clear owner, narrow API, no require cycle, success distinct from missing data, connections and tasks cleaned up, client input via `roblox-networking`.

> Details: [references/full.md](references/full.md)
