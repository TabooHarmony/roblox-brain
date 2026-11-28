---
name: roblox-physics
description: "Use when building or fixing Roblox physics: vehicles, ragdolls, projectiles, elevators, constraints, forces, network ownership."
when_to_use: "Also when parts fling, jitter, fall through floors or desync, and when tuning projectile or knockback feel."
last_reviewed: 2026-11-27
sources:
  - https://devforum.roblox.com/t/cframe-operations-for-the-rest-of-us/3546477
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/physics/mechanical-constraints.md
  - original
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine/classes/Humanoid.yaml
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine/classes/WorldRoot.yaml
  - https://create.roblox.com/docs/reference/engine/classes/AnimationConstraint
  - https://create.roblox.com/docs/reference/engine/classes/BasePart
  - https://create.roblox.com/docs/reference/engine/datatypes/RaycastParams
---

# Roblox Physics

## When to Load

Physics gameplay: vehicles, ragdolls, projectiles, contraptions, elevators, constraints and forces.

## Quick Reference

### Constraint Types
**Mechanical:** `HingeConstraint`, `PrismaticConstraint`, `CylindricalConstraint`, `BallSocketConstraint`, `UniversalConstraint`, `WeldConstraint`/`RigidConstraint`
**Motion:** `AlignPosition`, `AlignOrientation`, `LinearVelocity`, `AngularVelocity`, `VectorForce`, `Torque`
**Spring/Rope:** `SpringConstraint`, `RopeConstraint`, `RodConstraint`

Constraints connect two `Attachment`s; parent to part0. Actuators: `None`, `Motor`, `Servo`. Vehicles: motor hinges, spring suspension, servo steering.

### Character joints and ragdoll
New R15 rigs use `AnimationConstraint` (no `Motor6D`; `IsA("Motor6D")` is false) plus built-in enabled `BallSocketConstraint`s. Find joints with `FindFirstChildWhichIsA("AnimationConstraint")`, fall back to `Motor6D`. Procedural poses: multiply into `.Transform` in `PreSimulation`; never write C0. Ragdoll: `IsKinematic = false` + strength 0; don't add sockets on top.

### Authority and Network Ownership
Classic: `SetNetworkOwner(nil)` keeps it server-owned; player-owned physics is untrusted. Server Authority (`Workspace.AuthorityMode = Server`): core objects stay server-owned with prediction; `SetNetworkOwner()` is not a substitute.

### Queries and contacts
- `RaycastParams.Margin`/`SizeGradient`; `Shapecast` pose/size overrides.
- `CanQuery = false` works only with `CanCollide = false`; use `RespectCanCollide` or exclude helpers.
- `BasePart:BindToCollisionSummaries`: point, normal, relative velocity; local only.
- Free parts can hold more contacts than they touch (field-measured): compare scene-wide `Stats.ContactsCount` before/after. Anchor resting debris.

### Common Gotchas
- Constraints do nothing on Anchored parts; both attachments required
- Set velocity on `AssemblyRootPart`; judge launches by assembly COM
- Raycast for hitscan, `Touched` only for slow projectiles; always set a lifetime
See `references/full.md` for recipes, API details, and checks.
