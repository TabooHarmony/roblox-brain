---
name: roblox-luau-types
description: "Use when adding or fixing Luau type annotations: generics, unions, narrowing, strict mode, sealed tables, module type exports, typed metatables."
when_to_use: "Also for type checker errors and warnings, --!strict migration, luau-lsp diagnostics, and reviewing typed APIs."
last_reviewed: 2026-11-27
sources:
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/luau/type-checking.md
  - https://luau.org/types/type-functions/
  - https://luau.org/types/tables
  - https://create.roblox.com/docs/reference/engine/classes/Workspace
  - https://devforum.roblox.com/t/sudden-return-type-error/4939413
  - https://devforum.roblox.com/t/how-to-make-array-return-a-union-type/4549941
  - https://raw.githubusercontent.com/Kampfkarren/kampfkarren-luau-guidelines/main/README.md
---

# Luau Type System

## When to Load

Annotations, inference, narrowing, strictness, exports, solver features. Syntax: `roblox-luau-core`; lifecycle: `roblox-luau-patterns`.

## Quick Reference

**Strictness:** `--!strict` for maintained code, `--!nonstrict` while transitioning, `--!nocheck` only for legacy or generated code. Directives and project settings select it.

**New solver gate:** `keyof`, `rawkeyof`, `setmetatable<T, M>`, `type function`s, and `read` members need the new type solver. Strict projects opt in with `Workspace.UseNewLuauTypeSolver = Enabled`; `Default` follows the rollout, so a "sudden" error in unchanged code may be a solver switch.

**Inference:** annotate boundaries (params, returns, exports), not every local.

**Sealed vs unsealed tables:** An unannotated local table stays open until annotated, returned, or out of scope. Build it fully before annotating.

**Unions:** `local id: string | number` is a union; prefer tagged unions (`type State<T> = {kind:"loading"} | {kind:"ready", value:T}`) and discriminate on `kind` to narrow.

**Narrowing:** `typeof`, `IsA`, assertions, tagged discriminants.

**Missing keys:** use `{ [K]: V? }` when lookups may miss; narrow before use.

**Optional returns:** write `return nil`; falling off the end returns no values and is flagged.

**Closed vocabularies:** prefer literal unions, declared once (string array literals may widen to `string`); `never` checks flag missing branches. Keep requires static.

**Generics:** when input→output type matters: `function first<T>(list: {T}): T?`. Never replace with `any`.

**Type exports:** `export type Foo = {...}` at module boundaries; consumers use `Types.Foo`.

**Object typing:** `typeof(setmetatable({} :: CounterData, Counter))` types precise self; the new solver adds `setmetatable<T, M>` directly.

**Casts (::):** For narrowing overly generic inference, never for hiding errors.

**Trust boundaries:** Annotations contract with the compiler, not runtime data. Remotes, DataStores, HTTP and attributes still need runtime checks.

**Review:** no hidden `any`, premature sealing, unchecked casts, or solver-blind rewrites.

> Full reference: see `references/full.md`
