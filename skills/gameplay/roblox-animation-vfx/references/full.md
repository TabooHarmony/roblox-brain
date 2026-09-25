# roblox animation and vfx: full reference

> Code examples are illustrative. Adapt them to your project and verify in Studio before production use.

Visual effects are a budgeted part of gameplay, not decoration added after performance work. Build them around an owner, a trigger, a duration, and a cleanup path.

## Design an effect before wiring it

Start with the gameplay signal: where is the hazard, when is contact, and what changed? Sketch the effect in phases: an optional readable warning, a fast contact shape, a brief peak, then a quieter decay. A projectile may need a travel trail and a separate impact; an environmental effect may need continuous motion and an occasional accent. Give each layer one job rather than adding emitters until the event disappears under glow. Keep the warning distinguishable from the hit, especially when timing or danger matters.

Test the silhouette with sound and post-processing off. Does a player see the impact point and direction at gameplay distance, against both dark and bright backgrounds? Check that a moving slash's tapered tail trails its direction of travel instead of pointing ahead of it. Then add secondary motion (sparks, smoke, fragments or a shockwave), sound, and a small local camera response only where they clarify the event. Stagger layers deliberately so everything does not appear and vanish on the same frame. A bright fill and a darker edge can make the same shape read without stacking unrelated shapes. Make the strongest visual moment brief; reserve dense spectacle for rare events so routine actions stay legible. Reduce intensity or disable nonessential layers if the player has selected reduced motion.

For a natural-looking effect, break the subject into different behaviors rather than one emitter doing everything: for example, a water impact has a surface ring, heavy upward splashes, fine droplets, then lingering mist. Give those layers different lifetimes, speeds, scale and transparency. Reuse a coherent texture/palette family and vary motion enough to avoid obvious repetition. Roblox's volcano and waterfall tutorials demonstrate this layered approach; the composition is a design choice, not a requirement to reproduce their example assets.

## 1. Animation loading

Use an `Animator` under the character's `Humanoid` or under an `AnimationController` for non-character rigs. Keep asset IDs in configuration and verify that the experience has permission to use them.

```luau
local function loadTrack(animator: Animator, assetId: string, priority: Enum.AnimationPriority): AnimationTrack
    local animation = Instance.new("Animation")
    animation.AnimationId = assetId
    local track = animator:LoadAnimation(animation)
    track.Priority = priority
    return track
end
```

Load the track when the character or prop is created, not in a hot input path. A missing or unavailable asset should leave the gameplay state valid and produce a useful warning.

The helper above is a useful classic or local-presentation pattern. In a Server Authority project, do not treat an `AnimationTrack` reference as a permanent identity: rollback or resimulation can stop or replace the visible track. Store the animation ID in state and query the current animator tracks when applying changes, for example with `Animator:GetPlayingAnimationTracks()` or `Animator:GetTrackByAnimationId()`.

## Server Authority animation and effects

When an animation affects synchronized gameplay, mirror its control logic on the client and server in a shared module and run the synchronized part through `RunService:BindToSimulation()` (requires `Workspace.UseFixedSimulation` enabled in Studio). Keep camera, particles, sounds, and other presentation work outside the simulation callback so it can respond to the current predicted state.

Predicted effects must be reversible. A client can briefly predict an impact, explosion, or sound that the server later rejects. Drive durable presentation from synchronized state or a state machine, and cancel or hide effects when rollback changes that state. Do not let a predicted effect grant damage, rewards, or other gameplay outcomes.

## 2. Priorities and markers

Use animation priority to define which tracks may override the same joints. Keep locomotion and action tracks separate. Use marker signals for synchronized effects instead of guessing a timestamp that changes when an animation is retuned. In Server Authority, resolve the current track after rollback rather than assuming a cached track handle still represents the visible animation.

```luau
local attack = loadTrack(animator, ATTACK_ID, Enum.AnimationPriority.Action)

local markerConnection = attack:GetMarkerReachedSignal("Impact"):Connect(function(value)
    Effects:PlayImpact(character, value)
end)

attack.Stopped:Once(function()
    markerConnection:Disconnect()
end)
attack:Play(0.08)
```

If the animation can be stopped and restarted, make the effect trigger idempotent or clear the previous attack state before playing again.

## 3. Blending

Use a short fade when moving between locomotion states. Stop tracks that should no longer contribute. A track that remains playing at a low weight still consumes state and can make later debugging difficult.

Keep the state machine responsible for selecting tracks. The effect system should react to a named event such as `Footstep` or `Impact`, not inspect every animation frame. Treat the contact sound and its timing as part of the same cue: a visually sharp hit with late or missing audio can feel weak. Synchronize both to the event, allow players to lower effects independently, and route sound mixing details to `roblox-audio`.

## 4. Particle emitters

For a continuous effect, tune `Rate`, `Lifetime`, `Speed`, `Size`, and `Color`. For a one-shot effect, keep emission manual:

```luau
local emitter = template:Clone()
emitter.Rate = 0
emitter.Parent = attachment
emitter:Emit(18)

task.delay(2, function()
    if emitter.Parent then
        emitter:Destroy()
    end
end)
```

Use `NumberSequence` and `ColorSequence` to move size, transparency, and color over lifetime. Keep lifetime and rate low enough that a repeated effect cannot accumulate unbounded particles. Prefer a small set of reusable templates over creating new textures and emitters for every hit.

### Textures, flipbooks and non-particle effects

A flipbook is one image containing frames of motion. For a native `ParticleEmitter`, set a matching `FlipbookLayout` (including `Custom` with `FlipbookSizeX`/`FlipbookSizeY` for non-square grids), then choose `FlipbookMode`: `OneShot` plays once over the particle's lifetime, while `Loop` repeats. `FlipbookStartRandom` with `FlipbookFramerate` set to zero chooses a different static frame per particle, useful for varied sparks or shards; it is not an animated flipbook. Give frames enough padding to avoid texture bleeding. Make tintable shapes with a transparent background and neutral values rather than baking a different color into every texture; test the actual `Color` sequence and blend against the scene. Verify the animation at the intended lifetime and on mobile: expensive flipbooks may be disabled on memory-constrained clients.

Not every effect with a sequence of textures is a native particle flipbook. A model can hold individually textured decals, mesh frames, or UI images advanced by a separate player or plugin. Inspect its object types, animation script and asset IDs before assuming `ParticleEmitter.Flipbook*` settings will control it. An `.rbxm` may only contain templates while a place file carries the playback machinery. Treat imported effect scripts as untrusted; inspect them before running, check whether textures are owned and usable by the target experience, and recreate the idea with your own assets when reuse rights are unclear. A visual preview alone does not prove the model will play after insertion.

For one-shot hit feedback, an expanding mesh ring or a short screen-space image can make the first frame readable while particles supply texture and motion afterward. Keep screen effects local, brief and optional; do not let an overlay obscure the player's next input or an enemy's telegraph. Mesh-based shockwaves and custom image players can require more scripting than a native emitter, so prefer built-in effects when they achieve the same read.

## 5. Beams and trails

Both effects depend on attachments. Put the attachments on stable parts, and verify their orientation and lifetime when the model is animated.

```luau
local startAttachment = source:FindFirstChild("BeamStart")
local endAttachment = target:FindFirstChild("BeamEnd")
if not startAttachment or not endAttachment then
    return
end

local beam = beamTemplate:Clone()
beam.Attachment0 = startAttachment
beam.Attachment1 = endAttachment
beam.Parent = source

Debris:AddItem(beam, 0.35)
```

A trail records movement between its attachments. If the attachments are destroyed or teleported unexpectedly, the visual can stretch or disappear. Remove the trail with the owning projectile or character.

## 6. Tweening

`TweenService` is useful for UI, transparency, color, size, and camera-adjacent feedback. Keep the target properties explicit and retain the tween if you need to cancel it on a state change.

```luau
local TweenService = game:GetService("TweenService")
local tween = TweenService:Create(
    flashPart,
    TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
    { Transparency = 1 }
)

tween:Play()

-- `Completed` also fires with Enum.PlaybackState.Cancelled when the tween is
-- stopped early, including when a replacement setup cancels it. Check state
-- and ownership before destroying a target another effect may now use.
tween.Completed:Connect(function(playbackState)
    if playbackState ~= Enum.PlaybackState.Completed then
        return -- cancelled: leave cleanup to the current owner
    end
    if flashPart.Parent then
        flashPart:Destroy()
    end
end)
```

Do not start a new tween every render frame for a value that could be computed once. When a state changes quickly, cancel or replace the old tween rather than allowing several competing animations to finish.

`Completed` fires for cancelled tweens too. Destroying the target on cancellation is fine when it is a genuinely disposable one-shot object that no other effect can reuse; shared, pooled, or reused targets belong to their current owner:

```luau
local puff = Instance.new("Part")
puff.Anchored = true
puff.Parent = workspace

local puffTween = TweenService:Create(puff, TweenInfo.new(0.3), {Transparency = 1})
puffTween.Completed:Once(function(_playbackState)
    if puff.Parent then
        puff:Destroy() -- one-shot part: no other effect can reuse it
    end
end)
```

## 7. Lighting and camera feedback

Short-lived color correction, bloom, blur, or camera shake should be subtle and owned by the local player. Keep gameplay logic independent of the visual effect so a disabled effect does not change damage, movement, or reward results.

For camera shake, combine small offsets around the current camera transform and decay the amplitude. Avoid permanently setting `CameraType` or replacing the camera's subject without a restoration path.

## 8. Pooling and cleanup

Pool effects that fire frequently, such as muzzle flashes, hit sparks, and footsteps. A pool should reset every mutable property before reuse:

- parent and enabled state;
- attachments and adornments;
- transparency, color, and size sequences;
- active tweens and connections;
- expiration timestamp.

Use `Debris` for a simple one-shot lifetime. Use an explicit owner object when the effect has multiple connections or must be cancelled early. For continuous emitters, disable them first, let existing particles expire, and only then remove the owner if a natural fade matters. For multi-part effects, keep the triggers and timing together; an animation file or particle model alone may not include the sequence that actually plays it.

Budget the *simultaneous view*, not just each effect alone. Test several players repeating the action near the camera, and compare low- and high-quality graphics on a mobile-class device. Transparent screen coverage, overlapping layers, lights and unique animated textures can cost more than an emitter count suggests. Scale secondary layers down before sacrificing the primary contact cue. A showcase full of emitters is not a performance target.

## 9. Legacy effect classes: Sparkles (and Fire, Smoke)

`Sparkles` is a minimal particle emitter: parent to a `BasePart` or an `Attachment` in one. It has essentially three knobs (`Enabled`, `SparkleColor`, `Color`) and no lifetime, texture, rate, or `Emit()` control. Use it for quick placeholder effects only; any real effect should be a `ParticleEmitter`.

Two behaviors matter:

- Setting `Enabled = false` stops new emission, but existing particles render until their lifetime expires. Destroying the object (`Parent = nil` or `:Destroy()`) kills all particles instantly. To stop cleanly, disable first, then `Debris:AddItem(sparkles, a few seconds)`.
- Particles emit from the center of the parent part. Parent to an `Attachment` when the start position matters.

`Fire` and `Smoke` are the same story: fixed look, few knobs, superseded by `ParticleEmitter` for anything custom.

## 10. Preloading and runtime failure

Preload only the assets needed for an imminent experience state. Preloading an entire catalog increases memory pressure and still does not make an unavailable asset valid. Show a fallback when an animation, image, sound, or particle texture cannot load.

## 11. Review checklist

- [ ] Every animation uses an `Animator` and a verified asset ID.
- [ ] Track priority and stopping behavior are intentional.
- [ ] Markers or named gameplay events drive synchronized effects.
- [ ] Bursts have bounded count and lifetime; texture/flipbook layouts match their source images.
- [ ] The main silhouette and travel direction read before secondary layers, and contact VFX/SFX land together.
- [ ] Custom mesh, decal, or UI sequences have the player and asset permissions they need; imported scripts were inspected.
- [ ] Beam and trail attachments survive for the effect's lifetime.
- [ ] Tweens are replaced or cancelled when state changes.
- [ ] `Completed` handlers check `PlaybackState` and effect ownership before destroying shared or pooled instances.
- [ ] Temporary instances, connections, and tasks have an owner.
- [ ] Effects are tested on the target device class and in a real playtest.

## Community ecosystem (leads, not sources)

- [How to animate Tool Parts](https://devforum.roblox.com/t/how-to-animate-tool-parts-guns-knifes-etc/359484) (3.1k likes) and [Jespone's guide to animations](https://devforum.roblox.com/t/jespones-guide-to-animations/225752): the tool-animation canon; [Blender rig exporter](https://devforum.roblox.com/t/blender-rig-exporteranimation-importer/34729) for the art pipeline.
- VFX: [Hidden glass distortion w/ real-time reflections](https://devforum.roblox.com/t/hidden-glass-distortion-effect-with-real-time-reflections-tutorial/2338789); [Wind Shake](https://devforum.roblox.com/t/wind-shake-high-performance-wind-effect-for-leaves-and-foliage/1039806) foliage motion; [Realism pack](https://devforum.roblox.com/t/realism-%E2%80%94-make-your-games-feel-more-immersive/898642) (1.8k likes).
