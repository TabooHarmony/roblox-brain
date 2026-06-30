---
name: roblox-animation-vfx
description: >
  Animations, particles, tweens, ContentProvider, visual effects.
last_reviewed: 2026-05-25
sources:
  - https://github.com/brockmartin/roblox-game-skill (MIT)
---

# Animation & VFX Reference

## When to Load

Load when implementing character animations, particle/beam/trail effects, TweenService feedback, or other visual juice (camera shake, lighting pulses).

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

## Quick Reference

**Load Full Reference below only when you need specific property values, recipes, or implementation details.**

Key rules:
- Animations need uploaded AnimationIds (rbxassetid://). Never invent IDs.
- Priority order: Core < Idle < Movement < Action. Higher priority overrides lower on same track.
- Always use `Animator` (on Humanoid/AnimationController), not deprecated `Humanoid:LoadAnimation()`
- MarkerReachedSignal for syncing sounds/VFX to animation frames
- ParticleEmitter: Rate=0 + Emit(count) for burst effects. Enabled=false to stop new particles.
- Beams need Attachment0 + Attachment1. Trails need one Attachment.
- Highlight: parent to target or set Adornee. Max 255 per client. AlwaysOnTop to see through geometry.
- TweenService: create TweenInfo once, reuse. Chain with Completed event, don't nest.
- Post-processing: keep subtle. Bloom + ColorCorrection + DepthOfField cover most moods.
- Clean up: Destroy() particles/beams when done. Use Trove for lifecycle.
**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
