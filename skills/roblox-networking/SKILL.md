---
name: roblox-networking
description: >
  Server-authoritative networking, RemoteEvent validation, rate limiting, exploit prevention,
  security hardening.
last_reviewed: 2026-05-22
---

<!-- Source: brockmartin/roblox-game-skill (MIT) -->

# Roblox Networking & Security Reference

---

## Overview

**Load this reference when:**

- Validating RemoteEvent/RemoteFunction input on the server
- Implementing rate limiting or anti-exploit measures
- Designing server-authoritative systems (damage, currency, inventory)
- Hardening existing networking code against exploiters

This document covers server-side validation, rate limiting, suspicion scoring, and server-authoritative design patterns. For player lifecycle (PlayerAdded/Removing), see **roblox-architecture**.

---

## Quick Reference

**Load Full Reference below only when you need specific validation module code or rate limiting implementations.**

Key rules:
- NEVER trust the client. Every RemoteEvent arg is attacker-controlled.
- Validate: type, range, ownership, cooldown on EVERY server handler.
- Server-authoritative: server decides outcomes. Client is display-only.
- Rate limit all remotes. Per-player cooldown table minimum.
- Damage: server calculates from weapon stats + distance + cooldown. Never accept damage values from client.
- Currency: all math server-side. Client displays only.
- Movement: validate distance/speed against physics. Flag teleportation.
- Use `t` library for composable type checks on remote args.
- Suspicion scoring: accumulate violations, kick/ban at threshold. Don't instant-kick on first offense.
- Exploiters can: fire any remote, read all client code, modify any client state, speed/fly/teleport.
**Need more detail?** Load `references/full.md` for the complete reference with code examples, API tables, and edge cases.
