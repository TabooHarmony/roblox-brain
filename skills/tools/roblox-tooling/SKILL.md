---
name: roblox-tooling
description: "Use when setting up or fixing Roblox tooling: Rojo, Wally, pesde, Selene, StyLua, Lune, Rokit, luau-lsp, tests, or CI/CD."
when_to_use: "Also when sync or builds break, packages won't install, lint or format errors appear, or reviewing the project's toolchain."
last_reviewed: 2026-10-14
sources:
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine/classes/ScriptEditorService.yaml
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine/classes/ChangeHistoryService.yaml
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine/classes/InstanceFileSyncService.yaml
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/scripting/sync.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine/classes/Players.yaml
  - https://rojo.space/docs/
  - https://wally.run/
  - https://kampfkarren.github.io/selene/
  - https://raw.githubusercontent.com/JohnnyMorganz/StyLua/master/README.md
  - https://lune-org.github.io/docs/
  - https://raw.githubusercontent.com/LPGhatguy/aftman/main/README.md
  - https://raw.githubusercontent.com/rojo-rbx/rokit/main/README.md
  - https://raw.githubusercontent.com/rojo-rbx/rojo/v7.7.1/src/cli/syncback.rs
  - https://docs.pesde.dev/reference/manifest/
  - https://raw.githubusercontent.com/JohnnyMorganz/luau-lsp/main/README.md
  - https://raw.githubusercontent.com/lest-luau/lest/main/docs/backends.md
  - https://raw.githubusercontent.com/lest-luau/lest/main/docs/continuous-integration.md
  - https://raw.githubusercontent.com/UpliftGames/wally/main/src/resolution.rs
  - https://create.roblox.com/docs/llms.txt
  - https://devforum.roblox.com/t/evolving-luau-oss-community-contributions-more/4566806
  - original
---

# roblox tooling

## When to Load

Load for filesystem workflows, tool/package pins, linting, sourcemaps, and CI.

## Quick Reference

- Rojo when files own the truth; Wally for manifests+lockfile (explicit realm). Pin tools via the project's manager; new projects lead with Rokit (Aftman archived, reads `aftman.toml`).
- Selene + StyLua check-mode in CI (no silent rewrites); Lune for standalone Luau; Rojo sourcemap for editor tooling.
- CI gates on parsed results and counts, not exit codes; split logic/file/HTTP/engine suites (full.md).

**Source-of-truth first.** Know Studio vs files before editing; never assume sync. `rojo syncback` pulls saved-place edits, not live two-way sync — dry-run first. Don't impose optional tools. TestEZ archived: keep where used.

**Script writes from plugin/MCP** go through `ScriptEditorService:UpdateSourceAsync` (raw `.Source` writes can clobber an open editor) + one `ChangeHistoryService` recording per bounded mutation. Script Sync conflicts resolve as Keep Studio vs Keep Disk — never assume either side wins. See full.md §§1b–1d.

**Details:** `references/full.md` (setup, file layout, CI examples).
