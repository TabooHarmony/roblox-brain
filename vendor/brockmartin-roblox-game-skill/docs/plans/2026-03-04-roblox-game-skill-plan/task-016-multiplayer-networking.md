# Task 016: Write multiplayer-networking.md

**depends-on:** 001
**phase:** 3 - Specialized References
**files:** `references/multiplayer-networking.md`

## Description

Write a multiplayer and networking reference covering matchmaking, lobbies, teams, TeleportService, cross-server communication, and player management.

## What To Do

1. **Overview** — When to load (multiplayer design, matchmaking, lobbies, cross-server features)
2. **Player Management** — Players service, PlayerAdded/PlayerRemoving events, player instance lifecycle, character respawning
3. **Team Systems** — Teams service, team assignment, team-based gameplay, team balancing algorithms
4. **Lobby System** — Waiting area, ready-up mechanics, countdown, minimum player thresholds, auto-start
5. **Round-Based Games** — Round lifecycle (waiting → playing → results), intermission, map rotation, score tracking
6. **TeleportService** — Multi-place games, teleporting players between places, passing data between places (TeleportOptions), reserved servers for private matches
7. **MessagingService** — Cross-server communication, pub/sub pattern, global announcements, cross-server trading
8. **Matchmaking** — Skill-based matchmaking concepts, queue systems, ELO/MMR tracking via DataStore, party/group queuing
9. **Instance Management** — Private servers, reserved servers, VIP servers, server capacity management
10. **Best Practices** — Handle player disconnects gracefully, save data before teleport, validate player counts, anti-AFK systems
11. **Anti-Patterns** — Not handling teleport failures, losing data during server hop, unbalanced teams, no reconnection support

Include Luau code for a complete round-based game loop with lobby.

## Verification

- File exists at `references/multiplayer-networking.md`
- TeleportService patterns include data passing
- Round-based game loop implemented in Luau
- Cross-server communication documented
- Player disconnect handling covered
