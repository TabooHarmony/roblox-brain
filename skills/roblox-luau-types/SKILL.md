---
name: roblox-luau-types
description: >
  Luau type system: annotations, generics, narrowing, inference philosophy,
  sealed/unsealed tables, exports, and Roblox-aware typing.
last_reviewed: 2026-05-27
sources:
  - https://luau-lang.org/typecheck
---

# Luau Type System

## When to Load

Load this skill when working with Luau type annotations, generics, union types, type narrowing, or sealed/unsealed table behavior. Also load when choosing strictness modes (`--!strict` vs `--!nonstrict`), designing module type exports, or typing metatable-backed objects.

## Quick Reference

**Strictness:** `--!strict` (new code), `--!nonstrict` (transitional), `--!nocheck` (legacy only). The New Type Solver (GA Nov 2025) is faster/more accurate.

**Inference philosophy:** Infer first, annotate boundaries (params, returns, exports). Don't annotate every local — noise hides signal.

**Sealed vs unsealed tables:**
```luau
local t = {}          -- unsealed: can add fields
t.x = 1               -- OK

local t: {x: number} = {x=1}  -- sealed: no new fields
t.y = 2               -- ERROR
```
Build tables fully before annotating. Passing/returning seals them.

**Unions & tagged unions:**
```luau
local id: string | number = "abc"
type State<T> = {kind:"loading"} | {kind:"ready", value:T} | {kind:"fail", msg:string}
-- Discriminate: if state.kind == "ready" then state.value is narrowed
```

**Narrowing:**
```luau
if typeof(x) == "string" then ... end          -- primitive narrowing
if inst:IsA("BasePart") then ... end           -- Instance narrowing
assert(val, "missing")                          -- non-nil narrowing
```

**Generics:** Use when input→output type matters. `function first<T>(list: {T}): T?`. Generic aliases: `type Result<T> = {success: boolean, value: T?}`. Never replace with `any`.

**Type exports:** `export type Foo = {...}` at module boundary. Consumers use `require` + `Types.Foo`.

**Object typing:** `export type Counter = typeof(setmetatable({} :: CounterData, Counter))` for precise self.

**Casts (::):** Precision tool to narrow overly generic inference — never to hide errors.

**Key mistakes:** Unsealed `any` propagation in nonstrict, sealing tables too early, unions without discriminants, annotating every local.

> Full reference: see `references/full.md`
