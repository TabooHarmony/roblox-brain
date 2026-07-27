---
name: roblox-architecture
description: "Use when assigning Roblox feature ownership, code location, dependencies, startup, or client-server boundaries without imposing a framework."
last_reviewed: 2026-07-26
sources:
  - https://create.roblox.com/docs/projects/data-model
  - https://create.roblox.com/docs/projects/client-server
  - https://create.roblox.com/docs/scripting/locations
  - https://create.roblox.com/docs/scripting/security/access-control
  - original
---

# Roblox Architecture

## When to Load

Load when code ownership is unclear, a feature crosses client and server, startup order matters, or a module is being split. Do not load merely to add a service/controller framework to a small feature.

## Quick Reference

### Start from one owner

For each behavior, name:

- authoritative state and who may mutate it;
- public operations and callers;
- Roblox instances, connections, and tasks it owns;
- persistence or network boundary;
- startup and teardown conditions.

Group by feature when that keeps one change together. Split server, client, and shared code only where the runtime boundary requires it. Shared code contains no secrets or authoritative mutable state because replicated code is readable by clients.

### Use the smallest dependency shape

Direct module calls are the default for a stable dependency. Use a signal when one publisher has genuinely independent observers. Do not add a global event bus, dependency container, manager class, or `Init`/`Start` ceremony to hide an ordinary dependency.

Keep module top-level work cheap and non-yielding. A small bootstrap owns only startup that truly needs ordering. Call ordered startup sequentially and fail visibly. Concurrency must be explicit and safe, not automatic `task.spawn` around every module.

Bound `WaitForChild` when a dependency arrives through replication and handle
timeout. An unbounded wait turns a missing instance into a silent startup hang.

### Enforce runtime authority

The client presents input and prediction. The server validates and decides authoritative outcomes. Remotes are APIs with types, bounds, state, ownership, abuse controls, and failure behavior. Route implementation details to `roblox-networking` and `roblox-security`.

### Split only for evidence

Split when there is a separate lifecycle or authority boundary, a distinct persistence contract, an independently testable pure core, or unrelated reasons to change. Do not split for folder symmetry or speculative reuse.

### Review

One canonical owner per state mutation, no circular require, no hidden startup yield, no replicated secret or trust decision, no duplicate save or purchase owner, explicit cleanup, and the smallest structure that keeps the feature understandable.

> Detailed layouts, dependency rules, and startup examples: [references/full.md](references/full.md)
