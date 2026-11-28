---
name: roblox-luau-core
description: "Use when writing, editing, or debugging any Luau: tables, control flow, string patterns, scope, closures, and errors ported from JS/Python."
when_to_use: "Also for Luau syntax errors, nil indexing, wrong loop or table behavior, string formatting, and reviewing Luau code for correctness."
last_reviewed: 2026-11-27
sources:
  - https://luau.org/syntax
  - https://luau.org/library
  - https://create.roblox.com/docs/luau/control-structures
  - https://create.roblox.com/docs/luau/metatables
  - https://create.roblox.com/docs/luau/native-code-gen
  - https://raw.githubusercontent.com/Kampfkarren/kampfkarren-luau-guidelines/main/README.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine/libraries/vector.yaml
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine/libraries/buffer.yaml
  - original
---

# Luau Core Language

## When to Load

Load for Luau semantics and JS/Python translation. Types: `roblox-luau-types`; lifecycle: `roblox-luau-patterns`; engine APIs: domain skills.

## Quick Reference

- Only `false` and `nil` are falsy; `0`, `""`, `{}` are truthy. No coercion: `0 == "0"` is false; inequality is `~=`.
- Arrays are 1-based; `#array` is meaningful only without nil gaps. Dictionary order is unspecified.
- Assigning `nil` removes a key; tables are references; `table.clone` is shallow.
- Dynamic keys need brackets: `record[field]`.
- A call expands to all its values only as the last argument or item: `f(g(), x)` keeps one value of `g()`. Unpack into locals.
- Never start a line with `(`: it continues the previous statement as a call.
- Prefer an `if` expression over `cond and a or b` when `a` may be falsy.
- Locals start at their declaration; `repeat` locals reach `until`. `const` freezes the binding, not the table.
- `table.freeze` is shallow and errors on an already frozen table; guard with `table.isfrozen`.
- Weak tables (`__mode`) can drop Instance keys while the Instance lives; never track existence with them.
- `Vector3` table keys match by value; `Vector2` keys by identity (field-measured). Use `Vector3.new(x, 0, z)` for 2D cells.
- String patterns are not regular expressions. Join many fragments once in hot loops.
- NaN does not equal itself; test with `x ~= x`.
- `buffer`: fixed size, 0-based offsets, explicit widths; `readvectorf32x3`/`writevectorf32x3` move a `Vector3`. Avoid `readinteger`/`writeinteger`.
- `--!native` runs on servers and Android clients only.
- Base64, hashing, compression: `EncodingService` (buffers).

```luau
local label = if enabled then "On" else "Off"
local message = `{name}: {score}`
local size, center = sizeAndCenter()
place(size, center, owner)
```

### Translation traps

- JS `===`, `null`, `?.`, spread, arrow functions and array methods are not Luau.
- Python `None`, 0-based lists, comprehensions and exceptions don't translate.
- `x or fallback` replaces a valid `false`.
- `typeof` knows Roblox datatypes; `type` reports the Luau category.

> Language traps and translation examples: [references/full.md](references/full.md)
