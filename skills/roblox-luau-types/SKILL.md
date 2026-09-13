---
name: roblox-luau-types
description: "Use for Luau annotations, generics, unions, narrowing, strictness, sealed tables, module type exports, typed metatables, or new-solver features."
last_reviewed: 2026-09-13
sources:
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/luau/type-checking.md
  - https://luau.org/types/type-functions/
---

# Luau Type System

## When to Load

Load for Luau types: annotations, generics, unions, narrowing, sealed/unsealed tables, strictness (`--!strict` vs `--!nonstrict`), module type exports, metatable-backed object typing, and new-solver features (`keyof`, `setmetatable<T, M>`, type functions, `read` members). For syntax, use `roblox-luau-core`; for OOP/async, `roblox-luau-patterns`.

## Quick Reference

**Strictness:** `--!strict` for maintained code, `--!nonstrict` while transitioning, `--!nocheck` only for legacy or generated code. Directives and project settings select the mode; never assume one global default.

**New solver gate:** `keyof`, `rawkeyof`, `setmetatable<T, M>`, `type function`s, and `read` members need the new type solver. It is on by default for `nocheck`/`nonstrict` projects; strict projects need `Workspace.UseNewLuauTypeSolver = Enabled` (Scripting category). Errors here usually mean the wrong solver, not wrong syntax.

**Inference philosophy:** Infer first; annotate boundaries (params, returns, exports). Don't annotate every local.

**Sealed vs unsealed tables:** An empty `local t = {}` stays open to new fields; annotating or passing it seals it, so later additions error. Build tables fully before annotating.

**Unions:** `local id: string | number` is a union; prefer tagged unions (`type State<T> = {kind:"loading"} | {kind:"ready", value:T}`) and discriminate on `kind` to narrow.

**Narrowing:** `typeof(v) == "string"` narrows primitives, `instance:IsA("BasePart")` narrows Instances, and `assert(v, "msg")` narrows away `nil`. Discriminant fields narrow tagged unions; see full reference for worked examples.

**Generics:** Use when input→output type matters: `function first<T>(list: {T}): T?`, or `type Result<T> = {success: boolean, value: T?}`. Never replace with `any`.

**Type exports:** `export type Foo = {...}` at module boundaries; consumers use `Types.Foo`.

**Object typing:** `typeof(setmetatable({} :: CounterData, Counter))` types precise self; the new solver adds `setmetatable<T, M>` directly.

**Casts (::):** For narrowing overly generic inference, never for hiding errors.

**Trust boundaries:** Annotations contract with the compiler, not with runtime data. Remotes, DataStores, HttpService, and attributes still need checks; inside a trusted boundary, let types carry the load.

**Key mistakes:** `any` propagation in nonstrict, sealing too early, unions without discriminants, annotating every local, deleting new-solver syntax without checking the solver setting.

> Full reference: see `references/full.md`
