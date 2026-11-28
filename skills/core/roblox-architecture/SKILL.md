---
name: roblox-architecture
description: "Use when adding, moving, refactoring, or reviewing Roblox feature ownership, code layout, dependencies, startup, or client-server boundaries."
when_to_use: "Also when deciding where code goes, splitting a large script, fixing load-order or require cycles, untangling services/controllers, or auditing project structure."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/projects/data-model
  - https://create.roblox.com/docs/projects/client-server
  - https://create.roblox.com/docs/scripting/locations
  - https://create.roblox.com/docs/scripting/security/access-control
  - https://create.roblox.com/docs/reference/engine/classes/CollectionService
  - https://create.roblox.com/docs/projects/server-authority
  - https://create.roblox.com/docs/projects/file-based-workflows
  - https://raw.githubusercontent.com/Ukendio/jecs/v0.11.0/README.md
  - original
---

# Roblox Architecture

## When to Load

Load for ownership, integration, boundaries, startup, or module splits.

## Quick Reference

Reuse proven project modules first; inspect their contracts and cleanup paths.

### Start from one owner

For each behavior, name its authoritative state and mutators, public operations, owned instances/connections/tasks, persistence or network boundary, and startup/teardown.

Group by feature; split server/client/shared only at runtime boundaries. Shared code has no secrets.

### Use the smallest dependency shape

Direct module calls by default; a signal only for genuinely independent observers. No event bus, container or `Init`/`Start` ceremony for an ordinary dependency.

Keep module top level cheap and non-yielding. A small bootstrap owns ordered startup and fails visibly.

Bound `WaitForChild`; unbounded waits hang silently.

### Join and boot order (field-tested)

- Admission decides before any other join hook; wire `PlayerAdded` once, in order, and loop `Players:GetPlayers()`.
- Spawn with `LoadCharacterAsync()` (`LoadCharacter()` is deprecated).
- Long non-yielding boot work hits `Script timeout`; a `task.spawn` in `Init` dies with it. Defer warm-up.
- Live clients often find everything already replicated, so start-up lands in one frame. Test with `task.wait(8)` first.
- `GetTagged` searches the whole DataModel, including `ServerStorage` copies.

### Enforce runtime authority

The client presents and predicts; the server decides. Under Server Authority, gameplay is one shared module bound with `BindToSimulation`; destroy instances outside the simulation. Remotes: `roblox-networking`, `roblox-security`.

### Split only for evidence

Split for a separate lifecycle or authority boundary, persistence contract, testable pure core, or unrelated reasons to change.

### Data-oriented alternative: only on evidence

An ECS earns its cost only for many similar entities updated every frame by order-independent logic; hooks enforce invariants, ordered systems decide. Pitfalls: full.md.

### Review

One owner per mutation, no hidden startup yield, explicit cleanup, smallest traceable structure. Tags discover, attributes configure.

> Details: [references/full.md](references/full.md)
