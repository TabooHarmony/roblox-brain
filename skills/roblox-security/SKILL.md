---
name: roblox-security
description: "Use when auditing Roblox code for exploit vectors, authority models, remotes, economy, and DataStore flows."
last_reviewed: 2026-08-21
sources:
  - https://create.roblox.com/docs/scripting/security/security-tactics
  - https://create.roblox.com/docs/scripting/security/client-server-boundary
  - https://create.roblox.com/docs/projects/server-authority
  - https://create.roblox.com/docs/projects/server-authority/techniques
  - https://devforum.roblox.com/t/server-authority-client-beta-was-a-damn-nightmare-heres-some-advice/4712758
  - https://gist.githubusercontent.com/TheGreatSageEqualToHeaven/e0e1dc2698307c93f6013b9825705899/raw/51c04e2d8a28b0e66d2dae0898f6ca9d32cf9a8f/READ.md
---

# Roblox Security

## When to Load

Load for exploit audits and hardening. Covers classic replication, opt-in Server Authority, remote abuse, economy attacks, and DataStore flows. Use `roblox-networking` for validation and rate-limit implementations.

## Quick Reference

**Core:** Client is always compromised. The server remains the source of truth, but the implementation depends on the authority model.

### Authority Models

- **Classic replication:** validate client requests and custom movement against server state. Never trust client damage, currency, inventory, permissions, or positions.
- **Server Authority:** with `Workspace.AuthorityMode = Server`, the server owns core simulation while clients predict and recover from misprediction. Use `BindToSimulation()` (requires `Workspace.UseFixedSimulation`), not blanket `Heartbeat` CFrame correction. Migration is cheap for stock characters but a rewrite-scale commitment for authored simulation (reality check in full.md).
- **Both:** validate attacks, purchases, teleports, dashes, permissions, and custom remotes at the server boundary.

### Audit Checklist

**CRITICAL:** Server-authoritative state · Choose and document the authority model · Validate all arg types · Rate limit remotes · Session-lock DataStore · No client currency mutations · ProcessReceipt verification · No secrets in client or replicated code

**HIGH:** Validate custom movement and action transitions · BindToClose protection · Atomic trading · Never trust client values · Use InputActions for simulation input in Server Authority projects

**MEDIUM:** Server cooldowns · server-computed leaderboards · anti-AFK reward checks · TextService filtering

### Anti-Patterns

Don't obfuscate client code, use `_G` for security, kick without logging, over-validate movement, or rely on client anti-cheat.

See `references/full.md` for detailed examples.
