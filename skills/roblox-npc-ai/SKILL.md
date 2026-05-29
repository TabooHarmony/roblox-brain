---
name: roblox-npc-ai
description: Pathfinding, state machines, NPC detection (LOS/FOV), spawn systems, enemy AI patterns.
last_reviewed: 2026-05-27
sources:
  - https://github.com/Roblox/creator-docs/blob/main/content/en-us/characters/pathfinding.md
  - https://github.com/Echolewron/rbx-enemy-ai (MIT, FSM + raycasting + A*)
---

# Roblox NPC & AI

Use this skill when creating NPCs, enemies, bosses, or autonomous characters that navigate, detect players, or make decisions.

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

- Connect `path.Blocked` to recompute when world changes
- Region modifiers: Anchored part + `PathfindingModifier` with Label → Costs
- `PassThrough = true` for doors; `PathfindingLink` for disconnected navmesh
- `math.huge` cost = non-traversable

### State Machine

`idle → patrol → chase → attack → flee → dead`
- idle/patrol → chase (player detected) → attack (in range) → idle (lost)
- any → flee (health low) → idle (safe); any → dead (health ≤ 0)
- Transition func handles walk speed changes, clears target on idle

### Detection (distance → FOV → LOS)

1. **Distance** `(a-b).Magnitude` — cheapest, always first
2. **FOV** `forward:Dot(toTarget)` cosine — ~120° cone
3. **LOS** `workspace:Raycast` — expensive, last
- Skip dead players. Close-range (~30%) bypasses FOV (hearing)

### Spawners

- Track active enemies, cap count, remove on `Humanoid.Died`
- Clone → `PivotTo` → parent; `task.delay(3, Destroy)` for death anim
- Wave: `{enemies={{template, count}}, spawnDelay, waveDelay}`

### Network Ownership — MUST DO

```luau
for _, part in model:GetDescendants() do
    if part:IsA("BasePart") then part:SetNetworkOwner(nil) end
end
```
Without this, exploiters fling NPCs. Server = safe but 30Hz tick.

### Update Loop

- Throttle AI to 5-10 ticks/sec, NOT every Heartbeat
- Stagger large batches (5/frame); ALL NPC logic server-side only

### Pitfalls

- No `path.Blocked` handler → stale paths
- No `ComputeAsync` fallback → frozen NPCs
- `MoveTo` 8-sec timeout; handle `reached = false`
- Forget `SetNetworkOwner(nil)` → exploiters fling NPCs
- Dead corpses not destroyed → memory leak
- 50 NPCs pathfinding same frame → server lag spike
**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
