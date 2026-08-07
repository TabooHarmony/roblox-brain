---
name: roblox-luau-core
description: "Use for Luau language semantics, tables, control flow, string patterns, scope, closures, and cross-language translation errors."
last_reviewed: 2026-08-07
sources:
  - https://luau.org/syntax
  - https://luau.org/library
  - original
---

# Luau Core Language

## When to Load

Load for pure Luau syntax and semantics: truthiness, tables, iteration, functions, scope, operators, string patterns, and ports from JavaScript or Python. Use `roblox-luau-types` for type annotations, `roblox-luau-patterns` for ownership and lifecycle, and domain skills for Roblox APIs.

## Quick Reference

- Only `false` and `nil` are falsy. `0`, `""`, and `{}` are truthy.
- Equality does not coerce types. `0 == "0"` is false. Inequality is `~=`.
- Array conventions are 1-based. `#array` is meaningful only for a sequence without nil gaps.
- Assigning `nil` removes a table key. Assigning a table copies the reference. `table.clone` is shallow.
- Dictionary iteration order is unspecified. Do not make behavior depend on it.
- Dynamic keys require brackets: `record[field]`. Dot syntax uses a literal identifier.
- Missing arguments become `nil`; extra results and arguments can be discarded by context.
- Prefer an `if` expression over `condition and a or b` when `a` may be `false` or `nil`.
- Local names are scoped from their declaration onward. Forward-declare mutually recursive functions.
- Luau string patterns are not regular expressions. Their syntax and capabilities differ.
- Backtick interpolation and `..` concatenation are both valid. Choose the clearer form; collect many fragments and join once in a hot loop.

```luau
local label = if enabled then "On" else "Off"
local message = `{name}: {score}`

local byId: {[number]: string} = {}
byId[userId] = name

for index, value in values do
    print(index, value)
end
```

### Translation traps

- JavaScript `===`, `!==`, `null`, optional chaining, spread, arrow functions, and array methods are not Luau syntax.
- Python `None`, zero-based list assumptions, list comprehensions, exceptions, and implicit tuple behavior do not translate directly.
- `x or fallback` tests truthiness, not only absence. It replaces a valid `false` value.
- `typeof(value)` recognizes Roblox datatypes; `type(value)` reports the underlying Luau type category.

### Review

Valid Luau, intentional array/dictionary shape, no nil gaps in sequences, no assumed dictionary order, no accidental aliases, no cross-language syntax, and no clever boolean expression hiding `false` or `nil`.

> Detailed language traps and translation examples: [references/full.md](references/full.md)
