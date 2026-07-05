---
name: roblox-architecture
description: Service hierarchy, 7 foundational patterns, cross-platform input. Client-server architecture, module patterns, framework options.
last_reviewed: 2026-05-26
sources:
  - https://github.com/brockmartin/roblox-game-skill (MIT)
---

# Roblox Game Architecture Reference

---

## When to Load

Load when starting a new project, organizing/refactoring an existing codebase, choosing module/folder structure, or making service-hierarchy decisions.

## Quick Reference

**Load Full Reference below only when you need specific folder layouts or framework comparisons.**

Key rules:
- ServerScriptService: server logic (never visible to client)
- ServerStorage: server-only assets/data
- ReplicatedStorage: shared modules, RemoteEvents, assets both sides need
- StarterPlayerScripts: client controllers (run once per player)
- StarterGui: ScreenGuis (cloned to PlayerGui on spawn)
- Script types: Script (server), LocalScript (client), ModuleScript (shared, returns one table)
- Communication: RemoteEvent (fire-and-forget), RemoteFunction (request-response, avoid for client→server)
- Module pattern: return a table of functions. One module = one responsibility.
- Avoid circular requires. Use events/signals for cross-module communication.
- Single entry point per side: one server Script requires service modules, one LocalScript requires controllers.
**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
