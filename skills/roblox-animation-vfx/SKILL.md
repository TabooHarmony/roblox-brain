---
name: roblox-animation-vfx
description: "Use when implementing Roblox character animations, particles, beams, trails, tweens, camera shake, or other visual effects."
last_reviewed: 2026-07-12
sources:
  - https://create.roblox.com/docs/animation/using
  - https://create.roblox.com/docs/reference/engine/classes/Animator
  - https://create.roblox.com/docs/reference/engine/classes/ParticleEmitter
  - https://create.roblox.com/docs/reference/engine/classes/TweenService
  - original
---

# roblox animation and vfx

## When to Load

Load when implementing character animation, particle or beam effects, tweens, camera feedback, or visual cleanup.

## Quick Reference

- Load tracks through an `Animator` on a `Humanoid` or `AnimationController`.
- Use priorities and marker signals to coordinate animation with gameplay and effects.
- A burst emitter usually has `Rate = 0` and uses `:Emit(count)`.
- Beams and trails need two attachments with a meaningful world-space relationship.
- Tween a bounded set of properties and cancel or destroy temporary effects when their owner ends.
- Profile particle counts, lights, post-processing, and per-frame camera work on the target device class.

**Need the details?** Load `references/full.md` for animation and effect recipes.
