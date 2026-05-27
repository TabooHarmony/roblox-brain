---
name: roblox-npc-ai
description: >
  NPC behavior, pathfinding, state machines, enemy AI, spawn systems.
  Use when creating NPCs, enemies, bosses, or any autonomous character behavior.
last_reviewed: 2026-05-27
---

# Roblox NPC & AI Behavior

Use this skill when creating NPCs, enemies, bosses, pets, or any entity that needs autonomous behavior.

## Pathfinding

### Basic PathfindingService Usage

```luau
local PathfindingService = game:GetService("PathfindingService")

local function moveTo(humanoid: Humanoid, target: Vector3)
    local path = PathfindingService:CreatePath({
        AgentRadius = 2,      -- NPC width/2
        AgentHeight = 5,      -- NPC height
        AgentCanJump = true,
        AgentCanClimb = false,
        WaypointSpacing = 4,  -- distance between waypoints
    })

    path:ComputeAsync(humanoid.RootPart.Position, target)

    if path.Status == Enum.PathStatus.Success then
        local waypoints = path:GetWaypoints()
        for _, waypoint in waypoints do
            if waypoint.Action == Enum.PathWaypointAction.Jump then
                humanoid.Jump = true
            end
            humanoid:MoveTo(waypoint.Position)
            humanoid.MoveToFinished:Wait()
        end
    end
end
```

### Path Recomputation

Paths go stale when the world changes or the target moves. Recompute periodically:

```luau
local function chaseTarget(humanoid: Humanoid, target: BasePart)
    local path = PathfindingService:CreatePath({AgentRadius = 2, AgentHeight = 5})

    while target and target.Parent do
        path:ComputeAsync(humanoid.RootPart.Position, target.Position)
        if path.Status ~= Enum.PathStatus.Success then
            task.wait(0.5)
            continue
        end

        local waypoints = path:GetWaypoints()
        for i, waypoint in waypoints do
            -- Recompute if target moved significantly
            if (target.Position - waypoints[#waypoints].Position).Magnitude > 10 then
                break
            end
            if waypoint.Action == Enum.PathWaypointAction.Jump then
                humanoid.Jump = true
            end
            humanoid:MoveTo(waypoint.Position)

            local reached = humanoid.MoveToFinished:Wait()
            if not reached then break end
        end
        task.wait(0.1)
    end
end
```

### Pathfinding Modifiers

Use PathfindingModifiers to make NPCs prefer/avoid areas:

```luau
-- Make water expensive to traverse
local waterPart = workspace.Lake
local modifier = Instance.new("PathfindingModifier")
modifier.Label = "Water"
modifier.PassThrough = false -- can still traverse, just costly
modifier.Parent = waterPart

-- In CreatePath:
local path = PathfindingService:CreatePath({
    AgentRadius = 2,
    AgentHeight = 5,
    Costs = {
        Water = 20, -- 20x more expensive than normal ground
    },
})
```

## State Machine Pattern

The most reliable NPC AI pattern. Every NPC has a current state and transitions between them.

```luau
type State = "idle" | "patrol" | "chase" | "attack" | "flee" | "dead"

type NPCController = {
    state: State,
    humanoid: Humanoid,
    rootPart: BasePart,
    target: Player?,
    config: NPCConfig,
}

type NPCConfig = {
    detectionRange: number,
    attackRange: number,
    fleeHealthPercent: number,
    patrolPoints: {Vector3},
    attackCooldown: number,
}

local function updateNPC(npc: NPCController, dt: number)
    local state = npc.state

    if state == "idle" then
        -- Check for nearby players
        local nearest = findNearestPlayer(npc.rootPart.Position, npc.config.detectionRange)
        if nearest then
            npc.target = nearest
            npc.state = "chase"
        elseif #npc.config.patrolPoints > 0 then
            npc.state = "patrol"
        end

    elseif state == "patrol" then
        -- Move between patrol points
        local nearest = findNearestPlayer(npc.rootPart.Position, npc.config.detectionRange)
        if nearest then
            npc.target = nearest
            npc.state = "chase"
        else
            patrolStep(npc)
        end

    elseif state == "chase" then
        if not npc.target or not npc.target.Character then
            npc.state = "idle"
            return
        end

        local dist = (npc.rootPart.Position - npc.target.Character.HumanoidRootPart.Position).Magnitude

        -- Check flee condition
        if npc.humanoid.Health / npc.humanoid.MaxHealth < npc.config.fleeHealthPercent then
            npc.state = "flee"
        elseif dist <= npc.config.attackRange then
            npc.state = "attack"
        else
            chaseTarget(npc.humanoid, npc.target.Character.HumanoidRootPart)
        end

    elseif state == "attack" then
        if not npc.target or not npc.target.Character then
            npc.state = "idle"
            return
        end
        performAttack(npc)
        npc.state = "chase" -- return to chase after attack

    elseif state == "flee" then
        fleeFromTarget(npc)
        -- Return to idle if safe
        if not npc.target or getDistanceToTarget(npc) > npc.config.detectionRange * 1.5 then
            npc.state = "idle"
        end

    elseif state == "dead" then
        -- Cleanup handled elsewhere
        return
    end
end
```

## Detection Patterns

### Line of Sight

```luau
local function hasLineOfSight(from: Vector3, to: Vector3, ignore: {Instance}): boolean
    local params = RaycastParams.new()
    params.FilterDescendantsInstances = ignore
    params.FilterType = Enum.RaycastFilterType.Exclude

    local result = workspace:Raycast(from, (to - from), params)
    return result == nil -- nil means nothing blocked the ray
end
```

### Cone of Vision

```luau
local function isInFieldOfView(npcCFrame: CFrame, targetPos: Vector3, fovDegrees: number): boolean
    local toTarget = (targetPos - npcCFrame.Position).Unit
    local forward = npcCFrame.LookVector
    local dot = forward:Dot(toTarget)
    local angle = math.acos(math.clamp(dot, -1, 1))
    return angle <= math.rad(fovDegrees / 2)
end
```

### Hearing (Distance-Based)

```luau
local function canHear(npcPos: Vector3, soundPos: Vector3, loudness: number): boolean
    local dist = (npcPos - soundPos).Magnitude
    return dist <= loudness -- loudness acts as hearing range
end
```

## Spawn Systems

### Wave Spawner

```luau
local function spawnWave(waveConfig: {enemyType: string, count: number}, spawnPoints: {BasePart})
    local spawned = {}
    for i = 1, waveConfig.count do
        local spawnPoint = spawnPoints[math.random(1, #spawnPoints)]
        local enemy = createEnemy(waveConfig.enemyType)
        enemy:PivotTo(spawnPoint.CFrame + Vector3.new(0, 3, 0))
        enemy.Parent = workspace.Enemies
        table.insert(spawned, enemy)
        task.wait(0.5) -- stagger spawns
    end
    return spawned
end
```

### Respawn with Pooling

```luau
local RESPAWN_TIME = 10
local MAX_ENEMIES = 20

local activeEnemies: {Model} = {}
local deadEnemies: {Model} = {}

local function onEnemyDied(enemy: Model)
    table.insert(deadEnemies, {enemy = enemy, diedAt = os.clock()})
    local idx = table.find(activeEnemies, enemy)
    if idx then table.remove(activeEnemies, idx) end
end

-- Respawn loop
task.spawn(function()
    while true do
        task.wait(1)
        if #activeEnemies >= MAX_ENEMIES then continue end

        for i = #deadEnemies, 1, -1 do
            local entry = deadEnemies[i]
            if os.clock() - entry.diedAt >= RESPAWN_TIME then
                respawnEnemy(entry.enemy)
                table.insert(activeEnemies, entry.enemy)
                table.remove(deadEnemies, i)
                break -- one per tick
            end
        end
    end
end)
```

## Boss Patterns

### Phase-Based Boss

```luau
type BossPhase = {
    healthThreshold: number, -- switch to this phase when HP drops below
    attackPattern: {string},
    speed: number,
    damage: number,
}

local bossPhases: {BossPhase} = {
    {healthThreshold = 1.0, attackPattern = {"slash", "slash", "slam"}, speed = 16, damage = 10},
    {healthThreshold = 0.5, attackPattern = {"slam", "spin", "slam"}, speed = 20, damage = 15},
    {healthThreshold = 0.2, attackPattern = {"enrage", "spin", "spin", "slam"}, speed = 24, damage = 20},
}

local function getCurrentPhase(healthPercent: number): BossPhase
    for i = #bossPhases, 1, -1 do
        if healthPercent <= bossPhases[i].healthThreshold then
            return bossPhases[i]
        end
    end
    return bossPhases[1]
end
```

### Attack Telegraphing

Always telegraph attacks so players can react:

```luau
local function telegraphedAttack(boss: Model, attackName: string, windupTime: number)
    -- Visual warning (red zone on ground)
    local indicator = createAttackIndicator(boss, attackName)
    indicator.Parent = workspace

    -- Windup (player can dodge)
    task.wait(windupTime)

    -- Execute attack
    local hitbox = createHitbox(boss, attackName)
    local hits = getPlayersInHitbox(hitbox)
    for _, player in hits do
        dealDamage(player, boss.Config.Damage)
    end

    -- Cleanup
    indicator:Destroy()
    hitbox:Destroy()
end
```

## Common Mistakes

- **Client-side NPC logic**: All NPC behavior must run on the server. Client only handles visuals/animations.
- **No pathfinding timeout**: `ComputeAsync` can hang. Always wrap with a timeout or check Status.
- **Forgetting to anchor spawned NPCs**: Set `HumanoidRootPart.Anchored = false` after positioning (it defaults to false, but if you clone from a template that's anchored...).
- **Not cleaning up dead NPCs**: Destroy models after death animation. Don't let corpses accumulate.
- **Tight detection loops**: Don't check every NPC against every player every frame. Use spatial partitioning or throttle to 5-10 checks/sec.
- **Ignoring network ownership**: For physics-based NPCs, set `SetNetworkOwner(nil)` to keep them server-authoritative. Otherwise the nearest player "owns" the physics and exploiters can fling them.

```luau
-- Keep NPC physics server-authoritative
for _, part in npcModel:GetDescendants() do
    if part:IsA("BasePart") then
        part:SetNetworkOwner(nil)
    end
end
```
