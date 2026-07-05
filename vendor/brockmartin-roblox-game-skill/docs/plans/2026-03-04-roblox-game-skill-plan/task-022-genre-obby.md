# Task 022: Write genre-obby.md

**depends-on:** 001
**phase:** 4 - Genre Templates
**files:** `templates/genre-obby.md`

## Description

Write a complete obby (obstacle course) genre template. Obbys have low dev costs and high profit potential.

## What To Do

1. **Genre Overview** — Core loop: attempt → fail → learn → succeed → next level. Examples: Tower of Hell, Mega Easy Obby
2. **Architecture Blueprint** — StageManager, CheckpointSystem, ObstacleTypes, LeaderboardManager
3. **Core Systems (Luau code):**
   - Stage/checkpoint system (save progress, respawn at checkpoint)
   - Obstacle types (moving platforms, kill bricks, timed sections, disappearing platforms)
   - Stage completion tracking
   - Global and per-stage leaderboards (fastest times)
   - Skip stage system (DevProduct)
4. **Progression Design** — Difficulty curve across stages, themed worlds/sections, prestige stages
5. **Monetization Strategy** — Skip stage (DevProduct), checkpoint saves (GamePass), speed boost, trail effects, VIP stages
6. **Performance Considerations** — Obbys are typically lightweight, focus on smooth physics
7. **Launch Checklist** — Obby-specific items (playtest all stages, verify checkpoints)

## Verification

- File exists at `templates/genre-obby.md`
- Checkpoint system with respawning in Luau
- At least 4 obstacle types implemented
- Stage skip monetization pattern included
