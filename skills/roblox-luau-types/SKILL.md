---
name: roblox-luau-types
description: "Use for Luau annotations, generics, unions, narrowing, strictness, sealed tables, module type exports, or typed metatables."
last_reviewed: 2026-05-27
sources:
  - https://luau-lang.org/typecheck
---

# Luau Type System

## When to Load

Load for Luau type system work: annotations, generics, union types, type narrowing, sealed/unsealed tables, strictness modes (`--!strict` vs `--!nonstrict`), module type exports, and metatable-backed object typing. For syntax questions, use `roblox-luau-core`. For OOP/async/modules, use `roblox-luau-patterns`.

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
