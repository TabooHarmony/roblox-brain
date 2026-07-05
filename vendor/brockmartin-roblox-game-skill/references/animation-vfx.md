# Animation & VFX Reference

## Overview

Load this reference when working on:

- Character or NPC animations (idle, walk, attack, emotes)
- Particle effects (fire, smoke, sparkles, magic, weather)
- Beams and trails (lasers, sword swings, magic projectiles)
- TweenService-driven visual feedback (hit flashes, pulses, transitions)
- Lighting and post-processing (mood, atmosphere, glow)
- Sound design and positional audio
- Camera effects (shake, zoom, cutscenes)
- General visual polish and juice

---

## Character Animation

### Animator Service on Humanoid

Every `Humanoid` has (or should have) an `Animator` child. The `Animator` is the engine that plays, blends, and prioritizes animation tracks on a character rig.

```luau
local character = player.Character or player.CharacterAdded:Wait()
local humanoid = character:WaitForChild("Humanoid")
local animator = humanoid:FindFirstChildOfClass("Animator")
    or humanoid:WaitForChild("Animator")
```

### Loading and Playing Animations

```luau
-- 1. Create an Animation instance with the asset ID
local slashAnim = Instance.new("Animation")
slashAnim.AnimationId = "rbxassetid://123456789"

-- 2. Load it through the Animator (returns an AnimationTrack)
local slashTrack = animator:LoadAnimation(slashAnim)

-- 3. Play / Stop
slashTrack:Play()
-- Optional fade time and weight
slashTrack:Play(0.2)          -- 0.2s fade-in
slashTrack:Stop(0.3)          -- 0.3s fade-out

-- 4. Adjust speed at runtime
slashTrack:AdjustSpeed(1.5)   -- 1.5x playback
slashTrack:AdjustWeight(0.8)  -- 80% blend weight
```

### Animation Priorities

Priorities determine which animation wins when multiple tracks affect the same joints. Higher priority overrides lower.

| Priority                              | Use Case                           |
| ------------------------------------- | ---------------------------------- |
| `Enum.AnimationPriority.Idle`         | Breathing, idle sway               |
| `Enum.AnimationPriority.Movement`     | Walk, run, jump, fall              |
| `Enum.AnimationPriority.Action`       | Attack, interact, emote            |
| `Enum.AnimationPriority.Action2`      | Higher-priority actions            |
| `Enum.AnimationPriority.Action3`      | Even higher-priority actions       |
| `Enum.AnimationPriority.Action4`      | Highest action tier                |
| `Enum.AnimationPriority.Core`         | Internal Roblox (avoid overriding) |

```luau
slashTrack.Priority = Enum.AnimationPriority.Action
```

### MarkerReachedSignal

Animation events let you fire logic at exact frames inside an animation (set markers in the Animation Editor).

```luau
slashTrack:GetMarkerReachedSignal("HitFrame"):Connect(function(paramValue: string)
    -- Spawn hitbox, play sound, emit particles, etc.
    print("Hit frame reached!", paramValue)
end)
```

### Blending Between Animations

Roblox automatically blends overlapping tracks based on priority and weight. To cross-fade manually:

```luau
local walkTrack = animator:LoadAnimation(walkAnim)
local runTrack  = animator:LoadAnimation(runAnim)

walkTrack:Play(0.2)

-- Later, cross-fade to run
walkTrack:Stop(0.3)
runTrack:Play(0.3)
```

For partial-body layering (e.g., upper body attack while legs run), set different priorities and ensure the lower-priority animation only drives lower body joints.

---

## AnimationController

Use `AnimationController` for anything that is NOT a `Humanoid` -- props, doors, creatures with custom rigs, cutscene actors, etc.

```luau
local model = workspace.DragonNPC
local animController = Instance.new("AnimationController")
animController.Parent = model

local flyAnim = Instance.new("Animation")
flyAnim.AnimationId = "rbxassetid://987654321"

local flyTrack = animController:LoadAnimation(flyAnim)
flyTrack.Looped = true
flyTrack:Play()
```

### Custom Rigs

- The model needs `Motor6D` joints connecting its parts, just like a character rig.
- Root part should be the `PrimaryPart` of the model.
- Animations are authored in the Animation Editor against this rig, then exported.

### Attaching to Models

```luau
-- Typical setup for an animated NPC without Humanoid
local npc = Instance.new("Model")
npc.Name = "CrystalGolem"

local rootPart = Instance.new("Part")
rootPart.Name = "HumanoidRootPart" -- convention for animation rigs
rootPart.Anchored = false
rootPart.Parent = npc
npc.PrimaryPart = rootPart

local animController = Instance.new("AnimationController")
animController.Parent = npc

-- Add Motor6D joints, mesh parts, then load animations
```

---

## Particle Effects

### ParticleEmitter Core Properties

| Property        | Type              | Description                                        |
| --------------- | ----------------- | -------------------------------------------------- |
| `Rate`          | `number`          | Particles emitted per second (0 = manual Emit())   |
| `Lifetime`      | `NumberRange`     | How long each particle lives (seconds)             |
| `Speed`         | `NumberRange`     | Initial velocity (studs/second)                    |
| `SpreadAngle`   | `Vector2`         | Cone spread in X and Y (degrees)                   |
| `Size`          | `NumberSequence`  | Size over particle lifetime                        |
| `Color`         | `ColorSequence`   | Color over particle lifetime                       |
| `Transparency`  | `NumberSequence`  | Transparency over particle lifetime                |
| `Texture`       | `string`          | Decal/image asset ID for particle appearance       |
| `RotSpeed`      | `NumberRange`     | Rotation speed (degrees/second)                    |
| `Acceleration`  | `Vector3`         | Constant force (gravity = `Vector3.new(0,-10,0)`)  |
| `Drag`          | `number`          | Air resistance (0 = none, higher = more drag)      |
| `LightEmission` | `number`          | 0-1, additive blending (1 = fully additive/glowy)  |
| `LightInfluence`| `number`          | 0-1, how much scene lighting affects particles     |
| `ZOffset`       | `number`          | Render order offset toward/away from camera        |
| `Orientation`   | `Enum.ParticleOrientation` | FacingCamera, VelocityParallel, etc.      |

### NumberSequence and ColorSequence

```luau
-- Size: start at 1, peak at 2 at midlife, shrink to 0
local sizeSeq = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 1),
    NumberSequenceKeypoint.new(0.5, 2),
    NumberSequenceKeypoint.new(1, 0),
})

-- Color: orange to red
local colorSeq = ColorSequence.new({
    ColorSequenceKeypoint.new(0, Color3.fromRGB(255, 170, 0)),
    ColorSequenceKeypoint.new(1, Color3.fromRGB(200, 30, 0)),
})

-- Transparency: fade in then fade out
local transSeq = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 1),
    NumberSequenceKeypoint.new(0.1, 0),
    NumberSequenceKeypoint.new(0.8, 0),
    NumberSequenceKeypoint.new(1, 1),
})
```

### Common Effect Recipes

#### Fire

```luau
local fire = Instance.new("ParticleEmitter")
fire.Rate = 80
fire.Lifetime = NumberRange.new(0.4, 0.8)
fire.Speed = NumberRange.new(3, 6)
fire.SpreadAngle = Vector2.new(15, 15)
fire.Size = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0.5),
    NumberSequenceKeypoint.new(0.3, 1.5),
    NumberSequenceKeypoint.new(1, 0),
})
fire.Color = ColorSequence.new({
    ColorSequenceKeypoint.new(0, Color3.fromRGB(255, 220, 50)),
    ColorSequenceKeypoint.new(0.4, Color3.fromRGB(255, 100, 0)),
    ColorSequenceKeypoint.new(1, Color3.fromRGB(100, 20, 0)),
})
fire.Transparency = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0.3),
    NumberSequenceKeypoint.new(1, 1),
})
fire.LightEmission = 1
fire.Acceleration = Vector3.new(0, 4, 0)
fire.Texture = "rbxasset://textures/particles/fire_main.dds"
fire.Parent = somePart
```

#### Smoke

```luau
local smoke = Instance.new("ParticleEmitter")
smoke.Rate = 30
smoke.Lifetime = NumberRange.new(2, 4)
smoke.Speed = NumberRange.new(1, 3)
smoke.SpreadAngle = Vector2.new(30, 30)
smoke.Size = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 1),
    NumberSequenceKeypoint.new(1, 5),
})
smoke.Color = ColorSequence.new(Color3.fromRGB(120, 120, 120))
smoke.Transparency = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0.5),
    NumberSequenceKeypoint.new(1, 1),
})
smoke.RotSpeed = NumberRange.new(-30, 30)
smoke.Acceleration = Vector3.new(0, 2, 0)
smoke.LightInfluence = 1
smoke.Parent = somePart
```

#### Sparkles / Magic Particles

```luau
local sparkle = Instance.new("ParticleEmitter")
sparkle.Rate = 40
sparkle.Lifetime = NumberRange.new(0.5, 1.2)
sparkle.Speed = NumberRange.new(2, 5)
sparkle.SpreadAngle = Vector2.new(180, 180)
sparkle.Size = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0.3),
    NumberSequenceKeypoint.new(0.5, 0.6),
    NumberSequenceKeypoint.new(1, 0),
})
sparkle.Color = ColorSequence.new({
    ColorSequenceKeypoint.new(0, Color3.fromRGB(200, 200, 255)),
    ColorSequenceKeypoint.new(1, Color3.fromRGB(100, 100, 255)),
})
sparkle.LightEmission = 1
sparkle.Texture = "rbxasset://textures/particles/sparkles_main.dds"
sparkle.Parent = somePart
```

#### Rain

```luau
local rain = Instance.new("ParticleEmitter")
rain.Rate = 300
rain.Lifetime = NumberRange.new(0.8, 1.2)
rain.Speed = NumberRange.new(40, 60)
rain.SpreadAngle = Vector2.new(5, 5)
rain.Size = NumberSequence.new(0.05)
rain.Color = ColorSequence.new(Color3.fromRGB(180, 200, 220))
rain.Transparency = NumberSequence.new(0.4)
rain.Acceleration = Vector3.new(0, -80, 0)
rain.Drag = 0
rain.Orientation = Enum.ParticleOrientation.VelocityParallel
rain.Parent = largeCoverPart -- position above the play area
```

#### Snow

```luau
local snow = Instance.new("ParticleEmitter")
snow.Rate = 100
snow.Lifetime = NumberRange.new(4, 7)
snow.Speed = NumberRange.new(1, 3)
snow.SpreadAngle = Vector2.new(60, 60)
snow.Size = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0.1),
    NumberSequenceKeypoint.new(1, 0.15),
})
snow.Color = ColorSequence.new(Color3.new(1, 1, 1))
snow.Transparency = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0),
    NumberSequenceKeypoint.new(0.8, 0),
    NumberSequenceKeypoint.new(1, 1),
})
snow.Acceleration = Vector3.new(0, -2, 0)
snow.RotSpeed = NumberRange.new(-60, 60)
snow.Drag = 3
snow.Parent = largeCoverPart
```

#### Magic Aura (orbiting particles)

```luau
local aura = Instance.new("ParticleEmitter")
aura.Rate = 25
aura.Lifetime = NumberRange.new(1, 2)
aura.Speed = NumberRange.new(0.5, 1.5)
aura.SpreadAngle = Vector2.new(180, 180)
aura.Size = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0),
    NumberSequenceKeypoint.new(0.3, 0.8),
    NumberSequenceKeypoint.new(1, 0),
})
aura.Color = ColorSequence.new({
    ColorSequenceKeypoint.new(0, Color3.fromRGB(100, 0, 255)),
    ColorSequenceKeypoint.new(1, Color3.fromRGB(200, 50, 255)),
})
aura.Transparency = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 1),
    NumberSequenceKeypoint.new(0.2, 0.2),
    NumberSequenceKeypoint.new(1, 1),
})
aura.LightEmission = 1
aura.RotSpeed = NumberRange.new(-90, 90)
aura.Drag = 5
aura.Parent = character.HumanoidRootPart
```

---

## Beam and Trail

### Beam

A `Beam` renders a textured ribbon between two `Attachment` instances. Perfect for lasers, lightning, tethers, and energy connections.

```luau
-- Setup: two parts with attachments
local att0 = Instance.new("Attachment")
att0.Parent = partA

local att1 = Instance.new("Attachment")
att1.Parent = partB

local beam = Instance.new("Beam")
beam.Attachment0 = att0
beam.Attachment1 = att1
beam.Width0 = 0.5
beam.Width1 = 0.5
beam.Color = ColorSequence.new(Color3.fromRGB(0, 150, 255))
beam.Transparency = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0),
    NumberSequenceKeypoint.new(1, 0.5),
})
beam.LightEmission = 1
beam.FaceCamera = true
beam.Segments = 20         -- more segments = smoother curves
beam.CurveSize0 = 2       -- bend near Attachment0
beam.CurveSize1 = -2      -- bend near Attachment1
beam.TextureLength = 1
beam.TextureSpeed = 1      -- scrolling texture
beam.Texture = "rbxassetid://123456789"
beam.Parent = partA
```

### Key Beam Properties

| Property         | Description                                              |
| ---------------- | -------------------------------------------------------- |
| `Attachment0/1`  | Start and end points                                     |
| `Width0/1`       | Width at each attachment (studs)                         |
| `Color`          | `ColorSequence` along the beam length                    |
| `Transparency`   | `NumberSequence` along the beam length                   |
| `CurveSize0/1`   | Bezier curve magnitude at each end                       |
| `Segments`       | Number of straight segments (more = smoother curves)     |
| `FaceCamera`     | Always faces the camera for billboard effect             |
| `TextureSpeed`   | Scrolls the texture along the beam                       |
| `LightEmission`  | Additive blending for glow                               |

### Trail

A `Trail` renders a ribbon behind a moving part. Requires two `Attachment` instances on the same part (defining the trail's width axis).

```luau
local part = workspace.Sword.Blade

local att0 = Instance.new("Attachment")
att0.Position = Vector3.new(0, 0, -2)  -- base of blade
att0.Parent = part

local att1 = Instance.new("Attachment")
att1.Position = Vector3.new(0, 0, 2)   -- tip of blade
att1.Parent = part

local trail = Instance.new("Trail")
trail.Attachment0 = att0
trail.Attachment1 = att1
trail.Lifetime = 0.3                   -- how long segments persist
trail.MinLength = 0.05                 -- minimum distance before new segment
trail.FaceCamera = true
trail.Color = ColorSequence.new({
    ColorSequenceKeypoint.new(0, Color3.fromRGB(255, 255, 255)),
    ColorSequenceKeypoint.new(1, Color3.fromRGB(100, 100, 255)),
})
trail.Transparency = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0),
    NumberSequenceKeypoint.new(1, 1),
})
trail.LightEmission = 0.8
trail.WidthScale = NumberSequence.new(1)
trail.Parent = part
```

### Common Uses

- **Laser beams**: `Beam` between gun barrel attachment and hit-point attachment.
- **Sword trails**: `Trail` on blade with short `Lifetime` (0.2-0.4s).
- **Magic effects**: `Beam` with high `CurveSize` values and scrolling texture for arcane tethers.
- **Lightning**: `Beam` with many `Segments`, rapidly randomizing `CurveSize0/1` each frame.

---

## TweenService for VFX

`TweenService` interpolates any numeric or color property over time. It is the backbone of procedural visual feedback.

### TweenInfo

```luau
local TweenService = game:GetService("TweenService")

local info = TweenInfo.new(
    0.5,                             -- Duration (seconds)
    Enum.EasingStyle.Quad,           -- Easing style
    Enum.EasingDirection.Out,        -- Easing direction
    0,                               -- RepeatCount (0 = no repeat, -1 = infinite)
    false,                           -- Reverses (plays backward after forward)
    0                                -- DelayTime (seconds before starting)
)
```

### Common Easing Styles

| Style       | Feel                                    |
| ----------- | --------------------------------------- |
| `Linear`    | Constant speed, mechanical              |
| `Quad`      | Gentle acceleration/deceleration        |
| `Cubic`     | Stronger ease                           |
| `Quart`     | Even stronger                           |
| `Sine`      | Smooth, organic                         |
| `Back`      | Overshoots then settles                 |
| `Bounce`    | Bounces at the end                      |
| `Elastic`   | Springy overshoot                       |
| `Exponential` | Very sharp acceleration              |

### Tweening Part Properties

```luau
-- Flash on hit: turn white then revert
local function flashPart(part: BasePart, originalColor: Color3)
    part.Color = Color3.new(1, 1, 1)  -- instant white
    local tweenBack = TweenService:Create(part, TweenInfo.new(0.3, Enum.EasingStyle.Quad), {
        Color = originalColor,
    })
    tweenBack:Play()
end
```

```luau
-- Pulse effect: scale up then back
local function pulse(part: BasePart)
    local originalSize = part.Size
    local tweenGrow = TweenService:Create(part, TweenInfo.new(0.15, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
        Size = originalSize * 1.3,
    })
    local tweenShrink = TweenService:Create(part, TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
        Size = originalSize,
    })
    tweenGrow:Play()
    tweenGrow.Completed:Connect(function()
        tweenShrink:Play()
    end)
end
```

```luau
-- Grow and fade out (explosion ring)
local function expandAndFade(part: BasePart)
    local tween = TweenService:Create(part, TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
        Size = part.Size * 5,
        Transparency = 1,
    })
    tween:Play()
    tween.Completed:Connect(function()
        part:Destroy()
    end)
end
```

```luau
-- Color transition (damage indicator)
local function colorTransition(part: BasePart, targetColor: Color3, duration: number)
    local tween = TweenService:Create(part, TweenInfo.new(duration, Enum.EasingStyle.Sine), {
        Color = targetColor,
    })
    tween:Play()
end
```

### Chaining Tweens

Use the `Completed` event to sequence tweens without coroutines:

```luau
local function chainedEffect(part: BasePart)
    local step1 = TweenService:Create(part, TweenInfo.new(0.2), { Transparency = 0.5 })
    local step2 = TweenService:Create(part, TweenInfo.new(0.3), { Size = part.Size * 2 })
    local step3 = TweenService:Create(part, TweenInfo.new(0.2), { Transparency = 1 })

    step1:Play()
    step1.Completed:Connect(function()
        step2:Play()
    end)
    step2.Completed:Connect(function()
        step3:Play()
    end)
    step3.Completed:Connect(function()
        part:Destroy()
    end)
end
```

---

## Lighting Effects

### Dynamic Lights

```luau
-- PointLight: omnidirectional, good for torches, explosions
local pointLight = Instance.new("PointLight")
pointLight.Brightness = 2
pointLight.Color = Color3.fromRGB(255, 180, 50)
pointLight.Range = 20
pointLight.Shadows = true
pointLight.Parent = torchPart

-- SpotLight: directional cone, good for flashlights, spotlights
local spotLight = Instance.new("SpotLight")
spotLight.Brightness = 3
spotLight.Color = Color3.new(1, 1, 1)
spotLight.Range = 40
spotLight.Angle = 30           -- cone half-angle in degrees
spotLight.Face = Enum.NormalId.Front
spotLight.Parent = flashlightPart

-- SurfaceLight: emits from a surface, good for screens, signs
local surfLight = Instance.new("SurfaceLight")
surfLight.Brightness = 1
surfLight.Color = Color3.fromRGB(0, 200, 255)
surfLight.Range = 10
surfLight.Face = Enum.NormalId.Front
surfLight.Parent = screenPart
```

### Post-Processing Effects

All post-processing objects go in `Lighting` or `Camera`.

#### Atmosphere

```luau
local atmo = Instance.new("Atmosphere")
atmo.Density = 0.3           -- 0-1, how thick the atmosphere is
atmo.Offset = 0.25           -- shifts haze up/down
atmo.Color = Color3.fromRGB(200, 210, 230)  -- scatter color
atmo.Decay = Color3.fromRGB(120, 140, 170)  -- far-away color
atmo.Glare = 0.2             -- sun glare intensity
atmo.Haze = 1.5              -- haze amount
atmo.Parent = game.Lighting
```

#### ColorCorrection

```luau
local cc = Instance.new("ColorCorrectionEffect")
cc.Brightness = 0.05         -- -1 to 1
cc.Contrast = 0.1            -- -1 to 1
cc.Saturation = 0.15         -- -1 to 1
cc.TintColor = Color3.new(1, 0.95, 0.9)  -- warm tint
cc.Parent = game.Lighting
```

#### Bloom

```luau
local bloom = Instance.new("BloomEffect")
bloom.Intensity = 0.8        -- glow strength
bloom.Size = 24              -- glow spread (pixels)
bloom.Threshold = 1.2        -- brightness threshold to bloom
bloom.Parent = game.Lighting
```

#### DepthOfField

```luau
local dof = Instance.new("DepthOfFieldEffect")
dof.FarIntensity = 0.3       -- blur intensity far from focus
dof.FocusDistance = 30        -- distance in studs to focus point
dof.InFocusRadius = 20       -- radius of sharp area
dof.NearIntensity = 0.2      -- blur intensity near camera
dof.Parent = game.Lighting
```

#### SunRays

```luau
local sunRays = Instance.new("SunRaysEffect")
sunRays.Intensity = 0.15     -- ray visibility
sunRays.Spread = 0.8         -- how far rays extend
sunRays.Parent = game.Lighting
```

### Setting Mood with Global Lighting

```luau
local lighting = game.Lighting

-- Daytime bright
lighting.ClockTime = 14
lighting.Brightness = 2
lighting.Ambient = Color3.fromRGB(140, 140, 140)
lighting.OutdoorAmbient = Color3.fromRGB(130, 130, 130)

-- Nighttime spooky
lighting.ClockTime = 0
lighting.Brightness = 0.5
lighting.Ambient = Color3.fromRGB(20, 20, 40)
lighting.OutdoorAmbient = Color3.fromRGB(10, 10, 30)
lighting.FogEnd = 200
lighting.FogColor = Color3.fromRGB(15, 15, 30)
```

---

## Sound Design

### Sound Objects

```luau
local sound = Instance.new("Sound")
sound.SoundId = "rbxassetid://111222333"
sound.Volume = 0.8            -- 0 to 10
sound.PlaybackSpeed = 1       -- 0.5 = half speed, 2 = double speed
sound.Looped = false
sound.RollOffMode = Enum.RollOffMode.InverseTapered
sound.RollOffMaxDistance = 100
sound.RollOffMinDistance = 10
sound.Parent = somePart       -- positional audio: parent to a Part
sound:Play()
```

### SoundService for Global/Ambient Audio

```luau
local SoundService = game:GetService("SoundService")

-- Ambient music (non-positional, parent to SoundService or a ScreenGui)
local bgm = Instance.new("Sound")
bgm.SoundId = "rbxassetid://444555666"
bgm.Volume = 0.3
bgm.Looped = true
bgm.Parent = SoundService
bgm:Play()
```

### Positional Audio

Parent a `Sound` to a `Part` in the workspace. The engine automatically applies 3D rolloff based on `RollOffMinDistance`, `RollOffMaxDistance`, and `RollOffMode`.

```luau
-- Waterfall ambient sound
local waterSound = Instance.new("Sound")
waterSound.SoundId = "rbxassetid://777888999"
waterSound.Volume = 1
waterSound.Looped = true
waterSound.RollOffMode = Enum.RollOffMode.InverseTapered
waterSound.RollOffMinDistance = 10
waterSound.RollOffMaxDistance = 80
waterSound.Parent = workspace.Waterfall.MainPart
waterSound:Play()
```

### SoundGroup for Volume Control

`SoundGroup` lets you control volume for categories of sounds (SFX, Music, Ambient) from one place, which is ideal for settings menus.

```luau
local sfxGroup = Instance.new("SoundGroup")
sfxGroup.Name = "SFX"
sfxGroup.Volume = 1
sfxGroup.Parent = SoundService

local musicGroup = Instance.new("SoundGroup")
musicGroup.Name = "Music"
musicGroup.Volume = 0.5
musicGroup.Parent = SoundService

-- Assign sounds to groups
hitSound.SoundGroup = sfxGroup
bgm.SoundGroup = musicGroup

-- Player adjusts SFX volume:
sfxGroup.Volume = 0.3  -- all SFX sounds update
```

### Triggering Sounds with Animation Events

```luau
-- Sync a footstep sound to walk animation markers
walkTrack:GetMarkerReachedSignal("Footstep"):Connect(function()
    local footstep = Instance.new("Sound")
    footstep.SoundId = "rbxassetid://112233445"
    footstep.Volume = 0.5
    footstep.PlaybackSpeed = 0.9 + math.random() * 0.2  -- slight variation
    footstep.Parent = character.HumanoidRootPart
    footstep:Play()
    footstep.Ended:Connect(function()
        footstep:Destroy()
    end)
end)
```

---

## Camera Effects

### Camera Shake

```luau
local camera = workspace.CurrentCamera
local RunService = game:GetService("RunService")

local function shakeCamera(intensity: number, duration: number)
    local elapsed = 0
    local originalCFrame = camera.CFrame
    local connection: RBXScriptConnection

    connection = RunService.RenderStepped:Connect(function(dt: number)
        elapsed += dt
        if elapsed >= duration then
            connection:Disconnect()
            -- Camera returns to normal since CameraType is usually
            -- "Custom" (player-controlled)
            return
        end

        local progress = 1 - (elapsed / duration)  -- decay over time
        local shakeX = (math.random() - 0.5) * 2 * intensity * progress
        local shakeY = (math.random() - 0.5) * 2 * intensity * progress
        local shakeZ = (math.random() - 0.5) * 2 * intensity * progress

        camera.CFrame = camera.CFrame * CFrame.new(shakeX, shakeY, shakeZ)
    end)
end

-- Usage: moderate shake for 0.3 seconds
shakeCamera(0.5, 0.3)
```

### Zoom Effect

```luau
local TweenService = game:GetService("TweenService")
local camera = workspace.CurrentCamera

local function zoomCamera(targetFOV: number, duration: number)
    local tween = TweenService:Create(camera, TweenInfo.new(duration, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
        FieldOfView = targetFOV,
    })
    tween:Play()
    return tween
end

-- Zoom in for dramatic moment
local zoomIn = zoomCamera(40, 0.5)
zoomIn.Completed:Connect(function()
    task.wait(1)
    zoomCamera(70, 0.8)  -- zoom back to normal
end)
```

### Focus / CFrame Lerp

```luau
local function focusOnPoint(targetCFrame: CFrame, duration: number)
    camera.CameraType = Enum.CameraType.Scriptable

    local startCFrame = camera.CFrame
    local elapsed = 0
    local connection: RBXScriptConnection

    connection = RunService.RenderStepped:Connect(function(dt: number)
        elapsed += dt
        local alpha = math.clamp(elapsed / duration, 0, 1)
        -- Smooth step for natural feel
        local smoothAlpha = alpha * alpha * (3 - 2 * alpha)
        camera.CFrame = startCFrame:Lerp(targetCFrame, smoothAlpha)

        if alpha >= 1 then
            connection:Disconnect()
        end
    end)
end
```

### Cutscene Waypoint System

```luau
type CutsceneWaypoint = {
    cframe: CFrame,
    duration: number,
    easingStyle: Enum.EasingStyle?,
    holdTime: number?,  -- pause at this point before moving on
}

local function playCutscene(waypoints: { CutsceneWaypoint })
    camera.CameraType = Enum.CameraType.Scriptable

    for i, waypoint in waypoints do
        local style = waypoint.easingStyle or Enum.EasingStyle.Quad
        local info = TweenInfo.new(waypoint.duration, style, Enum.EasingDirection.InOut)

        local tween = TweenService:Create(camera, info, {
            CFrame = waypoint.cframe,
        })
        tween:Play()
        tween.Completed:Wait()

        if waypoint.holdTime and waypoint.holdTime > 0 then
            task.wait(waypoint.holdTime)
        end
    end

    -- Return camera control to player
    camera.CameraType = Enum.CameraType.Custom
end

-- Usage
playCutscene({
    { cframe = CFrame.new(0, 50, 0) * CFrame.Angles(math.rad(-90), 0, 0), duration = 2, holdTime = 1 },
    { cframe = CFrame.new(20, 10, 20) * CFrame.lookAt(Vector3.new(20, 10, 20), Vector3.zero), duration = 3 },
    { cframe = camera.CFrame, duration = 1.5, easingStyle = Enum.EasingStyle.Sine },
})
```

---

## Best Practices

### Performance Budgets

- **Max ~200 particles per emitter** -- more than this and you risk frame drops, especially on mobile.
- **Limit total active emitters** -- aim for fewer than 20-30 active emitters visible at once in any scene.
- **Particle texture size** -- keep textures small (64x64 or 128x128 PNG). Avoid large or high-res particle textures.
- **Beams** -- keep `Segments` reasonable (10-30). Very high segment counts cost draw calls.
- **Tweens** -- hundreds of simultaneous tweens are fine; thousands may cause issues. Cancel/destroy tweens when no longer needed.
- **Sounds** -- limit simultaneous playing sounds to ~20-30. Destroy one-shot sounds after `Ended`.

### Disable Effects on Low-End Devices

```luau
local function getQualityLevel(): string
    local quality = UserSettings().GameSettings.SavedQualityLevel
    -- quality is Enum.SavedQualitySetting or an int 1-10
    if quality == Enum.SavedQualitySetting.Automatic then
        -- Use a heuristic: check current graphics quality
        local level = settings().Rendering.QualityLevel
        if level <= 3 then return "low"
        elseif level <= 6 then return "medium"
        else return "high" end
    end
    local numQuality = quality.Value
    if numQuality <= 3 then return "low"
    elseif numQuality <= 6 then return "medium"
    else return "high" end
end

local function applyQualitySettings()
    local level = getQualityLevel()
    if level == "low" then
        -- Disable post-processing
        for _, effect in game.Lighting:GetChildren() do
            if effect:IsA("PostEffect") then
                effect.Enabled = false
            end
        end
        -- Reduce particle rates
        -- Disable shadows on dynamic lights
    end
end
```

### Pool VFX Objects

Avoid creating and destroying particles every frame. Pre-create a pool and enable/disable or reposition them.

```luau
local VFXPool = {}
VFXPool.__index = VFXPool

function VFXPool.new(template: Instance, poolSize: number): typeof(setmetatable({}, VFXPool))
    local self = setmetatable({}, VFXPool)
    self._pool = table.create(poolSize)
    self._available = table.create(poolSize)

    for i = 1, poolSize do
        local clone = template:Clone()
        clone.Parent = workspace.VFXFolder
        -- Disable all emitters
        for _, emitter in clone:GetDescendants() do
            if emitter:IsA("ParticleEmitter") then
                emitter.Enabled = false
            end
        end
        self._pool[i] = clone
        self._available[i] = clone
    end

    return self
end

function VFXPool:get(): Instance?
    local obj = table.remove(self._available)
    return obj
end

function VFXPool:release(obj: Instance)
    -- Reset position, disable emitters
    for _, emitter in obj:GetDescendants() do
        if emitter:IsA("ParticleEmitter") then
            emitter.Enabled = false
        end
    end
    table.insert(self._available, obj)
end
```

### Sync Sound with Visuals

- Use `MarkerReachedSignal` to trigger sounds at exact animation frames.
- Play impact sounds at the moment of collision, not when the swing starts.
- Match `PlaybackSpeed` to animation speed adjustments.
- Use `task.delay` or tween `Completed` events for sequenced audio.

---

## Anti-Patterns

### Unlimited Particles

```luau
-- BAD: unbounded particle creation with no cleanup
RunService.Heartbeat:Connect(function()
    local emitter = Instance.new("ParticleEmitter")
    emitter.Rate = 500  -- extremely high rate
    emitter.Parent = somePart
    -- never destroyed, accumulates forever
end)

-- GOOD: reuse a single emitter, burst when needed
local emitter = Instance.new("ParticleEmitter")
emitter.Rate = 0  -- manual emission only
emitter.Parent = somePart

local function burstParticles(count: number)
    emitter:Emit(count)
end
```

### Unoptimized Particle Textures

```luau
-- BAD: 1024x1024 high-res texture for tiny particles
emitter.Texture = "rbxassetid://huge_4k_texture"

-- GOOD: 64x64 or 128x128 simple shape on transparent background
emitter.Texture = "rbxassetid://small_optimized_circle"
-- Use LightEmission = 1 with simple shapes for clean glow effects
```

### Synchronous Animation Loading Blocking Gameplay

```luau
-- BAD: loading animations in a hot path synchronously
local function onAttack()
    local anim = Instance.new("Animation")
    anim.AnimationId = "rbxassetid://123456789"
    local track = animator:LoadAnimation(anim)  -- may yield on first load
    track:Play()
end

-- GOOD: preload animations at character spawn
local attackAnim = Instance.new("Animation")
attackAnim.AnimationId = "rbxassetid://123456789"
local attackTrack: AnimationTrack  -- forward declare

local function onCharacterAdded(character: Model)
    local animator = character:WaitForChild("Humanoid"):WaitForChild("Animator")
    attackTrack = animator:LoadAnimation(attackAnim)
    attackTrack.Priority = Enum.AnimationPriority.Action
end

local function onAttack()
    if attackTrack then
        attackTrack:Play()
    end
end
```

### Other Anti-Patterns to Avoid

- **Tweening properties every frame via RenderStepped instead of using TweenService** -- TweenService is optimized internally and handles cleanup.
- **Not disconnecting camera shake connections** -- leads to permanent jitter.
- **Setting `Camera.CameraType` to `Scriptable` and forgetting to restore it** -- player loses control.
- **Playing sounds without ever destroying them** -- memory leak. Always clean up one-shot sounds via `Ended`.
- **Creating hundreds of PointLights with shadows enabled** -- massive performance hit. Use `Shadows = false` for most dynamic lights.

---

## Complete Hit Effect System

A production-ready system combining white flash, particle burst, sound stinger, and camera shake. Designed for client-side use (LocalScript or module required from a LocalScript).

```luau
--[[
    HitEffectSystem
    Combines visual and audio feedback for combat hit registration.
    Run on the CLIENT only (camera shake and local VFX).
]]

local TweenService = game:GetService("TweenService")
local RunService = game:GetService("RunService")

local HitEffectSystem = {}

-- Configuration
local DEFAULT_CONFIG = {
    -- Flash
    flashColor = Color3.new(1, 1, 1),
    flashDuration = 0.15,
    flashRevertDuration = 0.25,

    -- Particles
    particleBurstCount = 20,
    particleLifetime = NumberRange.new(0.2, 0.5),
    particleSpeed = NumberRange.new(8, 15),
    particleSize = NumberSequence.new({
        NumberSequenceKeypoint.new(0, 0.5),
        NumberSequenceKeypoint.new(1, 0),
    }),
    particleColor = ColorSequence.new({
        ColorSequenceKeypoint.new(0, Color3.new(1, 1, 1)),
        ColorSequenceKeypoint.new(1, Color3.fromRGB(255, 200, 50)),
    }),
    particleTransparency = NumberSequence.new({
        NumberSequenceKeypoint.new(0, 0),
        NumberSequenceKeypoint.new(0.7, 0.3),
        NumberSequenceKeypoint.new(1, 1),
    }),

    -- Sound
    hitSoundId = "rbxassetid://123456789",  -- replace with your asset
    hitSoundVolume = 0.8,
    hitSoundPitchVariation = 0.15,           -- random pitch +/- this amount

    -- Camera shake
    shakeIntensity = 0.4,
    shakeDuration = 0.2,
}

-- Pre-create a reusable particle emitter template
local function createHitEmitterTemplate(config: typeof(DEFAULT_CONFIG)): ParticleEmitter
    local emitter = Instance.new("ParticleEmitter")
    emitter.Name = "HitBurst"
    emitter.Rate = 0                             -- manual emission only
    emitter.Lifetime = config.particleLifetime
    emitter.Speed = config.particleSpeed
    emitter.SpreadAngle = Vector2.new(180, 180)  -- omnidirectional burst
    emitter.Size = config.particleSize
    emitter.Color = config.particleColor
    emitter.Transparency = config.particleTransparency
    emitter.LightEmission = 1
    emitter.Drag = 5
    emitter.RotSpeed = NumberRange.new(-180, 180)
    return emitter
end

-- Emitter cache: one emitter per part (lazily created)
local emitterCache: { [BasePart]: ParticleEmitter } = {}
local emitterTemplate: ParticleEmitter? = nil

local function getOrCreateEmitter(part: BasePart, config: typeof(DEFAULT_CONFIG)): ParticleEmitter
    if emitterCache[part] then
        return emitterCache[part]
    end

    if not emitterTemplate then
        emitterTemplate = createHitEmitterTemplate(config)
    end

    local emitter = emitterTemplate:Clone()
    emitter.Parent = part
    emitterCache[part] = emitter

    -- Clean up if part is destroyed
    part.Destroying:Connect(function()
        emitterCache[part] = nil
    end)

    return emitter
end

--[[
    Flash the target part white and tween back to original color.
]]
local function flashPart(part: BasePart, config: typeof(DEFAULT_CONFIG))
    local originalColor = part.Color
    part.Color = config.flashColor

    local tweenBack = TweenService:Create(
        part,
        TweenInfo.new(config.flashRevertDuration, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        { Color = originalColor }
    )
    tweenBack:Play()
end

--[[
    Emit a burst of particles from the hit location.
]]
local function emitParticleBurst(part: BasePart, config: typeof(DEFAULT_CONFIG))
    local emitter = getOrCreateEmitter(part, config)
    emitter:Emit(config.particleBurstCount)
end

--[[
    Play a one-shot hit sound with slight pitch variation.
]]
local function playHitSound(part: BasePart, config: typeof(DEFAULT_CONFIG))
    local sound = Instance.new("Sound")
    sound.SoundId = config.hitSoundId
    sound.Volume = config.hitSoundVolume
    sound.PlaybackSpeed = 1 + (math.random() - 0.5) * 2 * config.hitSoundPitchVariation
    sound.RollOffMaxDistance = 80
    sound.RollOffMinDistance = 5
    sound.Parent = part
    sound:Play()

    sound.Ended:Connect(function()
        sound:Destroy()
    end)
end

--[[
    Apply a short screen shake that decays over time.
]]
local function shakeCamera(config: typeof(DEFAULT_CONFIG))
    local camera = workspace.CurrentCamera
    if not camera then return end

    local elapsed = 0
    local intensity = config.shakeIntensity
    local duration = config.shakeDuration
    local connection: RBXScriptConnection

    connection = RunService.RenderStepped:Connect(function(dt: number)
        elapsed += dt
        if elapsed >= duration then
            connection:Disconnect()
            return
        end

        local decay = 1 - (elapsed / duration)
        local offsetX = (math.random() - 0.5) * 2 * intensity * decay
        local offsetY = (math.random() - 0.5) * 2 * intensity * decay

        camera.CFrame = camera.CFrame * CFrame.new(offsetX, offsetY, 0)
    end)
end

--[[
    Main entry point: trigger the full hit effect on a target part.

    @param targetPart  The BasePart that was hit (e.g., a character limb or NPC body).
    @param overrides   Optional table to override any DEFAULT_CONFIG values.
]]
function HitEffectSystem.play(targetPart: BasePart, overrides: { [string]: any }?)
    -- Merge config with overrides
    local config = table.clone(DEFAULT_CONFIG)
    if overrides then
        for key, value in overrides do
            (config :: any)[key] = value
        end
    end

    -- Fire all effects simultaneously
    flashPart(targetPart, config)
    emitParticleBurst(targetPart, config)
    playHitSound(targetPart, config)
    shakeCamera(config)
end

--[[
    Clean up cached emitters (call when resetting scene or on player leave).
]]
function HitEffectSystem.cleanup()
    for part, emitter in emitterCache do
        emitter:Destroy()
    end
    table.clear(emitterCache)
end

return HitEffectSystem

--[[
    USAGE EXAMPLE (in a LocalScript):

    local HitEffectSystem = require(script.Parent.HitEffectSystem)

    -- When a hit is confirmed (e.g., via RemoteEvent from server):
    hitRemote.OnClientEvent:Connect(function(targetPart: BasePart)
        HitEffectSystem.play(targetPart)
    end)

    -- Custom overrides for a critical hit:
    hitRemote.OnClientEvent:Connect(function(targetPart: BasePart, isCritical: boolean)
        if isCritical then
            HitEffectSystem.play(targetPart, {
                flashColor = Color3.fromRGB(255, 50, 50),
                particleBurstCount = 40,
                shakeIntensity = 0.8,
                shakeDuration = 0.4,
                hitSoundId = "rbxassetid://critical_hit_sound_id",
            })
        else
            HitEffectSystem.play(targetPart)
        end
    end)
]]
```
