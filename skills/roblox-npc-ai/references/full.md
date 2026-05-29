# Roblox NPC & AI — Full Reference

> Moved from SKILL.md. Original: 13,451 chars, 7 sections.

## PathfindingService

### CreatePath Parameters

```luau
local PathfindingService = game:GetService("PathfindingService")

local path = PathfindingService:CreatePath({
    AgentRadius = 2,       -- half-width of the NPC (default 2)
    AgentHeight = 5,       -- height of the NPC (default 5)
    AgentCanJump = true,   -- can the agent jump over gaps?
    AgentCanClimb = true,  -- can the agent climb TrussParts?
    WaypointSpacing = 4,   -- studs between waypoints (default 4)
    Costs = {              -- material/region traversal costs
        Water = 20,        -- avoid water (20x more expensive)
        CrackedLava = math.huge, -- never traverse lava
    },
})
```

All materials have a default cost of 1. Set `math.huge` to make a material completely non-traversable.

### Computing and Following a Path

From the official Roblox pathfinding docs:

```luau
local PathfindingService = game:GetService("PathfindingService")

local path = PathfindingService:CreatePath({
    AgentCanClimb = true,
    Costs = { Water = 20 },
})

local character = script.Parent
local humanoid = character:WaitForChild("Humanoid")

local function followPath(destination: Vector3)
    path:ComputeAsync(humanoid.RootPart.Position, destination)

    if path.Status ~= Enum.PathStatus.Success then
        warn("Path failed:", path.Status)
        return false
    end

    local waypoints = path:GetWaypoints()

    -- Handle path blocked mid-traversal
    local blockedConnection
    blockedConnection = path.Blocked:Connect(function(blockedWaypointIndex)
        blockedConnection:Disconnect()
        -- Recompute from current position
        followPath(destination)
    end)

    for i, waypoint in waypoints do
        if waypoint.Action == Enum.PathWaypointAction.Jump then
            humanoid.Jump = true
        elseif waypoint.Action == Enum.PathWaypointAction.Custom then
            -- Custom action (e.g. open door, use ladder)
            -- Handle based on waypoint.Label
        end

        humanoid:MoveTo(waypoint.Position)
        local reached = humanoid.MoveToFinished:Wait()

        if not reached then
            blockedConnection:Disconnect()
            return false
        end
    end

    blockedConnection:Disconnect()
    return true
end
```

### Pathfinding Modifiers

Control how the pathfinder treats specific regions:

**Material costs** — make certain terrain materials expensive:
```luau
local path = PathfindingService:CreatePath({
    Costs = {
        Water = 20,         -- 20x more expensive than default
        CrackedLava = 100,  -- nearly impassable
        Slate = 20,         -- avoid slate areas
    },
})
```

**Region modifiers** — mark arbitrary zones as costly or impassable:
1. Create an Anchored, CanCollide=false Part around the region
2. Add a `PathfindingModifier` child with a `Label` (e.g. "DangerZone")
3. Reference the label in Costs:

```luau
local path = PathfindingService:CreatePath({
    Costs = {
        DangerZone = math.huge, -- completely avoid this region
    },
})
```

**PassThrough** — pathfind through solid obstacles (e.g. doors):
1. Create an Anchored, CanCollide=false Part around the door
2. Add a `PathfindingModifier` with `PassThrough = true`
3. The path will route through the door as if it's open

**PathfindingLink** — connect disconnected navmesh areas:
Use `PathfindingLink` to tell the pathfinder about custom traversal (teleporters, ziplines, boats). Set a Label and handle it in the waypoint loop via `waypoint.Action == Enum.PathWaypointAction.Custom`.

### Navigation Mesh

The navigation mesh is auto-generated from geometry. Debug it in Studio:
- View → Visualization Options → Navigation Mesh (shows walkable areas)
- View → Visualization Options → Pathfinding Modifiers (shows labels)

Colored areas = walkable. Small arrows = jump connections. Uncolored = impassable.

## State Machine Pattern

The most reliable NPC AI architecture. Each NPC has a current state and transitions based on conditions.

```luau
--!strict
type State = "idle" | "patrol" | "chase" | "attack" | "flee" | "dead"

type NPCConfig = {
    detectionRange: number,
    attackRange: number,
    fleeHealthPercent: number,
    patrolPoints: {Vector3},
    attackCooldown: number,
    walkSpeed: number,
    runSpeed: number,
}

type NPCState = {
    current: State,
    target: Player?,
    patrolIndex: number,
    lastAttackTime: number,
    humanoid: Humanoid,
    rootPart: BasePart,
    config: NPCConfig,
}

local function transition(npc: NPCState, newState: State)
    -- Exit current state
    if npc.current == "chase" or npc.current == "patrol" then
        npc.humanoid.WalkSpeed = npc.config.walkSpeed
    end

    -- Enter new state
    npc.current = newState

    if newState == "chase" then
        npc.humanoid.WalkSpeed = npc.config.runSpeed
    elseif newState == "idle" then
        npc.target = nil
    end
end
```

### State Transitions

```
idle → patrol (has patrol points)
idle → chase (player detected)
patrol → chase (player detected)
chase → attack (in attack range)
chase → idle (target lost/died)
chase → flee (health low)
attack → chase (target moved out of range)
attack → flee (health low)
flee → idle (safe distance reached)
any → dead (health <= 0)
```

## Detection

### Distance Check (cheapest, do first)

```luau
local Players = game:GetService("Players")

local function findNearestPlayer(position: Vector3, range: number): Player?
    local nearest: Player? = nil
    local nearestDist = range

    for _, player in Players:GetPlayers() do
        local char = player.Character
        if not char then continue end
        local root = char:FindFirstChild("HumanoidRootPart")
        if not root then continue end
        local humanoid = char:FindFirstChildOfClass("Humanoid")
        if not humanoid or humanoid.Health <= 0 then continue end

        local dist = (root.Position - position).Magnitude
        if dist < nearestDist then
            nearest = player
            nearestDist = dist
        end
    end

    return nearest
end
```

### Line of Sight (raycast)

Only check LOS after distance check passes (raycasts are expensive):

```luau
local function hasLineOfSight(from: Vector3, to: Vector3, ignore: {Instance}): boolean
    local direction = to - from
    local params = RaycastParams.new()
    params.FilterDescendantsInstances = ignore
    params.FilterType = Enum.RaycastFilterType.Exclude

    local result = workspace:Raycast(from, direction, params)
    -- nil result means nothing blocked the ray
    return result == nil
end

-- Usage: check if NPC can see player
local canSee = hasLineOfSight(
    npc.rootPart.Position + Vector3.new(0, 2, 0), -- eye height
    targetRoot.Position + Vector3.new(0, 2, 0),   -- target eye height
    {npc.rootPart.Parent}                          -- ignore NPC's own model
)
```

### Field of View (cone check)

```luau
local function isInFOV(npcCFrame: CFrame, targetPos: Vector3, fovDegrees: number): boolean
    local toTarget = (targetPos - npcCFrame.Position).Unit
    local forward = npcCFrame.LookVector
    local dot = forward:Dot(toTarget)
    local angle = math.acos(math.clamp(dot, -1, 1))
    return angle <= math.rad(fovDegrees / 2)
end
```

### Combined Detection (distance → FOV → LOS)

```luau
local function canDetectPlayer(npc: NPCState, player: Player): boolean
    local char = player.Character
    if not char then return false end
    local root = char:FindFirstChild("HumanoidRootPart")
    if not root then return false end

    -- 1. Distance (cheapest check first)
    local dist = (root.Position - npc.rootPart.Position).Magnitude
    if dist > npc.config.detectionRange then return false end

    -- 2. Field of view (medium cost)
    if not isInFOV(npc.rootPart.CFrame, root.Position, 120) then
        -- Can still detect if very close (hearing range)
        if dist > npc.config.detectionRange * 0.3 then return false end
    end

    -- 3. Line of sight (expensive, do last)
    return hasLineOfSight(
        npc.rootPart.Position + Vector3.new(0, 2, 0),
        root.Position + Vector3.new(0, 2, 0),
        {npc.rootPart.Parent}
    )
end
```

## Spawn Systems

### Basic Spawner with Cap

```luau
local MAX_ENEMIES = 10
local SPAWN_INTERVAL = 5
local activeEnemies: {Model} = {}

local function spawnEnemy(spawnPoint: BasePart): Model?
    if #activeEnemies >= MAX_ENEMIES then return nil end

    local enemy = ServerStorage.EnemyTemplate:Clone()
    enemy:PivotTo(spawnPoint.CFrame + Vector3.new(0, 3, 0))
    enemy.Parent = workspace.Enemies
    table.insert(activeEnemies, enemy)

    -- Track death
    local humanoid = enemy:FindFirstChildOfClass("Humanoid")
    if humanoid then
        humanoid.Died:Once(function()
            local idx = table.find(activeEnemies, enemy)
            if idx then table.remove(activeEnemies, idx) end
            task.delay(3, function() enemy:Destroy() end) -- cleanup after death anim
        end)
    end

    return enemy
end

-- Spawn loop
task.spawn(function()
    while true do
        task.wait(SPAWN_INTERVAL)
        local spawnPoints = workspace.SpawnPoints:GetChildren()
        local point = spawnPoints[math.random(1, #spawnPoints)]
        spawnEnemy(point)
    end
end)
```

### Wave System

```luau
type WaveConfig = {
    enemies: {{template: string, count: number}},
    spawnDelay: number, -- seconds between individual spawns
    waveDelay: number,  -- seconds between waves
}

local waves: {WaveConfig} = {
    {enemies = {{template = "Zombie", count = 5}}, spawnDelay = 1, waveDelay = 10},
    {enemies = {{template = "Zombie", count = 8}, {template = "FastZombie", count = 3}}, spawnDelay = 0.8, waveDelay = 15},
}

local function spawnWave(wave: WaveConfig, spawnPoints: {BasePart})
    for _, group in wave.enemies do
        for i = 1, group.count do
            local point = spawnPoints[math.random(1, #spawnPoints)]
            local template = ServerStorage.Enemies:FindFirstChild(group.template)
            if template then
                local enemy = template:Clone()
                enemy:PivotTo(point.CFrame + Vector3.new(0, 3, 0))
                enemy.Parent = workspace.Enemies
            end
            task.wait(wave.spawnDelay)
        end
    end
end
```

## Network Ownership

**Critical**: By default, the nearest player "owns" the physics of unanchored parts. This means exploiters can fling your NPCs.

```luau
-- Keep NPC physics server-authoritative
local function setServerOwned(model: Model)
    for _, part in model:GetDescendants() do
        if part:IsA("BasePart") then
            part:SetNetworkOwner(nil) -- server owns physics
        end
    end
end

-- Call after spawning
setServerOwned(enemy)
```

**Trade-off**: Server ownership means NPC movement is limited to server tick rate (30Hz). For smooth visual movement, replicate position to clients and interpolate.

## Update Loop

Don't run AI logic every frame. Throttle to 5-10 updates per second:

```luau
local AI_TICK_RATE = 1/10 -- 10 updates per second
local accumulated = 0

RunService.Heartbeat:Connect(function(dt)
    accumulated += dt
    if accumulated < AI_TICK_RATE then return end
    accumulated -= AI_TICK_RATE

    for _, npc in activeNPCs do
        updateNPC(npc)
    end
end)
```

For large NPC counts, stagger updates so not all NPCs think on the same frame:

```luau
local npcIndex = 0
RunService.Heartbeat:Connect(function(dt)
    -- Process 5 NPCs per frame instead of all at once
    for i = 1, math.min(5, #activeNPCs) do
        npcIndex = (npcIndex % #activeNPCs) + 1
        updateNPC(activeNPCs[npcIndex])
    end
end)
```

## Common Mistakes

- **Client-side NPC logic**: ALL NPC behavior must run on the server. Client only handles animations/visuals.
- **No path blocked handling**: Paths go stale when the world changes. Always connect `path.Blocked` and recompute.
- **ComputeAsync with no fallback**: If path computation fails (Status ~= Success), don't freeze. Fall back to direct movement or idle.
- **Tight detection loops**: Don't check every NPC against every player every frame. Distance check is O(n*m). Throttle to 5-10/sec.
- **Forgetting SetNetworkOwner(nil)**: Without this, the nearest player owns NPC physics. Exploiters fling them.
- **Not cleaning up dead NPCs**: Destroy models after death animation. Corpses accumulate and kill performance.
- **MoveTo timeout**: `Humanoid:MoveTo()` has an 8-second timeout. If the NPC gets stuck, `MoveToFinished` fires with `reached = false`. Handle it.
- **Pathfinding on the client**: PathfindingService works on both client and server, but NPC movement must be server-authoritative. Compute paths on the server.
- **No stagger for large NPC counts**: 50 NPCs all computing paths on the same frame = server lag spike. Stagger updates.
