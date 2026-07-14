---
name: roblox-npc-ai
description: "Use when creating Roblox NPCs or enemies with pathfinding, state machines, line-of-sight or FOV detection, spawns, or AI update loops."
last_reviewed: 2026-07-13
sources:
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/characters/pathfinding.md
  - https://devforum.roblox.com/t/improving-pathfinding-quality-with-new-algorithm/3258657
  - https://create.roblox.com/docs/projects/server-authority
---

# Roblox NPC & AI

## When to Load

Load for NPCs/enemies: pathfinding, state machines, LOS/FOV detection, spawns, AI loops, or physics ownership.

## Quick Reference

### PathfindingService

```luau
local path = PathfindingService:CreatePath({
    AgentRadius = 2, AgentHeight = 5, AgentCanJump = true,
    Costs = { Water = 20, DangerZone = math.huge },
})
path:ComputeAsync(npcPos, targetPos)
if path.Status ~= Enum.PathStatus.Success then return end
for _, wp in path:GetWaypoints() do
    if wp.Action == Enum.PathWaypointAction.Jump then humanoid.Jump = true end
    humanoid:MoveTo(wp.Position)
    if not humanoid.MoveToFinished:Wait() then return end
end
```

- Recompute on blocked with a bounded retry or cancellation policy.
- Test `Workspace.PathfindingUseImprovedSearch` on representative maps before rollout.
- Avoid long requests and repeated recomputation. Moving collidable geometry can trigger navigation-mesh work.
- Region modifiers: anchored part + `PathfindingModifier` Label → Costs
- `PassThrough = true` for doors; `PathfindingLink` for disconnected navmesh
- `math.huge` cost = non-traversable

### State Machine

`idle → patrol → chase → attack → flee → dead`
- idle/patrol → chase (player detected) → attack (in range) → idle (lost)
- any → flee (health low) → idle (safe); any → dead (health ≤ 0)
- Transitions own movement changes, target cleanup, and cancellation

### Detection (distance → FOV → LOS)

1. **Distance** `(a-b).Magnitude` — cheapest, always first
2. **FOV** `forward:Dot(toTarget)` cosine — use a configured cone for the game, not a universal angle
3. **LOS** `workspace:Raycast` — expensive, last
- If the design includes hearing or proximity detection, make it a separate configured signal rather than a universal FOV bypass.

### Network Ownership
- Classic projects may use `SetNetworkOwner(nil)` for physics-sensitive NPCs, but it is not complete security. In Server Authority projects, configure the authority model instead of treating network ownership as the security boundary.

### Update Loop

- Throttle and stagger AI based on NPC count, path cost, and profiler evidence, not a universal tick rate. Keep NPC decisions and movement server-side; client code may handle presentation.

For spawners, lifecycle cleanup, timeout handling, and performance budgets, load `references/full.md`.
