# Task 021: Write genre-tycoon.md

**depends-on:** 001
**phase:** 4 - Genre Templates
**files:** `templates/genre-tycoon.md`

## Description

Write a complete tycoon genre template. Tycoons are about building and managing an empire with incremental progression.

## What To Do

1. **Genre Overview** — Core loop: earn → purchase → build → automate → expand. Examples: Retail Tycoon 2, Restaurant Tycoon 2
2. **Architecture Blueprint** — TycoonManager, PlotSystem, DropperSystem, UpgradeTree, ConveyorSystem
3. **Core Systems (Luau code):**
   - Plot assignment (claim a plot, per-player base area)
   - Dropper/collector system (automated resource generation)
   - Build button pads (step on pad → purchase building)
   - Upgrade tree (unlock tiers of buildings/machines)
   - Income system (passive + active earning)
4. **Progression Design** — Building unlock order, cost scaling, income balancing, prestige tiers
5. **Monetization Strategy** — Auto-collect, 2x income GamePass, exclusive buildings, skip tiers
6. **Performance Considerations** — Many parts per tycoon base, instancing, streaming per-plot
7. **Launch Checklist** — Tycoon-specific items

## Verification

- File exists at `templates/genre-tycoon.md`
- Plot system with per-player bases implemented
- Dropper/collector with build pad pattern in Luau
- Progression balancing documented
