---
name: roblox-tooling
description: "Use when configuring Roblox tooling such as Rojo, Wally, Selene, StyLua, Lune, Aftman, luau-lsp, or CI/CD."
last_reviewed: 2026-07-12
sources:
  - https://rojo.space/docs/
  - https://wally.run/
  - https://kampfkarren.github.io/selene/
  - https://raw.githubusercontent.com/JohnnyMorganz/StyLua/master/README.md
  - https://lune-org.github.io/docs/
  - https://raw.githubusercontent.com/LPGhatguy/aftman/main/README.md
  - https://raw.githubusercontent.com/rojo-rbx/rokit/main/README.md
  - https://raw.githubusercontent.com/JohnnyMorganz/luau-lsp/main/README.md
  - original
---

# roblox tooling

## When to Load

Load when setting up a filesystem workflow, pinning tools, adding packages, configuring lint or format checks, generating a sourcemap, or building CI for a Roblox project.

## Quick Reference

- Use Rojo when the source of truth should live in files and sync or build into Studio.
- Use Wally only when the project wants package manifests and a lockfile; keep package scope and server/client placement explicit.
- Pin tools with Aftman only when maintaining an existing Aftman project. Aftman is archived; for a new project, evaluate a maintained manager such as Rokit.
- Run Selene and StyLua in check mode in CI. Do not let a formatter rewrite a contributor's branch silently.
- Use Lune for standalone Luau scripts or test helpers when its standard libraries fit the task.
- Generate a Rojo sourcemap for editor tooling when the project needs Roblox-aware navigation.

**Need the details?** Load `references/full.md` for setup, file layout, and CI examples.
