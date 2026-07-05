# Task 012: Write inventory-systems.md

**depends-on:** 001
**phase:** 3 - Specialized References
**files:** `references/inventory-systems.md`

## Description

Write an inventory systems reference covering item storage, equipment, trading, and server-side inventory management.

## What To Do

1. **Overview** — When to load (building inventory, items, equipment, trading)
2. **Item Data Architecture** — Item definitions (ID, name, rarity, stats, category), item instances vs templates, item metadata
3. **Inventory Storage** — Server-side inventory tables, slot-based vs list-based, stack management, capacity limits
4. **Equipment System** — Equip slots (weapon, armor, accessory), stat application on equip/unequip, visual representation
5. **Loot/Drop Systems** — Rarity weights, drop tables, random item generation, guaranteed drops, pity systems
6. **Trading System** — Trade request flow, validation (both players have items), atomic trades (all-or-nothing), trade logging
7. **Shop/Store System** — NPC shops, dynamic pricing, purchase validation, currency deduction + item grant as atomic operation
8. **DataStore Integration** — Serializing inventory to DataStore, handling large inventories, item ID references vs full data
9. **Best Practices** — Server owns all inventory state, validate all operations, log item transactions, handle edge cases (full inventory on loot)
10. **Anti-Patterns** — Client-side inventory management, trusting client item data, not validating trades server-side

Include Luau code for a complete inventory module with add/remove/equip/trade operations.

## Verification

- File exists at `references/inventory-systems.md`
- All operations are server-authoritative
- Trading system handles edge cases
- DataStore serialization pattern included
- Complete inventory module code
