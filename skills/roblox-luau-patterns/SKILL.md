---
name: roblox-luau-patterns
description: OOP with metatables, inheritance, async (Promises, pcall), module structure, service pattern.
last_reviewed: 2026-05-27
---

## When to Load

- Designing classes with metatables (constructors, methods, inheritance)
- Async control flow (Promises, coroutines, pcall/xpcall, retry patterns)
- Module structure and organization (service pattern, singletons)
- Roblox-specific patterns (Instance creation, service access, events, task library)
- Choosing between architectural approaches (OOP vs modules vs flat functions)
- Error handling strategy (pcall wrapping, fallbacks, retry logic)

**Hand off when:** Pure syntax → `roblox-luau-core` · Type annotations → `roblox-luau-types` · Networking/data/security → `roblox-networking`, `roblox-data`, `roblox-security` · Performance → `roblox-performance`.

Full examples and code samples: `references/full.md`

## Quick Reference

**OOP (metatables):** Use for multiple instances with shared behavior.
```luau
local MyClass = {}
MyClass.__index = MyClass
function MyClass.new(...): MyClass  -- . for constructors
    return setmetatable({...}, MyClass)
end
function MyClass:method()           -- : for methods (implicit self)
end
-- Inheritance: setmetatable(Child, { __index = Parent })
```
Always set `__index`. Constructors use `.`, methods use `:`.

**Module Services:** Singleton pattern for managers. `Service.init()` wires events; clean up in `PlayerRemoving`.

**Instance Creation:** Configure ALL properties, set `Parent` LAST (prevents replication races).

**Task Library:** Always use `task.*`. `wait()`/`spawn()`/`delay()` are deprecated.

**Error Handling:**
```luau
local ok, result = pcall(fn, args...)       -- one-shot fallible calls
local ok, result = xpcall(fn, handler)      -- custom error handler + traceback
```
Wrap ALL DataStore/HTTP calls. Use Promise library for async chains (`:andThen`/`:catch`/`:finally`).

**Naming:** PascalCase (classes/modules/types), camelCase (vars/functions), UPPER_CASE (constants). Prefix `_` for private.

**Anti-Patterns:**
- `wait()`/`spawn()`/`delay()` → `task.*`
- Polling loops → events or Heartbeat
- String `..` in loops → `table.concat()`
- Missing `pcall` on DataStore/HTTP → silent crash
- Trusting client → validate types, ranges, ownership
- Parent before config → replication race
- Props on class table instead of `self` → shared across instances
- No connection cleanup → use Trove or manual `:Disconnect()`

**Libraries:** Promise · Trove · Signal · Comm (Sleitnick) · ProfileStore · t (runtime checks)

**Checklist:** `__index` set · `.`/`:` correct · pcall on fallible · connections cleaned · Parent last · no deprecated · clear API · async error handling · player data cleaned on PlayerRemoving
