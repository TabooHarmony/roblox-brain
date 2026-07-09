---
name: roblox-tooling
description: "Use when configuring Roblox tooling such as Rojo, Wally, Selene, StyLua, Lune, Aftman, luau-lsp, or CI/CD."
last_reviewed: 2026-05-27
sources:
  - https://raw.githubusercontent.com/brockmartin/roblox-game-skill/main/references/tooling-ecosystem.md
  - https://rojo.space/docs
  - https://wally.run
---

## When to Load

Load when the task involves Rojo setup or `default.project.json`, Wally package management, Selene/StyLua linting/formatting, Lune scripting, Aftman toolchain config, CI/CD pipelines, or `.server.luau`/`.client.luau` file naming. Hand off to domain skills for game code, `roblox-luau-core` for language questions, `roblox-testing` for test patterns.

## Quick Reference

**Aftman** (toolchain pinning): `aftman.toml` — all tools installed via `aftman install`.
```
[tools]
rojo = "rojo-rbx/rojo@7.4.4"
wally = "UpliftGames/wally@0.3.2"
selene = "kampfkarren/selene@0.27.1"
stylua = "JohnnyMorganz/StyLua@2.0.2"
lune = "lune-org/lune@0.8.0"
```

**Rojo** (filesystem → Studio): `default.project.json` maps dirs to services.
- File suffixes: `.server.luau` (Script), `.client.luau` (LocalScript), `.luau` (ModuleScript), `init.luau` (folder-as-ModuleScript)
- Commands: `rojo serve` (live sync), `rojo build -o game.rbxl`, `rojo sourcemap ... -o sourcemap.json`

**Wally** (package manager): `wally.toml` with realms `shared`/`server`/`dev`.
- `wally install` → `/Packages/` (never commit this dir; do commit `wally.lock`)
- Format: `scope/package@version` e.g. `evaera/promise@4.0.0`

**Selene** (linter): Needs `std = "roblox"` in `selene.toml`.
- `selene src/` (lint), `--no-color` for CI, `-- selene: allow(rule)` inline

**StyLua** (formatter): `stylua.toml` — enforce style across team.
- `stylua src/` (format), `--check src/` (CI verify), `-- stylua: ignore` inline

**Lune** (headless Luau): `lune run script.luau` — built-ins: `@lune/fs`, `@lune/net`, `@lune/process`, `@lune/serde`

**luau-lsp**: Generate sourcemap for IntelliSense. VS Code: enable `luau-lsp.sourcemap.autogenerate`.

**CI pipeline**: Aftman install → selene → stylua --check → luau-lsp analyze → lune test → rojo build.

**Gitignore essentials**: `/Packages/`, `*.rbxl`, `sourcemap.json`, `/.aftman/`, `/build/`

**Full reference**: `references/full.md`
