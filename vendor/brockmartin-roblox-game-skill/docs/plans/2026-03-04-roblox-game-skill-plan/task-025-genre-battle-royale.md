# Task 025: Write genre-battle-royale.md

**depends-on:** 001
**phase:** 4 - Genre Templates
**files:** `templates/genre-battle-royale.md`

## Description

Write a complete battle royale genre template. Battle royale games combine survival, combat, and shrinking play areas.

## What To Do

1. **Genre Overview** — Core loop: drop → loot → survive → fight → win. Examples: BIG Paintball, Arsenal (arena variant)
2. **Architecture Blueprint** — MatchManager, ZoneManager (storm/circle), LootSpawner, CombatSystem, SpectatorSystem
3. **Core Systems (Luau code):**
   - Match lifecycle (lobby → countdown → drop → combat → victory)
   - Shrinking zone/storm system (timed circle reduction, damage outside zone)
   - Loot spawning (randomized weapon/item spawns across map, rarity tiers)
   - Elimination tracking (kill feed, placement, stats)
   - Spectator system (watch other players after elimination)
   - Drop/spawn system (choose landing spot or random spawn)
4. **Progression Design** — Match-based progression (no permanent power advantage), cosmetic unlocks, seasonal ranks, battle pass tiers
5. **Monetization Strategy** — Battle pass (seasonal), cosmetic skins, emotes, exclusive weapons (cosmetic only), lobby items
6. **Performance Considerations** — Many players in one server, weapon projectile optimization, map streaming, reduce distant player detail
7. **Launch Checklist** — BR-specific items (zone timing balance, loot distribution, min/max player counts)

## Verification

- File exists at `templates/genre-battle-royale.md`
- Match lifecycle implemented with all phases
- Shrinking zone system in Luau
- Loot spawning with rarity tiers
- Spectator system included
