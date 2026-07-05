---
name: roblox-security
description: Anti-exploit design, server authority, RemoteEvent validation, rate limiting, audit checklist.
last_reviewed: 2026-05-27
sources:
  - https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/security
---

## When to Load

Load this skill when auditing code for vulnerabilities or hardening against exploit vectors. Covers movement hacks, remote abuse, economy attacks, DataStore exploits. For validation implementation patterns and rate limiter code, see `roblox-networking`.

## Quick Reference

**Core:** Client is always compromised. Server = only source of truth.

### Vectors & Mitigations

| Vector | Attack | Fix |
|--------|--------|-----|
| Movement | Speed/teleport/fly/noclip | Server velocity+pos checks per Heartbeat |
| Remote | Spam, arg spoof, replay | Rate limiter + validate arg types + idempotency |
| Economy | Dupe, negative qty | Session lock, atomic ops, qty > 0 |
| DataStore | Save spam, session hijack | Server-controlled saves, JobId session lock |
| General | Client trusts values | Server computes ALL game state |

### Key Patterns

For rate limiter implementation and validation module code, see `roblox-networking`. Key audit points:
- Per-player, per-remote cooldown table exists
- All RemoteEvent handlers validate arg types, ranges, ownership
- Server computes all game state (damage, currency, movement)

### Audit Checklist

**CRITICAL:** Server-authoritative state · Validate all arg types · Rate limit remotes · Session-lock DataStore · No client currency mutations · ProcessReceipt verification · No sensitive LocalScript logic

**HIGH:** Server-validated movement · BindToClose protection · Atomic trading · Never trust client values

**MEDIUM:** Server cooldowns · Server leaderboards · Anti-AFK rewards · TextService filtering

### Anti-Patterns

Don't: obfuscate client, use `_G` for security, kick without logging, over-validate movement, rely on client anti-cheat

See `references/full.md` for detailed examples.
