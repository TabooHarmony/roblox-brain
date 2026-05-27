---
name: roblox-game-design
description: >
  Genre-specific game design patterns for Roblox: tycoon, simulator, obby, horror, RPG,
  battle royale. Core loops, progression curves, retention hooks, session design.
  Use when designing a new game or evaluating an existing game's design.
last_reviewed: 2026-05-27
---

# Roblox Game Design

Use this skill when designing a new game, choosing a genre, structuring a core loop, or evaluating why an existing game isn't retaining players.

## Core Loop Design

Every successful Roblox game has a tight core loop that delivers reward within 30-60 seconds:

```
ACTION → REWARD → UPGRADE → (stronger) ACTION
```

The loop must be satisfying on the FIRST cycle. If the player doesn't feel progress in 60 seconds, they leave.

## Genre Patterns

### Simulator

**Core loop**: Click/tap → earn currency → buy upgrade → earn faster

**Key systems**:
- Rebirth/prestige (reset for permanent multiplier)
- Pet/companion system (collectible power multipliers)
- Area unlocks (spend currency to access new zones with better rates)
- Leaderboards (competitive motivation)

**Retention hooks**:
- Daily rewards escalating over consecutive days
- Limited-time events with exclusive pets/items
- Group rewards (join group for bonus)
- Codes system (social media engagement)

**Pacing**:
- First rebirth: 15-30 minutes
- Each subsequent rebirth: 1.5-2x longer
- New area unlock every 5-10 minutes early, 30-60 minutes late

**Common mistakes**:
- No prestige system (players hit ceiling and leave)
- Linear scaling (should be exponential with resets)
- Too many currencies (max 2-3)

### Tycoon

**Core loop**: Build → earn passive income → expand → unlock new machines

**Key systems**:
- Conveyor/dropper mechanics (visual income)
- Upgrades (speed, value multipliers)
- Expansion plots (buy adjacent land)
- PvP element (optional: raid other tycoons)

**Retention hooks**:
- Offline earnings (capped, incentivizes return)
- Research tree (long-term goals)
- Cosmetic customization of tycoon
- Collaborative tycoons (play with friends)

**Pacing**:
- First machine: immediate (tutorial)
- First expansion: 5-10 minutes
- Full base: 2-4 hours
- Prestige/rebirth: 4-8 hours

### Obby (Obstacle Course)

**Core loop**: Attempt → fail → learn → succeed → checkpoint

**Key systems**:
- Checkpoint system (never lose more than 30 seconds of progress)
- Difficulty curve (gradual ramp, not cliff)
- Skip stage (premium currency or earned tokens)
- Cosmetic trails/effects for completion

**Retention hooks**:
- Daily stages (new content each day)
- Speedrun timer + leaderboard
- Difficulty modes (easy/hard paths)
- Social racing (compete with friends in real-time)

**Pacing**:
- Stages 1-5: trivial (build confidence)
- Stages 6-15: moderate (teach mechanics)
- Stages 16-30: hard (test mastery)
- Stages 31+: expert (bragging rights)
- Each stage: 15-60 seconds to complete

**Common mistakes**:
- No checkpoints (rage quit)
- Difficulty spike too early (lose casual players)
- No visual progress indicator (players don't know how far they are)

### Horror

**Core loop**: Explore → discover clue → encounter threat → survive/escape

**Key systems**:
- Atmosphere (lighting, sound, camera effects)
- Monster AI (patrol, chase, search states)
- Objective system (find X keys, solve puzzle)
- Multiplayer roles (optional: one player is the monster)

**Retention hooks**:
- Multiple endings based on choices
- Unlockable lore/backstory
- Harder difficulty modes
- Cosmetic survivor skins

**Pacing**:
- First 2 minutes: atmosphere building (NO jumpscares)
- 2-4 minutes: first sign something is wrong
- 4-6 minutes: first encounter (survivable)
- 6-10 minutes: escalating tension
- 10-15 minutes: climax/escape
- Total session: 10-20 minutes per round

**Common mistakes**:
- Jumpscare in first 30 seconds (desensitizes player)
- Monster always visible (not scary, just annoying)
- No safe moments (constant tension = no tension)
- Too dark to see anything (frustrating, not scary)

### RPG / Adventure

**Core loop**: Quest → combat → loot → level up → harder quest

**Key systems**:
- Class/ability system (player identity)
- Inventory with rarity tiers
- Quest log with main + side quests
- Party/group system for dungeons
- Boss encounters with mechanics

**Retention hooks**:
- Daily quests (quick, rewarding)
- Weekly dungeon resets
- Seasonal events with exclusive gear
- Guild/clan system
- Achievement collection

**Pacing**:
- Level 1-5: tutorial zone (30-60 minutes)
- Level 5-15: first region (2-4 hours)
- Level 15-30: mid-game (8-15 hours)
- Level 30+: endgame (ongoing)
- Each quest: 5-15 minutes

### Battle Royale

**Core loop**: Drop → loot → fight → survive → win/die → queue again

**Key systems**:
- Shrinking zone (forces encounters)
- Loot distribution (floor loot + chests)
- Weapon rarity tiers
- Building/fortification (optional)
- Respawn mode (for casual players)

**Retention hooks**:
- Battle pass with cosmetic rewards
- Ranked mode with visible rank
- Squad mode (play with friends)
- Limited-time modes (variety)

**Pacing**:
- Match length: 8-15 minutes
- First loot: within 10 seconds of landing
- First encounter: 1-3 minutes
- Zone shrink starts: 2-3 minutes
- Final circle: 8-12 minutes

## Session Design

### First-Time User Experience (FTUE)

The first 60 seconds determine if a player stays:

1. **0-5 seconds**: Player sees something visually interesting (not a loading screen)
2. **5-15 seconds**: Player understands what to do (clear UI prompt or obvious interaction)
3. **15-30 seconds**: Player does the core action for the first time
4. **30-60 seconds**: Player receives first reward/feedback

**Rules**:
- No text walls. Show, don't tell.
- No forced tutorials longer than 2 minutes.
- Let the player DO something immediately.
- First reward should feel generous (hook them).

### Session Length Targets

| Audience | Target Session | Design For |
|----------|---------------|-----------|
| Casual mobile | 5-15 minutes | Quick loops, save anywhere |
| Core mobile | 15-30 minutes | Session goals, daily rewards |
| Desktop casual | 30-60 minutes | Multiple objectives per session |
| Desktop core | 1-3 hours | Deep progression, social play |

### Retention Mechanics

- **Daily rewards**: Escalating value over consecutive days (day 7 = big reward)
- **Streaks**: Bonus for consecutive days (but don't punish missing one day too harshly)
- **Limited events**: FOMO drives return visits
- **Social hooks**: Friends playing = reason to return
- **Unfinished business**: End session with a visible goal almost reached

## Roblox-Specific Considerations

- **Mobile-first**: 60%+ of players are on phones. Design for touch, small screens, short sessions.
- **Young audience**: Average age 9-15. Simple UI, clear feedback, no complex text.
- **Discovery**: Roblox algorithm favors play time and return rate. Design for retention, not just acquisition.
- **Monetization ceiling**: Most players spend $0. Design the free experience to be complete. Premium = convenience/cosmetics.
- **Group play**: Friends playing together increases retention 3-5x. Always support multiplayer.
- **Updates**: Games that update weekly retain 2-3x better than static games. Plan for live service.
