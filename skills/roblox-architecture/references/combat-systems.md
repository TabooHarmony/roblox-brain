# Combat Systems Reference

> **Load when:** Building combat, weapons, PvP, PvE, damage systems, hitboxes, melee/ranged attacks, combo systems, blocking/parrying, cooldowns, or skill-based combat.

---

## 1. Overview

Combat is one of the most exploited systems in Roblox. Every design decision must start from the principle: **the server is the sole authority on damage, health, and combat state**. The client's job is to send *intent* ("I pressed attack"), show responsive animations/VFX, and display server-confirmed results.

This reference covers:

- Server-authoritative architecture
- Hitbox detection (spatial queries and raycasts)
- Combat state machines
- Damage calculation formulas
- Melee and ranged combat patterns
- Cooldown enforcement
- Anti-exploit hardening

All code examples are production-grade Luau. Adapt to your game's scale.

---

## 2. Combat Architecture

### The Golden Rule

> The client sends **intent**. The server **validates and applies**.

```
Client                          Server
------                          ------
Player presses attack
  |
  +--> FireServer("Attack")
         |
         +--> Validate cooldown
         +--> Validate state (not stunned, not dead)
         +--> Run hitbox detection
         +--> Calculate damage
         +--> Apply damage to targets
         +--> Update attacker state/cooldowns
         |
  <-- FireClient(results) ------+
  |
  +--> Play hit VFX/SFX
  +--> Show damage numbers
```

### Why Not Client-Authoritative?

Exploiters can modify LocalScripts, fire RemoteEvents with fabricated data, and teleport their character. If the client decides who gets hit or how much damage to deal, a single exploiter ruins the entire server.

### Latency Compensation

For fast-paced combat, pure server-side hitboxes can feel unresponsive. Two strategies:

1. **Predictive VFX** -- Client plays the swing animation and VFX immediately on input. Server confirms the hit separately. If the server says "miss," the client shows no damage numbers. Players perceive responsiveness from the animation even if the server takes 50-100ms to confirm.

2. **Client hint with server validation** -- Client sends its estimated hit targets along with the attack request. Server re-runs the hitbox check using the character's server-side position. If the server's check agrees, damage applies. If not, the client hint is discarded. This catches teleport exploits while tolerating minor positional lag.

---

## 3. Hitbox Detection

### Area Detection (Melee / AoE)

Use `workspace:GetPartBoundsInBox()` for volume-based detection:

```luau
local function getHitTargets(attackerRootPart: BasePart, range: number, width: number, height: number): {Model}
    local cf = attackerRootPart.CFrame * CFrame.new(0, 0, -range / 2)
    local size = Vector3.new(width, height, range)

    local overlapParams = OverlapParams.new()
    overlapParams.FilterType = Enum.RaycastFilterType.Exclude
    overlapParams.FilterDescendantsInstances = { attackerRootPart.Parent }

    local parts = workspace:GetPartBoundsInBox(cf, size, overlapParams)

    local hitCharacters: {[Model]: true} = {}
    local results: {Model} = {}

    for _, part in parts do
        local model = part:FindFirstAncestorWhichIsA("Model")
        if model and model:FindFirstChildWhichIsA("Humanoid") and not hitCharacters[model] then
            hitCharacters[model] = true
            table.insert(results, model)
        end
    end

    return results
end
```

### Alternative: `GetPartsInPart`

When you have a physical hitbox part (e.g., a sword blade):

```luau
local overlapParams = OverlapParams.new()
overlapParams.FilterType = Enum.RaycastFilterType.Exclude
overlapParams.FilterDescendantsInstances = { swordModel }

local touchingParts = workspace:GetPartsInPart(hitboxPart, overlapParams)
```

### Raycast Detection (Ranged / Hitscan)

```luau
local function hitscanRaycast(origin: Vector3, direction: Vector3, ignoreList: {Instance}): RaycastResult?
    local raycastParams = RaycastParams.new()
    raycastParams.FilterType = Enum.RaycastFilterType.Exclude
    raycastParams.FilterDescendantsInstances = ignoreList

    return workspace:Raycast(origin, direction, raycastParams)
end
```

### Hitbox Sizing Guidelines

| Weapon Type | Range (studs) | Width (studs) | Height (studs) |
|---|---|---|---|
| Dagger / Fist | 4-5 | 4 | 5 |
| Sword | 6-8 | 5 | 6 |
| Greatsword | 8-12 | 7 | 7 |
| Spear / Polearm | 10-14 | 3 | 5 |
| AoE Slam | 8-10 | 10 | 8 |

Position the hitbox CFrame in front of the character's HumanoidRootPart. Offset by half the range on the Z axis so the box starts at the character and extends forward.

---

## 4. State Machines

Combat states prevent invalid action combinations (e.g., attacking while stunned) and enforce recovery windows.

### State Diagram

```
                    +-----------+
            +------>|   Idle    |<------+
            |       +-----+-----+       |
            |             |             |
       (recovery      (attack      (block
        expires)       input)       input)
            |             |             |
            |       +-----v-----+      |
            |       | Attacking |      |
            |       +-----+-----+      |
            |             |            |
            |        (attack       +---+----+
            |         ends)        | Blocking|
            |             |        +---+----+
            |       +-----v-----+      |
            +-------+ Recovery  |      |
            |       +-----------+  (release
            |                       block)
            |                         |
       +----+-----+            +-----v-----+
       | Stunned  +----------->|   Idle    |
       +----------+ (stun      +-----------+
                    expires)

       Dodge can interrupt Idle or Blocking:
       Idle/Blocking --> Dodging --> Idle
```

### Complete State Machine Implementation

```luau
--!strict
-- CombatStateMachine.luau (ModuleScript in ReplicatedStorage)

export type CombatState = "Idle" | "Attacking" | "Recovery" | "Blocking" | "Dodging" | "Stunned"

export type StateTransition = {
    from: {CombatState},
    to: CombatState,
    condition: ((context: StateMachineContext) -> boolean)?,
}

export type StateMachineContext = {
    player: Player,
    currentState: CombatState,
    stateStartTime: number,
    lastAttackTime: number,
    comboCount: number,
    stunEndTime: number,
    dodgeCooldownEnd: number,
}

local CombatStateMachine = {}
CombatStateMachine.__index = CombatStateMachine

local RECOVERY_DURATION = 0.4
local DODGE_DURATION = 0.5
local DODGE_COOLDOWN = 1.5
local STUN_DEFAULT_DURATION = 1.0
local ATTACK_DURATION = 0.35
local COMBO_WINDOW = 0.8
local MAX_COMBO = 4

local VALID_TRANSITIONS: {StateTransition} = {
    { from = { "Idle" }, to = "Attacking" },
    { from = { "Attacking" }, to = "Recovery" },
    { from = { "Recovery" }, to = "Idle" },
    { from = { "Recovery" }, to = "Attacking" }, -- combo: attack during recovery window
    { from = { "Idle" }, to = "Blocking" },
    { from = { "Blocking" }, to = "Idle" },
    { from = { "Idle", "Blocking" }, to = "Dodging" },
    { from = { "Dodging" }, to = "Idle" },
    { from = { "Idle", "Attacking", "Recovery", "Blocking", "Dodging" }, to = "Stunned" },
    { from = { "Stunned" }, to = "Idle" },
}

function CombatStateMachine.new(player: Player)
    local self = setmetatable({}, CombatStateMachine)
    self.context = {
        player = player,
        currentState = "Idle" :: CombatState,
        stateStartTime = os.clock(),
        lastAttackTime = 0,
        comboCount = 0,
        stunEndTime = 0,
        dodgeCooldownEnd = 0,
    } :: StateMachineContext
    self._onStateChanged = {} :: {(CombatState, CombatState) -> ()}
    return self
end

function CombatStateMachine:getState(): CombatState
    return self.context.currentState
end

function CombatStateMachine:getComboCount(): number
    return self.context.comboCount
end

function CombatStateMachine:onStateChanged(callback: (CombatState, CombatState) -> ())
    table.insert(self._onStateChanged, callback)
end

function CombatStateMachine:canTransition(to: CombatState): boolean
    local from = self.context.currentState

    for _, transition in VALID_TRANSITIONS do
        if transition.to == to and table.find(transition.from, from) then
            if transition.condition and not transition.condition(self.context) then
                continue
            end
            return true
        end
    end

    return false
end

function CombatStateMachine:transition(to: CombatState): boolean
    if not self:canTransition(to) then
        return false
    end

    local from = self.context.currentState
    self.context.currentState = to
    self.context.stateStartTime = os.clock()

    for _, callback in self._onStateChanged do
        callback(from, to)
    end

    return true
end

function CombatStateMachine:tryAttack(): boolean
    local now = os.clock()
    local ctx = self.context

    -- Combo: if in Recovery and within combo window, allow chaining
    if ctx.currentState == "Recovery" then
        local timeSinceAttack = now - ctx.lastAttackTime
        if timeSinceAttack <= COMBO_WINDOW and ctx.comboCount < MAX_COMBO then
            ctx.comboCount += 1
            ctx.lastAttackTime = now
            return self:transition("Attacking")
        end
        return false
    end

    if ctx.currentState ~= "Idle" then
        return false
    end

    ctx.comboCount = 1
    ctx.lastAttackTime = now
    return self:transition("Attacking")
end

function CombatStateMachine:tryBlock(): boolean
    return self:transition("Blocking")
end

function CombatStateMachine:releaseBlock(): boolean
    if self.context.currentState ~= "Blocking" then
        return false
    end
    return self:transition("Idle")
end

function CombatStateMachine:tryDodge(): boolean
    local now = os.clock()
    if now < self.context.dodgeCooldownEnd then
        return false
    end

    if self:transition("Dodging") then
        self.context.dodgeCooldownEnd = now + DODGE_COOLDOWN
        return true
    end
    return false
end

function CombatStateMachine:applyStun(duration: number?)
    local stunDuration = duration or STUN_DEFAULT_DURATION
    self.context.stunEndTime = os.clock() + stunDuration
    self:transition("Stunned")
end

function CombatStateMachine:update()
    local now = os.clock()
    local ctx = self.context
    local elapsed = now - ctx.stateStartTime

    if ctx.currentState == "Attacking" and elapsed >= ATTACK_DURATION then
        self:transition("Recovery")
    elseif ctx.currentState == "Recovery" and elapsed >= RECOVERY_DURATION then
        ctx.comboCount = 0
        self:transition("Idle")
    elseif ctx.currentState == "Dodging" and elapsed >= DODGE_DURATION then
        self:transition("Idle")
    elseif ctx.currentState == "Stunned" and now >= ctx.stunEndTime then
        self:transition("Idle")
    end
end

function CombatStateMachine:destroy()
    table.clear(self._onStateChanged)
end

return CombatStateMachine
```

### Tuning Constants

| Constant | Default | Effect |
|---|---|---|
| `ATTACK_DURATION` | 0.35s | How long the attack hitbox is active |
| `RECOVERY_DURATION` | 0.4s | Window after attack before returning to Idle |
| `COMBO_WINDOW` | 0.8s | Time after an attack during which the next attack counts as a combo |
| `MAX_COMBO` | 4 | Maximum consecutive hits in a combo chain |
| `DODGE_DURATION` | 0.5s | Invulnerability / movement duration |
| `DODGE_COOLDOWN` | 1.5s | Time between dodge uses |
| `STUN_DEFAULT_DURATION` | 1.0s | Default stun length |

---

## 5. Damage Calculation

### Formula

```
finalDamage = baseDamage
            * weaponMultiplier
            * (1 + totalBuffPercent)
            * (1 - defensePercent)
            * critMultiplier
            * comboMultiplier
            * typeEffectiveness
```

### Implementation

```luau
--!strict
-- DamageCalculator.luau (ModuleScript in ServerScriptService)

export type DamageType = "Physical" | "Magical" | "Fire" | "Ice" | "Lightning"

export type WeaponStats = {
    baseDamage: number,
    weaponMultiplier: number,
    damageType: DamageType,
    critChance: number,    -- 0.0 to 1.0
    critMultiplier: number, -- e.g. 1.5 = 150% damage on crit
}

export type CombatStats = {
    attackBuff: number,   -- 0.0 to 1.0 (e.g. 0.25 = 25% buff)
    defense: number,      -- 0.0 to 1.0 (e.g. 0.3 = 30% damage reduction)
    resistances: {[DamageType]: number}, -- 0.0 to 1.0 per type
}

export type DamageResult = {
    rawDamage: number,
    finalDamage: number,
    isCritical: boolean,
    damageType: DamageType,
    blocked: boolean,
}

local DamageCalculator = {}

local COMBO_MULTIPLIERS = { 1.0, 1.1, 1.25, 1.5 }
local BLOCK_REDUCTION = 0.8 -- blocking reduces damage by 80%
local MIN_DAMAGE = 1

function DamageCalculator.calculate(
    weapon: WeaponStats,
    attackerStats: CombatStats,
    defenderStats: CombatStats,
    comboHit: number,
    isBlocking: boolean
): DamageResult
    local baseDamage = weapon.baseDamage * weapon.weaponMultiplier

    -- Buff multiplier
    local buffMultiplier = 1 + attackerStats.attackBuff

    -- Defense multiplier
    local defenseMultiplier = 1 - math.clamp(defenderStats.defense, 0, 0.9) -- cap at 90%

    -- Elemental resistance
    local resistance = defenderStats.resistances[weapon.damageType] or 0
    local typeMultiplier = 1 - math.clamp(resistance, 0, 0.9)

    -- Critical hit
    local isCritical = math.random() < weapon.critChance
    local critMultiplier = if isCritical then weapon.critMultiplier else 1.0

    -- Combo scaling
    local comboIndex = math.clamp(comboHit, 1, #COMBO_MULTIPLIERS)
    local comboMultiplier = COMBO_MULTIPLIERS[comboIndex]

    -- Combine
    local rawDamage = baseDamage * buffMultiplier * critMultiplier * comboMultiplier
    local finalDamage = rawDamage * defenseMultiplier * typeMultiplier

    -- Blocking
    local blocked = false
    if isBlocking then
        finalDamage *= (1 - BLOCK_REDUCTION)
        blocked = true
    end

    finalDamage = math.max(math.floor(finalDamage), MIN_DAMAGE)

    return {
        rawDamage = rawDamage,
        finalDamage = finalDamage,
        isCritical = isCritical,
        damageType = weapon.damageType,
        blocked = blocked,
    }
end

return DamageCalculator
```

### Damage Numbers Display (Client)

```luau
-- DamageDisplay.luau (ModuleScript in ReplicatedStorage, called from client)

local TweenService = game:GetService("TweenService")

local DamageDisplay = {}

local COLORS = {
    Normal = Color3.fromRGB(255, 255, 255),
    Critical = Color3.fromRGB(255, 50, 50),
    Blocked = Color3.fromRGB(150, 150, 150),
    Heal = Color3.fromRGB(50, 255, 50),
}

function DamageDisplay.show(target: Model, amount: number, isCritical: boolean, blocked: boolean)
    local head = target:FindFirstChild("Head") :: BasePart?
    if not head then
        return
    end

    local billboard = Instance.new("BillboardGui")
    billboard.Size = UDim2.fromOffset(100, 40)
    billboard.StudsOffset = Vector3.new(math.random(-2, 2), 2, 0)
    billboard.AlwaysOnTop = true
    billboard.Parent = head

    local label = Instance.new("TextLabel")
    label.Size = UDim2.fromScale(1, 1)
    label.BackgroundTransparency = 1
    label.Text = tostring(amount)
    label.Font = Enum.Font.GothamBold
    label.TextScaled = true

    if blocked then
        label.TextColor3 = COLORS.Blocked
        label.Text = amount .. " (Blocked)"
    elseif isCritical then
        label.TextColor3 = COLORS.Critical
        label.Text = amount .. "!"
        label.TextSize = 28
    else
        label.TextColor3 = COLORS.Normal
    end

    label.Parent = billboard

    -- Float up and fade
    local tweenInfo = TweenInfo.new(1.0, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
    local tween = TweenService:Create(billboard, tweenInfo, {
        StudsOffset = billboard.StudsOffset + Vector3.new(0, 3, 0),
    })

    local fadeTween = TweenService:Create(label, tweenInfo, {
        TextTransparency = 1,
    })

    tween:Play()
    fadeTween:Play()

    fadeTween.Completed:Once(function()
        billboard:Destroy()
    end)
end

return DamageDisplay
```

---

## 6. Melee Combat

### Swing Detection

The server creates a hitbox in front of the attacker for the duration of the attack state. Only characters that intersect the box during the active window take damage.

```luau
local function performMeleeAttack(attacker: Model, weapon: WeaponStats, comboHit: number): {DamageResult}
    local rootPart = attacker:FindFirstChild("HumanoidRootPart") :: BasePart
    if not rootPart then
        return {}
    end

    local targets = getHitTargets(rootPart, weapon.range or 7, weapon.width or 5, weapon.height or 6)
    local results: {DamageResult} = {}

    for _, targetModel in targets do
        local humanoid = targetModel:FindFirstChildWhichIsA("Humanoid")
        if not humanoid or humanoid.Health <= 0 then
            continue
        end

        local defenderStats = getStatsForCharacter(targetModel) -- your stats lookup
        local isBlocking = getStateMachine(targetModel):getState() == "Blocking"

        local result = DamageCalculator.calculate(weapon, getStatsForCharacter(attacker), defenderStats, comboHit, isBlocking)
        humanoid:TakeDamage(result.finalDamage)
        table.insert(results, result)
    end

    return results
end
```

### Combo System

Track consecutive hits within the combo window. Each successive hit escalates damage:

| Combo Hit | Multiplier | Typical Effect |
|---|---|---|
| 1 | 1.0x | Normal swing |
| 2 | 1.1x | Faster animation |
| 3 | 1.25x | Wider hitbox |
| 4 | 1.5x | Finisher with knockback |

The state machine tracks `comboCount`. When the combo window expires (player doesn't attack within `COMBO_WINDOW` seconds), the count resets to 0 on transition back to Idle.

### Parry / Block

- **Block**: Hold a button to enter Blocking state. Incoming damage is reduced by `BLOCK_REDUCTION` (80%). Blocking drains a stamina resource (optional). If stamina hits 0, the block breaks and the player is Stunned.
- **Parry**: A precisely timed block (within ~0.15s of an incoming attack) negates all damage and stuns the attacker instead. Implementation: check if the defender entered Blocking state within a `PARRY_WINDOW` before the hit lands.

```luau
local PARRY_WINDOW = 0.15

local function isParry(defenderStateMachine): boolean
    if defenderStateMachine:getState() ~= "Blocking" then
        return false
    end
    local blockDuration = os.clock() - defenderStateMachine.context.stateStartTime
    return blockDuration <= PARRY_WINDOW
end
```

### Knockback

Apply knockback on combo finishers or heavy attacks using `LinearVelocity` (preferred over deprecated `BodyVelocity`):

```luau
local function applyKnockback(targetRootPart: BasePart, direction: Vector3, force: number, duration: number)
    local attachment = targetRootPart:FindFirstChild("RootAttachment") :: Attachment?
    if not attachment then
        return
    end

    local linearVelocity = Instance.new("LinearVelocity")
    linearVelocity.Attachment0 = attachment
    linearVelocity.VelocityConstraintMode = Enum.VelocityConstraintMode.Vector
    linearVelocity.MaxForce = math.huge
    linearVelocity.VectorVelocity = direction.Unit * force
    linearVelocity.Parent = targetRootPart

    task.delay(duration, function()
        linearVelocity:Destroy()
    end)
end
```

---

## 7. Ranged Combat

### Projectile System

Create a physical part that moves each frame. Good for visible, dodgeable projectiles.

```luau
local RunService = game:GetService("RunService")

local function fireProjectile(origin: CFrame, speed: number, maxDistance: number, gravity: number, onHit: (RaycastResult) -> ())
    local projectile = Instance.new("Part")
    projectile.Size = Vector3.new(0.3, 0.3, 1)
    projectile.CFrame = origin
    projectile.Anchored = true
    projectile.CanCollide = false
    projectile.Parent = workspace

    local velocity = origin.LookVector * speed
    local distanceTraveled = 0

    local raycastParams = RaycastParams.new()
    raycastParams.FilterType = Enum.RaycastFilterType.Exclude
    raycastParams.FilterDescendantsInstances = { projectile }

    local connection: RBXScriptConnection
    connection = RunService.Heartbeat:Connect(function(dt: number)
        -- Apply gravity
        velocity += Vector3.new(0, -gravity * dt, 0)

        local displacement = velocity * dt
        local rayResult = workspace:Raycast(projectile.Position, displacement, raycastParams)

        if rayResult then
            connection:Disconnect()
            onHit(rayResult)
            projectile:Destroy()
            return
        end

        projectile.CFrame = CFrame.new(projectile.Position + displacement, projectile.Position + displacement + velocity)
        distanceTraveled += displacement.Magnitude

        if distanceTraveled >= maxDistance then
            connection:Disconnect()
            projectile:Destroy()
        end
    end)
end
```

### Hitscan (Instant Raycast)

For sniper rifles, laser beams, or any instant-hit weapon:

```luau
local function hitscanAttack(attacker: Model, aimDirection: Vector3, maxRange: number): RaycastResult?
    local rootPart = attacker:FindFirstChild("HumanoidRootPart") :: BasePart
    if not rootPart then
        return nil
    end

    local origin = rootPart.Position + Vector3.new(0, 1.5, 0) -- eye height
    local raycastParams = RaycastParams.new()
    raycastParams.FilterType = Enum.RaycastFilterType.Exclude
    raycastParams.FilterDescendantsInstances = { attacker }

    return workspace:Raycast(origin, aimDirection.Unit * maxRange, raycastParams)
end
```

### Bullet Drop

Simulate gravity over distance by bending the ray. For longer ranges, split into segments:

```luau
local function raycastWithDrop(origin: Vector3, direction: Vector3, segments: number, dropPerSegment: number): RaycastResult?
    local segmentLength = direction.Magnitude / segments
    local currentPos = origin
    local currentDir = direction.Unit

    local raycastParams = RaycastParams.new()
    raycastParams.FilterType = Enum.RaycastFilterType.Exclude

    for i = 1, segments do
        local drop = Vector3.new(0, -dropPerSegment * i, 0)
        local segmentDir = (currentDir * segmentLength) + drop

        local result = workspace:Raycast(currentPos, segmentDir, raycastParams)
        if result then
            return result
        end

        currentPos += segmentDir
    end

    return nil
end
```

### Spread / Bloom Patterns

Add random deviation within a cone for shotguns, automatic weapons, or hip-fire:

```luau
local function applySpread(direction: Vector3, spreadAngleDegrees: number): Vector3
    local spreadRadians = math.rad(spreadAngleDegrees)
    local randomAngle = math.random() * math.pi * 2
    local randomSpread = math.random() * spreadRadians

    local right = direction:Cross(Vector3.yAxis).Unit
    local up = right:Cross(direction).Unit

    local offset = (right * math.cos(randomAngle) + up * math.sin(randomAngle)) * math.sin(randomSpread)

    return (direction.Unit + offset).Unit
end

-- Usage: shotgun with 8 pellets, 12-degree spread
for i = 1, 8 do
    local spreadDir = applySpread(aimDirection, 12)
    local result = hitscanAttack(attacker, spreadDir, 50)
    if result then
        -- process hit
    end
end
```

---

## 8. WCS (Weapon Combat System) Framework

### What It Is

WCS is a community-built framework for Roblox combat that provides:

- Skill/ability definition with built-in cooldowns
- Status effects (buffs, debuffs, DoTs)
- Moveset management (assign skills to characters)
- Client-server synchronization out of the box
- Holdable skills, channeling, and charge mechanics

### When to Use WCS

| Scenario | Recommendation |
|---|---|
| Complex skill-based combat (RPG, fighting game) | **Use WCS** -- saves weeks of boilerplate |
| Many unique abilities with varied behavior | **Use WCS** -- skill definition system is well designed |
| Simple melee/ranged with few weapons | **Build custom** -- WCS adds unnecessary overhead |
| Learning combat fundamentals | **Build custom** -- understand the internals first |
| Very custom combo/input systems | **Build custom or extend WCS** -- may fight the framework |

### Basic WCS Skill Definition

```luau
-- Example: a fireball skill in WCS
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local WCS = require(ReplicatedStorage.Packages.WCS)

local Fireball = WCS.RegisterSkill("Fireball")
Fireball.CooldownTime = 3
Fireball.MaxHoldTime = 2

function Fireball:OnStartServer()
    -- Server-side fireball logic
    local character = self.Character
    -- spawn projectile, deal damage, etc.
end

function Fireball:OnStartClient()
    -- Client-side VFX
    -- play casting animation, spawn particle emitter
end
```

Install WCS via Wally: `wcs = "digest/wcs@latest"` or grab the model from the toolbox.

---

## 9. Cooldown Systems

### Server-Side Cooldown Tracking

All cooldowns must be tracked on the server. The client can display a timer, but the server rejects actions that violate cooldowns.

```luau
--!strict
-- CooldownManager.luau (ModuleScript in ServerScriptService)

local CooldownManager = {}
CooldownManager.__index = CooldownManager

type CooldownMap = {[string]: number} -- abilityName -> expiry timestamp
type PlayerCooldowns = {[Player]: CooldownMap}

local cooldowns: PlayerCooldowns = {}

function CooldownManager.initialize(player: Player)
    cooldowns[player] = {}
end

function CooldownManager.cleanup(player: Player)
    cooldowns[player] = nil
end

function CooldownManager.isReady(player: Player, abilityName: string): boolean
    local playerCooldowns = cooldowns[player]
    if not playerCooldowns then
        return false
    end

    local expiry = playerCooldowns[abilityName]
    if not expiry then
        return true
    end

    return os.clock() >= expiry
end

function CooldownManager.startCooldown(player: Player, abilityName: string, duration: number)
    local playerCooldowns = cooldowns[player]
    if not playerCooldowns then
        return
    end

    playerCooldowns[abilityName] = os.clock() + duration
end

function CooldownManager.getRemainingTime(player: Player, abilityName: string): number
    local playerCooldowns = cooldowns[player]
    if not playerCooldowns then
        return 0
    end

    local expiry = playerCooldowns[abilityName]
    if not expiry then
        return 0
    end

    return math.max(0, expiry - os.clock())
end

return CooldownManager
```

### Client-Side Cooldown Display

```luau
-- CooldownUI.luau (LocalScript in StarterPlayerScripts)

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local cooldownEvent = ReplicatedStorage:WaitForChild("CooldownStarted") :: RemoteEvent

local activeCooldowns: {[string]: {startTime: number, duration: number, frame: Frame}} = {}

cooldownEvent.OnClientEvent:Connect(function(abilityName: string, duration: number)
    local frame = findAbilityFrame(abilityName) -- your UI lookup
    if not frame then
        return
    end

    local overlay = frame:FindFirstChild("CooldownOverlay") :: Frame
    local label = frame:FindFirstChild("CooldownLabel") :: TextLabel

    activeCooldowns[abilityName] = {
        startTime = os.clock(),
        duration = duration,
        frame = frame,
    }
end)

RunService.RenderStepped:Connect(function()
    for abilityName, data in activeCooldowns do
        local elapsed = os.clock() - data.startTime
        local remaining = data.duration - elapsed

        if remaining <= 0 then
            -- Cooldown finished
            local overlay = data.frame:FindFirstChild("CooldownOverlay") :: Frame?
            if overlay then
                overlay.Size = UDim2.fromScale(1, 0)
            end
            local label = data.frame:FindFirstChild("CooldownLabel") :: TextLabel?
            if label then
                label.Text = ""
            end
            activeCooldowns[abilityName] = nil
            continue
        end

        -- Update sweep and text
        local fraction = remaining / data.duration
        local overlay = data.frame:FindFirstChild("CooldownOverlay") :: Frame?
        if overlay then
            overlay.Size = UDim2.fromScale(1, fraction)
        end
        local label = data.frame:FindFirstChild("CooldownLabel") :: TextLabel?
        if label then
            label.Text = string.format("%.1f", remaining)
        end
    end
end)
```

---

## 10. Complete Melee Combat System

This ties together the state machine, hitbox detection, damage calculation, and cooldowns into a working server-side combat handler.

```luau
--!strict
-- MeleeCombatServer.luau (Script in ServerScriptService)

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local CombatStateMachine = require(ReplicatedStorage:WaitForChild("CombatStateMachine"))
local DamageCalculator = require(game.ServerScriptService:WaitForChild("DamageCalculator"))
local CooldownManager = require(game.ServerScriptService:WaitForChild("CooldownManager"))

-- RemoteEvents
local attackRemote = ReplicatedStorage:WaitForChild("AttackRemote") :: RemoteEvent
local blockRemote = ReplicatedStorage:WaitForChild("BlockRemote") :: RemoteEvent
local dodgeRemote = ReplicatedStorage:WaitForChild("DodgeRemote") :: RemoteEvent
local combatResultRemote = ReplicatedStorage:WaitForChild("CombatResultRemote") :: RemoteEvent
local cooldownRemote = ReplicatedStorage:WaitForChild("CooldownStarted") :: RemoteEvent

-- Per-player state
local playerStateMachines: {[Player]: typeof(CombatStateMachine.new(nil :: any))} = {}

-- Weapon config (in production, load from a data module)
local DEFAULT_WEAPON: DamageCalculator.WeaponStats = {
    baseDamage = 20,
    weaponMultiplier = 1.0,
    damageType = "Physical",
    critChance = 0.1,
    critMultiplier = 1.5,
}

local DEFAULT_STATS: DamageCalculator.CombatStats = {
    attackBuff = 0,
    defense = 0,
    resistances = {},
}

local ATTACK_COOLDOWN = 0.3
local DODGE_INVULN_TAG = "DodgeInvuln"

-- Hitbox detection
local function getHitTargets(attackerRootPart: BasePart, range: number, width: number, height: number): {Model}
    local cf = attackerRootPart.CFrame * CFrame.new(0, 0, -range / 2)
    local size = Vector3.new(width, height, range)

    local overlapParams = OverlapParams.new()
    overlapParams.FilterType = Enum.RaycastFilterType.Exclude
    overlapParams.FilterDescendantsInstances = { attackerRootPart.Parent }

    local parts = workspace:GetPartBoundsInBox(cf, size, overlapParams)

    local hitCharacters: {[Model]: true} = {}
    local results: {Model} = {}

    for _, part in parts do
        local model = part:FindFirstAncestorWhichIsA("Model")
        if model and model:FindFirstChildWhichIsA("Humanoid") and not hitCharacters[model] then
            hitCharacters[model] = true
            table.insert(results, model)
        end
    end

    return results
end

-- Knockback helper
local function applyKnockback(targetRootPart: BasePart, direction: Vector3, force: number)
    local attachment = targetRootPart:FindFirstChild("RootAttachment") :: Attachment?
    if not attachment then
        return
    end

    local linearVelocity = Instance.new("LinearVelocity")
    linearVelocity.Attachment0 = attachment
    linearVelocity.VelocityConstraintMode = Enum.VelocityConstraintMode.Vector
    linearVelocity.MaxForce = math.huge
    linearVelocity.VectorVelocity = direction.Unit * force
    linearVelocity.Parent = targetRootPart

    task.delay(0.3, function()
        linearVelocity:Destroy()
    end)
end

-- Parry check
local PARRY_WINDOW = 0.15

local function isParry(defenderSM: typeof(CombatStateMachine.new(nil :: any))): boolean
    if defenderSM:getState() ~= "Blocking" then
        return false
    end
    return (os.clock() - defenderSM.context.stateStartTime) <= PARRY_WINDOW
end

-- Get state machine for a character model (NPC or player)
local function getStateMachineForCharacter(character: Model): typeof(CombatStateMachine.new(nil :: any))?
    local player = Players:GetPlayerFromCharacter(character)
    if player then
        return playerStateMachines[player]
    end
    return nil
end

-- Handle attack
local function onAttack(player: Player)
    local sm = playerStateMachines[player]
    if not sm then
        return
    end

    -- Cooldown check
    if not CooldownManager.isReady(player, "Attack") then
        return
    end

    -- State machine check
    if not sm:tryAttack() then
        return
    end

    CooldownManager.startCooldown(player, "Attack", ATTACK_COOLDOWN)

    -- Get character
    local character = player.Character
    if not character then
        return
    end
    local rootPart = character:FindFirstChild("HumanoidRootPart") :: BasePart?
    if not rootPart then
        return
    end

    -- Hitbox detection
    local comboHit = sm:getComboCount()
    local range = if comboHit >= 4 then 9 else 7
    local width = if comboHit >= 3 then 7 else 5
    local targets = getHitTargets(rootPart, range, width, 6)

    for _, targetModel in targets do
        local targetHumanoid = targetModel:FindFirstChildWhichIsA("Humanoid")
        if not targetHumanoid or targetHumanoid.Health <= 0 then
            continue
        end

        -- Check dodge invulnerability
        if targetModel:FindFirstChild(DODGE_INVULN_TAG) then
            continue
        end

        -- Check parry
        local targetSM = getStateMachineForCharacter(targetModel)
        if targetSM and isParry(targetSM) then
            -- Parry: stun the attacker instead
            sm:applyStun(1.2)
            combatResultRemote:FireClient(player, "Parried", targetModel)

            local targetPlayer = Players:GetPlayerFromCharacter(targetModel)
            if targetPlayer then
                combatResultRemote:FireClient(targetPlayer, "ParrySuccess", character)
            end
            continue
        end

        -- Calculate damage
        local isBlocking = if targetSM then targetSM:getState() == "Blocking" else false
        local attackerStats = DEFAULT_STATS -- replace with real stats lookup
        local defenderStats = DEFAULT_STATS -- replace with real stats lookup

        local result = DamageCalculator.calculate(DEFAULT_WEAPON, attackerStats, defenderStats, comboHit, isBlocking)
        targetHumanoid:TakeDamage(result.finalDamage)

        -- Knockback on combo finisher
        local targetRootPart = targetModel:FindFirstChild("HumanoidRootPart") :: BasePart?
        if comboHit >= 4 and targetRootPart then
            local knockDir = (targetRootPart.Position - rootPart.Position)
            applyKnockback(targetRootPart, knockDir, 50)
        end

        -- Notify all relevant clients
        combatResultRemote:FireAllClients("DamageDealt", {
            target = targetModel,
            amount = result.finalDamage,
            isCritical = result.isCritical,
            blocked = result.blocked,
            comboHit = comboHit,
        })
    end
end

-- Handle block
local function onBlock(player: Player, isBlocking: boolean)
    local sm = playerStateMachines[player]
    if not sm then
        return
    end

    if isBlocking then
        sm:tryBlock()
    else
        sm:releaseBlock()
    end
end

-- Handle dodge
local function onDodge(player: Player)
    local sm = playerStateMachines[player]
    if not sm then
        return
    end

    if not sm:tryDodge() then
        return
    end

    local character = player.Character
    if not character then
        return
    end
    local rootPart = character:FindFirstChild("HumanoidRootPart") :: BasePart?
    if not rootPart then
        return
    end

    -- Add invulnerability tag
    local tag = Instance.new("BoolValue")
    tag.Name = DODGE_INVULN_TAG
    tag.Parent = character

    -- Apply dodge movement
    local moveDir = rootPart.CFrame.LookVector
    applyKnockback(rootPart, moveDir, 60)

    -- Notify client for cooldown display
    cooldownRemote:FireClient(player, "Dodge", 1.5)

    -- Remove tag after dodge duration
    task.delay(0.5, function()
        tag:Destroy()
    end)
end

-- Player setup / teardown
Players.PlayerAdded:Connect(function(player: Player)
    CooldownManager.initialize(player)

    player.CharacterAdded:Connect(function()
        local sm = CombatStateMachine.new(player)
        playerStateMachines[player] = sm
    end)

    player.CharacterRemoving:Connect(function()
        local sm = playerStateMachines[player]
        if sm then
            sm:destroy()
            playerStateMachines[player] = nil
        end
    end)
end)

Players.PlayerRemoving:Connect(function(player: Player)
    CooldownManager.cleanup(player)
    local sm = playerStateMachines[player]
    if sm then
        sm:destroy()
        playerStateMachines[player] = nil
    end
end)

-- Update state machines every frame
RunService.Heartbeat:Connect(function()
    for _, sm in playerStateMachines do
        sm:update()
    end
end)

-- Connect remotes
attackRemote.OnServerEvent:Connect(onAttack)
blockRemote.OnServerEvent:Connect(function(player: Player, isBlocking: boolean)
    if typeof(isBlocking) ~= "boolean" then
        return -- type validation
    end
    onBlock(player, isBlocking)
end)
dodgeRemote.OnServerEvent:Connect(onDodge)
```

### Client-Side Input Handler

```luau
--!strict
-- CombatInput.luau (LocalScript in StarterPlayerScripts)

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local attackRemote = ReplicatedStorage:WaitForChild("AttackRemote") :: RemoteEvent
local blockRemote = ReplicatedStorage:WaitForChild("BlockRemote") :: RemoteEvent
local dodgeRemote = ReplicatedStorage:WaitForChild("DodgeRemote") :: RemoteEvent

-- Attack: left mouse click
UserInputService.InputBegan:Connect(function(input: InputObject, gameProcessed: boolean)
    if gameProcessed then
        return
    end

    if input.UserInputType == Enum.UserInputType.MouseButton1 then
        attackRemote:FireServer()
    elseif input.KeyCode == Enum.KeyCode.F then
        blockRemote:FireServer(true)
    elseif input.KeyCode == Enum.KeyCode.Q then
        dodgeRemote:FireServer()
    end
end)

-- Release block
UserInputService.InputEnded:Connect(function(input: InputObject, gameProcessed: boolean)
    if input.KeyCode == Enum.KeyCode.F then
        blockRemote:FireServer(false)
    end
end)
```

---

## 11. Best Practices

### Server Authority

- **All damage is applied server-side.** The client never calls `Humanoid:TakeDamage()`.
- **Validate every RemoteEvent argument.** Check `typeof()`, clamp numeric ranges, verify the player owns the weapon they claim to use.
- **Run hitbox detection on the server** using the server's known character positions, not client-reported positions.

### Hit Registration Integrity

- Use `OverlapParams.FilterDescendantsInstances` to exclude the attacker's own character from hitbox results.
- Deduplicate hits: track which characters were already hit during a single attack swing to prevent multi-hit exploits.
- Limit hit targets per swing (e.g., max 5) to prevent AoE exploits.

### Fair PvP

- Normalize base stats in PvP arenas so gear differences don't create unfair advantages, or use matchmaking tiers.
- Telegraph attacks: give enemies visual/audio cues (wind-up animation, sound effect) before damage lands so they can react.
- Balance risk vs. reward: powerful attacks should have longer recovery, wider parry windows, or more telegraphing.

### Performance

- Don't create new `OverlapParams` / `RaycastParams` every frame. Create once, reuse, update the filter list as needed.
- Pool damage number BillboardGuis instead of creating/destroying them constantly.
- For large-scale battles (20+ players), consider spatial partitioning to limit hitbox checks to nearby characters only.

---

## 12. Anti-Patterns

### Client-Side Damage Calculation

```luau
-- BAD: Client decides damage and tells server
attackRemote:FireServer(targetPlayer, 9999) -- exploiter sends any number

-- GOOD: Client sends intent, server calculates
attackRemote:FireServer() -- server determines targets and damage
```

### Trusting Client Hitbox Results

```luau
-- BAD: Client reports who it hit
attackRemote:FireServer(hitTargets) -- exploiter sends all players on server

-- GOOD: Server runs its own hitbox detection
-- Client sends nothing except "I attacked"
```

### No Cooldown Enforcement

```luau
-- BAD: Only client checks cooldowns (exploiter removes the check)
-- BAD: Server tracks cooldown but doesn't reject early attacks

-- GOOD: Server rejects and silently drops requests that violate cooldowns
if not CooldownManager.isReady(player, "Attack") then
    return -- silently ignore, don't send error messages exploiters can use
end
```

### No State Validation

```luau
-- BAD: Allow attacking while stunned, dead, or in menus
-- BAD: Allow blocking and attacking simultaneously

-- GOOD: State machine enforces valid transitions
if not stateMachine:canTransition("Attacking") then
    return
end
```

### Instant Unavoidable Attacks

- Every attack should have a counter: dodging, blocking, parrying, or spacing.
- If an attack is instant, it should deal low damage. If it deals high damage, it should be telegraphed and avoidable.
- Avoid homing projectiles that are both fast and undodgeable.

### Floating Point Stat Stacking

```luau
-- BAD: uncapped buff stacking
totalBuff = totalBuff + newBuff -- can exceed 100%, goes to infinity

-- GOOD: clamp all multipliers
totalBuff = math.clamp(totalBuff + newBuff, 0, 1.0) -- cap at 100% buff
defense = math.clamp(defense, 0, 0.9) -- cap at 90% reduction, minimum damage always gets through
```

---

## Quick Reference: Required RemoteEvents

Create these in ReplicatedStorage for the complete system:

| RemoteEvent Name | Direction | Purpose |
|---|---|---|
| `AttackRemote` | Client -> Server | Player pressed attack |
| `BlockRemote` | Client -> Server | Player started/stopped blocking |
| `DodgeRemote` | Client -> Server | Player pressed dodge |
| `CombatResultRemote` | Server -> Client | Damage dealt, parry, etc. for VFX |
| `CooldownStarted` | Server -> Client | Ability cooldown began (for UI) |

---

## Quick Reference: Module Locations

| Module | Location | Purpose |
|---|---|---|
| `CombatStateMachine` | ReplicatedStorage | State machine (shared types) |
| `DamageCalculator` | ServerScriptService | Damage formula (server only) |
| `CooldownManager` | ServerScriptService | Cooldown tracking (server only) |
| `DamageDisplay` | ReplicatedStorage | Floating damage numbers (client) |
| `MeleeCombatServer` | ServerScriptService | Main combat handler (server) |
| `CombatInput` | StarterPlayerScripts | Input -> RemoteEvent (client) |
