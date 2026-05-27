---
name: roblox-physics
description: >
  Physics constraints, motors, ragdoll, vehicles, projectiles, and simulated objects.
  Use when building anything that moves physically: cars, doors, ragdolls, cannons,
  elevators, swinging platforms, or custom character controllers.
last_reviewed: 2026-05-27
---

# Roblox Physics & Constraints

Use this skill when building physics-driven gameplay: vehicles, ragdolls, projectiles, mechanical contraptions, elevators, swinging platforms, or anything using constraints and forces.

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
| `Torque` | Apply constant torque | Spinning objects |

### Spring/Rope

| Constraint | What it does | Use for |
|-----------|-------------|---------|
| `SpringConstraint` | Bouncy connection | Suspension, trampolines, bouncy bridges |
| `RopeConstraint` | Max distance (slack allowed) | Grappling hooks, hanging objects |
| `RodConstraint` | Fixed distance (rigid) | Rigid linkages, pendulum arms |

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

```luau
local function enableRagdoll(character: Model)
    local humanoid = character:FindFirstChildOfClass("Humanoid")
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

            motor.Enabled = false
        end
    end
end

local function disableRagdoll(character: Model)
    local humanoid = character:FindFirstChildOfClass("Humanoid")

    -- Remove sockets, re-enable motors
    for _, obj in character:GetDescendants() do
        if obj:IsA("BallSocketConstraint") then
            obj:Destroy()
        elseif obj:IsA("Motor6D") then
            obj.Enabled = true
        end
    end

    humanoid:ChangeState(Enum.HumanoidStateType.GettingUp)
end
```

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

## Common Patterns

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

## Network Ownership

**Critical for physics objects**: By default, the nearest player "owns" the physics simulation of unanchored parts. This means exploiters can fling your physics objects.

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

**Trade-off**: Server ownership = secure but laggy (server tick rate). Player ownership = responsive but exploitable. For vehicles, give ownership to the driver. For NPCs and world objects, keep server-owned.

## Common Mistakes

- **Forgetting Anchored = false**: Constraints do nothing on anchored parts.
- **Missing Attachments**: Constraints need Attachment0 AND Attachment1. Missing one = silent failure.
- **No network ownership control**: Physics objects get owned by nearest player. Exploiters fling them.
- **Over-constraining**: Too many constraints on one assembly = physics solver instability (jitter).
- **No mass tuning**: Default density makes small parts too light. Use CustomPhysicalProperties.
- **Touched for projectiles**: Touched fires for every contact. Use Raycast for hitscan, Touched only for slow physics projectiles.
- **No lifetime on projectiles**: Forgotten projectiles accumulate and kill server performance.
