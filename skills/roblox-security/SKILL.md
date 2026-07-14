---
name: roblox-security
description: "Use when auditing Roblox code for exploit vectors, authority models, remotes, economy, and DataStore flows."
last_reviewed: 2026-07-13
sources:
  - https://create.roblox.com/docs/scripting/security/security-tactics
  - https://create.roblox.com/docs/scripting/security/client-server-boundary
  - https://create.roblox.com/docs/projects/server-authority
  - https://create.roblox.com/docs/projects/server-authority/techniques
---

## When to Load

Load for exploit audits and hardening. Covers classic replication, opt-in Server Authority, remote abuse, economy attacks, and DataStore flows. Use `roblox-networking` for validation and rate-limit implementations.

## Quick Reference

**Core:** Client is always compromised. The server remains the source of truth, but the implementation depends on the authority model.

### Authority Models

- **Classic replication:** validate client requests and custom movement against server state. Never trust client damage, currency, inventory, permissions, or positions.
- **Server Authority:** with `Workspace.AuthorityMode = Server` and its required settings, the server owns core simulation while clients predict and recover from misprediction. Use `BindToSimulation()`, not blanket `Heartbeat` CFrame correction.
- **Both:** validate attacks, purchases, teleports, dashes, permissions, and custom remotes at the server boundary.

### Vectors & Mitigations

| Vector | Attack | Fix |
|--------|--------|-----|
| Movement | Custom dash, teleport, or locomotion abuse | Server state and transition checks; under Server Authority, keep simulation logic in `BindToSimulation()` and do not add blanket CFrame snap-back |
| Remote | Spam, arg spoof, replay | Rate limiter + validate arg types + idempotency |
| Economy | Dupe, negative qty | Session lock, atomic ops, qty > 0 |
| DataStore | Save spam, session hijack | Server-controlled saves, JobId session lock |
| General | Client trusts values | Server computes ALL game state |

### Audit Checklist

**CRITICAL:** Server-authoritative state · Choose and document the authority model · Validate all arg types · Rate limit remotes · Session-lock DataStore · No client currency mutations · ProcessReceipt verification · No secrets in client or replicated code

**HIGH:** Validate custom movement and action transitions · BindToClose protection · Atomic trading · Never trust client values · Use InputActions for simulation input in Server Authority projects

**MEDIUM:** Server cooldowns · server-computed leaderboards · anti-AFK reward checks · TextService filtering

### Anti-Patterns

Don't obfuscate client code, use `_G` for security, kick without logging, over-validate movement, or rely on client anti-cheat.

See `references/full.md` for detailed examples.
