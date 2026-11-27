# Roblox NPC & AI: Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

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

    -- Mark the traversal stale. Let the caller retry with a bounded policy.
    local blocked = false
    local blockedConnection = path.Blocked:Connect(function()
        blocked = true
    end)

    local completed = true
    for _, waypoint in waypoints do
        if blocked then
            completed = false
            break
        end

        if waypoint.Action == Enum.PathWaypointAction.Jump then
            humanoid.Jump = true
        elseif waypoint.Action == Enum.PathWaypointAction.Custom then
            -- Custom action (e.g. open door, use ladder)
            -- Handle based on waypoint.Label
        end

        humanoid:MoveTo(waypoint.Position)
        local reached = humanoid.MoveToFinished:Wait()

        if blocked or not reached then
            completed = false
            break
        end
    end

    blockedConnection:Disconnect()
    return completed
end
```

If this returns `false`, the caller should recompute from the NPC's current position with a bounded retry or cancellation policy. Do not recursively call `followPath` from `Path.Blocked`; a persistently blocked route can otherwise create overlapping traversals and unbounded work.

### Pathfinding Modifiers

Control how the pathfinder treats specific regions:

**Material costs**: make certain terrain materials expensive:
```luau
local path = PathfindingService:CreatePath({
    Costs = {
        Water = 20,         -- 20x more expensive than default
        CrackedLava = 100,  -- nearly impassable
        Slate = 20,         -- avoid slate areas
    },
})
```

**Region modifiers**: mark arbitrary zones as costly or impassable:
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

**PassThrough**: pathfind through solid obstacles (e.g. doors):
1. Create an Anchored, CanCollide=false Part around the door
2. Add a `PathfindingModifier` with `PassThrough = true`
3. The path will route through the door as if it's open

**PathfindingLink**: connect disconnected navmesh areas:
Use `PathfindingLink` to tell the pathfinder about custom traversal (teleporters, ziplines, boats). Set a Label and handle it in the waypoint loop via `waypoint.Action == Enum.PathWaypointAction.Custom`.

### Navigation Mesh

The navigation mesh is auto-generated from geometry. Debug it in Studio:
- View → Visualization Options → Navigation Mesh (shows walkable areas)
- View → Visualization Options → Pathfinding Modifiers (shows labels)

Colored areas = walkable. Small arrows = jump connections. Uncolored = impassable.

### Custom navmesh alternatives to PathfindingService

PathfindingService auto-generates its navmesh from geometry server-side. It is robust but black-box: no control over walkable geometry or generation. For full control, community modules port real navmesh generators to Luau (see the Navcast thread as a lead, https://devforum.roblox.com/t/navcast-an-attempt-to-port-recast-to-luau/4743538). Such ports are not game-ready: voxelization is far too slow for live or changing maps, so tile generation with yields between chunks is required. Use them as a reference point when PathfindingService's constraints don't fit your geometry or agent needs, not as a drop-in replacement.

<!-- temporal: 2026-07 -->

## Pathfinding performance and improved search

Roblox has shipped an improved pathfinding search algorithm behind the Studio-only, non-scriptable `Workspace.PathfindingUseImprovedSearch` setting. Test it against representative maps and NPC agent parameters before enabling it in a live place. A path that succeeds is not automatically a cheap path.

Keep path requests bounded and event-driven:

- do not compute every NPC path every frame;
- stagger requests across frames and cache a path until the target or world meaningfully changes;
- avoid unnecessarily long searches and choose a destination budget appropriate for the map;
- avoid continuously moving `CanCollide` geometry when it is not needed, because navigation-mesh regeneration can become the bottleneck;
- capture a MicroProfiler trace when pathfinding slows down instead of assuming the state machine is at fault.

If `Path.Blocked` fires, recompute from the NPC's current position with a bounded retry policy. Do not allow a blocked-path callback to recursively create unlimited overlapping `ComputeAsync` calls.

## Pathfinding under streaming and debugging

- **Client pathfinding sees only streamed-in geometry**, so it can route through obstacles that exist on the server; streaming can also block or unblock a path while a character walks it. Handle blocked paths and recompute. A client script that targets a world object should target a part inside a `Persistent` model and wait for `Workspace.PersistentLoaded`. Server pathfinding sees the whole world.
- **Visualize** the navigation mesh, pathfinding modifiers and pathfinding links from Studio's Visualization Options widget (upper-right of the viewport).

## Architecture for many bots: sense, think, act

A structure that scales and tests well (field-tested in shooter bots):

- **Sense:** each bot updates on its own phase so raycasts spread across frames; it writes what it sees, hears (gunshots and sprinting within a radius) and who hurt it into a plain table.
- **Think:** a pure `Brain(mind, senses) -> intent` function with no Roblox calls. Being pure, it can be unit tested in Lune and run in a headless seeded simulation.
- **Act:** a motor that moves the body every frame with the same movement numbers players have, so bots never move in ways players can't.

```luau
-- Illustrative: the pure Think step. No Instances, no services.
export type Senses = { targetVisible: boolean, targetDistance: number, hurtBy: number?, now: number }
export type Mind = { state: string, reactAt: number, reactionDelay: number }
export type Intent = { move: string, fire: boolean }

local function think(mind: Mind, senses: Senses): Intent
    if senses.targetVisible then
        if mind.state ~= "engage" then
            mind.state = "engage"
            mind.reactAt = senses.now + mind.reactionDelay -- human-like reaction delay
        end
        return { move = "strafe", fire = senses.now >= mind.reactAt and senses.targetDistance < 120 }
    end
    mind.state = if senses.hurtBy then "search" else "patrol"
    return { move = mind.state, fire = false }
end

return think
```

**Think-rate tiers.** Distance-tiered thinking is a good start: decisions every 0.1 s within about 90 studs, every 1 s past about 220 studs, with a reaction delay of 0.15-0.28 s; then profile. One measured pen of 10 active ragdoll NPCs plus corpses owned by one client cost 0.25 ms of physics and 0.6 ms of heartbeat per frame.

**Virtual server NPCs, client rigs.** For many living NPCs, keep them virtual on the server (position, state and decisions as data, replicated at about 20 Hz) and draw them on each client as anchored rigs moved with `workspace:BulkMoveTo` and default animations; 40 NPCs cost about 0.2 ms of client script per frame in one project. Switch to shared server physics only for dead bodies and severed pieces, keep damage server-authoritative, keep gore client-only, and use collision groups so players walk through piles.

## Cover-point graphs instead of free pathfinding

For shooter bots, hand-placed tagged markers can beat `PathfindingService`:

1. Place cover and waypoint markers (a part or attachment; front = `LookVector`; attributes for full or half height, open peek sides, and a role such as camp or snipe).
2. Auto-link any two within about 48 studs that a straight walk connects: floor all the way, no step over about 3.5 studs, only jumpable obstacles with head room.
3. Run A* on that graph. Skip and warn on bad markers, draw points and links in a debug view, and treat an unlinked point as unreachable.
4. Claim cover points so two bots never share one, and drop a cover the bot was seen in for a few seconds so it doesn't oscillate between two failing covers.

## Fair, tunable bot difficulty

- **Tune reaction, not walk speed.** Reaction delay, attack cooldown and aim error read as a human; a visibly slower walk reads as "that's a bot" (in one game, 8.5 studs/s was obvious and 11 felt right).
- **Skill as a few numbers per rank** (reaction delay, aim-error cone, movement amount, first-shot accuracy) applied to one shared brain. Aim trails a moving target by part of the reaction, flicks past a new target and settles, then tightens while tracking; cap turn rate so slow turners can be circled; fire in bursts with rests; a sniper shows its aim line during a windup whose last fraction locks, so changing direction dodges it. Assert in tests that every skill number improves monotonically with rank.
- **Mixed lobbies:** filler bots target other bots before real players, so humans mostly face humans. Every new gate on bot behavior can switch something else off; list what a new flag disables before shipping it.
- **Measure with a headless, seeded simulation** of the pure bot code on the real map against scripted player profiles. Print K/D, kills and deaths per minute, median time to kill and to die, and stuck bots (wanted to move 5 of 10 s but moved under 3 studs, with seed and position). Compare versions over many seeds (36+ for a free-for-all, 72 for a duel). In free-for-all, K/D barely follows skill because bots kill each other, so judge by deaths per minute and time to death too.

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
    fovDegrees: number,
    hearingEnabled: boolean,
    hearingRange: number,
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
local function hasLineOfSight(from: Vector3, to: Vector3, ignore: {Instance}, target: Instance?): boolean
    local direction = to - from
    local params = RaycastParams.new()
    params.FilterDescendantsInstances = ignore
    params.FilterType = Enum.RaycastFilterType.Exclude

    local result = workspace:Raycast(from, direction, params)
    -- Nothing between the endpoints: sight is clear.
    if result == nil then return true end
    -- The segment can clip the target's own queryable parts (aiming at the
    -- head grazes a hat or hand). A hit inside the target means the ray
    -- REACHED it: that is sight, not an obstruction. Only a hit on some
    -- other instance (a wall) blocks.
    if target and result.Instance:IsDescendantOf(target) then
        return true
    end
    return false
end

-- Usage: check if NPC can see player. Exclude the NPC's own character but
-- NOT the target's: pass the target as the last argument instead.
local canSee = hasLineOfSight(
    npc.rootPart.Position + Vector3.new(0, 2, 0), -- eye height
    targetRoot.Position + Vector3.new(0, 2, 0),   -- target eye height
    {npc.rootPart.Parent},                        -- ignore the NPC itself
    targetRoot.Parent                             -- hits within the target are visibility
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
    if not isInFOV(npc.rootPart.CFrame, root.Position, npc.config.fovDegrees) then
        if not npc.config.hearingEnabled or dist > npc.config.hearingRange then
            return false
        end
    end

    -- 3. Line of sight (expensive, do last); pass the target so hits on
    -- the player's own parts read as visibility, not obstruction
    return hasLineOfSight(
        npc.rootPart.Position + Vector3.new(0, 2, 0),
        root.Position + Vector3.new(0, 2, 0),
        {npc.rootPart.Parent},
        root.Parent
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

## Network Ownership and Server Authority

For classic replication, decide deliberately whether an unanchored NPC assembly should be server-owned. Server ownership can prevent client-owned physics from producing unexpected motion, but it is not a complete anti-exploit boundary and it costs server simulation work.

```luau
local function setServerOwned(model: Model)
    for _, part in model:GetDescendants() do
        if part:IsA("BasePart") then
            part:SetNetworkOwner(nil)
        end
    end
end

setServerOwned(enemy)
```

In a Server Authority project, configure `Workspace.AuthorityMode = Server` and its required replication, fixed-simulation, streaming, and input settings. Server-owned gameplay physics can remain responsive through client prediction, so `SetNetworkOwner(nil)` is not the authority model and the classic secure-but-laggy trade-off does not apply in the same way.

Measure CPU, pathfinding, and replication cost at the intended NPC count. If visual motion becomes too coarse in a classic project, replicate authoritative state and interpolate on the client instead of handing gameplay authority to the client.

## Update Loop

Don't run AI logic every frame. Use a configured interval based on the behavior's responsiveness and profile it under the intended NPC count:

```luau
local AI_TICK_RATE = 1/10 -- example only; tune and measure for the project
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

For large NPC counts, keep a rotating work cursor or queue so not all NPCs think on the same frame. Make the per-tick budget a measured project setting.

## Common Mistakes

- **Client-side NPC logic**: ALL NPC behavior must run on the server. Client only handles animations/visuals.
- **No path blocked handling**: Paths go stale when the world changes. Always connect `path.Blocked` and recompute with bounded retries.
- **ComputeAsync with no fallback**: If path computation fails (`Status ~= Success`), don't freeze. Fall back to direct movement or idle.
- **Tight detection loops**: Don't check every NPC against every player every frame. Distance checks are O(n*m); throttle and batch based on profiler evidence.
- **Treating network ownership as security**: In classic projects, choose ownership deliberately. In Server Authority projects, configure the authority model; `SetNetworkOwner(nil)` alone is not the security boundary.
- **Not cleaning up dead NPCs**: Destroy models after death animation. Corpses accumulate and kill performance.
- **MoveTo timeout**: `Humanoid:MoveTo()` has an 8-second timeout. If the NPC gets stuck, `MoveToFinished` fires with `reached = false`. Handle it.
- **Pathfinding on the client**: PathfindingService works on both client and server, but NPC movement must be server-authoritative. Compute paths on the server.
- **No stagger for large NPC counts**: A large batch of path requests on one frame can spike the server. Stagger updates and measure the actual budget.

## Community ecosystem (leads, not sources)

- [SimplePath](https://devforum.roblox.com/t/simplepath-pathfinding-module/1196762) (894 likes): the PathfindingService wrapper standard; [How 2 Make A* Pathfinding](https://devforum.roblox.com/t/how-2-make-a-pathfinding/2714504) for custom grids.
- [BehaviorTrees3 + visual editor](https://devforum.roblox.com/t/behaviortrees3-btrees-visual-editor-v30/836158): the BT reference implementation.
- [Simulating thousands of moving NPCs performantly](https://devforum.roblox.com/t/simulating-thousands-of-moving-npcs-with-humanoidsphysics-performantly/4603494) (2026): current humanoid-scale density canon.
## Avatar appearance: HumanoidDescription, BodyColors, Shirt, Pants

### HumanoidDescription: the canonical runtime appearance API

- Change an NPC's appearance at runtime with `Humanoid:ApplyDescription(description)`; read current appearance with `Humanoid:GetDescription()`. ApplyDescription batch-applies every field in one step; prefer it over piecemeal property edits.
- Clone-and-modify: never mutate a shared or template description in place. Clone it, edit the clone, apply. A shared instance mutates every NPC referencing it.
- Key fields: `Shirt` and `Pants` (classic clothing asset IDs), `Face`, body-part mesh IDs (`Head`, `Torso`, `LeftArm`, `RightArm`, `LeftLeg`, `RightLeg`), per-part `*Color` (Color3), and R15 scale fields: `HeadScale`, `HeightScale`, `WidthScale`, `DepthScale`, `BodyTypeScale`, `ProportionScale`.
- Accessories: per-bone string fields (`HatAccessory`, `HairAccessory`, `FaceAccessory`, `NeckAccessory`, `FrontAccessory`, `BackAccessory`, `WaistAccessory`, `ShouldersAccessory`) plus the Accessories table managed by `SetAccessories(accessories, includeRigidAccessories)` / `GetAccessories(includeRigidAccessories)`. Attach accessory instances with `Humanoid:AddAccessory(accessory)`.
- R6 vs R15: scale fields and body-part mesh IDs apply to R15 only; they are ignored on R6. Classic clothing (`Shirt`/`Pants` IDs) works on both. Batch-apply with ApplyDescription so the rig rebuilds once.
- Build descriptions from real avatars: `Players:GetHumanoidDescriptionFromUserIdAsync(userId)` and `Players:GetHumanoidDescriptionFromOutfitIdAsync(outfitId)`.

### BodyColors (legacy)

- Legacy instance parented to the character with one BrickColor per body part: `HeadColor`, `TorsoColor`, `LeftArmColor`, `RightArmColor`, `LeftLegColor`, `RightLegColor`.
- Superseded by `HumanoidDescription`'s `*Color` Color3 fields for most uses. Keep for R6-only or legacy rigs.

### Shirt / Pants

- Parent a `Shirt` or `Pants` instance to the character model; set `ShirtTemplate` / `PantsTemplate` to classic clothing content IDs (ContentId).
- Replace safely: `character:FindFirstChildOfClass("Shirt")`, create and parent a new instance if missing, then set the template.

```luau
-- Server: clone a template description, tweak, apply
local template = ReplicatedStorage:FindFirstChild("NPCAppearance", true):FindFirstChildOfClass("HumanoidDescription")
local desc = template:Clone() -- never mutate the shared template
desc.HeightScale = 1.1
desc.HeadScale = 1.15
desc.Shirt = 5832882895 -- classic shirt asset ID
npcHumanoid:ApplyDescription(desc)
```

## Legacy tools: HopperBin (deprecated)

`HopperBin` is the pre-2013 ancestor of `Tool`: drop it in `StarterPack` and the player auto-equips it. It is deprecated; do not use it for new work. Migrate to `Tool` (parent to `Backpack` / equip via `Humanoid:EquipTool`) or to a prompt-based interaction (`ProximityPrompt`) for non-held abilities. Do not wire `HopperBin`-era events (`Bin.Selected`/`Bin.Deselected` are the old API) into new systems; only tolerate HopperBins when preserving a legacy place file.

## Group decisions and navigation progress

Observe the whole bot group after a shared event such as a dropped item or threat change. Independent greedy choices can converge on the same objective or escape point. Where the design calls for it, allocate a claimant for scarce objectives and vary escape preferences; test the group rather than only one successful path.

Give fixed objectives a bounded no-progress policy and a temporary rejection/retry rule. Define a different replan/progress policy for moving chase targets, whose movement can invalidate a path or erase apparent distance gains. Test vertical separation, an inaccessible fixed objective, a fleeing target, and recovery after the world changes. Measure actual movement and progress; a chase state label is not evidence that navigation works.
