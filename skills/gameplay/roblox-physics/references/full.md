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
| `LineForce` | Force along the Attachment0→Attachment1 line, applied to Attachment0's assembly | Tractor beams, magnetics, tethers |
| `Torque` | Apply constant torque | Spinning objects |

### Spring/Rope

| Constraint | What it does | Use for |
|-----------|-------------|---------|
| `SpringConstraint` | Bouncy connection | Suspension, trampolines, bouncy bridges |
| `RopeConstraint` | Max distance (slack allowed) | Grappling hooks, hanging objects |
| `RodConstraint` | Fixed distance (rigid) | Rigid linkages, pendulum arms |

## LineForce

`LineForce` applies a force along the line between `Attachment0` and `Attachment1`. By default the force is applied **to the parent of `Attachment0`** (toward or away from `Attachment1`, which serves as the target direction and receives no force unless `ReactionForceEnabled = true`). The direction tracks the parts as they move. Compare `VectorForce`: a fixed `Vector3` (world or attachment-relative) whose direction never changes. Use LineForce when the pull must follow a target part; use VectorForce for constant world-direction thrust.

```luau
local lf = Instance.new("LineForce")
lf.Attachment0 = anchorAtt     -- this part RECEIVES the force (default)
lf.Attachment1 = pulledTargetAtt -- target direction only, unless ReactionForceEnabled
lf.Magnitude = 5000            -- force along the attachment axis (sign sets pull vs push)
lf.InverseSquareLaw = true     -- falloff with distance (gravity/magnet feel)
lf.MaxForce = 10000            -- cap applied force; ONLY active when InverseSquareLaw=true
lf.ReactionForceEnabled = true -- also push the Attachment1 part with equal/opposite force
lf.ApplyAtCenterOfMass = true  -- apply at Attachment0's assembly CoM instead of Attachment0
lf.Parent = anchorPart
```

- `Magnitude`: signed force along the Attachment0→Attachment1 line; sign sets pull vs push.
- `MaxForce`: upper clamp on the absolute force, but **only active when `InverseSquareLaw = true`** (it guards the 1/d² blow-up when the attachments align). With `InverseSquareLaw = false` the property is inert — clamp `Magnitude` in scripts instead.
- `InverseSquareLaw`: force scales as 1/distance² between the attachments.
- `ApplyAtCenterOfMass`: when `true`, force is applied at the center of mass of `Attachment0`'s parent assembly (and the force line starts there); it does not move the application point to `Attachment1`.

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

## Character joints: AnimationConstraint rigs (2026)

With `StarterPlayer.AvatarJointUpgrade` enabled (the default for new experiences; a Studio setting, not script-writable), R15 player characters spawn with `AnimationConstraint` joints and `BallSocketConstraint`s instead of `Motor6D`s. A default R15 character checked in Studio in November 2026 had no `Motor6D` at all: 15 `AnimationConstraint`s, 14 `BallSocketConstraint`s (present and enabled) and 4 `RigidConstraint`s. Code that searches for `Motor6D` silently finds nothing. <!-- temporal: 2026-11 -->

Migration rules from the `AnimationConstraint` reference page:

| Old Motor6D habit | AnimationConstraint rig |
|-------------------|-------------------------|
| `FindFirstChildOfClass("Motor6D")` | `FindFirstChildWhichIsA("AnimationConstraint")`, then fall back to `Motor6D` for legacy rigs |
| `joint:IsA("Motor6D")` guards | Returns `false`; accept `"AnimationConstraint"` too |
| Write `C0`/`C1`/`Part0`/`Part1` | Read-only aliases of `Attachment0.CFrame`, `Attachment1.CFrame` and the attachments' parents. Don't write them |
| Edit rig attachment CFrames | Don't modify `RigAttachment.CFrame`: it breaks retargeting and costs performance |
| `neck.C0 = base * rot` every RenderStepped | Multiply into `Transform` during `RunService.PreSimulation` (`joint.Transform = rot * joint.Transform`), skipping frames where `Animator.EvaluationThrottled` is true |
| Server writes C0 to replicate a pose | Evaluate on clients; sync inputs through attributes or `UnreliableRemoteEvent` |

`IsKinematic = true` (default) behaves like a Motor6D: parts snap to `Transform`. `IsKinematic = false` makes the joint chase `Transform` with forces and torques capped by `MaxForce`/`MaxTorque`, with stiffness from `LinearStrength`/`AngularStrength` (normalized natural frequency, `f / 60`; `0` applies no force or torque; values well above `1` can go unstable) and `LinearDamping`/`AngularDamping` (`1` is critical damping). A root joint may still oscillate at low frequency because it doesn't "see" the downstream mass; raise both strength and damping. `Transform` writes are batched and applied after `PreSimulation`, and an `Animator` overwrites `Transform` each frame between `PreAnimation` and `PreSimulation`, which is why procedural layers go in `PreSimulation`. The `IKControl` reference still describes `Motor6D` chains, so verify IK on an AnimationConstraint rig in Studio.

```luau
-- Illustrative: find a joint on either rig type.
local function findJoint(part: BasePart, name: string): Instance?
    local joint = part:FindFirstChild(name)
    if joint and (joint:IsA("AnimationConstraint") or joint:IsA("Motor6D")) then
        return joint
    end
    return nil
end
```

## Ragdoll

### AnimationConstraint rigs: use the built-in joints

The upgraded rig is already a ragdoll rig: its `BallSocketConstraint`s are present and enabled, and force-based simulation is one property away. **Don't add a `BallSocketConstraint` per joint on top.** Measured in one project: hand-building sockets on a rig that already carried 14 `BallSocketConstraint`s and 19 `NoCollisionConstraint` pairs doubled the sockets to 28, and the rig fought itself and shook. Before building any rig, list the character's existing constraints by class.

Studio-measured 2026-11 (one run, default R15 rig, server-owned parts, `Humanoid` in `Physics`, `BreakJointsOnDeath = false`, dropped tilted 80 degrees with angular impulses on the limbs; mean joint deviation from pose after 4 s):

| AnimationConstraint setting | Mean deviation | Result |
|-----------------------------|----------------|--------|
| `IsKinematic = true` (default) | 0.0° | Rigid |
| `IsKinematic = false`, default strengths (`AngularStrength = 1`, `LinearStrength = 1`, `MaxTorque = 3000`) | 2.1° | Holds the pose: a powered ragdoll, not a limp one |
| `IsKinematic = false`, `AngularStrength = 0` | 44.5° | Limp |
| `IsKinematic = false`, `AngularStrength = 0`, `LinearStrength = 0` | 49.0° | Limp |
| `Enabled = false` (built-in BallSockets only) | 44.3° | Limp |

Rig defaults read in that run: `IsKinematic = true`, `MaxForce = 0`, `MaxTorque = 3000`, `AngularStrength = 1`, `LinearStrength = 1`, with 14 enabled `BallSocketConstraint`s. So `IsKinematic = false` alone keeps the character stiff; a limp ragdoll needs `AngularStrength = 0` as well, or simply `Enabled = false` on the AnimationConstraints. Recover by restoring the saved values, not by rebuilding joints.

Method:

1. Set `Humanoid.BreakJointsOnDeath = false` for a death ragdoll; it defaults to `true`, and broken joints leave nothing to simulate.
2. Put the Humanoid in `Enum.HumanoidStateType.Physics` (or let your death flow do it) so it stops driving the limbs.
3. For each `AnimationConstraint`, record its properties, then set `IsKinematic = false` and `AngularStrength = 0` (or `Enabled = false`); the built-in ball sockets hold the limbs. For a powered or struggling ragdoll, keep `IsKinematic = false` with some strength and cap `MaxTorque`.
4. To recover, restore the recorded values (`IsKinematic = true`) and move the Humanoid to `GettingUp`.

```luau
-- Illustrative: limp ragdoll on an AnimationConstraint rig (settings Studio-measured above).
type Saved = { joint: AnimationConstraint, kinematic: boolean, angular: number }
local ragdolled: { [Model]: { Saved } } = {}

local function enableRagdoll(character: Model)
    if ragdolled[character] then
        return -- idempotent
    end
    local humanoid = character:FindFirstChildOfClass("Humanoid")
    if not humanoid then
        return
    end
    local saved: { Saved } = {}
    for _, d in character:GetDescendants() do
        if d:IsA("AnimationConstraint") then
            table.insert(saved, { joint = d, kinematic = d.IsKinematic, angular = d.AngularStrength })
            d.IsKinematic = false
            d.AngularStrength = 0 -- limp: the built-in BallSockets hold the limbs
        end
    end
    if #saved == 0 then
        return -- legacy Motor6D rig: see the legacy note below
    end
    ragdolled[character] = saved
    humanoid:ChangeState(Enum.HumanoidStateType.Physics)
end

local function disableRagdoll(character: Model)
    local saved = ragdolled[character]
    if not saved then
        return
    end
    ragdolled[character] = nil
    for _, entry in saved do
        if entry.joint.Parent then
            entry.joint.IsKinematic = entry.kinematic
            entry.joint.AngularStrength = entry.angular
        end
    end
    local humanoid = character:FindFirstChildOfClass("Humanoid")
    if humanoid then
        humanoid:ChangeState(Enum.HumanoidStateType.GettingUp)
    end
end
```

Store the record in the character's cleanup object so it can't outlive the character, and restore only what this cycle changed. The sleep-system docs list `AnimationConstraint` with `IsKinematic = false` among constraints whose `MaxForce`/`MaxTorque` matter, and the performance docs recommend joint limits or no-collision constraints so ragdoll limbs don't collide with each other.

### Legacy Motor6D rigs

Experiences with `AvatarJointUpgrade` off, and custom NPC rigs, still use `Motor6D`. The classic method creates two attachments at `C0`/`C1`, a limited `BallSocketConstraint` between them, and disables the motor (keep `Root` for the HumanoidRootPart). Track exactly what you created and which motors you disabled, so recovery destroys only your instances and restores each motor's prior `Enabled`. Check first that the rig doesn't already carry sockets.

### Field-measured ragdoll lessons

- **Corpse ragdolls: remove the Humanoid and HumanoidRootPart once the joints go limp.** A live Humanoid kept setting R15 limbs back to non-colliding, so they sank into the floor. Keep the root collision box no wider than the body; an oversized root rubbed the legs.
- **Settle corpses.** Anchor once every part has moved under about 0.25 studs and 5 degrees for 0.3 s, never in the air; wake on a hit; cap awake pieces by freezing the slowest early; fade after a few seconds and cap the count (oldest first).
- **Consistent death ragdolls across clients.** The server anchors the body where it died and sends one event (hit direction, damage, body velocity, killer); each client hides the server body and simulates its own limp copy from that pose with that throw. The copy must drop its rig attachments or its Humanoid rebuilds joints on top. Give each joint a cone around where the limb hangs plus a small twist limit; lean the shoulder cone forward so a raised arm starts inside it.
- **Check self-contact** with `GetTouchingParts` per part while limp.

## IKControl

`IKControl` runs procedural inverse kinematics on a Motor6D rig; no baked animation needed. Parent it under the rig's `Humanoid`; it bends the joint chain from `ChainRoot` (e.g. `LeftUpperArm`) so `EndEffector` (e.g. `LeftHand`) reaches `Target` (usually an `Attachment` or `BasePart`). Common uses: foot placement on stairs/slopes, hands gripping rails or ladders, head look-at.

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
- The reference describes chains of `Motor6D` joints from `ChainRoot` to `EndEffector`; inspect with `GetChainLength()` / `GetChainCount()`, and verify on AnimationConstraint rigs.

## Projectiles

### Server-Authoritative Raycast Projectile (hitscan)

```luau
-- Modern filter API: ExcludeInstances/IncludeInstances (FilterType not needed).
local function fireProjectile(origin: Vector3, direction: Vector3, damage: number, ignore: {Instance})
    local params = RaycastParams.new()
    params.ExcludeInstances = ignore -- exclusions take priority over inclusions

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

### Raycast filtering: modern and legacy forms

`RaycastParams` has two filter APIs:

- **Modern**: `ExcludeInstances` (array of instances whose descendants are excluded) and `IncludeInstances` (only those descendants are considered). They can be combined for mixed filtering — e.g. include a large folder but exclude specific children — and **exclusions take priority over inclusions** when an instance matches both. `IncludeInstances = nil` is the most permissive filter (includes everything), whereas `IncludeInstances = {}` is the most restrictive (includes nothing) — a deliberate nil-vs-empty distinction when building "raycast only this folder" queries.
- **Legacy (still functional, superseded)**: `FilterDescendantsInstances` + `FilterType = Enum.RaycastFilterType.Exclude/Include`. Older examples using this pair keep working; for new work prefer `ExcludeInstances`/`IncludeInstances`.

### Cast options: Margin, SizeGradient, overrides (2026-11)

`RaycastParams` gained two shape controls, and `WorldRoot:Shapecast` gained overrides: <!-- temporal: 2026-11 -->

- `RaycastParams.Margin` (>= 0, default 0) expands the cast shape uniformly. It applies to `Shapecast`, `Blockcast`, `Spherecast` and `Raycast`; a non-zero `Margin` on `Raycast` makes it a sphere cast of that radius. The expanded shape counts toward the size limit, so a large margin can make a cast throw.
- `RaycastParams.SizeGradient` (>= -1, default 0) scales the shape over the cast: it ends at `1 + SizeGradient` times its size (`0.5` ends 50% larger, `-1` shrinks to nothing). It scales the shape, not the margin, except for `Spherecast`, where radius and margin scale together. Use it for cone-like melee sweeps or widening blasts.
- `WorldRoot:Shapecast(part, direction, params?, cframeOverride?, sizeOverride?)` casts a part's real geometry from another pose or size without moving the part. It ignores parts that **initially** intersect the shape (use `GetPartsInPart` for overlap), excludes the cast part itself, caps distance at 1024 studs, and throws for a Terrain part.
- `RaycastParams.RespectCanCollide = true` makes a query use `CanCollide` instead of `CanQuery` for each hit part.

`BasePart.CanQuery = false` only takes effect when `CanCollide` is also `false` (BasePart reference). A colliding helper part with `CanQuery = false` still blocks rays; measured in one project, invisible colliding helper boxes caught every close melee ray. Exclude helper folders through `ExcludeInstances`, or set `RespectCanCollide = true` on aim and melee rays so non-colliding helpers (a transparent SpawnLocation at head height, invisible triggers) stop counting as hits.

```luau
-- Illustrative melee sweep: widening box that ignores non-colliding helpers.
local function meleeSweep(origin: CFrame, reach: number, ignore: { Instance }): RaycastResult?
    local params = RaycastParams.new()
    params.ExcludeInstances = ignore
    params.RespectCanCollide = true
    params.SizeGradient = 1 -- ends twice as large as it starts
    return workspace:Blockcast(origin, Vector3.new(1, 2, 1), origin.LookVector * reach, params)
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

## Contact data: `BasePart:BindToCollisionSummaries` (2026-10)

`part:BindToCollisionSummaries(callback)` subscribes to per-frame contact data, separate from `Touched`. Once per frame, after simulation, the callback gets an array of summaries for every contact patch the part was in: `Time` (substep time), `Part0` (the subscribed part), `Part1` (the other part, possibly `Terrain`), `Point` (world, averaged over the patch), `Normal` (unit, oriented relative to the subscribed part), `RelativeVelocity` (Part1 relative to Part0 at the point) and `Area` (square studs; `0` for edge or corner contacts). It returns an `RBXScriptConnection`. <!-- temporal: 2026-11 -->

Behavior the docs spell out:

- It throws if the callback is nil or the part is not in `Workspace`. Destroying the part disconnects it.
- Recording runs only while at least one subscription exists, and its cost scales with the number of subscribed parts, not total collisions. Subscribe the few parts that matter (projectiles, vehicles, a held prop).
- Sleeping-on-sleeping contacts and `CanCollide = false` parts produce no summaries.
- Several substeps per frame can give several summaries per patch in one callback; order by `Time`. Non-convex geometry gives one summary per touching hull pair, and terrain contacts split further by normal.
- **Nothing replicates.** Each peer gets summaries only for collisions it owns, so a client-owned body reports on its owner's client. Validate on the server anything that grants damage.

Impact speed is the head-on component: `math.abs(summary.RelativeVelocity:Dot(summary.Normal))`; the remainder is sliding.

```luau
-- Illustrative: impact sound and damage threshold for one owned body.
local IMPACT_SPEED = 25

local function watchImpacts(body: BasePart, onImpact: (Vector3, number) -> ())
    return body:BindToCollisionSummaries(function(summaries)
        local best, bestPoint = 0, nil
        for _, summary in summaries do
            local speed = math.abs(summary.RelativeVelocity:Dot(summary.Normal))
            if speed > best then
                best, bestPoint = speed, summary.Point
            end
        end
        if bestPoint and best >= IMPACT_SPEED then
            onImpact(bestPoint, best)
        end
    end)
end
```

Field note from before this API: a client-owned body's velocity reached the server too coarsely to detect impacts (a 19 studs/s throw read about 5 on the server). Sense impacts on the owning client (now with collision summaries) and validate on the server.

## Mesh collision fidelity: `Tunable` (2026-10)

`Enum.CollisionFidelity.Tunable` exposes `MeshPart.CollisionPrecision` (0-1): `0` favors performance with the simplest collision mesh, `1` favors a close match to the visual mesh. Its default is chosen by the engine from the mesh's size, and it is written in Studio (plugin security), not by game scripts. Other options: `Box` for small or non-interactive props, `Hull` for shapes without deep cavities, `Default` (voxel-based decomposition with concavity), and `PreciseConvexDecomposition` (most accurate, most expensive). Inspect with Studio's Visualization Options → Collision fidelity. <!-- temporal: 2026-11 -->

## Field-measured physics lessons

Measured in individual projects; numbers are examples, verify on your own content.

### Contacts and resting bodies
- **A free part keeps contacts within roughly 5 studs, not only parts it touches.** About 300 contacts while touching about 2 in a dense map of small parts; about 100 free debris pieces made 30k contacts and 30-45 ms of physics. Put tiny map parts in a collision group the debris ignores (cut contacts from 239 to 41 per piece). Read `Stats.ContactsCount` per free object before optimizing anything else; `GetTouchingParts` doesn't show this cost.
- **Large resting unanchored assemblies keep costing physics.** A 1,750-part fallen piece cost about 11 ms per step at zero velocity (17 ms step vs 6 ms anchored). Anchor big debris after about one second still. For client debris piles: anchor below about 0.5 studs/s and 0.3 rad/s held for 0.5 s of clamped dt, unanchor on a nearby hit, and spread anchor and weld work across frames.
- **Settle loot only when slow and grounded.** Anchoring the first frame speed drops caught 9 of 22 pieces at the top of a bounce. Require a short slow run (about 0.15 s) and the box's lowest point within about 0.25 studs of a downward ray hit. Lowest point of a rotated box: `|Right.Y|*hx + |Up.Y|*hy + |Look.Y|*hz` below the center. Anchored loot outlives its support, so periodically unanchor pieces with nothing under them.
- **Resting bodies drift.** Sub-millimetre motion every step and non-orthonormal rotation made a 0.05-degree check fire every frame. Use roughly 0.002 studs and 0.2 degrees, and sweep an awake set a slice per frame.
- **Wake a settled body only for events that can remove its support.** Waking a large body for an unrelated hit cost about 41 ms of physics for seconds.

### Assemblies, velocity and welds
- **Set velocity and impulses on `part.AssemblyRootPart`.** Setting `AssemblyLinearVelocity` on a massless welded part didn't move the body and desynced client and server.
- **Judge a launch by `AssemblyCenterOfMass` and `AssemblyLinearVelocity`,** not one part's position (a tipping plate raised a corner 88 studs at zero velocity). Two bodies with identical velocity may be one assembly; size per-body forces from the body's own parts, not `AssemblyMass`. A fixed seed fixes input, not outcome; repeat runs.
- **Rebuilding welded collision parts right after an impulse drops the impulse** (a struck body read speed 0 over 10 hits). Diff and keep unchanged parts; apply impulses after any rebuild.
- **Don't set `CFrame` on a part welded into a moving assembly to reshape it;** that moves the whole assembly. Disable its `WeldConstraint`, set `Size` and `CFrame`, then re-enable the weld.
- **Overlapping client copies can launch like popcorn** (up to 330 studs/s) even with `NoCollisionConstraint`s on every starting overlap. Capping each body's rise, speed and spin in `Heartbeat` stopped it. Build lazy collision under a falling body before it lands, never remove it under a resting body, and destroy (don't fade) anything removed mid-simulation.

### Ownership, anchoring and authority
- **A client can't make a server-anchored part fall** by setting `Anchored = false` locally; it reads unanchored and never moves. For client debris, clone it into a local folder, hide the original locally (Transparency 1, CanCollide, CanQuery, CanTouch off) and simulate the clone.
- **Moving an anchored HumanoidRootPart on the client doesn't replicate,** so server origin checks silently reject the player's actions. In test scripts move the root unanchored, wait for replication, then anchor; log each server condition when a scripted action does nothing.
- **Don't anchor a character root to freeze a player when forces scale with assembly mass.** An anchored root reports infinite mass; the force becomes infinite and position turns NaN on unanchor. Freeze on the client with zero walk and jump.
- **Physics-reactive NPC ownership with hysteresis:** last hitter for a few seconds, otherwise the nearest player within a radius, switching only when another player is clearly closer. Damage stays on the server.
- **Client physics needs streaming.** Local client parts about 1,400 studs from the character didn't simulate at all; the streaming docs say client simulation happens only in streamed areas. Include a control body that should simply fall.

### Movement and carrying
- **`LinearVelocity` overrides Humanoid air control,** but disabling it lets the Humanoid zero sideways speed almost at once. To keep momentum after a dash, keep it enabled and aim it each frame at the current velocity minus `Gravity * dt` on Y and a little drag.
- **Carrying props:** server `SetNetworkOwner(player)`, then drive from the client with `AlignPosition`/`AlignOrientation` in OneAttachment mode. Put held bodies in a group that ignores characters, or the holder can shove or ride them. Holding a heavy body off-center levers it up; give over-limit bodies zero torque.
- **Two-handed tools:** `IKControl` on arms flipped arms 120-180 degrees per frame when a hand crossed the chest or went overhead. Place the tool from an authored grip frame in HumanoidRootPart space and solve analytic two-bone IK into the shoulder and elbow `Transform`s in `PreSimulation`, bending the elbow toward a fixed side point. Log each arm segment's rotation per frame; hand-to-target distance misses flips.

### Queries and fast bodies
- **Detect a trapped player with body-sized box casts or overlap queries,** not a few rays (8 short rays missed the corners of a 4x4 box). Define trapped narrowly (about 0.6 studs of room, held about 3 s) and reject candidate free spots that are themselves trapped.
- **At high speed a slow frame can skip a short "about to touch" window.** Detect impacts by the segment from the previous to the current position as well as by distance, and cast ahead by the expected delay when a server change lands a round trip later.
- **Drop thousands of parts with proxies.** Simulate one invisible proxy box per chunk and move the anchored, non-colliding visuals with one `workspace:BulkMoveTo` per frame. Measured: 5.5k real physics parts cost 60-70 ms per step; `BulkMoveTo` of 5k parts cost 6-11 ms. Let proxies collide only with the ground or a catch slab.
- **Side-only barriers:** a per-side collision group colliding only with the other side's character groups keeps players out of a spawn while shots and sight rays pass; back it with a server position check.
- **Foliage and props need an interaction matrix.** For each kind (bush, tree, prop), decide whether projectiles, explosions, melee, characters and the camera pass, hit or break, and test every pair. Imported plants cut or merged for performance silently lose collision and query behavior.

## Collision groups: PhysicsService

`PhysicsService` manages collision groups: named sets of `BasePart`s whose mutual collision rules you control. Assign a part by setting `part.CollisionGroup = "GroupName"` (the name, not an object).

Key facts (official):

- `RegisterCollisionGroup(name)`: name cannot be `"Default"`. Registration has slight overhead proportional to workspace part count, so register at edit time in Studio when possible; register/rename/unregister at runtime sparingly.
- `CollisionGroupSetCollidable(name1, name2, bool)`: throws if either group is unregistered; check `IsCollisionGroupRegistered` first.
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

## Overlapping effects, death, and projectile tolerance

- Coordinate independent temporary ragdoll or stun effects under one recovery owner. Track active holds and release each exactly once; recover only after the relevant holds have ended. Test both overlap orders, repeated application, death, character replacement, and the project's supported joint types. Do not let a second effect snapshot an already-modified state and restore it as the original.
- Separate bot-only corpse behavior from real-player death and respawn. A disabled `Dead` state prevents `Humanoid.Died`; verify the actual player elimination path through death registration, match removal and respawn. Include self-inflicted penalties and simultaneous eliminations. Do not generalize an NPC freeze workaround to all humanoids.
- If forgiving character hits are intended, keep their tolerance separate from environment collision. Validate candidate character hits against the unobstructed traveled segment rather than enlarging the world sweep indiscriminately. Test central hits, near misses on both sides of the chosen threshold, doorframes, and targets behind walls with the authoritative resolver. Handle initial overlap explicitly when the chosen sweep does not detect it.
