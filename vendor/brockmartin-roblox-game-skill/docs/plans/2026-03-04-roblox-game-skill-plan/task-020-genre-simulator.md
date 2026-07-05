# Task 020: Write genre-simulator.md

**depends-on:** 001
**phase:** 4 - Genre Templates
**files:** `templates/genre-simulator.md`

## Description

Write a complete simulator genre template with architecture, core systems, and production-ready Luau code. Simulators are the most popular Roblox genre (Pet Simulator, Blox Fruits style).

## What To Do

Follow the genre template structure:

1. **Genre Overview** — Core loop: collect → upgrade → unlock zones → prestige/rebirth. What makes simulators addictive. Examples: Pet Simulator 99, Bee Swarm Simulator
2. **Architecture Blueprint** — Extended folder structure on top of game-scaffold: PetSystem, ZoneManager, PrestigeSystem, CollectionSystem, UpgradeManager
3. **Core Systems (Luau code):**
   - Collection mechanic (click/tap to collect resources)
   - Pet/companion system (hatch, equip, level up, rarities)
   - Zone system (unlock zones with currency, increasing rewards)
   - Upgrade system (multipliers, speed boosts, auto-collect)
   - Prestige/rebirth system (reset progress for permanent multipliers)
4. **Progression Design** — XP curves, zone unlock costs (exponential scaling), rebirth multiplier formulas, pet rarity drop rates
5. **Monetization Strategy** — Lucky egg (2x luck GamePass), auto-collect, exclusive pets, VIP zone access, currency packs (DevProducts)
6. **Performance Considerations** — Many pets on screen (use attachments not models), zone streaming, particle effect limits
7. **Launch Checklist** — Simulator-specific pre-launch items

## Verification

- File exists at `templates/genre-simulator.md`
- Core loop (collect → upgrade → unlock → prestige) implemented
- Pet system with rarity includes complete code
- Progression math (curves, formulas) documented
- Monetization strategy is genre-appropriate
