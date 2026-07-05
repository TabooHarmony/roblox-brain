# Task 011: Write combat-systems.md

**depends-on:** 001
**phase:** 3 - Specialized References
**files:** `references/combat-systems.md`

## Description

Write a combat systems reference covering hitbox detection, state machines, damage calculation, and server-authoritative combat.

## What To Do

1. **Overview** — When to load (building combat, weapons, PvP, PvE systems)
2. **Combat Architecture** — Server-authoritative model, client prediction for responsiveness, server validation for fairness
3. **Hitbox Detection** — Spatial Query API (workspace:GetPartBoundsInBox), Region3, Raycast for ranged weapons, hitbox sizing and positioning
4. **State Machines** — Player states (Idle, Attacking, Blocking, Dodging, Stunned), state transitions, cooldowns between states
5. **Damage Calculation** — Base damage, modifiers (buffs/debuffs), armor/defense, critical hits, damage types (physical, magical, elemental)
6. **Melee Combat** — Swing detection, combo systems, parry/block mechanics, knockback
7. **Ranged Combat** — Projectile systems (FastCast or custom), hitscan vs projectile, bullet drop, spread patterns
8. **WCS Framework** — Overview of Weapon Combat System framework, when to use vs custom
9. **Cooldown Systems** — Server-tracked cooldowns, client-side prediction, anti-spam
10. **Best Practices** — Server validates all damage, prevent hit registration exploits, fair PvP mechanics
11. **Anti-Patterns** — Client-side damage calculation, trusting client hitbox results, no cooldown enforcement

Include Luau code for a complete melee combat system with state machine.

## Verification

- File exists at `references/combat-systems.md`
- Server-authoritative design emphasized throughout
- Hitbox detection includes at least 2 methods with code
- State machine pattern implemented in Luau
- Complete melee combat system example
