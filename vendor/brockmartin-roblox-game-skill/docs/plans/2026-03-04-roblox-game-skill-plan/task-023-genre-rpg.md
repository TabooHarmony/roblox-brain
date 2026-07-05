# Task 023: Write genre-rpg.md

**depends-on:** 001
**phase:** 4 - Genre Templates
**files:** `templates/genre-rpg.md`

## Description

Write a complete RPG genre template. RPGs combine character progression, combat, quests, and social features.

## What To Do

1. **Genre Overview** — Core loop: quest → fight → loot → level up → explore new area. Examples: Blox Fruits, Vesteria
2. **Architecture Blueprint** — CharacterStats, QuestSystem, CombatManager, NPCSystem, DialogSystem, ZoneManager
3. **Core Systems (Luau code):**
   - Character stat system (HP, MP, STR, DEF, level, XP)
   - XP and leveling (XP curve formulas, stat allocation)
   - Quest system (accept, track objectives, complete, rewards)
   - NPC system (spawning, AI behavior, loot drops)
   - Dialog system (NPC conversations, quest givers, choice trees)
   - Zone/map system (level-gated areas, zone transitions)
4. **Progression Design** — XP curves (quadratic or exponential), stat scaling, gear tiers, skill trees
5. **Monetization Strategy** — XP boost, exclusive classes/weapons, expanded inventory, cosmetics, premium quests
6. **Performance Considerations** — NPC count management, LOD for distant NPCs, zone streaming
7. **Launch Checklist** — RPG-specific items (balance testing, quest flow verification)

## Verification

- File exists at `templates/genre-rpg.md`
- Character stat system with leveling in Luau
- Quest system with objective tracking implemented
- NPC system with basic AI
- XP curve formulas documented
