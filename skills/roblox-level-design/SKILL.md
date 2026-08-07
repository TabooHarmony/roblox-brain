---
name: roblox-level-design
description: "Use when designing player-facing Roblox spaces, traversal, landmarks, affordances, spawn flow, or spatial onboarding."
last_reviewed: 2026-08-07
sources:
  - https://create.roblox.com/docs/production/game-design/design-for-roblox
  - https://create.roblox.com/docs/production/game-design/core-loops
  - https://create.roblox.com/docs/production/game-design/onboarding
  - https://create.roblox.com/docs/production/game-design/onboarding-techniques
  - https://create.roblox.com/docs/production/experiments
  - original
---

# roblox level design

## When to Load

Load for player-facing map layout, traversal, zones, landmarks, sightlines, affordances, spawn flow, environmental onboarding, or spatial readability. Use `roblox-building` for constructing geometry and `roblox-growth-design` for funnels, experiments, and measured player outcomes.

## Quick Reference

- Start with the player promise, core interaction, first meaningful action, and the space's job before placing decoration.
- Divide the space into named zones with an entry, destination, return path, landmark, affordance, and failure/recovery path.
- Design a route graph: spawn → first useful action → short-term goal → return or next zone. Check path width, blockers, dead ends, shortcuts, and sightlines from the player's camera.
- Make interaction readable in the world. Match prompts, highlights, billboards, signs, lighting, audio, and UI to the actual target, distance, state, and camera view.
- Treat spawn placement as a player-flow decision. Verify where the player looks, what they can reach, and how they return after the first action.
- Hand construction to `roblox-building`; keep the level brief and acceptance gates separate from geometry implementation.
- Validate with player-view screenshots or video, traversal playtests, and device/input variants. Static structure is a routing signal, not proof of readability, fun, or retention.

### Routing from shipped games

<!-- temporal: 2026-08 -->

In shipped Roblox games, spatial affordances are usually signposted rather than left to discovery: `ProximityPrompt` and `Highlight` mark interactables, `BillboardGui` carries labels, and spawn placement is treated as part of the flow. Use these as prompts to inspect spatial affordances and spawn flow, not as required design patterns.

**Need the details?** Load `references/full.md` for route graphs, affordance checks, player-view acceptance, and patterns observed in shipped games.
