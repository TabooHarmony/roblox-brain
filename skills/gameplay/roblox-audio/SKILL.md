---
name: roblox-audio
description: "Use when adding, changing, or fixing Roblox audio: playback, spatial sound, music, sound effects, SoundGroups, or dynamic effects."
when_to_use: "Also when a sound doesn't play, is too loud or quiet, overlaps or loops wrongly, volume settings, and auditing audio assets or mixes."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/reference/engine/classes/SoundService
  - https://create.roblox.com/docs/audio/objects
  - https://create.roblox.com/docs/audio/effects
  - https://create.roblox.com/docs/sound/groups
  - https://create.roblox.com/docs/sound/dynamic-effects
  - https://create.roblox.com/docs/reference/engine/classes/AudioEmitter
  - https://create.roblox.com/docs/reference/engine/classes/AudioTextToSpeech
  - https://create.roblox.com/docs/audio/assets
  - original
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine/classes/Sound.yaml
---

# Roblox Audio

## When to Load

Audio playback, spatial sound, music, SFX, mixing (SoundGroups), effects, leveling and cue timing. Covers legacy `Sound` and the modular AudioPlayer/Wire system.

## Quick Reference

**Two Systems**: Legacy (`Sound`/`SoundGroup`/`SoundEffect`): simpler. New modular (`AudioPlayer`/`AudioEmitter`/`Wire`/`AudioDeviceOutput`): preferred for new projects, required for voice chat.

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

**New Modular**: 2D: `AudioPlayer → Wire → AudioDeviceOutput`. 3D: `AudioPlayer → Wire → AudioEmitter` (on Part). Studio/plugin-only `SoundService.DefaultListenerLocation` controls the default listener; wire an explicit `AudioListener` for runtime control.

**One-shots**: create, `Play()`, `Ended:Once(Destroy)` (full.md).

**Preload**: `PreloadAsync({sound1, sound2})` with instances; confirm with `IsLoaded`/`TimeLength`. **Client SFX**: positioned cues on a temp part; positionless cues (UI, own weapon) flat in `SoundService`.

**New APIs**: acoustic simulation (`SoundService.AcousticSimulationEnabled` + emitter/listener; verify in live servers), `DistanceAttenuationMode` presets, `AudioTextToSpeech.AutoLocalize`.

**Pitfalls**: play feedback on the client. Set `RollOffMaxDistance` (default 10000) and per-cue `RollOffMinDistance` before raising Volume; Volume > 1 clips. Cooldowns must not drop real events. Stop loops when their source is destroyed.

See `references/full.md` for detailed examples, effect table, and client-side patterns.
