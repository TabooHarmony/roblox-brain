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

### Track control surface: Play parameters, weight, and event semantics

- `track:Play(fadeTime, weight, speed)` sets the initial controls; `AdjustSpeed`/`AdjustWeight` change them mid-play. `Speed`, `WeightCurrent`, and `WeightTarget` are read-only; there is no writable `.Weight` property.
- **Weight convergence**: weight fades toward `WeightTarget` over the fade time; `WeightCurrent` reflects the blend in progress. When a state machine must know the blend has settled, poll `math.abs(track.WeightCurrent - track.WeightTarget) < epsilon` (a small epsilon like 0.01) rather than assuming a fade is instant.
- **`Stopped` vs `Ended`**: `Stopped` fires on natural end *and* on an explicit `Stop()` (even with a fade); `Ended` fires only after the track has fully finished affecting the pose — after any fade. Hook cleanup/destroy to `Ended`; hook gameplay chaining to `Stopped` and guard against the explicit-stop case.
- **`DidLoop`** gives loop-count logic (play exactly N cycles) instead of wall-clock guessing against `track.Length`.
- **Duration math**: at constant positive speed, a full forward pass lasts `track.Length / track.Speed`. `Length` is `0` until loaded; guard readiness and bound waits. Speed `0` pauses playback, so do not divide by it; reverse playback and mid-track starts need separate handling.
- **Priority in practice**: `Core < Idle < Movement < Action < Action2 < Action3 < Action4`. For joints affected by multiple tracks, priority determines evaluation order, and tracks at the same priority blend by weight. Do not treat enum numeric values as this ordering (Core has a special value), or assume an equal-priority track blocks another regardless of weight.

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

## Animation Graphs: state machines and expressions (2026-11)

The Animation Graph Editor builds an `AnimationGraphDefinition` asset of nodes, connections and parameters. Publishing it gives an ordinary asset id: load it on an `Animator` like any `Animation`, `Play()` it, and drive it with `AnimationTrack:SetParameter(name, value)`. The node types include `StateMachineNode`, `OneShotNode`, `Blend1DNode`/`Blend2DNode`, `SelectNode`, `PrioritySelectNode`, `RandomSequenceNode`, `SequenceNode`, `SpeedNode`, `MaskNode`, `AddNode`/`SubtractNode`/`OverNode` and `ClipNode`; `GetParameter` and `GetParameterDefaults` read values back. <!-- temporal: 2026-11 -->

**State machines.** A state machine node groups named states (a clip, a blend node or a nested state machine; the state's name must match the node input) and outputs the active pose, or a blend of two while transitioning. `EntryState` picks the start state. Each transition has `From` (unset for an **(Any)** transition), `To`, `WaitFor` and a blend `Duration` (default 0.15 s) with `Curve` limited to `Linear` or `CubicV2`:

- `WaitFor = Trigger` shows an **Expression** box: a boolean parameter (`Grounded`) or a condition (`Speed >= 12`).
- `WaitFor = Finished` with `When = Finished` (after the source ends) or `BeforeFinished` (start blending one Duration before the end).
- When several expressions are true, the highest `Priority` (0-65,535) wins; equal priorities pick **at random**, so give competing transitions distinct priorities.
- Only the active state's events pass through; during a transition the graph's global event rules apply.

The documented jump example: states `Locomotion` (a `Blend1DNode` of idle and run on `Speed`), `Fall` and `LandIdle` (clips with Play Mode `OnceAndHold`); `Locomotion → Fall` on `not Grounded` (0.2 s), `Fall → LandIdle` on `Grounded` (0.1 s), `LandIdle → Locomotion` on `Finished`/`BeforeFinished` (0.2 s). Gameplay code only updates `Grounded` and `Speed`.

**Expressions** are short Luau-like formulas that compute a node property or a transition condition from graph parameters: arithmetic and comparisons, `and`/`or`/`not` with Luau truthiness, `if ... then ... elseif ... else` expressions, the `math` library (not `math.frexp`, `math.noise` or `math.randomseed`; `math.modf` returns only the integer part), `Vector2`/`Vector3`/`Color3`/`CFrame` construction and members, and `..`. Multi-line expressions allow `local` and `return`, but an `if` body may hold only a `return` or one expression. Value nodes (`AnimationValueNodeDefinition`, `NodeType = Expression`) publish computed values through `AnimationValueOutputDefinition` outputs. A `OneShotNode` combines its pose with the base pose by `Enum.AnimationNodeBlendMode`: `Over` replaces by weight, `Add` layers additively, `Subtract` removes.

```luau
-- Illustrative: drive a published graph from the humanoid.
local RunService = game:GetService("RunService")

local function driveGraph(animator: Animator, humanoid: Humanoid, graphId: string): AnimationTrack
    local animation = Instance.new("Animation")
    animation.AnimationId = graphId
    local track = animator:LoadAnimation(animation)
    track:Play()
    local connection: RBXScriptConnection
    connection = RunService.Stepped:Connect(function()
        if not track.IsPlaying then
            connection:Disconnect()
            return
        end
        track:SetParameter("MovementSpeed", humanoid.MoveDirection.Magnitude * humanoid.WalkSpeed)
        track:SetParameter("MaxSpeed", humanoid.WalkSpeed)
        track:SetParameter("Grounded", humanoid.FloorMaterial ~= Enum.Material.Air)
    end)
    return track
end
```

Prefer a graph state machine over hand-written track switching when transitions are pure animation decisions; keep gameplay state (can the player attack?) in code and pass only its result as a parameter. In Server Authority, the same "query, don't cache tracks" rule applies to graph tracks.

## Avatar joints and procedural poses

New R15 player rigs (with `StarterPlayer.AvatarJointUpgrade`, the default for new experiences) use `AnimationConstraint` joints instead of `Motor6D`; a default R15 checked in Studio in November 2026 had no `Motor6D`s at all. `IsA("Motor6D")` is false for them, and their `C0`/`C1` are read-only aliases. See `roblox-physics` for the full migration table. <!-- temporal: 2026-11 -->

- **Layer procedural motion in `Transform` during `RunService.PreSimulation`.** The `Animator` writes `Transform` between `PreAnimation` and `PreSimulation`, so multiplying in afterwards stacks with playing tracks. Skip frames where `Animator.EvaluationThrottled` is true. Never edit rig attachment CFrames.
- **Look joints up lazily and accept both classes.** `CharacterAdded` can fire before parts stream in; an eager lookup finds nothing and no pose ever applies (field-measured).
- **Measured R15 conventions** (one project): shoulder +X raises the arm forward, elbow +X bends the forearm up, waist +Y turns the chest so the right shoulder goes forward, and `Transform` composes `Rx * Ry * Rz`. Check reach in HumanoidRootPart space, not UpperTorso space. Drop joints a new pose doesn't use once they ease near zero, or they freeze instead of returning to the walk.
- **Skinned arms bend only while their joints still link the parts.** With elbow and wrist joints stripped, skinned meshes render as rigid blocks. Never resize skinned parts at runtime (the crease pinches); to reach further, straighten the arm.
- **Put the `Animator` under the `Humanoid`** in a model that contains one; an `Animator` under an `AnimationController` there moved nothing (field-observed).
- **Default idle and walk animations write face controls every frame,** hiding scripted dynamic-head expressions. Strip those tracks' face channels or apply the expression after the animator each frame, and check in Play, not Edit.

```luau
-- Illustrative: procedural neck look on either rig type.
local RunService = game:GetService("RunService")

local function findJoint(character: Model, partName: string, jointName: string): Instance?
    local part = character:FindFirstChild(partName)
    local joint = part and part:FindFirstChild(jointName)
    if joint and (joint:IsA("AnimationConstraint") or joint:IsA("Motor6D")) then
        return joint
    end
    return nil
end

local function bindNeckLook(character: Model, getYaw: () -> number): RBXScriptConnection
    local neck: Instance? = nil
    return RunService.PreSimulation:Connect(function()
        neck = neck or findJoint(character, "Head", "Neck") -- lazy: parts may stream in late
        if neck == nil then
            return
        end
        local look = CFrame.Angles(0, getYaw(), 0)
        if neck:IsA("AnimationConstraint") then
            neck.Transform = look * neck.Transform
        elseif neck:IsA("Motor6D") then
            neck.Transform = look * neck.Transform
        end
    end)
end
```

**NPC locomotion by direction.** Author forward, back and strafe clips at the same length so they stay in step, weight them each frame by movement direction against facing, and scale playback by actual speed over each clip's authored pace; a circling NPC then strafes with its chest on the target. Give crouch and slide clips the same sink the server applies, and after the Animator runs, counter-rotate head and arms by the torso's clip rotation plus aim pitch so the weapon points where the NPC aims. Make held weapons massless and non-queryable so shots pass through.

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

## Production VFX patterns

### Layered bursts timed by attributes

Author an effect as a template `Attachment` (or Folder) whose emitters each carry their own timing, so artists retune it in Studio without touching code. One module plays any such template:

- `EmitCount` (number): particles per emit;
- `EmitDelay` (number, seconds): offset from the trigger;
- optional `EmitDuration`: emit continuously for that long instead of a single burst;
- optional `Essential = true`: keep this layer even when the effect budget is tight.

```luau
-- Illustrative EffectPlayer: plays a layered template at a world CFrame.
local Debris = game:GetService("Debris")

local EffectPlayer = {}

local MAX_LIFETIME = 20 -- the docs cap particle lifetime at 20 s

local function longestLifetime(root: Instance): number
    local longest = 0
    for _, d in root:GetDescendants() do
        if d:IsA("ParticleEmitter") then
            local delay = d:GetAttribute("EmitDelay") or 0
            local duration = d:GetAttribute("EmitDuration") or 0
            longest = math.max(longest, delay + duration + math.min(d.Lifetime.Max, MAX_LIFETIME))
        end
    end
    return longest
end

-- scale: 0..1 budget multiplier from your effect budget (see below).
function EffectPlayer.play(template: Attachment, at: CFrame, scale: number)
    local fx = template:Clone()
    fx.WorldCFrame = at
    fx.Parent = workspace.Terrain -- attachments in Terrain need no host part
    for _, d in fx:GetDescendants() do
        if d:IsA("ParticleEmitter") then
            local essential = d:GetAttribute("Essential") == true
            local count = math.floor((d:GetAttribute("EmitCount") or 0) * (essential and 1 or scale) + 0.5)
            local delay = d:GetAttribute("EmitDelay") or 0
            local duration = d:GetAttribute("EmitDuration")
            d.Enabled = false
            task.delay(delay, function()
                if not d.Parent then
                    return -- effect already cleaned up
                end
                if duration then
                    d.Enabled = true
                    task.delay(duration, function()
                        if d.Parent then
                            d.Enabled = false
                        end
                    end)
                elseif count > 0 then
                    d:Emit(count)
                end
            end)
        end
    end
    Debris:AddItem(fx, longestLifetime(fx) + 0.25)
    return fx
end

return EffectPlayer
```

Rules that keep this safe: emitters in templates have `Rate = 0` or `Enabled = false`; cleanup waits for the longest layer, because destroying an emitter kills its live particles instantly; and nothing in the effect touches gameplay state.

### Effect budgets for phones

The docs advise against scaling visual effects from `UserGameSettings.SavedQualityLevel`, because it fights the engine's own quality scaling. Budget from what you control instead:

- **Cap concurrent effects per kind** (for example 8 hit sparks, 2 explosions) and drop the oldest or skip the newest past the cap.
- **Scale non-essential layers by measured frame time** with hysteresis (for example drop to 0.5 when the rolling average stays over 22 ms for a second, recover under 18 ms).
- **Cull by distance** to the camera for routine effects (field-measured: about 90 studs for small animated surfaces), and skip the effect entirely when its origin is off screen and not gameplay-critical.
- **Budget the simultaneous view**: several players repeating an action near the camera, on a mobile-class device. Particle property changes are documented as expensive, so set properties at template time rather than per frame.

```luau
-- Illustrative budget: frame-time-driven scale with hysteresis and per-kind caps.
local RunService = game:GetService("RunService")

local Budget = { scale = 1 }
local active: { [string]: number } = {}
local CAPS = { spark = 8, explosion = 2 }

local average = 1 / 60
RunService.Heartbeat:Connect(function(dt)
    average += (dt - average) * 0.05
    if average > 0.022 then
        Budget.scale = 0.5
    elseif average < 0.018 then
        Budget.scale = 1
    end
end)

function Budget.tryAcquire(kind: string, lifetime: number): boolean
    local count = active[kind] or 0
    if count >= (CAPS[kind] or math.huge) then
        return false
    end
    active[kind] = count + 1
    task.delay(lifetime, function()
        active[kind] = (active[kind] or 1) - 1
    end)
    return true
end

return Budget
```

### Server-authority-safe and replicated effects

- **Effects are presentation.** Never grant damage, rewards or state from an effect, a `Touched` on an effect part, or a particle callback.
- **Under Server Authority, predicted effects must be reversible.** Key each effect by the synchronized event that caused it (for example `entityId .. ":" .. shotIndex`); play once per key, and cancel or hide it when rollback changes that state. Do not cache `AnimationTrack` handles across rollback: the server-authority techniques page still says to query `Animator:GetTrackByAnimationId()` or `GetPlayingAnimationTracks()` when applying changes. <!-- temporal: 2026-11 -->
- **Classic replication:** the server sends one compact event (position, normal, kind) and every client plays the effect locally. The shooter's client plays its own copy immediately and ignores the echo for its own events.
- **Fire one-off payoff effects only on real events.** Late removal packets for crumbling chunks flashed the payoff effect once per chunk in one project.

```luau
-- Illustrative: play-once-per-key with rollback cancellation.
local played: { [string]: Instance } = {}

local function playKeyed(key: string, spawnEffect: () -> Instance)
    if played[key] then
        return -- resimulation replayed the same event: don't double the effect
    end
    played[key] = spawnEffect()
end

local function cancelKeyed(key: string)
    local fx = played[key]
    played[key] = nil
    if fx and fx.Parent then
        fx:Destroy()
    end
end
```

Expire old keys after a few seconds so the table can't grow without bound.

### Particle facts and field-tested settings

From the `ParticleEmitter` reference and particle guide: lifetime is capped at 20 s; `LightEmission` 0 is normal blending and 1 is additive; `Brightness` scales emitted light only when `LightInfluence` is 0; `FlipbookBlendFrames` crossfades flipbook frames instead of swapping them; `TimeScale` runs 0-1 and 0 freezes particles in place; particles follow global wind only with `WindAffectsDrag` on and `Drag > 0`; a grayscale texture without alpha can use `LightEmission = 1` to hide its dark regions.

Field-tested (individual projects; tune to your camera):

- **Hitstop:** `TimeScale = 0` right after `Emit` holds an impact's particles for the freeze, then restore it.
- **Size for camera distance.** The stock sparkles texture at `Size` 1.5 covered the screen at 3 studs; a contact flash about 0.4 studs across needed `Size` about 0.7 with a dark copy (`Size` 1.0) behind for contrast.
- **Small additive accents need `Brightness` (about 4).** A shockwave ring under about 2 studs was a faint smudge, invisible on light surfaces; it reads at 1-8 studs. Behind dust, use `LightEmission` 1, transparency 0 and a `ZOffset` toward the camera.
- **Lie a particle flat on a face** with `Orientation = VelocityPerpendicular` and a tiny speed (0.01) along the surface normal.
- **Loot and debris fountains under default gravity (196.2 studs/s²):** rise height is `v² / (2g)`, so 2.3-3.7 studs needs about 30-38 studs/s up; 8-12 studs/s rises under half a stud. Fan pieces evenly by index.
- **Cosmetic chips need no physics.** Anchored pooled Parts moved with one `workspace:BulkMoveTo` per frame in a client-only simulation. Spray them out of the impact (impact point minus object centre), spawn about 0.2 studs outside the surface with a minimum outward speed (about 35% of the burst), and re-read the floor every ~0.75 studs of sideways travel. A median throw of about 2 studs and a max of about 13 read right.
- **Trails on spinning debris:** `Trail.FaceCamera = true` with its two attachments across the piece keeps width; disable it at rest. On pooled pieces, create the trail once and call `Trail:Clear()` after setting the new CFrame (128 pieces cost nothing measurable).

### Beams from first person (field-tested)

- Start a smoke or trail beam past the muzzle (about 10x its width), fade its first 15%, and make `Width0` about a third of `Width1`, or it fills the view and hides the crosshair.
- Soft-alpha smoke needs width and opacity together to read heavy (0.3 studs at 0.92 opacity, not 0.12 at 0.55).
- A strong energy beam: three stacked additive `Beam`s (thin white core, mid color, wide scrolling haze), `LightEmission` 1, `LightInfluence` 0, held full about 0.05 s, then thinned and faded. Pool beams between Terrain-parented attachments; skip per-shot beams on multi-pellet weapons.

### Animated surfaces, highlights and orientation

- **Animate MeshPart surfaces with `Texture` instances** (tiling in studs, scrolling with `OffsetStudsU`/`OffsetStudsV`, tint and fade via `Color3`/`Transparency`), `Decal`s for one-off art, and `Color`/`Material` ramps for glow. Scripts can't set `SurfaceAppearance` maps at runtime (`ColorMap` is plugin-only; `ColorMapContent` is plugin-writable), per-frame `TextureID` swaps are content loads, and Beams float off curved meshes. Measured: 12 animated props with 178 overlays cost about 0.3 ms of Luau a frame on screen and 0.014 ms off screen; write properties only on change, and compute heat-style states in closed form from the last event so unseen objects cost nothing.
- **`Highlight` limit is 255 at once** (Highlight reference); extra instances are silently ignored, and a disabled `Highlight` still holds a slot, so delete highlights you won't reuse. Field notes: an `Adornee` set to a Folder drew nothing with no error (use a Model or BasePart); a fill ignores scene lighting and washes out texture, so use outline-only for selection.
- **Surface-aligned CFrames:** `normal:Cross(Vector3.zAxis)` is zero on ±Z faces and `.Unit` gives NaN, so the effect vanishes. Fall back to another axis.

```luau
-- Illustrative: a CFrame on a surface whose look vector is the normal.
local function surfaceCFrame(position: Vector3, normal: Vector3): CFrame
    local reference = if math.abs(normal:Dot(Vector3.yAxis)) > 0.99 then Vector3.xAxis else Vector3.yAxis
    local right = reference:Cross(normal).Unit
    local up = normal:Cross(right).Unit
    return CFrame.fromMatrix(position, right, up, -normal)
end
```

### Shipping and verifying effect assets

- **Upload every texture.** `rbxasset://textures/vfxpreview/...` paths live in Studio's install folder, get wiped by Studio updates and never exist on live servers.
- **Decal ids are not image ids.** An Open Cloud upload with asset type Decal returns a Decal id, which fails `PreloadAsync` as a particle texture. Resolve the image id inside it (in Edit mode, `InsertService:LoadAsset(decalId)` and read the Decal's `Texture`) and preload that to `Success`.
- **A broken id fails silently.** One broken texture made every instance of an effect invisible for a whole pass. Keep source images in the repo next to their uploaded ids so you can re-upload, and include Terrain in raycasts that place ground effects.
- **Freeze to inspect.** Set `TimeScale = 0` to screenshot particles (trails keep fading, so loop their source). MCP screenshot latency of about a second misses short flashes, and heavy atmosphere can wash out an effect that looks fine in clear air, so check under the game's real lighting, in a live player view.

## Procedural motion and feel

### Springs: integrate in fixed substeps

A visual spring stepped once per frame with semi-implicit Euler (5 Hz, damping 0.75) diverged at `dt = 1/30`, growing 67x in one second (field-measured). Unfocused Studio windows and slow phones run that slow. Substep stiff motion at a fixed rate and clamp `dt`:

```luau
-- Illustrative critically/under-damped spring with fixed substeps.
export type Spring = { x: number, v: number, target: number, freq: number, damping: number }

local SUBSTEP = 1 / 240
local MAX_DT = 0.1

local function stepSpring(s: Spring, dt: number)
    local remaining = math.min(dt, MAX_DT)
    local w = 2 * math.pi * s.freq
    while remaining > 0 do
        local h = math.min(SUBSTEP, remaining)
        local accel = w * w * (s.target - s.x) - 2 * s.damping * w * s.v
        s.v += accel * h
        s.x += s.v * h
        remaining -= h
    end
end

return stepSpring
```

### Feel values that passed playtests (field-tested, first person)

- **Viewmodel lag:** underdamped springs about 2.6 Hz, damping 0.4, scaled by tool heft; view lag about 0.025 x angular speed, capped at 0.08 rad; a figure-8 walk bob scaled by speed / 16, faded to 0 during strikes and hitstop.
- **Camera kick:** a non-oscillating pulse `x * e^(1 - x)` with `x = t / peak` (peak about 0.05 s), with a randomized shape per hit (pitch x0.75-1.2, yaw ±0.7 x pitch, roll toward the swinging hand). A fixed direction read as "too linear".
- **Struck heavy props:** a stiff near-critical spring (5 Hz, damping 0.75, small amplitude); set the spring's velocity on each hit rather than adding to it.
- **Recoil that never piles up:** a fast spring minus a slower, bouncier spring pushed by the same amount snaps out in about 35 ms, dips slightly below rest and settles in about 0.3 s, so held fire rattles about rest. Keep a small camera knock (about a degree) on the same springs; zero camera recoil felt dead. Guard "no pile-up at 3x fire rate" with a unit test.
- **Build stances from target axes, not guessed Euler angles:** decide where the grip sits and which way the striking face points, then `CFrame.fromMatrix(pos, up:Cross(-face), up, -face)`; read `ToEulerAnglesXYZ` back only if you must store angles.

### First-person viewmodels (field-tested across many tools)

- Judge a viewmodel through the live player camera at the game's FOV and at 16:9 and 21:9, never from stock render angles, and don't ship hold or motion changes nobody watched in the running game.
- Size the tool against the visible arm (forearm at most about twice the tool's thickest part); hold every tool at the same camera distance (about 1.7 studs); aim gun-like tools at a point 9-20 studs down the view axis with zero roll.
- A viewmodel that clips walls is usually a big model held far out: bake it smaller (x0.6) and hold it closer, which looks identical; for the rest, sphere-cast from the eye to the far end and dip the nose about the grip.
- Make each arm's far end leave the screen in every frame of every clip; key where the gun and hands go and solve arms from hand to shoulder rather than keying arms by hand.
- R15 details: `RightShoulderRigAttachment` sits on the upper arm's outer edge, not its axis; the `RightGripAttachment` +Y points out of the front of the fist. Cloned arms show the player's shirt only inside a model with a `Humanoid` of `RigType` R15 and R15 part names, and each sleeve maps through its own limb mesh's UVs, so a mirrored right arm renamed `LeftUpperArm` shows bare skin. Clothing can arrive after the tool script starts: re-dress the viewmodel when a `Shirt` or `BodyColors` is added.

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
- [ ] Joint code accepts `AnimationConstraint` as well as `Motor6D`; procedural poses write `Transform` in `PreSimulation`.
- [ ] Effect templates carry their own timing attributes; concurrent effects are capped and non-essential layers scale with a budget.
- [ ] Every texture is uploaded (no `rbxasset://` preview paths) and preloads to `Success` from its image id.

## Community ecosystem (leads, not sources)

- [How to animate Tool Parts](https://devforum.roblox.com/t/how-to-animate-tool-parts-guns-knifes-etc/359484) (3.1k likes) and [Jespone's guide to animations](https://devforum.roblox.com/t/jespones-guide-to-animations/225752): the tool-animation canon; [Blender rig exporter](https://devforum.roblox.com/t/blender-rig-exporteranimation-importer/34729) for the art pipeline.
- VFX: [Hidden glass distortion w/ real-time reflections](https://devforum.roblox.com/t/hidden-glass-distortion-effect-with-real-time-reflections-tutorial/2338789); [Wind Shake](https://devforum.roblox.com/t/wind-shake-high-performance-wind-effect-for-leaves-and-foliage/1039806) foliage motion; [Realism pack](https://devforum.roblox.com/t/realism-%E2%80%94-make-your-games-feel-more-immersive/898642) (1.8k likes).

## Sequence and hydrate effects explicitly

- Discovery of a replicated model does not establish that its required parts or effect metadata have arrived. Define the readiness contract, use bounded waits or arrival-driven checks, and apply presentation idempotently when the requirements are met. Cancel pending work when the model is removed; test a retained corpse after the victim respawns as well as the immediate local effect.
- Sequence phases that tween the same property. Starting a later tween with `TweenInfo.DelayTime` does not provide a safe ownership queue: competing tweens can cancel the earlier tween. Start the next phase after the prior phase actually completes under the current owner, and cancel the whole sequence when that owner ends. Inspect rise, hold, and exit visually; correct final properties alone do not prove the entrance rendered.
