---
name: roblox-luau-core
description: "Use for Luau syntax, tables, control flow, string patterns, math, scope, closures, idioms, or porting code from JavaScript or Python."
last_reviewed: 2026-05-27
sources:
  - https://luau-lang.org/
  - https://create.roblox.com/docs/luau
---

# Luau Core Language

## When to Load

Load for Luau syntax questions: variables, operators, tables, string patterns, math helpers, scope/closures, common idioms, porting from JS/Python, and sharp edges (1-based indexing, nil semantics, truthiness). For type annotations, use `roblox-luau-types`. For OOP/async/modules, use `roblox-luau-patterns`.

**Hand off to:** `roblox-luau-types` (type annotations/generics), `roblox-luau-patterns` (OOP/async/modules), `roblox-*` domain skills (engine APIs).

**Full reference:** `references/full.md`

## Quick Reference

**Basics:** Luau = Lua 5.1 + extensions. Always `local`. No hoisting — callees above callers. Forward-declare for mutual recursion.

**Extensions over Lua 5.1:** `continue`, `+= -= *=`, `//` floor division, `math.clamp/sign/round`, backtick interpolation, generalized iteration, `table.freeze/clone/clear`.

**Truthiness:** Only `nil` and `false` are falsy. `0`, `""`, `{}` are truthy. No type coercion in `==` (`0 == "0"` → `false`).

**Arrays:** 1-based. `#tbl` length — unreliable with nil gaps, keep contiguous. Use `table.insert/remove/find/sort/concat`. Iterate: `for k, v in tbl do`.

**Strings:** Prefer backticks `` `{name} age {age}` `` over `..`. Patterns (NOT regex): `%a %d %w %s` classes, `* + - ?` quantifiers, `^$` anchors. Functions: `string.match/gmatch/gsub/split`.

**Tables:** Only compound type. Reference semantics (`=` aliases). `table.clone` is shallow. `nil` removes keys. Dynamic keys need bracket notation `t[key]`.

**Ternary:** `(cond and val or fallback)` breaks if `val` is falsy. Use `if cond then a else b` for safety.

**Error handling:** `pcall(fn)` / `xpcall(fn, handler)`. No try/catch.

**Pitfalls:**
- `a and b or c` fails when `b` is nil/false
- Arrays start at 1, not 0
- `:` defines implicit self, `.` doesn't
- While-loop closures share variable — capture in local
- No arrow functions, `===`, `!=`, spread, `const/let`
- Reserved keywords can't be identifiers (`return`, `continue`, etc.)
- Use `task.wait/spawn/delay`, never deprecated `wait/spawn/delay`

**JS→Luau:** `map/filter` → manual loops, `null` → `nil`, `x ?? y` → `x or y`, `x?.y` → `x and x.y`, `===` → `==`, `!==` → `~=`, `import` → `require`, `class` → metatable+`__index`, `try/catch` → `pcall`.

For detailed examples, see `references/full.md`.
