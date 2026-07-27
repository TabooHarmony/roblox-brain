---
name: roblox-luau-patterns
description: "Use for Roblox module boundaries, object lifecycles, signals, task scheduling, fallible calls, and cleanup in Luau."
last_reviewed: 2026-07-26
sources:
  - https://luau-lang.org/
---

# Luau Patterns

## When to Load

Load when choosing a module shape, owning Roblox instances or event connections, scheduling work, or preserving failure semantics. Use `roblox-luau-core` for language behavior, `roblox-luau-types` for types, and `roblox-architecture` for project-wide ownership and startup.

## Quick Reference

### Choose the smallest shape

- **Plain functions:** default for stateless transformation or validation.
- **Module with private state:** one explicit subsystem owner. Do not create a manager class merely to namespace functions.
- **Object with metatable:** multiple independent values need shared behavior and lifecycle.
- **Existing library abstraction:** follow it when the project already uses it consistently. Do not add Promise, signal, cleanup, or framework dependencies for one call site.

```luau
local Counter = {}
Counter.__index = Counter

function Counter.new(initial: number): Counter
    return setmetatable({ value = initial }, Counter)
end

function Counter:increment()
    self.value += 1
end
```

Constructors use `.`, instance methods use `:`, and mutable fields belong on the instance, not the class table.

### Make ownership visible

The code that connects a signal, creates an instance, or starts a task owns cleanup. Store connections and cancel or disconnect them when it ends.

Configure an instance before parenting when observers should not see partial state. Parent earlier only when the API or lifecycle requires ancestry, and document that reason. This is visibility control, not a magic replication-race fix.

### Preserve failure semantics

```luau
local ok, value = pcall(dataStore.GetAsync, dataStore, key)
if not ok then
    return nil, `read failed: {value}`
end
return value, nil -- value may legitimately be nil
```

Do not collapse “call succeeded and returned nil” into “call failed.” Retry only when the domain operation is safe to repeat. Persistence, HTTP, purchases, and remotes belong to their domain skills.

### Schedule deliberately

Use `task.defer` to run after the current resumption cycle, `task.spawn` for independent immediate work, `task.delay` for delayed work, and `task.cancel` when the owner ends. Replacing a polling loop with a per-frame event is not automatically cheaper. Prefer event-driven work when a real state-change signal exists; otherwise choose and measure an explicit cadence.

### Review

Clear owner, narrow public API, no circular require, no accidental concurrent startup, success and missing-data states remain distinct, connections/tasks cleaned up, client input routed to `roblox-networking`.

> Detailed decision rules and lifecycle examples: [references/full.md](references/full.md)
