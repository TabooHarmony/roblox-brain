---
name: roblox-animation-vfx
description: "Use when implementing Roblox character animations, particles, beams, trails, tweens, camera shake, or other visual effects."
last_reviewed: 2026-07-13
sources:
  - https://create.roblox.com/docs/animation/using
  - https://create.roblox.com/docs/reference/engine/classes/Animator
  - https://create.roblox.com/docs/reference/engine/classes/ParticleEmitter
  - https://create.roblox.com/docs/reference/engine/classes/TweenService
  - https://create.roblox.com/docs/projects/server-authority
  - https://create.roblox.com/docs/projects/server-authority/techniques
  - original
---

# roblox animation and vfx

## When to Load

Load when implementing character animation, particle or beam effects, tweens, camera feedback, or visual cleanup.

## Quick Reference

- Load tracks through an `Animator` on a `Humanoid` or `AnimationController`; set `AnimationTrack.Priority` deliberately.
- Use `GetMarkerReachedSignal()` for named gameplay or presentation cues, then disconnect or replace the listener when the track ends.
- A burst `ParticleEmitter` usually has `Rate = 0` and uses `:Emit(count)` with a bounded lifetime; use pooling for frequent effects.
- Beams and trails need two attachments with a stable world-space relationship and a cleanup owner.
- Tween a bounded set of properties with `TweenService:Create`; cancel or destroy temporary effects when their owner ends, and use `Debris:AddItem` for simple lifetimes.
- In Server Authority projects, keep synchronized animation logic in `RunService:BindToSimulation()`, query current tracks instead of caching handles across rollback, and make predicted effects reversible.
- Profile particle counts, lights, post-processing, and per-frame camera work on the target device class.

**Need the details?** Load `references/full.md` for animation and effect recipes.
