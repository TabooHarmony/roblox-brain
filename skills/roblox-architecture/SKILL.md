---
name: roblox-architecture
description: "Use when starting or refactoring a Roblox project, choosing service or module structure, or making client-server architecture decisions."
last_reviewed: 2026-07-12
sources:
  - https://create.roblox.com/docs/projects/data-model
  - https://create.roblox.com/docs/projects/client-server
  - https://create.roblox.com/docs/scripting/locations
  - https://create.roblox.com/docs/scripting/security/access-control
  - original
---

# roblox architecture

## When to Load

Load when deciding where code and assets belong, introducing service or controller modules, or changing the client/server boundary.

## Quick Reference

- Put authoritative game rules in `ServerScriptService`; keep server-only templates and secrets in `ServerStorage`.
- Put only genuinely shared modules, remotes, and public assets in `ReplicatedStorage`.
- Treat `LocalScript` code and replicated contents as observable and modifiable by the player.
- Give each module one owner and one clear contract. Use signals or a coordinator for cross-system communication instead of circular `require` calls.
- Use one small bootstrap on each side, then initialize feature modules in an explicit order.
- Keep UI and input controllers on the client. Keep rewards, inventory, combat outcomes, and persistence on the server.

**Need the details?** Load `references/full.md` for layouts, lifecycle code, and boundary checks.
