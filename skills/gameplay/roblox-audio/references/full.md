# Roblox Audio: Full Reference


> **Code in this reference is illustrative. Adapt to your game and verify in Studio before production use.**

## Legacy System (Sound Objects)

### Where to Place Sounds

| Location | Behavior | Use for |
|----------|----------|---------|
| Child of block/sphere/cylinder BasePart | Volumetric: emits from entire surface, volume changes with distance AND part size | Ambient zones, large area sounds |
| Child of Attachment, MeshPart, TrussPart, WedgePart | Point source: emits from single point, volume changes with distance | Footsteps, impacts, small objects |
| Within SoundService or Workspace | Global: same volume everywhere regardless of position | Background music, UI sounds |

### Basic Playback

```luau
-- Background music (global, in SoundService)
local SoundService = game:GetService("SoundService")
local bgMusic = Instance.new("Sound")
bgMusic.Name = "BackgroundMusic"
bgMusic.SoundId = "rbxassetid://1843463175"
bgMusic.Looped = true
bgMusic.Volume = 0.25
bgMusic.Parent = SoundService
bgMusic:Play()
```

```luau
-- Positional sound (3D, on a part)
local waterfall = Instance.new("Sound")
waterfall.SoundId = "rbxassetid://ASSET_ID"
waterfall.Looped = true
waterfall.Volume = 0.5
waterfall.RollOffMode = Enum.RollOffMode.InverseTapered
waterfall.RollOffMinDistance = 10  -- full volume within this range
waterfall.RollOffMaxDistance = 100 -- silent beyond this range
waterfall.Parent = workspace.WaterfallPart
waterfall:Play()
```

### RollOff Modes

| Mode | Behavior |
|------|----------|
| `Inverse` | Realistic falloff (1/distance). Drops quickly near source, slowly far away. |
| `Linear` | Linear falloff between min and max distance. |
| `InverseTapered` | Inverse near the source, tapers to silence at max. Most natural for games. |
| `LinearSquare` | Attempt at realistic with linear square curve. |

- `RollOffMinDistance`: distance (studs) where volume starts decreasing. Default 10.
- `RollOffMaxDistance`: distance where volume reaches zero. Default 10000 (effectively infinite).

### SoundGroups (Audio Mixer)

SoundGroups let you control volume of multiple sounds at once. Nest them for a mix tree.

```luau
-- Create mix hierarchy in SoundService
local master = Instance.new("SoundGroup")
master.Name = "Master"
master.Volume = 1
master.Parent = SoundService

local music = Instance.new("SoundGroup")
music.Name = "Music"
music.Volume = 0.5
music.Parent = master  -- nested under Master

local sfx = Instance.new("SoundGroup")
sfx.Name = "SFX"
sfx.Volume = 0.8
sfx.Parent = master

-- Assign a sound to a group
bgMusic.SoundGroup = music
```

Adjusting `master.Volume` affects ALL nested groups. Players can control Music vs SFX independently.

### Dynamic Effects

Parent these to a Sound or SoundGroup to modify audio:

| Effect | What it does | Use for |
|--------|-------------|---------|
| `ReverbSoundEffect` | Simulates room reflections | Caves, large halls, bathrooms |
| `EqualizerSoundEffect` | Control volume of frequency bands | Muffled underwater, radio effect |
| `CompressorSoundEffect` | Reduces dynamic range | Consistent volume, ducking |
| `ChorusSoundEffect` | Thickens sound with copies | Ethereal voices, dream sequences |
| `DistortionSoundEffect` | Adds distortion/overdrive | Damaged radio, horror |
| `FlangeSoundEffect` | Sweeping comb filter | Sci-fi, psychedelic |
| `PitchShiftSoundEffect` | Changes pitch without speed | Chipmunk voice, deep voice |
| `TremoloSoundEffect` | Periodic volume modulation | Vibrato, pulsing |

```luau
-- Add reverb to all sounds in a cave zone
local caveGroup = Instance.new("SoundGroup")
caveGroup.Name = "Cave"
caveGroup.Parent = master

local reverb = Instance.new("ReverbSoundEffect")
reverb.DecayTime = 3.0
reverb.Density = 1.0
reverb.Diffusion = 1.0
reverb.WetLevel = -6  -- dB, how much reverb vs dry signal
reverb.Parent = caveGroup
```

### Ducking (Lower music when SFX plays)

Use CompressorSoundEffect with a SideChain:

```luau
-- Music ducks when SFX plays
local compressor = Instance.new("CompressorSoundEffect")
compressor.Threshold = -20
compressor.Ratio = 4
compressor.Attack = 0.01
compressor.Release = 0.2
compressor.SideChain = sfx  -- SFX group triggers the compression
compressor.Parent = music   -- Music group gets compressed
```

## New Modular System (Audio Objects)

The new system uses explicit wiring between audio components. Each object maps to a real-world audio device:

| Object | Real-world equivalent | Role |
|--------|----------------------|------|
| `AudioPlayer` | Media player / turntable | Produces audio from an asset |
| `AudioEmitter` | Speaker in 3D space | Emits audio positionally |
| `AudioListener` | Microphone | Picks up audio from 3D space |
| `AudioDeviceOutput` | Headphones/speakers | Plays to the real player |
| `AudioDeviceInput` | Physical microphone | Captures real player voice |
| `Wire` | Audio cable | Carries stream between objects |
| `AudioTextToSpeech` | TTS engine | Converts text to speech |
| `AudioEqualizer` | EQ pedal | Modifies frequency response |
| `AudioCompressor` | Compressor pedal | Controls dynamic range |
| `AudioReverb` | Reverb unit | Adds room reflections |

### 2D Audio (non-positional)

```
AudioPlayer → Wire → AudioDeviceOutput
```

```luau
-- In SoundService:
local player = Instance.new("AudioPlayer")
player.AssetId = "rbxassetid://MUSIC_ID"
player.Looping = true
player.Volume = 0.5
player.Parent = SoundService

local output = Instance.new("AudioDeviceOutput")
output.Parent = SoundService

local wire = Instance.new("Wire")
wire.SourceInstance = player
wire.TargetInstance = output
wire.Parent = SoundService

player:Play()
```

### 3D Audio (positional)

```
AudioPlayer → Wire → AudioEmitter (on Part)
AudioListener (on Camera/Character) → Wire → AudioDeviceOutput
```

```luau
-- On the part that emits sound:
local player = Instance.new("AudioPlayer")
player.AssetId = "rbxassetid://SFX_ID"
player.Parent = workspace.CampfirePart

local emitter = Instance.new("AudioEmitter")
emitter.Parent = workspace.CampfirePart

local wire = Instance.new("Wire")
wire.SourceInstance = player
wire.TargetInstance = emitter
wire.Parent = workspace.CampfirePart

-- SoundService.DefaultListenerLocation (settable only from Studio, plugins, or
-- Open Cloud Luau execution: PluginOrOpenCloud capability) controls whether
-- Roblox creates and wires the default AudioListener and AudioDeviceOutput.
-- For runtime custom placement, create and wire an explicit AudioListener.

player:Play()
```

`AudioEmitter.DistanceAttenuation` controls the volume-over-distance curve.

### Triggering Audio from Scripts

```luau
-- Basic trigger pattern
local audioPlayer = script.Parent -- AudioPlayer
local part = audioPlayer.Parent

part.Touched:Connect(function(hit)
    if hit.Parent:FindFirstChildOfClass("Humanoid") then
        audioPlayer:Play()
    end
end)
```

## Patterns

### Preloading Critical Audio

```luau
local ContentProvider = game:GetService("ContentProvider")

local criticalSounds = {
    Instance.new("Sound"), -- temp instances for preloading
    Instance.new("Sound"),
}
criticalSounds[1].SoundId = "rbxassetid://HIT_SOUND"
criticalSounds[2].SoundId = "rbxassetid://JUMP_SOUND"

ContentProvider:PreloadAsync(criticalSounds)
-- Now these assets are cached and play instantly
```

Pass the `Sound` instances, not raw id strings, when the status matters. `PreloadAsync` accepts content-ID strings in its `contentIdList`, but in one project every audio id given as a string reported `Failure` in the callback while the sounds loaded and played (`TimeLength` was correct); the same ids given as `Sound` instances reported `Success`. Confirm loading with `IsLoaded` or `TimeLength` rather than the string-form status. Preload only what the first moments need; preloading everything slows the join (performance guide).

### One-Shot SFX (auto-cleanup)

```luau
local function playSFX(parent: BasePart, soundId: string)
    local sound = Instance.new("Sound")
    sound.SoundId = soundId
    sound.RollOffMode = Enum.RollOffMode.InverseTapered
    sound.RollOffMinDistance = 10
    sound.RollOffMaxDistance = 80
    sound.Parent = parent
    sound:Play()
    sound.Ended:Once(function()
        sound:Destroy()
    end)
end
```

### Client-Side Playback

Play sounds on the client for zero-latency feedback. Server tells client WHAT to play:

```luau
-- Server
SFXRemote:FireClient(player, "hit", workspace.Enemy.HumanoidRootPart.Position)

-- Client: a positioned cue gets a temporary anchored part.
-- Cues with no world position (UI, your own weapon, reward chimes) skip this
-- and play on a flat Sound parented to SoundService (see "Flat vs 3D voices").
SFXRemote.OnClientEvent:Connect(function(sfxName: string, position: Vector3)
    local part = Instance.new("Part")
    part.Position = position
    part.Anchored = true
    part.Transparency = 1
    part.CanCollide = false
    part.Parent = workspace
    playSFX(part, SFX_IDS[sfxName])
    task.delay(3, function() part:Destroy() end)
end)
```

## Advanced Audio API Additions

<!-- temporal: 2026-11 -->
- **Acoustic simulation.** `SoundService.AcousticSimulationEnabled` turns on occlusion (muffling through walls), diffraction (bending around corners) and reverberation for the modular system. It also needs `AudioEmitter.AcousticSimulationEnabled` and `AudioListener.AcousticSimulationEnabled` on the pair; the global switch overrides both. `AudioEmitter.SimulationFidelity` (`Enum.AudioSimulationFidelity`) trades detail for cost, and when an emitter and listener disagree the less detailed option wins. A Roblox staff post on the DevForum (2026-11-24) said the feature was then Studio-only and that legacy `Sound` support was being added in a Studio beta (https://devforum.roblox.com/t/studio-beta-sounds-support-acoustic-simulation-for-more-immersive-audio/5003368). Confirm it works in a published server before relying on it, profile dense scenes (many NPC emitters), and keep a fallback such as the raycast occlusion below.
- **Distance attenuation presets.** `AudioEmitter.DistanceAttenuationMode` defaults to `Custom` (the curve from `SetDistanceAttenuation`). The presets `InverseTapered`, `Linear`, `LinearSquared` and `Inverse` use `AudioEmitter.DistanceAttenuationBounds` (default 4 to 10000 studs) instead of the custom curve.
- **Emitter position.** `AudioEmitter.PositionType` and `PositionInstance` let an emitter follow an instance other than its parent.
- **Raw samples (Studio only).** `AudioStreamReader` reads and `AudioStreamWriter` writes raw sample buffers in the audio graph (`Read`/`Peek`, `Write`/`Space`, with `SampleRate`, `WindowSize`, `Layout`, and a read-only `SampleFormat`). They are Studio-only and don't work in Team Create; use them for analysis and tooling plugins, not live gameplay.
- **Audio search ordering.** `AudioSearchParams.SortType` (`Enum.AudioSortType`: `Relevance`, `MostUsed`, `Trending`, `RecentlyCreated`, `ShortestToLongest`, `LongestToShortest`) orders `AssetService:SearchAudioAsync` results.
- **Text-to-speech translation.** `AudioTextToSpeech.AutoLocalize` defaults to `true`: `Text` is translated into the player's language and routed to a matching voice (for example, a female English voice routes to a female voice elsewhere). It currently covers Arabic, Chinese (Mandarin), English, French, German, Hindi, Italian, Japanese, Korean, Portuguese and Spanish. Set it false for names or lines that must stay verbatim (`roblox-localization`).

## Flat vs 3D Voices

- **No world position, no 3D voice.** Positionless one-shots (UI, your own gunshot, reward chimes) played on 3D voices parked at the camera pan and jump as the camera turns, which players report as glitchy audio (observed). Play them on `Sound`s parented to `SoundService` (no `Attachment` or `Part`), or through `AudioPlayer → Wire → AudioDeviceOutput`.
- **Your own first-person weapon.** A weapon sound on a part offset from the camera plays in one ear in first person. Play the local player's weapon flat or from the camera centre, and keep positional sound for other players' weapons.
- **Near distance before volume.** When a distant sound seems too quiet, check `RollOffMinDistance` before raising `Volume`. With `InverseTapered`, a blast 30 studs away with a near distance of 6 is about 14 dB down (6/30). Set the near distance per cue (large explosions far larger than footsteps) instead of one value for every sound. Keep `Volume` at or below 1 and layer instead; shot sounds at `Volume` 2.2 clipped in one project.

## Leveling and Asset Choice (measured in one project)

- **Level by loudness, not by ear.** Library files arrive at very different loudness (music 10+ LU above effects; some effects mastered near -9 LUFS with clipped peaks). Measure each file or slice (for example `ffmpeg -af ebur128` over the exact slice) and set `Volume = 10^((target - LUFS) / 20)`. One working set: music about -28.5 LUFS effective, ambience about 5 dB under music, effects about -18 LUFS per take, true peak at most -3 dBTP. Slices under about 0.4 s measure near -70 LUFS because of gating; level those by peak.
- **Measure before calling a sound weak.** A "too quiet" thump that has almost nothing above 300 Hz only gets louder as a thud when turned up; layering a bright transient fixes it. Compare band energy, loudness and how long the tail takes to fall 40 dB. A short tail, not missing bass, often makes a gun sound small.
- **Moderation.** Uploaded audio is moderated before others can hear it (`audio/assets`). Keep noise, static, hiss and harsh buzzers out of uploads; wire the new id in and keep working while it is reviewed.
- **Mono and channel balance.** Prefer mono takes for effects. One stereo file was 14 dB louder on one side and stayed panned on flat voices.
- **Client-shipped classics.** Some classic sounds ship with the client and play by content path (for example `rbxasset://sounds/oof.ogg`). Creator Store copies titled as a famous sound were unreliable in one check (most were a different recording), so when someone names a platform sound, use the original.
- **Licensed library sounds.** Roblox's catalog includes licensed sound-effect and music libraries that can be used by id without uploading (check the asset's description and the Creator Store terms). Search with the library's exact title shape; descriptive queries mostly return ripped game audio. Many effect files open with silence or hold several takes back to back: measure onsets in a downloaded copy, then play one slice with a playback region.
- **Music cuts.** Newer music uploads carry album and artist fields. Search the album for its cuts (main, underscore, short and sting versions); underscore cuts make quieter beds. Don't trust mood tags or "no percussion" titles; listen to or analyse each pick, and screen instrumentals for speech.

## Slicing, Loops and Timing

- **Playback regions are in source seconds.** Set `PlaybackRegionsEnabled = true` and `PlaybackRegion = NumberRange.new(start, start + length)`. The slice lasts `length / PlaybackSpeed`: 0.45 s at speed 0.4 plays about 1.1 s. Pitch a charge whine up to fit a shorter charge; a gunshot pitched to about 0.4 reads as a heavy thud and can double as a low layer.
- **Sync to the peak, not the first onset.** A crash sliced from 0 had its loudest hit 0.45 s in and boomed after the slam. Start the slice a few hundredths of a second before the peak, schedule each take early by its measured onset, and mark the animation frame where the sound belongs.
- **Keep natural tails.** Cutting a gunshot tail at 0.5 s made it sound clipped; fade only once the tail is about 30 dB down, and prefer takes that end in their own tail over a region cut mid-ring.
- **Held sounds are one looped voice.** Play a drill, motor or beam as one looped voice for as long as the input is held, not as repeated slices, which click. Pick a loop region with flat RMS, fade in fast and out slowly. A noisy-tailed ambience loops cleanly over its quiet middle on two voices with an equal-power crossfade a few seconds before the region ends.
- **Variation.** Give each repeated hit cue 3–8 takes with per-take gain, never repeat the last take, and vary pitch by roughly ±12%. A repeated mechanical beat from one machine should use one take and vary only pitch.
- **Motion-driven sounds.** Drive continuous movement sounds from distance travelled, scaled by speed over top speed, rather than from a timer.
- **Match meaning.** A cue must match what the player is getting: a coin sound on raw material reads wrong until it becomes money. Tool switches deserve a short sound even when the animation is smooth.
- **Counting plays in tests.** In one project `Sound.Played` did not fire for replays of region-sliced sounds while `IsPlaying` showed them playing. Count rising edges of `IsPlaying` on pooled voices, or count in your own play wrapper.

## Occlusion and Interior Sources

- **Cheap raycast occlusion.** For a few important sources, a few times a second cast one ray from the camera to the source; when a wall blocks it, ease the sound quieter and muffled (lower `Volume` plus an `EqualizerSoundEffect` cut) rather than switching hard. Prefer acoustic simulation once it is confirmed in published servers.
- **Interior sources and caps.** TVs and radios inside buildings played through walls at full volume and stacked, and many car alarms fired at once (observed). Lower interior sources when the listener is outside the room, and cap concurrent instances of the same ambient or alarm sound.
- **Stop sounds with their source.** A looping alarm kept playing after its car was destroyed. Parent loops to the emitting object or stop them in its cleanup path, and test the destroy path for every loop.

## Common Mistakes

- **Playing sounds on the server for feedback**: Server sounds have network latency. Play on client for responsive SFX. Server only for sounds ALL players must hear identically.
- **No RollOff configuration**: Default RollOffMaxDistance is 10000 studs (basically infinite). Set it explicitly or sounds bleed across the entire map.
- **Stacking rapid sounds**: Playing the same sound 10x in 0.1s creates ear-splitting overlap. Use a cooldown or a voice cap, but check it against the fastest real event spacing: a 0.3 s cooldown silently dropped the middle of three slams 0.28 s apart in one project, and a hit gated by a particle throttle skipped landings. Every visible event deserves a sound, even a quiet one.
- **Forgetting Looped = false on one-shots**: Default is false, but if you clone from a template that has Looped = true, your SFX plays forever.
- **Not destroying one-shot sounds**: Sounds parented to destroyed parts get GC'd, but sounds in SoundService accumulate. Always Destroy() after Ended.
- **Volume > 1**: Causes clipping/distortion. Keep ≤ 1. Use SoundGroup volume for amplification.
- **Using legacy system for voice chat integration**: The new AudioPlayer/Wire system is required for voice chat features (AudioDeviceInput, AudioSpeechToText).
- **No SoundGroup hierarchy**: Without groups, players can't independently control music vs SFX volume in settings.

## Review and regression checks

- Give subjective review candidates stable names or slots and freeze their source, pitch, speed, offset, and effects while comparing them. Record the selected settings before adding random variation.
- Listen to the actual requested cue and its in-game use. Successful loading, a filename, or measured loudness does not establish sound identity or acceptable feel. If listening is unavailable, keep that acceptance check explicitly unverified.
- Inspect a cropped cue's start, attack, peak, release, and tail. Use suitable fades or adjusted slice points where a hard boundary produces a click or abrupt cutoff; audition every derived cue at its actual playback settings. Do not apply one fade duration blindly to all recordings.
- Test each configured action slot and the full preview sequence: windup, charge, release, travel or near miss, impact, and kill where present. Confirm the correct cue plays in each slot and that previews use the intended nonspatial or spatial mix. A shared refactor must preserve deliberately distinct cosmetic overrides.
- Reproduce loudness complaints from the listener's actual position and event path. Check launch, passing near the listener, impact, and victim-local playback separately. Align the perceived attack and peak with the visual event; removing leading silence alone may leave a slow buildup.
- Validate an audio-review tool using known clips, including silence and a known signal, before trusting its descriptions. Use direct measurements for timing and perceptual review for identity/feel; record the tool's demonstrated limits and retain owner listening when needed. Do not infer capability from a model label or a successful request.
