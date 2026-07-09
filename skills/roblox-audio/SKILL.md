---
name: roblox-audio
description: "Use when implementing Roblox audio playback, spatial sound, music, sound effects, SoundGroups, or dynamic audio effects."
last_reviewed: 2026-05-27
sources:
  - https://create.roblox.com/docs/audio/objects
  - https://create.roblox.com/docs/audio/effects
  - https://create.roblox.com/docs/sound/groups
  - https://create.roblox.com/docs/sound/dynamic-effects
---

## When to Load

Load when implementing audio playback, spatial/3D sound, background music, sound effects, audio mixing (SoundGroups), or dynamic effects. Covers both legacy Sound objects and the newer modular AudioPlayer/Wire system.

## Quick Reference

**Two Systems**: Legacy (`Sound`/`SoundGroup`/`SoundEffect`) — simpler. New modular (`AudioPlayer`/`AudioEmitter`/`Wire`/`AudioDeviceOutput`) — preferred for new projects, required for voice chat.

**Sound Placement**: BasePart child → volumetric. Attachment/MeshPart → point source. SoundService/Workspace → global (BGM/UI).

**Legacy Setup**:
```luau
local s = Instance.new("Sound")
s.SoundId = "rbxassetid://ID"; s.Looped = true; s.Volume = 0.25
s.RollOffMode = Enum.RollOffMode.InverseTapered
s.RollOffMinDistance = 10; s.RollOffMaxDistance = 100
s.Parent = SoundService; s:Play()
```

**SoundGroups** (mixer): Nest `SoundGroup` under Master for player-adjustable Music vs SFX volume. `bgMusic.SoundGroup = musicGroup`. Effects (`ReverbSoundEffect`, `EqualizerSoundEffect`, `CompressorSoundEffect`, etc.) parent to Sound/SoundGroup. Ducking: `CompressorSoundEffect` with `SideChain = sfxGroup` on music.

**New Modular**: 2D: `AudioPlayer → Wire → AudioDeviceOutput`. 3D: `AudioPlayer → Wire → AudioEmitter` (on Part) + auto-created `AudioListener`. `SoundService.ListenerLocation` sets listener on Camera/Character.

**One-Shot SFX**:
```luau
local function playSFX(parent, id)
    local s = Instance.new("Sound"); s.SoundId = id
    s.RollOffMode = Enum.RollOffMode.InverseTapered
    s.RollOffMinDistance = 10; s.RollOffMaxDistance = 80
    s.Parent = parent; s:Play()
    s.Ended:Once(function() s:Destroy() end)
end
```

**Preload**: `ContentProvider:PreloadAsync({sound1, sound2})`. **Client SFX**: `FireClient` → `OnClientEvent` creates invisible Part + `playSFX`.

**Pitfalls**: Server sounds have latency → play feedback on client. Default `RollOffMaxDistance`=10000 studs → set explicitly. Volume > 1 clips. Rapid-fire → check `IsPlaying`. Always `Destroy()` one-shots after `Ended`.

See `references/full.md` for detailed examples, effect table, and client-side patterns.
