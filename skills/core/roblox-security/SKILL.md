---
name: roblox-security
description: "Use when auditing or hardening Roblox code against exploits: authority, remotes, economy, purchases, and DataStore flows."
when_to_use: "Also for security reviews, cheaters or exploiters, duplicated items or currency, trusting client values, admin commands, and pre-release audits."
last_reviewed: 2026-11-27
sources:
  - https://create.roblox.com/docs/ui/text-filtering
  - https://create.roblox.com/docs/scripting/security/security-tactics
  - https://create.roblox.com/docs/scripting/security/client-server-boundary
  - https://create.roblox.com/docs/projects/server-authority
  - https://create.roblox.com/docs/projects/server-authority/techniques
  - https://create.roblox.com/docs/reference/engine/classes/Players
  - https://create.roblox.com/docs/scripting/capabilities
  - https://create.roblox.com/docs/scripting/security/device-trust
  - original
  - https://create.roblox.com/docs/reference/engine/classes/Player
  - https://create.roblox.com/docs/reference/engine/classes/SocialService
---

# Roblox Security

## When to Load

Load for authority, remote abuse, economy, saves, bans, or sandboxing audits. Remote validation/rate limits: `roblox-networking`.

## Quick Reference

**Core:** Client is always compromised. The server remains the source of truth, but the implementation depends on the authority model.

### Authority Models

- **Classic replication:** validate client requests against server state. Never trust client damage, currency, inventory, permissions, or positions.
- **Server Authority:** `Workspace.AuthorityMode = Server`: the server owns core simulation while clients predict and recover from misprediction. `BindToSimulation()` (needs `UseFixedSimulation`), not `Heartbeat` fixes.
- **Both:** validate attacks, purchases, teleports, permissions, and custom remotes at the server boundary.

### Audit Checklist

**CRITICAL:** Server-authoritative state · Documented authority model · Validate all arg types · Rate limit remotes · Session-lock DataStore · No client currency mutations · ProcessReceipt verification · No secrets in client code

**HIGH:** Validate movement and action transitions · BindToClose · Atomic trading · InputActions for Server Authority input · Validate ProximityPrompt/ClickDetector/DragDetector like remotes

**MEDIUM:** Server cooldowns · server leaderboards · anti-AFK checks · TextService filtering · sandboxing third-party code

### Device Trust and accounts

<!-- temporal: 2026-11 -->
`Player.DeviceTrustLevel` is a risk signal: most platforms report `Unknown` today. Gate ranked modes via `IntegrityService.EvaluatePlayerDeviceTrust` with an explicit accepted set; errors and timeouts accept. Age check: `Player:PromptAgeCheck()`, `Player.AgeChecked`.

### Enforcement

`Players:BanAsync`/`UnbanAsync` are server-only and need `Players.BanningEnabled`; `pcall` them. Duration, reason limits and device blocks: full.md.

### Anti-Patterns

Don't obfuscate client code, use `_G` for security, kick without logging, over-validate movement, or rely on client anti-cheat. Lag-aware hit tolerances and shared hitboxes: full.md.

Examples: full.md.
