---
name: roblox-audio
description: >
  Sound design implementation for Roblox. SoundService, SoundGroups, spatial audio,
  music systems, SFX patterns, volume management, and audio triggers.
  Use when implementing any sound or music system.
last_reviewed: 2026-05-27
---

# Roblox Audio & Sound

Use this skill when implementing music, sound effects, ambient audio, or any audio system.

## SoundService Architecture

```
SoundService
├── SoundGroups
│   ├── Master (controls global volume)
│   ├── Music (background music)
│   ├── SFX (sound effects)
│   ├── UI (button clicks, notifications)
│   └── Ambient (environment loops)
└── Properties
    ├── AmbientReverb = Enum.ReverbType
    ├── DistanceFactor = 3.33 (studs per meter)
    └── RespectFilteringEnabled = true
```

### SoundGroup Setup

```luau
local SoundService = game:GetService("SoundService")

local function createSoundGroups()
    local master = Instance.new("SoundGroup")
    master.Name = "Master"
    master.Volume = 1
    master.Parent = SoundService

    local groups = {"Music", "SFX", "UI", "Ambient"}
    for _, name in groups do
        local group = Instance.new("SoundGroup")
        group.Name = name
        group.Volume = 1
        group.Parent = master -- nested under Master for global control
    end
end
```

## Sound Placement

### Where to put Sounds

| Sound Type | Parent | Why |
|-----------|--------|-----|
| 3D positional (footsteps, explosions) | The Part that emits it | Spatial audio works automatically |
| 2D global (music, UI) | SoundService or PlayerGui | No spatial falloff |
| Character sounds | HumanoidRootPart | Follows the character |
| Ambient loops | Part in the zone | Fades with distance |

### 3D Spatial Sound

```luau
local function playSpatialSound(parent: BasePart, soundId: string, volume: number?)
    local sound = Instance.new("Sound")
    sound.SoundId = soundId
    sound.Volume = volume or 0.5
    sound.RollOffMode = Enum.RollOffMode.InverseTapered
    sound.RollOffMinDistance = 10  -- full volume within 10 studs
    sound.RollOffMaxDistance = 100 -- silent beyond 100 studs
    sound.SoundGroup = SoundService.Master.SFX
    sound.Parent = parent
    sound:Play()

    -- Auto-cleanup after playing
    sound.Ended:Once(function()
        sound:Destroy()
    end)
end
```

### 2D Sound (Music/UI)

```luau
local function playMusic(soundId: string, fadeIn: number?)
    local sound = Instance.new("Sound")
    sound.SoundId = soundId
    sound.Volume = 0
    sound.Looped = true
    sound.SoundGroup = SoundService.Master.Music
    sound.Parent = SoundService
    sound:Play()

    -- Fade in
    local tween = TweenService:Create(sound, TweenInfo.new(fadeIn or 2), {Volume = 0.5})
    tween:Play()

    return sound
end
```

## Music System

### Crossfade Between Tracks

```luau
local currentMusic: Sound? = nil

local function crossfadeTo(newSoundId: string, duration: number?)
    local fadeDuration = (duration or 2) / 2

    -- Fade out current
    if currentMusic then
        local old = currentMusic
        local fadeOut = TweenService:Create(old, TweenInfo.new(fadeDuration), {Volume = 0})
        fadeOut:Play()
        fadeOut.Completed:Once(function()
            old:Destroy()
        end)
    end

    -- Fade in new
    local newSound = Instance.new("Sound")
    newSound.SoundId = newSoundId
    newSound.Volume = 0
    newSound.Looped = true
    newSound.SoundGroup = SoundService.Master.Music
    newSound.Parent = SoundService
    newSound:Play()

    local fadeIn = TweenService:Create(newSound, TweenInfo.new(fadeDuration), {Volume = 0.5})
    fadeIn:Play()

    currentMusic = newSound
end
```

### Zone-Based Music

```luau
-- Server: detect zone, tell client what to play
local ZONE_MUSIC = {
    Lobby = "rbxassetid://111111",
    Arena = "rbxassetid://222222",
    Boss = "rbxassetid://333333",
}

-- Client: listen for zone changes
local MusicRemote = ReplicatedStorage.Remotes.ZoneMusic
MusicRemote.OnClientEvent:Connect(function(zoneName: string)
    local soundId = ZONE_MUSIC[zoneName]
    if soundId then
        crossfadeTo(soundId)
    end
end)
```

## SFX Patterns

### Preloading

```luau
local ContentProvider = game:GetService("ContentProvider")

local SFX_IDS = {
    hit = "rbxassetid://123456",
    jump = "rbxassetid://234567",
    coin = "rbxassetid://345678",
    explosion = "rbxassetid://456789",
}

-- Preload all SFX on client start
local assets = {}
for _, id in SFX_IDS do
    table.insert(assets, Instance.new("Sound", nil))
    assets[#assets].SoundId = id
end
ContentProvider:PreloadAsync(assets)
```

### Randomized Pitch (prevents repetitive feel)

```luau
local function playSFX(parent: BasePart, soundId: string)
    local sound = Instance.new("Sound")
    sound.SoundId = soundId
    sound.Volume = 0.6
    sound.PlaybackSpeed = 0.9 + math.random() * 0.2 -- 0.9 to 1.1
    sound.SoundGroup = SoundService.Master.SFX
    sound.Parent = parent
    sound:Play()
    sound.Ended:Once(function() sound:Destroy() end)
end
```

### Footstep System (material-based)

```luau
local FOOTSTEP_SOUNDS = {
    [Enum.Material.Grass] = "rbxassetid://grass_step",
    [Enum.Material.Concrete] = "rbxassetid://concrete_step",
    [Enum.Material.Wood] = "rbxassetid://wood_step",
    [Enum.Material.Metal] = "rbxassetid://metal_step",
}

local function getGroundMaterial(character: Model): Enum.Material?
    local root = character:FindFirstChild("HumanoidRootPart")
    if not root then return nil end

    local params = RaycastParams.new()
    params.FilterDescendantsInstances = {character}
    local result = workspace:Raycast(root.Position, Vector3.new(0, -4, 0), params)
    return result and result.Material
end
```

## Volume Settings (Player Preferences)

```luau
-- Client: save/load volume preferences
local function setVolume(groupName: string, volume: number)
    local group = SoundService.Master:FindFirstChild(groupName)
    if group then
        group.Volume = math.clamp(volume, 0, 1)
    end
end

-- Persist with PlayerDataStore or local storage
-- Typical settings UI: Master, Music, SFX sliders (0-100%)
```

## Ambient Audio

### Layered Ambience

```luau
-- Multiple ambient layers that blend based on location
local function createAmbientZone(part: BasePart, soundId: string, volume: number)
    local sound = Instance.new("Sound")
    sound.SoundId = soundId
    sound.Volume = volume
    sound.Looped = true
    sound.RollOffMode = Enum.RollOffMode.InverseTapered
    sound.RollOffMinDistance = 20
    sound.RollOffMaxDistance = 80
    sound.SoundGroup = SoundService.Master.Ambient
    sound.Parent = part
    sound:Play()
    return sound
end

-- Example: forest zone has wind + birds + creek
createAmbientZone(workspace.Forest.WindEmitter, "rbxassetid://wind", 0.3)
createAmbientZone(workspace.Forest.BirdEmitter, "rbxassetid://birds", 0.2)
createAmbientZone(workspace.Forest.CreekEmitter, "rbxassetid://creek", 0.4)
```

## Common Mistakes

- **Playing sounds on the server**: Sounds should play on the client for responsiveness. Server only tells clients WHAT to play.
- **No SoundGroup hierarchy**: Without groups, players can't control music vs SFX volume independently.
- **Forgetting RollOff settings**: Default RollOff is often too aggressive. Set MinDistance and MaxDistance explicitly.
- **Not preloading**: First play of a sound has a loading delay. Preload critical SFX on join.
- **Stacking sounds**: Playing the same sound rapidly creates ear-splitting overlap. Use `sound.Playing` check or debounce.
- **No cleanup**: Sounds parented to destroyed parts get garbage collected, but sounds in SoundService don't. Destroy them manually.
- **Volume > 1**: Sounds clip and distort. Keep Volume ≤ 1, use SoundGroup for amplification.
- **Looped one-shots**: Forgetting `Looped = false` on SFX means they play forever.
