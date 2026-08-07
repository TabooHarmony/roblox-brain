# Roblox level design — full reference

> This skill covers the player-facing spatial layer. Code and geometry examples remain illustrative; verify the actual experience in Studio.

## 1. Define the space's job

Before opening a build tool, write a short level brief:

- **player promise:** what the player should feel or understand here;
- **core interaction:** what they repeat minute to minute;
- **first meaningful action:** the first action that demonstrates the promise;
- **space job:** teach, route, stage combat, support collection, create social visibility, or provide a destination;
- **success and recovery:** what completion looks like and where the player goes after failure or interruption;
- **evidence required:** structural readback, player-view capture, traversal playtest, runtime telemetry, or an experiment.

The brief keeps geometry, UI, effects, and progression connected without pretending that a static map proves the player experience.

## 2. Build a route graph before decoration

Represent a level as a graph of named spaces rather than a list of props. For every zone or node, record:

- role and expected player state on entry;
- entry points, exits, alternate routes, and return path;
- first visible landmark and the next intended destination;
- required interaction, affordance, and feedback;
- blockers, hazards, reset points, and recovery behavior;
- player scale, path width, occupancy, and camera constraints.

Then trace the minimum player path:

```text
spawn → orient → first meaningful action → feedback → short-term goal → return or next zone
```

Check the graph for a missing exit, a dead-end after success, a spawn that points at a wall, a reward that strands the player, and a shortcut that bypasses the intended first lesson. `roblox-building` owns the geometry implementation and bounds readback; this skill owns whether the built space supports the intended route.

## 3. Landmarks and sightlines

A landmark is useful when it helps the player answer “where am I?” or “where should I go?” Do not make every object a landmark. For each important destination:

1. choose a distinctive silhouette, height, color/material contrast, light, sound, or motion cue;
2. check that it is visible from the spawn and from the preceding decision point;
3. check the player's actual camera height, field of view, occlusion, and device viewport;
4. provide a nearer confirmation cue when the destination is too distant to read;
5. verify that decorative repetition does not erase the distinction.

Use `roblox-camera`, `roblox-lighting`, and `roblox-audio` for implementation-specific work. A landmark that exists in the instance tree but cannot be seen or interpreted is not a completed navigation cue.

## 4. Interaction affordances

The object class is not the affordance. A `ProximityPrompt`, `ClickDetector`, `Highlight`, `BillboardGui`, sign, or effect must agree with the action the player can take:

- the target is visible or discoverable from the approach path;
- the activation distance fits the path width and camera framing;
- the cue names or demonstrates the action without requiring a long paragraph;
- locked, unavailable, completed, and cooldown states are visibly distinct;
- the cue disappears, changes, or points elsewhere after completion;
- the player receives world, UI, audio, or VFX feedback that confirms the result;
- the server or simulation state, not the cue, decides whether the action succeeded.

For prompts and world UI, inspect `Adornee`, attachment, offset, occlusion, input mode, and cleanup. For highlights and effects, verify that the target remains correct after streaming, respawn, or model replacement.

## 5. Spawn and first-session flow

A spawn is a flow entry point, not only a `SpawnLocation` instance. Review each intended spawn from the actual player camera:

- what is visible in the first second;
- whether the player can identify a destination without guessing;
- whether the first action is reachable without crossing an unintended hazard;
- whether the player has a safe return path after acting;
- whether teammates, enemies, queues, or social spaces are visible when relevant;
- what happens after death, reset, teleport, or rejoin.

Use the official onboarding guidance for teaching essentials, getting to value quickly, and leaving a next goal. Prefer environmental and contextual cues when they communicate the action faster than a blocking text tutorial. A hint should be targeted to the state that needs help and should stop or transform once the player demonstrates understanding.

## 6. Feature-slice handoff

A space is not finished when the geometry is finished. For each player-facing feature, trace:

```text
world affordance → input/focus → request or simulation → authority → state change → UI/world feedback → persistence if durable
```

Use the owning skills at each boundary:

- geometry, bounds, collision, and asset provenance: `roblox-building`;
- camera framing: `roblox-camera`;
- UI layout and input modes: `roblox-gui`, `roblox-ui-design`, and `roblox-input`;
- animation, particles, beams, and feedback lifetime: `roblox-animation-vfx`;
- authority and remote contracts: `roblox-networking` and `roblox-security`;
- player saves or durable rewards: `roblox-data` and `roblox-monetization`;
- hypotheses, funnels, cohorts, and experiments: `roblox-growth-design`.

This map is a review boundary, not an invitation to duplicate every domain skill in the level-design document.

## 7. Evidence loop

Use progressive evidence:

1. **static:** read named roots, zones, spawns, prompts, billboards, highlights, bounds, paths, and ownership;
2. **player view:** capture spawn, first decision point, destination, interaction, and return path from the real camera;
3. **playtest:** perform the route with normal, failed, interrupted, and repeated states;
4. **measurement:** record time-to-first-action, route completion, abandonment, or experiment results only when runtime instrumentation exists.

A clean structural report proves what was inspected. A screenshot or video shows what the player can see. A playtest shows observed behavior in that run. A funnel or experiment is required for population-level claims.

## 8. Patterns observed in shipped games

<!-- temporal: 2026-08 -->

Shipped Roblox games signal interactability explicitly rather than leaving it to discovery: `ProximityPrompt` and `Highlight` mark what can be touched, `BillboardGui` carries labels and prompts, and `SpawnLocation` placement is treated as part of the flow. These co-occurrences justify a review recipe around spatial entry, destination cues, and interaction affordances. They do not establish that a place contains a coherent level, that the structures are reachable, or that the game is successful; static structure is not a runtime trace, and absence is not proof that a feature is missing.

Real places range from a few thousand instances to several hundred thousand. Use scoped roots and representative routes rather than unbounded dumps. Do not copy artifact names, source code, asset IDs, or unknown-provenance patterns into a trusted project.

## 9. Acceptance checklist

- [ ] The level brief names the player promise, core interaction, first meaningful action, and evidence required.
- [ ] Every zone has an entry, destination, exit, and return or recovery path.
- [ ] A player-view capture shows the intended first landmark and next action from each spawn.
- [ ] Main routes are traversable at intended player scale and do not rely on hidden collision or guessed jumps.
- [ ] Prompts, highlights, signs, billboards, effects, and UI point to real current targets and have state transitions.
- [ ] The first route teaches the intended action without an unnecessary blocking tutorial.
- [ ] Completion, failure, death, reset, teleport, streaming, and rejoin states have a deliberate destination.
- [ ] The feature slice has explicit input, authority, feedback, and persistence owners.
- [ ] Screenshots/video and playtests cover supported viewport and input variants.
- [ ] Runtime metrics are labeled as observed measurements, not inferred from static counts.

## Source notes

- Roblox Creator Hub, [Design for Roblox](https://create.roblox.com/docs/production/game-design/design-for-roblox), current platform design guidance.
- Roblox Creator Hub, [Core loops](https://create.roblox.com/docs/production/game-design/core-loops), minute-to-minute interaction, repeated actions, and progression engine.
- Roblox Creator Hub, [Onboarding](https://create.roblox.com/docs/production/game-design/onboarding), first-session goals, player funnel, and experimentation boundaries.
- Roblox Creator Hub, [Onboarding techniques](https://create.roblox.com/docs/production/game-design/onboarding-techniques), visual elements, contextual tutorials, and timed hints.
- Corpus observations: static review of a sample of shipped Roblox places, 2026-08-02. Presence counts are routing evidence only; they are not quality, licensing, retention, revenue, or production-readiness evidence.
- Original synthesis. No source code, project names, or asset identifiers from reviewed places were copied.
