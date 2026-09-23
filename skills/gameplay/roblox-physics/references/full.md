# Roblox Physics & Constraints: Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

## Constraint Types

### Mechanical Constraints

| Constraint | What it does | Use for |
|-----------|-------------|---------|
| `HingeConstraint` | Rotation around one axis | Doors, wheels, pendulums, flaps |
| `PrismaticConstraint` | Slide along one axis | Elevators, pistons, sliding doors |
| `CylindricalConstraint` | Rotate + slide on one axis | Telescoping arms, drill bits |
| `BallSocketConstraint` | Free rotation (3 DOF) | Ragdoll joints, chains, wrecking balls |
| `UniversalConstraint` | 2-axis rotation (no twist) | Steering columns, gimbal joints |
| `WeldConstraint` | Rigid connection | Attach parts permanently |
| `RigidConstraint` | Rigid (like Weld but with offset) | Precise attachment with maintained offset |

### Motion Constraints

| Constraint | What it does | Use for |
|-----------|-------------|---------|
| `AlignPosition` | Move toward target position | Floating platforms, magnetic attraction |
| `AlignOrientation` | Rotate toward target orientation | Auto-leveling, look-at behavior |
| `LinearVelocity` | Constant velocity in direction | Conveyor belts, moving platforms |
| `AngularVelocity` | Constant rotation speed | Spinning obstacles, fans |
| `VectorForce` | Apply constant force | Gravity modification, thrust |
| `LineForce` | Constant force along the Attachment0→Attachment1 axis | Tractor beams, magnetics, tethers |
| `Torque` | Apply constant torque | Spinning objects |

### Spring/Rope

| Constraint | What it does | Use for |
|-----------|-------------|---------|
| `SpringConstraint` | Bouncy connection | Suspension, trampolines, bouncy bridges |
| `RopeConstraint` | Max distance (slack allowed) | Grappling hooks, hanging objects |
| `RodConstraint` | Fixed distance (rigid) | Rigid linkages, pendulum arms |

## LineForce

`LineForce` applies a constant force along the axis between `Attachment0` and `Attachment1` — it pulls (or pushes) one assembly toward the other, and the direction tracks the parts as they move. Compare `VectorForce`: a fixed `Vector3` (world or attachment-relative) whose direction never changes. Use LineForce when the pull must follow a target part; use VectorForce for constant world-direction thrust.

```luau
local lf = Instance.new("LineForce")
lf.Attachment0 = anchorAtt     -- on the anchor part
lf.Attachment1 = pulledAtt     -- pulled toward Attachment0 when Magnitude > 0
lf.Magnitude = 5000            -- force along the attachment axis
lf.MaxForce = 10000            -- cap the applied force
lf.ReactionForceEnabled = true -- equal/opposite force on the anchor part
lf.ApplyAtCenterOfMass = true  -- apply at CoM instead of Attachment1
lf.InverseSquareLaw = true     -- falloff with distance (gravity/magnet feel)
lf.Parent = anchorPart
```

- `Magnitude`: signed force; sign sets pull vs push.
- `MaxForce`: upper clamp (no `MinForce` property — limit in scripts if needed).
- `InverseSquareLaw`: force scales as 1/distance² between the attachments.

## Attachment Pattern

All constraints connect via Attachments, not Parts directly:

```luau
local function connectHinge(part0: BasePart, part1: BasePart, pivotOffset: Vector3)
    local att0 = Instance.new("Attachment")
    att0.Position = pivotOffset
    att0.Parent = part0

    local att1 = Instance.new("Attachment")
    att1.Position = Vector3.new(0, 0, 0) -- at part1's origin
    att1.Parent = part1

    local hinge = Instance.new("HingeConstraint")
    hinge.Attachment0 = att0
    hinge.Attachment1 = att1
    hinge.ActuatorType = Enum.ActuatorType.Motor -- or None, Servo
    hinge.MotorMaxTorque = 1000
    hinge.AngularVelocity = 5 -- rad/s
    hinge.Parent = part0

    return hinge
end
```

## Vehicles

### Basic Car (4 wheels + body)

```luau
local function createWheel(chassis: BasePart, offset: Vector3, steer: boolean): HingeConstraint
    local wheel = Instance.new("Part")
    wheel.Shape = Enum.PartType.Cylinder
    wheel.Size = Vector3.new(1, 3, 3) -- width, diameter, diameter
    wheel.CFrame = chassis.CFrame * CFrame.new(offset) * CFrame.Angles(0, 0, math.pi/2)
    wheel.CustomPhysicalProperties = PhysicalProperties.new(1, 0.5, 0, 1, 1)
    wheel.Parent = chassis.Parent

    -- Suspension (spring between chassis and wheel)
    local springAtt0 = Instance.new("Attachment")
    springAtt0.Position = offset + Vector3.new(0, 1, 0)
    springAtt0.Parent = chassis

    local springAtt1 = Instance.new("Attachment")
    springAtt1.Parent = wheel

    local spring = Instance.new("SpringConstraint")
    spring.Attachment0 = springAtt0
    spring.Attachment1 = springAtt1
    spring.FreeLength = 2
    spring.Stiffness = 5000
    spring.Damping = 200
    spring.Parent = chassis

    -- Axle (hinge for rotation)
    local axleAtt0 = Instance.new("Attachment")
    axleAtt0.Position = offset
    axleAtt0.Parent = chassis

    local axleAtt1 = Instance.new("Attachment")
    axleAtt1.Parent = wheel

    local hinge = Instance.new("HingeConstraint")
    hinge.Attachment0 = axleAtt0
    hinge.Attachment1 = axleAtt1
    hinge.ActuatorType = Enum.ActuatorType.Motor
    hinge.MotorMaxTorque = 500
    hinge.AngularVelocity = 0 -- controlled by input
    hinge.Parent = chassis

    return hinge
end
```

### Vehicle Input (server-authoritative)

The `RemoteEvent` pattern below is for classic projects and discrete or low-frequency control. In a Server Authority project, continuous throttle and steering belong in the Input Action System, with input state available to the synchronized simulation through `RunService:BindToSimulation()` (requires `Workspace.UseFixedSimulation` enabled in Studio). RemoteEvents are still appropriate for discrete requests, not as the continuous prediction path.

```luau
-- Server: receive input, apply to constraints
local DriveRemote = Instance.new("RemoteEvent")
DriveRemote.Name = "Drive"
DriveRemote.Parent = ReplicatedStorage

DriveRemote.OnServerEvent:Connect(function(player, throttle: number, steer: number)
    -- Validate
    throttle = math.clamp(throttle, -1, 1)
    steer = math.clamp(steer, -1, 1)

    local vehicle = getPlayerVehicle(player)
    if not vehicle then return end

    -- Apply throttle to rear wheels
    for _, hinge in vehicle.rearWheels do
        hinge.AngularVelocity = throttle * MAX_SPEED
    end

    -- Apply steering to front wheels
    for _, servo in vehicle.frontSteering do
        servo.TargetAngle = steer * MAX_STEER_ANGLE
    end
end)
```

## Ragdoll

### Activate Ragdoll (replace Motor6Ds with BallSockets)

Enable creates attachments, sockets, and disables motors; disable must undo
exactly that set. Track ownership: which instances were created and which
motors were disabled, so recovery never re-enables a motor that was already
disabled before ragdolling, never destroys an unrelated socket, and repeated
or interleaved calls stay idempotent.

```luau
local ragdollState: { [Model]: { created: {Instance}, disabledMotors: { {motor: Motor6D, wasEnabled: boolean} } } } = {}

local function enableRagdoll(character: Model)
    if ragdollState[character] then return end -- already ragdolled

    local humanoid = character:FindFirstChildOfClass("Humanoid")
    if not humanoid then return end
    local record = { created = {}, disabledMotors = {} }
    ragdollState[character] = record

    humanoid:ChangeState(Enum.HumanoidStateType.Physics)

    for _, motor in character:GetDescendants() do
        if motor:IsA("Motor6D") and motor.Name ~= "Root" then -- keep Root for HRP
            local att0 = Instance.new("Attachment")
            att0.CFrame = motor.C0
            att0.Parent = motor.Part0

            local att1 = Instance.new("Attachment")
            att1.CFrame = motor.C1
            att1.Parent = motor.Part1

            local socket = Instance.new("BallSocketConstraint")
            socket.Attachment0 = att0
            socket.Attachment1 = att1
            socket.LimitsEnabled = true
            socket.UpperAngle = 45 -- prevent unnatural bending
            socket.Parent = motor.Part0

            table.insert(record.created, att0)
            table.insert(record.created, att1)
            table.insert(record.created, socket)
            table.insert(record.disabledMotors, { motor = motor, wasEnabled = motor.Enabled })
            motor.Enabled = false
        end
    end
end

local function disableRagdoll(character: Model)
    local record = ragdollState[character]
    if not record then return end -- not ragdolled by us
    ragdollState[character] = nil

    -- Destroy only instances enableRagdoll created; other sockets in the
    -- character belong to someone else and survive.
    for _, obj in record.created do
        if obj.Parent then
            obj:Destroy()
        end
    end

    -- Restore only motors this enable cycle disabled, to their prior state.
    for _, entry in record.disabledMotors do
        if entry.motor.Parent then
            entry.motor.Enabled = entry.wasEnabled
        end
    end

    local humanoid = character:FindFirstChildOfClass("Humanoid")
    if humanoid then
        humanoid:ChangeState(Enum.HumanoidStateType.GettingUp)
    end
end

-- Tolerate characters destroyed mid-ragdoll: drop the record so it cannot
-- leak. Illustrative; wire this when the character spawns. Declare the
-- local FIRST so the handler closes over a real upvalue instead of its own
-- initializer — referencing `connection` inside its own `local` declaration
-- reads a nil upvalue in the handler body.
local connection: RBXScriptConnection
connection = character.AncestryChanged:Connect(function()
    if not character.Parent then
        ragdollState[character] = nil
        connection:Disconnect()
    end
end)
```

For production use, store `ragdollState` inside your character/maid module rather than a module-level table, and wire the destruction cleanup into that maid so records cannot outlive their character.

## IKControl

`IKControl` runs procedural inverse kinematics on a Motor6D rig — no baked animation needed. Parent it under the rig's `Humanoid`; it bends the joint chain from `ChainRoot` (e.g. `LeftUpperArm`) so `EndEffector` (e.g. `LeftHand`) reaches `Target` (usually an `Attachment` or `BasePart`). Common uses: foot placement on stairs/slopes, hands gripping rails or ladders, head look-at.

```luau
local ik = Instance.new("IKControl")
ik.Type = Enum.IKControlType.Position -- see types below
ik.ChainRoot = character.LeftUpperArm
ik.EndEffector = character.LeftHand
ik.Target = railAttachment -- Attachment on the rail
ik.SmoothTime = 0.05       -- target smoothing; 0 = snap instantly
ik.Weight = 1
ik.Parent = humanoid

-- Stop the solve when the grip ends
ik.Enabled = false
```

- `Type`: `Position` (move effector to target), `Rotation` (match orientation), `Transform` (position + rotation), `LookAt` (aim the chain, e.g. head/eyes at a point).
- `SmoothTime`: seconds of smoothing toward the target; lower = snappier.
- `EndEffectorOffset` / `Offset`: CFrame adjustments to effector and target placement.
- `Pole`: optional part hinting elbow/knee bend direction.
- The chain must run through `Motor6D` joints from `ChainRoot` to `EndEffector`; inspect with `GetChainLength()` / `GetChainCount()`.

## Projectiles

### Server-Authoritative Raycast Projectile (hitscan)

```luau
local function fireProjectile(origin: Vector3, direction: Vector3, damage: number, ignore: {Instance})
    local params = RaycastParams.new()
    params.FilterDescendantsInstances = ignore
    params.FilterType = Enum.RaycastFilterType.Exclude

    local result = workspace:Raycast(origin, direction * 300, params)
    if result then
        local hit = result.Instance
        local humanoid = hit.Parent:FindFirstChildOfClass("Humanoid")
            or hit.Parent.Parent:FindFirstChildOfClass("Humanoid")
        if humanoid then
            humanoid:TakeDamage(damage)
        end
        return result.Position
    end
    return origin + direction * 300
end
```

### Physics Projectile (arcing, grenade-style)

For a Server Authority project, create and update gameplay-critical projectiles inside the synchronized simulation so the client can predict and reconcile them. Keep damage and state transitions in the simulation, not in a presentation-only `Touched` callback that can run again during resimulation. The example below is a classic illustrative projectile and needs that adaptation before use in Server Authority.

```luau
local function launchProjectile(origin: CFrame, velocity: Vector3, lifetime: number)
    local projectile = Instance.new("Part")
    projectile.Size = Vector3.new(0.5, 0.5, 0.5)
    projectile.Shape = Enum.PartType.Ball
    projectile.CFrame = origin
    projectile.Anchored = false
    projectile.CanCollide = true
    projectile.Parent = workspace

    -- Apply initial velocity
    projectile.AssemblyLinearVelocity = velocity

    -- Cleanup after lifetime
    task.delay(lifetime, function()
        if projectile.Parent then
            -- Explode or just destroy
            projectile:Destroy()
        end
    end)

    -- Detect hits
    projectile.Touched:Connect(function(hit)
        if hit.Parent:FindFirstChildOfClass("Humanoid") then
            -- Deal damage, create explosion, etc.
            projectile:Destroy()
        end
    end)

    return projectile
end
```

### Homing Projectile (velocity-aiming steering)

A common technique simulates homing missiles without Roblox physics by steering a velocity vector toward the target each frame, clamped to a max turn angle. This avoids physics-solver jitter and suits missiles, spells, and homing bullets. Keep the projectile anchored and interpolate its CFrame yourself (or drive `AssemblyLinearVelocity`); each frame rotate the current velocity direction toward the target direction, never exceeding the max turn rate per frame. Community projectile modules (e.g. HomingCast, https://devforum.roblox.com/t/homingcast-homing-projectiles/3786022) are a lead for this pattern.

```luau
-- Illustrative; tune for your projectile model. Steer `dir` toward `toTarget`
-- by at most `maxTurn * dt` radians, rotating about the current/target axis.
-- Direction-only: returns the new unit direction, so speed is preserved by
-- multiplying with the original magnitude. The actual turn is exactly
-- min(budget, angle); zero-vector and antiparallel cases are defined below.
local function steerDirection(dir: Vector3, toTarget: Vector3, maxTurn: number, dt: number): Vector3
    -- Always return a unit vector so callers multiply by speed exactly once.
    -- Zero/invalid input directions fall back to a deterministic axis instead
    -- of returning a non-unit vector (which re-multiplied speed in callers).
    local current: Vector3
    if dir.Magnitude == 0 then
        current = Vector3.zAxis
    else
        current = dir.Unit
    end
    if toTarget.Magnitude == 0 then
        return current -- no aim: hold direction, do not re-scale speed
    end
    local target = toTarget.Unit
    local dot = math.clamp(current:Dot(target), -1, 1)
    local angle = math.acos(dot)                       -- 0..pi
    local budget = maxTurn * dt
    if angle <= 1e-6 then
        return current                                 -- already aimed
    elseif angle >= math.pi - 1e-6 then
        -- Antiparallel: the cross-product axis is undefined. Pick any unit
        -- axis perpendicular to `current` and turn toward it, clamped to the
        -- remaining angle (min(budget, angle)) so an oversized budget can
        -- never rotate past the target and back.
        local axis = current:Cross(Vector3.yAxis)
        if axis.Magnitude < 1e-6 then
            axis = current:Cross(Vector3.xAxis)
        end
        return CFrame.fromAxisAngle(axis.Unit, math.min(budget, angle)) * current
    end
    local axis = current:Cross(target).Unit            -- rotation axis (perpendicular to both)
    local step = math.min(budget, angle)
    return CFrame.fromAxisAngle(axis, step) * current  -- exact bounded rotation
end

local function steerProjectile(cframe: CFrame, velocity: Vector3, target: Vector3, maxTurn: number, dt: number)
    local dir = steerDirection(velocity, target - cframe.Position, maxTurn, dt)
    return dir * velocity.Magnitude
end
```

## Common Patterns

### CFrame: reference frames for moving-platform / vehicle-follow patterns

Think of a part's `CFrame` as the transform from that part's **local space** to world space. Its `LookVector` points down its local −Z; `Vector3.zero` in its local frame is its world position. To transform between frames:

| Want | Code |
|---|---|
| Local frame → world space (point or offset) | `part.CFrame * offset` |
| World position → part's local frame | `part.CFrame:Inverse() * worldPos` (`ToObjectSpace`) |
| World-space `CFrame` → part's local frame | `part.CFrame:Inverse() * worldCFrame` |
| Move a piece with a platform, preserving orientation | `platform.CFrame * characterOffsetCFrame` |

`CFrame` composition is not commutative: `A * B` means "apply A, then in A's frame apply B". For a character standing on a rotating platform, compute the character's offset in the platform's frame **once**, then reapply it each frame after rotating the platform:

```luau
local RunService = game:GetService("RunService")
local platform = workspace:WaitForChild("Platform")

RunService:BindToRenderStep("RotatePlatform", Enum.RenderPriority.Camera.Value - 50, function(dt)
    local character = game.Players.LocalPlayer.Character
    if not character or not character.PrimaryPart then return end

    -- Keep the character fixed in the platform's reference frame
    local characterOffset = platform.CFrame:Inverse() * character:GetPivot()

    platform.CFrame *= CFrame.fromEulerAnglesXYZ(0, dt, 0)

    character:PivotTo(platform.CFrame * characterOffset)
end)
```

If you only need the position (not orientation), `character:GetPivot().Position` and `CFrame.new(platform.CFrame * characterOffset)` are enough; use the full `CFrame` when the character should keep its facing relative to the platform. For vehicles or moving platforms, prefer attachment/anchor constraints or a server-authoritative simulation over per-frame character CFrame writes.

### Elevator / Moving Platform

```luau
local function createElevator(platform: BasePart, bottomY: number, topY: number, speed: number)
    local att = Instance.new("Attachment")
    att.Parent = platform

    local prismatic = Instance.new("PrismaticConstraint")
    prismatic.Attachment0 = att
    -- Attachment1 on a fixed anchor
    local anchor = Instance.new("Part")
    anchor.Anchored = true
    anchor.CanCollide = false
    anchor.Transparency = 1
    anchor.Position = platform.Position
    anchor.Parent = workspace

    local anchorAtt = Instance.new("Attachment")
    anchorAtt.Parent = anchor

    prismatic.Attachment1 = anchorAtt
    prismatic.ActuatorType = Enum.ActuatorType.Servo
    prismatic.Speed = speed
    prismatic.ServoMaxForce = 100000
    prismatic.LowerLimit = 0
    prismatic.UpperLimit = topY - bottomY
    prismatic.Parent = platform

    platform.Anchored = false

    return prismatic -- set .TargetPosition to move
end
```

### Swinging Platform

```luau
local function createSwing(platform: BasePart, pivot: Vector3, maxAngle: number)
    platform.Anchored = false

    local pivotAtt = Instance.new("Attachment")
    pivotAtt.WorldPosition = pivot
    pivotAtt.Parent = workspace.Terrain -- fixed world point

    local platformAtt = Instance.new("Attachment")
    platformAtt.Position = platform.CFrame:PointToObjectSpace(pivot)
    platformAtt.Parent = platform

    local hinge = Instance.new("HingeConstraint")
    hinge.Attachment0 = pivotAtt
    hinge.Attachment1 = platformAtt
    hinge.LimitsEnabled = true
    hinge.LowerAngle = -maxAngle
    hinge.UpperAngle = maxAngle
    hinge.Parent = platform

    return hinge
end
```

## Collision groups: PhysicsService

`PhysicsService` manages collision groups: named sets of `BasePart`s whose mutual collision rules you control. Assign a part by setting `part.CollisionGroup = "GroupName"` (the name, not an object).

Key facts (official):

- `RegisterCollisionGroup(name)` — name cannot be `"Default"`. Registration has slight overhead proportional to workspace part count, so register at edit time in Studio when possible; register/rename/unregister at runtime sparingly.
- `CollisionGroupSetCollidable(name1, name2, bool)` — throws if either group is unregistered; check `IsCollisionGroupRegistered` first.
- Creating, deleting, or modifying collision relationships is server-only (Scripts); clients can only assign parts to existing groups.
- Max 32 groups (`GetMaxCollisionGroups`). `GetRegisteredCollisionGroups()` returns `{name, mask}` entries.
- `CollisionGroupsAreCollidable` returns true if either group is unregistered (default mask collides with everything).

```luau
local PhysicsService = game:GetService("PhysicsService")
if not PhysicsService:IsCollisionGroupRegistered("Ghosts") then
    PhysicsService:RegisterCollisionGroup("Ghosts")
end
PhysicsService:CollisionGroupSetCollidable("Ghosts", "Ghosts", false) -- ghosts pass through ghosts
for _, part in character:GetDescendants() do
    if part:IsA("BasePart") then part.CollisionGroup = "Ghosts" end
end
```

## Network Ownership and Server Authority

### Classic replication

By default in classic replication, Roblox may assign an unanchored assembly to a nearby player. This can make physics responsive but gives that client influence over the simulation, so gameplay-critical outcomes must still be validated.

```luau
-- Keep physics server-authoritative
local function setServerOwnership(model: Model)
    for _, part in model:GetDescendants() do
        if part:IsA("BasePart") and not part.Anchored then
            part:SetNetworkOwner(nil) -- server owns
        end
    end
end

-- Give ownership to driver (for responsive vehicles)
local function setDriverOwnership(vehicle: Model, player: Player)
    for _, part in vehicle:GetDescendants() do
        if part:IsA("BasePart") and not part.Anchored then
            part:SetNetworkOwner(player)
        end
    end
end
```

**Classic trade-off:** Server ownership can be more authoritative but costs server simulation work. Player ownership can be responsive but is not a security boundary. For NPCs and gameplay-critical world objects, prefer server ownership when the project is not using Server Authority. Give a vehicle to its driver only when the resulting behavior is acceptable and validated.

### Server Authority

When `Workspace.AuthorityMode = Server` and the required replication, fixed-simulation, streaming, and input settings are enabled, core gameplay objects can remain server-owned while client prediction keeps controls responsive. The traditional secure-but-laggy trade-off does not apply in the same way. `SetNetworkOwner()` is not a substitute for Server Authority.

Use `InputAction`/`InputContext` and `RunService:BindToSimulation()` (requires `Workspace.UseFixedSimulation` enabled in Studio) for continuous vehicle or character input. Create gameplay-critical predicted instances, such as projectiles, inside the synchronized simulation and make hit or damage transitions idempotent across rollback and resimulation.

For the migration reality check (cost scales with how much simulation you author, attribute payload budget, input buffering, and why side effects are the sharpest edge), see the Server Authority section in `roblox-security`.

## Common Mistakes

- **Forgetting Anchored = false**: Constraints do nothing on anchored parts.
- **Missing Attachments**: Constraints need Attachment0 AND Attachment1. Missing one = silent failure.
- **No network ownership control**: Physics objects get owned by nearest player. Exploiters fling them.
- **Over-constraining**: Too many constraints on one assembly = physics solver instability (jitter).
- **No mass tuning**: Default density makes small parts too light. Use CustomPhysicalProperties.
- **Touched for projectiles**: Touched fires for every contact. Use Raycast for hitscan, Touched only for slow physics projectiles.
- **No lifetime on projectiles**: Forgotten projectiles accumulate and kill server performance.

## Community ecosystem (leads, not sources)

Top-sorted DevForum canon for combat/physics modules. Verify status in-thread.

- Projectiles: [FastCast](https://devforum.roblox.com/t/making-a-combat-game-with-ranged-weapons-fastcast-may-be-the-module-for-you/133474) (3.3k likes, standard); [FastCast2](https://devforum.roblox.com/t/fastcast2-an-improved-version-of-fastcast-with-parallel-scripting-more-extensions-and-statically-typed-a-powerful-modern-projectile-library/4093890) (2025) successor; [projectile motion math](https://devforum.roblox.com/t/modeling-a-projectiles-motion/176677) for lead-aim.
- Melee hitboxes: [Raycast Hitbox](https://devforum.roblox.com/t/raycast-hitbox-401-for-all-your-melee-needs/374482) (3.3k likes); [ShapecastHitbox](https://devforum.roblox.com/t/shapecasthitbox-for-all-your-melee-needs-v025/3624241) successor; [ClientCast](https://devforum.roblox.com/t/clientcast-a-client-based-idiosyncratic-hitbox-system/895217) client-side variant (validate server-side).
- Custom characters/physics: [Chickynoid](https://devforum.roblox.com/t/chickynoid-server-authoritative-character-replacement/1660558) server-authoritative character; [Chrono](https://devforum.roblox.com/t/chrono-drop-in-custom-physics-replication-library/3873294) (2025) physics replication; [Wall stick/Gravity Controller](https://devforum.roblox.com/t/wall-stickgravity-controller/432598) (2.9k likes).
