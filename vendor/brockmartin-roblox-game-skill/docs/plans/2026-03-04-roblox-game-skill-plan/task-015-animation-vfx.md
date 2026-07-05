# Task 015: Write animation-vfx.md

**depends-on:** 001
**phase:** 3 - Specialized References
**files:** `references/animation-vfx.md`

## Description

Write an animation and VFX reference covering character animation, particle effects, visual polish, and sound design integration.

## What To Do

1. **Overview** — When to load (animation work, visual effects, particles, polish)
2. **Character Animation** — Animator service, loading animations, playing/stopping, animation priorities (Idle < Movement < Action < Core), animation events, blending
3. **Animation Controller** — AnimationController for non-humanoid objects, NPC animations, custom rigs
4. **Particle Effects** — ParticleEmitter properties (Rate, Lifetime, Speed, Size, Color, Texture), common effects (fire, smoke, sparkles, rain, snow), performance budgets
5. **Beam and Trail** — Beam (between two Attachments), Trail (follows movement), properties and styling, common uses (laser, sword trail, magic effects)
6. **TweenService for VFX** — Tweening part properties (Size, CFrame, Color, Transparency), creating visual feedback (flash on hit, pulse, grow/shrink), easing styles
7. **Lighting Effects** — PointLight, SpotLight, SurfaceLight, Atmosphere, ColorCorrection, Bloom, global lighting for mood
8. **Sound Design** — Sound objects, SoundService, positional audio, sound groups, triggering sounds with animations/effects
9. **Camera Effects** — Camera shake, zoom, focus transitions, cutscenes with TweenService
10. **Best Practices** — Performance budgets for particles, disable effects on low-end, pool VFX objects, sync sound with visual
11. **Anti-Patterns** — Too many particles, unoptimized textures, synchronous animations blocking gameplay

Include Luau code for a hit effect system (flash + particles + sound + camera shake).

## Verification

- File exists at `references/animation-vfx.md`
- Character animation system covered with priority levels
- Particle effects include performance guidance
- Complete hit effect system in Luau
- Sound integration included
