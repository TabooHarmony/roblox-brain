---
name: roblox-luau-mastery
description: >
  Router skill. Luau language mastery has been split into three focused skills
  for better context efficiency. Load the specific one you need.
last_reviewed: 2026-05-27
sources: []
---

# Luau Language Mastery (Index)

## When to Load

Load to route Luau questions to the right sub-skill (core syntax, types, or patterns). Always pair with one of `roblox-luau-core`, `roblox-luau-types`, or `roblox-luau-patterns`.

This skill has been split into three focused skills for better context efficiency. Load the one that matches your task:

## Routing

| Task | Load |
|------|------|
| Syntax, tables, control flow, string patterns, math, idioms, scope, closures, sharp edges, JS→Luau porting | `roblox-luau-core` |
| Type annotations, generics, narrowing, inference, strictness modes, exports, sealed/unsealed tables | `roblox-luau-types` |
| OOP (metatables, inheritance), async (Promises, pcall, coroutines), module structure, service pattern, Roblox idioms (Instance creation, events, task library) | `roblox-luau-patterns` |

## Quick Decision

- "How do I write this in Luau?" → `roblox-luau-core`
- "How should I type this?" → `roblox-luau-types`
- "How should I structure this?" → `roblox-luau-patterns`

## Quick Reference

- Luau is NOT Lua 5.1. Has: generics, `continue`, `+=`, string interpolation (backticks), floor division `//`
- Arrays are 1-based. `#tbl` for length. Generalized iteration: `for k, v in tbl do`
- Always use `task.wait/spawn/delay` (never deprecated `wait/spawn/delay`)
- Instance.new: configure properties THEN set Parent last (replication race)
- Services: `game:GetService("Name")` at top of script, stored in locals
- Methods: use `:` (implicit self) for instance methods, `.` for constructors/static
- Prefer backtick interpolation over `..` concatenation
- Local function order: callees above callers (no hoisting)
- Only `nil` and `false` are falsy
