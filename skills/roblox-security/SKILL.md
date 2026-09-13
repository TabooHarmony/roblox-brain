---
name: roblox-security
description: "Use when auditing Roblox code for exploit vectors, authority models, remotes, economy, and DataStore flows."
last_reviewed: 2026-09-13
sources:
  - https://create.roblox.com/docs/scripting/security/security-tactics
  - https://create.roblox.com/docs/scripting/security/client-server-boundary
  - https://create.roblox.com/docs/projects/server-authority
  - https://create.roblox.com/docs/projects/server-authority/techniques
  - https://create.roblox.com/docs/reference/engine/classes/Players
  - https://create.roblox.com/docs/scripting/capabilities
---

# Roblox Security

## When to Load

Load for exploit audits and hardening: authority models, remote abuse, economy, DataStore flows, native bans, sandboxing. Use `roblox-networking` for validation and rate limiting.

## Quick Reference

**Core:** Client is always compromised. The server remains the source of truth, but the implementation depends on the authority model.

### Authority Models

- **Classic replication:** validate client requests against server state. Never trust client damage, currency, inventory, permissions, or positions.
- **Server Authority:** `Workspace.AuthorityMode = Server`: the server owns core simulation while clients predict and recover from misprediction. Use `BindToSimulation()` (needs `UseFixedSimulation`), not blanket `Heartbeat` correction. Cheap for stock characters, rewrite-scale for authored simulation (full.md).
- **Both:** validate attacks, purchases, teleports, permissions, and custom remotes at the server boundary.

### Audit Checklist

**CRITICAL:** Server-authoritative state · Documented authority model · Validate all arg types · Rate limit remotes · Session-lock DataStore · No client currency mutations · ProcessReceipt verification · No secrets in client code

**HIGH:** Validate custom movement and action transitions · BindToClose protection · Atomic trading · Never trust client values · Use InputActions for simulation input in Server Authority projects · Validate ProximityPrompt/ClickDetector/DragDetector like remotes

**MEDIUM:** Server cooldowns · server-computed leaderboards · anti-AFK reward checks · TextService filtering · Script sandboxing for third-party code

### Enforcement

Enforcement is a product decision with appeal implications, not an automatic response. The native ban API is server-only (`Players:BanAsync` / `UnbanAsync` / `GetBanHistoryAsync`; `Players.BanningEnabled` must be on). `Duration` `-1` is permanent, `0` and other negatives are invalid; `DisplayReason` max 400 chars (filtered); `PrivateReason` max 1000, never client-shared; `ApplyDeviceBlock` lasts 24 hours and only `UnbanAsync` lifts it. Escalate via ban history; `pcall` every call (throttled HTTP). BanConfigType fields in full.md.

### Anti-Patterns

Don't obfuscate client code, use `_G` for security, kick without logging, over-validate movement, or rely on client anti-cheat.

See `references/full.md` for detailed examples.
