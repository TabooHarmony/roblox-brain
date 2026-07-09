---
name: roblox-luau-patterns
description: "Use for Luau metatable classes, inheritance, Promises, coroutines, pcall, module structure, services, and Roblox coding patterns."
last_reviewed: 2026-05-27
sources:
  - https://luau-lang.org/
---

## When to Load

Load for Luau patterns: classes with metatables (constructors, methods, inheritance), async control flow (Promises, coroutines, pcall/xpcall), module structure (service pattern, singletons), Roblox-specific patterns (Instance creation, service access, events, task library). For syntax questions, use `roblox-luau-core`. For type annotations, use `roblox-luau-types`.

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
