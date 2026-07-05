---
name: roblox-physics
description: Constraints, VehicleSeat, ragdoll, projectiles, Attachment patterns, network ownership.
last_reviewed: 2026-05-27
sources:
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/physics/mechanical-constraints.md
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/physics/mover-constraints.md
---

## When to Load

Use this skill when building physics-driven gameplay: vehicles, ragdolls, projectiles, mechanical contraptions, elevators, swinging platforms, or anything using constraints and forces.

## Quick Reference

### Constraint Types
**Mechanical:** `HingeConstraint` (doors/wheels), `PrismaticConstraint` (elevators/pistons), `CylindricalConstraint` (telescoping), `BallSocketConstraint` (ragdoll/chains), `UniversalConstraint` (steering), `WeldConstraint`/`RigidConstraint` (rigid attach)
**Motion:** `AlignPosition`, `AlignOrientation`, `LinearVelocity`, `AngularVelocity`, `VectorForce`, `Torque`
**Spring/Rope:** `SpringConstraint` (suspension/trampolines), `RopeConstraint` (grapple, slack), `RodConstraint` (rigid link)

### Attachment Pattern
All constraints connect via `Attachment` objects, not Parts directly. Create Attachment on each part, set `constraint.Attachment0`/`Attachment1`, parent constraint to part0. Actuator types: `None`, `Motor` (constant velocity), `Servo` (target position/angle).

### Vehicles
Wheel = `HingeConstraint` (ActuatorType.Motor) + `SpringConstraint` for suspension. Steer = Hinge with ActuatorType.Servo. Rear wheels get throttle AngularVelocity, front wheels get servo TargetAngle. Use `CustomPhysicalProperties` on wheels for friction tuning.

### Ragdoll
Replace Motor6Ds with `BallSocketConstraint`: create Attachments from motor.C0/C1, set `LimitsEnabled=true`, `UpperAngle=45`. Keep Root Motor6D for HRP. Set humanoid state to `Physics`. Re-enable motors to recover.

### Network Ownership
Default: nearest player owns unanchored physics (exploitable!). `part:SetNetworkOwner(nil)` = server-owned (secure, laggy). `part:SetNetworkOwner(player)` = player-owned (responsive). **Rule:** NPCs/world objects → server. Vehicles → driver player. Always set explicitly on important physics objects.

### Common Gotchas
- Constraints do nothing on Anchored parts
- Both Attachment0 AND Attachment1 required (missing one = silent fail)
- Over-constraining = jitter. Tune mass with `CustomPhysicalProperties`
- Use Raycast for hitscan, `Touched` only for slow physics projectiles
- Always set lifetime on physics projectiles (forgotten ones kill perf)
**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
