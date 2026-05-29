---
name: roblox-economy
description: Currency design, faucets/sinks, inflation control, time-to-earn, trading systems.
last_reviewed: 2026-05-27
---

## When to Load

Load when designing currency systems, balancing rewards, creating trading/marketplace systems, or diagnosing inflation/deflation in an existing game. Also relevant for monetization integration (GamePasses, battle passes, premium currency).

## Quick Reference

### Currencies (max 3)
- **Soft** (Gold): gameplay-earned, primary transactions
- **Premium** (Gems): rare/purchased with Robux, exclusive items
- **Tokens** (Event Points): limited-time, expires per event

### Faucets ↔ Sinks Balance
**Faucets:** quests, daily login, drops, PvP wins, selling items, achievements, rebirth
**Sinks:** purchases, upgrades, repairs (10-20% tax), cosmetics, consumables, gacha
- Faucets > Sinks → inflation (currency worthless)
- Sinks > Faucets → deflation (new players stuck)

### Time-to-Earn Targets
| Goal | Time |
|------|------|
| Early (first hour) | 5-15 min |
| Session | 30-60 min |
| Multi-session | 2-5 hrs |
| Long-term | 10-50 hrs |
| Prestige | 100+ hrs |

**Rule:** meaningful progress every 30-60 seconds.

### Inflation Control
Hard sinks, variable pricing, seasonal resets, luxury goods, 10-20% trade tax, durability costs, prestige/rebirth resets.

### Trading Rules
- **Atomic**: both sides complete or neither does (server-side)
- **Double confirm**: propose → review → confirm
- **Value warnings** on rarity mismatches
- **Trade cooldowns** + server-side logging for rollback
- **Tax**: 10-20% removed per transaction

### Monetization
- Never sell soft currency for Robux (instant inflation)
- Premium currency → exclusive items or time-skips (not power)
- 2x Gold passes = inflation accelerators; cap or scale prices
- Cosmetic-only passes = safest (zero economy impact)
- Battle pass: unconverted premium currency expires end-of-season (sink)

### Health Metrics
Track: earn rate by level, sink participation %, currency stockpile distribution, time-to-first-purchase, trade volume.

### Common Mistakes
Infinite faucets/finite sinks · rewarding AFK · linear scaling without price scaling · no early wins · tradeable premium currency · no trade tax

📖 Full reference: `references/full.md`
