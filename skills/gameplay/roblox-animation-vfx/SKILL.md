---
name: roblox-animation-vfx
description: "Use when adding, changing, or fixing Roblox animations, particles, beams, trails, tweens, camera shake, or other visual effects."
when_to_use: "Also when an effect is invisible, too weak, laggy or doesn't clean up, an animation won't play or blend, and when reviewing game feel or hit feedback."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/reference/engine/classes/AnimationTrack
  - https://create.roblox.com/docs/animation/using
  - https://create.roblox.com/docs/reference/engine/classes/Animator
  - https://create.roblox.com/docs/reference/engine/classes/ParticleEmitter
  - https://create.roblox.com/docs/effects/particle-emitters
  - https://create.roblox.com/docs/tutorials/use-case-tutorials/vfx/create-volcanoes
  - https://create.roblox.com/docs/tutorials/use-case-tutorials/vfx/create-waterfalls
  - https://create.roblox.com/docs/reference/engine/classes/TweenService
  - https://create.roblox.com/docs/projects/server-authority
  - https://create.roblox.com/docs/projects/server-authority/techniques
  - original
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine/classes/Instance.yaml
  - https://create.roblox.com/docs/animation/graph-editor-state-machine
  - https://create.roblox.com/docs/animation/expressions
  - https://create.roblox.com/docs/reference/engine/classes/AnimationConstraint
  - https://create.roblox.com/docs/reference/engine/classes/Highlight
---

# roblox animation and vfx

## When to Load

Animation, graphs, procedural poses, particles, beams, tweens, effect cleanup. Rigs: `roblox-physics`.

## Quick Reference

**Animation**
- `Animator` under the `Humanoid` (`AnimationController` for other rigs); set `Priority`; cue effects from `GetMarkerReachedSignal()`. `Ended` = post-fade; `Stopped` includes `Stop()`.
- Animation Graphs: load like an `Animation`, drive with `track:SetParameter()`. Give competing state-machine transitions distinct priorities (ties are random).
- New R15 rigs use `AnimationConstraint`, not `Motor6D`. Multiply poses into `.Transform` in `PreSimulation`; find joints lazily, accept both.
- Server Authority: `BindToSimulation()` (needs `Workspace.UseFixedSimulation`); query tracks (`GetTrackByAnimationId`), don't cache; key predicted effects, make them reversible.

**Effects**
- Bursts: `Rate = 0` + `:Emit(n)`, timed by `EmitCount`/`EmitDelay` attributes; clean up after the longest lifetime (max 20 s).
- Phases: warning, contact, peak, fade. Silhouette first.
- Cap effects per kind; scale extra layers by frame time, not `SavedQualityLevel`; pool.
- Small additive accents need `Brightness`; `TimeScale = 0` freezes particles (hitstop, screenshots).
- Beams/trails need stable attachments and an owner. `Highlight` cap is 255; disabled ones still count.
- Upload every texture; preload the image id, not a Decal id.
- Springs: fixed substeps and clamped dt, or they explode at 30 FPS.

**Details:** `references/full.md` (graphs, joints, `EffectPlayer`, budgets, feel, viewmodels).
