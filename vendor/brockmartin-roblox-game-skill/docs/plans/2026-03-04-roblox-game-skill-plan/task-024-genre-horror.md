# Task 024: Write genre-horror.md

**depends-on:** 001
**phase:** 4 - Genre Templates
**files:** `templates/genre-horror.md`

## Description

Write a complete horror genre template. Horror games on Roblox focus on atmosphere, tension, and social scares.

## What To Do

1. **Genre Overview** — Core experience: explore → build tension → scare → survive. Examples: Doors, The Mimic, Apeirophobia
2. **Architecture Blueprint** — AtmosphereManager, MonsterAI, EventSequencer, JumpscareSystem, SoundManager
3. **Core Systems (Luau code):**
   - Atmosphere system (dynamic lighting, fog, color correction, ambient sounds)
   - Monster/enemy AI (patrol paths, chase behavior, line of sight, hiding mechanics)
   - Event sequencer (scripted scare events, triggered by proximity/time)
   - Jumpscare system (camera control, sound stinger, visual effect, cooldown)
   - Flashlight/limited resource system (battery drain, item pickup)
   - Door/key system (locked doors, key items, puzzle elements)
4. **Progression Design** — Room/level progression, increasing difficulty, narrative reveals, multiple endings
5. **Monetization Strategy** — Revive tokens, exclusive character skins, bonus chapters, flashlight upgrades
6. **Performance Considerations** — Dynamic lighting is expensive, pre-bake where possible, optimize fog rendering
7. **Launch Checklist** — Horror-specific items (jumpscare timing, sound mixing, pacing review)

## Verification

- File exists at `templates/genre-horror.md`
- Atmosphere system with lighting/fog code
- Monster AI with chase behavior in Luau
- Jumpscare system with camera control
- Sound design integration documented
