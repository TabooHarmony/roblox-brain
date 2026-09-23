---
name: roblox-player-psychology
description: "Use when designing persuasion/behavior mechanics: first minute, reward schedules, streaks, pricing, RNG/pity, community loop."
last_reviewed: 2026-09-20
sources:
  - original
  - https://create.roblox.com/docs/production/monetization/paid-random-items
---

# Roblox Player Psychology

## When to Load

Load for behavior/persuasion questions: what happens in the first 60 seconds, why players return, reward schedules, streaks, pricing psychology, gamepass ladders, crate/RNG odds and pity, or turning players into a community. For structural craft (core loop, FTUE structure, level design, economy sources/sinks) load `roblox-game-design`; for dashboard diagnosis, discovery, and the algorithm load `roblox-growth-design`; for purchase implementation load `roblox-monetization`.

## Quick Reference

### First 60 seconds (50% of new players never return)

0–5s spawn in-world (no logo/cutscene) → 5–10s do the core verb → 10–30s first reward lands → 30–45s open a loop (next milestone looks close) → 45–60s taste of premium (expiring boost). Six effects: Zeigarnik (hand an incomplete goal in 10s), endowed progress (never start at zero), peak-end (best effect in minute one), cognitive load (one mechanic/one button/one goal), isolation (only the wanted action glows), reciprocity (give before the shop).

### Retention benchmarks & levers

D1 20/30/40% · D7 8/15/20% · D30 3/7/10% (good/great/excellent; compounds — 40% D1 ≈ 3× the players of 25% D1 by day 30). Low number → lever: PTR→curiosity gap/social proof; D1→Zeigarnik, endowed progress; session→flow, variable reward; D7→goal gradient, collections; D30→habit loop, social identity; conversion→anchoring, charm pricing; ARPPU→ladders, visible status.

### Hooks, pricing, RNG

Four reward schedules (fixed/variable × ratio/interval) — layer all four. Hooks: appointments, streaks with one forgiven day, rotation, shared clan goals, hook model, specific timers ("Back in 4h 32m"). Ladder: 49–99 break threshold · 199–399 convenience · 499–799 luck+power · 999+ identity. RNG: 5 tiers (55/27/12/5/1%), show the pool and pity counter. For paid RNG implementation, check current Roblox guidance in `roblox-monetization`.

> Full detail, tables, and community loop: [references/full.md](references/full.md)
